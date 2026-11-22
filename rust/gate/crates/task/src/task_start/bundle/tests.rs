//! `make task-start T=a,b,c` (451 T141): the bundle marked under its first task with every member listed, each start logged with the
//! first task's last, every member's refusal asked before anything is written.

use l7r_gate_core::ci::fixtures::put;

use super::super::cli_with;
use super::members;
use crate::tests::{env_of, repo, root_of};

fn words(a: &[&str]) -> Vec<String> {
    a.iter().map(|s| (*s).to_owned()).collect()
}

#[test]
fn a_bundle_is_marked_under_its_first_task_with_every_member_logged() {
    let dir = repo("start-bundle");
    let root = root_of(&dir);
    let env = env_of(&[("L7R_GATE_TREE", &root.to_string_lossy())]);
    let split = members("T03, T01 T03,T02");
    assert_eq!(split, ["T03", "T01", "T02"]);
    let said = cli_with(&words(&["9001", "T01,T02,T03"]), &root, &env);
    assert_eq!(said.code, 0, "{}", said.stderr);
    let first = said.stdout.lines().next().unwrap_or_default().to_owned();
    let opens =
        first.starts_with("task-start: 9001-x T01, T02, T03 is the active bundle (451 T141)");
    let names = first.contains("`### T01, T02, T03 (bundle)`")
        && first.contains("make decide F=9001 T=T01,T02,T03");
    let lands = first.contains("make land F=9001 T=T01,T02,T03");
    assert!(opens && names && lands, "{first}");
    let mark = std::fs::read_to_string(root.join(".git/active-task")).unwrap();
    assert_eq!(
        mark,
        "{\"feature\": \"9001-x\", \"task\": \"T01\", \"tasks\": [\"T01\", \"T02\", \"T03\"]}\n"
    );
    let starts = std::fs::read_to_string(root.join(".git/task-starts.jsonl")).unwrap();
    let order: Vec<String> = starts
        .lines()
        .map(|l| l.split("\"task\": \"").nth(1).unwrap_or_default()[..3].to_owned())
        .collect();
    assert_eq!(order, ["T02", "T03", "T01"]);
    // the space form, as `make land` takes it
    let spaced = cli_with(&words(&["9001", "T02 T01"]), &root, &env);
    assert_eq!(spaced.code, 0, "{}", spaced.stderr);
    let again = std::fs::read_to_string(root.join(".git/active-task")).unwrap();
    let listed = again.contains("\"task\": \"T02\", \"tasks\": [\"T02\", \"T01\"]");
    assert!(listed, "{again}");
}

#[test]
fn every_member_s_refusal_is_named_and_nothing_written() {
    let dir = repo("start-bundle-refused");
    let root = root_of(&dir);
    let env = env_of(&[("L7R_GATE_TREE", &root.to_string_lossy())]);
    let refused = cli_with(&words(&["9001", "T01,T09,T77"]), &root, &env);
    assert_eq!(refused.code, 2);
    assert!(
        refused
            .stderr
            .contains("the bundle T=T01,T09,T77 was not started, nothing written"),
        "{}",
        refused.stderr
    );
    assert!(
        refused
            .stderr
            .contains("T09 is not an open task of 9001-x/tasks.md"),
        "{}",
        refused.stderr
    );
    assert!(
        refused.stderr.contains("T77 is not an open task"),
        "{}",
        refused.stderr
    );
    assert!(!root.join(".git/active-task").exists());
    assert!(!root.join(".git/task-starts.jsonl").exists());
    put(
        &root,
        "specs/9001-x/tasks.md",
        "- [ ] T01 the frame\n      phase: water_frame\n- [ ] T02 other\n",
    );
    let phase = cli_with(&words(&["9001", "T02,T01"]), &root, &env);
    assert_eq!(phase.code, 2);
    assert!(phase.stderr.contains("T01 is a phase task (phase: water_frame): its stage's old code is held for it alone - start it by itself, make task-start F=9001 T=T01"), "{}", phase.stderr);
    assert!(!root.join(".git/active-task").exists());
    assert_eq!(
        cli_with(&words(&["99999", "T01,T02"]), &root, &env).stderr,
        "task-start: no single specs/99999* directory\n"
    );
}

#[test]
fn a_held_feature_refuses_its_bundle_once() {
    let dir = repo("start-bundle-held");
    let root = root_of(&dir);
    let env = env_of(&[("L7R_GATE_TREE", &root.to_string_lossy())]);
    put(
        &root,
        "specs/9001-x/spec.md",
        "**Status**: ON HOLD until feature 9003\n",
    );
    put(&root, "specs/9003-y/spec.md", "**Status**: In progress\n");
    put(&root, "specs/9003-y/tasks.md", "- [ ] T01 a\n");
    let held = cli_with(&words(&["9001", "T01,T02"]), &root, &env);
    assert_eq!(held.code, 2);
    let named = held
        .stderr
        .matches("is ON HOLD until 9003-y closes")
        .count();
    assert!(named >= 1, "{}", held.stderr);
    assert!(!root.join(".git/active-task").exists());
}

#[test]
fn a_bundle_with_no_plan_starts_and_one_with_no_performance_work_waits_for_it() {
    let dir = repo("start-bundle-perf");
    let root = root_of(&dir);
    let env = env_of(&[("L7R_GATE_TREE", &root.to_string_lossy())]);
    std::fs::remove_file(root.join("specs/9001-x/plan.md")).unwrap();
    let bare = cli_with(&words(&["9001", "T01,T02"]), &root, &env);
    assert_eq!(bare.code, 0, "{}", bare.stderr);
    put(
        &root,
        "specs/9001-x/tasks.md",
        "- [ ] T01 a\n- [ ] T02 b\n- [ ] T03 [perf] the faster gate\n",
    );
    let waits = cli_with(&words(&["9001", "T01,T02"]), &root, &env);
    let named = waits
        .stderr
        .contains("9001-x T01 is not performance work, and 9001-x T03 is");
    assert!(waits.code == 2 && named, "{}", waits.stderr);
    let with_it = cli_with(&words(&["9001", "T01,T03"]), &root, &env);
    assert_eq!(with_it.code, 0, "{}", with_it.stderr);
}

#[test]
fn performance_first_is_asked_of_each_member_the_waiting_task_counted_started_when_it_is_one() {
    let dir = repo("start-bundle-perf-each");
    let root = root_of(&dir);
    let env = env_of(&[("L7R_GATE_TREE", &root.to_string_lossy())]);
    put(
        &root,
        "specs/9001-x/tasks.md",
        "- [ ] T01 a\n- [ ] T02 [perf] the fast gate\n- [ ] T03 [perf] the faster gate\n",
    );
    // T01 waits on T02, which waits outside the bundle: T03's being performance work does not start T01
    let outside = cli_with(&words(&["9001", "T01,T03"]), &root, &env);
    let named = outside
        .stderr
        .contains("9001-x T01 is not performance work, and 9001-x T02 is");
    assert!(outside.code == 2 && named, "{}", outside.stderr);
    assert!(!root.join(".git/active-task").exists());
    // the waiting task in the bundle counts as started
    let inside = cli_with(&words(&["9001", "T01,T02"]), &root, &env);
    assert_eq!(inside.code, 0, "{}", inside.stderr);
    let all_perf = cli_with(&words(&["9001", "T03,T02"]), &root, &env);
    assert_eq!(all_perf.code, 0, "{}", all_perf.stderr);
}
