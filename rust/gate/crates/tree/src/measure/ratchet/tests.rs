//! A target that gets slower fails, each regime by its own rule.

use std::path::{Path, PathBuf};

use serde_json::{json, Value};

use super::{
    best_round, ceiling_for, ceiling_for_class, cli, decide, derive_ceiling, find, round_even,
    round_of, slowdown, spin, verdict, workers_of, Asked, Ratchet,
};

fn constant(_: usize) -> f64 {
    1.0
}

fn repository() -> PathBuf {
    Path::new(env!("CARGO_MANIFEST_DIR")).join("../../../..")
}

fn real(target: &str) -> Ratchet {
    find(&repository(), target).unwrap()
}

fn runs(seconds: i64) -> Asked<'static> {
    Asked {
        seconds: Some(seconds),
        ..Asked::default()
    }
}

#[test]
fn the_derivation_reproduces_the_gm_s_own_numbers_and_never_passes_them() {
    assert_eq!(derive_ceiling(11, Some(15)), 15);
    assert_eq!(derive_ceiling(35, Some(45)), 45);
    for b in [11, 12, 20, 35, 100, 155, 310] {
        assert!(derive_ceiling(b, Some(15)) <= 15);
    }
    assert_eq!(derive_ceiling(100, None), 130);
}

#[test]
fn quick_is_judged_on_the_run_itself_at_the_gm_s_fifteen_seconds() {
    let r = real("quick");
    assert!(verdict("quick", Some(&r), runs(14), 1.0).0);
    let (ok, msg) = verdict("quick", Some(&r), runs(15), 1.0);
    assert!(!ok && msg.contains("15s ceiling"));
}

#[test]
fn quick_is_judged_net_of_the_host_s_measured_slowdown() {
    let r = real("quick");
    let (ok, msg) = verdict("quick", Some(&r), runs(18), 1.5);
    assert!(ok && msg.contains("18s raw, 12s net") && msg.contains("15s ceiling"));
    let (ok, msg) = verdict("quick", Some(&r), runs(30), 1.5);
    assert!(!ok && msg.contains("20s (30s raw, net of the host's 1.50x slowdown)"));
    assert!(!verdict("quick", Some(&r), runs(15), 1.0).0);
    let (ok, msg) = verdict("quick", Some(&r), runs(12), 1.0);
    assert!(ok && msg.contains("slowdown not measured"));
    let pinned = r.calibration_s.unwrap();
    assert!(r.calibration_reason.contains("measured 2026-"));
    assert!((slowdown(&r, 6, 2, &|_| pinned * 2.0) - 2.0).abs() < 1e-9);
    assert!((slowdown(&r, 6, 5, &|_| pinned / 2.0) - 1.0).abs() < f64::EPSILON);
    assert!((slowdown(&real("done"), 6, 5, &constant) - 1.0).abs() < f64::EPSILON);
    assert!(spin(1000) >= 0.0 && round_of(2, 1000) >= 0.0);
    assert!((best_round(1, 3, &constant) - 1.0).abs() < f64::EPSILON);
    assert_eq!(
        (
            round_even(2.5),
            round_even(3.5),
            round_even(2.4),
            round_even(2.6)
        ),
        (2, 4, 2, 3)
    );
}

#[test]
fn done_uses_the_median_until_its_baseline_reaches_thirty_five() {
    let done = real("done");
    let (ceiling, mode) = ceiling_for(&done);
    assert_eq!(mode, "median");
    let asked = |seconds, median| Asked {
        seconds: Some(seconds),
        median: Some(median),
        ..Asked::default()
    };
    assert!(verdict("done", Some(&done), asked(ceiling * 2, ceiling - 1), 1.0).0);
    let (ok, msg) = verdict("done", Some(&done), asked(10, ceiling), 1.0);
    assert!(
        !ok && msg.contains(&format!("{ceiling}s ceiling"))
            && msg.contains("median of recent green runs")
    );
    let pinned = |baseline| Ratchet {
        baseline,
        hard_ceiling: Some(45),
        hard_at_or_below: Some(35),
        compare: "median".to_owned(),
        armed: true,
        ..Ratchet::default()
    };
    assert_eq!(ceiling_for(&pinned(35)), (45, "run".to_owned()));
    assert_eq!(ceiling_for(&pinned(25)).0, 45);
}

#[test]
fn every_pinned_baseline_carries_its_own_written_reason_and_the_aws_row_is_off() {
    let data: Value = serde_json::from_str(
        &std::fs::read_to_string(repository().join("dev/ratchets.json")).unwrap(),
    )
    .unwrap();
    for name in data.as_object().unwrap().keys() {
        let r = real(name);
        assert!(r.reason.split_whitespace().count() >= 5);
        assert!(r.baseline_cold.is_none() || r.reason_cold.split_whitespace().count() >= 5);
    }
    let full = real("test-full");
    assert!(!full.armed && verdict("test-full", Some(&full), runs(99_999), 1.0).0);
    assert!(verdict("no-such-target", None, runs(9999), 1.0).0);
    assert!(verdict("done", Some(&real("done")), Asked::default(), 1.0).0);
    assert!(find(&repository(), "no-such-target").is_none());
    assert!(find(Path::new("/nonexistent"), "done").is_none());
}

#[test]
fn a_failure_says_what_to_do() {
    let (_, msg) = verdict("quick", Some(&real("quick")), runs(99), 1.0);
    for expected in [
        "make audit",
        "make durations",
        "pinned baseline",
        "written reason",
    ] {
        assert!(msg.contains(expected));
    }
}

#[test]
fn warm_and_cold_are_separate_populations() {
    let r = real("done");
    let cold = r.baseline_cold.unwrap();
    assert_eq!(
        ceiling_for_class(&r, Some("cold")).0,
        derive_ceiling(cold, None)
    );
    assert_eq!(
        ceiling_for_class(&r, Some("warm")).0,
        derive_ceiling(r.baseline, None)
    );
    let class = |seconds, cache, scope| Asked {
        seconds: Some(seconds),
        cache,
        scope,
        class_runs: Some(0),
        median: None,
    };
    let bar = derive_ceiling(cold, None);
    let (ok, msg) = verdict(
        "done",
        Some(&r),
        class(bar + 1, Some("cold"), Some("reference")),
        1.0,
    );
    assert!(!ok && msg.contains("cold roll cache") && msg.contains(&format!("{cold}s")));
    assert!(
        verdict(
            "done",
            Some(&r),
            class(bar - 1, Some("cold"), Some("reference")),
            1.0
        )
        .0
    );
    let warm = derive_ceiling(r.baseline, None);
    assert!(
        !verdict(
            "done",
            Some(&r),
            class(warm + 1, None, Some("reference")),
            1.0
        )
        .0
    );
    assert!(
        verdict(
            "done",
            Some(&r),
            class(bar + 500, Some("cold"), Some("full")),
            1.0
        )
        .0
    );
}

fn tree(table: &Value) -> PathBuf {
    let root = crate::checks::scratch("ratchet-cli");
    std::fs::create_dir_all(root.join("dev")).unwrap();
    std::fs::write(root.join("dev/ratchets.json"), table.to_string()).unwrap();
    root
}

fn ask(root: &Path, words: &[&str], run: &dyn Fn(usize) -> f64) -> crate::Reply {
    let owned: Vec<String> = words.iter().map(|s| (*s).to_owned()).collect();
    decide(&owned, root, 6, run)
}

#[test]
fn the_command_line_judges_says_and_measures_only_at_the_ceiling() {
    let root = tree(
        &json!({"quick": {"baseline": 11, "reason": "r", "hard_ceiling": 15, "hard_at_or_below": 11, "compare": "run", "calibration_s": 1.0}, "done": {"baseline": 100, "compare": "median"}}),
    );
    let calls = std::cell::Cell::new(0);
    let at_two = |_: usize| {
        calls.set(calls.get() + 1);
        2.0
    };
    assert!(ask(&root, &["quick", "12"], &at_two)
        .stdout
        .contains("slowdown not measured"));
    assert_eq!(ask(&root, &["quick", "99"], &at_two).code, 1);
    assert_eq!(ask(&root, &["quick", "20"], &at_two).code, 0);
    assert_eq!(
        ask(&root, &["done", "5", "1", "warm", "", "9"], &at_two).stdout,
        ""
    );
    assert_eq!(ask(&root, &["done", "x", "200"], &at_two).code, 1);
    assert_eq!(ask(&root, &[], &at_two).code, 0);
    assert_eq!(ask(&root, &["--calibrate"], &at_two).stdout, "2.000\n");
    assert_eq!(ask(&root, &["--calibrate", "1"], &at_two).stdout, "2.000\n");
    assert_eq!(cli(&["nosuch".to_owned()], &root).code, 0);
    assert!(cli(&["--calibrate".to_owned()], &root)
        .stdout
        .ends_with('\n'));
    assert_eq!(
        (
            workers_of(Some("3".to_owned())),
            workers_of(None),
            workers_of(Some("x".to_owned()))
        ),
        (3, 6, 6)
    );
}

#[test]
fn a_class_median_over_its_ceiling_is_printed_and_does_not_refuse() {
    let done = real("done");
    let ceiling = ceiling_for(&done).0;
    let classed = Asked {
        median: Some(ceiling),
        cache: Some("warm"),
        ..Asked::default()
    };
    let (ok, msg) = verdict("done", Some(&done), classed, 1.0);
    assert!(ok && msg.contains("at or over its"));
}
