//! 451 T464: a landing's first pass judges its feature's plan once, not once a task. Its tick checks asked the plan gate of each task
//! in turn, and each ask read and judged the whole plan again (`ruled_tasks`, `block_status`) before narrowing it to the task: about
//! 2.4 s a task over a 1 MB plan.md, 92 s of a 35-task batch (measured 2026-11-27, an Instant trace per call over a scratch clone of
//! diagram-backlog). A [`Shared`] keeps the task-free part for the asks made through it; each task is told what it was told alone.

use super::super::status::judged;
use super::super::{tick_gate, tick_gate_in, Shared};
use super::{current, feature_at, git, repo, run, write_json, PLAN_TASKS};

/// RED FIRST: three asks through one [`Shared`] judge the plan once and answer as three asks alone; a [`Shared`] made after the plan
/// changed judges it again.
#[test]
fn a_landing_judges_its_plan_once_and_tells_each_task_what_it_was_told_alone() {
    let root = repo();
    std::fs::create_dir_all(root.join("dev")).unwrap();
    let dir = feature_at(&root, Some(PLAN_TASKS), None, "375-x");
    let boxes = "# Tasks\n\n- [ ] T05 the bath\n- [ ] T06 the wells\n";
    std::fs::write(dir.join("tasks.md"), boxes).unwrap();
    let src = write_json(&root, "w.json", &current(&[], "CLEAR", PLAN_TASKS));
    assert_eq!(
        run(&root, &["record", "375", &src, "--as", "spec-fidelity"]).code,
        0
    );
    git(&root, &["add", "-A"]);
    git(&root, &["commit", "-qm", "reviewed"]);
    // T06's section edited after its review: T05's tick passes, T06's is held
    let wells = PLAN_TASKS.replace(
        "- a well by the kitchen",
        "- a well by the kitchen, its depth measured",
    );
    std::fs::write(dir.join("plan.md"), &wells).unwrap();
    let asked = ["T05", "T06", "T05"];
    let alone: Vec<(bool, String)> = asked
        .iter()
        .map(|t| tick_gate(&dir, &root, None, t))
        .collect();
    assert!(alone[0].0 && !alone[1].0);
    assert!(alone[1].1.contains("T06 the wells"));
    let before = judged();
    let shared = Shared::default();
    let together: Vec<(bool, String)> = asked
        .iter()
        .map(|t| tick_gate_in(&dir, &root, None, t, Some(&shared)))
        .collect();
    assert_eq!((judged() - before, &together), (1, &alone));
    // a block outside every task's section changed: the next landing's own judgment holds T05 too
    std::fs::write(
        dir.join("plan.md"),
        wells.replace(
            "Each tub by a door.",
            "Each tub by a door, a drain beside it.",
        ),
    )
    .unwrap();
    let (before, next) = (judged(), Shared::default());
    let (ok, why) = tick_gate_in(&dir, &root, None, "T05", Some(&next));
    assert!(!ok && why.contains("preamble"), "{why}");
    assert_eq!(judged() - before, 1);
}
