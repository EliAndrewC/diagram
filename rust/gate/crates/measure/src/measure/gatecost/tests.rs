//! Only runs that did the work, and like with like.

use std::path::Path;

use serde_json::json;

use super::{class_count, cli, median_seconds};

fn put(root: &Path, name: &str, row: &serde_json::Value) {
    let path = root.join("dev/run-log").join(name);
    std::fs::create_dir_all(path.parent().unwrap()).unwrap();
    std::fs::write(path, row.to_string()).unwrap();
}

#[test]
fn the_median_ignores_short_circuits_failures_and_other_scopes() {
    let root = crate::checks::scratch("gatecost");
    let rows = [
        ("green", "reference", 100, 3, false),
        ("already-verified", "reference", 0, 9, false),
        ("failed:test", "reference", 4, 3, false),
        ("green", "full", 900, 3, false),
        ("green", "reference", 30, 5, true),
    ];
    let mut n = 0;
    for (result, scope, seconds, times, incremental) in rows {
        for _ in 0..times {
            let mut row = json!({"utc": format!("2026-08-30T{n:02}:00:00Z"), "target": "done", "scope": scope, "seconds": seconds, "result": result});
            if incremental {
                row["mode"] = json!("incremental");
            }
            put(&root, &format!("{n}.json"), &row);
            n += 1;
        }
    }
    put(&root, "broken.json", &json!(null));
    std::fs::write(root.join("dev/run-log/notjson.json"), "x").unwrap();
    assert_eq!(
        median_seconds(&root, "done", Some("reference"), None),
        Some(100)
    );
    assert_eq!(median_seconds(&root, "nothing", None, None), None);
}

#[test]
fn a_class_median_excludes_entries_that_carry_no_class() {
    let root = crate::checks::scratch("gatecost-class");
    let base = |seconds: i64, utc: &str, cache: Option<&str>| {
        let mut r = json!({"target": "done", "scope": "reference", "result": "green", "seconds": seconds, "utc": utc});
        if let Some(c) = cache {
            r["cache"] = json!(c);
        }
        r
    };
    put(&root, "0.json", &base(900, "2026-01-01", None));
    put(&root, "1.json", &base(100, "2026-01-02", Some("warm")));
    put(&root, "2.json", &base(700, "2026-01-03", Some("cold")));
    assert_eq!(
        median_seconds(&root, "done", Some("reference"), Some("warm")),
        Some(100)
    );
    assert_eq!(
        median_seconds(&root, "done", Some("reference"), Some("cold")),
        Some(700)
    );
    assert_eq!(
        class_count(&root, "done", Some("reference"), Some("warm")),
        1
    );
    assert_eq!(
        median_seconds(&root, "done", Some("reference"), None),
        Some(700)
    );
}

#[test]
fn a_clone_reads_the_mirror_above_it_a_run_counted_once_and_only_the_last_25() {
    let main = crate::checks::scratch("gatecost-mirror");
    let clone = main.join(".clones/c");
    let row = |s: i64, utc: String| json!({"target": "done", "result": "green", "seconds": s, "utc": utc});
    put(&main, "same.json", &row(10, "2026-01-01".to_owned()));
    put(&clone, "same.json", &row(20, "2026-01-02".to_owned()));
    put(&main, "other.json", &row(40, "2026-01-03".to_owned()));
    assert_eq!(class_count(&clone, "done", None, None), 2);
    for n in 0..30 {
        put(
            &clone,
            &format!("{n}.json"),
            &row(n, format!("2026-02-{n:02}")),
        );
    }
    assert_eq!(class_count(&clone, "done", None, None), 25);
}

fn ask(root: &Path, words: &[&str]) -> String {
    let owned: Vec<String> = words.iter().map(|s| (*s).to_owned()).collect();
    cli(&owned, root).stdout
}

#[test]
fn the_command_line_prints_the_figure_or_nothing() {
    let root = crate::checks::scratch("gatecost-cli");
    put(
        &root,
        "0.json",
        &json!({"target": "done", "result": "green", "seconds": 7, "scope": "reference", "utc": "u", "cache": "warm"}),
    );
    assert_eq!(ask(&root, &["done"]), "7\n");
    assert_eq!(ask(&root, &[]), "");
    assert_eq!(ask(&root, &["nothing"]), "");
    assert_eq!(ask(&root, &["--count", "done", "reference", ""]), "1\n");
    assert_eq!(ask(&root, &["--count", "done", "reference", "cold"]), "0\n");
}

#[test]
fn a_class_in_the_third_word_filters_the_median() {
    let root = crate::checks::scratch("gatecost-third");
    let row = |s: i64, cache: &str| json!({"target": "done", "result": "green", "scope": "reference", "seconds": s, "utc": "u", "cache": cache});
    put(&root, "0.json", &row(100, "warm"));
    put(&root, "1.json", &row(700, "cold"));
    assert_eq!(ask(&root, &["done", "reference", "warm"]), "100\n");
    assert_eq!(ask(&root, &["done", "reference", "cold"]), "700\n");
    assert_eq!(ask(&root, &["done", "reference", ""]), "400\n");
}
