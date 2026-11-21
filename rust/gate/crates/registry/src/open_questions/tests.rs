//! The open-questions report over a scratch record (feature 449 T149; its byte-for-byte equality with `open_questions.py` is the slice's
//! differential on the real record).

use super::{cli, heading_key, run, visible};
use l7r_gate_core::checks::scratch;
use l7r_gate_core::record::testkit::{commit, git, put};

const Q: &str = "research/questions";

fn args(list: &[&str]) -> Vec<String> {
    list.iter().map(|s| (*s).to_owned()).collect()
}

fn record() -> l7r_shared::tempdir::TempDir {
    let root = scratch("registry-open");
    git(&root, &["init", "-q"]);
    git(&root, &["config", "user.email", "t@t"]);
    git(&root, &["config", "user.name", "t"]);
    let first = format!("{Q}/{}-a.html", "0001");
    crate::testkit::hamlet(&root, &first);
    put(&root, &first, "<h2 id=\"paddies-wet\">Are paddies wet? <em>Yes</em></h2>\n<!-- tags: subject=farming; level=x -->\n<p>One is a GUESS. Two follows. (A GUESS again.) x</p>\n<p>A GUESS. A GUESS.</p>\n<p>See <a href=\"0002-b.html#b-dry\">b</a> and <a href=\"#paddies-wet\">self</a> and <a href=\"0009-z.html#nowhere\">z</a>. A claim here.<sup class=\"fn\" data-note=\"n1\"></sup> more</p>\n<!-- a GUESS in a comment -->\n");
    put(&root, &format!("{Q}/0001-a.notes.html"), "<ol><li data-note=\"n1\">no publicly readable source <!-- c --></li>\n<li data-note=\"n2\">no publicly readable source; settled 2026-01-02</li>\n<li data-note=\"n3\">a source</li></ol>\n");
    put(
        &root,
        &format!("{Q}/0002-b.html"),
        "<h2 id=\"b-dry\">B dry</h2>\n<p>The shares are GUESSES.</p>\n",
    );
    put(
        &root,
        &format!("{Q}/0002-b.drawing.html"),
        "<h2 id=\"b-drawn\">How B is drawn</h2>\n<p>Drawn by GUESS.</p>\n",
    );
    put(
        &root,
        &format!("{Q}/0003-c.html"),
        "<p>no heading GUESS</p>\n",
    );
    put(
        &root,
        &format!("{Q}/0004-quiet.html"),
        "<h2 id=\"quiet\">Quiet</h2>\n<!-- tags: subject=money -->\n<p>Nothing open.</p>\n",
    );
    put(&root, &format!("{Q}/x.html"), "<h2 id=\"x\">X GUESS</h2>\n");
    // a drawing page with no research page beside it; a page whose heading is no h2, which a kind names; a heading of no word
    put(
        &root,
        &format!("{Q}/0010-lone.drawing.html"),
        "<h2 id=\"lone\">Lone GUESS</h2>\n",
    );
    put(
        &root,
        &format!("{Q}/0011-three.html"),
        "<h3 id=\"h-three\">Three</h3>\n",
    );
    put(
        &root,
        &crate::about::modal_rel(&crate::kinds::HAMLET_REGISTRY, "byre"),
        &crate::testkit::modal("byre", &format!("{Q}/0011-three.html")),
    );
    put(
        &root,
        &format!("{Q}/0012-q.html"),
        "<h2 id=\"q-12\">?</h2>\n<p>A GUESS.</p>\n",
    );
    put(&root, "l7r/diagram/z.py", "# paddies alone\n");
    put(
        &root,
        "l7r/diagram/x.py",
        "# paddies-wet is read here\nx = 1  # Are paddies wet?\n# b-dry\n",
    );
    put(&root, "l7r/diagram/y.txt", "paddies-wet in a text file\n");
    put(
        &root,
        "docs/notes.md",
        "a GUESS line\nnone\n  GUESSES too  \n",
    );
    put(&root, "tests/t.py", "GUESS\n");
    put(&root, "dev/run-log/r.md", "GUESS\n");
    put(&root, "ABOUT", "GUESS at the root\n");
    std::fs::write(root.join("blob.bin"), [0xff, 0x00]).unwrap();
    commit(&root, "the record");
    root
}

#[test]
fn every_guess_and_absence_with_the_features_it_touches() {
    let root = record();
    let text = run(&root).unwrap();
    // the question pages' paths built from parts, so the research-pointer check reads no fixture here
    let first = format!("## Are paddies wet? Yes\n   {Q}/{}-a.html\n", "0001");
    let second = format!(
        "## B dry\n   {Q}/{}-b.html\n   map features: alder (through 'Are paddies wet? Yes'); ",
        "0002"
    );
    for want in [
        "OPEN RESEARCH QUESTIONS - read from the record and the tracked files now (feature 285)\n\n",
        "page                               questions  guesses  absences  settled\n",
        "farming                                    1        3         1        1\n",
        "untagged                                   4        4         0        0\n",
        "TOTAL                                      5        7         1        1\n",
        "GUESS lines outside the record: 3 (ABOUT 1, docs 2)\n",
        "subject: farming\n",
        first.as_str(),
        "   - GUESS: One is a GUESS.\n   - GUESS: (A GUESS again.) x\n   - GUESS: A GUESS.\n",
        "   - UNSOURCED: A claim here.\n       no publicly readable source\n",
        "   - UNSOURCED (searched twice, settled): (the claim is not marked in the text)\n       no publicly readable source; settled 2026-01-02\n",
        second.as_str(),
        "## How B is drawn\n",
        "   map features: no map feature found depending on it\n",
        "GUESSES MARKED OUTSIDE THE RECORD\n",
        "\nABOUT\n   1: GUESS at the root\n",
        "\ndocs/notes.md\n   1: a GUESS line\n   3: GUESSES too\n",
    ] {
        assert!(text.contains(want), "{want}\n---\n{text}");
    }
    // the first question's features: every kind names it, and the engine line quoting its anchor and its heading
    let features = text
        .lines()
        .find(|l| l.starts_with("   map features: alder; "))
        .unwrap();
    assert!(features.ends_with("; l7r/diagram/x.py:1; l7r/diagram/x.py:2"));
    assert!(text.contains("; l7r/diagram/x.py:3\n"));
    assert!(!text.contains("Quiet") && !text.contains("tests/t.py") && !text.contains("run-log"));
}

#[test]
fn the_command_line() {
    let root = record();
    let r = root.to_string_lossy().into_owned();
    assert!(cli(&args(&[&format!("--root={r}")]))
        .stdout
        .starts_with("OPEN RESEARCH QUESTIONS"));
    assert_eq!(cli(&args(&[])).code, 2);
}

#[test]
fn a_registry_that_does_not_load_fails_the_report() {
    let root = record();
    let r = root.to_string_lossy().into_owned();
    std::fs::remove_file(root.join(crate::about::modal_rel(
        &crate::kinds::HAMLET_REGISTRY,
        "byre",
    )))
    .unwrap();
    let failed = cli(&args(&["--root", &r]));
    assert_eq!(
        (failed.code, failed.stderr.as_str()),
        (
            1,
            "ValueError: Byre: the explanation is the docstring, and there is none\n"
        )
    );
}

#[test]
fn a_heading_s_key_and_a_page_s_visible_text() {
    assert_eq!(heading_key("Why? Because"), "Why?");
    assert_eq!(heading_key("No question"), "No question");
    assert_eq!(visible("<p>a <!-- b --> <b>c</b>\n d</p>"), "a c d");
}
