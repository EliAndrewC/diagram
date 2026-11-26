//! What the remote path's tests share: a repository with an `origin/main`, a stand-in for Python, and the two boundaries faked, the `git` underneath real.

use std::path::Path;
use std::process::Command;

/// # Panics
///
/// Where the fixture cannot be made, which fails the test that asked for it.
#[expect(
    clippy::must_use_candidate,
    reason = "a fixture runs git for what it does; most callers drop what it printed"
)]
pub fn git(dir: &Path, args: &[&str]) -> String {
    let done = Command::new("git")
        .arg("-C")
        .arg(dir)
        .args(args)
        .output()
        .unwrap();
    assert!(done.status.success(),);
    String::from_utf8_lossy(&done.stdout).trim().to_owned()
}

/// # Panics
///
/// Where the fixture cannot be made, which fails the test that asked for it.
pub fn put(dir: &Path, rel: &str, text: &str) {
    let path = dir.join(rel);
    std::fs::create_dir_all(path.parent().unwrap()).unwrap();
    std::fs::write(path, text).unwrap();
}

pub fn commit(dir: &Path, rel: &str, text: &str) {
    put(dir, rel, text);
    git(dir, &["add", "-A"]);
    git(dir, &["commit", "-qm", "c"]);
}

/// `rel` committed in `dir` and `task`'s Edit of it on `feature`'s event log, half a second after the commit: a started task's
/// work the push carries, which is what holds it (feature 451 T254, `shared::speckit::touch`).
///
/// # Panics
///
/// Where the fixture cannot be made, which fails the test that asked for it.
pub fn edited(dir: &Path, feature: &str, task: &str, rel: &str) {
    commit(dir, rel, &format!("{task}'s edit\n"));
    let secs: u64 = git(dir, &["log", "-1", "--format=%ct"]).parse().unwrap();
    let (y, m, d, h, mi, s) = l7r_shared::log::civil(secs);
    let path = std::fs::canonicalize(dir).unwrap().join(rel);
    let line = serde_json::json!({"ev": "PostToolUse", "cat": "edit", "task": task,
        "t": format!("{y:04}-{m:02}-{d:02}T{h:02}:{mi:02}:{s:02}.500Z"), "path": path.to_string_lossy()});
    let log = dir.join(format!(".git/l7r-events/{feature}.jsonl"));
    let mut text = std::fs::read_to_string(&log).unwrap_or_default();
    text += &format!("{line}\n");
    put(dir, &format!(".git/l7r-events/{feature}.jsonl"), &text);
}

/// A scratch directory of the test, removed when it is dropped.
pub fn scratch(tag: &str) -> l7r_shared::tempdir::TempDir {
    l7r_shared::tempdir::TempDir::new(&format!("gate-ci-{tag}"))
}

/// A repository, with `origin/main` at its first commit, and one engine file.
pub fn repo(tag: &str) -> l7r_shared::tempdir::TempDir {
    let dir = scratch(tag);
    git(&dir, &["init", "-q", "-b", "main"]);
    git(&dir, &["config", "user.email", "t@t"]);
    git(&dir, &["config", "user.name", "t"]);
    commit(&dir, "l7r/diagram/m.py", "x = 1\n");
    git(&dir, &["update-ref", "refs/remotes/origin/main", "HEAD"]);
    dir
}
