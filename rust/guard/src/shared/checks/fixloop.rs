//! A quote-check fix that keeps failing goes to the round arbiter (feature 399, kind B; from `hm_fixloop.py`): it counts per footnote beside the round counter.

use std::collections::{BTreeMap, BTreeSet, HashMap};
use std::path::Path;
use std::sync::LazyLock;

use fancy_regex::Regex;
use serde_json::{json, Map, Value};

use super::arbiter;
use super::{map_mut, text};

/// A footnote is held at its third round after two failed fixes, as the round cap holds a page at its third round.
const HOLD_AT: u64 = 2;

fn re(pattern: &str) -> Regex {
    Regex::new(pattern).unwrap_or_else(|e| unreachable!("{e}"))
}

static FLAG: LazyLock<Regex> = LazyLock::new(|| {
    re(r"(?<!\d )\b(?:NOT-READABLE|DIFFERS|NOT-ON-PAGE|PARTIAL|DOES-NOT-SUPPORT)\b")
});
static OUTSIDE: LazyLock<Regex> =
    LazyLock::new(|| re(r"(?m)^#*\s*\**OUTSIDE THE CHANGE\**\s*:?\s*$"));
static NOTE_UNIT: LazyLock<Regex> =
    LazyLock::new(|| re(r"(?m)^unit: quote-check:(\S+#\S+) (\S+)$"));

/// `{<stem>#<key>: fingerprint}` of the quote-check footnotes a bundle carries.
#[must_use]
pub fn notes_of(manifest: &str) -> BTreeMap<String, String> {
    NOTE_UNIT
        .captures_iter(manifest)
        .flatten()
        .filter(|c| !c[1].ends_with("#unfootnoted"))
        .map(|c| (c[1].to_owned(), c[2].to_owned()))
        .collect()
}

fn key_pattern(note: &str) -> Regex {
    let key = note.split_once('#').map_or("", |(_, k)| k);
    re(&format!(r"(?<![\w-]){}(?![\w-])", fancy_regex::escape(key)))
}

/// `({flagged footnote: its first flagged line}, the footnotes named and never flagged)`.
#[must_use]
pub fn read_reply(reply: &str, notes: &[String]) -> (BTreeMap<String, String>, BTreeSet<String>) {
    let body = OUTSIDE
        .find(reply)
        .ok()
        .flatten()
        .map_or(reply, |m| &reply[..m.start()]);
    let lines: Vec<&str> = body.lines().collect();
    let start = lines
        .iter()
        .position(|ln| !ln.trim().is_empty())
        .map_or(lines.len(), |i| i + 1);
    let keys: HashMap<&str, Regex> = notes.iter().map(|n| (n.as_str(), key_pattern(n))).collect();
    let mut flagged: BTreeMap<String, String> = BTreeMap::new();
    let mut named: BTreeSet<String> = BTreeSet::new();
    for ln in lines.iter().skip(start) {
        let hits: Vec<&str> = keys
            .iter()
            .filter(|(_, k)| k.is_match(ln).unwrap_or(false))
            .map(|(n, _)| *n)
            .collect();
        named.extend(hits.iter().map(|n| (*n).to_owned()));
        if !hits.is_empty() && FLAG.is_match(ln).unwrap_or(false) {
            let shown: String = ln
                .split_whitespace()
                .collect::<Vec<_>>()
                .join(" ")
                .chars()
                .take(200)
                .collect();
            for n in hits {
                flagged.entry(n.to_owned()).or_insert_with(|| shown.clone());
            }
        }
    }
    let passed = named
        .into_iter()
        .filter(|n| !flagged.contains_key(n))
        .collect();
    (flagged, passed)
}

/// Count a returned quote-check reading's flags, once (the caller's `rounded` guard).
pub fn returned(state: &mut Value, d: &Value, reply: &str) {
    let notes: BTreeMap<String, String> = d
        .get("quote_notes")
        .and_then(Value::as_object)
        .map(|m| {
            m.iter()
                .map(|(k, v)| (k.clone(), v.as_str().unwrap_or("").to_owned()))
                .collect()
        })
        .unwrap_or_default();
    if text(d, "check") != "quote-check" || notes.is_empty() || reply.trim().is_empty() {
        return;
    }
    let names: Vec<String> = notes.keys().cloned().collect();
    let (flagged, passed) = read_reply(reply, &names);
    let fl = map_mut(state, "flags");
    for (n, line) in flagged {
        let fp = notes[&n].clone();
        let prev = fl.get(&n).cloned().unwrap_or(Value::Null);
        let prev_n = prev.get("n").and_then(Value::as_u64).unwrap_or(0);
        if prev_n == 0 {
            fl.insert(n, json!({"n": 1, "fp": fp, "lines": [line]}));
        } else if text(&prev, "fp") != fp {
            let mut lines: Vec<Value> = prev
                .get("lines")
                .and_then(Value::as_array)
                .cloned()
                .unwrap_or_default();
            lines.push(json!(line));
            let tail = lines.split_off(lines.len().saturating_sub(2));
            fl.insert(n, json!({"n": prev_n + 1, "fp": fp, "lines": tail}));
        } else if let Some(row) = fl.get_mut(&n) {
            let mut lines: Vec<Value> = row
                .get("lines")
                .and_then(Value::as_array)
                .cloned()
                .unwrap_or_default();
            lines.pop();
            lines.push(json!(line));
            row["lines"] = Value::Array(lines);
        }
    }
    for n in passed {
        fl.shift_remove(&n);
    }
}

fn next_round(root: &Path, unit: &str, counted: u64) -> u64 {
    let prefix = format!("round:{unit}@");
    let used = arbiter::rulings(root, "")
        .keys()
        .chain(arbiter::owed(root).keys())
        .filter(|t| t.starts_with(&prefix))
        .map(|t| arbiter::round_no(t))
        .max()
        .unwrap_or(0);
    HOLD_AT.max(counted).max(used) + 1
}

fn note_unit(n: &str) -> String {
    let stem = n.split('#').next().unwrap_or(n);
    format!("quote-check|q:{}", stem.split('.').next().unwrap_or(stem))
}

/// The refusal for a quote-check bundle carrying a footnote whose fix keeps failing, or "".
pub fn hold(state: &mut Value, root: &Path, check: &str, manifest: &str, now: f64) -> String {
    if check != "quote-check" {
        return String::new();
    }
    let rul = arbiter::rulings(root, "");
    let rounds_of = |state: &Value, unit: &str| {
        state
            .get("rounds")
            .and_then(|r| r.get(unit))
            .and_then(Value::as_u64)
            .unwrap_or(0)
    };
    map_mut(state, "flag_trips");
    for (n, fp) in notes_of(manifest) {
        let trip_id = state["flag_trips"]
            .get(&n)
            .and_then(Value::as_str)
            .map(str::to_owned);
        if let Some(t) = trip_id
            .as_ref()
            .filter(|t| !t.is_empty() && rul.contains_key(t.as_str()))
        {
            let ruling = text(&rul[t.as_str()], "ruling").to_owned();
            flag_trips(state).shift_remove(&n);
            if let Some(f) = flags(state).and_then(|fl| fl.get_mut(&n)) {
                f["n"] = json!(u64::from(ruling == "continue"));
            }
            continue;
        }
        let f = state
            .get("flags")
            .and_then(|fl| fl.get(&n))
            .cloned()
            .unwrap_or(Value::Null);
        if f.is_null()
            || f.get("n").and_then(Value::as_u64).unwrap_or(0) < HOLD_AT
            || text(&f, "fp") == fp
        {
            continue;
        }
        if let Some(t) = trip_id.filter(|t| !t.is_empty()) {
            return arbiter::refusal(&[t], Some(root));
        }
        let unit = note_unit(&n);
        let counted = rounds_of(state, &unit);
        let trig = format!("round:{unit}@{}", next_round(root, &unit, counted));
        let lines: Vec<String> = f
            .get("lines")
            .and_then(Value::as_array)
            .map(|a| {
                a.iter()
                    .map(|l| l.as_str().unwrap_or("").to_owned())
                    .collect()
            })
            .unwrap_or_default();
        let detail = format!("footnote {n} flagged by quote-check in {} rounds in a row, changed between them (feature 399): {}", f["n"], lines.join(" | "));
        let _ = arbiter::trip(root, &trig, "round", &unit, &detail, &json!(now), "");
        flag_trips(state).insert(n, json!(trig.clone()));
        return arbiter::refusal(&[trig], Some(root));
    }
    String::new()
}

fn flag_trips(state: &mut Value) -> &mut Map<String, Value> {
    map_mut(state, "flag_trips")
}

fn flags(state: &mut Value) -> Option<&mut Map<String, Value>> {
    state.get_mut("flags").and_then(Value::as_object_mut)
}

#[cfg(test)]
mod tests;
