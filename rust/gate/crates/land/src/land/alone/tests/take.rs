//! The clone's take of the landed tip (451 T105): it gave up three times on 2026-11-21, each needing a hand merge - the review ledger's
//! rows written on both sides, plan.md and tasks.md after the same landing, and at T113's landing an archived section beside the
//! clone's new ones. Each shape is taken now; only a piece both sides changed otherwise still gives up, named.

use std::path::Path;

use l7r_gate_core::ci::fixtures::put;

use super::super::super::tests::has;
use super::{alone, sh, world};

/// The line the tick leaves where T1's section was (`plan/sections.rs`'s archive mark).
const MARK: &str =
    "<!-- plan-archive: T1 to T1 moved to plan-done.md, 2026-11-21 (feature 375 FR-044) -->\n";

/// The ledger's table head: ten cells, as `settle::COLUMNS` reads a measured row.
const HEAD: &str = "| date | check | subject | verdict | reply | found | fix | applied | wall | tokens |\n|---|---|---|---|---|---|---|---|---|---|\n";

/// A measured ledger row of the pass `check` with the wall time `wall`, its `applied or filed as` cell `at`.
fn row(check: &str, wall: &str, at: &str) -> String {
    format!("| 2026-11-21 | {check} | MODE 4: PLAN REVIEW | CLEAR | words | nothing | - | applied or filed as {at} records | {wall} | 1k in (0k cached) / 1k out |\n")
}

/// The stub landing's `STUB_MID`: each `(rel, text)` written over the worktree's file, then staged, for the stub's commit.
fn landing_writes(dir: &Path, files: &[(&str, &str)]) -> String {
    let mut steps = Vec::new();
    for (k, (rel, text)) in files.iter().enumerate() {
        put(dir, &format!("tip/{k}"), text);
        steps.push(format!("cp {}/tip/{k} {rel}", dir.display()));
    }
    steps.push("git add -A".to_owned());
    steps.join(" && ")
}

/// `text`'s lines but its blank ones.
fn unblank(text: &str) -> Vec<&str> {
    text.lines().filter(|l| !l.trim().is_empty()).collect()
}

/// Shapes 1 and 2, the T82-T101 landing: the session's `make ledger-owed` and the landing wrote rows for the same passes (their
/// `applied or filed as` cells differ), and the tick archived T1's section and line between the clone's edits of the next ones. The
/// tip's rows answer the passes, the clone's other row kept; the clone's text kept, T1's dropped, the tick's mark in its place; and in
/// a file no merge knows, the clone's lines that hold the landing's same added line.
#[test]
fn the_clone_takes_a_landing_that_wrote_its_rows_and_archived_beside_its_edits() {
    let (dir, c) = world("alone-take");
    let plan = "### T0 the section before\n\nT0's words.\n\n### T1 the landing's\n\nT1's words.\n\n### T2 the section after\n\nT2's words.\n";
    let old = row("old-check", "1 s", "x");
    put(&c, "specs/451-x/plan.md", plan);
    put(
        &c,
        "specs/451-x/tasks.md",
        "- [ ] T0 zero\n- [ ] T1 one\n- [ ] T2 two\n",
    );
    put(&c, "dev/review-ledger.md", &format!("{HEAD}{old}"));
    put(&c, "docs/notes.md", "a\n");
    sh(
        &c,
        "git add -A && git commit -qm 'the records' && git push -q origin HEAD:main 2>/dev/null",
    );
    // the clone, uncommitted: the session's rows for the two passes and one more, T0's and T2's edits beside T1, a new T3
    let session = |wall: &str| row("spec-fidelity", wall, "451 T1 (CLEAR by its builder)");
    let other = row("quote-check", "9 s", "451 T2");
    let ledger = format!("{HEAD}{old}{}{}{other}", session("56 s"), session("41 s"));
    put(&c, "dev/review-ledger.md", &ledger);
    let plan = "### T0 the section before\n\nT0's words.\n\nT0's builder's new line.\n\n### T1 the landing's\n\nT1's words.\n\n### T2 the section after, reworded\n\nT2's words.\n\n### T3 a new task\n\nT3's words.\n";
    put(&c, "specs/451-x/plan.md", plan);
    let tasks = "- [ ] T0 zero, reworded\n- [ ] T1 one\n- [ ] T2 two, reworded\n- [ ] T3 three\n";
    put(&c, "specs/451-x/tasks.md", tasks);
    put(&c, "docs/notes.md", "a\nb\nc\n");
    // the landing: its rows for the same passes, T1's section archived to the mark and its line moved out, the same line added
    let landed = |wall: &str| {
        row(
            "spec-fidelity",
            wall,
            "the plan-verdict record (make plan-verdict)",
        )
    };
    let tip_ledger = format!("{HEAD}{old}{}{}", landed("56 s"), landed("41 s"));
    let tip_plan = format!("### T0 the section before\n\nT0's words.\n\n{MARK}### T2 the section after\n\nT2's words.\n");
    let mid = landing_writes(
        &dir,
        &[
            ("dev/review-ledger.md", &tip_ledger),
            ("specs/451-x/plan.md", &tip_plan),
            ("specs/451-x/tasks.md", "- [ ] T0 zero\n- [ ] T2 two\n"),
            ("docs/notes.md", "a\nb\n"),
        ],
    );
    let (rc, said) = alone(&dir, &c, &[("STUB_MID", &mid)]);
    assert_eq!(rc, 0, "{said}");
    has(&said, "4 of them merged with the clone's uncommitted edits");
    let tip = sh(&dir, "git -C origin.git rev-parse main");
    assert_eq!(sh(&c, "git rev-parse HEAD"), tip);
    let read = |rel: &str| std::fs::read_to_string(c.join(rel)).unwrap();
    let want = format!("{tip_ledger}{other}");
    assert_eq!(read("dev/review-ledger.md"), want);
    let want = format!("### T0 the section before\n\nT0's words.\n\nT0's builder's new line.\n\n{MARK}### T2 the section after, reworded\n\nT2's words.\n\n### T3 a new task\n\nT3's words.\n");
    assert_eq!(read("specs/451-x/plan.md"), want);
    let want = "- [ ] T0 zero, reworded\n- [ ] T2 two, reworded\n- [ ] T3 three\n";
    assert_eq!(read("specs/451-x/tasks.md"), want);
    assert_eq!(read("docs/notes.md"), "a\nb\nc\n");
}

/// Shape 3, T113's landing (its sides as they were, `fixtures/t113-take/`, each piece cut to its first lines): the tick archived T113's
/// section and line, its marks left at the end of T112's text, which the clone had rewritten, with T114's new section after. Taken as
/// the hand resolution was: the clone's text, T113's section and line dropped, the tick's marks kept - but for one blank line the hand
/// resolution put after the marks, where the tick puts none.
#[test]
fn t113_s_landing_is_taken_beside_the_clone_s_new_sections() {
    let (dir, c) = world("alone-t113");
    let side = |name: &str, which: &str| match (name, which) {
        ("plan.md", "base") => include_str!("../fixtures/t113-take/plan.md.base"),
        ("plan.md", "ours") => include_str!("../fixtures/t113-take/plan.md.ours"),
        ("plan.md", "theirs") => include_str!("../fixtures/t113-take/plan.md.theirs"),
        ("plan.md", _) => include_str!("../fixtures/t113-take/plan.md.resolved"),
        (_, "base") => include_str!("../fixtures/t113-take/tasks.md.base"),
        (_, "ours") => include_str!("../fixtures/t113-take/tasks.md.ours"),
        (_, "theirs") => include_str!("../fixtures/t113-take/tasks.md.theirs"),
        _ => include_str!("../fixtures/t113-take/tasks.md.resolved"),
    };
    for name in ["plan.md", "tasks.md"] {
        put(&c, &format!("specs/451-x/{name}"), side(name, "base"));
    }
    sh(
        &c,
        "git add -A && git commit -qm 'the records' && git push -q origin HEAD:main 2>/dev/null",
    );
    for name in ["plan.md", "tasks.md"] {
        put(&c, &format!("specs/451-x/{name}"), side(name, "ours"));
    }
    let mid = landing_writes(
        &dir,
        &[
            ("specs/451-x/plan.md", side("plan.md", "theirs")),
            ("specs/451-x/tasks.md", side("tasks.md", "theirs")),
        ],
    );
    let (rc, said) = alone(&dir, &c, &[("STUB_MID", &mid)]);
    assert_eq!(rc, 0, "{said}");
    let read = |rel: &str| std::fs::read_to_string(c.join(rel)).unwrap();
    let plan = read("specs/451-x/plan.md");
    assert_eq!(unblank(&plan), unblank(side("plan.md", "resolved")));
    assert!(!plan.contains("### T113"), "{plan}");
    let marks = plan.matches("<!-- plan-archive: T113 to T1").count();
    assert_eq!(marks, 2, "{plan}");
    assert_eq!(read("specs/451-x/tasks.md"), side("tasks.md", "resolved"));
}

/// A real conflict - the same section changed otherwise on both sides, and a line two ways in a file no merge knows - still gives up,
/// every conflict named at once, the section by its task, and nothing moved.
#[test]
fn a_section_both_sides_changed_otherwise_still_gives_up_naming_it() {
    let (dir, c) = world("alone-take-conflict");
    let plan = "### T1 the landing's\n\nT1's words.\n\n### T2 the section after\n\nT2's words.\n";
    put(&c, "specs/451-x/plan.md", plan);
    put(&c, "docs/notes.md", "a\n");
    sh(
        &c,
        "git add -A && git commit -qm 'the records' && git push -q origin HEAD:main 2>/dev/null",
    );
    let before = sh(&c, "git rev-parse HEAD");
    let ours = "### T1 the landing's\n\nT1's words.\n\n### T2 the section after\n\nT2's words, the clone's.\n";
    put(&c, "specs/451-x/plan.md", ours);
    put(&c, "docs/notes.md", "a\nthe clone's\n");
    let tip_plan = format!("{MARK}### T2 the section after\n\nT2's words, the landing's.\n");
    let mid = landing_writes(
        &dir,
        &[
            ("specs/451-x/plan.md", &tip_plan),
            ("docs/notes.md", "a\nthe landing's\n"),
        ],
    );
    let (rc, said) = alone(&dir, &c, &[("STUB_MID", &mid)]);
    assert_eq!(rc, 4, "{said}");
    has(&said, "docs/notes.md - the landing's change and the clone's uncommitted edit conflict: a hunk both changed otherwise; specs/451-x/plan.md - the landing's change and the clone's uncommitted edit conflict: T2's section, changed otherwise on both sides");
    assert_eq!(sh(&c, "git rev-parse HEAD"), before);
    let read = |rel: &str| std::fs::read_to_string(c.join(rel)).unwrap();
    assert_eq!(read("specs/451-x/plan.md"), ours);
    assert_eq!(read("docs/notes.md"), "a\nthe clone's\n");
}
