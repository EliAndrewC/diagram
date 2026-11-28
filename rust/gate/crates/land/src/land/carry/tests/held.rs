//! A carried file whose change HEAD already holds (461 T73): the review ledger's rows, appended by the builder, already in the clone
//! among others - by another route, its union driver merging the pick to HEAD's own text, so the carry moves nothing there and HEAD's
//! blob is not the commit's. Met carrying 461 T21 (230b5c0c9d, 2026-11-27) and at the lane's batch 462-1 (1136054db4, 2026-11-28).

use std::path::PathBuf;

use l7r_shared::tempdir::TempDir;

use super::super::super::tests::has;
use super::super::super::unfinished::tests::repo;
use super::super::{holds_change, missing, Form};
use super::{carried, commit, git};

const LEDGER: &str = "dev/review-ledger.md";

/// A clone whose ledger holds rows a and b under the union driver; a builder's commit adding x and y and `rust/held.rs`; then the
/// clone given x and y with w after them, as the lane's base held 462 T549's rows: the clone, the builder and the builder's sha.
fn world(tag: &str) -> (TempDir, PathBuf, PathBuf, String) {
    let (dir, root) = repo(tag);
    commit(
        &root,
        "the ledger",
        &[
            (".gitattributes", "dev/review-ledger.md merge=union\n"),
            (LEDGER, "| a |\n| b |\n"),
        ],
    );
    let builder = dir.join("builder");
    let path = builder.to_string_lossy().into_owned();
    git(&root, &["worktree", "add", "-q", "-b", "builder", &path]);
    commit(
        &builder,
        "T73: code",
        &[
            ("rust/held.rs", "fn held() {}\n"),
            (LEDGER, "| a |\n| b |\n| x |\n| y |\n"),
        ],
    );
    let sha = git(&builder, &["rev-parse", "HEAD"]);
    commit(
        &root,
        "its rows by another route",
        &[(LEDGER, "| a |\n| b |\n| x |\n| y |\n| w |\n")],
    );
    (dir, root, builder, sha)
}

#[test]
fn a_carry_whose_ledger_rows_head_already_holds_among_others_is_verified() {
    let (_dir, root, builder, _) = world("carry-held-rows");
    let (code, out, err) = carried(&root, &builder);
    assert_eq!((code, err.as_str()), (0, ""));
    has(&out, "its 2 non-spec file(s) in HEAD");
    assert_eq!(
        std::fs::read_to_string(root.join(LEDGER)).unwrap(),
        "| a |\n| b |\n| x |\n| y |\n| w |\n"
    );
}

#[test]
fn a_file_whose_change_head_holds_is_held_and_one_head_lacks_still_is_not() {
    let (_dir, root, _builder, sha) = world("carry-held-missing");
    let head = git(&root, &["rev-parse", "HEAD"]);
    let lacks = Ok((2, vec!["rust/held.rs".to_owned()]));
    assert_eq!(missing(&root, &sha, &head, &[], Form::Commit), lacks);
    // the no-commit form reads the working tree: the same file held there, the same one lacking
    assert_eq!(missing(&root, &sha, &head, &[], Form::NoCommit), lacks);
    // HEAD's rows taken out again: the ledger no longer held
    commit(&root, "rows gone", &[(LEDGER, "| a |\n| b |\n| w |\n")]);
    let head = git(&root, &["rev-parse", "HEAD"]);
    let both = vec!["dev/review-ledger.md".to_owned(), "rust/held.rs".to_owned()];
    assert_eq!(
        missing(&root, &sha, &head, &[], Form::Commit),
        Ok((2, both))
    );
}

#[test]
fn a_change_is_held_by_its_lines_counted_never_by_a_reorder_or_a_common_line_alone() {
    let parent = "a\n}\nb\n";
    // added rows held among others, and a removed line gone
    assert!(holds_change(parent, "a\n}\nb\nx\n", "a\n}\nw\nb\nx\nv\n"));
    assert!(holds_change(parent, "a\n}\n", "a\n}\nw\n"));
    // an added row missing, a removed line still there
    assert!(!holds_change(parent, "a\n}\nb\nx\n", "a\n}\nb\nw\n"));
    assert!(!holds_change(parent, "a\n}\n", "a\n}\nb\nw\n"));
    // a common line added: held only where HEAD has as many of it as the commit's file
    assert!(!holds_change(parent, "a\n}\nb\n}\n", "a\n}\nb\nw\n"));
    assert!(holds_change(parent, "a\n}\nb\n}\n", "}\na\n}\nb\n"));
    // a reorder changes no count: held by no count
    assert!(!holds_change(parent, "b\n}\na\n", parent));
}
