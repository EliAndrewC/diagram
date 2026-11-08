//! The decider on the suite's shapes (`tests/hooks/test-claims-file-hooks.sh`, replayed through the shim, is the verdict).

use serde_json::{json, Value};

use super::{decide, hit};
use crate::protocol::{Answer, Event};
use crate::shared::session::Session;

const F: &str = "research/RESEARCH-CLAIMS.md";

fn event(tool: &str, input: &Value) -> Event {
    Event {
        name: "PreToolUse".to_owned(),
        input: json!({"tool_name": tool, "tool_input": input}),
    }
}

fn bash(cmd: &str) -> Option<String> {
    hit(&event("Bash", &json!({"command": cmd})))
}

#[test]
fn a_file_tool_on_the_sheet_is_a_hit() {
    assert_eq!(
        hit(&event("Read", &json!({"file_path": F}))).as_deref(),
        Some("Read")
    );
    assert_eq!(
        hit(&event("NotebookEdit", &json!({"notebook_path": F}))).as_deref(),
        Some("NotebookEdit")
    );
    assert_eq!(hit(&event("Edit", &json!({"file_path": "other.md"}))), None);
    assert_eq!(
        hit(&Event {
            name: "PreToolUse".to_owned(),
            input: json!({"tool_name": "Read"})
        }),
        None
    );
    assert_eq!(
        hit(&event("Grep", &json!({"command": format!("cat {F}")}))),
        None
    );
}

#[test]
fn a_bash_command_that_touches_the_file_is_a_hit_and_a_mention_is_not() {
    assert_eq!(bash(&format!("cat {F}")).as_deref(), Some("Bash"));
    assert_eq!(bash(&format!("echo x >> {F}")).as_deref(), Some("Bash"));
    assert_eq!(
        bash(&format!("make lines FILE={F}")).as_deref(),
        Some("Bash")
    );
    assert_eq!(bash(&format!("ls; grep -n x {F}")).as_deref(), Some("Bash"));
    assert_eq!(bash(&format!("git add {F}")), None);
    assert_eq!(bash("grep -rn RESEARCH-CLAIMS.md docs"), None);
    assert_eq!(bash("grep -c"), None);
    assert_eq!(bash("make research-claims Q=1"), None);
    assert_eq!(bash("echo RESEARCH-CLAIMS"), None);
}

#[test]
fn the_refusal_names_the_tools_and_nothing_else_is_read() {
    crate::shared::log::quiet();
    let e = event("Read", &json!({"file_path": F}));
    let got = decide(&e, &Session::from_input(&e.input));
    assert!(
        matches!(&got[..], [Answer::Refuse(t)] if t.contains("not opened by hand (Read)") && t.contains("make research-claim Q="))
    );
    let other = event("Read", &json!({"file_path": "x"}));
    assert!(decide(&other, &Session::from_input(&other.input)).is_empty());
    let mention = event("Bash", &json!({"command": "echo RESEARCH-CLAIMS"}));
    assert!(decide(&mention, &Session::from_input(&mention.input)).is_empty());
}
