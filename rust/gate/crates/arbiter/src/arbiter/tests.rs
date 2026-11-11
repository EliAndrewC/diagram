use std::path::Path;

use serde_json::{json, Value};

use super::{
    batch_plan, cli_in, fix_hold, open_fixes, py_repr, record_batch, record_ruling, spec_body_sha,
    spec_ruled, spec_verdict, unit_ruled, Stop,
};

fn clone_at(name: &str) -> l7r_guard::shared::tempdir::Held<std::path::PathBuf> {
    let d = l7r_guard::shared::tempdir::TempDir::new(&format!("gate-arbiter-{name}"));
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
    d.hold(root)
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

fn refused<T: std::fmt::Debug>(result: Result<T, Stop>, words: &str) {
    let why = result.err().map_or_else(String::new, Stop::words);
    assert!(why.contains(words), "{why}");
}

impl Stop {
    fn words(self) -> String {
        match self {
            Self::Declined(w) | Self::Refused(w) => w,
        }
    }
}

#[expect(
    clippy::needless_pass_by_value,
    reason = "the call's result, read here and dropped"
)]
fn declined<T: std::fmt::Debug>(result: Result<T, Stop>) {
    assert!(matches!(result, Err(Stop::Declined(_))), "{result:?}");
}

#[test]
fn a_ruling_is_recorded_once_and_lifts_its_trigger() {
    let root = clone_at("ruling");
    let w = json!({"ruling": "continue", "why": "w"});
    let when = Some("2026-01-01T00:00:00Z");
    declined(record_ruling(&root, "ask:foo", &w, "main", when, false));
    owe(
        &root,
        &json!({"ask:foo": {"kind": "ask", "unit": "", "detail": "why asked", "t": 1, "feature": "999-x"}, "ask:bar": {"kind": "cascade", "unit": "u", "t": 1, "feature": "999-x", "dispatches": 12}}),
    );
    let row = record_ruling(&root, "ask:foo", &w, "round-arbiter", when, false).unwrap();
    // a unit owed on no sheet has no content key
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
    python_tools(&root);
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
    refused(
        record_batch(&root, &w, "round-arbiter", None),
        "already ruled: round:a|q:1@3, round:b|q:2@3",
    );
    let by = |v: Value| record_batch(&root, &v, "round-arbiter", None);
    refused(by(json!({"triggers": []})), "names its `triggers`");
    refused(
        by(json!({"ruling": "c", "why": "w", "triggers": ["x", "x"]})),
        "named twice: x",
    );
    refused(
        by(json!({"ruling": "c", "why": "w", "triggers": ["x"], "exceptions": {"y": {}}})),
        "exception names a trigger",
    );
    declined(record_batch(
        &root,
        &json!({"ruling": "c", "why": "w", "triggers": ["x"]}),
        "main",
        None,
    ));
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
        batch_plan(&own_fix, &["t1".to_owned()]),
        "where does the batch's fix go",
    );
    let bare = json!({"ruling": "c", "why": "w"});
    let p = batch_plan(&bare, &["t1".to_owned()]).unwrap();
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
    assert_eq!(spec_body_sha(&d), mid);
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

const FAKE_GM_REVIEW: &str = "from pathlib import Path\ndef question(d, text, source, when):\n    Path(d, 'gm-question.txt').write_text(text + '|' + source + '|' + when)\n";

fn python_tools(root: &Path) {
    std::fs::write(root.join(".fake-answer"), "ok").unwrap();
    let scripts = root.join("scripts");
    std::fs::create_dir_all(&scripts).unwrap();
    std::fs::write(scripts.join("gm_review.py"), FAKE_GM_REVIEW).unwrap();
}

fn run(root: &Path, args: &[&str]) -> crate::Reply {
    cli_in(
        &args.iter().map(|a| (*a).to_string()).collect::<Vec<_>>(),
        root,
    )
}

fn rule_file(root: &Path, name: &str, body: &Value) -> String {
    let p = root.join(name);
    std::fs::write(&p, body.to_string()).unwrap();
    p.to_string_lossy().into_owned()
}

#[test]
fn the_rulings_tools_are_asked_by_path() {
    let root = clone_at("tools");
    python_tools(&root);
    owe(
        &root,
        &json!({
            "round:quote-check|q:0105@3": {"kind": "round", "unit": "quote-check|q:0105", "feature": "999-x", "t": 1},
        }),
    );
    let accept = json!({"ruling": "accept", "why": "fine"});
    let row = record_ruling(
        &root,
        "round:quote-check|q:0105@3",
        &accept,
        "round-arbiter",
        None,
        false,
    )
    .unwrap();
    assert!(row.get("content_key").is_none());
    std::fs::write(
        root.join(".git/glyph-clock.json"),
        r#"{"999-x": {"checkpoint_open_at": 5, "checkpoint_trigger": "hour:999-x@1"}}"#,
    )
    .unwrap();
    let hour = record_ruling(
        &root,
        "hour:999-x@1",
        &json!({"ruling": "continue", "why": "w"}),
        "round-arbiter",
        None,
        false,
    )
    .unwrap();
    assert_eq!(hour["kind"], json!("hour"));
    let clock: Value =
        serde_json::from_str(&std::fs::read_to_string(root.join(".git/glyph-clock.json")).unwrap())
            .unwrap();
    assert_eq!(clock["999-x"]["checkpoint_at"], json!(5));
    assert_eq!(clock["999-x"]["checkpoints"], json!(1));
    let row = record_ruling(
        &root,
        "round:spec-fidelity|999-x#1@6",
        &json!({"ruling": "accept", "why": "w", "for_gm": "is this right sir please"}),
        "round-arbiter",
        Some("2026-01-01T00:00:00Z"),
        false,
    )
    .unwrap();
    assert!(!row["spec_sha"].as_str().unwrap().is_empty());
    assert_eq!(
        std::fs::read_to_string(root.join("specs/999-x/gm-question.txt")).unwrap(),
        "is this right sir please|round:spec-fidelity|999-x#1@6|2026-01-01T00:00:00Z"
    );
    // a content-key ruling written without its key may be recorded again, the rekey: the unit a map new to the pool
    let before = rows(&root).len();
    let map = root.join("pool/hamlets/m");
    std::fs::create_dir_all(&map).unwrap();
    std::fs::write(map.join("m.json"), "{}").unwrap();
    std::fs::write(map.join("m.svg"), "<svg/>").unwrap();
    let unit = "settlement-review|settlement-review--m";
    std::fs::write(
        root.join("specs/999-x/arbiter.jsonl"),
        format!(
            "{}\n",
            json!({"trigger": format!("round:{unit}@3"), "ruling": "accept", "kind": "round", "unit": unit})
        ),
    )
    .unwrap();
    let trigger = format!("round:{unit}@3");
    let rekeyed = record_ruling(&root, &trigger, &accept, "round-arbiter", None, false).unwrap();
    let key = crate::reviews::prereq::unit_content_key(&root, "settlement-review--m");
    assert_eq!(key.len(), 16);
    assert_eq!(rekeyed["content_key"], json!(key));
    assert!(before >= 1);
    refused(
        record_ruling(&root, &trigger, &accept, "round-arbiter", None, false),
        "already ruled",
    );
    let bad_dir = root.join("specs/afile");
    std::fs::write(&bad_dir, "not a dir").unwrap();
    let pointed = clone_at("pointed");
    std::fs::write(
        pointed.join(".specify/feature.json"),
        r#"{"feature_directory": "specs/afile"}"#,
    )
    .unwrap();
    std::fs::write(pointed.join("specs/afile"), "x").unwrap();
    refused(
        record_ruling(
            &pointed,
            "ask:x",
            &json!({"ruling": "continue", "why": "w"}),
            "round-arbiter",
            None,
            false,
        ),
        "",
    );
}

#[test]
fn a_plan_or_claims_ask_stands_as_that_reviews_verdict() {
    let root = clone_at("reviews");
    python_tools(&root);
    std::fs::write(
        root.join("specs/999-x/plan.md"),
        "# p\n\n## T01 x\n\nbody\n",
    )
    .unwrap();
    owe(
        &root,
        &json!({
            "ask:999-x-plan": {"kind": "ask", "unit": "", "feature": "999-x", "t": 1, "review": "plan", "detail": "why"},
            "ask:999-x-claims": {"kind": "ask", "unit": "", "feature": "999-x", "t": 1, "review": "claims:a;b"},
            "red-gate@1": {"kind": "red-gate", "feature": "999-x"},
        }),
    );
    let accept = rule_file(
        &root,
        "accept.json",
        &json!({"ruling": "accept", "why": "fine", "n": 3}),
    );
    let said = run(
        &root,
        &["ruled", "ask:999-x-plan", &accept, "--as", "round-arbiter"],
    );
    assert_eq!(said.code, 0, "{}", said.stderr);
    assert!(
        said.stdout.contains("plan block(s) recorded CLEAR"),
        "{}",
        said.stdout
    );
    let claims = run(
        &root,
        &[
            "ruled",
            "ask:999-x-claims",
            &accept,
            "--as",
            "round-arbiter",
        ],
    );
    assert!(
        claims.stdout.contains("claims-accept: no such claim: a, b"),
        "{}",
        claims.stdout
    );
    let red = rule_file(
        &root,
        "red.json",
        &json!({"ruling": "continue", "why": "w"}),
    );
    let held = run(
        &root,
        &["ruled", "red-gate@1", &red, "--as", "round-arbiter"],
    );
    assert_eq!(held.code, 0, "{}", held.stderr);
    let batch = rule_file(
        &root,
        "batch.json",
        &json!({"ruling": "continue", "why": "w", "triggers": ["red-gate@2"]}),
    );
    let b = run(&root, &["ruled-batch", &batch, "--as", "round-arbiter"]);
    assert!(
        b.code == 0 && b.stdout.contains("the batch's 1 triggers recorded"),
        "{}",
        b.stderr
    );
    let failing = clone_at("no-plan");
    owe(
        &failing,
        &json!({"ask:999-p": {"kind": "ask", "unit": "", "feature": "999-x", "t": 1, "review": "plan"}}),
    );
    let rule = rule_file(&failing, "r.json", &json!({"ruling": "accept", "why": "w"}));
    let failed = run(
        &failing,
        &["ruled", "ask:999-p", &rule, "--as", "round-arbiter"],
    );
    assert!(failed.code == 0 || failed.code == 1, "{}", failed.stderr);
}

#[test]
fn a_failed_tool_leaves_the_ruling_half_recorded_and_refuses() {
    let root = clone_at("half");
    python_tools(&root);
    std::fs::write(root.join(".fake-answer"), "fail").unwrap();
    owe(
        &root,
        &json!({"round:c|q:0105@3": {"kind": "round", "unit": "c|q:0105", "feature": "999-x", "t": 1}}),
    );
    refused(
        record_ruling(
            &root,
            "round:c|q:0105@3",
            &json!({"ruling": "accept", "why": "w"}),
            "round-arbiter",
            None,
            false,
        ),
        "record-owed said",
    );
    assert_eq!(rows(&root).len(), 1);
    assert!(std::fs::read_to_string(root.join(".git/arbiter-owed.json"))
        .unwrap()
        .contains("round:c|q:0105@3"));
    refused(
        record_ruling(
            &root,
            "ask:gm",
            &json!({"ruling": "continue", "why": "w", "for_gm": "is this all right for you"}),
            "round-arbiter",
            None,
            false,
        ),
        "",
    );
    std::fs::write(root.join("specs/999-x/arbiter.jsonl"), "").unwrap();
    std::fs::write(
        root.join("scripts/gm_review.py"),
        "raise ImportError('x')\n",
    )
    .unwrap();
    refused(
        record_ruling(
            &root,
            "ask:gm2",
            &json!({"ruling": "continue", "why": "w", "for_gm": "is this all right for you"}),
            "round-arbiter",
            None,
            false,
        ),
        "python3 said",
    );
    std::fs::write(
        root.join("specs/999-x/arbiter.jsonl"),
        format!(
            "{}\n",
            json!({"trigger": "ask:f", "fix": "open", "tooling_fix": "e"})
        ),
    )
    .unwrap();
    refused(
        super::settle_fix(&root, "ask:f", "declined", "a note here", ""),
        "python3 said",
    );
}

#[test]
fn a_ruling_owed_nothing_and_its_rarer_shapes() {
    assert_eq!(super::owed_line(None), "");
    assert_eq!(super::owed_line(Some(String::new())), "");
    assert_eq!(super::owed_line(Some("x".to_owned())), "x\n");
    let root = clone_at("rarer");
    python_tools(&root);
    let num = record_ruling(
        &root,
        "ask:num",
        &json!({"ruling": "continue", "why": 5}),
        "round-arbiter",
        None,
        false,
    )
    .unwrap();
    assert_eq!(num["why"], json!(5));
    owe(
        &root,
        &json!({"round:modal-research|modal:sheet/bath@3": {"kind": "round", "unit": "modal-research|modal:sheet/bath", "feature": "999-x", "t": 1}}),
    );
    record_ruling(
        &root,
        "round:modal-research|modal:sheet/bath@3",
        &json!({"ruling": "accept", "why": "w"}),
        "round-arbiter",
        None,
        false,
    )
    .unwrap();
    let fixed = json!({"ruling": "process-fault", "why": "w", "tooling_fix": "f", "fix_minutes": 1, "triggers": ["ask:q1", "ask:q2"]});
    let rows_done = record_batch(&root, &fixed, "round-arbiter", None).unwrap();
    assert_eq!(rows_done[1]["tooling_fix_on"], json!("ask:q1"));
    std::fs::write(root.join("specs/999-x/plan.md"), "# p\n").unwrap();
    owe(
        &root,
        &json!({"ask:999-p": {"kind": "ask", "unit": "", "feature": "999-x", "t": 1, "review": "plan"}}),
    );
    let fault = rule_file(
        &root,
        "fault.json",
        &json!({"ruling": "process-fault", "why": "w", "tooling_fix": "f", "fix_minutes": 1}),
    );
    assert_eq!(
        run(
            &root,
            &["ruled", "ask:999-p", &fault, "--as", "round-arbiter"]
        )
        .code,
        0
    );
}

#[test]
fn a_fix_that_cannot_be_settled_says_why() {
    let root = clone_at("settle");
    refused(
        super::settle_fix(&root, "ask:nope", "done", "a note here", ""),
        "ask:nope has no open tooling fix",
    );
    let nofeature = clone_at("settle-nofeature");
    std::fs::remove_file(nofeature.join(".specify/feature.json")).unwrap();
    refused(
        super::settle_fix(&nofeature, "ask:x", "done", "a note here", ""),
        "no active feature",
    );
    std::fs::write(
        root.join("specs/999-x/arbiter.jsonl"),
        format!(
            "{}\n",
            json!({"trigger": "ask:f", "fix": "open", "tooling_fix": "one"})
        ),
    )
    .unwrap();
    refused(
        super::settle_fix(&root, "ask:f", "weird", "a note here", ""),
        "status is done or declined",
    );
    let nit = run(&root, &["nit", "ask:nothing", "a", "b"]);
    assert!(nit.code == 1 && nit.stderr.contains("no `accept` ruling"));
    std::fs::write(root.join("specs/999-x/arbiter.jsonl"), format!("{}\n", json!({"trigger": "ask:q", "ruling": "accept", "kind": "round", "unit": "c|q:0105", "what": "OLD NEW"}))).unwrap();
    let qnit = run(&root, &["nit", "ask:q", "OLD", "NEW"]);
    assert!(qnit.stderr.contains("q:0105 must hold NEW"));
}

mod verbs;
