//! A plan's earlier text, from what a verdict kept or from git.

use super::super::sections::{block_digest, digest};
use super::super::tests::{git, repo};
use super::{counted, keep, recall, History, CHUNK};
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

/// Each of `versions` a commit of `rel` on main, by one `git fast-import` where 30 commits took 30 processes (feature 449 T167); the
/// working copy the last.
fn committed(root: &std::path::Path, rel: &str, versions: &[String]) {
    let mut stream = String::new();
    for (n, text) in versions.iter().enumerate() {
        let message = if n == 0 { "first" } else { "next" };
        std::fmt::Write::write_fmt(
            &mut stream,
            format_args!(
                "commit refs/heads/main\ncommitter t <t@t> {} +0000\ndata {}\n{message}\nM 100644 inline {rel}\ndata {}\n{text}\n",
                1_700_000_000 + n,
                message.len(),
                text.len()
            ),
        )
        .unwrap();
    }
    let mut import = std::process::Command::new("git")
        .arg("-C")
        .arg(root)
        .args(["fast-import", "--quiet"])
        .stdin(std::process::Stdio::piped())
        .spawn()
        .unwrap();
    std::io::Write::write_all(&mut import.stdin.take().unwrap(), stream.as_bytes()).unwrap();
    assert!(import.wait().unwrap().success());
    std::fs::write(root.join(rel), versions.last().unwrap()).unwrap();
    git(root, &["reset", "-q"]);
}

#[test]
fn a_block_and_a_section_are_found_however_far_back() {
    let root = repo();
    let dir = root.join("specs/1-x");
    std::fs::create_dir_all(&dir).unwrap();
    let plan = dir.join("plan.md");
    let first = "## T01 a\n\nthe first\n";
    // the first version and CHUNK + 3 after it, more than one chunk back, each a commit of plan.md on main, the working copy the last
    let mut versions = vec![first.to_owned()];
    versions.extend((0..=CHUNK + 2).map(|i| format!("## T01 a\n\nversion {i}\n")));
    committed(&root, "specs/1-x/plan.md", &versions);
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

/// 451 T457: a landing's first pass asked 69 questions a task of fresh Histories, each question parsing every version it walked
/// again (16,773 parses of a 1 MB plan.md for one task, 56 s). Every version is now fetched and parsed once a process, however many
/// questions and Histories ask - and each answer is the one the newest-first walk gave.
#[test]
fn every_version_is_read_and_parsed_once_however_many_questions_ask() {
    let root = repo();
    let dir = root.join("specs/1-x");
    std::fs::create_dir_all(&dir).unwrap();
    let plan = dir.join("plan.md");
    let versions: Vec<String> = (0..=CHUNK + 4)
        .map(|i| format!("## T01 a\n\nversion {i}\n\n## T01 a\n\nthe same key again {i}\n"))
        .collect();
    committed(&root, "specs/1-x/plan.md", &versions);
    let (fetched, parsed) = (counted().0, counted().1);
    let one = History::new(&plan, "HEAD");
    for sha in ["1", "2", "3"] {
        assert_eq!(one.block("## T01 a", sha), None);
    }
    assert_eq!(one.section("T01", "4"), None);
    let two = History::new(&plan, "HEAD");
    assert_eq!(two.block("## T01 a", "5"), None);
    assert_eq!(two.section("T01", "6"), None);
    let v = versions.len();
    assert_eq!((counted().0 - fetched, counted().1 - parsed), (v, v));
    // the first block of a key in its version, the newest version holding it
    let first = "## T01 a\n\nversion 0\n\n";
    assert_eq!(
        two.block("## T01 a", &block_digest(first)).as_deref(),
        Some(first)
    );
    let again = "## T01 a\n\nthe same key again 0\n";
    assert_eq!(two.block("## T01 a", &block_digest(again)), None);
    assert_eq!(
        two.block("## T01 a#2", &block_digest(again)).as_deref(),
        Some(again)
    );
    let newest = &versions[v - 1];
    assert_eq!(
        one.section("T01", &digest(newest.as_bytes())).as_deref(),
        Some(newest.as_str())
    );
    // a commit made after a History read its versions is seen by the next History, never by that one
    let later = "## T01 a\n\nlater\n".to_owned();
    std::fs::write(&plan, &later).unwrap();
    git(&root, &["commit", "-qam", "later"]);
    assert_eq!(one.block("## T01 a", &block_digest(&later)), None);
    let three = History::new(&plan, "HEAD");
    assert_eq!(
        three.block("## T01 a", &block_digest(&later)).as_deref(),
        Some(later.as_str())
    );
    assert_eq!(
        (counted().0 - fetched, counted().1 - parsed),
        (v + 1, v + 1)
    );
}

/// Two bodies of one block digest - one with an archive line - answer with the newer version's.
#[test]
fn a_digest_two_versions_share_answers_with_the_newer_text() {
    let root = repo();
    let plan = root.join("plan.md");
    let old = "## A\n\nthe rule\n".to_owned();
    let archived = "## A\n\nthe rule\n<!-- plan-archive: plan-done.md -->\n".to_owned();
    committed(
        &root,
        "plan.md",
        &[old.clone(), archived.clone(), "## B\n".to_owned()],
    );
    let sha = block_digest(&old);
    assert_eq!(
        History::new(&plan, "HEAD").block("## A", &sha).as_deref(),
        Some(archived.as_str())
    );
    assert_eq!(
        History::new(&plan, "HEAD~1").block("## A", &sha).as_deref(),
        Some(archived.as_str())
    );
    assert_eq!(
        History::new(&plan, "HEAD~2").block("## A", &sha).as_deref(),
        Some(old.as_str())
    );
}
