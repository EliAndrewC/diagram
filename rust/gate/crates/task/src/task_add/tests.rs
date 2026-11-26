//! `l7r-gate task-add` (feature 449 T135, from `task-add.py`): the next id, the box before the GM's, the section before the close, the
//! template and its performance checklist, and each refusal and raise.

use l7r_gate_core::ci::fixtures::put;
use l7r_gate_plan::plan::template::TEMPLATE;

use super::{cli, lacks_red_exit, next_id, Insert};
use crate::tests::{repo, root_of};

/// The test's files committed and pushed, so `main` and `origin/main` hold the ids its tree does (451 T255 reads both).
fn landed(root: &std::path::Path) {
    crate::git(root, &["add", "-A"]);
    crate::git(root, &["commit", "-qm", "the test's files"]);
    crate::git(root, &["push", "-q", "origin", "main"]);
}

fn words(a: &[&str]) -> Vec<String> {
    a.iter().map(|s| (*s).to_owned()).collect()
}

/// `tasks` with the box [`super::add_box`] puts in.
fn add_box(tasks: &str, tid: &str, title: &str, physical: bool) -> String {
    super::add_box(tasks, tid, title, physical).applied(tasks)
}

/// `plan` with the section [`super::add_section`] puts in.
fn add_section(plan: &str, tid: &str, section: &str) -> String {
    super::add_section(plan, tid, section).applied(plan)
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
    landed(&root);
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
    let dir = l7r_shared::tempdir::TempDir::new("task-add-past-limit");
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
    use l7r_shared::guards::set_down_hooks::performance;
    let (_dir, root) = quick_repo("task-add-perf");
    let d = root.join("specs/9001-x");
    put(&root, "specs/9001-x/tasks.md", "- [x] T01 done\n");
    put(&root, "specs/9001-x/plan.md", "");
    landed(&root);
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
pub(super) fn quick_repo(tag: &str) -> (l7r_shared::tempdir::TempDir, std::path::PathBuf) {
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

/// Each filing's own text read back: its box in tasks.md and its section's heading in plan.md, by its id.
fn own_lines(root: &std::path::Path, tid: &str, title: &str) -> (usize, usize) {
    let d = root.join("specs/9001-x");
    let tasks = std::fs::read_to_string(d.join("tasks.md")).unwrap();
    let plan = std::fs::read_to_string(d.join("plan.md")).unwrap_or_default();
    (
        tasks.matches(&format!("- [ ] {tid} {title}\n")).count(),
        plan.matches(&format!("### {tid} (")).count(),
    )
}

/// RED FIRST (feature 451 T84): two `make task-add` of one feature at once, its quick red already and slow. Measured 2026-11-21 with
/// the binary (`/tmp/t84/race.sh red 6 3`): 6 of 6 rounds lost both boxes and both sections, each run printing "filed ... already red
/// ... so it is kept" - each restored the whole-file copies it took before its quick runs over the other's filing. The second starts a
/// tenth of a second into the first's run of quick, which takes three tenths: both are kept, the second the next id.
#[test]
fn two_filings_at_once_keep_both_boxes_and_both_sections() {
    let (_dir, root) = quick_repo("task-add-two-at-once");
    put(&root, "Makefile", "quick:\n\t@sh slow.sh\n");
    put(
        &root,
        "slow.sh",
        "touch running; sleep 0.3; echo 'l7r/a.py:3:1: F401 unused import'; exit 1\n",
    );
    let first = {
        let root = root.clone();
        std::thread::spawn(move || cli(&words(&["9001"]), &root, "the first filing"))
    };
    let started = std::time::Instant::now();
    while !root.join("running").exists() {
        assert!(started.elapsed().as_secs() < 20, "quick never ran");
        std::thread::sleep(std::time::Duration::from_millis(5));
    }
    std::thread::sleep(std::time::Duration::from_millis(100));
    let second = cli(&words(&["9001"]), &root, "the second filing");
    let first = first.join().unwrap();
    assert_eq!(first.code, 0, "{}", first.stderr);
    assert_eq!(second.code, 0, "{}", second.stderr);
    assert!(first.stdout.contains("T10 filed"), "{}", first.stdout);
    assert!(second.stdout.contains("T11 filed"), "{}", second.stdout);
    let (first_own, second_own) = (
        own_lines(&root, "T10", "the first filing"),
        own_lines(&root, "T11", "the second filing"),
    );
    assert_eq!(first_own, (1, 1), "the first filing lost");
    assert_eq!(second_own, (1, 1), "the second filing lost");
}

/// The other writer of [`a_refused_line_is_withdrawn_and_another_writer_s_lines_stay`] and its red-already twin: each run of quick
/// appends its own line to tasks.md and to plan.md, numbered by the run, as a session's edit landing while quick runs would.
const OTHER: &str = "n=$(( $(cat runs 2>/dev/null || echo 0) + 1 )); echo $n > runs\necho \"- another writer's line $n\" >> specs/9001-x/tasks.md\necho \"## another writer's section $n\" >> specs/9001-x/plan.md\n";

/// RED FIRST (feature 451 T84): a line quick refuses is withdrawn by taking out its own box and section, never by writing back the
/// files as they were before it - which threw away another writer's lines added while quick ran (measured 2026-11-21,
/// `/tmp/t84/midedit-refused.sh 3 0.5`: 3 of 3 rounds lost a line appended half a second in).
#[test]
fn a_refused_line_is_withdrawn_and_another_writer_s_lines_stay() {
    let (_dir, root) = quick_repo("task-add-withdrawn-other");
    put(
        &root,
        "Makefile",
        "quick:\n\t@sh other.sh\n\t@sh lint.sh specs/9001-x/tasks.md\n",
    );
    put(&root, "other.sh", OTHER);
    let (tasks, plan) = bytes(&root);
    let refused = cli(&words(&["9001"]), &root, "cite FR-404 bare");
    assert_eq!(refused.code, 2, "{}", refused.stderr);
    assert!(
        refused.stderr.contains("T10 withdrawn"),
        "{}",
        refused.stderr
    );
    let d = root.join("specs/9001-x");
    let mut want_tasks = String::from_utf8(tasks).unwrap();
    want_tasks += "- another writer's line 1\n- another writer's line 2\n";
    let mut want_plan = String::from_utf8(plan.unwrap()).unwrap();
    want_plan += "## another writer's section 1\n## another writer's section 2\n";
    assert_eq!(
        std::fs::read_to_string(d.join("tasks.md")).unwrap(),
        want_tasks
    );
    assert_eq!(
        std::fs::read_to_string(d.join("plan.md")).unwrap(),
        want_plan
    );
    // a plan.md the filing made is kept when another writer put lines in it, holding only theirs
    std::fs::remove_file(d.join("plan.md")).unwrap();
    assert_eq!(cli(&words(&["9001"]), &root, "FR-405 too").code, 2);
    assert_eq!(
        std::fs::read_to_string(d.join("plan.md")).unwrap(),
        "## another writer's section 3\n## another writer's section 4\n"
    );
}

/// RED FIRST (feature 451 T84): a red already there keeps the line with no copy of the files written back - which threw away another
/// writer's edit made during the run without the line (measured 2026-11-21, `/tmp/t84/midedit.sh 3 1.5`: 3 of 3 rounds lost it; one
/// made during the run with the line, 0 of 3).
#[test]
fn a_red_already_there_keeps_another_writer_s_lines_made_while_quick_ran() {
    let (_dir, root) = quick_repo("task-add-already-other");
    put(&root, "Makefile", "quick:\n\t@sh other.sh\n");
    put(
        &root,
        "other.sh",
        &format!("{OTHER}echo 'l7r/a.py:3:1: F401 unused import'\nexit 1\n"),
    );
    let kept = cli(&words(&["9001"]), &root, "a clean line");
    assert_eq!(kept.code, 0, "{}", kept.stderr);
    assert!(kept.stderr.contains("already red"), "{}", kept.stderr);
    assert_eq!(own_lines(&root, "T10", "a clean line"), (1, 1));
    let d = root.join("specs/9001-x");
    let tasks = std::fs::read_to_string(d.join("tasks.md")).unwrap();
    let plan = std::fs::read_to_string(d.join("plan.md")).unwrap();
    for n in [1, 2] {
        let (line, section) = (
            format!("- another writer's line {n}\n"),
            format!("## another writer's section {n}\n"),
        );
        assert!(tasks.contains(&line), "{line} lost");
        assert!(plan.contains(&section), "{section} lost");
    }
}

/// A withdrawal takes out the copy nearest where the text went - another writer's edit above it moves it - and none when no copy is
/// left; a text that occurs twice loses only that one.
#[test]
fn a_withdrawal_takes_out_the_copy_nearest_where_it_went() {
    let put_in = Insert {
        at: 4,
        text: "box\n".to_owned(),
    };
    assert_eq!(put_in.applied("one\ntwo\n"), "one\nbox\ntwo\n");
    assert_eq!(put_in.withdrawn("one\nbox\ntwo\n").unwrap(), "one\ntwo\n");
    // an edit above moved it five bytes on; a same-text line near the end is another's
    assert_eq!(
        put_in.withdrawn("zero\none\nbox\ntwo\nbox\n").unwrap(),
        "zero\none\ntwo\nbox\n"
    );
    assert_eq!(put_in.withdrawn("one\ntwo\n"), None);
}

/// The lock path of the fixture's feature: `task-add-9001-x.lock` in the git common directory.
fn lock_of(root: &std::path::Path) -> std::path::PathBuf {
    l7r_gate_core::codeid::common_git_dir(root)
        .unwrap()
        .join("task-add-9001-x.lock")
}

/// Another filing holding the feature's lock past the wait (`L7R_TASK_ADD_LOCK_WAIT`): refused, nothing written, the lock file named;
/// a lock file that cannot be opened raises, nothing written either.
#[test]
fn a_filing_that_cannot_take_the_lock_writes_nothing() {
    let (_dir, root) = quick_repo("task-add-lock-held");
    let before = bytes(&root);
    let lock = lock_of(&root);
    let held = l7r_shared::tool::flock_within(&lock, 0.0).unwrap().unwrap();
    let env = crate::tests::env_of(&[("L7R_TASK_ADD_LOCK_WAIT", "0.05")]);
    let refused = super::cli_with(&words(&["9001"]), &root, "a line", &env);
    assert_eq!(refused.code, 2, "{}", refused.stderr);
    assert!(
        refused.stderr.contains(&format!(
            "another make task-add of 9001-x still holds {} after 0.05 s",
            lock.display()
        )),
        "{}",
        refused.stderr
    );
    assert!(refused.stderr.contains("fuser -v"), "{}", refused.stderr);
    assert_eq!(bytes(&root), before);
    drop(held);
    std::fs::remove_file(&lock).unwrap();
    std::fs::create_dir_all(&lock).unwrap();
    let raised = cli(&words(&["9001"]), &root, "a line");
    assert_eq!(raised.code, 1, "{}", raised.stderr);
    assert!(
        raised.stderr.contains(&lock.display().to_string()),
        "{}",
        raised.stderr
    );
    assert_eq!(bytes(&root), before);
}

/// A box something else took out, or a plan.md it left unreadable, while quick ran: the withdrawal cannot take its own text out of
/// it, and raises naming the file, writing nothing over it.
#[test]
fn a_withdrawal_whose_own_text_is_gone_raises() {
    let (_dir, root) = quick_repo("task-add-own-gone");
    put(
        &root,
        "Makefile",
        "quick:\n\t@sed -i '/^- \\[ \\] T10 /d' specs/9001-x/tasks.md; exit 1\n",
    );
    let gone = cli(&words(&["9001"]), &root, "a line");
    assert_eq!(gone.code, 1, "{}", gone.stderr);
    assert!(
        gone.stderr.contains("T10's box is no longer in")
            && gone.stderr.contains("tasks.md as it was written"),
        "{}",
        gone.stderr
    );
    // the section is taken out all the same
    assert_eq!(own_lines(&root, "T10", "a line"), (0, 0));
    // a script, as a recipe line opening with `printf` is quick's closing line and never run
    put(&root, "Makefile", "quick:\n\t@sh unreadable.sh\n");
    put(
        &root,
        "unreadable.sh",
        "printf '\\377' >> specs/9001-x/plan.md; exit 1\n",
    );
    let unreadable = cli(&words(&["9001"]), &root, "a line");
    assert_eq!(unreadable.code, 1, "{}", unreadable.stderr);
    assert!(
        unreadable.stderr.contains("UnicodeDecodeError") && unreadable.stderr.contains("plan.md"),
        "{}",
        unreadable.stderr
    );
    // a plan.md something else removed while quick ran
    std::fs::write(root.join("specs/9001-x/plan.md"), "").unwrap();
    put(
        &root,
        "Makefile",
        "quick:\n\t@rm specs/9001-x/plan.md; exit 1\n",
    );
    let removed = cli(&words(&["9001"]), &root, "a line");
    assert_eq!(removed.code, 1, "{}", removed.stderr);
    assert!(
        removed.stderr.contains("plan.md: No such file"),
        "{}",
        removed.stderr
    );
}

/// A tree git does not know: the lock goes in `<root>/.git`, the filing goes ahead.
#[test]
fn a_tree_outside_git_locks_in_its_own_git_directory() {
    let dir = l7r_shared::tempdir::TempDir::new("task-add-no-git");
    let root = dir.path().to_path_buf();
    let outside = l7r_gate_core::codeid::common_git_dir(&root).is_none();
    assert!(outside, "the scratch is inside a repository");
    put(&root, "Makefile", "quick:\n\t@true\n");
    put(&root, "specs/9001-x/tasks.md", "- [x] T01 done\n");
    let filed = cli(&words(&["9001"]), &root, "a line");
    assert_eq!(filed.code, 0, "{}", filed.stderr);
    assert!(root.join(".git/task-add-9001-x.lock").is_file());
    assert_eq!(own_lines(&root, "T02", "a line"), (1, 1));
}

/// RED FIRST (feature 451 T255; the parallel trials of 2026-11-25, T247 and T248 each filed twice): two worktrees of one clone, each
/// filing a task of one feature with nothing committed between, take two ids - the second tree reads the first's reservation in the
/// shared git directory, not only its own tasks.md. A withdrawn filing gives its id back; an id only `main` holds is taken too.
#[test]
fn two_worktrees_never_take_one_id() {
    let (dir, root) = quick_repo("task-add-two-trees");
    put(&root, "Makefile", "quick:\n\t@true\n");
    crate::git(&root, &["add", "-A"]);
    crate::git(&root, &["commit", "-qm", "quick"]);
    let other = dir.join("other");
    let (code, _) = crate::git(
        &root,
        &[
            "worktree",
            "add",
            "-q",
            "--detach",
            &other.to_string_lossy(),
        ],
    );
    assert_eq!(code, Some(0));
    let first = cli(&words(&["9001"]), &root, "the first tree's");
    assert!(first.stdout.contains("T10 filed"), "{}", first.stdout);
    let second = cli(&words(&["9001"]), &other, "the second tree's");
    assert!(second.stdout.contains("T11 filed"), "{}", second.stdout);
    // the reservation of a filing withdrawn is given back, and one main holds counts though no file of this tree has it
    super::release(&root.join("specs/9001-x"), "T11");
    assert_eq!(next_id(&root.join("specs/9001-x")).unwrap(), "T11");
    std::fs::remove_file(root.join(".git").join(super::RESERVED)).unwrap();
    crate::git(&root, &["commit", "-qam", "the first tree's filing"]);
    crate::git(&other, &["checkout", "-q", "--", "specs"]);
    assert_eq!(next_id(&other.join("specs/9001-x")).unwrap(), "T11");
}

/// The reservation's two edges (451 T255): a tree git does not know keeps none and gives none back, and a reservation file that
/// cannot be written refuses the filing by its path.
#[test]
fn a_tree_outside_git_reserves_nothing_and_an_unwritable_reservation_is_named() {
    let outside = l7r_gate_core::ci::fixtures::scratch("task-add-no-git");
    assert_eq!(super::reserve(&outside, "T1"), Ok(()));
    super::release(&outside, "T1");
    let (_dir, root) = quick_repo("task-add-unwritable");
    std::fs::create_dir_all(root.join(".git").join(super::RESERVED)).unwrap();
    let refused = super::reserve(&root.join("specs/9001-x"), "T1").unwrap_err();
    assert!(refused.contains(super::RESERVED), "{refused}");
}

/// THE MEASUREMENT OF 451 T289 (2026-11-26), kept as a test: two worktrees of one clone filing AT ONCE - the second starts while the
/// first holds the filing lock through its slow quick - take two ids, and each writes its box and its section into its own tree only.
/// Green on the code as T255 left it (the lock and the reservations are both in the git common directory), so T289 changed nothing
/// here: a builder's `make task-add` from its pool tree already takes an id no other tree of the clone can.
#[test]
fn two_worktrees_filing_at_once_take_two_ids_each_in_its_own_tree() {
    let (dir, root) = quick_repo("task-add-two-trees-at-once");
    put(&root, "Makefile", "quick:\n\t@sh slow.sh\n");
    put(&root, "slow.sh", "touch running; sleep 0.3\n");
    crate::git(&root, &["add", "-A"]);
    crate::git(&root, &["commit", "-qm", "a slow quick"]);
    let other = dir.join("other");
    let (code, _) = crate::git(
        &root,
        &[
            "worktree",
            "add",
            "-q",
            "--detach",
            &other.to_string_lossy(),
        ],
    );
    assert_eq!(code, Some(0));
    let first = {
        let root = root.clone();
        std::thread::spawn(move || cli(&words(&["9001"]), &root, "the first tree's"))
    };
    let started = std::time::Instant::now();
    while !root.join("running").exists() {
        assert!(started.elapsed().as_secs() < 20, "quick never ran");
        std::thread::sleep(std::time::Duration::from_millis(5));
    }
    let second = cli(&words(&["9001"]), &other, "the second tree's");
    let first = first.join().unwrap();
    assert!(first.stdout.contains("T10 filed"), "{}", first.stdout);
    assert!(second.stdout.contains("T11 filed"), "{}", second.stdout);
    assert_eq!(own_lines(&root, "T10", "the first tree's"), (1, 1));
    assert_eq!(own_lines(&other, "T11", "the second tree's"), (1, 1));
    assert_eq!(own_lines(&root, "T11", "the second tree's"), (0, 0));
    assert_eq!(own_lines(&other, "T10", "the first tree's"), (0, 0));
}
