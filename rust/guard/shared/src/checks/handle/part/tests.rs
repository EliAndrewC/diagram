//! The partial read against the whole parse (451 T490): every shape's value and rows, and every hook mode's answer and saved bytes,
//! the same both ways.

use std::path::Path;

use serde_json::{json, Value};

use super::{rows_of, Part, Row, Skip, WHOLE};
use crate::checks::handle::handle;
use crate::checks::testkit::clone_at;
use crate::checks::{falsy, parsed, save};

/// A dispatch's `wave` and `reply` read as their truth, for every kind of JSON value: the truth is `!falsy`, as `concerns` read it.
#[test]
fn a_row_s_truths_are_the_whole_parse_s() {
    let values = [
        "null",
        "true",
        "false",
        "0",
        "1",
        "-1",
        "0.0",
        "-0.0",
        "1.5",
        "\"\"",
        "\"x\"",
        "\"\\u00e9\"",
        "[]",
        "[0]",
        "[[], {}]",
        "{}",
        "{\"a\": 1}",
        "{\"a\": {\"b\": [null]}}",
        "18446744073709551615",
    ];
    for v in values {
        let text = format!(
            r#"{{"dispatches": {{"t": {{"aid": "a", "state": 1, "wave": {v}, "reply": {v}, "t": {v}, "owed": {v}}}}}}}"#
        );
        let part = Part::parse(text.clone(), true);
        let whole: Value = serde_json::from_str(&text).unwrap();
        let d = &whole["dispatches"]["t"];
        assert_eq!(part.rows["t"], Row::of(d), "{v}");
        assert_eq!(part.rows["t"].wave, !falsy(d.get("wave")), "{v}");
        assert!(!part.whole, "{v}");
        assert_eq!(part.rows["t"].state, "", "{v}");
    }
}

/// Every shape the partial read cannot take, or takes in part, ends as the whole parse: its value once whole, and its rows.
#[test]
fn every_shape_reads_as_the_whole_parse() {
    let shapes = [
        "",
        "not json",
        "[]",
        "1",
        "{} x",
        r#"{"dispatches": []}"#,
        r#"{"dispatches": {"a": 1}}"#,
        r#"{"dispatches": {"a": {"x": 1e400}}}"#,
        r#"{"versions": {"s": [1e400]}}"#,
        r#"{"seen": "\ud800"}"#,
        r#"{"dispatches": {"a": {"aid": "x"}, "a": {"aid": "y"}}, "feature": "f"}"#,
        r#"{"dispatches": {"a": {"aid": "x"}}, "dispatches": {"b": {"aid": "z"}}}"#,
        r#"{"dispatches": {"a": {"aid": "x", "aid": 2}}, "versions": {"s": [["b"]]}, "seen": {"q": 1}, "plan_holds": {}}"#,
        r#"{"feature": "f", "feature": "g", "rounds": {"u": 1}}"#,
    ];
    for shape in shapes {
        let want = parsed(shape);
        for rows in [true, false] {
            let mut part = Part::parse(shape.to_owned(), rows);
            let want_rows = rows_of(&want).filter(|_| rows).unwrap_or_default();
            assert_eq!(part.rows, want_rows, "{shape}");
            assert_eq!(part.whole(), &want, "{shape}");
            assert_eq!(part.value(), &want, "{shape}");
        }
    }
}

/// The visitors' words, which serde shows only in an error: the three a shape reaches, and the scan's, which none can.
#[test]
fn each_visitor_says_what_it_expects() {
    let err = |text: &str| serde_json::from_str::<Value>(text).map(|_| ()).err();
    assert!(err("{}").is_none());
    let said = format!("{}", &Skip as &dyn serde::de::Expected);
    assert_eq!(said, "any JSON value");
    for (text, words) in [
        ("[]", "the check state"),
        (r#"{"dispatches": []}"#, "the dispatches"),
        (r#"{"dispatches": {"a": 1}}"#, "a dispatch"),
    ] {
        let mut de = serde_json::Deserializer::from_str(text);
        let got = serde::de::DeserializeSeed::deserialize(super::Top { rows: true }, &mut de);
        assert!(got.err().unwrap().to_string().contains(words), "{text}");
    }
}

const PAGE: &str = "research/questions/0105-x.html";

/// A clone whose state holds a running check on 0105, a pending dispatch, a wave row waiting for its agent, a plan hold, versions
/// and seen, as the clone's state has each.
fn clone(tag: &str) -> crate::tempdir::Held<std::path::PathBuf> {
    crate::log::quiet();
    let root = clone_at(tag);
    std::fs::create_dir_all(root.join("specs/900-a")).unwrap();
    std::fs::write(
        root.join("specs/900-a/plan.md"),
        "# p\n\n## T01 x\n\nbody long enough to hold\n",
    )
    .unwrap();
    std::fs::write(
        root.join("MANIFEST.md"),
        "unit: quote-check:0105.drawing#bath abc\n",
    )
    .unwrap();
    let hold = json!({"feature": "900-a", "task": "T01", "blocks": [], "t": 1000.0, "state": "running", "aid": "agh",
        "root": root.to_string_lossy()});
    let state = json!({"feature": "999-x", "plan_holds": {"h": hold}, "rounds": {"q:0105": {"n": 1}},
        "dispatches": {
            "run": {"check": "quote-check", "subjects": ["q:0105"], "state": "running", "t": 1000.0, "aid": "ag1", "manifest": ""},
            "pend": {"check": "record-format", "subjects": ["q:0200"], "state": "pending", "t": 1000.0, "manifest": ""},
            "wave:w:1": {"check": "record-format", "subjects": ["q:0300"], "state": "pending", "t": 1000.0, "wave": "k", "wave_len": 3}
        },
        "versions": {"q:0105": [["a"]]}, "seen": {"q:0105": ["x"]}});
    save(&root.join(".git/checks-open.json"), &state).unwrap();
    root
}

/// The calls each arm makes, in order: a hold's first Bash call (its save), its end, an Edit of the frozen page, an `apply-edits`, a
/// launch of the pending dispatch, a stranger's return while the wave row waits, the running check's return, a `TaskStop`, an
/// Explore and a spec-fidelity and a counted check's dispatches, and an Edit of a plan.
fn calls(root: &Path) -> Vec<(&'static str, Value)> {
    let bash = |cmd: &str, tid: &str| json!({"cwd": root, "tool_name": "Bash", "tool_use_id": tid, "tool_input": {"command": cmd}});
    let agent = |sub: &str, prompt: String, tid: &str| json!({"cwd": root, "tool_name": "Agent", "tool_use_id": tid, "tool_input": {"subagent_type": sub, "prompt": prompt}});
    let manifest = format!("Read {}", root.join("MANIFEST.md").display());
    vec![
        ("edit", bash("true", "b1")),
        ("after", bash("true", "b1")),
        (
            "edit",
            json!({"cwd": root, "tool_name": "Edit", "tool_input": {"file_path": PAGE, "old_string": "a", "new_string": "b"}}),
        ),
        (
            "edit",
            bash("make apply-edits FROM=/nonexistent/reply.md", "b2"),
        ),
        (
            "launched",
            json!({"cwd": root, "tool_name": "Agent", "tool_use_id": "pend", "tool_input": {},
            "tool_response": {"status": "async_launched", "agentId": "ag2"}}),
        ),
        (
            "returned",
            json!({"cwd": root, "agent_id": "stranger", "hook_event_name": "SubagentStop"}),
        ),
        (
            "returned",
            json!({"cwd": root, "agent_id": "ag1", "agent_type": "quote-check", "last_assistant_message": "q: 1\n"}),
        ),
        (
            "launched",
            json!({"cwd": root, "tool_name": "TaskStop", "tool_input": {"task_id": "ag2"}, "tool_response": {}}),
        ),
        ("dispatch", agent("Explore", "look".to_owned(), "x1")),
        (
            "dispatch",
            agent(
                "spec-fidelity",
                "Read /tmp/b/plan-900-a-T01/MANIFEST.md".to_owned(),
                "sf1",
            ),
        ),
        ("dispatch", agent("quote-check", manifest, "qc1")),
        (
            "edit",
            json!({"cwd": root, "tool_name": "Edit", "tool_input": {"file_path": root.join("specs/900-a/plan.md"),
            "old_string": "body", "new_string": "x"}}),
        ),
        (
            "edit",
            json!({"cwd": root, "tool_name": "Read", "tool_input": {"file_path": PAGE}}),
        ),
    ]
}

/// One arm's answers and the state's bytes after each call, its tree's path written as `<root>`.
fn arm(tag: &str, whole: bool, state: Option<&str>) -> Vec<(String, String)> {
    WHOLE.with(|w| w.set(whole));
    let root = clone(tag);
    let file = root.join(".git/checks-open.json");
    if let Some(text) = state {
        std::fs::write(&file, text).unwrap();
    }
    let here = root.to_string_lossy().into_owned();
    let out = calls(&root)
        .into_iter()
        .map(|(mode, payload)| {
            let said = handle(mode, &payload, Some(1001.0)).replace(&here, "<root>");
            let bytes = std::fs::read_to_string(&file)
                .unwrap_or_default()
                .replace(&here, "<root>");
            (said, bytes)
        })
        .collect();
    WHOLE.with(|w| w.set(false));
    out
}

/// Every hook mode's answer, and the state as saved after it, the same read in part as read whole: so every reader of the file,
/// the gate's among them, reads what it read.
#[test]
fn every_mode_answers_and_saves_as_the_whole_read() {
    let part = arm("part-diff-a", false, None);
    let whole = arm("part-diff-b", true, None);
    assert_eq!(part.len(), whole.len());
    for (i, (p, w)) in part.iter().zip(&whole).enumerate() {
        assert_eq!(p, w, "call {i}");
    }
    assert!(part[2].0.contains("frozen while its checks run"));
    assert!(part.iter().any(|(_, s)| s.contains("\"sf1\"")));
    let bad = arm("part-diff-c", false, Some("not json"));
    assert_eq!(bad, arm("part-diff-d", true, Some("not json")));
}
