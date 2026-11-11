//! The EARLIER ROUNDS of a record or pop-up check, handed to its next round in the bundle (from `earlier_rounds.py`, feature 393, the GM 2026-10-18: "give each reviewer the earlier rounds' verdicts and reasons to prevent reviewer loops"). Reads the check state and the rulings and never writes them.

use std::fmt::Write as _;
use std::path::Path;
use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_guard::guards::event_log_hooks::verdict_of;
use l7r_guard::shared::checks::arbiter as core;
use l7r_guard::shared::checks::rounds::{notes_of_manifest, subjects_of_manifest, PAGE_CHECKS};
use l7r_guard::shared::checks::{load, reply, state_path};
use serde_json::Value;

use crate::arbiter::bundle::marks::{last_edits, mark_rounds, reply_of, subject_files};
use crate::record::bundle::{dash_runs, pyre, write};
use crate::record::repo::{git, Fail};

pub(crate) const HEAD: &str = "## Earlier rounds (feature 393)";
const DIR: &str = "earlier";
const INTRO: &str = "Earlier rounds of this check on this subject in this feature, oldest first, with the round arbiter's rulings; each round's whole reply is the file named under it. What to do with them is your contract's **Earlier rounds (feature 393)** paragraph.";

static OWED: LazyLock<Regex> = LazyLock::new(|| pyre(r"(?m)^owed-checks: (.+)$"));

/// When the active feature began (its `spec.md`'s first commit), or 0.0.
fn feature_start(root: &Path) -> f64 {
    let Some(d) = core::feature_dir(root, "") else {
        return 0.0;
    };
    let spec = d.join("spec.md");
    let log = git(
        root,
        &[
            "log",
            "--diff-filter=A",
            "--format=%ct",
            "--",
            &spec.to_string_lossy(),
        ],
    );
    log.split_whitespace()
        .filter(|x| x.chars().all(|c| c.is_ascii_digit()))
        .filter_map(|x| x.parse::<f64>().ok())
        .reduce(f64::min)
        .unwrap_or(0.0)
}

fn num(v: &Value, key: &str) -> f64 {
    v.get(key).and_then(Value::as_f64).unwrap_or(0.0)
}

fn strs(v: &Value, key: &str) -> Vec<String> {
    v.get(key)
        .and_then(Value::as_array)
        .map(|a| {
            a.iter()
                .filter_map(Value::as_str)
                .map(str::to_owned)
                .collect()
        })
        .unwrap_or_default()
}

/// The dispatches of the check state, oldest first.
pub(crate) fn dispatches(state: &Value) -> Vec<&Value> {
    let mut all: Vec<&Value> = state
        .get("dispatches")
        .and_then(Value::as_object)
        .map(|m| m.values().collect())
        .unwrap_or_default();
    all.sort_by(|a, b| num(a, "t").total_cmp(&num(b, "t")));
    all
}

/// The returned dispatches of `check` on `subject` since `since`, oldest first; a note-scoped bundle's only where they read one of its notes or the page.
fn rounds<'a>(
    state: &'a Value,
    check: &str,
    subject: &str,
    since: f64,
    notes: &[String],
) -> Vec<&'a Value> {
    dispatches(state)
        .into_iter()
        .filter(|v| {
            v.get("check").and_then(Value::as_str) == Some(check)
                && strs(v, "subjects").iter().any(|s| s == subject)
                && num(v, "t") >= since
                && !matches!(
                    v.get("state").and_then(Value::as_str),
                    Some("pending" | "running")
                )
        })
        .filter(|v| {
            let read = v.get("notes").and_then(Value::as_array);
            notes.is_empty()
                || read.is_none_or(|r| {
                    r.is_empty()
                        || r.iter()
                            .filter_map(Value::as_str)
                            .any(|n| notes.iter().any(|k| k == n))
                })
        })
        .collect()
}

fn name(check: &str, subject: &str, i: usize) -> String {
    format!(
        "{DIR}/{check}-{}-round-{i}.md",
        dash_runs(subject, char::is_ascii_alphanumeric)
    )
}

fn ruling_lines(
    rulings: &serde_json::Map<String, Value>,
    check: &str,
    subject: &str,
) -> Vec<String> {
    let prefix = format!("round:{check}|{subject}@");
    let mut keyed: Vec<(&String, &Value)> = rulings.iter().collect();
    keyed.sort_by_key(|(t, _)| core::round_no(t));
    keyed
        .into_iter()
        .filter(|(t, _)| t.starts_with(&prefix))
        .map(|(t, r)| {
            let text = |k: &str| r.get(k).map(core::py_text);
            let mut line = format!(
                "- the round arbiter on `{t}`: **{}** - {}",
                text("ruling").unwrap_or_else(|| "?".to_owned()),
                text("why").unwrap_or_else(|| "(no reason recorded)".to_owned())
            );
            if let Some(what) = r
                .get("what")
                .filter(|w| !l7r_guard::shared::checks::falsy(Some(w)))
            {
                let _ = write!(
                    line,
                    " | what the next round looks at: {}",
                    core::py_text(what)
                );
            }
            line
        })
        .collect()
}

/// The lines for one check on one subject, its replies written beside the MANIFEST; none with no earlier round or ruling.
#[expect(clippy::too_many_arguments, reason = "the Python's own parameters")]
fn unit_section(
    root: &Path,
    out: &Path,
    state: &Value,
    rulings: &serde_json::Map<String, Value>,
    check: &str,
    subject: &str,
    since: f64,
    notes: &[String],
) -> Result<Vec<String>, Fail> {
    let mine = rounds(state, check, subject, since, notes);
    let ruled = ruling_lines(rulings, check, subject);
    if mine.is_empty() && ruled.is_empty() {
        return Ok(Vec::new());
    }
    let replies: Vec<String> = mine.iter().map(|v| reply_of(v)).collect();
    let others: Vec<(String, String)> = state
        .get("dispatches")
        .and_then(Value::as_object)
        .into_iter()
        .flat_map(serde_json::Map::values)
        .filter(|v| {
            strs(v, "subjects").iter().any(|s| s == subject)
                && v.get("check").and_then(Value::as_str) != Some(check)
                && num(v, "t") >= since
        })
        .flat_map(|v| {
            reply::blocks(&reply_of(v))
                .into_iter()
                .map(|(_, o, n)| (o, n))
        })
        .collect();
    let files = subject_files(root, subject);
    let mut lines = vec![format!("### {check} on {subject}"), String::new()];
    for (i, (r, marked)) in replies
        .iter()
        .zip(mark_rounds(&replies, &others))
        .enumerate()
    {
        let i = i + 1;
        if r.is_empty() {
            lines.push(format!("**Round {i}** - no reply kept"));
        } else {
            let v = verdict_of(r);
            lines.push(format!(
                "**Round {i}** - verdict: {}",
                if v.is_empty() { "none read" } else { &v }
            ));
            write(&out.join(name(check, subject, i)), r)?;
            lines.push(format!("The whole reply: `{}`.", name(check, subject, i)));
        }
        lines.extend(marked.iter().map(|(m, f)| format!("- {m}: {f}")));
        if !r.is_empty() {
            lines.extend(last_edits(root, r, &files));
        }
        lines.push(String::new());
    }
    if !ruled.is_empty() {
        lines.push("Rulings:".to_owned());
        lines.extend(ruled);
        lines.push(String::new());
    }
    Ok(lines)
}

/// The MANIFEST's Earlier rounds section for the checks and subjects `manifest` owes, or "".
pub(crate) fn section(root: &Path, out: &Path, manifest: &str) -> Result<String, Fail> {
    let owed = OWED
        .captures(manifest)
        .ok()
        .flatten()
        .and_then(|c| c.get(1))
        .map_or("", |m| m.as_str());
    let checks: Vec<String> = owed
        .replace(',', " ")
        .split_whitespace()
        .filter(|c| PAGE_CHECKS.contains(c))
        .map(str::to_owned)
        .collect();
    let subjects = subjects_of_manifest(manifest);
    let path = state_path(&root.to_string_lossy());
    let Some(path) = path.filter(|p| p.is_file()) else {
        return Ok(String::new());
    };
    if checks.is_empty() || subjects.is_empty() {
        return Ok(String::new());
    }
    let (state, rulings, since) = (load(&path), core::rulings(root, ""), feature_start(root));
    let notes: Vec<String> = notes_of_manifest(manifest).into_iter().collect();
    let mut body = Vec::new();
    for c in &checks {
        for s in &subjects {
            body.extend(unit_section(
                root, out, &state, &rulings, c, s, since, &notes,
            )?);
        }
    }
    Ok(if body.is_empty() {
        String::new()
    } else {
        format!("\n{HEAD}\n\n{INTRO}\n\n{}", body.join("\n"))
    })
}

#[cfg(test)]
mod tests;
