//! What one review run COST, read off its transcript - the ledger's cost cells (feature 294, FR-010; `review_cost.py`, ported by feature
//! 449 T83 from the copy `checks::passes` held, which this replaces).
//!
//! WHY (feature 294, GM 2026-10-01: the review's "time and tokens"; spec US7: the ledger measures every check by itself). A finished
//! agent's transcript (`<project>/<session>/subagents/agent-<id>.jsonl`) carries every model call's usage and every line's timestamp;
//! this sums them, so a ledger row's cost is copied from a measurement, never typed. A streamed reply is written as several lines
//! carrying the SAME call's usage, the last with the whole output count, so each call is counted once - its last line - by its
//! `requestId` (its message id where a line has none).
//!
//! What the Python raised, this answers as an `Err` (a line that is JSON but no object, a timestamp `fromisoformat` refuses, a token count
//! `int()` refuses, naive and aware times compared): `review-cost` fails on it as the Python's traceback did, and the pass log skips it.

use std::collections::BTreeMap;
use std::path::{Path, PathBuf};

use serde_json::Value;

use crate::shared::checks::falsy;
use crate::shared::iso;
use crate::shared::py_text::strip;

/// A JSON line's `message`, where it is an object.
fn message(d: &Value) -> Option<&serde_json::Map<String, Value>> {
    d.get("message").and_then(Value::as_object)
}

/// A user record whose content is the agent's instructions - a string, or text parts only - not a tool result (`_is_prompt`).
fn is_prompt(line: &str) -> bool {
    let Ok(d) = serde_json::from_str::<Value>(line) else {
        return false;
    };
    let Some(msg) = message(&d) else {
        return false;
    };
    if msg.get("role").and_then(Value::as_str) != Some("user") {
        return false;
    }
    match msg.get("content") {
        Some(Value::String(_)) => true,
        Some(Value::Array(parts)) => {
            !parts.is_empty()
                && parts
                    .iter()
                    .all(|p| p.get("type").and_then(Value::as_str) == Some("text"))
        }
        _ => false,
    }
}

/// The transcript split at each prompt after its first - one segment per RETURN (feature 371, plan review 2): an agent resumed after it
/// returned is given a new prompt, and each return is its own pass with its own cost.
#[must_use]
pub fn segments(lines: &[&str]) -> Vec<Vec<String>> {
    let mut out: Vec<Vec<String>> = vec![Vec::new()];
    let mut seen_prompt = false;
    for line in lines {
        if is_prompt(line) {
            if seen_prompt && out.last().is_some_and(|p| !p.is_empty()) {
                out.push(Vec::new());
            }
            seen_prompt = true;
        }
        if let Some(part) = out.last_mut() {
            part.push((*line).to_owned());
        }
    }
    out
}

/// What a transcript's calls summed to (`cost`'s dict).
#[derive(Debug, Default, Clone, Copy, PartialEq, Eq)]
pub struct Cost {
    pub wall_s: i64,
    pub input: i64,
    pub cache_read: i64,
    pub cache_write: i64,
    pub output: i64,
    pub calls: i64,
}

/// `str(value)` of a JSON scalar, as the Python hands a timestamp or a key to the next step.
fn py_str(value: &Value) -> String {
    match value {
        Value::String(s) => s.clone(),
        Value::Bool(true) => "True".to_owned(),
        other => other.to_string(),
    }
}

/// `int(value or 0)`: a falsy value is 0, a float is cut toward zero, a string read as `int()` reads one; anything else is the raise.
fn py_int(value: Option<&Value>) -> Result<i64, String> {
    if falsy(value) {
        return Ok(0);
    }
    match value {
        Some(Value::Bool(_)) => Ok(1),
        #[expect(
            clippy::cast_possible_truncation,
            reason = "int() of a float cuts it toward zero, as this does"
        )]
        Some(Value::Number(n)) => Ok(n
            .as_i64()
            .unwrap_or_else(|| n.as_f64().unwrap_or_default().trunc() as i64)),
        Some(Value::String(s)) => int_text(s)
            .ok_or_else(|| format!("ValueError: invalid literal for int() with base 10: {s:?}")),
        _ => Err("TypeError: int() argument must be a string or a number".to_owned()),
    }
}

/// `int(text)`: Python's whitespace around an optional sign and digits, an underscore allowed between two digits.
pub(crate) fn int_text(text: &str) -> Option<i64> {
    let t = strip(text);
    let (sign, body) = match t.as_bytes().first() {
        Some(b'-') => (-1, &t[1..]),
        Some(b'+') => (1, &t[1..]),
        _ => (1, t),
    };
    let ok = !body.is_empty()
        && body
            .split('_')
            .all(|g| !g.is_empty() && g.bytes().all(|b| b.is_ascii_digit()));
    ok.then(|| body.replace('_', "").parse::<i64>().ok())
        .flatten()
        .map(|n| sign * n)
}

/// `round(micros / 1e6)`: to the nearest second, a tie to the even one, as Python rounds `timedelta.total_seconds()`.
fn round_seconds(micros: i64) -> i64 {
    let (whole, part) = (micros.div_euclid(1_000_000), micros.rem_euclid(1_000_000));
    if part > 500_000 || (part == 500_000 && whole % 2 != 0) {
        whole + 1
    } else {
        whole
    }
}

/// The calls and the wall time summed over a transcript's lines (`cost`).
///
/// # Errors
///
/// Where the Python raised: a line that is JSON but no object, a timestamp `fromisoformat` refuses, a token count `int()` refuses, or
/// naive and aware times compared. The text says which.
pub fn cost(lines: &[String]) -> Result<Cost, String> {
    let mut last: BTreeMap<String, Value> = BTreeMap::new();
    let mut stamps: Vec<(i64, bool)> = Vec::new();
    for line in lines {
        let Ok(d) = serde_json::from_str::<Value>(line) else {
            continue;
        };
        if !d.is_object() {
            return Err(format!(
                "AttributeError: a transcript line is no object: {line}"
            ));
        }
        if !falsy(d.get("timestamp")) {
            let text = d.get("timestamp").map(py_str).unwrap_or_default();
            let (at, zone) = iso::moment(&text.replace('Z', "+00:00"))
                .ok_or_else(|| format!("ValueError: Invalid isoformat string: {text:?}"))?;
            stamps.push((at - zone.unwrap_or(0), zone.is_some()));
        }
        let msg = message(&d);
        let usage = msg.and_then(|m| m.get("usage")).filter(|u| u.is_object());
        let id = if falsy(d.get("requestId")) {
            msg.and_then(|m| m.get("id"))
        } else {
            d.get("requestId")
        };
        let key = id
            .filter(|v| !falsy(Some(v)))
            .map(py_str)
            .unwrap_or_default();
        if let Some(u) = usage.filter(|_| !key.is_empty()) {
            // a streamed call's lines repeat its usage, the last line's output count the whole
            last.insert(key, u.clone());
        }
    }
    let mut total = Cost::default();
    for u in last.values() {
        let (read, write) = (
            py_int(u.get("cache_read_input_tokens"))?,
            py_int(u.get("cache_creation_input_tokens"))?,
        );
        total.calls += 1;
        total.input += py_int(u.get("input_tokens"))? + read + write;
        total.cache_read += read;
        total.cache_write += write;
        total.output += py_int(u.get("output_tokens"))?;
    }
    if stamps.len() >= 2 {
        if stamps.iter().any(|s| s.1) && stamps.iter().any(|s| !s.1) {
            return Err(
                "TypeError: can't compare offset-naive and offset-aware datetimes".to_owned(),
            );
        }
        let (lo, hi) = stamps.iter().fold((i64::MAX, i64::MIN), |(lo, hi), s| {
            (lo.min(s.0), hi.max(s.0))
        });
        total.wall_s = round_seconds(hi - lo);
    }
    Ok(total)
}

/// The ledger's two cost cells, `wall s | Nk in (Mk cached) / P.Pk out` (`cells`).
#[must_use]
pub fn cells(c: &Cost) -> String {
    #[expect(
        clippy::cast_precision_loss,
        reason = "a transcript's token counts are far below 2^52, where Python's int / int is the same division"
    )]
    let (input, cached, output) = (c.input as f64, c.cache_read as f64, c.output as f64);
    format!(
        "{} s | {:.0}k in ({:.0}k cached) / {:.1}k out",
        c.wall_s,
        input / 1000.0,
        cached / 1000.0,
        output / 1000.0
    )
}

/// `os.stat(path).st_mtime` as `CPython` makes the float: the seconds plus the nanoseconds times 1e-9, so two times it cannot tell apart
/// tie here as they tied there.
#[must_use]
pub fn py_mtime(meta: &std::fs::Metadata) -> f64 {
    use std::os::unix::fs::MetadataExt as _;
    #[expect(
        clippy::cast_precision_loss,
        reason = "the very float CPython computes from the same two numbers"
    )]
    let at = meta.mtime() as f64 + meta.mtime_nsec() as f64 * 1e-9;
    at
}

/// Every `<root>/*/*/subagents/<name>` entry whose name `keep` takes, in the order the directories list them (`Path.glob`'s order),
/// with its modification time.
#[must_use]
pub fn subagent_files(root: &Path, keep: &dyn Fn(&str) -> bool) -> Vec<(PathBuf, f64)> {
    let mut out = Vec::new();
    let list = |dir: &Path| -> Vec<PathBuf> {
        std::fs::read_dir(dir)
            .into_iter()
            .flatten()
            .flatten()
            .map(|e| e.path())
            .collect()
    };
    for project in list(root) {
        for session in list(&project) {
            for file in list(&session.join("subagents")) {
                let name = file.file_name().unwrap_or_default().to_string_lossy();
                if !keep(&name) {
                    continue;
                }
                if let Ok(meta) = std::fs::metadata(&file) {
                    out.push((file, py_mtime(&meta)));
                }
            }
        }
    }
    out
}

/// The newest transcript of agent `agent` under `root`, or none (`transcript`): sorted by time, the last of a tie the last listed.
#[must_use]
pub fn transcript(agent: &str, root: &Path) -> Option<PathBuf> {
    let name = format!("agent-{agent}.jsonl");
    let mut hits = subagent_files(root, &|n| n == name);
    hits.sort_by(|a, b| a.1.total_cmp(&b.1));
    hits.pop().map(|(p, _)| p)
}

/// The latest return's cost cells of `agent` under `root` (`review_cost.py --last`), what `make append AGENT=` closes a row with.
///
/// # Errors
///
/// Where the agent has no transcript, the transcript cannot be read, or its cost raises (`cost`).
pub fn last_cells(agent: &str, root: &Path) -> Result<String, String> {
    let path = transcript(agent, root).ok_or_else(|| {
        format!(
            "_review_cost: no transcript for agent {agent} under {}",
            root.display()
        )
    })?;
    let parts = read_segments(&path)?;
    cost(parts.last().map_or(&[][..], Vec::as_slice)).map(|c| cells(&c))
}

/// A transcript read and split into its returns, as `path.read_text(encoding="utf-8").splitlines()` reads it.
///
/// # Errors
///
/// Where the file cannot be read or is not UTF-8 (the Python's raise).
pub fn read_segments(path: &Path) -> Result<Vec<Vec<String>>, String> {
    let text = std::fs::read_to_string(path).map_err(|e| format!("{}: {e}", path.display()))?;
    Ok(segments(&crate::shared::checks::reply::py_lines(&text)))
}

#[cfg(test)]
mod tests;
