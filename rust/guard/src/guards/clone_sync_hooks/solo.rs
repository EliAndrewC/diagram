//! Is this the only Claude Code session in the container (feature 444 T36; ported from `solo.py`, feature 449 T051)? The clone-sync prompt hook fetches main and merges it on every
//! message (0.65 s, measured 2026-11-07), because sessions run side by side; with no other session, main moves only when this one lands. The GM, 2026-11-07: "Can we also skip the
//! clone-sync hook on every message when no claude code session is running? And then cache the whether another claude code session is running for up to like 5 minutes so that the
//! check becomes extremely quick?" - and: "We should make sure not to count our own subagents, of course."
//!
//! WHAT COUNTS: every process named `claude` but this session's own and its descendants (a page session it started is its own work; a subagent runs inside the session's process). A
//! session that started this one is counted. Read from `/proc`. The answer is kept for `CACHE_S` seconds under `~/.cache/l7r/`, keyed by the session's process id.

use std::collections::{BTreeMap, HashMap};
use std::os::unix::fs::MetadataExt;
use std::path::Path;

use serde_json::{json, Map, Value};

const CACHE_S: f64 = 300.0;
const NAME: &str = "claude";

pub(crate) type Procs = HashMap<u32, (u32, String)>;

/// (parent pid, command name) from `/proc/<pid>/stat`: the name is between the first ( and the LAST ), since a name may hold either.
fn stat(dir: &Path) -> Option<(u32, String)> {
    let text = String::from_utf8_lossy(&std::fs::read(dir.join("stat")).ok()?).into_owned();
    let (open, close) = (text.find('(')?, text.rfind(')')?);
    let parent = text[close + 1..]
        .split_whitespace()
        .nth(1)
        .and_then(|f| f.parse().ok())
        .unwrap_or(0);
    Some((parent, text[open + 1..close].to_owned()))
}

/// Every process this one can read.
pub(crate) fn processes(proc: &Path) -> Procs {
    let dirs = std::fs::read_dir(proc).into_iter().flatten().flatten();
    dirs.filter_map(|d| Some((d.file_name().to_str()?.parse().ok()?, stat(&d.path())?)))
        .collect()
}

/// `start` and its ancestors only: the few reads that name the session.
pub(crate) fn chain(start: u32, proc: &Path) -> Procs {
    let (mut out, mut pid) = (Procs::new(), start);
    while pid > 1 && !out.contains_key(&pid) {
        let Some(found) = stat(&proc.join(pid.to_string())) else {
            break;
        };
        let next = found.0;
        out.insert(pid, found);
        pid = next;
    }
    out
}

fn ancestors(procs: &Procs, mut pid: u32) -> Vec<u32> {
    let mut out = Vec::new();
    while let Some((parent, _)) = procs
        .get(&pid)
        .filter(|(p, _)| *p != 0 && *p != pid && out.len() < 256)
    {
        pid = *parent;
        out.push(pid);
    }
    out
}

/// The `claude` process `start` runs under: itself, or its nearest such ancestor.
pub(crate) fn session(procs: &Procs, start: u32) -> Option<u32> {
    std::iter::once(start)
        .chain(ancestors(procs, start))
        .find(|p| procs.get(p).is_some_and(|(_, n)| n == NAME))
}

/// The `claude` processes that are neither this session nor one it started.
fn others(procs: &Procs, me: Option<u32>) -> Vec<u32> {
    let mine = |p: u32| Some(p) == me || me.is_some_and(|m| ancestors(procs, p).contains(&m));
    let mut out: Vec<u32> = procs
        .iter()
        .filter(|(p, (_, n))| n == NAME && !mine(**p))
        .map(|(p, _)| *p)
        .collect();
    out.sort_unstable();
    out
}

/// Is the session `start` runs under alone? Kept in `cache` for `CACHE_S` seconds per session.
pub(crate) fn solo(start: u32, cache: &Path, now: f64, procs_of: &dyn Fn() -> Procs) -> bool {
    let uid = std::fs::metadata("/proc/self").map_or(0, |m| m.uid());
    let key = cache.join(format!("solo-{uid}.json"));
    let kept: Map<String, Value> = std::fs::read_to_string(&key)
        .ok()
        .and_then(|t| serde_json::from_str(&t).ok())
        .unwrap_or_default();
    let young = |v: &Value| v.is_object() && now - v["t"].as_f64().unwrap_or(0.0) < CACHE_S;
    if let Some(entry) = kept.get(&start.to_string()).filter(|v| young(v)) {
        return entry["solo"].as_bool().unwrap_or(false);
    }
    let procs = procs_of();
    let alone = others(&procs, session(&procs, start)).is_empty();
    let mut fresh: BTreeMap<String, Value> = kept.into_iter().filter(|(_, v)| young(v)).collect();
    fresh.insert(start.to_string(), json!({"t": now, "solo": alone}));
    let _ = std::fs::create_dir_all(cache);
    let tmp = key.with_extension(format!("{}.tmp", std::process::id()));
    if std::fs::write(&tmp, json!(fresh).to_string()).is_ok() {
        let _ = std::fs::rename(&tmp, &key);
    }
    alone
}

/// The clone-sync hook's question. `L7R_SOLO=1` or `0` answers without looking (the hook's own test suite, or the GM's override).
pub(crate) fn alone(forced: Option<&str>, proc: &Path, cache: &Path, now: f64, own: u32) -> bool {
    match forced {
        Some("1") => true,
        Some("0") => false,
        _ => {
            let start = session(&chain(own, proc), own).unwrap_or(own);
            solo(start, cache, now, &|| processes(proc))
        }
    }
}

#[cfg(test)]
mod tests;
