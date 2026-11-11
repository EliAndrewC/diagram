//! The numbers that are ours: the list, its counts, the inline audit over the Rust and (through the runner) the Python.

use std::collections::HashMap;

use super::{fmt_g, render, render_inline, tunables, unstated_rust};
use crate::claims::index::current;
use crate::claims::scope::Reader;
use crate::claims::tests::{fixture, py_units, LIB};
use crate::record::testkit::put;

#[test]
fn a_number_is_written_as_python_writes_it() {
    for (v, s) in [
        (12.5, "12.5"),
        (1_234_567.0, "1.23457e+06"),
        (999_999.5, "1e+06"),
        (0.0001, "0.0001"),
        (0.000_01, "1e-05"),
        (100.0, "100"),
        (0.0, "0"),
        (-0.0, "-0"),
        (-2.5, "-2.5"),
        (f64::INFINITY, "inf"),
        (f64::NEG_INFINITY, "-inf"),
    ] {
        assert_eq!(fmt_g(v), s, "{v}");
    }
}

#[test]
fn the_list_and_the_inline_audit() {
    let root = fixture("claims-tunables");
    py_units(
        &root,
        &[],
        &[
            (
                "helper",
                "function",
                &["help - CONVENTION: 3 households"],
                false,
            ),
            ("plain", "function", &["plain - UNRESEARCHED"], false),
        ],
    );
    put(&root, "l7r/diagram/labels/x.py", "4.5\n");
    put(&root, "l7r/diagram/other.py", "4.5\n");
    let mut reader = Reader::new(&root, &root);
    let cur = current(&mut reader, &root, &root.join("research/questions")).unwrap();
    let found = tunables(&cur, "", true);
    assert_eq!(
        found.iter().map(|f| f.1.as_str()).collect::<Vec<_>>(),
        vec![
            "rust/phases/src/lib.rs::Thing.m#method guess",
            "l7r/diagram/m.py::helper#help"
        ]
    );
    assert_eq!(tunables(&cur, "", false).len(), 4);
    assert!(tunables(&cur, "nothing/", true).is_empty());
    assert_eq!(render(&[], false), "tunables: none - values no source states: a goal and a knob, never a target to defend (docs/approach-checklist.md A3)");
    let text = render(&found, false);
    assert!(text.starts_with("tunables: GUESS 1, CONVENTION 1 - ") && text.contains("\n  GUESS        rust/phases/src/lib.rs::Thing.m#method guess - wider than the page, 40 ft"), "{text}");
    assert_eq!(render(&found, true).lines().count(), 1);
    let inline = super::inline(&mut reader, &root, &cur, "").unwrap();
    let shown = render_inline(&inline, false);
    assert!(
        shown.contains("  l7r/diagram/labels/x.py:3 fn 4.5")
            && shown.contains("  l7r/diagram/labels/x.py:4 big 1.23457e+06")
            && shown.contains("  rust/phases/src/lib.rs:14 reach 3.25")
            && shown.contains("  rust/phases/src/lib.rs:23 m 42")
            && !shown.contains("8888")
            && !shown.contains("other.py"),
        "{shown}"
    );
    let counted = render_inline(&inline, true);
    assert!(
        counted.contains("      2  l7r/diagram/labels/x.py\n")
            || counted.contains("    2  l7r/diagram/labels/x.py"),
        "{counted}"
    );
    assert!(super::inline(&mut reader, &root, &cur, "rust/")
        .unwrap()
        .iter()
        .all(|f| f.0.starts_with("rust/")));
    let text: HashMap<String, String> =
        HashMap::from([("reach".to_owned(), " reach 3.25".to_owned())]);
    let got = unstated_rust(LIB, &text);
    assert!(got
        .iter()
        .all(|(f, _, v)| !(f == "reach" && (*v - 3.25).abs() < 1e-9)));
    assert!(unstated_rust(
        "fn a() { let b = [0; 2]; b[7]; let s = \"999\"; // 555\n}",
        &HashMap::new()
    )
    .is_empty());
}
