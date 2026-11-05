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
use super::fit_rules::{Chord, Rules};
use super::fixtures::{Forms, Kind, Place, Wall};
use super::ground::Ground;
use super::layout::{Byre, Rect};
use super::lots::{kind_name, Lots};
use super::place::{grow, Site};
use super::py::field;
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
    let bad = |m: String| pyo3::exceptions::PyValueError::new_err(m);
    let mut tests = Counts::default();
    let (origin, cell, nx, cells): (Pt, f64, usize, Vec<bool>) = field(inp, "ground")?;
    let ground = Ground::from_cells(origin, cell, nx, cells)
        .ok_or_else(|| bad("the raster's cells are not one a cell".to_owned()))?;
    let reach = ground.reach(&field::<Vec<Pt>>(inp, "seeds")?, &mut tests);
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
    let st = grow(&site, field(inp, "center")?, field(inp, "want")?);
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
