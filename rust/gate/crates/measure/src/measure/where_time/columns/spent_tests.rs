//! What was spent beside the critical path (feature 451 T10, plan D7; FR-005): two agents overlapping one wait of the main session,
//! the wait booked once on the critical path and each agent's span and tokens under its own task; a refused landing and a plan re-round
//! as rework - each through the command's own reading (`booked`, then `tables`, then `render`).

use std::collections::HashMap;
use std::path::Path;

use serde_json::{json, Value};

use super::super::super::feature_report::tests::put;
use super::super::{booked, render, tables};

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

/// An assistant row of a subagent's transcript: its message id and usage.
fn usage(t: &str, id: &str, (fresh, cached, created, out): (u64, u64, u64, u64)) -> String {
    json!({"type": "assistant", "timestamp": at(t), "message": {"id": id, "usage": {
        "input_tokens": fresh, "cache_read_input_tokens": cached, "cache_creation_input_tokens": created, "output_tokens": out}}})
    .to_string()
        + "\n"
}

/// Feature 901's log (`own`), feature 900's (`other`) and the session's transcripts (`files`, under `home/-proj`), read with no SINCE to
/// 08:30, booked by start (`named`, as the command books) or by the mark, and rendered for `order`.
fn report(
    tag: &str,
    own: &[Value],
    other: &[Value],
    files: &[(&str, String)],
    named: bool,
    order: &[&str],
) -> String {
    report_since(tag, (own, other), files, (named, ""), order)
}

/// [`report`], its window opening at `since`.
fn report_since(
    tag: &str,
    (own, other): (&[Value], &[Value]),
    files: &[(&str, String)],
    (named, since): (bool, &str),
    order: &[&str],
) -> String {
    let d = crate::checks::scratch(tag);
    let ok = std::process::Command::new("git")
        .args(["init", "-q"])
        .current_dir(&d)
        .status()
        .unwrap();
    assert!(ok.success());
    put(&d, "specs/901-s/tasks.md", "- [ ] T05\n- [ ] T06\n");
    put(&d, ".git/l7r-events/901-s.jsonl", &jsonl(own));
    put(&d, ".git/l7r-events/900-o.jsonl", &jsonl(other));
    for (rel, text) in files {
        put(&d, &format!("home/-proj/{rel}"), text);
    }
    let starts = [(0.0, "T05".to_owned())];
    let (events, _, _, booking) = booked(
        &d,
        "901-s",
        (since, &at("08:30:00")),
        &starts,
        &d.join("home"),
        Path::new("/nonexistent"),
    )
    .unwrap();
    let inputs = HashMap::new();
    let t = tables(&events, &starts, named.then_some(&inputs), "901", &booking).unwrap();
    let order: Vec<String> = order.iter().map(|k| (*k).to_owned()).collect();
    render(&t, &order)
}

/// The window: a builder (a1, task T05, 20 min) and a plan review (a2, task T06, 10 min) launched in one turn and overlapping its wait;
/// a second plan review of T06 (a3) whose start sits only in feature 900's log; a landing of T05 and T06 refused (`landed` false), and
/// one that exited 3 with its ticks standing (`landed` true), which is no rework.
fn window() -> (Vec<Value>, Vec<Value>, Vec<(&'static str, String)>) {
    let own = vec![
        line("08:00:00", "UserPromptSubmit", &json!({"gm": true})),
        line(
            "08:00:05",
            "PreToolUse",
            &json!({"tool": "Agent", "id": "toolu_1", "agent": "general-purpose", "task": "T05"}),
        ),
        line(
            "08:00:06",
            "SubagentStart",
            &json!({"aid": "a1", "agent": "general-purpose", "task": "T05"}),
        ),
        line(
            "08:00:06",
            "PostToolUse",
            &json!({"tool": "Agent", "id": "toolu_1", "aid": "a1"}),
        ),
        line(
            "08:00:10",
            "PreToolUse",
            &json!({"tool": "Agent", "id": "toolu_2", "agent": "spec-fidelity", "task": "T06"}),
        ),
        line(
            "08:00:11",
            "SubagentStart",
            &json!({"aid": "a2", "agent": "spec-fidelity", "task": "T06"}),
        ),
        line(
            "08:00:11",
            "PostToolUse",
            &json!({"tool": "Agent", "id": "toolu_2", "aid": "a2"}),
        ),
        line(
            "08:00:20",
            "Stop",
            &json!({"inflight": [{"id": "a1", "type": "subagent"}, {"id": "a2", "type": "subagent"}]}),
        ),
        line(
            "08:10:11",
            "SubagentStop",
            &json!({"aid": "a2", "agent": "spec-fidelity", "task": "T06",
            "tok": {"in": 0, "cached": 4000, "created": 1000, "out": 1500}}),
        ),
        line(
            "08:20:06",
            "SubagentStop",
            &json!({"aid": "a1", "agent": "general-purpose", "task": "T05",
            "tok": {"in": 1, "cached": 1, "created": 1, "out": 1}}),
        ),
        line("08:20:10", "UserPromptSubmit", &json!({"gm": false})),
        json!({"ev": "Phase", "src": "land", "sid": "s", "step": "end", "make": "land", "t": at("08:20:40"), "t0": at("08:20:20"),
               "t1": at("08:20:40"), "code": 1, "task": "T05", "tasks": ["T05", "T06"], "landed": false}),
        json!({"ev": "Phase", "src": "land", "sid": "s", "step": "end", "make": "land", "t": at("08:20:55"), "t0": at("08:20:45"),
               "t1": at("08:20:55"), "code": 3, "task": "T05", "tasks": ["T05"], "landed": true}),
        line("08:21:00", "Stop", &json!({})),
        line(
            "08:25:00",
            "SubagentStop",
            &json!({"aid": "a3", "agent": "spec-fidelity", "task": "T06"}),
        ),
        line("08:25:30", "UserPromptSubmit", &json!({"gm": true})),
        line("08:26:00", "Stop", &json!({})),
    ];
    let other = vec![line(
        "08:22:00",
        "SubagentStart",
        &json!({"aid": "a3", "agent": "spec-fidelity", "task": "T06"}),
    )];
    // a1's transcript: m1 written twice (counted once), m2, and m3 after the window's end (not counted); a2 has none, so its stop's
    // `tok` stands; a3 has neither
    let a1 = usage("08:01:00", "m1", (10, 1000, 500, 200))
        + &usage("08:01:00", "m1", (10, 1000, 500, 200))
        + &usage("08:19:00", "m2", (5, 2000, 0, 300))
        + &usage("08:40:00", "m3", (0, 0, 0, 99_999));
    (own, other, vec![("s/subagents/agent-a1.jsonl", a1)])
}

/// `text` holds `want`, the text shown where it does not.
fn has(text: &str, want: &str) {
    assert!(text.contains(want), "{want}\nnot in:\n{text}");
}

#[test]
fn two_agents_over_one_wait_are_booked_once_and_spent_under_their_tasks() {
    let (own, other, files) = window();
    let text = report(
        "measure-spent-agents",
        &own,
        &other,
        &files,
        true,
        &["T05", "T06"],
    );
    // the critical path: the session's 26 minutes, the 19:50 wait over both agents booked once
    has(&text, "| all | 26 | ");
    // each agent under the task its launch names, its tokens from its transcript, else its stop's `tok`, else none counted
    has(
        &text,
        "| T05 | 1 | 20 | 3.5 | 0.5 | 1 | 0 | general-purpose 1 |",
    );
    has(
        &text,
        "| T06 | 2 | 13 | 5.0 | 1.5 | 1 | 1 | spec-fidelity 2 |",
    );
    has(&text, "| all | 3 | 33 | 8.5 | 2.0 | 1 | 1 | |");
    has(
        &text,
        "| T05 | a1 | general-purpose | 08:00 | 20 | 3.5 | 0.5 |",
    );
    has(&text, "| T06 | a3 | spec-fidelity | 08:22 | 3 | - | - |");
    has(
        &text,
        "the critical path: 26 min of wall clock; beside it, the agents' own minutes summed: 33 min over 3 agents, 8.5k tokens in and \
         2.0k out (1 with no count); rework: 1 refused landing, 1 plan re-round",
    );
}

#[test]
fn by_the_mark_an_agent_goes_to_the_task_active_at_its_launch() {
    let (own, other, files) = window();
    let text = report(
        "measure-spent-mark",
        &own,
        &other,
        &files,
        false,
        &["T05", "T06"],
    );
    has(
        &text,
        "| T05 | 3 | 33 | 8.5 | 2.0 | 1 | 1 | spec-fidelity 2, general-purpose 1 |",
    );
    // a task with a refused landing and no agent has its row; no agent counted, the sum reads zero
    has(&text, "| T06 | 0 | 0 | - | - | 1 | 0 |  |");
}

#[test]
fn a_landing_naming_no_tasks_and_a_row_naming_no_message_are_read_as_far_as_they_go() {
    let end = |extra: Value| {
        let mut v = json!({"ev": "Phase", "src": "land", "step": "end", "t": at("08:00:00"), "landed": false});
        v.as_object_mut()
            .unwrap()
            .extend(extra.as_object().unwrap().clone());
        v.as_object().unwrap().clone()
    };
    let aside = [
        end(json!({"task": "T07"})),
        end(json!({})),
        end(json!({"t": at("09:00:00")})),
        end(json!({"landed": true})),
    ];
    assert_eq!(
        super::spent::refused(&aside, &at("08:30:00")),
        [vec!["T07".to_owned()], vec!["-".to_owned()]]
    );
    let mut tokens = super::spent::Tokens::default();
    let rows = "{\"usage\": no json}\n".to_owned()
        + &json!({"timestamp": at("08:00:00"), "message": {"usage": {"output_tokens": 5}}})
            .to_string()
        + "\n"
        + &usage("08:00:00", "m1", (0, 0, 0, 7));
    tokens.read(
        Path::new("subagents/agent-a9.jsonl"),
        &rows,
        (0.0, f64::MAX),
    );
    tokens.read(Path::new("subagents/notes.txt"), &rows, (0.0, f64::MAX));
    let sums = tokens.sums();
    assert_eq!((sums.len(), sums["a9"].out), (1, 7.0));
}

/// An agent's minutes are its spans inside the window: one started before `since` cut at it, one stopped after the window's end cut
/// there, one started twice with no stop between counted once (the union of its spans), never twice, and one started after the window's
/// end, its span empty, not counted.
#[test]
fn an_agents_minutes_are_its_spans_inside_the_window_counted_once() {
    let start = |t: &str, aid: &str| {
        line(
            t,
            "SubagentStart",
            &json!({"aid": aid, "agent": "general-purpose", "task": "T05"}),
        )
    };
    let stop = |t: &str, aid: &str| line(t, "SubagentStop", &json!({"aid": aid, "task": "T05"}));
    let own = [
        start("07:50:00", "a4"),
        line("08:00:00", "UserPromptSubmit", &json!({"gm": true})),
        stop("08:05:00", "a4"),
        start("08:06:00", "a6"),
        start("08:07:00", "a6"),
        stop("08:10:00", "a6"),
        start("08:28:00", "a5"),
        line("08:29:00", "Stop", &json!({})),
        start("08:35:00", "a7"),
        stop("08:40:00", "a5"),
    ];
    let text = report_since(
        "measure-spent-window",
        (&own, &[]),
        &[],
        (true, &at("08:00:00")),
        &["T05"],
    );
    has(
        &text,
        "| T05 | 3 | 11 | - | - | 0 | 0 | general-purpose 3 |",
    );
    has(&text, "| T05 | a4 | general-purpose | 08:00 | 5 | - | - |");
    has(&text, "| T05 | a6 | general-purpose | 08:06 | 4 | - | - |");
    has(&text, "| T05 | a5 | general-purpose | 08:28 | 2 | - | - |");
    // a7, started after the window, has no row
    assert_eq!(text.matches("| a7 |").count(), 0);
}
