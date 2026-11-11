//! What the sweep removes: the root's own children and its slug directories' children, each read with `lstat` - a symlink is never
//! followed, never descended, never removed - and judged idle by the newest mtime anywhere inside (a session by its transcript where it
//! has one). Every live process's cwd, binary and open files are read from `/proc` first; an entry holding one is kept, and where
//! `/proc` cannot be read nothing is removed.

use std::fs::Metadata;
use std::os::unix::fs::MetadataExt;
use std::path::{Path, PathBuf};
use std::time::{SystemTime, UNIX_EPOCH};

use super::Config;

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
    out.into_iter()
        .filter(|(p, _)| !live.iter().any(|l| l.starts_with(p)))
        .map(|(path, why)| Item {
            bytes: bytes(&path),
            path,
            why,
        })
        .collect()
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
