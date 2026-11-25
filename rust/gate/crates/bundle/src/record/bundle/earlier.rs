//! The EARLIER ROUNDS of a record or pop-up check, handed to its next round in the bundle (from `earlier_rounds.py`, feature 393, the GM 2026-10-18: "give each reviewer the earlier rounds' verdicts and reasons to prevent reviewer loops"). Reads the check state and the rulings and never writes them; it keeps what each round was bundled, so the next round is handed the change since (451 T189).

use std::fmt::Write as _;
use std::path::Path;
use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_shared::checks::arbiter as core;
use l7r_shared::checks::rounds::{notes_of_manifest, subjects_of_manifest, PAGE_CHECKS};
use l7r_shared::checks::{load, reply, state_path};
use l7r_shared::env::Rooted;
use l7r_shared::guards::event_log_hooks::verdict_of;
use serde_json::Value;

use crate::arbiter::bundle::marks::{last_edits, mark_rounds, reply_of, subject_files};
use crate::record::bundle::{dash_runs, pyre, write};
use crate::record::repo::{git, Fail};

pub const HEAD: &str = "## Earlier rounds (feature 393)";
const DIR: &str = "earlier";
const INTRO: &str = "Earlier rounds of this check on this subject in this feature, oldest first, with the round arbiter's rulings; each round's whole reply is the file named under it. What to do with them is your contract's **Earlier rounds (feature 393)** paragraph.";

static OWED: LazyLock<Regex> = LazyLock::new(|| pyre(r"(?m)^owed-checks: (.+)$"));

/// When the active feature began (its `spec.md`'s first commit), or 0.0.
fn feature_start(root: &Rooted) -> f64 {
    let Some(d) = core::feature_dir_in(root, "", root.reader()) else {
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
pub fn dispatches(state: &Value) -> Vec<&Value> {
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
                .filter(|w| !l7r_shared::checks::falsy(Some(w)))
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

const CHANGE_INTRO: &str = "This is a later round: judge ONLY whether this change made something wrong. Each pair is a run of lines changed since that round was bundled - by an EDIT or by hand - its text before and after; the whole unit is in the bundle for context. Re-open nothing the change did not touch - a finding on other text goes under OUTSIDE THE CHANGE - and raise no wording preference against words a round settled (451 T189, a rule the GM approved 2026-11-23).";

/// Where what each round of `check` on `subject` was bundled is kept (451 T189): `<git dir>/record-checks/seen/<check>-<subject>.json`,
/// `{"<round>": {"<file>": "<text>"}}`, the bundle for round `n` written under `n`, a regeneration before its dispatch overwriting
/// it, and the rounds before the last kept dropped.
fn seen_path(root: &Path, check: &str, subject: &str) -> std::path::PathBuf {
    // `section_in` reads the check state first, so its git directory is there whenever this is asked
    let state = state_path(&root.to_string_lossy()).unwrap_or_default();
    let name = dash_runs(&format!("{check}-{subject}"), char::is_ascii_alphanumeric);
    state
        .with_file_name("record-checks")
        .join("seen")
        .join(format!("{name}.json"))
}

/// Each file's text as round `n` was bundled, where it was kept.
fn seen_at(
    root: &Path,
    check: &str,
    subject: &str,
    n: usize,
) -> Option<serde_json::Map<String, Value>> {
    let kept = load(&seen_path(root, check, subject));
    kept.get(n.to_string()).and_then(Value::as_object).cloned()
}

/// Keep `files` as the bundle for round `n` now writes them, dropping every round before `n - 1`.
fn keep_seen(
    root: &Path,
    check: &str,
    subject: &str,
    n: usize,
    files: &[String],
) -> Result<(), Fail> {
    let path = seen_path(root, check, subject);
    let mut kept = load(&path).as_object().cloned().unwrap_or_default();
    kept.retain(|k, _| k.parse::<usize>().is_ok_and(|r| r + 1 >= n));
    let now: serde_json::Map<String, Value> = files
        .iter()
        .filter_map(|f| {
            std::fs::read_to_string(root.join(f))
                .ok()
                .map(|t| (f.clone(), Value::from(t)))
        })
        .collect();
    kept.insert(n.to_string(), Value::Object(now));
    write(&path, &Value::Object(kept).to_string())
}

/// The pairs of what changed in `files` since `was` (each file's text as the last round was bundled): every run of lines that differs,
/// whoever changed it - an EDIT or a hand edit (451 T189).
///
/// A file the last round was not bundled - a split's target (451 T196) - is diffed against the pages whose pointers reach it as they
/// were then: a line moved verbatim is no change, a line moved with an edit pairs with its old self, and what left those pages is
/// theirs to show, so no deletion is shown here.
fn pairs_since(root: &Path, was: &serde_json::Map<String, Value>, files: &[String]) -> Vec<String> {
    let read = |f: &str| std::fs::read_to_string(root.join(f)).unwrap_or_default();
    let mut out = Vec::new();
    for f in files {
        let (then, arrived) = match was.get(f).and_then(Value::as_str) {
            Some(t) => (t.to_owned(), false),
            None => (
                files
                    .iter()
                    .filter(|s| {
                        l7r_gate_owed::record::triage::change::pointer_targets(&read(s)).contains(f)
                    })
                    .filter_map(|s| was.get(s).and_then(Value::as_str))
                    .collect::<Vec<_>>()
                    .join("\n"),
                true,
            ),
        };
        let now = read(f);
        let (a, b): (Vec<&str>, Vec<&str>) = (then.lines().collect(), now.lines().collect());
        out.extend(crate::difflib::paired(f, &a, &b, !arrived));
    }
    out
}

/// The change section for round `n`'s successor, none where nothing changed.
fn change_lines(n: usize, pairs: Vec<String>) -> Vec<String> {
    if pairs.is_empty() {
        return Vec::new();
    }
    let mut lines = vec![
        format!("### The change since round {n} (451 T189)"),
        String::new(),
        CHANGE_INTRO.to_owned(),
        String::new(),
    ];
    lines.extend(pairs);
    lines.push(String::new());
    lines
}

/// The lines for one check on one subject, its replies written beside the MANIFEST; none with no earlier round or ruling. And whether
/// it is a later round whose last round was bundled with no snapshot kept, so it reads the whole unit (451 T249).
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
) -> Result<(Vec<String>, bool), Fail> {
    let mine = rounds(state, check, subject, since, notes);
    let ruled = ruling_lines(rulings, check, subject);
    if mine.is_empty() && ruled.is_empty() {
        return Ok((Vec::new(), false));
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
    // what the last round was bundled, where it was kept, against the files now: every change since it, by an EDIT or by hand; a
    // subject whose last round was bundled before the keeping gets none, and its round reads the whole unit, unscoped as before
    let n = mine.len();
    let was = seen_at(root, check, subject, n);
    let unscoped = n > 0 && was.is_none();
    if let Some(was) = was {
        lines.extend(change_lines(n, pairs_since(root, &was, &files)));
    }
    if !ruled.is_empty() {
        lines.push("Rulings:".to_owned());
        lines.extend(ruled);
        lines.push(String::new());
    }
    Ok((lines, unscoped))
}

/// The MANIFEST's Earlier rounds section for the checks and subjects `manifest` owes, or "".
///
/// # Errors
///
/// Where what it reads, writes or runs fails: the error says which and why.
pub fn section(root: &Path, out: &Path, manifest: &str) -> Result<String, Fail> {
    section_in(&Rooted::process(root), out, manifest)
}

/// [`section`] with the root's environment carried (feature 451 T38): the active feature and its rulings read through it.
///
/// # Errors
///
/// Where what it reads or writes fails: the error says which and why.
pub fn section_in(root: &Rooted, out: &Path, manifest: &str) -> Result<String, Fail> {
    Ok(parts_in(root, out, manifest)?.0)
}

/// A MANIFEST `text` with its Earlier rounds section after it (feature 393), and, where a later round's last round kept no snapshot,
/// one line under its title saying the round judges the whole unit (451 T249). Measured 2026-11-25 (451 T232): the guest-quarters
/// round of 2026-11-24 10:56 had no change section, its last round bundled before 451 T189 kept one, and with nothing saying so it
/// judged only "the bullet that changed", missing the alcove gap the next round found - against the Earlier rounds paragraph, which
/// says a round with no change section judges as a first round.
///
/// # Errors
///
/// Where what it reads or writes fails: the error says which and why.
pub fn headed_in(root: &Rooted, out: &Path, text: &str) -> Result<String, Fail> {
    let (section, unscoped) = parts_in(root, out, text)?;
    if unscoped.is_empty() {
        return Ok(format!("{text}{section}"));
    }
    let line = format!("**Scope: the whole unit (451 T249).** No snapshot was kept of what the last round of {} was bundled (a round bundled before 451 T189), so this bundle has no change section: judge the whole unit, every block, as in a first round - not only what an earlier round named.", unscoped.join(", "));
    // under the title, so the check meets its scope before anything it reads
    let (title, rest) = text.split_once('\n').unwrap_or((text, ""));
    let rest = rest.strip_prefix('\n').unwrap_or(rest);
    Ok(format!("{title}\n\n{line}\n\n{rest}{section}"))
}

/// [`section_in`] and the later rounds whose last bundle kept no snapshot.
fn parts_in(root: &Rooted, out: &Path, manifest: &str) -> Result<(String, Vec<String>), Fail> {
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
        return Ok((String::new(), Vec::new()));
    };
    if checks.is_empty() || subjects.is_empty() {
        return Ok((String::new(), Vec::new()));
    }
    let (state, rulings, since) = (
        load(&path),
        core::rulings_in(root, "", root.reader()),
        feature_start(root),
    );
    let notes: Vec<String> = notes_of_manifest(manifest).into_iter().collect();
    let (mut body, mut unscoped) = (Vec::new(), Vec::new());
    for c in &checks {
        for s in &subjects {
            let (lines, whole) = unit_section(root, out, &state, &rulings, c, s, since, &notes)?;
            body.extend(lines);
            if whole {
                unscoped.push(format!("{c} on {s}"));
            }
            // this bundle is the next round's: what it was bundled is kept for the round after (451 T189)
            let n = rounds(&state, c, s, since, &notes).len() + 1;
            keep_seen(root, c, s, n, &subject_files(root, s))?;
        }
    }
    let section = if body.is_empty() {
        String::new()
    } else {
        format!("\n{HEAD}\n\n{INTRO}\n\n{}", body.join("\n"))
    };
    Ok((section, unscoped))
}

#[cfg(test)]
mod tests;
