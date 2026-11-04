//! The seat's door to Python (feature 444 T27 D1): `stage_seat` takes what the thin Python gathered and returns the seat's frames,
//! the fords and the gapped streams as plain Python values.
//!
//! Research:
//!     the seat's door - NONE: the extension's own machinery; each record's claims are at the Rust that makes it

use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};

use super::{seat, SeatIn, Wall};
use crate::field::fan::Pt;

/// The seat stage (T27): Python's gathered inputs in, the frames, the fords and the streams gapped at them out.
///
/// # Errors
/// `ValueError` carrying the refusal where no margin keeps every rule.
#[pyfunction]
#[expect(
    clippy::too_many_arguments,
    reason = "the stage's inputs, each a plan field Python gathered (D1)"
)]
pub fn stage_seat(
    py: Python<'_>,
    canvas: Pt,
    fall: Pt,
    wind: Pt,
    back_min_dot: f64,
    outline: Vec<Pt>,
    band: Pt,
    plots: Vec<Vec<Pt>>,
    toe: Vec<Pt>,
    reeds: Vec<Vec<Pt>>,
    brook: Vec<Pt>,
    walls: Vec<Wall>,
    lines: Vec<(Pt, Pt)>,
    streams: Vec<Vec<Pt>>,
    ford: (f64, f64, f64),
) -> PyResult<Bound<'_, PyDict>> {
    let inp = SeatIn {
        canvas,
        fall,
        wind,
        back_min_dot,
        outline,
        band,
        plots,
        toe,
        reeds,
        brook,
        walls,
        lines,
        streams,
        ford,
    };
    let s = seat(&inp).map_err(|e| PyValueError::new_err(e.to_string()))?;
    let frames = PyList::empty(py);
    for f in &s.frames {
        let d = PyDict::new(py);
        d.set_item("cx", f.center.0)?;
        d.set_item("cy", f.center.1)?;
        d.set_item("along", f.along)?;
        d.set_item("out", f.out)?;
        d.set_item("lat", f.band.0)?;
        d.set_item("dep", f.band.1)?;
        d.set_item("anchor", f.anchor)?;
        d.set_item("offwind", f.offwind)?;
        frames.append(d)?;
    }
    let d = PyDict::new(py);
    d.set_item("frames", frames)?;
    d.set_item("fords", s.fords)?;
    d.set_item("stream_segs", s.stream_segs)?;
    d.set_item("counts", s.counts)?;
    Ok(d)
}
