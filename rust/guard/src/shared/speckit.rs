//! A spec-kit feature's state, what it affects and what holds its landing (feature 330; ported from `scripts/speckit-todo.py` by
//! feature 449 T118, the round arbiter's `ask:449-T83-scope`: "its Rust callers calling it in-process").
//!
//! THE STATE RULE (feature 330 plan D1). A feature is CLOSED when its `tasks.md` holds at least one task and no open one, or when its
//! spec's `**Status**:` value begins with one of [`CLOSING`]. Otherwise it is OPEN: FILED (no tasks yet), PLANNED (tasks, none ticked)
//! or IN PROGRESS (some ticked). A task is a box at column 0 - the form `make tick` writes and `l7r-gate plan` counts; an indented box
//! is part of its task. `Implemented` closes nothing: features say it while holding open tasks, so only the tasks or a closing word
//! decide. A checkbox form this does not read leaves the feature OPEN - a parsing miss shows as open work, never as finished work.
//!
//! WHAT IT AFFECTS, AND THE STAGE FROM THAT (the GM, 2026-10-10). Every open feature names what it affects in an `**Affects**:` line -
//! tags from `.specify/affects.json` - and the stage it is owed at is DERIVED: the earliest stage among its tags (*"If something will be
//! required for both towns and cities, then it is owed at the towns stage"*). An `**Owed at**:` line naming a stage overrides it.
//!
//! WHAT HOLDS A LANDING (feature 405 T32, D4; the GM, 2026-10-20: "I do not want each landing to owe a lands open line"). A feature in
//! progress holds a landing only through the task being worked - the clone's active task (`make task-start`, `.git/active-task`) - while
//! that task is open and the landing does not tick it (`L7R_LAND_TICKS`, the ids `make land` sets). A task nobody has started holds
//! nothing, nor does the GM-review box.
//!
//! WHY HERE, IN THE GUARD (feature 449 T118): `set_down_hooks` asks whether a status line closes a feature and `feature_approval_hooks`
//! reads the same status line and boxes at a past revision, and the guard cannot build on the gate's crates; the gate's CI merge
//! (`ci::features`), the glyph hour (`reviews::glyph`) and `l7r-gate speckit-todo` (the `cohort` crate) build on this one copy (FR-003),
//! as T117 put the review ledger's lint here.
//!
//! The reads keep Python's: a file read as `read_text(errors="replace")` (invalid UTF-8 replaced, `\r\n` and `\r` read as `\n`),
//! `str.splitlines`, `str.strip` and `re`'s `\s` (`py_text`). A read that raised in the Python is an `Err` carrying the reason, which
//! the command prints as the traceback did.

use std::path::{Component, Path, PathBuf};
use std::process::Command;
use std::sync::LazyLock;

use fancy_regex::Regex;
use serde_json::Value;

use crate::shared::py_text::{split, strip, SPACE_CLASS};

/// What a `**Status**:` value begins with when a feature is closed without every task ticked (plan D1, D3).
pub const CLOSING: [&str; 3] = ["done", "superseded by", "withdrawn"];
/// The open states, in the report's order.
pub const STATES: [&str; 4] = [
    "filed",
    "planned",
    "in progress",
    "done - GM review pending",
];
/// When an open feature is owed, in the order the work reaches it (the GM, 2026-10-10).
pub const STAGES: [&str; 5] = ["now", "village", "town", "provincial city", "capital"];
/// The tag vocabulary, relative to the repository root.
pub const AFFECTS: &str = ".specify/affects.json";

fn re(pattern: &str) -> Regex {
    // Python's `\s` and `\S` (the separator characters `\x1c`-`\x1f` included), spelled out for the regex crate
    let pattern = pattern
        .replace(r"\s", &format!("[{SPACE_CLASS}]"))
        .replace(r"\S", &format!("[^{SPACE_CLASS}]"));
    Regex::new(&pattern).unwrap_or_else(|e| unreachable!("{e}"))
}

/// A task box at column 0.
pub static BOX: LazyLock<Regex> = LazyLock::new(|| re(r"(?m)^- \[( |x|X)\] "));
/// The status line, in either bold form.
pub static STATUS: LazyLock<Regex> =
    LazyLock::new(|| re(r"(?m)^\*\*Status\*\*:?\s*(.+)$|^\*\*Status:\*\*\s*(.+)$"));
static OWED: LazyLock<Regex> =
    LazyLock::new(|| re(r"(?m)^\*\*Owed at\*\*:?\s*(.+)$|^\*\*Owed at:\*\*\s*(.+)$"));
static AFFECTS_LINE: LazyLock<Regex> =
    LazyLock::new(|| re(r"(?m)^\*\*Affects\*\*:?\s*(.+)$|^\*\*Affects:\*\*\s*(.+)$"));
static TITLE: LazyLock<Regex> =
    LazyLock::new(|| re(r"(?m)^#\s+(?:Feature(?: Specification)?\s*(?:\d+)?\s*[:-]\s*)?(.+)$"));
static TASK_LINE: LazyLock<Regex> = LazyLock::new(|| re(r"^(\s*)- \[([ xX])\] (\S+)"));
static OPEN_LINE: LazyLock<Regex> = LazyLock::new(|| re(r"^\s*- \[ \] (.*)$"));

/// One feature directory's state, tags and stage.
#[derive(Clone, Debug, Default, PartialEq, Eq)]
pub struct Feature {
    pub name: String,
    pub title: String,
    pub state: String,
    pub ticked: usize,
    pub total: usize,
    pub no_spec: bool,
    pub why: String,
    pub owed: String,
    pub affects: Vec<String>,
    pub unknown: Vec<String>,
    /// Feature 375 amendment 1: the session clone this row's state is read from, not yet landed.
    pub clone: String,
}

/// The tags and the stage of each, the aliases, and each later stage's placeholder feature, in the file's order.
#[derive(Clone, Debug, Default, PartialEq, Eq)]
pub struct Vocabulary {
    /// Each tag and its stage (`None` where the file's stage is not a string, which names no stage).
    pub stage: Vec<(String, Option<String>)>,
    pub aliases: Vec<(String, Vec<String>)>,
    pub placeholders: Vec<(String, Value)>,
}

impl Vocabulary {
    /// The tag's entry: its name and its stage, where the vocabulary knows it.
    fn entry(&self, tag: &str) -> Option<&(String, Option<String>)> {
        self.stage.iter().find(|(t, _)| t == tag)
    }

    /// The placeholder feature of a stage, where the file names one.
    #[must_use]
    pub fn placeholder(&self, stage: &str) -> Option<&Value> {
        self.placeholders
            .iter()
            .find(|(s, _)| s == stage)
            .map(|(_, v)| v)
    }
}

/// `Path(text)` as Python reads it: `.` parts and repeated or trailing slashes dropped, the empty path `.`.
#[must_use]
pub fn py_path(text: &str) -> PathBuf {
    let path = Path::new(text);
    let kept: PathBuf = path
        .components()
        .filter(|c| !matches!(c, Component::CurDir))
        .collect();
    if kept.as_os_str().is_empty() {
        PathBuf::from(".")
    } else {
        kept
    }
}

/// `path.parent` as Python reads it: `.` above a relative name, `/` above the root.
#[must_use]
pub fn py_parent(path: &Path) -> PathBuf {
    match path.parent() {
        Some(p) if !p.as_os_str().is_empty() => p.to_path_buf(),
        Some(_) => PathBuf::from("."),
        None => path.to_path_buf(),
    }
}

/// `path.name`: "" for `.` and `/`.
#[must_use]
pub fn py_name(path: &Path) -> String {
    path.file_name()
        .map(|n| n.to_string_lossy().into_owned())
        .unwrap_or_default()
}

/// `str.splitlines()` (Python's line boundaries, the separators `\x0b`, `\x0c`, `\x1c`-`\x1e`, `\x85`, U+2028 and U+2029 among them).
#[must_use]
pub fn splitlines(text: &str) -> Vec<&str> {
    let mut out = Vec::new();
    let mut rest = text;
    while let Some(at) = rest.find(|c: char| {
        matches!(
            c,
            '\n' | '\r' | '\x0b' | '\x0c' | '\x1c'..='\x1e' | '\u{85}' | '\u{2028}' | '\u{2029}'
        )
    }) {
        out.push(&rest[..at]);
        let skip = if rest[at..].starts_with("\r\n") {
            2
        } else {
            rest[at..].chars().next().map_or(1, char::len_utf8)
        };
        rest = &rest[at + skip..];
    }
    if !rest.is_empty() {
        out.push(rest);
    }
    out
}

/// A file as `read_text(errors="replace")` reads it: invalid UTF-8 replaced, every `\r\n` and `\r` a `\n`.
///
/// # Errors
/// What the read raised (a missing file, a directory, no permission).
pub fn read_text(path: &Path) -> Result<String, String> {
    let bytes = std::fs::read(path).map_err(|e| format!("{}: {e}", path.display()))?;
    Ok(String::from_utf8_lossy(&bytes)
        .replace("\r\n", "\n")
        .replace('\r', "\n"))
}

/// The file's text where it is a file, else "".
fn text_if_file(path: &Path) -> Result<String, String> {
    if path.is_file() {
        read_text(path)
    } else {
        Ok(String::new())
    }
}

/// The first capture of a two-form line pattern (`group(1) or group(2)`), or None when the text has no such line.
fn line_value(pattern: &Regex, text: &str) -> Option<String> {
    let caps = pattern.captures(text).ok().flatten()?;
    let got = caps
        .get(1)
        .filter(|m| !m.as_str().is_empty())
        .or_else(|| caps.get(2));
    Some(got.map_or_else(String::new, |m| m.as_str().to_owned()))
}

/// The tags and the stage of each, the aliases and the placeholders, from `.specify/affects.json`; none when the file is absent.
///
/// # Errors
/// What the Python raised: the file unreadable or not JSON, or a tag with no `stage`.
pub fn vocabulary(root: &Path) -> Result<Vocabulary, String> {
    let path = root.join(AFFECTS);
    if !path.is_file() {
        return Ok(Vocabulary::default());
    }
    let bytes = std::fs::read(&path).map_err(|e| format!("{}: {e}", path.display()))?;
    let text = String::from_utf8(bytes).map_err(|e| format!("UnicodeDecodeError: {e}"))?;
    let data: Value =
        serde_json::from_str(&text).map_err(|e| format!("json.decoder.JSONDecodeError: {e}"))?;
    let Value::Object(data) = data else {
        return Err("AttributeError: the vocabulary is not an object".to_owned());
    };
    let mut vocab = Vocabulary::default();
    for (tag, entry) in object(data.get("tags")) {
        let stage = entry
            .get("stage")
            .ok_or_else(|| format!("KeyError: 'stage' (the tag {tag})"))?;
        vocab
            .stage
            .push((tag.clone(), stage.as_str().map(str::to_owned)));
    }
    for (alias, tags) in object(data.get("aliases")) {
        let tags = match tags {
            Value::Array(items) => items
                .iter()
                .map(|t| t.as_str().map_or_else(|| t.to_string(), str::to_owned))
                .collect(),
            Value::String(s) => s.chars().map(String::from).collect(),
            _ => return Err(format!("TypeError: the alias {alias} names no tags")),
        };
        vocab.aliases.push((alias.clone(), tags));
    }
    vocab.placeholders = object(data.get("placeholders"))
        .map(|(k, v)| (k.clone(), v.clone()))
        .collect();
    Ok(vocab)
}

fn object(value: Option<&Value>) -> impl Iterator<Item = (&String, &Value)> {
    value.and_then(Value::as_object).into_iter().flatten()
}

/// The known tags an `**Affects**:` line names (aliases expanded, in order, once each) and the unknown ones.
#[must_use]
pub fn affects(text: &str, vocab: &Vocabulary) -> (Vec<String>, Vec<String>) {
    let line = line_value(&AFFECTS_LINE, text).unwrap_or_default();
    let (mut known, mut unknown) = (Vec::new(), Vec::new());
    for word in line.split(',').map(|w| strip(w).to_lowercase()) {
        if word.is_empty() {
            continue;
        }
        let expanded = vocab
            .aliases
            .iter()
            .find(|(a, _)| *a == word)
            .map_or_else(|| vec![word.clone()], |(_, ts)| ts.clone());
        for tag in expanded {
            let into = if vocab.entry(&tag).is_some() {
                &mut known
            } else {
                &mut unknown
            };
            if !into.contains(&tag) {
                into.push(tag);
            }
        }
    }
    (known, unknown)
}

/// The earliest stage among the tags, "" for none.
#[must_use]
pub fn derived_stage(tags: &[String], vocab: &Vocabulary) -> String {
    tags.iter()
        .filter_map(|t| vocab.entry(t).and_then(|(_, s)| s.as_deref()))
        .filter_map(|s| STAGES.iter().position(|st| *st == s))
        .min()
        .map_or_else(String::new, |i| STAGES[i].to_owned())
}

/// The stage an overriding `**Owed at**:` line names, or "" when there is none or it names no stage (a reason may follow).
#[must_use]
pub fn owed_at(text: &str) -> String {
    let value = line_value(&OWED, text).map_or_else(String::new, |v| strip(&v).to_lowercase());
    STAGES
        .iter()
        .find(|st| {
            value == **st
                || [" ", " -", ","]
                    .iter()
                    .any(|tail| value.starts_with(&format!("{st}{tail}")))
        })
        .map_or_else(String::new, |st| (*st).to_owned())
}

/// The status line's value, stripped, or "" where the spec has none.
fn status_of(text: &str) -> String {
    line_value(&STATUS, text).map_or_else(String::new, |s| strip(&s).to_owned())
}

/// Does a status value open with one of [`CLOSING`]?
#[must_use]
pub fn closes(status: &str) -> bool {
    let lower = status.to_lowercase();
    CLOSING.iter().any(|w| lower.starts_with(w))
}

/// The number before a directory name's first `-`.
fn number_of(name: &str) -> &str {
    name.split('-').next().unwrap_or_default()
}

/// One feature directory's state, tags and stage, from its own files; `vocab` is the tree's.
///
/// # Errors
/// A file that cannot be read.
pub fn feature(d: &Path, vocab: &Vocabulary) -> Result<Feature, String> {
    let spec = d.join("spec.md");
    let text = text_if_file(&spec)?;
    let name = py_name(d);
    let title = TITLE
        .captures(&text)
        .ok()
        .flatten()
        .and_then(|c| c.get(1))
        .map_or_else(
            || {
                name.split_once('-')
                    .map_or(name.as_str(), |(_, t)| t)
                    .to_owned()
            },
            |m| strip(m.as_str()).to_owned(),
        );
    let (state, why, ticked, total) = state_parts(d, &text)?;
    let (known, unknown) = affects(&text, vocab);
    let mut owed = owed_at(&text);
    if owed.is_empty() {
        owed = derived_stage(&known, vocab);
    }
    Ok(Feature {
        name,
        title,
        state,
        ticked,
        total,
        no_spec: !spec.is_file(),
        why,
        owed,
        affects: known,
        unknown,
        clone: String::new(),
    })
}

/// The state rule over the spec's text and the directory's tasks: (state, why, ticked, total).
fn state_parts(d: &Path, spec: &str) -> Result<(String, String, usize, usize), String> {
    let tasks = text_if_file(&d.join("tasks.md"))?;
    let boxes: Vec<bool> = BOX
        .captures_iter(&tasks)
        .filter_map(Result::ok)
        .map(|c| &c[1] != " ")
        .collect();
    let (ticked, total) = (boxes.iter().filter(|b| **b).count(), boxes.len());
    let status = status_of(spec);
    let (state, why) = if closes(&status) {
        ("closed", status)
    } else if total > 0 && ticked == total {
        ("closed", "every task ticked".to_owned())
    } else if total > 0 && ticked + 1 == total && holding(d)?.is_empty() && gm_rows(d)? > 0 {
        // feature 375 FR-012: landed, the GM's box open
        (
            "done - GM review pending",
            format!("make gm-reviewed F={}", number_of(&py_name(d))),
        )
    } else if total == 0 {
        ("filed", String::new())
    } else if ticked == 0 {
        ("planned", String::new())
    } else {
        ("in progress", String::new())
    };
    Ok((state.to_owned(), why, ticked, total))
}

/// One feature directory's state alone - what the glyph hour and the Python callers ask - as the Python's `feature(d).state` read it:
/// the vocabulary of the tree two levels above `d` first, which raised where `.specify/affects.json` was broken and so fails here too
/// (FR-002, the plan review of feature 449 T118, its decision D7); an absent vocabulary reads as none.
///
/// # Errors
/// The vocabulary above `d`, or a file of `d`, that cannot be read.
pub fn state(d: &Path) -> Result<String, String> {
    vocabulary(&py_parent(&py_parent(d)))?;
    state_given_vocabulary(d)
}

/// The state of `d` where the caller has read the vocabulary already (`feature(d, vocab)`): no vocabulary is read.
///
/// # Errors
/// A file of `d` that cannot be read.
pub fn state_given_vocabulary(d: &Path) -> Result<String, String> {
    let text = text_if_file(&d.join("spec.md"))?;
    Ok(state_parts(d, &text)?.0)
}

/// Does the spec's `**Status**:` line open with one of [`CLOSING`]? Only the line - no task is read.
///
/// # Errors
/// A spec that cannot be read.
pub fn closed_by_status(d: &Path) -> Result<bool, String> {
    let spec = d.join("spec.md");
    if !spec.is_file() {
        return Ok(false);
    }
    Ok(closes(&status_of(&read_text(&spec)?)))
}

/// A git command's trimmed output in `dir`, or None where it failed or printed nothing.
fn git_line(dir: &Path, args: &[&str]) -> Option<String> {
    let out = Command::new("git")
        .arg("-C")
        .arg(dir)
        .args(args)
        .output()
        .ok()?;
    let line = strip(&String::from_utf8_lossy(&out.stdout)).to_owned();
    (out.status.success() && !line.is_empty()).then_some(line)
}

/// Python's `str()` of a JSON value, and whether it is truthy.
fn py_str(v: &Value) -> (String, bool) {
    match v {
        Value::Null => ("None".to_owned(), false),
        Value::Bool(b) => ((if *b { "True" } else { "False" }).to_owned(), *b),
        Value::String(s) => (s.clone(), !s.is_empty()),
        Value::Number(n) => {
            let text = crate::shared::pyjson::dumps(v, None, true);
            (text, n.as_f64().is_some_and(|f| f != 0.0))
        }
        Value::Array(a) => (crate::shared::pyjson::dumps(v, None, true), !a.is_empty()),
        Value::Object(o) => (crate::shared::pyjson::dumps(v, None, true), !o.is_empty()),
    }
}

/// The clone's active task (`make task-start`) when it is this feature's, else "".
///
/// # Errors
/// The mark naming a value that is not an object, which the Python's `.get` raised on.
pub fn active_task(d: &Path) -> Result<String, String> {
    let Some(common) = git_line(
        d,
        &["rev-parse", "--path-format=absolute", "--git-common-dir"],
    ) else {
        return Ok(String::new());
    };
    let mark = PathBuf::from(common).join("active-task");
    if !mark.is_file() {
        return Ok(String::new());
    }
    let Ok(text) = std::fs::read(&mark).map(|b| String::from_utf8(b).map_err(|_| ())) else {
        return Err(format!("{}: unreadable", mark.display()));
    };
    let Some(got) = text
        .ok()
        .and_then(|t| serde_json::from_str::<Value>(&t).ok())
    else {
        return Ok(String::new());
    };
    let Value::Object(got) = got else {
        return Err("AttributeError: the active task is not an object".to_owned());
    };
    if got.get("feature").and_then(Value::as_str) != Some(py_name(d).as_str()) {
        return Ok(String::new());
    }
    Ok(got
        .get("task")
        .map(py_str)
        .filter(|(_, truthy)| *truthy)
        .map(|(s, _)| s)
        .unwrap_or_default())
}

/// The GM's open review rows for the feature (`gm-review.jsonl`, plan D12): its GM-review box is shown while there is one. A row the GM
/// has reviewed carries `reviewed`.
///
/// # Errors
/// A file that cannot be read.
pub fn gm_rows(d: &Path) -> Result<usize, String> {
    let text = text_if_file(&d.join("gm-review.jsonl"))?;
    Ok(splitlines(&text)
        .into_iter()
        .filter(|l| !strip(l).is_empty() && !l.contains("\"reviewed\""))
        .count())
}

/// The open box that holds the landing: the clone's active task of this feature, open and not ticked by the landing
/// (`L7R_LAND_TICKS`); every other open box holds nothing (feature 405 D4).
///
/// # Errors
/// A file that cannot be read, or an active-task mark that is not an object.
pub fn holding(d: &Path) -> Result<Vec<String>, String> {
    let tasks = d.join("tasks.md");
    let task = if tasks.is_file() {
        active_task(d)?
    } else {
        String::new()
    };
    let ticks = std::env::var("L7R_LAND_TICKS").unwrap_or_default();
    if task.is_empty() || split(&ticks).contains(&task.as_str()) {
        return Ok(Vec::new());
    }
    let name = py_name(d);
    let number = number_of(&name);
    // `int(number) if number.isdigit()`: an ASCII run of digits, its leading zeros dropped
    let shown = if !number.is_empty() && number.chars().all(|c| c.is_ascii_digit()) {
        number.trim_start_matches('0').to_owned()
    } else {
        name.clone()
    };
    let shown = if shown.is_empty() {
        "0".to_owned()
    } else {
        shown
    };
    let how = format!("land it with make land F={shown} T={task}");
    let text = read_text(&tasks)?;
    let lines = splitlines(&text);
    for (i, line) in lines.iter().enumerate() {
        let Some(m) = TASK_LINE.captures(line).ok().flatten() else {
            continue;
        };
        if &m[3] != task.as_str() {
            continue;
        }
        if &m[2] == " " {
            let title = line.split_once("] ").map_or("", |(_, t)| t);
            return Ok(vec![format!(
                "{}  <- the active task (make task-start), open: {how}",
                strip(title)
            )]);
        }
        // ...or a box nested under its line still open (a research pass): the task is not done (feature 330's indented rule)
        let indent = &m[1];
        for below in &lines[i + 1..] {
            let under = below.starts_with(&format!("{indent} "))
                || below.starts_with(&format!("{indent}\t"));
            if !under || strip(below).is_empty() {
                break;
            }
            if let Some(n) = OPEN_LINE.captures(below).ok().flatten() {
                return Ok(vec![format!(
                    "{}  <- open under the active task {task}: {how}",
                    strip(&n[1])
                )]);
            }
        }
    }
    Ok(Vec::new())
}

/// The feature directories of `specs`, sorted by name; none where `specs` is not a directory.
#[must_use]
pub fn feature_dirs(specs: &Path) -> Vec<PathBuf> {
    let mut dirs: Vec<PathBuf> = std::fs::read_dir(specs)
        .into_iter()
        .flatten()
        .filter_map(Result::ok)
        .map(|e| specs.join(e.file_name()))
        .filter(|p| p.is_dir())
        .collect();
    dirs.sort();
    dirs
}

/// Every feature directory; a tree with no `specs/` has none (the push runs `--check` in any repository).
///
/// # Errors
/// The vocabulary, or a feature's file, that cannot be read.
pub fn features(specs: &Path) -> Result<Vec<Feature>, String> {
    let vocab = vocabulary(&py_parent(specs))?;
    feature_dirs(specs)
        .iter()
        .map(|d| feature(d, &vocab))
        .collect()
}

#[cfg(test)]
mod tests;
