//! THE SHEET AS REVIEWED, FOUND AGAIN IN GIT HISTORY (451 T214). A verdict written before T199 kept no copy of the sheet its review
//! read, so `make review-fixed` could not show the edit and owed the full round for a nitpick fixed in the notes: the cascade test's
//! round-trip sheet. The verdict's content key is a hash of the drawing and the notes ([`super::super::files_key`]), so the sheet as
//! reviewed is any version of the two that hashes to it: each committed version of either file, and the drawing as it reads now
//! (a generated compound's drawing is never committed, and a notes fix leaves it as it was). On the round-trip sheet, measured
//! 2026-11-24: the drawing as it reads now with the notes at 03cc1514d1 hash to its verdict's `9b7b9464d35cc002`.
//!
//! Research: the sheet as reviewed found in history - NONE: review bookkeeping, no map decision

use std::path::Path;

use l7r_gate_pool::walk;

use super::super::files_key;
use super::files;
use crate::record::repo::cat_blobs;

/// The versions of the sheet's files git holds, newest first: this many commits back at most (a sheet's notes move a few times a day
/// at the busiest, measured 2026-11-24: the round-trip sheet's 15 commits over seven weeks).
const DEPTH: &str = "200";

/// Find the sheet `on` as the review that wrote content key `at` read it - its files now in `folder`, or a version git holds - and
/// keep it in `kept`, as [`super::keep`] would have: whether it was found.
pub fn recover(clone: &Path, folder: &Path, on: &str, at: &str, kept: &Path) -> bool {
    // the sheet's own pool folder holds its history, wherever the review tree's copy of it is
    let pool = walk(clone);
    let pool = pool.folder(on).map_or(folder, |m| m.dir.as_path());
    let rel = pool.strip_prefix(clone).unwrap_or(pool);
    let names = files(on);
    let paths = names
        .clone()
        .map(|f| rel.join(f).to_string_lossy().into_owned());
    let log = super::super::super::git(
        clone,
        &[
            "log",
            "--format=%H",
            "-n",
            DEPTH,
            "--",
            &paths[0],
            &paths[1],
        ],
    )
    .unwrap_or_default();
    let objects: Vec<String> = log
        .lines()
        .filter(|c| !c.is_empty())
        .flat_map(|c| paths.iter().map(move |p| format!("{c}:{p}")))
        .collect();
    let blobs = cat_blobs(clone, &objects);
    let now = |f: &str| std::fs::read(folder.join(f)).unwrap_or_default();
    let (mut svgs, mut notes) = (vec![now(&names[0])], vec![now(&names[1])]);
    for pair in blobs.chunks(2) {
        svgs.push(pair[0].clone().into_bytes());
        notes.push(pair[1].clone().into_bytes());
    }
    for v in [&mut svgs, &mut notes] {
        v.sort();
        v.dedup();
    }
    let found = svgs.iter().find_map(|s| {
        notes
            .iter()
            .find(|n| files_key(on, s, n) == at)
            .map(|n| (s, n))
    });
    found.is_some_and(|(svg, note)| {
        let _ = std::fs::remove_dir_all(kept);
        std::fs::create_dir_all(kept)
            .and_then(|()| std::fs::write(kept.join(&names[0]), svg))
            .and_then(|()| std::fs::write(kept.join(&names[1]), note))
            .is_ok()
    })
}
