//! The run log's entries and the spend summed from them.

use serde_json::json;

use super::super::fixtures::{put, repo};
use super::{
    log_files, month_to_date, remote_spend_report, stamp, utc_of, write_remote, write_would_have,
    Remote, RUN_LOG,
};

fn remote(result: &str) -> Remote<'_> {
    Remote {
        target: "ci-merge",
        scope: "reference",
        seconds: 9,
        result,
        build_id: "b:1",
        minutes: 10.0,
        reason: "r",
        rate: 0.02,
        compute: "C",
    }
}

#[test]
fn an_entry_carries_where_it_ran_what_it_cost_and_goes_in_its_month() {
    let dir = repo("log");
    let path = write_remote(&dir, &remote("SUCCEEDED")).unwrap();
    assert!(path.parent().unwrap().starts_with(dir.join(RUN_LOG)));
    let e: serde_json::Value =
        serde_json::from_str(&std::fs::read_to_string(&path).unwrap()).unwrap();
    assert_eq!(
        (
            e["where"].as_str(),
            e["minutes"].as_f64(),
            e["cost_usd"].as_f64(),
            e["compute"].as_str()
        ),
        (Some("codebuild"), Some(10.0), Some(0.2), Some("C"))
    );
    assert!(!e["commit"].as_str().unwrap().is_empty());
    assert!(std::fs::read_to_string(&path)
        .unwrap()
        .starts_with("{\n  \"utc\""));
}

#[test]
fn entries_sort_by_name_across_month_folders_and_flat_files() {
    let dir = repo("order");
    put(&dir, "dev/run-log/2026-10/b.json", "{}");
    put(&dir, "dev/run-log/a.json", "{}");
    put(&dir, "dev/run-log/2026-11/c.json", "{}");
    put(&dir, "dev/run-log/2026-11/not.txt", "");
    let names: Vec<String> = log_files(&dir, RUN_LOG)
        .iter()
        .map(|p| p.file_name().unwrap().to_string_lossy().into_owned())
        .collect();
    assert_eq!(names, ["a.json", "b.json", "c.json"]);
}

#[test]
fn only_a_real_build_is_spend_and_a_would_have_is_reported_as_never_spent() {
    let dir = repo("spend");
    assert!(
        remote_spend_report(&dir).contains("(no remote runs yet)")
            && remote_spend_report(&dir).contains("(none)")
    );
    write_remote(&dir, &remote("SUCCEEDED")).unwrap();
    write_would_have(&dir, "ci-check", "reference", 10.0, "remote off").unwrap();
    put(&dir, "dev/run-log/bad.json", "not json");
    put(
        &dir,
        "dev/run-log/old.json",
        &json!({"where": "codebuild", "utc": "2020-01-01T00:00:00Z", "cost_usd": 5.0}).to_string(),
    );
    assert!((month_to_date(&dir, None) - 0.2).abs() < 1e-9);
    assert!((month_to_date(&dir, Some("2020-01")) - 5.0).abs() < 1e-9);
    let report = remote_spend_report(&dir);
    assert!(
        report.contains("month-to-date: $0.20 over 1 run(s) this month")
            && report.contains("1 attempt(s), ~$0.20 not spent"),
    );
    assert!(report.contains("ci-check") && report.contains("remote off"));
}

#[test]
fn a_stamp_sorts_in_write_order() {
    assert_eq!(stamp(0, 7), "19700101T000000000007");
    assert_eq!(utc_of(0), "1970-01-01T00:00:00Z");
}
