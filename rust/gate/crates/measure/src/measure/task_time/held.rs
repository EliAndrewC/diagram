//! WHO HELD A POOL TREE, AND WHEN, read from the pool's log (`builder-pool.log` in a clone's git directory, `make builder-tree`'s
//! record) - and a pool tree's `Phase` lines given their holder's task at READ time (feature 451 T391).
//!
//! WHY. Until 451 T332 a tool's own line written from a pool tree took the task of the tree's last `make task-start`, which no
//! handout moves: 3,255 of the 3,883 `Phase` lines pool trees wrote into the 451 log name a task other than the first task of the
//! tree's holder at their start, 385 minutes of spans, measured 2026-11-27 (T332's plan section: each line's task against the
//! detail of the tree's last take at or before its `t0`). The lines are not rewritten; every reader that books a `Phase` line by
//! its task - `make task-time`, `make task-progress`, `make where-time` and through it `make feature-report` - re-tasks them here,
//! before its runs are read, with this one function.
//!
//! WHAT THE TASK DECIDES. A `Phase` line is tied to ONE Bash run of its session (`where_time::columns`' `tie`): among the runs whose
//! span holds it, one whose make target is the line's and whose task is the line's before one that shares the target alone, the
//! latest started breaking a tie. A session's builders share its id, so two builders each inside a `make builder-checks` at one
//! moment are told apart by the task alone; a stale task hands the first builder's build and test seconds to the second's run.
//!
//! THE RULE. A line whose `clone` is a tree the log names, begun while a holder held it for the line's feature, takes the holder's
//! FIRST task - unless its own task is one of the holder's (a bundle's second member, named by a builder's own later start, stands:
//! T332's rule at the writer). A line from a tree the log does not know, from a time nobody held it, or filed under a feature the
//! holder was not held for keeps its own task. A held line also carries `held_for`, the holder's tasks, and is tied only to a run of
//! one of them (451 T522 (d): two builders' runs of one target, one holding the other's lines, `where_time::columns::ran::tie`).

use std::path::{Path, PathBuf};

use l7r_shared::guards::event_log_hooks::common_git_dir;
use serde_json::Value;

use super::super::events::{is, or_s, ts, Event};
use super::tiers::dir_name;

/// One tree held: from a `take` (or a tree's `make` for a task, or an `adopt` of a held tree) to the tree's next `release` or
/// handout.
#[derive(Debug, Clone, PartialEq)]
pub struct Hold {
    /// When it was handed out.
    pub from: f64,
    /// When it was released or handed on; infinite while it is held.
    pub until: f64,
    /// The tree's directory name.
    pub tree: String,
    /// The holder's feature number (`451`).
    pub feature: String,
    /// The holder's tasks, a bundle's in its order.
    pub tasks: Vec<String>,
}

/// A holder's detail read (`451 T324,T345`): its feature number and its tasks, split on spaces AND commas (451 T393: a bundle is
/// written with commas, and a reader splitting on spaces alone took `T324,T345` for one task's name).
#[must_use]
pub fn holder(detail: &str) -> (String, Vec<String>) {
    let mut words = detail
        .split([' ', ','])
        .filter(|w| !w.is_empty())
        .map(str::to_owned);
    (words.next().unwrap_or_default(), words.collect())
}

/// Whether a row of the pool's log hands its tree to a holder: a `take`, a tree's `make` for a task (a tree's first holder is
/// written so, never as a `take`), or an `adopt` of a tree that was held - one adopted `free` names no task.
#[must_use]
pub fn opens(event: &str, tasks: &[String]) -> bool {
    ["take", "adopt", "make"].contains(&event) && !tasks.is_empty()
}

/// A holder's detail as a `Blocks:` clue reads it: its feature and its FIRST task (`451 T324`).
#[must_use]
pub fn first(detail: &str) -> String {
    let (feature, tasks) = holder(detail);
    format!("{feature} {}", tasks.first().map_or("", String::as_str))
        .trim_end()
        .to_owned()
}

/// Every hold the pool logs of `bases` record, each log read once, in the order written.
#[must_use]
pub fn holds(bases: &[PathBuf]) -> Vec<Hold> {
    let mut seen: Vec<PathBuf> = Vec::new();
    let mut out: Vec<Hold> = Vec::new();
    for base in bases {
        let log = common_git_dir(base).join("builder-pool.log");
        let path = std::fs::canonicalize(&log).unwrap_or(log);
        if seen.contains(&path) {
            continue;
        }
        let text = std::fs::read_to_string(&path).unwrap_or_default();
        seen.push(path);
        let from = out.len();
        for v in text
            .lines()
            .filter_map(|l| serde_json::from_str::<Value>(l).ok())
        {
            let field = |k: &str| v.get(k).and_then(Value::as_str).unwrap_or("").to_owned();
            let (event, tree) = (field("event"), dir_name(&field("tree")));
            let (feature, tasks) = holder(&field("detail"));
            let opens = opens(&event, &tasks);
            if !opens && event != "release" {
                continue;
            }
            let Ok(at) = ts(&field("utc")) else {
                continue;
            };
            // the tree's hold still open ends here: at its release, or at the handout that follows with none
            for h in out[from..]
                .iter_mut()
                .filter(|h| h.tree == tree && h.until.is_infinite())
            {
                h.until = at;
            }
            if opens {
                out.push(Hold {
                    from: at,
                    until: f64::INFINITY,
                    tree,
                    feature,
                    tasks,
                });
            }
        }
    }
    out
}

/// The log of the lines the writer filed under no feature (`event_log_hooks::log_path_in`).
const UNFILED: &str = "_unassigned";

/// Each `Phase` line of a pool tree given the task its tree's holder had when the phase began (the module's doc). `home` is the
/// feature of a line that carries none (one feature's log read untagged).
pub fn retask(aside: &mut [Event], holds: &[Hold], home: &str) {
    for e in aside.iter_mut().filter(|e| is(e, "ev", "Phase")) {
        let (tree, t0) = (
            dir_name(&or_s(e, "clone")),
            ts(&or_s(e, "t0")).unwrap_or(0.0),
        );
        let (tagged, own) = (or_s(e, "feature"), or_s(e, "task"));
        let feature = if tagged.is_empty() { home } else { &tagged };
        let held = holds.iter().rfind(|h| {
            h.tree == tree
                && h.from <= t0
                && t0 < h.until
                // a line the writer filed under no feature is the holder's (451 T522 (d): 647 of b1's lines on 2026-11-27, T529)
                && (feature == UNFILED
                    || feature == h.feature
                    || feature.starts_with(&format!("{}-", h.feature)))
        });
        let Some(h) = held else {
            continue;
        };
        // the holder's tasks, so the tie gives the line to no other builder's run of the same target (451 T522 (d), `ran::tie`)
        let tasks = h.tasks.iter().cloned().map(Value::String).collect();
        e.insert("held_for".to_owned(), Value::Array(tasks));
        if !h.tasks.contains(&own) {
            e.insert("task".to_owned(), Value::String(h.tasks[0].clone()));
        }
    }
}

/// [`holds`] of the trees a report reads, for [`retask`].
#[must_use]
pub fn of(root: &Path, clones: &Path) -> Vec<Hold> {
    holds(&super::bases(root, clones))
}

#[cfg(test)]
#[path = "held_tests.rs"]
mod tests;
