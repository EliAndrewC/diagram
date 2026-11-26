//! `SINCE=last`: when the GM last asked (feature 451 T298; the GM 2026-11-26: "we might want an additional capability in the time
//! task breakdown to keep track of whenever I last asked, so that I don't have to remember the period of time to ask for when I want
//! the new data").
//!
//! THE MARKER is a line a report, `{"until": "<the window's end>", "asked": "<when>"}`, appended to `task-time-asked.log` in the
//! clone's event-log directory (`<common .git>/l7r-events/`). It lives there because that directory is the tooling state that
//! travels: `scripts/state-sync.sh push` (`make state-push`, run by every landing) commits every file of it, and a restore merges
//! one by the lines the local file lacks, appended. So the marker is APPEND-ONLY and read as the GREATEST `until`, never the last
//! line - a restore may append an older one. Its extension is not `.jsonl`: `all_logs` reads only those as event logs.
//!
//! Only `SINCE=last` writes it, and only after its report was made: "a plain SINCE= does not move the marker" (T298's brief).

use std::io::Write as _;
use std::path::{Path, PathBuf};

use l7r_shared::guards::event_log_hooks::common_git_dir;
use serde_json::{json, Value};

/// The marker's file for the tree `root` (a worktree's is its clone's).
#[must_use]
pub fn marker(root: &Path) -> PathBuf {
    common_git_dir(root).join("l7r-events/task-time-asked.log")
}

/// The end of the last report `SINCE=last` made: the greatest `until` of the marker's lines.
#[must_use]
pub fn last(marker: &Path) -> Option<String> {
    std::fs::read_to_string(marker)
        .unwrap_or_default()
        .lines()
        .filter_map(|l| serde_json::from_str::<Value>(l).ok())
        .filter_map(|v| v.get("until").and_then(Value::as_str).map(str::to_owned))
        .max()
}

/// Appends the report's end `until` (asked at `asked`) to the marker.
///
/// # Errors
///
/// The marker's directory or file could not be written.
pub fn mark(marker: &Path, until: &str, asked: &str) -> std::io::Result<()> {
    if let Some(dir) = marker.parent() {
        std::fs::create_dir_all(dir)?;
    }
    let mut f = std::fs::OpenOptions::new()
        .create(true)
        .append(true)
        .open(marker)?;
    writeln!(f, "{}", json!({"until": until, "asked": asked}))
}
