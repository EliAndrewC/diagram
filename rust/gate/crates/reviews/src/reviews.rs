//! The review checks' tooling (feature 449 T89, `ask:449-T89-reviews`), ported from `scripts/reviews/`: what a delta owes (`owed`,
//! `review_owed.py`), the glyph clock (`glyph`, its hour half), a dispatch's prerequisites and a review's verdict record (`prereq`,
//! `review_prereq.py`), and the feature's hourly checkpoint (`checkpoint`, `checkpoint.py`), which the step-back bundle (`l7r-gate measure
//! step-back`) reads in process since feature 449 T120 removed its door (`reviews-door`). `hm_approval._state_at` is the guard's `feature_approval_hooks::at_rev`, reused.
//! The review ledger (feature 449 T83, `ask:449-T83-scope`): `ledger`, the command lines of `ledger_lint.py` and `review_cost.py` over the
//! guard's `shared::ledger`, and `ledger_passes`, `ledger_owed.py`'s port.
//! The GM-review queue (feature 449 T91, `ask:449-T82-claims`): `gm_review`, `scripts/gm_review.py`'s port behind `l7r-gate gm-review`, the one
//! writer of `gm-review.jsonl` and the GM's box, which the round arbiter and the claims tools call in process.
//! The reviewer's snapshot (feature 449 T132): `snapshot`, `scripts/reviews/review_snapshot.py`'s port behind `l7r-gate reviews snapshot`.
//! The review census and the agent sync (feature 449 T136, `ask:449-phase3-remainder`): `census`, `review_census.py`'s port behind
//! `l7r-gate reviews census`, and `agent_sync`, `agent_sync.py`'s port behind `l7r-gate reviews agent-sync`, the one writer of the modal
//! checks' agent files' generated guidelines.
//! The closing check (feature 449 T127): `closing`, the reasons of `scripts/gates/close_check.py`'s port, which `gm_review` asks in process and
//! `cohort`'s `l7r-gate close-check` serves to the push and `make tick`.

pub mod agent_sync;
pub mod census;
pub mod checkpoint;
pub mod closing;
pub mod glyph;
pub mod gm_review;
pub mod ledger;
pub mod ledger_passes;
pub mod owed;
pub mod prereq;
pub mod snapshot;

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
        Some("snapshot") => snapshot::cli(rest),
        Some("census") => census::cli(rest, &gate_tree()),
        Some("agent-sync") => agent_sync::cli(rest, &gate_tree(), agent_sync::SYNC),
        Some("ledger-lint") => ledger::lint_cli(
            rest,
            &std::env::var_os("L7R_GATE_TREE").map_or_else(|| PathBuf::from("."), PathBuf::from),
        ),
        Some("ledger-rows") => ledger::rows_cli(rest, &mut std::io::stdin()),
        Some("review-cost") => ledger::cost_cli(rest, &std::env::var("HOME").unwrap_or_default()),
        Some("ledger-owed") => ledger_passes::cli(rest, &ledger_passes::Env::of_process()),
        Some("ledger-passes") => ledger_passes::passes_cli(rest, &ledger_passes::Env::of_process()),
        _ => reply(
            String::new(),
            "usage: l7r-gate reviews owed|prereq|checkpoint|snapshot|census|agent-sync|ledger-lint|ledger-rows|review-cost|ledger-owed|ledger-passes ...\n".to_owned(),
            2,
        ),
    }
}

/// The gate's own tree (`L7R_GATE_TREE`, which `l7r-gate.sh` sets; the working directory where unset): where the Python's `__file__` stood.
fn gate_tree() -> PathBuf {
    std::env::var_os("L7R_GATE_TREE").map_or_else(|| PathBuf::from("."), PathBuf::from)
}

#[must_use]
pub fn reply(stdout: String, stderr: String, code: i32) -> Reply {
    Reply {
        stdout,
        stderr,
        code,
    }
}

/// `_git`: `git -C root args...`'s stdout, stripped, or None when git refused.
#[must_use]
pub fn git(root: &Path, args: &[&str]) -> Option<String> {
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
pub fn gitdir(root: &Path) -> Option<PathBuf> {
    git(root, &["rev-parse", "--absolute-git-dir"])
        .filter(|g| !g.is_empty())
        .map(PathBuf::from)
}

/// `Path(text)` as pathlib reads it: `.` components and a trailing slash dropped, `.` for nothing.
#[must_use]
pub fn py_path(text: &str) -> PathBuf {
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
#[must_use]
pub fn read_object(path: Option<&Path>) -> Map<String, Value> {
    path.and_then(|p| std::fs::read_to_string(p).ok())
        .and_then(|t| serde_json::from_str::<Value>(&t).ok())
        .and_then(|v| match v {
            Value::Object(m) => Some(m),
            _ => None,
        })
        .unwrap_or_default()
}

/// `float(value)` of a JSON value already known truthy-or-zero (`float(x or 0)`).
#[must_use]
pub fn as_float(value: Option<&Value>) -> f64 {
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
#[must_use]
pub fn int_of(at: f64) -> i64 {
    at.trunc() as i64
}

/// `time.strftime(fmt, time.localtime(at))`: the standard library reads no time zone, so `date` answers, as `passes.rs` asks it.
#[must_use]
pub fn local_time(at: f64, fmt: &str) -> String {
    let secs = int_of(at.floor());
    Command::new("date")
        .args(["-d", &format!("@{secs}"), &format!("+{fmt}")])
        .output()
        .map(|o| String::from_utf8_lossy(&o.stdout).trim().to_owned())
        .unwrap_or_default()
}

/// The epoch seconds now, as `time.time()`.
#[must_use]
pub fn now() -> f64 {
    l7r_guard::shared::checks::now()
}

/// `json.dumps(value, indent=1) + "\n"` written to `path`, as `Path.write_text` writes it.
///
/// # Errors
///
/// Where what it reads, writes or runs fails: the error says which and why.
pub fn write_json(path: &Path, value: &Value) -> std::io::Result<()> {
    std::fs::write(
        path,
        l7r_guard::shared::pyjson::dumps(value, Some(1), true) + "\n",
    )
}

/// An ISO time's epoch seconds as `datetime.fromisoformat(str(t).replace("Z", "+00:00")).timestamp()` reads one, or None.
#[must_use]
pub fn iso_seconds(t: Option<&Value>) -> Option<f64> {
    let text = t?.as_str()?.replace('Z', "+00:00");
    crate::measure::popup_rounds::iso::parse(&text)
}

#[cfg(test)]
mod tests;
