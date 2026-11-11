//! The record's rules; the entries a stage's landing makes stale, and the entry no stage can name.

use std::path::{Path, PathBuf};
use std::process::Command;

use super::{cli, load, missing, ranges, split};

fn scratch(tag: &str) -> PathBuf {
    let dir = std::env::temp_dir().join(format!("l7r-gate-exempt-{tag}-{}", std::process::id()));
    let _ = std::fs::remove_dir_all(&dir);
    std::fs::create_dir_all(dir.join("dev")).unwrap();
    dir
}

fn record(dir: &Path, entries: &str) {
    std::fs::write(
        dir.join("dev/coverage-exempt.json"),
        format!("{{\"ruling\": \"r\", \"entries\": [{entries}]}}"),
    )
    .unwrap();
}

fn file(dir: &Path, rel: &str) {
    std::fs::write(dir.join(rel), "x\n").unwrap();
}

fn accepted(dir: &Path, names: &str) {
    std::fs::write(
        dir.join("dev/work-budget.json"),
        format!("{{\"stages\": {{{names}}}}}"),
    )
    .unwrap();
}

fn stand_in(dir: &Path, body: &str) -> String {
    let path = dir.join("stand-in");
    std::fs::write(&path, format!("#!/bin/bash\n{body}\n")).unwrap();
    Command::new("chmod").arg("+x").arg(&path).status().unwrap();
    path.to_string_lossy().into_owned()
}

fn ask(dir: &Path, python: &str, args: &[&str]) -> crate::Reply {
    cli(
        &args.iter().map(|s| (*s).to_owned()).collect::<Vec<_>>(),
        dir,
        python,
    )
}

const LIVE: &str = r#"{"path": "a.py", "stages": ["seat", "hem"]}"#;
const DONE: &str = r#"{"path": "b.py", "stages": ["sink"]}"#;
const GONE: &str = r#"{"path": "gone.py", "stages": ["seat"]}"#;

fn three(tag: &str) -> PathBuf {
    let dir = scratch(tag);
    record(&dir, &[LIVE, DONE, GONE].join(","));
    file(&dir, "a.py");
    file(&dir, "b.py");
    accepted(
        &dir,
        r#""sink": {"status": "accepted"}, "seat": {"status": "budgeted"}, "hem": null"#,
    );
    dir
}

#[test]
fn no_record_exempts_nothing() {
    let dir = scratch("none");
    std::fs::remove_dir(dir.join("dev")).unwrap();
    assert_eq!(ask(&dir, "x", &["omit"]).stdout, "\n");
    assert_eq!(ask(&dir, "x", &["exempt"]).stdout, "");
    assert_eq!(ask(&dir, "x", &["report"]).stdout, "");
    assert_eq!(load(&dir).unwrap()["entries"], serde_json::json!([]));
}

#[test]
fn an_entry_naming_no_stages_refuses_rather_than_reading_as_accepted() {
    let dir = scratch("nostage");
    file(&dir, "a.py");
    for bad in [r#"{"path": "a.py", "stages": []}"#, r#"{"path": "a.py"}"#] {
        record(&dir, bad);
        let refused = ask(&dir, "x", &["omit"]);
        assert_eq!(refused.code, 1);
        assert!(refused.stderr.contains("a.py names no stages"));
    }
    std::fs::write(dir.join("dev/coverage-exempt.json"), "not json").unwrap();
    assert!(load(&dir).is_err());
    record(&dir, LIVE);
    std::fs::write(dir.join("dev/work-budget.json"), "not json").unwrap();
    assert_eq!(ask(&dir, "x", &["exempt"]).code, 1);
}

#[test]
fn an_entry_is_stale_when_its_file_is_gone_or_every_stage_it_serves_is_accepted() {
    let dir = three("stale");
    let (live, stale) = split(&dir).unwrap();
    assert_eq!(live.len(), 1);
    assert_eq!(live[0]["path"], "a.py");
    let whys: Vec<(&str, &str)> = stale
        .iter()
        .map(|(e, w)| (e["path"].as_str().unwrap(), w.as_str()))
        .collect();
    assert_eq!(
        whys,
        [
            (
                "b.py",
                "every stage it serves is accepted in Rust (sink); the thin door keeps the floor"
            ),
            ("gone.py", "the file is gone")
        ]
    );
    assert_eq!(ask(&dir, "x", &["omit"]).stdout, "--omit=a.py\n");
    assert_eq!(ask(&dir, "x", &["exempt"]).stdout, "a.py\n");
    assert_eq!(ask(&dir, "x", &["stale"]).stdout, "b.py\tevery stage it serves is accepted in Rust (sink); the thin door keeps the floor\ngone.py\tthe file is gone\n");
}

#[test]
fn the_list_names_each_and_a_prune_drops_the_stale_ones_and_keeps_the_rest() {
    let dir = three("list");
    let listed = ask(&dir, "x", &["list"]).stdout;
    assert!(
        listed.starts_with("a.py  (seat, hem)\nSTALE b.py - ")
            && listed.ends_with("coverage-exempt: 1 exempt, 2 stale\n"),
    );
    let pruned = ask(&dir, "x", &["list", "--prune"]).stdout;
    assert!(
        pruned.contains("coverage-exempt: dropped gone.py - the file is gone\n")
            && pruned.ends_with("coverage-exempt: 1 exempt, 0 stale\n")
    );
    let text = std::fs::read_to_string(dir.join("dev/coverage-exempt.json")).unwrap();
    assert!(
        text.starts_with("{\n \"ruling\": \"r\",\n \"entries\": [\n  {") && text.ends_with("}\n")
    );
}

#[test]
fn the_report_gives_unrun_lines_as_information_and_a_stale_entry_fails_it() {
    let dir = three("report");
    let py = stand_in(&dir, "echo 3,4,5,9");
    let done = ask(&dir, &py, &["report", "elsewhere.cov"]);
    assert_eq!(done.code, 1);
    assert!(done.stdout.contains("a.py - unrun lines: 3-5, 9\ncoverage: 1 files slated for the Rust port are exempt from the floor (1 with unrun lines;"));
    assert!(done.stdout.contains("COVERAGE: dev/coverage-exempt.json names gone.py, which is stale - the file is gone. Drop it: make coverage-exempt PRUNE=1\n"));
    ask(&dir, "x", &["list", "--prune"]);
    let clean = ask(&dir, &stand_in(&dir, "echo"), &["report"]);
    assert_eq!(
        (clean.code, clean.stdout.contains("(0 with unrun lines;")),
        (0, true)
    );
}

#[test]
fn a_python_that_cannot_answer_fails_the_report_and_no_live_entry_asks_nothing() {
    let dir = three("py");
    assert!(ask(&dir, "/no/such/python", &["report"])
        .stderr
        .contains("/no/such/python"));
    let refused = stand_in(&dir, "echo boom >&2; exit 1");
    assert!(ask(&dir, &refused, &["report"])
        .stderr
        .contains("answered no unrun lines: boom"));
    assert!(missing(&dir, &[], ".coverage", "/no/such/python")
        .unwrap()
        .is_empty());
    assert_eq!(ranges(&[1, 2, 7]), "1-2, 7");
    assert_eq!(ask(&dir, "x", &["nonsense"]).code, 2);
}
