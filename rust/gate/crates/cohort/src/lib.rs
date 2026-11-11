//! The landing cohort and the push (feature 449 T067-T068): each seed's standing against main's engine, the seed report, the room table
//! (`l7r-gate cohort`); the push's checks and what each push gate judges (`push-checks`, `push-gate`); the Rust crates' checks
//! (`l7r-gate rust`).

pub mod cohort;
pub mod push;
pub mod rustc;

use l7r_gate_core::{codeid, Reply};
use l7r_gate_plan::plan;
use l7r_gate_tree::{checks, delta, stamp, top};

#[cfg(test)]
use l7r_gate_core::{ci, record, write_executable};
