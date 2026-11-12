//! The records `make tool-yield` counts (feature 406 T04; feature 449 T120, from `tool_yield.py`): the guard log, every clone's usage
//! and event logs, the review ledger, the round arbiter's rulings and the bypass log, each read as the Python read it - a line that is
//! not JSON skipped, a file that cannot be read skipped where the Python skipped it, and a bypass record that is no object the
//! Python's raise. The guard log and the clones are walked in the directory's own order, as `pathlib`'s and `glob`'s walks are: a time
//! `utc` cannot read is 0, which restarts a tool's first use (`Tally::use_at`), so the order is the Python's.

use std::collections::{BTreeSet, HashMap, HashSet};
use std::path::{Path, PathBuf};
use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_gate_core::measure::tool_inventory::{ending, read_text};
use l7r_guard::shared::py_text::{split, strip};
use l7r_guard::shared::speckit::splitlines;
use serde_json::{Map, Value};

use super::super::events::{or_s, py_str, re, truthy, ts, Raised};
use super::{entry, guard_kind, Tools, DAY};

type Row = Map<String, Value>;

/// The guards' interventions and likely misfires by the event a firing logged.
const GUARD_HIT: [&str; 6] = [
    "blocked",
    "refused",
    "rewrote",
    "reminded",
    "warned",
    "blocked-cadence",
];
const GUARD_MISS: [&str; 1] = ["escaped"];

/// A pass with a finding: a verdict word, a bare "findings" (not "0 findings"), or a count above 0 of a finding kind (measured
/// 2026-10-19 on the ledger: "findings" is the commonest verdict; "TRUTH 1", "1 FIX, 1 NOTE", "1 VOCABULARY" its counted forms).
static FINDING: LazyLock<Regex> = LazyLock::new(|| {
    re(concat!(
        r"(?i)BLOCK|CHANGES|DRIFT|MISLABEL|NEEDS|TOUCHES|change-route|process-fault|FAIL|CONTRADICT|NOT-FOUND|DIFFERS",
        r"|(?<![0-9] )\bfindings\b|\b[1-9]\d* (?:FIX|VOCABULARY|HISTORY|SESSION|DRIFTED|MISLABELED|findings?|unfootnoted)",
        r"|\b(?:TRUTH|COVERAGE|LINKS) [1-9]",
    ))
});
static DATE: LazyLock<Regex> = LazyLock::new(|| re(r"^\d{4}-\d\d-\d\d"));

/// Seconds since the epoch of an ISO time (`...Z` or with an offset); 0 where it is unreadable (`utc`).
#[must_use]
pub fn utc(text: &str) -> f64 {
    ts(text).unwrap_or(0.0)
}

fn objects(text: &str) -> Vec<Row> {
    splitlines(text)
        .into_iter()
        .filter_map(|l| match serde_json::from_str(l) {
            Ok(Value::Object(m)) => Some(m),
            _ => None,
        })
        .collect()
}

/// A JSONL file's objects, none where it cannot be read (`jsonl`).
#[must_use]
pub fn jsonl(path: &Path) -> Vec<Row> {
    std::fs::read(path).map_or_else(|_| Vec::new(), |b| objects(&String::from_utf8_lossy(&b)))
}

/// Every guard-log firing, in the directory's order (`guard_rows`).
#[must_use]
pub fn guard_rows(guard_log: &Path) -> Vec<Row> {
    let mut out = Vec::new();
    for p in ending(guard_log, ".json") {
        let Ok(bytes) = std::fs::read(&p) else {
            continue;
        };
        if let Ok(Value::Object(m)) = serde_json::from_str(&String::from_utf8_lossy(&bytes)) {
            out.push(m);
        }
    }
    out
}

/// `Path.parent` of a path as pathlib reads it.
fn parent(p: &Path) -> PathBuf {
    match p.parent() {
        Some(q) if !q.as_os_str().is_empty() => q.to_path_buf(),
        Some(_) => PathBuf::from("."),
        None => p.to_path_buf(),
    }
}

/// Every clone's git directory beside the mirror's, where the event and usage logs live (`git_dirs`): `glob`'s `*` takes no dot name.
#[must_use]
pub fn git_dirs(root: &Path) -> Vec<PathBuf> {
    let up = parent(root);
    let base = if up.file_name().is_some_and(|n| n == ".clones") {
        parent(&up)
    } else {
        root.to_path_buf()
    };
    let mut dirs = vec![base.join(".git")];
    for e in std::fs::read_dir(base.join(".clones"))
        .into_iter()
        .flatten()
        .flatten()
    {
        if !e.file_name().to_string_lossy().starts_with('.') && e.path().is_dir() {
            dirs.push(e.path().join(".git"));
        }
    }
    dirs.retain(|d| d.is_dir());
    dirs
}

/// (date, check, verdict, class and missed cells, acted on) of the ledger's measured table.
///
/// # Errors
///
/// The ledger is not UTF-8 or cannot be read.
pub fn ledger_rows(root: &Path) -> Result<Vec<[String; 5]>, Raised> {
    let path = root.join("dev/review-ledger.md");
    let text = if path.is_file() {
        read_text(&path)?
    } else {
        String::new()
    };
    let Some(start) = text.find("| date | check | subject | verdict |") else {
        return Ok(Vec::new());
    };
    let mut out = Vec::new();
    for line in splitlines(&text[start..]).into_iter().skip(2) {
        let cells: Vec<&str> = strip(line)
            .trim_matches('|')
            .split('|')
            .map(strip)
            .collect();
        if cells.len() >= 8 && DATE.is_match(cells[0]).unwrap_or(false) {
            out.push([
                cells[0].to_owned(),
                cells[1].to_owned(),
                cells[3].to_owned(),
                format!("{} {}", cells[5], cells[6]),
                cells[7].to_owned(),
            ]);
        }
    }
    Ok(out)
}

pub fn tally_guards(t: &mut Tools, rows: &[Row]) {
    for row in rows {
        let g = py_or(row.get("guard"), "?");
        let when = utc(&or_s(row, "utc"));
        let event = or_s(row, "event");
        let tool = entry(t, "guard", &g);
        tool.use_at(when);
        tool.hit(when, GUARD_HIT.contains(&event.as_str()));
        tool.miss(when, GUARD_MISS.contains(&event.as_str()));
    }
}

/// `str(value or default)`.
fn py_or(value: Option<&Value>, default: &str) -> String {
    value
        .filter(|v| truthy(v))
        .map_or_else(|| default.to_owned(), py_str)
}

fn is(row: &Row, key: &str, text: &str) -> bool {
    row.get(key).and_then(Value::as_str) == Some(text)
}

/// The usage log's runs; returns when it began (the target counts before it come from the event logs).
pub fn tally_usage(t: &mut Tools, rows: &[Row]) -> f64 {
    let mut began = 0.0f64;
    for row in rows {
        let when = utc(&or_s(row, "utc"));
        began = if began == 0.0 { when } else { began.min(when) };
        let kind = py_or(row.get("kind"), "step");
        let name = row.get("tool").map_or_else(|| "None".to_owned(), py_str);
        let tool = entry(t, guard_kind(&kind), &name);
        tool.use_at(when);
        tool.hit(
            when,
            ["refused", "changed", "failed"]
                .iter()
                .any(|o| is(row, "outcome", o)),
        );
    }
    began
}

/// Targets: runs before the usage log began, and every session run's outcome; reviews: dispatches.
pub fn tally_events(t: &mut Tools, rows: &[Row], usage_began: f64) {
    // `pre` is a dict: a repeated id keeps its first place and takes the later value
    let mut pre: Vec<(String, (String, f64))> = Vec::new();
    let mut at: HashMap<String, usize> = HashMap::new();
    let mut post: HashSet<String> = HashSet::new();
    let mut failed: HashSet<String> = HashSet::new();
    for row in rows {
        let when = utc(&or_s(row, "t"));
        let id = || row.get("id").map_or_else(|| "None".to_owned(), py_str);
        if row.get("make").is_some_and(truthy) {
            if is(row, "ev", "PreToolUse") {
                let value = (py_str(&row["make"]), when);
                if let Some(i) = at.get(&id()) {
                    pre[*i].1 = value;
                } else {
                    at.insert(id(), pre.len());
                    pre.push((id(), value));
                }
            } else if is(row, "ev", "PostToolUse") {
                post.insert(id());
            } else if is(row, "ev", "PostToolUseFailure") {
                failed.insert(id());
            }
        } else if is(row, "ev", "SubagentStart") && row.get("agent").is_some_and(truthy) {
            entry(t, "review", &py_str(&row["agent"])).use_at(when);
        }
    }
    for (tid, (name, when)) in &pre {
        let tool = entry(t, "target", name);
        if usage_began == 0.0 || *when < usage_began {
            tool.use_at(*when);
        }
        if failed.contains(tid) || !post.contains(tid) {
            tool.hit(*when, true);
        }
    }
    if usage_began != 0.0 {
        // a run the usage log counts that no session's event matches has no outcome record
        let mut seen: HashMap<&str, usize> = HashMap::new();
        for (_, (name, when)) in &pre {
            if *when >= usage_began {
                *seen.entry(name.as_str()).or_default() += 1;
            }
        }
        for ((kind, name), tool) in t.iter_mut() {
            if kind == "target" {
                let after = tool.uses.iter().filter(|u| **u >= usage_began).count();
                tool.unseen = after.saturating_sub(seen.get(name.as_str()).copied().unwrap_or(0));
            }
        }
    }
}

/// Reviews' findings and misfires; returns the checks the ledger holds rows for.
pub fn tally_ledger(t: &mut Tools, rows: &[[String; 5]]) -> BTreeSet<String> {
    let mut held = BTreeSet::new();
    for [date, check, verdict, missed, acted] in rows {
        let tool = entry(t, "review", check);
        held.insert(check.clone());
        let when = utc(&format!("{date}T00:00:00Z"));
        if !tool.uses.is_empty() && when < tool.first - DAY {
            continue; // before its dispatches are recorded: findings and uses cover the same span
        }
        if tool.uses.is_empty() {
            tool.first = if tool.first == 0.0 {
                when
            } else {
                tool.first.min(when)
            };
        }
        tool.hit(when, FINDING.is_match(verdict).unwrap_or(false));
        tool.miss(
            when,
            acted.to_lowercase().contains("declined") || missed.contains("MISSED-BY-REVIEWER"),
        );
    }
    held
}

/// The round arbiter's outcomes, from every feature's `arbiter.jsonl` (it keeps no ledger rows): a ruling that changed the route,
/// found a process fault or named a tooling fix is its intervention. Returns whether any ruling was read.
pub fn tally_arbiter(t: &mut Tools, root: &Path) -> bool {
    let tool = entry(t, "review", "round-arbiter");
    let mut read = false;
    for e in std::fs::read_dir(root.join("specs"))
        .into_iter()
        .flatten()
        .flatten()
    {
        for row in jsonl(&e.path().join("arbiter.jsonl")) {
            if !row.get("ruling").is_some_and(truthy) {
                continue;
            }
            read = true;
            let when = utc(&or_s(&row, "utc"));
            if !tool.uses.is_empty() && when < tool.first - DAY {
                continue;
            }
            let changed = is(&row, "ruling", "change-route") || is(&row, "ruling", "process-fault");
            tool.hit(when, changed || row.get("tooling_fix").is_some_and(truthy));
        }
    }
    read
}

/// A target's rule escaped through its bypass route (the bypass log), counted only from when its use record begins.
///
/// # Errors
///
/// A bypass record that is no object: the Python's `AttributeError`.
pub fn tally_bypass(t: &mut Tools, root: &Path) -> Result<(), Raised> {
    for e in std::fs::read_dir(root.join("dev/bypass-log"))
        .into_iter()
        .flatten()
        .flatten()
    {
        for p in ending(&e.path(), ".json") {
            let Ok(text) = read_text(&p) else {
                continue;
            };
            let row = match serde_json::from_str(&text) {
                Ok(Value::Object(m)) => m,
                Ok(_) => return Err("AttributeError: a bypass record that is no object".to_owned()),
                Err(_) => continue,
            };
            let target = or_s(&row, "target");
            let Some(name) = split(&target).first().map(|s| (*s).to_owned()) else {
                continue;
            };
            let when = utc(&or_s(&row, "utc"));
            if let Some(tool) = t.get_mut(&("target".to_owned(), name)) {
                if tool.first != 0.0 && when >= tool.first {
                    tool.miss(when, true);
                }
            }
        }
    }
    Ok(())
}

#[cfg(test)]
mod tests;
