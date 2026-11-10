use std::path::Path;

use serde_json::{json, Value};

use super::{batch_refusal, blocked_text, close, escape_for, escaped, handle};
use crate::shared::checks::testkit::clone_at;
use crate::shared::checks::{load, save};

const MANIFEST: &str = "unit: quote-check:0105.drawing#bath abc\n";

fn setup(tag: &str) -> (std::path::PathBuf, std::path::PathBuf) {
    crate::shared::log::quiet();
    let root = clone_at(tag);
    let manifest = root.join("MANIFEST.md");
    std::fs::write(&manifest, MANIFEST).unwrap();
    (root, manifest)
}

fn agent(root: &Path, sub: &str, prompt: &str, tid: &str) -> Value {
    json!({"cwd": root, "tool_name": "Agent", "tool_use_id": tid, "tool_input": {"subagent_type": sub, "prompt": prompt}})
}

fn state(root: &Path) -> Value {
    load(&root.join(".git/checks-open.json"))
}

#[test]
fn a_check_round_goes_through_every_mode() {
    let (root, manifest) = setup("round");
    let prompt = format!("Read {}", manifest.display());
    assert_eq!(
        handle(
            "dispatch",
            &agent(&root, "quote-check", &prompt, "t1"),
            Some(1000.0)
        ),
        ""
    );
    assert_eq!(state(&root)["dispatches"]["t1"]["state"], json!("pending"));
    let launched = json!({"cwd": root, "tool_name": "Agent", "tool_use_id": "t1", "tool_input": {}, "tool_response": {"status": "async_launched", "agentId": "ag1"}});
    assert_eq!(handle("launched", &launched, Some(1000.0)), "");
    assert_eq!(state(&root)["dispatches"]["t1"]["state"], json!("running"));
    let page = json!({"cwd": root, "tool_name": "Edit", "tool_input": {"file_path": "research/questions/0105-x.html", "old_string": "a", "new_string": "b"}});
    assert!(handle("edit", &page, Some(1000.0)).contains("frozen while its checks run"));
    let escaped_edit = json!({"cwd": root, "tool_name": "Edit", "tool_input": {"file_path": "research/questions/0105-x.html", "old_string": "FREEZE_OK=\"a hand fix here\"", "new_string": "b"}});
    assert_eq!(handle("edit", &escaped_edit, Some(1000.0)), "");
    let other_tool = json!({"cwd": root, "tool_name": "Read", "tool_input": {"file_path": "x"}});
    assert_eq!(handle("edit", &other_tool, Some(1000.0)), "");
    let done = json!({"cwd": root, "agent_id": "ag1", "agent_type": "quote-check", "last_assistant_message": "q: 1\n\nEDIT research/questions/0105-x.html\n<<<\na\n===\nb\n>>>\n"});
    assert_eq!(handle("returned", &done, Some(1000.0)), "");
    assert_eq!(state(&root)["dispatches"]["t1"]["state"], json!("returned"));
    assert_eq!(handle("edit", &page, Some(1000.0)), "");
    assert_eq!(handle("unknown", &page, Some(1000.0)), "");
    let stop = json!({"cwd": root, "tool_name": "TaskStop", "tool_input": {"task_id": "ag9"}, "tool_response": {}});
    assert_eq!(
        handle(
            "dispatch",
            &agent(&root, "record-format", "no manifest", "t2"),
            Some(1000.0)
        ),
        ""
    );
    let mut s = state(&root);
    s["dispatches"]["t2"]["aid"] = json!("ag9");
    s["dispatches"]["t2"]["state"] = json!("running");
    save(&root.join(".git/checks-open.json"), &s).unwrap();
    assert_eq!(handle("launched", &stop, Some(1000.0)), "");
    assert_eq!(
        state(&root)["dispatches"]["t2"]["closed"],
        json!("stopped by the session (TaskStop)")
    );
    let shell = json!({"cwd": root, "tool_name": "TaskStop", "tool_input": {"shell_id": "ag8"}, "tool_response": {}});
    assert_eq!(handle("launched", &shell, Some(1000.0)), "");
    assert_eq!(
        handle(
            "dispatch",
            &json!({"cwd": root, "tool_name": "Bash"}),
            Some(1000.0)
        ),
        ""
    );
    assert_eq!(
        handle(
            "launched",
            &json!({"cwd": root, "tool_name": "Bash"}),
            Some(1000.0)
        ),
        ""
    );
    assert_eq!(
        handle(
            "dispatch",
            &json!({"cwd": "/nonexistent-l7r", "tool_name": "Agent"}),
            Some(1.0)
        ),
        ""
    );
    assert_eq!(handle("edit", &json!({}), None), "");
}

#[test]
fn a_new_feature_resets_the_counts_but_not_the_dispatches() {
    let (root, _) = setup("feature");
    save(
        &root.join(".git/checks-open.json"),
        &json!({"feature": "000-old", "rounds": {"x": 9}, "dispatches": {"a": {}}}),
    )
    .unwrap();
    assert_eq!(
        handle(
            "dispatch",
            &agent(&root, "quote-check", "plain", "tx"),
            Some(1000.0)
        ),
        ""
    );
    let s = state(&root);
    assert_eq!(s["feature"], json!("999-x"));
    assert!(s.get("rounds").is_none());
    assert!(s["dispatches"].get("a").is_some() && s["dispatches"].get("tx").is_some());
}

#[test]
fn escapes_and_their_rules() {
    let (root, manifest) = setup("escapes");
    assert!(!escaped("X_OK", "no token"));
    assert!(!escaped("X_OK", "X_OK=\"short\""));
    assert!(!escaped("X_OK", "X_OK=\"oneword-long-enough\""));
    assert!(escaped("X_OK", "X_OK=\"two words enough\""));
    assert_eq!(escape_for("a, batched"), "BATCH_OK");
    assert_eq!(escape_for("the arbiter said"), "ARBITER_OK");
    assert_eq!(escape_for("a freeze"), "FREEZE_OK");
    assert!(blocked_text("the arbiter").ends_with("(scripts/hooks/lib/hm_checks.py; escape ARBITER_OK=\"<reason>\" in the prompt or the edit)\n"));
    let prompt = format!("Read {} BATCH_OK=\"a single pop-up here\" FREEZE_OK=\"a hand fix here\" ARBITER_OK=\"the arbiter ruled it\"", manifest.display());
    assert_eq!(
        handle(
            "dispatch",
            &agent(&root, "record-format", &prompt, "t3"),
            Some(1000.0)
        ),
        ""
    );
    let wave = format!("Read {}", manifest.display());
    assert_eq!(
        handle(
            "dispatch",
            &agent(&root, "quote-check", &wave, "wave:1"),
            Some(1000.0)
        ),
        ""
    );
    assert!(state(&root)["dispatches"]["wave:1"].get("wave").is_some());
}

#[test]
fn the_round_arbiter_and_budget_and_plan_holds_are_handled() {
    let (root, _) = setup("branches");
    std::fs::write(
        root.join("specs/999-x/arbiter.jsonl"),
        "{\"trigger\": \"ask:done\", \"ruling\": \"accept\"}\n",
    )
    .unwrap();
    let bundle = root.join("arb-MANIFEST.md");
    std::fs::write(&bundle, "trigger: ask:done\n").unwrap();
    let said = handle(
        "dispatch",
        &agent(
            &root,
            "round-arbiter",
            &format!("Read {}", bundle.display()),
            "r",
        ),
        Some(1.0),
    );
    assert!(said.contains("already ruled"), "{said}");
    std::fs::write(&bundle, "trigger: ask:other\n").unwrap();
    assert_eq!(
        handle(
            "dispatch",
            &agent(
                &root,
                "round-arbiter",
                &format!("Read {}", bundle.display()),
                "r"
            ),
            Some(1.0)
        ),
        ""
    );
    assert_eq!(
        handle(
            "dispatch",
            &agent(&root, "round-arbiter", "no manifest", "r"),
            Some(1.0)
        ),
        ""
    );
    assert_eq!(
        handle(
            "dispatch",
            &agent(&root, "work-budget", "no stage here", "w"),
            Some(1.0)
        ),
        ""
    );
    assert_eq!(
        handle(
            "dispatch",
            &agent(&root, "settlement-review", "x", "v"),
            Some(1.0)
        ),
        ""
    );
    let phases = root.join("specs/999-x/phases");
    std::fs::create_dir_all(&phases).unwrap();
    for v in 1..=2 {
        std::fs::write(phases.join(format!("field.verdict-{v}.txt")), "x").unwrap();
    }
    let budget = "Read /tmp/l7r-check/work-budget-budget-field/MANIFEST.md";
    assert!(handle(
        "dispatch",
        &agent(&root, "work-budget", budget, "w"),
        Some(1.0)
    )
    .contains("passes its cap"));
    assert_eq!(
        handle(
            "dispatch",
            &agent(
                &root,
                "work-budget",
                &format!("{budget} ARBITER_OK=\"the arbiter ruled it\""),
                "w"
            ),
            Some(1.0)
        ),
        ""
    );
    let plan_bundle = root.join("plan-900-a-T01");
    std::fs::create_dir_all(&plan_bundle).unwrap();
    let prompt = format!("Review {}/MANIFEST.md", plan_bundle.display());
    assert_eq!(
        handle(
            "dispatch",
            &agent(&root, "spec-fidelity", &prompt, "h"),
            Some(1000.0)
        ),
        ""
    );
    assert_eq!(state(&root)["plan_holds"]["h"]["state"], json!("pending"));
    assert_eq!(
        handle(
            "dispatch",
            &agent(&root, "spec-fidelity", "no bundle", ""),
            Some(1000.0)
        ),
        ""
    );
    std::fs::create_dir_all(root.join("specs/900-a")).unwrap();
    std::fs::write(
        root.join("specs/900-a/plan.md"),
        "# p\n\n## T01 x\n\nbody long enough to hold\n",
    )
    .unwrap();
    let launched = json!({"cwd": root, "tool_name": "Agent", "tool_use_id": "h", "tool_input": {}, "tool_response": {"status": "async_launched", "agentId": "agh"}});
    assert_eq!(handle("launched", &launched, Some(1000.0)), "");
    let mut s = state(&root);
    s["plan_holds"]["h"]["t"] = json!(1000.0);
    save(&root.join(".git/checks-open.json"), &s).unwrap();
    let edit = json!({"cwd": root, "tool_name": "Edit", "tool_use_id": "e1", "tool_input": {"file_path": root.join("specs/900-a/plan.md"), "old_string": "body long", "new_string": "z"}});
    let held = handle("edit", &edit, Some(1000.0));
    assert!(held.contains("plan review"), "{held}");
    assert!(state(&root)["plan_snaps"].get("e1").is_some());
    std::fs::write(
        root.join("specs/900-a/plan.md"),
        "# p\n\n## T01 x\n\nchanged\n",
    )
    .unwrap();
    let after = json!({"cwd": root, "tool_name": "Edit", "tool_use_id": "e1", "tool_input": {}});
    let msg = handle("after", &after, Some(1000.0));
    assert!(msg.contains("written back"), "{msg}");
    assert!(std::fs::read_to_string(root.join(".git/tool-usage.jsonl"))
        .unwrap()
        .contains("planhold-restore"));
    let edit2 = json!({"cwd": root, "tool_name": "Bash", "tool_use_id": "e2", "tool_input": {"command": "PLAN_EDIT_OK=\"a dead hold here\" ls"}});
    assert_eq!(handle("edit", &edit2, Some(1000.0)), "");
    let empty_after = handle(
        "after",
        &json!({"cwd": root, "tool_name": "Bash", "tool_use_id": "e2"}),
        Some(1000.0),
    );
    assert_eq!(empty_after, "");
}

#[test]
fn the_gate_held_and_apply_edits_are_refused_for_a_bash_call() {
    let (root, _) = setup("bash");
    std::fs::write(
        root.join(".git/arbiter-owed.json"),
        json!({"red-gate@t": {"kind": "red-gate", "feature": "999-x"}}).to_string(),
    )
    .unwrap();
    let bash =
        |cmd: &str| json!({"cwd": root, "tool_name": "Bash", "tool_input": {"command": cmd}});
    assert!(handle("edit", &bash("make done"), Some(1.0)).contains("red-gate@t"));
    assert_eq!(
        handle(
            "edit",
            &bash("ARBITER_OK=\"the arbiter ruled it\" make done"),
            Some(1.0)
        ),
        ""
    );
    assert_eq!(handle("edit", &bash("make quick"), Some(1.0)), "");
    assert_eq!(
        handle(
            "edit",
            &bash("FREEZE_OK=\"a hand fix\" make quick"),
            Some(1.0)
        ),
        ""
    );
    assert_eq!(
        handle(
            "edit",
            &json!({"cwd": "/", "tool_name": "Bash", "tool_input": {"command": "make done"}}),
            Some(1.0)
        ),
        ""
    );
}

#[test]
fn a_cascade_and_a_reversal_owe_the_arbiter() {
    let (root, manifest) = setup("cascade");
    std::fs::create_dir_all(root.join("research/questions")).unwrap();
    let page = root.join("research/questions/0105-x.html");
    let prompt = format!("Read {}", manifest.display());
    for (i, body) in [
        "<p>the first block about a bath and its water</p>",
        "<p>another block entirely different words appear here now</p>",
        "<p>the first block about a bath and its water</p>",
    ]
    .iter()
    .enumerate()
    {
        std::fs::write(&page, body).unwrap();
        let said = handle(
            "dispatch",
            &agent(&root, "quote-check", &prompt, &format!("v{i}")),
            Some(1000.0),
        );
        assert_eq!(said.contains("reversal:q:0105@3"), i == 2, "{said}");
    }
    let owed: Value = serde_json::from_str(
        &std::fs::read_to_string(root.join(".git/arbiter-owed.json")).unwrap(),
    )
    .unwrap();
    assert!(
        owed.as_object()
            .unwrap()
            .keys()
            .any(|k| k.starts_with("reversal:q:0105@")),
        "{owed}"
    );
    std::fs::remove_file(root.join(".git/arbiter-owed.json")).unwrap();
    let many: serde_json::Map<String, Value> = (0..20)
        .map(|i| (format!("k{i}"), json!({"t": 2000.0, "check": "c"})))
        .collect();
    save(
        &root.join(".git/checks-open.json"),
        &json!({"feature": "999-x", "dispatches": many}),
    )
    .unwrap();
    assert_eq!(
        handle(
            "dispatch",
            &agent(&root, "quote-check", &prompt, "c9"),
            Some(2000.0)
        ),
        ""
    );
    assert!(std::fs::read_to_string(root.join(".git/arbiter-owed.json"))
        .unwrap()
        .contains("cascade@1"));
}

#[test]
fn a_popup_batch_refuses_one_agent_on_one_popup() {
    let root = clone_at("batch");
    let unit = "unit: modal-form:sheet/bath fp\n";
    assert_eq!(batch_refusal(None, "modal-form", unit, 1.0), None);
    assert_eq!(batch_refusal(Some(&root), "quote-check", unit, 1.0), None);
    assert_eq!(
        batch_refusal(Some(&root), "modal-form", "no unit", 1.0),
        None
    );
    assert_eq!(batch_refusal(Some(&root), "modal-form", unit, 1.0), None);
    let write = |utc: f64, kinds: &[&str]| {
        std::fs::write(
            root.join(".git/modal-batches.json"),
            json!({"utc": utc, "batches": {"modal-form": kinds}}).to_string(),
        )
        .unwrap()
    };
    write(1.0, &["sheet/bath", "sheet/well"]);
    let msg = batch_refusal(Some(&root), "modal-form", unit, 100.0).unwrap();
    assert!(
        msg.ends_with(", batched") && msg.contains("KIND=\"sheet/bath sheet/well\""),
        "{msg}"
    );
    assert_eq!(
        batch_refusal(Some(&root), "modal-form", unit, 100_000.0),
        None
    );
    write(1.0, &["sheet/bath"]);
    assert_eq!(batch_refusal(Some(&root), "modal-form", unit, 100.0), None);
    write(1.0, &["sheet/other", "sheet/x"]);
    assert_eq!(batch_refusal(Some(&root), "modal-form", unit, 100.0), None);
}

#[test]
fn check_closed_needs_a_reason_and_saves_what_it_closed() {
    let (root, _) = setup("close");
    assert_eq!(close(&root, "s", "x", 1.0, "").0, 2);
    let (code, out, _) = close(&root, "s", "nothing to close here", 1.0, "");
    assert_eq!(code, 0);
    assert!(out.contains("0 silent dispatch(es) on s"));
    let path = root.join(".git/checks-open.json");
    save(&path, &json!({"dispatches": {"a": {"check": "c", "subjects": ["s"], "state": "running", "t": 1000.0, "aid": "ag"}}})).unwrap();
    let (_, out, _) = close(&root, "s", "the session stopped it", 1000.0, "ag");
    assert!(out.contains("1 silent dispatch(es)") && !out.contains("still running"));
    assert_eq!(
        load(&path)["dispatches"]["a"]["closed"],
        json!("the session stopped it")
    );
    save(&path, &json!({"dispatches": {"a": {"check": "c", "subjects": ["s"], "state": "running", "t": 1000.0}}})).unwrap();
    let (_, out, _) = close(&root, "s", "the session stopped it", 1000.0, "");
    assert!(
        out.contains("; 1 still running and not silent: wait for them"),
        "{out}"
    );
    let (code, ..) = close(
        Path::new("/nonexistent-l7r"),
        "s",
        "nothing here to close",
        1.0,
        "",
    );
    assert_eq!(code, 0);
}
