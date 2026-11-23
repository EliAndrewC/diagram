//! 451 T183: STOP HOOKS THAT KEEP THE SESSION BUSY (the GM 2026-11-23). A ruling that holds new work silences the idle check; the idle
//! check is silent for a sub-agent, for anything the harness tracks running, and for a session that turned since its Stop; it waits
//! its seconds. Shapes from the coordinator's 2026-11-23 transcript.

use std::path::Path;

use serde_json::json;

use super::super::holds::held;
use super::super::idle_check;
use super::{agent, append, said, world};

/// A ruling row of `feature`'s `arbiter.jsonl`.
fn rule(c: &Path, feature: &str, trigger: &str, ruling: &str, what: &str, utc: &str) {
    let log = c.join("specs").join(feature).join("arbiter.jsonl");
    if !log.is_file() {
        std::fs::write(&log, "").unwrap();
    }
    append(
        &log,
        &json!({"trigger": trigger, "kind": "ask", "ruling": ruling, "what": what, "utc": utc})
            .to_string(),
    );
}

/// Today's two holds read as holds; the go-on rulings of the record do not; the newest set-down ruling decides; another feature's
/// trigger and an unreadable log hold nothing.
#[test]
fn a_set_down_ruling_that_holds_new_work_is_read_as_a_hold() {
    let (_dir, c, _tr) = world("holds", "no");
    assert_eq!(held(&c, "385-x"), None, "no log");
    let holds = [
        "Go on as the question proposes. 385 starts no new task, and the set-down hook stops asking 385 for one.",
        "Go on now, without pause, with the seven building defects until each lands. No other 385 task starts: the free-slot hook's request for one is answered by this ruling.",
        "Set 385 down now, as the question proposes.",
        "Set feature 385 down now and do not start T83.",
        "Stop 385 and start no further 385 task.",
        // ask:set-down-449-pilot (2026-11-17): its item 4 sets the feature down (T183's MODE 4 round 2, D11)
        "1. Do not start T150-T158. 2. Leave T171 open as filed, with both routes and their costs written in the task. 3. Make sure the pilot's report is complete for both pieces. 4. Then set down. The work resumes from the GM's reply to the pilot report.",
    ];
    let goes_on = [
        "Do not set down. Resume the ports now: T83 first.",
        "No set-down; the session goes on, in this order, with no porting.",
        "Go on as proposed. (1) Record seed 904.",
        "T26 is NOT set down; the session goes on now, in this order.",
        "1. Do not start T150-T158. 2. Leave T171 open as filed.",
        "Before setting the feature down, check that the T06 draft as it reads now is the text that passed escalation-check.",
        "The waiver covers this one landing and does not stop the session. While the batch landing runs, the session runs no make task-start.",
    ];
    for (n, what) in holds.iter().enumerate() {
        let trigger = format!("ask:set-down-385-h{n}");
        rule(
            &c,
            "385-x",
            &trigger,
            "continue",
            what,
            &format!("2026-11-23T10:0{n}:00Z"),
        );
        assert_eq!(held(&c, "385-x"), Some(trigger), "{what}");
    }
    for (n, what) in goes_on.iter().enumerate() {
        rule(
            &c,
            "385-x",
            &format!("ask:set-down-385-g{n}"),
            "continue",
            what,
            &format!("2026-11-23T11:0{n}:00Z"),
        );
        assert_eq!(held(&c, "385-x"), None, "{what}");
    }
    // an accept holds as a continue does; a process fault holds nothing
    rule(
        &c,
        "385-x",
        "ask:set-down-T26",
        "accept",
        "Set 385 down now.",
        "2026-11-23T12:00:00Z",
    );
    assert_eq!(held(&c, "385-x").as_deref(), Some("ask:set-down-T26"));
    rule(
        &c,
        "385-x",
        "ask:set-down-385-f",
        "process fault",
        "385 starts no new task.",
        "2026-11-23T12:01:00Z",
    );
    assert_eq!(held(&c, "385-x"), None);
    // another feature's trigger, an earlier time and a ruling of another kind are not the newest set-down ruling
    rule(
        &c,
        "385-x",
        "ask:set-down-449-x",
        "continue",
        "449 starts no new task.",
        "2026-11-23T13:00:00Z",
    );
    rule(
        &c,
        "385-x",
        "ask:set-down-385-old",
        "continue",
        "Set 385 down now.",
        "2026-11-01T00:00:00Z",
    );
    rule(
        &c,
        "385-x",
        "round:x@3",
        "continue",
        "385 starts no new task.",
        "2026-11-23T14:00:00Z",
    );
    assert_eq!(held(&c, "385-x"), None);
    std::fs::write(c.join("specs/385-x/arbiter.jsonl"), b"\xff\xfe\n").unwrap();
    assert_eq!(held(&c, "385-x"), None, "an unreadable log holds nothing");
}

/// A held feature: the idle check says nothing (said before the ruling), and nothing while a builder runs either way.
#[test]
fn a_held_feature_is_never_named_by_the_idle_check() {
    let (_dir, c, tr) = world("held", "no");
    crate::env::set("L7R_EVENTS_DIR", c.join("no-events"));
    std::fs::write(
        c.join("specs/385-x/tasks.md"),
        "- [ ] T02 the next thing\n- [ ] T03 later\n- [ ] T04 a fourth\n",
    )
    .unwrap();
    assert!(said(&c, &tr).is_some_and(|t| t.contains("open task(s) and nothing is running")));
    agent(&tr, "a1", 1, "385 T02: the next thing");
    assert_eq!(
        said(&c, &tr),
        None,
        "a builder runs: no free slot is named (451 T183's MODE 4, D10)"
    );
    rule(
        &c,
        "385-x",
        "ask:set-down-385-talk",
        "continue",
        "385 starts no new task.",
        "2026-11-23T14:42:15Z",
    );
    append(&tr, &super::notice("a1", super::FINISHED));
    assert_eq!(said(&c, &tr), None, "the idle check");
    crate::env::unset("L7R_EVENTS_DIR");
}

/// 451 T183's MODE 4, D6: A TASK A RULING HOLDS BY NAME IS NEVER NAMED. The newest set-down ruling's do-not-start clause holds the tasks
/// it names (the form of ask:set-down-449-pilot's "1. Do not start T150-T158", 2026-11-17, a ruling that also set 449 down, D11, so
/// here one that sends other work on): T150-T158 are never the idle check's next, T171 the clause does not name is; with only held
/// tasks open the check is silent; a later set-down ruling ends the hold, as it ends a feature's.
#[test]
fn a_task_a_ruling_holds_by_name_is_never_the_idle_check_s_next() {
    let (_dir, c, tr) = world("named-hold", "no");
    crate::env::set("L7R_EVENTS_DIR", c.join("no-events"));
    let pilot = "1. Do not start T150-T158. 2. Go on with T171, with both routes and their costs written in the task. 3. Make sure the pilot's report is complete (T169, T172, T173).";
    rule(
        &c,
        "385-x",
        "ask:set-down-385-pilot",
        "accept",
        pilot,
        "2026-11-17T18:45:45Z",
    );
    assert_eq!(
        held(&c, "385-x"),
        None,
        "a hold of named tasks holds no feature"
    );
    let write = |tasks: &str| std::fs::write(c.join("specs/385-x/tasks.md"), tasks).unwrap();
    write("- [ ] T150 [perf] the first piece\n- [ ] T154 the fifth piece\n- [ ] T158 the last piece\n- [ ] T171 the ways-out count\n");
    let text = said(&c, &tr).unwrap();
    assert!(
        text.contains("start the next (T171 the ways-out count)"),
        "{text}"
    );
    assert!(text.contains("4 open task(s)"), "{text}");
    // only held tasks open: silent
    write("- [ ] T150 [perf] the first piece\n- [ ] T158 the last piece\n");
    assert_eq!(said(&c, &tr), None, "only held tasks");
    // a later set-down ruling that sends the work on ends the hold
    rule(
        &c,
        "385-x",
        "ask:set-down-385-resume",
        "continue",
        "Do not set down. Resume the pieces now.",
        "2026-11-18T03:56:24Z",
    );
    let text = said(&c, &tr).unwrap();
    assert!(text.contains("start the next (T150 "), "{text}");
    crate::env::unset("L7R_EVENTS_DIR");
}

/// The idle check (`l7r-guard --idle-check`): silent at once for a sub-agent's stop or a Stop whose `background_tasks` names a run;
/// the harness's empty list taken at its word over the transcript's reading; silent where the transcript gained a turn while it
/// waited; else the set-down block.
#[test]
fn the_idle_check_speaks_only_when_idle_with_work() {
    let (_dir, c, tr) = world("idle", "no");
    crate::env::set("SET_DOWN_ROOT", &c);
    crate::env::set("L7R_IDLE_CHECK_SECS", "0");
    let at = tr.to_string_lossy().into_owned();
    let stop = |extra: serde_json::Value| {
        let mut input = json!({"transcript_path": at, "cwd": c.to_string_lossy()});
        for (k, v) in extra.as_object().unwrap() {
            input[k] = v.clone();
        }
        idle_check(&input)
    };
    assert!(stop(json!({})).is_some_and(|t| t.contains("make set-down F=385")));
    assert_eq!(stop(json!({"agent_id": "a9"})), None, "a sub-agent's stop");
    let running = json!({"background_tasks": [{"id": "b1", "type": "shell", "status": "running"}]});
    assert_eq!(stop(running), None, "a tracked run");
    // the transcript reads a launch the harness's list no longer names: the list is the harness's own, and wins
    append(&tr, r#"{"toolUseResult": {"backgroundTaskId": "b2"}}"#);
    assert_eq!(stop(json!({})), None, "no list: the transcript's reading");
    assert!(stop(json!({"background_tasks": []})).is_some());
    crate::env::unset("L7R_IDLE_CHECK_SECS");
    crate::env::unset("SET_DOWN_ROOT");
}

/// While the idle check waits, a prompt, a notice or a reply in the transcript is a turn: silent. A turn's own end records
/// (`system`) and a line that is no record are none. A transcript that cannot be opened reads as no turn.
#[test]
fn a_turn_while_the_idle_check_waits_silences_it() {
    let (_dir, c, tr) = world("turned", "no");
    let len = || std::fs::metadata(&tr).unwrap().len();
    let start = len();
    append(&tr, r#"{"type": "system", "subtype": "stop_hook_summary"}"#);
    append(&tr, "not json");
    assert!(!super::super::idle::turned_since(&tr, start));
    append(&tr, r#"{"type": "user", "message": {"content": "go on"}}"#);
    assert!(super::super::idle::turned_since(&tr, start));
    assert!(!super::super::idle::turned_since(&tr, len()));
    append(&tr, r#"{"type": "assistant", "message": {"content": []}}"#);
    assert!(super::super::idle::turned_since(&tr, start));
    assert!(!super::super::idle::turned_since(
        &c.join("no-such.jsonl"),
        0
    ));
    assert!(
        !super::super::idle::turned_since(&c, 0),
        "a directory reads nothing"
    );
}

/// A reply written while the idle check waits: silent (`idle_check` itself, not only its reader); a held turn's agent stop or a
/// silent verdict says nothing either.
#[test]
fn a_reply_during_the_idle_check_s_wait_silences_it() {
    let (_dir, c, tr) = world("turned-live", "no");
    crate::env::set("SET_DOWN_ROOT", &c);
    crate::env::set("L7R_IDLE_CHECK_SECS", "1");
    let input = json!({"transcript_path": tr.to_string_lossy(), "background_tasks": []});
    let at = tr.clone();
    let writer = std::thread::spawn(move || {
        std::thread::sleep(std::time::Duration::from_millis(200));
        append(&at, r#"{"type": "assistant", "message": {"content": []}}"#);
    });
    assert_eq!(idle_check(&input), None);
    writer.join().unwrap();
    crate::env::unset("L7R_IDLE_CHECK_SECS");
    crate::env::unset("SET_DOWN_ROOT");
}

/// Agent `id`'s meta as Claude Code writes it: the session's own dispatch (`spawnDepth` 1) or a sub-agent's.
#[test]
fn only_the_session_s_own_dispatch_is_session_dispatched() {
    let (_dir, _c, tr) = world("dispatched", "no");
    agent(&tr, "s1", 1, "building-review: the plan");
    agent(&tr, "b1", 2, "building-review: a builder's");
    let dir = tr.with_extension("").join("subagents");
    assert!(super::super::session_dispatched(&dir, "s1"));
    assert!(!super::super::session_dispatched(&dir, "b1"));
    assert!(!super::super::session_dispatched(&dir, "none"));
}

/// The wait is the knob's: one second, timed.
#[test]
fn the_idle_check_waits_its_seconds() {
    let (_dir, c, tr) = world("waits", "no");
    crate::env::set("SET_DOWN_ROOT", &c);
    crate::env::set("L7R_IDLE_CHECK_SECS", "1");
    let input = json!({"transcript_path": tr.to_string_lossy(), "background_tasks": []});
    let t0 = std::time::Instant::now();
    assert!(idle_check(&input).is_some());
    assert!(t0.elapsed() >= std::time::Duration::from_secs(1));
    crate::env::unset("L7R_IDLE_CHECK_SECS");
    crate::env::unset("SET_DOWN_ROOT");
}
