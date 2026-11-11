//! The timing of each row, the skip and the total.

use std::process::Command;

use serde_json::{json, Value};

use super::{cli, load, measure, report};

fn sh(body: &str) -> Command {
    let mut c = Command::new("sh");
    c.args(["-c", body]);
    c
}

#[test]
fn each_row_reports_its_last_run_and_its_exit() {
    let got = measure(
        vec![
            ("fine".to_owned(), Some(sh("exit 0"))),
            ("red".to_owned(), Some(sh("exit 3"))),
            ("absent".to_owned(), None),
        ],
        2,
    );
    assert_eq!(got[0]["exit"], 0);
    assert_eq!(got[1]["exit"], 3);
    assert!(got[0]["wall_s"].is_f64());
    assert_eq!(
        got[2],
        json!({"check": "absent", "skipped": "not in this clone"})
    );
}

#[test]
fn a_row_that_cannot_start_reports_no_exit_and_no_run_count_still_runs_once() {
    let touched = crate::checks::scratch("pct-once").join("t");
    let body = format!("echo x >> {}", touched.display());
    let _ = measure(vec![("once".to_owned(), Some(sh(&body)))], 0);
    assert_eq!(
        std::fs::read_to_string(&touched).unwrap().lines().count(),
        1
    );
    let got = measure(
        vec![("gone".to_owned(), Some(Command::new("/nonexistent/x")))],
        1,
    );
    assert_eq!(got[0]["exit"], -1);
}

#[test]
fn the_report_sums_what_ran() {
    let rows = [
        json!({"check": "a", "wall_s": 1.25, "exit": 0}),
        json!({"check": "b", "skipped": "not in this clone"}),
        json!({"check": "c", "wall_s": 0.5, "exit": 2}),
    ];
    let (out, total) = report(&rows, 4.25);
    assert_eq!(out, "  1.25 s  exit 0  a\n     -    b (not in this clone)\n  0.50 s  exit 2  c\n  1.75 s  in all, load 4.2\n");
    assert!((total - 1.75).abs() < f64::EPSILON);
}

#[test]
fn the_load_is_the_first_word_of_the_file() {
    assert!((load("4.25 1 1 1/1 1\n") - 4.25).abs() < f64::EPSILON);
    assert!(load("").abs() < f64::EPSILON);
}

#[test]
fn the_cli_keeps_the_json_it_is_asked_to() {
    let root = crate::checks::scratch("pct-cli");
    std::fs::create_dir_all(root.join("scripts/gates")).unwrap();
    crate::write_executable(
        &root.join("scripts/gates/l7r-gate.sh"),
        "#!/bin/sh\nexit 0\n",
    );
    let (there, kept) = (root.display().to_string(), root.join("k.json"));
    let args: Vec<String> = [
        "--root",
        &there,
        "--runs",
        "1",
        "--json",
        &kept.display().to_string(),
    ]
    .iter()
    .map(|s| (*s).to_owned())
    .collect();
    let got = cli(&args, &root, &root);
    assert_eq!(got.code, 0, "{}", got.stderr);
    assert!(
        got.stdout.contains("push checks (one process)") && got.stdout.contains("in all, load")
    );
    let saved: Value = serde_json::from_str(&std::fs::read_to_string(&kept).unwrap()).unwrap();
    assert!(saved["total_s"].is_f64() && saved["rows"].is_array());
    assert_eq!(cli(&[], &root, &root).code, 0);
    assert_eq!(
        cli(
            &["--root".to_owned(), "/nonexistent".to_owned()],
            &root,
            &root
        )
        .code,
        2
    );
    let args: Vec<String> = [
        "--root",
        &there,
        "--runs",
        "1",
        "--json",
        "/nonexistent/k.json",
    ]
    .iter()
    .map(|s| (*s).to_owned())
    .collect();
    assert_eq!(cli(&args, &root, &root).code, 1);
}
