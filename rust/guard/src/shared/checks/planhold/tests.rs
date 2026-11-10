use std::path::Path;

use serde_json::{json, Value};

use super::{hold, launched, live, purge, refusal, restore, returned, snapshot};
use crate::shared::checks::testkit::{clone_at, dir};

const PLAN: &str = "# plan\n\n## T01 the bath\n\nheld body of the section stands here\n\n## T02 other\n\nother text\n";

fn feature(root: &Path) {
    std::fs::create_dir_all(root.join("specs/900-a")).unwrap();
    std::fs::write(root.join("specs/900-a/plan.md"), PLAN).unwrap();
}

fn running(task: &str, blocks: &[&str], t: f64) -> Value {
    json!({"feature": "900-a", "task": task, "blocks": blocks, "t": t, "state": "running", "aid": "ag"})
}

#[test]
fn a_dispatch_takes_a_hold() {
    let d = dir("hold");
    let bundle = d.join("plan-900-a-T01");
    std::fs::create_dir_all(&bundle).unwrap();
    let mut state = json!({});
    hold(&mut state, "t0", "no bundle", 1.0);
    assert_eq!(state, json!({}));
    hold(
        &mut state,
        "t1",
        &format!("Read {}/MANIFEST.md", bundle.display()),
        1.5,
    );
    assert_eq!(
        state["plan_holds"]["t1"],
        json!({"feature": "900-a", "task": "T01", "blocks": [], "t": 1.5, "state": "pending"})
    );
    let blocks = d.join("plan-900-a-blocks-x");
    std::fs::create_dir_all(&blocks).unwrap();
    std::fs::write(blocks.join("blocks.md"), "<!-- block \"## A \\\"q\\\"\" sha256\nnot one\n<!-- block \"k\\\\z\\n\\t\\r\\a\\b\\f\\v\\'\\q\u{e9}\" sha256\n").unwrap();
    hold(
        &mut state,
        "t2",
        &format!("x {}/MANIFEST.md y", blocks.display()),
        2.0,
    );
    assert_eq!(
        state["plan_holds"]["t2"]["blocks"],
        json!([
            "## A \"q\"",
            "k\\z\n\t\r\u{7}\u{8}\u{c}\u{b}'\\q\u{c3}\u{a9}"
        ])
    );
    hold(
        &mut state,
        "t3",
        &format!("{}-gone/plan-900-a-blocks-y/MANIFEST.md", d.display()),
        2.0,
    );
    assert_eq!(state["plan_holds"]["t3"]["blocks"], json!([]));
    launched(&mut state, "t1", "ag1");
    launched(&mut state, "nope", "ag1");
    launched(&mut json!({}), "x", "y");
    assert_eq!(state["plan_holds"]["t1"]["state"], json!("running"));
    returned(&mut state, "ag1");
    returned(&mut json!({}), "ag1");
    assert!(state["plan_holds"].get("t1").is_none());
}

#[test]
fn a_hold_is_live_or_dead_by_its_age() {
    assert!(live(&running("T01", &[], 100.0), 1000.0));
    assert!(!live(&running("T01", &[], 0.0), 5000.0));
    assert!(!live(&json!({"state": "pending", "t": 0.0}), 10.0));
    let mut state = json!({"plan_holds": {"a": {"state": "pending", "t": 0.0}, "b": {"state": "pending", "t": 950.0}, "c": {"state": "running", "t": 0.0}}});
    purge(&mut state, 1000.0);
    let keys: Vec<&String> = state["plan_holds"].as_object().unwrap().keys().collect();
    assert_eq!(keys, ["b", "c"]);
    purge(&mut json!({}), 1.0);
}

#[test]
fn a_snapshot_is_written_back_when_held_text_changes() {
    let root = clone_at("restore");
    feature(&root);
    let mut state = json!({"plan_holds": {"h1": running("T01", &[], 900.0), "dead": running("T01", &[], 0.0), "p": {"feature": "x", "state": "pending", "t": 999.0}}});
    snapshot(&mut state, None, "call", 1000.0);
    assert!(state.get("plan_snaps").is_none());
    snapshot(&mut state, Some(&root), "call", 1000.0);
    assert!(state["plan_snaps"]["call"]["h1"][0]
        .as_str()
        .unwrap()
        .contains("held body"));
    assert_eq!(state["plan_holds"].as_object().unwrap().len(), 3);
    snapshot(&mut state, Some(&root), "empty", 100_000.0);
    assert!(state["plan_snaps"].get("empty").is_none());
    assert_eq!(restore(&mut state, Some(&root), "unrelated"), "");
    let unchanged = restore(&mut state, Some(&root), "call");
    assert_eq!(unchanged, "");
    assert!(state.get("plan_snaps").is_none());
    snapshot(&mut state, Some(&root), "again", 1000.0);
    std::fs::write(
        root.join("specs/900-a/plan.md"),
        PLAN.replace("held body", "CHANGED body"),
    )
    .unwrap();
    let msg = restore(&mut state, Some(&root), "again");
    assert!(msg.contains("T01's section of specs/900-a/plan.md") && msg.contains("(agent ag)"));
    assert!(std::fs::read_to_string(root.join("specs/900-a/plan.md"))
        .unwrap()
        .contains("held body"));
    let mut none = json!({"plan_snaps": {"x": {"gone": ["a"]}}, "plan_holds": {"h1": running("T01", &[], 1.0)}});
    assert_eq!(restore(&mut none, None, "x"), "");
    assert!(none.get("plan_snaps").is_none());
    let mut other_snap = json!({"plan_snaps": {"keep": {"h1": []}, "drop": {"gone": []}}, "plan_holds": {"h1": running("T01", &[], 1.0)}});
    restore(&mut other_snap, None, "absent");
    assert!(
        other_snap["plan_snaps"].get("keep").is_some()
            && other_snap["plan_snaps"].get("drop").is_none()
    );
    assert_eq!(restore(&mut json!({}), Some(&root), "x"), "");
    let mut gone_hold = json!({"plan_snaps": {"x": {"gone": ["a"]}}});
    assert_eq!(restore(&mut gone_hold, Some(&root), "x"), "");
}

#[test]
fn a_held_block_is_written_back() {
    let root = clone_at("blocks");
    feature(&root);
    let mut state =
        json!({"plan_holds": {"h": running("", &["## T01 the bath", "## T02 other"], 900.0)}});
    snapshot(&mut state, Some(&root), "c", 1000.0);
    let edited = PLAN
        .replace("held body", "X body")
        .replace("other text", "Y text");
    std::fs::write(root.join("specs/900-a/plan.md"), &edited).unwrap();
    let msg = restore(&mut state, Some(&root), "c");
    assert!(msg.contains("2 block(s) of specs/900-a/plan.md"));
    assert_eq!(
        std::fs::read_to_string(root.join("specs/900-a/plan.md")).unwrap(),
        PLAN
    );
    let mut one_same =
        json!({"plan_holds": {"h": running("", &["## T01 the bath", "## T02 other"], 900.0)}});
    snapshot(&mut one_same, Some(&root), "c", 1000.0);
    std::fs::write(
        root.join("specs/900-a/plan.md"),
        PLAN.replace("other text", "Y text"),
    )
    .unwrap();
    assert!(!restore(&mut one_same, Some(&root), "c").is_empty());
    assert_eq!(
        std::fs::read_to_string(root.join("specs/900-a/plan.md")).unwrap(),
        PLAN
    );
    let mut missing_plan = json!({"plan_holds": {"h": {"feature": "no", "task": "T01", "t": 1.0, "state": "running"}}, "plan_snaps": {"c": {"h": ["old"]}}});
    assert_eq!(restore(&mut missing_plan, Some(&root), "c"), "");
    let mut gone_task =
        json!({"plan_holds": {"h": running("T09", &[], 1.0)}, "plan_snaps": {"c": {"h": ["old"]}}});
    let msg = restore(&mut gone_task, Some(&root), "c");
    assert!(msg.contains("T09's section"));
    let mut empty_before =
        json!({"plan_holds": {"h": running("T01", &[], 1.0)}, "plan_snaps": {"c": {"h": []}}});
    assert!(restore(&mut empty_before, Some(&root), "c").contains("T01's section"));
    assert_eq!(
        std::fs::read_to_string(root.join("specs/900-a/plan.md")).unwrap(),
        PLAN
    );
}

#[test]
#[expect(
    clippy::too_many_lines,
    reason = "one hold walked through every way a write can reach it"
)]
fn a_write_to_held_text_is_refused() {
    let root = clone_at("refusal");
    feature(&root);
    let plan = root
        .join("specs/900-a/plan.md")
        .to_string_lossy()
        .into_owned();
    let state = json!({"plan_holds": {"h": running("T01", &[], 900.0)}});
    let check = |tool: &str, ti: Value, escaped: bool, at: f64| {
        refusal(&state, Some(&root), tool, &ti, at, escaped)
    };
    assert_eq!(refusal(&state, None, "Edit", &json!({}), 1.0, false), "");
    assert!(check(
        "Edit",
        json!({"file_path": plan, "old_string": "held body"}),
        false,
        1000.0
    )
    .contains("(agent ag)"));
    assert!(check(
        "Edit",
        json!({"file_path": plan, "old_string": "body of the"}),
        false,
        1000.0
    )
    .contains("running"));
    assert_eq!(
        check(
            "Edit",
            json!({"file_path": plan, "old_string": "other text"}),
            false,
            1000.0
        ),
        ""
    );
    assert_eq!(
        check(
            "Edit",
            json!({"file_path": plan, "old_string": ""}),
            false,
            1000.0
        ),
        ""
    );
    assert_eq!(
        check(
            "Edit",
            json!({"file_path": "/elsewhere", "old_string": "held body"}),
            false,
            1000.0
        ),
        ""
    );
    let writes = check(
        "Write",
        json!({"file_path": plan, "content": "new"}),
        false,
        1000.0,
    );
    assert!(writes.contains("T01's section"));
    let keep = format!("x{PLAN}");
    assert_eq!(
        check(
            "Write",
            json!({"file_path": plan, "content": keep}),
            false,
            1000.0
        ),
        ""
    );
    assert!(check(
        "MultiEdit",
        json!({"file_path": plan, "old_string": "held body"}),
        false,
        1000.0
    )
    .contains("running"));
    assert_eq!(check("Bash", json!({"command": "ls"}), false, 1000.0), "");
    assert_eq!(
        check(
            "Bash",
            json!({"command": "sed -i s/a/b/ specs/900-a/plan.md"}),
            false,
            1000.0
        ),
        ""
    );
    assert!(check(
        "Bash",
        json!({"command": "sed -i 's/## T01 the bath/x/' specs/900-a/plan.md"}),
        false,
        1000.0
    )
    .contains("running"));
    assert!(check(
        "Bash",
        json!({"command": "tee specs/900-a/plan.md # held body of the section stands here"}),
        false,
        1000.0
    )
    .contains("running"));
    assert!(check("Bash", json!({"command": "python3 -c 'open(\"x\", \"w\")' specs/900-a/plan.md \"held body of the\""}), false, 1000.0).contains("running"));
    assert_eq!(check("Read", json!({"file_path": plan}), false, 1000.0), "");
    let late = check(
        "Edit",
        json!({"file_path": plan, "old_string": "held body"}),
        false,
        3000.0,
    );
    assert!(late.contains("its dispatch looks dead"));
    assert_eq!(
        check(
            "Edit",
            json!({"file_path": plan, "old_string": "held body"}),
            true,
            3000.0
        ),
        ""
    );
    assert!(check(
        "Edit",
        json!({"file_path": plan, "old_string": "held body"}),
        true,
        1000.0
    )
    .contains("running"));
    let pending = json!({"plan_holds": {"h": {"feature": "900-a", "task": "T01", "t": 999.0, "state": "pending"}}});
    let said = refusal(
        &pending,
        Some(&root),
        "Edit",
        &json!({"file_path": plan, "old_string": "held body"}),
        1000.0,
        false,
    );
    assert!(said.contains("a dispatch not yet launched"));
    let never = json!({"plan_holds": {"h": {"feature": "900-a", "task": "T01", "t": 0.0, "state": "pending"}}});
    assert_eq!(
        refusal(
            &never,
            Some(&root),
            "Edit",
            &json!({"file_path": plan, "old_string": "held body"}),
            1000.0,
            false
        ),
        ""
    );
    let empty_block = json!({"plan_holds": {"h": {"feature": "900-a", "blocks": ["## nope"], "t": 999.0, "state": "running"}}});
    assert_eq!(
        refusal(
            &empty_block,
            Some(&root),
            "Edit",
            &json!({"file_path": plan, "old_string": "held body"}),
            1000.0,
            false
        ),
        ""
    );
    let block = json!({"plan_holds": {"h": running("", &["## T01 the bath"], 999.0)}});
    assert!(refusal(
        &block,
        Some(&root),
        "Edit",
        &json!({"file_path": plan, "old_string": "held body"}),
        1000.0,
        false
    )
    .contains("1 block(s)"));
    assert_eq!(
        refusal(&json!({}), Some(&root), "Edit", &json!({}), 1.0, false),
        ""
    );
}
