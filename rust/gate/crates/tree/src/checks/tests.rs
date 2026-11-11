//! Which retained check a change starts.

use std::process::Command;

use super::needs;

fn repo(tag: &str) -> l7r_guard::shared::tempdir::TempDir {
    let dir = l7r_gate_core::checks::scratch(tag);
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

fn put(dir: &std::path::Path, rel: &str, text: &str) {
    let path = dir.join(rel);
    std::fs::create_dir_all(path.parent().unwrap()).unwrap();
    std::fs::write(path, text).unwrap();
}

fn commit(dir: &std::path::Path) {
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

fn based(dir: &std::path::Path) {
    assert!(Command::new("git")
        .arg("-C")
        .arg(dir)
        .args(["update-ref", "refs/remotes/origin/main", "HEAD"])
        .output()
        .unwrap()
        .status
        .success());
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
    let ran = |dir: &std::path::Path| four.map(|c| needs(c, dir) == 0);
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
    alone("scripts/record/access_tags.py", [false, true, false, false]);
    alone(
        "rust/gate/crates/downloads/src/record/access_tags.rs",
        [false, false, true, false],
    );
    alone(
        "rust/gate/crates/downloads/src/record/downloads/parse.rs",
        [false, false, true, false],
    );
    alone(
        "scripts/gates/check-entry-headings.py",
        [false, true, false, true],
    );
    alone(
        "scripts/gates/check-duplicate-defs.py",
        [true, true, false, false],
    );
    put(
        &dir,
        "rust/gate/crates/checks/src/checks/partial_citations.rs",
        "\n",
    );
    assert_eq!(ran(&dir), [false, false, true, false]);
    assert_eq!(needs("something-else", &dir), 0);
    assert_eq!(needs("function-cap", &repo("needs-base")), 0);
}

#[test]
fn needs_run_is_needs_exit_zero_and_the_top_is_the_repository() {
    let dir = repo("needs-run");
    assert!(super::needs_run("function-cap", &dir));
    assert!(crate::top().join("rust").is_dir());
}
