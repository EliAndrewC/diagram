//! A BUILDER WAITING ON A WATCH THAT NEVER FIRES IS SEEN AND WOKEN (451 T193; the GM 2026-11-23: "I don't see any work happening").
//! WHY: 451 T184's builder (`a676c53072fd7258b`) ended its turn at 20:27:39Z waiting on its Monitor `bx5gtybg3`. The watch ended at
//! 20:39 - the coordinator's Stops listed it in `background_tasks` until 20:39:12 and never after - but its notice reached the
//! builder's transcript only after the coordinator's message at 21:35 (record 846, stamped 20:39:12, written after record 842, stamped
//! 21:35:26), so the builder waited about an hour on nothing, and the idle check said nothing: 451's hold (`holds`, "451 starts no new
//! task") silences the open-task block, and nothing else looked at the builder (measured 2026-11-23 from the coordinator's transcript
//! `c6fd72d1-...jsonl`, its subagents directory and 451's event log).
//!
//! A builder the session's transcript reads as running (launched or resumed, or its last notice interim) COUNTS AS RUNNING ONLY WHILE
//! IT HAS LIVE WORK: the Stop's `background_tasks` (the harness's own list of what runs, subagents' shells and sub-agents among them -
//! the builder's `bx5gtybg3` listed while it ran) names the builder itself or one of the runs its own transcript launched, or a
//! sub-agent of its own is still writing; or its own transcript moved within [`STALL_SECS`]. One with neither, whose task is still
//! open, is STALLED, and the idle check names it with its last line and the wake command - through a hold, which holds new tasks,
//! never a started builder's wake.
//!
//! WHY A BUILDER WITH AN OPEN TASK (a CONVENTION, the easier route where the record is silent): replayed over the coordinator's 42 idle
//! checks of 2026-11-23, every agent read as running with no live work named 21 agents at a check, the oldest silent for 6.7 days -
//! interim agents that never notified again, their work done by others; a builder (`builder_brief`) of a task still open named 3 in
//! all: T184's, and 451 T51's and 449 T158's, abandoned a day earlier with their tasks still open. Each is said once (`idle`).

use std::collections::HashSet;
use std::path::Path;
use std::time::{Duration, SystemTime};

use serde_json::Value;

use super::{builders, open_boxes, read_in_order, subagents};

/// How long a builder with no live work may be silent before it is named, in seconds: `L7R_STALL_SECS`, a GUESS of 600. Measured
/// 2026-11-23 over the 479 subagent transcripts written that day: the longest silence of an agent at work - a gap that ends in its own
/// reply or a tool's result, not in a notice or a prompt that woke it - was 280.6 s (an advisor call; p99.9 181 s, 20,003 gaps), so
/// 600 s is about twice it. A foreground call longer than that (the Bash tool's cap is 600 s) is no stall either way: the harness lists
/// an agent mid-turn as a running `subagent`, which is live work.
pub(super) const STALL_SECS: u64 = 600;

/// How many characters of a builder's last line the notice quotes (a CONVENTION: one line of a terminal).
const LAST: usize = 160;

/// A builder read as running with no live work and a silent transcript.
#[derive(Debug)]
pub(super) struct Stall {
    pub id: String,
    /// Its meta's description.
    pub description: String,
    /// The first line of its last reply.
    pub last: String,
    /// When its transcript last moved, seconds past the epoch.
    pub since: i64,
    /// Whether its context is past the cap (`context::CAP_TOKENS`): FR-006 resumes it only by a fresh dispatch from its handoff.
    pub capped: bool,
}

/// What [`stalled`] found: the stalled builders; how long until the next one that would be crosses the bound - a builder with no
/// live work still within it - None where none waits so; and whether one has live work that may yet end.
#[derive(Debug, Default)]
pub(super) struct Found {
    pub stalls: Vec<Stall>,
    pub soonest: Option<Duration>,
    /// Whether a builder of an open task has live work that may end with no notice to the session (its own run, its child), so the
    /// idle check looks again while it waits (`idle`).
    pub watched: bool,
    /// The other builders of open tasks read as running, each its status line (the status probe's, `idle::status`).
    pub working: Vec<String>,
}

impl Stall {
    /// Its line of the notice, with its wake command.
    pub(super) fn line(&self) -> String {
        format!(
            "- {} \"{}\", silent since {} UTC, last line \"{}\". {}",
            self.id,
            self.description,
            crate::once::hhmm(self.since),
            self.last,
            if self.capped {
                "Past the context cap: dispatch a fresh builder from its handoff, not a SendMessage (FR-006).".to_owned()
            } else {
                format!(
                    "Wake it: SendMessage to {} \"Background work ended; read its output, go on from your handoff.\"",
                    self.id
                )
            }
        )
    }
}

/// How long ago `file` was last written; None where it cannot be read or was written after `now`.
fn age(file: &Path, now: SystemTime) -> Option<Duration> {
    let at = std::fs::metadata(file).and_then(|m| m.modified()).ok()?;
    now.duration_since(at).ok()
}

/// Whether feature `number` has task `id` open in the clone at `root` (`specs/<number>-*/tasks.md`'s `- [ ]` lines).
fn open(root: &Path, number: &str, ids: &[String]) -> bool {
    crate::speckit::feature_dirs(&root.join("specs"))
        .iter()
        .filter(|d| {
            d.file_name()
                .is_some_and(|n| n.to_string_lossy().starts_with(&format!("{number}-")))
        })
        .filter_map(|d| std::fs::read_to_string(d.join("tasks.md")).ok())
        .any(|text| open_boxes(&text).iter().any(|(id, _)| ids.contains(id)))
}

/// The builders the session's transcript reads as running, of a task still open in the clone at `root`, that have no live work by
/// `live` (the Stop's `background_tasks` ids) and whose own transcript has been silent past `bound`, in id order, and how soon the next
/// such builder still within the bound crosses it. An id with no transcript of its own (a shell) is never one; a read error names none
/// (failing toward silence, as the idle check's other readers do).
pub(super) fn stalled(
    transcript: &Path,
    root: &Path,
    live: &HashSet<String>,
    bound: Duration,
) -> Found {
    let Ok(session) = read_in_order(transcript, "") else {
        return Found::default();
    };
    let dir = subagents(transcript);
    let now = SystemTime::now();
    let own = |id: &str| dir.join(format!("agent-{id}.jsonl"));
    let mut running: Vec<&String> = session.ids.keys().collect();
    running.sort_unstable();
    let mut found = Found::default();
    for id in running {
        let file = own(id);
        let Some(silent) = age(&file, now) else {
            continue;
        };
        if live.contains(id) {
            continue;
        }
        let Some((number, tasks)) = builders::builder_brief(&dir, id) else {
            continue;
        };
        let Ok(work) = read_in_order(&file, id) else {
            continue;
        };
        let busy = work
            .ids
            .keys()
            .any(|w| live.contains(w) || age(&own(w), now).is_some_and(|a| a <= bound));
        if !open(root, &number, &tasks) {
            continue;
        }
        if busy {
            found.watched = true;
            found.working.push(format!(
                "- {id} \"{}\": working, its own run or sub-agent live.",
                description(&dir, id)
            ));
            continue;
        }
        if silent <= bound {
            let left = bound - silent;
            found.soonest = Some(found.soonest.map_or(left, |s| s.min(left)));
            found.working.push(format!(
                "- {id} \"{}\": working, its transcript moved {} s ago.",
                description(&dir, id),
                silent.as_secs()
            ));
            continue;
        }
        let since = now.checked_sub(silent).unwrap_or(now);
        found.stalls.push(Stall {
            id: id.clone(),
            description: description(&dir, id),
            last: last_line(&file),
            since: since
                .duration_since(SystemTime::UNIX_EPOCH)
                .map_or(0, |d| i64::try_from(d.as_secs()).unwrap_or(i64::MAX)),
            capped: crate::context::context(&file).is_some_and(|c| c >= crate::context::CAP_TOKENS),
        });
    }
    found
}

/// Agent `id`'s description from its meta file, "" where it has none.
fn description(dir: &Path, id: &str) -> String {
    std::fs::read_to_string(dir.join(format!("agent-{id}.meta.json")))
        .ok()
        .and_then(|t| serde_json::from_str::<Value>(&t).ok())
        .and_then(|m| Some(m.get("description")?.as_str()?.to_owned()))
        .unwrap_or_default()
}

/// The first line of the last text an agent's transcript holds from the model (an `assistant` record's text block), cut to [`LAST`]
/// characters; "" where it holds none.
fn last_line(file: &Path) -> String {
    let text = std::fs::read_to_string(file).unwrap_or_default();
    let mut last = String::new();
    for line in text.lines() {
        let Ok(record) = serde_json::from_str::<Value>(line) else {
            continue;
        };
        if record.get("type").and_then(Value::as_str) != Some("assistant") {
            continue;
        }
        if let Some(said) = record["message"]["content"]
            .as_array()
            .into_iter()
            .flatten()
            .filter(|b| b["type"] == "text")
            .find_map(|b| b["text"].as_str())
        {
            said.lines()
                .find(|l| !l.trim().is_empty())
                .unwrap_or_default()
                .clone_into(&mut last);
        }
    }
    last.chars().take(LAST).collect()
}
