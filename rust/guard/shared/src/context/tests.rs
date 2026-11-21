//! The reader alone, on transcripts written here (the context-cap guard's own tests drive it through the hook).

use std::path::PathBuf;

use serde_json::json;

use super::{call_of, context, own_transcript, usage_of, Call, TAIL_BYTES};
use crate::tempdir::TempDir;

/// An assistant row of one model call whose context is `tokens`.
fn call(tokens: u64) -> String {
    json!({"type": "assistant", "message": {"id": "msg_x", "usage": {
        "input_tokens": 2, "cache_read_input_tokens": tokens - 102, "cache_creation_input_tokens": 100, "output_tokens": 50}}})
    .to_string()
}

#[test]
fn a_builders_transcript_is_beside_the_sessions() {
    assert_eq!(
        own_transcript("/p/sess.jsonl", "a1"),
        Some(PathBuf::from("/p/sess/subagents/agent-a1.jsonl"))
    );
    assert_eq!(own_transcript("/p/sess.json", "a1"), None);
}

#[test]
fn the_context_is_the_last_assistant_rows_usage() {
    let d = TempDir::new("context");
    let own = d.path().join("t.jsonl");
    std::fs::write(&own, format!("{}\n{}\n", call(100_000), call(350_000))).unwrap();
    assert_eq!(context(&own), Some(350_000));
    // a later user row carries a child's usage, a synthetic row of zero is no call, bad JSON is skipped
    let child = json!({"type": "user", "message": {"usage": {"input_tokens": 900_000}}});
    let synthetic = json!({"type": "assistant", "message": {"usage": {"input_tokens": 0}}});
    std::fs::write(
        &own,
        format!(
            "{}\n{child}\n{synthetic}\n\"x\"\n{{\"usage\" not json\n",
            call(120_000)
        ),
    )
    .unwrap();
    assert_eq!(context(&own), Some(120_000));
    // a last row longer than a read step, with no trailing newline
    let big = json!({"type": "assistant", "pad": "p".repeat(200_000), "message": {"usage": {"input_tokens": 400_000}}});
    std::fs::write(&own, format!("{}\n{big}", call(5_000))).unwrap();
    assert_eq!(context(&own), Some(400_000));
    // none at all, no file, and a call deeper than the tail
    std::fs::write(&own, "{\"type\": \"user\"}\n").unwrap();
    assert_eq!(context(&own), None);
    assert_eq!(context(&d.path().join("nothing.jsonl")), None);
    let deep = format!(
        "{}\n{}\n",
        call(500_000),
        "x".repeat(usize::try_from(TAIL_BYTES).unwrap() + 10)
    );
    std::fs::write(&own, deep).unwrap();
    assert_eq!(context(&own), None);
    assert_eq!(usage_of(b"{\"type\": \"assistant\"}"), None);
}

/// A real advisor-carrying row's usage (a builder's of 2026-11-20, `agent-a8dade2aa6a99c5dd.jsonl` row 132, its counts alone): the
/// top level sums the builder's own two `message` iterations, 149,686 before the advisor call and 151,198 after it, to 300,884;
/// the `advisor_message` iteration's 140,114 is in neither (451 T68, measured 2026-11-21 on all 581 such rows of the session).
fn advisor_row() -> serde_json::Value {
    json!({"type": "assistant", "message": {"id": "msg_a", "usage": {
        "input_tokens": 4, "cache_creation_input_tokens": 3045, "cache_read_input_tokens": 297_835, "output_tokens": 982,
        "server_tool_use": {"web_search_requests": 0, "web_fetch_requests": 0},
        "iterations": [
            {"input_tokens": 2, "output_tokens": 226, "cache_read_input_tokens": 148_151, "cache_creation_input_tokens": 1533,
             "type": "message"},
            {"input_tokens": 140_114, "output_tokens": 10489, "cache_read_input_tokens": 0, "cache_creation_input_tokens": 0,
             "type": "advisor_message", "model": "claude-fable-5-2"},
            {"input_tokens": 2, "output_tokens": 756, "cache_read_input_tokens": 149_684, "cache_creation_input_tokens": 1512,
             "type": "message"}]}}})
}

/// RED FIRST (451 T68): a row carrying an advisor call is read as the builder's own last iteration, 151,198, not the top level's
/// 300,884 that refused 33 of the cap's 34 refusals since T12; a row with no `iterations`, none of type `message`, or a last own
/// iteration of zero is read at its top level; the call's cost (`call_of`, the event log's `tok`) stays the top level's.
#[test]
fn an_advisor_rows_context_is_the_builders_own_last_iteration() {
    let adv = advisor_row().to_string();
    assert_eq!(usage_of(adv.as_bytes()), Some(151_198));
    let d = TempDir::new("context-advisor");
    let own = d.path().join("t.jsonl");
    std::fs::write(&own, format!("{}\n{adv}\n", call(140_000))).unwrap();
    assert_eq!(context(&own), Some(151_198));
    // two own iterations and no advisor: the last
    let two = json!({"type": "assistant", "message": {"usage": {"input_tokens": 9, "iterations": [
        {"type": "message", "input_tokens": 3}, {"type": "message", "input_tokens": 6}]}}});
    assert_eq!(usage_of(two.to_string().as_bytes()), Some(6));
    // no own iteration, an own iteration of zero, an `iterations` that is no list: the top level
    for its in [
        json!([{"type": "advisor_message", "input_tokens": 7}]),
        json!([{"type": "message", "input_tokens": 0}]),
        json!("x"),
    ] {
        let row = json!({"type": "assistant", "message": {"usage": {"input_tokens": 5, "iterations": its}}});
        assert_eq!(usage_of(row.to_string().as_bytes()), Some(5));
    }
    // the cost is the top level's, both own iterations billed
    let c = call_of(adv.as_bytes()).unwrap();
    assert_eq!(c.input + c.cached + c.created, 300_884);
}

#[test]
fn a_call_is_its_ids_and_its_four_counts() {
    assert_eq!(
        call_of(call(1_000).as_bytes()),
        Some(Call {
            id: "msg_x".into(),
            input: 2,
            cached: 898,
            created: 100,
            out: 50
        })
    );
    assert_eq!(
        call_of(b"{\"type\": \"assistant\", \"message\": {}, \"usage\": 1}"),
        None
    );
    assert_eq!(call_of(b"no usage here"), None);
}
