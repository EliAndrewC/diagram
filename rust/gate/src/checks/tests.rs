//! The shared helpers and the command line.

use std::process::Command;

use super::cli;

pub(super) fn repo(tag: &str) -> std::path::PathBuf {
    let dir = super::scratch(tag);
    for args in [
        vec!["init", "-q", "-b", "main"],
        vec!["config", "user.email", "t@t"],
        vec!["config", "user.name", "t"],
    ] {
        assert!(Command::new("git")
            .arg("-C")
            .arg(&dir)
            .args(args)
            .output()
            .unwrap()
            .status
            .success());
    }
    dir
}

pub(super) fn put(dir: &std::path::Path, rel: &str, text: &str) {
    let path = dir.join(rel);
    std::fs::create_dir_all(path.parent().unwrap()).unwrap();
    std::fs::write(path, text).unwrap();
}

pub(super) fn commit(dir: &std::path::Path) {
    for args in [vec!["add", "-A"], vec!["commit", "-qm", "c"]] {
        assert!(Command::new("git")
            .arg("-C")
            .arg(dir)
            .args(args)
            .output()
            .unwrap()
            .status
            .success());
    }
}

pub(super) fn based(dir: &std::path::Path) {
    assert!(Command::new("git")
        .arg("-C")
        .arg(dir)
        .args(["update-ref", "refs/remotes/origin/main", "HEAD"])
        .output()
        .unwrap()
        .status
        .success());
}

fn owned(args: &[&str]) -> Vec<String> {
    args.iter().map(|s| (*s).to_owned()).collect()
}

#[test]
fn each_check_answers_by_name_and_its_run_is_recorded() {
    let dir = repo("cli");
    assert_eq!(cli(&owned(&["nonsense"]), &dir).code, 2);
    let tree = dir.display().to_string();
    assert_eq!(cli(&owned(&["partial-citations", &tree]), &dir).code, 0);
    assert_eq!(cli(&[], &dir).code, 2);
    assert_eq!(cli(&owned(&["needs", "duplicate-defs"]), &dir).code, 0);
    assert_eq!(cli(&owned(&["needs"]), &dir).code, 0);
    for name in [
        "file-scale",
        "stale-dirs",
        "research-pointers",
        "house-style-delta",
    ] {
        assert_eq!(cli(&owned(&[name, "--selftest"]), &dir).code, 0, "{name}");
    }
    assert_eq!(cli(&owned(&["question-size"]), &dir).code, 0);
    assert_eq!(cli(&owned(&["rust-tooling"]), &dir).code, 0);
    let usage = std::fs::read_to_string(dir.join(".git/tool-usage.jsonl")).unwrap();
    assert!(
        usage.contains("\"tool\": \"check-file-scale\"")
            && usage.contains("\"tool\": \"check-rust-tooling\"")
    );
}

#[test]
fn a_refused_check_is_recorded_refused_and_a_failed_self_test_refuses() {
    let dir = repo("refused");
    assert_eq!(
        cli(&owned(&["file-scale", &dir.display().to_string()]), &dir).code,
        1
    );
    let usage = std::fs::read_to_string(dir.join(".git/tool-usage.jsonl")).unwrap();
    assert!(usage.contains("\"outcome\": \"refused\""));
    assert_eq!(
        super::Outcome::selftest(false, "ok", "bad".to_owned()).stderr,
        "bad"
    );
    assert_eq!(
        super::Outcome::selftest(true, "ok", "bad".to_owned()).stdout,
        "ok"
    );
}

