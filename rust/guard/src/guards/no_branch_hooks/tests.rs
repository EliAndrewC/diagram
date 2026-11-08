//! The decider on the suite's shapes (`tests/hooks/test-no-branch-hooks.sh`, replayed through the shim, is the verdict).

use serde_json::json;

use super::decide;
use crate::protocol::{Answer, Event};
use crate::shared::session::Session;

fn run(cmd: &str) -> Vec<Answer> {
    crate::shared::log::quiet();
    let e = Event {
        name: "PreToolUse".to_owned(),
        input: json!({"tool_input": {"command": cmd}}),
    };
    decide(&e, &Session::from_input(&e.input))
}

fn refused(got: &[Answer], words: &str) -> bool {
    matches!(got, [Answer::Refuse(t)] if t.contains(words))
}

#[test]
fn every_spelling_of_making_a_branch_is_refused() {
    for cmd in [
        "git checkout -b x",
        "git checkout -B x",
        "git switch -c x",
        "git switch -C x",
        "git switch --create x",
        "git checkout --branch x",
    ] {
        assert!(refused(&run(cmd), "does not use feature branches"), "{cmd}");
    }
}

#[test]
fn what_is_not_branch_creation_and_another_repository_pass() {
    assert!(
        run("git checkout main").is_empty()
            && run("git branch --list").is_empty()
            && run("").is_empty()
    );
    assert!(run("git -C /host-l7r-repo checkout -b w").is_empty());
}

#[test]
fn the_escape_needs_a_reason() {
    assert!(run("git checkout -b t  # NO_BRANCH_OK: a throwaway bisect").is_empty());
    assert!(refused(
        &run("git checkout -b t  # NO_BRANCH_OK"),
        "with no reason"
    ));
}
