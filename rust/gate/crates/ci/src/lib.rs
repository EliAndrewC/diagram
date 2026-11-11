//! The route and a gated push's conditions, the switches, the push's credential (feature 449 T064, T73): `l7r-gate ci`, `switches`,
//! `github-token`.

pub mod ci;

use l7r_gate_arbiter::arbiter;
use l7r_gate_core::{codeid, Reply};
use l7r_gate_tree::{delta, state};
