//! The data files the page writer read, for the generation cache (feature 449 T150, the engine port's step 2).
//!
//! WHY: `gencache.record` learns a pool generator's data files by spying on Python's `open()` (spec 187 D3: the page's stylesheet, script
//! and the question fragments its modals link are what re-keys a cached sheet when they change). Since T150 a sheet's page is written by
//! `l7r-mode-a sheet-page`, a process the spy cannot see, so the command lists here every file it read and `interactive/sheet.py`'s
//! `write_sheet_page` opens each for reading in the generator's process - the dependency record the Python writer left, kept (each pool
//! generator's recorded files at HEAD measured against the wired tree's, `specs/449-rust-codebase` T150).
//!
//! Research: the page's reads - NONE: bookkeeping for the generation cache, no map decision

use std::collections::BTreeSet;
use std::path::{Path, PathBuf};
use std::sync::{LazyLock, Mutex, PoisonError};

static READS: LazyLock<Mutex<BTreeSet<PathBuf>>> = LazyLock::new(|| Mutex::new(BTreeSet::new()));

/// `path` noted as read, where it is a file (the spy recorded a read of a file only: `os.path.isfile`).
pub fn note(path: &Path) {
    if path.is_file() {
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

    #[test]
    fn a_file_is_noted_and_a_missing_one_is_not() {
        let dir = l7r_guard::shared::tempdir::TempDir::new("reads");
        let (here, gone) = (dir.path().join("here.css"), dir.path().join("gone.css"));
        std::fs::write(&here, "x").unwrap();
        note(&here);
        note(&gone);
        note(dir.path());
        assert_eq!(
            (noted(&here), noted(&gone), noted(dir.path())),
            (true, false, false)
        );
    }
}
