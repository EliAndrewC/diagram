//! The plan gates (feature 449 T066): a plan's sections and blocks, what a plan owes, recording a verdict, the review bundle, the approach
//! gate, the engine-edit question - `l7r-gate plan <verb>`; `make tick` and `make task-start` ask it in process (feature 449 T131).

pub mod plan;

use l7r_gate_core::{codeid, Reply};
use l7r_gate_tree::{checks, delta, stamp};
