//! THE LANE'S COMPUTED STATES, READ IN ONE PLACE (feature 461 T11's readers, moved here by 461 T63; plan D8, `data-model.md`): the
//! states of a hand-in and of a batch, COMPUTED from the pool log's `done` lines, the done refs, `origin/main` and the lane's log
//! (`l7r-lane/lane.jsonl` of the git common directory) - never typed into a file (the queue's rule, `crate::builder_queue`). The lane
//! crate (`rust/gate/crates/lane/src/log.rs`, which keeps the log's writer and re-exports these) and the Stop rule
//! (`crate::lane_wake::holds`, which the guard reaches where it reaches no gate crate) both read here, so a change to a batch's or
//! a hand-in's state moves the Stop rule with it. Until T63 the Stop rule held a parallel copy, which disagreed on one point (below).
//!
//! A HAND-IN is a `done` line of the pool's log with `"handed_in": true`, one a commit (a bundle's tasks share it), that is still
//! the lane's: a done ref names its commit, or a line of the lane's log does (data-model.md, "A hand-in"; a done ref deleted by a
//! hand carry in phase 1 takes it off the lane). Its state, the first that holds ([`state`]): `landed` (`origin/main` holds its
//! author's time and subject - `task`'s `builder_done::held_by`, the carried rule, asked by the caller into [`World::on_main`] - or a
//! `landed` line lists it, which holds after the object is pruned), `in batch <b>` (an open batch names it and has not ejected it),
//! `superseded` (a later hand-in of its feature shares a task), `ejected -> repair <r>` (the last line of the log naming it is an
//! `eject`), else `waiting`. `in batch` is asked before `superseded`, against data-model.md's list (a deliberate deviation, 461 T53):
//! the open batch's `batch` line names this sha and lands it (D14, T52), so the batch carries it whatever later hand-in of its task
//! exists, and that later one waits.
//!
//! SUPERSEDED BY ANY LATER HAND-IN OF THE POOL'S LOG, the lane's or not ([`World::all`], 461 T63): a done ref is deleted only by a
//! carry's end, a landing's or a later hand-in of the task overwriting it, so a later hand-in off the lane has landed or been
//! superseded itself, and the earlier one's work rode in it (D14's handout half). The lane crate read the lane's hand-ins alone, so
//! an earlier hand-in kept on the lane by a stopped batch's line read as waiting after its successor was carried by hand - and
//! would have been batched again; the Stop rule's copy read every hand-in, as data-model.md's "a later hand-in of the same task
//! exists" words it. The Stop rule's reading kept, shown red first (`lane`'s `wake::tests`).
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
use std::path::Path;

use serde_json::Value;

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
#[must_use]
pub fn names(sha: &str, named: &str) -> bool {
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
    /// Every hand-in of the pool's log, the lane's or not, in its order: what a later hand-in supersedes over (the module's doc).
    pub all: &'a [HandIn],
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
        .all
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

/// The hand-ins of `all` (the pool log's, [`hand_ins`]) on the lane (`refs`, the done refs' commits; `lane`, its log) whose state is
/// `waiting` with `origin/main` NOT ASKED: the caller asks it of these alone, or not at all (the Stop rule, which pays no git walk
/// a turn). One assembly the Stop rule's [`crate::lane_wake::holds`] and the lane crate's `wake::waiting_on` share (461 T63).
#[must_use]
pub fn waiting_unasked(all: &[HandIn], refs: &BTreeSet<String>, lane: &[Value]) -> Vec<HandIn> {
    let hand_ins = on_lane(all.to_vec(), refs, lane);
    let batches = batches(lane);
    let none = BTreeSet::new();
    let world = World {
        hand_ins: &hand_ins,
        all,
        on_main: &none,
        log: lane,
        batches: &batches,
    };
    hand_ins
        .iter()
        .filter(|h| state(h, &world) == HandInState::Waiting)
        .cloned()
        .collect()
}

#[cfg(test)]
mod tests;
