#![expect(clippy::float_cmp, reason = "the fixture's exact epoch values")]

use std::path::{Path, PathBuf};

use serde_json::{json, Value};

use super::{
    aside, asked_feature, batch_triggers, blocking, blocking_for, cascade, cascade_state, closed,
    continues, epoch, epoch_iso, feature_dir, feature_dir_from, iso_seconds, lapsed, owed,
    pop_owed, py_text, refusal, reversal, round_no, rulings, spec_dirs, trip, trip_as, unit_of,
    Who,
};
use crate::checks::testkit::clone_at;
use crate::checks::{common_dir, OWED};

fn ruled(root: &Path, rows: &[Value]) {
    let body: String = rows.iter().map(|r| r.to_string() + "\n").collect();
    std::fs::write(
        root.join("specs/999-x/arbiter.jsonl"),
        format!("{body}not json\n{{\"no\": \"trigger\"}}\n"),
    )
    .unwrap();
}

fn owe(root: &Path, map: &Value) {
    std::fs::write(common_dir(root).join(OWED), map.to_string()).unwrap();
}

#[test]
fn the_feature_is_read_in_its_order() {
    let d = clone_at("feature");
    std::fs::create_dir_all(d.join("specs/414-a")).unwrap();
    std::fs::create_dir_all(d.join("specs/415-b")).unwrap();
    std::fs::create_dir_all(d.join("specs/415-c")).unwrap();
    assert_eq!(
        asked_feature(&d, "ask:414-round3"),
        Some(d.join("specs/414-a"))
    );
    assert_eq!(
        asked_feature(&d, "round:x|plan:414-a#T1@3"),
        Some(d.join("specs/414-a"))
    );
    assert_eq!(
        asked_feature(&d, "round:x|spec:414-a#1@3"),
        Some(d.join("specs/414-a"))
    );
    // a spec review's round names its feature as the review-round guard writes it (451 T179: its ruling is filed there, so read there)
    assert_eq!(
        asked_feature(&d, "round:spec-fidelity|414-a#1@6"),
        Some(d.join("specs/414-a"))
    );
    assert_eq!(asked_feature(&d, "ask:415-x"), None);
    assert_eq!(asked_feature(&d, "ask:9x"), None);
    assert_eq!(
        feature_dir_from(&d, "ask:414-q", "", ""),
        Some(d.join("specs/414-a"))
    );
    assert_eq!(
        feature_dir_from(&d, "", "specs/mine/", ""),
        Some(d.join("specs/mine"))
    );
    assert_eq!(
        feature_dir_from(&d, "", "", "/414-a/"),
        Some(d.join("specs/414-a"))
    );
    assert_eq!(
        feature_dir_from(&d, "ask:999-z", "", "no-such"),
        Some(d.join("specs/999-x"))
    );
    std::fs::remove_file(d.join(".specify/feature.json")).unwrap();
    assert_eq!(feature_dir_from(&d, "", "", ""), None);
    std::fs::write(d.join(".specify/feature.json"), "{}").unwrap();
    assert_eq!(feature_dir_from(&d, "", "", ""), None);
    std::fs::write(d.join(".specify/feature.json"), "x").unwrap();
    assert_eq!(feature_dir(&d, ""), None);
    assert_eq!(
        spec_dirs(Path::new("/nonexistent"), "4"),
        Vec::<PathBuf>::new()
    );
}

#[test]
fn the_feature_pointers_are_the_test_threads_own() {
    // feature 451 T32: `feature_dir` reads its two pointers through `shared::env`, the test thread's own map - so a session's
    // exported `L7R_FEATURE_DIRECTORY` (a page session's) never reaches a test, and a test that names one sees exactly it
    use crate::env::{set, unset};
    let d = clone_at("feature-env");
    std::fs::create_dir_all(d.join("specs/414-a")).unwrap();
    std::fs::write(d.join(".specify/feature.json"), "x").unwrap();
    assert_eq!(feature_dir(&d, ""), None);
    set("SPECIFY_FEATURE", "414-a");
    assert_eq!(feature_dir(&d, ""), Some(d.join("specs/414-a")));
    set("L7R_FEATURE_DIRECTORY", "specs/mine/");
    assert_eq!(feature_dir(&d, ""), Some(d.join("specs/mine")));
    unset("L7R_FEATURE_DIRECTORY");
    unset("SPECIFY_FEATURE");
    assert_eq!(feature_dir(&d, ""), None);
}

#[test]
fn rulings_and_owed_triggers_read_back() {
    let d = clone_at("rulings");
    assert!(owed(&d).is_empty());
    std::fs::write(common_dir(&d).join(OWED), "[]").unwrap();
    assert!(owed(&d).is_empty());
    ruled(
        &d,
        &[
            json!({"trigger": "round:c|q:1@3", "ruling": "continue"}),
            json!({"trigger": "round:c|q:1@5", "ruling": "continue"}),
            json!({"trigger": "round:c|q:2@3", "ruling": "accept", "content_key": "k1"}),
            json!({"trigger": "round:c|q:3@3", "ruling": "process-fault"}),
            json!({"trigger": 7, "ruling": "continue"}),
        ],
    );
    let r = rulings(&d, "");
    assert_eq!(r.len(), 5);
    assert!(r.contains_key("7"));
    assert!(rulings(&clone_at("no-feature-file"), "ask:1").is_empty());
    let nofeature = clone_at("nofeature");
    std::fs::remove_file(nofeature.join(".specify/feature.json")).unwrap();
    assert!(rulings(&nofeature, "").is_empty());
    assert_eq!(py_text(&json!("x")), "x");
    assert_eq!(py_text(&json!(3)), "3");
    assert_eq!(continues(&d, "round:c|q:1@", 0), 2);
    assert_eq!(continues(&d, "round:c|q:1@", 3), 1);
    assert_eq!(closed(&d, "round:c|q:2@", None), "accept");
    assert_eq!(closed(&d, "round:c|q:2@", Some("k1")), "accept");
    assert_eq!(closed(&d, "round:c|q:2@", Some("other")), "");
    assert_eq!(closed(&d, "round:c|q:2@", Some("")), "accept");
    assert_eq!(closed(&d, "round:c|q:3@", Some("k")), "process-fault");
    assert_eq!(closed(&d, "round:c|q:9@", None), "");
    assert_eq!(lapsed(&d, "round:c|q:2@", Some("other")), 1);
    assert_eq!(lapsed(&d, "round:c|q:2@", None), 0);
    // 451 T240: a plan round's rulings are read from the feature its prefix names, where `make arbiter-ruled` files them, not the
    // active feature's (the clone's pointer names 999-x)
    std::fs::create_dir_all(d.join("specs/386-y")).unwrap();
    std::fs::write(
        d.join("specs/386-y/arbiter.jsonl"),
        "{\"trigger\": \"round:spec-fidelity|plan:386-y#T14@3\", \"ruling\": \"continue\"}\n{\"trigger\": \"round:spec-fidelity|plan:386-y#T15@3\", \"ruling\": \"accept\"}\n",
    )
    .unwrap();
    assert_eq!(continues(&d, "round:spec-fidelity|plan:386-y#T14@", 0), 1);
    assert_eq!(
        closed(&d, "round:spec-fidelity|plan:386-y#T15@", None),
        "accept"
    );
}

#[test]
fn a_held_gate_and_a_batch_are_told_apart() {
    let d = clone_at("blocking");
    owe(
        &d,
        &json!({
            "round:c|q:1@3": {"kind": "round", "unit": "c|q:1", "feature": "999-x"},
            "round:d|q:2@3": {"kind": "round", "unit": "d|q:2", "feature": "999-x"},
            "round:spec-fidelity|999-x#1@6": {"kind": "round", "unit": "s", "feature": "999-x"},
            "round:e|q:5@3": {"kind": "round", "unit": "e|q:5", "feature": "000-other"},
            "reversal:a": {"kind": "reversal", "unit": "x"},
            "cascade@1": {"kind": "cascade", "feature": ""},
            "red-gate@t": {"kind": "red-gate", "feature": "000-other"},
            "red-gate@u": {"kind": "red-gate", "feature": "999-x"},
        }),
    );
    assert_eq!(
        aside(&d),
        [
            "red-gate@t (feature 000-other)",
            "round:e|q:5@3 (feature 000-other)"
        ]
    );
    // a record check's round follows its unit (451 T227): another feature's holds that unit's dispatch and joins the batch
    owe(
        &d,
        &json!({"round:record-format|q:7@3": {"kind": "round", "unit": "record-format|q:7", "feature": "000-other"}}),
    );
    assert!(aside(&d).is_empty());
    assert_eq!(
        blocking(&d, "record-format|q:7", false),
        ["round:record-format|q:7@3"]
    );
    assert_eq!(batch_triggers(&d, &[]), ["round:record-format|q:7@3"]);
    owe(
        &d,
        &json!({
            "round:c|q:1@3": {"kind": "round", "unit": "c|q:1", "feature": "999-x"},
            "round:d|q:2@3": {"kind": "round", "unit": "d|q:2", "feature": "999-x"},
            "round:spec-fidelity|999-x#1@6": {"kind": "round", "unit": "s", "feature": "999-x"},
            "round:e|q:5@3": {"kind": "round", "unit": "e|q:5", "feature": "000-other"},
            "reversal:a": {"kind": "reversal", "unit": "x"},
            "cascade@1": {"kind": "cascade", "feature": ""},
            "red-gate@t": {"kind": "red-gate", "feature": "000-other"},
            "red-gate@u": {"kind": "red-gate", "feature": "999-x"},
        }),
    );
    assert_eq!(
        blocking(&d, "c|q:1", false),
        ["cascade@1", "reversal:a", "round:c|q:1@3"]
    );
    assert_eq!(blocking(&d, "", true), ["red-gate@u"]);
    let batch = batch_triggers(
        &d,
        &[
            "round:x@1".to_owned(),
            "round:spec-fidelity|x".to_owned(),
            "other".to_owned(),
        ],
    );
    assert_eq!(batch, ["round:c|q:1@3", "round:d|q:2@3", "round:x@1"]);
    assert_eq!(refusal(&[], Some(&d)), "");
    let one = refusal(&["cascade@1".to_owned()], Some(&d));
    assert!(
        one.contains("a tripwire is owed its ruling first: make arbiter-bundle")
            && one.contains("TRIGGER=\"cascade@1\"")
    );
    let many = refusal(&batch, Some(&d));
    assert!(many.starts_with("3 round triggers are owed together ("));
    assert!(refusal(&batch, None).starts_with("a tripwire"));
    let lone = refusal(&["reversal:a".to_owned()], None);
    assert!(lone.starts_with("a tripwire"));
    let nofeature = clone_at("orphan");
    std::fs::remove_file(nofeature.join(".specify/feature.json")).unwrap();
    owe(
        &nofeature,
        &json!({"x": {"kind": "round", "feature": "000-z"}}),
    );
    assert!(aside(&nofeature).is_empty());
    assert_eq!(aside_of_numeric(), "n (feature 3)");
}

fn aside_of_numeric() -> String {
    let d = clone_at("numeric");
    owe(&d, &json!({"n": {"feature": 3}}));
    aside(&d).remove(0)
}

#[test]
fn a_reversal_and_a_cascade_read_as_python_does() {
    let evs = vec![
        json!({"ev": "PreToolUse", "tool": "Edit", "path": "/f", "old": "A"}),
        json!({"ev": "Other", "tool": "Edit", "path": "/f", "old": "Z"}),
        json!({"ev": "PreToolUse", "tool": "Edit", "path": "/g", "old": "B"}),
        json!({"ev": "PreToolUse", "tool": "Edit", "path": "/f"}),
    ];
    assert!(reversal(&evs, "/f", "B", "A"));
    assert!(!reversal(&evs, "/f", "A", "A"));
    assert!(!reversal(&evs, "/f", "B", ""));
    assert!(!reversal(&evs, "/f", "B", "Z"));
    assert!(reversal(&evs, "/f", "B", "None"));
    assert!(cascade(10, 1, 0));
    assert!(!cascade(9, 1, 0));
    assert!(!cascade(10, 20, 0));
    assert!(!cascade(12, 1, 5));
    assert!(cascade(20, 0, 5));
}

#[test]
fn dates_read_as_strptime_and_fromisoformat_do() {
    assert_eq!(epoch("1970-01-02T00:00:01Z"), 86401.0);
    assert_eq!(epoch("2024-02-29T00:00:00Z"), 1_709_164_800.0);
    assert_eq!(epoch("2023-02-29T00:00:00Z"), 0.0);
    assert_eq!(epoch("nope"), 0.0);
    assert_eq!(epoch("2024-13-01T00:00:00Z"), 0.0);
    assert_eq!(epoch("2024-01-01T24:00:00Z"), 0.0);
    assert_eq!(epoch("2024-01-01T00:60:00Z"), 0.0);
    assert_eq!(epoch("2024-00-01T00:00:00Z"), 0.0);
    assert_eq!(epoch("1900-01-01T00:00:00Z"), -2_208_988_800.0);
    assert_eq!(epoch_iso("2024-01-01T00:00:00Z"), 1_704_067_200.0);
    assert_eq!(
        epoch_iso("2024-01-01T00:00:00+05:30"),
        1_704_067_200.0 - 19800.0
    );
    assert_eq!(
        epoch_iso("2024-01-01T00:00:00-0100"),
        1_704_067_200.0 + 3600.0
    );
    assert_eq!(epoch_iso("2024-01-01T00:00:00.5"), 1_704_067_200.5);
    assert_eq!(epoch_iso("2024-01-01"), 1_704_067_200.0);
    assert_eq!(epoch_iso("x"), 0.0);
    assert_eq!(epoch_iso("2024-13-01"), 0.0);
    assert_eq!(iso_seconds("1970-01-01T00:00:00"), Some(0.0));
    assert_eq!(iso_seconds("x"), None);
    assert_eq!(iso_seconds("1970-01-01T00:00:01Z"), Some(1.0));
    assert_eq!(
        epoch_iso("2024-01-01T00:00:00+05"),
        1_704_067_200.0 - 18000.0
    );
}

#[test]
fn names_and_the_cascade_state_are_read_off_triggers() {
    assert_eq!(round_no("round:a|b@7"), 7);
    assert_eq!(round_no("round:a|b"), 0);
    assert_eq!(round_no("x@y"), 0);
    assert_eq!(unit_of("round:a|b@7"), "a|b");
    assert_eq!(unit_of("round:a|b"), "a|b");
    assert_eq!(unit_of("round:x"), "");
    assert_eq!(unit_of("ask:a|b@1"), "");
    let d = clone_at("cascade");
    ruled(
        &d,
        &[
            json!({"trigger": "cascade@1", "ruling": "continue", "dispatches": 12, "utc": "2026-01-02T00:00:00Z"}),
            json!({"trigger": "cascade@2", "ruling": "accept", "utc": "2020-01-02T00:00:00Z"}),
        ],
    );
    assert_eq!(
        cascade_state(&d, 1_735_689_600.0),
        ("cascade@3".to_owned(), 12)
    );
    assert_eq!(
        cascade_state(&d, 1_900_000_000.0),
        ("cascade@3".to_owned(), 0)
    );
}

#[test]
fn a_trigger_is_recorded_once_under_its_lock() {
    let d = clone_at("trip");
    ruled(
        &d,
        &[json!({"trigger": "round:r|s@3", "ruling": "continue"})],
    );
    assert!(!trip(
        &d,
        "round:r|s@3",
        "round",
        "r|s",
        "d",
        &json!(1.5),
        ""
    ));
    assert!(trip(
        &d,
        "cascade@1",
        "cascade",
        "",
        "12 check dispatches over 3 changed lines",
        &json!(1.5),
        ""
    ));
    assert!(!trip(
        &d,
        "cascade@1",
        "cascade",
        "",
        "again",
        &json!(2.5),
        ""
    ));
    assert!(trip(
        &d,
        "ask:spec-q",
        "ask",
        "",
        "why",
        &Value::Null,
        "spec"
    ));
    let all = owed(&d);
    assert_eq!(
        all["cascade@1"],
        json!({"detail": "12 check dispatches over 3 changed lines", "dispatches": 12, "feature": "999-x", "kind": "cascade", "t": 1.5, "unit": ""})
    );
    assert_eq!(all["ask:spec-q"]["review"], json!("spec"));
    assert!(all["ask:spec-q"]["t"].as_f64().unwrap() > 1.0);
    pop_owed(&common_dir(&d), "cascade@1").unwrap();
    assert!(!owed(&d).contains_key("cascade@1"));
    pop_owed(&common_dir(&d), "missing").unwrap();
    assert!(pop_owed(Path::new("/proc/nonexistent/x"), "a").is_err());
    // RED FIRST (451 T179): a trigger no feature resolves is refused at filing, never filed as feature "", which every feature's
    // dispatches read as their own - the mirror's `reversal:...context_cap_hooks.rs` held every builder for days (observed 2026-11-23)
    let orphan = clone_at("trip-orphan");
    std::fs::remove_file(orphan.join(".specify/feature.json")).unwrap();
    assert!(!trip(&orphan, "x", "k", "", "d", &json!(0), ""));
    assert!(!owed(&orphan).contains_key("x"));
    // ...but a reversal resolves its feature from the feature the event log filed its Edit under
    let who = Who { sid: "s", by: "" };
    assert!(trip_as(
        &orphan,
        "reversal:/f",
        "reversal",
        "/f",
        "d",
        who,
        "451-x"
    ));
    assert_eq!(owed(&orphan)["reversal:/f"]["feature"], json!("451-x"));
    assert!(!trip_as(
        &orphan,
        "reversal:/g",
        "reversal",
        "/g",
        "d",
        who,
        ""
    ));
    assert!(!owed(&orphan).contains_key("reversal:/g"));
    std::fs::remove_file(common_dir(&d).join("arbiter-owed.json")).ok();
    assert!(!trip(
        Path::new("/proc/nonexistent-l7r"),
        "x",
        "k",
        "",
        "d",
        &json!(0),
        ""
    ));
}

#[test]
fn a_reversal_holds_only_the_dispatches_of_the_session_and_builder_that_put_it_back() {
    // 449 arbiter fix (451's rulings on reversal:<file>, 2026-11-22): a put-back by one builder refused every builder in the clone
    let d = clone_at("reversal-who");
    let b1 = Who {
        sid: "s1",
        by: "b1",
    };
    assert!(trip_as(
        &d,
        "reversal:/f",
        "reversal",
        "/f",
        "A -> B -> A",
        b1,
        ""
    ));
    assert!(!trip_as(
        &d,
        "reversal:/f",
        "reversal",
        "/f",
        "again",
        b1,
        ""
    ));
    assert!(trip_as(
        &d,
        "reversal:/g",
        "reversal",
        "/g",
        "A -> B -> A",
        Who { sid: "s1", by: "" },
        ""
    ));
    assert!(trip_as(
        &d,
        "reversal:/h",
        "reversal",
        "/h",
        "A -> B -> A",
        Who::default(),
        ""
    ));
    let rows = owed(&d);
    assert_eq!(
        (
            rows["reversal:/f"]["sid"].as_str(),
            rows["reversal:/f"]["by"].as_str()
        ),
        (Some("s1"), Some("b1"))
    );
    assert!(rows["reversal:/g"].get("by").is_none() && rows["reversal:/h"].get("sid").is_none());
    // its own builder is held; the session's own put-back holds the session; an authorless row holds everyone, as before
    assert_eq!(blocking_for(&d, "", b1), ["reversal:/f", "reversal:/h"]);
    assert_eq!(
        blocking_for(&d, "", Who { sid: "s1", by: "" }),
        ["reversal:/g", "reversal:/h"]
    );
    // another builder of the same session, and another session's builder of the same id, pass
    assert_eq!(
        blocking_for(
            &d,
            "",
            Who {
                sid: "s1",
                by: "b2"
            }
        ),
        ["reversal:/h"]
    );
    assert_eq!(
        blocking_for(
            &d,
            "",
            Who {
                sid: "s2",
                by: "b1"
            }
        ),
        ["reversal:/h"]
    );
    // an asker the call does not know (the gate's read) is held by all of them
    assert_eq!(
        blocking(&d, "", false),
        ["reversal:/f", "reversal:/g", "reversal:/h"]
    );
}

/// 451 T170: a refusal's list of triggers reached a session at 1,358 characters; past the first few it names the file holding them all.
#[test]
fn a_long_list_of_triggers_names_its_first_few_and_the_file_holding_them_all() {
    let d = clone_at("many-triggers");
    let many: Vec<String> = (1..=12)
        .map(|i| format!("reversal:/c/rust/f{i}.rs"))
        .collect();
    let said = super::refusal_unbatched(&many, &d);
    assert!(said.contains("reversal:/c/rust/f2.rs, and 10 more: `cat "));
    assert!(!said.contains("f3.rs") && said.contains("ARBITER_OK"));
    let kept = said
        .split("more: `cat ")
        .nth(1)
        .unwrap()
        .split('`')
        .next()
        .unwrap();
    assert_eq!(
        std::fs::read_to_string(kept).unwrap(),
        many.join("\n") + "\n"
    );
    assert!(super::refusal(&many, None).contains("f12.rs"));
}
