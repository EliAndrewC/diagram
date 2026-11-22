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
mod tmp;
mod trees;

/// An entry the sweep removes: where, its size on disk, and why it is finished.
pub(crate) struct Item {
    pub path: PathBuf,
    pub bytes: u64,
    pub why: &'static str,
}

/// Every entry idle past the threshold and held by no live process, the current session's excepted.
pub(crate) fn plan(c: &Config, now: SystemTime) -> Vec<Item> {
    let (Some(root), Some(live)) = (real_root(&c.root), live_paths(&c.proc)) else {
        return Vec::new();
    };
    // a session whose process still runs is live however long its transcript has been quiet; where the registry cannot be read, no
    // session directory is judged at all
    let running = running_sessions(&c.sessions, &c.proc);
    let cutoff = now.checked_sub(c.age).unwrap_or(UNIX_EPOCH);
    let mut out = Vec::new();
    for (entry, name, meta) in children(&root) {
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
                Ok(_) | Err(_) => {}
            }
        }
    }
    let ago = |d: std::time::Duration| now.checked_sub(d).unwrap_or(UNIX_EPOCH);
    // an output inside a session already going whole is not listed twice
    for output in tmp::outputs(&root, ago(c.outputs_age)) {
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
    if building(&c.proc).is_none() {
        out.extend(cargo::plan(c, budgeted(c, cutoff, now), &live));
    }
    items(out, &live)
}

/// THE CACHE'S SIZE BUDGET (451 T158): past `L7R_CACHE_BUDGET_GB` in all, the cache's share takes every dead tree's build directory
/// and every variant past a crate's newest sixteen whatever its age - never one in use, never while a build runs - not only the idle.
fn budgeted(c: &Config, cutoff: SystemTime, now: SystemTime) -> SystemTime {
    let total: u64 = targets(c).iter().map(|t| t.bytes).sum();
    if total > c.budget {
        now
    } else {
        cutoff
    }
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

/// `make cache-clean`'s share alone (451 T158): the cargo target cache's entries idle since `cutoff`, none while a build runs
/// anywhere (Err names it) or where `/proc` cannot be read (Ok, nothing).
pub(crate) fn cache_plan(
    c: &Config,
    cutoff: SystemTime,
    now: SystemTime,
) -> Result<Vec<Item>, String> {
    if let Some(build) = building(&c.proc) {
        return Err(build);
    }
    let Some(live) = live_paths(&c.proc) else {
        return Ok(Vec::new());
    };
    Ok(items(
        cargo::plan(c, budgeted(c, cutoff, now), &live),
        &live,
    ))
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

pub(crate) use cargo::worktrees;
use cargo::Worktree;
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
