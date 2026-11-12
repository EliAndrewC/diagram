//! Python's own reading of whitespace (feature 449 T87): `str.split`, `str.strip` and `re`'s `\s` take the separator characters (`\x1c`-`\x1f`) that Rust's `char::is_whitespace` and the regex crate's `\s` leave out.

/// The characters of `str.isspace`, as the body of a regex character class.
pub const SPACE_CLASS: &str =
    r"\t-\r\x1c-\x1f \x85\xa0\x{1680}\x{2000}-\x{200a}\x{2028}\x{2029}\x{202f}\x{205f}\x{3000}";

/// Whether `c` is whitespace to Python's `str`.
#[must_use]
pub fn is_space(c: char) -> bool {
    matches!(
        c,
        '\t'..='\r'
            | '\x1c'..='\x1f'
            | ' '
            | '\u{85}'
            | '\u{a0}'
            | '\u{1680}'
            | '\u{2000}'..='\u{200a}'
            | '\u{2028}'
            | '\u{2029}'
            | '\u{202f}'
            | '\u{205f}'
            | '\u{3000}'
    )
}

/// `text.strip()`.
#[must_use]
pub fn strip(text: &str) -> &str {
    text.trim_matches(is_space)
}

/// `text.split()`.
#[must_use]
pub fn split(text: &str) -> Vec<&str> {
    text.split(is_space).filter(|p| !p.is_empty()).collect()
}

/// `" ".join(text.split())`.
#[must_use]
pub fn collapse(text: &str) -> String {
    split(text).join(" ")
}

/// A string as Python's `repr` prints it (moved from the gate's `record::bundle` by feature 449 T83: the review ledger's lint names a cell
/// by its repr, and the gate's crates re-export this one).
#[must_use]
pub fn repr(s: &str) -> String {
    use std::fmt::Write as _;
    let quote = if s.contains('\'') && !s.contains('"') {
        '"'
    } else {
        '\''
    };
    let mut out = String::with_capacity(s.len() + 2);
    out.push(quote);
    for c in s.chars() {
        match c {
            '\\' => out.push_str("\\\\"),
            '\n' => out.push_str("\\n"),
            '\t' => out.push_str("\\t"),
            '\r' => out.push_str("\\r"),
            c if c == quote => {
                out.push('\\');
                out.push(c);
            }
            c if !printable(c) => {
                let n = u32::from(c);
                let _ = if n <= 0xff {
                    write!(out, "\\x{n:02x}")
                } else if n <= 0xffff {
                    write!(out, "\\u{n:04x}")
                } else {
                    write!(out, "\\U{n:08x}")
                };
            }
            c => out.push(c),
        }
    }
    out.push(quote);
    out
}

/// `str.isprintable` for one character: not a control, format, separator (but the space), surrogate or private-use one.
fn printable(c: char) -> bool {
    !matches!(u32::from(c),
        0..=0x1f | 0x7f..=0xa0 | 0xad | 0x600..=0x605 | 0x61c | 0x6dd | 0x70f | 0x890..=0x891 | 0x8e2 | 0x1680 | 0x180e
        | 0x2000..=0x200f | 0x2028..=0x202f | 0x205f..=0x2064 | 0x2066..=0x206f | 0x3000 | 0xe000..=0xf8ff | 0xfeff
        | 0xfff9..=0xfffb | 0x1_10bd | 0x1_10cd | 0x1_3430..=0x1_343f | 0x1_bca0..=0x1_bca3 | 0x1_d173..=0x1_d17a | 0xe_0001
        | 0xe_0020..=0xe_007f | 0xf_0000..=0x0010_ffff)
}

#[cfg(test)]
mod tests {
    use super::{collapse, is_space, repr, split, strip};

    #[test]
    fn a_repr_is_pythons() {
        assert_eq!(repr("it's"), "\"it's\"");
        assert_eq!(repr("a'b\"c"), "'a\\'b\"c'");
        assert_eq!(
            repr("\\\n\t\r\u{1}\u{a0}\u{3000}\u{e0001}x\u{57a3}"),
            "'\\\\\\n\\t\\r\\x01\\xa0\\u3000\\U000e0001x\u{57a3}'"
        );
        // one character of each range `str.isprintable` refuses, escaped
        for c in [
            '\u{ad}',
            '\u{600}',
            '\u{61c}',
            '\u{6dd}',
            '\u{70f}',
            '\u{890}',
            '\u{8e2}',
            '\u{1680}',
            '\u{180e}',
            '\u{2000}',
            '\u{2028}',
            '\u{205f}',
            '\u{2066}',
            '\u{e000}',
            '\u{feff}',
            '\u{fff9}',
            '\u{110bd}',
            '\u{110cd}',
            '\u{13430}',
            '\u{1bca0}',
            '\u{1d173}',
            '\u{e0020}',
            '\u{f0000}',
        ] {
            assert!(repr(&c.to_string()).starts_with("'\\"));
        }
    }

    #[test]
    fn the_separator_characters_are_whitespace_as_python_reads_them() {
        for c in [
            '\t', '\r', '\x1c', '\x1f', ' ', '\u{85}', '\u{a0}', '\u{1680}', '\u{2000}',
            '\u{200a}', '\u{2028}', '\u{2029}', '\u{202f}', '\u{205f}', '\u{3000}',
        ] {
            assert!(is_space(c));
        }
        assert!(!is_space('x'));
        assert_eq!(strip("\x1f a\u{a0}"), "a");
        assert_eq!(split(" a\x1db\n c "), ["a", "b", "c"]);
        assert_eq!(collapse("a\x1eb   c"), "a b c");
    }
}
