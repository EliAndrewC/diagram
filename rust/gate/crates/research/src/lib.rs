//! The research record's core (feature 449 T144, phase 4's S1, `ask:449-phase4-slices`): the port of `l7r/diagram/interactive/record/`'s
//! reading half and of `interactive/sources.py` and `content.py`, under the Python's module names (`record::split`, `record::store`,
//! `sources`, ...). Nothing calls it in production yet: the Python stays the implementation for its importers until S5 (the record's site),
//! S11 (the Mode A top) or S12 (the pipeline) wires this in, and the slice's proof is the differential replaying the Python's recorded
//! runs against these functions. What the Rust already read of the record is reused, never copied (FR-003): the notes' and originals'
//! patterns and the stored-originals table are `core::record::units`', a cited URL's id and the blocked-domain list the guard's
//! `shared::cited_url` and `shared::blocked`, `html.escape` and `html.unescape` the guard's `shared::html_text`, Python's whitespace its
//! `shared::py_text`.
//!
//! No process cache: the Python's `@cache`, `clear_caches` and the store's `MEMO` are a caller's to keep or drop on its own measurement
//! (`ask:449-T81-slices`); a reader here takes the record's directory and a loaded [`record::questions::Record`] explicitly.

use std::fmt;

pub mod citations;
pub mod content;
pub mod glossary;
pub mod pages;
pub mod prepass;
pub mod pyre;
pub mod record;
pub mod source_pages;
pub mod sources;
pub mod style;
pub mod tools;
pub mod verbatim;

/// A refusal, as the Python raised it: the exception's class name and its message, which every caller prints.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Error {
    pub kind: &'static str,
    pub message: String,
}

impl Error {
    #[must_use]
    pub fn new(kind: &'static str, message: impl Into<String>) -> Self {
        Self {
            kind,
            message: message.into(),
        }
    }
}

impl fmt::Display for Error {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        f.write_str(&self.message)
    }
}

impl From<l7r_shared::blocked::Fault> for Error {
    fn from(f: l7r_shared::blocked::Fault) -> Self {
        Self::new(f.kind, f.message)
    }
}

/// A result of this crate.
pub type Result<T> = std::result::Result<T, Error>;

/// Compiles a pattern the source spells out.
#[must_use]
pub(crate) fn re(pattern: &str) -> fancy_regex::Regex {
    // NO BACKTRACK LIMIT IN PRACTICE (feature 449 T145): Python's `re` has none, and the regex crate's default of a million steps panicked
    // the record-prepass of the whole registry (`SOURCES.html`, a page of about two megabytes) where an `<em>` met no `</em>` and the
    // lazy scan to the end ran past it (observed 2026-11-16, the T145 differential's sweep); a pattern here runs to its answer as Python's did
    l7r_shared::regex::build(pattern).unwrap_or_else(|e| unreachable!("{e}"))
}

static DECIMAL: std::sync::LazyLock<fancy_regex::Regex> =
    std::sync::LazyLock::new(|| re(r"^\p{Nd}\z"));

/// A decimal digit's value, as Python's `int()` reads any of Unicode's: the digits come in runs of ten from a zero, so a digit's value
/// is its distance from the first digit of its run, modulo ten.
#[must_use]
pub fn digit_value(c: char) -> Option<u32> {
    let is_digit = |c: char| {
        DECIMAL
            .is_match(c.encode_utf8(&mut [0; 4]))
            .unwrap_or(false)
    };
    if !is_digit(c) {
        return None;
    }
    let mut start = u32::from(c);
    while start > 0 && char::from_u32(start - 1).is_some_and(is_digit) {
        start -= 1;
    }
    Some((u32::from(c) - start) % 10)
}

/// `Path.resolve()` (`os.path.realpath`): the longest part that exists resolved through its links, the rest joined after it, `.` and
/// `..` read first as the path's own text (feature 449 T145; the guard's `finished_run_hooks::runs::realpath` reads them the same way).
#[must_use]
pub fn resolve(p: &std::path::Path) -> std::path::PathBuf {
    use std::path::{Component, PathBuf};
    let absolute = if p.is_absolute() {
        p.to_path_buf()
    } else {
        std::env::current_dir().unwrap_or_default().join(p)
    };
    let mut clean = PathBuf::new();
    for c in absolute.components() {
        // an absolute path's components hold no `.` (the standard library drops it), so a `..` is the one to read
        if c == Component::ParentDir {
            clean.pop();
        } else {
            clean.push(c.as_os_str());
        }
    }
    // the root always resolves, so the longest part that exists is found
    clean
        .ancestors()
        .find_map(|a| {
            let real = std::fs::canonicalize(a).ok()?;
            let tail = clean.strip_prefix(a).ok()?;
            Some(if tail.as_os_str().is_empty() {
                real
            } else {
                real.join(tail)
            })
        })
        .unwrap_or(clean)
}

/// Python's `\s`, as a regex class body.
pub(crate) use l7r_shared::py_text::SPACE_CLASS;

/// `re.sub(pattern, "", text)`.
pub(crate) fn drop_all(pattern: &fancy_regex::Regex, text: &str) -> String {
    pattern.replace_all(text, "").into_owned()
}

/// Every match of `pattern` in `text`, as `finditer`.
pub(crate) fn caps<'t>(
    pattern: &fancy_regex::Regex,
    text: &'t str,
) -> Vec<fancy_regex::Captures<'t>> {
    pattern
        .captures_iter(text)
        .map_while(std::result::Result::ok)
        .collect()
}

/// A file read as Python's `open(encoding="utf-8").read()`: universal newlines, None where it cannot be read.
pub(crate) fn read(path: &std::path::Path) -> Option<String> {
    l7r_gate_core::record::read_text(path).ok()
}

/// The `(line, column)` text a JSON parse error names, `JSONDecodeError`'s words being the library's (`ask:449-T066-json-message`).
pub(crate) fn json(text: &str) -> std::result::Result<serde_json::Value, String> {
    serde_json::from_str(text).map_err(|e| e.to_string())
}

#[cfg(any(test, feature = "testkit"))]
pub mod fixture;

/// `name.endswith("." + ext)`, case and all as Python compares it: a page's or a fragment's suffix is the record's own spelling, never a
/// user's, so a case-blind test would take a file the Python skips (feature 449 T145).
#[must_use]
pub fn has_ext(name: &str, ext: &str) -> bool {
    name.rsplit_once('.').is_some_and(|(_, e)| e == ext)
}
#[cfg(test)]
mod tests;
