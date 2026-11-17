//! A plan's earlier text, from what a verdict kept or from git.

use super::super::sections::{block_digest, digest};
use super::super::tests::{git, repo};
use super::{keep, recall, History, CHUNK};
use crate::checks::scratch;

#[test]
fn a_kept_text_is_found_by_its_digest_before_it_is_ever_committed() {
    let root = repo();
    let plan = root.join("plan.md");
    std::fs::write(&plan, "x").unwrap();
    let body = "## A\n\nthe rule\n";
    keep(&plan, &[(block_digest(body), body.to_owned())]);
    let history = History::new(&plan, "HEAD");
    assert_eq!(
        history.block("## A", &block_digest(body)).as_deref(),
        Some(body)
    );
    assert_eq!(history.block("## A", "bad/sha"), None);
    assert_eq!(recall(&plan, ""), None);
    assert_eq!(history.path(), plan);
}

#[test]
fn a_block_and_a_section_are_found_however_far_back() {
    let root = repo();
    let dir = root.join("specs/1-x");
    std::fs::create_dir_all(&dir).unwrap();
    let plan = dir.join("plan.md");
    let first = "## T01 a\n\nthe first\n";
    // the first version and CHUNK + 3 after it, more than one chunk back, committed by one `git fast-import` where 30 commits took 30
    // processes (feature 449 T167); each a commit of plan.md on main, the working copy the last
    let mut versions = vec![first.to_owned()];
    versions.extend((0..=CHUNK + 2).map(|i| format!("## T01 a\n\nversion {i}\n")));
    let mut stream = String::new();
    for (n, text) in versions.iter().enumerate() {
        let message = if n == 0 { "first" } else { "next" };
        std::fmt::Write::write_fmt(
            &mut stream,
            format_args!(
                "commit refs/heads/main\ncommitter t <t@t> {} +0000\ndata {}\n{message}\nM 100644 inline specs/1-x/plan.md\ndata {}\n{text}\n",
                1_700_000_000 + n,
                message.len(),
                text.len()
            ),
        )
        .unwrap();
    }
    let mut import = std::process::Command::new("git")
        .arg("-C")
        .arg(&*root)
        .args(["fast-import", "--quiet"])
        .stdin(std::process::Stdio::piped())
        .spawn()
        .unwrap();
    std::io::Write::write_all(&mut import.stdin.take().unwrap(), stream.as_bytes()).unwrap();
    assert!(import.wait().unwrap().success());
    std::fs::write(&plan, versions.last().unwrap()).unwrap();
    git(&root, &["reset", "-q"]);
    assert_eq!(
        git(&root, &["rev-list", "--count", "HEAD"]),
        (CHUNK + 4).to_string()
    );
    let history = History::new(&plan, "HEAD");
    assert_eq!(
        history.block("## T01 a", &block_digest(first)).as_deref(),
        Some(first)
    );
    assert_eq!(
        history.section("T01", &digest(first.as_bytes())).as_deref(),
        Some(first)
    );
    assert_eq!(history.block("## T01 a", "0"), None);
}

#[test]
fn a_path_not_in_a_repository_knows_nothing_and_a_missing_version_reads_empty() {
    let dir = scratch("no-git");
    std::fs::write(dir.join("plan.md"), "x").unwrap();
    let history = History::new(&dir.join("plan.md"), "HEAD");
    assert_eq!(history.section("T01", "x"), None);
    keep(&dir.join("plan.md"), &[("a".to_owned(), "b".to_owned())]);
    let root = repo();
    std::fs::create_dir_all(root.join("sub")).unwrap();
    std::fs::write(root.join("sub/plan.md"), "## A\n").unwrap();
    git(&root, &["add", "-A"]);
    git(&root, &["commit", "-qm", "c"]);
    git(&root, &["rm", "-q", "sub/plan.md"]);
    git(&root, &["commit", "-qm", "gone"]);
    std::fs::create_dir_all(root.join("sub")).unwrap();
    std::fs::write(root.join("sub/plan.md"), "## A\n").unwrap();
    let gone = History::new(&root.join("sub/plan.md"), "HEAD");
    assert_eq!(
        gone.block("## A", &block_digest("## A\n")).as_deref(),
        Some("## A\n")
    );
}
