//! Footnotes in the record's site (`record/site_notes.py`, feature 301; ported by feature 449 T144). A small page counts its notes from one
//! and lists only those it cites (the GM, 2026-10-01); the single page keeps one count for everything, a note's key qualified by its page.
//! A note cited by a later question of the same page is looked up in its page's merged notes, never its own notes file alone (R4).

use std::collections::HashMap;
use std::sync::LazyLock;

use fancy_regex::{Captures, Regex};

use crate::record::notes::{allocate, number_references, render_note, Notes, Placed, REFERENCE};
use crate::{caps, re, Error, Result};

/// A source key as a note carries it - linked to the document, or to the registry where it was not read.
pub static KEY_LINK: LazyLock<Regex> =
    LazyLock::new(|| re(r#"<a href="[^"]*"><code>([a-z0-9][a-z0-9-]*)</code></a>"#));

fn note<'n>(notes: &'n Notes, key: &str) -> Option<&'n String> {
    notes.iter().rev().find(|(k, _)| k == key).map(|(_, b)| b)
}

/// A note with each source key linking `<prefix><key>` - `#work-` on a small page, `#` on the single page.
#[must_use]
pub fn keyed_to(body: &str, prefix: &str) -> String {
    KEY_LINK
        .replace_all(body, |m: &Captures| {
            format!(r#"<a href="{prefix}{k}"><code>{k}</code></a>"#, k = &m[1])
        })
        .into_owned()
}

/// A question with its references numbered from 1, and its notes in number order: only the notes this question cites are placed.
///
/// # Errors
/// [`allocate`]'s: a malformed key, or a reference no note defines.
pub fn small_page(
    question: &str,
    page_notes: &Notes,
    place: &str,
) -> Result<(String, Vec<Placed>)> {
    let mut cited: Notes = Vec::new();
    for c in caps(&REFERENCE, question) {
        let key = &c[1];
        if let Some(body) = note(page_notes, key) {
            if !cited.iter().any(|(k, _)| k == key) {
                cited.push((key.to_owned(), body.clone()));
            }
        }
    }
    let (_, placed) = allocate(question, &cited, place)?;
    Ok((number_references(question, &placed, ""), placed))
}

/// The foot of a small page: its notes, numbered, each with its way back; then the works they cite.
#[must_use]
pub fn foot(placed: &[Placed], works: &str) -> String {
    if placed.is_empty() {
        return String::new();
    }
    let notes: String = placed
        .iter()
        .map(|p| {
            let keyed = Placed {
                body: keyed_to(&p.body, "#work-"),
                ..p.clone()
            };
            render_note(&keyed, "") + "\n"
        })
        .collect();
    format!(
        "\n<section class=\"footnotes\"><h2 id=\"page-notes\">Notes</h2>\n<ol>\n{notes}</ol></section>\n<section class=\"works\"><h2 id=\"page-works\">Works cited here</h2>\n{works}\n</section>\n"
    )
}

/// One count through the whole single page: a note placed the first time it is cited, each reference id unique (`fnref-N-2`).
#[derive(Debug, Default)]
pub struct Numbering {
    /// (page, the note), in number order.
    pub placed: Vec<(String, Placed)>,
    numbers: HashMap<(String, String), usize>,
    used: HashMap<usize, usize>,
}

impl Numbering {
    #[must_use]
    pub fn new() -> Self {
        Self::default()
    }

    /// `question` with every reference numbered in the single page's count, placing each note the first time.
    ///
    /// # Errors
    /// A reference no note of its page defines (`NoteError`).
    pub fn number(
        &mut self,
        question: &str,
        page_rel: &str,
        page_notes: &Notes,
        place: &str,
    ) -> Result<String> {
        let mut fault = None;
        let out = REFERENCE
            .replace_all(question, |m: &Captures| {
                // the Python raised at the first such reference, so nothing after it is placed
                if fault.is_some() {
                    return String::new();
                }
                let key = &m[1];
                let Some(body) = note(page_notes, key) else {
                    fault.get_or_insert_with(|| {
                        Error::new("NoteError", format!("{place}: a reference names `{key}`, which no note on {page_rel} defines"))
                    });
                    return String::new();
                };
                let slot = (page_rel.to_owned(), key.to_owned());
                let n = if let Some(n) = self.numbers.get(&slot) {
                    *n
                } else {
                    let n = self.placed.len() + 1;
                    self.numbers.insert(slot, n);
                    self.placed.push((
                        page_rel.to_owned(),
                        Placed { key: key.to_owned(), number: n, body: body.clone(), references: 0 },
                    ));
                    n
                };
                let used = self.used.entry(n).or_default();
                *used += 1;
                let ref_id = if *used == 1 { format!("fnref-{n}") } else { format!("fnref-{n}-{used}") };
                format!(r##"<sup class="fn"><a id="{ref_id}" href="#fn-{n}">{n}</a></sup>"##)
            })
            .into_owned();
        fault.map_or(Ok(out), Err)
    }
}

#[cfg(test)]
mod tests;
