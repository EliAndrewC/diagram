//! A plan's digests (451 T474): each block's and each task section's, and the stamp of the code that computes them.
//!
//! WHY A FILE OF ITS OWN: the digest index on disk (`history/index.rs`, 451 T465) keeps every version's digests for every process
//! after, so a parser that digests otherwise must never answer from an index another parser wrote. The index is stamped with the
//! hash of the code that computes a digest (`stamp`): this file and the files `SOURCES` names, compiled in, and the Unicode tables
//! std's `char` methods read - as the views cache is keyed by its code (451 T434, `rustc/kept/code.rs`). Kept apart from
//! `sections.rs`, whose other functions reach the plan template, so the set is closed: the test
//! `the_digests_reach_nothing_outside_their_hashed_sources` holds every file `SOURCES` names to reaching only std, `fancy_regex`
//! (its version and its own dependencies' pinned by `Cargo.lock`, hashed) and the other files it names.
//!
//! WHY NOT THE BINARY'S BUILD ID: the index lives in the common git directory, which the clone and every pool tree share, and each
//! tree's `l7r-gate` binary differs from the next; keyed by the binary, every rebuild and every switch between trees would drop
//! and rewrite the others' index (a re-index about 5 s, measured 2026-11-27, 477 versions), as the whole-binary key of the views
//! cache read all 1,504 Rust files again after every rebuild (451 T434). Keyed by this code, only an edit of it does.

use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_shared::plan_text::{blocks, task_sections};
use l7r_shared::sha256;

/// The files a digest is computed from, compiled in, by their paths from the tree's root.
pub(crate) const SOURCES: [(&str, &str); 5] = [
    (
        "rust/gate/crates/plan/src/plan/sections/digests.rs",
        include_str!("digests.rs"),
    ),
    (
        "rust/guard/shared/src/plan_text.rs",
        include_str!("../../../../../../guard/shared/src/plan_text.rs"),
    ),
    (
        "rust/guard/shared/src/regex.rs",
        include_str!("../../../../../../guard/shared/src/regex.rs"),
    ),
    (
        "rust/guard/shared/src/sha256.rs",
        include_str!("../../../../../../guard/shared/src/sha256.rs"),
    ),
    (
        "rust/Cargo.lock",
        include_str!("../../../../../../Cargo.lock"),
    ),
];

/// The hash of the code that computes a digest (`SOURCES`) and of the Unicode version its `char` methods read: an index stamped
/// with another was written by another parser.
pub(crate) fn stamp() -> String {
    static STAMP: LazyLock<String> = LazyLock::new(|| stamp_of(&SOURCES, char::UNICODE_VERSION));
    STAMP.clone()
}

pub(crate) fn stamp_of(sources: &[(&str, &str)], unicode: (u8, u8, u8)) -> String {
    let mut all = format!("unicode {unicode:?}\n").into_bytes();
    for (path, text) in sources {
        all.extend(format!("{path} {}\n", text.len()).into_bytes());
        all.extend(text.as_bytes());
    }
    sha256::hex(&all)
}

/// The line `make plan-archive` leaves where finished sections were (FR-044): out of every digest, so it owes no review.
static ARCHIVE_LINE: LazyLock<Regex> = LazyLock::new(|| {
    l7r_shared::regex::build(r"(?m)^<!-- plan-archive: [^\n]*? -->\n?")
        .unwrap_or_else(|e| unreachable!("{e}"))
});

pub(crate) fn digest(data: &[u8]) -> String {
    sha256::hex(data)
}

pub(crate) fn strip_archive(text: &str) -> String {
    ARCHIVE_LINE.replace_all(text, "").into_owned()
}

pub(crate) fn block_digest(text: &str) -> String {
    digest(strip_archive(text).as_bytes())
}

/// (key, digest, text) of each block and of each task's section of `plan`: what the digest index keeps a version by.
pub(crate) type Digested = (Vec<(String, String, String)>, Vec<(String, String, String)>);

/// The blocks' and the task sections' digests of `plan`, each beside its key and text.
pub(crate) fn of(plan: &str) -> Digested {
    let blocks = blocks(plan)
        .into_iter()
        .map(|(key, body, _)| (key, block_digest(&body), body))
        .collect();
    let sections = task_sections(plan)
        .into_iter()
        .map(|(task, section)| (task, digest(section.as_bytes()), section))
        .collect();
    (blocks, sections)
}

#[cfg(test)]
mod tests;
