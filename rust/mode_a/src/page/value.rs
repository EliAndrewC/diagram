//! What the page writer's Python did with a value `json.load` made (feature 449 T150): `float()` of it, `for x in v or []`, `x, y = p`,
//! `q[0]`, and `min`/`max` over a list - each failing as the Python failed.
//!
//! Research: plumbing - NONE

use l7r_gate_research::Error;
use serde_json::Value;

use crate::py::{iterate, max, min, type_name};

/// `float(v)`.
///
/// # Errors
/// Python's `ValueError` for text that is no number, `TypeError` naming the type for anything but a number, a bool or text.
pub fn float_of(v: &Value) -> Result<f64, Error> {
    match v {
        Value::String(s) => crate::py::float(s),
        Value::Bool(b) => Ok(f64::from(u8::from(*b))),
        Value::Number(n) => Ok(n.as_f64().unwrap_or(f64::NAN)),
        other => Err(Error::new(
            "TypeError",
            format!(
                "float() argument must be a string or a real number, not '{}'",
                type_name(other)
            ),
        )),
    }
}

/// What `for x in v or []` walks: nothing for an absent or falsy value, else the value's items.
///
/// # Errors
/// A truthy value that is not iterable.
pub fn items(v: Option<&Value>) -> Result<Vec<Value>, Error> {
    match v {
        Some(v) if l7r_guard::shared::pyjson::truthy(v) => iterate(v),
        _ => Ok(Vec::new()),
    }
}

/// `x, y = p`.
///
/// # Errors
/// A value that is not iterable, or does not hold exactly two items.
pub fn unpack2(p: &Value) -> Result<(Value, Value), Error> {
    let mut all = iterate(p).map_err(|_| {
        Error::new(
            "TypeError",
            format!("cannot unpack non-iterable {} object", type_name(p)),
        )
    })?;
    match all.len() {
        2 => {
            let y = all.pop().unwrap_or(Value::Null);
            Ok((all.pop().unwrap_or(Value::Null), y))
        }
        n if n > 2 => Err(Error::new(
            "ValueError",
            format!("too many values to unpack (expected 2, got {n})"),
        )),
        n => Err(Error::new(
            "ValueError",
            format!("not enough values to unpack (expected 2, got {n})"),
        )),
    }
}

/// `q[i]` of a list, a string or a dict.
///
/// # Errors
/// An index past the end, a dict without the key, or a value that cannot be indexed.
pub fn index(q: &Value, i: usize) -> Result<Value, Error> {
    let out_of_range = |what: &str| Error::new("IndexError", format!("{what} index out of range"));
    match q {
        Value::Array(items) => items.get(i).cloned().ok_or_else(|| out_of_range("list")),
        Value::String(s) => s
            .chars()
            .nth(i)
            .map(|c| Value::from(c.to_string()))
            .ok_or_else(|| out_of_range("string")),
        Value::Object(map) => map
            .get(&i.to_string())
            .cloned()
            .ok_or_else(|| Error::new("KeyError", i.to_string())),
        other => Err(Error::new(
            "TypeError",
            format!("'{}' object is not subscriptable", type_name(other)),
        )),
    }
}

/// `(min(values), max(values))` as Python's: the first of equals kept.
#[must_use]
pub fn span(values: &[f64]) -> (f64, f64) {
    let lo = values.iter().copied().reduce(min).unwrap_or(f64::NAN);
    let hi = values.iter().copied().reduce(max).unwrap_or(f64::NAN);
    (lo, hi)
}

#[cfg(test)]
mod tests {
    use serde_json::json;

    use super::{float_of, index, items, span, unpack2};

    #[test]
    fn a_value_is_read_as_the_python_reads_it() {
        assert_eq!(float_of(&json!("1.5")).ok(), Some(1.5));
        assert_eq!(float_of(&json!(2)).ok(), Some(2.0));
        assert_eq!(float_of(&json!("x")).unwrap_err().kind, "ValueError");
        assert_eq!(
            float_of(&json!(null)).unwrap_err().message,
            "float() argument must be a string or a real number, not 'NoneType'"
        );
        assert_eq!(float_of(&json!(true)).ok(), Some(1.0));
        assert!(items(None).unwrap().is_empty() && items(Some(&json!([]))).unwrap().is_empty());
        assert_eq!(items(Some(&json!([1, 2]))).unwrap().len(), 2);
        assert_eq!(items(Some(&json!(3))).unwrap_err().kind, "TypeError");
        assert_eq!(unpack2(&json!([1, 2])).unwrap(), (json!(1), json!(2)));
        assert_eq!(unpack2(&json!("ab")).unwrap(), (json!("a"), json!("b")));
        assert_eq!(
            unpack2(&json!([1, 2, 3])).unwrap_err().message,
            "too many values to unpack (expected 2, got 3)"
        );
        assert_eq!(
            unpack2(&json!([1])).unwrap_err().message,
            "not enough values to unpack (expected 2, got 1)"
        );
        assert_eq!(
            unpack2(&json!(1)).unwrap_err().message,
            "cannot unpack non-iterable int object"
        );
        assert_eq!(index(&json!([4, 5]), 1).unwrap(), json!(5));
        assert_eq!(index(&json!([4]), 1).unwrap_err().kind, "IndexError");
        assert_eq!(index(&json!("ab"), 0).unwrap(), json!("a"));
        assert_eq!(
            index(&json!("a"), 3).unwrap_err().message,
            "string index out of range"
        );
        assert_eq!(index(&json!({"0": 1}), 0).unwrap(), json!(1));
        assert_eq!(index(&json!({}), 0).unwrap_err().kind, "KeyError");
        assert_eq!(index(&json!(1), 0).unwrap_err().kind, "TypeError");
        assert_eq!(span(&[2.0, 1.0, 3.0]), (1.0, 3.0));
    }
}
