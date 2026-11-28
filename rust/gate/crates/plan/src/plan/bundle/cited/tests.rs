//! What a block cites, read from where its name points (461 T68).

use std::path::Path;

use super::super::super::tests::repo;
use super::super::build;
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

/// A decision named with another feature's task, `451 T274's D3 (its gloss), D13 (...), D5`, is that task's section's, from that feature's
/// plan.md or plan-done.md, every id of the glossed run; a plan's `### D7 - title` decision is read; a section's own indented `- **D1.`
/// decisions are its own; a bare id found nowhere is named NOT FOUND (461 T68: 461 T61's bundle carried 451's plan-level D3 for T274's
/// and dropped D13 and D5; 461 T65's carried nothing, 461's decisions all being headings).
#[test]
fn a_decision_named_with_another_feature_s_task_is_that_task_s() {
    let root = repo();
    let (dir, other) = (root.join("specs/461-x"), root.join("specs/451-y"));
    for d in [&dir, &other] {
        std::fs::create_dir_all(d).unwrap();
    }
    std::fs::write(dir.join("plan.md"), "# Plan\n\n### D1 - OURS ONE\n\nx\n\n### D3 - OURS THREE\n\nx\n\n### D5 - OURS FIVE\n\nx\n\n### D7 - OURS SEVEN\n\nThe repair.\n\n### D13 - OURS THIRTEEN\n\nx\n").unwrap();
    std::fs::write(
        dir.join("spec.md"),
        "## Requirements\n\n- **FR-001**: Ours.\n",
    )
    .unwrap();
    std::fs::write(dir.join("request.md"), "> words\n").unwrap();
    std::fs::write(
        other.join("plan.md"),
        "# Plan\n\n**D3 - THEIRS PLAN THREE.** x\n",
    )
    .unwrap();
    std::fs::write(other.join("plan-done.md"), "## Done\n\n### T274 (the sampler)\n\n- **Decisions**:\n  - **D3. The sampler names itself.** Its pid file.\n  - **D5. Started through setsid.** Detached.\n  - **D13. The knobs.** Twelve hours.\n").unwrap();
    let out = scratch("out");
    let body = "### T61 (the sampler re-runs)\n\n- **Decisions**:\n  - **D1. Re-exec.** x\n  - **D2. The same process.** As D1 says.\n\n2. **The constraints.** 451 T274's D3 (the pid file names the sampler), D13 (`L7R_SAMPLE_MAX_H` bounds a\n   run), D5 (detached, no inherited descriptor); plan D7; 451 T999's D2; 451 T274's D4; D9.\n";
    let m = build(
        &dir,
        &out,
        "T61",
        &under(&[("### T61 (the sampler re-runs)", body)]),
        &[],
        "h",
    )
    .unwrap();
    let cited = read(m.parent().unwrap(), "spec-cited.md");
    for theirs in [
        "<!-- feature 451 T274 -->\n  - **D3. The sampler names itself.**",
        "<!-- feature 451 T274 -->\n  - **D5. Started through setsid.**",
        "<!-- feature 451 T274 -->\n  - **D13. The knobs.**",
        "### D7 - OURS SEVEN\n\nThe repair.",
        "- **D2**: NOT FOUND - specs/451-y has no T999 section in its plan.md or plan-done.md",
        "- **D4**: NOT FOUND - T274's section in specs/451-y holds no D4",
        "- **D9**: NOT FOUND - feature 461's spec.md, plan.md and plan-done.md hold no D9",
    ] {
        assert!(cited.contains(theirs));
    }
    for wrong in [
        "THEIRS PLAN",
        "OURS ONE",
        "OURS THREE",
        "OURS FIVE",
        "OURS THIRTEEN",
    ] {
        assert!(!cited.contains(wrong));
    }
    // a task named with this feature's number is read from that task's section too, and an FR a task names stays the spec's
    let body = "461 T61's D2 and 451 T274's FR-001.\n";
    let m = build(&dir, &out, "T62", &under(&[("T62", body)]), &[], "h").unwrap();
    let cited = read(m.parent().unwrap(), "spec-cited.md");
    let ours = "- **D2**: NOT FOUND - specs/461-x has no T61 section";
    assert!(cited.contains(ours) && !cited.contains("OURS"));
    assert!(cited.contains("<!-- feature 451 -->\n- **FR-001**: NOT FOUND"));
}

/// A task's numbered decision, `T16's Decision 3` (`Decisions 2 and 5`, `451 T16's Decision 1`), is read from that task's `**Decisions**`
/// list, never its Approach checklist's same number; a spec file's entry, `data-model.md, "A repair entry"` or `data-model.md's repair
/// entry`, is its heading's section, a quoted phrase no heading holds its paragraph; each not found is a NOT FOUND line; request.md's
/// quotes are the request's own words, carried beside (461 T69: 461 T65's bundle carried none of them).
#[test]
fn a_task_s_numbered_decision_and_a_spec_file_s_entry_are_carried() {
    let root = repo();
    let (dir, other) = (root.join("specs/461-x"), root.join("specs/451-y"));
    for d in [&dir, &other] {
        std::fs::create_dir_all(d).unwrap();
    }
    let plan = "# Plan\n\n### D7 - PLAN SEVEN\n\nx\n\n## Tasks\n\n### T16 (the queue)\n\n**Decisions** (each labeled):\n\n1. **SIXTEEN ONE.** x\n2. **SIXTEEN TWO.** x\n3. **SIXTEEN THREE.** Open is read.\n5. **SIXTEEN FIVE.** x\n\n### T16 Approach (checklist part A)\n\n3. **APPROACH THREE.** x\n\n### T17 (no list)\n\n- **Approach**: x\n";
    std::fs::write(dir.join("plan.md"), plan).unwrap();
    std::fs::write(dir.join("spec.md"), "- **FR-001**: Ours.\n").unwrap();
    std::fs::write(dir.join("request.md"), "> words\n").unwrap();
    std::fs::write(dir.join("data-model.md"), "# Data\n\n## A hand-in\n\nHAND IN.\n\n## A repair entry (`repairs.jsonl`)\n\nREPAIR BODY.\n\n### Its fields\n\nFIELDS.\n\n## The log line\n\nLOG. The earlier one's entry read as closed.\n\nNEXT.\n").unwrap();
    std::fs::write(
        other.join("plan.md"),
        "### T16 (x)\n\n**Decisions**:\n\n1. **THEIRS ONE.** x\n",
    )
    .unwrap();
    let out = scratch("out");
    let body = "Label: data-model.md, \"A repair entry\", as T16's Decision 3 states it; T16's Decisions 2 and 5; 451 T16's Decision 1; data-model.md's repair entry; data-model.md, \"the earlier one's entry\"; T16's Decision 4; T17's Decision 1; T99's Decision 1; 999 T1's Decision 1; data-model.md, \"No such words\"; data-model.md's batch entry; research.md, \"A\"; request.md, \"words\".\n";
    let m = build(&dir, &out, "T65", &under(&[("T65", body)]), &[], "h").unwrap();
    let cited = read(m.parent().unwrap(), "spec-cited.md");
    for want in [
        "<!-- feature 461 T16, Decision 3 -->\n3. **SIXTEEN THREE.** Open is read.\n",
        "<!-- feature 461 T16, Decision 2 -->\n2. **SIXTEEN TWO.**",
        "<!-- feature 461 T16, Decision 5 -->\n5. **SIXTEEN FIVE.**",
        "<!-- feature 451 T16, Decision 1 -->\n1. **THEIRS ONE.**",
        "<!-- data-model.md, \"A repair entry\" -->\n## A repair entry (`repairs.jsonl`)\n\nREPAIR BODY.\n\n### Its fields\n\nFIELDS.\n",
        "<!-- data-model.md, \"the earlier one's entry\" -->\nLOG. The earlier one's entry read as closed.\n",
        "- **T16's Decision 4**: NOT FOUND - T16's section in specs/461-x lists no decision 4",
        "- **T17's Decision 1**: NOT FOUND - T17's section in specs/461-x lists no decision 1",
        "- **T99's Decision 1**: NOT FOUND - specs/461-x has no T99 section",
        "- **T1's Decision 1**: NOT FOUND - feature 999 has no directory under specs/",
        "- **data-model.md, \"No such words\"**: NOT FOUND - specs/461-x/data-model.md holds no heading or paragraph with those words",
        "- **data-model.md's batch entry**: NOT FOUND - specs/461-x/data-model.md holds no heading naming a batch entry",
        "- **research.md, \"A\"**: NOT FOUND - specs/461-x has no research.md",
    ] {
        assert!(cited.contains(want), "{want}\n---\n{cited}");
    }
    assert_eq!(cited.matches("REPAIR BODY").count(), 1);
    for wrong in [
        "APPROACH THREE",
        "NEXT.",
        "HAND IN",
        "SIXTEEN ONE",
        "request.md",
    ] {
        assert!(!cited.contains(wrong), "{wrong}");
    }
}

/// A clause after a task's run naming the run's own feature cuts nothing from it; a task named with no number is this feature's, read
/// from its section; and a block's bare decision its task's other block defines is that section's own (461 T68, T68's plan review).
#[test]
fn a_task_s_run_keeps_its_clause_and_an_unnumbered_task_is_this_feature_s() {
    let root = repo();
    let (dir, other) = (root.join("specs/461-x"), root.join("specs/451-y"));
    for d in [&dir, &other] {
        std::fs::create_dir_all(d).unwrap();
    }
    let section = "### T61 (the sampler)\n\n- **Decisions**:\n  - **D1. SECTION ONE.** x\n  - **D2. SECTION TWO.** x\n\n### T61 Approach (checklist part A)\n\n1. **The goal.** As D1 says.\n";
    let plan = format!(
        "# Plan\n\n### D1 - PLAN ONE\n\nx\n\n### D5 - PLAN FIVE\n\nx\n\n## Tasks\n\n{section}"
    );
    std::fs::write(dir.join("plan.md"), plan).unwrap();
    std::fs::write(dir.join("spec.md"), "- **FR-001**: Ours.\n").unwrap();
    std::fs::write(dir.join("request.md"), "> words\n").unwrap();
    std::fs::write(other.join("plan.md"), "**D5 - THEIRS PLAN FIVE.** x\n\n### T274 (x)\n\n  - **D3. THEIRS THREE.** x\n  - **D5. THEIRS FIVE.** x\n").unwrap();
    let out = scratch("out");
    let body = "451 T274's D3, D13 and D5 from 451's plan-done.md; T61's D2 and FR-001.\n";
    let m = build(&dir, &out, "T68", &under(&[("T68", body)]), &[], "h").unwrap();
    let cited = read(m.parent().unwrap(), "spec-cited.md");
    for want in [
        "<!-- feature 451 T274 -->\n  - **D3. THEIRS THREE.**",
        "<!-- feature 451 T274 -->\n  - **D5. THEIRS FIVE.**",
        "<!-- feature 451 T274 -->\n- **D13**: NOT FOUND - T274's section in specs/451-y holds no D13",
        "<!-- feature 461 T61 -->\n  - **D2. SECTION TWO.**",
        "- **FR-001**: Ours.",
    ] {
        assert!(cited.contains(want));
    }
    assert!(!cited.contains("PLAN FIVE") && !cited.contains("<!-- feature 451 -->"));
    // the Approach block alone: its bare D1 is the section's, which its other block defines
    let approach = &section[section.find("### T61 Approach").unwrap()..];
    let key = "### T61 Approach (checklist part A)";
    let m = build(&dir, &out, "T61", &under(&[(key, approach)]), &[], "h").unwrap();
    assert!(!read(m.parent().unwrap(), "spec-cited.md").contains("PLAN ONE"));
}

/// A template's placeholder quote, `data-model.md, "<words>"`, names no entry and writes no NOT FOUND line; a real quote beside it is
/// still read (461 T71: 461 T69's bundle wrote a NOT FOUND line for `"<words>"`).
#[test]
fn a_placeholder_quote_is_no_citation() {
    let root = repo();
    let dir = root.join("specs/461-x");
    std::fs::create_dir_all(&dir).unwrap();
    std::fs::write(dir.join("plan.md"), "# Plan\n").unwrap();
    std::fs::write(dir.join("spec.md"), "- **FR-001**: Ours.\n").unwrap();
    std::fs::write(dir.join("request.md"), "> words\n").unwrap();
    std::fs::write(
        dir.join("data-model.md"),
        "# Data\n\n## Recovery\n\nRECOVER.\n",
    )
    .unwrap();
    let out = scratch("out");
    let body = "The forms: `data-model.md, \"<words>\"` and data-model.md, \"Recovery\".\n";
    let m = build(&dir, &out, "T71", &under(&[("T71", body)]), &[], "h").unwrap();
    let cited = read(m.parent().unwrap(), "spec-cited.md");
    assert!(
        cited.contains("<!-- data-model.md, \"Recovery\" -->\n## Recovery\n\nRECOVER.\n"),
        "{cited}"
    );
    assert!(!cited.contains("<words>"), "{cited}");
}
