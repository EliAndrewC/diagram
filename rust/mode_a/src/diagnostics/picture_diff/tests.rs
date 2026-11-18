//! Two renders compared (feature 449 T150): the statistics, the per-class attribution through a page's id map or an SVG's, the
//! report's words, and the command line.
//!
//! Research:
//!     the diagnostics' tests - NONE: fixtures and assertions, no map decision

use std::fmt::Write as _;
use std::path::Path;

use super::{by_class, diff_stats, lookup, main, report, set, sorted_palette, Stats, OFF_CLASS};
use crate::diagnostics::image::tests::png_of;
use crate::raster::encode::Rgb;
use crate::raster::Host;

fn image(w: usize, h: usize, data: Vec<u8>) -> Rgb {
    Rgb {
        width: w,
        height: h,
        data,
    }
}

fn rgb_png(w: u32, h: u32, data: &[u8]) -> Vec<u8> {
    png_of(
        w,
        h,
        png::ColorType::Rgb,
        png::BitDepth::Eight,
        data,
        None,
        None,
    )
}

fn words(w: &[&str]) -> Vec<String> {
    w.iter().map(|s| (*s).to_owned()).collect()
}

fn resvg() -> Host {
    Host::default()
}

#[test]
fn the_statistics_are_numpy_s() {
    let a = image(3, 2, vec![0; 18]);
    let mut b = image(3, 2, vec![0; 18]);
    b.data[5] = 7; // (1, 0) blue by 7
    b.data[9] = 8; // (0, 1) red by 8: the box grows to hold both
    b.data[3 * 5] = 6; // (2, 1) red by 6: not over the threshold
    let s = diff_stats(&a, &b, 6).unwrap();
    assert_eq!(
        (s.pixels, s.differing, s.max_delta, s.bbox),
        (6, 2, 8, Some((0, 0, 1, 1)))
    );
    assert_eq!(diff_stats(&a, &a, 6).unwrap().bbox, None);
    let e = diff_stats(&a, &image(2, 3, vec![0; 18]), 6).unwrap_err();
    assert_eq!(
        e.message,
        "the renders differ in size: (3, 2) against (2, 3) - render the SVG at the other's width"
    );
    assert_eq!(
        report(&s, None),
        "differing: 2 of 6 px = 33.333%   max channel delta: 8/255\nbbox: (0, 0, 1, 1)"
    );
    assert!(report(&diff_stats(&a, &a, 6).unwrap(), Some(&[])).ends_with("bbox: none (identical)"));
}

#[test]
fn a_differing_pixel_is_counted_on_the_ink_under_it() {
    // a 4 x 2 picture at 2 px per map px over a 2 x 1 id map: the left half red 4 (road), the right 9 (off the grid's reach of 8)
    let s = Stats {
        width: 4,
        pixels: 8,
        differing: 4,
        max_delta: 9,
        bbox: Some((0, 0, 3, 1)),
        mask: vec![true, true, false, true, false, false, false, true],
    };
    let palette = sorted_palette(&[
        ((0, 8), "well".into()),
        ((0, 4), "road".into()),
        ((0, 4), "lane".into()),
    ]);
    // one row: the green channel is not read, as the Python never read it
    let classes = by_class(&s, (&[4, 11], &[200, 0]), 2, &palette, 2.0);
    assert_eq!(classes, [("lane".to_owned(), 2), (OFF_CLASS.to_owned(), 2)]);
    assert_eq!(
        report(&s, Some(&classes)),
        "differing: 4 of 8 px = 50.000%   max channel delta: 9/255\nbbox: (0, 0, 3, 1)\non the ink of:\n   50.0%          2  lane\n   50.0%          2  off any class"
    );
    // at half a picture px per map px, a pixel past the id map's two columns is off every class
    assert_eq!(
        by_class(&s, (&[4, 4], &[0, 0]), 2, &palette, 0.5),
        [("lane".to_owned(), 1), (OFF_CLASS.to_owned(), 3)]
    );
    let mut out = vec![("a".to_owned(), 1)];
    set(&mut out, "a", 3);
    set(&mut out, "b", 2);
    assert_eq!(out, [("a".to_owned(), 3), ("b".to_owned(), 2)]);
}

#[test]
fn the_lookup_takes_python_s_slices() {
    let at = |red: usize, green: usize| red * 256 + green;
    let lut = lookup(&[(0, 0), (0, 4), (0, 255)]);
    assert_eq!(
        (
            lut[at(0, 0)],
            lut[at(1, 9)],
            lut[at(2, 0)],
            lut[at(3, 0)],
            lut[at(5, 0)],
            lut[at(6, 0)],
            lut[at(254, 0)],
            lut[at(255, 255)]
        ),
        (0, 0, -1, 1, 1, -1, 2, 2)
    );
    // a value far below the palette's: its stop counts from the end, as a negative slice bound does
    let lut = lookup(&[(0, -5)]);
    assert_eq!(
        (lut[at(0, 0)], lut[at(252, 0)], lut[at(253, 0)]),
        (0, 0, -1)
    );
    assert_eq!(lookup(&[(0, 300)])[at(255, 0)], -1);
    // past the first row both channels answer: (red 4, green 4) is the second row's, (4, 0) the first's, (4, 9) neither's
    let lut = lookup(&[(0, 4), (4, 4)]);
    assert_eq!((lut[at(4, 0)], lut[at(4, 5)], lut[at(4, 9)]), (0, 1, -1));
}

#[test]
fn the_command_compares_pngs_and_svgs_and_refuses_as_the_python_did() {
    let dir = l7r_guard::shared::tempdir::TempDir::new("picture-diff");
    let at = |n: &str| dir.path().join(n).to_string_lossy().into_owned();
    let mut px = vec![255_u8; 40 * 40 * 3];
    std::fs::write(at("a.png"), rgb_png(40, 40, &px)).unwrap();
    px[0] = 0;
    std::fs::write(at("b.png"), rgb_png(40, 40, &px)).unwrap();
    std::fs::write(at("c.png"), rgb_png(2, 2, &[0; 12])).unwrap();
    let svg = "<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"40\" height=\"40\" viewBox=\"0 0 40 40\">\
               <g class=\"f f-well\" data-k=\"well\"><rect width=\"40\" height=\"40\" fill=\"#fff\"/></g></svg>";
    std::fs::write(at("d.svg"), svg).unwrap();
    std::fs::write(at("page.html"), "no id map here").unwrap();
    let host = resvg();
    let run = |w: &[&str]| main(&words(w), &host);
    let r = run(&[&at("a.png"), &at("b.png"), "--th", "0"]);
    assert_eq!(
        (r.code, r.stdout.as_str()),
        (
            0,
            "differing: 1 of 1600 px = 0.062%   max channel delta: 255/255\nbbox: (0, 0, 0, 0)\n"
        )
    );
    // an SVG first is rendered at the PNG's width; its own class groups answer whose ink
    let r = run(&[&at("d.svg"), &at("b.png"), "--svg", &at("d.svg")]);
    assert!(
        r.stdout.ends_with(
            "on the ink of:\n  100.0%          1  well\n    0.0%          0  off any class\n"
        ),
        "{}",
        r.stdout
    );
    let r = run(&[
        &at("d.svg"),
        &at("d.svg"),
        "--page",
        &at("page.html"),
        "--svg",
        "",
    ]);
    assert!(
        r.stdout.starts_with("differing: 0 of 1600 px"),
        "{}",
        r.stdout
    );
    let r = run(&[&at("a.png"), &at("b.png"), "--page", &at("page.html")]);
    assert!(!r.stdout.contains("on the ink"));
    let r = run(&[&at("a.png"), &at("b.png"), "--svg", &at("a.png")]);
    assert_eq!(r.code, 1, "an svg source that is no text");
    let r = run(&[&at("a.png"), &at("c.png")]);
    assert!(r
        .stderr
        .starts_with("ValueError: the renders differ in size"));
    let r = run(&[&at("none.png"), &at("c.png")]);
    assert!(r.stderr.starts_with("FileNotFoundError: [Errno 2]"));
    assert_eq!(run(&["--help"]).code, 0);
    for bad in [
        &["a"][..],
        &["a", "b", "c"],
        &["a", "b", "--threshold", "x"],
        &["a", "b", "--bogus"],
    ] {
        let r = run(bad);
        assert_eq!((r.code, r.stdout.as_str()), (2, ""), "{bad:?}");
    }
    assert!(Path::new(&at("a.png")).is_file());
}

#[test]
fn the_ink_is_read_off_a_page_s_id_map_or_an_svg_s() {
    let dir = l7r_guard::shared::tempdir::TempDir::new("picture-diff-ink");
    let at = |n: &str| dir.path().join(n).to_string_lossy().into_owned();
    let mut px = vec![255_u8; 40 * 40 * 3];
    std::fs::write(at("a.png"), rgb_png(40, 40, &px)).unwrap();
    px[0] = 0;
    std::fs::write(at("b.png"), rgb_png(40, 40, &px)).unwrap();
    let host = resvg();
    let run = |w: &[&str]| main(&words(w), &host);
    // an SVG source with no class group attributes nothing; an SVG render missing is the open's refusal
    let svg = "<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"4\" height=\"4\"/>";
    std::fs::write(at("plain.svg"), svg).unwrap();
    let r = run(&[&at("a.png"), &at("b.png"), "--svg", &at("plain.svg")]);
    assert!(r.stdout.ends_with("bbox: (0, 0, 0, 0)\n"), "{}", r.stdout);
    assert!(run(&[&at("none.svg"), &at("a.png")])
        .stderr
        .starts_with("FileNotFoundError: "));
    // the page's own id map answers
    let idmap = rgb_png(40, 40, &[4; 40 * 40 * 3]);
    let page = format!(
        "\"idmap\": \"data:image/png;base64,{}\", \"palette\": {{\"4\": \"well\"}}, \"step\": 4",
        crate::raster::encode::base64(&idmap)
    );
    std::fs::write(at("lit.html"), page).unwrap();
    let r = run(&[&at("a.png"), &at("b.png"), "--page", &at("lit.html")]);
    assert!(
        r.stdout
            .ends_with("  100.0%          1  well\n    0.0%          0  off any class\n"),
        "{}",
        r.stdout
    );
    // a document past the palette's first row (63 kinds) keys a row `red,green`, which the Python's `int()` refused - fixed, and the
    // pixel answered by both channels: the 70th kind, on the second row, under the differing pixel
    let many = (0..70).fold(String::new(), |mut s, i| {
        let (x, y, side) = if i == 69 { (0, 0, 4) } else { (10 + i % 25, 10 + i / 25, 1) };
        let _ = write!(s, "<g class=\"f f-k{i}\" data-k=\"k{i}\"><rect x=\"{x}\" y=\"{y}\" width=\"{side}\" height=\"{side}\"/></g>");
        s
    });
    let doc = format!("<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"40\" height=\"40\" viewBox=\"0 0 40 40\">{many}</svg>");
    std::fs::write(at("many.svg"), doc).unwrap();
    let r = run(&[&at("a.png"), &at("b.png"), "--svg", &at("many.svg")]);
    let tail = "  100.0%          1  k69\n    0.0%          0  off any class\n";
    assert_eq!(&r.stdout[r.stdout.len().saturating_sub(tail.len())..], tail);
}
