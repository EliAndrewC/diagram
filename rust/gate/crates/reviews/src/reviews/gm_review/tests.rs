//! The GM-review queue's commands on scratch features: every verb, refusal and raise, and the queue's one writer (feature 449 T91). The
//! same outputs as `scripts/gm_review.py` are the differential's (`scratchpad/t91/diff.py`); these pin the branches.

use std::path::{Path, PathBuf};

use serde_json::{json, Value};

use super::super::tests::{commit, dir, put, sh};
use super::py::Raised;
use super::{
    add_row, cli, cli_in, ensure_box, escalated, feature, name, num, question, rows, Ctx, USAGE,
};
use crate::Reply;

pub(super) fn args(words: &[&str]) -> Vec<String> {
    words.iter().map(|w| (*w).to_owned()).collect()
}

/// `make gm-review ...` in `root` with the GM's `words`, at `cols` columns, the closing check under `python`.
pub(super) fn run_with(
    root: &Path,
    words: &[&str],
    gm_words: &str,
    cols: usize,
    python: &str,
) -> Reply {
    let width = move |_: usize| cols;
    let ctx = Ctx {
        root,
        tree: root,
        python,
        words: gm_words,
        columns: &width,
    };
    cli_in(&args(words), &ctx)
}

pub(super) fn run(root: &Path, words: &[&str]) -> Reply {
    run_with(root, words, "", 100, "python3")
}

pub(super) fn jl(rows: &[Value]) -> String {
    rows.iter().map(|r| r.to_string() + "\n").collect()
}

fn read(root: &Path, rel: &str) -> String {
    std::fs::read_to_string(root.join(rel)).unwrap()
}

/// The rows of a feature as written, parsed.
fn written(root: &Path, rel: &str) -> Vec<Value> {
    read(root, rel)
        .lines()
        .map(|l| serde_json::from_str(l).unwrap())
        .collect()
}

#[test]
fn the_usage_and_the_process_entry() {
    let d = dir("gm-usage");
    for words in [
        &[][..],
        &["bogus"],
        &["list", "1", "2"],
        &["explain", "1", "2", "3"],
        &["owed-check", "x"],
    ] {
        let got = run(&d, words);
        assert_eq!(
            (got.code, got.stderr.as_str(), got.stdout.as_str()),
            (2, USAGE, "")
        );
    }
    let got = cli(&args(&["bogus"]));
    assert_eq!(got.code, 2);
    let empty = run(&d, &["list"]);
    assert_eq!(empty.stdout, "gm-review: nothing waits on the GM\n");
}

#[test]
fn a_feature_by_number_or_name() {
    let d = dir("gm-feature");
    put(&d, "specs/042-b/x", "");
    put(&d, "specs/042-a/x", "");
    put(&d, "specs/043-file", "");
    put(&d, "specs/abc/x", "");
    assert!(feature(&d, "42").unwrap().ends_with("042-a"));
    assert!(feature(&d, "0042").unwrap().ends_with("042-a"));
    assert!(feature(&d, "abc/").unwrap().ends_with("abc"));
    assert!(feature(&d, "./abc").unwrap().ends_with("abc"));
    assert_eq!(feature(&d, "").unwrap(), d.join("specs"));
    assert_eq!(feature(&d, "/").unwrap(), PathBuf::from("/"));
    assert_eq!(name(Path::new("/")), "");
    assert_eq!(name(&d.join("specs/..")), "..");
    for missing in ["43", "nope", "999"] {
        assert_eq!(
            feature(&d, missing).unwrap_err(),
            Raised::Exit(format!("gm-review: no specs/{missing}* directory"))
        );
    }
    assert_eq!(
        feature(&d, "\u{b2}").unwrap_err(),
        Raised::Refused("invalid literal for int() with base 10: '\u{b2}'".to_owned())
    );
    assert!(num(&d.join("specs/abc")).is_err());
    let got = run(&d, &["accept", "nope", "f", "two words"]);
    assert_eq!(
        (got.code, got.stderr.as_str()),
        (1, "gm-review: no specs/nope* directory\n")
    );
}

#[test]
fn accept_adds_a_row_and_the_gms_box_once() {
    let d = dir("gm-accept");
    put(&d, "specs/500-x/tasks.md", "- [ ] T01 open\n\n\n");
    let got = run(&d, &["accept", "500", "a finding", "one"]);
    assert_eq!(
        got.stderr,
        "gm-review: refused - REASON needs two words or more - the GM reads it\n"
    );
    let got = run(&d, &["accept", "500", "a finding", "two words"]);
    assert_eq!(
        got.stdout,
        "accept: recorded - a row the GM may read and overturn (make gm-review)\n"
    );
    let box_text = "- [ ] T01 open\n- [ ] GM review (make gm-reviewed F=500) [lands-open]\n      research: rendering\n      verify: the GM reviewed every row (make gm-review lists them)\n";
    assert_eq!(read(&d, "specs/500-x/tasks.md"), box_text);
    let _ = run(&d, &["accept", "500", "again", "two words"]);
    assert_eq!(read(&d, "specs/500-x/tasks.md"), box_text);
    let rs = written(&d, "specs/500-x/gm-review.jsonl");
    assert_eq!(rs.len(), 2);
    assert_eq!(rs[0]["kind"], json!("accepted"));
    assert_eq!(
        rs[0].as_object().unwrap().keys().collect::<Vec<_>>(),
        ["kind", "finding", "why", "utc"]
    );
    // the GM reviewed every row: no box is added, a ticked one is reopened by a new row
    put(
        &d,
        "specs/501-y/gm-review.jsonl",
        &jl(&[json!({"reviewed": "x"})]),
    );
    put(
        &d,
        "specs/501-y/tasks.md",
        "- [x] GM review (make gm-reviewed F=501) [lands-open]\r\nend\r\n",
    );
    assert!(!ensure_box(&d.join("specs/501-y")).unwrap());
    assert!(add_row(&d.join("specs/501-y"), &json!({"kind": "known-drift"})).unwrap());
    assert_eq!(
        read(&d, "specs/501-y/tasks.md"),
        "- [ ] GM review (make gm-reviewed F=501) [lands-open]\nend\n"
    );
    assert!(!ensure_box(&d.join("specs/501-y")).unwrap());
    assert!(!ensure_box(&d.join("specs/502-none")).unwrap());
    // a link to a directory that is not there: the append raises
    std::fs::create_dir_all(d.join("specs/503-z")).unwrap();
    std::os::unix::fs::symlink(d.join("nowhere/x"), d.join("specs/503-z/gm-review.jsonl")).unwrap();
    let got = run(&d, &["accept", "503", "f", "two words"]);
    assert!(
        got.code == 1
            && got
                .stderr
                .starts_with("Traceback (most recent call last):\n  l7r-gate gm-review\nOSError"),
        "{}",
        got.stderr
    );
    std::fs::create_dir_all(d.join("specs/504-w/tasks.md")).unwrap();
    assert!(!ensure_box(&d.join("specs/504-w")).unwrap());
}

#[test]
fn a_question_is_written_owed_and_its_number_said() {
    let d = dir("gm-question");
    put(&d, "specs/510-q/tasks.md", "- [x] T01\n");
    let got = run(&d, &["question", "510", "three words only", "s"]);
    assert_eq!(got.stderr, "gm-review: refused - a question for the GM is a sentence he can answer - four words or more\n");
    put(
        &d,
        "specs/510-q/gm-review.jsonl",
        "not json\n{\"kind\": \"accepted\"}\n",
    );
    let got = run(
        &d,
        &["question", "510", "Is this a question here?", "the source"],
    );
    assert_eq!(got.stdout, "gm-question: row 1 of 510-q - owed escalation-check before it reaches the GM (make gm-escalated F=510 ROW=1)\n");
    let rs = rows(&d.join("specs/510-q")).unwrap();
    assert_eq!(rs[1]["status"], json!("owed"));
    assert!(
        question(
            &d.join("specs/510-q"),
            "a b c d",
            "src",
            Some("2026-01-01T00:00:00Z")
        )
        .unwrap()
            == 2
    );
    assert_eq!(
        rows(&d.join("specs/510-q")).unwrap()[2]["utc"],
        json!("2026-01-01T00:00:00Z")
    );
    put(&d, "specs/511-bad/gm-review.jsonl", "");
    std::fs::write(d.join("specs/511-bad/gm-review.jsonl"), b"{}\n\xff").unwrap();
    let got = run(&d, &["question", "511", "a b c d", "s"]);
    assert_eq!(got.stderr, "gm-review: refused - 'utf-8' codec can't decode byte 0xff in position 3: invalid start byte\n");
    put(&d, "specs/512-int/gm-review.jsonl", "3\n");
    put(&d, "specs/512-int/tasks.md", "x\n");
    let got = run(&d, &["question", "512", "a b c d", "s"]);
    assert!(
        got.stderr.contains("TypeError: argument of type 'int'"),
        "{}",
        got.stderr
    );
    put(&d, "specs/abc/tasks.md", "x\n");
    let got = run(&d, &["question", "abc", "a b c d", "s"]);
    assert_eq!(
        got.stderr,
        "gm-review: refused - invalid literal for int() with base 10: 'abc'\n"
    );
}

fn questions(d: &Path) {
    put(
        d,
        "specs/520-q/gm-review.jsonl",
        &jl(&[
            json!({"kind": "question", "status": "owed", "question": "q0 a b c"}),
            json!({"kind": "question", "status": "kept", "question": "q1 a b c"}),
            json!({"kind": "question", "status": "cut", "reviewed": "x"}),
            json!({"kind": "question", "status": "kept", "reviewed": "x"}),
            json!({"kind": "question", "status": "owed"}),
            json!({"kind": "question"}),
            json!({"kind": "accepted"}),
        ]),
    );
}

#[test]
fn escalation_checks_verdict_on_each_kind_of_row() {
    let d = dir("gm-escalated");
    questions(&d);
    let refused = |words: &[&str], why: &str| {
        let got = run(&d, words);
        let want = format!("gm-review: refused - {why}\n");
        assert!(got.code == 1 && got.stderr == want, "{words:?}");
    };
    refused(
        &["escalated", "520", "9", "KEEP", "a b"],
        "ROW=9 is no question of 520-q - make gm-review lists the owed ones",
    );
    refused(
        &["escalated", "520", "-1", "KEEP", "a b"],
        "ROW=-1 is no question of 520-q - make gm-review lists the owed ones",
    );
    refused(
        &["escalated", "520", "6", "KEEP", "a b"],
        "ROW=6 is no question of 520-q - make gm-review lists the owed ones",
    );
    refused(
        &["escalated", "520", "x", "KEEP", "a b"],
        "invalid literal for int() with base 10: 'x'",
    );
    refused(
        &["escalated", "520", "0", "KEEP", "a b", "z"],
        "invalid literal for int() with base 10: 'z'",
    );
    refused(
        &["escalated", "520", "1", "KEEP", "a b", "4"],
        "SUPERSEDED_BY closes a question: VERDICT=CUT",
    );
    refused(
        &["escalated", "520", "1", "CUT", "a b", "0"],
        "SUPERSEDED_BY=0 is no later question of 520-q than ROW=1",
    );
    refused(
        &["escalated", "520", "1", "CUT", "a b", "6"],
        "SUPERSEDED_BY=6 is no later question of 520-q than ROW=1",
    );
    refused(
        &["escalated", "520", "1", "CUT", "a b", "9"],
        "SUPERSEDED_BY=9 is no later question of 520-q than ROW=1",
    );
    refused(
        &["escalated", "520", "0", "CUT", "a b", "4"],
        "ROW=0 of 520-q is owed: SUPERSEDED_BY closes a kept question the GM has not reviewed",
    );
    refused(
        &["escalated", "520", "3", "CUT", "a b", "4"],
        "ROW=3 of 520-q is kept: SUPERSEDED_BY closes a kept question the GM has not reviewed",
    );
    refused(&["escalated", "520", "1", "KEEP", "a b"], "ROW=1 of 520-q is already kept - a kept question the record overturned is closed with SUPERSEDED_BY=<its later row>");
    refused(&["escalated", "520", "5", "KEEP", "a b"], "ROW=5 of 520-q is already None - a kept question the record overturned is closed with SUPERSEDED_BY=<its later row>");
    refused(
        &["escalated", "520", "0", "MAYBE", "a b"],
        "VERDICT is KEEP or CUT, escalation-check's",
    );
    refused(
        &["escalated", "520", "0", "KEEP", "one"],
        "REASON is escalation-check's, two words or more",
    );
    let got = run(&d, &["escalated", "520", "1", "CUT", "", "4"]);
    assert_eq!(
        got.stdout,
        "gm-escalated: question 1 of 520-q CUT - closed, not the GM's: superseded by row 4: \n"
    );
    let got = run(&d, &["escalated", "520", "0", "KEEP", "his to make", ""]);
    assert_eq!(got.stdout, "gm-escalated: question 0 of 520-q KEPT - it is the GM's decision now: name it in this turn's final message as \"520#0\" with the question\n");
    let rs = written(&d, "specs/520-q/gm-review.jsonl");
    assert_eq!(rs[0]["escalation"], json!("his to make"));
    assert_eq!(rs[1]["status"], json!("cut"));
    assert_eq!(rs.len(), 7);
    let kept = escalated(
        &d.join("specs/520-q"),
        4,
        "CUT",
        "not his",
        Some("2026-01-02T03:04:05Z"),
        None,
    )
    .unwrap();
    assert!(kept.contains("CUT"));
    assert_eq!(
        written(&d, "specs/520-q/gm-review.jsonl")[4]["reviewed"],
        json!("2026-01-02")
    );
    put(&d, "specs/521-list/gm-review.jsonl", "[\"kind\"]\n");
    let got = run(&d, &["escalated", "521", "0", "KEEP", "a b"]);
    assert!(
        got.stderr
            .contains("AttributeError: 'list' object has no attribute 'get'"),
        "{}",
        got.stderr
    );
}

#[test]
fn a_rows_review_alone() {
    let d = dir("gm-reviewed-row");
    questions(&d);
    let got = run_with(&d, &["reviewed-row", "520", "0"], "one", 100, "python3");
    assert_eq!(
        got.stderr,
        "gm-review: refused - WORDS are the GM's own, two words or more\n"
    );
    let got = run(&d, &["reviewed-row", "520", "7"]);
    assert_eq!(
        got.stderr,
        "gm-review: refused - ROW=7: 520-q has rows 0-6\n"
    );
    let got = run(&d, &["reviewed-row", "520", "y"]);
    assert_eq!(
        got.stderr,
        "gm-review: refused - invalid literal for int() with base 10: 'y'\n"
    );
    let got = run_with(
        &d,
        &["reviewed-row", "520", "3"],
        "his own words",
        100,
        "python3",
    );
    assert_eq!(
        got.stdout,
        "gm-reviewed: row 3 of 520-q reviewed; 5 still wait on the GM\n"
    );
    let rs = written(&d, "specs/520-q/gm-review.jsonl");
    assert_eq!(rs[3]["gm_words"], json!("his own words"));
    assert_ne!(rs[3]["reviewed"], json!("x"));
    let got = run(&d, &["reviewed-row", "520", "0"]);
    assert_eq!(
        got.stdout,
        "gm-reviewed: row 0 of 520-q reviewed; 4 still wait on the GM\n"
    );
    put(&d, "specs/522-str/gm-review.jsonl", "\"x\"\n{}\n");
    let got = run(&d, &["reviewed-row", "522", "1"]);
    assert_eq!(
        got.stdout,
        "gm-reviewed: row 1 of 522-str reviewed; 1 still wait on the GM\n"
    );
    put(&d, "specs/523-null/gm-review.jsonl", "{}\nnull\n");
    let got = run(&d, &["reviewed-row", "523", "0"]);
    assert!(
        got.stderr
            .contains("TypeError: argument of type 'NoneType'"),
        "{}",
        got.stderr
    );
}

/// A `close_check.py` stand-in under `scripts/gates/` that prints `out` and exits `code`.
fn close_check(root: &Path, out: &str, code: i32) {
    put(
        root,
        "scripts/gates/close_check.py",
        &format!("import sys\nassert sys.argv[1] == '--reasons-json'\nprint({out:?})\nsys.exit({code})\n"),
    );
}

#[test]
fn the_gm_reviews_a_feature_and_his_box_is_ticked() {
    let d = dir("gm-reviewed");
    put(
        &d,
        "specs/530-x/gm-review.jsonl",
        &jl(&[
            json!({"kind": "arbiter", "why": "a why", "note": "a note", "trigger": "ask:a"}),
            json!({"kind": "arbiter", "tooling_fix": "the fix", "finding": "f"}),
            json!({"kind": "accepted", "reviewed": null}),
            json!({"kind": "accepted", "why": 5}),
        ]),
    );
    put(
        &d,
        "specs/530-x/tasks.md",
        "- [x] T01\n- [ ] GM review (make gm-reviewed F=530)\n",
    );
    put(&d, "specs/531-to/x", "");
    let got = run_with(&d, &["reviewed", "530"], "one", 100, "python3");
    assert_eq!(
        got.stderr,
        "gm-review: refused - WORDS are the GM's own, two words or more\n"
    );
    for (o, why) in [
        ("4", "OVERTURN=<row number> needs TO=<an open feature>"),
        ("-1", "OVERTURN=<row number> needs TO=<an open feature>"),
        ("q", "invalid literal for int() with base 10: 'q'"),
    ] {
        let got = run(&d, &["reviewed", "530", o, "531"]);
        assert_eq!(got.stderr, format!("gm-review: refused - {why}\n"));
    }
    let got = run(&d, &["reviewed", "530", "3", "531"]);
    assert!(
        got.stderr.contains("TypeError: sequence item"),
        "{}",
        got.stderr
    );
    let got = run(&d, &["reviewed", "530", "0", "531"]);
    assert_eq!(
        got.stdout,
        "gm-reviewed: row 0 overturned - an open row of 531-to\n"
    );
    let got = run(&d, &["reviewed", "530", "1", "531"]);
    assert_eq!(
        got.stdout,
        "gm-reviewed: row 1 overturned - an open row of 531-to\n"
    );
    let found = written(&d, "specs/531-to/found.jsonl");
    assert_eq!(
        found[0],
        json!({"check": "gm-review", "file": "530-x", "block": "ask:a", "finding": "overturned by the GM: a why - a note", "status": "open"})
    );
    assert_eq!(found[1]["block"], json!("f"));
    assert_eq!(found[1]["finding"], json!("overturned by the GM: the fix"));
}

#[test]
fn the_closing_check_stands_before_the_gms_last_box() {
    let d = dir("gm-reviewed-close");
    put(
        &d,
        "specs/530-x/tasks.md",
        "- [x] T01\n- [ ] GM review (make gm-reviewed F=530)\n",
    );
    put(&d, "specs/531-to/x", "");
    // the GM's box the feature's last open one: the closing check is asked, its reasons refuse
    close_check(&d, "[\"530-x has no report.md\", \"another\"]", 0);
    put(
        &d,
        "specs/530-x/gm-review.jsonl",
        &jl(&[
            json!({"kind": "accepted"}),
            json!({"kind": "accepted", "reviewed": "2026-01-01"}),
        ]),
    );
    let got = run(&d, &["reviewed", "530"]);
    assert_eq!(got.stderr, "gm-review: refused - the GM's box closes the feature, and: 530-x has no report.md; another\n");
    close_check(&d, "not json", 0);
    assert!(run(&d, &["reviewed", "530"])
        .stderr
        .contains("close_check.py --reasons-json"));
    close_check(&d, "[]", 1);
    assert!(run(&d, &["reviewed", "530"])
        .stderr
        .contains("close_check.reasons raised"));
    let got = run_with(&d, &["reviewed", "530"], "", 100, "/no/such/python");
    assert!(got.stderr.contains("OSError"), "{}", got.stderr);
    close_check(&d, "[]", 0);
    let got = run_with(&d, &["reviewed", "530"], "his own words", 100, "python3");
    assert_eq!(got.stdout, "gm-reviewed: 2 row(s) of 530-x reviewed\n");
    assert_eq!(
        read(&d, "specs/530-x/tasks.md"),
        "- [x] T01\n- [x] GM review (make gm-reviewed F=530)\n"
    );
    let rs = written(&d, "specs/530-x/gm-review.jsonl");
    assert_eq!(rs[0]["gm_words"], json!("his own words"));
    assert_eq!(rs[1], json!({"kind": "accepted", "reviewed": "2026-01-01"}));
    // no tasks.md: the rows are reviewed and nothing is ticked
    let got = run(&d, &["reviewed", "531"]);
    assert_eq!(got.stdout, "gm-reviewed: 0 row(s) of 531-to reviewed\n");
    assert_eq!(read(&d, "specs/531-to/gm-review.jsonl"), "");
    put(&d, "specs/532-int/gm-review.jsonl", "7\n");
    assert!(run(&d, &["reviewed", "532"]).stderr.contains("TypeError"));
    put(&d, "specs/533-l/gm-review.jsonl", "[1]\n");
    assert!(run(&d, &["reviewed", "533"])
        .stderr
        .contains("TypeError: 'dict' object expected"));
    put(
        &d,
        "specs/534-one/gm-review.jsonl",
        &jl(&[json!({"kind": "accepted"}), json!({"kind": "accepted"})]),
    );
    let got = run(&d, &["reviewed", "534", "0", "531"]);
    assert_eq!(
        got.stdout,
        "gm-reviewed: row 0 overturned - an open row of 531-to\n"
    );
    let got = run(&d, &["reviewed", "534", "1", "531"]);
    assert_eq!(got.stdout, "gm-reviewed: row 1 overturned - an open row of 531-to\ngm-reviewed: 2 row(s) of 534-one reviewed\n");
}

#[test]
fn the_push_refuses_a_question_still_owed() {
    let d = dir("gm-owed");
    sh(
        &d,
        "git init -q -b main && git config user.email x@y && git config user.name x",
    );
    put(&d, "specs/540-a/tasks.md", "x\n");
    commit(&d, "base");
    sh(&d, "git update-ref refs/remotes/origin/main HEAD");
    let got = run(&d, &["owed-check"]);
    assert_eq!((got.code, got.stderr.as_str()), (0, ""));
    put(
        &d,
        "specs/540-a/gm-review.jsonl",
        &jl(&[
            json!({"kind": "question", "status": "owed", "question": "owed one here"}),
            json!({"kind": "question", "status": "owed", "reviewed": "x"}),
            json!({"kind": "question", "status": "kept"}),
        ]),
    );
    put(
        &d,
        "specs/541-b/gm-review.jsonl",
        &jl(&[json!({"kind": "question", "status": "owed"})]),
    );
    commit(&d, "rows");
    put(&d, "specs/542-c/sub/gm-review.jsonl", "{}\n");
    let got = run(&d, &["owed-check"]);
    assert_eq!(got.code, 1);
    assert_eq!(got.stderr, "gm-review: owed escalation-check - 540#0: owed one here\ngm-review: owed escalation-check - 541#0: \ngm-review: dispatch escalation-check on each, then make gm-escalated F=<n> ROW=<n> VERDICT=KEEP|CUT REASON=\"...\"\n");
    put(
        &d,
        "specs/zz/gm-review.jsonl",
        &jl(&[json!({"kind": "question", "status": "owed"})]),
    );
    assert_eq!(
        run(&d, &["owed-check"]).stderr,
        "gm-review: refused - invalid literal for int() with base 10: 'zz'\n"
    );
    let bare = dir("gm-owed-bare");
    put(&bare, "specs/540-a/gm-review.jsonl", "{}\n");
    assert_eq!(run(&bare, &["owed-check"]).code, 0);
    let rs = rows(&bare.join("specs/540-a")).unwrap();
    assert_eq!(rs, vec![json!({})]);
}

#[test]
fn a_broken_queue_or_ranking_fails_where_the_python_raised() {
    let d = dir("gm-broken");
    let ranking = "specs/328-match-the-research/audit";
    put(&d, &format!("{ranking}/overrides.json"), "{bad");
    assert!(run(&d, &["list"])
        .stderr
        .starts_with("gm-review: refused - key must be a string"));
    put(&d, &format!("{ranking}/overrides.json"), "[1]");
    assert!(run(&d, &["explain"]).stderr.contains("AttributeError"));
    put(&d, &format!("{ranking}/overrides.json"), "{\"a\": 1}");
    assert!(run(&d, &["list"])
        .stderr
        .contains("AttributeError: 'int' object"));
    put(
        &d,
        &format!("{ranking}/overrides.json"),
        "{\"a\": {\"flag\": \"Held behind x\"}, \"b\": {\"flag\": \"Held behind y\"}}",
    );
    put(&d, &format!("{ranking}/waves.json"), "3");
    assert!(run(&d, &["list"])
        .stderr
        .contains("TypeError: argument of type 'int'"));
    put(&d, &format!("{ranking}/waves.json"), "[\"a\"]");
    let got = run(&d, &["list"]);
    assert!(
        got.stdout.contains("* b\n") && !got.stdout.contains("* a\n"),
        "{}",
        got.stdout
    );
    // a feature with no dash in its name, a time that is no string, an agent file that is no UTF-8
    put(
        &d,
        "specs/600/gm-review.jsonl",
        &jl(&[json!({"kind": "accepted"})]),
    );
    assert!(run(&d, &["list"]).stderr.contains("IndexError"));
    put(
        &d,
        "specs/601-t/gm-review.jsonl",
        &jl(&[json!({"kind": "arbiter", "trigger": "round:bad|q:0001", "utc": 3})]),
    );
    assert!(run(&d, &["explain", "601"])
        .stderr
        .contains("TypeError: cannot slice 3"));
    put(
        &d,
        "specs/601-t/gm-review.jsonl",
        &jl(&[json!({"kind": "arbiter", "trigger": "round:bad|q:0001"})]),
    );
    std::fs::create_dir_all(d.join(".claude/agents")).unwrap();
    std::fs::write(d.join(".claude/agents/bad.md"), b"\xff").unwrap();
    assert!(run(&d, &["explain", "601"])
        .stderr
        .contains("invalid start byte"));
    put(&d, "specs/601-t/arbiter.jsonl", "[1]\n");
    assert!(run(&d, &["explain", "601"])
        .stderr
        .contains("AttributeError: 'list'"));
    put(&d, "specs/601-t/arbiter.jsonl", "{}\n{}\n");
    put(&d, "specs/602-l/gm-review.jsonl", "[2]\n");
    assert!(run(&d, &["explain", "602"])
        .stderr
        .contains("AttributeError: 'list'"));
    assert!(run(&d, &["list", "602"])
        .stderr
        .contains("AttributeError: 'list'"));
    put(
        &d,
        "specs/abc/gm-review.jsonl",
        &jl(&[json!({"kind": "accepted"})]),
    );
    assert!(run(&d, &["explain", "abc", "9"])
        .stdout
        .starts_with("gm-review: no open row 9 in abc"));
    assert!(run(&d, &["explain", "abc"])
        .stderr
        .contains("invalid literal"));
    assert!(run(&d, &["list", "abc"]).stderr.contains("invalid literal"));
}

#[test]
fn a_queue_with_no_ranking_and_nothing_for_the_gm() {
    let d = dir("gm-no-ranking");
    put(
        &d,
        "specs/610-a/gm-review.jsonl",
        &jl(&[json!({"kind": "accepted", "finding": "f", "why": "w"})]),
    );
    let got = run(&d, &["list"]);
    assert!(got.stdout.starts_with("GM REVIEW - 0 decision(s) for the GM, 0 question(s) owed escalation-check, 0 waiting on other work, 1 landed row(s) to review in 1 feature(s)\n\nTO REVIEW"), "{}", got.stdout);
    let got = run(&d, &["explain"]);
    assert_eq!(got.stdout, "WHAT NEEDS YOUR DECISION: nothing - no question kept for you and no fix declined to you\n\nThe other 1 row(s) are decisions already made that you may overturn; nothing waits on them. Each in\nfull: make gm-review F=NNN EXPLAIN=1 [ROW=n].\n");
}
