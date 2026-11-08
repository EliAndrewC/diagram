//! The decider on the suite's shapes (`tests/hooks/test-download-copy-hooks.sh`, replayed through the shim, is the verdict).

use serde_json::{json, Value};

use super::{decide, hit};
use crate::protocol::{Answer, Event};
use crate::shared::session::Session;

const F: &str = "/host-l7r-repo/academic-sources/TO-DOWNLOAD.md";

fn event(tool: &str, input: &Value) -> Event {
    crate::shared::log::quiet();
    Event {
        name: "PreToolUse".to_owned(),
        input: json!({"tool_name": tool, "tool_input": input}),
    }
}

fn bash(cmd: &str) -> Option<String> {
    hit(&event("Bash", &json!({"command": cmd})))
}

#[test]
fn a_write_of_the_copy_is_a_hit_and_a_read_is_not() {
    assert_eq!(
        hit(&event("Edit", &json!({"file_path": F}))).as_deref(),
        Some(F)
    );
    assert_eq!(
        hit(&event(
            "Edit",
            &json!({"file_path": "research/to-download.md"})
        )),
        None
    );
    assert!(bash(&format!("echo x >> {F}")).is_some());
    assert!(bash(&format!("cp -f a {F}")).is_some());
    assert!(bash(&format!("Path('{F}').write_text(y)")).is_some());
    assert!(bash(&format!("open('{F}', 'a')")).is_some());
    assert_eq!(bash(&format!("cat {F}")), None);
    assert_eq!(bash(&format!("open('{F}', 'r')")), None);
    assert_eq!(
        hit(&Event {
            name: "PreToolUse".to_owned(),
            input: json!({})
        }),
        None
    );
}

#[test]
fn the_refusal_and_the_escape() {
    let run = |cmd: String| {
        let e = event("Bash", &json!({"command": cmd}));
        decide(&e, &Session::from_input(&e.input))
    };
    let refused =
        |got: &[Answer], words: &str| matches!(got, [Answer::Refuse(t)] if t.contains(words));
    assert!(refused(
        &run(format!("echo x >> {F}")),
        "the GM's copy of the download list"
    ));
    assert!(run(format!(
        "echo x >> {F}  # DOWNLOAD_COPY_OK: the GM asked for this repair"
    ))
    .is_empty());
    assert!(refused(
        &run(format!("echo x >> {F}  # DOWNLOAD_COPY_OK")),
        "with no reason"
    ));
    assert!(run(format!("cat {F}")).is_empty());
    assert!(run("ls".to_owned()).is_empty());
    let file = event("Write", &json!({"file_path": F}));
    assert!(refused(
        &decide(&file, &Session::from_input(&file.input)),
        "the GM's copy"
    ));
    let bare = Event {
        name: "PreToolUse".to_owned(),
        input: json!({"tool_name": "Write", "note": "TO-DOWNLOAD"}),
    };
    assert!(decide(&bare, &Session::from_input(&bare.input)).is_empty());
}
