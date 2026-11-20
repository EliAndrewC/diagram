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
    let (_dir, root) = quick_repo("task-add");
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
    // an id archived in tasks-done.md is taken (feature 449 T142)
    put(&root, "specs/9001-x/tasks-done.md", "- [x] T09 archived\n");
    assert_eq!(next_id(&d).unwrap(), "T10");
    std::fs::remove_file(d.join("tasks-done.md")).unwrap();
    let said = cli(
        &words(&["9001", "--physical", "--performance"]),
        &root,
        " the next thing ",
    );
    assert_eq!(said.code, 0, "{}", said.stderr);
    assert_eq!(said.stdout, "task-add: T08 filed in specs/9001-x/tasks.md, its section in specs/9001-x/plan.md (the template: fill each <...>)\ntask-add: make quick's checks over it: clean (3 run)\n");
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
    let (_dir, root) = quick_repo("task-add-refusals");
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

/// Files past a megabyte (feature 449, found 2026-11-18): `fancy_regex` gives up a word-boundary pattern's search past a million steps,
/// about one a character on an unanchored search; the id's `.flatten()` over the error it repeats without advancing spun `make task-add`
/// without end on 449's 1.1 MB of tasks and plans; and a tasks.md or plan.md past a megabyte would put the box after the GM's and the
/// section after the close, their one search failed. The id is read to the end, bounded here so that the test cannot spin.
#[test]
fn the_next_id_and_the_anchors_are_read_past_a_megabyte() {
    let dir = l7r_guard::shared::tempdir::TempDir::new("task-add-past-limit");
    let d = dir.path().to_path_buf();
    std::fs::write(d.join("tasks.md"), "- [ ] T01 a\n").unwrap();
    let filler = "plain words of a finished section\n".repeat(40_000);
    std::fs::write(
        d.join("plan-done.md"),
        format!("{filler}## T41 the last archived\n"),
    )
    .unwrap();
    let (tx, rx) = std::sync::mpsc::channel();
    let _scan = std::thread::spawn(move || tx.send(next_id(&d)));
    let id = rx
        .recv_timeout(std::time::Duration::from_secs(20))
        .expect("the id's scan spun past its bound");
    assert_eq!(id.unwrap(), "T42");
    let done = "- [x] T01 a\n".repeat(100_000);
    assert!(
        add_box(&format!("{done}- [ ] GM review\n"), "T02", "b", false)
            .ends_with("- [ ] T02 b\n      research: rendering\n- [ ] GM review\n")
    );
    assert!(
        add_section(&format!("{filler}## T03 - the close\n"), "T02", "x")
            .ends_with("x\n\n## T03 - the close\n")
    );
}

/// Feature 451 FR-013: both of a task's performance marks, as `make task-add` writes them, read as performance work by the one reader
/// the set-down guard and `make task-start` share - `PERF=1`'s checklist heading and a `[perf]` title - and a plain task not.
#[test]
fn perf_1_and_a_perf_title_each_file_a_task_the_reader_calls_performance_work() {
    use l7r_guard::guards::set_down_hooks::performance;
    let (_dir, root) = quick_repo("task-add-perf");
    let d = root.join("specs/9001-x");
    put(&root, "specs/9001-x/tasks.md", "- [x] T01 done\n");
    put(&root, "specs/9001-x/plan.md", "");
    let title_of = |id: &str| {
        let tasks = std::fs::read_to_string(d.join("tasks.md")).unwrap();
        let line = tasks
            .lines()
            .find(|l| l.starts_with(&format!("- [ ] {id} ")))
            .unwrap()
            .to_owned();
        line[format!("- [ ] {id} ").len()..].to_owned()
    };
    assert_eq!(
        cli(&words(&["9001", "--performance"]), &root, "a faster gate").code,
        0
    );
    assert_eq!(
        cli(&words(&["9001"]), &root, "[perf] a faster loop").code,
        0
    );
    assert_eq!(cli(&words(&["9001"]), &root, "a plain task").code, 0);
    let plan = std::fs::read_to_string(d.join("plan.md")).unwrap();
    assert_eq!(title_of("T03"), "[perf] a faster loop");
    assert!(performance("T02", &title_of("T02"), &plan));
    assert!(performance("T03", &title_of("T03"), &plan));
    assert!(!performance("T04", &title_of("T04"), &plan));
}

/// `make quick` of a fixture (feature 451 T19): an EARLY check, red where `early-red` exists, as a ruff failure reads; a LINT, red on
/// each `FR-4nn` of the feature's tasks.md, as spec-lint's check 4 reads a bare id another feature defines, its recipe line continued;
/// a line `make quick` names ruff by, which leaves a file when it runs (a check that reads no specs/ file is run all the same); the
/// closing `printf` and the stamp, each leaving a file if it runs.
pub(super) const QUICK_MAKEFILE: &str = "quick:\n\t@sh early.sh\n\t@sh lint.sh \\\n\t  specs/9001-x/tasks.md\n\t@touch ruffed # python3 -m ruff check l7r/\n\t@printf 'clean\\n' > printed\n\t@touch stamped # state write green-local quick\n";
const EARLY: &str = "[ -f early-red ] || exit 0\necho 'l7r/a.py:3:1: F401 unused import'\nexit 1\n";
const LINT: &str = "grep -n 'FR-4[0-9][0-9]' \"$1\" | sed 's/^\\([0-9]*\\):.*\\(FR-4[0-9][0-9]\\).*/specs\\/9001-x\\/tasks.md:\\1: cites \\2, which spec.md does not define/' | grep . && exit 1\nexit 0\n";

/// A [`repo`] fixture with the quick of [`QUICK_MAKEFILE`].
pub(super) fn quick_repo(tag: &str) -> (l7r_guard::shared::tempdir::TempDir, std::path::PathBuf) {
    let dir = repo(tag);
    let root = root_of(&dir);
    put(&root, "Makefile", QUICK_MAKEFILE);
    put(&root, "early.sh", EARLY);
    put(&root, "lint.sh", LINT);
    (dir, root)
}

fn bytes(root: &std::path::Path) -> (Vec<u8>, Option<Vec<u8>>) {
    let d = root.join("specs/9001-x");
    (
        std::fs::read(d.join("tasks.md")).unwrap(),
        std::fs::read(d.join("plan.md")).ok(),
    )
}

/// RED FIRST (feature 451 T19, FR-011, FR-012): the motivating case, 449 on 2026-11-19 - a task line citing a bare requirement id
/// another feature defines passed `make task-add` and failed `make quick` at the landing. Withdrawn and refused, both files as they
/// were (a plan.md that did not exist does not exist after); a clean line stays; the stamp and the closing line never run, and every
/// other line does - the ruff line too, though it reads no specs/ file (the lead's ruling, 2026-11-20: no skip list to go stale).
#[test]
fn a_line_quick_refuses_is_withdrawn_and_a_clean_line_stays() {
    let (_dir, root) = quick_repo("task-add-quick");
    let before = bytes(&root);
    let refused = cli(&words(&["9001"]), &root, "cite FR-404 bare");
    assert_eq!(refused.code, 2, "{}", refused.stderr);
    assert!(
        refused.stderr.contains("T10 withdrawn"),
        "{}",
        refused.stderr
    );
    assert!(
        refused
            .stderr
            .contains("sh lint.sh specs/9001-x/tasks.md: specs/9001-x/tasks.md:"),
        "{}",
        refused.stderr
    );
    assert!(refused
        .stderr
        .contains("cites FR-404, which spec.md does not define"));
    assert!(refused.stderr.contains("QUICK_OK=\"<reason>\""));
    assert_eq!(bytes(&root), before);
    let kept = cli(&words(&["9001"]), &root, "a clean line");
    assert_eq!(kept.code, 0, "{}", kept.stderr);
    assert!(kept.stdout.contains("make quick's checks over it: clean"));
    assert!(std::fs::read_to_string(root.join("specs/9001-x/tasks.md"))
        .unwrap()
        .contains("- [ ] T10 a clean line\n"));
    for never in ["printed", "stamped"] {
        assert!(!root.join(never).exists(), "{never} ran");
    }
    assert!(root.join("ruffed").exists(), "the ruff line did not run");
    std::fs::remove_file(root.join("specs/9001-x/plan.md")).unwrap();
    let before = bytes(&root);
    assert_eq!(cli(&words(&["9001"]), &root, "FR-405 too").code, 2);
    assert_eq!(bytes(&root), before);
    assert!(before.1.is_none());
}

/// A sequential `make quick` stops at its first red, so a check already red EARLIER (the fixture's ruff) would hide the line's own
/// failure in a later one: each check runs to its own end, and the refusal names the line's failure alone.
#[test]
fn an_earlier_red_check_does_not_hide_the_line_s_own() {
    let (_dir, root) = quick_repo("task-add-quick-early");
    put(&root, "early-red", "");
    let before = bytes(&root);
    let refused = cli(&words(&["9001"]), &root, "cite FR-404 bare");
    assert_eq!(refused.code, 2, "{}", refused.stderr);
    assert!(refused.stderr.contains("cites FR-404"));
    assert!(!refused.stderr.contains("F401"), "{}", refused.stderr);
    assert_eq!(bytes(&root), before);
}

/// A red that was there before the line is not its fault: the finding sits below the box task-add writes, its line number shifted by
/// the box, and is the same finding once line numbers are masked - the line is kept and the red reported as already there.
#[test]
fn a_red_already_there_keeps_the_line() {
    let (_dir, root) = quick_repo("task-add-quick-already");
    put(
        &root,
        "specs/9001-x/tasks.md",
        &format!("{}- [ ] GM review (FR-401)\n", crate::tests::TASKS),
    );
    let kept = cli(&words(&["9001"]), &root, "a clean line");
    assert_eq!(kept.code, 0, "{}", kept.stderr);
    assert!(kept.stderr.contains("already red"), "{}", kept.stderr);
    assert!(kept.stderr.contains("cites FR-401"));
    let tasks = std::fs::read_to_string(root.join("specs/9001-x/tasks.md")).unwrap();
    assert!(tasks
        .contains("- [ ] T10 a clean line\n      research: rendering\n- [ ] GM review (FR-401)\n"));
}

/// A tree whose `make quick` cannot be listed files nothing.
#[test]
fn a_quick_that_cannot_be_listed_files_nothing() {
    let dir = repo("task-add-quick-none");
    let root = root_of(&dir);
    let before = bytes(&root);
    let refused = cli(&words(&["9001"]), &root, "a line");
    assert_eq!(refused.code, 2, "{}", refused.stderr);
    assert!(
        refused.stderr.contains("make -n quick"),
        "{}",
        refused.stderr
    );
    assert_eq!(bytes(&root), before);
}
