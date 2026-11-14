//! `make lines` and `make append` over scratch files: where FILE resolves, what is shown and appended, and every refusal.

use std::collections::HashMap;
use std::path::Path;

use serde_json::json;

use super::{agent_cells, append, cli, ledger_row_problems, lines, resolve, with_cost, Env};

fn args(words: &[&str]) -> Vec<String> {
    words.iter().map(|w| (*w).to_owned()).collect()
}

const GOOD: &str = "| 2026-10-02 | glyph-check | privy | PASS | reads | nothing | - | - | 412 s | 3100k in (2900k cached) / 4.2k out |";

#[test]
fn a_relative_file_is_taken_from_where_make_ran_else_the_repository() {
    let d = l7r_gate_core::ci::fixtures::scratch("coord-resolve");
    l7r_gate_core::record::testkit::git(&d, &["init", "-q"]);
    let top = std::fs::canonicalize(&*d).unwrap();
    std::fs::create_dir_all(top.join("sub/inner")).unwrap();
    std::fs::write(top.join("here.md"), "").unwrap();
    let sub = top.join("sub");
    assert_eq!(resolve("/abs/x.md", &sub), Path::new("/abs/x.md"));
    assert_eq!(resolve("inner/new.md", &sub), sub.join("inner/new.md"));
    assert_eq!(resolve("./here.md", &top), top.join("here.md"));
    assert_eq!(resolve("specs/x/new.md", &sub), top.join("specs/x/new.md"));
    let none = Path::new("/no/such/dir");
    assert_eq!(resolve("a/b.md", none), none.join("a/b.md"));
}

#[test]
fn lines_shows_at_most_eighty_and_says_how_many() {
    let d = l7r_gate_core::ci::fixtures::scratch("coord-lines");
    let f = d.join("h.md");
    let mut body: String = (1..=90)
        .flat_map(|n| ["- 269 line ".to_owned(), n.to_string(), "\r\n".to_owned()])
        .collect();
    body += "other\x1cend";
    std::fs::write(&f, body).unwrap();
    let got = lines(&f, "^- 269").unwrap();
    assert_eq!(got.len(), 82);
    assert_eq!(got[0], "1: - 269 line 1");
    assert_eq!(got[80], "(80 of 92 lines shown)");
    assert_eq!(got[81], "(10 more matched - narrow KEY)");
    assert_eq!(
        lines(&f, "^end").unwrap(),
        ["92: end", "(1 of 92 lines shown)"]
    );
    assert!(lines(&f, "(").unwrap_err().is_err());
    // Python's `\Z` is the end of the text; an escaped backslash before a Z is a backslash; a lone one at the end no pattern
    assert_eq!(
        lines(&f, r"end\Z").unwrap(),
        ["92: end", "(1 of 92 lines shown)"]
    );
    assert_eq!(lines(&f, r"\\Z").unwrap(), ["(0 of 92 lines shown)"]);
    assert!(lines(&f, "end\\").unwrap_err().is_err());
    assert!(lines(&d.join("none"), "x").unwrap_err().is_ok());
}

#[test]
fn append_writes_one_line_and_a_newline_only_where_owed() {
    let d = l7r_gate_core::ci::fixtures::scratch("coord-append");
    let f = d.join("new/dir/c.md");
    append(&f, "one\n").unwrap();
    append(&f, "two").unwrap();
    std::fs::write(d.join("open.md"), "no newline").unwrap();
    append(&d.join("open.md"), "three").unwrap();
    std::fs::write(d.join("empty.md"), "").unwrap();
    append(&d.join("empty.md"), "four").unwrap();
    assert_eq!(std::fs::read_to_string(&f).unwrap(), "one\ntwo\n");
    assert_eq!(
        std::fs::read_to_string(d.join("open.md")).unwrap(),
        "no newline\nthree\n"
    );
    assert_eq!(
        std::fs::read_to_string(d.join("empty.md")).unwrap(),
        "four\n"
    );
    std::fs::write(d.join("file"), "").unwrap();
    assert!(append(&d.join("file/x.md"), "x").is_err());
}

#[test]
fn a_ledger_row_is_linted_and_closed_with_its_cost() {
    let ledger = Path::new("/r/dev/review-ledger.md");
    assert!(ledger_row_problems(ledger, GOOD).is_empty());
    let bad = ledger_row_problems(ledger, "| 2026-10-02 | glyph-check | privy |");
    assert_eq!(bad.len(), 1);
    assert!(bad[0].starts_with("3 cells, the table has 10"), "{bad:?}");
    assert!(ledger_row_problems(Path::new("/r/other/review-ledger.md"), "| x |").is_empty());
    assert!(ledger_row_problems(Path::new("/r/dev/other.md"), "| x |").is_empty());
    assert_eq!(with_cost("| a | b |  ", "1 s | 2k"), "| a | b | 1 s | 2k |");
    assert_eq!(with_cost("| a | b", "1 s | 2k"), "| a | b | 1 s | 2k |");
    let d = l7r_gate_core::ci::fixtures::scratch("coord-cost");
    let home = d.to_string_lossy().into_owned();
    assert_eq!(
        agent_cells("nobody", &home).unwrap_err(),
        format!("_review_cost: no transcript for agent nobody under {home}/.claude/projects")
    );
    let sub = d.join(".claude/projects/p/s/subagents");
    std::fs::create_dir_all(&sub).unwrap();
    let turn = format!(
        "{}\n{}\n",
        json!({"timestamp": "2026-11-01T00:00:00Z", "message": {"role": "user", "content": "go"}}),
        json!({"timestamp": "2026-11-01T00:00:13Z", "requestId": "go", "message": {"usage": {"output_tokens": 2500}}})
    );
    std::fs::write(sub.join("agent-one.jsonl"), turn).unwrap();
    assert_eq!(
        agent_cells("one", &home).unwrap(),
        "13 s | 0k in (0k cached) / 2.5k out"
    );
}

#[test]
fn the_command_reads_its_line_from_the_environment_and_refuses_by_exit_two() {
    let d = l7r_gate_core::ci::fixtures::scratch("coord-cli");
    let cwd = std::fs::canonicalize(&*d).unwrap();
    std::fs::write(cwd.join("c.md"), "a\nb\n").unwrap();
    std::fs::create_dir_all(cwd.join("dev")).unwrap();
    let home = cwd.to_string_lossy().into_owned();
    let run = |a: &[&str], vars: &[(&str, &str)]| {
        let map: HashMap<String, String> = vars
            .iter()
            .map(|(k, v)| ((*k).to_owned(), (*v).to_owned()))
            .collect();
        let var = |k: &str| map.get(k).cloned();
        cli(
            &args(a),
            &Env {
                cwd: cwd.clone(),
                var: &var,
            },
        )
    };
    assert_eq!(run(&["lines"], &[]).code, 2);
    let got = run(&["lines", "c.md", "b"], &[]);
    assert_eq!(
        (got.code, got.stdout.as_str()),
        (0, "2: b\n(1 of 2 lines shown)\n")
    );
    assert!(run(&["lines", "no.md", "b"], &[])
        .stderr
        .starts_with("make lines: no file "));
    assert!(run(&["lines", "c.md", "("], &[])
        .stderr
        .starts_with("make lines: KEY is not a regular expression - "));
    std::fs::write(cwd.join("bad.md"), "x").unwrap();
    {
        use std::os::unix::fs::PermissionsExt as _;
        std::fs::set_permissions(cwd.join("bad.md"), std::fs::Permissions::from_mode(0o000))
            .unwrap();
    }
    assert_eq!(run(&["lines", "bad.md", "x"], &[]).code, 1);
    let refused = "make append: LINE=<text> is required, and it is ONE line\n";
    assert_eq!(run(&["append", "c.md"], &[]).stderr, refused);
    assert_eq!(run(&["append", "c.md"], &[("LINE", " ")]).stderr, refused);
    assert_eq!(
        run(&["append", "c.md"], &[("LINE", "a\nb")]).stderr,
        refused
    );
    let ok = run(
        &["append", "c.md"],
        &[("LINE", "c \"$x\"\n"), ("AGENT", "")],
    );
    assert_eq!(ok.stdout, format!("appended to {home}/c.md\n"));
    assert_eq!(
        std::fs::read_to_string(cwd.join("c.md")).unwrap(),
        "a\nb\nc \"$x\"\n"
    );
    let agent = run(
        &["append", "dev/review-ledger.md"],
        &[("LINE", "| x |"), ("AGENT", "none"), ("HOME", &home)],
    );
    assert_eq!(agent.code, 2);
    assert!(agent
        .stderr
        .starts_with("make append: AGENT=none - _review_cost: no transcript"));
    let sub = cwd.join(".claude/projects/p/s/subagents");
    std::fs::create_dir_all(&sub).unwrap();
    let turn = format!(
        "{}\n{}\n",
        json!({"timestamp": "2026-11-01T00:00:00Z", "message": {"role": "user", "content": "go"}}),
        json!({"timestamp": "2026-11-01T00:00:09Z", "requestId": "go", "message": {"usage": {"output_tokens": 100}}})
    );
    std::fs::write(sub.join("agent-a1.jsonl"), turn).unwrap();
    let row = "| 2026-10-02 | glyph-check | privy | PASS | reads | nothing | - | - |";
    let closed = run(
        &["append", "dev/review-ledger.md"],
        &[("LINE", row), ("AGENT", "a1"), ("HOME", &home)],
    );
    assert_eq!(closed.code, 0, "{}", closed.stderr);
    assert_eq!(
        std::fs::read_to_string(cwd.join("dev/review-ledger.md")).unwrap(),
        format!("{row} 9 s | 0k in (0k cached) / 0.1k out |\n")
    );
    let lint = run(
        &["append", "dev/review-ledger.md"],
        &[("LINE", "| short |")],
    );
    assert!(lint
        .stderr
        .starts_with("make append: the ledger row was NOT appended - 1 cells"));
    std::fs::write(cwd.join("file"), "").unwrap();
    assert_eq!(run(&["append", "file/x.md"], &[("LINE", "x")]).code, 1);
}
