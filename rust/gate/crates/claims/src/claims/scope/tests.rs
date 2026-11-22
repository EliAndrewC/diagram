//! Every unit in scope in the Python's order: the Rust's, then the procedure sections; a `.py` file is read no more (feature 449 T158).

use super::all_units;
use crate::claims::tests::fixture;
use crate::record::testkit::put;

#[test]
fn the_units_are_the_rust_then_the_sections_and_a_python_file_is_not_read() {
    let root = fixture("claims-scope");
    put(
        &root,
        "l7r/diagram/m.py",
        "\"\"\"Research: m - NONE\"\"\"\n",
    );
    let got: Vec<String> = all_units(&root, true)
        .unwrap()
        .iter()
        .map(|(u, _)| u.uid())
        .collect();
    assert!(got[0].starts_with("rust/phases/src/lib.rs::"));
    assert!(got.last().unwrap().starts_with("docs/buildings.md::"));
    assert!(!got.iter().any(|u| u.starts_with("l7r/")));
    std::fs::remove_file(root.join("docs/buildings.md")).unwrap();
    assert!(!all_units(&root, false)
        .unwrap()
        .iter()
        .any(|(u, _)| u.path.starts_with("docs/")));
    std::fs::write(root.join("docs/buildings.md"), [0xff_u8]).unwrap();
    assert!(all_units(&root, true).is_err());
}
