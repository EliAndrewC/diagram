//! A test's scratch worktrees: `<clones>/git-clone`, a repository with one commit on `main`, and its worktrees aged by hand.

use std::path::{Path, PathBuf};
use std::process::Command;
use std::time::{Duration, SystemTime};

/// Run git in `dir`; panics where it fails.
pub(crate) fn git(dir: &Path, args: &[&str]) {
    let ok = Command::new("git")
        .arg("-C")
        .arg(dir)
        .args(["-c", "user.name=t", "-c", "user.email=t@t"])
        .args(args)
        .output()
        .unwrap();
    assert_eq!(ok.status.code(), Some(0), "{args:?}");
}

/// Set every entry under `path` (and `path`) `days` ago.
pub(crate) fn age(path: &Path, days: u64) {
    let when = SystemTime::now() - Duration::from_secs(days * 86_400);
    let mut stack = vec![path.to_path_buf()];
    while let Some(p) = stack.pop() {
        if p.is_dir() {
            stack.extend(std::fs::read_dir(&p).unwrap().flatten().map(|e| e.path()));
        }
        std::fs::File::open(&p).unwrap().set_modified(when).unwrap();
    }
}

/// A detached worktree on `main` of `<clones>/git-clone` (a repository with one commit, made on the first call) at `tree`.
pub(crate) fn worktree(clones: &Path, tree: &Path) -> PathBuf {
    let clone = clones.join("git-clone");
    if !clone.join(".git").exists() {
        std::fs::create_dir_all(&clone).unwrap();
        git(&clone, &["init", "-q", "-b", "main"]);
        std::fs::write(clone.join("f"), "x").unwrap();
        git(&clone, &["add", "f"]);
        git(&clone, &["commit", "-qm", "one"]);
    }
    git(
        &clone,
        &[
            "worktree",
            "add",
            "-q",
            "--detach",
            tree.to_str().unwrap(),
            "main",
        ],
    );
    tree.to_path_buf()
}

/// A clean worktree at `tree`, it and the clone's worktree records idle `days`.
pub(crate) fn clean(clones: &Path, tree: &Path, days: u64) -> PathBuf {
    worktree(clones, tree);
    age(tree, days);
    age(&clones.join("git-clone/.git/worktrees"), days);
    tree.to_path_buf()
}
