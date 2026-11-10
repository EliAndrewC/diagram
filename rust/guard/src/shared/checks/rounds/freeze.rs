//! The freeze on a page while its checks run, the reversal test and what a cascade counts (from `hm_checks.py`, split from `rounds.rs` at the file-scale bar).

use std::collections::BTreeSet;
use std::path::Path;

use serde_json::{json, Value};

use super::reply;
use super::text;
use super::{
    dispatches, falsy, git_stdout, has_subject, open_round, running, subject_of_path, t_of, APPLY,
    GEN, SIMILAR, STALE_S, WORD,
};

fn edits_of(state: &Value, subject: &str) -> Vec<(String, String, String)> {
    state
        .get("edits")
        .and_then(|m| m.get(subject))
        .and_then(Value::as_array)
        .into_iter()
        .flatten()
        .filter_map(|e| {
            let row = e.as_array()?;
            Some((
                row.first()?.as_str()?.to_owned(),
                row.get(1)?.as_str()?.to_owned(),
                row.get(2)?.as_str()?.to_owned(),
            ))
        })
        .collect()
}

fn proposed(state: &Value, subject: &str, old: &str, new: &str) -> bool {
    !old.is_empty()
        && edits_of(state, subject).iter().any(|(_, b_old, b_new)| {
            b_old.find(old).is_some_and(|i| {
                let head = &b_old[..i];
                b_new.starts_with(&format!("{head}{new}"))
            })
        })
}

/// Why an Edit to `path` is refused now (FR-003(b)), or "".
#[must_use]
pub fn edit_refusal(state: &Value, path: &str, old: &str, new: &str, now: f64) -> String {
    let s = subject_of_path(path);
    if s.is_empty() || open_round(state, &s, now).is_empty() {
        return String::new();
    }
    let live_now = running(state, &s, now);
    if !live_now.is_empty() {
        let names: BTreeSet<&str> = live_now.iter().map(|d| text(d, "check")).collect();
        let stale = live_now.iter().filter(|d| now - t_of(d) > STALE_S).count();
        let tail = if stale > 0 {
            format!(" ({stale} silent past 90 minutes: `make check-closed SUBJECT={s} REASON=...` closes it)")
        } else {
            String::new()
        };
        return format!(
            "{s} is frozen while its checks run ({}) - edit it once every check of the round has returned{tail} (feature 375 FR-003b)",
            names.into_iter().collect::<Vec<_>>().join(", ")
        );
    }
    if proposed(state, &s, old, new) {
        return String::new();
    }
    let blocks = edits_of(state, &s);
    if blocks.is_empty() {
        format!("{s}'s checks returned no edit to apply; answer them (`make record-checked`) before editing it (FR-003b)")
    } else {
        format!("{s}'s checks have returned, and this edit is none of the {} edit(s) they proposed - apply those (`make apply-edits REPLY=<the reply>`, or by hand), answer the checks, and make any other change after (FR-003b)", blocks.len())
    }
}

/// Why `make apply-edits FROM=<reply>` is refused now, or "".
#[must_use]
pub fn apply_refusal(state: &Value, command: &str, now: f64) -> String {
    let Ok(Some(m)) = APPLY.captures(command) else {
        return String::new();
    };
    let from = m[1].trim_matches(|c| c == '\'' || c == '"').to_owned();
    for (path, old, new) in reply::blocks(&reply::reply_file(&from)) {
        let s = subject_of_path(&path);
        if s.is_empty() || open_round(state, &s, now).is_empty() {
            continue;
        }
        if !running(state, &s, now).is_empty() {
            return edit_refusal(state, &path, &old, &new, now);
        }
        let listed = edits_of(state, &s)
            .iter()
            .any(|e| *e == (path.clone(), old.clone(), new.clone()));
        if !listed && !proposed(state, &s, &old, &new) {
            return format!("a block of this reply for {s} is not one its round's checks returned - apply only this round's replies (FR-003b)");
        }
    }
    String::new()
}

fn word_set(t: &str) -> BTreeSet<String> {
    WORD.find_iter(&t.to_lowercase())
        .flatten()
        .map(|m| m.as_str().to_owned())
        .collect()
}

fn shares(a: &BTreeSet<String>, b: &BTreeSet<String>, base: usize) -> bool {
    #[expect(
        clippy::cast_precision_loss,
        reason = "word counts of a page block are far below 2^52"
    )]
    let need = SIMILAR * base as f64;
    #[expect(
        clippy::cast_precision_loss,
        reason = "word counts of a page block are far below 2^52"
    )]
    let have = a.intersection(b).count() as f64;
    have >= need
}

/// A block of the latest version that is a block an earlier version had and a later one had dropped; its first words, or "".
#[must_use]
pub fn oscillation(versions: &[Vec<String>]) -> String {
    if versions.len() < 3 {
        return String::new();
    }
    let (last, prev) = (&versions[versions.len() - 1], &versions[versions.len() - 2]);
    for b in last {
        let wb = word_set(b);
        if prev.iter().any(|p| {
            let wp = word_set(p);
            shares(&wb, &wp, wp.len().max(1))
        }) {
            continue;
        }
        for (i, vi) in versions[..versions.len() - 2].iter().enumerate() {
            for a in vi {
                let wa = word_set(a);
                if wa.len() >= 5 && shares(&wa, &wb, wa.len()) {
                    let gone = versions[i + 1..versions.len() - 1]
                        .iter()
                        .any(|vj| !vj.iter().any(|c| shares(&wa, &word_set(c), wa.len())));
                    if gone {
                        return b.split_whitespace().take(12).collect::<Vec<_>>().join(" ");
                    }
                }
            }
        }
    }
    String::new()
}

/// The `origin/main` merge-base commit time of the clone; 0 where it cannot be had (`hm_checks.window_start`).
#[must_use]
pub fn window_start(root: &Path) -> f64 {
    let base = git_stdout(root, &["merge-base", "HEAD", "origin/main"]);
    if base.is_empty() {
        return 0.0;
    }
    git_stdout(root, &["show", "-s", "--format=%ct", &base])
        .parse()
        .unwrap_or(0.0)
}

/// The check dispatches made at or after `since`; a pre-write source-reader read is not counted.
#[must_use]
pub fn dispatches_since(state: &Value, since: f64) -> u64 {
    let n = dispatches(state)
        .iter()
        .filter(|d| t_of(d) >= since && !d.get("prewrite").is_some_and(|p| !falsy(Some(p))))
        .count();
    u64::try_from(n).unwrap_or(0)
}

/// Hand-written lines the clone's delta changed against the merge base; the cascade ratio's base (FR-010).
#[must_use]
pub fn changed_lines(root: &Path) -> u64 {
    let merge = git_stdout(root, &["merge-base", "HEAD", "origin/main"]);
    let base = if merge.is_empty() {
        git_stdout(root, &["rev-parse", "HEAD"])
    } else {
        merge
    };
    let mut total = 0;
    for raw in git_stdout(root, &["diff", "--numstat", &base]).lines() {
        let parts: Vec<&str> = raw.split('\t').collect();
        if parts.len() == 3 && !GEN.is_match(parts[2]).unwrap_or(false) {
            if let (Ok(a), Ok(b)) = (parts[0].parse::<u64>(), parts[1].parse::<u64>()) {
                total += a + b;
            }
        }
    }
    total
}

/// The `Close` answer: how many dispatches `close` closed and how many remain running.
pub struct Closed {
    pub closed: usize,
    pub still_running: usize,
}

/// `make check-closed`: close the checks on `subject` that went silent, or the one a session stopped itself. The state is saved by the caller.
pub fn close_dispatches(
    state: &mut Value,
    subject: &str,
    reason: &str,
    now: f64,
    agent: &str,
) -> Closed {
    let mut closed = 0;
    if let Some(ds) = state.get_mut("dispatches").and_then(Value::as_object_mut) {
        for d in ds.values_mut() {
            let silent = text(d, "state") == "running" && now - t_of(d) > STALE_S;
            let named =
                !agent.is_empty() && text(d, "aid") == agent && text(d, "state") != "answered";
            if has_subject(d, subject) && (silent || named) {
                d["state"] = json!("answered");
                d["closed"] = json!(reason);
                closed += 1;
            }
        }
    }
    Closed {
        closed,
        still_running: running(state, subject, now).len(),
    }
}
