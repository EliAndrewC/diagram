//! The bundle: the lines a delta changed, marked; a Python unit's context and what a CANNOT-TELL asked; the failures the Python raised.

use std::collections::HashSet;

use serde_json::json;

use super::{bundle, changed_lines, mark_changed};
use crate::claims::index::current;
use crate::claims::scope::Reader;
use crate::claims::tests::{claims, fixture, py_units};
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
fn a_python_unit_carries_what_it_calls_and_what_a_cannot_tell_asked() {
    let root = fixture("claims-bundle-py");
    py_units(
        &root,
        &[],
        &[
            ("near", "function", &["kept 3 ft off - NONE"], false),
            ("gone", "function", &["g - NONE"], false),
        ],
    );
    put(&root, "dev/claims-index.json", &json!({"l7r/diagram/m.py::near#kept 3 ft off": {"verdict": "CANNOT-TELL", "note": "needs `FAR_GAP` and `helper`"}}).to_string());
    let o = root.join("b").to_string_lossy().into_owned();
    let got = claims(
        &root,
        &[
            "bundle",
            "--units",
            "l7r/diagram/m.py::near#kept 3 ft off",
            "--reason",
            "a re check",
            "--out",
            &o,
        ],
    );
    assert_eq!(got.code, 0);
    let manifest = std::fs::read_to_string(root.join("b/MANIFEST.md")).unwrap();
    for want in [
        "## CONTEXT l7r/diagram/m.py::helper\n",
        "## CONTEXT l7r/diagram/m.py::FAR\n",
        "## CONTEXT l7r/diagram/m.py::FAR_GAP\n",
        "```python\ndef FAR_GAP(): pass\n",
    ] {
        assert!(manifest.contains(want), "{want}");
    }
    let mut reader = Reader::new(&root, &root);
    let cur = current(&mut reader, &root, &root.join("research/questions")).unwrap();
    std::fs::remove_file(root.join("l7r/diagram/m.py")).unwrap();
    put(&root, "l7r/diagram/other.py", "");
    let err = bundle(
        &mut reader,
        &root,
        &cur,
        &["l7r/diagram/m.py::gone#g".to_owned()],
        &root.join("c"),
        &[],
        &[],
    )
    .unwrap_err();
    assert!(err.starts_with("FileNotFoundError"));
    std::fs::create_dir_all(root.join("d")).unwrap();
    let err = bundle(
        &mut reader,
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
