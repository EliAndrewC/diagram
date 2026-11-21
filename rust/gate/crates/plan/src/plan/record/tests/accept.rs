//! RED FIRST (feature 451 T92): the round arbiter's accept on one task's plan round is that task's verdict and no other's. Measured
//! 2026-11-21 (`ask:451-T79-third-plan-round`, plan-review.json's history): `make arbiter-ruled` recorded 28 blocks CLEAR where the
//! question was T79's section alone - T76's and T77's changed blocks among them - and left T79's task verdict BLOCKED, the one the
//! tick, the push and `l7r-gate plan decided` read.

use std::collections::BTreeSet;
use std::path::{Path, PathBuf};

use l7r_shared::tempdir::Held;

use serde_json::{json, Value};

use super::super::super::sections::{block_digest, blocks, digest, task_sections};
use super::super::super::status::{block_status, owed_for, task_current};
use super::super::super::task::task_refusal;
use super::super::super::tests::{feature, narrow_bad};
use super::super::{arbiter_accept, record_blocks, record_task};
use super::read;

const BEFORE: &str = "# plan\n\n## Shared\n\nthe shared rule.\n\n## T01 the bath\n\n- one tub\n\n### T01 Approach (checklist part A)\n\n1. **The goal.** a bath\n\n## T02 the wells\n\n- a well\n";
/// The shared block, T01's and T02's each changed since their CLEAR review.
const AFTER: &str = "# plan\n\n## Shared\n\nthe shared rule, changed.\n\n## T01 the bath\n\n- one tub, by the door\n\n### T01 Approach (checklist part A)\n\n1. **The goal.** a bath\n\n## T02 the wells\n\n- a well, deeper\n";

/// Every block of BEFORE reviewed CLEAR, then AFTER written, T01's section reviewed BLOCKED and `trigger` accepted: T79's history.
fn accepted_on(trigger: &str, review: &str) -> (Held<PathBuf>, Value) {
    let dir = feature(Some(BEFORE), None);
    let all: serde_json::Map<String, Value> = blocks(BEFORE)
        .into_iter()
        .map(|(k, b, _)| (k, json!(block_digest(&b))))
        .collect();
    record_blocks(
        &dir,
        &json!({"blocks": all, "decisions": []}),
        "spec-fidelity",
        None,
    )
    .unwrap();
    std::fs::write(dir.join("plan.md"), AFTER).unwrap();
    let section = &task_sections(AFTER)["T01"];
    let blocked =
        json!({"section_sha256": digest(section.as_bytes()), "decisions": [narrow_bad()]});
    assert_eq!(
        record_task(&dir, "T01", &blocked, "spec-fidelity", None).unwrap()["verdict"],
        "BLOCKED"
    );
    std::fs::write(
        dir.join("arbiter.jsonl"),
        format!(
            "{}\n",
            json!({"trigger": trigger, "ruling": "accept", "review": review})
        ),
    )
    .unwrap();
    let got = arbiter_accept(&dir, trigger, Some("2026-11-21")).unwrap();
    (dir, json!({"blocks": got.blocks, "tasks": got.tasks}))
}

fn owed_now(dir: &Path) -> Vec<String> {
    let plan = std::fs::read_to_string(dir.join("plan.md")).unwrap();
    let (owed, blocked) = block_status(&read(dir), &plan, &BTreeSet::new(), None, "");
    owed.into_iter().chain(blocked).collect()
}

#[test]
fn an_accept_on_one_task_s_round_clears_that_task_s_blocks_alone() {
    for (trigger, review) in [
        ("ask:243-T01-third-round", "plan"),
        ("round:spec-fidelity|plan:243-x#T01@3", ""),
    ] {
        let (dir, got) = accepted_on(trigger, review);
        assert_eq!(got["blocks"], json!(["## T01 the bath"]), "{trigger}");
        assert_eq!(
            owed_now(&dir),
            ["## Shared", "## T02 the wells"],
            "{trigger}: a second task's changed block and a shared one are not the question's"
        );
        let review = read(&dir);
        assert!(review["blocks"]["## Shared"]["declared"] != "round-arbiter");
        assert_eq!(
            review["block_reviews"].as_array().unwrap().last().unwrap()["tasks"],
            json!(["T01"])
        );
    }
}

#[test]
fn an_accepted_task_reads_as_decided_where_its_blocks_cannot_carry_it() {
    let (dir, got) = accepted_on("ask:243-T01-third-round", "plan");
    let root = dir.parent().unwrap().parent().unwrap();
    // the store the tick, the push, `plan decided` and the builder-stop guard read: the accept, not the reviewer's BLOCKED
    let entry = &read(&dir)["tasks"]["T01"];
    assert_eq!(entry["verdict"], "CLEAR");
    assert_eq!(task_refusal(root, "243", "T01"), "");
    assert_eq!(got["tasks"], json!(["T01"]));
    assert_eq!(entry["declared"], "round-arbiter");
    assert_eq!(
        entry["section_sha256"],
        digest(task_sections(AFTER)["T01"].as_bytes())
    );
    assert_eq!(entry["decisions"][0]["id"], "ask:243-T01-third-round");
    // the reviewer's BLOCKED entry is kept beside the accept, never lost
    assert_eq!(entry["accepted_over"]["verdict"], "BLOCKED");
    assert_eq!(entry["accepted_over"]["declared"], "spec-fidelity");
    // the shared block is still owed, so the block arm (`owed_for` none and the section CLEAR) cannot carry T01: the task verdict does
    let owed = owed_for(&dir, &["T01"]).unwrap().1;
    assert!(
        owed.contains("## Shared") && !owed.contains("## T01"),
        "{owed}"
    );
    assert!(task_current(&read(&dir), AFTER, "T01", None));
    // the other task is not decided by T01's accept
    assert!(!task_refusal(root, "243", "T02").is_empty());
}

#[test]
fn the_question_names_its_scope_and_an_archived_section_clears_nothing() {
    // two tasks named: both sections, and each its verdict
    let (dir, got) = accepted_on("ask:243-plan-T01-T02", "plan");
    assert_eq!(
        got["blocks"],
        json!(["## T01 the bath", "## T02 the wells"])
    );
    assert_eq!(got["tasks"], json!(["T01", "T02"]));
    assert_eq!(owed_now(&dir), ["## Shared"]);
    // a task whose section is archived: nothing recorded, never the whole plan
    let dir = feature(Some(AFTER), None);
    std::fs::write(
        dir.join("plan-done.md"),
        "# done\n\n## T07 the gate\n\n- done\n",
    )
    .unwrap();
    let trigger = "ask:243-T07-third-round";
    std::fs::write(
        dir.join("arbiter.jsonl"),
        format!(
            "{}\n",
            json!({"trigger": trigger, "ruling": "accept", "review": "plan"})
        ),
    )
    .unwrap();
    let got = arbiter_accept(&dir, trigger, None).unwrap();
    assert!(got.blocks.is_empty() && got.tasks.is_empty() && !got.whole);
    assert!(!dir.join("plan-review.json").exists() || read(&dir).get("tasks").is_none());
    // a task with no section anywhere is judged by the plan-stage review, as `plan decided` reads it: the whole plan
    let trigger = "ask:243-T09-third-round";
    std::fs::write(
        dir.join("arbiter.jsonl"),
        format!(
            "{}\n",
            json!({"trigger": trigger, "ruling": "accept", "review": "plan"})
        ),
    )
    .unwrap();
    let got = arbiter_accept(&dir, trigger, None).unwrap();
    assert!(got.whole && got.tasks.is_empty());
    assert_eq!(got.blocks.len(), blocks(AFTER).len());
}

#[test]
fn a_removed_block_is_dropped_only_for_the_task_the_question_names() {
    let dir = feature(Some(BEFORE), None);
    let mut all: serde_json::Map<String, Value> = blocks(BEFORE)
        .into_iter()
        .map(|(k, b, _)| (k, json!(block_digest(&b))))
        .collect();
    let plan = format!("{BEFORE}\n### T01 old notes\n\nx\n\n### T02 old notes\n\ny\n");
    std::fs::write(dir.join("plan.md"), &plan).unwrap();
    for (k, b, _) in blocks(&plan) {
        all.insert(k, json!(block_digest(&b)));
    }
    record_blocks(
        &dir,
        &json!({"blocks": all, "decisions": []}),
        "spec-fidelity",
        None,
    )
    .unwrap();
    std::fs::write(dir.join("plan.md"), BEFORE).unwrap();
    let trigger = "ask:243-T01-third-round";
    std::fs::write(
        dir.join("arbiter.jsonl"),
        format!(
            "{}\n",
            json!({"trigger": trigger, "ruling": "accept", "review": "plan"})
        ),
    )
    .unwrap();
    arbiter_accept(&dir, trigger, None).unwrap();
    let have = read(&dir)["blocks"].clone();
    assert!(have.get("### T01 old notes").is_none());
    assert!(have.get("### T02 old notes").is_some());
}

#[test]
fn a_task_only_a_heading_names_is_read_as_its_section_and_a_second_accept_keeps_the_reviewer_s() {
    // T03 has no heading of its own: its section is the first heading that names it, as `task_sections` reads it
    let plan = "# plan\n\n## About T03\n\n- shared by T03\n\n## Other\n\n- other\n";
    let dir = feature(Some(plan), None);
    let trigger = "ask:243-T03-third-round";
    std::fs::write(
        dir.join("arbiter.jsonl"),
        format!(
            "{}\n",
            json!({"trigger": trigger, "ruling": "accept", "review": "plan"})
        ),
    )
    .unwrap();
    let got = arbiter_accept(&dir, trigger, None).unwrap();
    assert_eq!(got.blocks, ["## About T03"]);
    assert_eq!(got.tasks, ["T03"]);
    assert!(read(&dir)["tasks"]["T03"].get("accepted_over").is_none());
    // an accept over the reviewer's BLOCKED, then a second accept: the reviewer's entry is carried forward, never the first accept's
    let (dir, _) = accepted_on("ask:243-T01-third-round", "plan");
    let again = "ask:243-T01-fourth-round";
    std::fs::write(
        dir.join("arbiter.jsonl"),
        format!(
            "{}\n",
            json!({"trigger": again, "ruling": "accept", "review": "plan"})
        ),
    )
    .unwrap();
    arbiter_accept(&dir, again, None).unwrap();
    let entry = &read(&dir)["tasks"]["T01"];
    assert_eq!(entry["decisions"][0]["id"], again);
    assert_eq!(entry["accepted_over"]["declared"], "spec-fidelity");
}
