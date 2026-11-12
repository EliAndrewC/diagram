//! A held feature's task (feature 449 T131, from `gates/plan_hold.py`): the hold read from the status paragraph, the engine task told
//! from the sure non-engine one, and `HOLD_OK`.

use l7r_gate_core::ci::fixtures::put;

use super::{engine_modules, holder, is_engine_task, refusal, task_lines};
use crate::tests::{repo, root_of};

const HELD: &str = "# F\n\n**Status**: Filed; ON HOLD from 2026-10-24\nuntil feature 9003 closes\n\n**Affects**: tooling\n";

#[test]
fn the_engine_s_module_names_are_read_from_the_tree() {
    let dir = repo("modules");
    let tree = root_of(&dir);
    put(&tree, "l7r/diagram/knots.py", "");
    put(&tree, "l7r/diagram/__init__.py", "");
    put(&tree, "l7r/diagram/sub/__init__.py", "");
    put(&tree, "pool/hamlet.gen.py", "");
    put(&tree, "pool/abc.py", "");
    put(&tree, "rust/phases/src/seats.rs", "");
    put(&tree, "rust/phases/src/lib.rs", "");
    put(&tree, "rust/phases/src/main.rs", "");
    put(&tree, "rust/x/mod.rs", "");
    put(&tree, "rust/.rs", "");
    std::os::unix::fs::symlink(tree.join("l7r/diagram"), tree.join("l7r/linked")).unwrap();
    let names = engine_modules(&tree);
    let listed: Vec<&str> = names.iter().map(String::as_str).collect();
    assert_eq!(
        listed,
        vec!["diagram", "hamlet", "knots", "linked", "seats"]
    );
}

#[test]
fn a_task_s_lines_are_its_line_and_the_indented_lines_under_it() {
    let dir = repo("lines");
    let d = root_of(&dir).join("specs/9001-x");
    put(&d, "tasks.md", "- [ ] T01 a\n  one\n\ttwo\n  - [ ] sub\n- [ ] T02 b\n   - [x] T02 again\n- [ ] T03 c\nafter\n- [ ] T03 d\n");
    assert_eq!(task_lines(&d, "T01").unwrap(), "- [ ] T01 a\n  one\n\ttwo");
    assert_eq!(task_lines(&d, "T02").unwrap(), "   - [x] T02 again");
    assert_eq!(task_lines(&d, "T03").unwrap(), "- [ ] T03 c");
    assert_eq!(task_lines(&d, "T99").unwrap(), "");
    std::fs::remove_file(d.join("tasks.md")).unwrap();
    assert_eq!(task_lines(&d, "T01").unwrap(), "");
}

#[test]
fn an_engine_task_is_one_not_sure_to_be_outside_the_engine() {
    let dir = repo("engine");
    let tree = root_of(&dir);
    put(&tree, "l7r/diagram/knots.py", "");
    let d = tree.join("specs/9001-x");
    let engine = |tasks: &str, section: Option<&str>| {
        put(&d, "tasks.md", tasks);
        is_engine_task(&tree, &d, "T01", section).unwrap()
    };
    assert!(engine("- [ ] T02 x\n", None), "a task not found is unsure");
    assert!(engine("- [ ] T01 edit l7r/diagram/x.py\n", None));
    assert!(engine("- [ ] T01 edit scripts/x for knots\n", None));
    assert!(engine(
        "- [ ] T01 edit scripts/x\n  research: physical\n",
        None
    ));
    assert!(engine(
        "- [ ] T01 edit scripts/x\n",
        Some("touches rust/phases/y.rs")
    ));
    assert!(engine("- [ ] T01 names nothing\n", None));
    assert!(!engine("- [ ] T01 edit scripts/x\n", None));
    assert!(!engine("- [ ] T01 the Makefile\n", Some("")));
    assert!(engine("- [ ] T01 edit my-scripts/x\n", None));
}

#[test]
fn a_held_feature_refuses_an_engine_task_and_admits_another_with_a_reason() {
    let dir = repo("hold");
    let tree = root_of(&dir);
    let d = tree.join("specs/9001-x");
    let ask = |task: &str, ok: &str| refusal(&tree, &d, task, None, ok).unwrap();
    std::fs::remove_file(d.join("spec.md")).unwrap();
    assert_eq!(holder(&d).unwrap(), None, "no spec, no hold");
    assert_eq!(ask("T01", ""), "", "no hold in the status");
    put(&d, "spec.md", HELD);
    assert_eq!(ask("T01", ""), "", "the holder is not there");
    put(
        &tree,
        "specs/9003-holder/spec.md",
        "**Status**: In progress\n",
    );
    put(&tree, "specs/9003-holder/tasks.md", "- [ ] T01 a\n");
    put(
        &d,
        "tasks.md",
        "- [ ] T01 edit scripts/x\n- [ ] T02 edit l7r/y\n",
    );
    assert_eq!(
        ask("T01", "  "),
        "task-start: REFUSED - 9001-x is ON HOLD until 9003-holder closes. T01 does not change the engine, so it may start with a reason: make task-start F=9001 T=T01 HOLD_OK=\"<why it cannot wait>\""
    );
    assert_eq!(ask("T01", "a reason"), "");
    assert!(ask("T02", "a reason").contains("T02 changes the engine"));
    // two holders, or a closed one, hold nothing
    put(&tree, "specs/9003-other/x", "");
    assert_eq!(ask("T02", ""), "");
    std::fs::remove_dir_all(tree.join("specs/9003-other")).unwrap();
    put(&tree, "specs/9003-holder/tasks.md", "- [x] T01 a\n");
    put(
        &tree,
        "specs/9003-holder/spec.md",
        "**Status**: Done 2026-11-12\n",
    );
    assert_eq!(ask("T02", ""), "");
    // a hold in the status paragraph's later line holds; one after the paragraph does not
    put(
        &tree,
        "specs/9003-holder/spec.md",
        "**Status**: In progress\n",
    );
    put(&tree, "specs/9003-holder/tasks.md", "- [ ] T01 a\n");
    put(
        &d,
        "spec.md",
        "**Status**: Filed\n\nON HOLD until feature 9003\n",
    );
    assert_eq!(holder(&d).unwrap(), None);
    put(
        &d,
        "spec.md",
        "**Status**: Filed; ON HOLD\nuntil feature 9003",
    );
    assert_eq!(holder(&d).unwrap(), Some(tree.join("specs/9003-holder")));
    put(&d, "spec.md", "**Status**: ON HOLD until feature 12\n");
    assert_eq!(holder(&d).unwrap(), None);
    // the holder's state unreadable raises
    put(&d, "spec.md", HELD);
    put(&tree, ".specify/affects.json", "[");
    assert!(holder(&d).is_err());
    assert!(refusal(&tree, &d, "T01", None, "").is_err());
}
