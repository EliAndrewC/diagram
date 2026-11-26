//! The edit lines read, the touched files found, and a delta with nothing to judge (451 T254: the reader moved here from
//! `land/ready.rs`, its edges pinned by this crate's own tests).

use std::path::Path;

use super::{delta_of, edit_lines, touched, Delta};

fn git(at: &Path, args: &[&str]) {
    let ok = std::process::Command::new("git")
        .arg("-C")
        .arg(at)
        .args(["-c", "user.email=t@t", "-c", "user.name=t"])
        .args(args)
        .status()
        .unwrap()
        .success();
    assert!(ok, "git {args:?}");
}

#[test]
fn only_a_task_tagged_write_with_a_time_is_an_edit_line() {
    let dir = crate::tempdir::TempDir::new("touch-lines");
    let lines = [
        r#"{"ev":"PreToolUse","cat":"edit","task":"T1","t":"2026-11-25T10:00:00Z","path":"/t/a"}"#,
        r#"{"ev":"PostToolUse","cat":"read","task":"T1","t":"2026-11-25T10:00:00Z","path":"/t/a"}"#,
        r#"{"ev":"PostToolUse","cat":"edit" not json"#,
        r#"{"ev":"PostToolUse","cat":"edit","task":"T1","t":"no time","path":"/t/a"}"#,
        r#"{"ev":"PostToolUse","cat":"edit","task":"","t":"2026-11-25T10:00:00Z","path":"/t/a"}"#,
        r#"{"ev":"PostToolUse","cat":"edit","task":"T1","fallback":true,"t":"2026-11-25T10:00:00Z","path":"/t/a"}"#,
        r#"{"ev":"PostToolUse","cat":"bash","task":"T2","t":"2026-11-25T10:00:01Z","writes":["/t/b",3]}"#,
        r#"{"ev":"PostToolUse","cat":"edit","task":"T3","t":"2026-11-25T10:00:02Z","path":"/t/c"}"#,
    ];
    std::fs::write(dir.join("9-x.jsonl"), lines.join("\n")).unwrap();
    std::fs::write(dir.join("10-y.jsonl"), lines[7]).unwrap();
    let read: Vec<(String, String)> = edit_lines(&dir, "9-x")
        .into_iter()
        .map(|(task, _, path)| (task, path))
        .collect();
    assert_eq!(
        read,
        [
            ("T2".to_owned(), "/t/b".to_owned()),
            ("T3".to_owned(), "/t/c".to_owned())
        ]
    );
}

#[test]
fn a_file_is_touched_only_by_a_wanted_tasks_edit_under_a_known_tree() {
    let dir = crate::tempdir::TempDir::new("touch-found");
    let lines = [
        r#"{"ev":"PostToolUse","cat":"edit","task":"T1","t":"2026-11-25T10:00:00Z","path":"/elsewhere/a.rs"}"#,
        r#"{"ev":"PostToolUse","cat":"edit","task":"T2","t":"2026-11-25T10:00:00Z","path":"/t/a.rs"}"#,
        r#"{"ev":"PostToolUse","cat":"edit","task":"T1","t":"2026-11-25T10:00:00Z","path":"/t/a.rs"}"#,
    ];
    std::fs::write(dir.join("9-x.jsonl"), lines.join("\n")).unwrap();
    let prefixes = ["/t/".to_owned()];
    let wanted = |t: &str| t == "T1";
    assert!(touched(&dir, "9-x", &prefixes, &Delta::default(), &wanted).is_empty());
    let mut delta = Delta::default();
    delta.judged.insert("a.rs".to_owned());
    // landed a day before the edit, committed by the push after it
    delta.landed.insert("a.rs".to_owned(), 1_795_514_400);
    delta.committed.insert("a.rs".to_owned(), 1_795_687_200);
    let found = touched(&dir, "9-x", &prefixes, &delta, &wanted);
    assert_eq!(found["a.rs"].0, "T1");
}

#[test]
fn a_delta_of_only_sectioned_files_judges_nothing() {
    let dir = crate::tempdir::TempDir::new("touch-delta");
    git(&dir, &["init", "-q"]);
    git(&dir, &["commit", "-q", "--allow-empty", "-m", "base"]);
    git(&dir, &["update-ref", "refs/remotes/origin/main", "HEAD"]);
    std::fs::create_dir_all(dir.join("specs/9-x")).unwrap();
    std::fs::write(dir.join("specs/9-x/tasks.md"), "- [ ] T1 x\n").unwrap();
    git(&dir, &["add", "-A"]);
    git(&dir, &["commit", "-q", "-m", "a task"]);
    let delta = delta_of(&dir, "specs/9-x").unwrap();
    assert!(delta.judged.is_empty() && delta.committed.is_empty());
}
