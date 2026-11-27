//! RED FIRST (feature 451 T462, the round arbiter's process-fault on `round:spec-fidelity|plan:451-time-retro-and-efficiency#T448@3`,
//! 2026-11-27): a task section still the `make task-add` template byte for byte is UNWRITTEN. T448's stub rode in other tasks'
//! `make plan-delta F=451` bundles, four reviewers ruled it decides nothing, and those rounds tripped the cap and held every plan-delta
//! dispatch of the feature. An unwritten section is left out of every bundle `make plan-delta` writes, and the arbiter's accept or
//! process-fault on its round records no verdict for it: it owes its first review once written, whatever was recorded before.

use std::path::Path;

use serde_json::{json, Value};

use super::super::record::arbiter_accept;
use super::super::sections::{block_digest, blocks, digest, task_sections};
use super::super::status::owed_for;
use super::super::template::stubs;
use super::{repo, run, write_json};

const BOXES: &str = "# Tasks\n\n- [ ] T05 the bath\n- [ ] T07 the gate\n";

/// `tests::feature_at` with T05's and T07's boxes, the tasks the plan's sections are.
fn feature_at(
    root: &Path,
    plan: Option<&str>,
    review: Option<&Value>,
    name: &str,
) -> std::path::PathBuf {
    let dir = super::feature_at(root, plan, review, name);
    std::fs::write(dir.join("tasks.md"), BOXES).unwrap();
    dir
}

const REAL: &str = concat!(
    "# plan\n\n### T05 (the bath)\n\n- **Approach**: one tub by the door.\n\n### T05 Approach (checklist part A)\n\n",
    "1. **The goal.** a bath\n6. **The exits.** Green: landed. Red: what failed recorded and the task set down, a claim that it ",
    "cannot be done ruled through `make arbiter-ask`.\n\n"
);
const FILLED: &str = "<the place as it should be>";

/// A plan of T05's real section and T07's unfilled stub (its plain form, or the performance form with `perf`).
fn with_stub(perf: bool) -> String {
    let [with_perf, plain, ..] = stubs("T07");
    format!("{REAL}{}", if perf { with_perf } else { plain })
}

/// The `blocks.md` of the one bundle `make plan-delta` wrote under `root`.
fn bundled(root: &Path) -> String {
    let dirs: Vec<_> = std::fs::read_dir(root.join("bundles"))
        .unwrap()
        .flatten()
        .map(|e| e.path())
        .collect();
    assert_eq!(dirs.len(), 1, "{dirs:?}");
    std::fs::read_to_string(dirs[0].join("blocks.md")).unwrap()
}

fn fresh_bundles(root: &Path) {
    let _ = std::fs::remove_dir_all(root.join("bundles"));
}

fn review(dir: &Path) -> Value {
    serde_json::from_str(&std::fs::read_to_string(dir.join("plan-review.json")).unwrap()).unwrap()
}

#[test]
fn a_blank_stub_rides_in_no_bundle_until_its_text_differs() {
    for perf in [false, true] {
        let root = repo();
        let dir = feature_at(&root, Some(&with_stub(perf)), None, "375-x");
        let got = run(&root, &["delta", "375"]);
        assert_eq!(got.code, 0, "{}", got.stderr);
        // the bundle's name lists the tasks it holds, which the review-round guard counts a round of each
        let label = got.stdout.contains("-blocks-T05-") && !got.stdout.contains("-blocks-T05-T07-");
        assert!(label, "{}", got.stdout);
        let blocks_md = bundled(&root);
        assert!(blocks_md.contains("### T05 (the bath)"), "{blocks_md}");
        assert!(!blocks_md.contains("T07"), "{blocks_md}");
        // a BLOCKED bundle verdict that named the stub (T448's rounds) does not put it back
        let stub_keys: serde_json::Map<String, Value> = blocks(&with_stub(perf))
            .into_iter()
            .filter(|(k, ..)| k.contains("T07"))
            .map(|(k, b, _)| (k, json!(block_digest(&b))))
            .collect();
        let blocked = json!({"blocks": stub_keys, "decisions": [super::narrow_bad()]});
        let src = write_json(&root, "b.json", &blocked);
        let recorded = run(
            &root,
            &["record-blocks", "375", &src, "--as", "spec-fidelity"],
        );
        assert_eq!(recorded.code, 0, "{}", recorded.stderr);
        fresh_bundles(&root);
        assert_eq!(run(&root, &["delta", "375"]).code, 0);
        assert!(!bundled(&root).contains("T07"));
        // its text first differs from the template: it is written, and owed
        let written = with_stub(perf).replace(FILLED, "the tub by the door");
        std::fs::write(dir.join("plan.md"), &written).unwrap();
        fresh_bundles(&root);
        let got = run(&root, &["delta", "375"]);
        assert!(got.stdout.contains("-blocks-T05-T07-"), "{}", got.stdout);
        assert!(bundled(&root).contains("### T07 Approach (checklist part A)"));
    }
}

#[test]
fn a_stub_beside_a_written_block_of_its_own_is_written_and_a_stub_alone_owes_no_whole_plan_review()
{
    let root = repo();
    let part_b = format!(
        "{}\n### T07 part B\n\n- the wells moved\n",
        with_stub(false)
    );
    feature_at(&root, Some(&part_b), None, "375-x");
    assert_eq!(run(&root, &["delta", "375"]).code, 0);
    assert!(bundled(&root).contains("### T07 Approach (checklist part A)"));
    // a plan of the stub alone, its record empty: neither plan-delta nor the feature's judgment owes it
    let root = repo();
    let [_, plain, ..] = stubs("T07");
    let dir = feature_at(&root, Some(&plain), Some(&json!({})), "375-x");
    assert!(run(&root, &["delta", "375"])
        .stdout
        .contains("no block of 375-x's plan is owed"));
    assert_eq!(run(&root, &["owed", &dir.to_string_lossy()]).code, 0);
    // the tick of the stub's own task still owes it: an unwritten section is no decision to tick
    let held = owed_for(&dir, &["T07"]).unwrap();
    assert_eq!(held.0, "plan-review-stale", "{held:?}");
}

#[test]
fn a_process_fault_on_a_stub_s_round_records_no_verdict_and_the_filled_section_owes_its_review() {
    let root = repo();
    let dir = feature_at(&root, Some(&with_stub(false)), Some(&json!({})), "375-x");
    let trigger = "round:spec-fidelity|plan:375-x#T07@3";
    let ruling = json!({"trigger": trigger, "ruling": "process-fault", "tooling_fix": "x"});
    std::fs::write(dir.join("arbiter.jsonl"), format!("{ruling}\n")).unwrap();
    let got = arbiter_accept(&dir, trigger, Some("2026-11-27")).unwrap();
    assert!(got.blocks.is_empty() && got.tasks.is_empty(), "{got:?}");
    assert_eq!(got.unwritten, ["T07"]);
    let after = review(&dir);
    assert!(
        after.get("tasks").is_none_or(|t| t.get("T07").is_none()),
        "{after}"
    );
    assert!(
        after.get("blocks").is_none_or(|b| b
            .as_object()
            .unwrap()
            .keys()
            .all(|k| !k.contains("T07"))),
        "{after}"
    );
    assert!(after.get("block_reviews").is_none(), "{after}");
    // a record that holds the stub's blocks and task CLEAR, as the arbiter wrote T448's before T462: the filled section is owed
    let plan = with_stub(false);
    let section = &task_sections(&plan)["T07"];
    let stub_clear: serde_json::Map<String, Value> = blocks(&plan)
        .into_iter()
        .filter(|(k, ..)| k.contains("T07"))
        .map(|(k, b, _)| (k, json!({"sha256": block_digest(&b), "verdict": "CLEAR"})))
        .collect();
    let old = json!({"blocks": stub_clear, "tasks": {"T07": {"section_sha256": digest(section.as_bytes()), "verdict": "CLEAR"}}});
    std::fs::write(dir.join("plan-review.json"), old.to_string()).unwrap();
    std::fs::write(
        dir.join("plan.md"),
        plan.replace(FILLED, "the tub by the door"),
    )
    .unwrap();
    let got = run(&root, &["delta", "375"]);
    assert!(got.stdout.contains("-blocks-T05-T07-"), "{}", got.stdout);
    assert!(bundled(&root).contains("the tub by the door"));
}
