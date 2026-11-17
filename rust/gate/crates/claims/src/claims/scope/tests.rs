//! The Python half asked only when a `.py` file it reads changed: a kept answer read back, a changed file asking again, the kept file
//! capped; every unit in the Python's order.

use super::{all_units, cache_off, Reader};
use crate::claims::tests::{fixture, py_units};
use crate::record::testkit::put;

#[test]
fn the_python_half_is_asked_once_for_a_tree_it_has_read() {
    let root = fixture("claims-scope");
    py_units(
        &root,
        &[("in", "function", &["i - NONE"], false)],
        &[("out", "function", &["o - NONE"], false)],
    );
    let order = |r: &mut Reader| {
        all_units(r, &root, false, true)
            .unwrap()
            .iter()
            .map(|(u, _)| u.uid())
            .collect::<Vec<_>>()
    };
    let mut reader = Reader::new(&root, &root);
    let first = order(&mut reader);
    assert_eq!(first[0], "l7r/diagram/m.py::in");
    assert_eq!(first[first.len() - 3], "l7r/diagram/m.py::out");
    assert!(first.last().unwrap().starts_with("docs/buildings.md::"));
    drop(reader);
    let kept = root.join(".git/l7r-cache/claims-py-units.json");
    assert!(kept.is_file());
    put(&root, "scripts/bundle_door.py", "raise SystemExit(1)\n");
    let mut reader = Reader::new(&root, &root);
    assert!(all_units(&mut reader, &root, false, true).is_err());
    put(
        &root,
        "scripts/bundle_door.py",
        crate::claims::tests::RUNNER,
    );
    let mut reader = Reader::new(&root, &root);
    assert_eq!(order(&mut reader), first);
    reader.save();
}

/// The kept file capped: four answers kept for four earlier `.py` trees, written as the reader keys them, and a fifth tree asked - the
/// file holds four, the newest first. Feature 449 T167: the test asked the Python half for six trees one after another, a 16 ms start
/// each, over FR-008's tenth of a second; the four kept before are written here, so one start asks the fifth.
#[test]
fn the_kept_answers_are_capped_at_four() {
    let root = fixture("claims-scope-cap");
    py_units(
        &root,
        &[("in", "function", &["i - NONE"], false)],
        &[("out", "function", &["o - NONE"], false)],
    );
    let kept = root.join(".git/l7r-cache/claims-py-units.json");
    let mut held = serde_json::Map::new();
    let skill = root.to_path_buf();
    for i in 0..4 {
        put(&root, "l7r/diagram/m.py", &format!("GAP = {i}\n"));
        let earlier = Reader::new(&root, &root);
        let files = vec![skill.join("l7r/diagram/m.py")];
        let key = earlier.key(&skill, false, true, &files).unwrap();
        held.insert(key, serde_json::json!([[], []]));
    }
    put(
        &root,
        ".git/l7r-cache/claims-py-units.json",
        &serde_json::Value::Object(held).to_string(),
    );
    put(&root, "l7r/diagram/m.py", "GAP = 4\n");
    let mut r = Reader::new(&root, &root);
    assert!(!all_units(&mut r, &root, false, true).unwrap().is_empty());
    drop(r);
    let held: serde_json::Value =
        serde_json::from_str(&std::fs::read_to_string(&kept).unwrap()).unwrap();
    assert_eq!(held.as_object().unwrap().len(), 4);
}

/// The scope's last part, on a tree of its own (feature 449 T167, as above): no Python module asks nothing, and one that cannot be
/// read fails.
#[test]
fn a_tree_with_no_python_module_asks_nothing_and_one_it_cannot_read_fails() {
    let root = fixture("claims-scope-none");
    std::fs::remove_file(root.join("l7r/diagram/m.py")).unwrap();
    let order = |r: &mut Reader| {
        all_units(r, &root, false, true)
            .unwrap()
            .iter()
            .map(|(u, _)| u.uid())
            .collect::<Vec<_>>()
    };
    let mut reader = Reader::new(&root, &root);
    assert!(!order(&mut reader).iter().any(|u| u.starts_with("l7r/")));
    let plain = crate::checks::scratch("claims-scope-plain");
    let mut r = Reader::new(&root, &plain);
    assert!(r.py_units(&plain, false, true).unwrap().0.is_empty());
    r.save();
    put(&plain, "l7r/diagram/x.py", "");
    std::os::unix::fs::symlink("/no/such/file", plain.join("l7r/diagram/y.py")).unwrap();
    assert!(r.py_units(&plain, false, true).is_err());
    assert!(!cache_off());
}

#[test]
fn the_cache_switch_reads_as_the_python_reads_it() {
    assert!(
        super::off(Some("1"))
            && !super::off(Some("0"))
            && !super::off(Some(""))
            && !super::off(None)
    );
}
