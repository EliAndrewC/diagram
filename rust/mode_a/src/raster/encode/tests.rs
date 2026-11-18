//! The picture's paste and encode at their edges (feature 449 T150); the page lockstep holds every picture's pixels to the Python's.
//!
//! Research: the picture encode's tests - NONE: fixtures and assertions, deciding nothing about a building

use super::{base64, decode_rgb, encode_picture, jpeg, paste, png_size, Rgb};

/// A PNG of `width` x `height` of the given form, every sample `sample`.
fn png_of(
    width: u32,
    height: u32,
    color: png::ColorType,
    depth: png::BitDepth,
    sample: u8,
) -> Vec<u8> {
    let mut out = Vec::new();
    {
        let mut e = png::Encoder::new(&mut out, width, height);
        e.set_color(color);
        e.set_depth(depth);
        if color == png::ColorType::Indexed {
            e.set_palette(vec![sample; 3]);
        }
        let mut writer = e.write_header().unwrap();
        let channels = match color {
            png::ColorType::Grayscale | png::ColorType::Indexed => 1,
            png::ColorType::GrayscaleAlpha => 2,
            png::ColorType::Rgb => 3,
            png::ColorType::Rgba => 4,
        };
        let bytes = if depth == png::BitDepth::Sixteen {
            2
        } else {
            1
        };
        let n = usize::try_from(width * height).unwrap() * channels * bytes;
        writer
            .write_image_data(&vec![
                if color == png::ColorType::Indexed {
                    0
                } else {
                    sample
                };
                n
            ])
            .unwrap();
    }
    out
}

#[test]
fn base64_is_the_standard_padded_form() {
    assert_eq!(base64(b""), "");
    assert_eq!(base64(b"h"), "aA==");
    assert_eq!(base64(b"hi"), "aGk=");
    assert_eq!(base64(b"hi!"), "aGkh");
    assert_eq!(base64(&[0xFB, 0xFF]), "+/8=");
}

#[test]
fn every_png_form_reads_as_pil_s_rgb_conversion_makes_it() {
    use png::{BitDepth::Eight, ColorType as C};
    for (color, want) in [
        (C::Grayscale, [9, 9, 9]),
        (C::GrayscaleAlpha, [9, 9, 9]),
        (C::Rgb, [9, 9, 9]),
        (C::Rgba, [9, 9, 9]),
    ] {
        let rgb = decode_rgb(&png_of(2, 1, color, Eight, 9)).unwrap();
        assert_eq!(
            (color, rgb.width, rgb.height, &rgb.data[..3]),
            (color, 2, 1, &want[..])
        );
    }
    assert_eq!(
        decode_rgb(&png_of(1, 1, C::Indexed, Eight, 9))
            .unwrap_err()
            .kind,
        "RuntimeError"
    );
    assert!(decode_rgb(&png_of(1, 1, C::Rgb, png::BitDepth::Sixteen, 9))
        .unwrap_err()
        .message
        .contains("depth"));
    assert!(decode_rgb(b"not a png").is_err() && png_size(b"not a png").is_err());
    let mut cut = png_of(4, 4, C::Rgba, Eight, 9);
    cut.truncate(cut.len() - 20);
    assert!(decode_rgb(&cut)
        .unwrap_err()
        .message
        .contains("did not decode"));
    assert_eq!(png_size(&png_of(3, 2, C::Rgba, Eight, 1)).unwrap(), (3, 2));
}

#[test]
fn tiles_paste_at_their_offsets_and_a_gap_is_refused() {
    use png::{BitDepth::Eight, ColorType::Rgba};
    let tiles = vec![
        (0, 0, png_of(2, 1, Rgba, Eight, 10)),
        (1, 0, png_of(1, 1, Rgba, Eight, 20)),
        (0, 1, png_of(2, 2, Rgba, Eight, 30)),
        (1, 1, png_of(1, 2, Rgba, Eight, 40)),
    ];
    let img = paste(&tiles).unwrap();
    assert_eq!((img.width, img.height), (3, 3));
    let at = |x: usize, y: usize| img.data[(y * 3 + x) * 3];
    assert_eq!([at(0, 0), at(2, 0), at(1, 2), at(2, 2)], [10, 20, 30, 40]);
    assert!(paste(&tiles[..3]).unwrap_err().message.contains("missing"));
    assert!(encode_picture(&tiles).unwrap().starts_with(&[0xFF, 0xD8]));
    let wide = Rgb {
        width: 70_000,
        height: 1,
        data: vec![0; 210_000],
    };
    assert!(jpeg(&wide).unwrap_err().message.contains("size"));
    let short = Rgb {
        width: 2,
        height: 2,
        data: vec![0; 3],
    };
    assert!(jpeg(&short).unwrap_err().message.contains("encoder"));
}
