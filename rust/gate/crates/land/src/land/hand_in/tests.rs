//! The hand-in's apply (461 T07, plan D3 steps 1-3, 5, 6), on scratch clones with a pool tree held as a handout leaves it: the work
//! applied onto the clone's HEAD and landed there as one commit; a conflict with the base refused naming its files and resumed after
//! the builder's resolution, the paths a rule resolves resolved at the resume; a first-pass refusal committing nothing, its rules'
//! list read back at the resume; and each way it refuses with nothing done.

use std::path::{Path, PathBuf};

use l7r_gate_core::ci::fixtures::{git, put};
use l7r_gate_core::{write_executable, Reply};
use l7r_shared::builder_pool;
use l7r_shared::tempdir::TempDir;
use serde_json::Value;

use super::super::tests::has;
use super::super::unfinished::tests::{repo, TASKS};
use super::{io, must, none as clear, run, FirstPass};

const TASKS_MD: &str = "specs/451-x/tasks.md";
const SCRATCH: &str = "refs/l7r/hand-in/9001-T01";
const DONE: &str = "refs/l7r/done/9001-T01";

fn with_line(line: &str) -> String {
    TASKS.replace(
        "tooling only\n",
        &format!("tooling only\n- none: {line} - tooling only\n"),
    )
}

/// A clone and a pool tree beside it, detached at the clone's HEAD and held by 9001 T01, as a handout leaves it.
fn pool(tag: &str) -> (TempDir, PathBuf, PathBuf) {
    let (dir, root) = repo(tag);
    let tree = dir.join("t01");
    git(
        &root,
        &["worktree", "add", "-q", "--detach", &tree.to_string_lossy()],
    );
    let held = builder_pool::Tree {
        tree: tree.clone(),
        feature: "9001".to_owned(),
        tasks: vec!["T01".to_owned()],
        since: String::new(),
    };
    builder_pool::write(&root.join(".git"), &[held]).unwrap();
    (dir, root, tree)
}

/// A commit of `files` in `tree`.
fn commit(tree: &Path, subject: &str, files: &[(&str, &str)]) {
    for (rel, text) in files {
        put(tree, rel, text);
    }
    git(tree, &["add", "-A"]);
    git(tree, &["commit", "-qm", subject]);
}

/// The tree brought to the clone's HEAD, as a handout brings it.
fn handed_out(root: &Path, tree: &Path) {
    let head = git(root, &["rev-parse", "HEAD"]);
    git(tree, &["checkout", "-q", "--detach", &head]);
}

/// `make builder-done T=T01 F=9001` as a hand-in, run in the tree, the base by `knob`.
fn handed(tree: &Path, knob: &str, first: FirstPass) -> Reply {
    let args = ["T01".to_owned(), "9001".to_owned()];
    run(&args, tree, "9001 T01: the work", "", knob, first)
}

/// Whether the clone holds `name`.
fn holds(root: &Path, name: &str) -> bool {
    !git(root, &["for-each-ref", "--format=%(refname)", name]).is_empty()
}

/// The tree's own hand-in files.
fn files(tree: &Path) -> PathBuf {
    PathBuf::from(git(tree, &["rev-parse", "--absolute-git-dir"])).join("l7r-hand-in")
}

fn held(root: &Path) -> bool {
    !builder_pool::read(&root.join(".git"))[0].free()
}

/// The done commit: its parent and the files it changes.
fn done(root: &Path) -> (String, String) {
    let parent = git(root, &["rev-parse", &format!("{DONE}^")]);
    let names = git(root, &["show", "--name-only", "--format=", DONE]);
    (parent, names)
}

/// A hand-in that ended with its commit: exit 0, nothing on stderr.
fn landed(said: &Reply) {
    let got = (said.code, said.stderr.as_str());
    assert_eq!(got, (0, ""), "{}", said.stdout);
}

/// Every refusal with nothing committed: no done ref, the tree still held.
fn nothing_done(root: &Path, said: &Reply, code: i32, why: &str) {
    assert_eq!((said.code, said.stdout.as_str()), (code, ""));
    has(&said.stderr, why);
    assert!(!holds(root, DONE));
    assert!(held(root));
}

#[test]
fn a_hand_in_applies_the_work_onto_the_clone_s_head_and_lands_one_commit_there() {
    let (_dir, root, tree) = pool("hand-in-clean");
    // the clone moves on after the handout: the hand-in lands on where work lands now, not on the tree's old base
    commit(&root, "later", &[("rust/later.rs", "fn later() {}\n")]);
    let head = git(&root, &["rev-parse", "HEAD"]);
    put(&tree, "rust/held.rs", "fn held() {}\n");
    let said = handed(&tree, "", &clear);
    landed(&said);
    has(&said.stdout, "hand-in: the work applied onto ");
    has(&said.stdout, " committed as ");
    assert_eq!(done(&root), (head.clone(), "rust/held.rs".to_owned()));
    let subject = git(&root, &["log", "-1", "--format=%s", DONE]);
    assert_eq!(subject, "9001 T01: the work");
    // the scratch ref and the tree's files gone, the clone untouched, the tree free at the clone's HEAD
    assert!(!holds(&root, SCRATCH));
    assert!(!files(&tree).join("9001-T01.base").exists());
    assert_eq!(git(&root, &["rev-parse", "HEAD"]), head);
    assert!(!held(&root));
    assert_eq!(git(&tree, &["rev-parse", "HEAD"]), head);
    let log = std::fs::read_to_string(root.join(".git/builder-pool.log")).unwrap();
    let line = log
        .lines()
        .map(|l| serde_json::from_str::<Value>(l).unwrap())
        .rfind(|l| l["event"] == "done")
        .unwrap();
    assert_eq!(line["handed_in"], Value::Bool(true));
}

#[test]
fn a_hand_in_that_conflicts_with_its_base_is_refused_naming_the_files_and_resumes_after_resolution()
{
    let (_dir, root, tree) = pool("hand-in-conflict");
    commit(
        &root,
        "the clone's",
        &[
            ("rust/lib.rs", "fn clone() {}\n"),
            (TASKS_MD, &with_line("T02")),
        ],
    );
    let head = git(&root, &["rev-parse", "HEAD"]);
    put(&tree, "rust/lib.rs", "fn builder() {}\n");
    put(&tree, TASKS_MD, &with_line("T01"));
    let said = handed(&tree, "", &clear);
    nothing_done(&root, &said, 2, "hand-in: STOPPED - nothing committed: ");
    has(&said.stderr, "rust/lib.rs (a line that is not prose");
    has(
        &said.stderr,
        "specs/451-x/tasks.md (its rule would resolve it; left with the rest)",
    );
    has(
        &said.stderr,
        "make builder-done T=T01 F=9001 MSG='9001 T01: the work'",
    );
    // the tree is left on the base with the conflict, the work kept at the scratch ref
    assert!(holds(&root, SCRATCH));
    assert_eq!(git(&tree, &["rev-parse", "HEAD"]), head);
    // run again unresolved: only the path no rule resolves is named
    let again = handed(&tree, "", &clear);
    nothing_done(&root, &again, 2, "rust/lib.rs (a line that is not prose");
    assert!(!again.stderr.contains("tasks.md ("));
    // resolved by hand: the resume resolves tasks.md by its rule and lands one commit on the base
    put(&tree, "rust/lib.rs", "fn both() {}\n");
    git(&tree, &["add", "--", "rust/lib.rs"]);
    // a file written while resolving and never added is committed too: everything is staged first (T05)
    put(&tree, "rust/extra.rs", "fn extra() {}\n");
    let resumed = handed(&tree, "", &clear);
    landed(&resumed);
    let (parent, names) = done(&root);
    assert_eq!(
        (parent, names.as_str()),
        (head, "rust/extra.rs\nrust/lib.rs\nspecs/451-x/tasks.md")
    );
    let tasks = git(&root, &["show", &format!("{DONE}:{TASKS_MD}")]);
    assert!(tasks.contains("T01 - tooling") && tasks.contains("T02 - tooling"));
    assert!(!holds(&root, SCRATCH));
    assert!(!files(&tree).join("9001-T01.resolved").exists());
}

#[test]
fn a_first_pass_refusal_commits_nothing_and_the_resume_reads_the_rules_resolved_list() {
    let (_dir, root, tree) = pool("hand-in-first-pass");
    commit(&root, "a page", &[("docs/a.md", "one two three\n")]);
    handed_out(&root, &tree);
    commit(
        &root,
        "the clone's word",
        &[("docs/a.md", "ONE two three\n")],
    );
    put(&tree, "docs/a.md", "one two THREE\n");
    let owed = |_: &Path| vec!["the plan review is owed: make plan-review T=T01 F=9001".to_owned()];
    let said = handed(&tree, "", &owed);
    nothing_done(
        &root,
        &said,
        2,
        "hand-in: refused by the first pass - nothing committed, the work applied onto ",
    );
    has(
        &said.stderr,
        "\n  the plan review is owed: make plan-review T=T01 F=9001\n",
    );
    let resolved = std::fs::read_to_string(files(&tree).join("9001-T01.resolved")).unwrap();
    assert!(resolved.starts_with("docs/a.md ("), "{resolved}");
    assert!(holds(&root, SCRATCH));
    let resumed = handed(&tree, "", &clear);
    landed(&resumed);
    assert_eq!(
        git(&root, &["show", &format!("{DONE}:docs/a.md")]),
        "ONE two THREE"
    );
    assert!(!files(&tree).join("9001-T01.resolved").exists());
}

#[test]
fn a_resolution_that_drops_the_work_is_not_verified() {
    let (_dir, root, tree) = pool("hand-in-dropped");
    commit(&root, "the clone's", &[("rust/lib.rs", "fn clone() {}\n")]);
    put(&tree, "rust/lib.rs", "fn builder() {}\n");
    nothing_done(&root, &handed(&tree, "", &clear), 2, "STOPPED");
    // "resolved" by taking the base's side: the work is gone from the tree
    put(&tree, "rust/lib.rs", "fn clone() {}\n");
    git(&tree, &["add", "--", "rust/lib.rs"]);
    let said = handed(&tree, "", &clear);
    nothing_done(
        &root,
        &said,
        1,
        "hand-in: NOT VERIFIED - nothing committed: ",
    );
    has(
        &said.stderr,
        "the working tree does not hold the applied commit's rust/lib.rs",
    );
}

#[test]
fn a_file_a_rule_resolved_back_to_the_base_s_text_stays_resolved_past_a_failed_end() {
    // 461 T39 (built inside T07): docs/a.md's words rule merges it to the clone's own text, which the working tree then holds -
    // unchanged against HEAD and not at the scratch commit's blob - so only the `.resolved` list tells it from a file missing
    let (_dir, root, tree) = pool("hand-in-ruled-past-not-verified");
    commit(&root, "a page", &[("docs/a.md", "one two three\n")]);
    handed_out(&root, &tree);
    commit(
        &root,
        "the clone's",
        &[
            ("docs/a.md", "ONE TWO three\n"),
            ("rust/lib.rs", "fn clone() {}\n"),
        ],
    );
    put(&tree, "docs/a.md", "ONE two three\n");
    put(&tree, "rust/lib.rs", "fn builder() {}\n");
    nothing_done(&root, &handed(&tree, "", &clear), 2, "STOPPED");
    // resolved by taking the base's side: the resume resolves docs/a.md by its rule, then its end fails on lib.rs
    put(&tree, "rust/lib.rs", "fn clone() {}\n");
    git(&tree, &["add", "--", "rust/lib.rs"]);
    let dropped = handed(&tree, "", &clear);
    nothing_done(&root, &dropped, 1, "NOT VERIFIED");
    let resolved =
        std::fs::read_to_string(files(&tree).join("9001-T01.resolved")).unwrap_or_default();
    assert!(resolved.starts_with("docs/a.md ("), "{resolved}");
    // mended: the third run lands, docs/a.md held by its rule though the base's text
    put(&tree, "rust/lib.rs", "fn both() {}\n");
    git(&tree, &["add", "--", "rust/lib.rs"]);
    let mended = handed(&tree, "", &clear);
    landed(&mended);
    assert_eq!(done(&root).1, "rust/lib.rs");
}

/// A hook of the clone's that acts once, while `flag` stands in the common git directory, then removes it.
fn hook(root: &Path, name: &str, flag: &str, act: &str) {
    let body = format!("#!/bin/sh\nf=\"$(git rev-parse --git-common-dir)/{flag}\"\n[ -f \"$f\" ] || exit 0\nrm -f \"$f\"\n{act}\n");
    std::fs::create_dir_all(root.join(".git/hooks")).unwrap();
    write_executable(&root.join(".git/hooks").join(name), &body);
}

#[test]
fn a_scratch_commit_git_refuses_leaves_the_work_uncommitted() {
    let (_dir, root, tree) = pool("hand-in-scratch-refused");
    hook(
        &root,
        "pre-commit",
        "no-commit",
        "echo refused by the hook >&2; exit 1",
    );
    std::fs::write(root.join(".git/no-commit"), "").unwrap();
    put(&tree, "rust/held.rs", "fn held() {}\n");
    let said = handed(&tree, "", &clear);
    nothing_done(&root, &said, 1, "hand-in: git commit failed in ");
    has(&said.stderr, "refused by the hook");
    assert!(!holds(&root, SCRATCH));
    assert_eq!(git(&tree, &["status", "--porcelain"]), "?? rust/held.rs");
}

#[test]
fn a_hand_in_commit_git_refuses_is_said_and_the_next_run_resumes() {
    let (_dir, root, tree) = pool("hand-in-commit-refused");
    hook(
        &root,
        "pre-commit",
        "no-commit",
        "echo refused by the hook >&2; exit 1",
    );
    put(&tree, "rust/held.rs", "fn held() {}\n");
    let flag = root.join(".git/no-commit");
    // the first pass is the last step before the commit: it arms the hook
    let arm = |_: &Path| {
        std::fs::write(&flag, "").unwrap();
        Vec::new()
    };
    let said = handed(&tree, "", &arm);
    nothing_done(&root, &said, 1, "hand-in: git commit failed in ");
    has(
        &said.stderr,
        "the work stands applied, uncommitted; run it again",
    );
    assert!(holds(&root, SCRATCH));
    let resumed = handed(&tree, "", &clear);
    landed(&resumed);
    assert_eq!(done(&root).1, "rust/held.rs");
}

#[test]
fn an_apply_refused_puts_the_work_back_uncommitted() {
    let (_dir, root, tree) = pool("hand-in-apply-refused");
    // a checkout hook that stages a file once: the apply then finds staged work and refuses before applying anything
    hook(
        &root,
        "post-checkout",
        "stage",
        "echo x > stray.txt && git add stray.txt",
    );
    std::fs::write(root.join(".git/stage"), "").unwrap();
    put(&tree, "rust/held.rs", "fn held() {}\n");
    let said = handed(&tree, "", &clear);
    nothing_done(&root, &said, 2, "hand-in: refused - nothing applied: ");
    has(&said.stderr, "the work is back in the tree uncommitted");
    assert!(!holds(&root, SCRATCH));
    let status = git(&tree, &["status", "--porcelain"]);
    assert!(status.contains("?? rust/held.rs"), "{status}");
}

#[test]
fn a_base_already_holding_the_work_hands_nothing_in() {
    let (_dir, root, tree) = pool("hand-in-empty");
    commit(&root, "the same", &[("rust/held.rs", "fn held() {}\n")]);
    put(&tree, "rust/held.rs", "fn held() {}\n");
    let said = handed(&tree, "", &clear);
    nothing_done(&root, &said, 2, "hand-in: nothing to hand in - the base ");
    has(&said.stderr, "make builder-tree-release T=T01 F=9001");
    assert!(!holds(&root, SCRATCH));
}

#[test]
fn a_scratch_ref_this_tree_did_not_leave_is_refused() {
    let (_dir, root, tree) = pool("hand-in-stale");
    let head = git(&root, &["rev-parse", "HEAD"]);
    git(&root, &["update-ref", SCRATCH, &head]);
    put(&tree, "rust/held.rs", "fn held() {}\n");
    let said = handed(&tree, "", &clear);
    nothing_done(
        &root,
        &said,
        2,
        "hand-in: refused - nothing done: refs/l7r/hand-in/9001-T01 stands",
    );
    has(&said.stderr, "git update-ref -d refs/l7r/hand-in/9001-T01");
}

#[test]
fn the_base_is_origin_main_after_a_fetch_where_the_knob_says_origin() {
    let (dir, root, tree) = pool("hand-in-origin");
    let origin = dir.join("origin.git");
    git(
        &root,
        &["clone", "-q", "--bare", ".", &origin.to_string_lossy()],
    );
    git(
        &root,
        &["remote", "add", "origin", &origin.to_string_lossy()],
    );
    commit(&root, "pushed", &[("rust/pushed.rs", "fn pushed() {}\n")]);
    git(&root, &["push", "-q", "origin", "HEAD:main"]);
    let main = git(&root, &["rev-parse", "HEAD"]);
    commit(
        &root,
        "staged in the clone",
        &[("rust/staged.rs", "fn staged() {}\n")],
    );
    put(&tree, "rust/held.rs", "fn held() {}\n");
    let said = handed(&tree, "origin", &clear);
    landed(&said);
    assert_eq!(done(&root), (main, "rust/held.rs".to_owned()));
}

#[test]
fn a_fetch_that_fails_refuses_with_nothing_done() {
    let (_dir, root, tree) = pool("hand-in-no-origin");
    put(&tree, "rust/held.rs", "fn held() {}\n");
    let said = handed(&tree, "origin", &clear);
    nothing_done(
        &root,
        &said,
        2,
        "hand-in: refused - nothing done: git fetch origin failed in ",
    );
    assert!(!holds(&root, SCRATCH));
    assert_eq!(git(&tree, &["status", "--porcelain"]), "?? rust/held.rs");
}

#[test]
fn a_git_step_that_fails_is_said_with_nothing_done() {
    // `handed()`'s Err path: an origin that fetches but holds no main, so `git rev-parse origin/main` fails before the scratch commit
    let (dir, root, tree) = pool("hand-in-no-main");
    let origin = dir.join("origin.git");
    git(
        &root,
        &["clone", "-q", "--bare", ".", &origin.to_string_lossy()],
    );
    git(&origin, &["branch", "-m", "main", "trunk"]);
    git(
        &root,
        &["remote", "add", "origin", &origin.to_string_lossy()],
    );
    put(&tree, "rust/held.rs", "fn held() {}\n");
    let said = handed(&tree, "origin", &clear);
    nothing_done(
        &root,
        &said,
        2,
        "hand-in: git rev-parse origin/main failed in ",
    );
    assert!(!holds(&root, SCRATCH));
    assert_eq!(git(&tree, &["status", "--porcelain"]), "?? rust/held.rs");
}

#[test]
fn a_git_step_that_fails_after_the_scratch_commit_puts_the_work_back_uncommitted() {
    // a reference-transaction hook vetoes the scratch ref: without the undo the scratch commit stood on the tree's HEAD with no
    // ref, and the next run found nothing to commit
    let (_dir, root, tree) = pool("hand-in-ref-vetoed");
    let veto = "#!/bin/sh\n[ \"$1\" = prepared ] || exit 0\ngrep -q refs/l7r/hand-in/ || exit 0\necho vetoed >&2\nexit 1\n";
    let at = root.join(".git/hooks/reference-transaction");
    std::fs::create_dir_all(root.join(".git/hooks")).unwrap();
    write_executable(&at, veto);
    let old = git(&tree, &["rev-parse", "HEAD"]);
    put(&tree, "rust/held.rs", "fn held() {}\n");
    let said = handed(&tree, "", &clear);
    nothing_done(
        &root,
        &said,
        2,
        "hand-in: git update-ref refs/l7r/hand-in/9001-T01 ",
    );
    has(&said.stderr, "the work is back in the tree uncommitted");
    assert_eq!(git(&tree, &["rev-parse", "HEAD"]), old);
    assert_eq!(git(&tree, &["status", "--porcelain"]), "?? rust/held.rs");
    assert!(!files(&tree).exists());
    std::fs::remove_file(&at).unwrap();
    landed(&handed(&tree, "", &clear));
    assert_eq!(done(&root).1, "rust/held.rs");
}

#[test]
fn the_knob_the_arguments_and_today_s_refusals_are_asked_first() {
    let (_dir, root, tree) = pool("hand-in-asked");
    put(&tree, "rust/held.rs", "fn held() {}\n");
    let knob = handed(&tree, "elsewhere", &clear);
    nothing_done(
        &root,
        &knob,
        2,
        "HAND_IN_BASE is clone (the clone's HEAD, phase 1) or origin",
    );
    // the arm in land.rs: the arguments checked as make builder-done checks them
    let usage = super::super::cli(&["--hand-in".to_owned()], &tree);
    nothing_done(
        &root,
        &usage,
        2,
        "usage: make builder-done T=<task(s)> F=<n> MSG=",
    );
    // today's refusals (builder_done::unready): a guard file with no GUARD=
    put(&tree, "Makefile", "all:\n");
    let guard = handed(&tree, "", &clear);
    nothing_done(
        &root,
        &guard,
        2,
        "builder-done: refused - nothing done: the commit changes a guard file (Makefile)",
    );
    assert!(!holds(&root, SCRATCH));
}

#[test]
fn a_git_step_that_cannot_fail_says_so_where_it_does() {
    let (_dir, _root, tree) = pool("hand-in-must");
    assert_eq!(
        must(&tree, &["rev-parse", "--is-inside-work-tree"]),
        Ok("true".to_owned())
    );
    let why = must(&tree, &["rev-parse", "--verify", "-q", "no-such-ref"]).unwrap_err();
    has(&why, "git rev-parse --verify -q no-such-ref failed in ");
}

#[test]
fn a_resolution_added_with_its_markers_standing_is_refused() {
    let (_dir, root, tree) = pool("hand-in-markers");
    commit(&root, "the clone's", &[("rust/lib.rs", "fn clone() {}\n")]);
    put(&tree, "rust/lib.rs", "fn builder() {}\n");
    nothing_done(&root, &handed(&tree, "", &clear), 2, "STOPPED");
    // added as git left it, the markers in
    git(&tree, &["add", "--", "rust/lib.rs"]);
    let said = handed(&tree, "", &clear);
    let why = "hand-in: refused - nothing committed: a conflict's markers stand in rust/lib.rs of ";
    nothing_done(&root, &said, 2, why);
    assert!(holds(&root, SCRATCH));
}

#[test]
fn the_records_a_clear_first_pass_writes_are_committed_with_the_work() {
    // D4: the first pass writes its records into the tree uncommitted, so the hand-in's commit carries them with the work
    let (_dir, root, tree) = pool("hand-in-records");
    put(&tree, "rust/held.rs", "fn held() {}\n");
    let records = |at: &Path| {
        put(at, "dev/review-ledger.md", "a row\n");
        Vec::new()
    };
    landed(&handed(&tree, "", &records));
    assert_eq!(done(&root).1, "dev/review-ledger.md\nrust/held.rs");
    assert_eq!(git(&tree, &["status", "--porcelain"]), "");
}

#[test]
fn a_file_step_that_fails_is_said_as_its_error() {
    // the hand-in's own files are written under the tree's git directory; a write under a file, not a directory, fails
    let (_dir, _root, tree) = pool("hand-in-io");
    let under = tree.join("rust-file");
    std::fs::write(&under, "").unwrap();
    assert_eq!(io(std::fs::write(&under, "x")), Ok(()));
    let why = io(std::fs::write(under.join("base"), "x")).unwrap_err();
    has(&why, "Not a directory");
}
