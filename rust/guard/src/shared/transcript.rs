//! What the session's transcript says (`hm_approval.gm_messages`): every message the GM wrote - typed prompts, the messages he sent
//! while the session worked (`queued_command` attachments), and his answers to `AskUserQuestion` - each with its curly quotes made
//! straight and its whitespace collapsed (`norm`).

use std::collections::HashSet;
use std::sync::LazyLock;

use fancy_regex::Regex;
use serde_json::Value;

/// The harness's words for an answered question, when the result carries no `answers`.
static ANSWERED: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(r"^\s*(?:Your questions have been answered|User has answered your questions)\b")
        .unwrap()
});

/// `text` with curly quotes straightened and its whitespace collapsed to single spaces (`norm`).
#[must_use]
pub fn norm(text: &str) -> String {
    let straight: String = text
        .chars()
        .map(|c| match c {
            '\u{2018}' | '\u{2019}' => '\'',
            '\u{201c}' | '\u{201d}' => '"',
            other => other,
        })
        .collect();
    straight.split_whitespace().collect::<Vec<_>>().join(" ")
}

fn s<'a>(v: &'a Value, k: &str) -> &'a str {
    v.get(k).and_then(Value::as_str).unwrap_or("")
}

fn truthy(v: Option<&Value>) -> bool {
    match v {
        Some(Value::Bool(b)) => *b,
        Some(Value::String(t)) => !t.is_empty(),
        Some(Value::Array(a)) => !a.is_empty(),
        Some(Value::Object(o)) => !o.is_empty(),
        Some(Value::Number(n)) => n.as_f64() != Some(0.0),
        _ => false,
    }
}

/// A `user` record the GM typed, not one the harness or an SDK caller wrote (`_typed`).
fn typed(rec: &Value) -> bool {
    if ["isMeta", "isSidechain", "isCompactSummary"]
        .iter()
        .any(|k| truthy(rec.get(*k)))
    {
        return false;
    }
    let origin = rec.get("origin").map_or("", |o| s(o, "kind"));
    if !origin.is_empty() || truthy(rec.get("promptSource")) {
        return origin == "human" || s(rec, "promptSource") == "typed";
    }
    !s(rec, "entrypoint").starts_with("sdk")
}

/// The text of a tool result's content: a string, or its parts' `text` joined by spaces.
fn result_text(body: Option<&Value>) -> String {
    match body {
        Some(Value::String(t)) => t.clone(),
        Some(Value::Array(parts)) => parts
            .iter()
            .filter(|p| p.is_object())
            .map(|p| s(p, "text"))
            .collect::<Vec<_>>()
            .join(" "),
        _ => String::new(),
    }
}

/// A queued message the GM sent while the session worked, or None.
fn queued(rec: &Value) -> Option<String> {
    let att = rec.get("attachment")?;
    let human = att.get("origin").is_some_and(|o| s(o, "kind") == "human");
    (human && !truthy(att.get("isMeta")))
        .then(|| att.get("prompt").and_then(Value::as_str).map(str::to_owned))?
}

/// The answers a `user` record carries to the questions `asked`.
fn answers(rec: &Value, content: &[Value], asked: &HashSet<String>) -> Vec<String> {
    let result = rec.get("toolUseResult");
    content
        .iter()
        .filter(|c| s(c, "type") == "tool_result" && asked.contains(s(c, "tool_use_id")))
        .map(|c| result_text(c.get("content")))
        // an ANSWER, not the harness's note that the GM declined to answer
        .filter(|text| match result {
            Some(r @ Value::Object(_)) => truthy(r.get("answers")),
            _ => ANSWERED.is_match(text).unwrap_or(false),
        })
        .collect()
}

/// Every message the GM wrote in the transcript `text` (JSON lines), in order and normalized.
#[must_use]
pub fn gm_messages(text: &str) -> Vec<String> {
    let mut out = Vec::new();
    let mut asked = HashSet::new();
    for rec in text
        .lines()
        .filter_map(|l| serde_json::from_str::<Value>(l).ok())
    {
        let content = rec.get("message").and_then(|m| m.get("content"));
        let parts = content
            .and_then(Value::as_array)
            .map_or(&[][..], Vec::as_slice);
        match s(&rec, "type") {
            "attachment"
                if rec
                    .get("attachment")
                    .is_some_and(|a| s(a, "type") == "queued_command") =>
            {
                out.extend(queued(&rec));
            }
            "assistant" => asked.extend(
                parts
                    .iter()
                    .filter(|c| s(c, "type") == "tool_use" && s(c, "name") == "AskUserQuestion")
                    .map(|c| s(c, "id").to_owned()),
            ),
            "user" => {
                if let Some(Value::String(t)) = content {
                    if typed(&rec) {
                        out.push(t.clone());
                    }
                }
                out.extend(answers(&rec, parts, &asked));
            }
            _ => {}
        }
    }
    out.iter().map(|m| norm(m)).collect()
}

#[cfg(test)]
mod tests;
