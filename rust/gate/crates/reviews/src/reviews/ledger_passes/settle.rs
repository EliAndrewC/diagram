//! The logged passes, read, costed from their transcripts and kept (`load_passes`, `settled`, `distinct`, `unanswered`).

use std::collections::{BTreeMap, HashSet};
use std::path::{Path, PathBuf};

use l7r_guard::shared::checks::falsy;
use l7r_guard::shared::checks::reply::{py_lines, read_lossy};
use l7r_guard::shared::ledger::cost::{cells, cost, py_mtime, segments, subagent_files};
use l7r_guard::shared::ledger::{cell, measured_rows, COLUMNS};
use serde_json::{json, Map, Value};

use super::{field, norm, py_path, required, text, Pass};
use crate::record::bundle::py_str;

/// Feature 383 (the GM 2026-10-12: "we probably don't need to search the entire session transcript ... if we are keeping track of how
/// far back it is that our most recent search was for"): a pass's cells, once costed, are kept here with its transcript's path, size and
/// mtime - a finished transcript never changes, and a resumed agent's appends change both - so a run where every pass is already costed
/// reads no transcript, and the transcripts are listed once for the passes that are new.
pub const SETTLED: &str = "l7r-cache/ledger-settled.json";

/// The logged passes, oldest first; a line that is not a pass is skipped (`load_passes`).
///
/// # Errors
///
/// Where the log is not UTF-8 (the Python's raise).
pub fn load_passes(path: &Path) -> Result<Vec<Pass>, String> {
    if !path.is_file() {
        return Ok(Vec::new());
    }
    let body = std::fs::read_to_string(path).map_err(|e| format!("{}: {e}", path.display()))?;
    Ok(py_lines(&body)
        .into_iter()
        .filter_map(|line| serde_json::from_str::<Value>(line).ok())
        .filter_map(|rec| match rec {
            Value::Object(m) if !falsy(m.get("check")) && !falsy(m.get("wall")) => Some(
                m.into_iter()
                    .map(|(k, v)| (k, Value::String(py_str(&v))))
                    .collect(),
            ),
            _ => None,
        })
        .collect())
}

/// `[st_size, st_mtime]` of a path, `[]` where it cannot be read (`_stat`).
fn stat(path: &Path) -> Vec<Value> {
    std::fs::metadata(path).map_or_else(
        |_| Vec::new(),
        |m| vec![json!(m.len()), json!(py_mtime(&m))],
    )
}

/// `stat == kept`, as Python compares two lists of numbers: element by element, an int equal to the float of its value.
fn same_stat(stat: &[Value], kept: Option<&Value>) -> bool {
    let number = |v: &Value| match v {
        Value::Bool(b) => Some(f64::from(u8::from(*b))),
        other => other.as_f64(),
    };
    kept.and_then(Value::as_array).is_some_and(|k| {
        k.len() == stat.len()
            && k.iter()
                .zip(stat)
                .all(|(a, b)| number(a).is_some() && number(a) == number(b))
    })
}

/// The newest transcript of each agent, from ONE listing of every subagent transcript made on the first lookup (a glob per pass was most
/// of this check's time): a later transcript replaces an earlier only when strictly newer, as `_Transcripts` kept the first of a tie.
struct Transcripts<'a> {
    root: &'a Path,
    index: Option<BTreeMap<String, (f64, PathBuf)>>,
}

impl Transcripts<'_> {
    fn find(&mut self, agent: &str) -> Option<PathBuf> {
        let root = self.root;
        let index = self.index.get_or_insert_with(|| {
            let mut found: BTreeMap<String, (f64, PathBuf)> = BTreeMap::new();
            #[expect(
                clippy::case_sensitive_file_extension_comparisons,
                reason = "fnmatch on Linux is case-sensitive, as the Python's glob of `agent-*.jsonl` was"
            )]
            let named = |n: &str| n.len() >= 12 && n.starts_with("agent-") && n.ends_with(".jsonl");
            for (path, at) in subagent_files(root, &named) {
                let name = path
                    .file_name()
                    .unwrap_or_default()
                    .to_string_lossy()
                    .into_owned();
                let aid = name["agent-".len()..name.len() - ".jsonl".len()].to_owned();
                if found.get(&aid).is_none_or(|(was, _)| at > *was) {
                    found.insert(aid, (at, path));
                }
            }
            found
        });
        index.get(agent).map(|(_, p)| p.clone())
    }
}

/// The kept costs, `{}` where the file is missing, unreadable, not JSON or not an object.
fn read_kept(kept_file: Option<&Path>) -> Map<String, Value> {
    kept_file
        .and_then(|f| std::fs::read_to_string(f).ok())
        .and_then(|t| serde_json::from_str::<Value>(&t).ok())
        .and_then(|v| match v {
            Value::Object(m) => Some(m),
            _ => None,
        })
        .unwrap_or_default()
}

/// The kept costs written whole by a rename, `json.dumps(kept)`; a failure costs the next run its speed, never its answer.
fn write_kept(kept_file: &Path, kept: Map<String, Value>) {
    let tmp = kept_file.with_extension("tmp");
    let text = l7r_guard::shared::pyjson::dumps(&Value::Object(kept), None, true);
    let _ = kept_file
        .parent()
        .map_or(Ok(()), std::fs::create_dir_all)
        .and_then(|()| std::fs::write(&tmp, text))
        .and_then(|()| std::fs::rename(&tmp, kept_file));
}

/// `{**p, **cells}`: the pass with the cells laid over it, a new key after the pass's own.
fn merged(p: &Pass, cells: &Map<String, Value>) -> Pass {
    let mut out = p.clone();
    for (k, v) in cells {
        out.insert(k.clone(), v.clone());
    }
    out
}

/// Each pass with its cells recomputed from its agent's FINISHED transcript, the segment it logged (its return) - the cells `make
/// review-cost` prints (`settled`). The hook logs at `SubagentStop`, before the agent's last call reaches the disk (measured 2026-10-10: a
/// 13 s check logged as 4 s), so its own cells are provisional; they stand only where the transcript is gone. A pass already costed is
/// served from `kept_file` while its transcript is unchanged (feature 383).
///
/// # Errors
///
/// Where the Python raised: a kept entry whose path is no string or whose cells are no object, a transcript that cannot be read, or a
/// cost that raises.
pub fn settled(
    passes: &[Pass],
    root: &Path,
    kept_file: Option<&Path>,
) -> Result<Vec<Pass>, String> {
    let mut kept = read_kept(kept_file);
    let (mut index, mut added, mut out) = (Transcripts { root, index: None }, false, Vec::new());
    for p in passes {
        let key = format!(
            "{}#{}#{}#{}",
            text(p, "agent"),
            text(p, "segment"),
            text(p, "check"),
            text(p, "wall")
        );
        let hit = if text(p, "agent").is_empty() {
            None
        } else {
            kept.get(&key)
        };
        if let Some(Value::Object(h)) = hit {
            let path = match h.get("path") {
                None => "",
                Some(Value::String(s)) => s.as_str(),
                Some(_) => return Err("TypeError: a kept path is no string".to_owned()),
            };
            // a transcript since deleted (Claude Code removes them after 30 days; 2026-11-10 saw 2026-10-10's go, 70 answered passes
            // reading as owed again and refusing every landing) keeps the cells it was costed at: it can change no more
            let now = stat(&py_path(path));
            if now.is_empty() || same_stat(&now, h.get("stat")) {
                out.push(match h.get("cells") {
                    Some(Value::Object(c)) => merged(p, c),
                    c if falsy(c) => p.clone(),
                    _ => return Err("TypeError: kept cells are no mapping".to_owned()),
                });
                continue;
            }
        }
        let path = if text(p, "agent").is_empty() {
            None
        } else {
            index.find(text(p, "agent"))
        };
        let parts = match &path {
            Some(t) => {
                let body = read_lossy(t).ok_or_else(|| format!("{}: unreadable", t.display()))?;
                segments(&py_lines(&body))
            }
            None => Vec::new(),
        };
        // a line logged before the segment was (2026-10-10) is settled only where its agent returned once - it can be no other
        let segment = text(p, "segment");
        let n = if !segment.is_empty() && segment.bytes().all(|b| b.is_ascii_digit()) {
            segment.parse().unwrap_or(usize::MAX)
        } else if parts.len() == 1 {
            0
        } else {
            parts.len()
        };
        let mut new_cells = Map::new();
        if let Some(part) = parts.get(n) {
            let both = cells(&cost(part)?);
            let (wall, tokens) = both.split_once(" | ").unwrap_or((&both, ""));
            // the logged cells are kept beside: a row written from them before this recompute (every row of 2026-10-10's sessions)
            // still answers its pass - without them 131 answered passes read as owed again
            new_cells.insert("wall".to_owned(), json!(wall));
            new_cells.insert("tokens".to_owned(), json!(tokens));
            new_cells.insert(
                "logged".to_owned(),
                json!(format!("{} | {}", text(p, "wall"), text(p, "tokens"))),
            );
        }
        if let Some(t) = &path {
            kept.insert(
                key,
                json!({"path": t.to_string_lossy(), "stat": stat(t), "cells": new_cells}),
            );
            added = true;
        }
        out.push(merged(p, &new_cells));
    }
    if let Some(f) = kept_file.filter(|_| added) {
        write_kept(f, kept);
    }
    Ok(out)
}

/// Each logged line is a pass (plan review 2: a resumed agent's every return is one); an identical repeat of an agent's line - the same
/// return seen by two events - is one (`distinct`).
#[must_use]
pub fn distinct(passes: &[Pass]) -> Vec<Pass> {
    let value_of = |p: &Pass, k: &str| p.get(k).map(ToString::to_string);
    let mut seen = HashSet::new();
    let mut out = Vec::new();
    for p in passes {
        let key = if p.contains_key("segment") {
            vec![
                value_of(p, "agent"),
                value_of(p, "check"),
                value_of(p, "segment"),
            ]
        } else {
            vec![
                value_of(p, "agent"),
                value_of(p, "check"),
                None,
                Some(norm(text(p, "wall"))),
                Some(norm(text(p, "tokens"))),
            ]
        };
        if seen.insert(key) {
            out.push(p.clone());
        }
    }
    out
}

/// The passes no measured row answers - a row of the same check carrying the pass's wall and tokens cells, or the cells it logged
/// (`unanswered`).
///
/// # Errors
///
/// Where a pass has no tokens cell (the Python's `KeyError`).
pub fn unanswered(passes: &[Pass], ledger_text: &str) -> Result<Vec<Pass>, String> {
    let keys: HashSet<(String, String, String)> = measured_rows(ledger_text)
        .into_iter()
        .filter(|(_, cells)| cells.len() == COLUMNS.len())
        .map(|(_, c)| {
            (
                norm(cell(&c, "check")),
                norm(cell(&c, "wall")),
                norm(cell(&c, "tokens")),
            )
        })
        .collect();
    let mut out = Vec::new();
    for p in passes {
        let mut cells = vec![(required(p, "wall")?, required(p, "tokens")?)];
        if let Some(pair) = field(p, "logged").and_then(|l| l.split_once(" | ")) {
            cells.push(pair);
        }
        let check = norm(required(p, "check")?);
        if !cells
            .iter()
            .any(|(w, k)| keys.contains(&(check.clone(), norm(w), norm(k))))
        {
            out.push(p.clone());
        }
    }
    Ok(out)
}

#[cfg(test)]
mod tests;
