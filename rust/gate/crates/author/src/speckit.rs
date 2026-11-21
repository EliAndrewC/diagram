//! Spec-kit's two JSON reads (feature 449 T143, `ask:449-phase4-slices` Q12): the inline Python of `.specify/scripts/bash/common.sh`,
//! ported as it read, each its own command the shell runs in its place - `l7r-gate speckit feature-dir <feature.json>` (the
//! `read_feature_json_feature_directory` fallback when there is no `jq`) and `l7r-gate speckit presets <.registry>` (`resolve_template`'s
//! presets in their order). `resolve_template_content` held the other two sites, and nothing called it, so it is deleted, not ported.
//!
//! Both keep the Python's exit: a file that does not read or parse, or is not the shape the Python's `.get` and `.items` needed, exits 1,
//! and `common.sh` takes that branch as it took the Python's failure (an empty directory, the unordered scan of the presets).

use std::cmp::Ordering;
use std::path::Path;

use l7r_gate_core::Reply;
use l7r_shared::pyjson::{py_str, truthy};
use serde_json::Value;

use crate::reply;

const USAGE: &str = "usage: l7r-gate speckit feature-dir <feature.json> | presets <registry>\n";

/// `l7r-gate speckit <verb> <file>`.
#[must_use]
pub fn cli(args: &[String]) -> Reply {
    let (verb, file) = match args {
        [verb, file] => (verb.as_str(), Path::new(file)),
        _ => return reply(String::new(), USAGE.to_owned(), 2),
    };
    let Some(doc) = std::fs::read(file)
        .ok()
        .and_then(|raw| serde_json::from_slice::<Value>(&raw).ok())
    else {
        return reply(String::new(), String::new(), 1);
    };
    let out = match verb {
        "feature-dir" => feature_dir(&doc),
        "presets" => presets(&doc),
        _ => return reply(String::new(), USAGE.to_owned(), 2),
    };
    out.map_or_else(
        || reply(String::new(), String::new(), 1),
        |text| reply(text, String::new(), 0),
    )
}

/// `v = d.get('feature_directory'); print(v if v else '')`: the value's `str()` when it is true, else an empty line; None where the
/// document is no dict.
fn feature_dir(doc: &Value) -> Option<String> {
    let d = doc.as_object()?;
    let v = d.get("feature_directory").filter(|v| truthy(v));
    Some(v.map(py_str).unwrap_or_default() + "\n")
}

/// The enabled presets' ids, one a line, in the order `sorted(presets.items(), key=priority)` gave them: a stable sort on each preset's
/// `priority` (10 where it has none or is no dict), compared as Python's `<` compares them, and a dict whose `enabled` is not `False`
/// printed. None where the Python raised: the document or its `presets` no dict, or two priorities `<` cannot order.
fn presets(doc: &Value) -> Option<String> {
    let empty = serde_json::Map::new();
    let presets = match doc.as_object()?.get("presets") {
        None => &empty,
        Some(p) => p.as_object()?,
    };
    let ten = Value::from(10);
    let mut items: Vec<(&String, &Value, &Value)> = presets
        .iter()
        .map(|(id, meta)| {
            let priority = meta
                .as_object()
                .map_or(&ten, |m| m.get("priority").unwrap_or(&ten));
            (id, meta, priority)
        })
        .collect();
    let mut raised = false;
    items.sort_by(|a, b| {
        let order = order(a.2, b.2);
        raised |= order.is_none();
        order.unwrap_or(Ordering::Equal)
    });
    if raised {
        return None;
    }
    Some(
        items
            .iter()
            .filter(|(_, meta, _)| {
                meta.as_object()
                    .is_some_and(|m| m.get("enabled") != Some(&Value::Bool(false)))
            })
            .fold(String::new(), |mut out, (id, _, _)| {
                out += id;
                out.push('\n');
                out
            }),
    )
}

/// Python's `<` both ways as an order: None where it raises (`TypeError`).
fn order(a: &Value, b: &Value) -> Option<Ordering> {
    Some(if less(a, b)? {
        Ordering::Less
    } else if less(b, a)? {
        Ordering::Greater
    } else {
        Ordering::Equal
    })
}

/// A number as Python compares one: `True` is 1, `False` 0.
fn number(v: &Value) -> Option<f64> {
    match v {
        Value::Bool(b) => Some(f64::from(u8::from(*b))),
        Value::Number(n) => n.as_f64(),
        _ => None,
    }
}

/// `a < b` as Python answers it for what `json.load` made: numbers by value, strings by code point, lists element by element (the
/// first unequal pair decides, else the shorter is less); None for anything else, which raises.
fn less(left: &Value, right: &Value) -> Option<bool> {
    if let (Some(l), Some(r)) = (number(left), number(right)) {
        return Some(l < r);
    }
    match (left, right) {
        (Value::String(l), Value::String(r)) => Some(l < r),
        (Value::Array(l), Value::Array(r)) => match l.iter().zip(r).find(|(p, q)| !equal(p, q)) {
            Some((p, q)) => less(p, q),
            None => Some(l.len() < r.len()),
        },
        _ => None,
    }
}

/// `a == b` as Python answers it, which never raises: numbers by value, the rest by their contents.
fn equal(a: &Value, b: &Value) -> bool {
    match (number(a), number(b)) {
        // exact, as Python's `==` on numbers is
        (Some(x), Some(y)) => x.partial_cmp(&y) == Some(Ordering::Equal),
        _ => match (a, b) {
            (Value::Array(x), Value::Array(y)) => {
                x.len() == y.len() && x.iter().zip(y).all(|(p, q)| equal(p, q))
            }
            (Value::Object(x), Value::Object(y)) => {
                x.len() == y.len() && x.iter().all(|(k, v)| y.get(k).is_some_and(|w| equal(v, w)))
            }
            _ => a == b,
        },
    }
}

#[cfg(test)]
mod tests;
