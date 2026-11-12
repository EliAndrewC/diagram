//! A pass's rows: by hand, filled from the reply, and a plan review's from its record.

use std::path::Path;

use serde_json::json;

use super::super::super::tests::put;
use super::super::tests::{as_pass, pass, transcript, world};
use super::{filled_row, in_the_record, plan_review_rows, row_for, session_of, Pass};

fn one(line: &str) -> Pass {
    as_pass(line)
}

#[test]
fn the_row_by_hand_fills_what_was_measured() {
    let mut p = one(&pass("c", "a", "", &json!({})));
    p.remove("date");
    assert_eq!(
        row_for(&p),
        "| ? | c | ? | ? | ? | ? | ? | ? | 5 s | 1k in (0k cached) / 0.5k out |"
    );
}

#[test]
fn a_filled_row_reads_the_agents_reply() {
    let (_d, env) = world("rows-filled", &[]);
    let root = Path::new(&env.home).join(".claude/projects");
    let reply = "\n# Heading\n```python\n  - **the caption sits wrong** -\nmore";
    put(
        &root,
        "p/s/subagents/agent-r.jsonl",
        &transcript(&json!("go"), reply),
    );
    let long = "y".repeat(130);
    put(
        &root,
        "p/s/subagents/agent-long.jsonl",
        &transcript(&json!("go"), &format!("{long}\n")),
    );
    put(
        &root,
        "p/s/subagents/agent-dash.jsonl",
        &transcript(&json!("go"), "---"),
    );
    let row = filled_row(
        &one(&pass("c", "r", &"s".repeat(90), &json!({}))),
        "here",
        &root,
    )
    .unwrap();
    assert!(row.starts_with(&format!(
        "| 2026-11-01 | c | {} | see reply | the caption sits wrong | judgment |",
        "s".repeat(80)
    )));
    let row = filled_row(&one(&pass("c", "long", "", &json!({}))), "here", &root).unwrap();
    assert!(row.contains(&format!(
        "| ? | see reply | {} | judgment |",
        "y".repeat(110)
    )));
    let row = filled_row(&one(&pass("c", "dash", "", &json!({}))), "here", &root).unwrap();
    assert!(row.contains("| see reply | - |"));
    let mut p = one(&pass("c", "", "", &json!({})));
    p.remove("check");
    assert!(filled_row(&p, "here", &root)
        .unwrap_err()
        .contains("KeyError"));
    assert_eq!(
        session_of(&one(&pass("c", "r", "", &json!({}))), &root),
        "s"
    );
    assert_eq!(session_of(&one(&pass("c", "", "", &json!({}))), &root), "");
}

#[test]
fn a_plan_reviews_record_answers_by_task_or_block() {
    let (_d, env) = world("rows-record", &[]);
    let repo = env.cwd.clone();
    let p = |subject: &str, date: Option<&str>| {
        let mut m = one(&pass("spec-fidelity", "zz", subject, &json!({})));
        match date {
            Some(d) => m.insert("date".to_owned(), json!(d)),
            None => m.remove("date"),
        };
        m
    };
    let task = "MODE 4: PLAN REVIEW of feature 449-x task T6";
    let blocks = "MODE 4: PLAN REVIEW of feature 449-x blocks";
    assert!(in_the_record(&p(task, Some("2026-11-01")), &repo).unwrap());
    assert!(!in_the_record(&p(task, Some("2026-11-09")), &repo).unwrap());
    assert!(in_the_record(&p(blocks, Some("2026-11-02")), &repo).unwrap());
    assert!(!in_the_record(&p("no feature named", None), &repo).unwrap());
    assert!(!in_the_record(&p("feature 449-none task T1", None), &repo).unwrap());
    let unknown = "MODE 4: PLAN REVIEW of feature 449-x task T9";
    assert!(!in_the_record(&p(unknown, Some("2026-11-01")), &repo).unwrap());
    let record = |text: &str| put(&repo, "specs/449-x/plan-review.json", text);
    record("{");
    assert!(!in_the_record(&p(task, None), &repo).unwrap());
    record("[1]");
    assert!(in_the_record(&p(task, None), &repo).is_err());
    record(r#"{"tasks": {"T6": null}}"#);
    assert!(in_the_record(&p(task, None), &repo).is_err());
    record(r#"{"tasks": {"T6": {"reviewed": null}}}"#);
    assert!(in_the_record(&p(task, None), &repo).unwrap());
    assert!(!in_the_record(&p(task, Some("2026-11-01")), &repo).unwrap());
    record(r#"{"tasks": [], "blocks": [1]}"#);
    assert!(in_the_record(&p(blocks, None), &repo).is_err());
    assert!(plan_review_rows(&[p(blocks, None)], &repo, &repo).is_err());
    record(r#"{"blocks": {}}"#);
    assert!(!in_the_record(&p(blocks, None), &repo).unwrap());
}
