//! Feature 451 T106: a builder the coordinator re-numbers mid-task. T101's builder was briefed as `451 T100` and told by a `SendMessage`
//! "Your task is T101, not T100" 20 s into its run; every one of its 230 lines, its Write and Edit lines of `speckit.rs`, `ready.rs` and
//! `land-alone.sh` among them, was filed under T100, so land-alone's list and the closing checks' split read those files as T100's
//! (observed 2026-11-21, method: the 451 log's lines by its `by`, against the session transcript's `SendMessage` calls).

use serde_json::{json, Value};

use super::super::append;
use super::{last_line, none, session_files, Builders};

const SID: &str = "s-t106";

/// A call of `tool` in session [`SID`], `by` the subagent whose call it is (None: the main session's).
fn call(b: &Builders, by: Option<&str>, ev: &str, tool: &str, input: &Value) -> Value {
    let mut p = json!({"hook_event_name": ev, "cwd": b.cwd, "session_id": SID, "transcript_path": b.transcript,
        "tool_name": tool, "tool_use_id": "tu", "tool_input": input});
    if let Some(a) = by {
        p["agent_id"] = json!(a);
    }
    p
}

/// The line `append` wrote for `p`, with the log it went to as `log`.
fn written(b: &Builders, p: &Value) -> Value {
    let log = append(p, "2026-11-21T19:04:02.000Z", &b.d, &none).unwrap();
    let mut row = last_line(&log);
    row["log"] = json!(log.file_stem().unwrap().to_string_lossy());
    row
}

/// The main session's `SendMessage` to `to`, its `PostToolUse`.
fn send(b: &Builders, to: &str, summary: &str, message: &str) -> Value {
    let p = call(
        b,
        None,
        "PostToolUse",
        "SendMessage",
        &json!({"to": to, "summary": summary, "message": message}),
    );
    written(b, &p)
}

/// The task of `by`'s next Read line.
fn task_of(b: &Builders, by: &str) -> Value {
    let p = call(
        b,
        Some(by),
        "PreToolUse",
        "Read",
        &json!({"file_path": "/x"}),
    );
    written(b, &p)["task"].clone()
}

const T101: &str = "From the session, a correction: the task your brief describes (make land holding any ready task, not only the active \
    mark's; and committing a task's own plan section apart from other tasks' in the same file) is T101 in tasks.md, not T100 - I gave you \
    the wrong number. T100 is a different task (the set-down guard's 'nothing is running' miss); leave it. Read T101's line, write T101's \
    plan section, and run `make decide F=451 T=T101`; T101 is now the clone's active task. Everything else in your brief stands.";

/// T101's case, replayed: the brief, the correction, then the builder's edit-tool ends of the three files - each filed under T101 in
/// 451's log, unmarked, which is what both splits key on (`ev` `PostToolUse`, `cat` edit, `path`, `task`, no `fallback`).
#[test]
fn a_builder_corrected_by_a_sendmessage_files_its_later_lines_under_the_new_task() {
    let b = Builders::new("t106-send");
    session_files(
        &b.d,
        "a30ac",
        r#"{"agentType":"general-purpose","description":"451 T100: land any ready task, its own section alone"}"#,
    );
    // its orientation, before the correction: the brief's, and it stays so (earlier lines are not re-filed)
    assert_eq!(task_of(&b, "a30ac"), json!("T100"));
    let sent = send(&b, "a30ac", "Your task is T101, not T100", T101);
    assert_eq!(
        sent["log"],
        json!("449-b"),
        "the coordinator's own line is filed as before"
    );
    let root = b.d.to_string_lossy().into_owned();
    for (tool, rel) in [
        ("Edit", "rust/guard/shared/src/speckit.rs"),
        ("Write", "rust/gate/crates/land/src/land/ready.rs"),
        ("Write", "scripts/land-alone.sh"),
    ] {
        let path = format!("{root}/{rel}");
        let p = call(
            &b,
            Some("a30ac"),
            "PostToolUse",
            tool,
            &json!({"file_path": path, "old_string": "a", "new_string": "b", "content": "c"}),
        );
        let row = written(&b, &p);
        assert_eq!(row["log"], json!("451-a"), "{rel}");
        assert_eq!(row["ev"], json!("PostToolUse"), "{rel}");
        assert_eq!(row["cat"], json!("edit"), "{rel}");
        assert_eq!(row["path"], json!(path), "{rel}");
        assert_eq!(row["task"], json!("T101"), "{rel}");
        assert_eq!(row.get("fallback"), None, "{rel}");
    }
    // its own stop too, and its closing step's own `T=` still wins on its own line
    let stop = json!({"hook_event_name": "SubagentStop", "cwd": b.cwd, "session_id": SID, "transcript_path": b.transcript,
        "agent_id": "a30ac", "agent_type": "general-purpose"});
    assert_eq!(written(&b, &stop)["task"], json!("T101"));
    let tick = call(
        &b,
        Some("a30ac"),
        "PreToolUse",
        "Bash",
        &json!({"command": "make tick F=451 T=T09"}),
    );
    assert_eq!(written(&b, &tick)["task"], json!("T09"));
    // another builder of the session is untouched
    assert_eq!(task_of(&b, "a451"), json!("T26"));
    // a second correction moves it again, naming the task it is filed under now
    let _ = send(&b, "a30ac", "Your task is T102, not T101", "");
    assert_eq!(task_of(&b, "a30ac"), json!("T102"));
}

/// A message naming another task is not a correction (40 of the night's 108 messages to a briefed agent named one, and one was):
/// "T43, not T42" told T40's builder where a deferral went, the old task not its own; a fold names T06 to T06's own builder; a summary
/// naming a correction in a `SendMessage`'s Pre half, a recipient that is a name and not an agent id, or one with no meta file, all
/// change nothing.
#[test]
fn a_message_that_only_names_a_task_corrects_nothing() {
    let b = Builders::new("t106-mention");
    session_files(
        &b.d,
        "a40",
        r#"{"description":"451 T40: the base re-read"}"#,
    );
    session_files(&b.d, "a06", r#"{"description":"451 T06: the landing"}"#);
    let _ = send(
        &b,
        "a40",
        "Correction: the base re-read is T43",
        "Correction: the base re-read (Delta::fetch reading all 1,951 pages) was filed as T43, not T42 (T42 is T31's heredoc task, \
         filed a moment earlier). T40's deferral reads \"Filed as T43; lands before T22.\"",
    );
    assert_eq!(task_of(&b, "a40"), json!("T40"));
    let _ = send(
        &b,
        "a06",
        "Fold both deferrals into T06",
        "The GM just reordered 451: the improvements (T12-T21) now land BEFORE T07-T11, so both your deferrals land after T13/T14 that \
         need them - fold both into T06: run `make decide F=451 T=T06` after the last edit",
    );
    assert_eq!(task_of(&b, "a06"), json!("T06"));
    let pre = call(
        &b,
        None,
        "PreToolUse",
        "SendMessage",
        &json!({"to": "a06", "summary": "Your task is T07, not T06"}),
    );
    let _ = written(&b, &pre);
    assert_eq!(task_of(&b, "a06"), json!("T06"));
    let mut bare = call(
        &b,
        None,
        "PostToolUse",
        "SendMessage",
        &json!({"to": "a06", "summary": "Your task is T07, not T06"}),
    );
    bare.as_object_mut().unwrap().remove("transcript_path");
    let _ = written(&b, &bare);
    assert_eq!(
        task_of(&b, "a06"),
        json!("T06"),
        "no transcript: no brief to correct"
    );
    let _ = send(&b, "builder", "Your task is T07, not T06", "");
    let _ = send(&b, "../a06", "Your task is T07, not T06", "");
    let _ = send(&b, "anometa", "Your task is T07, not T06", "");
    assert_eq!(task_of(&b, "a06"), json!("T06"));
    // an agent whose brief names no task carries none, never the clone's mark (451 T161)
    assert_eq!(task_of(&b, "anometa"), Value::Null);
    // a builder's own message to another agent (the coordinator is the main session), and one with no input at all, correct nothing
    let theirs = call(
        &b,
        Some("a40"),
        "PostToolUse",
        "SendMessage",
        &json!({"to": "a06", "summary": "Heads-up: T07, not T06, was killed"}),
    );
    let _ = written(&b, &theirs);
    assert_eq!(task_of(&b, "a06"), json!("T06"));
    let _ = written(
        &b,
        &call(&b, None, "PostToolUse", "SendMessage", &Value::Null),
    );
    assert_eq!(task_of(&b, "a40"), json!("T40"));
}

/// The builder's own closing step names its task: `make closing-checks T=` (which the line did not carry), `make decide T=` and `make
/// task-start T=` file that call's line and every later one, in any shape the shell runs it; a `T=` inside a heredoc's body, or another
/// target's, is no call of its own.
#[test]
fn a_builders_own_closing_step_files_its_later_lines() {
    let b = Builders::new("t106-own");
    session_files(
        &b.d,
        "a30ac",
        r#"{"description":"451 T100: land any ready task"}"#,
    );
    let bash = |by: Option<&str>, command: &str| {
        let p = call(&b, by, "PreToolUse", "Bash", &json!({ "command": command }));
        written(&b, &p)["task"].clone()
    };
    for not_own in [
        "cat > /tmp/x.rs <<'EOF'\nmake closing-checks T=T101 F=451\nEOF",
        "make rust-test T=T101",
        "make decide F=451",
        "make decide F=451 T=T100",
    ] {
        assert_eq!(bash(Some("a30ac"), not_own), json!("T100"), "{not_own}");
        assert_eq!(task_of(&b, "a30ac"), json!("T100"), "{not_own}");
    }
    assert_eq!(
        bash(
            Some("a30ac"),
            "(make closing-checks T=T101 F=451 > /tmp/t101/closing-1.log 2>&1; echo \"rc=$?\" >> /tmp/t101/closing-1.log)"
        ),
        json!("T101")
    );
    assert_eq!(task_of(&b, "a30ac"), json!("T101"));
    assert_eq!(
        bash(Some("a30ac"), "make decide F=451 T=T101"),
        json!("T101")
    );
    assert_eq!(task_of(&b, "a30ac"), json!("T101"));
    assert_eq!(
        bash(Some("a30ac"), "cd /x && make decide F=451 T=T102"),
        json!("T102")
    );
    assert_eq!(task_of(&b, "a30ac"), json!("T102"));
    assert_eq!(
        bash(Some("a30ac"), "make task-start F=451 T=T103"),
        json!("T103")
    );
    assert_eq!(task_of(&b, "a30ac"), json!("T103"));
    // a task its brief names is no re-numbering: a `T28+T29` builder's `decide T=T29` is that line's alone (the night's one such
    // builder, whose 64 later lines, 6 of them writes, the rule would otherwise have moved)
    session_files(
        &b.d,
        "a2829",
        r#"{"description":"451 T28+T29: performance work first"}"#,
    );
    assert_eq!(bash(Some("a2829"), "make decide F=451 T=T29"), json!("T29"));
    assert_eq!(task_of(&b, "a2829"), json!("T28"));
    // the main session's closing checks name their task on their own line, and keep no correction for anyone
    assert_eq!(
        bash(None, "make closing-checks T=T104 F=451"),
        json!("T104")
    );
    assert_eq!(task_of(&b, "a451"), json!("T26"));
}

/// A correction file that does not hold a task, or one in a session with no plain id, is no correction.
#[test]
fn a_correction_is_read_only_where_it_names_a_task() {
    let b = Builders::new("t106-edges");
    let dir =
        b.d.join(".git/l7r-events-dispatches")
            .join(format!("{SID}.tasks"));
    std::fs::create_dir_all(&dir).unwrap();
    std::fs::write(dir.join("a451"), "not a task\n").unwrap();
    assert_eq!(task_of(&b, "a451"), json!("T26"));
    std::fs::write(dir.join("a451"), "T31\n").unwrap();
    assert_eq!(task_of(&b, "a451"), json!("T31"));
    for sid in ["", ".hidden", "a/b"] {
        let mut p = call(
            &b,
            Some("a451"),
            "PreToolUse",
            "Read",
            &json!({"file_path": "/x"}),
        );
        p["session_id"] = json!(sid);
        assert_eq!(written(&b, &p)["task"], json!("T26"), "{sid:?}");
    }
}

/// A corrected builder's Agent call is filed by its own words first - its description's `T<n>`, else its prompt's first line's - and
/// by the correction only where they name none; the correction comes before the builder's brief.
#[test]
fn a_corrected_builders_dispatch_is_filed_by_its_own_words_first() {
    let b = Builders::new("t106-agent");
    session_files(
        &b.d,
        "a30ac",
        r#"{"description":"451 T100: land any ready task"}"#,
    );
    let _ = send(&b, "a30ac", "Your task is T101, not T100", "");
    let agent = |description: &str, prompt: &str| {
        let p = call(
            &b,
            Some("a30ac"),
            "PreToolUse",
            "Agent",
            &json!({"description": description, "subagent_type": "spec-fidelity", "prompt": prompt}),
        );
        written(&b, &p)["task"].clone()
    };
    assert_eq!(agent("spec-fidelity MODE 4 T55", "x"), json!("T55"));
    assert_eq!(
        agent("a plan review", "MODE 4 on T56's section\nT57"),
        json!("T56")
    );
    assert_eq!(
        agent("a plan review", "MODE 4 on the section"),
        json!("T101")
    );
    assert_eq!(agent("", "MODE 4 on T58's section"), json!("T101"));
}
