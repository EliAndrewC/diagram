//! The plain geometry held to the Python's figures (feature 449 T151; each value printed by `labels/geom.py` under `CPython` 3.14.4,
//! 2026-11-18).
//!
//! Research:
//!     its tests - NONE: the port held to the Python's answers, deciding nothing about a building

use super::{
    area_centroid, bbox, box_gap, centroid, inside, least, most, nearest_points, poly_gap,
    poly_seg_gap, rect, seg_closest, seg_dist, segments_cross, Pt,
};

const SQ: [Pt; 4] = [(0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0)];

#[test]
#[expect(clippy::float_cmp, reason = "each figure is Python's to the bit")]
fn the_measures_are_the_python_s() {
    assert_eq!(
        rect(5.0, 5.0, 2.0, 1.0, 30.0),
        [
            (3.767_949_192_431_122_4, 3.133_974_596_215_561),
            (7.232_050_807_568_878, 5.133_974_596_215_562),
            (6.232_050_807_568_878, 6.866_025_403_784_438),
            (2.767_949_192_431_122_4, 4.866_025_403_784_438)
        ]
    );
    assert_eq!(
        bbox(&[(3.0, 1.0), (1.0, 4.0), (2.0, 0.0)]),
        (1.0, 0.0, 3.0, 4.0)
    );
    assert_eq!(
        centroid(&[(0.0, 0.0), (1.0, 0.0), (0.0, 1.0)]),
        (0.333_333_333_333_333_3, 0.333_333_333_333_333_3)
    );
    assert_eq!(
        area_centroid(&[(0.0, 0.0), (2.0, 0.0), (2.0, 1.0)]),
        (1.333_333_333_333_333_3, 0.333_333_333_333_333_3)
    );
    // a degenerate outline's centroid is its vertices' mean
    assert_eq!(
        area_centroid(&[(0.0, 0.0), (1.0, 1.0), (2.0, 2.0)]),
        (1.0, 1.0)
    );
    assert_eq!(
        (inside(5.0, 5.0, &SQ), inside(15.0, 5.0, &SQ)),
        (true, false)
    );
    assert_eq!(seg_closest((1.0, 1.0), (0.0, 0.0), (0.0, 0.0)), (0.0, 0.0));
    assert_eq!(seg_dist((5.0, 5.0), (0.0, 0.0), (10.0, 0.0)), 5.0);
    assert_eq!(box_gap((0.0, 0.0, 1.0, 1.0), (4.0, 5.0, 6.0, 6.0)), 5.0);
    assert_eq!(
        (
            least([3.0, 1.0, 2.0]),
            most([3.0, 1.0, 4.0]),
            least([]),
            most([])
        ),
        (1.0, 4.0, f64::INFINITY, f64::NEG_INFINITY)
    );
}

#[test]
#[expect(clippy::float_cmp, reason = "each figure is Python's to the bit")]
fn outlines_meet_and_part_as_the_python_s() {
    // crossing, touching end to end, and parallel apart
    assert!(segments_cross(
        (0.0, 0.0),
        (10.0, 10.0),
        (0.0, 10.0),
        (10.0, 0.0)
    ));
    assert!(segments_cross(
        (0.0, 0.0),
        (5.0, 0.0),
        (5.0, 0.0),
        (9.0, 3.0)
    ));
    assert!(!segments_cross(
        (0.0, 0.0),
        (1.0, 0.0),
        (0.0, 1.0),
        (1.0, 1.0)
    ));
    let inner = [(2.0, 2.0), (3.0, 2.0), (3.0, 3.0), (2.0, 3.0)];
    let far = [(20.0, 0.0), (30.0, 0.0), (30.0, 10.0), (20.0, 10.0)];
    let cross = [(5.0, -5.0), (6.0, -5.0), (6.0, 15.0), (5.0, 15.0)];
    // held either way, crossing, apart, and against an open road
    assert_eq!(nearest_points(&inner, &SQ, true), ((2.0, 2.0), (2.0, 2.0)));
    assert_eq!(nearest_points(&SQ, &inner, true), ((2.0, 2.0), (2.0, 2.0)));
    assert_eq!(nearest_points(&SQ, &cross, true), ((0.0, 0.0), (0.0, 0.0)));
    assert_eq!(nearest_points(&SQ, &far, true), ((10.0, 0.0), (20.0, 0.0)));
    assert_eq!(
        nearest_points(&SQ, &[(12.0, -3.0), (12.0, 20.0), (40.0, 4.0)], false),
        ((10.0, 0.0), (12.0, 0.0))
    );
    assert_eq!(poly_gap(&SQ, &far), 10.0);
    assert_eq!(poly_seg_gap(&SQ, (5.0, 5.0), (50.0, 5.0)), 0.0);
    assert_eq!(poly_seg_gap(&SQ, (-5.0, 5.0), (50.0, 5.0)), 0.0);
    assert_eq!(poly_seg_gap(&SQ, (13.0, 0.0), (13.0, 3.0)), 3.0);
}
