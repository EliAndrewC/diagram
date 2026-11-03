//! The sink's door to Python (feature 444 T26 D1): `stage_sink` takes what the thin Python gathered - the brook as the Python
//! list the plan holds, read only where the sink looks - and returns the records as plain Python values.
//!
//! Research:
//!     the seam - NONE: the extension's own machinery; each record's claims are at the Rust that makes it

use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};

use super::brook::Stations;
use super::{sink, SinkIn};
use crate::field::fan::Pt;

/// The plan's brook as Python holds it, a list of points, each read when the sink first looks at it.
struct PyStations<'a, 'py> {
    list: &'a Bound<'py, PyList>,
}

impl Stations for PyStations<'_, '_> {
    fn len(&self) -> usize {
        self.list.len()
    }
    fn at(&mut self, i: usize) -> Pt {
        self.list
            .get_item(i)
            .and_then(|p| p.extract::<Pt>())
            .unwrap_or((f64::NAN, f64::NAN))
    }
}

/// The sink stage (T26): Python's gathered inputs in, the records out; None where the field has no collector.
///
/// # Errors
/// `ValueError` carrying the refusal where no run the rules allow exists.
#[pyfunction]
#[expect(
    clippy::too_many_arguments,
    clippy::needless_pass_by_value,
    reason = "the stage's inputs, each a plan field Python gathered (D1); PyO3 hands Vecs from Python lists"
)]
pub fn stage_sink<'py>(
    py: Python<'py>,
    pond: bool,
    canvas: Pt,
    fall: Pt,
    flow_deg: f64,
    outline: Vec<Pt>,
    drain: Vec<Pt>,
    brook: Bound<'py, PyList>,
    brook_w: f64,
    taps: Vec<Pt>,
    resting: Vec<Vec<Pt>>,
    reed_ft: f64,
    join_trunk: f64,
) -> PyResult<Option<Bound<'py, PyDict>>> {
    let inp = SinkIn {
        pond,
        canvas,
        fall,
        flow_deg,
        outline,
        drain,
        brook_w,
        taps,
        resting,
        reed_ft,
        join_trunk,
    };
    let mut stations = PyStations { list: &brook };
    let Some(s) = sink(&inp, &mut stations).map_err(|e| PyValueError::new_err(e.to_string()))?
    else {
        return Ok(None);
    };
    let d = PyDict::new(py);
    d.set_item("form", s.form)?;
    d.set_item("run", s.run)?;
    d.set_item("to", s.to)?;
    d.set_item("pond", s.pond)?;
    d.set_item("reeds", s.reeds)?;
    d.set_item("confluence", s.confluence)?;
    d.set_item("brook_drawn", s.brook_drawn)?;
    d.set_item("counts", s.counts)?;
    Ok(Some(d))
}
