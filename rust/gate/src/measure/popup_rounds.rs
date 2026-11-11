//! How many rounds a clone's pop-up checks took - feature 375 amendment 3, SC-012 (`m:375-a3-popup-rounds-before`; feature 449 T77, from
//! `popup_rounds.py`).
//!
//! Amendment 3 orders a pop-up's checks (form, research, depiction) and lets a later check's applied edits settle the earlier ones, as a
//! speculative fix measured afterwards (the GM, 2026-10-11). The baseline was counted from the kept dispatch records of two clones; this is
//! that count, kept, so the after is counted by the same method. A UNIT is a (pop-up, check) pair and its rounds are its dispatches.

use std::collections::{BTreeMap, BTreeSet};
use std::fmt::Write as _;
use std::path::Path;

use serde_json::{json, Map, Value};

use super::{reply, text_err};
use crate::plan::pretty;

pub(crate) mod iso;

const MODAL_CHECKS: [&str; 3] = ["modal-form", "modal-research", "modal-depiction"];

/// Python's `round(x, 2)`: the nearest two-place decimal.
fn two_places(x: f64) -> f64 {
    format!("{x:.2}").parse().unwrap_or(x)
}

fn row(values: &[i64]) -> Map<String, Value> {
    let total: i64 = values.iter().sum();
    let at_least = |n: i64| values.iter().filter(|v| **v >= n).count();
    #[expect(clippy::cast_precision_loss, reason = "counts of dispatches, small")]
    let per = if values.is_empty() {
        0.0
    } else {
        two_places(total as f64 / values.len() as f64)
    };
    let mut out = Map::new();
    out.insert("units".to_owned(), json!(values.len()));
    out.insert("dispatches".to_owned(), json!(total));
    out.insert("per unit".to_owned(), json!(per));
    out.insert("units with a 2nd round".to_owned(), json!(at_least(2)));
    out.insert("units with a 3rd".to_owned(), json!(at_least(3)));
    out
}

/// Units, dispatches, dispatches per unit, and the units with a second and a third round, overall and per check.
pub(crate) fn counts(dispatches: &[&Value], since: f64) -> Value {
    let mut units: BTreeMap<(String, &str), i64> = BTreeMap::new();
    for d in dispatches {
        let check = d["check"].as_str().unwrap_or("");
        let Some(known) = MODAL_CHECKS.iter().find(|c| **c == check) else {
            continue;
        };
        if d["t"].as_f64().unwrap_or(0.0) >= since {
            for subject in d["subjects"].as_array().map_or(&[][..], Vec::as_slice) {
                *units.entry((subject.to_string(), known)).or_insert(0) += 1;
            }
        }
    }
    let of = |check: &str| {
        units
            .iter()
            .filter(|((_, c), _)| *c == check)
            .map(|(_, n)| *n)
            .collect::<Vec<_>>()
    };
    let mut out = row(&units.values().copied().collect::<Vec<_>>());
    out.insert(
        "pop-ups".to_owned(),
        json!(units.keys().map(|(s, _)| s).collect::<BTreeSet<_>>().len()),
    );
    let by: Map<String, Value> = MODAL_CHECKS
        .iter()
        .map(|c| (*c, of(c)))
        .filter(|(_, v)| !v.is_empty())
        .map(|(c, v)| (c.to_owned(), Value::Object(row(&v))))
        .collect();
    out.insert("by check".to_owned(), Value::Object(by));
    Value::Object(out)
}

fn dispatches(state: &Value) -> Vec<&Value> {
    state["dispatches"]
        .as_object()
        .map_or_else(Vec::new, |m| m.values().collect())
}

fn state_of(clone: &Path) -> Value {
    let dir = crate::codeid::common_git_dir(clone).unwrap_or_else(|| clone.join(".git"));
    std::fs::read_to_string(dir.join("checks-open.json"))
        .ok()
        .and_then(|t| serde_json::from_str(&t).ok())
        .unwrap_or_else(|| json!({}))
}

/// Write each `<label>=<snapshot>`'s counts into `key`'s value in the measurements file `path`.
fn record(path: &Path, key: &str, snapshots: &[&str], since: f64) -> Result<(), String> {
    let read = |p: &Path| -> Result<Value, String> {
        let t = std::fs::read_to_string(p).map_err(|e| format!("{}: {e}", p.display()))?;
        serde_json::from_str(&t).map_err(|e| format!("{}: {e}", p.display()))
    };
    let mut data = read(path)?;
    for item in snapshots {
        let (label, snap) = item.split_once('=').unwrap_or((item, ""));
        data[key]["value"][label] = counts(&dispatches(&read(Path::new(snap))?), since);
    }
    std::fs::write(path, pretty(&data)).map_err(text_err)
}

fn line(name: &str, r: &Value, tail: &str) -> String {
    format!(
        "{name}{} over {} ({:?}){tail}",
        r["dispatches"],
        r["units"],
        r["per unit"].as_f64().unwrap_or(0.0)
    )
}

fn report(state: &Value, c: &Value) -> String {
    let feature = state["feature"].as_str().unwrap_or("?");
    let mut out = format!(
        "popup-rounds: {feature}: {} dispatches over {} units ({:?} per unit), {} with a second round, {} with a third; {} pop-ups\n",
        c["dispatches"],
        c["units"],
        c["per unit"].as_f64().unwrap_or(0.0),
        c["units with a 2nd round"],
        c["units with a 3rd"],
        c["pop-ups"]
    );
    for (check, r) in c["by check"].as_object().into_iter().flatten() {
        let tail = format!(
            ", {} second, {} third",
            r["units with a 2nd round"], r["units with a 3rd"]
        );
        let _ = writeln!(out, "{}", line(&format!("  {check}: "), r, &tail));
    }
    out
}

fn refused(words: &str) -> crate::Reply {
    reply(String::new(), format!("popup_rounds: {words}\n"), 2)
}

/// `l7r-gate measure popup-rounds <clone> [--since ISO] [--json]`, or `--record <measurements.json> --key <key> <label>=<snapshot.json> ...`.
pub(crate) fn cli(args: &[String]) -> crate::Reply {
    let (mut named, mut plain, mut json_out) = (BTreeMap::new(), Vec::new(), false);
    let mut words = args.iter();
    while let Some(word) = words.next() {
        match word.as_str() {
            "--json" => json_out = true,
            "--since" | "--record" | "--key" => {
                named.insert(word.as_str(), words.next().map_or("", String::as_str));
            }
            other => plain.push(other),
        }
    }
    let since_text = named.get("--since").copied().unwrap_or("");
    let since = if since_text.is_empty() {
        Some(0.0)
    } else {
        iso::parse(since_text)
    };
    let Some(since) = since else {
        return reply(
            String::new(),
            format!("popup_rounds: --since is not an ISO time: {since_text}\n"),
            1,
        );
    };
    if let Some(file) = named.get("--record").filter(|f| !f.is_empty()) {
        let key = named.get("--key").copied().unwrap_or("");
        if key.is_empty() || plain.is_empty() || !plain.iter().all(|c| c.contains('=')) {
            return refused("--record needs --key and one or more <label>=<snapshot.json>");
        }
        return match record(Path::new(file), key, &plain, since) {
            Ok(()) => reply(String::new(), String::new(), 0),
            Err(why) => reply(String::new(), format!("popup_rounds: {why}\n"), 1),
        };
    }
    let [clone] = plain[..] else {
        return refused("name one clone");
    };
    let state = state_of(Path::new(clone));
    let c = counts(&dispatches(&state), since);
    reply(
        if json_out {
            pretty(&c)
        } else {
            report(&state, &c)
        },
        String::new(),
        0,
    )
}

#[cfg(test)]
mod tests;
