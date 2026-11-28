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

use std::collections::BTreeSet;
use std::path::{Path, PathBuf};

use serde_json::Value;

use crate::builder_queue::{DONE_REFS, LOG as POOL_LOG};
use crate::lane_log::{batches, hand_ins, lines_of, waiting_unasked, Batch};
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

// WHAT THE LANE HOLDS FOR ITS COORDINATOR (feature 461 T21, D9's Stop rule, read by `pool-idle-hooks`): an open batch, or a waiting
// hand-in while the runner lives - the cases in which a line owed to the coordinator will come, so its `make lane-wait` must run.
// THE ONE READING OF THE LANE'S STATES (`crate::lane_log`, 461 T63), which the lane crate's `log.rs` re-exports: an open batch is
// `lane_log::batches`' open one, a waiting hand-in `lane_log::state`'s `waiting` (`lane_log::waiting_unasked`), so a change to a
// batch's or a hand-in's state moves this rule with it. Two of its parts are read the easier way, each labeled:
// - "landed" is a `landed` line listing the hand-in, or its done ref gone; `origin/main` holding it (the lane's `held_by`) is not
//   asked, a git walk a Stop hook would pay every turn. Cost: a hand-in landed on `origin/main` by hand while its done ref still
//   stands reads as waiting - which `make carry` (the ref deleted at its end) does not leave.
// - in PHASE 1 a waiting hand-in counts ONLY WHILE THE RUNNER LIVES (a deliberate deviation from D9's literal "a waiting hand-in"):
//   before T22 flips `HAND_IN_BASE` no hand-in starts the runner (T12 Decision 6), the coordinator lands each by hand, and a wait
//   over it could never wake (`wake::unserved` is quiet there on purpose). From PHASE 2'S BASE ([`origin_base`], 461 T64) it counts
//   whether the runner lives or not: every hand-in starts the runner there, so one no runner serves is a start that failed, and the
//   wait this rule keeps armed says that death once (`wake::unserved`, 461 T56).

/// The runner's lock, in [`DIR`] (the lane crate's `runner::LOCK`): held by `flock` while a runner lives.
pub const RUNNER_LOCK: &str = "lane.lock";

/// Whether a runner holds the lane's lock: the file opened (never made) and the lock asked for at once, let go at once.
#[must_use]
pub fn runner_lives(common: &Path) -> bool {
    std::fs::File::open(dir(common).join(RUNNER_LOCK)).is_ok_and(|f| {
        let free = flock(&f, "-n");
        // let go by `flock -u`, not the close: a child another thread forks holds a copy of the descriptor (461 T14)
        let _ = free && flock(&f, "-u");
        !free
    })
}

/// THE PHASE-2 BASE, ASKED IN ONE PLACE (461 T56, T64): whether `knob`, `HAND_IN_BASE`'s value, puts hand-ins on `origin/main`,
/// where every hand-in starts the runner (T12 Decision 6). T22's meaning: unset, empty or `origin` is phase 2; `clone` (and any word
/// T22's `l7r_shared::builder_pool::hand_in_base` refuses, whose hand-in starts nothing) is not. The Stop rule ([`holds`]) and
/// `make lane-wait` (the lane crate's `wake.rs`) both ask it, here because the guard reaches no gate crate; it asks T22's reader,
/// so one reading says the base everywhere. In code, not a make default: the Stop hook and `make lane-wait` never see a
/// `HAND_IN_BASE=` given on `make builder-done`'s command line.
#[must_use]
pub fn origin_base(knob: Option<&str>) -> bool {
    use crate::builder_pool::{hand_in_base, Base};
    matches!(hand_in_base(knob), Ok(Base::Origin))
}

/// What the lane under the git common directory `common` holds for its coordinator, said in a few words: its first open batch, else
/// its first waiting hand-in - in phase 1 only while the runner lives, from phase 2's base whether it lives or not ([`holds_at`]);
/// none where it holds neither. The base is this process's `HAND_IN_BASE`, read by [`origin_base`].
#[must_use]
pub fn holds(common: &Path) -> Option<String> {
    holds_at(
        common,
        origin_base(crate::env::opt("HAND_IN_BASE").as_deref()),
    )
}

/// [`holds`] on the base given, `origin` true from phase 2's base. In phase 1 a lane with no log holds nothing; from phase 2's a
/// hand-in whose runner never started may have left none, so the hand-ins are read all the same.
#[must_use]
pub fn holds_at(common: &Path, origin: bool) -> Option<String> {
    // GUARD_EDIT_OK: 461 T63 - the lane's states read through `lane_log`, the one reading the lane crate re-exports
    let lane = lines_of(&dir(common).join(FILE));
    if let Some(b) = batches(&lane).into_iter().find(Batch::open) {
        return Some(format!("batch {} is open", b.id));
    }
    if !origin && (lane.is_empty() || !runner_lives(common)) {
        return None;
    }
    let all = hand_ins(&lines_of(&common.join(POOL_LOG)));
    // no hand-in ever: no git spawned, a Stop of every phase-2 coordinator asks this
    if all.is_empty() {
        return None;
    }
    let refs = std::process::Command::new("git")
        .arg("-C")
        .arg(common)
        .args(["for-each-ref", "--format=%(objectname)", DONE_REFS])
        .output()
        .map(|o| String::from_utf8_lossy(&o.stdout).into_owned())
        .unwrap_or_default();
    let refs: BTreeSet<String> = refs.lines().map(str::to_owned).collect();
    waiting_unasked(&all, &refs, &lane).first().map(|h| {
        let short = h.commit.get(..10).unwrap_or(&h.commit);
        format!(
            "hand-in {} {} ({short}) waiting",
            h.feature,
            h.tasks.join(",")
        )
    })
}

#[cfg(test)]
mod tests;

#[cfg(test)]
mod holds_tests;
