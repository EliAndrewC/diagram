//! The world's checkout (feature 449 T169): a clone of a repository at a side's revision, limited to the paths the cases read.
//!
//! WHY: T168's first `make diff-run` took 307 s while the tool under test ran 0.0-0.2 s a case, because each case's world checked out
//! the whole repository - a fresh world for every case and side (`run.rs`); a sparse checkout limited to the paths the case reads cut a
//! world from 1.3-1.9 s to 0.2 s and the run to 50 s (observed 2026-11-17, T168's harness, `specs/449-rust-codebase/plan-done.md`).
//! That checkout was the harness's own setup script; here a cases file declares it (`world.checkout`) and the runner makes it, so every
//! port's differential gets the sparse world without writing it. The declaration is part of the world's definition, so both keys move
//! when it does (`keys.rs`).
//!
//! SPARSE FOR ITERATING, WHOLE FOR THE RECORD (T169's plan review): a list too narrow for what a case reads fails both sides alike,
//! which the comparison reads as agreement, so only the runs that iterate build sparse worlds; a `--verify` or `--all` run builds whole
//! ones, the list ignored ([`Worlds`]), and the keys keep the two apart (`keys.rs`).
//!
//! A cone-mode sparse checkout: each named directory whole, and the files directly in the root and in each named directory's
//! ancestors (git's `sparse-checkout set --cone`). `rev` `WORKTREE` is `HEAD` with the repository's uncommitted changes and untracked,
//! unignored files inside the cone laid over it, as T168's setup laid them.

use std::collections::BTreeMap;
use std::path::{Path, PathBuf};
use std::time::Duration;

use crate::cases::{fill, Checkout, Worlds};
use crate::run::command;

/// The revision that stands for the repository's working tree.
pub const WORKTREE: &str = "WORKTREE";

struct Git<'a> {
    env: &'a [(String, String)],
    timeout: Duration,
    root: &'a Path,
}

impl Git<'_> {
    /// `git <args>`'s stdout; a git that exits non-zero is the checkout's failure, its stderr's tail with it.
    fn run(&self, args: &[&str]) -> Result<String, String> {
        let mut words = vec!["git".to_owned()];
        words.extend(args.iter().map(|a| (*a).to_owned()));
        let out = command(&words, self.root, self.env, self.timeout)?;
        if out.exit != 0 {
            return Err(format!(
                "world.checkout: `{}` exited {}:\n{}",
                words.join(" "),
                out.exit,
                out.stderr.trim_end()
            ));
        }
        Ok(out.stdout)
    }
}

/// Whether `rel` (a path from the repository's root) is in the cone the `sparse` directories name: every path when none is named.
#[must_use]
pub fn in_cone(rel: &str, sparse: &[String]) -> bool {
    let dir = rel.rsplit_once('/').map_or("", |p| p.0);
    sparse.is_empty()
        || dir.is_empty()
        || sparse.iter().any(|e| {
            rel.starts_with(&format!("{e}/")) || e == dir || e.starts_with(&format!("{dir}/"))
        })
}

/// One path of the working tree laid over the checkout: copied (a link as a link), or removed where the working tree deleted it. What
/// stood at the path in the checkout goes first, a directory too - a working tree may hold a file where `HEAD` holds a directory.
fn lay(src: &Path, laid: &Path) -> std::io::Result<()> {
    match std::fs::symlink_metadata(laid) {
        Ok(m) if m.is_dir() => std::fs::remove_dir_all(laid)?,
        Ok(_) => std::fs::remove_file(laid)?,
        Err(_) => {}
    }
    let Ok(meta) = std::fs::symlink_metadata(src) else {
        return Ok(());
    };
    laid.parent().map_or(Ok(()), std::fs::create_dir_all)?;
    if meta.file_type().is_symlink() {
        std::os::unix::fs::symlink(std::fs::read_link(src)?, laid)
    } else {
        std::fs::copy(src, laid).map(drop)
    }
}

/// The working tree's changes and untracked files inside the cone, each laid over the checkout ([`lay`]).
fn overlay(git: &Git, repo: &str, dest: &Path, sparse: &[String]) -> Result<(), String> {
    let changed = git.run(&[
        "-C",
        repo,
        "diff",
        "HEAD",
        "--name-only",
        "--no-renames",
        "-z",
    ])?;
    let untracked = git.run(&["-C", repo, "ls-files", "-o", "--exclude-standard", "-z"])?;
    for rel in changed.split('\0').chain(untracked.split('\0')) {
        if rel.is_empty() || !in_cone(rel, sparse) {
            continue;
        }
        if let Err(e) = lay(&Path::new(repo).join(rel), &dest.join(rel)) {
            return Err(format!("world.checkout: the working tree's {rel}: {e}"));
        }
    }
    Ok(())
}

/// The checkout made into `world`: the clone, its cone, the revision and, for `WORKTREE`, the working tree's changes over it. `Whole`
/// worlds ignore the sparse list: the whole revision, and every change of the working tree laid over it.
///
/// # Errors
///
/// A git command that fails, or a file of the working tree that cannot be copied.
pub fn make(
    co: &Checkout,
    (root, world): (&Path, &Path),
    vars: &BTreeMap<String, String>,
    (env, timeout, worlds): (&[(String, String)], Duration, Worlds),
) -> Result<(), String> {
    let git = Git { env, timeout, root };
    let repo = root.join(fill(&co.repo, vars)).display().to_string();
    let dest: PathBuf = world.join(fill(&co.into, vars));
    let at = dest.display().to_string();
    git.run(&["clone", "-q", "--shared", "--no-checkout", &repo, &at])?;
    let sparse: Vec<String> = match worlds {
        Worlds::Sparse => co.sparse.iter().map(|p| fill(p, vars)).collect(),
        Worlds::Whole => Vec::new(),
    };
    if !sparse.is_empty() {
        let mut args = vec!["-C", &at, "sparse-checkout", "set", "--cone"];
        args.extend(sparse.iter().map(String::as_str));
        git.run(&args)?;
    }
    let rev = fill(&co.rev, vars);
    let worktree = rev == WORKTREE;
    git.run(&[
        "-C",
        &at,
        "checkout",
        "-q",
        if worktree { "HEAD" } else { &rev },
    ])?;
    if worktree {
        overlay(&git, &repo, &dest, &sparse)?;
    }
    Ok(())
}
