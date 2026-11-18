//! A reset world is a fresh one (feature 449 T179): after a case that writes, deletes, adds untracked and ignored files, changes modes,
//! the index and `.git`, commits and stashes, the reset world holds every path a fresh world holds, each with its bytes and mode, the
//! same index, HEAD, refs, stash and `git status`; and a world is made anew when the repository moved or a reset step fails.

use std::collections::BTreeMap;
use std::os::unix::fs::PermissionsExt as _;
use std::path::{Path, PathBuf};
use std::time::Duration;

use l7r_guard::shared::tempdir::TempDir;

use super::{beside, ready, release, Held};
use crate::cases::Checkout;

fn git(dir: &Path, args: &[&str]) -> String {
    let out = std::process::Command::new("git")
        .arg("-C")
        .arg(dir)
        .args([
            "-c",
            "user.name=t",
            "-c",
            "user.email=t@t",
            "-c",
            "commit.gpgsign=false",
        ])
        .args(args)
        .output()
        .unwrap();
    let err = String::from_utf8_lossy(&out.stderr);
    assert!(out.status.success(), "{args:?}: {err}");
    String::from_utf8_lossy(&out.stdout).into_owned()
}

/// The empty template directory every git of these tests starts its repositories from: a clone or `init` without git's sample hooks
/// writes, and the world copies, a dozen files fewer (FR-008's tenth of a second).
fn templates(root: &Path) -> PathBuf {
    let t = root.join("templates");
    std::fs::create_dir_all(&t).unwrap();
    t
}

fn sh(dir: &Path, script: &str, templates: &Path) {
    let out = std::process::Command::new("sh")
        .args(["-ec", script])
        .current_dir(dir)
        .env("GIT_TEMPLATE_DIR", templates)
        .env(
            "GIT_CONFIG_PARAMETERS",
            "'user.name=t' 'user.email=t@t' 'commit.gpgsign=false'",
        )
        .output()
        .unwrap();
    let err = String::from_utf8_lossy(&out.stderr);
    assert!(out.status.success(), "{err}");
}

/// A repository of each kind of entry - files, an executable, a link, nested directories, an ignore list - committed, its working tree
/// changed and added to.
fn repo(root: &Path) -> String {
    let repo = root.join("repo");
    std::fs::create_dir_all(&repo).unwrap();
    sh(
        &repo,
        "git init -q; mkdir -p a/deep d; printf 'top\\n' > top.txt; printf 'm\\n' > m.txt; printf 'p\\n' > p.txt; printf 'b\\n' > b.txt
         printf 'x\\n' > a/x.txt; printf 'y\\n' > a/deep/y.txt; printf 'i\\n' > d/i.txt; printf '#!/bin/sh\\n' > run.sh; chmod +x run.sh
         ln -s top.txt link; printf '*.log\\nbuild/\\n' > .gitignore; git add .; git commit -qm one
         printf 'x changed\\n' > a/x.txt; printf 'new\\n' > new.txt",
        &templates(root),
    );
    git(&repo, &["rev-parse", "HEAD"]).trim().to_owned()
}

/// Every path under `world`, its mode and its bytes (a link its target; an index and a reflog by name alone, their bytes holding the
/// times a world was made); and the checkout's index, HEAD, refs, stash and status as git reads them.
fn snapshot(world: &Path) -> Vec<String> {
    let mut out = Vec::new();
    let mut stack = vec![world.to_path_buf()];
    while let Some(d) = stack.pop() {
        for e in std::fs::read_dir(&d).unwrap().flatten() {
            let p = e.path();
            let rel = p.strip_prefix(world).unwrap().display().to_string();
            let meta = std::fs::symlink_metadata(&p).unwrap();
            let what = if meta.file_type().is_symlink() {
                format!("-> {}", std::fs::read_link(&p).unwrap().display())
            } else if meta.is_dir() {
                stack.push(p.clone());
                "dir".to_owned()
            } else if rel.ends_with(".git/index") || rel.contains(".git/logs/") {
                "timed".to_owned()
            } else {
                String::from_utf8_lossy(&std::fs::read(&p).unwrap_or_default()).into_owned()
            };
            out.push(format!("{rel} {:o} {what}", meta.permissions().mode()));
        }
    }
    out.sort();
    let c = world.join("c");
    for args in [
        &["status", "--porcelain", "--ignored"][..],
        &["ls-files", "--stage", "-v"],
        &["for-each-ref"],
    ] {
        out.push(format!("{args:?}: {}", git(&c, args)));
    }
    out
}

fn inode(p: &Path) -> u64 {
    std::os::unix::fs::MetadataExt::ino(&std::fs::metadata(p).unwrap())
}

struct World {
    tmp: TempDir,
    env: Vec<(String, String)>,
    vars: BTreeMap<String, String>,
    co: Checkout,
}

impl World {
    fn new(rev: &str) -> (Self, String) {
        let tmp = TempDir::new("diffrun-reuse");
        let sha = repo(tmp.path());
        let co = Checkout {
            repo: "repo".to_owned(),
            rev: if rev.is_empty() {
                sha.clone()
            } else {
                rev.to_owned()
            },
            into: "c".to_owned(),
            sparse: Vec::new(),
        };
        let blank = templates(tmp.path()).display().to_string();
        let w = World {
            tmp,
            env: std::env::vars()
                .chain([("GIT_TEMPLATE_DIR".to_owned(), blank)])
                .collect(),
            vars: BTreeMap::new(),
            co,
        };
        (w, sha)
    }

    fn at(&self, name: &str) -> PathBuf {
        self.tmp.path().join("work").join(name)
    }

    fn ready(&self, name: &str, held: &mut Option<Held>) {
        ready(
            &self.co,
            (self.tmp.path(), &self.at(name)),
            &self.vars,
            (&self.env, Duration::from_secs(10)),
            held,
        )
        .unwrap();
    }

    /// `name` reset after `case` ran in it, and a fresh world beside it: the two snapshots.
    fn reset_and_fresh(&self, case: &str) -> (Vec<String>, Vec<String>) {
        let mut held = None;
        self.ready("reused", &mut held);
        let made = inode(&self.at("reused/c"));
        sh(&self.at("reused/c"), case, &templates(self.tmp.path()));
        self.ready("reused", &mut held);
        // reset, not made anew: a fresh world would pass the comparison below whatever the reset left
        assert_eq!(inode(&self.at("reused/c")), made);
        assert!(held.is_some());
        let mut fresh = None;
        self.ready("fresh", &mut fresh);
        let both = (snapshot(&self.at("reused")), snapshot(&self.at("fresh")));
        release(held);
        release(fresh);
        both
    }
}

#[test]
fn a_reset_world_is_a_fresh_one_after_a_case_that_writes_deletes_and_adds() {
    let (w, _) = World::new("WORKTREE");
    let (reused, fresh) = w.reset_and_fresh(
        "printf 'TOP\\n' > top.txt
         cp -p a/deep/y.txt ../ref; printf 'Y\\n' > a/deep/y.txt; touch -r ../ref a/deep/y.txt
         rm b.txt; printf 'x again\\n' > a/x.txt; rm new.txt
         printf u > u.txt; mkdir -p nd/sub; printf f > nd/sub/f; printf l > out.log; mkdir build; printf b > build/b
         mkdir ../outdir",
    );
    assert_eq!(reused, fresh);
    // the working tree's change and its untracked file laid again
    assert!(fresh
        .iter()
        .any(|l| l.starts_with("c/a/x.txt ") && l.ends_with("x changed\n")));
    assert!(fresh.iter().any(|l| l.starts_with("c/new.txt ")));
}

#[test]
fn a_reset_world_is_a_fresh_one_after_a_case_that_changes_modes_and_kinds() {
    let (w, _) = World::new("");
    let (reused, fresh) = w.reset_and_fresh(
        "chmod 600 m.txt; chmod 700 a; chmod +x p.txt; chmod -x run.sh
         rm link; printf 'not a link' > link; rm -r d; printf 'now a file' > d; git init -q nested",
    );
    assert_eq!(reused, fresh);
}

#[test]
fn a_reset_world_is_a_fresh_one_after_a_case_that_changes_the_index_commits_and_writes_under_git() {
    let (w, _) = World::new("");
    let (reused, fresh) = w.reset_and_fresh(
        "printf s >> top.txt; git stash -q
         git update-index --assume-unchanged a/x.txt; printf 'X\\n' > a/x.txt
         git update-index --skip-worktree p.txt; printf 'P\\n' > p.txt
         printf u > u2.txt; git add u2.txt; git rm -q --cached m.txt; git commit -qm two
         git branch extra; git tag t1; git config foo.bar 1; mkdir -p .git/rust-checks; printf k > .git/rust-checks/test-a
         printf staged > b.txt; git add b.txt",
    );
    assert_eq!(reused, fresh);
    assert!(!fresh.iter().any(|l| l.contains("ORIG_HEAD")));
}

#[test]
fn a_world_is_made_anew_when_the_repository_moved_or_a_reset_step_fails() {
    let (w, _) = World::new("WORKTREE");
    let mut held = None;
    w.ready("w", &mut held);
    let first = held.as_ref().unwrap().made.refs.clone();
    // the repository's HEAD moved: a fresh clone holds the new one, so the world is made anew at it
    sh(
        &w.tmp.path().join("repo"),
        "printf q > q.txt; git add q.txt; git commit -qm two",
        &templates(w.tmp.path()),
    );
    w.ready("w", &mut held);
    assert_ne!(held.as_ref().unwrap().made.refs, first);
    assert!(w.at("w/c/q.txt").is_file());
    // a path the world did not hold when made: the reset refuses and the world is made anew
    held.as_mut()
        .unwrap()
        .modes
        .insert("/ghost".to_owned(), 0o644);
    w.ready("w", &mut held);
    assert!(!held.as_ref().unwrap().modes.contains_key("/ghost"));
    release(held);
}

#[test]
fn a_world_is_made_anew_when_its_git_or_its_copy_is_gone_and_none_is_held_where_no_copy_can_be_taken(
) {
    let (w, _) = World::new("");
    let mut held = None;
    w.ready("w", &mut held);
    // the kept index keeps the checkout's time: git reads an entry changed within the second the index was written as one that may
    // hide a change only by that time (a copy dated later left a file rewritten at its size in that second unrestored)
    let time = |p: PathBuf| std::fs::metadata(p).unwrap().modified().unwrap();
    assert_eq!(
        time(beside(&w.at("w"), ".git").join("index")),
        time(w.at("w/c/.git/index"))
    );
    // the checkout's `.git` gone, which the reset cannot remove: made anew
    std::fs::remove_dir_all(w.at("w/c/.git")).unwrap();
    w.ready("w", &mut held);
    assert!(w.at("w/c/.git/HEAD").is_file());
    // the kept `.git` gone: made anew
    std::fs::remove_dir_all(beside(&w.at("w"), ".git")).unwrap();
    w.ready("w", &mut held);
    assert!(beside(&w.at("w"), ".git").is_dir());
    // the run's end removes the world and its copies
    release(held);
    assert!(!w.at("w").exists() && !beside(&w.at("w"), ".git").exists());
    // where the copies cannot be taken, the world is made and nothing is held
    std::fs::create_dir_all(w.at("")).unwrap();
    std::fs::write(beside(&w.at("v"), ".git"), "a file").unwrap();
    let mut none = None;
    w.ready("v", &mut none);
    assert!(none.is_none() && w.at("v/c/top.txt").is_file());
    // a checkout that fails is the world's failure
    let bad = Checkout {
        repo: "repo".to_owned(),
        rev: "no-such-rev".to_owned(),
        into: "c".to_owned(),
        sparse: Vec::new(),
    };
    let err = ready(
        &bad,
        (w.tmp.path(), &w.at("x")),
        &w.vars,
        (&w.env, Duration::from_secs(10)),
        &mut None,
    )
    .unwrap_err();
    assert!(err.contains("no-such-rev"), "{err}");
}
