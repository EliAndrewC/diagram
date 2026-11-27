//! What the sweep removes: the root's own children and its slug directories' children, each read with `lstat` - a symlink is never
//! followed, never descended, never removed - and judged idle by the newest mtime anywhere inside (a session by its transcript where it
//! has one). Every live process's cwd, binary and open files are read from `/proc` first; an entry holding one is kept, and where
//! `/proc` cannot be read nothing is removed.

use std::fs::Metadata;
use std::os::unix::fs::MetadataExt;
use std::path::{Path, PathBuf};
use std::time::{SystemTime, UNIX_EPOCH};

use super::Config;

mod cargo;
mod evict;
pub(crate) mod leftovers;
mod prune;
#[cfg(test)]
pub(crate) use prune::WHY as PRUNED;
mod tmp;
mod trees;

/// An entry the sweep removes: where, its size on disk, and why it is finished.
pub(crate) struct Item {
    pub path: PathBuf,
    pub bytes: u64,
    pub why: &'static str,
}

/// Every entry idle past the threshold and held by no live process, the current session's excepted: the age shares, then the
/// cache's.
pub(crate) fn plan(c: &Config, now: SystemTime) -> Vec<Item> {
    let (Some(root), Some(live)) = (real_root(&c.root), live_paths(&c.proc)) else {
        return Vec::new();
    };
    let mut out = aged(c, &root, now);
    if building(&c.proc).is_none() {
        let cutoff = now.checked_sub(c.age).unwrap_or(UNIX_EPOCH);
        let (cut, budget) = budgeted(c, cutoff, now, 0);
        out.extend(cargo::plan(c, cut, &live, budget));
    }
    items(merge(out, prune::plan(c, &live)), &live)
}

/// The prune's entries (451 T515, `prune.rs`) beside a plan, those at or under one of its paths left out (a dead build directory
/// going whole, a profile evicted, a variant listed already).
fn merge(
    mut out: Vec<(PathBuf, &'static str)>,
    pruned: Vec<(PathBuf, &'static str)>,
) -> Vec<(PathBuf, &'static str)> {
    let planned: std::collections::BTreeSet<PathBuf> = out.iter().map(|(p, _)| p.clone()).collect();
    out.extend(
        pruned
            .into_iter()
            .filter(|(p, _)| !p.ancestors().any(|a| planned.contains(a))),
    );
    out
}

/// The age shares alone, held by no live process (451 T246: the low-disk trigger runs them too, a build running or not).
pub(crate) fn aged_plan(c: &Config, now: SystemTime) -> Vec<Item> {
    let (Some(root), Some(live)) = (real_root(&c.root), live_paths(&c.proc)) else {
        return Vec::new();
    };
    items(aged(c, &root, now), &live)
}

/// Every share judged by age: the root's sessions, loose entries and finished sessions' scratchpad entries, the task outputs, `/tmp`'s
/// scratch, the first-prompt marks, and the clones' review snapshots and dead generation-cache stores (451 T246, `leftovers.rs`).
fn aged(c: &Config, root: &Path, now: SystemTime) -> Vec<(PathBuf, &'static str)> {
    // a session whose process still runs is live however long its transcript has been quiet; where the registry cannot be read, no
    // session directory is judged at all
    let running = running_sessions(&c.sessions, &c.proc);
    let cutoff = now.checked_sub(c.age).unwrap_or(UNIX_EPOCH);
    let mut out = Vec::new();
    for (entry, name, meta) in children(root) {
        if !(name.starts_with('-') && meta.is_dir()) {
            if idle(&entry, cutoff) {
                out.push((entry, "loose, nothing inside changed"));
            }
            continue;
        }
        let Some(running) = running.as_ref() else {
            continue;
        };
        for (session, id, _) in children(&entry) {
            if id == c.keep || running.contains(&id) {
                continue;
            }
            let transcript = c.projects.join(&name).join(format!("{id}.jsonl"));
            match std::fs::metadata(&transcript).and_then(|m| m.modified()) {
                // both: a subagent writing into its session's scratch moves no line of the session's own transcript
                Ok(t) if t < cutoff && idle(&session, cutoff) => {
                    out.push((session, "its transcript idle, nothing inside changed"));
                }
                Err(_) if idle(&session, cutoff) => {
                    out.push((session, "no transcript, nothing inside changed"));
                }
                // A FINISHED SESSION'S SCRATCHPAD, ENTRY BY ENTRY (451 T246): a session no process runs whose transcript moved within
                // the threshold (resumed, or written by a subagent) kept its whole scratchpad - 12.8 GB of one session's on 2026-11-25,
                // every file of it over three days old (`find -mtime +3` summed), its pid gone. Each top-level entry of its
                // `scratchpad/` goes once nothing inside changed; a running session's, and the prompting one's, are never judged.
                Ok(_) | Err(_) => out.extend(
                    children(&session.join("scratchpad"))
                        .into_iter()
                        .filter(|(p, _, _)| idle(p, cutoff))
                        .map(|(p, _, _)| {
                            (
                                p,
                                "a finished session's scratchpad entry, nothing inside changed",
                            )
                        }),
                ),
            }
        }
    }
    let ago = |d: std::time::Duration| now.checked_sub(d).unwrap_or(UNIX_EPOCH);
    // an output inside a session already going whole is not listed twice
    for output in tmp::outputs(root, ago(c.outputs_age)) {
        if !out.iter().any(|(p, _)| output.0.starts_with(p)) {
            out.push(output);
        }
    }
    out.extend(tmp::idle_scratch(c, ago(c.tmp_age)));
    // a session's first-prompt mark (451 T158), kept a month: one gone too soon only sweeps once more
    out.extend(
        children(&c.state.join("seen"))
            .into_iter()
            .filter(|(p, _, _)| idle(p, ago(std::time::Duration::from_secs(30 * 86_400))))
            .map(|(p, _, _)| (p, "a session's first-prompt mark")),
    );
    out.extend(leftovers::snapshots(c, ago(c.snapshot_age)));
    out.extend(leftovers::dead_stores(c, cutoff));
    out
}

/// The landed tasks' own directories in the git directory `git` (451 T246, `leftovers::landed`), held by no live process; none where
/// `/proc` cannot be read.
pub(crate) fn landed_leftovers(c: &Config, git: &Path, numbers: &[u64]) -> Vec<Item> {
    let Some(live) = live_paths(&c.proc) else {
        return Vec::new();
    };
    items(leftovers::landed(git, numbers), &live)
}

/// THE CACHE'S SIZE BUDGET (451 T158): past `L7R_CACHE_BUDGET_GB` in all, the cache's share takes every dead tree's build directory
/// and every variant past a crate's newest sixteen whatever its age - never one in use, never while a build runs - not only the idle;
/// and (451 T245, `evict.rs`) live trees' idle profiles until the cache is back within it, or `short` more bytes are free (the
/// low-disk trigger's shortfall), whichever asks more.
fn budgeted(
    c: &Config,
    cutoff: SystemTime,
    now: SystemTime,
    short: u64,
) -> (SystemTime, cargo::Budget) {
    let total: u64 = targets(c).iter().map(|t| t.bytes).sum();
    let budget = cargo::Budget {
        need: total.saturating_sub(c.budget).max(short),
        idle: now.checked_sub(c.cache_age).unwrap_or(UNIX_EPOCH),
    };
    (if total > c.budget { now } else { cutoff }, budget)
}

/// The landed tasks' own `/tmp` scratch (`tmp::landed`), held by no live process; with the numbers another feature shares.
pub(crate) fn landed_plan(
    c: &Config,
    feature: &str,
    numbers: &[u64],
    starts: &Path,
    now: SystemTime,
) -> (Vec<Item>, Vec<u64>) {
    let Some(live) = live_paths(&c.proc) else {
        return (Vec::new(), Vec::new());
    };
    let (gone, shared) = tmp::landed(c, feature, numbers, starts, now);
    (items(gone, &live), shared)
}

fn items(found: Vec<(PathBuf, &'static str)>, live: &[PathBuf]) -> Vec<Item> {
    found
        .into_iter()
        .filter(|(p, _)| !live.iter().any(|l| l.starts_with(p)))
        .map(|(path, why)| Item {
            bytes: bytes(&path),
            path,
            why,
        })
        .collect()
}

/// `make cache-clean`'s share alone (451 T158): the cargo target cache's entries idle since `cutoff`, and the build that holds the
/// rest - the prune inside live profiles (451 T515) is planned while a build runs elsewhere, every other share waits for none to run;
/// nothing where `/proc` cannot be read.
pub(crate) fn cache_plan(
    c: &Config,
    cutoff: SystemTime,
    now: SystemTime,
    short: u64,
) -> (Vec<Item>, Option<String>) {
    let Some(live) = live_paths(&c.proc) else {
        return (Vec::new(), None);
    };
    let build = building(&c.proc);
    let rest = if build.is_none() {
        let (cut, budget) = budgeted(c, cutoff, now, short);
        cargo::plan(c, cut, &live, budget)
    } else {
        Vec::new()
    };
    (items(merge(rest, prune::plan(c, &live)), &live), build)
}

/// Remove one entry of the plan unless a build has started since it was made (451 T245: an eviction walks for seconds, and a build
/// begun meanwhile holds its profile from the moment it starts); the prune's entry (451 T515) unless a build read or wrote it since;
/// whether it went.
pub(crate) fn take(c: &Config, item: &Item) -> bool {
    let free = if item.why == prune::WHY {
        prune::still_stale(c, &item.path, SystemTime::now())
    } else {
        !item.path.starts_with(&c.cargo) || building(&c.proc).is_none()
    };
    free && remove(item)
}

/// The first live cargo, rustc or clippy process (`/proc/<pid>/comm`), as `<pid> <name>`: a build runs, so the cache's share waits
/// (451 T158; the run lock's record alone misses a bare `cargo build`).
pub(crate) fn building(proc: &Path) -> Option<String> {
    const BUILDERS: [&str; 4] = ["cargo", "rustc", "clippy-driver", "cargo-llvm-cov"];
    std::fs::read_dir(proc)
        .into_iter()
        .flatten()
        .flatten()
        .find_map(|e| {
            let comm = std::fs::read_to_string(e.path().join("comm")).unwrap_or_default();
            let name = comm.trim();
            BUILDERS
                .contains(&name)
                .then(|| format!("{} {name}", e.file_name().to_string_lossy()))
        })
}

/// One build directory of the cache: its name, its size on disk, whether a live tree's (never removed whole), and when anything in
/// it last changed.
pub(crate) struct Target {
    pub name: String,
    pub bytes: u64,
    pub live: bool,
    pub newest: SystemTime,
}

/// Every build directory of the cache, largest first (the floor's refusal, 451 T158).
pub(crate) fn targets(c: &Config) -> Vec<Target> {
    let live = cargo::trees(c).unwrap_or_default();
    let mut out: Vec<Target> = children(&c.cargo)
        .into_iter()
        .filter(|(_, _, m)| m.is_dir())
        .map(|(path, name, _)| Target {
            bytes: bytes(&path),
            live: live.contains(&name),
            newest: newest(&path).unwrap_or(UNIX_EPOCH),
            name,
        })
        .collect();
    out.sort_by(|a, b| b.bytes.cmp(&a.bytes));
    out
}

use cargo::Worktree;
pub(crate) use cargo::{worktrees, BUILT_INTO};
#[cfg(test)]
pub(crate) use trees::fixture;

/// The clean, idle scratch worktrees, removed (451 T158, `sweep/trees.rs`): the trees that went; none where `/proc` cannot be read.
pub(crate) fn clean_trees(c: &Config, now: SystemTime) -> Vec<PathBuf> {
    let Some(live) = live_paths(&c.proc) else {
        return Vec::new();
    };
    let cutoff = now.checked_sub(c.tmp_age).unwrap_or(UNIX_EPOCH);
    trees::remove_clean(c, cutoff, &live)
}

/// The build directories of the trees just removed (451 T245), each named for its tree's basename and taken once proven dead (another
/// tree of that name keeps it), none in use, none while a build runs.
pub(crate) fn gone_targets(c: &Config, removed: &[PathBuf]) -> Vec<Item> {
    let Some(live) = live_paths(&c.proc) else {
        return Vec::new();
    };
    if removed.is_empty() || building(&c.proc).is_some() {
        return Vec::new();
    }
    let names = cargo::trees(c);
    let found = removed
        .iter()
        .filter_map(|t| t.file_name())
        .map(|n| n.to_string_lossy().into_owned())
        .map(|n| (c.cargo.join(&n), n))
        .filter(|(t, n)| {
            t.is_dir() && !cargo::in_use(t, &live, &c.proc) && cargo::dead(t, n, names.as_deref())
        })
        .map(|(t, _)| {
            (
                t,
                "the build directory of the scratch worktree removed with it",
            )
        })
        .collect();
    items(found, &live)
}

/// Remove one entry, a directory's tree without following any symlink in it; whether it went.
pub(crate) fn remove(item: &Item) -> bool {
    match std::fs::symlink_metadata(&item.path) {
        Ok(m) if m.is_dir() => std::fs::remove_dir_all(&item.path).is_ok(),
        Ok(_) => std::fs::remove_file(&item.path).is_ok(),
        Err(_) => false,
    }
}

/// The root, resolved, only where it is itself a directory and not a symlink to one.
fn real_root(root: &Path) -> Option<PathBuf> {
    let m = std::fs::symlink_metadata(root).ok()?;
    if !m.is_dir() {
        return None;
    }
    std::fs::canonicalize(root).ok()
}

/// A directory's entries that are not symlinks, with their names and `lstat`.
fn children(dir: &Path) -> Vec<(PathBuf, String, Metadata)> {
    std::fs::read_dir(dir)
        .into_iter()
        .flatten()
        .flatten()
        .filter_map(|e| {
            let path = e.path();
            let meta = std::fs::symlink_metadata(&path).ok()?;
            let name = e.file_name().to_string_lossy().into_owned();
            (!meta.file_type().is_symlink()).then_some((path, name, meta))
        })
        .collect()
}

/// `path` and everything under it, each `lstat`ed and handed to `visit`, never through a symlink: false as soon as `visit` says
/// stop or a directory cannot be read.
fn walk(path: &Path, mut visit: impl FnMut(&Metadata) -> bool) -> bool {
    let mut stack: Vec<(PathBuf, Metadata)> = lstat(path).into_iter().collect();
    while let Some((p, m)) = stack.pop() {
        if !visit(&m) {
            return false;
        }
        if m.is_dir() {
            let Ok(entries) = std::fs::read_dir(&p) else {
                return false;
            };
            stack.extend(entries.flatten().filter_map(|e| lstat(&e.path())));
        }
    }
    true
}

fn lstat(p: &Path) -> Option<(PathBuf, Metadata)> {
    std::fs::symlink_metadata(p)
        .ok()
        .map(|m| (p.to_path_buf(), m))
}

/// The newest mtime at or under `path`; None where a directory in it cannot be read.
pub(crate) fn newest(path: &Path) -> Option<SystemTime> {
    let mut latest = UNIX_EPOCH;
    let read = walk(path, |m| {
        latest = latest.max(m.modified().unwrap_or(UNIX_EPOCH));
        true
    });
    read.then_some(latest)
}

/// Nothing at or under `path` modified at or after `cutoff`; a directory that cannot be read is not idle.
fn idle(path: &Path, cutoff: SystemTime) -> bool {
    walk(path, |m| m.modified().is_ok_and(|t| t < cutoff))
}

/// The blocks `path` and everything under it hold on disk, and the newest mtime there, in one walk (`make disk-audit`, 451 T245).
pub(crate) fn measure(path: &Path) -> (u64, SystemTime) {
    let (mut total, mut latest) = (0, UNIX_EPOCH);
    walk(path, |m| {
        total += m.blocks() * 512;
        latest = latest.max(m.modified().unwrap_or(UNIX_EPOCH));
        true
    });
    (total, latest)
}

/// A directory's entries that are not symlinks (`make disk-audit`'s listing, 451 T245).
pub(crate) fn entries(dir: &Path) -> Vec<(PathBuf, String, Metadata)> {
    children(dir)
}

/// The blocks `path` and everything under it hold on disk, symlinks counted as themselves.
fn bytes(path: &Path) -> u64 {
    let mut total = 0;
    walk(path, |m| {
        total += m.blocks() * 512;
        true
    });
    total
}

/// The ids of the sessions Claude Code records as running (`~/.claude/sessions/<pid>.json`: `pid`, `sessionId`, `procStart`), each
/// only while that pid still runs and started when the record says (`/proc/<pid>/stat`'s 22nd field), so a reused pid keeps nothing;
/// None where the registry cannot be listed.
fn running_sessions(registry: &Path, proc: &Path) -> Option<Vec<String>> {
    let records = std::fs::read_dir(registry).ok()?;
    let started = |pid: u64| {
        let stat = std::fs::read_to_string(proc.join(pid.to_string()).join("stat")).ok()?;
        let after = stat.rsplit_once(") ")?.1;
        after.split_whitespace().nth(19).map(str::to_owned)
    };
    Some(
        records
            .flatten()
            .filter(|e| e.path().extension().is_some_and(|x| x == "json"))
            .filter_map(|e| {
                let v: serde_json::Value =
                    serde_json::from_str(&std::fs::read_to_string(e.path()).ok()?).ok()?;
                let pid = v.get("pid")?.as_u64()?;
                let since = v.get("procStart")?.as_str()?;
                (started(pid)? == since)
                    .then(|| v.get("sessionId")?.as_str().map(str::to_owned))
                    .flatten()
            })
            .collect(),
    )
}

/// Every live process's cwd, binary and open files that this user can read; None where the process table cannot be listed.
fn live_paths(proc: &Path) -> Option<Vec<PathBuf>> {
    let pids = std::fs::read_dir(proc).ok()?;
    let mut out = Vec::new();
    for pid in pids.flatten() {
        let dir = pid.path();
        if !pid
            .file_name()
            .to_string_lossy()
            .bytes()
            .all(|b| b.is_ascii_digit())
        {
            continue;
        }
        let fds = std::fs::read_dir(dir.join("fd"))
            .into_iter()
            .flatten()
            .flatten()
            .map(|e| e.path());
        let links = [dir.join("cwd"), dir.join("exe")].into_iter().chain(fds);
        out.extend(links.filter_map(|l| std::fs::read_link(l).ok()));
    }
    Some(out)
}
