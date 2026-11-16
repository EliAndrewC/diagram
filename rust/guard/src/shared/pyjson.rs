//! Python's `json.dumps`, byte for byte (moved from `rust/gate/src/logs.rs` by feature 449 T86, so the checks state's writer in this crate shares it): the file shapes every
//! state file, record and log of the repository was written in.

use std::fmt::Write as _;

use serde_json::{Map, Value};

/// A string as Python's `json.dumps` writes it: every non-ASCII character escaped.
#[must_use]
pub fn ascii_string(text: &str, ascii: bool) -> String {
    let mut out = String::with_capacity(text.len() + 2);
    for c in Value::String(text.to_owned()).to_string().chars() {
        // DELETE IS ESCAPED TOO (feature 449 T143): Python's `ensure_ascii` writes every character outside space to `~` as `\uXXXX`,
        // and serde_json leaves `\x7f` bare: the shell's guard-log entries escaped it, and the guard's own writer now shares this one
        if ascii && c == '\u{7f}' {
            out += "\\u007f";
        } else if c.is_ascii() || !ascii {
            out.push(c);
        } else {
            let mut units = [0u16; 2];
            for unit in c.encode_utf16(&mut units) {
                let _ = write!(out, "\\u{unit:04x}");
            }
        }
    }
    out
}

/// A float as Python's `repr` writes it: shortest digits, positional from 1e-4 up to 1e16, and a signed two-digit exponent outside that;
/// `inf`, `-inf` and `nan` as Python names them (feature 449 T139: `float("inf")` of a figure printed `inf.0` before).
#[must_use]
pub fn py_float(f: f64) -> String {
    if !f.is_finite() {
        return if f.is_nan() {
            "nan"
        } else if f > 0.0 {
            "inf"
        } else {
            "-inf"
        }
        .to_owned();
    }
    let scientific = format!("{f:e}");
    let (mantissa, exponent) = scientific.split_once('e').unwrap_or((&scientific, "0"));
    let exponent: i32 = exponent.parse().unwrap_or(0);
    if (-4..16).contains(&exponent) {
        let plain = format!("{f}");
        return if plain.contains('.') {
            plain
        } else {
            plain + ".0"
        };
    }
    format!(
        "{mantissa}e{}{:02}",
        if exponent < 0 { '-' } else { '+' },
        exponent.abs()
    )
}

/// Python's `bool()` of what `json.loads` made of a value: `None`, `False`, a zero, and an empty string, list or dict are false - the
/// test a Python `x or y` makes (feature 449 T143: the guard log's fields were each `payload.get(k) or ""`).
#[must_use]
pub fn truthy(value: &Value) -> bool {
    match value {
        Value::Null => false,
        Value::Bool(b) => *b,
        Value::Number(n) => n.as_f64() != Some(0.0),
        Value::String(s) => !s.is_empty(),
        Value::Array(items) => !items.is_empty(),
        Value::Object(map) => !map.is_empty(),
    }
}

/// A JSON value as Python's `str()` prints what `json.loads` made of it (moved from the gate's `record::bundle` by feature 449 T119: the
/// event-log reader in this crate names an edit's path and time by it, and the gate's crates re-export this one).
#[must_use]
pub fn py_str(value: &Value) -> String {
    match value {
        Value::Null => "None".to_owned(),
        Value::Bool(b) => if *b { "True" } else { "False" }.to_owned(),
        Value::String(s) => s.clone(),
        Value::Number(n) => n
            .as_f64()
            .filter(|_| n.is_f64())
            .map_or_else(|| n.to_string(), py_float),
        other => value_repr(other),
    }
}

/// `repr()` of what `json.loads` made of a value: a list or dict as Python prints one.
#[must_use]
fn value_repr(value: &Value) -> String {
    use crate::shared::py_text::repr;
    match value {
        Value::String(s) => repr(s),
        Value::Array(items) => format!(
            "[{}]",
            items.iter().map(value_repr).collect::<Vec<_>>().join(", ")
        ),
        Value::Object(map) => format!(
            "{{{}}}",
            map.iter()
                .map(|(k, v)| format!("{}: {}", repr(k), value_repr(v)))
                .collect::<Vec<_>>()
                .join(", ")
        ),
        other => py_str(other),
    }
}

/// `value` as Python's `json.dumps(value, indent=indent)` writes it, byte for byte.
fn write_value(value: &Value, indent: Option<usize>, level: usize, out: &mut String, ascii: bool) {
    let line =
        |depth: usize| indent.map_or_else(String::new, |n| format!("\n{}", " ".repeat(n * depth)));
    let comma = if indent.is_some() { "," } else { ", " };
    match value {
        Value::Number(n) if n.is_f64() => *out += &py_float(n.as_f64().unwrap_or(0.0)),
        Value::String(s) => match python_number(s) {
            Some(text) => *out += text,
            None => *out += &ascii_string(s, ascii),
        },
        Value::Array(items) if !items.is_empty() => {
            out.push('[');
            for (i, item) in items.iter().enumerate() {
                *out += if i == 0 { "" } else { comma };
                *out += &line(level + 1);
                write_value(item, indent, level + 1, out, ascii);
            }
            *out += &line(level);
            out.push(']');
        }
        Value::Object(map) if !map.is_empty() => {
            out.push('{');
            for (i, (key, item)) in map.iter().enumerate() {
                *out += if i == 0 { "" } else { comma };
                *out += &line(level + 1);
                *out += &ascii_string(key, ascii);
                *out += ": ";
                write_value(item, indent, level + 1, out, ascii);
            }
            *out += &line(level);
            out.push('}');
        }
        other => *out += &other.to_string(),
    }
}

/// The mark [`loads`] puts before a number `serde_json` cannot hold, kept as a string: a private-use character no JSON a hook or a tool
/// writes starts a string with.
const KEPT: char = '\u{10FE00}';

/// The number's text where `s` is one [`loads`] kept: an integer's digits, or `NaN`, `Infinity`, `-Infinity`.
fn python_number(s: &str) -> Option<&str> {
    let text = s.strip_prefix(KEPT)?;
    let digits = text.strip_prefix('-').unwrap_or(text);
    let integer = !digits.is_empty() && digits.bytes().all(|b| b.is_ascii_digit());
    (integer || matches!(text, "NaN" | "Infinity" | "-Infinity")).then_some(text)
}

/// `json.loads(text)` as Python reads the numbers `serde_json` cannot hold (feature 449 T143, the plan review: the guard log's door wrote
/// `1.2345678901234568e+29` where `guard_log`'s Python kept `123456789012345678901234567890`): an integer past 64 bits keeps its digits,
/// `NaN`, `Infinity` and `-Infinity` are read (Python's extension to JSON), and a float past the double's range is Python's `inf`. Each is
/// held as a string carrying [`KEPT`] that [`dumps`] writes back as the number; [`plain`] drops them where a reader wants only the
/// strings. Scoped to this reader - `serde_json`'s `arbitrary_precision` is a feature of the whole build, and would change every
/// crate's numbers (`1.50` written as read, not as Python's `1.5`).
///
/// # Errors
/// What `serde_json` says of text that is not JSON once the numbers are kept.
pub fn loads(text: &str) -> Result<Value, serde_json::Error> {
    let mut out = String::with_capacity(text.len());
    let mut chars = text.char_indices().peekable();
    let keep = |out: &mut String, number: &str| {
        out.push('"');
        out.push(KEPT);
        out.push_str(number);
        out.push('"');
    };
    while let Some((at, c)) = chars.next() {
        if c == '"' {
            out.push(c);
            let mut escaped = false;
            for (_, s) in chars.by_ref() {
                out.push(s);
                if escaped {
                    escaped = false;
                } else if s == '\\' {
                    escaped = true;
                } else if s == '"' {
                    break;
                }
            }
            continue;
        }
        if c == '-' || c.is_ascii_alphanumeric() {
            let mut end = at + c.len_utf8();
            while let Some(&(i, n)) = chars.peek() {
                if !(n.is_ascii_alphanumeric() || matches!(n, '-' | '+' | '.')) {
                    break;
                }
                end = i + n.len_utf8();
                chars.next();
            }
            let token = &text[at..end];
            let digits = token.strip_prefix('-').unwrap_or(token);
            let integer = !digits.is_empty() && digits.bytes().all(|b| b.is_ascii_digit());
            if matches!(token, "NaN" | "Infinity" | "-Infinity")
                || (integer && token.parse::<i64>().is_err() && token.parse::<u64>().is_err())
            {
                keep(&mut out, token);
            } else if !integer
                && token
                    .bytes()
                    .next()
                    .is_some_and(|b| b == b'-' || b.is_ascii_digit())
                && token.parse::<f64>().is_ok_and(f64::is_infinite)
            {
                keep(
                    &mut out,
                    if token.starts_with('-') {
                        "-Infinity"
                    } else {
                        "Infinity"
                    },
                );
            } else {
                out.push_str(token);
            }
            continue;
        }
        out.push(c);
    }
    serde_json::from_str(&out)
}

/// `value` with each number [`loads`] kept as a string made `null`, for a reader that takes a field only when it is a string (the
/// session's resolver read `isinstance(v, str)`).
#[must_use]
pub fn plain(value: &Value) -> Value {
    match value {
        Value::String(s) if python_number(s).is_some() => Value::Null,
        Value::Array(items) => Value::Array(items.iter().map(plain).collect()),
        Value::Object(map) => {
            Value::Object(map.iter().map(|(k, v)| (k.clone(), plain(v))).collect())
        }
        other => other.clone(),
    }
}

/// `json.dumps(value, indent=indent, ensure_ascii=ascii)`.
#[must_use]
pub fn dumps(value: &Value, indent: Option<usize>, ascii: bool) -> String {
    let mut out = String::new();
    write_value(value, indent, 0, &mut out, ascii);
    out
}

/// Every object's keys in sorted order, as `sort_keys=True` writes them.
#[must_use]
pub fn sorted(value: &Value) -> Value {
    match value {
        Value::Object(map) => {
            let mut keys: Vec<&String> = map.keys().collect();
            keys.sort();
            let mut out = Map::new();
            for k in keys {
                out.insert(k.clone(), sorted(&map[k]));
            }
            Value::Object(out)
        }
        Value::Array(items) => Value::Array(items.iter().map(sorted).collect()),
        other => other.clone(),
    }
}

#[cfg(test)]
mod tests {
    use serde_json::json;

    use super::{dumps, loads, plain, py_float, py_str, sorted, truthy, value_repr};

    #[test]
    fn a_value_prints_as_python_str_prints_it() {
        assert_eq!(py_str(&json!(null)), "None");
        assert_eq!(py_str(&json!(true)), "True");
        assert_eq!(py_str(&json!(false)), "False");
        assert_eq!(py_str(&json!("a")), "a");
        assert_eq!(py_str(&json!(3)), "3");
        assert_eq!(py_str(&json!(2.5)), "2.5");
        assert_eq!(
            py_str(&json!([1, "a'", {"k": null}])),
            "[1, \"a'\", {'k': None}]"
        );
        assert_eq!(value_repr(&json!("x")), "'x'");
        let falsy = [
            json!(null),
            json!(false),
            json!(0),
            json!(0.0),
            json!(""),
            json!([]),
            json!({}),
        ];
        assert!(falsy.iter().all(|v| !truthy(v)));
        let true_ = [
            json!(true),
            json!(-1),
            json!(0.5),
            json!("0"),
            json!([0]),
            json!({"a": null}),
        ];
        assert!(true_.iter().all(truthy));
    }

    #[test]
    fn a_float_writes_as_python_repr_writes_it() {
        assert_eq!(py_float(1_762_000_000.125), "1762000000.125");
        assert_eq!(py_float(0.0001), "0.0001");
        assert_eq!(py_float(1e16), "1e+16");
        assert_eq!(py_float(1.5e-7), "1.5e-07");
        assert_eq!(py_float(3.0), "3.0");
        assert_eq!(py_float(f64::INFINITY), "inf");
        assert_eq!(py_float(f64::NEG_INFINITY), "-inf");
        assert_eq!(py_float(f64::NAN), "nan");
    }

    /// The numbers `serde_json` cannot hold, read and written back as Python wrote them (feature 449 T143).
    #[test]
    fn loads_keeps_what_python_keeps() {
        let text = r#"{"big": 123456789012345678901234567890, "neg": -99999999999999999999, "nan": NaN, "inf": Infinity,
            "ninf": -Infinity, "huge": 1e400, "nhuge": -1e400, "small": 18446744073709551615, "f": 1.5, "s": "-1 NaN \" 1e400",
            "l": [12345678901234567890123, true, null, false], "e": 2e5}"#;
        let v = loads(text).unwrap();
        assert_eq!(
            dumps(&v, None, true),
            "{\"big\": 123456789012345678901234567890, \"neg\": -99999999999999999999, \"nan\": NaN, \"inf\": Infinity, \"ninf\": -Infinity, \"huge\": Infinity, \"nhuge\": -Infinity, \"small\": 18446744073709551615, \"f\": 1.5, \"s\": \"-1 NaN \\\" 1e400\", \"l\": [12345678901234567890123, true, null, false], \"e\": 200000.0}"
        );
        assert_eq!(plain(&v)["big"], json!(null));
        assert_eq!(plain(&v)["s"], v["s"]);
        assert_eq!(plain(&v)["l"][1], json!(true));
        assert!(loads("{\"a\": 1} x").is_err());
        assert!(loads("not json").is_err());
        // a string that only looks like a kept number is written as the string it is
        assert_eq!(
            dumps(&json!("\u{10FE00}x"), None, true),
            "\"\\udbff\\ude00x\""
        );
        assert_eq!(
            dumps(&json!("\u{10FE00}"), None, true),
            "\"\\udbff\\ude00\""
        );
    }

    #[test]
    fn dumps_writes_python_shapes() {
        let v = json!({"b": [1, {"c": 2.0}], "a": "caf\u{e9}\"q\"\n", "e": {}, "f": []});
        assert_eq!(
            dumps(&v, None, true),
            "{\"b\": [1, {\"c\": 2.0}], \"a\": \"caf\\u00e9\\\"q\\\"\\n\", \"e\": {}, \"f\": []}"
        );
        assert_eq!(
            dumps(&v, None, false),
            "{\"b\": [1, {\"c\": 2.0}], \"a\": \"caf\u{e9}\\\"q\\\"\\n\", \"e\": {}, \"f\": []}"
        );
        let nested = sorted(&json!({"z": {"b": 1, "a": 2}, "a": [{"d": 1, "c": 2}]}));
        assert_eq!(
            dumps(&nested, Some(1), true),
            "{\n \"a\": [\n  {\n   \"c\": 2,\n   \"d\": 1\n  }\n ],\n \"z\": {\n  \"a\": 2,\n  \"b\": 1\n }\n}"
        );
        assert_eq!(dumps(&json!(null), None, true), "null");
        assert_eq!(dumps(&json!("a\u{7f}"), None, true), "\"a\\u007f\"");
        assert_eq!(dumps(&json!("a\u{7f}"), None, false), "\"a\u{7f}\"");
    }
}
