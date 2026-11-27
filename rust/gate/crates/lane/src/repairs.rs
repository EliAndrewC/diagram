//! THE REPAIR ENTRIES (feature 461 T15, plan D7; data-model.md, "A repair entry"): `l7r-lane/repairs.jsonl` in the git common
//! directory, one JSON line an ejected change - or, for a whole batch ejected as unplaced, one line for every change of it - which
//! `make queue` and `make builder-next` hand to a fresh builder before `queue.txt`'s entries (T16, `builder_queue/repairs.rs`). The
//! lane is its one writer (the runner, under `l7r-lane/lane.lock`), so the next id is read and written without a lock of its own.
//!
//! THE LINE, data-model.md's: `utc`, `repair` (`r<n>`, n one past the file's highest), `feature` (the spec directory's name,
//! `461-landing-lane`, as the example writes it - not the done ref's `461`), `tasks`, `kind` (`fix`, or `integrate` for a green set whose push failed twice, 461 T19),
//! `ejected`, `batch`, `why`, `units` and `attempt` (the attempt file's path). `ejected` is ALWAYS A LIST of the ejected done commits'
//! full shas, one for a change placed by the record, every change of the batch for an `unplaced` one (data-model.md's example showed
//! one sha as a string; a list is the one form both cases share, so T16 reads one shape - the data model's example amended to match).
//!
//! FILED ONCE: an entry of the same batch and the same `ejected` set is not written again - its id is returned - so a runner killed
//! between the entry and its `eject` lines files no second repair when the batch is resumed. Why the entry is written before the
//! `eject` lines: a kill between them leaves an entry the lane log does not yet name, which the resume answers with the same id; the
//! other order would leave an ejection naming a repair no file holds.

use std::io::Write as _;
use std::path::{Path, PathBuf};

use serde_json::{json, Value};

/// The repairs' file, in the lane's directory.
pub const FILE: &str = "repairs.jsonl";

/// The file's path under the git common directory `common`.
#[must_use]
pub fn path(common: &Path) -> PathBuf {
    common.join(crate::log::DIR).join(FILE)
}

/// A repair entry to file (the module's doc).
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Entry {
    pub feature: String,
    pub tasks: Vec<String>,
    pub kind: String,
    pub ejected: Vec<String>,
    pub batch: String,
    pub why: String,
    pub units: Vec<String>,
    pub attempt: String,
}

/// Every entry of the file, in the order filed.
#[must_use]
pub fn read(common: &Path) -> Vec<Value> {
    crate::log::lines_of(&path(common))
}

/// `e` filed at `now`: its id, a new one or the id of the same batch's entry for the same changes (the module's doc).
///
/// # Errors
///
/// The directory or the file that cannot be written, as a line naming it.
pub fn file(common: &Path, now: &str, e: &Entry) -> Result<String, String> {
    let all = read(common);
    let mut wanted = e.ejected.clone();
    wanted.sort();
    let same = all.iter().find(|l| {
        let mut had: Vec<String> = l["ejected"]
            .as_array()
            .into_iter()
            .flatten()
            .filter_map(Value::as_str)
            .map(str::to_owned)
            .collect();
        had.sort();
        l["batch"] == e.batch.as_str() && had == wanted
    });
    if let Some(id) = same.and_then(|l| l["repair"].as_str()) {
        return Ok(id.to_owned());
    }
    let n = all
        .iter()
        .filter_map(|l| l["repair"].as_str()?.strip_prefix('r')?.parse::<u64>().ok())
        .max()
        .unwrap_or(0);
    let id = format!("r{}", n + 1);
    let line = json!({
        "utc": now, "repair": id, "feature": e.feature, "tasks": e.tasks, "kind": e.kind, "ejected": e.ejected,
        "batch": e.batch, "why": e.why, "units": e.units, "attempt": e.attempt,
    });
    let file = path(common);
    std::fs::create_dir_all(common.join(crate::log::DIR))
        .and_then(|()| {
            std::fs::OpenOptions::new()
                .create(true)
                .append(true)
                .open(&file)
        })
        .and_then(|mut f| f.write_all(format!("{line}\n").as_bytes()))
        .map_err(|e| format!("lane: {}: {e}", file.display()))?;
    Ok(id)
}

#[cfg(test)]
mod tests;
