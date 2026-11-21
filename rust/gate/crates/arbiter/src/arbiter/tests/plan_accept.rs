//! RED FIRST (feature 451 T92): `make arbiter-ruled` on one task's plan round names what it recorded - that task's blocks and its task
//! verdict, never the whole plan's 28 (`ask:451-T79-third-plan-round`, measured 2026-11-21) - and a batch's plan accept is applied too.

use serde_json::{json, Value};

use super::{clone_at, owe, python_tools, rule_file, run};

const PLAN: &str = "# p\n\n## Shared\n\nshared\n\n## T01 x\n\nbody\n\n## T02 y\n\nother\n";

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
