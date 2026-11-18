//! The picture's tiles pasted and encoded (`raster.encode_picture` and its PIL child, features 208, 222, 324; ported by feature 449 T150):
//! each tile's PNG decoded, its alpha dropped as PIL's `convert('RGB')` drops it (the picture is opaque, the sheet drawn under it), pasted
//! at its column's and row's offset, and the whole written as a JPEG at [`super::PICTURE_QUALITY`] with no chroma subsampling.
//!
//! WHERE THIS DIFFERS FROM THE PYTHON: PIL's encoder is libjpeg's, this one the `jpeg-encoder` crate's, so the JPEG's bytes differ and its
//! decoded pixels differ by a few levels where the two encoders' transforms round apart - the GM's rule (2026-11-17, "the resulting maps do
//! NOT need to be bitwise identical"), held by part A's lockstep (2026-11-18) to the tolerance `picture_diff` judges two renders by (`diagnostics/picture_diff.rs`). In
//! process, one tile decoded at a time (feature 324's memory rule; the Python's child existed only to give PIL's buffers back to the OS).
//!
//! Research: raster plumbing - NONE: decoding, pasting and encoding the rendered tiles

use l7r_gate_research::Error;

/// `base64.b64encode(data)`: the standard alphabet, padded.
#[must_use]
pub fn base64(data: &[u8]) -> String {
    const ABC: &[u8; 64] = b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
    let mut out = String::with_capacity(data.len().div_ceil(3) * 4);
    for chunk in data.chunks(3) {
        let b = [
            chunk[0],
            *chunk.get(1).unwrap_or(&0),
            *chunk.get(2).unwrap_or(&0),
        ];
        let n = (u32::from(b[0]) << 16) | (u32::from(b[1]) << 8) | u32::from(b[2]);
        for (i, shift) in [18, 12, 6, 0].into_iter().enumerate() {
            if i <= chunk.len() {
                out.push(char::from(
                    ABC[usize::try_from((n >> shift) & 63).unwrap_or(0)],
                ));
            } else {
                out.push('=');
            }
        }
    }
    out
}

/// A decoded tile: its width, height and RGB bytes.
#[derive(Debug)]
pub struct Rgb {
    pub width: usize,
    pub height: usize,
    pub data: Vec<u8>,
}

fn failed(what: &str, e: impl std::fmt::Display) -> Error {
    Error::new(
        "RuntimeError",
        format!("the picture child failed: {what}: {e}"),
    )
}

/// A PNG's width and height, from its header alone (PIL opens a tile lazily).
///
/// # Errors
/// Bytes that are no PNG.
pub fn png_size(png: &[u8]) -> Result<(usize, usize), Error> {
    let reader = png::Decoder::new(std::io::Cursor::new(png))
        .read_info()
        .map_err(|e| failed("a tile is no PNG", e))?;
    let info = reader.info();
    Ok((
        usize::try_from(info.width).unwrap_or(0),
        usize::try_from(info.height).unwrap_or(0),
    ))
}

/// A PNG decoded to RGB as PIL's `convert('RGB')` makes it: 8-bit gray, gray with alpha, RGB and RGBA (resvg writes RGBA), its alpha
/// dropped, never composited.
///
/// # Errors
/// Bytes that are no PNG, or a form resvg does not write (16-bit, a palette).
pub fn decode_rgb(png: &[u8]) -> Result<Rgb, Error> {
    let mut reader = png::Decoder::new(std::io::Cursor::new(png))
        .read_info()
        .map_err(|e| failed("a tile is no PNG", e))?;
    let mut buf = vec![0; reader.output_buffer_size().unwrap_or(0)];
    let frame = reader
        .next_frame(&mut buf)
        .map_err(|e| failed("a tile did not decode", e))?;
    if frame.bit_depth != png::BitDepth::Eight {
        return Err(failed("a tile's depth", format!("{:?}", frame.bit_depth)));
    }
    let channels = match frame.color_type {
        png::ColorType::Grayscale => 1,
        png::ColorType::GrayscaleAlpha => 2,
        png::ColorType::Rgb => 3,
        png::ColorType::Rgba => 4,
        png::ColorType::Indexed => return Err(failed("a tile's colors", "a palette")),
    };
    let (width, height) = (
        usize::try_from(frame.width).unwrap_or(0),
        usize::try_from(frame.height).unwrap_or(0),
    );
    let mut data = Vec::with_capacity(width * height * 3);
    for row in buf[..frame.buffer_size()].chunks(frame.line_size) {
        for px in row[..width * channels].chunks(channels) {
            if channels < 3 {
                data.extend([px[0]; 3]);
            } else {
                data.extend(&px[..3]);
            }
        }
    }
    Ok(Rgb {
        width,
        height,
        data,
    })
}

/// The tiles `(column, row, PNG)` pasted into one image (the PIL child's canvas): each column as wide as its tile in the first row, each
/// row as tall as its tile in the first column, every tile pasted at the sum before it and clipped to the canvas.
///
/// # Errors
/// A tile that is no PNG, or a grid with a missing tile.
pub fn paste(tiles: &[(i64, i64, Vec<u8>)]) -> Result<Rgb, Error> {
    let mut cols: Vec<i64> = tiles.iter().map(|t| t.0).collect();
    let mut rows: Vec<i64> = tiles.iter().map(|t| t.1).collect();
    for v in [&mut cols, &mut rows] {
        v.sort_unstable();
        v.dedup();
    }
    let at = |c: i64, r: i64| {
        tiles
            .iter()
            .find(|t| t.0 == c && t.1 == r)
            .ok_or_else(|| failed("a tile is missing", format!("({c}, {r})")))
    };
    let (first_col, first_row) = (
        cols.first().copied().unwrap_or(0),
        rows.first().copied().unwrap_or(0),
    );
    let ws: Vec<usize> = cols
        .iter()
        .map(|&c| Ok(png_size(&at(c, first_row)?.2)?.0))
        .collect::<Result<_, Error>>()?;
    let hs: Vec<usize> = rows
        .iter()
        .map(|&r| Ok(png_size(&at(first_col, r)?.2)?.1))
        .collect::<Result<_, Error>>()?;
    let (width, height) = (ws.iter().sum::<usize>(), hs.iter().sum::<usize>());
    let mut data = vec![0_u8; width * height * 3];
    let mut y = 0;
    for (&r, &h) in rows.iter().zip(&hs) {
        let mut x = 0;
        for (&c, &w) in cols.iter().zip(&ws) {
            let tile = decode_rgb(&at(c, r)?.2)?;
            let cw = tile.width.min(width.saturating_sub(x));
            for ty in 0..tile.height.min(height.saturating_sub(y)) {
                let src = &tile.data[ty * tile.width * 3..(ty * tile.width + cw) * 3];
                let dst = ((y + ty) * width + x) * 3;
                data[dst..dst + cw * 3].copy_from_slice(src);
            }
            x += w;
        }
        y += h;
    }
    Ok(Rgb {
        width,
        height,
        data,
    })
}

/// An RGB image as the page's JPEG: quality [`super::PICTURE_QUALITY`], 4:4:4.
///
/// # Errors
/// An image past the JPEG's 65,535 px a side, or the encoder's own failure.
pub fn jpeg(image: &Rgb) -> Result<Vec<u8>, Error> {
    let side = |v: usize| u16::try_from(v).map_err(|_| failed("the picture's size", v));
    let (w, h) = (side(image.width)?, side(image.height)?);
    let mut out = Vec::new();
    let mut encoder = jpeg_encoder::Encoder::new(&mut out, super::PICTURE_QUALITY);
    encoder.set_sampling_factor(jpeg_encoder::SamplingFactor::R_4_4_4);
    encoder
        .encode(&image.data, w, h, jpeg_encoder::ColorType::Rgb)
        .map_err(|e| failed("the encoder", e))?;
    Ok(out)
}

/// The rendered tiles pasted into one image and encoded as the page's picture (`raster.encode_picture`).
///
/// # Errors
/// [`paste`]'s or [`jpeg`]'s.
pub fn encode_picture(tiles: &[(i64, i64, Vec<u8>)]) -> Result<Vec<u8>, Error> {
    jpeg(&paste(tiles)?)
}

#[cfg(test)]
mod tests;
