//! The decider on commands the suite carries (`tests/hooks/test-no-poll-hooks.sh`, replayed through the shim, is the verdict
//! against today's).

use std::path::PathBuf;

use serde_json::{json, Value};

use super::{decide, judge, local_minute, Ctx};
use crate::protocol::{Answer, Event};
use crate::shared::session::Session;
use crate::shared::shape::{strip_heredocs, strip_quotes};

fn minute() -> u64 {
    13
}

fn run_with(cmd: &str, background: bool) -> Vec<Answer> {
    crate::shared::log::quiet();
    let mut ti = json!({"command": cmd});
    if background {
        ti["run_in_background"] = Value::Bool(true);
    }
    let e = Event {
        name: "PreToolUse".to_owned(),
        input: json!({"tool_name": "Bash", "cwd": ".", "tool_input": ti}),
    };
    let s = Session::from_input(&json!({}));
    let scan = strip_quotes(&strip_heredocs(cmd));
    judge(&Ctx {
        event: &e,
        session: &s,
        cmd: cmd.to_owned(),
        scan,
        lib: PathBuf::from("/lib"),
        minute,
    })
}

fn run(cmd: &str) -> Vec<Answer> {
    run_with(cmd, false)
}

fn refused(a: &[Answer]) -> String {
    let [Answer::Refuse(w)] = a else {
        return String::new();
    };
    w.clone()
}

fn rewritten(a: &[Answer]) -> (Value, String) {
    let [Answer::Rewrite(v), Answer::Notice(n)] = a else {
        return (Value::Null, String::new());
    };
    (v.clone(), n.clone())
}

#[test]
fn a_busy_wait_and_a_disguised_sleep_are_refused() {
    assert!(refused(&run("while true; do echo; sleep 5; done")).contains("busy-wait loop"));
    assert!(refused(&run("command sleep 5")).contains("evades the harness"));
    assert!(run("git status").is_empty());
    assert!(run("sleep 1; for p in x; do echo; done").is_empty());
    assert!(rewritten(&[]).1.is_empty() && refused(&[]).is_empty());
}

#[test]
fn a_file_wait_is_made_safe_rather_than_refused() {
    let (v, said) = rewritten(&run("until grep -q x /tmp/a.log; do sleep 5; done"));
    assert!(
        v["run_in_background"] == true
            && said.contains("BACKGROUNDED")
            && said.contains("PROOF-OF-LIFE")
            && said.contains("CEILING")
    );
    let cmd = v["command"].as_str().unwrap_or_default().to_owned();
    assert!(cmd.contains("/lib/writer-alive.sh") && cmd.contains("WAIT TIMED OUT"));
    let (v2, said2) = rewritten(&run_with(&cmd, true));
    assert!(v2.is_null() && said2.is_empty());
    let alive = "until grep -q x /tmp/a.log || ! pgrep -f '[m]ake x'; do sleep 5; done";
    let (_, said3) = rewritten(&run_with(alive, true));
    assert!(
        said3.contains("CEILING") && !said3.contains("PROOF") && !said3.contains("BACKGROUNDED")
    );
    let ceiled = crate::shared::wait::add_ceiling(alive, crate::shared::wait::WAIT_CEILING_S)
        .unwrap_or_default();
    assert!(run_with(&ceiled, true).is_empty());
    let (_, said4) = rewritten(&run_with(
        "until grep -q x /tmp/a.log; do sleep 5; done",
        true,
    ));
    assert!(said4.contains("PROOF-OF-LIFE") && !said4.contains("BACKGROUNDED"));
    let own = "until grep -q x /tmp/a.log; do sleep 5; done; pgrep -f \"until grep\"";
    assert!(refused(&run(own)).contains("matches this command's own text"));
}

#[test]
fn a_self_matching_pattern_is_bracketed_or_refused() {
    let (v, said) = rewritten(&run("pgrep -f \"x y\" && echo up"));
    assert!(v["command"] == "pgrep -f \"[x] y\" && echo up" && said.contains("bracketed for you"));
    let (v2, said2) = rewritten(&run("pgrep -f \"make map GEN=a\" || echo gone"));
    assert!(
        v2["command"]
            .as_str()
            .unwrap_or_default()
            .contains("gates/l7r-gate.sh own-make map GEN=a")
            && said2.contains("scoped to this working tree")
    );
    let (v3, said3) = rewritten(&run("while pgrep -f \"x y\"; do :; done"));
    assert!(
        v3["command"]
            .as_str()
            .unwrap_or_default()
            .contains("WAIT TIMED OUT")
            && said3.contains("A ceiling was added")
    );
    assert!(refused(&run("pgrep -f \".x\"")).contains("matches this command's own text"));
    assert!(run("pgrep -f '[x] y'").is_empty());
}

#[test]
fn poll_ok_stands_aside_and_still_brackets_and_ceils() {
    assert!(run("curl -s x  # POLL_OK: the port is external").is_empty());
    let (v, said) = rewritten(&run(
        "until curl -s x; do sleep 5; done  # POLL_OK: the port is external",
    ));
    assert!(
        v["command"]
            .as_str()
            .unwrap_or_default()
            .contains("WAIT TIMED OUT")
            && said.contains("POLL_OK permitted this wait")
    );
    let (_, said2) = rewritten(&run(
        "pgrep -f \"x y\" && echo  # POLL_OK: the remote queue",
    ));
    assert!(
        said2.contains("POLL_OK permitted this wait, and its process-match pattern was bracketed")
    );
    assert!(refused(&run("sleep 5  # POLL_OK")).contains("POLL_OK with no reason"));
}

#[test]
fn a_periodic_report_goes_to_a_cron() {
    let r = refused(&run_with(
        "while true; do date; sleep 1800; done  # POLL_OK=\"every 30 minutes\"",
        true,
    ));
    assert!(
        r.contains("CronCreate(cron=\"*/30 * * * *\"")
            && r.contains("every 30 minutes: check the state once")
    );
    let plain = refused(&run_with("while true; do date; sleep 3600; done", true));
    assert!(plain.contains("cron=\"13 * * * *\"") && plain.contains("the periodic report: check"));
    assert!(refused(&run_with(
        "while true; do date; sleep 60; done  # CRON_OK: a one-off watch",
        true
    ))
    .contains("busy-wait"));
    assert!(
        refused(&run_with("while true; do sleep 60; done  # CRON_OK", true))
            .contains("CRON_OK with no reason")
    );
}

#[test]
fn decide_reads_the_command_and_skips_an_empty_one() {
    let s = Session::from_input(&json!({}));
    let empty = Event {
        name: "PreToolUse".to_owned(),
        input: json!({"tool_name": "Bash", "tool_input": {"command": ""}}),
    };
    assert!(decide(&empty, &s).is_empty());
    let ls = Event {
        name: "PreToolUse".to_owned(),
        input: json!({"tool_name": "Bash", "tool_input": {"command": "ls"}}),
    };
    assert!(decide(&ls, &s).is_empty());
    let quoted = Event {
        name: "PreToolUse".to_owned(),
        input: json!({"tool_name": "Bash", "tool_input": {"command": "''"}}),
    };
    assert!(decide(&quoted, &s).is_empty());
    assert!(local_minute() < 60);
}
