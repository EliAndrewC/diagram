//! The round arbiter's triggers and rulings (feature 449 T86, from `scripts/hooks/lib/hm_arbiter.py`): which are owed, which hold a dispatch or a gate, and recording one. Only a QUESTION reaches the GM; the
//! ruling itself is recorded by `l7r-gate arbiter`, here the reads and `trip` the guards and that command share.

use std::path::{Path, PathBuf};
use std::sync::LazyLock;

use fancy_regex::Regex;
use serde_json::{json, Map, Value};

use super::{common_dir, load, map_mut, name_of, now, text, with_owed, OWED};

/// The rulings a closing verdict is: `accept` and `process-fault` (`hm_arbiter.RULINGS[1:]`).
const CLOSING: [&str; 2] = ["accept", "process-fault"];
/// Dispatches past which a feature's checks are cascading, and the fewest before the ratio means anything (`CASCADE_RATIO`, `CASCADE_MIN`).
const CASCADE_RATIO: u64 = 1;
const CASCADE_MIN: u64 = 10;

fn re(pattern: &str) -> Regex {
    Regex::new(pattern).unwrap_or_else(|e| unreachable!("{e}"))
}

static ASK_FEATURE: LazyLock<Regex> = LazyLock::new(|| re(r"^ask:(\d{3})-"));
static PLAN_FEATURE: LazyLock<Regex> = LazyLock::new(|| re(r"\|(?:plan|spec):(\d{3})-"));
static DISPATCHES: LazyLock<Regex> = LazyLock::new(|| re(r"^(\d+) check dispatches"));
static EPOCH: LazyLock<Regex> =
    LazyLock::new(|| re(r"^(\d{4})-(\d{1,2})-(\d{1,2})T(\d{1,2}):(\d{1,2}):(\d{1,2})Z$"));
static ISO: LazyLock<Regex> = LazyLock::new(|| {
    re(
        r"^(\d{4})-(\d{2})-(\d{2})(?:[T ](\d{2}):(\d{2})(?::(\d{2})(?:\.(\d{1,6}))?)?)?(Z|[+-]\d{2}(?::?\d{2})?)?$",
    )
});

fn group(text_at: &str, pattern: &Regex) -> Option<String> {
    pattern
        .captures(text_at)
        .ok()
        .flatten()
        .and_then(|c| c.get(1).map(|m| m.as_str().to_owned()))
}

/// The directories under `root/specs` whose name starts with `prefix`, sorted (`sorted(specs.glob("<prefix>*/"))`).
#[must_use]
pub fn spec_dirs(root: &Path, prefix: &str) -> Vec<PathBuf> {
    let mut out: Vec<PathBuf> = std::fs::read_dir(root.join("specs"))
        .into_iter()
        .flatten()
        .flatten()
        .filter(|e| e.file_name().to_string_lossy().starts_with(prefix) && e.path().is_dir())
        .map(|e| e.path())
        .collect();
    out.sort();
    out
}

/// The feature an ask or a plan round names by its number, when exactly one directory has it (`hm_arbiter.asked_feature`).
#[must_use]
pub fn asked_feature(root: &Path, trigger: &str) -> Option<PathBuf> {
    let number = group(trigger, &ASK_FEATURE).or_else(|| group(trigger, &PLAN_FEATURE))?;
    let dirs = spec_dirs(root, &format!("{number}-"));
    (dirs.len() == 1).then(|| dirs[0].clone())
}

/// The environment's two feature pointers, read once per call of the public functions.
fn feature_env() -> (String, String) {
    (
        std::env::var("L7R_FEATURE_DIRECTORY").unwrap_or_default(),
        std::env::var("SPECIFY_FEATURE").unwrap_or_default(),
    )
}

/// `feature_dir` with its environment given: a page session's own first, then the exported feature whose directory exists, then `.specify/feature.json`.
#[must_use]
pub fn feature_dir_from(root: &Path, trigger: &str, own: &str, named: &str) -> Option<PathBuf> {
    if !trigger.is_empty() {
        if let Some(asked) = asked_feature(root, trigger) {
            return Some(asked);
        }
    }
    let own = own.trim().trim_end_matches('/');
    if !own.is_empty() {
        return Some(root.join(own));
    }
    let named = named.trim().trim_matches('/');
    if !named.is_empty() && root.join("specs").join(named).is_dir() {
        return Some(root.join("specs").join(named));
    }
    let pointer: Value =
        serde_json::from_str(&std::fs::read_to_string(root.join(".specify/feature.json")).ok()?)
            .ok()?;
    let fd = text(&pointer, "feature_directory");
    (!fd.is_empty()).then(|| root.join(fd.trim_end_matches('/')))
}

/// The active feature (`hm_arbiter.feature_dir`).
#[must_use]
pub fn feature_dir(root: &Path, trigger: &str) -> Option<PathBuf> {
    let (own, named) = feature_env();
    feature_dir_from(root, trigger, &own, &named)
}

/// The owed triggers (`hm_arbiter.owed`).
#[must_use]
pub fn owed(root: &Path) -> Map<String, Value> {
    match load(&common_dir(root).join(OWED)) {
        Value::Object(map) => map,
        _ => Map::new(),
    }
}

fn mine(root: &Path, v: &Value) -> bool {
    let d = feature_dir(root, "");
    super::falsy(v.get("feature"))
        || d.is_none()
        || d.is_some_and(|d| v.get("feature").and_then(Value::as_str) == Some(name_of(&d).as_str()))
}

/// The owed triggers another feature fired, left out of this feature's holds and named so none vanishes (`hm_arbiter.aside`).
#[must_use]
pub fn aside(root: &Path) -> Vec<String> {
    let mut out: Vec<String> = owed(root)
        .iter()
        .filter(|(_, v)| !mine(root, v))
        .map(|(t, v)| {
            let feature = v.get("feature").map_or_else(String::new, py_text);
            format!("{t} (feature {feature})")
        })
        .collect();
    out.sort();
    out
}

/// `{trigger: its ruling}` of the active feature, or of the feature `trigger` names.
#[must_use]
pub fn rulings(root: &Path, trigger: &str) -> Map<String, Value> {
    let mut out = Map::new();
    let Some(d) = feature_dir(root, trigger) else {
        return out;
    };
    for line in super::reply::py_lines(
        &std::fs::read_to_string(d.join("arbiter.jsonl")).unwrap_or_default(),
    ) {
        if let Ok(row) = serde_json::from_str::<Value>(line) {
            if let Some(t) = row.get("trigger").map(py_text) {
                out.insert(t, row);
            }
        }
    }
    out
}

/// A JSON value as Python's `str()` reads it: text as itself, everything else as JSON.
#[must_use]
pub fn py_text(value: &Value) -> String {
    match value {
        Value::String(s) => s.clone(),
        other => other.to_string(),
    }
}

/// `round:<unit>@7` -> 7; 0 where the trigger names no round (`hm_arbiter._round_no`).
#[must_use]
pub fn round_no(trigger: &str) -> u64 {
    trigger
        .rsplit_once('@')
        .map_or(trigger, |(_, tail)| tail)
        .parse()
        .unwrap_or(0)
}

/// How many `continue` rulings the round triggers of one unit carry; with `after`, only those past round `after`.
#[must_use]
pub fn continues(root: &Path, prefix: &str, after: u64) -> u64 {
    let n = rulings(root, "")
        .iter()
        .filter(|(t, r)| {
            t.starts_with(prefix) && text(r, "ruling") == "continue" && round_no(t) > after
        })
        .count();
    u64::try_from(n).unwrap_or(0)
}

fn is_closing(r: &Value) -> bool {
    CLOSING.contains(&text(r, "ruling"))
}

fn lapsed_one(r: &Value, content: Option<&str>) -> bool {
    content.is_some_and(|c| !c.is_empty())
        && !text(r, "content_key").is_empty()
        && Some(text(r, "content_key")) != content
}

/// The ruling that closed the unit, or ""; with `content`, a ruling bound to another `content_key` has lapsed.
#[must_use]
pub fn closed(root: &Path, prefix: &str, content: Option<&str>) -> String {
    rulings(root, "")
        .iter()
        .find(|(t, r)| t.starts_with(prefix) && is_closing(r) && !lapsed_one(r, content))
        .map_or_else(String::new, |(_, r)| text(r, "ruling").to_owned())
}

/// How many closing rulings on one unit have lapsed against `content`.
#[must_use]
pub fn lapsed(root: &Path, prefix: &str, content: Option<&str>) -> u64 {
    let n = rulings(root, "")
        .iter()
        .filter(|(t, r)| t.starts_with(prefix) && is_closing(r) && lapsed_one(r, content))
        .count();
    u64::try_from(n).unwrap_or(0)
}

/// The unruled triggers that hold the next dispatch on `unit`, or with `gate` the next `make done`.
#[must_use]
pub fn blocking(root: &Path, unit: &str, gate: bool) -> Vec<String> {
    let mut out: Vec<String> = owed(root)
        .iter()
        .filter(|(_, v)| mine(root, v))
        .filter(|(_, v)| {
            let kind = text(v, "kind");
            if gate {
                kind == "red-gate"
            } else {
                matches!(kind, "reversal" | "cascade")
                    || (kind == "round" && text(v, "unit") == unit)
            }
        })
        .map(|(t, _)| t.clone())
        .collect();
    out.sort();
    out
}

/// Every round trigger owed now but a spec review's own, plus any round the session names (`hm_arbiter.batch_triggers`).
#[must_use]
pub fn batch_triggers(root: &Path, extra: &[String]) -> Vec<String> {
    let own = owed(root)
        .into_iter()
        .filter(|(t, v)| {
            text(v, "kind") == "round" && !t.starts_with("round:spec-fidelity|") && mine(root, v)
        })
        .map(|(t, _)| t);
    let mut out: Vec<String> = own
        .chain(
            extra
                .iter()
                .filter(|t| t.starts_with("round:") && !t.starts_with("round:spec-fidelity|"))
                .cloned(),
        )
        .collect();
    out.sort();
    out.dedup();
    out
}

/// The refusal a tripwire owes, naming the batch where one is owed together.
#[must_use]
pub fn refusal(triggers: &[String], root: Option<&Path>) -> String {
    let Some(t) = triggers.first() else {
        return String::new();
    };
    let batched = root.map_or_else(Vec::new, |r| batch_triggers(r, triggers));
    if batched.len() > 1 && batched.contains(t) {
        return format!(
            "{} round triggers are owed together ({}; feature 375 FR-017): ONE ruling for the batch - make arbiter-bundle BATCH=1, dispatch `round-arbiter` on the MANIFEST it prints, then make arbiter-ruled BATCH=1 FILE=<its JSON> AS=round-arbiter. A round you mean to ask about ahead of its cap joins it with TRIGGERS=\"<trigger> ...\". The feature goes on elsewhere meanwhile.",
            batched.len(),
            batched.join(", ")
        );
    }
    format!(
        "a tripwire is owed its ruling first ({}; feature 375 FR-010/FR-011): make arbiter-bundle TRIGGER=\"{t}\", dispatch `round-arbiter` on the MANIFEST it prints, then make arbiter-ruled TRIGGER=\"{t}\" FILE=<its JSON> AS=round-arbiter. Several units at their cap together (a batch of pop-ups or pages)? `make arbiter-bundle BATCH=1` puts every owed round trigger to ONE ruling (feature 375 amendment 2). The feature goes on elsewhere meanwhile. (Claude Code picks up a new agent file mid-session - this one did on 2026-10-10 - so only if `round-arbiter` is missing from the session's agent list: restart it, or carry ARBITER_OK=\"<reason>\" on the gate or in the check's prompt - logged.)",
        triggers.join(", ")
    )
}

/// Whether an Edit of `path` (digests `old` -> `new`) puts back text an earlier Edit of that file replaced (A -> B -> A).
#[must_use]
pub fn reversal(events: &[Value], path: &str, old: &str, new: &str) -> bool {
    let replaced: Vec<String> = events
        .iter()
        .filter(|e| {
            text(e, "ev") == "PreToolUse"
                && text(e, "tool") == "Edit"
                && e.get("path").map(py_text).as_deref() == Some(path)
        })
        .map(|e| e.get("old").map_or_else(|| "None".to_owned(), py_text))
        .collect();
    !new.is_empty() && replaced.iter().any(|r| r == new) && new != old
}

/// Past the ratio with at least `CASCADE_MIN` dispatches, counted since the last cascade ruling.
#[must_use]
pub fn cascade(dispatches: u64, lines: u64, last: u64) -> bool {
    dispatches.saturating_sub(last) >= CASCADE_MIN && dispatches > CASCADE_RATIO * lines.max(1)
}

const SECONDS_A_DAY: i64 = 86_400;

fn is_leap(y: i64) -> bool {
    (y % 4 == 0 && y % 100 != 0) || y % 400 == 0
}

/// Days from 1970-01-01 to a civil date (Howard Hinnant's algorithm).
fn days_from_civil(y: i64, m: i64, d: i64) -> i64 {
    let y = if m <= 2 { y - 1 } else { y };
    let era = y.div_euclid(400);
    let yoe = y.rem_euclid(400);
    let mp = (m + 9) % 12;
    let doy = (153 * mp + 2) / 5 + d - 1;
    let of_era = yoe * 365 + yoe / 4 - yoe / 100 + doy;
    era * 146_097 + of_era - 719_468
}

/// A ruling's `utc` (`%Y-%m-%dT%H:%M:%SZ`) as epoch seconds; 0 where it reads as none (`hm_arbiter._epoch`).
#[must_use]
#[expect(clippy::many_single_char_names, reason = "the fields of a date")]
pub fn epoch(utc: &str) -> f64 {
    let Ok(Some(c)) = EPOCH.captures(utc) else {
        return 0.0;
    };
    let field = |i: usize| {
        c.get(i)
            .map_or(0, |m| m.as_str().parse::<i64>().unwrap_or(0))
    };
    let (y, mo, d, h, mi, s) = (field(1), field(2), field(3), field(4), field(5), field(6));
    let month_days: [i64; 12] = [
        31,
        if is_leap(y) { 29 } else { 28 },
        31,
        30,
        31,
        30,
        31,
        31,
        30,
        31,
        30,
        31,
    ];
    let days_in = month_days
        .get(usize::try_from(mo - 1).unwrap_or(99))
        .copied();
    let valid = days_in.is_some_and(|max| (1..=max).contains(&d)) && h < 24 && mi < 60 && s <= 61;
    if !valid {
        return 0.0;
    }
    #[expect(
        clippy::cast_precision_loss,
        reason = "epoch seconds for centuries around now fit a double exactly"
    )]
    let secs = (days_from_civil(y, mo, d) * SECONDS_A_DAY + h * 3600 + mi * 60 + s) as f64;
    secs
}

/// `datetime.fromisoformat(text.replace("Z", "+00:00")).timestamp()`, 0 where it reads as none (`hm_budget_rounds._utc`).
#[must_use]
pub fn epoch_iso(utc: &str) -> f64 {
    iso_seconds(&utc.replace('Z', "+00:00")).unwrap_or(0.0)
}

/// An ISO stamp's epoch seconds (`datetime.fromisoformat(...).timestamp()`), None where it reads as none.
#[must_use]
#[expect(clippy::many_single_char_names, reason = "the fields of a date")]
pub fn iso_seconds(stamp: &str) -> Option<f64> {
    let c = ISO.captures(stamp).ok().flatten()?;
    let field = |i: usize| {
        c.get(i)
            .map_or(0, |m| m.as_str().parse::<i64>().unwrap_or(0))
    };
    let (y, mo, d, h, mi, s) = (field(1), field(2), field(3), field(4), field(5), field(6));
    let plain = format!("{y:04}-{mo:02}-{d:02}T{h:02}:{mi:02}:{s:02}Z");
    let at = epoch(&plain);
    if at == 0.0 && plain != "1970-01-01T00:00:00Z" {
        return None;
    }
    let fraction = c
        .get(7)
        .map_or(0.0, |m| format!("0.{}", m.as_str()).parse().unwrap_or(0.0));
    let offset = c.get(8).map_or(0.0, |m| zone_seconds(m.as_str()));
    Some(at + fraction - offset)
}

/// An offset's seconds east of UTC, `+05:30`, `-0100` or `Z`.
fn zone_seconds(zone: &str) -> f64 {
    if zone == "Z" {
        return 0.0;
    }
    let digits: String = zone[1..].chars().filter(char::is_ascii_digit).collect();
    let (h, m) = digits.split_at(2.min(digits.len()));
    let (h, m): (f64, f64) = (h.parse().unwrap_or(0.0), m.parse().unwrap_or(0.0));
    let sign = if zone.starts_with('-') { -1.0 } else { 1.0 };
    sign * (h * 3600.0 + m * 60.0)
}

/// The next cascade trigger id, and the dispatches at the last cascade ruling inside the window opened at `since`.
#[must_use]
pub fn cascade_state(root: &Path, since: f64) -> (String, u64) {
    let ruled: Vec<Value> = rulings(root, "")
        .iter()
        .filter(|(t, _)| t.starts_with("cascade@"))
        .map(|(_, r)| r.clone())
        .collect();
    let last = ruled
        .iter()
        .filter(|r| epoch(text(r, "utc")) >= since)
        .map(|r| r.get("dispatches").and_then(Value::as_u64).unwrap_or(0))
        .max()
        .unwrap_or(0);
    (format!("cascade@{}", ruled.len() + 1), last)
}

/// `round:<check>|<subject>@N` -> `<check>|<subject>`; "" for any other trigger.
#[must_use]
pub fn unit_of(trigger: &str) -> String {
    let Some(body) = trigger.strip_prefix("round:") else {
        return String::new();
    };
    if !trigger.contains('|') {
        return String::new();
    }
    body.rsplit_once('@')
        .map_or(body, |(before, _)| before)
        .to_owned()
}

fn dispatches_in(detail: &str) -> Option<u64> {
    group(detail, &DISPATCHES).and_then(|d| d.parse().ok())
}

/// Record a trigger once (a second firing changes nothing); true when it is new. `now` is the epoch time written, null for the clock's; `review` names the spec or plan review an ask is about.
#[must_use]
pub fn trip(
    root: &Path,
    trigger: &str,
    kind: &str,
    unit: &str,
    detail: &str,
    when: &Value,
    review: &str,
) -> bool {
    if rulings(root, trigger).contains_key(trigger) {
        return false;
    }
    let common = common_dir(root);
    let mut new = false;
    let written = with_owed(&common, &mut |state| {
        if state.get(trigger).is_some() {
            return false;
        }
        let d = feature_dir(root, trigger);
        let mut row = Map::new();
        row.insert("kind".to_owned(), json!(kind));
        row.insert("unit".to_owned(), json!(unit));
        row.insert("detail".to_owned(), json!(detail));
        row.insert(
            "t".to_owned(),
            if when.is_null() {
                json!(now())
            } else {
                when.clone()
            },
        );
        row.insert(
            "feature".to_owned(),
            json!(d.map_or_else(String::new, |d| name_of(&d))),
        );
        if !review.is_empty() {
            row.insert("review".to_owned(), json!(review));
        }
        if let Some(n) = dispatches_in(detail) {
            row.insert("dispatches".to_owned(), json!(n));
        }
        map_mut(state, trigger);
        state[trigger] = Value::Object(row);
        new = true;
        true
    });
    written.is_ok() && new
}

/// The stored JSON's `state[trigger]`, popped under the owed lock, written back only where it was there (`record_ruling`'s last step).
///
/// # Errors
///
/// The lock or the file cannot be had.
pub fn pop_owed(common: &Path, trigger: &str) -> Result<(), String> {
    with_owed(common, &mut |state| {
        state
            .as_object_mut()
            .and_then(|map| map.shift_remove(trigger))
            .is_some()
    })
}

#[cfg(test)]
mod tests;
