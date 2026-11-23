//! The place card: what a reader gets for clicking the settlement's own title placard (`interactive/place.py`, feature 156; ported by
//! feature 449 T150, the engine port's step 2, the Python deleted by its part B, held by `page/held.rs`).
//!
//! The GM, 2026-08-29: *"if someone clicks on the title card, I want to have a brief 'what is this place' overview."* Everything the card
//! states is MEASURED (the map's own manifest and ink), CANON (`l7r.md`, what a tier is and how many live in a household) or AUTHORED (the
//! map's notes) - never a per-map special case here (spec FR-014). It does NOT rank kinds of hamlet (nothing answers it), does NOT claim
//! wet-rice dominance (the research pass came back NOT-FOUND), and says so where it rests on canon the record contradicts (FR-008a).
//!
//! Research:
//!     card plumbing - NONE: wording, joining and assembly; what the card states is read from the map, the notes and the record, each rule claimed beside its unit

use std::collections::BTreeSet;
use std::path::Path;

use l7r_gate_research::Error;
use l7r_shared::pyjson::{py_str, truthy};
use serde_json::{json, Map, Value};

use crate::dwellings::{is_dwelling, HOUSEHOLD};
use crate::notes::{get, Dict, MapNotes};
use crate::page::value::items;

/// `l7r.md`'s ~5 inhabitants per household, taken from the leaf so the card keeps no copy of its own (settlement-review round 5).
///
/// Research: inhabitants per household - research/questions/0004-households-how-many-live-in-a-house-and-under-how-many-roofs-ie.html: five
pub const PER_HOUSEHOLD: i64 = HOUSEHOLD;
/// [`PER_HOUSEHOLD`] as a float, for a households value Python multiplied as one - the one figure, written once.
#[allow(clippy::cast_precision_loss, reason = "five, exact in an f64")]
const PER_HOUSEHOLD_F64: f64 = PER_HOUSEHOLD as f64;

/// `l7r.md`'s median-domain table, for the one ranking the card is allowed to make - of TIERS - interpolated into the hamlet's text
/// rather than typed into it (settlement-review round 7).
///
/// Research: the tiers' counts - CANON: l7r.md's median domain, 1,296 hamlets to its 216 villages
pub const HAMLETS_PER_DOMAIN: i64 = 1296;
/// The villages of the median domain.
///
/// Research: the tiers' counts - CANON: l7r.md's median domain, 216 villages
pub const VILLAGES_PER_DOMAIN: i64 = 216;
/// The hamlets' share of the median domain's people.
///
/// Research: the tiers' counts - CANON: l7r.md's median domain, 40% of its inhabitants living in a hamlet
pub const HAMLET_SHARE: &str = "40%";

/// The class whose destination the GM singled out, the one class that gets a default annotation.
pub const LANE: &str = "village lane";
/// The windbreak class (feature 261).
pub const WINDBREAK: &str = "windbreak";
/// The farmstead grove class (feature 291).
pub const HOMESTEAD_GROVE: &str = "homestead grove";

/// The quarters a regional wind's belt may name: the northwest, or one of its two sides.
///
/// Research:
///     the regional quarters - research/questions/0072-shelter-belts-on-a-villages-windward-side-bofurin.drawing.html: every belt on the north and west of its houses, or on one of those two sides, unless the map declares a wind of its own
pub const REGIONAL_QUARTERS: [&str; 3] = ["NW", "N", "W"];

/// The quarter a belt stands toward, named by where the wind blows from - ONE direction, never the two sides of a hook (feature 261).
///
/// Research: the wind's quarter named - NONE: a compass abbreviation spelled out
pub const WIND_NAMES: [(&str, &str); 8] = [
    ("N", "north"),
    ("NE", "northeast"),
    ("E", "east"),
    ("SE", "southeast"),
    ("S", "south"),
    ("SW", "southwest"),
    ("W", "west"),
    ("NW", "northwest"),
];

/// The farmstead grove's sides, said.
///
/// Research: card plumbing - research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.drawing.html: two sides the windward pair, three open at the front, four broken once at the front
pub const SIDES_WORDS: [(i32, &str); 3] = [
    (
        2,
        "two sides of the house, the pair the winter wind blows on",
    ),
    (
        3,
        "three sides of the house, open only at the front where the yard and the way in are",
    ),
    (
        4,
        "all four sides of the house, broken once at the front for the way in",
    ),
];

/// The `### Place` keys the card understands; anything else is ignored rather than guessed at.
///
/// Research: the place keys - NONE: the notes' keys the card reads
pub const PLACE_KEYS: [&str; 7] = [
    "district",
    "district direction",
    "county",
    "imperial road",
    "town",
    "town direction",
    "also",
];

/// What one tier IS, in terms a player can use at the table (`place.Kind`), from `assets/place.json`.
#[derive(Debug, Clone, PartialEq)]
pub struct Kind {
    pub noun: String,
    pub what: String,
    pub houses_noun: String,
    pub excludes_farms: bool,
    pub population_note: String,
    pub default_population: Value,
}

/// `str.format` of a tier's text with the domain's counts: `{NAME}` and `{NAME:,}`, `{{` and `}}`.
fn format_what(text: &str) -> Result<String, Error> {
    let mut out = String::new();
    let mut rest = text;
    while let Some(at) = rest.find(['{', '}']) {
        out += &rest[..at];
        let tail = &rest[at..];
        if tail.starts_with("{{") || tail.starts_with("}}") {
            out.push(char::from(tail.as_bytes()[0]));
            rest = &tail[2..];
            continue;
        }
        let end = tail
            .find('}')
            .filter(|_| tail.starts_with('{'))
            .ok_or_else(|| Error::new("ValueError", "Single '}' encountered in format string"))?;
        let (name, spec) = tail[1..end].split_once(':').unwrap_or((&tail[1..end], ""));
        let value = match (name, spec) {
            ("HAMLETS_PER_DOMAIN", s) => count(HAMLETS_PER_DOMAIN, s),
            ("VILLAGES_PER_DOMAIN", s) => count(VILLAGES_PER_DOMAIN, s),
            ("HAMLET_SHARE", "") => Some(HAMLET_SHARE.to_owned()),
            ("HAMLET_SHARE", _) => None,
            _ => return Err(Error::new("KeyError", name)),
        };
        // a format the Python would write that this port does not (a hex count, a padded share): refused by name, never written wrong
        let Some(value) = value else {
            return Err(Error::new(
                "ValueError",
                format!("the place card formats {{{name}}} and a count's {{{name}:,}} only, not {{{name}:{spec}}} (feature 449 T150)"),
            ));
        };
        out += &value;
        rest = &tail[end + 1..];
    }
    Ok(out + rest)
}

/// A count as `{n}` or `{n:,}` writes it.
fn count(n: i64, spec: &str) -> Option<String> {
    match spec {
        "" => Some(n.to_string()),
        "," => Some(grouped(n)),
        _ => None,
    }
}

/// `f"{n:,}"` of an integer.
fn grouped(n: i64) -> String {
    let digits = n.unsigned_abs().to_string();
    let mut out = String::new();
    for (i, c) in digits.chars().enumerate() {
        if i > 0 && (digits.len() - i) % 3 == 0 {
            out.push(',');
        }
        out.push(c);
    }
    if n < 0 {
        format!("-{out}")
    } else {
        out
    }
}

fn text(v: Option<&Value>) -> String {
    v.map_or_else(String::new, py_str)
}

/// The tiers the card describes, keyed by `meta.scale`.
///
/// Research:
///     what each tier is - research/questions/0001-the-five-sizes-of-settlement-hamlet-village-town-provincial-city-and-capital.html
///     a city's figure takes in its samurai country estates - CANON: the GM's request of feature 156, a provincial city's ~3,000 includes the samurai country estates, not the farmers
///     a hamlet's dead at the village's grounds - research/questions/0236-where-a-village-buries-its-dead-its-own-ground-the-temple-yard-the-fields-or-the-home-plot.drawing.html: no cremation ground of its own; its dead burned and buried at the main village's, which holds the district's grounds
///
/// # Errors
/// `place.json` unreadable, or a tier's text naming a count the card does not know.
pub fn kinds(tree: &Path) -> Result<Vec<(String, Kind)>, Error> {
    crate::reads::asset(tree, "place.json");
    let content = l7r_gate_research::content::content(tree, "place.json")?;
    let mut out = Vec::new();
    for (key, f) in content
        .get("kinds")
        .and_then(Value::as_object)
        .into_iter()
        .flatten()
    {
        out.push((
            key.clone(),
            Kind {
                noun: text(f.get("noun")),
                what: format_what(&text(f.get("what")))?,
                houses_noun: text(f.get("houses_noun")),
                excludes_farms: f.get("excludes_farms").is_some_and(truthy),
                population_note: text(f.get("population_note")),
                default_population: f.get("default_population").cloned().unwrap_or(Value::Null),
            },
        ));
    }
    Ok(out)
}

/// `a`, `a and b`, `a, b and c` - the serial comma is not the house style here.
///
/// Research: the card's lists - CONVENTION: `a, b and c`, no serial comma, the house style here
#[must_use]
pub fn join(items: &[String]) -> String {
    match items {
        [] => String::new(),
        [one] => one.clone(),
        [head @ .., last] => format!("{} and {last}", head.join(", ")),
    }
}

/// An object of `place.json` as ordered pairs of text.
fn pairs(content: &Value, name: &str) -> Vec<(String, Value)> {
    content
        .get(name)
        .and_then(Value::as_object)
        .map(|m| m.iter().map(|(k, v)| (k.clone(), v.clone())).collect())
        .unwrap_or_default()
}

/// What this map grows, from the crop classes actually on it (spec FR-010, FR-014): a group with nothing present skipped, and empty when
/// it grows nothing the vocabulary knows.
///
/// Research: what the map grows - NONE: the crop classes drawn, grouped and said in `place.json`'s words
///
/// # Errors
/// `place.json` unreadable.
pub fn crop_sentence(tree: &Path, present: &BTreeSet<String>) -> Result<String, Error> {
    crate::reads::asset(tree, "place.json");
    let content = l7r_gate_research::content::content(tree, "place.json")?;
    let mut groups: Vec<(String, Vec<String>)> = Vec::new();
    for (key, gw) in pairs(&content, "crops") {
        if !present.contains(&key) {
            continue;
        }
        let (group, word) = (text(gw.get(0)), text(gw.get(1)));
        match groups.iter_mut().find(|(g, _)| *g == group) {
            Some((_, list)) => list.push(word),
            None => groups.push((group, vec![word])),
        }
    }
    let lead = content.get("crop_lead");
    let mut parts: Vec<String> = Vec::new();
    for g in ["wet", "dry", "dike", "water"] {
        if let Some((_, words)) = groups.iter().find(|(k, _)| k == g) {
            parts.push(format!(
                "{} {}.",
                text(lead.and_then(|l| l.get(g))),
                join(words)
            ));
        }
    }
    for (key, sentence) in pairs(&content, "crop_sentences") {
        if present.contains(&key) {
            parts.push(py_str(&sentence));
        }
    }
    Ok(parts.join(" "))
}

/// A JSON number's value, for the card's arithmetic.
fn number(v: &Value) -> Option<f64> {
    match v {
        Value::Number(n) => n.as_f64(),
        Value::Bool(b) => Some(f64::from(u8::from(*b))),
        _ => None,
    }
}

/// `int(population)` of a figure `meta` or the tier gave.
#[expect(
    clippy::cast_possible_truncation,
    reason = "Python's int() truncates toward zero; a population is far inside i64"
)]
fn population_int(v: &Value) -> Result<i64, Error> {
    match v {
        Value::Number(n) if n.is_i64() => Ok(n.as_i64().unwrap_or(0)),
        Value::String(s) => l7r_shared::py_text::strip(s)
            .replace('_', "")
            .parse()
            .map_err(|_| {
                Error::new(
                    "ValueError",
                    format!(
                        "invalid literal for int() with base 10: {}",
                        l7r_shared::py_text::repr(s)
                    ),
                )
            }),
        other => number(other).map(|f| f.trunc() as i64).ok_or_else(|| {
            Error::new(
                "TypeError",
                "int() argument must be a string, a bytes-like object or a real number",
            )
        }),
    }
}

/// The dwelling count, EXACT, and the population, tilde-marked (`place.size_sentence`; the GM, 2026-08-29: *"You should not use a ~ for
/// the number of farmhouses, because that actually IS an exact map feature"*). The tier's own figure first, else `meta.population`, else
/// five to a declared household; the households named only where the arithmetic would not work.
///
/// Research:
///     population from households - research/questions/0004-households-how-many-live-in-a-house-and-under-how-many-roofs-ie.html: five to a
///         DECLARED household (the meta households, not the drawn houses) where neither the tier records a figure of its own nor
///         the map's meta states its own `population`, the two overrides taken in that order
///     households named beside farmhouses - research/questions/0004-households-how-many-live-in-a-house-and-under-how-many-roofs-ie.drawing.html:
///         stated only where the drawn count differs from the declared households
///
/// # Errors
/// A population, or a households value given as text, no integer can be read from (the Python's `int()`).
pub fn size_sentence(kind: &Kind, meta: &Map<String, Value>, houses: i64) -> Result<String, Error> {
    let mut parts = Vec::new();
    if houses != 0 {
        parts.push(format!("{houses} {}", kind.houses_noun));
    }
    let households = meta.get("households").cloned().unwrap_or(Value::Null);
    // A HOUSEHOLDS VALUE GIVEN AS TEXT IS THE NUMBER IT NAMES, read as `int()` reads it (FIXED, feature 449 T183, T150's finding): the
    // Python multiplied the text, `"12"` five times over a population of 1,212,121,212, and never found it equal to the drawn count
    let counted = match &households {
        Value::String(s) if !s.is_empty() => json!(population_int(&households)?),
        h => h.clone(),
    };
    // `PER_HOUSEHOLD * households` as Python multiplies: an int by an int, a float by a float
    let from_households = || match &counted {
        h if !truthy(h) => Value::Null,
        Value::Bool(_) => json!(PER_HOUSEHOLD),
        h => h.as_i64().map_or_else(
            || number(h).map_or(Value::Null, |n| json!(PER_HOUSEHOLD_F64 * n)),
            |i| json!(PER_HOUSEHOLD * i),
        ),
    };
    let population = [
        kind.default_population.clone(),
        meta.get("population").cloned().unwrap_or(Value::Null),
    ]
    .into_iter()
    .find(truthy)
    .unwrap_or_else(from_households);
    if truthy(&population) {
        let p = grouped(population_int(&population)?);
        #[expect(
            clippy::cast_precision_loss,
            reason = "a count of drawn houses, far inside f64's exact integers"
        )]
        let differs = number(&counted)
            .is_none_or(|h| h.partial_cmp(&(houses as f64)) != Some(std::cmp::Ordering::Equal));
        if truthy(&counted) && houses != 0 && differs && !kind.excludes_farms {
            parts.push(format!(
                "about {} households, population ~{p}",
                py_str(&counted)
            ));
        } else {
            parts.push(format!("population ~{p}"));
        }
    }
    Ok(parts.join(", "))
}

/// Where this place sits, from what its notes record - nothing when they record nothing (`place.where_sentences`). A hamlet BELONGS to its
/// district; a village IS its district and is never said to belong to one (the GM, 2026-08-29: "there is no reason to ever say what
/// village district a village belongs to"); the Imperial road's sentence says where the road LIES, not how it runs.
///
/// Research: where a place sits - CANON: the GM 2026-08-29, a village is its district and a town its county's seat; the rest is the map's notes in their own words
#[must_use]
pub fn where_sentences(scale: &str, place: &Dict) -> Vec<String> {
    let mut out = Vec::new();
    let (district, direction) = (
        get(place, "district").filter(|s| !s.is_empty()),
        get(place, "district direction").filter(|s| !s.is_empty()),
    );
    if let Some(d) = district.filter(|_| scale != "village") {
        out.push(match direction {
            Some(dir) => format!("It belongs to the village district of {d}, which lies {dir}."),
            None => format!("It belongs to the village district of {d}."),
        });
    }
    if let Some(county) = get(place, "county").filter(|s| !s.is_empty()) {
        out.push(match scale {
            "village" => format!("It is in {county} county."),
            "town" => format!("It is the seat of {county} county."),
            _ => format!("The district is part of {county} county."),
        });
    }
    if let Some(road) = get(place, "imperial road").filter(|s| !s.is_empty()) {
        out.push(format!("An Imperial road passes {road} of here."));
    }
    if let Some(town) = get(place, "town").filter(|s| !s.is_empty()) {
        out.push(
            match get(place, "town direction").filter(|s| !s.is_empty()) {
                Some(dir) => format!("The town of {town} lies {dir}."),
                None => format!("The town of {town} is the county seat."),
            },
        );
    }
    if let Some(also) = get(place, "also").filter(|s| !s.is_empty()) {
        out.push(if also.ends_with('.') {
            also.to_owned()
        } else {
            format!("{also}.")
        });
    }
    out
}

/// Where this map's lanes lead, when its notes do not say (spec FR-021): the connector track toward the district's main village, whose
/// name the district takes (`l7r.md`, Place Names). It names no direction - a route off the sheet is not something the map knows
/// (settlement-review, 2026-08-29).
///
/// Research:
///     connector leads to the district's village - research/questions/0001-the-five-sizes-of-settlement-hamlet-village-town-provincial-city-and-capital.html:
///         the district a hamlet belongs to is named for the village its lanes lead to
#[must_use]
pub fn lane_default(scale: &str, place: &Dict) -> String {
    match get(place, "district").filter(|d| !d.is_empty() && scale == "hamlet") {
        Some(d) => format!("The connector track leads out of the hamlet toward {d}, the main village of the district it belongs to; the lanes between the farmsteads feed it."),
        None => String::new(),
    }
}

/// `str(meta.get("name") or "This settlement")`.
fn name_of(meta: &Map<String, Value>) -> String {
    meta.get("name")
        .filter(|v| truthy(v))
        .map_or_else(|| "This settlement".to_owned(), py_str)
}

/// Which side THIS map's windbreak stands on, and why (feature 261): the regional northwest, or a local wind the map declares (the GM,
/// 2026-09-26: "only when declared"); nothing where the map records no wind, or pairs the regional wind with a quarter other than
/// the northwest or one of its two sides (449 T301: no writer pairs them, measured 2026-11-22 - the five pool hamlets' records all
/// NW, no live writer of `wind_source` - so the pair is refused rather than printed as a region's wind from the southeast).
///
/// Research:
///     windbreak toward the winter wind - research/questions/0072-shelter-belts-on-a-villages-windward-side-bofurin.html, research/questions/0072-shelter-belts-on-a-villages-windward-side-bofurin.drawing.html:
///         the regional northwest unless a local wind is declared, the belt on the north and west or one of the two - so a regional quarter is NW, N or W
///     a declared northwest wind - NONE: a declared wind from the quarter the region's own wind blows from names that wind, so its card reads as the regional one rather than as departing from itself (449 T317)
#[must_use]
pub fn windbreak_default(meta: &Map<String, Value>) -> String {
    let quarter = meta
        .get("windward")
        .filter(|v| truthy(v))
        .map_or_else(String::new, py_str);
    let Some(&(_, wind)) = WIND_NAMES.iter().find(|(k, _)| *k == quarter) else {
        return String::new();
    };
    // 449 T317: a declared wind from the northwest is the region's own wind, so it prints as the regional one rather than as departing
    // from itself; a declared north or west wind still departs from the northwesterly one
    let source = match meta.get("wind_source").and_then(Value::as_str) {
        Some("declared") if quarter == REGIONAL_QUARTERS[0] => Some("regional"),
        other => other,
    };
    match source {
        Some("regional") if !REGIONAL_QUARTERS.contains(&quarter.as_str()) => String::new(),
        Some("regional") => format!(
            "Here the belt stands toward the {wind} of the houses, the side the winter wind across this region blows from; {} has no local wind patterns that would call for a different orientation from the norm.",
            name_of(meta)
        ),
        Some("declared") => format!(
            "Here the belt stands toward the {wind} of the houses, because this place has a local wind from the {wind} that departs from the region's northwesterly winter wind."
        ),
        _ => String::new(),
    }
}

/// Whether a value is a Python `int` (a bool among them).
fn is_int(v: &Value) -> bool {
    v.is_boolean() || v.is_i64() || v.is_u64()
}

/// How many of THIS settlement's homesteads keep a retirement house (feature 319, plan D10), read from the map; empty where the
/// settlement keeps the old couple under one roof.
///
/// Research:
///     card plumbing - research/questions/0004-households-how-many-live-in-a-house-and-under-how-many-roofs-ie.html: the count
///         the map records, said as a count of this settlement
#[must_use]
pub fn retirement_fact(meta: &Map<String, Value>) -> String {
    let (n, households) = (meta.get("retirement_houses"), meta.get("households"));
    let form = meta.get("family_form").and_then(Value::as_str);
    match (n, households) {
        (Some(n), Some(h))
            if form == Some("retirement_house") && is_int(n) && truthy(n) && is_int(h) =>
        {
            format!(
                "{} of {}'s {} homesteads have a retirement house.",
                py_str(n),
                name_of(meta),
                py_str(h)
            )
        }
        _ => String::new(),
    }
}

/// How many sides THIS settlement's farmstead groves take, and why that roll (feature 291, FR-009); nothing on a nucleated map or one that
/// records no side count.
///
/// Research:
///     grove side count - research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.html, research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.drawing.html:
///         two, three or four sides, one roll a settlement
///     full ring on flood ground - research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.drawing.html: four sides rolled more
///         often on flood-prone ground
///     no side sentence on a nucleated map - research/questions/0071-groves-around-a-southern-chinese-village-the-fengshui-woods-fengshuilin-and-the-dooryard-copse.drawing.html: a
///         farmstead's own grove is drawn only where a farmhouse stands apart, so a nucleated map states no side count
#[must_use]
pub fn homestead_grove_default(meta: &Map<String, Value>) -> String {
    let words = meta
        .get("grove_sides")
        .and_then(number)
        .and_then(|n| {
            SIDES_WORDS
                .iter()
                .find(|(k, _)| f64::from(*k).partial_cmp(&n) == Some(std::cmp::Ordering::Equal))
        })
        .map(|(_, w)| *w);
    let nucleated = meta
        .get("settlement_form")
        .is_none_or(|f| f.as_str() == Some("nucleated"));
    let Some(words) = words.filter(|_| !nucleated) else {
        return String::new();
    };
    let ground = if meta.get("flood_ground").is_some_and(truthy) {
        " These farms stand on flood-prone ground, where the full ring - the Izumo plain's, raised on a bank against floods - is rolled more often."
    } else {
        ""
    };
    format!("Here every farm's grove takes {words}: the shape was a regional custom, so one roll decides it for the whole settlement.{ground}")
}

/// `len(v)` of a value Python can measure.
fn length(v: &Value) -> Result<i64, Error> {
    let n = match v {
        Value::Array(a) => a.len(),
        Value::Object(m) => m.len(),
        Value::String(s) => s.chars().count(),
        other => {
            return Err(Error::new(
                "TypeError",
                format!(
                    "object of type '{}' has no len()",
                    crate::py::type_name(other)
                ),
            ))
        }
    };
    Ok(i64::try_from(n).unwrap_or(i64::MAX))
}

/// How many dwellings this map DRAWS that the tier is willing to count: its drawn farmhouses (`houses`) unless the tier excludes farms,
/// and every dwelling in `buildings`. A hamlet and a village draw only farmhouses; a town counts its farmhouses beside its other
/// dwellings; a city counts only its non-farm dwellings (the GM, 2026-08-29: its farm fields "are deliberately not all rendered on the
/// map"; FIXED, feature 449 T271: a town was counted as a city is, its farmhouses left out).
///
/// Research:
///     card plumbing - research/questions/0004-households-how-many-live-in-a-house-and-under-how-many-roofs-ie.drawing.html: which
///         building kinds count as homes (DWELLING_KINDS)
///     a town counts its farmhouses, a city none - research/questions/0004-households-how-many-live-in-a-house-and-under-how-many-roofs-ie.drawing.html:
///         a town counts its drawn farmhouses among its dwellings, a city counts no farmhouse at all
///
/// # Errors
/// A record that is no object, or a `houses` that has no length (the Python's `AttributeError` and `TypeError`).
#[expect(
    clippy::doc_markdown,
    reason = "the claim names the `DWELLING_KINDS` constant unquoted, as the claims registry records it"
)]
pub fn dwellings_shown(manifest: &Value, kind: &Kind) -> Result<i64, Error> {
    let mut n = if kind.excludes_farms {
        0
    } else {
        match manifest.get("houses").filter(|v| truthy(v)) {
            None => 0,
            Some(v) => length(v)?,
        }
    };
    for b in items(manifest.get("buildings"))? {
        let Value::Object(b) = &b else {
            return Err(Error::new(
                "AttributeError",
                format!(
                    "'{}' object has no attribute 'get'",
                    crate::py::type_name(&b)
                ),
            ));
        };
        if b.get("kind")
            .and_then(Value::as_str)
            .is_some_and(is_dwelling)
        {
            n += 1;
        }
    }
    Ok(n)
}

/// The card behind the title placard, or none for a tier the vocabulary does not describe (`place.place_card`); shaped like a class entry
/// so the page opens it through the same modal. Where it is comes before what it grows (settlement-review round 6).
///
/// # Errors
/// `place.json` unreadable, or a count or population the Python could not read.
///
/// Research: the title card - CONVENTION: what the tier is and its counts, then where it is before what it grows (settlement-review round 6), its basis on a hamlet's card only (spec FR-008a)
pub fn place_card(
    tree: &Path,
    meta: &Map<String, Value>,
    present: &BTreeSet<String>,
    notes: &MapNotes,
    manifest: &Value,
) -> Result<Option<Value>, Error> {
    let scale = crate::page::meta_str(meta, "scale");
    let Some((_, kind)) = kinds(tree)?.into_iter().find(|(k, _)| *k == scale) else {
        return Ok(None);
    };
    crate::reads::asset(tree, "place.json");
    let content = l7r_gate_research::content::content(tree, "place.json")?;
    let name = name_of(meta);
    let size = size_sentence(&kind, meta, dwellings_shown(manifest, &kind)?)?;
    let mut what = if size.is_empty() {
        format!("{name} is a {}: {}", kind.noun, kind.what)
    } else {
        format!("{name} is a {} of {size}: {}", kind.noun, kind.what)
    };
    for (key, sentence) in pairs(&content, "collisions") {
        if present.contains(&key) {
            what = format!("{what} {}", py_str(&sentence));
        }
    }
    // `str(meta.get("scale"))`: the scale the tier was found by, so present and truthy
    let mut why = where_sentences(&scale, &notes.place);
    why.push(crop_sentence(tree, present)?);
    why.push(kind.population_note.clone());
    why.retain(|x| !x.is_empty());
    let basis = if kind.noun == "hamlet" {
        text(content.get("basis_lead")) + &text(content.get("basis"))
    } else {
        String::new()
    };
    let questions: Vec<Value> = l7r_gate_research::sources::research_questions(
        &text(content.get("entry")),
        &tree.join("research"),
    )
    .into_iter()
    .map(|q| json!({"text": q.text, "url": q.url}))
    .collect();
    Ok(Some(json!({
        "name": name, "what": what, "why": why.join(" "), "basis": basis, "questions": questions, "siblings": [],
    })))
}

#[cfg(test)]
mod tests;
