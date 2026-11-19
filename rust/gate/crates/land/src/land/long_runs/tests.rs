//! The second pass: the Rust stage gate's record, the gates the stamp names, the cohort beside them, the work-budget run.

use super::super::tests::{fx, tool};
use super::{gate_machinery, stop_cohort};

fn stamp() -> String {
    format!("{} stamp --check origin/main", tool("gates/l7r-gate.sh"))
}

fn gate(rest: &str) -> String {
    format!("{} {rest}", tool("gates/l7r-gate.sh"))
}

#[test]
fn a_covered_delta_runs_nothing_long() {
    let fx = fx("long-none");
    assert_eq!(fx.land.long_runs(), Ok(0));
    assert!(!fx.log().contains("make"));
}

/// An engine delta on a Rust-only port: the stage gate owed.
fn rust_engine(tag: &str) -> super::super::tests::Fx {
    let fx = fx(tag);
    fx.in_delta("rust/phases/src/a.rs", "fn a() {}\n");
    fx.answer(&gate("cohort port"), "out", "rust-only\n");
    fx
}

#[test]
fn the_rust_stage_gate_s_record_is_made_and_a_failing_seed_stops_the_landing() {
    let fx = rust_engine("long-rust-gate");
    fx.answer("make --no-print-directory rust-gate", "rc", "1");
    assert_eq!(fx.land.long_runs(), Ok(1));
    assert!(fx
        .said()
        .1
        .contains("the Rust stage gate has a failing seed"));
}

/// The work-budget review after a green stage gate, apart from the failing seed above (feature 449 T167: the four second passes in one
/// test ran over FR-008's tenth of a second); it counts for itself (T224), so its refusal stops the landing and nothing is run for it.
#[test]
fn the_work_budget_review_s_refusal_stops_the_landing() {
    let fx = rust_engine("long-budget");
    fx.answer("make --no-print-directory rust-gate", "rc", "0");
    fx.answer(
        "make --no-print-directory work-budget-review ROUTE=GATED",
        "rc",
        "1",
    );
    fx.answer(
        "make --no-print-directory work-budget-review ROUTE=GATED",
        "out",
        "stage seat is over its figure\n",
    );
    assert_eq!(fx.land.long_runs(), Ok(1));
    assert!(fx
        .said()
        .1
        .contains("the work-budget review refuses this engine - nothing landed:\nstage seat"));
    fx.answer(
        "make --no-print-directory work-budget-review ROUTE=GATED",
        "rc",
        "0",
    );
    assert_eq!(fx.land.long_runs(), Ok(0));
}

#[test]
fn a_machinery_delta_whose_stamp_passes_runs_the_guard_suites() {
    let fx = fx("long-machinery");
    fx.in_delta("scripts/gates/x.sh", "true\n");
    assert_eq!(fx.land.long_runs(), Ok(0));
    fx.answer(&gate("stamp --fresh hooks"), "rc", "1");
    fx.answer("make --no-print-directory hooks-test", "rc", "1");
    assert_eq!(fx.land.long_runs(), Ok(1));
    assert!(fx.said().1.contains("land: make hooks-test is red"));
    assert!(fx
        .said()
        .0
        .contains("(scripts/gates/x.sh) - the gate's reuse stands"));
}

/// An engine delta whose stamp names `make done` and `make hooks-test`, with no landing cohort and 8 GB free.
fn named(tag: &str) -> super::super::tests::Fx {
    let fx = fx(tag);
    fx.in_delta("l7r/diagram/a.py", "x = 1\n");
    fx.answer(&gate("cohort rust-owed"), "rc", "1");
    fx.answer(
        &stamp(),
        "out",
        "stale (make done again) and (make hooks-test again) (make done again)\n",
    );
    fx.answer(&gate("cohort check"), "rc", "1");
    std::fs::write(&fx.land.meminfo, "MemAvailable: 8192000 kB\n").unwrap();
    fx
}

#[test]
fn the_gates_the_stamp_names_run_and_the_cohort_beside_make_done() {
    let fx = named("long-named");
    fx.answer(&stamp(), "rcs", "1\n1\n");
    fx.answer(
        "make --no-print-directory cohort-landing JOBS=8",
        "sh",
        "echo 'seed 7 passed the whole gate'; echo noise; echo 'a regression'\n",
    );
    assert_eq!(fx.land.long_runs(), Ok(1));
    let (out, err) = fx.said();
    assert!(out.contains("land: make cohort-landing JOBS=8 beside the gate (8000 MB free"));
    assert!(out.contains("make done (the changed modules"));
    assert!(out.contains("make hooks-test (the changed modules"));
    assert!(out.contains("seed 7 passed the whole gate\na regression\n"));
    assert!(err.contains("the green-gate stamp still refuses"));
}

/// The cohort beside the gate refusing, and a red gate stopping it, apart from the passing run above (feature 449 T167: the three
/// second passes in one test ran over FR-008's tenth of a second).
#[test]
fn a_refusing_cohort_or_a_red_gate_beside_it_stops_the_landing() {
    let fx = named("long-named-red");
    // the cohort refuses
    fx.answer(&stamp(), "rcs", "1\n");
    fx.answer("make --no-print-directory cohort-landing JOBS=8", "rc", "1");
    assert_eq!(fx.land.long_runs(), Ok(1));
    assert!(fx
        .said()
        .1
        .contains("land: the landing cohort refused - nothing landed ("));
    // a red gate stops it and the cohort with it
    fx.answer(&stamp(), "rcs", "1\n");
    fx.answer(
        "make --no-print-directory cohort-landing JOBS=8",
        "sh",
        "sleep 20\n",
    );
    fx.answer(
        "make --no-print-directory hooks-test NO_CUTOFF=1",
        "rc",
        "2",
    );
    assert_eq!(fx.land.long_runs(), Ok(1));
    assert!(fx.said().1.contains("land: make hooks-test is red"));
}

#[test]
fn a_green_gate_s_records_and_regenerated_maps_are_committed() {
    let fx = fx("long-records");
    fx.answer(&stamp(), "rcs", "1\n0\n");
    fx.answer(
        "make --no-print-directory done NO_CUTOFF=1",
        "sh",
        "mkdir -p dev/run-log dev/cohort-log pool && echo r > dev/run-log/r.json && echo c > dev/cohort-log/c.json && echo m > pool/m.json\n",
    );
    assert_eq!(fx.land.long_runs(), Ok(0));
    let subjects = fx.subjects();
    assert!(subjects.contains("the run records (make land)"));
    assert!(subjects.contains("regenerated by the landing's gate (make land)"));
}

#[test]
fn an_engine_delta_with_no_cohort_owes_make_cohort_landing() {
    let fx = fx("long-cohort-after");
    fx.in_delta("pool/a.json", "{}\n");
    fx.answer(&gate("cohort rust-owed"), "rc", "1");
    fx.answer(&gate("cohort check"), "rc", "1");
    fx.answer("make --no-print-directory cohort-landing", "rc", "1");
    assert_eq!(fx.land.long_runs(), Ok(1));
    assert!(fx
        .said()
        .1
        .contains("land: the landing cohort refused - nothing landed (above)"));
    fx.answer(
        "make --no-print-directory cohort-landing",
        "sh",
        "echo m > pool/b.json\n",
    );
    fx.answer("make --no-print-directory cohort-landing", "rc", "0");
    assert_eq!(fx.land.long_runs(), Ok(0));
    assert!(fx
        .subjects()
        .contains("regenerated by the landing's cohort"));
}

#[test]
fn a_gate_or_cohort_that_cannot_start_is_a_raise() {
    let mut fx = fx("long-raise");
    fx.land.make = "/no/such/make".to_owned();
    assert!(fx.land.run_gate("done").is_err());
    assert!(fx.land.start_cohort().is_err());
    fx.land.root = fx.dir.join("none");
    assert!(fx.land.start_cohort().is_err());
    stop_cohort(None);
    let mut done = std::process::Command::new("true").spawn().unwrap();
    let _ = done.wait();
    stop_cohort(Some(&mut done));
}

#[test]
fn the_machinery_is_python_s() {
    let names = |n: &[&str]| n.iter().map(|s| (*s).to_owned()).collect::<Vec<_>>();
    assert_eq!(
        gate_machinery(&names(&[
            "Makefile",
            "rust/gate/crates/land/src/land.rs",
            "rust/gate/crates/landx/src/lib.rs",
            "scripts/land.py",
            "scripts/gates/x.sh"
        ])),
        names(&[
            "Makefile",
            "rust/gate/crates/land/src/land.rs",
            "scripts/gates/x.sh"
        ])
    );
}
