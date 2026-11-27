//! The landing lane (feature 461 phase 2; plan D2, D8, D15): `l7r-gate lane`. T11 holds its command line ([`lane`], `make lane`)
//! and its log with the computed states of a hand-in and a batch ([`log`]); the runner (`runner.rs`, T12), the batch (`batch.rs`,
//! T14, run by `runner/run.rs`), a red batch's attribution (`attribute.rs`, T15) and its repair entries (`repairs.rs`, T15), the
//! red-gate tripwire by task (`tripwire.rs`, T18); the wake-up is `wake.rs` (`make lane-wait`, T20).

pub mod attribute;
pub mod batch;
pub mod lane;
pub mod log;
pub mod repairs;
pub mod runner;
pub mod tripwire;
pub mod wake;

pub use lane::cli;
