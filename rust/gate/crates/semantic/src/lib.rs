//! The research search (feature 449 T138, phase 4's S4 under `ask:449-phase4-slices`): `scripts/record/semantic_index.py` and
//! `research_search.py` ported, wired, and deleted in the same cut.
//!
//! WHY (the GM, 2026-10-29, `specs/447-semantic-index/request.md`): a text search finds a term and misses the same idea in other words or
//! another language, so a question is answered by meaning as well - each passage of the record's pages and the archive's texts is a BGE-M3
//! vector, and a question finds the passages nearest it; `research_search` runs the meaning search and the text search in one call (feature
//! 447 amendment 3: each found sources the other missed).
//!
//! The round arbiter's ruling `ask:449-phase4-slices` Q11: "a Rust embedder runs the same BGE-M3 weights (fastembed-rs or ort over the same
//! ONNX) against the stored index. FR-002 holds the result lists (ids and order) on recorded queries, not the float bytes." The embedder is
//! the `l7r-embed` program ([`embed`]); the index the Python stored is read and updated as it was ([`npz`], [`index`]).
//!
//! [`text`] reads a page as the index cut it, [`corpus`] lists the passages by shard, [`index`] builds, finds and commits, [`rank`] orders
//! by similarity, [`search`] is `research_search`, [`cli`] the command lines.

pub mod cli;
pub mod corpus;
pub mod embed;
pub mod index;
pub mod npz;
pub mod rank;
pub mod search;
pub mod text;

pub use l7r_gate_core::Reply;

/// What failed, in words (the Python's traceback; its text is not an output FR-002 binds, `ask:449-usage-text`).
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Error(pub String);

impl std::fmt::Display for Error {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.write_str(&self.0)
    }
}

pub type Result<T> = std::result::Result<T, Error>;

/// `semantic_index.py`'s constants: the model's name in each passage's fingerprint, its folder under the index, the vectors' length,
/// the index's folder in the archive's working copy, the model cache under the sources home, and a record shard's questions.
pub const MODEL: &str = "Xenova/bge-m3-int8";
pub const MODEL_DIR: &str = "bge-m3-int8";
pub const DIM: usize = 1024;
pub const INDEX_DIR: &str = "semantic-index";
pub const CACHE: &str = "model-cache";
/// A few hundred words of English; a CJK passage is cut at the same length (the trial measured 900 against 1,800: the same characters a
/// second).
pub const PASSAGE_CHARS: usize = 900;
pub const RECORD_SHARD: i64 = 100;
pub const QUESTIONS: &str = "research/questions";

/// Where the index lives in the archive's working copy `archive_dir`.
#[must_use]
pub fn index_dir(archive_dir: &std::path::Path) -> std::path::PathBuf {
    archive_dir.join(INDEX_DIR).join(MODEL_DIR)
}

/// `seq[:k]`'s length, as Python slices: a negative `k` counts from the end.
#[must_use]
pub fn head(len: usize, k: i64) -> usize {
    let len_i = i64::try_from(len).unwrap_or(i64::MAX);
    let n = if k < 0 {
        (len_i + k).max(0)
    } else {
        k.min(len_i)
    };
    usize::try_from(n).unwrap_or(0)
}

#[cfg(test)]
pub(crate) mod testkit;

#[cfg(test)]
mod tests;
