//! The hem's door to Python (feature 444 T28): `stage_hem` takes what the field handed on and the seat's ground, and returns the
//! dry plots, their grain and the room left as plain Python values.
//!
//! Research:
//!     the hem's door - NONE: the extension's own machinery; each record's claims are at the Rust that makes it

use pyo3::prelude::*;
use pyo3::types::PyDict;

use super::lay;
use crate::field::build::HemIn;
use crate::field::fan::Pt;

/// The hem stage (T28): the field's hem inputs and the settlement's ground in, the dry plots out.
#[pyfunction]
#[expect(
    clippy::too_many_arguments,
    reason = "the stage's inputs, each a plan field Python gathered (D1)"
)]
pub fn stage_hem(
    py: Python<'_>,
    line: Vec<Pt>,
    out: Pt,
    down: Pt,
    bounds: (f64, u32),
    seed: i64,
    ring: Vec<Pt>,
    water: Vec<(Pt, Pt, f64)>,
    keep: Vec<Vec<Pt>>,
) -> PyResult<Bound<'_, PyDict>> {
    let h = HemIn {
        line,
        out,
        down,
        bounds,
        seed,
    };
    let laid = lay(&h, &ring, &water, &keep);
    let d = PyDict::new(py);
    let dry: Vec<(Vec<Pt>, &str, f64, usize)> = laid
        .plots
        .iter()
        .map(|p| (p.poly.clone(), p.crop, p.theta, p.tract))
        .collect();
    d.set_item("dry", dry)?;
    d.set_item("grain", laid.grain)?;
    d.set_item("counts", laid.counts)?;
    Ok(d)
}
