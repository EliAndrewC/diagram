//! The data files the page writer read or looked for, for the generation cache (feature 449 T150, the engine port's step 2; T221).
//!
//! WHY: a cached sheet is regenerated when a file it was drawn from changes (the page's stylesheet, script, the modal texts and the
//! question fragments its modals link, the map's notes), so `hand-sheet` and `compound` print every file noted here in their reply's
//! `reads`, and the pool's generation cache (`rust/gate/crates/pool`'s `cache`, T221) holds each in its read table.
//!
//! A MISS IS A READ (T221, from T219's derivation, assumption 3): a file the writer looked for and did not find is noted as one it
//! read, since the absence of a modal text or of a map's notes shaped the page as much as their text would have; the cache holds its
//! absence, and the file created later regenerates the sheet. Before T221 a path was noted only where it was a file that exists (the
//! deleted spy's `os.path.isfile`), and such a file created later left its sheet cached and stale.
//!
//! Research: the page's reads - NONE: bookkeeping for the generation cache, no map decision

use std::collections::BTreeSet;
use std::path::{Path, PathBuf};
use std::sync::{LazyLock, Mutex, PoisonError};

static READS: LazyLock<Mutex<BTreeSet<PathBuf>>> = LazyLock::new(|| Mutex::new(BTreeSet::new()));

/// `path` noted as read: a file, or a path looked for and not there (a miss is a read); a directory is no file the writer reads.
pub fn note(path: &Path) {
    if !path.is_dir() {
        READS
            .lock()
            .unwrap_or_else(PoisonError::into_inner)
            .insert(path.to_path_buf());
    }
}

/// `assets/<name>` noted as read: a content file the writer reads through the gate's crates (`content`, the glossary, the knobs).
pub fn asset(tree: &Path, name: &str) {
    note(&tree.join(crate::page::ASSETS).join(name));
}

/// Held by a test whose command takes the log: the tests run side by side in one process, and one run's [`take`] drained another's notes
/// (feature 449 T151: the hand sheet's test lost its sheet so, the sheet-page command's test taking the log meanwhile).
#[cfg(test)]
pub static TAKERS: Mutex<()> = Mutex::new(());

/// [`TAKERS`] held for the caller's run.
#[cfg(test)]
pub fn taker() -> std::sync::MutexGuard<'static, ()> {
    TAKERS.lock().unwrap_or_else(PoisonError::into_inner)
}

/// Every file noted so far, in order, the log emptied.
#[must_use]
pub fn take() -> Vec<PathBuf> {
    std::mem::take(&mut *READS.lock().unwrap_or_else(PoisonError::into_inner))
        .into_iter()
        .collect()
}

/// Whether `path` has been noted (and not yet taken): what a test asks, never draining another test's notes.
#[must_use]
pub fn noted(path: &Path) -> bool {
    READS
        .lock()
        .unwrap_or_else(PoisonError::into_inner)
        .contains(path)
}

#[cfg(test)]
mod tests {
    use super::{note, noted};

    /// A MISS IS A READ (feature 449 T221, T219's derivation, assumption 3): a file the writer looked for and did not find is noted as a
    /// file that exists is, so a looked-for file created later (a modal text a kind has none of yet, a map's notes) re-keys the sheet; a
    /// directory is no file the writer reads, and is not noted.
    #[test]
    fn a_file_and_a_missing_one_are_noted_and_a_directory_is_not() {
        let dir = l7r_shared::tempdir::TempDir::new("reads");
        let (here, gone) = (dir.path().join("here.css"), dir.path().join("gone.css"));
        std::fs::write(&here, "x").unwrap();
        note(&here);
        note(&gone);
        note(dir.path());
        assert_eq!(
            (noted(&here), noted(&gone), noted(dir.path())),
            (true, true, false)
        );
    }
}
