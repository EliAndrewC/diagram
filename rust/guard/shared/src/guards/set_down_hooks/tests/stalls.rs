//! 451 T193: A BUILDER WAITING ON A WATCH THAT NEVER FIRES IS SEEN AND WOKEN (the GM 2026-11-23: "I don't see any work happening").
//! Today's shape: 451 T184's builder (`a676c53072fd7258b`) ended its turn at 20:27:39Z waiting on its Monitor `bx5gtybg3`; the watch
//! ended at 20:39 and the Stop's `background_tasks` stopped naming it, but its notice reached the builder's transcript only after the
//! coordinator's message at 21:35, and the idle check stayed silent under 451's hold ("451 starts no new task").

use std::cell::Cell;
use std::collections::HashMap;
use std::path::Path;
use std::time::{Duration, SystemTime};

use serde_json::json;

use super::super::stalls::{stalled, STALL_SECS};
use super::super::{idle_check, idle_check_with, status, Procs};
use super::{append, notice, own, world, WAITING};

/// The builder's own transcript: its Monitor launched (the tool's own record, `{"taskId": ..., "timeoutMs": ...}`), its turn ended
/// on its last line.
fn builder(tr: &Path, id: &str, watch: &str) {
    own(
        tr,
        id,
        &format!(
            r#"{{"isSidechain":true,"agentId":"{id}","toolUseResult":{{"taskId":"{watch}","timeoutMs":1800000,"persistent":false}}}}"#
        ),
    );
    own(tr, id, "not json");
    own(
        tr,
        id,
        &format!(
            r#"{{"isSidechain":true,"agentId":"{id}","type":"assistant","message":{{"role":"assistant","content":[{{"type":"text","text":"The plan section is CLEAR as of round 3. Waiting for the follow-ups session, then closing-checks run again.\nsecond line"}}],"stop_reason":"end_turn"}}}}"#
        ),
    );
}

/// Agent `id`'s own transcript and meta, last written `ago` seconds before now.
fn age(tr: &Path, id: &str, ago: u64) {
    let dir = tr.with_extension("").join("subagents");
    let at = SystemTime::now() - Duration::from_secs(ago);
    std::fs::File::options()
        .append(true)
        .open(dir.join(format!("agent-{id}.jsonl")))
        .unwrap()
        .set_modified(at)
        .unwrap();
}

fn meta(tr: &Path, id: &str, description: &str) {
    let dir = tr.with_extension("").join("subagents");
    std::fs::write(
        dir.join(format!("agent-{id}.meta.json")),
        json!({"spawnDepth": 1, "description": description}).to_string(),
    )
    .unwrap();
}

/// Today's shape, red before T193: a held feature, the Stop's list empty after the watch ended, the builder's last word an interim
/// notice and its transcript silent past the bound - the idle check names it, with its last line and the wake command, through the
/// hold; said once while unchanged.
#[test]
fn a_builder_whose_watch_ended_unheard_is_named_through_a_hold() {
    let (_dir, c, tr) = world("stalled", "no");
    std::fs::write(
        c.join("specs/385-x/arbiter.jsonl"),
        json!({"trigger": "ask:set-down-385-talk", "kind": "ask", "ruling": "continue",
               "what": "385 starts no new task.", "utc": "2026-11-23T14:42:15Z"})
        .to_string()
            + "\n",
    )
    .unwrap();
    crate::env::set("SET_DOWN_ROOT", &c);
    crate::env::set("L7R_IDLE_CHECK_SECS", "0");
    append(&tr, r#"{"toolUseResult": {"agentId": "a676"}}"#);
    builder(&tr, "a676", "bx5");
    meta(&tr, "a676", "385 T02: size edits never change a claim");
    append(&tr, &notice("a676", WAITING));
    age(&tr, "a676", 2_500);
    let input = json!({"transcript_path": tr.to_string_lossy(), "cwd": c.to_string_lossy(),
                       "session_id": "s-stall", "background_tasks": []});
    let text = idle_check(&input).expect("the stalled builder is named");
    assert!(text.contains("a676"), "{text}");
    assert!(text.contains("385 T02: size edits"), "{text}");
    assert!(
        text.contains("Waiting for the follow-ups session"),
        "its last line: {text}"
    );
    assert!(!text.contains("second line"), "one line: {text}");
    assert!(text.contains("SendMessage to a676"), "{text}");
    assert_eq!(idle_check(&input), None, "said once while unchanged");
    // a second builder stalls: it alone is said, the first not again beside it
    append(&tr, r#"{"toolUseResult": {"agentId": "a7"}}"#);
    builder(&tr, "a7", "bx7");
    meta(&tr, "a7", "385 T03: later");
    append(&tr, &notice("a7", WAITING));
    age(&tr, "a7", 2_000);
    let text = idle_check(&input).expect("the second is named");
    assert!(text.contains("SendMessage to a7"), "{text}");
    assert!(!text.contains("a676"), "{text}");
    assert!(text.starts_with("STALLED: 1 builder(s)"), "{text}");
    crate::env::unset("L7R_IDLE_CHECK_SECS");
    crate::env::unset("SET_DOWN_ROOT");
}

/// An agent with live work, or one whose transcript moved within the bound, is never named; nor one the Stop lists itself, one that
/// ended, or a shell. A child the harness lists, or a child whose transcript moves, is its parent's live work.
#[test]
fn only_an_agent_with_no_live_work_and_a_silent_transcript_is_stalled() {
    let (_dir, c, tr) = world("stall-rules", "no");
    let none = std::collections::HashSet::new();
    let bound = Duration::from_secs(STALL_SECS);
    append(&tr, r#"{"toolUseResult": {"agentId": "a1"}}"#);
    builder(&tr, "a1", "w1");
    append(&tr, &notice("a1", WAITING));
    age(&tr, "a1", 100);
    assert!(
        stalled(&tr, &c, &none, bound).stalls.is_empty(),
        "moved within the bound"
    );
    age(&tr, "a1", STALL_SECS + 60);
    assert!(
        stalled(&tr, &c, &none, bound).stalls.is_empty(),
        "no meta: no builder"
    );
    meta(&tr, "a1", "385 T01: done already");
    assert!(
        stalled(&tr, &c, &none, bound).stalls.is_empty(),
        "its task is closed"
    );
    meta(&tr, "a1", "a review of 385 T02");
    assert!(
        stalled(&tr, &c, &none, bound).stalls.is_empty(),
        "no builder's brief"
    );
    meta(&tr, "a1", "385 T02: build it");
    let named = stalled(&tr, &c, &none, bound).stalls;
    assert_eq!(named.len(), 1);
    assert_eq!(named[0].id, "a1");
    assert_eq!(named[0].description, "385 T02: build it");
    let listed: std::collections::HashSet<String> = ["w1".to_owned()].into();
    assert!(
        stalled(&tr, &c, &listed, bound).stalls.is_empty(),
        "its watch is live"
    );
    let itself: std::collections::HashSet<String> = ["a1".to_owned()].into();
    assert!(
        stalled(&tr, &c, &itself, bound).stalls.is_empty(),
        "listed itself: mid-turn"
    );
    // a child of its own: listed, or moving, is live work; silent and unlisted, none
    own(
        &tr,
        "a1",
        r#"{"isSidechain":true,"agentId":"a1","toolUseResult":{"status":"async_launched","agentId":"k1"}}"#,
    );
    own(&tr, "k1", r#"{"type":"assistant"}"#);
    age(&tr, "a1", STALL_SECS + 60);
    let child: std::collections::HashSet<String> = ["k1".to_owned()].into();
    assert!(
        stalled(&tr, &c, &child, bound).stalls.is_empty(),
        "its child is listed"
    );
    assert!(
        stalled(&tr, &c, &none, bound).stalls.is_empty(),
        "its child's transcript moves"
    );
    age(&tr, "k1", STALL_SECS + 60);
    assert_eq!(
        stalled(&tr, &c, &none, bound).stalls.len(),
        1,
        "a silent child is no work"
    );
    // ended: a final notice
    append(&tr, &notice("a1", r#"Agent \"build it\" finished"#));
    assert!(stalled(&tr, &c, &none, bound).stalls.is_empty(), "ended");
    // a shell the session launched has no transcript of its own
    append(&tr, r#"{"toolUseResult": {"backgroundTaskId": "b1"}}"#);
    assert!(stalled(&tr, &c, &none, bound).stalls.is_empty(), "a shell");
    assert!(
        stalled(&tr.with_file_name("none.jsonl"), &c, &none, bound)
            .stalls
            .is_empty(),
        "no transcript"
    );
    // a builder's transcript that cannot be read names nothing
    append(&tr, r#"{"toolUseResult": {"agentId": "a3"}}"#);
    append(&tr, &notice("a3", WAITING));
    let dir = tr.with_extension("").join("subagents");
    std::fs::create_dir_all(dir.join("agent-a3.jsonl")).unwrap();
    meta(&tr, "a3", "385 T02: unreadable");
    let at = SystemTime::now() - Duration::from_secs(STALL_SECS + 60);
    std::fs::File::open(dir.join("agent-a3.jsonl"))
        .unwrap()
        .set_modified(at)
        .unwrap();
    assert!(
        stalled(&tr, &c, &none, bound).stalls.is_empty(),
        "unreadable"
    );
}

/// The idle check with a run listed still looks for a stalled agent (a builder may sit stuck while another works), but names no
/// open task; with no list at all (a harness before the field) live work cannot be told, and no agent is named.
#[test]
fn a_listed_run_still_lets_a_stalled_agent_be_named_but_no_list_names_none() {
    let (_dir, c, tr) = world("stall-listed", "no");
    crate::env::set("SET_DOWN_ROOT", &c);
    crate::env::set("L7R_IDLE_CHECK_SECS", "0");
    let input = |tasks: Option<serde_json::Value>| {
        let mut i = json!({"transcript_path": tr.to_string_lossy(), "cwd": c.to_string_lossy(), "session_id": "s-listed"});
        if let Some(t) = tasks {
            i["background_tasks"] = t;
        }
        i
    };
    let other = json!([{"id": "a9", "type": "subagent"}]);
    assert_eq!(
        idle_check(&input(Some(other.clone()))),
        None,
        "a tracked run"
    );
    append(&tr, r#"{"toolUseResult": {"agentId": "a2"}}"#);
    builder(&tr, "a2", "w2");
    meta(&tr, "a2", "385 T03: later");
    append(&tr, &notice("a2", WAITING));
    age(&tr, "a2", STALL_SECS + 60);
    // the bound is the knob's
    crate::env::set("L7R_STALL_SECS", "100000");
    assert_eq!(
        idle_check(&input(Some(other.clone()))),
        None,
        "within a wider bound"
    );
    crate::env::set("L7R_STALL_SECS", "600");
    let text = idle_check(&input(Some(other))).expect("named beside a live run");
    crate::env::unset("L7R_STALL_SECS");
    assert!(text.contains("SendMessage to a2"), "{text}");
    assert!(
        !text.contains("make set-down"),
        "no open task named while a run is listed: {text}"
    );
    assert_eq!(
        idle_check(&input(None)).filter(|t| t.contains("SendMessage")),
        None
    );
    crate::env::unset("L7R_IDLE_CHECK_SECS");
    crate::env::unset("SET_DOWN_ROOT");
}

/// A stand-in process table: the writers each look sees, in turn (the last repeated), and the dead-producer waiters.
struct Table {
    looks: Vec<Option<HashMap<String, Vec<u32>>>>,
    seen: Cell<usize>,
    stale: Vec<(u32, String)>,
    /// The live command lines, each with its pid.
    cmds: Vec<(u32, String)>,
}

impl Procs for Table {
    fn writers(&self, _: &str) -> Option<HashMap<String, Vec<u32>>> {
        let at = self.seen.get();
        self.seen.set(at + 1);
        self.looks[at.min(self.looks.len() - 1)].clone()
    }
    fn stale(&self) -> Vec<(u32, String)> {
        self.stale.clone()
    }
    fn running(&self, fragment: &str) -> Vec<u32> {
        self.cmds
            .iter()
            .filter(|(_, c)| c.contains(fragment))
            .map(|(p, _)| *p)
            .collect()
    }
}

fn table(looks: &[&[(&str, u32)]], stale: &[(u32, &str)]) -> Table {
    Table {
        looks: looks
            .iter()
            .map(|l| {
                Some(
                    l.iter()
                        .map(|(id, p)| ((*id).to_owned(), vec![*p]))
                        .collect(),
                )
            })
            .collect(),
        seen: Cell::new(0),
        stale: stale.iter().map(|(p, f)| (*p, (*f).to_owned())).collect(),
        cmds: Vec::new(),
    }
}

/// [`table`], with live command lines.
fn running(mut t: Table, cmds: &[(u32, &str)]) -> Table {
    t.cmds = cmds.iter().map(|(p, c)| (*p, (*c).to_owned())).collect();
    t
}

/// T184's watch `bx5gtybg3` as the harness ran it: a Monitor, listed as a `shell` (451's event log, 2026-11-23), its command line.
const WATCH: &str = "until grep -q '^ALL DONE' /c/.git/page-session.log; do sleep 60; done";
const WATCH_LINE: &str = "/bin/bash -c eval 'until grep -q '\"'\"'^ALL DONE'\"'\"' /c/.git/page-session.log; do sleep 60; done' < /dev/null";

/// One builder of 385 T02 waiting on its own shell `bx5`, silent `ago` seconds.
fn waiting_builder(tr: &Path, ago: u64) {
    append(tr, r#"{"toolUseResult": {"agentId": "a676"}}"#);
    builder(tr, "a676", "bx5");
    meta(tr, "a676", "385 T02: size edits never change a claim");
    append(tr, &notice("a676", WAITING));
    age(tr, "a676", ago);
}

/// Today's shape, red before the re-read (MODE 4 D12, the gap audit's item 2): the Stop listed the builder's watch - T184's
/// `bx5gtybg3`, a Monitor the harness lists as a `shell`, its stream a pipe - alive then; it ended while the idle check waited, and no
/// Stop came after. The list read at the Stop said the builder had live work, so it was never named (HEAD's reading, the opening
/// assertion); read again after the wait - no process writes its file, none runs its command - the watch has ended, and the builder
/// is named. While its command still runs, or a shell still writes its file, it is live; a command too short to tell, or a table that
/// cannot be read, keeps the entry; an entry typed `monitor` is read the same way.
#[test]
fn a_watch_that_ended_after_the_stop_leaves_its_builder_named_with_no_later_stop() {
    let (_dir, c, tr) = world("stall-reread", "no");
    crate::env::set("SET_DOWN_ROOT", &c);
    crate::env::set("L7R_IDLE_CHECK_SECS", "0");
    waiting_builder(&tr, 2_500);
    let input = |tasks: serde_json::Value| {
        json!({"transcript_path": tr.to_string_lossy(), "cwd": c.to_string_lossy(), "session_id": "s-reread",
               "background_tasks": tasks})
    };
    let watch = json!([{"id": "bx5", "type": "shell", "command": WATCH}]);
    assert_eq!(
        idle_check(&input(watch.clone())),
        None,
        "the list as the Stop gave it"
    );
    let blind = Table {
        looks: vec![None],
        seen: Cell::new(0),
        stale: Vec::new(),
        cmds: Vec::new(),
    };
    assert_eq!(
        idle_check_with(&input(watch.clone()), &blind),
        None,
        "an unread table keeps the list"
    );
    assert_eq!(
        idle_check_with(&input(watch.clone()), &table(&[&[("bx5", 40)]], &[])),
        None,
        "a shell still writing"
    );
    let live = running(table(&[&[]], &[]), &[(41, WATCH_LINE)]);
    assert_eq!(
        idle_check_with(&input(watch.clone()), &live),
        None,
        "its command still runs"
    );
    let typed = json!([{"id": "bx5", "type": "monitor", "command": WATCH}]);
    assert_eq!(
        idle_check_with(&input(typed), &live),
        None,
        "typed monitor: read the same"
    );
    let short = json!([{"id": "bx5", "type": "shell", "command": "sleep 60"}]);
    assert_eq!(
        idle_check_with(&input(short), &table(&[&[]], &[])),
        None,
        "too short to tell"
    );
    let text = idle_check_with(&input(watch), &table(&[&[]], &[]))
        .expect("named once its watch has ended");
    assert!(text.contains("SendMessage to a676"), "{text}");
    crate::env::unset("L7R_IDLE_CHECK_SECS");
    crate::env::unset("SET_DOWN_ROOT");
}

/// While it waits (`L7R_IDLE_WAIT_SECS`), the idle check looks again: at the moment a quiet builder crosses the bound, and each
/// `L7R_IDLE_RECHECK_SECS` while a builder's own run still goes - so a watch that ends after the first look, or a builder that goes
/// quiet as the session's last Stop is written, is named with no Stop after; a turn of the session's own during the wait silences it,
/// and past the budget it says nothing.
#[test]
fn the_idle_check_looks_again_until_its_budget() {
    let (_dir, c, tr) = world("stall-wait", "no");
    crate::env::set("SET_DOWN_ROOT", &c);
    crate::env::set("L7R_IDLE_CHECK_SECS", "0");
    crate::env::set("L7R_IDLE_RECHECK_SECS", "1");
    crate::env::set("L7R_IDLE_WAIT_SECS", "10");
    waiting_builder(&tr, 2_500);
    let input = json!({"transcript_path": tr.to_string_lossy(), "cwd": c.to_string_lossy(), "session_id": "s-wait",
                       "background_tasks": [{"id": "bx5", "type": "shell", "command": WATCH}]});
    let ends = table(&[&[("bx5", 40)], &[("bx5", 40)], &[]], &[]);
    let text = idle_check_with(&input, &ends).expect("named once its watch ends, a look later");
    assert!(text.contains("a676"), "{text}");
    assert_eq!(ends.seen.get(), 3, "three looks");
    // the budget spent with the watch still going: silent
    crate::env::set("L7R_IDLE_WAIT_SECS", "1");
    assert_eq!(
        idle_check_with(&input, &table(&[&[("bx5", 40)]], &[])),
        None
    );
    // a builder that crosses the bound during the wait: named
    let (_dir2, c2, tr2) = world("stall-cross", "no");
    crate::env::set("SET_DOWN_ROOT", &c2);
    crate::env::set("L7R_IDLE_WAIT_SECS", "10");
    crate::env::set("L7R_STALL_SECS", "2");
    waiting_builder(&tr2, 0);
    let quiet = json!({"transcript_path": tr2.to_string_lossy(), "cwd": c2.to_string_lossy(), "session_id": "s-cross",
                       "background_tasks": []});
    let at = std::time::Instant::now();
    let text = idle_check(&quiet).expect("named as it crosses the bound");
    assert!(
        text.contains("silent >2 s") && at.elapsed() >= Duration::from_secs(2),
        "{text}"
    );
    // the session's own turn during that wait: silent
    let (_dir3, c3, tr3) = world("stall-turn", "no");
    crate::env::set("SET_DOWN_ROOT", &c3);
    crate::env::set("L7R_IDLE_WAIT_SECS", "10");
    waiting_builder(&tr3, 0);
    let turned = json!({"transcript_path": tr3.to_string_lossy(), "cwd": c3.to_string_lossy(), "session_id": "s-turn",
                        "background_tasks": []});
    let writer = {
        let tr3 = tr3.clone();
        std::thread::spawn(move || {
            std::thread::sleep(Duration::from_millis(500));
            append(
                &tr3,
                r#"{"type":"user","message":{"role":"user","content":"go on"}}"#,
            );
        })
    };
    assert_eq!(idle_check(&turned), None, "a turn while it waits");
    writer.join().unwrap();
    for k in [
        "L7R_STALL_SECS",
        "L7R_IDLE_WAIT_SECS",
        "L7R_IDLE_RECHECK_SECS",
        "L7R_IDLE_CHECK_SECS",
        "SET_DOWN_ROOT",
    ] {
        crate::env::unset(k);
    }
}

/// The gap audit's item 1: a page session's runner that dies never writes `ALL DONE`, so the wait it printed spins for good. A listed
/// shell whose writer waits on a dead producer is named, with the file and the stop command, once - and is no live work, so the
/// builder it held reads as stalled beside it. A dead-producer waiter that is not this session's listed shell is not named.
#[test]
fn a_listed_waiter_on_a_dead_producer_is_named_and_is_no_live_work() {
    let (_dir, c, tr) = world("stall-waiter", "no");
    crate::env::set("SET_DOWN_ROOT", &c);
    crate::env::set("L7R_IDLE_CHECK_SECS", "0");
    waiting_builder(&tr, 2_500);
    let input = json!({"transcript_path": tr.to_string_lossy(), "cwd": c.to_string_lossy(), "session_id": "s-waiter",
                       "background_tasks": [{"id": "bx5", "type": "shell", "command": WATCH}, {"id": "a9", "type": "subagent"}]});
    let runner_dead = table(
        &[&[("bx5", 300), ("bz", 400)]],
        &[(300, "/c/.git/page-session.log"), (500, "/other.log")],
    );
    let text = idle_check_with(&input, &runner_dead).expect("the waiter is named");
    assert!(
        text.starts_with("A WAITER IS SPINNING ON A DEAD PRODUCER - 1 will never finish:"),
        "{text}"
    );
    assert!(
        text.contains("- task bx5 (pid 300) waits on /c/.git/page-session.log"),
        "{text}"
    );
    assert!(text.contains("then TaskStop bx5."), "{text}");
    assert!(
        text.contains("\nSTALLED: 1 builder(s)") && text.contains("a676"),
        "its builder beside it: {text}"
    );
    assert!(!text.contains("/other.log"), "{text}");
    assert_eq!(
        idle_check_with(&input, &runner_dead),
        None,
        "said once; the sub-agent still listed"
    );
    crate::env::unset("L7R_IDLE_CHECK_SECS");
    crate::env::unset("SET_DOWN_ROOT");
}

/// MODE 4 D10b (FR-006): a builder past the context cap is resumed only by a fresh dispatch from its handoff, so its line says that
/// and no `SendMessage`.
#[test]
fn a_builder_past_the_context_cap_is_named_for_a_fresh_dispatch() {
    let (_dir, c, tr) = world("stall-capped", "no");
    crate::env::set("SET_DOWN_ROOT", &c);
    crate::env::set("L7R_IDLE_CHECK_SECS", "0");
    append(&tr, r#"{"toolUseResult": {"agentId": "a51"}}"#);
    builder(&tr, "a51", "bx1");
    own(
        &tr,
        "a51",
        &format!(
            r#"{{"isSidechain":true,"agentId":"a51","type":"assistant","message":{{"role":"assistant","content":[{{"type":"text","text":"Handoff written."}}],"usage":{{"input_tokens":{}}}}}}}"#,
            crate::context::CAP_TOKENS
        ),
    );
    meta(&tr, "a51", "385 T02: at the cap");
    append(&tr, &notice("a51", WAITING));
    age(&tr, "a51", 2_500);
    let input = json!({"transcript_path": tr.to_string_lossy(), "cwd": c.to_string_lossy(), "session_id": "s-capped",
                       "background_tasks": []});
    let text = idle_check(&input).expect("named");
    assert!(
        text.contains("dispatch a fresh builder from its handoff"),
        "{text}"
    );
    assert!(!text.contains("Wake it"), "{text}");
    crate::env::unset("L7R_IDLE_CHECK_SECS");
    crate::env::unset("SET_DOWN_ROOT");
}

/// Both waits sit under the Idle hook entry's timeout, with a minute for the reads (451 T193): the harness kills a hook past it.
#[test]
fn the_hook_timeout_holds_both_waits() {
    let settings = Path::new(env!("CARGO_MANIFEST_DIR")).join("../../../.claude/settings.json");
    let text = std::fs::read_to_string(settings).unwrap();
    let v: serde_json::Value = serde_json::from_str(&text).unwrap();
    let timeout = v["hooks"]["Stop"]
        .as_array()
        .into_iter()
        .flatten()
        .flat_map(|e| e["hooks"].as_array().into_iter().flatten())
        .find(|h| {
            h["command"]
                .as_str()
                .is_some_and(|c| c.ends_with("l7r-hook Idle"))
        })
        .and_then(|h| h["timeout"].as_u64())
        .expect("the Idle entry's timeout");
    assert!(
        timeout >= super::super::idle::IDLE_SECS + super::super::idle::WAIT_SECS + 60,
        "raise the Idle entry's timeout in .claude/settings.json to IDLE_SECS + WAIT_SECS + 60 s ({timeout} s)"
    );
}

/// THE STATUS PROBE (MODE 4 D11, the task line: "the coordinator's status of a builder comes from that probe, never from its last
/// message"): the list the session's last Stop gave, kept by the idle check, re-read now - each builder of an open task working or
/// stalled, and each dead-producer waiter; no list kept yet, or no clone, says so.
#[test]
fn the_status_probe_says_each_builder_working_or_stalled() {
    let (_dir, c, tr) = world("stall-status", "no");
    crate::env::set("SET_DOWN_ROOT", &c);
    crate::env::set("L7R_IDLE_CHECK_SECS", "0");
    let input = json!({"transcript_path": tr.to_string_lossy(), "cwd": c.to_string_lossy(), "session_id": "s-status",
                       "background_tasks": [{"id": "bx5", "type": "shell", "command": WATCH}, {"id": "bw", "type": "shell"}]});
    let none = table(&[&[]], &[]);
    assert!(status(&input, &none).contains("has no Stop list kept yet"));
    waiting_builder(&tr, 2_500);
    append(&tr, r#"{"toolUseResult": {"agentId": "a8"}}"#);
    builder(&tr, "a8", "bx8");
    meta(&tr, "a8", "385 T03: at work");
    append(&tr, &notice("a8", WAITING));
    age(&tr, "a8", 30);
    append(&tr, r#"{"toolUseResult": {"agentId": "a9"}}"#);
    builder(&tr, "a9", "bx9");
    meta(&tr, "a9", "385 T03: at work too");
    append(&tr, &notice("a9", WAITING));
    age(&tr, "a9", 20);
    let _ = idle_check(&input);
    let said = status(&input, &table(&[&[("bw", 7)]], &[(7, "/c/run.log")]));
    assert!(
        said.starts_with("builder-status: the Stop list of "),
        "{said}"
    );
    assert!(
        said.contains("- a8 \"385 T03: at work\": working, its transcript moved"),
        "{said}"
    );
    assert!(
        said.contains("- a676 \"385 T02") && said.contains("Wake it"),
        "{said}"
    );
    assert!(
        said.contains("- task bw (pid 7) waits on /c/run.log"),
        "{said}"
    );
    let busy = status(&input, &table(&[&[("bx5", 9)]], &[]));
    assert!(
        busy.contains("- a676 \"385 T02: size edits never change a claim\": working, its own run"),
        "{busy}"
    );
    crate::env::unset("SET_DOWN_ROOT");
    let nowhere =
        json!({"transcript_path": tr.to_string_lossy(), "cwd": "/", "session_id": "s-status"});
    assert!(
        status(&nowhere, &none).contains("no clone"),
        "{}",
        status(&nowhere, &none)
    );
    let mut listed = nowhere.clone();
    listed["background_tasks"] = json!([]);
    assert_eq!(idle_check(&listed), None, "no clone: nothing named");
    assert!(
        super::super::idle::Blind.stale().is_empty(),
        "the unread table names no waiter"
    );
    assert!(
        super::super::idle::Blind.running(WATCH).is_empty(),
        "nor a running command"
    );
    std::fs::remove_dir_all(c.join("specs")).unwrap();
    crate::env::set("SET_DOWN_ROOT", &c);
    assert!(status(&input, &none).ends_with("No builder of an open task reads as running."));
    crate::env::unset("L7R_IDLE_CHECK_SECS");
    crate::env::unset("SET_DOWN_ROOT");
}
