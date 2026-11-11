//! A round's findings and their marks.

use serde_json::json;

use super::*;
use crate::record::testkit::put;

#[test]
fn findings_are_read_whole() {
    let numbered = "Verdict: findings\n1. the first numbered finding:\n   - its evidence\n2. **2.** short\n\n- a bullet the numbers pass over\n3. /tmp/l7r-check/x/MANIFEST.md\n# head\n4. a fourth finding long enough\nplain text\n5. ok, passes\n";
    assert_eq!(
        findings_of(numbered),
        vec![
            "the first numbered finding: - its evidence",
            "**2.** short",
            "a fourth finding long enough"
        ]
    );
    let bullets = "- a bullet finding of length\n  continued here\n**VOCABULARY** - a bold one\nFIX M5 - a form fix finding\n- dismissed, ordinary\n";
    assert_eq!(
        findings_of(bullets),
        vec![
            "a bullet finding of length continued here",
            "**VOCABULARY** - a bold one",
            "FIX M5 - a form fix finding"
        ]
    );
    assert_eq!(words("It's A-b, c!"), "it s a b c");
}

#[test]
fn rounds_are_marked_new_repeated_and_reversing() {
    let r1 = "1. 0094: the passage \"twelve letters at least\" is missing\n2. M5 the guess runs long past the band\nNo page holds the size; needs new research.\nEDIT p\n<<<\nkeep these golden words always\n===\nkeep always\n>>>\n";
    let r2 = "1. a fresh claim \"twelve letters at least\" again\n2. 0094 ACCURACY: something else entirely\n3. M5 the guess runs long past the band again\nEDIT p\n<<<\nkeep always\n===\nkeep these golden words always\n>>>\nEDIT p\n<<<\nkeep always now\n===\nkeep these golden words always now\n>>>\nEDIT p\n<<<\ndifferent stuff\n===\ngolden words different\n>>>\nEDIT p\n<<<\nunrelated\n===\nquite unrelated\n>>>\n";
    let r3 = "clean - 0 findings\n1. a pass listed but the round is clean\n";
    let marks = mark_rounds(
        &[r1.to_owned(), r2.to_owned(), r3.to_owned()],
        &[("x".to_owned(), "y".to_owned())],
    );
    assert_eq!(
        marks[0].iter().map(|m| m.0.as_str()).collect::<Vec<_>>(),
        vec!["NEW", "NEW"]
    );
    let second: Vec<&str> = marks[1].iter().map(|m| m.0.as_str()).collect();
    assert_eq!(
        second,
        vec![
            "REPEATED",
            "NEW",
            "REPEATED",
            "REVERSING",
            "REVERSING",
            "REVERSING"
        ]
    );
    assert!(
        marks[1][3].1.contains("undoes an earlier round's fix")
            && marks[1][4].1.contains("adds back words")
            && marks[1][5].1.contains("adds back words")
    );
    assert!(marks[2].is_empty());
    assert_eq!(insertion("", "a"), None);
    assert_eq!(insertion("a c", "a b c"), Some("b".to_owned()));
}

#[test]
fn replies_files_and_edits() {
    let root = crate::checks::scratch("marks-replies");
    put(&root, "r.md", "the kept reply");
    assert_eq!(
        reply_of(&json!({"reply": root.join("r.md").to_string_lossy()})),
        "the kept reply"
    );
    assert_eq!(reply_of(&json!({"reply": "/no/such", "aid": null})), "");
    assert_eq!(reply_of(&json!({"aid": 12})), "");
    assert_eq!(reply_of(&json!({"aid": "none-such"})), "");
    put(
        &root,
        "h/a/b/subagents/agent-x1.jsonl",
        "{\"message\": {\"content\": [{\"type\": \"text\", \"text\": \"from the transcript\"}]}}\n",
    );
    put(&root, "h/a/c/subagents/agent-x1.jsonl", "");
    assert_eq!(
        transcript_of(&root.join("h"), "x1"),
        Some(root.join("h/a/b/subagents/agent-x1.jsonl"))
    );
    assert_eq!(transcript_of(&root.join("h"), "x2"), None);
    put(&root, "research/questions/0094-a.html", "now the words");
    put(&root, "research/questions/0094-a.notes.html", "n");
    assert_eq!(
        subject_files(&root, "q:0094"),
        vec![
            "research/questions/0094-a.html",
            "research/questions/0094-a.notes.html"
        ]
    );
    put(&root, "l7r/diagram/interactive/assets/modals/hamlet/w.md", "About: x\nEntry: research/questions/0094-a.html, research/questions/0777-gone.html\nDrawing: research/questions/0094-a.html\n");
    assert_eq!(
        subject_files(&root, "modal:hamlet/w"),
        vec![
            "l7r/diagram/interactive/assets/modals/hamlet/w.md",
            "research/questions/0094-a.html"
        ]
    );
    assert!(subject_files(&root, "other").is_empty());
    let reply = "EDIT  \n<<<\nthe words\n===\nnow the words\n>>>\nEDIT research/questions/0094-a.html\n<<<\nnot there\n===\nnot there either\n>>>\n";
    assert_eq!(
        last_edits(
            &root,
            reply,
            &[
                "research/questions/0094-a.html".to_owned(),
                "gone".to_owned()
            ]
        ),
        vec![
            "- APPLIED: (its file): 'the words' -> 'now the words'",
            "- NOT APPLIED: research/questions/0094-a.html: 'not there' -> 'not there either'"
        ]
    );
    assert!(transcripts().ends_with(".claude/projects"));
}

#[test]
fn a_reply_from_the_agents_own_transcript() {
    let root = crate::checks::scratch("marks-transcript");
    put(
        &root,
        "h/a/b/subagents/agent-x1.jsonl",
        "{\"message\": {\"content\": [{\"type\": \"text\", \"text\": \"from the transcript\"}]}}\n",
    );
    assert_eq!(
        reply_in(&json!({"aid": "x1"}), &root.join("h")),
        "from the transcript"
    );
}
