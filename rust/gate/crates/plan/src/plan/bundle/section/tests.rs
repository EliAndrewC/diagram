//! A labeled task section's own decisions in the plan review's bundle (451 T438).

use std::path::Path;

use super::super::super::tests::repo;
use super::super::{build, ids_in, named};
use crate::checks::scratch;

fn under(pairs: &[(&str, &str)]) -> Vec<(String, String)> {
    pairs
        .iter()
        .map(|(k, b)| ((*k).to_owned(), (*b).to_owned()))
        .collect()
}

fn read(dir: &Path, name: &str) -> String {
    std::fs::read_to_string(dir.join(name)).unwrap()
}

/// A bare D<n> in a task section that writes its own decisions `T<n>-D<k>` is that section's, not the spec's (451 T438, found by the
/// round-2 plan reviewer of 451 T369, 2026-11-27: T369's section, labeled T369-D1 to D4, wrote "(D1)" and "(D3)" bare, and its
/// bundle carried the spec's D1 and D3). The spec's own decisions are still carried where the section names them as the spec's.
#[test]
fn a_bare_decision_in_a_labeled_task_section_is_the_section_s_own() {
    let root = repo();
    let dir = root.join("specs/451-x");
    std::fs::create_dir_all(&dir).unwrap();
    let section = "### T369 (found by 451 T359's closing half)\n\n- **Decisions**:\n  - **T369-D1, built: one mark a task A TREE.** Reason: as before.\n  - **T369-D3, built: the layout of before T369 is read as written.**\n\n| step | test |\n|---|---|\n| start in tree A, unstart in B: the readers agree (D1) | `a` |\n| the marks' layout (D2 to D4) | `b` |\n\nThe real clone's start log (D1) and marks directory (D3); the section's D4 too. Bound by spec D5, the plan's D6, 451 D7 and FR-002.\n\n### T369 Approach (checklist part A)\n\n1. **The rule.** One mark a tree (D1), as D3 reads it.\n";
    let plan = format!("# Plan\n\n**D1 - SPEC ONE.** x\n\n**D2 - SPEC TWO.** x\n\n**D3 - SPEC THREE.** x\n\n**D4 - SPEC FOUR.** x\n\n**D5 - SPEC FIVE.** x\n\n**D6 - SPEC SIX.** x\n\n**D7 - SPEC SEVEN.** x\n\n## Tasks\n\n{section}\n### T05 - an unlabeled section\n\nAs D1 says.\n");
    std::fs::write(dir.join("plan.md"), &plan).unwrap();
    std::fs::write(
        dir.join("spec.md"),
        "## Requirements\n\n- **FR-002**: Ours.\n",
    )
    .unwrap();
    std::fs::write(dir.join("request.md"), "> words\n").unwrap();
    let out = scratch("out");
    let m = build(
        &dir,
        &out,
        "T369",
        &under(&[("the section of T369", section)]),
        &[],
        "h",
    )
    .unwrap();
    let cited = read(m.parent().unwrap(), "spec-cited.md");
    for (spec_only, why) in [
        ("SPEC ONE", "D1"),
        ("SPEC TWO", "D2"),
        ("SPEC THREE", "D3"),
        ("SPEC FOUR", "D4"),
    ] {
        assert!(!cited.contains(spec_only), "{why}: {cited}");
    }
    assert!(
        cited.contains("SPEC FIVE") && cited.contains("SPEC SIX") && cited.contains("SPEC SEVEN")
    );
    assert!(cited.contains("- **FR-002**: Ours."));
    // a block of the section with no label of its own is still the labeled section's; an unlabeled section's bare D1 is the spec's
    let approach = &section[section.find("### T369 Approach").unwrap()..];
    let tail = "### T05 - an unlabeled section\n\nAs D1 says.\n";
    let m = build(
        &dir,
        &out,
        "blocks",
        &under(&[
            ("### T369 Approach (checklist part A)", approach),
            ("### T05 - an unlabeled section", tail),
        ]),
        &[],
        "h",
    )
    .unwrap();
    let cited = read(m.parent().unwrap(), "spec-cited.md");
    assert!(cited.contains("SPEC ONE") && !cited.contains("SPEC THREE"));
    let m = build(
        &dir,
        &out,
        "approach",
        &under(&[("### T369 Approach (checklist part A)", approach)]),
        &[],
        "h",
    )
    .unwrap();
    assert!(!read(m.parent().unwrap(), "spec-cited.md").contains("SPEC ONE"));
}

/// The section's own possessives in a labeled section are the section's, as its bare ids are (451 T438, T438-D3).
#[test]
fn a_labeled_section_s_own_possessives_are_taken_out() {
    let owners = ["T369".to_owned()];
    let n = named(
        "T369's D1, the task's D2, the block's D3 and the section's D4; the plan's D5, T295's D6.\n",
        "451",
        &owners,
    );
    assert_eq!(ids_in(&n.bare), ["D5"]);
}

/// Another task's possessive decision in a labeled section is that task's own, `T295-D3`, not the spec's D3 (451 T467: 451 T306's
/// section, labeled T306-D1 to D3, wrote "T295's D3 limit", and its bundle carried the spec's D3). An unlabeled section's `T31's D3`
/// is read as before, the spec's.
#[test]
fn another_task_s_possessive_decision_in_a_labeled_section_is_that_task_s() {
    let root = repo();
    let dir = root.join("specs/451-x");
    std::fs::create_dir_all(&dir).unwrap();
    let section = "### T306 (found by 451 T295)\n\n- **Decisions**:\n  - **T306-D2, the plan hold places a Bash call where its command lands.** T295's D3 limit ends here; T12a's D4 and T7's D1, D2 too, and 451 T183's D2. Bound by spec D5 and 451 D5.\n";
    let plan = format!("# Plan\n\n**D1 - SPEC ONE.** x\n\n**D2 - SPEC TWO.** x\n\n**D3 - SPEC THREE.** x\n\n**D4 - SPEC FOUR.** x\n\n**D5 - SPEC FIVE.** x\n\n## Tasks\n\n{section}\n### T05 - an unlabeled section\n\nAs T31's D3 says.\n");
    std::fs::write(dir.join("plan.md"), &plan).unwrap();
    std::fs::write(
        dir.join("spec.md"),
        "## Requirements\n\n- **FR-002**: Ours.\n",
    )
    .unwrap();
    std::fs::write(dir.join("request.md"), "> words\n").unwrap();
    let out = scratch("out");
    let m = build(
        &dir,
        &out,
        "T306",
        &under(&[("the section of T306", section)]),
        &[],
        "h",
    )
    .unwrap();
    let cited = read(m.parent().unwrap(), "spec-cited.md");
    for spec_only in ["SPEC ONE", "SPEC TWO", "SPEC THREE", "SPEC FOUR"] {
        assert!(!cited.contains(spec_only), "{spec_only}: {cited}");
    }
    assert!(cited.contains("SPEC FIVE"), "{cited}");
    let tail = "### T05 - an unlabeled section\n\nAs T31's D3 says.\n";
    let m = build(
        &dir,
        &out,
        "T05",
        &under(&[("### T05 - an unlabeled section", tail)]),
        &[],
        "h",
    )
    .unwrap();
    assert!(read(m.parent().unwrap(), "spec-cited.md").contains("SPEC THREE"));
}
