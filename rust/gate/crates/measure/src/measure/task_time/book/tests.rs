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
        // the stop's named work had ended 5 s before the next prompt woke it
        (NOTHING_ENDED, (0.0, 5.0, 0.0)),
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
        blocks: String::new(),
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
    // its brief names no task: waited on, blocking nothing (451 T243)
    let free = booked(&mon, &aside, &commands, &[page.clone()]);
    assert_eq!(by_cat(&free)[PAGES], (320.0, 0.0, 0.0));
    assert_eq!(free.free[PAGES], 255.0);
    // its brief's `Blocks: 454 T3`: the task it names, the feature's number read as the feature it opens
    let page = Page {
        blocks: "454 T3".to_owned(),
        ..page
    };
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
        // the builder's last line: it never stops, so its span ends here, at its last own call (451 T243)
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
        blocks: String::new(),
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
        // the wait loops held open 170 s and 100 s; the page session they waited on names no task in its brief, so its hour and the
        // second launching the second loop block nothing (below)
        (program::PAGE_WAIT, (270.0, 0.0, 0.0)),
        (PAGES, (90.0, 0.0, 0.0)),
        // blocking, the loops' own time with no page session running: the first stop's 160 s to 03:00 (the builder ended at 00:08),
        // the first and third loops' launch seconds, the second loop's 30 s after the page session, and the builder-style loop's 40 s
        (program::WAIT, (50.0, 232.0, 0.0)),
        // 05:00-05:30 (m2, which the 03:30 stop's loop waited on, ended at 05:00) and 11:12:00-11:13:00 (the loop x3 ended at 11:12)
        (NOTHING_ENDED, (0.0, 90.0, 0.0)),
        // 11:10:10-11:11:00: a stop naming nothing, then a notice woke it
        (NOTHING_WOKEN, (0.0, 50.0, 0.0)),
        // 05:30 to 11:10:00, over the hour's cap: blocking, never minutes
        ("idle (over an hour)", (0.0, 3870.0, 0.0)),
        ("the GM away", (0.0, 4010.0, 0.0)),
    ]
    .into_iter()
    .map(|(k, v)| (k.to_owned(), v))
    .collect();
    assert_eq!(got, want);
    // the page session's 60 s and the second loop's launch second, waited on, blocking no task; and 03:00-03:10, the first loop ended
    // and the page session running, untracked: a wait on what it blocks, nothing
    assert_eq!(l.free.get(PAGES).copied(), Some(61.0));
    assert_eq!(l.free.get(NOTHING_PAGES).copied(), Some(10.0));
    // every second of the session's clock, 10:00:00 to 12:20:00, is booked once: as blocking, or as waited on blocking nothing
    let clock: f64 = got.values().map(|v| v.1).sum::<f64>() + l.free.values().sum::<f64>();
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
        what: What::Wait(Vec::new(), NOTHING.to_owned()),
    };
    let mut l = Ledger::default();
    ix.book_seg(&mut l, &seg, (1.0, 3.0), Some(&seg.key), 8);
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

#[test]
fn a_wait_with_nothing_in_flight_is_classed_by_what_came_before_and_after_it() {
    let runs = Runs::default();
    let commands = HashMap::new();
    let key = ("451-x".to_owned(), "T1".to_owned());
    // a detached page session ran 4-6 s, nothing tracking it
    let pages = [Page {
        t0: 4.0,
        t1: 6.0,
        key: key.clone(),
        sid: "p".to_owned(),
        blocks: String::new(),
    }];
    let world = World {
        stream: &[],
        runs: &runs,
        commands: &commands,
        agents: &[],
        pages: &pages,
        window: (0.0, 10.0),
    };
    let ix = Ix::new(&world);
    let stop =
        line(&json!({"t": "2026-11-25T10:00:00Z", "sid": "s", "ev": "Stop", "inflight": []}));
    let next =
        |ev: &str| line(&json!({"t": "2026-11-25T10:00:10Z", "sid": "s", "ev": ev, "gm": false}));
    let class = |ev: &str, c: &str| {
        assert_eq!(
            ix.after_stop("s:s", &stop, &next(ev), 10.0),
            What::Wait(Vec::new(), c.to_owned())
        );
    };
    class("UserPromptSubmit", NOTHING_WOKEN);
    class("SessionStart", NOTHING_RESTART);
    // what the data does not yet class is named so, with the line that ended it
    class(
        "PreToolUse",
        "waiting: nothing in flight - unexplained, then a PreToolUse line",
    );
    // the gap's piece under the page session is the page session's class, the rest its own
    let seg = Seg {
        t0: 0.0,
        t1: 10.0,
        key: key.clone(),
        what: What::Wait(Vec::new(), NOTHING_WOKEN.to_owned()),
    };
    let mut l = Ledger::default();
    ix.book_seg(&mut l, &seg, (0.0, 10.0), Some(&seg.key), 0);
    let block = |c: &str| l.cells[&(key.clone(), c.to_owned(), String::new())].block;
    // the piece under the page session blocks what it blocks: its brief names nothing, so nothing (451 T243)
    assert!(
        (l.free[NOTHING_PAGES] - 2.0).abs() < 1e-9 && (block(NOTHING_WOKEN) - 8.0).abs() < 1e-9
    );
}

#[test]
#[expect(
    clippy::float_cmp,
    reason = "seconds summed from whole-second times, exact"
)]
fn a_page_session_blocks_only_the_task_its_brief_names() {
    let runs = Runs::default();
    let commands = HashMap::new();
    let key = ("451-x".to_owned(), "T1".to_owned());
    // a page session ran 0-10 s beside a plan review the session waited on, 0-4 s
    let page = Page {
        t0: 0.0,
        t1: 10.0,
        key: key.clone(),
        sid: "p".to_owned(),
        blocks: String::new(),
    };
    let agents = [columns::Agent {
        aid: "R".to_owned(),
        kind: "spec-fidelity".to_owned(),
        spans: vec![(0.0, 4.0)],
        ..columns::Agent::default()
    }];
    let seg = Seg {
        t0: 0.0,
        t1: 10.0,
        key: key.clone(),
        what: What::Wait(vec![Cand::Agent(0), Cand::Pages], MONITOR.to_owned()),
    };
    let booked = |pages: &[Page]| {
        let world = World {
            stream: &[],
            runs: &runs,
            commands: &commands,
            agents: &agents,
            pages,
            window: (0.0, 10.0),
        };
        let ix = Ix::new(&world);
        let mut l = Ledger::default();
        ix.book_seg(&mut l, &seg, (0.0, 10.0), Some(&seg.key), 0);
        l.at_once = at_once(&world, &ix, &[], &std::collections::HashSet::new());
        l
    };
    let block = |l: &Ledger, c: &str| {
        l.cells
            .iter()
            .filter(|((_, cat, _), _)| cat == c)
            .map(|(_, v)| v.block)
            .sum::<f64>()
    };
    // no `Blocks:` line: the page session blocks nothing though it ends last; the review blocks the waiter's task, 4 s
    let free = booked(std::slice::from_ref(&page));
    assert_eq!(
        (block(&free, "plan review: agents"), block(&free, PAGES)),
        (4.0, 0.0)
    );
    assert_eq!(free.free[PAGES], 6.0);
    // `Blocks: T7`: the page session blocks T7, ending last, so it holds the whole wait (the critical one)
    let named = booked(&[Page {
        blocks: "T7".to_owned(),
        ..page
    }]);
    assert_eq!(
        named.cells[&(
            ("451-x".to_owned(), "T7".to_owned()),
            PAGES.to_owned(),
            String::new()
        )]
            .block,
        10.0
    );
    assert!(named.free.is_empty());
    // two actors at once 0-4 s, one 4-10 s
    assert_eq!(named.at_once, [0.0, 6.0, 4.0, 0.0]);
}

/// The defaults where no clue is given, and a clue over each (451 T243, the GM 2026-11-25: "if we need to decide which of two
/// implementations to perform, and ... that research must complete prior to us beginning our implementation work, then that research is
/// blocking"; "it doesn't have to be 100% exact").
#[test]
#[expect(
    clippy::float_cmp,
    reason = "seconds summed from whole-second times, exact"
)]
fn blocking_follows_each_default_and_each_clue() {
    let commands = HashMap::new();
    let mut r = run("tests", &["rust-test"], "x9");
    (r.t0, r.t1, r.bg) = (0.0, 10.0, true);
    let mut r2 = run("tests", &["rust-test"], "x8");
    (r2.t0, r2.t1, r2.bg) = (0.0, 10.0, true);
    let runs = Runs {
        runs: vec![r, r2],
        ..Runs::default()
    };
    let agent = |aid: &str, kind: &str, task: &str| columns::Agent {
        aid: aid.to_owned(),
        kind: kind.to_owned(),
        task: task.to_owned(),
        spans: vec![(0.0, 10.0)],
        ..columns::Agent::default()
    };
    let agents = [
        agent("P", "research-pass", ""),
        agent("Q", "research-pass", ""),
        agent("C", "spec-fidelity", ""),
        agent("B", "general-purpose", "T8"),
    ];
    // the clues as the event log writes them: a dispatch's on its Agent lines, a command's on its call's
    let stream = [
        line(&json!({"ev": "PostToolUse", "tool": "Agent", "id": "q", "aid": "Q", "blocks": "T4"})),
        line(
            &json!({"ev": "PostToolUse", "tool": "Agent", "id": "c", "aid": "C", "blocks": "none"}),
        ),
        line(&json!({"ev": "PostToolUse", "tool": "Agent", "id": "b", "aid": "B"})),
        line(&json!({"ev": "PreToolUse", "tool": "Bash", "id": "x9", "blocks": "451 T9"})),
    ];
    let world = World {
        stream: &stream,
        runs: &runs,
        commands: &commands,
        agents: &agents,
        pages: &[],
        window: (0.0, 10.0),
    };
    let ix = Ix::new(&world);
    let waiter = ("451-x".to_owned(), "T1".to_owned());
    let mut l = Ledger::default();
    for c in [
        Cand::Agent(0),
        Cand::Agent(1),
        Cand::Agent(2),
        Cand::Agent(3),
        Cand::Run(0),
        Cand::Run(1),
    ] {
        ix.descend(&mut l, &[c], (0.0, 10.0), Some(&waiter), MONITOR, 0);
    }
    let at = |task: &str, cat: &str| {
        l.cells
            .get(&(
                ("451-x".to_owned(), task.to_owned()),
                cat.to_owned(),
                if cat == "tests" { "make rust-test" } else { "" }.to_owned(),
            ))
            .map_or(0.0, |c| c.block)
    };
    // a research pass with no clue blocks nothing; with `Blocks: T4`, T4
    assert_eq!((l.free[PAGES], at("T4", PAGES)), (10.0, 10.0));
    // a review agent `Blocks: none` blocks nothing
    assert_eq!(l.free["plan review: agents"], 10.0);
    // a builder its own task (its brief's), its time no line of its covers
    assert_eq!(at("T8", UNLINED), 10.0);
    // a background run `L7R_BLOCKS=451:T9` that task; with none, the waiter's
    assert_eq!((at("T9", "tests"), at("T1", "tests")), (10.0, 10.0));
    // and a clue's words read: none, a task alone under the work's own feature, a feature's number as the feature it opens
    let k = |f: &str, t: &str| Some((f.to_owned(), t.to_owned()));
    assert_eq!(ix.resolve("none", Some(&waiter), "451-x"), None);
    assert_eq!(ix.resolve("T5", None, "451-x"), k("451-x", "T5"));
    assert_eq!(ix.resolve("451 T5", None, ""), k("451-x", "T5"));
    assert_eq!(ix.resolve("999 T5", None, ""), k("999", "T5"));
}
