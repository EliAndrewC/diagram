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
    for i in 0..5 {
        put(&root, "l7r/diagram/m.py", &format!("GAP = {i}\n"));
        let mut r = Reader::new(&root, &root);
        let _ = order(&mut r);
    }
    let held: serde_json::Value =
        serde_json::from_str(&std::fs::read_to_string(&kept).unwrap()).unwrap();
    assert_eq!(held.as_object().unwrap().len(), 4);
    std::fs::remove_file(root.join("l7r/diagram/m.py")).unwrap();
    std::fs::remove_file(root.join("l7r/py-units.json")).unwrap();
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
