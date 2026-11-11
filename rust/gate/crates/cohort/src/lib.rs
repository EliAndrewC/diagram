//! The landing cohort and the push (feature 449 T067-T068): each seed's standing against main's engine, the seed report, the room table
//! (`l7r-gate cohort`); the push's checks and what each push gate judges (`push-checks`, `push-gate`). The Rust crates' checks
//! (`l7r-gate rust`) are their own crate, `crates/rustc` (T93).

pub mod cohort;
pub mod push;

use l7r_gate_core::{codeid, Reply};
use l7r_gate_plan::plan;
use l7r_gate_tree::{checks, delta, stamp};

#[cfg(test)]
use l7r_gate_core::{ci, record, write_executable};
