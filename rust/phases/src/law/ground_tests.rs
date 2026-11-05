//! The ground half's unit tests (feature 444 T30).
//!
//! Research:
//!     the ground half's tests - NONE: fixtures and assertions, deciding nothing about the place

use super::ground::{
    hooked, house_hit, over_a_fixture, rot_rect, through_a_building, House, LawGround,
};
use super::water::Waters;
use super::Counts;
use crate::field::fan::Pt;
use crate::ways::track::{poly_box, segments_cross};

fn square(x0: f64, y0: f64, x1: f64, y1: f64) -> Vec<(f64, f64)> {
    vec![(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
}

fn house(x: f64, y: f64) -> House {
    House {
        quad: rot_rect(x, y, 40.0, 20.0, 0.0),
        at: (x, y),
        half_diag: 40f64.hypot(20.0) / 2.0,
    }
}

#[test]
fn the_fabric_the_open_ground_and_the_buildings_a_run_keeps_off() {
    let mut t = Counts::default();
    let houses = [house(100.0, 100.0)];
    assert!(house_hit(
        &[(0.0, 100.0), (200.0, 100.0)],
        3.0,
        &houses,
        &mut t
    ));
    assert!(house_hit(
        &[(0.0, 113.0), (200.0, 113.0)],
        3.0,
        &houses,
        &mut t
    ));
    assert!(!house_hit(
        &[(0.0, 120.0), (200.0, 120.0)],
        3.0,
        &houses,
        &mut t
    ));
    assert!(!house_hit(
        &[(0.0, 500.0), (200.0, 500.0)],
        3.0,
        &houses,
        &mut t
    ));
    assert!(house_hit(
        &[(100.0, 100.0), (100.0, 101.0)],
        3.0,
        &houses,
        &mut t
    ));
    let fx = square(50.0, 50.0, 55.0, 55.0);
    let fixtures = [(fx.clone(), poly_box(&fx))];
    assert_eq!(
        over_a_fixture(
            &[(0.0, 0.0), (10.0, 0.0), (52.0, 52.0)],
            3.0,
            &fixtures,
            &mut t
        ),
        Some(1)
    );
    assert_eq!(
        over_a_fixture(&[(0.0, 0.0), (10.0, 0.0)], 3.0, &fixtures, &mut t),
        None
    );
    assert_eq!(
        over_a_fixture(&[(52.0, 52.0), (53.0, 53.0)], 3.0, &fixtures, &mut t),
        Some(0)
    );
    assert_eq!(
        over_a_fixture(
            &[(0.0, 53.0), (40.0, 53.0), (40.0, 54.0), (53.0, 53.0)],
            3.0,
            &fixtures,
            &mut t
        ),
        Some(2)
    );
    let q = [rot_rect(0.0, 0.0, 10.0, 10.0, 45.0)];
    assert!(through_a_building(&[(-20.0, 0.0), (20.0, 0.0)], &q));
    assert!(through_a_building(&[(0.0, 0.0), (0.5, 0.0)], &q));
    assert!(!through_a_building(&[(-20.0, 20.0), (20.0, 20.0)], &q));
    assert_eq!(hooked(&[(0.0, 0.0), (10.0, 0.0)]), Vec::<i8>::new());
    assert_eq!(hooked(&[(0.0, 0.0), (100.0, 0.0), (100.0, 10.0)]), vec![-1]);
    assert_eq!(hooked(&[(0.0, 10.0), (0.0, 0.0), (100.0, 0.0)]), vec![0]);
}

#[test]
fn the_ground_half_names_the_first_rule_a_run_breaks() {
    let mut t = Counts::default();
    let yard = square(200.0, 200.0, 240.0, 230.0);
    let field = square(0.0, 600.0, 1000.0, 1000.0);
    let shed = rot_rect(500.0, 300.0, 10.0, 10.0, 0.0);
    let well = square(700.0, 100.0, 710.0, 110.0);
    let g = LawGround {
        houses: vec![house(100.0, 100.0)],
        yards: vec![
            (yard.clone(), poly_box(&yard), Some((220.0, 180.0))),
            (
                square(5000.0, 0.0, 5001.0, 1.0),
                (5000.0, 0.0, 5001.0, 1.0),
                None,
            ),
        ],
        solid: vec![(480.0, 280.0, 520.0, 320.0)],
        fixtures: vec![],
        buildings: vec![shed.clone()],
        open_rings: vec![field.clone()],
        forbidding: vec![(well.clone(), poly_box(&well))],
        waters: Waters {
            brooks: vec![vec![(0.0, 450.0), (1000.0, 450.0)]],
            fords: vec![(300.0, 450.0)],
            ..Waters::default()
        },
        ..LawGround::default()
    };
    assert_eq!(
        g.ground_fault(&[(0.0, 0.0)], 3.0, None, &mut t),
        Some("too short")
    );
    assert!(g.on_lawful_ground(&[(300.0, 0.0), (300.0, 150.0)], 3.0, None, &mut t));
    assert_eq!(
        g.ground_fault(&[(0.0, 100.0), (200.0, 100.0)], 3.0, None, &mut t),
        Some("fabric")
    );
    assert_eq!(
        g.ground_fault(&[(195.0, 150.0), (195.0, 260.0)], 3.0, None, &mut t),
        Some("fabric")
    );
    assert!(g.on_lawful_ground(
        &[(195.0, 150.0), (195.0, 260.0)],
        3.0,
        Some((220.0, 180.0)),
        &mut t
    ));
    assert_eq!(
        g.ground_fault(&[(700.0, 50.0), (705.0, 150.0)], 3.0, None, &mut t),
        Some("fabric")
    );
    assert_eq!(
        g.ground_fault(&[(300.0, 500.0), (300.0, 700.0)], 3.0, None, &mut t),
        Some("off open ground")
    );
    assert_eq!(
        g.ground_fault(&[(495.0, 295.0), (505.0, 305.0)], 3.0, None, &mut t),
        Some("through a building")
    );
    assert_eq!(
        g.ground_fault(&[(500.0, 200.0), (500.0, 400.0)], 3.0, None, &mut t),
        Some("fabric")
    );
    assert_eq!(
        g.ground_fault(&[(100.0, 400.0), (100.0, 500.0)], 3.0, None, &mut t),
        Some("crossing")
    );
    // a hook and a kink on open ground; a kink round a building the ground forces
    assert_eq!(
        g.ground_fault(
            &[(300.0, 0.0), (300.0, 100.0), (310.0, 100.0)],
            3.0,
            None,
            &mut t
        ),
        Some("bends")
    );
    assert_eq!(
        g.ground_fault(
            &[(310.0, 0.0), (300.0, 0.0), (300.0, 100.0)],
            3.0,
            None,
            &mut t
        ),
        Some("bends")
    );
    assert_eq!(
        g.ground_fault(
            &[(300.0, 0.0), (350.0, 0.0), (350.0, 20.0), (400.0, 20.0)],
            3.0,
            None,
            &mut t
        ),
        Some("bends")
    );
    assert!(!g.blocked((0.0, 0.0), (0.0, 0.0), 3.0, &mut t));
}

#[test]
fn a_turn_the_ground_forces_is_lawful() {
    let mut t = Counts::default();
    // a zigzag whose chord a strip of field crosses, the path itself clear of it
    let zig = LawGround {
        open_rings: vec![square(360.0, 5.0, 365.0, 15.0)],
        ..LawGround::default()
    };
    assert!(zig.on_lawful_ground(
        &[(300.0, 0.0), (350.0, 0.0), (350.0, 20.0), (400.0, 20.0)],
        3.0,
        None,
        &mut t
    ));
    // a hook at either end whose chord is blocked
    let hook = LawGround {
        open_rings: vec![square(303.0, 40.0, 306.0, 60.0)],
        ..LawGround::default()
    };
    assert!(hook.on_lawful_ground(
        &[(300.0, 0.0), (300.0, 100.0), (310.0, 100.0)],
        3.0,
        None,
        &mut t
    ));
    assert!(hook.on_lawful_ground(
        &[(310.0, 100.0), (300.0, 100.0), (300.0, 0.0)],
        3.0,
        None,
        &mut t
    ));
    // a doubled-back first turn has no vertex before it to take a chord from
    assert!(!zig.on_lawful_ground(
        &[(300.0, 0.0), (400.0, 0.0), (300.0, 3.0), (300.0, 50.0)],
        3.0,
        None,
        &mut t
    ));
}

#[test]
fn the_grid_asks_the_same_as_the_walk_of_every_outline_and_building() {
    let quads: Vec<Vec<Pt>> = (0..6)
        .map(|k| {
            rot_rect(
                70.0 * f64::from(k),
                40.0 * f64::from(k % 3),
                12.0,
                8.0,
                0.3 * f64::from(k),
            )
        })
        .collect();
    let rings = vec![
        square(0.0, 0.0, 130.0, 90.0),
        square(200.0, 30.0, 330.0, 260.0),
    ];
    let g = LawGround {
        buildings: quads.clone(),
        open_rings: rings.clone(),
        ..LawGround::default()
    };
    let walked = |run: &[Pt]| {
        !rings.iter().any(|ring| {
            let n = ring.len();
            run.windows(2)
                .any(|w| (0..n).any(|k| segments_cross(w[0], w[1], ring[k], ring[(k + 1) % n])))
        })
    };
    let (mut hits, mut opens) = (0, 0);
    for i in 0..40 {
        for j in 0..40 {
            let a = (f64::from(i) * 9.7 - 20.0, f64::from(j) * 7.3 - 20.0);
            let run = [
                a,
                (a.0 + 37.0, a.1 + 11.0 - f64::from(j % 5) * 6.0),
                (a.0 + 3.0, a.1 + 29.0),
            ];
            assert_eq!(g.through_a_building(&run), through_a_building(&run, &quads));
            assert_eq!(g.open_ground(&run), walked(&run));
            hits += usize::from(g.through_a_building(&run));
            opens += usize::from(g.open_ground(&run));
        }
    }
    assert!(hits > 0 && hits < 1600 && opens > 0 && opens < 1600);
    // a lone point asks whether it stands inside a building
    let c = quads[1]
        .iter()
        .fold((0.0, 0.0), |a, p| (a.0 + p.0 / 4.0, a.1 + p.1 / 4.0));
    assert!(g.through_a_building(&[c]) && !g.through_a_building(&[(-500.0, -500.0)]));
    // a fixture the grid files is met by a run across it, and missed by one far off
    let well = square(600.0, 600.0, 610.0, 610.0);
    let fixed = LawGround {
        fixtures: vec![(well.clone(), poly_box(&well))],
        ..LawGround::default()
    };
    let mut t = Counts::default();
    assert_eq!(
        fixed.fouled(&[(590.0, 605.0), (620.0, 605.0)], 3.0, None, &mut t),
        Some(0)
    );
    assert_eq!(
        fixed.fouled(&[(0.0, 0.0), (20.0, 0.0)], 3.0, None, &mut t),
        None
    );
}
