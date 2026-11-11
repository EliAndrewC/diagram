//! The hourly checkpoint on scratch repositories: the switch, the clock, the waits and idle gaps, the hold, the dispatch refusal, the
//! opening and the close.

use std::path::Path;

use serde_json::{json, Value};

use super::super::tests::{events, feature, map, put, repo};
use super::*;

/// Worked from `secs` ago to a minute ago, an event every ten minutes: no idle gap.
fn worked(root: &Path, secs: i64) {
    let mut rows: Vec<(i64, &str, bool)> = Vec::new();
    let mut ago = secs;
    while ago > 60 {
        rows.push((ago, "PreToolUse", false));
        ago -= 600;
    }
    rows.push((60, "PreToolUse", false));
    events(root, "900-x", &rows);
}

fn clock_of(root: &Path) -> Value {
    serde_json::from_str(&std::fs::read_to_string(root.join(".git").join(CLOCK)).unwrap()).unwrap()
}

fn cp(root: &Path, a: &[&str]) -> Reply {
    let mut all: Vec<String> = a.iter().map(|s| (*s).to_owned()).collect();
    all.extend(["--root".to_owned(), root.to_string_lossy().into_owned()]);
    cli(&all)
}

#[test]
fn the_switch_suspends_and_resumes_with_a_reason() {
    let r = repo("switch");
    assert!(suspended(&r).is_empty());
    let off = cp(&r, &["switch", "off", "--why", "a test reason"]);
    // 7140 s of gap, idle
    // 7200 s less a 3000 s wait and 540 s idle
    // an admitted dispatch marks the message
    // the same message's later dispatch
    assert_eq!(
        (off.code, off.stdout.as_str()),
        (0, "step-back: suspended - a test reason\n")
    );
    let sw = suspended(&r);
    assert_eq!(
        (sw["who"].clone(), sw["why"].clone()),
        (json!("T Tester"), json!("a test reason"))
    );
    let on = cp(&r, &["switch", "on", "--why", "  resume it  "]);
    assert_eq!(on.stdout, "step-back: resumed - resume it\n");
    assert!(suspended(&r).is_empty());
    let short = cp(&r, &["switch", "off", "--why", "one"]);
    assert_eq!(
        (short.code, short.stderr.as_str()),
        (
            2,
            "step-back: make step-back-off|step-back-on REASON=\"<why, two words or more>\"\n"
        )
    );
    assert_eq!(cp(&r, &["switch", "--why", "two words"]).code, 2);
    let nogit = super::super::tests::dir("who");
    assert_eq!(
        throw(&nogit, "on", "two words", 0.0).unwrap()["utc"],
        json!("1970-01-01T00:00:00Z")
    );
}

#[test]
fn the_state_counts_the_hour_less_the_waits_and_the_idle_gaps() {
    let r = repo("state");
    assert_eq!(
        Value::Object(state(&r, None)),
        json!({"feature": "", "due": false})
    );
    feature(&r, "900-x", "- [ ] T1\n");
    assert_eq!(state(&r, None)["due"], json!(false), "no event log");
    events(
        &r,
        "900-x",
        &[(7200, "PreToolUse", false), (60, "PreToolUse", false)],
    );
    let st = state(&r, None);
    assert_eq!(
        (st["due"].clone(), st["hour"].clone(), st["open"].clone()),
        (json!(false), json!(1), json!(""))
    );
    worked(&r, 7200);
    assert_eq!(state(&r, None)["due"], json!(true));
    // a wait on the GM: from a Stop to his next prompt; a background agent's stop does not end it, the session's own act does
    events(
        &r,
        "900-x",
        &[
            (7200, "PreToolUse", false),
            (6000, "Stop", false),
            (5000, "SubagentStop", false),
            (4000, "Stop", false),
            (3000, "UserPromptSubmit", true),
            (2900, "PreToolUse", false),
            (2800, "Stop", false),
            (2700, "UserPromptSubmit", false),
            (2000, "UserPromptSubmit", true),
            (1900, "Stop", false),
            (1800, "PreToolUse", false),
            (60, "Other", false),
        ],
    );
    put(
        &r,
        ".git/l7r-events/900-x.jsonl",
        &(std::fs::read_to_string(r.join(".git/l7r-events/900-x.jsonl")).unwrap()
            + "not json\n[1]\n"),
    );
    let st = state(&r, None);
    assert_eq!(st["due"], json!(true));
    assert!((gm_waits(&r, "900-x", 0.0, now()) - 3000.0).abs() < 2.0);
    assert!((idle(&r, "900-x", 0.0, now()) - 540.0).abs() < 2.0);
    assert!(
        gm_waits(&r, "nolog", 0.0, 1.0).abs() < 1e-9 && idle(&r, "nolog", 0.0, 1.0).abs() < 1e-9
    );
    let nogit = super::super::tests::dir("events");
    assert!(events_of(&nogit).is_empty());
    // the clock's own fields
    put(
        &r,
        ".git/glyph-clock.json",
        r#"{"900-x": {"checkpoint_at": 5, "checkpoints": 2, "checkpoint_trigger": "hour:900-x@3", "checkpoint_units": ["u"], "units_since": 7}}"#,
    );
    let st = state(&r, None);
    assert_eq!(
        (
            st["hour"].clone(),
            st["open"].clone(),
            st["units"].clone(),
            st["units_since"].clone()
        ),
        (json!(3), json!("hour:900-x@3"), json!(["u"]), json!(7.0))
    );
    put(
        &r,
        "dev/step-back.json",
        r#"{"state": "off", "why": "w w", "who": "x", "utc": "u"}"#,
    );
    let st = state(&r, None);
    assert_eq!(
        (st["suspended"].clone(), st["open"].clone()),
        (json!(true), json!(""))
    );
    put(&r, ".git/glyph-clock.json", r#"{"900-x": 4}"#);
    assert_eq!(state(&r, None)["hour"], json!(1));
}

fn events_of(root: &Path) -> Vec<(f64, Value)> {
    events_log(root, "x")
}

fn events_log(root: &Path, feature: &str) -> Vec<(f64, Value)> {
    super::events(root, feature)
}

#[test]
fn the_hold_names_what_the_checkpoint_owes() {
    let r = repo("hold");
    assert_eq!(hold(&r, None), "");
    map(&r, "pool", "m", &["well"]);
    feature(&r, "900-x", "- [ ] T1\n");
    worked(&r, 7200);
    assert!(hold(&r, None).starts_with("the feature has run an hour since its last checkpoint"));
    put(&r, "dev/step-back.json", r#"{"state": "off"}"#);
    assert_eq!(hold(&r, None), "");
    std::fs::remove_file(r.join("dev/step-back.json")).unwrap();
    put(
        &r,
        ".git/glyph-clock.json",
        r#"{"900-x": {"checkpoint_trigger": "hour:900-x@2"}}"#,
    );
    assert!(hold(&r, None).contains("(/tmp/l7r-check/step-back-900-x-2/MANIFEST.md)"));
    let t = int_of(now());
    put(&r, ".git/glyph-clock.json", &json!({"900-x": {"checkpoint_at": t, "checkpoint_units": ["settlement-review--m", "gone"], "units_since": t - 60}}).to_string());
    assert_eq!(hold(&r, None), "the last checkpoint owed 1 review unit(s) not yet dispatched: settlement-review--m - `make verify` writes one prompt per unit; dispatch each on a green gate (feature 383)");
    put(&r, ".git/key", "K");
    put(
        &r,
        ".git/review-verdicts/settlement-review--m.json",
        r#"{"verdict": "PASS", "engine_key": "K"}"#,
    );
    assert_eq!(hold(&r, None), "", "answered at the tree's engine key");
    std::fs::remove_file(r.join(".git/review-verdicts/settlement-review--m.json")).unwrap();
    put(
        &r,
        ".git/pairing-state.json",
        &json!({"dispatched": {"settlement-review--m": {"at": t}}}).to_string(),
    );
    assert_eq!(hold(&r, None), "", "dispatched since it opened");
    put(
        &r,
        ".git/glyph-clock.json",
        &json!({"900-x": {"checkpoint_at": t, "checkpoint_units": [], "units_since": t}})
            .to_string(),
    );
    assert_eq!(hold(&r, None), "");
    assert_eq!(cp(&r, &["hold"]).code, 0);
}

#[test]
fn past_the_hour_a_gate_or_a_dispatch_is_refused_until_the_step_back() {
    let r = repo("due");
    feature(&r, "900-x", "- [ ] T1\n");
    let t = now();
    assert_eq!(due(&r, "Agent", "x", t), "");
    assert!(r.join(".git").join(ADMITTED).is_file());
    worked(&r, 7200);
    assert_eq!(due(&r, "Agent", "round-arbiter", t), "");
    assert_eq!(due(&r, "Agent", "x", t + 1.0), "");
    assert!(due(&r, "Agent", "x", t + 60.0).starts_with("the feature's hour is up"));
    assert!(due(&r, "Bash", "", t).starts_with("the feature's hour is up"));
    put(&r, ".git/checkpoint-admitted", "nonsense\n");
    assert!(due(&r, "Agent", "x", t).starts_with("the feature's hour is up"));
    let refused = cp(&r, &["due", "--tool", "Bash"]);
    assert_eq!(refused.code, 1);
    put(
        &r,
        ".git/glyph-clock.json",
        r#"{"900-x": {"checkpoint_trigger": "hour:900-x@1"}}"#,
    );
    assert_eq!(due(&r, "Bash", "", t), "", "the step-back is open");
    let nogit = super::super::tests::dir("due-nogit");
    assert_eq!(due(&nogit, "Agent", "x", t), "");
}

#[test]
fn the_hour_opens_once_and_its_ruling_closes_it() {
    let r = repo("open");
    map(&r, "pool", "m", &["well"]);
    let opened = |exported: &str| open_checkpoint(&r, now(), exported);
    assert_eq!(opened("").unwrap_err(), "the checkpoint is not due - the feature's next hour is up at never (no feature or event log)");
    feature(&r, "900-x", "- [ ] T1\n");
    events(&r, "900-x", &[(600, "PreToolUse", false)]);
    let not = opened("").unwrap_err();
    assert!(
        not.starts_with("the checkpoint is not due - the feature's next hour is up at ")
            && not.ends_with(" s")
    );
    put(&r, "specs/901-y/x", "");
    assert_eq!(opened("901-y/").unwrap_err(), ".specify/feature.json names 900-x but this session works 901-y: run `make use-feature F=901` first");
    assert_eq!(misaligned(&r, "999-none"), "");
    assert_eq!(misaligned(&r, "900-x"), "");
    put(
        &r,
        "dev/step-back.json",
        r#"{"state": "off", "why": "w w", "utc": "u"}"#,
    );
    assert_eq!(opened("").unwrap_err(), "the hourly step-back is suspended (None, u: w w) - make step-back-on REASON=\"<why>\" resumes it (feature 405 T43)");
    std::fs::remove_file(r.join("dev/step-back.json")).unwrap();
    worked(&r, 7200);
    assert_eq!(opened("").unwrap(), "hour:900-x@1");
    let mine = clock_of(&r)["900-x"].clone();
    assert_eq!(
        (
            mine["checkpoint_trigger"].clone(),
            mine["checkpoint_units"].clone()
        ),
        (
            json!("hour:900-x@1"),
            json!(["settlement-review--m", "glyph-check--well--m"])
        )
    );
    let owed: Value =
        serde_json::from_str(&std::fs::read_to_string(r.join(".git/arbiter-owed.json")).unwrap())
            .unwrap();
    assert!(owed.get("hour:900-x@1").is_some());
    assert_eq!(opened("").unwrap(), "hour:900-x@1", "opened once");
    assert_eq!(cp(&r, &["open"]).stdout, "hour:900-x@1\n");
    let at = mine["checkpoint_open_at"].clone();
    close_checkpoint(&r, "hour:900-x@1");
    let mine = clock_of(&r)["900-x"].clone();
    assert_eq!(
        (
            mine["checkpoint_at"].clone(),
            mine["checkpoints"].clone(),
            mine.get("checkpoint_trigger").is_none()
        ),
        (at, json!(1), true)
    );
    // a second close of a trigger nothing holds changes nothing; with no open time it closes at now
    put(
        &r,
        ".git/glyph-clock.json",
        r#"{"900-x": {"checkpoint_trigger": "hour:900-x@2", "checkpoints": 1}, "other": 3, "y": {"checkpoint_trigger": "z"}}"#,
    );
    close_checkpoint(&r, "hour:900-x@2");
    assert!(clock_of(&r)["900-x"]["checkpoint_at"].as_i64().unwrap() > 1_000_000_000);
    let no = cp(&r, &["open"]);
    assert_eq!(no.code, 1);
    let nogit = super::super::tests::dir("close-nogit");
    close_checkpoint(&nogit, "x");
}

#[test]
fn the_command_line_reads_as_argparse_did() {
    let r = repo("cli");
    assert_eq!(cp(&r, &["nope"]).code, 2);
    assert_eq!(cp(&r, &["switch", "maybe"]).code, 2);
    assert_eq!(cli(&[]).code, 2);
    let status = cp(&r, &["status"]);
    assert_eq!(
        status.stdout,
        "{\n \"feature\": \"\",\n \"due\": false\n}\n"
    );
    let elsewhere = cli(&["status".to_owned(), "--root".to_owned(), "/".to_owned()]);
    assert_eq!(elsewhere.code, 0);
}
