//! THE COORDINATOR'S WAKE-UP (feature 461 T20, plan D9, FR-005): `l7r-gate lane wait` behind `make lane-wait`, which the
//! coordinator runs with `run_in_background: true` and so is woken when it exits. It blocks until the lane writes a line owed to the
//! coordinator past the read mark - a landed batch's one status line, a repair entry naming the fresh agent to dispatch, an arbiter
//! owed - prints those lines, moves the mark and exits 0. It has no ceiling of its own: it wakes the session only for what FR-005
//! lists. The mark is `l7r_shared::lane_wake`'s, which the prompt hook (`clone-sync-hooks`) reads too, so a wait killed early loses
//! nothing and a line the prompt showed is not shown again.
//!
//! THE RUNNER DEAD has no writer of its own: a killed runner writes nothing, and a runner that stopped on an error (a stopped carry, a
//! refused landing) writes its `stop` line but owes nothing, so a wait reading only `owed` lines would block for ever over a stranded
//! batch. So the wait writes that line itself ([`dead`]): no runner holds the lock, the log's last batch is open, and no `owed` line
//! naming it (such a line, or the runner's own red line) was written since the runner's last `start` - said once a death, so a re-armed wait blocks until the next start's lines - and held for
//! [`DEAD_GRACE_S`] first, so a runner a hand-in is still starting is not called dead. Its `owed` line carries `"why": "runner"`, the
//! key of "said once". In PHASE 1 a lane with no open batch is quiet whatever the runner does: an `idle` or `make lane-stop` end, and
//! waiting hand-ins with no runner (the coordinator lands them by hand), wake no one. Label: the easier route (D9's "the runner dead",
//! read as a stranded batch, the one case in which no other line will come).
//!
//! FROM PHASE 2'S BASE (`l7r_shared::lane_wake::origin_base`, 461 T56) every hand-in starts the runner, so a WAITING hand-in no runner
//! serves past the grace is a runner that died or never started (its start's `START_WAIT_S` passed, T51), and nothing else will
//! come - while the Stop rule keeps this wait armed over it (`lane_wake::holds`, 461 T64). So with no batch open the wait says it
//! once ([`unserved`]): one `owed` line, `"why": "runner"`, the hand-ins' commits under `unserved` (a key `log::mentions` does not
//! read, so the line moves no hand-in's state), said once a hand-in a start - a failed start writes no `start` line, so the key is
//! the commit, not the death, and a later hand-in whose start fails too is said itself. A hand-in older than a `make lane-stop` since
//! the last start is quiet: the coordinator stopped the runner over it on purpose (a decision, the easier route; one handed in after
//! the stop starts a runner, and its failure is said).
//!
//! Its command line is exactly `<dir>/l7r-gate lane wait`, no flag (its knobs from the environment), because the stall watchdog's
//! `waits_on_lane` (`stall_watchdog_hooks/pass.rs`, 461 T12) matches that argv.

use std::collections::BTreeSet;
use std::fmt::Write as _;
use std::path::Path;
use std::time::{Duration, SystemTime};

use l7r_gate_core::Reply;
use l7r_gate_task::builder_done::{held_by, REFS};
use l7r_shared::lane_wake::take_unread;
use serde_json::json;

use crate::log::{self, Batch, HandIn};
use crate::runner;

/// GUESS knob (`LANE_WAIT_POLL_S`): the wait's period. A line waits at most this long to wake the coordinator, against a gate of
/// minutes; each tick stats the log and probes the runner's lock, and reads the log only where the runner is gone.
pub const WAIT_POLL_S: f64 = 5.0;
/// GUESS knob (`LANE_DEAD_GRACE_S`): how long no runner must hold the lock over an open batch before the wait calls it dead - past a
/// start's `START_WAIT_S` (5 s) and a short rebuild of the lane tree's `l7r-gate` (461 T51), short against a gate's minutes.
pub const DEAD_GRACE_S: f64 = 30.0;
/// The `why` of the `owed` line the wait writes for a dead runner, the key of "said once a death".
pub const DEAD: &str = "runner";
/// The field of the runner's own `owed` line that says it stopped with its batch open (461 T15), so no death line follows it.
pub const STOPPED: &str = "stopped";

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
    /// The hand-ins waiting ([`waiting_on`]), asked only from phase 2's base (461 T56): none in phase 1, whose hand-ins start no runner.
    pub waiting: Option<&'a dyn Fn() -> Vec<HandIn>>,
}

/// The open batch a dead runner left, where the wait owes the coordinator that line (asked only once no runner holds the lock): the
/// log's last batch open, and no `owed` line since the last `start` that tells its death - a [`DEAD`] line, or the runner's own line
/// for that batch that it stopped with the batch open ([`STOPPED`]: today a `make land` with no exit code, `run.rs`), after which a
/// death line would wake the coordinator twice for one stop, a wake FR-005 does not list (461 T20's plan review). WHY that field and
/// not any line of the batch (T20's rule, written for T14's red stand-in, which stopped the runner): since T15 a red attempt's
/// ejection owes its line and the runner goes on to the next attempt, so a runner killed after it left an open batch no line said.
#[must_use]
pub fn dead(lane: &[serde_json::Value]) -> Option<Batch> {
    let since = lane
        .iter()
        .rposition(|l| l["event"] == "start")
        .map_or(0, |i| i + 1);
    let open = log::batches(lane).pop().filter(Batch::open)?;
    let told = lane[since..].iter().any(|l| {
        l["event"] == "owed"
            && (l["why"] == DEAD || (l["batch"] == open.id.as_str() && l[STOPPED] == true))
    });
    (!told).then_some(open)
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

/// The hand-ins of `waiting` no runner serves that the wait owes the coordinator a line for (asked only with no runner, from phase
/// 2's base, 461 T56): none while a batch is open (its own death line, [`dead`], says it); else each not named under `unserved` by a
/// [`DEAD`] line since the last `start`, nor handed in before a `make lane-stop` since it.
#[must_use]
pub fn unserved(lane: &[serde_json::Value], waiting: &[HandIn]) -> Vec<HandIn> {
    if log::batches(lane).iter().any(Batch::open) {
        return Vec::new();
    }
    let since = lane
        .iter()
        .rposition(|l| l["event"] == "start")
        .map_or(0, |i| i + 1);
    let after = &lane[since..];
    let told = |c: &str| {
        after.iter().any(|l| {
            l["event"] == "owed"
                && l["why"] == DEAD
                && l["unserved"]
                    .as_array()
                    .is_some_and(|a| a.iter().any(|s| s == c))
        })
    };
    // a `make lane-stop` (or `NOW=1`) the runner's last stop since its start: the hand-ins before it stopped over on purpose
    let stopped = after
        .iter()
        .rev()
        .find(|l| l["event"] == "stop")
        .filter(|l| {
            l["why"]
                .as_str()
                .is_some_and(|w| w.starts_with("make lane-stop"))
        })
        .and_then(|l| l["utc"].as_str());
    waiting
        .iter()
        .filter(|h| !told(&h.commit) && stopped.is_none_or(|s| h.at.as_str() > s))
        .cloned()
        .collect()
}

/// The line the hand-ins no runner serves owe: each, and the runner's last line.
#[must_use]
pub fn unserved_line(lane: &[serde_json::Value], hs: &[HandIn]) -> String {
    let named: Vec<String> = hs
        .iter()
        .map(|h| {
            let short = h.commit.get(..10).unwrap_or(&h.commit);
            format!("{} {} ({short})", h.feature, h.tasks.join(","))
        })
        .collect();
    let last = lane
        .iter()
        .rev()
        .find(|l| l["event"] == "start" || l["event"] == "stop");
    let end = match last {
        Some(l) if l["event"] == "stop" => {
            format!("it stopped: {}", l["why"].as_str().unwrap_or_default())
        }
        Some(_) => "it ended with no stop line (killed)".to_owned(),
        None => "no runner has started".to_owned(),
    };
    format!(
        "lane: the runner is not running and {} hand-in(s) wait with no batch formed ({}; {end}) - make lane-start starts it",
        hs.len(),
        named.join(", ")
    )
}

/// The hand-ins on the lane of `common` that wait, read as `make lane` reads them (`lane.rs`'s `status`): the pool's log, the done
/// refs and the lane's log, then `origin/main` asked only of the waiting ones (a hand-in it holds has landed), so a poll with
/// nothing waiting walks no history.
#[must_use]
pub fn waiting_on(common: &Path) -> Vec<HandIn> {
    let pool = log::lines_of(&common.join(l7r_shared::builder_queue::LOG));
    let all = log::hand_ins(&pool);
    if all.is_empty() {
        return all;
    }
    let refs: BTreeSet<String> =
        crate::lane::git(common, &["for-each-ref", "--format=%(objectname)", REFS])
            .unwrap_or_default()
            .lines()
            .map(str::to_owned)
            .collect();
    // `origin/main` not yet asked: a hand-in it holds reads as waiting here, and is dropped below (the Stop rule's assembly, 461 T63)
    let waiting = l7r_shared::lane_log::waiting_unasked(&all, &refs, &log::read(common));
    if waiting.is_empty() {
        return waiting;
    }
    let commits: Vec<String> = waiting.iter().map(|h| h.commit.clone()).collect();
    let on_main = held_by(common, "origin/main", &commits);
    waiting
        .into_iter()
        .filter(|h| !on_main.contains(&h.commit))
        .collect()
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
            dead(&lane)
                .map(|b| (json!({"batch": b.id}), dead_line(&lane, &b)))
                .or_else(|| {
                    let hs = unserved(&lane, &(w.waiting?)());
                    let shas: Vec<&str> = hs.iter().map(|h| h.commit.as_str()).collect();
                    (!hs.is_empty()).then(|| (json!({"unserved": shas}), unserved_line(&lane, &hs)))
                })
        };
        match stranded {
            Some((mut fields, line)) => {
                let first = *since.get_or_insert((w.now)());
                if (w.now)() - first >= w.grace_s {
                    fields["why"] = json!(DEAD);
                    fields["line"] = json!(line);
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

/// `l7r-gate lane wait`: [`wait`] with the standing seams - the hand-ins waiting asked where `HAND_IN_BASE` is phase 2's (461 T56) -
/// its lines printed, exit 0; a knob that is no number refused (exit 2), a line it could not write an error (exit 1).
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
    let waiting = || waiting_on(common);
    let origin = l7r_shared::lane_wake::origin_base(env("HAND_IN_BASE").as_deref());
    let w = Wait {
        common,
        poll_s,
        grace_s,
        now: &now,
        sleep: &sleep,
        alive: &alive,
        waiting: origin.then_some(&waiting as &dyn Fn() -> Vec<HandIn>),
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
