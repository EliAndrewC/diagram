//! A repeat round's cap (feature 375 FR-010): where a unit's rounds are ruled, what a later batch restarts (451 T248), and the
//! refusal; split from `rounds.rs` for file-scale (451 T248).

use std::path::Path;

use serde_json::{json, Value};

use super::super::{arbiter, falsy, git_stdout, map_mut, text};
use super::{open_round, subject_of_path, subject_of_unit, Dispatch, ROUND_CAP, UNIT_FP};

/// The feature directory a unit's rounds are filed and ruled in: the feature its count began in (`round_home`, else the state's), so
/// a ruling is read there whatever feature is active (451 T227); None where this clone has no such directory.
fn home_dir(state: &Value, root: &Path, unit: &str) -> Option<std::path::PathBuf> {
    let home = state
        .get("round_home")
        .and_then(|m| m.get(unit))
        .and_then(Value::as_str)
        .unwrap_or_else(|| text(state, "feature"));
    let d = root.join("specs").join(home);
    (!home.is_empty() && d.is_dir()).then_some(d)
}

/// The batch a round is counted in: the `origin/main` the clone stands on.
#[must_use]
pub fn batch_of(root: Option<&Path>) -> String {
    root.map_or_else(String::new, |r| {
        git_stdout(r, &["rev-parse", "origin/main"])
    })
}

/// Whether a dispatch in `batch` owes `unit` a fresh count: its last round counted under another `origin/main`, AND its subject
/// itself moved upstream since (`moved_upstream`). The batch rule (c5db336fd3, the round arbiter on
/// round:modal-depiction|modal:hamlet/woodland-commons@3) restarted on any move of `origin/main`; with several sessions landing a
/// third round in one batch was rare and the cap seldom fired (451 T248: record-format on 0097, 2026-11-24, two batches ten moves
/// apart, the page moved between only by the round's own edits landing).
fn new_cause(state: &Value, root: &Path, unit: &str, batch: &str) -> bool {
    let seen = state
        .get("round_batch")
        .and_then(|m| m.get(unit))
        .and_then(Value::as_str)
        .unwrap_or("");
    let subject = unit.split_once('|').map_or("", |(_, s)| s);
    !seen.is_empty()
        && !batch.is_empty()
        && seen != batch
        && moved_upstream(root, subject, seen, batch)
}

/// Whether `subject` itself moved upstream between batches `from` and `to`, not by this clone's own landing: a move of
/// `origin/main` that is not this clone's push (`update by push` in the ref's reflog, shared by every worktree of the clone; a
/// fetch, a pull or any other entry is another session's work) changed a file of the subject. Measured 2026-11-25 on the
/// coordinating clone's last 150 entries: 147 pushes and 3 fetches, no push carrying a commit made elsewhere. Where the reflog
/// does not reach `from` (expired, or no remote tracking log), any change of the subject between the two counts, whoever made it;
/// a `from` git cannot read moves nothing, so the cap holds and the round arbiter rules.
fn moved_upstream(root: &Path, subject: &str, from: &str, to: &str) -> bool {
    let common = git_stdout(root, &["rev-parse", "--git-common-dir"]);
    let log = root
        .join(if common.is_empty() { ".git" } else { &common })
        .join("logs/refs/remotes/origin/main");
    let moves: Vec<(String, String, bool)> = std::fs::read_to_string(log)
        .unwrap_or_default()
        .lines()
        .filter_map(|l| {
            let (head, why) = l.split_once('\t')?;
            let mut ids = head.split_whitespace();
            Some((
                ids.next()?.to_owned(),
                ids.next()?.to_owned(),
                why.starts_with("update by push"),
            ))
        })
        .collect();
    let changes = |a: &str, b: &str| {
        git_stdout(root, &["diff", "--name-only", a, b])
            .lines()
            .any(|p| subject_of_path(p) == subject)
    };
    moves
        .iter()
        .rposition(|(_, new, _)| new == from)
        .map_or_else(
            || changes(from, to),
            |at| {
                moves[at + 1..]
                    .iter()
                    .any(|(old, new, ours)| !ours && changes(old, new))
            },
        )
}

/// Whether the record store says every unit the bundle carries on `subject` is answered at its fingerprint; else the fingerprint of the first that is not.
fn moved_since_answer(root: &Path, text_of: &str, subject: &str) -> String {
    // `shared::env`: a test reads its own environment, never a session's export (feature 451 T32)
    let store = record_store(root, crate::env::opt("RECORD_CHECKS_DIR").as_deref());
    UNIT_FP
        .captures_iter(text_of)
        .map_while(Result::ok)
        .find(|c| {
            let slug = &c[1];
            let tail = slug.split_once(':').map_or("", |(_, t)| t);
            subject_of_unit(tail) == subject && !answered(&store, slug, &c[2])
        })
        .map_or_else(String::new, |c| c[2].to_owned())
}

/// Where the answer records live: `RECORD_CHECKS_DIR` (a test's throwaway store), else the clone's git dir.
pub(super) fn record_store(root: &Path, given: Option<&str>) -> std::path::PathBuf {
    if let Some(dir) = given.filter(|d| !d.is_empty()) {
        return dir.into();
    }
    let common = git_stdout(root, &["rev-parse", "--git-common-dir"]);
    let path = Path::new(if common.is_empty() { ".git" } else { &common });
    root.join(path).join("record-checks")
}

/// `urllib.parse.quote(slug, safe="")`.
fn quoted(slug: &str) -> String {
    slug.bytes()
        .map(|b| {
            if b.is_ascii_alphanumeric() || b"_.-~".contains(&b) {
                char::from(b).to_string()
            } else {
                format!("%{b:02X}")
            }
        })
        .collect()
}

fn answered(store: &Path, slug: &str, fp: &str) -> bool {
    let rec: Value = std::fs::read_to_string(store.join(format!("{}.json", quoted(slug))))
        .ok()
        .and_then(|t| serde_json::from_str(&t).ok())
        .unwrap_or(Value::Null);
    fp == text(&rec, "fingerprint")
        || rec
            .get("answered")
            .and_then(Value::as_array)
            .is_some_and(|a| a.iter().any(|x| x.as_str() == Some(fp)))
}

pub(super) fn cap_refusal(
    state: &mut Value,
    ask: &Dispatch,
    root: &Path,
    s: &str,
    n: u64,
) -> String {
    let unit = format!("{}|{s}", ask.check);
    let prefix = format!("round:{unit}@");
    let home = home_dir(state, root, &unit);
    let rulings = home
        .as_deref()
        .map_or_else(|| arbiter::rulings(root, &prefix), arbiter::rulings_of);
    let shut = arbiter::closed_of(&rulings, &prefix, None);
    let moved = if shut.is_empty() {
        String::new()
    } else {
        moved_since_answer(root, ask.text, s)
    };
    if !shut.is_empty() && moved.is_empty() {
        return format!("the round arbiter closed {unit} ({shut}) - what is left is filed; the session does not re-ask (FR-011)");
    }
    let base_has_moved = map_mut(state, "rebased")
        .get(&unit)
        .is_some_and(|b| text(b, "fp") == moved);
    if !moved.is_empty() && !base_has_moved {
        map_mut(state, "rebased").insert(unit.clone(), json!({"fp": moved, "n": n}));
    }
    let batch = batch_of(Some(root));
    if open_round(state, s, ask.now).is_empty() && new_cause(state, root, &unit, &batch) {
        map_mut(state, "rebased").insert(unit.clone(), json!({"fp": batch, "n": n, "cause": true}));
        map_mut(state, "round_batch").insert(unit.clone(), json!(batch));
    }
    let rebased = state
        .get("rebased")
        .and_then(|b| b.get(&unit))
        .cloned()
        .unwrap_or(Value::Null);
    let cause = !falsy(rebased.get("cause"));
    let n0 = if !shut.is_empty() || cause {
        rebased.get("n").and_then(Value::as_u64).unwrap_or(0)
    } else {
        0
    };
    let cap = n0 + ROUND_CAP + arbiter::continues_of(&rulings, &prefix, n0);
    if n >= cap {
        let trigger = format!("round:{unit}@{}", n + 1);
        let detail = format!("round {} of {} on {s}", n + 1, ask.check);
        let _ = match home.as_deref() {
            Some(h) => arbiter::trip_under(
                root,
                h,
                &trigger,
                ("round", &unit, &detail),
                &json!(ask.now),
            ),
            None => arbiter::trip(root, &trigger, "round", &unit, &detail, &json!(ask.now), ""),
        };
        return format!(
            "round {} of `{}` on {s} passes its cap of {cap} - {}",
            n + 1,
            ask.check,
            arbiter::refusal(&[format!("round:{unit}@{}", n + 1)], Some(root))
        );
    }
    String::new()
}
