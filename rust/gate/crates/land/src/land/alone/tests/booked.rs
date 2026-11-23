//! 451 T161: an edit is its builder's, not the clone's mark's. 449's record bundle, CLEAR and committed, was refused at land-alone's
//! own-edits step on four files the sheet bundle's builder had written, because that builder's description (`449 sheet bundle (fresh
//! 3): ...`) named no task and the event log booked its edits to the mark, which named the record bundle (observed 2026-11-22). Here the
//! line is written by the event log's own writer, as the hook writes it, and read by the script's split.

use serde_json::json;

use super::{alone, put, sh, world};

/// The builder `abun`'s edit of `rel`, its description naming no task and its prompt's first line naming T1, while the clone's mark
/// names T2: the event log's writer books it, into the script's events directory.
fn builder_edit(dir: &std::path::Path, c: &std::path::Path, rel: &str) {
    let subagents = dir.join("projects/s1/subagents");
    put(
        &subagents,
        "agent-abun.meta.json",
        r#"{"description":"451 sheet bundle (fresh 3): verify, the reviews, closing","spawnDepth":1}"#,
    );
    let first = json!({"type": "user", "message": {"role": "user", "content": "451 bundle T1, a fresh builder in the clone"}});
    put(&subagents, "agent-abun.jsonl", &format!("{first}\n"));
    put(
        c,
        ".git/task-starts.jsonl",
        "{\"feature\": \"451-x\", \"task\": \"T1\", \"utc\": \"2026-11-22T01:00:00Z\"}\n{\"feature\": \"451-x\", \"task\": \"T2\", \"utc\": \"2026-11-22T02:00:00Z\"}\n",
    );
    let payload = json!({"hook_event_name": "PostToolUse", "cwd": c, "session_id": "s1", "agent_id": "abun",
        "transcript_path": dir.join("projects/s1.jsonl"), "tool_name": "Edit", "tool_use_id": "tu",
        "tool_input": {"file_path": c.join(rel), "old_string": "a", "new_string": "b"}});
    let events = dir.join("events").to_string_lossy().into_owned();
    let env = move |k: &str| (k == "L7R_EVENTS_DIR").then(|| events.clone());
    let log =
        l7r_shared::guards::event_log_hooks::append(&payload, "2099-01-01T00:00:00.000Z", c, &env);
    assert!(log.is_some_and(|l| l.ends_with("451-x.jsonl")));
}

/// The builder's edit, made while the mark names T2, is T1's: T1's landing refuses it as its own uncommitted file, where booked to the
/// mark it was listed as T2's and left behind.
#[test]
fn a_builders_edit_is_its_briefs_task_not_the_marks() {
    let (dir, c) = world("alone-booked");
    put(&c, "src/t1d.rs", "T1's own, by its bundle's builder\n");
    builder_edit(&dir, &c, "src/t1d.rs");
    let (_, said) = alone(&dir, &c, &[]);
    let refused = said.contains("T1's own edits are uncommitted - commit them, then land again");
    assert!(refused, "{said}");
    assert!(said.contains("-- src/t1d.rs"), "{said}");
    assert!(!said.contains("T2: src/t1d.rs"), "{said}");
    sh(&c, "rm src/t1d.rs");
}
