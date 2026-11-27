//! Feature 451 T513: the main session's calls booked to the task their own tool calls name - the line's `names`, else the
//! transcript's call read the same way - never to the session's mark or to a builder's `Phase` line beside them; the rest counted
//! by why, from the window's start only.

use std::collections::{HashMap, HashSet};

use serde_json::json;

use super::super::events::Event;
use super::super::where_time::columns::spent::{Call, Tok};
use super::turns::{self, Unbooked};
use super::Key;

fn tok(out: f64) -> Tok {
    Tok {
        out,
        ..Tok::default()
    }
}

fn call(at: f64, uses: &[(&str, &[&str])]) -> Call {
    Call {
        at,
        tok: tok(1.0),
        uses: uses
            .iter()
            .map(|(id, n)| {
                (
                    (*id).to_owned(),
                    n.iter().map(|t| (*t).to_owned()).collect(),
                )
            })
            .collect(),
        model: String::new(),
    }
}

fn key(t: &str) -> Key {
    ("451-x".to_owned(), t.to_owned())
}

#[test]
fn a_session_call_books_to_the_task_its_own_tool_calls_name() {
    let stream: Vec<Event> = [
        // the writer's `names`, beside the mark `task` the line is filed under
        json!({"t": "x", "sid": "s", "ev": "PreToolUse", "id": "u1", "feature": "451-x", "task": "T99", "fallback": true, "names": ["T5", "T6"]}),
        // a line before the field: the transcript's call names its task
        json!({"t": "x", "sid": "s", "ev": "PreToolUse", "id": "u2", "feature": "451-x", "task": "T99"}),
        json!({"t": "x", "sid": "s", "ev": "PreToolUse", "id": "u3", "feature": "451-x", "task": "T99"}),
        // a builder's check run, sharing the session's id with no `by`: never a session call's
        json!({"t": "x", "sid": "s", "ev": "Phase", "id": "u4", "feature": "451-x", "task": "T7"}),
        // a builder's own call naming a task is no session line
        json!({"t": "x", "sid": "s", "ev": "PreToolUse", "id": "u5", "by": "B", "feature": "451-x", "names": ["T7"]}),
        json!({"t": "x", "sid": "s", "ev": "PreToolUse", "id": "u6", "feature": "451-x", "task": "T99", "names": ["T8"]}),
    ]
    .iter()
    .map(|v| v.as_object().unwrap().clone())
    .collect();
    let session = HashMap::from([(
        "s".to_owned(),
        vec![
            call(5.0, &[("u1", &["T1"])]),
            call(10.0, &[("u2", &["T5"])]),
            // the first tool call naming a task, the second; its line's names before the transcript's
            call(11.0, &[("u3", &[]), ("u1", &["T6"])]),
            call(12.0, &[]),
            call(13.0, &[("u4", &[]), ("u3", &[])]),
            call(14.0, &[("u5", &["T7"])]),
            call(15.0, &[("gone", &["T5"])]),
            call(16.0, &[("u6", &[])]),
            // before the window: booked where it names a task, never counted unbooked
            call(1.0, &[]),
        ],
    )]);
    let read = turns::Read {
        calls: &HashMap::new(),
        tokens: &HashMap::new(),
        session: &session,
        models: &HashMap::new(),
        paged: &HashSet::new(),
    };
    let ends = HashMap::from([(key("T8"), 15.5)]);
    let (got, unbooked, _) = turns::of(&stream, &[], &read, (&ends, 2.0));
    assert_eq!(got[&key("T5")].session, 3);
    assert_eq!(got[&key("T5")].session_tok, tok(3.0));
    for k in ["T99", "T7", "T1", "T6", "T8"] {
        assert!(!got.contains_key(&key(k)), "{k}");
    }
    let want = Unbooked {
        calls: 5,
        tok: tok(5.0),
        replies: 1,
        unnamed: 1,
        unlogged: 2,
        carried: 1,
    };
    assert_eq!(unbooked, want);
}

/// Feature 451 T514: a bundle's tasks - one pool tree handed out for both - each read the bundle's counts, make runs, turns and
/// tokens whole, marked, where the second read nothing; so do a task built inside another's tree (no builder of its own) and the
/// tasks it shares a commit with; tasks sharing a commit that each had a builder, a task in no bundle, and another feature's task of
/// the same id read their own.
#[test]
fn a_bundles_tasks_each_read_the_bundles_counts_turns_and_tokens_whole() {
    use super::super::where_time::columns::ran::{Kind, Ran};
    use super::beside::{self, Extra};
    use super::book::Ledger;
    use super::held::Hold;
    let hold = |tasks: &[&str]| Hold {
        from: 0.0,
        until: f64::INFINITY,
        tree: "t".to_owned(),
        feature: "451".to_owned(),
        tasks: tasks.iter().map(|t| (*t).to_owned()).collect(),
    };
    let other: Key = ("449-y".to_owned(), "T1".to_owned());
    let landed: Vec<(f64, Key)> = [
        key("T1"),
        key("T2"),
        key("T3"),
        key("T5"),
        key("T6"),
        key("T7"),
        other.clone(),
    ]
    .into_iter()
    .map(|k| (0.0, k))
    .collect();
    let holds = [hold(&["T1", "T2"]), hold(&["T2", "T4"]), hold(&["T3"])];
    let turns = super::turns::Turns {
        builders: 89,
        builders_tok: tok(100.0),
        ..super::turns::Turns::default()
    };
    let turned = std::collections::HashMap::from([
        (key("T1"), turns),
        (key("T3"), turns),
        (key("T6"), turns),
        (key("T7"), turns),
        (other.clone(), turns),
    ]);
    let shared = |with: &str| super::sized::Size {
        shared: vec![with.to_owned()],
        ..super::sized::Size::default()
    };
    let sizes = std::collections::HashMap::from([
        (key("T3"), shared("T5")),
        (key("T5"), shared("T3")),
        (key("T6"), shared("T7")),
        (key("T7"), shared("T6")),
    ]);
    let bundles = beside::bundles(&holds, &landed, (&sizes, &turned));
    assert_eq!(bundles[&key("T1")], [key("T1"), key("T2")]);
    assert_eq!(bundles[&key("T2")], [key("T2"), key("T1"), key("T4")]);
    assert_eq!(bundles[&key("T3")], [key("T3"), key("T5")]);
    assert_eq!(bundles[&key("T5")], [key("T5"), key("T3")]);
    for k in [key("T6"), key("T7"), other.clone()] {
        assert!(!bundles.contains_key(&k), "{k:?}");
    }
    let mut whole = Ledger::default();
    let ran = |step: &str| Ran {
        kind: Kind::UnitTest,
        step: step.to_owned(),
        t0: 0.0,
        t1: 60.0,
        tree: "t".to_owned(),
        make: "rust-test".to_owned(),
        crates: String::new(),
        key: key("T1"),
        said: None,
    };
    whole.ran.insert(key("T1"), vec![ran("test"), ran("test")]);
    whole
        .runs
        .insert((key("T1"), "make rust-test".to_owned()), 2);
    let x = Extra {
        turns: turned,
        bundles,
        sizes,
        ..Extra::default()
    };
    let mut out = String::new();
    beside::table(&mut out, &whole, &landed, &x);
    let row = |t: &str, mark: &str| {
        format!("| 451-x {t}{mark} | 0 | +0 -0 | +0 -0 | +0 -0 | 2, 1.0 min each | 0 | 0 (0 of 1.0 s or more) | 2 | 89 | 0 | 0 | 0.1k (100.0%) |")
    };
    let mark = " (bundle T1 T2: its counts, turns and tokens the bundle's, whole)";
    assert!(out.contains(&row("T1", mark)), "{out}");
    assert!(out.contains(&row("T2", &mark.replace("T1 T2:", "T2 T1 T4:"))));
    assert!(
        out.contains(
            "| 451-x T6 | 0 (shared with T7) | +0 -0 | +0 -0 | +0 -0 | 0 | 0 | 0 (0 of 1.0 s or more) | 0 | 89 |"
        )
    );
    let line = beside::line(&whole, &key("T2"), &[], &x);
    assert!(line.starts_with(&format!(
        "Beside its minutes (451 T512){}: ",
        mark.replace("T1 T2:", "T2 T1 T4:")
    )));
    assert!(line.contains(": 2 unit-test runs, 1.0 min each,"), "{line}");
    let built_inside =
        " (bundle T5 T3: its counts, turns and tokens the bundle's, whole) | 0 (shared with T3) |";
    assert!(out.contains(built_inside), "{out}");
}
