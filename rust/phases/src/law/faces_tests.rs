//! The web's faces' unit tests (feature 444 T30).
//!
//! Research:
//!     the faces' tests - NONE: fixtures and assertions, deciding nothing about the place

use super::faces::{needles, web_faces, Face};
use super::Counts;

#[test]
fn a_sliver_between_two_ways_is_a_needle_and_a_wide_loop_is_not() {
    let mut t = Counts::default();
    let thin = [
        vec![(0.0, 0.0), (100.0, 0.0)],
        vec![(0.0, 0.0), (50.0, 5.0), (100.0, 0.0)],
    ];
    assert_eq!(needles(&thin, &mut t), 1);
    let wide = [
        vec![(0.0, 0.0), (100.0, 0.0)],
        vec![(0.0, 0.0), (50.0, 80.0), (100.0, 0.0)],
    ];
    let f = web_faces(&wide, &mut t);
    assert_eq!(f.len(), 1);
    assert!(!f[0].is_needle() && (f[0].area - 4000.0).abs() < 1e-6);
    // an X and a lone way bound nothing; a way of one point or under a foot is no tread
    let x = [
        vec![(0.0, 0.0), (100.0, 100.0)],
        vec![(0.0, 100.0), (100.0, 0.0)],
    ];
    assert!(web_faces(&x, &mut t).is_empty());
    assert!(web_faces(&[vec![(0.0, 0.0), (10.0, 0.0)]], &mut t).is_empty());
    assert!(web_faces(
        &[
            vec![(0.0, 0.0)],
            vec![(0.0, 0.0), (0.5, 0.0)],
            vec![(5.0, 5.0), (5.0, 5.0), (9.0, 9.0)]
        ],
        &mut t
    )
    .is_empty());
    // a triangle closed by a way crossing two others, a dangle beyond it pruned; a T standing on a tread noded there
    let tri = [
        vec![(-50.0, 0.0), (150.0, 0.0)],
        vec![(0.0, -20.0), (50.0, 100.0)],
        vec![(100.0, -20.0), (50.0, 100.0), (50.0, 150.0)],
    ];
    let ft = web_faces(&tri, &mut t);
    assert_eq!(ft.len(), 1);
    let tee = [
        vec![(0.0, 0.0), (100.0, 0.0)],
        vec![(0.0, 0.0), (50.0, 60.0)],
        vec![(50.0, 60.0), (50.0, 0.0)],
    ];
    assert_eq!(web_faces(&tee, &mut t).len(), 1);
    // a speck is no needle
    let speck = Face {
        ring: vec![],
        area: 0.01,
        perimeter: 0.5,
    };
    assert!(!speck.is_needle());
}
