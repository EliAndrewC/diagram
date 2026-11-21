//! The closing step's order (feature 451 T55): the decide notice on a temporary clone's log, the foreground refusal and its escape.

use serde_json::{json, Value};

use super::{closing_run, code_path, told, Told, TOKEN};

const ROOT: &str = "/c";

fn edit(t: &str, by: &str, path: &str) -> Value {
    json!({"t": t, "ev": "PostToolUse", "tool": "Edit", "id": format!("e{t}"), "by": by, "sid": "s", "path": path})
}

fn bash(t: &str, by: &str, id: &str, make: &str, bg: bool) -> [Value; 2] {
    let mut post = json!({"t": t, "ev": "PostToolUse", "tool": "Bash", "id": id, "by": by, "sid": "s", "make": make});
    if bg {
        post["bg"] = json!("b9");
    }
    [
        json!({"t": t, "ev": "PreToolUse", "tool": "Bash", "id": id, "by": by, "sid": "s", "make": make}),
        post,
    ]
}

/// A call's hook input: by the builder `by` (none: the main session), its command and whether it is backgrounded.
fn call(by: &str, cmd: &str, bg: bool) -> Value {
    let mut v = json!({"hook_event_name": "PreToolUse", "tool_name": "Bash", "session_id": "s", "tool_input": {"command": cmd}});
    if !by.is_empty() {
        v["agent_id"] = json!(by);
    }
    if bg {
        v["tool_input"]["run_in_background"] = json!(true);
    }
    v
}

/// What was said's text, "" for nothing.
fn said_text(n: Option<Told>) -> String {
    match n {
        Some(Told::Decide(t) | Told::Foreground(t) | Told::Escaped(t) | Told::NoReason(t)) => t,
        None => String::new(),
    }
}

/// The caller's filing: the feature and task its own call's line goes under.
fn t55() -> (String, Option<String>) {
    (
        "451-time-retro-and-efficiency".to_owned(),
        Some("T55".to_owned()),
    )
}

fn decide_said(lines: &[Value], by: &str) -> Option<Told> {
    told(
        &call(by, "make decide F=451 T=T55", false),
        &|| ROOT.to_owned(),
        &|| lines.to_vec(),
        &t55,
    )
}

#[test]
fn a_decide_after_a_code_edit_with_no_closing_checks_started_since_is_told_the_order() {
    let lines = vec![edit(
        "2026-11-21T10:00:00.000Z",
        "a1",
        "/c/rust/guard/src/x.rs",
    )];
    assert!(matches!(decide_said(&lines, "a1"), Some(Told::Decide(_))));
    let text = said_text(decide_said(&lines, "a1"));
    for want in [
        // the caller's own closing run (451 T86): a bare `make closing-checks` judges the whole clone, another task's red counted
        "start `make closing-checks T=T55 F=451` now",
        "run_in_background",
        "rust/guard/src/x.rs",
        "make decide",
        "make quick",
    ] {
        assert!(text.contains(want), "{want} in {text}");
    }
    // the main session's own edits are its own, a builder's not
    assert!(decide_said(&lines, "").is_none());
    let main = vec![
        json!({"t": "2026-11-21T10:00:00.000Z", "ev": "PostToolUse", "tool": "Write", "id": "w", "sid": "s", "path": "/c/Makefile"}),
    ];
    assert!(matches!(decide_said(&main, ""), Some(Told::Decide(_))));
    assert!(decide_said(&main, "a1").is_none());
}

#[test]
fn a_closing_checks_run_started_since_the_last_code_edit_silences_it() {
    let mut lines = vec![edit(
        "2026-11-21T10:00:00.000Z",
        "a1",
        "/c/rust/guard/src/x.rs",
    )];
    lines.extend(bash(
        "2026-11-21T10:01:00.000Z",
        "a1",
        "k1",
        "closing-checks",
        true,
    ));
    assert!(decide_said(&lines, "a1").is_none());
    // an edit after it owes another start
    lines.push(edit(
        "2026-11-21T10:02:00.000Z",
        "a1",
        "/c/tests/hooks/t.sh",
    ));
    assert!(decide_said(&lines, "a1").is_some());
    // another builder's start is not this one's
    lines.extend(bash(
        "2026-11-21T10:03:00.000Z",
        "b2",
        "k2",
        "closing-checks",
        true,
    ));
    assert!(decide_said(&lines, "a1").is_some());
    // a call another guard refused, its PreToolUse alone, started nothing
    lines.push(json!({"t": "2026-11-21T10:04:00.000Z", "ev": "PreToolUse", "tool": "Bash", "id": "k3", "by": "a1", "sid": "s", "make": "closing-checks"}));
    assert!(decide_said(&lines, "a1").is_some());
    lines.extend(bash(
        "2026-11-21T10:05:00.000Z",
        "a1",
        "k4",
        "closing-checks",
        false,
    ));
    assert!(decide_said(&lines, "a1").is_none());
    // a start chained after another target: the line's `makes` names it
    lines.push(edit("2026-11-21T10:06:00.000Z", "a1", "/c/Makefile"));
    let mut chained = bash("2026-11-21T10:07:00.000Z", "a1", "k5", "format", true);
    for l in &mut chained {
        l["makes"] = json!(["format", "closing-checks"]);
    }
    lines.extend(chained);
    assert!(decide_said(&lines, "a1").is_none());
}

/// A code edit filed under `task`, by the builder `by` (none: the main session).
fn edit_of(t: &str, by: &str, path: &str, task: &str) -> Value {
    let mut e = edit(t, by, path);
    e["task"] = json!(task);
    if let Some(o) = e.as_object_mut().filter(|_| by.is_empty()) {
        o.remove("by");
    }
    e
}

/// `make land`'s end line: the main session's, with no `by`.
fn landing(t: &str, landed: bool, tasks: &[&str]) -> Value {
    json!({"ev": "Phase", "src": "land", "step": "end", "t": t, "code": 0, "make": "land", "tasks": tasks, "landed": landed})
}

#[test]
fn an_edit_before_a_landing_of_its_task_is_landed_and_never_told() {
    // the finding (T64): the main session's Makefile edit filed under T12, T12 landed after it, told at every later decide
    let mut lines = vec![
        edit_of("2026-11-20T15:48:51.173Z", "", "/c/Makefile", "T12"),
        landing("2026-11-20T15:55:22.200Z", true, &["T12", "T17"]),
    ];
    assert!(decide_said(&lines, "").is_none());
    // a landing that went out for another task, or one refused, lands nothing of T12's
    for other in [
        landing("2026-11-20T15:55:22.200Z", true, &["T17"]),
        landing("2026-11-20T15:55:22.200Z", false, &["T12"]),
        json!({"ev": "Phase", "step": "end", "t": "2026-11-20T15:55:22.200Z", "tasks": ["T12"]}),
        json!({"ev": "Phase", "step": "start", "t": "2026-11-20T15:55:22.200Z", "tasks": ["T12"], "landed": true}),
    ] {
        let refused = vec![lines[0].clone(), other];
        assert!(matches!(decide_said(&refused, ""), Some(Told::Decide(_))));
    }
    // a code edit after the landing is unchecked again, and named
    lines.push(edit_of(
        "2026-11-21T07:00:00.000Z",
        "",
        "/c/rust/guard/src/y.rs",
        "T12",
    ));
    assert!(said_text(decide_said(&lines, "")).contains("rust/guard/src/y.rs"));
    // the notice reads back past a landed edit to the caller's last one unlanded: an earlier edit of a task not yet landed
    let back = vec![
        edit_of(
            "2026-11-20T15:00:00.000Z",
            "",
            "/c/rust/guard/src/z.rs",
            "T13",
        ),
        edit_of("2026-11-20T15:48:51.173Z", "", "/c/Makefile", "T12"),
        landing("2026-11-20T15:55:22.200Z", true, &["T12"]),
    ];
    let text = said_text(decide_said(&back, ""));
    assert!(text.contains("rust/guard/src/z.rs"), "{text}");
}

#[test]
fn a_builders_edit_is_landed_by_the_main_sessions_landing_of_its_task() {
    // every landing line is the main session's (`make land` runs there): a builder's edit of the task is landed by it too
    let lines = vec![
        edit_of(
            "2026-11-21T10:00:00.000Z",
            "a1",
            "/c/rust/guard/src/x.rs",
            "T64",
        ),
        landing("2026-11-21T10:30:00.000Z", true, &["T63", "T64"]),
    ];
    assert!(decide_said(&lines, "a1").is_none());
    // an edit with no task: no landing names it, so it is still told (the log's first day, before lines carried a task)
    let taskless = vec![
        edit("2026-11-21T10:00:00.000Z", "a1", "/c/rust/guard/src/x.rs"),
        landing("2026-11-21T10:30:00.000Z", true, &["T64"]),
    ];
    assert!(matches!(
        decide_said(&taskless, "a1"),
        Some(Told::Decide(_))
    ));
}

#[test]
fn a_plan_or_document_edit_is_not_code_and_no_edit_says_nothing() {
    assert!(decide_said(&[], "a1").is_none());
    for p in [
        "/c/specs/451-x/plan.md",
        "/c/docs/guards.md",
        "/c/.git/l7r-handoffs/T55-a1.md",
        "/tmp/x.rs",
        "/other/rust/x.rs",
    ] {
        assert!(!code_path(p, ROOT), "{p}");
        assert!(decide_said(&[edit("2026-11-21T10:00:00.000Z", "a1", p)], "a1").is_none());
    }
    for p in [
        "/c/Makefile",
        "/c/scripts/gates/closing-checks.sh",
        "/c/rust/guard/src/x.rs",
    ] {
        assert!(code_path(p, ROOT), "{p}");
    }
}

#[test]
fn a_foreground_closing_check_is_refused_naming_the_background_and_nothing_else_is_read() {
    let read = std::cell::Cell::new(0);
    let never = || -> Vec<Value> {
        read.set(read.get() + 1);
        Vec::new()
    };
    let root = || -> String {
        read.set(read.get() + 1);
        String::new()
    };
    // the caller's filing is asked only for what is said
    let unasked = || -> (String, Option<String>) {
        read.set(read.get() + 1);
        t55()
    };
    for (by, cmd) in [
        ("a1", "make static"),
        ("a1", "make hooks-test"),
        ("a1", "timeout 900 make hooks-test"),
        ("a1", "make closing-checks"),
        ("a1", "make rust-test CRATE=rust/guard && make static"),
        ("a1", "make static 2>&1 | tail -30"),
        // the main session's too: 451's log holds none of its, so no measured case stands it aside
        ("", "make hooks-test"),
        // the run count's escape is not this rule's
        (
            "a1",
            "STATIC_OK=\"the landing gate needs it\" make closing-checks",
        ),
    ] {
        let got = told(&call(by, cmd, false), &root, &never, &t55);
        assert!(matches!(got, Some(Told::Foreground(_))), "{cmd}");
        let text = said_text(got);
        for want in [
            "BLOCKED",
            "run_in_background: true",
            "`make closing-checks T=T55 F=451` runs make static",
            "FOREGROUND_OK=\"<reason>\"",
            "recorded",
        ] {
            assert!(text.contains(want), "{want} in {text}");
        }
        let quiet = told(&call(by, cmd, true), &root, &never, &unasked);
        assert!(quiet.is_none(), "{cmd}");
    }
    assert!(said_text(told(
        &call("a1", "make hooks-test", false),
        &root,
        &never,
        &t55
    ))
    .contains("`make hooks-test` in the foreground"));
    for cmd in [
        "make quick",
        "grep decide Makefile",
        "echo make static",
        "make rust-test CRATE=rust/guard",
    ] {
        assert!(told(&call("a1", cmd, false), &root, &never, &unasked).is_none());
    }
    assert_eq!(read.get(), 0);
    // the counters count: each read once by hand
    assert!(never().is_empty() && root().is_empty() && unasked().1.is_some());
    assert_eq!(read.get(), 3);
    assert_eq!(said_text(None), "");
}

#[test]
fn the_foreground_refusal_is_escaped_by_a_reason_and_refused_without_one() {
    let say = |cmd: &str| {
        told(
            &call("a1", cmd, false),
            &String::new,
            &Vec::<Value>::new,
            &t55,
        )
    };
    assert_eq!(
        say("FOREGROUND_OK=\"the next edit needs it\" make static"),
        Some(Told::Escaped("the next edit needs it".to_owned()))
    );
    assert_eq!(
        say("make hooks-test  # FOREGROUND_OK: the fix needs this result"),
        Some(Told::Escaped("the fix needs this result".to_owned()))
    );
    let bare = say("make static FOREGROUND_OK");
    assert!(matches!(&bare, Some(Told::NoReason(t)) if t.contains(TOKEN)));
    // a mention of the token in a quoted string or a search escapes nothing
    for cmd in [
        "echo \"FOREGROUND_OK=two words here\" && make static",
        "grep FOREGROUND_OK docs/guards.md; make static",
        // a closing check chained with a decide, either order: the refusal is judged first, for every command in the chain
        "make closing-checks && make decide F=451 T=T55",
        "make decide F=451 T=T55 && make static",
        "make hooks-test; make decide F=451 T=T55",
    ] {
        assert!(matches!(say(cmd), Some(Told::Foreground(_))), "{cmd}");
    }
    assert_eq!(
        say("FOREGROUND_OK=\"the next edit needs it\" make static && make decide F=451 T=T55"),
        Some(Told::Escaped("the next edit needs it".to_owned()))
    );
}

#[test]
fn the_closing_run_named_is_the_callers_task_and_feature_number() {
    // 451 T86: `make closing-checks T=<task> F=<feature>` judges the caller's own files; F= takes the feature's number
    assert_eq!(
        closing_run("451-time-retro-and-efficiency", Some("T86")),
        "make closing-checks T=T86 F=451"
    );
    assert_eq!(
        closing_run("449", Some("T12")),
        "make closing-checks T=T12 F=449"
    );
    // a call filed under no task, or outside any clone: the placeholders, never a bare whole-clone run
    assert_eq!(
        closing_run("451-time-retro-and-efficiency", None),
        "make closing-checks T=<your task> F=451"
    );
    assert_eq!(
        closing_run("", None),
        "make closing-checks T=<your task> F=<feature>"
    );
    // a feature with no number before its first dash is named whole
    assert_eq!(
        closing_run("unassigned", Some("T1")),
        "make closing-checks T=T1 F=unassigned"
    );
}
