//! The started-task marks (feature 451 T254): one a task, a tree's own newest, the legacy mark as the main worktree's oldest, the
//! set-down's clear of one tree's and the landing's removal.

use std::path::Path;

use serde_json::json;

use super::{all, clear, of_tree, remove, tasks_of, write, LEGACY};
use crate::tempdir::TempDir;
use crate::tool::ask;

fn git(at: &Path, args: &[&str]) {
    let said = ask(at, "git", args, "");
    assert!(said.ok(), "git {args:?}: {}", said.err);
}

/// RED FIRST: two worktrees each start a task; each tree reads its own, neither start moves the other's, and the main worktree's
/// one-mark file of before is read until its next start replaces it.
#[test]
fn each_tree_keeps_its_own_mark() {
    let d = TempDir::new("guard-marks");
    let at = d.canonicalize().unwrap();
    git(&at, &["init", "-q"]);
    let id = ["-c", "user.email=t@t", "-c", "user.name=t"];
    git(
        &at,
        &[&id[..], &["commit", "-q", "--allow-empty", "-m", "base"]].concat(),
    );
    let other = at.join("other");
    git(
        &at,
        &["worktree", "add", "-q", "--detach", &other.to_string_lossy()],
    );
    let common = at.join(".git");
    assert!(of_tree(&at).unwrap().is_null());
    assert!(of_tree(Path::new("/no/such/dir")).unwrap().is_null());
    std::fs::write(common.join(LEGACY), r#"{"feature": "9-x", "task": "T01"}"#).unwrap();
    assert_eq!(of_tree(&at).unwrap()["task"], "T01");
    assert!(
        of_tree(&other).unwrap().is_null(),
        "the legacy mark is the main worktree's"
    );
    let theirs = json!({"feature": "9-x", "task": "T02"});
    write(&common, &other, theirs, "2026-11-25T10:00:00Z").unwrap();
    assert_eq!(of_tree(&at).unwrap()["task"], "T01");
    assert_eq!(of_tree(&other).unwrap()["task"], "T02");
    let bundle = json!({"feature": "9-x", "task": "T03", "tasks": ["T03", "T04"]});
    write(&common, &at, bundle, "2026-11-25T10:00:01Z").unwrap();
    assert!(
        !common.join(LEGACY).exists(),
        "the main worktree's start replaces the legacy mark"
    );
    assert_eq!(of_tree(&at).unwrap()["task"], "T03");
    assert_eq!(of_tree(&other).unwrap()["task"], "T02");
    let tasks: Vec<Vec<String>> = all(&common).iter().map(tasks_of).collect();
    assert_eq!(
        tasks,
        [vec!["T02".to_owned()], vec!["T03".to_owned(), "T04".to_owned()]]
    );
    // a set-down clears its own tree's marks of the feature, not another worktree's
    assert_eq!(clear(&common, &at, "8-y"), None);
    assert_eq!(clear(&common, &at, "9-x").as_deref(), Some("T03"));
    assert_eq!(of_tree(&other).unwrap()["task"], "T02");
    std::fs::write(common.join(LEGACY), r#"{"feature": "9-x"}"#).unwrap();
    assert_eq!(clear(&common, &at, "9-x").as_deref(), Some("None"));
    // a landing removes its tasks' marks, its feature named by number
    remove(&common, "8", &["T02".to_owned()]);
    assert_eq!(all(&common).len(), 1);
    remove(&common, "9", &["T02".to_owned()]);
    assert!(all(&common).is_empty());
    // a legacy mark that is not JSON, or not an object, is none in the list, and read as written for its readers
    std::fs::write(common.join(LEGACY), "[1]").unwrap();
    assert!(all(&common).is_empty());
    assert!(of_tree(&at).unwrap().is_array());
    std::fs::write(common.join(LEGACY), "not json").unwrap();
    assert!(of_tree(&at).unwrap().is_null());
    std::fs::remove_file(common.join(LEGACY)).unwrap();
    std::os::unix::fs::symlink("/proc/self/mem", common.join(LEGACY)).unwrap();
    assert!(of_tree(&at).is_err());
    std::fs::remove_file(common.join(LEGACY)).unwrap();
    // a mark that cannot be written is the start's error
    std::fs::write(common.join(super::DIR).join("7-z"), "").unwrap();
    let blocked = json!({"feature": "7-z", "task": "T1"});
    assert!(write(&common, &at, blocked, "x").is_err());
    std::fs::create_dir_all(common.join(super::DIR).join("6-w/T1.json")).unwrap();
    let blocked = json!({"feature": "6-w", "task": "T1"});
    assert!(write(&common, &at, blocked, "x").is_err());
}
