//! The walk, the framing and the two configurations; the hashes against the Python are `m:t72-state`.

use std::path::{Path, PathBuf};
use std::process::Command;

use super::{
    cli, config_hash, content_hash, makefile_test_config, pyproject_test_config, under_each,
};

fn scratch(tag: &str) -> PathBuf {
    let dir = std::env::temp_dir().join(format!("l7r-gate-hash-{tag}-{}", std::process::id()));
    let _ = std::fs::remove_dir_all(&dir);
    std::fs::create_dir_all(&dir).unwrap();
    dir
}

fn put(dir: &Path, rel: &str, text: &str) {
    let path = dir.join(rel);
    std::fs::create_dir_all(path.parent().unwrap()).unwrap();
    std::fs::write(path, text).unwrap();
}

fn stand_in(dir: &Path, body: &str) -> String {
    let path = dir.join("stand-in");
    std::fs::write(&path, format!("#!/bin/bash\n{body}\n")).unwrap();
    Command::new("chmod").arg("+x").arg(&path).status().unwrap();
    path.to_string_lossy().into_owned()
}

#[test]
fn a_tree_is_sorted_as_paths_a_link_is_not_descended_and_a_named_file_stands_alone() {
    let dir = scratch("walk");
    put(&dir, "t/b.txt", "1");
    put(&dir, "t/a/z.txt", "1");
    put(&dir, "elsewhere/x.txt", "1");
    std::os::unix::fs::symlink(dir.join("elsewhere"), dir.join("t/link")).unwrap();
    let rels: Vec<String> = under_each(&dir, &["t", "named"])
        .iter()
        .map(|p| p.strip_prefix(&dir).unwrap().display().to_string())
        .collect();
    assert_eq!(rels, ["t/a", "t/a/z.txt", "t/b.txt", "t/link", "named"]);
    assert!(under_each(&dir.join("no-such"), &[]).is_empty());
}

#[test]
fn each_file_is_its_path_then_its_content_and_a_python_file_what_runs() {
    let dir = scratch("content");
    put(&dir, "a.txt", "AA");
    put(&dir, "b.py", "ignored");
    put(&dir, "__pycache__/c.txt", "no");
    let files = [
        dir.join("a.txt"),
        dir.join("b.py"),
        dir.join("__pycache__/c.txt"),
        dir.join("gone"),
    ];
    let py = stand_in(&dir, "printf '3\\nDMP'");
    assert_eq!(
        content_hash(&dir, &files, true, &py).unwrap(),
        b"a.txtAAb.pyDMP"
    );
    assert_eq!(
        content_hash(&dir, &files[..1], false, "/no/such").unwrap(),
        b"a.txtAA",
    );
}

#[test]
fn a_python_that_cannot_answer_fails_the_hash() {
    let dir = scratch("bad");
    put(&dir, "b.py", "x");
    let files = [dir.join("b.py")];
    for (body, says) in [
        ("echo no >&2; exit 1", "could not read"),
        ("printf 'no newline'", "framed"),
        ("printf 'x\\n'", "framed"),
        ("printf '9\\nab'", "short"),
        ("exit 0", "answered short"),
        ("printf '1\\nx1\\ny'", "answered short"),
    ] {
        let py = stand_in(&dir, body);
        let why = content_hash(&dir, &files, false, &py).unwrap_err();
        assert!(why.contains(says), "{why}");
    }
    assert!(content_hash(&dir, &files, false, "/no/such/python").is_err());
}

#[test]
fn a_kept_form_starts_no_python_and_an_old_unused_one_goes() {
    let dir = scratch("kept");
    assert!(Command::new("git")
        .arg("-C")
        .arg(&dir)
        .args(["init", "-q"])
        .status()
        .unwrap()
        .success());
    put(&dir, "b.py", "x");
    let files = [dir.join("b.py")];
    let py = stand_in(&dir, "printf '3\\nDMP'");
    let first = content_hash(&dir, &files, false, &py).unwrap();
    assert_eq!(
        content_hash(&dir, &files, false, "/no/such/python").unwrap(),
        first
    );
    assert!(content_hash(&dir, &files, true, "/no/such/python").is_err());
    let kept = dir.join(".git/semantic-dumps/strip");
    let (old, fresh) = (kept.join("old"), kept.join("fresh"));
    std::fs::write(&old, "x").unwrap();
    std::fs::write(&fresh, "x").unwrap();
    let long_ago = std::time::SystemTime::now() - super::KEPT_FOR * 2;
    std::fs::File::options()
        .write(true)
        .open(&old)
        .unwrap()
        .set_modified(long_ago)
        .unwrap();
    put(&dir, "b.py", "changed");
    content_hash(&dir, &files, false, &py).unwrap();
    assert!(!old.exists() && fresh.exists());
    assert_eq!(std::fs::read_dir(&kept).unwrap().count(), 3);
}

#[test]
fn the_makefile_s_test_configuration_is_the_recipes_and_the_variables_they_close_over() {
    let text = "A = 1 ## help\nB = $(A) $(C) $(C)\nC := 2\nUNUSED = 3\nother:\n\tno $(UNUSED)\ntest:  ## run\n\tgo $(B)\n## a comment inside\n\tmore\nT = x\ntest-full: A\n\tall\nX: Y = 1\n";
    assert_eq!(
        makefile_test_config(text),
        "test:\n\tgo $(B)\n\tmore\ntest-full: A\n\tall\nA = 1 ## help\nB = $(A) $(C) $(C)\nC := 2"
    );
    assert_eq!(makefile_test_config("test := 1\n"), "");
}

#[test]
fn only_the_pytest_and_coverage_tables_of_pyproject_count() {
    let text = "[tool.ruff]\nx = 1\n[tool.pytest.ini_options]\na = 1\n[[tool.coverage.x]]\nb = 2\n[project]\nc = 3\n";
    assert_eq!(
        pyproject_test_config(text),
        "[tool.pytest.ini_options]\na = 1\n[[tool.coverage.x]]\nb = 2"
    );
}

#[test]
fn the_config_hash_moves_with_what_decides_and_counts_a_missing_file_as_empty() {
    let dir = scratch("config");
    let py = stand_in(&dir, "shift 3; for f in \"$@\"; do printf '1\\nz'; done");
    let empty = config_hash(&dir, &py).unwrap();
    put(&dir, "Makefile", "other:\n\tx\n");
    assert_eq!(
        config_hash(&dir, &py).unwrap(),
        l7r_guard::shared::sha256::hex(b"Makefilepyproject.toml"),
    );
    assert_eq!(empty, config_hash(&dir, &py).unwrap());
    put(&dir, "requirements.txt", "a==1\n");
    let locked = config_hash(&dir, &py).unwrap();
    assert_ne!(locked, empty);
    put(&dir, "l7r/diagram/ci/m.py", "x");
    assert_ne!(config_hash(&dir, &py).unwrap(), locked);
    assert_eq!(cli(&[], &dir, &py).stdout.trim().len(), 64);
    assert_eq!(cli(&[], &dir, "/no/such/python").code, 1);
    assert_eq!(cli(&["x".to_owned()], &dir, &py).code, 2);
}
