//! The shared helpers and the command line.

use std::process::Command;

use super::cli;

pub(super) fn repo(tag: &str) -> l7r_guard::shared::tempdir::TempDir {
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
    for name in ["file-scale", "stale-dirs"] {
        assert_eq!(cli(&owned(&[name, "--selftest"]), &dir).code, 0, "{name}");
    }
}

/// The self-tests that read a record, a registry or a delta of their own, by name (split from the test above, feature 449 T167:
/// together they took 104 ms against FR-008's tenth of a second).
#[test]
fn the_record_registry_and_delta_checks_answer_their_self_tests_by_name() {
    let dir = repo("cli-selftests");
    for name in [
        "research-pointers",
        "house-style-delta",
        // the registry's check (feature 449 T149): a tree with no engine runs its form half
        "entry-headings",
    ] {
        assert_eq!(cli(&owned(&[name, "--selftest"]), &dir).code, 0, "{name}");
    }
}

/// The remaining checks by name, and each run recorded (split from the test above, feature 449 T167: the two halves together took
/// 104 ms against FR-008's tenth of a second); `file-scale` is asked here again so its run is recorded beside `rust-tooling`'s.
#[test]
fn a_tree_whose_registry_does_not_load_is_refused_and_each_run_is_recorded() {
    let dir = repo("cli-recorded");
    assert_eq!(cli(&owned(&["file-scale", "--selftest"]), &dir).code, 0);
    // a tree whose registry does not load: refused, and no run recorded, as the Python raised before it recorded one (feature 449 T149)
    let engine = repo("cli-engine");
    std::fs::create_dir_all(engine.join("l7r")).unwrap();
    let crashed = cli(&owned(&["entry-headings", "--selftest"]), &engine);
    assert!(crashed.code == 1 && !engine.join(".git/tool-usage.jsonl").exists());
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
