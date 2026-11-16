use std::time::{Duration, UNIX_EPOCH};

use serde_json::{json, Value};

use super::{civil, dir_from, python_surrogates, surrogate_escaped, write_at, write_entry, Entry};

#[test]
fn a_firing_is_one_file_with_todays_fields() {
    let d = crate::shared::tempdir::TempDir::new("guard-log");
    let input = json!({"session_id": "sid", "cwd": "/c", "tool_name": "Bash", "transcript_path": "/t", "tool_input": {"command": "ls"}});
    let e = Entry {
        guard: "make-only",
        event: "blocked",
        detail: &"x".repeat(250),
        rule: "",
        context: Some(json!({"why": 1})),
        input: &input,
        session_name: "",
    };
    let at = UNIX_EPOCH + Duration::from_micros(1_794_112_496_123_456);
    let p = write_at(&d, &e, at).unwrap();
    assert!(p
        .file_name()
        .unwrap()
        .to_string_lossy()
        .starts_with("20261108T043456123456-"));
    let v: Value = serde_json::from_str(&std::fs::read_to_string(&p).unwrap()).unwrap();
    assert_eq!(v["utc"], "2026-11-08T04:34:56Z");
    assert_eq!(
        (
            v["rule"].as_str(),
            v["session_name"].as_str(),
            v["command"].as_str()
        ),
        (Some("blocked"), Some("sid"), Some("ls"))
    );
    assert_eq!(v["detail"].as_str().unwrap().len(), 200);
    let bare = json!({});
    let e2 = Entry {
        guard: "g",
        event: "escaped",
        detail: "",
        rule: "r",
        context: None,
        input: &bare,
        session_name: "named",
    };
    let v2: Value =
        serde_json::from_str(&std::fs::read_to_string(write_at(&d, &e2, at).unwrap()).unwrap())
            .unwrap();
    assert_eq!(
        (
            v2["session"].as_str(),
            v2["session_name"].as_str(),
            v2["context"].clone()
        ),
        (Some("unknown"), Some("named"), Value::Null)
    );
    std::fs::write(d.join("a-file"), "").unwrap();
    assert!(write_at(&d.join("a-file"), &e2, at).is_none());
    assert_eq!(civil(951_782_400), (2000, 2, 29, 0, 0, 0), "a leap day");
    assert_eq!(civil(0), (1970, 1, 1, 0, 0, 0));
    assert_eq!(
        dir_from(None, "/h"),
        std::path::Path::new("/h/.claude/guard-log")
    );
    assert_eq!(
        dir_from(Some(String::new()), "/h"),
        std::path::Path::new("/h/.claude/guard-log"),
        // an empty seam is no seam
    );
    assert_eq!(
        dir_from(Some("/x".to_owned()), "/h"),
        std::path::Path::new("/x")
    );
}

/// The entry `guard_log`'s Python wrote, byte for byte: Python's `json.dumps(indent=2)` of these fields in this order.
#[test]
fn the_shells_entry_is_pythons_text() {
    let d = crate::shared::tempdir::TempDir::new("guard-log-text");
    let at = UNIX_EPOCH + Duration::from_secs(1_794_112_496);
    let input = json!({"session_id": 7, "cwd": ["/a"], "tool_name": "", "transcript_path": null,
        "tool_input": {"command": "", "file_path": "caf\u{e9}\u{7f}"}});
    let e = Entry {
        guard: "g",
        event: "blocked",
        detail: "d",
        rule: "",
        context: Some(json!([1, 2.0])),
        input: &input,
        session_name: "",
    };
    let text = std::fs::read_to_string(write_entry(&d, &e, "S", at).unwrap()).unwrap();
    assert_eq!(
        text,
        "{\n  \"utc\": \"2026-11-08T04:34:56Z\",\n  \"guard\": \"g\",\n  \"event\": \"blocked\",\n  \"rule\": \"blocked\",\n  \"session\": 7,\n  \"session_name\": 7,\n  \"cwd\": [\n    \"/a\"\n  ],\n  \"tool\": \"\",\n  \"transcript\": \"\",\n  \"detail\": \"d\",\n  \"command\": \"caf\\u00e9\\u007f\",\n  \"context\": [\n    1,\n    2.0\n  ]\n}"
    );
    // the caller's session where the input names none; `unknown` and `nosession` are none
    let session = |input: &Value, sid: &str| {
        let e = Entry {
            guard: "g",
            event: "e",
            detail: "",
            rule: "",
            context: None,
            input,
            session_name: "",
        };
        let v: Value = serde_json::from_str(
            &std::fs::read_to_string(write_entry(&d, &e, sid, at).unwrap()).unwrap(),
        )
        .unwrap();
        (v["session"].clone(), v["command"].clone(), v["cwd"].clone())
    };
    assert_eq!(session(&json!("not a dict"), "S").0, json!("S"));
    assert_eq!(session(&json!({}), "nosession").0, json!("unknown"));
    assert_eq!(session(&json!({}), "unknown").0, json!("unknown"));
    assert_eq!(session(&json!({"session_id": ""}), "").0, json!("unknown"));
    let odd = json!({"tool_input": [1], "cwd": 0});
    assert_eq!(
        session(&odd, "").1,
        json!(""),
        // a tool_input that is no dict
    );
    assert_eq!(session(&odd, "").2, json!(""), "a zero is false");
    assert_eq!(
        session(&json!({"tool_input": {"command": "ls"}}), "").1,
        json!("ls")
    );
}

#[test]
fn a_byte_utf8_cannot_take_is_written_as_pythons_surrogate() {
    assert_eq!(surrogate_escaped(b"plain"), "plain");
    let cut = surrogate_escaped(b"a\xe2\x82");
    assert_eq!(cut.chars().count(), 3, "each byte one character");
    let mid = surrogate_escaped(b"\xff-\xc3\xa9");
    assert_eq!(mid.chars().count(), 3);
    assert!(mid.ends_with("-\u{e9}"));
    let text = crate::shared::pyjson::dumps(&json!(cut), None, true);
    assert_eq!(python_surrogates(&text), "\"a\\udce2\\udc82\"");
    // an escaped backslash before the same letters, a stand-in below 0x80 and a plain escape are left as they are
    assert_eq!(
        python_surrogates("\"\\\\udbff\\udf80\\udbff\\udf7f\\n\""),
        "\"\\\\udbff\\udf80\\udbff\\udf7f\\n\""
    );
}
