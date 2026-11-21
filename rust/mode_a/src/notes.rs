//! The map-notes block: facts a map's `.notes.md` hands its page (`interactive/notes.py`, feature 156; ported by feature 449 T150, the
//! engine port's step 2, the Python deleted by its part B, held by `page/held.rs`).
//!
//! THE READER HAS NO ERROR PATH, AND THAT IS THE REQUIREMENT (the GM, 2026-08-29: *"we should not presume that such sections exist and
//! our code that parses the notes file to find these special notes should be resilient against that formatting not being present, and
//! should default to simply not pulling anything in if the parsing fails"*): a missing file, a missing section, a bullet with no colon, a
//! nested list, a truncated line or a key nobody knows each contributes nothing, silently. `## Map notes` holds `### Place` (the title
//! card's keys) and `### Features` (a sentence true of this map only, keyed by class key).
//!
//! Research: plumbing - NONE

use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_gate_research::pyre::py;
use l7r_shared::py_text::{collapse, is_space, strip};
use l7r_shared::speckit::splitlines;

/// A heading line: the hashes give the level, the rest is the title.
static HEADING: LazyLock<Regex> = LazyLock::new(|| py(r"^(#{1,6})[ \t]+(.*?)[ \t]*$"));

/// A top-level entry: the bullet at column 0 - an INDENTED bullet is a nested list, which the convention does not use.
static BULLET: LazyLock<Regex> =
    LazyLock::new(|| py(r"^-[ \t]+\*\*(.+?)\*\*[ \t]*:[ \t]*(.*?)[ \t]*$"));

/// An ordered `dict[str, str]`: each key once, in the order first written.
pub type Dict = Vec<(String, String)>;

/// The value of `key` in `dict`, as `dict.get(key)`.
#[must_use]
pub fn get<'a>(dict: &'a Dict, key: &str) -> Option<&'a str> {
    dict.iter().find(|(k, _)| k == key).map(|(_, v)| v.as_str())
}

/// What one map's notes offer its page; both halves optional and usually absent (`notes.MapNotes`).
#[derive(Debug, Clone, Default, PartialEq, Eq)]
pub struct MapNotes {
    pub place: Dict,
    pub features: Dict,
}

/// A key as it is looked up: surrounding whitespace and emphasis gone, whitespace collapsed, lower-cased - so `**District Direction**`
/// and `**district  direction**` are one key.
#[must_use]
pub fn normalize_key(raw: &str) -> String {
    collapse(strip(raw).trim_matches(['`', '*', '_'])).to_lowercase()
}

/// The two groups of a match of `re` over `line`, or none.
fn groups(re: &Regex, line: &str) -> Option<(String, String)> {
    let c = re.captures(line).ok().flatten()?;
    Some((c[1].to_owned(), c[2].to_owned()))
}

/// The body under the FIRST heading whose title is `heading` (normalized), to the next heading of the same or higher level; empty when
/// there is none - the normal case for most of the pool.
#[must_use]
pub fn section(text: &str, heading: &str) -> String {
    let want = normalize_key(heading);
    let mut level = 0;
    let mut body: Vec<&str> = Vec::new();
    for line in splitlines(text) {
        let Some((hashes, title)) = groups(&HEADING, line) else {
            if level > 0 {
                body.push(line);
            }
            continue;
        };
        let depth = hashes.chars().count();
        if level > 0 {
            if depth <= level {
                break; // a sibling or an uncle closes the section
            }
            body.push(line); // a deeper heading is part of the body
        } else if normalize_key(&title) == want {
            level = depth;
        }
    }
    body.join("\n")
}

/// The `- **key**: value` entries of one section, in order, the first occurrence winning; an indented line that is no bullet, heading
/// or comment continues the entry above it; anything else ends it, and an entry whose value is empty is dropped.
#[must_use]
pub fn bullets(block: &str) -> Dict {
    fn close(out: &mut Dict, key: &str, parts: &[String]) {
        let value = collapse(&parts.join(" "));
        if !key.is_empty() && !value.is_empty() && get(out, key).is_none() {
            out.push((key.to_owned(), value));
        }
    }
    let mut out = Dict::new();
    let mut key = String::new();
    let mut parts: Vec<String> = Vec::new();
    for line in splitlines(block) {
        if let Some((k, v)) = groups(&BULLET, line) {
            close(&mut out, &key, &parts);
            key = normalize_key(&k);
            parts = vec![v];
            continue;
        }
        let stripped = strip(line);
        let wrapped = !key.is_empty()
            && line.chars().next().is_some_and(is_space)
            && !stripped.is_empty()
            && !["-", "*", "#", "<!--", "|"]
                .iter()
                .any(|p| stripped.starts_with(p));
        if wrapped {
            parts.push(stripped.to_owned());
        } else if !stripped.is_empty() || groups(&HEADING, line).is_some() {
            close(&mut out, &key, &parts); // anything else ends the entry above it
            key.clear();
            parts.clear();
        }
    }
    close(&mut out, &key, &parts);
    out
}

/// The block's two halves from a `.notes.md`'s text; no block, no halves - empty, never an error.
#[must_use]
pub fn parse_map_notes(text: &str) -> MapNotes {
    let block = section(text, "map notes");
    if block.is_empty() {
        return MapNotes::default();
    }
    MapNotes {
        place: bullets(&section(&block, "place")),
        features: bullets(&section(&block, "features")),
    }
}

/// `<base>.notes.md` beside a map's output, parsed: missing or unreadable is empty, undecodable bytes replaced (`errors="replace"`), and
/// its line ends read as Python's text mode reads them. This does not fail; that is the GM's requirement.
#[must_use]
pub fn read_map_notes(path: &std::path::Path) -> MapNotes {
    crate::reads::note(path);
    std::fs::read(path).map_or_else(
        |_| MapNotes::default(),
        |bytes| parse_map_notes(&String::from_utf8_lossy(&bytes)),
    )
}

#[cfg(test)]
mod tests;
