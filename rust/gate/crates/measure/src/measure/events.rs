//! The events a feature's report reads, as `feature_report.py` and `task_phases.py` read them (feature 449 T119, the measure chain under
//! `ask:449-T83-scope`): every clone's event log for the feature and any transcript, deduplicated and in time order, through the guard's
//! one event-log reader (`event_log_hooks::read`, the T89 precedent of reusing `at_rev`); and the Python's arithmetic and text the
//! report's figures are printed in, so each table is the Python's byte for byte.
//!
//! An event is the `dict` `json.loads` made; where the Python indexed one (`e["t"]`, `e["ev"]`) and raised on a missing key or a time
//! `fromisoformat` refuses, the reading here returns the error at the same point, so the command fails where the Python failed.

use std::cmp::Ordering;
use std::collections::HashMap;
use std::path::{Path, PathBuf};
use std::process::{Command, Output};

use l7r_guard::guards::event_log_hooks::common_git_dir;
use l7r_guard::guards::event_log_hooks::read::{from_transcript, read_jsonl, universal};
use l7r_guard::shared::iso;
use l7r_guard::shared::log::civil;
use l7r_guard::shared::py_text::{repr, strip};
use serde_json::{Map, Value};

pub use l7r_gate_core::cohort::truthy;
pub use l7r_gate_core::record::bundle::{head, py_str};

/// One event: the object a log line or a transcript row became.
pub type Event = Map<String, Value>;
/// What a run raised, as the Python's traceback named it.
pub type Raised = String;

/// A gap past this is the session left alone, counted apart (`IDLE_CAP_S`).
pub const IDLE_CAP_S: f64 = 3600.0;
/// Every clone's checkout, whose event logs the report reads beside this clone's (`feature_report.CLONES`).
pub const CLONES: &str = "/diagram/.clones";

static NULL: Value = Value::Null;

/// A pattern of this port's own, compiled once.
#[must_use]
pub fn re(pattern: &str) -> fancy_regex::Regex {
    fancy_regex::Regex::new(pattern).unwrap_or_else(|e| unreachable!("{e}"))
}

/// `e.get(key)`: the value, `None` where it is missing.
#[must_use]
pub fn get<'a>(e: &'a Event, key: &str) -> &'a Value {
    e.get(key).unwrap_or(&NULL)
}

/// `str(e.get(key))`.
#[must_use]
pub fn s(e: &Event, key: &str) -> String {
    py_str(get(e, key))
}

/// `str(e.get(key) or "")`.
#[must_use]
pub fn or_s(e: &Event, key: &str) -> String {
    or_text(get(e, key), "")
}

/// `str(v or default)`.
#[must_use]
pub fn or_text(v: &Value, default: &str) -> String {
    if truthy(v) {
        py_str(v)
    } else {
        default.to_owned()
    }
}

/// Whether `e.get(key)` is truthy.
#[must_use]
pub fn on(e: &Event, key: &str) -> bool {
    truthy(get(e, key))
}

/// `e.get(key) == text`.
#[must_use]
pub fn is(e: &Event, key: &str, text: &str) -> bool {
    get(e, key).as_str() == Some(text)
}

/// `e[key]`: the Python's `KeyError` where it is missing.
///
/// # Errors
///
/// The key is missing.
pub fn need<'a>(e: &'a Event, key: &str) -> Result<&'a Value, Raised> {
    e.get(key).ok_or_else(|| format!("KeyError: {}", repr(key)))
}

/// `datetime.fromisoformat(text.replace("Z", "+00:00")).timestamp()` (`_t`, `parse_t`): an aware time is its microseconds over a million,
/// as `total_seconds` divides them, a naive one the machine's local time.
///
/// # Errors
///
/// `fromisoformat`'s `ValueError`.
pub fn ts(text: &str) -> Result<f64, Raised> {
    let text = text.replace('Z', "+00:00");
    let bad = || format!("ValueError: Invalid isoformat string: {}", repr(&text));
    let (moment, zone) = iso::moment(&text).ok_or_else(bad)?;
    match zone {
        #[expect(
            clippy::cast_precision_loss,
            reason = "microseconds since the epoch, inside f64's exact range"
        )]
        Some(offset) => Ok((moment - offset) as f64 / 1e6),
        None => iso::parse(&text).ok_or_else(bad),
    }
}

/// `_t(e["t"])`: the event's time, the Python's raise where it has none, or one that is no text or no time.
///
/// # Errors
///
/// The `KeyError`, `AttributeError` or `ValueError` the Python raised.
pub fn t_of(e: &Event) -> Result<f64, Raised> {
    match need(e, "t")? {
        Value::String(t) => ts(t),
        _ => Err("AttributeError: an event's time is no text".to_owned()),
    }
}

/// `Path(text).parts` past its root: `.` and empty components dropped, as pathlib drops them.
#[must_use]
pub fn py_path_parts(text: &str) -> Vec<String> {
    text.split('/')
        .filter(|c| !c.is_empty() && *c != ".")
        .map(str::to_owned)
        .collect()
}

/// `fromisoformat(iso.replace("Z", "+00:00")).astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")` (`utc`).
///
/// # Errors
///
/// `fromisoformat`'s `ValueError`.
pub fn iso_utc(iso: &str) -> Result<String, Raised> {
    #[expect(
        clippy::cast_possible_truncation,
        clippy::cast_sign_loss,
        reason = "seconds since the epoch, after it"
    )]
    let secs = ts(iso)?.floor().max(0.0) as u64;
    let (y, mo, d, h, mi, sec) = civil(secs);
    Ok(format!("{y:04}-{mo:02}-{d:02}T{h:02}:{mi:02}:{sec:02}Z"))
}

/// `e["t"]` as text: every event read has one, `load_events` keeping no other.
#[must_use]
pub fn t_text(e: &Event) -> &str {
    get(e, "t").as_str().unwrap_or_default()
}

/// `f"{x:.{n}f}"`: Rust's fixed formatting rounds the exact binary value half to even, as Python's does.
#[must_use]
pub fn fixed(x: f64, n: usize) -> String {
    format!("{x:.n$}")
}

/// `_hm`: minutes, rounded half to even, as `N min` or `H h MM min`.
#[must_use]
pub fn hm(seconds: f64) -> String {
    #[expect(
        clippy::cast_possible_truncation,
        reason = "Python's round() of a duration in minutes"
    )]
    let m = (seconds / 60.0).round_ties_even() as i64;
    if m >= 60 {
        format!("{} h {:02} min", m.div_euclid(60), m.rem_euclid(60))
    } else {
        format!("{m} min")
    }
}

/// `datetime.fromtimestamp(t, UTC).strftime("%H:%M")`: the microseconds rounded half to even first, as `CPython` rounds them.
#[must_use]
pub fn hhmm(t: f64) -> String {
    let mut whole = t.trunc();
    let us = ((t - whole) * 1e6).round_ties_even();
    if us >= 1e6 {
        whole += 1.0;
    } else if us < 0.0 {
        whole -= 1.0;
    }
    #[expect(
        clippy::cast_possible_truncation,
        clippy::cast_sign_loss,
        reason = "seconds since the epoch, after it"
    )]
    let secs = whole.max(0.0) as u64;
    let (_, _, _, h, m, _) = civil(secs);
    format!("{h:02}:{m:02}")
}

/// Python's `float()` of a value and of a text: the guard's `py_text` since feature 449 T136, where the review census reads them too
/// (one implementation, FR-003).
pub use l7r_guard::shared::py_text::{py_float_of, py_float_text};

/// `int(text)`: Python's whitespace stripped, a sign, ASCII digits with an underscore only between two.
///
/// # Errors
///
/// `int()`'s `ValueError`.
pub fn py_int(text: &str) -> Result<i128, Raised> {
    let bad = || {
        format!(
            "ValueError: invalid literal for int() with base 10: {}",
            repr(text)
        )
    };
    let t = strip(text);
    let (sign, digits) = match t.strip_prefix('-') {
        Some(rest) => (-1, rest),
        None => (1, t.strip_prefix('+').unwrap_or(t)),
    };
    let b = digits.as_bytes();
    if b.is_empty()
        || !b.iter().enumerate().all(|(i, c)| {
            c.is_ascii_digit()
                || (*c == b'_'
                    && i > 0
                    && b[i - 1].is_ascii_digit()
                    && b.get(i + 1).is_some_and(u8::is_ascii_digit))
        })
    {
        return Err(bad());
    }
    digits
        .replace('_', "")
        .parse::<i128>()
        .map(|n| sign * n)
        .map_err(|_| bad())
}

/// Floats compared as Python compares them (no NaN reaches here).
#[must_use]
pub fn cmp_f(a: f64, b: f64) -> Ordering {
    a.partial_cmp(&b).unwrap_or(Ordering::Equal)
}

/// A `Counter` kept in its insertion order, as the Python's dicts are, so a stable sort over it ties as the Python's did.
#[derive(Clone, Debug, Default)]
pub struct Tally<K> {
    items: Vec<(K, f64)>,
}

impl<K: PartialEq + Clone> Tally<K> {
    /// `counter[key] += by`.
    pub fn add(&mut self, key: &K, by: f64) {
        match self.items.iter_mut().find(|(k, _)| k == key) {
            Some((_, v)) => *v += by,
            None => self.items.push((key.clone(), by)),
        }
    }

    /// `counter[key]`, 0 where it is missing.
    #[must_use]
    pub fn get(&self, key: &K) -> f64 {
        self.items
            .iter()
            .find(|(k, _)| k == key)
            .map_or(0.0, |(_, v)| *v)
    }

    /// The items in insertion order.
    #[must_use]
    pub fn items(&self) -> &[(K, f64)] {
        &self.items
    }

    /// `most_common()`: by count, descending, ties in insertion order.
    #[must_use]
    pub fn most_common(&self) -> Vec<(K, f64)> {
        let mut out = self.items.clone();
        out.sort_by(|a, b| cmp_f(b.1, a.1));
        out
    }

    /// Whether it holds nothing.
    #[must_use]
    pub fn is_empty(&self) -> bool {
        self.items.is_empty()
    }
}

/// `subprocess.run(["git", "-C", root, *args], capture_output=True, text=True)`: its output where git exits 0, else "", read as the
/// Python's text mode reads it (UTF-8, universal newlines).
///
/// # Errors
///
/// No git to run, or output that is not UTF-8: the Python's `FileNotFoundError` and `UnicodeDecodeError`.
pub fn git(root: &Path, args: &[&str]) -> Result<String, Raised> {
    git_with("git", root, args)
}

/// [`git`] run as `program`, so a test can ask for one that is not there.
fn git_with(program: &str, root: &Path, args: &[&str]) -> Result<String, Raised> {
    let done = Command::new(program)
        .arg("-C")
        .arg(root)
        .args(args)
        .output()
        .map_err(|e| format!("FileNotFoundError: {program}: {e}"))?;
    text_of(done)
}

/// A finished run's output as `text=True` reads it: both streams decoded (either undecodable is the raise), the output kept only where
/// it exited 0.
fn text_of(done: Output) -> Result<String, Raised> {
    let text = |b: Vec<u8>| {
        String::from_utf8(b).map_err(|e| format!("UnicodeDecodeError: git's output: {e}"))
    };
    let out = text(done.stdout)?;
    text(done.stderr)?;
    Ok(if done.status.success() {
        universal(&out)
    } else {
        String::new()
    })
}

/// A file as `Path.read_text(encoding="utf-8")` reads it.
///
/// # Errors
///
/// The file cannot be read or is not UTF-8.
pub fn read_text(path: &Path) -> Result<String, Raised> {
    let bytes = std::fs::read(path).map_err(|e| format!("OSError: {}: {e}", path.display()))?;
    String::from_utf8(bytes)
        .map(|t| universal(&t))
        .map_err(|e| format!("UnicodeDecodeError: {}: {e}", path.display()))
}

/// `read_text()` where `is_file()`, else "".
///
/// # Errors
///
/// As [`read_text`].
pub fn text_if_file(path: &Path) -> Result<String, Raised> {
    if path.is_file() {
        read_text(path)
    } else {
        Ok(String::new())
    }
}

/// The names in a directory, sorted, none where it cannot be read (`sorted(dir.glob(...))`'s walk; a glob's `*` takes a dot file too).
#[must_use]
pub fn names(dir: &Path) -> Vec<String> {
    let mut out: Vec<String> = std::fs::read_dir(dir)
        .map(|rd| {
            rd.filter_map(Result::ok)
                .map(|e| e.file_name().to_string_lossy().into_owned())
                .collect()
        })
        .unwrap_or_default();
    out.sort();
    out
}

/// `spec_dir`: the first `specs/NNN-*` entry, `NNN` the feature as `f"{int(feature):03d}"`.
///
/// # Errors
///
/// A feature `int()` cannot read.
pub fn spec_dir(root: &Path, feature: &str) -> Result<Option<PathBuf>, Raised> {
    let prefix = format!("{:03}-", py_int(feature)?);
    Ok(names(&root.join("specs"))
        .into_iter()
        .find(|n| n.starts_with(&prefix))
        .map(|n| root.join("specs").join(n)))
}

/// Every clone's event log for the feature directory `name`, this clone's first (`event_logs`).
#[must_use]
pub fn event_logs(root: &Path, name: &str, clones: &Path) -> Vec<PathBuf> {
    let mut bases = vec![root.to_path_buf()];
    if clones.is_dir() {
        bases.extend(names(clones).into_iter().map(|n| clones.join(n)));
    }
    let mut seen: Vec<PathBuf> = Vec::new();
    let mut real: Vec<PathBuf> = Vec::new();
    for base in bases {
        if !base.join(".git").exists() {
            continue;
        }
        let p = common_git_dir(&base)
            .join("l7r-events")
            .join(format!("{name}.jsonl"));
        let r = std::fs::canonicalize(&p).unwrap_or_else(|_| p.clone());
        if p.is_file() && !real.contains(&r) {
            real.push(r);
            seen.push(p);
        }
    }
    seen
}

/// An event's identity across its sources: by the call's id where it has one, its agent's id otherwise, else its session, kind and second.
#[derive(Hash, PartialEq, Eq)]
enum Key {
    Two(String, String),
    Three(String, String, String),
}

fn key_text(v: &Value) -> String {
    v.to_string()
}

/// `load_events`: the events of every source, deduplicated, in time order, inside [since, until].
///
/// # Errors
///
/// A source that cannot be read, a line or row that is no object, or an event whose time is no text: the Python's raise.
pub fn load_events(
    logs: &[PathBuf],
    transcripts: &[PathBuf],
    since: &str,
    until: &str,
) -> Result<Vec<Event>, Raised> {
    let open = |p: &Path| read_jsonl(p).map_err(|e| format!("OSError: {}: {e}", p.display()));
    let mut rows: Vec<Event> = Vec::new();
    for p in logs {
        for v in open(p)? {
            match v {
                Value::Object(m) => rows.push(m),
                _ => return Err("AttributeError: an event log line is no object".to_owned()),
            }
        }
    }
    for p in transcripts {
        rows.extend(from_transcript(&open(p)?)?);
    }
    let mut seen: HashMap<Key, usize> = HashMap::new();
    let mut out: Vec<Event> = Vec::new();
    for e in rows {
        let t = or_s(&e, "t");
        if t.is_empty()
            || (!since.is_empty() && t.as_str() < since)
            || (!until.is_empty() && t.as_str() > until)
        {
            continue;
        }
        if !get(&e, "t").is_string() {
            return Err("TypeError: an event's time is no text".to_owned());
        }
        let ev = key_text(get(&e, "ev"));
        let key = if on(&e, "id") {
            Key::Two(ev, key_text(get(&e, "id")))
        } else if on(&e, "aid") {
            Key::Two(ev, key_text(get(&e, "aid")))
        } else {
            Key::Three(key_text(get(&e, "sid")), ev, head(&t, 19).to_owned())
        };
        if let std::collections::hash_map::Entry::Vacant(v) = seen.entry(key) {
            v.insert(out.len());
            out.push(e);
        }
    }
    out.sort_by(|a, b| t_text(a).cmp(t_text(b)));
    Ok(out)
}

#[cfg(test)]
pub mod tests;
