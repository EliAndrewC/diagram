//! The round arbiter (feature 449 T86, T88): its rulings and tripwires (`l7r-gate arbiter ...`), its bundle (`arbiter bundle`), and
//! `checks-close`, what `make check-closed` runs (its door `checks-door` left with its last caller, feature 449 T132).

pub mod arbiter;
pub mod checks_door;

use l7r_gate_bundle::record;
use l7r_gate_claims::claims;
use l7r_gate_cohort::cohort;
#[cfg(test)]
use l7r_gate_core::checks;
use l7r_gate_core::Reply;
use l7r_gate_plan::plan;
use l7r_gate_reviews::reviews;
