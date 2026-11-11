//! Question bundles, notes and the parts a bundle cuts, on the testkit's record through the stub runner.

use std::collections::HashSet;
use std::path::Path;

use serde_json::json;

use super::*;
use crate::record::bundle::tests::{args, scratch, state};
use crate::record::testkit::{edit_everything, put};

fn keys(list: &[&str]) -> HashSet<String> {
    list.iter().map(|s| (*s).to_owned()).collect()
}

fn bundle(root: &Path, extra: &[&str]) -> Reply {
    let r = root.to_string_lossy().into_owned();
    let mut a = vec!["--root", r.as_str()];
    a.extend(extra);
    cli(&args(&a))
}

#[test]
fn the_pure_parts_of_a_bundle() {
    assert_eq!(cited_keys("<a href=\"x\"> <code>k-1</code> </a><a href=\"y\"><code>k-1</code></a><a href=\"z\"><code>k2</code></a>"), vec!["k-1", "k2"]);
    assert_eq!(
        url_of("<p>(https://e.org/Edo_(x)), 5 August;</p>"),
        "https://e.org/Edo_(x)"
    );
    assert_eq!(
        url_of("see https://e.org/a?b=1&amp;c=2."),
        "https://e.org/a?b=1&c=2"
    );
    assert_eq!(url_of("none"), "");
    let html = "<h2 id=\"t\">T</h2>\n<p>one<sup data-note=\"a\"></sup></p>\n<ul><li>lead<ul><li>inner<sup data-note=\"b\"></sup></li></ul> tail<sup data-note=\"c\"></sup></li></ul>\n<li>open<ul>\n<p>bare\n<p>bare";
    let cut = excerpt(html, &keys(&["c"]), false);
    assert!(cut.starts_with("<h2 id=\"t\">T</h2>\n<!-- an EXCERPT: only the blocks carrying the named notes -->\n<li>lead"), "{cut}");
    assert!(!excerpt(html, &keys(&["b"]), false).contains("<li>lead"));
    let bare = excerpt(html, &keys(&["a"]), true);
    assert!(
        bare.contains("and every block carrying none") && bare.contains("<p>bare\n"),
        "{bare}"
    );
    assert!(excerpt("<p>x</p>", &keys(&["a"]), false).starts_with("<!-- an EXCERPT"));
    let notes = "<li data-note=\"a\">A</li>\n<li data-note=\"b\">B</li>\n";
    assert_eq!(
        notes_subset(notes, &keys(&["b"])),
        "<li data-note=\"b\">B</li>\n"
    );
    assert_eq!(parts("bogus"), parts("all"));
    assert_eq!(flat(" a \n b "), "a b");
    assert_eq!(untagged("<b>x</b>"), "x");
    assert_eq!(
        report_lines("head\n  fn-1 k - OK\ntail"),
        vec!["head", "tail"]
    );
    assert_eq!(dumps(&json!({"a": [1]})), "{\n \"a\": [\n  1\n ]\n}\n");
    assert_eq!(
        out_or("", "x".to_owned()),
        Path::new(DEFAULT_ROOT).join("x")
    );
    assert_eq!(out_or("./o/", "x".to_owned()), Path::new("o"));
}

#[test]
fn a_registry_entry_and_a_fresh_directory() {
    let root = scratch("bundle-check-files");
    put(
        &root,
        "research/sources/040-uncited-works/0002-fires-in-key-a.html",
        "x",
    );
    assert_eq!(
        registry_entry(&root, "key-a"),
        Some(root.join("research/sources/010-works-cited/0001-key-a.html"))
    );
    assert_eq!(registry_entry(&root, "none"), None);
    let out = root.join("o");
    fresh(&out).unwrap();
    put(&root, "o/MANIFEST.md", "m");
    fresh(&out).unwrap();
    assert!(!out.join("MANIFEST.md").exists());
    put(&root, "o/x", "x");
    assert!(fresh(&out)
        .unwrap_err()
        .contains("exists and is not a bundle"));
    assert!(fresh(&root.join("research/STYLE.md")).is_err());
    assert!(inline(
        &root,
        &[("research".to_owned(), String::new(), String::new())]
    )
    .unwrap()
    .is_empty());
    std::fs::write(root.join("bad.txt"), [0xff]).unwrap();
    assert!(inline(
        &root,
        &[("bad.txt".to_owned(), String::new(), String::new())]
    )
    .is_err());
    assert!(manifest(
        &root,
        "t",
        &[("bad.txt".to_owned(), String::new(), String::new())]
    )
    .is_err());
}

#[test]
fn a_question_bundle_end_to_end() {
    let root = scratch("bundle-check-q");
    edit_everything(&root);
    let out = root.join("out");
    let o = out.to_string_lossy().into_owned();
    let all = bundle(&root, &["0094", "--out", &format!("{o}/a"), "--no-quotes"]);
    assert_eq!(all.code, 0, "{}", all.stderr);
    let text = std::fs::read_to_string(out.join("a/MANIFEST.md")).unwrap();
    assert!(
        text.contains("| `prepass.txt` | `make record-prepass Q=0094` |"),
        "{text}"
    );
    assert!(
        text.contains("## The change (feature 375, FR-006)")
            && text.contains("changed-note: research/questions/0094-trade.notes.html | "),
        "{text}"
    );
    assert!(
        text.contains("| `sources/key-a.html` |")
            && text.contains("changed-block: research/questions/0094-trade.html | "),
        "{text}"
    );
    put(&root, "qv.json", &json!({"footnotes": [{"id": "fn-1", "key": "key-a", "readability": "OK", "links": ["https://e.org/b", "ftp://x", "https://e.org/b"], "passages": [{"quote": "a passage", "quotation": "NOT FOUND"}], "assertion": ""}, {"id": "fn-2", "class": "absence", "links": ["https://e.org/c"], "passages": [{"quote": "", "original": "x", "quotation": "VERBATIM"}], "assertion": "A short distance apart."}]}).to_string());
    let q = bundle(
        &root,
        &["0094", "--for", "quote-check", "--out", &format!("{o}/b")],
    );
    assert_eq!(q.code, 0, "{}", q.stderr);
    let text = std::fs::read_to_string(out.join("b/MANIFEST.md")).unwrap();
    assert!(
        text.contains("| `pages/` | `the host's page cache (feature 288)` |")
            && out.join("b/pages/MANIFEST.txt").is_file(),
        "{text}"
    );
    let scoped = bundle(
        &root,
        &[
            "0094",
            "--for",
            "quote-check",
            "--notes",
            "k,",
            "--out",
            &format!("{o}/c"),
        ],
    );
    assert_eq!(scoped.code, 0, "{}", scoped.stderr);
    let report = std::fs::read_to_string(out.join("c/quote-verbatim.txt")).unwrap();
    assert!(
        report.contains("(scoped to the 2 footnote(s)") && report.contains("  fn-2 absence - None"),
        "{report}"
    );
    for (for_, file) in [
        ("record-style", "style-prepass.txt"),
        ("translation-check", "translations.txt"),
        ("record-format", "glossary-variants.txt"),
    ] {
        let r = bundle(
            &root,
            &[
                "0094",
                "--for",
                for_,
                "--not-owed-ok",
                "an audit asked",
                "--out",
                &format!("{o}/{for_}"),
                "--extra",
                "research/STYLE.md",
                &format!("{}/research/STYLE.md", root.display()),
            ],
        );
        assert_eq!(r.code, 0, "{for_}: {}", r.stderr);
        assert!(out.join(for_).join(file).is_file(), "{for_}");
    }
    let drift = bundle(
        &root,
        &[
            "0094",
            "--for",
            "entry-drift",
            "--kind",
            "homestead.Well",
            "--not-owed-ok",
            "an audit asked",
            "--out",
            &format!("{o}/k"),
        ],
    );
    assert_eq!(drift.code, 0, "{}", drift.stderr);
    assert!(std::fs::read_to_string(out.join("k/kind.txt"))
        .unwrap()
        .starts_with("class homestead.Well  ("));
    let images = root.join("imgs");
    put(&root, "imgs/p1.png", "one");
    let im = bundle(
        &root,
        &[
            "0094",
            "--no-quotes",
            "--out",
            &format!("{o}/im"),
            "--images",
            &images.to_string_lossy(),
            "/no/such.png",
        ],
    );
    assert!(
        std::fs::read_to_string(out.join("im/MANIFEST.md"))
            .unwrap()
            .contains("- `images/p1.png`"),
        "{}",
        im.stderr
    );
}

#[test]
fn the_refusals_of_a_question_bundle() {
    let root = scratch("bundle-check-refused");
    let o = root.join("out").to_string_lossy().into_owned();
    assert!(bundle(&root, &["0094", "--out", &o])
        .stderr
        .starts_with("check-bundle: REFUSED - no record check is owed"));
    assert_eq!(bundle(&root, &["0777"]).code, 2);
    assert_eq!(bundle(&root, &[]).code, 2);
    assert_eq!(bundle(&root, &["--for", "bogus", "0094"]).code, 2);
    assert_eq!(bundle(&root, &["--bogus"]).code, 2);
    assert_eq!(
        bundle(
            &root,
            &[
                "0094",
                "--for",
                "entry-drift",
                "--kind",
                "Well",
                "--out",
                &o
            ]
        )
        .code,
        3
    );
    let none = bundle(
        &root,
        &[
            "0094",
            "--for",
            "entry-drift",
            "--kind",
            "Nope",
            "--not-owed-ok",
            "an audit asked",
            "--out",
            &o,
        ],
    );
    assert!(none.stderr.contains("no modal class 'Nope'") && none.code == 2);
    put(&root, "out/x", "x");
    let busy = bundle(
        &root,
        &[
            "0094",
            "--not-owed-ok",
            "an audit asked",
            "--no-quotes",
            "--out",
            &o,
        ],
    );
    assert_eq!(busy.code, 1);
    assert!(busy.stderr.contains("exists and is not a bundle"));
    let printed = bundle(&root, &["0094", "--notes", "k", "--print-notes"]);
    assert!(
        printed
            .stdout
            .contains("== research/questions/0094-trade.notes.html\n<li data-note=\"k\">"),
        "{}",
        printed.stdout
    );
    assert_eq!(bundle(&root, &["0094", "--print-notes"]).code, 2);
    assert_eq!(
        bundle(&root, &["0777", "--notes", "k", "--print-notes"]).code,
        2
    );
    put(&root, "scripts/bundle_door.py", "import json, sys\nfor l in sys.stdin:\n    print(json.dumps({'ok': [5, 'helper said no']}), flush=True)\n");
    for for_ in ["record-format", "record-style", "quote-check"] {
        let r = bundle(
            &root,
            &[
                "0094",
                "--for",
                for_,
                "--not-owed-ok",
                "an audit asked",
                "--out",
                &format!("{o}2/{for_}"),
            ],
        );
        assert_eq!(r.code, 5, "{for_}");
        assert!(r.stderr.contains("helper said no"));
    }
    put(&root, "scripts/bundle_door.py", "import json, sys\nfor l in sys.stdin:\n    print(json.dumps({'error': 'Traceback (most recent call last):\\nOSError: no'}), flush=True)\n");
    assert_eq!(
        bundle(
            &root,
            &[
                "0094",
                "--for",
                "record-format",
                "--not-owed-ok",
                "an audit asked",
                "--out",
                &format!("{o}3")
            ]
        )
        .code,
        1
    );
    put(
        &root,
        "research/questions/0094-trade.notes.html",
        "<li data-note=\"q\">\"x\"</li>",
    );
    put(
        &root,
        "scripts/record/quote_verbatim.py",
        "raise ImportError('x')\n",
    );
    assert_eq!(
        bundle(
            &root,
            &[
                "0094",
                "--for",
                "translation-check",
                "--not-owed-ok",
                "an audit asked",
                "--out",
                &format!("{o}4")
            ]
        )
        .code,
        1
    );
}

#[test]
fn a_large_question_is_batched() {
    let root = scratch("bundle-check-batches");
    let note = |k: usize| format!("<li data-note=\"n{k}\">\"{}\"</li>\n", "w".repeat(5000));
    let notes: String = (0..5).map(note).collect();
    put(
        &root,
        "research/questions/0094-trade.notes.html",
        &format!("<ol>\n{notes}</ol>\n"),
    );
    put(
        &root,
        "research/questions/0094-trade.html",
        "<h2 id=\"t\">Trade</h2>\n<p>A claim.<sup data-note=\"n4\"></sup></p>\n<p>bare</p>\n",
    );
    let base = crate::record::testkit::commit(&root, "big notes");
    crate::record::testkit::git(&root, &["update-ref", "refs/remotes/origin/main", &base]);
    put(&root, "research/questions/0094-trade.html", "<h2 id=\"t\">Trade</h2>\n<p>A claim.<sup data-note=\"n4\"></sup></p>\n<p>bare, changed</p>\n");
    let o = root.join("out").to_string_lossy().into_owned();
    put(&root, "out/MANIFEST.md", "stale");
    let r = bundle(&root, &["0094", "--for", "quote-check", "--out", &o]);
    assert_eq!(r.code, 0, "{}", r.stderr);
    assert!(
        r.stdout
            .contains("over 12,000 bytes - 3 quote-check bundles")
            && r.stdout.contains("batch-1/MANIFEST.md")
            && !r.stdout.contains("batch-3/MANIFEST.md"),
        "{}",
        r.stdout
    );
    assert!(!root.join("out/MANIFEST.md").exists());
    std::fs::write(
        root.join("research/questions/0094-trade.notes.html"),
        [0xff],
    )
    .unwrap();
    assert!(note_batches(&root, "0094").is_err());
    assert!(changed_section(
        &root,
        &["research/questions/0094-trade.notes.html".to_owned()]
    )
    .is_err());
    assert!(print_notes(&mut Run::new(&root), &root, "0094", &keys(&["x"])).is_err());
}

#[test]
fn earlier_rounds_ride_a_bundle() {
    let root = scratch("bundle-check-earlier");
    edit_everything(&root);
    let reply = root.join("reply.md");
    put(
        &root,
        "reply.md",
        "1. a finding of some length, unrecorded here\n",
    );
    state(
        &root,
        &json!({"dispatches": {"a": {"check": "record-format", "subjects": ["q:0094"], "t": 1, "state": "returned", "reply": reply.to_string_lossy()}}}),
    );
    let o = root.join("out").to_string_lossy().into_owned();
    let r = bundle(&root, &["0094", "--for", "record-format", "--out", &o]);
    assert_eq!(r.code, 0, "{}", r.stderr);
    assert!(std::fs::read_to_string(root.join("out/MANIFEST.md"))
        .unwrap()
        .contains("## Earlier rounds (feature 393)"));
}
