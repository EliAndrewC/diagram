//! `make land` carrying its tasks' done commits before anything else (451 T397 part (c)): a commit `make builder-done` kept is in HEAD
//! before the first pass asks, two are carried oldest first, a carry that stops lands nothing, and a dirty clone carries before it
//! lands alone.

use std::path::{Path, PathBuf};

use l7r_gate_core::ci::fixtures::{git, put};
use l7r_shared::builder_pool;

use super::super::tests::{fx, has, Fx, NOTE};

/// The fixture's feature, as `make builder-done` keys its refs.
const F: &str = "449";

/// A builder's linked worktree beside the clone, detached at its HEAD.
fn side(fx: &Fx) -> PathBuf {
    let tree = fx.dir.join("side");
    git(
        &fx.root,
        &["worktree", "add", "-q", "--detach", &tree.to_string_lossy()],
    );
    tree
}

/// A commit of `rel` in `tree` from the clone's HEAD, its author's time `at`, kept under `refs/l7r/done/449-<task>`: its sha.
fn kept(fx: &Fx, tree: &Path, task: &str, rel: &str, at: u64) -> String {
    git(tree, &["checkout", "-q", "--detach", "main"]);
    put(tree, rel, &format!("{rel}\n"));
    git(tree, &["add", "-A"]);
    git(tree, &["commit", "-qm", rel, &format!("--date=@{at}")]);
    let sha = git(tree, &["rev-parse", "HEAD"]);
    git(
        &fx.root,
        &["update-ref", &format!("refs/l7r/done/{F}-{task}"), &sha],
    );
    sha
}

/// The done refs the clone still keeps.
fn waiting(root: &Path) -> String {
    git(
        root,
        &["for-each-ref", "--format=%(refname)", "refs/l7r/done"],
    )
}

fn landed(fx: &Fx, tasks: &[&str]) -> Result<i32, String> {
    let tasks: Vec<String> = tasks.iter().map(|t| (*t).to_owned()).collect();
    fx.land.land(&fx.root.join("specs/449-x"), &tasks, NOTE)
}

/// RED FIRST: the session's hand step, gone - `make builder-done` keeps T1's work, and the landing's first step carries it, so the
/// first pass (refusing here on the holding box) reads a HEAD that holds it, and the ref no longer says it waits.
#[test]
fn a_landing_carries_its_tasks_done_commit_before_its_first_pass() {
    let fx = fx("carry-done-first");
    let tree = side(&fx);
    let held = builder_pool::Tree {
        tree: tree.clone(),
        feature: F.to_owned(),
        tasks: vec!["T1".to_owned()],
        since: String::new(),
    };
    builder_pool::write(&fx.root.join(".git"), &[held]).unwrap();
    put(&tree, "notes/built.txt", "built\n");
    let args = ["T1".to_owned(), F.to_owned()];
    let said = l7r_gate_task::builder_done::cli_with(&args, &fx.root, "449 T1: built", "");
    assert_eq!((said.code, said.stderr.as_str()), (0, ""));
    let sha = git(&fx.root, &["rev-parse", "refs/l7r/done/449-T1"]);
    *fx.answers.holding.borrow_mut() = "T9 nine  <- the active task\n".to_owned();
    assert_eq!(landed(&fx, &["T1"]), Ok(2));
    let (out, err) = fx.said();
    has(
        &out,
        "land: carrying 1 done commit(s) of T1 that HEAD does not hold, oldest first (451 T397)\n",
    );
    has(&out, &format!("carry: {} carried into", &sha[..10]));
    has(&err, "land: refused before anything ran");
    has(&err, "held by T9 nine");
    assert_eq!(
        std::fs::read_to_string(fx.root.join("notes/built.txt")).unwrap(),
        "built\n"
    );
    assert_eq!(waiting(&fx.root), "");
}

/// Two tasks' commits carried OLDEST FIRST by their author's time, whatever order they were made in; a task with no done ref and a
/// commit HEAD already holds carry nothing.
#[test]
fn done_commits_are_carried_oldest_first_and_a_held_one_is_left() {
    let fx = fx("carry-done-order");
    let tree = side(&fx);
    kept(&fx, &tree, "T1", "notes/newer.txt", 1_700_000_000);
    kept(&fx, &tree, "T2", "notes/older.txt", 1_600_000_000);
    *fx.answers.holding.borrow_mut() = "T9 nine  <- the active task\n".to_owned();
    assert_eq!(landed(&fx, &["T1", "T2"]), Ok(2));
    assert_eq!(fx.subjects(), "notes/newer.txt\nnotes/older.txt");
    has(&fx.said().0, "land: carrying 2 done commit(s) of T1 T2");
    // a ref whose commit HEAD holds (finished by hand, its author's time and subject in HEAD) carries nothing and is left
    let again = super::super::tests::fx("carry-done-held");
    git(&again.root, &["update-ref", "refs/l7r/done/449-T1", "HEAD"]);
    assert_eq!(landed(&again, &["T1"]), Ok(0));
    assert!(!again.said().0.contains("carrying"));
    assert_eq!(waiting(&again.root), "refs/l7r/done/449-T1");
}

/// A carry that stops - a code conflict no rule resolves - lands nothing: the first pass and the gate never run, and the refusal names
/// the commit, its hand command and the carry before it that stands.
#[test]
fn a_carry_that_stops_lands_nothing_and_names_its_hand_command() {
    let fx = fx("carry-done-stops");
    let tree = side(&fx);
    let first = kept(&fx, &tree, "T1", "notes/first.txt", 1_600_000_000);
    let stops = kept(&fx, &tree, "T2", "code.rs", 1_700_000_000);
    fx.in_delta("code.rs", "fn ours() {}\n");
    assert_eq!(landed(&fx, &["T1", "T2"]), Ok(2));
    let err = fx.said().1;
    has(&err, &format!("carry: STOPPED - {}", &stops[..10]));
    has(&err, &format!("land: refused before anything ran - nothing landed, nothing ticked: the done commit {} (refs/l7r/done/449-T2) did not carry", &stops[..10]));
    has(
        &err,
        &format!("carried before it, in HEAD and verified: {}", &first[..10]),
    );
    has(&err, &format!("`make carry COMMIT={stops}`"));
    assert!(!fx.log().contains("stamp --check"));
    assert!(fx.answers.asked.borrow().is_empty());
    assert_eq!(waiting(&fx.root), "refs/l7r/done/449-T2");
}

/// A dirty clone carries before it is sent to land alone: the landing worktree is checked out at a HEAD that holds the commit.
#[test]
fn a_dirty_clone_carries_before_it_lands_alone() {
    let fx = fx("carry-done-alone");
    let tree = side(&fx);
    kept(&fx, &tree, "T1", "notes/built.txt", 1_600_000_000);
    put(&fx.root, "untracked.txt", "x");
    let _ = landed(&fx, &["T1"]);
    let out = fx.said().0;
    let carried = out.find("carry: ").unwrap();
    let alone = out.find("lands alone").unwrap();
    assert!(carried < alone);
    assert!(fx.root.join("notes/built.txt").is_file());
}
