//! The ways (feature 444 T30): the track out of the frame, its dry exit, and the lane router with the clearance tests every way
//! asks - shared by the homesteads' track and households' ways and, later, the web and the track stages (T30 D1). Ported behind
//! the homesteads' Python door, which it replaces when whole; until then nothing calls it but its tests.
//!
//! Research:
//!     the ways - NONE: the ways' machinery; each rule's claim is at the unit that keeps it
#![cfg_attr(
    not(test),
    expect(
        dead_code,
        reason = "the stage's port, wired into STAGES when whole (feature 444 T30 D1)"
    )
)]

pub use crate::counts::Counts;

pub mod dry_exit;
pub mod gateway;
pub mod route;
pub mod squaring;
pub mod through;
pub mod track;

#[cfg(test)]
mod dry_exit_tests;
#[cfg(test)]
mod gateway_tests;
#[cfg(test)]
mod route_tests;
#[cfg(test)]
mod squaring_tests;
#[cfg(test)]
mod through_tests;
#[cfg(test)]
mod track_tests;
