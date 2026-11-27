use std::path::Path;

use serde_json::{json, Value};

use super::{batch_refusal, blocked_text, close, escape_for, escaped, handle};
use crate::checks::testkit::clone_at;
use crate::checks::{load, save};

const MANIFEST: &str = "unit: quote-check:0105.drawing#bath abc\n";

fn setup(tag: &str) -> (crate::tempdir::Held<std::path::PathBuf>, std::path::PathBuf) {
    crate::log::quiet();
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
    assert_eq!(
        handle(
            "launched",
            &json!({"cwd": root, "tool_name": "Agent", "tool_response": 3}),
            Some(1.0)
        ),
        ""
    );
    let write = json!({"cwd": root, "tool_name": "Write", "tool_input": {"file_path": "research/questions/0105-x.html", "content": "b"}});
    assert!(handle("edit", &write, Some(1000.0)).contains("none of the 1 edit(s)"));
    let worktree = clone_at("wt-owner");
    let common = worktree.join("x.git");
    std::fs::create_dir_all(common.join("worktrees/w")).unwrap();
    std::fs::write(common.join("worktrees/w/commondir"), "../..\n").unwrap();
    let wt = worktree.join("wt");
    std::fs::create_dir_all(&wt).unwrap();
    std::fs::write(
        wt.join(".git"),
        format!("gitdir: {}\n", common.join("worktrees/w").display()),
    )
    .unwrap();
    assert_eq!(
        handle(
            "dispatch",
            &json!({"cwd": wt, "tool_name": "Agent", "tool_input": {"subagent_type": "quote-check", "prompt": "plain"}}),
            Some(1.0)
        ),
        ""
    );
    assert_eq!(load(&common.join("checks-open.json"))["feature"], json!(""));
}

#[test]
fn a_new_feature_keeps_the_counts_their_home_and_the_dispatches() {
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
    // a count follows its unit (451 T227)
    assert_eq!(s["rounds"]["x"], json!(9));
    assert_eq!(s["round_home"]["x"], json!("000-old"));
    assert!(s["dispatches"].get("a").is_some() && s["dispatches"].get("tx").is_some());
}

#[test]
fn escapes_and_their_rules() {
    let (root, manifest) = setup("escapes");
    let modal = root.join("mm/MANIFEST.md");
    std::fs::create_dir_all(modal.parent().unwrap()).unwrap();
    std::fs::write(&modal, "unit: modal-form:sheet/bath fp\n").unwrap();
    let kinds = json!({"utc": 1.0, "batches": {"modal-form": ["sheet/bath", "sheet/well"]}});
    std::fs::write(root.join(".git/modal-batches.json"), kinds.to_string()).unwrap();
    let batched = handle(
        "dispatch",
        &agent(
            &root,
            "modal-form",
            &format!("Read {}", modal.display()),
            "mf",
        ),
        Some(10.0),
    );
    assert!(batched.ends_with(", batched"));
    assert!(!escaped("X_OK", "no token"));
    assert!(!escaped("X_OK", "X_OK=\"short\""));
    assert!(!escaped("X_OK", "X_OK=\"oneword-long-enough\""));
    assert!(escaped("X_OK", "X_OK=\"two words enough\""));
    assert_eq!(escape_for("a, batched"), "BATCH_OK");
    assert_eq!(escape_for("the arbiter said"), "ARBITER_OK");
    assert_eq!(escape_for("a freeze"), "FREEZE_OK");
    assert!(blocked_text("the arbiter")
        .ends_with("\n(escape ARBITER_OK=\"<reason>\" in the prompt or the edit)\n"));
    let named = blocked_text("the arbiter, or ARBITER_OK=\"<reason>\" - logged");
    assert_eq!(
        named,
        "BLOCKED: the arbiter, or ARBITER_OK=\"<reason>\" - logged\n"
    );
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
#[expect(
    clippy::too_many_lines,
    reason = "one clone walked through every branch of a dispatch"
)]
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
    assert!(said.contains("already ruled"));
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
    assert!(held.contains("plan review"));
    assert!(state(&root)["plan_snaps"].get("e1").is_some());
    std::fs::write(
        root.join("specs/900-a/plan.md"),
        "# p\n\n## T01 x\n\nchanged\n",
    )
    .unwrap();
    let after = json!({"cwd": root, "tool_name": "Edit", "tool_use_id": "e1", "tool_input": {}});
    let msg = handle("after", &after, Some(1000.0));
    assert!(msg.contains("written back"));
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
        assert_eq!(said.contains("reversal:q:0105@3"), i == 2);
    }
    let owed: Value = serde_json::from_str(
        &std::fs::read_to_string(root.join(".git/arbiter-owed.json")).unwrap(),
    )
    .unwrap();
    assert!(owed
        .as_object()
        .unwrap()
        .keys()
        .any(|k| k.starts_with("reversal:q:0105@")));
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
        .unwrap();
    };
    write(1.0, &["sheet/bath", "sheet/well"]);
    let msg = batch_refusal(Some(&root), "modal-form", unit, 100.0).unwrap();
    assert!(msg.ends_with(", batched") && msg.contains("KIND=\"sheet/bath sheet/well\""));
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
    assert!(out.contains("; 1 still running and not silent: wait for them"));
    let (code, ..) = close(
        Path::new("/nonexistent-l7r"),
        "s",
        "nothing here to close",
        1.0,
        "",
    );
    assert_eq!(code, 0);
}

/// `f`'s answer, or a failure once it runs past 20 s (feature 449 T185: a quadratic search, or a scan over an error it repeats, must
/// fail the test rather than hang it).
fn within<T: Send + 'static>(f: impl FnOnce() -> T + Send + 'static) -> T {
    let (tx, rx) = std::sync::mpsc::channel();
    let _run = std::thread::spawn(move || tx.send(f()));
    rx.recv_timeout(std::time::Duration::from_secs(20))
        .expect("the search ran past its bound")
}

/// A `make done` past a million steps of command (feature 449 T185): `MAKE_DONE` erred at `fancy_regex`'s old limit and read as no
/// gate run, so the arbiter's hold was not asked.
#[test]
fn a_make_done_past_a_million_steps_is_seen() {
    let command = format!(
        "{}\nmake done",
        "plain words of a long text ".repeat(50_000)
    );
    assert_eq!(
        within(move || Some(crate::make::invoked(&command).iter().any(|t| t == "done"))),
        Some(true)
    );
}

/// A plan review's dispatch records the tree its call ran in, a directory inside it read as the tree's root: the one tree its hold's
/// write-back runs in (451 T123).
#[test]
fn a_dispatch_records_the_tree_its_hold_is_taken_in() {
    let (root, _) = setup("dispatch-root");
    let bundle = root.join("plan-900-a-T01");
    std::fs::create_dir_all(&bundle).unwrap();
    let prompt = format!("Read {}/MANIFEST.md", bundle.display());
    let said = handle(
        "dispatch",
        &agent(&root.join("specs"), "spec-fidelity", &prompt, "d"),
        Some(1.0),
    );
    let recorded = state(&root)["plan_holds"]["d"]["root"].clone();
    let rooted = said.is_empty() && recorded == json!(root.to_string_lossy());
    assert!(rooted, "{said} {recorded}");
}

/// The footnote hold's trip outlives the refusal that made it (ruling `ask:454-c1b-fixloop-retrip`): a refused dispatch saves the
/// trigger, so the next dispatch names the SAME trigger, and once that trigger is ruled the dispatch goes through.
/// `GUARD_EDIT_OK`: the test of a fix to a guard that fired on correct work.
#[test]
fn a_refused_dispatch_keeps_the_footnote_holds_trip() {
    let (root, manifest) = setup("fixloop-kept");
    std::fs::write(&manifest, "unit: quote-check:0105#bath newfp\n").unwrap();
    let path = root.join(".git/checks-open.json");
    let flagged = json!({"feature": "999-x", "rounds": {}, "flags": {"0105#bath": {"n": 2, "fp": "old", "lines": ["L1", "L2"]}}});
    save(&path, &flagged).unwrap();
    let ask = |tid: &str| {
        handle(
            "dispatch",
            &agent(
                &root,
                "quote-check",
                &format!("Read {}", manifest.display()),
                tid,
            ),
            Some(1.0),
        )
    };
    let first = ask("q1");
    assert!(first.contains("round:quote-check|q:0105@3"), "{first}");
    assert_eq!(
        state(&root)["flag_trips"]["0105#bath"],
        json!("round:quote-check|q:0105@3")
    );
    let second = ask("q2");
    assert!(second.contains("round:quote-check|q:0105@3"));
    assert!(!second.contains("@4"));
    std::fs::write(
        root.join("specs/999-x/arbiter.jsonl"),
        "{\"trigger\": \"round:quote-check|q:0105@3\", \"ruling\": \"continue\"}\n",
    )
    .unwrap();
    assert_eq!(ask("q3"), "");
    assert!(state(&root)["flag_trips"].get("0105#bath").is_none());
}

/// One record-format round on 0097 through the hook's three events, its reply `reply`.
fn record_round(root: &Path, prompt: &str, tid: &str, at: f64) -> String {
    let said = handle(
        "dispatch",
        &agent(root, "record-format", prompt, tid),
        Some(at),
    );
    if said.is_empty() {
        let aid = format!("ag-{tid}");
        let launched = json!({"cwd": root, "tool_name": "Agent", "tool_use_id": tid, "tool_input": {}, "tool_response": {"status": "async_launched", "agentId": aid}});
        assert_eq!(handle("launched", &launched, Some(at)), "");
        let done = json!({"cwd": root, "agent_id": aid, "agent_type": "record-format", "last_assistant_message": "record-format: 0097 - 1 finding"});
        assert_eq!(handle("returned", &done, Some(at)), "");
    }
    said
}

#[test]
fn a_record_round_follows_its_unit_across_features() {
    // 451 T227's first case, 2026-11-24: record-format was dispatched on 0097 four times across features and its third round was
    // held only because the page session noticed it - a change of active feature wiped the counts
    let (root, _) = setup("unit-follows");
    std::fs::create_dir_all(root.join("research/questions")).unwrap();
    std::fs::write(
        root.join("research/questions/0097-staff-rowhouses.html"),
        "<p>Rowhouses ran about 80 to 300 ft long.</p>",
    )
    .unwrap();
    let manifest = root.join("rf/MANIFEST.md");
    std::fs::create_dir_all(manifest.parent().unwrap()).unwrap();
    std::fs::write(&manifest, "unit: record-format:0097 fp\n").unwrap();
    let prompt = format!("Run your check on the bundle {}", manifest.display());
    assert_eq!(record_round(&root, &prompt, "r1", 1000.0), "");
    assert_eq!(record_round(&root, &prompt, "r2", 1001.0), "");
    std::fs::create_dir_all(root.join("specs/998-y")).unwrap();
    std::fs::write(
        root.join(".specify/feature.json"),
        r#"{"feature_directory": "specs/998-y"}"#,
    )
    .unwrap();
    let third = record_round(&root, &prompt, "r3", 1002.0);
    // the third round is held under the next feature
    assert!(third.contains("round 3 of `record-format` on q:0097 passes its cap of 2"));
    let s = state(&root);
    assert_eq!(s["rounds"]["record-format|q:0097"], json!(2));
    assert_eq!(s["round_home"]["record-format|q:0097"], json!("999-x"));
    let owed = load(&root.join(".git/arbiter-owed.json"));
    // filed under the feature its count began in, where its ruling is read
    assert_eq!(
        owed["round:record-format|q:0097@3"]["feature"],
        json!("999-x")
    );
    // make arbiter-bundle BATCH=1 bundles it under the active feature
    assert_eq!(
        crate::checks::arbiter::batch_triggers(&root, &[]),
        ["round:record-format|q:0097@3"]
    );
    std::fs::write(
        root.join("specs/999-x/arbiter.jsonl"),
        "{\"trigger\": \"round:record-format|q:0097@3\", \"ruling\": \"continue\"}\n",
    )
    .unwrap();
    let path = root.join(".git/arbiter-owed.json");
    save(&path, &json!({})).unwrap();
    // the continue ruled in its home feature lifts the hold under the next
    assert_eq!(record_round(&root, &prompt, "r4", 1003.0), "");
}

fn git(at: &Path, args: &[&str]) {
    let said = crate::tool::ask(at, "git", args, "");
    assert!(said.ok(), "{args:?}: {}", said.err);
}

/// Commit everything in `at` as `msg`.
fn commit(at: &Path, msg: &str) {
    git(at, &["add", "-A"]);
    let who = ["-c", "user.name=t", "-c", "user.email=t@t"];
    git(at, &[&who[..], &["commit", "-q", "-m", msg]].concat());
}

/// A clone with 0097's page committed and pushed to a bare `origin`, and a second clone of that origin: another session.
fn two_sessions(
    tag: &str,
) -> (
    crate::tempdir::Held<std::path::PathBuf>,
    crate::tempdir::TempDir,
    crate::tempdir::TempDir,
) {
    let (root, _) = setup(tag);
    std::fs::create_dir_all(root.join("research/questions")).unwrap();
    std::fs::write(
        root.join("research/questions/0097-staff-rowhouses.html"),
        "<p>Rowhouses ran about 80 to 300 ft long.</p>",
    )
    .unwrap();
    commit(&root, "the page");
    let up = crate::checks::testkit::dir(&format!("{tag}-up"));
    git(up.path(), &["init", "--bare", "-q"]);
    git(
        &root,
        &["remote", "add", "origin", &up.path().to_string_lossy()],
    );
    git(&root, &["push", "-q", "origin", "HEAD:main"]);
    let other = crate::checks::testkit::dir(&format!("{tag}-other"));
    git(
        other.path(),
        &["clone", "-q", &up.path().to_string_lossy(), "."],
    );
    (root, up, other)
}

/// The other session lands `file` with `body`; this clone fetches and merges it (a fetch move of `origin/main`).
fn they_land(root: &Path, other: &Path, file: &str, body: &str) {
    git(other, &["fetch", "-q", "origin"]);
    git(other, &["merge", "-q", "--ff-only", "origin/main"]);
    let path = other.join(file);
    std::fs::create_dir_all(path.parent().unwrap()).unwrap();
    std::fs::write(path, body).unwrap();
    commit(other, file);
    git(other, &["push", "-q", "origin", "HEAD:main"]);
    git(root, &["fetch", "-q", "origin"]);
    git(root, &["merge", "-q", "--ff-only", "origin/main"]);
}

/// This clone lands `file` with `body` (a push move of `origin/main`).
fn we_land(root: &Path, file: &str, body: &str) {
    let path = root.join(file);
    std::fs::create_dir_all(path.parent().unwrap()).unwrap();
    std::fs::write(path, body).unwrap();
    commit(root, file);
    git(root, &["push", "-q", "origin", "HEAD:main"]);
}

/// A record round dispatched, returned and answered (`make record-answer`), as 0097's 2026-11-24 rounds stand in the clone's state.
fn answered_round(root: &Path, prompt: &str, tid: &str, at: f64) -> String {
    let said = record_round(root, prompt, tid, at);
    crate::checks::rounds::record_answer(root, "record-format", &["record-format:0097".to_owned()]);
    said
}

fn whole_page_prompt(root: &Path) -> String {
    let manifest = root.join("rf/MANIFEST.md");
    std::fs::create_dir_all(manifest.parent().unwrap()).unwrap();
    std::fs::write(&manifest, "unit: record-format:0097 fp\n").unwrap();
    format!("Run your check on the bundle {}", manifest.display())
}

#[test]
fn a_later_batch_whose_moves_left_the_page_alone_keeps_the_count() {
    // 451 T248, 0097's 2026-11-24 sequence (the clone's origin/main reflog against record-format's dispatch times): rounds 1 and 2 at
    // 05:15-05:25Z, then ten moves of origin/main - the round's own edits of 0097 landed by this clone's push (7fc9f06512 in
    // c7dac385dd), eight more of its own pushes and a fetch of other sessions' work on other files - and the next round after them
    // ran as round 1 of a fresh count
    let (root, _up, other) = two_sessions("unrelated-moves");
    let prompt = whole_page_prompt(&root);
    assert_eq!(answered_round(&root, &prompt, "r1", 1000.0), "");
    assert_eq!(answered_round(&root, &prompt, "r2", 1001.0), "");
    let page = "research/questions/0097-staff-rowhouses.html";
    we_land(
        &root,
        page,
        "<p>Rowhouses ran about 80 to 300 ft long, past 145 ft at Matsusaka.</p>",
    );
    for n in 0..8 {
        we_land(&root, &format!("specs/999-x/n{n}.md"), "x\n");
    }
    they_land(&root, other.path(), "specs/453-z/spec.md", "theirs\n");
    let third = answered_round(&root, &prompt, "r3", 1002.0);
    // the round's own edits landing, and moves elsewhere, are no new cause: round 3 is held (on HEAD it was let through, "")
    assert!(third.contains("round 3 of `record-format` on q:0097 passes its cap of 2"));
}

#[test]
fn a_later_batch_whose_page_another_session_moved_starts_a_fresh_count() {
    // 451 T248: the batch rule's intent kept (c5db336fd3, the round arbiter on woodland-commons@3) - a subject that truly changed
    // upstream owes a check its next rounds afresh
    let (root, _up, other) = two_sessions("page-moved");
    let prompt = whole_page_prompt(&root);
    assert_eq!(answered_round(&root, &prompt, "r1", 1000.0), "");
    assert_eq!(answered_round(&root, &prompt, "r2", 1001.0), "");
    we_land(&root, "specs/999-x/n.md", "x\n");
    they_land(
        &root,
        other.path(),
        "research/questions/0097-staff-rowhouses.notes.html",
        "<p>A note another session wrote.</p>",
    );
    assert_eq!(answered_round(&root, &prompt, "r3", 1002.0), "");
    let s = state(&root);
    assert_eq!(s["rebased"]["record-format|q:0097"]["cause"], json!(true));
    assert_eq!(s["rebased"]["record-format|q:0097"]["n"], json!(2));
    // its fresh count has its own cap
    assert_eq!(answered_round(&root, &prompt, "r4", 1003.0), "");
    assert!(answered_round(&root, &prompt, "r5", 1004.0)
        .contains("round 5 of `record-format` on q:0097 passes its cap of 4"));
}

/// 451 T306 (T295's D3 limit): a Bash call is placed in the tree its command lands in, as the walk reads its `cd`s and `-C`s, so a
/// builder's `cd <worktree> && sed -i ... plan.md`, run with the session's clone as its cwd, is judged and written back in the
/// worktree; a call that moves nowhere, and any other tool's, stays in its cwd's tree.
#[test]
fn a_bash_call_is_placed_where_its_command_lands() {
    let clone = clone_at("lands-clone");
    let tree = clone_at("lands-tree");
    let (c, t) = (clone.display(), tree.display());
    let bash = |cmd: String| json!({"cwd": c.to_string(), "tool_name": "Bash", "tool_input": {"command": cmd}});
    for cmd in [
        format!("cd {t} && sed -i s/a/b/ specs/900-a/plan.md"),
        format!("cd {t} && make task-add F=900 TITLE=x"),
        format!("git -C {t} add -A"),
        format!("make -C {t} decide"),
    ] {
        let (got, want) = (
            super::call_root(&bash(cmd.clone())),
            Some(tree.to_path_buf()),
        );
        assert_eq!(got, want, "{cmd}");
    }
    for cmd in [
        "sed -i s/a/b/ specs/900-a/plan.md".to_owned(),
        "ls /x".to_owned(),
        // a command that lands in no tree stays in its cwd's
        "cd /proc && ls".to_owned(),
    ] {
        let (got, want) = (
            super::call_root(&bash(cmd.clone())),
            Some(clone.to_path_buf()),
        );
        assert_eq!(got, want, "{cmd}");
    }
    let edit = json!({"cwd": c.to_string(), "tool_name": "Edit", "tool_input": {"command": format!("cd {t}")}});
    assert_eq!(super::call_root(&edit), Some(clone.to_path_buf()));
}
