//! The lane law's water's unit tests (feature 444 T30).
//!
//! Research:
//!     the water's tests - NONE: fixtures and assertions, deciding nothing about the place

use super::water::{
    corners_clear, crossing_deck, deck_quad, lands_dry, off_square, seat_deck, Waters,
};
use super::Counts;
use crate::ways::track::poly_box;

fn square(x0: f64, y0: f64, x1: f64, y1: f64) -> Vec<(f64, f64)> {
    vec![(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
}

#[test]
fn a_run_crosses_each_brook_once_at_a_ford_square_and_where_a_deck_seats() {
    let mut t = Counts::default();
    let brook = vec![(0.0, 100.0), (400.0, 100.0)];
    let w = Waters {
        brooks: vec![brook.clone()],
        channels: vec![vec![(0.0, 300.0), (400.0, 300.0)]],
        crossed: vec![(brook.clone(), 6.0)],
        fords: vec![(200.0, 100.0)],
        ..Waters::default()
    };
    // square at the ford: lawful
    assert!(!w.crossing_fault(&[(200.0, 50.0), (200.0, 150.0)], 3.0, &mut t));
    // off the ford, over and back, off square
    assert!(w.off_a_ford(&[(50.0, 50.0), (50.0, 150.0)], &mut t));
    assert!(w.crossing_fault(&[(50.0, 50.0), (50.0, 150.0)], 3.0, &mut t));
    assert!(w.crossing_fault(
        &[(195.0, 50.0), (195.0, 150.0), (205.0, 150.0), (205.0, 50.0)],
        3.0,
        &mut t
    ));
    assert!(w.oblique(&[(180.0, 50.0), (220.0, 150.0)], &mut Counts::default()));
    assert!(w.oblique(&[(150.0, 250.0), (250.0, 350.0)], &mut Counts::default()));
    assert!(!w.oblique(&[(150.0, 500.0), (250.0, 600.0)], &mut Counts::default()));
    assert!(w.crossing_fault(&[(180.0, 50.0), (220.0, 150.0)], 3.0, &mut t));
    assert!((off_square((0.0, 0.0), (0.0, 1.0), (0.0, 0.0), (1.0, 0.0))).abs() < 1e-9);
    // a deck on paddy, or on what stands, does not seat
    let wet = Waters {
        wet: vec![square(190.0, 105.0, 210.0, 130.0)],
        ..Waters {
            brooks: vec![],
            channels: vec![],
            crossed: vec![(brook.clone(), 6.0)],
            fords: vec![],
            wet: vec![],
            deck_forbidding: vec![],
            boxes: std::cell::OnceCell::new(),
        }
    };
    assert!(wet.undeckable(&[(200.0, 50.0), (200.0, 150.0)], 3.0, &mut t));
    let well = square(198.0, 112.0, 202.0, 116.0);
    let stood = Waters {
        deck_forbidding: vec![(well.clone(), poly_box(&well))],
        crossed: vec![(brook.clone(), 6.0)],
        ..Waters::default()
    };
    assert!(stood.undeckable(&[(200.0, 50.0), (200.0, 150.0)], 3.0, &mut t));
    let far = square(900.0, 900.0, 910.0, 910.0);
    let clear = Waters {
        deck_forbidding: vec![(far.clone(), poly_box(&far))],
        crossed: vec![(brook.clone(), 6.0)],
        ..Waters::default()
    };
    assert!(!clear.undeckable(&[(200.0, 50.0), (200.0, 150.0)], 3.0, &mut t));
}

#[test]
fn a_deck_is_grown_then_skewed_until_its_corners_clear() {
    let mut t = Counts::default();
    let straight = [(0.0, 0.0), (100.0, 0.0)];
    let q = deck_quad((0.0, 0.0), 10.0, 4.0, 90.0);
    assert!((q[0].0 - 2.0).abs() < 1e-9 && (q[0].1 + 5.0).abs() < 1e-9);
    assert!(corners_clear(
        (50.0, 0.0),
        90.0,
        40.0,
        3.0,
        &straight,
        5.0,
        &mut t
    ));
    assert!(!corners_clear(
        (50.0, 0.0),
        90.0,
        4.0,
        3.0,
        &straight,
        5.0,
        &mut t
    ));
    // square: seated as solved; near-parallel to a bending course: grown, then skewed
    let (rot, span, seated) = seat_deck(
        ((50.0, 0.0), 90.0, 30.0, 3.0),
        &straight,
        8.0,
        (straight[0], straight[1]),
        &mut t,
    );
    assert!(seated && (rot - 90.0).abs() < 1e-9 && (span - 30.0).abs() < 1e-9);
    let hopeless = [
        (0.0, 0.0),
        (100.0, 0.0),
        (100.0, 1.0),
        (0.0, 1.0),
        (0.0, 2.0),
        (100.0, 2.0),
    ];
    let (r3, s3, ok3) = seat_deck(
        ((50.0, 1.0), 0.0, 10.0, 3.0),
        &hopeless,
        50.0,
        (hopeless[0], hopeless[1]),
        &mut t,
    );
    assert!(!ok3 && r3 == 0.0 && (s3 - 10.0).abs() < 1e-12);
    let (_, _, ok4) = seat_deck(
        ((50.0, 1.0), 0.0, 10.0, 3.0),
        &hopeless,
        50.0,
        ((0.0, 0.0), (0.0, 0.0)),
        &mut t,
    );
    assert!(!ok4);
    // a skew that seats where growth alone does not
    let elbow = [(-100.0, 0.0), (100.0, 0.0), (100.0, 60.0)];
    let (r5, _, ok5) = seat_deck(
        ((60.0, 0.0), 80.0, 10.0, 3.0),
        &elbow,
        8.0,
        (elbow[0], elbow[1]),
        &mut t,
    );
    assert!(ok5 || (r5 - 80.0).abs() < 1e-9);
    let hook = [
        (-100.0, 0.0),
        (100.0, 0.0),
        (100.0, 500.0),
        (5.0, 500.0),
        (5.0, 10.0),
    ];
    let (r6, _, ok6) = seat_deck(
        ((0.0, 0.0), 90.0, 21.0, 3.0),
        &hook,
        4.0,
        (hook[0], hook[1]),
        &mut t,
    );
    assert!(ok6 && r6 > 90.0);
    assert!(lands_dry((0.0, 0.0), 0.0, 10.0, 3.0, &[]));
    assert!(!lands_dry(
        (0.0, 0.0),
        0.0,
        10.0,
        3.0,
        &[square(4.0, 0.0, 10.0, 5.0)]
    ));
    let (p, _, span, seated) = crossing_deck(
        ((50.0, -20.0), (50.0, 20.0), 3.0),
        ((0.0, 0.0), (100.0, 0.0), 6.0),
        &straight,
        &[],
        &mut t,
    );
    assert!(seated && p == (50.0, 0.0) && (span - 26.0).abs() < 1e-9);
}
