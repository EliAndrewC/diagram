//! The title card's choices (`interactive/choices.py`, feature 319 plan D10, FR-009; ported by feature 449 T149 under
//! `ask:449-phase4-slices` Q1): what was chosen for this settlement, each value a modal. The GM, 2026-10-03, on Inashiro: the
//! per-settlement differences belong on the title card, where each choice opens its own modal, so every feature modal can be the same on
//! every map. `assets/choices.json` is the table; a value's modal is `assets/modals/choice/<key>--<value>.md` (a degree along a continuum,
//! marked `degree`, one file `<key>.md`), read by the same parser as a feature modal and keyed `choice:<key>=<value>` (or `choice:<key>`).

use std::path::{Path, PathBuf};

use l7r_gate_research::{Error, Result};
use l7r_shared::pyjson::{py_str, truthy};
use serde_json::{json, Map, Value};

use crate::about::{about_feature, parse_explanation, FeatureClass, MODALS};
use crate::conditions;

/// The choices table, from the tree's root.
pub const TABLE: &str = "l7r/diagram/interactive/assets/choices.json";

fn read_table(tree: &Path) -> Result<Value> {
    let path = tree.join(TABLE);
    let text = l7r_gate_core::record::read_text(&path)
        .map_err(|e| Error::new("OSError", format!("{e}: '{}'", path.display())))?;
    serde_json::from_str(&text).map_err(|e| Error::new("JSONDecodeError", e.to_string()))
}

/// Per-settlement rolls that are not choices of form, each with why (the plan review of D10).
///
/// # Errors
/// The table unreadable or not JSON.
pub fn not_choices(tree: &Path) -> Result<Map<String, Value>> {
    Ok(read_table(tree)?
        .get("not_choices")
        .and_then(Value::as_object)
        .cloned()
        .unwrap_or_default())
}

/// The choices in card order.
///
/// # Errors
/// The table unreadable, not JSON, or without its `choices`.
pub fn table(tree: &Path) -> Result<Vec<Value>> {
    read_table(tree)?
        .get("choices")
        .and_then(Value::as_array)
        .cloned()
        .ok_or_else(|| Error::new("KeyError", "choices"))
}

fn text(entry: &Value, field: &str) -> String {
    entry.get(field).map_or_else(String::new, py_str)
}

fn degree(entry: &Value) -> bool {
    entry.get("degree").is_some_and(truthy)
}

/// The page-data key of a value's modal.
#[must_use]
pub fn modal_key(entry: &Value, value: &str) -> String {
    if degree(entry) {
        format!("choice:{}", text(entry, "key"))
    } else {
        format!("choice:{}={value}", text(entry, "key"))
    }
}

/// The file a value's modal is written in.
#[must_use]
pub fn modal_file(tree: &Path, entry: &Value, value: &str) -> PathBuf {
    let name = if degree(entry) {
        text(entry, "key")
    } else {
        format!("{}--{value}", text(entry, "key"))
    };
    tree.join(MODALS).join("choice").join(format!("{name}.md"))
}

/// A value's modal, or None while its file is not written.
///
/// # Errors
/// The file unreadable, or refused as a kind's would be.
pub fn modal(tree: &Path, entry: &Value, value: &str) -> Result<Option<FeatureClass>> {
    let path = modal_file(tree, entry, value);
    if !path.is_file() {
        return Ok(None);
    }
    let body = l7r_gate_core::record::read_text(&path)
        .map_err(|e| Error::new("OSError", format!("{e}: '{}'", path.display())))?;
    let name = path
        .file_name()
        .map_or_else(String::new, |n| n.to_string_lossy().into_owned());
    let parts = parse_explanation(Some(&body), &name)?;
    crate::items::resolve(
        tree,
        about_feature(&name, &modal_key(entry, value), &parts)?,
    )
    .map(Some)
}

/// The value a map records for a choice, where it records one that is not null.
fn recorded<'m>(entry: &Value, meta: &'m Map<String, Value>) -> Option<&'m Value> {
    meta.get(&text(entry, "key")).filter(|v| !v.is_null())
}

/// This map's choices, in card order: each recorded choice's name, its value's label and its modal's key ("" while the modal is not
/// written). A recorded value the table does not know is listed by its raw value, so a gap shows.
///
/// # Errors
/// The table or a modal unreadable or refused.
pub fn made(tree: &Path, meta: &Map<String, Value>) -> Result<Vec<Value>> {
    let mut out = Vec::new();
    for entry in table(tree)? {
        let Some(raw) = recorded(&entry, meta) else {
            continue;
        };
        if !applies(&entry, meta)? {
            continue;
        }
        let value = py_str(raw);
        let labels = entry.get("values");
        let label = labels
            .and_then(|l| l.get(&value))
            .cloned()
            .unwrap_or_else(|| {
                Value::String(if degree(&entry) {
                    format!("{value} degrees")
                } else {
                    value.clone()
                })
            });
        let k = if modal(tree, &entry, &value)?.is_some() {
            modal_key(&entry, &value)
        } else {
            String::new()
        };
        out.push(json!({"name": entry.get("name").cloned().unwrap_or(Value::Null), "value": label, "k": k}));
    }
    Ok(out)
}

/// Does this choice belong to this settlement? An entry's `when`, in the conditions' form, names the settlement it is a choice of.
///
/// # Errors
/// A malformed `when`.
pub fn applies(entry: &Value, meta: &Map<String, Value>) -> Result<bool> {
    let when = entry.get("when").map_or_else(String::new, py_str);
    let (conds, _) = conditions::split(&when)?;
    Ok(conditions::holds(conds.as_ref(), meta))
}

/// The modals of this map's choices, by page-data key, in card order.
///
/// # Errors
/// The table or a modal unreadable or refused.
pub fn registry_for(tree: &Path, meta: &Map<String, Value>) -> Result<Vec<FeatureClass>> {
    let mut out: Vec<FeatureClass> = Vec::new();
    for entry in table(tree)? {
        let Some(raw) = recorded(&entry, meta) else {
            continue;
        };
        if !applies(&entry, meta)? {
            continue;
        }
        if let Some(fc) = modal(tree, &entry, &py_str(raw))? {
            match out.iter_mut().find(|o| o.key == fc.key) {
                Some(slot) => *slot = fc,
                None => out.push(fc),
            }
        }
    }
    Ok(out)
}

#[cfg(test)]
mod tests;
