//! The units: a procedure document's sections, a Rust file's items, the JSON the runner hands over, the walk of `rust/` (each value
//! the Python reader's own on the same text, read 2026-11-11).

use std::path::Path;

use serde_json::json;

use super::{
    all_rust_units, doc_units, from_json, items, rglob, rust_units, section_blocks, splitlines,
    splitlines_keep, to_json,
};
use crate::claims::tests::{fixture, BUILDINGS, LIB};
use crate::record::testkit::put;

#[test]
fn a_procedure_document_is_read_by_its_headings() {
    let units = doc_units(BUILDINGS, "docs/buildings.md", None);
    let got: Vec<(&str, usize, usize, usize, &str)> = units
        .iter()
        .map(|u| {
            (
                u.qualname.as_str(),
                u.lineno,
                u.end_lineno,
                u.claims.len(),
                u.core.as_str(),
            )
        })
        .collect();
    assert_eq!(
        got,
        vec![
            ("Walls", 3, 13, 2, "5a446aed967da80f"),
            ("Deep", 14, 17, 0, "ade2e04867162908")
        ]
    );
    assert_eq!(
        units[0].blocks,
        vec!["Walls stand.", "- a list item continued", "| a | table |"]
    );
    assert!(units[0].line_keyed() && units[0].uid() == "docs/buildings.md::Walls");
    let tops: &[&str] = &["Deep"];
    let only = doc_units(
        "## A\n\n### Deep\n<!-- Research: bad -->\n#### Under\n\n## B\n",
        "d.md",
        Some(tops),
    );
    assert_eq!(
        only.iter().map(|u| u.qualname.as_str()).collect::<Vec<_>>(),
        vec!["Deep", "Under"]
    );
    assert!(only[0].errors[0].contains("has no `<label> - <backing>`"));
    assert_eq!(
        section_blocks("para one\nline two\n\n- item\n  cont\n| a | b |\n|---|---|\n# head\nafter head\n<!-- x -->\n1) n\n"),
        vec!["para one line two", "- item cont", "| a | b |", "# head", "after head", "1) n"]
    );
}

#[test]
fn a_rust_file_is_read_by_its_items() {
    let found: Vec<(String, String, usize, usize)> = items(LIB, 0, "", false)
        .into_iter()
        .map(|(q, k, f, l, _, _)| (q, k, f, l))
        .collect();
    let want = [
        ("GAP", "constant", 10, 10),
        ("reach", "function", 13, 16),
        ("Thing.m", "method", 20, 24),
        ("helper", "function", 27, 29),
    ];
    assert_eq!(
        found,
        want.map(|(q, k, f, l)| (q.to_owned(), k.to_owned(), f, l))
            .to_vec()
    );
    let (errors, units) = rust_units(LIB, "rust/phases/src/lib.rs");
    assert!(errors.is_empty());
    let cores: Vec<(&str, &str, bool)> = units
        .iter()
        .map(|u| (u.qualname.as_str(), u.core.as_str(), u.inherited))
        .collect();
    assert_eq!(
        cores,
        vec![
            ("GAP", "2397112476f581b8", false),
            ("reach", "004681655ed00657", false),
            ("Thing.m", "08b04300c56f01ee", false),
            ("helper", "88d9634f1ba5eae9", true)
        ]
    );
    assert_eq!(units[3].claims[0].line, "plumbing - NONE");
    let odd = "impl<T> Foo<T> {\n    fn a() {}\n}\nimpl Bar for Baz {\n    const C: [u8; 2] = [1, 2];\n}\nstruct S;\nfn f() -> ([Pt; 4], f64) { let c = '{'; let s = \"}\\\"}\"; /* } */ // }\n 1 }\nfn g(x: &'a str) {}\nmod m {\n fn hidden() {}\n}\n#[expect(\n    x,\n    reason = \"y\"\n)]\nfn after() {}\nimpl Nothing\nfn unclosed() {";
    let names: Vec<(String, usize, usize)> = items(odd, 0, "", false)
        .into_iter()
        .map(|(q, _, f, l, _, _)| (q, f, l))
        .collect();
    let want = [
        ("Foo.a", 2, 2),
        ("Baz.C", 5, 5),
        ("S", 7, 7),
        ("f", 8, 9),
        ("g", 10, 10),
        ("after", 18, 18),
    ];
    assert_eq!(names, want.map(|(q, f, l)| (q.to_owned(), f, l)).to_vec());
    let (errors, units) = rust_units("//! Research:\n//!     bad\n/// Research: x - NONE\nfn a() {}\n/// Research: broken\nfn b() {}\n", "x.rs");
    assert_eq!(errors.len(), 1);
    assert!(units[1].claims.is_empty() && !units[1].inherited && units[1].errors.len() == 1);
}

#[test]
fn lines_split_as_python_splits_them() {
    assert_eq!(
        splitlines_keep("a\r\nb\rc\x0bd\ne"),
        vec!["a\r\n", "b\r", "c\x0b", "d\n", "e"]
    );
    assert_eq!(splitlines("a\r\nb\rc\u{2028}d\n"), vec!["a", "b", "c", "d"]);
    assert_eq!(splitlines("no end"), vec!["no end"]);
}

#[test]
fn a_unit_crosses_the_runner_as_json() {
    let v = json!({"path": "l7r/a.py", "qualname": "T", "kind": "constant", "lineno": 3, "end_lineno": 5, "claims": ["t - NONE", "broken"],
                   "inherited": true, "core": "c", "errors": ["e"], "names": ["N=1"], "blocks": ["b"], "module_errors": ["m"]});
    let (u, errors) = from_json(&v);
    assert_eq!(
        (u.claims.len(), u.lineno, errors),
        (1, 3, vec!["m".to_owned()])
    );
    assert!(u.line_keyed());
    let back = to_json(&u);
    assert_eq!(back["claims"], json!(["t - NONE"]));
    assert_eq!(from_json(&json!({})).0.qualname, "");
}

#[test]
fn the_rust_walk_skips_the_tooling_crates_and_targets_and_keeps_python_order() {
    let root = fixture("claims-units-walk");
    put(&root, "rust/phases/src/a-x/c.rs", "pub fn c() {}\n");
    put(&root, "rust/phases/src/a/b.rs", "pub fn b() {}\n");
    put(&root, "rust/browser/src/lib.rs", "pub fn launch() {}\n");
    // the embedder program holds no research claim either (feature 449 T138)
    put(&root, "rust/embed/src/lib.rs", "pub fn cli() {}\n");
    put(&root, "rust/gate/src/lib.rs", "pub fn cli() {}\n");
    let paths: Vec<String> = rglob(&root.join("rust"), ".rs")
        .iter()
        .map(|p| super::rel(p, &root))
        .collect();
    assert!(
        paths.iter().position(|p| p.ends_with("a/b.rs"))
            < paths.iter().position(|p| p.ends_with("a-x/c.rs"))
    );
    let units = all_rust_units(&root, "", true).unwrap();
    assert!(units
        .iter()
        .all(|(u, _)| u.path.starts_with("rust/phases/src/") && !u.path.contains("target")));
    std::fs::write(root.join("rust/phases/src/bad.rs"), [0xff_u8]).unwrap();
    assert!(all_rust_units(&root, "", true).is_err());
    assert!(rglob(Path::new("/no/such/dir"), ".rs").is_empty());
}

/// The engine's slices (S7-S12) port into new crates: one NEW under `rust/` is walked with nothing declared - its claims read, its
/// target and a parked copy pruned - so the claims track it from its first commit (feature 449 T165).
#[test]
fn a_new_crate_under_rust_is_walked_with_nothing_declared() {
    let root = crate::checks::scratch("claims-units-new-crate");
    let claimed = "/// Research: the reach - NONE: plumbing\npub fn sheet() {}\n";
    put(&root, "rust/mode_a/src/lib.rs", claimed);
    put(&root, "rust/mode_a/src/sheet/walls.rs", claimed);
    put(&root, "rust/mode_a/target/debug/build/x.rs", claimed);
    put(&root, "rust/parked/mode_a/src/lib.rs", claimed);
    let units = all_rust_units(&root, "", true).unwrap();
    let keys: Vec<String> = units.iter().map(|(u, _)| u.key(&u.claims[0])).collect();
    assert_eq!(
        keys,
        vec![
            "rust/mode_a/src/lib.rs::sheet#the reach",
            "rust/mode_a/src/sheet/walls.rs::sheet#the reach"
        ]
    );
    for (inner, walked) in [
        ("mode_a/src/lib.rs", true),
        ("phases/src/lib.rs", true),
        ("gate/crates/claims/src/claims.rs", false),
        ("guard/src/lib.rs", false),
        ("browser/src/lib.rs", false),
        ("embed/src/lib.rs", false),
        ("parked/x.rs", false),
        ("mode_a/target/x.rs", false),
    ] {
        assert_eq!(super::walked(inner), walked, "{inner}");
    }
}

#[test]
fn a_statement_between_a_doc_and_its_item_ends_the_doc() {
    let got = items("/// a doc\nuse x;\nfn a() {}\n", 0, "", false);
    assert_eq!(got[0].4, "");
}
