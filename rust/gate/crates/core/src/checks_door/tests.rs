use std::io::{Cursor, Write as _};

use serde_json::{json, Value};

use super::{keep_batches, reply_line, serve_with};

struct Closed;

impl std::io::Write for Closed {
    fn write(&mut self, _: &[u8]) -> std::io::Result<usize> {
        Err(std::io::Error::other("closed"))
    }

    fn flush(&mut self) -> std::io::Result<()> {
        Ok(())
    }
}

fn verbs(verb: &str, args: &[Value]) -> Result<Value, String> {
    match verb {
        "echo" => Ok(json!(args)),
        other => Err(format!("door: no verb {other}")),
    }
}

#[test]
fn a_line_is_answered_by_its_verb_and_the_loop_ends_with_its_input() {
    let mut w = Closed;
    assert!(w.flush().is_ok());
    assert!(reply_line("not json", &verbs).starts_with("{\"error\""));
    assert_eq!(
        reply_line("{\"verb\": \"echo\", \"args\": [\"a\"]}", &verbs),
        "{\"ok\": [\"a\"]}\n"
    );
    let mut out = Vec::new();
    let done = serve_with(
        &mut Cursor::new("\n{\"verb\": \"echo\"}\n{\"verb\": \"nope\"}\n"),
        &mut out,
        &verbs,
    );
    assert_eq!(done.code, 0);
    assert_eq!(
        String::from_utf8(out).unwrap(),
        "{\"ok\": []}\n{\"error\": \"door: no verb nope\"}\n"
    );
    assert_eq!(
        serve_with(&mut Cursor::new("{\"verb\": \"echo\"}\n"), &mut Closed, &verbs).code,
        0
    );
}

#[test]
fn the_batches_are_kept_whole_or_the_failure_named() {
    let d = std::env::temp_dir().join(format!("l7r-gate-core-door-{}", std::process::id()));
    let _ = std::fs::remove_dir_all(&d);
    std::fs::create_dir_all(&d).unwrap();
    assert!(std::process::Command::new("git")
        .arg("-C")
        .arg(&d)
        .args(["init", "-q"])
        .status()
        .unwrap()
        .success());
    keep_batches(&d, &json!({"modal-form": ["a"]})).unwrap();
    let kept: Value =
        serde_json::from_str(&std::fs::read_to_string(d.join(".git/modal-batches.json")).unwrap())
            .unwrap();
    assert_eq!(kept["batches"], json!({"modal-form": ["a"]}));
    assert!(keep_batches(std::path::Path::new("/proc/nonexistent/x"), &json!({})).is_err());
    std::fs::remove_file(d.join(".git/modal-batches.json")).unwrap();
    std::fs::create_dir_all(d.join(".git/modal-batches.json")).unwrap();
    assert!(keep_batches(&d, &json!({})).is_err());
}
