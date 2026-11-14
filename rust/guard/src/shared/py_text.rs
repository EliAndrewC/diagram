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

/// `float(text)`: Python's whitespace stripped, an underscore only between two digits, `inf` and `nan` read (moved here from the gate's
/// `measure::events` and `trials::budget_change`, which each held a copy, by feature 449 T136 under `ask:449-phase3-remainder`: the review
/// census reads its old rows' figures as `float()` read them, and the crates below `measure` could reach neither copy; one implementation, FR-003).
#[must_use]
pub fn py_float_text(text: &str) -> Option<f64> {
    let t = strip(text);
    let b = t.as_bytes();
    for (i, c) in b.iter().enumerate() {
        if *c == b'_'
            && !(i > 0 && b[i - 1].is_ascii_digit() && b.get(i + 1).is_some_and(u8::is_ascii_digit))
        {
            return None;
        }
    }
    t.replace('_', "").parse().ok()
}

/// Python's `float()` of a value `json.loads` made: a number as it is, `True` one, a string as `float(str)` reads it (moved with
/// `py_float_text`, feature 449 T136).
///
/// # Errors
///
/// `float()`'s `ValueError` or `TypeError`, as the traceback's last line names it.
pub fn py_float_of(v: &serde_json::Value) -> Result<f64, String> {
    use serde_json::Value;
    match v {
        Value::Bool(b) => Ok(f64::from(u8::from(*b))),
        Value::Number(n) => Ok(n.as_f64().unwrap_or(0.0)),
        Value::String(text) => py_float_text(text).ok_or_else(|| {
            format!(
                "ValueError: could not convert string to float: {}",
                repr(text)
            )
        }),
        _ => Err("TypeError: float() argument must be a string or a real number".to_owned()),
    }
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

/// `f"{v:g}"`: six significant digits, trailing zeros dropped, an exponent outside 1e-4..1e6 (moved from the gate's `claims::tunables` by
/// feature 449 T135: `make set-down` and `make claim` write their figures by it too).
#[must_use]
pub fn fmt_g(v: f64) -> String {
    if v == 0.0 {
        return if v.is_sign_negative() {
            "-0".to_owned()
        } else {
            "0".to_owned()
        };
    }
    if v.is_infinite() {
        return if v > 0.0 {
            "inf".to_owned()
        } else {
            "-inf".to_owned()
        };
    }
    let sci = format!("{v:.5e}");
    let (mantissa, exp) = sci.split_once('e').unwrap_or((&sci, "0"));
    let exp: i32 = exp.parse().unwrap_or(0);
    let trim = |s: &str| {
        if s.contains('.') {
            s.trim_end_matches('0').trim_end_matches('.').to_owned()
        } else {
            s.to_owned()
        }
    };
    if (-4..6).contains(&exp) {
        let decimals = usize::try_from(5 - exp).unwrap_or(0);
        trim(&format!("{v:.decimals$}"))
    } else {
        format!(
            "{}e{}{:02}",
            trim(mantissa),
            if exp < 0 { '-' } else { '+' },
            exp.abs()
        )
    }
}

#[cfg(test)]
mod tests {
    use super::{collapse, fmt_g, is_space, py_float_of, py_float_text, repr, split, strip};

    #[test]
    fn a_number_is_written_as_python_writes_it() {
        for (v, s) in [
            (12.5, "12.5"),
            (1_234_567.0, "1.23457e+06"),
            (999_999.5, "1e+06"),
            (123_456.0, "123456"),
            (0.0001, "0.0001"),
            (0.000_01, "1e-05"),
            (100.0, "100"),
            (0.0, "0"),
            (-0.0, "-0"),
            (-2.5, "-2.5"),
            (f64::INFINITY, "inf"),
            (f64::NEG_INFINITY, "-inf"),
        ] {
            assert_eq!(fmt_g(v), s, "{v}");
        }
    }

    #[test]
    fn float_reads_text_and_values_as_python_reads_them() {
        assert_eq!(py_float_text(" 6_000 "), Some(6000.0));
        assert_eq!(py_float_text("1."), Some(1.0));
        assert_eq!(py_float_text("-Infinity"), Some(f64::NEG_INFINITY));
        for bad in ["_1", "1_", "1__0", ".", "", "abc"] {
            assert_eq!(py_float_text(bad), None, "{bad}");
        }
        assert_eq!(py_float_of(&serde_json::json!(true)), Ok(1.0));
        assert_eq!(py_float_of(&serde_json::json!(2.5)), Ok(2.5));
        assert_eq!(py_float_of(&serde_json::json!("7")), Ok(7.0));
        assert!(py_float_of(&serde_json::json!("x"))
            .unwrap_err()
            .starts_with("ValueError"));
        assert!(py_float_of(&serde_json::json!([1]))
            .unwrap_err()
            .starts_with("TypeError"));
    }

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
