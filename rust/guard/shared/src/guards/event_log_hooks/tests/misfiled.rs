//! Feature 451 T53: the shapes T26's chain still filed wrong, each found in the 449 and 385 logs after T26 landed (observed
//! 2026-11-21, method: `make events-refile DRY=1`'s 21 moves and 23 lines left, each joined to its subagent's meta file and transcript).

use std::path::Path;

use serde_json::{json, Value};

use super::super::append;
use super::{last_line, none, want, Builders, Filed};

const SID: &str = "s-t53";

impl Builders {
    /// The log a payload's line went to at `t`, its task, and whether it is marked `fallback`.
    fn filed_at(&self, p: &Value, t: &str) -> Filed {
        let log = append(p, t, &self.d, &none).unwrap();
        let row = last_line(&log);
        (
            log.file_stem().unwrap().to_string_lossy().into_owned(),
            row.get("task").and_then(Value::as_str).map(str::to_owned),
            row.get("fallback").is_some(),
        )
    }

    /// The main session's Agent call, `ev` its half; `aid` the agent its launch returned.
    fn dispatch(
        &self,
        id: &str,
        kind: &str,
        description: &str,
        ev: &str,
        aid: Option<&str>,
    ) -> Value {
        let mut p = json!({"hook_event_name": ev, "cwd": self.cwd, "session_id": SID, "transcript_path": self.transcript,
            "tool_name": "Agent", "tool_use_id": id,
            "tool_input": {"description": description, "subagent_type": kind, "prompt": "x"}});
        if let Some(a) = aid {
            p["tool_response"] = json!({"agentId": a});
        }
        p
    }

    /// A subagent's start; `aid` has no meta file on disk, as at every first start (measured 2026-11-21: the meta file is written
    /// 24-29 ms after the `SubagentStart` hook's line).
    fn start(&self, aid: &str, kind: &str) -> Value {
        json!({"hook_event_name": "SubagentStart", "cwd": self.cwd, "session_id": SID, "transcript_path": self.transcript,
            "agent_id": aid, "agent_type": kind})
    }
}

/// A subagent's FIRST start fires before its meta file exists: filed by the dispatch it came from, not by feature.json.
#[test]
fn a_subagent_start_before_its_meta_file_is_filed_by_its_dispatch() {
    let b = Builders::new("t53-start");
    let _ = b.filed_at(
        &b.dispatch(
            "tu1",
            "general-purpose",
            "451 T26: a builder",
            "PreToolUse",
            None,
        ),
        "2026-11-20T11:47:06.100Z",
    );
    assert_eq!(
        b.filed_at(
            &b.start("anew1", "general-purpose"),
            "2026-11-20T11:47:06.377Z"
        ),
        want("451-a", "T26", false)
    );
    // the launch returned: that call names its agent, which wins over any other dispatch still pending
    let _ = b.filed_at(
        &b.dispatch(
            "tu1",
            "general-purpose",
            "451 T26: a builder",
            "PostToolUse",
            Some("anew1"),
        ),
        "2026-11-20T11:47:06.500Z",
    );
    let _ = b.filed_at(
        &b.dispatch(
            "tu2",
            "general-purpose",
            "449 T236: the reed strip",
            "PreToolUse",
            None,
        ),
        "2026-11-20T11:47:10.000Z",
    );
    let _ = b.filed_at(
        &b.dispatch(
            "tu3",
            "general-purpose",
            "451 T03: the other",
            "PreToolUse",
            None,
        ),
        "2026-11-20T11:47:10.100Z",
    );
    let _ = b.filed_at(
        &b.dispatch(
            "tu2",
            "general-purpose",
            "449 T236: the reed strip",
            "PostToolUse",
            Some("anew2"),
        ),
        "2026-11-20T11:47:10.200Z",
    );
    assert_eq!(
        b.filed_at(
            &b.start("anew2", "general-purpose"),
            "2026-11-20T11:47:10.300Z"
        ),
        want("449-b", "T236", false)
    );
    // two dispatches pending whose briefs name two features: nothing says which, so feature.json's, marked
    let _ = b.filed_at(
        &b.dispatch(
            "tu4",
            "general-purpose",
            "449 T236: again",
            "PreToolUse",
            None,
        ),
        "2026-11-20T11:47:10.400Z",
    );
    assert_eq!(
        b.filed_at(
            &b.start("anew3", "general-purpose"),
            "2026-11-20T11:47:10.500Z"
        ),
        ("449-b".to_owned(), None, true) // an agent's line takes no mark (451 T161)
    );
}

/// A start is filed only by a call that could have started it: of its type, or the review-round twin, inside the window.
#[test]
fn a_start_is_filed_only_by_a_call_of_its_type_inside_the_window() {
    let b = Builders::new("t53-window");
    let _ = b.filed_at(
        &b.dispatch(
            "tu3",
            "general-purpose",
            "449 T236: a builder",
            "PreToolUse",
            None,
        ),
        "2026-11-20T11:59:59.000Z",
    );
    // a spec-fidelity call the review-round guard routes to its twin; a dispatch past the window is no candidate
    let _ = b.filed_at(
        &b.dispatch(
            "tu5",
            "spec-fidelity",
            "spec-fidelity on 451 T03's section",
            "PreToolUse",
            None,
        ),
        "2026-11-20T12:00:00.000Z",
    );
    assert_eq!(
        b.filed_at(
            &b.start("anew4", "spec-fidelity-verify"),
            "2026-11-20T12:00:00.400Z"
        ),
        want("451-a", "T03", false)
    );
    let _ = b.filed_at(
        &b.dispatch(
            "tu6",
            "round-arbiter",
            "451 T26 arbiter",
            "PreToolUse",
            None,
        ),
        "2026-11-20T12:00:01.000Z",
    );
    assert_eq!(
        b.filed_at(
            &b.start("anew5", "round-arbiter"),
            "2026-11-20T12:30:00.000Z"
        ),
        ("449-b".to_owned(), None, true) // an agent's line takes no mark (451 T161)
    );
    // a resumed agent's meta is on disk: its brief, as before
    assert_eq!(
        b.filed_at(
            &b.start("a451", "general-purpose"),
            "2026-11-20T12:30:01.000Z"
        ),
        want("451-a", "T26", false)
    );
}

/// A builder's make call naming another feature's `F=` with no `T=` (`make task-add F=449` from a 451 T36 builder) is the builder's
/// time: filed by its brief, feature and task from one source; a call carrying its own `T=` keeps its `F=`.
#[test]
fn a_builders_f_without_its_own_t_is_filed_by_its_brief() {
    let b = Builders::new("t53-brief");
    for ev in ["PreToolUse", "PostToolUse"] {
        assert_eq!(
            b.filed_at(
                &b.bash(Some("a451"), "make task-add F=449 TITLE='x'", ev),
                "2026-11-20T12:00:00.000Z"
            ),
            want("451-a", "T26", false)
        );
    }
    assert_eq!(
        b.filed_at(
            &b.bash(Some("a451"), "make decide F=449 T=T236", "PreToolUse"),
            "2026-11-20T12:00:00.000Z"
        ),
        want("449-b", "T236", false)
    );
}

/// A heredoc's body is text written to a file, never the command's own words: an `F=` or `T=` quoted in it names nothing.
#[test]
fn an_f_or_t_inside_a_heredoc_names_nothing() {
    let b = Builders::new("t53-heredoc");
    let cat = "cat >> tests.rs <<'EOF'\n\"(make static > log) & make decide F=451 T=T03 | tail -40; wait\",\nEOF\nmake rust-test CRATE=rust/guard";
    assert_eq!(
        b.filed_at(&b.bash(None, cat, "PreToolUse"), "2026-11-20T12:00:00.000Z"),
        want("449-b", "T236", true)
    );
    let tick = "cat > x <<'EOF'\nmake tick F=451 T=T03\nEOF\nmake tick F=449 T=T236";
    assert_eq!(
        b.filed_at(
            &b.bash(None, tick, "PreToolUse"),
            "2026-11-20T12:00:00.000Z"
        ),
        want("449-b", "T236", false)
    );
    // a quoted value is still the command's own
    assert_eq!(
        b.filed_at(
            &b.bash(None, "make where-time F=\"451\"", "PreToolUse"),
            "2026-11-20T12:00:00.000Z"
        ),
        want("451-a", "T26", false)
    );
}

/// A brief naming only a task (`T47 plan review`) is not filed by a start weeks old: 385's T47 of 2026-10-18 took a 451 T47
/// builder's three spec-fidelity rounds of 2026-11-21 into 385's log.
#[test]
fn a_task_only_brief_is_not_filed_by_a_stale_start() {
    let b = Builders::new("t53-stale");
    let starts = b.d.join(".git/task-starts.jsonl");
    let mut text = std::fs::read_to_string(&starts).unwrap();
    text.insert_str(
        0,
        "{\"feature\": \"450-c\", \"task\": \"T47\", \"utc\": \"2026-10-18T17:01:28Z\"}\n",
    );
    std::fs::write(&starts, text).unwrap();
    super::session_files(&b.d, "at47", r#"{"description":"T47 plan review"}"#);
    // weeks old: feature.json's, marked, the brief's task kept
    assert_eq!(
        b.filed_at(
            &b.bash(Some("at47"), "ls", "PreToolUse"),
            "2026-11-20T23:56:24.000Z"
        ),
        want("449-b", "T47", true)
    );
    // within the bound: that start's feature, as T26 filed it
    assert_eq!(
        b.filed_at(
            &b.bash(Some("at47"), "ls", "PreToolUse"),
            "2026-10-19T17:00:00.000Z"
        ),
        want("450-c", "T47", false)
    );
}

/// The side file: only an Agent call's two halves, with an id and a plain session; read back from its last 64 KiB, at a `now` that parses.
#[test]
fn the_side_file_keeps_only_an_agent_calls_halves() {
    use super::super::dispatches::{briefs_at_start, record};
    let d = crate::tempdir::TempDir::new("guard-events-t53-side");
    let events = d.join("l7r-events");
    let call = |ev: &str, id: &str, sid: &str| {
        json!({"hook_event_name": ev, "session_id": sid, "tool_name": "Agent", "tool_use_id": id,
            "tool_input": {"description": "451 T26: x"}})
    };
    let t = "2026-11-20T12:00:00.000Z";
    for p in [
        call("PreToolUse", "", SID),
        call("PreToolUse", "tu1", ""),
        call("PreToolUse", "tu1", "../up"),
        call("PreToolUse", "tu1", ".hidden"),
        call("PostToolUse", "tu1", SID),
        call("PermissionRequest", "tu1", SID),
        json!({"hook_event_name": "PreToolUse", "session_id": SID, "tool_name": "Bash", "tool_use_id": "tb"}),
    ] {
        record(&events, &p, t);
    }
    let side = d.join("l7r-events-dispatches").join(format!("{SID}.jsonl"));
    assert!(!side.exists());
    let start = json!({"hook_event_name": "SubagentStart", "session_id": SID, "agent_id": "a1", "agent_type": "general-purpose"});
    assert!(briefs_at_start(&events, &start, "2026-11-20T12:00:01.000Z").is_empty());
    // a long file: its tail alone, the cut line dropped; no subagent_type is a general-purpose call
    std::fs::create_dir_all(side.parent().unwrap()).unwrap();
    std::fs::write(&side, format!("{}\n", "x".repeat(70 * 1024))).unwrap();
    record(&events, &call("PreToolUse", "tu1", SID), t);
    assert_eq!(
        briefs_at_start(&events, &start, "2026-11-20T12:00:01.000Z"),
        vec!["451 T26: x".to_owned()]
    );
    // a `now` that does not parse, a start with no agent id, a session with no side file
    assert!(briefs_at_start(&events, &start, "T").is_empty());
    let mut bare = start.clone();
    bare.as_object_mut().unwrap().remove("agent_id");
    assert_eq!(
        briefs_at_start(&events, &bare, "2026-11-20T12:00:01.000Z").len(),
        1
    );
    bare["session_id"] = json!("s-other");
    assert!(briefs_at_start(&events, &bare, "2026-11-20T12:00:01.000Z").is_empty());
    assert!(briefs_at_start(Path::new("/"), &start, "2026-11-20T12:00:01.000Z").is_empty());
}
