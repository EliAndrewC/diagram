//! What a gate run costs, from the run records.

use serde_json::json;

use super::{cli, fit, growth, records};

#[test]
fn the_fit_the_growth_and_the_records_read() {
    let root = crate::checks::scratch("gate-costs");
    let dir = root.join("dev/run-log/2026-10");
    std::fs::create_dir_all(&dir).unwrap();
    let rows = [
        json!({"utc": "2026-10-24T01:00:00Z", "target": "done", "result": "green", "plan_mode": "full", "selected": 1000, "phases": {"pytest": 110.0, "floors": 3.0}, "seconds": 200, "host": {"load": [2.5]}}),
        json!({"utc": "2026-10-24T02:00:00Z", "target": "done", "result": "green", "plan_mode": "incremental", "selected": 100, "phases": {"pytest": 20.0}, "seconds": 40}),
        json!({"utc": "2026-10-24T03:00:00Z", "target": "idle-done", "result": "green", "plan_mode": "incremental", "selected": 200, "phases": {"pytest": 30.0}, "seconds": 50}),
        json!({"utc": "2026-10-24T04:00:00Z", "target": "done", "result": "green", "seconds": 50}),
        json!({"utc": "2026-10-24T05:00:00Z", "target": "quick", "phases": {}}),
    ];
    for (n, row) in rows.iter().enumerate() {
        std::fs::write(dir.join(format!("{n}.json")), row.to_string()).unwrap();
    }
    std::fs::write(dir.join("x.json"), "not json").unwrap();
    std::fs::write(root.join("dev/run-log/flat.txt"), "").unwrap();
    let recs = records(&root, "");
    assert_eq!(recs.len(), 3);
    assert_eq!(records(&root, "2026-10-24T02").len(), 2);
    let (fixed, per) = fit(&[(1000.0, 110.0), (100.0, 20.0), (200.0, 30.0)]).unwrap();
    assert!((fixed - 10.0).abs() < 1e-6 && (per - 0.1).abs() < 1e-6);
    assert_eq!(fit(&[(5.0, 1.0), (5.0, 2.0)]), None);
    assert_eq!(fit(&[]), None);
    assert_eq!(
        growth(&recs),
        [
            ("2026-10-24T02:00:00Z".to_owned(), 1, 100),
            ("2026-10-24T03:00:00Z".to_owned(), 2, 200)
        ]
    );
    let out = cli(&[], &root).stdout;
    assert!(out.starts_with("utc ") && out.contains("full") && out.contains("2.5"));
    assert!(
        out.contains("fit over 3 run(s): test phase = 10.0 s fixed + 100.00 ms per selected test")
    );
    assert!(out.contains("growth: 2026-10-24T02:00:00Z - incremental run 1 since the last full, 100 test(s) selected"));
    let none = crate::checks::scratch("gate-costs-none");
    assert!(cli(&["--since".to_owned(), "x".to_owned()], &none)
        .stdout
        .contains("too few distinct selections"));
}
