//! THE SECOND TIER, BOOKED APART (feature 451 T298; the GM 2026-11-26: "I do think that we should probably move batched landing stuff
//! that happens as the second tier of checks into its own separate category rather than counting it against any individual task").
//!
//! A BATCH is one `make land` over its tasks, every attempt at it (a red gate, its re-run) until one lands: its key is
//! `(feature, "second tier: <tasks>")`, a task of no one's. Booked to it:
//! - each attempt's own run - the cheap refusals, the gate, the claims round, the ticks and the push - whatever task the session's
//!   mark named and whatever else its command line ran (a `make format && make land` was booked to tests under `make format`, a
//!   `make task-start && make land` to the first task of the batch, measured 2026-11-26 on the window from 17:00Z);
//! - everything a batch's task is named on FROM ITS CARRY into the clone to the landing - the repairs between a red gate and its
//!   re-run, the session's `make quick` before the push: "a task's own table ends at its carry into the clone" (T298's line). With
//!   no carry found (a task built in the clone itself, a carry no transcript holds) its table ends where the batch's first attempt
//!   starts - a GUESS, said on the batch's line.
//!
//! ITS BLOCKING stands on its own line, expected near zero since no new task waits on the gate - a rise is the signal that something
//! has begun to wait on it (a carry behind a running gate, a repair, a build slot): the task line's words, relaying the GM's ruling
//! of 2026-11-26. So a gate in flight blocks
//! nothing while any task's own work in flight blocks that task (the session is waiting on builders, the gate beside them), and is
//! never booked beside the session's own turn; it blocks - the batch, no task - where the session waits on it ALONE, where it ran in
//! the foreground, and through a repair (the session's own turns from the carry on, and what they wait on). Where the batch's own
//! landing run is in flight, the wait is booked to it - its gate, its push - whatever else in flight ends later (`each_task`): another
//! task's leftover background loop is not what the session waited on. A carry held behind a
//! running gate and a build slot the gate holds are not told apart here: 451 T319.
//!
//! AFTER ITS LANDING a task is done: a main session's line that still carries it only because the mark was never moved (`fallback`)
//! is the session's, under no task (`-`). On 2026-11-26 T305 landed at 17:37 and its mark stood to 18:20, taking the session's
//! turns, a `make task-time` and two other tasks' carries.

use std::collections::HashMap;

use super::{is_wait, ran, Cand, Ix, Key, SESSION_CHECKS};

/// The prefix of a batch's task name: a key so named is a batch's, no task's.
pub const TIER: &str = "second tier: ";
/// The one category the window's table folds every batch's time to.
pub const SECOND_TIER: &str = "the second tier (a batch's gate, repairs and push)";

/// One `make land` run over a batch.
#[derive(Debug, Clone, PartialEq, Default)]
pub struct Attempt {
    /// Its start (the landing's own, after whatever its command line ran first).
    pub t0: f64,
    /// Its end; the window's end while it is in flight.
    pub t1: f64,
    /// Whether it landed.
    pub landed: bool,
    /// Its gate step's seconds.
    pub gate: f64,
    /// Whether it wrote no end line: in flight at the window's end, or killed.
    pub open: bool,
}

/// A batch: the tasks one `make land` named, and each attempt at landing them.
#[derive(Debug, Clone, PartialEq, Default)]
pub struct Batch {
    /// Its feature (its log's).
    pub feature: String,
    /// Its tasks, as the landing listed them.
    pub tasks: Vec<String>,
    /// Its attempts, in time order, the last the one that landed (if any did).
    pub attempts: Vec<Attempt>,
    /// (task, when its `make carry` ended), for each task a carry was found for.
    pub carried: Vec<(String, f64)>,
}

impl Batch {
    /// Its key: under its feature, a task name no task has.
    #[must_use]
    pub fn key(&self) -> Key {
        (
            self.feature.clone(),
            format!("{TIER}{}", self.tasks.join(" ")),
        )
    }

    /// When it landed.
    #[must_use]
    pub fn landed(&self) -> Option<f64> {
        self.attempts.iter().find(|a| a.landed).map(|a| a.t1)
    }

    /// Where `task`'s own table ends and the batch's begins: its carry, else the first attempt's start.
    #[must_use]
    pub fn from(&self, task: &str) -> f64 {
        self.carried
            .iter()
            .find(|(t, _)| t == task)
            .map_or_else(|| self.attempts.first().map_or(f64::MAX, |a| a.t0), |c| c.1)
    }

    /// Its span: from its first task's hand-over to its landing (open-ended while nothing has landed).
    #[must_use]
    pub fn span(&self) -> (f64, f64) {
        let from = self
            .tasks
            .iter()
            .map(|t| self.from(t))
            .fold(f64::MAX, f64::min);
        (from, self.landed().unwrap_or(f64::MAX))
    }
}

/// Whether a key is a batch's.
#[must_use]
pub fn is_tier(k: &Key) -> bool {
    k.1.starts_with(TIER)
}

/// What a run blocks when it is waited on with no clue of its own.
#[derive(Debug, Clone, PartialEq)]
pub enum Blocks {
    /// Its waiter's task (451 T243's default).
    Waiter,
    /// No task: waited on, never blocking (a detached wait loop of the session's own).
    Nothing,
    /// This key: a batch's, or the session's own (`-`).
    Task(Key),
}

impl Ix<'_> {
    /// Every run's and every agent's key set ([`Ix::run_booking`]): `pre_key` each call's line's key and whether the mark alone named it.
    pub(super) fn book_keys(&mut self, pre_key: &HashMap<&str, (Key, bool)>) {
        let run_pre: Vec<(Key, bool)> = self
            .w
            .runs
            .runs
            .iter()
            .map(|r| {
                let (k, fb) = pre_key.get(r.id.as_str()).cloned().unwrap_or_default();
                ((k.0, r.task.clone()), fb)
            })
            .collect();
        for (i, (key, fb)) in run_pre.into_iter().enumerate() {
            let (key, batch, blocks) = self.run_booking(i, key, fb);
            self.run_key.push(key);
            self.tier_run.push(batch);
            self.run_blocks.push(blocks);
        }
        // an agent started after its task's carry (a repair's builder, a late review) is its batch's
        self.agent_key = (0..self.w.agents.len())
            .map(|i| {
                self.tiered(
                    self.agent_own[i].clone(),
                    self.span(Cand::Agent(i)).0,
                    false,
                )
            })
            .collect();
    }

    /// Where the run `i`, its line naming `key` (by the mark alone: `fallback`), is booked - its key, its batch where it is a
    /// batch's landing, and what it blocks when waited on (451 T298, `tier`'s doc): a landing its batch; a carry the task it
    /// carried; a main session's `make quick` or `make done` under the mark alone the batch whose span holds it, else the session's
    /// own (`-`); a main session's background command under the mark alone no task - a wait loop of that kind blocking nothing; any
    /// other its line's key, its batch's from the task's carry on.
    pub(super) fn run_booking(&self, i: usize, key: Key, fb: bool) -> (Key, Option<usize>, Blocks) {
        let r = &self.w.runs.runs[i];
        let makes = ran(r, self.w.commands);
        let has = |list: &[&str]| makes.iter().any(|m| list.contains(&m.as_str()));
        if let Some(b) = self.batch_of_run(i, &key.0, has(&["land"])) {
            let k = self.w.batches[b].key();
            return (k.clone(), Some(b), Blocks::Task(k));
        }
        if let Some(k) = self
            .w
            .carried
            .get(&r.id)
            // a bundle's carry is keyed to its first task, never to a task named `T324,T345` (451 T393)
            .and_then(|c| self.resolve(&super::super::held::first(c), None, &key.0))
        {
            return (k.clone(), None, Blocks::Task(k));
        }
        let own = r.by.is_empty() && fb;
        let none = (key.0.clone(), "-".to_owned());
        if own && has(&SESSION_CHECKS) {
            let k = self.batch_at(&key.0, r.t0).unwrap_or(none);
            return (k.clone(), None, Blocks::Task(k));
        }
        if own && r.bg {
            let blocks = if is_wait(&self.run_cats[i].0) {
                Blocks::Nothing
            } else {
                Blocks::Task(none.clone())
            };
            return (none, None, blocks);
        }
        (self.tiered(key, r.t0, fb), None, Blocks::Waiter)
    }

    /// The batch whose attempt the run `i` is: a main session's `make land`, matched by its feature and by the attempt starting
    /// inside it.
    pub(super) fn batch_of_run(&self, i: usize, feature: &str, lands: bool) -> Option<usize> {
        let r = &self.w.runs.runs[i];
        if !lands || !r.by.is_empty() {
            return None;
        }
        self.w.batches.iter().position(|b| {
            b.feature == feature
                && b.attempts
                    .iter()
                    .any(|a| r.t0 - 1.0 <= a.t0 && a.t0 <= r.t1)
        })
    }

    /// The batch of `feature` whose span holds `t`.
    pub(super) fn batch_at(&self, feature: &str, t: f64) -> Option<Key> {
        self.w
            .batches
            .iter()
            .find(|b| {
                let (x, y) = b.span();
                b.feature == feature && x <= t && t <= y
            })
            .map(Batch::key)
    }

    /// The key a line naming `key` at `t` is booked to (the module's doc): its batch's from the task's carry to the landing; the
    /// session's own (`-`) for a `fallback` line after the landing; else its own.
    pub(super) fn tiered(&self, key: Key, t: f64, fallback: bool) -> Key {
        let mut landed_before = false;
        for b in self
            .w
            .batches
            .iter()
            .filter(|b| b.feature == key.0 && b.tasks.contains(&key.1))
        {
            let until = b.landed().unwrap_or(f64::MAX);
            if b.from(&key.1) <= t && t <= until {
                return b.key();
            }
            landed_before |= until < t;
        }
        if fallback && landed_before {
            (key.0, "-".to_owned())
        } else {
            key
        }
    }

    /// Whether a candidate is a batch's own landing run.
    pub(super) fn is_landing(&self, c: Cand) -> bool {
        matches!(c, Cand::Run(i) if self.tier_run[i].is_some())
    }
}
