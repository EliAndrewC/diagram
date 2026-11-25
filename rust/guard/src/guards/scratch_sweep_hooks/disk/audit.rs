//! `make disk-audit` (451 T245; the GM 2026-11-25: "having some kind of audit of disk space and what this container specifically is
//! leaving sitting around is probably something we should add to our performance tuning and checks"): every place this container
//! writes, each with its size, its owner (a tree, a session), its age and a budget, the largest entries under it, and the total against
//! the disk - and what the low-disk eviction would free now. Read-only; nothing is removed.
//!
//! The places and their budgets (each a GUESS, a constant here but the cache's, from the 2026-11-25 measurement: `du` of each, `df`):
//! the build cache 100 GB (`L7R_CACHE_BUDGET_GB`, T158's); Claude Code's scratch under `/tmp/claude-<uid>` 20 GB (17 GB measured, the
//! sweep's three-day age holding it); this project's session transcripts, `~/.claude/projects/-diagram*` 10 GB (451 T246: 6.8 GB of
//! the 14 GB there; the directory is every container's and the host's, so the other projects' are never counted here; nothing of ours
//! removes them, Claude Code's own `cleanupPeriodDays` does); the guard log 1 GB (0.5 GB, 123,137 files); `/tmp/l7r-*` 5 GB (2 GB in
//! 1,184 entries); the rest of this user's `/tmp` 10 GB (the day's sweep takes it idle a day); the session clones 25 GB (13 GB in 7);
//! the mirror outside the clones 25 GB (17 GB); the rest of `~/.cache` 5 GB (1.7 GB). Their sum, 201 GB, is under half the 461 GB
//! disk.
//!
//! WITHIN THE CLONES AND THE MIRROR (451 T246, `sweep/leftovers.rs`), each its own line but not added to the total again, measured
//! 2026-11-25: the tasks' scratch in the git directories, `.git/t<N>*`, 1 GB (1.1 MB left; T204's 335 MB copy the case); the handoff
//! folders `.git/l7r-handoffs` 0.5 GB (207 MB, 166 MB of it seven scratch folders); the review snapshots 1.5 GB (1.75 GB in 141, 0.9
//! GB once the week's rule takes the 37 idle past it); the generation caches `.gencache` 1 GB (6.2 GB, 6.1 GB of it the dead `rolls`
//! store; the live `rust` store 16 MB). Each budget a GUESS: the day's working set, about twice it.
//!
//! The overlay's `df` reports the host's disk, so "used" holds what no place here writes (the image, other containers, other projects'
//! transcripts, the host's own files): the audit states it as unaccounted, not as ours (2026-11-25: 392 GB used, about 240 GB in these
//! places), and names the host's podman storage, which this container cannot see, as the host's.

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

/// One place: its name, its budget, its entries (path, owner), and whether it lies within another place (sized, not added again).
struct Place {
    name: String,
    budget: u64,
    entries: Vec<(PathBuf, String)>,
    within: bool,
}

/// THE HOST'S, NOT OURS (451 T246, the host session's measurement of 2026-11-25): about 13 GB of podman's storage on the host is unused
/// image layers, which this container cannot see or remove.
const HOST_SIDE: &str = "host-side, not counted: podman's image storage on the host (about 13 GB of unused layers, the host's \
                         measurement of 2026-11-25) - the host's to clean (podman image prune), unseen from this container";

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
        if !place.within {
            accounted += total;
        }
        let verdict = if total > place.budget {
            format!("OVER by {}", gb(total - place.budget))
        } else {
            "within".to_owned()
        };
        let _ = writeln!(
            out,
            "{:>9} of {:>9}  {verdict:<16} {} ({} entries{})",
            gb(total),
            gb(place.budget),
            place.name,
            sized.len(),
            if place.within {
                "; within the clones and the mirror above, not added again"
            } else {
                ""
            }
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
    let _ = writeln!(out, "{HOST_SIDE}");
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

/// A directory's entries that `keep` keeps, each with the owner `owner` names.
fn dirs(
    dir: &Path,
    keep: &dyn Fn(&str, &std::fs::Metadata) -> bool,
    owner: &dyn Fn(&str) -> String,
) -> Vec<(PathBuf, String)> {
    sweep::entries(dir)
        .into_iter()
        .filter(|(_, n, m)| keep(n, m))
        .map(|(p, n, _)| (p, owner(&n)))
        .collect()
}

/// Every place, its entries and their owners: the places counted in the total, then those within the clones and the mirror.
fn places(c: &Config) -> Vec<Place> {
    let place = |name: String, budget: u64, entries| Place {
        name,
        budget,
        entries,
        within: false,
    };
    let mine = |m: &std::fs::Metadata| m.uid() == c.uid;
    // this project's transcripts alone: the mirror's slug, and every path under it (its clones'), never another project's (451 T246)
    let slug = slug_of(&c.mirror);
    let ours = |n: &str| n == slug || n.starts_with(&format!("{slug}-"));
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
            format!(
                "this project's session transcripts {}/{slug}*",
                c.projects.display()
            ),
            10 * GB,
            dirs(&c.projects, &|n, _| ours(n), &|n| format!("project {n}")),
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
    .into_iter()
    .chain(within_places(c))
    .collect()
}

/// The places within the clones and the mirror (451 T246): sized, each its own line, not added to the total again.
fn within_places(c: &Config) -> Vec<Place> {
    let inner = |name: String, budget: u64, entries| Place {
        name,
        budget,
        entries,
        within: true,
    };
    let gits = sweep::leftovers::git_dirs(c);
    vec![
        inner(
            "the tasks' scratch in the git directories <tree>/.git/t<N>*".to_owned(),
            GB,
            gits.iter()
                .flat_map(|g| {
                    dirs(g, &|n, _| task(n, 't'), &|_| {
                        "a task's scratch: make land takes its directory".to_owned()
                    })
                })
                .collect(),
        ),
        inner(
            "the handoff folders <tree>/.git/l7r-handoffs".to_owned(),
            GB / 2,
            gits.iter()
                .flat_map(|g| {
                    dirs(&g.join("l7r-handoffs"), &|_, _| true, &|n| {
                        if Path::new(n).extension().is_some_and(|x| x == "md") {
                            "a builder's handoff note".to_owned()
                        } else {
                            "a handoff's scratch: make land takes a folder".to_owned()
                        }
                    })
                })
                .collect(),
        ),
        inner(
            "the review snapshots <tree>/.git/review-snapshot".to_owned(),
            3 * GB / 2,
            gits.iter()
                .flat_map(|g| {
                    let snaps = g.join("review-snapshot");
                    dirs(&snaps, &|_, _| true, &|n| {
                        if snaps.join(n).join("tree.json").exists() {
                            "the review tree's: kept until taken again".to_owned()
                        } else {
                            format!(
                                "the sweep takes it idle {} days",
                                c.snapshot_age.as_secs() / 86_400
                            )
                        }
                    })
                })
                .collect(),
        ),
        inner(
            "the generation caches <tree>/.gencache".to_owned(),
            GB,
            sweep::leftovers::gencaches(c)
                .iter()
                .flat_map(|g| {
                    dirs(g, &|_, _| true, &|n| {
                        if sweep::leftovers::live_store(n) {
                            "the live cache".to_owned()
                        } else {
                            "a dead store: the sweep takes it idle".to_owned()
                        }
                    })
                })
                .collect(),
        ),
    ]
}

/// A Claude Code project slug of a path: every character but a letter or a digit a hyphen (`/diagram/.clones/x` is
/// `-diagram--clones-x`).
fn slug_of(path: &Path) -> String {
    path.to_string_lossy()
        .chars()
        .map(|ch| if ch.is_ascii_alphanumeric() { ch } else { '-' })
        .collect()
}

/// A name a task's number follows (`t204`, `t31-parked`, `t122-land.log`).
fn task(name: &str, prefix: char) -> bool {
    name.strip_prefix(prefix)
        .is_some_and(|r| r.starts_with(|ch: char| ch.is_ascii_digit()))
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
