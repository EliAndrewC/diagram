//! A household reached across a neighbor's yard: the passage's unit tests (feature 444 T30).
//!
//! Research:
//!     the passage's tests - NONE: fixtures and assertions, deciding nothing about the place
#![expect(clippy::many_single_char_names, reason = "the tests' own short names")]

use super::access::parts_of;
use super::bundle::{bundle, Bundle, Lot, Sun};
use super::fixtures::{Forms, Kind};
use super::ground::Ground;
use super::layout::Side;
use super::passage::{
    apart, box_foot, grown, land_box, on_their_land, own_parts, passage_of, walk_of, yard_side,
    Tight, Walls,
};
use super::place::box_reach;
use super::wood::Shares;
use super::Counts;
use crate::field::fan::Pt;

fn laid_with(at: Pt, fixtures: Vec<Kind>) -> Bundle {
    let lot = Lot {
        house: (46.0, 28.0),
        kura: false,
        byre: None,
        fixtures,
    };
    bundle(
        &lot,
        at,
        Side::E,
        at,
        0.0,
        &Forms::default(),
        &Sun {
            shade: 0.0,
            turns: &[0.0],
        },
        &mut Counts::default(),
    )
}

/// A household with no fixtures (a walk keeps off each by its leg tests; the test asks the walk round the houses, and moves none).
fn laid(at: Pt) -> Bundle {
    laid_with(at, vec![])
}

/// A household laid south of `a` and 40 ft east, on its yard's side, moved whole so its box stands a foot off `a`'s.
fn south_of(a: &Bundle) -> Bundle {
    let mut b = laid((a.house.0 + 40.0, a.house.1 + 200.0));
    let dy = (a.bbox.1 + a.bbox.3 / 2.0 + 1.0 + b.bbox.3 / 2.0) - b.bbox.1;
    let down = |r: &mut super::layout::Rect| r.1 += dy;
    down(&mut b.house);
    down(&mut b.yard);
    down(&mut b.bbox);
    b.gardens.iter_mut().for_each(down);
    b.boxes.iter_mut().for_each(down);
    b
}

#[test]
fn the_passages_geometry() {
    let r = land_box((10.0, 10.0), (4.0, 6.0, 2.0, 8.0));
    assert_eq!(r, (11.0, 13.0, 10.0, 10.0));
    assert_eq!(grown(r, 1.0), (11.0, 13.0, 12.0, 12.0));
    assert!((apart((0.0, 0.0, 2.0, 2.0), (5.0, 0.0, 2.0, 2.0)) - 3.0).abs() < 1e-12);
    assert!(apart((0.0, 0.0, 4.0, 4.0), (1.0, 1.0, 2.0, 2.0)) < 0.0);
    assert!(yard_side(
        (0.0, 0.0),
        (0.0, 10.0),
        std::f64::consts::FRAC_PI_2
    ));
    assert!(!yard_side(
        (0.0, 0.0),
        (0.0, 10.0),
        -std::f64::consts::FRAC_PI_2
    ));
    assert_eq!(box_foot((20.0, 0.0), (0.0, 0.0, 4.0, 4.0)), (2.0, 0.0));
    let lands = [(0.0, 0.0, 10.0, 10.0)];
    assert!(on_their_land((0.0, 0.0), (4.0, 4.0), &lands));
    assert!(!on_their_land((0.0, 0.0), (20.0, 0.0), &lands));
    // a walk keeps off the house, beds and fixtures - never the persimmon's crown
    let b = laid_with((500.0, 500.0), vec![Kind::Privy, Kind::Persimmon]);
    let parts = own_parts(&parts_of(&b));
    assert_eq!(parts.len(), 1 + b.gardens.len() + 1);
}

#[test]
fn a_household_against_its_neighbors_land_is_reached_across_its_yard() {
    let mut t = Counts::default();
    let a = laid((500.0, 500.0));
    let b = south_of(&a);
    // the ground's window short of the lands' southern edge (the ground past it asked as clear), another homestead far off
    let ground = Ground::new((0.0, 0.0), (1000.0, 560.0), &mut t);
    let wood = Shares::default();
    let beyond = |_p: Pt| false;
    assert!(!beyond((0.0, 0.0)));
    let walls = Walls {
        boxes: vec![(900.0, 100.0, 10.0, 10.0)],
        ground: &ground,
        beyond: &beyond,
        wood: &wood,
        lane_gap: 10.0,
    };
    let tight = Tight {
        nb: 0,
        land: a.bbox,
        // its allotted reach, as the growth parts its seat by: wider than its own box, west and north toward the neighbor
        own: {
            let (w, e, n, so) = box_reach((b.boxes[0].0, b.boxes[0].1), b.bbox);
            (w + 40.0, e, n + 20.0, so)
        },
    };
    let got = passage_of(&b, &a, Some(0), &tight, &walls, &mut t)
        .expect("a walk across the neighbor's yard");
    assert_eq!((got.of, got.depth), (0, 1));
    assert!(got.walk.len() >= 2);
    // past the chain, or with no way of its own to reach the neighbor by, none
    assert!(passage_of(&b, &a, Some(2), &tight, &walls, &mut t).is_none());
    assert!(passage_of(&b, &a, None, &tight, &walls, &mut t).is_none());
    // land that does not adjoin the neighbor's
    let far = Tight {
        land: (a.bbox.0, a.bbox.1 + 400.0, a.bbox.2, a.bbox.3),
        ..tight
    };
    assert!(passage_of(&b, &a, Some(0), &far, &walls, &mut t).is_none());
    // the ground between them all taken: no walk
    let mut full = Ground::new((0.0, 0.0), (1000.0, 1000.0), &mut t);
    full.fill_ring(
        &[
            (-10.0, -10.0),
            (1010.0, -10.0),
            (1010.0, 1010.0),
            (-10.0, 1010.0),
        ],
        &mut t,
    );
    let shut = Walls {
        ground: &full,
        ..walls
    };
    let (me, them) = (parts_of(&b), parts_of(&a));
    let lands = [
        grown(land_box((b.boxes[0].0, b.boxes[0].1), tight.own), 3.0),
        grown(a.bbox, 3.0),
    ];
    assert!(walk_of(
        me.doors(7.0)[0],
        them.yard,
        &lands,
        &me,
        &them,
        &shut,
        &mut t
    )
    .is_none());
}
