//! THE LANE'S READ MARK (feature 461 T20, plan D9, data-model.md "The log line"): the `owed` lines of the lane's log
//! (`l7r-lane/lane.jsonl` of the git common directory) not yet shown to the coordinator, taken ONCE. `l7r-gate lane wait` (`make
//! lane-wait`, the lane crate's `wake.rs`) and the prompt hook (`clone-sync-hooks`) both read here, so one rule says what is unread:
//! the lines past `l7r-lane/read-mark`, a byte offset into the log.
//!
//! WHICHEVER READER COMES FIRST MOVES THE MARK, the hook too (a decision, the easier route of D9's "prints any unread lane lines, so a
//! wake-up command killed early loses nothing"): a hook that printed without moving it would have each re-armed wait print at once
//! what the prompt already showed, a wake FR-005 does not list. So the read, the lines taken and the mark moved run under the mark's
//! own lock (`read-mark.lock`, by `flock`, let go by `flock -u` before the close - 461 T14's reason: a child another thread forks holds
//! a copy of the descriptor until its `exec`), and the mark is written whole by a rename. Only complete lines are taken: a writer's
//! torn last line (no newline yet) is read again once whole. A mark past the log's end (the log replaced) reads from its start.
//!
//! It creates nothing where the lane has no log: a clone with no lane prints nothing and is left as it was.

use std::path::{Path, PathBuf};

use serde_json::Value;

use crate::tool::{flock, flock_within};

/// The lane's directory, in the git common directory.
pub const DIR: &str = "l7r-lane";
/// The lane's log, in [`DIR`].
pub const FILE: &str = "lane.jsonl";
/// The read mark: the byte offset into [`FILE`] up to which every `owed` line was shown.
pub const MARK: &str = "read-mark";
/// The mark's lock, held while a reader reads, takes and moves.
pub const MARK_LOCK: &str = "read-mark.lock";
/// GUESS: how long a reader waits for another holding the mark's lock (its read takes milliseconds) before it leaves the lines to
/// that reader, which is showing them.
pub const LOCK_S: f64 = 5.0;

/// The lane's directory under the git common directory `common`.
#[must_use]
pub fn dir(common: &Path) -> PathBuf {
    common.join(DIR)
}

/// The mark's offset as written; none where it is missing or no number.
fn mark_of(dir: &Path) -> Option<u64> {
    std::fs::read_to_string(dir.join(MARK))
        .ok()
        .and_then(|t| t.trim().parse().ok())
}

/// Whether any byte of the log lies past the mark: asked without the lock, so a reader with nothing to take spawns no `flock`.
#[must_use]
pub fn unread(common: &Path) -> bool {
    let d = dir(common);
    std::fs::metadata(d.join(FILE)).is_ok_and(|m| mark_of(&d) != Some(m.len()))
}

/// The `line` of every `owed` event past the mark, in the log's order, and the mark moved past the last complete line read: each
/// such line is taken once, by whichever reader comes first. Empty where there is no log, nothing past the mark, or another reader
/// holds the lock past [`LOCK_S`].
#[must_use]
pub fn take_unread(common: &Path) -> Vec<String> {
    if !unread(common) {
        return Vec::new();
    }
    let d = dir(common);
    let Ok(Some(lock)) = flock_within(&d.join(MARK_LOCK), LOCK_S) else {
        return Vec::new();
    };
    let taken = take(&d);
    let _ = flock(&lock, "-u");
    taken
}

/// [`take_unread`] under the lock: the log read from the mark, its complete lines' owed lines, the mark moved past them.
fn take(dir: &Path) -> Vec<String> {
    let bytes = std::fs::read(dir.join(FILE)).unwrap_or_default();
    let from = mark_of(dir)
        .and_then(|m| usize::try_from(m).ok())
        .filter(|m| *m <= bytes.len())
        .unwrap_or(0);
    let rest = &bytes[from..];
    let Some(end) = rest.iter().rposition(|b| *b == b'\n') else {
        return Vec::new();
    };
    let lines = owed(&rest[..end]);
    let tmp = dir.join(format!("{MARK}.{}", std::process::id()));
    let to = (from + end + 1).to_string();
    let _ = std::fs::write(&tmp, to).and_then(|()| std::fs::rename(&tmp, dir.join(MARK)));
    lines
}

/// The `line` of each `owed` event among `bytes`' lines; a line that does not parse is skipped, as the log's reader skips it.
fn owed(bytes: &[u8]) -> Vec<String> {
    String::from_utf8_lossy(bytes)
        .lines()
        .filter_map(|l| serde_json::from_str::<Value>(l).ok())
        .filter(|l| l["event"] == "owed")
        .filter_map(|l| l["line"].as_str().map(str::to_owned))
        .collect()
}

#[cfg(test)]
mod tests;
