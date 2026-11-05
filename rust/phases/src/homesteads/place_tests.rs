//! The seating's unit tests (feature 444 T30).
//!
//! Research:
//!     the seating's tests - NONE: fixtures and assertions, deciding nothing about the place
#![expect(
    clippy::manual_midpoint,
    reason = "two half-sizes summed in the tests' own checks"
)]

use super::bearing::Margin;
use super::fit::{corners, quad_gap, EAVE_FT};
use super::fit_rules::Rules;
use super::fixtures::{Forms, Kind};
use super::ground::Ground;
use super::layout::Byre;
use super::lots::Lots;
use super::passage::{land_box, Tight, TIGHT};
use super::place::{
    box_reach, chain_distance, field_distance, grow, keeps_its_distance, seat_toward, union, Keep,
    Seating, Site,
};
use super::Counts;

#[test]
fn a_cluster_grows_from_its_first_house_every_rule_kept() {
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
    let reach = ground.reach(&[(1200.0, 100.0)], &mut t);
    let margin = Margin::new(&field, 0.0, &mut t);
    let lots = Lots::deal(
        4,
        12,
        0.3,
        &[(Kind::Privy, 1.0), (Kind::Coop, 0.5), (Kind::Woodpile, 0.4)],
    );
    let forms = Forms::default();
    let beyond = |_p: (f64, f64)| true;
    let site = Site {
        ground: &ground,
        beyond: &beyond,
        reach: &reach,
        field: &field,
        streams: &[((1350.0, 1000.0), (1450.0, 1150.0))],
        canvas,
        bearing: (&margin, 0.0),
        lots: &lots,
        byre: Some(Byre::YardShed),
        forms: &forms,
        shade: 50.0,
        rules: &Rules::default(),
    };
    assert!(beyond((0.0, 0.0)));
    let st = grow(&site, (1200.0, 1350.0), 12);
    assert_eq!(st.seated.len(), 12);
    // the first house nearest the seat, the cluster compact about it
    assert!(st
        .seated
        .iter()
        .enumerate()
        .all(|(k, s)| s.lot == k && s.seat.0 > 0.0 && s.wood.len() >= 20));
    let first = &st.seated[0].bundle;
    assert!((first.house.0 - 1200.0).hypot(first.house.1 - 1350.0) < 200.0);
    for (i, a) in st.seated.iter().enumerate() {
        // off the field
        assert!(a.bundle.bbox.1 + a.bundle.bbox.3 / 2.0 <= 1500.0 + 8.0 * 1.5);
        for b in &st.seated[i + 1..] {
            let (ra, rb) = (a.bundle.bbox, b.bundle.bbox);
            assert!(apart(ra, rb));
            let gap = quad_gap(
                &corners(a.bundle.house, a.bundle.turn),
                &corners(b.bundle.house, b.bundle.turn),
            );
            assert!(gap >= EAVE_FT.0);
        }
    }
    assert!(st.search.0 >= 12 && st.search.3 >= 12 && st.tests.total() > 0);
    // no household is seated where the seat's ground is all taken
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
    let none = full.reach(&[(1200.0, 100.0)], &mut t);
    let site_full = Site {
        ground: &full,
        reach: &none,
        ..site
    };
    assert!(grow(&site_full, (1200.0, 1350.0), 3).seated.is_empty());
    // a shared byre's pocket, reserved before any house, takes no wood seat
    let pocket = Rules {
        bars: vec![(1200.0, 1300.0, 80.0)],
        placed: vec![(1200.0, 1300.0, 22.0, 17.0), (300.0, 300.0, 10.0, 10.0)],
        site_chains: vec![vec![((200.0, 1500.0), (2200.0, 1500.0), (0.0, -1.0))]],
        ..Rules::default()
    };
    let barred = grow(
        &Site {
            rules: &pocket,
            ..site
        },
        (1200.0, 1350.0),
        2,
    );
    assert!(barred
        .seated
        .iter()
        .flat_map(|s| &s.wood)
        .all(|w| (w.0 - 1200.0).hypot(w.1 - 1300.0) >= 80.0));
    assert!((field_distance((0.0, 0.0), &field) - (200.0f64.hypot(1500.0))).abs() < 1e-6);
}

#[test]
fn the_growths_tie_break_reads_the_facing_chains() {
    assert!(chain_distance((5.0, 5.0), &[]).abs() < 1e-12);
    let chord = vec![vec![((0.0, 0.0), (10.0, 0.0), (0.0, -1.0))]];
    assert!((chain_distance((5.0, 5.0), &chord) - 5.0).abs() < 1e-9);
}

#[test]
#[expect(
    clippy::too_many_lines,
    reason = "one tight seat's scenarios, each built on the last"
)]
fn a_household_on_a_tight_seat_is_reached_across_its_neighbors_yard() {
    let mut t = Counts::default();
    let canvas = (1000.0, 1000.0);
    let ground = Ground::new((0.0, 0.0), canvas, &mut t);
    let open = ground.reach(&[(500.0, 100.0)], &mut t);
    let shut = ground.reach(&[], &mut t);
    let field = [
        (0.0, 990.0),
        (1000.0, 990.0),
        (1000.0, 1000.0),
        (0.0, 1000.0),
    ];
    let margin = Margin::new(&field, 0.0, &mut t);
    let forms = Forms::default();
    let lots = Lots::deal(4, 2, 0.0, &[]);
    let beyond = |_p: (f64, f64)| true;
    assert!(beyond((0.0, 0.0)));
    let rules = Rules {
        passage_left: 1,
        ..Rules::default()
    };
    let site = Site {
        ground: &ground,
        beyond: &beyond,
        reach: &open,
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
    let mut st = Seating {
        passage_left: 1,
        walks: super::access::AccessTree::new(7.0),
        ..Seating::default()
    };
    assert!(st.offer(&site, 500.0, 400.0, None));
    // ...then no lane ground reached anywhere: a seat against the first household's land is taken only by passage across its yard
    let landlocked = Site {
        reach: &shut,
        ..site
    };
    let (c, fp) = st.footprint(0);
    let mut seated = false;
    'seek: for ang in [1.0, 2.0] {
        for dx in (-15..=10).map(|k| f64::from(k) * 4.0) {
            for dy in (-10..=10).map(|k| f64::from(k) * 4.0) {
                // within a quarter turn of its yard (east-southeast, then southeast): there its footprint ends at its box, and the seat
                // laps it at some offset toward the house
                let q = seat_toward(c, fp, fp, std::f64::consts::FRAC_PI_6 * ang, TIGHT.0);
                let tight = Tight {
                    nb: 0,
                    land: land_box(c, fp),
                    own: (fp.0 + 40.0, fp.1 + 40.0, fp.2 + 20.0, fp.3),
                };
                let keep = Keep {
                    from: (c, fp),
                    gap: TIGHT.0,
                    standing: vec![(c, fp)],
                    others: 20.0,
                    tight: Some(tight),
                };
                // land that does not adjoin the neighbor's has no passage: a moved layout there is refused
                let alone = Keep {
                    tight: Some(Tight {
                        own: (0.0, 0.0, 0.0, 0.0),
                        ..tight
                    }),
                    ..Keep {
                        from: (c, fp),
                        gap: TIGHT.0,
                        standing: vec![(c, fp)],
                        others: 20.0,
                        tight: None,
                    }
                };
                assert!(!st.offer(&landlocked, q.0 + dx, q.1 + dy, Some(&alone)));
                if st.offer(&landlocked, q.0 + dx, q.1 + dy, Some(&keep)) {
                    seated = true;
                    break 'seek;
                }
            }
        }
    }
    assert!(seated, "a tight seat's household seated by passage");
    let p = st.seated[1].passage.as_ref().expect("its passage");
    assert_eq!(
        (p.of, p.depth, st.depth[1], st.passage_left),
        (0, 1, Some(1), 0)
    );
    assert_eq!(p.parts(), (p.walk.clone(), 0, 1));
    // ...its walk kept clear of every later homestead: a box over it is refused
    let w = p.walk[p.walk.len() / 2];
    // ...and with a third lot, a tight seat asked again against the first: the passage household stands among what its walk keeps off
    let three = Lots::deal(4, 3, 0.0, &[]);
    let wider = Site {
        lots: &three,
        ..landlocked
    };
    let again = Keep {
        from: (c, fp),
        gap: TIGHT.0,
        standing: vec![(c, fp), st.footprint(1)],
        others: 20.0,
        tight: Some(Tight {
            nb: 0,
            land: land_box(c, fp),
            own: fp,
        }),
    };
    assert!(!st.offer(&wider, c.0 - 100.0, c.1 + 300.0, Some(&again)));
    assert!(st.walks.covers_box((w.0, w.1, 4.0, 4.0), &mut t));
    assert!(!Seating {
        walks: std::mem::take(&mut st.walks),
        ..Seating::default()
    }
    .offer(&site, w.0, w.1, None));
}

#[test]
fn a_cluster_with_lane_ground_only_at_its_first_house_tries_its_tight_seats_and_seats_none() {
    let mut t = Counts::default();
    let canvas = (1000.0, 1000.0);
    let ground = Ground::new((0.0, 0.0), canvas, &mut t);
    // lane ground only in a pocket about the seat: the first house opens onto it, every later one is landlocked
    let cell = 4.0;
    let nx: u32 = 250;
    let cells: Vec<bool> = (0..nx * nx)
        .map(|k| {
            let (i, j) = (k % nx, k / nx);
            let p = ((f64::from(i) + 0.5) * cell, (f64::from(j) + 0.5) * cell);
            (p.0 - 500.0).abs() > 25.0 || (p.1 - 520.0).abs() > 25.0
        })
        .collect();
    let lanes = Ground::from_cells((0.0, 0.0), cell, nx as usize, cells).unwrap();
    let pocket = lanes.reach(&[(500.0, 520.0)], &mut t);
    let field = [
        (0.0, 990.0),
        (1000.0, 990.0),
        (1000.0, 1000.0),
        (0.0, 1000.0),
    ];
    let margin = Margin::new(&field, 0.0, &mut t);
    let forms = Forms::default();
    let lots = Lots::deal(4, 3, 0.0, &[]);
    let beyond = |_p: (f64, f64)| true;
    assert!(beyond((0.0, 0.0)));
    let rules = Rules {
        passage_left: 1,
        ..Rules::default()
    };
    let site = Site {
        ground: &ground,
        beyond: &beyond,
        reach: &pocket,
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
    // ...its tight seats queued, settled and offered, each refused: one parted from its neighbor's whole footprint (its sun and its
    // wood) laps no box to be moved off, and a seat it is not moved from asks the lane ground, which it does not reach
    let st = grow(&site, (500.0, 500.0), 3);
    assert_eq!((st.seated.len(), st.passage_left), (1, 1));
    assert!(st.seated[0].passage.is_none() && st.search.0 > 1);
}

#[test]
fn the_growths_step_parts_two_footprints() {
    let r = box_reach((0.0, 0.0), (0.0, 0.0, 20.0, 10.0));
    assert_eq!(r, (10.0, 10.0, 5.0, 5.0));
    assert_eq!(union(r, (1.0, 20.0, 1.0, 1.0)), (10.0, 20.0, 5.0, 5.0));
    let q = seat_toward((0.0, 0.0), r, r, 0.0, 2.0);
    assert!((q.0 - 22.0).abs() < 1e-9 && q.1.abs() < 1e-9);
    assert!(seat_toward((0.0, 0.0), r, r, std::f64::consts::FRAC_PI_2, 2.0).1 > 11.0);
    assert!(
        keeps_its_distance((30.0, 0.0, 10.0, 10.0), (0.0, 0.0), r, 2.0)
            && !keeps_its_distance((14.0, 0.0, 10.0, 10.0), (0.0, 0.0), r, 2.0)
    );
}

#[test]
#[expect(
    clippy::too_many_lines,
    reason = "one placer's scenarios, each built on the last"
)]
fn a_seat_is_refused_off_the_canvas_unlaid_or_unreached_and_a_full_ground_stops_the_growth() {
    let mut t = Counts::default();
    let canvas = (600.0, 600.0);
    let ground = Ground::new((0.0, 0.0), canvas, &mut t);
    let reach = ground.reach(&[(300.0, 300.0)], &mut t);
    let margin = Margin::new(
        &[(0.0, 590.0), (600.0, 590.0), (600.0, 600.0), (0.0, 600.0)],
        0.0,
        &mut t,
    );
    let forms = Forms::default();
    let lots = Lots::deal(4, 1, 0.0, &[]);
    let beyond = |_p: (f64, f64)| true;
    let field = [(0.0, 590.0), (600.0, 590.0), (600.0, 600.0), (0.0, 600.0)];
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
        rules: &Rules::default(),
    };
    assert!(beyond((0.0, 0.0)));
    // off the canvas
    let mut st = Seating::default();
    assert!(!st.offer(&site, 5.0, 5.0, None));
    // seated once, then the lots are spent
    assert!(st.offer(&site, 300.0, 250.0, None));
    assert!(!st.offer(&site, 300.0, 450.0, None));
    // a seat whose yard laps one standing homestead is moved off it, and the move asks the growth's distance
    let two = Lots::deal(4, 2, 0.0, &[]);
    let site_two = Site { lots: &two, ..site };
    let mut pair = Seating::default();
    assert!(pair.offer(&site_two, 300.0, 400.0, None));
    let a = pair.seated[0].bundle.bbox;
    let keep = Keep {
        from: ((5000.0, 5000.0), (1.0, 1.0, 1.0, 1.0)),
        gap: 1.0,
        standing: vec![((5000.0, 5000.0), (1.0, 1.0, 1.0, 1.0))],
        others: 1.0,
        tight: None,
    };
    // (the first household's wood seats would close the second's yard off the reach here: this asks the move, not the wood)
    pair.seats.clear();
    assert!(pair.offer(&site_two, a.0 - a.2 / 2.0 - 25.0, 400.0, Some(&keep)));
    // a move that would break the growth's distance is refused
    let mut again = Seating::default();
    assert!(again.offer(&site_two, 300.0, 400.0, None));
    let strict = Keep {
        from: ((300.0, 400.0), (2000.0, 2000.0, 2000.0, 2000.0)),
        gap: 1.0,
        standing: vec![],
        others: 1.0,
        tight: None,
    };
    again.seats.clear();
    assert!(!again.offer(&site_two, a.0 - a.2 / 2.0 - 25.0, 400.0, Some(&strict)));
    // a lot whose fixture finds no seat is unlaid on every side
    let unlaid = Lots::deal(4, 2, 0.0, &[(Kind::Retirement, 1.0)]);
    let nowhere = Forms {
        retirement_gaps: vec![],
        ..Forms::default()
    };
    let site_unlaid = Site {
        lots: &unlaid,
        forms: &nowhere,
        ..site
    };
    assert!(!Seating::default().offer(&site_unlaid, 300.0, 250.0, None));
    // a reach that no yard touches: the seat is refused, and the first house's grid offers nothing
    let mut walled = Ground::new((0.0, 0.0), canvas, &mut t);
    walled.fill_ring(
        &[(0.0, 0.0), (600.0, 0.0), (600.0, 40.0), (0.0, 40.0)],
        &mut t,
    );
    walled.fill_ring(
        &[(40.0, 40.0), (600.0, 40.0), (600.0, 600.0), (40.0, 600.0)],
        &mut t,
    );
    let pocket = walled.reach(&[(10.0, 10.0)], &mut t);
    let open = Ground::new((0.0, 0.0), canvas, &mut t);
    let site_far = Site {
        ground: &open,
        reach: &pocket,
        ..site
    };
    assert!(!Seating::default().offer(&site_far, 300.0, 250.0, None));
    assert!(grow(&site_far, (300.0, 300.0), 1).seated.is_empty());
    // a window smaller than the canvas: its first house's grid asks past the window of the window's owner
    let small = Ground::new((0.0, 0.0), (300.0, 300.0), &mut t);
    let small_reach = small.reach(&[(150.0, 150.0)], &mut t);
    let site_small = Site {
        ground: &small,
        reach: &small_reach,
        ..site
    };
    assert!(grow(&site_small, (150.0, 150.0), 1).seated.len() <= 1);
    // a ground that holds a few: the growth widens past its table and stops when no new seat is queued
    let many = Lots::deal(4, 30, 0.0, &[]);
    let site_many = Site {
        lots: &many,
        ..site
    };
    let st = grow(&site_many, (300.0, 300.0), 30);
    assert!(!st.seated.is_empty() && st.seated.len() < 30);
}

/// Do two boxes stand apart on one axis at least?
fn apart(a: (f64, f64, f64, f64), b: (f64, f64, f64, f64)) -> bool {
    let dx = (a.0 - b.0).abs() >= (a.2 + b.2) / 2.0 - 1e-6;
    let dy = (a.1 - b.1).abs() >= (a.3 + b.3) / 2.0 - 1e-6;
    dx || dy
}

#[test]
fn a_homestead_may_not_stand_its_parts_over_a_neighbors_wood() {
    let mut t = Counts::default();
    let canvas = (1200.0, 1200.0);
    let ground = Ground::new((0.0, 0.0), canvas, &mut t);
    let reach = ground.reach(&[(600.0, 600.0)], &mut t);
    let margin = Margin::new(
        &[
            (0.0, 1190.0),
            (1200.0, 1190.0),
            (1200.0, 1200.0),
            (0.0, 1200.0),
        ],
        0.0,
        &mut t,
    );
    let forms = Forms::default();
    let lots = Lots::deal(4, 2, 0.0, &[]);
    let beyond = |_p: (f64, f64)| true;
    assert!(beyond((0.0, 0.0)));
    let field = [
        (0.0, 1190.0),
        (1200.0, 1190.0),
        (1200.0, 1200.0),
        (0.0, 1200.0),
    ];
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
        rules: &Rules::default(),
    };
    let mut st = Seating::default();
    assert!(st.offer(&site, 600.0, 600.0, None));
    // a seat whose house would stand on the first homestead's wood, behind it to the north
    let h = st.seated[0].bundle.house;
    let seat = st.seated[0]
        .wood
        .iter()
        .copied()
        .max_by(|p, q| ((p.0 - h.0) + (h.1 - p.1)).total_cmp(&((q.0 - h.0) + (h.1 - q.1))))
        .unwrap_or((0.0, 0.0));
    assert!(!st.offer(&site, seat.0, seat.1, None));
    assert!(
        !apart((0.0, 0.0, 2.0, 2.0), (1.0, 1.0, 2.0, 2.0))
            && apart((0.0, 0.0, 2.0, 2.0), (0.0, 5.0, 2.0, 2.0))
    );
}

#[test]
fn a_homesteads_copse_keeps_off_its_retirement_house_and_well_and_not_its_other_fixtures() {
    use super::bundle::Bundle;
    use super::wood::{in_keepouts, WELL_KEEPOUT_FT};
    let b = Bundle {
        house: (0.0, 0.0, 46.0, 28.0),
        yard: (0.0, 40.0, 30.0, 20.0),
        fixtures: vec![
            (Kind::Retirement, (-200.0, 0.0, 20.0, 16.0)),
            (Kind::Privy, (200.0, 0.0, 6.0, 6.0)),
        ],
        well: Some((0.0, -300.0, 10.0, 10.0)),
        ..Bundle::default()
    };
    let own = Seating::keepouts_of(&b);
    assert!(in_keepouts((-200.0, 20.0), &own) && !in_keepouts((200.0, -20.0), &own));
    assert!(in_keepouts((0.0, -300.0 + WELL_KEEPOUT_FT - 1.0), &own));
    assert!(!in_keepouts((0.0, -300.0 + WELL_KEEPOUT_FT + 1.0), &own));
}
