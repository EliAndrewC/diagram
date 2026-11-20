//! A sheet's page written (feature 449 T150); the page lockstep holds each pool sheet's pieces, census and page to the Python's.
//!
//! Research: the sheet page's tests - NONE: fixtures and assertions, deciding nothing about a building

use std::path::Path;

use super::{py_title, title_of, write_sheet_page};
use crate::raster::Host;

#[test]
fn a_sheet_s_page_is_written_beside_it_and_its_census_returned() {
    let tree = Path::new(env!("CARGO_MANIFEST_DIR")).join("../..");
    // one kind of the sheet's vocabulary, built here: the whole registry's modal files took the test near FR-008's bar
    let registry = [l7r_gate_registry::about::FeatureClass {
        key: "well".into(),
        name: "Well".into(),
        ..Default::default()
    }];
    let dir = l7r_guard::shared::tempdir::TempDir::new("sheet-page");
    let svg = dir.path().join("karo-plan.svg");
    std::fs::write(
        &svg,
        "<svg viewBox=\"0 0 9 9\"><rect data-kind=\"well\"/><circle/></svg>",
    )
    .unwrap();
    let host = Host {
        vars: vec![("DIAGRAM_SKIP_RENDER".into(), "1".into())],
        ..Host::default()
    };
    let at = svg.to_string_lossy().into_owned();
    let census = write_sheet_page(&tree, &host, &at, &registry, None, None, None).unwrap();
    assert_eq!(
        (
            census.counts.len(),
            census.unclassed.len(),
            census.unregistered.len()
        ),
        (1, 1, 0)
    );
    let html = std::fs::read_to_string(dir.path().join("karo-plan.html")).unwrap();
    assert!(
        html.contains("<svg id=\"map\" data-sheet=\"mode-a\" viewBox")
            && html.contains("\"raster\": {\"r\": 0}")
    );
    assert!(html.contains("<title>Karo Plan - interactive map</title>"));
    std::fs::create_dir_all(dir.path().join("out")).unwrap();
    let given = write_sheet_page(
        &tree,
        &host,
        &at,
        &registry,
        Some(false),
        Some("<svg><rect data-kind=\"nope\"/></svg>"),
        Some(&dir.path().join("out")),
    )
    .unwrap();
    assert_eq!(given.unregistered, ["nope"]);
    // `out` (feature 449 T221): the page written there, under the sheet's name
    assert!(dir.path().join("out/karo-plan.html").is_file());
    let missing = dir.path().join("none.svg").to_string_lossy().into_owned();
    assert_eq!(
        write_sheet_page(&tree, &host, &missing, &registry, None, None, None)
            .unwrap_err()
            .kind,
        "FileNotFoundError"
    );
    assert_eq!(
        (title_of("a/ochiba-manor.svg"), py_title("3d plan o'neil")),
        ("Ochiba Manor".to_owned(), "3D Plan O'Neil".to_owned())
    );
}
