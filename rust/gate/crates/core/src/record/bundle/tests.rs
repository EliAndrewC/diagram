//! The bundles' shared helpers, and the scratch record every bundle test builds on: the record of `testkit`, a stub runner, a check state.

use std::path::Path;

#[cfg(test)]
use serde_json::json;

#[cfg(test)]
use super::*;
use crate::record::testkit::{put, record};

/// The runner's stub: canned answers for every verb, a failure on asking.
pub const RUNNER: &str = r#"import json, os, sys, pathlib
for line in sys.stdin:
    ask = json.loads(line)
    v, a = ask["verb"], ask["args"]
    if v == "run":
        name, args, root = a
        if "--boom" in args:
            print(json.dumps({"error": "Traceback (most recent call last):\nValueError: boom"}), flush=True)
            continue
        code = 4 if "--fail" in args else 0
        text = f"{name} ran {' '.join(args)}\n"
        if name == "quote_verbatim" and "--json" in args:
            out = args[args.index("--json") + 1]
            data = json.loads(pathlib.Path(root, "qv.json").read_text()) if pathlib.Path(root, "qv.json").is_file() else {"footnotes": []}
            pathlib.Path(out).write_text(json.dumps(data))
            text = "quote-verbatim:\n  fn-1 key - OK\nkept line\n"
        if name == "source_pages":
            pathlib.Path(args[0]).mkdir(parents=True, exist_ok=True)
            pathlib.Path(args[0], "MANIFEST.txt").write_text("m\n")
            text = ("sources-consulted: earlier reads\n" if "--question" in args else "") + "pointer | file | state\nx | y | FETCHED\n"
        print(json.dumps({"ok": [code, text]}), flush=True)
    elif v == "passages":
        print(json.dumps({"ok": [{"quote": "a quoted passage of twenty letters", "original": ""}, {"quote": "short", "original": "an original long enough to keep"}, {"quote": "https://example.org/a/long/link", "original": ""}, {"quote": "short"}]}), flush=True)
    elif v == "save_cached":
        pathlib.Path(a[1]).mkdir(parents=True, exist_ok=True)
        pathlib.Path(a[1], "MANIFEST.txt").write_text("\n".join(a[0]) + "\n")
        print(json.dumps({"ok": None}), flush=True)
    elif v == "claims_py_units":
        def u(q, kind, claim):
            return {"path": "l7r/m.py", "qualname": q, "kind": kind, "lineno": 1, "end_lineno": 1, "claims": [claim], "inherited": False, "core": "c", "errors": [], "names": [], "blocks": [], "module_errors": []}
        print(json.dumps({"ok": [[u("Mod.ROUND_CAP", "constant", "cap - research/questions/0094-trade.html: ROUND_CAP is 12 ft"), u("other", "function", "o - GUESS: about 3 households"), u("Third", "class", "t - CONVENTION: nothing named")], []]}), flush=True)
    elif v == "knobs":
        print(json.dumps({"ok": {"winter_crop": ["none", "wheat"]}}), flush=True)
    elif v == "knob_table":
        print(json.dumps({"ok": {"winter_crop": {"default": "none", "typing_rule": "def rule():\n    pass\n"}, "empty": {}}}), flush=True)
    else:
        print(json.dumps({"error": f"Traceback (most recent call last):\nKeyError: '{v}'"}), flush=True)
"#;

/// The testkit's record with the stub runner, the style guide and the variant index.
pub fn scratch(tag: &str) -> l7r_guard::shared::tempdir::TempDir {
    let root = record(tag);
    put(&root, "scripts/bundle_door.py", RUNNER);
    put(&root, "research/STYLE.md", "# Style\n");
    put(
        &root,
        "research/assets/glossary-variants.txt",
        "wells\twell\n",
    );
    root
}

/// The check state of `root`, written as `checks-open.json` in its git dir.
///
/// # Panics
///
/// Where the fixture cannot be made, which fails the test that asked for it.
pub fn state(root: &Path, value: &serde_json::Value) {
    std::fs::write(
        root.join(".git").join("checks-open.json"),
        value.to_string(),
    )
    .unwrap();
}

#[must_use]
pub fn args(list: &[&str]) -> Vec<String> {
    list.iter().map(|s| (*s).to_owned()).collect()
}

#[test]
fn paths_are_spelled_as_pathlib_spells_them() {
    assert_eq!(py_path("./a//b/"), PathBuf::from("a/b"));
    assert_eq!(py_path("."), PathBuf::from("."));
    assert_eq!(relative(Path::new("/r/a/b"), Path::new("/r")), "a/b");
    assert_eq!(relative(Path::new("/x/a"), Path::new("/r")), "/x/a");
    let mut ps = vec![PathBuf::from("a/b/c"), PathBuf::from("a/b-c")];
    sort_paths(&mut ps);
    assert_eq!(ps[0], PathBuf::from("a/b/c"));
    assert!(resolve("no/such/dir").is_absolute());
    assert!(resolve("/").is_absolute());
    assert_eq!(resolve("/no/such"), PathBuf::from("/no/such"));
}

#[test]
fn names_slugs_and_numbers() {
    assert_eq!(slug("--Stra\u{df}e 12__X--"), "strasse-12-x");
    assert_eq!(dash_runs("A/b c", char::is_ascii_alphanumeric), "A-b-c");
    assert_eq!(thousands(12_000), "12,000");
    assert_eq!(thousands(999), "999");
    assert_eq!(thousands(1_234_567), "1,234,567");
    assert_eq!(rstrip("a \n\u{3000}"), "a");
    assert_eq!(head("\u{57a3}\u{6839}x", 2), "\u{57a3}\u{6839}");
    assert_eq!(head("ab", 5), "ab");
    assert_eq!(today().len(), 10);
}

#[test]
fn reprs_are_pythons() {
    assert_eq!(py_repr("it's"), "\"it's\"");
    assert_eq!(py_repr("a'b\"c"), "'a\\'b\"c'");
    assert_eq!(
        py_repr("\\\n\t\r\u{1}\u{a0}\u{3000}\u{e0001}x\u{57a3}"),
        "'\\\\\\n\\t\\r\\x01\\xa0\\u3000\\U000e0001x\u{57a3}'"
    );
    assert_eq!(py_str(&json!(null)), "None");
    assert_eq!(py_str(&json!(true)), "True");
    assert_eq!(py_str(&json!(false)), "False");
    assert_eq!(py_str(&json!(3)), "3");
    assert_eq!(py_str(&json!(2.5)), "2.5");
    assert_eq!(py_str(&json!("s")), "s");
    assert_eq!(py_str(&json!(["a", 1, null])), "['a', 1, None]");
    assert_eq!(py_str(&json!({"k": ["v"]})), "{'k': ['v']}");
}

#[test]
fn patterns_read_as_python_reads_them() {
    let p = pyre(r"a\sb[\s,]\S\Z");
    assert!(hit(&p, "a\u{1c}b\u{1d}x"));
    assert!(!hit(&p, "a b,  "));
    assert!(hit(&pyre(r"[]x]\d"), "]1"));
    assert!(hit(&pyre(r"[^]x]"), "y"));
    assert!(hit(&pyre(r"\\"), "\\"));
    assert_eq!(
        findall(&pyre(r"(a)|b"), "ab", 1),
        vec!["a".to_owned(), String::new()]
    );
    assert_eq!(split_on(&pyre(r",\s*"), "a, b,c"), vec!["a", "b", "c"]);
}

#[test]
fn files_are_written_and_copied_or_fail() {
    let root = crate::checks::scratch("bundle-files");
    write(&root.join("a/b.txt"), "x").unwrap();
    assert!(write(&root.join("a/b.txt/c"), "x").is_err());
    assert!(write(&root.join("a"), "x").is_err());
    assert_eq!(
        copy(&root.join("a/b.txt"), &root.join("o"), None).unwrap(),
        "b.txt"
    );
    assert_eq!(
        copy(&root.join("a/b.txt"), &root.join("o"), Some("s/k.html")).unwrap(),
        "s/k.html"
    );
    assert!(copy(&root.join("none"), &root.join("o"), None).is_err());
    assert!(copy(&root.join("a/b.txt"), &root.join("a/b.txt"), Some("x")).is_err());
    assert!(remove_tree(&root.join("never")).is_err());
    assert_eq!(usage("v", "c").code, 2);
}

#[test]
fn a_run_replies_as_the_python_exited() {
    let mut run = Run::new(Path::new("/nonexistent"));
    run.say("out");
    run.warn("err");
    let r = run.reply(Ok(3));
    assert_eq!(
        (r.stdout.as_str(), r.stderr.as_str(), r.code),
        ("out\n", "err\n", 3)
    );
    let r = Run::new(Path::new("/nonexistent")).reply(Err("boom".to_owned()));
    assert_eq!((r.stderr.as_str(), r.code), ("boom\n", 1));
    let r = Run::new(Path::new("/nonexistent")).reply(Err("boom\n".to_owned()));
    assert_eq!(r.stderr, "boom\n");
}

#[test]
fn every_unprintable_range_is_escaped() {
    for c in [
        '\u{fff9}',
        '\u{110bd}',
        '\u{110cd}',
        '\u{13430}',
        '\u{1bca0}',
        '\u{1d173}',
        '\u{e0001}',
        '\u{e0020}',
        '\u{f0000}',
        '\u{600}',
        '\u{61c}',
        '\u{6dd}',
        '\u{70f}',
        '\u{890}',
        '\u{8e2}',
        '\u{1680}',
        '\u{180e}',
        '\u{2028}',
        '\u{205f}',
        '\u{2066}',
        '\u{e000}',
        '\u{feff}',
        '\u{ad}',
    ] {
        assert!(!printable(c));
    }
    assert!(printable(' ') && printable('\u{57a3}'));
    assert!(hit(&pyre("a\\"), "a\\"));
}

#[test]
fn a_path_with_no_parent() {
    assert!(write(Path::new(""), "x").is_err());
    assert!(copy(Path::new("/no/such"), Path::new(""), Some("")).is_err());
}
