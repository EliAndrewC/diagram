//! The guard on fixture trees, never the live switch (451 T244): deferred refuses each start, open, missing and malformed are silent,
//! the escape passes with a reason and is refused bare.

use serde_json::{json, Value};

use super::judge;
use crate::protocol::{Answer, Event};
use crate::shared::session::Session;
use crate::shared::tempdir::TempDir;

fn tree(body: Option<&str>) -> TempDir {
    let dir = TempDir::new("research-switch");
    if let Some(body) = body {
        std::fs::create_dir_all(dir.path().join("dev")).unwrap();
        std::fs::write(dir.path().join("dev/switches.json"), body).unwrap();
    }
    dir
}

const DEFERRED: &str = r#"{"research": {"state": "deferred", "why": "the GM: defer all of it", "who": "E", "utc": "2026-11-25T00:00:00Z"}}"#;

fn run(dir: &TempDir, tool: &str, input: &Value) -> Vec<Answer> {
    crate::shared::log::quiet();
    let e = Event {
        name: "PreToolUse".to_owned(),
        input: json!({"tool_name": tool, "tool_input": input}),
    };
    judge(&e, &Session::from_input(&e.input), dir.path())
}

fn agent(prompt: &str) -> Value {
    json!({"subagent_type": "research-pass", "prompt": prompt})
}

fn bash(cmd: &str) -> Value {
    json!({ "command": cmd })
}

fn refused(got: &[Answer], words: &str) -> bool {
    matches!(got, [Answer::Refuse(t)] if t.contains(words))
}

#[test]
fn deferred_refuses_a_research_pass_and_a_page_session_naming_the_switch() {
    let dir = tree(Some(DEFERRED));
    let a = run(&dir, "Agent", &agent("the ford's width"));
    assert!(refused(&a, "research is DEFERRED"));
    assert!(refused(&a, "the GM: defer all of it"));
    assert!(refused(&a, "make research-open"));
    assert!(refused(&a, "in the prompt"));
    let b = run(&dir, "Bash", &bash("make page-session BRIEF=/x/brief.md"));
    assert!(refused(&b, "BLOCKED: make page-session"));
    assert!(refused(&b, "in the command"));
    // a mention is not an invocation, and another agent or target is not research
    assert!(run(&dir, "Bash", &bash("grep -n page-session Makefile")).is_empty());
    assert!(run(&dir, "Bash", &bash("make research-backlog STAGE=seat")).is_empty());
    assert!(run(
        &dir,
        "Agent",
        &json!({"subagent_type": "impl-drift", "prompt": "x"})
    )
    .is_empty());
    assert!(run(&dir, "Read", &json!({"file_path": "x"})).is_empty());
    let bare = Event {
        name: "PreToolUse".to_owned(),
        input: json!({"tool_name": "Agent"}),
    };
    assert!(judge(&bare, &Session::from_input(&bare.input), dir.path()).is_empty());
}

#[test]
fn open_missing_and_malformed_are_silent() {
    for body in [
        Some(r#"{"research": {"state": "open"}}"#),
        None,
        Some("not json"),
        Some(r#"{"research": {"state": "later"}}"#),
    ] {
        let dir = tree(body);
        assert!(run(&dir, "Agent", &agent("q")).is_empty());
        assert!(run(&dir, "Bash", &bash("make page-session BRIEF=b")).is_empty());
    }
}

#[test]
fn the_escape_passes_with_a_reason_and_is_refused_bare() {
    let dir = tree(Some(DEFERRED.replace(", \"who\": \"E\"", "").as_str()));
    assert!(run(
        &dir,
        "Agent",
        &agent("the GM's question\nRESEARCH_OK: the GM asked for this pass")
    )
    .is_empty());
    assert!(refused(
        &run(&dir, "Agent", &agent("q RESEARCH_OK")),
        "with no reason"
    ));
    assert!(run(
        &dir,
        "Bash",
        &bash("RESEARCH_OK=\"the GM asked for it\" make page-session BRIEF=b")
    )
    .is_empty());
    assert!(refused(
        &run(
            &dir,
            "Bash",
            &bash("make page-session BRIEF=b # RESEARCH_OK")
        ),
        "with no reason"
    ));
    // no who recorded reads `?`
    assert!(refused(&run(&dir, "Agent", &agent("q")), "by ?"));
}

#[test]
fn the_hook_reads_the_switch_of_the_tree_it_runs_in() {
    crate::shared::log::quiet();
    let dir = tree(Some(DEFERRED));
    std::fs::create_dir_all(dir.path().join(".git")).unwrap();
    let e = Event {
        name: "PreToolUse".to_owned(),
        input: json!({"tool_name": "Agent", "cwd": dir.path(), "tool_input": agent("q")}),
    };
    assert!(refused(
        &super::decide(&e, &Session::from_input(&e.input)),
        "research is DEFERRED"
    ));
}
