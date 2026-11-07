//! The homesteads (feature 444 T30): every household seated on its own ground while no way stands, then the track out chosen and
//! each household's way laid in the gaps (0246). Ported piece by piece behind the stage's Python door, which it replaces when whole
//! (T30 D1); until then nothing calls it but its tests.
//!
//! Research:
//!     the homesteads' stage - NONE: the stage's machinery; each rule's claim is at the unit that keeps it
#![cfg_attr(
    not(test),
    expect(
        dead_code,
        reason = "the stage's port, wired into STAGES when whole (feature 444 T30 D1)"
    )
)]

pub use crate::counts::Counts;

pub mod access;
pub mod bearing;
pub mod bundle;
pub mod dispersed;
pub mod fit;
pub mod fit_rules;
pub mod fixtures;
pub mod gap_ways;
pub mod ground;
pub mod grove_rounds;
pub mod grove_seat;
pub mod layout;
pub mod level;
pub mod lots;
pub mod passage;
pub mod place;
#[cfg(feature = "python")]
pub mod py;
#[cfg(feature = "python")]
pub mod py_seat;
pub mod row_seat;
pub mod rows;
pub mod standing;
pub mod track_out;
pub mod ways_judge;
pub mod wood;

#[cfg(test)]
mod access_tests;
#[cfg(test)]
mod dispersed_tests;
#[cfg(test)]
mod fit_rules_tests;
#[cfg(test)]
mod fit_tests;
#[cfg(test)]
mod fixtures_tests;
#[cfg(test)]
mod gap_ways_tests;
#[cfg(test)]
mod grove_seat_tests;
#[cfg(test)]
mod level_tests;
#[cfg(test)]
mod passage_tests;
#[cfg(test)]
mod place_tests;
#[cfg(test)]
mod row_seat_tests;
#[cfg(test)]
mod rows_tests;
#[cfg(test)]
mod standing_tests;
#[cfg(test)]
mod tests;
#[cfg(test)]
mod track_out_tests;
#[cfg(test)]
mod ways_judge_tests;
#[cfg(test)]
mod wood_tests;
