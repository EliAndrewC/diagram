//! A quotation's ORIGINAL-language text, stored apart from its translation (`record/originals.py`, feature 292; ported by feature 449
//! T144). The notes a session edits keep a placeholder `<span class="orig" data-orig="<key>#<n>"></span>` where an original stood; the
//! original lives in the question's `.originals.html`, and the assembly puts it back, wrapped, so every reader meets the note's text as
//! before. A UNIT is `original: 「...」` with any originals joined to it in one run; brackets nest, so a unit closes at depth zero. The
//! placeholder pattern and the stored table are `core::record::units`' (FR-003).

use std::fmt::Write as _;
use std::sync::LazyLock;

use fancy_regex::{Captures, Regex};
use l7r_gate_core::record::units::{stored_table, ORIG_STORED, ORIG_TOKEN};

use crate::{caps, re, Error, Result, SPACE_CLASS};

pub const ORIGINALS_SUFFIX: &str = ".originals.html";
static START: LazyLock<Regex> = LazyLock::new(|| re(&format!("original:[{SPACE_CLASS}]*\u{300c}")));
/// What may stand between two originals of one run: a joiner, and perhaps a repeated `original:`.
static JOIN: LazyLock<Regex> = LazyLock::new(|| {
    re(&format!(
        "^[{SPACE_CLASS}]*(?:and|/|,|;)?[{SPACE_CLASS}]*(?:original:[{SPACE_CLASS}]*)?(?=\u{300c})"
    ))
});
static NOTE: LazyLock<Regex> =
    LazyLock::new(|| re(r#"(?s)(<li data-note="([^"]+)">)(.*?)(</li>)"#));

/// Just past the bracket that closes the one opening at `at`, depth counted (the half-width forms too: a source's own nested `｢...｣`).
fn close(text: &str, at: usize) -> Option<usize> {
    let mut depth = 0_i32;
    for (i, c) in text[at..].char_indices() {
        match c {
            '\u{300c}' | '\u{ff62}' => depth += 1,
            '\u{300d}' | '\u{ff63}' => {
                depth -= 1;
                if depth == 0 {
                    return Some(at + i + c.len_utf8());
                }
            }
            _ => {}
        }
    }
    None
}

/// The [start, end) of every original run in one note's text, as byte offsets.
#[must_use]
pub fn units(text: &str) -> Vec<(usize, usize)> {
    let mut out = Vec::new();
    let mut pos = 0;
    while let Some(m) = START.find_from_pos(text, pos).ok().flatten() {
        let Some(mut end) = close(text, m.end() - '\u{300c}'.len_utf8()) else {
            break;
        };
        while let Some(j) = JOIN.find(&text[end..]).ok().flatten() {
            match close(text, end + j.end()) {
                Some(next) if next > 0 => end = next,
                _ => break,
            }
        }
        out.push((m.start(), end));
        pos = end;
    }
    out
}

/// `int()` of a stored reference's number.
fn number(text: &str) -> Result<i64> {
    let t = l7r_guard::shared::py_text::strip(text);
    let digits: Option<String> = t
        .chars()
        .enumerate()
        .map(|(i, c)| {
            crate::digit_value(c)
                .and_then(|d| char::from_digit(d, 10))
                .or((i == 0 && matches!(c, '-' | '+')).then_some(c))
        })
        .collect();
    digits.and_then(|d| d.parse().ok()).ok_or_else(|| {
        Error::new(
            "ValueError",
            format!(
                "invalid literal for int() with base 10: {}",
                l7r_guard::shared::py_text::repr(text)
            ),
        )
    })
}

/// `ref.rsplit("#", 1)`: the key and the number's text.
fn halves(reference: &str) -> Result<(&str, &str)> {
    reference.rsplit_once('#').ok_or_else(|| {
        Error::new(
            "ValueError",
            "not enough values to unpack (expected 2, got 1)",
        )
    })
}

/// (the notes with a placeholder for each original still written inline, the originals file with those runs appended). A run already
/// moved stays; a new one in the same note is numbered after the note's highest, so a session writes a note the natural way and
/// `make record` moves it.
///
/// # Errors
/// A stored reference or placeholder whose number is not a number, as Python's `int()` refused it.
pub fn split(notes_html: &str, originals_html: &str) -> Result<(String, String)> {
    let mut stored: Vec<(String, i64)> = Vec::new();
    for c in caps(&ORIG_STORED, originals_html) {
        let (key, n) = halves(&c[1])?;
        let n = number(n)?;
        match stored.iter_mut().find(|(k, _)| k == key) {
            Some(slot) => slot.1 = slot.1.max(n),
            None => stored.push((key.to_owned(), n.max(0))),
        }
    }
    let mut added = String::new();
    let mut fault = None;
    let text = NOTE
        .replace_all(notes_html, |m: &Captures| {
            let (key, body) = (&m[2], &m[3]);
            let mut n = stored.iter().find(|(k, _)| k == key).map_or(0, |s| s.1);
            for t in caps(&ORIG_TOKEN, body) {
                match halves(&t[1]).and_then(|(_, x)| number(x)) {
                    Ok(v) => n = n.max(v),
                    Err(e) => {
                        fault.get_or_insert(e);
                    }
                }
            }
            let (mut parts, mut last) = (String::new(), 0);
            for (a, b) in units(body) {
                n += 1;
                let reference = format!("{key}#{n}");
                let _ = writeln!(added, "<li data-orig=\"{reference}\">{}</li>", &body[a..b]);
                parts.push_str(&body[last..a]);
                let _ = write!(
                    parts,
                    r#"<span class="orig" data-orig="{reference}"></span>"#
                );
                last = b;
            }
            format!("{}{parts}{}{}", &m[1], &body[last..], &m[4])
        })
        .into_owned();
    match fault {
        Some(e) => Err(e),
        None => Ok((text, format!("{originals_html}{added}"))),
    }
}

/// Does this notes text hold a placeholder, which needs its originals file?
#[must_use]
pub fn has_placeholder(notes_html: &str) -> bool {
    ORIG_TOKEN.is_match(notes_html).unwrap_or(false)
}

/// The notes with each placeholder replaced by its original - wrapped in `<span class="orig">` for the pages a reader opens, or bare to
/// reproduce the text as it was before the split.
///
/// # Errors
/// A placeholder with no stored original (Python's `KeyError`): the original would silently vanish from the page.
pub fn restore(notes_html: &str, originals_html: &str, wrapped: bool) -> Result<String> {
    let table = stored_table(originals_html);
    let mut missing = None;
    let text = ORIG_TOKEN
        .replace_all(notes_html, |m: &Captures| {
            let reference = &m[1];
            match table.get(reference) {
                Some(original) if wrapped => format!(r#"<span class="orig">{original}</span>"#),
                Some(original) => original.clone(),
                None => {
                    missing.get_or_insert_with(|| reference.to_owned());
                    String::new()
                }
            }
        })
        .into_owned();
    match missing {
        Some(r) => Err(Error::new(
            "KeyError",
            format!("no original stored for `{r}` - its `.originals.html` lacks `<li data-orig=\"{r}\">`"),
        )),
        None => Ok(text),
    }
}

#[cfg(test)]
mod tests;
