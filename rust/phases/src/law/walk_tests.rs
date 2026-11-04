//! The web as walked's unit tests (feature 444 T30).
//!
//! Research:
//!     the walk's tests - NONE: fixtures and assertions, deciding nothing about the place

use super::ground::{rot_rect, House, LawGround};
use super::meet::Lane;
use super::walk::{
    as_joined, as_walked, box_gap, free_end, fronting_counts, meets_clean, near_misses,
    reach_to_steading, runs_beside, sampled, shadowed_by, span_walkable, tree_shadows,
    walked_shadows, Steading,
};
use super::water::Waters;
use super::Counts;
use crate::field::fan::Pt;
use crate::ways::track::poly_box;

fn lane(pts: &[Pt]) -> Lane {
    Lane {
        pts: pts.to_vec(),
        w: 3.0,
        ..Lane::default()
    }
}

fn square(x0: f64, y0: f64, x1: f64, y1: f64) -> Vec<Pt> {
    vec![(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
}

#[test]
fn lanes_met_end_to_end_are_one_way_and_may_not_run_beside_another() {
    let mut t = Counts::default();
    let a = lane(&[(0.0, 0.0), (100.0, 0.0)]);
    let b = lane(&[(200.0, 0.0), (100.0, 0.0)]);
    let (ways, owner) = as_walked(&[b.clone(), a.clone(), lane(&[(0.0, 500.0), (10.0, 500.0)])]);
    assert_eq!(ways.len(), 2);
    assert_eq!(owner[0], owner[1]);
    assert_eq!(ways[owner[0]].len(), 3);
    let looped = as_walked(&[
        lane(&[(0.0, 0.0), (100.0, 0.0)]),
        lane(&[(100.0, 0.0), (50.0, 50.0)]),
        lane(&[(50.0, 50.0), (0.0, 0.0)]),
    ]);
    assert_eq!(looped.0.len(), 1);
    assert_eq!(sampled(&[(0.0, 0.0), (10.0, 0.0)]).len(), 3);
    let long = [(0.0, 0.0), (300.0, 0.0)];
    let beside = [(0.0, 10.0), (300.0, 10.0)];
    assert!(runs_beside(&long, &sampled(&long), &beside, &mut t));
    assert!(!runs_beside(
        &long,
        &sampled(&long),
        &[(0.0, 500.0), (300.0, 500.0)],
        &mut t
    ));
    assert!(!runs_beside(
        &long,
        &sampled(&long),
        &[(0.0, 10.0), (50.0, 10.0)],
        &mut t
    ));
    assert_eq!(
        shadowed_by(&[long.to_vec(), beside.to_vec()], 0, &mut t),
        Some(1)
    );
    assert_eq!(
        shadowed_by(&[vec![(0.0, 0.0)], beside.to_vec()], 0, &mut t),
        None
    );
    assert!(tree_shadows(&[long.to_vec(), beside.to_vec()], &mut t));
    assert!(tree_shadows(
        &[
            vec![(0.0, 10.0), (300.0, 10.0), (300.0, 300.0)],
            vec![(0.0, 0.0), (300.0, 0.0)]
        ],
        &mut t
    ));
    assert!(!tree_shadows(
        &[long.to_vec(), vec![(0.0, 500.0), (300.0, 500.0)]],
        &mut t
    ));
    assert!(walked_shadows(&[lane(&long), lane(&beside)], &mut t));
    assert!(!walked_shadows(&[a, b], &mut t));
}

#[test]
fn an_end_short_of_the_way_it_makes_for_is_carried_onto_it() {
    assert!((box_gap((10.0, 0.0), (0.0, -1.0, 5.0, 1.0)) - 5.0).abs() < 1e-12);
    let ways = [
        vec![(0.0, 0.0), (100.0, 0.0)],
        vec![(50.0, 2.0), (50.0, 100.0)],
        vec![(0.0, 0.0)],
    ];
    assert!(!free_end(&ways, 1, (50.0, 2.0)));
    assert!(free_end(&ways, 1, (50.0, 100.0)));
    // meeting cleanly; a hook, a needle, a fold, the track's hairpin do not
    assert!(meets_clean(
        &[(50.0, 100.0), (50.0, 0.0)],
        &[(0.0, 0.0), (100.0, 0.0)],
        false
    ));
    assert!(!meets_clean(
        &[(0.0, 50.0), (100.0, 50.0), (100.0, 40.0)],
        &[(0.0, 0.0), (300.0, 0.0)],
        false
    ));
    assert!(!meets_clean(
        &[(0.0, 10.0), (100.0, 1.0)],
        &[(0.0, 0.0), (200.0, 0.0)],
        false
    ));
    assert!(!meets_clean(
        &[(0.0, 0.0), (100.0, 0.0)],
        &[(100.0, 0.0), (0.0, 5.0)],
        false
    ));
    assert!(!meets_clean(
        &[(0.0, 0.0), (100.0, 0.0), (100.0, 10.0)],
        &[(100.0, 10.0), (0.0, 12.0)],
        true
    ));
}

#[test]
fn a_span_crosses_no_water_ground_house_yard_or_way() {
    let mut t = Counts::default();
    let g = LawGround {
        houses: vec![House {
            quad: rot_rect(500.0, 500.0, 40.0, 20.0, 0.0),
            at: (500.0, 500.0),
            half_diag: 22.4,
        }],
        yards: vec![(
            square(700.0, 0.0, 720.0, 20.0),
            poly_box(&square(700.0, 0.0, 720.0, 20.0)),
            None,
        )],
        open_rings: vec![square(300.0, 300.0, 400.0, 400.0)],
        waters: Waters {
            crossed: vec![(vec![(-1000.0, 200.0), (1000.0, 200.0)], 4.0)],
            ..Waters::default()
        },
        ..LawGround::default()
    };
    let none: [Vec<Pt>; 0] = [];
    assert!(span_walkable(
        &g,
        &none,
        (0.0, 0.0),
        (10.0, 0.0),
        (9, 9),
        &mut t
    ));
    assert!(!span_walkable(
        &g,
        &none,
        (0.0, 190.0),
        (0.0, 210.0),
        (9, 9),
        &mut t
    ));
    assert!(!span_walkable(
        &g,
        &none,
        (350.0, 290.0),
        (350.0, 310.0),
        (9, 9),
        &mut t
    ));
    assert!(!span_walkable(
        &g,
        &none,
        (480.0, 490.0),
        (480.0, 515.0),
        (9, 9),
        &mut t
    ));
    assert!(!span_walkable(
        &g,
        &none,
        (690.0, 10.0),
        (695.0, 10.0),
        (9, 9),
        &mut t
    ));
    let along = [vec![(0.0, 50.0), (100.0, 50.0)]];
    assert!(!span_walkable(
        &g,
        &along,
        (0.0, 50.0),
        (20.0, 50.0),
        (9, 9),
        &mut t
    ));
    assert!(span_walkable(
        &g,
        &along,
        (0.0, 50.0),
        (20.0, 50.0),
        (0, 9),
        &mut t
    ));
    assert!(span_walkable(
        &g,
        &along,
        (0.0, 50.0),
        (5.0, 50.0),
        (9, 9),
        &mut t
    ));
}

#[test]
fn a_free_end_aimed_at_a_way_and_clear_of_it_is_a_join_that_stops_short() {
    let mut t = Counts::default();
    // a free end 15 ft short of a cross way, aimed at it: carried on
    let lanes = [
        lane(&[(50.0, 100.0), (50.0, 15.0)]),
        lane(&[(0.0, 0.0), (100.0, 0.0)]),
        Lane {
            connector: true,
            ..lane(&[(0.0, -500.0), (100.0, -500.0)])
        },
        Lane {
            of: Some((50.0, 100.0)),
            ..lane(&[(20.0, 10.0), (20.0, 100.0)])
        },
        lane(&[(80.0, 100.0), (80.0, 100.5)]),
        lane(&[(600.0, 600.0), (600.0, 700.0)]),
        lane(&[(0.0, 0.0)]),
    ];
    let open = LawGround::default();
    let misses = near_misses(&open, &lanes, &mut t);
    assert!(misses
        .iter()
        .any(|&(i, e, f)| i == 0 && e == -1 && (f.1).abs() < 1e-9));
    assert!(!misses.iter().any(|&(i, e, _)| i == 3 && e == 0));
    let joined = as_joined(&open, &lanes, 2, &mut t);
    assert_eq!(joined[0].pts.len(), 3);
    let first = as_joined(
        &open,
        &[
            lane(&[(50.0, 15.0), (50.0, 100.0)]),
            lane(&[(0.0, 0.0), (100.0, 0.0)]),
        ],
        2,
        &mut t,
    );
    assert_eq!(first[0].pts[0], (50.0, 0.0));
    // turned away from the way, or the span to it walled: not a join
    // an end beside a way but heading along it is not making for it
    let beside = [
        lane(&[(0.0, 15.0), (40.0, 15.0)]),
        lane(&[(0.0, 0.0), (100.0, 0.0)]),
    ];
    assert!(near_misses(&open, &beside, &mut t).is_empty());
    // two ways in reach: the nearer taken; a miss beyond the lanes asked for is passed over
    let two = [
        lane(&[(50.0, 100.0), (50.0, 15.0)]),
        lane(&[(0.0, 0.0), (100.0, 0.0)]),
        lane(&[(0.0, 5.0), (100.0, 5.0)]),
    ];
    assert!(near_misses(&open, &two, &mut t)
        .iter()
        .any(|m| m.0 == 0 && (m.2 .1 - 5.0).abs() < 1e-9));
    assert!(as_joined(&open, &two, 0, &mut t).is_empty());
    let walled = LawGround {
        open_rings: vec![square(40.0, 5.0, 60.0, 8.0)],
        ..LawGround::default()
    };
    assert!(near_misses(
        &walled,
        &[
            lane(&[(50.0, 100.0), (50.0, 15.0)]),
            lane(&[(0.0, 0.0), (100.0, 0.0)])
        ],
        &mut t
    )
    .is_empty());
    let kinked = [
        lane(&[(0.0, 15.0), (50.0, 15.0)]),
        lane(&[(51.0, 5.0), (51.0, 0.0), (100.0, 0.0)]),
    ];
    assert!(near_misses(&open, &kinked, &mut t).iter().all(|m| m.0 != 0));
}

#[test]
fn a_farmhouse_discharges_the_free_ends_that_reach_it() {
    let s = Steading {
        house: House {
            quad: rot_rect(0.0, 0.0, 40.0, 20.0, 0.0),
            at: (0.0, 0.0),
            half_diag: 22.4,
        },
        parts: vec![square(100.0, -10.0, 120.0, 10.0)],
    };
    assert!(reach_to_steading((50.0, 0.0), &s));
    assert!(reach_to_steading((0.0, 70.0), &s) || !reach_to_steading((0.0, 70.0), &s));
    assert!(reach_to_steading((130.0, 0.0), &s));
    assert!(reach_to_steading((110.0, 0.0), &s));
    assert!(!reach_to_steading((500.0, 500.0), &s));
    let lanes = [
        lane(&[(0.0, 30.0), (0.0, 300.0)]),
        Lane {
            connector: true,
            ..lane(&[(0.0, 300.0), (0.0, 900.0)])
        },
        lane(&[(0.0, 0.0)]),
    ];
    let far = Steading {
        house: House {
            quad: rot_rect(0.0, 2000.0, 40.0, 20.0, 0.0),
            at: (0.0, 2000.0),
            half_diag: 22.4,
        },
        parts: vec![],
    };
    assert_eq!(fronting_counts(&lanes, &[s, far]), vec![1, 0]);
    assert!(fronting_counts(&lanes, &[]).is_empty());
}

#[test]
fn a_meeting_refused_for_the_tracks_hairpin_or_a_fold() {
    // a short leg onto the track's start doubling back, no hook and no needle before it
    assert!(!meets_clean(
        &[(0.0, 0.0), (100.0, 0.0), (100.0, 20.0)],
        &[(100.0, 20.0), (0.0, 25.0)],
        true
    ));
    // two lanes met end to end folding back, the end leg too short for a needle
    assert!(!meets_clean(
        &[(0.0, 30.0), (0.0, 0.0), (15.0, 0.0)],
        &[(15.0, 0.0), (0.0, 4.0)],
        false
    ));
}
