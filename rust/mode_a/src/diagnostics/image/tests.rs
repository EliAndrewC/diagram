//! A render read as PIL read it (feature 449 T150): each PNG form, the refusals, base64 and the page's id map.
//!
//! Research:
//!     the diagnostics' tests - NONE: fixtures and assertions, no map decision

use super::{b64decode, decode_idmap, rgb};

/// A PNG of `color` at `depth`, `w` x `h`, from `data` (a palette and transparency where given).
pub fn png_of(
    w: u32,
    h: u32,
    color: png::ColorType,
    depth: png::BitDepth,
    data: &[u8],
    palette: Option<&[u8]>,
    trns: Option<&[u8]>,
) -> Vec<u8> {
    let mut out = Vec::new();
    {
        let mut e = png::Encoder::new(&mut out, w, h);
        e.set_color(color);
        e.set_depth(depth);
        if let Some(p) = palette {
            e.set_palette(p.to_vec());
        }
        if let Some(t) = trns {
            e.set_trns(t.to_vec());
        }
        e.write_header().unwrap().write_image_data(data).unwrap();
    }
    out
}

#[test]
fn every_png_form_reads_as_pil_converts_it() {
    use png::{BitDepth as D, ColorType as C};
    let rgba = png_of(
        2,
        1,
        C::Rgba,
        D::Eight,
        &[1, 2, 3, 0, 4, 5, 6, 255],
        None,
        None,
    );
    assert_eq!(rgb(&rgba, "a").unwrap().data, [1, 2, 3, 4, 5, 6]);
    let gray = png_of(2, 1, C::Grayscale, D::Eight, &[7, 9], None, Some(&[0, 7]));
    assert_eq!(rgb(&gray, "g").unwrap().data, [7, 7, 7, 9, 9, 9]);
    let ga = png_of(1, 1, C::GrayscaleAlpha, D::Eight, &[8, 0], None, None);
    assert_eq!(rgb(&ga, "ga").unwrap().data, [8, 8, 8]);
    let pal = png_of(
        2,
        1,
        C::Indexed,
        D::Two,
        &[0b0001_0000],
        Some(&[10, 20, 30, 40, 50, 60]),
        Some(&[0]),
    );
    assert_eq!(rgb(&pal, "p").unwrap().data, [10, 20, 30, 40, 50, 60]);
    let low = png_of(2, 1, C::Grayscale, D::Four, &[0xf1], None, None);
    assert_eq!(rgb(&low, "l").unwrap().data, [255, 255, 255, 17, 17, 17]);
    // 16 bits: gray is PIL's `I;16`, clipped; every other form its high byte
    let g16 = png_of(2, 1, C::Grayscale, D::Sixteen, &[0, 200, 1, 0], None, None);
    assert_eq!(
        rgb(&g16, "g16").unwrap().data,
        [200, 200, 200, 255, 255, 255]
    );
    let rgb16 = png_of(1, 1, C::Rgb, D::Sixteen, &[1, 2, 3, 4, 5, 6], None, None);
    assert_eq!(rgb(&rgb16, "c16").unwrap().data, [1, 3, 5]);
}

#[test]
fn what_is_no_png_is_refused_by_name() {
    // a JPEG's header and no picture: read as a JPEG, and refused as one that does not decode
    assert_eq!(
        rgb(b"\xff\xd8\xff\xe0", "x.jpg").unwrap_err().kind,
        "OSError"
    );
    let e = rgb(b"plain text", "x.png").unwrap_err();
    assert_eq!(
        (e.kind, e.message.as_str()),
        (
            "PIL.UnidentifiedImageError",
            "cannot identify image file 'x.png'"
        )
    );
    assert_eq!(
        rgb(b"\x89PNG\r\n\x1a\nbroken", "b").unwrap_err().kind,
        "OSError"
    );
    let mut cut = png_of(
        4,
        4,
        png::ColorType::Rgb,
        png::BitDepth::Eight,
        &[9; 48],
        None,
        None,
    );
    cut.truncate(cut.len() - 20);
    assert_eq!(rgb(&cut, "c").unwrap_err().kind, "OSError");
}

#[test]
fn base64_is_python_s() {
    assert_eq!(b64decode("QUJD").unwrap(), b"ABC");
    assert_eq!(b64decode("QUI=").unwrap(), b"AB");
    assert_eq!(b64decode("QQ==").unwrap(), b"A");
    let refused: Vec<String> = ["QQ", "Q", "QQ=", "QUJDQ==="]
        .iter()
        .map(|bad| b64decode(bad).unwrap_err().message)
        .collect();
    assert_eq!(refused, ["Incorrect padding"; 4]);
    // `/` and `+` are the alphabet's last two; a character outside it is dropped, as `b64decode` drops it
    assert_eq!(b64decode("+/+/").unwrap(), [0xfb, 0xff, 0xbf]);
    assert_eq!(b64decode("QU\nJD").unwrap(), b"ABC");
}

#[test]
fn a_page_s_id_map_decodes_and_a_row_past_the_first_refuses() {
    let png = png_of(
        2,
        1,
        png::ColorType::Rgba,
        png::BitDepth::Eight,
        &[4, 0, 0, 255, 8, 1, 0, 255],
        None,
        None,
    );
    let data = crate::raster::encode::base64(&png);
    let page = format!("x \"idmap\": \"data:image/png;base64,{data}\", \"palette\": {{\"8\": \"well\", \"4\": \"road\"}}, \"step\": 4");
    let m = decode_idmap(&page).unwrap().unwrap();
    assert_eq!(
        (m.width, m.height, m.red, m.green, m.step),
        (2, 1, vec![4, 8], vec![0, 1], 4)
    );
    assert_eq!(
        m.palette,
        [((0, 8), "well".to_owned()), ((0, 4), "road".to_owned())]
    );
    assert!(decode_idmap("\"palette\": {}").unwrap().is_none());
    // a row past the first, `red,green` (fixed: the Python's `int()` refused it), and a key of neither form
    let rows = page.replace("\"8\":", "\"4,4\":");
    assert_eq!(decode_idmap(&rows).unwrap().unwrap().palette[0].0, (4, 4));
    let bad = page.replace("\"8\":", "\"x\":");
    assert_eq!(
        decode_idmap(&bad).unwrap_err().message,
        "invalid literal for int() with base 10: 'x'"
    );
    let bad = page.replace("{\"8\"", "{8");
    assert_eq!(
        decode_idmap(&bad).unwrap_err().kind,
        "json.decoder.JSONDecodeError"
    );
}

/// Each format and mode HEAD's PIL wrote and read (`pil.json`, written by PIL 12.3.0 in a scratch probe, 2026-11-18), read here as PIL
/// read it: every lossless one pixel for pixel; JPEG within its decoders' rounding (zune-jpeg against libjpeg-turbo: 2 levels at most
/// on these, measured). FIXED (feature 449 T183, T150's finding): the two TIFF forms the `image` crate does not read, gray with alpha
/// and a palette, were refused; they are read as PIL read them.
#[test]
fn every_format_reads_as_pil_reads_it() {
    let v: serde_json::Value = serde_json::from_str(include_str!("pil.json")).unwrap();
    let (mut exact, mut jpeg) = (Vec::new(), Vec::new());
    for c in v["cases"].as_array().unwrap() {
        let ext = match c["format"].as_str().unwrap() {
            "JPEG" => "jpg".to_owned(),
            "TIFF" => "tif".to_owned(),
            f => f.to_lowercase(),
        };
        let name = format!("{}.{ext}", c["name"].as_str().unwrap());
        let file = b64decode(c["file"].as_str().unwrap()).unwrap();
        let want = b64decode(c["rgb"].as_str().unwrap()).unwrap();
        let got = rgb(&file, &name).unwrap();
        if ext == "jpg" {
            let d = got
                .data
                .iter()
                .zip(&want)
                .map(|(a, b)| a.abs_diff(*b))
                .max()
                .unwrap_or(0);
            jpeg.push((name, got.data.len() == want.len() && d <= 2));
        } else {
            exact.push((name, got.data == want));
        }
    }
    assert_eq!(exact.iter().filter(|(_, same)| !*same).count(), 0);
    assert_eq!(exact.len(), 33);
    assert_eq!(jpeg.iter().filter(|(_, near)| *near).count(), 3);
}

/// An 8-bit palette TIFF, 2 x 1, its indices 1 and 0 over (10, 20, 30) and (40, 50, 60), big-endian or little: PIL writes its palettes
/// little-endian, so a scratch probe wrote both forms by hand, and PIL 12.3.0 read each as `P`, RGB `28323c0a141e` (2026-11-18, feature
/// 449 T183).
fn palette_tiff(big: bool) -> Vec<u8> {
    let n = |v: u32, width: usize| {
        if big {
            v.to_be_bytes()[4 - width..].to_vec()
        } else {
            v.to_le_bytes()[..width].to_vec()
        }
    };
    let mut map = [0u32; 768];
    for (i, rgb) in [[10, 20, 30], [40, 50, 60]].iter().enumerate() {
        for (c, v) in rgb.iter().enumerate() {
            map[256 * c + i] = v * 257;
        }
    }
    let colors_at = 8 + 2 + 12 * 9 + 4;
    let entries: [(u32, u32, u32, u32); 9] = [
        (256, 3, 1, 2),
        (257, 3, 1, 1),
        (258, 3, 1, 8),
        (259, 3, 1, 1),
        (262, 3, 1, 3),
        (273, 4, 1, colors_at + 1536),
        (278, 3, 1, 1),
        (279, 4, 1, 2),
        (320, 3, 768, colors_at),
    ];
    let mut out = if big { b"MM".to_vec() } else { b"II".to_vec() };
    out.extend(n(42, 2));
    out.extend(n(8, 4));
    out.extend(n(9, 2));
    for (tag, kind, count, value) in entries {
        out.extend(n(tag, 2));
        out.extend(n(kind, 2));
        out.extend(n(count, 4));
        // a single short sits at the field's start; a long or an offset fills it
        let mut field = n(value, if (kind, count) == (3, 1) { 2 } else { 4 });
        field.resize(4, 0);
        out.extend(field);
    }
    out.extend(n(0, 4));
    out.extend(map.iter().flat_map(|v| n(*v, 2)));
    out.extend([1, 0]);
    out
}

/// FIXED (feature 449 T183): a palette TIFF big-endian or little reads through its color map; a palette form PIL
/// wrote but this port does not read is refused naming it, never read as something else; a TIFF the decoder cannot read is refused as
/// one that does not decode.
#[test]
fn a_palette_tiff_reads_in_either_order_and_another_palette_form_is_refused() {
    for big in [true, false] {
        assert_eq!(
            rgb(&palette_tiff(big), "p.tif").unwrap().data,
            [40, 50, 60, 10, 20, 30]
        );
    }
    let e = rgb(b"II*\0\x08\0\0\0", "cut.tif").unwrap_err();
    assert_eq!(
        (e.kind, e.message.starts_with("Tiff file does not decode: ")),
        ("OSError", true)
    );
    let v: serde_json::Value = serde_json::from_str(include_str!("pil.json")).unwrap();
    let p = v["cases"]
        .as_array()
        .unwrap()
        .iter()
        .find(|c| c["name"] == "tiff-p")
        .unwrap();
    let mut four = b64decode(p["file"].as_str().unwrap()).unwrap();
    // BitsPerSample (258), one short, 8 -> 4: PIL's `P;4`
    let at = four
        .windows(10)
        .position(|w| w == [2, 1, 3, 0, 1, 0, 0, 0, 8, 0])
        .unwrap();
    four[at + 8] = 4;
    let e = rgb(&four, "p4.tif").unwrap_err();
    assert_eq!(
        (e.kind, e.message.as_str()),
        (
            "OSError",
            "a TIFF palette image of [4] bits a sample is not read here: PIL's 8-bit palette (`P`) is the one palette form read"
        )
    );
}
