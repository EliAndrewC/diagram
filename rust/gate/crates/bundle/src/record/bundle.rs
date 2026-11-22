//! The check bundles (feature 449 T88): `record check-bundle` (`check.rs`, `parts.rs`, `keys.rs`, `owed.rs`), `record modal-bundle` (`modal.rs`, `depiction.rs`), the earlier rounds (`earlier.rs`); their shared helpers are `l7r_gate_core::record::bundle` (T92; its runner of `scripts/bundle_door.py` left with its last verb, feature 449 T158).

pub use l7r_gate_core::record::bundle::*;

pub mod check;
pub mod depiction;
pub mod earlier;
mod keys;
pub mod modal;
pub mod owed;
mod parts;
