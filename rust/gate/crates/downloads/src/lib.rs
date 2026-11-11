//! The download list and the access tags (feature 449 T80-T81): `l7r-gate record downloads ...`, `record access-tags ...` - what the
//! research record still has to fetch, and how open each cited source is.

/// The record's tools held here, beside the shared record helpers of the core.
pub mod record {
    pub use l7r_gate_core::record::*;
    pub mod access_tags;
    pub mod downloads;
}

use l7r_gate_core::{checks, cohort, difflib, logs, measure, Reply};
#[cfg(test)]
use l7r_gate_core::write_executable;
