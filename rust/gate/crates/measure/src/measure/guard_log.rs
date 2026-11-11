//! `make guard-log`: the guard firings, listed so a refusal can be audited after the fact (feature 204; feature 449 T76, from `guard-log.py`).
//!
//! WHY (GM 2026-09-07): "anytime we block a command invocation, we can see what specifically was happening and whether the command was
//! rewritable safely." A reader, not a report generator: filters and columns, nothing derived.

use std::path::{Path, PathBuf};

use serde_json::Value;

use super::reply;

const EVENTS: [&str; 4] = ["blocked", "rewrote", "escaped", "reminded"];

fn load(dir: &Path) -> Vec<Value> {
    let mut names: Vec<PathBuf> = std::fs::read_dir(dir)
        .into_iter()
        .flatten()
        .flatten()
        .map(|e| e.path())
        .filter(|p| p.extension().is_some_and(|x| x == "json"))
        .collect();
    names.sort();
    let mut rows: Vec<Value> = names
        .iter()
        .filter_map(|p| serde_json::from_str(&std::fs::read_to_string(p).ok()?).ok())
        .collect();
    rows.sort_by_key(|r| text(r, "utc"));
    rows
}

/// `row.get(key)` as text, empty when absent.
fn text(row: &Value, key: &str) -> String {
    match &row[key] {
        Value::Null => String::new(),
        Value::String(s) => s.clone(),
        other => other.to_string(),
    }
}

fn session_name(row: &Value) -> String {
    let named = text(row, "session_name");
    if !named.is_empty() {
        return named;
    }
    let sid = text(row, "session");
    if sid.is_empty() || sid == "unknown" || sid == "nosession" {
        "unknown".to_owned()
    } else {
        sid.chars().take(8).collect()
    }
}

/// What the rows are filtered by.
#[derive(Default)]
struct Filter<'a> {
    guard: Option<&'a str>,
    since: Option<&'a str>,
    event: Option<&'a str>,
}

impl Filter<'_> {
    fn matches(&self, row: &Value) -> bool {
        self.guard.is_none_or(|g| row["guard"] == g)
            && self.since.is_none_or(|s| text(row, "utc").as_str() >= s)
            && self.event.is_none_or(|e| row["event"] == e)
    }
}

fn cut(s: &str, n: usize) -> String {
    s.chars().take(n).collect()
}

fn or_dash(s: String) -> String {
    if s.is_empty() {
        "-".to_owned()
    } else {
        s
    }
}

fn render(rows: &[Value], full: bool) -> Vec<String> {
    let mut out = Vec::new();
    for r in rows {
        let name = session_name(r);
        let command = [text(r, "command"), text(r, "detail")]
            .into_iter()
            .find(|c| !c.is_empty())
            .unwrap_or_default();
        let first = command.split('\n').next().unwrap_or_default();
        let rule = [text(r, "rule"), text(r, "event")]
            .into_iter()
            .find(|c| !c.is_empty())
            .unwrap_or_default();
        let head = format!(
            "{}  {:<18}  {:<12}  {}/{rule}",
            cut(&text(r, "utc"), 19),
            cut(&name, 18),
            text(r, "guard"),
            text(r, "event")
        );
        if full {
            out.push(head);
            out.push(format!(
                "    cwd: {}    tool: {}",
                or_dash(text(r, "cwd")),
                or_dash(text(r, "tool"))
            ));
            out.push(format!(
                "    command: {}",
                command.replace('\n', "\n             ")
            ));
            if !r["context"].is_null() && r["context"] != "" {
                out.push(format!("    context: {}", r["context"]));
            }
        } else {
            out.push(format!(
                "{head}  {:<36}  {}",
                cut(&or_dash(text(r, "cwd")), 36),
                cut(first, 80)
            ));
        }
    }
    out
}

fn flag<'a>(args: &'a [String], name: &str) -> Option<&'a str> {
    args.windows(2)
        .find(|w| w[0] == name)
        .map(|w| w[1].as_str())
}

/// `l7r-gate measure guard-log [--guard G] [--since D] [--event E] [--full] [--dir D]`.
pub fn cli(args: &[String], home: &Path) -> crate::Reply {
    let event = flag(args, "--event");
    if event.is_some_and(|e| !EVENTS.contains(&e)) {
        return reply(
            String::new(),
            "guard-log: --event is one of blocked, rewrote, escaped, reminded\n".to_owned(),
            2,
        );
    }
    let dir = flag(args, "--dir").map_or_else(|| home.join(".claude/guard-log"), PathBuf::from);
    let filter = Filter {
        guard: flag(args, "--guard"),
        since: flag(args, "--since"),
        event,
    };
    let rows: Vec<Value> = load(&dir)
        .into_iter()
        .filter(|r| filter.matches(r))
        .collect();
    if rows.is_empty() {
        return reply("(no matching firings)\n".to_owned(), String::new(), 0);
    }
    let body = render(&rows, args.iter().any(|a| a == "--full")).join("\n");
    reply(
        format!("{body}\n{} firing(s)\n", rows.len()),
        String::new(),
        0,
    )
}

#[cfg(test)]
mod tests;
