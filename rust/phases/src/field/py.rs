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

/// A rice polder's pocket pond: the comb's own roll over the block's low row, a resting plot never its host (0008) - the host
/// plot's index, the pond's middle and radii.
///
/// Research:
///     the pond's host - NONE: the polder's plots as the comb's basins; the roll and its rules are `features::pocket_pond`'s
///     a four-sided host - GUESS: research/questions/0008-ponds-rocks-and-graves-in-the-middle-of-the-fields.drawing.html silent on the host plot's shape; only a four-sided plot, so the pond's fit inside it holds
///     never a resting plot - GUESS: research/questions/0008-ponds-rocks-and-graves-in-the-middle-of-the-fields.drawing.html silent on a pond in a plot left to rest; never its host
fn rice_pond(
    plots: &[super::polder::Plot],
    resting: &[usize],
    seed: i64,
    work: &mut u64,
) -> Option<(usize, f64, f64, f64, f64)> {
    let hosts: Vec<(usize, super::lattice::Basin)> = plots
        .iter()
        .enumerate()
        .filter(|(i, x)| !resting.contains(i) && x.ring.len() == 4)
        .map(|(i, x)| {
            (
                i,
                super::lattice::Basin {
                    row: usize::from(x.low),
                    col: x.col,
                    ring: x.ring.clone(),
                    on_drain_right: false,
                    on_drain_left: false,
                },
            )
        })
        .collect();
    let basins: Vec<super::lattice::Basin> = hosts.iter().map(|(_, b)| b.clone()).collect();
    *work += plots.len() as u64;
    super::features::pocket_pond(&basins, seed, "polder", work)
        .map(|(k, q)| (hosts[k].0, q.x, q.y, q.rx, q.ry))
}

/// The polder's plots drawn apart (`states::polder_states`), each low plot wet and the rest green on a dike-pond block, whose
/// parcels `_dikeponds` draws.
///
/// Research:
///     the polder's plots drawn apart - NONE: the rolls are `states::polder_states`'s; a dike-pond block's states set here draw nothing, every parcel of it converted and drawn by its ponds (`field_stage._dikeponds`)
fn polder_drawn(
    plots: &[super::polder::Plot],
    resting: &[usize],
    seed: i64,
    dikepond: bool,
    counts: &mut crate::counts::Counts,
) -> Vec<State> {
    let drawn: Vec<(usize, usize, bool)> = plots.iter().map(|x| (x.row, x.col, x.low)).collect();
    if dikepond {
        return drawn
            .iter()
            .map(|x| if x.2 { State::Wet } else { State::Green })
            .collect();
    }
    let mut work = 0;
    let out = super::states::polder_states(&drawn, resting, seed, &mut work);
    counts.add("candidate@polder_states", work);
    out
}

/// The polder (T16 D8): the households' paddy as a rice polder or a dike-pond block - its block, dike, outfall, resting plots and,
/// on a dike-pond, its conversion - the records out for the thin Python to write and draw.
///
/// Research:
///     the polder's seam - NONE: the records out; each placement is claimed at the Rust that makes it
///     a rice polder's pocket pond - research/questions/0008-ponds-rocks-and-graves-in-the-middle-of-the-fields.drawing.html: a polder may have a pond on a low plot, a little over half the time; the dike-pond ground has none - the comb's own roll (`features::pocket_pond`) over the block's low row, a resting plot never its host
///     resting only when unsettled - research/questions/0013-paddies-left-to-rest-kataarashi.drawing.html: an unsettled settlement rests two to four whole plots (`polder::rest`), a settled one none
///     no resting plot on a dike-pond block - GUESS: research/questions/0013-paddies-left-to-rest-kataarashi.drawing.html silent on a converted block; its parcels are ponds, their banks and a few in standing rice, and none is rested
#[pyfunction]
#[expect(
    clippy::too_many_arguments,
    clippy::needless_pass_by_value,
    reason = "the polder's inputs, each a plan field Python gathered (D1); PyO3 hands owned strings in the tuple"
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
    canvas: Pt,
    unsettled: bool,
    pond: (f64, String, String, String),
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
    let dike = super::dike::dike(&p.inner_env, &p.sluices, seed);
    let run = super::polder::outfall(p.sluices[1], down_deg, canvas);
    let resting = super::polder::rest(&p.plots, seed, unsettled && !dikepond);
    let mut pond_work = 0_u64;
    let pocket = if dikepond {
        None
    } else {
        rice_pond(&p.plots, &resting, seed, &mut pond_work)
    };
    let mut counts = crate::counts::Counts::default();
    counts.add("candidate@polder_pond", pond_work);
    let states = polder_drawn(&p.plots, &resting, seed, dikepond, &mut counts);
    counts.add("candidate@polder_shape", 4);
    counts.add("write@polder_plot", 5 * p.plots.len() as u64);
    counts.add(
        "write@polder_ditch",
        2 * p.ditches.iter().map(|d| d.pts.len() as u64).sum::<u64>(),
    );
    counts.add("write@polder_pond", 6);
    counts.add("write@dike_crest", 2 * dike.crest.len() as u64);
    counts.add("write@dike_face", 2 * dike.outer.len() as u64);
    counts.add(
        "write@dike_tree",
        2 * dike.trees.iter().map(|(_, r)| r.len() as u64).sum::<u64>(),
    );
    let d = PyDict::new(py);
    d.set_item("outline", pts(&p.outline))?;
    d.set_item("inner_env", pts(&p.inner_env))?;
    let plots = PyList::empty(py);
    for (i, x) in p.plots.iter().enumerate() {
        let q = PyDict::new(py);
        q.set_item("ring", pts(&x.ring))?;
        q.set_item("row", x.row)?;
        q.set_item("col", x.col)?;
        q.set_item("low", x.low)?;
        q.set_item("rest", resting.contains(&i))?;
        q.set_item("state", state(states[i]))?;
        plots.append(q)?;
    }
    d.set_item("plots", plots)?;
    let ditches = PyList::empty(py);
    for x in &p.ditches {
        ditches.append((x.role, x.seg, pts(&x.pts), x.w, x.w_tail))?;
    }
    d.set_item("ditches", ditches)?;
    d.set_item("fringe", p.fringe.clone())?;
    d.set_item("sluices", p.sluices.to_vec())?;
    d.set_item("pond", (p.pond.0 .0, p.pond.0 .1, p.pond.1, p.pond.2))?;
    d.set_item("feeder", pts(&p.feeder))?;
    d.set_item("pocket_pond", pocket)?;
    d.set_item("shape", p.shape)?;
    d.set_item("outfall", run)?;
    let dk = PyDict::new(py);
    dk.set_item("inner", pts(&dike.inner))?;
    dk.set_item("outer", pts(&dike.outer))?;
    dk.set_item("crest", pts(&dike.crest))?;
    dk.set_item("gaps", pts(&dike.gaps))?;
    dk.set_item("widths", dike.widths)?;
    dk.set_item("trees", dike.trees.clone())?;
    d.set_item("dike", dk)?;
    if dikepond {
        let (share, leftover, fry, crop) = &pond;
        let rings: Vec<Vec<Pt>> = p.plots.iter().map(|x| x.ring.clone()).collect();
        let at = super::landuse::inset(&rings, *share);
        let (parcels, crops) = super::landuse::convert(&rings, seed, at, leftover, fry, crop);
        counts.add("write@dikepond", 13 * parcels.len() as u64);
        counts.add(
            "write@bank_crop",
            2 * (crops.crowns.len() + crops.hedges.len()) as u64,
        );
        let conv = PyList::empty(py);
        for x in &parcels {
            conv.append((x.kind, pts(&x.ring), x.bank.clone(), x.water.clone()))?;
        }
        d.set_item("dikeponds", conv)?;
        d.set_item("inset", at)?;
        d.set_item(
            "crops",
            (
                crops.crop.clone(),
                crops.crowns.clone(),
                crops.hedges.clone(),
            ),
        )?;
    }
    d.set_item("counts", counts.0)?;
    Ok(d)
}

/// The bean runs that survive the map's final water (finish's settling): `runs` against `segs` (a, b, width) and `ponds`, with the
/// work done and the beads dropped, for the counters.
#[pyfunction]
#[expect(
    clippy::needless_pass_by_value,
    reason = "PyO3 hands Vecs from Python lists"
)]
#[must_use]
pub fn settle_runs(
    runs: Vec<Vec<Pt>>,
    segs: Vec<(Pt, Pt, f64)>,
    ponds: Vec<(f64, f64, f64, f64)>,
) -> (Vec<Vec<Pt>>, u64, u64) {
    let mut counts = [0; 2];
    let kept = super::beans::settle(&runs, &segs, &ponds, &mut counts);
    (kept, counts[0], counts[1])
}

/// A dike-pond's pond or bank rounded from its parcel (`ponds::rounded`): the path and its samples, `draw` a draw from the caller's
/// own stream.
#[pyfunction]
#[expect(
    clippy::needless_pass_by_value,
    reason = "PyO3 hands a Vec from a Python list"
)]
#[must_use]
pub fn rounded_pond(ring: Vec<Pt>, inset: f64, reach: f64, draw: u32) -> (String, Vec<Pt>) {
    super::ponds::rounded(&ring, inset, reach, draw)
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
