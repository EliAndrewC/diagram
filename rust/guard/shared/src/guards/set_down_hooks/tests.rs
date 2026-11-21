//! The decider over a fixture clone, the status line read in process (feature 449 T118); `tests/hooks/test-set-down-hooks.sh` replays
//! the guard through the shim.

use std::path::{Path, PathBuf};

use serde_json::json;

use super::{decide, judge, next_performance, open_boxes, performance, verdict, OpenTask};
use crate::protocol::{Answer, Event};
use crate::session::Session;
use crate::tool::ask;

const TASKS: &str = "- [x] T01 done\n- [ ] T02 the next thing\n- [ ] T03 later\n- [ ] GM review (make gm-reviewed F=385)\n";
const START: &str =
    "{\"feature\": \"385-x\", \"task\": \"T02\", \"utc\": \"2026-10-18T23:00:00Z\"}\n";

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
