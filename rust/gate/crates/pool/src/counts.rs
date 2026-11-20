//! The walk's counted work, by tree and kind (`specs/449-rust-codebase/derivations/T219-pipeline.md`, "The budget by counted kind").
//!
//! COMPILED OUT BY DEFAULT (as `rust/phases`' and `rust/mode_a`'s counters, 444 FR-012; the GM 2026-11-07: "We should probably run with
//! counters compiled out by default"): [`Counts::add`] counts only in a build with the crate's `counters` feature, and every other
//! build's [`Counts`] holds nothing. Each count is charged to the tree whose walk did it; the once-a-run terms (the types declaration
//! read and parsed) to `pool`, the tree whose maps need them, as the derivation charges them.
//!
//! `engine_run` is not the derivation's: an engine run is its own stage's work, counted there; it is counted here so a run that drew a map
//! says so beside its counts (the all-hit run the budget holds draws none).
//!
//! Research: plumbing - NONE: it counts, and decides nothing about a map

#[cfg(feature = "counters")]
use std::collections::BTreeMap;

/// The derivation's counted kinds, in its order: the walk's and the index's (T220), then the generation key's, the read table's and the
/// cache's (T221), then the kinds only a change does (`## The work a change adds`), each 0 on the all-hit run the budget counts.
#[cfg(feature = "counters")]
pub const KINDS: [&str; 26] = [
    "dir_list",
    "dir_entry",
    "classify",
    "folder_kind",
    "tier_lookup",
    "tracked_lookup",
    "file_read",
    "lock",
    "parse_block",
    "engine_id",
    "index_row",
    "meta_read",
    "id_compare",
    "record",
    "stat",
    "stat_compare",
    "list_read",
    "hash_block",
    "digest_compare",
    "entry_remove",
    "key_fold",
    "row_update",
    "row_write",
    "rename",
    "link",
    "engine_run",
];

/// The counts of one walk: by (tree, kind) in a counting build, nothing in any other.
#[derive(Clone, Debug, Default, PartialEq, Eq)]
pub struct Counts {
    #[cfg(feature = "counters")]
    by: BTreeMap<(&'static str, &'static str), u64>,
}

impl Counts {
    /// `n` operations of `kind` done for `tree`.
    pub fn add(&mut self, tree: &'static str, kind: &'static str, n: usize) {
        #[cfg(feature = "counters")]
        {
            *self.by.entry((tree, kind)).or_default() += n as u64;
        }
        #[cfg(not(feature = "counters"))]
        let _ = (tree, kind, n);
    }

    /// Each kind's count for `tree`, every kind of [`KINDS`] named (a kind not done is 0).
    #[cfg(feature = "counters")]
    #[must_use]
    pub fn of(&self, tree: &str) -> Vec<(&'static str, u64)> {
        KINDS
            .iter()
            .map(|k| {
                let n = self
                    .by
                    .iter()
                    .filter(|((t, kind), _)| *t == tree && kind == k)
                    .map(|(_, n)| *n)
                    .sum();
                (*k, n)
            })
            .collect()
    }
}

#[cfg(test)]
mod tests;
