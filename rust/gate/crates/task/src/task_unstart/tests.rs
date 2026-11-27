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
    // the landing's ticks handed in as none: `holding` reads a `make land`'s `L7R_LAND_TICKS` from the process (451 T143: these two
    // tests red with `L7R_LAND_TICKS=T01` exported, measured 2026-11-27)
    let holds_it = || {
        let all = l7r_shared::speckit::holding_with(&root.join("specs/9001-x"), "").unwrap();
        all.iter().any(|h| h.starts_with("T01 "))
    };
    assert!(holds_it());
    let file = marks::own_file(&common, "9001-x", "T01", &root).unwrap();
    let said = cli(&words(&["9001", "T01"]), &root);
    assert_eq!(said.code, 0, "{}", said.stderr);
    // unstarted once: it holds no landing, and both of its rows read as no start
    assert!(!holds_it());
    let tree = root.to_string_lossy();
    let want = format!("task-unstart: 9001-x T01 is no longer started in {tree} - its mark removed ({}), an unstart row in {tree}/.git/task-starts.jsonl\n", file.display());
    assert_eq!(said.stdout, want);
    assert!(!file.exists());
    assert!(marks::own_file(&common, "9001-x", "T02", &root).is_some());
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
            live.contains("\"T01\"")
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
    // a tree that still stands (451 T437: a mark of a tree gone is any tree's to remove)
    let (other_top, _) = other_tree(&dir, &root);
    assert_eq!(start(&words(&["9001", "T02"]), &other_top, &env).code, 0);
    let theirs = marks::all(&common)[0]["tree"].as_str().unwrap().to_owned();
    let other = cli(&words(&["9001", "T02"]), &root);
    assert_eq!(other.code, 2);
    assert_eq!(other.stderr, format!("task-unstart: refused - 9001-x T02 was started in {theirs}, not in this tree ({}): its mark is that tree's to remove - make -C {theirs} task-unstart F=9001 T=T02\n", root.display()));
    assert_eq!(marks::all(&common).len(), 1);
    assert_eq!(cli(&words(&["9001", "T02"]), &other_top).code, 0);
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
    assert_eq!(cli(&words(&["9001", "T02"]), &root).code, 1);
    std::fs::remove_file(common.join("task-marks/9001-x/odd.json")).unwrap();
    // the log not writable: the mark removed, then the raise
    assert_eq!(start(&words(&["9001", "T01"]), &root, &env).code, 0);
    std::fs::remove_file(common.join("task-starts.jsonl")).unwrap();
    std::fs::create_dir_all(common.join("task-starts.jsonl")).unwrap();
    assert_eq!(cli(&words(&["9001", "T01"]), &root).code, 1);
}

/// The trees that hold `task` of 9001-x, each reader asked: its marks' trees, and its live start rows' trees - each resolved, sorted
/// and once.
fn holders(common: &std::path::Path, task: &str) -> (Vec<String>, Vec<String>) {
    let resolved = |t: &str| {
        std::fs::canonicalize(t).map_or(t.to_owned(), |p| p.to_string_lossy().into_owned())
    };
    let mut marked: Vec<String> = marks::all(common)
        .iter()
        .filter(|m| m["feature"] == "9001-x" && m["task"] == task)
        .map(|m| resolved(m["tree"].as_str().unwrap_or_default()))
        .collect();
    let mut logged: Vec<String> = marks::starts_text(common)
        .lines()
        .filter_map(|l| serde_json::from_str::<serde_json::Value>(l).ok())
        .filter(|r| r["feature"] == "9001-x" && r["task"] == task)
        .map(|r| resolved(r["tree"].as_str().unwrap_or_default()))
        .collect();
    for list in [&mut marked, &mut logged] {
        list.sort();
        list.dedup();
    }
    (marked, logged)
}

/// A worktree of the fixture's repository beside it, `<dir>/other`, and its resolved path.
fn other_tree(dir: &std::path::Path, root: &std::path::Path) -> (std::path::PathBuf, String) {
    let other = dir.join("other");
    let (code, _) = crate::git(
        root,
        &[
            "worktree",
            "add",
            "-q",
            "--detach",
            &other.to_string_lossy(),
        ],
    );
    assert_eq!(code, Some(0));
    let shown = std::fs::canonicalize(&other).unwrap();
    (other, shown.to_string_lossy().into_owned())
}

/// RED FIRST (451 T369): a task started in two trees keeps each tree's mark, so the second tree's unstart leaves the first tree's start
/// true in every reader - its mark, its row of the log and the hold on its own landings - and the first tree unstarts it there.
#[test]
fn a_task_started_in_two_trees_keeps_each_tree_s_mark() {
    let dir = repo("unstart-two-trees");
    let root = root_of(&dir);
    let env = env_of(&[("L7R_GATE_TREE", &root.to_string_lossy())]);
    let common = root.join(".git");
    let (other, theirs) = other_tree(&dir, &root);
    let ours = std::fs::canonicalize(&root)
        .unwrap()
        .to_string_lossy()
        .into_owned();
    assert_eq!(start(&words(&["9001", "T01"]), &other, &env).code, 0);
    assert_eq!(start(&words(&["9001", "T01"]), &root, &env).code, 0);
    let both = vec![ours.clone(), theirs.clone()];
    let mut both = both;
    both.sort();
    assert_eq!(holders(&common, "T01"), (both.clone(), both));
    let said = cli(&words(&["9001", "T01"]), &root);
    assert_eq!(said.code, 0, "{}", said.stderr);
    let first = vec![theirs.clone()];
    assert_eq!(holders(&common, "T01"), (first.clone(), first));
    let holds = |tree: &std::path::Path| {
        let all = l7r_shared::speckit::holding_with(&tree.join("specs/9001-x"), "").unwrap();
        all.iter()
            .any(|h| h.starts_with("T01 ") && h.contains("<- the active task"))
    };
    assert_eq!((holds(&other), holds(&root)), (true, false));
    let undone = cli(&words(&["9001", "T01"]), &other);
    assert_eq!(undone.code, 0, "{}", undone.stderr);
    assert_eq!(holders(&common, "T01"), (vec![], vec![]));
}

/// RED FIRST (451 T369): the landing's way - a builder's pool tree started the task and was released, and the clone starts the
/// carried task: an unstart in the clone leaves the builder's start, mark and row alike, and the landing's sweep removes every tree's.
#[test]
fn a_released_pool_tree_s_start_outlives_the_clone_s_undo_until_the_landing() {
    let dir = repo("unstart-pool");
    let root = root_of(&dir);
    let env = env_of(&[("L7R_GATE_TREE", &root.to_string_lossy())]);
    let common = root.join(".git");
    let (other, theirs) = other_tree(&dir, &root);
    let pool = |tasks: &[&str]| {
        let tree = l7r_shared::builder_pool::Tree {
            tree: other.clone(),
            feature: "9001".to_owned(),
            tasks: tasks.iter().map(|t| (*t).to_owned()).collect(),
            since: "2026-11-26T00:00:00Z".to_owned(),
        };
        l7r_shared::builder_pool::write(&common, &[tree]).unwrap();
    };
    pool(&["T01"]);
    assert_eq!(start(&words(&["9001", "T01"]), &other, &env).code, 0);
    pool(&[]);
    assert_eq!(start(&words(&["9001", "T01"]), &root, &env).code, 0);
    assert_eq!(cli(&words(&["9001", "T01"]), &root).code, 0);
    let first = vec![theirs];
    assert_eq!(holders(&common, "T01"), (first.clone(), first));
    assert_eq!(start(&words(&["9001", "T01"]), &root, &env).code, 0);
    assert_eq!(marks::all(&common).len(), 2);
    marks::remove(&common, "9001", &["T01".to_owned()]);
    assert!(marks::all(&common).is_empty());
}

/// RED FIRST (451 T437): a mark of a tree that no longer exists - a worktree removed, or a path never made, in the layout of before
/// T369 - is any tree's to remove: unstarted from this tree, its unstart row naming the tree the mark named, so its start rows go too.
#[test]
fn a_mark_of_a_tree_gone_is_unstarted_from_any_tree() {
    let dir = repo("unstart-gone");
    let root = root_of(&dir);
    let env = env_of(&[("L7R_GATE_TREE", &root.to_string_lossy())]);
    let common = root.join(".git");
    let (other, _) = other_tree(&dir, &root);
    assert_eq!(start(&words(&["9001", "T01"]), &other, &env).code, 0);
    let theirs = marks::all(&common)[0]["tree"].as_str().unwrap().to_owned();
    let (code, _) = crate::git(
        &root,
        &["worktree", "remove", "--force", &other.to_string_lossy()],
    );
    assert_eq!(code, Some(0));
    let said = cli(&words(&["9001", "T01"]), &root);
    assert_eq!(said.code, 0, "{}", said.stderr);
    assert!(said.stdout.starts_with(&format!(
        "task-unstart: 9001-x T01 is no longer started in {theirs} - its mark removed ("
    )));
    assert_eq!(holders(&common, "T01"), (vec![], vec![]));
    let never = dir.join("never-made").to_string_lossy().into_owned();
    put(&root, ".git/task-marks/9001-x/T02.json", &format!("{{\"feature\": \"9001-x\", \"task\": \"T02\", \"tree\": \"{never}\", \"utc\": \"2026-11-26T00:00:00Z\"}}\n"));
    assert_eq!(cli(&words(&["9001", "T02"]), &root).code, 0);
    assert!(marks::all(&common).is_empty());
}
