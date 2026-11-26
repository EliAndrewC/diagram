//! The record's merge (451 T256): both sides' verdicts kept, an entry whole, the log's rows each side's in order.

use serde_json::{json, Value};

use super::{merge_files, merge_records};

fn entry(sha: &str, verdict: &str, day: &str) -> Value {
    json!({"sha256": sha, "verdict": verdict, "reviewed": day, "declared": "spec-fidelity"})
}

fn row(block: &str) -> Value {
    json!({"reviewed": "2026-11-26", "blocks": [block], "verdict": "CLEAR", "decisions": []})
}

fn merged(base: &Value, ours: &Value, theirs: &Value) -> Value {
    merge_records(&base.to_string(), &ours.to_string(), &theirs.to_string()).unwrap()
}

fn base() -> Value {
    json!({
        "feature": "451-x",
        "blocks": {"## Summary": entry("s0", "CLEAR", "2026-11-20")},
        "block_reviews": [row("## Summary")],
        "tasks": {"T01": {"section_sha256": "t1", "verdict": "CLEAR", "reviewed": "2026-11-20"}}
    })
}

/// Branch `a` adds T256's verdict, its block and its row, as `record_task`'s CLEAR path writes them.
fn adding(task: &str) -> Value {
    let mut v = base();
    v["tasks"][task] = json!({"section_sha256": format!("{task}-sha"), "verdict": "CLEAR", "reviewed": "2026-11-26"});
    v["blocks"][format!("### {task} x")] = entry(&format!("{task}-b"), "CLEAR", "2026-11-26");
    v["block_reviews"]
        .as_array_mut()
        .unwrap()
        .push(row(&format!("### {task} x")));
    v
}

#[test]
fn two_sides_each_adding_a_task_keep_both() {
    let got = merged(&base(), &adding("T256"), &adding("T257"));
    for t in ["T01", "T256", "T257"] {
        assert!(got["tasks"].get(t).is_some(), "{t} kept: {got}");
    }
    for b in ["## Summary", "### T256 x", "### T257 x"] {
        assert!(got["blocks"].get(b).is_some(), "{b} kept");
    }
    let blocks: Vec<&str> = got["block_reviews"]
        .as_array()
        .unwrap()
        .iter()
        .map(|r| r["blocks"][0].as_str().unwrap())
        .collect();
    assert_eq!(blocks, ["## Summary", "### T256 x", "### T257 x"]);
    assert_eq!(got["feature"], "451-x");
}

#[test]
fn the_same_row_on_both_sides_is_kept_once() {
    let got = merged(&base(), &adding("T256"), &adding("T256"));
    assert_eq!(got["block_reviews"].as_array().unwrap().len(), 2);
}

#[test]
fn an_entry_is_whole_and_the_later_review_wins() {
    let (mut ours, mut theirs) = (base(), base());
    ours["blocks"]["## Summary"] = entry("s1", "CLEAR", "2026-11-25");
    theirs["blocks"]["## Summary"] = entry("s2", "BLOCKED", "2026-11-26");
    assert_eq!(
        merged(&base(), &ours, &theirs)["blocks"]["## Summary"],
        entry("s2", "BLOCKED", "2026-11-26")
    );
    ours["blocks"]["## Summary"] = entry("s1", "CLEAR", "2026-11-27");
    assert_eq!(
        merged(&base(), &ours, &theirs)["blocks"]["## Summary"],
        entry("s1", "CLEAR", "2026-11-27")
    );
    ours["blocks"]["## Summary"] = entry("s1", "CLEAR", "2026-11-26");
    assert_eq!(
        merged(&base(), &ours, &theirs)["blocks"]["## Summary"]["sha256"],
        "s2"
    );
}

#[test]
fn one_side_changed_is_that_sides() {
    let mut ours = base();
    ours["blocks"]["## Summary"] = entry("s1", "CLEAR", "2026-11-25");
    assert_eq!(
        merged(&base(), &ours, &base())["blocks"]["## Summary"]["sha256"],
        "s1"
    );
    assert_eq!(
        merged(&base(), &base(), &ours)["blocks"]["## Summary"]["sha256"],
        "s1"
    );
}

#[test]
fn a_removal_holds_unless_the_other_side_changed_it() {
    let mut gone = base();
    gone["blocks"]
        .as_object_mut()
        .unwrap()
        .shift_remove("## Summary");
    assert!(merged(&base(), &gone, &base())["blocks"]
        .get("## Summary")
        .is_none());
    assert!(merged(&base(), &base(), &gone)["blocks"]
        .get("## Summary")
        .is_none());
    let mut changed = base();
    changed["blocks"]["## Summary"] = entry("s1", "CLEAR", "2026-11-26");
    assert_eq!(
        merged(&base(), &gone, &changed)["blocks"]["## Summary"]["sha256"],
        "s1"
    );
    assert_eq!(
        merged(&base(), &changed, &gone)["blocks"]["## Summary"]["sha256"],
        "s1"
    );
}

#[test]
fn a_map_one_side_lacks_is_merged_whole() {
    let mut ours = base();
    ours["tasks"] = json!("not a map");
    assert_eq!(merged(&base(), &ours, &base())["tasks"], json!("not a map"));
}

#[test]
fn an_empty_side_is_an_empty_record_and_a_side_not_json_is_named() {
    let got = merge_records("", &adding("T256").to_string(), &adding("T257").to_string()).unwrap();
    assert!(got["tasks"].get("T256").is_some() && got["tasks"].get("T257").is_some());
    assert_eq!(merge_records("{", "{}", "{}").unwrap_err(), "the base");
    assert_eq!(merge_records("{}", "<<<<<<<", "{}").unwrap_err(), "ours");
    assert_eq!(merge_records("{}", "{}", "x").unwrap_err(), "theirs");
}

#[test]
fn the_driver_writes_ours_and_leaves_a_bad_side_unmerged() {
    let dir = crate::checks::scratch("plan-merge");
    let (b, o, t) = (dir.join("O"), dir.join("A"), dir.join("B"));
    std::fs::write(&b, base().to_string()).unwrap();
    std::fs::write(&o, adding("T256").to_string()).unwrap();
    std::fs::write(&t, adding("T257").to_string()).unwrap();
    let got = merge_files(&b, &o, &t);
    assert_eq!(got.code, 0, "{}", got.stderr);
    let written = std::fs::read_to_string(&o).unwrap();
    assert!(written.starts_with("{\n \"feature\""));
    let v: Value = serde_json::from_str(&written).unwrap();
    assert!(v["tasks"].get("T257").is_some());
    std::fs::write(&t, "<<<<<<< ours").unwrap();
    let got = merge_files(&b, &o, &t);
    assert_eq!(got.code, 1);
    assert!(
        got.stderr
            .contains("theirs of plan-review.json is not JSON")
            && got.stderr.contains("git add"),
        "{}",
        got.stderr
    );
    assert_eq!(std::fs::read_to_string(&o).unwrap(), written);
    let got = merge_files(&b, &dir.join("no-such-dir").join("A"), &o);
    assert_eq!(got.code, 1);
    assert!(got.stderr.contains("cannot write"), "{}", got.stderr);
}

#[test]
fn the_verb_is_git_s_driver() {
    let dir = crate::checks::scratch("plan-merge-verb");
    let (b, o, t) = (dir.join("O"), dir.join("A"), dir.join("B"));
    std::fs::write(&b, base().to_string()).unwrap();
    std::fs::write(&o, adding("T256").to_string()).unwrap();
    std::fs::write(&t, adding("T257").to_string()).unwrap();
    let words = [
        "merge-record",
        b.to_str().unwrap(),
        o.to_str().unwrap(),
        t.to_str().unwrap(),
    ];
    let got = super::super::tests::run(&dir, &words);
    assert_eq!(got.code, 0, "{}", got.stderr);
    let v: Value = serde_json::from_str(&std::fs::read_to_string(&o).unwrap()).unwrap();
    assert!(v["tasks"].get("T256").is_some() && v["tasks"].get("T257").is_some());
}
