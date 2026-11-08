//! The decider over a fixture repository (`tests/hooks/test-agent-model-hooks.sh`, replayed through the shim, is the verdict).

use std::path::{Path, PathBuf};

use serde_json::{json, Value};

use super::{decide, judge};
use crate::protocol::{Answer, Event};
use crate::shared::session::Session;
use crate::shared::tool::ask;

fn world(tag: &str) -> PathBuf {
    crate::shared::log::quiet();
    let d = std::env::temp_dir().join(format!("l7r-guard-agentmodel-{tag}-{}", std::process::id()));
    let _ = std::fs::remove_dir_all(&d);
    std::fs::create_dir_all(d.join(".claude/agents")).unwrap();
    assert!(ask(
        Path::new("/"),
        "git",
        &["init", "-q", &d.to_string_lossy()],
        ""
    )
    .ok());
    std::fs::write(d.join(".claude/agents/quote-check.md"), "x").unwrap();
    d.canonicalize().unwrap()
}

fn run(tool: &str, input: &Value, at: &Path) -> Vec<Answer> {
    let e = Event {
        name: "PreToolUse".to_owned(),
        input: json!({"tool_name": tool, "cwd": at, "tool_input": input}),
    };
    judge(&e, &Session::from_input(&e.input), at)
}

fn refused(got: &[Answer], words: &str) -> bool {
    matches!(got, [Answer::Refuse(t)] if t.contains(words))
}

#[test]
fn a_dispatch_with_no_model_and_no_file_is_refused_with_the_rule() {
    let at = world("refuse");
    let got = run("Agent", &json!({"subagent_type": "Explore"}), &at);
    assert!(refused(&got, "this `Explore` agent names no model"));
    assert!(refused(&got, "for anything that judges"));
    assert!(refused(&run("Agent", &json!({}), &at), "`general-purpose`"));
    assert!(refused(
        &run(
            "Agent",
            &json!({"subagent_type": "general-purpose", "model": ""}),
            &at
        ),
        "no model"
    ));
}

#[test]
fn a_named_model_a_pinned_type_a_fork_or_another_tool_passes() {
    let at = world("pass");
    assert!(run(
        "Agent",
        &json!({"subagent_type": "general-purpose", "model": "sonnet"}),
        &at
    )
    .is_empty());
    assert!(run("Agent", &json!({"subagent_type": "quote-check"}), &at).is_empty());
    assert!(run("Agent", &json!({"subagent_type": "fork"}), &at).is_empty());
    assert!(run("Bash", &json!({"command": "make done"}), &at).is_empty());
}

#[test]
fn outside_a_repository_the_trees_scripts_are_asked() {
    let at = world("tree");
    let e = Event {
        name: "PreToolUse".to_owned(),
        input: json!({"tool_name": "Agent", "cwd": "/no/such/place", "tool_input": {"subagent_type": "quote-check"}}),
    };
    let s = Session::from_input(&e.input);
    assert!(refused(&judge(&e, &s, &at), "quote-check"));
    std::fs::create_dir_all(at.join("scripts/.claude/agents")).unwrap();
    std::fs::write(at.join("scripts/.claude/agents/quote-check.md"), "x").unwrap();
    assert!(judge(&e, &s, &at).is_empty());
    let bash = Event {
        name: "PreToolUse".to_owned(),
        input: json!({"tool_name": "Bash"}),
    };
    assert!(decide(&bash, &Session::from_input(&bash.input)).is_empty());
}

#[test]
fn the_sessions_clone_says_what_is_pinned() {
    let at = world("clone");
    let mine = at.join(".clones/mine/.claude/agents");
    std::fs::create_dir_all(&mine).unwrap();
    std::fs::write(mine.join("only-here.md"), "x").unwrap();
    std::fs::create_dir_all(at.join(".clones/.session-clones")).unwrap();
    std::fs::write(
        at.join(".clones/.session-clones/s-am"),
        at.join(".clones/mine").to_string_lossy().as_bytes(),
    )
    .unwrap();
    let e = Event {
        name: "PreToolUse".to_owned(),
        input: json!({"tool_name": "Agent", "session_id": "s-am", "cwd": at, "tool_input": {"subagent_type": "only-here"}}),
    };
    let main = at.to_string_lossy().into_owned();
    let session = Session::with_env(&e.input, |k| (k == "CLONE_MAIN").then(|| main.clone()));
    assert!(judge(&e, &session, &at).is_empty());
}
