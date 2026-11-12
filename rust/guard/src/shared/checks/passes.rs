//! A check's pass logged, read off its transcript (features 371, 294; from `hm_checks.log_pass`): one line per return in `<git common dir>/check-passes.jsonl`, the ledger's
//! cost cells computed over the transcript by `shared::ledger::cost` (the one review cost, feature 449 T83), and the tool-usage line (`usage_log.record`) an automatic step leaves. Never raises: a hook that fails here must not take the session's tool call with it.

use std::path::Path;

use serde_json::{json, Value};

use super::reply::{py_lines, read_lossy};
use super::text;
use crate::shared::ledger::cost::{cells, cost, segments, transcript};
use crate::shared::ledger::CHECKS;
use crate::shared::log::civil;
use crate::shared::pyjson;
use crate::shared::tool::ask;

const PASS_LOG: &str = "check-passes.jsonl";

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

fn transcript_of(agent: &str) -> Option<std::path::PathBuf> {
    transcript(
        agent,
        &Path::new(&std::env::var("HOME").ok()?).join(".claude/projects"),
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
    if !CHECKS.contains(&check.as_str()) || tpath.is_empty() {
        return false;
    }
    let Some(body) = read_lossy(Path::new(&tpath)) else {
        return false;
    };
    let lines = py_lines(&body);
    let parts = segments(&lines);
    let Some(costed) = parts.last().and_then(|p| cost(p).ok()) else {
        return false;
    };
    let both = cells(&costed);
    let (wall, tokens) = both.split_once(" | ").unwrap_or((&both, ""));
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
#[expect(clippy::many_single_char_names, reason = "the fields of a date")]
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
