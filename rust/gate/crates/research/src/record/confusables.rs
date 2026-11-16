//! *Not to be confused with:* - the list under a section a reader could mistake for another (`record/confusables.py`, feature 292 FR-016;
//! ported by feature 449 T144). The pairs live once in `research/confusables.json`, two-way by construction; an entry is the other
//! section's heading, linked, and its definition - the first sentence of its opening paragraph, read at assembly so it never drifts. A pair
//! naming a section that does not exist is a refusal.

use std::fmt::Write as _;
use std::path::Path;
use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_guard::shared::html_text::{escape, unescape};
use l7r_guard::shared::py_text::collapse;
use serde_json::Value;

use crate::record::questions::Record;
use crate::{drop_all, re, Error, Result, SPACE_CLASS};

/// The pairs, kept once, beside the questions they join.
pub const DATA: &str = "confusables.json";
pub const LABEL: &str = "Not to be confused with:";
static H2: LazyLock<Regex> = LazyLock::new(|| re(r#"(?s)<h2 id="([^"]+)">(.*?)</h2>"#));
static P: LazyLock<Regex> = LazyLock::new(|| re(r"(?s)<p>(.*?)</p>"));
static COMMENT: LazyLock<Regex> = LazyLock::new(|| re(r"(?s)<!--.*?-->"));
static SUP: LazyLock<Regex> = LazyLock::new(|| re(r"(?s)<sup\b[^>]*>.*?</sup>"));
static TAG: LazyLock<Regex> = LazyLock::new(|| re(r"<[^>]+>"));
static SENTENCE: LazyLock<Regex> =
    LazyLock::new(|| re(&format!(r"(?s)^(.+?[.!?])(?:[{SPACE_CLASS}]|\z)")));

/// Two sections a reader could mistake for each other: `NNNN-<slug>[.drawing].html#<heading id>` each.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Pair {
    pub a: String,
    pub b: String,
}

/// `x[k]` of a pair's row, as Python indexes it.
fn side(row: &Value, k: &str) -> Result<String> {
    let kind = l7r_guard::shared::blocked::type_name(row);
    match row {
        Value::Object(m) => m
            .get(k)
            .map(l7r_guard::shared::pyjson::py_str)
            .ok_or_else(|| Error::new("KeyError", format!("'{k}'"))),
        Value::String(_) => Err(Error::new(
            "TypeError",
            "string indices must be integers, not 'str'",
        )),
        Value::Array(_) => Err(Error::new(
            "TypeError",
            "list indices must be integers or slices, not str",
        )),
        _ => Err(Error::new(
            "TypeError",
            format!("'{kind}' object is not subscriptable"),
        )),
    }
}

/// Every pair in the data file, in file order; none where there is no file.
///
/// # Errors
/// A file that is not JSON (the library's words), or a row short of a side.
pub fn load(record_dir: &Path) -> Result<Vec<Pair>> {
    let path = record_dir.join(DATA);
    if !path.is_file() {
        return Ok(Vec::new());
    }
    let text = crate::read(&path).unwrap_or_default();
    let data = crate::json(&text).map_err(|e| Error::new("JSONDecodeError", e))?;
    let rows: Vec<Value> = match &data {
        Value::Array(rows) => rows.clone(),
        Value::Object(m) => m.keys().map(|k| Value::from(k.as_str())).collect(),
        Value::String(t) => t.chars().map(|c| Value::from(c.to_string())).collect(),
        other => {
            let kind = l7r_guard::shared::blocked::type_name(other);
            return Err(Error::new(
                "TypeError",
                format!("'{kind}' object is not iterable"),
            ));
        }
    };
    rows.iter()
        .map(|x| {
            Ok(Pair {
                a: side(x, "a")?,
                b: side(x, "b")?,
            })
        })
        .collect()
}

fn halves(reference: &str) -> (&str, &str) {
    reference.split_once('#').unwrap_or((reference, ""))
}

/// The text of the page `reference` names, when its heading is the anchor.
fn section<'r>(record: &'r Record, reference: &str) -> Option<&'r str> {
    let (file, anchor) = halves(reference);
    record
        .by_file(file)
        .filter(|p| p.heading_id == anchor)
        .map(|p| p.text.as_str())
}

fn text(fragment: &str) -> String {
    collapse(&unescape(&drop_all(&TAG, &drop_all(&SUP, fragment))))
}

/// A section's heading as its reader sees it.
#[must_use]
pub fn title(section: &str) -> String {
    H2.captures(section)
        .ok()
        .flatten()
        .map_or_else(String::new, |m| text(&m[2]))
}

/// The first sentence of a section's opening paragraph - the record's own definition of its subject.
#[must_use]
pub fn definition(section: &str) -> String {
    let body = drop_all(&COMMENT, section);
    let Some(m) = P.captures(&body).ok().flatten() else {
        return String::new();
    };
    let words = text(&m[1]);
    SENTENCE
        .captures(&words)
        .ok()
        .flatten()
        .map_or(words.clone(), |s| s[1].to_owned())
}

/// A message for each side of a pair that names no section, and for a pair joining a section to itself.
#[must_use]
pub fn unresolved(pairs: &[Pair], record: &Record) -> Vec<String> {
    let mut bad = Vec::new();
    for p in pairs {
        if p.a == p.b {
            bad.push(format!("`{}` is paired with itself", p.a));
        }
        for (here, other) in [(&p.a, &p.b), (&p.b, &p.a)] {
            if section(record, here).is_none() {
                bad.push(format!(
                    "`{here}` (paired with `{other}`) - no such section"
                ));
            }
        }
    }
    bad
}

/// Section id on this page to its entries' HTML: each pair adds an entry under both of its sections, its link the other page's file name.
#[must_use]
pub fn entries(file: &str, pairs: &[Pair], record: &Record) -> Vec<(String, Vec<String>)> {
    let mut out: Vec<(String, Vec<String>)> = Vec::new();
    for p in pairs {
        for (here, there) in [(&p.a, &p.b), (&p.b, &p.a)] {
            let (page, anchor) = halves(here);
            if page != file {
                continue;
            }
            let other = section(record, there).unwrap_or("");
            let mut entry = format!(
                r#"<li><a href="{}">{}</a>"#,
                halves(there).0,
                escape(&title(other), false)
            );
            let gloss = definition(other);
            if gloss.is_empty() {
                entry.push_str("</li>");
            } else {
                let _ = write!(entry, " - {}</li>", escape(&gloss, false));
            }
            match out.iter_mut().find(|(a, _)| a == anchor) {
                Some(slot) => slot.1.push(entry),
                None => out.push((anchor.to_owned(), vec![entry])),
            }
        }
    }
    out
}

/// The page with the list written right after each paired section's heading.
#[must_use]
pub fn write(page_html: &str, file: &str, pairs: &[Pair], record: &Record) -> String {
    let mut page = page_html.to_owned();
    for (anchor, items) in entries(file, pairs, record) {
        let heading = re(&format!(
            r#"(?s)<h2 id="{}">.*?</h2>"#,
            fancy_regex::escape(&anchor)
        ));
        let Some(m) = heading.find(&page).ok().flatten() else {
            continue; // `unresolved` has already refused a pair naming no section
        };
        let block = format!(
            "\n<div class=\"confusables\"><p><em>{LABEL}</em></p>\n<ul>\n{}\n</ul></div>",
            items.join("\n")
        );
        page.insert_str(m.end(), &block);
    }
    page
}

#[cfg(test)]
mod tests;
