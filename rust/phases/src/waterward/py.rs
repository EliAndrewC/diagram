//! The waterward fringe's door to Python (feature 444 T29): `stage_waterward` takes the dikes' rings and notches and returns the
//! water-facing flanks and their strips as plain Python values.
//!
//! Research:
//!     the fringe's door - NONE: the extension's own machinery; each record's claims are at the Rust that makes it

use pyo3::prelude::*;
use pyo3::types::PyDict;

use super::fringe;
use crate::field::fan::Pt;

/// The waterward stage (T29): the dikes in, the flanks facing the water and their strips out.
#[pyfunction]
#[expect(
    clippy::too_many_arguments,
    reason = "the stage's inputs, each a plan field Python gathered (D1)"
)]
pub fn stage_waterward(
    py: Python<'_>,
    dikes: Vec<(Vec<Pt>, Vec<Pt>)>,
    cut: f64,
    cut_hw: f64,
    depth: f64,
    canvas: Pt,
    fall: Pt,
    seat_out: Option<Pt>,
) -> PyResult<Bound<'_, PyDict>> {
    let f = fringe(&dikes, cut, cut_hw, depth, canvas, fall, seat_out);
    let d = PyDict::new(py);
    d.set_item(
        "flanks",
        f.flanks.iter().map(char::to_string).collect::<Vec<_>>(),
    )?;
    d.set_item("strips", f.strips)?;
    d.set_item("counts", f.counts)?;
    Ok(d)
}
