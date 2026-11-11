//! What the cohort's readers share with the rest of the gate (feature 449 T068, from `cohort.rs`, split out by T92): git's answer, and a
//! record's value read as the Python read it.

use std::path::Path;
use std::process::Command;

use serde_json::Value;

/// `git <args>`: whether it succeeded, and its stdout.
#[must_use]
pub fn git(root: &Path, args: &[&str]) -> (bool, String) {
    let done = Command::new("git").arg("-C").arg(root).args(args).output();
    done.map_or((false, String::new()), |o| {
        (
            o.status.success(),
            String::from_utf8_lossy(&o.stdout).into_owned(),
        )
    })
}

/// `int(v)`: a number, or a numeric string, else 0.
#[must_use]
pub fn int(v: &Value) -> i64 {
    v.as_i64()
        .or_else(|| v.as_str().and_then(|s| s.parse().ok()))
        .unwrap_or(0)
}

/// `str(rec.get(key))`: the record's value as text, `None` when absent, because a record's `utc` is compared as text.
#[must_use]
pub fn text(rec: &Value, key: &str) -> String {
    match rec.get(key) {
        None | Some(Value::Null) => "None".to_owned(),
        Some(Value::String(s)) => s.clone(),
        Some(other) => other.to_string(),
    }
}

/// Python's truth of a JSON value.
#[must_use]
pub fn truthy(v: &Value) -> bool {
    match v {
        Value::Null => false,
        Value::Bool(b) => *b,
        Value::Number(n) => n.as_f64() != Some(0.0),
        Value::String(s) => !s.is_empty(),
        Value::Array(a) => !a.is_empty(),
        Value::Object(o) => !o.is_empty(),
    }
}

#[expect(
    clippy::cast_precision_loss,
    reason = "seed counts, far inside f64's exact range"
)]
#[must_use]
pub fn percent(part: usize, whole: usize) -> f64 {
    100.0 * part as f64 / whole.max(1) as f64
}

#[cfg(test)]
mod tests;
