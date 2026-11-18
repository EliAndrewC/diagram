//! The page lit (feature 449 T150): the attribution through the screen transform and the viewBox, the report, and the command with
//! a stand-in for the browser's launcher.
//!
//! Research:
//!     the diagnostics' tests - NONE: fixtures and assertions, no map decision

use serde_json::json;

use super::{abspath, attribute, main, report};
use crate::diagnostics::image::tests::png_of;
use crate::diagnostics::image::IdMap;
use crate::raster::encode::Rgb;

fn map() -> IdMap {
    // 2 x 2: road (4) on the left column, well (8) top right, nothing bottom right
    IdMap {
        width: 2,
        height: 2,
        red: vec![4, 8, 4, 0],
        green: vec![0; 4],
        palette: vec![((0, 8), "well".into()), ((0, 4), "road".into())],
        step: 4,
    }
}

fn shot(lit: &[usize]) -> Rgb {
    let mut data = vec![0_u8; 4 * 4 * 3];
    for &i in lit {
        data[3 * i] = 200;
    }
    Rgb {
        width: 4,
        height: 4,
        data,
    }
}

#[test]
fn each_screen_pixel_is_answered_by_the_id_map_under_it() {
    // the 4 x 4 screen shows the map at 2 px per unit; the viewBox is the map
    let got = attribute(
        &shot(&[]),
        &shot(&[0, 1, 4]),
        &map(),
        &json!([2, 0, 0, 2, 0, 0]),
        &json!(null),
    )
    .unwrap();
    assert_eq!(
        got,
        [("road".to_owned(), (3, 8)), ("well".to_owned(), (0, 4))]
    );
    // at 1 px per unit the viewBox (4 units for the id map's 2 px) scales the map back over the whole screen; shifted 2 units right,
    // the left half of the screen falls before the map
    let ident = json!([1, 0, 0, 1, 0, 0]);
    let vb = attribute(
        &shot(&[]),
        &shot(&[0]),
        &map(),
        &ident,
        &json!([0, 0, 4, 4]),
    )
    .unwrap();
    assert_eq!(
        vb,
        [("road".to_owned(), (1, 8)), ("well".to_owned(), (0, 4))]
    );
    let shifted = attribute(
        &shot(&[]),
        &shot(&[0]),
        &map(),
        &ident,
        &json!([2, 0, 4, 4]),
    )
    .unwrap();
    assert_eq!(
        shifted,
        [("road".to_owned(), (0, 8)), ("well".to_owned(), (0, 0))]
    );
    // a transform with no inverse: every sample is NaN, off the map
    let flat = attribute(
        &shot(&[]),
        &shot(&[0]),
        &map(),
        &json!([0, 0, 0, 0, 0, 0]),
        &json!(null),
    )
    .unwrap();
    assert_eq!(
        flat,
        [("road".to_owned(), (0, 0)), ("well".to_owned(), (0, 0))]
    );
    // two palette values naming one class: one row, the last value's counts, as a dict keeps it
    let mut twice = map();
    twice.palette.push(((0, 0), "road".into()));
    let got = attribute(
        &shot(&[]),
        &shot(&[]),
        &twice,
        &json!([2, 0, 0, 2, 0, 0]),
        &json!(null),
    )
    .unwrap();
    assert_eq!(
        got,
        [("road".to_owned(), (0, 8)), ("well".to_owned(), (0, 4))]
    );
    let small = Rgb {
        width: 1,
        height: 1,
        data: vec![0; 3],
    };
    assert!(attribute(
        &small,
        &shot(&[]),
        &map(),
        &json!([1, 0, 0, 1, 0, 0]),
        &json!(null)
    )
    .is_err());
    assert_eq!(
        attribute(&shot(&[]), &shot(&[]), &map(), &json!([1, 0]), &json!(null))
            .unwrap_err()
            .kind,
        "ValueError"
    );
    assert_eq!(
        attribute(
            &shot(&[]),
            &shot(&[]),
            &map(),
            &json!([1, 0, 0, 1, 0, null]),
            &json!(null)
        )
        .unwrap_err()
        .kind,
        "TypeError"
    );
}

#[test]
fn the_report_puts_the_most_changed_first() {
    let classes = vec![
        ("road".to_owned(), (3, 8)),
        ("well".to_owned(), (0, 4)),
        ("gone".to_owned(), (0, 0)),
    ];
    assert_eq!(
        report("road", &json!("vector"), &json!(2.0), &classes).unwrap(),
        "lit: road  mode: vector  zoom: 2.00x of fit\n changed    changed/on screen  class\n   37.5%          3/8          road\n    0.0%          0/4          well"
    );
    let r = report("lane", &json!(null), &json!(1), &classes).unwrap();
    assert!(r.starts_with("lit: lane  mode: None  zoom: 1.00x of fit\n  (no pixels of 'lane' are on screen in this view)"), "{r}");
    assert_eq!(
        report("x", &json!("v"), &json!("big"), &[])
            .unwrap_err()
            .kind,
        "TypeError"
    );
    assert_eq!(abspath("/a/./b/../c"), "/a/c");
    assert!(abspath("x.html").ends_with("/x.html"));
}

/// A page with an id map, a page with none, the two shots, and the launcher's stand-in: `browser lit <page> <key> <before> <after>
/// [--vector]`, copying the shots and answering - its key picks a failure. The directory, the launcher and the lit shot's PNG.
fn world() -> (
    l7r_guard::shared::tempdir::TempDir,
    std::path::PathBuf,
    Vec<u8>,
) {
    let dir = l7r_guard::shared::tempdir::TempDir::new("page-lit");
    let at = |n: &str| dir.path().join(n).to_string_lossy().into_owned();
    let png = png_of(
        2,
        2,
        png::ColorType::Rgba,
        png::BitDepth::Eight,
        &[4, 0, 0, 255, 8, 0, 0, 255, 4, 0, 0, 255, 0, 0, 0, 255],
        None,
        None,
    );
    let page = format!(
        "\"idmap\": \"data:image/png;base64,{}\", \"palette\": {{\"4\": \"road\", \"8\": \"well\"}}, \"step\": 4",
        crate::raster::encode::base64(&png)
    );
    std::fs::write(at("p.html"), page).unwrap();
    std::fs::write(at("bare.html"), "no map").unwrap();
    let before = png_of(
        4,
        4,
        png::ColorType::Rgb,
        png::BitDepth::Eight,
        &[0; 48],
        None,
        None,
    );
    let mut lit = vec![0_u8; 48];
    lit[0] = 200;
    let after = png_of(
        4,
        4,
        png::ColorType::Rgb,
        png::BitDepth::Eight,
        &lit,
        None,
        None,
    );
    std::fs::write(at("before.png"), &before).unwrap();
    std::fs::write(at("after.png"), &after).unwrap();
    // the launcher's stand-in: `browser lit <page> <key> <before> <after> [--vector]`, copying the shots and answering
    let launcher = dir.path().join("launcher");
    l7r_gate_core::write_executable(
        &launcher,
        &format!(
            "#!/bin/sh\ncase \"$4\" in fail) echo 'l7r-browser lit: page.goto: net::ERR' >&2; exit 1;; junk) echo nope; exit 0;; noshot) echo '{{}}'; exit 0;; badshot) echo x > \"$5\"; echo x > \"$6\"; echo '{{\"zoom\": 1}}'; exit 0;; badpixels) cp {b} \"$5\"; echo x > \"$6\"; echo '{{\"zoom\": 1}}'; exit 0;; esac\n\
             cp {b} \"$5\"; cp {a} \"$6\"; echo '{{\"mode\": \"raster\", \"zoom\": 1, \"ctm\": [2, 0, 0, 2, 0, 0], \"viewbox\": null}}'\n",
            b = at("before.png"),
            a = at("after.png")
        ),
    );
    (dir, launcher, after)
}

#[test]
fn the_command_runs_the_browser_and_reports() {
    let (dir, launcher, after) = world();
    let at = |n: &str| dir.path().join(n).to_string_lossy().into_owned();
    let run = |w: &[&str]| {
        main(
            &w.iter().map(|s| (*s).to_owned()).collect::<Vec<_>>(),
            &launcher,
        )
    };
    let r = run(&[&at("p.html"), "road", "--vector", "--out", &at("lit.png")]);
    assert_eq!(r.code, 0, "{}", r.stderr);
    assert!(
        r.stdout
            .starts_with("lit: road  mode: raster  zoom: 1.00x of fit\n"),
        "{}",
        r.stdout
    );
    assert!(
        r.stdout.contains("   12.5%          1/8          road\n"),
        "{}",
        r.stdout
    );
    assert_eq!(std::fs::read(at("lit.png")).unwrap(), after);
    let r = run(&[&at("bare.html"), "road"]);
    assert_eq!(r.stderr, format!("{} carries no class id map (rendered without resvg?) - nothing to attribute pixels to\n", at("bare.html")));
    assert!(run(&[&at("p.html"), "fail"]).stderr.contains("net::ERR"));
    assert!(run(&[&at("p.html"), "badshot"])
        .stderr
        .starts_with("PIL.UnidentifiedImageError: "));
    assert!(run(&[&at("p.html"), "noshot"])
        .stderr
        .starts_with("FileNotFoundError: "));
    let r = run(&[&at("p.html"), "road", "--out", &at("no/dir/lit.png")]);
    assert!(r.stderr.starts_with("FileNotFoundError: "), "{}", r.stderr);
    assert!(run(&[&at("p.html"), "junk"])
        .stderr
        .starts_with("RuntimeError: the browser answered"));
    assert!(
        main(&[at("p.html"), "road".into()], &dir.path().join("none"))
            .stderr
            .starts_with("OSError: ")
    );
    assert_eq!(run(&[&at("none.html"), "road"]).code, 1);
    assert_eq!(run(&["-h"]).code, 0);
    assert_eq!((run(&["p"]).code, run(&["p", "k", "--out"]).code), (2, 2));
}

#[test]
fn the_lit_shot_is_saved_in_the_format_its_name_asks() {
    let (dir, launcher, after) = world();
    let at = |n: &str| dir.path().join(n).to_string_lossy().into_owned();
    let run = |w: &[&str]| {
        main(
            &w.iter().map(|s| (*s).to_owned()).collect::<Vec<_>>(),
            &launcher,
        )
    };
    // any other format by its extension: a BMP's pixels the shot's own; a name of no known format refused in PIL's words
    let r = run(&[&at("p.html"), "road", "--out", &at("lit.BMP")]);
    assert_eq!(r.code, 0, "{}", r.stderr);
    let bmp =
        crate::diagnostics::image::rgb(&std::fs::read(at("lit.BMP")).unwrap(), "lit.bmp").unwrap();
    assert_eq!(
        bmp.data,
        crate::diagnostics::image::rgb(&after, "after")
            .unwrap()
            .data
    );
    // a pixmap and a TGA, as PIL wrote them
    for name in ["lit.ppm", "lit.tga"] {
        assert_eq!(run(&[&at("p.html"), "road", "--out", &at(name)]).code, 0);
        let got = crate::diagnostics::image::rgb(&std::fs::read(at(name)).unwrap(), name).unwrap();
        assert_eq!(
            got.data,
            crate::diagnostics::image::rgb(&after, "after")
                .unwrap()
                .data
        );
    }
    assert!(std::fs::read(at("lit.ppm")).unwrap().starts_with(b"P6"));
    let r = run(&[&at("p.html"), "road", "--out", &at("lit.xyz")]);
    assert_eq!(r.stderr, "ValueError: unknown file extension: .xyz\n");
    let r = run(&[&at("p.html"), "road", "--out", &at("lit")]);
    assert_eq!(r.stderr, "ValueError: unknown file extension: \n");
    let r = run(&[&at("p.html"), "road", "--out", &at("no/dir/lit.bmp")]);
    assert!(r.stderr.starts_with("FileNotFoundError: "), "{}", r.stderr);
    let r = run(&[&at("p.html"), "badpixels", "--out", &at("x.bmp")]);
    assert!(
        r.stderr.starts_with("PIL.UnidentifiedImageError: "),
        "{}",
        r.stderr
    );
}

/// The 16 x 14 frame PIL 12.3.0 wrote of [`gradient`]'s 300 x 260 shot, as RGB (a scratch probe, 2026-11-18, feature 449 T183).
const PIL_ICO_16: &str = "Z1kpmYQpZoApl2Qpa4IpkocpcEIpjV0pdYgph3ope2YpgYQpgYIpfDcphG4pgYIpoWWTbIeTk3eTanaTl3eTZouTnFGTYmmTn4aTX3aTonaTXHmTo4mTW0iTpHeTVoGTp26vXIOvo32vXYKvoXyvYIWvnWCvZG+vmYOvaH6vlIGvbnyvj4Svc1qvjXivZICvcXk4hYE4eX44iYg4dHw4joQ4bm44lHk4aX84mIA4ZYc4nXo4YYU4oGk4Xn84pnw4TH6zp4GzWYmzpYyzWoizpIGzW3qzo32zXYKzoIqzYIyznYazZIGzmXizZn+zpoGzgYeIiIKId4WIho+IfISIgIOIgoWIeoWIiIKIdIiIjo6IboKIk4OIaYaIloSIaoKIrYtEXX5EonJEXHhEpHJEW39EpY5EWolEpXxEWnJEpXdEW3REo4FEXZBEooVEUnxElZPHaHjHln3Ha23HkX7HcHnHjJnHdo/HhnfHfHrHgG/Hgn3HenzHiJzHeIjHfnjHWY9emXxeZoZemnNeY4lennheX5xeoYxeXH9epINeW3VepYleWnhepqNeWINes4NeWZNkoYdkX4hkn39kYopkm4RkZqBkl5Jka4hkkoVkcH9kjIxkdoNkh6VkeYtkj4tkmpDEc3HEi37EcYzEkXzEbG/ElqDEZ43EmnDEY4LEnorEX3nEoXLEXKjEooHEWXXEq40+Wng+pnY+WpA+pHQ+XHc+ops+Xo4+n3U+Yns+m40+ZnM+l3o+aqE+lYU+W3Y+fIGKfIeKgoKKgImKfIOKhoSKdouKi4SKcYeKkYKKbIiKloWKZ4GKmo+KZIGKmomKTmu4o364XYi4o3y4XIi4pH24W2S4pG24XIG4o4a4XX24oYe4X3q4n2C4X3O4rn+4";

/// How far the smallest frame's pixels differ from PIL's at most: the `image` crate's Lanczos3 against PIL's LANCZOS, 1 level on this shot
/// (measured 2026-11-18, feature 449 T183: every frame of four shots against PIL's, `scratchpad/t183/ico-measure.json`; the 256 px frame
/// of this deliberately aliasing gradient 19 levels at most, 0.86% of its samples past 3, a 1280 x 800 one's 4 levels).
const ICO_LEVELS: u8 = 1;

/// A `w` x `h` RGB shot whose every pixel differs from its neighbors, as the PIL probe drew it.
fn gradient(w: u32, h: u32) -> Vec<u8> {
    let mut data = Vec::new();
    for y in 0..h {
        for x in 0..w {
            data.extend(
                [(x * 7 + y * 3) % 256, (x * x + y) % 256, (y * 5) % 256]
                    .map(|v| u8::try_from(v).unwrap()),
            );
        }
    }
    png_of(
        w,
        h,
        png::ColorType::Rgb,
        png::BitDepth::Eight,
        &data,
        None,
        None,
    )
}

/// An icon's frames as its directory lists them: (width, height, the frame's bytes).
fn frames(ico: &[u8]) -> Vec<(u32, u32, Vec<u8>)> {
    let n = usize::from(u16::from_le_bytes([ico[4], ico[5]]));
    (0..n)
        .map(|i| {
            let e = &ico[6 + 16 * i..22 + 16 * i];
            let side = |b: u8| if b == 0 { 256 } else { u32::from(b) };
            let len = u32::from_le_bytes([e[8], e[9], e[10], e[11]]) as usize;
            let at = u32::from_le_bytes([e[12], e[13], e[14], e[15]]) as usize;
            (side(e[0]), side(e[1]), ico[at..at + len].to_vec())
        })
        .collect()
}

/// FIXED (feature 449 T183, T150's finding): a shot past an icon's 256 px was refused by the encoder where PIL's `IcoImagePlugin`
/// shrank it. It is written as PIL wrote it - a frame for each of PIL's sizes that fits the shot, each a Lanczos thumbnail keeping
/// the shot's aspect at PIL's rounding - its pixels the `image` crate's Lanczos3, not PIL's; and a shot no size fits, of which PIL
/// wrote an icon with no image in it, is refused naming the format.
#[test]
fn an_icon_past_256_px_is_shrunk_into_pil_s_sizes() {
    let dir = l7r_guard::shared::tempdir::TempDir::new("lit-ico");
    let at = |n: &str| dir.path().join(n).to_string_lossy().into_owned();
    super::save(&at("big.ico"), &gradient(300, 260)).unwrap();
    let got = frames(&std::fs::read(at("big.ico")).unwrap());
    let sizes: Vec<(u32, u32)> = got.iter().map(|(w, h, _)| (*w, *h)).collect();
    assert_eq!(
        sizes,
        [
            (16, 14),
            (24, 21),
            (32, 28),
            (48, 42),
            (64, 55),
            (128, 111),
            (256, 222)
        ]
    );
    let small = crate::diagnostics::image::rgb(&got[0].2, "f").unwrap();
    let pil = crate::diagnostics::image::b64decode(PIL_ICO_16).unwrap();
    let worst = small
        .data
        .iter()
        .zip(&pil)
        .map(|(a, b)| a.abs_diff(*b))
        .max();
    assert_eq!((small.data.len(), worst), (pil.len(), Some(ICO_LEVELS)));
    // the other way up, and a strip only the smallest size fits
    super::save(&at("tall.ico"), &gradient(260, 300)).unwrap();
    assert_eq!(frames(&std::fs::read(at("tall.ico")).unwrap())[6].0, 222);
    super::save(&at("strip.ico"), &gradient(1000, 20)).unwrap();
    let strip = frames(&std::fs::read(at("strip.ico")).unwrap());
    assert_eq!(
        strip.iter().map(|(w, h, _)| (*w, *h)).collect::<Vec<_>>(),
        [(16, 1)]
    );
    // an encoder's own refusal stands in its words: a JPEG past 65,535 px a side (the ICO case that once reached it is now written)
    let wide = png_of(
        65_536,
        1,
        png::ColorType::Rgb,
        png::BitDepth::Eight,
        &vec![0; 3 * 65_536],
        None,
        None,
    );
    let e = super::save(&at("wide.jpg"), &wide).unwrap_err();
    assert_eq!(
        (
            e.kind,
            e.message
                .starts_with(&format!("cannot write {}: ", at("wide.jpg")))
        ),
        ("OSError", true)
    );
    let e = super::save(&at("line.ico"), &gradient(300, 1)).unwrap_err();
    assert_eq!(
        (e.kind, e.message),
        (
            "OSError",
            format!("cannot write {}: an ICO's smallest image is 16 x 16 px and the lit shot is 300 x 1 px, so no size of PIL's fits it", at("line.ico"))
        )
    );
}
