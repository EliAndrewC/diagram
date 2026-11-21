//! The closing step's order (feature 451 T55): the decide notice on a temporary clone's log, the foreground refusal and its escape.

use serde_json::{json, Value};

use super::{code_path, told, Told, TOKEN};

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

fn decide_said(lines: &[Value], by: &str) -> Option<Told> {
    told(
        &call(by, "make decide F=451 T=T55", false),
        &|| ROOT.to_owned(),
        &|| lines.to_vec(),
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
        "make closing-checks",
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
        let got = told(&call(by, cmd, false), &root, &never);
        assert!(matches!(got, Some(Told::Foreground(_))), "{cmd}");
        let text = said_text(got);
        for want in [
            "BLOCKED",
            "run_in_background: true",
            "make closing-checks",
            "FOREGROUND_OK=\"<reason>\"",
            "recorded",
        ] {
            assert!(text.contains(want), "{want} in {text}");
        }
        assert!(told(&call(by, cmd, true), &root, &never).is_none(), "{cmd}");
    }
    assert!(
        said_text(told(&call("a1", "make hooks-test", false), &root, &never))
            .contains("`make hooks-test` in the foreground")
    );
    for cmd in [
        "make quick",
        "grep decide Makefile",
        "echo make static",
        "make rust-test CRATE=rust/guard",
    ] {
        assert!(told(&call("a1", cmd, false), &root, &never).is_none());
    }
    assert_eq!(read.get(), 0);
    // the counters count: each read once by hand
    assert!(never().is_empty() && root().is_empty());
    assert_eq!(read.get(), 2);
    assert_eq!(said_text(None), "");
}

#[test]
fn the_foreground_refusal_is_escaped_by_a_reason_and_refused_without_one() {
    let say = |cmd: &str| told(&call("a1", cmd, false), &String::new, &Vec::<Value>::new);
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
