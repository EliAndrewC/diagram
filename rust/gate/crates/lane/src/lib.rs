//! The landing lane (feature 461 phase 2; plan D2, D8, D15): `l7r-gate lane`. T11 holds its command line ([`lane`], `make lane`)
//! and its log with the computed states of a hand-in and a batch ([`log`]); the runner (`runner.rs`, T12), the batch (`batch.rs`,
//! T14, run by `runner/run.rs`), the attribution and the wake-up build on them.

pub mod batch;
pub mod lane;
pub mod log;
pub mod runner;

pub use lane::cli;
