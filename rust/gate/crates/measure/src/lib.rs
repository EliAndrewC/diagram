//! What things cost (feature 449 T75): `l7r-gate measure figures | gatecost | gate-costs | ratchet | probe | ...`; and the gate's first
//! phase and its tree check, `l7r-gate preflight` (T071).

pub mod measure;
pub mod preflight;

use l7r_gate_cohort::{cohort, push};
#[cfg(test)]
use l7r_gate_core::write_executable;
use l7r_gate_core::{codeid, plan, Reply};
use l7r_gate_tree::{checks, stamp};
