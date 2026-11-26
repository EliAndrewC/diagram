//! `make carry` (451 T292): a builder worktree's commit carried by one command - a both-sides-added Occasions conflict and a
//! plan-review.json conflict kept both and continued, a code conflict stopped with the pick standing, and the end verified.

use std::path::{Path, PathBuf};

use l7r_gate_core::ci::fixtures::{git, put};
use l7r_shared::tempdir::TempDir;
use serde_json::{json, Value};

use super::super::tests::has;
use super::super::unfinished::tests::{repo, TASKS};
use super::super::unfinished::{self, refusals};
use super::{cli, end, keep_both, missing, Kind, Said};

const REVIEW: &str = "specs/451-x/plan-review.json";
const TASKS_MD: &str = "specs/451-x/tasks.md";

fn with_line(line: &str) -> String {
    TASKS.replace(
        "tooling only\n",
        &format!("tooling only\n- none: {line} - tooling only\n"),
    )
}

/// A plan review record holding one more task's verdict.
fn record(task: Option<&str>) -> String {
    let mut tasks = json!({"T1": {"verdict": "CLEAR", "reviewed": "2026-11-25"}});
    if let Some(t) = task {
        tasks[t] = json!({"verdict": "CLEAR", "reviewed": "2026-11-26"});
    }
    serde_json::to_string_pretty(&json!({"tasks": tasks})).unwrap() + "\n"
}

/// A clone with a record, and a builder's linked worktree beside it.
fn trees(tag: &str) -> (TempDir, PathBuf, PathBuf) {
    let (dir, root) = repo(tag);
    put(&root, REVIEW, &record(None));
    git(&root, &["add", "-A"]);
    git(&root, &["commit", "-qm", "the record"]);
    let builder = dir.join("builder");
    git(
        &root,
        &[
            "worktree",
            "add",
            "-q",
            "-b",
            "builder",
            &builder.to_string_lossy(),
        ],
    );
    (dir, root, builder)
}

/// A commit of `files` in `tree`.
fn commit(tree: &Path, subject: &str, files: &[(&str, &str)]) {
    for (rel, text) in files {
        put(tree, rel, text);
    }
    git(tree, &["add", "-A"]);
    git(tree, &["commit", "-qm", subject]);
}

/// The carry of `from`'s HEAD into `root`: its exit, stdout and stderr.
fn carried(root: &Path, from: &Path) -> (i32, String, String) {
    let said = cli(&[from.to_string_lossy().into_owned()], root);
    (said.code, said.stdout, said.stderr)
}

#[test]
fn a_clean_carry_is_verified_and_says_so_in_one_line() {
    let (_dir, root, builder) = trees("carry-clean");
    commit(
        &builder,
        "T270: code",
        &[
            ("rust/held.rs", "fn held() {}\n"),
            (TASKS_MD, &with_line("T270")),
        ],
    );
    let (code, out, err) = carried(&root, &builder);
    assert_eq!((code, err.as_str()), (0, ""));
    assert_eq!(out.lines().count(), 1);
    has(&out, " - verified: nothing in progress, nothing unmerged, nothing staged, its 1 non-spec file(s) in HEAD\n");
    assert_eq!(git(&root, &["log", "-1", "--format=%s"]), "T270: code");
    // carried twice: already there
    let (code, out, _) = carried(&root, &builder);
    assert_eq!(code, 0);
    has(&out, "'s history - nothing to carry\n");
}

#[test]
fn an_occasions_conflict_and_a_record_conflict_keep_both_sides_and_continue() {
    // RED FIRST (2026-11-26): with `resolve_all` answering every path a stop, this carry exits 2 on `specs/451-x/tasks.md`
    // the shape of 20347702fc against be3f3a248b's parent: each side's Occasions line added after the same line, and each side's
    // verdict added to the record, whose merge driver this tree's git config does not define
    let (_dir, root, builder) = trees("carry-both");
    commit(
        &builder,
        "T269: code",
        &[
            ("rust/detect.rs", "fn detect() {}\n"),
            (TASKS_MD, &with_line("T269")),
            (REVIEW, &record(Some("T269"))),
        ],
    );
    commit(
        &root,
        "T270 landed here first",
        &[
            (TASKS_MD, &with_line("T270")),
            (REVIEW, &record(Some("T270"))),
        ],
    );
    let (code, out, err) = carried(&root, &builder);
    assert_eq!((code, err.as_str()), (0, ""), "{out}");
    has(&out, "its 1 non-spec file(s) in HEAD; both sides kept in specs/451-x/plan-review.json, specs/451-x/tasks.md\n");
    let tasks = std::fs::read_to_string(root.join(TASKS_MD)).unwrap();
    assert_eq!(
        tasks,
        TASKS.replace(
            "tooling only\n",
            "tooling only\n- none: T270 - tooling only\n- none: T269 - tooling only\n"
        )
    );
    let review: Value =
        serde_json::from_str(&std::fs::read_to_string(root.join(REVIEW)).unwrap()).unwrap();
    for t in ["T1", "T269", "T270"] {
        assert_eq!(review["tasks"][t]["verdict"], "CLEAR", "{t}");
    }
    assert!(root.join("rust/detect.rs").exists());
    assert_eq!(git(&root, &["status", "--porcelain"]), "");
    assert_eq!(git(&root, &["log", "-1", "--format=%s"]), "T269: code");
    assert!(!root.join(".git/l7r-carry").exists());
}

#[test]
fn a_code_conflict_stops_with_the_pick_standing_and_nothing_resolved() {
    let (_dir, root, builder) = trees("carry-code");
    commit(
        &builder,
        "T269: code",
        &[
            ("rust/lib.rs", "fn builder() {}\n"),
            (TASKS_MD, &with_line("T269")),
        ],
    );
    commit(
        &root,
        "the clone's own edit",
        &[
            ("rust/lib.rs", "fn clone() {}\n"),
            (TASKS_MD, &with_line("T270")),
        ],
    );
    let (code, out, err) = carried(&root, &builder);
    assert_eq!((code, out.as_str()), (2, ""));
    has(&err, "carry: STOPPED - ");
    has(&err, "a conflict this command does not resolve, in rust/lib.rs (not a tasks.md, plan.md or plan-review.json of a feature) - nothing was resolved\n");
    has(&err, "  a cherry-pick is in progress in ");
    has(
        &err,
        "resolve 2 unmerged path(s) (rust/lib.rs specs/451-x/tasks.md), `git -C ",
    );
    has(&err, "-c core.editor=true cherry-pick --continue`");
    // the pick stands, tasks.md too is left as git left it, and a landing or a second carry is refused
    assert!(root.join(".git/CHERRY_PICK_HEAD").exists());
    assert_eq!(
        git(&root, &["status", "--porcelain"]),
        "UU rust/lib.rs\nUU specs/451-x/tasks.md"
    );
    assert_eq!(refusals(&root).unwrap().len(), 1);
    let (code, _, err) = carried(&root, &builder);
    assert_eq!(code, 2);
    has(&err, "carry: refused - nothing carried; ");
    has(
        &err,
        "holds unfinished work:\n  a cherry-pick is in progress in ",
    );
}

#[test]
fn a_tasks_conflict_that_is_not_both_sides_adding_stops() {
    // both sides rewrote one task's line
    let (_dir, root, builder) = trees("carry-changed");
    commit(
        &builder,
        "b",
        &[(
            TASKS_MD,
            &TASKS.replace("T9 nine", "T9 nine, the builder's"),
        )],
    );
    commit(
        &root,
        "c",
        &[(TASKS_MD, &TASKS.replace("T9 nine", "T9 nine, the clone's"))],
    );
    let (code, _, err) = carried(&root, &builder);
    assert_eq!(code, 2);
    has(
        &err,
        "specs/451-x/tasks.md (a hunk both sides changed, not only added to)",
    );
    // each side added the file: no base to merge from
    let (_dir, root, builder) = trees("carry-added");
    commit(&builder, "b", &[("specs/452-y/tasks.md", "- [ ] T1 b\n")]);
    commit(&root, "c", &[("specs/452-y/tasks.md", "- [ ] T1 c\n")]);
    let (code, _, err) = carried(&root, &builder);
    assert_eq!(code, 2);
    has(&err, "specs/452-y/tasks.md (added or deleted by one side)");
    // a record that is not JSON on one side
    let (_dir, root, builder) = trees("carry-not-json");
    commit(&builder, "b", &[(REVIEW, "{ not json b\n")]);
    commit(&root, "c", &[(REVIEW, "{ not json c\n")]);
    let (code, _, err) = carried(&root, &builder);
    assert_eq!(code, 2);
    has(&err, "specs/451-x/plan-review.json (a side is not JSON)");
}

#[test]
fn keep_both_takes_only_list_lines_both_sides_added() {
    let hunk = |ours: &str, base: &str, theirs: &str| {
        format!("top\n<<<<<<< a\n{ours}||||||| o\n{base}=======\n{theirs}>>>>>>> b\nend\n")
    };
    let tasks = |text: &str| keep_both(text, Kind::Tasks);
    // theirs' line ours already holds is not doubled; a continuation line and a blank are list lines
    assert_eq!(
        tasks(&hunk("- a\n      verify: x\n", "", "- a\n\n- b\n")),
        Ok("top\n- a\n      verify: x\n\n- b\nend\n".to_owned())
    );
    // RED FIRST (451 T289): theirs' continuation line stays with its own list line though ours holds the same words under another
    assert_eq!(
        tasks(&hunk(
            "- [ ] T10 a\n      research: rendering\n",
            "",
            "      orphan\n- [ ] T11 b\n      research: rendering\n"
        )),
        Ok("top\n- [ ] T10 a\n      research: rendering\n      orphan\n- [ ] T11 b\n      research: rendering\nend\n".to_owned())
    );
    assert_eq!(
        tasks(&hunk("- a\n", "- old\n", "- b\n")),
        Err("a hunk both sides changed, not only added to".to_owned())
    );
    assert_eq!(
        tasks(&hunk("- a\n", "", "A paragraph.\n")),
        Err("an added line that is no list line: A paragraph.".to_owned())
    );
    // one list line with different lines under it on each side is a choice, left to a hand; blank lines apart are not
    assert_eq!(
        tasks(&hunk(
            "- a\n      verify: x\n",
            "",
            "- a\n      verify: y\n"
        )),
        Err("both sides added one list line with different lines under it: - a".to_owned())
    );
    assert_eq!(
        tasks(&hunk("- a\n\n      x\n", "", "- a\n\n      y\n")),
        Ok("top\n- a\n\n      x\n\n      y\nend\n".to_owned())
    );
    assert_eq!(tasks("no conflict\n"), Ok("no conflict\n".to_owned()));
}

#[test]
fn keep_both_takes_whole_plan_sections_both_sides_added() {
    let hunk = |ours: &str, theirs: &str| {
        format!("top\n<<<<<<< a\n{ours}||||||| o\n=======\n{theirs}>>>>>>> b\nend\n")
    };
    let plan = |text: &str| keep_both(text, Kind::Plan);
    // each side's stub whole, the lines they share kept in both; a section both hold whole is not doubled
    assert_eq!(
        plan(&hunk(
            "\n### T10 (a)\n\nsame words\n\n### T10 Approach\n\n1. same\n\n",
            "\n### T10 (a)\n\nsame words\n\n### T11 (b)\n\nsame words\n\n### T11 Approach\n\n1. same\n\n"
        )),
        Ok("top\n\n### T10 (a)\n\nsame words\n\n### T10 Approach\n\n1. same\n\n### T11 (b)\n\nsame words\n\n### T11 Approach\n\n1. same\n\nend\n".to_owned())
    );
    // one task's section written by both, differently: a choice, left to a hand
    assert_eq!(
        plan(&hunk("### T10 (a)\n\nours\n", "### T10 (a)\n\ntheirs\n")),
        Err("both sides wrote T10's section, differently".to_owned())
    );
    // prose that is no section, and a heading that names no task
    for theirs in ["A paragraph.\n", "### Notes\n", "### Tx\n"] {
        assert_eq!(
            plan(&hunk("### T10 (a)\n", theirs)),
            Err(format!(
                "an added block that is no `### T<n>` section: {}",
                theirs.trim_end()
            ))
        );
    }
    // a heading that ends at its id, and a side of blank lines only
    assert_eq!(
        plan(&hunk("### T10\n", "\n")),
        Ok("top\n### T10\n\nend\n".to_owned())
    );
}

/// A task filed in `tree` by the real `make task-add` and committed: what it printed.
fn filed(tree: &Path, title: &str) -> String {
    let said = l7r_gate_task::task_add::cli(&["451".to_owned()], tree, title);
    assert_eq!(said.code, 0, "{}", said.stderr);
    git(tree, &["add", "-A"]);
    git(tree, &["commit", "-qm", title]);
    said.stdout
}

/// RED FIRST (451 T289, 2026-11-26): two builders' trees each file a task they found with `make task-add` - two ids, by the
/// reservation both read (451 T255) - each appending its box to the end of tasks.md and its section stub to the end of plan.md, as
/// feature 451's files take them. Carried one after the other, the second conflicts in both files. On the old code the carry stopped
/// on plan.md ("not a tasks.md or plan-review.json of a feature"); with plan.md let through, the second box came out without its
/// research line, dropped as a line the first box already held.
#[test]
fn two_trees_filed_tasks_are_carried_with_both_boxes_and_both_stubs() {
    let (dir, root) = repo("carry-filed");
    commit(
        &root,
        "a plan and a quick",
        &[
            ("Makefile", "quick:\n\t@true\n"),
            (
                "specs/451-x/plan.md",
                "# Plan\n\n### T9 (nine)\n\nIts words.\n",
            ),
        ],
    );
    let trees: Vec<PathBuf> = ["one", "two"]
        .iter()
        .map(|name| {
            let tree = dir.join(name);
            git(
                &root,
                &["worktree", "add", "-q", "-b", name, &tree.to_string_lossy()],
            );
            tree
        })
        .collect();
    has(&filed(&trees[0], "the first tree's find"), "T10 filed");
    has(&filed(&trees[1], "the second tree's find"), "T11 filed");
    let (code, out, err) = carried(&root, &trees[0]);
    assert_eq!((code, err.as_str()), (0, ""), "{out}");
    let (code, out, err) = carried(&root, &trees[1]);
    assert_eq!((code, err.as_str()), (0, ""), "{out}");
    has(
        &out,
        "both sides kept in specs/451-x/plan.md, specs/451-x/tasks.md\n",
    );
    let tasks = std::fs::read_to_string(root.join(TASKS_MD)).unwrap();
    assert!(
        tasks.ends_with(
            "- [ ] T9 nine\n- [ ] T10 the first tree's find\n      research: rendering\n- [ ] T11 the second tree's find\n      research: rendering\n"
        ),
        "{tasks}"
    );
    let plan = std::fs::read_to_string(root.join("specs/451-x/plan.md")).unwrap();
    let stub = |t: &str| l7r_gate_plan::plan::template::TEMPLATE.replace("{T}", t);
    for t in ["T10", "T11"] {
        assert_eq!(plan.matches(stub(t).trim_end()).count(), 1, "{t}: {plan}");
    }
    assert!(plan.find("### T10 (").unwrap() < plan.find("### T11 (").unwrap());
    assert_eq!(plan.matches("8. **The budget.** One landing.").count(), 2);
    assert_eq!(git(&root, &["status", "--porcelain"]), "");
}

#[test]
fn another_clones_commit_is_fetched_and_one_out_of_reach_is_refused() {
    let (dir, root, _builder) = trees("carry-fetch");
    let other = dir.join("other");
    git(
        &dir,
        &[
            "clone",
            "-q",
            &root.to_string_lossy(),
            &other.to_string_lossy(),
        ],
    );
    git(&other, &["config", "user.email", "t@t"]);
    git(&other, &["config", "user.name", "t"]);
    commit(
        &other,
        "another clone's",
        &[("rust/other.rs", "fn other() {}\n")],
    );
    let (code, out, err) = carried(&root, &other);
    assert_eq!((code, err.as_str()), (0, ""), "{out}");
    assert!(root.join("rust/other.rs").exists());
    // a commit on no branch HEAD reaches: named, it cannot be fetched
    git(&other, &["checkout", "-q", "-b", "aside", "HEAD~1"]);
    commit(&other, "aside", &[("rust/aside.rs", "fn aside() {}\n")]);
    let aside = git(&other, &["rev-parse", "HEAD"]);
    git(&other, &["checkout", "-q", "main"]);
    let said = cli(&[other.to_string_lossy().into_owned(), aside], &root);
    assert_eq!(said.code, 2);
    has(&said.stderr, "so it cannot be fetched from there\n");
}

#[test]
fn a_pick_that_cannot_start_or_continue_is_stopped_with_gits_words() {
    // an uncommitted edit of the clone's in the pick's way: git refuses to start, nothing is in progress
    let (_dir, root, builder) = trees("carry-in-the-way");
    commit(&builder, "b", &[("rust/lib.rs", "fn builder() {}\n")]);
    put(&root, "rust/lib.rs", "fn half_done() {}\n");
    let (code, _, err) = carried(&root, &builder);
    assert_eq!(code, 2);
    has(&err, "carry: STOPPED - ");
    has(&err, "git cherry-pick said: error: ");
    assert!(!root.join(".git/CHERRY_PICK_HEAD").exists());
    // a continue the tree's commit hook refuses: the conflicts resolved and staged, the pick standing
    let (_dir, root, builder) = trees("carry-hook");
    commit(&builder, "b", &[(TASKS_MD, &with_line("T269"))]);
    commit(&root, "c", &[(TASKS_MD, &with_line("T270"))]);
    std::fs::create_dir_all(root.join(".git/hooks")).unwrap();
    l7r_gate_core::write_executable(
        &root.join(".git/hooks/pre-commit"),
        "#!/bin/sh\necho the hook says no >&2\nexit 1\n",
    );
    let (code, _, err) = carried(&root, &builder);
    assert_eq!(code, 2);
    has(&err, "its continue failed: the hook says no");
    has(
        &err,
        "(CHERRY_PICK_HEAD, 1 staged path(s) uncommitted) - finish it: `git -C ",
    );
}

#[test]
fn the_end_refuses_a_carry_whose_files_head_does_not_hold() {
    let (_dir, root, builder) = trees("carry-end");
    commit(
        &builder,
        "b",
        &[
            ("rust/held.rs", "fn held() {}\n"),
            (TASKS_MD, &with_line("T270")),
        ],
    );
    let sha = git(&builder, &["rev-parse", "HEAD"]);
    let head = git(&root, &["rev-parse", "HEAD"]);
    // T270's landing: the commit's code not in HEAD, nothing moved since `before`
    assert_eq!(
        missing(&root, &sha, &head),
        Ok((1, vec!["rust/held.rs".to_owned()]))
    );
    let mut said = Said {
        out: String::new(),
        err: String::new(),
    };
    assert_eq!(end(&root, &sha, &head, &[], &mut said), Ok(1));
    has(&said.err, "carry: NOT VERIFIED - ");
    has(
        &said.err,
        "HEAD does not hold the carried commit's rust/held.rs\n",
    );
    // the same content already committed here under another commit: held, though the carry moved nothing
    commit(&root, "by hand", &[("rust/held.rs", "fn held() {}\n")]);
    let head = git(&root, &["rev-parse", "HEAD"]);
    assert_eq!(missing(&root, &sha, &head), Ok((1, Vec::new())));
}

#[test]
fn the_arguments_are_checked() {
    let (dir, root, builder) = trees("carry-args");
    for args in [
        vec![],
        vec![String::new()],
        vec!["a".to_owned(), "b".to_owned(), "c".to_owned()],
    ] {
        let said = cli(&args, &root);
        assert_eq!(said.code, 2);
        assert!(said
            .stderr
            .starts_with("usage: l7r-gate land --carry <tree> [<commit>]"));
    }
    let said = cli(
        &[builder.to_string_lossy().into_owned(), "no-such".to_owned()],
        &root,
    );
    assert_eq!(said.code, 2);
    has(&said.stderr, "holds no commit no-such\nusage: ");
    // run where there is no git tree
    let said = cli(&[builder.to_string_lossy().into_owned()], &dir);
    assert_eq!(said.code, 2);
    has(&said.stderr, "carry: ");
    has(&said.stderr, "is no git tree");
    let _ = unfinished::git(&root, &["status"]);
}
