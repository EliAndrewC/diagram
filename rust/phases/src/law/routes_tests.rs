//! The ways out's unit tests (feature 444 T30).
//!
//! Research:
//!     the ways out's tests - NONE: fixtures and assertions, deciding nothing about the place

use super::meet::Lane;
use super::routes::{adds_a_way_out_crossing, departure_routes, way_outs_crossing};
use super::Counts;
use crate::field::fan::Pt;

fn lane(pts: &[Pt]) -> Lane {
    Lane {
        pts: pts.to_vec(),
        w: 3.0,
        ..Lane::default()
    }
}

#[test]
fn every_household_walks_out_to_the_tracks_outer_end() {
    let mut t = Counts::default();
    let track = Lane {
        connector: true,
        ..lane(&[(100.0, 100.0), (100.0, 1000.0)])
    };
    let way = lane(&[(0.0, 100.0), (100.0, 100.0)]);
    let houses = [(0.0, 110.0), (5000.0, 5000.0)];
    let routes = departure_routes(&[track.clone(), way.clone()], &houses, &mut t);
    assert_eq!(routes.len(), 1);
    assert!((routes[0][routes[0].len() - 1].1 - 1000.0).abs() < 1e-9);
    // no track, or no house: no route
    assert!(departure_routes(&[way.clone()], &houses, &mut t).is_empty());
    assert!(departure_routes(&[track.clone(), way.clone()], &[], &mut t).is_empty());
    // a way out over a brook and back
    let brook = vec![(-100.0, 50.0), (300.0, 50.0)];
    let over = lane(&[(0.0, 100.0), (0.0, 0.0), (100.0, 0.0), (100.0, 100.0)]);
    let r2 = departure_routes(&[track.clone(), over.clone()], &houses[..1], &mut t);
    assert_eq!(way_outs_crossing(&[brook.clone()], &r2, &mut t), 1);
    assert!(adds_a_way_out_crossing(
        &[track.clone()],
        &over.pts,
        3.0,
        &houses[..1],
        &[brook.clone()],
        &mut t
    ));
    assert!(!adds_a_way_out_crossing(
        &[track.clone()],
        &way.pts,
        3.0,
        &houses[..1],
        &[brook],
        &mut t
    ));
    assert!(!adds_a_way_out_crossing(
        &[track.clone()],
        &over.pts,
        3.0,
        &houses[..1],
        &[],
        &mut t
    ));
    // a way meeting the track's middle: the walk branches there
    let tee = lane(&[(0.0, 500.0), (100.0, 500.0)]);
    let r3 = departure_routes(
        &[track.clone(), tee, way.clone()],
        &[(0.0, 510.0), (0.0, 110.0)],
        &mut t,
    );
    assert_eq!(r3.len(), 2);
    assert!(departure_routes(
        &[
            Lane {
                connector: true,
                ..lane(&[(0.0, 0.0)])
            },
            lane(&[(0.0, 0.0)])
        ],
        &houses,
        &mut t
    )
    .is_empty());
}
