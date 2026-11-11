//! The review checks' tooling (feature 449 T89, `ask:449-T89-reviews`), ported from `scripts/reviews/`: what a delta owes (`owed`,
//! `review_owed.py`), the glyph clock (`glyph`, its hour half), a dispatch's prerequisites and a review's verdict record (`prereq`,
//! `review_prereq.py`), the feature's hourly checkpoint (`checkpoint`, `checkpoint.py`), and `door`, the one door the step-back
//! bundle reaches them through until T83 ports it. `hm_approval._state_at` is the guard's `feature_approval_hooks::at_rev`, reused.

pub(crate) mod checkpoint;
pub mod door;
pub(crate) mod glyph;
pub(crate) mod owed;
pub(crate) mod prereq;

use std::path::{Component, Path, PathBuf};
use std::process::Command;

use serde_json::{Map, Value};

use crate::record::repo::universal;
use crate::Reply;

/// `l7r-gate reviews <owed|prereq|checkpoint> ...`.
#[must_use]
pub fn cli(args: &[String]) -> Reply {
    let rest = args.get(1..).unwrap_or_default();
    match args.first().map(String::as_str) {
        Some("owed") => owed::cli(rest),
        Some("prereq") => prereq::cli(rest),
        Some("checkpoint") => checkpoint::cli(rest),
        _ => reply(
            String::new(),
            "usage: l7r-gate reviews owed|prereq|checkpoint ...\n".to_owned(),
            2,
        ),
    }
}

pub(crate) fn reply(stdout: String, stderr: String, code: i32) -> Reply {
    Reply {
        stdout,
        stderr,
        code,
    }
}

/// `_git`: `git -C root args...`'s stdout, stripped, or None when git refused.
pub(crate) fn git(root: &Path, args: &[&str]) -> Option<String> {
    let done = Command::new("git")
        .arg("-C")
        .arg(root)
        .args(args)
        .output()
        .ok()?;
    done.status.success().then(|| {
        universal(&String::from_utf8_lossy(&done.stdout))
            .trim()
            .to_owned()
    })
}

/// `_gitdir`: the repository's absolute git directory.
pub(crate) fn gitdir(root: &Path) -> Option<PathBuf> {
    git(root, &["rev-parse", "--absolute-git-dir"])
        .filter(|g| !g.is_empty())
        .map(PathBuf::from)
}

/// `Path(text)` as pathlib reads it: `.` components and a trailing slash dropped, `.` for nothing.
pub(crate) fn py_path(text: &str) -> PathBuf {
    let kept: PathBuf = Path::new(text)
        .components()
        .filter(|c| !matches!(c, Component::CurDir))
        .collect();
    if kept.as_os_str().is_empty() {
        PathBuf::from(".")
    } else {
        kept
    }
}

/// `_read_json`: the file's JSON object, or an empty one where it is unreadable, not JSON or not an object.
pub(crate) fn read_object(path: Option<&Path>) -> Map<String, Value> {
    path.and_then(|p| std::fs::read_to_string(p).ok())
        .and_then(|t| serde_json::from_str::<Value>(&t).ok())
        .and_then(|v| match v {
            Value::Object(m) => Some(m),
            _ => None,
        })
        .unwrap_or_default()
}

/// `float(value)` of a JSON value already known truthy-or-zero (`float(x or 0)`).
pub(crate) fn as_float(value: Option<&Value>) -> f64 {
    match value {
        Some(Value::Number(n)) => n.as_f64().unwrap_or(0.0),
        Some(Value::Bool(true)) => 1.0,
        Some(Value::String(s)) => s.trim().parse().unwrap_or(0.0),
        _ => 0.0,
    }
}

/// `int(float)`: toward zero.
#[expect(
    clippy::cast_possible_truncation,
    reason = "an epoch time fits an i64, as Python's int() of one does"
)]
pub(crate) fn int_of(at: f64) -> i64 {
    at.trunc() as i64
}

/// `time.strftime(fmt, time.localtime(at))`: the standard library reads no time zone, so `date` answers, as `passes.rs` asks it.
pub(crate) fn local_time(at: f64, fmt: &str) -> String {
    let secs = int_of(at.floor());
    Command::new("date")
        .args(["-d", &format!("@{secs}"), &format!("+{fmt}")])
        .output()
        .map(|o| String::from_utf8_lossy(&o.stdout).trim().to_owned())
        .unwrap_or_default()
}

/// The epoch seconds now, as `time.time()`.
pub(crate) fn now() -> f64 {
    l7r_guard::shared::checks::now()
}

/// `json.dumps(value, indent=1) + "\n"` written to `path`, as `Path.write_text` writes it.
pub(crate) fn write_json(path: &Path, value: &Value) -> std::io::Result<()> {
    std::fs::write(
        path,
        l7r_guard::shared::pyjson::dumps(value, Some(1), true) + "\n",
    )
}

/// An ISO time's epoch seconds as `datetime.fromisoformat(str(t).replace("Z", "+00:00")).timestamp()` reads one, or None.
pub(crate) fn iso_seconds(t: Option<&Value>) -> Option<f64> {
    let text = t?.as_str()?.replace('Z', "+00:00");
    crate::measure::popup_rounds::iso::parse(&text)
}

#[cfg(test)]
mod tests;
