//! The homesteads' unit tests (feature 444 T30).
//!
//! Research:
//!     the homesteads' tests - NONE: fixtures and assertions, deciding nothing about the place
#![expect(clippy::too_many_lines, reason = "one test a rule, its cases together")]

use super::bearing::{house_rot, soft_limit, turned_box, wrap_square, Margin, SPREAD_DEG};
use super::bundle::{bbox_of, bundle, envelope, Lot, Sun};
use super::fixtures::{Forms, Kind};
use super::ground::{Ground, CELL};
use super::layout::{
    beds, byre, hjit, kura, yard, yard_area_ft2, Byre, Side, SIDES, TSUBO_FT2, YARD_MIN_TSUBO,
};
use super::lots::{larger_first, quota_carriers, size_ladder, Lots};
use super::Counts;

#[test]
fn a_ring_takes_the_cells_whose_centers_lie_inside_it() {
    let mut t = Counts::default();
    let mut g = Ground::new((0.0, 0.0), (100.0, 100.0), &mut t);
    g.fill_ring(
        &[(20.0, 20.0), (60.0, 20.0), (60.0, 60.0), (20.0, 60.0)],
        &mut t,
    );
    assert_eq!(g.taken_at((40.0, 40.0)), Some(true));
    assert_eq!(g.taken_at((10.0, 40.0)), Some(false));
    assert_eq!(g.taken_at((70.0, 40.0)), Some(false));
    // a cell whose center is just outside stays clear: the ring's edge at 20 ft, the cell 16-24 centered at 20, inside
    assert_eq!(g.taken_at((21.0, 21.0)), Some(true));
    assert_eq!(g.taken_at((15.0, 15.0)), Some(false));
    // outside the window, the owner decides
    assert_eq!(g.taken_at((-5.0, 40.0)), None);
    assert_eq!(g.taken_at((40.0, 120.0)), None);
    // a ring of two points fills nothing; a ring past the window is clipped
    g.fill_ring(&[(0.0, 0.0), (90.0, 90.0)], &mut t);
    g.fill_ring(
        &[(80.0, -50.0), (200.0, -50.0), (200.0, 200.0), (80.0, 200.0)],
        &mut t,
    );
    assert_eq!(g.taken_at((90.0, 50.0)), Some(true));
    assert_eq!(g.taken_at((75.0, 50.0)), Some(false));
    assert!(t.total() > 0);
}

#[test]
fn a_strip_takes_the_cells_within_its_reach_and_a_rect_is_refused_at_nine_points() {
    let mut t = Counts::default();
    let mut g = Ground::new((0.0, 0.0), (200.0, 200.0), &mut t);
    g.paint_strip((0.0, 100.0), (200.0, 100.0), 6.0, &mut t);
    assert_eq!(g.taken_at((50.0, 100.0)), Some(true));
    assert_eq!(g.taken_at((50.0, 100.0 + CELL * 1.5)), Some(false));
    let never = |_p: (f64, f64)| false;
    let always = |_p: (f64, f64)| true;
    // a rectangle across the strip is refused at its center row; one clear of it is not
    assert!(g.rect_refused((40.0, 80.0), (80.0, 120.0), &never, &mut t));
    assert!(!g.rect_refused((40.0, 20.0), (80.0, 60.0), &never, &mut t));
    // a rectangle reaching past the window asks the owner for the points beyond it
    assert!(!g.rect_refused((180.0, 20.0), (260.0, 60.0), &never, &mut t));
    assert!(g.rect_refused((180.0, 20.0), (260.0, 60.0), &always, &mut t));
    // a window of no extent is one cell
    let mut u = Counts::default();
    let one = Ground::new((5.0, 5.0), (5.0, 5.0), &mut u);
    assert_eq!(one.taken_at((5.0, 5.0)), Some(false));
}

#[test]
fn the_reach_is_the_free_ground_joined_to_its_seeds() {
    let mut t = Counts::default();
    let mut g = Ground::new((0.0, 0.0), (160.0, 160.0), &mut t);
    // a wall across the window at x 72-88, the whole height: the east is cut off from a seed in the west
    g.fill_ring(
        &[(72.0, -10.0), (88.0, -10.0), (88.0, 170.0), (72.0, 170.0)],
        &mut t,
    );
    let r = g.reach(&[(20.0, 20.0), (80.0, 80.0), (-50.0, 0.0)], &mut t);
    assert!(r.touches((10.0, 10.0), (30.0, 30.0), &mut t));
    assert!(!r.touches((100.0, 10.0), (150.0, 30.0), &mut t));
    // a box on the wall itself touches the west's reach only past the wall's edge
    assert!(!r.touches((74.0, 40.0), (86.0, 50.0), &mut t));
    assert!(r.touches((60.0, 40.0), (86.0, 50.0), &mut t));
    // a box past the window touches nothing
    assert!(!r.touches((300.0, 300.0), (320.0, 320.0), &mut t));
    // seeded on both sides, both are reached
    let both = g.reach(&[(20.0, 20.0), (120.0, 120.0)], &mut t);
    assert!(both.touches((100.0, 10.0), (150.0, 30.0), &mut t));
}

#[test]
fn the_rolls_are_the_python_seatings_and_the_yard_is_log_normal_about_its_median() {
    // the hash as the Python seating computes it (`Settlement._hjit`): sin(12.9898 x + 4.1414 y + 7.373 salt) x 43758.5453, fractional
    let v = (100.0f64 * 12.9898 + 200.0 * 4.1414 + 3.0 * 7.373).sin() * 43_758.545_3;
    assert!((hjit(100.0, 200.0, 3.0) - (v - v.floor())).abs() < 1e-12);
    assert!((0.0..1.0).contains(&hjit(-5.0, 7.0, 9.0)));
    // the yard: never under the least, larger for a larger house at the same seat
    let small = yard_area_ft2((10.0, 10.0), 30.0, 20.0);
    let big = yard_area_ft2((10.0, 10.0), 60.0, 34.0);
    assert!(small >= YARD_MIN_TSUBO * TSUBO_FT2 - 1e-9 && big > small);
    let y = yard((10.0, 10.0), 46.0, 28.0);
    assert!(y.0 == 0.0 && y.1 > 14.0 && (y.2 / y.3 - 1.45).abs() < 1e-9);
}

#[test]
fn the_garden_lies_on_its_side_and_splits_in_one_household_in_four() {
    let mut forms = [0usize; 4];
    for k in 0..400 {
        let seat = (f64::from(k) * 37.0, f64::from(k) * 11.0);
        for side in SIDES {
            let b = beds(seat, 46.0, 28.0, side);
            for r in &b {
                match side {
                    Side::E | Side::SE => assert!(b.len() == 2 || r.0 > 0.0),
                    Side::W | Side::SW => assert!(b.len() == 2 || r.0 < 0.0),
                }
                assert!(r.2 >= 6.0 - 1e-9 && r.3 > 0.0);
            }
            if side == Side::SE {
                forms[b.len() - 1] += 1;
                if b.len() == 2 {
                    let flank = b[0].0 > 0.0 && b[1].0 < 0.0;
                    let stacked = (b[0].0 - b[1].0).abs() < 1e-9;
                    forms[2 + usize::from(stacked && !flank)] += 1;
                }
            }
        }
    }
    // about one in four split, and both split forms occur
    assert!(forms[1] > 60 && forms[1] < 150, "{forms:?}");
    assert!(forms[2] > 0 && forms[3] > 0, "{forms:?}");
    // a garden too narrow to split stays whole
    assert!(beds((0.0, 0.0), 8.0, 28.0, Side::E).len() <= 2);
    let tiny = (0..200)
        .map(|k| beds((f64::from(k), 3.0), 6.0, 6.0, Side::W).len())
        .max();
    assert_eq!(tiny, Some(1));
}

#[test]
fn the_storehouse_annex_keeps_its_band_and_the_byre_its_flank() {
    // the ordinary minka's north annex inside the band, unchanged at 21.2 x 12.6 ft
    let n = kura(46.0, 28.0, true);
    assert!((n.2 - 21.16).abs() < 1e-9 && (n.3 - 12.6).abs() < 1e-9 && (n.1 + 18.9).abs() < 1e-9);
    // a long house's annex held to the band's 1.8 to one; a shallow house's at the band's floor
    assert!(kura(70.0, 28.0, true).2 <= 1.8 * 12.6 + 1e-9);
    let floor = kura(46.0, 18.0, true);
    assert!((floor.2 - 18.0).abs() < 1e-9 && (floor.3 - 10.0).abs() < 1e-9);
    // the west annex along the wall, its length in the band
    let w = kura(46.0, 28.0, false);
    assert!(w.0 < 0.0 && (18.0..=27.0).contains(&w.3) && w.2 <= w.3 / 1.5 + 1e-9);
    // the byre on the flank away from the garden, long side along the wall
    let (dx, _dy, bw, bh, turn) = byre(46.0, 28.0, Side::E, Byre::YardShed);
    assert!(dx < -23.0 && bw < bh && (turn - 90.0).abs() < 1e-9);
    let (dx, dy, _, _, turn) = byre(46.0, 28.0, Side::W, Byre::Courtyard);
    assert!(dx > 23.0 && dy >= 0.0 && (turn + 90.0).abs() < 1e-9);
    assert!(
        byre(46.0, 28.0, Side::SE, Byre::Courtyard).4 > 0.0
            && byre(10.0, 4.0, Side::SW, Byre::Courtyard).1 == 0.0
    );
}

#[test]
fn a_house_turns_with_the_margin_it_stands_by_held_under_the_spread() {
    assert!((wrap_square(80.0) + 10.0).abs() < 1e-9 && (wrap_square(-50.0) - 40.0).abs() < 1e-9);
    assert!(
        soft_limit(60.0, SPREAD_DEG) < SPREAD_DEG && (soft_limit(0.1, 30.0) - 0.1).abs() < 1e-4
    );
    // the turn keyed on the seat's 4 ft cell, its spread inside the limit about the common bearing
    assert!(
        (house_rot((101.0, 99.0), 5.0, 0.0) - house_rot((100.0, 100.0), 5.0, 0.0)).abs() < 1e-12
    );
    for k in 0..50 {
        let r = house_rot((f64::from(k) * 37.0, 11.0), 5.0, 20.0);
        assert!((r - 5.0).abs() < SPREAD_DEG);
    }
    // a margin square to the axis gives no turn; one bent 20 degrees turns a house beside it, fading past the pull's reach
    let mut t = Counts::default();
    let square = Margin::new(
        &[(0.0, 0.0), (1000.0, 0.0), (1000.0, 1000.0), (0.0, 1000.0)],
        0.0,
        &mut t,
    );
    assert!(square.follow((500.0, 50.0), &mut t).abs() < 1e-9);
    let a = 20f64.to_radians();
    let bent = Margin::new(
        &[
            (0.0, 0.0),
            (1000.0 * a.cos(), 1000.0 * a.sin()),
            (500.0, 2000.0),
        ],
        0.0,
        &mut t,
    );
    let near = bent.follow((500.0 * a.cos(), 500.0 * a.sin() + 20.0), &mut t);
    assert!((near - 20.0).abs() < 1.0, "{near}");
    assert!(bent.follow((5000.0, 5000.0), &mut t).abs() < 1e-12);
    // halfway through the fade, half the turn
    let mid = bent.follow(
        (
            500.0 * a.cos() - 168.0 * a.sin(),
            500.0 * a.sin() + 168.0 * a.cos(),
        ),
        &mut t,
    );
    assert!(mid > 5.0 && mid < 15.0, "{mid}");
    // a ring of two points turns nothing
    assert!(
        Margin::new(&[(0.0, 0.0), (10.0, 0.0)], 0.0, &mut t)
            .follow((5.0, 1.0), &mut t)
            .abs()
            < 1e-12
    );
    // a box turned a quarter swaps its sides
    let b = turned_box((0.0, 0.0, 40.0, 20.0), 90.0);
    assert!((b.2 - 20.0).abs() < 1e-9 && (b.3 - 40.0).abs() < 1e-9);
}

#[test]
fn a_bundle_turns_as_one_piece_and_its_envelope_holds_every_side() {
    let lot = Lot {
        house: (46.0, 28.0),
        kura: true,
        byre: Some(Byre::YardShed),
        fixtures: vec![Kind::Privy, Kind::Coop, Kind::Persimmon],
    };
    let forms = Forms::default();
    let sun = Sun {
        shade: 50.0,
        turns: &[0.0],
    };
    let mut t = Counts::default();
    let flat = bundle(
        &lot,
        (300.0, 200.0),
        Side::SE,
        (300.0, 200.0),
        0.0,
        &forms,
        &sun,
        &mut t,
    );
    assert!(flat.unlaid.is_none() && flat.kura.is_some() && flat.byre.is_some());
    // the yard before the south wall, unturned
    assert!((flat.yard.0 - 300.0).abs() < 1e-9 && flat.yard.1 > 214.0);
    // turned a quarter, the yard is carried round to the west of the house
    let quarter = bundle(
        &lot,
        (300.0, 200.0),
        Side::SE,
        (300.0, 200.0),
        90.0,
        &forms,
        &sun,
        &mut t,
    );
    assert!((quarter.turn - 90.0).abs() < 1e-12 && quarter.bath.is_none());
    assert!(quarter.yard.0 < 300.0 - 14.0 && (quarter.yard.1 - 200.0).abs() < 1e-6);
    // every part inside its box, and the envelope round every side's
    let env = envelope(
        &lot,
        (300.0, 200.0),
        (300.0, 200.0),
        10.0,
        &forms,
        &sun,
        &mut t,
    );
    for side in SIDES {
        let b = bundle(
            &lot,
            (300.0, 200.0),
            side,
            (300.0, 200.0),
            10.0,
            &forms,
            &sun,
            &mut t,
        );
        for r in &b.boxes {
            assert!(
                r.0 - r.2 / 2.0 >= b.bbox.0 - b.bbox.2 / 2.0 - 1e-9
                    && r.0 + r.2 / 2.0 <= env.0 + env.2 / 2.0 + 1e-9
            );
        }
    }
    // a lot with no fixtures lays none; one whose fixtures find no seat is unlaid
    let bare = Lot {
        house: (46.0, 28.0),
        kura: false,
        byre: None,
        fixtures: vec![],
    };
    assert!(bundle(
        &bare,
        (0.0, 0.0),
        Side::E,
        (0.0, 0.0),
        0.0,
        &forms,
        &sun,
        &mut t
    )
    .fixtures
    .is_empty());
    let walled = Lot {
        house: (46.0, 28.0),
        kura: false,
        byre: Some(Byre::Courtyard),
        fixtures: vec![Kind::Bath, Kind::Retirement, Kind::Retirement],
    };
    let tight = Forms {
        retirement_gaps: vec![0.5],
        retirement_ft: (60.0, 40.0),
        ..Forms::default()
    };
    let _ = bundle(
        &walled,
        (0.0, 0.0),
        Side::W,
        (0.0, 0.0),
        0.0,
        &tight,
        &sun,
        &mut t,
    );
    let nowhere = Forms {
        retirement_gaps: vec![],
        ..Forms::default()
    };
    assert!(bundle(
        &walled,
        (0.0, 0.0),
        Side::W,
        (0.0, 0.0),
        0.0,
        &nowhere,
        &sun,
        &mut t
    )
    .unlaid
    .is_some());
    assert_eq!(
        bbox_of(&[(0.0, 0.0, 2.0, 2.0), (10.0, 0.0, 2.0, 2.0)]),
        (5.0, 0.0, 12.0, 2.0)
    );
}

#[test]
fn the_lots_are_dealt_as_the_python_seating_deals_them() {
    // seed 4, 20 households, read off the Python seating's deal (`settlement/rolling/lot.py`)
    let sizes = size_ladder(4, 20);
    let lengths: Vec<f64> = sizes
        .iter()
        .take(5)
        .map(|s| (s.0 * 1e4).round() / 1e4)
        .collect();
    assert_eq!(lengths, vec![1.2625, 0.9875, 1.0625, 1.3375, 1.0375]);
    let kura: Vec<usize> = larger_first(4, "kura", &sizes, 0.125)
        .iter()
        .enumerate()
        .filter(|(_, c)| **c)
        .map(|(k, _)| k)
        .collect();
    assert_eq!(kura, vec![3, 9, 16]);
    let byre: Vec<usize> = quota_carriers(4, "byre", 20, 0.3)
        .iter()
        .enumerate()
        .filter(|(_, c)| **c)
        .map(|(k, _)| k)
        .collect();
    assert_eq!(byre, vec![1, 4, 6, 9, 11, 18]);
    let lots = Lots::deal(4, 20, 0.3, &[(Kind::Woodpile, 0.4), (Kind::Privy, 1.0)]);
    let (house, keeps_kura, keeps_beast, kinds) = lots.lot(3).expect("a declared household");
    assert!(
        (house.0 - 46.0 * 1.3375).abs() < 1e-9
            && keeps_kura
            && !keeps_beast
            && kinds.contains(&Kind::Privy)
    );
    assert!(lots.lot(20).is_none());
    // every kind's quota keyed on its own name
    let all = Lots::deal(4, 20, 0.0, &super::fixtures::ORDER.map(|k| (k, 0.5)));
    assert_eq!(all.fixtures.len(), 9);
    assert!(all
        .fixtures
        .iter()
        .all(|(_, c)| c.iter().filter(|x| **x).count() == 10));
    assert_eq!(
        lots.fixtures
            .iter()
            .find(|(k, _)| *k == Kind::Woodpile)
            .map(|(_, c)| c.iter().filter(|x| **x).count()),
        Some(8)
    );
}

#[test]
fn the_counts_file_each_kind_and_total_all_but_the_moves() {
    let mut c = Counts::default();
    c.add("pt_test@a", 2);
    c.add("pt_test@a", 3);
    c.add("moved@b", 4);
    assert_eq!(c.0.len(), 2);
    assert_eq!(c.total(), 5);
}

#[test]
fn the_threads_tally_is_drained_into_the_stages_counts() {
    crate::counts::note("seg_test@noted", 3);
    let mut c = Counts::default();
    crate::counts::drain_into(&mut c);
    assert_eq!(c.0.get("seg_test@noted"), Some(&3));
    let mut again = Counts::default();
    crate::counts::drain_into(&mut again);
    assert!(again.0.is_empty());
}

#[test]
fn a_raster_is_built_from_the_cells_python_marks_taken() {
    let g = Ground::from_cells((0.0, 0.0), 5.0, 2, vec![false, true]).expect("two cells");
    assert_eq!(g.taken_at((2.0, 2.0)), Some(false));
    assert_eq!(g.taken_at((7.0, 2.0)), Some(true));
    assert_eq!(g.taken_at((12.0, 2.0)), None);
    assert!(Ground::from_cells((0.0, 0.0), 5.0, 2, vec![true]).is_none());
    assert!(Ground::from_cells((0.0, 0.0), 5.0, 0, vec![true]).is_none());
    assert!(Ground::from_cells((0.0, 0.0), 5.0, 2, vec![]).is_none());
}
