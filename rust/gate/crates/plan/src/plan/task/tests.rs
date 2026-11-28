//! The active task, a check's wait, the archive and the push.

use std::path::Path;

use serde_json::json;

use super::super::record::{record, record_task};
use super::super::sections::{digest, task_sections};
use super::super::tests::{current, feature_at, git, repo, within, PLAN, PLAN_TASKS, TASKS};
use super::{
    active_task, archive, decision_refusal, owed, owed_for, push_owed, resolve, touched_features,
    RECORD,
};
use crate::checks::scratch;

fn activate(root: &Path) {
    std::fs::create_dir_all(root.join(".specify")).unwrap();
    std::fs::write(
        root.join(".specify/feature.json"),
        "{\"feature_directory\": \"specs/375-x\"}",
    )
    .unwrap();
}

#[test]
fn a_check_waits_for_its_task_s_decisions() {
    let root = repo();
    let dir = feature_at(&root, Some(PLAN_TASKS), None, "375-x");
    std::fs::write(
        dir.join("tasks.md"),
        "- [x] T04 done\n- [ ] T05 the bath\n- [ ] T07 docs\n",
    )
    .unwrap();
    assert_eq!(decision_refusal(&root), "");
    assert_eq!(active_task(&root), (None, String::new()));
    activate(&root);
    assert_eq!(active_task(&root), (Some(dir.clone()), "T05".to_owned()));
    assert!(decision_refusal(&root)
        .contains("T05: its plan section carries no current CLEAR decision verdict"));
    record(
        &dir,
        &current(&[within()], "CLEAR", PLAN_TASKS),
        "spec-fidelity",
        None,
    )
    .unwrap();
    assert_eq!(decision_refusal(&root), "");
    std::fs::write(
        dir.join("plan.md"),
        PLAN_TASKS.replace("10 x 8 ft", "12 x 9 ft"),
    )
    .unwrap();
    assert!(decision_refusal(&root).contains("T05: its plan section"));
    std::fs::write(dir.join("plan.md"), PLAN_TASKS).unwrap();
    std::fs::remove_file(dir.join("plan-review.json")).unwrap();
    let sha = digest(task_sections(PLAN_TASKS)["T05"].as_bytes());
    record_task(
        &dir,
        "T05",
        &json!({"section_sha256": sha, "decisions": []}),
        "spec-fidelity",
        None,
    )
    .unwrap();
    assert_eq!(decision_refusal(&root), "");
    std::fs::write(
        root.join(".git/active-task"),
        json!({"feature": "375-x", "task": "T07"}).to_string(),
    )
    .unwrap();
    assert_eq!(active_task(&root), (Some(dir.clone()), "T07".to_owned()));
    assert!(decision_refusal(&root).contains("no section for this task"));
    record(
        &dir,
        &current(&[within()], "CLEAR", PLAN_TASKS),
        "spec-fidelity",
        None,
    )
    .unwrap();
    assert_eq!(decision_refusal(&root), "");
    std::fs::write(root.join(".specify/feature.json"), "not json").unwrap();
    assert_eq!(active_task(&root), (None, String::new()));
}

#[test]
fn a_mark_naming_a_ticked_task_falls_back_to_the_first_open_task() {
    let root = repo();
    let dir = feature_at(&root, Some(PLAN_TASKS), None, "375-x");
    std::fs::write(
        dir.join("tasks.md"),
        "- [x] T04 done\n- [ ] T05 the bath\n- [ ] T07 docs\n",
    )
    .unwrap();
    activate(&root);
    for (mark, want) in [("T07", "T07"), ("T04", "T05"), ("T99", "T05")] {
        std::fs::write(
            root.join(".git/active-task"),
            json!({"feature": "375-x", "task": mark}).to_string(),
        )
        .unwrap();
        assert_eq!(active_task(&root).1, want);
    }
}

#[test]
fn a_wording_only_task_waits_for_nothing() {
    let root = repo();
    let dir = feature_at(
        &root,
        Some("## T01 x\n\n### T01 Decisions\n\n**Wording only.** a comment.\n"),
        None,
        "375-x",
    );
    std::fs::write(dir.join("tasks.md"), "- [ ] T01 x\n").unwrap();
    activate(&root);
    assert_eq!(decision_refusal(&root), "");
}

#[test]
fn the_push_judges_every_touched_feature_with_a_tick_at_head() {
    let root = repo();
    std::fs::write(root.join("README"), "x").unwrap();
    git(&root, &["add", "-A"]);
    git(&root, &["commit", "-qm", "base"]);
    let base = git(&root, &["rev-parse", "HEAD"]);
    let ticked = TASKS.replace("- [ ] T01", "- [x] T01");
    let no_review = feature_at(&root, Some(PLAN), None, "001-a");
    std::fs::write(no_review.join("tasks.md"), &ticked).unwrap();
    feature_at(&root, Some(PLAN), None, "002-b");
    let cleared = feature_at(
        &root,
        Some(PLAN),
        Some(&current(&[within()], "CLEAR", PLAN)),
        "003-c",
    );
    std::fs::write(cleared.join("tasks.md"), &ticked).unwrap();
    std::fs::create_dir_all(root.join("specs/006-z")).unwrap();
    std::fs::write(root.join("specs/006-z/note.md"), "x").unwrap();
    let no_plan = feature_at(&root, None, None, "004-d");
    std::fs::write(
        no_plan.join("tasks.md"),
        TASKS.replace("- [ ] T02", "- [X] T02"),
    )
    .unwrap();
    git(&root, &["add", "-A"]);
    git(&root, &["commit", "-qm", "work"]);
    let range = format!("{base}..HEAD");
    assert_eq!(
        touched_features(&root, &range),
        [
            "specs/001-a",
            "specs/002-b",
            "specs/003-c",
            "specs/004-d",
            "specs/006-z"
        ]
    );
    let found: Vec<(String, &str)> = push_owed(&root, &range, "HEAD")
        .into_iter()
        .map(|(f, r, _)| (f, r))
        .collect();
    assert_eq!(
        found,
        [
            ("specs/001-a".to_owned(), "plan-review-missing"),
            ("specs/004-d".to_owned(), "plan-missing")
        ]
    );
    std::fs::write(
        no_review.join("plan-review.json"),
        current(&[], "CLEAR", PLAN).to_string(),
    )
    .unwrap();
    assert!(push_owed(&root, &range, "HEAD")
        .iter()
        .any(|(f, ..)| f == "specs/001-a"));
    git(&root, &["-c", "core.fileMode=false", "status", "-s"]);
    std::fs::create_dir_all(root.join("specs/005-e")).unwrap();
    assert_eq!(touched_features(&root, "HEAD"), Vec::<String>::new());
}

#[test]
fn a_feature_resolves_from_a_path_a_number_or_a_name() {
    let root = scratch("resolve");
    let dir = feature_at(&root, Some(PLAN), None, "243-x");
    assert_eq!(resolve("243", &root), Some(dir.clone()));
    assert_eq!(resolve("243-x", &root), Some(dir.clone()));
    assert_eq!(resolve(&dir.display().to_string(), &root), Some(dir));
    assert_eq!(resolve("999", &root), None);
    assert_eq!(resolve("a/b", &root), None);
    feature_at(&root, Some(PLAN), None, "243-y");
    assert_eq!(resolve("243", &root), None, "two of them");
}

fn ticked_feature(plan: &str, tasks: &str) -> l7r_shared::tempdir::Held<std::path::PathBuf> {
    let root = repo();
    let dir = feature_at(&root, Some(plan), None, "375-x");
    std::fs::write(dir.join("tasks.md"), tasks).unwrap();
    record(&dir, &current(&[], "CLEAR", plan), "spec-fidelity", None).unwrap();
    root.hold(dir)
}

#[test]
fn the_archive_moves_ticked_cleared_sections_byte_for_byte() {
    let dir = ticked_feature(PLAN_TASKS, "- [x] T05 the bath\n- [ ] T06 the wells\n");
    assert_eq!(archive(&dir, Some("2026-01-01"), false), ["T05"]);
    let plan = std::fs::read_to_string(dir.join("plan.md")).unwrap();
    assert!(plan.contains("<!-- plan-archive: T05 to T05 moved to plan-done.md, 2026-01-01 (feature 375 FR-044) -->\n## T06"));
    let done = std::fs::read_to_string(dir.join("plan-done.md")).unwrap();
    assert!(
        done.starts_with("# 375-x - the plan's finished sections")
            && done.contains("<!-- plan-archive: archived 2026-01-01 -->\n## T05 the bath")
    );
    assert_eq!(archive(&dir, None, false), Vec::<String>::new());
}

#[test]
fn a_run_of_sections_leaves_one_line_and_a_second_archive_appends() {
    let plan = "# p\n\n## T01 a\n\nx\n\n## T02 b\n\ny\n\n## T03 c\n\nz\n";
    let dir = ticked_feature(plan, "- [x] T01 a\n- [x] T02 b\n- [ ] T03 c\n");
    assert_eq!(archive(&dir, Some("2026-01-01"), false), ["T01", "T02"]);
    assert!(std::fs::read_to_string(dir.join("plan.md"))
        .unwrap()
        .contains("T01 to T02 moved"));
    std::fs::write(
        dir.join("tasks.md"),
        "- [x] T01 a\n- [x] T02 b\n- [x] T03 c\n",
    )
    .unwrap();
    assert_eq!(archive(&dir, Some("2026-01-02"), false), ["T03"]);
    let done = std::fs::read_to_string(dir.join("plan-done.md")).unwrap();
    assert_eq!(done.matches("the plan's finished sections").count(), 1);
    assert!(done.contains("archived 2026-01-02"));
}

#[test]
fn a_section_joined_from_two_places_is_moved_piece_by_piece() {
    let plan = "# p\n\n### T01 Approach\n\nfirst\n\n<!-- between -->\n\n## Other\n\nkept\n\n### T01 Decisions\n\nsecond\n";
    let dir = ticked_feature(plan, "- [x] T01 a\n");
    assert_eq!(archive(&dir, Some("2026-01-01"), false), ["T01"]);
    let text = std::fs::read_to_string(dir.join("plan.md")).unwrap();
    assert!(text.contains("## Other") && !text.contains("first") && !text.contains("second"));
    assert_eq!(text.matches("plan-archive:").count(), 2);
}

#[test]
fn nothing_ticked_or_nothing_clear_stays() {
    let open = ticked_feature(PLAN_TASKS, "- [ ] T05 x\n- [ ] T06 y\n");
    assert_eq!(archive(&open, None, false), Vec::<String>::new());
    let root = repo();
    let dir = feature_at(&root, Some(PLAN_TASKS), None, "375-x");
    std::fs::write(dir.join("tasks.md"), "- [x] T05 x\n").unwrap();
    assert_eq!(archive(&dir, None, false), Vec::<String>::new());
}

#[test]
fn a_section_with_its_own_verdict_is_archivable() {
    let root = repo();
    let dir = feature_at(&root, Some(PLAN_TASKS), None, "375-x");
    std::fs::write(dir.join("tasks.md"), "- [x] T05 x\n").unwrap();
    let sha = digest(task_sections(PLAN_TASKS)["T05"].as_bytes());
    record_task(
        &dir,
        "T05",
        &json!({"section_sha256": sha, "decisions": []}),
        "spec-fidelity",
        None,
    )
    .unwrap();
    assert_eq!(archive(&dir, None, false), ["T05"]);
}

#[test]
fn a_ticked_task_is_a_column_zero_line_in_either_case() {
    assert!(super::has_ticked("- [x] T01 a\n") && super::has_ticked("- [X] T02 b\n"));
    assert!(!super::has_ticked(
        "- [ ] T03 c\n  - [x] research pass - [x] source-reader confirmed\n"
    ));
}

const BLOCKS: &str = "# Plan\n\n**D1 - shared.** Every gate is checked once.\n\n## Batch 1\n\n### Wave 1 (T01)\n\n**D2 - the sty.** The sty stands by the house (FR-001).\n\n## Batch 2\n\n### Wave 2 (T02)\n\n**D3 - the well.** The well stands by the lane (FR-002).\n\n## Notes\n\nA note on the waves, 3 items.\n";

fn reviewed(tasks: &str, plan: &str) -> l7r_shared::tempdir::Held<std::path::PathBuf> {
    let root = repo();
    let dir = feature_at(&root, Some(plan), None, "999-x");
    std::fs::write(dir.join("tasks.md"), tasks).unwrap();
    record(
        &dir,
        &current(&[within()], "CLEAR", plan),
        "spec-fidelity",
        None,
    )
    .unwrap();
    git(&root, &["add", "-A"]);
    git(&root, &["commit", "-qm", "the plan, reviewed"]);
    root.hold(dir)
}

#[test]
fn the_archive_moves_only_finished_clear_sections_and_owes_nothing() {
    let dir = reviewed("- [x] T01 the sty\n- [ ] T02 the well\n", BLOCKS);
    let sec = task_sections(BLOCKS)["T01"].clone();
    assert_eq!(archive(&dir, Some("2026-10-13"), false), ["T01"]);
    let plan = std::fs::read_to_string(dir.join("plan.md")).unwrap();
    assert!(
        !plan.contains(&sec)
            && plan.contains("<!-- plan-archive: T01 to T01 moved to plan-done.md, 2026-10-13")
    );
    assert!(std::fs::read_to_string(dir.join("plan-done.md"))
        .unwrap()
        .contains(&sec));
    assert_eq!(owed(&dir), None);
    std::fs::write(
        dir.join("tasks.md"),
        "- [x] T01 the sty\n- [x] T02 the well\n",
    )
    .unwrap();
    assert_eq!(archive(&dir, None, false), ["T02"]);
    assert!(!std::fs::read_to_string(dir.join("plan.md"))
        .unwrap()
        .contains("Wave 2"));
    assert_eq!(owed(&dir), None);
}

#[test]
fn a_finished_section_a_typo_from_its_reviewed_text_is_archived() {
    let dir = reviewed("- [x] T01 the sty\n- [ ] T02 the well\n", BLOCKS);
    let sec = task_sections(BLOCKS)["T01"].clone();
    std::fs::write(
        dir.join("plan.md"),
        BLOCKS.replace(&sec, &format!("{}\n\n\n", sec.trim_end_matches('\n'))),
    )
    .unwrap();
    git(
        dir.parent().unwrap().parent().unwrap(),
        &["commit", "-qam", "a blank line"],
    );
    assert_eq!(archive(&dir, Some("2026-10-21"), false), ["T01"]);
}

#[test]
fn a_task_whose_blocks_stand_in_two_places_is_archived_whole() {
    let split = format!(
        "{BLOCKS}\n### T01 Decisions\n\n**D4 - the sty's door.** It faces south (FR-001).\n"
    );
    let dir = reviewed("- [x] T01 the sty\n- [ ] T02 the well\n", &split);
    assert_eq!(archive(&dir, Some("2026-10-31"), false), ["T01", "T01"]);
    let plan = std::fs::read_to_string(dir.join("plan.md")).unwrap();
    assert!(
        !plan.to_lowercase().contains("the sty stands")
            && !plan.contains("the sty's door")
            && plan.contains("Wave 2 (T02)")
    );
    assert_eq!(archive(&dir, None, false), Vec::<String>::new());
}

#[test]
fn a_range_heading_and_its_tasks_own_blocks_are_archived_once_each() {
    let ranged = "# Plan\n\n### T01-T02 - the yard\n\n**D1 - shared.** The yard is fenced (FR-001).\n\n### T02 Approach\n\n1. The well by the lane (FR-002).\n\n### T01 Approach\n\n1. The sty by the house (FR-001).\n\n## Notes\n\nA note.\n";
    let dir = reviewed("- [x] T01 the sty\n- [x] T02 the well\n", ranged);
    archive(&dir, Some("2026-11-08"), false);
    let done = std::fs::read_to_string(dir.join("plan-done.md")).unwrap();
    let plan = std::fs::read_to_string(dir.join("plan.md")).unwrap();
    for heading in [
        "### T01-T02 - the yard",
        "### T02 Approach",
        "### T01 Approach",
    ] {
        assert_eq!(done.matches(heading).count(), 1, "{heading}");
        assert!(!plan.contains(heading));
    }
    assert!(!done.contains("moved to plan-done.md") && plan.contains("## Notes"));
    assert_eq!(archive(&dir, None, false), Vec::<String>::new());
}

#[test]
fn a_task_archived_in_tasks_done_is_ticked_for_the_archive_and_the_push() {
    // feature 449 T142: the ticked task moved to tasks-done.md, its section moves when its review is CLEAR...
    let dir = ticked_feature(PLAN_TASKS, "- [ ] T06 the wells\n");
    std::fs::write(dir.join("tasks-done.md"), "# h\n\n- [x] T05 the bath\n").unwrap();
    assert_eq!(archive(&dir, Some("2026-01-01"), false), ["T05"]);
    // ...and a feature whose ticked tasks all moved still owes the push its plan review
    let root = repo();
    std::fs::write(root.join("README"), "x").unwrap();
    git(&root, &["add", "-A"]);
    git(&root, &["commit", "-qm", "base"]);
    let base = git(&root, &["rev-parse", "HEAD"]);
    let moved = feature_at(&root, Some(PLAN), None, "001-a");
    std::fs::write(moved.join("tasks.md"), "# Tasks\n\n- [ ] T02 build it\n").unwrap();
    std::fs::write(moved.join("tasks-done.md"), "- [x] T01 x\n").unwrap();
    git(&root, &["add", "-A"]);
    git(&root, &["commit", "-qm", "work"]);
    let found: Vec<&str> = push_owed(&root, &format!("{base}..HEAD"), "HEAD")
        .into_iter()
        .map(|(_, r, _)| r)
        .collect();
    assert_eq!(found, ["plan-review-missing"]);
}

#[test]
fn a_bundle_block_stays_while_any_task_it_lists_is_open() {
    // 449's batch landing (2026-11-22): ticking T197 archived its section, joined with the shared `### T158, T197, ... part B`
    // block every listed task owned (451 T141), so the 35 still open lost the part B their red-gate trigger owed and every tick refused
    let plan = "# p\n\n### T01 Approach\n\nfirst\n\n### T02 Approach\n\nsecond\n\n### T01, T02 part B (2026-01-01T00:00Z)\n\n1. shared\n";
    let dir = ticked_feature(plan, "- [x] T01 a\n- [ ] T02 b\n");
    assert_eq!(archive(&dir, Some("2026-01-01"), false), ["T01"]);
    let text = std::fs::read_to_string(dir.join("plan.md")).unwrap();
    let kept = text.contains("### T01, T02 part B") && text.contains("1. shared");
    assert!(!text.contains("first") && kept);
    std::fs::write(dir.join("tasks.md"), "- [x] T01 a\n- [x] T02 b\n").unwrap();
    assert_eq!(archive(&dir, Some("2026-01-02"), false), ["T02"]);
    let text = std::fs::read_to_string(dir.join("plan.md")).unwrap();
    assert!(!text.contains("part B") && !text.contains("second"));
}

#[test]
fn a_heading_that_names_a_ticked_task_leaves_none_of_its_own_section_behind() {
    // 451 T487 (2026-11-27, 11:29Z and 11:36Z): T475's heading named 451 T451, ticked and with no section of its own, so T451's
    // "section" was T475's heading block alone; it was taken first, T475's whole section starting at the same byte was skipped as
    // inside it, and the archive left `### T475 Approach` in plan.md - judged alone, by a block verdict a carry had made stale, it
    // refused every later tick of the landing while `make plan-delta` (T475's section current) owed nothing
    let plan = "# p\n\n### T02 (filed from T01's finding)\n\nwhy\n\n### T02 Approach (checklist part A)\n\n1. The well by the lane (FR-002).\n\n## T03 open\n\nlater\n";
    let root = repo();
    let dir = feature_at(&root, Some(plan), None, "375-x");
    std::fs::write(
        dir.join("tasks.md"),
        "- [x] T01 a\n- [x] T02 b\n- [ ] T03 c\n",
    )
    .unwrap();
    record(&dir, &current(&[], "CLEAR", plan), "spec-fidelity", None).unwrap();
    let sha = digest(task_sections(plan)["T02"].as_bytes());
    record_task(
        &dir,
        "T02",
        &json!({"section_sha256": sha, "decisions": []}),
        "spec-fidelity",
        None,
    )
    .unwrap();
    // the block's own entry made stale, as T310's carry made T475's: a same-day verdict on the unfilled stub's text won the merge
    let path = dir.join(RECORD);
    let mut review: serde_json::Value =
        serde_json::from_str(&std::fs::read_to_string(&path).unwrap()).unwrap();
    review["blocks"]["### T02 Approach (checklist part A)"]["sha256"] =
        json!(digest(b"the stub's text"));
    std::fs::write(&path, review.to_string()).unwrap();
    archive(&dir, Some("2026-11-27"), false);
    let text = std::fs::read_to_string(dir.join("plan.md")).unwrap();
    assert!(
        !text.contains("T02 Approach") && !text.contains("why\n") && text.contains("## T03 open")
    );
    assert_eq!(owed_for(&dir, &["T03"]), None);
}
