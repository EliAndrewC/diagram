//! Feature 451 T07 (FR-004, plan D6): an agent's cost and task in the log - `task` on its Agent dispatch line from the description, else
//! the prompt's first line; `tok` (`in`, `cached`, `created`, `out`, each `message.id` once), `ctx` (its last call's context) and `task`
//! (its meta file's description) on each `SubagentStop` line.

use std::path::Path;

use serde_json::{json, Value};

use super::super::append;
use super::{clone, last_line, none, session_files};

/// One assistant row of model call `id`: `input`, `read`, `write` and `out` its usage.
fn call(id: &str, input: u64, read: u64, write: u64, out: u64) -> String {
    json!({"type": "assistant", "requestId": format!("req-{id}"), "message": {"id": id, "role": "assistant",
        "usage": {"input_tokens": input, "cache_read_input_tokens": read, "cache_creation_input_tokens": write, "output_tokens": out}}})
    .to_string()
}

/// The agent's reply: model call `id`'s last row, its content one `text` block.
fn reply(id: &str, input: u64, read: u64, write: u64, out: u64, text: &str) -> String {
    let mut row: Value = serde_json::from_str(&call(id, input, read, write, out)).unwrap();
    row["message"]["content"] = json!([{"type": "text", "text": text}]);
    row.to_string()
}

fn write_transcript(d: &Path, aid: &str, rows: &[String]) -> String {
    let p = d.join(format!("projects/s1/subagents/agent-{aid}.jsonl"));
    std::fs::create_dir_all(p.parent().unwrap()).unwrap();
    std::fs::write(&p, rows.join("\n") + "\n").unwrap();
    p.to_string_lossy().into_owned()
}

/// A stop naming no reply (`last_assistant_message`), so it waits for none: the reply's own tests name one.
fn stop(cwd: &str, session: &str, aid: &str) -> Value {
    json!({"hook_event_name": "SubagentStop", "cwd": cwd, "transcript_path": session, "agent_id": aid,
        "agent_type": "general-purpose"})
}

/// A stop waits for its agent's reply to reach the transcript (451 T59): Claude Code writes a transcript's rows on a timer, so the
/// reply's row is often not yet on disk when `SubagentStop` fires, and lands while the hook runs. Here it lands 60 ms in, the probe's
/// middle (5.8-89.2 ms).
#[test]
fn a_stop_waits_for_its_agents_reply_to_reach_the_transcript() {
    use std::io::Write as _;
    let d = clone("cost-reply");
    let cwd = d.to_string_lossy().into_owned();
    let session = session_files(
        &d,
        "late",
        r#"{"agentType":"general-purpose","description":"T59: the reply","toolUseId":"tu"}"#,
    );
    let own = write_transcript(&d, "late", &[call("m1", 3, 1000, 200, 10)]);
    let mut p = stop(&cwd, &session, "late");
    p["agent_transcript_path"] = json!(own);
    p["last_assistant_message"] = json!("DONE-1");
    let writer = std::thread::spawn(move || {
        std::thread::sleep(std::time::Duration::from_millis(60));
        let mut f = std::fs::OpenOptions::new().append(true).open(&own).unwrap();
        writeln!(f, "{}", reply("m2", 2, 1500, 100, 7, "DONE-1")).unwrap();
    });
    let row = last_line(&append(&p, "T", &d, &none).unwrap());
    writer.join().unwrap();
    assert_eq!(
        row["tok"],
        json!({"in": 5, "cached": 2500, "created": 300, "out": 17})
    );
    assert_eq!(row["ctx"], json!(1602));
}

/// The wait's edges (451 T59): a reply already on disk is not waited for, nor one that ends a longer last message (several blocks'
/// text joined); a reply before the last `user` row answers an earlier prompt, so it is waited for, and a reply that never lands is
/// waited for no longer than the bound, writing what is on disk. A tool's result longer than the reader's chunk is one row.
#[test]
fn a_stop_waits_only_for_a_reply_not_yet_on_disk() {
    use super::super::fields::agent_cost_within;
    use std::time::{Duration, Instant};
    let d = clone("cost-wait");
    let user = json!({"type": "user", "message": {"role": "user", "content": "again"}}).to_string();
    let result =
        json!({"type": "user", "message": {"role": "user", "content": "x".repeat(200_000)}})
            .to_string();
    let cost = |aid: &str, rows: &[String], said: &str, wait: Duration| {
        let own = write_transcript(&d, aid, rows);
        let p = json!({"agent_transcript_path": own, "last_assistant_message": said});
        let mut out = serde_json::Map::new();
        let start = Instant::now();
        agent_cost_within(&mut out, &p, wait);
        (out["tok"]["out"].clone(), start.elapsed())
    };
    let long = Duration::from_secs(30);
    let (out, took) = cost(
        "ondisk",
        &[
            call("m1", 1, 2, 3, 4),
            result,
            reply("m2", 1, 2, 3, 5, "CLEAR"),
        ],
        " CLEAR\n",
        long,
    );
    assert_eq!((out, took < long / 3), (json!(9), true));
    let (out, took) = cost(
        "joined",
        &[reply("m1", 1, 2, 3, 4, "part two")],
        "part one\n\npart two",
        long,
    );
    assert_eq!((out, took < long / 3), (json!(4), true));
    let short = Duration::from_millis(40);
    for (aid, rows) in [
        (
            "earlier",
            vec![reply("m1", 1, 2, 3, 4, "CLEAR"), user.clone()],
        ),
        ("never", vec![call("m1", 1, 2, 3, 4)]),
    ] {
        let (out, took) = cost(aid, &rows, "CLEAR", short);
        assert_eq!((out, took >= short), (json!(4), true), "{aid}");
    }
}

/// A stop's `tok`, `ctx` and `task`: one model call split across three rows (a streamed reply, its last row the whole output) is
/// counted once; a user row carrying usage (an Agent call's result) and a row that is no JSON are no call; the context is the last
/// call's.
#[test]
fn a_stop_carries_its_agents_tokens_context_and_task() {
    let d = clone("cost");
    let cwd = d.to_string_lossy().into_owned();
    let session = session_files(
        &d,
        "ab1",
        r#"{"agentType":"general-purpose","description":"T202: rebuild the placer","toolUseId":"tu"}"#,
    );
    let rows = [
        call("m1", 3, 1000, 200, 10),
        call("m1", 3, 1000, 200, 10),
        call("m1", 3, 1000, 200, 40),
        json!({"type": "user", "message": {"role": "user", "content": "x"}, "toolUseResult": {"usage": {"input_tokens": 9}}})
            .to_string(),
        "not json".to_owned(),
        call("m2", 2, 1500, 100, 7),
        // a synthetic message: no model call, so neither its tokens nor the context
        call("m3", 0, 0, 0, 0),
    ];
    let own = write_transcript(&d, "ab1", &rows);
    let mut p = stop(&cwd, &session, "ab1");
    p["agent_transcript_path"] = json!(own);
    let row = last_line(&append(&p, "T", &d, &none).unwrap());
    assert_eq!(
        row["tok"],
        json!({"in": 5, "cached": 2500, "created": 300, "out": 47})
    );
    assert_eq!(row["ctx"], json!(1602));
    assert_eq!(row["task"], json!("T202"));
    // no `agent_transcript_path`: the agent's own transcript beside the session's
    let row = last_line(&append(&stop(&cwd, &session, "ab1"), "T", &d, &none).unwrap());
    assert_eq!(row["tok"]["out"], json!(47));
}

/// A builder with no meta file still has its cost; a stop whose transcript is missing or holds no call writes neither field; a
/// `SubagentStart` and a main-session `Stop` carry none.
#[test]
fn a_stop_with_no_meta_or_no_transcript() {
    let d = clone("cost-none");
    let cwd = d.to_string_lossy().into_owned();
    let session = d.join("projects/s1.jsonl").to_string_lossy().into_owned();
    // two rows naming no `message.id`: nothing ties them to one call, so each is its own
    write_transcript(&d, "nometa", &[call("", 1, 2, 3, 4), call("", 1, 2, 3, 4)]);
    let row = last_line(&append(&stop(&cwd, &session, "nometa"), "T", &d, &none).unwrap());
    assert_eq!(
        row["tok"],
        json!({"in": 2, "cached": 4, "created": 6, "out": 8})
    );
    assert_eq!(row["ctx"], json!(6));
    assert!(row.get("task").is_none(), "{row}");
    write_transcript(&d, "empty", &["{\"type\": \"user\"}".to_owned()]);
    for aid in ["missing", "empty"] {
        let row = last_line(&append(&stop(&cwd, &session, aid), "T", &d, &none).unwrap());
        assert!(
            row.get("tok").is_none() && row.get("ctx").is_none(),
            "{aid}: {row}"
        );
    }
    let mut start = stop(&cwd, &session, "nometa");
    start["hook_event_name"] = json!("SubagentStart");
    let row = last_line(&append(&start, "T", &d, &none).unwrap());
    assert!(row.get("tok").is_none(), "{row}");
    let mut bare = stop(&cwd, &session, "nometa");
    bare.as_object_mut().unwrap().remove("transcript_path");
    let row = last_line(&append(&bare, "T", &d, &none).unwrap());
    assert!(row.get("tok").is_none(), "{row}");
}

/// The dispatch's task: its description's `T<n>`, else its prompt's first line's - never a later line's, which quotes other tasks.
#[test]
fn a_dispatch_carries_its_briefs_task() {
    let d = clone("dispatch");
    let cwd = d.to_string_lossy().into_owned();
    let task = |description: &str, prompt: &str| {
        let p = json!({"hook_event_name": "PreToolUse", "cwd": cwd, "tool_name": "Agent",
            "tool_input": {"description": description, "prompt": prompt}});
        last_line(&append(&p, "T", &d, &none).unwrap())
            .get("task")
            .cloned()
    };
    assert_eq!(
        task("T08: the readers", "Feature 451 task T09"),
        Some(json!("T08"))
    );
    assert_eq!(
        task(
            "the readers",
            "Feature 451 task T07, in the clone\nT33 is another's"
        ),
        Some(json!("T07"))
    );
    assert_eq!(task("the readers", "no task here\nT33 is another's"), None);
}
