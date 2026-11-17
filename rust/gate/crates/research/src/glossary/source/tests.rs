//! The glossary's term files (feature 449 T148): `expected.json` holds HEAD's `glossary_source.py` and `glossary.py` on the same small
//! trees (the T148 scratch's `pygloss.py`).

use std::path::{Path, PathBuf};

use serde_json::{json, Value};

use super::{
    check, decode, encode, file_name, first_difference, normpath, relpath, term_files, term_of,
    write_index, write_source, write_term_files, HERE,
};
use crate::fixture::put;
use l7r_gate_core::checks::{scratch, TempDir};

const G: &str = "{\n \"b/c\": {\n  \"def\": \"x\",\n  \"variants\": [\n   \"B\",\n   \"\u{3a3}\u{3af}\u{3c3}\u{3c5}\u{3c6}\u{3bf}\u{3c2}\"\n  ]\n },\n \"a%\": {\n  \"variants\": [\n   \"a\"\n  ],\n  \"def\": 1\n }\n}\n";

fn expected() -> Value {
    serde_json::from_str(include_str!("expected.json")).unwrap()
}

fn tree(files: &[(&str, &str)]) -> (TempDir, PathBuf) {
    let d = scratch("glossary-tree");
    let base = d.join(HERE);
    for (rel, text) in files {
        put(&base, rel, text);
    }
    std::fs::create_dir_all(d.join("research/assets")).unwrap();
    (d, base)
}

fn answer<T: Into<Value>>(r: crate::Result<T>) -> Value {
    match r {
        Ok(v) => json!(["ok", v.into()]),
        Err(e) => json!([e.kind, e.message]),
    }
}

#[test]
fn the_split_and_the_assembly_are_the_pythons() {
    let e = expected();
    let (d, base) = tree(&[("assets/glossary.json", G)]);
    assert_eq!(answer(write_term_files(&base)), e["split"]);
    for (name, text) in e["files"].as_object().unwrap() {
        assert_eq!(
            &std::fs::read_to_string(base.join("assets/glossary").join(name)).unwrap(),
            text.as_str().unwrap()
        );
    }
    assert_eq!(answer(check(&base)), e["check_unindexed"]);
    assert_eq!(answer(write_index(&base)), e["write_index"]);
    assert_eq!(
        std::fs::read_to_string(d.join("research/assets/glossary-variants.txt")).unwrap(),
        e["index"].as_str().unwrap()
    );
    assert_eq!(answer(write_index(&base)), e["write_index_again"]);
    assert_eq!(answer(write_source(&base)), e["write_source"]);
    put(&base, "assets/glossary.json", "{}\n");
    assert_eq!(answer(check(&base)), e["check_stale"]);
    assert_eq!(answer(write_source(&base)), e["write_source_changed"]);
    let terms = crate::glossary::load(&d).unwrap();
    assert_eq!(
        crate::glossary::record_glossary_js(&terms),
        e["js"].as_str().unwrap()
    );
}

#[test]
fn every_refusal_is_the_pythons() {
    let e = expected();
    let a = "{\"term\": \"a\", \"variants\": []}";
    let b = "{\"term\": \"b\", \"variants\": []}";
    let cases: [(&str, Vec<(&str, &str)>); 7] = [
        ("no dir", vec![]),
        ("stray", vec![("assets/glossary/README", "x")]),
        (
            "prefix",
            vec![
                ("assets/glossary/0010-a.json", a),
                ("assets/glossary/00010-b.json", b),
            ],
        ),
        (
            "mismatch",
            vec![(
                "assets/glossary/0010-a.json",
                "{\"term\": \"z\", \"variants\": []}",
            )],
        ),
        (
            "no term",
            vec![("assets/glossary/0010-None.json", "{\"variants\": []}")],
        ),
        (
            "twice",
            vec![
                ("assets/glossary/0010-a.json", a),
                ("assets/glossary/0020-a.json", a),
            ],
        ),
        (
            "five digits",
            vec![
                (
                    "assets/glossary/10020-b.json",
                    "{\"term\": \"b\", \"variants\": [\"B\"]}",
                ),
                (
                    "assets/glossary/1290-a.json",
                    "{\"term\": \"a\", \"variants\": [\"A\"]}",
                ),
            ],
        ),
    ];
    for (name, mut files) in cases {
        files.push(("assets/glossary.json", G));
        let (_d, base) = tree(&files);
        let want = &e["errors"][name];
        assert_eq!(
            answer(term_files(&base).map(|t| t.into_iter().map(Value::Object).collect::<Vec<_>>())),
            want[0]
        );
        assert_eq!(answer(check(&base)), want[1], "{name}");
    }
    let (_d, base) = tree(&[(
        "assets/glossary.json",
        "{\"a\": {\"variants\": [\"x\"]}, \"b\": {\"variants\": [\"x\"]}}\n",
    )]);
    assert_eq!(answer(write_term_files(&base)), e["split_lossy"]);
    assert_eq!(
        json!([
            first_difference("abc", "abd"),
            first_difference("ab", "abc")
        ]),
        e["first_difference"]
    );
}

#[test]
fn the_reads_that_are_not_a_glossary_are_refused() {
    let (_d, base) = tree(&[("assets/glossary.json", "[1]")]);
    assert_eq!(write_term_files(&base).unwrap_err().kind, "AttributeError");
    let (_d, base) = tree(&[("assets/glossary.json", "{\"a\": 1}")]);
    assert_eq!(write_term_files(&base).unwrap_err().kind, "TypeError");
    let (_d, base) = tree(&[("assets/glossary.json", "{bad")]);
    assert_eq!(write_term_files(&base).unwrap_err().kind, "JSONDecodeError");
    let (_d, base) = tree(&[]);
    assert_eq!(write_term_files(&base).unwrap_err().kind, "OSError");
    for (file, kind) in [("{bad", "JSONDecodeError"), ("[1]", "AttributeError")] {
        let (_d, base) = tree(&[("assets/glossary/0010-a.json", file)]);
        assert_eq!(term_files(&base).unwrap_err().kind, kind);
    }
    let (_d, base) = tree(&[
        ("assets/glossary/0010-a.json", "{\"term\": \"a\"}"),
        ("assets/glossary.json", G),
    ]);
    assert_eq!(check(&base).unwrap_err().message, "'variants'");
    let (_d, base) = tree(&[
        (
            "assets/glossary/0010-a.json",
            "{\"term\": \"a\", \"variants\": [1]}",
        ),
        ("assets/glossary.json", G),
    ]);
    assert_eq!(check(&base).unwrap_err().kind, "AttributeError");
    let (d, base) = tree(&[
        (
            "assets/glossary/0010-a.json",
            "{\"term\": \"a\", \"variants\": []}",
        ),
        ("assets/glossary.json", G),
    ]);
    std::fs::create_dir_all(d.join("research/assets/glossary-variants.txt")).unwrap();
    assert_eq!(write_index(&base).unwrap_err().kind, "OSError");
    // a split into a directory it cannot write
    let (_d, base) = tree(&[("assets/glossary.json", G), ("assets/glossary", "a file")]);
    assert_eq!(write_term_files(&base).unwrap_err().kind, "OSError");
    let (_d, base) = tree(&[
        ("assets/glossary.json", "{\"a/b\": {}}"),
        ("assets/glossary/0010-a", ""),
    ]);
    std::fs::remove_file(base.join("assets/glossary/0010-a")).unwrap();
    std::fs::create_dir_all(base.join("assets/glossary/0010-a%2Fb.json")).unwrap();
    assert_eq!(write_term_files(&base).unwrap_err().kind, "OSError");
}

#[test]
fn names_and_paths() {
    assert_eq!(file_name(579, "towpath"), "5790-towpath.json");
    assert_eq!(file_name(2, "dS/m%"), "0020-dS%2Fm%25.json");
    assert_eq!(decode(&encode("a/b%2F")), "a/b%2F");
    assert_eq!(term_of("0010-a%2Fb.json").unwrap(), "a/b");
    assert_eq!(
        term_of("\u{661}\u{660}\u{661}\u{660}-x.json\n").unwrap(),
        "x"
    );
    assert_eq!(
        normpath(Path::new("/a/./b/../c/../../..")),
        PathBuf::from("/")
    );
    assert_eq!(normpath(Path::new("../a")), PathBuf::from("../a"));
    assert_eq!(normpath(Path::new("./a")), PathBuf::from("a"));
    assert_eq!(relpath(Path::new("a"), Path::new("a")), ".");
    let (_d, base) = tree(&[
        (
            "assets/glossary/0010-a.json",
            "{\"term\": \"a\", \"variants\": []}",
        ),
        (
            "assets/glossary/0010-b.json",
            "{\"term\": \"b\", \"variants\": []}",
        ),
    ]);
    assert_eq!(term_files(&base).unwrap_err().message, "assets/glossary/: 0010-a.json and 0010-b.json both claim prefix 0010 - the assembly will not choose between them");
    // a term directory it cannot list
    let dir = base.join("assets/glossary");
    let mode = |m: u32| {
        std::fs::set_permissions(&dir, std::os::unix::fs::PermissionsExt::from_mode(m)).unwrap();
    };
    mode(0o000);
    let refused = term_files(&base).unwrap_err().kind;
    mode(0o755);
    assert_eq!(refused, "OSError");
}
