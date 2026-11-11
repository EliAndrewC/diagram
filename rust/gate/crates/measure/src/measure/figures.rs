//! `make figures`: re-run every recorded measurement and report what moved (feature 239 FR-011; feature 449 T75, from `figures.py`).
//!
//! For each distinct `command` in a feature's `measurements.json` the command is re-run once, the values it writes are compared with the
//! recorded ones, and the ORIGINAL file is restored: this reports, it never records. A moved COUNT fails; a TIMING outside its band is
//! reported and never fails, a timing being a property of the machine as well as the code. A command with a `<placeholder>`, one reaching
//! the deleted Python hamlet engine and one written as prose are listed as not re-measured and never run.

use std::collections::BTreeSet;
use std::fmt::Write as _;
use std::path::{Path, PathBuf};
use std::process::{Command, Stdio};
use std::sync::LazyLock;

use fancy_regex::Regex;
use serde_json::Value;

use super::reply;

const DEFAULT_BAND: f64 = 0.10;
static PLACEHOLDER: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"<[A-Za-z][^<>]*>").unwrap_or_else(|e| unreachable!("{e}")));
static DELETED_ENGINE: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(r"\bl7r[./]diagram[./](hamletgen|settlement|sitegen|waterfields|overlap|citybudget)\b|\btests/(hamletgen|settlement|sitegen|waterfields|overlap|citybudget)\b")
        .unwrap_or_else(|e| unreachable!("{e}"))
});

/// A value as Python's `str()` prints it.
fn py_str(v: &Value) -> String {
    match v {
        Value::String(s) => s.clone(),
        other => py_repr(other),
    }
}

fn py_repr(v: &Value) -> String {
    match v {
        Value::Null => "None".to_owned(),
        Value::Bool(true) => "True".to_owned(),
        Value::Bool(false) => "False".to_owned(),
        Value::Number(n) => n.to_string(),
        Value::String(s) => format!("'{s}'"),
        Value::Array(a) => format!("[{}]", a.iter().map(py_repr).collect::<Vec<_>>().join(", ")),
        Value::Object(o) => format!(
            "{{{}}}",
            o.iter()
                .map(|(k, x)| format!("'{k}': {}", py_repr(x)))
                .collect::<Vec<_>>()
                .join(", ")
        ),
    }
}

/// `float(v)`, as far as JSON's values reach it.
fn float(v: &Value) -> Option<f64> {
    match v {
        Value::Number(n) => n.as_f64(),
        Value::Bool(b) => Some(f64::from(u8::from(*b))),
        Value::String(s) => s.trim().parse().ok(),
        _ => None,
    }
}

/// Python's `==` over JSON: `1 == 1.0`.
fn equal(a: &Value, b: &Value) -> bool {
    match (a, b) {
        (Value::Number(x), Value::Number(y)) => x.as_f64() == y.as_f64(),
        _ => a == b,
    }
}

fn band(entry: &Value) -> f64 {
    if entry["varies"] == Value::Bool(true) {
        DEFAULT_BAND
    } else {
        entry["varies"].as_f64().unwrap_or(0.0)
    }
}

fn moved_by(old: &Value, new: &Value) -> f64 {
    let (Some(o), Some(n)) = (float(old), float(new)) else {
        return 1.0;
    };
    if o == 0.0 {
        1.0
    } else {
        (n - o).abs() / o.abs()
    }
}

/// (failures, reports) for the keys a re-run produced.
fn compare(recorded: &Value, fresh: &Value) -> (Vec<String>, Vec<String>) {
    let (mut failures, mut reports) = (Vec::new(), Vec::new());
    let mut keys: Vec<&String> = recorded
        .as_object()
        .map(|o| o.keys().collect())
        .unwrap_or_default();
    keys.sort();
    for key in keys {
        let Some(latest) = fresh.get(key) else {
            continue;
        };
        let (entry, old, new) = (&recorded[key], &recorded[key]["value"], &latest["value"]);
        if equal(old, new) {
            continue;
        }
        let varies = !entry["varies"].is_null()
            && entry["varies"] != Value::Bool(false)
            && entry["varies"] != 0;
        if varies {
            let limit = band(entry);
            if moved_by(old, new) > limit {
                let load = latest.get("load").map_or_else(|| "?".to_owned(), py_str);
                reports.push(format!("  REPORT `{key}`: {} -> {}, outside its band of {:.0}% (a timing - reported, never failed; load {load})", py_str(old), py_str(new), limit * 100.0));
            }
        } else {
            failures.push(format!(
                "  FAIL   `{key}`: {} -> {} - a count that moved means the thing counted changed",
                py_str(old),
                py_str(new)
            ));
        }
    }
    (failures, reports)
}

/// POSIX word splitting, as `shlex.split` does it; `None` for a quote left open.
fn shlex(text: &str) -> Option<Vec<String>> {
    let (mut words, mut word, mut began, mut quote, mut escape) =
        (Vec::new(), String::new(), false, None, false);
    for c in text.chars() {
        if escape {
            word.push(c);
            escape = false;
        } else if let Some(q) = quote {
            match (q, c) {
                (_, c) if c == q => quote = None,
                ('"', '\\') => escape = true,
                _ => word.push(c),
            }
        } else if c == '\'' || c == '"' {
            quote = Some(c);
            began = true;
        } else if c == '\\' {
            escape = true;
            began = true;
        } else if c.is_whitespace() {
            if began || !word.is_empty() {
                words.push(std::mem::take(&mut word));
                began = false;
            }
        } else {
            word.push(c);
        }
    }
    if quote.is_some() || escape {
        return None;
    }
    if began || !word.is_empty() {
        words.push(word);
    }
    Some(words)
}

fn cut(text: &str, n: usize) -> String {
    text.chars().take(n).collect()
}

fn not_measured(command: &str, why: &str) -> String {
    format!("  NOT RE-MEASURED: {}\n      {why}", cut(command, 120))
}

/// Why a command will not be run, if it will not.
fn refused(command: &str) -> Option<String> {
    if PLACEHOLDER.is_match(command).unwrap_or(false) {
        return Some(not_measured(
            command,
            "names a <placeholder> - a one-shot's description, not run",
        ));
    }
    DELETED_ENGINE.is_match(command).unwrap_or(false).then(|| {
        not_measured(
            command,
            "runs the deleted Python hamlet engine (feature 444) - a frozen figure, not run",
        )
    })
}

fn error_name(e: &std::io::Error) -> &'static str {
    match e.kind() {
        std::io::ErrorKind::NotFound => "FileNotFoundError",
        std::io::ErrorKind::PermissionDenied => "PermissionError",
        _ => "OSError",
    }
}

/// (failures, reports, not re-measured) for one command, its feature's file written fresh before and read after.
fn one(
    command: &str,
    root: &Path,
    path: &Path,
    original: &str,
    recorded: &Value,
) -> (Vec<String>, Vec<String>, Vec<String>) {
    let _ = std::fs::write(path, original);
    if let Some(why) = refused(command) {
        return (Vec::new(), Vec::new(), vec![why]);
    }
    let Some(words) = shlex(command).filter(|w| !w.is_empty()) else {
        return (
            Vec::new(),
            Vec::new(),
            vec![not_measured(command, "not a runnable command (ValueError)")],
        );
    };
    let done = Command::new(&words[0])
        .args(&words[1..])
        .current_dir(root)
        .stdin(Stdio::null())
        .output();
    let run = match done {
        Ok(run) => run,
        Err(e) => {
            return (
                Vec::new(),
                Vec::new(),
                vec![not_measured(
                    command,
                    &format!("not a runnable command ({})", error_name(&e)),
                )],
            )
        }
    };
    if !run.status.success() {
        let text = String::from_utf8_lossy(&run.stderr);
        let reason = text.trim().lines().last().map_or_else(
            || format!("exit {}", run.status.code().unwrap_or(-1)),
            |l| cut(l, 160),
        );
        return (
            Vec::new(),
            Vec::new(),
            vec![format!("  NOT RE-MEASURED: {command}\n      {reason}")],
        );
    }
    let fresh: Value = serde_json::from_str(&std::fs::read_to_string(path).unwrap_or_default())
        .unwrap_or_default();
    let (f, r) = compare(recorded, &fresh);
    (f, r, Vec::new())
}

/// One feature's commands, with its measurements file restored.
fn rerun(dir: &Path, root: &Path) -> (Vec<String>, Vec<String>, Vec<String>) {
    let path = dir.join("measurements.json");
    let original = std::fs::read_to_string(&path).unwrap_or_default();
    let recorded: Value = serde_json::from_str(&original).unwrap_or_default();
    let commands: BTreeSet<&str> = recorded
        .as_object()
        .into_iter()
        .flat_map(|o| o.values())
        .filter_map(|e| e["command"].as_str())
        .filter(|c| !c.is_empty())
        .collect();
    let (mut failures, mut reports, mut skipped) = (Vec::new(), Vec::new(), Vec::new());
    for command in commands {
        let (f, r, s) = one(command, root, &path, &original, &recorded);
        failures.extend(f);
        reports.extend(r);
        skipped.extend(s);
    }
    let _ = std::fs::write(&path, original); // reports, never records
    (failures, reports, skipped)
}

fn every_feature(root: &Path) -> Vec<PathBuf> {
    let mut dirs: Vec<PathBuf> = std::fs::read_dir(root.join("specs"))
        .into_iter()
        .flatten()
        .flatten()
        .map(|e| e.path())
        .filter(|p| p.join("measurements.json").is_file())
        .collect();
    dirs.sort();
    dirs
}

/// `l7r-gate measure figures [specs/NNN-slug ...]`.
#[must_use]
pub fn cli(args: &[String], root: &Path) -> crate::Reply {
    let named: Vec<PathBuf> = args
        .iter()
        .filter(|a| !a.starts_with('-'))
        .map(|a| {
            if Path::new(a).exists() {
                PathBuf::from(a)
            } else {
                root.join(a)
            }
        })
        .collect();
    let dirs = if named.is_empty() {
        every_feature(root)
    } else {
        named.clone()
    };
    let (mut out, mut err, mut code) = (String::new(), String::new(), 0);
    for dir in dirs {
        if !dir.join("measurements.json").is_file() {
            let _ = writeln!(
                err,
                "figures: {} has no measurements.json - nothing was re-run",
                dir.display()
            );
            code = 1;
            continue;
        }
        let (failures, reports, skipped) = rerun(&dir, root);
        let _ = writeln!(
            out,
            "{}: {} moved count(s), {} timing(s) outside their band, {} command(s) not re-measured",
            dir.file_name().unwrap_or_default().to_string_lossy(),
            failures.len(),
            reports.len(),
            skipped.len()
        );
        code |= i32::from(!failures.is_empty());
        for line in failures.iter().chain(&reports).chain(&skipped) {
            let _ = writeln!(out, "{line}");
        }
    }
    reply(out, err, code)
}

#[cfg(test)]
mod tests;
