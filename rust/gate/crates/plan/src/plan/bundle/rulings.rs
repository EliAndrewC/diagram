//! The round arbiter's rulings a plan review's blocks cite, each one's ruling, why and what (feature 449 T169): the bundle's `rulings.md`.
//!
//! WHY: a plan block decides under a ruling it names (`ask:449-engine-order`), and the bundle carried only the rulings the spec's own
//! text quotes, so plan reviews kept saying a ruling the block named was not in the bundle - T168's first review came back
//! NOT-REVIEWABLE partly for it (`specs/449-rust-codebase/plan-done.md`, `### T168 (`). The reviewer reads the bundle and nothing in the
//! repository, so each cited ruling's own record - when it was ruled, its ruling, why and what, verbatim - rides in it.

use std::fmt::Write as _;
use std::path::Path;
use std::sync::LazyLock;

use fancy_regex::Regex;
use serde_json::{Map, Value};

use super::super::sections::re;

/// A ruling's key as the plans cite it: `ask:` and its name (`ask:449-engine-order`, `ask:set-down-449-efficiency-round-2`), a trailing
/// `'s` or punctuation left out.
static ASK: LazyLock<Regex> =
    LazyLock::new(|| re(r"(?<![\w:-])(ask:[A-Za-z0-9](?:[A-Za-z0-9._-]*[A-Za-z0-9])?)"));

/// The fields a ruling's record carries into the bundle, in this order: when it was ruled, the ruling, its why and its what - the brief's
/// "its why and what, verbatim" (feature 449 T169). The question asked and the rest stay in the log: on T168's bundle `asked` alone was
/// 12.6 KB of the 33.6 KB the records' fields took (observed 2026-11-17, method: the bytes of each field's lines in `rulings.md`).
const FIELDS: [&str; 4] = ["utc", "ruling", "why", "what"];

/// Each `ask:` key the blocks cite, in their order, each once.
pub(super) fn cited(bodies: &[&str]) -> Vec<String> {
    let mut keys: Vec<String> = Vec::new();
    for body in bodies {
        for c in ASK.captures_iter(body).flatten() {
            if !keys.iter().any(|k| *k == c[1]) {
                keys.push(c[1].to_owned());
            }
        }
    }
    keys
}

/// Every record of a ruling log, the lines that are not JSON objects left out.
fn records(path: &Path) -> Vec<Map<String, Value>> {
    std::fs::read_to_string(path)
        .unwrap_or_default()
        .lines()
        .filter_map(|l| serde_json::from_str::<Map<String, Value>>(l).ok())
        .collect()
}

/// One record as Markdown: each of [`FIELDS`] it holds, verbatim - a string as written, anything else as its JSON, an empty one left out.
fn shown(m: &Map<String, Value>, file: &str) -> String {
    let fields: String = FIELDS
        .iter()
        .filter_map(|n| {
            let v = m.get(*n)?;
            let text = v.as_str().map_or_else(|| v.to_string(), str::to_owned);
            (!text.is_empty()).then(|| format!("- **{n}**: {text}\n"))
        })
        .collect();
    format!("Recorded in `{file}`:\n\n{fields}")
}

/// `rulings.md`: for each `ask:` key the blocks cite, every record of it - from the reviewed feature's own `arbiter.jsonl`, else from
/// whichever other feature's log holds it - or a line saying no log does, so the reviewer can tell "not recorded" from "not cited".
pub(super) fn rulings(spec_dir: &Path, bodies: &[&str]) -> String {
    let keys = cited(bodies);
    let head = "# The round arbiter's rulings the blocks cite, their ruling, why and what from `arbiter.jsonl`, verbatim\n\n";
    if keys.is_empty() {
        return format!("{head}(none - the blocks cite no `ask:` ruling)\n");
    }
    let parent = spec_dir.parent().unwrap_or(Path::new("."));
    let name = |p: &Path| {
        p.strip_prefix(parent.parent().unwrap_or(parent))
            .unwrap_or(p)
            .display()
            .to_string()
    };
    let own = spec_dir.join("arbiter.jsonl");
    let mut logs: Vec<(String, Vec<Map<String, Value>>)> = vec![(name(&own), records(&own))];
    let hits = |logs: &[(String, Vec<Map<String, Value>>)],
                key: &str|
     -> Option<(String, Vec<Map<String, Value>>)> {
        logs.iter().find_map(|(n, rows)| {
            let got: Vec<Map<String, Value>> = rows
                .iter()
                .filter(|r| r.get("trigger").and_then(Value::as_str) == Some(key))
                .cloned()
                .collect();
            (!got.is_empty()).then(|| (n.clone(), got))
        })
    };
    // the other features' logs (1.5 MB together, 2026-11-17) read only when the feature's own holds no record of a cited key
    if keys.iter().any(|k| hits(&logs, k).is_none()) {
        let mut others: Vec<_> = std::fs::read_dir(parent)
            .into_iter()
            .flatten()
            .flatten()
            .map(|e| e.path().join("arbiter.jsonl"))
            .filter(|p| *p != own && p.is_file())
            .collect();
        others.sort();
        logs.extend(others.iter().map(|p| (name(p), records(p))));
    }
    let mut out = head.to_owned();
    for key in &keys {
        let _ = write!(out, "## {key}\n\n");
        match hits(&logs, key) {
            Some((file, rows)) => {
                for row in &rows {
                    out.push_str(&shown(row, &file));
                    out.push('\n');
                }
            }
            None => {
                let _ = write!(
                    out,
                    "(no record - no `arbiter.jsonl` under `specs/` holds a ruling whose trigger is `{key}`)\n\n"
                );
            }
        }
    }
    out
}

#[cfg(test)]
mod tests;
