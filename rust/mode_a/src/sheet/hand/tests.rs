//! The hand sheet driver (feature 449 T151): a small sheet drawn whole - placed, rendered or not, its page written, its census judged -
//! and each refusal; the real country shrine drawn by it is the crate's end-to-end test's (`parse/lockstep.rs`).
//!
//! Research: the hand sheet driver's tests - NONE: fixtures and assertions, deciding nothing about a building

use std::path::Path;

use l7r_gate_registry::about::FeatureClass;
use serde_json::Value;

use super::{main, parse, py_list, run};
use crate::raster::Host;

fn words(w: &[&str]) -> Vec<String> {
    w.iter().map(|s| (*s).to_owned()).collect()
}

/// A wide, short sheet (its picture 2400 px wide is 2400 x 24) with one building and its caption, which the placer seats.
const SHEET: &str = r##"<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 4">
  <rect x="0" y="0" width="400" height="4" fill="#EFE3C2" data-kind="-"/>
  <rect x="100" y="0" width="200" height="4" fill="#DDB87A" data-kind="well" data-id="w"/>
  <text x="0" y="3" font-size="2" data-kind="well" data-names="w">well</text>
</svg>
"##;

/// One kind of the sheet's vocabulary, built here: the whole registry's modal files would take a test past FR-008's tenth of a second.
#[expect(
    clippy::unnecessary_wraps,
    reason = "the registry reader's signature, which the command takes"
)]
fn well(_: &Path) -> Result<Vec<FeatureClass>, l7r_gate_research::Error> {
    Ok(vec![FeatureClass {
        key: "well".into(),
        name: "Well".into(),
        ..Default::default()
    }])
}

#[test]
fn the_arguments_are_one_sheet_and_where_its_placed_text_goes() {
    assert_eq!(parse(&words(&["a.svg"])), Some(("a.svg", None)));
    assert_eq!(
        parse(&words(&["a.svg", "--placed", "o.svg"])),
        Some(("a.svg", Some("o.svg")))
    );
    assert_eq!(
        parse(&words(&["--placed", "o.svg", "a.svg"])),
        Some(("a.svg", Some("o.svg")))
    );
    for bad in [
        &[][..],
        &["--placed"],
        &["a.svg", "b.svg"],
        &["a.svg", "--x", "o.svg"],
        &["--placed", "o.svg", "--x"],
        &["--x"],
    ] {
        assert_eq!(parse(&words(bad)), None, "{bad:?}");
    }
    assert_eq!(
        py_list(&words(&["a", "it's"])),
        "['a', \"it's\"]".to_owned()
    );
}

#[test]
fn a_sheet_is_placed_rendered_and_paged_and_its_reads_listed() {
    let _log = crate::reads::taker();
    let tree = Path::new(env!("CARGO_MANIFEST_DIR")).join("../..");
    let dir = l7r_guard::shared::tempdir::TempDir::new("hand-sheet");
    let svg = dir.path().join("shrine.svg");
    std::fs::write(&svg, SHEET).unwrap();
    let at = svg.to_string_lossy().into_owned();
    let out = dir.path().join("placed.svg").to_string_lossy().into_owned();
    // the switch set: the page alone, no picture
    let skip = Host {
        vars: vec![("DIAGRAM_SKIP_RENDER".into(), "1".into())],
        ..Host::default()
    };
    let r = run(&words(&[&at, "--placed", &out]), &tree, &skip, &well);
    assert_eq!((r.code, r.stderr.as_str()), (0, ""));
    let v: Value = serde_json::from_str(&r.stdout).unwrap();
    assert_eq!(v["counts"], serde_json::json!([["-", 1], ["well", 2]]));
    let reads: Vec<&str> = v["reads"]
        .as_array()
        .unwrap()
        .iter()
        .map(|p| p.as_str().unwrap())
        .collect();
    assert!(reads.contains(&at.as_str()), "{reads:?}");
    let placed = std::fs::read_to_string(&out).unwrap();
    assert_eq!(placed, crate::caption_place::placed(SHEET).unwrap());
    assert_ne!(placed, SHEET);
    let html = std::fs::read_to_string(dir.path().join("shrine.html")).unwrap();
    assert!(html.contains("<title>Shrine - interactive map</title>"));
    assert!(!dir.path().join("shrine.png").exists());
    // the switch unset: the picture too, at the sheets' 2400 px width
    let r = run(&words(&[&at]), &tree, &Host::default(), &well);
    assert_eq!(r.code, 0, "{}", r.stderr);
    let png = std::fs::read(dir.path().join("shrine.png")).unwrap();
    assert_eq!(&png[16..24], &[0, 0, 9, 96, 0, 0, 0, 24]);
}

#[test]
fn a_census_that_fails_and_each_refusal_end_the_run() {
    let _log = crate::reads::taker();
    let tree = Path::new(env!("CARGO_MANIFEST_DIR")).join("../..");
    let dir = l7r_guard::shared::tempdir::TempDir::new("hand-sheet-refused");
    let at = |name: &str| dir.path().join(name).to_string_lossy().into_owned();
    let skip = Host {
        vars: vec![("DIAGRAM_SKIP_RENDER".into(), "1".into())],
        ..Host::default()
    };
    std::fs::write(
        at("bad.svg"),
        "<svg viewBox=\"0 0 9 9\"><rect data-kind=\"nope\"/><circle/></svg>",
    )
    .unwrap();
    let r = run(&words(&[&at("bad.svg")]), &tree, &skip, &well);
    assert_eq!(r.code, 1);
    assert!(
        r.stderr
            .starts_with("bad.svg: untagged ink ['<circle> <circle/>']")
            && r.stderr.ends_with("; unknown kinds ['nope']\n"),
        "{}",
        r.stderr
    );
    assert!(r.stdout.contains("\"reads\""));
    let r = run(&words(&[&at("none.svg")]), &tree, &skip, &well);
    assert_eq!(
        (r.code, r.stderr.starts_with("FileNotFoundError: [Errno 2]")),
        (1, true)
    );
    assert!(r
        .stdout
        .starts_with("{\"error\":{\"kind\":\"FileNotFoundError\""));
    let nowhere = at("no/dir/placed.svg");
    let r = run(
        &words(&[&at("bad.svg"), "--placed", &nowhere]),
        &tree,
        &skip,
        &well,
    );
    assert_eq!(
        (r.code, r.stderr.starts_with("FileNotFoundError: ")),
        (1, true)
    );
    assert_eq!(run(&[], &tree, &skip, &well).code, 2);
    // the command's own registry, read from a tree with no modal files: the refusal, not the page
    let r = main(&words(&[&at("bad.svg")]), dir.path(), &skip);
    assert_eq!(r.code, 1);
}
