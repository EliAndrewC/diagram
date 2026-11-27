//! A plan review record's merge (feature 451 T256): git's merge driver for `specs/*/plan-review.json`, so two worktrees' tasks carried
//! into one clone keep both sides' verdicts with no hand merge. Every carry-over in the parallel trials (2026-11-25) conflicted there.
//! `.gitattributes` names the driver; `scripts/sync-with-main.sh` defines it in the clone's git config (a driver is local config).
//!
//! The merge is three-way against the base (451 T256-D2): the top level and the `blocks` and `tasks` maps key by key, each entry WHOLE,
//! never field by field - one side's digest beside the other's verdict could read CLEAR on a text nobody cleared. Both sides changing one
//! key: the later `reviewed` day wins, a tie the incoming side's; each entry carries its digest, so a wrong pick only owes a review again.
//! BUT FIRST THE TEXT THERE (451 T495): where the merged plan.md is known - `make carry` merges it before the record - an entry whose
//! digest that plan holds for its key wins over one whose digest it does not, since the text a reviewer judged is the text there.
//! WHY: T310's carry (cec429b447) replaced the clone's CLEAR on T475's filled Approach with the pool tree's same-day verdict on its
//! unfilled stub, the tie going to the incoming side, and the orphaned block then refused a landing's ticks (451 T487). git's own
//! driver (`merge-record %O %A %B`) is given no merged plan - mid-merge the work tree holds ours' (probed 2026-11-27, git 2.53) - so
//! there the day rule stands; the carry runs its pick with that driver failing, so the record reaches the in-process merge.
//! `block_reviews` is an append-only log (T256-D3): ours, then theirs' rows the base and ours lack, each side's order kept (the
//! review-round guard counts a task's trailing rows).

use std::collections::HashMap;
use std::path::Path;

use serde_json::{Map, Value};

use super::pretty;
use super::sections::digests;

/// The maps merged key by key; any other value is merged whole.
const KEYED: [&str; 2] = ["blocks", "tasks"];

fn reviewed(v: &Value) -> &str {
    v.get("reviewed").and_then(Value::as_str).unwrap_or("")
}

/// The digests the merged plan holds, by the record's map: `blocks` by each block's (`sha256`), `tasks` by each section's
/// (`section_sha256`).
#[derive(Default)]
struct Held {
    blocks: HashMap<String, String>,
    tasks: HashMap<String, String>,
}

impl Held {
    fn of(plan: &str) -> Self {
        let (blocks, tasks) = digests::of(plan);
        let keyed =
            |v: Vec<(String, String, String)>| v.into_iter().map(|(k, d, _)| (k, d)).collect();
        Self {
            blocks: keyed(blocks),
            tasks: keyed(tasks),
        }
    }

    /// The field an entry of `map` keeps its digest in, and the digest the plan holds for `key`.
    fn at(&self, map: &str, key: &str) -> Option<(&'static str, &str)> {
        match map {
            "blocks" => self.blocks.get(key).map(|d| ("sha256", d.as_str())),
            "tasks" => self.tasks.get(key).map(|d| ("section_sha256", d.as_str())),
            _ => None,
        }
    }
}

/// One value merged whole: where the two sides differ and the plan holds one's digest and not the other's, that one; else an
/// unchanged side takes the other's; both changed, the later `reviewed` wins, a tie theirs.
fn whole(
    base: Option<&Value>,
    ours: Option<&Value>,
    theirs: Option<&Value>,
    held: Option<(&str, &str)>,
) -> Option<Value> {
    let holds =
        |v: &Value| held.is_some_and(|(field, d)| v.get(field).and_then(Value::as_str) == Some(d));
    match (ours, theirs) {
        (o, t) if o == t => o.cloned(),
        (Some(o), Some(t)) if holds(o) != holds(t) => Some(if holds(o) { o } else { t }.clone()),
        (o, t) if o == base => t.cloned(),
        (o, t) if t == base => o.cloned(),
        // one side removed it and the other changed it: the changed entry is a newer verdict
        (None, t) => t.cloned(),
        (o, None) => o.cloned(),
        (Some(o), Some(t)) => Some(if reviewed(o) > reviewed(t) { o } else { t }.clone()),
    }
}

/// Ours, then each of theirs' rows that neither the base nor ours holds.
fn rows(base: Option<&Value>, ours: Option<&Value>, theirs: Option<&Value>) -> Value {
    let list = |v: Option<&Value>| v.and_then(Value::as_array).cloned().unwrap_or_default();
    let (base, mut out) = (list(base), list(ours));
    for row in list(theirs) {
        if !base.contains(&row) && !out.contains(&row) {
            out.push(row);
        }
    }
    Value::Array(out)
}

fn keyed(
    base: Option<&Value>,
    ours: Option<&Value>,
    theirs: Option<&Value>,
    map: Option<&str>,
    held: &Held,
) -> Option<Value> {
    let (Some(o), Some(t)) = (
        ours.and_then(Value::as_object),
        theirs.and_then(Value::as_object),
    ) else {
        return whole(base, ours, theirs, None);
    };
    let empty = Map::new();
    let b = base.and_then(Value::as_object).unwrap_or(&empty);
    let mut out = Map::new();
    for key in o.keys().chain(t.keys().filter(|k| !o.contains_key(*k))) {
        let (bv, ov, tv) = (b.get(key), o.get(key), t.get(key));
        let merged = match (map, key.as_str()) {
            (None, "block_reviews") => Some(rows(bv, ov, tv)),
            (None, name) if KEYED.contains(&name) => keyed(bv, ov, tv, Some(name), held),
            (None, _) => whole(bv, ov, tv, None),
            (Some(within), name) => whole(bv, ov, tv, held.at(within, name)),
        };
        if let Some(v) = merged {
            out.insert(key.clone(), v);
        }
    }
    Some(Value::Object(out))
}

/// The three records merged, beside the merged plan where it is known; the error names the side that is not JSON.
pub(super) fn merge_records(
    base: &str,
    ours: &str,
    theirs: &str,
    plan: Option<&str>,
) -> Result<Value, &'static str> {
    let parse = |text: &str, side| {
        if text.trim().is_empty() {
            return Ok(Value::Object(Map::new()));
        }
        serde_json::from_str::<Value>(text).map_err(|_| side)
    };
    let (b, o, t) = (
        parse(base, "the base")?,
        parse(ours, "ours")?,
        parse(theirs, "theirs")?,
    );
    let held = plan.map(Held::of).unwrap_or_default();
    Ok(keyed(Some(&b), Some(&o), Some(&t), None, &held).unwrap_or_default())
}

/// `l7r-gate plan merge-record %O %A %B`: the merge written to `%A`, git's contract; exit 1 leaves `%A` as it was, unmerged; `plan`
/// is none there. Asked in process by `make carry` (the `land` crate's `carry.rs`, 451 T292) with the merged plan.md's text (451 T495).
#[must_use]
pub fn merge_files(base: &Path, ours: &Path, theirs: &Path, plan: Option<&str>) -> crate::Reply {
    let read = |p: &Path| std::fs::read_to_string(p).unwrap_or_default();
    match merge_records(&read(base), &read(ours), &read(theirs), plan) {
        Ok(v) => match std::fs::write(ours, pretty(&v)) {
            Ok(()) => super::said(String::new()),
            Err(e) => super::fail(format!("plan merge-record: cannot write {}: {e}\n", ours.display()), 1),
        },
        Err(side) => super::fail(
            format!("plan merge-record: {side} of plan-review.json is not JSON, so it is left to a hand merge: keep both sides' entries under `blocks` and `tasks` and both sides' `block_reviews` rows, then `git add` it (451 T256)\n"),
            1,
        ),
    }
}

#[cfg(test)]
mod tests;
