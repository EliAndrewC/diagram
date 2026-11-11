//! `scratch-sweep-hooks` (feature 449 T103, FR-013; the GM: "Fix those leaks as well"): A FINISHED SESSION'S SCRATCH IS SWEPT.
//! Claude Code keeps each session's scratch and task output under `/tmp/claude-<uid>/<project slug>/<session id>/`, and agents left
//! loose files and trees beside them; nothing removed any of it, and it reached 38 GB (one session's scratch 20 GB). Once a day per
//! machine a prompt starts one sweep, detached, which removes a session's directory once its transcript has been idle three days and a
//! loose top-level entry once nothing inside it has changed in three days - never the prompting session's, never one a live process
//! has as its cwd, its binary or an open file ([`sweep`]), never through a symlink. Each removal and the total are on the guard log.
//!
//! Decisions: (a) the hook only reads the stamp's age - one `stat` - and the sweep is a detached process (`setsid -f`), so a 20 GB
//! walk costs no prompt anything; (b) the stamp is written under the lock BEFORE the walk, so a sweep that dies is not retried on every
//! prompt, and a second session finds the lock held or the stamp fresh; (c) the self-check starts no sweep; (d) `dry` neither takes the
//! lock nor touches the stamp.

use std::fs::File;
use std::os::unix::fs::MetadataExt;
use std::path::PathBuf;
use std::process::{Command, Stdio};
use std::time::{Duration, SystemTime};

use serde_json::{json, Value};

use crate::protocol::{Answer, Event, Guard, Reply};
use crate::shared::log;
use crate::shared::session::Session;
use crate::shared::tool::flock;

pub(crate) mod sweep;

/// The guard.
pub const GUARD: Guard = Guard {
    name: "scratch-sweep-hooks",
    events: &["UserPromptSubmit"],
    matcher: "*",
    decide,
};

const DAY: f64 = 86_400.0;

/// What the guard and its sweep read; every path and the clock's thresholds a seam, so the tests sweep a fixture tree.
pub(crate) struct Config {
    /// `/tmp/claude-<uid>`, the uid this process's own.
    pub root: PathBuf,
    /// `~/.claude/projects`, where each session's transcript says when it was last used.
    pub projects: PathBuf,
    /// Claude Code's registry of running sessions (`~/.claude/sessions`), read so a live session's scratch is never swept.
    pub sessions: PathBuf,
    /// The stamp and the lock (`~/.claude/scratch-sweep`), outside the root so they are never a loose entry.
    pub state: PathBuf,
    /// Idle longer than this and a session's scratch is finished (3 days, `SCRATCH_SWEEP_DAYS`).
    pub age: Duration,
    /// At most one sweep this often (1 day).
    pub period: Duration,
    /// The session never swept: the prompting one, else `CLAUDE_CODE_SESSION_ID`.
    pub keep: String,
    /// Where the live processes are read (`/proc`).
    pub proc: PathBuf,
    pub exe: PathBuf,
    pub off: bool,
}

impl Config {
    pub(crate) fn from_env(env: &dyn Fn(&str) -> Option<String>, uid: u32) -> Self {
        let set = |k: &str| env(k).filter(|v| !v.is_empty());
        let home = PathBuf::from(set("HOME").unwrap_or_default());
        let days: f64 = set("SCRATCH_SWEEP_DAYS")
            .and_then(|v| v.parse().ok())
            .filter(|d: &f64| d.is_finite() && *d >= 0.0)
            .unwrap_or(3.0);
        Self {
            root: set("SCRATCH_SWEEP_ROOT").map_or_else(
                || PathBuf::from(format!("/tmp/claude-{uid}")),
                PathBuf::from,
            ),
            projects: set("SCRATCH_SWEEP_PROJECTS")
                .map_or_else(|| home.join(".claude/projects"), PathBuf::from),
            sessions: set("SCRATCH_SWEEP_SESSIONS")
                .map_or_else(|| home.join(".claude/sessions"), PathBuf::from),
            state: set("SCRATCH_SWEEP_STATE")
                .map_or_else(|| home.join(".claude/scratch-sweep"), PathBuf::from),
            age: Duration::from_secs_f64(days * DAY),
            period: Duration::from_secs_f64(DAY),
            keep: set("CLAUDE_CODE_SESSION_ID").unwrap_or_default(),
            proc: PathBuf::from("/proc"),
            exe: std::env::current_exe().unwrap_or_default(),
            off: set("L7R_SELF_CHECK").is_some(),
        }
    }

    fn read() -> Self {
        Self::from_env(&|k| std::env::var(k).ok(), uid())
    }

    fn stamp(&self) -> PathBuf {
        self.state.join("stamp")
    }

    /// No sweep within the period: the stamp is missing, or older than a day (or from the future, a clock set back).
    fn due(&self, now: SystemTime) -> bool {
        match std::fs::metadata(self.stamp()).and_then(|m| m.modified()) {
            Ok(t) => !matches!(now.duration_since(t), Ok(d) if d < self.period),
            Err(_) => true,
        }
    }
}

/// This process's uid, from its own `/proc` entry - never a hard-coded 1000.
fn uid() -> u32 {
    std::fs::metadata("/proc/self").map_or(u32::MAX, |m| m.uid())
}

fn decide(event: &Event, _: &Session) -> Vec<Answer> {
    judge(event, &Config::read(), SystemTime::now())
}

/// Start a sweep, detached, when none ran within the period; says nothing.
pub(crate) fn judge(event: &Event, c: &Config, now: SystemTime) -> Vec<Answer> {
    if c.off || !c.due(now) {
        return Vec::new();
    }
    let keep = event
        .input
        .get("session_id")
        .and_then(Value::as_str)
        .unwrap_or("");
    let _ = Command::new("setsid")
        .arg("-f")
        .arg(&c.exe)
        .args(["--scratch-sweep", "run", "--keep", keep])
        .current_dir("/")
        .stdin(Stdio::null())
        .stdout(Stdio::null())
        .stderr(Stdio::null())
        .status();
    Vec::new()
}

/// `--scratch-sweep run` (the hook's: once a period), `now` (on demand: the lock, not the period) or `dry` (what either would remove),
/// each with `--keep <session id>`.
#[must_use]
pub fn cli(args: &[String]) -> Reply {
    with(args, &mut Config::read(), SystemTime::now())
}

pub(crate) fn with(args: &[String], c: &mut Config, now: SystemTime) -> Reply {
    let say = |stdout: String, code: i32| Reply {
        stdout,
        stderr: String::new(),
        code,
    };
    if let (Some("--keep"), Some(id)) = (args.get(1).map(String::as_str), args.get(2)) {
        c.keep.clone_from(id);
    }
    match args.first().map(String::as_str) {
        Some("dry") => {
            let plan = sweep::plan(c, now);
            say(report(&plan, "would remove"), 0)
        }
        Some(mode @ ("run" | "now")) => match locked(c, now, mode == "run") {
            Some(text) => say(text, 0),
            None => say(
                "scratch-sweep: another sweep holds the lock, or one ran within the day\n"
                    .to_owned(),
                0,
            ),
        },
        _ => Reply {
            stdout: String::new(),
            stderr: "usage: l7r-guard --scratch-sweep run | now | dry [--keep <session id>]\n"
                .to_owned(),
            code: 2,
        },
    }
}

/// Under the lock: the stamp written first (decision (b)), then the sweep, each removal and the total logged. None where another
/// holds the lock, or `periodic` and a sweep ran within the period.
fn locked(c: &Config, now: SystemTime, periodic: bool) -> Option<String> {
    std::fs::create_dir_all(&c.state).ok()?;
    let lock = File::create(c.state.join("lock")).ok()?;
    if !flock(&lock, "-n") || (periodic && !c.due(now)) {
        return None;
    }
    File::create(c.stamp()).ok()?.set_modified(now).ok()?;
    let plan = sweep::plan(c, now);
    let removed: Vec<sweep::Item> = plan.into_iter().filter(sweep::remove).collect();
    let input = json!({ "session_id": c.keep });
    for item in &removed {
        record(
            &input,
            "removed",
            &item.path.to_string_lossy(),
            json!({ "bytes": item.bytes, "why": item.why }),
        );
    }
    let total: u64 = removed.iter().map(|i| i.bytes).sum();
    record(
        &input,
        "swept",
        &format!("{} removed, {} freed", removed.len(), size(total)),
        json!({ "count": removed.len(), "bytes": total }),
    );
    Some(report(&removed, "removed"))
}

fn record(input: &Value, event: &str, detail: &str, context: Value) {
    let _ = log::write(&log::Entry {
        guard: "scratch-sweep",
        event,
        detail,
        rule: "scratch-sweep",
        context: Some(context),
        input,
        session_name: "",
    });
}

/// One line an entry, then the count and the total.
fn report(items: &[sweep::Item], verb: &str) -> String {
    let mut lines: Vec<String> = items
        .iter()
        .map(|i| format!("{verb} {} ({}, {})", i.path.display(), size(i.bytes), i.why))
        .collect();
    let total: u64 = items.iter().map(|i| i.bytes).sum();
    lines.push(format!(
        "scratch-sweep: {} entries, {} - {verb}",
        items.len(),
        size(total)
    ));
    lines.join("\n") + "\n"
}

/// Bytes as megabytes, to one place.
fn size(bytes: u64) -> String {
    let tenths = bytes / 100_000;
    format!("{}.{} MB", tenths / 10, tenths % 10)
}

#[cfg(test)]
mod tests;
