//! Every reason the tick refuses (feature 449 T131): the plan gate unescaped, a spec waiting on an open feature, an open tooling fix,
//! several together, and a "landed" note over work not on main.

use l7r_gate_core::ci::fixtures::{git, put};
use serde_json::json;

use super::{field, files_of, landed_refusal, refusal, state, truthy, waits, Ask};
use crate::tests::{ask, env_of, repo, root_of};

#[test]
fn the_plan_gate_unescaped_refuses_and_its_message_is_kept_only_when_it_passes() {
    let dir = repo("plan-gate");
    let root = root_of(&dir);
    let d = root.join("specs/9001-x");
    let mut a = ask(&root, &d, "T01", "n");
    a.escaped = None;
    let (why, message) = refusal(&a, true, false).unwrap();
    assert!(why.starts_with(
        "tick: refused - tick: refused - 9001-x's plan decisions have no current CLEAR review"
    ));
    assert_eq!(message, "");
    let (none, said) = refusal(&ask(&root, &d, "T01", "n"), true, false).unwrap();
    assert_eq!(none, "");
    assert!(said.contains("BYPASSED"));
    // the process's ask reads the environment
    let env = env_of(&[("PLAN_REVIEW_OK", "x"), ("L7R_GATE_TREE", "/t")]);
    let from = Ask::with_env(&root, &d, "T01", "n", &env);
    assert_eq!(
        (from.escaped.as_deref(), from.tree.to_str()),
        (Some("x"), Some("/t"))
    );
    let cwd = Ask::with_env(&root, &d, "T01", "n", &env_of(&[]));
    assert_eq!(cwd.tree, std::env::current_dir().unwrap());
}

#[test]
fn a_spec_that_waits_on_an_open_feature_refuses() {
    let dir = repo("waits");
    let root = root_of(&dir);
    let d = root.join("specs/9001-x");
    assert_eq!(waits(&root, &d).unwrap(), "");
    std::fs::remove_file(d.join("spec.md")).unwrap();
    assert_eq!(waits(&root, &d).unwrap(), "", "no spec, no wait");
    put(&d, "spec.md", "**Waits on**: 9003\n");
    assert_eq!(waits(&root, &d).unwrap(), "");
    put(
        &root,
        "specs/9003-other/spec.md",
        "**Status**: In progress\n",
    );
    put(&root, "specs/9003-other/tasks.md", "- [ ] T01 a\n");
    assert_eq!(
        waits(&root, &d).unwrap(),
        "9001-x waits on feature 9003 (9003-other), which is still open - its spec says `**Waits on**: 9003`; take its tasks once that one has closed"
    );
    put(&root, "specs/9003-other/tasks.md", "- [x] T01 a\n");
    put(
        &root,
        "specs/9003-other/spec.md",
        "**Status**: Done 2026-11-12\n",
    );
    assert_eq!(waits(&root, &d).unwrap(), "");
    put(&d, "spec.md", "no wait\n");
    assert_eq!(waits(&root, &d).unwrap(), "");
    // a feature state that cannot be read raises, as `--each-state` failing did
    put(&d, "spec.md", "**Waits on**: 9003\n");
    put(&root, ".specify/affects.json", "not json");
    assert!(waits(&root, &d).unwrap_err().starts_with("speckit-todo: "));
    assert!(state(&d).is_err());
    std::fs::write(d.join("spec.md"), [0xff]).unwrap();
    assert!(waits(&root, &d).is_err());
}

#[test]
fn every_refusal_is_said_together_numbered() {
    let dir = repo("together");
    let root = root_of(&dir);
    let d = root.join("specs/9001-x");
    put(
        &d,
        "arbiter.jsonl",
        &format!(
            "{}\n",
            json!({"trigger": "round:x", "fix": "open", "tooling_fix": "the fix"})
        ),
    );
    let mut a = ask(&root, &d, "T03", "n");
    a.escaped = None;
    let (why, message) = refusal(&a, true, false).unwrap();
    assert!(why.starts_with("tick: refused - \n  (1) tick: refused - 9001-x's plan decisions"));
    assert!(
        why.contains("\n  (2) T03 is a `research: physical` task")
            && why.contains("\n  (3) the round arbiter's tooling fix is open")
    );
    assert_eq!(message, "");
    // no plan, no tasks: nothing but the fix
    std::fs::remove_file(d.join("plan.md")).unwrap();
    std::fs::remove_file(d.join("tasks.md")).unwrap();
    let (fix, _) = refusal(&ask(&root, &d, "T03", "n"), true, false).unwrap();
    assert!(fix.starts_with("tick: refused - \n  (1) the round arbiter's tooling fix is open"));
    assert!(fix.contains("\n  (2) T03 has no `### T03 Approach` block"));
    // an unreadable plan or tasks.md raises
    std::fs::write(d.join("plan.md"), [0xff]).unwrap();
    assert!(refusal(&ask(&root, &d, "T03", "n"), true, false).is_err());
    std::fs::remove_file(d.join("plan.md")).unwrap();
    std::fs::write(d.join("tasks.md"), [0xff]).unwrap();
    assert!(refusal(&ask(&root, &d, "T03", "n"), true, false).is_err());
}

fn tooling(root: &std::path::Path, rows: &[serde_json::Value]) {
    let mut text = String::new();
    for r in rows {
        text.push_str(&r.to_string());
        text.push('\n');
    }
    text.push_str("not json\n");
    std::fs::write(root.join(".git/land-tooling.jsonl"), text).unwrap();
}

#[test]
fn a_landed_note_over_work_off_main_refuses() {
    let dir = repo("landed");
    let root = root_of(&dir);
    let d = root.join("specs/9001-x");
    let landed = |note: &str| landed_refusal(&root, "9001-x", "T01", note).unwrap();
    assert_eq!(landed("verified"), "");
    // no run: work committed off main refuses, the feature's records and the run records do not
    assert_eq!(landed("landed"), "");
    put(&root, "specs/9001-x/n.md", "n\n");
    put(&root, "dev/r.md", "n\n");
    git(&root, &["add", "-A"]);
    git(&root, &["commit", "-qm", "records"]);
    assert_eq!(landed("LANDED"), "");
    put(&root, "scripts/a.py", "x = 2\n");
    git(&root, &["add", "-A"]);
    git(&root, &["commit", "-qm", "work"]);
    assert!(landed("landed").starts_with(
        "the NOTE says landed, but scripts/a.py is committed here and not on origin/main"
    ));
    // the last run failed: its files off main refuse; on main, it passes
    let row = |task: &str, outcome: &str, files: serde_json::Value| json!({"feature": "9001-x", "task": task, "outcome": outcome, "log": "/l", "files": files});
    tooling(&root, &[row("T01", "failed", json!(["scripts/a.py"]))]);
    assert_eq!(landed("landed"), "the NOTE says landed, but T01's last make land-tooling ended 'failed' (/l) - land it, then tick");
    tooling(
        &root,
        &[row(
            "T01",
            "landed",
            json!(["scripts/a.py", "dev/review-ledger.md"]),
        )],
    );
    assert!(landed("landed").contains("scripts/a.py differs from origin/main"));
    tooling(&root, &[row("T01", "failed", json!(["specs/x"]))]);
    assert_eq!(landed("landed"), "");
    tooling(&root, &[json!({"feature": "9001-x", "task": "T01"})]);
    assert!(landed("landed").contains("ended 'None' (None)"));
    // a later run of the same files lands them
    tooling(
        &root,
        &[
            row("T01", "failed", json!(["scripts/a.py"])),
            row("T81", "landed", json!(["specs/y", "scripts/a.py"])),
            row("T82", "landed", json!(["other"])),
        ],
    );
    assert!(landed("landed").contains("differs from origin/main"));
    // rows Python could not read raise
    tooling(&root, &[json!([1])]);
    assert!(landed_refusal(&root, "9001-x", "T01", "landed").is_err());
    tooling(&root, &[row("T01", "failed", json!(5))]);
    assert!(landed_refusal(&root, "9001-x", "T01", "landed").is_err());
    tooling(&root, &[row("T01", "failed", json!(["a"])), json!("text")]);
    assert!(landed_refusal(&root, "9001-x", "T01", "landed").is_err());
    std::fs::write(root.join(".git/land-tooling.jsonl"), [0xff]).unwrap();
    assert!(landed_refusal(&root, "9001-x", "T01", "landed").is_err());
    // outside a repository: no runs, and nothing ahead to read
    let _ = d;
    assert_eq!(landed_refusal(&dir, "9001-x", "T01", "landed").unwrap(), "");
    // the whole refusal asks it last, and only when nothing else refused
    std::fs::remove_file(root.join(".git/land-tooling.jsonl")).unwrap();
    let (why, _) = refusal(
        &ask(&root, &root.join("specs/9001-x"), "T01", "landed"),
        true,
        false,
    )
    .unwrap();
    assert!(why.contains("is committed here and not on origin/main"));
    assert_eq!(
        refusal(
            &ask(&root, &root.join("specs/9001-x"), "T01", "landed"),
            false,
            false
        )
        .unwrap()
        .0,
        ""
    );
}

#[test]
fn python_s_reading_of_a_row() {
    assert!(!truthy(None));
    for (v, t) in [
        (json!(null), false),
        (json!(true), true),
        (json!(0), false),
        (json!(1.5), true),
        (json!(""), false),
        (json!("a"), true),
        (json!([]), false),
        (json!([1]), true),
        (json!({}), false),
        (json!({"a": 1}), true),
    ] {
        assert_eq!(truthy(Some(&v)), t, "{v}");
    }
    for (v, kind) in [
        (json!([]), "list"),
        (json!("s"), "str"),
        (json!(true), "bool"),
        (json!(null), "NoneType"),
        (json!(1), "number"),
    ] {
        assert!(field(&v, "x").unwrap_err().contains(&format!("'{kind}'")));
    }
    assert_eq!(files_of(&json!({"files": "ab"})).unwrap(), vec!["a", "b"]);
    assert_eq!(files_of(&json!({"files": {"k": 1}})).unwrap(), vec!["k"]);
    assert_eq!(
        files_of(&json!({"files": [1, "x"]})).unwrap(),
        vec!["1", "x"]
    );
    assert_eq!(files_of(&json!({})).unwrap(), Vec::<String>::new());
    assert!(files_of(&json!({"files": true})).is_err());
}
