//! THE BATCH (feature 461 T14, plan D5, D14; data-model.md "A batch"): which waiting hand-ins the lane runs together, and the batch's
//! id. The oldest waiting hand-in, then the waiting hand-ins of ITS feature that come straight after it in hand-in order (FR-003's
//! "in order"), cut at the first waiting hand-in of another feature, at one D14 holds behind an open batch, or at [`LANE_MAX`]
//! changes, whichever comes first. A same-feature hand-in after another feature's is not pulled forward: no hand-in lands ahead of
//! an older one it was not batched with. One feature a batch, because `make land` takes one `F=`. Label: the literal order (D5); the
//! cut at a held hand-in the easier route.
//!
//! D14'S OPEN-BATCH HALF: a hand-in of a task that an OPEN batch already carries (an earlier hand-in of the same feature sharing a
//! task) waits until that batch ends; a batch read its changes' shas when it formed, so a later hand-in moves no open batch. Where the
//! OLDEST waiting hand-in is held, no batch forms at all, since nothing may land ahead of it. The runner forms no batch while one is
//! open anyway (it runs one at a time); the rule is here so the batch is right by its own reading, whoever forms it.
//!
//! Only `waiting` hand-ins are batched (`log::state`): a superseded one rides inside its successor's commit (D14's handout half,
//! T09), an ejected one waits on its repair, one in an open batch is that batch's.

use crate::log::{self, HandIn, HandInState, World};

/// GUESS knob (`LANE_MAX`, plan D5): the most changes a batch holds - the two-tier threshold's ceiling of "about six tasks"
/// (`docs/process-decisions.md`); the night's 63-task batch took 14 attempts where the smaller ones landed on the first or second.
/// Trial 458's verdict resets it.
pub const LANE_MAX: usize = 6;

/// Whether `h` is held behind an open batch (D14): an open batch carries a change of `h`'s feature that shares one of its tasks.
fn held(h: &HandIn, w: &World) -> bool {
    w.batches.iter().filter(|b| b.open()).any(|b| {
        b.changes.iter().any(|c| {
            w.hand_ins.iter().any(|o| {
                log::names(&o.commit, c)
                    && o.commit != h.commit
                    && o.feature == h.feature
                    && o.tasks.iter().any(|t| h.tasks.contains(t))
            })
        })
    })
}

/// D5's batch of `w`, at most `max` changes, in hand-in order; empty where nothing waits or the oldest waiting is held.
#[must_use]
pub fn form<'a>(w: &World<'a>, max: usize) -> Vec<&'a HandIn> {
    let waiting: Vec<&HandIn> = w
        .hand_ins
        .iter()
        .filter(|h| log::state(h, w) == HandInState::Waiting)
        .collect();
    let Some(first) = waiting.first() else {
        return Vec::new();
    };
    waiting
        .iter()
        .take_while(|h| h.feature == first.feature && !held(h, w))
        .take(max)
        .copied()
        .collect()
}

/// The next batch id of `feature` in `log`: `<feature>-<n>`, n one past the highest of its batch lines (data-model.md).
#[must_use]
pub fn next_id(log: &[serde_json::Value], feature: &str) -> String {
    let prefix = format!("{feature}-");
    let n = log
        .iter()
        .filter(|l| l["event"] == "batch")
        .filter_map(|l| {
            l["batch"]
                .as_str()?
                .strip_prefix(&prefix)?
                .parse::<u64>()
                .ok()
        })
        .max()
        .unwrap_or(0);
    format!("{feature}-{}", n + 1)
}

#[cfg(test)]
mod tests;
