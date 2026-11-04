//! The homesteads' unit tests (feature 444 T30).
//!
//! Research:
//!     the homesteads' tests - NONE: fixtures and assertions, deciding nothing about the place

use super::ground::{Ground, CELL};
use super::layout::{beds, hjit, yard, yard_area_ft2, Side, SIDES, TSUBO_FT2, YARD_MIN_TSUBO};

#[test]
fn a_ring_takes_the_cells_whose_centers_lie_inside_it() {
    let mut t = 0;
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
    assert!(t > 0);
}

#[test]
fn a_strip_takes_the_cells_within_its_reach_and_a_rect_is_refused_at_nine_points() {
    let mut t = 0;
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
    let mut u = 0;
    let one = Ground::new((5.0, 5.0), (5.0, 5.0), &mut u);
    assert_eq!(one.taken_at((5.0, 5.0)), Some(false));
}

#[test]
fn the_reach_is_the_free_ground_joined_to_its_seeds() {
    let mut t = 0;
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
