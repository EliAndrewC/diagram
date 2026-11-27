//! The carry's no-commit form (461 T05, plan D3): a commit applied onto HEAD with the carry's rules and left uncommitted, ending
//! verified on its own end - nothing in progress, nothing unmerged, the commit's non-spec files in the working tree - where the carry's
//! own end asks "nothing staged", which a no-commit apply contradicts by design.

use std::fmt::Write as _;
use std::path::Path;

use super::super::super::tests::has;
use super::super::apply::{apply, verified, Applied};
use super::super::Form;
use super::{cli, commit, git, record, trees, with_line, REVIEW, TASKS_MD};

/// The no-commit apply of `from`'s HEAD onto `root` through the command line: its exit, stdout and stderr.
fn applied(root: &Path, from: &Path) -> (i32, String, String) {
    let words = [
        "--no-commit".to_owned(),
        from.to_string_lossy().into_owned(),
    ];
    let said = cli(&words, root);
    (said.code, said.stdout, said.stderr)
}

fn head(tree: &Path) -> String {
    git(tree, &["rev-parse", "HEAD"])
}

#[test]
fn a_clean_apply_is_left_staged_uncommitted_and_verified() {
    // RED FIRST (461 T05): with the carry's own end (every refusal, "nothing staged" among them) this apply is NotVerified on
    // `rust/held.rs` standing staged - the contradiction D3 names; 5 of the form's 8 tests red so, 2026-11-27
    let (_dir, root, builder) = trees("apply-clean");
    commit(
        &root,
        "the clone's own",
        &[("rust/own.rs", "fn own() {}\n")],
    );
    commit(
        &builder,
        "T05: code",
        &[
            ("rust/held.rs", "fn held() {}\n"),
            (TASKS_MD, &with_line("T05")),
        ],
    );
    let base = head(&root);
    let (code, out, err) = applied(&root, &builder);
    assert_eq!((code, err.as_str()), (0, ""), "{out}");
    has(&out, "applied onto ");
    has(&out, "'s HEAD, uncommitted (the no-commit form) - verified: nothing in progress, nothing unmerged, its 1 non-spec file(s) in the working tree\n");
    assert_eq!(head(&root), base);
    assert_eq!(
        git(&root, &["status", "--porcelain"]),
        "A  rust/held.rs\nM  specs/451-x/tasks.md"
    );
    // nothing stands to continue or skip: a -n pick writes no marker
    assert!(!root.join(".git/CHERRY_PICK_HEAD").exists());
    let sha = head(&builder);
    assert_eq!(verified(&root, &sha, &[]), Ok(Ok(1)));
}

#[test]
fn a_commit_the_clone_holds_is_applied_by_its_sha_alone_and_its_done_ref_kept() {
    // the command's door for a caller below the land crate (461 T09's handout in the task crate, which cannot call `apply` in
    // process): `land --carry --no-commit "" <sha>`, the commit a done ref keeps, never spent here - the successor's hand-in
    // supersedes it (D14)
    let (_dir, root, builder) = trees("apply-sha");
    commit(&builder, "T05: code", &[("rust/held.rs", "fn held() {}\n")]);
    let sha = head(&builder);
    let kept = "refs/l7r/done/451-T05";
    git(&root, &["update-ref", kept, &sha]);
    let base = head(&root);
    let said = cli(
        &["--no-commit".to_owned(), String::new(), sha.clone()],
        &root,
    );
    assert_eq!(
        (said.code, said.stderr.as_str()),
        (0, ""),
        "{}",
        said.stdout
    );
    has(
        &said.stdout,
        "uncommitted (the no-commit form) - verified: ",
    );
    assert_eq!(head(&root), base);
    assert_eq!(git(&root, &["rev-parse", kept]), sha);
}

#[test]
fn a_file_the_commit_deletes_is_held_where_the_working_tree_lacks_it() {
    let (_dir, root, builder) = trees("apply-delete");
    git(&builder, &["rm", "-q", "rust/lib.rs"]);
    git(&builder, &["commit", "-qm", "T05: lib.rs gone"]);
    let sha = head(&builder);
    assert_eq!(
        apply(&root, &sha),
        Ok(Applied::Verified {
            files: 1,
            resolved: Vec::new()
        })
    );
    assert!(!root.join("rust/lib.rs").exists());
    // the base already lacks the file the commit deletes: the pick leaves it unchanged against HEAD, so it is held by its content -
    // absent in the working tree as in the commit, `rev-parse -q --verify <sha>:<path>` answering `(1, "")` as the form's own reading
    let (_dir, root, builder) = trees("apply-delete-gone");
    git(&builder, &["rm", "-q", "rust/lib.rs"]);
    commit(
        &builder,
        "T05: lib.rs gone",
        &[("rust/held.rs", "fn held() {}\n")],
    );
    git(&root, &["rm", "-q", "rust/lib.rs"]);
    git(&root, &["commit", "-qm", "gone here first"]);
    let sha = head(&builder);
    assert_eq!(
        apply(&root, &sha),
        Ok(Applied::Verified {
            files: 2,
            resolved: Vec::new()
        })
    );
}

#[test]
fn an_empty_apply_verifies_with_nothing_staged() {
    // every change already in HEAD: a -n pick exits 0, stages nothing and leaves nothing standing
    let (_dir, root, builder) = trees("apply-empty");
    commit(&builder, "T05: code", &[("rust/held.rs", "fn held() {}\n")]);
    commit(
        &root,
        "the same, by hand",
        &[("rust/held.rs", "fn held() {}\n")],
    );
    let sha = head(&builder);
    assert_eq!(
        apply(&root, &sha),
        Ok(Applied::Verified {
            files: 1,
            resolved: Vec::new()
        })
    );
    assert_eq!(git(&root, &["status", "--porcelain"]), "");
}

#[test]
fn the_carry_s_rules_resolve_a_no_commit_apply_s_conflicts() {
    // the shape of the carry's own test: each side's Occasions line after the same line, and each side's verdict in the record
    let (_dir, root, builder) = trees("apply-rules");
    commit(
        &builder,
        "T05: code",
        &[
            ("rust/detect.rs", "fn detect() {}\n"),
            (TASKS_MD, &with_line("T05")),
            (REVIEW, &record(Some("T05"))),
        ],
    );
    commit(
        &root,
        "T06 here first",
        &[
            (TASKS_MD, &with_line("T06")),
            (REVIEW, &record(Some("T06"))),
        ],
    );
    let (code, out, err) = applied(&root, &builder);
    assert_eq!((code, err.as_str()), (0, ""), "{out}");
    has(&out, "in the working tree; resolved specs/451-x/plan-review.json (the record's merge), specs/451-x/tasks.md (both sides' list lines)\n");
    assert_eq!(
        git(&root, &["status", "--porcelain"]),
        "A  rust/detect.rs\nM  specs/451-x/plan-review.json\nM  specs/451-x/tasks.md"
    );
    assert_eq!(git(&root, &["log", "-1", "--format=%s"]), "T06 here first");
}

/// A tasks.md of the open boxes named, each with its research line unless listed in `bare`.
fn boxes(ids: &[&str], bare: &[&str]) -> String {
    let mut out = "# Tasks\n\n".to_owned();
    for id in ids {
        let _ = writeln!(out, "- [ ] T{id} a task");
        if !bare.contains(id) {
            out += "      research: rendering\n";
        }
    }
    out
}

#[test]
fn a_tasks_md_git_merged_cleanly_beside_a_conflict_takes_its_boxes_lines_from_the_applied_commit() {
    // RED FIRST (461 T05, 2026-11-27): while `resolve_all` read the applied side as `CHERRY_PICK_HEAD`, which a -n pick never writes,
    // `git show CHERRY_PICK_HEAD:<path>` failed and its error text was handed in as a side, so T2 stayed bare. The shape of the
    // carry's own test of it: the plan conflicts (resolved by section), the tasks merge cleanly, the clone's T2 bare
    let plan = "specs/451-x/plan.md";
    let stubs = |ids: &[&str]| {
        let mut out = "# Plan\n\n## Task sections\n\n".to_owned();
        for id in ids {
            let _ = write!(out, "### T{id} (task {id}'s title)\n\nstub {id}\n\n");
        }
        out
    };
    let (_dir, root, builder) = trees("apply-boxes");
    commit(
        &root,
        "the spec",
        &[
            (TASKS_MD, &boxes(&["1", "2", "9"], &[])),
            (plan, &stubs(&["1", "2"])),
        ],
    );
    git(&builder, &["merge", "-q", "--ff-only", "main"]);
    commit(
        &builder,
        "T4 filed",
        &[
            (TASKS_MD, &boxes(&["1", "2", "9", "4"], &[])),
            (plan, &stubs(&["1", "2", "4"])),
        ],
    );
    commit(
        &root,
        "T2 withdrawn, T3 filed",
        &[
            (TASKS_MD, &boxes(&["3", "1", "2", "9"], &["2"])),
            (plan, &stubs(&["1"])),
        ],
    );
    let (code, out, err) = applied(&root, &builder);
    assert_eq!((code, err.as_str()), (0, ""), "{out}");
    has(&out, "; resolved specs/451-x/plan.md (by section), specs/451-x/tasks.md (a bare box's lines restored)\n");
    let tasks = std::fs::read_to_string(root.join(TASKS_MD)).unwrap();
    assert_eq!(tasks, boxes(&["3", "1", "2", "9", "4"], &[]));
}

#[test]
fn a_code_conflict_is_left_in_the_tree_named_and_verified_once_resolved_by_hand() {
    let (_dir, root, builder) = trees("apply-code");
    commit(
        &builder,
        "T05: code",
        &[
            ("rust/lib.rs", "fn builder() {}\n"),
            ("rust/held.rs", "fn held() {}\n"),
            (TASKS_MD, &with_line("T05")),
        ],
    );
    commit(
        &root,
        "the clone's own edit",
        &[
            ("rust/lib.rs", "fn clone() {}\n"),
            (TASKS_MD, &with_line("T06")),
        ],
    );
    let sha = head(&builder);
    let (code, out, err) = applied(&root, &builder);
    assert_eq!((code, out.as_str()), (2, ""));
    has(&err, "carry: STOPPED - ");
    // RED FIRST (461 T05, the advisor's reading, 2026-11-27): the refusal named only rust/lib.rs, the one path no rule resolves,
    // though the rules' all-or-none leaves tasks.md unmerged too
    has(&err, " uncommitted, with a conflict this command does not resolve - nothing was resolved, every path left unmerged: rust/lib.rs (a line that is not prose: `fn a() {}`), specs/451-x/tasks.md (its rule would resolve it; left with the rest) - resolve each, `git -C ");
    has(
        &err,
        "add -- <path>`, and nothing to continue or commit (the no-commit form's caller commits)\n",
    );
    assert_eq!(
        git(&root, &["status", "--porcelain"]),
        "A  rust/held.rs\nUU rust/lib.rs\nUU specs/451-x/tasks.md"
    );
    // the resumed hand-in's question: unmerged - in this form's words, never "commit" - then resolved by hand to the clone's own
    // text (the builder's change dropped), then to the builder's
    let unmerged = verified(&root, &sha, &[]).unwrap().unwrap_err();
    assert_eq!(unmerged.len(), 1);
    has(&unmerged[0], "2 path(s) unmerged in ");
    has(
        &unmerged[0],
        " (rust/lib.rs specs/451-x/tasks.md) - resolve each and `git -C ",
    );
    has(
        &unmerged[0],
        "committing nothing: the no-commit form's caller commits",
    );
    std::fs::write(root.join("rust/lib.rs"), "fn clone() {}\n").unwrap();
    std::fs::write(root.join(TASKS_MD), with_line("T06")).unwrap();
    git(&root, &["add", "--", "rust/lib.rs", TASKS_MD]);
    let dropped = verified(&root, &sha, &[]).unwrap().unwrap_err();
    assert_eq!(
        dropped,
        ["the working tree does not hold the applied commit's rust/lib.rs"]
    );
    std::fs::write(root.join("rust/lib.rs"), "fn builder() {}\nfn clone() {}\n").unwrap();
    assert_eq!(verified(&root, &sha, &[]), Ok(Ok(2)));
}

#[test]
fn unfinished_work_no_commit_and_a_pick_that_cannot_start_are_refused() {
    let (_dir, root, builder) = trees("apply-refused");
    commit(
        &builder,
        "T05: code",
        &[("rust/lib.rs", "fn builder() {}\n")],
    );
    let sha = head(&builder);
    // what the apply came to, as its Debug words: each is a refusal
    let refused = |r: Result<Applied, String>| {
        let said = format!("{r:?}");
        assert!(said.starts_with("Ok(Refused("), "{said}");
        said
    };
    has(
        &refused(apply(&root, "no-such-ref")),
        " holds no commit no-such-ref",
    );
    // an unstaged edit in the pick's way: git refuses to start, nothing unmerged
    std::fs::write(root.join("rust/lib.rs"), "fn local() {}\n").unwrap();
    has(&refused(apply(&root, &sha)), "git cherry-pick -n said: ");
    // a staged change is unfinished work
    git(&root, &["add", "--", "rust/lib.rs"]);
    has(
        &refused(apply(&root, &sha)),
        " holds unfinished work: 1 staged path(s)",
    );
    let (code, _, err) = applied(&root, &builder);
    assert_eq!(code, 2);
    has(&err, "carry: refused - nothing applied: ");
    // a commit the tree cannot find is the carry's own refusal
    let (code, _, err) = applied(&root, &root.join("no-tree"));
    assert_eq!(code, 2);
    has(&err, "holds no commit HEAD");
}

#[test]
fn a_not_verified_apply_exits_1_and_says_what_failed() {
    let (_dir, root, builder) = trees("apply-unverified");
    commit(
        &builder,
        "T05: code",
        &[("rust/lib.rs", "fn builder() {}\n")],
    );
    let mut said = super::Said {
        out: String::new(),
        err: String::new(),
    };
    // an end that does not verify is NotVerified: no apply in a scratch repository reaches it (a -n pick that exits 0 leaves its
    // files in the working tree), so the end's answer is handed in
    let fails = super::super::apply::ended(Err(vec!["a reason".to_owned()]), Vec::new());
    assert_eq!(fails, Applied::NotVerified(vec!["a reason".to_owned()]));
    assert_eq!(
        super::super::apply::told(&root, &head(&builder), &fails, &mut said),
        1
    );
    has(&said.err, " uncommitted:\n  a reason\n");
    // the hand step a no-commit pick names after its page is regenerated by hand
    assert_eq!(
        Form::NoCommit.then(),
        "nothing to continue (the no-commit form commits nothing)"
    );
}
