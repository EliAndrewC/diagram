//! The text checks and the spec lint (feature 449 T065-T066): `l7r-gate check <name> ...`, each one module that records its run.

pub mod checks;

/// The record's tools these checks read: the access tags, and the shared readers.
mod record {
    pub use l7r_gate_downloads::record::*;
}

use l7r_gate_core::Reply;
use l7r_gate_tree::{measure, stamp};
