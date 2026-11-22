//! The one-sheet sweep's tests (feature 449 T252): the reference map and a hand sheet passing by name, a generated exception composed
//! never read, each finding a line, and what is not a Mode A sheet refused.
//!
//! Research:
//!     the one-sheet sweep's tests - NONE: fixtures and assertions, deciding nothing about a building

use std::path::{Path, PathBuf};

use super::{judge, listed, main, sheet};

fn tree() -> PathBuf {
    Path::new(env!("CARGO_MANIFEST_DIR")).join("../..")
}

fn args(a: &[&str]) -> Vec<String> {
    a.iter().map(|s| (*s).to_owned()).collect()
}

/// The reference map of `make maps`' Mode A row (a generated compound, composed in process) and a hand sheet both pass by name.
#[test]
fn a_pool_sheet_named_passes_its_tiers_checks() {
    let r = main(
        &args(&[
            "county-magistracy-example",
            "pool/magistracies/ubame-magistracy",
        ]),
        &tree(),
    );
    assert_eq!((r.code, r.stderr.as_str()), (0, ""));
    assert!(r.stdout.contains("county-magistracy-example: clean"));
    assert!(r.stdout.contains("ubame-magistracy: clean"));
}

/// A generated exception is composed from its spec, not read from its svg on disk; a hand sheet is read as tracked.
#[test]
fn a_generated_exception_is_composed_and_a_hand_sheet_read() {
    let tree = tree();
    let w = l7r_gate_pool::walk(&tree);
    let composed = sheet(&tree, w.folder("county-magistracy-example").unwrap()).unwrap();
    assert!(composed.generated);
    // composed, never read: the same spec beside a sheet on disk that is not one
    let scratch = l7r_shared::tempdir::TempDir::new("mode-a-sweep-composed");
    let dir = scratch
        .path()
        .join("pool/magistracies/county-magistracy-example");
    std::fs::create_dir_all(&dir).unwrap();
    let spec = "county-magistracy-example.compound.json";
    std::fs::copy(
        tree.join("pool/magistracies/county-magistracy-example")
            .join(spec),
        dir.join(spec),
    )
    .unwrap();
    std::fs::write(dir.join("county-magistracy-example.svg"), "not the sheet").unwrap();
    let elsewhere = l7r_gate_pool::walk(scratch.path());
    let again = sheet(
        &tree,
        elsewhere.folder("county-magistracy-example").unwrap(),
    )
    .unwrap();
    assert_eq!(again.text, composed.text);
    let hand = sheet(&tree, w.folder("ubame-magistracy").unwrap()).unwrap();
    assert!(!hand.generated);
    let judged = judge(&tree, &hand.tier, &hand.svg, &hand.text).unwrap();
    assert_eq!(judged, Vec::<String>::new());
}

/// Findings are each a line, under the map's name, and fail the run; none is the map's clean line.
#[test]
fn each_finding_is_a_line_and_fails() {
    assert_eq!(
        listed(
            "m",
            &["a: b - fix: c".to_owned(), "d: e - fix: f".to_owned()]
        ),
        ("m: a: b - fix: c\nm: d: e - fix: f\n".to_owned(), true)
    );
    assert_eq!(listed("m", &[]), ("m: clean\n".to_owned(), false));
}

/// What is not a Mode A pool sheet is refused with the way to name one: no map, a hamlet, a frozen exhibit, a sheet with no svg.
#[test]
fn what_is_not_a_mode_a_sheet_is_refused() {
    let r = main(&args(&[]), &tree());
    assert_eq!(r.code, 2);
    assert!(r.stderr.starts_with("usage: l7r-mode-a sweep"));
    let r = main(&args(&["no-such-map"]), &tree());
    assert_eq!(r.code, 2);
    assert!(r.stderr.contains("no pool map is named no-such-map"));
    let r = main(&args(&["inashiro"]), &tree());
    assert_eq!(r.code, 2);
    assert!(r.stderr.contains("not a Mode A tier"));
}

/// A sheet whose svg is missing and is no declared generated exception is an error naming the fix; an unparseable sheet is the
/// uncaught error's line and exit 1.
#[test]
fn a_sheet_that_cannot_be_read_or_parsed_is_an_error() {
    let scratch = l7r_shared::tempdir::TempDir::new("mode-a-sweep");
    let root = scratch.path();
    std::fs::create_dir_all(root.join("l7r/diagram/buildings")).unwrap();
    std::fs::copy(
        tree().join("l7r/diagram/buildings/types.json"),
        root.join("l7r/diagram/buildings/types.json"),
    )
    .unwrap();
    let dir = root.join("pool/magistracies/broken-magistracy");
    std::fs::create_dir_all(&dir).unwrap();
    std::fs::write(dir.join("broken-magistracy.notes.md"), "notes\n").unwrap();
    let w = l7r_gate_pool::walk(root);
    let m = w.folder("broken-magistracy").unwrap();
    assert!(sheet(root, m).unwrap_err().message.contains("no svg"));
    let r = main(&args(&["broken-magistracy"]), root);
    assert_eq!(r.code, 1);
    assert!(r.stderr.contains("no svg"));
    std::fs::write(dir.join("broken-magistracy.svg"), "<not svg").unwrap();
    let r = main(&args(&["broken-magistracy"]), root);
    assert_eq!(r.code, 1);
    assert!(!r.stderr.is_empty());
}
