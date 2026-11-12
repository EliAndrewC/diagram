//! A feature's questions and the passes its work can be traced to.

use std::collections::BTreeSet;
use std::path::Path;

use serde_json::{json, Value};

use super::super::super::tests::put;
use super::super::tests::{as_pass, pass, transcript, world};
use super::{active_feature, belongs, feature_of, feature_questions, unit_prompt, Pass};

fn one(line: &str) -> Pass {
    as_pass(line)
}

fn set(words: &[&str]) -> BTreeSet<String> {
    words.iter().map(|w| (*w).to_owned()).collect()
}

#[test]
fn a_features_questions_come_from_the_sheet_and_its_own_files() {
    let (_d, mut env) = world("trace-questions", &[]);
    assert_eq!(feature_of("specs/449-x/checks.md").as_deref(), Some("449"));
    assert_eq!(feature_of("nothing"), None);
    let repo = env.cwd.clone();
    put(&repo, "specs/449-x/briefs/.hidden.md", "SECTION=0078\n");
    put(
        &repo,
        "specs/449-y/implementation-check.md",
        "- 0090: another\n",
    );
    put(
        &repo,
        "specs/4490-z/implementation-check.md",
        "- 0091: not ours\n",
    );
    assert_eq!(
        feature_questions("449", &repo, &env).unwrap(),
        set(&["0094", "0077", "0078", "0090", "0123"])
    );
    env.claims_sheet = Some("bad.md".to_owned());
    std::fs::write(repo.join("bad.md"), [0xff_u8]).unwrap();
    assert!(feature_questions("449", &repo, &env).is_err());
    env.claims_sheet = Some(String::new());
    std::fs::write(repo.join("specs/449-x/briefs/b.md"), [0xff_u8]).unwrap();
    assert!(feature_questions("449", &repo, &env).is_err());
}

#[test]
fn a_pass_belongs_by_its_subject_its_prompt_its_question_its_bundle_or_its_key() {
    let (_d, env) = world("trace-belongs", &[]);
    let (repo, root) = (
        env.cwd.clone(),
        Path::new(&env.home).join(".claude/projects"),
    );
    let qs = set(&["0094"]);
    let is = |agent: &str, subject: &str| {
        belongs(
            &one(&pass("c", agent, subject, &json!({}))),
            "449",
            &qs,
            &repo,
            &root,
        )
        .unwrap()
    };
    assert!(is("", "about feature 449"));
    assert!(is("w1", "[Workflow harness - computed task] x"));
    assert!(!is("nobody", "[Workflow harness - computed task] x"));
    put(
        &root,
        "p/s/subagents/agent-long.jsonl",
        &transcript(&json!("the whole prompt names specs/449-x"), "x"),
    );
    assert!(is("long", &"z".repeat(100)));
    assert!(!is("long", &"z".repeat(99)));
    assert!(is("", "question 0094 and 1.0043"));
    assert!(is("", "/tmp/l7r-check/claims-owed/x"));
    put(
        &repo,
        ".specify/feature.json",
        r#"{"feature_directory": "specs/450-y"}"#,
    );
    assert!(!is("", "/tmp/l7r-check/work-budget-audit-1/"));
    assert!(is("", "/tmp/l7r-check/key-smith-1990-whole/"));
    assert!(!is("", "/tmp/l7r-check/key-jones-2001/"));
    std::fs::write(
        repo.join("research/questions").join("0094-b.html"),
        [0xff_u8],
    )
    .unwrap();
    std::fs::remove_file(repo.join("research/questions").join("0094-a.html")).unwrap();
    assert!(belongs(
        &one(&pass("c", "", "/key-smith-1990/", &json!({}))),
        "449",
        &qs,
        &repo,
        &root
    )
    .is_err());
}

#[test]
fn a_units_prompt_is_its_first_user_message() {
    let (_d, env) = world("trace-prompt", &[]);
    let root = Path::new(&env.home).join(".claude/projects");
    assert_eq!(
        unit_prompt(&one(&pass("c", "", "", &json!({}))), &root).unwrap(),
        ""
    );
    let ask = |first: &str| {
        put(
            &root,
            "p/s/subagents/workflows/run/agent-u.jsonl",
            &format!("{first}\n"),
        );
        unit_prompt(&one(&pass("c", "u", "", &json!({}))), &root)
    };
    let user =
        |content: Value| json!({"type": "user", "message": {"content": content}}).to_string();
    assert_eq!(ask(&user(json!("plain"))).unwrap(), "plain");
    assert_eq!(
        ask(&user(
            json!([{"text": "a"}, {"type": "x"}, "s", {"text": "b"}])
        ))
        .unwrap(),
        "a  b"
    );
    assert_eq!(ask(&user(json!({"k": 1}))).unwrap(), "");
    assert!(ask(&user(json!([{"text": 3}]))).is_err());
    assert!(ask(&user(json!(5))).is_err());
    assert!(ask(&json!({"type": "user", "message": "text"}).to_string()).is_err());
    assert!(ask("[1]").is_err());
    let skipped = [
        json!({"type": "assistant"}).to_string(),
        json!({"type": "user", "message": null}).to_string(),
        user(json!("")),
        "x".to_owned(),
        user(json!("found")),
    ];
    assert_eq!(ask(&skipped.join("\n")).unwrap(), "found");
    std::fs::write(
        root.join("p/s/subagents/workflows/run/agent-u.jsonl"),
        [0xff_u8],
    )
    .unwrap();
    assert!(unit_prompt(&one(&pass("c", "u", "", &json!({}))), &root).is_err());
    std::os::unix::fs::symlink(
        root.join("p/s/subagents/workflows"),
        root.join("p/s/subagents/linked"),
    )
    .unwrap();
    put(
        &root,
        "p/s/subagents/workflows/run/agent-u.jsonl",
        &format!("{}\n", user(json!("real"))),
    );
    assert_eq!(
        unit_prompt(&one(&pass("c", "u", "", &json!({}))), &root).unwrap(),
        "real"
    );
}

#[test]
fn the_active_feature_is_the_one_its_record_names() {
    let (_d, env) = world("trace-active", &[]);
    let repo = env.cwd.clone();
    assert_eq!(active_feature(&repo).unwrap(), "449");
    put(&repo, ".specify/feature.json", "{");
    assert_eq!(active_feature(&repo).unwrap(), "");
    put(
        &repo,
        ".specify/feature.json",
        r#"{"feature_directory": 450}"#,
    );
    assert_eq!(active_feature(&repo).unwrap(), "");
    put(&repo, ".specify/feature.json", "{}");
    assert_eq!(active_feature(&repo).unwrap(), "");
    put(&repo, ".specify/feature.json", "[1]");
    assert!(active_feature(&repo).is_err());
}
