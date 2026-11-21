//! Which retained check a change starts.

use std::process::Command;

use super::needs;

fn repo(tag: &str) -> l7r_shared::tempdir::TempDir {
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
    // each path alone, read by the rule `needs` asks of every changed path (feature 449 T160): put in the tree, the 17 rows asked git
    // three times a check, 265 git calls and 0.40 s against FR-008's tenth of a second; the tree's own paths reach the rule above and
    // below
    let alone = |rel: &str, want: [bool; 4]| {
        assert_eq!(four.map(|c| super::reads(c, rel)), want, "{rel}");
    };
    alone("tools/a.py", [false, false, false, false]);
    alone("scripts/a.py", [false, true, false, false]);
    alone("tests/a.py", [true, true, false, false]);
    alone("l7r/a.py", [true, true, false, false]);
    alone("l7r/diagram/interactive/a.py", [true, true, false, false]);
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
        "l7r/diagram/interactive/assets/siblings.json",
        [false, false, false, true],
    );
    alone(
        "rust/gate/crates/registry/src/kinds.rs",
        [false, false, false, true],
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
