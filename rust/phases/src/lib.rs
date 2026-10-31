//! The rebuilt hamlet phases (feature 444 FR-010, FR-017): each a function here, its stage a thin Python function calling it.
//!
//! Research:
//!     phases module - NONE: the extension's own machinery; each phase carries its own claims

mod comb;
mod pyrand;
mod water_frame;

use pyo3::prelude::*;

/// The module Python imports as `l7r_phases`.
///
/// # Errors
/// When a function cannot be added to the module.
#[pymodule]
fn l7r_phases(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(water_frame::stage_water_frame, m)?)?;
    m.add_function(wrap_pyfunction!(water_frame::admitted_falls, m)?)?;
    Ok(())
}
