//! A RULING THAT HOLDS NEW WORK (451 T183; the GM 2026-11-23, 451's request.md "Stop hooks that keep the session busy"): the round
//! arbiter's binding answer to a set-down ask, `ask:set-down-<feature>-...` in the feature's own `arbiter.jsonl`, ruled `continue` or
//! `accept`, whose `what` says no new task starts - today's `ask:set-down-451-gm-stop-for-convergence-talk` ("451 starts no new task")
//! and `ask:set-down-449-rows-gm-stop-for-convergence-talk` ("No other 449 task starts"). While one holds, the idle check names no task
//! of that feature. WHY: both rulings stood from 14:42 and the free-slot block went on naming 449 T403
//! and 451 T104 (measured 2026-11-23 from the coordinator's transcript, T183's plan section).
//!
//! Which ruling: the feature's NEWEST set-down ruling (its latest `utc`, the later line on a tie) decides, so a later ruling that sends
//! the work on (`ask:set-down-449-efficiency-round-4`, "Do not set down. Resume the ports now") ends an earlier hold, and the hold ends
//! only so - through the same door, `make arbiter-ask`. A `make task-start` does not end it: T183 was started under the 451 hold, which
//! still holds the rest of 451 (a task-start's own refusal never reads a hold, so a start the GM approved is never refused by one).
//! A ruling whose trigger names another feature's number (`ask:set-down-449-...` in 451's log) is that feature's, not this one's.
//!
//! What reads as a hold (a CONVENTION: the arbiter writes free prose and no field says "holds", so the words are read - the easier
//! route, root CLAUDE.md, where the record is silent): [`HOLD`]'s forms, matched against every set-down ruling on record (2026-11-23):
//! the two of today, `Set 444 down now`, `Set feature 449 down now`, `Stop 405 and start no further 405 task`, `Set 422 down`, the
//! pilot's `4. Then set down. The work resumes from the GM's reply` (ask:set-down-449-pilot, T183's MODE 4 round 2, D11: its set-down
//! holds T171 and the rest of 449 with it); and not `Do not set down`, `No set-down; the session goes on`, `Go on as proposed`, `T26 is
//! NOT set down`, `Before setting the feature down, check ...`, a bare `Do not start T150-T158` (a hold of named tasks, not of new
//! work: [`named`]) or the mid-landing waiver's `runs no make task-start` (one landing's, 451 T156).
//!
//! A RULING THAT HOLDS NAMED TASKS (T183's MODE 4, D6: the approved offer "respects binding rulings", and a ruling that holds a task by
//! name is one): the same newest set-down ruling's do-not-start clause ([`NAMED_HOLD`]) holds each task it names, a range each member
//! (`Do not start T150-T158`, ask:set-down-449-pilot, 2026-11-17), never a task the ruling names elsewhere. On record every such clause
//! stands beside a set-down (the pilot's `Then set down`, `Set feature 449 down now and do not start T83`, `Set 444 down now; do not
//! start T19's build`), so the feature hold covers it too; the clause holds its tasks alone under a ruling that sends other work on. The
//! idle check never names one, and is silent when only those are open. Its end is a feature hold's: a later set-down
//! ruling (449's pilot hold ended at ask:set-down-449-pieces34, its `do not start T83` at ask:set-down-449-efficiency-round-4's "T83
//! first"). Matched against every set-down ruling on record (2026-11-23): `Do not start T150-T158`, `do not start T83`, `do not start
//! T19's build`; `T24, T27-T33 stay untouched` is not of the form, and it holds nothing now (a later 444 ruling stands). `make
//! task-start`'s picker does not read it: a start the GM approved is never refused by a hold.

use std::path::Path;
use std::sync::LazyLock;

use fancy_regex::Regex;
use serde_json::Value;

use super::{re, rows};
use crate::state::field;

/// The words of a ruling that holds a feature's new work: no new, other or further task starts, or the feature set down.
static HOLD: LazyLock<Regex> = LazyLock::new(|| {
    re(concat!(
        r"(?i)\bstarts? no (?:new|other|further)\b[^.]*?\btasks?\b",
        r"|\bno (?:new|other|further) (?:\d{3} )?tasks? starts?\b",
        r"|\bstart no (?:new|other|further) (?:\d{3} )?tasks?\b",
        r"|\bset (?:feature )?\d{3} down\b",
        r"|\bthen set (?:it |the feature )?down\b",
    ))
});

/// A do-not-start clause and the task ids it names, ranges and lists: `Do not start T150-T158`, `do not start T83`.
static NAMED_HOLD: LazyLock<Regex> = LazyLock::new(|| {
    re(concat!(
        r"(?i)\b(?:do not|don't|never) start (T\d+[a-z]?(?:-T\d+[a-z]?)?",
        r"(?:(?:\s*,\s*|\s+(?:and|or|nor)\s+)T\d+[a-z]?(?:-T\d+[a-z]?)?)*)",
    ))
});

/// The feature number a set-down trigger names (`ask:set-down-449-...` -> 449); none for `ask:set-down-T26`.
static NAMED: LazyLock<Regex> = LazyLock::new(|| re(r"^ask:set-down-(\d{3})(?:-|$)"));

/// `feature`'s newest set-down ruling (`specs/<feature>/arbiter.jsonl`) ruled `continue` or `accept`, or None. A log that cannot be
/// read holds nothing: a hold only silences a nudge, so failing open costs a nudge, never a refusal.
fn newest(root: &Path, feature: &str) -> Option<Value> {
    let number = feature.split('-').next().unwrap_or(feature);
    let log = rows(&root.join("specs").join(feature).join("arbiter.jsonl")).ok()?;
    let mut newest: Option<&Value> = None;
    for row in &log {
        let trigger = field(row, "trigger");
        let named = NAMED.captures(trigger).ok().flatten();
        if !trigger.starts_with("ask:set-down-") || named.is_some_and(|c| &c[1] != number) {
            continue;
        }
        if newest.is_none_or(|n| field(n, "utc") <= field(row, "utc")) {
            newest = Some(row);
        }
    }
    newest
        .filter(|n| matches!(field(n, "ruling"), "continue" | "accept"))
        .cloned()
}

/// The trigger of the ruling that holds `feature`'s new work, or None.
#[must_use]
pub fn held(root: &Path, feature: &str) -> Option<String> {
    let newest = newest(root, feature)?;
    HOLD.is_match(field(&newest, "what"))
        .unwrap_or(false)
        .then(|| field(&newest, "trigger").to_owned())
}

/// The tasks `feature`'s newest set-down ruling holds by name ([`NAMED_HOLD`]), each range's every member; none where it holds none.
#[must_use]
pub fn named(root: &Path, feature: &str) -> Vec<String> {
    let Some(newest) = newest(root, feature) else {
        return Vec::new();
    };
    NAMED_HOLD
        .captures_iter(field(&newest, "what"))
        .map_while(Result::ok)
        .flat_map(|c| super::builders::task_ids(&c[1]))
        .collect()
}
