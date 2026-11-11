//! A glyph check is DUE on the feature's hour, not on each occasion (feature 375 amendments 9 and 10, the GM 2026-10-12: "every
//! feature which takes longer than 1 hour to implement is 'due' to run it once after every hour"; ported from `review_owed.py`,
//! feature 449 T89). The clock is `<git dir>/glyph-clock.json`, `{<feature>: {"batch_at", "batch", "reopened", ...}}`; the push's
//! refusal marks the work landing (`glyph-landing`); the pair guard's dispatches are `pairing-state.json`'s `dispatched`.

use std::collections::BTreeMap;
use std::path::{Path, PathBuf};
use std::sync::Mutex;

use serde_json::{json, Map, Value};

use super::owed::{all_owed, Unit};
use super::{as_float, git, gitdir, int_of, iso_seconds, local_time, now, read_object, write_json};

/// An hour of the feature's time.
pub const GLYPH_HOUR_S: f64 = 3600.0;
/// The clock, in the git dir.
pub const CLOCK: &str = "glyph-clock.json";
/// `{"feature", "at"}`: the push refused for an unanswered glyph unit.
const LANDING: &str = "glyph-landing";
/// The pair guard's `dispatched[<slug>].at`.
pub const PAIRING: &str = "pairing-state.json";
/// How far back the reopening is looked for (feature 375 amendment 10: no feature directory had more than 57 commits in an hour).
const REOPEN_WALK: usize = 200;
/// The states `make speckit-todo` reads as closed.
const CLOSED: [&str; 2] = ["closed", "done - GM review pending"];

fn nowhere() -> PathBuf {
    PathBuf::from("/nonexistent")
}

/// Each feature directory's state, asked of `speckit-todo.py --state` once a run (`ask:449-T89-reviews`).
static STATES: Mutex<BTreeMap<PathBuf, String>> = Mutex::new(BTreeMap::new());

fn speckit_state(root: &Path, dir: &Path) -> String {
    if let Some(s) = STATES.lock().ok().and_then(|m| m.get(dir).cloned()) {
        return s;
    }
    let tool = crate::record::repo::tree_of(root).join("scripts/speckit-todo.py");
    // from `/`, outside any repository: the tool's run record (`usage_log`) is the landing's holding check's, and the Python asked
    // this in-process, recording nothing
    let said = std::process::Command::new("python3")
        .arg(&tool)
        .arg("--state")
        .arg(std::path::absolute(dir).unwrap_or(dir.to_path_buf()))
        .current_dir("/")
        .output()
        .map(|o| String::from_utf8_lossy(&o.stdout).trim().to_owned())
        .unwrap_or_default();
    if let Ok(mut m) = STATES.lock() {
        m.insert(dir.to_path_buf(), said.clone());
    }
    said
}

/// The feature whose hour a glyph check keeps, or "" (D54): `.specify/feature.json` names one, it exists, and `make speckit-todo`
/// does not read it closed.
#[must_use]
pub fn active_feature(root: &Path) -> String {
    let Some(d) = l7r_guard::shared::checks::arbiter::feature_dir(root, "") else {
        return String::new();
    };
    if !d.join("spec.md").is_file() || CLOSED.contains(&speckit_state(root, &d).as_str()) {
        return String::new();
    }
    d.file_name()
        .map(|n| n.to_string_lossy().into_owned())
        .unwrap_or_default()
}

/// When the feature began in this clone: the first event of `<git dir>/l7r-events/<feature>.jsonl`, or None.
#[must_use]
pub fn first_event(root: &Path, feature: &str) -> Option<f64> {
    let path = gitdir(root)?
        .join("l7r-events")
        .join(format!("{feature}.jsonl"));
    let text = std::fs::read_to_string(path).ok()?;
    let first: Value =
        serde_json::from_str(text.split_inclusive('\n').next().unwrap_or("")).ok()?;
    iso_seconds(first.get("t"))
}

/// When the feature was last REOPENED (feature 375 amendment 10, FR-042): the newest commit to `specs/<feature>` after which its
/// state is open where the previous change left it closed; kept in the clock, keyed by the directory's newest commit.
pub fn last_reopening(root: &Path, feature: &str, since: f64) -> Option<f64> {
    let dir = format!("specs/{feature}");
    let newest = git(root, &["log", "-1", "--format=%H", "--", &dir]).unwrap_or_default();
    if newest.is_empty() {
        return None;
    }
    let g = gitdir(root);
    let clock = read_object(g.as_ref().map(|g| g.join(CLOCK)).as_deref());
    if let Some(Value::Object(kept)) = clock.get(feature).and_then(|m| m.get("reopened")) {
        if kept.get("key").and_then(Value::as_str) == Some(newest.as_str()) {
            return kept.get("at").and_then(Value::as_f64);
        }
    }
    let walk = format!("-{}", REOPEN_WALK + 1);
    let log = git(root, &["log", &walk, "--format=%H %ct", "--", &dir]).unwrap_or_default();
    let top = root.to_string_lossy();
    let mut at = None;
    let mut newer: Option<(i64, &'static str)> = None;
    for line in log.lines() {
        let (h, ct) = line.split_once(' ').unwrap_or((line, "0"));
        let ct: i64 = ct.trim().parse().unwrap_or(0);
        let state = l7r_guard::guards::feature_approval_hooks::at_rev(&top, h, feature)
            .map_or("", |r| r.state);
        if let Some((t, s)) = newer {
            if !s.is_empty() && !CLOSED.contains(&s) && CLOSED.contains(&state) {
                #[expect(
                    clippy::cast_precision_loss,
                    reason = "a commit time is far below 2^53"
                )]
                let t = t as f64;
                at = Some(t);
                break;
            }
        }
        #[expect(
            clippy::cast_precision_loss,
            reason = "a commit time is far below 2^53"
        )]
        if (ct as f64) < since {
            break;
        }
        newer = Some((ct, state));
    }
    if let Some(g) = g {
        let mut clock = read_object(Some(&g.join(CLOCK)));
        let mine = entry(&mut clock, feature);
        mine.insert("reopened".to_owned(), json!({"key": newest, "at": at}));
        let _ = write_json(&g.join(CLOCK), &Value::Object(clock));
    }
    at
}

/// `clock.setdefault(feature, {})`.
pub fn entry<'a>(
    clock: &'a mut Map<String, Value>,
    feature: &str,
) -> &'a mut Map<String, Value> {
    let slot = clock
        .entry(feature.to_owned())
        .or_insert_with(|| Value::Object(Map::new()));
    if !slot.is_object() {
        *slot = Value::Object(Map::new());
    }
    slot.as_object_mut().unwrap_or_else(|| unreachable!())
}

/// When the feature's hour began (D53, D58): the later of its first event and its most recent reopening, or None with no event log.
#[must_use]
pub fn feature_start(root: &Path, feature: &str) -> Option<f64> {
    let first = first_event(root, feature)?;
    Some(last_reopening(root, feature, first).map_or(first, |r| first.max(r)))
}

/// Is the work landing - the push refused for an unanswered glyph unit, the marker naming this feature (or none)?
pub fn landing(root: &Path, feature: &str) -> bool {
    let mark = read_object(Some(&gitdir(root).unwrap_or_else(nowhere).join(LANDING)));
    !mark.is_empty() && mark.get("feature").unwrap_or(&json!("")) == &json!(feature)
}

/// The feature's own clock entry (`clock.get(feature) or {}`).
pub fn mine(root: &Path, feature: &str) -> Map<String, Value> {
    let clock = read_object(Some(&gitdir(root).unwrap_or_else(nowhere).join(CLOCK)));
    match clock.get(feature) {
        Some(Value::Object(m)) => m.clone(),
        _ => Map::new(),
    }
}

/// `(the glyph units due, the glyph units owed and waiting with when each comes due)` - plan D53-D55.
pub fn glyph_due(
    root: &Path,
    units: &[Unit],
    at: Option<f64>,
) -> (Vec<Unit>, Vec<(Unit, String)>) {
    let now = at.unwrap_or_else(now);
    let glyph: Vec<Unit> = units
        .iter()
        .filter(|u| u.check == "glyph-check")
        .cloned()
        .collect();
    if glyph.is_empty() {
        return (Vec::new(), Vec::new());
    }
    let feature = active_feature(root);
    if landing(root, &feature) {
        return (glyph, Vec::new());
    }
    let start = if feature.is_empty() {
        None
    } else {
        feature_start(root, &feature)
    };
    let Some(start) = start else {
        return (
            Vec::new(),
            glyph
                .into_iter()
                .map(|u| (u, "at landing".to_owned()))
                .collect(),
        );
    };
    let g = gitdir(root).unwrap_or_else(nowhere);
    let mine = mine(root, &feature);
    let batch_at = as_float(mine.get("batch_at"));
    let hour = start.max(batch_at);
    if now - hour >= GLYPH_HOUR_S {
        return (glyph, Vec::new());
    }
    let pairing = read_object(Some(&g.join(PAIRING)));
    let disp = pairing.get("dispatched").cloned().unwrap_or(Value::Null);
    let batch: Vec<&str> = mine
        .get("batch")
        .and_then(Value::as_array)
        .map(|b| b.iter().filter_map(Value::as_str).collect())
        .unwrap_or_default();
    let undispatched = |slug: &str| as_float(disp.get(slug).and_then(|d| d.get("at"))) < batch_at;
    let due: Vec<Unit> = glyph
        .iter()
        .filter(|u| {
            batch_at != 0.0 && batch.contains(&u.slug().as_str()) && undispatched(&u.slug())
        })
        .cloned()
        .collect();
    let when = local_time(hour + GLYPH_HOUR_S, "%H:%M");
    let waiting = glyph
        .into_iter()
        .filter(|u| !due.contains(u))
        .map(|u| (u, format!("at {when}")))
        .collect();
    (due, waiting)
}

/// A glyph dispatch passed on the hour, or under `GLYPH_DUE_OK`, opens a batch (D53, D55).
fn open_batch(root: &Path, units: &[Unit], at: f64) {
    let feature = active_feature(root);
    let Some(g) = gitdir(root) else { return };
    if feature.is_empty() {
        return;
    }
    let mut clock = read_object(Some(&g.join(CLOCK)));
    let mut batch: Vec<String> = units
        .iter()
        .filter(|u| u.check == "glyph-check")
        .map(Unit::slug)
        .collect();
    batch.sort();
    let mine = entry(&mut clock, &feature);
    mine.insert("batch_at".to_owned(), json!(int_of(at)));
    mine.insert("batch".to_owned(), json!(batch));
    let _ = write_json(&g.join(CLOCK), &Value::Object(clock));
}

/// `review-gate.sh`'s refusal for an unanswered glyph unit sets the marker; a clean push clears it (D55).
pub fn mark_landing(root: &Path, on: bool) {
    let Some(g) = gitdir(root) else { return };
    if on {
        let body = json!({"feature": active_feature(root), "at": now()});
        let _ = std::fs::write(
            g.join(LANDING),
            l7r_guard::shared::pyjson::dumps(&body, None, true) + "\n",
        );
    } else {
        let _ = std::fs::remove_file(g.join(LANDING));
    }
}

/// `--glyph-gate SLUG` (`gate`): 0 when the unit may be dispatched now, else 1 naming when it comes due. `--glyph-dispatched
/// SLUG`: a passed dispatch on the hour or under the escape opens a batch. `(exit, stdout)`.
#[must_use]
pub fn glyph_cli(root: &Path, slug: &str, gate: bool, escaped: bool) -> (i32, String) {
    let units = all_owed(root).1;
    let Some(unit) = units.iter().find(|u| u.slug() == slug) else {
        return (0, String::new());
    };
    if unit.check != "glyph-check" {
        return (0, String::new());
    }
    let at = now();
    let (due, waiting) = glyph_due(root, &units, Some(at));
    if gate {
        if due.contains(unit) || escaped {
            return (0, String::new());
        }
        let when = waiting
            .iter()
            .find(|(u, _)| u == unit)
            .map_or("later", |(_, w)| w.as_str());
        return (1, format!("{slug} is owed but not yet due - due {when} (a glyph check runs on the feature's hour, all owed units together, or at landing; feature 375 amendment 9)\n"));
    }
    let feature = active_feature(root);
    let start = if feature.is_empty() {
        None
    } else {
        feature_start(root, &feature)
    };
    let batch_at = as_float(mine(root, &feature).get("batch_at"));
    let on_the_hour =
        start.is_some_and(|s| !landing(root, &feature) && at - s.max(batch_at) >= GLYPH_HOUR_S);
    if on_the_hour || escaped {
        open_batch(root, &units, at);
    }
    (0, String::new())
}

#[cfg(test)]
mod tests;
