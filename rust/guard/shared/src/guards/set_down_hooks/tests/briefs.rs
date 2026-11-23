//! 451 T156: A BUILDER'S BRIEF, READ AS THE SESSION WRITES IT. The five descriptions the Stop hook's free-slot check misread on
//! 2026-11-22 (a landing agent with no task id, a word between the feature and the first id, a range, a range inside a list); the
//! brief's reader stays for `builder_stop_hooks` and the event log after the free slot itself went (451 T183's MODE 4, D10).

use std::path::Path;

use super::super::builders::builder_brief;

fn ids(from: &str, to: u32) -> Vec<String> {
    let start: u32 = from.parse().unwrap();
    (start..=to).map(|n| format!("T{n}")).collect()
}

/// The brief of an agent whose meta file holds `description` alone.
fn brief(dir: &Path, description: &str) -> Option<(String, Vec<String>)> {
    std::fs::write(
        dir.join("agent-x.meta.json"),
        serde_json::json!({"spawnDepth": 1, "description": description}).to_string(),
    )
    .unwrap();
    builder_brief(dir, "x")
}

#[test]
fn every_task_id_before_the_colon_is_read_words_between_and_ranges_expanded() {
    let d = crate::tempdir::TempDir::new("guard-setdown-briefs");
    let s = |v: &[&str]| v.iter().map(|t| (*t).to_owned()).collect::<Vec<_>>();
    let got = brief(&d, "449 bundle T259, T277: the two bundle follow-ups");
    assert_eq!(got, Some(("449".to_owned(), s(&["T259", "T277"]))));
    let got = brief(&d, "449 T289-T300 bundle (fresh): twelve tasks");
    assert_eq!(got, Some(("449".to_owned(), ids("289", 300))));
    let mut list = s(&["T275", "T276"]);
    list.extend(ids("278", 281));
    let got = brief(&d, "449 bundle T275, T276, T278-T281: the six");
    assert_eq!(got, Some(("449".to_owned(), list)));
    let mut shrine = s(&["T260"]);
    shrine.extend(ids("282", 287));
    let got = brief(
        &d,
        "449 shrine bundle T260, T282-T287 (fresh): the shrine's",
    );
    assert_eq!(got, Some(("449".to_owned(), shrine)));
    // a range keeps its ids' width; one written backwards, or past a sane span, is its two ends
    let got = brief(&d, "385 T02-T04: three");
    assert_eq!(got, Some(("385".to_owned(), s(&["T02", "T03", "T04"]))));
    let got = brief(&d, "385 T09-T03, T05a: backwards");
    assert_eq!(got, Some(("385".to_owned(), s(&["T09", "T03", "T05a"]))));
    let got = brief(&d, "385 T1-T9999: past a span");
    assert_eq!(got, Some(("385".to_owned(), s(&["T1", "T9999"]))));
    // a landing agent names no task before its colon: no builder of a task
    assert_eq!(
        brief(&d, "449 batch landing: clear the six refusals and land"),
        None
    );
}
