use std::path::{Path, PathBuf};
use std::sync::atomic::{AtomicU64, Ordering};

use serde_json::{json, Value};

use super::{
    batch_plan, cli, fix_hold, open_fixes, py_repr, record_batch, record_ruling, spec_body_sha,
    spec_ruled, spec_verdict, unit_ruled, Stop,
};

static NEXT: AtomicU64 = AtomicU64::new(0);

fn clone_at(name: &str) -> PathBuf {
    let d = std::env::temp_dir().join(format!(
        "l7r-gate-arbiter-{}-{}-{name}",
        std::process::id(),
        NEXT.fetch_add(1, Ordering::Relaxed)
    ));
    let _ = std::fs::remove_dir_all(&d);
    std::fs::create_dir_all(&d).unwrap();
    let root = std::fs::canonicalize(&d).unwrap();
    assert!(std::process::Command::new("git")
        .arg("-C")
        .arg(&root)
        .args(["init", "-q"])
        .status()
        .unwrap()
        .success());
    std::fs::create_dir_all(root.join(".specify")).unwrap();
    std::fs::write(
        root.join(".specify/feature.json"),
        r#"{"feature_directory": "specs/999-x"}"#,
    )
    .unwrap();
    std::fs::create_dir_all(root.join("specs/999-x")).unwrap();
    std::fs::write(
        root.join("specs/999-x/spec.md"),
        "# t\n\nstatus: draft\n\n## Body\n\ntext\n\n## Review history\n\nmore\n",
    )
    .unwrap();
    root
}

fn owe(root: &Path, map: &Value) {
    std::fs::write(root.join(".git/arbiter-owed.json"), map.to_string()).unwrap();
}

fn rows(root: &Path) -> Vec<Value> {
    std::fs::read_to_string(root.join("specs/999-x/arbiter.jsonl"))
        .unwrap_or_default()
        .lines()
        .map(|l| serde_json::from_str(l).unwrap())
        .collect()
}

fn refused(result: Result<Value, Stop>, words: &str) {
    match result {
        Err(Stop::Refused(why)) => assert!(why.contains(words), "{why}"),
        other => panic!("{other:?}"),
    }
}

#[test]
fn a_ruling_is_recorded_once_and_lifts_its_trigger() {
    let root = clone_at("ruling");
    let w = json!({"ruling": "continue", "why": "w"});
    let when = Some("2026-01-01T00:00:00Z");
    match record_ruling(&root, "ask:foo", &w, "main", when, false) {
        Err(Stop::Declined(why)) => assert!(why.starts_with("declined:")),
        other => panic!("{other:?}"),
    }
    owe(
        &root,
        &json!({"ask:foo": {"kind": "ask", "unit": "", "detail": "why asked", "t": 1, "feature": "999-x"}, "ask:bar": {"kind": "cascade", "unit": "u", "t": 1, "feature": "999-x", "dispatches": 12}}),
    );
    let row = record_ruling(&root, "ask:foo", &w, "round-arbiter", when, false).unwrap();
    assert_eq!(
        row,
        json!({"trigger": "ask:foo", "kind": "ask", "unit": "", "asked": "why asked", "ruling": "continue", "why": "w", "what": "", "utc": "2026-01-01T00:00:00Z"})
    );
    assert_eq!(std::fs::read_to_string(root.join("specs/999-x/arbiter.jsonl")).unwrap(), "{\"trigger\": \"ask:foo\", \"kind\": \"ask\", \"unit\": \"\", \"asked\": \"why asked\", \"ruling\": \"continue\", \"why\": \"w\", \"what\": \"\", \"utc\": \"2026-01-01T00:00:00Z\"}\n");
    refused(
        record_ruling(&root, "ask:foo", &w, "round-arbiter", when, false),
        "already ruled",
    );
    let row = record_ruling(
        &root,
        "ask:bar",
        &json!({"ruling": "process-fault", "why": "f", "tooling_fix": "fix it", "fix_minutes": 3}),
        "round-arbiter",
        when,
        false,
    )
    .unwrap();
    assert_eq!(row["dispatches"], json!(12));
    assert_eq!(row["tooling_fix"], json!("fix it"));
    assert_eq!(row["fix"], json!("open"));
    assert_eq!(row["fix_minutes"], json!(3.0));
    let owed = std::fs::read_to_string(root.join(".git/arbiter-owed.json")).unwrap();
    assert!(!owed.contains("ask:foo") && !owed.contains("ask:bar"));
}

#[test]
fn a_ruling_is_checked_before_anything_is_written() {
    let root = clone_at("checks");
    let t = "ask:foo";
    let by = |v: Value| record_ruling(&root, t, &v, "round-arbiter", None, false);
    refused(
        by(json!({"ruling": "maybe", "why": "w"})),
        "a ruling is one of",
    );
    refused(by(json!({"ruling": "continue"})), "a ruling is one of");
    refused(
        by(json!({"ruling": "continue", "why": "  "})),
        "a ruling is one of",
    );
    refused(
        by(json!({"ruling": "process-fault", "why": "w"})),
        "names its fault",
    );
    refused(
        by(json!({"ruling": "accept", "why": "the GM's call"})),
        "hands the GM a decision",
    );
    refused(
        by(json!({"ruling": "accept", "why": "w", "what": "held for the GM"})),
        "hands the GM a decision",
    );
    refused(
        by(json!({"ruling": "process-fault", "why": "w", "tooling_fix": "f"})),
        "fix_minutes",
    );
    refused(
        by(json!({"ruling": "process-fault", "why": "w", "tooling_fix": "f", "fix_minutes": -1})),
        "fix_minutes",
    );
    refused(
        by(json!({"ruling": "process-fault", "why": "w", "tooling_fix": "f", "fix_minutes": "x"})),
        "fix_minutes",
    );
    refused(
        by(json!({"ruling": "process-fault", "why": "w", "tooling_fix": "f", "fix_minutes": [1]})),
        "fix_minutes",
    );
    refused(
        record_ruling(
            &root,
            "hour:999@1",
            &json!({"ruling": "change-route", "why": "w"}),
            "round-arbiter",
            None,
            false,
        ),
        "change-route",
    );
    assert!(rows(&root).is_empty());
    let ok = by(
        json!({"ruling": "process-fault", "why": "w", "tooling_fix": "f", "fix_minutes": "2.5"}),
    )
    .unwrap();
    assert_eq!(ok["fix_minutes"], json!(2.5));
    let nofeature = clone_at("no-feature");
    std::fs::remove_file(nofeature.join(".specify/feature.json")).unwrap();
    refused(
        record_ruling(
            &nofeature,
            "ask:x",
            &json!({"ruling": "continue", "why": "w"}),
            "round-arbiter",
            None,
            false,
        ),
        "no active feature",
    );
    let hour = record_ruling(
        &root,
        "hour:999@2",
        &json!({"ruling": "change-route", "why": "w", "what": "the route"}),
        "round-arbiter",
        None,
        false,
    )
    .unwrap();
    assert_eq!(hour["ruling"], json!("change-route"));
}

#[test]
fn a_round_owed_with_others_is_ruled_as_a_batch() {
    let root = clone_at("batch");
    owe(
        &root,
        &json!({"round:a|q:1@3": {"kind": "round", "unit": "a|q:1", "feature": "999-x", "t": 1}, "round:b|q:2@3": {"kind": "round", "unit": "b|q:2", "feature": "999-x", "t": 1}}),
    );
    refused(
        record_ruling(
            &root,
            "round:a|q:1@3",
            &json!({"ruling": "continue", "why": "w"}),
            "round-arbiter",
            None,
            false,
        ),
        "rule them together",
    );
    let w =
        json!({"ruling": "continue", "why": "w", "triggers": ["round:a|q:1@3", "round:b|q:2@3"]});
    let done = record_batch(&root, &w, "round-arbiter", None).unwrap();
    assert_eq!(done.len(), 2);
    match record_batch(&root, &w, "round-arbiter", None) {
        Err(Stop::Refused(why)) => assert!(
            why.contains("already ruled: round:a|q:1@3, round:b|q:2@3"),
            "{why}"
        ),
        other => panic!("{other:?}"),
    }
    let by = |v: Value| record_batch(&root, &v, "round-arbiter", None).map(|_| Value::Null);
    refused(by(json!({"triggers": []})), "names its `triggers`");
    refused(
        by(json!({"ruling": "c", "why": "w", "triggers": ["x", "x"]})),
        "named twice: x",
    );
    refused(
        by(json!({"ruling": "c", "why": "w", "triggers": ["x"], "exceptions": {"y": {}}})),
        "exception names a trigger",
    );
    match record_batch(
        &root,
        &json!({"ruling": "c", "why": "w", "triggers": ["x"]}),
        "main",
        None,
    ) {
        Err(Stop::Declined(_)) => {}
        other => panic!("{other:?}"),
    }
    refused(
        by(json!({"ruling": "bad", "why": "w", "triggers": ["ask:z1"]})),
        "ask:z1: a ruling is one of",
    );
    refused(
        by(json!({"ruling": "process-fault", "why": "w", "triggers": ["ask:z2"]})),
        "names its fault",
    );
}

#[test]
fn a_batch_fix_lands_on_one_row() {
    let w = json!({"ruling": "process-fault", "why": "w", "tooling_fix": "f", "fix_minutes": 2, "triggers": ["t1", "t2", "t3"], "exceptions": {"t2": {"ruling": "continue", "why": "o"}}});
    let plan = batch_plan(&w, &["t1".to_owned(), "t2".to_owned(), "t3".to_owned()]).unwrap();
    assert_eq!(plan[0].1["tooling_fix"], json!("f"));
    assert_eq!(plan[0].1["fix_minutes"], json!(2));
    assert_eq!(plan[1].1["ruling"], json!("continue"));
    assert_eq!(plan[2].1["tooling_fix_on"], json!("t1"));
    let only_exceptions = json!({"tooling_fix": "f", "triggers": ["t1"], "exceptions": {"t1": {"ruling": "continue", "why": "o"}}});
    assert_eq!(
        batch_plan(&only_exceptions, &["t1".to_owned()]).unwrap()[0].1["tooling_fix"],
        json!("f")
    );
    let own_fix =
        json!({"tooling_fix": "f", "triggers": ["t1"], "exceptions": {"t1": {"tooling_fix": "g"}}});
    refused(
        batch_plan(&own_fix, &["t1".to_owned()]).map(|_| Value::Null),
        "where does the batch's fix go",
    );
    let plain = json!({"ruling": "c", "why": "w"});
    let p = batch_plan(&plain, &["t1".to_owned()]).unwrap();
    assert!(p[0].1.get("tooling_fix_on").is_none() && p[0].1.get("tooling_fix").is_none());
}

#[test]
fn verdicts_read_the_spec_and_its_rulings() {
    let root = clone_at("verdict");
    let d = root.join("specs/999-x");
    let sha = spec_body_sha(&d);
    assert_eq!(sha.len(), 64);
    assert_eq!(spec_verdict(&d), "");
    assert_eq!(spec_ruled(&d), "");
    std::fs::write(
        d.join("arbiter.jsonl"),
        format!(
            "not json\n{}\n",
            json!({"trigger": "round:spec-fidelity|999-x#1@6", "ruling": "accept", "spec_sha": sha})
        ),
    )
    .unwrap();
    assert_eq!(spec_ruled(&d), "round:spec-fidelity|999-x#1@6");
    std::fs::write(d.join("arbiter.jsonl"), format!("{}\n", json!({"trigger": "ask:1", "review": "spec", "ruling": "process-fault", "spec_sha": sha}))).unwrap();
    assert_eq!(spec_verdict(&d), "ask:1");
    std::fs::write(
        d.join("arbiter.jsonl"),
        format!(
            "{}\n",
            json!({"trigger": "ask:1", "review": "spec", "ruling": "accept", "spec_sha": "stale"})
        ),
    )
    .unwrap();
    assert_eq!(spec_ruled(&d), "");
    let mid = spec_body_sha(&d);
    std::fs::write(
        d.join("spec.md"),
        "# t\n\nstatus: other\n\n## Body\n\ntext\n\n## Review history\n\nchanged\n",
    )
    .unwrap();
    assert_eq!(
        spec_body_sha(&d),
        mid,
        "the header and the history are not what a review judged"
    );
    std::fs::write(d.join("spec.md"), "# t only").unwrap();
    assert_ne!(spec_body_sha(&d), mid);
    std::fs::write(
        d.join("spec.md"),
        "# t\n\nverdict: NOT FAITHFUL\nFAITHFUL in prose only\n",
    )
    .unwrap();
    assert_eq!(spec_verdict(&d), "");
    std::fs::write(d.join("spec.md"), "# t\n\nRound 2 verdict: FAITHFUL\n").unwrap();
    assert_eq!(spec_verdict(&d), "FAITHFUL");
    std::fs::write(d.join("arbiter.jsonl"), format!("x\n{}\n", json!({"unit": "c|u", "trigger": "round:c|u@3", "ruling": "accept", "content_key": "ck"}))).unwrap();
    assert_eq!(unit_ruled(&d, "u", "ck"), "round:c|u@3");
    assert_eq!(unit_ruled(&d, "c|u", "ck"), "round:c|u@3");
    assert_eq!(unit_ruled(&d, "u", "other"), "");
    assert_eq!(unit_ruled(&d, "u", ""), "");
}

#[test]
fn open_fixes_are_listed_until_settled() {
    let root = clone_at("fixes");
    let d = root.join("specs/999-x");
    assert_eq!(fix_hold(&d), "");
    std::fs::write(
        d.join("arbiter.jsonl"),
        format!(
            "x\n{}\n{}\n{}\n{}\n",
            json!({"trigger": "t1", "fix": "open", "tooling_fix": "one"}),
            json!({"trigger": "t1", "fix": "open", "tooling_fix": "newer"}),
            json!({"trigger": "t2", "fix": "open", "tooling_fix": "two"}),
            json!({"fix_of": "t2", "status": "done"})
        ),
    )
    .unwrap();
    assert_eq!(open_fixes(&d), [("t1".to_owned(), "newer".to_owned())]);
    let hold = fix_hold(&d);
    assert!(
        hold.starts_with("the round arbiter's tooling fix is open")
            && hold.contains("    t1: newer")
            && hold.contains("make arbiter-fix-declined")
    );
}

#[test]
fn a_python_string_repr_chooses_its_quote() {
    assert_eq!(py_repr("ab"), "'ab'");
    assert_eq!(py_repr("a'b"), "\"a'b\"");
    assert_eq!(py_repr("a'b\"c"), "'a\\'b\"c'");
    assert_eq!(py_repr("a\\\n\t\r"), "'a\\\\\\n\\t\\r'");
}

#[test]
fn every_verb_answers_on_a_clone() {
    let root = clone_at("cli");
    let old = std::env::current_dir().unwrap();
    std::env::set_current_dir(&root).unwrap();
    let run = |args: &[&str]| cli(&args.iter().map(|a| (*a).to_string()).collect::<Vec<_>>());
    assert_eq!(run(&["bogus"]).code, 2);
    assert_eq!(run(&[]).code, 2);
    assert_eq!(run(&["gate-held"]).code, 0);
    owe(
        &root,
        &json!({"red-gate@t": {"kind": "red-gate", "feature": "999-x"}}),
    );
    let held = run(&["gate-held"]);
    assert_eq!(held.code, 1);
    assert!(held.stderr.starts_with("make done: refused - a tripwire"));
    assert_eq!(run(&["spec-verdict", "specs/999-x"]).code, 1);
    assert_eq!(run(&["spec-ruled", "specs/999-x"]).code, 1);
    assert_eq!(run(&["unit-ruled", "u", "c"]).code, 1);
    assert_eq!(run(&["ask", "has space", "two words here"]).code, 2);
    assert_eq!(run(&["ask", "ok-1", "short"]).code, 2);
    assert_eq!(run(&["ask", "ok-1", "two words here", "wrong"]).code, 2);
    let asked = run(&["ask", "ok-1", "two words here", "spec"]);
    assert!(asked.code == 0 && asked.stdout.contains("(REVIEW=spec: an accept stands"));
    let hint = run(&["ask", "ok-2", "a plan review question"]);
    assert!(hint.stdout.contains("arbiter-ask: hint"));
    let claims = run(&["ask", "ok-3", "two words here", "claims:a"]);
    assert_eq!(claims.code, 0);
    let plain = run(&["ask", "ok-4", "two words here"]);
    assert!(!plain.stdout.contains("hint"));
    std::fs::write(
        "rule.json",
        format!(r#"{{"ruling": "continue", "why": "a colo{}r fix"}}"#, "u"),
    )
    .unwrap();
    std::fs::write("bad.json", "nope").unwrap();
    let wrong = run(&["ruled", "ask:ok-4", "rule.json", "--as", "main"]);
    assert!(wrong.code == 2 && wrong.stderr.starts_with("arbiter-ruled: declined"));
    assert_eq!(
        run(&["ruled", "ask:ok-4", "missing.json", "--as", "round-arbiter"]).code,
        1
    );
    assert_eq!(
        run(&["ruled", "ask:ok-4", "bad.json", "--as", "round-arbiter"]).code,
        1
    );
    let ruled = run(&["ruled", "ask:ok-4", "rule.json", "--as", "round-arbiter"]);
    assert!(
        ruled.code == 0
            && ruled
                .stdout
                .starts_with("arbiter-ruled: ask:ok-4 - continue (binding;"),
        "{}",
        ruled.stderr
    );
    assert!(rows(&root)[0]["why"].as_str().unwrap().contains("color"));
    let again = run(&["ask", "ok-4", "two words here"]);
    assert_eq!(again.code, 1);
    std::fs::write(
        "batch.json",
        r#"{"ruling": "continue", "why": "w", "triggers": ["ask:b1"]}"#,
    )
    .unwrap();
    let batch = run(&["ruled-batch", "batch.json", "--as", "round-arbiter"]);
    assert!(batch.code == 0 && batch.stdout.contains("the batch's 1 triggers recorded"));
    assert_eq!(
        run(&["ruled-batch", "bad.json", "--as", "round-arbiter"]).code,
        1
    );
    assert_eq!(run(&["fix", "done", "ask:none", "a note here"]).code, 1);
    let nit = run(&["nit", "ask:none", "a", "b"]);
    assert!(nit.code == 1 && nit.stderr.contains("no `accept` ruling"));
    std::env::set_current_dir(old).unwrap();
}
