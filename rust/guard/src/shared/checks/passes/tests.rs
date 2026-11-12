use serde_json::json;

use super::{log_pass_at, usage};
use crate::shared::checks::testkit::{clone_at, dir};

fn transcript(lines: &[String]) -> String {
    format!("{}\n", lines.join("\n"))
}

fn line(body: &serde_json::Value) -> String {
    body.to_string()
}

fn sample() -> Vec<String> {
    vec![
        line(
            &json!({"message": {"role": "user", "content": "first line of the prompt | piped\nmore"}, "timestamp": "2026-11-01T00:00:00Z"}),
        ),
        line(
            &json!({"requestId": "r1", "message": {"role": "assistant", "usage": {"input_tokens": 1000, "cache_read_input_tokens": 500, "cache_creation_input_tokens": 100, "output_tokens": 50}}, "timestamp": "2026-11-01T00:00:13Z"}),
        ),
        line(
            &json!({"requestId": "r1", "message": {"usage": {"input_tokens": 1000, "output_tokens": 2500}}}),
        ),
        line(
            &json!({"message": {"id": "m2", "usage": {"output_tokens": 1000}}, "timestamp": null}),
        ),
        "not json".to_owned(),
        line(&json!({"message": {"usage": 3}})),
        line(&json!({"message": {"role": "user", "content": 7}})),
    ]
}

#[test]
fn a_returned_check_logs_one_pass_and_a_second_return_a_second() {
    let g = dir("passes");
    let t = g.join("agent.jsonl");
    std::fs::write(&t, transcript(&sample())).unwrap();
    let payload = json!({"agent_type": "quote-check", "agent_id": "ag1", "agent_transcript_path": t.to_string_lossy()});
    let at = 1_762_000_000.0;
    assert!(!log_pass_at(
        &g,
        "returned",
        &json!({"agent_type": "not-a-check", "agent_id": "x", "agent_transcript_path": t.to_string_lossy()}),
        at
    ));
    assert!(!log_pass_at(
        &g,
        "returned",
        &json!({"agent_type": "quote-check", "agent_id": "x"}),
        at
    ));
    assert!(!log_pass_at(
        &g,
        "returned",
        &json!({"agent_type": "quote-check", "agent_id": "x", "agent_transcript_path": "/no/such"}),
        at
    ));
    assert!(log_pass_at(&g, "returned", &payload, at));
    let row: serde_json::Value = serde_json::from_str(
        std::fs::read_to_string(g.join("check-passes.jsonl"))
            .unwrap()
            .lines()
            .next()
            .unwrap(),
    )
    .unwrap();
    assert_eq!(row["check"], json!("quote-check"));
    assert_eq!(row["subject"], json!("first line of the prompt piped"));
    assert_eq!(row["segment"], json!(0));
    assert_eq!(row["wall"], json!("13 s"));
    assert_eq!(row["tokens"], json!("1k in (0k cached) / 3.5k out"));
    assert_eq!(row["date"], json!("2025-11-01"));
    assert!(!log_pass_at(&g, "returned", &payload, at));
    let mut more = sample();
    more.push(line(&json!({"message": {"role": "user", "content": [{"type": "text", "text": "resumed"}]}, "timestamp": "2026-11-01T00:00:20Z"})));
    more.push(line(
        &json!({"message": {"role": "user", "content": [{"type": "tool_result"}]}}),
    ));
    std::fs::write(&t, transcript(&more)).unwrap();
    assert!(log_pass_at(&g, "returned", &payload, at));
    let last: serde_json::Value = serde_json::from_str(
        std::fs::read_to_string(g.join("check-passes.jsonl"))
            .unwrap()
            .lines()
            .last()
            .unwrap(),
    )
    .unwrap();
    assert_eq!(
        (last["segment"].clone(), last["subject"].clone()),
        (json!(1), json!("first line of the prompt piped"))
    );
    std::fs::write(g.join("check-passes.jsonl"), "not json\n").unwrap();
    assert!(!log_pass_at(&g, "returned", &payload, at));
}

#[test]
fn a_transcript_that_cannot_be_costed_is_not_logged() {
    let g = dir("cost-bad");
    let t = g.join("bad.jsonl");
    let payload = json!({"agent_type": "quote-check", "agent_id": "ag", "agent_transcript_path": t.to_string_lossy()});
    std::fs::write(&t, transcript(&[line(&json!({"timestamp": "not-a-date"}))])).unwrap();
    assert!(!log_pass_at(&g, "returned", &payload, 1.0));
    std::fs::write(&t, transcript(&["[1, 2]".to_owned()])).unwrap();
    assert!(!log_pass_at(&g, "returned", &payload, 1.0));
    std::fs::write(
        &t,
        transcript(&[
            line(&json!({"message": 3})),
            line(&json!({"timestamp": "2026-01-01T00:00:00Z"})),
        ]),
    )
    .unwrap();
    assert!(log_pass_at(&g, "returned", &payload, 1.0));
    let row = std::fs::read_to_string(g.join("check-passes.jsonl")).unwrap();
    assert!(row.contains("\"subject\": \"\"") && row.contains("\"wall\": \"0 s\""));
}

#[test]
fn only_a_finished_foreground_launch_is_a_pass() {
    let g = dir("launched");
    let payload = json!({"tool_response": {"status": "completed", "agentId": "nobody-has-this-id"}, "tool_input": {"subagent_type": "quote-check"}});
    assert!(!log_pass_at(&g, "launched", &payload, 1.0));
    assert!(!log_pass_at(
        &g,
        "launched",
        &json!({"tool_response": {"status": "async_launched"}}),
        1.0
    ));
    assert!(!log_pass_at(&g, "launched", &json!({}), 1.0));
    super::log_pass(&g, "launched", &payload, 1.0);
    let t = g.join("found.jsonl");
    std::fs::write(
        &t,
        transcript(&[
            line(&json!({"timestamp": "2026-01-01T00:00:00Z"})),
            line(&json!({"message": {"role": "user", "content": [{"text": "from parts"}, 4]}})),
        ]),
    )
    .unwrap();
    let found = t.clone();
    let done = |_: &str| Some(found.clone());
    assert!(super::log_pass_found(&g, "launched", &payload, 1.0, &done));
    let logged = std::fs::read_to_string(g.join("check-passes.jsonl")).unwrap();
    assert!(logged.contains("\"subject\": \"from parts\""));
    assert!(!log_pass_at(
        &g,
        "launched",
        &json!({"tool_response": 3, "tool_input": 4}),
        1.0
    ));
}

#[test]
fn a_step_leaves_a_tool_usage_line() {
    let root = clone_at("usage");
    usage(&root.join(".git"), "planhold-restore", "step", "changed");
    let line = std::fs::read_to_string(root.join(".git/tool-usage.jsonl")).unwrap();
    assert!(
        line.contains("\"tool\": \"planhold-restore\"")
            && line.contains("\"outcome\": \"changed\"")
    );
}

#[test]
fn a_prompt_after_noise_and_two_transcripts_of_one_agent() {
    let g = dir("noise");
    let t = g.join("found.jsonl");
    std::fs::write(
        &t,
        transcript(&[
            "not json at first".to_owned(),
            line(&json!({"timestamp": "2026-01-01T00:00:00Z"})),
            line(&json!({"message": {"role": "user", "content": [{"text": "from parts"}, 4]}})),
        ]),
    )
    .unwrap();
    let found = t.clone();
    let done = |_: &str| Some(found.clone());
    let payload = json!({"tool_response": {"status": "completed", "agentId": "x"}, "tool_input": {"subagent_type": "quote-check"}});
    assert!(super::log_pass_found(&g, "launched", &payload, 1.0, &done));
    let odd_input =
        json!({"tool_response": {"status": "completed", "agentId": "x"}, "tool_input": 3});
    assert!(!super::log_pass_found(
        &g, "launched", &odd_input, 1.0, &done
    ));
}
