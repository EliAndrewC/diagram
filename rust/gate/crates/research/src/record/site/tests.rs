//! The record's site (feature 449 T148): `cases.json` holds, for the crate's fixture tree under each of its edits, HEAD's Python build's
//! answer - every file's sha256, or the exception's kind and `str` - written by the T148 scratch's `pyexpect.py` (its glossary read from the
//! fixture's tree), and the Rust must give the same.

use std::path::Path;

use serde_json::Value;

use super::write::{
    fingerprint, is_input, read_stamp, rebuild_if_stale, record_files, write, STAMP,
};
use super::{
    as_title, build, build_index, canon_list, item, lead_of, Build, Item, Registry, SiteFiles,
};
use crate::fixture::{put, tree};
use crate::record::questions::QUESTIONS;
use l7r_guard::shared::sha256;

fn edit(root: &Path, e: &[Value]) {
    let rel = e[0]
        .as_str()
        .unwrap()
        .replace("{QUESTIONS}", &format!("research/{QUESTIONS}"));
    let path = root.join(&rel);
    let arg = |i: usize| e[i].as_str().unwrap();
    match arg(1) {
        "delete" if path.is_dir() => std::fs::remove_dir_all(&path).unwrap(),
        "delete" => std::fs::remove_file(&path).unwrap(),
        "write" => put(root, &rel, arg(2)),
        "append" => {
            let text = std::fs::read_to_string(&path).unwrap();
            std::fs::write(&path, text + arg(2)).unwrap();
        }
        _ => {
            let text = std::fs::read_to_string(&path).unwrap();
            assert!(text.contains(arg(2)), "{rel}: {}", arg(2));
            std::fs::write(&path, text.replacen(arg(2), arg(3), 1)).unwrap();
        }
    }
}

#[test]
fn every_case_builds_as_the_python_built_it() {
    let cases: serde_json::Map<String, Value> =
        serde_json::from_str(include_str!("cases.json")).unwrap();
    assert_eq!(cases.len(), 28);
    for (name, case) in &cases {
        let t = tree();
        for e in case["edits"].as_array().unwrap() {
            edit(&t, e.as_array().unwrap());
        }
        match build(&t.join("research"), &t) {
            Ok(files) => {
                assert!(case["files"].is_object(), "{name}: {case}");
                let want = case["files"].as_object().unwrap();
                let got: Vec<(String, String)> = {
                    let mut g: Vec<(String, String)> = files
                        .files
                        .iter()
                        .map(|(p, d)| (p.clone(), sha256::hex(d)))
                        .collect();
                    g.sort();
                    g
                };
                let want: Vec<(String, String)> = want
                    .iter()
                    .map(|(p, h)| (p.clone(), h.as_str().unwrap().to_owned()))
                    .collect();
                assert_eq!(got, want, "{name}");
                assert_eq!(
                    files.pages(),
                    want.iter()
                        .filter(|(p, _)| crate::has_ext(p, "html"))
                        .count()
                );
            }
            Err(e) => {
                assert!(case["error"].is_string());
                let kind = case["error"].as_str().unwrap();
                // an `OSError`'s subclass names what the C library said, its words no caller binds (`ask:449-usage-text`)
                if kind == "FileNotFoundError" {
                    assert_eq!(e.kind, "OSError", "{name}");
                } else {
                    let want = (kind, case["str"].as_str().unwrap().to_owned());
                    assert_eq!((e.kind, crate::tools::py_str(&e)), want, "{name}");
                }
            }
        }
    }
}

#[test]
fn the_small_helpers_read_as_the_python_did() {
    assert_eq!(lead_of("<p>One two. Three.</p>"), "One two.");
    assert_eq!(lead_of("<p>No stop</p>"), "No stop");
    assert_eq!(
        lead_of("<!-- <p>hidden.</p> --><div class=\"confusables\"><p>x.</p></div>"),
        ""
    );
    assert_eq!(as_title("no heading"), "no heading");
    assert_eq!(as_title("a<h3 id=\"x\">T</h3>b"), "a<h1 id=\"x\">T</h1>b");
    let line = "<p>The GM's campaign notes, <code>l7r.md</code>, \"A\" (https://h/l7r.md#a) and \"B\" (https://h/l7r.md#b)<!-- READ --></p>";
    assert_eq!(
        canon_list(line),
        "<p>The GM's campaign notes, <code>l7r.md</code>:<!-- READ --></p>\n<ul class=\"canon-sections\">\n<li>\"A\" (https://h/l7r.md#a)</li>\n<li>\"B\" (https://h/l7r.md#b)</li>\n</ul>"
    );
    for one in [
        "<p>The GM's campaign notes, <code>l7r.md</code>, \"A\" (https://h/#a)</p>",
        "<p>The GM's campaign notes, <code>l7r.md</code>, \"A\" (https://h/#a) and \"B\" (https://h/#b) trailing</p>",
        "<p>Another line</p>",
    ] {
        assert_eq!(canon_list(one), one);
    }
    let mut files = SiteFiles::default();
    files.set("a.html", "x");
    files.set("b.js", "y");
    files.set("a.html", "z");
    assert_eq!(
        (files.get("a.html"), files.get("c"), files.pages()),
        (Some(&b"z"[..]), None, 1)
    );
}

#[test]
fn the_ids_collide_by_name() {
    let t = tree();
    let registry = Registry::new(&t.join("research")).unwrap();
    let item = |id: &str, html: &str| Item {
        id: id.into(),
        html: html.into(),
        title: id.into(),
        lead: String::new(),
    };
    let items = vec![
        (
            "a.html".to_owned(),
            item("a", "<p id=\"same\">x</p><p id=\"same\">again</p>"),
        ),
        (
            "b.html".to_owned(),
            item("b", "<p id=\"same\">y</p><p id=\"record\">r</p>"),
        ),
    ];
    let e = build_index(&items, &registry, &["works-japan".to_owned()]).unwrap_err();
    assert_eq!(e.message, "the record's ids collide:\n  the id `same` is used in questions/a.html and again in questions/b.html - the single page holds both, and an id names one place\n  the id `record` (in questions/b.html) is one the site's own pages use");
}

#[test]
fn the_site_is_written_whole_and_built_again_only_when_an_input_moved() {
    let t = tree();
    let out = t.join("research/site");
    let mut files = SiteFiles::default();
    files.set("a/b.html", "new");
    write(&files, &out).unwrap();
    put(&out, "stale.html", "old");
    write(&files, &out).unwrap();
    assert!(!out.join("stale.html").exists());
    assert_eq!(
        std::fs::read_to_string(out.join("a/b.html")).unwrap(),
        "new"
    );
    // a site whose parent cannot be made
    put(&t, "file", "x");
    assert_eq!(
        write(&files, &t.join("file/site")).unwrap_err().kind,
        "OSError"
    );
    for (rel, input) in [
        ("site/x.html", false),
        ("citations/x", false),
        (".site-1/x", false),
        ("assets/glossary.js", false),
        ("CLAUDE.md", false),
        ("old.html", false),
        ("questions/x.html", true),
        ("assets/record.css", true),
    ] {
        assert_eq!(is_input(rel), input, "{rel}");
    }
    let research = t.join("research");
    put(&research, "citations/x.html", "x");
    put(&research, "deep/site/y.html", "x");
    std::os::unix::fs::symlink(research.join("questions"), research.join("linked")).unwrap();
    let files = record_files(&research);
    assert!(
        files.contains(&"assets/record.css".to_owned())
            && !files.iter().any(|f| f.starts_with("site/")
                || f.starts_with("linked")
                || f.contains("deep/site"))
    );
    assert_eq!(read_stamp(&t.join("nowhere")), "");
    // `os.walk` passes over a directory it cannot list
    assert!(record_files(&t.join("nowhere")).is_empty());
    std::fs::remove_dir_all(&out).unwrap();
    assert!(rebuild_if_stale(&t, b"code").unwrap());
    assert_eq!(read_stamp(&out), fingerprint(&t, b"code"));
    assert!(out.join(STAMP).is_file() && out.join("all.html").is_file());
    assert!(!rebuild_if_stale(&t, b"code").unwrap());
    assert!(rebuild_if_stale(&t, b"other code").unwrap());
    std::fs::remove_file(t.join("l7r/diagram/interactive/assets/glossary.json")).unwrap();
    assert_ne!(fingerprint(&t, b"code"), read_stamp(&out));
    assert_eq!(rebuild_if_stale(&t, b"code").unwrap_err().kind, "OSError");
}

#[test]
fn an_item_or_an_entry_with_no_heading() {
    assert_eq!(item("<p>x.</p>", "id").title, "id");
    let t = tree();
    let b = Build::new(&t.join("research")).unwrap();
    let bare = Item {
        id: "src-a".into(),
        html: "<p>no heading</p>\n<!-- tags: period=modern; region=japan; kind=book -->".into(),
        title: String::new(),
        lead: String::new(),
    };
    assert_eq!(b.entry_html(&bare), "<p>no heading</p>");
    let unread = Item {
        id: "src-a".into(),
        html: "<h3 id=\"src-a\">x</h3> no paragraph".into(),
        title: String::new(),
        lead: String::new(),
    };
    assert!(b
        .entry_html(&unread)
        .starts_with("<h3 id=\"src-a\">x</h3>\n<p class=\"srctags\">"));
}

#[test]
fn a_bare_less_than_is_no_markup() {
    assert_eq!(
        crate::sources::linkify("a < b <> https://x.y <!-- open"),
        "a < b <> <a href=\"https://x.y\" target=\"_blank\" rel=\"noopener\">https://x.y</a> <!-- open"
    );
}
