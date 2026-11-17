//! What a kind's modal says, read from its Markdown file (feature 449 T149, `ask:449-phase4-slices` Q5): `classes/_base.py`'s machinery
//! ported - the [`FeatureClass`] the page reads, the About form's parser ([`parse_explanation`]) and its refusals ([`about_feature`]), the
//! sibling texts installed both ways, the not-highlighted rulings - and the two registries built as `classes/__init__.py` and
//! `compound_kinds/__init__.py` build `CLASSES` and `COMPOUND_CLASSES`.
//!
//! THE PROSE IS THE FILE (feature 319, plan D12, the GM 2026-10-03): `assets/modals/<hamlet|sheet>/<slug of the key>.md`, read here as
//! Python's text mode reads it. Feature 319 had already moved every kind's text out of its class docstring, so Q5's move of the prose
//! "verbatim, byte for byte, to one Markdown file per class and compound kind" was complete before this port: the files stay where they
//! are, beside the Python registry that still reads them and now the Rust one (`kinds.rs`), and no modal's id or fingerprint changes
//! (`specs/449-rust-codebase/t149-modal-map.json`, measured). A kind with no file would fall back to its docstring in the Python, and none
//! has one, so here a missing file is the Python's refusal of a kind with no text.
//!
//! Every refusal is the Python's `ValueError` (or `KeyError`, its message the exception's `args[0]`, as the research crate's are), its words byte for byte: the Python raised them at import, so a broken file
//! failed every reader loudly; here [`classes`] and [`compound_classes`] return the first one, in the registry's order.

use std::path::Path;
use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_gate_research::pyre::py;
use l7r_gate_research::{Error, Result};
use l7r_guard::shared::py_text::{repr, split, strip};
use serde_json::{json, Value};

use crate::conditions;
use crate::kinds::{Registry, HAMLET_REGISTRY, SHEET_REGISTRY};

/// Where the modal files are, from the tree's root (`_base.MODALS_DIR`).
pub const MODALS: &str = "l7r/diagram/interactive/assets/modals";

/// The pseudo-class of ink ruled out of highlighting.
pub const NOT_HIGHLIGHTED: &str = "-";

/// The reserved pseudo-class of the title placard (feature 156).
pub const PLACE: &str = "place";

/// The prose tags, then the data tags (feature 207).
pub const TAGS: [&str; 9] = [
    "About",
    "Guesses",
    "Depiction",
    "Name",
    "Covers",
    "Sources",
    "Entry",
    "Drawing",
    "Form",
];

/// The data tags: what is not a modal's explanation prose.
pub const DATA_TAGS: [&str; 6] = ["Name", "Covers", "Sources", "Entry", "Drawing", "Form"];

/// The retired tags (feature 319), still recognized so a file carrying one is refused by name - never read as part of the paragraph
/// above it. Don't drop them from the pattern: an unrecognized `Why:` line would silently join the About text.
const RETIRED: [&str; 5] = ["What", "Why", "Note", "Caveat", "Label"];

/// The required data tags; `Form:` and `Drawing:` are optional.
const ABOUT_DATA_TAGS: [&str; 4] = ["Name", "Covers", "Sources", "Entry"];

/// A tag's line: the tag at the start, a colon, one optional space, the value.
static TAG_LINE: LazyLock<Regex> = LazyLock::new(|| {
    py(&format!(
        r"^({}):\s?(.*)$",
        TAGS.iter()
            .chain(RETIRED.iter())
            .copied()
            .collect::<Vec<_>>()
            .join("|")
    ))
});

/// THE OLDER MAPS ARE NEVER MENTIONED (the GM, 2026-10-04, `dev/modals.md` M21): older, earlier, legacy, frozen or hand-drawn MAPS, and
/// the frozen or legacy POOL; a sheet's "hand-drawn plans" are building plans, which stay.
static OLDER_MAPS: LazyLock<Regex> = LazyLock::new(|| {
    py(
        r"(?i)\b(?:older|earlier|legacy|frozen|hand[- ](?:drawn|authored|made))\b(?:[ -]\w+){0,2}[ -](?:maps?|pool)\b",
    )
});

/// One highlightable kind of thing on the map, and what its modal says (`_base.FeatureClass`).
#[derive(Debug, Clone, PartialEq, Eq, Default)]
pub struct FeatureClass {
    pub key: String,
    pub name: String,
    pub covers: String,
    pub sources: Vec<String>,
    pub entry: String,
    /// sibling key -> how this class differs from it, in the order the pairs installed them
    pub siblings: Vec<(String, String)>,
    pub about: Vec<String>,
    pub guesses: Vec<String>,
    pub form: String,
    pub depiction: Vec<String>,
    pub drawing: String,
}

impl FeatureClass {
    /// The fields as `dataclasses.asdict` lists them.
    #[must_use]
    pub fn json(&self) -> Value {
        let siblings: serde_json::Map<String, Value> = self
            .siblings
            .iter()
            .map(|(k, v)| (k.clone(), json!(v)))
            .collect();
        json!({
            "key": self.key, "name": self.name, "covers": self.covers, "sources": self.sources, "entry": self.entry,
            "siblings": siblings, "about": self.about, "guesses": self.guesses, "form": self.form,
            "depiction": self.depiction, "drawing": self.drawing,
        })
    }
}

/// The CSS token for a class key: every character outside `[a-z0-9-]` a hyphen (feature 262).
#[must_use]
pub fn slug(key: &str) -> String {
    key.to_lowercase()
        .chars()
        .map(|c| {
            if c.is_ascii_lowercase() || c.is_ascii_digit() || c == '-' {
                c
            } else {
                '-'
            }
        })
        .collect()
}

/// A kind's modal file, repository-relative (`_base.modal_path`).
#[must_use]
pub fn modal_rel(registry: &Registry, key: &str) -> String {
    format!("{MODALS}/{}/{}.md", registry.dir, slug(key))
}

/// `str.expandtabs()`: a tab to the next multiple of eight, the column counted from the last line end.
fn expandtabs(text: &str) -> String {
    let mut out = String::with_capacity(text.len());
    let mut column = 0;
    for c in text.chars() {
        match c {
            '\t' => {
                let n = 8 - column % 8;
                out.extend(std::iter::repeat_n(' ', n));
                column += n;
            }
            '\n' | '\r' => {
                out.push(c);
                column = 0;
            }
            _ => {
                out.push(c);
                column += 1;
            }
        }
    }
    out
}

/// The tagged sections of a modal's text, in the order first met (`parse_explanation`): each tag at the start of a line, each value
/// running to the next tag, wrapped lines joined with one space; `inspect.cleandoc` first, whose only effect on stripped lines is
/// its tab expansion.
///
/// # Errors
/// No text, a line before the first tag, or no `About:` - the Python's `ValueError`, naming the class.
pub fn parse_explanation(doc: Option<&str>, name: &str) -> Result<Vec<(String, String)>> {
    let Some(doc) = doc.filter(|d| !strip(d).is_empty()) else {
        return Err(value_error(format!(
            "{name}: the explanation is the docstring, and there is none"
        )));
    };
    let mut out: Vec<(String, Vec<String>)> = Vec::new();
    let mut cur: Option<usize> = None;
    let text = expandtabs(doc);
    for raw in l7r_gate_core::record::py_lines(&text) {
        let line = strip(raw);
        if let Ok(Some(m)) = TAG_LINE.captures(line) {
            let tag = m[1].to_owned();
            let value = if m[2].is_empty() {
                Vec::new()
            } else {
                vec![m[2].to_owned()]
            };
            let at = out.iter().position(|(t, _)| *t == tag).unwrap_or_else(|| {
                out.push((tag, Vec::new()));
                out.len() - 1
            });
            out[at].1 = value;
            cur = Some(at);
            continue;
        }
        if line.is_empty() {
            if let Some(at) = cur.filter(|at| paragraphed(&out[*at].0) && !out[*at].1.is_empty()) {
                out[at].1.push(String::new());
            }
            continue;
        }
        let Some(at) = cur else {
            let head: String = line.chars().take(40).collect();
            return Err(value_error(format!(
                "{name}: text before the first tag ({}) - every line belongs to a tag, About: first",
                repr(&head)
            )));
        };
        out[at].1.push(line.to_owned());
    }
    let got: Vec<(String, String)> = out.iter().map(|(t, v)| (t.clone(), join(t, v))).collect();
    if get(&got, "About").is_empty() {
        return Err(value_error(format!(
            "{name}: the docstring has no About: section"
        )));
    }
    Ok(got)
}

fn paragraphed(tag: &str) -> bool {
    tag == "About" || tag == "Depiction"
}

fn value_error(message: String) -> Error {
    Error::new("ValueError", message)
}

/// A parsed tag's value, "" where the text has none (`parts.get(tag, "")`).
#[must_use]
pub fn get<'a>(parts: &'a [(String, String)], tag: &str) -> &'a str {
    parts
        .iter()
        .find(|(t, _)| t == tag)
        .map_or("", |(_, v)| v.as_str())
}

fn has(parts: &[(String, String)], tag: &str) -> bool {
    parts.iter().any(|(t, _)| t == tag)
}

/// One tag's value: wrapped lines joined with one space; `About:` and `Depiction:` keep their paragraph breaks, `Guesses:` its bullets.
fn join(tag: &str, lines: &[String]) -> String {
    if paragraphed(tag) {
        let mut paras: Vec<Vec<&str>> = vec![Vec::new()];
        for line in lines {
            if !line.is_empty() {
                if let Some(p) = paras.last_mut() {
                    p.push(line.as_str());
                }
            } else if paras.last().is_some_and(|p| !p.is_empty()) {
                paras.push(Vec::new());
            }
        }
        let body: Vec<String> = paras
            .iter()
            .filter(|p| !p.is_empty())
            .map(|p| p.join(" "))
            .collect();
        return strip(&body.join("\n\n")).to_owned();
    }
    if tag == "Guesses" {
        let mut bullets: Vec<Vec<&str>> = Vec::new();
        for line in lines {
            if line.starts_with("- ") || bullets.is_empty() {
                bullets.push(vec![line.as_str()]);
            } else if let Some(b) = bullets.last_mut() {
                b.push(line.as_str());
            }
        }
        let body: Vec<String> = bullets.iter().map(|b| b.join(" ")).collect();
        return strip(&body.join("\n")).to_owned();
    }
    strip(&lines.join(" ")).to_owned()
}

/// The About tab's paragraphs from a parsed value.
#[must_use]
pub fn about_paragraphs(text: &str) -> Vec<String> {
    text.split("\n\n")
        .filter(|p| !strip(p).is_empty())
        .map(|p| split(p).join(" "))
        .collect()
}

/// The Guesses tab's bullets from a parsed value, each without its `- `.
#[must_use]
pub fn guess_bullets(text: &str) -> Vec<String> {
    l7r_gate_core::record::py_lines(text)
        .into_iter()
        .filter(|l| !strip(l).is_empty())
        .map(|l| strip(&l.chars().skip(2).collect::<String>()).to_owned())
        .collect()
}

/// A kind's [`FeatureClass`] from its parsed text (`_about_feature`), refusing what the About form does not take.
///
/// # Errors
/// A required tag missing, a retired tag, an unknown `Form:`, a drawing page under `Entry:`, the older maps named, a guess that is not a
/// bullet, or a malformed knob condition - each the Python's `ValueError`, naming the kind.
pub fn about_feature(name: &str, key: &str, parts: &[(String, String)]) -> Result<FeatureClass> {
    for tag in ABOUT_DATA_TAGS {
        if get(parts, tag).is_empty() {
            return Err(value_error(format!(
                "{name}: the docstring has no {tag}: section"
            )));
        }
    }
    if has(parts, "Label") {
        return Err(value_error(format!("{name}: the About form takes no Label: - a guess is a bullet under Guesses: (dev/modals.md M11)")));
    }
    let old: Vec<String> = RETIRED
        .iter()
        .filter(|t| **t != "Label" && has(parts, t))
        .map(|t| format!("{t}:"))
        .collect();
    if !old.is_empty() {
        return Err(value_error(format!(
            "{name}: the About form replaces What/Why/Note/Caveat - remove {}",
            old.join(", ")
        )));
    }
    let form = if has(parts, "Form") {
        get(parts, "Form")
    } else {
        "standard"
    };
    if form != "standard" && form != "particular" {
        return Err(value_error(format!(
            "{name}: Form: {} is not one of ['particular', 'standard']",
            repr(form)
        )));
    }
    let entry = get(parts, "Entry");
    if entry.contains(".drawing.html") {
        return Err(value_error(format!("{name}: a 'how our maps draw it' page belongs under Drawing:, not Entry: (the Depiction tab - dev/modals.md D-rules)")));
    }
    for tag in ["About", "Guesses", "Depiction"] {
        if let Ok(Some(hit)) = OLDER_MAPS.find(get(parts, tag)) {
            return Err(value_error(format!(
                "{name}: {tag}: names the older maps ({}) - they will all be scripted before anyone else reads this; say what the scripted maps do and drop the exception (dev/modals.md M21)",
                repr(hit.as_str())
            )));
        }
    }
    let raw_guesses = get(parts, "Guesses");
    if !raw_guesses.is_empty()
        && !l7r_gate_core::record::py_lines(raw_guesses)
            .iter()
            .all(|l| l.starts_with("- "))
    {
        return Err(value_error(format!(
            "{name}: each guess is a bullet - start every line under Guesses: with '- '"
        )));
    }
    let about = about_paragraphs(get(parts, "About"));
    let depiction = about_paragraphs(get(parts, "Depiction"));
    let guesses = guess_bullets(raw_guesses);
    for item in about.iter().chain(&depiction).chain(&guesses) {
        if let Err(e) = conditions::split(item) {
            return Err(value_error(format!("{name}: {}", e.message)));
        }
    }
    Ok(FeatureClass {
        key: key.to_owned(),
        name: get(parts, "Name").to_owned(),
        covers: get(parts, "Covers").to_owned(),
        sources: get(parts, "Sources")
            .split(',')
            .map(strip)
            .filter(|s| !s.is_empty())
            .map(str::to_owned)
            .collect(),
        entry: entry.to_owned(),
        siblings: Vec::new(),
        about,
        guesses,
        form: form.to_owned(),
        depiction,
        drawing: get(parts, "Drawing").to_owned(),
    })
}

/// A kind's modal text: its file as Python's text mode reads it, or None where it has none (and the Python fell back to a docstring no
/// kind carries).
///
/// # Errors
/// A file that cannot be read as UTF-8.
pub fn modal_text(tree: &Path, registry: &Registry, key: &str) -> Result<Option<String>> {
    let path = tree.join(modal_rel(registry, key));
    if !path.is_file() {
        return Ok(None);
    }
    l7r_gate_core::record::read_text(&path)
        .map(Some)
        .map_err(|e| Error::new("OSError", format!("{e}: '{}'", path.display())))
}

/// One kind's [`FeatureClass`] (`Kind.feature()`).
///
/// # Errors
/// What [`parse_explanation`] and [`about_feature`] refuse, or an unreadable file.
pub fn feature(tree: &Path, registry: &Registry, class: &str, key: &str) -> Result<FeatureClass> {
    let text = modal_text(tree, registry, key)?;
    about_feature(class, key, &parse_explanation(text.as_deref(), class)?)
}

/// The registry by key, each sibling pair's text installed both ways (`install_siblings`); a pair naming no kind is the Python's `KeyError`.
///
/// # Errors
/// A pair naming a key the registry does not hold.
pub fn install_siblings(
    defs: Vec<FeatureClass>,
    pairs: &[((String, String), String)],
) -> Result<Vec<FeatureClass>> {
    let mut by_key: Vec<FeatureClass> = Vec::new();
    for d in defs {
        match by_key.iter().position(|b| b.key == d.key) {
            Some(at) => by_key[at] = d,
            None => by_key.push(d),
        }
    }
    let find = |by_key: &[FeatureClass], k: &str| by_key.iter().position(|d| d.key == k);
    for ((a, b), text) in pairs {
        let (Some(ia), Some(ib)) = (find(&by_key, a), find(&by_key, b)) else {
            return Err(Error::new(
                "KeyError",
                format!(
                    "sibling pair names an unknown class: ({}, {})",
                    repr(a),
                    repr(b)
                ),
            ));
        };
        set(&mut by_key[ia].siblings, b, text);
        set(&mut by_key[ib].siblings, a, text);
    }
    Ok(by_key)
}

/// `d[key] = value`: a key already there keeps its place.
fn set(map: &mut Vec<(String, String)>, key: &str, value: &str) {
    match map.iter_mut().find(|(k, _)| k == key) {
        Some(slot) => value.clone_into(&mut slot.1),
        None => map.push((key.to_owned(), value.to_owned())),
    }
}

/// The hamlet sibling pairs, from `assets/siblings.json` (`classes/siblings.py`): a text beginning `@` names a shared passage.
///
/// # Errors
/// The file unreadable or not JSON, or a pair naming a shared passage the file does not hold (`KeyError`).
pub fn sibling_pairs(tree: &Path) -> Result<Vec<((String, String), String)>> {
    let raw = l7r_gate_research::content::content(tree, "siblings.json")?;
    let texts = raw.get("texts").cloned().unwrap_or(Value::Null);
    let mut out: Vec<((String, String), String)> = Vec::new();
    for pair in raw
        .get("pairs")
        .and_then(Value::as_array)
        .into_iter()
        .flatten()
    {
        let part = |i: usize| pair.get(i).and_then(Value::as_str).unwrap_or("").to_owned();
        let (a, b, text) = (part(0), part(1), part(2));
        let text = match text.strip_prefix('@') {
            Some(name) => texts
                .get(name)
                .and_then(Value::as_str)
                .map(str::to_owned)
                .ok_or_else(|| Error::new("KeyError", name))?,
            None => text,
        };
        match out.iter_mut().find(|(k, _)| k.0 == a && k.1 == b) {
            Some(slot) => slot.1 = text,
            None => out.push(((a, b), text)),
        }
    }
    Ok(out)
}

/// A registry's kinds as their `FeatureClass`es, in its order, its sibling pairs installed.
fn build(
    tree: &Path,
    registry: &Registry,
    pairs: &[((String, String), String)],
) -> Result<Vec<FeatureClass>> {
    let defs = registry
        .kinds()
        .into_iter()
        .map(|(_, k)| feature(tree, registry, k.class, k.key))
        .collect::<Result<Vec<_>>>()?;
    install_siblings(defs, pairs)
}

/// Every feature class of the hamlet vocabulary, in the spec's FR-007 order (`CLASSES`).
///
/// # Errors
/// The first kind whose file is missing or refused, or a sibling pair that does not resolve.
pub fn classes(tree: &Path) -> Result<Vec<FeatureClass>> {
    build(tree, &HAMLET_REGISTRY, &sibling_pairs(tree)?)
}

/// Every Mode A kind, in its families' order (`COMPOUND_CLASSES`); its sibling pairs are none.
///
/// # Errors
/// The first kind whose file is missing or refused.
pub fn compound_classes(tree: &Path) -> Result<Vec<FeatureClass>> {
    build(tree, &SHEET_REGISTRY, &[])
}

/// One ruling of the not-highlighted list: what, who, when, why.
pub type Ruling = [String; 4];

/// The rulings standing and the rulings overturned.
pub type Rulings = (Vec<Ruling>, Vec<Ruling>);

/// The not-highlighted rulings and the overturned ones, `(what, who, when, why)` each, from `assets/page-text.json`.
///
/// # Errors
/// The file unreadable or not JSON.
pub fn not_highlighted(tree: &Path) -> Result<Rulings> {
    let text = l7r_gate_research::content::content(tree, "page-text.json")?;
    let rows = |name: &str| -> Vec<Ruling> {
        text.get(name)
            .and_then(Value::as_array)
            .into_iter()
            .flatten()
            .map(|r| {
                std::array::from_fn(|i| {
                    r.get(i)
                        .map_or_else(String::new, l7r_guard::shared::pyjson::py_str)
                })
            })
            .collect()
    };
    Ok((
        rows("not_highlighted_rulings"),
        rows("not_highlighted_overturned"),
    ))
}

#[cfg(test)]
mod tests;
