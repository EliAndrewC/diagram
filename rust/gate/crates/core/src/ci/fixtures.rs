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

/// A scratch directory of the test, removed when it is dropped.
pub fn scratch(tag: &str) -> l7r_guard::shared::tempdir::TempDir {
    l7r_guard::shared::tempdir::TempDir::new(&format!("gate-ci-{tag}"))
}

/// A repository, with `origin/main` at its first commit, and one engine file.
pub fn repo(tag: &str) -> l7r_guard::shared::tempdir::TempDir {
    let dir = scratch(tag);
    git(&dir, &["init", "-q", "-b", "main"]);
    git(&dir, &["config", "user.email", "t@t"]);
    git(&dir, &["config", "user.name", "t"]);
    commit(&dir, "l7r/diagram/m.py", "x = 1\n");
    git(&dir, &["update-ref", "refs/remotes/origin/main", "HEAD"]);
    dir
}

/// A stand-in for `python3`: the `.py` ids by a hash of the bytes, `--holding` from `<feature>/.holding`, and a verdict by `<feature>/.faithful`.
#[must_use]
///
/// # Panics
///
/// Where the fixture cannot be made, which fails the test that asked for it.
pub fn python(dir: &Path) -> String {
    let path = dir.join(".git/stand-in-python");
    std::fs::write(&path, "#!/bin/bash\ncase \"$1\" in\n *codeid.py) [ \"$2\" = --debug-free-equal ] && { echo x >> \"$0.calls\"; shift 2; while [ $# -gt 0 ]; do echo 0; shift 2; done; exit 0; }; if [ \"$2\" = --semantic ]; then shift 3; for f in \"$@\"; do printf '1\\nz'; done; else shift 2; for f in \"$@\"; do sha1sum \"$f\" | cut -d' ' -f1; done; fi;;\n *speckit-todo.py) cat \"$3/.holding\" 2>/dev/null; true;;\n *hm_arbiter.py) [ -f \"$3/.faithful\" ];;\nesac\n").unwrap();
    Command::new("chmod").arg("+x").arg(&path).status().unwrap();
    path.to_string_lossy().into_owned()
}
