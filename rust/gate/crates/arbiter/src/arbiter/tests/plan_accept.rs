//! RED FIRST (feature 451 T92): `make arbiter-ruled` on one task's plan round names what it recorded - that task's blocks and its task
//! verdict, never the whole plan's 28 (`ask:451-T79-third-plan-round`, measured 2026-11-21) - and a batch's plan accept is applied too.

use serde_json::{json, Value};

use super::{clone_at, owe, python_tools, rule_file, run};

const PLAN: &str = "# p\n\n## Shared\n\nshared\n\n## T01 x\n\nbody\n\n## T02 y\n\nother\n";

/// The feature's tasks, so a plan round's trigger names a task of its feature (451 T179).
const TASKS: &str = "# Tasks\n\n- [ ] T01 x\n- [ ] T02 y\n";

fn review(root: &std::path::Path) -> Value {
    serde_json::from_str(
        &std::fs::read_to_string(root.join("specs/999-x/plan-review.json")).unwrap(),
    )
    .unwrap()
}

#[test]
fn an_accept_on_one_task_s_round_names_that_task_s_blocks_and_verdict() {
    let root = clone_at("plan-task");
    python_tools(&root);
    std::fs::write(root.join("specs/999-x/plan.md"), PLAN).unwrap();
    std::fs::write(root.join("specs/999-x/tasks.md"), TASKS).unwrap();
    owe(
        &root,
        &json!({"ask:999-T01-third-round": {"kind": "ask", "unit": "", "feature": "999-x", "t": 1, "review": "plan", "detail": "why"}}),
    );
    let accept = rule_file(&root, "a.json", &json!({"ruling": "accept", "why": "fine"}));
    let said = run(
        &root,
        &[
            "ruled",
            "ask:999-T01-third-round",
            &accept,
            "--as",
            "round-arbiter",
        ],
    );
    assert_eq!(said.code, 0, "{}", said.stderr);
    assert!(
        said.stdout.contains("1 plan block(s) of T01's section recorded CLEAR: ## T01 x; and T01's task verdict CLEAR"),
        "{}",
        said.stdout
    );
    let got = review(&root);
    assert_eq!(got["tasks"]["T01"]["declared"], "round-arbiter");
    assert!(got["blocks"].get("## T02 y").is_none() && got["blocks"].get("## Shared").is_none());
}

#[test]
fn a_batch_s_plan_accept_stands_as_that_review_s_verdict() {
    let root = clone_at("plan-batch");
    python_tools(&root);
    std::fs::write(root.join("specs/999-x/plan.md"), PLAN).unwrap();
    std::fs::write(root.join("specs/999-x/tasks.md"), TASKS).unwrap();
    owe(
        &root,
        &json!({
            "ask:999-T02-third-round": {"kind": "ask", "unit": "", "feature": "999-x", "t": 1, "review": "plan"},
            "ask:999-T05-gone": {"kind": "ask", "unit": "", "feature": "999-x", "t": 1, "review": "plan"},
        }),
    );
    std::fs::write(
        root.join("specs/999-x/plan-done.md"),
        "# done\n\n## T05 z\n\ndone\n",
    )
    .unwrap();
    std::fs::write(
        root.join("specs/999-x/tasks-done.md"),
        "# Done\n\n- [x] T05 z\n",
    )
    .unwrap();
    let batch = rule_file(
        &root,
        "b.json",
        &json!({"ruling": "accept", "why": "fine", "triggers": ["ask:999-T02-third-round", "ask:999-T05-gone"]}),
    );
    let said = run(&root, &["ruled-batch", &batch, "--as", "round-arbiter"]);
    assert_eq!(said.code, 0, "{}", said.stderr);
    assert!(
        said.stdout
            .contains("of T02's section recorded CLEAR: ## T02 y; and T02's task verdict"),
        "{}",
        said.stdout
    );
    assert!(
        said.stdout.contains("has no section in plan.md"),
        "{}",
        said.stdout
    );
    assert_eq!(review(&root)["tasks"]["T02"]["verdict"], "CLEAR");
}

/// 451 T462: a process-fault on the round of a section still the `make task-add` template records no verdict, and says so.
#[test]
fn a_process_fault_on_an_unwritten_section_s_round_records_no_verdict() {
    let root = clone_at("plan-stub");
    python_tools(&root);
    let [_, stub, ..] = crate::plan::template::stubs("T02");
    std::fs::write(root.join("specs/999-x/plan.md"), format!("# p\n\n{stub}")).unwrap();
    std::fs::write(root.join("specs/999-x/tasks.md"), TASKS).unwrap();
    let trigger = "round:spec-fidelity|plan:999-x#T02@3";
    owe(
        &root,
        &json!({trigger: {"kind": "round", "unit": "spec-fidelity|plan:999-x#T02", "feature": "999-x", "t": 1}}),
    );
    let fault = rule_file(
        &root,
        "f.json",
        &json!({"ruling": "process-fault", "why": "a blank stub", "tooling_fix": "the stub rides in no bundle", "fix_minutes": 15}),
    );
    let said = run(&root, &["ruled", trigger, &fault, "--as", "round-arbiter"]);
    assert_eq!(said.code, 0, "{}", said.stderr);
    let line =
        "arbiter-ruled: no verdict recorded - T02's section is still the `make task-add` template";
    assert!(said.stdout.contains(line), "{}", said.stdout);
    let path = root.join("specs/999-x/plan-review.json");
    assert!(
        !path.exists()
            || review(&root)
                .get("tasks")
                .is_none_or(|t| t.get("T02").is_none())
    );
}
