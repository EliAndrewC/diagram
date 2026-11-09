//! The shared helpers and the command line.

use std::process::Command;

use super::{cli, needs, py_lines};

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
fn lines_end_where_python_ends_them() {
    assert_eq!(
        py_lines("a\nb\r\nc\x0cd\u{2028}e").collect::<Vec<_>>(),
        ["a", "b", "c", "d", "e"]
    );
    assert_eq!(py_lines("a\r\rb\n").collect::<Vec<_>>(), ["a", "", "b"]);
    assert_eq!(py_lines("").count(), 0);
}

#[test]
fn a_rust_only_change_starts_none_of_the_python_checks() {
    let dir = repo("needs");
    put(&dir, "rust/a.rs", "fn f() {}\n");
    commit(&dir);
    based(&dir);
    let four = [
        "duplicate-defs",
        "function-cap",
        "partial-citations",
        "entry-headings",
    ];
    let ran = |dir: &std::path::Path| four.map(|c| needs(c, dir).code == 0);
    put(&dir, "rust/a.rs", "fn f() { }\n");
    assert_eq!(ran(&dir), [false, false, false, false]);
    put(&dir, "pyproject.toml", "");
    assert_eq!(ran(&dir), [false, true, false, false]);
    std::fs::remove_file(dir.join("pyproject.toml")).unwrap();
    let alone = |rel: &str, want: [bool; 4]| {
        put(&dir, rel, "x = 1\n");
        assert_eq!(ran(&dir), want);
        std::fs::remove_file(dir.join(rel)).unwrap();
    };
    alone("tools/a.py", [false, false, false, false]);
    alone("scripts/a.py", [false, true, false, false]);
    alone("tests/a.py", [true, true, false, false]);
    alone("l7r/a.py", [true, true, false, false]);
    alone("l7r/diagram/interactive/a.py", [true, true, false, true]);
    alone(
        "l7r/diagram/interactive/assets/modals/hamlet/x.md",
        [false, false, false, true],
    );
    alone("research/x.txt", [false, false, false, false]);
    alone(
        "research/questions/0001-a.html",
        [false, false, false, true],
    );
    alone(
        "research/questions/0001-a.notes.html",
        [false, false, true, true],
    );
    alone(
        "research/sources/010-works-cited/k.html",
        [false, false, true, false],
    );
    alone("research/archive/a/b.json", [false, false, true, false]);
    alone("research/source-access.json", [false, false, true, false]);
    alone("scripts/record/access_tags.py", [false, true, true, false]);
    alone(
        "scripts/gates/check-entry-headings.py",
        [false, true, false, true],
    );
    alone(
        "scripts/gates/check-duplicate-defs.py",
        [true, true, false, false],
    );
    put(&dir, "scripts/gates/check-partial-citations.py", "x = 1\n");
    assert_eq!(ran(&dir), [false, true, true, false]);
    assert_eq!(needs("something-else", &dir).code, 0);
    assert_eq!(needs("function-cap", &repo("needs-base")).code, 0);
}

#[test]
fn each_check_answers_by_name_and_its_run_is_recorded() {
    let dir = repo("cli");
    assert_eq!(cli(&owned(&["nonsense"]), &dir).code, 2);
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
