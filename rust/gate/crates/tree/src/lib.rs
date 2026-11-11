//! The gate's view of the tree (feature 449 T92): the green-gate stamps, the delta and the engine paths, the verification state, the
//! hashing of what runs, the coverage exemptions, the host-wide lock, the time ratchets, and which retained check a change starts.

pub mod checks;
pub mod delta;
pub mod exempt;
pub mod hashing;
pub mod lock;
pub mod stamp;
pub mod state;

/// The time ratchets (`l7r-gate measure ratchet`, `dev/ratchets.json`), beside the cost tools' shared helpers.
pub mod measure {
    pub use l7r_gate_core::measure::*;
    pub mod ratchet;
}

pub use l7r_gate_core::{codeid, Reply};

/// The repository the command was started in, or `.` outside one.
#[must_use]
pub fn top() -> std::path::PathBuf {
    stamp::toplevel().unwrap_or(std::path::PathBuf::from("."))
}
