//! The task gate (feature 449 T131, `ask:449-phase3-remainder` Q2 task A, one cut with no door, FR-003): `l7r-gate tick` - `make tick`,
//! and `make land`'s first pass and its ticks, which ask [`tick::land_check`] and [`tick::tick`] in process where they ran
//! `scripts/tick-task.py` by path; `l7r-gate task-start` (`make task-start`, `scripts/task_start.py` with `gates/plan_hold.py`); and
//! `l7r-gate phase-read` (`make phase-read`, `gates/phase_sources.py`). `gates/wording.py`, the wording-only check the tick asks, is
//! [`wording`]. What the Python reached through `scripts/plan_door.py`, the closing check, the reviews' checkpoint and the work budget's
//! sources by command is asked in process, each the function its command runs. `l7r-gate task-add` (`make task-add`, [`task_add`]) and
//! `l7r-gate set-down` (`make set-down`, [`set_down`]) are `scripts/task-add.py` and `set-down.py`, ported whole by T135.

pub mod phase_sources;
mod plan_hold;
#[cfg(test)]
mod research_boxes;
pub mod set_down;
pub mod task_add;
pub mod task_start;
pub mod tick;
mod wording;

use std::path::{Path, PathBuf};
use std::process::Command;

use l7r_gate_core::Reply;
use l7r_guard::shared::py_text::strip;

/// `l7r-gate tick|task-start|task-add|set-down|phase-read <args>` from `cwd`, as the binary dispatches them.
#[must_use]
pub fn cli(verb: &str, args: &[String], cwd: &Path) -> Reply {
    match verb {
        "tick" => tick::cli(args, cwd),
        "task-start" => task_start::cli(args, cwd),
        "task-add" => task_add::cli(args, cwd, &std::env::var("TASK_TITLE").unwrap_or_default()),
        "set-down" => set_down::cli(args, cwd),
        _ => phase_sources::cli(args, cwd),
    }
}

/// A file as `read_text(encoding="utf-8")` reads it: strictly UTF-8, its newlines universal; the error what the Python raised.
fn read_strict(path: &Path) -> Result<String, String> {
    let bytes = std::fs::read(path).map_err(|e| format!("{}: {e}", path.display()))?;
    let text = String::from_utf8(bytes)
        .map_err(|e| format!("UnicodeDecodeError: {}: {e}", path.display()))?;
    Ok(text.replace("\r\n", "\n").replace('\r', "\n"))
}

/// `git <args>` in `root`: its exit code (`None` when git could not start) and its stdout as text.
fn git(root: &Path, args: &[&str]) -> (Option<i32>, Vec<u8>) {
    Command::new("git")
        .arg("-C")
        .arg(root)
        .args(args)
        .output()
        .map_or((None, Vec::new()), |o| (o.status.code(), o.stdout))
}

/// `path` written with `data`; the error what the Python's write raised.
fn write_file(path: &Path, data: &[u8]) -> Result<(), String> {
    std::fs::write(path, data).map_err(|e| format!("{}: {e}", path.display()))
}

/// The git common directory as `rev-parse --path-format=absolute --git-common-dir` prints it, stripped ("" outside a repository), from
/// `root`.
fn common_text(root: &Path) -> String {
    let (_, out) = git(
        root,
        &["rev-parse", "--path-format=absolute", "--git-common-dir"],
    );
    strip(&String::from_utf8_lossy(&out)).to_owned()
}

/// `git rev-parse --show-toplevel` in the working directory, stripped, as `Path(...)` reads it ("" is `.`).
fn toplevel_or_dot(cwd: &Path) -> PathBuf {
    let (_, out) = git(cwd, &["rev-parse", "--show-toplevel"]);
    let text = strip(&String::from_utf8_lossy(&out)).to_owned();
    if text.is_empty() {
        PathBuf::from(".")
    } else {
        PathBuf::from(text)
    }
}

/// The time now, as seconds since the epoch.
fn now_secs() -> u64 {
    std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .map_or(0, |d| d.as_secs())
}

/// `%Y-%m-%dT%H:%M:%SZ` of a UTC time.
#[expect(clippy::many_single_char_names, reason = "the fields of a date")]
fn utc_text(secs: u64) -> String {
    let (y, m, d, h, mi, s) = l7r_guard::shared::log::civil(secs);
    format!("{y:04}-{m:02}-{d:02}T{h:02}:{mi:02}:{s:02}Z")
}

fn reply(stdout: String, stderr: String, code: i32) -> Reply {
    Reply {
        stdout,
        stderr,
        code,
    }
}

/// A raise: what was printed before it, then its message after a `Traceback` line, exit 1, as the Python's uncaught exception ended.
fn raised(tool: &str, stdout: String, stderr: &str, why: &str) -> Reply {
    reply(
        stdout,
        format!("{stderr}Traceback (most recent call last):\n  l7r-gate {tool}\n{why}\n"),
        1,
    )
}

#[cfg(test)]
mod tests;
