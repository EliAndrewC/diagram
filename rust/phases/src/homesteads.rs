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

pub mod bearing;
pub mod bundle;
pub mod fit;
pub mod fixtures;
pub mod ground;
pub mod layout;
pub mod lots;
pub mod place;
pub mod track;
pub mod wood;

#[cfg(test)]
mod fit_tests;
#[cfg(test)]
mod fixtures_tests;
#[cfg(test)]
mod place_tests;
#[cfg(test)]
mod tests;
#[cfg(test)]
mod track_tests;
#[cfg(test)]
mod wood_tests;
