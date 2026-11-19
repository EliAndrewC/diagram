//! The delta's rules on fixture repositories; its answers against the Python over recorded commits are `m:t063-slice2`.

use std::path::Path;
use std::process::Command;

use super::{cat_blobs, cli, compute, engine_key, engine_key_worktree, is_engine};

fn git(dir: &Path, args: &[&str]) -> String {
    let done = Command::new("git")
        .arg("-C")
        .arg(dir)
        .args(args)
        .output()
        .unwrap();
    assert!(done.status.success(), "{args:?}");
    String::from_utf8_lossy(&done.stdout).trim().to_owned()
}

fn put(dir: &Path, rel: &str, text: &str) {
    let path = dir.join(rel);
    std::fs::create_dir_all(path.parent().unwrap()).unwrap();
    std::fs::write(path, text).unwrap();
}

fn commit(dir: &Path) {
    git(dir, &["add", "-A"]);
    git(dir, &["commit", "-qm", "c"]);
}

/// A repository with the real `codeid.py`, one engine module and a branch `base` at its first commit.
fn repo(tag: &str) -> l7r_guard::shared::tempdir::TempDir {
    let dir = l7r_guard::shared::tempdir::TempDir::new(&format!("gate-delta-{tag}"));
    std::fs::create_dir_all(dir.join("scripts/gates")).unwrap();
    // the repository `git init -b main` and the two settings make, written as git writes them, and `base` below as `git branch` writes
    // it: four processes saved a test (feature 449 T167, each test under FR-008's tenth of a second)
    put(&dir, ".git/HEAD", "ref: refs/heads/main\n");
    // `maintenance.auto` off: each commit started `git maintenance run --auto`, a process more (feature 449 T167)
    put(&dir, ".git/config", "[core]\n\trepositoryformatversion = 0\n\tfilemode = true\n\tbare = false\n[user]\n\temail = t@t\n\tname = t\n[commit]\n\tgpgsign = false\n[maintenance]\n\tauto = false\n");
    for sub in ["objects", "refs/heads", "refs/tags"] {
        std::fs::create_dir_all(dir.join(".git").join(sub)).unwrap();
    }
    let real = Path::new(env!("CARGO_MANIFEST_DIR")).join("../../../../scripts");
    std::fs::copy(
        real.join("gates/codeid.py"),
        dir.join("scripts/gates/codeid.py"),
    )
    .unwrap();
    put(&dir, "l7r/diagram/m.py", "def f():\n    return 1\n");
    put(&dir, "docs/a.md", "a\n");
    commit(&dir);
    let head = std::fs::read_to_string(dir.join(".git/refs/heads/main")).unwrap();
    put(&dir, ".git/refs/heads/base", &head);
    dir
}

fn delta(dir: &Path) -> serde_json::Value {
    serde_json::from_str(&compute(dir, "base", "python3").unwrap()).unwrap()
}

#[test]
fn every_path_kind_is_pinned() {
    for path in [
        "l7r/diagram/pipeline/gencache.py",
        "pool/hamlets/i/i.gen.py",
        "pool/hamlets/i/i.json",
        "legacy-hand-authored-pool/x.gen.py",
        "rust/phases/src/field.rs",
        "rust/phases/Cargo.toml",
        "rust/phases/Cargo.lock",
    ] {
        assert!(is_engine(path), "{path}");
    }
    for path in [
        "l7r/diagram/ci/dispatch.py",
        "tests/pipeline/t.py",
        "pool/hamlets/i/i.notes.md",
        "pool/hamlets/i/i.py",
        "Makefile",
        "pyproject.toml",
        "scripts/gates/codeid.py",
        "l7r/diagram/interactive/assets/page.js",
        "docs/a.md",
        "rust/phases/README.md",
    ] {
        assert!(!is_engine(path), "{path}");
    }
}

#[test]
fn the_delta_is_our_commits_and_what_they_changed_in_what_runs() {
    let dir = repo("delta");
    assert_eq!(delta(&dir)["files"], serde_json::json!([]));
    put(&dir, "docs/a.md", "b\n");
    commit(&dir);
    assert_eq!(delta(&dir)["engine"], serde_json::json!([]));
    put(
        &dir,
        "l7r/diagram/m.py",
        "\"\"\"doc\"\"\"\n\n# comment\ndef f():\n    return 1\n",
    );
    commit(&dir);
    let wording = delta(&dir);
    assert_eq!(
        wording["files"],
        serde_json::json!(["docs/a.md", "l7r/diagram/m.py"])
    );
    assert_eq!(wording["engine"], serde_json::json!([]),);
}

/// The second half of the delta's test, on a repository of its own (feature 449 T167: the two halves read nothing of each other's, and
/// together they took over FR-008's tenth of a second).
#[test]
fn the_delta_names_each_engine_path_that_changed_and_its_base() {
    let dir = repo("delta-engine");
    put(&dir, "l7r/diagram/m.py", "def f():\n    return 2\n");
    put(&dir, "l7r/diagram/added.py", "x = 1\n");
    put(&dir, "pool/a.json", "{}\n");
    commit(&dir);
    assert_eq!(
        delta(&dir)["engine"],
        serde_json::json!(["l7r/diagram/added.py", "l7r/diagram/m.py", "pool/a.json"])
    );
    assert_eq!(delta(&dir)["base"], git(&dir, &["rev-parse", "base"]));
}

#[test]
fn the_key_moves_with_what_runs_and_the_worktree_key_equals_the_tree_key() {
    let dir = repo("key");
    let head = engine_key(&dir, "HEAD", "python3").unwrap();
    assert_eq!(engine_key_worktree(&dir, "python3").unwrap(), head);
    put(&dir, "docs/a.md", "b\n");
    commit(&dir);
    assert_eq!(engine_key(&dir, "HEAD", "python3").unwrap(), head,);
}

/// A stand-in for `python3 codeid.py --ids <file>...` that ids a file by its lines with `#` comments and blank lines dropped: the real
/// `codeid.py` is 30 ms a start, and the key's tests that follow ask it twice or more, over FR-008's tenth of a second (feature 449 T167);
/// the real one is asked above and in the delta's tests, and the stamp's self-test holds it to its own rules.
fn ids(dir: &Path) -> String {
    let path = dir.join("ids");
    l7r_gate_core::write_executable(
        &path,
        "#!/bin/sh\nshift; shift; for f in \"$@\"; do sed 's/ *#.*//;/^$/d' \"$f\" | sha256sum | cut -c1-64; done\n",
    );
    path.to_string_lossy().into_owned()
}

/// The second part of the key's test, on a repository of its own (feature 449 T167: it reads nothing the first part wrote).
#[test]
fn a_comment_alone_keeps_the_worktree_key() {
    let dir = repo("key-comment");
    let py = ids(&dir);
    let head = engine_key(&dir, "HEAD", &py).unwrap();
    put(
        &dir,
        "l7r/diagram/m.py",
        "# a comment\ndef f():\n    return 1\n",
    );
    assert_eq!(engine_key_worktree(&dir, &py).unwrap(), head,);
}

/// The last part of the key's test, on a repository of its own (feature 449 T167, as above).
#[test]
fn an_untracked_engine_file_moves_the_key_and_its_commit_keeps_it() {
    let dir = repo("key-moved");
    let py = ids(&dir);
    let head = engine_key(&dir, "HEAD", &py).unwrap();
    put(&dir, "rust/phases/a.rs", "fn f() {} // c\n");
    put(&dir, "pool/a.json", "{}\n");
    let moved = engine_key_worktree(&dir, &py).unwrap();
    assert_ne!(moved, head, "an untracked engine file counts");
    commit(&dir);
    assert_eq!(engine_key(&dir, "HEAD", &py).unwrap(), moved);
    assert_eq!(engine_key_worktree(&dir, &py).unwrap(), moved,);
    assert_eq!(engine_key(&dir, "HEAD", &py).unwrap(), moved);
    assert!(engine_key(&dir, "no-such-tree", &py).is_err());
}

#[test]
fn a_tree_with_no_engine_keys_on_nothing() {
    let dir = l7r_guard::shared::tempdir::TempDir::new("gate-delta-empty");
    git(&dir, &["init", "-q"]);
    assert_eq!(
        engine_key_worktree(&dir, "python3").unwrap(),
        l7r_guard::shared::sha256::hex(b"")
    );
}

#[test]
fn a_blob_git_cannot_find_is_none_and_others_are_whole() {
    let dir = repo("blobs");
    let names = [
        "HEAD:docs/a.md".to_owned(),
        "HEAD:no-such".to_owned(),
        "HEAD:docs/a.md".to_owned(),
    ];
    assert_eq!(
        cat_blobs(&dir, &names).unwrap(),
        [Some(b"a\n".to_vec()), None, Some(b"a\n".to_vec())]
    );
    assert_eq!(cat_blobs(&dir, &[]).unwrap(), Vec::<Option<Vec<u8>>>::new());
    assert!(super::git_fed(&dir, &["no-such-verb"], String::new()).is_err());
}

#[test]
fn the_command_line_answers_and_refuses() {
    let dir = repo("cli");
    let ask = |args: &[&str]| {
        cli(
            &args.iter().map(|s| (*s).to_owned()).collect::<Vec<_>>(),
            &dir,
            "python3",
            &mut "l7r/a.py
docs/b.md
"
            .as_bytes(),
        )
    };
    assert_eq!(ask(&["key"]).stdout.trim().len(), 64);
    assert_eq!(
        ask(&["key", "worktree"]).stdout,
        ask(&["key", "HEAD"]).stdout
    );
    assert_eq!(ask(&["compute", "base"]).code, 0);
    assert_eq!(ask(&["engine-paths"]).stdout, "l7r/a.py\n");
    assert_eq!(ask(&["nonsense"]).code, 2);
    let bad = ask(&["compute", "no-such-ref"]);
    assert_eq!(bad.code, 1);
    assert!(bad.stderr.contains("l7r-gate delta: git merge-base"));
}

#[test]
fn the_route_and_its_reason() {
    use super::Delta;
    let files: Vec<String> = (0..6).map(|n| format!("l7r/{n}.py")).collect();
    let d = Delta {
        base: String::new(),
        files: files.clone(),
        engine: files,
    };
    assert_eq!(d.route(), "GATED");
    assert!(
        d.reason()
            .starts_with("6 engine path(s) in our delta: l7r/0.py, ")
            && d.reason().ends_with("(+2 more)")
    );
    assert_eq!(Delta::default().route(), "DIRECT");
    assert!(Delta::default().reason().contains("nothing to push"));
    let docs = Delta {
        files: vec!["a.md".to_owned()],
        ..Delta::default()
    };
    assert!(docs.reason().contains("none of them diagram engine code"));
}

#[test]
fn a_short_engine_list_names_every_path_and_no_more() {
    let d = super::Delta {
        base: "b".to_owned(),
        files: vec!["l7r/a.py".to_owned()],
        engine: vec!["l7r/a.py".to_owned()],
    };
    assert_eq!(d.reason(), "1 engine path(s) in our delta: l7r/a.py");
}
