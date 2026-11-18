//! The page writer's own edges (feature 449 T150); the page writer's cases are held to the Python's answers by
//! `page/held.rs` (part B: the pinned answers, and the live-tree outcomes in the end-to-end test).
//!
//! Research: the page writer's tests - NONE: fixtures and assertions, deciding nothing about a building

use std::path::Path;

use serde_json::json;

use super::{asset, ink_census, meta_str, rendered_text, Page};
use crate::tags::ClsTag;

fn real() -> std::path::PathBuf {
    Path::new(env!("CARGO_MANIFEST_DIR")).join("../..")
}

#[test]
fn the_census_names_an_unclassed_piece_by_its_first_ink() {
    let (_, unclassed) = ink_census(&["<g><text>a</text></g>".to_owned()], &[ClsTag::Unruled]);
    assert_eq!(unclassed, ["<text> <g><text>a</text></g>"]);
    let missing = asset(Path::new("/nowhere"), "page.css").unwrap_err();
    assert_eq!(missing.kind, "FileNotFoundError");
    assert_eq!(meta_str(&serde_json::Map::new(), "scale"), "");
}

#[test]
fn only_words_the_reader_sees_are_rendered() {
    let entry = json!({"name": "a", "plain": true, "about": ["b", 3], "questions": [{"text": "q"}], "n": 4, "siblings": ["s"]});
    assert_eq!(rendered_text(entry.as_object().unwrap()), "a b");
}

#[test]
fn a_page_is_written_beside_its_map_with_its_notes() {
    let dir = l7r_guard::shared::tempdir::TempDir::new("page-write");
    std::fs::write(
        dir.path().join("m.notes.md"),
        "## Map notes\n### Features\n- **well**: the map's own.\n",
    )
    .unwrap();
    // one kind of the sheet's vocabulary, built here: the whole registry's modal files took the test near FR-008's bar
    let registry = [l7r_gate_registry::about::FeatureClass {
        key: "well".into(),
        name: "Well".into(),
        ..Default::default()
    }];
    let page = |name| Page {
        strings: vec!["<svg>".into(), "<rect/>".into(), "</svg>".into()],
        tags: vec![ClsTag::key("-"), ClsTag::key("well"), ClsTag::key("-")],
        name,
        meta: None,
        manifest: None,
        notes: crate::notes::MapNotes::default(),
        with_raster: false,
        registry: &registry,
        within: None,
    };
    let host = crate::raster::Host::default();
    let at = dir.path().join("m.html");
    super::write_html(&real(), &host, &at, page("M")).unwrap();
    let html = std::fs::read_to_string(&at).unwrap();
    assert!(html.contains("<title>M - interactive map</title>") && html.contains("the map's own."));
    // a path that is no `.html` reads no notes, and one that cannot be written is the Python's error
    super::write_html(&real(), &host, &dir.path().join("m.txt"), page("T")).unwrap();
    assert!(!std::fs::read_to_string(dir.path().join("m.txt"))
        .unwrap()
        .contains("the map's own."));
    let e =
        super::write_html(&real(), &host, &dir.path().join("no/such.html"), page("N")).unwrap_err();
    assert_eq!(e.kind, "FileNotFoundError");
}
