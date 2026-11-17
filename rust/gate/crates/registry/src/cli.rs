//! `l7r-gate registry <verb>` (feature 449 T149): `dump`, the library's reading of a tree - both registries, the rulings, the knobs, the
//! choices table, and for each map's recorded knobs what its page would show - which the slice's differential compares with the Python's
//! reading of the same tree (`ask:449-phase4-slices` Q1: a slice's Rust is held to the Python it mirrors on the real inputs); and
//! `silent`, `make audit`'s list of the declared silences, which the Makefile asked of the Python in one line.

use std::path::Path;

use l7r_gate_core::Reply;
use l7r_gate_research::{Error, Result};
use serde_json::{json, Map, Value};

use crate::about::{classes, compound_classes, not_highlighted, FeatureClass};
use crate::{choices, conditions, headings};

fn reply(stdout: String, stderr: String, code: i32) -> Reply {
    Reply {
        stdout,
        stderr,
        code,
    }
}

/// A result as the dump writes it: the value, or `{"error": "<kind>: <message>"}` where the Python raised.
fn or_error(result: Result<Value>) -> Value {
    result.unwrap_or_else(|e| json!({"error": format!("{}: {}", e.kind, e.message)}))
}

fn listed(defs: &[FeatureClass]) -> Value {
    Value::Array(defs.iter().map(FeatureClass::json).collect())
}

/// What `page.explanations` shows of one class on a map with these knobs: the conditions checked, then each tab's items shown.
fn shown(tree: &Path, fc: &FeatureClass, meta: &Map<String, Value>) -> Result<Value> {
    let mut conds: Vec<Option<conditions::Cond>> = Vec::new();
    for item in fc.about.iter().chain(&fc.depiction).chain(&fc.guesses) {
        conds.push(conditions::split(item)?.0);
    }
    let on_entry = conditions::entry_conditions(&fc.entry)?;
    let on_drawing = conditions::entry_conditions(&fc.drawing)?;
    conds.extend(
        on_entry
            .iter()
            .chain(&on_drawing)
            .map(|(_, c)| Some(c.clone())),
    );
    conditions::check(tree, &fc.name, &conds)?;
    let line = |text: &str, had: bool| -> Result<String> {
        if had {
            conditions::shown_entry(text, meta)
        } else {
            Ok(text.to_owned())
        }
    };
    let labels: Vec<String> = conds.iter().flatten().map(conditions::label).collect();
    Ok(json!({
        "entry": line(&fc.entry, !on_entry.is_empty())?,
        "about": conditions::shown(&fc.about, meta)?,
        "guesses": conditions::shown(&fc.guesses, meta)?,
        "depiction": conditions::shown(&fc.depiction, meta)?,
        "drawing": line(&fc.drawing, !on_drawing.is_empty())?,
        "stripped": conditions::strip_entry(&fc.entry),
        "labels": labels,
    }))
}

/// One map's knobs read: what its title card lists and what each class's modal shows there.
fn map_view(
    tree: &Path,
    meta: &Map<String, Value>,
    registries: &[(&str, &[FeatureClass])],
) -> Value {
    let mut out = Map::new();
    out.insert(
        "made".into(),
        or_error(choices::made(tree, meta).map(Value::Array)),
    );
    out.insert(
        "registry_for".into(),
        or_error(choices::registry_for(tree, meta).map(|r| listed(&r))),
    );
    for (name, defs) in registries {
        let views: Map<String, Value> = defs
            .iter()
            .map(|fc| (fc.key.clone(), or_error(shown(tree, fc, meta))))
            .collect();
        out.insert((*name).to_owned(), Value::Object(views));
    }
    Value::Object(out)
}

/// A map's recorded knobs: its manifest's `meta`, or the file's whole object where it has none.
fn meta_of(path: &Path) -> Result<Map<String, Value>> {
    let text = l7r_gate_core::record::read_text(path)
        .map_err(|e| Error::new("OSError", format!("{e}: '{}'", path.display())))?;
    let value: Value =
        serde_json::from_str(&text).map_err(|e| Error::new("JSONDecodeError", e.to_string()))?;
    let meta = value.get("meta").cloned().unwrap_or(value);
    Ok(meta.as_object().cloned().unwrap_or_default())
}

/// The dump of the tree at `tree`, with a view of each map whose manifest is in `maps`.
#[must_use]
pub fn dump(tree: &Path, maps: &[String]) -> Value {
    let hamlet = classes(tree);
    let sheet = compound_classes(tree);
    let mut out = Map::new();
    out.insert(
        "classes".into(),
        or_error(hamlet.clone().map(|d| listed(&d))),
    );
    out.insert(
        "compound".into(),
        or_error(sheet.clone().map(|d| listed(&d))),
    );
    out.insert(
        "rulings".into(),
        or_error(
            not_highlighted(tree).map(|(r, o)| json!({"not_highlighted": r, "overturned": o})),
        ),
    );
    out.insert(
        "knobs".into(),
        or_error(
            conditions::knobs(tree)
                .map(|k| Value::Object(k.into_iter().map(|(n, f)| (n, Value::Array(f))).collect())),
        ),
    );
    out.insert(
        "knob_table".into(),
        or_error(conditions::knob_table(tree).map(Value::Object)),
    );
    out.insert(
        "choices".into(),
        or_error(choices::table(tree).map(Value::Array)),
    );
    out.insert(
        "not_choices".into(),
        or_error(choices::not_choices(tree).map(Value::Object)),
    );
    let (hamlet, sheet) = (hamlet.unwrap_or_default(), sheet.unwrap_or_default());
    let registries: [(&str, &[FeatureClass]); 2] = [("hamlet", &hamlet), ("sheet", &sheet)];
    let views: Map<String, Value> = maps
        .iter()
        .map(|m| {
            let view = meta_of(Path::new(m)).map(|meta| map_view(tree, &meta, &registries));
            (m.clone(), or_error(view))
        })
        .collect();
    out.insert("maps".into(), Value::Object(views));
    Value::Object(out)
}

/// `--root <dir>` and the rest, in order.
fn root_and_rest(args: &[String]) -> (String, Vec<String>) {
    let mut root = ".".to_owned();
    let mut rest = Vec::new();
    let mut it = args.iter();
    while let Some(a) = it.next() {
        if a == "--root" {
            root = it.next().cloned().unwrap_or_default();
        } else {
            rest.push(a.clone());
        }
    }
    (root, rest)
}

/// `l7r-gate registry dump [--root DIR] [MANIFEST...]` | `silent [--root DIR]`.
#[must_use]
pub fn cli(args: &[String]) -> Reply {
    let (root, rest) = root_and_rest(args.get(1..).unwrap_or(&[]));
    let tree = l7r_gate_research::resolve(Path::new(&root));
    match args.first().map(String::as_str) {
        Some("dump") => reply(
            l7r_guard::shared::pyjson::dumps(&dump(&tree, &rest), Some(1), false) + "\n",
            String::new(),
            0,
        ),
        Some("silent") => match headings::silent_listing(&tree) {
            Ok(text) => reply(text, String::new(), 0),
            Err(e) => reply(String::new(), format!("{}: {}\n", e.kind, e.message), 1),
        },
        _ => reply(
            String::new(),
            "usage: l7r-gate registry dump [--root DIR] [MANIFEST...] | silent [--root DIR]\n"
                .to_owned(),
            2,
        ),
    }
}

#[cfg(test)]
mod tests;
