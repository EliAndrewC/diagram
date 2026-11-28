//! THE LANE'S LOG AND ITS COMPUTED STATES (feature 461 T11, plan D8, `data-model.md`): one JSON line a transition in
//! `l7r-lane/lane.jsonl` of the git common directory, shared by the clone, the pool trees and the lane's tree; and the states of a
//! hand-in and of a batch, COMPUTED from the pool log's `done` lines, the done refs, `origin/main` and this log - never typed into
//! a file (the queue's rule, `l7r_shared::builder_queue`), so a runner that dies is restarted with nothing to repair. Why a log and
//! not a state file the runner rewrites: the night of 2026-11-27's causes were "partly inferred: several attempts overwrote one
//! log" (spec), and a rewritten file is lost or stale on a crash where a log replayed is not (D8, convention: the pool's log).
//!
//! THE STATES ARE READ IN `l7r_shared::lane_log` (461 T63), re-exported here under their old names (`log::state`, `log::batches`,
//! `log::HandIn`, ...): the Stop rule (`l7r_shared::lane_wake::holds`) reads the same functions, where the guard reaches no gate
//! crate, so a change to a batch's or a hand-in's state moves it too. Its module doc holds the states' rules and their labels; this
//! module keeps the log's path, its writer and the repairs open.

use std::io::Write as _;
use std::path::{Path, PathBuf};

pub use l7r_shared::lane_log::{
    batches, hand_ins, lines_of, names, on_lane, state, state_of, Batch, BatchState, HandIn,
    HandInState, World,
};
use serde_json::{Map, Value};

/// The lane's directory, in the git common directory: the read mark's (`l7r_shared::lane_wake`, 461 T20), so the prompt hook and
/// `make lane-wait` read the log this writes.
pub const DIR: &str = l7r_shared::lane_wake::DIR;
/// The log's file, in [`DIR`].
pub const FILE: &str = l7r_shared::lane_wake::FILE;
/// The events of data-model.md's table, the only ones [`append`] writes.
pub const EVENTS: [&str; 10] = [
    "start",
    "stop",
    "batch",
    "carry",
    "run",
    "attribute",
    "push",
    "eject",
    "landed",
    "owed",
];

/// The log's path under the git common directory `common`.
#[must_use]
pub fn path(common: &Path) -> PathBuf {
    common.join(DIR).join(FILE)
}

/// One transition appended: `utc` and `event`, then `fields`' own, written with one `write_all` of the whole line, its newline
/// included, so two writers never interleave inside a line.
///
/// # Errors
///
/// An event data-model.md does not name, or the directory or file that cannot be written, as a line naming it.
pub fn append(common: &Path, now: &str, event: &str, fields: &Value) -> Result<(), String> {
    if !EVENTS.contains(&event) {
        return Err(format!(
            "lane: no event {event} (data-model.md's are {})",
            EVENTS.join(", ")
        ));
    }
    let mut line = Map::new();
    line.insert("utc".to_owned(), Value::from(now));
    line.insert("event".to_owned(), Value::from(event));
    for (k, v) in fields.as_object().into_iter().flatten() {
        line.insert(k.clone(), v.clone());
    }
    let file = path(common);
    let text = format!("{}\n", Value::Object(line));
    std::fs::create_dir_all(common.join(DIR))
        .and_then(|()| {
            std::fs::OpenOptions::new()
                .create(true)
                .append(true)
                .open(&file)
        })
        .and_then(|mut f| f.write_all(text.as_bytes()))
        .map_err(|e| format!("lane: {}: {e}", file.display()))
}

/// The lane's log under `common`, read.
#[must_use]
pub fn read(common: &Path) -> Vec<Value> {
    lines_of(&path(common))
}

/// The repair entries open under the git common directory `common`, by id, in the order filed: the queue's reader's
/// (`l7r_shared::builder_queue::repairs::open`, 461 T16) - filed, ejected, unanswered by a `repair_of` and not superseded by a later
/// hand-in of its task - so `make lane` says the repairs `make builder-next` offers (461 T65), one rule in one place.
#[must_use]
pub fn repairs_open(common: &Path) -> Vec<String> {
    l7r_shared::builder_queue::repairs::open(common)
        .into_iter()
        .map(|r| r.id)
        .collect()
}

#[cfg(test)]
mod tests;
