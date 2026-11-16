//! Footnotes that carry a name instead of a number (`record/notes.py`, feature 258 stage 3; ported by feature 449 T144): a reference and its
//! note both name a KEY, and every number on both pages is allocated at assembly, in the order the references appear - 16 of 19 pages once
//! carried their references out of order, and 1,860 references are too many to renumber by hand (research R4, R5).

use std::collections::HashMap;
use std::sync::LazyLock;

use fancy_regex::{Captures, Regex};

use crate::{caps, re, Error, Result};

/// A reference in a question fragment: a key and no number. Matched loosely and validated after, so a malformed key is refused, never
/// passed over.
pub static REFERENCE: LazyLock<Regex> =
    LazyLock::new(|| re(r#"<sup class="fn" data-note="([^"]*)"></sup>"#));
/// A note in a notes fragment: a key, no number, no back link.
pub static NOTE: LazyLock<Regex> =
    LazyLock::new(|| re(r#"(?s)<li data-note="([^"]*)">(.*?)</li>"#));
static KEY: LazyLock<Regex> = LazyLock::new(|| re(r"^[a-z0-9][a-z0-9-]*\n?\z"));

/// A dict's order and values: (key, body) in insertion order.
pub type Notes = Vec<(String, String)>;

/// One note after allocation: its key, its number, its body, and how many references name it.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Placed {
    pub key: String,
    pub number: usize,
    pub body: String,
    pub references: usize,
}

fn refused(message: String) -> Error {
    Error::new("NoteError", message)
}

/// Is `key` a note key: lower case, digits and hyphens?
#[must_use]
pub fn is_key(key: &str) -> bool {
    KEY.is_match(key).unwrap_or(false)
}

fn body_of<'n>(notes: &'n [(String, String)], key: &str) -> Option<&'n String> {
    notes.iter().rev().find(|(k, _)| k == key).map(|(_, b)| b)
}

/// Number the references of `page_html` in the order they appear and place their notes: the page with every reference dropped, and the
/// notes in number order. `keys_defined` is the page's notes, key to body.
///
/// # Errors
/// A malformed key, a reference no note defines, or a note nothing references.
pub fn allocate(
    page_html: &str,
    keys_defined: &[(String, String)],
    place: &str,
) -> Result<(String, Vec<Placed>)> {
    let mut order: Vec<String> = Vec::new();
    let mut counts: HashMap<String, usize> = HashMap::new();
    for c in caps(&REFERENCE, page_html) {
        let key = &c[1];
        if !is_key(key) {
            return Err(refused(format!(
                "{place}: `{key}` is not a note key - lower case, digits and hyphens"
            )));
        }
        if body_of(keys_defined, key).is_none() {
            return Err(refused(format!(
                "{place}: a reference names `{key}`, which no note on this page defines"
            )));
        }
        if !order.iter().any(|k| k == key) {
            order.push(key.to_owned());
        }
        *counts.entry(key.to_owned()).or_default() += 1;
    }
    let mut unused: Vec<&str> = Vec::new();
    for (k, _) in keys_defined {
        if !order.contains(k) && !unused.contains(&k.as_str()) {
            unused.push(k);
        }
    }
    if !unused.is_empty() {
        unused.sort_unstable();
        return Err(refused(format!(
            "{place}: {} - defined as a note, referenced nowhere. A note nothing cites is either a reference that was deleted or a note that was never wired up; the assembly will not quietly drop it",
            unused.join(", ")
        )));
    }
    let placed = order
        .iter()
        .enumerate()
        .map(|(i, k)| Placed {
            key: k.clone(),
            number: i + 1,
            body: body_of(keys_defined, k).cloned().unwrap_or_default(),
            references: counts[k],
        })
        .collect();
    Ok((REFERENCE.replace_all(page_html, "").into_owned(), placed))
}

/// Every reference rewritten into the numbered anchor a reader's page carries; a key referenced again gets `fnref-N-2`, so every id on
/// the page is unique.
#[must_use]
pub fn number_references(page_html: &str, placed: &[Placed], citations_href: &str) -> String {
    let numbers: HashMap<&str, usize> = placed.iter().map(|p| (p.key.as_str(), p.number)).collect();
    let mut used: HashMap<String, usize> = HashMap::new();
    REFERENCE
        .replace_all(page_html, |c: &Captures| {
            let key = &c[1];
            let n = numbers.get(key).copied().unwrap_or(0);
            let seen = used.entry(key.to_owned()).or_default();
            *seen += 1;
            let ref_id = if *seen == 1 {
                format!("fnref-{n}")
            } else {
                format!("fnref-{n}-{seen}")
            };
            format!(
                r#"<sup class="fn"><a id="{ref_id}" href="{citations_href}#fn-{n}">{n}</a></sup>"#
            )
        })
        .into_owned()
}

/// One `<li>` of a citations page: the number, the body as written, and the back link.
#[must_use]
pub fn render_note(placed: &Placed, page_href: &str) -> String {
    format!(
        r#"<li id="fn-{n}">{} <a class="fnback" href="{page_href}#fnref-{n}">back</a></li>"#,
        placed.body,
        n = placed.number
    )
}

/// key to body from one notes fragment, refusing what the contract refuses.
///
/// # Errors
/// A malformed key, or a key defined twice in the file.
pub fn notes_of(fragment: &str, place: &str) -> Result<Notes> {
    let mut out: Notes = Vec::new();
    for c in caps(&NOTE, fragment) {
        let (key, body) = (&c[1], &c[2]);
        if !is_key(key) {
            return Err(refused(format!(
                "{place}: `{key}` is not a note key - lower case, digits and hyphens"
            )));
        }
        if out.iter().any(|(k, _)| k == key) {
            return Err(refused(format!(
                "{place}: `{key}` is defined twice in one file"
            )));
        }
        out.push((key.to_owned(), body.to_owned()));
    }
    Ok(out)
}

/// Every note of a page, from its questions' notes fragments, refusing a key defined twice.
///
/// # Errors
/// A key defined in two of the fragments.
pub fn merge(per_question: &[(String, Notes)]) -> Result<Notes> {
    let mut out: Notes = Vec::new();
    let mut seen: HashMap<&str, &str> = HashMap::new();
    for (place, notes) in per_question {
        for (key, body) in notes {
            if let Some(first) = seen.get(key.as_str()) {
                return Err(refused(format!(
                    "`{key}` is defined in {first} and again in {place} - a note key is unique within its page, because the reference names it and nothing else"
                )));
            }
            seen.insert(key, place);
            out.push((key.clone(), body.clone()));
        }
    }
    Ok(out)
}

#[cfg(test)]
mod tests;
