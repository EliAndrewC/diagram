use serde_json::{json, Value};

use super::{run, Answer, Event, Guard, Reply};
use crate::shared::session::Session;

fn bash(command: &str) -> Event {
    Event {
        name: "PreToolUse".to_owned(),
        input: json!({"tool_name": "Bash", "tool_input": {"command": command}}),
    }
}

fn refuse(_: &Event, _: &Session) -> Vec<Answer> {
    vec![Answer::Refuse("no".to_owned())]
}
fn refuse_too(_: &Event, _: &Session) -> Vec<Answer> {
    vec![Answer::Refuse("nor this".to_owned())]
}
fn upper(e: &Event, _: &Session) -> Vec<Answer> {
    let c = e.input["tool_input"]["command"]
        .as_str()
        .unwrap_or_default()
        .to_uppercase();
    vec![Answer::Rewrite(json!({ "command": c }))]
}
fn suffix(e: &Event, _: &Session) -> Vec<Answer> {
    let c = e.input["tool_input"]["command"]
        .as_str()
        .unwrap_or_default();
    vec![Answer::Rewrite(json!({ "command": format!("{c} !") }))]
}
fn note(_: &Event, _: &Session) -> Vec<Answer> {
    vec![Answer::Notice("a notice".to_owned())]
}
fn note_too(_: &Event, _: &Session) -> Vec<Answer> {
    vec![Answer::Notice("another".to_owned())]
}
fn hold(_: &Event, _: &Session) -> Vec<Answer> {
    vec![Answer::StopBlock("held".to_owned())]
}
fn allow(_: &Event, _: &Session) -> Vec<Answer> {
    Vec::new()
}

fn guard(decide: fn(&Event, &Session) -> Vec<Answer>) -> Guard {
    Guard {
        name: "g",
        events: &["PreToolUse", "Stop"],
        matcher: "Bash|Edit",
        decide,
    }
}

fn out(r: &Reply) -> Value {
    serde_json::from_str(&r.stdout).unwrap()
}

#[test]
fn no_guard_allows_with_no_output() {
    let none = Reply {
        stdout: String::new(),
        stderr: String::new(),
        code: 0,
    };
    assert_eq!(run(&mut bash("ls"), &[]), none);
    assert_eq!(run(&mut bash("ls"), &[guard(allow)]), none);
}

#[test]
fn every_refusal_is_reported_and_wins() {
    let r = run(
        &mut bash("ls"),
        &[guard(note), guard(refuse), guard(upper), guard(refuse_too)],
    );
    assert_eq!(
        (r.code, r.stderr.as_str(), r.stdout.as_str()),
        (2, "no\n\nnor this", "")
    );
}

#[test]
fn rewrites_apply_in_order_and_a_later_guard_sees_the_earlier() {
    let r = run(&mut bash("ls"), &[guard(upper), guard(suffix)]);
    let want = json!({"hookSpecificOutput": {"hookEventName": "PreToolUse", "updatedInput": {"command": "LS !"}}});
    assert_eq!(out(&r), want);
}

#[test]
fn notices_join_and_ride_with_a_rewrite() {
    let r = run(
        &mut bash("ls"),
        &[guard(note), guard(upper), guard(note_too)],
    );
    let o = out(&r);
    assert_eq!(
        o["hookSpecificOutput"]["additionalContext"],
        "a notice\n\nanother"
    );
    assert_eq!(
        o["hookSpecificOutput"]["updatedInput"],
        json!({"command": "LS"})
    );
}

#[test]
fn a_stop_block_joins_its_reasons() {
    let mut e = Event {
        name: "Stop".to_owned(),
        input: json!({}),
    };
    let one = Guard {
        name: "s",
        events: &["Stop"],
        matcher: "*",
        decide: hold,
    };
    let two = Guard {
        name: "s2",
        events: &["Stop"],
        matcher: "*",
        decide: hold,
    };
    let r = run(&mut e, &[one, two]);
    assert_eq!(
        out(&r),
        json!({"decision": "block", "reason": "held\n\nheld"})
    );
}

#[test]
fn a_guard_decides_only_its_events_and_its_tools() {
    let g = guard(refuse);
    assert!(g.takes(&bash("ls")));
    let mut read = bash("ls");
    read.input["tool_name"] = json!("Read");
    assert!(!g.takes(&read) && read.tool() == "Read");
    let prompt = Event {
        name: "UserPromptSubmit".to_owned(),
        input: json!({}),
    };
    assert!(!g.takes(&prompt) && prompt.tool().is_empty());
    let stop = Event {
        name: "Stop".to_owned(),
        input: json!({}),
    };
    assert!(g.takes(&stop));
}

fn say(_: &Event, _: &Session) -> Vec<Answer> {
    vec![Answer::Print("subset_pending=0".to_owned())]
}

#[test]
fn a_hand_run_mode_prints_its_text_as_it_is() {
    let mut e = Event {
        name: "status".to_owned(),
        input: json!({}),
    };
    let g = Guard {
        name: "s",
        events: &["status"],
        matcher: "*",
        decide: say,
    };
    assert_eq!(run(&mut e, &[g]).stdout, "subset_pending=0");
}
