//! What a delta owes the record checks and what answered them (feature 449 T87): `record record-owed`, `modal-owed`,
//! `translation-owed`, `modal-triage`; and the leaves Python reaches through a verb (`edit-route`, `fragments`, `moved-only`,
//! `americanize`).

/// The record's tools held here, beside the shared record helpers of the core.
pub mod record {
    pub use l7r_gate_core::record::*;
    pub mod leaves;
    pub mod modals;
    pub mod owed;
    pub mod translation;
    pub mod triage;
}

use l7r_gate_core::{checks, checks_door, logs, Reply};
