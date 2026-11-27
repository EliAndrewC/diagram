//! The verification state (feature 449 T72, from `l7r/diagram/ci/state.py`): the most recent verification event, per clone, in `.git/verification-state.json`, so that a merge a day after the local check can
//! still lean on it. A source edit is not an event to catch: the record holds the content hash of the diagram area at the time of the run, and a later reader recomputes it. The GM's rulings on what counts
//! (2026-08-25, 2026-08-26, 2026-09-06) are in the git history of `state.py`.

use std::path::{Path, PathBuf};
use std::time::{SystemTime, UNIX_EPOCH};

use l7r_shared::log::civil;
use serde_json::{json, Value};

use crate::codeid::{parsed, stated};
use crate::{delta, stamp};

const GREEN: &str = "green-local";
const FAILED: &str = "failed-gate";
const NAME: &str = "verification-state.json";

/// One record, as `.git/verification-state.json` holds it.
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct State {
    pub event: String,
    pub target: String,
    pub utc: String,
    pub hash: String,
    pub commit: String,
    pub engine_key: String,
}

impl State {
    fn json(&self) -> Value {
        json!({"event": self.event, "target": self.target, "utc": self.utc, "hash": self.hash, "commit": self.commit, "engine_key": self.engine_key})
    }
}

/// Where the record lives for this checkout: a worktree's `.git` is a file naming its own git directory, so two worktrees of one repository never share a record.
fn state_file(root: &Path) -> PathBuf {
    let dotgit = root.join(".git");
    let text = std::fs::read_to_string(&dotgit).unwrap_or_default();
    match text.trim().strip_prefix("gitdir:") {
        Some(rest) => root.join(rest.trim()).join(NAME),
        None => dotgit.join(NAME),
    }
}

fn dir_of(root: &Path) -> PathBuf {
    state_file(root)
        .parent()
        .map_or_else(PathBuf::new, Path::to_path_buf)
}

fn text(data: &Value, key: &str) -> String {
    data[key].as_str().unwrap_or_default().to_owned()
}

/// # Errors
///
/// Where what it reads, writes or runs fails: the error says which and why.
pub fn read(root: &Path) -> Result<Option<State>, String> {
    let path = state_file(root);
    if !path.is_file() {
        return Ok(None);
    }
    let data = parsed(&stated(std::fs::read_to_string(&path), NAME)?, NAME)?;
    Ok(Some(State {
        event: text(&data, "event"),
        target: text(&data, "target"),
        utc: text(&data, "utc"),
        hash: text(&data, "hash"),
        commit: text(&data, "commit"),
        engine_key: text(&data, "engine_key"),
    }))
}

fn store(root: &Path, st: &State) -> Result<(), String> {
    let body = stated(
        serde_json::to_string_pretty(&st.json()).map_err(std::io::Error::other),
        NAME,
    )?;
    stated(std::fs::write(state_file(root), format!("{body}\n")), NAME)
}

fn clock() -> f64 {
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map_or(0.0, |d| d.as_secs_f64())
}

fn utc(secs: f64) -> String {
    let (y, mo, d, h, mi, s) = civil(secs.trunc().to_string().parse().unwrap_or(0));
    format!("{y:04}-{mo:02}-{d:02}T{h:02}:{mi:02}:{s:02}Z")
}

fn commit(root: &Path) -> String {
    let done = std::process::Command::new("git")
        .arg("-C")
        .arg(root)
        .args(["rev-parse", "--short", "HEAD"])
        .output();
    let out = done.map(|o| o.stdout).unwrap_or_default();
    String::from_utf8_lossy(&out).trim().to_owned()
}

/// A second red `make done` in a row owes the round arbiter a ruling before the next gate (feature 375 FR-010), unless the run is
/// the landing lane's own ([`lane_run`], 461 T17).
fn second_red_gate(root: &Path, now: f64) -> Result<(), String> {
    let trigger = format!("red-gate@{}", utc(now));
    l7r_shared::checks::with_owed(&dir_of(root), &mut |owed| {
        if let Some(map) = owed.as_object_mut() {
            map.insert(trigger.clone(), json!({"detail": "a second red make done in a row", "kind": "red-gate", "t": now, "unit": ""}));
        }
        true
    })
}

/// # Errors
///
/// Where what it reads, writes or runs fails: the error says which and why.
pub fn current_hash(root: &Path) -> Result<String, String> {
    stamp::area_key_named(root, "diagram")
}

/// # Errors
///
/// Where what it reads, writes or runs fails: the error says which and why.
pub fn write(root: &Path, event: &str, target: &str) -> Result<State, String> {
    let run = Run {
        batch: std::env::var("L7R_LANE_BATCH").unwrap_or_default(),
        me: std::process::id(),
    };
    record(root, event, target, &run)
}

/// Who runs the gate, as the red-gate tripwire asks (feature 461 T17): the batch `L7R_LANE_BATCH` names, and this process.
struct Run {
    batch: String,
    me: u32,
}

/// THE TRIPWIRE'S STAND-DOWN (feature 461 T17, plan D6 step 4; FR-008): a second red is left to the lane's own rule, which keys the
/// tripwire by task, only for a run that IS the lane's - `L7R_LANE_BATCH` set, the run in the lane's tree (the tree the pool's
/// registry holds under [`LANE`](l7r_shared::builder_pool::LANE), `<clone>-land` or the one `L7R_LANE_TREE` named at adoption, 461
/// T13), and either its batch open in `l7r-lane/lane.jsonl` or the run started by the runner holding `l7r-lane/lane.lock`. Anything
/// else - a by-hand `make land` with the variable exported, in the clone or in the lane's tree with no open batch - meets
/// [`second_red_gate`] as before, so the variable is no unrecorded escape. The tree is asked of every run, the runner too: the
/// stricter of the plan's two readings ("in the lane's tree AND its batch open, or started by the runner"), which costs the lane
/// nothing, since its every attempt runs there (D1).
fn lane_run(root: &Path, run: &Run) -> bool {
    if run.batch.is_empty() {
        return false;
    }
    let common = l7r_shared::checks::common_dir(root);
    let here = std::fs::canonicalize(root).unwrap_or_default();
    let in_tree = l7r_shared::builder_pool::read_all(&common)
        .iter()
        .any(|t| t.lane() && std::fs::canonicalize(&t.tree).is_ok_and(|p| p == here));
    in_tree && (batch_open(&common, &run.batch) || runner_started(&common, run.me))
}

/// A `batch` line naming `batch` with no `landed` or `stop` of it after (the lane's `log::Batch::open`, read here because the lane
/// crate builds on this one); a line that does not parse is skipped, as the lane skips it.
fn batch_open(common: &Path, batch: &str) -> bool {
    let text = std::fs::read_to_string(common.join("l7r-lane/lane.jsonl")).unwrap_or_default();
    let mut open = false;
    for line in text
        .lines()
        .filter_map(|l| serde_json::from_str::<Value>(l).ok())
    {
        if line["batch"] == batch {
            match line["event"].as_str().unwrap_or_default() {
                "batch" => open = true,
                "landed" | "stop" => open = false,
                _ => {}
            }
        }
    }
    open
}

/// The lane's runner holds its lock (the pid in the file read only while it is held, the lane's `runner::holder`) and `me` is
/// that pid or a descendant of it, walked up `/proc/<pid>/stat`.
fn runner_started(common: &Path, me: u32) -> bool {
    let lock = common.join("l7r-lane/lane.lock");
    let held = std::fs::File::open(&lock).is_ok_and(|f| !l7r_shared::tool::flock(&f, "-n"));
    let holder = std::fs::read_to_string(&lock)
        .ok()
        .and_then(|t| t.trim().parse::<u32>().ok());
    let Some(holder) = holder.filter(|_| held) else {
        return false;
    };
    let mut pid = me;
    while pid > 0 {
        if pid == holder {
            return true;
        }
        pid = parent(pid);
    }
    false
}

/// A process's parent, 0 where `/proc` does not say: the field after the state, past the command's closing parenthesis.
fn parent(pid: u32) -> u32 {
    let stat = std::fs::read_to_string(format!("/proc/{pid}/stat")).unwrap_or_default();
    let after = stat.rsplit_once(')').map_or("", |(_, rest)| rest);
    after
        .split_whitespace()
        .nth(1)
        .and_then(|p| p.parse().ok())
        .unwrap_or(0)
}

fn record(root: &Path, event: &str, target: &str, run: &Run) -> Result<State, String> {
    if event != GREEN && event != FAILED {
        return Err(format!(
            "unknown verification event '{event}' (want {GREEN} or {FAILED})"
        ));
    }
    let prior = read(root)?;
    if target == "done" {
        let last = dir_of(root).join("last-gate");
        if event == FAILED
            && std::fs::read_to_string(&last).unwrap_or_default().trim() == FAILED
            && !lane_run(root, run)
        {
            second_red_gate(root, clock())?;
        }
        stated(std::fs::write(&last, format!("{event}\n")), "last-gate")?;
    }
    let hash = current_hash(root)?;
    let engine_key = delta::engine_key_worktree(root)?;
    // a green subset never forgets a green gate on the same content (GM 2026-08-26): the record is one slot
    if let Some(standing) = prior.as_ref().filter(|p| {
        event == GREEN
            && target != "done"
            && p.event == GREEN
            && p.target == "done"
            && p.hash == hash
            && p.engine_key == engine_key
    }) {
        return Ok(standing.clone());
    }
    let st = State {
        event: event.to_owned(),
        target: target.to_owned(),
        utc: utc(clock()),
        hash,
        commit: commit(root),
        engine_key,
    };
    store(root, &st)?;
    Ok(st)
}

/// Whether a green `make done` already stands on exactly this content (feature 132 amendment, GM 2026-08-25), and why.
fn already_verified(root: &Path) -> Result<(bool, String), String> {
    let Some(st) = read(root)? else {
        return Ok((false, "no local check recorded in this clone".to_owned()));
    };
    let (at, sha) = (&st.utc, &st.commit);
    if st.event != GREEN || st.target != "done" {
        return Ok((
            false,
            format!(
                "the last record is `make {}` ({}) - only a green `make done` can be reused",
                st.target, st.event
            ),
        ));
    }
    if st.hash != current_hash(root)? {
        return Ok((false, format!("`make done` was green at {at} ({sha}), but the engine code it tested (Python, Rust, the pool's sources) changed since - that run vouched for different code")));
    }
    if st.engine_key.is_empty() || st.engine_key != delta::engine_key_worktree(root)? {
        return Ok((false, format!("`make done` was green at {at} ({sha}), but it recorded no engine key, or the engine content changed since - that run vouched for different content")));
    }
    Ok((true, format!("already verified: `make done` was green at {at} ({sha}) against exactly this engine content - nothing it exercises has changed (docs, the Makefile, config and scripts/ do not count)")))
}

/// `l7r-gate state write EVENT TARGET [reused] | read | dir | verified-done`.
pub fn cli(args: &[String], root: &Path) -> crate::Reply {
    let words: Vec<&str> = args.iter().map(String::as_str).collect();
    let verified = |(ok, why): (bool, String)| (format!("make done: {why}\n"), i32::from(!ok));
    let answer: Result<(String, i32), String> = match words.as_slice() {
        ["write", event, target] => write(root, event, target).map(|s| {
            (
                format!("verification-state: {} ({}) recorded\n", s.event, s.target),
                0,
            )
        }),
        ["write", event, target, "reused"] => write(root, event, target).map(|s| {
            (
                format!("verification-state: {} ({}) recorded\n", s.event, s.target),
                0,
            )
        }),
        ["read"] => read(root).map(|s| (format!("{}\n", s.map_or(Value::Null, |st| st.json())), 0)),
        ["dir"] => Ok((format!("{}\n", dir_of(root).display()), 0)),
        ["verified-done"] => already_verified(root).map(verified),
        _ => return crate::Reply {
            stdout: String::new(),
            stderr:
                "usage: l7r-gate state write EVENT TARGET [reused] | read | dir | verified-done\n"
                    .to_owned(),
            code: 2,
        },
    };
    match answer {
        Ok((stdout, code)) => crate::Reply {
            stdout,
            stderr: String::new(),
            code,
        },
        Err(why) => crate::Reply {
            stdout: String::new(),
            stderr: format!("l7r-gate state: {why}\n"),
            code: 1,
        },
    }
}

#[cfg(test)]
mod tests;
