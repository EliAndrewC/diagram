//! The attribution's readers and its phase-2 verdict (feature 461 T15).

use std::path::Path;

use serde_json::{json, Value};

use super::{attribute, reds, refusal, Change, Refusal, Verdict};

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

/// Batch 462-2's first pass (461 T76; `l7r-lane/attempts/462-2-1.log`, 2026-11-28): ONE refusal of T278's over five lines, as `make
/// land` prints it since T76 - a row's own continuation lines four spaces deeper than the rows ([`super::ROWS`]).
const T278: &str = "land: refused before anything ran - nothing landed, nothing ticked. Every refusal:
  T278: tick: refused - 
      (1) tick: refused - 462-efficiency-backlog's plan decisions have no current CLEAR review (feature 243).
      2 block(s) of plan.md changed since their review by more than a typo (feature 375 FR-043): ### T278 (<why: the finding or measurement that files it>), ### T278 Approach (checklist part A) - `make plan-delta F=<n>` builds the review of those blocks alone
      A case that is genuinely exempt: PLAN_REVIEW_OK=\"<reason>\", which is recorded.
      (2) T278's Approach block leaves part A item(s) 12 unanswered (feature 385 D8)
make: *** [Makefile:662: land] Error 2
";

#[test]
fn a_row_s_continuation_lines_are_that_row_so_a_task_s_refusal_over_several_lines_names_its_change()
{
    let batch = [
        change(&["specs/462-efficiency-backlog/plan.md"], &["T278"]),
        change(&["rust/x.rs"], &["T279"]),
    ];
    let r = reds(&[], SPAN, Path::new("/lane"), T278);
    assert_eq!(r.len(), 1);
    assert!(r[0].unit.starts_with("first-pass T278: tick: refused - (1) tick: refused - 462-efficiency-backlog's plan decisions"));
    assert_eq!(refusal(&r, &batch), Refusal::Named(vec![0]));
    assert_eq!(
        attribute(&r, &batch),
        Verdict::Placed(vec![(0, vec![r[0].unit.clone()])])
    );
    // a hold after it is a row of its own, and names no change though it names T278: the runner stops, nothing ejected (461 T15)
    let held = T278.replace(
        "make: *** [Makefile:662: land] Error 2\n",
        "  held by 462 T270 - and T278 cannot land beside it (451 T101): not started\n",
    );
    let r = reds(&[], SPAN, Path::new("/lane"), &held);
    assert_eq!(r.len(), 2);
    assert_eq!(
        refusal(&r, &batch),
        Refusal::Unnamed(vec![
            "first-pass held by 462 T270 - and T278 cannot land beside it (451 T101): not started"
                .to_owned()
        ])
    );
    // the attempt file as the first pass wrote it before T76, every line two spaces in: four rows of five name no change
    let before = T278.replace("\n      ", "\n  ");
    let r = reds(&[], SPAN, Path::new("/lane"), &before);
    assert_eq!(r.len(), 5);
    assert!(matches!(refusal(&r, &batch), Refusal::Unnamed(rows) if rows.len() == 4));
}

/// Batch 462-3's coverage red (461 T86; `l7r-lane/attempts/462-3-1.log`, 2026-11-28): the gate's lines no test reaches, verbatim,
/// under the lane's tree. Both crates' `cover-run` Phase lines were `code` 0, so the record held no red unit and the batch of six
/// was ejected unplaced; each file is touched by 462 T545/T555's change alone.
const LANE: &str = "/diagram/.clones/diagram-backlog-land";
const T545: &str = "rust-checks: cover FAILED on rust/gate/crates/plan
/diagram/.clones/diagram-backlog-land/rust/gate/crates/plan/src/plan/split.rs - lines no test reaches: 88, 208
/diagram/.clones/diagram-backlog-land/rust/gate/crates/plan/src/plan/split/tests.rs - lines no test reaches: 70, 99, 130, 196

rust-checks: cover FAILED on rust/guard/shared
\u{1b}[1m/diagram/.clones/diagram-backlog-land/rust/guard/shared/src/speckit/archive/report.rs - lines no test reaches: 127\u{1b}[0m
/diagram/.clones/diagram-backlog-land/rust/guard/shared/src/speckit/archive/report/tests.rs - lines no test reaches: 62
";

fn batch_462_3() -> [Change; 6] {
    [
        change(
            &[
                "rust/gate/crates/plan/src/plan.rs",
                "rust/gate/crates/plan/src/plan/history.rs",
            ],
            &["T543"],
        ),
        change(
            &[
                "rust/gate/crates/plan/src/plan.rs",
                "rust/gate/crates/plan/src/plan/split.rs",
                "rust/gate/crates/plan/src/plan/split/tests.rs",
                "rust/guard/shared/src/speckit/archive/report.rs",
                "rust/guard/shared/src/speckit/archive/report/tests.rs",
            ],
            &["T545", "T555"],
        ),
        change(
            &["rust/gate/crates/rustc/src/rustc/cover.rs"],
            &["T146", "T206"],
        ),
        change(
            &["rust/gate/crates/bundle/src/record/bundle/depiction.rs"],
            &["T107", "T173"],
        ),
        change(&["rust/guard/shared/src/checks/planhold.rs"], &["T120"]),
        change(
            &["rust/gate/crates/measure/src/measure/task_time.rs"],
            &["T544"],
        ),
    ]
}

#[test]
fn a_line_no_test_reaches_names_the_change_that_touches_its_file() {
    let (start, end) = ("2026-11-28T03:01:00.000Z", "2026-11-28T03:02:00.000Z");
    let events = [
        phase("cover-run", 0, start, end, LANE, &["rust/gate/crates/plan"]),
        phase("cover-run", 0, start, end, LANE, &["rust/guard/shared"]),
    ];
    let read = reds(&events, SPAN, Path::new(LANE), T545);
    let shown: Vec<&str> = read.iter().map(|u| u.unit.as_str()).collect();
    let files = [
        "rust/gate/crates/plan/src/plan/split.rs cover-run",
        "rust/gate/crates/plan/src/plan/split/tests.rs cover-run",
        "rust/guard/shared/src/speckit/archive/report.rs cover-run",
        "rust/guard/shared/src/speckit/archive/report/tests.rs cover-run",
    ];
    assert_eq!(shown, files);
    assert_eq!(
        attribute(&read, &batch_462_3()),
        Verdict::Placed(vec![(1, files.iter().map(|f| (*f).to_owned()).collect())])
    );
    // a file no change touches, or one two changes touch, is unplaced: the halving's (461 T24)
    let mut two = batch_462_3();
    two[0]
        .files
        .push("rust/gate/crates/plan/src/plan/split.rs".to_owned());
    assert_eq!(attribute(&read, &two), Verdict::Unplaced);
    let none = &batch_462_3()[2..];
    assert_eq!(attribute(&read, none), Verdict::Unplaced);
    // beside another red unit, each is placed on its own change
    let lint = [phase(
        "lint",
        1,
        start,
        end,
        LANE,
        &["rust/gate/crates/rustc"],
    )];
    let mut both = reds(&lint, SPAN, Path::new(LANE), T545);
    assert_eq!(both.len(), 5);
    let verdict = attribute(&both, &batch_462_3());
    assert!(
        matches!(&verdict, Verdict::Placed(p) if p.iter().map(|(i, _)| *i).collect::<Vec<_>>() == [1, 2])
    );
    // a path outside the tree is kept whole, and names a change only by that whole path
    both = reds(
        &[],
        SPAN,
        Path::new("/lane"),
        "/elsewhere/x.rs - lines no test reaches: 3\n",
    );
    assert_eq!(both[0].unit, "/elsewhere/x.rs cover-run");
    assert_eq!(
        attribute(&both, &[change(&["x.rs"], &["T01"])]),
        Verdict::Unplaced
    );
}
