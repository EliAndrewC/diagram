//! What the ported Python said when it failed (feature 449 T168): an exception it did not catch ended the run with a traceback whose last
//! line is `<class>: <message>` and exit 1, so the port prints that line and exits 1 - the frames above it name Python files that no
//! longer exist. The differential (FR-002) compares the line byte for byte, the frames stripped.
//!
//! Research:
//!     the ported Python's failures - NONE: how an error is printed, deciding nothing about a building

use l7r_gate_research::Error;
use serde_json::Value;

/// The last line of the traceback `err` would have ended a Python run with: a `KeyError`'s message is its key's `repr`.
#[must_use]
pub fn uncaught(err: &Error) -> String {
    let message = if err.kind == "KeyError" {
        l7r_guard::shared::py_text::repr(&err.message)
    } else {
        err.message.clone()
    };
    if message.is_empty() {
        format!("{}\n", err.kind)
    } else {
        format!("{}: {message}\n", err.kind)
    }
}

/// The `OSError` subclass and message Python's `open(path)` raised for `err`: `[Errno N] <strerror>: '<path>'`.
#[must_use]
pub fn os_error(err: &std::io::Error, path: &str) -> Error {
    if err.kind() == std::io::ErrorKind::InvalidData {
        // `l7r_gate_core::record::read_text`'s word for bytes that are not UTF-8; the codec's own words name a byte and a position the
        // differential normalizes as the library's
        return Error::new(
            "UnicodeDecodeError",
            "'utf-8' codec can't decode the file: invalid utf-8",
        );
    }
    let code = err.raw_os_error().unwrap_or(0);
    let kind = match code {
        2 => "FileNotFoundError",
        13 | 1 => "PermissionError",
        20 => "NotADirectoryError",
        21 => "IsADirectoryError",
        _ => "OSError",
    };
    let text = err.to_string();
    let strerror = text.split(" (os error").next().unwrap_or(&text);
    Error::new(
        kind,
        format!(
            "[Errno {code}] {strerror}: {}",
            l7r_guard::shared::py_text::repr(path)
        ),
    )
}

/// Python's type name of what `json.load` made of `value`, for a `TypeError` or `AttributeError`.
#[must_use]
pub fn type_name(value: &Value) -> &'static str {
    match value {
        Value::Null => "NoneType",
        Value::Bool(_) => "bool",
        Value::Number(n) if n.is_f64() => "float",
        Value::Number(_) => "int",
        Value::String(_) => "str",
        Value::Array(_) => "list",
        Value::Object(_) => "dict",
    }
}

/// What a Python `for x in value` walks: a list's items, a string's characters, a dict's keys; anything else is the `TypeError`.
///
/// # Errors
/// `value` is `None`, a bool or a number.
pub fn iterate(value: &Value) -> Result<Vec<Value>, Error> {
    match value {
        Value::Array(items) => Ok(items.clone()),
        Value::String(s) => Ok(s.chars().map(|c| Value::from(c.to_string())).collect()),
        Value::Object(map) => Ok(map.keys().map(|k| Value::from(k.as_str())).collect()),
        other => Err(Error::new(
            "TypeError",
            format!("'{}' object is not iterable", type_name(other)),
        )),
    }
}

#[cfg(test)]
mod tests {
    use super::{iterate, os_error, type_name, uncaught};
    use l7r_gate_research::Error;
    use serde_json::json;

    #[test]
    fn an_uncaught_error_is_its_traceback_s_last_line() {
        assert_eq!(uncaught(&Error::new("ValueError", "x")), "ValueError: x\n");
        assert_eq!(uncaught(&Error::new("KeyError", "k")), "KeyError: 'k'\n");
        assert_eq!(uncaught(&Error::new("ValueError", "")), "ValueError\n");
    }

    #[test]
    fn an_open_that_fails_is_python_s_os_error() {
        let e = |code| std::io::Error::from_raw_os_error(code);
        assert_eq!(
            uncaught(&os_error(&e(2), "/x")),
            "FileNotFoundError: [Errno 2] No such file or directory: '/x'\n"
        );
        assert_eq!(os_error(&e(13), "a").kind, "PermissionError");
        assert_eq!(os_error(&e(1), "a").kind, "PermissionError");
        assert_eq!(os_error(&e(20), "a").kind, "NotADirectoryError");
        assert_eq!(os_error(&e(21), "a").kind, "IsADirectoryError");
        assert_eq!(os_error(&e(5), "a").kind, "OSError");
        let bad = std::io::Error::from(std::io::ErrorKind::InvalidData);
        assert_eq!(os_error(&bad, "a").kind, "UnicodeDecodeError");
    }

    #[test]
    fn a_value_iterates_and_is_named_as_python_s() {
        assert_eq!(iterate(&json!("ab")).unwrap(), vec![json!("a"), json!("b")]);
        assert_eq!(iterate(&json!({"k": 1})).unwrap(), vec![json!("k")]);
        assert_eq!(iterate(&json!([1])).unwrap(), vec![json!(1)]);
        assert_eq!(
            iterate(&json!(null)).unwrap_err().message,
            "'NoneType' object is not iterable"
        );
        let names: Vec<&str> = [json!(true), json!(1), json!(1.5), json!("s"), json!({})]
            .iter()
            .map(type_name)
            .collect();
        assert_eq!(names, ["bool", "int", "float", "str", "dict"]);
    }
}
