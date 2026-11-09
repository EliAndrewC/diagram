//! Every condition reported, and the verdict the first failure's.

use super::super::features::FeatureStatus;
use super::{decide, estimate, render, Decision, Inputs, VerifiedRecord, CHECK, MERGE};
use crate::delta::Delta;
use crate::state::State;

fn gated() -> Delta {
    Delta {
        base: "b".to_owned(),
        files: vec!["l7r/a.py".to_owned()],
        engine: vec!["l7r/a.py".to_owned()],
    }
}

fn green(hash: &str) -> State {
    State {
        event: "green-local".to_owned(),
        target: "quick".to_owned(),
        utc: "U".to_owned(),
        hash: hash.to_owned(),
        commit: "c".to_owned(),
        engine_key: String::new(),
        tooling: String::new(),
    }
}

fn complete() -> FeatureStatus {
    FeatureStatus {
        name: Some("9".to_owned()),
        exists: true,
        faithful: true,
        open_tasks: Vec::new(),
    }
}

fn record(scope: &str, id: &str) -> VerifiedRecord {
    VerifiedRecord {
        tree: "t".to_owned(),
        build_id: id.to_owned(),
        scope: scope.to_owned(),
        utc: String::new(),
    }
}

/// A decision that dispatches, changed by `edit`.
fn with(edit: impl FnOnce(&mut Inputs<'_>)) -> Decision {
    let (d, st, f) = (gated(), green("h"), complete());
    let mut i = Inputs {
        delta: &d,
        state: Some(&st),
        now_hash: "h",
        verified: None,
        breaker: None,
        mode: CHECK,
        feature: Some(&f),
        scope: "reference",
        month_to_date_usd: 1.234,
        operation: None,
        remote_off: None,
        measure: false,
    };
    edit(&mut i);
    decide(i)
}

#[test]
fn every_condition_is_reported_and_a_clean_case_dispatches() {
    let d = with(|_| {});
    assert!(d.dispatches() && !d.skip_verified());
    assert_eq!(
        d.conditions.iter().map(|c| c.name).collect::<Vec<_>>(),
        [
            "remote-enabled",
            "route-is-gated",
            "green-local-since-edit",
            "tree-not-already-verified",
            "breaker-not-tripped"
        ]
    );
    let text = render(&d, CHECK, "reference");
    assert!(
        text.starts_with(
            "ci-check (reference scope) - dispatch conditions:\n  [ok] remote-enabled"
        ) && text.contains(
            "estimate: ~10 build-min at $0.02/min = ~$0.20; month-to-date remote spend $1.23"
        ) && text.ends_with("verdict: DISPATCH")
    );
}

#[test]
fn a_direct_route_a_red_gate_and_an_edit_each_refuse_by_name() {
    let direct = Delta {
        files: vec!["docs/a.md".to_owned()],
        ..Delta::default()
    };
    assert_eq!(
        with(|i| i.delta = Box::leak(Box::new(direct))).verdict,
        "REFUSE(route-is-gated)"
    );
    assert_eq!(
        with(|i| i.state = None).verdict,
        "REFUSE(green-local-since-edit)"
    );
    let red = State {
        event: "failed-gate".to_owned(),
        ..green("h")
    };
    let failed = with(|i| i.state = Some(Box::leak(Box::new(red))));
    assert!(failed.conditions[2].why.contains("the last gate FAILED"));
    let moved = with(|i| i.now_hash = "other");
    assert_eq!(moved.verdict, "REFUSE(green-local-since-edit)");
    assert!(moved.conditions[2].why.contains("the code changed since"));
    assert_eq!(
        with(|i| i.breaker = Some("tripped")).verdict,
        "REFUSE(breaker-not-tripped)"
    );
}

#[test]
fn a_merge_needs_a_complete_feature_and_with_none_says_so() {
    let d = with(|i| i.mode = MERGE);
    assert_eq!(d.conditions[2].name, "feature-complete");
    assert!(d.dispatches());
    let none = with(|i| {
        i.mode = MERGE;
        i.feature = None;
    });
    assert_eq!(none.verdict, "REFUSE(feature-complete)");
}

#[test]
fn a_verified_record_skips_only_for_its_scope_and_says_who() {
    let skip = with(|i| i.verified = Some(record("reference", "b:1")));
    assert!(skip.skip_verified() && skip.conditions[3].why.contains("by b:1"));
    let local = with(|i| i.verified = Some(record("reference", "local:make-done@c")));
    assert!(local.conditions[3]
        .why
        .contains("a green local `make done`"));
    let owed = with(|i| {
        i.verified = Some(record("reference", "b:1"));
        i.scope = "full";
    });
    assert!(owed.dispatches() && owed.conditions[3].why.contains("a full run is still owed"));
    assert!(with(|i| {
        i.verified = Some(record("full", "b:1"));
        i.scope = "full";
    })
    .skip_verified());
    assert!(with(|i| {
        i.verified = Some(record("full", "b:1"));
    })
    .skip_verified());
}

#[test]
fn an_operation_or_a_measurement_is_never_short_circuited() {
    assert!(with(|i| {
        i.verified = Some(record("full", "b"));
        i.operation = Some("cohort");
    })
    .dispatches());
    assert!(with(|i| {
        i.verified = Some(record("full", "b"));
        i.measure = true;
    })
    .dispatches());
}

#[test]
fn the_measurement_bypasses_only_the_route_and_prints_that_it_did() {
    let direct = Delta::default();
    let d = with(|i| {
        i.delta = Box::leak(Box::new(direct));
        i.measure = true;
    });
    assert!(d.dispatches() && d.conditions[1].why.contains("BYPASSED"));
    let red = with(|i| {
        i.measure = true;
        i.state = None;
    });
    assert_eq!(red.verdict, "REFUSE(green-local-since-edit)");
    assert_eq!(
        with(|i| {
            i.measure = true;
            i.remote_off = Some("off");
        })
        .verdict,
        "REFUSE(remote-enabled)"
    );
}

#[test]
fn remote_off_is_reported_first_but_a_vouched_merge_still_lands() {
    let d = with(|i| i.remote_off = Some("remote is OFF"));
    assert_eq!(d.verdict, "REFUSE(remote-enabled)");
    assert!(
        !d.conditions[0].passed && render(&d, CHECK, "reference").contains("[--] remote-enabled")
    );
    assert!(with(|i| {
        i.remote_off = Some("off");
        i.verified = Some(record("reference", "b"));
    })
    .skip_verified());
}

#[test]
fn the_estimate_is_the_scope_s_or_the_operation_s() {
    assert!((estimate("full", 0.0, None).minutes - 8.0).abs() < f64::EPSILON);
    assert!((estimate("full", 0.0, Some("x")).minutes - 10.0).abs() < f64::EPSILON);
}
