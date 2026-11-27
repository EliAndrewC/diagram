//! `make builder-done` on a real repository and its pool (feature 451 T394): a builder's tree committed, kept under its ref and
//! released in one call, the commit outliving the tree's next handout; each refusal with nothing done; a guard file with and
//! without `GUARD=`; a bundle; a done ref never written over while its commit waits on its carry, and its task handed no tree until
//! then (451 T398).

use std::path::{Path, PathBuf};

use l7r_gate_core::ci::fixtures::{commit, git, put};
use l7r_gate_core::write_executable;
use l7r_gate_core::Reply;

use super::{guard_file, quoted, run, TRAILER};
use crate::builder_tree::tests::{env, pool_of, words, world};
use crate::builder_tree::{self, Env};

/// The fixture's clone, `*.profraw` ignored as the project ignores it, its environment, and the tree `tasks` took.
fn held(tag: &str, tasks: &str) -> (l7r_shared::tempdir::TempDir, PathBuf, Env, PathBuf) {
    let (dir, root) = world(tag);
    commit(&root, ".gitignore", "*.profraw\n");
    let mut e = env(&dir);
    e.prewarm = false;
    let took = builder_tree::run(&words(&["take", tasks, "9001"]), &root, &e);
    let tree = PathBuf::from(took.stdout.trim());
    assert!(tree.is_dir());
    (dir, root, e, tree)
}

fn done(root: &Path, e: &Env, tasks: &str, msg: &str, guard: &str) -> Reply {
    run(&words(&[tasks, "9001"]), root, e, msg, guard)
}

fn refs(root: &Path) -> String {
    git(
        root,
        &["for-each-ref", "--format=%(refname)", "refs/l7r/done"],
    )
}

fn list(root: &Path, e: &Env) -> String {
    builder_tree::run(&words(&["list"]), root, e).stdout
}

#[test]
fn a_tree_is_committed_kept_and_released_in_one_call_and_its_commit_outlives_the_next_handout() {
    let (_dir, root, e, b1) = held("done-one", "T01");
    let head = git(&root, &["rev-parse", "HEAD"]);
    assert!(list(&root, &e).ends_with("builder-trees: no done commit waits on its carry\n"));
    put(&b1, "scripts/a.py", "x = 2\n");
    put(&b1, "scripts/new.py", "y = 1\n");
    put(&b1, "default_1.profraw", "");
    put(&b1, "rust/x/default_2.profraw", "");
    put(&b1, "rust/x/kept.profraw", "");
    let said = done(&b1, &e, "T01", " 9001 T01: the reader reads\n", "");
    assert_eq!(said.code, 0);
    // the commit: the builder's work on the clone's HEAD, the subject and the trailer, under a ref of its own
    let sha = git(&root, &["rev-parse", "refs/l7r/done/9001-T01"]);
    assert_eq!(
        git(&root, &["log", "-1", "--format=%P%n%B", &sha]),
        format!("{head}\n9001 T01: the reader reads\n\n{TRAILER}")
    );
    assert_eq!(
        git(&root, &["show", "--name-only", "--format=", &sha]),
        "scripts/a.py\nscripts/new.py"
    );
    // the stray profile files went, another ignored file stayed
    assert!(
        !b1.join("default_1.profraw").exists() && !b1.join("rust/x/default_2.profraw").exists()
    );
    assert!(b1.join("rust/x/kept.profraw").exists());
    // the clone is untouched, the tree free and back at the clone's HEAD
    assert_eq!(git(&root, &["rev-parse", "HEAD"]), head);
    assert!(pool_of(&root)[0].free());
    assert_eq!(git(&b1, &["rev-parse", "HEAD"]), head);
    assert_eq!(git(&b1, &["status", "--porcelain"]), "");
    assert!(!b1.join("scripts/new.py").exists());
    // the pool's log: the done line with its commit, then the release
    let log = std::fs::read_to_string(root.join(".git/builder-pool.log")).unwrap();
    let lines: Vec<serde_json::Value> = log
        .lines()
        .map(|l| serde_json::from_str(l).unwrap())
        .collect();
    let at = lines.len() - 2;
    assert_eq!(
        (
            &lines[at]["event"],
            &lines[at]["commit"],
            &lines[at]["detail"]
        ),
        (
            &serde_json::json!("done"),
            &serde_json::json!(sha),
            &serde_json::json!("9001 T01")
        )
    );
    assert_eq!(lines[at]["tree"], serde_json::json!(b1));
    assert_eq!(lines[at + 1]["event"], "release");
    // what it prints: the commit, the release, then the next dispatch BEFORE the carry, the carry last
    let carry = format!("make carry FROM={} COMMIT={sha}", b1.display());
    assert!(
        said.stdout.contains("committed as") && said.stdout.contains("is free (9001 T01 released)")
    );
    let brief = said
        .stdout
        .find("make builder-brief T=<the first task of specs/9001-x/queue.md no tree holds> F=9001 KIND=")
        .unwrap();
    assert!(brief < said.stdout.find(&carry).unwrap());
    assert!(said.stdout.ends_with(&format!("  2. {carry}\n")));
    // the reader: the commit done and not yet carried, with its carry
    let listed = list(&root, &e);
    assert!(listed.contains("builder-trees: commits done and not yet carried into"));
    assert!(listed.contains(&format!(
        "  {}  9001-T01  9001 T01: the reader reads\n    {carry}\n",
        &sha[..10]
    )));
    // the tree's next handout: the done commit is still there to carry
    commit(&root, "scripts/later.py", "w = 1\n");
    let next = builder_tree::run(&words(&["take", "T02", "9001"]), &root, &e);
    assert_eq!(PathBuf::from(next.stdout.trim()), b1);
    assert_eq!(git(&root, &["rev-parse", "refs/l7r/done/9001-T01"]), sha);
    git(&root, &["cherry-pick", &sha]);
    assert_eq!(
        std::fs::read_to_string(root.join("scripts/new.py")).unwrap(),
        "y = 1\n"
    );
    // carried: the reader lets it go, and the next done drops its ref
    assert!(list(&root, &e).ends_with("builder-trees: no done commit waits on its carry\n"));
    put(&b1, "scripts/b.py", "z = 1\n");
    assert_eq!(done(&root, &e, "T02", "9001 T02: the second", "").code, 0);
    assert_eq!(refs(&root), "refs/l7r/done/9001-T02");
    // a done ref the log names no tree for is carried from the clone
    std::fs::remove_file(root.join(".git/builder-pool.log")).unwrap();
    assert!(list(&root, &e).contains(&format!("make carry FROM={} COMMIT=", root.display())));
}

/// A refusal with nothing done: its words, the tree still held with its work uncommitted, no ref.
fn refused(root: &Path, said: &Reply, why: &str) {
    assert_eq!(said.code, 2);
    assert!(said.stderr.contains(why));
    assert_eq!(said.stdout, "");
    assert!(!pool_of(root)[0].free());
    assert_eq!(refs(root), "");
}

#[test]
fn each_refusal_leaves_the_tree_held_and_nothing_committed() {
    let (dir, root, e, b1) = held("done-refused", "T01");
    let none: &[&str] = &[];
    let usage = run(&words(none), &root, &e, "m", "");
    refused(
        &root,
        &usage,
        "usage: make builder-done T=<task(s)> F=<n> MSG=",
    );
    let unnamed = run(&words(&["T01"]), &root, &e, "m", "");
    refused(&root, &unnamed, "F=<feature>");
    refused(
        &root,
        &done(&root, &e, "T01", " ", ""),
        "MSG is the commit's subject, one line",
    );
    refused(
        &root,
        &done(&root, &e, "T01", "a\nb", ""),
        "MSG is the commit's subject, one line",
    );
    refused(
        &root,
        &done(&root, &e, "T01", "m", "why"),
        "GUARD needs a reason of two words or more",
    );
    refused(
        &root,
        &done(&root, &e, "T07", "m", ""),
        "9001 T07 holds no pool tree",
    );
    let outside = run(&words(&["T01", "9001"]), &dir, &e, "m", "");
    assert_eq!(
        (outside.code, outside.stderr.as_str()),
        (2, "builder-done: not in a git repository\n")
    );
    // nothing to commit
    refused(&root, &done(&root, &e, "T01", "m", ""), "nothing to commit");
    // a conflict's markers in a changed file
    put(
        &b1,
        "scripts/a.py",
        "<<<<<<< ours\nx = 2\n=======\nx = 3\n>>>>>>> theirs\n",
    );
    let marked = done(&root, &e, "T01", "m", "");
    refused(&root, &marked, "a conflict's markers stand in scripts/a.py");
    put(&b1, "scripts/a.py", "x = 2\n");
    // a cherry-pick left unfinished
    let git_dir = PathBuf::from(git(&b1, &["rev-parse", "--absolute-git-dir"]));
    std::fs::write(git_dir.join("CHERRY_PICK_HEAD"), "x\n").unwrap();
    let picking = done(&root, &e, "T01", "m", "");
    refused(
        &root,
        &picking,
        "holds an unfinished cherry-pick (CHERRY_PICK_HEAD)",
    );
    std::fs::remove_file(git_dir.join("CHERRY_PICK_HEAD")).unwrap();
    assert_eq!(git(&b1, &["status", "--porcelain"]), "M scripts/a.py");
    // a bundle's tree is done by the whole bundle
    let b2 = builder_tree::run(&words(&["take", "T02,T03", "9001"]), &root, &e);
    put(Path::new(b2.stdout.trim()), "scripts/c.py", "c = 1\n");
    let part = done(&root, &e, "T02", "m", "");
    refused(
        &root,
        &part,
        "is held by 9001 T02,T03: make builder-done T=T02,T03 F=9001",
    );
    // a tree gone from disk
    std::fs::remove_dir_all(b2.stdout.trim()).unwrap();
    let gone = done(&root, &e, "T03,T02", "m", "");
    refused(&root, &gone, "is gone from disk");
}

#[test]
fn an_unmerged_path_is_refused() {
    let (_dir, root, e, b1) = held("done-unmerged", "T01");
    commit(&root, "scripts/a.py", "x = 5\n");
    let theirs = git(&root, &["rev-parse", "HEAD"]);
    commit(&b1, "scripts/a.py", "x = 7\n");
    let picked = std::process::Command::new("git")
        .arg("-C")
        .arg(&b1)
        .args(["cherry-pick", &theirs])
        .output()
        .unwrap();
    assert!(!picked.status.success());
    // the markers resolved by hand, the pick's own marker gone, the path never added
    put(&b1, "scripts/a.py", "x = 7\n");
    let git_dir = PathBuf::from(git(&b1, &["rev-parse", "--absolute-git-dir"]));
    std::fs::remove_file(git_dir.join("CHERRY_PICK_HEAD")).unwrap();
    let said = done(&root, &e, "T01", "m", "");
    refused(&root, &said, "an unmerged path stands: scripts/a.py");
}

#[test]
fn a_guard_file_is_committed_only_with_its_reason_and_the_refusal_prints_the_re_run() {
    let (_dir, root, e, b1) = held("done-guard", "T01");
    put(&b1, "Makefile", "all:\n");
    put(&b1, "scripts/hooks/x-hooks.sh", "#!/bin/sh\n");
    let bare = done(&root, &e, "T01", "9001 T01: it's built", "");
    refused(
        &root,
        &bare,
        "changes a guard file (Makefile, scripts/hooks/x-hooks.sh)",
    );
    assert!(
        bare.stderr.contains("  make builder-done T=T01 F=9001 MSG='9001 T01: it'\\''s built' GUARD=\"<what the guard-file edit does, and why it is legitimate>\"\n"));
    let said = done(
        &root,
        &e,
        "T01",
        "9001 T01: it's built",
        " adding an operation ",
    );
    assert_eq!(said.code, 0);
    assert_eq!(
        git(
            &root,
            &["log", "-1", "--format=%B", "refs/l7r/done/9001-T01"]
        ),
        format!("9001 T01: it's built\nGUARD_EDIT_OK: adding an operation\n\n{TRAILER}")
    );
    assert_eq!(quoted("a b"), "'a b'");
    for held in [
        "Makefile",
        "rust/x/Makefile",
        "scripts/gates/a-hooks.sh",
        ".claude/settings.json",
        "tests/rolls.py",
        "dev/switches.json",
        "dev/work-budget.json",
        "rust/guard/src/guards/a.rs",
        "rust/guard/shared/src/lib.rs",
        "rust/guard/Cargo.toml",
        "rust/guard/shared/Cargo.toml",
        "scripts/hooks/l7r-guard.sh",
        "scripts/hooks/l7r-hook",
    ] {
        assert!(guard_file(held));
    }
    for free in [
        "tests/hooks/test-a-hooks.sh",
        "scripts/tests/hooks/test-a-hooks.sh",
        "rust/guard/src/guards/a/tests.rs",
        "rust/guard/src/tests/fixture.txt",
        "rust/gate/src/lib.rs",
        "docs/Makefile.md",
        "scripts/gates/review-gate.sh",
    ] {
        assert!(!guard_file(free));
    }
}

#[test]
fn a_bundle_is_one_commit_under_a_ref_for_each_task() {
    let (dir, root) = world("done-bundle");
    let mut e = env(&dir);
    e.prewarm = false;
    let took = builder_tree::run(&words(&["take", "T01,T02", "77"]), &root, &e);
    let b1 = PathBuf::from(took.stdout.trim());
    put(&b1, "scripts/n.py", "n = 1\n");
    let said = run(
        &words(&["T02 T01", "77"]),
        &root,
        &e,
        "77 T01 T02: both",
        "",
    );
    assert_eq!(said.code, 0);
    let sha = git(&root, &["rev-parse", "refs/l7r/done/77-T01"]);
    assert_eq!(git(&root, &["rev-parse", "refs/l7r/done/77-T02"]), sha);
    assert!(pool_of(&root)[0].free());
    let log = std::fs::read_to_string(root.join(".git/builder-pool.log")).unwrap();
    assert!(log.contains("\"detail\":\"77 T01,T02\"") && log.contains("\"event\":\"done\""));
    // no feature directory to name: the queue's place as a pattern
    assert!(said.stdout.contains(
        "make builder-brief T=<the first task of specs/77-*/queue.md no tree holds> F=77 KIND="
    ));
    let listed = list(&root, &e);
    assert!(listed.contains(&format!(
        "  {}  77-T01, 77-T02  77 T01 T02: both\n",
        &sha[..10]
    )));
}

#[test]
fn a_done_commit_not_yet_carried_is_never_written_over() {
    let (_dir, root, e, b1) = held("done-twice", "T01");
    // a done commit of T01 the clone's HEAD does not hold, while T01 holds the tree: a ref written by hand, as a tree held some
    // other way than a handout would leave it (the handout itself is refused, the next test)
    // (its subject its own: a commit is told carried by its author's second and its subject, and the fixture's commits share both)
    put(&b1, "scripts/n.py", "n = 1\n");
    git(&b1, &["add", "-A"]);
    git(&b1, &["commit", "-qm", "9001 T01: the build half"]);
    let first = git(&b1, &["rev-parse", "HEAD"]);
    git(&root, &["update-ref", "refs/l7r/done/9001-T01", &first]);
    put(&b1, "scripts/o.py", "o = 1\n");
    let said = done(&root, &e, "T01", "9001 T01: the closing half", "");
    assert_eq!(said.code, 2);
    assert!(said.stderr.contains(&format!(
        "builder-done: refused - nothing done: refs/l7r/done/9001-T01 ({}, \"9001 T01: the build half\") is done and not yet carried - carry it first: make carry FROM={} COMMIT={first}\n",
        &first[..10],
        root.display()
    )));
    assert_eq!(git(&root, &["rev-parse", "refs/l7r/done/9001-T01"]), first);
    assert!(!pool_of(&root)[0].free() && b1.join("scripts/o.py").exists());
    // carried: the second commit takes the ref
    git(&root, &["cherry-pick", &first]);
    assert_eq!(
        done(&root, &e, "T01", "9001 T01: the closing half", "").code,
        0
    );
    let second = git(&root, &["rev-parse", "refs/l7r/done/9001-T01"]);
    assert_ne!(second, first);
    assert_eq!(
        git(&root, &["log", "-1", "--format=%s", &second]),
        "9001 T01: the closing half"
    );
}

#[test]
fn a_task_is_handed_no_tree_while_its_own_done_commit_waits_on_its_carry() {
    let (_dir, root, e, b1) = held("done-handout", "T01");
    put(&b1, "scripts/n.py", "n = 1\n");
    assert_eq!(
        done(&root, &e, "T01", "9001 T01: the build half", "").code,
        0
    );
    let first = git(&root, &["rev-parse", "refs/l7r/done/9001-T01"]);
    // the closing half's handout before the build half's carry: refused with the carry, alone or in a bundle, nothing taken
    for tasks in ["T01", "T03,T01"] {
        let took = builder_tree::run(&words(&["take", tasks, "9001"]), &root, &e);
        assert_eq!((took.code, took.stdout.as_str()), (2, ""));
        assert_eq!(
            took.stderr,
            format!(
                "builder-tree: refused - no tree handed out: refs/l7r/done/9001-T01 ({}, \"9001 T01: the build half\") is done and not yet carried - carry it first: make carry FROM={} COMMIT={first}\n  a handout starts at the clone's HEAD, so this task's next builder would start without that commit's work\n",
                &first[..10],
                b1.display()
            )
        );
        assert!(pool_of(&root)[0].free());
    }
    // another task's handout, and another feature's task of the same id, wait on nothing
    let other = builder_tree::run(&words(&["take", "T02", "9001"]), &root, &e);
    assert_eq!(other.code, 0);
    assert_eq!(Path::new(other.stdout.trim()), b1);
    assert_eq!(
        builder_tree::run(&words(&["release", "T02", "9001"]), &root, &e).code,
        0
    );
    let alike = builder_tree::run(&words(&["take", "T01", "77"]), &root, &e);
    assert_eq!(alike.code, 0);
    assert_eq!(
        builder_tree::run(&words(&["release", "T01", "77"]), &root, &e).code,
        0
    );
    // carried: the task's next builder is handed its tree, at a HEAD that holds the build half's work
    git(&root, &["cherry-pick", &first]);
    let took = builder_tree::run(&words(&["take", "T01", "9001"]), &root, &e);
    assert_eq!(took.code, 0);
    assert_eq!(Path::new(took.stdout.trim()), b1);
    assert!(b1.join("scripts/n.py").exists());
}

#[test]
fn a_commit_git_refuses_leaves_nothing_staged_and_the_tree_held() {
    let (_dir, root, e, b1) = held("done-hook", "T01");
    std::fs::create_dir_all(root.join(".git/hooks")).unwrap();
    write_executable(
        &root.join(".git/hooks/pre-commit"),
        "#!/bin/sh\necho the hook says no >&2\nexit 1\n",
    );
    put(&b1, "scripts/n.py", "n = 1\n");
    let said = done(&root, &e, "T01", "m", "");
    assert_eq!(said.code, 1);
    assert!(said.stderr.contains("git commit failed") && said.stderr.contains("the hook says no"));
    assert_eq!(git(&b1, &["status", "--porcelain"]), "?? scripts/n.py");
    assert!(!pool_of(&root)[0].free());
    assert_eq!(refs(&root), "");
}
