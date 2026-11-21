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

/// The characters Python's `re.IGNORECASE` holds one letter on a `str` pattern: `i`, `I`, `İ` (U+0130) and `ı` (U+0131), each matching
/// the other three (observed 2026-11-16, method: `re.fullmatch("(?i)" + a, b)` for every pair in `CPython` 3.14.4 - all sixteen true, as
/// `[a-z]` takes `İ` and `ı` and `[^i]` takes neither); the regex crate's Unicode simple case folding pairs only `i` and `I`, its other
/// folds (`k` and the Kelvin sign, `s` and the long s) the ones Python makes. Feature 449 T147 (the plan review: the port matches the
/// Python, no ruling).
const DOTTED_I: &str = "iI\u{130}\u{131}";

/// Whether a pattern opens with inline flags that hold `i` (`(?i)`, `(?im)`): Python's `re.I` over the whole pattern.
fn ignores_case(pattern: &str) -> bool {
    pattern
        .strip_prefix("(?")
        .and_then(|rest| rest.split_once(')'))
        .is_some_and(|(flags, _)| {
            !flags.is_empty()
                && flags.chars().all(|c| c.is_ascii_alphabetic())
                && flags.contains('i')
        })
}

/// Whether a class takes one of the four letters: a member that is one, or a range over `i` or `I`.
#[derive(Default)]
struct Class {
    last: Option<char>,
    ranged: bool,
    covers: bool,
}

impl Class {
    fn literal(&mut self, c: char, at_end: bool) {
        if c == '-' && self.last.is_some() && !self.ranged && !at_end {
            self.ranged = true;
            return;
        }
        if self.ranged {
            let lo = self.last.take().unwrap_or(c);
            self.covers |= (lo..=c).contains(&'i') || (lo..=c).contains(&'I');
            self.ranged = false;
            return;
        }
        self.covers |= DOTTED_I.contains(c);
        self.last = Some(c);
    }
}

/// A Python pattern in the regex crate's terms: `\w`, `\W`, `\s`, `\S` and `\b` read as Python reads them, inside a class or out, and
/// `$` outside a class as Python's (the end, or before a final newline); under `(?i)`, the four letters `i`, `I`, `İ` and `ı` one letter
/// as Python's `re.I` holds them ([`DOTTED_I`]).
#[must_use]
pub fn translate(pattern: &str) -> String {
    let space = l7r_shared::py_text::SPACE_CLASS;
    let fold = ignores_case(pattern);
    let mut out = String::with_capacity(pattern.len() * 2);
    let (mut in_class, mut chars) = (false, pattern.chars().peekable());
    let mut class = Class::default();
    // where the class opens in `out`, and whether it is negated: the two letters join it as a class of their own, beside it
    let (mut class_at, mut negated) = (0, false);
    while let Some(c) = chars.next() {
        match c {
            '\\' => {
                let next = chars.next().unwrap_or('\\');
                class.last = None;
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
                class = Class::default();
                class_at = out.len();
                out.push(c);
                negated = chars.peek() == Some(&'^');
                if negated {
                    out.push('^');
                    chars.next();
                }
                if chars.peek() == Some(&']') {
                    out.push_str("\\]");
                    chars.next();
                    class.literal(']', false);
                }
            }
            // a `[` inside a class is a literal to Python and a nested class to the regex crate
            '[' => {
                out.push_str("\\[");
                class.literal('[', false);
            }
            ']' if in_class => {
                in_class = false;
                out.push(c);
                if fold && class.covers {
                    // `[...]` takes the two letters beside its own members, `[^...]` refuses them too
                    let whole = out.split_off(class_at);
                    let joined = if negated {
                        format!("[{whole}&&[^\u{130}\u{131}]]")
                    } else {
                        format!("[{whole}\u{130}\u{131}]")
                    };
                    out.push_str(&joined);
                }
            }
            // a group's header (`(?i)`, `(?:`, `(?P<name>`, `(?<=`) is no letter of the pattern; `(?P=name)` names one wholly
            '(' if !in_class && chars.peek() == Some(&'?') => {
                out.push('(');
                out.push('?');
                chars.next();
                let mut prev = '?';
                while let Some(&h) = chars.peek() {
                    if !(h.is_ascii_alphanumeric()
                        || h == '<'
                        || (h == '=' && prev == 'P')
                        || (prev == '=' && h != ')'))
                    {
                        break;
                    }
                    out.push(h);
                    prev = if prev == '=' { '=' } else { h };
                    chars.next();
                }
            }
            '$' if !in_class => out.push_str(r"(?=\n?\z)"),
            _ if in_class => {
                class.literal(c, chars.peek() == Some(&']'));
                out.push(c);
            }
            'i' | 'I' | '\u{130}' | '\u{131}' if fold => {
                let _ = write!(out, "[{DOTTED_I}]");
            }
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

    #[test]
    fn under_ignorecase_the_dotted_and_dotless_i_are_one_letter_as_python_holds_them() {
        // `CPython` 3.14.4's answers, `bool(re.fullmatch("(?i)" + pattern, text))` (observed 2026-11-16, in the interpreter)
        let four = ['i', 'I', '\u{130}', '\u{131}'];
        for p in four {
            for t in four {
                assert!(py(&format!("(?i)^{p}$")).is_match(&t.to_string()).unwrap());
            }
        }
        for (pattern, text, python) in [
            ("(?i)^[a-z]$", "\u{130}", true),
            ("(?i)^[a-z]$", "\u{131}", true),
            ("(?i)^[A-Z]$", "\u{131}", true),
            ("(?i)^[^i]$", "\u{130}", false),
            ("(?i)^[j-z]$", "\u{131}", false),
            ("(?i)^[ai]$", "\u{131}", true),
            ("(?i)^[-i]$", "\u{130}", true),
            ("(?i)^[i-]$", "-", true),
            ("(?i)^[]i]$", "]", true),
            ("(?i)^[\\wq]$", "\u{130}", true),
            ("(?i)^[[x]$", "[", true),
            ("(?i)^k$", "\u{212a}", true),
            ("(?i)^\u{130}$", "i\u{307}", false),
            ("(?im)^shi$", "SH\u{130}", true),
            ("^i$", "\u{130}", false),
            ("(?i)(?P<id>i)i", "\u{131}\u{131}", true),
            ("(?i)(?:mi)(?<=i)(?=$)", "M\u{130}", true),
            ("(?i)(?<!x)i", "\u{131}", true),
        ] {
            assert_eq!(
                (pattern, py(pattern).is_match(text).unwrap()),
                (pattern, python)
            );
        }
        assert_eq!(translate("(?i)(?:x)"), "(?i)(?:x)");
        // a named back-reference's name is no letter of the pattern
        assert_eq!(translate("(?i)(?P=id)"), "(?i)(?P=id)");
    }
}
