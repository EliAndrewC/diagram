//! THE POOL TREE A PASS WAS DISPATCHED FROM (feature 451 T305). WHY: `whose.rs` left a pass to another task's landing only where a
//! source named a task STARTED in the landing's tree, and a builder in a pool tree (`make builder-tree`, 451 T285) is started by
//! nothing there: the pool's registry holds its task, its start is made in the clone by the landing's session, minutes before the
//! landing. So on 2026-11-26 the landing of 451 T281 and T284 was refused three times on message-check rounds T295's builder had run
//! from its tree (agents `aacfece6ce5ac4886` at 16:19Z and `a258d8d9d92cfd749` at 16:23Z, T295's first start row 16:46Z), and T272's
//! once. Replayed that day on the real pass, each rung of `whose.rs` failed: its subject (`Judge the guard message unit(s) in the
//! bundle: read /tmp/l7r-check/guard-messages/MANIFEST.md ...`) and its description (`Message check static-runs`) name no task; its
//! builder's description (`Build 451 T295 wrong-tree guards`) does not open with the feature's number, so `builder_brief` reads no
//! builder; and T295 had no start row for `served` to find.
//!
//! So a pass is tied to the task that HELD THE POOL TREE it was dispatched from, WHEN it was dispatched: the tree its own subject
//! names, else the one its dispatching agent's brief names on its first line (`... in the pool worktree <tree> ...`), and the holder
//! the pool's log (`<git common dir>/builder-pool.log`, written by the gate's `task` crate, `builder_tree.rs`'s `note`) gives at the
//! time of the pass's transcript's first record. The LOG and not the registry: the registry says who holds a tree now, and a tree is
//! handed on (`diagram-backlog-t270` was T295's until 16:54Z and T303's from 17:13Z), so read at a later landing it would hand
//! T295's pass to T303. A hold counts as the task's start for this rung alone. A pass made while the tree was free, before its log
//! begins, under a hold naming no feature, or whose transcript carries no time is tied to nothing and holds the push as before.

use std::io::{BufRead, BufReader};
use std::path::Path;

use serde_json::Value;

/// One line of the pool's log: the tree, when, and who held it from then (None: free).
struct Event {
    tree: String,
    at: f64,
    hold: Option<(String, Vec<String>)>,
}

/// The pool's log, read once a run.
pub(super) struct Holds(Vec<Event>);

/// A log line's holder (`451 T285,T286`) as its feature and tasks; None for `free` and for a hold naming no feature.
fn hold(detail: &str) -> Option<(String, Vec<String>)> {
    let (feature, tasks) = detail.split_once(' ')?;
    Some((
        feature.to_owned(),
        tasks.split(',').map(str::to_owned).collect(),
    ))
}

/// Does `text` name the tree at `tree` - its path, not a longer name beside it (`<tree>-old`)?
fn names(text: &str, tree: &str) -> bool {
    !tree.is_empty()
        && text.match_indices(tree).any(|(i, _)| {
            !text[i + tree.len()..]
                .starts_with(|c: char| c.is_alphanumeric() || matches!(c, '_' | '-'))
        })
}

impl Holds {
    /// The log under the git common directory `common`: a line that is not an event with a time is skipped, a missing file is no pool.
    pub(super) fn read(common: &Path) -> Self {
        let text = std::fs::read_to_string(common.join("builder-pool.log")).unwrap_or_default();
        let field = |e: &Value, k: &str| e[k].as_str().unwrap_or_default().to_owned();
        let events = text
            .lines()
            .filter_map(|l| serde_json::from_str::<Value>(l).ok())
            .filter_map(|e| {
                let hold = match field(&e, "event").as_str() {
                    "take" | "make" | "adopt" => hold(&field(&e, "detail")),
                    "release" | "landed" | "drop" => None,
                    _ => return None,
                };
                Some(Event {
                    tree: field(&e, "tree"),
                    at: l7r_shared::iso::parse(&field(&e, "utc"))?,
                    hold,
                })
            })
            .collect();
        Self(events)
    }

    /// The feature and tasks holding, at `at`, the pool tree `text` names: the last event by then of a tree named there.
    pub(super) fn holder(&self, text: &str, at: f64) -> Option<(String, Vec<String>)> {
        self.0
            .iter()
            .rfind(|e| e.at <= at && names(text, &e.tree))?
            .hold
            .clone()
    }
}

/// The first record of a transcript: its time, and the first line of its prompt - `(None, "")` where it has none.
pub(super) fn first_record(transcript: &Path) -> (Option<f64>, String) {
    // its first line alone is read (a builder's transcript runs to megabytes); one that cannot be read is no record
    let mut first = String::new();
    if let Ok(file) = std::fs::File::open(transcript) {
        let _ = BufReader::new(file).read_line(&mut first);
    }
    let record: Value = serde_json::from_str(&first).unwrap_or(Value::Null);
    let content = &record["message"]["content"];
    let prompt = content
        .as_str()
        .or_else(|| content[0]["text"].as_str())
        .unwrap_or_default();
    (
        record["timestamp"]
            .as_str()
            .and_then(l7r_shared::iso::parse),
        prompt.lines().next().unwrap_or_default().to_owned(),
    )
}

#[cfg(test)]
mod tests;
