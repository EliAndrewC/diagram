//! ONE HAMLET SPEC ROLLED AND JUDGED (feature 449 T252): `hamlet --check <spec>...`, the reference step of `make maps`' hamlet row. A
//! single `make hamlet` roll never asks the finished map's rules (a roll a stage refused is an error and writes no map, 449 T426); the
//! cohort asks them of each seed (`hamlet --cohort`). This asks them of a pool spec: a stage's error, each rule the map breaks, one
//! problem each, and writes nothing.
//!
//! Research:
//!     the spec check - NONE: plumbing over the driver's roll and its rule check, deciding nothing about a place

use crate::driver::{check, roll, spec, Refused};

/// Every problem of the hamlet `text` specifies: none is a clean roll.
#[must_use]
pub fn problems(text: &str) -> Vec<String> {
    match spec::parse(text) {
        Err(e) => vec![format!("its spec does not parse: {e}")],
        Ok(s) => listed(roll(&s).map(|r| {
            let broke = check::check(&r);
            (r.refusals, broke)
        })),
    }
}

/// A roll's outcome as problems: its stage's error, or each refusal then each broken rule.
#[must_use]
pub fn listed(rolled: Result<(Vec<String>, Vec<String>), Refused>) -> Vec<String> {
    match rolled {
        Err(e) => vec![format!("FAILED: {e}")],
        Ok((refusals, broke)) => refusals
            .iter()
            .map(|w| format!("REFUSED: {w}"))
            .chain(broke.iter().map(|b| format!("BROKE: {b}")))
            .collect(),
    }
}

#[cfg(test)]
mod tests;
