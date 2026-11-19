//! A count typed into a notes file's CURRENT prose, held to what the map ships or the sheet draws (feature 449 T170, `notes_census.py`'s
//! second and third halves): feature 294 B14 (a hamlet's notes against its manifest, [`stale_counts`]) and B15b (a Mode A sheet's notes
//! against the sheet's own tags, [`stale_sheet_counts`], which `pool_check.rs` holds every pool sheet to).
//!
//! History is exempt: a section whose heading dates it or names its feature, pass or round, and a paragraph or bullet carrying its own
//! date (a sheet's journal also by month), records counts that were true when written.
//!
//! Research:
//!     the typed counts - NONE: a count read from a notes file's prose and compared, deciding nothing about the place

use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_gate_research::pyre::py;
use l7r_gate_research::{digit_value, Error};
use serde_json::Value;

use super::{get, items, len, BEGIN, END};
use crate::parse::{parse_marked, WELL_FILL};
use crate::tagged::marks;

/// The palette's latrine and utility fill (`pack_audit/program_rules.py`'s `PRIVY_FILL`, which stays there for the Python's checks under
/// the lockstep rule): a privy is a latrine-tagged rect in it.
pub const PRIVY_FILL: &str = "#7E726A";

/// The number words a count may be typed in, zero to twenty.
pub const WORDS: [&str; 21] = [
    "zero",
    "one",
    "two",
    "three",
    "four",
    "five",
    "six",
    "seven",
    "eight",
    "nine",
    "ten",
    "eleven",
    "twelve",
    "thirteen",
    "fourteen",
    "fifteen",
    "sixteen",
    "seventeen",
    "eighteen",
    "nineteen",
    "twenty",
];

/// The kinds a typed count names, in the Python's order (the alternation's).
pub const COUNTED: [&str; 10] = [
    "farmhouses",
    "households",
    "homesteads",
    "retirement houses",
    "byres",
    "wells",
    "footbridges",
    "persimmons",
    "privies",
    "wood sheds",
];

/// The nouns a sheet's notes type a count of, and the object each counts on the sheet. Arches are NOT counted: the notes type them as
/// ranges and rules, never as a census, and a drawn arch is a group of strokes no tag marks as one (measured 2026-10-01 on the six sheets).
pub const SHEET_NOUNS: [(&str, &str); 5] = [
    ("fire-water tubs", "tubs"),
    ("tubs", "tubs"),
    ("privies", "privies"),
    ("latrines", "privies"),
    ("wells", "wells"),
];

/// A heading that dates its section, or names the feature or pass it records, is HISTORY.
static HISTORY: LazyLock<Regex> =
    LazyLock::new(|| py(r"\b(?:\d{4}-\d{2}-\d{2}|[Ff]eature \d{3}|pass \d+|round \d+)\b"));
// the Python's `^#{1,6} .*$` under `re.M`: `.` stops at a newline, so the line's end needs no `$`
static HEADING: LazyLock<Regex> = LazyLock::new(|| py(r"(?m)^#{1,6} .*"));
static DATED: LazyLock<Regex> = LazyLock::new(|| py(r"\b\d{4}-\d{2}-\d{2}\b"));
static MONTH_DATED: LazyLock<Regex> = LazyLock::new(|| py(r"\b\d{4}-\d{2}\b"));
static BLOCKS: LazyLock<Regex> = LazyLock::new(|| py(r"\n\s*\n|\n(?=\s*- )"));
static COUNT: LazyLock<Regex> = LazyLock::new(|| {
    py(&format!(
        r"(?i)\b(\d+|{})\s+({})\b",
        WORDS.join("|"),
        COUNTED.join("|")
    ))
});
static SHEET_COUNT: LazyLock<Regex> = LazyLock::new(|| {
    // the nouns longest first (a stable sort), so `fire-water tubs` is read before `tubs`
    let mut nouns: Vec<&str> = SHEET_NOUNS.iter().map(|(n, _)| *n).collect();
    nouns.sort_by_key(|n| std::cmp::Reverse(n.len()));
    py(&format!(
        r"(?i)(?<![\d~-])\b(\d+|{})\s+({})\b",
        WORDS.join("|"),
        nouns.join("|")
    ))
});
/// A count after a determiner names a PART of the sheet's objects, not their census ("the house's two privies"); the word list is a
/// GUESS - the forms the six sheets' notes use for a part (measured 2026-10-01).
static PART_OF_THE_WHOLE: LazyLock<Regex> = LazyLock::new(|| {
    py(r"(?i)(?:\b(?:the|its|their|his|her|own|these|those|both|each|all)|'s)\s+$")
});

/// `re.split(BLOCKS, text)`: the pieces between the matches.
fn split_blocks(text: &str) -> Vec<&str> {
    let mut out = Vec::new();
    let mut last = 0;
    for m in BLOCKS.find_iter(text).map_while(Result::ok) {
        out.push(&text[last..m.start()]);
        last = m.end();
    }
    out.push(&text[last..]);
    out
}

fn dated(re: &Regex, block: &str) -> bool {
    re.is_match(block).unwrap_or(false)
}

/// The notes' CURRENT description: every section whose heading is not history, less the census block, less every paragraph or bullet
/// carrying its own date.
#[must_use]
pub fn current_prose(text: &str) -> String {
    let mut text = text.to_owned();
    if let (Some(i), Some(j)) = (text.find(BEGIN), text.find(END)) {
        if i < j {
            text = format!("{}{}", &text[..i], &text[j + END.len()..]);
        }
    }
    let mut out = String::new();
    let (mut keep, mut last) = (true, 0);
    for m in HEADING.find_iter(&text).map_while(Result::ok) {
        if keep {
            out += &text[last..m.start()];
        }
        (keep, last) = (!dated(&HISTORY, m.as_str()), m.start());
    }
    if keep {
        out += &text[last..];
    }
    let blocks: Vec<&str> = split_blocks(&out)
        .into_iter()
        .filter(|b| !dated(&DATED, b))
        .collect();
    blocks.join("\n\n")
}

/// A typed count's value: its digits (of any script, as Python's `int()`), or its word's - a word the case-blind match took that
/// `lower()` does not give back (`ſix`) is the Python's `KeyError`. The digits are kept as text, a count of any length compared exactly.
fn typed(word: &str) -> Result<String, Error> {
    let digits: Option<String> = word
        .chars()
        .map(|c| digit_value(c).and_then(|d| char::from_digit(d, 10)))
        .collect();
    if let Some(d) = digits {
        let d = d.trim_start_matches('0');
        return Ok(if d.is_empty() { "0" } else { d }.to_owned());
    }
    let lower = word.to_lowercase();
    WORDS
        .iter()
        .position(|w| *w == lower)
        .map(|n| n.to_string())
        .ok_or_else(|| Error::new("KeyError", lower))
}

/// How many of `kind` the manifest ships (`COUNTED`'s readings).
fn shipped(kind: &str, m: &Value) -> Result<usize, Error> {
    let fixtures = |want: &str| -> Result<usize, Error> {
        let mut n = 0;
        for f in items(m, "farm_fixtures")? {
            if super::get(&f, "kind")?.and_then(Value::as_str) == Some(want) {
                n += 1;
            }
        }
        Ok(n)
    };
    let key = match kind {
        "farmhouses" | "households" | "homesteads" => "houses",
        "retirement houses" => "retirement_houses",
        "byres" => "byres",
        "wells" => "wells",
        "footbridges" => "bridges",
        "persimmons" => "persimmons",
        "privies" => return fixtures("privy"),
        "wood sheds" => return fixtures("woodpile"),
        other => return Err(Error::new("KeyError", other.to_owned())),
    };
    match get(m, key)? {
        Some(v) if l7r_guard::shared::pyjson::truthy(v) => len(v),
        _ => Ok(0),
    }
}

/// Each count the notes' current prose types that the manifest does not ship - "15 farmhouses" on a map of 16 (feature 294 B14).
///
/// # Errors
/// A manifest of the wrong shape, or a matched word with no value, as the Python raised them.
pub fn stale_counts(text: &str, m: &Value) -> Result<Vec<String>, Error> {
    let mut out = Vec::new();
    for c in COUNT
        .captures_iter(&current_prose(text))
        .map_while(Result::ok)
    {
        let n = typed(&c[1])?;
        let kind = c[2].to_lowercase();
        let ships = shipped(&kind, m)?;
        if n != ships.to_string() {
            out.push(format!("'{}' - the map ships {ships} {kind}", &c[0]));
        }
    }
    Ok(out)
}

/// How many of each counted object the sheet DRAWS, read from its tags: a tub is a circle of the fire-water group; a privy a
/// latrine-tagged rect in the privy fill (its collection hatch is not a second privy); a well a well-tagged rect in the curb fill.
///
/// # Errors
/// The sheet's parse refused ([`crate::parse::parse_svg`]), or a mark's number `float()` refuses.
pub fn sheet_counts(svg: &str) -> Result<[(&'static str, usize); 3], Error> {
    let marked = marks(svg)?;
    let tubs = parse_marked(svg, &marked)?.tubs.len();
    let rects = marked.iter().filter(|m| m.tag == "rect");
    let privies = rects
        .clone()
        .filter(|m| m.belongs_to("latrine") && m.fill() == PRIVY_FILL)
        .count();
    let wells = rects
        .filter(|m| m.belongs_to("well") && m.fill() == WELL_FILL)
        .count();
    Ok([("tubs", tubs), ("privies", privies), ("wells", wells)])
}

/// A sheet's notes' CURRENT prose: [`current_prose`], less every block dated by month.
#[must_use]
pub fn sheet_prose(notes: &str) -> String {
    let prose = current_prose(notes);
    let blocks: Vec<&str> = split_blocks(&prose)
        .into_iter()
        .filter(|b| !dated(&MONTH_DATED, b))
        .collect();
    blocks.join("\n\n")
}

/// Each census count a sheet's notes type in their CURRENT prose that the sheet does not draw - "11 tubs" on a sheet of 10 (feature 294
/// B15b). Dated history is exempt, and so is a count of a part (`the house's two privies`).
///
/// # Errors
/// As [`sheet_counts`], and a matched word with no value.
pub fn stale_sheet_counts(notes: &str, svg: &str) -> Result<Vec<String>, Error> {
    let drawn = sheet_counts(svg)?;
    let prose = sheet_prose(notes);
    let mut out = Vec::new();
    for c in SHEET_COUNT.captures_iter(&prose).map_while(Result::ok) {
        let start = c.get(0).map_or(0, |m| m.start());
        // the 40 CHARACTERS before the count (the Python's slice of a `str`), searched as a string of their own
        let before = &prose[..start];
        let from = before.char_indices().rev().nth(39).map_or(0, |(i, _)| i);
        if PART_OF_THE_WHOLE.is_match(&before[from..]).unwrap_or(false) {
            continue;
        }
        let n = typed(&c[1])?;
        let noun = c[2].to_lowercase();
        let what = SHEET_NOUNS
            .iter()
            .find(|(k, _)| *k == noun)
            .map(|(_, w)| *w)
            .ok_or_else(|| Error::new("KeyError", noun.clone()))?;
        let has = drawn
            .iter()
            .find(|(k, _)| *k == what)
            .map_or(0, |(_, v)| *v);
        if n != has.to_string() {
            out.push(format!("'{}' - the sheet draws {has} {what}", &c[0]));
        }
    }
    Ok(out)
}
