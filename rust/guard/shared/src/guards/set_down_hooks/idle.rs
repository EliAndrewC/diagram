//! THE IDLE CHECK (451 T183): moved off the Stop, which blocked the session at each of its waits - split out
//! of `set_down_hooks.rs` past the file-scale bar.

use std::fs::File;
use std::path::{Path, PathBuf};

use serde_json::Value;

use super::{judge, rows};
use crate::protocol::{Answer, Event};
use crate::session::Session;
use crate::state::field;
use crate::tool::ask;

/// The clone's git common dir and its last `make task-start`'s feature and time, or None where it has none; an Err where git cannot
/// name the dir or the start log cannot be read.
pub(super) fn last_start(root: &Path) -> Result<Option<(PathBuf, String, String)>, String> {
    let at = root.to_string_lossy();
    let said = ask(
        Path::new("/"),
        "git",
        &[
            "-C",
            &at,
            "rev-parse",
            "--path-format=absolute",
            "--git-common-dir",
        ],
        "",
    );
    if !said.ok() {
        return Err(said.err);
    }
    let git_dir = PathBuf::from(said.out.trim());
    let starts = rows(&git_dir.join("task-starts.jsonl"))?;
    Ok(starts.last().map(|last| {
        let (feature, since) = (field(last, "feature"), field(last, "utc"));
        (git_dir.clone(), feature.to_owned(), since.to_owned())
    }))
}

/// How long the idle check waits after a Stop before it looks again, in seconds: `L7R_IDLE_CHECK_SECS`, a GUESS of 300 - the GM's
/// "a cron that fires every 5 minutes" (2026-11-23) - held under the hook entry's timeout in `.claude/settings.json`.
const IDLE_SECS: u64 = 300;

/// THE IDLE CHECK (451 T183; the GM 2026-11-23: "something like a cron that fires every 5 minutes and does nothing and adds nothing to
/// the context if we are still active, and only injects data into the session if we are stopped"): `l7r-guard --idle-check`, the Stop
/// entry Claude Code runs with `asyncRewake` - in the background, waking the session only on exit 2, its stderr shown as a reminder
/// (hooks reference, "Run hooks in the background", read 2026-11-23; a cron's fire always submits a prompt, and a `Notification`
/// `idle_prompt` hook cannot inject, so neither can stay silent). Silent, at once, for a sub-agent's stop or a Stop whose
/// `background_tasks` names anything running (its end wakes the session, whose next Stop arms a check of its own); else it waits
/// [`IDLE_SECS`] and is silent where the session's transcript gained a turn since (it was active; that turn's Stop arms the next), and
/// otherwise says the set-down block - once while its text is unchanged - unless a set-down or a ruling holds the work. The words to
/// say, or None.
#[must_use]
pub fn idle_check(input: &Value) -> Option<String> {
    if !field(input, "agent_id").is_empty()
        || input
            .get("background_tasks")
            .and_then(Value::as_array)
            .is_some_and(|t| !t.is_empty())
    {
        return None;
    }
    let transcript = Path::new(field(input, "transcript_path"));
    let start = std::fs::metadata(transcript).map_or(0, |m| m.len());
    let secs = crate::env::opt("L7R_IDLE_CHECK_SECS")
        .and_then(|v| v.trim().parse().ok())
        .unwrap_or(IDLE_SECS);
    if secs > 0 {
        std::thread::sleep(std::time::Duration::from_secs(secs));
    }
    if turned_since(transcript, start) {
        return None;
    }
    let event = Event {
        name: "Stop".to_owned(),
        input: input.clone(),
    };
    let session = Session::from_input(input);
    // a Stop's answer is its refusal or none (`judge`)
    match judge(&event, &session, crate::env::opt("SET_DOWN_ROOT")).pop() {
        Some(Answer::Refuse(text)) => Some(text),
        _ => None,
    }
}

/// Whether the transcript gained a prompt, a notice or a reply past byte `start` - a record whose own `type` is `user` or
/// `assistant` (the harness's `system` records of a turn's end, written after its Stop hooks, are none).
pub(super) fn turned_since(transcript: &Path, start: u64) -> bool {
    use std::io::{Read as _, Seek as _, SeekFrom};
    let Ok(mut file) = File::open(transcript) else {
        return false;
    };
    let mut tail = String::new();
    if file.seek(SeekFrom::Start(start)).is_err() || file.read_to_string(&mut tail).is_err() {
        return false;
    }
    tail.lines().any(|line| {
        serde_json::from_str::<Value>(line)
            .is_ok_and(|r| matches!(field(&r, "type"), "user" | "assistant"))
    })
}
