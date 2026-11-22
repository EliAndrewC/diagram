//! `/tmp`'s share of the sweep and the task outputs' (feature 451 T158, the host's measurement of 2026-11-22 ~19:45Z at the GM's
//! request): 2,081 `/tmp/t<N>` scratch entries at 63 GB (27 GB idle over a day) and ~5,200 `/tmp/tmp.*` at 4.2 GB, which nothing
//! removed, and 17 GB of task outputs under `/tmp/claude-<uid>`, all of the last day, which the day's sweep kept because their sessions
//! were live.
//!
//! - A builder's scratch, `/tmp/t<N>...` (its task's number: `t33`, `t216r`, `t02-base.log`), and a `mktemp -d`'s `/tmp/tmp.*`, this
//!   uid's own, go once nothing in them changed in the scratch threshold (`SCRATCH_SWEEP_TMP_HOURS`); and a task's own go when its
//!   task lands (`landed`, `make land`'s last step), unless another feature started a task of the same number within the day (449's
//!   T158 and 451's share `/tmp/t158`), which leaves them to the age rule.
//! - Either is kept while it holds a registered worktree's tree (a clean idle one goes first, `sweep/trees.rs`, and this entry with it; any other `make land` names) or a
//!   live process holds a path under it (the sweep's filter).
//! - A task's output (`<root>/<slug>/<session>/tasks/*.output`), a live session's too, goes once idle past the outputs threshold
//!   (`SCRATCH_SWEEP_OUTPUT_HOURS`); a running task's is held open by the shell writing it, so the filter keeps it.

use std::os::unix::fs::MetadataExt;
use std::path::{Path, PathBuf};
use std::time::{Duration, SystemTime};

use super::{children, idle, worktrees, Config};

/// How long another feature's start of a task of the same number holds the landing's removal (a day: `/tmp/t<N>` names a number,
/// not a feature).
const SAME_NUMBER: Duration = Duration::from_secs(86_400);

/// The task number a `/tmp` entry's name gives (`t216r` -> Some(Some(216)), `t02-base.log` -> Some(Some(2))), a `mktemp -d`'s
/// `tmp.*` (Some(None)); None for any other name.
#[expect(
    clippy::option_option,
    reason = "three cases: not scratch, a mktemp's (no task), a task's number"
)]
fn scratch_name(name: &str) -> Option<Option<u64>> {
    if name.starts_with("tmp.") {
        return Some(None);
    }
    let digits: String = name
        .strip_prefix('t')?
        .chars()
        .take_while(char::is_ascii_digit)
        .collect();
    digits.parse().ok().map(Some)
}

/// This uid's scratch entries of `/tmp`, with the task number each names, none holding a registered worktree's tree.
fn scratch(c: &Config) -> Vec<(PathBuf, Option<u64>)> {
    let trees: Vec<PathBuf> = worktrees(c).into_iter().map(|w| w.tree).collect();
    children(&c.tmp)
        .into_iter()
        .filter(|(_, _, m)| m.uid() == c.uid)
        .filter_map(|(p, name, _)| scratch_name(&name).map(|n| (p, n)))
        .filter(|(p, _)| !trees.iter().any(|t| t.starts_with(p)))
        .collect()
}

/// The scratch entries idle since `cutoff`.
pub(super) fn idle_scratch(c: &Config, cutoff: SystemTime) -> Vec<(PathBuf, &'static str)> {
    scratch(c)
        .into_iter()
        .filter(|(p, _)| idle(p, cutoff))
        .map(|(p, _)| (p, "/tmp scratch, nothing inside changed"))
        .collect()
}

/// Every task output idle since `cutoff`, under every session of every slug of the root.
pub(super) fn outputs(root: &Path, cutoff: SystemTime) -> Vec<(PathBuf, &'static str)> {
    let mut out = Vec::new();
    for (slug, name, meta) in children(root) {
        if !(name.starts_with('-') && meta.is_dir()) {
            continue;
        }
        for (session, _, _) in children(&slug) {
            for (file, name, _) in children(&session.join("tasks")) {
                if name.ends_with(".output") && idle(&file, cutoff) {
                    out.push((file, "a finished task's output, idle"));
                }
            }
        }
    }
    out
}

/// The landed tasks' own scratch (`numbers`), but a number another feature than `feature` started within the day, from the clone's
/// `task-starts.jsonl` (`starts`): the entries to remove, and the numbers left to the age rule.
pub(super) fn landed(
    c: &Config,
    feature: &str,
    numbers: &[u64],
    starts: &Path,
    now: SystemTime,
) -> (Vec<(PathBuf, &'static str)>, Vec<u64>) {
    let text = std::fs::read_to_string(starts).unwrap_or_default();
    let since = now
        .checked_sub(SAME_NUMBER)
        .and_then(|t| t.duration_since(SystemTime::UNIX_EPOCH).ok())
        .map_or(0.0, |d| d.as_secs_f64());
    let shared: Vec<u64> = numbers
        .iter()
        .copied()
        .filter(|n| {
            text.lines().any(|l| {
                let v: serde_json::Value = serde_json::from_str(l).unwrap_or_default();
                let task = v["task"].as_str().unwrap_or("");
                // `make land F=451` names the number, the record the directory (`451-time-retro-and-efficiency`)
                let other = v["feature"]
                    .as_str()
                    .is_some_and(|f| f != feature && !f.starts_with(&format!("{feature}-")));
                let recent = crate::shared::iso::parse(v["utc"].as_str().unwrap_or(""))
                    .is_some_and(|t| t >= since);
                other && recent && task.strip_prefix('T').and_then(|d| d.parse().ok()) == Some(*n)
            })
        })
        .collect();
    let gone = scratch(c)
        .into_iter()
        .filter(|(_, n)| n.is_some_and(|n| numbers.contains(&n) && !shared.contains(&n)))
        .map(|(p, _)| (p, "its task landed"))
        .collect();
    (gone, shared)
}

#[cfg(test)]
mod tests;
