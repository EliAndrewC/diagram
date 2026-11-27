//! The screen against the full parse (feature 451 T383): what it keeps, what it never parses, and the paths JSON spells several ways;
//! and the log read a chunk at a time as bytes (451 T392): every chunk size, a failed read, and a line that is not UTF-8.

use serde_json::{json, Value};

use super::{candidate, needle, replaced, reversal, CHUNK};

/// One log line as the hook's writer writes it (`write_line`: serde's compact text).
fn row(ev: &str, tool: &str, path: &Value, old: &str) -> String {
    json!({"t": "T", "sid": "s", "ev": ev, "tool": tool, "id": "i", "path": path, "old": old, "new": "n"})
        .to_string()
}

/// The `old` digests the parse of EVERY line keeps for `path`: the read before the screen, the oracle.
fn parse_all(text: &str, path: &Value) -> Vec<Value> {
    text.lines()
        .filter_map(|l| serde_json::from_str::<Value>(l.trim()).ok())
        .filter(|e| {
            e.get("ev") == Some(&Value::from("PreToolUse"))
                && e.get("tool") == Some(&Value::from("Edit"))
                && e.get("path") == Some(path)
        })
        .map(|e| e.get("old").cloned().unwrap_or(Value::Null))
        .collect()
}

/// The paths a screen could get wrong: plain, a quote, a backslash, non-ASCII, a control character, DEL, empty, and no string at all.
fn odd_paths() -> Vec<Value> {
    vec![
        json!("/c/docs/usage.md"),
        json!("/c/a \"quoted\" name.md"),
        json!("C:\\clone\\a.md"),
        json!("/c/caf\u{e9}/\u{5c71}.md"),
        json!("/c/tab\there.md"),
        json!("/c/del\u{7f}.md"),
        json!(""),
        Value::Null,
        json!(7),
    ]
}

#[test]
fn only_the_lines_that_could_be_an_edit_of_the_path_are_parsed() {
    let p = json!("/c/docs/usage.md");
    let other = json!("/c/docs/other.md");
    let mut text = String::new();
    for i in 0..40 {
        text.push_str(&row("PreToolUse", "Bash", &p, &format!("b{i}")));
        text.push('\n');
        text.push_str(&row("PreToolUse", "Edit", &other, &format!("o{i}")));
        text.push('\n');
    }
    text.push_str(&row("PreToolUse", "Edit", &p, "A"));
    text.push('\n');
    text.push_str(&row("PostToolUse", "Edit", &p, "post"));
    text.push_str("\nnot json \"Edit\" \"/c/docs/usage.md\"\n");
    text.push_str(&row("PreToolUse", "Write", &p, "w"));
    text.push_str("\n  ");
    text.push_str(&row("PreToolUse", "Edit", &p, "B"));
    text.push_str("  \n");
    let (olds, parsed) = replaced(text.as_bytes(), &p, CHUNK);
    assert_eq!(olds, [json!("A"), json!("B")]);
    assert_eq!(olds, parse_all(&text, &p));
    // the two Edits, the PostToolUse of one and the line that is no JSON; not the 80 lines of another tool or another path, nor the Write
    assert_eq!((parsed, text.lines().count()), (4, 85));
}

#[test]
fn a_path_json_spells_several_ways_is_screened_by_the_tool_alone_and_misses_no_line() {
    let mut text = String::new();
    for p in odd_paths() {
        for (ev, tool) in [
            ("PreToolUse", "Edit"),
            ("PreToolUse", "Bash"),
            ("PostToolUse", "Edit"),
        ] {
            text.push_str(&row(ev, tool, &p, &format!("{p}")));
            text.push('\n');
        }
    }
    // lines another writer could have written: every non-ASCII and the quote as \u escapes, and spaces at the colons
    text.push_str("{\"ev\": \"PreToolUse\", \"tool\": \"Edit\", \"path\": \"/c/caf\\u00e9/\\u5c71.md\", \"old\": \"py\"}\n");
    text.push_str("{\"ev\":\"PreToolUse\",\"tool\":\"Edit\",\"path\":\"/c/a \\u0022quoted\\u0022 name.md\",\"old\":\"u22\"}\n");
    text.push_str("{\"ev\": \"PreToolUse\", \"tool\": \"Edit\", \"path\": \"/c/docs/usage.md\", \"old\": \"spaced\"}\n");
    for p in odd_paths() {
        let (olds, parsed) = replaced(text.as_bytes(), &p, CHUNK);
        assert_eq!(olds, parse_all(&text, &p), "{p}");
        assert!(!olds.is_empty(), "{p}");
        assert!(parsed < text.lines().count(), "{p}: {parsed}");
    }
    let twice = |p: &str| parse_all(&text, &json!(p)).len() == 2;
    assert!(
        twice("/c/caf\u{e9}/\u{5c71}.md")
            && twice("/c/a \"quoted\" name.md")
            && twice("/c/docs/usage.md")
    );
}

#[test]
fn the_needle_is_the_path_only_where_it_has_one_spelling() {
    let needles: Vec<Option<String>> = odd_paths().iter().map(needle).collect();
    let plain = |s: &str| Some(format!("\"{s}\""));
    assert_eq!(
        needles,
        [
            plain("/c/docs/usage.md"),
            None,
            None,
            None,
            None,
            None,
            plain(""),
            None,
            None
        ]
    );
    let line = row("PreToolUse", "Edit", &json!("/c/docs/usage.md"), "A");
    assert!(candidate(&line, Some("\"/c/docs/usage.md\"")));
    assert!(candidate(&line, None));
    assert!(!candidate(&line, Some("\"/c/docs/other.md\"")));
    assert!(!candidate(&line.replace("Edit", "Write"), None));
}

#[test]
fn a_put_back_is_a_reversal_whatever_the_path() {
    for (i, p) in odd_paths().into_iter().enumerate() {
        let d = crate::tempdir::TempDir::new(&format!("guard-events-screen-{i}"));
        let log = d.join("log.jsonl");
        let text = [
            row("PreToolUse", "Edit", &p, "A"),
            row("PreToolUse", "Edit", &json!("/elsewhere"), "Z"),
        ]
        .join("\n");
        std::fs::write(&log, text).unwrap();
        assert!(reversal(&log, &p, &json!("B"), &json!("A")), "{p}");
        assert!(!reversal(&log, &p, &json!("A"), &json!("A")), "{p}");
        assert!(!reversal(&log, &p, &json!("B"), &json!("Z")), "{p}");
        assert!(!reversal(&log, &p, &json!("B"), &json!("")), "{p}");
        let none = d.join("none.jsonl");
        assert!(!reversal(&none, &p, &json!("B"), &json!("A")), "{p}");
    }
}

/// A reader that hands out its text a few bytes at a time, says `Interrupted` before every other read, and fails once `fail_at`
/// bytes are out where that is set.
struct Halting {
    text: Vec<u8>,
    at: usize,
    calls: usize,
    fail_at: Option<usize>,
}

impl std::io::Read for Halting {
    fn read(&mut self, out: &mut [u8]) -> std::io::Result<usize> {
        self.calls += 1;
        if self.calls % 2 == 1 {
            return Err(std::io::ErrorKind::Interrupted.into());
        }
        if self.fail_at.is_some_and(|f| self.at >= f) {
            return Err(std::io::Error::other("the disk went away"));
        }
        let n = out.len().min(7).min(self.text.len() - self.at);
        out[..n].copy_from_slice(&self.text[self.at..self.at + n]);
        self.at += n;
        Ok(n)
    }
}

/// A log whose lines a chunk's edge can cut anywhere: a line longer than most chunks, a `\r\n` ending, spaces round a line, a blank
/// line, and a last Edit with no newline after it.
fn edged(p: &Value) -> String {
    let long = "x".repeat(700);
    [
        row("PreToolUse", "Edit", p, "A"),
        row("PreToolUse", "Bash", p, &long),
        format!("{}\r", row("PreToolUse", "Edit", p, "B")),
        String::new(),
        format!("   {}  ", row("PreToolUse", "Edit", p, &long)),
        row("PreToolUse", "Edit", &json!("/c/other.md"), "Z"),
        row("PreToolUse", "Edit", p, "C"),
    ]
    .join("\n")
}

#[test]
fn the_chunked_read_keeps_the_full_parses_lines_at_every_chunk_size() {
    let mut cases = 0;
    for p in odd_paths() {
        let text = edged(&p);
        let want = parse_all(&text, &p);
        assert_eq!(want.len(), 4, "{p}");
        for chunk in 1..=text.len() + 1 {
            assert_eq!(replaced(text.as_bytes(), &p, chunk).0, want, "{p} {chunk}");
            cases += 1;
        }
    }
    assert!(cases > 9 * 2_000, "{cases}");
}

#[test]
fn an_interrupted_read_is_retried_and_a_failed_one_keeps_the_whole_lines_before_it() {
    let p = json!("/c/docs/usage.md");
    let text = edged(&p);
    let read = |fail_at| {
        let log = Halting {
            text: text.clone().into_bytes(),
            at: 0,
            calls: 0,
            fail_at,
        };
        replaced(log, &p, 64).0
    };
    assert_eq!(read(None), parse_all(&text, &p));
    // failed inside the third line: the first line's Edit is kept, the line the failure cut is not
    let third = text.find("\"B\"").unwrap();
    assert_eq!(read(Some(third)), [json!("A")]);
}

#[test]
fn a_line_that_is_not_utf8_costs_only_itself() {
    let p = json!("/c/docs/usage.md");
    let d = crate::tempdir::TempDir::new("guard-events-not-utf8");
    let log = d.join("log.jsonl");
    let mut bytes = row("PreToolUse", "Edit", &p, "A").into_bytes();
    bytes.extend_from_slice(b"\n{\"ev\":\"PreToolUse\",\"tool\":\"Edit\",\"path\":\"/c/docs/usage.md\",\"old\":\"\xff\"}\n");
    std::fs::write(&log, bytes).unwrap();
    // the earlier Edit's put-back is caught; the whole-string read found nothing in a log holding one bad byte
    assert!(reversal(&log, &p, &json!("B"), &json!("A")));
    let (olds, parsed) = replaced(std::fs::File::open(&log).unwrap(), &p, CHUNK);
    assert_eq!((olds, parsed), (vec![json!("A")], 1));
}
