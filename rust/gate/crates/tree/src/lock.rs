//! One `make done` at a time in a clone (feature 375 follow-up, the GM 2026-10-10; feature 449 T067, from `gate_lock.py`), and whether a
//! make runs in this tree (from `own-make.sh`). Two gates on one tree write the same pool maps, coverage data and failure markers and
//! fail together. `<git dir>/gate.lock` names the `make` process that owns the gate; an owner that died is no owner, so there is never a
//! stale lock to clear by hand. `own-make` is what a waiter means by `pgrep -f "make done"`, scoped to the tree that asks: on 2026-09-28 a
//! waiter looped six hours after its own gate had failed, held by another clone's. Only a make process counts: the waiting shell that
//! launched the run carries the words too, and once waited four hours past a roll that had finished (2026-09-30).

use std::path::{Path, PathBuf};
use std::time::{SystemTime, UNIX_EPOCH};

use fancy_regex::Regex;
use serde_json::{json, Value};

use crate::Reply;

const LOCK: &str = "gate.lock";

fn cmdline(proc_root: &Path, pid: u64) -> Vec<String> {
    let raw = std::fs::read(proc_root.join(pid.to_string()).join("cmdline")).unwrap_or_default();
    raw.split(|b| *b == 0)
        .filter(|w| !w.is_empty())
        .map(|w| String::from_utf8_lossy(w).into_owned())
        .collect()
}

fn base_name(word: &str) -> &str {
    word.rsplit('/').next().unwrap_or(word)
}

/// Whether `pid` is alive and still a make running the gate (a reused pid is some other program).
fn running_gate(proc_root: &Path, pid: u64) -> bool {
    let words: Vec<String> = cmdline(proc_root, pid)
        .join(" ")
        .split_whitespace()
        .map(str::to_owned)
        .collect();
    words
        .first()
        .is_some_and(|w| ["make", "gmake"].contains(&base_name(w)))
        && words[1..].iter().any(|w| w == "done")
}

fn read_lock(git_dir: &Path) -> Value {
    serde_json::from_str(&std::fs::read_to_string(git_dir.join(LOCK)).unwrap_or_default())
        .unwrap_or(Value::Null)
}

/// Own the clone's gate for `pid`, or say who already does.
fn acquire(git_dir: &Path, pid: u64, proc_root: &Path, now: f64) -> String {
    let held = read_lock(git_dir);
    let other = held["pid"].as_u64().unwrap_or(0);
    if other != 0 && other != pid && running_gate(proc_root, other) {
        #[expect(
            clippy::cast_possible_truncation,
            clippy::cast_sign_loss,
            reason = "a whole second since the epoch"
        )]
        let (_, _, _, h, mi, s) =
            l7r_guard::shared::log::civil(held["t"].as_f64().unwrap_or(0.0) as u64);
        return format!("a `make done` is already running in this clone (pid {other}, started {h:02}:{mi:02}:{s:02}): two gates on one tree write the same maps and coverage files and fail together (feature 375 follow-up). Wait for its notification, or stop it first.");
    }
    let _ = std::fs::write(
        git_dir.join(LOCK),
        json!({"pid": pid, "t": now}).to_string(),
    );
    String::new()
}

/// Whether a live gate owns the clone (feature 385 T30: nothing may merge into a tree while its gate runs).
fn held(git_dir: &Path, proc_root: &Path) -> bool {
    let pid = read_lock(git_dir)["pid"].as_u64().unwrap_or(0);
    pid != 0 && running_gate(proc_root, pid)
}

fn reply(stderr: String, code: i32) -> Reply {
    Reply {
        stdout: String::new(),
        stderr,
        code,
    }
}

/// Is a process under `proc_root` a make of this target, working inside `top`?
fn own_make(proc_root: &Path, top: &Path, target: &str) -> bool {
    let Ok(pattern) = Regex::new(&format!("make {target}")) else {
        return false;
    };
    let prefix = format!("{}/", top.display());
    let pids: Vec<PathBuf> = std::fs::read_dir(proc_root)
        .into_iter()
        .flatten()
        .flatten()
        .map(|e| e.path())
        .collect();
    pids.iter().any(|dir| {
        let raw = std::fs::read(dir.join("cmdline")).unwrap_or_default();
        let words: Vec<&[u8]> = raw.split(|b| *b == 0).collect();
        let argv0 = String::from_utf8_lossy(words[0]);
        let name = base_name(&argv0);
        let is_make = name == "make"
            || name == "gmake"
            || name.starts_with("make ")
            || name.starts_with("gmake ");
        let line = String::from_utf8_lossy(&raw).replace('\0', " ");
        let cwd = std::fs::read_link(dir.join("cwd")).unwrap_or_default();
        is_make
            && pattern.is_match(&line).unwrap_or(false)
            && format!("{}/", cwd.display()).starts_with(&prefix)
    })
}

fn top_of(cwd: &Path) -> PathBuf {
    crate::stamp::toplevel()
        .or(std::fs::canonicalize(cwd).ok())
        .unwrap_or_default()
}

/// `l7r-gate own-make <target words...>`: exit 0 while a `make <target>` runs in this working tree, 1 otherwise.
#[must_use]
pub fn own_make_cli(args: &[String], proc_root: &Path) -> Reply {
    if args.is_empty() {
        return reply("usage: own-make <make target>\n".to_owned(), 2);
    }
    let found = own_make(proc_root, &top_of(Path::new(".")), &args.join(" "));
    reply(String::new(), i32::from(!found))
}

/// `l7r-gate lock acquire <git dir> <make pid> | held <git dir>`.
pub fn cli(args: &[String], proc_root: &Path) -> Reply {
    let words: Vec<&str> = args.iter().map(String::as_str).collect();
    match words.as_slice() {
        ["held", dir] => reply(String::new(), i32::from(!held(Path::new(dir), proc_root))),
        ["acquire", dir, pid] => {
            let now = SystemTime::now()
                .duration_since(UNIX_EPOCH)
                .map_or(0.0, |d| d.as_secs_f64());
            let why = acquire(Path::new(dir), pid.parse().unwrap_or(0), proc_root, now);
            if why.is_empty() {
                reply(String::new(), 0)
            } else {
                reply(format!("\nGATE REFUSED: {why}\n"), 1)
            }
        }
        _ => reply(
            "usage: lock acquire <git dir> <make pid> | held <git dir>\n".to_owned(),
            2,
        ),
    }
}

#[cfg(test)]
mod tests;
