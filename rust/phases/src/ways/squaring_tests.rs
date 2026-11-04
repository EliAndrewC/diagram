//! The squaring's unit tests (feature 444 T30).
//!
//! Research:
//!     the squaring's tests - NONE: fixtures and assertions, deciding nothing about the place

use super::squaring::{
    boxes_meet, kink_spans, square_crossings, square_run, squared_against, water, Kink,
};
use super::Counts;

#[test]
fn a_crossing_off_square_is_squared_on_a_leg_and_a_square_one_left() {
    let mut t = Counts::default();
    let brook = [(0.0, 0.0), (100.0, 0.0)];
    // square already: left as drawn
    let sq = square_crossings(&[(50.0, -50.0), (50.0, 50.0)], &brook, 5.0, &mut t);
    assert_eq!(sq, vec![(50.0, -50.0), (50.0, 50.0)]);
    // oblique: a leg along the brook's normal through the crossing, 6 ft either side
    let ob = square_crossings(&[(0.0, -50.0), (100.0, 50.0)], &brook, 5.0, &mut t);
    assert_eq!(ob.len(), 4);
    assert!((ob[1].0 - 50.0).abs() < 1e-9 && (ob[1].1 + 6.0).abs() < 1e-9);
    assert!((ob[2].0 - 50.0).abs() < 1e-9 && (ob[2].1 - 6.0).abs() < 1e-9);
    // crossed against the brook's own direction: the normal flipped to the run's side
    let back = square_crossings(&[(100.0, 50.0), (0.0, -50.0)], &brook, 5.0, &mut t);
    assert!(back[1].1 > 0.0 && back[2].1 < 0.0);
    // an elbow inside the water is dropped first
    let el = square_crossings(
        &[(0.0, -50.0), (48.0, 2.0), (100.0, 50.0)],
        &brook,
        5.0,
        &mut t,
    );
    assert!(!el.contains(&(48.0, 2.0)));
    // a run that starts and ends too near the water to hold the leg starts and ends on it
    let near = square_crossings(&[(48.0, -3.0), (52.0, 3.0)], &brook, 5.0, &mut t);
    assert_eq!(near.len(), 2);
    assert!((near[0].1 + 6.0).abs() < 1e-9 && (near[1].1 - 6.0).abs() < 1e-9);
    // a zero-length segment and a zero-length brook leg cross nothing
    let z = square_crossings(
        &[(5.0, 5.0), (5.0, 5.0)],
        &[(0.0, 0.0), (0.0, 0.0), (10.0, 0.0)],
        1.0,
        &mut t,
    );
    assert_eq!(z.len(), 2);
    // one segment over a bending brook twice: each crossing squared, nearest first
    let two = square_crossings(
        &[(-50.0, 0.0), (150.0, 0.0)],
        &[(0.0, 10.0), (50.0, -10.0), (100.0, 10.0)],
        2.0,
        &mut t,
    );
    assert_eq!(two.len(), 6);
    assert!(two[1].0 < two[3].0);
    // a parallel run along the brook's line touches no crossing
    assert_eq!(
        square_crossings(&[(-10.0, 0.0), (-5.0, 0.0)], &brook, 1.0, &mut t).len(),
        2
    );
}

#[test]
fn kinks_the_longer_leg_and_the_run_squared_against_each_water() {
    let mut t = Counts::default();
    assert_eq!(kink_spans(&[(0.0, 0.0), (10.0, 0.0)]), vec![]);
    assert_eq!(
        kink_spans(&[(0.0, 0.0), (50.0, 0.0), (0.0, 5.0)]),
        vec![Kink::DoublesBack(1)]
    );
    assert_eq!(
        kink_spans(&[(0.0, 0.0), (50.0, 0.0), (50.0, 20.0), (100.0, 20.0)]),
        vec![Kink::Kinks(1, 2)]
    );
    assert_eq!(kink_spans(&[(0.0, 0.0), (0.0, 0.0), (10.0, 0.0)]), vec![]);
    assert_eq!(
        kink_spans(&[(0.0, 0.0), (50.0, 0.0), (50.0, 60.0), (100.0, 60.0)]),
        vec![]
    );
    // an oblique approach squared on the short leg kinks: squared again on the longer one
    let brook = [(0.0, 0.0), (200.0, 0.0)];
    let q = [(0.0, -30.0), (200.0, 30.0)];
    let r = squared_against(&q, &brook, 5.0, &mut t);
    assert!(kink_spans(&r).is_empty());
    assert!(r.iter().any(|p| (p.1 - 22.0).abs() < 1e-6));
    // a square crossing: left as it was
    let sq = [(50.0, -50.0), (50.0, 50.0)];
    assert_eq!(squared_against(&sq, &brook, 5.0, &mut t), sq.to_vec());
    // out of a water's reach the run is untouched; in it, squared
    let waters = vec![
        (brook.to_vec(), 5.0),
        water(vec![(5000.0, 5000.0), (5100.0, 5000.0)], 4.0),
    ];
    assert!((waters[1].1 - 8.0).abs() < 1e-12);
    assert_eq!(square_run(&q, &waters, &mut t).len(), r.len());
    assert!(!boxes_meet(&[], &brook, 1.0) && boxes_meet(&q, &brook, 0.0));
    assert!(!boxes_meet(&[(0.0, 500.0)], &brook, 1.0));
}
