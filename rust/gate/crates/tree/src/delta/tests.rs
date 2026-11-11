//! The delta's rules on fixture repositories; its answers against the Python over recorded commits are `m:t063-slice2`.

use std::path::{Path, PathBuf};
use std::process::Command;

use super::{
    cat_blobs, cli, compute, coverage_scope, engine_key, engine_key_worktree, is_engine,
    pytest_words,
};

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
fn repo(tag: &str) -> PathBuf {
    let dir = std::env::temp_dir().join(format!("l7r-gate-delta-{tag}-{}", std::process::id()));
    let _ = std::fs::remove_dir_all(&dir);
    std::fs::create_dir_all(dir.join("scripts/gates")).unwrap();
    git(&dir, &["init", "-q", "-b", "main"]);
    git(&dir, &["config", "user.email", "t@t"]);
    git(&dir, &["config", "user.name", "t"]);
    let real = Path::new(env!("CARGO_MANIFEST_DIR")).join("../../../../scripts");
    std::fs::create_dir_all(dir.join("scripts/hooks/lib")).unwrap();
    for rel in ["gates/codeid.py", "hooks/lib/usage_log.py"] {
        std::fs::copy(real.join(rel), dir.join("scripts").join(rel)).unwrap();
    }
    put(&dir, "l7r/diagram/m.py", "def f():\n    return 1\n");
    put(&dir, "docs/a.md", "a\n");
    commit(&dir);
    git(&dir, &["branch", "base"]);
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
    put(
        &dir,
        "l7r/diagram/m.py",
        "# a comment\ndef f():\n    return 1\n",
    );
    assert_eq!(engine_key_worktree(&dir, "python3").unwrap(), head,);
    put(&dir, "rust/phases/a.rs", "fn f() {} // c\n");
    put(&dir, "pool/a.json", "{}\n");
    let moved = engine_key_worktree(&dir, "python3").unwrap();
    assert_ne!(moved, head, "an untracked engine file counts");
    commit(&dir);
    assert_eq!(engine_key(&dir, "HEAD", "python3").unwrap(), moved);
    assert_eq!(engine_key_worktree(&dir, "python3").unwrap(), moved,);
    assert_eq!(engine_key(&dir, "HEAD", "python3").unwrap(), moved);
    assert!(engine_key(&dir, "no-such-tree", "python3").is_err());
}

#[test]
fn a_tree_with_no_engine_keys_on_nothing() {
    let dir = std::env::temp_dir().join(format!("l7r-gate-delta-empty-{}", std::process::id()));
    let _ = std::fs::remove_dir_all(&dir);
    std::fs::create_dir_all(&dir).unwrap();
    git(&dir, &["init", "-q"]);
    assert_eq!(
        engine_key_worktree(&dir, "python3").unwrap(),
        l7r_guard::shared::sha256::hex(b"")
    );
}

#[test]
fn coverage_follows_the_diff_and_needs_no_origin() {
    let dir = repo("cov");
    assert_eq!(coverage_scope(&dir, "base").unwrap(), Vec::<String>::new());
    put(&dir, "l7r/diagram/a/x.py", "x = 1\n");
    put(&dir, "l7r/diagram/tests/t.py", "x = 1\n");
    put(&dir, "docs/x.py", "x = 1\n");
    assert_eq!(
        coverage_scope(&dir, "no-such-ref").unwrap(),
        ["l7r/diagram/a"]
    );
    commit(&dir);
    put(&dir, "l7r/b/y.py", "y = 1\n");
    assert_eq!(
        coverage_scope(&dir, "base").unwrap(),
        ["l7r/b", "l7r/diagram/a"]
    );
    assert_eq!(pytest_words(&[]), "-o addopts= --no-cov\n");
    assert_eq!(
        pytest_words(&["a".to_owned(), "b".to_owned()]),
        "-o addopts=--cov=a --cov=b\n"
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
    assert_eq!(ask(&["cov-scope", "base"]).stdout, "-o addopts= --no-cov\n");
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
