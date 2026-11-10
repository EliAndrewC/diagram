use serde_json::json;

use super::GUARD;
use crate::protocol::{Answer, Event};
use crate::shared::checks::testkit::clone_at;
use crate::shared::session::Session;

fn run(name: &str, input: serde_json::Value) -> Vec<Answer> {
    (GUARD.decide)(
        &Event {
            name: name.to_owned(),
            input: input.clone(),
        },
        &Session::from_input(&input),
    )
}

#[test]
fn each_event_keeps_its_book() {
    let root = clone_at("hook");
    let path = root.join(".git/checks-open.json");
    std::fs::write(root.join("MANIFEST.md"), "unit: quote-check:0105 f\n").unwrap();
    assert!(run("PostToolUse", json!({"cwd": root, "tool_name": "Agent", "tool_use_id": "t", "tool_response": {"status": "async_launched", "agentId": "a"}})).is_empty());
    std::fs::write(&path, json!({"feature": "999-x", "dispatches": {"t": {"check": "quote-check", "subjects": [], "state": "pending", "t": 1.0}}}).to_string()).unwrap();
    assert!(run("PostToolUse", json!({"cwd": root, "tool_name": "Agent", "tool_use_id": "t", "tool_response": {"status": "async_launched", "agentId": "a"}})).is_empty());
    assert!(std::fs::read_to_string(&path)
        .unwrap()
        .contains("\"aid\": \"a\""));
    assert!(run(
        "SubagentStop",
        json!({"cwd": root, "agent_id": "a", "last_assistant_message": "x"})
    )
    .is_empty());
    assert!(run(
        "PostToolUse",
        json!({"cwd": root, "tool_name": "Bash", "tool_use_id": "b", "tool_input": {}})
    )
    .is_empty());
    assert!(run("PostToolUse", json!({"tool_name": "Bash"})).is_empty());
}

#[test]
fn a_write_back_is_refused_on_the_post_call() {
    let root = clone_at("after");
    std::fs::create_dir_all(root.join("specs/900-a")).unwrap();
    std::fs::write(root.join("specs/900-a/plan.md"), "# p\n\n## T01 x\n\nnow\n").unwrap();
    std::fs::write(
        root.join(".git/checks-open.json"),
        json!({"feature": "999-x", "plan_holds": {"h": {"feature": "900-a", "task": "T01", "t": 1.0, "state": "running", "aid": "ag"}}, "plan_snaps": {"e": {"h": ["## T01 x\n\nbefore\n"]}}}).to_string(),
    )
    .unwrap();
    let got = run(
        "PostToolUse",
        json!({"cwd": root, "tool_name": "Edit", "tool_use_id": "e", "tool_input": {}}),
    );
    assert!(
        matches!(&got[..], [Answer::Refuse(t)] if t.contains("written back")),
        "{got:?}"
    );
    assert!(std::fs::read_to_string(root.join("specs/900-a/plan.md"))
        .unwrap()
        .contains("before"));
}
