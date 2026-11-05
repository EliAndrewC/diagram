//! The hard ground's distance and level sets: their unit tests, against shapely's own figures (feature 444 T30).
//!
//! Research:
//!     the level set's tests - NONE: fixtures and assertions, deciding nothing about the place

use super::level::{interpolate, length, project, ring_dist, Hard};
use super::Counts;
use crate::field::fan::Pt;

fn hard(t: &mut Counts) -> Hard {
    let field = vec![
        (200.0, 1500.0),
        (2200.0, 1500.0),
        (2200.0, 2300.0),
        (200.0, 2300.0),
    ];
    let pond = vec![
        (2600.0, 600.0),
        (2800.0, 600.0),
        (2800.0, 800.0),
        (2600.0, 800.0),
    ];
    Hard::new(
        &[field, pond, vec![(0.0, 0.0), (1.0, 1.0)]],
        &[
            ((1000.0, 1100.0), (1000.0, 1490.0), 8.0),
            ((5.0, 5.0), (5.0, 5.0), 3.0),
        ],
        t,
    )
}

#[test]
fn the_distance_to_the_hard_ground_is_shapelys() {
    let mut t = Counts::default();
    let h = hard(&mut t);
    assert!(!h.is_empty());
    for (p, want) in [
        ((1200.0, 1250.0), 192.0),
        ((1000.0, 1050.0), 42.0),
        ((500.0, 1600.0), 0.0),
        ((2700.0, 500.0), 100.0),
    ] {
        assert!((h.dist(p, 1e9, &mut t) - want).abs() < 1e-6, "{p:?}");
    }
    // read no farther than its cap
    assert!((h.dist((1200.0, 1250.0), 50.0, &mut t) - 50.0).abs() < 1e-12);
    assert!(Hard::new(&[], &[], &mut t)
        .grown_rings(10.0, &mut t)
        .is_empty());
}

#[test]
fn the_grown_ground_s_rings_are_shapelys_to_a_foot() {
    let mut t = Counts::default();
    let h = hard(&mut t);
    for (d, near, far) in [(24.0, 6539.23, 950.74), (60.0, 6734.38, 1176.84)] {
        let rings = h.grown_rings(d, &mut t);
        assert_eq!(rings.len(), 2, "two parts at {d}");
        let mut lens: Vec<f64> = rings.iter().map(|r| length(r)).collect();
        lens.sort_by(f64::total_cmp);
        // the level set's chords cut each round corner short by under a cell's sagitta: within a foot a hundred feet of ring
        assert!((lens[1] - near).abs() < near / 100.0 && (lens[0] - far).abs() < far / 100.0);
        let anchor: Pt = (1200.0, 1250.0);
        let ring = rings
            .iter()
            .min_by(|a, b| ring_dist(a, anchor).total_cmp(&ring_dist(b, anchor)))
            .unwrap();
        assert!((ring_dist(ring, anchor) - (192.0 - d)).abs() < 1.0);
    }
}

#[test]
fn a_ring_is_walked_by_its_arc_length() {
    let sq = vec![(0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0)];
    assert!((length(&sq) - 40.0).abs() < 1e-12);
    assert!(
        (project(&sq, (5.0, -3.0)) - 5.0).abs() < 1e-12
            && (project(&sq, (13.0, 5.0)) - 15.0).abs() < 1e-12
    );
    assert_eq!(interpolate(&sq, 15.0), (10.0, 5.0));
    assert_eq!(interpolate(&sq, -5.0), (0.0, 5.0));
    assert_eq!(
        interpolate(&[(1.0, 1.0), (1.0, 1.0), (1.0, 1.0)], 5.0),
        (1.0, 1.0)
    );
    assert!((project(&[(1.0, 1.0), (1.0, 1.0), (3.0, 1.0)], (2.0, 5.0)) - 1.0).abs() < 1e-12);
}

#[test]
fn a_saddle_cell_is_joined_through_its_center_where_its_mean_is_below_the_level() {
    use super::level::march;
    // a 4 x 4 grid, its border above the level: one interior cell, its diagonal corners below
    let at = |i: usize, j: usize| {
        (
            f64::from(u32::try_from(i).unwrap_or(0)),
            f64::from(u32::try_from(j).unwrap_or(0)),
        )
    };
    let grid = |a: f64, b: f64, c: f64, d: f64| {
        let mut v = vec![1.0; 16];
        (v[5], v[6], v[10], v[9]) = (a, b, c, d);
        v
    };
    // corners north-west and south-east below: apart (two rings) where the mean is above, one ring where below
    assert_eq!(march(&grid(-1.0, 1.0, -1.0, 1.0), (4, 4), &at).len(), 2);
    assert_eq!(march(&grid(-3.0, 1.0, -3.0, 1.0), (4, 4), &at).len(), 1);
    // north-east and south-west below
    assert_eq!(march(&grid(1.0, -1.0, 1.0, -1.0), (4, 4), &at).len(), 2);
    assert_eq!(march(&grid(1.0, -3.0, 1.0, -3.0), (4, 4), &at).len(), 1);
}
