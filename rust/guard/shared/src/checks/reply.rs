//! What a returned check said (from `hm_checks.py`): the reply itself, read off the hook's payload or the agent's transcript, and the EDIT blocks in it the round's apply pass may write.

use std::path::Path;
use std::sync::LazyLock;

use fancy_regex::Regex;
use serde_json::Value;

static EDIT: LazyLock<Regex> = LazyLock::new(|| {
    crate::regex::build(
        r"(?sm)^(?P<ind>[ \t]*)EDIT[ \t]+(?:\((?P<cat>[A-Za-z][A-Za-z -]*)\)[ \t]+)?`?(?P<path>[^\n`]+?)`?[ \t]*\n\k<ind><<<\n(?P<old>.*?)\n\k<ind>===\n(?P<new>.*?)\n?\k<ind>>>>[ \t]*$",
    )
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

/// The text of one transcript line when the line is the agent's own: an assistant's text block, or the `text` a wave agent hands back through its
/// `StructuredOutput` call.
///
/// A line of another kind (a request blob or a user turn, whose text is a tool's output or the session's instructions) is never the reply: a wave's
/// agent ends on a `StructuredOutput` call with no text block, and the reverse scan took the request blob before it as the reply (449 T349: 334 of
/// the 341 wave replies kept were a truncated manifest view or the MCP instructions, so a check's next round saw no earlier round).
fn last_text_of(line: &Value) -> Option<String> {
    if line
        .get("type")
        .and_then(Value::as_str)
        .is_some_and(|t| t != "assistant")
    {
        return None;
    }
    let content = line.get("message")?.get("content")?.as_array()?;
    let nonempty = |v: Option<&Value>| {
        v.and_then(Value::as_str)
            .filter(|t| !t.is_empty())
            .map(str::to_owned)
    };
    content
        .iter()
        .find_map(|b| match b.get("type").and_then(Value::as_str) {
            Some("text") => nonempty(b.get("text")),
            Some("tool_use")
                if b.get("name").and_then(Value::as_str) == Some("StructuredOutput") =>
            {
                nonempty(b.get("input").and_then(|i| i.get("text")))
            }
            _ => None,
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
    categorized(reply)
        .into_iter()
        .map(|(p, o, n, _)| (p, o, n))
        .collect()
}

/// `(path, old, new, category)` of every EDIT block of `reply`: the category the header names in brackets, `EDIT (LINKS) <path>`,
/// else "" (451 T188).
#[must_use]
pub fn categorized(reply: &str) -> Vec<(String, String, String, String)> {
    EDIT.captures_iter(reply)
        .map_while(Result::ok)
        .map(|m| {
            let g = |k: &str| m.name(k).map_or("", |x| x.as_str());
            let ind = g("ind");
            (
                g("path").trim().to_owned(),
                undent(g("old"), ind),
                undent(g("new"), ind),
                g("cat").trim().to_uppercase(),
            )
        })
        .collect()
}

/// The line a check's finding ends with when it carries no EDIT block - the one form every check agent's contract under
/// `.claude/agents/` gives, and the one [`unread_edits`] reads as no block (451 T228: P7's modal-form reply was refused whole over
/// three of them; the test `every_check_agent_names_the_no_edit_line_the_parser_reads` holds the two sides to each other).
pub const NO_EDIT: &str = "EDIT: none - <why>";

/// The form of an EDIT block, as a refusal of an unread one names it.
pub const EDIT_FORM: &str = "EDIT [(CATEGORY)] <path>, then the lines <<<, the old text, ===, the new text and >>>, each fence at the header's indent (plain text: no bullet or bold, the path alone or in one pair of backticks, the category before it)";

/// Each line of `reply` that is shaped as an EDIT block's header or its `<<<` fence but stands in no block the parser reads
/// (`line N: <text>`), FAIL CLOSED (feature 451 T195, gap audit item 12a). WHY: `` EDIT `p` (TRUTH) `` - its category after the
/// path - matched nothing and was dropped without a word, as were a bulleted or bold header and a fence at another indent; the
/// reader that writes refuses a reply holding one, the line and [`EDIT_FORM`] named. A header-shaped line is one whose first word,
/// past any bullet, quote or bold, is `EDIT` (not `EDITS`, `EDITED`); prose that merely holds the word is no header.
#[must_use]
pub fn unread_edits(reply: &str) -> Vec<String> {
    let spans: Vec<(usize, usize)> = EDIT
        .find_iter(reply)
        .map_while(Result::ok)
        .map(|m| (m.start(), m.end()))
        .collect();
    let mut out = Vec::new();
    let mut at = 0;
    for (i, line) in reply.split('\n').enumerate() {
        let start = at;
        at += line.len() + 1;
        let word = line.trim_start_matches(|c: char| {
            c.is_whitespace() || matches!(c, '-' | '*' | '>' | '#' | '+' | '\u{2022}')
        });
        // [`NO_EDIT`] is the checks' own contract line for a finding with no block (every check agent that writes EDIT blocks): it
        // opens no block, so it is not an unread one (feature 453's check session, 2026-11-24: nine replies were refused whole for
        // it and applied from hand-altered copies; 451 T228, P7's modal-form reply). GUARD_EDIT_OK: fixing a guard that fires on correct work.
        let header = word.strip_prefix("EDIT").is_some_and(|rest| {
            !rest.starts_with(|c: char| c.is_alphanumeric() || c == '_')
                && !rest
                    .trim_start_matches([':', ' ', '*', '`'])
                    .to_lowercase()
                    .starts_with("none")
        });
        if (header || line.trim() == "<<<") && !spans.iter().any(|(s, e)| (*s..*e).contains(&start))
        {
            out.push(format!("line {}: {}", i + 1, line.trim()));
        }
    }
    out
}

/// The checks whose every finding is one of form or wording, never of fact (451 T188, the GM 2026-11-23: "style edits are just a
/// different category of thing than factual inaccuracies"): modal-form's replacement "only rewords" (its contract), record-format's
/// VOCABULARY, SESSION NOTE and HISTORY are how a reader meets the words, record-style is presentation, intro-check a question's opening.
pub const WORDING_CHECKS: [&str; 4] =
    ["modal-form", "record-format", "record-style", "intro-check"];
/// (check, category) of the other checks' wording findings: modal-depiction's LINKS fixes a pointer to a drawing page and states no fact.
const WORDING_CATEGORIES: [(&str, &str); 1] = [("modal-depiction", "LINKS")];

/// Whether an EDIT of `check`'s, of `category`, fixes a fact (and so may re-owe a round and what depends on it) rather than wording
/// (applied once, owing nothing): a category no table names, or none told, is factual, so a mislabel never skips a review (451 T188).
#[must_use]
pub fn factual(check: &str, category: &str) -> bool {
    let cat = category.trim().to_uppercase();
    !(WORDING_CHECKS.contains(&check)
        || WORDING_CATEGORIES
            .iter()
            .any(|(c, k)| *c == check && *k == cat))
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

    use super::{
        blocks, categorized, factual, reply_file, reply_of, response_text, unread_edits, NO_EDIT,
    };
    use crate::checks::testkit::dir;

    /// An EDIT header or fence the parser does not read is named, never dropped (feature 451 T195, gap audit item 12a): the
    /// category after the path, a bullet, bold, a fence at another indent; a block read, prose naming EDIT and `EDITS:` are not.
    #[test]
    fn an_edit_line_the_parser_cannot_read_is_named() {
        for (reply, line) in [
            ("EDIT `l7r/m.md` (TRUTH)\n<<<\na\n===\nb\n>>>\n", 1),
            ("note\n- EDIT l7r/m.md\n<<<\na\n===\nb\n>>>\n", 2),
            ("**EDIT** `l7r/m.md`\n<<<\na\n===\nb\n>>>\n", 1),
            ("EDIT l7r/m.md\n  <<<\na\n===\nb\n>>>\n", 1),
        ] {
            let (got, at) = (unread_edits(reply), format!("line {line}: "));
            assert!(!got.is_empty() && got[0].starts_with(&at), "{reply:?}");
            assert!(blocks(reply).is_empty(), "{reply:?}");
        }
        let fine = "Two EDIT blocks follow.\nEDITS:\nEDIT (LINKS) `l7r/m.md`\n<<<\na\n===\nb\n>>>\n  EDIT l7r/n.md\n  <<<\n  c\n  ===\n  >>>\n";
        assert_eq!(unread_edits(fine), Vec::<String>::new());
        assert_eq!(blocks(fine).len(), 2);
    }

    /// `EDIT: none - <why>`, the contract line of a finding that carries no block, is no unread EDIT - plain, bulleted or bold - and
    /// a real block beside it is still read; a bulleted header naming a path is still refused.
    #[test]
    fn the_contract_line_edit_none_is_not_an_unread_edit() {
        // GUARD_EDIT_OK: the test of a fix to a guard that fired on correct work
        let reply = "FIX 1 needs a source.\nEDIT: none - a source to find\n- EDIT: none - a choice for the GM\n**EDIT: none** - research\nEDIT `l7r/m.md`\n<<<\na\n===\nb\n>>>\n";
        assert_eq!(unread_edits(reply), Vec::<String>::new());
        assert_eq!(blocks(reply).len(), 1);
        assert!(!unread_edits("- EDIT l7r/m.md\n<<<\na\n===\nb\n>>>\n").is_empty());
    }

    /// The reply page session P7's cascade got back from modal-form (2026-11-24), byte for byte: three findings ending
    /// `EDIT: none - <why>` beside three real blocks. `make apply-edits` refused it whole on a build without the contract line's
    /// exemption and the session applied it from a hand-altered copy (451 T228); it reads whole, its three blocks found.
    #[test]
    fn the_p7_modal_form_reply_is_read_whole() {
        let reply = include_str!("reply_p7_modal_form.txt");
        assert_eq!(unread_edits(reply), Vec::<String>::new());
        assert_eq!(blocks(reply).len(), 3);
        assert_eq!(reply.matches("\nEDIT: none - ").count(), 3);
    }

    /// The parser and the agent files agree on how a check says it has no edit (451 T228): every line of a check agent's contract
    /// that names a no-edit line names [`NO_EDIT`] itself, the checks that write EDIT blocks name it, and the parser reads it -
    /// plain, bulleted, indented or bold - as no block.
    #[test]
    fn every_check_agent_names_the_no_edit_line_the_parser_reads() {
        // GUARD_EDIT_OK: the test of the agreement T228 pins
        let named = crate::regex::build(r"(?i)\bEDIT\W{0,4}(none|n/a|no edit)\b").unwrap();
        let agents =
            std::path::Path::new(env!("CARGO_MANIFEST_DIR")).join("../../../.claude/agents");
        let mut naming = Vec::new();
        for entry in std::fs::read_dir(&agents).unwrap() {
            let path = entry.unwrap().path();
            let text = std::fs::read_to_string(&path).unwrap();
            for line in text.lines().filter(|l| named.is_match(l).unwrap()) {
                let at = path.file_name().unwrap().to_string_lossy().into_owned();
                let held = line.contains(NO_EDIT);
                assert!(held, "{at}: no-edit line not `{NO_EDIT}`: {line}");
                naming.push(at);
            }
        }
        naming.sort();
        naming.dedup();
        for check in [
            "entry-drift.md",
            "intro-check.md",
            "modal-depiction.md",
            "modal-form.md",
            "modal-research.md",
            "quote-check.md",
            "record-format.md",
            "record-style.md",
            "source-applicability.md",
            "translation-check.md",
        ] {
            let kept = naming.iter().any(|n| n == check);
            assert!(kept, "{check} no longer names `{NO_EDIT}`");
        }
        let line = NO_EDIT.replace("<why>", "a source to find");
        for reply in [
            line.clone(),
            format!("- {line}"),
            format!("   {line}"),
            format!("**{}** - research", NO_EDIT.split(" - ").next().unwrap()),
        ] {
            let got = unread_edits(&format!("FIX 1 - x\n{reply}\n"));
            assert_eq!(got, Vec::<String>::new(), "{reply:?}");
        }
    }

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
    fn a_wave_agent_s_reply_is_its_structured_output_never_a_request_blob() {
        // the shape of 449 T349's inner-court round: the agent ends on a StructuredOutput call, with a request blob before it
        let d = dir("reply-wave");
        let t = d.join("agent.jsonl");
        std::fs::write(
            &t,
            [
                r#"{"type": "user", "message": {"role": "user", "content": [{"type": "text", "text": "the brief"}]}}"#,
                r#"{"type": "assistant", "message": {"content": [{"type": "text", "text": "an early aside"}]}}"#,
                r#"{"type": "api-request-blob", "message": {"content": [{"type": "text", "text": "[Truncated: PARTIAL view - MANIFEST.md"}]}}"#,
                r#"{"type": "assistant", "message": {"content": [{"type": "tool_use", "name": "StructuredOutput", "input": {"label": "x", "verdict": "COVERAGE 0", "text": "modal-depiction: x - COVERAGE 0"}}]}}"#,
                r#"{"type": "user", "message": {"content": [{"type": "tool_result", "content": "Structured output provided successfully"}]}}"#,
            ]
            .join("\n"),
        )
        .unwrap();
        assert_eq!(
            reply_of(&t.to_string_lossy(), ""),
            "modal-depiction: x - COVERAGE 0"
        );
        // another tool's call, or a StructuredOutput with no text, is not the reply: the scan goes on to the agent's last text
        let other = d.join("other.jsonl");
        std::fs::write(
            &other,
            [
                r#"{"type": "assistant", "message": {"content": [{"type": "text", "text": "said"}]}}"#,
                r#"{"type": "api-request-blob", "message": {"content": [{"type": "text", "text": "blob"}]}}"#,
                r#"{"type": "assistant", "message": {"content": [{"type": "tool_use", "name": "StructuredOutput", "input": {"text": ""}}, {"type": "tool_use", "name": "Read", "input": {"text": "no"}}]}}"#,
            ]
            .join("\n"),
        )
        .unwrap();
        assert_eq!(reply_of(&other.to_string_lossy(), ""), "said");
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

    #[test]
    fn an_edit_s_category_is_read_off_its_header_and_its_path_stays_whole() {
        let reply =
            "EDIT (LINKS) `l7r/m.md`\n<<<\na\n===\nb\n>>>\nEDIT l7r/n.md\n<<<\nc\n===\nd\n>>>\n";
        let got = categorized(reply);
        assert_eq!(got[0].0, "l7r/m.md");
        assert_eq!(got[0].3, "LINKS");
        assert_eq!(got[1].3, "");
        assert_eq!(blocks(reply)[0].0, "l7r/m.md");
    }

    #[test]
    fn only_a_wording_finding_is_not_factual_and_an_untold_one_is() {
        for check in ["modal-form", "record-format", "record-style", "intro-check"] {
            assert!(!factual(check, ""), "{check}");
        }
        assert!(!factual("modal-depiction", "LINKS"));
        assert!(!factual("modal-depiction", "links"));
        for (check, cat) in [
            ("modal-depiction", ""),
            ("modal-depiction", "TRUTH"),
            ("modal-depiction", "COVERAGE"),
            ("modal-accuracy", "LINKS"),
            ("quote-check", ""),
            ("source-reader", ""),
            ("translation-check", ""),
            ("", ""),
        ] {
            assert!(factual(check, cat), "{check} {cat}");
        }
    }
}
