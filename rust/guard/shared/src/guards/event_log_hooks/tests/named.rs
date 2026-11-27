//! Feature 451 T513: the main session's own line names the tasks its command or dispatch names (`names`), so `make task-time` books
//! the session's calls to them; a builder's line names none, and `task` stays the filing's.

use serde_json::{json, Value};

use super::super::{line, session_names};

fn names(tool: &str, input: &Value, by: Option<&str>) -> Option<Value> {
    let mut p = json!({"hook_event_name": "PreToolUse", "session_id": "s", "tool_name": tool, "tool_use_id": "u", "tool_input": input});
    if let Some(by) = by {
        p["agent_id"] = json!(by);
    }
    line(&p, "T").remove("names")
}

fn bash(command: &str) -> Value {
    json!({ "command": command })
}

/// Every `T=` a command gives, in order and once each, a heredoc's left out; else the done refs it names; an Agent call's
/// description, else its marker line, else its `Blocks:` line; nothing else, and nothing on a builder's line.
#[test]
fn a_session_call_names_the_tasks_its_command_or_dispatch_names() {
    for (cmd, want) in [
        (
            "make builder-brief T=T513,T514 F=451 KIND=fix",
            vec!["T513", "T514"],
        ),
        (
            r#"make land F=451 T="T526 T517" NOTE=x; make tick T=T526"#,
            vec!["T526", "T517"],
        ),
        ("make plan-section T='T9'", vec!["T9"]),
        (
            "c=$(git rev-parse refs/l7r/done/451-T462); make carry COMMIT=$c",
            vec!["T462"],
        ),
        (
            "git rev-parse refs/l7r/done/461-landing-T06 refs/l7r/done/451-T7a",
            vec!["T06", "T7a"],
        ),
        (
            "cat > f <<'X'\nmake land T=T1\nX\nmake carry COMMIT=abc",
            vec![],
        ),
        ("T=$HOME/.cache/x; ls $T", vec![]),
        ("grep -n T513 specs/451/tasks.md", vec![]),
    ] {
        assert_eq!(session_names("Bash", &bash(cmd)), want, "{cmd}");
    }
    let agent = |d: &str, p: &str| session_names("Agent", &json!({"description": d, "prompt": p}));
    assert_eq!(
        agent("451 T5 builder", "BUILDER-BRIEF 451 T6 KIND=fix\nT7"),
        ["T5"]
    );
    assert_eq!(
        agent(
            "a builder",
            "BUILDER-BRIEF 451 T6,T8 KIND=fix\nBlocks: 451 T9"
        ),
        ["T6", "T8"]
    );
    assert_eq!(agent("a review", "Review it.\nBlocks: 451 T9\nT10"), ["T9"]);
    assert!(agent("a review", "Review it.\nBlocks: none").is_empty());
    assert!(session_names("Read", &json!({"file_path": "T=T1"})).is_empty());
    // on the line: the session's own call, never a builder's, and none where nothing is named
    assert_eq!(
        names("Bash", &bash("make builder-done T=T5 F=451"), None),
        Some(json!(["T5"]))
    );
    assert_eq!(
        names(
            "Agent",
            &json!({"description": "451 T5", "prompt": "x"}),
            None
        ),
        Some(json!(["T5"]))
    );
    assert_eq!(
        names("Bash", &bash("make plan-section T=T5"), Some("b")),
        None
    );
    assert_eq!(names("Bash", &bash("git status"), None), None);
    // `task` stays the filing's: a builder-done's T= is not the line's own task
    let p = json!({"hook_event_name": "PreToolUse", "session_id": "s", "tool_name": "Bash", "tool_use_id": "u",
        "tool_input": bash("make builder-done T=T5")});
    assert_eq!(line(&p, "T").get("task"), None);
}
