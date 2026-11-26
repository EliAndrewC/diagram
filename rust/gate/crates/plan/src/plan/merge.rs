//! A plan review record's merge (feature 451 T256): git's merge driver for `specs/*/plan-review.json`, so two worktrees' tasks carried
//! into one clone keep both sides' verdicts with no hand merge. Every carry-over in the parallel trials (2026-11-25) conflicted there.
//! `.gitattributes` names the driver; `scripts/sync-with-main.sh` defines it in the clone's git config (a driver is local config).
//!
//! The merge is three-way against the base (451 T256-D2): the top level and the `blocks` and `tasks` maps key by key, each entry WHOLE,
//! never field by field - one side's digest beside the other's verdict could read CLEAR on a text nobody cleared. Both sides changing one
//! key: the later `reviewed` day wins, a tie the incoming side's; each entry carries its digest, so a wrong pick only owes a review again.
//! `block_reviews` is an append-only log (T256-D3): ours, then theirs' rows the base and ours lack, each side's order kept (the
//! review-round guard counts a task's trailing rows).

use std::path::Path;

use serde_json::{Map, Value};

use super::pretty;

/// The maps merged key by key; any other value is merged whole.
const KEYED: [&str; 2] = ["blocks", "tasks"];

fn reviewed(v: &Value) -> &str {
    v.get("reviewed").and_then(Value::as_str).unwrap_or("")
}

/// One value merged whole: an unchanged side takes the other's; both changed, the later `reviewed` wins, a tie theirs.
fn whole(base: Option<&Value>, ours: Option<&Value>, theirs: Option<&Value>) -> Option<Value> {
    match (ours, theirs) {
        (o, t) if o == t => o.cloned(),
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
    depth: u8,
) -> Option<Value> {
    let (Some(o), Some(t)) = (
        ours.and_then(Value::as_object),
        theirs.and_then(Value::as_object),
    ) else {
        return whole(base, ours, theirs);
    };
    let empty = Map::new();
    let b = base.and_then(Value::as_object).unwrap_or(&empty);
    let mut out = Map::new();
    for key in o.keys().chain(t.keys().filter(|k| !o.contains_key(*k))) {
        let (bv, ov, tv) = (b.get(key), o.get(key), t.get(key));
        let merged = match (depth, key.as_str()) {
            (0, "block_reviews") => Some(rows(bv, ov, tv)),
            (0, k) if KEYED.contains(&k) => keyed(bv, ov, tv, 1),
            _ => whole(bv, ov, tv),
        };
        if let Some(v) = merged {
            out.insert(key.clone(), v);
        }
    }
    Some(Value::Object(out))
}

/// The three records merged; `None` names the side that is not JSON.
pub(super) fn merge_records(base: &str, ours: &str, theirs: &str) -> Result<Value, &'static str> {
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
    Ok(keyed(Some(&b), Some(&o), Some(&t), 0).unwrap_or_default())
}

/// `l7r-gate plan merge-record %O %A %B`: the merge written to `%A`, git's contract; exit 1 leaves `%A` as it was, unmerged.
pub(super) fn merge_files(base: &Path, ours: &Path, theirs: &Path) -> crate::Reply {
    let read = |p: &Path| std::fs::read_to_string(p).unwrap_or_default();
    match merge_records(&read(base), &read(ours), &read(theirs)) {
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
