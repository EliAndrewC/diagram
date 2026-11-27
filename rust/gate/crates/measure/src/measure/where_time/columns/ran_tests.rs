//! Feature 451 T522: what a task's counts count, and a pool tree's line tied to its holder's run.

use std::collections::HashMap;

use serde_json::{json, Value};

use super::super::{runs, Window};
use super::*;

fn at(hms: &str) -> String {
    format!("2026-11-27T{hms}Z")
}

fn ev(v: &Value) -> Event {
    v.as_object().unwrap().clone()
}

fn phase(step: &str, (t0, t1): (&str, &str), make: &str, task: &str) -> Event {
    ev(
        &json!({"ev": "Phase", "src": "rust", "step": step, "t0": at(t0), "t1": at(t1), "make": make, "sid": "s",
        "task": task, "clone": "/c/pool-a", "crates": ["rust/guard", "rust/gate"], "feature": "451-x"}),
    )
}

/// Every compiler invocation a compile, a unit-test run apart from a coverage run, a `make quick` line none; a compile under the
/// knob counted as a no-op, the writer's `compiled` taken first.
#[test]
fn every_compiler_invocation_is_a_compile_and_a_coverage_run_is_apart() {
    let lines = [
        ("build", ("03:00:00", "03:00:05")),
        ("cover-build", ("03:00:00", "03:00:00.4")),
        ("lint", ("03:00:00", "03:00:02")),
        ("lint", ("03:00:00", "03:00:00.2")),
        ("prewarm", ("03:00:00", "03:00:00.5")),
        ("test", ("03:00:00", "03:00:03")),
        ("cover-run", ("03:00:00", "03:00:01")),
        ("format", ("03:00:00", "03:00:01")),
        ("slot-wait", ("03:00:00", "03:00:01")),
    ];
    let rans: Vec<Ran> = lines
        .iter()
        .filter_map(|(step, span)| {
            let p = phase(step, *span, "rust-test", "T1");
            let (a, b) = (ts(&at(span.0)).unwrap(), ts(&at(span.1)).unwrap());
            kind(&p).map(|k| Ran::of(&p, k, (a, b)))
        })
        .collect();
    let quick = ev(&json!({"ev": "Phase", "src": "quick", "step": "quick"}));
    assert_eq!(kind(&quick), None);
    let c = counts(&rans);
    assert_eq!((c.compile.0, c.worked, c.unit.0, c.cover.0), (5, 2, 1, 1));
    assert!((c.unit.1 - 3.0).abs() < 1e-6 && (c.cover.1 - 1.0).abs() < 1e-6);
    let r = &rans[0];
    assert_eq!(
        (r.tree.as_str(), r.make.as_str(), r.crates.as_str(), &r.key),
        (
            "pool-a",
            "rust-test",
            "rust/guard rust/gate",
            &("451-x".to_owned(), "T1".to_owned())
        )
    );
    // the writer's word stands over the span: a fast build that compiled, a slow one that did not
    let mut said = phase("build", ("03:00:00", "03:00:00.1"), "rust-test", "");
    said.insert("compiled".into(), json!(2));
    let fast = Ran::of(&said, Kind::Compile, (0.0, 0.1));
    said.insert("compiled".into(), json!(0));
    let slow = Ran::of(&said, Kind::Compile, (0.0, 9.0));
    assert_eq!(
        (fast.worked(), slow.worked(), fast.key.1.as_str()),
        (true, false, "-")
    );
}

fn call(id: &str, by: &str, task: &str, make: &str, (t0, t1): (&str, &str)) -> [Event; 2] {
    let line = |ev_: &str, t: &str| {
        ev(
            &json!({"t": at(t), "sid": "s", "ev": ev_, "tool": "Bash", "id": id, "by": by, "make": make, "task": task}),
        )
    };
    [line("PreToolUse", t0), line("PostToolUse", t1)]
}

/// T417's case (2026-11-27): two builders of one session, each in a `make rust-test`; T2's build line from its pool tree, held for
/// T2, falls inside both runs. Before T522 it went to T1's run, started later, wherever T2's run did not hold it; now only to T2's,
/// and to no run where T2's does not hold it. A lint (no category) and a pre-warm (no run) are counted all the same.
#[test]
fn a_pool_trees_line_ties_only_to_its_holders_run() {
    let stream: Vec<Event> = [
        call("t2", "b2", "T2", "rust-test", ("03:00:00", "03:01:00")),
        call("t1", "b1", "T1", "rust-test", ("03:00:10", "03:02:00")),
    ]
    .concat();
    let held = |step: &str, span: (&str, &str)| {
        let mut p = phase(step, span, "rust-test", "T2");
        p.insert("held_for".into(), json!(["T2", "T9"]));
        p
    };
    let aside = [
        held("build", ("03:00:20", "03:00:30")),
        // T2's run ended at 03:01:00: this one T1's run alone holds, and it is not T1's
        held("build", ("03:01:10", "03:01:20")),
        held("lint", ("03:00:40", "03:00:50")),
        held("prewarm", ("02:59:00", "02:59:30")),
    ];
    let (none, no_stops) = (HashMap::new(), HashMap::new());
    let w = Window {
        stopped: &no_stops,
        queued: &HashMap::new(),
        end: ts(&at("04:00:00")).unwrap(),
        enqueued: &none,
        goal: "done",
    };
    let r = runs(&stream, &aside, &[], &w).unwrap();
    let by = |id: &str| r.runs.iter().find(|x| x.id == id).unwrap();
    assert_eq!(by("t1").split.spans("compile"), []);
    assert_eq!(by("t2").split.spans("compile").len(), 1);
    assert_eq!(r.loose.0, 1);
    let steps: Vec<&str> = by("t2").split.ran.iter().map(|x| x.step.as_str()).collect();
    assert_eq!(
        (steps, by("t1").split.ran.len()),
        (vec!["build", "lint"], 0)
    );
    assert_eq!(r.prewarm.len(), 1);
    assert_eq!(r.prewarm[0].key.1, "T2");
}
