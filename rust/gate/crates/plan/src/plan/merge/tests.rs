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
    merge_records(
        &base.to_string(),
        &ours.to_string(),
        &theirs.to_string(),
        None,
    )
    .unwrap()
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
    let got = merge_records(
        "",
        &adding("T256").to_string(),
        &adding("T257").to_string(),
        None,
    )
    .unwrap();
    assert!(got["tasks"].get("T256").is_some() && got["tasks"].get("T257").is_some());
    assert_eq!(
        merge_records("{", "{}", "{}", None).unwrap_err(),
        "the base"
    );
    assert_eq!(
        merge_records("{}", "<<<<<<<", "{}", None).unwrap_err(),
        "ours"
    );
    assert_eq!(merge_records("{}", "{}", "x", None).unwrap_err(), "theirs");
}

#[test]
fn the_driver_writes_ours_and_leaves_a_bad_side_unmerged() {
    let dir = crate::checks::scratch("plan-merge");
    let (b, o, t) = (dir.join("O"), dir.join("A"), dir.join("B"));
    std::fs::write(&b, base().to_string()).unwrap();
    std::fs::write(&o, adding("T256").to_string()).unwrap();
    std::fs::write(&t, adding("T257").to_string()).unwrap();
    let got = merge_files(&b, &o, &t, None);
    assert_eq!(got.code, 0, "{}", got.stderr);
    let written = std::fs::read_to_string(&o).unwrap();
    assert!(written.starts_with("{\n \"feature\""));
    let v: Value = serde_json::from_str(&written).unwrap();
    assert!(v["tasks"].get("T257").is_some());
    std::fs::write(&t, "<<<<<<< ours").unwrap();
    let got = merge_files(&b, &o, &t, None);
    assert_eq!(got.code, 1);
    assert!(
        got.stderr
            .contains("theirs of plan-review.json is not JSON")
            && got.stderr.contains("git add"),
        "{}",
        got.stderr
    );
    assert_eq!(std::fs::read_to_string(&o).unwrap(), written);
    let got = merge_files(&b, &dir.join("no-such-dir").join("A"), &o, None);
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

/// The plan of 451 T487's trace in small: T05's Approach as the clone filled it, its section's digest, and the stub's block.
const STUB: &str = "### T05 Approach (checklist part A)\n\n1. **The goal, in the world.** <the place as it should be>\n";
const FILLED: &str = "### T05 Approach (checklist part A)\n\n1. **The goal, in the world.** A landing's ticks refuse only what plan-delta names.\n";
const KEY: &str = "### T05 Approach (checklist part A)";

fn plan(block: &str) -> String {
    format!("# Plan\n\n### T05 (why)\n\n- **Approach**: x.\n\n{block}")
}

fn held(plan: &str) -> Value {
    let (b, o, t) = tonight();
    merge_records(&b.to_string(), &o.to_string(), &t.to_string(), Some(plan)).unwrap()
}

/// Ours (the clone): CLEAR on the filled block and on T05's filled section; theirs (a pool tree): a same-day verdict on the stub's,
/// for both - the order of T310's carry, cec429b447.
fn tonight() -> (Value, Value, Value) {
    let digest = |s: &str| l7r_shared::sha256::hex(s.as_bytes());
    let section = |block: &str| plan(block).trim_start_matches("# Plan\n\n").to_owned();
    let (mut ours, mut theirs) = (base(), base());
    ours["blocks"][KEY] = entry(&digest(FILLED), "CLEAR", "2026-11-27");
    theirs["blocks"][KEY] = entry(&digest(STUB), "BLOCKED", "2026-11-27");
    ours["tasks"]["T05"] = json!({"section_sha256": digest(&section(FILLED)), "verdict": "CLEAR", "reviewed": "2026-11-27"});
    theirs["tasks"]["T05"] = json!({"section_sha256": digest(&section(STUB)), "verdict": "BLOCKED", "reviewed": "2026-11-27"});
    (base(), ours, theirs)
}

#[test]
fn the_entry_whose_digest_the_merged_plan_holds_wins_a_same_day_tie() {
    // RED FIRST (451 T495): with no plan the tie is theirs' - the stub's verdict over the clone's CLEAR on the text there
    let (b, o, t) = tonight();
    let blind = merged(&b, &o, &t);
    assert_eq!(blind["blocks"][KEY]["verdict"], "BLOCKED");
    assert_eq!(blind["tasks"]["T05"]["verdict"], "BLOCKED");
    let got = held(&plan(FILLED));
    assert_eq!(got["blocks"][KEY], o["blocks"][KEY]);
    assert_eq!(got["tasks"]["T05"], o["tasks"]["T05"]);
    // the mirror: the merged plan holds the stub, so theirs' entry is the one on the text there
    let got = held(&plan(STUB));
    assert_eq!(got["blocks"][KEY], t["blocks"][KEY]);
    assert_eq!(got["tasks"]["T05"], t["tasks"]["T05"]);
}

#[test]
fn where_the_plan_holds_neither_or_both_the_newer_wins_a_tie_theirs() {
    let other = plan("### T05 Approach (checklist part A)\n\nanother text\n");
    let got = held(&other);
    assert_eq!(got["blocks"][KEY]["verdict"], "BLOCKED");
    let (b, mut o, t) = tonight();
    o["blocks"][KEY]["reviewed"] = json!("2026-11-28");
    let got = merge_records(&b.to_string(), &o.to_string(), &t.to_string(), Some(&other)).unwrap();
    assert_eq!(got["blocks"][KEY]["verdict"], "CLEAR");
    // a key the plan has no block for, and a map that is neither blocks nor tasks, keep the day rule
    assert_eq!(held("# Plan\n")["tasks"]["T05"]["verdict"], "BLOCKED");
    let (mut ob, mut tb) = (base(), base());
    ob["other"] = json!({"k": {"sha256": "a", "reviewed": "2026-11-27"}});
    tb["other"] = json!({"k": {"sha256": "b", "reviewed": "2026-11-27"}});
    let got = merge_records(
        &base().to_string(),
        &ob.to_string(),
        &tb.to_string(),
        Some(&plan(FILLED)),
    )
    .unwrap();
    assert_eq!(got["other"]["k"]["sha256"], "b");
}

#[test]
fn the_driver_given_the_plan_merges_by_it() {
    let dir = crate::checks::scratch("plan-merge-held");
    let (b, o, t) = (dir.join("O"), dir.join("A"), dir.join("B"));
    let (bv, ov, tv) = tonight();
    std::fs::write(&b, bv.to_string()).unwrap();
    std::fs::write(&o, ov.to_string()).unwrap();
    std::fs::write(&t, tv.to_string()).unwrap();
    assert_eq!(merge_files(&b, &o, &t, Some(&plan(FILLED))).code, 0);
    let v: Value = serde_json::from_str(&std::fs::read_to_string(&o).unwrap()).unwrap();
    assert_eq!(v["blocks"][KEY]["verdict"], "CLEAR");
}

/// A map the record keeps no digest for decides nothing by the plan (451 T495's `Held::at`).
#[test]
fn a_map_with_no_digest_is_held_by_no_plan() {
    assert!(super::Held::of("").at("passes", "x").is_none());
}

/// 462 T545: a pre-split tree's record carried onto a split clone (and the reverse) brings back no entry the split moved to the archive's
/// parts, its side unchanged from the base - only its own new verdict.
#[test]
fn a_pre_split_side_resurrects_no_archived_entry() {
    let pre = base();
    let mut split = base();
    split["tasks"] = json!({});
    split["block_reviews"] = json!([]);
    let theirs = adding("T300");
    for m in [merged(&pre, &split, &theirs), merged(&pre, &theirs, &split)] {
        assert!(m["tasks"].get("T01").is_none() && m["tasks"].get("T300").is_some());
        assert_eq!(m["block_reviews"], json!([row("### T300 x")]));
    }
}
