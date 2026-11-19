//! A page as the index read and cut it (feature 449 T138, `semantic_index.py`'s `strip_html`, `passages`, `fingerprint` and `preview`).
//! Offsets are Python's: characters (code points), not bytes, so a span stored by the Python indexes the same text here.

use std::path::Path;
use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_guard::shared::py_text::is_space;

use crate::{Error, Result, MODEL};

static COMMENT: LazyLock<Regex> = LazyLock::new(|| {
    l7r_guard::shared::regex::build(r"(?s)<!--.*?-->").unwrap_or_else(|e| unreachable!("{e}"))
});
static TAG: LazyLock<Regex> = LazyLock::new(|| {
    l7r_guard::shared::regex::build(r"<[^>]+>").unwrap_or_else(|e| unreachable!("{e}"))
});

/// `path.read_text(encoding="utf-8", errors="replace")`: bad bytes as U+FFFD, `\r\n` and a lone `\r` read as `\n` (universal newlines).
///
/// # Errors
/// The file cannot be read (a folder named `*.txt` among them, as the Python's `read_text` raised).
pub fn read_lossy(path: &Path) -> Result<String> {
    let bytes = std::fs::read(path).map_err(|e| Error(format!("{e}: '{}'", path.display())))?;
    Ok(String::from_utf8_lossy(&bytes)
        .replace("\r\n", "\n")
        .replace('\r', "\n"))
}

/// `re.sub(r"\s+", " ", text)`: each run of Python's whitespace one space, the ends kept.
#[must_use]
pub fn squeeze(text: &str) -> String {
    let mut out = String::with_capacity(text.len());
    let mut space = false;
    for c in text.chars() {
        if is_space(c) {
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

/// A record page's visible text: comments and tags dropped, entities read, whitespace collapsed (`strip_html`).
#[must_use]
pub fn strip_html(text: &str) -> String {
    let text = COMMENT.replace_all(text, " ");
    let text = TAG.replace_all(&text, " ");
    let text = l7r_guard::shared::html_text::unescape(&text);
    l7r_guard::shared::py_text::strip(&squeeze(&text)).to_owned()
}

/// The (start, end) of each passage of `text` (its characters): cut at the last space before `size` characters, or at `size` where a run
/// has none (Japanese and Chinese), so every passage is at most `size` long and together they cover the text.
#[must_use]
pub fn passages(text: &[char], size: usize) -> Vec<(usize, usize)> {
    let mut out = Vec::new();
    let (mut i, n) = (0, text.len());
    while i < n {
        while i < n && is_space(text[i]) {
            i += 1;
        }
        if i >= n {
            break;
        }
        let mut end = (i + size).min(n);
        if end < n {
            let from = i + size / 2;
            let cut = (from..end).rev().find(|&j| text[j] == ' ');
            if let Some(cut) = cut.filter(|&c| c > i) {
                end = cut;
            }
        }
        out.push((i, end));
        i = end;
    }
    out
}

/// A passage's key: the model and its text (`fingerprint`), so a changed passage or a new model is embedded again.
#[must_use]
pub fn fingerprint(text: &str) -> String {
    let mut h = l7r_guard::shared::sha1::hex(format!("{MODEL}\n{text}").as_bytes());
    h.truncate(20);
    h
}

/// `text[start:end]` of `chars`, as Python slices a string.
#[must_use]
pub fn slice(chars: &[char], start: i64, end: i64) -> String {
    let n = i64::try_from(chars.len()).unwrap_or(i64::MAX);
    let at = |v: i64| usize::try_from(if v < 0 { (n + v).max(0) } else { v.min(n) }).unwrap_or(0);
    let (s, e) = (at(start), at(end));
    if s >= e {
        return String::new();
    }
    chars[s..e].iter().collect()
}

/// `s[:width]` in characters.
#[must_use]
pub fn first(s: &str, width: usize) -> String {
    s.chars().take(width).collect()
}

#[cfg(test)]
mod tests;
