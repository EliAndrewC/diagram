//! The plan gates (feature 449 T066): a plan's sections and blocks, what a plan owes, recording a verdict, the review bundle, the approach
//! gate, the engine-edit question - `l7r-gate plan <verb>`, and `scripts/plan_door.py`'s door.

pub mod plan;

use l7r_gate_core::{codeid, Reply};
use l7r_gate_tree::{checks, delta, stamp};
