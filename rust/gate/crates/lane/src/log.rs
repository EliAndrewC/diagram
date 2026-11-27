//! THE LANE'S LOG AND ITS COMPUTED STATES (feature 461 T11, plan D8, `data-model.md`): one JSON line a transition in
//! `l7r-lane/lane.jsonl` of the git common directory, shared by the clone, the pool trees and the lane's tree; and the states of a
//! hand-in and of a batch, COMPUTED from the pool log's `done` lines, the done refs, `origin/main` and this log - never typed into
//! a file (the queue's rule, `l7r_shared::builder_queue`), so a runner that dies is restarted with nothing to repair. Why a log and
//! not a state file the runner rewrites: the night of 2026-11-27's causes were "partly inferred: several attempts overwrote one
//! log" (spec), and a rewritten file is lost or stale on a crash where a log replayed is not (D8, convention: the pool's log).
//!
//! A HAND-IN is a `done` line of the pool's log with `"handed_in": true`, one a commit (a bundle's tasks share it), that is still
//! the lane's: a done ref names its commit, or a line of this log does (data-model.md, "A hand-in"; a done ref deleted by a hand
//! carry in phase 1 takes it off the lane). Its state, the first that holds ([`state`]): `landed` (`origin/main` holds its author's
//! time and subject - `task`'s `builder_done::held_by`, the carried rule - or a `landed` line lists it, which holds after the
//! object is pruned), `in batch <b>` (an open batch names it and has not ejected it), `superseded` (a later hand-in of its feature
//! shares a task), `ejected -> repair <r>` (the last line of this log naming it is an `eject`), else `waiting`. `in batch` is asked
//! before `superseded`, against data-model.md's list (a deliberate deviation, 461 T53): the open batch's `batch` line names this
//! sha and lands it (D14, T52), so the batch carries it whatever later hand-in of its task exists, and that later one waits.
//!
//! A BATCH's state is read from its lines in order ([`state_of`]); every line of a batch carries `batch` (the data model's `run`
//! example does). The data model is silent on three points, each read the easier way and labeled here, the mapping kept in that
//! one function so T12 and T14 can move it:
//! - `forming` has no event before the `batch` line (D5's cut, `LANE_WAIT_S` = 0, takes no time), so a batch in the log is
//!   `carrying` from its `batch` line; were T14 to add a wait, it adds the event that shows it (a deliberate deviation, labeled).
//! - `stopped` is a `stop` line naming the batch (the arbiter owed, D6 step 4); a runner killed writes no line, and its batch is
//!   resumed (data-model.md, "Recovery"), not stopped - the data model's "or the runner killed" read as Recovery reads it.
//! - the hand-in scratch refs (`refs/l7r/hand-in/`) mark a hand-in not yet made, which is no lane entry: they add no state.

use std::collections::BTreeSet;
use std::fmt;
use std::io::Write as _;
use std::path::{Path, PathBuf};

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

/// A JSON-lines file's objects: none for a missing file, and a line that does not parse - the torn last line of a killed writer -
/// skipped.
#[must_use]
pub fn lines_of(file: &Path) -> Vec<Value> {
    std::fs::read_to_string(file)
        .unwrap_or_default()
        .lines()
        .filter_map(|l| serde_json::from_str::<Value>(l).ok())
        .filter(Value::is_object)
        .collect()
}

/// A hand-in, as the lane reads it from its `done` line (data-model.md, "A hand-in").
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct HandIn {
    /// The feature's key, as the done ref names it (`461`).
    pub feature: String,
    pub tasks: Vec<String>,
    pub commit: String,
    /// The `done` line's `utc`.
    pub at: String,
    /// The repair entry it answers, where the line names one.
    pub repair_of: Option<String>,
}

/// Every hand-in of the pool's log, in its order, one a commit (the first line of a commit kept).
#[must_use]
pub fn hand_ins(pool: &[Value]) -> Vec<HandIn> {
    let mut seen = BTreeSet::new();
    pool.iter()
        .filter(|l| l["event"] == "done" && l["handed_in"] == true)
        .filter_map(|l| {
            let (feature, tasks) = l["detail"].as_str()?.split_once(' ')?;
            Some(HandIn {
                feature: feature.to_owned(),
                tasks: tasks.split(',').map(str::to_owned).collect(),
                commit: l["commit"].as_str()?.to_owned(),
                at: l["utc"].as_str().unwrap_or_default().to_owned(),
                repair_of: l["repair_of"].as_str().map(str::to_owned),
            })
        })
        .filter(|h| seen.insert(h.commit.clone()))
        .collect()
}

/// Those of `all` still the lane's: a done ref names the commit (`refs` holds the refs' commits), or a line of `log` does.
#[must_use]
pub fn on_lane(all: Vec<HandIn>, refs: &BTreeSet<String>, log: &[Value]) -> Vec<HandIn> {
    all.into_iter()
        .filter(|h| refs.contains(&h.commit) || log.iter().any(|l| mentions(l, &h.commit)))
        .collect()
}

/// Whether `named`, a commit as a line writes it (whole, or the short sha of a `run`'s `set`), is `sha`: the shorter a prefix of
/// the longer, at least seven characters.
pub(crate) fn names(sha: &str, named: &str) -> bool {
    let short = sha.len().min(named.len());
    short >= 7 && sha.get(..short) == named.get(..short)
}

/// The commits a line lists under `key`.
fn listed<'a>(line: &'a Value, key: &str) -> impl Iterator<Item = &'a str> {
    line[key]
        .as_array()
        .into_iter()
        .flatten()
        .filter_map(Value::as_str)
}

/// Whether a line of the log names `commit`: a batch's `changes`, a run's or a push's `set`, an ejection's `change`, a `landed`
/// line's `landed` or `ejected`.
fn mentions(line: &Value, commit: &str) -> bool {
    let mut all = ["changes", "set", "landed", "ejected"]
        .into_iter()
        .flat_map(|k| listed(line, k))
        .chain(line["change"].as_str());
    all.any(|s| names(commit, s))
}

/// A batch's state (data-model.md, "A batch").
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum BatchState {
    Carrying,
    /// The gate's attempt under way, from 1.
    Gating(usize),
    Halving,
    Pushing,
    Landed,
    Stopped,
}

impl fmt::Display for BatchState {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::Carrying => f.write_str("carrying"),
            Self::Gating(n) => write!(f, "gating {n}"),
            Self::Halving => f.write_str("halving"),
            Self::Pushing => f.write_str("pushing"),
            Self::Landed => f.write_str("landed"),
            Self::Stopped => f.write_str("stopped"),
        }
    }
}

/// A batch: its id, the changes its `batch` line named, its lines from that one on, and its state.
#[derive(Debug, Clone, PartialEq)]
pub struct Batch {
    pub id: String,
    pub changes: Vec<String>,
    pub lines: Vec<Value>,
    pub state: BatchState,
}

impl Batch {
    /// Neither landed nor stopped: what Recovery resumes.
    #[must_use]
    pub fn open(&self) -> bool {
        !matches!(self.state, BatchState::Landed | BatchState::Stopped)
    }
}

/// THE ONE MAPPING of a batch's lines, in order, to its state (the module's doc): `batch` carrying; `carry` (its carries ended)
/// and `eject` (the rest runs again) gating the next attempt; a green `run` pushing, a red one halving, as an `attribute`;
/// `push` pushing; `landed` and `stop` end it; `owed` and the runner's own lines change nothing.
#[must_use]
pub fn state_of(lines: &[Value]) -> BatchState {
    let mut runs = 0;
    let mut state = BatchState::Carrying;
    for l in lines {
        state = match l["event"].as_str().unwrap_or_default() {
            "carry" | "eject" => BatchState::Gating(runs + 1),
            "run" if l["code"] == 0 => {
                runs += 1;
                BatchState::Pushing
            }
            "run" => {
                runs += 1;
                BatchState::Halving
            }
            "attribute" => BatchState::Halving,
            "push" => BatchState::Pushing,
            "landed" => BatchState::Landed,
            "stop" => BatchState::Stopped,
            _ => state,
        };
    }
    state
}

/// Every batch of the log in the order formed, each with its lines (those carrying its id, from its `batch` line on) and state.
#[must_use]
pub fn batches(log: &[Value]) -> Vec<Batch> {
    let mut out: Vec<Batch> = Vec::new();
    for line in log {
        let Some(id) = line["batch"].as_str() else {
            continue;
        };
        if line["event"] == "batch" {
            out.push(Batch {
                id: id.to_owned(),
                changes: listed(line, "changes").map(str::to_owned).collect(),
                lines: Vec::new(),
                state: BatchState::Carrying,
            });
        }
        if let Some(b) = out.iter_mut().rev().find(|b| b.id == id) {
            b.lines.push(line.clone());
            b.state = state_of(&b.lines);
        }
    }
    out
}

/// A hand-in's state (data-model.md, "A hand-in").
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum HandInState {
    Landed,
    Superseded,
    /// Its repair entry.
    Ejected(String),
    /// The open batch naming it.
    InBatch(String),
    Waiting,
}

impl fmt::Display for HandInState {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::Landed => f.write_str("landed"),
            Self::Superseded => f.write_str("superseded"),
            Self::Ejected(r) if r.starts_with("ask:") => {
                write!(f, "ejected -> the round arbiter {r}")
            }
            Self::Ejected(r) => write!(f, "ejected -> repair {r}"),
            Self::InBatch(b) => write!(f, "in batch {b}"),
            Self::Waiting => f.write_str("waiting"),
        }
    }
}

/// What a hand-in's state is computed from.
pub struct World<'a> {
    /// The lane's hand-ins, in the pool log's order.
    pub hand_ins: &'a [HandIn],
    /// The commits of them `origin/main` holds (`builder_done::held_by`).
    pub on_main: &'a BTreeSet<String>,
    pub log: &'a [Value],
    pub batches: &'a [Batch],
}

/// A hand-in's state, the first of the module doc's order that holds (data-model.md's, `in batch` moved before `superseded`).
#[must_use]
pub fn state(h: &HandIn, w: &World) -> HandInState {
    let landed_line = w
        .log
        .iter()
        .any(|l| l["event"] == "landed" && listed(l, "landed").any(|s| names(&h.commit, s)));
    if w.on_main.contains(&h.commit) || landed_line {
        return HandInState::Landed;
    }
    // the last line naming it an `eject`, or the `landed` line that ended its batch listing it as ejected (461 T15: read as `waiting`
    // there, an ejected hand-in formed a batch again)
    let last = w.log.iter().rev().find(|l| mentions(l, &h.commit));
    let ended_out =
        |l: &&Value| l["event"] == "landed" && listed(l, "ejected").any(|s| names(&h.commit, s));
    let ejected = last.filter(|l| l["event"] == "eject" || ended_out(l));
    let open = w
        .batches
        .iter()
        .find(|b| b.open() && b.changes.iter().any(|c| names(&h.commit, c)));
    if let (Some(b), None) = (open, ejected) {
        return HandInState::InBatch(b.id.clone());
    }
    let later = w
        .hand_ins
        .iter()
        .skip_while(|o| o.commit != h.commit)
        .skip(1)
        .any(|o| o.feature == h.feature && o.tasks.iter().any(|t| h.tasks.contains(t)));
    if later {
        return HandInState::Superseded;
    }
    if ejected.is_none() {
        return HandInState::Waiting;
    }
    // to the repair its last `eject` line names, or the round arbiter's trigger it waits on (461 T18: the tripwire files no repair)
    let ejection = w
        .log
        .iter()
        .rev()
        .find(|l| l["event"] == "eject" && mentions(l, &h.commit));
    HandInState::Ejected(
        ejection
            .and_then(|l| l["repair"].as_str().or_else(|| l["arbiter"].as_str()))
            .unwrap_or_default()
            .to_owned(),
    )
}

/// The repair entries the log's ejections filed that no hand-in answers by its `repair_of`, each once, in the order filed.
#[must_use]
pub fn repairs_open(log: &[Value], hand_ins: &[HandIn]) -> Vec<String> {
    let mut open: Vec<String> = Vec::new();
    let filed = log
        .iter()
        .filter(|l| l["event"] == "eject")
        .filter_map(|l| l["repair"].as_str());
    for r in filed {
        let answered = hand_ins.iter().any(|h| h.repair_of.as_deref() == Some(r));
        if !answered && !open.iter().any(|o| o == r) {
            open.push(r.to_owned());
        }
    }
    open
}

#[cfg(test)]
mod tests;
