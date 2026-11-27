//! The reversal tripwire's read of a feature's log (feature 451 T383): whether an Edit puts back text an earlier Edit of the same file
//! replaced (A -> B -> A), asked on every Edit's `PreToolUse`.
//!
//! WHY A SCREEN BEFORE THE PARSE: the read parsed every line of the log as JSON to keep the few that are earlier Edits of this path -
//! 333 ms of every Edit's hook on 2026-11-26, the log 41.0 MB and 156,753 lines, growing 8.1 ms for each MB
//! (`dev/measurements/2026-11-26/edit-hook/t373-results.md`). Each line is now tested as text first ([`candidate`]) and only a
//! line that could be such an Edit is parsed; what a parsed line must say is unchanged, so the screen can only cost a line by
//! dropping it, never add one.
//!
//! THE TRIPWIRE MUST NOT MISS A REVERSAL, so the screen is a SUPERSET of the parse's lines by construction, not by trusting one
//! writer's spelling: JSON spells one string several ways (a quote as `\"` or `"`, `é` raw or as `é`), the parse reads them
//! all as equal, and a search for text does not. So the path's own text is searched for only where it has ONE spelling in every
//! writer that escapes no more than JSON asks or a non-ASCII character - a path of printable ASCII with no quote and no backslash
//! ([`needle`]). Any other path (a quote, a backslash, a control character, non-ASCII, or a path that is no string) is screened by
//! the Edit tool's name alone and its lines parsed as before.

use std::path::Path;

use serde_json::Value;

use super::truthy;

/// The Edit tool's name as a line's JSON holds it, whatever the writer puts around the colon.
const EDIT: &str = "\"Edit\"";

/// The text every log line naming `path` holds, where the path has one JSON spelling; None where it may have several.
fn needle(path: &Value) -> Option<String> {
    let plain = |b: u8| (0x20..0x7f).contains(&b) && b != b'"' && b != b'\\';
    path.as_str()
        .filter(|p| p.bytes().all(plain))
        .map(|p| format!("\"{p}\""))
}

/// Whether a log line could be an Edit of the path whose [`needle`] this is: the screen, before any parse.
fn candidate(line: &str, needle: Option<&str>) -> bool {
    line.contains(EDIT) && needle.is_none_or(|n| line.contains(n))
}

/// The text each earlier Edit of `path` replaced (its `old` digest), from a log's text, and how many lines were parsed to find them.
fn replaced(text: &str, path: &Value) -> (Vec<Value>, usize) {
    let needle = needle(path);
    let mut parsed = 0;
    let olds = text
        .lines()
        .filter(|l| candidate(l, needle.as_deref()))
        .filter_map(|l| {
            parsed += 1;
            serde_json::from_str::<Value>(l.trim()).ok()
        })
        .filter(|e| {
            e.get("ev") == Some(&Value::from("PreToolUse"))
                && e.get("tool") == Some(&Value::from("Edit"))
                && e.get("path") == Some(path)
        })
        .map(|e| e.get("old").cloned().unwrap_or(Value::Null))
        .collect();
    (olds, parsed)
}

/// Whether an Edit of `path` puts back text an earlier Edit of that file replaced (`hm_arbiter.reversal`).
pub(super) fn reversal(log: &Path, path: &Value, old: &Value, new: &Value) -> bool {
    let text = std::fs::read_to_string(log).unwrap_or_default();
    truthy(new) && replaced(&text, path).0.contains(new) && new != old
}

#[cfg(test)]
mod tests;
