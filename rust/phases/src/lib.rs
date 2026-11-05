//! The rebuilt hamlet phases (feature 444 FR-010, FR-017): each a function here, its stage a thin Python function calling it.
//!
//! Research:
//!     phases module - NONE: the extension's own machinery; each phase carries its own claims

mod counts;
mod course;
mod field;
mod hem;
mod homesteads;
mod law;
mod pyrand;
mod seat;
mod sink;
mod track;
mod water_frame;
mod waterward;
mod ways;

use pyo3::prelude::*;

/// The module Python imports as `l7r_phases`.
///
/// # Errors
/// When a function cannot be added to the module.
#[pymodule]
fn l7r_phases(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(water_frame::stage_water_frame, m)?)?;
    m.add_function(wrap_pyfunction!(water_frame::admitted_falls, m)?)?;
    m.add_function(wrap_pyfunction!(field::py::stage_field, m)?)?;
    m.add_function(wrap_pyfunction!(field::py::roll_knob, m)?)?;
    m.add_function(wrap_pyfunction!(field::py::stage_polder, m)?)?;
    m.add_function(wrap_pyfunction!(field::py::settle_runs, m)?)?;
    m.add_function(wrap_pyfunction!(field::py::rounded_pond, m)?)?;
    m.add_function(wrap_pyfunction!(sink::py::stage_sink, m)?)?;
    m.add_function(wrap_pyfunction!(seat::py::stage_seat, m)?)?;
    m.add_function(wrap_pyfunction!(hem::py::stage_hem, m)?)?;
    m.add_function(wrap_pyfunction!(waterward::py::stage_waterward, m)?)?;
    m.add_function(wrap_pyfunction!(waterward::py::water_flanks, m)?)?;
    m.add_function(wrap_pyfunction!(homesteads::py::track_out, m)?)?;
    m.add_function(wrap_pyfunction!(homesteads::py::households_ways, m)?)?;
    m.add_function(wrap_pyfunction!(homesteads::py_seat::seat_households, m)?)?;
    m.add_function(wrap_pyfunction!(homesteads::py_seat::seat_scattered, m)?)?;
    m.add_function(wrap_pyfunction!(homesteads::py_seat::seat_rows, m)?)?;
    m.add_function(wrap_pyfunction!(track::py::row_road_runs, m)?)?;
    Ok(())
}
