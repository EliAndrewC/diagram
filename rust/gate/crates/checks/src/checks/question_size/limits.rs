//! The per-page limits (feature 451 T184, the GM 2026-11-23: *"an audit-based process that permits us to go past the size
//! limit when an adversarial subagent check confirms that there don't seem to be a lot of good ways to do edits that would
//! allow us to maintain the current amount of useful information ... so that we record a new limit for this specific
//! entry"*). `research/size-limits.json` maps a question's path to its `limit`, the `date`, and the `size-exception`
//! check's `verdict` (INDIVISIBLE) with its `ledger` row; an entry with no INDIVISIBLE verdict, or a limit not above the
//! cap, is refused rather than read.

use std::collections::BTreeMap;
use std::path::Path;

use serde_json::Value;

pub(super) const RECORD: &str = "research/size-limits.json";

fn field<'v>(e: &'v Value, name: &str) -> &'v str {
    e.get(name).and_then(Value::as_str).unwrap_or("")
}

/// Each recorded page's limit, or the problems that refuse the record.
pub(super) fn read(root: &Path, cap: usize) -> Result<BTreeMap<String, usize>, Vec<String>> {
    let Ok(text) = std::fs::read_to_string(root.join(RECORD)) else {
        return Ok(BTreeMap::new());
    };
    let file: Value = serde_json::from_str(&text)
        .map_err(|e| vec![format!("question-size: {RECORD} does not parse: {e}")])?;
    let empty = serde_json::Map::new();
    let pages = file
        .get("pages")
        .and_then(Value::as_object)
        .unwrap_or(&empty);
    let mut bad = Vec::new();
    let mut limits = BTreeMap::new();
    for (page, e) in pages {
        if !field(e, "verdict").starts_with("INDIVISIBLE")
            || field(e, "date").is_empty()
            || field(e, "ledger").is_empty()
        {
            bad.push(format!("question-size: {RECORD}: {page}'s limit carries no size-exception verdict - a page's own limit needs `verdict: \"INDIVISIBLE - <why>\"`, its `date` and its `ledger` row (.claude/agents/size-exception.md); otherwise split the page"));
        }
        let limit = e
            .get("limit")
            .and_then(Value::as_u64)
            .and_then(|n| usize::try_from(n).ok())
            .unwrap_or(0);
        if limit <= cap {
            bad.push(format!("question-size: {RECORD}: {page}'s limit {limit} is not above the {cap} cap - drop the entry"));
        }
        limits.insert(page.clone(), limit);
    }
    if bad.is_empty() {
        Ok(limits)
    } else {
        Err(bad)
    }
}
