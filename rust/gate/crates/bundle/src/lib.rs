//! The check bundles (feature 449 T88): `record check-bundle`, `record modal-bundle`, the earlier rounds; and the round marks the arbiter's
//! bundle reads. `owed-door`, Python's door to the owed tools (T87), left with its last caller, `entry_owed.py` (T149).

/// The record's tools held here, beside those of the owed crate and the core.
pub mod record {
    pub use l7r_gate_owed::record::*;
    pub mod bundle;
    pub mod helpers;
}

/// The round marks: what each review round of a unit left (`arbiter bundle` reads them; the check bundles too).
pub mod arbiter {
    pub mod bundle {
        pub mod marks;
    }
}

#[cfg(test)]
use l7r_gate_core::checks;
use l7r_gate_core::{difflib, measure, Reply};
