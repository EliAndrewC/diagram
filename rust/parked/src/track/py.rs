//! The track stage's door (feature 444 T32): a row village's road from Python's gathered state.
//!
//! Research:
//!     the door - NONE: plumbing, the road's inputs and its runs

use pyo3::prelude::*;
use pyo3::types::PyDict;

use super::{row_road, RoadSite};
use crate::counts::Counts;
use crate::field::fan::Pt;
use crate::ways::route::Crossing;
use crate::ways::through::Fabric;

fn field<'py, T: FromPyObject<'py>>(d: &Bound<'py, PyDict>, key: &str) -> PyResult<T> {
    d.get_item(key)?
        .ok_or_else(|| pyo3::exceptions::PyKeyError::new_err(key.to_owned()))?
        .extract()
}

/// A row village's road (`track.row_road`): its runs, the nearer end's first, and the work counted.
///
/// # Errors
/// `KeyError` naming a field the dict lacks, or a `TypeError` where one does not convert.
#[pyfunction]
pub fn row_road_runs<'py>(
    py: Python<'py>,
    inp: &Bound<'py, PyDict>,
) -> PyResult<Bound<'py, PyDict>> {
    let street: Vec<Pt> = field(inp, "street")?;
    let farms: Vec<Pt> = field(inp, "farms")?;
    let frames: Vec<f64> = field(inp, "frames")?;
    let brook: Vec<Pt> = field(inp, "brook")?;
    let fords: Vec<Pt> = field(inp, "fords")?;
    let sheet: Pt = field(inp, "canvas")?;
    let waters: Vec<(Vec<Pt>, f64)> = field(inp, "square_waters")?;
    let steadings: Vec<(Vec<Pt>, bool)> = field(inp, "steadings")?;
    let envelope: Vec<Pt> = field(inp, "envelope")?;
    let crops: Vec<Vec<Pt>> = field(inp, "crops")?;
    let wet: Vec<Vec<Pt>> = field(inp, "wet")?;
    let paddy: Vec<Vec<Pt>> = field(inp, "paddy")?;
    let lines: Vec<(Pt, Pt)> = field(inp, "thread_lines")?;
    let houses: Vec<Pt> = field(inp, "houses")?;
    let toll: Option<(Vec<Pt>, f64, f64)> = field(inp, "crossing")?;
    let mut tests = Counts::default();
    let crossing = toll.map(|(c, r, cost)| Crossing::new(&c, r, cost, &mut tests));
    let fabric = Fabric {
        steadings: &steadings,
        envelope: &envelope,
        crops: &crops,
        wet: &wet,
        paddy: &paddy,
        lines: &lines,
        houses: &houses,
        crossing: crossing.as_ref(),
    };
    let site = RoadSite {
        street: &street,
        farms: &farms,
        frames: &frames,
        brook: &brook,
        fords: &fords,
        sheet,
        waters: &waters,
        fabric: &fabric,
    };
    let runs = row_road(&site, &mut tests);
    let d = PyDict::new(py);
    d.set_item("runs", runs)?;
    d.set_item("counts", tests.0)?;
    Ok(d)
}
