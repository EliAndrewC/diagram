//! The fixtures' unit tests (feature 444 T30).
//!
//! Research:
//!     the fixtures' tests - NONE: fixtures and assertions, deciding nothing about the place
#![expect(
    clippy::float_cmp,
    clippy::too_many_lines,
    reason = "the tests' own arithmetic, exact table values and one test a table"
)]

use super::fixtures::{
    along, along_its_wall, bath_seats, bath_wall, clears, in_dooryard, lay, outward, seats, shades,
    shed_off_a_wall, size_ft, wall_places, weighted, within_reach_of, Forms, Frame, Kind, Place,
    Unlaid, Wall, ORDER, PIT_FT, PRIVY_SUN, WALL_GAP_FT,
};
use super::layout::{hjit, Rect};

fn frame<'a>(
    roofs: &'a [Rect],
    ground: &'a [Rect],
    yard: Option<Rect>,
    kura: bool,
    shade: (f64, &'a [f64]),
    keep: &'a [Rect],
) -> Frame<'a> {
    Frame {
        house: (46.0, 28.0),
        roofs,
        ground,
        yard,
        kura,
        shade,
        keep,
    }
}

#[test]
fn every_kind_is_laid_beside_its_house_in_order_with_its_rule_kept() {
    let house = (0.0, 0.0, 46.0, 28.0);
    let yard = (0.0, 27.0, 30.0, 20.0);
    let bed = (30.0, 25.0, 12.0, 14.0);
    let turns = [0.0, 10.0];
    let forms = Forms::default();
    let mut t = 0;
    let mut seen = 0;
    for k in 0..40 {
        let seat = (f64::from(k) * 53.0, f64::from(k) * 17.0);
        let roll = |s: f64| hjit(seat.0, seat.1, s);
        let roofs = [house];
        let ground = [yard, bed];
        let fr = frame(&roofs, &ground, Some(yard), k % 2 == 0, (20.0, &turns), &[]);
        let (laid, bath) =
            lay(&ORDER, &fr, &roll, &forms, &mut t).expect("every kind laid on a realistic frame");
        seen += 1;
        let kinds: Vec<Kind> = laid.iter().map(|(k, _)| *k).collect();
        // in order; every kind but the persimmon laid
        assert!(
            kinds
                .windows(2)
                .all(|p| ORDER.iter().position(|o| *o == p[0])
                    < ORDER.iter().position(|o| *o == p[1]))
        );
        assert!(ORDER
            .iter()
            .filter(|k| **k != Kind::Persimmon)
            .all(|k| kinds.contains(k)));
        assert!(bath.is_some());
        for (kind, r) in &laid {
            match kind {
                Kind::Privy => assert!(within_reach_of(*r, house, PRIVY_SUN.1)),
                Kind::Woodpile => assert!(r.1 + r.3 / 2.0 <= 14.0 + 1e-6),
                Kind::Persimmon => assert!(in_dooryard(r.0, r.1, r.2 / 2.0, 46.0, 28.0, 30.0)),
                _ => {}
            }
            // no two fixtures overlap
            for (other, q) in &laid {
                if other != kind && *other != Kind::Persimmon && *kind != Kind::Persimmon {
                    assert!(clears(*r, &[*q], -1e-6, &mut t));
                }
            }
        }
    }
    assert_eq!(seen, 40);
}

#[test]
fn a_kind_with_no_seat_refuses_the_layout_and_a_persimmon_is_simply_not_kept() {
    let forms = Forms::default();
    let roll = |s: f64| hjit(1.0, 2.0, s);
    let mut t = 0;
    // the house walled round by a ring of roofs: no bath room, no shed, no privy
    let house = (0.0, 0.0, 46.0, 28.0);
    let wall = (0.0, 0.0, 800.0, 800.0);
    let roofs = [house];
    let ground = [wall];
    for kinds in [
        &[Kind::Bath][..],
        &[Kind::Woodpile][..],
        &[Kind::Privy][..],
        &[Kind::Coop][..],
    ] {
        let fr = frame(&roofs, &ground, None, false, (0.0, &[0.0]), &[]);
        assert!(matches!(
            lay(kinds, &fr, &roll, &forms, &mut t),
            Err(Unlaid(_))
        ));
    }
    // the bath room may stand on the kept ground; nothing else may
    let kept = [wall];
    let fr = frame(&roofs, &[], None, false, (0.0, &[0.0]), &kept);
    assert!(lay(&[Kind::Bath], &fr, &roll, &forms, &mut t).is_ok());
    assert!(lay(&[Kind::Shrine], &fr, &roll, &forms, &mut t).is_err());
    // a persimmon with no seat is not kept, the rest laid
    let fr = frame(&roofs, &ground, None, false, (0.0, &[0.0]), &[]);
    assert_eq!(
        lay(&[Kind::Persimmon], &fr, &roll, &forms, &mut t),
        Ok((vec![], None))
    );
}

#[test]
fn the_tables_and_rolls_hold_their_research() {
    let forms = Forms::default();
    let roll = |s: f64| hjit(3.0, 4.0, s);
    assert_eq!(
        size_ft(
            Kind::Manure,
            &Forms {
                manure_pit: true,
                ..Forms::default()
            },
            &roll
        ),
        (PIT_FT, PIT_FT)
    );
    assert_eq!(
        size_ft(Kind::Retirement, &forms, &roll),
        forms.retirement_ft
    );
    assert_eq!(size_ft(Kind::Coop, &forms, &roll), (5.0, 5.0));
    let b = size_ft(Kind::Bath, &forms, &roll);
    assert!((6.0..=12.0).contains(&b.0) && b.1 == 6.0);
    assert_eq!(weighted(&[0.5, 0.25], 0.9), 1);
    assert_eq!(weighted(&[0.5, 0.25], 0.6), 1);
    assert_eq!(weighted(&[0.5, 0.25], 0.1), 0);
    assert_eq!(bath_wall(0.1, &forms), Wall::StableEnd);
    assert_eq!(bath_wall(0.81, &forms), Wall::FlooredRooms);
    assert_eq!(bath_wall(0.9, &forms), Wall::MainDoor);
    // the bath room's seats, the rolled wall first, then the slides
    let s = bath_seats(Wall::MainDoor, 46.0, 28.0, 8.0, 6.0, Some((0.0, 15.0)));
    assert_eq!(s[0].1, Wall::MainDoor);
    assert!(s.iter().any(|(_, k)| *k == Wall::FlooredRooms) && s.len() > 9);
    assert_eq!(
        bath_seats(Wall::StableEnd, 46.0, 28.0, 8.0, 6.0, None)[0].1,
        Wall::StableEnd
    );
    // a narrow yard leaves room past its sides on the front wall
    let narrow = bath_seats(Wall::MainDoor, 46.0, 28.0, 8.0, 6.0, Some((0.0, 5.0)));
    assert!(narrow
        .iter()
        .take(4)
        .any(|(q, _)| (q.0.abs() - 12.0).abs() < 1e-9));
    // the walk along a wall, out from the center, and its places
    assert_eq!(along(0.0, 4.0), vec![0.0]);
    assert_eq!(along(5.0, 4.0), vec![0.0, -4.0, 4.0, -5.0, 5.0]);
    assert_eq!(
        along_its_wall((20.0, 30.0, 6.0, 6.0), 4.0, 10, 23.0).len(),
        0
    );
    assert_eq!(
        along_its_wall((-5.0, 30.0, 6.0, 6.0), 4.0, 10, 23.0).len(),
        3
    );
    assert_eq!(
        outward(&[(0.0, 0.0, 1.0, 1.0)], 8.0, 2),
        vec![(0.0, 0.0, 1.0, 1.0); 2]
    );
    assert_eq!(
        wall_places(&[(0.0, 0.0, 10.0, 10.0)], 4.0, 4.0, 1.0, 4.0).len() % 4,
        0
    );
    // every kind's recorded seats
    for kind in ORDER {
        assert!(!seats(kind, 46.0, 28.0, 6.0, 6.0, None, &roll, 0.4, &forms).is_empty());
    }
    let privy = (10.0, -30.0, 6.0, 6.0);
    assert_eq!(
        seats(
            Kind::Manure,
            46.0,
            28.0,
            8.0,
            6.0,
            Some(privy),
            &roll,
            0.4,
            &forms
        )
        .len(),
        8
    );
    assert!(
        seats(
            Kind::Manure,
            46.0,
            28.0,
            8.0,
            6.0,
            Some((0.0, 0.0, 6.0, 6.0)),
            &roll,
            0.4,
            &forms
        )
        .len()
            == 8
    );
    // a privy rolled off the sun side takes its attested places only; on it, the sector first
    let sunny = |s: f64| if (s - 101.25).abs() < 1e-9 { 0.1 } else { 0.5 };
    let shady = |s: f64| if (s - 101.25).abs() < 1e-9 { 0.9 } else { 0.5 };
    assert_eq!(
        seats(Kind::Privy, 46.0, 28.0, 6.0, 6.0, None, &shady, 0.4, &forms).len(),
        3
    );
    assert!(seats(Kind::Privy, 46.0, 28.0, 6.0, 6.0, None, &sunny, 0.4, &forms).len() > 3);
    assert!(Forms::default()
        .privy_weights
        .iter()
        .any(|(p, _)| *p == Place::Barn));
    // the shed's rule and the sun ground
    let walls = [(0.0, 0.0, 46.0, 28.0)];
    let mut t = 0;
    assert!(shed_off_a_wall(
        (0.0, -(14.0 + WALL_GAP_FT + 6.0 + 6.0), 24.0, 12.0),
        &walls,
        &mut t
    ));
    assert!(!shed_off_a_wall((0.0, 30.0, 24.0, 12.0), &walls, &mut t));
    assert!(shades(
        0.0,
        27.0,
        5.0,
        &[(0.0, 0.0, 10.0, 10.0)],
        20.0,
        &[0.0]
    ));
    assert!(!shades(
        0.0,
        -30.0,
        5.0,
        &[(0.0, 0.0, 10.0, 10.0)],
        20.0,
        &[0.0]
    ));
}
