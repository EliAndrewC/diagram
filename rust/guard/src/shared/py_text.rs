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

#[cfg(test)]
mod tests {
    use super::{collapse, is_space, split, strip};

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
