//! 451 T359: a task closed by `make task-withdraw` owes no plan review. Its box is ticked `Withdrawn YYYY-MM-DD: <why>` and its
//! unfilled stub removed from plan.md; a stub a whole-plan or a delta review had recorded is then a `(removed)` block of a ticked
//! task with no CLEAR verdict, which every later tick and the push answered for (`status::in_scope`) though nobody decided anything
//! in it. So a withdrawn task's removed block that was a block of its unfilled stub owes nothing ([`l7r_shared::speckit::withdrawn_box`],
//! the one rule of the form; `template::stub_block`, the one stub test, which `make task-withdraw` removes a section by), while a
//! live block that names it and has no other owner is still answered for - and so is a removed block that was filled in (D15b).

use super::super::template::stubs;
use super::super::tick_gate;
use super::{current, feature_at, git, repo, run, write_json, PLAN_TASKS};

/// RED FIRST: the recorded stub of a withdrawn task, removed, holds no later tick - in tasks.md or archived in tasks-done.md - while a
/// task ticked any other way, the words `Withdrawn: <why>` with no date among them, still answers for its removed block.
#[test]
fn a_withdrawn_task_s_removed_stub_holds_no_later_tick() {
    let root = repo();
    std::fs::create_dir_all(root.join("dev")).unwrap();
    // reviewed whole, T06's unfilled stub among its blocks
    let [_, stub, ..] = stubs("T06");
    let template = PLAN_TASKS.replace("## T06 the wells\n\n- a well by the kitchen\n", &stub);
    let dir = feature_at(&root, Some(&template), None, "375-x");
    let boxes = "# Tasks\n\n- [ ] T05 the bath\n- [ ] T06 the wells\n";
    std::fs::write(dir.join("tasks.md"), boxes).unwrap();
    let src = write_json(&root, "w.json", &current(&[], "CLEAR", &template));
    assert_eq!(
        run(&root, &["record", "375", &src, "--as", "spec-fidelity"]).code,
        0
    );
    // T06 withdrawn: its stub gone from the plan, its box ticked with the dated word
    let at = template.find(&stub).unwrap();
    std::fs::write(dir.join("plan.md"), &template[..at]).unwrap();
    let ask = |t: &str| tick_gate(&dir, &root, None, t);
    let line = "- [x] T06 the wells Withdrawn 2026-11-26: a duplicate of T05";
    let ticked = |l: &str| boxes.replace("- [ ] T06 the wells", l);
    std::fs::write(dir.join("tasks.md"), ticked(line)).unwrap();
    // its earlier text unread (no commit holds the plan the review read): not known to be the stub, so answered for
    let (ok, why) = ask("T05");
    assert!(!ok && why.contains("(removed) ### T06"), "{why}");
    // the reviewed plan in the history, as a feature's is: the removed blocks read as the stub's, and nothing is owed
    std::fs::write(dir.join("plan.md"), &template).unwrap();
    git(&root, &["add", "-A"]);
    git(&root, &["commit", "-q", "-m", "the plan as reviewed"]);
    std::fs::write(dir.join("plan.md"), &template[..at]).unwrap();
    assert_eq!(ask("T05"), (true, String::new()));
    // archived by the next tick, it still holds none
    std::fs::write(dir.join("tasks.md"), "# Tasks\n\n- [ ] T05 the bath\n").unwrap();
    std::fs::write(dir.join("tasks-done.md"), format!("# done\n\n{line}\n")).unwrap();
    assert_eq!(ask("T05"), (true, String::new()));
    std::fs::remove_file(dir.join("tasks-done.md")).unwrap();
    // a live block under a heading that only names the withdrawn task, changed: still answered for, as any ticked task's is
    std::fs::write(dir.join("tasks.md"), ticked(line)).unwrap();
    let noted = format!("{}## Notes (T06)\n\n- why it went\n", &template[..at]);
    std::fs::write(dir.join("plan.md"), noted).unwrap();
    let (ok, why) = ask("T05");
    assert!(!ok && why.contains("## Notes (T06)"), "{why}");
    std::fs::write(dir.join("plan.md"), &template[..at]).unwrap();
    // ...and a box closed BUILT INSIDE another task's section (451 T307 part 2, `inside::built_inside_box`): the same exemption
    std::fs::write(
        dir.join("tasks.md"),
        ticked("- [x] T06 the wells built inside T05"),
    )
    .unwrap();
    assert_eq!(ask("T05"), (true, String::new()));
    // ticked by a landing, or with the word and no date (T359's own line quotes that form): its removed block is answered for
    for other in [
        "- [x] T06 the wells",
        "- [x] T06 the wells, ticked with 'Withdrawn: <why>'",
        "- [x] T06 the wells built inside T05 and more words",
    ] {
        std::fs::write(dir.join("tasks.md"), ticked(other)).unwrap();
        let (ok, why) = ask("T05");
        assert!(!ok && why.contains("(removed) ### T06"), "{other}: {why}");
    }
}

/// RED FIRST (T359-D15b): the form of the box alone exempts nothing. A box ticked by hand in the Withdrawn form whose FILLED block
/// was removed is still answered for - only a removed block whose earlier text is the unfilled template's is nobody's decision.
#[test]
fn a_withdrawn_form_box_whose_filled_block_was_removed_is_still_answered_for() {
    let root = repo();
    std::fs::create_dir_all(root.join("dev")).unwrap();
    let dir = feature_at(&root, Some(PLAN_TASKS), None, "375-x");
    let line = "- [x] T06 the wells Withdrawn 2026-11-26: a duplicate of T05";
    let boxes = format!("# Tasks\n\n- [ ] T05 the bath\n{line}\n");
    std::fs::write(dir.join("tasks.md"), boxes).unwrap();
    let src = write_json(&root, "w.json", &current(&[], "CLEAR", PLAN_TASKS));
    assert_eq!(
        run(&root, &["record", "375", &src, "--as", "spec-fidelity"]).code,
        0
    );
    // T06's section was filled in and reviewed (the plan as reviewed in the history, its text read); deleted by hand beside the
    // hand-written box
    git(&root, &["add", "-A"]);
    git(&root, &["commit", "-q", "-m", "the plan as reviewed"]);
    let at = PLAN_TASKS.find("## T06 the wells").unwrap();
    std::fs::write(dir.join("plan.md"), &PLAN_TASKS[..at]).unwrap();
    let (ok, why) = tick_gate(&dir, &root, None, "T05");
    assert!(!ok && why.contains("(removed) ## T06 the wells"), "{why}");
}
