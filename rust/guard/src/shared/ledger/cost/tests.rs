//! The cost over hand-made transcripts: a streamed call counted once, the returns split, each raise the Python's, and the newest
//! transcript found.

use serde_json::json;

use super::{
    cells, cost, int_text, last_cells, read_segments, round_seconds, segments, transcript, Cost,
};
use crate::shared::tempdir::TempDir;

fn lines(values: &[serde_json::Value]) -> Vec<String> {
    values.iter().map(ToString::to_string).collect()
}

#[test]
fn a_streamed_call_counts_once_and_the_wall_spans_the_stamps() {
    let got = cost(&lines(&[
        json!({"timestamp": "2026-11-01T00:00:00.250Z"}),
        json!({"requestId": "r1", "message": {"usage": {"input_tokens": 1000, "cache_read_input_tokens": 500, "cache_creation_input_tokens": 100, "output_tokens": 50}}}),
        json!({"requestId": "r1", "message": {"usage": {"input_tokens": 1000, "output_tokens": "2_500"}}, "timestamp": "2026-11-01T00:00:12.750Z"}),
        json!({"message": {"id": 7, "usage": {"output_tokens": 1000.9, "input_tokens": true, "cache_read_input_tokens": " -3 "}}}),
        json!({"message": {"usage": {"output_tokens": 5}}}),
        json!({"message": 3, "requestId": ""}),
    ]))
    .unwrap();
    assert_eq!(
        got,
        Cost {
            wall_s: 12,
            input: 998,
            cache_read: -3,
            cache_write: 0,
            output: 3500,
            calls: 2
        }
    );
    assert_eq!(cells(&got), "12 s | 1k in (-0k cached) / 3.5k out");
    let one = cost(&[
        "not json".to_owned(),
        json!({"timestamp": "2026-11-01"}).to_string(),
    ])
    .unwrap();
    assert_eq!(one.wall_s, 0);
    let naive = cost(&lines(&[
        json!({"timestamp": "2026-11-01T00:00:00"}),
        json!({"timestamp": 20_261_102}),
    ]))
    .unwrap();
    assert_eq!(naive.wall_s, 86_400);
}

#[test]
fn what_the_python_raised_is_an_error() {
    let bad = |v: serde_json::Value| cost(&lines(&[v])).unwrap_err();
    assert!(bad(json!([1])).contains("no object"));
    assert!(bad(json!({"timestamp": "yesterday"})).contains("isoformat"));
    assert!(bad(json!({"timestamp": true})).contains("\"True\""));
    assert!(
        bad(json!({"requestId": "r", "message": {"usage": {"output_tokens": "many"}}}))
            .contains("invalid literal")
    );
    assert!(
        bad(json!({"requestId": "r", "message": {"usage": {"output_tokens": [1]}}}))
            .contains("TypeError")
    );
    let mixed = cost(&lines(&[
        json!({"timestamp": "2026-11-01T00:00:00"}),
        json!({"timestamp": "2026-11-01T00:00:00Z"}),
    ]));
    assert!(mixed.unwrap_err().contains("offset-naive"));
}

#[test]
fn a_python_int_and_a_tie_read_as_python_reads_them() {
    assert_eq!(int_text("+1_000"), Some(1000));
    assert_eq!(int_text("1__0"), None);
    assert_eq!(int_text("-"), None);
    assert_eq!(int_text("x"), None);
    assert_eq!(round_seconds(2_500_000), 2);
    assert_eq!(round_seconds(3_500_000), 4);
    assert_eq!(round_seconds(1_400_000), 1);
    assert_eq!(round_seconds(1_600_000), 2);
}

#[test]
fn each_prompt_after_the_first_opens_a_return() {
    let prompt = json!({"message": {"role": "user", "content": "go"}}).to_string();
    let parts_prompt =
        json!({"message": {"role": "user", "content": [{"type": "text", "text": "again"}]}})
            .to_string();
    let result =
        json!({"message": {"role": "user", "content": [{"type": "tool_result"}]}}).to_string();
    let empty = json!({"message": {"role": "user", "content": []}}).to_string();
    let other = json!({"message": {"role": "assistant", "content": "x"}}).to_string();
    let odd = json!({"message": {"role": "user", "content": 4}}).to_string();
    let plain = json!({"message": 1}).to_string();
    let all = [
        prompt.as_str(),
        "noise",
        result.as_str(),
        parts_prompt.as_str(),
        empty.as_str(),
        other.as_str(),
        odd.as_str(),
        plain.as_str(),
    ];
    let got = segments(&all);
    assert_eq!(got.len(), 2);
    assert_eq!(got[1].len(), 5);
    assert_eq!(segments(&[parts_prompt.as_str()]).len(), 1);
}

#[test]
fn the_newest_transcript_is_found_and_costed() {
    let root = TempDir::new("guard-ledger-cost");
    let old = root.join("p/s/subagents");
    let new = root.join("q/t/subagents");
    for d in [&old, &new] {
        std::fs::create_dir_all(d).unwrap();
    }
    std::fs::write(root.join("p/file"), "not a dir").unwrap();
    std::fs::write(old.join("agent-ab.jsonl"), "x\n").unwrap();
    let body = lines(&[
        json!({"message": {"role": "user", "content": "go"}, "timestamp": "2026-11-01T00:00:00Z"}),
        json!({"requestId": "a", "message": {"usage": {"output_tokens": 100}}, "timestamp": "2026-11-01T00:00:04Z"}),
        json!({"message": {"role": "user", "content": "again"}, "timestamp": "2026-11-01T00:01:00Z"}),
        json!({"requestId": "b", "message": {"usage": {"input_tokens": 2400}}, "timestamp": "2026-11-01T00:01:09Z"}),
    ]);
    std::fs::write(new.join("agent-ab.jsonl"), body.join("\n")).unwrap();
    let file = std::fs::File::options()
        .write(true)
        .open(old.join("agent-ab.jsonl"))
        .unwrap();
    file.set_modified(std::time::UNIX_EPOCH + std::time::Duration::from_secs(1_000))
        .unwrap();
    assert_eq!(transcript("ab", &root), Some(new.join("agent-ab.jsonl")));
    assert_eq!(transcript("zz", &root), None);
    assert_eq!(
        last_cells("ab", &root).unwrap(),
        "9 s | 2k in (0k cached) / 0.0k out"
    );
    assert_eq!(read_segments(&new.join("agent-ab.jsonl")).unwrap().len(), 2);
    assert!(last_cells("zz", &root)
        .unwrap_err()
        .starts_with("_review_cost: no transcript for agent zz under "));
    std::fs::write(new.join("agent-ab.jsonl"), [0xff_u8, 0xfe]).unwrap();
    assert!(last_cells("ab", &root).is_err());
    std::fs::write(new.join("agent-ab.jsonl"), "[1]\n").unwrap();
    assert!(last_cells("ab", &root).unwrap_err().contains("no object"));
}
