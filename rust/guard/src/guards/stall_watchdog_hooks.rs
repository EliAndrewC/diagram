//! `stall-watchdog-hooks` (feature 295 item 4; ported from the shell of the same name, feature 449 T016): A STALL IS SEEN FROM OUTSIDE
//! EVERY SESSION. Nothing outside a session saw it stop: a headless check session sat two and a half hours with its work done and
//! unreported (2026-09-30). Any session's prompt starts the loop, detached, when its pid file names no live process, so it outlives
//! every session and comes back after a container restart. Each pass is a fresh process, through the wrapper, so an update to what a
//! stall is takes effect without restarting the loop; every action is a line in the state directory's log.
//!
//! Plan T016's decisions: (a) `prompt` is the guard, `run` and `once` are [`cli`], the pass is [`pass`]; (b) the lock is the
//! open file's and no child inherits it; (c) the self-check starts no loop; (d) `STALL_PASSES` ends a loop in a test.

use std::fs::{File, OpenOptions};
use std::path::{Path, PathBuf};
use std::process::{Command, Stdio};
use std::time::Duration;

use crate::protocol::{Answer, Event, Guard, Reply};
use crate::shared::log;
use crate::shared::session::Session;
use crate::shared::tool::flock;

pub(crate) mod pass;

/// The guard.
pub const GUARD: Guard = Guard {
    name: "stall-watchdog-hooks",
    events: &["UserPromptSubmit"],
    matcher: "*",
    decide,
};

/// What the guard and its loop read.
pub(crate) struct Config {
    pub state: PathBuf,
    pub period: f64,
    pub passes: Option<u64>,
    pub tree: PathBuf,
    pub exe: PathBuf,
    pub bash: &'static str,
    pub off: bool,
}

impl Config {
    pub(crate) fn from_env(env: &dyn Fn(&str) -> Option<String>) -> Self {
        let set = |k: &str| env(k).filter(|v| !v.is_empty());
        let home = set("HOME").unwrap_or_default();
        Self {
            state: set("STALL_STATE_DIR").map_or_else(
                || Path::new(&home).join(".claude/stall-watchdog"),
                PathBuf::from,
            ),
            period: set("STALL_PERIOD")
                .and_then(|v| v.parse().ok())
                .unwrap_or(300.0),
            passes: set("STALL_PASSES").and_then(|v| v.parse().ok()),
            tree: set("L7R_GUARD_TREE").map_or_else(|| PathBuf::from("/diagram"), PathBuf::from),
            exe: std::env::current_exe().unwrap_or_default(),
            bash: "bash",
            off: set("L7R_SELF_CHECK").is_some(),
        }
    }

    fn read() -> Self {
        Self::from_env(&|k| std::env::var(k).ok())
    }

    fn wrapper(&self) -> String {
        self.tree
            .join("scripts/hooks/l7r-guard.sh")
            .to_string_lossy()
            .into_owned()
    }
}

fn decide(event: &Event, session: &Session) -> Vec<Answer> {
    judge(event, session, &Config::read())
}

/// Start the loop when it is not running; says nothing.
pub(crate) fn judge(event: &Event, session: &Session, c: &Config) -> Vec<Answer> {
    if c.off || std::fs::create_dir_all(&c.state).is_err() {
        return Vec::new();
    }
    let pid = std::fs::read_to_string(c.state.join("pid")).unwrap_or_default();
    let pid = pid.trim();
    if !pid.is_empty() && Path::new("/proc").join(pid).is_dir() {
        return Vec::new();
    }
    let _ = Command::new("setsid")
        .arg("-f")
        .arg(&c.exe)
        .args(["--stall-watchdog", "run"])
        .stdin(Stdio::null())
        .stdout(Stdio::null())
        .stderr(Stdio::null())
        .status();
    log::fire(
        "stall-watchdog",
        "started",
        if pid.is_empty() { "none" } else { pid },
        "watchdog-started",
        &event.input,
        session,
    );
    Vec::new()
}

/// The loop: one instance on the host by the lock, then a pass every period, until its state directory goes.
pub(crate) fn run(c: &Config) -> i32 {
    if std::fs::create_dir_all(&c.state).is_err() {
        return 1;
    }
    let Ok(lock) = File::create(c.state.join("lock")) else {
        return 1;
    };
    if !flock(&lock, "-n") {
        return 0;
    }
    let _ = std::fs::write(c.state.join("pid"), std::process::id().to_string());
    let mut done = 0;
    while c.state.is_dir() && c.passes.is_none_or(|n| done < n) {
        pass(c);
        std::thread::sleep(Duration::from_secs_f64(c.period));
        done += 1;
    }
    0
}

/// One pass in a fresh process, through the wrapper, so an update reaches a running loop; its errors appended to the state's log.
fn pass(c: &Config) {
    let errors = OpenOptions::new()
        .create(true)
        .append(true)
        .open(c.state.join("errors"));
    let _ = Command::new(c.bash)
        .args([c.wrapper().as_str(), "--stall-watchdog", "once"])
        .stdin(Stdio::null())
        .stdout(Stdio::null())
        .stderr(errors.map_or(Stdio::null(), Stdio::from))
        .status();
}

/// `--stall-watchdog run` and `once` (one pass, printing what it did).
#[must_use]
pub fn cli(args: &[String]) -> Reply {
    with(args, &Config::read())
}

pub(crate) fn with(args: &[String], c: &Config) -> Reply {
    match args.first().map(String::as_str) {
        Some("run") => Reply {
            stdout: String::new(),
            stderr: String::new(),
            code: run(c),
        },
        Some("once") => {
            let lines = pass::run_pass(
                &pass::Paths::from_env(&|k| std::env::var(k).ok()),
                pass::now(),
            );
            Reply {
                code: 0,
                stdout: lines.join("\n") + if lines.is_empty() { "" } else { "\n" },
                stderr: String::new(),
            }
        }
        _ => Reply {
            stdout: String::new(),
            stderr: "usage: l7r-guard --stall-watchdog run | once\n".to_owned(),
            code: 2,
        },
    }
}

#[cfg(test)]
mod tests;
