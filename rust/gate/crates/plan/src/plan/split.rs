//! `make archive-split F=<feature>` (`l7r-gate plan split`): a feature's records cut into parts a session can read (451 T537, 462 T545,
//! T555), rerunnable, in this order - a closed feature's finished plan.md sections moved to plan-done.md, plan-done.md and tasks-done.md
//! folded into parts (`archive::fold`), the plan review's closed entries cut against the plan.md that results ([`review`]), and the
//! report cut at its tables' rows (`archive::report`).
//!
//! THE REVIEW'S CUT (462 T545): the flat `plan-review.json` keeps the file's own format and its LIVE entries - every key but the three
//! maps, `blocks` of a block plan.md holds, `tasks` of a task with a section in plan.md or an open box, `block_reviews` rounds naming a
//! live block or a live task - so its writers (`plan-verdict`), its merge driver (`merge.rs`: an entry the split removed, unchanged on
//! the other side, stays removed, the base holding it), the plan gate, the push's hold at HEAD and the review-round guard read it as
//! before. Each closed task's entries - its tasks entry, the blocks its headings led, the rounds whose first task (or first block's) it
//! is - go together into JSON parts of at most `archive::BOUND` bytes, in id order, under `archive/plan-review/`, `index.json` naming
//! every task a part holds. A reader of a closed task's verdict reads `archive::review(read, task)`: `built_inside` for an archived
//! host, the ledger's late row (`in_the_record`). WHY: 451's record stood at 5,074,158 bytes, its live part a few hundred KB (observed
//! 2026-11-27, method: its blocks and rounds read against plan.md's headings); the tools read it whole every call.

use std::collections::{BTreeMap, BTreeSet};
use std::fmt::Write as _;
use std::path::Path;

use l7r_shared::speckit::archive::{self, Part, BOUND};
use serde_json::{json, Map, Value};

use super::sections::{blocks, leading_tasks, re, task_sections};
use super::status::RECORD;
use super::{fail, pretty, said, task};

/// A task's sort key: its number, then its letter; a key that is no task last.
fn order(id: &str) -> (u128, String) {
    let digits: String = id
        .chars()
        .skip(1)
        .take_while(char::is_ascii_digit)
        .collect();
    (
        digits.parse().unwrap_or(u128::MAX),
        id.get(1 + digits.len()..).unwrap_or("").to_owned(),
    )
}

/// The task a block key leads with (`### T18 Approach ...` -> T18), `-` for a block that is no task's.
fn lead(key: &str) -> String {
    leading_tasks(key.trim_start_matches('#').trim())
        .first()
        .map_or_else(|| "-".to_owned(), |t| (*t).to_owned())
}

fn names(v: &Value, field: &str) -> Vec<String> {
    v.get(field)
        .and_then(Value::as_array)
        .map(|a| {
            a.iter()
                .filter_map(Value::as_str)
                .map(str::to_owned)
                .collect()
        })
        .unwrap_or_default()
}

/// The live record and the closed entries grouped by task: (the live record, task -> its closed entries in the flat file's shape).
pub(super) fn cut_review(
    record: Map<String, Value>,
    plan: &str,
    open: &BTreeSet<String>,
) -> (Map<String, Value>, BTreeMap<String, Value>) {
    let live_blocks: BTreeSet<String> = blocks(plan).into_iter().map(|(k, _, _)| k).collect();
    let mut live_tasks: BTreeSet<String> = task_sections(plan).into_keys().collect();
    live_tasks.extend(open.iter().cloned());
    let mut groups: BTreeMap<String, Value> = BTreeMap::new();
    let mut live = Map::new();
    let mut moved: Vec<(String, &'static str, String, Value)> = Vec::new();
    for (key, value) in record {
        match (key.as_str(), value) {
            ("blocks", Value::Object(m)) => {
                let mut kept = Map::new();
                for (k, v) in m {
                    if live_blocks.contains(&k) {
                        kept.insert(k, v);
                    } else {
                        moved.push((lead(&k), "blocks", k, v));
                    }
                }
                live.insert(key, Value::Object(kept));
            }
            ("tasks", Value::Object(m)) => {
                let mut kept = Map::new();
                for (k, v) in m {
                    if live_tasks.contains(&k) {
                        kept.insert(k, v);
                    } else {
                        moved.push((k.clone(), "tasks", k, v));
                    }
                }
                live.insert(key, Value::Object(kept));
            }
            ("block_reviews", Value::Array(rows)) => {
                let mut kept = Vec::new();
                for row in rows {
                    let (bs, ts) = (names(&row, "blocks"), names(&row, "tasks"));
                    if bs.iter().any(|b| live_blocks.contains(b))
                        || ts.iter().any(|t| live_tasks.contains(t))
                    {
                        kept.push(row);
                    } else {
                        let id = ts.first().cloned().unwrap_or_else(|| {
                            bs.first().map_or_else(|| "-".to_owned(), |b| lead(b))
                        });
                        moved.push((id, "block_reviews", String::new(), row));
                    }
                }
                live.insert(key, Value::Array(kept));
            }
            (_, value) => {
                live.insert(key, value);
            }
        }
    }
    for (id, map, key, value) in moved {
        let g = groups
            .entry(id)
            .or_insert_with(|| json!({"blocks": {}, "tasks": {}, "block_reviews": []}));
        if map == "block_reviews" {
            if let Some(a) = g[map].as_array_mut() {
                a.push(value);
            }
        } else {
            g[map][key] = value;
        }
    }
    (live, groups)
}

/// The closed groups packed, in id order, into parts of at most [`BOUND`] bytes (a group larger than it alone in its part): each part
/// (its lowest task, its highest, every task it holds - its groups' and its rounds' - and its JSON text).
pub(super) fn pack(feature: &str, groups: BTreeMap<String, Value>) -> Vec<Part> {
    let mut ordered: Vec<(String, Value)> = groups.into_iter().collect();
    ordered.sort_by_key(|(id, _)| order(id));
    let mut packs: Vec<(Vec<String>, Value, usize)> = Vec::new();
    for (id, g) in ordered {
        let size = pretty(&g).len();
        let mut ids = vec![id];
        for row in g["block_reviews"].as_array().into_iter().flatten() {
            ids.extend(names(row, "tasks"));
        }
        match packs.last_mut() {
            Some(p) if p.2 + size <= BOUND => {
                p.0.extend(ids);
                for map in ["blocks", "tasks"] {
                    if let (Some(to), Some(from)) = (p.1[map].as_object_mut(), g[map].as_object()) {
                        to.extend(from.clone());
                    }
                }
                if let (Some(to), Some(from)) = (
                    p.1["block_reviews"].as_array_mut(),
                    g["block_reviews"].as_array(),
                ) {
                    to.extend(from.iter().cloned());
                }
                p.2 += size;
            }
            _ => packs.push((ids, g, size)),
        }
    }
    packs
        .into_iter()
        .map(|(ids, mut body, _)| {
            let tasks: Vec<&String> = ids.iter().filter(|i| i.as_str() != "-").collect();
            let lo = tasks.iter().min_by_key(|i| order(i)).map_or("other".to_owned(), |s| (*s).clone());
            let hi = tasks.iter().max_by_key(|i| order(i)).map_or("other".to_owned(), |s| (*s).clone());
            body["part"] = json!(format!("{feature} - plan-review.json, the closed tasks' entries {lo} to {hi}, cut by `make archive-split` (462 T545); what is where: archive/INDEX.md"));
            let mut held: Vec<String> = ids.into_iter().filter(|i| i != "-").collect();
            held.sort_by_key(|i| order(i));
            held.dedup();
            (lo, hi, held, pretty(&body))
        })
        .collect()
}

/// The open boxes of `dir`'s tasks.md.
fn open_tasks(dir: &Path) -> BTreeSet<String> {
    let text = std::fs::read_to_string(dir.join("tasks.md")).unwrap_or_default();
    re(r"(?m)^\s*- \[ \] (T\d+[a-z]?)")
        .captures_iter(&text)
        .map_while(Result::ok)
        .map(|c| c[1].to_owned())
        .collect()
}

/// Cut `dir`'s plan review: the closed entries into parts, then the flat record rewritten with the live ones; the parts written.
///
/// # Errors
/// A record that is not a JSON object, or a file that cannot be written.
pub(super) fn review(dir: &Path) -> Result<Vec<String>, String> {
    let path = dir.join(RECORD);
    let Ok(text) = std::fs::read_to_string(&path) else {
        return Ok(Vec::new());
    };
    let Ok(Value::Object(record)) = serde_json::from_str::<Value>(&text) else {
        return Err(format!("{}: not a JSON object, left whole", path.display()));
    };
    let plan = std::fs::read_to_string(dir.join("plan.md")).unwrap_or_default();
    let (live, groups) = cut_review(record, &plan, &open_tasks(dir));
    if groups.is_empty() {
        return Ok(Vec::new());
    }
    let feature = dir.file_name().unwrap_or_default().to_string_lossy();
    let written = archive::add_review(dir, pack(&feature, groups))?;
    std::fs::write(&path, pretty(&Value::Object(live)))
        .map_err(|e| format!("{}: {e}", path.display()))?;
    Ok(written)
}

/// The verb: each step in order, its counts said; the first failure is the verb's.
pub(super) fn split(dir: &Path) -> crate::Reply {
    let moved = if task::closed(dir) {
        task::archive(dir, None, true)
    } else {
        Vec::new()
    };
    let step = archive::fold(dir, true).and_then(|mut parts| {
        parts.extend(review(dir)?);
        let report = dir.join(archive::report::REPORT);
        if let Ok(text) = std::fs::read_to_string(&report) {
            parts.extend(archive::report::write(dir, &text, true)?);
        }
        Ok(parts)
    });
    match step {
        Ok(parts) => {
            let mut out = format!(
                "split: {} part(s) written under {}/archive/ (what is where: {}/{})\n",
                parts.len(),
                dir.display(),
                dir.display(),
                archive::NOTE
            );
            if !moved.is_empty() {
                let _ = writeln!(
                    out,
                    "split: {} finished section(s) of the closed feature moved from plan.md first: {}",
                    moved.len(),
                    moved.join(", ")
                );
            }
            said(out)
        }
        Err(why) => fail(format!("split: {why}\n"), 1),
    }
}

#[cfg(test)]
mod tests;
