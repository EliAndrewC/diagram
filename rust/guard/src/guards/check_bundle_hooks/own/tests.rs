use std::path::Path;

use serde_json::{json, Value};

use super::{own_task, Own};
use crate::shared::checks::testkit::clone_at;

fn own(feature: &str, tasks: &[&str]) -> Own {
    let tasks = tasks.iter().map(|t| (*t).to_owned()).collect();
    Own {
        feature: feature.to_owned(),
        tasks,
    }
}

fn input(description: &str, prompt: &str, extra: &Value) -> Value {
    let mut v = json!({"tool_name": "Agent", "tool_input": {"subagent_type": "quote-check", "description": description, "prompt": prompt}});
    if let (Some(to), Some(from)) = (v.as_object_mut(), extra.as_object()) {
        to.extend(from.clone());
    }
    v
}

fn write(path: &Path, text: &str) {
    std::fs::create_dir_all(path.parent().unwrap()).unwrap();
    std::fs::write(path, text).unwrap();
}

/// Its own words: the description's first task, else the prompt's first line's; the feature the number before it, else the one whose
/// start names it, else feature.json's; a later line names nothing.
#[test]
fn a_check_s_own_words_name_its_task_and_feature() {
    let root = clone_at("own-words");
    let none = json!({});
    let named = own_task(&input("449 T265 round 5", "x", &none), &root);
    assert_eq!(named, Some(own("449", &["T265"])));
    let head = own_task(
        &input("impl-drift", "DECIDE_OK=\"451 T7's re-check\"\nT9", &none),
        &root,
    );
    assert_eq!(head, Some(own("451", &["T7"])));
    write(
        &root.join(".git/task-starts.jsonl"),
        "{\"feature\": \"449-rust\", \"task\": \"T3\", \"utc\": \"2026-11-22T10:00:00Z\"}\n",
    );
    let started = own_task(&input("T3 claims", "x", &none), &root);
    assert_eq!(started, Some(own("449-rust", &["T3"])));
    let fallback = own_task(&input("T4 claims", "x", &none), &root);
    assert_eq!(fallback, Some(own("999-x", &["T4"])));
    let later = own_task(
        &input("a check", "Read the bundle.\nT5 is named later", &none),
        &root,
    );
    assert_eq!(later, None);
    write(&root.join(".specify/feature.json"), "{}");
    let unknown = own_task(&input("T4 claims", "x", &none), &root);
    assert_eq!(unknown, None);
}

/// Its builder: the dispatching agent's brief, a bundle's builder every member; an agent that is no builder names nothing.
#[test]
fn a_check_s_builder_names_its_task() {
    let root = clone_at("own-builder");
    let session = root.join("sess.jsonl");
    let subagents = root.join("sess/subagents");
    write(
        &subagents.join("agent-b1.meta.json"),
        &json!({"spawnDepth": 1, "description": "449 bundle T258, T268, T269: three"}).to_string(),
    );
    write(
        &subagents.join("agent-h1.meta.json"),
        &json!({"spawnDepth": 2, "description": "449 T1: a helper"}).to_string(),
    );
    let from = |aid: &str| json!({"agent_id": aid, "transcript_path": session.to_string_lossy()});
    let bundle = own_task(&input("a check", "Read the bundle.", &from("b1")), &root);
    assert_eq!(bundle, Some(own("449", &["T258", "T268", "T269"])));
    let helper = own_task(&input("a check", "Read the bundle.", &from("h1")), &root);
    assert_eq!(helper, None);
    let no_transcript = own_task(
        &input("a check", "Read it.", &json!({"agent_id": "b1"})),
        &root,
    );
    assert_eq!(no_transcript, None);
}

/// Its page session: the brief its id names in the clone's index - the feature its path's, the task its first line's, else its file
/// name's; an id the index lacks, or a brief outside `specs/`, names nothing.
#[test]
fn a_page_session_s_brief_names_its_task() {
    let root = clone_at("own-page");
    let headed = root.join("specs/449-x/briefs/t197-g2-checks.md");
    write(
        &headed,
        "# Brief - feature 449 task T197, group G2: check and apply\n",
    );
    let bare = root.join("specs/449-x/briefs/t201-g1-write.md");
    write(&bare, "# Brief - the shrine group\n");
    let outside = root.join("notes/t5-x.md");
    write(&outside, "# T5\n");
    let index = format!(
        "s1 {}\ns2 {}\ns3 {}\nmalformed\n",
        headed.display(),
        bare.display(),
        outside.display()
    );
    write(&root.join(".git/page-sessions/index.txt"), &index);
    let none = json!({});
    let ask = || own_task(&input("a check", "Read the bundle.", &none), &root);
    let unset = ask();
    assert_eq!(unset, None);
    crate::shared::env::set("L7R_PAGE_SESSION", "s1");
    let by_line = ask();
    assert_eq!(by_line, Some(own("449-x", &["T197"])));
    crate::shared::env::set("L7R_PAGE_SESSION", "s2");
    let by_name = ask();
    assert_eq!(by_name, Some(own("449-x", &["T201"])));
    crate::shared::env::set("L7R_PAGE_SESSION", "s3");
    let outside_specs = ask();
    assert_eq!(outside_specs, None);
    crate::shared::env::set("L7R_PAGE_SESSION", "s9");
    let unindexed = ask();
    assert_eq!(unindexed, None);
    crate::shared::env::unset("L7R_PAGE_SESSION");
}
