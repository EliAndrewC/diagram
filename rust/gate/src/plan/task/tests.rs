//! The active task, a check's wait, the archive and the push.

use std::path::Path;

use serde_json::json;

use super::super::record::{record, record_task};
use super::super::sections::{digest, task_sections};
use super::super::tests::{current, feature_at, git, repo, within, PLAN, PLAN_TASKS, TASKS};
use super::{active_task, archive, decision_refusal, push_owed, resolve, touched_features};
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

fn ticked_feature(plan: &str, tasks: &str) -> std::path::PathBuf {
    let root = repo();
    let dir = feature_at(&root, Some(plan), None, "375-x");
    std::fs::write(dir.join("tasks.md"), tasks).unwrap();
    record(&dir, &current(&[], "CLEAR", plan), "spec-fidelity", None).unwrap();
    dir
}

#[test]
fn the_archive_moves_ticked_cleared_sections_byte_for_byte() {
    let dir = ticked_feature(PLAN_TASKS, "- [x] T05 the bath\n- [ ] T06 the wells\n");
    assert_eq!(archive(&dir, Some("2026-01-01")), ["T05"]);
    let plan = std::fs::read_to_string(dir.join("plan.md")).unwrap();
    assert!(plan.contains("<!-- plan-archive: T05 to T05 moved to plan-done.md, 2026-01-01 (feature 375 FR-044) -->\n## T06"));
    let done = std::fs::read_to_string(dir.join("plan-done.md")).unwrap();
    assert!(
        done.starts_with("# 375-x - the plan's finished sections")
            && done.contains("<!-- plan-archive: archived 2026-01-01 -->\n## T05 the bath")
    );
    assert_eq!(archive(&dir, None), Vec::<String>::new());
}

#[test]
fn a_run_of_sections_leaves_one_line_and_a_second_archive_appends() {
    let plan = "# p\n\n## T01 a\n\nx\n\n## T02 b\n\ny\n\n## T03 c\n\nz\n";
    let dir = ticked_feature(plan, "- [x] T01 a\n- [x] T02 b\n- [ ] T03 c\n");
    assert_eq!(archive(&dir, Some("2026-01-01")), ["T01", "T02"]);
    assert!(std::fs::read_to_string(dir.join("plan.md"))
        .unwrap()
        .contains("T01 to T02 moved"));
    std::fs::write(
        dir.join("tasks.md"),
        "- [x] T01 a\n- [x] T02 b\n- [x] T03 c\n",
    )
    .unwrap();
    assert_eq!(archive(&dir, Some("2026-01-02")), ["T03"]);
    let done = std::fs::read_to_string(dir.join("plan-done.md")).unwrap();
    assert_eq!(done.matches("the plan's finished sections").count(), 1);
    assert!(done.contains("archived 2026-01-02"));
}

#[test]
fn a_section_joined_from_two_places_is_moved_piece_by_piece() {
    let plan = "# p\n\n### T01 Approach\n\nfirst\n\n<!-- between -->\n\n## Other\n\nkept\n\n### T01 Decisions\n\nsecond\n";
    let dir = ticked_feature(plan, "- [x] T01 a\n");
    assert_eq!(archive(&dir, Some("2026-01-01")), ["T01"]);
    let text = std::fs::read_to_string(dir.join("plan.md")).unwrap();
    assert!(text.contains("## Other") && !text.contains("first") && !text.contains("second"));
    assert_eq!(text.matches("plan-archive:").count(), 2);
}

#[test]
fn nothing_ticked_or_nothing_clear_stays() {
    let open = ticked_feature(PLAN_TASKS, "- [ ] T05 x\n- [ ] T06 y\n");
    assert_eq!(archive(&open, None), Vec::<String>::new());
    let root = repo();
    let dir = feature_at(&root, Some(PLAN_TASKS), None, "375-x");
    std::fs::write(dir.join("tasks.md"), "- [x] T05 x\n").unwrap();
    assert_eq!(archive(&dir, None), Vec::<String>::new());
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
    assert_eq!(archive(&dir, None), ["T05"]);
}
