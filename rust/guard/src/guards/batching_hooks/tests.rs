//! The guard on a clock of its own (`tests/hooks/test-batching-hooks.sh`, replayed through the shim, is the verdict).

use std::path::Path;

use serde_json::{json, Value};

use super::{decide, judge, Config};
use crate::protocol::{Answer, Event};
use crate::shared::session::Session;

fn dir(tag: &str) -> crate::shared::tempdir::TempDir {
    crate::shared::log::quiet();
    let d = crate::shared::tempdir::TempDir::new(&format!("guard-batching-{tag}"));
    d
}

fn config(d: &Path, now_ms: u64) -> Config {
    let path = d.to_string_lossy().into_owned();
    Config::from_env(&|k| (k == "BATCH_STATE_DIR").then(|| path.clone()), now_ms)
}

fn fire(d: &Path, name: &str, input: &Value, at: u64) -> Vec<Answer> {
    let e = Event {
        name: name.to_owned(),
        input: input.clone(),
    };
    judge(&e, &Session::from_input(&e.input), &config(d, at))
}

fn read() -> Value {
    json!({"session_id": "s", "tool_name": "Read", "tool_input": {"file_path": "/a.md"}})
}

/// A serial turn at `at`: a pre, then a post a moment later.
fn turn(d: &Path, input: &Value, at: u64) -> Vec<Answer> {
    let got = fire(d, "PreToolUse", input, at);
    fire(d, "PostToolUse", input, at + 5);
    got
}

fn history(d: &Path) -> String {
    let said = format!("{:?}", fire(d, "status", &read(), 0));
    said.split_whitespace()
        .find_map(|w| w.strip_prefix("history="))
        .unwrap_or("")
        .to_owned()
}

fn refused(got: &[Answer]) -> bool {
    matches!(got, [Answer::Refuse(t)] if t.contains("BLOCKED (batching)"))
}

fn noticed(got: &[Answer]) -> bool {
    matches!(got, [Answer::Notice(t)] if t.contains("BATCHING NOTICE"))
}

#[test]
fn a_run_of_bare_reads_is_noticed_then_refused_and_the_window_clears() {
    let d = dir("run");
    assert!(turn(&d, &read(), 10_000).is_empty());
    assert!(turn(&d, &read(), 20_000).is_empty());
    assert!(noticed(&turn(&d, &read(), 30_000)));
    assert_eq!(history(&d), "111");
    assert!(refused(&fire(&d, "PreToolUse", &read(), 40_000)));
    assert_eq!(history(&d), "");
}

#[test]
fn what_is_not_a_bare_read_does_not_count() {
    let d = dir("shapes");
    let bash =
        |cmd: &str| json!({"session_id": "s", "tool_name": "Bash", "tool_input": {"command": cmd}});
    turn(
        &d,
        &json!({"session_id": "s", "tool_name": "Read", "tool_input": {"file_path": "/x/CROP.PNG"}}),
        10_000,
    );
    turn(&d, &bash("grep a b; grep c d"), 20_000);
    turn(
        &d,
        &json!({"session_id": "s", "tool_name": "Edit", "tool_input": {"file_path": "x"}}),
        30_000,
    );
    turn(
        &d,
        &json!({"session_id": "s", "tool_name": "Bash", "tool_input": {"command": "ls", "run_in_background": true}}),
        40_000,
    );
    assert_eq!(history(&d), "0000");
    turn(&d, &bash("grep a b"), 50_000);
    turn(&d, &json!({"session_id": "s", "tool_name": "Grep"}), 60_000);
    turn(&d, &json!({"session_id": "s", "tool_name": "Glob"}), 70_000);
    assert_eq!(history(&d), "000111");
}

#[test]
fn a_batched_or_a_slow_turn_is_one_zero() {
    let d = dir("batched");
    fire(&d, "PreToolUse", &read(), 10_000);
    fire(&d, "PreToolUse", &read(), 10_100);
    fire(&d, "PostToolUse", &read(), 10_150);
    fire(&d, "PostToolUse", &read(), 10_200);
    assert_eq!(history(&d), "0");
    fire(&d, "PreToolUse", &read(), 20_000);
    fire(&d, "PostToolUse", &read(), 25_000);
    assert_eq!(history(&d), "00");
}

#[test]
fn the_bar_doubles_after_a_refusal_and_decays_as_turns_batch() {
    let d = dir("backoff");
    for i in 1..=4 {
        turn(&d, &read(), i * 10_000);
    }
    let state = d.join("s.state3");
    assert!(std::fs::read_to_string(&state).unwrap().contains(" 6 "));
    fire(&d, "PreToolUse", &read(), 50_000);
    fire(&d, "PostToolUse", &read(), 58_000);
    assert!(std::fs::read_to_string(&state).unwrap().contains(" 5 "));
}

#[test]
fn the_window_keeps_its_length_and_a_stray_state_is_harmless() {
    let d = dir("window");
    for i in 1..=9 {
        let input =
            json!({"session_id": "s", "tool_name": "Bash", "tool_input": {"command": "make x"}});
        turn(&d, &input, i * 10_000);
    }
    assert_eq!(history(&d), "000000");
    std::fs::write(d.join("s.state3"), "x y z 1a0b\n").unwrap();
    assert_eq!(history(&d), "10");
    std::fs::write(d.join("s.state3"), "5 1 1 111\n").unwrap();
    assert!(refused(&fire(&d, "PreToolUse", &read(), 20_000)));
}

#[test]
fn the_state_directory_has_a_default() {
    assert_eq!(
        Config::from_env(&|_| None, 0).dir,
        Path::new("/tmp/claude-batching")
    );
}

#[test]
fn each_session_keeps_its_own_window() {
    let d = dir("sessions");
    turn(&d, &read(), 10_000);
    let other = json!({"tool_name": "Read"});
    let e = Event {
        name: "status".to_owned(),
        input: other.clone(),
    };
    let got = judge(&e, &Session::from_input(&e.input), &config(&d, 0));
    assert!(
        matches!(&got[..], [Answer::Print(t)] if t.contains("tool=Read history= ") && t.contains("nosession.state3"))
    );
    let bare = Event {
        name: "status".to_owned(),
        input: json!({"session_id": "a/b"}),
    };
    let got = judge(&bare, &Session::from_input(&bare.input), &config(&d, 0));
    assert!(
        matches!(&got[..], [Answer::Print(t)] if t.contains("tool=unknown") && t.contains("a_b.state3"))
    );
    std::env::set_var("BATCH_THRESHOLD", "3");
    std::env::set_var("BATCH_STATE_DIR", d.join("real"));
    let real = Event {
        name: "status".to_owned(),
        input: json!({}),
    };
    assert_eq!(decide(&real, &Session::from_input(&real.input)).len(), 1);
}
