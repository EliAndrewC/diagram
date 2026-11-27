use serde_json::json;

use super::GUARD;
use crate::protocol::{Answer, Event};
use crate::shared::checks::testkit::clone_at;
use crate::shared::session::Session;

fn run(name: &str, input: &serde_json::Value) -> Vec<Answer> {
    (GUARD.decide)(
        &Event {
            name: name.to_owned(),
            input: input.clone(),
        },
        &Session::from_input(input),
    )
}

#[test]
fn each_event_keeps_its_book() {
    let root = clone_at("hook");
    let path = root.join(".git/checks-open.json");
    std::fs::write(root.join("MANIFEST.md"), "unit: quote-check:0105 f\n").unwrap();
    assert!(run("PostToolUse", &json!({"cwd": root, "tool_name": "Agent", "tool_use_id": "t", "tool_response": {"status": "async_launched", "agentId": "a"}})).is_empty());
    std::fs::write(&path, json!({"feature": "999-x", "dispatches": {"t": {"check": "quote-check", "subjects": [], "state": "pending", "t": 1.0}}}).to_string()).unwrap();
    assert!(run("PostToolUse", &json!({"cwd": root, "tool_name": "Agent", "tool_use_id": "t", "tool_response": {"status": "async_launched", "agentId": "a"}})).is_empty());
    assert!(std::fs::read_to_string(&path)
        .unwrap()
        .contains("\"aid\": \"a\""));
    assert!(run(
        "SubagentStop",
        &json!({"cwd": root, "agent_id": "a", "last_assistant_message": "x"})
    )
    .is_empty());
    assert!(run(
        "PostToolUse",
        &json!({"cwd": root, "tool_name": "Bash", "tool_use_id": "b", "tool_input": {}})
    )
    .is_empty());
    // no cwd: a test build reads the tree its test names, none here (451 T123)
    assert!(run("PostToolUse", &json!({"tool_name": "Bash"})).is_empty());
}

/// A call with no cwd reads the tree its test names and no other (451 T123): the guard's tests ran in the landing worktree, whose
/// `.git` file leads to the clone's check state, and their no-cwd `PostToolUse` found a live review's hold there and a snapshot under
/// no id, wrote it back and failed the landing (2026-11-21, T80's). The tree named, the call is written back there; none named, the
/// call reads no state, and the scratch state stands as it was.
#[test]
fn a_call_with_no_cwd_reads_only_the_tree_its_test_names() {
    let root = clone_at("no-cwd");
    let state_file = root.join(".git/checks-open.json");
    std::fs::create_dir_all(root.join("specs/900-a")).unwrap();
    let planted = json!({"feature": "999-x", "plan_holds": {"h": {"feature": "900-a", "task": "T01", "t": 1.0, "state": "running", "aid": "ag"}}, "plan_snaps": {"": {"h": ["## T01 x\n\nbefore\n"]}}}).to_string();
    let bare = json!({"tool_name": "Bash"});
    std::fs::write(root.join("specs/900-a/plan.md"), "# p\n\n## T01 x\n\nnow\n").unwrap();
    std::fs::write(&state_file, &planted).unwrap();
    let unnamed = run("PostToolUse", &bare);
    let untouched = std::fs::read_to_string(&state_file).unwrap();
    crate::shared::env::set("PWD", root.as_os_str());
    let named = run("PostToolUse", &bare);
    crate::shared::env::unset("PWD");
    let plan = std::fs::read_to_string(root.join("specs/900-a/plan.md")).unwrap();
    assert!(unnamed.is_empty() && untouched == planted, "{untouched}");
    let refused = matches!(&named[..], [Answer::Refuse(t)] if t.contains("written back"));
    assert!(refused, "{named:?}");
    assert!(plan.contains("before"), "{plan}");
}

/// A state that is not UTF-8 holds no snapshot, as the whole-string read found (451 T508): a stream that skipped the check let
/// `handle` run on it, and its empty reading was written over the file's bytes.
#[test]
fn a_state_that_is_not_utf8_is_left_as_it_is() {
    let root = clone_at("not-utf8");
    let path = root.join(".git/checks-open.json");
    let mut planted = b"{\"feature\": \"\xff\", ".to_vec();
    planted.extend_from_slice(br#""plan_holds": {"h": {"feature": "900-a", "task": "T01", "t": 1.0, "state": "running", "aid": "ag"}}, "plan_snaps": {"e": {"h": ["x"]}}}"#);
    std::fs::write(&path, &planted).unwrap();
    let got = run(
        "PostToolUse",
        &json!({"cwd": root, "tool_name": "Bash", "tool_use_id": "e", "tool_input": {}}),
    );
    assert!(got.is_empty() && std::fs::read(&path).unwrap() == planted);
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
    assert!(run(
        "PostToolUse",
        &json!({"cwd": root, "tool_name": "Write", "tool_use_id": "unrelated"})
    )
    .is_empty());
    let got = run(
        "PostToolUse",
        &json!({"cwd": root, "tool_name": "Edit", "tool_use_id": "e", "tool_input": {}}),
    );
    assert!(matches!(&got[..], [Answer::Refuse(t)] if t.contains("written back")));
    assert!(std::fs::read_to_string(root.join("specs/900-a/plan.md"))
        .unwrap()
        .contains("before"));
}

/// A call that changes held text and then fails is written back too (451 T78): a Bash command that exits non-zero fires
/// `PostToolUseFailure`, not `PostToolUse` (measured 2026-11-21), and the guard took only the second, so the hook's own event filter
/// is what this drives. A failed Agent or `TaskStop` call launched and stopped nothing: its hold keeps its state.
#[test]
fn a_failed_call_is_written_back_and_a_failed_launch_keeps_its_hold() {
    let root = clone_at("failure");
    let state_file = root.join(".git/checks-open.json");
    std::fs::create_dir_all(root.join("specs/900-a")).unwrap();
    std::fs::write(root.join("specs/900-a/plan.md"), "# p\n\n## T01 x\n\nnow\n").unwrap();
    std::fs::write(
        &state_file,
        json!({"feature": "999-x", "plan_holds": {"h": {"feature": "900-a", "task": "T01", "t": 1.0, "state": "pending"}, "r": {"feature": "900-a", "task": "T01", "t": 1.0, "state": "running", "aid": "ag"}}, "plan_snaps": {"e": {"r": ["## T01 x\n\nbefore\n"]}}}).to_string(),
    )
    .unwrap();
    let fail = |tool: &str, extra: serde_json::Value| {
        let mut input = json!({"cwd": root, "tool_name": tool});
        for (k, v) in extra.as_object().unwrap() {
            input[k] = v.clone();
        }
        crate::protocol::run(
            &mut Event {
                name: "PostToolUseFailure".to_owned(),
                input,
            },
            &[GUARD],
        )
    };
    let reply = fail(
        "Bash",
        json!({"tool_use_id": "e", "tool_input": {"command": "x"}}),
    );
    assert!(reply.code == 2 && reply.stderr.contains("written back"));
    assert!(std::fs::read_to_string(root.join("specs/900-a/plan.md"))
        .unwrap()
        .contains("before"));
    assert_eq!(
        fail("Agent", json!({"tool_use_id": "h", "tool_input": {}})).code,
        0
    );
    assert_eq!(
        fail(
            "TaskStop",
            json!({"tool_use_id": "s", "tool_input": {"task_id": "ag"}})
        )
        .code,
        0
    );
    let holds: serde_json::Value =
        serde_json::from_str(&std::fs::read_to_string(&state_file).unwrap()).unwrap();
    assert_eq!(holds["plan_holds"]["h"]["state"], "pending");
    assert_eq!(holds["plan_holds"]["r"]["aid"], "ag");
}

/// The hold through both guards (451 T387): record-edit's `PreToolUse` keeps the held text once, a Bash call's later start and end
/// save nothing, and checks-hooks' `PostToolUse` still finds the kept text through its prefilter and writes a change back.
#[test]
fn a_hold_kept_by_record_edit_is_written_back_by_checks_hooks() {
    use std::os::unix::fs::MetadataExt;
    let root = clone_at("two-guards");
    let state_file = root.join(".git/checks-open.json");
    let plan = root.join("specs/900-a/plan.md");
    std::fs::create_dir_all(root.join("specs/900-a")).unwrap();
    std::fs::write(&plan, "# p\n\n## T01 x\n\nbefore\n").unwrap();
    let now = crate::shared::checks::now();
    std::fs::write(&state_file, json!({"feature": "999-x", "plan_holds": {"h": {"feature": "900-a", "task": "T01", "t": now,
        "state": "running", "aid": "ag", "root": root.to_string_lossy()}}}).to_string()).unwrap();
    let call = |tid: &str| json!({"cwd": root, "tool_name": "Bash", "tool_use_id": tid, "tool_input": {"command": "true"}});
    let pre = |tid: &str| {
        let input = call(tid);
        (crate::guards::record_edit_hooks::GUARD.decide)(
            &Event {
                name: "PreToolUse".to_owned(),
                input: input.clone(),
            },
            &Session::from_input(&input),
        )
    };
    assert!(pre("a").is_empty() && run("PostToolUse", &call("a")).is_empty());
    let kept = std::fs::metadata(&state_file).unwrap().ino();
    assert!(pre("b").is_empty());
    std::fs::write(&plan, "# p\n\n## T01 x\n\nCHANGED\n").unwrap();
    let got = run("PostToolUse", &call("b"));
    assert!(matches!(&got[..], [Answer::Refuse(t)] if t.contains("written back")));
    assert!(std::fs::read_to_string(&plan).unwrap().contains("before"));
    assert_eq!(std::fs::metadata(&state_file).unwrap().ino(), kept);
}
