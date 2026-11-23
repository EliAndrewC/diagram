//! 451 T180: a heading that only names a task makes it no owner of another task's own section. 449 T377's filled heading names T351
//! (`ask:glyph-occasions-emit-449-T351`); once T351 was ticked and its section archived, that mention was T351's whole "section", so
//! each later tick of the landing, answering for the ticked T351, was refused on T377's open block (observed 2026-11-23,
//! `/tmp/land351/land1.log`: T358 and six more refused on `### T377 (the round arbiter's ...`).

use super::super::tick_gate;
use super::{current, feature_at, repo, run, write_json, PLAN_TASKS};

#[test]
fn a_ticked_task_named_in_an_open_task_s_heading_owns_none_of_its_section() {
    let root = repo();
    std::fs::create_dir_all(root.join("dev")).unwrap();
    // reviewed whole with T06's template heading; T04 ticked and its section archived
    let template = PLAN_TASKS.replace("## T06 the wells", "## T06 (<why: the finding>)");
    let dir = feature_at(&root, Some(&template), None, "375-x");
    let boxes = "# Tasks\n\n- [x] T04 the drain\n- [ ] T05 the bath\n- [ ] T06 the wells\n";
    std::fs::write(dir.join("tasks.md"), boxes).unwrap();
    let src = write_json(&root, "w.json", &current(&[], "CLEAR", &template));
    assert_eq!(
        run(&root, &["record", "375", &src, "--as", "spec-fidelity"]).code,
        0
    );
    // T06's builder fills its heading, naming the ticked T04; nobody has reviewed it yet
    let named = "## T06 (filed by T04's review) the wells";
    let plan = PLAN_TASKS.replace("## T06 the wells", named);
    std::fs::write(dir.join("plan.md"), &plan).unwrap();
    let ask = |t: &str| tick_gate(&dir, &root, None, t);
    // T05's tick answers for T05 and the ticked T04, never for T06's open section
    assert_eq!(ask("T05"), (true, String::new()));
    // T06's own tick still owes it
    let (ok, why) = ask("T06");
    assert!(!ok && why.contains(named), "{why}");
    // a heading naming T04 that is no task's own still answers to T04's tick, as before
    let shared = plan.replace(
        "# plan\n\n",
        "# plan\n\n## The drains (T04)\n\n- one drain a tub\n\n",
    );
    std::fs::write(dir.join("plan.md"), shared).unwrap();
    let (ok, why) = ask("T05");
    assert!(!ok && why.contains("## The drains (T04)"), "{why}");
}
