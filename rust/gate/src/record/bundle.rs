//! The check bundles (feature 449 T88): `record check-bundle` (`check.rs`, `parts.rs`, `keys.rs`, `owed.rs`), `record modal-bundle` (`modal.rs`, `depiction.rs`), the earlier rounds (`earlier.rs`); their shared helpers and the runner of `scripts/bundle_door.py` are `l7r_gate_core::record::bundle` (T92).

pub use l7r_gate_core::record::bundle::*;

pub(crate) mod check;
pub(crate) mod depiction;
pub(crate) mod earlier;
mod keys;
pub(crate) mod modal;
pub(crate) mod owed;
mod parts;
