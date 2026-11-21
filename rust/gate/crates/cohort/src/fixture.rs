//! The repositories the crate's tests build (feature 449 T167): a history written by one `git fast-import`.

use std::fmt::Write as _;
use std::io::Write as _;
use std::process::{Command, Stdio};

use l7r_gate_core::ci::fixtures::{git, scratch};
use l7r_shared::tempdir::TempDir;

/// A repository whose history is `commits` on `main`, each a commit of its files, with `origin/main` at the commit `main_at` counts and
/// the work tree and index at `main`; each commit's id, oldest first. Git's `fast-import` writes the whole history in one process, and
/// the repository's directory is written as `git init` writes the part git reads (its `HEAD`, `objects/`, `refs/` and a config naming
/// the committer), where `ci`'s `repo` and the commits after it started git a dozen times: about 5 ms a process here, and a test's
/// tenth of a second under FR-008 (feature 449 T167).
pub fn built(tag: &str, commits: &[&[(&str, &str)]], main_at: usize) -> (TempDir, Vec<String>) {
    let root = scratch(tag);
    for dir in [".git/objects", ".git/refs/heads", ".git/refs/tags"] {
        std::fs::create_dir_all(root.join(dir)).unwrap();
    }
    std::fs::write(root.join(".git/HEAD"), "ref: refs/heads/main\n").unwrap();
    std::fs::write(
        root.join(".git/config"),
        "[core]\n\trepositoryformatversion = 0\n\tfilemode = true\n\tbare = false\n[user]\n\temail = t@t\n\tname = t\n",
    )
    .unwrap();
    let mut stream = String::new();
    for (n, files) in commits.iter().enumerate() {
        let _ = write!(
            stream,
            "commit refs/heads/main\nmark :{}\ncommitter t <t@t> {} +0000\ndata 1\nc\n",
            n + 1,
            1_763_000_000 + n
        );
        for (path, body) in *files {
            let _ = write!(
                stream,
                "M 100644 inline {path}\ndata {}\n{body}\n",
                body.len()
            );
        }
    }
    let _ = write!(
        stream,
        "reset refs/remotes/origin/main\nfrom :{}\n\n",
        main_at + 1
    );
    let mut child = Command::new("git")
        .arg("-C")
        .arg(&root)
        .args(["fast-import", "--quiet", "--export-marks=.git/marks"])
        .stdin(Stdio::piped())
        .spawn()
        .unwrap();
    child
        .stdin
        .take()
        .unwrap()
        .write_all(stream.as_bytes())
        .unwrap();
    assert!(child.wait().unwrap().success());
    git(&root, &["reset", "-q", "--hard"]);
    // `:<mark> <id>` a line, in mark order
    let mut marks: Vec<(usize, String)> = std::fs::read_to_string(root.join(".git/marks"))
        .unwrap()
        .lines()
        .filter_map(|l| l.strip_prefix(':')?.split_once(' '))
        .map(|(m, id)| (m.parse().unwrap(), id.to_owned()))
        .collect();
    marks.sort();
    (root, marks.into_iter().map(|(_, id)| id).collect())
}

/// A commit's id as `git rev-parse --short` gives it in a repository this small: its first seven characters.
pub fn short(id: &str) -> String {
    id[..7].to_owned()
}
