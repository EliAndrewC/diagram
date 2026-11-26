//! THE CACHE'S BUDGET HELD (451 T245; the GM 2026-11-25: "my host has a 461G disk drive, so if that is full then it is because this
//! container specifically is leaving artifacts sitting around"). Measured 2026-11-25 (`du` of each build directory, `df`): the cache
//! held 190 GB against its 100 GB budget, and `make cache-clean DRY=1` freed 27 MB, because T158's rules take only a proven-dead build
//! directory and a crate's variants past its newest sixteen - a live tree's build directory was "never removed whole", and every tree
//! the cache held was live. The budget was a number nothing held.
//!
//! The rule: past the budget (or, from the low-disk trigger, short of the free-space share), whole PROFILES of live trees' build
//! directories go - `debug/`, `cover-gate/`, `tool/`, each a child directory, never the build directory's own files (the guard's kept
//! `l7r-guard.good`, the run lock and record) - least recently built first, until the shortfall is met, and only a profile:
//! - not of the mirror's build directory (the guard hook runs its kept binary), not of a builder pool tree's (451 T285: a free
//!   pool tree is idle, and its warm cache is what the pool keeps), and not in a build directory in use (`cargo::in_use`:
//!   a live process holds a path under it, or its run record names a live member);
//! - idle past `L7R_CACHE_IDLE_HOURS` (12, the variants' knob): nothing in it changed since;
//! - its tree's ranked: a tree IDLE first - none of its trees exists (a landing tree between landings, a name the suites build into), or
//!   each one's HEAD log (`.git/logs/HEAD`: a commit, a checkout, a reset) is older than the knob and no live process has its cwd in
//!   it - and only then an ACTIVE tree's idle profile (a coverage family no gate has run since), so a tree in use keeps its working set
//!   longest. Within a rank, the least recently built first.
//!
//! Cost, priced 2026-11-25: a profile taken is a cold rebuild of that profile on its tree's next build (one crate's coverage family a
//! few minutes; the landing tree's whole set, 43 GB, its next landing's gate cold). T158 kept every live tree's whole under the GM's
//! "no loss of performance" condition; the GM's T245 words ask for the budget held, and on a disk at 90% the alternative is the
//! 2026-11-22 failure (every builder's coverage run "No space left on device"). Alternatives priced: a larger budget (holds nothing,
//! the working set grows with each parallel tree, 13-14 GB a trial); evicting only gone trees (27 MB on the day); evicting by tree
//! rather than profile (a tree touched at 13:28 by one tool build kept its 25 GB coverage set from 07:34). Chosen by the T245 builder
//! under the GM's words; the knobs are the budget, the idle hours and the free-space share.

use std::path::{Path, PathBuf};
use std::time::{SystemTime, UNIX_EPOCH};

use super::cargo::{in_use, BUILT_INTO};
use super::{bytes, children, newest, Config};

/// A profile the budget may take: where, its size, when it was last built, and its tree's rank (0 idle, 1 active).
struct Candidate {
    path: PathBuf,
    bytes: u64,
    built: SystemTime,
    rank: u8,
}

/// The profiles to remove to free `need` bytes, in the order taken, each with why; none where `need` is 0.
pub(super) fn choose(
    c: &Config,
    need: u64,
    cutoff: SystemTime,
    held: &[PathBuf],
) -> Vec<(PathBuf, &'static str)> {
    if need == 0 {
        return Vec::new();
    }
    let mirror = c
        .mirror
        .file_name()
        .map(|n| n.to_string_lossy().into_owned());
    // A POOL TREE'S BUILD DIRECTORY IS NEVER THE BUDGET'S (451 T285, its plan review of 2026-11-26): a free pool tree is idle
    // by this rule's own ranking, so past the budget its profiles went first and the next builder was handed a cold tree - the
    // failure the pool exists to end. The pool's share is bounded apart: its cap of trees (`builder_pool::CAP`), about 9 GB
    // each, measured 2026-11-26 (`du -sh` of the three trees' build directories); `make builder-tree-drop` gives one back.
    let pool: Vec<String> = crate::shared::builder_pool::pools(&c.clones)
        .iter()
        .filter_map(|t| t.tree.file_name())
        .map(|n| n.to_string_lossy().into_owned())
        .collect();
    let mut found = Vec::new();
    for (target, name, meta) in children(&c.cargo) {
        if !meta.is_dir()
            || Some(&name) == mirror.as_ref()
            || pool.contains(&name)
            || in_use(&target, held, &c.proc)
        {
            continue;
        }
        let rank = u8::from(active(c, &name, cutoff, held));
        for (profile, _, m) in children(&target) {
            match newest(&profile) {
                Some(built) if m.is_dir() && built < cutoff => found.push(Candidate {
                    bytes: bytes(&profile),
                    path: profile,
                    built,
                    rank,
                }),
                _ => {}
            }
        }
    }
    found.sort_by(|a, b| a.rank.cmp(&b.rank).then(a.built.cmp(&b.built)));
    let mut freed = 0;
    let mut out = Vec::new();
    for cand in found {
        if freed >= need {
            break;
        }
        freed += cand.bytes;
        out.push((
            cand.path,
            if cand.rank == 0 {
                "the cache past its budget: an idle tree's profile, least recently built"
            } else {
                "the cache past its budget: an active tree's profile, idle past the knob"
            },
        ));
    }
    out
}

/// A tree of this name is in use: one exists (the clone of that name, a registered worktree of it) whose HEAD moved since `cutoff`
/// or where a live process has its cwd. A name the suites build into (`BUILT_INTO`) or whose trees are all gone is idle.
fn active(c: &Config, name: &str, cutoff: SystemTime, held: &[PathBuf]) -> bool {
    if BUILT_INTO.contains(&name) {
        return false;
    }
    let mut trees: Vec<PathBuf> = vec![c.clones.join(name)];
    trees.extend(
        super::worktrees(c)
            .into_iter()
            .map(|w| w.tree)
            .filter(|t| t.file_name().is_some_and(|n| n == name)),
    );
    trees.iter().filter(|t| t.is_dir()).any(|t| {
        held.iter().any(|h| h.starts_with(t)) || head_moved(t).is_some_and(|m| m >= cutoff)
    })
}

/// When the tree's HEAD last moved: its HEAD log's mtime (`.git/logs/HEAD`, a worktree's in its administrative directory).
fn head_moved(tree: &Path) -> Option<SystemTime> {
    let git = tree.join(".git");
    let dir = if git.is_dir() {
        git
    } else {
        let text = std::fs::read_to_string(&git).ok()?;
        PathBuf::from(text.trim().strip_prefix("gitdir:")?.trim())
    };
    let t = std::fs::metadata(dir.join("logs/HEAD"))
        .ok()?
        .modified()
        .ok()?;
    (t > UNIX_EPOCH).then_some(t)
}

#[cfg(test)]
mod tests;
