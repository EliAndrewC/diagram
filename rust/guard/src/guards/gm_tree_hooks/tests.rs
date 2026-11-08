//! The decider on the suite's shapes (`tests/hooks/test-gm-tree-hooks.sh`, replayed through the shim, is the verdict).

use serde_json::json;

use super::{decide, judge, offending};
use crate::protocol::{Answer, Event};
use crate::shared::session::Session;

const G: &str = "/gm/gm-assistant";

fn event(tool: &str, input: &serde_json::Value, cwd: &str) -> Event {
    crate::shared::log::quiet();
    Event {
        name: "PreToolUse".to_owned(),
        input: json!({"tool_name": tool, "tool_input": input, "cwd": cwd}),
    }
}

fn run(e: &Event) -> Vec<Answer> {
    judge(e, &Session::from_input(&e.input), G, "/h")
}

fn bash(cmd: &str) -> Vec<Answer> {
    run(&event("Bash", &json!({"command": cmd}), "/tmp"))
}

fn refused(got: &[Answer], words: &str) -> bool {
    matches!(got, [Answer::Refuse(t)] if t.contains(words))
}

#[test]
fn a_file_tool_is_refused_in_the_main_tree_and_nowhere_else() {
    let edit = |tool: &str, key: &str, path: &str| run(&event(tool, &json!({key: path}), "/tmp"));
    let got = edit("Edit", "file_path", &format!("{G}/setting/a.md"));
    assert!(
        refused(&got, "main working tree (/gm/gm-assistant/setting/a.md)")
            && refused(&got, "gm-assistant clone")
            && refused(&got, "issue_watch.py open")
    );
    assert!(refused(
        &edit("NotebookEdit", "notebook_path", &format!("{G}/x.ipynb")),
        "main working tree"
    ));
    assert!(edit("Edit", "file_path", &format!("{G}/.clones/m/a.md")).is_empty());
    assert!(edit("Edit", "file_path", "/elsewhere/gm-assistant-notes.md").is_empty());
    assert!(edit("Edit", "file_path", "relative/gm-assistant.md").is_empty());
    assert!(edit("Edit", "other", "gm-assistant").is_empty());
}

#[test]
fn a_bash_write_lands_by_invocation_never_by_mention() {
    assert!(refused(
        &bash(&format!("echo x >> {G}/a.md")),
        "main working tree"
    ));
    assert!(refused(
        &bash(&format!("cp /tmp/a {G}/b")),
        "main working tree"
    ));
    assert!(bash(&format!("grep -rn koku {G}/setting")).is_empty());
    assert!(bash(&format!("cat {G}/a > /tmp/x")).is_empty());
    assert!(bash(&format!("echo x > {G}/.clones/m/a")).is_empty());
    assert!(bash(&format!("git -C {G} commit -m x")).is_empty());
    assert!(bash(&format!("echo 'never edit {G}' > /tmp/n")).is_empty());
    let standing = event(
        "Bash",
        &json!({"command": "echo x > a.md # gm-assistant"}),
        G,
    );
    assert!(refused(&run(&standing), "main working tree ("));
    let other = event("Bash", &json!({"command": "echo x > a.md"}), "/tmp");
    assert_eq!(offending(&other, G, "/h"), None);
    let var = event(
        "Bash",
        &json!({"command": "echo x > $UNSET/gm-assistant"}),
        G,
    );
    assert_eq!(offending(&var, G, "/h"), Some(G.to_owned()));
    let unresolved = event(
        "Bash",
        &json!({"command": "python3 -c 'x' # gm-assistant"}),
        G,
    );
    assert_eq!(offending(&unresolved, G, "/h").as_deref(), Some(G));
}

#[test]
fn the_escape_serves_a_bash_call_with_a_reason() {
    let write = format!("echo x > {G}/a");
    assert!(bash(&format!("{write}  # GM_TREE_OK: the GM asked for this")).is_empty());
    assert!(refused(
        &bash(&format!("{write}  # GM_TREE_OK")),
        "GM_TREE_OK with no reason"
    ));
}

#[test]
fn no_mention_of_the_tree_is_no_business_of_this_guard() {
    assert!(bash("echo hello").is_empty());
    let none = Event {
        name: "PreToolUse".to_owned(),
        input: json!({"tool_name": "Bash", "note": "gm-assistant"}),
    };
    assert!(run(&none).is_empty());
    let e = event("Bash", &json!({"command": "echo gm-assistant"}), "/tmp");
    assert!(decide(&e, &Session::from_input(&e.input)).is_empty());
}
