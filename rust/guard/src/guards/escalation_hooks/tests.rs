//! The decider over a fixture clone, the ledger tool stubbed by shell snippets (`tests/hooks/test-escalation-hooks.sh`, replayed through the shim, runs the real one).

use std::path::{Path, PathBuf};

use serde_json::{json, Value};

use super::{
    classify, cli, decide, filtered_since_gm, judge, judge_ask, read_state, run_cli, unnamed, Ctx,
};
use crate::protocol::{Answer, Event};
use crate::shared::session::Session;

fn world(tag: &str) -> crate::shared::tempdir::Held<PathBuf> {
    crate::shared::log::quiet();
    let d = crate::shared::tempdir::TempDir::new(&format!("guard-esc-{tag}"));
    std::fs::create_dir_all(d.join(".git")).unwrap();
    std::fs::create_dir_all(d.join("specs/432-x")).unwrap();
    let held = d.canonicalize().unwrap();
    d.hold(held)
}

fn ctx(d: &Path, disposed: bool) -> Ctx<'static> {
    Ctx {
        tree: d.to_path_buf(),
        python: "sh",
        count_code: "echo 7",
        disposed_code: if disposed { "exit 0" } else { "exit 1" },
    }
}

fn agent(kind: &str, prompt: &str, d: &Path, c: &Ctx) -> Vec<Answer> {
    let e = Event {
        name: "PreToolUse".to_owned(),
        input: json!({"tool_name": "Agent", "tool_input": {"subagent_type": kind, "prompt": prompt}}),
    };
    judge(&e, &Session::from_input(&e.input), d, c)
}

fn stop_with(input: &Value, d: &Path, c: &Ctx) -> Vec<Answer> {
    let e = Event {
        name: "Stop".to_owned(),
        input: input.clone(),
    };
    judge(&e, &Session::from_input(&e.input), d, c)
}

fn stop(d: &Path, c: &Ctx) -> Vec<Answer> {
    stop_with(&json!({"session_id": "t"}), d, c)
}

fn refused(got: &[Answer], words: &str) -> bool {
    matches!(got, [Answer::Refuse(t)] if t.contains(words))
}

fn armed(d: &Path) -> String {
    read_state(d)
        .get("armed_by")
        .and_then(Value::as_str)
        .unwrap_or("")
        .to_owned()
}

fn transcript(d: &Path, rows: &[Value]) -> String {
    let path = d.join("tr.jsonl");
    let lines: Vec<String> = rows.iter().map(ToString::to_string).collect();
    std::fs::write(&path, lines.join("\n") + "\n").unwrap();
    path.to_string_lossy().into_owned()
}

fn gm(at: &str) -> Value {
    json!({"type": "user", "timestamp": at, "message": {"content": "please do it"}})
}

fn filter_dispatch() -> Value {
    json!({"type": "assistant", "message": {"content": [{"type": "tool_use", "name": "Agent", "input": {"subagent_type": "escalation-check"}}]}})
}

#[test]
fn a_review_arms_the_filter_disarms_and_the_refusal_comes_once() {
    let d = world("arm");
    let c = ctx(&d, false);
    assert!(
        matches!(&agent("settlement-review", "go", &d, &c)[..], [Answer::Notice(t)] if t.contains("escalation-check"))
    );
    assert_eq!(armed(&d), "settlement-review");
    assert_eq!(
        read_state(&d).get("ledger_rows").and_then(Value::as_str),
        Some("7")
    );
    assert!(refused(
        &stop(&d, &c),
        "FINDINGS UNFILTERED: settlement-review"
    ));
    assert!(stop(&d, &c).is_empty());
    assert!(agent("escalation-check", "draft", &d, &c).is_empty());
    assert_eq!(armed(&d), "");
    agent("building-review", "go", &d, &c);
    assert!(agent(
        "size-audit",
        "x ESCALATION_OK=\"nothing relayed here\"",
        &d,
        &c
    )
    .is_empty());
    assert_eq!(armed(&d), "");
    assert!(agent("quote-check", "x", &d, &c).is_empty());
    let bash = Event {
        name: "PreToolUse".to_owned(),
        input: json!({"tool_name": "Bash"}),
    };
    assert!(judge(&bash, &Session::from_input(&bash.input), &d, &c).is_empty());
}

#[test]
fn a_disposed_review_owes_nothing_and_a_failed_count_is_zero() {
    let d = world("disposed");
    let c = ctx(&d, true);
    agent("settlement-review", "go", &d, &c);
    assert!(stop(&d, &c).is_empty());
    assert_eq!(armed(&d), "");
    let failing = Ctx {
        count_code: "exit 3",
        ..ctx(&d, false)
    };
    agent("settlement-review", "go", &d, &failing);
    assert_eq!(
        read_state(&d).get("ledger_rows").and_then(Value::as_str),
        Some("0")
    );
}

#[test]
fn asks_and_offers_are_told_apart() {
    let (asks, offers) = classify("Should I go on?\nDo the thing.\n```\nshall I?\n```\n> should I?\nI can revert it.\nWhat do you think?\n`should I` is named\n\"should I\"");
    assert_eq!(asks, ["Should I go on?", "What do you think?"]);
    assert_eq!(offers, ["I can revert it."]);
    assert_eq!(classify("Is it done?").0.len(), 0);
}

#[test]
fn a_question_owes_the_filter_once_and_a_dispatch_since_the_gm_answers_it() {
    let d = world("ask");
    let c = ctx(&d, false);
    let tr = transcript(&d, &[gm("2026-11-08T01:00:00Z")]);
    let ask = json!({"transcript_path": tr, "last_assistant_message": "Should I go on?", "cwd": d});
    assert!(refused(&stop_with(&ask, &d, &c), "QUESTION UNFILTERED"));
    assert!(stop_with(&ask, &d, &c).is_empty());
    let offer =
        json!({"transcript_path": tr, "last_assistant_message": "I can revert it.", "cwd": d});
    assert!(refused(&stop_with(&offer, &d, &c), "OFFER UNFILTERED"));
    let tr2 = transcript(&d, &[gm("x"), filter_dispatch()]);
    assert!(filtered_since_gm(&tr2));
    assert!(judge_ask(
        &json!({"transcript_path": tr2, "last_assistant_message": "Should I?"}),
        &d
    )
    .is_none());
    let tr3 = transcript(&d, &[filter_dispatch(), gm("x")]);
    assert!(!filtered_since_gm(&tr3));
    assert!(filtered_since_gm("/no/such"));
    assert!(judge_ask(&json!({"last_assistant_message": "All done."}), &d).is_none());
}

#[test]
fn a_kept_question_is_named_and_a_named_one_is_no_new_ask() {
    let d = world("kept");
    let c = ctx(&d, false);
    let row = json!({"kind": "question", "status": "kept", "kept": "2026-11-08T02:00:00Z", "question": "which road?"});
    let older = json!({"kind": "question", "status": "kept", "kept": "2026-11-08T00:00:00Z", "question": "old?"});
    let lines = format!(
        "{row}\nnot json\n{older}\n{}",
        json!({"kind": "question", "status": "kept", "reviewed": true})
    );
    std::fs::write(d.join("specs/432-x/gm-review.jsonl"), lines).unwrap();
    std::fs::write(d.join("specs/notes"), "x").unwrap();
    let tr = transcript(
        &d,
        &[
            gm("2026-11-08T01:00:00Z"),
            json!({"type": "assistant", "message": {"content": [{"type": "text", "text": "named 432#9"}]}}),
        ],
    );
    let input = json!({"transcript_path": tr, "last_assistant_message": "done", "cwd": d});
    assert_eq!(unnamed(&d, &input), ["432#0: which road?"]);
    assert!(refused(
        &stop_with(&input, &d, &c),
        "QUESTION KEPT, NOT NAMED"
    ));
    assert!(stop_with(&input, &d, &c).is_empty());
    let named = json!({"transcript_path": tr, "last_assistant_message": "Should I take 432#0, which road?", "cwd": d});
    assert!(unnamed(&d, &named).is_empty());
    assert!(judge_ask(&named, &d).is_none());
    assert!(unnamed(&d, &json!({"transcript_path": "/no/such"})).is_empty());
}

#[test]
fn a_gm_message_is_told_from_a_hook_echo() {
    let d = world("gm");
    let meta = json!({"type": "user", "isMeta": true, "message": {"content": "note"}});
    let echo = json!({"type": "user", "message": {"content": "<hook>"}});
    let blocks = json!({"type": "user", "timestamp": "b", "message": {"content": [{"type": "text", "text": "hi"}]}});
    let tool = json!({"type": "user", "message": {"content": [{"type": "tool_result"}]}});
    let bare = json!({"type": "user"});
    let tr = transcript(&d, &[blocks, meta, echo, tool, bare]);
    assert_eq!(super::gm_last_at(&tr), "b");
    let path = d.join("big.jsonl");
    let padding = "x".repeat(usize::try_from(super::CHUNK).unwrap());
    std::fs::write(
        &path,
        format!(
            "{}\n{}\n{}\n",
            gm("first"),
            json!({"pad": padding}),
            "tail not json"
        ),
    )
    .unwrap();
    assert_eq!(super::gm_last_at(&path.to_string_lossy()), "first");
    let single = d.join("one.jsonl");
    std::fs::write(&single, gm("only").to_string()).unwrap();
    assert_eq!(super::gm_last_at(&single.to_string_lossy()), "only");
}

#[test]
fn the_seams_take_only_a_fixture_path() {
    let d = world("cli");
    let args = |a: &[&str]| a.iter().map(|s| (*s).to_owned()).collect::<Vec<_>>();
    let at = d.to_string_lossy().into_owned();
    assert_eq!(run_cli(&args(&["arm", &at, "size-audit"]), &d).code, 0);
    assert_eq!(armed(&d), "size-audit");
    assert!(run_cli(&args(&["state"]), &d)
        .stdout
        .contains("armed by  size-audit"));
    assert!(run_cli(&args(&["state", &at]), &d)
        .stdout
        .contains("armed by  size-audit"));
    assert_eq!(run_cli(&args(&["disarm", &at]), &d).code, 0);
    assert_eq!(armed(&d), "");
    assert_eq!(run_cli(&args(&["arm", &at]), &d).code, 0);
    assert_eq!(armed(&d), "settlement-review");
    assert_eq!(run_cli(&args(&["arm", "/diagram"]), &d).code, 2);
    assert_eq!(run_cli(&args(&["other"]), &d).code, 0);
    assert!(run_cli(&args(&["state", "/"]), &d)
        .stdout
        .contains("<none>"));
    assert_eq!(cli(&args(&["other"])).code, 0);
}

#[test]
fn outside_a_repository_nothing_is_said() {
    let e = Event {
        name: "Stop".to_owned(),
        input: json!({}),
    };
    let c = Ctx {
        tree: "/".into(),
        python: "sh",
        count_code: "",
        disposed_code: "",
    };
    assert!(judge(&e, &Session::from_input(&e.input), Path::new("/"), &c).is_empty());
    let bash = Event {
        name: "PreToolUse".to_owned(),
        input: json!({"tool_name": "Bash"}),
    };
    assert!(decide(&bash, &Session::from_input(&bash.input)).is_empty());
}
