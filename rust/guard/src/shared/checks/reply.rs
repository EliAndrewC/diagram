//! What a returned check said (from `hm_checks.py`): the reply itself, read off the hook's payload or the agent's transcript, and the EDIT blocks in it the round's apply pass may write.

use std::path::Path;
use std::sync::LazyLock;

use fancy_regex::{Regex, RegexBuilder};
use serde_json::Value;

static EDIT: LazyLock<Regex> = LazyLock::new(|| {
    RegexBuilder::new(
        r"(?sm)^(?P<ind>[ \t]*)EDIT[ \t]+`?(?P<path>[^\n`]+?)`?[ \t]*\n\k<ind><<<\n(?P<old>.*?)\n\k<ind>===\n(?P<new>.*?)\n?\k<ind>>>>[ \t]*$",
    )
    .backtrack_limit(10_000_000)
    .build()
    .unwrap_or_else(|e| unreachable!("{e}"))
});

/// `str.splitlines()`: a line ends at any of Python's line boundaries, not only a newline (a transcript line's raw `\u{2028}` splits it, as the Python read it).
#[must_use]
pub fn py_lines(text: &str) -> Vec<&str> {
    let mut out = Vec::new();
    let mut start = 0;
    let mut chars = text.char_indices().peekable();
    while let Some((i, c)) = chars.next() {
        let ends = matches!(
            c,
            '\n' | '\r'
                | '\x0b'
                | '\x0c'
                | '\x1c'
                | '\x1d'
                | '\x1e'
                | '\u{85}'
                | '\u{2028}'
                | '\u{2029}'
        );
        if ends {
            out.push(&text[start..i]);
            if c == '\r' && chars.peek().is_some_and(|(_, n)| *n == '\n') {
                chars.next();
            }
            start = i + c.len_utf8() + usize::from(c == '\r' && text[i + 1..].starts_with('\n'));
        }
    }
    if start < text.len() {
        out.push(&text[start..]);
    }
    out
}

/// A file read as text, undecodable bytes replaced (`errors="replace"`).
#[must_use]
pub fn read_lossy(path: &Path) -> Option<String> {
    std::fs::read(path)
        .ok()
        .map(|b| String::from_utf8_lossy(&b).into_owned())
}

fn last_text_of(line: &Value) -> Option<String> {
    let content = line.get("message")?.get("content")?.as_array()?;
    content.iter().find_map(|b| {
        (b.get("type").and_then(Value::as_str) == Some("text"))
            .then(|| {
                b.get("text")
                    .and_then(Value::as_str)
                    .filter(|t| !t.is_empty())
            })
            .flatten()
            .map(str::to_owned)
    })
}

/// A returned agent's reply: `last`, else the last text of its own transcript (`hm_checks._reply_of`).
#[must_use]
pub fn reply_of(transcript: &str, last: &str) -> String {
    if !last.is_empty() {
        return last.to_owned();
    }
    let Some(lines) = read_lossy(Path::new(transcript)) else {
        return String::new();
    };
    py_lines(&lines)
        .into_iter()
        .rev()
        .filter_map(|raw| serde_json::from_str::<Value>(raw).ok())
        .find_map(|d| last_text_of(&d))
        .unwrap_or_default()
}

/// `t`, each line losing its indent where it carries it (`hm_checks._blocks`' undent).
fn undent(t: &str, ind: &str) -> String {
    t.split('\n')
        .map(|line| line.strip_prefix(ind).unwrap_or(line))
        .collect::<Vec<_>>()
        .join("\n")
}

/// `(path, old, new)` of every EDIT block of `reply`.
#[must_use]
pub fn blocks(reply: &str) -> Vec<(String, String, String)> {
    EDIT.captures_iter(reply)
        .flatten()
        .map(|m| {
            let ind = m.name("ind").map_or("", |g| g.as_str());
            (
                m.name("path").map_or("", |g| g.as_str()).trim().to_owned(),
                undent(m.name("old").map_or("", |g| g.as_str()), ind),
                undent(m.name("new").map_or("", |g| g.as_str()), ind),
            )
        })
        .collect()
}

/// The reply `make apply-edits FROM=` reads: an agent's transcript (`.jsonl` / `.output`, its last text) or a saved reply.
#[must_use]
#[expect(
    clippy::case_sensitive_file_extension_comparisons,
    reason = "the transcript names Claude Code writes, as `str.endswith` read them"
)]
pub fn reply_file(path: &str) -> String {
    if path.ends_with(".jsonl") || path.ends_with(".output") {
        return reply_of(path, "");
    }
    read_lossy(Path::new(path)).unwrap_or_default()
}

/// The text of an Agent tool's response: its `content` blocks, or a plain string.
#[must_use]
pub fn response_text(resp: &Value) -> String {
    match resp.get("content") {
        Some(Value::String(s)) => s.clone(),
        Some(Value::Array(blocks)) => blocks
            .iter()
            .filter(|b| b.is_object())
            .map(|b| b.get("text").and_then(Value::as_str).unwrap_or(""))
            .collect::<Vec<_>>()
            .join("\n"),
        _ => String::new(),
    }
}

#[cfg(test)]
mod tests {
    use serde_json::json;

    use super::{blocks, reply_file, reply_of, response_text};
    use crate::shared::checks::testkit::dir;

    #[test]
    fn an_edit_block_is_read_with_its_indent_dropped() {
        let reply = "quote-check: 0105 - 1\n\nEDIT `research/questions/0105-x.html`\n<<<\nabout 10 ft\n===\nabout 10 feet\n>>>\n  EDIT a/b.md \n  <<<\n  one\n  two\n  ===\n  three\n  >>>\n";
        let got = blocks(reply);
        assert_eq!(got.len(), 2);
        assert_eq!(
            got[0],
            (
                "research/questions/0105-x.html".to_owned(),
                "about 10 ft".to_owned(),
                "about 10 feet".to_owned()
            )
        );
        assert_eq!(
            got[1],
            (
                "a/b.md".to_owned(),
                "one\ntwo".to_owned(),
                "three".to_owned()
            )
        );
        assert!(blocks("no edit here").is_empty());
    }

    #[test]
    fn a_reply_comes_from_the_message_or_the_transcript() {
        assert_eq!(reply_of("/nonexistent", "said"), "said");
        assert_eq!(reply_of("/nonexistent", ""), "");
        let d = dir("reply");
        let t = d.join("t.jsonl");
        std::fs::write(&t, "{\"message\": {\"content\": [{\"type\": \"text\", \"text\": \"first\"}]}}\nnot json\n{\"message\": {\"content\": [{\"type\": \"tool_use\"}, {\"type\": \"text\", \"text\": \"last\"}]}}\n").unwrap();
        assert_eq!(reply_of(&t.to_string_lossy(), ""), "last");
        assert_eq!(reply_file(&t.to_string_lossy()), "last");
        let saved = d.join("reply.md");
        std::fs::write(&saved, "plain").unwrap();
        assert_eq!(reply_file(&saved.to_string_lossy()), "plain");
        assert_eq!(reply_file("/nonexistent.md"), "");
        let no_text = d.join("n.jsonl");
        std::fs::write(
            &no_text,
            "{\"message\": {\"content\": [{\"type\": \"text\", \"text\": \"\"}]}}\n",
        )
        .unwrap();
        assert_eq!(reply_file(&no_text.to_string_lossy()), "");
    }

    #[test]
    fn lines_split_as_python_splits_them() {
        assert_eq!(
            super::py_lines("a\r\nb\u{2028}c\rd\ne"),
            ["a", "b", "c", "d", "e"]
        );
        assert_eq!(super::py_lines("a\n"), ["a"]);
        assert!(super::py_lines("").is_empty());
    }

    #[test]
    fn a_response_reads_as_text() {
        assert_eq!(response_text(&json!({"content": "x"})), "x");
        assert_eq!(
            response_text(&json!({"content": [{"text": "a"}, {"text": "b"}, 3]})),
            "a\nb"
        );
        assert_eq!(response_text(&json!({"content": 1})), "");
    }
}
