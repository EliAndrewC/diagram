//! How long the model takes per turn, against the context it reads (feature 375 amendment 7, FR-034, `research.md` R5; feature 449 T120,
//! from `turn_time.py`, under `ask:449-T83-scope`).
//!
//! A TURN is an assistant reply that follows a tool result: its time is from the tool result to the reply. Each turn's context is the
//! input tokens it read (cached, cache-written and fresh) and its output tokens are what it wrote. A least-squares fit of time on context
//! and output says how much of the model time the context's size explains. The step-back bundle's model time is the sum of these turns
//! (`stepback_bundle.rs`); `l7r-gate measure turn-time` is the Python's own command, kept so no command vanishes unannounced (T119's
//! precedent).

use std::path::Path;

use l7r_gate_core::record::args::{parse_with, Spec};
use l7r_guard::shared::pyjson::dumps;
use l7r_guard::shared::speckit::splitlines;
use serde_json::{json, Map, Value};

use super::events::{cmp_f, py_int, read_text, truthy, ts, Raised};
use super::reply;
use crate::Reply;

/// (context tokens, seconds, output tokens).
pub type Turn = (i128, f64, i128);

/// A gap at or past this is no turn (`turns`' `ceiling`).
const CEILING: f64 = 1200.0;

/// `_ts(value)`: a time that is no text is the Python's `AttributeError` (`.replace` on it).
///
/// # Errors
///
/// The value is no text, or no time `fromisoformat` reads.
pub fn ts_of(value: &Value) -> Result<f64, Raised> {
    match value {
        Value::String(t) => ts(t),
        _ => Err("AttributeError: a timestamp that is no text".to_owned()),
    }
}

/// `(value or {})` read as a mapping: a truthy value that is no object is the Python's `AttributeError` on `.get`.
///
/// # Errors
///
/// A truthy value that is no object.
pub fn or_map(value: Option<&Value>) -> Result<Option<&Map<String, Value>>, Raised> {
    match value {
        Some(v) if truthy(v) => v
            .as_object()
            .map(Some)
            .ok_or_else(|| "AttributeError: a value that is no object has no .get".to_owned()),
        _ => Ok(None),
    }
}

/// `int(value or 0)`.
fn py_int_or_zero(value: Option<&Value>) -> Result<i128, Raised> {
    match value {
        Some(v) if truthy(v) => match v {
            Value::Bool(_) => Ok(1),
            Value::Number(n) => n
                .as_i64()
                .map(i128::from)
                .or_else(|| n.as_u64().map(i128::from))
                .map_or_else(
                    || {
                        let f = n.as_f64().unwrap_or(0.0);
                        #[expect(
                            clippy::cast_possible_truncation,
                            reason = "int() truncates a float toward zero"
                        )]
                        let whole = f.trunc() as i128;
                        Ok(whole)
                    },
                    Ok,
                ),
            Value::String(s) => py_int(s),
            _ => Err("TypeError: int() argument must be a string or a real number".to_owned()),
        },
        _ => Ok(0),
    }
}

/// (context tokens, seconds, output tokens) per turn of the main session (no sidechain), one per request.
///
/// # Errors
///
/// A record that is no object, a time that is not one, a message or usage that is no object, or a token count `int()` refuses: the
/// Python's raise.
pub fn turns(records: &[Value]) -> Result<Vec<Turn>, Raised> {
    let mut prev: Option<f64> = None;
    let mut seen: std::collections::HashSet<String> = std::collections::HashSet::new();
    let mut out = Vec::new();
    for d in records {
        let Value::Object(d) = d else {
            return Err("AttributeError: a transcript line that is no object".to_owned());
        };
        if d.get("isSidechain").is_some_and(truthy) {
            continue;
        }
        let Some(stamp) = d.get("timestamp") else {
            continue;
        };
        let t = ts_of(stamp)?;
        let m = or_map(d.get("message"))?;
        let content = m.and_then(|m| m.get("content"));
        let kind = d.get("type").and_then(Value::as_str);
        if kind == Some("user") {
            if let Some(Value::Array(blocks)) = content {
                if blocks
                    .iter()
                    .any(|b| b.get("type").and_then(Value::as_str) == Some("tool_result"))
                {
                    prev = Some(t);
                }
            }
            continue;
        }
        let Some(before) = prev.filter(|_| kind == Some("assistant")) else {
            continue;
        };
        let rid = [d.get("requestId"), m.and_then(|m| m.get("id"))]
            .into_iter()
            .flatten()
            .find(|v| truthy(v))
            .map_or_else(String::new, super::events::py_str);
        if !seen.insert(rid) {
            continue;
        }
        let u = or_map(m.and_then(|m| m.get("usage")))?;
        let field = |k: &str| u.and_then(|u| u.get(k));
        let ctx = py_int_or_zero(field("cache_read_input_tokens"))?
            + py_int_or_zero(field("cache_creation_input_tokens"))?
            + py_int_or_zero(field("input_tokens"))?;
        let gap = t - before;
        if 0.0 < gap && gap < CEILING && ctx > 0 {
            out.push((ctx, gap, py_int_or_zero(field("output_tokens"))?));
        }
        prev = None;
    }
    Ok(out)
}

/// `round(x, n)`: the exact binary value rounded half to even at `n` places, as Python's `round` and Rust's fixed formatting both do.
#[must_use]
pub fn py_round(x: f64, n: usize) -> f64 {
    format!("{x:.n$}").parse().unwrap_or(x)
}

#[expect(
    clippy::cast_precision_loss,
    reason = "a token count as Python's int / float converts it"
)]
fn as_f(n: i128) -> f64 {
    n as f64
}

/// `seconds = a + b * (context / 100k) + c * (output / 1k)`, least squares by the normal equations, Gauss-Jordan with partial pivoting
/// in the Python's order of operations, so each coefficient is its float.
#[must_use]
pub fn fit(points: &[Turn]) -> [f64; 3] {
    let rows: Vec<[f64; 4]> = points
        .iter()
        .map(|p| [1.0, as_f(p.0) / 1e5, as_f(p.2) / 1e3, p.1])
        .collect();
    let mut ata = [[0.0f64; 3]; 3];
    let mut rhs = [0.0f64; 3];
    for i in 0..3 {
        for j in 0..3 {
            ata[i][j] = rows.iter().fold(0.0, |s, r| s + r[i] * r[j]);
        }
        rhs[i] = rows.iter().fold(0.0, |s, r| s + r[i] * r[3]);
    }
    for col in 0..3 {
        // `max(range(col, n), key=...)`: the FIRST row of the largest magnitude
        let mut piv = col;
        for i in col + 1..3 {
            if ata[i][col].abs() > ata[piv][col].abs() {
                piv = i;
            }
        }
        ata.swap(col, piv);
        rhs.swap(col, piv);
        for i in 0..3 {
            if i != col && ata[col][col] != 0.0 {
                let f = ata[i][col] / ata[col][col];
                let pivot_row = ata[col];
                for (a, b) in ata[i].iter_mut().zip(pivot_row) {
                    *a -= f * b;
                }
                rhs[i] -= f * rhs[col];
            }
        }
    }
    [0, 1, 2].map(|i| {
        let x = if ata[i][i] == 0.0 {
            0.0
        } else {
            rhs[i] / ata[i][i]
        };
        py_round(x, 2)
    })
}

/// `statistics.median`.
fn median(mut values: Vec<f64>) -> f64 {
    values.sort_by(|a, b| cmp_f(*a, *b));
    let n = values.len();
    if n % 2 == 1 {
        values[n / 2]
    } else {
        #[expect(
            clippy::manual_midpoint,
            reason = "statistics.median's own (a + b) / 2, its float to the bit"
        )]
        let mid = (values[n / 2 - 1] + values[n / 2]) / 2.0;
        mid
    }
}

/// The summary `turn_time.summary` printed: its keys in the Python's order.
#[must_use]
pub fn summary(points: &[Turn]) -> Value {
    let [a, b, c] = fit(points);
    let total = points.iter().fold(0.0, |s, p| s + p.1);
    let explained = points.iter().fold(0.0, |s, p| s + b * as_f(p.0) / 1e5);
    let mut bands = Map::new();
    for lo in (0..1000).step_by(200) {
        let inside =
            |p: &&Turn| f64::from(lo) * 1e3 <= as_f(p.0) && as_f(p.0) < f64::from(lo + 200) * 1e3;
        let band: Vec<f64> = points.iter().filter(inside).map(|p| p.1).collect();
        if !band.is_empty() {
            bands.insert(
                format!("{lo}-{}k", lo + 200),
                json!(py_round(median(band), 1)),
            );
        }
    }
    json!({
        "turns": points.len(),
        "model hours": py_round(total / 3600.0, 2),
        "median turn s": py_round(median(points.iter().map(|p| p.1).collect()), 1),
        "fit: s fixed, per 100k context, per 1k output": [a, b, c],
        "hours explained by context size": py_round(explained / 3600.0, 2),
        "median turn s by context (200k bands)": bands,
    })
}

/// `l7r-gate measure turn-time <transcript> [--record <measurements.json> --key <key>]`.
#[must_use]
pub fn cli(args: &[String]) -> Reply {
    let specs = [Spec::value("--record"), Spec::value("--key")];
    let p = match parse_with(args, &specs, 1) {
        Ok(p) if !p.positional.is_empty() => p,
        Ok(_) => return usage("the following arguments are required: transcript"),
        Err(why) => return usage(&why),
    };
    match run(
        Path::new(&p.positional[0]),
        p.text("--record", ""),
        p.text("--key", ""),
    ) {
        Ok(Ok(text)) => reply(text, String::new(), 0),
        Ok(Err(refusal)) => reply(String::new(), refusal, 2),
        Err(why) => reply(
            String::new(),
            format!("Traceback (most recent call last):\n  l7r-gate measure turn-time\n{why}\n"),
            1,
        ),
    }
}

fn usage(why: &str) -> Reply {
    reply(
        String::new(),
        format!("usage: l7r-gate measure turn-time [--record RECORD] [--key KEY] transcript\nl7r-gate measure turn-time: error: {why}\n"),
        2,
    )
}

/// `main` after its arguments: the summary's text, or a refusal (exit 2).
fn run(transcript: &Path, record: &str, key: &str) -> Result<Result<String, String>, Raised> {
    let text = read_text(transcript)?;
    let lines: Vec<Value> = splitlines(&text)
        .into_iter()
        .filter_map(|l| serde_json::from_str(l).ok())
        .collect();
    let points = turns(&lines)?;
    if points.is_empty() {
        return Ok(Err("turn_time: no turns found\n".to_owned()));
    }
    let s = summary(&points);
    if !record.is_empty() {
        if key.is_empty() {
            return Ok(Err("turn_time: --record needs --key\n".to_owned()));
        }
        let path = Path::new(record);
        let mut data: Value =
            serde_json::from_str(&read_text(path)?).map_err(|e| format!("JSONDecodeError: {e}"))?;
        let Value::Object(top) = &mut data else {
            return Err("AttributeError: the record is no object".to_owned());
        };
        let Value::Object(entry) = top.entry(key.to_owned()).or_insert_with(|| json!({})) else {
            return Err("TypeError: the record's entry is no object".to_owned());
        };
        entry.insert("value".to_owned(), s.clone());
        std::fs::write(path, dumps(&data, Some(1), false) + "\n")
            .map_err(|e| format!("OSError: {}: {e}", path.display()))?;
    }
    Ok(Ok(dumps(&s, Some(1), true) + "\n"))
}

#[cfg(test)]
mod tests;
