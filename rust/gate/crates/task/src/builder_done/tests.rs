//! `make builder-done` on a real repository and its pool (feature 451 T394): a builder's tree committed, kept under its ref and
//! released in one call, the commit outliving the tree's next handout; each refusal with nothing done; a guard file with and
//! without `GUARD=`; a bundle; a done ref never written over while its commit waits on its carry, but by a hold whose handout built
//! on it (461 T09), and its task's next handout building on it - or, with no apply program, handed no tree until then (451 T398).

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
        .find("  1. no next dispatch named: specs/9001-x/queue.txt: ")
        .unwrap();
    assert!(brief < said.stdout.find(&carry).unwrap());
    // 451 T450: the landing carries the commit; make carry is named for a carry by hand or a stopped one
    let land = format!("  2. make land F=9001 T=\"T01\" NOTE=\"<what was verified>\" - it carries this commit first (by hand, or where a carry stopped: {carry})\n");
    assert!(said.stdout.ends_with(&land), "{}", said.stdout);
    let order = "the next dispatch FIRST, the landing after it";
    assert!(said.stdout.contains(order));
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
    // no feature directory to name: no queue to read
    let unnamed = format!("  1. no next dispatch named: no specs/77-* directory in {} - make queue-add T=<task(s)> KIND=<kind> F=77 starts the queue\n", root.display());
    assert!(said.stdout.contains(&unnamed), "{}", said.stdout);
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
    // other way than a handout would leave it (a handout builds on the commit and logs it, 461 T09: this hold logged none)
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
fn another_tasks_done_keeps_the_ref_of_a_commit_that_waits_and_deletes_a_carried_ones() {
    let (_dir, root, e, b1) = held("done-waits", "T01");
    // (each commit's subject its own: a commit is told carried by its author's second and its subject)
    put(&b1, "scripts/n.py", "n = 1\n");
    assert_eq!(done(&root, &e, "T01", "9001 T01: waits", "").code, 0);
    let first = git(&root, &["rev-parse", "refs/l7r/done/9001-T01"]);
    // T02's done while T01's commit waits on its carry: T01's ref is kept beside T02's
    let done_in_turn = |task: &str, file: &str, subject: &str| {
        let took = builder_tree::run(&words(&["take", task, "9001"]), &root, &e);
        assert_eq!(Path::new(took.stdout.trim()), b1);
        put(&b1, file, "o = 1\n");
        assert_eq!(done(&root, &e, task, subject, "").code, 0);
    };
    done_in_turn("T02", "scripts/o.py", "9001 T02: carried next");
    assert_eq!(
        refs(&root),
        "refs/l7r/done/9001-T01\nrefs/l7r/done/9001-T02"
    );
    // T02's commit carried, T01's still not: T03's done deletes T02's ref and keeps T01's, at the commit it named
    let second = git(&root, &["rev-parse", "refs/l7r/done/9001-T02"]);
    git(&root, &["cherry-pick", &second]);
    done_in_turn("T03", "scripts/p.py", "9001 T03: the last");
    assert_eq!(
        refs(&root),
        "refs/l7r/done/9001-T01\nrefs/l7r/done/9001-T03"
    );
    assert_eq!(git(&root, &["rev-parse", "refs/l7r/done/9001-T01"]), first);
    assert!(list(&root, &e).contains(&format!("  {}  9001-T01  9001 T01: waits\n", &first[..10])));
}

/// With no apply program known (`env.apply` empty, the gate binary not found) a handout cannot build on the task's own done commit,
/// so it waits for the carry, as before 461 T09 (451 T398).
#[test]
fn with_no_apply_program_a_task_is_handed_no_tree_while_its_own_done_commit_waits_on_its_carry() {
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

/// A stand-in for the no-commit carry's door (`l7r-gate land --carry --no-commit "" <sha>`, 461 T05), its words for the `Env`: it
/// writes the tree it ran in and its arguments to `apply.sh.args` beside it, then runs `body`.
fn applier(dir: &Path, body: &str) -> Vec<String> {
    let at = dir.join("apply.sh");
    write_executable(
        &at,
        &format!("#!/bin/sh\nprintf '%s\\n' \"$(git rev-parse --show-toplevel)\" \"$@\" > \"$0.args\"\n{body}\n"),
    );
    [&*at.to_string_lossy(), "land", "--carry", "--no-commit"]
        .map(str::to_owned)
        .to_vec()
}

/// 461 T09 (plan D14): a task's next builder is handed its tree while its earlier done commit waits on its carry - the commit
/// applied onto the clone's HEAD uncommitted - and its done supersedes the earlier ref: one ref, one commit of both halves.
#[test]
fn a_closing_half_handed_out_before_its_build_half_s_carry_builds_on_it_and_its_done_leaves_one_ref(
) {
    let (dir, root, mut e, b1) = held("done-builds-on", "T01");
    e.apply = applier(&dir, "exec git cherry-pick -n \"$5\"");
    put(&b1, "scripts/n.py", "n = 1\n");
    assert_eq!(
        done(&root, &e, "T01", "9001 T01: the build half", "").code,
        0
    );
    let first = git(&root, &["rev-parse", "refs/l7r/done/9001-T01"]);
    // the clone moves on before the closing half's handout: its base is the clone's HEAD, the build half applied on it
    commit(&root, "scripts/m.py", "m = 1\n");
    let head = git(&root, &["rev-parse", "HEAD"]);
    let took = builder_tree::run(&words(&["take", "T01", "9001"]), &root, &e);
    assert_eq!(took.code, 0, "{}", took.stderr);
    assert_eq!(Path::new(took.stdout.trim()), b1);
    assert!(took.stderr.contains(&format!(
        "builder-tree: it builds on refs/l7r/done/9001-T01 ({}, \"9001 T01: the build half\"), not yet carried: applied onto the clone's HEAD uncommitted - the builder's done supersedes it\n",
        &first[..10]
    )));
    assert_eq!(git(&b1, &["rev-parse", "HEAD"]), head);
    assert_eq!(git(&b1, &["status", "--porcelain"]), "A  scripts/n.py");
    assert!(b1.join("scripts/m.py").exists());
    // the door as T05 built it: run in the tree, the commit by its sha alone
    let args = std::fs::read_to_string(dir.join("apply.sh.args")).unwrap();
    let at = b1.canonicalize().unwrap();
    assert_eq!(
        args,
        format!("{}\nland\n--carry\n--no-commit\n\n{first}\n", at.display())
    );
    // the closing half's done: one commit of both halves on the handout's base, the one ref moved to it
    put(&b1, "scripts/o.py", "o = 1\n");
    let said = done(&root, &e, "T01", "9001 T01: the closing half", "");
    assert_eq!(said.code, 0);
    assert_eq!(refs(&root), "refs/l7r/done/9001-T01");
    let second = git(&root, &["rev-parse", "refs/l7r/done/9001-T01"]);
    assert_ne!(second, first);
    assert_eq!(git(&root, &["log", "-1", "--format=%P", &second]), head);
    assert_eq!(
        git(&root, &["show", "--name-only", "--format=", &second]),
        "scripts/n.py\nscripts/o.py"
    );
    assert!(!list(&root, &e).contains(&first[..10]));
}

/// 461 T09: an apply that does not end verified (its conflict, its failed end, a program that does not start) hands no tree out -
/// the tree put back clean at the clone's HEAD and free, the carry named - and logs nothing it built on.
#[test]
fn a_handout_whose_apply_does_not_end_verified_is_refused_with_the_tree_put_back_free() {
    let (dir, root, mut e, b1) = held("done-apply-fails", "T01");
    put(&b1, "scripts/n.py", "n = 1\n");
    assert_eq!(
        done(&root, &e, "T01", "9001 T01: the build half", "").code,
        0
    );
    let first = git(&root, &["rev-parse", "refs/l7r/done/9001-T01"]);
    let head = git(&root, &["rev-parse", "HEAD"]);
    let named = format!(
        "builder-tree: refused - no tree handed out: the handout could not build on refs/l7r/done/9001-T01 ({}, \"9001 T01: the build half\"), not yet carried: its no-commit apply onto the clone's HEAD did not end verified - ",
        &first[..10]
    );
    let carry = format!(
        "\n  the tree is put back at the clone's HEAD and free; carry it first: make carry FROM={} COMMIT={first}\n",
        b1.display()
    );
    let stubs = [
        (
            "git cherry-pick -n \"$5\" >/dev/null 2>&1\necho 'carry: 1 path(s) unmerged' >&2\nexit 2",
            "it exited 2:\ncarry: 1 path(s) unmerged",
        ),
        (
            "git cherry-pick -n \"$5\" >/dev/null 2>&1\necho NOT VERIFIED\nexit 1",
            "it exited 1:\nNOT VERIFIED",
        ),
    ];
    for (body, why) in stubs {
        e.apply = applier(&dir, body);
        let took = builder_tree::run(&words(&["take", "T01", "9001"]), &root, &e);
        assert_eq!((took.code, took.stdout.as_str()), (2, ""));
        assert!(
            took.stderr.ends_with(&format!("{named}{why}{carry}")),
            "{}",
            took.stderr
        );
        assert!(pool_of(&root)[0].free());
        assert_eq!(git(&b1, &["rev-parse", "HEAD"]), head);
        assert_eq!(git(&b1, &["status", "--porcelain"]), "");
    }
    e.apply = vec!["/no/such/apply".to_owned()];
    let took = builder_tree::run(&words(&["take", "T01", "9001"]), &root, &e);
    assert_eq!(took.code, 2);
    assert!(took
        .stderr
        .contains(&format!("{named}it did not start (/no/such/apply: ")));
    assert!(took.stderr.ends_with(&carry));
    assert!(pool_of(&root)[0].free());
    let log = std::fs::read_to_string(root.join(".git/builder-pool.log")).unwrap();
    assert!(!log.contains("\"builds-on\""));
    assert_eq!(refs(&root), "refs/l7r/done/9001-T01");
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

/// THE NEXT DISPATCH IS THE QUEUE'S (451 T313, T395): the first READY entry that overlaps no task in flight, with its command;
/// the task just done reads as built and is never named again; no entry to hand out says why.
#[test]
fn the_next_dispatch_is_the_queue_s_next_entry() {
    let (_dir, root, e, b1) = held("done-queue", "T01");
    put(&root, "specs/9001-x/queue.txt", "T01 fix files=scripts/a.py\nT02 fix files=scripts/a.py\nT03 fix jobs=2 crates=rust/x files=-\n");
    builder_tree::run(&words(&["take", "T02", "9001"]), &root, &e);
    put(&b1, "scripts/a.py", "x = 2\n");
    let said = done(&b1, &e, "T01", "9001 T01: one", "");
    assert_eq!(said.code, 0);
    let sha = git(&root, &["rev-parse", "refs/l7r/done/9001-T01"]);
    let want = format!("  1. make builder-brief T=T03 F=9001 KIND=fix JOBS=2 CRATE=\"rust/x\" ENTRY=1   (9001 T03, line 3 of specs/9001-x/queue.txt: the next READY entry that overlaps no task in flight, performance work of any queue first)\n  2. make land F=9001 T=\"T01\" NOTE=\"<what was verified>\" - it carries this commit first (by hand, or where a carry stopped: make carry FROM={} COMMIT={sha})\n", b1.display());
    assert!(said.stdout.ends_with(&want), "{}", said.stdout);
    // T03 handed out and T02 done: nothing is left to hand out, and T01, built, is not offered again
    builder_tree::run(&words(&["take", "T03", "9001"]), &root, &e);
    let b2 = pool_of(&root)[1].tree.clone();
    put(&b2, "scripts/b.py", "y = 2\n");
    let said = done(&b2, &e, "T02", "9001 T02: two", "");
    assert_eq!(said.code, 0);
    let none = "  1. no next dispatch: the queue is empty: each entry is landed, built or in flight (make queue F=9001)\n";
    assert!(said.stdout.contains(none), "{}", said.stdout);
}

/// 451 T313's round-3 ruling: step 1 takes `idle`'s any-queue preference - a READY performance entry of another active feature's
/// queue before the done task's own feature's first pick - and names an open performance task no queue line names first.
#[test]
fn the_next_dispatch_prefers_performance_work_of_any_queue() {
    let (_dir, root, e, b1) = held("done-any-queue", "T01");
    put(
        &root,
        "specs/9001-x/queue.txt",
        "T01 fix files=scripts/a.py\nT02 fix files=docs/a.md\n",
    );
    put(&root, "specs/9002-y/spec.md", "**Status**: In progress\n");
    put(
        &root,
        "specs/9002-y/tasks.md",
        "- [ ] T05 [perf] split the suite\n- [ ] T06 [perf] the faster gate\n",
    );
    put(&root, "specs/9002-y/queue.txt", "T05 fix files=docs/b.md\n");
    put(
        &root,
        ".git/task-starts.jsonl",
        "{\"feature\": \"9002-y\", \"task\": \"T05\", \"utc\": \"2026-11-27T01:00:00Z\"}\n",
    );
    put(&b1, "scripts/a.py", "x = 2\n");
    let said = done(&b1, &e, "T01", "9001 T01: one", "");
    assert_eq!(said.code, 0);
    let want = "  1. FIRST, open performance work (FR-013) no queue line names - write each one's line (CRATE= and FILES= as its task line names them, WAITS= where it waits, which quiets it):\n     make queue-add F=9002 T=T06 KIND=fix   (9002 T06, KIND by make builder-brief's mechanism test)\n     make builder-brief T=T05 F=9002 KIND=fix ENTRY=1   (9002 T05, line 1 of specs/9002-y/queue.txt: the next READY entry that overlaps no task in flight, performance work of any queue first)\n  2. make land F=9001 T=\"T01\"";
    assert!(said.stdout.contains(want), "{}", said.stdout);
    // the other queue's performance entry lined and waiting, T06's too: the done task's own feature's pick
    put(
        &root,
        "specs/9002-y/queue.txt",
        "T05 fix files=docs/b.md waits=GM\nT06 fix files=- waits=GM\n",
    );
    let p = crate::builder_tree::pool(&root).unwrap();
    let next = crate::builder_queue::dispatch(&p, "9001");
    let own =
        next.starts_with("make builder-brief T=T02 F=9001 KIND=fix ENTRY=1   (9001 T02, line 2 of");
    assert!(own, "{next}");
    // the done task's feature holds no queue: said, and another queue's pick still named
    put(
        &root,
        "specs/9002-y/queue.txt",
        "T05 fix files=docs/b.md\nT06 fix files=- waits=GM\n",
    );
    let next = crate::builder_queue::dispatch(&p, "77");
    let named = next.starts_with("no next dispatch named: no specs/77-* directory in ")
        && next.contains("\n     make builder-brief T=T05 F=9002 KIND=fix ENTRY=1   (9002 T05");
    assert!(named, "{next}");
    // nothing to hand out anywhere, and the feature's queue missing: the one line
    std::fs::remove_file(root.join("specs/9002-y/queue.txt")).unwrap();
    std::fs::remove_file(root.join("specs/9001-x/queue.txt")).unwrap();
    let next = crate::builder_queue::dispatch(&p, "9001");
    let first =
        next.starts_with("FIRST, ") && next.contains("make queue-add F=9002 T=T05 KIND=fix");
    assert!(first, "{next}");
    assert!(next.ends_with("\n     no next dispatch named: specs/9001-x/queue.txt: No such file or directory (os error 2) - make queue-add T=<task(s)> KIND=<kind> F=9001 starts the queue\n"), "{next}");
}

/// What `make land` carries (451 T397 part (c)): the landed tasks' done commits HEAD lacks, each once - two tasks of one bundle
/// share a commit - oldest first by its author's time, whatever order they were made in; a commit HEAD holds and a task not landed
/// are left.
#[test]
fn the_commits_a_landing_carries_are_its_tasks_uncarried_ones_once_and_oldest_first() {
    let (_dir, root) = world("done-to-carry");
    git(&root, &["checkout", "-q", "-b", "side"]);
    let at = |rel: &str, when: u64| {
        put(&root, rel, "x\n");
        git(&root, &["add", "-A"]);
        git(&root, &["commit", "-qm", rel, &format!("--date=@{when}")]);
        git(&root, &["rev-parse", "HEAD"])
    };
    let newer = at("n.txt", 1_700_000_000);
    let older = at("o.txt", 1_600_000_000);
    git(&root, &["checkout", "-q", "-"]);
    let head = git(&root, &["rev-parse", "HEAD"]);
    for (task, sha) in [
        ("T01", &newer),
        ("T02", &older),
        ("T03", &older),
        ("T04", &head),
        ("T05", &newer),
    ] {
        git(
            &root,
            &["update-ref", &format!("refs/l7r/done/9001-{task}"), sha],
        );
    }
    let tasks: Vec<String> = ["T01", "T02", "T03", "T04"]
        .iter()
        .map(|t| (*t).to_owned())
        .collect();
    assert_eq!(
        super::to_carry(&root, "specs/9001-x", &tasks),
        vec![
            (
                older,
                vec![
                    "refs/l7r/done/9001-T02".to_owned(),
                    "refs/l7r/done/9001-T03".to_owned()
                ]
            ),
            (newer, vec!["refs/l7r/done/9001-T01".to_owned()]),
        ]
    );
    assert!(super::to_carry(&root, "9001", &["T09".to_owned()]).is_empty());
}

/// 461 T07: the hand-in's door in - the tree found as `make builder-done` finds it, its refusals asked, and a commit made elsewhere
/// than the tree's HEAD kept under the done ref with `"handed_in": true` on its `done` line, the tree released.
#[test]
fn a_found_tree_s_commit_made_elsewhere_is_kept_as_a_hand_in() {
    let (_dir, root, _e, b1) = held("done-found", "T01");
    let head = git(&root, &["rev-parse", "HEAD"]);
    let refusal = super::found(&words(&["T01"]), &root, "m", "")
        .err()
        .unwrap();
    assert!(refusal.stderr.contains("F=<feature>"));
    let f = super::found(
        &words(&["T01", "9001"]),
        &root,
        " the subject ",
        "the reason given",
    )
    .unwrap();
    assert_eq!(
        (f.tree(), f.clone_head(), f.feature()),
        (b1.as_path(), head.as_str(), "9001")
    );
    assert_eq!(f.tasks(), ["T01".to_owned()]);
    assert_eq!(
        f.command(),
        "make builder-done T=T01 F=9001 MSG='the subject'"
    );
    assert_eq!(
        f.message(),
        format!("the subject\nGUARD_EDIT_OK: the reason given\n\n{TRAILER}\n")
    );
    assert!(f.unready().unwrap().contains("nothing to commit"));
    put(&b1, "default_3.profraw", "");
    f.sweep();
    assert!(!b1.join("default_3.profraw").exists());
    put(&b1, "scripts/a.py", "x = 3\n");
    assert_eq!(f.unready(), None);
    git(&b1, &["add", "-A"]);
    git(&b1, &["commit", "-qm", "the hand-in"]);
    let sha = git(&b1, &["rev-parse", "HEAD"]);
    let said = f.kept(&sha, true);
    assert_eq!(said.code, 0);
    // 461 T08: the lane's line where the landing's stood
    assert!(
        said.stdout
            .ends_with("handed in to the lane (make lane for its place)\n"),
        "{}",
        said.stdout
    );
    assert!(!said.stdout.contains("make land F="), "{}", said.stdout);
    assert_eq!(git(&root, &["rev-parse", "refs/l7r/done/9001-T01"]), sha);
    let log = std::fs::read_to_string(root.join(".git/builder-pool.log")).unwrap();
    let done = log
        .lines()
        .map(|l| serde_json::from_str::<serde_json::Value>(l).unwrap())
        .rfind(|l| l["event"] == "done")
        .unwrap();
    assert_eq!(
        (&done["commit"], &done["handed_in"]),
        (&serde_json::json!(sha), &serde_json::json!(true))
    );
    assert!(pool_of(&root)[0].free());
}

/// 461 T44: the kind a tree's builder was briefed as is its last `brief` line's since the take, for its own holder only; none where
/// no brief names one - the hand-in's section mode is read from it, never from the builder.
#[test]
fn the_kind_is_the_tree_s_last_brief_since_its_take() {
    let (_dir, root, _e, tree) = held("done-kind", "T01");
    let kind = || {
        super::found(&words(&["T01", "9001"]), &tree, "s", "")
            .ok()
            .unwrap()
            .kind()
    };
    assert_eq!(kind(), None);
    let common = root.join(".git");
    let brief = |holder: &str, kind: &str| {
        let line =
            serde_json::json!({"event": "brief", "tree": tree, "detail": holder, "kind": kind});
        builder_tree::log_in(&common, &line);
    };
    brief("9001 T01", "fix");
    brief("9001 T01", "build-half");
    brief("9001 T09", "measurement");
    assert_eq!(kind().as_deref(), Some("build-half"));
    // a take since: the briefs before it were another hold's
    builder_tree::log_in(
        &common,
        &serde_json::json!({"event": "take", "tree": tree, "detail": "9001 T01"}),
    );
    assert_eq!(kind(), None);
}

/// 461 T11: the carried rule asked of another rev - a commit cherry-picked onto `origin/main` is held by its author's time and
/// subject, one only on a side branch is not, a missing object is in none, and no commits ask nothing.
#[test]
fn held_by_asks_the_carried_rule_of_any_rev() {
    let dir = l7r_gate_core::ci::fixtures::repo("done-held-by");
    let root = dir.path();
    git(root, &["checkout", "-qb", "side"]);
    commit(root, "a.txt", "a\n");
    let picked = git(root, &["rev-parse", "HEAD"]);
    put(root, "b.txt", "b\n");
    git(root, &["add", "-A"]);
    git(root, &["commit", "-qm", "only on the side"]);
    let side = git(root, &["rev-parse", "HEAD"]);
    git(root, &["checkout", "-q", "main"]);
    git(root, &["cherry-pick", &picked]);
    git(root, &["update-ref", "refs/remotes/origin/main", "HEAD"]);
    let missing = "0123456789abcdef0123456789abcdef01234567".to_owned();
    let short = picked.get(..10).unwrap().to_owned();
    let held = super::held_by(root, "origin/main", &[short.clone(), side, missing.clone()]);
    assert_eq!(held.into_iter().collect::<Vec<_>>(), vec![short]);
    assert!(super::held_by(root, "origin/main", &[missing]).is_empty());
    assert!(super::held_by(root, "origin/main", &[]).is_empty());
}

/// The lane's files for one ejected change of T01: its repair entry and its `eject` line.
fn ejected(root: &Path, sha: &str) {
    let lane = root.join(".git/l7r-lane");
    put(&lane, "repairs.jsonl", &format!("{{\"utc\": \"2026-11-26T12:00:00Z\", \"repair\": \"r1\", \"feature\": \"9001-x\", \"tasks\": [\"T01\"], \"kind\": \"fix\", \"ejected\": [\"{sha}\"], \"batch\": \"9001-1\", \"why\": \"red\", \"units\": [\"rust/x test\"], \"attempt\": \"/c/.git/l7r-lane/attempts/9001-1-1.log\"}}\n"));
    put(&lane, "lane.jsonl", &format!("{{\"utc\": \"2026-11-26T12:00:01Z\", \"event\": \"eject\", \"batch\": \"9001-1\", \"change\": \"{sha}\", \"repair\": \"r1\", \"why\": \"red\"}}\n"));
}

/// 461 T16 (D7, US4): an ejected change's repair entry is the next dispatch, ahead of a READY queue entry; its brief names the
/// gate's output and the change, its handout builds on the ejected commit, and its done answers the entry (`repair_of`) and
/// supersedes the ejected ref - after which no command offers it again.
#[test]
fn a_repair_entry_is_dispatched_first_briefed_with_the_gate_s_output_and_answered_by_its_done() {
    let (dir, root, mut e, b1) = held("done-repair", "T01");
    e.apply = applier(&dir, "exec git cherry-pick -n \"$5\"");
    put(&b1, "scripts/n.py", "n = 1\n");
    assert_eq!(done(&root, &e, "T01", "9001 T01: the change", "").code, 0);
    let sha = git(&root, &["rev-parse", "refs/l7r/done/9001-T01"]);
    ejected(&root, &sha);
    put(
        &root,
        "specs/9001-x/queue.txt",
        "T02 fix files=scripts/a.py\nT03 fix files=scripts/b.py\n",
    );
    // another builder's done: its step 1 names the repair before the queue's READY T03
    builder_tree::run(&words(&["take", "T02", "9001"]), &root, &e);
    put(&b1, "scripts/a.py", "a = 1\n");
    let said = done(&b1, &e, "T02", "9001 T02: two", "");
    assert_eq!(said.code, 0);
    let first = format!("  1. make builder-brief T=T01 F=9001 KIND=fix CRATE=\"rust/x\" REPAIR=r1   (9001 T01 (repair r1): the lane ejected {} from batch 9001-1 (red); the gate's output /c/.git/l7r-lane/attempts/9001-1-1.log - a FRESH builder, never one kept past its report)\n", &sha[..10]);
    assert!(said.stdout.contains(&first), "{}", said.stdout);
    let brief = |a: &[&str]| crate::builder_brief::run(&words(a), &root, &e, "");
    // a repair no open entry has, or briefed as another task's, is refused before any tree is taken
    let none = brief(&["T01", "9001", "fix", "", "", "", "", "", "", "r9"]);
    assert!(
        none.stderr
            .starts_with("builder-brief: refused - REPAIR=r9 is no open repair entry of the lane"),
        "{}",
        none.stderr
    );
    let other = brief(&["T03", "9001", "fix", "", "", "", "", "", "", "r1"]);
    assert!(other.stderr.contains("REPAIR=r1 is 9001 T01 (repair r1) of kind fix, not this brief's: brief it as filed\n  make builder-brief T=T01 F=9001 KIND=fix CRATE=\"rust/x\" REPAIR=r1\n"), "{}", other.stderr);
    assert_eq!(pool_of(&root).iter().filter(|t| !t.free()).count(), 0);
    // the repair's brief: the gate's output and the change named, the ejected commit applied in the tree uncommitted
    let r = brief(&["T01", "9001", "fix", "", "", "rust/x", "", "", "", "r1"]);
    assert_eq!(r.code, 0, "{}", r.stderr);
    let line = format!("REPAIR r1 (batch 9001-1, red): the lane ejected {}, applied in your tree uncommitted - fix it on top. Read first: the gate's output /c/.git/l7r-lane/attempts/9001-1-1.log\n", &sha[..10]);
    assert!(r.stdout.contains(&line), "{}", r.stdout);
    assert!(
        r.stderr
            .contains("builder-tree: it builds on refs/l7r/done/9001-T01"),
        "{}",
        r.stderr
    );
    // still under the prefix guard's 2,000 characters with the repair's line (the fixture's paths read as a real tree's)
    let n = r
        .stdout
        .replace(&*dir.to_string_lossy(), "/diagram/.clones")
        .chars()
        .count();
    assert!(n < 2000, "{n}");
    let tree = pool_of(&root)
        .into_iter()
        .find(|t| t.tasks == ["T01"])
        .unwrap()
        .tree;
    assert!(git(&tree, &["status", "--porcelain"]).contains("scripts/n.py"));
    // its done answers the entry and supersedes the ejected ref
    put(&tree, "scripts/n.py", "n = 2\n");
    let fixed = done(&root, &e, "T01", "9001 T01: the repair", "");
    assert_eq!(fixed.code, 0, "{}", fixed.stderr);
    let log = std::fs::read_to_string(root.join(".git/builder-pool.log")).unwrap();
    let last = log
        .lines()
        .rfind(|l| l.contains("\"event\":\"done\""))
        .unwrap();
    assert!(last.contains("\"repair_of\":\"r1\""), "{last}");
    assert_ne!(git(&root, &["rev-parse", "refs/l7r/done/9001-T01"]), sha);
    assert!(l7r_shared::builder_queue::repairs::open(&root.join(".git")).is_empty());
    assert!(!fixed.stdout.contains("REPAIR=r1"), "{}", fixed.stdout);
}

/// 461 T67 (T18's `file_ruled`): a repair entry of why `arbiter` carries the trigger as its `attempt`, which is no file - its
/// brief and its offer name the ruling's row in the clone's `specs/<spec>/arbiter.jsonl` and the batch `stop` line's two attempt
/// files instead.
#[test]
fn an_arbiter_repair_is_briefed_with_its_ruling_s_row_and_the_two_red_attempts() {
    let (dir, root, mut e, b1) = held("done-arbiter", "T01");
    e.apply = applier(&dir, "exec git cherry-pick -n \"$5\"");
    put(&b1, "scripts/n.py", "n = 1\n");
    assert_eq!(done(&root, &e, "T01", "9001 T01: the change", "").code, 0);
    let sha = git(&root, &["rev-parse", "refs/l7r/done/9001-T01"]);
    let lane = root.join(".git/l7r-lane");
    let (a1, a2) = (
        lane.join("attempts/9001-1-2.log"),
        lane.join("attempts/9001-3-1.log"),
    );
    put(&lane, "repairs.jsonl", &format!("{{\"utc\": \"2026-11-26T12:00:00Z\", \"repair\": \"r1\", \"feature\": \"9001-x\", \"tasks\": [\"T01\"], \"kind\": \"fix\", \"ejected\": [\"{sha}\"], \"batch\": \"9001-3\", \"why\": \"arbiter\", \"units\": [\"continue: fix the test\"], \"attempt\": \"ask:lane-T01\"}}\n"));
    put(&lane, "lane.jsonl", &format!("{{\"utc\": \"2026-11-26T11:00:00Z\", \"event\": \"stop\", \"batch\": \"9001-3\", \"why\": \"arbiter\", \"trigger\": \"ask:lane-T01\", \"spec\": \"9001-x\", \"tasks\": [\"T01\"], \"held\": [\"{sha}\"], \"attempts\": \"{} {}\"}}\n{{\"utc\": \"2026-11-26T12:00:01Z\", \"event\": \"eject\", \"of_batch\": \"9001-3\", \"change\": \"{sha}\", \"repair\": \"r1\", \"why\": \"arbiter\"}}\n", a1.display(), a2.display()));
    put(&root, "specs/9001-x/arbiter.jsonl", "{\"trigger\": \"ask:other\", \"ruling\": \"accept\"}\n{\"trigger\": \"ask:lane-T01\", \"ruling\": \"continue\", \"what\": \"fix the test\"}\n");
    // named from the clone, the second attempt by its file name in the first's directory
    let ruled = format!("the ruling of ask:lane-T01 and the red attempts, in {}: specs/9001-x/arbiter.jsonl line 2, .git/l7r-lane/attempts/9001-1-2.log 9001-3-1.log", root.display());
    let next = crate::builder_queue::run("builder-next", &words(&["9001"]), &root, "", 3).stdout;
    // a ruling's unit names no crate, though its last word is a step's (`test`)
    let offered = format!("make builder-brief T=T01 F=9001 KIND=fix REPAIR=r1   (9001 T01 (repair r1): the lane ejected {} from batch 9001-3 (arbiter); {ruled} - a FRESH builder", &sha[..10]);
    assert!(next.contains(&offered), "{next}");
    let r = crate::builder_brief::run(
        &words(&["T01", "9001", "fix", "", "", "", "", "", "", "r1"]),
        &root,
        &e,
        "",
    );
    assert_eq!(r.code, 0, "{}", r.stderr);
    let said = format!("REPAIR r1 (batch 9001-3, arbiter): the lane ejected {}, applied in your tree uncommitted - fix it on top. Read first: {ruled}\n", &sha[..10]);
    let out = &r.stdout;
    assert!(out.contains(&said), "{out}");
    assert!(!r.stdout.contains("output first: ask:"), "{}", r.stdout);
    // still under the prefix guard's 2,000 characters with the ruling's and the attempts' paths (read as a real tree's)
    let n = r
        .stdout
        .replace(&*dir.to_string_lossy(), "/diagram/.clones")
        .chars()
        .count();
    assert!(n < 2000, "{n}");
#[test]
fn from_phase_two_s_base_builder_trees_lists_what_waits_on_the_lane() {
    // 461 T22, plan D8: carried is asked of origin/main, where the lane lands, not of the clone's HEAD
    let (_dir, root, mut e, b1) = held("done-lane-listed", "T01");
    put(&b1, "scripts/a.py", "x = 2\n");
    assert_eq!(done(&b1, &e, "T01", "9001 T01: the lane's", "").code, 0);
    let sha = git(&root, &["rev-parse", "refs/l7r/done/9001-T01"]);
    // in the clone's HEAD but not on origin/main: carried at phase 1's base, waiting on the lane at phase 2's
    git(&root, &["cherry-pick", &sha]);
    assert!(list(&root, &e).ends_with("builder-trees: no done commit waits on its carry\n"));
    e.origin = true;
    let listed = list(&root, &e);
    assert!(listed.contains("builder-trees: commits done and not yet on origin/main, waiting on the lane (make builder-done kept each under refs/l7r/done/; make lane for where each stands): 1\n"));
    assert!(listed.ends_with(&format!(
        "  {}  9001-T01  9001 T01: the lane's\n",
        &sha[..10]
    )));
    // landed on origin/main: nothing waits
    git(&root, &["push", "-q", "origin", "main"]);
    assert!(list(&root, &e).ends_with(
        "builder-trees: no done commit waits on the lane (origin/main holds every one)\n"
    ));
}
