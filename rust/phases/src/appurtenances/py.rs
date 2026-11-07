//! The appurtenances stage's door (feature 444 T33): the communal wells' and the shared row wells' seats from Python's gathered
//! state, each group's or mark's in the order the door asks them.
//!
//! Research:
//!     the door - NONE: plumbing, the seats' inputs and their lists

use pyo3::prelude::*;
use pyo3::types::PyDict;

use super::farm_water::{farm_channels as channels, Farm, Ground};
use super::wells::{cluster_seats, row_well_seats, verge_seats, Cluster, House, RowWells};
use crate::counts::Counts;
use crate::field::fan::Pt;

fn field<'py, T: FromPyObject<'py>>(d: &Bound<'py, PyDict>, key: &str) -> PyResult<T> {
    d.get_item(key)?
        .ok_or_else(|| pyo3::exceptions::PyKeyError::new_err(key.to_owned()))?
        .extract()
}

/// The communal wells' seats, group by group (`wells.cluster_seats`; on the lane-side form, given `track`, `wells.verge_seats`),
/// and the work counted.
///
/// # Errors
/// `KeyError` naming a field the dict lacks, or a `TypeError` where one does not convert.
#[pyfunction]
pub fn well_seats<'py>(py: Python<'py>, inp: &Bound<'py, PyDict>) -> PyResult<Bound<'py, PyDict>> {
    let houses: Vec<House> = field(inp, "houses")?;
    let needy: Vec<bool> = field(inp, "needy")?;
    let want: usize = field(inp, "want")?;
    let rungs: Vec<(f64, usize)> = field(inp, "rungs")?;
    let gap: f64 = field(inp, "gap")?;
    let track: Option<Vec<Pt>> = field(inp, "track")?;
    let verge: (f64, f64) = field(inp, "verge")?;
    let mut tests = Counts::default();
    let c = Cluster {
        houses: &houses,
        needy: &needy,
        want,
        rungs: &rungs,
        gap,
    };
    let seats = match track {
        Some(t) => verge_seats(&c, &t, verge, &mut tests),
        None => cluster_seats(&c, &mut tests),
    };
    let d = PyDict::new(py);
    d.set_item("groups", seats)?;
    d.set_item("counts", tests.0)?;
    Ok(d)
}

/// A row village's shared wells' seats, mark by mark (`wells.row_well_seats`), and the work counted.
///
/// # Errors
/// `KeyError` naming a field the dict lacks, or a `TypeError` where one does not convert.
#[pyfunction]
pub fn row_wells<'py>(py: Python<'py>, inp: &Bound<'py, PyDict>) -> PyResult<Bound<'py, PyDict>> {
    let streets: Vec<Vec<Pt>> = field(inp, "streets")?;
    let farms: Vec<Pt> = field(inp, "farms")?;
    let mut tests = Counts::default();
    let r = RowWells {
        streets: &streets,
        farms: &farms,
        frame: field(inp, "frame")?,
        reach: field(inp, "reach")?,
        off: field(inp, "off")?,
        bend: field(inp, "bend")?,
    };
    let marks = row_well_seats(&r, &mut tests);
    let d = PyDict::new(py);
    d.set_item("marks", marks)?;
    d.set_item("counts", tests.0)?;
    Ok(d)
}

/// Each grove farm's channel into its grounds, in the farms' order (`farm_water.farm_channels`), and the work counted: an empty
/// run for a farm no course reaches.
///
/// # Errors
/// `KeyError` naming a field the dict lacks, or a `TypeError` where one does not convert.
#[pyfunction]
pub fn farm_channels<'py>(
    py: Python<'py>,
    inp: &Bound<'py, PyDict>,
) -> PyResult<Bound<'py, PyDict>> {
    let farms: Vec<(Pt, Vec<Pt>, Vec<Vec<Pt>>)> = field(inp, "farms")?;
    let hard: Vec<Vec<Pt>> = field(inp, "hard")?;
    let walls: Vec<Vec<Pt>> = field(inp, "walls")?;
    let courses: Vec<Vec<Pt>> = field(inp, "courses")?;
    let water: Vec<(Pt, Pt)> = field(inp, "water")?;
    let farms: Vec<Farm> = farms
        .into_iter()
        .map(|(at, yard, own)| Farm { at, yard, own })
        .collect();
    let ground = Ground {
        hard: &hard,
        walls: &walls,
        courses: &courses,
        water: &water,
    };
    let mut tests = Counts::default();
    let paths = channels(&farms, &ground, &mut tests);
    let d = PyDict::new(py);
    d.set_item("paths", paths)?;
    d.set_item("counts", tests.0)?;
    Ok(d)
}
