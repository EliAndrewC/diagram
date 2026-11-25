//! One task's worked day: a main session that reads, edits, runs a test, dispatches a builder and waits; the builder runs a test in the
//! background and waits on it with a wait loop, dispatches a plan review and waits on it, then reads; the session runs cargo. Each
//! second's booking is worked by hand in the comments, the blocking summing to the session's 410-second clock.

use std::collections::HashMap;

use serde_json::{json, Value};

use super::super::super::events::{ts, Event};
use super::super::super::where_time::columns::{self, Window};
use super::*;

fn at(ms: &str) -> String {
    format!("2026-11-25T10:{ms}Z")
}

fn line(v: &Value) -> Event {
    let mut e = v.as_object().unwrap().clone();
    e.insert("feature".to_owned(), json!("451-x"));
    e.entry("task").or_insert(json!("T1"));
    e
}

fn pre(t: &str, tool: &str, id: &str, by: &str, extra: &Value) -> Event {
    let mut v = json!({"t": at(t), "sid": "s", "ev": "PreToolUse", "tool": tool, "id": id});
    if !by.is_empty() {
        v["by"] = json!(by);
    }
    for (k, x) in extra.as_object().unwrap() {
        v[k] = x.clone();
    }
    line(&v)
}

fn post(t: &str, tool: &str, id: &str, by: &str, extra: &Value) -> Event {
    let mut e = pre(t, tool, id, by, extra);
    e.insert("ev".to_owned(), json!("PostToolUse"));
    e
}

/// The day's lines, the set-aside lines, and the commands.
#[must_use]
pub fn day() -> (Vec<Event>, Vec<Event>, HashMap<String, String>) {
    let none = json!({});
    let stream = vec![
        line(&json!({"t": at("00:00"), "sid": "s", "ev": "UserPromptSubmit"})),
        pre("00:10", "Read", "r1", "", &none),
        post("00:11", "Read", "r1", "", &none),
        pre("00:20", "Edit", "e1", "", &none),
        post("00:21", "Edit", "e1", "", &none),
        pre("00:30", "Bash", "b1", "", &json!({"make": "static"})),
        post("01:30", "Bash", "b1", "", &json!({"make": "static"})),
        pre("01:40", "Agent", "a1", "", &none),
        post("01:41", "Agent", "a1", "", &json!({"aid": "B"})),
        line(
            &json!({"t": at("01:41"), "sid": "s", "ev": "SubagentStart", "aid": "B", "agent": "general-purpose"}),
        ),
        line(
            &json!({"t": at("01:50"), "sid": "s", "ev": "Stop", "inflight": [{"id": "B", "type": "subagent"}]}),
        ),
        pre("02:00", "Bash", "b2", "B", &json!({"make": "rust-test"})),
        post(
            "02:01",
            "Bash",
            "b2",
            "B",
            &json!({"make": "rust-test", "bg": "x2"}),
        ),
        pre("02:10", "Bash", "b3", "B", &none),
        post("04:00", "Bash", "b3", "B", &none),
        pre("04:10", "Agent", "a2", "B", &none),
        post("04:11", "Agent", "a2", "B", &json!({"aid": "C"})),
        line(
            &json!({"t": at("04:11"), "sid": "s", "ev": "SubagentStart", "aid": "C", "agent": "spec-fidelity"}),
        ),
        line(
            &json!({"t": at("05:11"), "sid": "s", "ev": "SubagentStop", "aid": "C", "agent": "spec-fidelity"}),
        ),
        pre("05:20", "Read", "r2", "B", &none),
        post("05:21", "Read", "r2", "B", &none),
        line(
            &json!({"t": at("06:00"), "sid": "s", "ev": "SubagentStop", "aid": "B", "agent": "general-purpose"}),
        ),
        line(&json!({"t": at("06:05"), "sid": "s", "ev": "UserPromptSubmit", "gm": false})),
        pre("06:10", "Bash", "b4", "", &none),
        post("06:40", "Bash", "b4", "", &none),
        line(&json!({"t": at("06:50"), "sid": "s", "ev": "Stop", "inflight": []})),
    ];
    let aside = vec![
        line(
            &json!({"t": at("01:00"), "ev": "Phase", "src": "rust", "step": "build", "t0": at("00:40"), "t1": at("01:00"), "make": "static", "sid": "s"}),
        ),
        line(&json!({"t": at("04:00"), "sid": "s", "ev": "BgEnd", "id": "b2"})),
    ];
    let commands = HashMap::from([
        ("b1".to_owned(), "make static".to_owned()),
        (
            "b3".to_owned(),
            "until [ -s /tmp/x ]; do sleep 5; done".to_owned(),
        ),
        ("b4".to_owned(), "cargo test -p x".to_owned()),
    ]);
    (stream, aside, commands)
}

/// The day booked.
///
/// # Panics
///
/// Where the fixture's lines do not read or book.
#[must_use]
#[expect(clippy::implicit_hasher, reason = "the map `World` holds")]
pub fn booked(
    stream: &[Event],
    aside: &[Event],
    commands: &HashMap<String, String>,
    pages: &[Page],
) -> Ledger {
    booked_to(stream, aside, commands, pages, (&at("00:00"), &at("06:50")))
}

/// The day booked to `until`.
fn booked_to(
    stream: &[Event],
    aside: &[Event],
    commands: &HashMap<String, String>,
    pages: &[Page],
    (from, until): (&str, &str),
) -> Ledger {
    let end = ts(until).unwrap();
    let (times, ids) = (HashMap::new(), HashMap::new());
    let w = Window {
        end,
        enqueued: &times,
        stopped: &ids,
        queued: &times,
        goal: "help",
    };
    let runs = columns::runs(stream, aside, &[], &w).unwrap();
    let agents: Vec<Event> = stream
        .iter()
        .filter(|e| is(e, "ev", "SubagentStart") || is(e, "ev", "SubagentStop"))
        .cloned()
        .collect();
    let flight = columns::flight(&runs, &agents, stream, end).unwrap();
    let world = World {
        stream,
        runs: &runs,
        commands,
        agents: &flight.agents,
        pages,
        window: (ts(from).unwrap(), end),
    };
    book(&world).unwrap()
}

/// Seconds by category: (minutes, blocking, foreground blocking).
#[must_use]
pub fn by_cat(l: &Ledger) -> HashMap<String, (f64, f64, f64)> {
    let mut out: HashMap<String, (f64, f64, f64)> = HashMap::new();
    for ((_, cat, _), c) in &l.cells {
        let e = out.entry(cat.clone()).or_default();
        e.0 += c.min;
        e.1 += c.block;
        e.2 += c.fg;
    }
    for v in out.values_mut() {
        *v = (
            (v.0 * 1000.0).round() / 1000.0,
            (v.1 * 1000.0).round() / 1000.0,
            (v.2 * 1000.0).round() / 1000.0,
        );
    }
    out
}

#[test]
fn every_second_of_the_day_is_booked_by_what_it_was() {
    let (stream, aside, commands) = day();
    let got = by_cat(&booked(&stream, &aside, &commands, &[]));
    let want: HashMap<String, (f64, f64, f64)> = [
        // the main session's turns by the tool each ends in, its tools' own run with them
        ("main session: reading code", (11.0, 11.0, 0.0)),
        ("main session: writing code", (10.0, 10.0, 0.0)),
        (
            "main session: running a command (the model's turn)",
            (14.0, 14.0, 0.0),
        ),
        ("main session: dispatching an agent", (11.0, 11.0, 0.0)),
        ("main session: writing its reply", (19.0, 19.0, 0.0)),
        // `make static` in the foreground: its 20 s build phase compile, the rest tests
        ("compile", (20.0, 20.0, 20.0)),
        // and the builder's background `make rust-test`, 120 s: blocking from its launch's 1 s and the 110 s the wait loop held
        ("tests", (160.0, 151.0, 41.0)),
        // the builder: from its start, its turns; while the main session waited, from 01:50
        (
            "builders: running a command (the model's turn)",
            (28.0, 19.0, 0.0),
        ),
        ("builders: dispatching an agent", (11.0, 11.0, 0.0)),
        ("builders: reading code", (10.0, 10.0, 0.0)),
        ("builders: writing its reply", (39.0, 39.0, 0.0)),
        // the builder's wait loop: 110 s held open, no work; its blocking is the test it waited on
        (program::WAIT, (110.0, 0.0, 0.0)),
        // the plan review the builder waited on in its turn
        ("plan review: agents", (60.0, 60.0, 0.0)),
        (NOTHING, (0.0, 5.0, 0.0)),
        ("cargo, called directly", (30.0, 30.0, 30.0)),
    ]
    .into_iter()
    .map(|(k, v)| (k.to_owned(), v))
    .collect();
    assert_eq!(got, want);
    let clock: f64 = got.values().map(|v| v.1).sum();
    // the blocking sums to the session's clock
    assert!((clock - 410.0).abs() < 1e-6);
}

#[test]
#[expect(
    clippy::float_cmp,
    reason = "seconds summed from whole-second times, exact"
)]
fn a_monitor_wait_goes_to_the_page_session_and_the_gm_is_named() {
    let (stream, aside, commands) = day();
    // the GM answered the stop, not a notice: the wait is his
    let mut gm = stream.clone();
    gm[22].insert("gm".to_owned(), json!(true));
    let got = by_cat(&booked(&gm, &aside, &commands, &[]));
    assert_eq!(got["the GM"], (0.0, 255.0, 0.0));
    assert!(!got.contains_key(NOTHING));
    // its minutes stand; nobody waited on it
    assert_eq!(got["plan review: agents"], (60.0, 0.0, 0.0));
    // the stop waited on a monitor alone: a page session running is what held it, under the page's own task
    let mut mon = stream;
    mon[10].insert(
        "inflight".to_owned(),
        json!([{"id": "m", "type": "monitor"}]),
    );
    let page = Page {
        t0: ts(&at("01:00")).unwrap(),
        t1: ts(&at("06:20")).unwrap(),
        key: ("454-y".to_owned(), "T3".to_owned()),
        sid: "pg".to_owned(),
    };
    // the page session's own lines: a session of its own, whose turns and runs are its phase's, nobody's clock
    for (t, ev, tool) in [
        ("02:00", "UserPromptSubmit", ""),
        ("02:10", "PreToolUse", "Bash"),
        ("03:10", "PostToolUse", "Bash"),
        ("03:20", "Stop", ""),
    ] {
        mon.push(line(
            &json!({"t": at(t), "sid": "pg", "ev": ev, "tool": tool, "id": "pb"}),
        ));
    }
    mon.sort_by(|a, b| {
        ts(a["t"].as_str().unwrap())
            .unwrap()
            .total_cmp(&ts(b["t"].as_str().unwrap()).unwrap())
    });
    let l = booked(&mon, &aside, &commands, &[page.clone()]);
    let got = by_cat(&l);
    assert_eq!(got[PAGES], (320.0, 255.0, 0.0));
    // the page session's turn is not the session's
    assert_eq!(
        got["main session: running a command (the model's turn)"],
        (14.0, 14.0, 0.0)
    );
    assert!(!got.contains_key(UNREAD), "nor its run");
    assert_eq!(
        l.cells[&(page.key, PAGES.to_owned(), String::new())].block,
        255.0
    );
    // no page session running: the monitor alone, named
    let alone = by_cat(&booked(&mon, &aside, &commands, &[]));
    assert_eq!(alone[MONITOR], (0.0, 255.0, 0.0));
}

/// A run of the given bucket and targets, its id `id`.
fn run(bucket: &'static str, makes: &[&str], id: &str) -> Run {
    Run {
        id: id.to_owned(),
        t0: 0.0,
        t1: 1.0,
        sid: "s".to_owned(),
        by: String::new(),
        bg_id: String::new(),
        makes: makes.iter().map(|m| (*m).to_owned()).collect(),
        bucket,
        task: "T1".to_owned(),
        bg: false,
        open: false,
        split: columns::Split::default(),
    }
}

#[test]
fn the_kinds_and_the_runs_are_named() {
    for (kind, want) in [
        ("claims-triage", Some("claims round: agents")),
        ("impl-drift", Some("claims round: agents")),
        ("modal-form", Some(RECORD)),
        ("modal-triage", Some(RECORD)),
        ("round-arbiter", Some("arbiter: agents")),
        ("spec-fidelity-verify", Some("plan review: agents")),
        ("glyph-check", Some("map and building reviews: agents")),
        (
            "escalation-check",
            Some("the GM's filter: agents (escalation-check)"),
        ),
        ("research-pass", Some(PAGES)),
        (
            "work-budget",
            Some("other review agents (work-budget, message-check)"),
        ),
        ("general-purpose", None),
    ] {
        assert_eq!(review_cat(kind), want, "{kind}");
    }
    assert_eq!(
        tool_cat("builders", "Monitor"),
        "builders: other tools (Monitor)"
    );
    let none = HashMap::new();
    for (bucket, makes, want) in [
        (
            "review",
            &["decide"][..],
            ("plan review: commands", "make decide"),
        ),
        (
            "review",
            &["claims-owed", "land"][..],
            ("claims round: commands", "make claims-owed"),
        ),
        (
            "review",
            &["arbiter-bundle"][..],
            ("arbiter: commands", "make arbiter-bundle"),
        ),
        (
            "review",
            &["check-bundle"][..],
            ("record and pop-up checks: commands", "make check-bundle"),
        ),
        (
            "review",
            &["review-cost"][..],
            ("review: other commands", "make review-cost"),
        ),
        (
            "docs",
            &["record"][..],
            ("record builds and docs", "make record"),
        ),
        ("land", &["land"][..], ("landing", "make land")),
        // generating maps is its own category (the GM's list), whatever bucket the guard's table gives the target
        ("tests", &["hamlet"][..], (MAPS, "make hamlet")),
        ("gate", &["cohort"][..], (MAPS, "make cohort")),
        // a check the table leaves unbooked that runs tests books to them
        (
            "other",
            &["crate-checks"][..],
            ("tests", "make crate-checks"),
        ),
        (
            "other",
            &["source-pages"][..],
            (BOOKED_ELSEWHERE, "make source-pages"),
        ),
        ("other", &[][..], (UNREAD, "a command no transcript holds")),
    ] {
        assert_eq!(
            run_cat(&run(bucket, makes, "z"), &none),
            (want.0.to_owned(), want.1.to_owned())
        );
    }
    assert_eq!(phase_cat("docs"), "record builds and docs");
    assert_eq!(phase_cat("review"), PAGES);
}

#[test]
#[expect(
    clippy::too_many_lines,
    reason = "one worked day: its lines and its hand-worked sums read together"
)]
fn the_edges_of_a_day_are_booked() {
    let none = json!({});
    let at11 = |ms: &str| format!("2026-11-25T11:{ms}Z");
    let page_wait = "until grep -q '^ALL DONE' /d/.git/page-sessions/run-1.log; do sleep 30; done";
    let stream = vec![
        // a line of a kind the booking does not read
        line(&json!({"t": at("00:00"), "sid": "s", "ev": "SessionStart"})),
        line(&json!({"t": at("00:00"), "sid": "s", "ev": "UserPromptSubmit"})),
        // a call that starts and ends in one instant: no time between its lines
        pre("00:02", "Read", "r0", "", &none),
        post("00:02", "Read", "r0", "", &none),
        pre("00:05", "Agent", "a1", "", &none),
        post("00:06", "Agent", "a1", "", &json!({"aid": "B"})),
        line(
            &json!({"t": at("00:06"), "sid": "s", "ev": "SubagentStart", "aid": "B", "agent": "general-purpose"}),
        ),
        // the builder's last line: it never stops, so its span runs to the window's end with no line of its
        pre("00:07", "Read", "rb", "B", &none),
        post("00:08", "Read", "rb", "B", &none),
        // the session's own background wait on the page queue
        pre("00:10", "Bash", "m1", "", &none),
        post("00:11", "Bash", "m1", "", &json!({"bg": "x1"})),
        // a stop naming nothing in flight: every one the session owns, the builder ending last
        line(&json!({"t": at("00:20"), "sid": "s", "ev": "Stop"})),
        // a notice under no task
        line(
            &json!({"t": at("03:10"), "sid": "s", "ev": "UserPromptSubmit", "gm": false, "task": ""}),
        ),
        pre("03:20", "Bash", "m2", "", &none),
        post("03:21", "Bash", "m2", "", &json!({"bg": "x2"})),
        // a stop naming the background wait loop: its blocking goes to the page session it waited on
        line(
            &json!({"t": at("03:30"), "sid": "s", "ev": "Stop", "inflight": [{"id": "x2", "type": "shell"}]}),
        ),
        line(&json!({"t": at("05:30"), "sid": "s", "ev": "UserPromptSubmit", "gm": false})),
        // over an hour with nothing open and no stop: idle
        line(
            &json!({"t": at11("10:00"), "sid": "s", "ev": "PreToolUse", "tool": "Read", "id": "r9"}),
        ),
        line(
            &json!({"t": at11("10:01"), "sid": "s", "ev": "PostToolUse", "tool": "Read", "id": "r9"}),
        ),
        line(&json!({"t": at11("10:10"), "sid": "s", "ev": "Stop", "inflight": []})),
        // a stop naming a builder-style wait loop: nothing under it, its own 40 s are the loop's
        line(&json!({"t": at11("11:00"), "sid": "s", "ev": "UserPromptSubmit", "gm": false})),
        line(
            &json!({"t": at11("11:10"), "sid": "s", "ev": "PreToolUse", "tool": "Bash", "id": "m3"}),
        ),
        line(
            &json!({"t": at11("11:11"), "sid": "s", "ev": "PostToolUse", "tool": "Bash", "id": "m3", "bg": "x3"}),
        ),
        line(
            &json!({"t": at11("11:20"), "sid": "s", "ev": "Stop", "inflight": [{"id": "x3", "type": "shell"}]}),
        ),
        line(&json!({"t": at11("13:00"), "sid": "s", "ev": "UserPromptSubmit", "gm": false})),
        line(&json!({"t": at11("13:10"), "sid": "s", "ev": "Stop", "inflight": []})),
        // the GM answers over an hour later: away
        line(&json!({"t": "2026-11-25T12:20:00Z", "sid": "s", "ev": "UserPromptSubmit"})),
    ];
    let aside = vec![
        line(&json!({"t": at("03:00"), "sid": "s", "ev": "BgEnd", "id": "m1"})),
        line(&json!({"t": at("05:00"), "sid": "s", "ev": "BgEnd", "id": "m2"})),
        line(&json!({"t": at11("12:00"), "sid": "s", "ev": "BgEnd", "id": "m3"})),
    ];
    let commands = HashMap::from([
        ("m1".to_owned(), page_wait.to_owned()),
        ("m2".to_owned(), page_wait.to_owned()),
        (
            "m3".to_owned(),
            "until [ -s /tmp/x ]; do sleep 5; done".to_owned(),
        ),
    ]);
    let page = Page {
        t0: ts(&at("03:00")).unwrap(),
        t1: ts(&at("04:30")).unwrap(),
        key: ("451-x".to_owned(), "T2".to_owned()),
        sid: "pg".to_owned(),
    };
    let l = booked_to(
        &stream,
        &aside,
        &commands,
        &[page.clone()],
        (&at("00:00"), "2026-11-25T12:30:00Z"),
    );
    let got = by_cat(&l);
    let want: HashMap<String, (f64, f64, f64)> = [
        // 00:00-00:02 and the hour-late read's 1 s
        ("main session: reading code", (3.0, 3.0, 0.0)),
        ("main session: dispatching an agent", (4.0, 4.0, 0.0)),
        (
            "main session: running a command (the model's turn)",
            (24.0, 24.0, 0.0),
        ),
        ("main session: writing its reply", (46.0, 46.0, 0.0)),
        // the builder's two lines, before anybody waited on it
        ("builders: reading code", (2.0, 0.0, 0.0)),
        // the first stop's 170 s and each wait loop's launch second: the builder ends last, and no line of its covers them
        (UNLINED, (0.0, 173.0, 0.0)),
        // the wait loops held open 170 s and 100 s; their blocking is the page session's hour, then the loop's own 30 s
        (program::PAGE_WAIT, (270.0, 0.0, 0.0)),
        (PAGES, (90.0, 60.0, 0.0)),
        // the builder-style loop held open 50 s; blocking, the page loop's own 30 s and this loop's 40 s
        (program::WAIT, (50.0, 70.0, 0.0)),
        // 05:00-05:30, 11:10:10-11:11:00 and 11:12:00-11:13:00
        (NOTHING, (0.0, 140.0, 0.0)),
        // 05:30 to 11:10:00, over the hour's cap: blocking, never minutes
        ("idle (over an hour)", (0.0, 3870.0, 0.0)),
        ("the GM away", (0.0, 4010.0, 0.0)),
    ]
    .into_iter()
    .map(|(k, v)| (k.to_owned(), v))
    .collect();
    assert_eq!(got, want);
    // every second of the session's clock, 10:00:00 to 12:20:00, is booked once
    let clock: f64 = got.values().map(|v| v.1).sum();
    assert!((clock - 8400.0).abs() < 1e-6);
    // from 03:10 the first page-queue wait (00:10-03:00) is before the window: one run of the label counted, not two
    let late = booked_to(
        &stream,
        &aside,
        &commands,
        &[page],
        (&at("03:10"), "2026-11-25T12:30:00Z"),
    );
    let waits: usize = late
        .runs
        .iter()
        .filter(|((_, label), _)| label == "a wait loop on a page session")
        .map(|(_, n)| n)
        .sum();
    assert_eq!(waits, 1);
    // the notice under no task keys its segment to `-`
    assert!(l.cells.keys().any(|k| k.0 .1 == "-"));
}

#[test]
fn a_wait_past_the_depth_bound_is_booked_to_its_fallback() {
    let runs = Runs::default();
    let commands = HashMap::new();
    let world = World {
        stream: &[],
        runs: &runs,
        commands: &commands,
        agents: &[],
        pages: &[],
        window: (0.0, 10.0),
    };
    let ix = Ix::new(&world);
    let key = ("451-x".to_owned(), "T1".to_owned());
    let seg = Seg {
        t0: 0.0,
        t1: 4.0,
        key: key.clone(),
        what: What::Wait(Vec::new(), NOTHING),
    };
    let mut l = Ledger::default();
    ix.book_seg(&mut l, &seg, (1.0, 3.0), 8);
    let c = &l.cells[&(key, NOTHING.to_owned(), String::new())];
    assert!((c.block - 2.0).abs() < 1e-9 && c.min.abs() < 1e-9);
}

#[test]
fn a_command_books_what_it_runs_not_what_it_mentions() {
    // a run its log line names no target of, whose command runs one the table books: booked by the table, as a logged one is
    // and one the table leaves unbooked, listed by name
    let cmd = HashMap::from([
        ("y".to_owned(), "cd /c && make rust-test CRATE=x".to_owned()),
        (
            "u".to_owned(),
            "cd /c && ap(){ make apply-edits FROM=x; }; ap a".to_owned(),
        ),
        ("v".to_owned(), "make -s reserve KIND=registry".to_owned()),
    ]);
    for (id, want) in [
        ("y", ("tests", "make rust-test")),
        ("u", (BOOKED_ELSEWHERE, "make apply-edits")),
        ("v", (BOOKED_ELSEWHERE, "make reserve")),
    ] {
        assert_eq!(
            run_cat(&run("other", &[], id), &cmd),
            (want.0.to_owned(), want.1.to_owned())
        );
    }
}
