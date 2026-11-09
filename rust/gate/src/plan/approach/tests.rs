//! A task's Approach answered before its tick, and again after a trigger.

use std::path::{Path, PathBuf};

use serde_json::json;

use super::super::tests::{git, repo};
use super::{
    best, future_refusal, future_stamps, in_flight, owe, owed_entries, parse_utc, part_items,
    refusal, ruled, unanswered,
};

const CHECKLIST: &str = "# Checklist\n\n## A. At task start\n\n1. **The goal.** x\n2. **The constraints.** y\n3. **Where from.** z\n\n## B. When the work resists\n\n1. **What refuses.** a\n2. **Again.** b\n\n## C. Habits\n\n1. **Edit once.** c\n";
const PLAN: &str = "# Plan\n\n## T01 - the first\n\n### T01 Approach (checklist part A)\n\n1. **The goal.** a lane.\n2. **The constraints.** the law.\n3. **Where from.** R.\n\n### T01 Decisions\n\n**D1 - the lane.** It is laid after the houses.\n\n## T02 - the second\n\n### T02 Approach (checklist part A)\n\n1. **The goal.** a well.\n3. **Where from.** O.\n\n### T02 Decisions\n\n**D2 - the well.** By the lane.\n";
const TASKS: &str =
    "- [ ] T01 the first\n      research: rendering\n- [ ] T02 the second\n- [ ] T03 the third\n";

fn feature() -> (PathBuf, PathBuf) {
    let root = repo();
    let dir = root.join("specs/999-x");
    std::fs::create_dir_all(&dir).unwrap();
    std::fs::create_dir_all(root.join("docs")).unwrap();
    std::fs::write(root.join("docs/approach-checklist.md"), CHECKLIST).unwrap();
    std::fs::write(dir.join("plan.md"), PLAN).unwrap();
    std::fs::write(dir.join("tasks.md"), TASKS).unwrap();
    std::fs::create_dir_all(root.join(".specify")).unwrap();
    std::fs::write(
        root.join(".specify/feature.json"),
        json!({"feature_directory": "specs/999-x"}).to_string(),
    )
    .unwrap();
    (root, dir)
}

fn why(dir: &Path, root: &Path, task: &str) -> String {
    refusal(dir, root, task).unwrap_or_default()
}

#[test]
fn the_checklist_s_items_are_read_by_part() {
    assert_eq!(part_items(CHECKLIST, "A"), [1, 2, 3]);
    assert_eq!(part_items(CHECKLIST, "B"), [1, 2]);
    assert_eq!(part_items(CHECKLIST, "D"), Vec::<u32>::new());
    assert_eq!(
        parse_utc("### T01 part B (2026-10-17T21:40Z)"),
        parse_utc("2026-10-17T21:40:00Z")
    );
    assert_eq!(parse_utc("2026-01-01T00:00Z"), Some(1_767_225_600));
    assert_eq!(parse_utc("no stamp"), None);
}

#[test]
fn a_task_is_ticked_only_with_every_part_a_item_answered() {
    let (root, dir) = feature();
    assert_eq!(refusal(&dir, &root, "T01"), None);
    assert!(why(&dir, &root, "T02").contains("item(s) 2 unanswered"));
    let missing = why(&dir, &root, "T03");
    assert!(missing.contains("no `### T03 Approach` block") && missing.contains("(1, 2, 3)"));
    std::fs::write(
        dir.join("plan.md"),
        format!("{PLAN}\n**Approach checklist**: `specs/999-x/thin.md`\n"),
    )
    .unwrap();
    assert!(why(&dir, &root, "T03").contains("no `### T03 Approach` block"));
    std::fs::remove_file(root.join("docs/approach-checklist.md")).unwrap();
    assert_eq!(refusal(&dir, &root, "T03"), None);
}

#[test]
fn a_trigger_owes_a_block_stamped_after_it() {
    let (root, dir) = feature();
    let msg = owe(
        &root,
        "999-x",
        "T01",
        "hour:999-x@2",
        "B",
        Some("2026-10-17T21:40:00Z"),
    );
    assert!(
        msg.contains("part B - when the work resists")
            && msg.contains("`### T01 part B (2026-10-17T21:40Z)`")
    );
    owe(
        &root,
        "999-x",
        "T01",
        "hour:999-x@2",
        "B",
        Some("2026-10-17T22:00:00Z"),
    );
    assert_eq!(owed_entries(&root).len(), 1);
    assert!(why(&dir, &root, "T01").contains("no block stamped after it"));
    std::fs::write(
        dir.join("plan.md"),
        format!("{PLAN}\n### T01 part B (2026-10-17T21:00Z)\n\n1. x\n2. y\n"),
    )
    .unwrap();
    assert!(why(&dir, &root, "T01").contains("no block stamped after it"));
    std::fs::write(
        dir.join("plan.md"),
        format!("{PLAN}\n### T01 part B (2026-10-17T21:45Z)\n\n1. the lane law\n"),
    )
    .unwrap();
    assert!(why(&dir, &root, "T01").contains("item(s) 2 unanswered"));
    std::fs::write(
        dir.join("plan.md"),
        format!("{PLAN}\n### T01 part B (2026-10-17T21:45Z)\n\n1. the lane law\n2. R, checked\n"),
    )
    .unwrap();
    assert_eq!(refusal(&dir, &root, "T01"), None);
    assert!(!why(&dir, &root, "T02").contains("D9"));
    assert!(owe(
        &root,
        "999-x",
        "T02",
        "re-decided:x",
        "A",
        Some("2026-10-17T22:00:00Z")
    )
    .contains("Approach (re-answered 2026-10-17T22:00Z)"));
}

#[test]
fn an_hour_or_red_gate_ruling_owes_the_active_task_part_b() {
    let (root, dir) = feature();
    assert_eq!(
        ruled(&root, "ask:something", Some("2026-10-17T21:40:00Z")),
        None
    );
    assert!(ruled(&root, "hour:999-x@3", Some("2026-10-17T21:40:00Z")).is_some());
    assert!(ruled(&root, "red-gate@2", Some("2026-10-17T21:41:00Z")).is_some());
    let tasks: Vec<String> = owed_entries(&root)
        .iter()
        .map(|r| r["task"].as_str().unwrap().to_owned())
        .collect();
    assert_eq!(tasks, ["T01", "T01"]);
    std::fs::write(dir.join("plan.md"), PLAN.replace("T01", "T09")).unwrap();
    assert!(ruled(&root, "hour:999-x@4", None).is_some());
    std::fs::remove_file(root.join("docs/approach-checklist.md")).unwrap();
    assert_eq!(ruled(&root, "hour:999-x@5", None), None);
}

#[test]
fn the_heading_owe_asks_for_passes_at_a_trigger_with_seconds() {
    let (root, dir) = feature();
    let msg = owe(
        &root,
        "999-x",
        "T01",
        "hour:999-x@12",
        "B",
        Some("2026-10-18T10:25:14Z"),
    );
    let head = msg.split('`').nth(1).unwrap().to_owned();
    assert_eq!(head, "### T01 part B (2026-10-18T10:25Z)");
    std::fs::write(
        dir.join("plan.md"),
        format!("{PLAN}\n{head}\n\n1. the lane law\n2. R, checked\n"),
    )
    .unwrap();
    assert_eq!(refusal(&dir, &root, "T01"), None);
    std::fs::write(
        dir.join("plan.md"),
        format!("{PLAN}\n### T01 part B (2026-10-18T10:24Z)\n\n1. the lane law\n2. R, checked\n"),
    )
    .unwrap();
    assert!(why(&dir, &root, "T01").contains("no block stamped after it"));
}

#[test]
fn a_part_b_stamped_after_the_clock_is_refused() {
    let plan = "### T08 part B (2026-10-18T16:40Z)\n\n1. x\n\n### T46 part B (2026-10-18T16:31Z)\n\n1. y\n";
    assert_eq!(
        future_stamps(plan, "2026-10-18T16:31:59Z"),
        ["### T08 part B (2026-10-18T16:40Z)"]
    );
    let told = future_refusal(plan, Some("2026-10-18T16:31:59Z")).unwrap();
    assert!(told.contains("16:31Z") && told.contains("T08 part B (2026-10-18T16:40Z)"));
    assert_eq!(future_refusal(plan, Some("2026-10-18T16:40:00Z")), None);
    assert_eq!(
        future_refusal(
            "### T08 Approach (checklist part A)\n",
            Some("2026-10-18T16:31:00Z")
        ),
        None
    );
    assert_eq!(future_refusal("", None), None);
    let (root, dir) = feature();
    std::fs::write(dir.join("plan.md"), "### T01 part B (2099-01-01T00:00Z)\n").unwrap();
    assert!(why(&dir, &root, "T01").contains("stamped after the clock"));
}

#[test]
fn part_a_holds_the_constant_and_the_arithmetic_items() {
    let text = std::fs::read_to_string(
        Path::new(env!("CARGO_MANIFEST_DIR")).join("../../docs/approach-checklist.md"),
    )
    .unwrap();
    let items = part_items(&text, "A");
    assert_eq!(items, (1..12).collect::<Vec<u32>>());
    assert!(
        text.contains("**Before moving a constant.**")
            && text.contains("**Before fitting things into room.**")
    );
    let old: String = (1..10).map(|n| format!("{n}. **x.** answered\n")).collect();
    assert_eq!(unanswered(&old, &items), [10, 11]);
}

#[test]
fn the_most_complete_block_counts() {
    let plan = "### T01 Approach\n\n1. a\n\n### T01 Approach\n\n1. a\n2. b\n";
    assert_eq!(best(plan, "T01", "A", &[1, 2, 3], None), (true, vec![3]));
    assert_eq!(best(plan, "T09", "A", &[1], None), (false, vec![1]));
}

#[test]
fn a_trigger_charges_every_task_in_flight_not_only_the_last_started() {
    let (root, dir) = feature();
    git(&root, &["add", "-A"]);
    git(
        &root,
        &[
            "commit",
            "-qm",
            "999-x: T00 ticked (make land)",
            "--date=2026-10-17T10:00:00Z",
        ],
    );
    let tick: i64 = git(&root, &["log", "-1", "--format=%ct"]).parse().unwrap();
    let stamp = |s: i64| {
        let (y, mo, d, h, mi, sec) =
            l7r_guard::shared::log::civil(u64::try_from(tick + s).unwrap());
        format!("{y:04}-{mo:02}-{d:02}T{h:02}:{mi:02}:{sec:02}Z")
    };
    let rows: String = [("T03", -60), ("T01", 60), ("T02", 120)]
        .iter()
        .map(|(t, s)| {
            format!(
                "{}\n",
                json!({"feature": "999-x", "task": t, "utc": stamp(*s)})
            )
        })
        .collect();
    std::fs::write(
        root.join(".git/task-starts.jsonl"),
        format!("not json\n{rows}"),
    )
    .unwrap();
    std::fs::write(
        root.join(".git/active-task"),
        json!({"feature": "999-x", "task": "T02"}).to_string(),
    )
    .unwrap();
    assert_eq!(in_flight(&root, &dir, "T02"), ["T02", "T01"]);
    let msg = ruled(&root, "hour:999-x@3", Some("2026-10-17T21:40:00Z")).unwrap();
    assert!(msg.contains("T02 owes") && msg.contains("T01 owes"));
    assert_eq!(owed_entries(&root).len(), 2);
}

#[test]
fn a_part_named_otherwise_is_shown_as_it_is() {
    assert_eq!((super::heads("C"), super::part_title("C")), ("C", "C"));
    let (root, dir) = feature();
    owe(
        &root,
        "999-x",
        "T01",
        "x",
        "A",
        Some("2026-10-17T21:40:00Z"),
    );
    assert!(why(&dir, &root, "T01").contains("part A - at task start"));
}
