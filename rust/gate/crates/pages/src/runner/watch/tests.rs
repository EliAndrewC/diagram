//! The transcript readings and the watch: a stall ended, a session whose agents returned ended sooner, a session still at work, or one
//! whose transcript the Python's thread raised on, left alone - each path on counted checks, none on the host's timing (451 T47). The
//! processes a watch ends are this test's own `sleep`s, found through a scratch `/proc` that names them.

use std::path::Path;
use std::time::Duration;

use serde_json::json;

use super::{
    entries, last_activity, now, projects_dir, returned_file, session_pids, terminate, turn_ended,
    undelivered, watch, Times, Watch,
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

/// A wait that watches on for `checks` checks and then halts, counting each time it is asked - the watch's checks counted, never timed
/// (451 T47: a path only a scheduler reached in time went unreached once in `make static`'s coverage, as T35's injected clock).
fn counted(checks: u32, asked: &mut u32) -> impl FnMut(Duration) -> bool + '_ {
    move |_| {
        *asked += 1;
        *asked <= checks
    }
}

/// Each path the watch takes, its checks counted on this thread: a stall ended, a session whose agents returned ended though its quiet
/// is short of `after`, a session still at work or whose turn ended with nothing waiting watched on, and one whose transcript the
/// Python's thread raised on left on the first check. The bounds are infinities, so no branch turns on how long the host took.
#[test]
fn each_check_takes_its_path_however_slow_the_host() {
    let d = l7r_gate_core::ci::fixtures::scratch("watch-paths");
    let (projects, proc) = (d.join("projects"), d.join("proc"));
    std::fs::create_dir_all(&projects).unwrap();
    let p = projects.to_string_lossy().into_owned();
    let (never, always) = (f64::INFINITY, f64::NEG_INFINITY);
    put(
        &projects.join("r.jsonl"),
        &lines(&[
            json!({"type": "assistant", "message": {"stop_reason": "end_turn"}}),
            json!({"type": "queue-operation", "operation": "enqueue", "content": "<task-notification>x</task-notification>"}),
        ]),
    );
    put(
        &projects.join("e.jsonl"),
        &lines(&[json!({"type": "assistant", "message": {"stop_reason": "end_turn"}})]),
    );
    put(
        &projects.join("t.jsonl"),
        &lines(&[json!({"type": "assistant", "message": "text"})]),
    );
    let run = |sid: &str, times: Times, checks: u32| {
        let mut asked = 0;
        let seen = watch(&p, sid, times, &proc, counted(checks, &mut asked));
        (seen, asked)
    };
    // still quiet short of `returned`, or its turn ended with nothing waiting: watched on until halted, every check taken
    assert_eq!(run("q", quick(never, never), 3), ((false, 0), 4));
    assert_eq!(run("e", quick(never, always), 3), ((false, 0), 4));
    // the transcript the Python's thread raised on: it watched no more, on its first check, with checks left
    assert_eq!(run("t", quick(never, always), 3), ((false, 0), 1));
    // the turn ended with reports waiting: ended though short of `after`
    let mut returned = claude_in(&proc, "r");
    assert_eq!(run("r", quick(never, always), 3).1, 1);
    assert!(!returned.wait().unwrap().success());
    // quiet past `after` with nothing in `proc`: watched on; the process there at the second check, ended
    let (mut asked, mut child) = (0, None);
    let started = std::time::Instant::now();
    let (stalled, idle) = watch(&p, "s", quick(always, always), &proc, |_| {
        asked += 1;
        if asked == 2 {
            child = Some(claude_in(&proc, "s"));
        }
        asked <= 3
    });
    assert_eq!((stalled, asked), (true, 2));
    assert!(idle <= started.elapsed().as_secs() + 1);
    assert!(!child.unwrap().wait().unwrap().success());
}

/// A started watch ends a stalled session on its own thread, and one stopped while its session works says it stalled nothing; each
/// waits on an event (the process ended, the thread joined), never on a sleep.
#[test]
fn a_started_watch_ends_a_stall_and_stops_when_halted() {
    let d = l7r_gate_core::ci::fixtures::scratch("watch-stall");
    let (projects, proc) = (d.join("projects"), d.join("proc"));
    std::fs::create_dir_all(&projects).unwrap();
    let p = projects.to_string_lossy().into_owned();
    let mut child = claude_in(&proc, "s");
    let stall = Watch::start(
        p.clone(),
        "s".to_owned(),
        quick(f64::NEG_INFINITY, f64::NEG_INFINITY),
        proc.clone(),
    );
    assert!(!child.wait().unwrap().success());
    assert!(stall.stop().0);
    let working = Watch::start(p, "q".to_owned(), quick(f64::INFINITY, f64::INFINITY), proc);
    assert_eq!(working.stop(), (false, 0));
}
