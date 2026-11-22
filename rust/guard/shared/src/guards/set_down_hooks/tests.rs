//! The decider over a fixture clone, the status line read in process (feature 449 T118); `tests/hooks/test-set-down-hooks.sh` replays
//! the guard through the shim.

use std::path::{Path, PathBuf};

use serde_json::json;

use super::{decide, judge, next_performance, open_boxes, performance, verdict, OpenTask};
use crate::protocol::{Answer, Event};
use crate::session::Session;
use crate::tool::ask;

const TASKS: &str = "- [x] T01 done\n- [ ] T02 the next thing\n- [ ] T03 later\n- [ ] GM review (make gm-reviewed F=385)\n";
// T03 started too (451 T88): with no task left never started, work running lets the turn end whatever the builder count
const START: &str = "{\"feature\": \"385-x\", \"task\": \"T03\", \"utc\": \"2026-10-18T22:00:00Z\"}\n{\"feature\": \"385-x\", \"task\": \"T02\", \"utc\": \"2026-10-18T23:00:00Z\"}\n";

/// A clone with a started feature and an empty transcript; `closed` gives its spec a status line that closes it.
fn world(tag: &str, closed: &str) -> (crate::tempdir::TempDir, PathBuf, PathBuf) {
    crate::log::quiet();
    let d = crate::tempdir::TempDir::new(&format!("guard-setdown-{tag}"));
    std::fs::create_dir_all(d.join("c/specs/385-x")).unwrap();
    let (keep, d) = {
        let canon = d.canonicalize().unwrap();
        (d, canon)
    };
    let c = d.join("c");
    assert!(ask(
        Path::new("/"),
        "git",
        &["init", "-q", &c.to_string_lossy()],
        ""
    )
    .ok());
    std::fs::write(c.join("specs/385-x/tasks.md"), TASKS).unwrap();
    std::fs::write(c.join(".git/task-starts.jsonl"), START).unwrap();
    let status = if closed == "yes" {
        "Done (2026-10-19)"
    } else {
        "Implemented"
    };
    std::fs::write(
        c.join("specs/385-x/spec.md"),
        format!("# F\n\n**Status**: {status}\n"),
    )
    .unwrap();
    std::fs::write(d.join("tr.jsonl"), "").unwrap();
    (keep, c, d.join("tr.jsonl"))
}

fn said(c: &Path, tr: &Path) -> Option<String> {
    verdict(c, &tr.to_string_lossy()).unwrap()
}

fn append(tr: &Path, line: &str) {
    let old = std::fs::read_to_string(tr).unwrap();
    std::fs::write(tr, format!("{old}{line}\n")).unwrap();
}

#[test]
fn an_open_task_with_nothing_running_is_refused_naming_the_next_step() {
    let (_dir, c, tr) = world("refuse", "no");
    let text = said(&c, &tr).unwrap();
    assert!(text.contains("feature 385-x has 2 open task(s)"));
    assert!(text.contains("(T02 the next thing)"));
    assert!(text.contains("make set-down F=385 WHY="));
}

#[test]
fn work_still_running_lets_the_turn_end_until_it_reports_back() {
    let (_dir, c, tr) = world("running", "no");
    append(&tr, r#"{"toolUseResult": {"backgroundTaskId": "b1abc"}}"#);
    assert_eq!(said(&c, &tr), None);
    append(
        &tr,
        "<task-notification><task-id>b1abc</task-id></task-notification>",
    );
    assert!(said(&c, &tr).is_some());
    append(&tr, r#"{"toolUseResult": {"agentId": "a9f00"}}"#);
    assert_eq!(said(&c, &tr), None);
    append(
        &tr,
        r#"{"name": "TaskStop", "input": {"task_id": "a9f00"}}"#,
    );
    assert!(said(&c, &tr).is_some());
    append(&tr, r#"{"status": "async_launched", "taskId": "w9wave"}"#);
    assert_eq!(said(&c, &tr), None);
    append(&tr, "<task-id>w9wave</task-id>");
    append(&tr, "Command running in background with ID: b4note.");
    assert!(said(&c, &tr).is_some());
}

// 451 T65: the shapes as Claude Code writes them, read 2026-11-21 from a session's transcript (`c6fd72d1-...jsonl`, grep -o): a notice
// JSON-escaped in a user line, an interim one saying the agent "is waiting on its own background work"; a SendMessage resume's
// `resumedAgentId` in its `toolUseResult`, unescaped there and escaped in the text the model reads.
const WAITING: &str = r#"Agent \"build it\" is waiting on its own background work"#;
const FINISHED: &str = r#"Agent \"build it\" finished"#;

fn notice(id: &str, summary: &str) -> String {
    let note = if summary == WAITING {
        r"\n<note>This agent stopped with background work of its own still running. It may resume on its own when that work completes or reports, and the same task-id notifies again if it does; the result below may be interim.</note>"
    } else {
        ""
    };
    format!(
        r#"{{"type":"user","message":{{"role":"user","content":"<task-notification>\n<task-id>{id}</task-id>\n<output-file>/tmp/x/{id}.output</output-file>\n<status>completed</status>\n<summary>{summary}</summary>{note}\n<result>done</result>\n</task-notification>"}}}}"#
    )
}

fn resume(id: &str) -> String {
    format!(
        r#"{{"type":"user","message":{{"role":"user","content":[{{"type":"tool_result","content":[{{"type":"text","text":"{{\"success\":true,\"message\":\"Resuming agent {id}\",\"resumedAgentId\":\"{id}\"}}"}}]}}]}},"toolUseResult":{{"success":true,"message":"Resuming agent {id}","resumedAgentId":"{id}","revivedAgentId":"{id}"}}}}"#
    )
}

fn end_turn(id: &str) -> String {
    format!(
        r#"{{"isSidechain":true,"agentId":"{id}","message":{{"role":"assistant","content":[{{"type":"text","text":"done"}}],"stop_reason":"end_turn"}}}}"#
    )
}

/// A line of agent `id`'s own transcript, `<transcript stem>/subagents/agent-<id>.jsonl` as Claude Code keeps it.
fn own(tr: &Path, id: &str, line: &str) {
    let dir = tr.with_extension("").join("subagents");
    std::fs::create_dir_all(&dir).unwrap();
    let file = dir.join(format!("agent-{id}.jsonl"));
    if !file.is_file() {
        std::fs::write(&file, "").unwrap();
    }
    append(&file, line);
}

#[test]
fn a_resumed_agent_runs_until_its_next_final_notice_and_a_replay_ends_nothing() {
    let (_dir, c, tr) = world("resume", "no");
    append(&tr, r#"{"toolUseResult": {"agentId": "a1"}}"#);
    append(&tr, &notice("a1", FINISHED));
    assert!(said(&c, &tr).is_some());
    append(&tr, &resume("a1"));
    assert_eq!(said(&c, &tr), None, "a SendMessage resume is a launch");
    // a request blob re-emits the history: its copy of the old notice is no notice (no task-id of 6,636 in 12 transcripts is
    // named in a blob alone, measured 2026-11-21)
    append(
        &tr,
        &notice("a1", FINISHED).replacen(r#"{"type":"user""#, r#"{"type":"api-request-blob""#, 1),
    );
    assert_eq!(said(&c, &tr), None, "a blob's replay ends nothing");
    append(&tr, &notice("a1", FINISHED));
    assert!(said(&c, &tr).is_some());
}

#[test]
fn an_interim_notice_ends_nothing_while_the_agent_s_own_work_runs_or_has_woken_it() {
    let (_dir, c, tr) = world("interim", "no");
    append(&tr, r#"{"toolUseResult": {"agentId": "a2"}}"#);
    own(
        &tr,
        "a2",
        r#"{"isSidechain":true,"agentId":"a2","toolUseResult":{"backgroundTaskId":"b7"}}"#,
    );
    own(&tr, "a2", &end_turn("a2"));
    append(&tr, &notice("a2", WAITING));
    assert_eq!(said(&c, &tr), None, "its own background work runs");
    own(
        &tr,
        "a2",
        &notice(
            "b7",
            r#"Background command \"make done\" completed (exit code 0)"#,
        ),
    );
    // woken by its work's notice, it is mid-turn
    assert_eq!(said(&c, &tr), None);
    // its final message's thinking, a record of its own written before the text, carries `end_turn` too
    own(
        &tr,
        "a2",
        r#"{"isSidechain":true,"agentId":"a2","message":{"role":"assistant","content":[{"type":"thinking","thinking":""}],"stop_reason":"end_turn"}}"#,
    );
    assert_eq!(said(&c, &tr), None, "still writing its answer");
    own(&tr, "a2", &end_turn("a2"));
    // its work ended and its turn ended with nothing since: it will not notify again (8 of 58 such agents never did, 2026-11-21)
    assert!(said(&c, &tr).is_some(), "stale");
    own(
        &tr,
        "a2",
        r#"{"isSidechain":true,"agentId":"a2","toolUseResult":{"backgroundTaskId":"b8"}}"#,
    );
    assert_eq!(said(&c, &tr), None);
    append(&tr, &notice("a2", FINISHED));
    // a final notice after an interim one ends it
    assert!(said(&c, &tr).is_some());
}

#[test]
fn an_interim_agent_with_no_transcript_of_its_own_is_not_running() {
    let (_dir, c, tr) = world("nofile", "no");
    append(&tr, r#"{"toolUseResult": {"agentId": "a3"}}"#);
    append(&tr, &notice("a3", WAITING));
    assert!(said(&c, &tr).is_some());
}

/// One agent asked by the same reading (451 T85, `finished_run_hooks`' reader): launched, interim with its own work running, ended.
#[test]
fn one_agent_is_asked_by_the_same_reading() {
    use super::still_running;
    let (_dir, _c, tr) = world("one", "no");
    assert!(!still_running(&tr, "a5").unwrap(), "never named");
    append(&tr, r#"{"toolUseResult": {"agentId": "a5"}}"#);
    assert!(still_running(&tr, "a5").unwrap());
    append(&tr, &notice("a5", WAITING));
    // interim, and no transcript of its own
    assert!(!still_running(&tr, "a5").unwrap());
    own(
        &tr,
        "a5",
        r#"{"isSidechain":true,"agentId":"a5","toolUseResult":{"backgroundTaskId":"b9"}}"#,
    );
    // interim, its own work running
    assert!(still_running(&tr, "a5").unwrap());
    append(&tr, &notice("a5", FINISHED));
    assert!(!still_running(&tr, "a5").unwrap());
    assert!(still_running(&tr.with_extension("gone"), "a5").is_err());
}

#[test]
fn a_line_s_notices_are_read_in_their_order_each_by_its_own_summary() {
    let (_dir, c, tr) = world("order", "no");
    append(&tr, r#"{"toolUseResult": {"agentId": "a4"}}"#);
    own(&tr, "a4", r#"{"toolUseResult":{"backgroundTaskId":"b9"}}"#);
    let interim = notice("a4", WAITING);
    let last = notice("a4", FINISHED);
    // one record holding an interim notice and the final one after it, as a delivered batch does (line 42866 of the session above)
    append(&tr, &format!("{interim} {last}"));
    assert!(said(&c, &tr).is_some());
    append(&tr, &format!("{last} {interim}"));
    assert_eq!(said(&c, &tr), None);
    // a summary past the notice's close is not its summary
    append(
        &tr,
        &format!("<task-notification><task-id>a4</task-id></task-notification> <summary>{WAITING}</summary>"),
    );
    assert!(said(&c, &tr).is_some());
}

#[test]
fn an_interim_sub_agent_is_read_through_its_own_transcript_and_a_cycle_ends() {
    let (_dir, c, tr) = world("nested", "no");
    append(&tr, r#"{"toolUseResult": {"agentId": "a5"}}"#);
    append(&tr, &notice("a5", WAITING));
    own(&tr, "a5", r#"{"toolUseResult":{"agentId":"a6"}}"#);
    own(&tr, "a5", &notice("a6", WAITING));
    own(&tr, "a5", &end_turn("a5"));
    own(&tr, "a6", &notice("a5", WAITING));
    own(&tr, "a6", &end_turn("a6"));
    // nothing of either runs, and the cycle ends
    assert!(said(&c, &tr).is_some());
    own(&tr, "a6", r#"{"toolUseResult":{"backgroundTaskId":"b10"}}"#);
    assert_eq!(said(&c, &tr), None, "the sub-agent's own work runs");
}

#[test]
fn a_set_down_since_the_start_or_a_closing_status_lets_it_end() {
    let (_dir, c, tr) = world("down", "no");
    let log = c.join(".git/set-downs.jsonl");
    std::fs::write(
        &log,
        "{\"feature\": \"385-x\", \"utc\": \"2026-10-18T22:00:00Z\"}\nnot json\n",
    )
    .unwrap();
    assert!(said(&c, &tr).is_some());
    std::fs::write(
        &log,
        "{\"feature\": \"999-y\", \"utc\": \"2026-10-19T00:00:00Z\"}\n",
    )
    .unwrap();
    assert!(said(&c, &tr).is_some());
    std::fs::write(
        &log,
        "{\"feature\": \"385-x\", \"utc\": \"2026-10-18T23:00:00Z\"}\n",
    )
    .unwrap();
    assert_eq!(said(&c, &tr), None);
    let (_dir, c2, tr2) = world("closed", "yes");
    assert_eq!(said(&c2, &tr2), None);
}

#[test]
fn no_feature_begun_or_only_the_gms_box_passes() {
    let (_dir, c, tr) = world("none", "no");
    std::fs::write(
        c.join("specs/385-x/tasks.md"),
        "- [x] T02 done\n- [ ] GM review (make gm-reviewed F=385)\n",
    )
    .unwrap();
    assert_eq!(said(&c, &tr), None);
    std::fs::write(c.join(".git/task-starts.jsonl"), "{\"utc\": \"x\"}\n").unwrap();
    assert_eq!(said(&c, &tr), None);
    std::fs::remove_file(c.join(".git/task-starts.jsonl")).unwrap();
    assert_eq!(said(&c, &tr), None);
    assert_eq!(verdict(&c, "/no/such/transcript").unwrap(), None);
    assert_eq!(open_boxes(TASKS).len(), 2);
}

#[test]
fn a_read_error_lets_the_turn_end_recorded() {
    let (_dir, c, tr) = world("error", "no");
    std::fs::write(c.join("specs/385-x/tasks.md"), [0xff_u8, 0xfe]).unwrap();
    let e = Event {
        name: "Stop".to_owned(),
        input: json!({"cwd": c, "transcript_path": tr}),
    };
    let session = Session::from_input(&e.input);
    assert!(verdict(&c, "").is_err());
    assert!(judge(&e, &session, Some(c.to_string_lossy().into_owned())).is_empty());
    std::fs::write(c.join("specs/385-x/tasks.md"), TASKS).unwrap();
    std::fs::write(c.join(".git/task-starts.jsonl"), [0xff_u8]).unwrap();
    assert!(verdict(&c, "").is_err());
    assert!(verdict(Path::new("/no/such/place"), "").is_err());
    std::fs::write(c.join(".git/task-starts.jsonl"), START).unwrap();
    assert!(verdict(&c, "/proc/self/mem").is_err());
}

#[test]
fn the_root_is_the_seam_else_the_work_tree() {
    let (_dir, c, tr) = world("root", "no");
    let at = c.to_string_lossy().into_owned();
    let run = |cwd: &str, seam: Option<String>| {
        let e = Event {
            name: "Stop".to_owned(),
            input: json!({"cwd": cwd, "transcript_path": tr}),
        };
        judge(&e, &Session::from_input(&e.input), seam)
    };
    assert!(matches!(&run("", Some(at.clone()))[..], [Answer::Refuse(t)] if t.contains("T02")));
    assert!(matches!(
        &run(&at, Some("/no/such".to_owned()))[..],
        [Answer::Refuse(_)]
    ));
    assert!(matches!(&run(&at, None)[..], [Answer::Refuse(_)]));
    assert!(run("/no/such/place", None).is_empty());
    std::fs::remove_file(c.join(".git/task-starts.jsonl")).unwrap();
    assert!(run(&at, None).is_empty());
    let e = Event {
        name: "Stop".to_owned(),
        input: json!({"cwd": "/no/such/place"}),
    };
    assert!(decide(&e, &Session::from_input(&e.input)).is_empty());
}

/// T28's own line, which quotes `[perf]` in its prose: a performance task by its tag alone (feature 451 FR-013).
const T28: &str = "[perf] Performance work goes first (FR-013, the GM 2026-11-20): a [perf] tag or PERF=1 marks a task";

#[test]
fn performance_work_is_its_tag_after_the_id_or_the_checklist_perf_1_writes() {
    assert!(performance("T28", T28, ""));
    assert!(performance("T03", "[P] [US1] [perf] x", ""));
    assert!(performance("T03", "[perf]", ""));
    // a tag quoted in prose, a word that only starts with it, or a tag after the title's first words is no mark
    assert!(!performance("T05", "a [perf] tag quoted in the title", ""));
    assert!(!performance("T05", "[perf-ish] x", ""));
    assert!(!performance("T05", "[P] x [perf]", ""));
    // `make task-add ... PERF=1`'s mark: the section's checklist heading, its own id's alone
    let plan = "### T07 (why)\n\n### T07 Performance checklist (docs/performance-checklist.md - prompts)\n";
    assert!(performance("T07", "the title", plan));
    assert!(!performance("T70", "the title", plan));
    assert!(!performance("T0", "the title", plan));
}

/// A second feature started in the clone: its tasks, its start, its status.
fn second(c: &Path, tasks: &str, utc: &str, status: &str) {
    std::fs::create_dir_all(c.join("specs/386-y")).unwrap();
    std::fs::write(c.join("specs/386-y/tasks.md"), tasks).unwrap();
    std::fs::write(
        c.join("specs/386-y/spec.md"),
        format!("# F\n\n**Status**: {status}\n"),
    )
    .unwrap();
    let starts =
        format!("{{\"feature\": \"386-y\", \"task\": \"T01\", \"utc\": \"{utc}\"}}\n{START}");
    std::fs::write(c.join(".git/task-starts.jsonl"), starts).unwrap();
}

fn open(feature: &str, id: &str, title: &str) -> OpenTask {
    OpenTask {
        feature: feature.to_owned(),
        id: id.to_owned(),
        title: title.to_owned(),
    }
}

#[test]
fn the_stop_names_an_open_performance_task_before_any_other() {
    let (_dir, c, tr) = world("perf", "no");
    std::fs::write(
        c.join("specs/385-x/tasks.md"),
        "- [ ] T02 the next thing\n- [ ] T03 [perf] the faster gate\n",
    )
    .unwrap();
    let text = said(&c, &tr).unwrap();
    assert!(text.contains("(T03 [perf] the faster gate - performance work first, FR-013: make task-start F=385 T=T03)"), "{text}");
    assert!(!text.contains("T02 the next thing"), "{text}");
    // PERF=1's checklist marks T02, the first in the list
    std::fs::write(
        c.join("specs/385-x/plan.md"),
        "### T02 Performance checklist (prompts)\n",
    )
    .unwrap();
    assert!(said(&c, &tr)
        .unwrap()
        .contains("make task-start F=385 T=T02"));
}

#[test]
fn another_active_feature_s_performance_task_is_named_until_it_is_set_down_or_closed() {
    let (_dir, c, tr) = world("perf-other", "no");
    second(
        &c,
        "- [ ] T04 [perf] split the suite\n- [ ] GM review (make gm-reviewed F=386)\n",
        "2026-10-18T22:00:00Z",
        "Draft",
    );
    let git = c.join(".git");
    let text = said(&c, &tr).unwrap();
    assert!(text.contains("feature 385-x has 2 open task(s)"), "{text}");
    assert!(text.contains("(T04 [perf] split the suite of 386-y - performance work first, FR-013: make task-start F=386 T=T04)"), "{text}");
    assert_eq!(
        next_performance(&c, &git, "385-x").unwrap(),
        Some(open("386-y", "T04", "[perf] split the suite"))
    );
    // the feature preferred first, then the most recent start
    std::fs::write(
        c.join("specs/385-x/tasks.md"),
        "- [ ] T02 [perf] mine first\n",
    )
    .unwrap();
    assert_eq!(
        next_performance(&c, &git, "385-x").unwrap(),
        Some(open("385-x", "T02", "[perf] mine first"))
    );
    std::fs::write(c.join("specs/385-x/tasks.md"), TASKS).unwrap();
    // set down since its own last start: not active
    std::fs::write(
        git.join("set-downs.jsonl"),
        "{\"feature\": \"386-y\", \"utc\": \"2026-10-18T22:30:00Z\"}\n",
    )
    .unwrap();
    assert_eq!(next_performance(&c, &git, "385-x").unwrap(), None);
    assert!(said(&c, &tr).unwrap().contains("(T02 the next thing)"));
    // ...but the feature being started counts whatever was set down (its start resets it)
    assert_eq!(
        next_performance(&c, &git, "386-y").unwrap(),
        Some(open("386-y", "T04", "[perf] split the suite"))
    );
    // closed by its status line: not active, even preferred
    std::fs::remove_file(git.join("set-downs.jsonl")).unwrap();
    second(
        &c,
        "- [ ] T04 [perf] split the suite\n",
        "2026-10-18T22:00:00Z",
        "Done (2026-10-19)",
    );
    assert_eq!(next_performance(&c, &git, "386-y").unwrap(), None);
    // never started in this clone and not preferred: not active
    std::fs::write(c.join(".git/task-starts.jsonl"), START).unwrap();
    second(
        &c,
        "- [ ] T04 [perf] split the suite\n",
        "2026-10-18T22:00:00Z",
        "Draft",
    );
    std::fs::write(c.join(".git/task-starts.jsonl"), START).unwrap();
    assert_eq!(next_performance(&c, &git, "385-x").unwrap(), None);
    // no feature preferred, none started
    std::fs::remove_file(c.join(".git/task-starts.jsonl")).unwrap();
    assert_eq!(next_performance(&c, &git, "").unwrap(), None);
    assert_eq!(next_performance(&c, &git, "999-gone").unwrap(), None);
}

#[test]
fn the_performance_reader_s_read_errors_are_errors() {
    let (_dir, c, _tr) = world("perf-error", "no");
    let git = c.join(".git");
    std::fs::write(c.join("specs/385-x/plan.md"), [0xff_u8]).unwrap();
    assert!(next_performance(&c, &git, "385-x").is_err());
    std::fs::remove_file(c.join("specs/385-x/plan.md")).unwrap();
    std::fs::write(c.join("specs/385-x/tasks.md"), [0xff_u8]).unwrap();
    assert!(next_performance(&c, &git, "385-x").is_err());
    std::fs::write(c.join("specs/385-x/tasks.md"), TASKS).unwrap();
    std::fs::write(git.join("set-downs.jsonl"), [0xff_u8]).unwrap();
    assert!(next_performance(&c, &git, "385-x").is_err());
    std::fs::remove_file(git.join("set-downs.jsonl")).unwrap();
    std::fs::write(git.join("task-starts.jsonl"), [0xff_u8]).unwrap();
    assert!(next_performance(&c, &git, "385-x").is_err());
}

/// A running agent of the session with its meta file, as Claude Code keeps one beside the transcript.
fn agent(tr: &Path, id: &str, depth: u64, description: &str) {
    append(
        tr,
        &format!(r#"{{"toolUseResult": {{"agentId": "{id}"}}}}"#),
    );
    let dir = tr.with_extension("").join("subagents");
    std::fs::create_dir_all(&dir).unwrap();
    std::fs::write(
        dir.join(format!("agent-{id}.meta.json")),
        json!({"spawnDepth": depth, "description": description}).to_string(),
    )
    .unwrap();
}

/// 451 T88: ROLLING DISPATCH. Two builders run (T02 editing `rust/x/alpha.rs`, T03); a review agent and a builder's own helper are not
/// builders. Of the open tasks never started, T04 (performance work) names T02's file and T05 comes after T04, so T06 is named - with
/// task-start's escape, since T04 is open performance work - until a third builder runs, the knob is met, or no task is left.
#[test]
fn a_free_builder_slot_names_the_next_independent_open_task() {
    let (_dir, c, tr) = world("roll", "no");
    let events = c.join("events");
    std::fs::create_dir_all(&events).unwrap();
    crate::env::set("L7R_EVENTS_DIR", &events);
    crate::env::unset("L7R_BUILDERS");
    let edit = |task: &str, rel: &str, extra: &str| {
        format!(
            r#"{{"t":"2026-10-18T23:10:00Z","ev":"PostToolUse","tool":"Edit","cat":"edit","by":"a1","path":"{}/{rel}","task":"{task}"{extra}}}"#,
            c.display()
        )
    };
    std::fs::write(
        events.join("385-x.jsonl"),
        [
            edit("T02", "rust/x/alpha.rs", ""),
            edit("T02", "specs/385-x/plan.md", ""),
            edit("T03", "rust/x/delta.rs", r#","fallback":true"#),
            r#"{"ev":"PostToolUse","cat":"edit","not json"#.to_owned(),
            edit("T09", "rust/x/epsilon.rs", ""),
        ]
        .join("\n"),
    )
    .unwrap();
    std::fs::write(
        c.join("specs/385-x/tasks.md"),
        "- [x] T01 done\n- [ ] T02 the next thing\n- [ ] T03 later\n- [ ] T04 [perf] a faster `rust/x/alpha.rs`\n- [ ] T05 tidy after T04\n- [ ] T06 the gamma tool in `scripts/gamma.sh` and delta.rs and tests.rs\n- [ ] T07 epsilon.rs\n- [ ] GM review (make gm-reviewed F=385)\n",
    )
    .unwrap();
    agent(&tr, "a1", 1, "385 T02: the next thing");
    agent(&tr, "a2", 1, "385 T03 (fresh): later");
    agent(&tr, "r1", 1, "spec-fidelity on 385's changed blocks");
    agent(&tr, "h1", 2, "385 T02: a builder's own helper");
    let text = said(&c, &tr).unwrap();
    let free = text.contains("a builder slot is free - 2 of 3 builders running (385 T02, 385 T03)");
    assert!(free, "{text}");
    assert!(text.contains("(T06 the gamma tool"), "{text}");
    assert!(text.contains("PERF_LATER_OK=\"385 T04, the open performance work, is started or touches a running task's files\" make task-start F=385 T=T06"), "{text}");
    assert!(text.contains("make set-down F=385 WHY="), "{text}");
    // a performance task free to start is named first, with no escape
    std::fs::write(
        c.join("specs/385-x/tasks.md"),
        "- [ ] T02 the next thing\n- [ ] T03 later\n- [ ] T06 the gamma tool\n- [ ] T08 [perf] a faster beta\n",
    )
    .unwrap();
    let text = said(&c, &tr).unwrap();
    let first = text.contains("(T08 [perf] a faster beta): make task-start F=385 T=T08,");
    assert!(first, "{text}");
    // the knob met: two builders of two
    crate::env::set("L7R_BUILDERS", "2");
    assert_eq!(said(&c, &tr), None);
    crate::env::set("L7R_BUILDERS", "3");
    // a third builder running: no slot free
    agent(&tr, "a3", 1, "385 T08: a faster beta");
    assert_eq!(said(&c, &tr), None);
    append(&tr, &notice("a3", FINISHED));
    assert!(said(&c, &tr).unwrap().contains("2 of 3 builders running"));
    // nothing left never started
    let starts = std::fs::read_to_string(c.join(".git/task-starts.jsonl")).unwrap();
    std::fs::write(
        c.join(".git/task-starts.jsonl"),
        format!("{starts}{{\"feature\": \"385-x\", \"task\": \"T06\", \"utc\": \"2026-10-19T00:00:00Z\"}}\n{{\"feature\": \"385-x\", \"task\": \"T08\", \"utc\": \"2026-10-19T00:00:00Z\"}}\n"),
    )
    .unwrap();
    assert_eq!(said(&c, &tr), None);
    crate::env::unset("L7R_EVENTS_DIR");
}

/// 451 T88: a running builder whose feature has no directory or no log names no file; one in another feature is counted all the same.
#[test]
fn a_running_builder_with_no_log_names_no_file() {
    let (_dir, c, tr) = world("roll-nolog", "no");
    crate::env::set("L7R_EVENTS_DIR", c.join("no-events"));
    crate::env::unset("L7R_BUILDERS");
    std::fs::write(
        c.join("specs/385-x/tasks.md"),
        "- [ ] T02 the next thing\n- [ ] T03 later\n- [ ] T04 alpha.rs\n",
    )
    .unwrap();
    agent(&tr, "a1", 1, "385 T02: the next thing");
    agent(&tr, "a2", 1, "999 T01: a feature with no directory");
    let text = said(&c, &tr).unwrap();
    let counted = text.contains("2 of 3 builders running (385 T02, 999 T01)");
    assert!(counted, "{text}");
    assert!(text.contains("make task-start F=385 T=T04,"), "{text}");
    crate::env::unset("L7R_EVENTS_DIR");
}

/// 451 T88 (its plan review, 2026-11-21): PERFORMANCE WORK FIRST ACROSS EVERY ACTIVE FEATURE (FR-013) - another active feature's open
/// performance task is named before the started feature's own task that is not performance work.
#[test]
fn a_free_slot_names_another_feature_s_performance_task_first() {
    let (_dir, c, tr) = world("roll-perf", "no");
    let events = c.join("events");
    std::fs::create_dir_all(&events).unwrap();
    crate::env::set("L7R_EVENTS_DIR", &events);
    crate::env::unset("L7R_BUILDERS");
    std::fs::write(
        c.join("specs/385-x/tasks.md"),
        "- [ ] T02 the next thing\n- [ ] T03 later\n- [ ] T04 a plain tool\n",
    )
    .unwrap();
    std::fs::create_dir_all(c.join("specs/386-y")).unwrap();
    std::fs::write(
        c.join("specs/386-y/tasks.md"),
        "- [ ] T01 [perf] a faster gate\n",
    )
    .unwrap();
    std::fs::write(
        c.join("specs/386-y/spec.md"),
        "# F\n\n**Status**: Implemented\n",
    )
    .unwrap();
    let other = r#"{"feature": "386-y", "task": "T00", "utc": "2026-10-18T21:00:00Z"}"#;
    std::fs::write(
        c.join(".git/task-starts.jsonl"),
        format!("{other}\n{START}"),
    )
    .unwrap();
    agent(&tr, "a1", 1, "385 T02: the next thing");
    let text = said(&c, &tr).unwrap();
    let first = text.contains("(T01 [perf] a faster gate): make task-start F=386 T=T01,");
    assert!(first, "{text}");
    crate::env::unset("L7R_EVENTS_DIR");
}

/// 451 T88: what `free_slot` cannot read is an error, never a free slot: a running task's event log that is not text, the feature's
/// plan that is not text, and an interim builder's own transcript that cannot be opened.
#[test]
fn a_free_slot_s_unreadable_reads_are_errors() {
    use std::os::unix::fs::PermissionsExt;
    let (_dir, c, tr) = world("roll-errors", "no");
    let events = c.join("events");
    std::fs::create_dir_all(&events).unwrap();
    crate::env::set("L7R_EVENTS_DIR", &events);
    crate::env::unset("L7R_BUILDERS");
    agent(&tr, "a1", 1, "385 T02: the next thing");
    let at = tr.to_string_lossy().into_owned();
    std::fs::write(events.join("385-x.jsonl"), b"\xff\xfe\n").unwrap();
    assert!(verdict(&c, &at).is_err());
    std::fs::remove_file(events.join("385-x.jsonl")).unwrap();
    std::fs::write(c.join("specs/385-x/plan.md"), b"\xff\xfe\n").unwrap();
    assert!(verdict(&c, &at).is_err());
    std::fs::remove_file(c.join("specs/385-x/plan.md")).unwrap();
    assert!(verdict(&c, &at).is_ok());
    agent(&tr, "a2", 1, "385 T03: later");
    append(&tr, &notice("a2", WAITING));
    let own = tr.with_extension("").join("subagents/agent-a2.jsonl");
    std::fs::write(&own, "").unwrap();
    std::fs::set_permissions(&own, std::fs::Permissions::from_mode(0o000)).unwrap();
    assert!(verdict(&c, &at).is_err());
    std::fs::set_permissions(&own, std::fs::Permissions::from_mode(0o644)).unwrap();
    crate::env::unset("L7R_EVENTS_DIR");
}

/// 451 T102: a land `end` line of the feature's event log, as `make land` writes one (its `tasks`, or `task` alone).
fn landed(tasks: &str, t1: &str, ok: bool) -> String {
    format!(
        r#"{{"ev":"Phase","src":"land","step":"end","t1":"{t1}","code":0,"make":"land",{tasks},"landed":{ok}}}"#
    )
}

/// 451 T102: A WAIT THE HOOK READS. A task line's `(waits: <when>)` right after its tags holds it from the free-slot reading until its
/// wait is met - a full day after the latest landing of the tasks it names (T11 landed twice, T12's line names it by `task` alone, T13
/// landed before the log carried end lines, a refused landing counts for nothing), or a landing - and so do `after T<n>` an open task
/// and an open task's line saying it `lands before` it; a clause the line only quotes in its prose is no wait.
#[test]
fn a_free_slot_skips_a_task_whose_wait_is_not_met() {
    let (_dir, c, tr) = world("roll-waits", "no");
    let events = c.join("events");
    std::fs::create_dir_all(&events).unwrap();
    crate::env::set("L7R_EVENTS_DIR", &events);
    crate::env::unset("L7R_BUILDERS");
    crate::env::set("L7R_WAITS_NOW", "2026-11-21T20:00:00Z");
    std::fs::write(
        events.join("385-x.jsonl"),
        [
            landed(r#""tasks":["T11"]"#, "2026-11-20T10:00:00Z", true),
            landed(r#""task":"T12""#, "2026-11-21T08:00:27.560Z", true),
            landed(r#""tasks":["T11","T12"]"#, "2026-11-21T19:00:00Z", false),
            landed(r#""tasks":["T13"]"#, "not a time", true),
            r#"{"src":"land","step":"end" not json"#.to_owned(),
        ]
        .join("\n"),
    )
    .unwrap();
    let tasks = |seventh: &str| {
        format!("- [x] T01 done\n- [ ] T02 the next thing\n- [ ] T03 later\n- [ ] T04 [perf] (waits: a full day after T11-T13 land) the measured day\n- [ ] T05 [perf] (waits: T03 lands) the third's follow-up\n- [ ] T06 [perf] (waits: T07 lands) the seventh's follow-up\n- [{seventh}] T07 the landing T06 waits on, which lands before T08\n- [ ] T08 [perf] held by the seventh's line\n- [ ] T09 a line that quotes a (waits: 2999-01-01) clause in its prose\n- [x] T11 eleven\n- [x] T12 twelve\n- [x] T13 thirteen\n")
    };
    std::fs::write(c.join("specs/385-x/tasks.md"), tasks(" ")).unwrap();
    agent(&tr, "a1", 1, "385 T02: the next thing");
    // every performance task waits, so the first other task is named, with no escape: no open performance task can start
    let text = said(&c, &tr).unwrap();
    let seventh = text.contains(
        "(T07 the landing T06 waits on, which lands before T08): make task-start F=385 T=T07,",
    );
    assert!(seventh, "{text}");
    assert!(!text.contains("PERF_LATER_OK"), "{text}");
    let start = |task: &str| {
        let starts = std::fs::read_to_string(c.join(".git/task-starts.jsonl")).unwrap();
        let row =
            format!(r#"{{"feature": "385-x", "task": "{task}", "utc": "2026-11-21T19:00:00Z"}}"#);
        std::fs::write(c.join(".git/task-starts.jsonl"), format!("{starts}{row}\n")).unwrap();
    };
    // a clause quoted in the prose is no wait
    start("T07");
    let ninth = said(&c, &tr)
        .unwrap()
        .contains("make task-start F=385 T=T09,");
    assert!(ninth);
    // the seventh landed: its follow-up and the task its line held are free, performance work first
    std::fs::write(c.join("specs/385-x/tasks.md"), tasks("x")).unwrap();
    let sixth = said(&c, &tr)
        .unwrap()
        .contains("make task-start F=385 T=T06,");
    assert!(sixth);
    start("T06");
    start("T08");
    // a full day after the latest landing of T11-T13 (T12's, 08:00:27.560Z): not met 0.56 s short of it, met at it
    crate::env::set("L7R_WAITS_NOW", "2026-11-22T08:00:27Z");
    let short = said(&c, &tr)
        .unwrap()
        .contains("make task-start F=385 T=T09,");
    assert!(short);
    crate::env::set("L7R_WAITS_NOW", "2026-11-22T08:00:27.560Z");
    let met = said(&c, &tr)
        .unwrap()
        .contains("make task-start F=385 T=T04,");
    assert!(met);
    crate::env::unset("L7R_WAITS_NOW");
    crate::env::unset("L7R_EVENTS_DIR");
}

/// 451 T102: ONE RULE, task-start's too. `make task-start`'s performance-first picker ([`next_performance`]) skips a performance task
/// that waits - on a landing (one task, or a range with one open) or on an open task (`after T<n>`) - so the start of other work needs
/// no `PERF_LATER_OK` for it. A bare date is no wait (T102's plan review, D7e: the clock against a typed date would be an escape with
/// no reason recorded), and nor is a clause that does not parse, failing toward a start the session sees named.
#[test]
fn task_start_s_performance_picker_skips_a_waiting_task() {
    let (_dir, c, _tr) = world("perf-waits", "no");
    let git = c.join(".git");
    crate::env::set("L7R_EVENTS_DIR", c.join("events"));
    crate::env::unset("L7R_WAITS_NOW");
    let write = |tasks: &str| std::fs::write(c.join("specs/385-x/tasks.md"), tasks).unwrap();
    let picked = || next_performance(&c, &git, "385-x").unwrap().map(|t| t.id);
    let tasks = |second: &str| {
        format!("- [{second}] T02 the next thing\n- [ ] T04 [perf] (waits: T02 lands) the second's follow-up\n- [ ] T05 [P] [perf] (waits: T01-T03 land) a range with one open\n- [ ] T06 [perf] a faster gate after T02\n- [ ] T08 [perf] a faster check\n")
    };
    write(&tasks(" "));
    assert_eq!(picked().as_deref(), Some("T08"));
    // the second landed: the first task that waited on it is named
    write(&tasks("x"));
    assert_eq!(picked().as_deref(), Some("T04"));
    write("- [ ] T02 the next thing\n- [ ] T05 [perf] (waits: 2999-01-01) a bare date\n");
    assert_eq!(picked().as_deref(), Some("T05"));
    write("- [ ] T02 the next thing\n- [ ] T05 [perf] (waits: when the GM says) an unread wait\n");
    assert_eq!(picked().as_deref(), Some("T05"));
    // a task ticked with no land line (before the log carried them, 451 T02-T05) landed long ago; no log at all reads as none
    write(
        "- [x] T01 done\n- [ ] T04 [perf] (waits: a full day after T01 lands) the measured day\n",
    );
    assert_eq!(picked().as_deref(), Some("T04"));
    // a full-day wait reads the log, and a log that is not text is an error
    std::fs::create_dir_all(c.join("events")).unwrap();
    std::fs::write(c.join("events/385-x.jsonl"), b"\xff\xfe\n").unwrap();
    assert!(next_performance(&c, &git, "385-x").is_err());
    crate::env::unset("L7R_EVENTS_DIR");
}

/// 451 T102: with nothing running, the set-down refusal names the first task that can start - and says none can where every one waits.
#[test]
fn nothing_running_names_the_first_task_that_can_start() {
    let (_dir, c, tr) = world("waits-none", "no");
    crate::env::unset("L7R_WAITS_NOW");
    std::fs::write(
        c.join("specs/385-x/tasks.md"),
        "- [ ] T02 (waits: T03 lands) the third's follow-up\n- [ ] T03 later\n",
    )
    .unwrap();
    let text = said(&c, &tr).unwrap();
    assert!(text.contains("start the next (T03 later)"), "{text}");
    std::fs::write(
        c.join("specs/385-x/tasks.md"),
        "- [ ] T02 (waits: T03 lands) the third's follow-up\n- [ ] T03 (waits: T02 lands) the second's follow-up\n",
    )
    .unwrap();
    let text = said(&c, &tr).unwrap();
    let none = text.contains("2 open task(s) and nothing is running - start the next (none can start yet: each waits on a day or a landing, 451 T102)");
    assert!(none, "{text}");
}

/// 449 T244: a parked stage's task is never named as the next, nor a free slot's; with only those open, the refusal names the GM's
/// ruling and the set-down that takes it - until a row resumes the stage.
#[test]
fn a_parked_stage_s_task_is_never_the_next_and_only_those_left_name_the_ruling() {
    let (_dir, c, tr) = world("parked", "no");
    std::fs::create_dir_all(c.join("rust/parked/src")).unwrap();
    std::fs::write(c.join("rust/parked/src/homesteads.rs"), "").unwrap();
    let tasks = |rest: &str| {
        format!("- [ ] T02 phase: homesteads - every household\n- [ ] T03 [perf] phase: homesteads - faster{rest}\n- [ ] GM review (make gm-reviewed F=385)\n")
    };
    std::fs::write(
        c.join("specs/385-x/tasks.md"),
        tasks("\n- [ ] T04 the port switch"),
    )
    .unwrap();
    let text = said(&c, &tr).unwrap();
    let ok1 = text.contains("start the next (T04 the port switch)");
    assert!(ok1, "{text}");
    std::fs::write(c.join("specs/385-x/tasks.md"), tasks("")).unwrap();
    let text = said(&c, &tr).unwrap();
    let ok2 = text.contains("every one a parked hamlet stage the GM stops before");
    assert!(ok2, "{text}");
    let ok3 = text.contains("Stop before homesteads, and talk first");
    assert!(ok3, "{text}");
    assert!(text.contains("make set-down F=385 WHY="), "{text}");
    // a free slot: no parked stage's task to start, so the turn ends
    std::fs::write(
        c.join(".git/task-starts.jsonl"),
        "{\"feature\": \"385-x\", \"task\": \"T09\", \"utc\": \"2026-10-18T23:00:00Z\"}\n",
    )
    .unwrap();
    agent(&tr, "a1", 1, "385 T09: something else");
    crate::env::unset("L7R_BUILDERS");
    assert_eq!(said(&c, &tr), None);
    // resumed: the stage's task is work again
    std::fs::write(
        c.join(".git/parked-resumed.jsonl"),
        "{\"stage\": \"homesteads\"}\n",
    )
    .unwrap();
    let text = said(&c, &tr).unwrap();
    assert!(text.contains("a builder slot is free"), "{text}");
}
