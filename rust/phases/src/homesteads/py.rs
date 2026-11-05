//! The homesteads' door to Python (feature 444 T30 D1): what the thin Python gathered from the settlement, read from a dict by
//! name, and the stage's results as plain Python values. The track out first (`track_out`): Python's own state, frozen once the
//! last house stands, can be run through it and the two tracks compared before the stage is wired.
//!
//! Research:
//!     the homesteads' door - NONE: the extension's own machinery; each record's claims are at the Rust that makes it

use pyo3::prelude::*;
use pyo3::types::PyDict;

use super::access::{AccessTree, Parts, ACCESS_HALF_FT};
use super::fixtures::Kind;
use super::gap_ways::{lay_the_ways, GapSite, Household, Judge};
use super::ground::Ground;
use super::layout::Rect;
use super::standing::Standing;
use super::ways_judge::WaysJudge;
use super::wood::Shares;
use super::Counts;
use crate::field::fan::Pt;
use crate::law::ground::{rot_rect, House, LawGround};
use crate::law::meet::Destinations;
use crate::law::tree::Tree;
use crate::law::walk::Steading;
use crate::law::water::Waters;
use crate::ways::dry_exit::DrySite;
use crate::ways::gateway::{choose_track_out, Axes, Choice};
use crate::ways::route::Crossing;
use crate::ways::through::{Fabric, Law};
use crate::ways::track::{poly_box, Box4, Pond, TrackSite};

/// A field of the gathered dict, by name.
pub(super) fn field<'py, T: FromPyObject<'py>>(d: &Bound<'py, PyDict>, key: &str) -> PyResult<T> {
    d.get_item(key)?
        .ok_or_else(|| pyo3::exceptions::PyKeyError::new_err(key.to_owned()))?
        .extract()
}

fn quad(b: Box4) -> Vec<Pt> {
    vec![(b.0, b.1), (b.2, b.1), (b.2, b.3), (b.0, b.3)]
}

fn boxed(polys: Vec<Vec<Pt>>) -> Vec<(Vec<Pt>, Box4)> {
    polys
        .into_iter()
        .map(|p| {
            let b = poly_box(&p);
            (p, b)
        })
        .collect()
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
    let forbidding = boxed(field::<Vec<Vec<Pt>>>(inp, "forbidding")?);
    let seats: Vec<Vec<Pt>> = field(inp, "seats")?;
    let brooks: Vec<Vec<Pt>> = field(inp, "brooks")?;
    let square: Vec<(Vec<Pt>, f64)> = field(inp, "square_waters")?;
    let houses: Vec<Pt> = field(inp, "houses")?;
    let paddy: Vec<Vec<Pt>> = field(inp, "paddy")?;
    // the thread walls the planned watercourses and the drawn channels, not the streams (`_thread_the_fabric`)
    let thread_lines: Vec<(Pt, Pt)> = field(inp, "thread_lines")?;
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
        lines: &thread_lines,
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
    let standing = boxed(steadings.iter().map(|s| s.0.clone()).collect());
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

/// A household as Python gathers it: its turned house, yard, beds and annexes, its fixtures (each marked where it is a
/// persimmon), its house and yard before the turn, the turn, the box round its homestead, and its house's center.
type PyHousehold = (
    Rect,
    Rect,
    Vec<Rect>,
    Vec<Rect>,
    Vec<(bool, Rect)>,
    Rect,
    Rect,
    f64,
    Rect,
    Pt,
    Option<Rect>,
);

/// What an end may reach as Python gathers it: the houses and way targets, the worked ground's edge, the steadings.
type PyDestinations = (Vec<Pt>, Vec<(Pt, Pt)>, Vec<Vec<Pt>>);

fn household(h: PyHousehold) -> Household {
    let (house, yard, gardens, sheds, fixtures, raw_house, raw_yard, turn, bbox, at, well) = h;
    let fixtures = fixtures
        .into_iter()
        .map(|(persimmon, r)| {
            (
                if persimmon {
                    Kind::Persimmon
                } else {
                    Kind::Privy
                },
                r,
            )
        })
        .collect();
    Household {
        parts: Parts {
            house,
            yard,
            gardens,
            sheds,
            fixtures,
            raw: (raw_house, raw_yard),
            turn,
            well,
        },
        bbox,
        at,
    }
}

fn house_of((x, y, w, h, rot): (f64, f64, f64, f64, f64)) -> House {
    House {
        quad: rot_rect(x, y, w, h, rot),
        at: (x, y),
        half_diag: w.hypot(h) / 2.0,
    }
}

/// The lane law's ground as Python's `Lawful` reads it, from the gathered dict.
fn law_ground(d: &Bound<'_, PyDict>) -> PyResult<LawGround> {
    let houses: Vec<(f64, f64, f64, f64, f64)> = field(d, "houses")?;
    let yards: Vec<(Vec<Pt>, Option<Pt>)> = field(d, "yards")?;
    Ok(LawGround {
        houses: houses.into_iter().map(house_of).collect(),
        yards: yards
            .into_iter()
            .map(|(r, o)| {
                let b = poly_box(&r);
                (r, b, o)
            })
            .collect(),
        solid: field(d, "solid")?,
        fixtures: boxed(field(d, "fixtures")?),
        buildings: field(d, "buildings")?,
        open_rings: field(d, "open_rings")?,
        forbidding: boxed(field(d, "forbidding")?),
        waters: Waters {
            brooks: field(d, "brooks")?,
            channels: field(d, "channels")?,
            crossed: field(d, "crossed")?,
            fords: field(d, "fords")?,
            wet: field(d, "flooded")?,
            deck_forbidding: boxed(field(d, "deck_forbidding")?),
            boxes: std::cell::OnceCell::new(),
        },
        ..LawGround::default()
    })
}

/// The judge, every verdict it gave kept for the comparison: the way, the household (None for a leg's ground), and the verdict.
struct Recorded<'a> {
    judge: WaysJudge<'a>,
    verdicts: Vec<(Vec<Pt>, Option<usize>, Option<&'static str>)>,
}

impl Judge for Recorded<'_> {
    fn lawful_leg(&mut self, a: Pt, b: Pt, tests: &mut Counts) -> bool {
        let ok = self.judge.lawful_leg(a, b, tests);
        self.verdicts
            .push((vec![a, b], None, (!ok).then_some("ground")));
        ok
    }

    fn tree_admits(&mut self, drawn: &[Pt], k: usize, tests: &mut Counts) -> bool {
        let why = self.judge.refusal(drawn, k, tests);
        self.verdicts.push((drawn.to_vec(), Some(k), why));
        why.is_none()
    }

    fn reserve(&mut self, drawn: &[Pt], k: usize) {
        self.judge.reserve(drawn, k);
    }
}

/// Every household's way laid in the gaps once the last house stands (`homesteads/gap_ways.rs`), from Python's gathered state:
/// each household's way as drawn, or the neighbor it is reached across, and the work counted.
///
/// # Errors
/// `KeyError` naming a field the dict lacks, a `TypeError` where one does not convert, or `ValueError` where the raster's cells
/// are not one a cell.
#[pyfunction]
pub fn households_ways<'py>(
    py: Python<'py>,
    inp: &Bound<'py, PyDict>,
) -> PyResult<Bound<'py, PyDict>> {
    let mut tests = Counts::default();
    let households: Vec<Household> = field::<Vec<PyHousehold>>(inp, "households")?
        .into_iter()
        .map(household)
        .collect();
    let (origin, cell, nx, cells): (Pt, f64, usize, Vec<bool>) = field(inp, "ground")?;
    let ground = Ground::from_cells(origin, cell, nx, cells).ok_or_else(|| {
        pyo3::exceptions::PyValueError::new_err("the raster's cells are not one a cell")
    })?;
    let beyond = |_p: Pt| true;
    let mut wood = Shares::default();
    wood.commit(
        &field::<Vec<Pt>>(inp, "seats")?,
        (Vec::new(), Vec::new()),
        &mut tests,
    );
    let lane_gap: f64 = field(inp, "lane_gap")?;
    let extra: Vec<Rect> = field(inp, "extra")?;
    let site = GapSite {
        ground: &ground,
        beyond: &beyond,
        wood: &wood,
        canvas: field(inp, "canvas")?,
        lane_gap,
        extra: &extra,
    };
    let square: Vec<(Vec<Pt>, f64)> = field(inp, "square_waters")?;
    let brooks: Vec<Vec<Pt>> = field(inp, "brooks")?;
    let dest: PyDestinations = field(inp, "destinations")?;
    let destinations = Destinations {
        centers: dest.0,
        edge: dest.1,
        steadings: dest.2,
    };
    let mut tree = Tree::new(
        field(inp, "root")?,
        law_ground(inp)?,
        destinations,
        &square,
        &brooks,
    );
    tree.steadings = field::<Vec<((f64, f64, f64, f64, f64), Vec<Vec<Pt>>)>>(inp, "steadings")?
        .into_iter()
        .map(|(h, parts)| Steading {
            house: house_of(h),
            parts,
        })
        .collect();
    let boxes: Vec<Rect> = households
        .iter()
        .map(|h| h.bbox)
        .chain(extra.iter().copied())
        .collect();
    let judge = WaysJudge {
        tree,
        parts: households.iter().map(|h| h.parts.clone()).collect(),
        centers: households.iter().map(|h| h.at).collect(),
        standing: Standing::new(&ground, &beyond, &wood, &boxes, (ACCESS_HALF_FT, lane_gap)),
    };
    let mut access = AccessTree::new(ACCESS_HALF_FT);
    for (a, b) in field::<Vec<(Pt, Pt)>>(inp, "segs")? {
        access.add(a, b);
    }
    let mut judge = Recorded {
        judge,
        verdicts: Vec::new(),
    };
    let ways = lay_the_ways(&site, &households, &mut access, &mut judge, &mut tests);
    let d = PyDict::new(py);
    d.set_item("drawn", ways.drawn)?;
    d.set_item("pinched", ways.pinched)?;
    d.set_item("verdicts", judge.verdicts)?;
    d.set_item("counts", tests.0)?;
    Ok(d)
}
