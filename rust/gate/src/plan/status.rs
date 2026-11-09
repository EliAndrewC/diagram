//! Which blocks of a plan a review still owes, and what a feature owes before a tick (feature 449 T066, from `plan_sections.py` and
//! `plan_gate.py`). A review of a plan keeps a verdict per block (feature 375 amendment 11, D60), and only a block added or changed
//! since its CLEAR verdict is owed: sixteen whole-plan reviews of 374 cost 13.7 million input tokens (observed 2026-10-13, method: the
//! review ledger), each re-judging every earlier decision because one edit outside a task's section staled the whole plan's verdict.

use std::collections::{BTreeMap, BTreeSet};
use std::path::Path;

use serde_json::{json, Map, Value};

use super::history::History;
use super::sections::{
    below_heading, block_digest, blocks, decides_nothing, digest, heading_text,
    lands_open_appended, leading_task, quiet_out, repointed, stem, strip_archive, task_sections,
    typo_only, wording_only, PART_B,
};

pub(super) const RECORD: &str = "plan-review.json";
pub(super) const REMOVED: &str = "(removed) ";
const HOW: &str = "dispatch `spec-fidelity` in its PLAN REVIEW mode with request.md, spec.md and plan.md, then record its JSON: make plan-verdict F=<feature> FILE=<json> AS=spec-fidelity";

pub(super) fn text_of<'v>(value: &'v Value, key: &str) -> Option<&'v str> {
    value.get(key).and_then(Value::as_str)
}

/// A value as Python's `str()` prints it for a digest lookup: a string as itself, a missing one as `None`.
fn sha_of(entry: &Value) -> Option<String> {
    entry
        .get("sha256")
        .filter(|v| truthy(v))
        .map(|v| v.as_str().map_or_else(|| v.to_string(), str::to_owned))
}

fn truthy(value: &Value) -> bool {
    !matches!(value, Value::Null | Value::Bool(false))
        && value != ""
        && value != 0
        && value.as_array().is_none_or(|a| !a.is_empty())
}

/// The block's earlier text: as the record kept it, or from the plan's history at its recorded digest.
fn earlier_text(entry: &Value, key: &str, history: Option<&History>) -> Option<String> {
    if let Some(kept) = text_of(entry, "text").filter(|t| !t.is_empty()) {
        return Some(kept.to_owned());
    }
    history?.block(key, &sha_of(entry)?)
}

/// Whether the task's section carries a CLEAR decision verdict that still matches it, a typo aside.
pub(super) fn task_current(
    review: &Value,
    plan: &str,
    task: &str,
    history: Option<&History>,
) -> bool {
    let sections = task_sections(plan);
    let Some(section) = sections.get(task) else {
        return false;
    };
    let empty = json!({});
    let entry = review
        .get("tasks")
        .and_then(|t| t.get(task))
        .unwrap_or(&empty);
    if text_of(entry, "verdict") != Some("CLEAR") {
        return false;
    }
    let recorded = text_of(entry, "section_sha256").unwrap_or("");
    if recorded == digest(section.as_bytes()) {
        return true;
    }
    let section = strip_archive(section);
    let kept = text_of(entry, "section_text")
        .filter(|t| !t.is_empty())
        .map(str::to_owned);
    let Some(earlier) = kept.or_else(|| history?.section(task, recorded)) else {
        return false;
    };
    let (was, now) = (
        quiet_out(&strip_archive(&earlier), plan),
        quiet_out(&section, plan),
    );
    let done = history
        .and_then(|h| std::fs::read_to_string(h.path().with_file_name("plan-done.md")).ok())
        .unwrap_or_default();
    typo_only(&was, &now) || typo_only(&repointed(&was, &now, task, &format!("{plan}{done}")), &now)
}

/// `{key: {sha256, verdict}}` the record holds: its `blocks`, or, a record from before amendment 11, its one verdict on each block.
pub(super) fn reviewed_blocks(review: &Value) -> Map<String, Value> {
    if let Some(have) = review.get("blocks").and_then(Value::as_object) {
        return have.clone();
    }
    let Some(text) = text_of(review, "plan_text") else {
        return Map::new();
    };
    let verdict = review.get("verdict").cloned().unwrap_or(Value::Null);
    blocks(text)
        .into_iter()
        .map(|(k, body, _)| {
            (
                k,
                json!({"sha256": block_digest(&body), "verdict": verdict, "text": body}),
            )
        })
        .collect()
}

/// The recorded entry this block was moved from: a recorded heading of the same stem, with the same text below its heading line.
fn moved_from(
    have: &Map<String, Value>,
    key: &str,
    body: &str,
    history: Option<&History>,
) -> Option<Value> {
    have.iter()
        .filter(|(k, e)| *k != key && e.is_object() && stem(k) == stem(key))
        .find_map(|(k, e)| {
            let earlier = earlier_text(e, k, history)?;
            (below_heading(&earlier) == below_heading(body)).then(|| {
                let mut moved = e.clone();
                moved["moved"] = json!(true);
                moved
            })
        })
}

fn span_of(plan: &str, section: &str) -> Option<(usize, usize)> {
    plan.find(section).map(|at| (at, at + section.len()))
}

fn inside(spans: &[(usize, usize)], at: usize) -> bool {
    spans.iter().any(|(lo, hi)| *lo <= at && at < *hi)
}

/// (the blocks owed a review, the blocks BLOCKED): every block outside a task section with its own current verdict, judged against the
/// record's verdict at its digest, a typo-scale change aside. A recorded block plan.md no longer has is owed too, as `(removed) <key>`,
/// unless `plan-done.md` holds it.
pub(super) fn block_status(
    review: &Value,
    plan: &str,
    ruled: &BTreeSet<String>,
    history: Option<&History>,
    done: &str,
) -> (Vec<String>, Vec<String>) {
    let sections = task_sections(plan);
    let out_of: Vec<(usize, usize)> = sections
        .iter()
        .filter(|(t, _)| ruled.contains(*t))
        .filter_map(|(_, s)| span_of(plan, s))
        .collect();
    let words: Vec<(usize, usize)> = sections
        .values()
        .filter(|s| wording_only(s))
        .filter_map(|s| span_of(plan, s))
        .collect();
    let have = reviewed_blocks(review);
    let (mut owed, mut blocked) = (Vec::new(), Vec::new());
    let empty = json!({});
    let now_blocks = blocks(plan);
    for (key, body, at) in &now_blocks {
        let part_b = PART_B.is_match(key).unwrap_or(false);
        if inside(&out_of, *at)
            || (!part_b && inside(&words, *at))
            || (key == "preamble" && strip_archive(body).trim().is_empty())
            || decides_nothing(key, body, plan, done)
        {
            continue;
        }
        let moved = if have.contains_key(key) {
            None
        } else {
            moved_from(&have, key, body, history)
        };
        let entry = have.get(key).or(moved.as_ref()).unwrap_or(&empty);
        if text_of(entry, "sha256") != Some(block_digest(body).as_str())
            && entry.get("moved").is_none()
        {
            let earlier = earlier_text(entry, key, history);
            let was = strip_archive(earlier.as_deref().unwrap_or(""));
            let current =
                strip_archive(&lands_open_appended(earlier.as_deref().unwrap_or(""), body));
            let title = heading_text(key);
            let own = leading_task(&title);
            let forgiven = earlier.is_some()
                && (typo_only(&was, &current)
                    || own.is_some_and(|t| {
                        typo_only(
                            &repointed(&was, &current, t, &format!("{plan}{done}")),
                            &current,
                        )
                    }));
            if !forgiven {
                owed.push(key.clone());
                continue;
            }
        }
        match text_of(entry, "verdict") {
            Some("BLOCKED") => blocked.push(key.clone()),
            Some("CLEAR") => {}
            _ => owed.push(key.clone()),
        }
    }
    let done_blocks = if done.is_empty() {
        Vec::new()
    } else {
        blocks(done)
    };
    let archived: BTreeSet<String> = done_blocks
        .iter()
        .map(|(_, b, _)| block_digest(b))
        .collect();
    let done_text: BTreeMap<&str, &str> = done_blocks
        .iter()
        .map(|(k, b, _)| (k.as_str(), b.as_str()))
        .collect();
    let current: BTreeSet<&str> = now_blocks.iter().map(|(k, ..)| k.as_str()).collect();
    let live: BTreeSet<(String, String)> = now_blocks
        .iter()
        .chain(&done_blocks)
        .map(|(k, b, _)| (stem(k), below_heading(b)))
        .collect();
    for (key, entry) in &have {
        let sha = text_of(entry, "sha256").unwrap_or("");
        if current.contains(key.as_str())
            || key == "preamble"
            || !entry.is_object()
            || (!sha.is_empty() && archived.contains(sha))
        {
            continue;
        }
        let earlier = earlier_text(entry, key, history);
        if let Some(text) = &earlier {
            if live.contains(&(stem(key), below_heading(text))) {
                continue;
            }
            if done_text
                .get(key.as_str())
                .is_some_and(|d| typo_only(&strip_archive(text), &strip_archive(d)))
            {
                continue;
            }
        }
        owed.push(format!("{REMOVED}{key}"));
    }
    (owed, blocked)
}

/// Every task whose section carries its own current verdict.
pub(super) fn ruled_tasks(
    review: &Value,
    plan: &str,
    history: Option<&History>,
) -> BTreeSet<String> {
    task_sections(plan)
        .into_keys()
        .filter(|t| task_current(review, plan, t, history))
        .collect()
}

/// (rule, reason) when a feature owes a plan review, from the plan's bytes and the record's text.
pub(super) fn judge(
    plan: Option<&[u8]>,
    review_text: Option<&str>,
    history: Option<&History>,
    done: &str,
) -> Option<(&'static str, String)> {
    let Some(plan) = plan else {
        return Some(("plan-missing", format!("no plan.md - the plan stage is owed before its review can be (spec D5); then {HOW}")));
    };
    let Some(review_text) = review_text else {
        return Some(("plan-review-missing", format!("no {RECORD} - {HOW}")));
    };
    let Ok(mut review) = serde_json::from_str::<Value>(review_text) else {
        return Some((
            "plan-review-missing",
            format!("{RECORD} is not JSON - {HOW}"),
        ));
    };
    let text = String::from_utf8_lossy(plan).into_owned();
    if !review.get("blocks").is_some_and(Value::is_object)
        && text_of(&review, "plan_text").is_none()
        && text_of(&review, "plan_sha256") == Some(digest(plan).as_str())
    {
        let verdict = review.get("verdict").cloned().unwrap_or(Value::Null);
        let whole: Map<String, Value> = blocks(&text)
            .into_iter()
            .map(|(k, b, _)| (k, json!({"sha256": block_digest(&b), "verdict": verdict})))
            .collect();
        review["blocks"] = Value::Object(whole);
    }
    let ruled = ruled_tasks(&review, &text, history);
    let (owed_keys, blocked) = block_status(&review, &text, &ruled, history, done);
    if !owed_keys.is_empty() {
        let shown: Vec<String> = owed_keys
            .iter()
            .take(5)
            .map(|k| k.chars().take(60).collect())
            .collect();
        let more = if owed_keys.len() > 5 {
            format!(" and {} more", owed_keys.len() - 5)
        } else {
            String::new()
        };
        return Some(("plan-review-stale", format!("{} block(s) of plan.md changed since their review by more than a typo (feature 375 FR-043): {}{more} - `make plan-delta F=<n>` builds the review of those blocks alone", owed_keys.len(), shown.join(", "))));
    }
    let whole_not_clear = !matches!(review.get("verdict"), None | Some(Value::Null))
        && text_of(&review, "verdict") != Some("CLEAR")
        && !review.get("blocks").is_some_and(Value::is_object);
    if !blocked.is_empty() || whole_not_clear {
        let rows = review
            .get("decisions")
            .and_then(Value::as_array)
            .cloned()
            .unwrap_or_default();
        let narrowing: Vec<String> = rows
            .iter()
            .filter(|d| text_of(d, "ruling") == Some("NOT LEGITIMATE"))
            .map(|d| text_of(d, "id").unwrap_or("?").to_owned())
            .collect();
        let named = if narrowing.is_empty() {
            "no ruling named".to_owned()
        } else {
            narrowing.join(", ")
        };
        return Some(("plan-review-blocked", format!("the plan review is BLOCKED ({named} ruled NOT LEGITIMATE) - withdraw or overrule the decision in plan.md, then {HOW}")));
    }
    None
}

/// What this feature owes, read from its directory.
pub(super) fn owed(spec_dir: &Path) -> Option<(&'static str, String)> {
    let plan_path = spec_dir.join("plan.md");
    let plan = std::fs::read(&plan_path).ok();
    let review = std::fs::read_to_string(spec_dir.join(RECORD)).ok();
    let done = std::fs::read_to_string(spec_dir.join("plan-done.md")).unwrap_or_default();
    judge(
        plan.as_deref(),
        review.as_deref(),
        Some(&History::new(&plan_path, "HEAD")),
        &done,
    )
}

/// Every block of the section carries a CLEAR verdict at its digest, or at a text it differs from by a typo only (405 T81, D57).
pub(super) fn section_clear(review: &Value, section: &str, history: Option<&History>) -> bool {
    let have = reviewed_blocks(review);
    let empty = json!({});
    blocks(section)
        .iter()
        .filter(|(k, ..)| k != "preamble")
        .all(|(k, b, _)| {
            let entry = have.get(k).unwrap_or(&empty);
            text_of(entry, "verdict") == Some("CLEAR")
                && (text_of(entry, "sha256") == Some(block_digest(b).as_str())
                    || earlier_text(entry, k, history)
                        .is_some_and(|e| typo_only(&strip_archive(&e), &strip_archive(b))))
        })
}

#[cfg(test)]
mod tests;
