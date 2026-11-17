//! The building types' reader (feature 449 T168): `l7r/diagram/buildings/types.py` ported. The declaration is `types.json` beside the
//! Python (feature 254, D1), read, shaped and validated here; a malformed file is refused naming the field, each refusal the Python's
//! `ValueError` (or `TypeError`, `AttributeError`) word for word, since a refusal is a check's output and FR-002 binds it exactly.
//!
//! LOCKSTEP (the round arbiter's `ask:449-engine-order` condition 3): `types.py` stays the implementation for the Python that still
//! imports it (the compound generators, `pool_index`, `poolmaps`, `pack_audit`'s labels and `mapmatch`, `compound_kinds`) until step 3
//! deletes it; an edit of it makes the same change here in the same commit, and `types/tests.rs` holds this parse equal to the Python's on
//! the real `types.json`.
//!
//! A KIND ITEM STATES NO CLASS OR WHY OF ITS OWN (feature 262, FR-003a): its kind's registry entry says what it is, so
//! [`classification`] reads the kind's guesses from the Mode A registry (the gate's `registry` crate, the modal files), loaded the first
//! time a kind item asks - the Python imported the registry lazily there, and a broken modal file failed only a run that reached one.
//!
//! Research:
//!     the building types' reader - NONE: the declaration read and validated; what each type requires is `types.json`'s, and its research is claimed in `docs/building-programs.md`

use std::collections::{BTreeSet, HashMap};
use std::path::Path;

use l7r_gate_research::Error;
use l7r_guard::shared::py_text::repr;
use l7r_guard::shared::pyjson::{py_str, truthy, value_repr};
use serde_json::{Map, Value};

use crate::py::{iterate, os_error, type_name};

/// A required item's classes (`types.CLASSES`).
pub const CLASSES: [&str; 4] = ["accurate", "deviation", "convention", "guess"];

/// The declaration, from the tree's root.
pub const DECLARATION: &str = "l7r/diagram/buildings/types.json";

/// The class column of a kind item (feature 319): the classification lives per statement in the kind's modal.
pub const PER_STATEMENT: &str = "per statement";

/// The why of a kind item whose modal lists no guess.
pub const NOTHING_GUESSED: &str = "nothing guessed";

/// A footprint band in feet: `w` and `h` ranges, or an `area` range in sq ft; none = presence only.
#[derive(Debug, Clone, Copy, PartialEq, Default)]
pub struct Band {
    pub w: Option<(f64, f64)>,
    pub h: Option<(f64, f64)>,
    pub area: Option<(f64, f64)>,
}

impl Band {
    #[must_use]
    pub fn presence_only(&self) -> bool {
        self.w.is_none() && self.h.is_none() && self.area.is_none()
    }

    /// Whether a `w_ft` by `h_ft` footprint lies in the band (either orientation for w/h).
    #[must_use]
    pub fn holds(&self, w_ft: f64, h_ft: f64) -> bool {
        let within = |(lo, hi): (f64, f64), v: f64| lo <= v && v <= hi;
        if self.area.is_some_and(|a| !within(a, w_ft * h_ft)) {
            return false;
        }
        let (Some(w), Some(h)) = (self.w, self.h) else {
            return true;
        };
        (within(w, w_ft) && within(h, h_ft)) || (within(w, h_ft) && within(h, w_ft))
    }
}

/// One item of a type's program: found on a sheet by `label` (a pattern) or, for a tier whose sheets are tagged, by its `kind`
/// (feature 262), and held to `band`. A kind item's `cls` and `why` are empty: [`classification`] reads them from the registry.
#[derive(Debug, Clone, PartialEq)]
pub struct RequiredItem {
    pub id: String,
    /// the pattern's text (`label.pattern`), compiled case-blind where it is matched
    pub label: Option<String>,
    pub band: Band,
    pub cls: String,
    pub why: String,
    pub optional: bool,
    /// a form's own band, or None = absent under that form, in the declaration's order
    pub forms: Vec<(String, Option<Band>)>,
    /// a SITE item (feature 257): its correspondence class
    pub site: Option<String>,
    /// the Mode A kind the item IS (feature 262)
    pub kind: Option<String>,
}

impl RequiredItem {
    /// The band under `form` (a notes file's `**Form**:` value): the form's own, None if the item is absent under it, else the default.
    #[must_use]
    pub fn band_for(&self, form: Option<&str>) -> Option<Band> {
        form.and_then(|f| self.forms.iter().find(|(k, _)| k == f))
            .map_or(Some(self.band), |(_, b)| *b)
    }
}

/// One declared building type.
#[derive(Debug, Clone, PartialEq)]
pub struct BuildingType {
    pub tier: String,
    pub title: String,
    pub program: String,
    pub hand_drawn: bool,
    pub required: Vec<RequiredItem>,
    pub checks: Vec<String>,
    pub generated_exceptions: Vec<String>,
    pub notes: String,
    /// the settlement manifest keys a map records this tier's subject under (feature 294 B24's `**On map**` line)
    pub map_keys: Vec<String>,
}

fn value_error(message: String) -> Error {
    Error::new("ValueError", message)
}

/// `sorted(raw)` of a dict, as Python prints the list.
fn sorted_keys(map: &Map<String, Value>) -> String {
    let mut keys: Vec<&String> = map.keys().collect();
    keys.sort();
    value_repr(&Value::from(
        keys.into_iter()
            .map(|k| Value::from(k.as_str()))
            .collect::<Vec<_>>(),
    ))
}

/// What a refusal shows of `raw`: a dict's sorted keys, else its `repr`.
fn shown(raw: &Value) -> String {
    raw.as_object().map_or_else(|| value_repr(raw), sorted_keys)
}

fn range(value: &Value, at: &str) -> Result<(f64, f64), Error> {
    // a JSON bool passes Python's `isinstance(v, (int, float))`, as `True` is an int
    let number = |v: &Value| match v {
        Value::Bool(b) => Some(f64::from(u8::from(*b))),
        Value::Number(n) => n.as_f64(),
        _ => None,
    };
    if let Some([lo, hi]) = value.as_array().map(Vec::as_slice) {
        if let (Some(lo), Some(hi)) = (number(lo), number(hi)) {
            if lo <= hi {
                return Ok((lo, hi));
            }
        }
    }
    Err(value_error(format!(
        "{at}: a band range is [min, max] with min <= max, not {}",
        value_repr(value)
    )))
}

fn band(raw: &Value, at: &str) -> Result<Band, Error> {
    let Some(map) = raw
        .as_object()
        .filter(|m| m.keys().all(|k| ["w", "h", "area"].contains(&k.as_str())))
    else {
        return Err(value_error(format!(
            "{at}: band_ft carries only w, h and area, not {}",
            value_repr(raw)
        )));
    };
    let get = |k: &str| map.get(k).map(|v| range(v, at)).transpose();
    Ok(Band {
        w: get("w")?,
        h: get("h")?,
        area: get("area")?,
    })
}

fn non_empty_text(v: &Value) -> bool {
    matches!(v, Value::String(s) if !s.is_empty())
}

/// Python's `re.compile(label, re.IGNORECASE)`, for its refusal of a pattern that does not compile. Python's own words for that cannot be
/// reproduced (the regex crate's differ); the differential normalizes them as the library's.
fn compiled(pattern: &str) -> Result<(), Error> {
    let translated = l7r_gate_research::pyre::translate(&format!("(?i){pattern}"));
    fancy_regex::Regex::new(&translated)
        .map(|_| ())
        .map_err(|e| Error::new("re.PatternError", e.to_string()))
}

const ITEM_KEYS: [&str; 9] = [
    "id", "label", "band_ft", "class", "why", "optional", "forms", "site", "kind",
];

fn item(raw: &Value, at: &str) -> Result<RequiredItem, Error> {
    let obj = raw.as_object();
    let has = |k: &&str| obj.is_some_and(|m| m.contains_key(*k));
    let labeled = ["id", "label", "band_ft", "class", "why"].iter().all(has) && !has(&"kind");
    let kinded =
        ["id", "kind", "band_ft"].iter().all(has) && !["label", "class", "why"].iter().any(has);
    let known = obj.is_some_and(|m| m.keys().all(|k| ITEM_KEYS.contains(&k.as_str())));
    let Some(m) = obj.filter(|_| (labeled || kinded) && known) else {
        return Err(value_error(format!(
            "{at}: a required item carries id, label, band_ft, class, why - or id, kind, band_ft, whose class and why are its kind's (feature 262) - (and optional, forms, site), not {}",
            shown(raw)
        )));
    };
    let id = py_str(&m["id"]);
    if let Some(site) = m.get("site").filter(|s| !non_empty_text(s)) {
        return Err(value_error(format!(
            "{at}/{id}: site names a correspondence class (a non-empty string), not {}",
            value_repr(site)
        )));
    }
    if kinded && !non_empty_text(&m["kind"]) {
        return Err(value_error(format!(
            "{at}/{id}: kind names a Mode A kind (a non-empty string), not {}",
            value_repr(&m["kind"])
        )));
    }
    if labeled && !m["class"].as_str().is_some_and(|c| CLASSES.contains(&c)) {
        return Err(value_error(format!(
            "{at}/{id}: class must be one of ('accurate', 'deviation', 'convention', 'guess'), not {}",
            value_repr(&m["class"])
        )));
    }
    // `(raw.get("forms") or {}).items()`: a falsy value is no forms; a truthy one that is not a dict has no `.items`
    let mut forms = Vec::new();
    match m.get("forms").filter(|f| truthy(f)) {
        None => {}
        Some(Value::Object(spec)) => {
            for (form, b) in spec {
                let parsed = if b.is_null() {
                    None
                } else {
                    Some(band(b, &format!("{at}/{id}/forms/{form}"))?)
                };
                forms.push((form.clone(), parsed));
            }
        }
        Some(other) => {
            return Err(Error::new(
                "AttributeError",
                format!("'{}' object has no attribute 'items'", type_name(other)),
            ))
        }
    }
    let label = if labeled {
        let pattern = py_str(&m["label"]);
        compiled(&pattern)?;
        Some(pattern)
    } else {
        None
    };
    let text = |k: &str| m.get(k).map_or_else(String::new, py_str);
    Ok(RequiredItem {
        label,
        band: band(&m["band_ft"], &format!("{at}/{id}"))?,
        cls: text("class"),
        why: text("why"),
        optional: m.get("optional").is_some_and(truthy),
        forms,
        site: m.get("site").map(py_str),
        kind: kinded.then(|| py_str(&m["kind"])),
        id,
    })
}

/// `^[a-z][a-z0-9-]*$` as Python's `re.match` reads it: its `$` also matches before a final newline.
fn kebab(tier: &str) -> bool {
    let t = tier.strip_suffix('\n').unwrap_or(tier);
    let mut chars = t.chars();
    chars.next().is_some_and(|c| c.is_ascii_lowercase())
        && chars.all(|c| c.is_ascii_lowercase() || c.is_ascii_digit() || c == '-')
}

const NEED: [&str; 6] = [
    "checks",
    "hand_drawn",
    "program",
    "required",
    "tier",
    "title",
];

fn texts(value: Option<&Value>) -> Result<Vec<String>, Error> {
    value.map_or_else(
        || Ok(Vec::new()),
        |v| Ok(iterate(v)?.iter().map(py_str).collect()),
    )
}

fn building_type(raw: &Value) -> Result<BuildingType, Error> {
    let allowed =
        |k: &str| NEED.contains(&k) || ["generated_exceptions", "notes", "map_keys"].contains(&k);
    let Some(m) = raw
        .as_object()
        .filter(|m| NEED.iter().all(|k| m.contains_key(*k)) && m.keys().all(|k| allowed(k)))
    else {
        return Err(value_error(format!(
            "a type object carries ['checks', 'hand_drawn', 'program', 'required', 'tier', 'title'] (and generated_exceptions, notes, map_keys), not {}",
            shown(raw)
        )));
    };
    let tier = py_str(&m["tier"]);
    if !kebab(&tier) {
        return Err(value_error(format!(
            "tier {} is not lower-case kebab",
            repr(&tier)
        )));
    }
    let required = iterate(&m["required"])?
        .iter()
        .map(|r| item(r, &tier))
        .collect::<Result<Vec<_>, _>>()?;
    let ids: BTreeSet<&str> = required.iter().map(|i| i.id.as_str()).collect();
    if ids.len() != required.len() {
        return Err(value_error(format!("{tier}: required item ids repeat")));
    }
    Ok(BuildingType {
        title: py_str(&m["title"]),
        program: py_str(&m["program"]),
        hand_drawn: truthy(&m["hand_drawn"]),
        required,
        checks: texts(Some(&m["checks"]))?,
        generated_exceptions: texts(m.get("generated_exceptions"))?,
        notes: m.get("notes").map_or_else(String::new, py_str),
        map_keys: texts(m.get("map_keys"))?,
        tier,
    })
}

/// The declaration's objects as [`BuildingType`]s, refusing a malformed one by name (`parse_types`).
///
/// # Errors
/// The Python's refusal of the first malformed object or field.
pub fn parse_types(data: &Value) -> Result<Vec<BuildingType>, Error> {
    let Some(list) = data.as_array().filter(|l| !l.is_empty()) else {
        return Err(value_error(
            "types.json is a non-empty list of type objects".to_owned(),
        ));
    };
    let out = list
        .iter()
        .map(building_type)
        .collect::<Result<Vec<_>, _>>()?;
    let tiers: BTreeSet<&str> = out.iter().map(|t| t.tier.as_str()).collect();
    if tiers.len() != out.len() {
        return Err(value_error("a tier is declared twice".to_owned()));
    }
    Ok(out)
}

/// The declaration of the tree at `tree` (`load_types`): the file read as Python's text mode reads it, then parsed.
///
/// # Errors
/// The file unreadable (Python's `OSError`), not JSON (its `JSONDecodeError`, the parser's own words), or refused by [`parse_types`].
pub fn load_types(tree: &Path) -> Result<Vec<BuildingType>, Error> {
    let path = tree.join(DECLARATION);
    let text = l7r_gate_core::record::read_text(&path)
        .map_err(|e| os_error(&e, &path.to_string_lossy()))?;
    let data: Value = serde_json::from_str(&text)
        .map_err(|e| Error::new("json.decoder.JSONDecodeError", e.to_string()))?;
    parse_types(&data)
}

/// Every declared tier.
///
/// # Errors
/// What [`load_types`] refuses.
pub fn tiers(tree: &Path) -> Result<BTreeSet<String>, Error> {
    Ok(load_types(tree)?.into_iter().map(|t| t.tier).collect())
}

/// The type declared for `tier`, if any.
///
/// # Errors
/// What [`load_types`] refuses.
pub fn by_tier(tier: &str, tree: &Path) -> Result<Option<BuildingType>, Error> {
    Ok(load_types(tree)?.into_iter().find(|t| t.tier == tier))
}

/// The tiers whose sheets are drawn by hand.
///
/// # Errors
/// What [`load_types`] refuses.
pub fn hand_drawn_tiers(tree: &Path) -> Result<BTreeSet<String>, Error> {
    Ok(load_types(tree)?
        .into_iter()
        .filter(|t| t.hand_drawn)
        .map(|t| t.tier)
        .collect())
}

/// The Mode A kinds' guesses by key, read from the tree's modal files the first time a kind item asks.
pub struct Kinds<'a> {
    tree: &'a Path,
    guesses: Option<HashMap<String, Vec<String>>>,
}

impl<'a> Kinds<'a> {
    #[must_use]
    pub fn new(tree: &'a Path) -> Self {
        Self {
            tree,
            guesses: None,
        }
    }

    /// The registry, loaded as the Python's import of `compound_kinds` loaded it: the hamlet vocabulary's package first (its
    /// `page-text.json` rulings, then its classes), then the Mode A kinds; a failure is not kept, so the next ask fails again.
    fn registry(&mut self) -> Result<&HashMap<String, Vec<String>>, Error> {
        if self.guesses.is_none() {
            use l7r_gate_registry::about::{classes, compound_classes, not_highlighted};
            not_highlighted(self.tree)?;
            classes(self.tree)?;
            let kinds = compound_classes(self.tree)?;
            self.guesses = Some(kinds.into_iter().map(|k| (k.key, k.guesses)).collect());
        }
        Ok(self.guesses.get_or_insert_with(HashMap::new))
    }
}

/// (class, why) for a program item (`classification`): its own for a label item; for a kind item `per statement` and its kind's
/// guesses, joined - since feature 319 a kind's modal classifies each statement, and a reviewer of a size needs what was guessed. A kind
/// the registry does not know is refused by name.
///
/// # Errors
/// The registry's refusal of a modal file, or a kind it does not know.
pub fn classification(item: &RequiredItem, kinds: &mut Kinds) -> Result<(String, String), Error> {
    let Some(kind) = &item.kind else {
        return Ok((item.cls.clone(), item.why.clone()));
    };
    let Some(guesses) = kinds.registry()?.get(kind) else {
        return Err(value_error(format!(
            "program item {} names the kind {}, which the Mode A registry does not know",
            repr(&item.id),
            repr(kind)
        )));
    };
    let why = if guesses.is_empty() {
        NOTHING_GUESSED.to_owned()
    } else {
        guesses.join(" ")
    };
    Ok((PER_STATEMENT.to_owned(), why))
}

#[cfg(test)]
pub(crate) mod tests;
