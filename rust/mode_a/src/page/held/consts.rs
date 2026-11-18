//! The page writer's constants as the Python's `consts` case listed them (feature 449 T150, part A's lockstep), in the `pj` shape; a
//! live-tree case since part B (the plain cursor's kinds are read from `page-text.json`).
//!
//! Research: the page writer's lockstep constants - NONE: the port's constants listed, deciding nothing about a building

use std::path::Path;

use l7r_gate_research::Error;
use serde_json::{json, Value};

use super::call::pj;
use crate::page::{self, hits, merge};
use crate::{dwellings, place, raster};

fn sorted(items: &[&str]) -> Vec<String> {
    let mut v: Vec<String> = items.iter().map(|s| (*s).to_owned()).collect();
    v.sort();
    v
}

fn d(pairs: Vec<Value>) -> Value {
    json!({"d": Value::Array(pairs)})
}

/// The constants, as the Python lists them.
///
/// # Errors
/// `page-text.json` unreadable.
pub fn consts(tree: &Path) -> Result<Value, Error> {
    let widen = d(hits::HIT_WIDEN
        .iter()
        .map(|(k, (a, b, c))| json!([k, pj(&json!([a, b, c]))]))
        .collect());
    let regions: Vec<Value> = hits::HIT_REGIONS
        .iter()
        .map(|(k, roles)| json!([k, d(roles.iter().map(|(r, c)| json!([r, c])).collect())]))
        .collect();
    let mut plain = page::plain_cursor(tree)?;
    plain.sort();
    let f = |x: f64| pj(&json!(x));
    let fields: Vec<(&str, Value)> = vec![
        ("UNCLASSED_CAP", json!(page::UNCLASSED_CAP)),
        ("TILE", f(merge::TILE)),
        ("TILE_MIN", json!(merge::TILE_MIN)),
        ("SKIP_CAP", json!(merge::SKIP_CAP)),
        ("HIT_WIDEN", widen),
        ("HIT_ON_TOP", json!(sorted(&hits::HIT_ON_TOP))),
        ("HIT_PRIORITY", json!(hits::HIT_PRIORITY)),
        ("HIT_KEEP_CLEAR", json!(hits::HIT_KEEP_CLEAR)),
        ("HIT_WIDEN_FACTOR", f(hits::HIT_DEFAULT.0)),
        ("HIT_WIDEN_MIN", f(hits::HIT_DEFAULT.1)),
        ("HIT_REGIONS", json!(regions)),
        ("NOT_RENDERED", json!(sorted(&page::NOT_RENDERED))),
        ("PLAIN_CURSOR", json!(plain)),
        ("RASTER_R", f(raster::RASTER_R)),
        ("PICTURE_FORMAT", json!(raster::PICTURE_FORMAT)),
        ("PICTURE_QUALITY", json!(raster::PICTURE_QUALITY)),
        ("PICTURE_SUBSAMPLING", json!(raster::PICTURE_SUBSAMPLING)),
        ("PICTURE_MIME", json!(raster::PICTURE_MIME)),
        ("TILE_MPX", f(raster::TILE_MPX)),
        ("TILE_WORKERS", json!(raster::TILE_WORKERS)),
        ("RESVG_SLOTS", json!(raster::RESVG_SLOTS)),
        ("OFFMAP_MARGIN", f(raster::OFFMAP_MARGIN)),
        ("PALETTE_STEP", json!(raster::PALETTE_STEP)),
        ("PALETTE_ROW", json!(raster::PALETTE_ROW)),
        ("PALETTE_MAX", json!(raster::PALETTE_MAX)),
        ("RESVG_FONT_ARGS", json!(raster::RESVG_FONT_ARGS)),
        (
            "BOXGRID",
            json!([f(merge::BoxGrid::CELL), merge::BoxGrid::BIG]),
        ),
        ("PER_HOUSEHOLD", json!(place::PER_HOUSEHOLD)),
        (
            "DOMAIN",
            json!([
                place::HAMLETS_PER_DOMAIN,
                place::VILLAGES_PER_DOMAIN,
                place::HAMLET_SHARE
            ]),
        ),
        (
            "WIND_NAMES",
            d(place::WIND_NAMES
                .iter()
                .map(|(k, v)| json!([k, v]))
                .collect()),
        ),
        (
            "SIDES_WORDS",
            d(place::SIDES_WORDS
                .iter()
                .map(|(k, v)| json!([k, v]))
                .collect()),
        ),
        ("PLACE_KEYS", json!(place::PLACE_KEYS)),
        ("LANE", json!(place::LANE)),
        ("WINDBREAK", json!(place::WINDBREAK)),
        ("HOMESTEAD_GROVE", json!(place::HOMESTEAD_GROVE)),
        ("DWELLING_KINDS", json!(sorted(&dwellings::DWELLING_KINDS))),
        ("BUSINESS_KINDS", json!(sorted(&dwellings::BUSINESS_KINDS))),
        ("HOUSEHOLD", json!(dwellings::HOUSEHOLD)),
        ("TEST_RENDER_PX", json!(1200)),
        ("DEFS", json!(crate::sheet::DEFS)),
    ];
    assert!((raster::TEST_RENDER_PX - 1200.0).abs() < f64::EPSILON);
    Ok(d(fields.into_iter().map(|(k, v)| json!([k, v])).collect()))
}
