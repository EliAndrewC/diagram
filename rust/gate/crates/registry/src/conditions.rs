//! Items of a modal that depend on the settlement's knobs (`interactive/conditions.py`, feature 319 FR-015, plan D14; ported by feature
//! 449 T149 under `ask:449-phase4-slices` Q1): a guess bullet, a paragraph of About or Depiction, or an `Entry:` path may carry
//! `[knob=value|value]...`, and a page shows the item only on a map whose manifest records, for every condition, a value among them. The
//! GM, 2026-10-05: *"Could we make that kind of item still automatic but dependent on the "knobs" for a settlement in cases where that is
//! relevant?"* The condition never reaches the reader; a bracket that looks meant as one and is not is refused, so a typo is not shown.

use std::path::Path;
use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_gate_research::pyre::py;
use l7r_gate_research::{Error, Result};
use l7r_shared::py_text::{repr, strip};
use l7r_shared::pyjson::{py_str, value_repr};
use serde_json::{Map, Value};

/// `[knob=value]` or `[knob=value|value]`, at the start of an item.
static LEAD: LazyLock<Regex> =
    LazyLock::new(|| py(r"^\[([a-z_]+)=([a-z_0-9-]+(?:\|[a-z_0-9-]+)*)\]\s*"));

/// The same condition after an `Entry:` path, up to the next comma.
static AFTER_PATH: LazyLock<Regex> =
    LazyLock::new(|| py(r"(\S+\.html)((?:\s*\[[a-z_]+=[a-z_0-9-]+(?:\|[a-z_0-9-]+)*\])+)"));

/// Anything bracketed that looks meant as a condition but is not one.
static LOOSE: LazyLock<Regex> = LazyLock::new(|| py(r"^\[[^\]]*=[^\]]*\]"));

/// A path separator of an `Entry:` line.
static SEPARATOR: LazyLock<Regex> = LazyLock::new(|| py(r"[,;]\s*"));

/// Where the knob registry is, from the tree's root (feature 444 T39's export).
pub const KNOBS_FILE: &str = "l7r/diagram/knobs.json";

/// An item's conditions: (knob, its values), all of which must hold.
pub type Cond = Vec<(String, Vec<String>)>;

/// The item's conditions and its text; None for an item with none.
///
/// # Errors
/// A bracket at the start that is not a well-formed condition (the Python's `ValueError`).
pub fn split(item: &str) -> Result<(Option<Cond>, String)> {
    let mut conds: Cond = Vec::new();
    let mut rest = item;
    while let Ok(Some(hit)) = LEAD.captures(rest) {
        conds.push((
            hit[1].to_owned(),
            hit[2].split('|').map(str::to_owned).collect(),
        ));
        rest = &rest[hit.get(0).map_or(0, |m| m.end())..];
    }
    if LOOSE.is_match(rest).unwrap_or(false) {
        let head: String = item.chars().take(60).collect();
        return Err(Error::new(
            "ValueError",
            format!(
                "a modal condition is written [knob=value] or [knob=value|value], lower case: {} (dev/modals.md M22)",
                repr(&head)
            ),
        ));
    }
    Ok(((!conds.is_empty()).then_some(conds), rest.to_owned()))
}

/// The `Entry:` paths that carry conditions, each with them, in the order first met.
///
/// # Errors
/// A malformed condition (never, the pattern holding only well-formed ones; kept as the Python's call is).
pub fn entry_conditions(entry: &str) -> Result<Vec<(String, Cond)>> {
    let mut out: Vec<(String, Cond)> = Vec::new();
    for m in AFTER_PATH
        .captures_iter(entry)
        .map_while(std::result::Result::ok)
    {
        // the pattern holds only well-formed conditions, so the Python's `if conds:` always held
        let conds = split(&m[2].replace(' ', ""))?.0.unwrap_or_default();
        match out.iter_mut().find(|(p, _)| p == &m[1]) {
            Some(slot) => slot.1 = conds,
            None => out.push((m[1].to_owned(), conds)),
        }
    }
    Ok(out)
}

/// The `Entry:` line with its conditions removed.
#[must_use]
pub fn strip_entry(entry: &str) -> String {
    AFTER_PATH.replace_all(entry, "$1").into_owned()
}

/// Does the map meet every condition? An item with none always does; a map recording no value for a knob never does.
#[must_use]
pub fn holds(conds: Option<&Cond>, meta: &Map<String, Value>) -> bool {
    conds.is_none_or(|conds| {
        conds.iter().all(|(knob, values)| {
            let had = meta.get(knob).map_or_else(String::new, py_str);
            values.contains(&had)
        })
    })
}

/// The items this map shows, conditions removed.
///
/// # Errors
/// A malformed condition.
pub fn shown(items: &[String], meta: &Map<String, Value>) -> Result<Vec<String>> {
    let mut out = Vec::new();
    for item in items {
        let (cond, text) = split(item)?;
        if holds(cond.as_ref(), meta) {
            out.push(text);
        }
    }
    Ok(out)
}

/// The `Entry:` line this map lists: a path whose condition fails is dropped (FR-015, the GM: "simply not link to things which are not
/// covered").
///
/// # Errors
/// A malformed condition.
pub fn shown_entry(entry: &str, meta: &Map<String, Value>) -> Result<String> {
    let conds = entry_conditions(entry)?;
    let stripped = strip_entry(entry);
    let kept: Vec<&str> = SEPARATOR
        .split(&stripped)
        .map_while(std::result::Result::ok)
        .map(strip)
        .filter(|p| {
            !p.is_empty()
                && holds(
                    conds.iter().find(|(path, _)| path == p).map(|(_, c)| c),
                    meta,
                )
        })
        .collect();
    Ok(kept.join(", "))
}

/// Every hamlet knob as `knobs.json` records it (`knob_table`).
///
/// # Errors
/// The file unreadable, not JSON, or without its `knobs`.
pub fn knob_table(tree: &Path) -> Result<Map<String, Value>> {
    let path = tree.join(KNOBS_FILE);
    let text = l7r_gate_core::record::read_text(&path)
        .map_err(|e| Error::new("OSError", format!("{e}: '{}'", path.display())))?;
    let value: Value =
        serde_json::from_str(&text).map_err(|e| Error::new("JSONDecodeError", e.to_string()))?;
    value
        .get("knobs")
        .and_then(Value::as_object)
        .cloned()
        .ok_or_else(|| Error::new("KeyError", "knobs"))
}

/// Every knob and its forms: `knobs.json`'s, then the title card's declared choices and the values a manifest records beyond a knob's
/// registry (`knobs`).
///
/// # Errors
/// The knob table or the choices table unreadable.
pub fn knobs(tree: &Path) -> Result<Vec<(String, Vec<Value>)>> {
    let mut out: Vec<(String, Vec<Value>)> = knob_table(tree)?
        .iter()
        .map(|(name, k)| {
            let forms = k
                .get("forms")
                .and_then(Value::as_array)
                .cloned()
                .unwrap_or_default();
            (name.clone(), forms)
        })
        .collect();
    for entry in crate::choices::table(tree)? {
        let key = entry.get("key").map_or_else(String::new, py_str);
        let values: Vec<Value> = entry
            .get("values")
            .and_then(Value::as_object)
            .into_iter()
            .flat_map(|m| m.keys().map(|k| Value::String(k.clone())))
            .collect();
        let at = out.iter().position(|(n, _)| *n == key).unwrap_or_else(|| {
            out.push((key, Vec::new()));
            out.len() - 1
        });
        for v in values {
            if !out[at].1.contains(&v) {
                out[at].1.push(v);
            }
        }
    }
    Ok(out)
}

/// Refuse a condition naming a knob or a value the registry and the choices table do not know, with the knob's forms in the message.
///
/// # Errors
/// The first such condition (the Python's `ValueError`), or the tables unreadable.
pub fn check(tree: &Path, name: &str, conds: &[Option<Cond>]) -> Result<()> {
    let known = knobs(tree)?;
    for (knob, values) in conds.iter().flatten().flatten() {
        let Some((_, forms)) = known.iter().find(|(n, _)| n == knob) else {
            let mut names: Vec<&str> = known.iter().map(|(n, _)| n.as_str()).collect();
            names.sort_unstable();
            return Err(Error::new(
                "ValueError",
                format!(
                    "{name}: [{knob}=...] names no registered knob - one of {} (dev/modals.md M22)",
                    str_list(&names)
                ),
            ));
        };
        let bad: Vec<&str> = values
            .iter()
            .filter(|v| !forms.contains(&Value::String((*v).clone())))
            .map(String::as_str)
            .collect();
        if !bad.is_empty() {
            return Err(Error::new(
                "ValueError",
                format!(
                    "{name}: [{knob}={}]: {} not among {knob}'s forms {} (dev/modals.md M22)",
                    values.join("|"),
                    str_list(&bad),
                    value_repr(&Value::Array(forms.clone()))
                ),
            ));
        }
    }
    Ok(())
}

/// A list of strings as Python prints one.
fn str_list(items: &[&str]) -> String {
    format!(
        "[{}]",
        items.iter().map(|s| repr(s)).collect::<Vec<_>>().join(", ")
    )
}

/// How a check's bundle shows conditions: "(only where `settlement_form` is nucleated or linear)".
#[must_use]
pub fn label(conds: &Cond) -> String {
    let parts: Vec<String> = conds
        .iter()
        .map(|(knob, values)| format!("{knob} is {}", values.join(" or ")))
        .collect();
    format!("(only where {})", parts.join(" and "))
}

#[cfg(test)]
mod tests;
