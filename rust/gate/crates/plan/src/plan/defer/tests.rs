//! The deferral's form through `make decide` and `make plan-delta`, and `DEFER_FORM_OK` on both (feature 451 T17, D15). Each test has
//! a feature of its own, since the guard log the escape is read back from is one directory for the whole test process.

use std::path::{Path, PathBuf};

use super::super::tests::{current, feature_at, repo, run, run_deferred, write_json};
use super::decided_under;

const TASKS: &str =
    "# Tasks\n\n- [ ] T05 the wells\n- [ ] T123 open one\n- [ ] T124 open two\n- [x] T120 ticked\n";
const FORMED: &str =
    "- The wells break. Not fixed here: outside the files. Filed as T123; lands before T124.";
const NO_ORDER: &str = "- The wells break. Not fixed here: outside the files. Filed as T123.";

fn plan(found: &str) -> String {
    format!("# plan\n\n## T05 the wells\n\n- **Approach**: the wells, by the kitchen.\n\n**Found and left?**\n{found}\n\n**Performance work?** no\n")
}

/// A feature named `name` holding `found`'s plan and the fixture's tasks.
fn at(root: &Path, name: &str, found: &str) -> PathBuf {
    let dir = feature_at(root, Some(&plan(found)), None, name);
    std::fs::write(dir.join("tasks.md"), TASKS).unwrap();
    dir
}

/// The plan recorded CLEAR, then its block changed, so `make plan-delta` lints it.
fn cleared_then_changed(root: &Path, dir: &Path, number: &str) {
    let text = std::fs::read_to_string(dir.join("plan.md")).unwrap();
    let src = write_json(root, "w.json", &current(&[], "CLEAR", &text));
    let got = run(root, &["record", number, &src, "--as", "spec-fidelity"]);
    assert_eq!(got.code, 0, "{}", got.stderr);
    std::fs::write(
        dir.join("plan.md"),
        text.replace("by the kitchen", "by the kitchen door"),
    )
    .unwrap();
}

#[test]
fn decide_passes_a_formed_deferral_and_refuses_each_unformed_one() {
    let root = repo();
    at(&root, "461-formed", FORMED);
    let got = run(&root, &["decide", "461", "T05"]);
    assert_eq!(got.code, 0, "{}", got.stderr);
    for (number, found, words) in [
        ("462", NO_ORDER, "no order"),
        ("463", "- The wells break. Filed as T123; lands before T124.", "no reason"),
        ("464", "- The wells break. Not fixed here: outside the files. Lands before T124.", "no task id"),
        ("465", "- The wells break. Not fixed here: outside the files. Filed as T120; lands before T124.", "T120 is not an open task"),
        ("466", "- The wells break. Not fixed here: outside the files. Filed as T123; lands before T123.", "lands before its own id T123"),
    ] {
        at(&root, &format!("{number}-x"), found);
        let got = run(&root, &["decide", number, "T05"]);
        assert_eq!(got.code, 2, "{found}");
        assert!(got.stderr.contains(words), "{}", got.stderr);
        assert!(got.stderr.contains("plan.md:8: "), "{}", got.stderr);
        assert!(got.stderr.contains("DEFER_FORM_OK"), "{}", got.stderr);
    }
}

#[test]
fn a_decided_section_is_not_refused_later_because_its_task_landed() {
    let root = repo();
    let dir = at(&root, "471-landed", FORMED);
    assert_eq!(run(&root, &["decide", "471", "T05"]).code, 0);
    cleared_then_changed(&root, &dir, "471");
    std::fs::write(
        dir.join("tasks.md"),
        TASKS.replace("- [ ] T124", "- [x] T124"),
    )
    .unwrap();
    let got = run(&root, &["delta", "471"]);
    assert_eq!(got.code, 0, "{}", got.stderr);
    // the same block, never decided, with an id filed nowhere: refused by plan-delta too (the timeless half)
    let dir = at(&root, "472-nowhere", &FORMED.replace("T124", "T998"));
    cleared_then_changed(&root, &dir, "472");
    let got = run(&root, &["delta", "472"]);
    assert_eq!(got.code, 1);
    assert!(
        got.stderr.contains("T998 is filed in no tasks.md"),
        "{}",
        got.stderr
    );
}

#[test]
fn a_section_decided_under_the_escape_keeps_it_when_its_block_changes() {
    let root = repo();
    let dir = at(&root, "481-escaped", NO_ORDER);
    assert_eq!(run(&root, &["decide", "481", "T05"]).code, 2);
    let got = run_deferred(
        &root,
        &["decide", "481", "T05"],
        "the order waits on the GM's ruling",
    );
    assert_eq!(got.code, 0, "{}", got.stderr);
    assert!(decided_under(&dir).contains("T05"));
    cleared_then_changed(&root, &dir, "481");
    let got = run(&root, &["delta", "481"]);
    assert_eq!(got.code, 0, "{}", got.stderr);
    // the same block never decided under it is refused
    let dir = at(&root, "482-plain", NO_ORDER);
    cleared_then_changed(&root, &dir, "482");
    assert!(decided_under(&dir).is_empty());
    let got = run(&root, &["delta", "482"]);
    assert_eq!(got.code, 1);
    assert!(got.stderr.contains("no order"), "{}", got.stderr);
    // plan-delta takes the escape itself, and records it
    let got = run_deferred(
        &root,
        &["delta", "482"],
        "a section never decided, ordered later",
    );
    assert_eq!(got.code, 0, "{}", got.stderr);
    assert!(decided_under(&dir).contains("plan-delta"));
}

#[test]
fn the_escape_needs_a_reason_and_leaves_the_other_findings() {
    let root = repo();
    let dir = at(&root, "491-thin", NO_ORDER);
    for verb in ["decide", "delta"] {
        let words: &[&str] = if verb == "decide" {
            &["decide", "491", "T05"]
        } else {
            &["delta", "491"]
        };
        let got = run_deferred(&root, words, "because");
        assert_eq!(got.code, 2, "{verb}");
        assert!(
            got.stderr.contains("DEFER_FORM_OK needs a REASON"),
            "{}",
            got.stderr
        );
    }
    assert!(decided_under(&dir).is_empty());
    let text = plan(NO_ORDER).replace("the wells, by", "the check takes 48 s, by");
    std::fs::write(dir.join("plan.md"), text).unwrap();
    let got = run_deferred(
        &root,
        &["decide", "491", "T05"],
        "the order waits on the GM's ruling",
    );
    assert_eq!(got.code, 2);
    assert!(
        got.stderr.contains("48 s") && !got.stderr.contains("no order"),
        "{}",
        got.stderr
    );
    // a refused run records nothing, so the section is not taken for decided under the escape
    assert!(decided_under(&dir).is_empty());
    // plan-delta records the escape only where it excused a finding
    let plain = at(&root, "492-formed", FORMED);
    cleared_then_changed(&root, &plain, "492");
    let got = run_deferred(&root, &["delta", "492"], "nothing here needs it at all");
    assert_eq!(got.code, 0, "{}", got.stderr);
    assert!(decided_under(&plain).is_empty());
}

/// History (D15): plan-done.md is read by neither `make decide` (its section is plan.md's) nor `make plan-delta`'s lint (plan.md's
/// changed blocks), so an archived section's old deferral form never holds a landing.
#[test]
fn an_archived_section_is_never_judged() {
    let root = repo();
    let dir = at(&root, "495-archived", FORMED);
    std::fs::write(
        dir.join("plan-done.md"),
        plan(NO_ORDER).replace("T05", "T120"),
    )
    .unwrap();
    cleared_then_changed(&root, &dir, "495");
    let got = run(&root, &["delta", "495"]);
    assert_eq!(got.code, 0, "{}", got.stderr);
    let got = run(&root, &["decide", "495", "T120"]);
    assert_eq!(got.code, 2);
    assert!(
        got.stderr.contains("no plan section names T120"),
        "{}",
        got.stderr
    );
}

/// Only the plan gate's own escape records count: a blocked entry of the rule, or another guard's, names no task (feature 451 T17).
#[test]
fn only_an_escaped_record_of_the_plan_gate_counts() {
    let root = repo();
    let dir = at(&root, "497-records", NO_ORDER);
    let log = super::super::tests::quiet_census();
    for (name, guard, event) in [
        ("a", "plan-gate", "blocked"),
        ("b", "other", "escaped"),
        ("c", "plan-gate", "escaped"),
    ] {
        let entry = serde_json::json!({"guard": guard, "event": event, "rule": "defer-form-ok", "detail": format!("497-records T0{name}: why not")});
        std::fs::write(log.join(format!("t17-{name}.json")), entry.to_string()).unwrap();
    }
    std::fs::write(log.join("t17-d.json"), "defer-form-ok, not JSON").unwrap();
    assert_eq!(decided_under(&dir).into_iter().collect::<Vec<_>>(), ["T0c"]);
    assert!(super::super::environment("PATH").is_some());
}
