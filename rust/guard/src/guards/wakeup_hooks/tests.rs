//! The decider over fixture transcripts (`tests/hooks/test-wakeup-hooks.sh`, replayed through the shim, is the verdict).

use serde_json::{json, Value};

use super::decide;
use crate::protocol::{Answer, Event};
use crate::shared::session::Session;

const WAKE: &str = "Continue feature 262.";
const LOOP: &str = "/loop check the deploy";

fn tool(name: &str, input: &Value) -> Value {
    json!({"type": "assistant", "message": {"content": [{"type": "tool_use", "name": name, "input": input}]}})
}

fn loop_command() -> Value {
    json!({"type": "user", "message": {"content": "<command-name>/loop</command-name>"}})
}

fn wake(prompt: &str) -> Value {
    tool("ScheduleWakeup", &json!({"prompt": prompt}))
}

fn transcript(tag: &str, rows: &[Value]) -> crate::shared::tempdir::Held<String> {
    crate::shared::log::quiet();
    let dir = crate::shared::tempdir::TempDir::new(&format!("guard-wakeup-{tag}"));
    let path = dir.join("transcript.jsonl");
    let lines: Vec<String> = rows.iter().map(ToString::to_string).collect();
    std::fs::write(&path, lines.join("\n") + "\n").unwrap();
    let held = path.to_string_lossy().into_owned();
    dir.hold(held)
}

fn call(tr: &str, input: &Value) -> Vec<Answer> {
    let e = Event {
        name: "PreToolUse".to_owned(),
        input: json!({"tool_name": "ScheduleWakeup", "transcript_path": tr, "tool_input": input}),
    };
    decide(&e, &Session::from_input(&e.input))
}

fn turn_end(tr: &str, crons: &Value) -> Vec<Answer> {
    let e = Event {
        name: "Stop".to_owned(),
        input: json!({"transcript_path": tr, "session_crons": crons}),
    };
    decide(&e, &Session::from_input(&e.input))
}

fn cron(id: &str, prompt: &str) -> Value {
    json!({"id": id, "schedule": "51 20 * * *", "prompt": prompt})
}

fn refused(got: &[Answer], words: &str) -> bool {
    matches!(got, [Answer::Refuse(t)] if t.contains(words))
}

#[test]
fn a_call_outside_a_live_loop_is_refused() {
    let plain = transcript(
        "plain",
        &[
            wake(WAKE),
            tool("Read", &json!({"file_path": "/loop"})),
            json!({"type": "user", "note": "/loop"}),
        ],
    );
    assert!(refused(
        &call(&plain, &json!({"prompt": WAKE})),
        "outside /loop"
    ));
    assert!(call(&plain, &json!({"stop": true})).is_empty());
    let stopped = transcript(
        "stopped",
        &[
            loop_command(),
            tool("ScheduleWakeup", &json!({"stop": true})),
        ],
    );
    assert!(refused(
        &call(&stopped, &json!({"prompt": LOOP})),
        "outside /loop"
    ));
}

#[test]
fn a_live_loops_own_prompt_passes_and_a_fallback_inside_it_does_not() {
    let live = transcript("live", &[loop_command()]);
    assert!(call(&live, &json!({"prompt": LOOP})).is_empty());
    assert!(call(&live, &json!({"prompt": "/loop"})).is_empty());
    assert!(call(&live, &json!({"prompt": "<<autonomous-loop-dynamic>>"})).is_empty());
    assert!(refused(
        &call(&live, &json!({"prompt": WAKE})),
        "OWN prompt"
    ));
    let skill = transcript("skill", &[tool("Skill", &json!({"skill": "loop"}))]);
    assert!(call(&skill, &json!({"prompt": LOOP})).is_empty());
    let blocks = json!({"type": "user", "message": {"content": [{"text": "<command-name>/loop</command-name>"}]}});
    let listed = transcript("listed", &[blocks]);
    assert!(call(&listed, &json!({"prompt": LOOP})).is_empty());
}

#[test]
fn the_call_fails_closed_and_the_turn_end_open() {
    assert!(refused(
        &call("/no/such", &json!({"prompt": WAKE})),
        "could not establish"
    ));
    assert!(call("/no/such", &json!({"stop": true})).is_empty());
    let dir = crate::shared::tempdir::TempDir::new("guard-wakeup-broken");
    let path = dir.join("broken.jsonl");
    std::fs::write(&path, "[\"/loop x\"]\n{not json /loop\n").unwrap();
    let broken = path.to_string_lossy().into_owned();
    assert!(refused(
        &call(&broken, &json!({"prompt": WAKE})),
        "could not establish"
    ));
    assert!(turn_end("/no/such", &json!([cron("a", WAKE)])).is_empty());
    let skipped = dir.join("skipped.jsonl");
    std::fs::write(&skipped, "{not json /loop\nunrelated\n").unwrap();
    assert!(refused(
        &call(&skipped.to_string_lossy(), &json!({"prompt": WAKE})),
        "outside /loop"
    ));
}

#[test]
fn other_tools_pass() {
    let e = Event {
        name: "PreToolUse".to_owned(),
        input: json!({"tool_name": "Bash", "tool_input": {"command": "ls"}}),
    };
    assert!(decide(&e, &Session::from_input(&e.input)).is_empty());
    let none = transcript("none", &[]);
    let bare = Event {
        name: "PreToolUse".to_owned(),
        input: json!({"transcript_path": none, "tool_input": {"prompt": WAKE}}),
    };
    assert!(decide(&bare, &Session::from_input(&bare.input)).is_empty());
}

#[test]
fn a_stale_wakeup_blocks_every_turn_end_and_a_reminder_never() {
    let plain = transcript("stale", &[wake(WAKE)]);
    let got = turn_end(
        &plain,
        &json!([cron("rem", "Remind the GM."), cron("e1f0", WAKE), {"prompt": WAKE}]),
    );
    assert!(refused(
        &got,
        "CronDelete e1f0      (51 20 * * *: Continue feature 262.)"
    ));
    assert!(!refused(&got, "rem"));
    assert!(turn_end(&plain, &json!([cron("rem", "Remind the GM.")])).is_empty());
    assert!(turn_end(&plain, &json!([])).is_empty());
    let live = transcript("stale-live", &[loop_command(), wake(LOOP)]);
    assert!(turn_end(&live, &json!([cron("own", LOOP)])).is_empty());
    let empty = transcript("no-crons", &[tool("ScheduleWakeup", &json!({}))]);
    let e = Event {
        name: "Stop".to_owned(),
        input: json!({"transcript_path": empty}),
    };
    assert!(decide(&e, &Session::from_input(&e.input)).is_empty());
}
