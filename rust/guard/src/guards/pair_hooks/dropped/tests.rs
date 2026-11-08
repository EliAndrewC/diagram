//! The dropped-dispatch rule over a fixture transcript and clone; `tests/hooks/test-pair-hooks.sh` drives it through the Stop event.

use std::path::{Path, PathBuf};
use std::process::Command;

use serde_json::{json, Value};

use super::{calls, cli, key_of, refusal_for, rows_of};

fn clone(tag: &str) -> PathBuf {
    let dir = std::env::temp_dir().join(format!("l7r-guard-dropped-{tag}-{}", std::process::id()));
    let _ = std::fs::remove_dir_all(&dir);
    std::fs::create_dir_all(&dir).unwrap();
    assert!(Command::new("git")
        .arg("-C")
        .arg(&dir)
        .args(["init", "-q"])
        .status()
        .unwrap()
        .success());
    dir
}

fn agent(t: &str, id: &str, kind: &str, prompt: &str) -> Value {
    json!({"timestamp": t, "message": {"content": [{"type": "tool_use", "name": "Agent", "id": id, "input": {"subagent_type": kind, "prompt": prompt, "description": "d"}}]}})
}

fn refused(id: &str) -> Value {
    json!({"message": {"content": [{"type": "tool_result", "tool_use_id": id, "is_error": true, "content": "PreToolUse:Agent hook error: x\nBLOCKED: not decided\nmore"}]}})
}

fn turn_end(t: &str) -> Value {
    json!({"type": "system", "subtype": "turn_duration", "timestamp": t})
}

fn transcript(dir: &Path, rows: &[Value]) -> Value {
    let path = dir.join("t.jsonl");
    let body: Vec<String> = rows
        .iter()
        .map(Value::to_string)
        .chain(["not json".to_owned()])
        .collect();
    std::fs::write(&path, body.join("\n")).unwrap();
    json!({"transcript_path": path})
}

const BUN: &str = "read /tmp/l7r-check/b/MANIFEST.md";

#[test]
fn a_refused_dispatch_blocks_until_sent_again() {
    let dir = clone("resent");
    let first = [
        turn_end("1"),
        agent("2", "a", "impl-drift", BUN),
        refused("a"),
    ];
    let why = refusal_for(&dir, &transcript(&dir, &first)).unwrap();
    assert!(why.starts_with("BLOCKED: 1 dispatch(es)"));
    assert!(why.contains("impl-drift on /tmp/l7r-check/b/MANIFEST.md - refused: not decided"));
    assert!(why
        .contains("make dispatch-dropped TYPE=impl-drift BUNDLE=\"/tmp/l7r-check/b/MANIFEST.md\""));
    let mut sent = first.to_vec();
    sent.push(agent("3", "b", "impl-drift", BUN));
    assert_eq!(refusal_for(&dir, &transcript(&dir, &sent)), None);
}

#[test]
fn an_earlier_turns_refusal_and_a_twin_count_once_or_not_at_all() {
    let dir = clone("window");
    let old = [agent("2", "a", "x", BUN), refused("a"), turn_end("3")];
    assert_eq!(refusal_for(&dir, &transcript(&dir, &old)), None);
    let twins = [
        agent("2", "a", "x", BUN),
        refused("a"),
        agent("3", "b", "x", BUN),
        refused("b"),
    ];
    assert!(refusal_for(&dir, &transcript(&dir, &twins))
        .unwrap()
        .starts_with("BLOCKED: 1 "));
    let no_session_end = [agent("2", "a", "x", "no bundle here"), refused("a")];
    assert!(refusal_for(&dir, &transcript(&dir, &no_session_end))
        .unwrap()
        .contains("x on d"));
}

#[test]
fn a_recorded_drop_answers_it_and_needs_a_reason() {
    let dir = clone("drop");
    let rows = [agent("2", "a", "x", BUN), refused("a")];
    let payload = transcript(&dir, &rows);
    let args = |why: &str| {
        [
            "drop",
            "--root",
            dir.to_str().unwrap(),
            "--type",
            "x",
            "--bundle",
            "/tmp/l7r-check/b/MANIFEST.md",
            "--why",
            why,
        ]
        .map(str::to_owned)
    };
    assert_eq!(cli(&args("short")).code, 2);
    assert!(refusal_for(&dir, &payload).is_some());
    let done = cli(&args("the round was folded"));
    assert_eq!(done.code, 0);
    assert!(done.stdout.contains("recorded - the round was folded"));
    assert_eq!(refusal_for(&dir, &payload), None);
    assert_eq!(cli(&["bogus".to_owned()]).code, 2);
    assert_eq!(
        cli(&["drop".to_owned(), "--why".to_owned(), "x".to_owned()]).code,
        2
    );
}

#[test]
fn what_it_cannot_read_passes() {
    let dir = clone("unread");
    assert_eq!(
        refusal_for(&dir, &json!({"transcript_path": "/no/such"})),
        None
    );
    assert_eq!(refusal_for(&dir, &json!({})), None);
    assert!(rows_of(&dir.join("absent")).is_empty());
    assert_eq!(key_of(&json!({"prompt": "x", "description": "y"})), "y");
    let not_refused = [
        json!({"message": {"content": [{"type": "tool_result", "tool_use_id": "a", "is_error": true, "content": [{"text": "other"}]}]}}),
    ];
    assert!(calls(&not_refused).is_empty());
    let other_error = [
        agent("2", "a", "x", BUN),
        json!({"message": {"content": [{"type": "tool_result", "tool_use_id": "a", "is_error": true, "content": [{"text": "other"}]}]}}),
    ];
    assert!(!calls(&other_error)[0].refused);
    let no_block = [
        agent("2", "a", "x", BUN),
        json!({"message": {"content": [{"type": "tool_result", "tool_use_id": "a", "is_error": true, "content": "PreToolUse:Agent hook error"}]}}),
    ];
    assert_eq!(calls(&no_block)[0].why, "");
    assert!(refusal_for(&dir, &transcript(&dir, &no_block))
        .unwrap()
        .contains("x on /tmp/l7r-check/b/MANIFEST.md\n"));
    assert!(calls(&[json!({"message": {"content": [{"type": "text"}]}})]).is_empty());
    let not_list = [json!({"message": {"content": "text"}})];
    assert!(calls(&not_list).is_empty());
}

#[test]
fn a_directory_that_is_no_repository_still_answers() {
    let dir = std::env::temp_dir().join(format!("l7r-guard-dropped-plain-{}", std::process::id()));
    std::fs::create_dir_all(&dir).unwrap();
    assert_eq!(super::gitdir(&dir), dir.join(".git"));
}
