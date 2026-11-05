//! The dispersed farmstead's layout: its unit tests, against values the Python layout gives the same input (feature 444 T30).
//!
//! Research:
//!     the dispersed layout's tests - NONE: fixtures and assertions, deciding nothing about the place

use super::dispersed::{
    bundle_turn, clear_east_of_beds, dispersed_layout, door_room, turn_face, turns_axes,
    way_in_strip, Depth, Layout, Spec, E, N, S, W,
};
use super::layout::Rect;

fn near(a: Rect, b: Rect) -> bool {
    [(a.0, b.0), (a.1, b.1), (a.2, b.2), (a.3, b.3)]
        .iter()
        .all(|(x, y)| (x - y).abs() < 1e-6)
}

fn spec(sides: u32, sun_band: bool, well: f64) -> Spec {
    Spec {
        gap: 3.0,
        garden: (22.08, 23.8),
        yard: (34.0, 22.0),
        sides,
        garden_by_yard: false,
        thin: 17.0,
        sun_east: 50.0,
        way_in: 36.0,
        yard_sun: if sun_band { 69.56 } else { 22.0 },
        sun_band,
        back: 24.0,
        well,
    }
}

#[test]
fn a_two_sided_grove_in_the_canonical_frame_is_pythons() {
    let out = dispersed_layout(
        (500.0, 400.0, 46.0, 28.0),
        &spec(2, false, 0.0),
        bundle_turn("NW"),
        16.0,
    );
    assert!(near(out.yard, (500.0, 428.0, 34.0, 22.0)));
    assert!(near(out.garden, (537.04, 400.0, 22.08, 23.8)));
    assert!(near(out.frame, (477.06, 377.02, 174.04, 155.96)));
    assert_eq!(out.well, None);
    assert!(
        near(out.groves[0], (477.06, 337.02, 142.04, 43.96))
            && near(out.groves[1], (428.02, 399.0, 43.96, 80.0))
    );
    assert_eq!(out.faces, vec![(N, Depth::Deep), (W, Depth::Deep)]);
}

#[test]
fn a_three_sided_grove_turned_to_a_southeast_wind_on_a_sun_keeping_map_is_pythons() {
    let out = dispersed_layout(
        (500.0, 400.0, 46.0, 28.0),
        &spec(3, true, 0.0),
        bundle_turn("SE"),
        16.0,
    );
    assert!(near(out.yard, (463.0, 400.0, 22.0, 34.0)));
    assert!(near(out.garden, (462.1, 368.96, 23.8, 22.08)));
    assert!(near(out.frame, (536.21, 403.07, 204.02, 258.3)));
    let want = [
        (586.11, 403.07, 72.22, 226.3),
        (500.1, 480.11, 99.8, 72.22),
        (513.5, 298.42, 73.0, 17.0),
    ];
    assert!(out.groves.iter().zip(want).all(|(&a, b)| near(a, b)));
    assert_eq!(
        out.faces,
        vec![(E, Depth::Deep), (S, Depth::Deep), (N, Depth::Thin)]
    );
}

#[test]
fn a_ring_with_its_well_pocket_turned_southwest_and_northeast_is_pythons() {
    let sw = dispersed_layout(
        (500.0, 400.0, 46.0, 28.0),
        &spec(4, true, 55.6),
        bundle_turn("SW"),
        16.0,
    );
    assert!(near(sw.well.unwrap(), (537.0, 447.8, 55.6, 55.6)));
    assert!(near(sw.frame, (515.07, 432.37, 306.58, 316.9)));
    assert!(
        near(sw.groves[3], (643.86, 496.41, 17.0, 156.82))
            && near(sw.groves[4], (643.86, 335.96, 17.0, 92.08))
    );
    let ne = dispersed_layout(
        (500.0, 400.0, 46.0, 28.0),
        &spec(4, false, 55.6),
        bundle_turn("NE"),
        16.0,
    );
    assert!(near(ne.garden, (468.96, 428.0, 22.08, 23.8)));
    assert!(near(ne.well.unwrap(), (547.8, 439.8, 55.6, 55.6)));
    assert!(near(ne.frame, (518.24, 411.32, 288.64, 224.56)));
    let want = [
        (518.24, 337.02, 256.64, 43.96),
        (624.58, 433.3, 43.96, 148.6),
        (398.42, 433.3, 17.0, 148.6),
        (582.28, 499.1, 128.56, 17.0),
        (435.96, 499.1, 92.08, 17.0),
    ];
    assert!(ne.groves.iter().zip(want).all(|(&a, b)| near(a, b)));
    // a ring's well pocket stands below a shallow yard's middle, its wellhead clear of the house's front wall
    let deep = Spec {
        yard: (20.0, 6.0),
        ..spec(4, false, 55.6)
    };
    let low = dispersed_layout((0.0, 0.0, 46.0, 28.0), &deep, bundle_turn("NW"), 0.0);
    assert!(low.well.unwrap().1 > low.yard.1);
}

#[test]
fn a_three_sided_grove_on_an_unkept_map_closes_the_east_to_the_yard() {
    let out = dispersed_layout(
        (0.0, 0.0, 46.0, 28.0),
        &spec(3, false, 0.0),
        bundle_turn("NW"),
        0.0,
    );
    let east = out.groves[2];
    assert_eq!(out.faces[2], (E, Depth::Thin));
    assert!((east.1 + east.3 / 2.0 - (out.yard.1 + out.yard.3 / 2.0)).abs() < 1e-9);
}

#[test]
fn the_symmetries_carry_the_faces() {
    assert_eq!(bundle_turn("ZZ"), (1, 0, 0, 1));
    assert!(turns_axes(bundle_turn("SW")) && !turns_axes(bundle_turn("NE")));
    assert_eq!(turn_face(bundle_turn("SE"), N), (1, 0));
}

#[test]
fn a_band_in_a_beds_morning_sun_is_cut_back_or_dropped_as_pythons() {
    let cut = clear_east_of_beds(
        &[
            (560.0, 380.0, 17.0, 120.0),
            (900.0, 380.0, 17.0, 60.0),
            (540.0, 400.0, 20.0, 10.0),
        ],
        &[(520.0, 400.0, 22.0, 24.0)],
        50.0,
    );
    assert_eq!(cut.len(), 2);
    assert!(near(cut[0], (560.0, 353.5, 17.0, 67.0)) && near(cut[1], (900.0, 380.0, 17.0, 60.0)));
    // a band south of the bed is cut back from its north end
    let south = clear_east_of_beds(
        &[(560.0, 460.0, 17.0, 100.0)],
        &[(520.0, 400.0, 22.0, 24.0)],
        50.0,
    );
    assert!(near(south[0], (560.0, 461.5, 17.0, 97.0)));
}

#[test]
fn a_rings_way_in_and_its_doors_room_are_pythons() {
    let house = (0.0, 0.0, 46.0, 28.0);
    let lay = |sides, key| {
        dispersed_layout(
            house,
            &Spec {
                yard_sun: 22.0,
                ..spec(sides, false, 0.0)
            },
            bundle_turn(key),
            16.0,
        )
    };
    let faces = |l: &Layout| l.faces.iter().map(|f| f.0).collect::<Vec<_>>();
    let nw = lay(4, "NW");
    assert!(near(
        way_in_strip(house, &nw.groves, &faces(&nw)).unwrap(),
        (0.0, 38.0, 36.0, 48.0)
    ));
    let sw = lay(4, "SW");
    assert!(near(
        way_in_strip(house, &sw.groves, &faces(&sw)).unwrap(),
        (47.45, 0.0, 48.9, 36.0)
    ));
    let two = lay(2, "NW");
    assert!(way_in_strip(house, &two.groves, &faces(&two)).is_none());
    assert!(near(
        door_room(house, (0.0, 28.0, 34.0, 22.0), 8.0, 12.0),
        (0.0, 47.0, 24.0, 24.0)
    ));
    assert!(near(
        door_room(house, (-30.0, 0.0, 22.0, 34.0), 8.0, 12.0),
        (-49.0, 0.0, 24.0, 24.0)
    ));
}

#[test]
#[expect(
    clippy::too_many_lines,
    reason = "one grove farm's scenarios, each built on the last"
)]
fn a_grove_farm_is_laid_round_its_bands_and_turned_with_its_house() {
    use super::bundle::{grove_bundle, Grove, Lot, Sun};
    use super::fixtures::{Forms, Kind};
    use super::Counts;
    let lot = Lot {
        house: (46.0, 28.0),
        kura: false,
        byre: None,
        fixtures: vec![Kind::Privy, Kind::Persimmon, Kind::Woodpile],
    };
    let grove = Grove {
        sides: 4,
        turn: bundle_turn("NW"),
        sun_band: true,
        well: 55.6,
        yard_sun: 66.62,
    };
    let sun = Sun {
        shade: 50.0,
        turns: &[8.0],
    };
    let mut t = Counts::default();
    let b = grove_bundle(
        &lot,
        (500.0, 400.0),
        (500.0, 400.0),
        8.0,
        &Forms::default(),
        &sun,
        &grove,
        &mut t,
    );
    assert!(b.unlaid.is_none(), "{:?}", b.unlaid);
    assert_eq!(b.groves.len(), 5);
    assert!(b.groves.iter().any(|g| g.2 == Depth::Deep));
    // the yard and the bed turned with the house about its center; the bands unraked
    // (at 8 degrees a yard 28 ft or more south of the house's center stands over 3.5 ft sideways of it)
    assert!((b.yard.0 - 500.0).abs() > 3.5);
    assert!(b.well.is_some() && b.boxes.len() == 2 + b.gardens.len() + b.fixtures.len());
    // every part and the grove's frame inside the box round them
    let inside = |r: Rect| {
        r.0 - r.2 / 2.0 >= b.bbox.0 - b.bbox.2 / 2.0 - 1e-9
            && r.0 + r.2 / 2.0 <= b.bbox.0 + b.bbox.2 / 2.0 + 1e-9
    };
    assert!(b.groves.iter().all(|g| inside(g.0)) && b.boxes.iter().all(|&r| inside(r)));
    // no fixture but the persimmon stands in a band
    let meets = |a: Rect, g: Rect| {
        (a.0 - g.0).abs() < f64::midpoint(a.2, g.2) && (a.1 - g.1).abs() < f64::midpoint(a.3, g.3)
    };
    assert!(b
        .fixtures
        .iter()
        .filter(|(k, _)| *k != Kind::Persimmon)
        .all(|&(_, f)| b.groves.iter().all(|g| !meets(f, g.0))));
    // a two-sided grove with no well: no way in to keep, no pocket
    let open = grove_bundle(
        &lot,
        (500.0, 400.0),
        (500.0, 400.0),
        0.0,
        &Forms::default(),
        &sun,
        &Grove {
            sides: 2,
            well: 0.0,
            sun_band: false,
            yard_sun: 22.0,
            ..grove
        },
        &mut t,
    );
    assert!(open.well.is_none() && open.groves.len() == 2);
    // a lot whose bath room finds no wall clear inside a closed ring is not the household's
    let crowded = Lot {
        fixtures: vec![
            Kind::Retirement,
            Kind::Bath,
            Kind::Woodpile,
            Kind::Privy,
            Kind::Coop,
            Kind::Shrine,
            Kind::Grave,
        ],
        house: (64.0, 40.0),
        ..lot
    };
    let tight = (0..40).map(|k| {
        let seat = (f64::from(k) * 37.0, f64::from(k) * 11.0);
        grove_bundle(
            &crowded,
            seat,
            seat,
            0.0,
            &Forms::default(),
            &sun,
            &grove,
            &mut t,
        )
    });
    assert!(tight.into_iter().any(|b| b.unlaid.is_some()));
    // a lot with no fixtures lays none
    let bare = Lot {
        fixtures: vec![],
        ..lot
    };
    assert!(grove_bundle(
        &bare,
        (500.0, 400.0),
        (500.0, 400.0),
        0.0,
        &Forms::default(),
        &sun,
        &grove,
        &mut t
    )
    .fixtures
    .is_empty());
}
