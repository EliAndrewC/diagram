//! The deferral's form, each refused form and each passing one (feature 451 T17, D15, the plan section's cases).

use std::path::Path;

use super::{boxes, class_unlabeled, closed, unformed, Boxes};
use crate::checks::scratch;

const TASKS: &str = "# Tasks\n\n- [ ] T123 open one\n- [ ] T124 open two\n- [x] T120 ticked\n- [ ] T22 the close\n- [ ] T32 a\n- [ ] T33 b\n- [ ] T34 c\n";
const DONE: &str = "# Done\n\n- [x] T110 archived\n";

fn fixture() -> (l7r_shared::tempdir::TempDir, Boxes) {
    let dir = scratch("deferral");
    std::fs::write(dir.join("tasks.md"), TASKS).unwrap();
    std::fs::write(dir.join("tasks-done.md"), DONE).unwrap();
    let b = boxes(&dir);
    (dir, b)
}

/// A section whose found-and-left answer is `found`.
fn sec(found: &str) -> String {
    format!("### T17 Approach (checklist part A)\n\n12. **Before any fix.** n/a.\n\n**Found and left?** {found}\n\n**Performance work?** no\n")
}

fn words(found: &[((usize, usize), String)]) -> Vec<String> {
    found.iter().map(|(_, w)| w.clone()).collect()
}

#[test]
fn the_boxes_are_read_from_both_task_files() {
    let (_dir, b) = fixture();
    for id in ["T123", "T124", "T120", "T110"] {
        assert!(b.filed.contains(id), "{id}");
    }
    assert!(b.open.contains("T123") && !b.open.contains("T120") && !b.open.contains("T110"));
    let none = boxes(Path::new("/nonexistent-t17"));
    assert!(none.filed.is_empty());
}

#[test]
fn a_formed_deferral_none_and_a_fixed_item_pass() {
    let (_dir, b) = fixture();
    for found in [
        "none",
        "none - the two readers first found here were fixed in T05.",
        "<none - or each item with its visible effect or the research finding it breaks; an item with neither is not a defect and is not filed>",
        "- The wells stage draws a well in a road. Not fixed here: it is in the wells stage, outside this task's files. Filed as T123; lands before T124.",
        "\n- The wells stage draws a well in a road. Not fixed here because the stage is outside T17's files; filed as `T123`, which lands before T124 and T22.",
        "- A comment in the reader was stale; fixed here.",
        "- T17's own, written before its tick: the `docs/guards.md` row.",
        "Each of (a) to (b) is fixed by the session before T17 lands: (a) the help line; (b) the word list.",
        "`dist()` calls a software `hypot`: not a defect (no output is wrong) and moot under the rebuild.",
        "- The ditch reads as a road: no wrong outcome of this task.",
    ] {
        let s = sec(found);
        assert_eq!(words(&unformed(&s, &b)), Vec::<String>::new(), "{found}");
        assert_eq!(words(&closed(&s, &b)), Vec::<String>::new(), "{found}");
    }
    let template = crate::plan::template::TEMPLATE.replace("{T}", "T17");
    assert!(unformed(&template, &b).is_empty() && class_unlabeled(&template).is_empty());
    assert!(unformed("no found-and-left here\n", &b).is_empty());
}

#[test]
fn a_deferral_missing_its_reason_id_or_order_is_refused_naming_what_it_lacks() {
    let (_dir, b) = fixture();
    for (found, lacks) in [
        (
            "- The wells break. Not fixed here: outside the files. Lands before T124.",
            "no task id",
        ),
        ("- The wells break. Filed as T123; lands before T124.", "no reason"),
        (
            "- The wells break. Not fixed here: outside the files. Filed as T123.",
            "no order",
        ),
        ("- The wells break.", "no reason, no task id, no order"),
        (
            "- `POLL_CHECK_S` goes into D14's knob table with T22, which lands before the close (T22 is the close).",
            "no reason, no task id, no order",
        ),
        (
            "- The wells break. Not fixed here: outside the files. Filed as T999; lands before T124.",
            "T999 is filed in no tasks.md or tasks-done.md",
        ),
        (
            "- The wells break. Not fixed here: outside the files. Filed as T123; lands before T998.",
            "T998 is filed in no tasks.md or tasks-done.md",
        ),
        (
            "- The wells break. Not fixed here: outside the files. Filed as T123; lands before T123.",
            "orders nothing: it lands before its own id T123",
        ),
        (
            "- The wells break. Not fixed here: outside the files, filed as T123 (lands before T124). A comment was stale and is not fixed here either.",
            "",
        ),
    ] {
        let s = sec(found);
        let got = words(&unformed(&s, &b));
        if lacks.is_empty() {
            assert!(got.is_empty(), "{found}: {got:?}");
            continue;
        }
        assert_eq!(got.len(), 1, "{found}: {got:?}");
        assert!(got[0].contains(lacks), "{found}: {got:?}");
        assert!(got[0].contains("The wells") || got[0].contains("POLL_CHECK_S"), "{got:?}");
    }
}

#[test]
fn a_bare_not_fixed_here_is_neither_a_fix_nor_a_reason() {
    let (_dir, b) = fixture();
    let s = sec("- The wells break. Not fixed here. Filed as T123; lands before T124.");
    assert!(words(&unformed(&s, &b))[0].contains("no reason"));
}

#[test]
fn each_item_of_a_list_is_judged_alone_and_placed_by_its_offset() {
    let (_dir, b) = fixture();
    let ok =
        "- The wells break. Not fixed here: outside the files. Filed as T123; lands before T124.";
    let bad = "- The roads break. Filed as T123.";
    let s = sec(&format!(
        "\n{ok}\n{bad}\n  its second line.\n- T17's own, written before its tick."
    ));
    let got = unformed(&s, &b);
    assert_eq!(got.len(), 1, "{got:?}");
    let ((a, z), text) = &got[0];
    assert_eq!(
        &s[*a..*z],
        "- The roads break. Filed as T123.\n  its second line."
    );
    assert!(text.contains("no reason, no order"), "{text}");
}

#[test]
fn a_deferral_to_a_task_no_longer_open_is_refused_at_the_decision_alone() {
    let (_dir, b) = fixture();
    for (found, id) in [
        ("- The wells break. Not fixed here: outside the files. Filed as T120; lands before T124.", "T120"),
        ("- The wells break. Not fixed here: outside the files. Filed as T110; lands before T124.", "T110"),
        ("- The wells break. Not fixed here: outside the files. Filed as T123; lands before T120.", "T120"),
        ("- The wells break. Not fixed here: outside the files. Filed as T123; lands before T124, T22 and T110.", "T110"),
    ] {
        let s = sec(found);
        assert!(unformed(&s, &b).is_empty(), "{found}");
        let got = words(&closed(&s, &b));
        assert_eq!(got.len(), 1, "{found}: {got:?}");
        assert!(got[0].contains(&format!("{id} is not an open task")), "{got:?}");
    }
}

#[test]
fn the_real_t14_block_passes_and_t16s_is_refused() {
    let (_dir, b) = fixture();
    let t14 = "\n- T14's own, written before its tick (the session wrote them, 2026-11-20): the `docs/guards.md` row, the `STATIC_RUNS_A_TASK` row of its knob\n  table (D14), the `rust/guard/CLAUDE.md` mention.\n- The guard crate's tests read the process's environment: with `L7R_FEATURE_DIRECTORY` exported (a page session exports it), 17 to\n  20 tests of other guards fail, measured 2026-11-20 (`make rust-test CRATE=rust/guard FRESH=1` with it exported).\n  Not fixed here: it is in six other guards' tests, outside T14's files. How every instance was found: the crate's whole test run under\n  the export. Filed as T32; lands before T22 (SC-005 is measured on work that runs these tests).\n- `guard_file_hooks` refused this builder's `sed -i` on a guard file but let a Python heredoc write the same files. Not fixed here: `guard_file_hooks` is outside T14's files. Filed as T33; lands\n  before T22.\n- No make target formats one file. Not fixed here (a Makefile change, outside T14's files). Filed as T34; lands before T22.";
    let s = sec(t14).replace("T17", "T14");
    assert!(unformed(&s, &b).is_empty(), "{:?}", unformed(&s, &b));
    assert!(closed(&s, &b).is_empty());
    assert!(class_unlabeled(&s).is_empty(), "{:?}", class_unlabeled(&s));
    let t16 = sec("\n- `POLL_CHECK_S` goes into D14's knob table with T22, which lands before the close (T22 is the close).");
    assert_eq!(unformed(&t16, &b).len(), 1);
}

#[test]
fn a_class_fix_carries_its_labeled_line() {
    for (text, refused) in [
        (sec("- Every writer of the log dropped its newline; fixed here."), true),
        (
            sec("- Every writer of the log dropped its newline; fixed here (observed 2026-11-20, method: a grep for the log's writers)."),
            false,
        ),
        (
            sec("- All the readers of the stamp skip it; fixed here, measured 2026-11-20 (`make rust-test`, the readers' tests)."),
            false,
        ),
        (
            "### T17 Approach\n\n12. **Before any fix.** Each of the guards reads the variable; each now takes it as an argument.\n\n**Found and left?** none\n".to_owned(),
            true,
        ),
        (
            "### T17 Approach\n\n12. **Before any fix.** Each of the guards reads the variable (observed 2026-11-20, method: a grep of `rust/guard`).\n\n**Found and left?** none\n".to_owned(),
            false,
        ),
        (
            "### T17 Approach\n\n12. **Before any fix.** n/a - every writer is named in item 9.\n\n**Found and left?** none\n".to_owned(),
            true,
        ),
        (
            "### T17 Approach\n\n9. **Done.** Every file of the crate is covered.\n12. **Before any fix.** n/a.\n\n**Found and left?** none\n".to_owned(),
            false,
        ),
    ] {
        let got = class_unlabeled(&text);
        assert_eq!(!got.is_empty(), refused, "{text}: {got:?}");
    }
}
