//! The three command lines over scratch ledgers and transcripts: each output, each refusal and each raise.

use std::path::Path;

use serde_json::json;

use super::super::tests::{dir, put};
use super::{cost_cli, lint_cli, raised, rows_cli};
use crate::reviews::cli;

const HEAD: &str = "## Review checks, measured (feature 294 on)\n\n| date | check | subject | verdict | finding | class | author missed? | acted on | wall | tokens |\n|---|---|---|---|---|---|---|---|---|---|\n";
const GOOD: &str = "| 2026-10-02 | glyph-check | privy | PASS | reads | nothing | - | - | 412 s | 3100k in (2900k cached) / 4.2k out |\n";

fn args(words: &[&str]) -> Vec<String> {
    words.iter().map(|w| (*w).to_owned()).collect()
}

/// One return's transcript lines: a prompt, then a call with `output` tokens `secs` seconds later.
fn turn(prompt: &str, secs: u32, output: u32) -> String {
    format!(
        "{}\n{}\n",
        json!({"timestamp": "2026-11-01T00:00:00Z", "message": {"role": "user", "content": prompt}}),
        json!({"timestamp": format!("2026-11-01T00:00:{secs:02}Z"), "requestId": prompt, "message": {"usage": {"output_tokens": output}}})
    )
}

#[test]
fn the_lint_names_each_short_row_and_reads_the_trees_ledger_by_default() {
    let d = dir("ledger-lint");
    put(&d, "dev/review-ledger.md", &format!("{HEAD}{GOOD}"));
    put(
        &d,
        "short.md",
        &format!("{HEAD}| 2026-10-02 | glyph-check | short |\n"),
    );
    let clean = lint_cli(&[], &d);
    assert_eq!((clean.code, clean.stdout.as_str()), (0, ""));
    let short = lint_cli(
        &args(&[&d.join("short.md").to_string_lossy(), "ignored"]),
        Path::new("/"),
    );
    assert_eq!(short.code, 1);
    assert!(short
        .stdout
        .starts_with("line 5: 3 cells, the table has 10"));
    let missing = lint_cli(&args(&["/no/such/ledger.md"]), &d);
    assert_eq!(missing.code, 1);
    assert!(missing.stderr.starts_with(
        "Traceback (most recent call last):\n  l7r-gate reviews ledger-lint\n/no/such/ledger.md: "
    ));
    let via = cli(&args(&[
        "ledger-lint",
        &d.join("short.md").to_string_lossy(),
    ]));
    assert_eq!(via.code, 1);
}

#[test]
fn the_rows_are_read_from_a_file_or_the_input() {
    let d = dir("ledger-rows");
    put(&d, "l.md", &format!("{HEAD}{GOOD}| short |\n"));
    let path = d.join("l.md").to_string_lossy().into_owned();
    let got = rows_cli(&args(&[&path]), &mut std::io::empty());
    let v: serde_json::Value = serde_json::from_str(&got.stdout).unwrap();
    assert_eq!(v["columns"][9], json!("tokens"));
    assert_eq!(v["rows"][1], json!([6, ["short"]]));
    let piped = rows_cli(&[], &mut format!("{HEAD}{GOOD}").as_bytes());
    assert!(piped.stdout.contains("\"rows\":[[5,"));
    assert_eq!(
        rows_cli(&args(&["/no/such"]), &mut std::io::empty()).code,
        1
    );
    assert_eq!(rows_cli(&[], &mut &[0xff_u8][..]).code, 1);
    assert_eq!(cli(&args(&["ledger-rows", &path])).code, 0);
}

#[test]
fn a_reviews_cost_is_its_transcripts_one_line_a_return() {
    let d = dir("review-cost");
    let root = d.join("projects");
    let sub = root.join("p/s/subagents");
    put(&sub, "agent-one.jsonl", &turn("go", 13, 2500));
    put(
        &sub,
        "agent-two.jsonl",
        &format!("{}{}", turn("go", 4, 100), turn("again", 9, 50)),
    );
    put(
        &sub,
        "agent-late.jsonl",
        &format!(
            "{}{}",
            turn("go", 4, 100),
            "{\"message\": {\"role\": \"user\", \"content\": \"again\"}}\n[1]\n"
        ),
    );
    put(&sub, "agent-first.jsonl", "[1]\n");
    std::fs::write(sub.join("agent-bytes.jsonl"), [0xff_u8]).unwrap();
    let r = root.to_string_lossy().into_owned();
    let run = |extra: &[&str]| cost_cli(&args(&[&["--root", &r], extra].concat()), "/home/nobody");
    assert_eq!(
        run(&["--agent", "one"]).stdout,
        "13 s | 0k in (0k cached) / 2.5k out\n"
    );
    assert_eq!(
        run(&["--agent", "two"]).stdout,
        "return 1: 4 s | 0k in (0k cached) / 0.1k out\nreturn 2: 9 s | 0k in (0k cached) / 0.1k out\n"
    );
    assert_eq!(
        run(&["--agent", "two", "--last"]).stdout,
        "9 s | 0k in (0k cached) / 0.1k out\n"
    );
    let late = run(&["--agent", "late"]);
    assert_eq!(
        (late.code, late.stdout.as_str()),
        (1, "return 1: 4 s | 0k in (0k cached) / 0.1k out\n")
    );
    assert!(late.stderr.contains("no object"));
    assert_eq!(run(&["--agent", "first"]).code, 1);
    assert_eq!(run(&["--agent", "bytes"]).code, 1);
    let none = cost_cli(&args(&["--agent", "nobody"]), "/home/nobody");
    assert_eq!(
        none.stderr,
        "_review_cost: no transcript for agent nobody under /home/nobody/.claude/projects\n"
    );
    assert_eq!(cost_cli(&args(&["--last"]), "/h").code, 2);
    assert_eq!(cost_cli(&args(&["--bogus"]), "/h").code, 2);
    assert_eq!(cli(&args(&["review-cost", "--bogus"])).code, 2);
    assert_eq!(raised("x".to_owned(), "c", "why").stdout, "x");
}

#[test]
fn the_ledger_commands_are_dispatched() {
    assert_eq!(cli(&args(&["ledger-owed", "--bogus"])).code, 2);
    assert_eq!(cli(&args(&["ledger-passes", "extra"])).code, 2);
}
