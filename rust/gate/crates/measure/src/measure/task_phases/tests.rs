//! Whose call, the phases and the skeleton over small event lists (the differential reads them over the real logs, `diff.py`).

use std::collections::{HashMap, HashSet};

use serde_json::{json, Value};

use super::*;

fn evs(list: &[Value]) -> Vec<Event> {
    list.iter()
        .map(|v| v.as_object().unwrap().clone())
        .collect()
}

fn at(hms: &str) -> String {
    format!("2026-11-01T{hms}Z")
}

fn t(hms: &str) -> f64 {
    super::super::events::ts(&at(hms)).unwrap()
}

#[test]
fn a_cohort_or_gate_run_is_measured() {
    for (e, want) in [
        (json!({"make": "cohort-landing"}), true),
        (json!({"make": "x", "cat": "gate"}), true),
        (json!({"make": "verify"}), true),
        (json!({"make": "quick"}), false),
        (json!({"cat": "gate"}), false),
    ] {
        assert_eq!(measured_run(e.as_object().unwrap()), want, "{e}");
    }
}

#[test]
fn a_subagent_call_is_told_by_its_transcript_hook_or_window() {
    let home = crate::checks::scratch("measure-phases-calls");
    let sub = home.join("p/s2/subagents");
    std::fs::create_dir_all(&sub).unwrap();
    std::fs::write(
        sub.join("agent-a1.jsonl"),
        r#"{"id": "toolu_1"} {"id":"toolu_1"}"#,
    )
    .unwrap();
    std::fs::write(sub.join("agent-a3.jsonl"), r#"{"id": "toolu_1"}"#).unwrap();
    std::fs::write(sub.join("other.txt"), "").unwrap();
    let (calls, found) = subagent_calls(&["s2", "", "s2", "none"].map(String::from), &home);
    assert_eq!(calls.get("toolu_1").map(String::as_str), Some("a1"));
    assert_eq!(found, HashSet::from(["a1".to_owned(), "a3".to_owned()]));
    let events = evs(&[
        json!({"t": at("08:00:00"), "sid": "s", "ev": "SubagentStart", "aid": "w1"}),
        json!({"t": at("08:00:01"), "sid": "s", "ev": "SubagentStart", "aid": "w1"}),
        json!({"t": at("08:00:02"), "sid": "s", "ev": "SubagentStart", "aid": "a1"}),
        json!({"t": at("08:00:03"), "sid": "s", "ev": "PreToolUse", "tool": "Read", "id": "toolu_1"}),
        json!({"t": at("08:00:04"), "sid": "s", "ev": "PreToolUse", "tool": "Read", "id": "n", "by": "z"}),
        json!({"t": at("08:00:05"), "sid": "s", "ev": "PreToolUse", "tool": "Read", "id": "m"}),
        json!({"t": at("08:00:06"), "sid": "s", "ev": "PreToolUse", "tool": "Agent", "id": "k"}),
        json!({"t": at("08:00:07"), "sid": "t", "ev": "PreToolUse", "tool": "Read", "id": "o"}),
        json!({"t": at("08:00:08"), "sid": "s", "ev": "SubagentStop", "aid": "w1"}),
        json!({"t": at("08:00:09"), "sid": "s", "ev": "SubagentStop", "aid": "a1"}),
        json!({"t": at("08:00:09"), "sid": "s", "ev": "SubagentStop", "aid": "never"}),
        json!({"t": at("08:00:09"), "sid": "s", "ev": "Stop", "aid": "", "tool": ""}),
        json!({"t": at("08:00:09"), "sid": "s", "ev": "UserPromptSubmit", "aid": "zz"}),
        json!({"t": at("08:00:09"), "sid": "s", "ev": "SubagentStop", "aid": "w9", "tool": "x"}),
    ]);
    let out = attribute(events, &calls, &found).unwrap();
    let marks: Vec<(String, String)> = out
        .iter()
        .map(|e| (or_s(e, "by"), or_s(e, "how")))
        .collect();
    assert_eq!(marks[3], ("a1".to_owned(), "transcript".to_owned()));
    assert_eq!(marks[4], ("z".to_owned(), "hook".to_owned()));
    assert_eq!(marks[5], ("w1".to_owned(), "window".to_owned()));
    assert_eq!(marks[6], (String::new(), String::new()));
    assert_eq!(marks[7], (String::new(), String::new()));
    let how = attribution(&out);
    assert_eq!(how.items().len(), 3);
    assert_eq!(session_events(&out).len(), 11);
    assert_eq!(call_counts(&out), (2, 3));
    let bad = evs(&[json!({"t": "x", "ev": "SubagentStart", "aid": "q"})]);
    assert!(attribute(bad, &HashMap::new(), &HashSet::new()).is_err());
    let bad = evs(&[json!({"t": "x", "ev": "PreToolUse", "tool": "Read"})]);
    assert!(attribute(bad, &HashMap::new(), &HashSet::new()).is_err());
}

fn day() -> Vec<Event> {
    evs(&[
        json!({"t": at("08:00:00"), "sid": "s", "ev": "PreToolUse", "tool": "Bash", "id": "b1"}),
        json!({"t": at("08:01:00"), "sid": "s", "ev": "PostToolUse", "tool": "Bash", "id": "b1", "make": "done", "cat": "gate", "ms": 60000}),
        json!({"t": at("08:02:00"), "sid": "s", "ev": "PreToolUse", "tool": "Agent", "id": "g", "agent": "spec-fidelity"}),
        json!({"t": at("08:02:01"), "sid": "s", "ev": "SubagentStart", "aid": "f", "agent": "spec-fidelity"}),
        json!({"t": at("08:02:30"), "sid": "s", "ev": "PreToolUse", "tool": "Read", "id": "r", "by": "f"}),
        json!({"t": at("08:10:00"), "sid": "s", "ev": "SubagentStop", "aid": "f", "agent": "spec-fidelity", "verdict": "BLOCKED"}),
        json!({"t": at("08:10:01"), "sid": "s", "ev": "PostToolUse", "tool": "Agent", "id": "g", "aid": "f"}),
        json!({"t": at("08:10:02"), "sid": "s", "ev": "PreToolUse", "tool": "Agent", "id": "h"}),
        json!({"t": at("08:10:03"), "sid": "s", "ev": "PostToolUse", "tool": "Agent", "id": "h", "aid": "nostop"}),
        json!({"t": at("08:10:04"), "sid": "s", "ev": "PostToolUse", "tool": "Agent", "id": "unknown"}),
        json!({"t": at("08:11:00"), "sid": "s", "ev": "SubagentStart", "aid": "q", "agent": "quote-check"}),
        json!({"t": at("08:11:30"), "sid": "s", "ev": "PostToolUse", "make": "cohort-x", "ms": "120000"}),
        json!({"t": at("08:11:40"), "sid": "s", "ev": "PostToolUse", "make": "verify"}),
        json!({"t": at("08:12:00"), "sid": "s", "ev": "Stop"}),
        json!({"t": at("08:20:00"), "sid": "s", "ev": "SubagentStop", "aid": "q", "agent": "quote-check"}),
        json!({"t": at("08:20:00"), "sid": "s", "ev": "SubagentStop", "aid": "q2"}),
        json!({"t": at("10:00:00"), "sid": "s", "ev": "SubagentStart", "aid": "r1", "agent": "round-arbiter"}),
        json!({"t": at("10:05:00"), "sid": "s", "ev": "SubagentStop", "aid": "r1", "agent": "round-arbiter"}),
        json!({"t": at("10:05:00"), "sid": "s", "ev": "UserPromptSubmit"}),
    ])
}

#[test]
fn runs_spans_and_gaps_are_read_from_the_events() {
    let e = day();
    let runs = subagent_runs(&e).unwrap();
    assert_eq!(runs.len(), 3);
    assert_eq!(runs[0].2, "spec-fidelity");
    assert_eq!(runs[0].3, "BLOCKED");
    let fg = foreground_spans(&e).unwrap();
    assert_eq!(
        fg,
        [(t("08:02:00"), t("08:10:01"), "spec-fidelity".to_owned())]
    );
    assert_eq!(in_span(t("08:05:00"), &fg), "spec-fidelity");
    assert_eq!(in_span(t("08:10:01"), &fg), "");
    assert_eq!(by_sid(&e).len(), 1);
    let g = gaps(&e).unwrap();
    let kinds: Vec<&str> = g.iter().map(|x| x.2.as_str()).collect();
    assert!(kinds.contains(&"idle") && kinds.contains(&"wait") && kinds.contains(&"work"));
    for bad in [
        json!([{"t": "x", "ev": "SubagentStart", "aid": "a"}]),
        json!([{"t": at("08:00:00"), "ev": "SubagentStart", "aid": "a"}, {"t": "x", "ev": "SubagentStop", "aid": "a", "agent": "k"}]),
        json!([{"t": "x", "ev": "SubagentStop", "aid": "a"}]),
        json!([{"t": "x", "ev": "PreToolUse", "tool": "Agent", "id": "g"}, {"t": at("08:00:00"), "ev": "PostToolUse", "tool": "Agent", "id": "g"}]),
        json!([{"t": "x", "sid": "s", "ev": "Stop"}, {"t": at("08:00:00"), "sid": "s", "ev": "Stop"}]),
    ] {
        let list = evs(bad.as_array().unwrap());
        assert!(
            subagent_runs(&list).is_err()
                || foreground_spans(&list).is_err()
                || gaps(&list).is_err()
        );
    }
    assert!(gaps(&evs(&[json!({"t": "x", "ev": "SubagentStop", "aid": "a"})])).is_err());
}

#[test]
fn a_task_splits_into_phases_and_a_skeleton() {
    let e = day();
    let p = Phases::new(&e).unwrap();
    let rows = p
        .rows(
            "T01",
            t("08:00:00"),
            t("10:10:00"),
            &["spec-fidelity", "round-arbiter"],
        )
        .unwrap();
    assert_eq!(
        rows,
        [
            "| T01 | 08:00-08:10 | spec-fidelity BLOCKED | 2 | 2 | 8 | 0 | spec-fidelity x1 (8 min) |",
            "| T01 | 08:10-10:05 | round-arbiter | 1 | 7 | 8 | 100 | quote-check x1, round-arbiter x1 (14 min) |",
            "| T01 | 10:05-10:10 | the tick or the last event | 0 | 0 | 0 | 0 | - |",
        ]
    );
    let plan = "### T01 part B (2026-11-01T08:05Z)\n#### T01 Approach (re-answered 2026-11-01T08:06:30Z)\n### T02 part B (2026-11-01T08:05Z)\n### T01 part B (2026-11-02T08:05Z)\n";
    let sk = p
        .skeleton("T01", t("08:00:00"), t("10:10:00"), plan, true)
        .unwrap();
    assert_eq!(
        sk,
        [
            "| T01 | 08:00 | started (`make task-start`) | |",
            "| T01 | 08:01 | `make done` (1 min) | |",
            "| T01 | 08:05 | part B written | |",
            "| T01 | 08:06 | Approach re-answered | |",
            "| T01 | 08:10 | spec-fidelity returned BLOCKED (8 min) | |",
            "| T01 | 08:11 | `make cohort-x` (2 min) | |",
            "| T01 | 08:11 | `make verify` (0 min) | |",
            "| T01 | 08:20 | quote-check returned (9 min) | |",
            "| T01 | 10:05 | round-arbiter returned (5 min) | |",
            "| T01 | 10:10 | ticked | |",
        ]
    );
    assert_eq!(
        p.skeleton("T01", t("09:00:00"), t("09:10:00"), "", false)
            .unwrap()
            .len(),
        1
    );
    assert!(p
        .skeleton(
            "T01",
            t("08:00:00"),
            t("10:10:00"),
            "### T01 part B (2026-13-01T08:05Z)",
            false
        )
        .is_err());
    let bad =
        evs(&[json!({"t": at("08:00:00"), "ev": "PostToolUse", "make": "verify", "ms": "x"})]);
    let p = Phases::new(&bad).unwrap();
    assert!(p.skeleton("T", 0.0, t("09:00:00"), "", false).is_err());
    let bad = evs(&[json!({"t": "x", "ev": "PostToolUse", "make": "verify"})]);
    assert!(Phases::new(&bad)
        .unwrap()
        .skeleton("T", 0.0, 1.0, "", false)
        .is_err());
    let bad = evs(&[json!({"t": "x", "ev": "PreToolUse"})]);
    assert!(Phases::new(&bad).unwrap().rows("T", 0.0, 1.0, &[]).is_err());
    let bad = evs(&[json!({"t": "x", "ev": "SubagentStop", "agent": "round-arbiter"})]);
    assert!(Phases::new(&bad)
        .unwrap()
        .rows("T", 0.0, 1.0, &["round-arbiter"])
        .is_err());
}
