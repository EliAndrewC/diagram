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
            delta.changed(base, None, specs),
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
        delta.changed(base, None, &pages),
        narrow(&root, base, None, &pages)
    );
    assert!(!delta
        .changed(base, None, &pages)
        .contains("0094-trade.html\n"));
    let head = commit(&root, "moved");
    assert_eq!(
        delta.changed(base, Some(&head), &pages),
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
