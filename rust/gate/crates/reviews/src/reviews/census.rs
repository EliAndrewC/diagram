//! `l7r-gate reviews census [--root CLONE]` (feature 449 T136, the round arbiter's `ask:449-phase3-remainder`): `scripts/reviews/review_census.py`'s
//! port behind `make review-census`. Is each review check pulling its weight? One line per check: runs, NOT-REVIEWABLE runs, findings
//! by class, author-missed, and for the measured rows wall time and tokens (feature 294, FR-013 and US7; the GM 2026-10-01: *"I want to
//! take a hard look at what it is doing, what it is buying us"*).
//!
//! The rows before feature 294 carry no class, so they are classified once, as data (`dev/review-ledger-r0.json`); the measured table's
//! rows carry their class and cost in the row. The Python read the measured rows by running `reviews ledger-rows`; here they are the
//! guard's `shared::ledger::measured_rows`, asked in process (one implementation, FR-003).
//!
//! Where the Python raised (a missing or undecodable ledger, an r0 file that is not JSON or not a list of objects, a figure `float()`
//! refuses, a measured row with an empty wall cell) the reply is exit 1 and a `Traceback` line, nothing on stdout, as `ledger::raised`
//! answers one.

use std::collections::{HashMap, HashSet};
use std::fmt::Write as _;
use std::path::{Path, PathBuf};
use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_guard::shared::ledger::{measured_rows, COLUMNS};
use l7r_guard::shared::py_text::{py_float_of, split};
use l7r_guard::shared::pyjson::py_str;
use serde_json::Value;

use super::ledger::raised;
use super::{py_path, reply};
use crate::record::args::{parse, Spec};
use crate::record::repo::universal;
use crate::Reply;

/// The finding classes, in the report's column order.
pub const CLASSES: [&str; 4] = ["geometric", "judgment", "paperwork", "nothing"];
/// `_TOK`: the thousands of input tokens a tokens cell opens with (`\d` any script's decimal digit, as Python's `re` reads it).
static TOK: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"^(\d+)k in").unwrap_or_else(|e| unreachable!("{e}")));
/// One decimal digit of any script (Unicode `Nd`), as Python's `\d` and `float()` read one.
static ND: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"^\d$").unwrap_or_else(|e| unreachable!("{e}")));

fn is_nd(c: char) -> bool {
    ND.is_match(c.encode_utf8(&mut [0; 4])).unwrap_or(false)
}

/// A decimal digit's value: Unicode keeps each script's `Nd` digits as runs of ten from 0, so it is the distance from the run's start.
fn digit_value(c: char) -> Option<u32> {
    if !is_nd(c) {
        return None;
    }
    let mut start = u32::from(c);
    while char::from_u32(start - 1).is_some_and(is_nd) {
        start -= 1;
    }
    Some((u32::from(c) - start) % 10)
}

/// `float(text)` of a word of decimal digits, any script's (Python's `str.isdigit()` then `float()`), or None where a character is no
/// decimal digit. A word of other numeric characters (a superscript) is none here, where `isdigit` took it and `float` raised: the
/// ledger's lint (`^\d+ s$`) refuses such a wall cell at the commit, so no committed row reaches it.
fn decimal(word: &str) -> Option<f64> {
    let ascii: Option<String> = word
        .chars()
        .map(|c| digit_value(c).and_then(|d| char::from_digit(d, 10)))
        .collect();
    ascii?.parse().ok()
}

/// One check's totals, keyed by the Python's names (`runs`, `not_reviewable`, a class, `author_missed`, `wall_s`, `tokens_k`).
pub type Totals = HashMap<&'static str, f64>;

/// The checks in the order the Python's `defaultdict` first met them, each with its totals.
#[derive(Default)]
pub struct Tally {
    order: Vec<(String, Totals)>,
    at: HashMap<String, usize>,
}

impl Tally {
    fn of(&mut self, check: String) -> &mut Totals {
        let n = *self.at.entry(check.clone()).or_insert_with(|| {
            self.order.push((check, Totals::new()));
            self.order.len() - 1
        });
        &mut self.order[n].1
    }
}

fn add(t: &mut Totals, key: &'static str, by: f64) {
    *t.entry(key).or_insert(0.0) += by;
}

/// Whether Python reads the value as false (`x or ...` takes the other side).
fn falsy(v: Option<&Value>) -> bool {
    match v {
        None | Some(Value::Null) => true,
        Some(Value::Bool(b)) => !b,
        Some(Value::Number(n)) => n.as_f64() == Some(0.0),
        Some(Value::String(s)) => s.is_empty(),
        Some(Value::Array(a)) => a.is_empty(),
        Some(Value::Object(m)) => m.is_empty(),
    }
}

/// `float(x or 0)`.
fn float_or_zero(v: Option<&Value>) -> Result<f64, String> {
    match v {
        Some(v) if !falsy(Some(v)) => py_float_of(v),
        _ => Ok(0.0),
    }
}

/// The rows `for row in r0` walks: a list's items; an empty object or string none; any other value raised as Python raised it.
fn r0_rows(r0: &Value) -> Result<Vec<&serde_json::Map<String, Value>>, String> {
    let items: Vec<&Value> = match r0 {
        Value::Array(a) => a.iter().collect(),
        Value::Object(m) if m.is_empty() => Vec::new(),
        Value::String(s) if s.is_empty() => Vec::new(),
        Value::Object(_) | Value::String(_) => {
            return Err("AttributeError: 'str' object has no attribute 'get'".to_owned())
        }
        _ => return Err("TypeError: the r0 data is not iterable".to_owned()),
    };
    items
        .into_iter()
        .map(|row| {
            row.as_object()
                .ok_or_else(|| "AttributeError: a row has no attribute 'get'".to_owned())
        })
        .collect()
}

/// `tally(r0, ledger_text)`: the old rows' data, then the measured table's rows. A measured row is one finding; its run is counted
/// once per (date, check, subject, wall).
///
/// # Errors
///
/// What the Python raised, as its traceback's last line names it.
pub fn tally(r0: &Value, ledger_text: &str) -> Result<Tally, String> {
    let mut out = Tally::default();
    for row in r0_rows(r0)? {
        let t = out.of(py_str(row.get("agent").unwrap_or(&Value::Null)));
        add(t, "runs", float_or_zero(row.get("runs"))?);
        add(
            t,
            "not_reviewable",
            float_or_zero(row.get("not_reviewable_runs"))?,
        );
        let findings = row.get("findings");
        let classes = match findings {
            Some(Value::Object(m)) => Some(m),
            f if falsy(f) => None,
            _ => return Err("AttributeError: findings has no attribute 'get'".to_owned()),
        };
        for c in CLASSES {
            add(t, c, float_or_zero(classes.and_then(|m| m.get(c)))?);
        }
        add(
            t,
            "author_missed",
            float_or_zero(row.get("author_missed_fixed"))?,
        );
        add(t, "wall_s", 60.0 * float_or_zero(row.get("wall_min"))?);
    }
    let mut seen: HashSet<[String; 4]> = HashSet::new();
    for (_n, cells) in measured_rows(ledger_text) {
        if cells.len() != COLUMNS.len() {
            continue;
        }
        // the cells in `COLUMNS`' order: date, check, subject, verdict, finding, class, author missed?, acted on, wall, tokens
        let t = out.of(cells[1].clone());
        if let Some(class) = CLASSES.iter().find(|c| **c == cells[5]) {
            add(t, class, 1.0);
        }
        add(t, "author_missed", f64::from(u8::from(cells[6] == "yes")));
        let run = [
            cells[0].clone(),
            cells[1].clone(),
            cells[2].clone(),
            cells[8].clone(),
        ];
        if seen.insert(run) {
            add(t, "runs", 1.0);
            add(
                t,
                "not_reviewable",
                f64::from(u8::from(cells[3].to_uppercase() == "NOT-REVIEWABLE")),
            );
            let Some(wall) = split(&cells[8]).first().copied() else {
                return Err("IndexError: list index out of range".to_owned());
            };
            add(t, "wall_s", decimal(wall).unwrap_or(0.0));
            let tok = TOK
                .captures(&cells[9])
                .ok()
                .flatten()
                .and_then(|c| c.get(1).and_then(|m| decimal(m.as_str())));
            add(t, "tokens_k", tok.unwrap_or(0.0));
        }
    }
    Ok(out)
}

/// `f"{x:.<places>f}"`, `nan` as Python spells it.
fn fixed(x: f64, places: usize) -> String {
    if x.is_nan() {
        "nan".to_owned()
    } else {
        format!("{x:.places$}")
    }
}

/// `report(totals)`: the table, the checks by most runs first, ties in the order they were met.
#[must_use]
pub fn report(totals: &Tally) -> String {
    let mut rows: Vec<&(String, Totals)> = totals.order.iter().collect();
    let get = |t: &Totals, k: &str| t.get(k).copied().unwrap_or(0.0);
    rows.sort_by(|a, b| {
        (-get(&a.1, "runs"))
            .partial_cmp(&-get(&b.1, "runs"))
            .unwrap_or(std::cmp::Ordering::Equal)
    });
    let mut out = "check | runs | not-reviewable | geometric | judgment | paperwork | nothing | author missed | wall (min) | tokens (M)".to_owned();
    for (check, t) in rows {
        let classes: Vec<String> = CLASSES.iter().map(|c| fixed(get(t, c), 0)).collect();
        let _ = write!(
            out,
            "\n{check} | {} | {} | {} | {} | {} | {}",
            fixed(get(t, "runs"), 0),
            fixed(get(t, "not_reviewable"), 0),
            classes.join(" | "),
            fixed(get(t, "author_missed"), 0),
            fixed(get(t, "wall_s") / 60.0, 0),
            fixed(get(t, "tokens_k") / 1000.0, 1),
        );
    }
    out
}

/// The census of the clone at `root`: its r0 data (none where the file is not a file), then its ledger.
///
/// # Errors
///
/// What the Python raised: an unreadable or undecodable file, r0 that is not JSON, and what `tally` raises.
pub fn census(root: &Path) -> Result<String, String> {
    let r0_path = root.join("dev/review-ledger-r0.json");
    let r0 = if r0_path.is_file() {
        let text =
            std::fs::read_to_string(&r0_path).map_err(|e| format!("{}: {e}", r0_path.display()))?;
        serde_json::from_str(&text).map_err(|e| format!("json.decoder.JSONDecodeError: {e}"))?
    } else {
        Value::Array(Vec::new())
    };
    let ledger = root.join("dev/review-ledger.md");
    let text =
        std::fs::read_to_string(&ledger).map_err(|e| format!("{}: {e}", ledger.display()))?;
    Ok(report(&tally(&r0, &universal(&text))?))
}

/// `review_census.py [--root CLONE]`: the clone defaults to the gate's own tree (`tree`, where the Python's `__file__` stood).
#[must_use]
pub fn cli(args: &[String], tree: &Path) -> Reply {
    let p = match parse(args, &[Spec::value("--root")]) {
        Ok(p) => p,
        Err(why) => {
            return reply(
                String::new(),
                format!("usage: l7r-gate reviews census [--root ROOT]\nl7r-gate reviews census: error: {why}\n"),
                2,
            )
        }
    };
    let root: PathBuf = if p.has("--root") {
        py_path(p.text("--root", ""))
    } else {
        tree.to_path_buf()
    };
    match census(&root) {
        Ok(table) => reply(table + "\n", String::new(), 0),
        Err(why) => raised(String::new(), "census", &why),
    }
}

#[cfg(test)]
mod tests;
