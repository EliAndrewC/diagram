//! The track out's unit tests (feature 444 T30).
//!
//! Research:
//!     the track's tests - NONE: fixtures and assertions, deciding nothing about the place

use super::track::{
    connector, crosses_fabric, crossing_lands_on_crop, edge_dist, fabric_hits, grown, in_poly,
    pairs_within, past_the_frame, poly_box, pull_clear, seg_intersect, segments_cross,
    shallow_crossing, Checker, Swept, TrackSite,
};
use super::Counts;
use crate::field::fan::Pt;

fn square(x0: f64, y0: f64, x1: f64, y1: f64) -> Vec<Pt> {
    vec![(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
}

#[test]
fn the_path_rules_measure_crossings_angles_decks_and_samples() {
    let mut t = Counts::default();
    let sq = square(0.0, 0.0, 10.0, 10.0);
    assert!(in_poly((5.0, 5.0), &sq) && !in_poly((15.0, 5.0), &sq));
    assert!(segments_cross(
        (-1.0, 5.0),
        (11.0, 5.0),
        (5.0, -1.0),
        (5.0, 11.0)
    ));
    assert!(!segments_cross(
        (0.0, 0.0),
        (1.0, 0.0),
        (0.0, 1.0),
        (1.0, 1.0)
    ));
    assert_eq!(
        seg_intersect((0.0, 0.0), (2.0, 2.0), (0.0, 2.0), (2.0, 0.0)),
        Some((1.0, 1.0))
    );
    assert!(seg_intersect((0.0, 0.0), (1.0, 0.0), (0.0, 1.0), (1.0, 1.0)).is_none());
    assert!(seg_intersect((0.0, 0.0), (1.0, 1.0), (3.0, 0.0), (2.0, 1.0)).is_none());
    assert!((edge_dist((5.0, 12.0), &sq) - 2.0).abs() < 1e-9);
    // a crossing square is lawful, a slant one is not; a deck beside the crop fouls
    assert!(!shallow_crossing(
        (0.0, -5.0),
        (0.0, 5.0),
        (-5.0, 0.0),
        (5.0, 0.0)
    ));
    assert!(shallow_crossing(
        (-5.0, -1.0),
        (5.0, 1.0),
        (-5.0, 0.0),
        (5.0, 0.0)
    ));
    assert!(!shallow_crossing(
        (0.0, 1.0),
        (1.0, 2.0),
        (-5.0, 0.0),
        (5.0, 0.0)
    ));
    let crop = square(20.0, -5.0, 40.0, 5.0);
    let crops = [crop.as_slice()];
    assert!(crossing_lands_on_crop(
        (10.0, -5.0),
        (10.0, 5.0),
        (0.0, 0.0),
        (30.0, 0.0),
        &crops
    ));
    assert!(!crossing_lands_on_crop(
        (-50.0, -5.0),
        (-50.0, 5.0),
        (-90.0, 0.0),
        (30.0, 0.0),
        &crops
    ));
    assert!(crossing_lands_on_crop(
        (30.0, -5.0),
        (30.0, 5.0),
        (0.0, 0.0),
        (50.0, 0.0),
        &crops
    ));
    assert!(!crossing_lands_on_crop(
        (0.0, 1.0),
        (1.0, 2.0),
        (-5.0, 0.0),
        (5.0, 0.0),
        &crops
    ));
    // two crossings within the deck's distance are a pair, three in a row two pairs, cells apart none
    let pts = [(0.0, 0.0), (10.0, 0.0), (47.0, 0.0), (500.0, 500.0)];
    assert_eq!(pairs_within(&pts, 46.0, &mut t), 2);
    assert_eq!(pairs_within(&pts[..1], 46.0, &mut t), 0);
    assert_eq!(pairs_within(&pts, 0.0, &mut t), 0);
    assert_eq!(pairs_within(&[(45.0, 45.0), (47.0, 47.0)], 46.0, &mut t), 1);
}

#[test]
fn the_checker_counts_each_foul_segment_and_the_decks_too_close() {
    let mut t = Counts::default();
    let crop = square(100.0, 100.0, 200.0, 200.0);
    let brook = [((0.0, 300.0), (400.0, 300.0))];
    let waters = [((50.0, 0.0), (50.0, 400.0)), ((60.0, 0.0), (60.0, 400.0))];
    let chk = Checker::new(
        &[crop.clone(), vec![(0.0, 0.0)]],
        Some((350.0, 50.0, 10.0, 5.0)),
        &brook,
        &waters,
    );
    // a segment wholly inside the crop crosses no edge and is caught by its samples
    assert_eq!(chk.violations(&[(120.0, 150.0), (180.0, 150.0)], &mut t), 1);
    // across the crop, the brook, the pond's berth, and two decks too close
    assert_eq!(chk.violations(&[(80.0, 150.0), (220.0, 150.0)], &mut t), 1);
    assert_eq!(chk.violations(&[(250.0, 250.0), (250.0, 350.0)], &mut t), 1);
    assert_eq!(chk.violations(&[(300.0, 10.0), (300.0, 20.0)], &mut t), 1);
    assert_eq!(chk.violations(&[(0.0, 20.0), (100.0, 20.0)], &mut t), 1);
    assert_eq!(chk.violations(&[(250.0, 250.0), (260.0, 250.0)], &mut t), 0);
    let dry = Checker::new(&[], None, &[], &[]);
    assert_eq!(dry.violations(&[(0.0, 0.0), (10.0, 0.0)], &mut t), 0);
}

#[test]
fn the_fabric_is_fouled_by_a_crossing_a_near_corner_or_a_leg_inside() {
    let mut t = Counts::default();
    let steading = square(100.0, 100.0, 140.0, 140.0);
    let fab = [(steading.clone(), poly_box(&steading))];
    let b = poly_box(&steading);
    assert!(crosses_fabric(
        &[(80.0, 120.0), (160.0, 120.0)],
        &steading,
        b,
        7.0,
        &mut t
    ));
    assert!(crosses_fabric(
        &[(0.0, 145.0), (300.0, 145.0)],
        &steading,
        b,
        7.0,
        &mut t
    ));
    assert!(crosses_fabric(
        &[(120.0, 120.0), (125.0, 125.0)],
        &steading,
        b,
        0.5,
        &mut t
    ));
    assert!(crosses_fabric(
        &[(120.0, 146.0), (120.0, 200.0)],
        &steading,
        b,
        7.0,
        &mut t
    ));
    assert!(!crosses_fabric(
        &[(0.0, 0.0), (10.0, 0.0)],
        &steading,
        b,
        7.0,
        &mut t
    ));
    assert!(!crosses_fabric(
        &[(0.0, 160.0), (300.0, 160.0)],
        &steading,
        b,
        7.0,
        &mut t
    ));
    assert_eq!(
        fabric_hits(&[(80.0, 120.0), (160.0, 120.0)], &fab, 7.0, &mut t),
        1
    );
    assert_eq!(
        fabric_hits(&[(0.0, 0.0), (10.0, 0.0)], &fab, 7.0, &mut t),
        0
    );
}

#[test]
fn the_frame_the_grown_ring_and_the_gateway_pulled_clear() {
    let mut t = Counts::default();
    // east from the middle: to the edge and past it; straight down; from outside the canvas the margin alone
    assert!((past_the_frame((100.0, 100.0), 0.0, 1000.0, 1000.0) - 1300.0).abs() < 1e-9);
    assert!(
        (past_the_frame((100.0, 100.0), std::f64::consts::PI, 1000.0, 1000.0) - 500.0).abs() < 1e-6
    );
    assert!(
        (past_the_frame((100.0, 100.0), std::f64::consts::FRAC_PI_2, 1000.0, 1000.0) - 1300.0)
            .abs()
            < 1e-6
    );
    assert!(
        (past_the_frame((100.0, 100.0), -std::f64::consts::FRAC_PI_2, 1000.0, 1000.0) - 500.0)
            .abs()
            < 1e-6
    );
    assert!((past_the_frame((2000.0, 100.0), 0.0, 1000.0, 1000.0) - 400.0).abs() < 1e-9);
    // grown along its outward normals, either winding; a hairpin and a doubled corner fall back to the first edge's normal
    let g = grown(&square(0.0, 0.0, 10.0, 10.0), 8.0);
    assert!(g
        .iter()
        .all(|p| edge_dist(*p, &square(0.0, 0.0, 10.0, 10.0)) > 7.9));
    let mut rev = square(0.0, 0.0, 10.0, 10.0);
    rev.reverse();
    assert!(grown(&rev, 8.0).iter().all(|p| !in_poly(*p, &rev)));
    let hair = grown(&[(0.0, 0.0), (10.0, 0.0), (0.0, 0.0), (0.0, 0.0)], 1.0);
    assert_eq!(hair.len(), 4);
    // the gateway stepped toward the seat until it stands 12 ft clear; one that cannot clear stops where its tries ran out
    let crop = square(0.0, 0.0, 100.0, 100.0);
    let p = pull_clear((50.0, 95.0), (50.0, 300.0), &[crop.as_slice()], &mut t);
    assert!(p.1 >= 112.0 && p.1 < 125.0);
    let big = square(0.0, 0.0, 1000.0, 1000.0);
    let q = pull_clear((50.0, 50.0), (50.0, 900.0), &[big.as_slice()], &mut t);
    assert!((q.1 - (50.0 + 24.0 * 12.0)).abs() < 1e-6);
    assert_eq!(
        pull_clear((500.0, 500.0), (0.0, 0.0), &[crop.as_slice()], &mut t),
        (500.0, 500.0)
    );
}

#[test]
fn the_sweep_takes_the_clean_bearing_the_least_dry_one_or_the_dry_exit() {
    let mut t = Counts::default();
    let field = vec![square(0.0, 600.0, 1000.0, 1000.0)];
    let fabric = vec![square(480.0, 420.0, 520.0, 460.0)];
    let site = TrackSite {
        lean: ((0.0, -1.0), (0.0, -1.0)),
        seat: (500.0, 500.0),
        avoid: &field,
        wet: &[],
        fabric: &[],
        water: (None, &[], &[]),
        canvas: (1000.0, 1000.0),
    };
    // away from the field, straight north
    let (s, found) = connector(&site, (500.0, 500.0), &mut t);
    assert_eq!(s, (500.0, 500.0));
    assert!(
        matches!(found, Swept::Clean(ref p) if p[1].1 < -399.0 && (p[1].0 - 500.0).abs() < 1e-6)
    );
    // a steading on the ideal bearing swings the track off it
    let steaded = TrackSite {
        fabric: &fabric,
        ..site
    };
    let (_, found) = connector(&steaded, (500.0, 500.0), &mut t);
    assert!(matches!(found, Swept::Clean(ref p) if (p[1].0 - 500.0).abs() > 10.0));
    // a crop on every bearing, dry and clear of steadings: the least-bad bearing is kept
    let everywhere = [
        square(-5000.0, -5000.0, 5000.0, 5000.0),
        square(495.0, 0.0, 505.0, 450.0),
    ];
    let cropped = TrackSite {
        avoid: &everywhere[1..],
        ..site
    };
    let ring = square(0.0, 0.0, 1000.0, 1000.0);
    let rim = [
        ((0.0, 0.0), (1000.0, 0.0)),
        ((1000.0, 0.0), (1000.0, 1000.0)),
        ((1000.0, 1000.0), (0.0, 1000.0)),
        ((0.0, 1000.0), (0.0, 0.0)),
    ];
    let walled = TrackSite {
        water: (None, &rim, &[]),
        ..cropped
    };
    assert!(matches!(
        connector(&walled, (500.0, 500.0), &mut t).1,
        Swept::Least(_)
    ));
    // and a bearing behind the best on wet ground is pruned before its crop is scored
    let south = [square(0.0, 600.0, 1000.0, 1000.0)];
    let damp = TrackSite {
        wet: &south,
        ..walled
    };
    assert!(matches!(
        connector(&damp, (500.0, 500.0), &mut t).1,
        Swept::Least(_)
    ));
    // wet ground on every bearing: the dry exit
    let wet = vec![ring.clone(), vec![(0.0, 0.0)]];
    let soaked = TrackSite { wet: &wet, ..site };
    assert_eq!(connector(&soaked, (500.0, 500.0), &mut t).1, Swept::DryExit);
    assert!(t.total() > 0 && everywhere[0].len() == 4);
}
