//! A WORKER'S WHOLE WORLD KEPT FOR THE RUN (feature 449 T179, the GM 2026-11-18, request.md: the efficiency fixes): a verify run built
//! and removed a whole checkout for every case side - T174's first verify took 276.5 s and T175's 511.1 s against 58.2 s of T174's sides'
//! own commands. Where a side's world goes, measured (2026-11-18, T175's harness, one whole world made by hand with the runner's commands,
//! best of three, scratchpad `t178/t179/phases.py`): the clone 0.01-0.02 s, the checkout of 27,770 files 1.25-1.33 s, the working tree's
//! overlay 0.03 s, the setup 0.03 s, the snapshots under 0.01 s, the removal 0.27-0.30 s - so the checkout and the removal, about 1.6 s
//! of every side. A worker's whole world for a side is now made once a run, and reset between cases to what a fresh one is (the steps
//! below, measured on the same world after a case that writes, its second to fourth reset, scratchpad `t178/t179/reset2.py`: `.git`
//! restored 0.005-0.007 s, `read-tree` 0.08-0.13 s, `clean` 0.02-0.03 s, the mode walk under 0.09 s in Python), removed at the run's end.
//! The runs, `VERIFY=1 JOBS=4` from an empty state, one binary, `--fresh-worlds` and reuse alternating (2026-11-18, the host's load 0.8-5
//! of 22 cores, scratchpad `t178/t179/measure.sh`): T174's 113 cases 152.4 s fresh against 51.0 s reused, T175's 207 cases 376.1 s
//! against 164.5 s, each report's rows the same as its harness's earlier verify.
//!
//! THE RISK (T169's plan review): a world that differs from a fresh one makes two sides agree falsely. So the reset restores everything
//! a case can change - and the equality tests (`reuse_tests.rs`; the runner's, `tests/reuse.rs`) hold a reset world to a fresh one, every path, its bytes and mode, the
//! index, HEAD, the refs and `git status`, after cases that write, delete, add ignored and untracked files, change the index, commit,
//! and write under `.git/`:
//! - the world outside the checkout emptied (the setup writes there, and runs again after);
//! - the checkout's `.git` put back whole from a copy taken when the world was made, its index with it: the case's index is never read,
//!   so neither its staged entries nor an `assume-unchanged` or `skip-worktree` flag hides a change from the next step. Git sees a
//!   rewritten file by its change time, which no case can put back (`touch -r` or not), and one rewritten at its size within the second
//!   the index was written by the index file's own time, which the copy keeps ([`copy_tree`]);
//! - `git read-tree -u --reset HEAD`, which writes back every tracked file that differs from HEAD without moving a ref or writing a
//!   reflog (`git reset --hard` writes `ORIG_HEAD` and a reflog line a fresh world has not);
//! - `git clean -ffdx`: every untracked and ignored file, and a nested repository;
//! - the working tree's overlay laid again (a `WORKTREE` side), as the fresh world lays it;
//! - each path's mode put back to the one it had when the world was made: git keeps only the executable bit, so a `chmod 600` or a
//!   directory's mode outlived the other steps; a path that is there and was not, or the reverse, makes the world anew.
//!
//! A world is made anew - never reset - when the repository's refs or HEAD moved since it was made (a fresh clone would hold the new
//! ones), when the checkout's declaration filled or a `GIT_` variable of the side's environment differs, and when any step of the reset
//! fails. Sparse worlds stay fresh: they cost 0.2 s a side already (T169), and the iterating runs that build them are not the ones a
//! plan cites. `--fresh-worlds` turns the reuse off, the run as it was.

use std::collections::BTreeMap;
use std::os::unix::fs::PermissionsExt as _;
use std::path::{Path, PathBuf};
use std::time::Duration;

use crate::cases::{fill, Checkout, Worlds};
use crate::checkout::{make, overlay, Git, WORKTREE};

/// What a world was made from: the checkout's declaration filled, the side's `GIT_` variables, and the repository's HEAD and refs.
#[derive(PartialEq, Eq, Debug)]
struct Made {
    checkout: [String; 3],
    git_env: Vec<(String, String)>,
    refs: String,
}

/// A worker's world for a side, kept between its cases.
pub struct Held {
    made: Made,
    world: PathBuf,
    dest: PathBuf,
    /// The checkout's `.git` as made (beside the world, under `work/`).
    git: PathBuf,
    /// Each path's mode under the checkout, `.git` aside, as made.
    modes: BTreeMap<String, u32>,
}

/// Where the reset's copy of `world`'s `.git` lives: beside it under `work/`, so a run's removal of `work/` takes it too.
fn beside(world: &Path, what: &str) -> PathBuf {
    let mut name = world.file_name().unwrap_or_default().to_os_string();
    name.push(what);
    world.with_file_name(name)
}

fn made(
    co: &Checkout,
    git: &Git,
    vars: &BTreeMap<String, String>,
    repo: &str,
) -> Result<Made, String> {
    // one git start: HEAD's and every ref's object, then their names (HEAD's branch among them)
    let refs = git.run(&[
        "-C",
        repo,
        "rev-parse",
        "HEAD",
        "--all",
        "--symbolic-full-name",
        "HEAD",
        "--all",
    ])?;
    Ok(Made {
        checkout: [repo.to_owned(), fill(&co.rev, vars), fill(&co.into, vars)],
        git_env: git
            .env
            .iter()
            .filter(|(k, _)| k.starts_with("GIT_"))
            .cloned()
            .collect(),
        refs,
    })
}

/// Every path under `dir` but its top `.git`, with its mode (the file type's bits with it).
fn modes(dir: &Path) -> BTreeMap<String, u32> {
    let mut out = BTreeMap::new();
    let mut stack = vec![(dir.to_path_buf(), String::new())];
    while let Some((d, rel)) = stack.pop() {
        let entries = std::fs::read_dir(&d).into_iter().flatten().flatten();
        for (e, meta) in
            entries.filter_map(|e| std::fs::symlink_metadata(e.path()).ok().map(|m| (e, m)))
        {
            let name = e.file_name().to_string_lossy().into_owned();
            if rel.is_empty() && name == ".git" {
                continue;
            }
            let here = format!("{rel}/{name}");
            if meta.is_dir() {
                stack.push((e.path(), here.clone()));
            }
            out.insert(here, meta.permissions().mode());
        }
    }
    out
}

/// A directory copied, each file's mode and modification time with it (a fresh clone's `.git`, which holds no link). The time is the
/// index's that matters: git takes an entry whose file changed in the same second as the index was written for one that may hide a
/// change, and reads its bytes - a copy dated now made a file a case rewrote at the same size within the second of the checkout look
/// clean, and the reset left it (the equality test's `TOP`, observed 2026-11-18 when the copy dropped the time).
fn copy_tree(from: &Path, to: &Path) -> std::io::Result<()> {
    std::fs::create_dir_all(to)?;
    for e in std::fs::read_dir(from)? {
        let e = e?;
        let (src, dst) = (e.path(), to.join(e.file_name()));
        let kind = e.file_type()?;
        if kind.is_dir() {
            copy_tree(&src, &dst)?;
        } else {
            std::fs::copy(&src, &dst)?;
            let time = std::fs::metadata(&src)?.modified()?;
            std::fs::File::options()
                .write(true)
                .open(&dst)?
                .set_modified(time)?;
        }
    }
    Ok(())
}

/// An I/O step's failure named: one closure for every step, so every error reads alike and one failing step tests them all.
fn failed(what: &str) -> impl FnOnce(std::io::Error) -> String + '_ {
    move |e| format!("world reset: {what}: {e}")
}

/// Everything under `world` removed but the directories down to the checkout `dest`.
fn clear(world: &Path, dest: &Path) -> Result<(), String> {
    let mut keep = dest;
    while let Some(parent) = keep.parent().filter(|p| p.starts_with(world)) {
        for e in std::fs::read_dir(parent).map_err(failed("list"))?.flatten() {
            let p = e.path();
            if p == keep {
                continue;
            }
            let gone = if e.file_type().is_ok_and(|t| t.is_dir()) {
                std::fs::remove_dir_all(&p)
            } else {
                std::fs::remove_file(&p)
            };
            gone.map_err(failed(&p.display().to_string()))?;
        }
        keep = parent;
    }
    Ok(())
}

/// Each path's mode put back to `want`'s; an error where the paths themselves differ.
fn remode(dest: &Path, want: &BTreeMap<String, u32>) -> Result<(), String> {
    let now = modes(dest);
    if now.len() != want.len() || now.keys().ne(want.keys()) {
        return Err("world reset: the paths differ from the world as made".to_owned());
    }
    for (rel, mode) in want.iter().filter(|(rel, mode)| now[*rel] != **mode) {
        let at = dest.join(rel.trim_start_matches('/'));
        let mode = std::fs::Permissions::from_mode(*mode);
        std::fs::set_permissions(&at, mode).map_err(failed(rel))?;
    }
    Ok(())
}

impl Held {
    /// The world `world` reset to what a fresh one is (the module's steps).
    fn reset(
        &self,
        git: &Git,
        co: &Checkout,
        vars: &BTreeMap<String, String>,
    ) -> Result<(), String> {
        clear(&self.world, &self.dest)?;
        let dot = self.dest.join(".git");
        std::fs::remove_dir_all(&dot).map_err(failed(".git"))?;
        copy_tree(&self.git, &dot).map_err(failed("the kept .git"))?;
        let at = self.dest.display().to_string();
        git.run(&["-C", &at, "read-tree", "-u", "--reset", "HEAD"])?;
        git.run(&["-C", &at, "clean", "-q", "-ffdx"])?;
        if fill(&co.rev, vars) == WORKTREE {
            overlay(git, &self.made.checkout[0], &self.dest, &[])?;
        }
        remode(&self.dest, &self.modes)
    }
}

/// The side's whole world ready in `world`: `held`'s reset where it was made from the same checkout and nothing has moved, else made
/// fresh and held for the next case (a world whose copies cannot be taken is made fresh each time).
///
/// # Errors
///
/// The fresh checkout's failure, as [`make`] names it.
pub fn ready(
    co: &Checkout,
    (root, world): (&Path, &Path),
    vars: &BTreeMap<String, String>,
    (env, timeout): (&[(String, String)], Duration),
    held: &mut Option<Held>,
) -> Result<(), String> {
    let git = Git { env, timeout, root };
    let repo = root.join(fill(&co.repo, vars)).display().to_string();
    let now = made(co, &git, vars, &repo);
    if let (Some(h), Ok(now)) = (held.as_ref(), &now) {
        if &h.made == now && h.reset(&git, co, vars).is_ok() {
            return Ok(());
        }
    }
    *held = None;
    let _ = std::fs::remove_dir_all(world);
    std::fs::create_dir_all(world).map_err(failed(&world.display().to_string()))?;
    make(co, (root, world), vars, (env, timeout, Worlds::Whole))?;
    let dest = world.join(fill(&co.into, vars));
    let dot = beside(world, ".git");
    let _ = std::fs::remove_dir_all(&dot);
    let kept = now
        .ok()
        .filter(|_| copy_tree(&dest.join(".git"), &dot).is_ok());
    *held = kept.map(|made| Held {
        made,
        modes: modes(&dest),
        world: world.to_path_buf(),
        dest,
        git: dot,
    });
    Ok(())
}

/// A held world removed at the run's end, with its copies.
pub fn release(held: Option<Held>) {
    if let Some(h) = held {
        let _ = std::fs::remove_dir_all(&h.world);
        let _ = std::fs::remove_dir_all(&h.git);
    }
}

#[cfg(test)]
#[path = "reuse_tests.rs"]
mod tests;
