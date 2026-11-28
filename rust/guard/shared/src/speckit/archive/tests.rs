//! The archive's cut, its index and its readers over scratch feature directories (451 T537). `GUARD_EDIT_OK`: 451 T537 the new archive
//! module's own tests.

use std::path::Path;

use super::*;
use crate::plan_text::task_sections;
use crate::tempdir::TempDir;

/// A plan section of about `bytes` bytes under `heading`.
fn section(heading: &str, bytes: usize) -> String {
    format!("{heading}\n\n{}\n\n", "word ".repeat(bytes / 5))
}

/// A flat plan-done.md: its title, an archive marker, tasks out of id order (a part's name its lowest and highest id), a bundle heading, an Approach heading apart from its
/// task's, a heading with no id, and two sections large enough that the cut makes several parts.
fn flat_plan() -> String {
    let mut t = String::from("# 999-scratch - the plan's finished sections\n\n<!-- plan-archive: archived 2026-11-20 -->\n");
    t += &section("### T10 (the tenth)", 200);
    t += &section("### T2 (the second)", 40_000);
    t += "<!-- plan-archive: archived 2026-11-21 -->\n";
    t += &section("### T3, T4 (bundle)", 300);
    t += &section("### Notes kept with T3's bundle", 100);
    t += &section("### T10 Approach (checklist part A)", 300);
    t += &section("### T7 (the seventh)", 40_000);
    t += &section("### T4 Approach (checklist part A)", 200);
    t
}

fn tasks_done() -> String {
    "# 999-scratch - the ticked tasks\n\n- [x] T2 the second\n      verify: DONE. two\n- [x] T3 the third\n      research: rendering\n- [x] T7 the seventh\n- [x] T10 the tenth\n".to_owned()
}

fn scratch(tag: &str) -> (TempDir, std::path::PathBuf) {
    let t = TempDir::new(&format!("archive-{tag}"));
    let d = t.join("999-scratch");
    std::fs::create_dir_all(&d).unwrap();
    std::fs::write(d.join(PLAN_DONE), flat_plan()).unwrap();
    std::fs::write(d.join(TASKS_DONE), tasks_done()).unwrap();
    (t, d)
}

/// Every task's own sections, as `make plan-section` finds them, from the whole text.
fn own(text: &str) -> Vec<(String, String)> {
    task_sections(text)
        .into_iter()
        .filter(|(t, s)| {
            let title = s
                .lines()
                .next()
                .unwrap_or("")
                .trim_start_matches('#')
                .trim();
            leading_tasks(title).contains(&t.as_str())
        })
        .collect()
}

#[test]
fn a_split_moves_every_task_whole_and_a_reader_of_one_task_opens_only_its_part() {
    let (_t, d) = scratch("split");
    let before = own(&flat_plan());
    let written = fold(&d, true).unwrap();
    assert!(!d.join(PLAN_DONE).exists() && !d.join(TASKS_DONE).exists());
    // T2 and T7 (40 KB each) cannot share a part under the 64 KiB bound: two plan parts, one tasks part
    assert_eq!(written.len(), 3, "{written:?}");
    assert!(written[0].starts_with("archive/plan-done/001-T2-"));
    let read = files(&d);
    for (task, text) in &before {
        let opened = task_text(&read, PLAN_DONE, task);
        assert_eq!(task_sections(&opened).get(task), Some(text), "{task}");
        // a task opens its parts alone: T4, in its bundle's part and in the part its own Approach stands in, opens two
        let parts = index(&read)["tasks"][PLAN_DONE][task]
            .as_array()
            .unwrap()
            .len();
        assert!(opened.len() <= parts * (BOUND + 200), "{task}");
    }
    // the heading with no id stays with the piece before it, the first marker with the first piece
    assert!(task_text(&read, PLAN_DONE, "T3").contains("### Notes kept with T3's bundle"));
    assert!(text(&read, PLAN_DONE).contains("archived 2026-11-20"));
    let flat = tasks_done();
    let mut lines: Vec<&str> = flat.lines().skip(2).collect();
    let all = text(&read, TASKS_DONE);
    let mut got: Vec<&str> = all
        .lines()
        .filter(|l| !l.starts_with("# ") && !l.is_empty())
        .collect();
    lines.sort_unstable();
    got.sort_unstable();
    assert_eq!(lines, got);
    assert_eq!(
        task_text(&read, TASKS_DONE, "T7")
            .lines()
            .filter(|l| l.starts_with("- ["))
            .count(),
        4
    );
    assert_eq!(ids(&read, TASKS_DONE), ["T2", "T3", "T7", "T10"]);
    assert!(ids(&read, PLAN_DONE).contains(&"T4".to_owned()));
    let paths = paths(&read);
    assert_eq!(paths.len(), 5);
    let note = std::fs::read_to_string(d.join(NOTE)).unwrap();
    assert!(note
        .lines()
        .nth(2)
        .unwrap()
        .starts_with("Load this file when:"));
    assert!(
        note.contains("make plan-section F=999 T=T<n>")
            && note.contains("| plan-done.md | `plan-done/001-T2-")
            && note.contains("Read the feature's plan-review.json whole, or its parts here")
            && note.contains("WHY: these records grew to megabytes")
    );
    assert!(plan_done_is(&d, &before));
}

#[test]
fn a_piece_whose_lead_continues_the_run_before_it_joins_that_run() {
    // a bundle heading followed by its member's part B (as 451 T352's were): one run, so one part though together over the bound
    let mut t = section("### T3, T4 (bundle)", 40_000);
    t += &section("### T4 Approach (checklist part B)", 40_000);
    t += &section("### T5 (the fifth)", 100);
    let parts = cut(PLAN_DONE, &t);
    assert_eq!(parts.len(), 2);
    assert_eq!(parts[0].2, ["T3", "T4", "T4"]);
    assert_eq!((parts[0].0.as_str(), parts[0].1.as_str()), ("T3", "T4"));
    assert!(parts[0].3.find("### T3, T4") < parts[0].3.find("### T4 Approach"));
    assert_eq!(parts[1].2, ["T5"]);
}

fn plan_done_is(d: &Path, before: &[(String, String)]) -> bool {
    own(&plan_done(d)) == before
}

#[test]
fn a_tail_written_after_the_split_is_folded_into_new_parts_and_read_with_them() {
    let (_t, d) = scratch("tail");
    fold(&d, true).unwrap();
    std::fs::write(
        d.join(PLAN_DONE),
        "# 999-scratch - the plan's finished sections\n\n### T11 (late)\n\nlate\n",
    )
    .unwrap();
    let read = files(&d);
    // before the fold the tail is read beside the parts, by the whole reader and the by-task reader alike
    assert!(text(&read, PLAN_DONE).ends_with("late\n"));
    assert!(task_text(&read, PLAN_DONE, "T11").contains("### T11 (late)"));
    // a tick's fold: archive/ stands, so no force is needed
    let written = fold(&d, false).unwrap();
    assert_eq!(written, ["archive/plan-done/003-T11-T11.md"]);
    assert!(!d.join(PLAN_DONE).exists());
    assert_eq!(
        task_text(&read, PLAN_DONE, "T11")
            .matches("### T11")
            .count(),
        1
    );
}

#[test]
fn a_flat_feature_is_left_flat_unasked_and_a_task_over_the_bound_stands_alone() {
    let (_t, d) = scratch("small");
    assert!(fold(&d, false).unwrap().is_empty());
    assert!(d.join(PLAN_DONE).is_file() && !d.join(DIR).exists());
    // the flat layout reads as before: no index, the file whole
    let read = files(&d);
    assert_eq!(text(&read, PLAN_DONE), flat_plan());
    assert_eq!(task_text(&read, PLAN_DONE, "T2"), flat_plan());
    assert!(ids(&read, PLAN_DONE).is_empty() && paths(&read).is_empty());
    // a flat record of any size waits for `make archive-split`
    std::fs::write(d.join(PLAN_DONE), section("### T1 (big)", 2 * BOUND)).unwrap();
    assert!(fold(&d, false).unwrap().is_empty());
    let written = fold(&d, true).unwrap();
    // one task larger than the bound stands in a part alone
    assert_eq!(written[0], "archive/plan-done/001-T1-T1.md");
}

#[test]
fn a_part_with_no_header_line_is_read_whole() {
    // a part edited by hand, its header gone: no line of it is dropped as one
    let (_t, d) = scratch("headless");
    fold(&d, true).unwrap();
    let part = d.join(DIR).join("tasks-done/001-T2-T10.md");
    std::fs::write(&part, "- [x] T2 the second\n\n- [x] T3 the third\n").unwrap();
    assert_eq!(
        text(&files(&d), TASKS_DONE),
        "- [x] T2 the second\n\n- [x] T3 the third\n"
    );
}

#[test]
fn a_part_that_cannot_be_written_is_named_and_the_flat_file_kept() {
    let (_t, d) = scratch("unwritable");
    std::fs::create_dir_all(d.join(DIR)).unwrap();
    std::fs::write(
        d.join(DIR).join("plan-done"),
        "a file where the directory goes",
    )
    .unwrap();
    let why = fold(&d, false).unwrap_err();
    assert!(why.contains("archive/plan-done"), "{why}");
    assert!(d.join(PLAN_DONE).is_file());
}

/// 462 T545: a closed task's review entries added as JSON parts are read back for that task beside the flat (live) record, the flat
/// entry over a part's; the index, the note and the paths name them; a part that does not parse is passed over.
#[test]
fn a_review_part_is_read_for_its_task_beside_the_live_record() {
    let (_t, d) = scratch("review");
    fold(&d, true).unwrap();
    let part = json!({"part": "999 - plan-review.json", "blocks": {"### T2 x": {"verdict": "CLEAR"}}, "tasks": {"T2": {"verdict": "CLEAR"}, "T3": {"verdict": "OLD"}}, "block_reviews": [{"blocks": ["### T2 x"], "tasks": ["T2"]}]});
    let cut = vec![(
        "T2".to_owned(),
        "T3".to_owned(),
        vec!["T2".to_owned(), "T3".to_owned()],
        part.to_string(),
    )];
    assert_eq!(
        add_review(&d, cut).unwrap(),
        ["archive/plan-review/001-T2-T3.json"]
    );
    std::fs::write(d.join(REVIEW), json!({"feature": "999-scratch", "blocks": {}, "tasks": {"T3": {"verdict": "CLEAR"}}, "block_reviews": [{"blocks": ["## Summary"]}]}).to_string()).unwrap();
    let read = files(&d);
    let r = review(&read, "T3");
    assert_eq!(r["tasks"]["T3"]["verdict"], "CLEAR");
    assert_eq!(r["tasks"]["T2"]["verdict"], "CLEAR");
    assert_eq!(r["feature"], "999-scratch");
    assert!(r.get("part").is_none());
    assert_eq!(r["block_reviews"].as_array().unwrap().len(), 2);
    // a task no part holds reads the flat record alone
    assert!(review(&read, "T9")["tasks"].get("T2").is_none());
    assert!(paths(&read).contains(&"archive/plan-review/001-T2-T3.json".to_owned()));
    let note = std::fs::read_to_string(d.join(NOTE)).unwrap();
    assert!(note.contains("| plan-review.json | `plan-review/001-T2-T3.json` |"));
    std::fs::write(d.join(DIR).join("plan-review/001-T2-T3.json"), "not json").unwrap();
    std::fs::write(d.join(REVIEW), "[]").unwrap();
    assert_eq!(
        review(&read, "T3"),
        json!({"blocks": {}, "tasks": {}, "block_reviews": []})
    );
    // a part that cannot be written is named
    std::fs::remove_dir_all(d.join(DIR).join("plan-review")).unwrap();
    std::fs::write(d.join(DIR).join("plan-review"), "in the way").unwrap();
    assert!(add_review(&d, Vec::new())
        .unwrap_err()
        .contains("archive/plan-review"));
}
