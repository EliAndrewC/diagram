use std::io::{Cursor, Write as _};

use serde_json::{json, Value};

use super::{answer, close_cli, serve};

struct Closed;

impl std::io::Write for Closed {
    fn write(&mut self, _: &[u8]) -> std::io::Result<usize> {
        Err(std::io::Error::other("closed"))
    }

    fn flush(&mut self) -> std::io::Result<()> {
        Ok(())
    }
}

fn clone_at(name: &str) -> std::path::PathBuf {
    let d = std::env::temp_dir().join(format!("l7r-gate-door-{}-{name}", std::process::id()));
    let _ = std::fs::remove_dir_all(&d);
    std::fs::create_dir_all(&d).unwrap();
    assert!(std::process::Command::new("git")
        .arg("-C")
        .arg(&d)
        .args(["init", "-q"])
        .status()
        .unwrap()
        .success());
    let root = std::fs::canonicalize(&d).unwrap();
    std::fs::create_dir_all(root.join(".specify")).unwrap();
    std::fs::write(
        root.join(".specify/feature.json"),
        r#"{"feature_directory": "specs/999-x"}"#,
    )
    .unwrap();
    std::fs::create_dir_all(root.join("specs/999-x")).unwrap();
    root
}

#[expect(
    clippy::needless_pass_by_value,
    reason = "the verb's args, read and dropped"
)]
fn ask(verb: &str, args: Value) -> Value {
    answer(verb, args.as_array().unwrap()).unwrap()
}

#[test]
fn each_read_verb_answers_as_json() {
    let root = clone_at("reads");
    let r = root.to_string_lossy().into_owned();
    assert_eq!(ask("load", json!(["/no/such"])), json!({}));
    assert_eq!(
        ask("state_path", json!([r])),
        json!(format!("{r}/.git/checks-open.json"))
    );
    assert_eq!(ask("state_path", json!(["/nonexistent-l7r"])), Value::Null);
    assert_eq!(
        ask("_blocks", json!(["EDIT a\n<<<\nx\n===\ny\n>>>\n"])),
        json!([["a", "x", "y"]])
    );
    assert_eq!(ask("_reply_of", json!(["/x", "said"])), json!("said"));
    assert_eq!(ask("ROUND_CAP", json!([])), json!(2));
    assert_eq!(ask("PAGE_CHECKS", json!([])).as_array().unwrap().len(), 10);
    assert_eq!(
        ask("subject_of_path", json!(["research/questions/0105-x.html"])),
        json!("q:0105")
    );
    assert_eq!(
        ask(
            "notes_of_manifest",
            json!(["ONLY the notes a and the blocks that carry them\n"])
        ),
        json!(["a"])
    );
    assert_eq!(
        ask("subjects_of_manifest", json!(["unit: c:0105 f\n"])),
        json!(["q:0105"])
    );
    assert_eq!(
        ask("feature_dir", json!([r, ""])),
        json!(format!("{r}/specs/999-x"))
    );
    assert_eq!(ask("unit_of", json!(["round:a|b@3"])), json!("a|b"));
    assert_eq!(ask("owed", json!([r])), json!({}));
    assert_eq!(ask("aside", json!([r])), json!([]));
    assert_eq!(ask("rulings", json!([r, ""])), json!({}));
    assert_eq!(ask("_round_no", json!(["x@3"])), json!(3));
    assert_eq!(
        ask("batch_triggers", json!([r, ["round:a@1", 3]])),
        json!(["round:a@1"])
    );
    assert_eq!(
        ask(
            "reversal",
            json!([[{"ev": "PreToolUse", "tool": "Edit", "path": "/f", "old": "A"}], "/f", "B", "A"])
        ),
        json!(true)
    );
    assert_eq!(
        ask("reversal", json!(["bad", "/f", "B", "A"])),
        json!(false)
    );
    assert_eq!(
        ask("fix_hold", json!([format!("{r}/specs/999-x")])),
        json!("")
    );
    assert!(answer("nope", &[]).is_err());
}

#[test]
fn the_write_verbs_and_the_door_loop() {
    let root = clone_at("writes");
    let r = root.to_string_lossy().into_owned();
    assert_eq!(
        ask("trip", json!([r, "ask:x", "ask", "", "why", null, ""])),
        json!(true)
    );
    assert_eq!(
        ask("trip", json!([r, "ask:x", "ask", "", "why", 1.5, ""])),
        json!(false)
    );
    assert!(std::fs::read_to_string(root.join(".git/arbiter-owed.json"))
        .unwrap()
        .contains("ask:x"));
    assert!(answer(
        "trip",
        &[
            json!("/proc/nonexistent/x"),
            json!("ask:x"),
            json!("ask"),
            json!(""),
            json!("why"),
            json!(null),
            json!("")
        ]
    )
    .is_err());
    assert_eq!(
        ask("record_answer", json!([r, "c", ["c:0105"]])),
        Value::Null
    );
    assert_eq!(
        ask("keep_batches", json!([r, {"modal-form": ["a", "b"]}])),
        Value::Null
    );
    let kept: Value = serde_json::from_str(
        &std::fs::read_to_string(root.join(".git/modal-batches.json")).unwrap(),
    )
    .unwrap();
    assert_eq!(kept["batches"], json!({"modal-form": ["a", "b"]}));
    assert!(answer("keep_batches", &[json!("/proc/nonexistent/x"), json!({})]).is_err());
    let mut w = Closed;
    assert!(w.flush().is_ok());
    let mut out = Vec::new();
    let reply = serve(
        &mut Cursor::new("\n{\"verb\": \"ROUND_CAP\"}\n{\"verb\": \"nope\"}\n"),
        &mut out,
    );
    std::fs::remove_file(root.join(".git/modal-batches.json")).unwrap();
    std::fs::create_dir_all(root.join(".git/modal-batches.json")).unwrap();
    assert!(answer("keep_batches", &[json!(r), json!({})]).is_err());
    std::fs::remove_dir(root.join(".git/modal-batches.json")).unwrap();
    assert_eq!(reply.code, 0);
    assert_eq!(
        String::from_utf8(out).unwrap(),
        "{\"ok\": 2}\n{\"error\": \"checks-door: no verb nope\"}\n"
    );
    assert_eq!(
        serve(&mut Cursor::new("{\"verb\": \"ROUND_CAP\"}\n"), &mut Closed).code,
        0
    );
}

#[test]
fn close_answers_its_usage_and_its_verdict() {
    assert_eq!(close_cli(&[]).code, 2);
    let one = close_cli(&["s".to_owned(), "x".to_owned()]);
    assert_eq!(one.code, 2);
    let two = close_cli(&["s".to_owned(), "nothing to close here".to_owned()]);
    assert_eq!(two.code, 0);
    assert!(two.stdout.contains("0 silent dispatch(es) on s"));
    let three = close_cli(&[
        "s".to_owned(),
        "nothing to close here".to_owned(),
        "ag".to_owned(),
    ]);
    assert_eq!(three.code, 0);
}

#[test]
fn the_reviews_verbs_answer_through_the_door() {
    let root = clone_at("reviews");
    let path = root.to_string_lossy().into_owned();
    assert_eq!(answer("review_hold", &[json!(path)]).unwrap(), json!(""));
    let owed = answer("review_owed", &[json!(path)]).unwrap();
    assert_eq!(owed[1], json!([]));
    let map = root.join("pool/hamlets/m");
    std::fs::create_dir_all(&map).unwrap();
    std::fs::write(map.join("m.json"), "{}").unwrap();
    let owed = answer("review_owed", &[json!(path)]).unwrap();
    assert_eq!(
        owed[1][0],
        json!({"slug": "settlement-review--m", "check": "settlement-review", "subject": "m", "on": "m", "occasion": "a map new to the pool"})
    );
}
