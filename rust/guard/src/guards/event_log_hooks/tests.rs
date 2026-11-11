//! The line and its log against a temporary clone; the verdicts against today's are the suite's
//! (`tests/hooks/test-event-log-hooks.sh`, replayed through the shim).

use std::path::{Path, PathBuf};
use std::time::{Duration, UNIX_EPOCH};

use serde_json::{json, Value};

use super::{
    agent_category, append, category, common_git_dir, feature_of, line, make_target, now_stamp,
    typed_prompt, verdict_of,
};

fn clone(tag: &str) -> PathBuf {
    let d = std::env::temp_dir().join(format!("l7r-guard-events-{tag}-{}", std::process::id()));
    let _ = std::fs::remove_dir_all(&d);
    std::fs::create_dir_all(d.join(".git")).unwrap();
    std::fs::create_dir_all(d.join(".specify")).unwrap();
    std::fs::write(
        d.join(".specify/feature.json"),
        r#"{"feature_directory": "specs/999-a"}"#,
    )
    .unwrap();
    d
}

fn none(_: &str) -> Option<String> {
    None
}

#[test]
fn a_reply_is_read_for_its_verdict() {
    for (text, want) in [
        ("plan-verdict: recorded PASS for x", "PASS"),
        ("  VERDICT: needs-work\n", "NEEDS-WORK"),
        ("The plan is CLEAR.", "CLEAR"),
        ("impl-drift: 3 findings in all", "findings"),
        ("nothing to act on here", "clean"),
        ("COVERAGE 0; TRUTH 0", "clean"),
        ("COVERAGE 0; TRUTH 2", "findings"),
        ("units\nquote-check: x - READ 0 findings; ok", "clean"),
        ("units\nquote-check: x - READ 2 findings; ok", "findings"),
        ("the bundle was empty", "empty bundle"),
        ("words", ""),
    ] {
        assert_eq!(verdict_of(text), want, "{text}");
    }
}

#[test]
fn a_call_has_its_target_and_its_category() {
    assert_eq!(make_target("make -C x quick ALL=1"), "quick");
    assert_eq!(make_target("cat <<EOF\nmake done\nEOF"), "");
    assert_eq!(make_target("ls"), "");
    let ti = |v: Value| v.as_object().cloned().unwrap_or_default();
    assert_eq!(category("Edit", &ti(json!({}))), "edit");
    assert_eq!(
        category("Bash", &ti(json!({"command": "make done"}))),
        "gate"
    );
    assert_eq!(
        category("Bash", &ti(json!({"command": "make quick"}))),
        "quick test"
    );
    assert_eq!(
        category("Bash", &ti(json!({"command": "make test-file FILE=x"}))),
        "test file"
    );
    assert_eq!(
        category("Bash", &ti(json!({"command": "make tick"}))),
        "spec-kit step"
    );
    assert_eq!(
        category("Bash", &ti(json!({"command": "ls"}))),
        "other tool"
    );
    assert_eq!(
        category("Skill", &ti(json!({"skill": "speckit-plan"}))),
        "spec-kit step"
    );
    assert_eq!(category("Skill", &ti(json!({"skill": "x"}))), "other tool");
    assert_eq!(
        category("Agent", &ti(json!({"subagent_type": "quote-check"}))),
        "record check"
    );
    for (agent, prompt, want) in [
        ("impl-drift", "", "claims check"),
        ("x", "claims-triage", "claims check"),
        ("x", "modal-triage", "record check"),
        ("glyph-check", "", "review check"),
        ("spec-fidelity-verify", "", "spec review"),
        ("round-arbiter", "", "round arbiter"),
        ("", "", "other subagent"),
    ] {
        assert_eq!(agent_category(agent, prompt), want);
    }
}

#[test]
fn each_events_line_carries_its_fields() {
    let t = "T";
    let bash = line(
        &json!({"hook_event_name": "PreToolUse", "session_id": "s", "tool_name": "Bash", "tool_use_id": "u", "agent_id": "a1", "tool_input": {"command": "make tick F=1 T=T07"}, "duration_ms": 12}),
        t,
    );
    assert_eq!(
        Value::Object(bash).to_string(),
        r#"{"t":"T","sid":"s","ev":"PreToolUse","tool":"Bash","id":"u","cat":"spec-kit step","by":"a1","make":"tick","task":"T07","ms":12}"#
    );
    let quick = line(
        &json!({"tool_name": "Bash", "tool_input": {"command": "make quick"}}),
        t,
    );
    assert_eq!(
        (quick["make"].as_str(), quick.get("task")),
        (Some("quick"), None)
    );
    let tick = line(
        &json!({"tool_name": "Bash", "tool_input": {"command": "make tick"}}),
        t,
    );
    assert!(tick.get("task").is_none() && tick["make"] == "tick");
    let edit = line(
        &json!({"tool_name": "Edit", "tool_input": {"file_path": "/p", "old_string": "a", "new_string": "### H"}}),
        t,
    );
    assert_eq!(
        (edit["old"].as_str(), edit["heading"].clone()),
        (Some("86f7e437faa5"), json!(true))
    );
    let write = line(
        &json!({"tool_name": "Write", "tool_input": {"notebook_path": "/n", "content": "x"}}),
        t,
    );
    assert_eq!(
        (write["path"].as_str(), write["new"].as_str().map(str::len)),
        (Some("/n"), Some(12))
    );
    let agent = line(
        &json!({"tool_name": "Agent", "tool_input": {"prompt": "read /tmp/x/MANIFEST.md UNIT: u1, now REVIEW_ROUNDS_OK=1"}, "tool_response": {"agentId": "ag"}}),
        t,
    );
    assert_eq!(
        (
            agent["agent"].as_str(),
            agent["manifest"].as_str(),
            agent["unit"].as_str(),
            agent["waiver"].clone(),
            agent["aid"].as_str()
        ),
        (
            Some("general-purpose"),
            Some("/tmp/x/MANIFEST.md"),
            Some("u1"),
            json!(1),
            Some("ag")
        )
    );
    let bare = line(
        &json!({"tool_name": "Agent", "tool_input": "not an object"}),
        t,
    );
    assert_eq!(bare["agent"], "general-purpose");
    let prompt = line(
        &json!({"hook_event_name": "UserPromptSubmit", "prompt": "go"}),
        t,
    );
    assert_eq!(prompt["gm"], true);
    let stop = line(
        &json!({"hook_event_name": "SubagentStop", "agent_type": "quote-check", "agent_id": "q", "last_assistant_message": "PASS"}),
        t,
    );
    assert_eq!(
        (stop["cat"].as_str(), stop["verdict"].as_str()),
        (Some("record check"), Some("PASS"))
    );
    let start = line(&json!({"hook_event_name": "SubagentStart"}), t);
    assert!(start.get("verdict").is_none() && start["agent"] == "");
    assert_eq!(
        line(&json!({"hook_event_name": "Stop", "session_id": 0}), t)["sid"],
        ""
    );
}

#[test]
fn a_prompt_is_the_gms_when_typed() {
    assert!(typed_prompt(&json!("go")));
    assert!(!typed_prompt(&json!("<system-reminder>x")));
    assert!(!typed_prompt(&json!("  ")));
    assert!(typed_prompt(&json!([{"type": "text", "text": "go"}])));
    assert!(!typed_prompt(
        &json!([{"type": "text", "text": "go"}, {"type": "tool_result"}])
    ));
    assert!(!typed_prompt(&json!([{"type": "image"}])));
    assert!(typed_prompt(&json!(3)));
}

#[test]
fn the_line_goes_to_the_features_log_in_the_clones_git_dir() {
    let d = clone("append");
    let p = append(
        &json!({"hook_event_name": "Stop", "cwd": d.to_string_lossy()}),
        "T",
        Path::new("/"),
        &none,
    )
    .unwrap();
    assert_eq!(
        p,
        std::fs::canonicalize(&d)
            .unwrap()
            .join(".git/l7r-events/999-a.jsonl")
    );
    assert!(append(&json!({"cwd": "/"}), "T", Path::new("/"), &none).is_none());
    let to = d.join("events");
    let env = |k: &str| (k == "L7R_EVENTS_DIR").then(|| to.to_string_lossy().into_owned());
    assert_eq!(
        append(&json!({}), "T", &d, &env).unwrap(),
        to.join("999-a.jsonl")
    );
    assert!(now_stamp(UNIX_EPOCH + Duration::from_millis(1_500)) == "1970-01-01T00:00:01.500Z");
}

#[test]
fn an_edit_that_puts_back_replaced_text_owes_the_arbiter() {
    let d = clone("reversal");
    let edit = |old: &str, new: &str| json!({"hook_event_name": "PreToolUse", "cwd": d.to_string_lossy(), "tool_name": "Edit", "tool_input": {"file_path": "/f", "old_string": old, "new_string": new}});
    append(&edit("A", "B"), "1", &d, &none).unwrap();
    append(&edit("B", "A"), "2", &d, &none).unwrap();
    let owed = std::fs::read_to_string(d.join(".git/arbiter-owed.json")).unwrap();
    assert!(owed.contains("reversal:/f"));
    std::fs::remove_file(d.join(".git/arbiter-owed.json")).unwrap();
    append(&edit("A", "C"), "3", &d, &none).unwrap();
    assert!(!d.join(".git/arbiter-owed.json").exists());
}

#[test]
fn the_feature_and_the_git_dir_are_read_as_the_tool_reads_them() {
    let d = clone("feature");
    assert_eq!(feature_of(&d, &none), "999-a");
    assert_eq!(
        feature_of(&d, &|k: &str| (k == "L7R_FEATURE_DIRECTORY")
            .then(|| "specs/444-b/".to_owned())),
        "444-b"
    );
    std::fs::create_dir_all(d.join("specs/445-c")).unwrap();
    assert_eq!(
        feature_of(&d, &|k: &str| (k == "SPECIFY_FEATURE")
            .then(|| "445-c".to_owned())),
        "445-c"
    );
    assert_eq!(
        feature_of(&d, &|k: &str| (k == "SPECIFY_FEATURE")
            .then(|| "446-missing".to_owned())),
        "999-a"
    );
    std::fs::write(d.join(".specify/feature.json"), "not json").unwrap();
    assert_eq!(feature_of(&d, &none), "");
    let wt = d.join("wt");
    std::fs::create_dir_all(d.join(".git/worktrees/wt")).unwrap();
    std::fs::create_dir_all(&wt).unwrap();
    std::fs::write(wt.join(".git"), "gitdir: ../.git/worktrees/wt\n").unwrap();
    std::fs::write(d.join(".git/worktrees/wt/commondir"), "../..\n").unwrap();
    assert_eq!(
        common_git_dir(&wt),
        std::fs::canonicalize(d.join(".git")).unwrap()
    );
    std::fs::remove_file(d.join(".git/worktrees/wt/commondir")).unwrap();
    assert_eq!(
        common_git_dir(&wt),
        std::fs::canonicalize(d.join(".git/worktrees/wt")).unwrap()
    );
    assert!(super::decide(
        &crate::protocol::Event {
            name: "Stop".into(),
            input: json!({"cwd": "/"})
        },
        &crate::shared::session::Session::from_input(&json!({}))
    )
    .is_empty());
}

#[test]
fn the_edges_of_a_value_and_a_path() {
    use super::{text_of, truthy};
    assert_eq!(verdict_of(&format!("{} PASS", "x".repeat(700))), "");
    assert_eq!(
        (
            text_of(Some(&json!(5))),
            text_of(Some(&json!(0))),
            text_of(Some(&json!(false))),
            text_of(None)
        ),
        ("5".into(), String::new(), String::new(), String::new())
    );
    assert!(
        !truthy(&json!(null))
            && truthy(&json!(true))
            && !truthy(&json!([]))
            && truthy(&json!({"a": 1}))
            && !truthy(&json!({}))
    );
    let typed = line(
        &json!({"tool_name": "Agent", "tool_input": {"subagent_type": "quote-check"}}),
        "T",
    );
    assert_eq!(typed["agent"], "quote-check");
    let read = line(
        &json!({"tool_name": "Read", "tool_input": {"file_path": "/f"}}),
        "T",
    );
    assert!(read.get("path").is_none() && read["cat"] == "other tool");
    let start = line(
        &json!({"tool_name": "Bash", "tool_input": {"command": "make task-start F=1 T=T3"}}),
        "T",
    );
    assert_eq!(start["task"], "T3");
    assert!(append(
        &json!({"cwd": "/nonexistent/deeper"}),
        "T",
        Path::new("/"),
        &none
    )
    .is_none());
    let d = clone("edges");
    std::fs::remove_file(d.join(".specify/feature.json")).unwrap();
    assert!(append(&json!({"cwd": d.to_string_lossy()}), "T", &d, &none)
        .unwrap()
        .ends_with("_unassigned.jsonl"));
    let wt = d.join("wt");
    std::fs::create_dir_all(&wt).unwrap();
    std::fs::write(wt.join(".git"), "gitdir: missing/dir\n").unwrap();
    assert_eq!(common_git_dir(&wt), wt.join("missing/dir"));
    std::fs::create_dir_all(d.join("g")).unwrap();
    std::fs::write(d.join("g/commondir"), "nowhere\n").unwrap();
    std::fs::write(wt.join(".git"), "gitdir: ../g\n").unwrap();
    assert_eq!(
        common_git_dir(&wt),
        std::fs::canonicalize(d.join("g")).unwrap().join("nowhere")
    );
    let outcome = super::decide(
        &crate::protocol::Event {
            name: "Stop".into(),
            input: json!({"cwd": d.to_string_lossy()}),
        },
        &crate::shared::session::Session::from_input(&json!({})),
    );
    assert!(outcome.is_empty());
}

#[test]
fn a_bash_call_that_runs_no_make_target_names_none() {
    assert!(line(
        &json!({"tool_name": "Bash", "tool_input": {"command": "ls"}}),
        "T"
    )
    .get("make")
    .is_none());
}

#[test]
fn a_features_log_is_named_for_it() {
    let root = clone("log-path");
    assert!(super::log_path(&root, "500-f").ends_with("500-f.jsonl"));
    let named = |k: &str| (k == "L7R_EVENTS_DIR").then(|| "/elsewhere".to_owned());
    assert_eq!(
        super::log_path_in(&root, "", &named),
        Path::new("/elsewhere/_unassigned.jsonl")
    );
    assert_eq!(
        super::log_path_in(&root, "f", &none),
        root.join(".git/l7r-events/f.jsonl")
    );
}
