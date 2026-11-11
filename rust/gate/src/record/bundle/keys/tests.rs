//! Source bundles, the intro-check batch and the parts a question bundle borrows.

use std::path::Path;

use serde_json::json;

use super::*;
use crate::record::bundle::tests::{args, scratch, state};
use crate::record::testkit::{edit_everything, put};
use crate::Reply;

fn bundle(root: &Path, extra: &[&str]) -> Reply {
    let r = root.to_string_lossy().into_owned();
    let mut a = vec!["--root", r.as_str()];
    a.extend(extra);
    crate::record::bundle::check::cli(&args(&a))
}

#[test]
fn a_source_bundle_end_to_end() {
    let root = scratch("bundle-key");
    put(
        &root,
        "research/sources/010-works-cited/0001-key-a.html",
        "<p>Write-up A (https://e.org/a).</p>\n",
    );
    put(&root, "research/questions/citations/0001-key.notes.html", "<li data-note=\"key-a-2\">\"q\" <!-- \"a session note\" --></li><li data-note=\"key-ab\">x</li>");
    let base = crate::record::testkit::commit(&root, "a pointer");
    crate::record::testkit::git(&root, &["update-ref", "refs/remotes/origin/main", &base]);
    let o = root.join("out").to_string_lossy().into_owned();
    assert_eq!(bundle(&root, &["--key", "key-a", "--out", &o]).code, 3);
    assert_eq!(
        bundle(
            &root,
            &[
                "--key",
                "nope",
                "--not-owed-ok",
                "an audit asked",
                "--out",
                &o
            ]
        )
        .code,
        2
    );
    let r = bundle(
        &root,
        &[
            "--key",
            "key-a",
            "--not-owed-ok",
            "an audit asked",
            "--out",
            &o,
        ],
    );
    assert_eq!(r.code, 0, "{}", r.stderr);
    let quoted: serde_json::Value =
        serde_json::from_str(&std::fs::read_to_string(root.join("out/quotes.json")).unwrap())
            .unwrap();
    assert_eq!(
        quoted,
        json!([
            "a quoted passage of twenty letters",
            "an original long enough to keep"
        ])
    );
    edit_everything(&root);
    put(
        &root,
        "research/sources/010-works-cited/0002-key-b.html",
        "<p>B (https://e.org/b)</p>\n",
    );
    let reply = root.join("r.md");
    put(&root, "r.md", "clean\n");
    state(
        &root,
        &json!({"dispatches": {"a": {"check": "source-reader", "subjects": ["q:0094"], "t": 1.5, "state": "returned", "notes": ["n"], "reply": reply.to_string_lossy()}, "b": {"check": "source-reader", "subjects": ["q:0094"], "t": 2, "state": "running"}}}),
    );
    let whole = bundle(
        &root,
        &[
            "--key",
            "key-b",
            "--whole",
            "--question",
            "0094",
            "--out",
            &format!("{o}/w"),
            "--images",
            &format!("{}/r.md", root.display()),
        ],
    );
    assert_eq!(whole.code, 0, "{}", whole.stderr);
    assert!(
        whole
            .stdout
            .starts_with("sources-consulted: earlier reads\n"),
        "{}",
        whole.stdout
    );
    let text = std::fs::read_to_string(root.join("out/w/MANIFEST.md")).unwrap();
    assert!(
        text.contains("## The claims to read")
            && text.contains("```diff\n--- at the last round\n+++ now\n")
            && text.contains("- `images/r.md`"),
        "{text}"
    );
    put(&root, "scripts/bundle_door.py", "import json, sys\nfor l in sys.stdin:\n    print(json.dumps({'ok': [2, 'pointer | file | state\\nno']}), flush=True)\n");
    let failed = bundle(
        &root,
        &[
            "--key",
            "key-b",
            "--whole",
            "--new",
            "a claim read",
            "--out",
            &format!("{o}/f"),
        ],
    );
    assert!(
        failed.stderr.contains("pointer | file | state"),
        "{}",
        failed.stderr
    );
    put(
        &root,
        "research/sources/010-works-cited/0003-key-n.html",
        "<p>no pointer</p>\n",
    );
    assert_eq!(
        bundle(
            &root,
            &[
                "--key",
                "key-n",
                "--not-owed-ok",
                "an audit asked",
                "--out",
                &format!("{o}/n")
            ]
        )
        .code,
        0
    );
}

#[test]
fn several_keys_and_the_intro_batch() {
    let root = scratch("bundle-keys");
    put(
        &root,
        "research/sources/040-uncited-works/20501-key-c.html",
        "<p>C (https://e.org/c)</p>\n",
    );
    let o = root.join("out").to_string_lossy().into_owned();
    assert_eq!(
        bundle(&root, &["--keys", "key-a key-c", "--out", &o]).code,
        3
    );
    assert_eq!(
        bundle(&root, &["--keys", "nope key-a", "--out", &o]).code,
        2
    );
    let r = bundle(
        &root,
        &[
            "--keys",
            "key-a key-c",
            "--not-owed-ok",
            "a batch asked",
            "--out",
            &o,
        ],
    );
    assert_eq!(r.code, 0, "{}", r.stderr);
    assert!(root.join("out/pages/key-c.quotes.json").is_file());
    assert!(bundle(&root, &["--keys", " "])
        .stderr
        .contains("IndexError"));
    let intro = bundle(
        &root,
        &[
            "--for",
            "intro-check",
            "--qs",
            "0094 0095",
            "--not-owed-ok",
            "a backfill asked",
            "--out",
            &format!("{o}/i"),
        ],
    );
    assert_eq!(intro.code, 0, "{}", intro.stderr);
    assert!(root.join("out/i/q-0095.txt").is_file());
    assert_eq!(
        bundle(&root, &["0094", "--for", "intro-check", "--out", &o]).code,
        3
    );
    assert_eq!(
        bundle(
            &root,
            &[
                "--for",
                "intro-check",
                "--qs",
                "0777",
                "--not-owed-ok",
                "a backfill asked"
            ]
        )
        .code,
        2
    );
    assert!(bundle(&root, &["--for", "intro-check"])
        .stderr
        .contains("IndexError"));
    edit_everything(&root);
    let one = bundle(
        &root,
        &["0094", "--for", "intro-check", "--out", &format!("{o}/one")],
    );
    assert_eq!(one.code, 0, "{}", one.stderr);
}

#[test]
fn the_borrowed_parts_and_their_failures() {
    let root = scratch("bundle-keys-parts");
    let out = root.join("o");
    std::fs::create_dir_all(&out).unwrap();
    let mut run = crate::record::bundle::Run::new(&root);
    assert_eq!(residue_pages(&mut run, &out).unwrap(), 0);
    put(&root, "o/quote-verbatim.json", &json!({"footnotes": [{"links": ["https://a"], "passages": [{"quotation": "VERBATIM"}]}, {"links": ["https://b"]}]}).to_string());
    assert_eq!(residue_pages(&mut run, &out).unwrap(), 0);
    put(&root, "o/quote-verbatim.json", "not json");
    assert!(residue_pages(&mut run, &out).is_err());
    assert!(scoped_verbatim(&out, "").is_err());
    put(&root, "o/quote-verbatim.json", "{}");
    assert!(scoped_verbatim(&out, "").unwrap_err().contains("KeyError"));
    put(&root, "o/quote-verbatim.json", "[]");
    assert!(scoped_verbatim(&out, "").is_err());
    put(&root, "o/quote-verbatim.json", &json!({"footnotes": [{"id": 1, "key": "", "class": "c", "passages": [{"quote": "the kept text"}, {"original": null}]}, {"id": 2, "assertion": "said here"}]}).to_string());
    put(
        &root,
        "o/page.html",
        "<p>the kept text and <b>said</b> here</p>",
    );
    let text = scoped_verbatim(&out, "head\n").unwrap();
    assert!(
        text.contains("  1 c - None\n  2 None - None\n  (scoped to the 2 footnote(s)"),
        "{text}"
    );
    std::fs::write(out.join("page.html"), [0xff]).unwrap();
    assert!(scoped_verbatim(&out, "").is_err());
    assert!(scoped_verbatim(&root.join("none"), "").is_err());
    assert!(
        images_section(&out, &[root.join("none").to_string_lossy().into_owned()])
            .unwrap()
            .is_empty()
    );
    put(&root, "imgs/a.png", "a");
    let dir = root.join("imgs").to_string_lossy().into_owned();
    std::fs::write(out.join("images"), "a file in the way").unwrap();
    assert!(images_section(&out, std::slice::from_ref(&dir)).is_err());
    assert_eq!(
        ledger_part("before\npointer | file | state\nrows"),
        "before"
    );
    assert_eq!(ledger_part("only"), "only");
    put(
        &root,
        "research/questions/citations/0001-x.notes.html",
        "<li data-note=\"key-a\">x</li>",
    );
    std::fs::write(root.join("research/questions/0099-bad.notes.html"), [0xff]).unwrap();
    assert!(quoted_passages(&mut run, &root, "key-a").is_err());
}
