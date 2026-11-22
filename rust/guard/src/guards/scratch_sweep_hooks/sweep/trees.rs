//! THE CLEAN SCRATCH WORKTREE (451 T158, its plan review of 2026-11-22: naming one at a landing is an instruction, not the cleanup).
//! A scratch worktree - a registered worktree of a clone or the mirror outside the clones directory, not the mirror - goes in the
//! day's sweep and at a landing once (a) nothing in its tree or its administrative directory changed in the scratch threshold
//! (`SCRATCH_SWEEP_TMP_HOURS`), (b) no live process holds a path under it, (c) a ref holds its HEAD (`git for-each-ref --contains`:
//! its branch, or a commit already on one), so no commit is lost, and (d) `git worktree remove` without `--force` takes it - git
//! itself refusing one with a modified or untracked file. A worktree failing any of them stays, named by `make land` as before:
//! it may hold a builder's uncommitted probe, and which task made it is recorded nowhere.

use std::path::{Path, PathBuf};
use std::process::Command;
use std::time::SystemTime;

use super::{idle, worktrees, Config, Worktree};

/// The scratch worktrees (a) to (c) allow, before git's own check.
fn removable(c: &Config, cutoff: SystemTime, live: &[PathBuf]) -> Vec<Worktree> {
    worktrees(c)
        .into_iter()
        .filter(|w| !w.tree.starts_with(&c.clones) && w.tree != c.mirror)
        .filter(|w| idle(&w.tree, cutoff) && idle(&w.admin, cutoff))
        .filter(|w| !live.iter().any(|l| l.starts_with(&w.tree)))
        .filter(|w| head_on_a_ref(&w.tree))
        .collect()
}

/// A ref contains the tree's HEAD: removing the tree loses no commit.
fn head_on_a_ref(tree: &Path) -> bool {
    Command::new("git")
        .arg("-C")
        .arg(tree)
        .args(["for-each-ref", "--contains", "HEAD", "--count=1"])
        .output()
        .is_ok_and(|o| o.status.success() && !o.stdout.is_empty())
}

/// The clean, idle scratch worktrees, each removed by `git worktree remove` (no `--force`): the trees removed.
pub(super) fn remove_clean(c: &Config, cutoff: SystemTime, live: &[PathBuf]) -> Vec<PathBuf> {
    removable(c, cutoff, live)
        .into_iter()
        .filter(|w| {
            Command::new("git")
                .arg("-C")
                .arg(&w.repo)
                .args(["worktree", "remove"])
                .arg(&w.tree)
                .output()
                .is_ok_and(|o| o.status.success())
        })
        .map(|w| w.tree)
        .collect()
}

#[cfg(test)]
pub(crate) mod fixture;
#[cfg(test)]
mod tests;
