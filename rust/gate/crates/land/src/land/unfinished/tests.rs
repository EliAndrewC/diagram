//! An unfinished carry-over lands nothing (451 T292): T270's state, built by a real `git cherry-pick`, is refused before the landing is
//! sent to land alone; each state's printed command, run, finishes it; a linked worktree's own git directory is the one read.

use std::path::{Path, PathBuf};

use l7r_gate_core::ci::fixtures::{git, put, scratch};
use l7r_shared::tempdir::TempDir;

use super::super::alone::SCRIPT;
use super::super::tests::{fx, has, NOTE};
use super::{cli, refusals};

/// The Occasions block both sides add a line to.
pub(in super::super) const TASKS: &str =
    "# Tasks\n\n## Occasions\n\n- none: T1 - tooling only\n\n## Dependencies\n\n- [ ] T9 nine\n";

fn with_line(line: &str) -> String {
    TASKS.replace(
        "tooling only\n",
        &format!("tooling only\n- none: {line} - tooling only\n"),
    )
}

/// A repository whose `main` holds a feature's tasks.md and a code file.
pub(in super::super) fn repo(tag: &str) -> (TempDir, PathBuf) {
    let dir = scratch(tag);
    let root = dir.join("repo");
    std::fs::create_dir_all(&root).unwrap();
    git(&root, &["init", "-q", "-b", "main"]);
    git(&root, &["config", "user.email", "t@t"]);
    git(&root, &["config", "user.name", "t"]);
    put(&root, "specs/451-x/tasks.md", TASKS);
    put(&root, "rust/lib.rs", "fn a() {}\n");
    git(&root, &["add", "-A"]);
    git(&root, &["commit", "-qm", "base"]);
    (dir, root)
}

/// T270's carry-over (2026-11-26): a builder's commit - its Occasions line and its code - on a branch, the tree's own Occasions line
/// committed after the same line, and the cherry-pick of the one onto the other, stopped: tasks.md unmerged, the code staged.
pub(in super::super) fn t270_state(root: &Path) {
    git(root, &["checkout", "-q", "-b", "builder"]);
    put(root, "specs/451-x/tasks.md", &with_line("T270"));
    put(root, "rust/held.rs", "fn held() {}\n");
    git(root, &["add", "-A"]);
    git(root, &["commit", "-qm", "451 T270: the builder's commit"]);
    git(root, &["checkout", "-q", "-"]);
    put(root, "specs/451-x/tasks.md", &with_line("T271"));
    git(root, &["add", "-A"]);
    git(root, &["commit", "-qm", "T271's line"]);
    let (rc, _) = super::git(root, &["cherry-pick", "builder"]).unwrap();
    assert_ne!(rc, 0);
}

/// The command a refusal prints after `after`, between its backquotes, run by the shell.
fn run_printed(line: &str, after: &str) {
    let rest = &line[line.find(after).unwrap() + after.len()..];
    let cmd = rest.split('`').nth(1).unwrap();
    let done = std::process::Command::new("sh")
        .args(["-c", cmd])
        .output()
        .unwrap();
    assert!(done.status.success(), "{cmd}: {done:?}");
}

#[test]
fn t270s_unfinished_cherry_pick_is_refused_before_the_landing_runs_alone() {
    // RED FIRST (2026-11-26): without the check in `Land::land` the landing answers Ok(0) here, `land-alone.sh 449-x T1` in its log
    let fx = fx("unfinished-t270");
    std::fs::hard_link(
        fx.dir.join("tree/scripts/gates/l7r-gate.sh"),
        fx.dir.join("tree/scripts").join(SCRIPT),
    )
    .unwrap();
    put(&fx.root, "specs/451-x/tasks.md", TASKS);
    git(&fx.root, &["add", "-A"]);
    git(&fx.root, &["commit", "-qm", "the feature"]);
    t270_state(&fx.root);
    assert!(fx.root.join(".git/CHERRY_PICK_HEAD").exists());
    assert_eq!(
        git(&fx.root, &["status", "--porcelain"]),
        "A  rust/held.rs\nUU specs/451-x/tasks.md"
    );
    let landed = fx
        .land
        .land(&fx.root.join("specs/449-x"), &["T1".to_owned()], NOTE);
    assert_eq!(landed, Ok(2));
    let err = fx.said().1;
    has(&err, "land: refused before anything ran - nothing landed, nothing ticked. Every refusal:\n  a cherry-pick is in progress in ");
    has(&err, "(CHERRY_PICK_HEAD, 1 staged path(s) uncommitted) - finish it: resolve 1 unmerged path(s) (specs/451-x/tasks.md), `git -C ");
    has(
        &err,
        "-c core.editor=true cherry-pick --continue` (or take it back: `git -C ",
    );
    // nothing ran: no landing alone, no first pass, no commit of the landing's
    assert_eq!(fx.log(), "");
    assert!(fx.root.join(".git/CHERRY_PICK_HEAD").exists());
    assert!(!fx.subjects().contains("make land"));
}

#[test]
fn the_printed_commands_finish_a_stopped_cherry_pick() {
    let (_dir, root) = repo("unfinished-finish");
    t270_state(&root);
    let stops = refusals(&root).unwrap();
    assert_eq!(stops.len(), 1, "{stops:?}");
    // resolved by hand, then the two commands as printed
    put(&root, "specs/451-x/tasks.md", &with_line("T271"));
    run_printed(&stops[0], "unmerged path(s)");
    run_printed(&stops[0], "then ");
    assert_eq!(refusals(&root).unwrap(), Vec::<String>::new());
    assert_eq!(
        git(&root, &["log", "-1", "--format=%s"]),
        "451 T270: the builder's commit"
    );
    assert!(root.join("rust/held.rs").exists());
    assert_eq!(cli(&root).code, 0);
    // the gate's two forms: `land --unfinished [<tree>]`, the tree its working directory's where none is named, and `land --carry`
    let form = |args: &[&str], cwd: &Path| {
        let args: Vec<String> = args.iter().map(|a| (*a).to_owned()).collect();
        super::super::cli(&args, cwd)
    };
    assert_eq!(form(&["--unfinished"], &root.join("rust")).code, 0);
    assert_eq!(
        form(&["--unfinished", &root.to_string_lossy()], Path::new("/")).code,
        0
    );
    let said = form(&["--carry"], &root);
    assert_eq!(said.code, 2);
    assert!(said.stderr.starts_with("usage: l7r-gate land --carry"));
}

#[test]
fn a_linked_worktrees_own_git_directory_is_read() {
    // its `.git` is a file (451 T267): the pick's marker stands in <common>/worktrees/<name>, never in <tree>/.git/
    let (dir, root) = repo("unfinished-worktree");
    let tree = dir.join("linked");
    git(
        &root,
        &[
            "worktree",
            "add",
            "-q",
            "-b",
            "side",
            &tree.to_string_lossy(),
        ],
    );
    assert!(tree.join(".git").is_file());
    t270_state(&tree);
    let stops = refusals(&tree).unwrap();
    has(&stops[0], "a cherry-pick is in progress in ");
    has(
        &stops[0],
        &format!("`git -C {} add -- specs/451-x/tasks.md`", tree.display()),
    );
    // the clone the worktree hangs off holds none of it
    assert_eq!(refusals(&root).unwrap(), Vec::<String>::new());
    let said = cli(&tree);
    assert_eq!(said.code, 2);
    assert!(said
        .stderr
        .starts_with("unfinished: a cherry-pick is in progress in "));
}

#[test]
fn a_merge_a_revert_and_a_rebase_are_each_named_with_their_command() {
    // a merge that stands with nothing unmerged, its tree clean but for what it staged
    let (_dir, root) = repo("unfinished-merge");
    git(&root, &["checkout", "-q", "-b", "side"]);
    put(&root, "rust/side.rs", "fn side() {}\n");
    git(&root, &["add", "-A"]);
    git(&root, &["commit", "-qm", "side"]);
    git(&root, &["checkout", "-q", "main"]);
    git(&root, &["merge", "-q", "--no-ff", "--no-commit", "side"]);
    let stops = refusals(&root).unwrap();
    assert_eq!(stops.len(), 1, "{stops:?}");
    has(&stops[0], "a merge is in progress in ");
    has(
        &stops[0],
        "(MERGE_HEAD, 1 staged path(s) uncommitted) - finish it: `git -C ",
    );
    run_printed(&stops[0], "finish it: ");
    assert_eq!(refusals(&root).unwrap(), Vec::<String>::new());
    // a revert left uncommitted
    git(&root, &["revert", "--no-commit", "side"]);
    let stops = refusals(&root).unwrap();
    has(&stops[0], "a revert is in progress in ");
    has(&stops[0], "-c core.editor=true revert --continue`");
    run_printed(&stops[0], "finish it: ");
    assert_eq!(refusals(&root).unwrap(), Vec::<String>::new());
    // a rebase, either of its directories, is named once and taken back, never continued
    git(&root, &["checkout", "-q", "side"]);
    put(&root, "rust/lib.rs", "fn side_edit() {}\n");
    git(&root, &["commit", "-qam", "side edits lib"]);
    git(&root, &["checkout", "-q", "main"]);
    put(&root, "rust/lib.rs", "fn main_edit() {}\n");
    git(&root, &["commit", "-qam", "main edits lib"]);
    let (rc, _) = super::git(&root, &["rebase", "side"]).unwrap();
    assert_ne!(rc, 0);
    std::fs::create_dir_all(root.join(".git/rebase-apply")).unwrap();
    let stops = refusals(&root).unwrap();
    assert_eq!(stops.len(), 1, "{stops:?}");
    has(&stops[0], "a rebase is in progress in ");
    has(
        &stops[0],
        "this project rewrites no history, take it back: `git -C ",
    );
    std::fs::remove_dir_all(root.join(".git/rebase-apply")).unwrap();
    // the printed command is the one form of `git rebase` the history guard lets through (its own test holds each printed form)
    let rest = &stops[0][stops[0].find("take it back: ").unwrap()..];
    assert!(rest.split('`').nth(1).unwrap().ends_with(" rebase --abort"));
    run_printed(&stops[0], "take it back: ");
    assert_eq!(refusals(&root).unwrap(), Vec::<String>::new());
    // a mailbox apply (git am) stopped on a patch that does not apply: named as itself, taken back by its own abort
    let patch = root.join("../p.patch");
    std::fs::write(&patch, "From 0000000000000000000000000000000000000000 Mon Sep 17 00:00:00 2001\nFrom: t <t@t>\nDate: Thu, 26 Nov 2026 00:00:00 +0000\nSubject: [PATCH] p\n\n---\n rust/gone.rs | 2 +-\n\ndiff --git a/rust/gone.rs b/rust/gone.rs\n--- a/rust/gone.rs\n+++ b/rust/gone.rs\n@@ -1 +1 @@\n-old\n+new\n-- \n2.0\n").unwrap();
    let (rc, _) = super::git(&root, &["am", &patch.to_string_lossy()]).unwrap();
    assert_ne!(rc, 0);
    let stops = refusals(&root).unwrap();
    assert_eq!(stops.len(), 1, "{stops:?}");
    has(&stops[0], "a mailbox apply (git am) is in progress in ");
    has(
        &stops[0],
        "(rebase-apply) - this project rewrites no history, take it back: `git -C ",
    );
    run_printed(&stops[0], "take it back: ");
    assert_eq!(refusals(&root).unwrap(), Vec::<String>::new());
}

#[test]
fn a_pick_of_several_commits_paused_between_two_is_refused() {
    // RED FIRST (2026-11-26, the plan review's state): the first commit's conflict resolved and committed by a plain `git commit` -
    // no CHERRY_PICK_HEAD, a clean status, the second commit's file not in the tree - read as nothing unfinished before `sequencer/todo`
    let (_dir, root) = repo("unfinished-sequencer");
    git(&root, &["checkout", "-q", "-b", "builder"]);
    put(&root, "rust/lib.rs", "fn builder() {}\n");
    git(&root, &["commit", "-qam", "A"]);
    put(&root, "rust/second.rs", "fn second() {}\n");
    git(&root, &["add", "-A"]);
    git(&root, &["commit", "-qm", "B"]);
    git(&root, &["checkout", "-q", "main"]);
    put(&root, "rust/lib.rs", "fn main_edit() {}\n");
    git(&root, &["commit", "-qam", "main edits lib"]);
    let (rc, _) = super::git(&root, &["cherry-pick", "builder~1", "builder"]).unwrap();
    assert_ne!(rc, 0);
    // stopped on its first commit, the pick is named once, by its CHERRY_PICK_HEAD
    let stops = refusals(&root).unwrap();
    assert_eq!(stops.len(), 1, "{stops:?}");
    has(
        &stops[0],
        "(CHERRY_PICK_HEAD) - finish it: resolve 1 unmerged path(s)",
    );
    put(&root, "rust/lib.rs", "fn both() {}\n");
    git(&root, &["add", "-A"]);
    git(&root, &["commit", "-qm", "A, resolved by hand"]);
    assert!(!root.join(".git/CHERRY_PICK_HEAD").exists());
    assert_eq!(git(&root, &["status", "--porcelain"]), "");
    assert!(!root.join("rust/second.rs").exists());
    let stops = refusals(&root).unwrap();
    assert_eq!(stops.len(), 1, "{stops:?}");
    has(
        &stops[0],
        "a cherry-pick of several commits is in progress in ",
    );
    has(&stops[0], "(sequencer/todo) - finish it: `git -C ");
    has(&stops[0], "(or take it back: `git -C ");
    has(&stops[0], " cherry-pick --abort`)");
    run_printed(&stops[0], "finish it: ");
    assert!(root.join("rust/second.rs").exists());
    assert_eq!(refusals(&root).unwrap(), Vec::<String>::new());
    // a revert of several, paused the same way, is named a revert
    std::fs::create_dir_all(root.join(".git/sequencer")).unwrap();
    std::fs::write(root.join(".git/sequencer/todo"), "revert 1234567 B\n").unwrap();
    let stops = refusals(&root).unwrap();
    has(&stops[0], "a revert of several commits is in progress in ");
    has(&stops[0], "-c core.editor=true revert --continue`");
}

#[test]
fn unmerged_paths_and_staged_changes_are_refused_with_nothing_in_progress() {
    let (_dir, root) = repo("unfinished-staged");
    t270_state(&root);
    // the pick's marker gone, as after `git cherry-pick --quit`: the paths still stand
    std::fs::remove_file(root.join(".git/CHERRY_PICK_HEAD")).unwrap();
    let stops = refusals(&root).unwrap();
    assert_eq!(stops.len(), 2, "{stops:?}");
    has(&stops[0], "1 path(s) unmerged in ");
    has(
        &stops[0],
        "(specs/451-x/tasks.md) - resolve each, then `git -C ",
    );
    has(&stops[1], "1 staged path(s) stand uncommitted in ");
    has(&stops[1], "(rust/held.rs) - commit them: `git -C ");
    put(&root, "specs/451-x/tasks.md", &with_line("T271"));
    run_printed(&stops[0], "resolve each, then ");
    // unstaged as printed: an untracked file is no refusal of this check's
    run_printed(&stops[1], "(or unstage them: ");
    assert_eq!(refusals(&root).unwrap(), Vec::<String>::new());
    // past six paths the rest are counted
    for n in 0..8 {
        put(&root, &format!("rust/n{n}.rs"), "x");
    }
    git(&root, &["add", "-A"]);
    let stops = refusals(&root).unwrap();
    has(&stops[0], "9 staged path(s) stand uncommitted in ");
    has(&stops[0], "rust/n4.rs and 3 more) - commit them");
}

#[test]
fn a_directory_that_is_no_git_tree_is_said_so() {
    let dir = scratch("unfinished-no-git");
    let err = refusals(&dir).unwrap_err();
    has(&err, "is no git tree");
    let said = cli(&dir);
    assert_eq!(said.code, 2);
    has(&said.stderr, "unfinished: ");
    assert!(super::git(Path::new("/"), &["-C", "\0"]).is_err());
}
