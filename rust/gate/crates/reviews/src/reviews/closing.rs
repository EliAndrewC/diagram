//! No route closes a feature without its report and its carried measurements (feature 375, FR-009, FR-014; plan D13), ported from
//! `scripts/gates/close_check.py` by feature 449 T127 (phase 3 by FR-001, filed by T91's plan review).
//!
//! WHY. The GM, 2026-10-10: the post-mortem table is the last step of every feature, and *"anything that requires someone to just
//! remember to do the right thing is not tenable"*. A feature closes three ways - its last `make tick`, a status line turned `Done`
//! (or `Superseded by`, `Withdrawn`), `make gm-reviewed` - and each asks this one check, as does the push for every feature the delta
//! touches that reads closed. Owed: `specs/NNN-*/report.md` (FR-009), every measurement another spec CARRIED to it
//! (`Carried: SC-nnn -> NNN <key>`, FR-014) as a key of its `measurements.json`, a `research record` feature's implementation check
//! (feature 378) and no open arbiter tooling fix (feature 379). A feature already closed when the check landed is not asked
//! (`closed-before-375.txt`, written at that commit from what `make speckit-todo` read closed - never a number range: 372 and 374
//! were open, and are asked).
//!
//! WHERE (feature 449 T127): here in `reviews`, which builds on `core` alone, so that `gm_review`'s last-box close calls it in process
//! and `cohort`, which holds the push and the command line (`l7r-gate close-check`, beside `touched_features` and the speckit state it
//! reads), builds on it without a cycle. `core` was the other crate under both, and was passed over: an edit there rebuilds every gate
//! crate (T92). The arbiter's open tooling fixes (`open_fixes`, `fix_hold`) moved here from `arbiter`, which builds on `reviews`, so the
//! one reader serves both; `arbiter` re-exports them.
//!
//! THE IMPLEMENTATION CHECK, IN PROCESS (feature 449 T132, `ask:449-phase3-remainder` Q2 task B): `impl_check.py`'s port lives in `claims`,
//! which builds on this crate (its `make claims-known` row is `gm_review::add_row`), so the check is a function each caller hands in
//! ([`ImplCheck`]) - the binary for `l7r-gate close-check` and `l7r-gate gm-review`, `task`, which builds on `claims`, for the tick - as
//! `plan::cli` takes the claims tool. T127 ran `impl_check.py --missing-json DIR...` by path here; nothing reaches Python now.

#[cfg(test)]
mod tests;

use std::path::{Path, PathBuf};
use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_guard::shared::checks;
use l7r_guard::shared::py_text::{split, strip};
use serde_json::Value;

use super::gm_review::name;

/// The features closed when the check landed, under the tree whose tools run (`GRANDFATHERED`, beside the script it was).
pub const GRANDFATHERED: &str = "scripts/gates/closed-before-375.txt";

static CARRY: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(r"`?Carried:\s*(SC-\d+)\s*->\s*(\d+)\s+([\w.-]+)`?")
        .unwrap_or_else(|_| unreachable!("the carry pattern compiles"))
});

/// One carry: (declaring feature, SC, carrying feature number, key).
pub type Carry = (String, String, String, String);

/// Every `Carried:` line in any spec under `specs`, in the order of `sorted(specs.glob("*/spec.md"))`.
///
/// # Errors
/// A `spec.md` that cannot be read (a directory, a dangling link), as `read_text` raised.
pub fn carries(specs: &Path) -> Result<Vec<Carry>, String> {
    // `*` matches a dot directory and a link to a directory; `spec.md` is matched by `lstat`, so a dangling link is listed and raises
    let mut dirs: Vec<PathBuf> = std::fs::read_dir(specs)
        .map(|it| {
            it.flatten()
                .map(|e| e.path())
                .filter(|p| p.is_dir())
                .collect()
        })
        .unwrap_or_default();
    dirs.sort();
    let mut out = Vec::new();
    for d in dirs {
        let spec = d.join("spec.md");
        if std::fs::symlink_metadata(&spec).is_err() {
            continue;
        }
        let bytes =
            std::fs::read(&spec).map_err(|e| format!("OSError: {e}: {}", spec.display()))?;
        let text = String::from_utf8_lossy(&bytes);
        for c in CARRY.captures_iter(&text).flatten() {
            out.push((name(&d), c[1].to_owned(), c[2].to_owned(), c[3].to_owned()));
        }
    }
    Ok(out)
}

/// `str(int(s))`: Python's `int()` of a feature's number, kept as text so a number of any length is read (ASCII digits; Python also
/// reads other scripts' digits, which no feature directory holds).
fn py_int_text(s: &str) -> Result<String, String> {
    let body = strip(s);
    let (neg, digits) = match body.as_bytes().first() {
        Some(b'-') => (true, &body[1..]),
        Some(b'+') => (false, &body[1..]),
        _ => (false, body),
    };
    let ok = !digits.is_empty()
        && !digits.starts_with('_')
        && !digits.ends_with('_')
        && !digits.contains("__")
        && digits.chars().all(|c| c.is_ascii_digit() || c == '_');
    if !ok {
        return Err(format!(
            "ValueError: invalid literal for int() with base 10: {s:?}"
        ));
    }
    let n = digits.replace('_', "");
    let n = n.trim_start_matches('0');
    Ok(match (n.is_empty(), neg) {
        (true, _) => "0".to_owned(),
        (false, true) => format!("-{n}"),
        (false, false) => n.to_owned(),
    })
}

/// JSON as Python's `json` reads it: `NaN`, `Infinity` and `-Infinity` are values there (its own `json.dump` writes them for a float
/// that is no number), which serde refuses; outside a string each reads here as `null`, enough to say which keys the file holds.
fn py_json(text: &str) -> Option<Value> {
    if let Ok(v) = serde_json::from_str(text) {
        return Some(v);
    }
    let (mut out, mut in_string, mut escaped) = (String::with_capacity(text.len()), false, false);
    let mut rest = text;
    while let Some(c) = rest.chars().next() {
        if in_string {
            in_string = escaped || c != '"';
            escaped = !escaped && c == '\\';
        } else if c == '"' {
            in_string = true;
        } else if let Some(word) = ["-Infinity", "Infinity", "NaN"]
            .into_iter()
            .find(|w| rest.starts_with(w))
        {
            out.push_str("null");
            rest = &rest[word.len()..];
            continue;
        }
        out.push(c);
        rest = &rest[c.len_utf8()..];
    }
    serde_json::from_str(&out).ok()
}

/// The names in `closed-before-375.txt` under `tree`; none where it is no file.
fn grandfathered(tree: &Path) -> Result<Vec<String>, String> {
    let path = tree.join(GRANDFATHERED);
    if !path.is_file() {
        return Ok(Vec::new());
    }
    let bytes = std::fs::read(&path).map_err(|e| format!("OSError: {e}: {}", path.display()))?;
    let text = String::from_utf8(bytes)
        .map_err(|e| format!("UnicodeDecodeError: {e}: {}", path.display()))?;
    Ok(split(&text).into_iter().map(str::to_owned).collect())
}

/// `set(json.loads(measurements.json))` as the keys it holds: an unreadable or broken file is none (`OSError`, `ValueError` caught);
/// a value `set()` cannot take (a number, `null`, a list holding a list or an object) raises, as the uncaught `TypeError` did.
fn measured(d: &Path) -> Result<Vec<String>, String> {
    let Ok(bytes) = std::fs::read(d.join("measurements.json")) else {
        return Ok(Vec::new());
    };
    let Some(value) = std::str::from_utf8(&bytes).ok().and_then(py_json) else {
        return Ok(Vec::new());
    };
    let unhashable = |v: &Value| {
        format!(
            "TypeError: unhashable type in {}/measurements.json: {v}",
            name(d)
        )
    };
    match value {
        Value::Object(m) => Ok(m.keys().cloned().collect()),
        Value::String(s) => Ok(s.chars().map(String::from).collect()),
        Value::Array(items) => {
            let mut out = Vec::new();
            for v in &items {
                match v {
                    Value::Array(_) | Value::Object(_) => return Err(unhashable(v)),
                    Value::String(s) => out.push(s.clone()),
                    _ => {}
                }
            }
            Ok(out)
        }
        other => Err(format!(
            "TypeError: {} object is not iterable ({}/measurements.json)",
            match other {
                Value::Null => "'NoneType'",
                Value::Bool(_) => "'bool'",
                _ => "a number",
            },
            name(d)
        )),
    }
}

/// `(trigger, tooling_fix)` of every open arbiter tooling fix in feature `d` (`hm_arbiter.open_fixes`; moved from `arbiter` by feature
/// 449 T127 so the closing check reads it in process).
#[must_use]
pub fn open_fixes(d: &Path) -> Vec<(String, String)> {
    let text = |r: &Value, k: &str| r.get(k).and_then(Value::as_str).unwrap_or("").to_owned();
    let py = |v: Option<&Value>| match v {
        None | Some(Value::Null) => String::new(),
        Some(Value::String(s)) => s.clone(),
        Some(other) => other.to_string(),
    };
    let mut fixes: Vec<(String, String)> = Vec::new();
    for line in std::fs::read_to_string(d.join("arbiter.jsonl"))
        .unwrap_or_default()
        .lines()
    {
        let Ok(r) = serde_json::from_str::<Value>(line) else {
            continue;
        };
        if text(&r, "fix") == "open" && !checks::falsy(r.get("tooling_fix")) {
            let t = py(r.get("trigger"));
            let fix = py(r.get("tooling_fix"));
            match fixes.iter_mut().find(|(k, _)| *k == t) {
                Some(slot) => slot.1 = fix,
                None => fixes.push((t, fix)),
            }
        } else if matches!(text(&r, "status").as_str(), "done" | "declined") {
            let of = py(r.get("fix_of"));
            fixes.retain(|(k, _)| *k != of);
        }
    }
    fixes
}

/// Why feature `d` may not move on while an arbiter tooling fix is open, or "" (feature 379 FR-004).
#[must_use]
pub fn fix_hold(d: &Path) -> String {
    let fixes = open_fixes(d);
    if fixes.is_empty() {
        return String::new();
    }
    let listed = fixes
        .iter()
        .map(|(t, fix)| format!("    {t}: {fix}"))
        .collect::<Vec<_>>()
        .join("\n");
    format!(
        "the round arbiter's tooling fix is open - make it, with its test, in this feature before going on (feature 379):\n{listed}\n  made:     make arbiter-fix-done ID=\"<trigger>\" NOTE=\"<what was built>\" TEST=<its test under tests/> LAND=\"<the fix's files>\" F=<feature> TICK=<the task> (lands them, settles the fix, ticks the task)\n  overhaul: make arbiter-fix-declined ID=\"<trigger>\" REASON=\"<why it overhauls a process>\" (a question for the GM, owed escalation-check)"
    )
}

/// The implementation check (`claims::impl_check::missing_each`): `impl_check.missing(d, d.resolve().parents[1])` for each directory, in
/// order, or what it raised.
pub type ImplCheck = fn(&[&Path]) -> Result<Vec<Vec<String>>, String>;

/// What the closing check runs: the tree whose closing list it reads (`L7R_GATE_TREE`) and the implementation check.
pub struct Tools<'a> {
    pub tree: &'a Path,
    pub impl_check: ImplCheck,
}

/// What the closing check found: each directory's reasons.
pub struct Closing {
    pub each: Vec<Vec<String>>,
}

/// The implementation check of `dirs` (none asked when there are none). A raise keeps its last line `impl_check.missing raised`, under
/// what the check said, as the by-path run's carried the traceback above its own words (feature 449 T127).
fn impl_missing(tools: &Tools, dirs: &[&Path]) -> Result<Vec<Vec<String>>, String> {
    if dirs.is_empty() {
        return Ok(Vec::new());
    }
    (tools.impl_check)(dirs).map_err(|why| format!("{why}\nimpl_check.missing raised"))
}

/// The reasons before the implementation check: no report, a carried key missing from `measurements.json`.
fn first_reasons(
    d: &Path,
    carried: &mut Option<Vec<Carry>>,
    specs: &Path,
) -> Result<Vec<String>, String> {
    let n = name(d);
    let mut out = Vec::new();
    if !d.join("report.md").is_file() {
        let f = py_int_text(n.split('-').next().unwrap_or_default())?;
        out.push(format!(
            "{n} has no report.md - `make feature-report F={f} WRITE=1` writes it (FR-009)"
        ));
    }
    let have = measured(d)?;
    let num = n
        .split('-')
        .next()
        .unwrap_or_default()
        .trim_start_matches('0');
    if carried.is_none() {
        *carried = Some(carries(specs)?);
    }
    for (decl, sc, k, key) in carried.iter().flatten() {
        if k.trim_start_matches('0') == num && !have.contains(key) {
            out.push(format!(
                "{decl}'s {sc} is carried here and `{key}` is not in {n}/measurements.json (FR-014)"
            ));
        }
    }
    Ok(out)
}

/// Why each of `dirs` may not close (`close_check.reasons(d, specs)` for each, in order): no report, a carried key missing from its
/// `measurements.json`, its implementation check owed, an open arbiter tooling fix; none for a feature closed before the check.
///
/// # Errors
/// What the Python raised: an unreadable list or spec, a number that is no number, a `measurements.json` `set()` cannot take, the
/// implementation check failing. As the Python asked each directory in turn, the directories before the one that fails are still put
/// to the implementation check first.
pub fn reasons(tools: &Tools, specs: &Path, dirs: &[PathBuf]) -> Result<Closing, String> {
    let mut carried = None;
    let mut known: Option<Vec<String>> = None;
    let mut firsts: Vec<Option<Vec<String>>> = Vec::with_capacity(dirs.len());
    let mut failed = None;
    for d in dirs {
        let old = match &known {
            Some(k) => k,
            None => known.insert(grandfathered(tools.tree)?),
        };
        if old.contains(&name(d)) {
            firsts.push(None);
            continue;
        }
        match first_reasons(d, &mut carried, specs) {
            Ok(r) => firsts.push(Some(r)),
            Err(e) => {
                failed = Some(e);
                break;
            }
        }
    }
    let asked: Vec<&Path> = dirs
        .iter()
        .zip(&firsts)
        .filter(|(_, f)| f.is_some())
        .map(|(d, _)| d.as_path())
        .collect();
    // as the Python asked each directory in turn, the directories before one that fails are still put to the implementation check
    // first, and its raise is the one reported
    let missing = impl_missing(tools, &asked)?;
    if let Some(e) = failed {
        return Err(e);
    }
    let mut missing = missing.into_iter();
    let each = dirs
        .iter()
        .zip(firsts)
        .map(|(d, first)| {
            first.map_or_else(Vec::new, |mut out| {
                out.extend(missing.next().unwrap_or_default());
                let hold = fix_hold(d);
                if !hold.is_empty() {
                    out.push(hold);
                }
                out
            })
        })
        .collect();
    Ok(Closing { each })
}
