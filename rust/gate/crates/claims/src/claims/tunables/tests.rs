//! The numbers that are ours: the list, its counts, the inline audit over the Rust (a `.py` file read no more, feature 449 T158).

use std::collections::HashMap;

use super::{fmt_g, render, render_inline, tunables, unstated_rust};
use crate::claims::index::current;
use crate::claims::tests::{fixture, LIB};
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
    put(&root, "l7r/diagram/tools/pack_audit/x.py", "4.5\n");
    put(&root, "l7r/diagram/other.py", "4.5\n");
    // a crate new under `rust/` is audited, a tooling crate is not (feature 449 T165)
    put(
        &root,
        "rust/mode_a/src/lib.rs",
        "/// Research: help - CONVENTION: 3 households\npub fn sheet() -> f64 {\n    77.5\n}\n\n/// Research: plain - UNRESEARCHED\npub fn plain() {}\n",
    );
    put(
        &root,
        "rust/gate/src/odd.rs",
        "pub fn odd() -> f64 {\n    66.5\n}\n",
    );
    let cur = current(&root, &root.join("research/questions")).unwrap();
    let found = tunables(&cur, "", true);
    assert_eq!(
        found.iter().map(|f| f.1.as_str()).collect::<Vec<_>>(),
        vec![
            "rust/phases/src/lib.rs::Thing.m#method guess",
            "rust/mode_a/src/lib.rs::sheet#help"
        ]
    );
    assert_eq!(tunables(&cur, "", false).len(), 4);
    assert!(tunables(&cur, "nothing/", true).is_empty());
    assert_eq!(render(&[], false), "tunables: none - values no source states: a goal and a knob, never a target to defend (docs/approach-checklist.md A3)");
    let text = render(&found, false);
    assert!(text.starts_with("tunables: GUESS 1, CONVENTION 1 - ") && text.contains("\n  GUESS        rust/phases/src/lib.rs::Thing.m#method guess - wider than the page, 40 ft"), "{text}");
    assert_eq!(render(&found, true).lines().count(), 1);
    let inline = super::inline(&root, &cur, "").unwrap();
    let shown = render_inline(&inline, false);
    assert!(
        shown.contains("  rust/phases/src/lib.rs:14 reach 3.25")
            && shown.contains("  rust/phases/src/lib.rs:23 m 42")
            && shown.contains("  rust/mode_a/src/lib.rs:3 sheet 77.5")
            && !shown.contains("66.5")
            && !shown.contains("8888")
            && !shown.contains(".py"),
    );
    let counted = render_inline(&inline, true);
    assert!(counted.contains("  rust/mode_a/src/lib.rs"), "{counted}");
    assert!(super::inline(&root, &cur, "rust/")
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

#[test]
fn a_whole_number_of_six_digits_is_written_whole() {
    assert_eq!(fmt_g(123_456.0), "123456");
}
