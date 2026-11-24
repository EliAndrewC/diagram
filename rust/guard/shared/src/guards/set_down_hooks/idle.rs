//! THE IDLE CHECK (451 T183): moved off the Stop, which blocked the session at each of its waits - split out
//! of `set_down_hooks.rs` past the file-scale bar.

use std::collections::{HashMap, HashSet};
use std::fs::File;
use std::path::{Path, PathBuf};
use std::time::{Duration, Instant};

use serde_json::Value;

use super::{judge, rows, stalls};
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
/// "a cron that fires every 5 minutes" (2026-11-23). It and [`WAIT_SECS`] are held under the hook entry's `timeout` in
/// `.claude/settings.json` (2,760 s: the two, and 60 s for the reads; 960 s before 451 T201).
pub(super) const IDLE_SECS: u64 = 300;

/// A Monitor's own cap, in seconds: its launch's result carries `"timeoutMs": 1800000` (all 214 Monitor launches in the transcripts
/// of 2026-11-22 and 23, measured by 451 T193), after which the harness ends the watch.
const MONITOR_SECS: u64 = 1_800;

/// How long past [`IDLE_SECS`] the idle check may go on looking, in seconds: `L7R_IDLE_WAIT_SECS`, a Monitor's cap and the bound
/// after it ([`MONITOR_SECS`] + [`stalls::STALL_SECS`], 451 T201; T193's was the bound alone, MODE 4 D12): a builder that goes quiet
/// as the session's last Stop is written crosses the bound within it, and so does one whose watch runs its full 30 minutes and ends
/// unheard, with no later Stop to arm another check. Live work that outlasts even this is handed on ([`watched`]): one short wake,
/// whose Stop arms the next check.
pub(super) const WAIT_SECS: u64 = MONITOR_SECS + stalls::STALL_SECS;

/// How often the idle check looks again while a builder's live work runs on, in seconds: `L7R_IDLE_RECHECK_SECS`, a GUESS of 60 (a
/// background shell's end reaches only its builder, so nothing tells the session; a minute's lateness beside a 600 s bound).
const RECHECK_SECS: u64 = 60;

/// What the idle check asks of the process table (451 T193): the guard's `finished_run_hooks` answers from `/proc`; [`idle_check`]
/// asks nothing of it, and keeps the Stop's list as given.
pub trait Procs {
    /// Each background task of session `session` some live process writes - its `<session>/tasks/<id>.output` on that process's
    /// stdout or stderr, which the harness's shell holds for its whole run (measured 2026-11-23 on a backgrounded `sleep`) - with
    /// those pids; None where the table cannot be read.
    fn writers(&self, session: &str) -> Option<HashMap<String, Vec<u32>>>;
    /// Each waiter on a dead producer (`finished_run_hooks`' `stale_waiters`, the Stop's own detector): its pid and the file it watches.
    fn stale(&self) -> Vec<(u32, String)>;
    /// The live processes whose command line holds `fragment` - a Monitor's, whose stream is a pipe and holds no file: the harness
    /// runs its command as `eval '<command>'`, its quotes rewritten (measured 2026-11-23 on a Monitor's `until grep` loop).
    fn running(&self, fragment: &str) -> Vec<u32>;
}

/// The process table unread.
pub(super) struct Blind;

impl Procs for Blind {
    fn writers(&self, _: &str) -> Option<HashMap<String, Vec<u32>>> {
        None
    }
    fn stale(&self) -> Vec<(u32, String)> {
        Vec::new()
    }
    fn running(&self, _: &str) -> Vec<u32> {
        Vec::new()
    }
}

/// The longest run of a command's text with no quote or backslash, the part the harness's `eval '...'` keeps as written; None where
/// it is shorter than [`FRAGMENT`] characters, too short to tell one command from another.
fn fragment(command: &str) -> Option<&str> {
    command
        .split(['\'', '"', '\\'])
        .map(str::trim)
        .max_by_key(|f| f.len())
        .filter(|f| f.len() >= FRAGMENT)
}

/// How long a command fragment must be to name its process (a CONVENTION: shorter, `sleep 60` alone names many).
const FRAGMENT: usize = 12;

/// THE IDLE CHECK (451 T183; the GM 2026-11-23: "something like a cron that fires every 5 minutes and does nothing and adds nothing to
/// the context if we are still active, and only injects data into the session if we are stopped"): `l7r-guard --idle-check`, the Stop
/// entry Claude Code runs with `asyncRewake` - in the background, waking the session only on exit 2, its stderr shown as a reminder
/// (hooks reference, "Run hooks in the background", read 2026-11-23; a cron's fire always submits a prompt, and a `Notification`
/// `idle_prompt` hook cannot inject, so neither can stay silent). Silent, at once, for a sub-agent's stop; else it waits [`IDLE_SECS`]
/// and is silent where the session's transcript gained a turn since (it was active; that turn's Stop arms the next). Then, where the
/// Stop's `background_tasks` was given, it RE-READS that list (451 T193, [`reread`]: a shell no process writes any more has ended, one
/// that waits on a dead producer is named) and names a STALLED builder (`stalls`) - once while its notice is unchanged, through any
/// hold - looking again until [`WAIT_SECS`] while one may still cross the bound; a list naming anything still running is waited on
/// (its end wakes the session, whose next Stop arms a check of its own); otherwise it says the set-down block - once while its text is
/// unchanged - unless a set-down or a ruling holds the work. The words to say, or None. The process table unread: [`idle_check_with`].
#[must_use]
pub fn idle_check(input: &Value) -> Option<String> {
    idle_check_with(input, &Blind)
}

/// [`idle_check`], the process table read through `procs`.
#[must_use]
pub fn idle_check_with(input: &Value, procs: &dyn Procs) -> Option<String> {
    if !field(input, "agent_id").is_empty() {
        return None;
    }
    let listed: Option<Vec<Value>> = input
        .get("background_tasks")
        .and_then(Value::as_array)
        .cloned();
    let transcript = Path::new(field(input, "transcript_path"));
    let start = std::fs::metadata(transcript).map_or(0, |m| m.len());
    let mut event = Event {
        name: "Stop".to_owned(),
        input: input.clone(),
    };
    let session = Session::from_input(input);
    if let (Some(listed), Some(root)) = (
        &listed,
        super::root_of(&event, &session, crate::env::opt("SET_DOWN_ROOT")),
    ) {
        keep_list(&root, field(input, "session_id"), listed);
    }
    let secs = secs_of("L7R_IDLE_CHECK_SECS", IDLE_SECS);
    if secs > 0 {
        std::thread::sleep(Duration::from_secs(secs));
    }
    if turned_since(transcript, start) {
        return None;
    }
    if let Some(listed) = listed {
        let now = match watched(&event, &session, (transcript, start), &listed, procs) {
            Watched::Turned => return None,
            Watched::Said(text) => return Some(text),
            Watched::Quiet(now) => now,
        };
        if !now.is_empty() {
            return None;
        }
        event.input["background_tasks"] = Value::Array(now);
    }
    // a Stop's answer is its refusal or none (`judge`)
    match judge(&event, &session, crate::env::opt("SET_DOWN_ROOT")).pop() {
        Some(Answer::Refuse(text)) => Some(text),
        _ => None,
    }
}

/// Where the session's last Stop list is kept for [`status`]: `<git common dir>/idle-listed/<session>.json`.
fn kept_list(root: &Path, session: &str) -> PathBuf {
    crate::guards::event_log_hooks::common_git_dir(root)
        .join("idle-listed")
        .join(format!("{session}.json"))
}

/// The Stop's list kept for [`status`], with when; a session with no id keeps none, and a write that fails is lost (the probe then
/// reads an older list, or none).
fn keep_list(root: &Path, session: &str, listed: &[Value]) {
    if session.is_empty() {
        return;
    }
    let file = kept_list(root, session);
    let _ = file.parent().map(std::fs::create_dir_all);
    let kept = serde_json::json!({"at": super::now() / 1_000_000, "background_tasks": listed});
    let _ = std::fs::write(file, kept.to_string());
}

/// THE STATUS PROBE (451 T193, MODE 4 D11; the task line: "the coordinator's status of a builder comes from that probe, never from its
/// last message"): `make builder-status`, each builder of an open task the session's transcript reads as running, said working or
/// stalled, and each dead-producer waiter, by the idle check's own reading - the list the session's last Stop gave (kept by
/// [`idle_check_with`]), re-read now ([`reread`]). Nothing is marked said. `input` names the transcript, the session and the clone.
#[must_use]
pub fn status(input: &Value, procs: &dyn Procs) -> String {
    let event = Event {
        name: "Stop".to_owned(),
        input: input.clone(),
    };
    let session = Session::from_input(input);
    let Some(root) = super::root_of(&event, &session, crate::env::opt("SET_DOWN_ROOT")) else {
        return "builder-status: no clone to read the open tasks from".to_owned();
    };
    let sid = field(input, "session_id");
    let Some(kept) = std::fs::read_to_string(kept_list(&root, sid))
        .ok()
        .and_then(|t| serde_json::from_str::<Value>(&t).ok())
    else {
        return format!("builder-status: session {sid} has no Stop list kept yet (the idle check keeps one at each Stop)");
    };
    let listed = kept["background_tasks"]
        .as_array()
        .cloned()
        .unwrap_or_default();
    let (now_listed, waiters) = reread(&listed, sid, procs);
    let live: HashSet<String> = now_listed
        .iter()
        .map(|r| field(r, "id").to_owned())
        .collect();
    let bound = secs_of("L7R_STALL_SECS", stalls::STALL_SECS);
    let found = stalls::stalled(
        Path::new(field(input, "transcript_path")),
        &root,
        &live,
        Duration::from_secs(bound),
    );
    let mut lines = vec![format!(
        "builder-status: the Stop list of {} UTC, re-read now; stalled = silent over {bound} s, nothing live.",
        crate::once::hhmm(kept["at"].as_i64().unwrap_or(0))
    )];
    lines.extend(found.working);
    lines.extend(found.stalls.iter().map(stalls::Stall::line));
    lines.extend(waiters.iter().map(Waiter::line));
    if lines.len() == 1 {
        lines.push("No builder of an open task reads as running.".to_owned());
    }
    lines.join("\n")
}

/// A knob's seconds: `name` from the environment, else `default`.
fn secs_of(name: &str, default: u64) -> u64 {
    crate::env::opt(name)
        .and_then(|v| v.trim().parse().ok())
        .unwrap_or(default)
}

/// A listed shell that waits on a dead producer (451 T193, the gap audit's item 1: a page session's runner that dies never writes
/// `ALL DONE`, so the wait it printed spins for good).
struct Waiter {
    id: String,
    pid: u32,
    file: String,
}

impl Waiter {
    fn line(&self) -> String {
        format!(
            "- task {} (pid {}) waits on {}, which nothing writes any more: read what it holds, then TaskStop {}.",
            self.id, self.pid, self.file, self.id
        )
    }
}

/// The Stop's list as it stands now (451 T193, MODE 4 D12 and the gap audit's item 2: the list is the Stop's, read before the wait):
/// a `shell` or `monitor` no live process writes, and none runs by its command line (a Monitor, listed as a shell, whose stream holds
/// no file, measured 2026-11-23), has ended, and one whose process waits on a dead producer is no live work but a [`Waiter`]; every other
/// entry - a sub-agent (its turn's end is a notice to the session, which silences the check), a shell whose command is too short to
/// tell, or any entry where the table cannot be read - is kept as the Stop listed it, failing toward silence.
fn reread(listed: &[Value], session: &str, procs: &dyn Procs) -> (Vec<Value>, Vec<Waiter>) {
    let Some(held) = procs.writers(session) else {
        return (listed.to_vec(), Vec::new());
    };
    let stale = procs.stale();
    let mut waiters = Vec::new();
    let mut kept = Vec::new();
    for entry in listed {
        let id = field(entry, "id");
        if !matches!(field(entry, "type"), "shell" | "monitor") {
            kept.push(entry.clone());
            continue;
        }
        // a Monitor is listed as a `shell` too (bx5gtybg3, T184's watch, measured 2026-11-23 in 451's event log), its stream a pipe:
        // read by its command line; a command too short to tell keeps the entry, failing toward silence
        let pids = match held.get(id) {
            Some(pids) => pids.clone(),
            None => match fragment(field(entry, "command")) {
                None => {
                    kept.push(entry.clone());
                    continue;
                }
                Some(text) => procs.running(text),
            },
        };
        if pids.is_empty() {
            continue; // ended
        }
        match stale.iter().find(|(p, _)| pids.contains(p)) {
            Some((pid, file)) => waiters.push(Waiter {
                id: id.to_owned(),
                pid: *pid,
                file: file.clone(),
            }),
            None => kept.push(entry.clone()),
        }
    }
    (kept, waiters)
}

/// What [`watched`] ended on.
enum Watched {
    /// The session took a turn while it waited.
    Turned,
    /// The notice to say.
    Said(String),
    /// Nothing to name: the list as it stands now.
    Quiet(Vec<Value>),
}

/// The stalled builders and dead-producer waiters, named (451 T193): each said once while its line is unchanged, in the session's
/// said-once record (`once`, the set-down block's own) under its own key, so one stalled a day ago is not said again beside a new
/// one. The list is re-read ([`reread`]) at each look, and while a builder still within the bound (`L7R_STALL_SECS`, else
/// [`stalls::STALL_SECS`]) may cross it, or a builder's live work may end, it looks again - at the crossing, or each
/// [`RECHECK_SECS`] - until [`WAIT_SECS`] have passed (MODE 4 D12: when the builder is the last thing running, no later Stop arms
/// another check); the session's own turn silences it.
fn watched(
    event: &Event,
    session: &Session,
    (transcript, start): (&Path, u64),
    listed: &[Value],
    procs: &dyn Procs,
) -> Watched {
    let who = field(&event.input, "session_id");
    let Some(root) = super::root_of(event, session, crate::env::opt("SET_DOWN_ROOT")) else {
        return Watched::Quiet(reread(listed, who, procs).0);
    };
    let bound = secs_of("L7R_STALL_SECS", stalls::STALL_SECS);
    let bound_for = Duration::from_secs(bound);
    let recheck = Duration::from_secs(secs_of("L7R_IDLE_RECHECK_SECS", RECHECK_SECS));
    let deadline = Instant::now() + Duration::from_secs(secs_of("L7R_IDLE_WAIT_SECS", WAIT_SECS));
    let said = crate::once::file(
        &crate::guards::event_log_hooks::common_git_dir(&root),
        &event.input,
    );
    loop {
        let (now_listed, waiters) = reread(listed, who, procs);
        let live: HashSet<String> = now_listed
            .iter()
            .map(|r| field(r, "id").to_owned())
            .collect();
        let found = stalls::stalled(transcript, &root, &live, bound_for);
        let now = super::now() / 1_000_000;
        let fresh = |pairs: Vec<(String, String)>| -> Vec<String> {
            pairs
                .into_iter()
                .filter(|(key, line)| {
                    crate::once::repeat(said.as_deref(), key, line, now).is_none()
                })
                .map(|(_, line)| line)
                .collect()
        };
        let waiting = fresh(
            waiters
                .iter()
                .map(|w| (format!("waiter {}", w.id), w.line()))
                .collect(),
        );
        let stalled = fresh(
            found
                .stalls
                .iter()
                .map(|s| (format!("stalled {}", s.id), s.line()))
                .collect(),
        );
        if let Some(text) = notice(&waiting, &stalled, bound) {
            crate::log::fire(
                "set-down",
                "reminded",
                "idle: stalled agent",
                "stalled-agent",
                &event.input,
                session,
            );
            return Watched::Said(text);
        }
        let next = [
            found.soonest.map(|left| left + Duration::from_secs(1)),
            found.watched.then_some(recheck),
        ]
        .into_iter()
        .flatten()
        .min();
        let Some(next) = next.filter(|n| Instant::now() + *n <= deadline) else {
            // LIVE WORK OUTLASTING THE WAIT IS HANDED ON (451 T201): the check wakes the session only by its own exit, held under the
            // hook's `timeout`, so a builder's run or child still live at the deadline would be named only at a later Stop, and with
            // none, never. One short wake, said every time (each is a check of its own, not a repeat), whose Stop arms the next check
            if found.watched {
                crate::log::fire(
                    "set-down",
                    "reminded",
                    "idle: handed on",
                    "idle-handed-on",
                    &event.input,
                    session,
                );
                return Watched::Said(handed_on(&found.working));
            }
            return Watched::Quiet(now_listed);
        };
        std::thread::sleep(next);
        if turned_since(transcript, start) {
            return Watched::Turned;
        }
    }
}

/// The hand-on notice (451 T201): the builders still at work when the idle check's wait ran out, each its status line.
fn handed_on(working: &[String]) -> String {
    let names: Vec<&str> = working
        .iter()
        .map(|l| {
            l.split_once(": working")
                .map_or(l.as_str(), |(name, _)| name)
        })
        .collect();
    format!(
        "IDLE CHECK: {} builder(s) still working past its wait. End the turn; the next Stop re-arms the check.\n{}",
        working.len(),
        names.join("\n")
    )
}

/// The notice: its waiters' section, then its stalled builders', or None where both are empty.
fn notice(waiting: &[String], stalled: &[String], bound: u64) -> Option<String> {
    let mut parts = Vec::new();
    if !waiting.is_empty() {
        parts.push(format!(
            "A WAITER IS SPINNING ON A DEAD PRODUCER - {} will never finish:\n{}",
            waiting.len(),
            waiting.join("\n")
        ));
    }
    if !stalled.is_empty() {
        parts.push(format!(
            "STALLED: {} builder(s) read as running have no live work (transcripts silent >{bound} s), so no notice will wake them:\n{}",
            stalled.len(),
            stalled.join("\n")
        ));
    }
    (!parts.is_empty()).then(|| parts.join("\n"))
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
