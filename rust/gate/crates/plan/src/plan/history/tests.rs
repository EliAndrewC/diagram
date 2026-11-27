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

/// 451 T465: after T457 each process still fetched and parsed every version the first question walked, about 5 s of a landing's
/// tick checks and again in `plan push`. The versions' digests are now kept on disk in the clone's git directory: a second process
/// (a thread of its own, its thread-local stores fresh) answers from them, fetching only the one version whose text it returns.
#[test]
fn a_second_process_reads_the_versions_from_the_index_not_git() {
    let root = repo();
    let dir = root.join("specs/1-x");
    std::fs::create_dir_all(&dir).unwrap();
    let plan = dir.join("plan.md");
    let versions: Vec<String> = (0..=CHUNK + 4)
        .map(|i| format!("## T01 a\n\nversion {i}\n\n## T01 a\n\nthe same key again {i}\n"))
        .collect();
    committed(&root, "specs/1-x/plan.md", &versions);
    let ask = |plan: std::path::PathBuf| {
        std::thread::spawn(move || {
            let history = History::new(&plan, "HEAD");
            let missing = (history.block("## T01 a", "1"), history.section("T01", "2"));
            let after_missing = counted();
            let first = "## T01 a\n\nversion 0\n\n";
            let found = history.block("## T01 a", &block_digest(first));
            (missing, after_missing, found, counted())
        })
        .join()
        .unwrap()
    };
    let v = versions.len();
    let first = Some("## T01 a\n\nversion 0\n\n".to_owned());
    // the first process reads every version from git; the second only its canary (the newest version, parsed to check the
    // index's digests) to say a block is missing, and the text it returns from where the first kept it
    assert_eq!(
        ask(plan.clone()),
        ((None, None), (v, v), first.clone(), (v, v))
    );
    assert_eq!(
        ask(plan.clone()),
        ((None, None), (1, 1), first.clone(), (1, 1))
    );
    // a commit made since: only the new version is read beside the canary
    let later = "## T01 a\n\nlater\n".to_owned();
    std::fs::write(&plan, &later).unwrap();
    git(&root, &["commit", "-qam", "later"]);
    assert_eq!(
        ask(plan.clone()),
        ((None, None), (2, 2), first.clone(), (2, 2))
    );
    assert_eq!(
        ask(plan.clone()),
        ((None, None), (1, 1), first.clone(), (1, 1))
    );
    // a kept text whose digest is not the question's is not taken: its version is read again
    let texts = root.join(".git/plan-index/texts");
    for kept in std::fs::read_dir(&texts).unwrap().flatten() {
        std::fs::write(kept.path(), "changed").unwrap();
    }
    assert_eq!(
        ask(plan.clone()),
        ((None, None), (1, 1), first.clone(), (2, 2))
    );
    // and kept again
    assert_eq!(ask(plan), ((None, None), (1, 1), first, (1, 1)));
}

/// An index whose digests the parser no longer gives (a later `blocks` or archive rule) is dropped by its canary and written anew,
/// and a commit another process indexed since this thread read the file is taken from the file, not git.
#[test]
fn a_changed_parser_drops_the_index_and_another_process_s_commits_are_read_from_it() {
    let root = repo();
    let dir = root.join("specs/1-x");
    std::fs::create_dir_all(&dir).unwrap();
    let plan = dir.join("plan.md");
    let versions: Vec<String> = (0..5)
        .map(|i| format!("## T01 a\n\nversion {i}\n"))
        .collect();
    committed(&root, "specs/1-x/plan.md", &versions);
    let newest = versions[4].clone();
    let on_thread = |plan: &std::path::Path, work: fn(&History) -> Option<String>| {
        let plan = plan.to_owned();
        std::thread::spawn(move || (work(&History::new(&plan, "HEAD")), counted()))
            .join()
            .unwrap()
    };
    let missing: fn(&History) -> Option<String> = |h| h.block("## T01 a", "1");
    assert_eq!(on_thread(&plan, missing), (None, (5, 5)));
    let file = root.join(".git/plan-index/specs%2F1-x%2Fplan.md.idx");
    let text = std::fs::read_to_string(&file).unwrap();
    let sha = digest(newest.as_bytes());
    std::fs::write(&file, text.replace(&sha, &"0".repeat(64))).unwrap();
    // the canary's version and the four others: all five read again, and the index written anew
    assert_eq!(on_thread(&plan, missing), (None, (5, 5)));
    let newest_section: fn(&History) -> Option<String> =
        |h| h.section("T01", &digest("## T01 a\n\nversion 4\n".as_bytes()));
    assert_eq!(on_thread(&plan, newest_section), (Some(newest), (1, 1)));
    assert_eq!(on_thread(&plan, missing), (None, (1, 1)));
    // this thread reads the file; another thread commits three versions and indexes them; a new History here meets them uncovered,
    // reads the file again and takes them from it: the canary's one version read, where the walk would read three
    let here = History::new(&plan, "HEAD");
    assert_eq!(here.block("## T01 a", "1"), None);
    let before = counted();
    let more = on_thread(&plan, |h| {
        let root = h
            .path()
            .parent()
            .unwrap()
            .parent()
            .unwrap()
            .parent()
            .unwrap()
            .to_owned();
        for i in 5..8 {
            std::fs::write(h.path(), format!("## T01 a\n\nversion {i}\n")).unwrap();
            git(&root, &["commit", "-qam", "more"]);
        }
        History::new(h.path(), "HEAD").block("## T01 a", "1")
    });
    assert_eq!(more, (None, (4, 4)));
    assert_eq!(History::new(&plan, "HEAD").block("## T01 a", "1"), None);
    assert_eq!((counted().0 - before.0, counted().1 - before.1), (1, 1));
}

/// A version that could not be read - here the commit that removed the path - is read as empty and never kept on disk, so a
/// passing failure is not kept either: every process reads it again.
#[test]
fn a_version_that_cannot_be_read_is_never_kept() {
    let root = repo();
    std::fs::create_dir_all(root.join("sub")).unwrap();
    std::fs::write(root.join("sub/plan.md"), "## A\n").unwrap();
    git(&root, &["add", "-A"]);
    git(&root, &["commit", "-qm", "c"]);
    git(&root, &["rm", "-q", "sub/plan.md"]);
    git(&root, &["commit", "-qm", "gone"]);
    std::fs::create_dir_all(root.join("sub")).unwrap();
    std::fs::write(root.join("sub/plan.md"), "## A\n").unwrap();
    let plan = root.join("sub/plan.md");
    let ask = |plan: std::path::PathBuf| {
        std::thread::spawn(move || {
            let found = History::new(&plan, "HEAD").block("## A", &block_digest("## A\n"));
            (found, counted())
        })
        .join()
        .unwrap()
    };
    let found = Some("## A\n".to_owned());
    assert_eq!(ask(plan.clone()), (found.clone(), (2, 2)));
    // the canary (the one readable version) and the removal again
    assert_eq!(ask(plan), (found, (2, 2)));
}

/// 451 T474: an index another digest code wrote - its header's stamp another, though every digest in it is what this parser gives -
/// is read as nothing: every version is read from git again, and the index written anew under this code's stamp.
#[test]
fn an_index_stamped_by_other_digest_code_is_read_again_from_git() {
    let root = repo();
    std::fs::create_dir_all(root.join("specs/1-x")).unwrap();
    let plan = root.join("specs/1-x/plan.md");
    let versions: Vec<String> = (0..4).map(|i| format!("## A\n\nversion {i}\n")).collect();
    committed(&root, "specs/1-x/plan.md", &versions);
    let missing = |plan: std::path::PathBuf| {
        std::thread::spawn(move || (History::new(&plan, "HEAD").block("## A", "1"), counted()))
            .join()
            .unwrap()
    };
    assert_eq!(missing(plan.clone()), (None, (4, 4)));
    assert_eq!(missing(plan.clone()), (None, (1, 1)));
    let file = root.join(".git/plan-index/specs%2F1-x%2Fplan.md.idx");
    let text = std::fs::read_to_string(&file).unwrap();
    let stamp = super::super::sections::digests::stamp();
    std::fs::write(&file, text.replacen(&stamp, &"0".repeat(64), 1)).unwrap();
    assert_eq!(missing(plan.clone()), (None, (4, 4)));
    assert!(std::fs::read_to_string(&file)
        .unwrap()
        .starts_with(&format!("l7r plan-index 1 {stamp}\n")));
    assert_eq!(missing(plan), (None, (1, 1)));
}

/// A section's kept text is judged by the section digest, a block's by the block digest (`kept_text`).
#[test]
fn a_kept_section_text_is_found_by_its_section_digest() {
    let root = repo();
    let file = root.join("plan.idx");
    let body = "### T1 a task\n\nits text\n";
    let at = super::index::text_file(&file, "c0", false, "T1");
    std::fs::create_dir_all(at.parent().unwrap()).unwrap();
    std::fs::write(&at, body).unwrap();
    assert_eq!(
        super::kept_text(&file, "c0", false, "T1", &digest(body.as_bytes())).as_deref(),
        Some(body)
    );
    assert_eq!(super::kept_text(&file, "c0", false, "T1", "other"), None);
    // 451 T478: a hit is a read, which touches the text so the prune keeps it; a miss touches nothing
    let old = std::time::SystemTime::now() - std::time::Duration::from_secs(9 * 86_400);
    let file_at = std::fs::File::options().write(true).open(&at).unwrap();
    file_at.set_modified(old).unwrap();
    let mtime = || std::fs::metadata(&at).unwrap().modified().unwrap();
    assert_eq!(super::kept_text(&file, "c0", false, "T1", "other"), None);
    assert_eq!(mtime(), old);
    assert!(super::kept_text(&file, "c0", false, "T1", &digest(body.as_bytes())).is_some());
    assert!(mtime() > old);
}
