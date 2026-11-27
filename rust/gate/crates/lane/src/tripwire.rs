//! THE TRIPWIRE BY TASK (feature 461 T18, plan D6 step 4, D7's table; data-model.md, "A batch"): inside the lane the red-gate
//! tripwire fires on repeated reds of the same TASK, which T17's stand-down leaves to it. A red counts against a task only where the
//! lane PINS it: an `eject` line of `lane.jsonl` with `why` `red`, `inferred` or `unplaced` ([`PINS`]) whose change is a hand-in of
//! that task's (keyed by feature and task: `T01` is every feature's). A `conflict` ejection pins nothing, nor does the ruling's own
//! ejection (`arbiter`), nor a red half of two changes or more (phase 3's halving writes no `eject` line for one). Pins are counted
//! by BATCH: each batch ejects a task at most once, and a kill between a repair entry and its `eject` lines (461 T15 Decision 7) is
//! never read as a second pin.
//!
//! At a task's SECOND pin - a repair's hand-in red again, or one task ejected from two batches - the runner ([`crate::runner::run`])
//! files no repair: it writes the change's `eject` line with no repair and the trigger it waits on (`arbiter`), which holds the
//! hand-in off every batch (`log::state` reads it ejected); a `stop` line naming the batch (`why` `arbiter`, the `trigger`, the
//! `held` changes); runs `make arbiter-ask SUBJECT=<subject> FILES="<the two attempt files>"` in the lane's tree; and owes the
//! coordinator ONE line, the runner's own stop (`run.rs`'s `stopped()`). Once `make arbiter-ruled` records the ruling, the runner's
//! next step files its ONE repair entry (`why` `arbiter`, `attempt` the trigger) and an `eject` line naming it ([`awaiting`]).
//!
//! Each choice the plan is silent on, labeled:
//! - THE SUBJECT is `lane-<task>` (D6's words), the tasks of a bundle joined by `-`, and from a third pin on `lane-<task>-<n>`, n the
//!   pin: one ruling a trigger is binding (`arbiter-ask` refuses a ruled trigger), so a third pin's ask needs a trigger of its own,
//!   and the earlier ruling, read under its own trigger, files nothing for it. The easier route.
//! - THE RULING IS READ in the clone's `specs/<spec>/arbiter.jsonl`, where `make arbiter-ruled` run there writes it (uncommitted
//!   until the coordinator's push) - not the lane's tree, which every batch resets to `origin/main`. The easier route.
//! - THE RUNNER STOPS at the trip (the task's "the lane stops") and its next start - `make lane-start`, which the owed line names,
//!   or a hand-in's own - files the ruling's repair: no runner waits on a ruling the coordinator dispatches. The changes of the
//!   stopped batch the tripwire did not hold read `waiting` and form the next batch; only the held ones wait on the ruling.
//! - THE RULING'S `eject` LINE carries `of_batch`, not `batch`: the batch ended at its `stop`, and every reader of a batch's lines
//!   (`log::state_of`, `tree`'s stand-down, `builder_tree`'s open check) would read a later `eject` of it as the batch reopened.

use std::collections::BTreeSet;

use serde_json::Value;

use crate::log::{self, HandIn};

/// The `why`s of an `eject` line that pin its change's tasks.
pub const PINS: [&str; 3] = ["red", "inferred", "unplaced"];

/// A pin: the batch that ejected the task, and its attempt file.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Pin {
    pub batch: String,
    pub attempt: String,
}

/// The tasks of the hand-in of `feature` whose commit `change` names, none where no hand-in does.
fn tasks_of<'a>(hand_ins: &'a [HandIn], feature: &str, change: &str) -> &'a [String] {
    hand_ins
        .iter()
        .find(|h| h.feature == feature && log::names(&h.commit, change))
        .map_or(&[], |h| h.tasks.as_slice())
}

/// The pins of `task` of `feature` in `lane`, one a batch, in the order written; each attempt read from its `eject` line, else from
/// the repair entry the line names (`repairs`, `l7r-lane/repairs.jsonl`'s lines).
#[must_use]
pub fn pins(
    lane: &[Value],
    repairs: &[Value],
    hand_ins: &[HandIn],
    feature: &str,
    task: &str,
) -> Vec<Pin> {
    let mut out: Vec<Pin> = Vec::new();
    for l in lane {
        let (Some(batch), Some(change)) = (l["batch"].as_str(), l["change"].as_str()) else {
            continue;
        };
        let pinning = l["event"] == "eject" && PINS.iter().any(|w| l["why"] == *w);
        if !pinning
            || !tasks_of(hand_ins, feature, change)
                .iter()
                .any(|t| t == task)
            || out.iter().any(|p| p.batch == batch)
        {
            continue;
        }
        let of_entry = || {
            repairs
                .iter()
                .find(|r| r["repair"] == l["repair"])
                .and_then(|r| r["attempt"].as_str())
        };
        let attempt = l["attempt"].as_str().or_else(of_entry).unwrap_or_default();
        out.push(Pin {
            batch: batch.to_owned(),
            attempt: attempt.to_owned(),
        });
    }
    out
}

/// A task at its second pin or later: the task, its pin's number (2 on), and the pin before this batch's.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Trip {
    pub task: String,
    pub n: usize,
    pub before: Pin,
}

/// The tasks of `tasks` (of `feature`) that batch `batch` pins a second time or later: those with a pin in another batch.
#[must_use]
pub fn trips(
    lane: &[Value],
    repairs: &[Value],
    hand_ins: &[HandIn],
    feature: &str,
    tasks: &[String],
    batch: &str,
) -> Vec<Trip> {
    tasks
        .iter()
        .filter_map(|t| {
            let earlier: Vec<Pin> = pins(lane, repairs, hand_ins, feature, t)
                .into_iter()
                .filter(|p| p.batch != batch)
                .collect();
            Some(Trip {
                task: t.clone(),
                n: earlier.len() + 1,
                before: earlier.last()?.clone(),
            })
        })
        .collect()
}

/// The ask's SUBJECT for `trips` (the module's doc): `lane-<task>[-<task>...]`, with `-<n>` from a third pin on.
#[must_use]
pub fn subject(trips: &[Trip]) -> String {
    let tasks: Vec<&str> = trips.iter().map(|t| t.task.as_str()).collect();
    let n = trips.iter().map(|t| t.n).max().unwrap_or(2);
    let pin = if n > 2 {
        format!("-{n}")
    } else {
        String::new()
    };
    format!("lane-{}{pin}", tasks.join("-"))
}

/// The ask's attempt files: each trip's earlier attempt, then this one's, each once.
#[must_use]
pub fn files(trips: &[Trip], attempt: &str) -> Vec<String> {
    let mut out: Vec<String> = Vec::new();
    for f in trips
        .iter()
        .map(|t| t.before.attempt.as_str())
        .chain([attempt])
    {
        if !f.is_empty() && !out.iter().any(|o| o == f) {
            out.push(f.to_owned());
        }
    }
    out
}

/// The bundle `make arbiter-ask` names in its output: the last word ending in `MANIFEST.md`, its backticks dropped.
#[must_use]
pub fn manifest(output: &str) -> Option<String> {
    output
        .split_whitespace()
        .map(|w| w.trim_matches(|c| c == '`' || c == '\'' || c == '"'))
        .rfind(|w| w.ends_with("MANIFEST.md"))
        .map(str::to_owned)
}

/// A stopped batch's hold on the arbiter: its `stop` line's batch, trigger, spec directory, tasks and held changes.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Held {
    pub batch: String,
    pub trigger: String,
    pub spec: String,
    pub tasks: Vec<String>,
    pub changes: Vec<String>,
}

fn strings(v: &Value) -> Vec<String> {
    v.as_array()
        .into_iter()
        .flatten()
        .filter_map(Value::as_str)
        .map(str::to_owned)
        .collect()
}

/// The holds of `lane` whose ruling's repair is not yet filed: a `stop` line naming a batch and a trigger, and no `eject` line of
/// that batch (`of_batch`) with `why` `arbiter` after it.
#[must_use]
pub fn awaiting(lane: &[Value]) -> Vec<Held> {
    let filed: BTreeSet<&str> = lane
        .iter()
        .filter(|l| l["event"] == "eject" && l["why"] == "arbiter")
        .filter_map(|l| l["of_batch"].as_str())
        .collect();
    lane.iter()
        .filter(|l| l["event"] == "stop" && l["why"] == "arbiter")
        .filter_map(|l| {
            let batch = l["batch"].as_str()?;
            (!filed.contains(batch)).then(|| Held {
                batch: batch.to_owned(),
                trigger: l["trigger"].as_str().unwrap_or_default().to_owned(),
                spec: l["spec"].as_str().unwrap_or_default().to_owned(),
                tasks: strings(&l["tasks"]),
                changes: strings(&l["held"]),
            })
        })
        .collect()
}

/// A ruling's units, as its repair entry carries them: `<ruling>: <what>`, or the ruling alone where it asks nothing.
#[must_use]
pub fn units(ruling: &Value) -> Vec<String> {
    let said = |k: &str| ruling[k].as_str().unwrap_or_default().trim().to_owned();
    let (r, what) = (said("ruling"), said("what"));
    vec![if what.is_empty() {
        r
    } else {
        format!("{r}: {what}")
    }]
}

#[cfg(test)]
mod tests;
