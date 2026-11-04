//! The seated parts' unit tests (feature 444 T30).
//!
//! Research:
//!     the seated parts' tests - NONE: fixtures and assertions, deciding nothing about the place

use super::bundle::Bundle;
use super::fixtures::Kind;
use super::place::Seated;
use super::track_out::{
    box_poly, clip, near_the_cluster, seat_reach, seated_parts, Part, TRUNK_FT,
};

#[test]
fn the_homesteads_as_seated_and_the_tracks_stretch_about_them() {
    let b = Bundle {
        gardens: vec![(0.0, 0.0, 1.0, 1.0)],
        kura: Some((0.0, 0.0, 1.0, 1.0)),
        fixtures: vec![
            (Kind::Privy, (0.0, 0.0, 5.0, 5.0)),
            (Kind::Persimmon, (9.0, 9.0, 23.0, 23.0)),
        ],
        boxes: vec![
            (0.0, 0.0, 40.0, 20.0),
            (0.0, 30.0, 30.0, 20.0),
            (30.0, 0.0, 10.0, 10.0),
            (-30.0, 0.0, 8.0, 8.0),
            (0.0, -20.0, 5.0, 5.0),
            (9.0, 9.0, 23.0, 23.0),
        ],
        ..Bundle::default()
    };
    let s = Seated {
        lot: 0,
        seat: (0.0, 0.0),
        bundle: b,
        wood: vec![(100.0, 100.0)],
    };
    let parts = seated_parts(&[s], 20.0);
    let kinds: Vec<Part> = parts.iter().map(|p| p.1).collect();
    assert_eq!(
        kinds,
        vec![
            Part::House,
            Part::Yard,
            Part::Garden,
            Part::Shed,
            Part::Fixture,
            Part::Fixture,
            Part::WoodSeat
        ]
    );
    assert!((parts[5].0[1].0 - parts[5].0[0].0 - TRUNK_FT).abs() < 1e-9);
    assert_eq!(parts[6].0.len(), 8);
    assert!((parts[6].0[0].0 - 120.0).abs() < 1e-9);
    assert_eq!(box_poly((0.0, 0.0, 2.0, 4.0))[2], (1.0, 2.0));
    assert!(seat_reach(1.0) > 15.0);
    // the stretch: clipped to the extent and its margin; every leg where nothing is seated
    assert_eq!(
        clip((0.0, 0.0), (10.0, 0.0), (2.0, -1.0, 8.0, 1.0)),
        Some((0.2, 0.8))
    );
    assert!(clip((0.0, 5.0), (10.0, 5.0), (2.0, -1.0, 8.0, 1.0)).is_none());
    assert!(clip((-5.0, 0.0), (-5.0, 10.0), (2.0, -1.0, 8.0, 1.0)).is_none());
    assert!(clip((20.0, 0.0), (30.0, 0.0), (2.0, -1.0, 8.0, 1.0)).is_none());
    let track = [(0.0, 0.0), (0.0, -1000.0)];
    let near = near_the_cluster(&[(0.0, 20.0, 40.0, 40.0)], &track, 100.0);
    assert_eq!(near.len(), 1);
    assert!((near[0].1 .1 + 100.0).abs() < 1e-9);
    assert_eq!(near_the_cluster(&[], &track, 100.0).len(), 1);
    assert!(
        near_the_cluster(
            &[(0.0, 2000.0, 4.0, 4.0)],
            &[(0.0, -500.0), (0.0, -600.0), (5000.0, 5000.0)],
            10.0
        )
        .len()
            <= 2
    );
}
