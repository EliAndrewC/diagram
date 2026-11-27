//! 461 T06: the first pass in its hand-in mode (D4). Each fixture stands as a builder's tree does after the hand-in's apply: the work
//! staged on top of the base, nothing committed. The left column of D4's table is asked there, with its fixing command; the right
//! column (another writer's changes, the mark's hold, the red-gate tripwire) is quiet; the records the pass writes stay in the tree
//! uncommitted, HEAD the base.

use l7r_gate_core::ci::fixtures::{git, put};

use super::super::super::tests::{fx, has, push_call, tool, Fx, NOTE};
use super::{tasks, PHASE_TASKS, TEMPLATE};
use crate::land::Pass;

/// The hand-in mode over `base`.
fn at(base: &str) -> Pass {
    Pass::HandIn {
        base: base.to_owned(),
    }
}

/// A file the apply left staged, never committed.
fn staged(fx: &Fx, rel: &str, text: &str) {
    put(&fx.root, rel, text);
    git(&fx.root, &["add", "--", rel]);
}

/// The first pass at hand-in of `t` over the fixture's feature, onto the tree's HEAD.
fn pass(fx: &Fx, t: &[&str]) -> Vec<String> {
    let base = git(&fx.root, &["rev-parse", "HEAD"]);
    let d = fx.root.join("specs/449-x");
    fx.land
        .cheap_refusals(&d, &tasks(t), NOTE, &at(&base), None)
        .unwrap()
}

#[test]
fn every_left_column_refusal_fires_at_hand_in_with_its_fixing_command() {
    let fx = fx("hand-in-left");
    let d = fx.root.join("specs/449-x");
    put(&d, "tasks.md", "- [ ] T1 one\n- [x] T3 three\n");
    git(&fx.root, &["commit", "-qam", "T3 ticked"]);
    let base = git(&fx.root, &["rev-parse", "HEAD"]);
    staged(&fx, "scripts/work.sh", "true\n");
    // the gates that take a range are given the hand-in base: the working tree against it (D4)
    for gate in ["review-gate.sh", "plan-gate.sh"] {
        let line = format!("{} {base}", tool(&format!("gates/{gate}")));
        fx.answer(&line, "rc", "1");
        fx.answer(&line, "out", &format!("{gate} refused at the base\n"));
    }
    fx.answer(&tool("gates/entry-gate.sh"), "rc", "1");
    fx.answer(&tool("gates/entry-gate.sh"), "out", "an entry drifted\n");
    let claims = tool("gates/claims-gate.sh");
    fx.answer(&claims, "rc", "1");
    fx.answer(&claims, "out", "owed (impl-drift) k\n");
    fx.answer(&push_call(&fx), "rc", "1");
    fx.answer(
        &push_call(&fx),
        "err",
        "sync-with-main: a Rust file is past the bar\n",
    );
    let stale = format!("{} coverage-exempt stale", tool("gates/l7r-gate.sh"));
    fx.answer(&stale, "out", "a.py\n");
    *fx.answers.ledger.borrow_mut() = "| ? | a pass |\n".to_owned();
    let stops = pass(&fx, &["T3"]);
    let all = stops.join("\n");
    has(&all, "T3: T3 is already ticked");
    has(&all, "1 stale entry (a.py) - make coverage-exempt PRUNE=1");
    has(
        &all,
        "review passes with no ledger row - make ledger-owed WRITE=",
    );
    has(&all, "review-gate.sh: review-gate.sh refused at the base");
    has(&all, "plan-gate.sh: plan-gate.sh refused at the base");
    has(&all, "entry-gate.sh: an entry drifted");
    // an owed claim with no check in flight: its bundle named, and the builder's command to run again
    has(
        &all,
        "claims-gate.sh: a claim is owed a check and none is in flight",
    );
    has(&all, "`make claims-bundle OWED=1`");
    has(&all, "then run make builder-done again");
    assert!(!all.contains("make land again"), "{all}");
    has(
        &all,
        "push-checks: sync-with-main: a Rust file is past the bar",
    );
    assert_eq!(stops.len(), 8, "{stops:?}");
    // the push's table without the gate's stamp rows, and no coverage run asked
    let log = fx.log();
    has(&log, &push_call(&fx));
    let runs = |w: &str| ["cover", "crate-checks", "done", "rust"].contains(&w);
    assert!(!log.split_whitespace().any(runs), "{log}");
}

#[test]
fn an_owed_claim_with_a_round_in_flight_is_the_lane_s_at_hand_in() {
    let fx = fx("hand-in-flight");
    let claims = tool("gates/claims-gate.sh");
    fx.answer(&claims, "rc", "1");
    fx.answer(&claims, "out", "owed (impl-drift) k\n");
    fx.answers.flight.borrow_mut().push("b".to_owned());
    assert!(pass(&fx, &["T1"]).is_empty());
    // ...said to the caller's list where it gives one
    let d = fx.root.join("specs/449-x");
    let base = git(&fx.root, &["rev-parse", "HEAD"]);
    let mut later = Vec::new();
    let stops = fx
        .land
        .cheap_refusals(&d, &tasks(&["T1"]), NOTE, &at(&base), Some(&mut later))
        .unwrap();
    assert_eq!((stops.len(), later.len()), (0, 1));
    // a refusal no round answers is the builder's, a round in flight or not
    fx.answer(&claims, "out", "a form problem\n");
    has(
        &pass(&fx, &["T1"]).join("\n"),
        "claims-gate.sh: a form problem",
    );
}

#[test]
fn the_lane_s_checks_are_quiet_at_hand_in() {
    let fx = fx("hand-in-right");
    // an engine change committed past origin/main, the hand-in onto origin/main (phase 2's base), and the work staged
    fx.in_delta("rust/gate/src/a.rs", "fn a() {}\n");
    staged(&fx, "rust/gate/src/b.rs", "fn b() {}\n");
    let held = format!("{} arbiter gate-held", tool("gates/l7r-gate.sh"));
    fx.answer(&held, "rc", "1");
    fx.answer(&held, "out", "make done: refused - the tripwire holds\n");
    *fx.answers.holding.borrow_mut() = "T9 nine".to_owned();
    let d = fx.root.join("specs/449-x");
    let landing = fx
        .land
        .cheap_refusals(&d, &tasks(&["T1"]), NOTE, &Pass::Landing, None)
        .unwrap()
        .join("\n");
    has(
        &landing,
        "uncommitted changes in the clone, not this landing's",
    );
    has(&landing, "held by T9 nine");
    has(&landing, "the tripwire holds");
    let base = git(&fx.root, &["rev-parse", "origin/main"]);
    let stops = fx
        .land
        .cheap_refusals(&d, &tasks(&["T1"]), NOTE, &at(&base), None)
        .unwrap();
    assert!(stops.is_empty(), "{stops:?}");
}

#[test]
fn the_records_are_written_into_the_tree_uncommitted_and_head_stays_the_base() {
    let fx = fx("hand-in-records");
    *fx.answers.ledger_writes.borrow_mut() = Some(fx.root.join("dev/review-ledger.md"));
    put(&fx.root, "Makefile", "a:   ## [tests] a target\n\techo a\n");
    put(&fx.root, "docs/make-targets.html", "stale\n");
    git(&fx.root, &["add", "Makefile", "docs/make-targets.html"]);
    put(&fx.root, "dev/claims-index.json", "{}\n");
    git(&fx.root, &["add", "dev/claims-index.json"]);
    put(&fx.root, "dev/bypass-log/2026-11/r.json", "{}\n");
    fx.answers.claims.borrow_mut().insert(
        "carry".to_owned(),
        (0, "claims-carry: 1 filed into 449-x T7\n".to_owned()),
    );
    put(&fx.root, "specs/449-x/claims-carried.jsonl", "{}\n");
    fx.answers.claims.borrow_mut().insert(
        "known".to_owned(),
        (0, "claims-known: recorded 1\n".to_owned()),
    );
    staged(&fx, "scripts/work.sh", "true\n");
    let before = git(&fx.root, &["rev-parse", "HEAD"]);
    assert!(pass(&fx, &["T1"]).is_empty());
    assert_eq!(git(&fx.root, &["rev-parse", "HEAD"]), before);
    let status = fx.land.dirty(&[]).unwrap();
    for path in [
        "dev/review-ledger.md",
        "docs/make-targets.html",
        "dev/claims-index.json",
        "dev/bypass-log/",
        "specs/449-x/claims-carried.jsonl",
        "scripts/work.sh",
    ] {
        has(&status, path);
    }
    assert_eq!(l7r_gate_cohort::make_docs::check(&fx.root).code, 0);
    // the landing's own pass commits them, as before: the mode is the pass's alone
    let d = fx.root.join("specs/449-x");
    git(&fx.root, &["reset", "-q", "--", "scripts/work.sh"]);
    std::fs::remove_file(fx.root.join("scripts/work.sh")).unwrap();
    fx.land
        .cheap_refusals(&d, &tasks(&["T1"]), NOTE, &Pass::Landing, None)
        .unwrap();
    has(&fx.subjects(), "the review passes' ledger rows");
}

#[test]
fn a_named_file_is_held_by_the_applied_tree_not_by_the_base() {
    let fx = fx("hand-in-named");
    let d = fx.root.join("specs/449-x");
    let new = "rust/gate/crates/land/src/land/new.rs";
    put(
        &d,
        "tasks.md",
        "## Occasions\n\n- none: T1 - tooling only\n\n## Tasks\n\n- [ ] T1 one\n",
    );
    put(
        &d,
        "plan.md",
        &format!("### T1 (why)\n\n  - **Where.** A new module, `{new}`.\n"),
    );
    git(&fx.root, &["commit", "-qam", "the tasks"]);
    let refused = |stops: Vec<String>| stops.iter().any(|s| s.contains("plan section names"));
    assert!(refused(pass(&fx, &["T1"])));
    staged(&fx, new, "fn new() {}\n");
    assert!(!refused(pass(&fx, &["T1"])));
    // the landing's own pass still reads HEAD, which lacks it
    let landing = fx
        .land
        .cheap_refusals(&d, &tasks(&["T1"]), NOTE, &Pass::Landing, None);
    assert!(refused(landing.unwrap()));
}

#[test]
fn a_rust_stage_s_checklist_and_open_claims_are_asked_of_the_applied_work() {
    let fx = fx("hand-in-phase");
    let d = fx.root.join("specs/444-x");
    put(&d, "tasks.md", PHASE_TASKS);
    for f in ["plan.md", "plan-review.json"] {
        std::fs::copy(fx.root.join("specs/449-x").join(f), d.join(f)).unwrap();
    }
    put(&fx.root, ".specify/templates/phase-checklist.md", TEMPLATE);
    git(&fx.root, &["add", "-A"]);
    git(&fx.root, &["commit", "-qm", "444"]);
    let base = git(&fx.root, &["rev-parse", "HEAD"]);
    // the stage's code is the work, staged and not committed: the delta read against the base holds it
    staged(&fx, "rust/phases/src/seat.rs", "fn seat() {}\n");
    fx.answers
        .own
        .borrow_mut()
        .push("DRIFTED  rust/phases/src/seat.rs::seat".to_owned());
    let stops = fx
        .land
        .cheap_refusals(&d, &tasks(&["T1"]), NOTE, &at(&base), None)
        .unwrap();
    let all = stops.join("\n");
    has(
        &all,
        "phase seat: no checklist at specs/444-x/phases/seat.md",
    );
    has(
        &all,
        "T1 is a Rust stage's landing with 1 open claim finding(s)",
    );
}
