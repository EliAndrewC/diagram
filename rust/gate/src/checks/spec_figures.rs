//! spec-lint's check 5: a measured figure is derived, not typed (feature 239 section C; feature 449 T066, from `spec_figures.py`). A
//! figure with a unit carries `m:<key>` in its paragraph, the key is in the feature's `measurements.json`, and the recorded value
//! appears in that paragraph, numerically (FR-009a). The reach is the operative sections, all of `research.md` and the Review history
//! (FR-009b); a backtick span names a figure rather than asserting it (FR-009c); a one-shot observation passes with its date and method
//! (FR-010); `varies` belongs to a timing (FR-011b), and a timing names its sample (FR-011e).
//!
//! THE ONE DEFINITION OF A FIGURE (spec D4): check 1, check 5, the plan lint and feature 240's reviewer precondition read this pattern,
//! so they cannot drift apart. It reads every touched spec, whatever its number: a cutoff at feature 239 was ruled NOT LEGITIMATE,
//! because the case that motivated the rule was a feature below it.

use std::path::{Path, PathBuf};
use std::sync::LazyLock;

use fancy_regex::{Captures, Regex};
use serde_json::Value;

use super::{blank_matches, py_repr};
pub(super) use super::{figure_source, FIGURE, ONE_SHOT};

const TIMING_UNITS: [&str; 6] = ["ms", "s", "min", "h", "%", "x"];
const OPERATIVE: [&str; 4] = [
    "summary",
    "functional requirements",
    "success criteria",
    "decisions recorded",
];
/// The shapes of check 5's own messages, so a test of checks 1 to 4 can set them aside by what they say.
const CHECK5_MARKS: [&str; 6] = [
    "carries no `m:<key>`",
    "is not in measurements.json",
    "which this paragraph does not state",
    "(FR-011b)",
    "(FR-011e)",
    "not valid JSON",
];

fn re(pattern: &str) -> Regex {
    Regex::new(pattern).unwrap_or_else(|e| unreachable!("{e}"))
}

static KEY: LazyLock<Regex> = LazyLock::new(|| re(r"\bm:([a-z0-9][a-z0-9-]*)"));
static SPAN: LazyLock<Regex> = LazyLock::new(|| re(r"`[^`\n]*`"));
static TOKEN: LazyLock<Regex> = LazyLock::new(|| re(r"(?<![\w\p{N}.])\d[\d,]*(?:\.\d+)?"));
static ROUND_LABEL: LazyLock<Regex> =
    LazyLock::new(|| re(r"(?i)\b(?:round \d+|this round)'s own run\b"));
static HEADING: LazyLock<Regex> = LazyLock::new(|| re(r"(?m)^(#{2,})\s+(.*?)\s*$"));
static BLOCK_BREAK: LazyLock<Regex> = LazyLock::new(|| re(r"\n\s*\n"));
static HEAD_LINE: LazyLock<Regex> = LazyLock::new(|| re(r"(?m)^#{1,6}\s.*$"));

pub(super) fn is_check5(message: &str) -> bool {
    CHECK5_MARKS.iter().any(|m| message.contains(m))
}

/// Every number a recorded value holds: the value itself, or each number nested in a table of them.
fn recorded_numbers(value: &Value) -> Vec<f64> {
    match value {
        Value::Number(n) => n.as_f64().into_iter().collect(),
        Value::String(s) => s.replace(',', "").trim().parse().into_iter().collect(),
        Value::Object(map) => map.values().flat_map(recorded_numbers).collect(),
        Value::Array(rows) => rows.iter().flat_map(recorded_numbers).collect(),
        _ => Vec::new(),
    }
}

/// FR-009a: some number token equals a recorded value, exactly or at the token's own precision.
fn appears(value: &Value, paragraph: &str) -> bool {
    let numbers = recorded_numbers(value);
    TOKEN.find_iter(paragraph).flatten().any(|raw| {
        let token = raw.as_str().replace(',', "");
        let places = token.split_once('.').map_or(0, |(_, d)| d.len());
        let wanted: f64 = token.parse().unwrap_or(f64::NAN);
        numbers
            .iter()
            .any(|n| format!("{n:.places$}").parse() == Ok(wanted))
    })
}

/// (file, first line, paragraph, section kind) of every paragraph this check reads.
fn paragraphs_in_scope(spec_dir: &Path) -> Vec<(PathBuf, usize, String, &'static str)> {
    let mut out = Vec::new();
    for (name, whole_file) in [("spec.md", false), ("research.md", true)] {
        let path = spec_dir.join(name);
        let Ok(text) = std::fs::read_to_string(&path) else {
            continue;
        };
        let mut blocks: Vec<&str> = Vec::new();
        let mut at = 0;
        for gap in BLOCK_BREAK.find_iter(&text).flatten() {
            blocks.extend([&text[at..gap.start()], gap.as_str()]);
            at = gap.end();
        }
        blocks.push(&text[at..]);
        let (mut line, mut top, mut sub) = (1, String::new(), String::new());
        for block in blocks {
            if let Ok(Some(head)) = HEADING.captures(block) {
                let title = head[2].to_lowercase();
                if head[1].len() <= 2 {
                    top = title;
                    sub.clear();
                } else {
                    sub = title;
                }
            }
            let kind = section_kind(whole_file, &top, &sub);
            if !kind.is_empty() && !block.trim().is_empty() {
                out.push((path.clone(), line, block.to_owned(), kind));
            }
            line += block.matches('\n').count();
        }
    }
    out
}

fn section_kind(whole_file: bool, top: &str, sub: &str) -> &'static str {
    let operative = |name: &str| OPERATIVE.iter().any(|o| name.starts_with(o));
    if whole_file {
        "research"
    } else if top.starts_with("review history") {
        "review"
    } else if operative(top) || operative(sub) || (top == "requirements" && sub.is_empty()) {
        "operative"
    } else {
        ""
    }
}

fn check_paragraphs(spec_dir: &Path, recorded: &Value) -> Vec<String> {
    let mut bad = Vec::new();
    for (path, line, para, kind) in paragraphs_in_scope(spec_dir) {
        let path = path.display();
        let visible = blank_matches(&HEAD_LINE, &blank_matches(&SPAN, &para));
        let first = FIGURE.find(&visible).ok().flatten();
        let Some(first) = first else {
            continue;
        };
        if ONE_SHOT.is_match(&para).unwrap_or(false) && para.to_lowercase().contains("method") {
            continue;
        }
        let keys: Vec<String> = KEY
            .captures_iter(&para)
            .flatten()
            .map(|c| key_of(&c))
            .collect();
        if keys.is_empty() {
            if !(kind == "review" && ROUND_LABEL.is_match(&para).unwrap_or(false)) {
                let round = if kind == "review" {
                    " or as a round's own run"
                } else {
                    ""
                };
                bad.push(format!("{path}:{line}: the figure {} carries no `m:<key>` - record it with the harness that measured it, or label it as a one-shot observation (date and method){round}", py_repr(&Value::from(first.as_str().trim()))));
            }
            continue;
        }
        for key in keys {
            match recorded.get(&key) {
                None => bad.push(format!(
                    "{path}:{line}: `m:{key}` is not in measurements.json"
                )),
                Some(entry) => {
                    let value = entry.get("value").unwrap_or(&Value::Null);
                    if !appears(value, &visible) {
                        bad.push(format!("{path}:{line}: `m:{key}` records {}, which this paragraph does not state", py_repr(value)));
                    }
                }
            }
        }
    }
    bad
}

fn key_of(c: &Captures<'_>) -> String {
    c[1].to_owned()
}

fn truthy(value: Option<&Value>) -> bool {
    match value {
        None | Some(Value::Null | Value::Bool(false)) => false,
        Some(Value::Number(n)) => n.as_f64() != Some(0.0),
        Some(Value::String(s)) => !s.is_empty(),
        Some(Value::Array(a)) => !a.is_empty(),
        Some(Value::Object(o)) => !o.is_empty(),
        Some(Value::Bool(true)) => true,
    }
}

/// FR-011b and FR-011e, on the measurements file itself.
fn check_entries(spec_dir: &Path, recorded: &Value) -> Vec<String> {
    let where_ = spec_dir.join("measurements.json");
    let where_ = where_.display();
    let mut rows: Vec<(&String, &Value)> = recorded.as_object().into_iter().flatten().collect();
    rows.sort_by_key(|(k, _)| *k);
    let mut bad = Vec::new();
    for (key, entry) in rows.into_iter().filter(|(_, e)| truthy(e.get("varies"))) {
        let unit = entry.get("unit").unwrap_or(&Value::Null);
        if !TIMING_UNITS.iter().any(|u| unit == *u) {
            bad.push(format!("{where_}: `{key}` carries `varies` but its unit {} counts things - a count repeats exactly or the thing counted changed (FR-011b)", py_repr(unit)));
        }
        if !truthy(entry.get("quantity")) {
            bad.push(format!("{where_}: `{key}` is a timing with no `quantity` naming the sample it measured (FR-011e)"));
        }
    }
    bad
}

pub(super) fn check_measured_figures(spec_dir: &Path) -> Vec<String> {
    let path = spec_dir.join("measurements.json");
    let recorded = match std::fs::read_to_string(&path) {
        Err(_) => Value::Object(serde_json::Map::new()),
        Ok(text) => match serde_json::from_str(&text) {
            Ok(value) => value,
            Err(e) => return vec![format!("{}: not valid JSON ({e})", path.display())],
        },
    };
    let mut bad = check_paragraphs(spec_dir, &recorded);
    bad.extend(check_entries(spec_dir, &recorded));
    bad
}

#[cfg(test)]
mod tests;
