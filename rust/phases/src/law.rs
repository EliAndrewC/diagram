//! The lane law (feature 444 T30 D1): every rule a lane keeps, each one predicate its placer and its test both ask - ported rule
//! by rule as the stages that ask them are (`hamletgen/ways/law/`, `law_water.py`). Until the homesteads' door wires them, nothing
//! calls them but their tests.
//!
//! Research:
//!     the lane law - NONE: the rules' machinery; each rule's claim is at the unit that keeps it
#![cfg_attr(
    not(test),
    expect(
        dead_code,
        reason = "the stage's port, wired into STAGES when whole (feature 444 T30 D1)"
    )
)]

pub use crate::counts::Counts;

pub mod ground;
pub mod meet;
pub mod routes;
pub mod rules;
pub mod water;

#[cfg(test)]
mod ground_tests;
#[cfg(test)]
mod meet_tests;
#[cfg(test)]
mod routes_tests;
#[cfg(test)]
mod tests;
#[cfg(test)]
mod water_tests;
