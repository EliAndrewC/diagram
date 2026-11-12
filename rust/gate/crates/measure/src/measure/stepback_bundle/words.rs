//! What the step-back bundle reads of the session transcripts (feature 383, plan D11; feature 449 T120, from `stepback_bundle.py`):
//! the tools' time by command, the session's own words, and the calls a guard refused. Each reads a record as the Python did: a
//! `message`, `input` or `content` the Python called `.get` on, or iterated, raises here where it raised there.

use std::collections::{HashMap, HashSet};
use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_gate_core::measure::tool_inventory::py_iter;
use l7r_guard::shared::py_text::{collapse, is_space, repr, strip};
use serde_json::{Map, Value};

use super::super::events::{head, hhmm, py_str, re, truthy, Raised, Tally};
use super::super::turn_time::{or_map, ts_of};

type Row = Map<String, Value>;

/// The words' cap: about 40,000 characters, the newest kept.
pub const WORDS_CAP: usize = 40_000;
const CUT: &str = "[... the hour's earlier words cut to the cap ...]\n";

static MAKES: LazyLock<Regex> = LazyLock::new(|| re(r"\bmake\s+(?:-\S+\s+)*([a-z][\w-]*)"));
static LEAD: LazyLock<Regex> = LazyLock::new(|| re(r"^(cd \S+ && |[A-Z_]+=\S+ )+"));

/// `str(value or default)` of a key.
fn or_text(m: &Row, key: &str, default: &str) -> String {
    m.get(key)
        .filter(|v| truthy(v))
        .map_or_else(|| default.to_owned(), py_str)
}

fn get_str<'a>(m: &'a Row, key: &str) -> Option<&'a str> {
    m.get(key).and_then(Value::as_str)
}

/// `value or []` walked as Python walks it: the `TypeError` for a truthy value that is no list, object or text.
fn walk_or_none(value: Option<&Value>) -> Result<Vec<Value>, Raised> {
    match value {
        Some(v) if truthy(v) => py_iter(v),
        _ => Ok(Vec::new()),
    }
}

/// A command's name for the tally: `make <targets>`, else its first program (assignments and a leading `cd` dropped).
#[must_use]
pub fn command_key(cmd: &str) -> String {
    let mut makes: Vec<String> = Vec::new();
    for c in MAKES.captures_iter(cmd).flatten() {
        if !makes.contains(&c[1].to_owned()) {
            makes.push(c[1].to_owned());
        }
    }
    if !makes.is_empty() {
        return format!("make {}", makes.join("+"));
    }
    let rest = LEAD.replace(strip(cmd), "").into_owned();
    rest.split(is_space)
        .find(|w| !w.is_empty())
        .unwrap_or("?")
        .to_owned()
}

/// The main session's tool calls that started in the window: seconds in tools, and per command its seconds, calls and longest call.
pub struct ToolTime {
    pub total: f64,
    pub spent: Tally<String>,
    pub count: HashMap<String, usize>,
    pub longest: HashMap<String, (f64, String)>,
}

/// `tool_time`: each `tool_use` paired with its `tool_result`.
///
/// # Errors
///
/// A time that is not one, or a message that is no object: the Python's raise.
pub fn tool_time(records: &[Row], since: f64, until: f64) -> Result<ToolTime, Raised> {
    let mut start: HashMap<String, (f64, String, String)> = HashMap::new();
    let mut spent: Tally<String> = Tally::default();
    let mut count: HashMap<String, usize> = HashMap::new();
    let mut longest: HashMap<String, (f64, String)> = HashMap::new();
    for d in records {
        if d.get("isSidechain").is_some_and(truthy) {
            continue;
        }
        let Some(stamp) = d.get("timestamp") else {
            continue;
        };
        let t = ts_of(stamp)?;
        let content = or_map(d.get("message"))?.and_then(|m| m.get("content"));
        let Some(Value::Array(blocks)) = content else {
            continue;
        };
        for b in blocks {
            let Value::Object(b) = b else {
                continue;
            };
            if get_str(b, "type") == Some("tool_use") {
                // the input is read only for a Bash call, as the Python's conditional expression read it
                let cmd = if get_str(b, "name") == Some("Bash") {
                    let inp = or_map(b.get("input"))?;
                    let cmd = inp.map_or_else(String::new, |i| or_text(i, "command", ""));
                    let bg = inp
                        .and_then(|i| i.get("run_in_background"))
                        .is_some_and(truthy);
                    (cmd, bg)
                } else {
                    (String::new(), false)
                };
                let key = if cmd.0.is_empty() {
                    or_text(b, "name", "?")
                } else {
                    command_key(&cmd.0) + if cmd.1 { " [background]" } else { "" }
                };
                let id = b.get("id").map_or_else(|| "None".to_owned(), py_str);
                start.insert(id, (t, key, cmd.0));
            } else if get_str(b, "type") == Some("tool_result") {
                let id = b
                    .get("tool_use_id")
                    .map_or_else(|| "None".to_owned(), py_str);
                let Some((t0, key, cmd)) = start.remove(&id) else {
                    continue;
                };
                if since <= t0 && t0 <= until {
                    spent.add(&key, t - t0);
                    *count.entry(key.clone()).or_default() += 1;
                    if t - t0 > longest.get(&key).map_or(0.0, |l| l.0) {
                        longest.insert(key, (t - t0, head(&collapse(&cmd), 160).to_owned()));
                    }
                }
            }
        }
    }
    let total = spent.items().iter().fold(0.0, |s, (_, v)| s + v);
    Ok(ToolTime {
        total,
        spent,
        count,
        longest,
    })
}

/// The ids of the tool calls a hook refused: their result is an error that opens with the hook's own words.
///
/// # Errors
///
/// A message that is no object, or content the Python could not iterate.
pub fn refused_calls(records: &[Row]) -> Result<HashSet<String>, Raised> {
    let mut out = HashSet::new();
    for d in records {
        if get_str(d, "type") != Some("user") {
            continue;
        }
        let content = or_map(d.get("message"))?.and_then(|m| m.get("content"));
        for b in walk_or_none(content)? {
            let Value::Object(b) = b else {
                continue;
            };
            if get_str(&b, "type") != Some("tool_result") || !b.get("is_error").is_some_and(truthy)
            {
                continue;
            }
            let text = match b.get("content") {
                Some(Value::String(s)) => s.clone(),
                c => walk_or_none(c)?
                    .iter()
                    .filter_map(Value::as_object)
                    .map(|x| or_text(x, "text", ""))
                    .collect::<Vec<_>>()
                    .join(" "),
            };
            let lead = text.trim_start_matches(is_space);
            if lead.starts_with("PreToolUse:")
                || lead.starts_with("<tool_use_error>PreToolUse:")
                || head(&text, 200).contains("hook error:")
            {
                out.insert(
                    b.get("tool_use_id")
                        .map_or_else(|| "None".to_owned(), py_str),
                );
            }
        }
    }
    Ok(out)
}

/// One entry of the words for a tool call, or none for a call the words do not name.
fn call_words(b: &Row, stamp: &str, refused: &HashSet<String>) -> Result<Option<String>, Raised> {
    let name = get_str(b, "name");
    if !matches!(name, Some("Bash" | "Edit" | "Write" | "Agent")) {
        return Ok(None);
    }
    let inp = or_map(b.get("input"))?;
    let empty = Row::new();
    let inp = inp.unwrap_or(&empty);
    // A CALL A GUARD REFUSED never ran (the round arbiter's tooling fix on hour:397@2)
    let verb = if get_str(b, "id").is_some_and(|id| refused.contains(id)) {
        "REFUSED "
    } else {
        ""
    };
    let s = |k: &str| inp.get(k).map_or_else(|| "None".to_owned(), py_str);
    Ok(Some(match name {
        Some("Bash") => format!(
            "[{stamp}] {verb}RAN: {}",
            head(&or_text(inp, "command", ""), 300)
        ),
        Some("Agent") => format!(
            "[{stamp}] {} {}: {}",
            if verb.is_empty() {
                "DISPATCHED".to_owned()
            } else {
                format!("{verb}DISPATCH")
            },
            or_text(inp, "subagent_type", "agent"),
            or_text(inp, "description", "")
        ),
        _ => {
            let old = or_text(inp, "old_string", "");
            let new = [inp.get("new_string"), inp.get("content")]
                .into_iter()
                .flatten()
                .find(|v| truthy(v))
                .map_or_else(String::new, py_str);
            format!(
                "[{stamp}] {verb}{} {}: {} -> {}",
                name.unwrap_or_default().to_uppercase(),
                s("file_path"),
                repr(head(&old, 200)),
                repr(head(&new, 200))
            )
        }
    }))
}

/// The sessions' own words in the window, in order: replies, commands, edits - never a tool's output; the newest kept. A record
/// tagged `_sid` is labeled with its session's first 8 characters.
///
/// # Errors
///
/// A time that is not one, or a message, input or content the Python could not read.
pub fn words(records: &[Row], since: f64, until: f64, cap: usize) -> Result<String, Raised> {
    let mut parts: Vec<String> = Vec::new();
    let refused = refused_calls(records)?;
    for d in records {
        if d.get("isSidechain").is_some_and(truthy) || get_str(d, "type") != Some("assistant") {
            continue;
        }
        let Some(stamp) = d.get("timestamp") else {
            continue;
        };
        let t = ts_of(stamp)?;
        if !(since <= t && t <= until) {
            continue;
        }
        let sid = d
            .get("_sid")
            .filter(|v| truthy(v))
            .map_or_else(String::new, |v| format!(" {}", head(&py_str(v), 8)));
        let stamp = format!("{}{sid}", hhmm(t));
        let content = or_map(d.get("message"))?.and_then(|m| m.get("content"));
        for b in walk_or_none(content)? {
            let Value::Object(b) = b else {
                continue;
            };
            if get_str(&b, "type") == Some("text") && !strip(&or_text(&b, "text", "")).is_empty() {
                parts.push(format!("[{stamp}] SAID: {}", strip(&py_str(&b["text"]))));
            } else if get_str(&b, "type") == Some("tool_use") {
                parts.extend(call_words(&b, &stamp, &refused)?);
            }
        }
    }
    let text = parts.join("\n");
    if text.chars().count() <= cap {
        return Ok(text);
    }
    // OVER THE CAP, COMMANDS AND EDITS SHRINK FIRST (the round arbiter's tooling fix on hour:383@1): each RAN and EDIT keeps its first
    // line, every SAID and DISPATCHED stays whole, and only then are the oldest entries dropped
    let parts: Vec<String> = parts
        .iter()
        .map(|p| {
            let body = p.split_once("] ").map_or(p.as_str(), |(_, b)| b);
            if body.starts_with("SAID") || body.starts_with("DISPATCHED") {
                p.clone()
            } else {
                head(p.split('\n').next().unwrap_or_default(), 200).to_owned()
            }
        })
        .collect();
    let text = parts.join("\n");
    let n = text.chars().count();
    if n <= cap {
        return Ok(text);
    }
    Ok(CUT.to_owned() + &text.chars().skip(n - cap).collect::<String>())
}

#[cfg(test)]
mod tests;
