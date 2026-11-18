//! The HTML target: wrap each classed string, take the ink census, assemble and write the page (`interactive/page.py`, feature 134; ported
//! by feature 449 T150, the engine port's step 2, the Python deleted by its part B, held by `page/held.rs`).
//!
//! The page is the map inlined as SVG with every classed string wrapped in its class group ([`hits::wrap`]), the page's CSS and script
//! inlined (a plain `file://` open, no network - spec FR-001), and the explanations of the classes PRESENT embedded as JSON. Nothing here
//! touches the SVG or the PNG (FR-010). The census ([`ink_census`]) counts drawn elements per class and lists the ones that carry NO class
//! - ink nobody has ruled on; a `"-"` tag is a RULING, counted under its own key.
//!
//! Research:
//!     page plumbing - NONE: wrapping, the ink census, merging, hit geometry and assembly
//!     hover and modal presentation - CONVENTION: what lights, how wide a hit band is, what the modal shows

use std::collections::BTreeSet;
use std::path::Path;
use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_gate_registry::about::FeatureClass;
use l7r_gate_research::pyre::py;
use l7r_gate_research::Error;
use serde_json::{json, Map, Value};

use crate::notes::{get, MapNotes};
use crate::tags::{ClsTag, NOT_HIGHLIGHTED, PLACE};

pub mod explain;
pub mod hits;
pub mod merge;
pub mod render;
pub mod value;

pub use explain::{explanations, glossary_for, rendered_text, NOT_RENDERED};
pub use hits::{hit_copies, hit_layer, hit_regions, part_of, wrap};
pub use merge::merge_primitives;
pub use render::{raster_wanted, render_page, write_html, Page};

/// The elements that put ink on the sheet; a `<g>` or `<clipPath>` draws nothing by itself.
static INK: LazyLock<Regex> =
    LazyLock::new(|| py(r"<(rect|circle|ellipse|line|polyline|polygon|path|text|image)\b"));
/// Definitions whose children never paint: stripped before an element is counted.
static NOT_INK: LazyLock<Regex> = LazyLock::new(|| py(r"(?s)<(clipPath|pattern|defs)\b.*?</\1>"));

/// How many unclassed snippets the census keeps - enough to find the emit site, not the whole map.
pub const UNCLASSED_CAP: usize = 20;

/// The repository's interactive assets, where the page's CSS, script and fixed phrases are read from.
pub const ASSETS: &str = "l7r/diagram/interactive/assets";

/// (class, text) for every separately-classed piece of one string - a `Split` once, under its fill class (`page._pieces`).
fn pieces<'a>(s: &'a str, tag: &'a ClsTag) -> Vec<(Option<&'a str>, &'a str)> {
    match tag {
        ClsTag::Unruled => vec![(None, s)],
        ClsTag::Key(k) => vec![(Some(k.name.as_str()), s)],
        ClsTag::Split { fill, .. } => vec![(Some(fill.as_str()), s)],
        ClsTag::Parts(parts) => parts
            .iter()
            .map(|(c, p)| (c.as_ref().map(|k| k.name.as_str()), p.as_str()))
            .collect(),
    }
}

/// `<name> <the piece's first 80 characters>` (`page._snippet`).
fn snippet(piece: &str) -> String {
    // "?" where the piece names no ink element, as the Python's; never on a piece the census counted, which holds one
    let mut name = "?".to_owned();
    if let Some(c) = INK.captures(piece).ok().flatten() {
        c[1].clone_into(&mut name);
    }
    format!("<{name}> {}", piece.chars().take(80).collect::<String>())
}

/// Drawn elements per class, in order of first count, and the ones with no class (capped, with a final "... and N more") (`page.ink_census`).
/// A merged class counts its tile paths since feature 222, a measure of spread rather than density.
#[must_use]
pub fn ink_census(strings: &[String], tags: &[ClsTag]) -> (Vec<(String, i64)>, Vec<String>) {
    let mut counts: Vec<(String, i64)> = Vec::new();
    let mut unclassed: Vec<String> = Vec::new();
    let mut more = 0;
    for (s, tag) in strings.iter().zip(tags) {
        for (key, piece) in pieces(s, tag) {
            let stripped = NOT_INK.replace_all(piece, "");
            let n = INK.find_iter(&stripped).flatten().count();
            if n == 0 {
                continue;
            }
            let Some(key) = key else {
                if unclassed.len() < UNCLASSED_CAP {
                    unclassed.push(snippet(piece));
                } else {
                    more += 1;
                }
                continue;
            };
            let n = i64::try_from(n).unwrap_or(i64::MAX);
            match counts.iter_mut().find(|(k, _)| k == key) {
                Some((_, c)) => *c += n,
                None => counts.push((key.to_owned(), n)),
            }
        }
    }
    if more > 0 {
        unclassed.push(format!("... and {more} more"));
    }
    (counts, unclassed)
}

/// Class keys tagged that the registry has no entry for, sorted (`page.unregistered_classes`): a typo, or a class not named yet.
#[must_use]
pub fn unregistered_classes(counts: &[(String, i64)], registry: &[FeatureClass]) -> Vec<String> {
    let mut out: Vec<String> = counts
        .iter()
        .map(|(k, _)| k.clone())
        .filter(|k| k != NOT_HIGHLIGHTED && k != PLACE && !registry.iter().any(|fc| fc.key == *k))
        .collect();
    out.sort();
    out
}

/// Every class a tag names, but the ruling (`page.present_classes`).
#[must_use]
pub fn present_classes(tags: &[ClsTag]) -> BTreeSet<String> {
    let mut keys = BTreeSet::new();
    for tag in tags {
        match tag {
            ClsTag::Key(k) => {
                keys.insert(k.name.clone());
            }
            ClsTag::Split { fill, stroke } => {
                keys.insert(fill.clone());
                keys.insert(stroke.clone());
            }
            ClsTag::Parts(parts) => keys.extend(
                parts
                    .iter()
                    .filter_map(|(k, _)| k.as_ref().map(|k| k.name.clone())),
            ),
            ClsTag::Unruled => {}
        }
    }
    keys.remove(NOT_HIGHLIGHTED);
    keys
}

/// `assets/<name>`'s text.
///
/// # Errors
/// The file unreadable, as Python's `open`.
pub fn asset(tree: &Path, name: &str) -> Result<String, Error> {
    let path = tree.join(ASSETS).join(name);
    crate::reads::note(&path);
    l7r_gate_core::record::read_text(&path)
        .map_err(|e| crate::py::os_error(&e, &path.to_string_lossy()))
}

/// The BROAD kinds, over which the cursor stays the normal arrow (GM 2026-09-26: *"very large things don't need to turn the mouse into a
/// pointer"*), read from `page-text.json`.
///
/// # Errors
/// The file unreadable or not JSON.
///
/// Research: the broad kinds' cursor - CONVENTION: the arrow over the kinds `page-text.json` lists, the link hand over every other clickable kind (the GM 2026-09-26)
pub fn plain_cursor(tree: &Path) -> Result<Vec<String>, Error> {
    crate::reads::asset(tree, "page-text.json");
    let text = l7r_gate_research::content::content(tree, "page-text.json")?;
    crate::py::iterate(text.get("plain_cursor").unwrap_or(&Value::Null))
        .map(|v| v.iter().map(l7r_guard::shared::pyjson::py_str).collect())
}

/// `notes.features.get(key, "")`.
fn on_this_map(notes: &MapNotes, key: &str) -> String {
    get(&notes.features, key).unwrap_or_default().to_owned()
}

/// The `meta` value of `key` as `str(meta.get(key) or "")`.
#[must_use]
pub fn meta_str(meta: &Map<String, Value>, key: &str) -> String {
    meta.get(key)
        .filter(|v| l7r_guard::shared::pyjson::truthy(v))
        .map_or_else(String::new, l7r_guard::shared::pyjson::py_str)
}

/// A stub for a present key the registry does not know: it says so, never silence.
///
/// Research: a kind the registry does not know - CONVENTION: its modal says so on its About tab, never silence
fn stub(key: &str) -> Value {
    json!({
        "name": key,
        "about": ["This kind of feature has no entry in the class registry yet (interactive/classes/); the gate reports it."],
        "guesses": [], "depiction": [], "drawing": [], "questions": [], "siblings": [], "on_this_map": "",
    })
}

#[cfg(test)]
pub(crate) mod held;
#[cfg(test)]
mod tests;
