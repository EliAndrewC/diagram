//! What a call under a plan hold writes to the check state (451 T387): a Bash `true` wrote the whole 3.0 MB `checks-open.json`
//! twice - its snapshot at the `PreToolUse`, its removal at the `PostToolUse` - 97 to 118 ms of CPU a call (T373's lever E). The state
//! is saved now only where the call changed it; the hold still puts back held text a command overwrote.

use std::os::unix::fs::MetadataExt;
use std::path::Path;

use serde_json::{json, Value};

use super::handle;
use crate::checks::testkit::clone_at;
use crate::checks::{load, save};

const PLAN: &str = "# p\n\n## T01 x\n\nbody long enough to hold\n\n## T02 y\n\nother\n";

fn state_file(root: &Path) -> std::path::PathBuf {
    root.join(".git/checks-open.json")
}

/// The state file's inode: `save` writes a temporary and renames it, so a save is a new inode.
fn inode(root: &Path) -> u64 {
    std::fs::metadata(state_file(root)).unwrap().ino()
}

fn held(tag: &str) -> crate::tempdir::Held<std::path::PathBuf> {
    crate::log::quiet();
    let root = clone_at(tag);
    std::fs::create_dir_all(root.join("specs/900-a")).unwrap();
    std::fs::write(root.join("specs/900-a/plan.md"), PLAN).unwrap();
    let hold = json!({"feature": "900-a", "task": "T01", "blocks": [], "t": 1000.0, "state": "running", "aid": "agh",
        "root": root.to_string_lossy()});
    let state = json!({"feature": "999-x", "plan_holds": {"h": hold}, "dispatches": {}});
    save(&state_file(&root), &state).unwrap();
    root
}

fn bash(root: &Path, tid: &str) -> Value {
    json!({"cwd": root, "tool_name": "Bash", "tool_use_id": tid, "tool_input": {"command": "true"}})
}

fn plan(root: &Path) -> String {
    std::fs::read_to_string(root.join("specs/900-a/plan.md")).unwrap()
}

#[test]
fn a_bash_true_during_a_hold_writes_nothing() {
    let root = held("hold-writes");
    // the hold's first call keeps the held text: one write
    assert_eq!(handle("edit", &bash(&root, "b1"), Some(1000.0)), "");
    assert_eq!(handle("after", &bash(&root, "b1"), Some(1000.0)), "");
    let first = inode(&root);
    for tid in ["b2", "b3"] {
        assert_eq!(handle("edit", &bash(&root, tid), Some(1001.0)), "");
        assert_eq!(handle("after", &bash(&root, tid), Some(1001.0)), "");
    }
    assert_eq!(inode(&root), first);
}

#[test]
fn a_command_that_overwrote_held_text_is_still_written_back() {
    let root = held("hold-restore");
    assert_eq!(handle("edit", &bash(&root, "a"), Some(1000.0)), "");
    std::fs::write(
        root.join("specs/900-a/plan.md"),
        PLAN.replace("body long", "CHANGED"),
    )
    .unwrap();
    // another call begins while the first's change stands: it must not take the changed text as the held text
    assert_eq!(handle("edit", &bash(&root, "b"), Some(1000.0)), "");
    let msg = handle("after", &bash(&root, "a"), Some(1000.0));
    assert!(
        msg.contains("T01's section of specs/900-a/plan.md"),
        "{msg}"
    );
    assert_eq!(plan(&root), PLAN);
    assert_eq!(handle("after", &bash(&root, "b"), Some(1000.0)), "");
    // a later call's change is written back too
    assert_eq!(handle("edit", &bash(&root, "c"), Some(1001.0)), "");
    std::fs::write(
        root.join("specs/900-a/plan.md"),
        PLAN.replace("body long", "AGAIN"),
    )
    .unwrap();
    assert!(!handle("after", &bash(&root, "c"), Some(1001.0)).is_empty());
    assert_eq!(plan(&root), PLAN);
}

#[test]
fn a_held_heading_gone_is_named_once_not_at_every_call() {
    let root = held("hold-gone");
    assert_eq!(handle("edit", &bash(&root, "a"), Some(1000.0)), "");
    let gone = PLAN.replace("## T01 x\n\nbody long enough to hold\n\n", "");
    std::fs::write(root.join("specs/900-a/plan.md"), &gone).unwrap();
    let msg = handle("after", &bash(&root, "a"), Some(1000.0));
    assert!(msg.contains("NOTHING of it is written back"), "{msg}");
    assert_eq!(handle("edit", &bash(&root, "b"), Some(1000.0)), "");
    assert_eq!(handle("after", &bash(&root, "b"), Some(1000.0)), "");
}

#[test]
fn a_returned_review_leaves_no_kept_text() {
    let root = held("hold-returned");
    assert_eq!(handle("edit", &bash(&root, "a"), Some(1000.0)), "");
    assert_eq!(handle("after", &bash(&root, "a"), Some(1000.0)), "");
    let stop = json!({"cwd": root, "agent_id": "agh", "hook_event_name": "SubagentStop"});
    assert_eq!(handle("returned", &stop, Some(1000.0)), "");
    let s = load(&state_file(&root));
    assert!(s.get("plan_snaps").is_none(), "{s}");
}

#[test]
fn an_agent_launch_no_check_or_hold_names_writes_nothing() {
    let root = held("hold-agent");
    let first = inode(&root);
    let launched = json!({"cwd": root, "tool_name": "Agent", "tool_use_id": "x1", "tool_input": {"subagent_type": "Explore"},
        "tool_response": {"status": "completed", "agentId": "agx"}});
    assert_eq!(handle("launched", &launched, Some(1000.0)), "");
    let stop = json!({"cwd": root, "agent_id": "agx", "hook_event_name": "SubagentStop"});
    assert_eq!(handle("returned", &stop, Some(1000.0)), "");
    assert_eq!(inode(&root), first);
    // a wave dispatch still waiting for its agent: a return may pair it, so it is booked
    let mut s = load(&state_file(&root));
    s["dispatches"]["wave:1"] = json!({"check": "record-format", "state": "pending", "wave": "abc", "wave_len": 3, "t": 1000.0});
    save(&state_file(&root), &s).unwrap();
    let waiting = inode(&root);
    assert_eq!(handle("returned", &stop, Some(1000.0)), "");
    assert_ne!(inode(&root), waiting);
}
