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
    // the reply's first line in the house style, a quotation held (feature 449 T242): the ledger is Markdown, so straight quotes hold too
    let brit = format!("behavio{}", "ur");
    put(
        &root,
        "p/s/subagents/agent-brit.jsonl",
        &transcript(
            &json!("go"),
            &format!("the {brit} \u{2013} off, \u{201c}{brit}\u{201d} and \"{brit}\" held\n"),
        ),
    );
    let row = filled_row(&one(&pass("c", "brit", "", &json!({}))), "here", &root).unwrap();
    let want = format!(
        "| see reply | the behavior - off, \u{201c}{brit}\u{201d} and \"{brit}\" held | judgment |"
    );
    assert!(row.contains(&want));
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

/// `f`'s answer, or a failure once it runs past 20 s (feature 449 T185: a quadratic search, or a scan over an error it repeats, must
/// fail the test rather than hang it).
fn within<T: Send + 'static>(f: impl FnOnce() -> T + Send + 'static) -> T {
    let (tx, rx) = std::sync::mpsc::channel();
    let _run = std::thread::spawn(move || tx.send(f()));
    rx.recv_timeout(std::time::Duration::from_secs(20))
        .expect("the search ran past its bound")
}

/// A plan review's record named after a line of many `recorded` words (feature 449 T185): unlimited, `PLAN_RECORDED` tried every one to
/// its line's end (14 s on 100 KB, measured 2026-11-18, scratchpad t185/sizecurve.log), and at `fancy_regex`'s old limit it erred and read as unrecorded; it now starts
/// at the line's first.
#[test]
fn a_plan_record_after_many_recordeds_is_seen_in_linear_time() {
    let reply = format!(
        "{}\nI ran make plan-verdict and it stored the verdict",
        "recorded x ".repeat(30_000)
    );
    assert_eq!(
        within(move || super::PLAN_RECORDED.is_match(&reply).ok()),
        Some(true)
    );
}

/// A check-wave unit whose run returned text, not structured output: the journal's result is its reply, the subject its place, and its
/// session the directory above `subagents/workflows/<run>/` (451 T151); a journal with no result for the agent leaves the reply empty.
#[test]
fn a_wave_unit_s_text_result_is_its_reply() {
    let (_d, env) = world("rows-wave", &[]);
    let root = Path::new(&env.home).join(".claude/projects");
    let journal = [
        json!({"type": "result", "agentId": "w9", "result": "PASS - all fine"}),
        json!({"type": "result", "agentId": "other", "result": "x"}),
    ];
    let body = journal
        .iter()
        .map(ToString::to_string)
        .collect::<Vec<_>>()
        .join("\n");
    put(&root, "p/s9/subagents/workflows/wf_z/journal.jsonl", &body);
    put(
        &root,
        "p/s9/subagents/workflows/wf_z/agent-w9.jsonl",
        &transcript(&json!("go"), ""),
    );
    put(
        &root,
        "p/s9/subagents/workflows/wf_y/journal.jsonl",
        "{\"type\": \"launched\"}",
    );
    put(
        &root,
        "p/s9/subagents/workflows/wf_y/agent-w8.jsonl",
        &transcript(&json!("go"), ""),
    );
    let p = one(&pass("c", "w9", "subj", &json!({})));
    let session = session_of(&p, &root);
    assert_eq!(session, "s9");
    let row = filled_row(&p, "here", &root).unwrap();
    let starts = row.starts_with("| 2026-11-01 | c | subj | PASS | PASS - all fine | nothing |");
    assert!(starts, "{row}");
    let none = filled_row(&one(&pass("c", "w8", "subj", &json!({}))), "here", &root).unwrap();
    let empty = none.contains("| subj | see reply | - | judgment |");
    assert!(empty, "{none}");
    // a structured result with no `text`: the result itself is the reply, its label the place
    let bare = json!({"type": "result", "agentId": "w7", "result": {"label": "unit-7", "verdict": "PASS"}});
    put(
        &root,
        "p/s9/subagents/workflows/wf_x/journal.jsonl",
        &bare.to_string(),
    );
    put(
        &root,
        "p/s9/subagents/workflows/wf_x/agent-w7.jsonl",
        &transcript(&json!("go"), ""),
    );
    let seven = filled_row(&one(&pass("c", "w7", "subj", &json!({}))), "here", &root).unwrap();
    let whole =
        seven.contains("| unit-7 | PASS | {\"label\":\"unit-7\",\"verdict\":\"PASS\"} | nothing |");
    assert!(whole, "{seven}");
    let nobody = session_of(&one(&pass("c", "", "subj", &json!({}))), &root);
    assert_eq!(nobody, "");
}
