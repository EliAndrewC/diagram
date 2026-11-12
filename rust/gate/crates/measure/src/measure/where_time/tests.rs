//! The per-task tables over the scratch feature, by start and by tick, and the command line.

use std::collections::HashMap;
use std::fmt::Write as _;
use std::path::Path;

use serde_json::{json, Value};

use super::super::feature_report::tests::{put, tree};
use super::*;

fn evs(list: &[Value]) -> Vec<Event> {
    list.iter()
        .map(|v| v.as_object().unwrap().clone())
        .collect()
}

fn at(hms: &str) -> String {
    format!("2026-11-01T{hms}Z")
}

#[test]
fn categories_go_to_buckets_and_gaps_to_tasks() {
    for (cat, want) in [
        ("thinking", "model"),
        ("waiting: quote-check", "record/modal checks"),
        ("dispatching: review check", "record/modal checks"),
        ("dispatching: record check", "record/modal checks"),
        ("waiting: general-purpose", "other subagent"),
        ("dispatching: other subagent", "other subagent"),
        ("edit", "tools"),
    ] {
        assert_eq!(bucket(cat), want, "{cat}");
    }
    let starts = [(1.0, "T01".to_owned()), (5.0, "T02".to_owned())];
    assert_eq!(task_at(&starts, 0.5), "-");
    assert_eq!(task_at(&starts, 5.0), "T02");
    let p = named_pattern("901");
    for (text, want) in [
        ("make tick T=T05", "T05"),
        ("git commit -m '901 T07: x'", "T07"),
        ("plan-bundle-T08 and ## T08 -", "T08"),
        ("task T09, TASK=T10", ""),
        ("T=T5", ""),
    ] {
        assert_eq!(named_task(text, &p), want, "{text}");
    }
    assert_eq!(named_task("plan-x-T11", &named_pattern("")), "T11");
}

#[test]
fn the_tables_book_turns_windows_and_agents() {
    let e = evs(&[
        json!({"t": at("08:00:00"), "sid": "s", "ev": "UserPromptSubmit"}),
        json!({"t": at("08:00:10"), "sid": "s", "ev": "PreToolUse", "tool": "Bash", "id": "b1", "cat": "gate"}),
        json!({"t": at("08:00:20"), "sid": "s", "ev": "PostToolUse", "tool": "Bash", "id": "b1"}),
        json!({"t": at("08:00:20"), "sid": "s", "ev": "PreToolUse", "tool": "Bash", "id": "b2"}),
        json!({"t": at("08:00:30"), "sid": "s", "ev": "Stop"}),
        json!({"t": at("08:00:40"), "sid": "s", "ev": "UserPromptSubmit", "gm": false}),
        json!({"t": at("08:00:50"), "sid": "s", "ev": "Stop"}),
        json!({"t": at("10:00:00"), "sid": "s", "ev": "UserPromptSubmit"}),
        json!({"t": at("10:00:10"), "sid": "s", "ev": "Stop"}),
        json!({"t": at("10:00:20"), "sid": "s", "ev": "UserPromptSubmit"}),
        json!({"t": at("10:00:30"), "sid": "s", "ev": "PreToolUse", "tool": "Agent", "id": "g", "agent": "spec-fidelity"}),
        json!({"t": at("10:00:31"), "sid": "s", "ev": "SubagentStart", "aid": "f", "agent": "spec-fidelity"}),
        json!({"t": at("10:00:35"), "sid": "s", "ev": "SubagentStart", "aid": "n"}),
        json!({"t": at("10:05:00"), "sid": "s", "ev": "SubagentStop", "aid": "f"}),
        json!({"t": at("10:05:01"), "sid": "s", "ev": "PostToolUse", "tool": "Agent", "id": "g", "aid": "f"}),
        json!({"t": at("10:05:02"), "sid": "s", "ev": "SubagentStop", "aid": "never"}),
        json!({"t": at("12:00:00"), "sid": "s", "ev": "Stop"}),
        json!({"t": at("12:00:01"), "sid": "s", "ev": "SubagentStop", "aid": "n"}),
    ]);
    let starts = [(0.0, "T01".to_owned())];
    let inputs = HashMap::from([("b1".to_owned(), "\"make done T=T02\"".to_owned())]);
    let t = tables(&e, &starts, Some(&inputs), "901").unwrap();
    let text = render(
        &t,
        &[
            "-".to_owned(),
            "T01".to_owned(),
            "T02".to_owned(),
            "T09".to_owned(),
        ],
    );
    assert!(text.contains("| T02 | "), "{text}");
    assert!(text.contains("| all | "), "{text}");
    assert!(text.contains("spec-fidelity 1, ? 1"), "{text}");
    assert_eq!(t.rules.items().len(), 3);
    let none = tables(&e, &starts, None, "").unwrap();
    assert_eq!(none.rules.items().len(), 1);
    for bad in [
        json!([{"t": "x", "ev": "Stop"}]),
        json!([{"t": at("08:00:00"), "sid": "s"}, {"t": at("08:00:01"), "sid": "s", "ev": "Stop"}]),
        json!([{"t": at("08:00:00"), "sid": "s", "ev": "Stop"}, {"t": at("08:00:01"), "sid": "s"}]),
        json!([{"t": at("08:00:00"), "ev": "SubagentStop", "aid": "a"}, {"t": "x", "ev": "PreToolUse", "tool": "Agent"}]),
    ] {
        assert!(tables(&evs(bad.as_array().unwrap()), &starts, None, "").is_err());
    }
}

#[test]
fn ticks_make_windows() {
    let log = "@@2026-11-01T08:00:00+00:00\n+- [x] T01 a\n+- [x] T02 b\n@@2026-11-01T09:00:00Z\n+- [x] T01 again\n+- [x] T03\n@@ -1 +1 @@\n";
    let ticks = parse_ticks(log).unwrap();
    assert_eq!(ticks.len(), 3);
    assert!(parse_ticks("@@2026-13-01T08:00:00\n").is_err());
    assert_eq!(parse_ticks("+- [x] T01\n").unwrap(), Vec::new());
    let wins = tick_windows(&ticks, 0.0);
    assert_eq!(
        wins.iter().map(|w| w.2.as_str()).collect::<Vec<_>>(),
        ["T01+T02", "T03"]
    );
    assert_eq!(tick_windows(&ticks, wins[1].0 + 1.0).len(), 1);
}

#[test]
fn a_transcript_names_each_calls_input() {
    let home = crate::checks::scratch("measure-where-inputs");
    let line = |v: Value| v.to_string();
    put(
        &home,
        "p/s1.jsonl",
        &[
            line(json!({"message": {"content": [{"type": "tool_use", "id": "a", "input": {"x": "caf\u{e9}", "n": 1.5}}, 5]}})),
            line(json!({"message": {"content": "a tool_use string"}, "k": "tool_use"})),
            line(json!({"message": null, "k": "tool_use"})),
            "\"tool_use\" not json".to_owned(),
            line(json!({"no": "x"})),
        ]
        .join("\n"),
    );
    let got = transcript_inputs(&["s1".to_owned(), "s2".to_owned()], &home).unwrap();
    assert_eq!(got["a"], "{\"x\": \"caf\\u00e9\", \"n\": 1.5}");
    for bad in [
        "[\"tool_use\"]",
        r#"{"message": "x", "k": "tool_use"}"#,
        r#"{"message": {"content": 5}, "k": "tool_use"}"#,
        r#"{"message": {"content": true}, "k": "tool_use"}"#,
    ] {
        put(&home, "p/s3.jsonl", bad);
        assert!(transcript_inputs(&["s3".to_owned()], &home).is_err());
    }
    put(
        &home,
        "p/s3.jsonl",
        r#"{"message": {"content": 0}, "k": "tool_use"}"#,
    );
    assert!(transcript_inputs(&["s3".to_owned()], &home)
        .unwrap()
        .is_empty());
}

fn args(list: &[&str]) -> Vec<String> {
    list.iter().map(|s| (*s).to_owned()).collect()
}

#[test]
#[expect(
    clippy::too_many_lines,
    reason = "one scratch feature through every form of the command line"
)]
fn the_command_line_books_by_start_or_by_tick() {
    let d = tree("measure-where-cli");
    let root = d.display().to_string();
    let projects = d.join("home");
    let none = Path::new("/nonexistent");
    assert_eq!(cli(&[], &projects, none).code, 2);
    assert_eq!(cli(&args(&["901", "--nope"]), &projects, none).code, 2);
    let missing = cli(&args(&["903", "--root", &root]), &projects, none);
    assert_eq!(
        (missing.code, missing.stderr.as_str()),
        (2, "where-time: no specs/903-* directory\n")
    );
    assert_eq!(cli(&args(&["x", "--root", &root]), &projects, none).code, 1);
    let log = d.join(".git/l7r-events/901-s.jsonl");
    let mut text = std::fs::read_to_string(&log).unwrap();
    let _ = write!(
        text,
        "{}\n{}\n",
        json!({"t": at("07:00:00"), "sid": "z", "ev": "SubagentStart", "aid": "zz", "agent": "k"}),
        json!({"t": at("07:00:00"), "sid": "z", "ev": "SubagentStop", "aid": "zz"})
    );
    std::fs::write(&log, text).unwrap();
    let by_start = cli(&args(&["901", "--root", &root]), &projects, none);
    assert_eq!(by_start.code, 0);
    assert!(
        by_start.stdout.contains("\nbooked by: "),
        "{}",
        by_start.stdout
    );
    let since = cli(
        &args(&["901", "--root", &root, "--since", "2026-11-01T08:10:00Z"]),
        &projects,
        none,
    );
    assert_eq!(since.code, 0);
    let by_tick = cli(
        &args(&["901", "--root", &root, "--by-tick"]),
        &projects,
        none,
    );
    assert!(
        by_tick
            .stdout
            .contains("| window | from (UTC) | to (UTC) | wall minutes |"),
        "{}",
        by_tick.stdout
    );
    assert_eq!(
        cli(
            &args(&[
                "901",
                "--root",
                &root,
                "--by-tick",
                "--since",
                "2026-11-01T08:00:00Z"
            ]),
            &projects,
            none
        )
        .code,
        0
    );
    put(
        &d,
        ".git/task-starts.jsonl",
        &format!(
            "{}\n{}\n",
            json!({"feature": "901-s", "task": 5, "utc": at("08:00:00")}),
            json!({"feature": "x"})
        ),
    );
    assert_eq!(
        cli(&args(&["901", "--root", &root]), &projects, none).code,
        0
    );
    for bad in ["{", "[1]", r#"{"feature": "901-s", "task": "T1"}"#] {
        put(&d, ".git/task-starts.jsonl", bad);
        assert_eq!(
            cli(&args(&["901", "--root", &root]), &projects, none).code,
            1
        );
    }
    put(
        &d,
        ".git/task-starts.jsonl",
        r#"{"feature": "901-s", "task": "T1", "utc": 5}"#,
    );
    assert_eq!(
        cli(
            &args(&["901", "--root", &root, "--since", "2026"]),
            &projects,
            none
        )
        .code,
        1
    );
    // outside any repository the root is taken as given, and there are no starts
    let bare = crate::checks::scratch("measure-where-bare");
    std::fs::create_dir_all(bare.join("specs/901-s")).unwrap();
    assert_eq!(
        cli(
            &args(&["901", "--root", &bare.display().to_string()]),
            &projects,
            none
        )
        .code,
        0
    );
}
