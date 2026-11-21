//! The blocked-domain list (`l7r/diagram/interactive/record/blocked.py`'s domain half, feature 312): ONE reader for the
//! `blocked-fetch` guard and the record's port (feature 449 T144, phase 4's S1 under `ask:449-phase4-slices`). The guard had its own
//! loader, host and refusal, restated from the same Python; they live here now (FR-003), the loader returning the Python's own refusal
//! where it raised, which the guard reads as it always did - a list that cannot be trusted fetches as if there were none.

use std::path::Path;

use serde_json::Value;

use crate::pyjson::{py_str, truthy, value_repr};

/// The list's file, beside the record.
pub const DOMAINS: &str = "blocked-domains.json";

/// One entry of either list (`blocked.Rule`): what it matches, why, and the GM's approval as `<date>: <words>`.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Rule {
    pub matches: String,
    pub reason: String,
    pub approved: String,
}

/// Why a list could not be read: the Python exception's class name and its message.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Fault {
    pub kind: &'static str,
    pub message: String,
}

impl Fault {
    #[must_use]
    pub fn new(kind: &'static str, message: String) -> Self {
        Self { kind, message }
    }
}

/// Python's type name of a JSON value, for its own messages.
#[must_use]
pub fn type_name(v: &Value) -> &'static str {
    match v {
        Value::Null => "NoneType",
        Value::Bool(_) => "bool",
        Value::Number(n) if n.is_f64() => "float",
        Value::Number(_) => "int",
        Value::String(_) => "str",
        Value::Array(_) => "list",
        Value::Object(_) => "dict",
    }
}

/// `for raw in data.get(field + "s", [])`: what Python iterates of the list's value.
fn items(data: &Value, list: &str) -> Result<Vec<Value>, Fault> {
    let Value::Object(map) = data else {
        return Err(Fault::new(
            "AttributeError",
            format!("'{}' object has no attribute 'get'", type_name(data)),
        ));
    };
    match map.get(list) {
        None => Ok(Vec::new()),
        Some(Value::Array(rows)) => Ok(rows.clone()),
        Some(Value::Object(keys)) => Ok(keys.keys().map(|k| Value::from(k.as_str())).collect()),
        Some(Value::String(s)) => Ok(s.chars().map(|c| Value::from(c.to_string())).collect()),
        Some(other) => Err(Fault::new(
            "TypeError",
            format!("'{}' object is not iterable", type_name(other)),
        )),
    }
}

/// Each entry of a list file as (what it matches, the entry), `where` the file as the messages name it; a missing file is an empty
/// list, and every entry needs its `field` and its reason before any is used (`blocked._load`).
///
/// # Errors
/// The Python's refusal: a file not JSON (`JSONDecodeError`, the library's words), a shape it cannot iterate, an entry short of a field.
pub fn load(
    record_dir: &Path,
    name: &str,
    field: &str,
) -> Result<(String, Vec<(Value, Value)>), Fault> {
    let path = record_dir.join(name);
    let place = path.to_string_lossy().into_owned();
    let text = match std::fs::read(&path) {
        Ok(bytes) => String::from_utf8_lossy(&bytes).into_owned(),
        Err(e) if e.kind() == std::io::ErrorKind::NotFound => return Ok((place, Vec::new())),
        Err(e) => return Err(Fault::new("OSError", format!("{e}: '{place}'"))),
    };
    let data: Value =
        serde_json::from_str(&text).map_err(|e| Fault::new("JSONDecodeError", e.to_string()))?;
    let mut out = Vec::new();
    for raw in items(&data, &format!("{field}s"))? {
        let ok = raw.as_object().is_some_and(|m| {
            m.get(field).is_some_and(truthy) && m.get("reason").is_some_and(truthy)
        });
        if !ok {
            return Err(Fault::new(
                "BlockedListError",
                format!(
                    "{place}: {} needs its {field} and its reason",
                    value_repr(&raw)
                ),
            ));
        }
        out.push((raw[field].clone(), raw));
    }
    Ok((place, out))
}

/// The GM's approval an entry carries, as `<date>: <words>` (`blocked._approval`).
///
/// # Errors
/// An entry with no approval, its date or its words.
pub fn approval(place: &str, raw: &Value) -> Result<String, Fault> {
    let approved = raw.get("approved");
    let ok = approved
        .and_then(Value::as_object)
        .filter(|a| a.get("date").is_some_and(truthy) && a.get("words").is_some_and(truthy));
    let Some(a) = ok else {
        return Err(Fault::new(
            "BlockedListError",
            format!(
                "{place}: {} carries no approval - every entry names the GM's approval as \"approved\": {{\"date\": \"YYYY-MM-DD\", \"words\": \"<the GM's words>\"}}",
                value_repr(raw)
            ),
        ));
    };
    Ok(format!("{}: {}", py_str(&a["date"]), py_str(&a["words"])))
}

/// `blocked.domains`: every blocked domain, lower-cased and its dots trimmed.
///
/// # Errors
/// The list's refusal ([`load`], [`approval`]), or a domain that is not text (Python's `AttributeError`).
pub fn domains(record_dir: &Path) -> Result<Vec<Rule>, Fault> {
    let (place, rows) = load(record_dir, DOMAINS, "domain")?;
    rows.iter()
        .map(|(m, raw)| {
            let Some(name) = m.as_str() else {
                return Err(Fault::new(
                    "AttributeError",
                    format!("'{}' object has no attribute 'lower'", type_name(m)),
                ));
            };
            Ok(Rule {
                matches: name.to_lowercase().trim_matches('.').to_owned(),
                reason: py_str(&raw["reason"]),
                approved: approval(&place, raw)?,
            })
        })
        .collect()
}

/// The URL's host, lower-cased; a URL written without its scheme is read as https (`blocked.host`): `urlsplit`'s, ported whole in
/// [`super::url_host`] (feature 449 T148).
pub use super::url_host::host;

/// The rule a URL falls under: its host is the domain or a subdomain of it, never a name that merely ends with the same letters.
#[must_use]
pub fn blocked<'r>(url: &str, rules: &'r [Rule]) -> Option<&'r Rule> {
    let h = host(url);
    rules
        .iter()
        .find(|r| h == r.matches || h.ends_with(&format!(".{}", r.matches)))
}

/// The one message every refusal prints: what was refused, the list, and why the entry is on it (`blocked.refusal`).
#[must_use]
pub fn refusal(url: &str, rule: &Rule, what: &str) -> String {
    format!(
        "{what} refused: {url} is on the blocked list ({DOMAINS}: {} - {}; approved {}). Find the same fact on another page; a blocked site is never read, cited or recorded.",
        rule.matches, rule.reason, rule.approved
    )
}

#[cfg(test)]
mod tests;
