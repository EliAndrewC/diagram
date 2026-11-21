//! The line and its log against a temporary clone; the verdicts against today's are the suite's
//! (`tests/hooks/test-event-log-hooks.sh`, replayed through the shim).

use std::path::Path;
use std::time::{Duration, UNIX_EPOCH};

use serde_json::{json, Value};

use super::{
    agent_category, append, bucket_of, category, common_git_dir, feature_of, line, make_target,
    now_stamp, typed_prompt, verdict_of,
};

fn clone(tag: &str) -> crate::shared::tempdir::TempDir {
    let d = crate::shared::tempdir::TempDir::new(&format!("guard-events-{tag}"));
    std::fs::create_dir_all(d.join(".git")).unwrap();
    std::fs::create_dir_all(d.join(".specify")).unwrap();
    std::fs::write(
        d.join(".specify/feature.json"),
        r#"{"feature_directory": "specs/999-a"}"#,
    )
    .unwrap();
    d
}

fn none(_: &str) -> Option<String> {
    None
}

#[test]
fn a_reply_is_read_for_its_verdict() {
    for (text, want) in [
        ("plan-verdict: recorded PASS for x", "PASS"),
        ("  VERDICT: needs-work\n", "NEEDS-WORK"),
        ("The plan is CLEAR.", "CLEAR"),
        ("impl-drift: 3 findings in all", "findings"),
        ("nothing to act on here", "clean"),
        ("COVERAGE 0; TRUTH 0", "clean"),
        ("COVERAGE 0; TRUTH 2", "findings"),
        ("units\nquote-check: x - READ 0 findings; ok", "clean"),
        ("units\nquote-check: x - READ 2 findings; ok", "findings"),
        ("the bundle was empty", "empty bundle"),
        ("words", ""),
    ] {
        assert_eq!(verdict_of(text), want, "{text}");
    }
}

#[test]
fn a_call_has_its_target_and_its_category() {
    assert_eq!(make_target("make -C x quick ALL=1"), "quick");
    assert_eq!(make_target("cat <<EOF\nmake done\nEOF"), "");
    assert_eq!(make_target("ls"), "");
    let ti = |v: Value| v.as_object().cloned().unwrap_or_default();
    assert_eq!(category("Edit", &ti(json!({}))), "edit");
    assert_eq!(
        category("Bash", &ti(json!({"command": "make done"}))),
        "gate"
    );
    assert_eq!(
        category("Bash", &ti(json!({"command": "make quick"}))),
        "tests"
    );
    assert_eq!(
        category("Bash", &ti(json!({"command": "make test-file FILE=x"}))),
        "tests"
    );
    assert_eq!(
        category("Bash", &ti(json!({"command": "make tick"}))),
        "spec-kit step"
    );
    assert_eq!(
        category("Bash", &ti(json!({"command": "ls"}))),
        "other tool"
    );
    assert_eq!(
        category("Skill", &ti(json!({"skill": "speckit-plan"}))),
        "spec-kit step"
    );
    assert_eq!(category("Skill", &ti(json!({"skill": "x"}))), "other tool");
    assert_eq!(
        category("Agent", &ti(json!({"subagent_type": "quote-check"}))),
        "record check"
    );
    for (agent, prompt, want) in [
        ("impl-drift", "", "claims check"),
        ("x", "claims-triage", "claims check"),
        ("x", "modal-triage", "record check"),
        ("glyph-check", "", "review check"),
        ("spec-fidelity-verify", "", "spec review"),
        ("round-arbiter", "", "round arbiter"),
        ("", "", "other subagent"),
    ] {
        assert_eq!(agent_category(agent, prompt), want);
    }
}

#[test]
fn each_events_line_carries_its_fields() {
    let t = "T";
    let bash = line(
        &json!({"hook_event_name": "PreToolUse", "session_id": "s", "tool_name": "Bash", "tool_use_id": "u", "agent_id": "a1", "tool_input": {"command": "make tick F=1 T=T07"}, "duration_ms": 12}),
        t,
    );
    assert_eq!(
        Value::Object(bash).to_string(),
        r#"{"t":"T","sid":"s","ev":"PreToolUse","tool":"Bash","id":"u","cat":"spec-kit step","by":"a1","make":"tick","task":"T07","ms":12}"#
    );
    let quick = line(
        &json!({"tool_name": "Bash", "tool_input": {"command": "make quick"}}),
        t,
    );
    assert_eq!(
        (quick["make"].as_str(), quick.get("task")),
        (Some("quick"), None)
    );
    let tick = line(
        &json!({"tool_name": "Bash", "tool_input": {"command": "make tick"}}),
        t,
    );
    assert!(tick.get("task").is_none() && tick["make"] == "tick");
    let edit = line(
        &json!({"tool_name": "Edit", "tool_input": {"file_path": "/p", "old_string": "a", "new_string": "### H"}}),
        t,
    );
    assert_eq!(
        (edit["old"].as_str(), edit["heading"].clone()),
        (Some("86f7e437faa5"), json!(true))
    );
    let write = line(
        &json!({"tool_name": "Write", "tool_input": {"notebook_path": "/n", "content": "x"}}),
        t,
    );
    assert_eq!(
        (write["path"].as_str(), write["new"].as_str().map(str::len)),
        (Some("/n"), Some(12))
    );
    let agent = line(
        &json!({"tool_name": "Agent", "tool_input": {"prompt": "read /tmp/x/MANIFEST.md UNIT: u1, now REVIEW_ROUNDS_OK=1"}, "tool_response": {"agentId": "ag"}}),
        t,
    );
    assert_eq!(
        (
            agent["agent"].as_str(),
            agent["manifest"].as_str(),
            agent["unit"].as_str(),
            agent["waiver"].clone(),
            agent["aid"].as_str()
        ),
        (
            Some("general-purpose"),
            Some("/tmp/x/MANIFEST.md"),
            Some("u1"),
            json!(1),
            Some("ag")
        )
    );
    let bare = line(
        &json!({"tool_name": "Agent", "tool_input": "not an object"}),
        t,
    );
    assert_eq!(bare["agent"], "general-purpose");
    let prompt = line(
        &json!({"hook_event_name": "UserPromptSubmit", "prompt": "go"}),
        t,
    );
    assert_eq!(prompt["gm"], true);
    let stop = line(
        &json!({"hook_event_name": "SubagentStop", "agent_type": "quote-check", "agent_id": "q", "last_assistant_message": "PASS"}),
        t,
    );
    assert_eq!(
        (stop["cat"].as_str(), stop["verdict"].as_str()),
        (Some("record check"), Some("PASS"))
    );
    let start = line(&json!({"hook_event_name": "SubagentStart"}), t);
    assert!(start.get("verdict").is_none() && start["agent"] == "");
    assert_eq!(
        line(&json!({"hook_event_name": "Stop", "session_id": 0}), t)["sid"],
        ""
    );
}

#[test]
fn a_prompt_is_the_gms_when_typed() {
    assert!(typed_prompt(&json!("go")));
    assert!(!typed_prompt(&json!("<system-reminder>x")));
    assert!(!typed_prompt(&json!("  ")));
    assert!(typed_prompt(&json!([{"type": "text", "text": "go"}])));
    assert!(!typed_prompt(
        &json!([{"type": "text", "text": "go"}, {"type": "tool_result"}])
    ));
    assert!(!typed_prompt(&json!([{"type": "image"}])));
    assert!(typed_prompt(&json!(3)));
}

#[test]
fn the_line_goes_to_the_features_log_in_the_clones_git_dir() {
    let d = clone("append");
    let p = append(
        &json!({"hook_event_name": "Stop", "cwd": d.to_string_lossy()}),
        "T",
        Path::new("/"),
        &none,
    )
    .unwrap();
    assert_eq!(
        p,
        std::fs::canonicalize(&d)
            .unwrap()
            .join(".git/l7r-events/999-a.jsonl")
    );
    assert!(append(&json!({"cwd": "/"}), "T", Path::new("/"), &none).is_none());
    let to = d.join("events");
    let env = |k: &str| (k == "L7R_EVENTS_DIR").then(|| to.to_string_lossy().into_owned());
    assert_eq!(
        append(&json!({"hook_event_name": "Stop"}), "T", &d, &env).unwrap(),
        to.join("999-a.jsonl")
    );
    assert!(now_stamp(UNIX_EPOCH + Duration::from_millis(1_500)) == "1970-01-01T00:00:01.500Z");
}

#[test]
fn an_edit_that_puts_back_replaced_text_owes_the_arbiter() {
    let d = clone("reversal");
    let edit = |old: &str, new: &str| json!({"hook_event_name": "PreToolUse", "cwd": d.to_string_lossy(), "tool_name": "Edit", "tool_input": {"file_path": "/f", "old_string": old, "new_string": new}});
    append(&edit("A", "B"), "1", &d, &none).unwrap();
    append(&edit("B", "A"), "2", &d, &none).unwrap();
    let owed = std::fs::read_to_string(d.join(".git/arbiter-owed.json")).unwrap();
    assert!(owed.contains("reversal:/f"));
    std::fs::remove_file(d.join(".git/arbiter-owed.json")).unwrap();
    append(&edit("A", "C"), "3", &d, &none).unwrap();
    assert!(!d.join(".git/arbiter-owed.json").exists());
}

#[test]
fn the_feature_and_the_git_dir_are_read_as_the_tool_reads_them() {
    let d = clone("feature");
    assert_eq!(feature_of(&d, &none), "999-a");
    assert_eq!(
        feature_of(&d, &|k: &str| (k == "L7R_FEATURE_DIRECTORY")
            .then(|| "specs/444-b/".to_owned())),
        "444-b"
    );
    std::fs::create_dir_all(d.join("specs/445-c")).unwrap();
    assert_eq!(
        feature_of(&d, &|k: &str| (k == "SPECIFY_FEATURE")
            .then(|| "445-c".to_owned())),
        "445-c"
    );
    assert_eq!(
        feature_of(&d, &|k: &str| (k == "SPECIFY_FEATURE")
            .then(|| "446-missing".to_owned())),
        "999-a"
    );
    std::fs::write(d.join(".specify/feature.json"), "not json").unwrap();
    assert_eq!(feature_of(&d, &none), "");
    let wt = d.join("wt");
    std::fs::create_dir_all(d.join(".git/worktrees/wt")).unwrap();
    std::fs::create_dir_all(&wt).unwrap();
    std::fs::write(wt.join(".git"), "gitdir: ../.git/worktrees/wt\n").unwrap();
    std::fs::write(d.join(".git/worktrees/wt/commondir"), "../..\n").unwrap();
    assert_eq!(
        common_git_dir(&wt),
        std::fs::canonicalize(d.join(".git")).unwrap()
    );
    std::fs::remove_file(d.join(".git/worktrees/wt/commondir")).unwrap();
    assert_eq!(
        common_git_dir(&wt),
        std::fs::canonicalize(d.join(".git/worktrees/wt")).unwrap()
    );
    assert!(super::decide(
        &crate::protocol::Event {
            name: "Stop".into(),
            input: json!({"hook_event_name": "Stop", "cwd": "/"})
        },
        &crate::shared::session::Session::from_input(&json!({}))
    )
    .is_empty());
}

#[test]
fn the_edges_of_a_value_and_a_path() {
    use super::{text_of, truthy};
    assert_eq!(verdict_of(&format!("{} PASS", "x".repeat(700))), "");
    assert_eq!(
        (
            text_of(Some(&json!(5))),
            text_of(Some(&json!(0))),
            text_of(Some(&json!(false))),
            text_of(None)
        ),
        ("5".into(), String::new(), String::new(), String::new())
    );
    assert!(
        !truthy(&json!(null))
            && truthy(&json!(true))
            && !truthy(&json!([]))
            && truthy(&json!({"a": 1}))
            && !truthy(&json!({}))
    );
    let typed = line(
        &json!({"tool_name": "Agent", "tool_input": {"subagent_type": "quote-check"}}),
        "T",
    );
    assert_eq!(typed["agent"], "quote-check");
    let read = line(
        &json!({"tool_name": "Read", "tool_input": {"file_path": "/f"}}),
        "T",
    );
    assert!(read.get("path").is_none() && read["cat"] == "other tool");
    let start = line(
        &json!({"tool_name": "Bash", "tool_input": {"command": "make task-start F=1 T=T3"}}),
        "T",
    );
    assert_eq!(start["task"], "T3");
    assert!(append(
        &json!({"hook_event_name": "Stop", "cwd": "/nonexistent/deeper"}),
        "T",
        Path::new("/"),
        &none
    )
    .is_none());
    let d = clone("edges");
    std::fs::remove_file(d.join(".specify/feature.json")).unwrap();
    assert!(append(
        &json!({"hook_event_name": "Stop", "cwd": d.to_string_lossy()}),
        "T",
        &d,
        &none
    )
    .unwrap()
    .ends_with("_unassigned.jsonl"));
    let wt = d.join("wt");
    std::fs::create_dir_all(&wt).unwrap();
    std::fs::write(wt.join(".git"), "gitdir: missing/dir\n").unwrap();
    assert_eq!(common_git_dir(&wt), wt.join("missing/dir"));
    std::fs::create_dir_all(d.join("g")).unwrap();
    std::fs::write(d.join("g/commondir"), "nowhere\n").unwrap();
    std::fs::write(wt.join(".git"), "gitdir: ../g\n").unwrap();
    assert_eq!(
        common_git_dir(&wt),
        std::fs::canonicalize(d.join("g")).unwrap().join("nowhere")
    );
    let outcome = super::decide(
        &crate::protocol::Event {
            name: "Stop".into(),
            input: json!({"hook_event_name": "Stop", "cwd": d.to_string_lossy()}),
        },
        &crate::shared::session::Session::from_input(&json!({})),
    );
    assert!(outcome.is_empty());
}

#[test]
fn a_bash_call_that_runs_no_make_target_names_none() {
    assert!(line(
        &json!({"tool_name": "Bash", "tool_input": {"command": "ls"}}),
        "T"
    )
    .get("make")
    .is_none());
}

#[test]
fn a_features_log_is_named_for_it() {
    let root = clone("log-path");
    assert!(super::log_path(&root, "500-f").ends_with("500-f.jsonl"));
    let named = |k: &str| (k == "L7R_EVENTS_DIR").then(|| "/elsewhere".to_owned());
    assert_eq!(
        super::log_path_in(&root, "", &named),
        Path::new("/elsewhere/_unassigned.jsonl")
    );
    assert_eq!(
        super::log_path_in(&root, "f", &none),
        root.join(".git/l7r-events/f.jsonl")
    );
}

/// T207: a payload that names no hook event is no hook's - the measure crate's test of an empty input (`l7r-gate measure event-log hook`
/// given nothing) wrote a `{"sid": "", "ev": ""}` row into the clone's real log on every `make static` and `make rust-test` of that crate,
/// 348 of them 2026-11-12 to 11-19 (18 more on 11-08 carried `--self-check`'s `"tool": "Bash"`), and `make where-time` read them as a
/// session whose gaps were 379 minutes of "idle".
#[test]
fn a_payload_naming_no_event_writes_no_line() {
    let d = clone("no-event");
    let cwd = d.to_string_lossy().into_owned();
    for payload in [
        json!({"cwd": cwd}),
        json!({"cwd": cwd, "hook_event_name": ""}),
        json!({"cwd": cwd, "tool_name": "Bash", "tool_input": {"command": "true"}}),
    ] {
        assert!(append(&payload, "T", &d, &none).is_none(), "{payload}");
    }
    assert!(!d.join(".git/l7r-events").exists());
}

/// Feature 451 T03 (FR-001, D2): the old categorizer knew `quick`, `test-file`, `done` and three spec-kit targets, so `make static`,
/// `make rust-test`, `make hooks-test` and the gate's own `l7r-gate.sh rust test` were all "other tool" - 210 of the window's tool-minutes
/// (research R1). One table books a target by its bucket; a target it does not know is `other`, never dropped.
#[test]
fn the_category_table_books_a_target_by_its_bucket() {
    for (target, want) in [
        ("static", "tests"),
        ("rust-test", "tests"),
        ("hooks-test", "tests"),
        ("quick", "tests"),
        ("format", "tests"),
        ("map", "tests"),
        ("done", "gate"),
        ("cohort-landing", "gate"),
        ("land", "land"),
        ("land-tooling", "land"),
        ("plan-delta", "review"),
        ("decide", "review"),
        ("record", "docs"),
        ("render-sync", "docs"),
        ("tick", "spec-kit step"),
        ("rust-hamlet", "other"),
        ("frobnicate", "other"),
        ("", "other"),
    ] {
        assert_eq!(bucket_of(target), want, "{target}");
    }
    let ti = |c: &str| {
        json!({ "command": c })
            .as_object()
            .cloned()
            .unwrap_or_default()
    };
    for (command, want) in [
        ("make static", "tests"),
        ("timeout 2400 make rust-test CRATE=rust/guard", "tests"),
        ("(make hooks-test > /tmp/h.log 2>&1) &", "tests"),
        (
            "scripts/gates/l7r-gate.sh rust test --crate rust/guard",
            "tests",
        ),
        ("make land F=451 T=T05", "land"),
        ("make frobnicate", "other tool"),
        ("ls", "other tool"),
    ] {
        assert_eq!(category("Bash", &ti(command)), want, "{command}");
    }
}

/// Feature 451 T03 (D2): a line carries `task` where one is known - a `tick`, `task-start`, `decide` or `land` command's `T=` first.
#[test]
fn a_commands_task_is_its_t() {
    for (command, want) in [
        ("make land F=451 T=T05", Some("T05")),
        ("make land F=451 T=\"T05\"", Some("T05")),
        ("make land F=451 T='T05'", Some("T05")),
        ("make decide F=451 T=T7a", Some("T7a")),
        ("make static T=T05", None),
    ] {
        let row = line(
            &json!({"tool_name": "Bash", "tool_input": {"command": command}}),
            "T",
        );
        assert_eq!(row.get("task").and_then(|v| v.as_str()), want, "{command}");
    }
}

fn session_files(d: &Path, aid: &str, meta: &str) -> String {
    let transcript = d.join("projects/s1.jsonl");
    std::fs::create_dir_all(d.join("projects/s1/subagents")).unwrap();
    std::fs::write(
        d.join(format!("projects/s1/subagents/agent-{aid}.meta.json")),
        meta,
    )
    .unwrap();
    transcript.to_string_lossy().into_owned()
}

fn last_line(log: &Path) -> Value {
    let text = std::fs::read_to_string(log).unwrap();
    serde_json::from_str(text.lines().last().unwrap()).unwrap()
}

/// Feature 451 T03 (D2): no `T=` - a subagent's line carries the `T<n>` its meta file's `description` names; else, and for the main
/// session, the clone's last `task-starts.jsonl` entry for the log's feature. Nothing found, no field; a file that is missing or does not
/// parse is no error.
#[test]
fn a_line_with_no_t_carries_the_agents_task_else_the_clones() {
    let d = clone("task");
    let cwd = d.to_string_lossy().into_owned();
    let transcript = session_files(
        &d,
        "ab1",
        r#"{"agentType":"general-purpose","description":"451 T07: the agent's cost","toolUseId":"tu"}"#,
    );
    session_files(
        &d,
        "nodesc",
        r#"{"agentType":"general-purpose","description":"read the log"}"#,
    );
    session_files(&d, "bad", "not json");
    let call = |by: Option<&str>| {
        let mut p = json!({"hook_event_name": "PreToolUse", "cwd": cwd, "transcript_path": transcript, "tool_name": "Bash", "tool_input": {"command": "make static"}});
        if let Some(aid) = by {
            p["agent_id"] = json!(aid);
        }
        p
    };
    let task = |p: &Value| {
        let log = append(p, "T", &d, &none).unwrap();
        last_line(&log).get("task").cloned()
    };
    // no task-starts.jsonl yet: a main-session call names none
    assert_eq!(task(&call(None)), None);
    assert_eq!(task(&call(Some("ab1"))), Some(json!("T07")));
    std::fs::write(
        d.join(".git/task-starts.jsonl"),
        concat!(
            "{\"feature\": \"999-a\", \"task\": \"T02\", \"utc\": \"2026-11-20T01:00:00Z\"}\n",
            "not json\n",
            "{\"feature\": \"999-a\", \"task\": \"T03\", \"utc\": \"2026-11-20T02:00:00Z\"}\n",
            "{\"feature\": \"449-other\", \"task\": \"T237\", \"utc\": \"2026-11-20T03:00:00Z\"}\n",
            "\n",
        ),
    )
    .unwrap();
    assert_eq!(task(&call(None)), Some(json!("T03")));
    assert_eq!(task(&call(Some("ab1"))), Some(json!("T07")));
    for aid in ["nodesc", "bad", "missing"] {
        assert_eq!(task(&call(Some(aid))), Some(json!("T03")), "{aid}");
    }
    // a subagent's own stop is its line too (D10 reads an agent's first line)
    let stop = json!({"hook_event_name": "SubagentStop", "cwd": cwd, "transcript_path": transcript, "agent_id": "ab1", "agent_type": "general-purpose"});
    assert_eq!(task(&stop), Some(json!("T07")));
    // a command's own T= wins
    let mut land = call(Some("ab1"));
    land["tool_input"]["command"] = json!("make land F=999 T=T09");
    assert_eq!(task(&land), Some(json!("T09")));
    // no transcript path: the clone's
    let mut bare = call(Some("ab1"));
    bare.as_object_mut().unwrap().remove("transcript_path");
    assert_eq!(task(&bare), Some(json!("T03")));
    // no feature: no task-starts entry is the log's
    std::fs::remove_file(d.join(".specify/feature.json")).unwrap();
    assert_eq!(task(&call(None)), None);
}

/// Feature 451 T26: one clone working two features, `.specify/feature.json` naming `449-b`, the one whose task started last; a `451 T26`
/// builder, a `449 T236` builder, briefs naming only a task, only a feature, or neither.
struct Builders {
    d: crate::shared::tempdir::TempDir,
    cwd: String,
    transcript: String,
}

type Filed = (String, Option<String>, bool);

impl Builders {
    fn new(tag: &str) -> Self {
        let d = clone(tag);
        let cwd = d.to_string_lossy().into_owned();
        for f in ["449-b", "451-a", "450-c"] {
            std::fs::create_dir_all(d.join("specs").join(f)).unwrap();
        }
        std::fs::write(
            d.join(".specify/feature.json"),
            r#"{"feature_directory": "specs/449-b"}"#,
        )
        .unwrap();
        std::fs::write(
            d.join(".git/task-starts.jsonl"),
            concat!(
                "{\"feature\": \"449-b\", \"task\": \"T226\", \"utc\": \"2026-11-20T05:00:00Z\"}\n",
                "{\"feature\": \"451-a\", \"task\": \"T03\", \"utc\": \"2026-11-20T07:00:00Z\"}\n",
                "{\"feature\": \"451-a\", \"task\": \"T26\", \"utc\": \"2026-11-20T08:00:00Z\"}\n",
                "{\"feature\": \"449-b\", \"task\": \"T236\", \"utc\": \"2026-11-20T08:00:01Z\"}\n",
            ),
        )
        .unwrap();
        let transcript = session_files(
            &d,
            "a451",
            r#"{"description":"451 T26: each line under its own feature"}"#,
        );
        for (aid, brief) in [
            ("a449", "449 T236: the reed strip"),
            ("anum", "T226: polder counters"),
            ("afeat", "spec-fidelity plan review of 451, round 2"),
            ("anone", "record-format 0054 r3"),
            ("acount", "Arbiter: FR-451 and 450 owed claims"),
        ] {
            session_files(&d, aid, &format!(r#"{{"description":"{brief}"}}"#));
        }
        Self { d, cwd, transcript }
    }

    fn bash(&self, by: Option<&str>, command: &str, ev: &str) -> Value {
        let mut p = json!({"hook_event_name": ev, "cwd": self.cwd, "transcript_path": self.transcript, "tool_name": "Bash", "tool_input": {"command": command}});
        if let Some(aid) = by {
            p["agent_id"] = json!(aid);
        }
        p
    }

    /// The log a payload's line went to, its task, and whether it is marked `fallback`.
    fn filed(&self, p: &Value) -> Filed {
        let log = append(p, "T", &self.d, &none).unwrap();
        let row = last_line(&log);
        (
            log.file_stem().unwrap().to_string_lossy().into_owned(),
            row.get("task").and_then(Value::as_str).map(str::to_owned),
            row.get("fallback").is_some(),
        )
    }
}

fn want(f: &str, t: &str, fb: bool) -> Filed {
    (f.to_owned(), Some(t.to_owned()), fb)
}

/// Each line is filed under the feature of the task it carries: a command's `F=`, the dispatch's brief, the task-start in force for
/// its task.
#[test]
fn two_features_builders_in_one_clone_each_line_in_its_own_log() {
    let b = Builders::new("two-builders");
    // each builder's own calls, by its brief
    assert_eq!(
        b.filed(&b.bash(Some("a451"), "make static", "PreToolUse")),
        want("451-a", "T26", false)
    );
    assert_eq!(
        b.filed(&b.bash(Some("a449"), "make static", "PreToolUse")),
        want("449-b", "T236", false)
    );
    // a brief naming a task and no feature: the feature that started that task
    assert_eq!(
        b.filed(&b.bash(Some("anum"), "ls", "PostToolUse")),
        want("449-b", "T226", false)
    );
    // a brief naming a feature and no task: that feature's task-start in force
    assert_eq!(
        b.filed(&b.bash(Some("afeat"), "ls", "PostToolUse")),
        want("451-a", "T26", false)
    );
    // the main session's landing and task start: the command's F=, both halves of the call
    for ev in ["PreToolUse", "PostToolUse"] {
        assert_eq!(
            b.filed(&b.bash(None, "make land F=451 T=T03 NOTE=x", ev)),
            want("451-a", "T03", false)
        );
        assert_eq!(
            b.filed(&b.bash(None, "make task-start F=451 T=T26", ev)),
            want("451-a", "T26", false)
        );
    }
    assert_eq!(
        b.filed(&b.bash(None, "make tick F=449 T=T236", "PreToolUse")),
        want("449-b", "T236", false)
    );
    // F= with no T=: that feature's task in force; F= naming the whole directory
    assert_eq!(
        b.filed(&b.bash(None, "make where-time F=451", "PreToolUse")),
        want("451-a", "T26", false)
    );
    assert_eq!(
        b.filed(&b.bash(None, "make where-time F=451-a", "PreToolUse")),
        want("451-a", "T26", false)
    );
    // a feature with no task started: filed under it with no task
    assert_eq!(
        b.filed(&b.bash(None, "make where-time F=450", "PreToolUse")),
        ("450-c".to_owned(), None, false)
    );
    // the dispatch's own line, by its description; a builder's own dispatch with none, by its own brief
    let agent = json!({"hook_event_name": "PreToolUse", "cwd": b.cwd, "tool_name": "Agent", "tool_input": {"description": "451 T26: each line", "prompt": "x"}});
    assert_eq!(b.filed(&agent), want("451-a", "T26", false));
    let nested = json!({"hook_event_name": "PreToolUse", "cwd": b.cwd, "transcript_path": b.transcript, "agent_id": "a449", "tool_name": "Agent", "tool_input": {"prompt": "x"}});
    assert_eq!(b.filed(&nested), want("449-b", "T236", false));
    // a subagent's stop, by its brief
    let stop = json!({"hook_event_name": "SubagentStop", "cwd": b.cwd, "transcript_path": b.transcript, "agent_id": "a451", "agent_type": "general-purpose"});
    assert_eq!(b.filed(&stop), want("451-a", "T26", false));
}

/// Where nothing on the line says: feature.json's feature, its task in force, the line marked `fallback`.
#[test]
fn a_line_nothing_names_is_filed_by_feature_json_and_marked() {
    let b = Builders::new("two-builders-fallback");
    assert_eq!(
        b.filed(&b.bash(None, "make static", "PreToolUse")),
        want("449-b", "T236", true)
    );
    assert_eq!(
        b.filed(&b.bash(Some("anone"), "ls", "PreToolUse")),
        want("449-b", "T236", true)
    );
    // a brief's counts and hyphenated ids name no feature: 451 only inside `FR-451`, 450 a feature this clone never started
    assert_eq!(
        b.filed(&b.bash(Some("acount"), "ls", "PreToolUse")),
        want("449-b", "T236", true)
    );
    // an F= naming no single feature directory says nothing
    assert_eq!(
        b.filed(&b.bash(None, "make where-time F=4", "PreToolUse")),
        want("449-b", "T236", true)
    );
    // a session that declares its feature (a page session's L7R_FEATURE_DIRECTORY, a SPECIFY_FEATURE naming one) is not marked
    let p = b.bash(None, "make static", "PreToolUse");
    for (k, v) in [
        ("L7R_FEATURE_DIRECTORY", "specs/451-a/"),
        ("SPECIFY_FEATURE", "451-a"),
    ] {
        let log = append(&p, "T", &b.d, &|e: &str| (e == k).then(|| v.to_owned())).unwrap();
        assert!(log.ends_with("451-a.jsonl"), "{k}");
        assert!(last_line(&log).get("fallback").is_none(), "{k}");
    }
    // a SPECIFY_FEATURE naming no feature declares nothing
    let log = append(&p, "T", &b.d, &|e: &str| {
        (e == "SPECIFY_FEATURE").then(|| "999-none".to_owned())
    })
    .unwrap();
    assert_eq!(last_line(&log).get("fallback"), Some(&json!(true)));
}

mod background;
mod cost;
