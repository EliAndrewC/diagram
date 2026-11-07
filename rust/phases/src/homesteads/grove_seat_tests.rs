//! A scattered hamlet's seating: its unit tests (feature 444 T30).
//!
//! Research:
//!     the scattered seating's tests - NONE: fixtures and assertions, deciding nothing about the place

use super::bearing::Margin;
use super::bundle::Grove;
use super::dispersed::bundle_turn;
use super::fit_rules::Rules;
use super::fixtures::{Forms, Kind};
use super::ground::Ground;
use super::grove_rounds::seat_scattered;
use super::grove_seat::{
    cluster_seeds, drawn_aspect, front_row, ground_push, row_span, turned_reach, water_push, Axes,
    Corridors, GroveSite,
};
use super::lots::Lots;
use super::place::Site;
use super::Counts;
use crate::field::fan::Pt;
use crate::pyrand::PyRandom;

fn axes() -> Axes {
    Axes {
        c: (1200.0, 1250.0),
        along: (1.0, 0.0),
        out: (0.0, -1.0),
        anchor: (1200.0, 1500.0),
        lat: 400.0,
    }
}

#[test]
fn the_front_row_is_offset_from_its_chains_center_out() {
    let chains = vec![vec![((200.0, 1500.0), (2200.0, 1500.0), (0.0, -1.0))]];
    let row = front_row(&chains, &axes(), (-30.0, -20.0, 30.0, 40.0), 100.0, 400.0);
    assert!(!row.is_empty() && row.len() <= 9);
    // each seat the house's reach toward its chord, the wall's gap and the slack off it, the nearest the seat first
    assert!(row
        .iter()
        .all(|(q, n)| (q.1 - (1500.0 - 50.0)).abs() < 1e-9 && *n == (0.0, -1.0)));
    assert!(row
        .windows(2)
        .all(|w| (w[0].0 .0 - 1200.0).abs() <= (w[1].0 .0 - 1200.0).abs() + 1e-9));
    // a degenerate chord is passed, a long field thinned to 64
    let long = vec![vec![
        ((0.0, 0.0), (0.0, 0.0), (0.0, -1.0)),
        ((0.0, 1500.0), (90000.0, 1500.0), (0.0, -1.0)),
    ]];
    assert_eq!(
        front_row(
            &long,
            &axes(),
            (-30.0, -20.0, 30.0, 40.0),
            10.0,
            f64::INFINITY
        )
        .len(),
        64
    );
    // a chord facing east: the house's west reach
    let east = vec![vec![((100.0, 0.0), (100.0, 400.0), (1.0, 0.0))]];
    let e = front_row(
        &east,
        &Axes {
            anchor: (100.0, 200.0),
            along: (0.0, 1.0),
            ..axes()
        },
        (-30.0, -20.0, 30.0, 40.0),
        100.0,
        1000.0,
    );
    assert!(e.iter().all(|(q, _)| (q.0 - (100.0 + 40.0)).abs() < 1e-9));
}

#[test]
fn a_seat_is_pushed_off_the_other_ground_and_the_water() {
    let mut t = Counts::default();
    assert!((turned_reach((-30.0, -20.0, 30.0, 40.0), 0.0, (0.0, 1.0)) - 40.0).abs() < 1e-9);
    assert!(turned_reach((-30.0, -20.0, 30.0, 40.0), 20.0, (0.0, 1.0)) > 40.0);
    let n = (0.0, -1.0);
    let bx = (500.0, 500.0, 60.0, 60.0);
    // clear: unmoved
    let clear = Corridors::default();
    assert_eq!(
        ground_push((500.0, 500.0), n, bx, &clear, &mut t),
        ((500.0, 500.0), false)
    );
    // a ring the box stands in: pushed past its vertices by a footpath's room
    let ring = Corridors {
        rings: vec![vec![
            (480.0, 490.0),
            (520.0, 490.0),
            (520.0, 600.0),
            (480.0, 600.0),
        ]],
        ..Corridors::default()
    };
    let (q, wet) = ground_push((500.0, 500.0), n, bx, &ring, &mut t);
    assert!(!wet && q.1 < 500.0 - 20.0);
    // a ring the box stands in whose vertices all lie beside it: hit, and unmoved
    let wide = Corridors {
        rings: vec![vec![
            (300.0, 400.0),
            (700.0, 400.0),
            (700.0, 700.0),
            (300.0, 700.0),
        ]],
        ..Corridors::default()
    };
    assert_eq!(
        ground_push((500.0, 500.0), n, bx, &wide, &mut t),
        ((500.0, 500.0), false)
    );
    // a hole in it leaves a point inside unhit; a vertex inside the box still hits
    let holed = Corridors {
        holes: vec![vec![
            (450.0, 470.0),
            (550.0, 470.0),
            (550.0, 530.0),
            (450.0, 530.0),
        ]],
        ..ring
    };
    assert!(!holed.hit_points(&[(500.0, 500.0)], &mut t));
    assert!(holed.hit_points(&[(390.0, 480.0), (610.0, 610.0)], &mut t));
    // a brook across it: pushed by the water, and the clearance's sampling
    let brook = Corridors {
        water: vec![((300.0, 526.0), (700.0, 526.0), 8.0)],
        ..Corridors::default()
    };
    let (q, wet) = ground_push((500.0, 500.0), n, bx, &brook, &mut t);
    assert!(wet && q.1 < 500.0);
    assert!(water_push(&brook.water, (500.0, 500.0), n, 30.0, -530.0, -470.0) > 0.0);
    assert!(
        water_push(
            &[((5000.0, 5000.0), (5100.0, 5000.0), 8.0)],
            (500.0, 500.0),
            n,
            30.0,
            -530.0,
            -470.0
        )
        .abs()
            < 1e-12
    );
}

#[test]
fn the_cloud_and_the_bands_are_pythons_shapes() {
    for shape in ["round", "elongated", "crescent", "split"] {
        let mut rng = PyRandom::new(12345);
        let pts = cluster_seeds(shape, 300.0, 120.0, 40, &mut rng);
        assert_eq!(pts.len(), 40);
        assert!(pts
            .iter()
            .all(|p| p.0.abs() <= 300.0 * 1.04 + 1e-9 && p.1.abs() <= 120.0 * 1.4 + 1e-9));
    }
    assert_eq!(drawn_aspect("round"), (1.0, 2.0));
    assert_eq!(drawn_aspect("elongated"), (2.8, 12.0));
    assert_eq!(drawn_aspect("split"), (1.9, 4.2));
    assert!(
        (row_span("round") - 1.2).abs() < 1e-12
            && (row_span("elongated") - 2.6).abs() < 1e-12
            && (row_span("crescent") - 1.6).abs() < 1e-12
    );
}

#[test]
#[expect(
    clippy::too_many_lines,
    reason = "one scattered hamlet's seatings, each built on the last"
)]
fn a_scattered_hamlet_seats_its_row_ranks_and_the_rest_and_a_single_file_its_row() {
    let mut t = Counts::default();
    let canvas = (2400.0, 2400.0);
    let field = vec![
        (200.0, 1500.0),
        (2200.0, 1500.0),
        (2200.0, 2300.0),
        (200.0, 2300.0),
    ];
    let mut ground = Ground::new((0.0, 0.0), canvas, &mut t);
    ground.fill_ring(&field, &mut t);
    let reach = ground.reach(&[], &mut t);
    let margin = Margin::new(&field, 0.0, &mut t);
    let lots = Lots::deal(4, 9, 0.0, &[(Kind::Privy, 1.0), (Kind::Persimmon, 0.5)]);
    let forms = Forms::default();
    let beyond = |_p: Pt| true;
    assert!(beyond((0.0, 0.0)));
    let rules = Rules {
        chains: vec![vec![((200.0, 1500.0), (2200.0, 1500.0), (0.0, -1.0))]],
        sun: true,
        placed: vec![(150.0, 150.0, 10.0, 10.0)],
        ..Rules::default()
    };
    let site = Site {
        ground: &ground,
        beyond: &beyond,
        reach: &reach,
        field: &field,
        streams: &[],
        canvas,
        bearing: (&margin, 0.0),
        lots: &lots,
        byre: None,
        forms: &forms,
        shade: 50.0,
        rules: &rules,
    };
    let chains = rules.chains.clone();
    let paddies = vec![field.clone()];
    let corridors = Corridors {
        water: vec![((1000.0, 1300.0), (1000.0, 1490.0), 8.0)],
        ..Corridors::default()
    };
    let gs = GroveSite {
        site: &site,
        grove: Grove {
            sides: 2,
            turn: bundle_turn("NW"),
            sun_band: true,
            well: 0.0,
            yard_sun: 66.6,
        },
        paddies: &paddies,
        corridors: &corridors,
        axes: axes(),
        chains: &chains,
        house_max: (62.1, 30.8),
        shape: "crescent",
        alleys: true,
        seed: 7,
        want: 9,
        band: (400.0, 150.0),
        bound: 1.15 * 400.0_f64.hypot(150.0),
        single_file: false,
        streets: (&[], 0.0),
    };
    let st = seat_scattered(&gs);
    assert_eq!(st.seated.len(), 9, "every household seated");
    // a watercourse along the front row: each seat pushed off its water, and tried a quarter seat either side
    let wet = Corridors {
        water: vec![((200.0, 1420.0), (2200.0, 1420.0), 8.0)],
        ..Corridors::default()
    };
    let pushed = seat_scattered(&GroveSite {
        corridors: &wet,
        ..gs
    });
    assert!(pushed.seated.len() <= 9);
    // grove farms with their own well pockets: each well's box among the homestead's parts its streets keep off
    let welled = seat_scattered(&GroveSite {
        grove: Grove {
            well: 8.0,
            ..gs.grove
        },
        ..gs
    });
    assert!(welled.seated.iter().any(|a| a.bundle.well.is_some()));
    // every farm off the field, its bands with it, no two homesteads' boxes within 2 ft
    for (i, a) in st.seated.iter().enumerate() {
        assert!(!a.bundle.groves.is_empty());
        // (its box carries the frame's lane pad, which may overhang the field; its parts and bands may not)
        let south = |r: super::layout::Rect| r.1 + r.3 / 2.0 <= 1500.0 + 4.0;
        assert!(
            a.bundle.boxes.iter().all(|&r| south(r)) && a.bundle.groves.iter().all(|g| south(g.0))
        );
        for b in &st.seated[i + 1..] {
            let (p, q) = (a.bundle.bbox, b.bundle.bbox);
            assert!(
                (p.0 - q.0).abs() >= f64::midpoint(p.2, q.2) + 2.0 - 1e-6
                    || (p.1 - q.1).abs() >= f64::midpoint(p.3, q.3) + 2.0 - 1e-6
            );
        }
    }
    // in single file round the field: its row alone
    let line = seat_scattered(&GroveSite {
        single_file: true,
        grove: Grove {
            sides: 4,
            well: 30.0,
            sun_band: false,
            yard_sun: 22.0,
            ..gs.grove
        },
        ..gs
    });
    assert!(!line.seated.is_empty() && line.seated.len() <= 9);
    // a field that takes the whole canvas seats no one
    let mut full = Ground::new((0.0, 0.0), canvas, &mut t);
    full.fill_ring(
        &[
            (-10.0, -10.0),
            (2410.0, -10.0),
            (2410.0, 2410.0),
            (-10.0, 2410.0),
        ],
        &mut t,
    );
    let none = seat_scattered(&GroveSite {
        site: &Site {
            ground: &full,
            ..site
        },
        ..gs
    });
    assert!(none.seated.is_empty());
}

#[test]
fn a_crowded_hamlet_takes_its_rescue_and_the_rest_of_the_ground() {
    let mut t = Counts::default();
    let canvas = (1150.0, 800.0);
    // a field over most of the canvas, free ground north of it and east, past the band's reach; a repeated vertex in the paddy's
    // outline
    let field = vec![
        (80.0, 220.0),
        (720.0, 220.0),
        (720.0, 220.0),
        (720.0, 780.0),
        (80.0, 780.0),
    ];
    // the ground's window short of the canvas's south edge: the ground past it asked of `beyond`
    let mut ground = Ground::new((0.0, 0.0), (1150.0, 720.0), &mut t);
    ground.fill_ring(&field, &mut t);
    let reach = ground.reach(&[], &mut t);
    let margin = Margin::new(&field, 0.0, &mut t);
    let lots = Lots::deal(5, 12, 0.0, &[(Kind::Retirement, 1.0), (Kind::Bath, 1.0)]);
    let forms = Forms::default();
    let beyond = |_p: Pt| true;
    assert!(beyond((0.0, 0.0)));
    let rules = Rules {
        chains: vec![vec![((80.0, 220.0), (720.0, 220.0), (0.0, -1.0))]],
        sun: true,
        ..Rules::default()
    };
    let site = Site {
        ground: &ground,
        beyond: &beyond,
        reach: &reach,
        field: &field,
        streams: &[],
        canvas,
        bearing: (&margin, 0.0),
        lots: &lots,
        byre: None,
        forms: &forms,
        shade: 50.0,
        rules: &rules,
    };
    let chains = rules.chains.clone();
    let paddies = vec![field.clone()];
    let corridors = Corridors::default();
    let gs = GroveSite {
        site: &site,
        grove: Grove {
            sides: 3,
            turn: bundle_turn("NW"),
            sun_band: true,
            well: 30.0,
            yard_sun: 66.6,
        },
        paddies: &paddies,
        corridors: &corridors,
        axes: Axes {
            c: (400.0, 130.0),
            along: (1.0, 0.0),
            out: (0.0, -1.0),
            anchor: (400.0, 220.0),
            lat: 150.0,
        },
        chains: &chains,
        house_max: (62.1, 30.8),
        shape: "round",
        alleys: false,
        seed: 11,
        want: 12,
        band: (120.0, 60.0),
        bound: 150.0,
        single_file: false,
        streets: (&[], 0.0),
    };
    let mut st = seat_scattered(&gs);
    assert!(st.seated.len() < 12 && st.search.0 > 12);
    // ...and its lots, once spent, take no seat: a ninth lot offered on a three-lot deal is refused
    let three = Lots::deal(5, 3, 0.0, &[]);
    let small = Site {
        lots: &three,
        ..site
    };
    let mut few = seat_scattered(&GroveSite {
        site: &small,
        want: 3,
        ..gs
    });
    assert!(
        few.seated.len() <= 3 && !few.offer_grove(&GroveSite { site: &small, ..gs }, 400.0, 100.0)
    );
    // the nearest point of an outline with a repeated vertex, and none of no outline
    let _ = st.offer_grove(&gs, 400.0, 60.0);
    assert!(super::grove_seat::nearest_on((400.0, 250.0), &paddies).is_some());
    assert!(super::grove_seat::nearest_on((400.0, 250.0), &[]).is_none());
}

#[test]
fn a_band_in_a_yards_strip_or_a_beds_morning_sun_is_seen() {
    use super::grove_seat::{bed_shaded, yard_shaded};
    let yard = (0.0, 0.0, 30.0, 20.0);
    assert!(
        yard_shaded((0.0, 20.0, 40.0, 10.0), yard) && !yard_shaded((0.0, 80.0, 40.0, 10.0), yard)
    );
    let bed = (0.0, 0.0, 20.0, 20.0);
    assert!(bed_shaded((20.0, 0.0, 10.0, 40.0), bed));
    assert!(
        !bed_shaded((60.0, 0.0, 10.0, 40.0), bed)
            && !bed_shaded((20.0, 60.0, 10.0, 20.0), bed)
            && !bed_shaded((20.0, -60.0, 10.0, 20.0), bed)
    );
}
