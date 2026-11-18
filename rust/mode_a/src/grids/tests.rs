//! Its unit tests (feature 449 T174).
//!
//! Research:
//!     its tests - NONE: tests, deciding nothing about a building

use super::{
    coverage, grids, perimeter_band, perimeter_hugging_pct, region_density, top_vacant_rects,
    RegionTile, VacantRect,
};
use crate::parse::{parse_svg, ParsedPlan, Rect};
use crate::py::uncaught;

/// A court of 40 x 26 px on a half-pixel, one building, one divider (every figure below is `CPython` 3.14.4's on the same sheet).
const SHEET: &str = r##"<svg><rect id="precinct" x="0.5" y="0" width="40" height="26" fill="url(#court-earth)"/><rect x="0.5" y="0" width="25" height="21" fill="#DDB87A"/><g stroke="#3F3A30" stroke-width="2"><line x1="30" y1="0" x2="30" y2="26"/></g></svg>"##;

fn rows(g: &[Vec<bool>]) -> Vec<String> {
    g.iter()
        .map(|r| r.iter().map(|c| if *c { '1' } else { '0' }).collect())
        .collect()
}

#[test]
#[expect(clippy::float_cmp, reason = "each figure is Python's to the bit")]
fn the_grid_measures_are_the_python_s() {
    let plan = parse_svg(SHEET).unwrap();
    let g = grids(&plan, 2).unwrap();
    assert_eq!((g.w, g.h), (21, 14));
    let band = rows(&perimeter_band(&g, 1));
    assert_eq!(band[1], "100000000000011110001");
    assert_eq!(band[0], "1".repeat(21));
    assert!(rows(&perimeter_band(&g, -1))
        .iter()
        .all(|r| !r.contains('1')));
    assert_eq!(coverage(&plan, 2).unwrap(), 0.486_394_557_823_129_24);
    assert_eq!(coverage(&plan, 3).unwrap(), 0.571_428_571_428_571_4);
    assert_eq!(
        perimeter_hugging_pct(&plan, 2.0, 2).unwrap(),
        0.552_447_552_447_552_4
    );
    let v = |w_ft, h_ft, area_sqft, x, y| VacantRect {
        w_ft,
        h_ft,
        area_sqft,
        x,
        y,
        zone: "perimeter",
    };
    let vacant = top_vacant_rects(&plan, 3, 2, 0.0, 2.0).unwrap();
    assert_eq!(
        vacant,
        [
            v(5.333_333_333_333_333, 9.333_333_333_333_334, 50, 26.5, 0.0),
            v(8.666_666_666_666_666, 2.0, 17, 0.5, 22.0),
            v(0.0, 0.0, 0, 0.5, 0.0)
        ]
    );
    assert_eq!(
        vacant.iter().map(VacantRect::orient).collect::<Vec<_>>(),
        ["vertical", "horizontal", "horizontal"]
    );
    assert!(top_vacant_rects(&plan, 3, 2, 150.0, 25.0)
        .unwrap()
        .is_empty());
    let t = |row, col, coverage_pct, interior_sqft| RegionTile {
        row,
        col,
        coverage_pct,
        interior_sqft,
    };
    assert_eq!(
        region_density(&plan, 2, 2, 3).unwrap(),
        [
            t(0, 0, 1.0, 28),
            t(0, 1, 0.285_714_285_714_285_7, 28),
            t(1, 0, 0.8, 35),
            t(1, 1, 0.228_571_428_571_428_56, 35)
        ]
    );
    assert!(region_density(&plan, 0, 2, 2).unwrap().is_empty());
}

#[test]
#[expect(clippy::float_cmp, reason = "each figure is Python's to the bit")]
fn what_the_python_refused_is_refused() {
    let e = |r: Result<f64, l7r_gate_research::Error>| uncaught(&r.unwrap_err());
    let none = ParsedPlan::default();
    assert_eq!(
        e(coverage(&none, 2)),
        "ValueError: min() iterable argument is empty\n"
    );
    let plan = parse_svg(SHEET).unwrap();
    assert_eq!(
        e(coverage(&plan, 0)),
        "ZeroDivisionError: division by zero\n"
    );
    // an interior drawn backwards paints no cell: a share of nothing
    let backwards = ParsedPlan {
        interior: vec![Rect::new(20.0, 20.0, -5.0, 9.0, "", 0)],
        ..ParsedPlan::default()
    };
    assert_eq!(
        e(coverage(&backwards, 2)),
        "ZeroDivisionError: division by zero\n"
    );
    assert_eq!(perimeter_hugging_pct(&backwards, 25.0, 2).unwrap(), 0.0);
    let huge = ParsedPlan {
        interior: vec![Rect::new(0.0, 0.0, 1e12, 1e12, "", 0)],
        ..ParsedPlan::default()
    };
    assert_eq!(e(coverage(&huge, 2)), "MemoryError\n");
    let endless = ParsedPlan {
        interior: vec![Rect::new(0.0, 0.0, f64::INFINITY, 1.0, "", 0)],
        ..ParsedPlan::default()
    };
    assert_eq!(
        e(coverage(&endless, 2)),
        "ValueError: cannot convert float NaN to integer\n"
    );
}
