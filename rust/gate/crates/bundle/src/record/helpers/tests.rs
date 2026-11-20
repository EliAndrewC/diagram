//! The four record helpers as commands (feature 449 T145; the T145 differential holds them to the Python on the real record, these
//! tests every branch on the `research` crate's test record). No test reaches the network: a page is read from an offline copy or the
//! page cache.

use std::os::unix::fs::PermissionsExt as _;
use std::path::{Path, PathBuf};

use l7r_gate_research::fixture::{put, FILES};
use l7r_gate_research::pages::{entry_dir, put as cache_put, Stored};
use l7r_guard::shared::tempdir::TempDir;

use super::{quote_verbatim, record_prepass, run, save_cached, source_pages, style_prepass, VARS};

/// A clone holding the research crate's test record under `research/`, its mirror's ledger home beside it.
fn world(tag: &str) -> (TempDir, PathBuf) {
    let d = TempDir::new(tag);
    let root = d.join("m/.clones/c");
    for (rel, text) in FILES {
        put(&root.join("research"), rel, text);
    }
    std::fs::create_dir_all(root.join(".git")).unwrap();
    (d, root)
}

fn a(list: &[&str]) -> Vec<String> {
    list.iter().map(|s| (*s).to_owned()).collect()
}

fn s(p: &Path) -> String {
    p.to_string_lossy().into_owned()
}

/// The cited page held fresh in the page cache, so a run reads it there and never fetches.
fn cached(root: &Path) {
    let home = root.join("../../.specify");
    let how = Stored {
        fetched: Some("2099-01-01T00:00:00+00:00"),
        exact: true,
        origin: "fetch",
    };
    cache_put(
        &home,
        "https://e.org/a",
        "Paddies one and two are here.",
        &how,
        &root.join("research"),
    )
    .unwrap();
}

#[test]
fn quote_verbatim_reports_each_question_and_writes_its_json() {
    let (d, root) = world("helpers-quote");
    cached(&root);
    let r = s(&root);
    let got = quote_verbatim(&a(&["--root", &r, "0001"]), &root);
    assert_eq!(got.code, 0, "{}", got.stderr);
    assert!(
        got.stdout
            .contains("quote-verbatim: questions/0001-paddies.html - 2 footnotes\n"),
        "{}",
        got.stdout
    );
    assert!(got.stdout.ends_with(&format!(
        "  report for quote-check: {r}/.git/quote-verbatim/0001.json\n"
    )));
    let json = std::fs::read_to_string(root.join(".git/quote-verbatim/0001.json")).unwrap();
    assert!(json.contains("\"question\": \"0001-paddies.html\""));
    let out = d.join("q.json");
    let notes = quote_verbatim(
        &a(&["--root", &r, "0001", "--notes", "1", "--json", &s(&out)]),
        &root,
    );
    assert!(notes
        .stdout
        .ends_with(&format!("  report for quote-check: {}\n", out.display())));
    let within = quote_verbatim(&a(&["--root", &r, "--in", "land"]), &root);
    assert_eq!(within.code, 0, "{}", within.stderr);
    let offline = d.join("offline");
    std::fs::create_dir_all(&offline).unwrap();
    std::fs::write(
        offline.join(l7r_gate_research::verbatim::fetch::name_for(
            "https://e.org/a",
        )),
        "<p>one</p>",
    )
    .unwrap();
    let off = quote_verbatim(
        &a(&[
            "--root",
            &r,
            "0001",
            "--offline",
            &s(&offline),
            "--json",
            &s(&out),
        ]),
        &root,
    );
    assert_eq!(off.code, 0);
    let none = quote_verbatim(&a(&["--root", &r, "9999"]), &root);
    assert_eq!((none.code, none.stderr.as_str()), (2, "quote-verbatim: '9999' names no question - e.g. make quote-verbatim Q=0041 or IN=homesteads\n"));
    assert_eq!(quote_verbatim(&a(&["--root", &r]), &root).stderr, "quote-verbatim: 'nothing' names no question - e.g. make quote-verbatim Q=0041 or IN=homesteads\n");
    assert_eq!(quote_verbatim(&a(&["--x"]), &root).code, 2);
    assert_eq!(
        quote_verbatim(&a(&["--root", &r, "--in", "nope"]), &root).code,
        2
    );
    std::fs::write(root.join("research/contents.json"), "{").unwrap();
    assert_eq!(
        quote_verbatim(&a(&["--root", &r, "--in", "land"]), &root).code,
        1
    );
    assert_eq!(quote_verbatim(&a(&["--root", &r, "0001"]), &root).code, 1);
}

#[test]
fn quote_verbatim_stops_where_a_fetch_or_a_write_fails() {
    let (d, root) = world("helpers-quote-fail");
    let r = s(&root);
    cached(&root);
    std::fs::write(root.join("research/blocked-domains.json"), "{").unwrap();
    let blocked = quote_verbatim(&a(&["--root", &r, "0001"]), &root);
    assert_eq!(blocked.code, 1);
    put(
        &root.join("research"),
        "blocked-domains.json",
        FILES
            .iter()
            .find(|f| f.0 == "blocked-domains.json")
            .unwrap()
            .1,
    );
    std::fs::write(d.join("file"), "x").unwrap();
    let out = d.join("file/q.json");
    assert_eq!(
        quote_verbatim(&a(&["--root", &r, "0001", "--json", &s(&out)]), &root).code,
        1
    );
    let offline = d.join("offline");
    std::fs::create_dir_all(&offline).unwrap();
    put(&root.join("research"), "questions/0001-paddies.notes.html", "<ol>\n<li data-note=\"k\"><a href=\"http://a..b/x\"><code>src-a</code></a> and <a href=\"http://[bad/x\">x</a> and <a href=\"http://[bad/y\">y</a> - \"one\" <span class=\"orig\" data-orig=\"k#1\"></span></li>\n<li data-note=\"n\">no publicly readable source</li>\n</ol>\n");
    assert_eq!(
        quote_verbatim(
            &a(&["--root", &r, "0001", "--offline", &s(&offline)]),
            &root
        )
        .code,
        1
    );
    put(&root.join("research"), "questions/0001-paddies.notes.html", "<ol>\n<li data-note=\"k\"><a href=\"http://a..b/x\"><code>src-a</code></a> - \"one\" <span class=\"orig\" data-orig=\"k#1\"></span></li>\n<li data-note=\"n\">no publicly readable source</li>\n</ol>\n");
    let named = quote_verbatim(
        &a(&["--root", &r, "0001", "--json", &s(&d.join("r.json"))]),
        &root,
    );
    assert!(
        named
            .stdout
            .contains("  refused: a..b - UnicodeEncodeError: label empty or too long"),
        "{}",
        named.stdout
    );
    assert!(std::fs::read_to_string(d.join("r.json"))
        .unwrap()
        .contains("\"refused\": {\n  \"a..b\""));
    put(&root.join("research"), "questions/0001-paddies.notes.html", "<ol>\n<li data-note=\"k\"><a href=\"http://a..b/x\"><code>src-a</code></a> and <a href=\"http://[bad/x\">x</a> and <a href=\"http://[bad/y\">y</a> - \"one\" <span class=\"orig\" data-orig=\"k#1\"></span></li>\n<li data-note=\"n\">no publicly readable source</li>\n</ol>\n");
    let refused = quote_verbatim(&a(&["--root", &r, "0001"]), &root);
    assert_eq!(refused.code, 1);
    assert!(refused.stderr.starts_with("ValueError: Invalid IPv6 URL"));
}

#[test]
fn record_prepass_lists_a_question_the_registry_and_a_section() {
    let (d, root) = world("helpers-prepass");
    let r = s(&root);
    let got = record_prepass(&a(&["--root", &r, "0001"]), &root);
    assert_eq!(got.code, 0, "{}", got.stderr);
    assert!(got.stdout.contains("\n## What to hand the check (feature 258)\n\nThe files these sections are written in - read THESE, not the built site:\n\n  research/questions/0001-paddies.drawing.html\n  research/questions/0001-paddies.html\n"), "{}{}", got.stdout, got.stderr);
    assert_eq!(
        record_prepass(&a(&["--root", &r, "SOURCES"]), &root).code,
        0
    );
    assert_eq!(
        record_prepass(&a(&["--root", &r, "--in", "land"]), &root).code,
        0
    );
    let none = record_prepass(&a(&["--root", &r]), &root);
    assert_eq!(none.stderr, "record-prepass: 'nothing' names no question - e.g. make record-prepass Q=0041, IN=homesteads, or Q=SOURCES\n");
    let out = d.join("rp.json");
    assert_eq!(
        record_prepass(&a(&["--root", &r, "0001", "--json", &s(&out)]), &root).code,
        0
    );
    assert!(std::fs::read_to_string(&out)
        .unwrap()
        .starts_with("{\n \"page\": \"0001\","));
    std::fs::write(d.join("file"), "x").unwrap();
    assert_eq!(
        record_prepass(
            &a(&["--root", &r, "0001", "--json", &s(&d.join("file/x.json"))]),
            &root
        )
        .code,
        1
    );
    assert_eq!(record_prepass(&a(&["--y"]), &root).code, 2);
    std::fs::create_dir_all(root.join("l7r/diagram/interactive/assets")).unwrap();
    std::fs::write(
        root.join("l7r/diagram/interactive/assets/glossary.json"),
        "[]",
    )
    .unwrap();
    assert_eq!(record_prepass(&a(&["--root", &r, "0001"]), &root).code, 1);
    std::fs::write(root.join("research/contents.json"), "{").unwrap();
    assert_eq!(
        record_prepass(&a(&["--root", &r, "--in", "land"]), &root).code,
        1
    );
}

#[test]
fn style_prepass_reads_a_question_and_its_notes() {
    let (_d, root) = world("helpers-style");
    let r = s(&root);
    assert_eq!(style_prepass(&a(&["--root", &r, "0002"]), &root).code, 0);
    put(
        &root.join("research"),
        "assets/glossary-variants.txt",
        "1650\tx\n",
    );
    let got = style_prepass(&a(&["--root", &r, "0001"]), &root);
    assert!(got
        .stdout
        .contains("== 0001-paddies.html\nMETRIC WITHOUT A CONVERSION (0)"));
    assert_eq!(style_prepass(&a(&["--root", &r, "9999"]), &root).stderr, "style-prepass: no question is '9999' - name one by its number, e.g. make style-prepass Q=0041\n");
    assert_eq!(style_prepass(&a(&["--root", &r]), &root).code, 2);
    assert_eq!(style_prepass(&a(&["--z"]), &root).code, 2);
    std::fs::write(
        root.join("research/questions/0001-paddies.notes.html"),
        [0xff],
    )
    .unwrap();
    assert_eq!(style_prepass(&a(&["--root", &r, "0001"]), &root).code, 1);
    std::fs::write(root.join("research/questions/0001-paddies.notes.html"), "").unwrap();
    std::fs::write(root.join("research/questions/0001-paddies.html"), [0xff]).unwrap();
    assert_eq!(style_prepass(&a(&["--root", &r, "0001"]), &root).code, 1);
    std::fs::write(root.join("research/assets/glossary-variants.txt"), [0xff]).unwrap();
    assert_eq!(style_prepass(&a(&["--root", &r, "0002"]), &root).code, 1);
    std::fs::write(root.join("research/assets/glossary-variants.txt"), "").unwrap();
    std::fs::set_permissions(
        root.join("research/questions/0002-coins.html"),
        std::fs::Permissions::from_mode(0o000),
    )
    .unwrap();
    assert_eq!(style_prepass(&a(&["--root", &r, "0002"]), &root).code, 1);
}

#[test]
#[expect(
    clippy::too_many_lines,
    reason = "every refusal and save of source-pages, one after another on one ledger"
)]
fn source_pages_saves_from_the_cache_and_refuses_without_a_reason() {
    let (d, root) = world("helpers-pages");
    cached(&root);
    let out = s(&d.join("saved"));
    let got = source_pages(
        &a(&[
            &out,
            "https://e.org/a",
            "--question",
            "0001",
            "--sought",
            "the paddies",
        ]),
        &root,
    );
    assert_eq!(got.code, 0, "{}", got.stderr);
    assert!(got
        .stdout
        .contains("sources-consulted: https://e.org/a - no earlier read on the ledger\n"));
    assert!(got.stdout.ends_with(&format!(
        "  saved 1 of 1 to {out} - hand source-reader the manifest\n"
    )));
    let quotes = d.join("quotes.json");
    std::fs::write(&quotes, "[\"one\"]").unwrap();
    assert_eq!(
        source_pages(
            &a(&[
                &s(&d.join("ex")),
                "https://e.org/a",
                "--quotes",
                &s(&quotes),
                "--no-ledger"
            ]),
            &root
        )
        .code,
        0
    );
    std::fs::write(&quotes, "{").unwrap();
    assert_eq!(
        source_pages(
            &a(&[
                &s(&d.join("ex2")),
                "https://e.org/a",
                "--quotes",
                &s(&quotes),
                "--no-ledger"
            ]),
            &root
        )
        .code,
        1
    );
    assert_eq!(
        source_pages(&a(&[&out]), &root).stderr,
        "source-pages: no pointer given - URL=<u1> [URL=<u2> ...]\n"
    );
    assert!(
        source_pages(&a(&[&out, "https://e.org/a", "--question", "0001"]), &root)
            .stderr
            .starts_with("source-pages: say what this read is for")
    );
    assert_eq!(source_pages(&a(&[]), &root).code, 2);
    assert_eq!(source_pages(&a(&[&out, "--bad"]), &root).code, 2);
    std::fs::write(root.join("research/source-attempts.jsonl"), "{\"url\": \"e.org/a\", \"question\": \"0001\", \"outcome\": \"not-found\", \"sought\": \"x\"}\n").unwrap();
    let judged = source_pages(
        &a(&[
            &out,
            "https://e.org/a",
            "--question",
            "0001",
            "--sought",
            "y",
        ]),
        &root,
    );
    assert!(judged.stderr.starts_with(
        "source-pages: https://e.org/a was already read for question 0001 on None: not-found - x\n"
    ));
    assert_eq!(
        source_pages(
            &a(&[
                &out,
                "https://e.org/a",
                "--question",
                "0001",
                "--sought",
                "y",
                "--reread",
                "a new reason"
            ]),
            &root
        )
        .code,
        0
    );
    std::fs::write(root.join("research/source-attempts.jsonl"), "[1]\n").unwrap();
    assert_eq!(
        source_pages(
            &a(&[
                &out,
                "https://e.org/a",
                "--question",
                "0001",
                "--sought",
                "y"
            ]),
            &root
        )
        .code,
        1
    );
    std::fs::write(root.join("research/source-attempts.jsonl"), "").unwrap();
    std::fs::create_dir_all(root.join(".specify")).unwrap();
    std::fs::write(root.join(".specify/feature.json"), "[1]").unwrap();
    // The ledger's context read from this thread's own environment, never the shell's (feature 451 T24): with no feature named, the
    // pointer is read and refused; with one named, the pointer is never read and the save goes on.
    let ctx = || {
        source_pages(
            &a(&[
                &out,
                "https://e.org/a",
                "--question",
                "none",
                "--sought",
                "y",
            ]),
            &root,
        )
    };
    let refused = ctx();
    assert_eq!(refused.code, 1, "{}", refused.stderr);
    assert_eq!(
        refused.stderr,
        "AttributeError: 'list' object has no attribute 'get'\n"
    );
    VARS.with(|v| {
        v.borrow_mut()
            .insert("SPECIFY_FEATURE".to_owned(), "451-x".to_owned())
    });
    let named = ctx();
    VARS.with(|v| v.borrow_mut().clear());
    assert_eq!(named.code, 0, "{}", named.stderr);
    std::fs::remove_file(root.join(".specify/feature.json")).unwrap();
    std::fs::write(d.join("blocker"), "").unwrap();
    assert_eq!(
        source_pages(
            &a(&[&s(&d.join("blocker/x")), "https://e.org/a", "--no-ledger"]),
            &root
        )
        .code,
        1
    );
}

#[test]
fn the_residue_save_and_the_runner() {
    let (d, root) = world("helpers-residue");
    let here = std::env::current_dir().unwrap();
    assert!(save_cached(&["https://e.org/none".to_owned()], &d.join("pages")).is_ok());
    assert!(std::fs::read_to_string(d.join("pages/MANIFEST.txt"))
        .unwrap()
        .contains("NOT-CACHED"));
    std::fs::write(d.join("file"), "x").unwrap();
    assert!(save_cached(&[], &d.join("file/x")).is_err());
    assert_eq!(std::env::current_dir().unwrap(), here);
    let r = s(&root);
    for name in [
        "quote_verbatim",
        "record_prepass",
        "style_prepass",
        "source_pages",
    ] {
        assert!(run(name, &a(&["--root", &r]), &root).is_some());
    }
    assert!(run("nope", &[], &root).is_none());
    assert!(entry_dir(&root, "x").ends_with(entry_dir(Path::new(""), "x")));
}
