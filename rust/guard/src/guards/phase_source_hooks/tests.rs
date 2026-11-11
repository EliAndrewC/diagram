//! The decider over a real checkout (`tests/hooks/test-phase-source-hooks.sh`, replayed through the shim, is the verdict).

use serde_json::{json, Value};

use super::{any_match, decide, judge, parent_of, stamp};
use crate::protocol::{Answer, Event};
use crate::shared::session::Session;
use crate::shared::tool::ask;

const OLD: &str = "l7r/diagram/old/stage.py";

/// A checkout holding phase task T9's old module, its box open.
fn world(tag: &str, allow: &Value) -> crate::shared::tempdir::Held<String> {
    crate::shared::log::quiet();
    let d = crate::shared::tempdir::TempDir::new(&format!("guard-phase-{tag}"));
    std::fs::create_dir_all(d.join("l7r/diagram/old")).unwrap();
    std::fs::create_dir_all(d.join("specs/444-x")).unwrap();
    let at = d.canonicalize().unwrap().to_string_lossy().into_owned();
    assert!(ask(std::path::Path::new("/"), "git", &["init", "-q", &at], "").ok());
    std::fs::write(format!("{at}/{OLD}"), "x\n").unwrap();
    std::fs::write(
        format!("{at}/specs/444-x/tasks.md"),
        "- [ ] T9 rebuild\n- [x] T90 other\n",
    )
    .unwrap();
    let state =
        json!({"feature": "444-x", "task": "T9", "phase": "water", "files": [OLD], "allow": allow});
    std::fs::write(format!("{at}/.git/phase-sources.json"), state.to_string()).unwrap();
    let held = at;
    d.hold(held)
}

fn run(tool: &str, input: &Value, at: &str) -> Vec<Answer> {
    let e = Event {
        name: "PreToolUse".to_owned(),
        input: json!({"tool_name": tool, "cwd": at, "tool_input": input}),
    };
    judge(
        &e,
        &Session::from_input(&e.input),
        at,
        &format!("{at}/.git/phase-sources.json"),
        "2026-11-08T00:00:00Z",
    )
}

fn bash(cmd: &str, at: &str) -> Vec<Answer> {
    run("Bash", &json!({"command": cmd}), at)
}

fn refused(got: &[Answer], words: &str) -> bool {
    matches!(got, [Answer::Refuse(t)] if t.contains(words))
}

#[test]
fn a_read_of_a_held_file_is_refused_and_says_where_to_write_from() {
    let at = world("read", &json!([]));
    let got = run("Read", &json!({"file_path": format!("{at}/{OLD}")}), &at);
    assert!(
        refused(&got, "is the old code of `water`")
            && refused(&got, "444-x/phases/water_greenfield.derivation.md")
    );
    assert!(refused(
        &run("Read", &json!({"file_path": OLD}), &at),
        "old code"
    ));
    assert!(run("Read", &json!({"file_path": "other.py"}), &at).is_empty());
    assert!(refused(
        &run("Grep", &json!({"path": "l7r/diagram/old"}), &at),
        "old code"
    ));
    assert!(refused(
        &run("Glob", &json!({"path": OLD}), &at),
        "old code"
    ));
    assert!(run("Grep", &json!({"path": "l7r"}), &at).is_empty());
    assert!(run("Grep", &json!({}), &at).is_empty());
    assert!(run("Read", &json!({"file_path": "/outside/x"}), &at).is_empty());
}

#[test]
fn a_shell_read_is_refused_and_a_mention_is_not() {
    let at = world("shell", &json!([]));
    assert!(refused(&bash(&format!("cat {OLD}"), &at), "old code"));
    assert!(refused(
        &bash("grep -n x l7r/diagram/old/", &at),
        "old code"
    ));
    assert!(refused(
        &bash(&format!("git show HEAD:{OLD}"), &at),
        "old code"
    ));
    assert!(bash(&format!("git rm {OLD}"), &at).is_empty());
    assert!(bash(&format!("make test-file FILE={OLD}"), &at).is_empty());
    assert!(bash("cat other.py", &at).is_empty());
}

#[test]
fn an_allowance_and_a_closed_task_release_the_file() {
    let at = world(
        "allow",
        &json!([{"file": OLD, "until": "2026-11-08T00:10:00Z"}, {"file": "z", "until": "2030"}]),
    );
    assert!(run("Read", &json!({"file_path": OLD}), &at).is_empty());
    let late = world(
        "late",
        &json!([{"file": OLD, "until": "2026-01-01T00:00:00Z"}]),
    );
    assert!(refused(
        &run("Read", &json!({"file_path": OLD}), &late),
        "old code"
    ));
    let closed = world("closed", &json!([]));
    std::fs::write(
        format!("{closed}/specs/444-x/tasks.md"),
        "- [x] T9 rebuild\n- [ ] T90 other\n",
    )
    .unwrap();
    assert!(run("Read", &json!({"file_path": OLD}), &closed).is_empty());
    std::fs::remove_file(format!("{closed}/specs/444-x/tasks.md")).unwrap();
    assert!(run("Read", &json!({"file_path": OLD}), &closed).is_empty());
}

#[test]
fn the_escape_needs_a_reason() {
    let at = world("escape", &json!([]));
    assert!(bash(
        &format!("cat {OLD}  # PHASE_SOURCE_OK: replacing its thin wrapper"),
        &at
    )
    .is_empty());
    assert!(refused(
        &bash(&format!("cat {OLD}  # PHASE_SOURCE_OK"), &at),
        "with no reason"
    ));
}

#[test]
fn nothing_held_or_nowhere_to_look_passes() {
    let at = world("none", &json!([]));
    let e = Event {
        name: "PreToolUse".to_owned(),
        input: json!({"tool_name": "Read", "tool_input": {"file_path": OLD}}),
    };
    let s = Session::from_input(&e.input);
    assert!(judge(&e, &s, &at, "/no/such/file", "now").is_empty());
    assert!(judge(
        &e,
        &s,
        "/tmp",
        &format!("{at}/.git/phase-sources.json"),
        "now"
    )
    .is_empty());
    std::fs::write(format!("{at}/.git/phase-sources.json"), "{").unwrap();
    assert!(run("Read", &json!({"file_path": OLD}), &at).is_empty());
    let nokey = Event {
        name: "PreToolUse".to_owned(),
        input: json!({"tool_name": "Read", "cwd": at}),
    };
    assert!(judge(
        &nokey,
        &Session::from_input(&nokey.input),
        &at,
        &format!("{at}/.git/phase-sources.json"),
        "now"
    )
    .is_empty());
    assert!(
        any_match(&format!("/no/such {at}/.git/HEAD"))
            && any_match(&format!("{at}/*/HEAD"))
            && !any_match(&format!("{at}/*/nothing"))
            && !any_match("/no/such/*/x")
    );
    assert_eq!((parent_of("a/b.py"), parent_of("b.py")), ("a", "."));
    assert_eq!(stamp().len(), 20);
    // The default glob names this host's checkouts, so what it answers is the host's; the seam's cases above are the verdict.
    let _host_answer = decide(&e, &s);
}
