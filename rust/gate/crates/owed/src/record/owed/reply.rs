//! The reply a check returned, as `make apply-edits` reads it (`apply_edits.reply_of` and `unescaped`, in process since feature 449 T145,
//! where `record-checked --reply` and the claims' reply reading ran it by command): a saved reply, or a transcript's last assistant reply.
//! Split out of `answers.rs`, which re-exports it, to keep that file under the size bar.

use std::path::Path;

use serde_json::Value;

use crate::record::repo::Fail;

/// A report saved inside a task notification has its markup escaped: unescaped only when its markers are (`apply_edits.unescaped`).
#[must_use]
pub fn unescaped(text: &str) -> String {
    if text.contains("&lt;&lt;&lt;") && !text.contains("\n<<<") {
        l7r_guard::shared::html_text::unescape(text)
    } else {
        text.to_owned()
    }
}

/// The report's text, as `make apply-edits` reads one (`apply_edits.reply_of`, in process since feature 449 T145, where it ran by command):
/// the file itself, or the last assistant reply in a transcript (`.jsonl` or `.output`), its text blocks joined.
///
/// # Errors
/// A file that cannot be read, or a transcript line Python could not read (a record, message or block of the wrong kind).
pub fn reply_text(path: &Path) -> Result<String, Fail> {
    let raw =
        std::fs::read(path).map_err(|e| format!("FileNotFoundError: {}: {e}", path.display()))?;
    let text = String::from_utf8_lossy(&raw)
        .replace("\r\n", "\n")
        .replace('\r', "\n");
    let suffix = path
        .file_name()
        .map(|n| n.to_string_lossy().into_owned())
        .unwrap_or_default();
    let suffix = suffix
        .rfind('.')
        .filter(|&i| i > 0)
        .map_or("", |i| &suffix[i..]);
    if suffix != ".jsonl" && suffix != ".output" {
        return Ok(unescaped(&text));
    }
    let bad = |what: &str| format!("AttributeError: {what}");
    let mut last = String::new();
    for line in l7r_guard::shared::checks::reply::py_lines(&text) {
        let Ok(rec) = l7r_guard::shared::pyjson::loads(line) else {
            continue;
        };
        let Value::Object(rec) = rec else {
            return Err(bad("a transcript line is not an object"));
        };
        if rec.get("type").and_then(Value::as_str) != Some("assistant") {
            continue;
        }
        let msg = match rec
            .get("message")
            .filter(|m| l7r_guard::shared::pyjson::truthy(m))
        {
            None => serde_json::Map::new(),
            Some(Value::Object(m)) => m.clone(),
            Some(_) => return Err(bad("a message is not an object")),
        };
        let Some(Value::Array(content)) = msg.get("content") else {
            continue;
        };
        let mut said = String::new();
        for c in content {
            let Value::Object(c) = c else {
                return Err(bad("a content block is not an object"));
            };
            if c.get("type").and_then(Value::as_str) == Some("text") {
                match c.get("text") {
                    None => {}
                    Some(Value::String(t)) => said.push_str(t),
                    Some(_) => {
                        return Err("TypeError: a text block's text is not a string".to_owned())
                    }
                }
            }
        }
        if !said.is_empty() {
            last = said;
        }
    }
    Ok(last)
}

/// A transcript's last reply, as `make apply-edits` reads one: [`reply_text`] of `path` (relative to the working directory).
///
/// # Errors
/// As [`reply_text`].
pub fn reply_of(_root: &Path, path: &str) -> Result<String, Fail> {
    reply_text(Path::new(path))
}
