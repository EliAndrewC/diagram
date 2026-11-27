//! THE PER-CLONE LEFTOVERS (451 T246; the GM 2026-11-25: "the old task scratch folder is over 1/3 of a gigabyte? That doesn't seem
//! right to me"). What a clone's own directories kept that nothing removed, measured 2026-11-25 (`du` of each, `find -printf '%T'`):
//!
//! - A TASK'S SCRATCH in the git directory, `.git/t<N>...` (451 T204's 335 MB copy of the tree and gate binary, T192's 14 MB, removed
//!   by hand; 23 entries and 1.1 MB left, mostly land logs), and A HANDOFF'S SCRATCH FOLDER, `.git/l7r-handoffs/T<N>-<what>/` (T432
//!   55 MB, T433 36 MB, T435 35 MB of a 207 MB folder): taken by `make land` for the tasks it lands ([`landed`]), each a directory,
//!   never a handoff note (`T<N>-<agent>.md`, which `land/writers.rs` and the context-cap guard read) nor a loose file (`t<N>-land.log`,
//!   a few kilobytes: a landing's own log, written while it runs). A number another feature started within the day is left
//!   (`tmp::landed`'s rule: `T432-scratch` is 449's).
//! - A REVIEW SNAPSHOT, `.git/review-snapshot/<unit>/` (1.75 GB in 141, one a unit, `l7r-gate reviews snapshot` clearing a unit's own
//!   before it takes it again): taken once idle past `SCRATCH_SWEEP_SNAPSHOT_DAYS` ([`snapshots`]) unless it holds `tree.json`.
//!   MEASURED FIRST, 2026-11-25 (`scratchpad/t246-snapread.py` over the `-diagram*` transcripts: an Agent prompt naming
//!   `review-snapshot/<unit>` is a read, a tool result naming its `dispatch.md` a take): 245 reads of 57 units, each at most 10.6 h after
//!   its unit's last take, none past 72 h; the 58 with no take in the transcripts read the review tree's snapshots, 5 within 0.1 h of the
//!   `dispatch.md` on disk and 53 taken again since. A snapshot without `tree.json` is read only by its unit's dispatch (`prereq.rs`'s
//!   `stale_maps`, the pair guard's prompt file), so a week idle is 16 times the oldest read. One WITH `tree.json` (the review tree's,
//!   451 T164: 58, all of 2026-11-23) is read after its review too - `tree::of_unit` keys the unit's content key, its verdict's carry,
//!   the checkpoint and the arbiter's round count to its copy, and without it they read the live pool - so it is KEPT whatever its age,
//!   until its unit is snapshotted again. Cost: those snapshots' bytes (about 0.9 GB on the day) held; the alternative priced, taking
//!   one whose copy matches the live pool's sheet, needs the pool walk this crate does not have. Chosen by the T246 builder.
//! - A DEAD STORE of the generation cache, `<tree>/.gencache/<store>` other than `rust` ([`dead_stores`]): the Python engine's roll
//!   store and per-map entries (6.1 GB of `rolls` in one clone, unwritten since that engine was deleted on 2026-11-07, which
//!   `sync-with-main.sh` already calls a dead store; no code reads `.gencache/` but `.gencache/rust`, `rg '\.gencache'` 2026-11-25),
//!   taken once idle past `SCRATCH_SWEEP_DAYS`. The live cache, `.gencache/rust` (16 MB), holds its own lock and read table and is
//!   never taken.
//!
//! The trees are the mirror and every directory under the clones directory; a git directory is a tree's own `.git` directory (a
//! worktree's `.git` is a file, its scratch in its clone's).

use std::path::{Path, PathBuf};
use std::time::SystemTime;

use super::{children, idle, Config};

/// The live generation cache's store, never taken.
const LIVE_STORE: &str = "rust";

/// The mirror and every directory under the clones directory.
fn trees(c: &Config) -> Vec<PathBuf> {
    let mut out = vec![c.mirror.clone()];
    out.extend(
        children(&c.clones)
            .into_iter()
            .filter(|(_, _, m)| m.is_dir())
            .map(|(p, _, _)| p),
    );
    out
}

/// Each tree's own git directory.
pub(crate) fn git_dirs(c: &Config) -> Vec<PathBuf> {
    trees(c)
        .into_iter()
        .map(|t| t.join(".git"))
        .filter(|g| std::fs::symlink_metadata(g).is_ok_and(|m| m.is_dir()))
        .collect()
}

/// Each tree's generation cache, where it has one.
pub(crate) fn gencaches(c: &Config) -> Vec<PathBuf> {
    trees(c)
        .into_iter()
        .map(|t| t.join(".gencache"))
        .filter(|g| g.is_dir())
        .collect()
}

/// Whether a generation cache's store is the live one.
pub(crate) fn live_store(name: &str) -> bool {
    name == LIVE_STORE
}

/// The review snapshots without `tree.json`, idle since `cutoff`.
pub(super) fn snapshots(c: &Config, cutoff: SystemTime) -> Vec<(PathBuf, &'static str)> {
    git_dirs(c)
        .iter()
        .flat_map(|g| children(&g.join("review-snapshot")))
        .filter(|(p, _, m)| m.is_dir() && !p.join("tree.json").exists() && idle(p, cutoff))
        .map(|(p, _, _)| (p, "a review snapshot idle past its age, no review tree's"))
        .collect()
}

/// The generation caches' dead stores, idle since `cutoff`.
pub(super) fn dead_stores(c: &Config, cutoff: SystemTime) -> Vec<(PathBuf, &'static str)> {
    gencaches(c)
        .iter()
        .flat_map(|g| children(g))
        .filter(|(p, name, _)| !live_store(name) && idle(p, cutoff))
        .map(|(p, _, _)| (p, "a dead store of the generation cache, idle"))
        .collect()
}

/// The task number a name gives after `prefix` (`t204` and `t31-parked` after `t`, `T432-scratch` after `T`): its leading digits.
fn number(name: &str, prefix: char) -> Option<u64> {
    let digits: String = name
        .strip_prefix(prefix)?
        .chars()
        .take_while(char::is_ascii_digit)
        .collect();
    digits.parse().ok()
}

/// The landed tasks' own directories in the git directory `git`: `t<N>...` and `l7r-handoffs/T<N>-...`.
pub(super) fn landed(git: &Path, numbers: &[u64]) -> Vec<(PathBuf, &'static str)> {
    let ours = |name: &str, prefix| number(name, prefix).is_some_and(|n| numbers.contains(&n));
    let mut out: Vec<(PathBuf, &'static str)> = children(git)
        .into_iter()
        .filter(|(_, name, m)| m.is_dir() && ours(name, 't'))
        .map(|(p, _, _)| {
            (
                p,
                "its task landed: the task's scratch in the git directory",
            )
        })
        .collect();
    out.extend(
        children(&git.join("l7r-handoffs"))
            .into_iter()
            .filter(|(_, name, m)| m.is_dir() && ours(name, 'T'))
            .map(|(p, _, _)| (p, "its task landed: the handoff's scratch folder")),
    );
    out
}

/// THE LANDING SESSION'S SCRATCHPAD (451 T517): the landed tasks' own scratch worlds in it - an entry named for the task's number,
/// `t<N>` then anything but a digit (`t373/`, `t386-bench/`, `t517-sizes.txt`; `t51` is never `t515`'s), a file or a directory,
/// holding no registered worktree's tree. The session is the one landing (`CLAUDE_CODE_SESSION_ID`, the sweep's `keep`), found under
/// whichever slug of the root holds it: builders write into their coordinator's scratchpad (451 T271), and its slug is the tree the
/// session started in, not the clone it lands from. No session, none: another session's scratchpad is judged by the age rule alone.
pub(super) fn scratchpad(c: &Config, numbers: &[u64]) -> Vec<(PathBuf, &'static str)> {
    if c.keep.is_empty() {
        return Vec::new();
    }
    let trees: Vec<PathBuf> = super::worktrees(c).into_iter().map(|w| w.tree).collect();
    children(&c.root)
        .into_iter()
        .flat_map(|(slug, _, _)| children(&slug.join(&c.keep).join("scratchpad")))
        .filter(|(p, name, _)| {
            number(name, 't').is_some_and(|n| numbers.contains(&n))
                && !trees.iter().any(|t| t.starts_with(p))
        })
        .map(|(p, _, _)| {
            (
                p,
                "its task landed: its scratch world in a session's scratchpad",
            )
        })
        .collect()
}

/// The numbers of `numbers` another feature than `feature` started and has not ticked, whatever the start's age (451 T517): a live
/// scratchpad has no age rule to fall back on, as `/tmp`'s has (`tmp::landed`'s day), so a start of another feature still open in its
/// `tasks.md` (the clone's `specs/<feature>/`, beside the git directory holding `starts`) holds the number. A start whose `tasks.md`
/// cannot be read holds it too.
pub(super) fn open_elsewhere(starts: &Path, feature: &str, numbers: &[u64]) -> Vec<u64> {
    let text = crate::shared::speckit::marks::live_starts(
        &std::fs::read_to_string(starts).unwrap_or_default(),
    );
    let specs = starts
        .parent()
        .and_then(Path::parent)
        .unwrap_or(Path::new(""))
        .join("specs");
    let ours = |f: &str| f == feature || f.starts_with(&format!("{feature}-"));
    let open = |f: &str, task: &str| {
        let line = format!("- [ ] {task} ");
        children(&specs)
            .into_iter()
            .find(|(_, name, _)| name == f || name.starts_with(&format!("{f}-")))
            .and_then(|(d, _, _)| std::fs::read_to_string(d.join("tasks.md")).ok())
            .is_none_or(|t| t.lines().any(|l| format!("{l} ").starts_with(&line)))
    };
    numbers
        .iter()
        .copied()
        .filter(|n| {
            text.lines().any(|l| {
                let v: serde_json::Value = serde_json::from_str(l).unwrap_or_default();
                let (f, task) = (
                    v["feature"].as_str().unwrap_or(""),
                    v["task"].as_str().unwrap_or(""),
                );
                !f.is_empty() && !ours(f) && number(task, 'T') == Some(*n) && open(f, task)
            })
        })
        .collect()
}

#[cfg(test)]
mod tests;
