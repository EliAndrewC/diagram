//! The meeting half's unit tests (feature 444 T30).
//!
//! Research:
//!     the meeting half's tests - NONE: fixtures and assertions, deciding nothing about the place

#![expect(clippy::many_single_char_names, reason = "the tests' own short names")]

use super::meet::{
    along_tail, connector_hairpin_ends, dangling_lane_ends, end_serves, folded_joint_pairs, foot,
    hairpin_over_a_short_leg, joints, needle_ends, oriented, tail_doubled, tread_bearings,
    Destinations, Lane,
};
use crate::field::fan::Pt;

fn lane(pts: &[Pt]) -> Lane {
    Lane {
        pts: pts.to_vec(),
        w: 3.0,
        ..Lane::default()
    }
}

#[test]
fn two_lanes_met_end_to_end_are_one_way_and_may_not_fold() {
    let a = lane(&[(0.0, 0.0), (100.0, 0.0)]);
    let b = lane(&[(100.0, 0.0), (0.0, 5.0)]);
    let lanes = [a.clone(), b.clone()];
    let j = joints(&lanes);
    assert_eq!(j, vec![(0, -1, 1, 0)]);
    let (x, y) = oriented(&lanes, j[0]);
    assert_eq!((x[1], y[0]), ((100.0, 0.0), (100.0, 0.0)));
    assert_eq!(oriented(&lanes, (1, 0, 0, -1)).0[0], (0.0, 5.0));
    let mut open = |_a: Pt, _b: Pt, _w: f64| false;
    assert_eq!(folded_joint_pairs(&lanes, &mut open).len(), 1);
    let mut walled = |_a: Pt, _b: Pt, _w: f64| true;
    assert!(folded_joint_pairs(&lanes, &mut walled).is_empty());
    // a third way touching, a loop, the track out: no joint
    let third = [a.clone(), b.clone(), lane(&[(100.0, -50.0), (100.0, 50.0)])];
    assert!(joints(&third).is_empty());
    let looped = [a.clone(), lane(&[(100.0, 0.0), (0.0, 0.0)])];
    assert!(joints(&looped).is_empty());
    let track = [
        Lane {
            connector: true,
            ..a.clone()
        },
        b,
    ];
    assert!(joints(&track).is_empty());
    assert!(joints(&[
        a.clone(),
        lane(&[(500.0, 0.0), (600.0, 0.0)]),
        lane(&[(0.0, 0.0)])
    ])
    .is_empty());
}

#[test]
fn a_lane_doubles_back_on_the_tracks_start_or_runs_back_along_a_tread() {
    assert!(hairpin_over_a_short_leg(
        (0.0, 0.0),
        (100.0, 0.0),
        (100.0, 10.0),
        (0.0, 10.0)
    ));
    assert!(!hairpin_over_a_short_leg(
        (0.0, 0.0),
        (100.0, 0.0),
        (100.0, 100.0),
        (0.0, 100.0)
    ));
    let track = Lane {
        connector: true,
        ..lane(&[(100.0, 10.0), (0.0, 12.0)])
    };
    let ln = lane(&[(0.0, 0.0), (100.0, 0.0), (100.0, 10.0)]);
    let rev = lane(&[(100.0, 10.0), (100.0, 0.0), (0.0, 0.0)]);
    let mut open = |_a: Pt, _b: Pt, _w: f64| false;
    assert_eq!(
        connector_hairpin_ends(&[track.clone(), ln], &mut open),
        vec![(0, 1, -1)]
    );
    assert_eq!(
        connector_hairpin_ends(&[track.clone(), rev], &mut open),
        vec![(0, 1, 0)]
    );
    let mut walled = |_a: Pt, _b: Pt, _w: f64| true;
    assert!(connector_hairpin_ends(
        &[track, lane(&[(0.0, 0.0), (100.0, 0.0), (100.0, 10.0)])],
        &mut walled
    )
    .is_empty());
    // a needle: an end leg running back along a tread under 20 degrees
    let tread = lane(&[(0.0, 0.0), (200.0, 0.0)]);
    let needle = lane(&[(0.0, 5.0), (100.0, 2.0)]);
    assert_eq!(
        needle_ends(&[needle.clone(), tread.clone()], &mut open).len(),
        1
    );
    assert!(needle_ends(&[needle.clone(), tread.clone()], &mut walled).is_empty());
    let tee = lane(&[(100.0, 100.0), (100.0, 2.0)]);
    assert!(needle_ends(&[tee, tread.clone()], &mut open).is_empty());
    let short = lane(&[(90.0, 5.0), (100.0, 2.0)]);
    assert!(needle_ends(&[short, tread.clone()], &mut open).is_empty());
    let far = lane(&[(0.0, 500.0), (100.0, 502.0)]);
    assert!(needle_ends(&[far, tread.clone(), lane(&[(0.0, 0.0)])], &mut open).is_empty());
    let near_box = lane(&[(0.0, 50.0), (100.0, 2.5)]);
    assert!(needle_ends(&[near_box, lane(&[(98.0, 7.0), (98.0, 300.0)])], &mut open).is_empty());
    assert_eq!(
        tread_bearings((50.0, 1.0), (0.0, 0.0), (100.0, 0.0)).len(),
        2
    );
    assert_eq!(tread_bearings((0.0, 0.0), (0.0, 0.0), (0.0, 0.0)).len(), 0);
    assert_eq!(foot((5.0, 5.0), ((0.0, 0.0), (0.0, 0.0))), (0.0, 0.0));
}

#[test]
fn an_end_may_not_run_on_beside_a_way_and_must_reach_something() {
    let way = [(0.0, 0.0), (300.0, 0.0)];
    assert!(along_tail(&[(0.0, 100.0), (0.0, 10.0), (100.0, 5.0)], &way, 15.0).is_some());
    assert!(along_tail(&[(0.0, 100.0), (100.0, 100.0)], &way, 15.0).is_none());
    assert!(along_tail(&[(0.0, 100.0), (100.0, 5.0)], &way[..1], 15.0).is_none());
    assert!(tail_doubled(
        &[(100.0, 5.0), (0.0, 10.0), (0.0, 100.0)],
        &way
    ));
    assert!(!tail_doubled(&[(0.0, 100.0), (100.0, 100.0)], &way));
    assert!(!tail_doubled(&[(0.0, 100.0), (100.0, 100.0)], &way[..1]));
    let d = Destinations {
        centers: vec![(500.0, 500.0)],
        edge: vec![((1000.0, 0.0), (1000.0, 1000.0))],
        steadings: vec![vec![
            (2000.0, 0.0),
            (2010.0, 0.0),
            (2010.0, 10.0),
            (2000.0, 10.0),
        ]],
    };
    assert!(end_serves((540.0, 500.0), &[], &d));
    assert!(end_serves((1004.0, 500.0), &[], &d));
    assert!(end_serves((2005.0, 5.0), &[], &d));
    assert!(end_serves((2005.0, 20.0), &[], &d));
    assert!(end_serves((0.0, 50.0), &[((0.0, 0.0), (10.0, 0.0))], &d));
    assert!(!end_serves((3000.0, 3000.0), &[], &d));
    // a lane between two farmhouses, and one that ends in open ground
    let lanes = [
        lane(&[(500.0, 520.0), (500.0, 900.0)]),
        lane(&[(400.0, 900.0), (600.0, 900.0)]),
        Lane {
            connector: true,
            ..lane(&[(0.0, 0.0), (1.0, 0.0)])
        },
    ];
    assert!(dangling_lane_ends(&lanes, &d, Some(0)).is_empty());
    assert_eq!(dangling_lane_ends(&lanes, &d, None), vec![(1, -1), (1, 0)]);
}
