//! One computation's reads against the narrow git calls each family made before (feature 449 T107).

use super::Delta;
use crate::record::repo::git;
use crate::record::testkit::{commit, edit_everything, put, record, PAGE};

/// What the narrow `git diff --name-only` printed before the shared listing.
fn narrow(root: &std::path::Path, base: &str, head: Option<&str>, specs: &[&str]) -> String {
    let mut args = vec!["diff", "--name-only", base];
    args.extend(head);
    args.push("--");
    args.extend(specs);
    git(root, &args)
}

#[test]
fn every_family_s_pathspec_lies_under_the_shared_ones() {
    for spec in ["research/questions", "research/sources/010-works-cited"] {
        assert!(Delta::WATCHED.iter().any(|w| super::under(spec, w)));
    }
    assert!(super::under(
        "\"research/questions/\\303\\251.html\"",
        "research/questions"
    ));
    assert!(!super::under(
        "research/questions2/a.html",
        "research/questions"
    ));
    assert!(super::under("research/x", "research/"));
}

#[test]
fn the_shared_diff_prints_what_each_narrow_diff_printed() {
    let root = record("delta-diff");
    edit_everything(&root);
    let base = git(&root, &["rev-parse", "HEAD"]);
    let base = base.trim();
    let mut delta = Delta::new(&root);
    for specs in [
        &["research/questions"][..],
        &crate::record::units::SOURCE_DIRS[..],
        &crate::record::owed::ENTRY_READS[..],
    ] {
        assert_eq!(
            delta.changed(base, None, specs).unwrap(),
            narrow(&root, base, None, specs)
        );
    }
    // a page deleted and another added under one pathspec could pair as a rename: the narrow diff runs itself
    git(&root, &["checkout", base, "--", PAGE]);
    std::fs::rename(
        root.join(PAGE),
        root.join("research/questions/0099-moved.html"),
    )
    .unwrap();
    git(&root, &["add", "-A"]);
    let mut delta = Delta::new(&root);
    let pages = ["research/questions"];
    assert_eq!(
        delta.changed(base, None, &pages).unwrap(),
        narrow(&root, base, None, &pages)
    );
    assert!(!delta
        .changed(base, None, &pages)
        .unwrap()
        .contains("0094-trade.html\n"));
    let head = commit(&root, "moved");
    assert_eq!(
        delta.changed(base, Some(&head), &pages).unwrap(),
        narrow(&root, base, Some(&head), &pages)
    );
}

#[test]
fn the_revisions_the_listing_and_the_blobs_are_read_once() {
    let root = record("delta-revs");
    let head = git(&root, &["rev-parse", "HEAD"]).trim().to_owned();
    let mut delta = Delta::new(&root);
    assert_eq!(delta.merge_base(), head);
    assert_eq!(delta.entry_base(), head);
    assert_eq!(delta.translation_base(), head);
    assert!(delta.git_dir().ends_with(".git"));
    git(&root, &["update-ref", "-d", "refs/remotes/origin/main"]);
    let mut delta = Delta::new(&root);
    assert_eq!(delta.merge_base(), head);
    assert_eq!(delta.translation_base(), "");
    let names = vec![PAGE.to_owned(), "research/questions/none.html".to_owned()];
    let texts = delta.texts(&head, &names);
    assert!(texts[0].contains("Trade"));
    assert_eq!(texts[1], "");
    put(&root, PAGE, "changed after the read\n");
    assert!(delta.texts(&head, &names[..1])[0].contains("Trade"));
    let listing = delta.listing(&head, &["research/questions"]);
    assert!(listing.contains(PAGE) && !listing.contains("modals"));
    put(&root, "research/questions/new.html", "x\n");
    assert_eq!(
        delta.others(&["research/questions"]),
        "research/questions/new.html\n"
    );
}

#[test]
fn a_one_page_delta_asks_git_for_that_page_alone() {
    // feature 451 T43: every computation read every page at the base, 1,951 blobs by one `cat-file --batch` for a
    // one-page delta on the real record; an unchanged page reads the same in the working tree
    let root = record("delta-one-page");
    let text = std::fs::read_to_string(root.join(PAGE)).unwrap();
    put(
        &root,
        PAGE,
        &text.replace("A short way apart.", "A long way apart."),
    );
    let mut delta = Delta::new(&root);
    let families = crate::record::owed::FAMILIES;
    let owed = crate::record::owed::units_in(&mut delta, None, None, &families, "").unwrap();
    let slugs: Vec<&str> = owed.iter().map(|u| u.slug.as_str()).collect();
    assert!(!slugs.is_empty(), "{slugs:?}");
    assert_eq!(delta.blobs_asked(), 1, "{slugs:?}");
}

#[test]
fn a_file_read_from_the_tree_is_the_blob_git_would_give() {
    // every state a page can be in against the base, each file's text equal to what `cat-file` reads of it (451 T43)
    let root = record("delta-same-bytes");
    put(&root, "research/questions/0095-crlf.html", "a\r\nb\r\n");
    put(&root, "research/questions/0096-sparse.html", "kept\n");
    put(&root, "research/questions/0097-staged.html", "staged\n");
    put(&root, "research/questions/0098-gone.html", "gone\n");
    put(&root, "research/questions/0099-linked.html", "target\n");
    put(&root, "research/questions/0101-assumed.html", "assumed\n");
    let base = commit(&root, "states");
    let text = std::fs::read_to_string(root.join(PAGE)).unwrap();
    put(
        &root,
        PAGE,
        &text.replace("A short way apart.", "A long way apart."),
    );
    put(
        &root,
        "research/questions/0097-staged.html",
        "staged again\n",
    );
    git(&root, &["add", "research/questions/0097-staged.html"]);
    put(&root, "research/questions/0097-staged.html", "staged\n");
    std::fs::remove_file(root.join("research/questions/0098-gone.html")).unwrap();
    git(
        &root,
        &[
            "update-index",
            "--skip-worktree",
            "research/questions/0096-sparse.html",
        ],
    );
    std::fs::remove_file(root.join("research/questions/0096-sparse.html")).unwrap();
    let link = root.join("research/questions/0099-linked.html");
    std::fs::remove_file(&link).unwrap();
    std::os::unix::fs::symlink("0094-trade.html", &link).unwrap();
    git(
        &root,
        &[
            "update-index",
            "--assume-unchanged",
            "research/questions/0099-linked.html",
        ],
    );
    put(&root, "research/questions/0100-new.html", "untracked\n");
    // a file git is told not to compare, edited: its diff is silent, its blob still the base's
    git(
        &root,
        &[
            "update-index",
            "--assume-unchanged",
            "research/questions/0101-assumed.html",
        ],
    );
    put(&root, "research/questions/0101-assumed.html", "edited\n");
    let mut delta = Delta::new(&root);
    let mut names: Vec<String> = delta
        .listing(&base, &["research/questions"])
        .lines()
        .map(str::to_owned)
        .collect();
    names.push("research/questions/0100-new.html".to_owned());
    let objects: Vec<String> = names.iter().map(|n| format!("{base}:{n}")).collect();
    assert_eq!(
        delta.texts(&base, &names),
        crate::record::repo::cat_blobs(&root, &objects)
    );
    // the edited page, the gone one, the skip-worktree one, the link, the carriage return, the untracked one and the
    // assumed-unchanged one went to git
    assert_eq!(delta.blobs_asked(), 7, "{names:?}");
}

#[test]
fn a_diff_git_cannot_run_reads_every_base_file_from_git() {
    // the ruling on T43's found-and-left: a failed `git diff` printed nothing, so every page read from the tree and the
    // record owed nothing; a corrupt index fails the diff (and `ls-files -v`) while `cat-file` still reads the base
    let root = record("delta-diff-fails");
    let base = git(&root, &["rev-parse", "HEAD"]).trim().to_owned();
    let text = std::fs::read_to_string(root.join(PAGE)).unwrap();
    put(
        &root,
        PAGE,
        &text.replace("A short way apart.", "A long way apart."),
    );
    std::fs::write(root.join(".git/index"), "corrupt").unwrap();
    let mut delta = Delta::new(&root);
    let names: Vec<String> = delta
        .listing(&base, &["research/questions"])
        .lines()
        .map(str::to_owned)
        .collect();
    let objects: Vec<String> = names.iter().map(|n| format!("{base}:{n}")).collect();
    assert_eq!(
        delta.texts(&base, &names),
        crate::record::repo::cat_blobs(&root, &objects)
    );
    assert_eq!(delta.blobs_asked(), names.len(), "{names:?}");
}

#[test]
fn a_diff_git_cannot_run_is_refused_not_read_as_nothing_changed() {
    // the session's second ruling on T43: a failed `git diff` read as an empty delta, so the pop-ups citing a reworded
    // page went unowed (six modal-research units on the real record); it refuses with git's error, never owing everything
    let root = record("delta-diff-refused");
    let text = std::fs::read_to_string(root.join(PAGE)).unwrap();
    put(
        &root,
        PAGE,
        &text.replace("A short way apart.", "A long way apart."),
    );
    let families = crate::record::owed::FAMILIES;
    let whole =
        crate::record::owed::units_in(&mut Delta::new(&root), None, None, &families, "").unwrap();
    assert!(whole.iter().any(|u| u.slug.starts_with("modal-")));
    std::fs::write(root.join(".git/index"), "corrupt").unwrap();
    let repair = format!(
        "; repair the index, e.g. git -C {} reset -q",
        root.display()
    );
    let refused = crate::record::owed::units_in(&mut Delta::new(&root), None, None, &families, "")
        .unwrap_err();
    let said = refused.starts_with("cannot tell what changed: git diff failed: ")
        && refused.contains("index")
        && refused.ends_with(&repair);
    assert!(said, "{refused}");
}
