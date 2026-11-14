//! The watch beside each session (`page_session_runner.py`'s `StallWatch` and the transcript readings it rests on, ported by feature 449
//! T137).
//!
//! A HEADLESS SESSION THAT HAS GONE QUIET IS RESUMED (feature 295 item 3). `claude -p` is never re-invoked by background work - a
//! backgrounded Bash, a detached make, a background agent (feature 293's measurement) - so a session that ends its turn to wait for its
//! own check agents sits until somebody kills it: R12's check session idled about two and a half hours on 2026-09-30 after all five of its
//! re-checks had returned. Killing it and resuming the same session (`--resume`) is what got it moving that day, and the runner already
//! knows how to resume. So each session runs beside a watch that reads its transcript and every subagent transcript of it; silence past
//! [`STALL_AFTER`], with the process alive, ends the process, and the loop resumes the session at once.
//!
//! `STALL_AFTER` IS 15 MINUTES because the longest silence a WORKING session shows is one foreground tool call, and the Bash tool's own
//! ceiling is 10 minutes (research R3); 15 is past any legitimate silence and costs at most 16 minutes against the 2.5 hours measured.
//! [`STALL_RESUMES`] caps the resumes so a session that stalls every time it is resumed does not hold the queue for good: eight resumes is
//! two hours of quiet at the outside.
//!
//! ...AND HANDED WHAT ITS AGENTS RETURNED (feature 317, 2026-10-03). The agents' reports reach a headless session's transcript only as
//! QUEUED notifications (`queue-operation` / `enqueue`) that its process never takes up, and a resumed session is told by Claude Code that
//! its "background agents didn't finish before the previous session ended" - so feature 317's R1 check session, whose eight checks had
//! all returned within two minutes of its turn's end, was resumed fifteen minutes later, dispatched all eight again, ended its turn and
//! sat again. So the resume names a file holding every report queued since the session last took one up ([`undelivered`]), and a session
//! whose turn has ended with reports waiting is resumed after [`RETURNED_AFTER`] of quiet rather than `STALL_AFTER`: its agents' writes
//! count as activity, so five quiet minutes is every agent finished or stuck, and a session still in a tool call (its last turn not
//! ended) is left alone.
//!
//! The transcripts are read line by line as the Python's `_entries` read them (a line that is no JSON object skipped), not through the
//! guard's event-log reader, which keeps only the fields the measure chain reads.

use std::path::{Path, PathBuf};
use std::sync::mpsc;
use std::time::{Duration, SystemTime};

use l7r_guard::shared::pyjson::py_str;
use serde_json::Value;

use super::retry::truthy;
use crate::{py_join, read_lossy};

pub const STALL_AFTER: f64 = 15.0 * 60.0;
pub const STALL_CHECK: f64 = 60.0;
pub const STALL_RESUMES: u32 = 8;
pub const RETURNED_AFTER: f64 = 5.0 * 60.0;

/// The watch's three intervals and the retry's cap on one sleep, in seconds: the constants in a queue, shorter in a test.
#[derive(Clone, Copy, Debug)]
pub struct Times {
    pub check: f64,
    pub after: f64,
    pub returned: f64,
    pub retry_every: f64,
}

impl Times {
    /// A queue's own.
    #[must_use]
    pub fn standing() -> Self {
        Self {
            check: STALL_CHECK,
            after: STALL_AFTER,
            returned: RETURNED_AFTER,
            retry_every: super::retry::RETRY_EVERY,
        }
    }
}

/// Seconds since the epoch, as `time.time()`.
pub(crate) fn now() -> f64 {
    SystemTime::now()
        .duration_since(SystemTime::UNIX_EPOCH)
        .unwrap_or_default()
        .as_secs_f64()
}

/// Each line of a transcript that is a JSON object.
fn entries(path: &str) -> Vec<serde_json::Map<String, Value>> {
    l7r_guard::shared::speckit::splitlines(&read_lossy(Path::new(path)))
        .iter()
        .filter_map(|l| serde_json::from_str::<Value>(l).ok())
        .filter_map(|v| match v {
            Value::Object(o) => Some(o),
            _ => None,
        })
        .collect()
}

fn transcript(projects: &str, sid: &str) -> String {
    py_join(projects, &format!("{sid}.jsonl"))
}

fn is(row: &serde_json::Map<String, Value>, key: &str, value: &str) -> bool {
    row.get(key).and_then(Value::as_str) == Some(value)
}

/// The task notifications queued in the session's transcript since it last took one up (each `enqueue` after the last `dequeue`) - the
/// agents' reports a headless process never read.
#[must_use]
pub fn undelivered(projects: &str, sid: &str) -> Vec<String> {
    let rows: Vec<_> = entries(&transcript(projects, sid))
        .into_iter()
        .filter(|r| is(r, "type", "queue-operation"))
        .collect();
    let last = rows.iter().rposition(|r| is(r, "operation", "dequeue"));
    rows[last.map_or(0, |i| i + 1)..]
        .iter()
        .filter(|r| is(r, "operation", "enqueue"))
        .filter_map(|r| {
            let content = r.get("content");
            let shown = if truthy(content) {
                content.map(py_str)
            } else {
                None
            };
            shown.filter(|s| s.contains("<task-notification>"))
        })
        .collect()
}

/// Has the session's last turn ended (its last assistant entry stopped at `end_turn`, not at a tool call it is running)? `None` where
/// that entry's `message` is a value no `.get` reads, the Python's `AttributeError`, which ended its watch's thread.
#[must_use]
pub fn turn_ended(projects: &str, sid: &str) -> Option<bool> {
    let rows = entries(&transcript(projects, sid));
    let Some(last) = rows.iter().rev().find(|r| is(r, "type", "assistant")) else {
        return Some(false);
    };
    match last.get("message") {
        Some(Value::Object(m)) => {
            Some(m.get("stop_reason").and_then(Value::as_str) == Some("end_turn"))
        }
        other if truthy(other) => None,
        _ => Some(false),
    }
}

/// Write the reports a resume hands its session to `<log>/returned.md`; None, and nothing written, when there are none.
///
/// # Errors
///
/// What the write raised.
pub fn returned_file(log: &str, reports: &[String]) -> Result<Option<String>, String> {
    if reports.is_empty() {
        return Ok(None);
    }
    let path = py_join(log, "returned.md");
    std::fs::write(&path, format!("{}\n", reports.join("\n\n")))
        .map_err(|e| format!("{path}: {e}"))?;
    Ok(Some(path))
}

/// Where Claude Code writes the transcripts of a session started in `root` - as `page-session.sh` computes it.
#[must_use]
pub fn projects_dir(root: &str, home: &str) -> String {
    let home = home.trim_end_matches('/');
    let home = if home.is_empty() { "/" } else { home };
    let mangled: String = root
        .chars()
        .map(|c| if c == '/' || c == '.' { '-' } else { c })
        .collect();
    py_join(&py_join(&py_join(home, ".claude"), "projects"), &mangled)
}

fn mtime(path: &Path) -> Option<f64> {
    std::fs::metadata(path)
        .and_then(|m| m.modified())
        .ok()
        .and_then(|t| t.duration_since(SystemTime::UNIX_EPOCH).ok())
        .map(|d| d.as_secs_f64())
}

/// The newest write to the session's transcript or any of its subagents' transcripts, or None before the first.
#[must_use]
pub fn last_activity(projects: &str, sid: &str) -> Option<f64> {
    let subagents = PathBuf::from(py_join(&py_join(projects, sid), "subagents"));
    let mut paths = vec![PathBuf::from(transcript(projects, sid))];
    if let Ok(found) = std::fs::read_dir(&subagents) {
        paths.extend(found.filter_map(Result::ok).map(|e| e.path()).filter(|p| {
            let n = l7r_guard::shared::speckit::py_name(p);
            !n.starts_with('.') && p.extension().is_some_and(|x| x == "jsonl")
        }));
    }
    paths.iter().filter_map(|p| mtime(p)).reduce(f64::max)
}

/// The live `claude` processes running session `sid` - read from `proc` by argument, never by a pattern search.
#[must_use]
pub fn session_pids(sid: &str, proc: &Path) -> Vec<i32> {
    let Ok(found) = std::fs::read_dir(proc) else {
        return Vec::new();
    };
    found
        .filter_map(Result::ok)
        .filter_map(|e| {
            let name = e.file_name().to_string_lossy().into_owned();
            let pid: i32 = name
                .starts_with(|c: char| c.is_ascii_digit())
                .then(|| name.parse().ok())??;
            let argv = std::fs::read(e.path().join("cmdline")).ok()?;
            let words: Vec<String> = argv
                .split(|b| *b == 0)
                .map(|a| String::from_utf8_lossy(a).into_owned())
                .collect();
            let ours = crate::basename(&words[0]) == "claude"
                && words.iter().any(|a| a == sid)
                && words.iter().any(|a| a == "--session-id" || a == "--resume");
            ours.then_some(pid)
        })
        .collect()
}

extern "C" {
    fn kill(pid: i32, sig: i32) -> i32;
}

/// `os.kill(pid, SIGTERM)`, a failure ignored (the process gone already). The crate's one signal; std has no safe form of `kill(2)`.
pub(crate) fn terminate(pid: i32) {
    // SAFETY: kill(2) with a positive pid signals that one process and touches no memory of this one
    unsafe {
        kill(pid, 15);
    }
}

/// A watch started beside one session: stopped by [`Watch::stop`], which says whether it stalled and how long it was quiet.
pub struct Watch {
    halt: mpsc::Sender<()>,
    thread: std::thread::JoinHandle<(bool, u64)>,
}

impl Watch {
    /// Every `times.check` seconds, the silence since the session's last transcript write or since the watch began, whichever is later;
    /// past `times.after` (or `times.returned`, its turn ended with reports waiting) it ends the session's processes in `proc`.
    #[must_use]
    pub fn start(projects: String, sid: String, times: Times, proc: PathBuf) -> Self {
        let (halt, wait) = mpsc::channel::<()>();
        let thread = std::thread::spawn(move || watch(&projects, &sid, times, &proc, &wait));
        Self { halt, thread }
    }

    /// The watch halted: (it stalled, the quiet it saw in whole seconds).
    #[must_use]
    pub fn stop(self) -> (bool, u64) {
        let _ = self.halt.send(());
        self.thread.join().unwrap_or((false, 0))
    }
}

#[allow(
    clippy::cast_possible_truncation,
    clippy::cast_sign_loss,
    reason = "the quiet in whole seconds, as the Python's int() of it"
)]
fn watch(
    projects: &str,
    sid: &str,
    times: Times,
    proc: &Path,
    wait: &mpsc::Receiver<()>,
) -> (bool, u64) {
    let began = now();
    while wait.recv_timeout(Duration::from_secs_f64(times.check))
        == Err(mpsc::RecvTimeoutError::Timeout)
    {
        // never before the watch began: a RESUMED session's transcript is as old as the wait that preceded it
        let quiet = now() - last_activity(projects, sid).unwrap_or(0.0).max(began);
        if quiet < times.after {
            if quiet < times.returned {
                continue;
            }
            match turn_ended(projects, sid) {
                Some(true) if !undelivered(projects, sid).is_empty() => {}
                Some(_) => continue,
                // the Python's thread ended on the raise: it watched no more and stalled nothing
                None => return (false, 0),
            }
        }
        let pids = session_pids(sid, proc);
        if pids.is_empty() {
            continue; // nothing to end: the session is between processes, or already gone
        }
        for pid in pids {
            terminate(pid);
        }
        return (true, quiet as u64);
    }
    (false, 0)
}

#[cfg(test)]
mod tests;
