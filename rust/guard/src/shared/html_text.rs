//! Python's `html.unescape`, whole (moved from `rust/gate/src/record/money.rs` by feature 449 T86): the guards' reading of a research page and the gate's money check share one table of `CPython`'s entities.

use std::collections::{HashMap, HashSet};
use std::sync::LazyLock;

use fancy_regex::{Captures, Regex};

/// `CPython`'s own entity tables, generated once from `html.entities.html5`, `html._invalid_charrefs` and `html._invalid_codepoints`: `html.unescape`, whole.
const HTML5: &str = include_str!("../../../gate/src/record/html5_entities.tsv");

static ENTITY: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(r"&(#[0-9]+;?|#[xX][0-9a-fA-F]+;?|[^\t\n\f <&#;]{1,32};?)")
        .unwrap_or_else(|e| unreachable!("{e}"))
});
/// The three tables of `HTML5`, by kind.
struct Tables {
    named: HashMap<&'static str, String>,
    replaced: HashMap<u32, String>,
    invalid: HashSet<u32>,
}

fn hex_text(cells: &str) -> String {
    cells
        .split(' ')
        .filter_map(|c| u32::from_str_radix(c, 16).ok())
        .filter_map(char::from_u32)
        .collect()
}

static TABLES: LazyLock<Tables> = LazyLock::new(|| {
    let mut t = Tables {
        named: HashMap::new(),
        replaced: HashMap::new(),
        invalid: HashSet::new(),
    };
    for row in HTML5.lines() {
        let mut cells = row.splitn(3, '\t');
        let (kind, key, value) = (
            cells.next().unwrap_or(""),
            cells.next().unwrap_or(""),
            cells.next().unwrap_or(""),
        );
        let number = u32::from_str_radix(key, 16).unwrap_or(0);
        match kind {
            "E" => {
                t.named.insert(key, hex_text(value));
            }
            "C" => {
                t.replaced.insert(number, hex_text(value));
            }
            _ => {
                t.invalid.insert(number);
            }
        }
    }
    t
});

/// One numeric reference, as `html._replace_charref` reads it; a number too long to hold is past the last code point.
fn numeric(body: &str) -> String {
    let digits = body[1..].trim_end_matches(';');
    let parsed = match digits.strip_prefix(['x', 'X']) {
        Some(hex) => u32::from_str_radix(hex, 16),
        None => digits.parse(),
    };
    let number = parsed.unwrap_or(u32::MAX);
    if let Some(text) = TABLES.replaced.get(&number) {
        return text.clone();
    }
    if (0xD800..=0xDFFF).contains(&number) || number > 0x10_FFFF {
        return "\u{fffd}".to_owned();
    }
    if TABLES.invalid.contains(&number) {
        return String::new();
    }
    char::from_u32(number).map(String::from).unwrap_or_default()
}

fn entity(caps: &Captures) -> String {
    let body = &caps[1];
    if body.starts_with('#') {
        return numeric(body);
    }
    if let Some(text) = TABLES.named.get(body) {
        return text.clone();
    }
    // the longest matching name, as the standard defines it
    let ends: Vec<usize> = body
        .char_indices()
        .map(|(i, _)| i)
        .filter(|i| *i >= 2)
        .collect();
    for end in ends.into_iter().rev() {
        if let Some(text) = TABLES.named.get(&body[..end]) {
            return format!("{text}{}", &body[end..]);
        }
    }
    format!("&{body}")
}

/// `text` with its character references decoded, as `html.unescape`.
#[must_use]
pub fn unescape(text: &str) -> String {
    ENTITY
        .replace_all(text, |c: &Captures| entity(c))
        .into_owned()
}

#[cfg(test)]
mod tests {
    use super::unescape;

    /// Each answer is `CPython`'s `html.unescape` on the same text (observed 2026-11-10).
    #[test]
    fn entities_are_read_as_html_unescape_reads_them() {
        let cases = [
            ("&amp;&lt;x&gt; &#x27;&#34;", "&<x> '\""),
            ("&nbsp;", "\u{a0}"),
            ("&amp", "&"),
            ("&ampfoo", "&foo"),
            ("&#128;", "\u{20ac}"),
            ("&#0;", "\u{fffd}"),
            ("&#xD800;", "\u{fffd}"),
            ("&#x110000;", "\u{fffd}"),
            ("&#99999999999;", "\u{fffd}"),
            ("&#1;", ""),
            ("&notreal;", "\u{ac}real;"),
            ("&zzz;", "&zzz;"),
            ("&not", "\u{ac}"),
        ];
        for (raw, want) in cases {
            assert_eq!(unescape(raw), want, "{raw}");
        }
    }
}
