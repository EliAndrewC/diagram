//! The homesteads' door to Python (feature 444 T30 D1): what the thin Python gathered from the settlement, read from a dict by
//! name, and the stage's results as plain Python values. The track out first (`track_out`): Python's own state, frozen once the
//! last house stands, can be run through it and the two tracks compared before the stage is wired.
//!
//! Research:
//!     the homesteads' door - NONE: the extension's own machinery; each record's claims are at the Rust that makes it

use pyo3::prelude::*;
use pyo3::types::PyDict;

use super::Counts;
use crate::field::fan::Pt;
use crate::ways::dry_exit::DrySite;
use crate::ways::gateway::{choose_track_out, Axes, Choice};
use crate::ways::route::Crossing;
use crate::ways::through::{Fabric, Law};
use crate::ways::track::{poly_box, Box4, Pond, TrackSite};

/// A field of the gathered dict, by name.
fn field<'py, T: FromPyObject<'py>>(d: &Bound<'py, PyDict>, key: &str) -> PyResult<T> {
    d.get_item(key)?
        .ok_or_else(|| pyo3::exceptions::PyKeyError::new_err(key.to_owned()))?
        .extract()
}

fn quad(b: Box4) -> Vec<Pt> {
    vec![(b.0, b.1), (b.2, b.1), (b.2, b.3), (b.0, b.3)]
}

fn segs(course: &[Pt]) -> Vec<(Pt, Pt)> {
    course.windows(2).map(|w| (w[0], w[1])).collect()
}

/// The track out, chosen once the last house stands (`ways/gateway.rs`), from Python's gathered state: the run and whether it
/// took a reserved wood seat, and the work counted; None where no way leaves the frame.
///
/// # Errors
/// `KeyError` naming a field the dict lacks, or a `TypeError` where one does not convert.
#[pyfunction]
pub fn track_out<'py>(
    py: Python<'py>,
    inp: &Bound<'py, PyDict>,
) -> PyResult<Option<Bound<'py, PyDict>>> {
    let canvas: Pt = field(inp, "canvas")?;
    let (out, fall, seat): (Pt, Pt, Pt) =
        (field(inp, "out")?, field(inp, "fall")?, field(inp, "seat")?);
    let envelope: Vec<Pt> = field(inp, "envelope")?;
    let crops: Vec<Vec<Pt>> = field(inp, "crops")?;
    let wet: Vec<Vec<Pt>> = field(inp, "wet")?;
    let steadings: Vec<(Vec<Pt>, bool)> = field(inp, "steadings")?;
    let solid: Vec<Box4> = field(inp, "solid")?;
    let pond: Option<Pond> = field(inp, "pond")?;
    let sink_brook = segs(&field::<Vec<Pt>>(inp, "sink_brook")?);
    let mut waters: Vec<(Pt, Pt)> = field(inp, "watercourses")?;
    let drawn: Vec<(Pt, Pt)> = field(inp, "drawn")?;
    waters.extend(&drawn);
    let course: Vec<Pt> = field(inp, "course")?;
    let forbidding: Vec<(Vec<Pt>, Box4)> = field::<Vec<Vec<Pt>>>(inp, "forbidding")?
        .into_iter()
        .map(|p| {
            let b = poly_box(&p);
            (p, b)
        })
        .collect();
    let seats: Vec<Vec<Pt>> = field(inp, "seats")?;
    let brooks: Vec<Vec<Pt>> = field(inp, "brooks")?;
    let square: Vec<(Vec<Pt>, f64)> = field(inp, "square_waters")?;
    let houses: Vec<Pt> = field(inp, "houses")?;
    let paddy: Vec<Vec<Pt>> = field(inp, "paddy")?;
    let toll: Option<(Vec<Pt>, f64, f64)> = field(inp, "crossing")?;
    let mut tests = Counts::default();
    let crossing = toll.map(|(c, r, cost)| Crossing::new(&c, r, cost, &mut tests));
    let mut avoid = vec![envelope.clone()];
    avoid.extend(crops.iter().cloned());
    let solid_quads: Vec<Vec<Pt>> = solid.iter().map(|&b| quad(b)).collect();
    let mut sweep_fabric: Vec<Vec<Pt>> = steadings.iter().map(|s| s.0.clone()).collect();
    sweep_fabric.extend(solid_quads.iter().cloned());
    let mut dry_fabric = steadings.clone();
    dry_fabric.extend(solid_quads.iter().map(|q| (q.clone(), false)));
    let lines: Vec<(Pt, Pt)> = sink_brook.iter().chain(&waters).copied().collect();
    let sweep = TrackSite {
        lean: (out, fall),
        seat,
        avoid: &avoid,
        wet: &wet,
        fabric: &sweep_fabric,
        water: (pond, &sink_brook, &waters),
        canvas,
    };
    let dry = DrySite {
        wet: &wet,
        fabric: &dry_fabric,
        avoid: &avoid,
        pond,
        lines: &lines,
        course: &course,
        canvas,
    };
    let fabric = Fabric {
        steadings: &steadings,
        envelope: &envelope,
        crops: &crops,
        wet: &wet,
        paddy: &paddy,
        lines: &waters,
        houses: &houses,
        crossing: crossing.as_ref(),
    };
    let law = Law {
        solid: &solid,
        forbidding: &forbidding,
        seats: &seats,
        brooks: &brooks,
        waters: &square,
    };
    // the gateway walks out clear of the homesteads alone, as `_cluster_gateway` reads `_homestead_polys`
    let standing: Vec<(Vec<Pt>, Box4)> = steadings
        .iter()
        .map(|s| s.0.clone())
        .map(|p| {
            let b = poly_box(&p);
            (p, b)
        })
        .collect();
    let c = Choice {
        sweep: &sweep,
        dry: &dry,
        fabric: &fabric,
        law: &law,
        standing: &standing,
        axes: Axes {
            along: field(inp, "along")?,
            out,
        },
        fallback: field(inp, "fallback")?,
    };
    let Some((run, took)) = choose_track_out(&c, &mut tests) else {
        return Ok(None);
    };
    let d = PyDict::new(py);
    d.set_item("track", run)?;
    d.set_item("seats_taken", took)?;
    d.set_item("counts", tests.0)?;
    Ok(Some(d))
}
