//! The decider over a fixture file (`tests/hooks/test-source-block-hooks.sh`, replayed through the shim, is the verdict).

use serde_json::{json, Value};

use super::{decide, report};
use crate::protocol::{Answer, Event};
use crate::shared::session::Session;

const BLOCK: &str =
    "<!-- SOURCE: GM NOTES - DO NOT MODIFY -->\nThe color of the sky.\n<!-- END SOURCE -->";

fn file(tag: &str, text: &str) -> crate::shared::tempdir::Held<String> {
    crate::shared::log::quiet();
    let dir = crate::shared::tempdir::TempDir::new(&format!("guard-source-{tag}"));
    let path = dir.join("doc.md");
    std::fs::write(&path, text).unwrap();
    let held = path.to_string_lossy().into_owned();
    dir.hold(held)
}

fn run(input: &Value) -> Vec<Answer> {
    let e = Event {
        name: "PreToolUse".to_owned(),
        input: json!({"tool_name": "Edit", "tool_input": input}),
    };
    decide(&e, &Session::from_input(&e.input))
}

fn refused(got: &[Answer], words: &str) -> bool {
    matches!(got, [Answer::Refuse(t)] if t.contains(words))
}

#[test]
fn an_edit_inside_a_block_and_a_write_dropping_one_are_named() {
    let path = file("report", &format!("before\n{BLOCK}\nafter\n"));
    assert!(report(&path, " color of ", "")
        .unwrap()
        .contains("anchor lies inside a SOURCE block"));
    assert_eq!(report(&path, "before", ""), None);
    assert_eq!(report(&path, "  ", ""), None);
    assert!(report(&path, "", "all new")
        .unwrap()
        .contains("change or drop 1 SOURCE block(s)"));
    assert_eq!(report(&path, "", &format!("kept {BLOCK}")), None);
    assert_eq!(report("/no/such", "x", ""), None);
    let plain = file("plain", "nothing protected");
    assert_eq!(report(&plain, "nothing", "all new"), None);
}

#[test]
fn the_refusal_and_the_escape() {
    let path = file("decide", &format!("{BLOCK}\n"));
    assert!(refused(
        &run(&json!({"file_path": path, "old_string": "color"})),
        "the GM's own writing"
    ));
    assert!(run(&json!({"file_path": path, "old_string": "color", "new_string": "color SOURCE_EDIT_OK: the GM asked for this spelling"})).is_empty());
    assert!(refused(
        &run(
            &json!({"file_path": path, "old_string": "color", "new_string": "color SOURCE_EDIT_OK"})
        ),
        "with no reason"
    ));
    assert!(run(&json!({"file_path": path, "old_string": "absent"})).is_empty());
    let bare = Event {
        name: "PreToolUse".to_owned(),
        input: json!({}),
    };
    assert!(decide(&bare, &Session::from_input(&bare.input)).is_empty());
}
