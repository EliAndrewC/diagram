//! The glossary the map's explanations and the record's pages share (`interactive/glossary.py`, feature 134; ported by feature 449 T148,
//! phase 4's S5, `ask:449-phase4-slices`): the terms read from `assets/glossary.json`, and the record's copy of them, the script
//! `research/assets/glossary.js` the site carries (feature 209). The page writer (`page.py`, S7) still reads the glossary through the
//! Python `glossary.py`, which only reads; every write of the glossary's files is this crate's (FR-003, `ask:449-T81-slices`).
//!
//! The one-word-per-file source the JSON is assembled from is [`source`] (`glossary_source.py`, feature 259).

use std::path::Path;

use serde_json::{json, Map, Value};

use crate::{content, Error, Result};

pub mod source;

/// One term: the variants matched in the prose, its definition, and whether its variants match only as written (`"cased": true`,
/// feature 265 FR-003: `ochiba`, the fallen leaves, must not wrap Ochiba, the manor of that name).
#[derive(Debug, Clone, PartialEq)]
pub struct Term {
    pub term: String,
    pub variants: Vec<String>,
    pub definition: Value,
    pub cased: bool,
}

/// `GLOSSARY` and `CASED` as the module builds them at import: each term of `glossary.json` in the file's order, its `variants` and
/// `def` indexed as the Python indexes them (a missing one Python's `KeyError`).
///
/// # Errors
/// The file unreadable or not JSON, an entry that is not an object, or one with no `variants` or `def`.
pub fn load(tree: &Path) -> Result<Vec<Term>> {
    let data = content::content(tree, "glossary.json")?;
    let Value::Object(map) = data else {
        return Err(Error::new(
            "AttributeError",
            format!(
                "'{}' object has no attribute 'items'",
                l7r_guard::shared::blocked::type_name(&data)
            ),
        ));
    };
    map.iter()
        .map(|(term, entry)| term_of(term, entry))
        .collect()
}

fn term_of(term: &str, entry: &Value) -> Result<Term> {
    let field = |k: &str| {
        entry
            .get(k)
            .ok_or_else(|| Error::new("KeyError", format!("'{k}'")))
    };
    let variants = match field("variants")? {
        Value::Array(items) => items
            .iter()
            .map(|v| v.as_str().map(str::to_owned).ok_or_else(not_text))
            .collect::<Result<Vec<String>>>()?,
        _ => return Err(not_text()),
    };
    Ok(Term {
        term: term.to_owned(),
        variants,
        definition: field("def")?.clone(),
        cased: entry
            .get("cased")
            .is_some_and(l7r_guard::shared::pyjson::truthy),
    })
}

/// A variant that is not text: the record's glossary holds strings only, and a reader of one that is not would fail as the Python's
/// `len()` and `lower()` do.
fn not_text() -> Error {
    Error::new("TypeError", "a glossary variant is text")
}

/// The record's copy of the glossary as the script `glossary.js` (`record_glossary_js`, feature 209): each term with its variants longest
/// first (a stable sort, so "head race" wins over "head" and equals keep their order), its definition, and `cased` where it is.
#[must_use]
pub fn record_glossary_js(terms: &[Term]) -> String {
    let entries: Vec<Value> = terms
        .iter()
        .map(|t| {
            let mut variants = t.variants.clone();
            variants.sort_by_key(|v| std::cmp::Reverse(v.chars().count()));
            let mut entry = Map::new();
            entry.insert("term".into(), json!(t.term));
            entry.insert("variants".into(), json!(variants));
            entry.insert("def".into(), t.definition.clone());
            if t.cased {
                entry.insert("cased".into(), Value::Bool(true));
            }
            Value::Object(entry)
        })
        .collect();
    format!(
        "// DERIVED FILE - written by `make glossary` from l7r/diagram/interactive/assets/glossary.json (features 207 and 209). Never\n\
         // edit here: add or change a term in glossary.json and run `make glossary`; the gate fails while the two differ.\n\
         window.RECORD_GLOSSARY = {};\n",
        l7r_guard::shared::pyjson::dumps(&Value::Array(entries), Some(1), false)
    )
}

#[cfg(test)]
mod tests;
