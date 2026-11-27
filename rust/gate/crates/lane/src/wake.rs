//! THE COORDINATOR'S WAKE-UP (feature 461 T20, plan D9, FR-005): `l7r-gate lane wait` behind `make lane-wait`, which the
//! coordinator runs with `run_in_background: true` and so is woken when it exits. It blocks until the lane writes a line owed to the
//! coordinator past the read mark - a landed batch's one status line, a repair entry naming the fresh agent to dispatch, an arbiter
//! owed - prints those lines, moves the mark and exits 0. It has no ceiling of its own: it wakes the session only for what FR-005
//! lists. The mark is `l7r_shared::lane_wake`'s, which the prompt hook (`clone-sync-hooks`) reads too, so a wait killed early loses
//! nothing and a line the prompt showed is not shown again.
//!
//! THE RUNNER DEAD has no writer of its own: a killed runner writes nothing, and a runner that stopped on an error (a stopped carry, a
//! refused landing) writes its `stop` line but owes nothing, so a wait reading only `owed` lines would block for ever over a stranded
//! batch. So the wait writes that line itself ([`dead`]): no runner holds the lock, the log's last batch is open, and no such line was
//! written since the runner's last `start` - said once a death, so a re-armed wait blocks until the next start's lines - and held for
//! [`DEAD_GRACE_S`] first, so a runner a hand-in is still starting is not called dead. Its `owed` line carries `"why": "runner"`, the
//! key of "said once". A lane with no open batch is quiet whatever the runner does: an `idle` or `make lane-stop` end, and phase 1's
//! waiting hand-ins with no runner (the coordinator lands them by hand), wake no one. Label: the easier route (D9's "the runner dead",
//! read as a stranded batch, the one case in which no other line will come).
//!
//! Its command line is exactly `<dir>/l7r-gate lane wait`, no flag (its knobs from the environment), because the stall watchdog's
//! `waits_on_lane` (`stall_watchdog_hooks/pass.rs`, 461 T12) matches that argv.

use std::fmt::Write as _;
use std::path::Path;
use std::time::{Duration, SystemTime};

use l7r_gate_core::Reply;
use l7r_shared::lane_wake::take_unread;
use serde_json::json;

use crate::log::{self, Batch};
use crate::runner;

/// GUESS knob (`LANE_WAIT_POLL_S`): the wait's period. A line waits at most this long to wake the coordinator, against a gate of
/// minutes; each tick stats the log and probes the runner's lock, and reads the log only where the runner is gone.
pub const WAIT_POLL_S: f64 = 5.0;
/// GUESS knob (`LANE_DEAD_GRACE_S`): how long no runner must hold the lock over an open batch before the wait calls it dead - past a
/// start's `START_WAIT_S` (5 s) and a short rebuild of the lane tree's `l7r-gate` (461 T51), short against a gate's minutes.
pub const DEAD_GRACE_S: f64 = 30.0;
/// The `why` of the `owed` line the wait writes for a dead runner, the key of "said once a death".
pub const DEAD: &str = "runner";

/// What one wait reads and calls, handed in so a test drives it on a clock of its own.
pub struct Wait<'a> {
    pub common: &'a Path,
    pub poll_s: f64,
    pub grace_s: f64,
    /// Seconds since the epoch.
    pub now: &'a dyn Fn() -> f64,
    pub sleep: &'a dyn Fn(f64),
    /// Whether a runner holds the lane's lock.
    pub alive: &'a dyn Fn() -> bool,
}

/// The open batch a dead runner left, where the wait owes the coordinator that line (asked only once no runner holds the lock): the
/// log's last batch open, and no [`DEAD`] line since the last `start`.
#[must_use]
pub fn dead(lane: &[serde_json::Value]) -> Option<Batch> {
    let since = lane
        .iter()
        .rposition(|l| l["event"] == "start")
        .map_or(0, |i| i + 1);
    let told = lane[since..]
        .iter()
        .any(|l| l["event"] == "owed" && l["why"] == DEAD);
    if told {
        return None;
    }
    log::batches(lane).pop().filter(Batch::open)
}

/// The line a dead runner's batch owes: the batch, its changes, the runner's last stop (none where it was killed) and the command.
#[must_use]
pub fn dead_line(lane: &[serde_json::Value], b: &Batch) -> String {
    let last = lane
        .iter()
        .rev()
        .find(|l| l["event"] == "start" || l["event"] == "stop");
    let end = match last {
        Some(l) if l["event"] == "stop" => {
            format!("it stopped: {}", l["why"].as_str().unwrap_or_default())
        }
        _ => "it ended with no stop line (killed)".to_owned(),
    };
    format!(
        "lane: the runner is not running and batch {} is open ({} change(s), {}; {end}) - make lane-start resumes it",
        b.id,
        b.changes.len(),
        b.state
    )
}

/// The wait itself: the owed lines past the mark once there are any, a dead runner's line written first where it is owed.
///
/// # Errors
///
/// The dead runner's line that could not be written.
pub fn wait(w: &Wait) -> Result<Vec<String>, String> {
    // when the runner was first seen gone over a batch it stranded; reset whenever it is seen again or nothing is stranded
    let mut since: Option<f64> = None;
    loop {
        let lines = take_unread(w.common);
        if !lines.is_empty() {
            return Ok(lines);
        }
        let stranded = if (w.alive)() {
            None
        } else {
            let lane = log::read(w.common);
            dead(&lane).map(|b| (b.id.clone(), dead_line(&lane, &b)))
        };
        match stranded {
            Some((batch, line)) => {
                let first = *since.get_or_insert((w.now)());
                if (w.now)() - first >= w.grace_s {
                    let fields = json!({"batch": batch, "why": DEAD, "line": line});
                    log::append(
                        w.common,
                        &l7r_gate_core::record::repo::utc_now(),
                        "owed",
                        &fields,
                    )?;
                    continue;
                }
            }
            None => since = None,
        }
        (w.sleep)(w.poll_s);
    }
}

/// `l7r-gate lane wait`: [`wait`] with the standing seams, its lines printed, exit 0; a knob that is no number refused (exit 2), a
/// line it could not write an error (exit 1).
#[must_use]
pub fn wait_cli(common: &Path, env: &dyn Fn(&str) -> Option<String>) -> Reply {
    let knobs = runner::knob(env, "LANE_WAIT_POLL_S", WAIT_POLL_S)
        .and_then(|poll| Ok((poll, runner::knob(env, "LANE_DEAD_GRACE_S", DEAD_GRACE_S)?)));
    let (poll_s, grace_s) = match knobs {
        Ok(k) => k,
        Err(stderr) => {
            return Reply {
                stdout: String::new(),
                stderr,
                code: 2,
            }
        }
    };
    let now = || {
        SystemTime::now()
            .duration_since(SystemTime::UNIX_EPOCH)
            .unwrap_or_default()
            .as_secs_f64()
    };
    let sleep = |s: f64| std::thread::sleep(Duration::from_secs_f64(s.max(0.0)));
    let alive = || runner::held(common);
    let w = Wait {
        common,
        poll_s,
        grace_s,
        now: &now,
        sleep: &sleep,
        alive: &alive,
    };
    match wait(&w) {
        Ok(lines) => {
            let mut stdout = String::new();
            for l in lines {
                let _ = writeln!(stdout, "{l}");
            }
            Reply {
                stdout,
                stderr: String::new(),
                code: 0,
            }
        }
        Err(e) => Reply {
            stdout: String::new(),
            stderr: format!("{e}\n"),
            code: 1,
        },
    }
}

#[cfg(test)]
mod tests;
