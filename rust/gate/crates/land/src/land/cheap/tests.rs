//! The first pass: each refusal, the records the landing commits for itself, the phase checklist and the Rust stage's open claims.

use std::path::Path;

use l7r_gate_core::ci::fixtures::{git, put};

use super::super::tests::{fx, tool, NOTE, TASKS};
use super::{boxes_in, kept_lines, phase_of, task_block};

fn tasks(t: &[&str]) -> Vec<String> {
    t.iter().map(|s| (*s).to_owned()).collect()
}

#[test]
fn a_refusal_shared_by_tasks_is_said_once_naming_them_all() {
    // an open arbiter tooling fix refuses every task alike; T3 is ticked already; T2's box is open, kept for the tick's `--boxes`
    let mut fx = fx("cheap-shared");
    let d = fx.root.join("specs/449-x");
    put(&d, "tasks.md", "- [ ] T1 one\n- [ ] T2 two\n      research: physical\n      - [ ] research pass\n- [x] T3 three\n- [ ] T4 four\n");
    put(
        &d,
        "arbiter.jsonl",
        "{\"trigger\": \"round:x\", \"fix\": \"open\", \"tooling_fix\": \"the fix\"}\n",
    );
    git(&fx.root, &["add", "-A"]);
    git(&fx.root, &["commit", "-qm", "the tasks"]);
    fx.land.boxes = true;
    let mut later = Vec::new();
    let stops = fx
        .land
        .cheap_refusals(&d, &tasks(&["T1", "T2", "T3"]), NOTE, Some(&mut later))
        .unwrap();
    assert_eq!(stops.len(), 2, "{stops:?}");
    assert!(stops[0].starts_with("T1, T2: tick: refused - the round arbiter's tooling fix is open"));
    assert_eq!(stops[1], "T3: T3 is already ticked");
    assert!(later.is_empty());
    // the open box is kept for the tick's `--boxes` choice (feature 449 T121)
    assert_eq!(*fx.land.box_open.borrow(), vec!["T2".to_owned()]);
}

#[test]
fn the_tick_check_is_asked_in_process_and_its_raise_is_the_landing_s() {
    let fx = fx("cheap-check");
    let d = fx.root.join("specs/449-x");
    // a plan the tick check cannot read raises (feature 449 T131, where `tick-task.py --land-check` was run by path)
    std::fs::write(d.join("plan.md"), [0xff]).unwrap();
    assert!(fx
        .land
        .cheap_refusals(&d, &tasks(&["T1"]), NOTE, None)
        .is_err());
    std::fs::remove_file(d.join("plan.md")).unwrap();
    std::fs::write(d.join("tasks.md"), [0xff]).unwrap();
    assert!(fx
        .land
        .cheap_refusals(&d, &tasks(&["T1"]), NOTE, None)
        .is_err());
}

/// A landing whose claims gate says a claim is owed and whose plan gate refuses.
fn gates(tag: &str) -> super::super::tests::Fx {
    let fx = fx(tag);
    let claims = tool("gates/claims-gate.sh");
    fx.answer(&claims, "rc", "1");
    fx.answer(&claims, "out", "owed (impl-drift) k\n");
    fx.answer(&tool("gates/plan-gate.sh"), "rc", "1");
    fx
}

#[test]
fn the_gates_refuse_and_a_claims_refusal_is_deferred_only_where_a_wait_may_cure_it() {
    let fx = gates("cheap-gates");
    let d = fx.root.join("specs/449-x");
    // owed, none in flight: a stop now, with its cure
    let mut later = Vec::new();
    let stops = fx
        .land
        .cheap_refusals(&d, &tasks(&["T1"]), NOTE, Some(&mut later))
        .unwrap();
    assert!(stops[0].starts_with("claims-gate.sh: a claim is owed a check and none is in flight"));
    assert_eq!(stops[1], "plan-gate.sh: ");
}

/// The owed claim with a check in flight, apart from the stop above (feature 449 T167: the four first passes in one test ran over
/// FR-008's tenth of a second).
#[test]
fn an_owed_claim_with_a_check_in_flight_waits_and_an_unreadable_flight_mark_raises() {
    let fx = gates("cheap-gates-flight");
    let d = fx.root.join("specs/449-x");
    let mut later = Vec::new();
    // one in flight: deferred to the wait
    fx.answers.flight.borrow_mut().push("b".to_owned());
    let stops = fx
        .land
        .cheap_refusals(&d, &tasks(&["T1"]), NOTE, Some(&mut later))
        .unwrap();
    assert_eq!((stops.len(), later.len()), (1, 1));
    // no wait at all: said as it is
    let stops = fx
        .land
        .cheap_refusals(&d, &tasks(&["T1"]), NOTE, None)
        .unwrap();
    assert_eq!(stops[0], "claims-gate.sh: owed (impl-drift) k");
    // a flight mark that cannot be read is the landing's raise
    *fx.answers.flight_fails.borrow_mut() = true;
    assert!(fx
        .land
        .cheap_refusals(&d, &tasks(&["T1"]), NOTE, Some(&mut later))
        .is_err());
}

#[test]
fn a_red_gate_tripwire_holds_an_engine_landing_unless_escaped() {
    let mut fx = fx("cheap-arbiter");
    fx.in_delta("rust/gate/src/a.rs", "fn a() {}\n");
    fx.answer(
        &format!("{} arbiter gate-held", tool("gates/l7r-gate.sh")),
        "rc",
        "1",
    );
    fx.answer(
        &format!("{} arbiter gate-held", tool("gates/l7r-gate.sh")),
        "out",
        "make done: refused - the tripwire holds\n",
    );
    let d = fx.root.join("specs/449-x");
    let stops = fx
        .land
        .cheap_refusals(&d, &tasks(&["T1"]), NOTE, None)
        .unwrap();
    assert_eq!(stops, vec!["the tripwire holds"]);
    fx.land.arbiter_ok = true;
    assert!(fx
        .land
        .cheap_refusals(&d, &tasks(&["T1"]), NOTE, None)
        .unwrap()
        .is_empty());
}

#[test]
fn the_first_pass_commits_its_own_records() {
    let fx = fx("cheap-records");
    let d = fx.root.join("specs/449-x");
    *fx.answers.ledger_writes.borrow_mut() = Some(fx.root.join("dev/review-ledger.md"));
    // a real Makefile and a stale page: the check asked in process finds it stale and the page is written (feature 449 T135)
    put(&fx.root, "Makefile", "a:   ## [tests] a target\n\techo a\n");
    put(&fx.root, "docs/make-targets.html", "stale\n");
    git(&fx.root, &["add", "Makefile", "docs/make-targets.html"]);
    fx.answers
        .claims
        .borrow_mut()
        .insert("rekey".to_owned(), (0, String::new()));
    put(&fx.root, "dev/claims-index.json", "{}\n");
    // the deferred list a port's rekey re-keyed is committed with the rows (feature 449 T166)
    put(&fx.root, "dev/claims-deferred.json", "{}\n");
    git(
        &fx.root,
        &["add", "dev/claims-index.json", "dev/claims-deferred.json"],
    );
    put(&fx.root, "dev/bypass-log/2026-11/r.json", "{}\n");
    fx.answers.claims.borrow_mut().insert(
        "carry".to_owned(),
        (0, "claims-carry: 1 filed into 405-engine T7\n".to_owned()),
    );
    put(&fx.root, "specs/405-engine/tasks.md", "- [ ] T7 carried\n");
    put(&fx.root, "specs/405-engine/claims-carried.jsonl", "{}\n");
    fx.answers.claims.borrow_mut().insert(
        "known".to_owned(),
        (0, "claims-known: recorded 1\n".to_owned()),
    );
    put(&fx.root, "specs/449-x/gm-review.jsonl", "{}\n");
    let stops = fx
        .land
        .cheap_refusals(&d, &tasks(&["T1"]), NOTE, None)
        .unwrap();
    assert!(stops.is_empty());
    assert!(fx
        .land
        .dirty(&["dev/claims-deferred.json"])
        .unwrap()
        .is_empty());
    let subjects = fx.subjects();
    for s in [
        "the review passes' ledger rows",
        "docs/make-targets.html regenerated",
        "claim rows carried",
        "claims findings outside the change filed as a task",
        "known drifts recorded",
        "the landing's escape records",
    ] {
        assert!(subjects.contains(s), "{s}: {subjects}");
    }
    assert!(fx
        .said()
        .0
        .contains("land: claims-carry: 1 filed into 405-engine T7"));
    assert_eq!(l7r_gate_cohort::make_docs::check(&fx.root).code, 0);
}

/// The carry of [`the_first_pass_commits_its_own_records`] that names no feature, a test of its own after the one carry that pass filed
/// (feature 449 T167: the first pass, this carry and a second pass in one test ran over FR-008's tenth of a second).
#[test]
fn a_carry_that_names_no_feature_is_filed_into_this_one() {
    let fx = fx("cheap-carry");
    let d = fx.root.join("specs/449-x");
    // the carry the first pass filed, into the feature it names
    fx.answers.claims.borrow_mut().insert(
        "carry".to_owned(),
        (0, "claims-carry: 1 filed into 405-engine T7\n".to_owned()),
    );
    put(&fx.root, "specs/405-engine/tasks.md", "- [ ] T7 carried\n");
    put(&fx.root, "specs/405-engine/claims-carried.jsonl", "{}\n");
    fx.land.file_carries(&d).unwrap();
    // a carry that names no feature is filed into this one
    fx.answers.claims.borrow_mut().insert(
        "carry".to_owned(),
        (0, "filed into nothing named\n".to_owned()),
    );
    put(&fx.root, "specs/449-x/claims-carried.jsonl", "{}\n");
    fx.land.file_carries(&d).unwrap();
    assert!(fx.subjects().matches("filed as a task").count() == 2);
}

/// The second pass of [`the_first_pass_commits_its_own_records`], after a pass that regenerated the stale page, a test of its own
/// (feature 449 T167).
#[test]
fn a_second_pass_regenerates_and_commits_no_current_page() {
    let fx = fx("cheap-second-pass");
    let d = fx.root.join("specs/449-x");
    put(&fx.root, "Makefile", "a:   ## [tests] a target\n\techo a\n");
    put(&fx.root, "docs/make-targets.html", "stale\n");
    git(&fx.root, &["add", "Makefile", "docs/make-targets.html"]);
    fx.land.records_on_the_way(&d, &tasks(&["T1"])).unwrap();
    // the page current now: a second pass regenerates and commits nothing
    let before = fx
        .subjects()
        .matches("docs/make-targets.html regenerated")
        .count();
    assert_eq!(before, 1, "the first pass regenerated the stale page");
    fx.land.records_on_the_way(&d, &tasks(&["T1"])).unwrap();
    assert_eq!(
        fx.subjects()
            .matches("docs/make-targets.html regenerated")
            .count(),
        before
    );
}

#[test]
fn a_stale_exempt_entry_is_named_and_the_record_s_failure_said() {
    let fx = fx("cheap-exempt");
    let line = format!("{} coverage-exempt stale", tool("gates/l7r-gate.sh"));
    assert_eq!(fx.land.stale_exempt_refusal(), Ok(String::new()));
    fx.answer(&line, "out", "a.py\twhy\n");
    assert!(fx
        .land
        .stale_exempt_refusal()
        .unwrap()
        .contains("1 stale entry (a.py)"));
    fx.answer(&line, "out", "a.py\twhy\nb.py\n");
    assert!(fx
        .land
        .stale_exempt_refusal()
        .unwrap()
        .contains("2 stale entries (a.py, b.py)"));
    fx.answer(&line, "rc", "1");
    fx.answer(&line, "err", " broken record \n");
    assert_eq!(
        fx.land.stale_exempt_refusal(),
        Ok("broken record".to_owned())
    );
    let mut gone = fx;
    gone.land.scripts = gone.dir.join("none");
    assert!(gone.land.stale_exempt_refusal().is_err());
}

const PHASE_TASKS: &str = "- [ ] T1 the seat\n      phase: seat\n- [ ] T2 other\n";
const TEMPLATE: &str = "- [ ] 1. **one** a\n- [ ] 2. **two** b\n";

#[test]
fn a_phase_task_lands_only_with_its_checklist_ticked() {
    let fx = fx("cheap-phase");
    let d = fx.root.join("specs/444-x");
    std::fs::create_dir_all(&d).unwrap();
    assert_eq!(
        fx.land
            .phase_refusal(&fx.root.join("specs/449-x"), PHASE_TASKS, "T1"),
        Ok(String::new())
    );
    assert_eq!(
        fx.land.phase_refusal(&d, PHASE_TASKS, "T2"),
        Ok(String::new())
    );
    assert!(fx.land.phase_refusal(&d, PHASE_TASKS, "T1").is_err());
    put(&fx.root, ".specify/templates/phase-checklist.md", TEMPLATE);
    assert!(fx
        .land
        .phase_refusal(&d, PHASE_TASKS, "T1")
        .unwrap()
        .contains("no checklist at specs/444-x/phases/seat.md"));
    put(&d, "phases/seat.md", "- [x] 1. **one** done\n");
    assert!(fx
        .land
        .phase_refusal(&d, PHASE_TASKS, "T1")
        .unwrap()
        .contains("lacks the box `2. **two**`"));
    put(
        &d,
        "phases/seat.md",
        "- [x] 1. **one** done\n- [ ] 2. **two** not\n",
    );
    assert!(fx
        .land
        .phase_refusal(&d, PHASE_TASKS, "T1")
        .unwrap()
        .contains("has `2. **two**` unticked"));
    put(
        &d,
        "phases/seat.md",
        "- [x] 1. **one** done\n- [X] 2. **two** done\n",
    );
    assert_eq!(
        fx.land.phase_refusal(&d, PHASE_TASKS, "T1"),
        Ok(String::new())
    );
}

#[test]
fn a_rust_stage_lands_with_no_open_claim_in_its_own_code() {
    let fx = fx("cheap-open-claims");
    let d = fx.root.join("specs/444-x");
    assert_eq!(
        fx.land.open_claims_refusal(&d, PHASE_TASKS, "T2"),
        Ok(String::new())
    );
    assert_eq!(
        fx.land.open_claims_refusal(&d, PHASE_TASKS, "T1"),
        Ok(String::new())
    );
    fx.in_delta("rust/phases/src/seat.rs", "fn seat() {}\n");
    assert_eq!(
        fx.land.open_claims_refusal(&d, PHASE_TASKS, "T1"),
        Ok(String::new())
    );
    fx.answers
        .own
        .borrow_mut()
        .extend((1..=6).map(|i| format!("DRIFTED  rust/phases/src/seat.rs::f{i}")));
    let why = fx.land.open_claims_refusal(&d, PHASE_TASKS, "T1").unwrap();
    assert!(why.starts_with("T1 is a Rust stage's landing with 6 open claim finding(s)"));
    assert!(why.ends_with(" and 1 more"));
    let asked = fx.answers.asked.borrow();
    let split_no_seam = asked
        .iter()
        .any(|a| a.starts_with("split") && a.ends_with(" 0"));
    assert!(split_no_seam, "{asked:?}");
}

#[test]
fn the_text_helpers_read_as_the_python_did() {
    assert_eq!(kept_lines(" a \n\n b pre-existing\nc"), "a | c");
    assert_eq!(phase_of(Path::new("specs/449-x"), PHASE_TASKS, "T1"), None);
    assert_eq!(
        phase_of(Path::new("specs/444-x"), PHASE_TASKS, "T1").as_deref(),
        Some("seat")
    );
    assert_eq!(task_block(TASKS, "T9"), "");
    assert!(task_block(PHASE_TASKS, "T1").contains("phase: seat"));
    assert!(!task_block(PHASE_TASKS, "T1").contains("T2"));
    assert_eq!(boxes_in(TEMPLATE).len(), 2);
}

#[test]
fn a_phase_task_s_refusals_and_a_stale_exempt_entry_join_the_first_pass() {
    let fx = fx("cheap-phase-pass");
    let d = fx.root.join("specs/444-x");
    put(&d, "tasks.md", PHASE_TASKS);
    // the plan reviewed CLEAR, as the fixture's 449-x has it
    for f in ["plan.md", "plan-review.json"] {
        std::fs::copy(fx.root.join("specs/449-x").join(f), d.join(f)).unwrap();
    }
    put(&fx.root, ".specify/templates/phase-checklist.md", TEMPLATE);
    git(&fx.root, &["add", "-A"]);
    git(&fx.root, &["commit", "-qm", "444"]);
    fx.answer(
        &format!("{} coverage-exempt stale", tool("gates/l7r-gate.sh")),
        "out",
        "a.py\n",
    );
    let stops = fx
        .land
        .cheap_refusals(&d, &tasks(&["T1"]), NOTE, None)
        .unwrap();
    assert_eq!(stops.len(), 2);
    assert!(stops[0].starts_with("T1: phase seat: no checklist at specs/444-x/phases/seat.md"));
    assert!(stops[1].contains("1 stale entry (a.py)"));
}
