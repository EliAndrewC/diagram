//! The screen against the full parse (feature 451 T383): what it keeps, what it never parses, and the paths JSON spells several ways.

use serde_json::{json, Value};

use super::{candidate, needle, replaced, reversal};

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
    let (olds, parsed) = replaced(&text, &p);
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
        let (olds, parsed) = replaced(&text, &p);
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
