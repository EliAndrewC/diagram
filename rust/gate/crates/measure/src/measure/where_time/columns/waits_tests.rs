//! A wait between turns booked to the run in flight (feature 451 T09, plan D3; FR-002): a background `make land`, a builder agent, and a
//! turn whose `Stop` sits only in another feature's log - each through the command's own reading (`booked`, then `tables`).

use std::path::Path;

use serde_json::{json, Value};

use super::super::super::feature_report::tests::put;
use super::super::{booked, row, tables};
use super::{ts, Runs};

fn at(hms: &str) -> String {
    format!("2026-11-01T{hms}Z")
}

fn line(t: &str, ev: &str, extra: &Value) -> Value {
    let mut v = json!({"t": at(t), "sid": "s", "ev": ev});
    v.as_object_mut()
        .unwrap()
        .extend(extra.as_object().unwrap().clone());
    v
}

fn jsonl(lines: &[Value]) -> String {
    lines.iter().map(|l| l.to_string() + "\n").collect()
}

/// A scratch repository holding feature 901's log (`own`), feature 900's (`other`) and the session's transcripts (`files`, under
/// `home/-proj`), read through `booked` to `until` and booked by `tables`: the one task row's seconds by column.
fn book(
    tag: &str,
    own: &[Value],
    other: &[Value],
    files: &[(&str, String)],
    until: &str,
) -> (Vec<(String, f64)>, Runs) {
    let d = crate::checks::scratch(tag);
    let ok = std::process::Command::new("git")
        .args(["init", "-q"])
        .current_dir(&d)
        .status()
        .unwrap();
    assert!(ok.success());
    put(&d, "specs/901-s/tasks.md", "- [ ] T05\n");
    put(&d, ".git/l7r-events/901-s.jsonl", &jsonl(own));
    if !other.is_empty() {
        put(&d, ".git/l7r-events/900-o.jsonl", &jsonl(other));
    }
    for (rel, text) in files {
        put(&d, &format!("home/-proj/{rel}"), text);
    }
    let (events, _, runs, booking) = booked(
        &d,
        "901-s",
        ("", &at(until)),
        &[],
        &d.join("home"),
        Path::new("/nonexistent"),
    )
    .unwrap();
    let t = tables(&events, &[], None, "901", &booking).unwrap();
    let mut got: Vec<(String, f64)> = row(&t.time, "-").unwrap().items().to_vec();
    got.retain(|(_, v)| v.abs() > 1e-9);
    got.sort_by(|a, b| a.0.cmp(&b.0));
    (got, runs)
}

fn secs(pairs: &[(&str, f64)]) -> Vec<(String, f64)> {
    let mut v: Vec<(String, f64)> = pairs.iter().map(|(k, s)| ((*k).to_owned(), *s)).collect();
    v.sort_by(|a, b| a.0.cmp(&b.0));
    v
}

/// The landing's launch: a background `make land`, its notice queued at 08:10:00 (the main transcript's enqueue row), its gate phase
/// 08:02-08:06 holding a minute of compile.
fn landing() -> (Vec<Value>, String) {
    let bash = json!({"tool": "Bash", "id": "toolu_l", "make": "land", "cat": "land"});
    let mut post = bash.clone();
    post["bg"] = json!("b1");
    let lines = vec![
        line("08:00:00", "UserPromptSubmit", &json!({"gm": true})),
        line("08:00:00", "PreToolUse", &bash),
        line("08:00:01", "PostToolUse", &post),
        json!({"ev": "Phase", "src": "land", "sid": "s", "step": "gate", "make": "land", "t": at("08:06:00"), "t0": at("08:02:00"), "t1": at("08:06:00")}),
        json!({"ev": "Phase", "src": "rust", "sid": "s", "step": "build", "make": "land", "t": at("08:03:00"), "t0": at("08:02:00"), "t1": at("08:03:00")}),
        json!({"t": at("08:10:05"), "sid": "s", "ev": "BgEnd", "id": "toolu_l", "bg": "b1", "status": "completed", "exit": 0, "make": "land", "t0": at("08:00:00")}),
        line("08:10:05", "UserPromptSubmit", &json!({"gm": false})),
        line("08:11:00", "Stop", &json!({})),
    ];
    let queued = json!({"type": "queue-operation", "operation": "enqueue", "timestamp": at("08:10:00"), "content": "<task-notification>\n<task-id>b1</task-id>\n<tool-use-id>toolu_l</tool-use-id>\n</task-notification>"});
    (lines, format!("{queued}\n"))
}

/// The wait over a background `make land` (08:00:30 to its notice's prompt at 08:10:05) goes to land, its gate and its compile split
/// out as a call's are; only the five seconds after the notice was queued stay waiting on work.
#[test]
fn a_wait_over_a_background_landing_is_booked_to_it() {
    let (mut own, queued) = landing();
    own.insert(
        3,
        line(
            "08:00:30",
            "Stop",
            &json!({"inflight": [{"id": "b1", "type": "shell", "make": "land"}]}),
        ),
    );
    let (got, _) = book(
        "measure-wait-land",
        &own,
        &[],
        &[("s.jsonl", queued)],
        "08:11:00",
    );
    let want = secs(&[
        ("model", 29.0 + 55.0),
        ("land", 1.0 + 570.0 - 180.0 - 60.0),
        ("gate", 180.0),
        ("compile", 60.0),
        ("waiting on work", 5.0),
    ]);
    assert_eq!(got, want);
}

/// The wait over a builder (08:00:10 to its stop at 08:20:00) goes to the builder - by its kind, `waiting: general-purpose`, the column
/// a foreground wait on it has - over the monitor in flight beside it, which holds the two seconds after the builder stopped; the
/// builder's own lines inside the wait do not cut it. The
/// builder's background `make quick` ends at its transcript's `queued_command` row (08:12:00), not open to the window's end.
#[test]
fn a_wait_over_a_builder_is_booked_to_it() {
    let agent = json!({"tool": "Agent", "id": "toolu_g", "cat": "other subagent", "agent": "general-purpose"});
    let mut post = agent.clone();
    post["aid"] = json!("a1");
    let quick =
        json!({"tool": "Bash", "id": "toolu_q", "make": "quick", "cat": "tests", "by": "a1"});
    let mut quick_post = quick.clone();
    quick_post["bg"] = json!("b9");
    let own = [
        line("08:00:00", "UserPromptSubmit", &json!({"gm": true})),
        line("08:00:00", "PreToolUse", &agent),
        line("08:00:01", "PostToolUse", &post),
        line(
            "08:00:01",
            "SubagentStart",
            &json!({"aid": "a1", "agent": "general-purpose"}),
        ),
        line(
            "08:00:10",
            "Stop",
            &json!({"inflight": [{"id": "m1", "type": "monitor"}, {"id": "a1", "type": "subagent"}]}),
        ),
        line("08:05:00", "PreToolUse", &quick),
        line("08:05:01", "PostToolUse", &quick_post),
        line(
            "08:20:00",
            "SubagentStop",
            &json!({"aid": "a1", "agent": ""}),
        ),
        line("08:20:02", "UserPromptSubmit", &json!({"gm": false})),
        line("08:21:00", "Stop", &json!({})),
    ];
    let note = json!({"type": "attachment", "agentId": "a1", "timestamp": at("08:12:00"), "attachment": {"type": "queued_command", "timestamp": at("08:12:00"), "prompt": "<task-notification>\n<task-id>b9</task-id>\n<tool-use-id>toolu_q</tool-use-id>\n<status>completed</status>\n</task-notification>"}});
    let files = [("s/subagents/agent-a1.jsonl", format!("{note}\n"))];
    let (got, runs) = book("measure-wait-builder", &own, &[], &files, "08:21:00");
    let quick = runs.runs.iter().find(|r| r.id == "toolu_q").unwrap();
    assert_eq!(
        (quick.t1, quick.open),
        (ts(&at("08:12:00")).unwrap(), false)
    );
    let want = secs(&[
        ("model", 9.0 + 58.0),
        ("other subagent", 1.0 + 1190.0),
        ("background run", 2.0),
    ]);
    assert_eq!(got, want);
}

/// The session's turn lines are filed in whichever feature's log was active (T08's finding): here the `Stop` that opened the wait over
/// the landing sits only in feature 900's log, and without it the wait was booked model. Feature 900's own turn (its prompt and stop
/// both in its log, no line of 901 between) is booked `another feature` from its prompt to the session's next line of 901's (08:30-08:50), the wait after its
/// stop among it: the session was working on 900, neither thinking for 901
/// nor waiting on it (T09's plan review, 2026-11-21: the two hours of 449's turns had been booked 451's waits).
#[test]
fn a_stop_in_another_features_log_opens_the_wait() {
    let (mut own, queued) = landing();
    own.push(line("08:50:00", "UserPromptSubmit", &json!({"gm": true})));
    own.push(line(
        "08:50:10",
        "PreToolUse",
        &json!({"tool": "Read", "id": "toolu_r", "cat": "read"}),
    ));
    own.push(line(
        "08:50:11",
        "PostToolUse",
        &json!({"tool": "Read", "id": "toolu_r", "cat": "read"}),
    ));
    own.push(line("08:51:00", "Stop", &json!({})));
    let other = [
        line(
            "08:00:30",
            "Stop",
            &json!({"inflight": [{"id": "b1", "type": "shell", "make": "land"}]}),
        ),
        line("08:30:00", "UserPromptSubmit", &json!({"gm": true})),
        line("08:40:00", "Stop", &json!({})),
    ];
    let (got, _) = book(
        "measure-wait-other-log",
        &own,
        &other,
        &[("s.jsonl", queued)],
        "08:52:00",
    );
    let want = secs(&[
        ("model", 29.0 + 55.0 + 59.0),
        ("land", 1.0 + 570.0 - 180.0 - 60.0),
        ("gate", 180.0),
        ("compile", 60.0),
        ("waiting on work", 5.0),
        ("the GM", 19.0 * 60.0),
        ("another feature", 20.0 * 60.0),
        ("tools", 1.0),
    ]);
    assert_eq!(got, want);
}
