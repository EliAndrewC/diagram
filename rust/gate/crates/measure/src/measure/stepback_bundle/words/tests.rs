//! The tools' time, the refused calls and the words of scratch transcript records.

use serde_json::{json, Value};

use super::*;

fn rows(list: &[Value]) -> Vec<Row> {
    list.iter()
        .map(|v| v.as_object().unwrap().clone())
        .collect()
}

fn at(s: u32) -> String {
    format!("2026-11-01T08:{:02}:{:02}Z", s / 60, s % 60)
}

#[expect(
    clippy::needless_pass_by_value,
    reason = "a test row built from a literal"
)]
fn use_at(s: u32, id: &str, name: &str, input: Value) -> Value {
    json!({"type": "assistant", "timestamp": at(s), "message": {"content": [{"type": "tool_use", "id": id, "name": name, "input": input}]}})
}

fn result_at(s: u32, id: &str) -> Value {
    json!({"type": "user", "timestamp": at(s), "message": {"content": [{"type": "tool_result", "tool_use_id": id}]}})
}

fn t(s: u32) -> f64 {
    super::super::super::events::ts(&at(s)).unwrap()
}

#[test]
fn a_command_is_named_by_its_targets_or_its_program() {
    assert_eq!(
        command_key("make -j2 quick && make quick && make done"),
        "make quick+done"
    );
    assert_eq!(command_key("cd /x && FOO=1 BAR=2 ls -l"), "ls");
    assert_eq!(command_key("   "), "?");
}

#[test]
fn the_tools_time_pairs_each_call_with_its_result() {
    let r = rows(&[
        json!({"timestamp": at(0), "isSidechain": true}),
        json!({"type": "user"}),
        json!({"timestamp": at(0), "message": {"content": "x"}}),
        json!({"timestamp": at(0), "message": {"content": [1]}}),
        use_at(
            0,
            "a",
            "Bash",
            json!({"command": "make quick", "run_in_background": true}),
        ),
        use_at(1, "b", "Read", json!("not an object")),
        use_at(2, "c", "Bash", json!({"command": "ls   -l\n x"})),
        result_at(5, "a"),
        result_at(6, "b"),
        result_at(7, "c"),
        result_at(8, "nope"),
        use_at(8, "e", "Bash", json!({"command": "ls"})),
        result_at(9, "e"),
        use_at(10, "f", "Bash", json!({"command": "ls -a"})),
        result_at(19, "f"),
        json!({"type": "assistant", "timestamp": at(20), "message": {"content": [{"type": "tool_use", "name": "Skill"}]}}),
        json!({"type": "user", "timestamp": at(21), "message": {"content": [{"type": "tool_result"}]}}),
        use_at(100, "d", "Bash", json!({"command": "ls"})),
        result_at(101, "d"),
    ]);
    let got = tool_time(&r, t(0), t(60)).unwrap();
    assert!((got.total - 26.0).abs() < 1e-9);
    assert_eq!(got.spent.most_common()[0].0, "ls");
    assert!((got.spent.get(&"make quick [background]".to_owned()) - 5.0).abs() < 1e-9);
    assert_eq!(got.longest["ls"], (9.0, "ls -a".to_owned()));
    assert_eq!(got.count["Skill"], 1);
    assert_eq!(got.count["Read"], 1);
    assert!(tool_time(&rows(&[use_at(0, "a", "Bash", json!("x"))]), 0.0, 1.0).is_err());
    assert!(tool_time(&rows(&[json!({"timestamp": 3})]), 0.0, 1.0).is_err());
}

#[test]
fn a_call_a_hook_refused_is_named() {
    let r = rows(&[
        json!({"type": "user", "message": {"content": [
            {"type": "tool_result", "is_error": true, "tool_use_id": "a", "content": "  PreToolUse: refused"},
            {"type": "tool_result", "is_error": true, "tool_use_id": "b", "content": [{"text": "x hook error: y"}, "s"]},
            {"type": "tool_result", "is_error": true, "tool_use_id": "c", "content": "fine"},
            {"type": "tool_result", "is_error": true},
            {"type": "tool_result", "is_error": true, "content": "PreToolUse: x"},
            {"type": "tool_result", "tool_use_id": "d", "content": "PreToolUse:"},
            "text"
        ]}}),
        json!({"type": "user", "message": {"content": "plain"}}),
        json!({"type": "assistant", "message": 3}),
    ]);
    let got = refused_calls(&r).unwrap();
    assert!(got.contains("a") && got.contains("b") && got.contains("None") && got.len() == 3);
    assert!(refused_calls(&rows(&[json!({"type": "user", "message": {"content": 5}})])).is_err());
    let bad = json!({"type": "user", "message": {"content": [{"type": "tool_result", "is_error": true, "content": 5}]}});
    assert!(refused_calls(&rows(&[bad])).is_err());
}

#[test]
fn the_words_name_each_reply_and_call_newest_kept() {
    let r = rows(&[
        json!({"type": "assistant", "isSidechain": true, "timestamp": at(0)}),
        json!({"type": "assistant"}),
        json!({"type": "assistant", "timestamp": at(3599)}),
        json!({"type": "assistant", "timestamp": at(1), "_sid": "0123456789", "message": {"content": [
            {"type": "text", "text": "  hello  "},
            {"type": "text", "text": "   "},
            "x",
            {"type": "tool_use", "id": "r", "name": "Bash", "input": {"command": "rm -rf x"}},
            {"type": "tool_use", "name": "Edit", "input": {"file_path": "f", "old_string": "a'b", "content": "c"}},
            {"type": "tool_use", "name": "Write", "input": {"content": "new"}},
            {"type": "tool_use", "name": "Agent", "input": {}},
            {"type": "tool_use", "id": "r", "name": "Agent", "input": {"subagent_type": "quote-check", "description": "d"}},
            {"type": "tool_use", "name": "Read", "input": "x"}
        ]}}),
        json!({"type": "user", "message": {"content": [{"type": "tool_result", "is_error": true, "tool_use_id": "r", "content": "PreToolUse: no"}]}}),
    ]);
    let text = words(&r, t(0), t(60), WORDS_CAP).unwrap();
    let want = "[08:00 01234567] SAID: hello\n[08:00 01234567] REFUSED RAN: rm -rf x\n[08:00 01234567] EDIT f: \"a'b\" -> 'c'\n[08:00 01234567] WRITE None: '' -> 'new'\n[08:00 01234567] DISPATCHED agent: \n[08:00 01234567] REFUSED DISPATCH quote-check: d";
    assert_eq!(text, want);
    assert!(words(
        &rows(&[use_at(0, "a", "Bash", json!("x"))]),
        0.0,
        t(60),
        WORDS_CAP
    )
    .is_err());
    assert!(words(
        &rows(&[json!({"type": "assistant", "timestamp": at(0), "message": {"content": 4}})]),
        0.0,
        t(60),
        WORDS_CAP
    )
    .is_err());
}

#[test]
fn over_the_cap_commands_shrink_before_anything_is_cut() {
    let long = "x".repeat(100);
    let r = rows(&[
        json!({"type": "assistant", "timestamp": at(1), "message": {"content": [{"type": "text", "text": "said"}]}}),
        use_at(
            2,
            "a",
            "Bash",
            json!({"command": format!("{long}\nsecond line")}),
        ),
    ]);
    let whole = words(&r, t(0), t(60), 10_000).unwrap();
    assert!(whole.contains("second line"));
    let shrunk = words(&r, t(0), t(60), 135).unwrap();
    assert!(!shrunk.contains("second line") && shrunk.starts_with("[08:00] SAID: said\n"));
    let cut = words(&r, t(0), t(60), 30).unwrap();
    assert!(cut.starts_with(CUT) && cut.chars().count() == CUT.chars().count() + 30);
}
