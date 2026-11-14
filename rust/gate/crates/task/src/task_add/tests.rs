//! `l7r-gate task-add` (feature 449 T135, from `task-add.py`): the next id, the box before the GM's, the section before the close, the
//! template and its performance checklist, and each refusal and raise.

use l7r_gate_core::ci::fixtures::put;
use l7r_gate_plan::plan::template::TEMPLATE;

use super::{add_box, add_section, cli, lacks_red_exit, next_id};
use crate::tests::{repo, root_of};

fn words(a: &[&str]) -> Vec<String> {
    a.iter().map(|s| (*s).to_owned()).collect()
}

#[test]
fn a_task_takes_the_next_id_and_its_box_and_section_land_in_place() {
    let dir = repo("task-add");
    let root = root_of(&dir);
    let d = root.join("specs/9001-x");
    put(
        &root,
        "specs/9001-x/tasks.md",
        "- [x] T01 done\n- [ ] T02 quotes (385 T147)\n- [ ] GM review (make gm-reviewed F=9001)\n",
    );
    put(
        &root,
        "specs/9001-x/plan.md",
        "## T03 a section\n\n## T04 - the close\n",
    );
    put(
        &root,
        "specs/9001-x/plan-done.md",
        "  - [X] T07b archived\n",
    );
    assert_eq!(next_id(&d).unwrap(), "T08");
    let said = cli(
        &words(&["9001", "--physical", "--performance"]),
        &root,
        " the next thing ",
    );
    assert_eq!(said.code, 0, "{}", said.stderr);
    assert_eq!(said.stdout, "task-add: T08 filed in specs/9001-x/tasks.md, its section in specs/9001-x/plan.md (the template: fill each <...>)\n");
    let tasks = std::fs::read_to_string(d.join("tasks.md")).unwrap();
    assert!(tasks.contains("- [ ] T08 the next thing\n      research: physical\n      - [ ] research pass  - [ ] source-reader confirmed"));
    assert!(tasks.find("T08").unwrap() < tasks.find("GM review").unwrap());
    let plan = std::fs::read_to_string(d.join("plan.md")).unwrap();
    assert!(
        plan.starts_with("## T03 a section\n\n### T08 (<why:")
            && plan.ends_with("\n\n## T04 - the close\n")
    );
    assert!(plan.contains("### T08 Performance checklist"));
    // a section of the caller's, its item 6 lacking the red exit: warned, filed
    put(
        &root,
        "section.md",
        "### {T} mine\n\n6. **The exits.** Green: done.\n",
    );
    let own = cli(&words(&["9001", "--section", "section.md"]), &root, "mine");
    assert_eq!(own.code, 0);
    assert!(
        own.stderr.contains("checklist item 6 has no red exit") && !own.stdout.contains("template")
    );
    assert!(std::fs::read_to_string(d.join("plan.md"))
        .unwrap()
        .contains("### T09 mine\n\n6. **The exits.** Green: done.\n\n## T04"));
}

#[test]
fn the_box_and_the_section_go_at_the_end_with_no_anchor() {
    assert_eq!(
        add_box("- [ ] T01 a", "T02", "b", false),
        "- [ ] T01 a\n- [ ] T02 b\n      research: rendering\n"
    );
    assert_eq!(
        add_box("", "T01", "b", false),
        "\n- [ ] T01 b\n      research: rendering\n"
    );
    assert_eq!(
        add_section("# plan", "T02", "### {T}\n\n\n"),
        "# plan\n\n### T02\n\n"
    );
    assert_eq!(add_section("", "T02", "x"), "\n\nx\n\n");
    assert!(!lacks_red_exit(TEMPLATE) && lacks_red_exit("no item six"));
}

#[test]
fn each_refusal_and_raise() {
    let dir = repo("task-add-refusals");
    let root = root_of(&dir);
    let d = root.join("specs/9001-x");
    let usage = |args: &[&str], title: &str| cli(&words(args), &root, title).code;
    assert_eq!(usage(&["9001"], "  "), 2);
    assert_eq!(usage(&[], "t"), 2);
    assert_eq!(usage(&["9001", "extra"], "t"), 2);
    assert_eq!(usage(&["9001", "--section"], "t"), 0);
    let none = cli(&words(&["99999"]), &root, "t");
    assert!(
        none.code == 2
            && none
                .stderr
                .contains("no single specs/99999* directory with a tasks.md under")
    );
    let missing = cli(&words(&["9001", "--section", "nope.md"]), &root, "t");
    assert_eq!(
        (missing.code, missing.stderr.as_str()),
        (2, "task-add: SECTION=nope.md is not a file\n")
    );
    // a feature with no plan gets one; files that are not UTF-8 raise, the warning printed first
    std::fs::remove_file(d.join("plan.md")).ok();
    assert_eq!(cli(&words(&["9001"]), &root, "t").code, 0);
    assert!(d.join("plan.md").is_file());
    put(&root, "bad.md", "x");
    std::fs::write(root.join("bad.md"), [0xff]).unwrap();
    assert_eq!(
        cli(&words(&["9001", "--section", "bad.md"]), &root, "t").code,
        1
    );
    put(&root, "ok.md", "### {T}\n");
    std::fs::write(d.join("plan.md"), [0xff]).unwrap();
    let raised = cli(&words(&["9001", "--section", "ok.md"]), &root, "t");
    assert!(
        raised.code == 1
            && raised
                .stderr
                .starts_with("task-add: SECTION=ok.md's checklist item 6")
    );
    std::fs::write(d.join("plan-done.md"), [0xff]).unwrap();
    assert_eq!(cli(&words(&["9001"]), &root, "t").code, 1);
    std::fs::remove_file(d.join("plan-done.md")).unwrap();
    std::fs::write(d.join("plan.md"), "").unwrap();
    // a feature named by an absolute path is outside the root: written, then the Python's `relative_to` raised
    let outside = l7r_gate_core::ci::fixtures::scratch("task-add-outside");
    put(&outside, "tasks.md", "- [ ] T01 a\n");
    let far = cli(&words(&[outside.to_str().unwrap()]), &root, "t");
    assert_eq!(far.code, 1);
    assert!(std::fs::read_to_string(outside.join("tasks.md"))
        .unwrap()
        .contains("T02 t"));
    // a tasks.md that cannot be written
    let ro = |m: &str| {
        std::process::Command::new("chmod")
            .arg(m)
            .arg(d.join("tasks.md"))
            .status()
            .unwrap()
    };
    ro("444");
    let blocked = cli(&words(&["9001"]), &root, "t");
    ro("644");
    assert_eq!(blocked.code, 1);
    std::fs::write(d.join("plan.md"), "").unwrap();
    let plan_ro = |m: &str| {
        std::process::Command::new("chmod")
            .arg(m)
            .arg(d.join("plan.md"))
            .status()
            .unwrap()
    };
    plan_ro("444");
    let blocked = cli(&words(&["9001"]), &root, "t");
    plan_ro("644");
    assert_eq!(blocked.code, 1);
    std::fs::write(d.join("tasks.md"), [0xff]).unwrap();
    assert_eq!(cli(&words(&["9001"]), &root, "t").code, 1);
    assert_eq!(crate::cli("task-add", &words(&[]), &root).code, 2);
}
