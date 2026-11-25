//! `make disk-audit` (451 T245; the GM 2026-11-25: "having some kind of audit of disk space and what this container specifically is
//! leaving sitting around is probably something we should add to our performance tuning and checks"): every place this container
//! writes, each with its size, its owner (a tree, a session), its age and a budget, the largest entries under it, and the total against
//! the disk - and what the low-disk eviction would free now. Read-only; nothing is removed.
//!
//! The places and their budgets (each a GUESS, a constant here but the cache's, from the 2026-11-25 measurement: `du` of each, `df`):
//! the build cache 100 GB (`L7R_CACHE_BUDGET_GB`, T158's); Claude Code's scratch under `/tmp/claude-<uid>` 20 GB (17 GB measured, the
//! sweep's three-day age holding it); the session transcripts `~/.claude/projects` 20 GB (14 GB; nothing of ours removes them, Claude
//! Code's own `cleanupPeriodDays` does); the guard log 1 GB (0.5 GB, 123,137 files); `/tmp/l7r-*` 5 GB (2 GB in 1,184 entries); the
//! rest of this user's `/tmp` 10 GB (the day's sweep takes it idle a day); the session clones 25 GB (13 GB in 7); the mirror outside
//! the clones 25 GB (17 GB); the rest of `~/.cache` 5 GB (1.7 GB). Their sum, 211 GB, is under half the 461 GB disk.
//!
//! The overlay's `df` reports the host's disk, so "used" holds what no place here writes (the image, other containers, the host's own
//! files): the audit states it as unaccounted, not as ours (2026-11-25: 392 GB used, about 240 GB in these places).

use std::fmt::Write as _;
use std::os::unix::fs::MetadataExt;
use std::path::{Path, PathBuf};
use std::time::SystemTime;

use super::super::{sweep, Config};
use super::{gb, hours};
use crate::protocol::Reply;

const GB: u64 = 1_000_000_000;
/// How many of a place's largest entries the audit names.
const LARGEST: usize = 4;

/// One place: its name, its budget, and its entries (path, owner).
struct Place {
    name: String,
    budget: u64,
    entries: Vec<(PathBuf, String)>,
}

/// The audit: one block a place, then the total against the disk and the eviction's figure.
pub(in super::super) fn audit(c: &Config, now: SystemTime) -> Reply {
    let mut out = String::new();
    let mut accounted = 0;
    for place in places(c) {
        let mut sized: Vec<(PathBuf, String, u64, SystemTime)> = place
            .entries
            .into_iter()
            .map(|(p, owner)| {
                let (b, t) = sweep::measure(&p);
                (p, owner, b, t)
            })
            .collect();
        sized.sort_by(|a, b| b.2.cmp(&a.2));
        let total: u64 = sized.iter().map(|e| e.2).sum();
        accounted += total;
        let verdict = if total > place.budget {
            format!("OVER by {}", gb(total - place.budget))
        } else {
            "within".to_owned()
        };
        let _ = writeln!(
            out,
            "{:>9} of {:>9}  {verdict:<16} {} ({} entries)",
            gb(total),
            gb(place.budget),
            place.name,
            sized.len()
        );
        for (p, owner, b, t) in sized.iter().take(LARGEST) {
            let _ = writeln!(
                out,
                "  {:>9}  {}  ({owner}; last written {} ago)",
                gb(*b),
                p.display(),
                hours(now, *t)
            );
        }
    }
    match c.disk() {
        Some((size, free)) => {
            let used = size.saturating_sub(free);
            let _ = writeln!(
                out,
                "disk: {} used of {}, {} free ({}%; the eviction starts below {}%, L7R_DISK_FREE_PCT); these places {}, \
                 unaccounted {} (the overlay's df counts the host's disk: the image, other containers, the host's own files)",
                gb(used),
                gb(size),
                gb(free),
                free * 100 / size.max(1),
                (c.free_at * 100.0).round(),
                gb(accounted),
                gb(used.saturating_sub(accounted))
            );
        }
        None => {
            let _ = writeln!(
                out,
                "disk: df could not read {}; these places {}",
                c.cargo.display(),
                gb(accounted)
            );
        }
    }
    let dry = super::evict(c, now, true);
    let _ = write!(
        out,
        "{}",
        dry.stdout
            .lines()
            .last()
            .map(|l| format!("now: {l}\n"))
            .unwrap_or_default()
    );
    Reply {
        stdout: out,
        stderr: String::new(),
        code: 0,
    }
}

/// Every place, its entries and their owners.
fn places(c: &Config) -> Vec<Place> {
    let place = |name: String, budget: u64, entries| Place {
        name,
        budget,
        entries,
    };
    let dirs = |dir: &Path,
                keep: &dyn Fn(&str, &std::fs::Metadata) -> bool,
                owner: &dyn Fn(&str) -> String| {
        sweep::entries(dir)
            .into_iter()
            .filter(|(_, n, m)| keep(n, m))
            .map(|(p, n, _)| (p, owner(&n)))
            .collect::<Vec<_>>()
    };
    let mine = |m: &std::fs::Metadata| m.uid() == c.uid;
    let tmp_root = c.root.clone();
    let mut sessions = Vec::new();
    for (slug, name, m) in sweep::entries(&c.root) {
        if m.is_dir() && name.starts_with('-') {
            sessions.extend(dirs(&slug, &|_, _| true, &|id| format!("session {id}")));
        } else {
            sessions.push((slug, "loose".to_owned()));
        }
    }
    vec![
        place(
            format!("the build cache {}", c.cargo.display()),
            c.budget,
            dirs(&c.cargo, &|_, m| m.is_dir(), &|n| owner(c, n)),
        ),
        place(
            format!("Claude Code's scratch {}", c.root.display()),
            20 * GB,
            sessions,
        ),
        place(
            format!("the session transcripts {}", c.projects.display()),
            20 * GB,
            dirs(&c.projects, &|_, _| true, &|n| format!("project {n}")),
        ),
        place(
            format!("the guard log {}", c.guard_log.display()),
            GB,
            vec![(
                c.guard_log.clone(),
                "every session's guard firings".to_owned(),
            )],
        ),
        place(
            format!("{}/l7r-*", c.tmp.display()),
            5 * GB,
            dirs(&c.tmp, &|n, m| n.starts_with("l7r-") && mine(m), &|_| {
                "a suite or a tool".to_owned()
            }),
        ),
        place(
            format!("the rest of this user's {}", c.tmp.display()),
            10 * GB,
            dirs(
                &c.tmp,
                &|n, m| !n.starts_with("l7r-") && mine(m) && c.tmp.join(n) != tmp_root,
                &|_| "a builder's scratch".to_owned(),
            ),
        ),
        place(
            format!("the session clones {}", c.clones.display()),
            25 * GB,
            dirs(&c.clones, &|_, m| m.is_dir(), &|n| {
                format!("clone or worktree {n}")
            }),
        ),
        place(
            format!("the mirror {} outside the clones", c.mirror.display()),
            25 * GB,
            dirs(&c.mirror, &|n, _| c.mirror.join(n) != c.clones, &|_| {
                "the mirror".to_owned()
            }),
        ),
        place(
            format!("the rest of {}", c.cache_home.display()),
            5 * GB,
            dirs(
                &c.cache_home,
                &|n, _| c.cache_home.join(n) != c.cargo,
                &|n| format!("cache {n}"),
            ),
        ),
    ]
}

/// A build directory's owner: the tree its name is, and whether it is there.
fn owner(c: &Config, name: &str) -> String {
    if c.mirror.file_name().is_some_and(|n| n == name) {
        return "the mirror's: the guard's kept binary".to_owned();
    }
    if c.clones.join(name).is_dir() {
        return format!("the tree {}", c.clones.join(name).display());
    }
    if let Some(w) = sweep::worktrees(c)
        .into_iter()
        .find(|w| w.tree.file_name().is_some_and(|n| n == name))
    {
        return format!("the worktree {} of {}", w.tree.display(), w.repo.display());
    }
    if sweep::BUILT_INTO.contains(&name) {
        return "the hooks suites' and trials' fixture trees".to_owned();
    }
    "no tree of that name on disk (a landing tree between landings, or gone)".to_owned()
}

#[cfg(test)]
mod tests;
