//! A Rust stage's own findings split from the rest, and the rest filed once.

use super::{changed_lines, file_left, git_diff, split, CLAIMS_FEATURE_DIR};
use crate::claims::scope::Reader;
use crate::claims::tests::fixture;
use crate::record::testkit::{commit, put};

#[test]
fn a_landing_answers_for_its_own_findings() {
    let root = fixture("claims-seam");
    put(
        &root,
        "l7r/diagram/s.py",
        "{\"own\": [1, 3], \"Cls\": [5, 9]}\n",
    );
    put(&root, "l7r/diagram/t.py", "not json\n");
    commit(&root, "seam base");
    put(
        &root,
        "l7r/diagram/s.py",
        "{\"own\": [1, 3], \"Cls\": [5, 9]}\nchanged\n",
    );
    put(&root, "l7r/diagram/t.py", "not json\nmore\n");
    commit(&root, "seam edit");
    assert_eq!(
        changed_lines("@@ -1 +2,0 @@\n@@ -3,2 +4,3 @@\n@@ -9 +9 @@"),
        vec![(2, 2), (4, 6), (9, 9)]
    );
    assert!(git_diff(&root, "l7r/diagram/s.py").contains("+changed"));
    let report = "claims: 3 in scope\n  DRIFTED        l7r/diagram/m.py::read#x - seam\n  DRIFTED        rust/phases/src/lib.rs::GAP#g - rust\n  DRIFTED        l7r/diagram/s.py::own#o - hit\n  MISLABELED     l7r/diagram/s.py::Cls.m#c - miss\n  DRIFTED        l7r/diagram/t.py::f#o - unknown\n  DRIFTED        l7r/diagram/gone.py::f#o - gone\n  DRIFTED        docs/x.md::y#z - not changed\nUNRESEARCHED claims\n";
    let changed: Vec<String> = [
        "rust/phases/src/lib.rs",
        "l7r/diagram/s.py",
        "l7r/diagram/t.py",
        "l7r/diagram/gone.py",
    ]
    .map(str::to_owned)
    .to_vec();
    let mut reader = Reader::new(&root, &root);
    let (own, left) = split(
        &mut reader,
        &root,
        report,
        &changed,
        &["l7r/diagram/m.py".to_owned()],
    )
    .unwrap();
    assert_eq!(
        own,
        vec![
            "DRIFTED        l7r/diagram/m.py::read#x - seam",
            "DRIFTED        rust/phases/src/lib.rs::GAP#g - rust",
            "DRIFTED        l7r/diagram/s.py::own#o - hit"
        ]
    );
    assert_eq!(left.len(), 3);
    put(
        &root,
        &format!("{CLAIMS_FEATURE_DIR}/found.jsonl"),
        &format!("{{\"finding\": \"{}\"}}\n\n", left[0]),
    );
    assert_eq!(file_left(&root, "T9", &left).unwrap(), 2);
    let found = std::fs::read_to_string(root.join(CLAIMS_FEATURE_DIR).join("found.jsonl")).unwrap();
    assert!(
        found.contains("\"from\": \"feature 444 T9's landing (FR-021: not the stage's own code)\"")
            && found.contains("\"block\": \"f\"")
    );
    assert_eq!(file_left(&root, "T9", &left).unwrap(), 0);
    assert_eq!(
        file_left(&root, "T9", &["no finding form".to_owned()]).unwrap(),
        1
    );
    assert!(
        std::fs::read_to_string(root.join(CLAIMS_FEATURE_DIR).join("found.jsonl"))
            .unwrap()
            .contains("\"file\": \"?\"")
    );
    put(&root, &format!("{CLAIMS_FEATURE_DIR}/found.jsonl"), "{\n");
    assert!(file_left(&root, "T9", &left).is_err());
}
