//! The bundle: the lines a delta changed, marked; a context reference a Rust item; the failures it reports.

use std::collections::HashSet;

use super::{bundle, changed_lines, mark_changed};
use crate::claims::index::current;
use crate::claims::tests::{claims, fixture};
use crate::record::testkit::{commit, git, put};

#[test]
fn the_lines_a_delta_changed_are_marked() {
    let root = fixture("claims-bundle-marks");
    assert!(changed_lines(&root, "origin/main").is_empty());
    let lib = std::fs::read_to_string(root.join("rust/phases/src/lib.rs")).unwrap();
    std::fs::write(
        root.join("rust/phases/src/lib.rs"),
        lib.replace(
            "    x + GAP + y",
            "    x + GAP + y + 1.0\n    // and more\n    // still",
        ),
    )
    .unwrap();
    put(&root, "rust/phases/src/new.rs", "pub fn n() {}\n");
    commit(&root, "changed");
    std::fs::remove_file(root.join("docs/buildings.md")).unwrap();
    let got = changed_lines(&root, "origin/main");
    assert_eq!(got["rust/phases/src/lib.rs"], HashSet::from([15, 16, 17]));
    assert_eq!(got["rust/phases/src/new.rs"], HashSet::from([1]));
    assert!(!got.contains_key("docs/buildings.md"));
    assert!(changed_lines(&root, "no-such-base").is_empty());
    assert_eq!(
        mark_changed("a\nb", 10, Some(&HashSet::from([11]))),
        "  a\n+ b"
    );
    assert_eq!(mark_changed("a\nb", 10, Some(&HashSet::from([99]))), "a\nb");
    assert_eq!(mark_changed("a", 1, None), "a");
    let o = root.join("b").to_string_lossy().into_owned();
    let got = claims(
        &root,
        &[
            "bundle",
            "--units",
            "rust/phases/src/lib.rs::reach#reach",
            "--out",
            &o,
        ],
    );
    assert_eq!(got.code, 0);
    let manifest = std::fs::read_to_string(root.join("b/MANIFEST.md")).unwrap();
    assert!(manifest.contains("+     x + GAP + y + 1.0\n") && manifest.contains("  pub fn reach"));
}

#[test]
fn a_context_reference_is_a_rust_item_and_a_gone_unit_fails() {
    let root = fixture("claims-bundle-ctx");
    let o = root.join("b").to_string_lossy().into_owned();
    // a `.py` reference's source was the Python's (feature 449 T158): it is refused, naming the form
    let got = claims(
        &root,
        &[
            "bundle",
            "--units",
            "rust/phases/src/lib.rs::reach#reach",
            "--with",
            "l7r/diagram/m.py::helper",
            "--reason",
            "a re check",
            "--out",
            &o,
        ],
    );
    assert_eq!(got.code, 1);
    assert!(
        got.stderr
            .contains("`l7r/diagram/m.py::helper` is not a Rust item"),
        "{}",
        got.stderr
    );
    let cur = current(&root, &root.join("research/questions")).unwrap();
    std::fs::remove_file(root.join("rust/phases/src/lib.rs")).unwrap();
    let err = bundle(
        &root,
        &cur,
        &["rust/phases/src/lib.rs::reach#reach".to_owned()],
        &root.join("c"),
        &[],
        &[],
    )
    .unwrap_err();
    assert!(err.starts_with("FileNotFoundError"));
    std::fs::create_dir_all(root.join("d")).unwrap();
    let err = bundle(
        &root,
        &cur,
        &["no#such".to_owned()],
        &root.join("d"),
        &[],
        &[],
    )
    .unwrap_err();
    assert_eq!(err, "KeyError: 'no#such'");
    git(&root, &["status"]);
}

/// A unit for the cited-pages test: its claim's account names a page its backing does not, and its guess names one in its account.
const DIKE: &str = "/// Research:
///     ring - research/questions/0001-gap.html: off the dike; research/questions/0002-other.drawing.html: the face pushed out
///     widest - GUESS: research/questions/0002-other.drawing.html: the breadth, held at its widest
pub fn ring() {}

/// Research: gone - GUESS: research/questions/0003-gone.drawing.html: a page the record never had
pub fn gone() {}
";

#[test]
fn every_page_a_claim_cites_is_in_its_bundle_or_the_bundle_refuses_naming_it() {
    // 449 T241: off_the_dike's claims cited 0027 in their accounts, and its bundle held only the pages its backings named
    let root = crate::claims::tests::fixture_with("claims-bundle-cited", &|r| {
        put(r, "rust/phases/src/dike.rs", DIKE);
    });
    let o = root.join("b").to_string_lossy().into_owned();
    let got = claims(
        &root,
        &[
            "bundle",
            "--units",
            "rust/phases/src/dike.rs::ring#ring,rust/phases/src/dike.rs::ring#widest",
            "--reason",
            "a re check",
            "--out",
            &o,
        ],
    );
    assert_eq!(got.code, 0, "{}", got.stderr);
    let held = root
        .join("b/questions/0002-other.drawing.html.txt")
        .is_file();
    assert!(held);
    let manifest = std::fs::read_to_string(root.join("b/MANIFEST.md")).unwrap();
    assert!(manifest.contains("`questions/0002-other.drawing.html.txt`"));
    // the page is in each claim's recorded pages too, so a reply's rests on its blocks are kept, never dropped as a page not cited
    let units: serde_json::Value =
        serde_json::from_str(&std::fs::read_to_string(root.join("b/units.json")).unwrap()).unwrap();
    let guess = units["rust/phases/src/dike.rs::ring#widest"]["pages"]
        .get("0002-other.drawing.html")
        .is_some();
    let account = units["rust/phases/src/dike.rs::ring#ring"]["pages"]
        .get("0002-other.drawing.html")
        .is_some();
    assert!(guess && account, "{units}");
    let o = root.join("c").to_string_lossy().into_owned();
    let got = claims(
        &root,
        &[
            "bundle",
            "--units",
            "rust/phases/src/dike.rs::gone#gone",
            "--reason",
            "a re check",
            "--out",
            &o,
        ],
    );
    let named = got
        .stderr
        .contains("research/questions/0003-gone.drawing.html");
    assert_eq!(got.code, 1, "{}", got.stderr);
    assert!(named, "{}", got.stderr);
}

#[test]
fn a_cannot_tell_verdict_s_backticked_names_are_chased() {
    let root = fixture("claims-bundle-asked");
    put(&root, "dev/claims-index.json", "{\"rust/phases/src/lib.rs::reach#reach\": {\"verdict\": \"CANNOT-TELL\", \"note\": \"needs `GAP`\"}}\n");
    let o = root.join("b").to_string_lossy().into_owned();
    let got = claims(
        &root,
        &[
            "bundle",
            "--units",
            "rust/phases/src/lib.rs::reach#reach",
            "--reason",
            "a re check",
            "--out",
            &o,
        ],
    );
    assert_eq!(got.code, 0, "{}", got.stderr);
}
