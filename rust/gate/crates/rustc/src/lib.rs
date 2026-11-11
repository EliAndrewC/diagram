//! The Rust crates' checks (`l7r-gate rust`, feature 449 T93): their own crate over core and tree, so the program that runs a crate's
//! tests is rebuilt only when what it builds from changes, and their own binary `l7r-rust`, which `scripts/gates/l7r-gate.sh` runs for
//! the `rust` verb.

pub mod rustc;

use l7r_gate_core::{checks, plan, Reply};
use l7r_gate_tree::{stamp, top};

#[cfg(test)]
use l7r_gate_core::write_executable;
