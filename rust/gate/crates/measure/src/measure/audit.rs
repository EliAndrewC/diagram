//! `l7r-gate measure audit runs|guards|claims` - three of `make audit`'s four sections: the gate runs and the bypasses (`dev/run-log/`,
//! `dev/bypass-log/`), the guard firings (`~/.claude/guard-log/`), and the feature numbers claimed (`.specify/feature-numbers.jsonl` of
//! main's mirror). Ported from the Makefile's inline `python3 -c` recipes by feature 449 T121: `ask:449-T83-scope` places T83's three
//! `make audit` recipes, the three that do not read `CLASSES`, each with the slice whose module it calls or with T121 when it calls none,
//! and none calls one. The fourth, the class entries with no research section, reads the registry and stays a phase-4 remainder.
//!
//! Each prints what its one-liner printed, ANSI bold and all, and fails where it raised: a record that is no JSON, one missing a field
//! the line reads, a value Python cannot format - exit 1, what was printed before kept, a `Traceback` line and the reason after.

use std::fmt::Write as _;
use std::path::{Path, PathBuf};

use l7r_guard::shared::pyjson::{py_float, py_str};
use serde_json::Value;

use crate::Reply;

const BOLD: &str = "\x1b[1m";
const PLAIN: &str = "\x1b[0m";

/// What the section printed before it raised, if it did.
struct Out {
    text: String,
}

impl Out {
    fn line(&mut self, text: &str) {
        self.text.push_str(text);
        self.text.push('\n');
    }
}

/// `str()` of a value, as an f-string's `{v}` prints it.
fn s(v: &Value) -> String {
    py_str(v)
}

/// `format(v, "<width" | ">width")`: a string, an int (a bool as its int) or a float padded; Python's `TypeError` for anything else.
fn pad(v: &Value, left: bool, width: usize) -> Result<String, String> {
    let text = match v {
        Value::String(t) => t.clone(),
        Value::Bool(b) => u8::from(*b).to_string(),
        Value::Number(n) if n.is_f64() => py_float(n.as_f64().unwrap_or(0.0)),
        Value::Number(n) => n.to_string(),
        other => {
            return Err(format!(
                "TypeError: unsupported format string passed to {}.__format__",
                type_name(other)
            ))
        }
    };
    let fill = width.saturating_sub(text.chars().count());
    Ok(if left {
        format!("{text}{}", " ".repeat(fill))
    } else {
        format!("{}{text}", " ".repeat(fill))
    })
}

fn type_name(v: &Value) -> &'static str {
    match v {
        Value::Null => "NoneType",
        Value::Array(_) => "list",
        Value::Object(_) => "dict",
        Value::Bool(_) => "bool",
        Value::Number(n) if n.is_f64() => "float",
        Value::Number(_) => "int",
        Value::String(_) => "str",
    }
}

/// Python's truth of a value.
fn truthy(v: &Value) -> bool {
    match v {
        Value::Null => false,
        Value::Bool(b) => *b,
        Value::Number(n) => n.as_f64().is_some_and(|f| f != 0.0),
        Value::String(t) => !t.is_empty(),
        Value::Array(a) => !a.is_empty(),
        Value::Object(o) => !o.is_empty(),
    }
}

/// `r[key]` of a record, Python's `KeyError` (or `TypeError` for a record that is no object) where it fails.
fn field<'a>(r: &'a Value, key: &str) -> Result<&'a Value, String> {
    match r {
        Value::Object(m) => m.get(key).ok_or_else(|| format!("KeyError: '{key}'")),
        other => Err(format!(
            "TypeError: {} indices must be integers or slices, not str",
            type_name(other)
        )),
    }
}

/// `r.get(key, default)`, Python's `AttributeError` for a record that is no object.
fn get<'a>(r: &'a Value, key: &str) -> Result<Option<&'a Value>, String> {
    match r {
        Value::Object(m) => Ok(m.get(key)),
        other => Err(format!(
            "AttributeError: '{}' object has no attribute 'get'",
            type_name(other)
        )),
    }
}

/// `x[a:b]` of a string, Python's `TypeError` for a value that cannot be sliced so.
fn slice(v: &Value, from: usize, to: usize) -> Result<String, String> {
    match v {
        Value::String(t) => Ok(t.chars().skip(from).take(to.saturating_sub(from)).collect()),
        other => Err(format!(
            "TypeError: '{}' object is not subscriptable",
            type_name(other)
        )),
    }
}

/// `sorted(items, key=..., reverse=...)` over JSON keys as Python compares them: strings among strings, numbers (a bool its int) among
/// numbers, stable both ways; a mix, or keys of another type, Python's `TypeError` - and only where a comparison is made, so one item
/// sorts whatever its key.
fn py_sorted<T>(items: Vec<(Value, T)>, reverse: bool) -> Result<Vec<T>, String> {
    comparable(&items.iter().map(|(k, _)| k).collect::<Vec<_>>())?;
    let mut items = items;
    items.sort_by(|a, b| {
        let order = py_cmp(&a.0, &b.0);
        if reverse {
            order.reverse()
        } else {
            order
        }
    });
    Ok(items.into_iter().map(|(_, t)| t).collect())
}

/// Python's `TypeError` where two of `keys` would be compared and cannot be: a mix of strings and numbers, or a type with no order.
fn comparable(keys: &[&Value]) -> Result<(), String> {
    if keys.len() < 2 {
        return Ok(());
    }
    let strs = keys.iter().all(|k| k.is_string());
    let nums = keys.iter().all(|k| k.is_number() || k.is_boolean());
    if strs || nums {
        return Ok(());
    }
    let kinds: Vec<&str> = keys.iter().map(|k| type_name(k)).collect();
    let other = kinds.iter().find(|k| **k != kinds[0]).unwrap_or(&kinds[0]);
    Err(format!(
        "TypeError: '<' not supported between instances of '{}' and '{other}'",
        kinds[0]
    ))
}

/// Two keys of one kind compared: strings by code point, numbers by value.
fn py_cmp(a: &Value, b: &Value) -> std::cmp::Ordering {
    let num = |v: &Value| {
        v.as_f64()
            .unwrap_or_else(|| f64::from(u8::from(v.as_bool() == Some(true))))
    };
    match (a, b) {
        (Value::String(x), Value::String(y)) => x.cmp(y),
        _ => num(a).total_cmp(&num(b)),
    }
}

/// `sorted(records, key=lambda r: r.get('utc', ''))`.
fn by_utc(rows: Vec<Value>) -> Result<Vec<Value>, String> {
    let mut keyed = Vec::new();
    for r in rows {
        let key = get(&r, "utc")?
            .cloned()
            .unwrap_or(Value::String(String::new()));
        keyed.push((key, r));
    }
    py_sorted(keyed, false)
}

/// What a raise said of a file it could not open.
fn io<E: std::fmt::Display>(e: E) -> String {
    e.to_string()
}

/// `json.load(open(f))` of each file.
fn load(files: &[PathBuf]) -> Result<Vec<Value>, String> {
    files
        .iter()
        .map(|f| {
            let bytes = std::fs::read(f).map_err(io)?;
            let text = String::from_utf8(bytes)
                .map_err(|e| format!("UnicodeDecodeError: {}: {e}", f.display()))?;
            serde_json::from_str(&text).map_err(|e| format!("json.decoder.JSONDecodeError: {e}"))
        })
        .collect()
}

/// A directory's names as `os.scandir` lists them, the hidden ones dropped as `glob` drops them.
fn names(dir: &Path) -> Vec<(String, PathBuf, bool)> {
    std::fs::read_dir(dir)
        .into_iter()
        .flatten()
        .flatten()
        .filter_map(|e| {
            let name = e.file_name().to_string_lossy().into_owned();
            (!name.starts_with('.')).then(|| {
                let path = e.path();
                let is_dir = path.is_dir();
                (name, path, is_dir)
            })
        })
        .collect()
}

#[expect(
    clippy::case_sensitive_file_extension_comparisons,
    reason = "glob's `*.json`, case and all"
)]
/// `glob.glob('<dir>/**/*.json', recursive=True)`: the directory itself, then each below it in preorder, each one's `*.json` files in
/// the order the directory lists them.
fn json_under(dir: &Path) -> Vec<PathBuf> {
    fn dirs(dir: &Path, out: &mut Vec<PathBuf>) {
        out.push(dir.to_path_buf());
        for (_, path, is_dir) in names(dir) {
            if is_dir {
                dirs(&path, out);
            }
        }
    }
    let mut all = Vec::new();
    if !dir.is_dir() {
        return all;
    }
    dirs(dir, &mut all);
    all.iter()
        .flat_map(|d| names(d))
        .filter(|(name, _, is_dir)| name.ends_with(".json") && !is_dir)
        .map(|(_, path, _)| path)
        .collect()
}

/// The gate runs and the bypasses.
fn runs(cwd: &Path, out: &mut Out) -> Result<(), String> {
    let rows = by_utc(load(&json_under(&cwd.join("dev/run-log")))?)?;
    out.line(&format!("\n{BOLD}Gate runs{PLAIN} (dev/run-log/)"));
    let last = &rows[rows.len().saturating_sub(25)..];
    for r in last {
        let mode = match get(r, "mode")? {
            None => String::new(),
            Some(Value::String(m)) => m.clone(),
            Some(other) => {
                return Err(format!(
                    "TypeError: unsupported operand type(s) for +: '{}' and 'str'",
                    type_name(other)
                ))
            }
        };
        let selected = get(r, "selected")?.map_or_else(String::new, s);
        let tail = format!("{mode} {selected}");
        out.line(&format!(
            "  {}  {} {}s  {} {}  {}",
            s(field(r, "utc")?),
            pad(field(r, "scope")?, true, 9)?,
            pad(field(r, "seconds")?, false, 4)?,
            pad(field(r, "result")?, true, 22)?,
            s(field(r, "commit")?),
            l7r_guard::shared::py_text::strip(&tail)
        ));
    }
    if last.is_empty() {
        out.line("  (none yet)");
    }
    let mut count = Counter::default();
    for r in &rows {
        count.add(field(r, "scope")?.clone());
    }
    if !rows.is_empty() {
        let parts: Vec<String> = count
            .sorted()?
            .iter()
            .map(|(k, v)| format!("{}={v}", s(k)))
            .collect();
        out.line(&format!("  {} runs: {}", rows.len(), parts.join(", ")));
    }
    let bypasses = by_utc(load(&json_under(&cwd.join("dev/bypass-log")))?)?;
    out.line(&format!(
        "\n{BOLD}Bypasses{PLAIN} (dev/bypass-log/) - a FULL run is only justified at the END of a feature"
    ));
    let last = &bypasses[bypasses.len().saturating_sub(15)..];
    for r in last {
        let first = |keys: &[&str], default: &str| -> Result<Value, String> {
            for k in keys {
                if let Some(v) = get(r, k)? {
                    if truthy(v) {
                        return Ok(v.clone());
                    }
                }
            }
            Ok(Value::String(default.to_owned()))
        };
        out.line(&format!(
            "  {}  {} {}",
            s(field(r, "utc")?),
            pad(&first(&["outcome", "guard"], "?")?, true, 10)?,
            slice(&first(&["why", "reason", "what"], "")?, 0, 76)?
        ));
    }
    if last.is_empty() {
        out.line("  (none yet)");
    }
    out.line("");
    Ok(())
}

/// A counter that keeps the order its keys were first counted in (`collections.Counter`).
#[derive(Default)]
struct Counter {
    keys: Vec<Value>,
    n: Vec<usize>,
}

impl Counter {
    fn add(&mut self, key: Value) {
        if let Some(i) = self.keys.iter().position(|k| *k == key) {
            self.n[i] += 1;
        } else {
            self.keys.push(key);
            self.n.push(1);
        }
    }

    fn get(&self, key: &str) -> usize {
        self.keys
            .iter()
            .position(|k| k == key)
            .map_or(0, |i| self.n[i])
    }

    fn items(&self) -> Vec<(Value, usize)> {
        self.keys
            .iter()
            .cloned()
            .zip(self.n.iter().copied())
            .collect()
    }

    /// `sorted(c.items())`: by key, Python's `TypeError` where the keys cannot be compared.
    fn sorted(&self) -> Result<Vec<(Value, usize)>, String> {
        py_sorted(
            self.items()
                .into_iter()
                .map(|(k, n)| (k.clone(), (k, n)))
                .collect(),
            false,
        )
    }

    /// `most_common(n)`: by count, ties in the order first counted.
    fn most_common(&self, n: usize) -> Vec<(Value, usize)> {
        let mut out = self.items();
        out.sort_by(|a, b| b.1.cmp(&a.1));
        out.truncate(n);
        out
    }
}

/// The counter of `key` in a `defaultdict(Counter)`, made on first use.
fn counter_of(by: &mut Vec<(Value, Counter)>, key: Value) -> &mut Counter {
    let at = by.iter().position(|(k, _)| *k == key).unwrap_or_else(|| {
        by.push((key, Counter::default()));
        by.len() - 1
    });
    &mut by[at].1
}

/// `f"{x:.0%}"`.
fn percent(x: f64) -> String {
    format!("{:.0}%", x * 100.0)
}

/// `glob('<dir>/*.json')` less the empty files (`if os.path.getsize(f)`).
#[expect(
    clippy::case_sensitive_file_extension_comparisons,
    reason = "glob's `*.json`, case and all"
)]
fn guard_files(dir: &Path) -> Vec<PathBuf> {
    names(dir)
        .into_iter()
        .filter(|(name, path, is_dir)| {
            name.ends_with(".json") && !is_dir && std::fs::metadata(path).is_ok_and(|m| m.len() > 0)
        })
        .map(|(_, path, _)| path)
        .collect()
}

/// The guard firings.
fn guards(dir: &Path, out: &mut Out) -> Result<(), String> {
    let rows = load(&guard_files(dir))?;
    out.line(&format!("{BOLD}Guard firings{PLAIN} (~/.claude/guard-log/) - what each guard did: blocked, rewrote, reminded, escaped"));
    // `defaultdict(Counter)` by guard, in the order first met; `sorted(by.items())` compares the guards
    let mut by: Vec<(Value, Counter)> = Vec::new();
    for r in &rows {
        let g = field(r, "guard")?.clone();
        let event = field(r, "event")?.clone();
        counter_of(&mut by, g).add(event);
    }
    let mut rules: Vec<(Value, Counter)> = Vec::new();
    for r in &rows {
        let rule = match get(r, "rule")? {
            Some(v) if truthy(v) => v.clone(),
            _ => field(r, "event")?.clone(),
        };
        counter_of(&mut rules, field(r, "guard")?.clone()).add(rule);
    }
    let empty = by.is_empty();
    let sorted = py_sorted(
        by.into_iter().map(|(g, c)| (g.clone(), (g, c))).collect(),
        false,
    )?;
    for (g, c) in &sorted {
        let parts: Vec<String> = c
            .sorted()?
            .iter()
            .map(|(k, v)| format!("{}={v}", s(k)))
            .collect();
        let (blocked, escaped) = (c.get("blocked"), c.get("escaped"));
        let rate = if blocked > 0 || escaped > 0 {
            #[expect(
                clippy::cast_precision_loss,
                reason = "Python's true division of two counts"
            )]
            let r = escaped as f64 / (escaped + blocked).max(1) as f64;
            format!("   escape rate {}", percent(r))
        } else {
            String::new()
        };
        out.line(&format!(
            "  {} {}{rate}",
            pad(g, true, 12)?,
            parts.join(", ")
        ));
        let rule = counter_of(&mut rules, g.clone());
        if rule.keys.len() > 1 && rule.keys.iter().any(|k| !c.keys.contains(k)) {
            let parts: Vec<String> = rule
                .most_common(4)
                .iter()
                .map(|(k, v)| format!("{}={v}", s(k)))
                .collect();
            out.line(&format!("               by rule: {}", parts.join(", ")));
        }
    }
    if empty {
        out.line("  (none recorded yet)");
    }
    let mut esc: Vec<(Value, &Value)> = Vec::new();
    for r in &rows {
        if field(r, "event")? == "escaped" {
            esc.push((Value::Null, r));
        }
    }
    if !esc.is_empty() {
        out.line(&format!(
            "{BOLD}  escapes taken, with what the session said{PLAIN}"
        ));
        for item in &mut esc {
            item.0 = field(item.1, "utc")?.clone();
        }
        // `sorted(..., reverse=True)` keeps equal keys in their order
        for r in py_sorted(esc, true)?.into_iter().take(8) {
            let detail = field(r, "detail")?;
            let detail = if truthy(detail) {
                detail.clone()
            } else {
                Value::String("(no reason recorded)".to_owned())
            };
            out.line(&format!(
                "    {}  {} {}",
                slice(field(r, "utc")?, 5, 16)?,
                pad(field(r, "guard")?, true, 12)?,
                slice(&detail, 0, 88)?
            ));
        }
    }
    let span = if rows.is_empty() {
        String::new()
    } else {
        // `min()` and `max()` of the times: the first and the last of them sorted, a stable sort's ends
        let mut utcs = Vec::new();
        for r in &rows {
            let u = field(r, "utc")?.clone();
            utcs.push((u.clone(), u));
        }
        let ordered = py_sorted(utcs, false)?;
        format!(", {} to {}", s(&ordered[0]), s(&ordered[ordered.len() - 1]))
    };
    out.line(&format!("  {} entries{span}", rows.len()));
    out.line("");
    Ok(())
}

/// The feature numbers claimed, from main's mirror (a clone's grandparent).
fn claims(cwd: &Path, out: &mut Out) -> Result<(), String> {
    let top = std::process::Command::new("git")
        .args(["rev-parse", "--show-toplevel"])
        .current_dir(cwd)
        .output()
        .map(|o| String::from_utf8_lossy(&o.stdout).trim().to_owned())
        .unwrap_or_default();
    // outside a repository git says nothing: `Path("")`, which pathlib reads as `.` and joins to a relative path
    let root = PathBuf::from(&top);
    let mirror = match root.parent() {
        Some(p) if p.file_name().is_some_and(|n| n == ".clones") => {
            p.parent().map_or(root.clone(), Path::to_path_buf)
        }
        _ => root.clone(),
    };
    let p = mirror.join(".specify").join("feature-numbers.jsonl");
    let mut rows = Vec::new();
    if cwd.join(&p).is_file() {
        let bytes = std::fs::read(cwd.join(&p)).map_err(io)?;
        let text = String::from_utf8(bytes).map_err(|e| format!("UnicodeDecodeError: {e}"))?;
        for l in l7r_guard::shared::speckit::splitlines(&text) {
            if !l7r_guard::shared::py_text::strip(l).is_empty() {
                rows.push(
                    serde_json::from_str::<Value>(l)
                        .map_err(|e| format!("json.decoder.JSONDecodeError: {e}"))?,
                );
            }
        }
    }
    out.line(&format!(
        "{BOLD}Feature numbers claimed{PLAIN} ({} - make claim, feature 197)",
        p.display()
    ));
    let last = &rows[rows.len().saturating_sub(10)..];
    for r in last {
        let or =
            |k: &str, d: Value| -> Result<Value, String> { Ok(get(r, k)?.cloned().unwrap_or(d)) };
        out.line(&format!(
            "  {} {}  {} {}",
            pad(&or("utc", Value::String("?".into()))?, true, 20)?,
            pad(&or("number", Value::from(0))?, false, 4)?,
            pad(&or("slug", Value::String("?".into()))?, true, 40)?,
            s(&or("clone", Value::String("?".into()))?)
        ));
    }
    if last.is_empty() {
        out.line("  (none yet - every claim made by make claim lands here)");
    }
    if !rows.is_empty() {
        out.line(&format!("  {} claims recorded", rows.len()));
    }
    out.line("");
    Ok(())
}

/// `l7r-gate measure audit runs|guards|claims`, from the working directory `cwd`; `guard_dir` the guard log
/// (`$GUARD_LOG_DIR`, else `~/.claude/guard-log`).
#[must_use]
pub fn cli(args: &[String], cwd: &Path, guard_dir: &Path) -> Reply {
    let mut out = Out {
        text: String::new(),
    };
    let done = match args {
        [one] if one == "runs" => runs(cwd, &mut out),
        [one] if one == "guards" => guards(guard_dir, &mut out),
        [one] if one == "claims" => claims(cwd, &mut out),
        _ => {
            return Reply {
                stdout: String::new(),
                stderr: "usage: l7r-gate measure audit runs|guards|claims\n".to_owned(),
                code: 2,
            }
        }
    };
    let mut stderr = String::new();
    let code = match done {
        Ok(()) => 0,
        Err(why) => {
            let _ = write!(
                stderr,
                "Traceback (most recent call last):\n  l7r-gate measure audit\n{why}\n"
            );
            1
        }
    };
    Reply {
        stdout: out.text,
        stderr,
        code,
    }
}

/// `os.path.expanduser(os.environ.get('GUARD_LOG_DIR', '~/.claude/guard-log'))`.
#[must_use]
pub fn guard_dir(value: Option<&str>, home: &Path) -> PathBuf {
    // the pattern is the value with `/*.json` appended, so an empty value globs `/`, and `~` expands only as a first component
    let raw = format!("{}/", value.unwrap_or("~/.claude/guard-log"));
    match raw.strip_prefix("~/") {
        Some(rest) => home.join(rest),
        None => PathBuf::from(raw),
    }
}

#[cfg(test)]
mod tests;
