//! The fit rules past the raster: their unit tests (feature 444 T30).
//!
//! Research:
//!     the fit rules' tests - NONE: fixtures and assertions, deciding nothing about the place
#![expect(
    clippy::many_single_char_names,
    reason = "a bundle, its yard and the tally, named as the rules name them"
)]

use super::bundle::{bundle, Bundle, Lot, Sun};
use super::fit::{Placed, Standing};
use super::fit_rules::{
    admitted, beds_on_water, chain_violated, crown_shades, on_water, persimmon_conflict,
    persimmon_of, unreachable, wall_on_the_bund, Rules,
};
use super::fixtures::{Forms, Kind};
use super::layout::{Byre, Side};
use super::Counts;
use crate::field::fan::Pt;

fn laid(x: f64, y: f64) -> Bundle {
    let lot = Lot {
        house: (46.0, 28.0),
        kura: true,
        byre: Some(Byre::YardShed),
        fixtures: vec![Kind::Privy, Kind::Retirement, Kind::Persimmon],
    };
    bundle(
        &lot,
        (x, y),
        Side::E,
        (x, y),
        0.0,
        &Forms::default(),
        &Sun {
            shade: 0.0,
            turns: &[0.0],
        },
        &mut Counts::default(),
    )
}

fn square(c: Pt, r: f64) -> Vec<Pt> {
    vec![
        (c.0 - r, c.1 - r),
        (c.0 + r, c.1 - r),
        (c.0 + r, c.1 + r),
        (c.0 - r, c.1 + r),
    ]
}

/// The persimmon of `b` moved to `at`, its box with it.
fn tree_at(b: &mut Bundle, at: Pt) {
    let k = b
        .fixtures
        .iter()
        .position(|(k, _)| *k == Kind::Persimmon)
        .unwrap();
    let first = 2 + b.gardens.len() + usize::from(b.kura.is_some()) + usize::from(b.byre.is_some());
    let r = b.fixtures[k].1;
    b.fixtures[k].1 = (at.0, at.1, r.2, r.3);
    b.boxes[first + k] = (at.0, at.1, r.2, r.3);
}

#[test]
fn the_wall_keeps_off_the_paddys_chords_by_side_and_gap() {
    let mut t = Counts::default();
    let chain = vec![
        ((0.0, 600.0), (1000.0, 600.0), (0.0, -1.0)),
        ((5.0, 5.0), (5.0, 5.0), (0.0, -1.0)),
    ];
    let chains = vec![chain];
    assert!(!chain_violated((500.0, 500.0), &chains, 7.0, &mut t));
    assert!(chain_violated((500.0, 595.0), &chains, 7.0, &mut t));
    assert!(chain_violated((500.0, 700.0), &chains, 7.0, &mut t));
    assert!(chain_violated((1003.0, 600.0), &chains, 7.0, &mut t));
    assert!(chain_violated((-3.0, 600.0), &chains, 7.0, &mut t));
    assert!(!chain_violated((1100.0, 600.0), &chains, 7.0, &mut t));
    let b = laid(500.0, 500.0);
    let near = Rules {
        chains: vec![vec![(
            (0.0, b.house.1 + 18.0),
            (1000.0, b.house.1 + 18.0),
            (0.0, -1.0),
        )]],
        ..Rules::default()
    };
    assert!(wall_on_the_bund(&b, &near, &mut t));
    assert!(!wall_on_the_bund(
        &b,
        &Rules {
            chains,
            ..Rules::default()
        },
        &mut t
    ));
}

#[test]
fn a_bed_keeps_off_running_water() {
    let mut t = Counts::default();
    let r = (500.0, 500.0, 100.0, 10.0);
    let w = |line: Vec<Pt>, hw: f64| Rules::boxed(vec![(line, hw)]);
    // a line through the box's edges, far from its corners and center
    assert!(on_water(
        r,
        &w(vec![(530.0, 400.0), (530.0, 600.0)], 1.0),
        &mut t
    ));
    // near a corner
    assert!(on_water(
        r,
        &w(vec![(552.0, 400.0), (552.0, 600.0)], 3.0),
        &mut t
    ));
    // a course whose box is out of reach, and one whose box reaches while its segment does not
    assert!(!on_water(
        r,
        &w(vec![(900.0, 900.0), (950.0, 950.0)], 2.0),
        &mut t
    ));
    assert!(!on_water(
        r,
        &w(vec![(400.0, 400.0), (400.0, 600.0), (600.0, 600.0)], 2.0),
        &mut t
    ));
    assert!(!on_water(
        r,
        &w(vec![(400.0, 400.0), (400.0, 520.0)], 2.0),
        &mut t
    ));
    let b = laid(500.0, 500.0);
    let g = b.boxes[2];
    let on = Rules {
        waters: w(vec![(g.0, g.1 - 100.0), (g.0, g.1 + 100.0)], 2.0),
        ..Rules::default()
    };
    assert!(!b.gardens.is_empty() && beds_on_water(&b, &on, &mut t));
    assert!(!beds_on_water(&b, &Rules::default(), &mut t));
}

#[test]
fn a_house_deeper_than_a_ways_reach_in_the_hard_ground_is_refused() {
    let mut t = Counts::default();
    let rules = Rules {
        hard: Rules::boxed(vec![
            (square((1000.0, 1000.0), 1000.0), 8.0),
            (
                vec![(3000.0, 3000.0), (3400.0, 3000.0), (3000.0, 3400.0)],
                0.0,
            ),
        ]),
        ..Rules::default()
    };
    assert!(unreachable((1000.0, 1000.0), &rules, &mut t));
    assert!(!unreachable((50.0, 1000.0), &rules, &mut t));
    assert!(!unreachable((5000.0, 5000.0), &rules, &mut t));
    assert!(!unreachable((3350.0, 3350.0), &rules, &mut t));
}

#[test]
fn every_part_is_asked_of_what_the_registry_forbids_it() {
    let mut t = Counts::default();
    let b = laid(500.0, 500.0);
    let h = (b.house.0, b.house.1);
    let forbid = |key: &str, ring: Vec<Pt>| Rules {
        forbidding: vec![(key.to_owned(), vec![ring])],
        ..Rules::default()
    };
    assert!(admitted(&b, &Rules::default(), &mut t));
    // a ring across the house, one wholly inside it, and one it stands wholly inside
    assert!(!admitted(
        &b,
        &forbid("houses", square((h.0 + 23.0, h.1), 5.0)),
        &mut t
    ));
    assert!(!admitted(&b, &forbid("houses", square(h, 2.0)), &mut t));
    assert!(!admitted(&b, &forbid("houses", square(h, 500.0)), &mut t));
    // a key the part is not filed under, and a ring far off
    assert!(admitted(&b, &forbid("wells", square(h, 2.0)), &mut t));
    assert!(admitted(
        &b,
        &forbid("houses", square((900.0, 900.0), 5.0)),
        &mut t
    ));
    // a held fixture, and the retirement house, each under its own key; the persimmon is held by none
    let first = 2 + b.gardens.len() + 2;
    let at = |k: Kind| {
        let i = b.fixtures.iter().position(|(f, _)| *f == k).unwrap();
        let r = b.boxes[first + i];
        (r.0, r.1)
    };
    assert!(!admitted(
        &b,
        &forbid("farm_fixtures", square(at(Kind::Privy), 1.0)),
        &mut t
    ));
    assert!(!admitted(
        &b,
        &forbid("retirement_houses", square(at(Kind::Retirement), 1.0)),
        &mut t
    ));
    assert!(admitted(
        &b,
        &forbid("farm_fixtures", square(at(Kind::Persimmon), 1.0)),
        &mut t
    ));
    assert!(!admitted(
        &b,
        &forbid(
            "farm_sheds",
            square(
                (
                    b.boxes[2 + b.gardens.len()].0,
                    b.boxes[2 + b.gardens.len()].1
                ),
                1.0
            )
        ),
        &mut t
    ));
}

#[test]
fn the_persimmon_is_dropped_from_the_sun_and_a_neighbors_refuses_the_seat() {
    let mut t = Counts::default();
    let sun = Rules {
        sun: true,
        ..Rules::default()
    };
    assert!(crown_shades(
        (0.0, 30.0),
        12.5,
        (0.0, 0.0, 20.0, 20.0),
        50.0
    ));
    assert!(!crown_shades(
        (0.0, -30.0),
        12.5,
        (0.0, 0.0, 20.0, 20.0),
        50.0
    ));
    let empty = Standing::default();
    // no sun corridor kept: nothing asked
    let mut b = laid(500.0, 500.0);
    assert!(!persimmon_conflict(
        &mut b,
        &empty,
        &Rules::default(),
        &mut t
    ));
    // its own yard's sun: the tree dropped, the seat kept
    let y = b.boxes[1];
    tree_at(&mut b, (y.0, y.1 + y.3 / 2.0 + 10.0));
    let n = b.boxes.len();
    assert!(!persimmon_conflict(&mut b, &empty, &sun, &mut t));
    assert!(persimmon_of(&b).is_none() && b.boxes.len() == n - 1);
    // a seat with no tree asks only the neighbors'
    assert!(!persimmon_conflict(&mut b, &empty, &sun, &mut t));
    // a neighbor's yard in this tree's shade: dropped; a neighbor's tree in this yard's sun: refused
    let mut c = laid(500.0, 500.0);
    tree_at(&mut c, (y.0 + 300.0, y.1 - 300.0));
    let mut standing = Standing::default();
    let yard = (y.0 + 300.0, y.1 - 330.0, 20.0, 20.0);
    standing.add(
        Placed {
            house: ((yard.0, yard.1 - 40.0, 40.0, 20.0), 0.0),
            house_box: (yard.0, yard.1 - 40.0, 40.0, 20.0),
            yard,
            beds: vec![],
            bbox: (yard.0, yard.1 - 20.0, 60.0, 60.0),
            persimmon: None,
        },
        &mut t,
    );
    assert!(!persimmon_conflict(&mut c, &standing, &sun, &mut t));
    assert!(persimmon_of(&c).is_none());
    let mut d = laid(500.0, 500.0);
    tree_at(&mut d, (y.0 + 300.0, y.1 - 300.0));
    let mut theirs = Standing::default();
    theirs.add(
        Placed {
            house: ((y.0, y.1 + 200.0, 40.0, 20.0), 0.0),
            house_box: (y.0, y.1 + 200.0, 40.0, 20.0),
            yard: (y.0, y.1 + 230.0, 20.0, 20.0),
            beds: vec![],
            bbox: (y.0, y.1 + 30.0, 60.0, 60.0),
            persimmon: Some((y.0, y.1 + y.3 / 2.0 + 10.0)),
        },
        &mut t,
    );
    assert!(persimmon_conflict(&mut d, &theirs, &sun, &mut t));
    assert!(persimmon_of(&d).is_some());
}
