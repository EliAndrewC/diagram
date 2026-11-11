//! What the text checks share with the rest of the gate (feature 449 T92, from `checks.rs` and `checks/spec_figures.rs`): git's text,
//! a scratch directory, Python's line split and `repr`, an extension test, and THE ONE DEFINITION OF A FIGURE (spec D4).

use std::path::Path;
use std::process::Command;
use std::sync::LazyLock;

use fancy_regex::Regex;
pub use l7r_guard::shared::tempdir::TempDir;

pub mod moves;

const UNITS: [&str; 18] = [
    "ft", "m", "km", "ha", "mu", "sq ft", "%", "ms", "s", "min", "minute", "minutes", "h", "MB",
    "MiB", "GB", "GiB", "px",
];

fn re(pattern: &str) -> Regex {
    Regex::new(pattern).unwrap_or_else(|e| unreachable!("{e}"))
}

/// A figure with a unit: the longest unit first, so `minutes` is not read as `m`.
#[must_use]
pub fn figure_source() -> String {
    let mut units: Vec<String> = UNITS.iter().map(|u| u.replace(' ', "\\ ")).collect();
    units.sort_by_key(|u| std::cmp::Reverse(u.len()));
    format!(
        r"(?<![\w.])\d[\d,]*(?:\.\d+)?\s*(?:{})(?![\w-])",
        units.join("|")
    )
}

/// Python's `\\w` holds every numeric character: a figure followed by a superscript (`2,179 px\u{b2}`) is no figure there.
pub static FIGURE: LazyLock<Regex> =
    LazyLock::new(|| re(&figure_source().replace(r"\w", r"\w\p{N}")));
/// A one-shot observation's label.
pub static ONE_SHOT: LazyLock<Regex> = LazyLock::new(|| re(r"(?i)\bobserved \d{4}-\d{2}-\d{2}\b"));

/// `git <args>`'s text; empty where it fails, as the Python's unchecked calls read it.
#[must_use]
pub fn git_text(root: &Path, args: &[&str]) -> String {
    let done = Command::new("git").arg("-C").arg(root).args(args).output();
    done.ok()
        .filter(|o| o.status.success())
        .map_or_else(String::new, |o| {
            String::from_utf8_lossy(&o.stdout).into_owned()
        })
}

/// A scratch directory of this process, `l7r-gate-check-{tag}-{pid}-{seq}`, removed when the value is dropped (feature 449 T101): hold
/// it for as long as the directory is used.
pub fn scratch(tag: &str) -> TempDir {
    TempDir::new(&format!("gate-check-{tag}"))
}

/// Python's `str.splitlines`: a form feed and the Unicode line separators end a line too, so a reported line number agrees.
pub fn py_lines(text: &str) -> impl Iterator<Item = &str> {
    text.split_inclusive([
        '\n', '\r', '\x0b', '\x0c', '\x1c', '\x1d', '\x1e', '\u{85}', '\u{2028}', '\u{2029}',
    ])
    .scan(false, |after_cr, piece| {
        let empty_lf = *after_cr && piece == "\n";
        *after_cr = piece.ends_with('\r');
        Some((empty_lf, piece))
    })
    .filter(|(skip, _)| !skip)
    .map(|(_, piece)| {
        piece.trim_end_matches([
            '\n', '\r', '\x0b', '\x0c', '\x1c', '\x1d', '\x1e', '\u{85}', '\u{2028}', '\u{2029}',
        ])
    })
}

/// A JSON value as Python's `repr` prints it, for a message.
#[must_use]
pub fn py_repr(value: &serde_json::Value) -> String {
    use serde_json::Value;
    match value {
        Value::Null => "None".to_owned(),
        Value::Bool(b) => if *b { "True" } else { "False" }.to_owned(),
        Value::Number(n) => n.to_string(),
        Value::String(s) => {
            let quote = if s.contains('\'') && !s.contains('"') {
                '"'
            } else {
                '\''
            };
            let inner = s.replace('\\', "\\\\").replace('\n', "\\n");
            let inner = if quote == '\'' {
                inner.replace('\'', "\\'")
            } else {
                inner
            };
            format!("{quote}{inner}{quote}")
        }
        Value::Array(rows) => format!(
            "[{}]",
            rows.iter().map(py_repr).collect::<Vec<_>>().join(", ")
        ),
        Value::Object(map) => {
            let pairs: Vec<String> = map
                .iter()
                .map(|(k, v)| format!("{}: {}", py_repr(&Value::from(k.as_str())), py_repr(v)))
                .collect();
            format!("{{{}}}", pairs.join(", "))
        }
    }
}

/// Does this path carry the extension?
#[must_use]
pub fn has_ext(path: &str, ext: &str) -> bool {
    Path::new(path).extension().is_some_and(|e| e == ext)
}

/// The one definition of a figure with a unit, and of a one-shot label (`spec_figures`), for the plan lint.
#[must_use]
pub fn figure_pattern() -> &'static Regex {
    &FIGURE
}

#[must_use]
pub fn one_shot_pattern() -> &'static Regex {
    &ONE_SHOT
}

#[cfg(test)]
mod tests;
