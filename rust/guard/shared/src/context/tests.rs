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
