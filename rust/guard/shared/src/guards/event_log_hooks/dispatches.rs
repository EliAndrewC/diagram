//! THE DISPATCHES A START CAME FROM (feature 451 T53): a subagent's FIRST `SubagentStart` fires before its meta file is written, so
//! T26's read of the brief found none and the line went to feature.json's feature, marked `fallback` - 15 lines of 451 builders and
//! reviews in 449's log, every one an agent's first start, written after T26 landed (observed 2026-11-21, method: the 449 log's
//! `SubagentStart` lines joined by `aid` to the subagents' meta files; the meta file of a running agent born 24 and 29 ms after its
//! start's line, measured 2026-11-21 (`stat %w` of two running agents' meta files against their `SubagentStart` `t`)).
//!
//! So the writer keeps, per session, a side file of the session's Agent calls - the call's `PreToolUse` (its id, its `subagent_type`,
//! its `description`) and its `PostToolUse` (the agent its launch returned) - at `<events dir>-dispatches/<sid>.jsonl`, outside the
//! events directory every reader lists. A start with no meta file is filed by:
//! - the call whose launch returned this agent, where that came first;
//! - else the session's calls of its type in the [`WINDOW_S`] before it whose launch has not returned, each brief read by the chain,
//!   taken only where they all agree (the caller's rule); a disagreement is feature.json's, marked, as before.
//!
//! The rule replayed over the clone's 4,527 first starts, each against every Agent `PreToolUse` of its session, the meta files'
//! `toolUseId` the truth (the replay over the logs):
//! - 0 to a wrong feature and 0 disagreeing at windows of 2, 5, 30 and 300 s, measured 2026-11-21 (the replay over the logs);
//! - all 156 starts marked `fallback` resolved right, measured 2026-11-21 (the replay over the logs);
//! - no candidate for 910 starts at 2 s and 284 at 300 s, measured 2026-11-21 (the replay over the logs).
//!
//! THE CORRECTIONS (feature 451 T106): a builder the coordinator re-numbers mid-task kept its brief's task on every line - T101's,
//! briefed `451 T100` and told "Your task is T101, not T100" 20 s into its run, filed all 230 of its lines under T100, its Write and
//! Edit lines of `speckit.rs`, `ready.rs` and `land-alone.sh` among them, so land-alone's list and the closing checks' split read them
//! as T100's (observed 2026-11-21, method: the 451 log's lines by `by` against the session transcript's `SendMessage` calls). So the side
//! directory also keeps, per agent, the task its later lines are filed under, at `<events dir>-dispatches/<sid>.tasks/<aid>` (one
//! task, the last said; a file a line, read by a missing-file open in the common case), written by [`record`] from what
//! `filed::renumbered` reads - the coordinator's correction, or the builder's own closing step - and read by `filed` ([`corrected`]).

use std::io::{Read as _, Seek as _, SeekFrom, Write as _};
use std::path::{Path, PathBuf};

use serde_json::{json, Value};

use super::text_of;

/// How far back a pending call counts. GUESS knob: 300 s, since a wider window found more starts their call and none wrong:
/// - 0 wrong and 0 disagreeing at 2, 5, 30 and 300 s over 4,527 first starts, measured 2026-11-21 (the replay over the logs, above);
/// - 910 starts with no candidate at 2 s and 284 at 300 s, measured 2026-11-21 (the same replay).
pub(super) const WINDOW_S: f64 = 300.0;
/// The side file's tail read at a start: 64 KiB, some 300 calls at ~200 bytes a call, against a window that held at most a few.
const TAIL: u64 = 64 * 1024;

/// Whether `name` is a plain file name: not empty, no separator, not hidden (a session or agent id).
pub(super) fn plain(name: &str) -> bool {
    !name.is_empty() && !name.contains(['/', '\\']) && !name.starts_with('.')
}

/// The session's side file beside `events`; none without a session id or one that is not a plain name.
fn path(events: &Path, sid: &str) -> Option<PathBuf> {
    if !plain(sid) {
        return None;
    }
    let name = events.file_name()?.to_string_lossy().into_owned();
    Some(
        events
            .with_file_name(format!("{name}-dispatches"))
            .join(format!("{sid}.jsonl")),
    )
}

/// Keep an Agent call's half on the session's side file, and an agent's correction in its task file (451 T106); anything else, or any
/// write that fails, is nothing (the hook never refuses).
pub(super) fn record(events: &Path, payload: &Value, t: &str) {
    if let Some((file, row)) = row(events, payload, t) {
        let _ = file.parent().map(std::fs::create_dir_all);
        let _ = std::fs::OpenOptions::new()
            .create(true)
            .append(true)
            .open(&file)
            .and_then(|mut f| f.write_all(format!("{row}\n").as_bytes()));
    }
    let sid = text_of(payload.get("session_id"));
    if let Some((file, task)) = super::filed::renumbered(payload, events)
        .and_then(|(aid, task)| Some((task_file(events, &sid, &aid)?, task)))
    {
        let _ = file.parent().map(std::fs::create_dir_all);
        let _ = std::fs::write(&file, format!("{task}\n"));
    }
}

/// The file holding the task agent `aid`'s later lines are filed under (451 T106); none for a session or agent id that is not a plain
/// name.
fn task_file(events: &Path, sid: &str, aid: &str) -> Option<PathBuf> {
    if !plain(aid) {
        return None;
    }
    Some(path(events, sid)?.with_extension("tasks").join(aid))
}

/// The task agent `aid`'s later lines are filed under, as the coordinator or its own closing step last said (451 T106); None where
/// nothing said, or the file holds no task.
pub(super) fn corrected(events: &Path, sid: &str, aid: &str) -> Option<String> {
    let text = std::fs::read_to_string(task_file(events, sid, aid)?).ok()?;
    let task = text.trim();
    super::filed::is_task(task).then(|| task.to_owned())
}

/// The side file and the row an Agent call's half keeps there: its `PreToolUse` the call, its `PostToolUse` the agent its launch
/// returned; None for any other payload, or one with no call id or session.
fn row(events: &Path, payload: &Value, t: &str) -> Option<(PathBuf, Value)> {
    let id = text_of(payload.get("tool_use_id"));
    if text_of(payload.get("tool_name")) != "Agent" || id.is_empty() {
        return None;
    }
    let file = path(events, &text_of(payload.get("session_id")))?;
    let input = |k: &str| text_of(payload.get("tool_input").and_then(|i| i.get(k)));
    let aid = text_of(payload.get("tool_response").and_then(|r| r.get("agentId")));
    let row = match text_of(payload.get("hook_event_name")).as_str() {
        "PreToolUse" => {
            let kind = Some(input("subagent_type")).filter(|k| !k.is_empty());
            json!({"t": t, "id": id, "type": kind.unwrap_or_else(|| "general-purpose".to_owned()), "brief": input("description")})
        }
        "PostToolUse" if !aid.is_empty() => json!({"t": t, "id": id, "aid": aid}),
        _ => return None,
    };
    Some((file, row))
}

/// The side file's last [`TAIL`] bytes as rows, a partial first line dropped; none where it cannot be read.
fn tail(file: &Path) -> Vec<Value> {
    let read = std::fs::File::open(file).and_then(|mut f| {
        let from = f.metadata()?.len().saturating_sub(TAIL);
        f.seek(SeekFrom::Start(from))?;
        let mut bytes = Vec::new();
        f.read_to_end(&mut bytes)?;
        Ok((from, bytes))
    });
    let Ok((from, bytes)) = read else {
        return Vec::new();
    };
    let text = String::from_utf8_lossy(&bytes);
    text.lines()
        .skip(usize::from(from > 0))
        .filter_map(|l| serde_json::from_str(l).ok())
        .collect()
}

/// Whether a call of `kind` can start an agent of `started`: the same type, or the review-round guard's twin (`spec-fidelity` routed to
/// `spec-fidelity-verify`).
fn compatible(kind: &str, started: &str) -> bool {
    kind == started || started.strip_suffix("-verify") == Some(kind)
}

/// The briefs a start with no meta file may have come from, at `now`: its returned call's alone, else every pending candidate's.
pub(super) fn briefs_at_start(events: &Path, payload: &Value, now: &str) -> Vec<String> {
    let aid = text_of(payload.get("agent_id"));
    let Some(file) = path(events, &text_of(payload.get("session_id"))) else {
        return Vec::new();
    };
    let Some(at) = crate::iso::parse(now) else {
        return Vec::new();
    };
    let rows = tail(&file);
    let returned = |r: &Value| !text_of(r.get("aid")).is_empty();
    let brief_of = |id: &str| {
        rows.iter()
            .find(|r| !returned(r) && text_of(r.get("id")) == id)
            .map(|r| text_of(r.get("brief")))
    };
    if let Some(own) = rows
        .iter()
        .rev()
        .find(|r| !aid.is_empty() && text_of(r.get("aid")) == aid)
        .and_then(|r| brief_of(&text_of(r.get("id"))))
    {
        return vec![own];
    }
    let started = text_of(payload.get("agent_type"));
    let done: Vec<String> = rows
        .iter()
        .filter(|r| returned(r))
        .map(|r| text_of(r.get("id")))
        .collect();
    rows.iter()
        .filter(|r| !returned(r) && !done.contains(&text_of(r.get("id"))))
        .filter(|r| compatible(&text_of(r.get("type")), &started))
        .filter(|r| {
            crate::iso::parse(&text_of(r.get("t"))).is_some_and(|t| t <= at && at - t <= WINDOW_S)
        })
        .map(|r| text_of(r.get("brief")))
        .collect()
}
