//! The event log READ (feature 449 T119, the measure chain's first slice under `ask:449-T83-scope`): `event_log.py`'s other half - a log
//! or a transcript's lines, a session transcript turned into the events the hooks would have written (`from_transcript`, plan D8 of
//! feature 375), and the reversals (A -> B -> A) a log records. It lives beside the writer so there is one reader: the round arbiter's
//! bundle (`arbiter/bundle/sections.rs`) and `make feature-report` and `make where-time` (`l7r-gate measure`) all read through it, the
//! T89 precedent of reusing `at_rev`, and the guard crate cannot build on the gate's.

use std::collections::{HashMap, HashSet};
use std::path::Path;
use std::sync::LazyLock;

use fancy_regex::Regex;
use serde_json::{Map, Value};

use super::{first_group, line, now_stamp, re, truthy, typed_prompt};
use crate::shared::py_text::strip;
use crate::shared::pyjson::py_str;

static NOTIFICATION: LazyLock<Regex> = LazyLock::new(|| re(r"<task-id>([^<]+)</task-id>"));
// Python's `$` without MULTILINE also stops before a final newline (`event_log._RESULT`), which Rust's `\z` does not
static RESULT: LazyLock<Regex> =
    LazyLock::new(|| re(r"(?s)<result>(.*?)(?:</result>|(?=\n\z)|\z)"));

/// Text as Python's text mode reads it: `\r\n` and a lone `\r` both end a line (universal newlines).
#[must_use]
pub fn universal(text: &str) -> String {
    text.replace("\r\n", "\n").replace('\r', "\n")
}

/// `json.loads` of each line of a JSONL file read with `errors="replace"`, a line that does not parse skipped (`event_log.read_jsonl`).
///
/// # Errors
///
/// Where the file cannot be read, as the Python's `open` raised.
pub fn read_jsonl(path: &Path) -> std::io::Result<Vec<Value>> {
    let bytes = std::fs::read(path)?;
    Ok(universal(&String::from_utf8_lossy(&bytes))
        .split('\n')
        .map(strip)
        .filter(|l| !l.is_empty())
        .filter_map(|l| serde_json::from_str(l).ok())
        .collect())
}

/// `str(x or "")`: Python's `str` of a truthy value, "" otherwise.
fn or_str(v: Option<&Value>) -> String {
    v.filter(|x| truthy(x)).map_or_else(String::new, py_str)
}

/// `x or {}`: the value where it is truthy, an empty object otherwise.
fn or_object(v: Option<&Value>) -> Value {
    v.filter(|x| truthy(x))
        .cloned()
        .unwrap_or_else(|| Value::Object(Map::new()))
}

/// `(x or {})` read as a mapping: a truthy value that is no object is the Python's `AttributeError`.
fn mapping<'a>(v: &'a Value, what: &str) -> Result<&'a Map<String, Value>, String> {
    v.as_object()
        .ok_or_else(|| format!("AttributeError: the transcript's {what} is no object"))
}

/// `for b in (x or [])`: the items a value iterates as, a number or `true` the Python's `TypeError`; a string or an object iterate as
/// characters and keys, which no test of a block passes, so as nothing.
fn blocks<'a>(v: Option<&'a Value>, what: &str) -> Result<&'a [Value], String> {
    match v.filter(|x| truthy(x)) {
        None | Some(Value::String(_) | Value::Object(_)) => Ok(&[]),
        Some(Value::Array(items)) => Ok(items),
        Some(_) => Err(format!(
            "TypeError: the transcript's {what} is not iterable"
        )),
    }
}

fn payload(pairs: &[(&str, Value)]) -> Value {
    Value::Object(
        pairs
            .iter()
            .map(|(k, v)| ((*k).to_owned(), v.clone()))
            .collect(),
    )
}

/// The events a session transcript records, in time order, as the hook would have written them (`event_log.from_transcript`): a
/// `tool_use` its `PreToolUse`, its `tool_result` its `PostToolUse`, an async agent's launch its `SubagentStart` and the queue's
/// `<task-notification>` its `SubagentStop`, a typed prompt `UserPromptSubmit`, an `end_turn` Stop.
///
/// # Errors
///
/// Where the Python raised: a row, a message or a tool's input that is no object, a content that is not iterable.
pub fn from_transcript(rows: &[Value]) -> Result<Vec<Map<String, Value>>, String> {
    let mut out: Vec<Map<String, Value>> = Vec::new();
    let mut calls: HashMap<String, (String, Value)> = HashMap::new();
    let mut agent_types: HashMap<String, String> = HashMap::new();
    let null = Value::Null;
    for d in rows {
        let d = mapping(d, "row")?;
        if d.get("isSidechain").is_some_and(truthy) {
            continue;
        }
        let stamp = or_str(d.get("timestamp"));
        // `line(payload, t or now())`: a row with no time is stamped now, as the Python's was
        let t = if stamp.is_empty() {
            now_stamp(std::time::SystemTime::now())
        } else {
            stamp
        };
        let sid = Value::from(or_str(d.get("sessionId")));
        let kind = d.get("type").unwrap_or(&null);
        if kind == "assistant" {
            let msg = or_object(d.get("message"));
            let msg = mapping(&msg, "message")?;
            for b in blocks(msg.get("content"), "content")? {
                if b.get("type") == Some(&Value::from("tool_use")) {
                    let input = or_object(b.get("input"));
                    calls.insert(
                        py_str(b.get("id").unwrap_or(&null)),
                        (py_str(b.get("name").unwrap_or(&null)), input.clone()),
                    );
                    out.push(line(
                        &payload(&[
                            ("hook_event_name", Value::from("PreToolUse")),
                            ("session_id", sid.clone()),
                            ("tool_name", b.get("name").cloned().unwrap_or(Value::Null)),
                            ("tool_use_id", b.get("id").cloned().unwrap_or(Value::Null)),
                            ("tool_input", input),
                        ]),
                        &t,
                    ));
                }
            }
            if msg.get("stop_reason") == Some(&Value::from("end_turn")) {
                out.push(line(
                    &payload(&[
                        ("hook_event_name", Value::from("Stop")),
                        ("session_id", sid.clone()),
                    ]),
                    &t,
                ));
            }
        } else if kind == "user" && !d.get("isMeta").is_some_and(truthy) {
            let msg = or_object(d.get("message"));
            let content = mapping(&msg, "message")?.get("content").unwrap_or(&null);
            for b in content.as_array().map_or(&[][..], Vec::as_slice) {
                if b.get("type") == Some(&Value::from("tool_result")) {
                    user_result(b, d, &sid, &t, &calls, &mut agent_types, &mut out)?;
                }
            }
            if typed_prompt(content) {
                let mut row = line(
                    &payload(&[
                        ("hook_event_name", Value::from("UserPromptSubmit")),
                        ("session_id", sid.clone()),
                    ]),
                    &t,
                );
                row.insert("gm".into(), Value::Bool(true));
                out.push(row);
            }
        } else if kind == "queue-operation" && d.get("operation") == Some(&Value::from("enqueue")) {
            let content = or_str(d.get("content"));
            let Some(id) = first_group(&NOTIFICATION, &content) else {
                continue;
            };
            let Some(atype) = agent_types.get(&id) else {
                continue;
            };
            let result = first_group(&RESULT, &content).unwrap_or_default();
            out.push(line(
                &payload(&[
                    ("hook_event_name", Value::from("SubagentStop")),
                    ("session_id", sid.clone()),
                    ("agent_type", Value::from(atype.clone())),
                    ("agent_id", Value::from(id)),
                    ("last_assistant_message", Value::from(result)),
                ]),
                &t,
            ));
        }
    }
    out.sort_by(|a, b| a["t"].as_str().cmp(&b["t"].as_str()));
    Ok(out)
}

/// A `tool_result` block: its `PostToolUse`, and an Agent's launch remembered (its `SubagentStart` where it went to the background).
fn user_result(
    b: &Value,
    d: &Map<String, Value>,
    sid: &Value,
    t: &str,
    calls: &HashMap<String, (String, Value)>,
    agent_types: &mut HashMap<String, String>,
    out: &mut Vec<Map<String, Value>>,
) -> Result<(), String> {
    let null = Value::Null;
    let use_id = b.get("tool_use_id").unwrap_or(&null);
    let (name, ti) = calls
        .get(&py_str(use_id))
        .cloned()
        .unwrap_or_else(|| (String::new(), Value::Object(Map::new())));
    let resp = d
        .get("toolUseResult")
        .filter(|r| r.is_object())
        .cloned()
        .unwrap_or_else(|| Value::Object(Map::new()));
    out.push(line(
        &payload(&[
            ("hook_event_name", Value::from("PostToolUse")),
            ("session_id", sid.clone()),
            ("tool_name", Value::from(name.clone())),
            ("tool_use_id", use_id.clone()),
            ("tool_input", ti.clone()),
            ("tool_response", resp.clone()),
        ]),
        t,
    ));
    let Some(aid) = resp.get("agentId").filter(|a| truthy(a)) else {
        return Ok(());
    };
    if name != "Agent" {
        return Ok(());
    }
    let atype = or_str(mapping(&ti, "tool input")?.get("subagent_type"));
    let atype = if atype.is_empty() {
        "general-purpose".to_owned()
    } else {
        atype
    };
    agent_types.insert(py_str(aid), atype.clone());
    if resp.get("status") == Some(&Value::from("async_launched")) {
        out.push(line(
            &payload(&[
                ("hook_event_name", Value::from("SubagentStart")),
                ("session_id", sid.clone()),
                ("agent_type", Value::from(atype)),
                ("agent_id", aid.clone()),
            ]),
            t,
        ));
    }
    Ok(())
}

/// (path, time) of every Edit that put back a passage an earlier Edit of the same file had replaced (`feature_report.reversals`, moved
/// here from the round arbiter's bundle by feature 449 T119 so the report and the bundle share it).
#[must_use]
pub fn reversals(events: &[&Map<String, Value>]) -> Vec<(String, String)> {
    let mut out: Vec<(String, String)> = Vec::new();
    let mut replaced: HashMap<String, HashSet<String>> = HashMap::new();
    let null = Value::Null;
    for e in events {
        if e.get("ev") != Some(&Value::from("PreToolUse"))
            || e.get("tool") != Some(&Value::from("Edit"))
            || !e.get("old").is_some_and(truthy)
        {
            continue;
        }
        let path = py_str(e.get("path").unwrap_or(&null));
        let seen = replaced.entry(path.clone()).or_default();
        if e.get("new")
            .and_then(Value::as_str)
            .is_some_and(|n| seen.contains(n))
        {
            out.push((path, py_str(e.get("t").unwrap_or(&null))));
        }
        seen.insert(py_str(e.get("old").unwrap_or(&null)));
    }
    out
}

#[cfg(test)]
mod tests;
