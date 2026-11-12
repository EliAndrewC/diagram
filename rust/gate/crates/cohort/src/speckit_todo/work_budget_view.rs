//! The work budget's standing record, in view (feature 443 T04, FR-007, plan D8), under feature 444's row of the report: the whole roll's
//! line of `dev/work-budget.md`, every stage's status, and the stages whose counted operations at 40 households moved between the two
//! newest runs in `dev/work-budget/`.
//!
//! Ported from `scripts/measure/work_budget_view.py` by feature 449 T118 because the report it prints in is ported here; the Rust land
//! prints it too (`l7r-gate land`, T121, `ask:449-T83-scope`), one implementation for both, the `.py` deleted with `land.py`.

use std::path::Path;

use l7r_guard::shared::py_text::strip;
use l7r_guard::shared::speckit::splitlines;
use serde_json::Value;

use super::truthy;

const RECORD: &str = "dev/work-budget.md";
const RUNS: &str = "dev/work-budget";
const ROLL: &str = "| **the whole roll** |";

/// A file read as `read_text(encoding="utf-8")`: strict, every `\r\n` and `\r` a `\n`.
fn read_utf8(path: &Path) -> Result<String, String> {
    let bytes = std::fs::read(path).map_err(|e| format!("{}: {e}", path.display()))?;
    let text = String::from_utf8(bytes).map_err(|e| format!("UnicodeDecodeError: {e}"))?;
    Ok(text.replace("\r\n", "\n").replace('\r', "\n"))
}

/// A table row's cells: `line.strip().strip("|").split("|")`, each stripped.
fn cells(line: &str) -> Vec<String> {
    strip(line)
        .trim_matches('|')
        .split('|')
        .map(|c| strip(c).to_owned())
        .collect()
}

/// Each stage's counted operations at 40 households, in the run's order.
fn ops40(run: &Value) -> Result<Vec<(String, Value)>, String> {
    let Value::Object(run) = run else {
        return Err("AttributeError: a work-budget run is not an object".to_owned());
    };
    let summary = run.get("summary").filter(|v| truthy(v));
    let stages = match summary {
        None => None,
        Some(Value::Object(s)) => s.get("stages").filter(|v| truthy(v)),
        Some(_) => return Err("AttributeError: a run's summary is not an object".to_owned()),
    };
    let mut out = Vec::new();
    let Some(stages) = stages else {
        return Ok(out);
    };
    let Value::Object(stages) = stages else {
        return Err("AttributeError: a run's stages are not an object".to_owned());
    };
    for (name, st) in stages {
        let Value::Object(st) = st else {
            return Err(format!("AttributeError: the stage {name} is not an object"));
        };
        let at = match st.get("per").filter(|v| truthy(v)) {
            None => None,
            Some(Value::Object(per)) => per.get("40").filter(|v| truthy(v)),
            Some(_) => {
                return Err(format!(
                    "AttributeError: the stage {name}'s per is not an object"
                ))
            }
        };
        if let Some(at) = at {
            let ops = at
                .get("ops")
                .ok_or_else(|| format!("KeyError: 'ops' (the stage {name})"))?;
            out.push((name.clone(), ops.clone()));
        }
    }
    Ok(out)
}

/// `f"{x:,.0f}"`: the number rounded half to even, its thousands grouped.
fn grouped(v: &Value) -> Result<String, String> {
    let x = match v {
        Value::Number(n) => n.as_f64().unwrap_or_default(),
        Value::Bool(b) => f64::from(u8::from(*b)),
        _ => {
            return Err(
                "ValueError: Unknown format code 'f' for a value that is no number".to_owned(),
            )
        }
    };
    let text = format!("{x:.0}");
    let (sign, digits) = text
        .strip_prefix('-')
        .map_or(("", text.as_str()), |d| ("-", d));
    let mut out = String::new();
    for (i, c) in digits.chars().enumerate() {
        if i > 0 && (digits.len() - i) % 3 == 0 {
            out.push(',');
        }
        out.push(c);
    }
    Ok(format!("{sign}{out}"))
}

/// Python's `!=` between two numbers of a run (`1 == 1.0`), or two absent ones.
fn differ(a: Option<&Value>, b: Option<&Value>) -> bool {
    match (a, b) {
        (Some(Value::Number(x)), Some(Value::Number(y))) => x.as_f64() != y.as_f64(),
        (a, b) => a != b,
    }
}

/// `<stage> <before> -> <after>` for each stage whose operations at 40 households differ between the two newest runs.
fn moved(root: &Path) -> Result<Vec<String>, String> {
    let mut runs: Vec<_> = std::fs::read_dir(root.join(RUNS))
        .into_iter()
        .flatten()
        .filter_map(Result::ok)
        .filter(|e| e.file_name().to_string_lossy().ends_with(".json"))
        .map(|e| e.path())
        .collect();
    runs.sort();
    if runs.len() < 2 {
        return Ok(Vec::new());
    }
    let read = |p: &Path| -> Result<Vec<(String, Value)>, String> {
        let run: Value = serde_json::from_str(&read_utf8(p)?)
            .map_err(|e| format!("json.decoder.JSONDecodeError: {e}"))?;
        ops40(&run)
    };
    let old = read(&runs[runs.len() - 2])?;
    let new = read(&runs[runs.len() - 1])?;
    let get =
        |m: &[(String, Value)], k: &str| m.iter().find(|(n, _)| n == k).map(|(_, v)| v.clone());
    let mut keys: Vec<&String> = new.iter().map(|(k, _)| k).collect();
    keys.extend(
        old.iter()
            .map(|(k, _)| k)
            .filter(|k| get(&new, k).is_none()),
    );
    let zero = Value::from(0);
    let mut out = Vec::new();
    for k in keys {
        let (before, after) = (get(&old, k), get(&new, k));
        if k == "roll" || !differ(before.as_ref(), after.as_ref()) {
            continue;
        }
        out.push(format!(
            "{k} {} -> {}",
            grouped(before.as_ref().unwrap_or(&zero))?,
            grouped(after.as_ref().unwrap_or(&zero))?
        ));
    }
    Ok(out)
}

/// The record's summary, or one line saying there is none yet.
///
/// # Errors
/// A record or run the Python raised on.
pub fn lines(root: &Path) -> Result<Vec<String>, String> {
    let path = root.join(RECORD);
    if !path.is_file() {
        return Ok(vec![
            "work budget: no standing record yet - `make work-budget` writes dev/work-budget.md"
                .to_owned(),
        ]);
    }
    let text = read_utf8(&path)?;
    let all = splitlines(&text);
    let rows: Vec<&str> = all
        .iter()
        .copied()
        .filter(|l| l.starts_with("| ") && !l.starts_with("| stage |") && !l.starts_with("|---"))
        .collect();
    let head = rows.iter().find(|l| l.starts_with(ROLL));
    let header = all
        .iter()
        .find(|l| l.starts_with("| stage |"))
        .copied()
        .unwrap_or("");
    let cols = cells(header);
    let mut out = Vec::new();
    if let Some(head) = head {
        let mut c: Vec<(String, String)> = Vec::new();
        for (k, v) in cols.iter().zip(cells(head)) {
            match c.iter_mut().find(|(n, _)| n == k) {
                Some((_, old)) => *old = v,
                None => c.push((k.clone(), v)),
            }
        }
        let get = |k: &str| {
            c.iter()
                .find(|(n, _)| n == k)
                .map_or("-", |(_, v)| v.as_str())
        };
        out.push(format!(
            "work budget (dev/work-budget.md): the whole roll {} counted operations @40, exponent {}, budget {}, {}",
            get("ops @40"),
            get("exponent"),
            get("budget @40"),
            get("status")
        ));
    }
    let mut by: Vec<(String, Vec<String>)> = Vec::new();
    for row in rows.iter().filter(|l| !l.starts_with(ROLL)) {
        let c = cells(row);
        let [.., before, last] = c.as_slice() else {
            return Err("IndexError: list index out of range".to_owned());
        };
        let entry = if before == "-" {
            c[0].clone()
        } else {
            format!("{} ({before})", c[0])
        };
        match by.iter_mut().find(|(s, _)| s == last) {
            Some((_, names)) => names.push(entry),
            None => by.push((last.clone(), vec![entry])),
        }
    }
    out.extend(
        by.iter()
            .map(|(status, names)| format!("  {status} ({}): {}", names.len(), names.join(", "))),
    );
    let mv = moved(root)?;
    out.push(format!(
        "  moved since the previous run (@40): {}",
        if mv.is_empty() {
            "none".to_owned()
        } else {
            mv.join("; ")
        }
    ));
    Ok(out)
}
