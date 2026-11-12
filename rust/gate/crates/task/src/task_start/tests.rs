//! `l7r-gate task-start` (feature 449 T131, from `task_start.py`): the mark, the feature named, the start logged, a held feature
//! refused, a phase task's old code held and any other task's hold cleared.

use l7r_gate_core::ci::fixtures::put;

use super::{cli, cli_with, task_block};
use crate::tests::{env_of, repo, root_of};

fn words(a: &[&str]) -> Vec<String> {
    a.iter().map(|s| (*s).to_owned()).collect()
}

#[test]
fn a_task_started_is_marked_named_and_logged() {
    let dir = repo("start");
    let root = root_of(&dir);
    let env = env_of(&[("L7R_GATE_TREE", &root.to_string_lossy())]);
    assert_eq!(
        cli(&words(&["9001"]), &root).stderr,
        "usage: task_start.py <feature> <task>\n"
    );
    assert_eq!(
        cli_with(&words(&["99999", "T01"]), &root, &env).stderr,
        "task-start: no single specs/99999* directory\n"
    );
    let said = cli_with(&words(&["9001", "T01"]), &root, &env);
    assert_eq!(said.code, 0, "{}", said.stderr);
    assert_eq!(said.stdout, "task-start: 9001-x T01 is the active task - its checks need its decisions ruled first (make decide)\n");
    assert_eq!(
        std::fs::read_to_string(root.join(".git/active-task")).unwrap(),
        "{\"feature\": \"9001-x\", \"task\": \"T01\"}\n"
    );
    assert_eq!(
        std::fs::read_to_string(root.join(".specify/feature.json")).unwrap(),
        "{\n  \"feature_directory\": \"specs/9001-x\"\n}\n"
    );
    let starts = std::fs::read_to_string(root.join(".git/task-starts.jsonl")).unwrap();
    assert!(starts.starts_with("{\"feature\": \"9001-x\", \"task\": \"T01\", \"utc\": \"20"));
    // by path, from below the root, the tree read where the wrapper did not say
    let by_path = format!("{}/", root.join("specs/9001-x").display());
    let again = cli(&words(&[&by_path, "T02"]), &root);
    assert_eq!(again.code, 0, "{}", again.stderr);
    assert_eq!(
        std::fs::read_to_string(root.join(".git/task-starts.jsonl"))
            .unwrap()
            .lines()
            .count(),
        2
    );
}

#[test]
fn a_held_feature_s_task_is_refused_and_a_raise_keeps_what_was_printed() {
    let dir = repo("start-held");
    let root = root_of(&dir);
    let env = env_of(&[("L7R_GATE_TREE", &root.to_string_lossy())]);
    put(
        &root,
        "specs/9001-x/spec.md",
        "**Status**: ON HOLD until feature 9003\n",
    );
    put(&root, "specs/9003-y/spec.md", "**Status**: In progress\n");
    put(&root, "specs/9003-y/tasks.md", "- [ ] T01 a\n");
    let held = cli_with(&words(&["9001", "T01"]), &root, &env);
    assert_eq!(held.code, 2);
    assert!(held.stderr.contains("is ON HOLD until 9003-y closes"));
    assert!(!root.join(".git/active-task").exists());
    // an unreadable plan raises before anything is written
    std::fs::write(root.join("specs/9001-x/plan.md"), [0xff]).unwrap();
    assert_eq!(cli_with(&words(&["9001", "T01"]), &root, &env).code, 1);
    // `.specify` a file: the mark written, then the raise
    std::fs::remove_file(root.join("specs/9001-x/plan.md")).unwrap();
    put(&root, "specs/9001-x/spec.md", "**Status**: In progress\n");
    std::fs::remove_dir_all(root.join(".specify")).ok();
    put(&root, ".specify", "x");
    let raised = cli_with(&words(&["9001", "T01"]), &root, &env);
    assert_eq!(raised.code, 1);
    assert!(root.join(".git/active-task").exists());
    // the start log not writable: the mark and the name written, then the raise
    std::fs::remove_file(root.join(".specify")).unwrap();
    std::fs::rename(root.join(".git/task-starts.jsonl"), root.join(".git/kept")).ok();
    std::fs::create_dir_all(root.join(".git/task-starts.jsonl")).unwrap();
    assert_eq!(cli_with(&words(&["9001", "T01"]), &root, &env).code, 1);
    std::fs::remove_dir(root.join(".git/task-starts.jsonl")).unwrap();
    // the hold's own raise
    put(
        &root,
        "specs/9001-x/spec.md",
        "**Status**: ON HOLD until feature 9003\n",
    );
    put(&root, ".specify/affects.json", "[");
    assert_eq!(cli_with(&words(&["9001", "T01"]), &root, &env).code, 1);
}

#[test]
fn a_phase_task_holds_its_old_code_and_another_task_clears_it() {
    let dir = repo("start-phase");
    let root = root_of(&dir);
    let env = env_of(&[("L7R_GATE_TREE", &root.to_string_lossy())]);
    put(
        &root,
        "l7r/diagram/frame.py",
        "def stage_water_frame(x):\n    return x\n",
    );
    put(
        &root,
        "specs/9001-x/tasks.md",
        "- [ ] T01 the frame\n      phase: water_frame\n      old-code: scripts/*.py\n- [ ] T02 other\n",
    );
    let said = cli_with(&words(&["9001", "T01"]), &root, &env);
    assert_eq!(said.code, 0, "{}", said.stderr);
    assert!(
        said.stdout
            .contains("phase-sources: T01 rebuilds `water_frame` from its derivation - "),
        "{}",
        said.stdout
    );
    let state = std::fs::read_to_string(root.join(".git/phase-sources.json")).unwrap();
    assert!(state.contains("\"scripts/a.py\""), "{state}");
    let other = cli_with(&words(&["9001", "T02"]), &root, &env);
    assert_eq!(other.code, 0);
    assert!(!root.join(".git/phase-sources.json").exists());
    // the sources' raise after the mark: what was printed is kept
    put(
        &root,
        "specs/9001-x/tasks.md",
        "- [ ] T01 x\n      phase: water_frame\n      old-code: /abs\n",
    );
    let raised = cli_with(&words(&["9001", "T01"]), &root, &env);
    assert_eq!(raised.code, 1);
    assert!(raised.stdout.contains("is the active task"));
    // no tasks.md: no block, no hold
    std::fs::remove_file(root.join("specs/9001-x/tasks.md")).unwrap();
    assert_eq!(cli_with(&words(&["9001", "T01"]), &root, &env).code, 0);
    std::fs::write(root.join("specs/9001-x/tasks.md"), [0xff]).unwrap();
    assert_eq!(cli_with(&words(&["9001", "T01"]), &root, &env).code, 1);
}

#[test]
fn a_task_s_block_runs_to_the_next_box() {
    let tasks = "- [ ] T01 a\n  phase: x\n- [x] T02 b\n  more\n";
    assert_eq!(task_block(tasks, "T01"), "- [ ] T01 a\n  phase: x\n");
    assert_eq!(task_block(tasks, "T02"), "- [x] T02 b\n  more\n");
    assert_eq!(task_block(tasks, "T03"), "");
}
