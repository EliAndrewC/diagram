//! `l7r-gate task-unstart` (451 T359): this tree's mark of a task removed and an `unstart` row logged, which every reader of the
//! start log takes with its start as no start; another tree's mark, no mark and a bundle's member refused.

use l7r_gate_core::ci::fixtures::put;
use l7r_shared::speckit::marks;

use super::cli;
use crate::task_start::cli_with as start;
use crate::tests::{env_of, repo, root_of};

fn words(a: &[&str]) -> Vec<String> {
    a.iter().map(|s| (*s).to_owned()).collect()
}

/// RED FIRST: a task started by mistake is unstarted - its mark gone, the log's pair read as no start, the task no longer the one
/// the tick's wording check or a landing beside it reads as started - and a bundle goes whole under its first task.
#[test]
fn a_start_is_undone_and_the_log_s_pair_reads_as_no_start() {
    let dir = repo("unstart");
    let root = root_of(&dir);
    let env = env_of(&[("L7R_GATE_TREE", &root.to_string_lossy())]);
    assert_eq!(
        cli(&words(&["9001"]), &root).stderr,
        "usage: make task-unstart F=<feature> T=<task>\n"
    );
    assert_eq!(
        cli(&words(&["99999", "T01"]), &root).stderr,
        "task-unstart: no single specs/99999* directory\n"
    );
    let none = cli(&words(&["9001", "T01"]), &root);
    assert_eq!((none.code, none.stderr.as_str()), (2, "task-unstart: refused - 9001-x T01 has no start mark in any tree: nothing to unstart (make speckit-todo lists what is started)\n"));
    assert_eq!(start(&words(&["9001", "T02"]), &root, &env).code, 0);
    assert_eq!(start(&words(&["9001", "T01"]), &root, &env).code, 0);
    let common = root.join(".git");
    assert_eq!(
        crate::wording::started(&root, "9001-x", "T01")
            .unwrap()
            .as_str()
            .map(str::len),
        Some(20)
    );
    // started a second time in this tree: one mark, two rows - and the open task holds this tree's landings
    assert_eq!(start(&words(&["9001", "T01"]), &root, &env).code, 0);
    let holds_it = || {
        let all = l7r_shared::speckit::holding(&root.join("specs/9001-x")).unwrap();
        all.iter().any(|h| h.starts_with("T01 "))
    };
    assert!(holds_it());
    let said = cli(&words(&["9001", "T01"]), &root);
    assert_eq!(said.code, 0, "{}", said.stderr);
    // unstarted once: it holds no landing, and both of its rows read as no start
    assert!(!holds_it());
    let tree = root.to_string_lossy();
    let want = format!("task-unstart: 9001-x T01 is no longer started in {tree} - its mark removed ({tree}/.git/task-marks/9001-x/T01.json), an unstart row in {tree}/.git/task-starts.jsonl\n");
    assert_eq!(said.stdout, want);
    assert!(!common.join("task-marks/9001-x/T01.json").exists());
    assert!(common.join("task-marks/9001-x/T02.json").exists());
    let log = std::fs::read_to_string(common.join(marks::STARTS)).unwrap();
    let last = log.lines().last().unwrap();
    let head = format!("{{\"unstart\": {{\"feature\": \"9001-x\", \"task\": \"T01\"}}, \"tree\": \"{tree}\", \"utc\": \"20");
    assert!(last.starts_with(&head), "{last}");
    // the readers: T02's start alone is left, and T01 has no start
    let live = marks::starts_text(&common);
    assert_eq!(
        (
            live.lines().count(),
            live.contains("\"T02\""),
            live.contains("T01")
        ),
        (1, true, false)
    );
    assert_eq!(crate::wording::started(&root, "9001-x", "T01").unwrap(), "");
    // a bundle: a member that is not its first task refused, its first task unstarting every member
    assert_eq!(start(&words(&["9001", "T01,T02"]), &root, &env).code, 0);
    let member = cli(&words(&["9001", "T02"]), &root);
    assert_eq!(member.code, 0, "{}", member.stderr);
    let inner = cli(&words(&["9001", "T02"]), &root);
    assert_eq!(inner.stderr, "task-unstart: refused - T02 is a member of the bundle started under T01, whose one mark is T01's (451 T141): make task-unstart F=9001 T=T01 unstarts the bundle\n");
    let whole = cli(&words(&["9001", "T01"]), &root);
    assert!(whole
        .stdout
        .starts_with("task-unstart: 9001-x T01, T02 is no longer started in "));
    assert_eq!(marks::starts_text(&common), "");
    assert!(marks::all(&common).is_empty());
}

/// RED FIRST: another tree's mark is that tree's to remove; the main worktree's one-mark file of before is unstarted as its own;
/// a phase task's hold goes with its start; a log that cannot be written raises.
#[test]
fn another_tree_s_mark_is_refused_and_a_phase_hold_is_lifted() {
    let dir = repo("unstart-other");
    let root = root_of(&dir);
    let env = env_of(&[("L7R_GATE_TREE", &root.to_string_lossy())]);
    let common = root.join(".git");
    put(&root, ".git/task-marks/9001-x/T02.json", "{\"feature\": \"9001-x\", \"task\": \"T02\", \"tree\": \"/another/tree\", \"utc\": \"2026-11-26T00:00:00Z\"}\n");
    let other = cli(&words(&["9001", "T02"]), &root);
    assert_eq!(other.code, 2);
    assert_eq!(other.stderr, format!("task-unstart: refused - 9001-x T02 was started in /another/tree, not in this tree ({}): its mark is that tree's to remove - make -C /another/tree task-unstart F=9001 T=T02\n", root.display()));
    assert!(common.join("task-marks/9001-x/T02.json").exists());
    // the legacy mark, the main worktree's
    put(
        &root,
        ".git/active-task",
        "{\"feature\": \"9001-x\", \"task\": \"T03\"}\n",
    );
    put(
        &root,
        ".git/task-starts.jsonl",
        "{\"feature\": \"9001-x\", \"task\": \"T03\", \"utc\": \"2026-10-01T00:00:00Z\"}\n",
    );
    let legacy = cli(&words(&["9001", "T03"]), &root);
    assert_eq!(legacy.code, 0, "{}", legacy.stderr);
    assert!(!common.join("active-task").exists());
    assert_eq!(marks::starts_text(&common), "");
    // a phase task: its hold lifted with its start
    put(
        &root,
        "l7r/diagram/frame.py",
        "def stage_water_frame(x):\n    return x\n",
    );
    put(&root, "specs/9001-x/tasks.md", "- [ ] T01 the frame\n      phase: water_frame\n      old-code: scripts/*.py\n- [ ] T02 other\n");
    assert_eq!(start(&words(&["9001", "T01"]), &root, &env).code, 0);
    assert!(common.join("phase-sources.json").exists());
    let phase = cli(&words(&["9001", "T01"]), &root);
    assert!(phase
        .stdout
        .ends_with("; its hold on its stage's old code is lifted\n"));
    assert!(!common.join("phase-sources.json").exists());
    // a mark whose file is not its task's own name, in a tree with no one-mark file: nothing to remove, a raise
    put(&root, ".git/task-marks/9001-x/odd.json", &format!("{{\"feature\": \"9001-x\", \"task\": \"T02\", \"tree\": \"{}\", \"utc\": \"2026-11-26T00:00:00Z\"}}\n", root.display()));
    std::fs::remove_file(common.join("task-marks/9001-x/T02.json")).unwrap();
    assert_eq!(cli(&words(&["9001", "T02"]), &root).code, 1);
    std::fs::remove_file(common.join("task-marks/9001-x/odd.json")).unwrap();
    // the log not writable: the mark removed, then the raise
    assert_eq!(start(&words(&["9001", "T01"]), &root, &env).code, 0);
    std::fs::remove_file(common.join("task-starts.jsonl")).unwrap();
    std::fs::create_dir_all(common.join("task-starts.jsonl")).unwrap();
    assert_eq!(cli(&words(&["9001", "T01"]), &root).code, 1);
}
