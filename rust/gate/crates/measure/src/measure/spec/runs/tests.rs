//! The change's size from git, the full plans' reasons from the run log, and the triage price replayed over a scratch history.

use std::path::Path;
use std::process::Command;

use l7r_gate_core::record::testkit::put;
use serde_json::{json, Value};

use super::{change_size, finding, full_reasons, get, py_eq, triage_price, Index};

fn words(w: &[&str]) -> Vec<String> {
    w.iter().map(|s| (*s).to_owned()).collect()
}

/// `git args...` in `dir`, author and committer dated `date`.
fn git_at(dir: &Path, date: &str, args: &[&str]) -> String {
    let out = Command::new("git")
        .arg("-C")
        .arg(dir)
        .args(["-c", "user.name=t", "-c", "user.email=t@t"])
        .args(args)
        .env("GIT_AUTHOR_DATE", date)
        .env("GIT_COMMITTER_DATE", date)
        .output()
        .unwrap();
    assert!(out.status.success());
    String::from_utf8_lossy(&out.stdout).trim().to_owned()
}

fn commit(dir: &Path, date: &str) -> String {
    git_at(dir, date, &["add", "-A"]);
    git_at(dir, date, &["commit", "-qm", "c", "--allow-empty"]);
    git_at(dir, date, &["rev-parse", "--short", "HEAD"])
}

#[test]
fn the_change_is_counted_from_git_and_recorded() {
    let root = crate::checks::scratch("spec-change-size");
    git_at(&root, "2026-01-01T00:00:00", &["init", "-q"]);
    put(&root, "scripts/house-style-hooks.sh", "a\nb\n");
    put(&root, "scripts/other.sh", "1\n2\n");
    put(
        &root,
        "specs/239-measurable-guards-and-derived-figures/x",
        "",
    );
    commit(&root, "2026-01-01T00:00:00");
    git_at(&root, "2026-01-01T00:00:00", &["tag", "one"]);
    put(&root, "scripts/house-style-hooks.sh", "a\nB\nc\n");
    put(&root, "scripts/_hm_house.py", "x\n");
    put(&root, "scripts/other.sh", "1\n");
    commit(&root, "2026-01-02T00:00:00");
    let mut out = String::new();
    assert_eq!(
        change_size(&words(&["one", "HEAD", "--record"]), &root, &mut out),
        Ok(0)
    );
    assert_eq!(out, "one..HEAD\n  the hook and its module: +3 -1\n  all of scripts/:         +3 -2\nrecorded 2 figures in measurements.json\n");
    let rec: Value = serde_json::from_str(
        &std::fs::read_to_string(
            root.join("specs/239-measurable-guards-and-derived-figures/measurements.json"),
        )
        .unwrap(),
    )
    .unwrap();
    assert_eq!(rec["amendment-guard-lines-added"]["value"], 3);
    assert_eq!(
        rec["amendment-scripts-lines-added"]["command"],
        "scripts/gates/l7r-gate.sh measure spec 239 change-size one HEAD --record"
    );
    let mut out = String::new();
    assert_eq!(
        change_size(&words(&["nope", "HEAD"]), &root, &mut out),
        Ok(0)
    );
    assert_eq!(
        out,
        "nope..HEAD\n  the hook and its module: +0 -0\n  all of scripts/:         +0 -0\n"
    );
    assert_eq!(
        change_size(&words(&["one"]), &root, &mut String::new()),
        Err("IndexError: list index out of range".to_owned())
    );
}

#[test]
fn the_full_plans_are_counted_by_their_reason() {
    let root = crate::checks::scratch("spec-full-reasons");
    let mut out = String::new();
    assert_eq!(full_reasons(&root, &mut out), Ok(0));
    assert_eq!(out, "");
    let t = "a non-module file under tests/ changed: ";
    let e = "an engine file that is not Python changed: ";
    for (name, run) in [
        (
            "20261026a.json",
            json!({"target": "done", "plan": {"reason": format!("{t}tests/x.md")}}),
        ),
        (
            "20261026b.json",
            json!({"target": "done", "why": [format!("{e}pool/a.json"), 1.5]}),
        ),
        (
            "20261026c.json",
            json!({"target": "done", "plan": {"reason": format!("{e}pool/a.json")}}),
        ),
        (
            "20261026d.json",
            json!({"target": "quick", "plan": {"reason": format!("{t}tests/y.md")}}),
        ),
        (
            "20261026e.json",
            json!({"target": "done", "plan": {"reason": "python"}}),
        ),
        (
            "20261026f.json",
            json!({"target": "done", "plan": {"reason": format!("{t}tests/\u{fc}.md")}}),
        ),
        (
            "20261027a.json",
            json!({"target": "done", "plan": {"reason": format!("{t}tests/z.md")}}),
        ),
        (
            "20261026g.txt",
            json!({"target": "done", "plan": {"reason": format!("{t}tests/z.md")}}),
        ),
    ] {
        put(
            &root,
            &format!("dev/run-log/2026-10/{name}"),
            &run.to_string(),
        );
    }
    let mut out = String::new();
    assert_eq!(full_reasons(&root, &mut out), Ok(0));
    assert_eq!(
        out,
        format!("2 {e}pool/a.json\n1 {t}tests/x.md\n1 {t}tests/\n")
    );
    for (bad, why) in [("[1]", "AttributeError"), ("{", "JSONDecodeError")] {
        put(&root, "dev/run-log/2026-10/20261026z.json", bad);
        assert!(full_reasons(&root, &mut String::new())
            .unwrap_err()
            .starts_with(why));
    }
}

#[expect(
    clippy::needless_pass_by_value,
    reason = "a fixture built from `json!` values at each call"
)]
fn row(code: Value, pages: &str, rests: &str, verdict: Value) -> Value {
    json!({"code": code, "pages": pages, "rests": rests, "verdict": verdict})
}

#[test]
fn the_triage_route_is_replayed_over_the_window() {
    let root = crate::checks::scratch("spec-triage");
    git_at(&root, "2026-10-01T00:00:00", &["init", "-q"]);
    let index = |v: &Value| put(&root, "dev/claims-index.json", &v.to_string());
    let mut out = String::new();
    assert_eq!(triage_price(&root, &mut out), Ok(0));
    assert_eq!(out, "{}\n");
    put(&root, "README", "r");
    commit(&root, "2026-10-01T00:00:00");
    let before = json!({"a": row(json!("c"), "p", "r", json!("IN-STEP")), "b": row(json!("c"), "p", "r", Value::Null), "c": row(json!("c"), "p", "r", json!("IN-STEP")), "d": row(json!(1), "p", "r", json!(1)), "f": row(json!("c"), "p", "r", json!("DRIFTED")), "g": row(json!("c"), "p", "r", json!("IN-STEP")), "h": 0, "i": row(json!("c"), "p", "r", json!("IN-STEP"))});
    let after = json!({"a": row(json!("c"), "p2", "r", json!("DRIFTED")), "b": row(json!("c"), "p2", "r2", json!("MISLABELED")), "c": row(json!("c"), "p2", "r", json!("IN-STEP")), "d": row(json!(1.0), "p2", "r", json!(true)), "f": row(json!("c"), "p2", "r", json!("IN-STEP")), "g": row(json!("c2"), "p2", "r", json!("DRIFTED")), "e": row(json!("c"), "p", "r", json!("DRIFTED")), "h": row(json!("c"), "p", "r", json!("x")), "i": row(json!("c"), "p", "r", json!("IN-STEP"))});
    index(&before);
    commit(&root, "2026-10-05T00:00:00");
    index(&after);
    let finding_at = commit(&root, "2026-10-06T00:00:00");
    put(&root, "dev/claims-index.json", "not json");
    commit(&root, "2026-10-07T00:00:00");
    index(&before);
    commit(&root, "2026-10-08T00:00:00");
    index(&after);
    commit(&root, "2026-10-27T00:00:00");
    let mut out = String::new();
    assert_eq!(triage_price(&root, &mut out), Ok(0));
    assert_eq!(
        out,
        format!("{{'triage: new finding': 1, 'rests: new finding': 1, 'triage: re-judged, same verdict': 2}}\n  {finding_at} DRIFTED    a\n")
    );
    index(&json!({"a": row(json!("c"), "p3", "r", json!(["DRIFTED"]))}));
    commit(&root, "2026-10-09T00:00:00");
    assert_eq!(
        triage_price(&root, &mut String::new()),
        Err("TypeError: unhashable type".to_owned())
    );
    index(&json!({"a": [1]}));
    commit(&root, "2026-10-10T00:00:00");
    assert!(triage_price(&root, &mut String::new())
        .unwrap_err()
        .starts_with("AttributeError"));
    index(&json!([1]));
    commit(&root, "2026-10-11T00:00:00");
    assert!(triage_price(&root, &mut String::new())
        .unwrap_err()
        .starts_with("AttributeError"));
}

#[test]
fn the_index_reader_and_pythons_readings() {
    let root = crate::checks::scratch("spec-index");
    let mut none = Index {
        cat: None,
        kept: Vec::new(),
    };
    assert_eq!(*none.at("abc"), json!({}));
    assert_eq!(*none.at(""), json!({}));
    git_at(&root, "2026-10-01T00:00:00", &["init", "-q"]);
    let mut open = Index::new(&root);
    assert_eq!(
        *open.at("0000000000000000000000000000000000000000"),
        json!({})
    );
    for a in ["a", "b", "c", "d"] {
        assert_eq!(*open.at(a), json!({}));
    }
    assert_eq!(open.kept.len(), 3);
    assert!(py_eq(&json!(1), &json!(1.0)) && py_eq(&json!(true), &json!(1)));
    assert!(py_eq(&json!([1, {"a": 1}]), &json!([1.0, {"a": true}])));
    assert!(!py_eq(&json!([1]), &json!([1, 2])) && !py_eq(&json!({"a": 1}), &json!({"b": 1})));
    assert!(!py_eq(&json!({"a": 1}), &json!({"a": 1, "b": 2})) && !py_eq(&json!("1"), &json!(1)));
    assert!(py_eq(&Value::Null, &Value::Null) && !py_eq(&json!("a"), &json!("b")));
    assert_eq!(finding(&json!("MISLABELED")), Ok(true));
    assert_eq!(finding(&json!(1)), Ok(false));
    assert!(finding(&json!({})).is_err());
    assert_eq!(get(&json!({"a": 1}), "b"), Ok(&Value::Null));
    assert!(get(&json!(1), "a").is_err());
}
