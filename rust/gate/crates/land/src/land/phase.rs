//! THE LANDING'S PHASE LINES (feature 451 T06, plan D5, FR-003; the GM's approved "make land its phases' seconds"): a landing was one
//! span in the event log, so its first pass, its gate, the claims wait and its push could not be told apart, and a refused landing was
//! counted only by guessing from a tool response. Each step now writes one `Phase` line at its end, through the writer the hooks use
//! (`append_row_for`, filed in the landed feature's log, a task never started in the clone too), and the landing writes a last `end`
//! line with its exit code, the tasks it was asked to land and whether its push went out (`landed`), whether it landed, was refused or
//! raised - the readers count a refused landing (rework, FR-005) and a landing of a task (D10, D11) from that one line.
//!
//! The steps tile the landing, every part of it booked to one:
//! - `cheap`: the first pass (every cheap refusal, [`super::cheap`]);
//! - `gate`: the second pass whole ([`super::long_runs`]) - the delta's engine reads, the green-gate stamp, the gates it names or the
//!   machinery's guard suites, a landing cohort run alone, the records and maps they regenerated committed, the work-budget review;
//! - `cohort`: `make cohort-landing`, beside the gate or after it - NESTED in the `gate` line's span, never past it;
//! - `claims`: the wait for the claims round and the ledger rows its passes owe;
//! - `push`: the ticks, their commit, the one push carrying both, a failed push's revert;
//! - `end`: the landing from its arguments read to its verdict - written THE MOMENT THE PUSH WENT OUT (exit 0, or 3 with the ticks
//!   standing), `landed` true and its code the push's, so no later stop leaves a pushed landing reading unlanded (T06's plan review,
//!   T06-stop-after-push); else at the landing's exit, `landed` false;
//! - `after-push`: the push's tail, after the `end` - the fresh block's start and the work-budget view; a raise there is its own
//!   line's code, the landing's `end` standing.
//!
//! A step that did not run writes no line (a refused first pass writes `cheap` and `end`). A stopped landing (`make land-stop`, TERM)
//! writes none past its last finished step: its handler exits at once ([`super::stop`]), and a file write is no signal handler's work.

use std::path::Path;
use std::time::SystemTime;

use l7r_shared::env::Rooted;
use l7r_shared::guards::event_log_hooks::{append_row_with, phase_row};
use serde_json::{json, Value};

use super::Land;

/// The make target a landing runs under where no `make` is above it: `make land`'s (`land-batch` is the same command, plan D2's
/// bucket `land` both).
const LAND: &str = "land";

impl Land {
    /// One step timed: `go` run, its line written at its end with its exit code - 1 where it raised, as the landing's own raise exits.
    pub(super) fn phase(
        &self,
        step: &str,
        go: impl FnOnce() -> Result<i32, String>,
    ) -> Result<i32, String> {
        let began = SystemTime::now();
        let done = go();
        self.phase_line(step, began, code_of(&done));
        done
    }

    /// A step's line, `began` its start, `code` how it went.
    pub(super) fn phase_line(&self, step: &str, began: SystemTime, code: i32) {
        let tasks = self.landing_tasks.borrow();
        let _ = append_row_with(
            &self.root,
            Some(&self.landing_feature.borrow()),
            row(&self.root, step, began, code, &self.make_target, &tasks),
            self.root.reader(),
        );
    }

    /// The landing of `tasks`, its `end` line written whatever it comes to - at the push, where it went out ([`Land::end_now`]), else at
    /// its exit; `began` is when its arguments were read.
    pub(super) fn landing(
        &self,
        d: &Path,
        tasks: &[String],
        note: &str,
        began: SystemTime,
    ) -> Result<i32, String> {
        self.began.set(Some(began));
        let done = self.land(d, tasks, note);
        if !self.ended.get() {
            self.end_now(code_of(&done));
        }
        done
    }

    /// The landing's `end` line, now, once: its code, the tasks asked, and whether its push went out.
    pub(super) fn end_now(&self, code: i32) {
        self.ended.set(true);
        let began = self.began.get().unwrap_or_else(SystemTime::now);
        let tasks = self.landing_tasks.borrow();
        let mut line = row(&self.root, "end", began, code, &self.make_target, &tasks);
        line.insert("landed".into(), Value::Bool(self.pushed.get()));
        let _ = append_row_with(
            &self.root,
            Some(&self.landing_feature.borrow()),
            line,
            self.root.reader(),
        );
    }
}

/// The `end` line of a landing refused before it began (`main`'s refusals: no note, no feature directory), filed in the feature its
/// `F=` names where it names one.
pub(super) fn end(
    root: &Rooted,
    feature: &str,
    tasks: &[String],
    began: SystemTime,
    done: &Result<i32, String>,
    make: &str,
) {
    let mut line = row(root, "end", began, code_of(done), make, tasks);
    line.insert("landed".into(), Value::Bool(false));
    let _ = append_row_with(root, Some(feature), line, root.reader());
}

/// A step's exit code: its own, or 1 for a raise (the landing's raise exits 1, `finish`).
fn code_of(done: &Result<i32, String>) -> i32 {
    done.as_ref().map_or(1, |c| *c)
}

/// One line of the landing's, in the one form (`phase_row`, 451 T153).
fn row(
    root: &Path,
    step: &str,
    began: SystemTime,
    code: i32,
    make: &str,
    tasks: &[String],
) -> serde_json::Map<String, Value> {
    let mut row = phase_row("land", step, (began, SystemTime::now()), code, make, root);
    if let Some(first) = tasks.first() {
        row.insert("task".into(), Value::from(first.as_str()));
    }
    if step == "end" {
        row.insert("tasks".into(), json!(tasks));
    }
    row
}

/// The landing's make target (plan D4's `make`, as T05's checks name theirs): `shared::make::outermost_goal` (moved there by 451 T153,
/// every Phase writer's one reading); `land` where no `make` is above it or its command line names no goal.
pub(super) fn run_target(proc_root: &Path, pid: u32) -> String {
    l7r_shared::make::outermost_goal(proc_root, pid).unwrap_or_else(|| LAND.to_owned())
}

#[cfg(test)]
mod tests;
