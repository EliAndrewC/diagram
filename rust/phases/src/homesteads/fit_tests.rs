//! The fit rules' unit tests (feature 444 T30).
//!
//! Research:
//!     the fit rules' tests - NONE: fixtures and assertions, deciding nothing about the place
#![expect(clippy::float_cmp, reason = "an exact zero gap")]

use super::bundle::{bundle, Lot, Sun};
use super::fit::{
    across_a_stream, corners, crossing, on_free_ground, opens, quad_gap, seg_in_box, shades,
    sun_ok, too_near, Placed, Standing,
};
use super::fixtures::Forms;
use super::ground::Ground;
use super::layout::Side;

fn placed_at(x: f64, y: f64) -> Placed {
    let lot = Lot {
        house: (46.0, 28.0),
        kura: false,
        byre: None,
        fixtures: vec![],
    };
    let b = bundle(
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
        &mut 0,
    );
    Placed {
        house: (b.house, 0.0),
        house_box: b.boxes[0],
        yard: b.boxes[1],
        beds: b.boxes[2..2 + b.gardens.len()].to_vec(),
        bbox: b.bbox,
    }
}

#[test]
fn a_house_keeps_off_the_sun_of_every_yard_both_ways() {
    let mut t = 0;
    let lot = Lot {
        house: (46.0, 28.0),
        kura: false,
        byre: None,
        fixtures: vec![],
    };
    let sun = Sun {
        shade: 0.0,
        turns: &[0.0],
    };
    let mut standing = Standing::default();
    standing.add(placed_at(500.0, 500.0), &mut t);
    let yard_south = standing.all[0].yard.1 + standing.all[0].yard.3 / 2.0;
    // a house just south of the standing yard shades it
    let close = bundle(
        &lot,
        (500.0, yard_south + 20.0),
        Side::E,
        (500.0, yard_south + 20.0),
        0.0,
        &Forms::default(),
        &sun,
        &mut t,
    );
    assert!(!sun_ok(&close, &standing, &mut t));
    // beside the yard's corridor, its box met but no plot shaded
    let aside = bundle(
        &lot,
        (452.0, yard_south + 20.0),
        Side::E,
        (452.0, yard_south + 20.0),
        0.0,
        &Forms::default(),
        &sun,
        &mut t,
    );
    assert!(sun_ok(&aside, &standing, &mut t));
    // far enough south, it does not
    let far = bundle(
        &lot,
        (500.0, yard_south + 120.0),
        Side::E,
        (500.0, yard_south + 120.0),
        0.0,
        &Forms::default(),
        &sun,
        &mut t,
    );
    assert!(sun_ok(&far, &standing, &mut t));
    // a new yard just north of a standing house is shaded by it
    let north = bundle(
        &lot,
        (500.0, 430.0),
        Side::E,
        (500.0, 430.0),
        0.0,
        &Forms::default(),
        &sun,
        &mut t,
    );
    assert!(!sun_ok(&north, &standing, &mut t));
    // a bed shaded counts as a yard does
    let bed = standing.all[0].beds[0];
    let (bx, by) = (bed.0 + 30.0, bed.1 + bed.3 / 2.0 + 10.0 + 14.0);
    let by_bed = bundle(
        &lot,
        (bx, by),
        Side::E,
        (bx, by),
        0.0,
        &Forms::default(),
        &sun,
        &mut t,
    );
    assert!(
        !shades(by_bed.boxes[0], standing.all[0].yard, 41.0, 2.0)
            && !sun_ok(&by_bed, &standing, &mut t)
    );
    let p = &standing.all[0];
    assert!(
        shades(
            (500.0, 600.0, 46.0, 28.0),
            (500.0, 570.0, 10.0, 10.0),
            41.0,
            2.0
        ) && !p.beds.is_empty()
    );
    assert!(!shades(
        (800.0, 600.0, 46.0, 28.0),
        (500.0, 570.0, 10.0, 10.0),
        41.0,
        2.0
    ));
}

#[test]
fn two_roofs_shed_apart_and_a_farmstead_keeps_to_one_bank() {
    let mut t = 0;
    let mut standing = Standing::default();
    standing.add(placed_at(0.0, 0.0), &mut t);
    assert!(too_near((50.0, 0.0, 46.0, 28.0), 0.0, &standing, &mut t));
    assert!(!too_near((60.0, 0.0, 46.0, 28.0), 0.0, &standing, &mut t));
    // turned, the corners reach nearer
    assert!(too_near((57.0, 0.0, 46.0, 28.0), 30.0, &standing, &mut t));
    assert_eq!(
        quad_gap(
            &corners((0.0, 0.0, 10.0, 10.0), 0.0),
            &corners((3.0, 0.0, 10.0, 10.0), 0.0)
        ),
        0.0
    );
    assert!(
        (quad_gap(
            &corners((0.0, 0.0, 10.0, 10.0), 0.0),
            &corners((20.0, 0.0, 10.0, 10.0), 0.0)
        ) - 10.0)
            .abs()
            < 1e-9
    );
    // a stream between the house and its yard, or through a part
    let lot = Lot {
        house: (46.0, 28.0),
        kura: false,
        byre: None,
        fixtures: vec![],
    };
    let b = bundle(
        &lot,
        (0.0, 0.0),
        Side::E,
        (0.0, 0.0),
        0.0,
        &Forms::default(),
        &Sun {
            shade: 0.0,
            turns: &[0.0],
        },
        &mut t,
    );
    assert!(across_a_stream(
        &b,
        &[((-100.0, 18.0), (100.0, 18.0))],
        &mut t
    ));
    assert!(!across_a_stream(
        &b,
        &[((-100.0, -200.0), (100.0, -200.0))],
        &mut t
    ));
    assert!(crossing(
        ((0.0, 0.0), (10.0, 10.0)),
        ((0.0, 10.0), (10.0, 0.0))
    ));
    assert!(
        seg_in_box((0.0, 0.0), (1.0, 1.0), (0.0, 0.0, 4.0, 4.0))
            && !seg_in_box((10.0, 10.0), (11.0, 11.0), (0.0, 0.0, 4.0, 4.0))
    );
    assert!(seg_in_box((-10.0, 0.0), (10.0, 0.0), (0.0, 0.0, 4.0, 4.0)));
    // the parts on free ground, and the yard opening onto the reach
    let never = |_p: (f64, f64)| false;
    assert!(!never((0.0, 0.0)));
    let mut g = Ground::new((-200.0, -200.0), (200.0, 200.0), &mut t);
    assert!(on_free_ground(&b, &g, &never, &mut t));
    // a part past the window is asked of the window's owner
    let small = Ground::new((-10.0, -10.0), (10.0, 10.0), &mut t);
    assert!(!on_free_ground(&b, &small, &|_p| true, &mut t));
    let reach = g.reach(&[(-190.0, -190.0)], &mut t);
    assert!(opens(&b, &reach, &mut t));
    g.fill_ring(
        &[
            (-200.0, -200.0),
            (200.0, -200.0),
            (200.0, 200.0),
            (-200.0, 200.0),
        ],
        &mut t,
    );
    assert!(!on_free_ground(&b, &g, &never, &mut t));
    assert!(!opens(&b, &g.reach(&[(-190.0, -190.0)], &mut t), &mut t));
}
