//! A dispatch a guard refused is sent again or recorded dropped before a turn ends (feature 385 T22, plan D44; ported from `hm_dropped.py`, feature 449 T051).
//!
//! WHY. Measured on feature 385 T05 (2026-10-18, the session transcript): of seven agents sent at 03:57, the decide-first guard refused four with identical lines that named
//! no check. The session re-sent three at 04:02; the fourth, impl-drift round 2, was never re-sent, and the session ended its turn "waiting on" it - about 5 h idle until the
//! GM came back.
//!
//! WHAT IS READ. The Stop payload's transcript, from its last TURN END - a `system` entry of subtype `turn_duration`, which the harness writes only for a turn that ended (a
//! turn end this guard blocks writes none, so a refusal stays in the window until answered) - never from the GM's last prompt: the incident's refusals came after a prompt
//! queued and taken into the running turn, so that window would have missed them. A refusal is answered by a later Agent call of the same type and key that was not refused,
//! or by `make dispatch-dropped`, which appends to `<gitdir>/dropped-dispatches.jsonl`.

use std::collections::{HashMap, HashSet};
use std::path::{Path, PathBuf};
use std::sync::LazyLock;

use fancy_regex::Regex;
use serde_json::{json, Value};

use crate::protocol::Reply;
use crate::shared::escape::enough;
use crate::shared::state::field;
use crate::shared::tool::ask;

fn re(pattern: &str) -> Regex {
    Regex::new(pattern).unwrap_or_else(|e| unreachable!("{e}"))
}

static BUNDLE: LazyLock<Regex> =
    LazyLock::new(|| re(r#"[^\s`'"]*/MANIFEST\.md|/tmp/l7r-check/[^\s`'")]+"#));
static BLOCKED: LazyLock<Regex> = LazyLock::new(|| re(r"BLOCKED: ([^\n]*)"));
const REFUSED: &str = "PreToolUse:Agent hook error";
const DROPPED: &str = "dropped-dispatches.jsonl";

fn gitdir(root: &Path) -> PathBuf {
    let text = root.to_string_lossy();
    let out = ask(
        root,
        "git",
        &["-C", &text, "rev-parse", "--git-common-dir"],
        "",
    )
    .out;
    let dir = PathBuf::from(if out.trim().is_empty() {
        ".git"
    } else {
        out.trim()
    });
    root.join(dir) // an absolute one (a linked worktree) replaces `root`
}

fn key_of(input: &Value) -> String {
    let prompt = field(input, "prompt");
    match BUNDLE.find(prompt) {
        Ok(Some(m)) => m.as_str().to_owned(),
        _ => field(input, "description").to_owned(),
    }
}

fn rows_of(transcript: &Path) -> Vec<Value> {
    let text = String::from_utf8_lossy(&std::fs::read(transcript).unwrap_or_default()).into_owned();
    text.lines()
        .filter_map(|l| serde_json::from_str(l).ok())
        .collect()
}

fn content(entry: &Value) -> &[Value] {
    entry["message"]["content"]
        .as_array()
        .map_or(&[], Vec::as_slice)
}

fn last_turn_end(rows: &[Value]) -> String {
    let mut ended = rows
        .iter()
        .filter(|r| r["type"] == "system" && r["subtype"] == "turn_duration");
    ended
        .next_back()
        .map_or_else(String::new, |r| field(r, "timestamp").to_owned())
}

#[derive(Clone, Debug, PartialEq, Eq)]
struct Call {
    t: String,
    kind: String,
    key: String,
    refused: bool,
    why: String,
}

/// Every Agent call in order.
fn calls(rows: &[Value]) -> Vec<Call> {
    let (mut out, mut by_id): (Vec<Call>, HashMap<&str, usize>) = (Vec::new(), HashMap::new());
    for row in rows {
        for block in content(row) {
            if block["type"] == "tool_use" && block["name"] == "Agent" {
                let input = &block["input"];
                let call = Call {
                    t: field(row, "timestamp").to_owned(),
                    kind: field(input, "subagent_type").to_owned(),
                    key: key_of(input),
                    refused: false,
                    why: String::new(),
                };
                by_id.insert(field(block, "id"), out.len());
                out.push(call);
            } else if block["type"] == "tool_result" && block["is_error"] == true {
                let Some(call) = by_id.get(field(block, "tool_use_id")).map(|i| &mut out[*i])
                else {
                    continue;
                };
                let text = block["content"]
                    .as_str()
                    .map_or_else(|| block["content"].to_string(), str::to_owned);
                if text.contains(REFUSED) {
                    call.refused = true;
                    let reason = BLOCKED
                        .captures(&text)
                        .ok()
                        .flatten()
                        .and_then(|m| m.get(1))
                        .map_or("", |m| m.as_str());
                    call.why = reason.chars().take(160).collect();
                }
            }
        }
    }
    out
}

fn dropped(root: &Path) -> HashSet<(String, String)> {
    let text = std::fs::read_to_string(gitdir(root).join(DROPPED)).unwrap_or_default();
    let rows = text
        .lines()
        .filter_map(|l| serde_json::from_str::<Value>(l).ok());
    rows.map(|d| (field(&d, "type").to_owned(), field(&d, "bundle").to_owned()))
        .collect()
}

fn unanswered(rows: &[Value], since: &str, gone: &HashSet<(String, String)>) -> Vec<Call> {
    let seq = calls(rows);
    let same = |a: &Call, b: &Call| a.kind == b.kind && a.key == b.key;
    let mut left: Vec<Call> = Vec::new();
    for (i, call) in seq.iter().enumerate() {
        let answered = seq[i + 1..].iter().any(|d| !d.refused && same(d, call));
        let recorded = gone.contains(&(call.kind.clone(), call.key.clone()));
        if call.refused
            && call.t.as_str() > since
            && !recorded
            && !answered
            && !left.iter().any(|d| same(d, call))
        {
            left.push(call.clone());
        }
    }
    left
}

fn refusal(left: &[Call]) -> String {
    let mut lines = vec![format!("BLOCKED: {} dispatch(es) a guard refused this turn were neither sent again nor recorded dropped:", left.len())];
    for c in left {
        let why = if c.why.is_empty() {
            String::new()
        } else {
            format!(" - refused: {}", c.why)
        };
        lines.push(format!("    {} on {}{why}", c.kind, c.key));
    }
    lines
        .push("Send each again once its refusal is met, or, if it is no longer wanted:".to_owned());
    for c in left {
        lines.push(format!(
            "    make dispatch-dropped TYPE={} BUNDLE=\"{}\" WHY=\"<why it is not owed>\"",
            c.kind, c.key
        ));
    }
    lines.push("(feature 385 T22: a refused impl-drift was never re-sent and the session idled 5 h waiting on it)".to_owned());
    lines.join("\n")
}

/// The refusal for a turn's end, or None when every refused dispatch is answered.
pub(crate) fn refusal_for(root: &Path, payload: &Value) -> Option<String> {
    let transcript = Path::new(field(payload, "transcript_path"));
    if !transcript.is_file() {
        return None;
    }
    let rows = rows_of(transcript);
    let left = unanswered(&rows, &last_turn_end(&rows), &dropped(root));
    (!left.is_empty()).then(|| refusal(&left))
}

fn drop_one(root: &Path, kind: &str, bundle: &str, why: &str) -> Reply {
    if !enough(why) {
        return Reply { stdout: String::new(), stderr: "dispatch-dropped: WHY=\"<reason>\" needs two words and eight characters, so the audit says why\n".to_owned(), code: 2 };
    }
    let t = ask(root, "date", &["-u", "+%FT%TZ"], "")
        .out
        .trim()
        .to_owned();
    let row = json!({"type": kind, "bundle": bundle, "why": why, "t": t});
    let path = gitdir(root).join(DROPPED);
    let kept = std::fs::read_to_string(&path).unwrap_or_default();
    let _ = std::fs::write(&path, format!("{kept}{row}\n"));
    Reply {
        stdout: format!("dispatch-dropped: {kind} on {bundle} recorded - {why}\n"),
        stderr: String::new(),
        code: 0,
    }
}

/// `l7r-guard dropped drop --root <clone> --type <t> --bundle <key> --why "<reason>"`.
#[must_use]
pub fn cli(args: &[String]) -> Reply {
    let value = |flag: &str| {
        args.iter()
            .position(|a| a == flag)
            .and_then(|i| args.get(i + 1))
            .map_or("", String::as_str)
    };
    if args.first().map(String::as_str) != Some("drop") {
        return Reply { stdout: String::new(), stderr: "usage: l7r-guard dropped drop --root <clone> --type <t> --bundle <key> --why \"<reason>\"\n".to_owned(), code: 2 };
    }
    let root = value("--root");
    drop_one(
        Path::new(if root.is_empty() { "." } else { root }),
        value("--type"),
        value("--bundle"),
        value("--why"),
    )
}

#[cfg(test)]
mod tests;
