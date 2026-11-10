//! A check's pass logged, read off its transcript (features 371, 294; from `hm_checks.log_pass` and `scripts/reviews/review_cost.py`): one line per return in `<git common dir>/check-passes.jsonl`, the ledger's
//! cost cells computed over the transcript, and the tool-usage line (`usage_log.record`) an automatic step leaves. Never raises: a hook that fails here must not take the session's tool call with it.

use std::collections::BTreeMap;
use std::path::Path;

use serde_json::{json, Value};

use super::arbiter::iso_seconds;
use super::reply::{py_lines, read_lossy};
use super::{falsy, text};
use crate::shared::log::civil;
use crate::shared::pyjson;
use crate::shared::tool::ask;

const PASS_LOG: &str = "check-passes.jsonl";
/// `ledger_lint.CHECKS`: the checks a row may name (the five map reviews and the record and plan checks the ledger also logs).
const LEDGER_CHECKS: [&str; 23] = [
    "building-review",
    "entry-drift",
    "escalation-check",
    "fix-check",
    "glyph-check",
    "impl-drift",
    "intro-check",
    "modal-depiction",
    "modal-form",
    "modal-research",
    "perf-audit",
    "quote-check",
    "record-format",
    "record-style",
    "settlement-review",
    "size-audit",
    "source-applicability",
    "source-filter",
    "source-reader",
    "spec-fidelity",
    "spec-fidelity-verify",
    "translation-check",
    "work-budget",
];

fn is_prompt(line: &str) -> bool {
    let Ok(d) = serde_json::from_str::<Value>(line) else {
        return false;
    };
    let msg = d
        .get("message")
        .filter(|m| m.is_object())
        .cloned()
        .unwrap_or_else(|| json!({}));
    if text(&msg, "role") != "user" {
        return false;
    }
    match msg.get("content") {
        Some(Value::String(_)) => true,
        Some(Value::Array(parts)) => {
            !parts.is_empty()
                && parts
                    .iter()
                    .all(|p| p.is_object() && text(p, "type") == "text")
        }
        _ => false,
    }
}

/// The transcript split at each prompt after its first - one segment per return.
fn segments(lines: &[&str]) -> Vec<Vec<String>> {
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

/// One call's counted usage: the last line a streamed call wrote carries its whole output count.
#[derive(Default, Clone, Copy)]
struct Usage {
    input: u64,
    cache_read: u64,
    cache_write: u64,
    output: u64,
}

fn usage_int(u: &Value, key: &str) -> u64 {
    u.get(key).and_then(Value::as_u64).unwrap_or(0)
}

fn one_usage(u: &Value) -> Usage {
    Usage {
        input: usage_int(u, "input_tokens")
            + usage_int(u, "cache_read_input_tokens")
            + usage_int(u, "cache_creation_input_tokens"),
        cache_read: usage_int(u, "cache_read_input_tokens"),
        cache_write: usage_int(u, "cache_creation_input_tokens"),
        output: usage_int(u, "output_tokens"),
    }
}

/// `{wall_s, input, cache_read, cache_write, output, calls}` summed over a segment; None where a line is unreadable as an object or a timestamp will not parse (the Python's uncaught raise, `log_pass` swallows it).
fn cost(lines: &[String]) -> Option<(u64, Usage)> {
    let mut last: BTreeMap<String, Usage> = BTreeMap::new();
    let mut stamps = Vec::new();
    for line in lines {
        let Ok(d) = serde_json::from_str::<Value>(line) else {
            continue;
        };
        if !d.is_object() {
            return None;
        }
        if !falsy(d.get("timestamp")) {
            stamps.push(iso_seconds(
                &super::arbiter::py_text(d.get("timestamp")?).replace('Z', "+00:00"),
            )?);
        }
        let msg = d
            .get("message")
            .filter(|m| m.is_object())
            .cloned()
            .unwrap_or_else(|| json!({}));
        let usage = msg.get("usage").filter(|u| u.is_object());
        let id = if falsy(d.get("requestId")) {
            msg.get("id")
        } else {
            d.get("requestId")
        };
        let key = id
            .filter(|v| !falsy(Some(v)))
            .map_or_else(String::new, super::arbiter::py_text);
        if let Some(u) = usage.filter(|_| !key.is_empty()) {
            last.insert(key, one_usage(u));
        }
    }
    let mut total = Usage::default();
    for u in last.values() {
        total.input += u.input;
        total.cache_read += u.cache_read;
        total.cache_write += u.cache_write;
        total.output += u.output;
    }
    let (min, max) = stamps
        .iter()
        .fold((f64::INFINITY, f64::NEG_INFINITY), |(lo, hi), t| {
            (lo.min(*t), hi.max(*t))
        });
    let wall = if stamps.len() >= 2 { max - min } else { 0.0 };
    Some((round_half_even(wall), total))
}

/// `round(wall)`: to the nearest integer, ties to even.
fn round_half_even(wall: f64) -> u64 {
    let floor = wall.floor();
    let frac = wall - floor;
    #[expect(
        clippy::cast_possible_truncation,
        clippy::cast_sign_loss,
        reason = "a wall time in seconds is small and not negative"
    )]
    let at = floor as u64;
    if frac > 0.5 || (frac == 0.5 && at % 2 == 1) {
        at + 1
    } else {
        at
    }
}

/// The ledger's two cost cells: `wall s | Nk in (Mk cached) / P.Pk out`.
fn cells(wall_s: u64, c: Usage) -> (String, String) {
    #[expect(
        clippy::cast_precision_loss,
        reason = "a transcript's token counts are far below 2^52"
    )]
    let (input, cached, output) = (c.input as f64, c.cache_read as f64, c.output as f64);
    (
        format!("{wall_s} s"),
        format!(
            "{:.0}k in ({:.0}k cached) / {:.1}k out",
            input / 1000.0,
            cached / 1000.0,
            output / 1000.0
        ),
    )
}

/// The dispatch's prompt - the transcript's first user message - as a one-line subject a ledger cell can hold.
fn first_prompt(lines: &[&str]) -> String {
    for line in lines {
        let Ok(rec) = serde_json::from_str::<Value>(line) else {
            continue;
        };
        let msg = rec
            .get("message")
            .filter(|m| m.is_object())
            .cloned()
            .unwrap_or_else(|| json!({}));
        if text(&msg, "role") != "user" {
            continue;
        }
        let content = match msg.get("content") {
            Some(Value::String(s)) => s.clone(),
            other => other
                .and_then(Value::as_array)
                .into_iter()
                .flatten()
                .filter(|p| p.is_object())
                .map(|p| p.get("text").and_then(Value::as_str).unwrap_or(""))
                .collect::<Vec<_>>()
                .join(" "),
        };
        let first = content
            .lines()
            .map(str::trim)
            .find(|l| !l.is_empty())
            .unwrap_or("");
        let flat: String = first
            .chars()
            .map(|c| {
                if c == '|' || c.is_whitespace() {
                    ' '
                } else {
                    c
                }
            })
            .collect();
        let squeezed = flat
            .split(' ')
            .filter(|p| !p.is_empty())
            .collect::<Vec<_>>()
            .join(" ");
        return squeezed
            .chars()
            .take(100)
            .collect::<String>()
            .trim()
            .to_owned();
    }
    String::new()
}

fn transcript_under(projects: &Path, agent: &str) -> Option<std::path::PathBuf> {
    let name = format!("agent-{agent}.jsonl");
    let mut hits: Vec<(std::time::SystemTime, std::path::PathBuf)> = Vec::new();
    for project in std::fs::read_dir(projects).ok()?.flatten() {
        for session in std::fs::read_dir(project.path())
            .into_iter()
            .flatten()
            .flatten()
        {
            let candidate = session.path().join("subagents").join(&name);
            if let Ok(meta) = std::fs::metadata(&candidate) {
                hits.push((meta.modified().unwrap_or(std::time::UNIX_EPOCH), candidate));
            }
        }
    }
    hits.sort_by_key(|(when, _)| *when);
    hits.pop().map(|(_, p)| p)
}

fn transcript_of(agent: &str) -> Option<std::path::PathBuf> {
    transcript_under(
        &Path::new(&std::env::var("HOME").ok()?).join(".claude/projects"),
        agent,
    )
}

/// The local date of an epoch time, as `time.strftime("%Y-%m-%d", time.localtime(at))` (this crate reads no time zone itself, so `date` answers).
fn local_date(at: f64) -> String {
    #[expect(clippy::cast_possible_truncation, reason = "an epoch time fits an i64")]
    let secs = at as i64;
    let said = ask(
        Path::new("/"),
        "date",
        &["-d", &format!("@{secs}"), "+%Y-%m-%d"],
        "",
    );
    said.out.trim().to_owned()
}

/// Which agent's transcript and check `mode` reports: `(check, agent id, transcript)`, or None where nothing is logged.
fn identity(
    mode: &str,
    payload: &Value,
    find: &dyn Fn(&str) -> Option<std::path::PathBuf>,
) -> Option<(String, String, String)> {
    if mode == "returned" {
        return Some((
            text(payload, "agent_type").to_owned(),
            text(payload, "agent_id").to_owned(),
            text(payload, "agent_transcript_path").to_owned(),
        ));
    }
    let resp = payload
        .get("tool_response")
        .filter(|v| v.is_object())
        .cloned()
        .unwrap_or_else(|| json!({}));
    if text(&resp, "status") != "completed" {
        return None;
    }
    let ti = payload
        .get("tool_input")
        .filter(|v| v.is_object())
        .cloned()
        .unwrap_or_else(|| json!({}));
    let aid = text(&resp, "agentId").to_owned();
    let found = (!aid.is_empty()).then(|| find(&aid)).flatten();
    Some((
        text(&ti, "subagent_type").to_owned(),
        aid,
        found.map_or_else(String::new, |p| p.to_string_lossy().into_owned()),
    ))
}

/// Append a check's pass to the log; false where there is nothing to log.
#[must_use = "the log is an append; a caller may ignore whether it wrote"]
pub fn log_pass_at(git_dir: &Path, mode: &str, payload: &Value, at: f64) -> bool {
    log_pass_found(git_dir, mode, payload, at, &transcript_of)
}

/// `log_pass_at`, its transcript finder given.
fn log_pass_found(
    git_dir: &Path,
    mode: &str,
    payload: &Value,
    at: f64,
    find: &dyn Fn(&str) -> Option<std::path::PathBuf>,
) -> bool {
    let Some((check, aid, tpath)) = identity(mode, payload, find) else {
        return false;
    };
    if !LEDGER_CHECKS.contains(&check.as_str()) || tpath.is_empty() {
        return false;
    }
    let Some(body) = read_lossy(Path::new(&tpath)) else {
        return false;
    };
    let lines = py_lines(&body);
    let parts = segments(&lines);
    let Some((wall_s, usage)) = parts.last().and_then(|p| cost(p)) else {
        return false;
    };
    let (wall, tokens) = cells(wall_s, usage);
    let segment = parts.len() - 1;
    let log = git_dir.join(PASS_LOG);
    let mut prior = Vec::new();
    for raw in std::fs::read_to_string(&log)
        .unwrap_or_default()
        .split('\n')
        .filter(|l| !l.trim().is_empty())
    {
        match serde_json::from_str::<Value>(raw) {
            Ok(row) => prior.push(row),
            Err(_) => return false,
        }
    }
    if prior.iter().any(|r| {
        text(r, "agent") == aid
            && r.get("segment").and_then(Value::as_u64) == Some(u64::try_from(segment).unwrap_or(0))
    }) {
        return false;
    }
    let rec = json!({"date": local_date(at), "check": check, "subject": first_prompt(&lines), "agent": aid, "segment": segment, "wall": wall, "tokens": tokens});
    append_line(&log, &format!("{}\n", pyjson::dumps(&rec, None, true))).is_ok()
}

/// `log_pass`, the outcome dropped (`hm_checks._handle` ignores it).
pub fn log_pass(git_dir: &Path, mode: &str, payload: &Value, at: f64) {
    let _ = log_pass_at(git_dir, mode, payload, at);
}

fn append_line(path: &Path, line: &str) -> std::io::Result<()> {
    use std::io::Write as _;
    let mut f = std::fs::OpenOptions::new()
        .append(true)
        .create(true)
        .open(path)?;
    f.write_all(line.as_bytes())
}

/// One line in `<common>/tool-usage.jsonl` (`usage_log.record`), never failing its tool.
pub fn usage(common: &Path, tool: &str, kind: &str, outcome: &str) {
    let secs = std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .map_or(0, |d| d.as_secs());
    let (y, m, d, h, mi, s) = civil(secs);
    let session = std::env::var("CLAUDE_SESSION_ID").unwrap_or_default();
    let rec = json!({"utc": format!("{y:04}-{m:02}-{d:02}T{h:02}:{mi:02}:{s:02}Z"), "tool": tool, "kind": kind, "outcome": outcome, "session": session});
    let _ = append_line(
        &common.join("tool-usage.jsonl"),
        &format!("{}\n", pyjson::dumps(&rec, None, true)),
    );
}

#[cfg(test)]
mod tests;
