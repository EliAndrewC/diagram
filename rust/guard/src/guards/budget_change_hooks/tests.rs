//! The decider on the suite's shapes (`tests/hooks/test-budget-change-hooks.sh`, replayed through the shim, is the verdict).

use serde_json::json;

use super::{decide, verdict};
use crate::protocol::{Answer, Event};
use crate::shared::session::Session;

fn said() -> Vec<String> {
    vec!["raise the web budget to 40 per lane, that one is fine.".to_owned()]
}

#[test]
fn the_words_must_be_the_gms_and_long_enough() {
    let m = said();
    assert_eq!(
        verdict(
            "make budget-change PHASE=web TO=40 WORDS=\"raise the web budget\"",
            &m
        ),
        ""
    );
    assert_eq!(
        verdict("make budget-program WORDS='that one is fine'", &m),
        ""
    );
    assert_eq!(verdict("make budget-change PHASE=web", &m), "no-words");
    assert_eq!(verdict("make budget-change WORDS=\"\"", &m), "no-words");
    assert_eq!(verdict("make budget-change WORDS=fine", &m), "short");
    assert_eq!(
        verdict("make budget-change WORDS=\"words he never wrote\"", &m),
        "not-found"
    );
    assert_eq!(verdict("cd /x && make budget-change", &m), "no-words");
    assert_eq!(verdict("make budget-set WORDS=x", &m), "");
    assert_eq!(
        verdict("git commit -m 'the make budget-change target'", &m),
        ""
    );
    assert_eq!(
        verdict("make budget-change XWORDS=\"raise the web budget\"", &m),
        "no-words"
    );
}

fn run(cmd: &str, transcript: &str) -> Vec<Answer> {
    crate::shared::log::quiet();
    let e = Event {
        name: "PreToolUse".to_owned(),
        input: json!({"transcript_path": transcript, "tool_input": {"command": cmd}}),
    };
    decide(&e, &Session::from_input(&e.input))
}

#[test]
fn each_refusal_says_why_and_names_the_compliant_command() {
    let refused = |got: &[Answer], words: &str| matches!(got, [Answer::Refuse(t)] if t.contains(words) && t.contains("make budget-program OPS_AT_40"));
    assert!(refused(&run("make budget-change", ""), "no WORDS= given"));
    assert!(refused(
        &run("make budget-change WORDS=fine", ""),
        "under three words"
    ));
    assert!(refused(
        &run("make budget-change WORDS=\"three whole words\"", ""),
        "in no message the GM wrote"
    ));
    assert!(run("echo hi", "").is_empty());
    assert!(run("echo budget-change", "").is_empty());
}
