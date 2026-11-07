//! The water frame's door (feature 444 T19): its two functions as Python calls them, each handing its arguments on.
//!
//! Research:
//!     the door - NONE: plumbing, the frame's inputs and its plan

use std::collections::HashMap;

use pyo3::prelude::*;

use super::KnobIn;

/// `water_frame::admitted_falls`, as Python calls it.
#[pyfunction]
#[must_use]
pub fn admitted_falls(windward: String, cardinal: bool) -> Vec<f64> {
    super::admitted_falls(windward, cardinal)
}

/// `water_frame::stage_water_frame`, as Python calls it.
#[pyfunction]
#[must_use]
pub fn stage_water_frame(
    seed: i64,
    windward: String,
    cardinal: bool,
    fall_pinned: bool,
    forms: Vec<String>,
    knobs: Vec<KnobIn>,
) -> (Option<f64>, Vec<Option<u32>>, HashMap<String, u64>) {
    super::stage_water_frame(seed, windward, cardinal, fall_pinned, forms, knobs)
}
