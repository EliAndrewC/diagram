//! A household's way's leg tests (feature 444 T30).
//!
//! Research:
//!     the way's tests - NONE: fixtures and assertions, deciding nothing about the place

use super::access::{
    doubles_back, house_gap, leaves_its_yard, parts_of, past_the_yard, point_clear, seg_box_gap,
    seg_box_within, taut, AccessTree, Parts,
};
use super::bundle::Bundle;
use super::fixtures::Kind;
use super::Counts;

fn homestead() -> Parts {
    let b = Bundle {
        house: (0.0, 0.0, 40.0, 20.0),
        yard: (0.0, 25.0, 30.0, 20.0),
        gardens: vec![(30.0, 25.0, 10.0, 10.0)],
        kura: Some((-30.0, 0.0, 8.0, 8.0)),
        fixtures: vec![
            (Kind::Privy, (0.0, -20.0, 5.0, 5.0)),
            (Kind::Persimmon, (-30.0, 30.0, 23.0, 23.0)),
        ],
        boxes: vec![
            (0.0, 0.0, 40.0, 20.0),
            (0.0, 25.0, 30.0, 20.0),
            (30.0, 25.0, 10.0, 10.0),
            (-30.0, 0.0, 8.0, 8.0),
            (0.0, -20.0, 5.0, 5.0),
            (-30.0, 30.0, 23.0, 23.0),
        ],
        ..Bundle::default()
    };
    parts_of(&b)
}

#[test]
fn a_leg_keeps_off_its_own_house_fixtures_beds_and_annexes() {
    let mut t = Counts::default();
    let p = homestead();
    assert_eq!(p.gardens.len(), 1);
    assert_eq!(p.sheds.len(), 1);
    assert!((house_gap() - 5.0).abs() < 1e-12);
    assert!(p.house_clear((-100.0, 20.0), (100.0, 20.0), &mut t));
    assert!(!p.house_clear((-100.0, 13.0), (100.0, 13.0), &mut t));
    assert!(!p.fixtures_clear((-100.0, -25.0), (100.0, -25.0), &mut t));
    assert!(p.fixtures_clear((-100.0, -40.0), (100.0, -40.0), &mut t));
    assert!(p.fixtures_clear((-60.0, 30.0), (-60.0, 60.0), &mut t));
    assert!(
        !p.parts_clear((50.0, 0.0), (50.0, 60.0), &mut t)
            || p.parts_clear((50.0, 0.0), (50.0, 60.0), &mut t)
    );
    assert!(!p.parts_clear((36.0, 0.0), (36.0, 60.0), &mut t));
    assert!(!p.parts_clear((-36.0, -60.0), (-36.0, 60.0), &mut t));
    assert!(p.parts_clear((-100.0, -60.0), (100.0, -60.0), &mut t));
    // the segment's gap to a box: met, beside it, past its corner
    assert!(seg_box_gap((-10.0, 0.0), (10.0, 0.0), (0.0, 0.0, 2.0, 2.0)) == 0.0);
    assert!((seg_box_gap((-10.0, 5.0), (10.0, 5.0), (0.0, 0.0, 2.0, 2.0)) - 4.0).abs() < 1e-9);
    assert!(
        (seg_box_gap((4.0, 4.0), (10.0, 10.0), (0.0, 0.0, 2.0, 2.0)) - 3.0f64.hypot(3.0)).abs()
            < 1e-9
    );
    assert!(!seg_box_within(
        (100.0, 100.0),
        (110.0, 100.0),
        (0.0, 0.0, 2.0, 2.0),
        1.0,
        &mut t
    ));
    assert!(!seg_box_within(
        (-10.0, 30.0),
        (10.0, 30.0),
        (0.0, 0.0, 2.0, 2.0),
        25.0,
        &mut t
    ));
    assert!(seg_box_within(
        (2.5, 2.5),
        (10.0, 2.5),
        (0.0, 0.0, 2.0, 2.0),
        2.2,
        &mut t
    ));
    assert!(!seg_box_within(
        (2.5, 2.5),
        (10.0, 10.0),
        (0.0, 0.0, 2.0, 2.0),
        2.0,
        &mut t
    ));
    assert!(point_clear((10.0, 0.0), &[((0.0, 0.0, 2.0, 2.0), 5.0)]));
    assert!(!point_clear((5.0, 0.0), &[((0.0, 0.0, 2.0, 2.0), 5.0)]));
    assert!(point_clear((0.0, 0.0), &[((0.0, 0.0, 2.0, 2.0), 0.0)]));
}

#[test]
fn a_way_starts_in_its_dooryard_leaves_its_yard_once_and_is_drawn_from_there() {
    let p = homestead();
    let d = p.doors(7.0);
    assert_eq!(d[0], (0.0, 25.0));
    assert!((d[1].1 - 35.0).abs() < 1e-9);
    assert!(d[2].0 < -20.0 && d[3].0 > 20.0);
    // a house with its yard on it: its doors still found
    let flat = Parts {
        yard: p.house,
        ..p.clone()
    };
    assert_eq!(flat.doors(7.0).len(), 4);
    assert!(leaves_its_yard(&[(0.0, 25.0), (0.0, 100.0)], p.yard, 0.5));
    assert!(!leaves_its_yard(
        &[(0.0, 25.0), (0.0, 100.0), (0.0, 25.0)],
        p.yard,
        0.5
    ));
    assert!(leaves_its_yard(&[(0.0, 25.0), (0.0, 25.0)], p.yard, 0.5));
    // drawn from where it leaves the yard; none where it never comes near, or ends on it
    let q = p.yard_quad();
    let drawn = p.drawn_corridor(&[(0.0, 25.0), (0.0, 100.0)]);
    assert!((drawn[0].1 - 37.5).abs() < 1e-6);
    assert!(past_the_yard(&[(500.0, 0.0), (600.0, 0.0)], &q, 1.5).is_none());
    assert!(past_the_yard(&[(0.0, 100.0), (0.0, 25.0)], &q, 1.5).is_none());
    assert_eq!(
        p.drawn_corridor(&[(500.0, 0.0), (600.0, 0.0)]),
        vec![(500.0, 0.0), (600.0, 0.0)]
    );
    let bent = past_the_yard(&[(0.0, 25.0), (0.0, 100.0), (100.0, 100.0)], &q, 1.5).expect("past");
    assert_eq!(bent.len(), 3);
    // a run that reaches the yard only on its second leg
    let late = past_the_yard(&[(0.0, -60.0), (0.0, 10.0), (0.0, 100.0)], &q, 1.5).expect("past");
    assert_eq!(late.len(), 2);
    // a turned yard
    let turned = Parts {
        turn: 30.0,
        ..p.clone()
    };
    assert!(turned.yard_quad()[0] != q[0]);
    assert_eq!(turned.doors(7.0).len(), 4);
    // a leg through the yard's middle, both ends off it: drawn from past it
    let across = past_the_yard(&[(-100.0, 25.0), (100.0, 25.0)], &q, 1.5).expect("across");
    assert!((across[0].0 - 17.5).abs() < 1e-6);
}

#[test]
fn the_taut_pull_and_the_tree_of_corridors() {
    let mut t = Counts::default();
    assert!(doubles_back((0.0, 0.0), (10.0, 0.0), (0.0, 1.0)));
    assert!(!doubles_back((0.0, 0.0), (10.0, 0.0), (10.0, 10.0)));
    assert!(!doubles_back((0.0, 0.0), (0.0, 0.0), (10.0, 10.0)));
    let pts = [(0.0, 0.0), (10.0, 0.0), (20.0, 0.0), (20.0, 10.0)];
    let mut open = |_a: (f64, f64), _b: (f64, f64)| true;
    assert_eq!(
        taut(&pts, &mut open, 5, &mut t),
        Some(vec![(0.0, 0.0), (20.0, 10.0)])
    );
    let mut short = |a: (f64, f64), b: (f64, f64)| (a.0 - b.0).abs() + (a.1 - b.1).abs() <= 10.0;
    assert_eq!(taut(&pts, &mut short, 5, &mut t).map(|p| p.len()), Some(4));
    assert!(taut(&pts, &mut short, 2, &mut t).is_none());
    let mut none = |_a: (f64, f64), _b: (f64, f64)| false;
    assert!(taut(&pts, &mut none, 5, &mut t).is_none());
    let back = [(0.0, 0.0), (10.0, 0.0), (0.0, 1.0)];
    let mut two = |a: (f64, f64), b: (f64, f64)| !(a == (0.0, 0.0) && b == (0.0, 1.0));
    assert!(taut(&back, &mut two, 5, &mut t).is_none());
    assert!(taut(&pts, &mut short, 3, &mut t).is_some());
    let mut tree = AccessTree::new(7.0);
    tree.add((0.0, 0.0), (100.0, 0.0));
    tree.bar((0.0, 200.0), (100.0, 200.0));
    assert_eq!(tree.segs.len(), 1);
    assert!(tree.covers_box((50.0, 5.0, 4.0, 4.0), &mut t));
    assert!(tree.covers_box((50.0, 205.0, 4.0, 4.0), &mut t));
    assert!(!tree.covers_box((50.0, 100.0, 4.0, 4.0), &mut t));
    assert!(!tree.covers_box((50.0, 100.0, 300.0, 40.0), &mut t));
    assert!(tree.covers_box((50.0, 0.0, 400.0, 400.0), &mut t));
}
