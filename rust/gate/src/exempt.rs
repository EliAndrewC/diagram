//! The engine code the Rust port replaces, exempt from the coverage floor (feature 449 T72, from `l7r/diagram/ci/coverage_exempt.py`; feature 448, the GM 2026-11-02). The record is `dev/coverage-exempt.json`; a file not
//! in it owes 100%. An entry names the stages whose old code it is, and is stale once its file is gone or every one of those stages is accepted in Rust. An entry naming no stages is refused: the round arbiter's
//! `ask:449-T72-coverage-exempt` dropped the import-graph check that alone gave one a meaning, the engine it served being deleted.

use std::collections::BTreeSet;
use std::fmt::Write as _;
use std::path::Path;
use std::process::Command;

use serde_json::{json, Value};

use crate::codeid::{self, parsed, stated};

const RECORD: &str = "dev/coverage-exempt.json";
const BUDGETS: &str = "dev/work-budget.json";
const CURE: &str = "make coverage-exempt PRUNE=1";
const RULING: &str = "the GM, 2026-11-02: \"We can relax that for the engine code at this pooint since that's going away, so long as we maintain it for our other Python code not currently slated to be removed (tools, automated checks for hand-drawn maps, etc).\"";

fn stages_of(entry: &Value) -> Vec<&str> {
    entry["stages"]
        .as_array()
        .into_iter()
        .flatten()
        .filter_map(Value::as_str)
        .collect()
}

fn path_of(entry: &Value) -> &str {
    entry["path"].as_str().unwrap_or_default()
}

/// The record, an absent file being an empty one; an entry naming no stages fails, naming it.
fn load(root: &Path) -> Result<Value, String> {
    let path = root.join(RECORD);
    if !path.is_file() {
        return Ok(json!({"ruling": RULING, "entries": []}));
    }
    let record = parsed(&stated(std::fs::read_to_string(&path), RECORD)?, RECORD)?;
    if let Some(bad) = record["entries"]
        .as_array()
        .into_iter()
        .flatten()
        .find(|e| stages_of(e).is_empty())
    {
        return Err(format!("{RECORD}: {} names no stages; an entry says which stages' old code it is (ask:449-T72-coverage-exempt)", path_of(bad)));
    }
    Ok(record)
}

/// The stages whose Rust has landed: `accepted` in the work-budget record.
fn accepted(root: &Path) -> Result<BTreeSet<String>, String> {
    let path = root.join(BUDGETS);
    if !path.is_file() {
        return Ok(BTreeSet::new());
    }
    let record = parsed(&stated(std::fs::read_to_string(&path), BUDGETS)?, BUDGETS)?;
    Ok(record["stages"]
        .as_object()
        .into_iter()
        .flatten()
        .filter(|(_, row)| row["status"] == "accepted")
        .map(|(name, _)| name.clone())
        .collect())
}

fn stale_why(root: &Path, entry: &Value, done: &BTreeSet<String>) -> Option<String> {
    let stages = stages_of(entry);
    if !root.join(path_of(entry)).is_file() {
        return Some("the file is gone".to_owned());
    }
    stages.iter().all(|s| done.contains(*s)).then(|| {
        format!(
            "every stage it serves is accepted in Rust ({}); the thin door keeps the floor",
            stages.join(", ")
        )
    })
}

type Split = (Vec<Value>, Vec<(Value, String)>);

/// (live entries, stale entries with why).
fn split(root: &Path) -> Result<Split, String> {
    let done = accepted(root)?;
    let record = load(root)?;
    let (mut live, mut stale) = (Vec::new(), Vec::new());
    for entry in record["entries"].as_array().cloned().unwrap_or_default() {
        match stale_why(root, &entry, &done) {
            Some(why) => stale.push((entry, why)),
            None => live.push(entry),
        }
    }
    Ok((live, stale))
}

/// 3, 4, 5, 9 -> "3-5, 9".
fn ranges(lines: &[u64]) -> String {
    let mut runs: Vec<(u64, u64)> = Vec::new();
    for &n in lines {
        match runs.last_mut() {
            Some((_, end)) if n == *end + 1 => *end = n,
            _ => runs.push((n, n)),
        }
    }
    runs.iter()
        .map(|(a, b)| {
            if a == b {
                a.to_string()
            } else {
                format!("{a}-{b}")
            }
        })
        .collect::<Vec<_>>()
        .join(", ")
}

/// Each live entry's unrun lines, from coverage.py, one process with every entry in it (`ask:449-T062-py-id`); asked only when a live entry exists, and a failure is the run's failure rather than an empty report.
fn missing(root: &Path, live: &[Value], data: &str, python: &str) -> Result<Vec<Vec<u64>>, String> {
    if live.is_empty() {
        return Ok(Vec::new());
    }
    let script = codeid::script(root);
    let paths = live.iter().map(|e| root.join(path_of(e)));
    let done = stated(
        Command::new(python)
            .arg(&script)
            .arg("--missing")
            .arg(root.join(data))
            .args(paths)
            .output(),
        python,
    )?;
    let text = String::from_utf8_lossy(&done.stdout).into_owned();
    let lines: Vec<&str> = text.split('\n').take(live.len()).collect();
    if !done.status.success() || lines.len() != live.len() {
        return Err(format!(
            "{} answered no unrun lines: {}",
            script.display(),
            String::from_utf8_lossy(&done.stderr).trim()
        ));
    }
    Ok(lines
        .iter()
        .map(|l| l.split(',').filter_map(|n| n.parse().ok()).collect())
        .collect())
}

fn report(root: &Path, data: &str, python: &str) -> Result<(String, i32), String> {
    let (live, stale) = split(root)?;
    let mut out = String::new();
    let mut shown = 0;
    for (entry, unrun) in live.iter().zip(missing(root, &live, data, python)?) {
        if !unrun.is_empty() {
            shown += 1;
            let _ = writeln!(out, "coverage (information, feature 448 - slated for the Rust port): {} - unrun lines: {}", path_of(entry), ranges(&unrun));
        }
    }
    if !live.is_empty() {
        let _ = writeln!(out, "coverage: {} files slated for the Rust port are exempt from the floor ({shown} with unrun lines; {RECORD})", live.len());
    }
    for (entry, why) in &stale {
        let _ = writeln!(
            out,
            "COVERAGE: {RECORD} names {}, which is stale - {why}. Drop it: {CURE}",
            path_of(entry)
        );
    }
    Ok((out, i32::from(!stale.is_empty())))
}

fn list(root: &Path, prune: bool) -> Result<String, String> {
    let mut out = String::new();
    if prune {
        let mut record = load(root)?;
        let (live, stale) = split(root)?;
        for (entry, why) in &stale {
            let _ = writeln!(out, "coverage-exempt: dropped {} - {why}", path_of(entry));
        }
        record["entries"] = Value::Array(live);
        let mut text = Vec::new();
        let mut writer = serde_json::Serializer::with_formatter(
            &mut text,
            serde_json::ser::PrettyFormatter::with_indent(b" "),
        );
        stated(
            serde::Serialize::serialize(&record, &mut writer).map_err(std::io::Error::other),
            RECORD,
        )?;
        text.push(b'\n');
        stated(std::fs::write(root.join(RECORD), text), RECORD)?;
    }
    let (live, stale) = split(root)?;
    for entry in &live {
        let _ = writeln!(out, "{}  ({})", path_of(entry), stages_of(entry).join(", "));
    }
    for (entry, why) in &stale {
        let _ = writeln!(out, "STALE {} - {why}", path_of(entry));
    }
    let _ = writeln!(
        out,
        "coverage-exempt: {} exempt, {} stale",
        live.len(),
        stale.len()
    );
    Ok(out)
}

pub(crate) fn paths(root: &Path) -> Result<Vec<String>, String> {
    let mut found: Vec<String> = split(root)?
        .0
        .iter()
        .map(|e| path_of(e).to_owned())
        .collect();
    found.sort();
    Ok(found)
}

/// `l7r-gate coverage-exempt omit | exempt | stale | report [DATA] | list [--prune]`.
pub(crate) fn cli(args: &[String], root: &Path, python: &str) -> crate::Reply {
    let words: Vec<&str> = args.iter().map(String::as_str).collect();
    let plain = |text: String| (text, 0);
    let answer: Result<(String, i32), String> = match words.as_slice() {
        ["omit"] => paths(root).map(|p| plain(if p.is_empty() { "\n".to_owned() } else { format!("--omit={}\n", p.join(",")) })),
        ["exempt"] => paths(root).map(|p| plain(p.iter().flat_map(|x| [x.as_str(), "
"]).collect())),
        ["stale"] => split(root).map(|(_, stale)| plain(stale.iter().flat_map(|(e, why)| [path_of(e), "	", why.as_str(), "
"]).collect())),
        ["report"] => report(root, ".coverage", python),
        ["report", data] => report(root, data, python),
        ["list"] => list(root, false).map(plain),
        ["list", "--prune"] => list(root, true).map(plain),
        _ => return crate::Reply { stdout: String::new(), stderr: "usage: l7r-gate coverage-exempt omit | exempt | stale | report [DATA] | list [--prune]\n".to_owned(), code: 2 },
    };
    match answer {
        Ok((stdout, code)) => crate::Reply {
            stdout,
            stderr: String::new(),
            code,
        },
        Err(why) => crate::Reply {
            stdout: String::new(),
            stderr: format!("l7r-gate coverage-exempt: {why}\n"),
            code: 1,
        },
    }
}

#[cfg(test)]
mod tests;
