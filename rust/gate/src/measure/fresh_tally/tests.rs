//! Fresh seeds pooled by form and cause.

use std::path::Path;

use serde_json::{json, Value};

use super::{cause, cli};

fn put(dir: &Path, name: &str, r: &Value) {
    std::fs::write(dir.join(name), r.to_string()).unwrap();
}

fn ask(dir: &Path, words: &[&str]) -> String {
    let mut owned = vec!["--log".to_owned(), dir.display().to_string()];
    owned.extend(words.iter().map(|s| (*s).to_owned()));
    cli(&owned, Path::new("/nonexistent")).stdout
}

#[test]
fn fresh_seeds_are_pooled_by_form_and_cause_and_fixed_and_pinned_seeds_are_left_out() {
    let dir = crate::checks::scratch("fresh");
    put(
        &dir,
        "a.json",
        &json!({"utc": "1", "commit": "c1", "first_seed": 1, "seeds": [{"seed": 1, "form": "linear", "failures": ["x"]}, {"seed": 901, "fresh": true, "failures": ["y"]}, {"seed": 20_000, "fresh": true, "form": "linear", "failures": ["lane_knots 2", "lane_knots"]}]}),
    );
    put(
        &dir,
        "b.json",
        &json!({"utc": "2", "commit": "c2", "first_seed": 10_000, "seeds": [{"seed": 10_000, "form": "nucleated", "failures": [{"check": "refused:WebRefused 1"}, {"other": 1}]}, {"seed": 10_001, "form": "nucleated"}, {"seed": 10_002, "verdict": "refused"}]}),
    );
    put(&dir, "features.json", &json!({}));
    std::fs::write(dir.join("broken.json"), "x").unwrap();
    let out = ask(&dir, &[]);
    assert!(out.contains("fresh seeds: 3 of 4 failed (75%)"));
    assert!(
        out.contains("linear      1 of 1 (100%)")
            && out.contains("nucleated   1 of 2 (50%)")
            && out.contains("?           1 of 1 (100%)")
    );
    assert!(
        out.contains("      1  lane_knots")
            && out.contains("      1  refused:WebRefused")
            && out.contains("      1  verdict")
    );
}

#[test]
fn a_seed_rolled_twice_on_one_engine_counts_once_and_commit_and_since_filter() {
    let dir = crate::checks::scratch("fresh-twice");
    let seed = |failures: Value| json!([{"seed": 20_000, "fresh": true, "form": "f", "failures": failures}]);
    put(
        &dir,
        "a.json",
        &json!({"utc": "1", "commit": "c1", "seeds": seed(json!(["x"]))}),
    );
    put(
        &dir,
        "b.json",
        &json!({"utc": "2", "commit": "c1", "seeds": seed(json!([]))}),
    );
    put(
        &dir,
        "c.json",
        &json!({"utc": "3", "commit": "c2", "seeds": seed(json!(["x"]))}),
    );
    assert!(ask(&dir, &["--commit", "c1"]).contains("fresh seeds: 0 of 1 failed (0%)"));
    assert!(ask(&dir, &["--commit", "c2"]).contains("fresh seeds: 1 of 1 failed (100%)"));
    assert!(ask(&dir, &["--since", "3"]).contains("1 of 1"));
    assert!(ask(&dir, &["--since", "9"]).contains("fresh seeds: 0 of 0 failed (-)"));
    assert!(ask(&dir, &["--since", "9"]).contains("  none"));
    assert_eq!(cause(&json!(3)), "3");
    assert_eq!(cause(&json!({"check": 7})), "7");
    let bare = cli(&[], &crate::checks::scratch("fresh-none")).stdout;
    assert!(bare.contains("0 of 0"));
}
