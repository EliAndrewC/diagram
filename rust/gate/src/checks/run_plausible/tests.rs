//! A run too fast to have worked does not get to say it passed.

use super::{baseline, check, cli, dry_run, floor_for, ABSOLUTE_MIN};
use crate::checks::scratch;

fn root() -> std::path::PathBuf {
    let dir = scratch("plausible");
    std::fs::create_dir_all(dir.join("dev")).unwrap();
    std::fs::write(dir.join("dev/ratchets.json"), "{\"quick\": {\"baseline\": 11}, \"done\": {\"baseline\": 400}, \"zero\": {\"baseline\": 0}}").unwrap();
    dir
}

fn ask(dir: &std::path::Path, flags: &str, words: &[&str]) -> super::Outcome {
    let owned: Vec<String> = words.iter().map(|s| (*s).to_owned()).collect();
    cli(&owned, dir, flags)
}

#[test]
fn a_dry_run_may_not_record_and_only_the_flag_word_says_so() {
    assert!(check(&root(), "done", 320.0, "n", "full")
        .unwrap()
        .contains("DRY RUN"));
    assert!(dry_run("n") && dry_run("nrR"));
    assert!(
        !dry_run("") && !dry_run("REASON=nothing") && !dry_run("-- REASON=iterating on Inashiro")
    );
}

#[test]
fn a_run_below_the_floor_may_not_record_and_an_incremental_run_has_the_absolute_floor() {
    let dir = root();
    assert!(check(&dir, "done", 4.0, "", "full")
        .unwrap()
        .contains("floor"));
    assert_eq!(check(&dir, "done", 320.0, "", "full"), None);
    assert_eq!(check(&dir, "done", 6.0, "", "incremental"), None);
    assert!(check(&dir, "done", 4.0, "", "incremental").is_some());
    assert_eq!(check(&dir, "no-such-target", 0.0, "", "full"), None);
}

#[test]
fn the_floor_is_derived_from_the_pinned_ratchet_baseline() {
    let dir = root();
    assert_eq!(floor_for(&dir, "done"), Some(40));
    assert_eq!(floor_for(&dir, "quick"), Some(ABSOLUTE_MIN));
    assert_eq!(baseline(&dir, "quick"), Some(11));
    assert_eq!(floor_for(&dir, "no-such-target"), None);
    assert_eq!(floor_for(&dir, "zero"), None);
    assert_eq!(baseline(&scratch("no-ratchet"), "done"), None);
}

#[test]
fn the_reuse_path_is_guarded_too_and_the_command_line_says_how_to_use_it() {
    let dir = root();
    let refused = ask(&dir, "n", &["--reuse", "done"]);
    assert!(refused.code == 1 && refused.stderr.contains("DRY RUN"));
    assert_eq!(ask(&dir, "", &["--reuse", "done"]).code, 0);
    assert_eq!(ask(&dir, "", &["done", "not-a-number"]).code, 0);
    assert_eq!(ask(&dir, "", &["done", "320"]).code, 0);
    assert_eq!(ask(&dir, "", &["done", "4", "incremental"]).code, 1);
    assert_eq!(ask(&dir, "", &[]).code, 2);
}

fn repository() -> std::path::PathBuf {
    std::path::Path::new(env!("CARGO_MANIFEST_DIR")).join("../..")
}

#[test]
fn the_dry_run_floor_still_reads_the_ratchet_s_baseline() {
    let repo = repository();
    let floor = floor_for(&repo, "done").unwrap();
    assert_eq!(
        floor,
        ABSOLUTE_MIN.max(baseline(&repo, "done").unwrap() / 10)
    );
    assert!(floor_for(&repo, "quick").is_some());
    assert_eq!(floor_for(&repo, "no-such-target"), None);
}

fn walk(dir: &std::path::Path, out: &mut Vec<serde_json::Value>) {
    for entry in std::fs::read_dir(dir).into_iter().flatten().flatten() {
        let path = entry.path();
        if path.is_dir() {
            walk(&path, out);
        } else if let Ok(row) =
            serde_json::from_str(&std::fs::read_to_string(&path).unwrap_or_default())
        {
            out.push(row);
        }
    }
}

fn median(values: &mut [f64]) -> f64 {
    values.sort_by(f64::total_cmp);
    let n = values.len();
    if n % 2 == 1 {
        values[n / 2]
    } else {
        values[n / 2 - 1].midpoint(values[n / 2])
    }
}

#[test]
fn the_floor_catches_the_known_dry_runs_in_the_recorded_history() {
    let repo = repository();
    let mut rows = Vec::new();
    walk(&repo.join("dev/run-log"), &mut rows);
    rows.retain(|d| d["target"] == "done" && d["result"] == "green" && d["utc"].is_string());
    assert!(rows.len() > 100);
    let seconds = |d: &serde_json::Value| d["seconds"].as_f64().unwrap_or(0.0);
    let mut by_day: std::collections::HashMap<String, Vec<f64>> = std::collections::HashMap::new();
    for d in &rows {
        by_day
            .entry(d["utc"].as_str().unwrap()[..10].to_owned())
            .or_default()
            .push(seconds(d));
    }
    let medians: std::collections::HashMap<String, f64> = by_day
        .into_iter()
        .map(|(k, mut v)| (k, median(&mut v)))
        .collect();
    let implausible: Vec<&serde_json::Value> = rows
        .iter()
        .filter(|d| {
            let day = medians[&d["utc"].as_str().unwrap()[..10]];
            day > 0.0 && seconds(d) < 0.02 * day
        })
        .collect();
    let mut stamps: Vec<&str> = implausible
        .iter()
        .map(|d| &d["utc"].as_str().unwrap()[..19])
        .collect();
    stamps.sort_unstable();
    assert_eq!(stamps, ["2026-09-05T18:01:45", "2026-09-05T18:07:40"]);
    assert!(implausible
        .iter()
        .all(|d| check(&repo, "done", seconds(d), "", "full").is_some()));
}
