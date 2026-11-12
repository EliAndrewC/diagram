//! Python's `json.dumps`, byte for byte (moved from `rust/gate/src/logs.rs` by feature 449 T86, so the checks state's writer in this crate shares it): the file shapes every
//! state file, record and log of the repository was written in.

use std::fmt::Write as _;

use serde_json::{Map, Value};

/// A string as Python's `json.dumps` writes it: every non-ASCII character escaped.
#[must_use]
pub fn ascii_string(text: &str, ascii: bool) -> String {
    let mut out = String::with_capacity(text.len() + 2);
    for c in Value::String(text.to_owned()).to_string().chars() {
        if c.is_ascii() || !ascii {
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

/// A float as Python's `repr` writes it: shortest digits, positional from 1e-4 up to 1e16, and a signed two-digit exponent outside that.
#[must_use]
pub fn py_float(f: f64) -> String {
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
        Value::String(s) => *out += &ascii_string(s, ascii),
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

    use super::{dumps, py_float, py_str, sorted, value_repr};

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
    }

    #[test]
    fn a_float_writes_as_python_repr_writes_it() {
        assert_eq!(py_float(1_762_000_000.125), "1762000000.125");
        assert_eq!(py_float(0.0001), "0.0001");
        assert_eq!(py_float(1e16), "1e+16");
        assert_eq!(py_float(1.5e-7), "1.5e-07");
        assert_eq!(py_float(3.0), "3.0");
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
    }
}
