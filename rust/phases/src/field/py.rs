//! The field stage's door to Python (feature 444 T16 D1): `stage_field` takes what the thin Python gathered and returns the
//! records as plain Python values, which Python writes to the manifest's keys and the plan's fields.
//!
//! Research:
//!     the seam - NONE: the extension's own machinery; each record's claims are at the Rust that makes it

use std::collections::HashMap;

use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};

use super::brook::BrookIn;
use super::build::{build, Field, FieldIn, KnobIn};
use super::fan::Pt;
use super::states::State;

/// The brook's figures as Python passes them: lead, offtake angle, tap run, slew, skirt, wander, station, width.
type BrookTuple = (f64, f64, f64, f64, f64, f64, f64, f64);

fn pts(v: &[Pt]) -> Vec<(f64, f64)> {
    v.to_vec()
}

fn state(s: State) -> &'static str {
    match s {
        State::Green => "green",
        State::Wet => "wet",
        State::Flooded => "flooded",
        State::Gold => "gold",
        State::Rest => "rest",
    }
}

fn field_dict<'py>(py: Python<'py>, f: &Field) -> PyResult<Bound<'py, PyDict>> {
    let d = PyDict::new(py);
    d.set_item("ring", pts(&f.fan.ring))?;
    d.set_item(
        "fork",
        f.channels.first().and_then(|c| c.pts.last().copied()),
    )?;
    d.set_item("head_middle", f.fan.fork)?;
    d.set_item("foot", f.fan.foot)?;
    d.set_item("brook", pts(&f.brook.pts))?;
    d.set_item("intake", f.brook.intake)?;
    d.set_item(
        "weir",
        f.weir
            .as_ref()
            .map(|(ring, deg, form)| (ring.to_vec(), *deg, form.clone())),
    )?;
    let plots = PyList::empty(py);
    for (b, s) in f.basins.iter().zip(&f.states) {
        let p = PyDict::new(py);
        p.set_item("ring", pts(&b.ring))?;
        p.set_item("row", b.row)?;
        p.set_item("col", b.col)?;
        p.set_item("state", state(*s))?;
        p.set_item("drain_side", b.drain_side().map(|s| s.to_vec()))?;
        plots.append(p)?;
    }
    d.set_item("plots", plots)?;
    let chans = PyList::empty(py);
    for c in &f.channels {
        chans.append((c.role, pts(&c.pts), c.w, c.w_tail))?;
    }
    d.set_item("channels", chans)?;
    d.set_item("beans", f.beans.iter().map(|r| pts(r)).collect::<Vec<_>>())?;
    let dry = PyList::empty(py);
    for p in &f.dry {
        dry.append((pts(&p.poly), p.crop, p.theta, p.tract))?;
    }
    d.set_item("dry", dry)?;
    d.set_item("pond", f.pond.map(|(i, p)| (i, p.x, p.y, p.rx, p.ry)))?;
    d.set_item(
        "grave",
        f.grave.as_ref().map(|g| {
            (
                g.at,
                g.form,
                g.host,
                g.rings.iter().map(|r| pts(r)).collect::<Vec<_>>(),
            )
        }),
    )?;
    d.set_item("segments", f.segments.clone())?;
    Ok(d)
}

/// The polder (T16 D8): the households' paddy as a rice polder or a dike-pond block, its records out for the thin Python to hand
/// the free helpers (`perimeter_dike`, `marsh`, `apply_land_use`).
#[pyfunction]
#[expect(
    clippy::too_many_arguments,
    reason = "the polder's inputs, each a plan field Python gathered (D1)"
)]
pub fn stage_polder<'py>(
    py: Python<'py>,
    seed: i64,
    households: u32,
    dikepond: bool,
    layout: &str,
    down_deg: f64,
    center: Pt,
    aspect: f64,
) -> PyResult<Bound<'py, PyDict>> {
    let p = super::polder::polder(
        super::paddy_sq_ft(households),
        dikepond,
        layout,
        down_deg,
        center,
        aspect,
        seed,
    );
    let mut counts = crate::counts::Counts::default();
    counts.add("candidate@polder_shape", 4);
    counts.add("write@polder_plot", 5 * p.plots.len() as u64);
    counts.add(
        "write@polder_ditch",
        2 * p.ditches.iter().map(|d| d.pts.len() as u64).sum::<u64>(),
    );
    counts.add("write@polder_pond", 6);
    let d = PyDict::new(py);
    d.set_item("outline", pts(&p.outline))?;
    d.set_item("inner_env", pts(&p.inner_env))?;
    let plots = PyList::empty(py);
    for x in &p.plots {
        let q = PyDict::new(py);
        q.set_item("ring", pts(&x.ring))?;
        q.set_item("row", x.row)?;
        q.set_item("col", x.col)?;
        q.set_item("low", x.low)?;
        plots.append(q)?;
    }
    d.set_item("plots", plots)?;
    let ditches = PyList::empty(py);
    for x in &p.ditches {
        ditches.append((x.role, x.seg, pts(&x.pts), x.w, x.w_tail))?;
    }
    d.set_item("ditches", ditches)?;
    d.set_item("sluices", p.sluices.to_vec())?;
    d.set_item("pond", (p.pond.0 .0, p.pond.0 .1, p.pond.1, p.pond.2))?;
    d.set_item("feeder", pts(&p.feeder))?;
    d.set_item("shape", p.shape)?;
    d.set_item("counts", counts.0)?;
    Ok(d)
}

/// One of the stage's knobs drawn from its table (D3): Python builds the typing-filtered forms and their weights against the running
/// context, Rust draws the form's index as `Knob.roll` does.
#[pyfunction]
#[expect(
    clippy::needless_pass_by_value,
    reason = "PyO3 hands a Vec from a Python list"
)]
#[must_use]
pub fn roll_knob(seed: i64, name: &str, n: u32, weights: Vec<f64>) -> u32 {
    crate::pyrand::roll(seed, name, n, &weights)
}

/// The comb stage (T16): Python's gathered inputs in, the records out.
///
/// # Errors
/// `ValueError` naming the rule when a basin or a grave breaks one where it is decided (D7).
#[pyfunction]
#[expect(
    clippy::too_many_arguments,
    reason = "the stage's inputs, each a plan field Python gathered (D1)"
)]
pub fn stage_field<'py>(
    py: Python<'py>,
    seed: i64,
    households: u32,
    down_deg: f64,
    aspect: f64,
    center: Pt,
    canvas: Pt,
    brook_side: f64,
    brook: BrookTuple,
    offtakes: (Vec<f64>, Vec<f64>),
    weir: (f64, f64, HashMap<String, f64>),
    plot_size: &str,
    cell: f64,
    knobs: Vec<KnobIn>,
) -> PyResult<Bound<'py, PyDict>> {
    let (lead, offtake_deg, tap_run, slew, skirt, wander, station, w) = brook;
    let inp = FieldIn {
        seed,
        households,
        down_deg,
        aspect,
        center,
        canvas,
        brook_side,
        brook: BrookIn {
            lead,
            offtake_deg,
            tap_run,
            slew,
            skirt,
            wander,
            station,
            w,
        },
        offtakes,
        weir,
        row_ft: super::lattice::row_ft_for(plot_size),
        cell,
        knobs,
    };
    let out = build(&inp).map_err(|e| PyValueError::new_err(e.to_string()))?;
    let d = PyDict::new(py);
    d.set_item("knobs", out.knobs)?;
    let fields = PyList::empty(py);
    for f in &out.fields {
        fields.append(field_dict(py, f)?)?;
    }
    d.set_item("fields", fields)?;
    d.set_item("grain", out.grain)?;
    d.set_item("counts", out.counts)?;
    Ok(d)
}
