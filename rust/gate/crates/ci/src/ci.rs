//! What a push asks of the gate: the route, a gated push's local conditions, and the iteration switches (feature 449 T064, T73). The
//! remote path that was here was deleted, not ported (FR-001a; the GM, 2026-11-09: "Let's delete rather than port our tooling which
//! runs our tests remotely on AWS."); its history is in git.

pub mod config;
pub mod features;
pub mod gated;
pub mod switches;
pub mod via_make;

#[cfg(test)]
pub use l7r_gate_core::ci::fixtures;
