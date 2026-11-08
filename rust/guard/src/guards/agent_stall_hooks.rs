//! `agent-stall-hooks` (feature 143; ported from the shell of the same name, feature 449 T015): A BACKGROUND SUBAGENT THAT HAS SILENTLY
//! STALLED IS REPORTED, NEVER ASSUMED RUNNING. A `source-reader` hit a bad TLS certificate and the harness sent no completion
//! notification; the session assumed it was still running for ten hours, until the GM asked (2026-08-28). A stall's shape: a subagent
//! transcript whose LAST record is a `user` record (a `tool_result` waiting for the next turn) and whose mtime has not moved for
//! `AGENT_STALE_S`; a finished agent ends on an `assistant` record. The harness gives no other liveness signal.
//!
//! Plan T015's decisions: (a) every mode ported, `prompt` the guard and the rest [`cli`]; (b) `scripts/hooks/agent-stall-hooks.sh`
//! stays as a forwarder, because a session runs the `ack` these messages print by hand; (c) `AGENT_WATCH_TICKS` ends a watch in a test.

use std::collections::HashSet;
use std::fs::File;
use std::io::{Read, Seek, SeekFrom};
use std::path::{Path, PathBuf};
use std::time::{Duration, SystemTime};

use serde_json::Value;

use crate::protocol::{Answer, Event, Guard, Reply};
use crate::shared::log;
use crate::shared::session::Session;
use crate::shared::state::field;

/// The guard.
pub const GUARD: Guard = Guard {
    name: "agent-stall-hooks",
    events: &["UserPromptSubmit"],
    matcher: "*",
    decide,
};

/// How long a transcript must stand still, how old one may be and still count, and the watch's pace.
pub(crate) struct Limits {
    pub stale: u64,
    pub recent: u64,
    pub tick: f64,
    pub ticks: Option<u64>,
}

impl Limits {
    pub(crate) fn from_env(env: &dyn Fn(&str) -> Option<String>) -> Self {
        let num = |k: &str, d: u64| env(k).and_then(|v| v.parse().ok()).unwrap_or(d);
        Self {
            stale: num("AGENT_STALE_S", 300),
            recent: num("AGENT_RECENT_S", 172_800),
            tick: env("AGENT_TICK_S")
                .and_then(|v| v.parse().ok())
                .unwrap_or(30.0),
            ticks: env("AGENT_WATCH_TICKS").and_then(|v| v.parse().ok()),
        }
    }

    fn read() -> Self {
        Self::from_env(&|k| std::env::var(k).ok())
    }
}

/// The `type` of a transcript's last JSON record, read back from its end until that line is whole; `None` when unreadable.
fn last_type(path: &Path) -> Option<String> {
    const STEP: u64 = 65_536;
    let mut f = File::open(path).ok()?;
    let mut pos = f.seek(SeekFrom::End(0)).ok()?;
    let mut buf: Vec<u8> = Vec::new();
    let trimmed = |b: &[u8]| b.len() - b.iter().rev().take_while(|c| **c == b'\n').count();
    while pos > 0 {
        let step = STEP.min(pos);
        pos -= step;
        f.seek(SeekFrom::Start(pos)).ok()?;
        let mut chunk = vec![0; usize::try_from(step).ok()?];
        f.read_exact(&mut chunk).ok()?;
        chunk.extend_from_slice(&buf);
        buf = chunk;
        if buf[..trimmed(&buf)].contains(&b'\n') {
            break;
        }
    }
    let body = &buf[..trimmed(&buf)];
    let line = body.rsplit(|c| *c == b'\n').next()?;
    let doc: Value = serde_json::from_slice(line).ok()?;
    doc.get("type")
        .and_then(Value::as_str)
        .filter(|t| !t.is_empty())
        .map(str::to_owned)
}

/// One transcript no older than `recent`: its id, its age, and the `type` of its last record, read only when `age >= stale`.
fn scan(dir: &Path, stale: u64, recent: u64) -> Vec<(String, u64, String)> {
    let Ok(entries) = std::fs::read_dir(dir) else {
        return Vec::new();
    };
    let mut files: Vec<PathBuf> = entries.filter_map(Result::ok).map(|e| e.path()).collect();
    files.sort();
    let now = SystemTime::now();
    let mut out = Vec::new();
    for f in files {
        let name = f
            .file_name()
            .map(|n| n.to_string_lossy().into_owned())
            .unwrap_or_default();
        let Some(id) = name
            .strip_prefix("agent-")
            .and_then(|n| n.strip_suffix(".jsonl"))
        else {
            continue;
        };
        let age = std::fs::metadata(&f)
            .and_then(|m| m.modified())
            .ok()
            .and_then(|at| now.duration_since(at).ok())
            .map_or(0, |d| d.as_secs());
        if age > recent {
            continue;
        }
        let kind = if age >= stale {
            last_type(&f).unwrap_or_else(|| "-".to_owned())
        } else {
            "-".to_owned()
        };
        out.push((id.to_owned(), age, kind));
    }
    out
}

/// The line for each stalled transcript; with `seen`, each stall once until its transcript moves again.
fn report(dir: &Path, l: &Limits, mut seen: Option<&mut HashSet<String>>) -> Vec<String> {
    let mut out = Vec::new();
    for (id, age, kind) in scan(dir, l.stale, l.recent) {
        if dir.join("../stall-ack").join(&id).exists() {
            continue;
        }
        if age < l.stale {
            if let Some(s) = seen.as_deref_mut() {
                s.remove(&id);
            }
            continue;
        }
        if kind != "user" || seen.as_deref_mut().is_some_and(|s| !s.insert(id.clone())) {
            continue;
        }
        // the exact command, the directory this scans already in it: acking with the tasks directory the task-notification names
        // created a marker nothing reads, and the stall came back at every prompt (feature 166, measured 2026-08-30)
        out.push(format!(
            "STALLED {id}: transcript unchanged for {age}s, last record a tool_result with no reply - stop it (TaskStop) and relaunch its \
batch, or read the rest yourself in a NEW background agent; never in a foreground WebFetch batch; then run exactly: \
scripts/hooks/agent-stall-hooks.sh ack {} {id}",
            dir.display()
        ));
    }
    out
}

fn decide(event: &Event, session: &Session) -> Vec<Answer> {
    judge(event, session, &Limits::read())
}

pub(crate) fn judge(event: &Event, session: &Session, l: &Limits) -> Vec<Answer> {
    let transcript = field(&event.input, "transcript_path");
    if transcript.is_empty() {
        return Vec::new();
    }
    let dir = PathBuf::from(format!(
        "{}/subagents",
        transcript.strip_suffix(".jsonl").unwrap_or(transcript)
    ));
    let lines = report(&dir, l, None).join("\n");
    if lines.is_empty() {
        return Vec::new();
    }
    log::fire(
        "agent-stall",
        "reminded",
        &lines,
        "stalled-agent",
        &event.input,
        session,
    );
    vec![Answer::Print(format!(
        "agent-stall: {lines}\nagent-stall: a stalled reader is not \"still running\" - act on it now (scripts/hooks/agent-stall-hooks.sh)."
    ))]
}

fn watch(dir: &Path, l: &Limits) {
    let mut seen = HashSet::new();
    let mut done = 0;
    while l.ticks.is_none_or(|t| done < t) {
        for line in report(dir, l, Some(&mut seen)) {
            println!("{line}");
        }
        std::thread::sleep(Duration::from_secs_f64(l.tick));
        done += 1;
    }
}

/// `--agent-stall check <dir>`, `watch <dir>`, `pending <dir>` (one id per line for every agent still awaiting a reply) and
/// `ack <dir> <id>` (the session has handled this stall: never report it again).
#[must_use]
pub fn cli(args: &[String]) -> Reply {
    let say = |stdout: String, code: i32| Reply {
        stdout,
        stderr: String::new(),
        code,
    };
    let arg = |i: usize| args.get(i).map_or("", String::as_str);
    let dir = Path::new(arg(1));
    let l = Limits::read();
    let block = |lines: Vec<String>| lines.into_iter().map(|x| x + "\n").collect::<String>();
    match (arg(0), arg(1).is_empty()) {
        ("check", false) => say(block(report(dir, &l, None)), 0),
        ("pending", false) => {
            let waiting = scan(dir, 0, u64::MAX).into_iter().filter(|(_, _, kind)| kind == "user").map(|(id, _, _)| id).collect();
            say(block(waiting), 0)
        }
        ("ack", false) if !arg(2).is_empty() => {
            let marks = dir.join("../stall-ack");
            let made = std::fs::create_dir_all(&marks).and_then(|()| File::create(marks.join(arg(2))).map(|_| ()));
            say(String::new(), i32::from(made.is_err()))
        }
        ("watch", false) => {
            watch(dir, &l);
            say(String::new(), 0)
        }
        _ => Reply {
            stdout: String::new(),
            stderr: "usage: l7r-guard --agent-stall check <dir> | watch <dir> | pending <dir> | ack <dir> <id>\n".to_owned(),
            code: 2,
        },
    }
}

#[cfg(test)]
mod tests;
