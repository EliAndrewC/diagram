//! The uncited pages, judged once: kept, or recorded as not kept with their reasons (feature 312, FR-006 - FR-011; `scripts/record/uncited.py`
//! and `uncited_imports.py`, ported by feature 449 T147, phase 4's S3b under `ask:449-phase4-slices`).
//!
//! WHY (the GM, 2026-10-02): *"anything that we take the time to actually store a copy of should get a write-up"*, but blog posts and dead
//! ends *"feel like things that we should have a record of. So that we know not to check them next time. But which we don't bother to
//! store the full copy of"* - so *"part of our looking through the backlog of unsighted sources should be applying a filter and that
//! filter can be its own subagent check"*, its reasons *"a simple matter of tagging"*.
//!
//! THE SET (FR-006) is computed, never listed ([`set::uncited_set`]): the ledger's and the page cache's URLs with no archive manifest row,
//! less any URL a registry entry carries, less any URL with a verdict, less a blocked domain; plus the manifest rows that no key and no
//! footnote cite (the three pages captured before the GM held the backfill - the GM: *"their disposition should just be whatever the
//! filter ends up saying"*). THE RULE (FR-007, [`rule`]) decides what needs no judgment, with no agent. THE FILTER (FR-008) is the
//! `source-filter` agent over BUNDLES of whole pages ([`bundles`]). WHERE A VERDICT GOES (FR-010, plan D7): a NOT-KEPT is a line of
//! `research/not-kept.jsonl`, a KEEP a line of the kept list until its write-up exists ([`entries`]); this crate is the one writer of the
//! filter's three lists ([`lists`]). The imported copies (research.md R5) are [`imports`]; the command line is [`cli`].

use std::path::{Path, PathBuf};

use fancy_regex::Regex;

pub use l7r_gate_archive::{Error, Result};
pub use l7r_gate_core::Reply;

pub mod bundles;
pub mod cli;
pub mod dupes;
pub mod entries;
pub mod fetch;
pub mod imports;
pub mod lists;
pub mod random;
pub mod rule;
pub mod set;

#[cfg(test)]
mod testkit;

/// Feature 312's list of the pages kept (the archive's [`l7r_gate_archive::ops::KEPT`], which reads it).
pub const KEPT: &str = l7r_gate_archive::ops::KEPT;
/// The pages not kept, each with its reasons: committed beside the record, union-merged.
pub const NOT_KEPT: &str = l7r_shared::attempts::NOT_KEPT;
/// The import check's lines (research.md R5).
pub const MISFILED: &str = "specs/312-uncited-source-catalog/import-check.jsonl";
/// The registry.
pub const SOURCES: &str = "research/sources";
/// The uncited works' group of the registry.
pub const UNCITED: &str = l7r_shared::attempts::UNCITED;
/// The reasons a page is not kept.
pub const REASONS: [&str; 6] = [
    "off-topic",
    "modern-only",
    "unreliable-kind",
    "no-substance",
    "duplicate",
    "unreadable",
];
/// A page no route reads: its access state (feature 313's vocabulary).
pub const ACCESS: [&str; 4] = ["bot-refused", "down", "gone", "paywalled"];
/// A SHELL: saved text this thin is usually the page's frame, not the page (observed 2026-10-02: a Baidu Baike entry saved as its
/// five-character site name, an ADEAC municipal-history page as ~200 characters of navigation, a frameset's "this page needs frames") -
/// so the fetch reads it again, rendered; and a shell no route improves, under [`EMPTY`] characters, is unreadable rather than judged.
pub const SHELL_CHARS: usize = 600;
pub const EMPTY: usize = 100;

/// A Python pattern, compiled as Python reads it.
pub(crate) fn py(pattern: &str) -> Regex {
    l7r_gate_research::pyre::py(pattern)
}

/// `re.sub(r"\s+", " ", text)`: Python's whitespace, each run one space.
#[must_use]
pub fn squeeze(text: &str) -> String {
    let mut out = String::with_capacity(text.len());
    let mut space = false;
    for c in text.chars() {
        if l7r_shared::py_text::is_space(c) {
            if !space {
                out.push(' ');
            }
            space = true;
        } else {
            out.push(c);
            space = false;
        }
    }
    out
}

/// `str.strip()`.
#[must_use]
pub fn strip(text: &str) -> &str {
    l7r_shared::py_text::strip(text)
}

/// `len(text)`: its characters.
#[must_use]
pub fn chars(text: &str) -> usize {
    text.chars().count()
}

/// `text[:n]`.
#[must_use]
pub fn first(text: &str, n: usize) -> String {
    text.chars().take(n).collect()
}

/// An estimate: a CJK character about a token, anything else about a quarter of one (research.md R3). The CJK characters are the
/// Python's class `[\u3000-\u9fff\uac00-\ud7af\uf900-\ufaff]`.
#[must_use]
pub fn tokens(text: &str) -> usize {
    let c = text
        .chars()
        .filter(|ch| matches!(u32::from(*ch), 0x3000..=0x9fff | 0xac00..=0xd7af | 0xf900..=0xfaff))
        .count();
    c + (chars(text) - c) / 4
}

/// The local date, as the Python's `date.today()` read it.
#[must_use]
pub fn today() -> String {
    l7r_shared::attempts::today()
}

/// The tree whose `research/` holds the record's lists (`attempts.base`: the clone, or `L7R_ATTEMPTS_ROOT`).
#[must_use]
pub fn base(root: &Path) -> PathBuf {
    l7r_shared::attempts::base(root)
}

/// The record's directory a URL is checked against the blocked list by.
#[must_use]
pub fn record_dir(root: &Path) -> PathBuf {
    root.join("research")
}

/// A page's saved text, at any age (`text_of`).
///
/// # Errors
/// A cached file that is not UTF-8, or a `meta.json` the Python's read raised on.
pub fn text_of(home: &Path, url: &str) -> Result<Option<String>> {
    Ok(l7r_gate_research::pages::cached(home, url, 10_000.0, false)?.map(|c| c.text))
}

/// `str.splitlines(keepends=True)`: Python's line boundaries, each line keeping its own.
#[must_use]
pub fn lines_keep(text: &str) -> Vec<&str> {
    let mut out = Vec::new();
    let mut start = 0;
    let mut it = text.char_indices().peekable();
    while let Some((i, c)) = it.next() {
        let end = match c {
            '\r' if it.peek().is_some_and(|(_, n)| *n == '\n') => {
                it.next();
                i + 2
            }
            '\n'
            | '\r'
            | '\x0b'
            | '\x0c'
            | '\x1c'..='\x1e'
            | '\u{85}'
            | '\u{2028}'
            | '\u{2029}' => i + c.len_utf8(),
            _ => continue,
        };
        out.push(&text[start..end]);
        start = end;
    }
    if start < text.len() {
        out.push(&text[start..]);
    }
    out
}

/// `str.splitlines()`.
#[must_use]
pub fn lines(text: &str) -> Vec<&str> {
    l7r_shared::speckit::splitlines(text)
}

/// A file read as `read_text(encoding="utf-8")` (universal newlines).
///
/// # Errors
/// Unreadable (`FileNotFoundError` where it is missing), or not UTF-8.
pub fn read_text(path: &Path) -> Result<String> {
    let bytes = std::fs::read(path).map_err(|e| os_error(&e, path))?;
    let text = String::from_utf8(bytes).map_err(|e| {
        Error::new(
            "UnicodeDecodeError",
            format!("'utf-8' codec can't decode: {e}"),
        )
    })?;
    Ok(text.replace("\r\n", "\n").replace('\r', "\n"))
}

/// A write, as `write_text` made it.
///
/// # Errors
/// The write.
pub fn write_text(path: &Path, text: &str) -> Result<()> {
    std::fs::write(path, text).map_err(|e| os_error(&e, path))
}

/// A directory made with its parents (`mkdir(parents=True, exist_ok=True)`).
///
/// # Errors
/// It cannot be made.
pub fn mkdir(path: &Path) -> Result<()> {
    std::fs::create_dir_all(path).map_err(|e| os_error(&e, path))
}

/// A file removed (`unlink`).
///
/// # Errors
/// It cannot be.
pub fn remove_file(path: &Path) -> Result<()> {
    std::fs::remove_file(path).map_err(|e| os_error(&e, path))
}

/// An I/O failure as the Python's `OSError` family named it.
#[must_use]
pub fn os_error(e: &std::io::Error, path: &Path) -> Error {
    let kind = match e.kind() {
        std::io::ErrorKind::NotFound => "FileNotFoundError",
        std::io::ErrorKind::AlreadyExists => "FileExistsError",
        std::io::ErrorKind::IsADirectory => "IsADirectoryError",
        std::io::ErrorKind::NotADirectory => "NotADirectoryError",
        std::io::ErrorKind::PermissionDenied => "PermissionError",
        _ => "OSError",
    };
    Error::new(
        kind,
        format!(
            "[Errno {}] {}: '{}'",
            e.raw_os_error().unwrap_or(0),
            strerror(e),
            path.display()
        ),
    )
}

/// The C library's words for an error, as Python's `OSError` prints them (Rust appends " (os error N)").
fn strerror(e: &std::io::Error) -> String {
    let s = e.to_string();
    s.rfind(" (os error ")
        .map_or(s.clone(), |i| s[..i].to_owned())
}

/// `json.loads` of a text.
///
/// # Errors
/// Not JSON (`JSONDecodeError`, the library's words: `ask:449-T066-json-message`).
pub fn loads(text: &str) -> Result<serde_json::Value> {
    l7r_shared::pyjson::loads(text).map_err(|e| Error::new("JSONDecodeError", e.to_string()))
}

/// The name of a path (`Path.name`).
#[must_use]
pub fn name_of(path: &Path) -> String {
    path.file_name()
        .map(|n| n.to_string_lossy().into_owned())
        .unwrap_or_default()
}

/// A path's entries in path order, hidden ones too (pathlib's `glob("*")` takes a dot file); none where it is no directory.
#[must_use]
pub fn entries(dir: &Path) -> Vec<PathBuf> {
    l7r_gate_archive::ops::sorted_entries(dir, true)
}

/// `[0-9]*-*.html` (a glob): a name opening with an ASCII digit, with a `-` after it, ending `.html`.
#[must_use]
#[expect(
    clippy::case_sensitive_file_extension_comparisons,
    reason = "the glob's `.html` matched the name's case exactly, as this does"
)]
pub fn numbered_html(name: &str) -> bool {
    name.as_bytes().first().is_some_and(u8::is_ascii_digit)
        && name.len() >= 6
        && name.ends_with(".html")
        && name[1..name.len() - 5].contains('-')
}

/// The registry's entry files: `sorted((base / SOURCES).glob("*/[0-9]*-*.html"))`.
#[must_use]
pub fn registry_files(root: &Path) -> Vec<PathBuf> {
    let mut out: Vec<PathBuf> = entries(&base(root).join(SOURCES))
        .into_iter()
        .flat_map(|d| entries(&d))
        .filter(|f| numbered_html(&name_of(f)))
        .collect();
    out.sort();
    out
}

/// `re.fullmatch(r"\d+-(.+)\.html", name)`'s group: the key of a numbered entry's file name.
#[must_use]
pub fn key_of(name: &str) -> Option<&str> {
    let stem = name.strip_suffix(".html")?;
    let (digits, key) = stem.split_once('-')?;
    let numeric = !digits.is_empty()
        && digits
            .chars()
            .all(|c| l7r_gate_archive::ops::decimal(c).is_some());
    (numeric && !key.is_empty() && !key.contains(['\n'])).then_some(key)
}

/// Every key the registry holds an entry for (`registry_keys`).
#[must_use]
pub fn registry_keys(root: &Path) -> std::collections::BTreeSet<String> {
    registry_files(root)
        .iter()
        .filter_map(|f| key_of(&name_of(f)).map(str::to_owned))
        .collect()
}

/// The files of `dir` named `\d+-<key>.html` exactly (`[f for f in dir.glob(f"*-{key}.html") if re.fullmatch(...)]`), in path order.
#[must_use]
pub fn entry_files(dir: &Path, key: &str) -> Vec<PathBuf> {
    entries(dir)
        .into_iter()
        .filter(|f| key_of(&name_of(f)) == Some(key))
        .collect()
}

#[cfg(test)]
mod tests;
