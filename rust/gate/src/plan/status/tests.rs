//! What a feature owes, block by block.

use std::collections::BTreeSet;

use serde_json::{json, Value};

use super::super::history::History;
use super::super::record::record;
use super::super::sections::{block_digest, digest, task_sections};
use super::super::tests::{current, feature, git, narrow_bad, narrow_ok, within, PLAN, PLAN_TASKS};
use super::{block_status, judge, owed, section_clear, task_current, REMOVED};
use crate::checks::scratch;

fn none() -> BTreeSet<String> {
    BTreeSet::new()
}

fn owed_of(review: &Value, plan: &str, done: &str) -> Vec<String> {
    block_status(review, plan, &none(), None, done).0
}

#[test]
fn each_reason_a_feature_owes_a_review() {
    assert_eq!(owed(&feature(None, None)).unwrap().0, "plan-missing");
    assert_eq!(
        owed(&feature(Some(PLAN), None)).unwrap().0,
        "plan-review-missing"
    );
    let dir = feature(Some(PLAN), None);
    std::fs::write(dir.join("plan-review.json"), "{not json").unwrap();
    assert_eq!(owed(&dir).unwrap().0, "plan-review-missing");
    assert_eq!(
        owed(&feature(
            Some(PLAN),
            Some(&current(&[], "CLEAR", "an older plan"))
        ))
        .unwrap()
        .0,
        "plan-review-stale"
    );
    let blocked = owed(&feature(
        Some(PLAN),
        Some(&current(&[narrow_bad()], "BLOCKED", PLAN)),
    ))
    .unwrap();
    assert!(blocked.0 == "plan-review-blocked" && blocked.1.contains("P1"));
    assert_eq!(
        owed(&feature(
            Some(PLAN),
            Some(&current(&[within(), narrow_ok()], "CLEAR", PLAN))
        )),
        None
    );
    let review = json!({"plan_sha256": "x", "plan_text": "", "decisions": [], "verdict": "CLEAR"});
    assert_eq!(
        judge(Some(b"anything"), Some(&review.to_string()), None, "")
            .unwrap()
            .0,
        "plan-review-stale"
    );
}

#[test]
fn a_whole_plan_blocked_with_no_ruling_named_and_more_than_five_owed() {
    let plan = "# p\n";
    let bare = json!({"plan_sha256": digest(plan.as_bytes()), "verdict": "BLOCKED"});
    assert!(
        judge(Some(plan.as_bytes()), Some(&bare.to_string()), None, "")
            .unwrap()
            .1
            .contains("no ruling named")
    );
    let many = "## a\n## b\n## c\n## d\n## e\n## f\n## g\n";
    let got = judge(Some(many.as_bytes()), Some("{}"), None, "").unwrap();
    assert!(got.1.contains("and 2 more"));
}

const PLAN_375: &str = "# plan\n\n**D1 - the gatehouse.** Each sheet draws its gatehoue at 12 ft, and every tub stands by a door.\n**D2 - the bath.** The bath is 10 x 8 ft.\n";

#[test]
fn a_verdict_survives_a_typo_and_nothing_more() {
    for (old, new, keeps) in [
        ("gatehoue", "gatehouse", true),
        ("12 ft, and", "12 ft,\n and", true),
        ("stands by a door.", "stands by a door;", true),
        ("12 ft", "14 ft", false),
        ("every tub", "each tub", false),
        ("stands by", "never stands by", false),
        (
            "10 x 8 ft.\n",
            "10 x 8 ft.\n**D3 - a new decision.** A well by the kitchen.\n",
            false,
        ),
        ("the gatehouse.", "the gateway.", false),
    ] {
        let dir = feature(Some(PLAN_375), None);
        let root = dir.parent().unwrap().parent().unwrap().to_owned();
        git(&root, &["init", "-q", "-b", "main"]);
        record(
            &dir,
            &current(&[within()], "CLEAR", PLAN_375),
            "spec-fidelity",
            None,
        )
        .unwrap();
        git(&root, &["add", "-A"]);
        git(&root, &["commit", "-qm", "the reviewed plan"]);
        assert!(!std::fs::read_to_string(dir.join("plan-review.json"))
            .unwrap()
            .contains("plan_text"));
        assert_eq!(owed(&dir), None);
        std::fs::write(dir.join("plan.md"), PLAN_375.replace(old, new)).unwrap();
        assert_eq!(owed(&dir).is_none(), keeps, "{old:?} -> {new:?}");
    }
}

#[test]
fn an_archived_block_a_typo_from_its_reviewed_text_is_not_owed() {
    let body =
        "### T49 Decisions\n\n**D70 - the mark falls back.** When the mark names a ticked task.\n";
    let review = json!({"blocks": {"preamble": {"sha256": block_digest("# Plan\n"), "verdict": "CLEAR"}, "### T49 Decisions": {"sha256": block_digest(body), "verdict": "CLEAR", "text": body}}});
    let typo = body.replace("When the mark", "when the mark");
    let changed = body.replace("falls back", "is refused");
    assert_eq!(
        block_status(&review, "# Plan\n", &none(), None, &typo),
        (vec![], vec![])
    );
    assert_eq!(
        owed_of(&review, "# Plan\n", &changed),
        ["(removed) ### T49 Decisions"]
    );
    assert_eq!(
        owed_of(&review, "# Plan\n", ""),
        ["(removed) ### T49 Decisions"]
    );
    let moved_whole = owed_of(&review, "# Plan\n", body);
    assert_eq!(moved_whole, Vec::<String>::new(), "archived byte for byte");
}

#[test]
fn ids_appended_to_the_lands_open_line_owe_no_review_and_a_reorder_does() {
    let body = "## Landing\n\n**Lands open**: T02, T03\n\nEach task lands when it closes.\n";
    let review = json!({"blocks": {"preamble": {"sha256": block_digest("# Plan\n\n"), "verdict": "CLEAR"}, "## Landing": {"sha256": block_digest(body), "verdict": "CLEAR", "text": body}}});
    let appended = body.replace("T02, T03", "T02, T03, T09");
    assert_eq!(
        owed_of(&review, &format!("# Plan\n\n{appended}"), ""),
        Vec::<String>::new()
    );
    for changed in [
        body.replace("T02, T03", "T03, T02"),
        body.replace("T02, T03", "T02, T09"),
        appended.replace("lands when it closes", "lands at once"),
    ] {
        assert_eq!(
            owed_of(&review, &format!("# Plan\n\n{changed}"), ""),
            ["## Landing"]
        );
    }
}

fn part_b(four: &str, five: &str, extra: &str) -> String {
    format!("### T05 part B (2026-10-19T00:30Z)\n\n1. **What is refusing?** Nothing.\n4. **Moving something earlier?** {four}\n5. **Tuning or changing?** {five}\n{extra}")
}

#[test]
fn a_part_b_that_decides_nothing_owes_no_review_and_one_that_decides_does() {
    let plan = "# Plan\n\n**D10 - a rule.** x\n\n";
    let review =
        json!({"blocks": {"preamble": {"sha256": block_digest(plan), "verdict": "CLEAR"}}});
    assert_eq!(
        owed_of(
            &review,
            &format!(
                "{plan}{}",
                part_b(
                    "No.",
                    "Neither - landing what was checked.",
                    "6. **Test.** D10 holds.\n"
                )
            ),
            ""
        ),
        Vec::<String>::new()
    );
    for loud in [
        part_b("No.", "Changing: the rule widens.", ""),
        part_b("Yes - the wells move.", "Neither.", ""),
        part_b("No.", "Neither.", "7. **Next.** D11 - a new rule.\n"),
    ] {
        assert_eq!(
            owed_of(&review, &format!("{plan}{loud}"), ""),
            ["### T05 part B (2026-10-19T00:30Z)"]
        );
    }
}

fn task_review(sec: &str, task: &str) -> Value {
    json!({"tasks": {task: {"verdict": "CLEAR", "section_sha256": digest(sec.as_bytes()), "section_text": sec}}})
}

#[test]
fn a_quiet_part_b_leaves_its_task_s_section_reviewed() {
    let sec = "## T05 - x\n\n### T05 Approach (checklist part A)\n\n1. **G.** y\n\n### T05 Decisions\n\n**D10 - a rule.** z\n\n";
    let plan = format!("# Plan\n\n{sec}");
    let review = task_review(sec, "T05");
    for (block, expect) in [("### T05 part B (2026-10-19T01:30Z)\n\n4. **Moving?** No.\n5. **Tuning or changing?** Neither.\n\n", true), ("### T05 part B (2026-10-19T01:30Z)\n\n4. **Moving?** No.\n5. **Tuning or changing?** Changing: wider.\n\n", false)] {
        let text = plan.replace("### T05 Decisions", &format!("{block}### T05 Decisions"));
        assert_eq!(task_current(&review, &text, "T05", None), expect);
    }
}

#[test]
fn a_pointer_repointed_to_a_recorded_split_leaves_the_section_reviewed() {
    let sec = "## T31 - x\n\n### T31 Decisions\n\n**D113 - a rule.** Row 841 is its own task, T32 (FR-015).\n\n";
    let review = task_review(sec, "T31");
    let split =
        "## T95 - the leg (found working T31, 2026-10-19; ranking row 841)\n\n**D117 - y.** z\n\n";
    let other = "## T95 - the leg (ranking row 841)\n\n**D117 - y.** z\n\n";
    let moved = sec.replace("T32", "T95");
    assert!(task_current(
        &review,
        &format!("# Plan\n\n{moved}{split}"),
        "T31",
        None
    ));
    assert!(!task_current(
        &review,
        &format!("# Plan\n\n{moved}{other}"),
        "T31",
        None
    ));
    assert!(!task_current(
        &review,
        &format!("# Plan\n\n{}{split}", sec.replace("T32", "T96")),
        "T31",
        None
    ));
    assert!(!task_current(
        &review,
        &format!(
            "# Plan\n\n{}{split}",
            moved.replace("its own task", "a later task")
        ),
        "T31",
        None
    ));
}

#[test]
fn a_repoint_to_a_split_already_archived_leaves_the_section_reviewed() {
    let dir = scratch("archived-split");
    let sec = "## T31 - x\n\nRow 841 is T32.\n\n";
    let review = task_review(sec, "T31");
    let text = format!("# Plan\n\n{}", sec.replace("T32", "T95"));
    std::fs::write(dir.join("plan.md"), &text).unwrap();
    std::fs::write(
        dir.join("plan-done.md"),
        "## T95 - the leg (found working T31)\n\nz\n",
    )
    .unwrap();
    let history = History::new(&dir.join("plan.md"), "HEAD");
    assert!(task_current(&review, &text, "T31", Some(&history)));
    std::fs::write(dir.join("plan-done.md"), "## T95 - the leg\n\nz\n").unwrap();
    assert!(!task_current(&review, &text, "T31", Some(&history)));
}

#[test]
fn an_archive_line_inside_a_task_s_section_leaves_it_reviewed() {
    let sec = "## T05 - x\n\n### T05 Decisions\n\n**D10 - a rule.** z\n\n";
    let review = task_review(sec, "T05");
    let line = "<!-- plan-archive: T06 to T07 moved to plan-done.md, 2026-10-19 (feature 375 FR-044) -->\n";
    assert!(task_current(
        &review,
        &format!("# Plan\n\n{sec}{line}"),
        "T05",
        None
    ));
    assert!(!task_current(
        &review,
        &format!("# Plan\n\n{sec}A new decision.\n"),
        "T05",
        None
    ));
}

#[test]
fn a_blocked_or_absent_task_verdict_is_not_current() {
    assert!(!task_current(
        &json!({"tasks": {"T05": {"verdict": "BLOCKED"}}}),
        PLAN_TASKS,
        "T05",
        None
    ));
    assert!(!task_current(&json!({}), PLAN_TASKS, "T99", None));
    assert!(!task_current(
        &json!({"tasks": {"T05": {"verdict": "CLEAR", "section_sha256": "x"}}}),
        PLAN_TASKS,
        "T05",
        None
    ));
    let sec = &task_sections(PLAN_TASKS)["T05"];
    assert!(task_current(
        &json!({"tasks": {"T05": {"verdict": "CLEAR", "section_sha256": digest(sec.as_bytes())}}}),
        PLAN_TASKS,
        "T05",
        None
    ));
}

#[test]
fn a_wording_only_section_owes_no_review_but_a_decision_or_a_deciding_part_b_does() {
    let sec = "## T05 - x\n\n### T05 Approach (checklist part A)\n\n1. **G.** y\n\n### T05 Decisions\n\n**Wording only.** a claim relabeled.\n\n";
    let plan = format!("# Plan\n\n{sec}");
    let review =
        json!({"blocks": {"preamble": {"sha256": block_digest("# Plan\n\n"), "verdict": "CLEAR"}}});
    assert_eq!(owed_of(&review, &plan, ""), Vec::<String>::new());
    let decided = plan.replace(
        "a claim relabeled.\n",
        "a claim relabeled.\n\n**D10 - a rule.** z\n",
    );
    assert_ne!(owed_of(&review, &decided, ""), Vec::<String>::new());
    let loud = "### T05 part B (2026-10-19T01:30Z)\n\n4. **Moving?** No.\n5. **Tuning or changing?** Changing: wider.\n\n";
    assert_eq!(
        owed_of(&review, &format!("{plan}{loud}"), ""),
        ["### T05 part B (2026-10-19T01:30Z)"]
    );
}

#[test]
fn the_decide_guard_reads_a_block_as_plan_delta_does() {
    let reviewed = "### T77 Decisions\n\n**D55 - carries filed.** As written.\n";
    let review = json!({"blocks": {"### T77 Decisions": {"verdict": "CLEAR", "sha256": block_digest(reviewed), "text": reviewed}}});
    assert!(section_clear(&review, reviewed, None));
    assert!(section_clear(&review, &format!("{reviewed}\n"), None));
    assert!(!section_clear(
        &review,
        &reviewed.replace(
            "As written.",
            "A different decision entirely, three new words."
        ),
        None
    ));
    assert!(!section_clear(&json!({}), reviewed, None));
    let keyless = json!({"blocks": {"### T77 Decisions": {"verdict": "CLEAR", "sha256": "other"}}});
    assert!(!section_clear(&keyless, reviewed, None));
}

#[test]
fn a_re_dated_heading_with_its_text_unchanged_is_the_same_block() {
    let old = "### T9 Approach (checklist part A)\n\n1. **The goal.** the bath\n";
    let review = json!({"blocks": {"### T9 Approach (checklist part A)": {"sha256": block_digest(old), "verdict": "CLEAR", "text": old}}});
    let moved = "# Plan\n\n### T9 Approach (2026-10-31T04:00Z)\n\n1. **The goal.** the bath\n";
    assert_eq!(
        owed_of(&review, moved, "")
            .iter()
            .filter(|k| k.contains("T9"))
            .count(),
        0
    );
    let changed = moved.replace("the bath", "the wells");
    let got = owed_of(&review, &changed, "");
    assert!(
        got.contains(&format!("{REMOVED}### T9 Approach (checklist part A)"))
            && got
                .iter()
                .any(|k| k == "### T9 Approach (2026-10-31T04:00Z)")
    );
    let other = moved.replace("### T9 Approach", "### T9 Decisions");
    assert!(owed_of(&review, &other, "")
        .contains(&format!("{REMOVED}### T9 Approach (checklist part A)")));
}

#[test]
fn a_re_dated_heading_archived_at_the_tick_is_the_same_block() {
    let old = "### T9 Approach (checklist part A)\n\n1. **The goal.** the bath\n";
    let review = json!({"blocks": {"### T9 Approach (checklist part A)": {"sha256": block_digest(old), "verdict": "CLEAR", "text": old}}});
    let done = "<!-- plan-archive: archived 2026-10-31 -->\n### T9 Approach (2026-10-31T04:00Z)\n\n1. **The goal.** the bath\n";
    let key = format!("{REMOVED}### T9 Approach (checklist part A)");
    assert!(!owed_of(&review, "# Plan\n", done).contains(&key));
    assert!(owed_of(&review, "# Plan\n", &done.replace("bath", "wells")).contains(&key));
}

#[test]
fn a_record_from_before_block_verdicts_is_read_block_by_block() {
    let plan = "# p\n\n## A\n\nx\n";
    let review = json!({"plan_text": plan, "verdict": "CLEAR"});
    assert_eq!(
        block_status(&review, plan, &none(), None, ""),
        (vec![], vec![])
    );
    let unjudged = json!({"blocks": {"## A": {"sha256": block_digest("## A\n\nx\n"), "verdict": "maybe"}, "preamble": {"sha256": block_digest("# p\n\n"), "verdict": "CLEAR"}, "stray": "not an object"}});
    assert_eq!(owed_of(&unjudged, plan, ""), ["## A"]);
    let blocked = json!({"blocks": {"## A": {"sha256": block_digest("## A\n\nx\n"), "verdict": "BLOCKED"}, "preamble": {"sha256": block_digest("# p\n\n"), "verdict": "CLEAR"}}});
    assert_eq!(block_status(&blocked, plan, &none(), None, "").1, ["## A"]);
}

#[test]
fn a_ticked_task_s_block_may_be_repointed_too() {
    let was = "## T31 - x\n\nRow 841 is T32.\n";
    let now = "## T31 - x\n\nRow 841 is T95.\n";
    let review = json!({"blocks": {"## T31 - x": {"sha256": block_digest(was), "verdict": "CLEAR", "text": was}}});
    let done = "## T95 - the leg (found working T31)\n\nz\n";
    assert_eq!(owed_of(&review, now, done), Vec::<String>::new());
    assert_eq!(owed_of(&review, now, ""), ["## T31 - x"]);
}

#[test]
fn the_truth_of_a_recorded_digest() {
    assert_eq!(super::sha_of(&json!({"sha256": 5})), Some("5".to_owned()));
    assert_eq!(super::sha_of(&json!({"sha256": ""})), None);
    assert_eq!(super::sha_of(&json!({"sha256": []})), None);
    assert_eq!(super::sha_of(&json!({"sha256": false})), None);
    assert_eq!(super::sha_of(&json!({"sha256": 0})), None);
}

const BLOCKS: &str = "# Plan\n\n**D1 - shared.** Every gate is checked once.\n\n## Batch 1\n\n### Wave 1 (T01)\n\n**D2 - the sty.** The sty stands by the house (FR-001).\n\n## Batch 2\n\n### Wave 2 (T02)\n\n**D3 - the well.** The well stands by the lane (FR-002).\n\n## Notes\n\nA note on the waves, 3 items.\n";

fn reviewed() -> std::path::PathBuf {
    let dir = feature(Some(BLOCKS), None);
    let root = dir.parent().unwrap().parent().unwrap().to_owned();
    git(&root, &["init", "-q", "-b", "main"]);
    record(
        &dir,
        &current(&[within()], "CLEAR", BLOCKS),
        "spec-fidelity",
        None,
    )
    .unwrap();
    git(&root, &["add", "-A"]);
    git(&root, &["commit", "-qm", "the plan, reviewed"]);
    dir
}

fn read_review(dir: &std::path::Path) -> Value {
    serde_json::from_str(&std::fs::read_to_string(dir.join("plan-review.json")).unwrap()).unwrap()
}

#[test]
fn an_edit_to_one_block_owes_that_block_alone() {
    let dir = reviewed();
    let edited = BLOCKS.replace(
        "A note on the waves, 3 items.",
        "A note on the waves, 4 items, and a new rule.",
    );
    std::fs::write(dir.join("plan.md"), &edited).unwrap();
    let (rule, reason) = owed(&dir).unwrap();
    assert!(
        rule == "plan-review-stale" && reason.contains("## Notes") && !reason.contains("Batch 1")
    );
    assert_eq!(owed_of(&read_review(&dir), &edited, ""), ["## Notes"]);
}

#[test]
fn a_record_from_before_the_amendment_covers_the_blocks_it_reviewed() {
    let dir = reviewed();
    let old = json!({"plan_sha256": digest(BLOCKS.as_bytes()), "plan_text": BLOCKS, "verdict": "CLEAR", "decisions": [within()]});
    std::fs::write(dir.join("plan-review.json"), old.to_string()).unwrap();
    std::fs::write(
        dir.join("plan.md"),
        BLOCKS.replace("by the lane", "by the pond"),
    )
    .unwrap();
    assert!(owed(&dir).unwrap().1.contains("Wave 2 (T02)"));
    let slim = super::super::record::slim_record(&old);
    assert!(
        slim.get("plan_text").is_none()
            && slim["blocks"]
                .as_object()
                .unwrap()
                .values()
                .all(|e| e["verdict"] == "CLEAR")
    );
    std::fs::write(dir.join("plan-review.json"), slim.to_string()).unwrap();
    assert!(owed(&dir).unwrap().1.contains("Wave 2 (T02)"));
    std::fs::write(
        dir.join("plan.md"),
        BLOCKS.replace("checked once", "cheked once"),
    )
    .unwrap();
    assert_eq!(owed(&dir), None);
}

#[test]
fn a_block_deleted_by_hand_is_owed_and_its_removal_reviewed() {
    let dir = reviewed();
    std::fs::write(
        dir.join("plan.md"),
        BLOCKS.replace(&task_sections(BLOCKS)["T02"], ""),
    )
    .unwrap();
    let (rule, reason) = owed(&dir).unwrap();
    assert!(rule == "plan-review-stale" && reason.contains("(removed) ### Wave 2 (T02)"));
    super::super::record::record_blocks(
        &dir,
        &json!({"blocks": {"(removed) ### Wave 2 (T02)": "removed"}, "decisions": [within()]}),
        "spec-fidelity",
        None,
    )
    .unwrap();
    assert_eq!(owed(&dir), None);
}

#[test]
fn a_typo_since_an_accept_is_forgiven_before_the_accepted_text_is_committed() {
    let dir = feature(
        Some("# plan\n\n## T17 - x\n\n### T17 Decisions\n\n**D1** the rule of teh ways.\n"),
        None,
    );
    let root = dir.parent().unwrap().parent().unwrap().to_owned();
    git(&root, &["init", "-q", "-b", "main"]);
    let trigger = "round:spec-fidelity|plan:243-x#T17@3";
    std::fs::write(
        dir.join("arbiter.jsonl"),
        format!("{}\n", json!({"trigger": trigger, "ruling": "accept"})),
    )
    .unwrap();
    super::super::record::arbiter_accept(&dir, trigger, None).unwrap();
    let plan_path = dir.join("plan.md");
    let fixed = "# plan\n\n## T17 - x\n\n### T17 Decisions\n\n**D1** the rule of the ways.\n";
    std::fs::write(&plan_path, fixed).unwrap();
    let review = read_review(&dir);
    let history = History::new(&plan_path, "HEAD");
    assert!(section_clear(
        &review,
        &task_sections(fixed)["T17"],
        Some(&history)
    ));
    let changed = fixed.replace("the rule of the ways", "never the rule of the ways");
    assert!(!section_clear(
        &review,
        &task_sections(&changed)["T17"],
        Some(&history)
    ));
}
