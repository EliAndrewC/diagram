//! The reader against scratch logs and transcripts: every branch `event_log.from_transcript` took, and its raises.

use serde_json::{json, Value};

use super::{from_transcript, read_jsonl, reversals, universal};

fn evs(rows: &[Value]) -> Vec<Value> {
    from_transcript(rows)
        .unwrap()
        .into_iter()
        .map(Value::Object)
        .collect()
}

#[test]
fn a_log_reads_as_python_text_mode_reads_it() {
    let d = crate::shared::tempdir::TempDir::new("guard-events-read");
    let p = d.join("log.jsonl");
    std::fs::write(
        &p,
        b"{\"a\":1}\r{\"b\":2}\r\n\n  \nnot json\n{\"c\":\"\xff\"}\n",
    )
    .unwrap();
    let rows = read_jsonl(&p).unwrap();
    assert_eq!(
        rows,
        vec![json!({"a": 1}), json!({"b": 2}), json!({"c": "\u{fffd}"})]
    );
    assert!(read_jsonl(&d.join("absent.jsonl")).is_err());
    assert_eq!(universal("a\r\nb\rc"), "a\nb\nc");
}

#[test]
fn a_transcript_becomes_the_hooks_events() {
    let rows = [
        json!({"isSidechain": true, "type": "assistant", "timestamp": "2026-01-01T00:00:09Z"}),
        json!({"type": "assistant", "timestamp": "2026-01-01T00:00:01Z", "sessionId": "s",
               "message": {"stop_reason": "end_turn", "content": [
                   "text", {"type": "text"},
                   {"type": "tool_use", "id": "t1", "name": "Agent", "input": {"subagent_type": "quote-check", "prompt": "x"}},
                   {"type": "tool_use", "id": "t2", "name": "Agent", "input": {}},
                   {"type": "tool_use", "id": "t3", "name": "Bash", "input": {"command": "make quick"}}]}}),
        json!({"type": "user", "timestamp": "2026-01-01T00:00:02Z", "sessionId": "s",
               "toolUseResult": {"agentId": "a1", "status": "async_launched"},
               "message": {"content": [{"type": "tool_result", "tool_use_id": "t1"}, "x"]}}),
        json!({"type": "user", "timestamp": "2026-01-01T00:00:03Z", "sessionId": "s",
               "toolUseResult": {"agentId": "a2"},
               "message": {"content": [{"type": "tool_result", "tool_use_id": "t2"}]}}),
        json!({"type": "user", "timestamp": "2026-01-01T00:00:04Z", "sessionId": "s", "toolUseResult": "no",
               "message": {"content": [{"type": "tool_result", "tool_use_id": "t3"}]}}),
        json!({"type": "user", "timestamp": "2026-01-01T00:00:05Z", "sessionId": "s", "toolUseResult": {"agentId": "a3"},
               "message": {"content": [{"type": "tool_result", "tool_use_id": "t9"}]}}),
        json!({"type": "user", "timestamp": "2026-01-01T00:00:06Z", "sessionId": "s", "message": {"content": "go on"}}),
        json!({"type": "user", "isMeta": true, "timestamp": "2026-01-01T00:00:06Z", "message": {"content": "meta"}}),
        json!({"type": "user", "timestamp": "2026-01-01T00:00:06Z", "message": {"content": "<system-reminder>x"}}),
        json!({"type": "queue-operation", "operation": "enqueue", "timestamp": "2026-01-01T00:00:07Z",
               "content": "<task-notification><task-id>a1</task-id><result>quote-check: 0 findings\n</result>"}),
        json!({"type": "queue-operation", "operation": "enqueue", "timestamp": "2026-01-01T00:00:08Z",
               "content": "<task-id>a2</task-id><result>PASS\n"}),
        json!({"type": "queue-operation", "operation": "enqueue", "timestamp": "2026-01-01T00:00:08Z",
               "content": "<task-id>a2</task-id>"}),
        json!({"type": "queue-operation", "operation": "enqueue", "content": "<task-id>zz</task-id>"}),
        json!({"type": "queue-operation", "operation": "enqueue", "content": "nothing"}),
        json!({"type": "queue-operation", "operation": "dequeue"}),
        json!({"type": "summary"}),
    ];
    let got = evs(&rows);
    let shape: Vec<String> = got
        .iter()
        .map(|e| {
            format!(
                "{} {} {} {}",
                e["t"].as_str().unwrap().get(17..19).unwrap_or("?"),
                e["ev"],
                e.get("agent")
                    .or_else(|| e.get("tool"))
                    .unwrap_or(&Value::Null),
                e.get("verdict")
                    .or_else(|| e.get("gm"))
                    .unwrap_or(&Value::Null)
            )
        })
        .collect();
    assert_eq!(
        shape,
        [
            "01 \"PreToolUse\" \"quote-check\" null",
            "01 \"PreToolUse\" \"general-purpose\" null",
            "01 \"PreToolUse\" \"Bash\" null",
            "01 \"Stop\" null null",
            "02 \"PostToolUse\" \"quote-check\" null",
            "02 \"SubagentStart\" \"quote-check\" null",
            "03 \"PostToolUse\" \"general-purpose\" null",
            "04 \"PostToolUse\" \"Bash\" null",
            "05 \"PostToolUse\" null null",
            "06 \"UserPromptSubmit\" null true",
            "07 \"SubagentStop\" \"quote-check\" \"clean\"",
            "08 \"SubagentStop\" \"general-purpose\" \"PASS\"",
            "08 \"SubagentStop\" \"general-purpose\" null",
        ]
    );
    // a row with no time is stamped now
    let now = evs(&[json!({"type": "assistant", "message": {"stop_reason": "end_turn"}})]);
    assert!(now[0]["t"].as_str().unwrap().ends_with('Z'));
}

#[test]
fn a_transcript_raises_where_the_python_raised() {
    for row in [
        json!(5),
        json!({"type": "assistant", "message": "text"}),
        json!({"type": "assistant", "message": {"content": 5}}),
        json!({"type": "user", "message": [1]}),
    ] {
        assert!(from_transcript(&[row]).is_err());
    }
    let launch = [
        json!({"type": "assistant", "message": {"content": [{"type": "tool_use", "id": "t", "name": "Agent", "input": [1]}]}}),
        json!({"type": "user", "toolUseResult": {"agentId": "a"}, "message": {"content": [{"type": "tool_result", "tool_use_id": "t"}]}}),
    ];
    assert!(from_transcript(&launch).is_err());
    assert_eq!(
        evs(&[
            json!({"type": "assistant", "message": {"content": "words"}}),
            json!({"type": "assistant", "message": {"content": {"k": 1}}})
        ]),
        Vec::<Value>::new()
    );
}

#[test]
fn the_capped_checks_are_the_record_claims_and_review_checks() {
    use super::super::round_capped;
    assert!(
        round_capped("impl-drift") && round_capped("quote-check") && round_capped("glyph-check")
    );
    assert!(!round_capped("spec-fidelity"));
}

#[test]
fn a_put_back_passage_is_a_reversal() {
    let e = |path: Value, old: &str, new: Value, t: &str| json!({"ev": "PreToolUse", "tool": "Edit", "path": path, "old": old, "new": new, "t": t});
    let events = [
        e(json!("a.md"), "A", json!("B"), "1"),
        e(json!("a.md"), "B", json!("A"), "2"),
        e(json!(null), "C", json!(5), "3"),
        json!({"ev": "PreToolUse", "tool": "Edit", "path": "a.md", "old": "", "new": "A"}),
        json!({"ev": "PreToolUse", "tool": "Write", "path": "a.md", "old": "x", "new": "A"}),
        json!({"ev": "PostToolUse", "tool": "Edit"}),
    ];
    let maps: Vec<_> = events.iter().filter_map(Value::as_object).collect();
    assert_eq!(reversals(&maps), [("a.md".to_owned(), "2".to_owned())]);
}
