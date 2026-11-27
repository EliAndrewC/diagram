//! The attribution's readers and its phase-2 verdict (feature 461 T15).

use std::path::Path;

use serde_json::{json, Value};

use super::{attribute, reds, Change, Verdict};

const SPAN: (&str, &str) = ("2026-11-28T03:00:00.000Z", "2026-11-28T03:10:00.000Z");

fn phase(step: &str, code: i32, t0: &str, t1: &str, clone: &str, crates: &[&str]) -> Value {
    json!({"ev": "Phase", "src": "rust", "step": step, "t0": t0, "t1": t1, "code": code, "clone": clone, "crates": crates})
}

fn units(events: &[Value], output: &str) -> Vec<String> {
    reds(events, SPAN, Path::new("/lane"), output)
        .into_iter()
        .map(|r| r.unit)
        .collect()
}

fn change(files: &[&str], tasks: &[&str]) -> Change {
    Change {
        files: files.iter().map(|f| (*f).to_owned()).collect(),
        tasks: tasks.iter().map(|t| (*t).to_owned()).collect(),
    }
}

#[test]
fn a_red_phase_line_in_the_attempt_s_span_and_tree_names_its_crates_once() {
    let (a, b) = ("2026-11-28T03:01:00.000Z", "2026-11-28T03:02:00.000Z");
    let events = [
        phase(
            "test",
            101,
            a,
            b,
            "/lane",
            &["rust/gate/crates/land", "rust/guard"],
        ),
        // one crate of it alone is a unit of its own, and the same unit twice is kept once
        phase("test", 101, a, b, "/lane", &["rust/gate/crates/land"]),
        phase("test", 101, a, b, "/lane", &["rust/gate/crates/land"]),
        // a line naming no crate is no unit
        phase("build", 101, a, b, "/lane", &[]),
        phase("lint", 1, a, b, "/lane", &["rust/gate/crates/lane/"]),
        // green, another tree's, before the span, after it, a step that names no crate's red, not a Phase line
        phase("test", 0, a, b, "/lane", &["rust/gate/crates/green"]),
        phase("test", 101, a, b, "/b1", &["rust/gate/crates/other"]),
        phase(
            "test",
            101,
            "2026-11-28T02:59:59.999Z",
            b,
            "/lane",
            &["rust/early"],
        ),
        phase(
            "test",
            101,
            a,
            "2026-11-28T03:10:00.001Z",
            "/lane",
            &["rust/late"],
        ),
        phase("test", 101, a, "", "/lane", &["rust/unended"]),
        phase("format", 1, a, b, "/lane", &["rust/fmt"]),
        json!({"ev": "PreToolUse", "step": "test", "code": 1, "t0": a, "t1": b, "clone": "/lane", "crates": ["rust/tool"]}),
    ];
    assert_eq!(
        units(&events, ""),
        [
            "rust/gate/crates/land rust/guard test",
            "rust/gate/crates/land test",
            "rust/gate/crates/lane/ lint"
        ]
    );
}

/// A red `cover-build` is one compile of a crate family: its red names the family, never a change under each crate of it, so two
/// changes under two of its crates are unplaced, and a change under one of them alone is placed with the one unit.
#[test]
fn a_red_line_naming_several_crates_is_one_unit_over_all_of_them() {
    let (a, b) = ("2026-11-28T03:01:00.000Z", "2026-11-28T03:02:00.000Z");
    let family = [phase(
        "cover-build",
        101,
        a,
        b,
        "/lane",
        &["rust/a", "rust/b", "rust/c", "rust/d", "rust/e"],
    )];
    let read = reds(&family, SPAN, Path::new("/lane"), "");
    let shown: Vec<&str> = read.iter().map(|r| r.unit.as_str()).collect();
    assert_eq!(shown, ["rust/a rust/b rust/c (+2 more) cover-build"]);
    let under_a = change(&["rust/a/src/x.rs"], &["T01"]);
    let under_e = change(&["rust/e/src/y.rs"], &["T02"]);
    let elsewhere = change(&["docs/z.md"], &["T03"]);
    assert_eq!(
        attribute(&read, &[under_a.clone(), under_e.clone()]),
        Verdict::Unplaced
    );
    assert_eq!(
        attribute(&read, &[elsewhere, under_e]),
        Verdict::Placed(vec![(
            1,
            vec!["rust/a rust/b rust/c (+2 more) cover-build".to_owned()]
        )])
    );
    let two = [phase("test", 101, a, b, "/lane", &["rust/a", "rust/b"])];
    let read = reds(&two, SPAN, Path::new("/lane"), "");
    assert_eq!(read[0].unit, "rust/a rust/b test");
    assert_eq!(
        attribute(&read, &[under_a]),
        Verdict::Placed(vec![(0, vec!["rust/a rust/b test".to_owned()])])
    );
}

#[test]
fn a_red_suite_and_the_first_pass_s_rows_are_read_from_the_output() {
    let output = "\n\u{1b}[1mHOOK TESTS FAILED: agent-model-hooks.sh.3 (whole log kept: /g/x)\u{1b}[0m\n  a line of its log\n\
        HOOK TESTS FAILED: test-sync-with-main.sh\n\
        HOOK TESTS FAILED: review-gate.sh.x\n\
        land: refused before anything ran - nothing landed, nothing ticked. Every refusal:\n  T13: the plan review is owed\n  push-checks: docs/make-targets.html is stale\n\n  after a blank, no row\n";
    assert_eq!(
        units(&[], output),
        [
            "hooks agent-model-hooks.sh",
            "hooks sync-with-main.sh",
            "hooks review-gate.sh.x",
            "first-pass T13: the plan review is owed",
            "first-pass push-checks: docs/make-targets.html is stale"
        ]
    );
    // a long row's unit is cut, its whole text still matched
    let long = format!("Every refusal:\n  {}rust/x.rs\n", "y".repeat(200));
    let cut = reds(&[], SPAN, Path::new("/lane"), &long);
    assert_eq!(cut[0].unit.chars().count(), "first-pass ".len() + 120);
    let v = attribute(
        &cut,
        &[change(&["rust/x.rs"], &["T01"]), change(&["b"], &["T02"])],
    );
    assert_eq!(v, Verdict::Placed(vec![(0, vec![cut[0].unit.clone()])]));
}

#[test]
fn each_unit_naming_one_change_places_that_change_with_its_units() {
    let (a, b) = ("2026-11-28T03:01:00.000Z", "2026-11-28T03:02:00.000Z");
    let events = [
        phase(
            "test",
            101,
            a,
            b,
            "/lane",
            &["rust/gate/crates/land", "rust/gate"],
        ),
        phase("lint", 1, a, b, "/lane", &["rust/gate/crates/land"]),
    ];
    let output = "HOOK TESTS FAILED: agent-model-hooks.sh\nHOOK TESTS FAILED: sync-with-main.sh\nEvery refusal:\n  T07, T09: owed\n  push-checks: docs/x.md is stale\n";
    let r = reds(&events, SPAN, Path::new("/lane"), output);
    let changes = [
        change(&["docs/y.md"], &["T01"]),
        // `rust/gate/crates/land/` and `rust/gate/` both hold it: one unit of the line's two crates, and the lint's, one change
        change(&["rust/gate/crates/land/src/a.rs"], &["T02"]),
        change(
            &["rust/guard/shared/src/guards/agent_model_hooks/x.rs"],
            &["T03"],
        ),
        change(&["scripts/sync-with-main.sh"], &["T04"]),
        change(&["specs/x/tasks.md"], &["T09"]),
        change(&["docs/x.md"], &["T05"]),
    ];
    assert_eq!(
        attribute(&r, &changes),
        Verdict::Placed(vec![
            (
                1,
                vec![
                    "rust/gate/crates/land rust/gate test".to_owned(),
                    "rust/gate/crates/land lint".to_owned()
                ]
            ),
            (2, vec!["hooks agent-model-hooks.sh".to_owned()]),
            (3, vec!["hooks sync-with-main.sh".to_owned()]),
            (4, vec!["first-pass T07, T09: owed".to_owned()]),
            (
                5,
                vec!["first-pass push-checks: docs/x.md is stale".to_owned()]
            ),
        ])
    );
}

#[test]
fn a_suite_names_its_tests_and_its_guard_s_sources_but_a_guard_s_sources_only_for_a_hooks_suite() {
    let r = reds(
        &[],
        SPAN,
        Path::new("/lane"),
        "HOOK TESTS FAILED: agent-model-hooks.sh\n",
    );
    for files in [
        &["tests/hooks/test-agent-model-hooks.sh"][..],
        &["tests/hooks/test-agent-model-hooks.2.sh"],
        &["rust/guard/src/guards/agent_model_hooks.rs"],
    ] {
        let placed = Verdict::Placed(vec![(0, vec!["hooks agent-model-hooks.sh".to_owned()])]);
        let got = (files, attribute(&r, &[change(files, &["T01"])]));
        assert_eq!(got, (files, placed));
    }
    let gate = reds(
        &[],
        SPAN,
        Path::new("/lane"),
        "HOOK TESTS FAILED: review-gate.sh\n",
    );
    let not_a_guard = change(&["rust/guard/src/guards/review_gate.rs"], &["T01"]);
    assert_eq!(attribute(&gate, &[not_a_guard]), Verdict::Unplaced);
}

#[test]
fn a_red_no_unit_or_no_single_change_places_is_unplaced() {
    let (a, b) = ("2026-11-28T03:01:00.000Z", "2026-11-28T03:02:00.000Z");
    let one = [phase(
        "test",
        101,
        a,
        b,
        "/lane",
        &["rust/gate/crates/land"],
    )];
    let r = reds(&one, SPAN, Path::new("/lane"), "");
    // nothing read
    assert_eq!(
        attribute(&[], &[change(&["x"], &["T01"])]),
        Verdict::Unplaced
    );
    // no change under the crate: `rust/gate/crates/landing/` is not `rust/gate/crates/land/`
    assert_eq!(
        attribute(
            &r,
            &[change(
                &["rust/gate/crates/landing/a.rs", "rust/gate/crates/land"],
                &["T01"]
            )]
        ),
        Verdict::Unplaced
    );
    // two changes under it
    let both = [
        change(&["rust/gate/crates/land/a.rs"], &["T01"]),
        change(&["rust/gate/crates/land/b.rs"], &["T02"]),
    ];
    assert_eq!(attribute(&r, &both), Verdict::Unplaced);
    // one unit placed, another not: the batch is unplaced
    let output = "Every refusal:\n  push-checks: nothing named\n  Tx: not a task\n";
    let mut more = r.clone();
    more.extend(reds(&[], SPAN, Path::new("/lane"), output));
    assert_eq!(attribute(&more, &both[..1]), Verdict::Unplaced);
    let tx = reds(
        &[],
        SPAN,
        Path::new("/lane"),
        "Every refusal:\n  T: x\n  T1x: y\n",
    );
    assert_eq!(
        attribute(&tx[..1], &[change(&["a"], &["T"])]),
        Verdict::Unplaced
    );
    assert_eq!(
        attribute(&tx[1..], &[change(&["a"], &["T1x"])]),
        Verdict::Unplaced
    );
}
