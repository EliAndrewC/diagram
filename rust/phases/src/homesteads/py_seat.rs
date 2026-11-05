//! The seating's door to Python (feature 444 T30 D1): a nucleated cluster grown (`place.rs` `grow`) from what the thin Python
//! gathered once the seat region stands - the free ground as cells, the way out's anchor, the field, the streams, the margin and
//! the common bearing, the lots and the fixture forms, and what the rules read past the raster - and every household seated, as
//! plain Python values for Python to record.
//!
//! Research:
//!     the seating's door - NONE: the extension's own machinery; each record's claims are at the Rust that makes it

use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};

use super::bearing::Margin;
use super::bundle::Grove;
use super::dispersed::bundle_turn;
use super::fit_rules::{Chord, Rules};
use super::fixtures::{Forms, Kind, Place, Wall};
use super::ground::Ground;
use super::grove_rounds::seat_scattered as seat_scattered_on;
use super::grove_seat::{Axes, Corridors, GroveSite};
use super::layout::{Byre, Rect};
use super::level::Hard;
use super::lots::{kind_name, Lots};
use super::place::{grow, Site};
use super::py::field;
use super::row_seat::{row_room, seat_rows as seat_rows_on, RowSite};
use super::rows::Form;
use super::Counts;
use crate::field::fan::Pt;

/// A fixture kind by the name Python files it under.
fn kind_of(name: &str) -> Option<Kind> {
    [
        Kind::Retirement,
        Kind::Bath,
        Kind::Woodpile,
        Kind::Privy,
        Kind::Manure,
        Kind::Coop,
        Kind::Shrine,
        Kind::Grave,
        Kind::Persimmon,
    ]
    .into_iter()
    .find(|&k| kind_name(k) == name)
}

/// A privy's place by the name Python weighs it under.
fn place_of(name: &str) -> Option<Place> {
    match name {
        "stable" => Some(Place::Stable),
        "yard" => Some(Place::Yard),
        "front" => Some(Place::Front),
        "barn" => Some(Place::Barn),
        _ => None,
    }
}

/// The walls a bath room may take, each by the name Python records it under (`fixture_seats.bath_room_seats`).
const WALLS: [(Wall, &str); 3] = [
    (Wall::MainDoor, "main_door"),
    (Wall::StableEnd, "stable_end"),
    (Wall::FlooredRooms, "floored_rooms"),
];

/// The wall a bath room took, by the name Python records it under.
fn wall_name(w: Wall) -> &'static str {
    WALLS
        .iter()
        .find(|(v, _)| *v == w)
        .map_or("main_door", |&(_, n)| n)
}

/// The hamlet's fixture forms as Python rolled them: the privy's weighted places, the bath room's share beyond the stable wing,
/// the persimmon's front share, whether the manure is pitted, and the retirement house's size and gaps.
type PyForms = (Vec<(String, f64)>, f64, f64, bool, (f64, f64), Vec<f64>);

fn forms_of((privy, bath, front, pit, ft, gaps): PyForms) -> PyResult<Forms> {
    let privy_weights = privy
        .iter()
        .map(|(n, w)| {
            place_of(n).map(|p| (p, *w)).ok_or_else(|| {
                pyo3::exceptions::PyValueError::new_err(format!("no privy place {n}"))
            })
        })
        .collect::<PyResult<_>>()?;
    let joined = Forms::default().bath_shares.1;
    Ok(Forms {
        privy_weights,
        bath_shares: (bath, joined),
        persimmon_front: front,
        manure_pit: pit,
        retirement_ft: ft,
        retirement_gaps: gaps,
    })
}

/// What the rules read past the raster, from the gathered dict.
fn rules_of(d: &Bound<'_, PyDict>) -> PyResult<Rules> {
    Ok(Rules {
        chains: field::<Vec<Vec<Chord>>>(d, "chains")?,
        waters: Rules::boxed(field(d, "waters")?),
        hard: Rules::boxed(field(d, "hard")?),
        forbidding: field(d, "forbidding")?,
        sun: field(d, "sun")?,
        bars: field(d, "bars")?,
        placed: field(d, "placed")?,
        site_chains: field(d, "site_chains")?,
        lane_gap: field(d, "lane_gap")?,
        passage_left: field(d, "passage_left")?,
    })
}

/// The households of a nucleated cluster seated (`place.rs` `grow`) from Python's gathered state: each household's lot, seat and
/// homestead - its house, yard, beds, annexes and fixtures, its rake, every part's box as drawn and the box round them - and the
/// wood seats it reserved; the search's counts and the work counted.
///
/// # Errors
/// `KeyError` naming a field the dict lacks, a `TypeError` where one does not convert, or `ValueError` where the raster's cells are
/// not one a cell, a fixture kind, privy place or byre form is unknown.
#[pyfunction]
pub fn seat_households<'py>(
    py: Python<'py>,
    inp: &Bound<'py, PyDict>,
) -> PyResult<Bound<'py, PyDict>> {
    seat_with(py, inp, &|site, inp| {
        Ok(grow(site, field(inp, "center")?, field(inp, "want")?))
    })
}

/// The seating's site read from the gathered dict, `run` over it, and every household it seated as plain Python values.
fn seat_with<'py>(
    py: Python<'py>,
    inp: &Bound<'py, PyDict>,
    run: &dyn Fn(&Site, &Bound<'py, PyDict>) -> PyResult<super::place::Seating>,
) -> PyResult<Bound<'py, PyDict>> {
    let bad = |m: String| pyo3::exceptions::PyValueError::new_err(m);
    let mut tests = Counts::default();
    let (origin, cell, nx, cells): (Pt, f64, usize, Vec<bool>) = field(inp, "ground")?;
    let ground = Ground::from_cells(origin, cell, nx, cells)
        .ok_or_else(|| bad("the raster's cells are not one a cell".to_owned()))?;
    // the reach over the seating's window where the door hands one (a nucleated cluster's), else the whole ground
    let seeds: Vec<Pt> = field(inp, "seeds")?;
    let reach = match field::<Option<(Pt, Pt)>>(inp, "window")? {
        Some(w) => ground.reach_in(w, &seeds, &mut tests),
        None => ground.reach(&seeds, &mut tests),
    };
    let field_ring: Vec<Pt> = field(inp, "field")?;
    let streams: Vec<(Pt, Pt)> = field(inp, "streams")?;
    let (along, common): (f64, f64) = field(inp, "bearing")?;
    let margin = Margin::new(&field_ring, along, &mut tests);
    let (seed, n, byre_share): (i64, usize, f64) = field(inp, "lots")?;
    let shares = field::<Vec<(String, f64)>>(inp, "shares")?
        .iter()
        .map(|(k, p)| {
            kind_of(k)
                .map(|k| (k, *p))
                .ok_or_else(|| bad(format!("no fixture kind {k}")))
        })
        .collect::<PyResult<Vec<_>>>()?;
    let lots = Lots::deal(seed, n, byre_share, &shares);
    let byre = match field::<Option<String>>(inp, "byre")?.as_deref() {
        None => None,
        Some("courtyard") => Some(Byre::Courtyard),
        Some("yard_shed") => Some(Byre::YardShed),
        Some(other) => return Err(bad(format!("no byre form {other}"))),
    };
    let forms = forms_of(field(inp, "forms")?)?;
    let rules = rules_of(inp)?;
    let beyond = |_p: Pt| true;
    let site = Site {
        ground: &ground,
        beyond: &beyond,
        reach: &reach,
        field: &field_ring,
        streams: &streams,
        canvas: field(inp, "canvas")?,
        bearing: (&margin, common),
        lots: &lots,
        byre,
        forms: &forms,
        shade: field(inp, "shade")?,
        rules: &rules,
    };
    let st = run(&site, inp)?;
    let seated = PyList::empty(py);
    for s in &st.seated {
        let b = &s.bundle;
        let h = PyDict::new(py);
        h.set_item("lot", s.lot)?;
        h.set_item("seat", s.seat)?;
        h.set_item("house", b.house)?;
        h.set_item("yard", b.yard)?;
        h.set_item("gardens", b.gardens.clone())?;
        h.set_item("shed", b.kura)?;
        h.set_item("byre", b.byre)?;
        let fixtures: Vec<(&str, Rect)> =
            b.fixtures.iter().map(|&(k, r)| (kind_name(k), r)).collect();
        h.set_item("fixtures", fixtures)?;
        h.set_item("bath", b.bath.map(wall_name))?;
        h.set_item("turn", b.turn)?;
        h.set_item("boxes", b.boxes.clone())?;
        h.set_item("bbox", b.bbox)?;
        h.set_item("wood", s.wood.clone())?;
        h.set_item(
            "passage",
            s.passage.as_ref().map(super::passage::Passage::parts),
        )?;
        let groves: Vec<(Rect, (i32, i32), bool)> = b
            .groves
            .iter()
            .map(|&(r, f, d)| (r, f, d == super::dispersed::Depth::Deep))
            .collect();
        h.set_item("groves", groves)?;
        h.set_item("well", b.well)?;
        // the lot's kura: a grove farm lays none in its bundle, and Python draws it on the house's north wall all the same
        let kura = b.kura.is_some() || site.lots.lot(s.lot).is_some_and(|l| l.1);
        h.set_item("kura", kura)?;
        seated.append(h)?;
    }
    for (k, v) in st.tests.0 {
        tests.add(&k, v);
    }
    let d = PyDict::new(py);
    d.set_item("seated", seated)?;
    d.set_item("search", st.search)?;
    d.set_item("counts", tests.0)?;
    Ok(d)
}

/// A scattered hamlet's grove farms seated (`grove_rounds.rs` `seat_scattered`) from Python's gathered state - the seating's site, and
/// the grove its farms carry, the paddies, the other ground and the water, the seat band and its axes, the chains its front row is
/// offset from, the largest house, the cluster's shape, the lanes' form, the seed, the households wanted, the band's reach and
/// whether its farms stand in single file: each household seated, as `seat_households` returns them, its bands and well pocket too.
///
/// # Errors
/// As `seat_households`.
#[pyfunction]
pub fn seat_scattered<'py>(
    py: Python<'py>,
    inp: &Bound<'py, PyDict>,
) -> PyResult<Bound<'py, PyDict>> {
    seat_with(py, inp, &|site, inp| {
        let g = GroveIn::of(inp)?;
        Ok(seat_scattered_on(&g.site(site, inp)?))
    })
}

/// What a grove farm's site reads from Python beyond the seating's own: the grove, the other ground and the water, the axes, the
/// paddies, the chains and the cluster's shape.
struct GroveIn {
    grove: Grove,
    corridors: Corridors,
    axes: Axes,
    paddies: Vec<Vec<Pt>>,
    chains: Vec<Vec<Chord>>,
    shape: String,
}

impl GroveIn {
    fn of(inp: &Bound<'_, PyDict>) -> PyResult<Self> {
        let (sides, wind, sun_band, well, yard_sun): (u32, String, bool, f64, f64) =
            field(inp, "grove")?;
        let (rings, holes, water): CorridorsIn = field(inp, "corridors")?;
        let (c, along, out, anchor, lat): (Pt, Pt, Pt, Pt, f64) = field(inp, "axes")?;
        Ok(Self {
            grove: Grove {
                sides,
                turn: bundle_turn(&wind),
                sun_band,
                well,
                yard_sun,
            },
            corridors: Corridors {
                rings,
                holes,
                water,
            },
            axes: Axes {
                c,
                along,
                out,
                anchor,
                lat,
            },
            paddies: field(inp, "paddies")?,
            chains: field(inp, "row_chains")?,
            shape: field(inp, "shape")?,
        })
    }

    fn site<'a>(&'a self, site: &'a Site<'a>, inp: &Bound<'_, PyDict>) -> PyResult<GroveSite<'a>> {
        Ok(GroveSite {
            site,
            grove: self.grove,
            paddies: &self.paddies,
            corridors: &self.corridors,
            axes: self.axes,
            chains: &self.chains,
            house_max: field(inp, "house_max")?,
            shape: &self.shape,
            alleys: field(inp, "alleys")?,
            seed: field(inp, "seed")?,
            want: field(inp, "want")?,
            band: field(inp, "band")?,
            bound: field(inp, "bound")?,
            single_file: field(inp, "single_file")?,
            streets: (&[], 0.0),
        })
    }
}

/// What a row village reads beyond its grove farms' site: both sides or one, the line's form, the sheltered form's roll and the
/// wind's vector, the farms' front face, the sheet, the planned seat's point, and the hard ground's polygons and water strips.
type RowsIn = (
    bool,
    String,
    bool,
    Pt,
    Pt,
    Pt,
    Pt,
    Vec<Vec<Pt>>,
    Vec<(Pt, Pt, f64)>,
);

/// What a row village returns beyond its seating: each street with its farms' houses, each holding (its ring, the street's tangent
/// and normal, its depth, its farm's lot), and each seated farm's sheltered mark.
type RowsOut = (
    Vec<(Vec<Pt>, Vec<Pt>)>,
    Vec<(Vec<Pt>, Pt, Pt, f64, usize)>,
    Vec<bool>,
);

/// A row village's grove farms seated along its streets (`row_seat.rs` `seat_rows`) from Python's gathered state - a scattered
/// hamlet's, and the `rows` its streets are planned from: each household seated as `seat_households` returns them, with the
/// `streets`, the `holdings` and the `sheltered` marks.
///
/// # Errors
/// As `seat_households`, and where the line's form is neither `street` nor `edge`.
#[pyfunction]
pub fn seat_rows<'py>(py: Python<'py>, inp: &Bound<'py, PyDict>) -> PyResult<Bound<'py, PyDict>> {
    let extra: std::cell::RefCell<RowsOut> = std::cell::RefCell::default();
    let room: std::cell::RefCell<usize> = std::cell::RefCell::default();
    let d = seat_with(py, inp, &|site, inp| {
        let g = GroveIn::of(inp)?;
        let (both, form, shelter, wind, front, sheet, anchor, polys, strips): RowsIn =
            field(inp, "rows")?;
        let form = match form.as_str() {
            "street" => Form::Street,
            "edge" => Form::Edge,
            other => {
                return Err(pyo3::exceptions::PyValueError::new_err(format!(
                    "no row line form {other}"
                )))
            }
        };
        let mut tests = Counts::default();
        let hard = Hard::new(&polys, &strips, &mut tests);
        let ask_only: bool = inp
            .get_item("ask_only")?
            .map_or(Ok(false), |v| v.extract())?;
        let rs = RowSite {
            gs: g.site(site, inp)?,
            hard: &hard,
            anchor,
            both,
            form,
            shelter: (shelter, wind),
            front,
            sheet,
        };
        let rows = if ask_only {
            row_room(&rs)
        } else {
            seat_rows_on(&rs)
        };
        *room.borrow_mut() = rows.room;
        let mut st = rows.seating;
        for (k, v) in tests.0 {
            st.tests.add(&k, v);
        }
        *extra.borrow_mut() = (rows.streets, rows.holdings, rows.sheltered);
        Ok(st)
    })?;
    let (streets, holdings, sheltered) = extra.take();
    d.set_item("streets", streets)?;
    d.set_item("holdings", holdings)?;
    d.set_item("sheltered", sheltered)?;
    d.set_item("room", room.take())?;
    Ok(d)
}

/// The other ground and the water as Python gathers them: its exterior rings, its holes, and each water segment with its clearance.
type CorridorsIn = (Vec<Vec<Pt>>, Vec<Vec<Pt>>, Vec<(Pt, Pt, f64)>);
