//! RED FIRST (feature 451 T182): a round-arbiter tooling fix built in Rust inside the very task being landed settles as that landing
//! pushes. Observed 2026-11-23 (451 T177, `ask:guard-wordings-sleep-and-slot`): `make arbiter-fix-done` wanted the fix's test on main,
//! `LAND=` goes through `make land-tooling`, which rightly refuses `rust/`, and the task's own `make land` was refused by the open fix -
//! so `make arbiter-fix-done ... LANDING=<task>` records the fix as pending, and the landing of that task writes its done row into its
//! own tick commit: fix and tick reach main in one push, or neither does.

use l7r_gate_core::ci::fixtures::{git, put};
use serde_json::json;

use super::{fx, land, tasks, Fx, NOTE};

const PENDING: &str = ".git/arbiter-fix-landing.json";

/// An open fix in `home`'s log, committed, and its pending entry naming 449-x's `task`.
fn pending_fix(fx: &Fx, home: &str, task: &str) {
    put(
        &fx.root,
        &format!("specs/{home}/arbiter.jsonl"),
        &format!(
            "{}\n",
            json!({"trigger": "ask:449-fix", "fix": "open", "tooling_fix": "build the thing"})
        ),
    );
    git(&fx.root, &["add", "-A"]);
    git(&fx.root, &["commit", "-qm", "the fix and its test"]);
    put(
        &fx.root,
        PENDING,
        &json!([{"trigger": "ask:449-fix", "feature": "449-x", "task": task, "home": home, "note": "the thing built",
                 "test": "rust/x/src/tests.rs", "files": ["rust/x/src/x.rs"], "utc": "2026-11-23T00:00:00Z"}])
        .to_string(),
    );
}

fn done_at_head(fx: &Fx, home: &str) -> bool {
    let at = git(
        &fx.root,
        &["show", &format!("HEAD:specs/{home}/arbiter.jsonl")],
    );
    at.contains("\"fix_of\":\"ask:449-fix\"") && at.contains("\"status\":\"done\"")
}

#[test]
fn a_fix_landing_with_its_task_goes_out_in_the_tick_commit() {
    let fx = fx("land-fix");
    pending_fix(&fx, "449-x", "T1");
    assert_eq!(land(&fx), Ok(0), "{:?}", fx.said());
    let (out, _) = fx.said();
    assert!(
        out.contains("land: ask:449-fix settled in the tick commit (the round arbiter's tooling fix, landed with T1)"),
        "{out}"
    );
    assert!(done_at_head(&fx, "449-x"));
    assert!(git(&fx.root, &["log", "-1", "--format=%s"]).contains("449-x: T1 ticked (make land)"));
    assert!(git(&fx.root, &["status", "--porcelain", "--", "specs"]).is_empty());
    assert!(!fx.root.join(PENDING).exists());
}

#[test]
fn a_fix_whose_home_is_another_feature_lands_its_row_there_and_one_the_landing_does_not_tick_waits()
{
    let one = fx("land-fix-home");
    pending_fix(&one, "448-y", "T1");
    assert_eq!(land(&one), Ok(0), "{:?}", one.said());
    assert!(done_at_head(&one, "448-y"));
    assert!(git(&one.root, &["status", "--porcelain", "--", "specs"]).is_empty());
    // pending on T2, which this landing does not tick: held at the first pass, nothing written
    let other = fx("land-fix-other");
    pending_fix(&other, "449-x", "T2");
    assert_eq!(land(&other), Ok(2));
    assert!(
        other.said().1.contains("tooling fix is open"),
        "{:?}",
        other.said()
    );
    assert!(!done_at_head(&other, "449-x"));
    assert!(other.root.join(PENDING).exists());
}

/// The closing check at the feature's last tick reads the open fixes too: the rows are written before the ticks, so a landing that
/// closes its feature is not refused by the fix it carries.
#[test]
fn a_landing_that_closes_its_feature_carries_its_fix() {
    let fx = fx("land-fix-close");
    let d = fx.root.join("specs/449-x");
    put(&d, "report.md", "# r\n");
    pending_fix(&fx, "449-x", "T2");
    assert_eq!(
        fx.land.land(&d, &tasks(&["T1", "T2"]), NOTE),
        Ok(0),
        "{:?}",
        fx.said()
    );
    assert!(done_at_head(&fx, "449-x"));
}

/// A refused tick and a failed push each put the rows back and keep the fix pending, for the landing that goes through.
#[test]
fn a_landing_that_does_not_push_settles_nothing() {
    let one = fx("land-fix-refused");
    let d = one.root.join("specs/449-x");
    pending_fix(&one, "448-y", "T2");
    let before = std::fs::read_to_string(one.root.join("specs/448-y/arbiter.jsonl")).unwrap();
    // T2's tick would close the feature, which has no report: refused
    assert_eq!(one.land.land(&d, &tasks(&["T1", "T2"]), NOTE), Ok(2));
    assert_eq!(
        std::fs::read_to_string(one.root.join("specs/448-y/arbiter.jsonl")).unwrap(),
        before
    );
    assert!(one.root.join(PENDING).exists());
    let push = fx("land-fix-push");
    pending_fix(&push, "449-x", "T1");
    push.answer(
        &format!("{} done", super::tool("sync-with-main.sh")),
        "rc",
        "1",
    );
    assert_eq!(land(&push), Ok(1));
    assert!(!done_at_head(&push, "449-x"));
    assert!(push.root.join(PENDING).exists());
}
