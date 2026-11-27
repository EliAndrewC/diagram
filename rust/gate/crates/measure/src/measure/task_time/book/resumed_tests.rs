//! A resumed agent's day (feature 451 T324, T345): a builder that stops with its background test still running, is resumed, stops
//! again and runs on with no start line, a span of its own from its first line there (451 T382); a plan review resumed for a second round. Each second's booking is worked by hand in the
//! comments, the blocking summing to the session's clock.

use std::collections::HashMap;

use serde_json::json;

use super::super::super::events::Event;
use super::tests::{at, booked_to, by_cat, line, post, pre};
use super::*;

fn agent(ev: &str, t: &str, aid: &str, kind: &str) -> Event {
    line(&json!({"t": at(t), "sid": "s", "ev": ev, "aid": aid, "agent": kind}))
}

fn turn(ev: &str, t: &str, extra: &serde_json::Value) -> Event {
    let mut e = line(&json!({"t": at(t), "sid": "s", "ev": ev}));
    e.extend(extra.as_object().unwrap().clone());
    e
}

/// The session dispatches builder B and waits on it from 00:20 to a notification at 04:00. B starts a background `make rust-test`
/// (00:30 to 02:00), reads, and STOPS at 01:00 with the test still running; it is resumed at 02:10, edits, stops at 02:40, and its own
/// lines run on from 03:00 with no start line (a start no log read holds), to a last stop at 03:30.
fn builder_day() -> (Vec<Event>, Vec<Event>) {
    let none = json!({});
    let test = json!({"make": "rust-test"});
    let stream = vec![
        turn("UserPromptSubmit", "00:00", &none),
        pre("00:10", "Agent", "a1", "", &none),
        post("00:11", "Agent", "a1", "", &json!({"aid": "B"})),
        agent("SubagentStart", "00:11", "B", "general-purpose"),
        turn(
            "Stop",
            "00:20",
            &json!({"inflight": [{"id": "B", "type": "subagent"}]}),
        ),
        pre("00:30", "Bash", "b1", "B", &test),
        post(
            "00:31",
            "Bash",
            "b1",
            "B",
            &json!({"make": "rust-test", "bg": "x1"}),
        ),
        pre("00:40", "Read", "r1", "B", &none),
        post("00:41", "Read", "r1", "B", &none),
        agent("SubagentStop", "01:00", "B", "general-purpose"),
        agent("SubagentStart", "02:10", "B", "general-purpose"),
        pre("02:20", "Edit", "e1", "B", &none),
        post("02:21", "Edit", "e1", "B", &none),
        agent("SubagentStop", "02:40", "B", "general-purpose"),
        pre("03:00", "Read", "r2", "B", &none),
        post("03:01", "Read", "r2", "B", &none),
        agent("SubagentStop", "03:30", "B", "general-purpose"),
        turn("UserPromptSubmit", "04:00", &json!({"gm": false})),
        turn("Stop", "04:10", &json!({"inflight": []})),
    ];
    let aside = vec![line(
        &json!({"t": at("02:00"), "sid": "s", "ev": "BgEnd", "id": "b1"}),
    )];
    (stream, aside)
}

/// T324, T345 and T382 together: each of the builder's three spans is the session's wait on it - the third opened by its own line
/// at 03:00, no start line logged - and the time between them is the builder STOPPED - waiting on its own test while that ran
/// (blocking as the test, 01:00 to 02:00), then on being resumed with nothing of its own in flight (02:00 to 02:10, and 02:40 to
/// 03:00 where no start line follows the stop) - never a model turn of its own.
#[test]
fn a_resumed_builder_is_booked_in_every_span_and_stopped_between_them() {
    let (stream, aside) = builder_day();
    let l = booked_to(
        &stream,
        &aside,
        &HashMap::new(),
        &[],
        (&at("00:00"), &at("04:10")),
    );
    let got = by_cat(&l);
    let want: HashMap<String, (f64, f64, f64)> = [
        ("main session: dispatching an agent", (11.0, 11.0, 0.0)),
        ("main session: writing its reply", (19.0, 19.0, 0.0)),
        // 00:11 to 00:30, the session waiting from 00:20
        (
            "builders: running a command (the model's turn)",
            (19.0, 10.0, 0.0),
        ),
        // the test's 90 s: its launch's 1 s in the builder's first span, and the 60 s the stopped builder waited on it
        ("tests", (90.0, 61.0, 1.0)),
        // 00:31 to 00:41 in the first span; 03:00 to 03:01 in the third, the one its own line opens
        ("builders: reading code", (11.0, 11.0, 0.0)),
        // 00:41 to 01:00, 02:21 to 02:40 and 03:01 to 03:30, each to a stop
        ("builders: writing its reply", (67.0, 67.0, 0.0)),
        // the second span: 02:10 to 02:21
        ("builders: writing code", (11.0, 11.0, 0.0)),
        // 02:00 to 02:10 and 02:40 to 03:00: stopped with nothing of its own in flight; a wait has no minutes
        (STOPPED, (0.0, 30.0, 0.0)),
        // 03:30 to 04:00: past the builder's last span
        (NOTHING_ENDED, (0.0, 30.0, 0.0)),
    ]
    .into_iter()
    .map(|(k, v)| (k.to_owned(), v))
    .collect();
    assert_eq!(got, want);
    let clock: f64 = got.values().map(|v| v.1).sum();
    assert!((clock - 250.0).abs() < 1e-6);
    // the builder's minutes are its three spans, 49 s, 30 s and 30 s, and it is one builder
    let key = ("451-x".to_owned(), "T1".to_owned());
    assert_eq!(l.builders[&key], (109.0, 1));
}

/// T324 alone: a plan review the session waits on returns at 01:00 and is resumed for a second round, 01:30 to 02:00. The wait is cut
/// at every span's edge: both rounds are the review's, and the time between them, with nothing in flight, is named so.
#[test]
fn a_wait_across_a_resumed_review_is_cut_at_every_span() {
    let none = json!({});
    let stream = vec![
        turn("UserPromptSubmit", "00:00", &none),
        pre("00:10", "Agent", "a1", "", &none),
        post("00:11", "Agent", "a1", "", &json!({"aid": "C"})),
        agent("SubagentStart", "00:11", "C", "spec-fidelity"),
        turn(
            "Stop",
            "00:20",
            &json!({"inflight": [{"id": "C", "type": "subagent"}]}),
        ),
        agent("SubagentStop", "01:00", "C", "spec-fidelity"),
        agent("SubagentStart", "01:30", "C", "spec-fidelity"),
        agent("SubagentStop", "02:00", "C", "spec-fidelity"),
        turn("UserPromptSubmit", "02:30", &json!({"gm": false})),
        turn("Stop", "02:40", &json!({"inflight": []})),
    ];
    let got = by_cat(&booked_to(
        &stream,
        &[],
        &HashMap::new(),
        &[],
        (&at("00:00"), &at("02:40")),
    ));
    // 49 s and 30 s of spans; the session waited through 40 s of the first and all of the second
    assert_eq!(got["plan review: agents"], (79.0, 70.0, 0.0));
    // 01:00 to 01:30 between the rounds and 02:00 to 02:30 after the last
    assert_eq!(got[NOTHING_ENDED], (0.0, 60.0, 0.0));
}

/// The session waits on builder B and a claims round R it dispatched beside it; B waits on a plan review K of its own (00:31 to
/// 00:50), is stopped from 01:00 to 02:10 with nothing of its own in flight, and R returns at 02:30, before B's last stop at 02:40.
/// The session's two dispatches carry the clue `blocks`.
fn beside_a_round(blocks: &str) -> Ledger {
    let none = json!({});
    let stream = vec![
        turn("UserPromptSubmit", "00:00", &none),
        pre("00:10", "Agent", "a1", "", &none),
        post(
            "00:11",
            "Agent",
            "a1",
            "",
            &json!({"aid": "B", "blocks": blocks}),
        ),
        agent("SubagentStart", "00:11", "B", "general-purpose"),
        pre("00:12", "Agent", "a2", "", &none),
        post(
            "00:13",
            "Agent",
            "a2",
            "",
            &json!({"aid": "R", "blocks": blocks}),
        ),
        agent("SubagentStart", "00:13", "R", "claims-triage"),
        turn(
            "Stop",
            "00:20",
            &json!({"inflight": [{"id": "B", "type": "subagent"}, {"id": "R", "type": "subagent"}]}),
        ),
        pre("00:30", "Agent", "a3", "B", &none),
        post("00:31", "Agent", "a3", "B", &json!({"aid": "K"})),
        agent("SubagentStart", "00:31", "K", "spec-fidelity"),
        agent("SubagentStop", "00:50", "K", "spec-fidelity"),
        agent("SubagentStop", "01:00", "B", "general-purpose"),
        agent("SubagentStart", "02:10", "B", "general-purpose"),
        agent("SubagentStop", "02:30", "R", "claims-triage"),
        agent("SubagentStop", "02:40", "B", "general-purpose"),
        turn("UserPromptSubmit", "03:00", &json!({"gm": false})),
        turn("Stop", "03:10", &json!({"inflight": []})),
    ];
    booked_to(
        &stream,
        &[],
        &HashMap::new(),
        &[],
        (&at("00:00"), &at("03:10")),
    )
}

/// T345's rank: a stopped builder with nothing of its own in flight is what a wait is on only where nothing else is. While B is
/// stopped the session's wait is on the claims round - though B, resumed later, ends last - and where both run, on B as before.
#[test]
fn a_wait_beside_a_stopped_builder_is_on_what_else_is_in_flight() {
    // no clue: both block the session's task
    let got = by_cat(&beside_a_round(""));
    // 01:00 to 02:10, the 70 s B was stopped
    assert_eq!(got["claims round: agents"], (137.0, 70.0, 0.0));
    // B's own spans: its dispatch to 00:31 (the session waiting from 00:20), its wait on its review, its replies to each stop
    assert_eq!(got["builders: dispatching an agent"], (20.0, 11.0, 0.0));
    assert_eq!(got["plan review: agents"], (19.0, 19.0, 0.0));
    assert_eq!(got["builders: writing its reply"], (40.0, 40.0, 0.0));
    assert!(!got.contains_key(STOPPED));
    // `Blocks: none` on both: nothing in flight blocks a task, and the one waited on is chosen the same way
    let l = beside_a_round("none");
    assert_eq!(l.free.get("claims round: agents"), Some(&70.0));
    assert_eq!(l.free.get("builders: writing its reply"), Some(&40.0));
    assert!(!l.free.contains_key(STOPPED));
}

/// T345's other shape: a start that follows a line of the builder's own, where no log read holds the stop between them. The time to
/// that start is the builder stopped too - 00:21 to 01:00 is no reply of its model, whose one reply is the 10 s to its stop.
#[test]
fn a_start_after_a_line_of_its_own_is_a_resumption() {
    let none = json!({});
    let stream = vec![
        agent("SubagentStart", "00:11", "B", "general-purpose"),
        pre("00:20", "Read", "r1", "B", &none),
        post("00:21", "Read", "r1", "B", &none),
        agent("SubagentStart", "01:00", "B", "general-purpose"),
        agent("SubagentStop", "01:10", "B", "general-purpose"),
    ];
    let got = by_cat(&booked_to(
        &stream,
        &[],
        &HashMap::new(),
        &[],
        (&at("00:00"), &at("01:10")),
    ));
    assert_eq!(got["builders: reading code"], (10.0, 0.0, 0.0));
    assert_eq!(got["builders: writing its reply"], (10.0, 0.0, 0.0));
}

/// 451 T512's own path is clipped to the builder's spans: of the session's wait on B, 00:11 to 03:30, its three spans' 109 s are B's
/// path and none of its stopped stretches (the test it waited on while stopped, 01:00 to 02:00, nor 02:00 to 02:10 and 02:40 to
/// 03:00) - a builder's own path never past its builder minutes (unclipped, the overnight window read T455 at 62.4 own-path minutes
/// against 20.5 builder minutes). Its edit's lines name a bundle's other task, T9: its machine minutes go there, its own path stays
/// its builder's own task's, as its builder minutes do (the overnight window's T428).
#[test]
fn a_builders_own_path_is_its_spans_not_its_stopped_stretches() {
    let (mut stream, aside) = builder_day();
    for e in stream.iter_mut().filter(|e| or_s(e, "id") == "e1") {
        e.insert("task".to_owned(), json!("T9"));
    }
    let l = booked_to(
        &stream,
        &aside,
        &HashMap::new(),
        &[],
        (&at("00:00"), &at("04:10")),
    );
    let key = ("451-x".to_owned(), "T1".to_owned());
    let mut own: HashMap<String, f64> = HashMap::new();
    for ((k, cat, _), s) in &l.own {
        assert_eq!(k, &key);
        *own.entry(cat.clone()).or_default() += s;
    }
    let want: HashMap<String, f64> = [
        ("builders: running a command (the model's turn)", 19.0),
        // the test's launch, 00:30 to 00:31, inside the first span; its run while B was stopped is no part of B's path
        ("tests", 1.0),
        ("builders: reading code", 11.0),
        ("builders: writing its reply", 67.0),
        ("builders: writing code", 11.0),
    ]
    .into_iter()
    .map(|(k, v)| (k.to_owned(), v))
    .collect();
    assert_eq!(own, want);
    assert!((own.values().sum::<f64>() - l.builders[&key].0).abs() < 1e-6);
    // beside it, its stopped stretches by what was in flight: its own test, 01:00 to 02:00, and nothing, 02:00 to 02:10 and 02:40 to
    // 03:00, all its own task's
    let mut stopped: HashMap<String, f64> = HashMap::new();
    for ((k, cat, _), s) in &l.stopped {
        assert_eq!(k, &key);
        *stopped.entry(cat.clone()).or_default() += s;
    }
    let want: HashMap<String, f64> = [("tests", 60.0), (STOPPED, 30.0)]
        .into_iter()
        .map(|(k, v)| (k.to_owned(), v))
        .collect();
    assert_eq!(stopped, want);
    let t9 = ("451-x".to_owned(), "T9".to_owned());
    assert!(l.cells.keys().any(|(k, _, _)| k == &t9));
}
