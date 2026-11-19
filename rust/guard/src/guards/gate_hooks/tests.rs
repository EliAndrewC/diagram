//! The decider; the verdicts against today's are the suite's (`tests/hooks/test-gate-hooks.sh`, replayed through the shim).

use serde_json::json;

use super::decide;
use crate::protocol::{Answer, Event};
use crate::shared::session::Session;

fn bash(cmd: &str) -> Event {
    Event {
        name: "PreToolUse".to_owned(),
        input: json!({"tool_name": "Bash", "session_id": "s", "tool_input": {"command": cmd}}),
    }
}

fn run(e: &Event) -> Vec<Answer> {
    crate::shared::log::quiet();
    decide(e, &Session::from_input(&json!({})))
}

#[test]
fn gate_ok_stands_aside_with_a_reason_and_refuses_without() {
    assert!(run(&bash(
        "make quick && make done  # GATE_OK: comparing the two"
    ))
    .is_empty());
    assert!(
        matches!(&run(&bash("make done  # GATE_OK"))[..], [Answer::Refuse(w)] if w.contains("GATE_OK with no reason"))
    );
}

#[test]
fn quick_and_done_are_rewritten_to_done() {
    let got = run(&bash("make quick && make done"));
    assert!(
        matches!(&got[..], [Answer::Rewrite(v), Answer::Notice(n)] if v["command"] == "make done" && n.contains("superset"))
    );
}

#[test]
fn a_subset_run_arms_nothing_and_another_tool_is_not_read() {
    assert!(run(&bash("make done")).is_empty());
    assert!(run(&bash("python3 -m pytest t.py -k \"a or b\"")).is_empty());
    assert!(run(&bash("make done")).is_empty());
    let edit = Event {
        name: "PreToolUse".to_owned(),
        input: json!({"tool_name": "Edit", "tool_input": {"file_path": "a.py"}}),
    };
    assert!(run(&edit).is_empty());
}
