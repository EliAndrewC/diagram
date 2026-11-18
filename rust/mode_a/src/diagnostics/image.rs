//! A render read as PIL read it for the two diagnostics (feature 449 T150): its pixels as `Image.open(...).convert("RGB")` makes them,
//! and the class id map a page carries as `page_lit.decode_idmap` decoded it. Every PNG form is read here - a palette expanded, a
//! low-depth gray scaled to 8 bits, a 16-bit sample cut to its high byte except 16-bit gray, which PIL reads as `I;16` and clips at
//! 255, alpha dropped and never composited; every other format HEAD's PIL read that the `image` crate reads goes through that crate,
//! held to PIL's own reading of a PIL-written file of each format and mode (`image/pil.json`, the tests).
//!
//! Research: the diagnostics' images - NONE: decoding, no map decision

use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_gate_research::pyre::py;
use l7r_gate_research::Error;

use crate::raster::encode::Rgb;

static IDMAP: LazyLock<Regex> =
    LazyLock::new(|| py(r#""idmap":\s*"data:image/png;base64,([A-Za-z0-9+/=]+)""#));
static PALETTE: LazyLock<Regex> = LazyLock::new(|| py(r#""palette":\s*(\{[^{}]*\})"#));
static STEP: LazyLock<Regex> = LazyLock::new(|| py(r#""step":\s*(\d+)"#));

/// `bytes` (the file at `path`) as RGB.
///
/// # Errors
/// Bytes that are no image this port reads (PIL's `UnidentifiedImageError`), or an image that does not decode.
pub fn rgb(bytes: &[u8], path: &str) -> Result<Rgb, Error> {
    if !bytes.starts_with(b"\x89PNG\r\n\x1a\n") {
        return other(bytes, path);
    }
    let broken = |e: &dyn std::fmt::Display| Error::new("OSError", format!("broken PNG file: {e}"));
    let mut decoder = png::Decoder::new(std::io::Cursor::new(bytes));
    decoder.set_transformations(png::Transformations::EXPAND);
    let mut reader = decoder.read_info().map_err(|e| broken(&e))?;
    let source = reader.info().color_type;
    let mut buf = vec![0; reader.output_buffer_size().unwrap_or(0)];
    let frame = reader.next_frame(&mut buf).map_err(|e| broken(&e))?;
    let wide = frame.bit_depth == png::BitDepth::Sixteen;
    let channels = frame.color_type.samples();
    let (width, height) = (frame.width as usize, frame.height as usize);
    let sample = |px: &[u8], i: usize| -> u8 {
        if !wide {
            return px[i];
        }
        let v = u16::from_be_bytes([px[2 * i], px[2 * i + 1]]);
        if source == png::ColorType::Grayscale {
            u8::try_from(v.min(255)).unwrap_or(255) // PIL's `I;16` to RGB: clipped, not scaled
        } else {
            px[2 * i] // `;16B` raw modes: the high byte
        }
    };
    let step = channels * if wide { 2 } else { 1 };
    let mut data = Vec::with_capacity(width * height * 3);
    for row in buf[..frame.buffer_size()].chunks(frame.line_size) {
        for px in row[..width * step].chunks(step) {
            if channels < 3 {
                data.extend([sample(px, 0); 3]);
            } else {
                data.extend([sample(px, 0), sample(px, 1), sample(px, 2)]);
            }
        }
    }
    Ok(Rgb {
        width,
        height,
        data,
    })
}

/// Any other format the `image` crate reads, as PIL's `convert("RGB")` makes it: gray replicated, alpha dropped and never composited, a
/// 16-bit gray clipped at 255 as PIL's `I;16` is, any other 16-bit sample cut to its high byte, CMYK as PIL inverts it.
fn other(bytes: &[u8], path: &str) -> Result<Rgb, Error> {
    let unidentified = || {
        Error::new(
            "PIL.UnidentifiedImageError",
            format!(
                "cannot identify image file {}",
                l7r_guard::shared::py_text::repr(path)
            ),
        )
    };
    // a format with no magic of its own (TGA) is known by its name, as PIL's openers try each in turn
    let format = image::guess_format(bytes)
        .or_else(|_| {
            image::ImageFormat::from_path(path)
                .map_err(|_| ())
                .and_then(|f| {
                    if f == image::ImageFormat::Tga {
                        Ok(f)
                    } else {
                        Err(())
                    }
                })
        })
        .map_err(|()| unidentified())?;
    if format == image::ImageFormat::Ico {
        if let Some(png) = ico_png(bytes) {
            return rgb(png, path);
        }
    }
    let decoded = image::load_from_memory_with_format(bytes, format)
        .map_err(|e| Error::new("OSError", format!("{format:?} file does not decode: {e}")))?;
    let (width, height) = (decoded.width() as usize, decoded.height() as usize);
    let data = match decoded {
        image::DynamicImage::ImageLuma16(g) => g
            .as_raw()
            .iter()
            .flat_map(|v| [u8::try_from((*v).min(255)).unwrap_or(255); 3])
            .collect(),
        other => other.to_rgb8().into_raw(),
    };
    Ok(Rgb {
        width,
        height,
        data,
    })
}

/// The largest image of an icon when it is a PNG (PIL's `IcoFile` takes the largest size, then the deepest): read as any PNG is here -
/// the `image` crate refuses a PNG in an icon that is not RGBA, which PIL itself writes for an RGB image.
fn ico_png(bytes: &[u8]) -> Option<&[u8]> {
    let n = usize::from(u16::from_le_bytes([*bytes.get(4)?, *bytes.get(5)?]));
    let entry = |i: usize| -> Option<(u32, u16, usize, usize)> {
        let e = bytes.get(6 + 16 * i..6 + 16 * (i + 1))?;
        let side = |b: u8| if b == 0 { 256 } else { u32::from(b) };
        let len = u32::from_le_bytes([e[8], e[9], e[10], e[11]]) as usize;
        let at = u32::from_le_bytes([e[12], e[13], e[14], e[15]]) as usize;
        Some((
            side(e[0]) * side(e[1]),
            u16::from_le_bytes([e[6], e[7]]),
            at,
            len,
        ))
    };
    let (_, _, at, len) = (0..n)
        .filter_map(entry)
        .max_by_key(|(area, bpp, _, _)| (*area, *bpp))?;
    bytes
        .get(at..at + len)
        .filter(|d| d.starts_with(b"\x89PNG\r\n\x1a\n"))
}

/// `base64.b64decode`: the standard alphabet; data that does not pad out refused as `binascii` refuses it.
///
/// # Errors
/// Incorrect padding.
pub fn b64decode(text: &str) -> Result<Vec<u8>, Error> {
    let value = |c: u8| match c {
        b'A'..=b'Z' => Some(c - b'A'),
        b'a'..=b'z' => Some(c - b'a' + 26),
        b'0'..=b'9' => Some(c - b'0' + 52),
        b'+' => Some(62),
        b'/' => Some(63),
        _ => None,
    };
    // a character outside the alphabet is dropped (`binascii`'s non-strict mode); the data then pads out by its `=`s or is refused
    let sextets: Vec<u8> = text.bytes().filter_map(value).collect();
    let pads = text.bytes().filter(|b| *b == b'=').count();
    let padded = match sextets.len() % 4 {
        0 => true,
        2 => pads >= 2,
        3 => pads >= 1,
        _ => false,
    };
    if !padded {
        return Err(Error::new("binascii.Error", "Incorrect padding"));
    }
    let mut out = Vec::with_capacity(sextets.len() * 3 / 4);
    for chunk in sextets.chunks(4) {
        let n = chunk
            .iter()
            .enumerate()
            .fold(0_u32, |n, (i, &s)| n | (u32::from(s) << (18 - 6 * i)));
        out.extend(&n.to_be_bytes()[1..chunk.len()]);
    }
    Ok(out)
}

/// A palette entry's key as the attribution sorts and reads it: `(green, red)` - the palette's row, then its red value.
pub type Key = (i64, i64);

/// A palette key as the page writes it: `"red"` on the palette's first row, `"red,green"` past it (feature 264: past 63 kinds the green
/// channel counts the rows, `raster.rs`'s `palette_key`).
///
/// FIXED, NOT REPRODUCED (feature 449 T150; constitution XIV and FR-002's exception for a check that refuses correct work): the Python
/// read each key with `int()`, which refused `"4,4"` - so `page_lit`, and `picture_diff --page` whenever anything differed, refused every
/// page past 63 kinds, Hayakawa's and Ubame's among the pool's. Both halves are read here, and the attribution answers by both channels,
/// as `page.js keyAtPoint` does.
///
/// # Errors
/// A key of neither form, refused in `int()`'s words.
pub fn palette_key_of(k: &str) -> Result<Key, Error> {
    let bad = || {
        Error::new(
            "ValueError",
            format!(
                "invalid literal for int() with base 10: {}",
                l7r_guard::shared::py_text::repr(k)
            ),
        )
    };
    let (red, green) = k.split_once(',').unwrap_or((k, "0"));
    let int = |s: &str| super::args::py_int(s).map_err(|_| bad());
    Ok((int(green)?, int(red)?))
}

/// The class id map a page carries: its red and green channels row by row, `{(green, red): class key}` and the palette step.
#[derive(Debug)]
pub struct IdMap {
    pub width: usize,
    pub height: usize,
    pub red: Vec<u8>,
    pub green: Vec<u8>,
    pub palette: Vec<(Key, String)>,
    pub step: i64,
}

/// The page's id map decoded (`page_lit.decode_idmap`): the first `"idmap"`, `"palette"` and `"step"` in its text, none where any is
/// missing (a page rendered without its raster).
///
/// # Errors
/// The id map no PNG or no base64, the palette no JSON object, or a key of neither form ([`palette_key_of`]).
pub fn decode_idmap(html: &str) -> Result<Option<IdMap>, Error> {
    let first = |re: &Regex| re.captures(html).ok().flatten().map(|c| c[1].to_owned());
    let (Some(data), Some(palette), Some(step)) = (first(&IDMAP), first(&PALETTE), first(&STEP))
    else {
        return Ok(None);
    };
    let png = rgb(&b64decode(&data)?, "<the id map>")?;
    let object = l7r_guard::shared::pyjson::loads(&palette)
        .map_err(|e| Error::new("json.decoder.JSONDecodeError", e.to_string()))?;
    let mut keys = Vec::new();
    for (k, v) in object.as_object().into_iter().flatten() {
        keys.push((palette_key_of(k)?, l7r_guard::shared::pyjson::py_str(v)));
    }
    Ok(Some(IdMap {
        width: png.width,
        height: png.height,
        red: png.data.iter().step_by(3).copied().collect(),
        green: png.data.iter().skip(1).step_by(3).copied().collect(),
        palette: keys,
        step: step.parse().unwrap_or(0),
    }))
}

#[cfg(test)]
pub(crate) mod tests;
