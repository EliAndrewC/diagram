//! The lane law's unit tests (feature 444 T30).
//!
//! Research:
//!     the law's tests - NONE: fixtures and assertions, deciding nothing about the place

use super::rules::{
    bends_badly, breaks_through, connector_keeps_the_law, crossing_points, forbidden_segment,
    ribbon, sat_overlap,
};
use super::Counts;
use crate::ways::track::poly_box;

#[test]
fn the_track_bends_like_a_path_through_no_building_and_over_each_brook_once() {
    let mut t = Counts::default();
    assert!(bends_badly(&[(0.0, 0.0), (50.0, 0.0), (0.0, 5.0)]));
    assert!(!bends_badly(&[(0.0, 0.0), (50.0, 0.0)]));
    let solid = [(40.0, -5.0, 60.0, 5.0)];
    assert_eq!(
        breaks_through(&[(0.0, 0.0), (100.0, 0.0)], &solid),
        vec![(0, (50.0, 0.0))]
    );
    assert!(breaks_through(&[(30.0, 0.0), (70.0, 0.0)], &solid).is_empty());
    assert!(breaks_through(&[(0.0, 50.0), (100.0, 50.0)], &solid).is_empty());
    let brook = [(0.0, 10.0), (50.0, -10.0), (100.0, 10.0)];
    let x = crossing_points(&[(-10.0, 0.0), (110.0, 0.0)], &brook, &mut t);
    assert_eq!(x.len(), 2);
    assert!(x[0].1 .0 < x[1].1 .0);
    assert!(crossing_points(&[(0.0, 500.0), (10.0, 500.0)], &brook, &mut t).is_empty());
    assert!(crossing_points(&[(0.0, 0.0)], &brook, &mut t).is_empty());
    // the matrix: a ribbon on a forbidden extent, beside it, or on its box alone
    assert!(sat_overlap(
        &ribbon((0.0, 0.0), (10.0, 0.0), 1.0),
        &ribbon((5.0, -5.0), (5.0, 5.0), 1.0)
    ));
    assert!(!sat_overlap(
        &ribbon((0.0, 0.0), (10.0, 0.0), 1.0),
        &ribbon((0.0, 5.0), (10.0, 5.0), 1.0)
    ));
    assert_eq!(ribbon((1.0, 1.0), (1.0, 1.0), 1.0)[0], (1.0, 1.0));
    let plot = vec![(40.0, 2.0), (60.0, 2.0), (60.0, 20.0), (40.0, 20.0)];
    let far = vec![(400.0, 2.0), (600.0, 2.0), (600.0, 20.0)];
    let forbidding = [
        (plot.clone(), poly_box(&plot)),
        (far.clone(), poly_box(&far)),
    ];
    assert_eq!(
        forbidden_segment(
            &[(0.0, 50.0), (0.0, 0.0), (100.0, 0.0)],
            6.0,
            &forbidding,
            &mut t
        ),
        Some(1)
    );
    assert_eq!(
        forbidden_segment(&[(0.0, -10.0), (100.0, -10.0)], 6.0, &forbidding, &mut t),
        None
    );
    // the connector, against each rule
    let ok = [(0.0, -30.0), (100.0, -30.0)];
    assert!(connector_keeps_the_law(
        &ok,
        &solid,
        &forbidding,
        &[brook.to_vec()],
        &mut t
    ));
    assert!(!connector_keeps_the_law(
        &[(0.0, 0.0), (100.0, 0.0)],
        &solid,
        &[],
        &[],
        &mut t
    ));
    assert!(!connector_keeps_the_law(
        &[(0.0, -10.0), (100.0, -10.0), (0.0, -5.0)],
        &[],
        &[],
        &[],
        &mut t
    ));
    assert!(!connector_keeps_the_law(
        &[(0.0, 0.0), (100.0, 0.0)],
        &[],
        &forbidding,
        &[],
        &mut t
    ));
    assert!(!connector_keeps_the_law(
        &[(-10.0, 0.0), (110.0, 0.0)],
        &[],
        &[],
        &[brook.to_vec()],
        &mut t
    ));
}
