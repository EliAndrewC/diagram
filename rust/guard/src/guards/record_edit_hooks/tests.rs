use std::path::Path;

use serde_json::{json, Value};

use super::{judge, GUARD};
use crate::protocol::{Answer, Event};
use crate::shared::checks::testkit::{clone_at, dir};
use crate::shared::session::Session;

fn event(cwd: Option<&Path>, tool: &str, ti: &Value) -> Event {
    let mut input = json!({"tool_name": tool, "tool_input": ti, "session_id": "s"});
    if let Some(c) = cwd {
        input["cwd"] = json!(c);
    }
    Event {
        name: "PreToolUse".to_owned(),
        input,
    }
}

fn gate(tree: &Path, script: &str) {
    std::fs::create_dir_all(tree.join("scripts/gates")).unwrap();
    crate::guards::write_executable(
        &tree.join("scripts/gates/l7r-gate.sh"),
        &format!("#!/bin/sh\ncat >/dev/null\n{script}\n"),
    );
}

fn call(e: &Event, here: &Path, tree: &Path) -> Vec<Answer> {
    judge(e, &Session::from_input(&e.input), here, tree)
}

#[test]
fn a_plain_call_passes_and_a_frozen_page_is_refused() {
    crate::shared::log::quiet();
    let root = clone_at("freeze");
    gate(&root, "exit 1");
    assert!(call(
        &event(Some(&root), "Bash", &json!({"command": "ls"})),
        &root,
        &root
    )
    .is_empty());
    assert!((GUARD.decide)(
        &event(Some(&root), "Bash", &json!({"command": "ls"})),
        &Session::from_input(&json!({}))
    )
    .is_empty());
    let page = json!({"file_path": "research/questions/0105-x.html", "old_string": "a", "new_string": "b"});
    std::fs::write(root.join(".git/checks-open.json"), json!({"feature": "999-x", "dispatches": {"a": {"check": "quote-check", "subjects": ["q:0105"], "state": "running", "t": 1e12}}}).to_string()).unwrap();
    assert!(
        matches!(&call(&event(Some(&root), "Edit", &page), &root, &root)[..], [Answer::Refuse(t)] if t.starts_with("BLOCKED: q:0105 is frozen"))
    );
    assert!(call(
        &event(None, "Bash", &json!({"command": "ls"})),
        &root,
        &root
    )
    .is_empty());
    assert!(call(
        &event(Some(&root), "Bash", &json!({"command": "make done"})),
        &root,
        &root
    )
    .is_empty());
    std::fs::write(root.join(".git/checks-open.json"), r#"{"dispatches": {}}"#).unwrap();
    assert!(call(&event(Some(&root), "Edit", &page), &root, &root).is_empty());
}

#[test]
fn the_route_rewrites_or_refuses() {
    crate::shared::log::quiet();
    let root = dir("route");
    let page =
        json!({"file_path": "/r/research/site/q/x.html", "old_string": "o", "new_string": "n"});
    let rewrite = r#"echo '{"verdict": "rewrite", "hook": {"hookSpecificOutput": {"updatedInput": {"file_path": "moved"}, "additionalContext": "re-aimed"}}}'"#;
    gate(&root, rewrite);
    let e = event(Some(&root), "Edit", &page);
    assert!(
        matches!(&call(&e, &root, &root)[..], [Answer::Rewrite(v), Answer::Notice(n)] if v["file_path"] == "moved" && n == "re-aimed")
    );
    gate(
        &root,
        r#"echo '{"verdict": "rewrite", "hook": {"updatedInput": {"file_path": "bare"}}}'"#,
    );
    assert!(
        matches!(&call(&e, &root, &root)[..], [Answer::Rewrite(v)] if v["file_path"] == "bare")
    );
    gate(
        &root,
        r#"echo '{"verdict": "refuse", "message": "no fragment", "rule": "text-in-no-fragment"}'"#,
    );
    assert!(
        matches!(&call(&e, &root, &root)[..], [Answer::Refuse(t)] if t == "BLOCKED: no fragment\n(scripts/hooks/record-edit-hooks.sh; feature 258, spec FR-028)\n")
    );
    gate(&root, r#"echo '{"verdict": "refuse", "message": "m"}'"#);
    assert!(matches!(&call(&e, &root, &root)[..], [Answer::Refuse(_)]));
    gate(&root, r#"echo '{"verdict": "pass"}'"#);
    assert!(call(&e, &root, &root).is_empty());
    gate(&root, "echo not json");
    assert!(call(&e, &root, &root).is_empty());
}
