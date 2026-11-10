use std::path::{Path, PathBuf};
use std::sync::atomic::{AtomicU64, Ordering};

use serde_json::{json, Value};

use super::{
    batch_plan, cli, cli_in, fix_hold, open_fixes, py_repr, record_batch, record_ruling,
    spec_body_sha, spec_ruled, spec_verdict, unit_ruled, Stop,
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

fn refused<T: std::fmt::Debug>(result: Result<T, Stop>, words: &str) {
    let Err(Stop::Refused(why)) = result else {
        unreachable!("{result:?}")
    };
    assert!(why.contains(words), "{why}");
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
        Err(Stop::Refused(why)) => {
            assert!(why.contains("already ruled: round:a|q:1@3, round:b|q:2@3"));
        }
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

const FAKE_RECORD_OWED: &str =
    "def answer(root, check, result, q='', kind=''):\n    return ['u:' + check]\n";
const FAKE_GM_REVIEW: &str = "from pathlib import Path\ndef question(d, text, source, when):\n    Path(d, 'gm-question.txt').write_text(text + '|' + source + '|' + when)\n";
const FAKE_CHECKPOINT: &str = "from pathlib import Path\ndef close_checkpoint(root, trigger):\n    Path(root, 'closed-checkpoint.txt').write_text(trigger)\n";

fn python_tools(root: &Path) {
    let scripts = root.join("scripts");
    for (rel, body) in [
        ("record/record_owed.py", FAKE_RECORD_OWED),
        ("gm_review.py", FAKE_GM_REVIEW),
        ("reviews/checkpoint.py", FAKE_CHECKPOINT),
        (
            "reviews/review_prereq.py",
            "import sys\nprint('ck-' + sys.argv[sys.argv.index('--map') + 1])\n",
        ),
        (
            "record/claims.py",
            "import sys\nprint('claims accepted', sys.argv[sys.argv.index('--keys') + 1])\n",
        ),
    ] {
        std::fs::create_dir_all(scripts.join(rel).parent().unwrap()).unwrap();
        std::fs::write(scripts.join(rel), body).unwrap();
    }
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
    assert_eq!(row["content_key"], json!("ck-q:0105"));
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
    assert_eq!(
        std::fs::read_to_string(root.join("closed-checkpoint.txt")).unwrap(),
        "hour:999-x@1"
    );
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
    // a content-key ruling written without its key may be recorded again, the rekey
    let before = rows(&root).len();
    std::fs::write(
        root.join("specs/999-x/arbiter.jsonl"),
        format!(
            "{}\n",
            json!({"trigger": "round:c|u@3", "ruling": "accept", "kind": "round", "unit": "c|u"})
        ),
    )
    .unwrap();
    let rekeyed =
        record_ruling(&root, "round:c|u@3", &accept, "round-arbiter", None, false).unwrap();
    assert_eq!(rekeyed["content_key"], json!("ck-u"));
    assert!(before >= 1);
    refused(
        record_ruling(&root, "round:c|u@3", &accept, "round-arbiter", None, false),
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
        claims.stdout.contains("claims accepted a;b"),
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
fn every_verb_answers_on_a_clone() {
    let root = clone_at("cli");
    assert_eq!(cli(&["bogus".to_owned()]).code, 2);
    assert_eq!(run(&root, &["bogus"]).code, 2);
    assert_eq!(run(&root, &[]).code, 2);
    assert_eq!(run(&root, &["gate-held"]).code, 0);
    owe(
        &root,
        &json!({"red-gate@t": {"kind": "red-gate", "feature": "999-x"}}),
    );
    let held = run(&root, &["gate-held"]);
    assert_eq!(held.code, 1);
    assert!(held.stderr.starts_with("make done: refused - a tripwire"));
    let dir_text = root.join("specs/999-x").to_string_lossy().into_owned();
    assert_eq!(run(&root, &["spec-verdict", &dir_text]).code, 1);
    assert_eq!(run(&root, &["spec-ruled", &dir_text]).code, 1);
    assert_eq!(run(&root, &["unit-ruled", "u", "c"]).code, 1);
    assert_eq!(run(&root, &["ask", "has space", "two words here"]).code, 2);
    assert_eq!(run(&root, &["ask", "ok-1", "short"]).code, 2);
    assert_eq!(
        run(&root, &["ask", "ok-1", "two words here", "wrong"]).code,
        2
    );
    let asked = run(&root, &["ask", "ok-1", "two words here", "spec"]);
    assert!(asked.code == 0 && asked.stdout.contains("(REVIEW=spec: an accept stands"));
    let hint = run(&root, &["ask", "ok-2", "a plan review question"]);
    assert!(hint.stdout.contains("arbiter-ask: hint"));
    assert_eq!(
        run(&root, &["ask", "ok-3", "two words here", "claims:a"]).code,
        0
    );
    let plain = run(&root, &["ask", "ok-4", "two words here"]);
    assert!(!plain.stdout.contains("hint"));
    std::fs::write(
        root.join("rule.json"),
        format!(
            r#"{{"ruling": "continue", "why": "a colo{}r fix", "x": 1, "y": null}}"#,
            "u"
        ),
    )
    .unwrap();
    let rule = root.join("rule.json").to_string_lossy().into_owned();
    let bad = root.join("bad.json");
    std::fs::write(&bad, "nope").unwrap();
    let bad = bad.to_string_lossy().into_owned();
    let wrong = run(&root, &["ruled", "ask:ok-4", &rule, "--as", "main"]);
    assert!(wrong.code == 2 && wrong.stderr.starts_with("arbiter-ruled: declined"));
    assert_eq!(
        run(
            &root,
            &[
                "ruled",
                "ask:ok-4",
                "/no/such.json",
                "--as",
                "round-arbiter"
            ]
        )
        .code,
        1
    );
    assert_eq!(
        run(&root, &["ruled", "ask:ok-4", &bad, "--as", "round-arbiter"]).code,
        1
    );
    let ruled = run(
        &root,
        &["ruled", "ask:ok-4", &rule, "--as", "round-arbiter"],
    );
    assert!(
        ruled.code == 0
            && ruled
                .stdout
                .starts_with("arbiter-ruled: ask:ok-4 - continue (binding;"),
        "{}",
        ruled.stderr
    );
    assert!(rows(&root)[0]["why"].as_str().unwrap().contains("color"));
    assert_eq!(run(&root, &["ask", "ok-4", "two words here"]).code, 1);
    assert_eq!(
        run(&root, &["ruled-batch", &bad, "--as", "round-arbiter"]).code,
        1
    );
    assert_eq!(run(&root, &["ruled-batch", &rule, "--as", "main"]).code, 1);
    assert_eq!(
        run(
            &root,
            &["ruled", "ask:ok-3", &rule, "--as", "round-arbiter"]
        )
        .code,
        0
    );
}

fn committed(root: &Path, rel: &str) {
    let run_git = |args: &[&str]| {
        assert!(std::process::Command::new("git")
            .arg("-C")
            .arg(root)
            .args(args)
            .status()
            .unwrap()
            .success());
    };
    run_git(&["add", rel]);
    run_git(&[
        "-c",
        "user.name=t",
        "-c",
        "user.email=t@t",
        "commit",
        "-q",
        "-m",
        "x",
    ]);
}

#[test]
#[expect(
    clippy::too_many_lines,
    reason = "one fixture walked through every path a settled fix can take"
)]
fn fixes_are_settled_and_nits_answered() {
    let root = clone_at("fixes-cli");
    python_tools(&root);
    let d = root.join("specs/999-x");
    let fix_row = |t: &str, f: &str| {
        format!(
            "{}\n",
            json!({"trigger": t, "fix": "open", "tooling_fix": f})
        )
    };
    std::fs::write(
        d.join("arbiter.jsonl"),
        fix_row("ask:f1", "one") + &fix_row("hour:999-x@2", "two"),
    )
    .unwrap();
    let none = run(&root, &["fix", "done", "ask:none", "a note here"]);
    assert!(
        none.code == 1
            && none.stderr.contains("no open tooling fix: ask:none")
            && none.stderr.contains("open now: ask:f1, hour:999-x@2"),
        "{}",
        none.stderr
    );
    assert!(run(&root, &["fix", "done", "", "a note here"])
        .stderr
        .contains("(no ID)"));
    assert_eq!(run(&root, &["fix", "done", "ask:f1", "x"]).code, 1);
    let notest = run(
        &root,
        &["fix", "done", "ask:f1", "a note here", "tests/none.sh"],
    );
    assert!(
        notest
            .stderr
            .contains("TEST=tests/none.sh is not a file under tests/"),
        "{}",
        notest.stderr
    );
    assert!(run(&root, &["fix", "done", "ask:f1", "a note here"])
        .stderr
        .contains("TEST=<none>"));
    std::fs::create_dir_all(root.join("tests")).unwrap();
    std::fs::write(root.join("tests/t.sh"), "x").unwrap();
    let not_main = run(
        &root,
        &["fix", "done", "ask:f1", "a note here", "tests/t.sh"],
    );
    assert!(
        not_main.stderr.contains("is not on main as it is here"),
        "{}",
        not_main.stderr
    );
    committed(&root, "tests/t.sh");
    // a landed copy of the test settles it; the origin ref is the fixture's main
    assert!(std::process::Command::new("git")
        .arg("-C")
        .arg(&root)
        .args(["update-ref", "refs/remotes/origin/main", "HEAD"])
        .status()
        .unwrap()
        .success());
    let done = run(
        &root,
        &["fix", "done", "ask:f1", "a note here", "tests/t.sh"],
    );
    assert!(
        done.code == 0 && done.stdout.contains("1 fix(es) settled - ask:f1"),
        "{}",
        done.stderr
    );
    assert_eq!(open_fixes(&d).len(), 1);
    let declined_fix = run(
        &root,
        &[
            "fix",
            "declined",
            "hour:999-x@2",
            "this overhauls a process",
        ],
    );
    assert!(
        declined_fix.code == 0
            && declined_fix
                .stdout
                .contains("each a question owed escalation-check"),
        "{}",
        declined_fix.stderr
    );
    assert!(std::fs::read_to_string(d.join("gm-question.txt"))
        .unwrap()
        .contains("Declined because"));
    let nofeature = clone_at("no-active");
    std::fs::remove_file(nofeature.join(".specify/feature.json")).unwrap();
    assert!(run(&nofeature, &["fix", "done", "ask:none", "a note here"])
        .stderr
        .contains("the active feature (none)"));
    let nit_root = clone_at("nit");
    python_tools(&nit_root);
    let modal = nit_root.join("l7r/diagram/interactive/assets/modals/sheet/bath.md");
    std::fs::create_dir_all(modal.parent().unwrap()).unwrap();
    std::fs::write(&modal, "the NEW words\n").unwrap();
    let rid = "round:modal-form|modal:sheet/bath@3";
    std::fs::write(nit_root.join("specs/999-x/arbiter.jsonl"), format!("{}\n", json!({"trigger": rid, "ruling": "accept", "kind": "round", "unit": "modal-form|modal:sheet/bath", "what": "make OLD into NEW"}))).unwrap();
    let not_quoted = run(&nit_root, &["nit", rid, "zzz", "NEW"]);
    assert!(not_quoted.stderr.contains("must quote both OLD and NEW"));
    let unmade = run(&nit_root, &["nit", rid, "NEW", "OLD"]);
    assert!(
        unmade.stderr.contains("must hold NEW and no longer OLD"),
        "{}",
        unmade.stderr
    );
    let answered = run(&nit_root, &["nit", rid, "OLD", "NEW"]);
    assert!(
        answered.code == 0
            && answered
                .stdout
                .contains("1 unit(s) answered at today's words - u:modal-form"),
        "{}",
        answered.stderr
    );
    std::fs::remove_file(nit_root.join("scripts/record/record_owed.py")).unwrap();
    let none_owed = run(&nit_root, &["nit", rid, "OLD", "NEW"]);
    assert!(
        none_owed.stdout.contains("0 unit(s) answered") && none_owed.stdout.contains("none owed")
    );
    std::env::set_var("ARBITER_FIX_ENGINE", "1");
    let engine = clone_at("engine");
    std::fs::write(
        engine.join("specs/999-x/arbiter.jsonl"),
        format!(
            "{}\n",
            json!({"trigger": "ask:e1", "fix": "open", "tooling_fix": "e"})
        ),
    )
    .unwrap();
    std::fs::create_dir_all(engine.join("tests")).unwrap();
    std::fs::write(engine.join("tests/e.sh"), "x").unwrap();
    committed(&engine, "tests/e.sh");
    let e = run(
        &engine,
        &["fix", "done", "ask:e1", "an engine note", "tests/e.sh"],
    );
    std::env::remove_var("ARBITER_FIX_ENGINE");
    assert_eq!(e.code, 0, "{}", e.stderr);
    assert!(
        std::fs::read_to_string(engine.join("specs/999-x/arbiter.jsonl"))
            .unwrap()
            .contains("(an engine fix")
    );
}
