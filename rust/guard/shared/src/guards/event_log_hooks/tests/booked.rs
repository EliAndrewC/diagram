//! Feature 451 T161: an edit is booked to the task the editing agent's own brief names, the clone's mark only for the main session's own
//! lines. WHY: the 449 sheet bundle's builder, described `449 sheet bundle (fresh 3): verify, the nine map reviews, closing` and briefed
//! `449 bundle T312, T313, ...` on its prompt's first line, had its edits of `reviews/owed.rs`, `reviews/prereq.rs`, their tests and
//! `gen_tests_seat.rs` booked to T317, the record bundle's task the mark named, and that bundle's landing was refused at land-alone's
//! own-edits step (observed 2026-11-22, method: the 449 log's edit lines `by` a6ed2241ba6a59166, read against its meta file and
//! transcript).

use std::path::Path;

use serde_json::{json, Value};

use super::super::append;
use super::{clone, last_line, none, session_files};
use crate::guards::set_down_hooks::{agent_builder, page_session_brief};

/// A clone working 451-a, its mark naming T09; a bundle builder `abun` whose description names no task and whose prompt's first line
/// names T05 and T06; a review `arev` that builder launched; an agent `aloose` nothing names a task for.
struct World {
    d: crate::tempdir::TempDir,
    transcript: String,
}

impl World {
    fn new(tag: &str) -> Self {
        let d = clone(tag);
        std::fs::create_dir_all(d.join("specs/451-a")).unwrap();
        std::fs::write(
            d.join(".specify/feature.json"),
            r#"{"feature_directory": "specs/451-a"}"#,
        )
        .unwrap();
        std::fs::write(
            d.join(".git/task-starts.jsonl"),
            concat!(
                "{\"feature\": \"451-a\", \"task\": \"T05\", \"utc\": \"2026-11-22T01:00:00Z\"}\n",
                "{\"feature\": \"451-a\", \"task\": \"T09\", \"utc\": \"2026-11-22T02:00:00Z\"}\n",
            ),
        )
        .unwrap();
        let transcript = session_files(
            &d,
            "abun",
            r#"{"description":"451 sheet bundle (fresh 3): verify, the reviews, closing","spawnDepth":1}"#,
        );
        let first = json!({"type": "user", "message": {"role": "user", "content": "451 bundle T05, T06, a fresh builder\nT09 is another's"}});
        std::fs::write(
            d.join("projects/s1/subagents/agent-abun.jsonl"),
            format!("{first}\n"),
        )
        .unwrap();
        session_files(
            &d,
            "arev",
            r#"{"description":"building-review of the sheet","spawnDepth":2,"parentAgentId":"abun"}"#,
        );
        session_files(
            &d,
            "aloose",
            r#"{"description":"read the log","spawnDepth":1}"#,
        );
        Self { d, transcript }
    }

    fn call(&self, by: Option<&str>, tool: &str, input: &Value) -> Value {
        let mut p = json!({"hook_event_name": "PostToolUse", "cwd": self.d.to_string_lossy(), "session_id": "s1",
            "transcript_path": self.transcript, "tool_name": tool, "tool_use_id": "tu", "tool_input": input});
        if let Some(a) = by {
            p["agent_id"] = json!(a);
        }
        p
    }

    fn edit(&self, by: Option<&str>) -> Value {
        self.call(
            by,
            "Edit",
            &json!({"file_path": self.d.join("src/a.rs"), "old_string": "a", "new_string": "b"}),
        )
    }

    /// The log `p`'s line went to and its task, with the environment `env`.
    fn booked(&self, p: &Value, env: &dyn Fn(&str) -> Option<String>) -> (String, Option<String>) {
        let log = append(p, "2026-11-22T03:00:00.000Z", &self.d, env).unwrap();
        let row = last_line(&log);
        (
            log.file_stem().unwrap().to_string_lossy().into_owned(),
            row.get("task").and_then(Value::as_str).map(str::to_owned),
        )
    }
}

fn at(task: Option<&str>) -> (String, Option<String>) {
    ("451-a".to_owned(), task.map(str::to_owned))
}

/// An edit by an agent whose brief names T05, made while the mark names T09, is T05's: a bundle builder's by its prompt's first line, a
/// review it launched by its builder's; one nothing names carries no task, never the mark's; the main session's own edit is the mark's.
#[test]
fn an_edit_is_booked_to_its_editors_brief_not_the_mark() {
    let w = World::new("booked");
    assert_eq!(w.booked(&w.edit(Some("abun")), &none), at(Some("T05")));
    assert_eq!(w.booked(&w.edit(Some("arev")), &none), at(Some("T05")));
    let env = |k: &str| (k == "SPECIFY_FEATURE").then(|| "451-a".to_owned());
    assert_eq!(w.booked(&w.edit(Some("aloose")), &env), at(None));
    assert_eq!(w.booked(&w.edit(Some("agone")), &env), at(None));
    assert_eq!(w.booked(&w.edit(None), &env), at(Some("T09")));
    // a bundle member's own closing step is its own, no correction: its later lines stay T05's
    let decide = w.call(
        Some("abun"),
        "Bash",
        &json!({"command": "make decide F=451 T=T06"}),
    );
    let mut pre = decide.clone();
    pre["hook_event_name"] = json!("PreToolUse");
    w.booked(&pre, &none);
    assert_eq!(w.booked(&w.edit(Some("abun")), &none), at(Some("T05")));
}

/// A page session's lines are booked to its brief's task, the mark never: its first line's, else its file name's; a session the index
/// does not hold carries none.
#[test]
fn a_page_sessions_edit_is_booked_to_its_brief() {
    let w = World::new("booked-page");
    let briefs = w.d.join("specs/451-a/briefs");
    std::fs::create_dir_all(&briefs).unwrap();
    std::fs::write(
        briefs.join("t05-write.md"),
        "# Brief - feature 451 task T05, the page\n",
    )
    .unwrap();
    std::fs::write(briefs.join("t07-checks.md"), "# Brief - the checks\n").unwrap();
    std::fs::create_dir_all(w.d.join(".git/page-sessions")).unwrap();
    std::fs::write(
        w.d.join(".git/page-sessions/index.txt"),
        format!(
            "ps1 {0}/t05-write.md\nps2 {0}/t07-checks.md\n",
            briefs.display()
        ),
    )
    .unwrap();
    let page = |sid: &'static str| {
        move |k: &str| match k {
            "L7R_PAGE_SESSION" => Some(sid.to_owned()),
            "L7R_FEATURE_DIRECTORY" => Some("specs/451-a/".to_owned()),
            _ => None,
        }
    };
    assert_eq!(w.booked(&w.edit(None), &page("ps1")), at(Some("T05")));
    assert_eq!(w.booked(&w.edit(None), &page("ps2")), at(Some("T07")));
    assert_eq!(w.booked(&w.edit(None), &page("ps3")), at(None));
    // a page session's own agent naming none: its page session's
    assert_eq!(
        w.booked(&w.edit(Some("aloose")), &page("ps1")),
        at(Some("T05"))
    );
}

/// 451 T167: a page session's line is booked by its SESSION ID in the index, its environment naming no `L7R_PAGE_SESSION`, while the
/// mark names T09 - T330's page sessions' lines went to the mark's T328 (observed 2026-11-23). Its brief's first line names its task
/// (`t05a-checks.md`, "feature 451 T05 and T07"); a listed session whose brief names none carries none, never the mark; a session the
/// index does not list is the main session, the mark's.
#[test]
fn a_page_sessions_line_is_booked_by_its_session_id() {
    let w = World::new("booked-sid");
    let briefs = w.d.join("specs/451-a/briefs");
    std::fs::create_dir_all(&briefs).unwrap();
    std::fs::write(
        briefs.join("t05a-checks.md"),
        "# Brief - feature 451 T05 and T07.5 (0101, 0104), session 2: check and apply\n",
    )
    .unwrap();
    std::fs::write(briefs.join("notes.md"), "# Brief - the checks\n").unwrap();
    std::fs::create_dir_all(w.d.join(".git/page-sessions")).unwrap();
    let index = |brief: &str| {
        std::fs::write(
            w.d.join(".git/page-sessions/index.txt"),
            format!("other {0}/notes.md\ns1 {0}/{brief}\n", briefs.display()),
        )
        .unwrap();
    };
    let env = |k: &str| (k == "SPECIFY_FEATURE").then(|| "451-a".to_owned());
    index("t05a-checks.md");
    assert_eq!(w.booked(&w.edit(None), &env), at(Some("T05")));
    // its own agent naming none: its session's
    assert_eq!(w.booked(&w.edit(Some("aloose")), &env), at(Some("T05")));
    index("notes.md");
    assert_eq!(w.booked(&w.edit(None), &env), at(None));
    std::fs::write(w.d.join(".git/page-sessions/index.txt"), "other x\n").unwrap();
    assert_eq!(w.booked(&w.edit(None), &env), at(Some("T09")));
}

/// The page-session reader's every refusal: no index, no `specs/` in the path, nothing after it, no task in the line or the name.
#[test]
fn a_page_session_brief_names_its_feature_and_task_or_nothing() {
    let w = World::new("booked-reader");
    let root: &Path = &w.d;
    assert_eq!(page_session_brief(root, "ps1"), None);
    std::fs::create_dir_all(w.d.join(".git/page-sessions")).unwrap();
    std::fs::write(
        w.d.join(".git/page-sessions/index.txt"),
        format!(
            "ps1 /tmp/no/brief.md\nps2 {0}/specs\nps3 {0}/specs/451-a/notes.md\nps4 {0}/specs/451-a/t08-x.md\n",
            w.d.display()
        ),
    )
    .unwrap();
    assert_eq!(page_session_brief(root, "ps1"), None);
    assert_eq!(page_session_brief(root, "ps2"), None);
    assert_eq!(page_session_brief(root, "ps3"), None);
    assert_eq!(
        page_session_brief(root, "ps4"),
        Some(("451-a".to_owned(), "T08".to_owned()))
    );
}

/// The builder reading's refusals: a meta missing, one naming no builder.
#[test]
fn an_agents_builder_is_its_own_or_its_dispatchers() {
    let w = World::new("booked-builder");
    let dir = w.d.join("projects/s1/subagents");
    let both = Some(("451".to_owned(), vec!["T05".to_owned(), "T06".to_owned()]));
    assert_eq!(agent_builder(&dir, "abun"), both);
    assert_eq!(agent_builder(&dir, "arev"), both);
    assert_eq!(agent_builder(&dir, "aloose"), None);
    assert_eq!(agent_builder(&dir, "agone"), None);
    // a line with no transcript reads no builder
    let mut p = w.edit(Some("abun"));
    p.as_object_mut().unwrap().remove("transcript_path");
    assert_eq!(w.booked(&p, &none), at(None));
}

/// A correction to a bundle builder whose description names no task is read against its builder reading's task: "T07, not T05"
/// re-numbers it, and its later lines are T07's.
#[test]
fn a_bundle_builder_is_corrected_from_its_builder_readings_task() {
    let w = World::new("booked-corrected");
    let send = w.call(
        None,
        "SendMessage",
        &json!({"to": "abun", "summary": "Your task is T07, not T05", "message": ""}),
    );
    w.booked(&send, &none);
    assert_eq!(w.booked(&w.edit(Some("abun")), &none), at(Some("T07")));
}
