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

pub(crate) mod disk;
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
    /// The cargo target cache (`~/.cache/l7r-cargo-target`, T102): one build directory a tree that builds, named for the tree.
    pub cargo: PathBuf,
    /// Where the session clones are (`/diagram/.clones`): a clone's build directory is never removed whole.
    pub clones: PathBuf,
    /// The mirror (`/diagram`), whose build directory holds the guard hook's kept binary, never removed whole.
    pub mirror: PathBuf,
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
    /// The free space the gate, the landing and the closing checks ask of the cache's disk, in bytes (`L7R_DISK_FLOOR_GB`, 451 T158).
    pub floor: u64,
    /// Idle longer than this and `make cache-clean` takes a build directory or a variant (`L7R_CACHE_IDLE_HOURS`, 451 T158).
    pub cache_age: Duration,
    /// Past this many bytes in all, the cache's share takes what is not in use whatever its age (`L7R_CACHE_BUDGET_GB`, 451 T158).
    pub budget: u64,
    /// Where a builder's scratch and a `mktemp -d` land (`/tmp`, `SCRATCH_SWEEP_TMP`), and how long one sits idle before it goes
    /// (`SCRATCH_SWEEP_TMP_HOURS`), and a task output (`SCRATCH_SWEEP_OUTPUT_HOURS`) (451 T158).
    pub tmp: PathBuf,
    pub tmp_age: Duration,
    pub outputs_age: Duration,
    /// This process's uid: only its own `/tmp` entries are judged.
    pub uid: u32,
    /// Below this share of the disk free, a prompt starts the cache's eviction (`L7R_DISK_FREE_PCT`, 451 T245), as a fraction.
    pub free_at: f64,
    /// The disk's size and free bytes where a test or a suite sets them (`SCRATCH_SWEEP_DF="<size> <free>"`); else `df` is asked.
    pub space: Option<(u64, u64)>,
    /// `~/.cache` and the guard log's directory, which `make disk-audit` sizes (451 T245).
    pub cache_home: PathBuf,
    pub guard_log: PathBuf,
}

impl Config {
    pub(crate) fn from_env(env: &dyn Fn(&str) -> Option<String>, uid: u32) -> Self {
        let set = |k: &str| env(k).filter(|v| !v.is_empty());
        let home = PathBuf::from(set("HOME").unwrap_or_default());
        let days: f64 = set("SCRATCH_SWEEP_DAYS")
            .and_then(|v| v.parse().ok())
            .filter(|d: &f64| d.is_finite() && *d >= 0.0)
            .unwrap_or(3.0);
        let knob = |k: &str, default: f64| {
            set(k)
                .and_then(|v| v.parse().ok())
                .filter(|n: &f64| n.is_finite() && *n >= 0.0)
                .unwrap_or(default)
        };
        let floor_gb = knob("L7R_DISK_FLOOR_GB", disk::FLOOR_GB);
        let cache_hours = knob("L7R_CACHE_IDLE_HOURS", disk::IDLE_HOURS);
        Self {
            root: set("SCRATCH_SWEEP_ROOT").map_or_else(
                || PathBuf::from(format!("/tmp/claude-{uid}")),
                PathBuf::from,
            ),
            projects: set("SCRATCH_SWEEP_PROJECTS")
                .map_or_else(|| home.join(".claude/projects"), PathBuf::from),
            cargo: set("SCRATCH_SWEEP_CARGO")
                .map_or_else(|| home.join(".cache/l7r-cargo-target"), PathBuf::from),
            clones: set("SCRATCH_SWEEP_CLONES")
                .map_or_else(|| PathBuf::from("/diagram/.clones"), PathBuf::from),
            mirror: set("SCRATCH_SWEEP_MIRROR")
                .map_or_else(|| PathBuf::from("/diagram"), PathBuf::from),
            sessions: set("SCRATCH_SWEEP_SESSIONS")
                .map_or_else(|| home.join(".claude/sessions"), PathBuf::from),
            state: set("SCRATCH_SWEEP_STATE")
                .map_or_else(|| home.join(".claude/scratch-sweep"), PathBuf::from),
            age: Duration::from_secs_f64(days * DAY),
            period: Duration::from_secs_f64(DAY),
            keep: set("CLAUDE_CODE_SESSION_ID").unwrap_or_default(),
            // a hook suite's stand-in process table (451 T158), so a build running elsewhere on the machine holds no fixture's cleanup
            proc: set("SCRATCH_SWEEP_PROC").map_or_else(|| PathBuf::from("/proc"), PathBuf::from),
            exe: std::env::current_exe().unwrap_or_default(),
            off: set("L7R_SELF_CHECK").is_some(),
            // whole bytes of a gigabyte (10^9, df's and the refusal's unit); the float's cast saturates and the knob is finite
            #[expect(
                clippy::cast_possible_truncation,
                clippy::cast_sign_loss,
                reason = "a finite, non-negative knob"
            )]
            floor: (floor_gb * 1e9) as u64,
            cache_age: Duration::from_secs_f64(cache_hours * 3600.0),
            #[expect(
                clippy::cast_possible_truncation,
                clippy::cast_sign_loss,
                reason = "a finite, non-negative knob"
            )]
            budget: (knob("L7R_CACHE_BUDGET_GB", disk::BUDGET_GB) * 1e9) as u64,
            tmp: set("SCRATCH_SWEEP_TMP").map_or_else(|| PathBuf::from("/tmp"), PathBuf::from),
            tmp_age: Duration::from_secs_f64(
                knob("SCRATCH_SWEEP_TMP_HOURS", disk::TMP_HOURS) * 3600.0,
            ),
            outputs_age: Duration::from_secs_f64(
                knob("SCRATCH_SWEEP_OUTPUT_HOURS", disk::TMP_HOURS) * 3600.0,
            ),
            uid,
            free_at: knob("L7R_DISK_FREE_PCT", disk::FREE_PCT) / 100.0,
            space: set("SCRATCH_SWEEP_DF").and_then(|v| {
                let (a, b) = v.split_once(' ')?;
                Some((a.trim().parse().ok()?, b.trim().parse().ok()?))
            }),
            cache_home: home.join(".cache"),
            guard_log: set("GUARD_LOG_DIR")
                .map_or_else(|| home.join(".claude/guard-log"), PathBuf::from),
        }
    }

    /// The cache's disk: its size and free bytes (`space`, else `df`); None where neither says.
    pub(crate) fn disk(&self) -> Option<(u64, u64)> {
        self.space.or_else(|| disk::df(&self.cargo))
    }

    /// The configuration from the environment, through `shared::env` (a test's own, feature 451 T32).
    fn read() -> Self {
        Self::from_env(&crate::shared::env::opt, uid())
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

/// Start a sweep, detached, when none ran within the period; below the disk's free-space share, start the eviction (451 T245); say
/// the line the last eviction wrote, once.
pub(crate) fn judge(event: &Event, c: &Config, now: SystemTime) -> Vec<Answer> {
    start(event, c, now);
    if c.off {
        return Vec::new();
    }
    let keep = event
        .input
        .get("session_id")
        .and_then(Value::as_str)
        .unwrap_or("");
    disk::trigger(c, keep, now);
    disk::note(c).map(Answer::Notice).into_iter().collect()
}

/// `judge`'s work, saying whether it started the sweep: the test of a prompt within the day asks this where it slept 0.3 s to see no
/// detached sweeper appear, a wait past FR-008's tenth of a second that proved nothing a slower start would not also pass (feature 449
/// T167).
fn start(event: &Event, c: &Config, now: SystemTime) -> bool {
    let keep = event
        .input
        .get("session_id")
        .and_then(Value::as_str)
        .unwrap_or("");
    // A SESSION'S FIRST PROMPT SWEEPS TOO (451 T158: "a sweep by age runs at session start ... for what a crash left"), on the same
    // prompt event the clone-sync guard syncs on: a session seen for the first time (no `seen/<id>` mark) starts a sweep however
    // recent the day's, as `now` (the lock, not the period); its marks go with the sweep once idle past the age.
    let seen = c.state.join("seen").join(keep);
    let first = !keep.is_empty() && !seen.exists();
    if c.off || !(first || c.due(now)) {
        return false;
    }
    if first {
        let _ = std::fs::create_dir_all(c.state.join("seen"));
        let _ = File::create(&seen);
    }
    let _ = Command::new("setsid")
        .arg("-f")
        .arg(&c.exe)
        .args([
            "--scratch-sweep",
            if first { "now" } else { "run" },
            "--keep",
            keep,
        ])
        .current_dir("/")
        .stdin(Stdio::null())
        .stdout(Stdio::null())
        .stderr(Stdio::null())
        .status();
    true
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
        // the disk and the build cache (451 T158, `disk.rs`)
        Some("floor") => disk::floor(c, disk::free(&c.cargo), now),
        Some(mode @ ("cache" | "cache-dry")) => disk::cache(c, now, mode == "cache-dry"),
        // the low-disk trigger's eviction and the audit (451 T245)
        Some(mode @ ("evict" | "evict-dry")) => disk::evict(c, now, mode == "evict-dry"),
        Some("audit") => disk::audit(c, now),
        Some("landed") => disk::landed(c, &args[1..], now),
        Some("trees") => say(
            disk::trees(c, now)
                .into_iter()
                .map(|t| t + "\n")
                .collect(),
            0,
        ),
        _ => Reply {
            stdout: String::new(),
            stderr: "usage: l7r-guard --scratch-sweep run | now | dry | floor | cache | cache-dry | evict | evict-dry | audit | trees [--keep <session id>]\n"
                .to_owned(),
            code: 2,
        },
    }
}

/// `work` under the sweep's lock, waited for a second at most; None where another sweep holds it or the state directory cannot be
/// made. A second, not none: a process another thread forks inherits the lock's description until its exec, and a test's cleanup
/// that met that instant was refused (observed 2026-11-22, one run in about five of the disk tests).
fn locked_by<T>(c: &Config, work: impl FnOnce() -> T) -> Option<T> {
    let _lock = crate::shared::tool::flock_within(&c.state.join("lock"), 1.0).ok()??;
    Some(work())
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
    let input = json!({ "session_id": c.keep });
    // the clean scratch worktrees first (451 T158), so their /tmp entries and build directories go in this same plan
    for tree in sweep::clean_trees(c, now) {
        record(
            &input,
            "removed",
            &tree.to_string_lossy(),
            json!({ "why": "a clean scratch worktree, idle, its HEAD on a ref" }),
        );
    }
    let plan = sweep::plan(c, now);
    let removed: Vec<sweep::Item> = plan.into_iter().filter(|i| sweep::take(c, i)).collect();
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
