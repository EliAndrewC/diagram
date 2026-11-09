//! A workflow wave against the last hand-launched one.

use std::path::{Path, PathBuf};

use serde_json::{json, Value};

use super::{cli, newest_run, report};

fn agent(d: &Path, id: &str, start: &str, read: i64, written: i64, meta: &Value) {
    std::fs::create_dir_all(d).unwrap();
    std::fs::write(d.join(format!("agent-{id}.meta.json")), meta.to_string()).unwrap();
    let usage = json!({"cache_read_input_tokens": read, "cache_creation_input_tokens": written});
    let rows = [
        json!({"type": "user", "timestamp": start, "message": {"role": "user", "content": "go"}}),
        json!({"type": "assistant", "timestamp": start, "message": {"usage": usage}}),
    ];
    std::fs::write(
        d.join(format!("agent-{id}.jsonl")),
        rows.iter()
            .map(Value::to_string)
            .collect::<Vec<_>>()
            .join("\n")
            + "\nnot json\n[1]\n",
    )
    .unwrap();
}

fn note(t: &str, tool: &str) -> Value {
    json!({"type": "user", "timestamp": t, "message": {"role": "user", "content": format!("<task-notification>\n<task-id>x</task-id>\n<tool-use-id>{tool}</tool-use-id>\n</task-notification>")}})
}

fn turn(t: &str, context: i64) -> Value {
    json!({"type": "assistant", "timestamp": t, "message": {"id": format!("w{t}"), "usage": {"cache_read_input_tokens": context, "cache_creation_input_tokens": 0}}})
}

fn wave(root: &Path) -> (PathBuf, PathBuf) {
    let proj = root.join("-diagram");
    let session = proj.join("s1");
    let run = session.join("subagents/workflows/wf_1");
    for (i, (read, written)) in [(0, 6178), (3462, 2716), (3462, 2716), (3462, 2716)]
        .iter()
        .enumerate()
    {
        agent(
            &run,
            &format!("w{i}"),
            &format!("2026-10-17T22:34:4{}.000Z", i + 1),
            *read,
            *written,
            &json!({"agentType": "claims-triage"}),
        );
    }
    std::fs::write(
        run.join("journal.jsonl"),
        json!({"type": "result", "agentId": "w3"}).to_string() + "\n",
    )
    .unwrap();
    let hand: Vec<String> = (0..4).map(|i| format!("toolu_h{i}")).collect();
    for (i, tid) in hand.iter().enumerate() {
        agent(
            &session.join("subagents"),
            &format!("h{i}"),
            &format!("2026-10-17T20:00:0{i}.000Z"),
            4443,
            2514,
            &json!({"agentType": "quote-check", "toolUseId": tid}),
        );
    }
    let mut main: Vec<Value> = hand.iter().map(|tid| json!({"type": "assistant", "timestamp": "2026-10-17T19:59:59.000Z", "message": {"id": "launch", "content": [{"type": "tool_use", "id": tid, "name": "Agent", "input": {"subagent_type": "quote-check"}}]}})).collect();
    main.extend([note("2026-10-17T20:01:00.000Z", "toolu_h0"), turn("2026-10-17T20:01:01.000Z", 400_000), note("2026-10-17T20:02:00.000Z", "toolu_h1"), turn("2026-10-17T20:02:01.000Z", 410_000), note("2026-10-17T20:03:00.000Z", "toolu_other"), turn("2026-10-17T20:03:01.000Z", 1), note("2026-10-17T22:34:44.500Z", "toolu_wf"), turn("2026-10-17T22:34:45.000Z", 930_000), json!({"type": "user", "timestamp": "2026-10-17T22:40:00.000Z", "message": {"content": [{"type": "text", "text": "plain"}]}}), json!({"type": "user", "timestamp": "2026-10-17T22:41:00.000Z", "message": {"content": 3}})]);
    main.insert(0, json!({"type": "assistant", "timestamp": "2026-10-17T19:00:00.000Z", "uuid": "u1", "message": {"content": [{"type": "text"}, {"type": "tool_use", "id": "z", "name": "Agent", "input": {}}]}}));
    std::fs::write(proj.join("s0.jsonl"), "").unwrap();
    std::fs::write(proj.join("s9.jsonl"), "").unwrap();
    std::fs::write(
        proj.join("s1.jsonl"),
        main.iter()
            .map(Value::to_string)
            .collect::<Vec<_>>()
            .join("\n")
            + "\n",
    )
    .unwrap();
    (proj, run)
}

#[test]
fn a_workflow_wave_against_the_last_hand_launched_one() {
    let (proj, run) = wave(&crate::checks::scratch("wave"));
    let out = report(&run);
    assert!(out.contains("WORKFLOW RUN wf_1 (s1): 4 agent(s)"));
    assert!(
        out.contains("read       0  written   6,178")
            && out.matches("read   3,462  written   2,716").count() == 3
    );
    assert!(out.contains("main-session wakes: 1, median context re-read 930k"));
    assert!(out.contains("LAST HAND-LAUNCHED WAVE: 4 quote-check in one message (-diagram/s1)"));
    assert!(out.contains("main-session wakes: 2, median context re-read 405k"));
    assert_eq!(newest_run(&proj), Some(run.clone()));
    let got = cli(
        &["--run".to_owned(), run.display().to_string()],
        Path::new("/nonexistent"),
    );
    assert_eq!(got.code, 0);
    let by_root = cli(
        &["--root".to_owned(), proj.display().to_string()],
        Path::new("/nonexistent"),
    );
    assert!(by_root.stdout.contains("wf_1"));
}

#[test]
fn nothing_to_measure() {
    let root = crate::checks::scratch("wave-none");
    let run = root.join("-diagram/s/subagents/workflows/wf_9");
    std::fs::create_dir_all(&run).unwrap();
    assert!(report(&run).contains("has no agent with a request yet"));
    agent(&run, "a", "2026-10-17T22:34:41.000Z", 1, 2, &json!({}));
    let out = report(&run);
    assert!(
        out.contains("no hand-launched wave of 4+ before it")
            && out.contains("main-session wakes: 0")
            && out.contains('?')
    );
    let none = cli(
        &["--root".to_owned(), root.join("none").display().to_string()],
        Path::new("/nonexistent"),
    );
    assert!(none.code == 1 && none.stdout.contains("no workflow run"));
    assert_eq!(super::commas(-1234), "-1,234");
    assert_eq!(newest_run(Path::new("/")), None);
}
