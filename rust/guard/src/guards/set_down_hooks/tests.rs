//! The decider over a fixture clone, `speckit-todo.py` stubbed by a shell script (`tests/hooks/test-set-down-hooks.sh`, replayed through the shim, runs the real one).

use std::path::{Path, PathBuf};

use serde_json::json;

use super::{decide, judge, open_boxes, verdict, Ctx};
use crate::protocol::{Answer, Event};
use crate::shared::session::Session;
use crate::shared::tool::ask;

const TASKS: &str = "- [x] T01 done\n- [ ] T02 the next thing\n- [ ] T03 later\n- [ ] GM review (make gm-reviewed F=385)\n";
const START: &str =
    "{\"feature\": \"385-x\", \"task\": \"T02\", \"utc\": \"2026-10-18T23:00:00Z\"}\n";

/// A clone with a started feature and an empty transcript; the status tool answers `closed`.
fn world(tag: &str, closed: &str) -> (PathBuf, PathBuf, Ctx<'static>) {
    crate::shared::log::quiet();
    let d = std::env::temp_dir().join(format!("l7r-guard-setdown-{tag}-{}", std::process::id()));
    let _ = std::fs::remove_dir_all(&d);
    std::fs::create_dir_all(d.join("c/specs/385-x")).unwrap();
    std::fs::create_dir_all(d.join("tree/scripts")).unwrap();
    let d = d.canonicalize().unwrap();
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
    std::fs::write(
        d.join("tree/scripts/speckit-todo.py"),
        format!("echo {closed}\n"),
    )
    .unwrap();
    std::fs::write(d.join("tr.jsonl"), "").unwrap();
    let ctx = Ctx {
        tree: d.join("tree"),
        python: "sh",
    };
    (c, d.join("tr.jsonl"), ctx)
}

fn said(c: &Path, tr: &Path, ctx: &Ctx) -> Option<String> {
    verdict(c, &tr.to_string_lossy(), ctx).unwrap()
}

fn append(tr: &Path, line: &str) {
    let old = std::fs::read_to_string(tr).unwrap();
    std::fs::write(tr, format!("{old}{line}\n")).unwrap();
}

#[test]
fn an_open_task_with_nothing_running_is_refused_naming_the_next_step() {
    let (c, tr, ctx) = world("refuse", "no");
    let text = said(&c, &tr, &ctx).unwrap();
    assert!(text.contains("feature 385-x has 2 open task(s)"));
    assert!(text.contains("(T02 the next thing)"));
    assert!(text.contains("make set-down F=385 WHY="));
}

#[test]
fn work_still_running_lets_the_turn_end_until_it_reports_back() {
    let (c, tr, ctx) = world("running", "no");
    append(&tr, r#"{"toolUseResult": {"backgroundTaskId": "b1abc"}}"#);
    assert_eq!(said(&c, &tr, &ctx), None);
    append(
        &tr,
        "<task-notification><task-id>b1abc</task-id></task-notification>",
    );
    assert!(said(&c, &tr, &ctx).is_some());
    append(&tr, r#"{"toolUseResult": {"agentId": "a9f00"}}"#);
    assert_eq!(said(&c, &tr, &ctx), None);
    append(
        &tr,
        r#"{"name": "TaskStop", "input": {"task_id": "a9f00"}}"#,
    );
    assert!(said(&c, &tr, &ctx).is_some());
    append(&tr, r#"{"status": "async_launched", "taskId": "w9wave"}"#);
    assert_eq!(said(&c, &tr, &ctx), None);
    append(&tr, "<task-id>w9wave</task-id>");
    append(&tr, "Command running in background with ID: b4note.");
    assert!(said(&c, &tr, &ctx).is_some());
}

#[test]
fn a_set_down_since_the_start_or_a_closing_status_lets_it_end() {
    let (c, tr, ctx) = world("down", "no");
    let log = c.join(".git/set-downs.jsonl");
    std::fs::write(
        &log,
        "{\"feature\": \"385-x\", \"utc\": \"2026-10-18T22:00:00Z\"}\nnot json\n",
    )
    .unwrap();
    assert!(said(&c, &tr, &ctx).is_some());
    std::fs::write(
        &log,
        "{\"feature\": \"999-y\", \"utc\": \"2026-10-19T00:00:00Z\"}\n",
    )
    .unwrap();
    assert!(said(&c, &tr, &ctx).is_some());
    std::fs::write(
        &log,
        "{\"feature\": \"385-x\", \"utc\": \"2026-10-18T23:00:00Z\"}\n",
    )
    .unwrap();
    assert_eq!(said(&c, &tr, &ctx), None);
    let (c2, tr2, ctx2) = world("closed", "yes");
    assert_eq!(said(&c2, &tr2, &ctx2), None);
}

#[test]
fn no_feature_begun_or_only_the_gms_box_passes() {
    let (c, tr, ctx) = world("none", "no");
    std::fs::write(
        c.join("specs/385-x/tasks.md"),
        "- [x] T02 done\n- [ ] GM review (make gm-reviewed F=385)\n",
    )
    .unwrap();
    assert_eq!(said(&c, &tr, &ctx), None);
    std::fs::write(c.join(".git/task-starts.jsonl"), "{\"utc\": \"x\"}\n").unwrap();
    assert_eq!(said(&c, &tr, &ctx), None);
    std::fs::remove_file(c.join(".git/task-starts.jsonl")).unwrap();
    assert_eq!(said(&c, &tr, &ctx), None);
    assert_eq!(verdict(&c, "/no/such/transcript", &ctx).unwrap(), None);
    assert_eq!(open_boxes(TASKS).len(), 2);
}

#[test]
fn a_read_error_lets_the_turn_end_recorded() {
    let (c, tr, ctx) = world("error", "no");
    std::fs::write(c.join("specs/385-x/tasks.md"), [0xff_u8, 0xfe]).unwrap();
    let e = Event {
        name: "Stop".to_owned(),
        input: json!({"cwd": c, "transcript_path": tr}),
    };
    let session = Session::from_input(&e.input);
    assert!(verdict(&c, "", &ctx).is_err());
    assert!(judge(&e, &session, &ctx, Some(c.to_string_lossy().into_owned())).is_empty());
    std::fs::write(c.join("specs/385-x/tasks.md"), TASKS).unwrap();
    std::fs::write(c.join(".git/task-starts.jsonl"), [0xff_u8]).unwrap();
    assert!(verdict(&c, "", &ctx).is_err());
    assert!(verdict(Path::new("/no/such/place"), "", &ctx).is_err());
    std::fs::write(c.join(".git/task-starts.jsonl"), START).unwrap();
    assert!(verdict(&c, "/proc/self/mem", &ctx).is_err());
}

#[test]
fn the_root_is_the_seam_else_the_work_tree() {
    let (c, tr, ctx) = world("root", "no");
    let at = c.to_string_lossy().into_owned();
    let run = |cwd: &str, seam: Option<String>| {
        let e = Event {
            name: "Stop".to_owned(),
            input: json!({"cwd": cwd, "transcript_path": tr}),
        };
        judge(&e, &Session::from_input(&e.input), &ctx, seam)
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
