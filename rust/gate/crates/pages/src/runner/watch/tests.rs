//! The transcript readings and the watch: a stall ended, a session whose agents returned ended sooner, a session still at work, or one
//! whose transcript the Python's thread raised on, left alone. The processes a watch ends are this test's own `sleep`s, found through a
//! scratch `/proc` that names them.

use std::path::Path;
use std::time::Duration;

use serde_json::json;

use super::{
    entries, last_activity, now, projects_dir, returned_file, session_pids, terminate, turn_ended,
    undelivered, Times, Watch,
};

fn put(path: &Path, text: &str) {
    std::fs::create_dir_all(path.parent().unwrap()).unwrap();
    std::fs::write(path, text).unwrap();
}

fn lines(rows: &[serde_json::Value]) -> String {
    rows.iter()
        .flat_map(|r| [r.to_string(), "\n".to_owned()])
        .collect()
}

#[test]
fn the_transcript_says_what_was_queued_and_whether_the_turn_ended() {
    let d = l7r_gate_core::ci::fixtures::scratch("watch-read");
    let p = d.to_string_lossy().into_owned();
    let note = "<task-notification>done</task-notification>";
    put(
        &d.join("s.jsonl"),
        &(lines(&[
            json!({"type": "queue-operation", "operation": "enqueue", "content": "<task-notification>old</task-notification>"}),
            json!({"type": "queue-operation", "operation": "dequeue"}),
            json!({"type": "queue-operation", "operation": "enqueue", "content": note}),
            json!({"type": "queue-operation", "operation": "enqueue", "content": {"text": note}}),
            json!({"type": "queue-operation", "operation": "enqueue", "content": "plain"}),
            json!({"type": "queue-operation", "operation": "enqueue", "content": ""}),
            json!({"type": "assistant", "message": {"stop_reason": "tool_use"}}),
            json!({"type": "assistant", "message": {"stop_reason": "end_turn"}}),
        ]) + "[1]\nnot json\n"),
    );
    assert_eq!(entries(&format!("{p}/s.jsonl")).len(), 8);
    assert_eq!(
        undelivered(&p, "s"),
        [note.to_owned(), format!("{{'text': '{note}'}}")]
    );
    assert_eq!(turn_ended(&p, "s"), Some(true));
    assert!(undelivered(&p, "none").is_empty());
    assert_eq!(turn_ended(&p, "none"), Some(false));
    put(
        &d.join("t.jsonl"),
        &lines(&[json!({"type": "assistant", "message": "text"})]),
    );
    assert_eq!(turn_ended(&p, "t"), None);
    put(
        &d.join("u.jsonl"),
        &lines(&[json!({"type": "assistant", "message": 0})]),
    );
    assert_eq!(turn_ended(&p, "u"), Some(false));
}

#[test]
fn the_returned_reports_and_the_transcripts_directory() {
    let d = l7r_gate_core::ci::fixtures::scratch("watch-files");
    let log = d.to_string_lossy().into_owned();
    assert_eq!(returned_file(&log, &[]), Ok(None));
    let at = returned_file(&log, &["a".to_owned(), "b".to_owned()])
        .unwrap()
        .unwrap();
    assert_eq!(std::fs::read_to_string(&at).unwrap(), "a\n\nb\n");
    assert!(returned_file(&format!("{log}/no/such"), &["a".to_owned()]).is_err());
    assert_eq!(
        projects_dir("/diagram/.clones/x", "/home/u/"),
        "/home/u/.claude/projects/-diagram--clones-x"
    );
    assert_eq!(projects_dir("/r", ""), "/.claude/projects/-r");
    assert_eq!(last_activity(&log, "s"), None);
    put(&d.join("s/subagents/agent-a.jsonl"), "x");
    put(&d.join("s/subagents/.hidden.jsonl"), "x");
    put(&d.join("s/subagents/notes.txt"), "x");
    let sub = last_activity(&log, "s").unwrap();
    put(&d.join("s.jsonl"), "x");
    assert!(last_activity(&log, "s").unwrap() >= sub);
    assert!(now() > 1.7e9);
    let t = Times::standing();
    assert_eq!(
        (t.check, t.after, t.returned, t.retry_every),
        (60.0, 900.0, 300.0, 900.0)
    );
}

/// A `sleep` this test owns, named in `proc` as a `claude` process of session `sid`.
fn claude_in(proc: &Path, sid: &str) -> std::process::Child {
    let child = std::process::Command::new("sleep")
        .arg("30")
        .spawn()
        .unwrap();
    put(
        &proc.join(child.id().to_string()).join("cmdline"),
        &format!("/usr/bin/claude\0-p\0go\0--session-id\0{sid}\0"),
    );
    child
}

#[test]
fn the_session_s_processes_are_read_by_their_arguments() {
    let d = l7r_gate_core::ci::fixtures::scratch("watch-pids");
    let proc = d.join("proc");
    put(&proc.join("1/cmdline"), "claude\0--resume\0s1\0");
    put(&proc.join("2/cmdline"), "node\0--session-id\0s1\0");
    put(&proc.join("3/cmdline"), "claude\0s1\0");
    put(&proc.join("4/cmdline"), "claude\0--session-id\0other\0");
    put(&proc.join("self/cmdline"), "claude\0--resume\0s1\0");
    std::fs::create_dir_all(proc.join("5")).unwrap();
    assert_eq!(session_pids("s1", &proc), [1]);
    assert!(session_pids("s1", &d.join("none")).is_empty());
    let mut child = claude_in(&proc, "s2");
    terminate(i32::try_from(child.id()).unwrap());
    assert!(!child.wait().unwrap().success());
}

fn quick(after: f64, returned: f64) -> Times {
    Times {
        check: 0.001,
        after,
        returned,
        retry_every: 0.01,
    }
}

/// Every watch runs at once and the test waits on the one that must end its session (feature 449 T167: the five watches one after
/// another, each given its own sleep, took 367 ms against FR-008's tenth of a second); a millisecond's check leaves each watch tens of
/// checks inside the wait, so each path the watch can take is still taken.
#[test]
fn a_quiet_session_is_ended_and_a_working_one_left_alone() {
    let d = l7r_gate_core::ci::fixtures::scratch("watch-stall");
    let (projects, proc) = (d.join("projects"), d.join("proc"));
    std::fs::create_dir_all(&projects).unwrap();
    let p = projects.to_string_lossy().into_owned();
    // the turn ended with reports waiting: ended after `returned`, before `after`
    put(
        &projects.join("r.jsonl"),
        &lines(&[
            json!({"type": "assistant", "message": {"stop_reason": "end_turn"}}),
            json!({"type": "queue-operation", "operation": "enqueue", "content": "<task-notification>x</task-notification>"}),
        ]),
    );
    // the turn ended with nothing waiting, or the session is still in a tool call: left alone until stopped
    put(
        &projects.join("e.jsonl"),
        &lines(&[json!({"type": "assistant", "message": {"stop_reason": "end_turn"}})]),
    );
    // a transcript the Python's thread raised on: it watched no more
    put(
        &projects.join("t.jsonl"),
        &lines(&[json!({"type": "assistant", "message": "text"})]),
    );
    // quiet past `after` (none: every check is past it), with nothing in `proc` at first: watched on until the process is there, then
    // ended
    let stall = Watch::start(p.clone(), "s".to_owned(), quick(0.0, 0.0), proc.clone());
    let mut returned = claude_in(&proc, "r");
    let reports = Watch::start(p.clone(), "r".to_owned(), quick(60.0, 0.01), proc.clone());
    let ended = Watch::start(p.clone(), "e".to_owned(), quick(60.0, 0.0), proc.clone());
    let quiet = Watch::start(p.clone(), "q".to_owned(), quick(60.0, 30.0), proc.clone());
    let raised = Watch::start(p, "t".to_owned(), quick(60.0, 0.0), proc.clone());
    std::thread::sleep(Duration::from_millis(20));
    let mut child = claude_in(&proc, "s");
    let started = std::time::Instant::now();
    while child.try_wait().unwrap().is_none() && started.elapsed() < Duration::from_secs(5) {
        std::thread::sleep(Duration::from_millis(2));
    }
    let (stalled, idle) = stall.stop();
    assert!(stalled);
    assert_eq!(idle, 0);
    let _ = child.wait();
    let _ = returned.wait();
    assert!(reports.stop().0);
    assert_eq!(ended.stop(), (false, 0));
    assert_eq!(quiet.stop(), (false, 0));
    assert_eq!(raised.stop(), (false, 0));
}
