//! Python's own reading of a pattern's classes and of `str.casefold`, for the record tools ported by feature 449 T145 (phase 4's S2 under
//! `ask:449-phase4-slices`). Measured, not assumed (observed 2026-11-16, method: every code point through `CPython` 3.14.4's `re` and the
//! regex crate the gate builds): Python's `\w` is exactly `[\p{L}\p{N}_]` there, where the regex crate's `\w` also takes the marks; its
//! `\d` is the regex crate's; its `\s` adds `\x1c`-`\x1f` (`py_text::SPACE_CLASS`). `str.lower` matched `char::to_lowercase` on every code
//! point, and `casefold` differs from it on 297, held in `casefold.tsv`.

use std::collections::HashMap;
use std::fmt::Write as _;
use std::sync::LazyLock;

/// Python's `\w`, as a regex class body.
pub const WORD: &str = r"\p{L}\p{N}_";

/// Python's `\b`: a place between a word character and anything else.
#[must_use]
pub fn boundary() -> String {
    format!(r"(?:(?<=[{WORD}])(?![{WORD}])|(?<![{WORD}])(?=[{WORD}]))")
}

/// A Python pattern in the regex crate's terms: `\w`, `\W`, `\s`, `\S` and `\b` read as Python reads them, inside a class or out, and
/// `$` outside a class as Python's (the end, or before a final newline).
#[must_use]
pub fn translate(pattern: &str) -> String {
    let space = l7r_guard::shared::py_text::SPACE_CLASS;
    let mut out = String::with_capacity(pattern.len() * 2);
    let (mut in_class, mut chars) = (false, pattern.chars().peekable());
    while let Some(c) = chars.next() {
        match c {
            '\\' => {
                let next = chars.next().unwrap_or('\\');
                match (next, in_class) {
                    ('w', true) => out.push_str(WORD),
                    ('s', true) => out.push_str(space),
                    ('w', false) => {
                        let _ = write!(out, "[{WORD}]");
                    }
                    ('W', false) => {
                        let _ = write!(out, "[^{WORD}]");
                    }
                    ('s', false) => {
                        let _ = write!(out, "[{space}]");
                    }
                    ('S', false) => {
                        let _ = write!(out, "[^{space}]");
                    }
                    ('b', false) => out.push_str(&boundary()),
                    _ => {
                        out.push('\\');
                        out.push(next);
                    }
                }
            }
            '[' if !in_class => {
                in_class = true;
                out.push(c);
                if chars.peek() == Some(&'^') {
                    out.push('^');
                    chars.next();
                }
                if chars.peek() == Some(&']') {
                    out.push_str("\\]");
                    chars.next();
                }
            }
            // a `[` inside a class is a literal to Python and a nested class to the regex crate
            '[' => out.push_str("\\["),
            ']' if in_class => {
                in_class = false;
                out.push(c);
            }
            '$' if !in_class => out.push_str(r"(?=\n?\z)"),
            _ => out.push(c),
        }
    }
    out
}

/// A Python pattern compiled.
#[must_use]
pub fn py(pattern: &str) -> fancy_regex::Regex {
    crate::re(&translate(pattern))
}

const FOLDS: &str = include_str!("pyre/casefold.tsv");

static FOLD: LazyLock<HashMap<char, String>> = LazyLock::new(|| {
    let hex = |h: &str| u32::from_str_radix(h, 16).ok().and_then(char::from_u32);
    FOLDS
        .lines()
        .filter(|l| !l.starts_with('#'))
        .filter_map(|l| {
            let (from, to) = l.split_once('\t')?;
            Some((hex(from)?, to.split(' ').filter_map(hex).collect()))
        })
        .collect()
});

/// `text.casefold()`.
#[must_use]
pub fn casefold(text: &str) -> String {
    let mut out = String::with_capacity(text.len());
    for c in text.chars() {
        match FOLD.get(&c) {
            Some(to) => out.push_str(to),
            None => out.extend(c.to_lowercase()),
        }
    }
    out
}

#[cfg(test)]
mod tests {
    use super::{boundary, casefold, py, translate};

    #[test]
    fn python_folds_and_bounds_words_as_it_does() {
        assert_eq!(casefold("Straße ﬀ KELVIN K Σ"), "strasse ff kelvin k σ");
        let b = crate::re(&format!("{}cat{}", boundary(), boundary()));
        assert!(b.is_match("a cat.").unwrap());
        assert!(!b.is_match("concat").unwrap());
        assert!(!b.is_match("猫cat").unwrap());
        assert!(py(r"^\w+\s[\w-]$").is_match("ab\x1c-\n").unwrap());
        assert!(!py(r"\W\S[^]x]").is_match(" a]").unwrap());
        assert!(py(r"[[]").is_match("[").unwrap());
        assert!(py(r"\W\S[^]x]").is_match(" ab").unwrap());
        assert_eq!(translate(r"\d\\"), r"\d\\");
    }
}
