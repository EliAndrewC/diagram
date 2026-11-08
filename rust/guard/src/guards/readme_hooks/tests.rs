//! The decider on the suite's shapes (`tests/hooks/test-readme-hooks.sh`, replayed through the shim, is the verdict).

use serde_json::{json, Value};

use super::{decide, hit};
use crate::protocol::{Answer, Event};
use crate::shared::session::Session;

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
fn a_write_of_a_readme_is_a_hit_and_a_read_or_mention_is_not() {
    assert_eq!(
        hit(&event("Write", &json!({"file_path": "a/README.md"}))).as_deref(),
        Some("a/README.md")
    );
    assert_eq!(
        hit(&event("Edit", &json!({"file_path": "readme"}))).as_deref(),
        Some("readme")
    );
    assert_eq!(
        hit(&event("Write", &json!({"file_path": "a/READMEX.md"}))),
        None
    );
    assert!(bash("echo x > dev/README.md").is_some());
    assert!(bash("sed -i s/a/b/ README.md").is_some());
    assert!(bash("printf x | tee -a docs/README").is_some());
    assert!(bash("cp a README.txt").is_some());
    assert!(bash("Path('x/README.md').write_text(y)").is_some());
    assert_eq!(bash("cat README.md"), None);
    assert_eq!(bash("grep -n x README.md"), None);
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
    let run = |cmd: &str| {
        let e = event("Bash", &json!({"command": cmd}));
        decide(&e, &Session::from_input(&e.input))
    };
    let refused =
        |got: &[Answer], words: &str| matches!(got, [Answer::Refuse(t)] if t.contains(words));
    assert!(refused(
        &run("echo x > README.md"),
        "BLOCKED: writing a README (> README.md)"
    ));
    assert!(run("echo x > README.md  # README_OK: the GM asked for this link table").is_empty());
    assert!(refused(
        &run("echo x > README.md  # README_OK"),
        "with no reason"
    ));
    assert!(run("ls").is_empty());
    let file = event("Write", &json!({"file_path": "README.md"}));
    assert!(refused(
        &decide(&file, &Session::from_input(&file.input)),
        "(README.md)"
    ));
    let none = Event {
        name: "PreToolUse".to_owned(),
        input: json!({"tool_name": "Write"}),
    };
    assert!(decide(&none, &Session::from_input(&none.input)).is_empty());
}
