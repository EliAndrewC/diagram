//! The raster's host, its refusals and its renders' edges (feature 449 T150); part A's page lockstep held every
//! document and picture to the Python's (its Python deleted by part B, the cases' answers held by `page/held.rs`).
//!
//! Research: the raster's tests - NONE: fixtures and assertions, deciding nothing about a building

use super::{id_map_doc, picture, Host, PALETTE_MAX};
use crate::py::uncaught;

#[test]
fn a_host_is_read_from_the_process() {
    assert!(Host::current().vars.len() <= super::HOST_VARS.len());
}

#[test]
fn a_render_is_drawn_in_process_and_its_refusals_are_the_python_s() {
    let doc = "<svg viewBox=\"0 0 4 4\"><rect x=\"0\" fill=\"#123\"/></svg>";
    let args = |a: &[&str]| a.iter().map(|s| (*s).to_owned()).collect::<Vec<_>>();
    // a bare `<svg>` gets its namespace; a document naming no width is asked at its zoom alone
    let png = Host::default()
        .resvg_png(doc, &args(&["--zoom", "2"]))
        .unwrap();
    assert_eq!(crate::raster::encode::png_size(&png).unwrap(), (8, 8));
    let skip = Host {
        vars: vec![("DIAGRAM_SKIP_RENDER".into(), "1".into())],
        ..Host::default()
    };
    let refused = skip
        .resvg_png(doc, &args(&["--width", "2000"]))
        .unwrap_err();
    assert_eq!(refused.kind, "RenderedInATest");
    assert_eq!(
        uncaught(&skip.resvg_png(doc, &args(&["--width", "x"])).unwrap_err()),
        "ValueError: could not convert string to float: 'x'\n"
    );
    assert_eq!(
        Host::default()
            .resvg_png(doc, &args(&["--dpi", "1"]))
            .unwrap_err()
            .kind,
        "RuntimeError"
    );
    // a picture whole and tiled
    assert_eq!(
        &picture(&Host::default(), doc, 2.0, None).unwrap()[..2],
        [0xFF, 0xD8]
    );
    assert_eq!(
        &picture(&Host::default(), doc, 2.0, Some(2)).unwrap()[..2],
        [0xFF, 0xD8]
    );
}

#[test]
fn the_id_map_refuses_what_its_palette_cannot_hold() {
    let keys: Vec<String> = (0..=PALETTE_MAX).map(|i| i.to_string()).collect();
    assert_eq!(
        id_map_doc("<svg>", &keys).unwrap_err().message,
        format!(
            "{} classes on one page - past the id map's 4032-class palette",
            keys.len()
        )
    );
    // a class group inside a class group is painted with its outer one; a group the keys do not name is the Python's KeyError
    let nested =
        "<svg ><g class=\"f f-a\" data-k=\"a\"><g class=\"f f-b\" data-k=\"b\"></g></g></svg>";
    let (doc, palette) = id_map_doc(nested, &["a".into(), "b".into()]).unwrap();
    assert!(doc.contains("data-k=\"b\"") && palette.len() == 2);
    assert_eq!(
        id_map_doc(nested, &["b".into()]).unwrap_err().kind,
        "KeyError"
    );
}
