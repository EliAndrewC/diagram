//! THE LANE'S REPAIR ENTRIES, OFFERED FIRST (feature 461 T16, plan D7; data-model.md, "A repair entry"; closes 451 T308's "repaired by
//! whoever is cheapest"): a change the lane ejects is a line of `l7r-lane/repairs.jsonl` in the git common directory (the lane's
//! `repairs.rs` its one writer, T15), and here it becomes the next dispatch - `make builder-next`, `make queue`, `make builder-done`'s
//! next-dispatch line and the pool-idle Stop guard name an open entry BEFORE any `queue.txt` entry (`LANE_REPAIR_FIRST` = 1, a GUESS
//! knob: `0` offers a repair only where no queue entry is READY), with the command whose brief a FRESH builder needs: `make
//! builder-brief ... REPAIR=<id>`, which names the gate's output (the attempt file) and the change to repair - for an arbiter's
//! repair (`why` `arbiter`, T18), whose `attempt` is its trigger, the ruling's row and the two red attempts ([`Repair::read`], 461
//! T67). The guard cannot reach
//! the lane crate (the lane builds on `l7r_shared`, so the other way is a cycle): the three files are read here, by their names.
//!
//! OPEN, the first that holds decides (each the entry's id `r<n>`):
//! 1. NOT YET EJECTED - no `eject` line of `l7r-lane/lane.jsonl` carries the id: the runner files the entry before its `eject` lines,
//!    and a runner killed between them resumes what the log has not ejected, which may land a change the entry lists (461 T15's
//!    Decision 7). So an entry is offered only once an `eject` line names it, and ITS CHANGES ARE THOSE LINES' `change`s, never the
//!    entry's `ejected` alone; its tasks are those changes' done lines' tasks (the entry's `tasks` where no done line names one).
//! 2. ANSWERED - a `done` line of the pool's log names it in `repair_of` (`make builder-done` copies it from the `brief` line that
//!    `make builder-brief REPAIR=` wrote): built.
//! 3. SUPERSEDED - a hand-in (a `done` line with `"handed_in": true`) of its feature sharing one of its tasks, later than its
//!    changes' own hand-ins (their done lines; the last `eject` line where none names them), so one made while the batch was still
//!    open, before the eject, counts (461 T26, plan D14: the later hand-in waits for the open batch, then supersedes the ejected
//!    one; asked against the eject alone, the entry stayed open, offered to a fresh builder beside the work that replaced it): data-model.md's "the earlier one's repair entry then read as closed (`superseded`)", the work handed in again
//!    by a builder briefed without `REPAIR=`. The lane's own `log::repairs_open` (`make lane`'s status) lists these same entries by id (461 T65); this offers.
//!
//! Of the open ones, [`offer`] passes over two kinds with a line, and the rest are READY:
//! - IN FLIGHT - a pool tree is held for one of its tasks: a handout would hand that tree back to whoever holds it, and a repair is
//!   a fresh builder's;
//! - NOT A BRIEF'S KIND - `integrate` (T19, a push failed twice) is no kind `make builder-brief` takes yet: never offered as a
//!   command that refuses.
//!
//! A missing file is no entry, read for nothing: the Stop guard asks this on every turn's end.
// GUARD_EDIT_OK: feature 461 T16 - a new operation, the lane's repair entries offered first by the builders' queue and the pool-idle guard

use std::path::Path;

use serde_json::Value;

use crate::builder_pool::Tree;

/// The repairs' file, in the lane's directory (`l7r_gate_lane::repairs::FILE`).
pub const FILE: &str = "repairs.jsonl";
/// The knob: `0` offers a repair only where no queue entry is READY; anything else, or unset, offers it first.
pub const KNOB: &str = "LANE_REPAIR_FIRST";
/// The steps a red unit's last word names, whose other words are crate directories (the lane's `attribute.rs`).
const STEPS: [&str; 5] = ["test", "lint", "cover-build", "cover-run", "build"];

/// A repair entry the queue may offer.
#[derive(Debug, Clone, PartialEq, Eq, Default)]
pub struct Repair {
    /// `r<n>`.
    pub id: String,
    /// The feature's key, `461`, from the entry's spec directory name.
    pub key: String,
    pub tasks: Vec<String>,
    pub kind: String,
    pub batch: String,
    pub why: String,
    pub units: Vec<String>,
    /// The attempt file, the gate's output - but for `why` `arbiter` (T18's `file_ruled`), the trigger its ruling answers.
    pub attempt: String,
    /// The ejected done commits, full shas, as the `eject` lines name them.
    pub changes: Vec<String>,
    /// For `why` `arbiter` (461 T67): its ruling's row, `specs/<spec>/arbiter.jsonl line <n>` under `clone` (the file alone where
    /// no row holds the trigger), and the batch `stop` line's two attempt files; empty for any other.
    pub ruling: String,
    pub attempts: Vec<String>,
    /// The clone, where the ruling is recorded uncommitted (a pool tree has no copy of it).
    pub clone: String,
}

impl Repair {
    /// As a reader names it: `461 T13 (repair r3)`.
    #[must_use]
    pub fn name(&self) -> String {
        format!("{} {} (repair {})", self.key, self.tasks.join(","), self.id)
    }

    /// The crate directories its red units name (`<dir> [<dir> ...] [(+<k> more)] <step>`); none for a suite, a row or a conflict.
    #[must_use]
    pub fn crates(&self) -> Vec<String> {
        let mut out: Vec<String> = Vec::new();
        // an arbiter's units are its ruling's words (`continue: fix the test`), never red units, whatever their last word
        let units = if self.why == "arbiter" {
            &[][..]
        } else {
            &self.units[..]
        };
        for u in units {
            let words: Vec<&str> = u.split_whitespace().collect();
            // an empty unit and a unit whose last word is no step (a suite, a row) name no crate alike
            let Some((_, dirs)) = words.split_last().filter(|(s, _)| STEPS.contains(s)) else {
                continue;
            };
            for d in dirs.iter().take_while(|d| !d.starts_with('(')) {
                if !out.iter().any(|o| o == d) {
                    out.push((*d).to_owned());
                }
            }
        }
        out
    }

    /// What its fresh builder reads first, as the brief and the offer name it: the gate's output, or for an arbiter's repair the
    /// ruling's row and the two red attempts (its `attempt` is the trigger, no file).
    #[must_use]
    pub fn read(&self) -> String {
        if self.why != "arbiter" {
            return format!("the gate's output {}", self.attempt);
        }
        // the paths under the clone named from it, and an attempt in the first's directory by its file name: the brief's block
        // stays under the prefix guard's 2,000 characters (2,039 with three whole paths, 2026-11-27)
        let root = format!("{}/", self.clone);
        let dir = |p: &str| Path::new(p).parent().map(Path::to_path_buf);
        let first = self
            .attempts
            .first()
            .map(String::as_str)
            .unwrap_or_default();
        let named: Vec<&str> = self
            .attempts
            .iter()
            .enumerate()
            .map(|(i, a)| match Path::new(a).file_name() {
                Some(f) if i > 0 && dir(a) == dir(first) => f.to_str().unwrap_or(a),
                _ => a.strip_prefix(&root).unwrap_or(a),
            })
            .collect();
        format!(
            "the ruling of {} and the red attempts, in {}: {}, {}",
            self.attempt,
            self.clone,
            self.ruling,
            named.join(" ")
        )
    }

    /// The command that briefs its fresh builder.
    #[must_use]
    pub fn command(&self) -> String {
        let crates = self.crates();
        let named = if crates.is_empty() {
            String::new()
        } else {
            format!(" CRATE=\"{}\"", crates.join(" "))
        };
        format!(
            "make builder-brief T={} F={} KIND={}{named} REPAIR={}",
            self.tasks.join(","),
            self.key,
            self.kind,
            self.id
        )
    }
}

/// What the repair entries offer.
#[derive(Debug, Clone, PartialEq, Eq, Default)]
pub struct Offer {
    /// The open entries a fresh builder can take now, in the order filed.
    pub ready: Vec<Repair>,
    /// Each open entry passed over, with why.
    pub passed: Vec<(Repair, String)>,
}

/// A JSON-lines file's objects: none for a missing file, a torn line skipped.
fn lines(file: &Path) -> Vec<Value> {
    std::fs::read_to_string(file)
        .unwrap_or_default()
        .lines()
        .filter_map(|l| serde_json::from_str::<Value>(l).ok())
        .collect()
}

fn strings(v: &Value) -> Vec<String> {
    v.as_array()
        .into_iter()
        .flatten()
        .filter_map(Value::as_str)
        .map(str::to_owned)
        .collect()
}

/// A done line's feature key and tasks.
fn done_of(l: &Value) -> Option<(&str, Vec<String>)> {
    let (feature, tasks) = l["detail"].as_str()?.split_once(' ')?;
    Some((feature, tasks.split(',').map(str::to_owned).collect()))
}

/// An arbiter's repair's reading (461 T67): its ruling's row in the clone's `specs/<feature>/arbiter.jsonl` - the last row holding
/// `trigger`, as `checks::arbiter::rulings_of` reads it, named by its line (the file alone where none holds it) - and the attempt
/// files of the batch's `stop` line for that trigger (T18's `trip` writes them space-joined), set on `r`.
fn ruled(r: &mut Repair, common: &Path, lane: &[Value], feature: &str) {
    let clone = common.parent().unwrap_or(common);
    let file = format!("specs/{feature}/arbiter.jsonl");
    let text = std::fs::read_to_string(clone.join(&file)).unwrap_or_default();
    let trigger = Some(r.attempt.as_str());
    let row = crate::checks::reply::py_lines(&text).iter().rposition(|l| {
        serde_json::from_str::<Value>(l).is_ok_and(|v| {
            v.get("trigger")
                .map(crate::checks::arbiter::py_text)
                .as_deref()
                == trigger
        })
    });
    r.ruling = row.map_or(file.clone(), |i| format!("{file} line {}", i + 1));
    r.clone = clone.display().to_string();
    r.attempts = lane
        .iter()
        .find(|l| {
            l["event"] == "stop"
                && l["why"] == "arbiter"
                && l["batch"] == r.batch.as_str()
                && l["trigger"] == r.attempt.as_str()
        })
        .and_then(|l| l["attempts"].as_str())
        .unwrap_or_default()
        .split_whitespace()
        .map(str::to_owned)
        .collect();
}

/// The open repair entries under the git common directory `common`, every one: ejected, unanswered and not superseded (the
/// module's 1-3), in the order filed.
#[must_use]
pub fn open(common: &Path) -> Vec<Repair> {
    let dir = common.join(crate::lane_wake::DIR);
    let entries = lines(&dir.join(FILE));
    if entries.is_empty() {
        return Vec::new();
    }
    let lane = lines(&dir.join(crate::lane_wake::FILE));
    let pool = lines(&common.join(super::LOG));
    let dones: Vec<&Value> = pool.iter().filter(|l| l["event"] == "done").collect();
    let mut out = Vec::new();
    for e in entries {
        let id = e["repair"].as_str().unwrap_or_default();
        let ejects: Vec<&Value> = lane
            .iter()
            .filter(|l| l["event"] == "eject" && l["repair"] == id)
            .collect();
        let changes: Vec<String> = ejects
            .iter()
            .filter_map(|l| l["change"].as_str().map(str::to_owned))
            .collect();
        if id.is_empty() || changes.is_empty() || dones.iter().any(|d| d["repair_of"] == id) {
            continue;
        }
        let feature = e["feature"].as_str().unwrap_or_default();
        let key: String = feature.chars().take_while(char::is_ascii_digit).collect();
        let mut tasks: Vec<String> = Vec::new();
        for c in &changes {
            let named = dones.iter().find(|d| d["commit"] == c.as_str());
            for t in named
                .and_then(|d| done_of(d))
                .map(|(_, t)| t)
                .unwrap_or_default()
            {
                if !tasks.contains(&t) {
                    tasks.push(t);
                }
            }
        }
        if tasks.is_empty() {
            tasks = strings(&e["tasks"]);
        }
        // later than the ejected changes' own hand-ins, else than the last `eject` line where no done line names them (461 T26, D14):
        // a hand-in of the task made while the batch was still open, before the eject, supersedes it as one made after does
        let own = changes
            .iter()
            .filter_map(|c| dones.iter().find(|d| d["commit"] == c.as_str()))
            .filter_map(|d| d["utc"].as_str())
            .max();
        let last = own.or_else(|| ejects.iter().filter_map(|l| l["utc"].as_str()).max());
        let later = |d: &&&Value| {
            d["handed_in"] == true
                && d["utc"].as_str() > last
                && !d["commit"]
                    .as_str()
                    .is_some_and(|c| changes.iter().any(|x| x == c))
                && done_of(d)
                    .is_some_and(|(f, ts)| f == key && ts.iter().any(|t| tasks.contains(t)))
        };
        if dones.iter().any(|d| later(&d)) {
            continue;
        }
        let text = |k: &str| e[k].as_str().unwrap_or_default().to_owned();
        let mut r = Repair {
            id: id.to_owned(),
            tasks,
            kind: e["kind"].as_str().unwrap_or("fix").to_owned(),
            batch: text("batch"),
            why: text("why"),
            units: strings(&e["units"]),
            attempt: text("attempt"),
            changes,
            key,
            ..Repair::default()
        };
        if r.why == "arbiter" {
            ruled(&mut r, common, &lane, feature);
        }
        out.push(r);
    }
    out
}

/// The open entries sorted into what a fresh builder can take and what is passed over (the module's last two), `held` the pool's
/// held trees.
#[must_use]
pub fn offer(common: &Path, held: &[Tree]) -> Offer {
    let mut o = Offer::default();
    for r in open(common) {
        let holds = |t: &&Tree| t.feature == r.key && t.tasks.iter().any(|x| r.tasks.contains(x));
        let why = if let Some(t) = held.iter().find(holds) {
            Some(format!(
                "in flight ({} holds {})",
                t.holder(),
                t.tree.display()
            ))
        } else if super::KINDS.contains(&r.kind.as_str()) {
            None
        } else {
            Some(format!(
                "kind {} is no kind make builder-brief takes yet: brief its builder by hand",
                r.kind
            ))
        };
        match why {
            Some(w) => o.passed.push((r, w)),
            None => o.ready.push(r),
        }
    }
    o
}

/// The knob, read: a repair offered before any queue entry.
#[must_use]
pub fn first() -> bool {
    crate::env::var(KNOB).trim() != "0"
}

#[cfg(test)]
mod tests;
