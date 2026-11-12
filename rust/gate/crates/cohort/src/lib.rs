//! The landing cohort and the push (feature 449 T067-T068): each seed's standing against main's engine, the seed report, the room table
//! (`l7r-gate cohort`); the push's checks and what each push gate judges (`push-checks`, `push-gate`). The Rust crates' checks
//! (`l7r-gate rust`) are their own crate, `crates/rustc` (T93). `l7r-gate speckit-todo` lives here beside the push that runs its `--check`
//! (feature 449 T118), the narrowest crate the binary already builds on; `l7r-gate close-check` beside the push that runs its `--push`
//! row, over the reasons in `reviews::closing` (feature 449 T127).

pub mod close_check;
pub mod cohort;
pub mod push;
pub mod speckit_todo;

use l7r_gate_core::{codeid, Reply};
use l7r_gate_plan::plan;
use l7r_gate_tree::{checks, delta, stamp};

#[cfg(test)]
use l7r_gate_core::{ci, record, write_executable};
