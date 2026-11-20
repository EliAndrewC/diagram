//! Feature 451 T04 (FR-002, plan D3): a background run's start and end both in the log - `bg` on the launch's `PostToolUse`, a `BgEnd`
//! line from the main session's completion notice, `inflight` on every `Stop` and `SubagentStop`.

use std::path::{Path, PathBuf};

use serde_json::{json, Value};

use super::super::{append, append_row_in};
use super::{last_line, none, Builders};

/// R2's observed shell notice (the main session's queue, 2026-11-16, `-diagram/c6fd72d1-...jsonl`), its exit code and summary given.
fn shell_notice(tool_use: &str, summary: &str) -> String {
    format!(
        "<task-notification>\n<task-id>bx2d0japp</task-id>\n<tool-use-id>{tool_use}</tool-use-id>\n\
         <output-file>/tmp/claude-1000/-diagram/c6fd72d1/tasks/bx2d0japp.output</output-file>\n<status>completed</status>\n\
         <summary>{summary}</summary>\n</task-notification>"
    )
}

/// An agent's notice as the queue holds it: it names the launching call's `<tool-use-id>` too (3,801 of the 3,986 agent notices,
/// measured 2026-11-20 (the `-diagram` and clone transcripts' queue rows tallied by summary and tags)).
fn agent_notice(tool_use: &str) -> String {
    format!(
        "<task-notification>\n<task-id>a7edba00fee798166</task-id>\n<tool-use-id>{tool_use}</tool-use-id>\n\
         <output-file>/tmp/x/tasks/a7edba00fee798166.output</output-file>\n<status>completed</status>\n\
         <summary>Agent \"modal-triage 0006\" finished</summary>\n<result>TOUCHES x (exit code 3)\n\
         <tool-use-id>toolu_quoted</tool-use-id>\nBackground command \"y\" completed (exit code 4)</result>\n\
         <usage><subagent_tokens>2</subagent_tokens><tool_uses>1</tool_uses><duration_ms>9</duration_ms></usage>\n</task-notification>"
    )
}

impl Builders {
    fn prompt(&self, text: &str) -> Value {
        json!({"hook_event_name": "UserPromptSubmit", "cwd": self.cwd, "transcript_path": self.transcript, "prompt": text})
    }

    fn log(&self, feature: &str) -> PathBuf {
        std::fs::canonicalize(&*self.d)
            .unwrap()
            .join(".git/l7r-events")
            .join(format!("{feature}.jsonl"))
    }
}

fn rows(log: &Path) -> Vec<Value> {
    std::fs::read_to_string(log)
        .unwrap_or_default()
        .lines()
        .map(|l| serde_json::from_str(l).unwrap())
        .collect()
}

fn ends(log: &Path) -> Vec<Value> {
    rows(log)
        .into_iter()
        .filter(|r| r["ev"] == "BgEnd")
        .collect()
}

/// The shell's notice writes a `BgEnd` beside its launch - in the launch's feature's log, not feature.json's - with the launch's tool-use
/// id, its task id, its status and exit code, and the launch's `make`, `cat`, `task` and start (`t0`): the run's span. The prompt's own
/// line is kept.
#[test]
fn a_shell_notice_writes_its_end_beside_its_launch() {
    let b = Builders::new("bg-shell");
    let mut launch = b.bash(None, "make static F=451", "PreToolUse");
    launch["tool_use_id"] = json!("toolu_01Rw");
    append(&launch, "2026-11-20T09:00:00.000Z", &b.d, &none).unwrap();
    let mut back = b.bash(None, "make static F=451", "PostToolUse");
    back["tool_use_id"] = json!("toolu_01Rw");
    back["tool_input"]["run_in_background"] = json!(true);
    back["tool_response"] = json!({"backgroundTaskId": "bx2d0japp"});
    append(&back, "2026-11-20T09:00:01.000Z", &b.d, &none).unwrap();
    assert_eq!(last_line(&b.log("451-a"))["bg"], json!("bx2d0japp"));
    let notice = shell_notice(
        "toolu_01Rw",
        "Background command \"Run the prepass sweep\" completed (exit code -1)",
    );
    append(&b.prompt(&notice), "2026-11-20T09:05:00.000Z", &b.d, &none).unwrap();
    // the prompt's line goes where it went before: feature.json's, marked
    let prompt = last_line(&b.log("449-b"));
    assert_eq!(
        (&prompt["ev"], &prompt["gm"]),
        (&json!("UserPromptSubmit"), &json!(false))
    );
    let end = ends(&b.log("451-a"));
    assert_eq!(end.len(), 1, "{end:?}");
    let e = &end[0];
    for (k, want) in [
        ("t", json!("2026-11-20T09:05:00.000Z")),
        ("id", json!("toolu_01Rw")),
        ("bg", json!("bx2d0japp")),
        ("status", json!("completed")),
        ("exit", json!(-1)),
        ("make", json!("static")),
        ("cat", json!("tests")),
        ("task", json!("T26")),
        ("t0", json!("2026-11-20T09:00:00.000Z")),
    ] {
        assert_eq!(e[k], want, "{k}: {e}");
    }
    assert!(e.get("fallback").is_none(), "{e}");
    assert!(ends(&b.log("449-b")).is_empty());
    // a launch filed by feature.json's guess: its end beside it, the mark copied
    let mut guessed = b.bash(None, "make done", "PreToolUse");
    guessed["tool_use_id"] = json!("toolu_guess");
    append(&guessed, "T0", &b.d, &none).unwrap();
    let notice = shell_notice(
        "toolu_guess",
        "Background command \"gate\" completed (exit code 0)",
    );
    append(&b.prompt(&notice), "T1", &b.d, &none).unwrap();
    let e = ends(&b.log("449-b")).pop().unwrap();
    assert_eq!(
        (&e["make"], &e["t0"], &e["fallback"]),
        (&json!("done"), &json!("T0"), &json!(true))
    );
}

/// Every exit form the notices take (the summaries of the `-diagram` and clone transcripts tallied, measured 2026-11-20): the code is
/// the summary's LAST `exit code N`, the quoted description being free text; none where the run was stopped or the session ended.
#[test]
fn each_exit_form_is_read_and_a_launch_not_logged_ends_beside_the_prompt() {
    let b = Builders::new("bg-forms");
    for (summary, status, want) in [
        (
            "Background command \"make done\" failed with exit code 2",
            "failed",
            Some(2),
        ),
        (
            "Background command \"grep x\" completed (exit code 1: No matches found)",
            "completed",
            Some(1),
        ),
        (
            "Background command \"echo exit code 9\" completed (exit code 0)",
            "completed",
            Some(0),
        ),
        (
            "Background command \"sleep 900\" was stopped after reaching its background time limit",
            "killed",
            None,
        ),
        (
            "Background shell command didn't finish before the previous session ended",
            "killed",
            None,
        ),
        // a workflow and a Monitor are background runs a session waits on too, and name their launch: each ends (T04's section)
        (
            "Dynamic workflow \"check-wave\" completed",
            "completed",
            None,
        ),
        ("Monitor \"the gate's log\" stream ended", "completed", None),
    ] {
        let notice = shell_notice("toolu_unlogged", summary)
            .replace("completed</status>", &format!("{status}</status>"));
        append(&b.prompt(&notice), "T", &b.d, &none).unwrap();
        // no launch line in any log: the end goes beside the prompt, under its feature and task, and copies nothing
        let e = ends(&b.log("449-b")).pop().unwrap();
        assert_eq!(e["status"], json!(status), "{summary}");
        assert_eq!(e.get("exit").and_then(Value::as_i64), want, "{summary}");
        assert_eq!((&e["task"], &e["fallback"]), (&json!("T236"), &json!(true)));
        assert!(e.get("make").is_none() && e.get("t0").is_none(), "{e}");
    }
    assert_eq!(ends(&b.log("449-b")).len(), 7);
}

/// An agent's notice writes no end - its `SubagentStop` is its end - though it names the launching call's tool-use id; nor does an
/// end named only inside its `<result>`, a notice whose launch was an Agent call, a prompt the GM typed that quotes a notice, or a notice
/// with no tool-use id (a Monitor's event).
#[test]
fn an_agent_notice_and_a_quoted_one_write_none() {
    let b = Builders::new("bg-agent");
    let mut launch = json!({"hook_event_name": "PreToolUse", "cwd": b.cwd, "tool_name": "Agent", "tool_use_id": "toolu_agent",
        "tool_input": {"description": "451 T26: x", "prompt": "x", "run_in_background": true}});
    append(&launch, "T", &b.d, &none).unwrap();
    launch["hook_event_name"] = json!("PostToolUse");
    append(&launch, "T", &b.d, &none).unwrap();
    let shell_summary = "Background command \"x\" completed (exit code 0)";
    for prompt in [
        agent_notice("toolu_agent"),
        agent_notice("toolu_other"),
        shell_notice("toolu_agent", shell_summary),
        format!("why did this fail?\n{}", shell_notice("toolu_x", shell_summary)),
        "<task-notification>\n<task-id>bwf1</task-id>\n<summary>Monitor event: \"x\"</summary>\n</task-notification>".to_owned(),
    ] {
        append(&b.prompt(&prompt), "T", &b.d, &none).unwrap();
    }
    for f in ["449-b", "451-a"] {
        assert!(ends(&b.log(f)).is_empty(), "{f}");
    }
    assert_eq!(
        rows(&b.log("449-b"))
            .iter()
            .filter(|r| r["ev"] == "UserPromptSubmit")
            .count(),
        5
    );
}

/// Every `Stop` and `SubagentStop` names the background work in flight (the payload's `background_tasks`, research R2): each one's id
/// and type, and a shell's make target; an empty list is written (nothing in flight), a payload with none writes no field.
#[test]
fn a_stop_names_the_runs_in_flight() {
    let b = Builders::new("bg-inflight");
    let stop = json!({"hook_event_name": "Stop", "cwd": b.cwd, "background_tasks": [
        {"id": "bx1", "type": "shell", "status": "running", "description": "the gate", "command": "timeout 900 make done > /tmp/d.log 2>&1"},
        {"id": "a77", "type": "subagent", "status": "running", "description": "451 T05: phases"},
    ]});
    let log = append(&stop, "T", &b.d, &none).unwrap();
    assert_eq!(
        last_line(&log)["inflight"],
        json!([{"id": "bx1", "type": "shell", "make": "done"}, {"id": "a77", "type": "subagent"}])
    );
    let sub = json!({"hook_event_name": "SubagentStop", "cwd": b.cwd, "transcript_path": b.transcript, "agent_id": "a451",
        "agent_type": "general-purpose", "background_tasks": [{"id": "bx2", "type": "shell", "command": "ls"}]});
    let log = append(&sub, "T", &b.d, &none).unwrap();
    assert_eq!(
        last_line(&log)["inflight"],
        json!([{"id": "bx2", "type": "shell"}])
    );
    let idle = json!({"hook_event_name": "Stop", "cwd": b.cwd, "background_tasks": []});
    let log = append(&idle, "T", &b.d, &none).unwrap();
    assert_eq!(last_line(&log)["inflight"], json!([]));
    let old = json!({"hook_event_name": "Stop", "cwd": b.cwd});
    let log = append(&old, "T", &b.d, &none).unwrap();
    assert!(last_line(&log).get("inflight").is_none());
}

/// `append_row` (D4), the writer a gate tool calls in process: filed by the task it carries as a hook's line is, stamped now and given the
/// session's id from `CLAUDE_CODE_SESSION_ID` where it names neither, under `L7R_EVENTS_DIR` where that is set; a row naming no event
/// writes nothing (T207).
#[test]
fn a_gate_tools_row_is_filed_stamped_and_named_by_its_session() {
    let b = Builders::new("bg-append-row");
    let env = |k: &str| (k == "CLAUDE_CODE_SESSION_ID").then(|| "s9".to_owned());
    let phase = |task: Option<&str>| {
        let mut row = serde_json::Map::new();
        row.insert("ev".into(), json!("Phase"));
        row.insert("step".into(), json!("build"));
        if let Some(t) = task {
            row.insert("task".into(), json!(t));
        }
        row
    };
    let log = append_row_in(&b.d, phase(Some("T03")), "2026-11-20T09:00:00.000Z", &env).unwrap();
    assert!(log.ends_with("451-a.jsonl"), "{}", log.display());
    let row = last_line(&log);
    assert_eq!(
        (&row["t"], &row["sid"], &row["task"], row.get("fallback")),
        (
            &json!("2026-11-20T09:00:00.000Z"),
            &json!("s9"),
            &json!("T03"),
            None
        )
    );
    // its own t and sid kept; a row naming no task goes to the session's feature, its task in force, marked
    let mut own = phase(None);
    own.insert("t".into(), json!("X"));
    own.insert("sid".into(), json!("s1"));
    let log = append_row_in(&b.d, own, "T", &none).unwrap();
    assert!(log.ends_with("449-b.jsonl"), "{}", log.display());
    let row = last_line(&log);
    assert_eq!(
        (&row["t"], &row["sid"], &row["task"], &row["fallback"]),
        (&json!("X"), &json!("s1"), &json!("T236"), &json!(true))
    );
    let row = last_line(&append_row_in(&b.d, phase(None), "T", &none).unwrap());
    assert_eq!(row["sid"], json!(""));
    let mut blank = phase(None);
    blank.insert("ev".into(), json!(""));
    assert!(append_row_in(&b.d, blank, "T", &env).is_none());
    assert!(append_row_in(&b.d, serde_json::Map::new(), "T", &env).is_none());
    let to = b.d.join("events");
    let elsewhere = |k: &str| (k == "L7R_EVENTS_DIR").then(|| to.to_string_lossy().into_owned());
    assert_eq!(
        append_row_in(&b.d, phase(Some("T03")), "T", &elsewhere).unwrap(),
        to.join("451-a.jsonl")
    );
    // the public door: the process's own clock and environment
    let row = last_line(&super::super::append_row(&b.d, phase(Some("T03"))).unwrap());
    assert!(row["t"].as_str().unwrap().ends_with('Z'), "{row}");
}
