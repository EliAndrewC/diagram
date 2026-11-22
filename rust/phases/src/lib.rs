//! The rebuilt hamlet phases (feature 444 FR-010, FR-017): each a function here, its stage a thin Python function calling it.
//!
//! Research:
//!     phases module - NONE: the extension's own machinery; each phase carries its own claims

mod counts;
mod course;
pub mod driver;
mod field;
mod hem;
mod pyrand;
mod seat;
mod sink;
pub mod spec_check;
mod water_frame;
mod waterward;
