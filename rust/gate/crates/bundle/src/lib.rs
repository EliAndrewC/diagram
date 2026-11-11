//! The check bundles (feature 449 T88): `record check-bundle`, `record modal-bundle`, the earlier rounds; the round marks the arbiter's
//! bundle reads; and `owed-door`, Python's door to the owed tools (T87).

/// The record's tools held here, beside those of the owed crate and the core.
pub mod record {
    pub use l7r_gate_owed::record::*;
    pub mod bundle;
}

/// The round marks: what each review round of a unit left (`arbiter bundle` reads them; the check bundles too).
pub mod arbiter {
    pub mod bundle {
        pub mod marks;
    }
}

pub mod owed_door;

#[cfg(test)]
use l7r_gate_core::checks;
use l7r_gate_core::{checks_door, difflib, measure, Reply};
