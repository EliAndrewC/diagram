//! Which run in flight each second of a wait goes to (feature 451 T09): by rank, the latest started breaking a tie.

use serde_json::{json, Value};

use super::super::super::super::events::{ts, Event};
use super::super::{Run, Runs, Split};
use super::*;

fn ev(v: &Value) -> Event {
    v.as_object().unwrap().clone()
}

fn run(id: &str, bg: &str, by: &str, bucket: &'static str, (t0, t1): (f64, f64)) -> Run {
    Run {
        id: id.to_owned(),
        t0,
        t1,
        sid: "s".to_owned(),
        by: by.to_owned(),
        bg_id: bg.to_owned(),
        makes: Vec::new(),
        bucket,
        task: "-".to_owned(),
        bg: !bg.is_empty(),
        open: false,
        split: Split::default(),
    }
}

fn the_flight() -> Flight {
    let runs = Runs {
        runs: vec![
            run("f", "", "", "tests", (0.0, 100.0)),
            run("p1", "b1", "", "other", (0.0, 100.0)),
            run("p2", "b2", "", "other", (5.0, 100.0)),
            run("t", "b3", "", "tests", (40.0, 60.0)),
            run("x", "b4", "a9", "land", (0.0, 100.0)),
        ],
        ..Runs::default()
    };
    let stream = [
        ev(
            &json!({"t": "2026-11-01T00:00:00Z", "ev": "SubagentStart", "sid": "s", "aid": "a1", "agent": "spec-fidelity"}),
        ),
        ev(&json!({"t": "2026-11-01T00:00:00Z", "ev": "SubagentStart", "sid": "s", "aid": "a2"})),
        ev(&json!({"t": "2026-11-01T00:00:00Z", "ev": "SubagentStop", "sid": "s", "aid": "a1"})),
    ];
    let mut f = flight(&runs, &stream, &stream, 1.0e10).unwrap();
    // the agents started at the epoch's 2026 second; set them inside the test's span
    for c in &mut f.fliers {
        if c.kind == "agent" {
            c.t0 = 20.0;
            c.t1 = if c.bucket == "plan review" {
                30.0
            } else {
                90.0
            };
        }
    }
    f
}

#[test]
fn each_second_goes_to_the_run_of_highest_rank() {
    let f = the_flight();
    let stop = ev(&json!({"inflight": [
        {"id": "b1"}, {"id": "b2"}, {"id": "b3"}, {"id": "a1"}, {"id": "a2"}, {"id": "m", "type": "monitor"}, {"id": "gone"}
    ]}));
    let got = f.book("s", Some(&stop), 10.0, 95.0);
    assert_eq!(
        got,
        vec![
            ("background run".to_owned(), "shell", 10.0),
            ("plan review".to_owned(), "agent", 10.0),
            ("other subagent".to_owned(), "agent", 10.0),
            ("tests".to_owned(), "shell", 20.0),
            ("other subagent".to_owned(), "agent", 30.0),
            ("background run".to_owned(), "shell", 5.0),
        ]
    );
    // of two Bash runs no column names, the later started (p2) holds the second
    let one = ev(&json!({"inflight": [{"id": "b1"}, {"id": "b2"}]}));
    assert_eq!(
        f.book("s", Some(&one), 10.0, 11.0),
        vec![("background run".to_owned(), "shell", 1.0)]
    );
    // a monitor alone; an empty list holds nothing
    let mon = ev(&json!({"inflight": [{"id": "m", "type": "monitor"}]}));
    assert_eq!(
        f.book("s", Some(&mon), 10.0, 11.0),
        vec![("background run".to_owned(), "monitor", 1.0)]
    );
    let none = ev(&json!({"inflight": []}));
    assert_eq!(
        f.book("s", Some(&none), 10.0, 11.0),
        vec![(UNBOOKED.to_owned(), "", 1.0)]
    );
}

/// A `Stop` written before `inflight`: the session's own runs whose span holds the wait, a subagent's own run (`x`, a landing) not
/// among them; a run's compile and a landing's gate split out of its seconds.
#[test]
fn a_stop_naming_none_books_the_sessions_own_runs() {
    let mut f = the_flight();
    f.fliers[2].split = Split {
        parts: vec![
            ("compile", vec![(41.0, 43.0)]),
            ("gate", vec![(50.0, 51.0)]),
        ],
    };
    let got = f.book("s", None, 40.0, 60.0);
    assert_eq!(
        got,
        vec![
            ("compile".to_owned(), "shell", 2.0),
            ("gate".to_owned(), "shell", 1.0),
            ("tests".to_owned(), "shell", 17.0),
        ]
    );
    assert_eq!(f.book("other", None, 40.0, 60.0)[0].0, UNBOOKED);
}

/// A resumed agent starts again under its id: each start opens its own span, to the first stop after it, its kind from the start that
/// names one; a line two logs hold is read once, and a start with no stop and no own call runs to the window's end.
#[test]
fn a_resumed_agent_is_in_flight_in_each_of_its_spans() {
    let at = |m: u32| format!("2026-11-01T08:{m:02}:00Z");
    let line = |m: u32, kind_of: &str, kind: &str| {
        ev(&json!({"t": at(m), "ev": kind_of, "sid": "s", "aid": "a1", "agent": kind}))
    };
    let agents = [
        line(0, "SubagentStart", "spec-fidelity"),
        line(10, "SubagentStop", ""),
        line(10, "SubagentStop", ""),
        line(20, "SubagentStart", ""),
        line(30, "SubagentStop", ""),
        line(40, "SubagentStart", ""),
    ];
    let t = |m: u32| ts(&at(m)).unwrap();
    // a2's lines sit in the logs too, but no line of the feature's names it: another feature's agent, never in flight here
    let mut all = agents.to_vec();
    all.push(ev(
        &json!({"t": at(0), "ev": "SubagentStart", "sid": "s", "aid": "a2"}),
    ));
    let f = flight(&Runs::default(), &all, &agents, t(50)).unwrap();
    assert_eq!(f.fliers.len(), 3);
    let stop = ev(&json!({"inflight": [{"id": "a1", "type": "subagent"}]}));
    assert_eq!(
        f.book("s", Some(&stop), t(5), t(45)),
        vec![
            ("plan review".to_owned(), "agent", 300.0),
            (UNBOOKED.to_owned(), "", 600.0),
            ("plan review".to_owned(), "agent", 600.0),
            (UNBOOKED.to_owned(), "", 600.0),
            ("plan review".to_owned(), "agent", 300.0),
        ]
    );
}

/// A start no stop follows ends at the agent's last own call before its next start, or the window's end where it made none: an agent
/// cut off (its stop in no log read) is not in flight to the window's end (451 T243: on 2026-11-25 eight such agents held `make
/// task-time`'s "Working at once" at three or more for all 1,440 minutes of a day).
#[test]
fn an_unstopped_agent_ends_at_its_last_own_call() {
    let at = |m: u32| format!("2026-11-01T08:{m:02}:00Z");
    let t = |m: u32| ts(&at(m)).unwrap();
    let start = |m: u32, aid: &str| {
        ev(
            &json!({"t": at(m), "ev": "SubagentStart", "sid": "s", "aid": aid, "agent": "general-purpose"}),
        )
    };
    let call = |m: u32, aid: &str| {
        ev(&json!({"t": at(m), "ev": "PreToolUse", "sid": "s", "by": aid, "tool": "Read"}))
    };
    let lines = [
        start(0, "a1"),
        call(5, "a1"),
        call(12, "a1"),
        start(20, "a1"),
        call(25, "a1"),
        start(30, "a2"),
    ];
    let agents: Vec<Event> = lines
        .iter()
        .filter(|e| is(e, "ev", "SubagentStart"))
        .cloned()
        .collect();
    let f = flight(&Runs::default(), &agents, &lines, t(50)).unwrap();
    let spans: Vec<(String, Vec<(f64, f64)>)> = f
        .agents
        .iter()
        .map(|a| (a.aid.clone(), a.spans.clone()))
        .collect();
    assert_eq!(
        spans,
        vec![
            ("a1".to_owned(), vec![(t(0), t(12)), (t(20), t(25))]),
            // no own call: still running, to the window's end
            ("a2".to_owned(), vec![(t(30), t(50))]),
        ]
    );
}
