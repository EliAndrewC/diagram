//! The connector's thread's unit tests (feature 444 T30).
//!
//! Research:
//!     the thread's tests - NONE: fixtures and assertions, deciding nothing about the place

#![expect(clippy::many_single_char_names, reason = "the tests' own short names")]

use super::dry_exit::DrySite;
use super::through::{
    connector_through, connector_ways, inner, out_of_bands, push_clear_of_fabric, route_around,
    thread_the_fabric, water_crossings, Fabric, Law,
};
use super::track::{poly_box, segments_cross};
use super::Counts;
use crate::field::fan::Pt;

fn square(x0: f64, y0: f64, x1: f64, y1: f64) -> Vec<Pt> {
    vec![(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
}

fn crosses(path: &[Pt], ring: &[Pt]) -> bool {
    path.windows(2).any(|w| {
        (0..ring.len()).any(|k| segments_cross(w[0], w[1], ring[k], ring[(k + 1) % ring.len()]))
    })
}

#[test]
fn a_track_across_the_field_walks_round_its_outline() {
    let mut t = Counts::default();
    let field = square(0.0, 0.0, 100.0, 100.0);
    let r = route_around(&field, &[(-50.0, 40.0), (150.0, 60.0)], 17.0, &mut t).expect("round it");
    assert!(!crosses(&r, &field) && r.len() > 2);
    // clear already: as it was
    let c = route_around(&field, &[(-50.0, -50.0), (150.0, -50.0)], 17.0, &mut t).expect("clear");
    assert_eq!(c.len(), 2);
    // a leg from one edge of the outline to the other crosses it once, stepped there round after round: none
    let one = route_around(
        &square(0.0, 0.0, 10.0, 10.0),
        &[(5.0, 10.0), (5.0, 0.0)],
        0.0,
        &mut t,
    );
    assert!(one.is_none());
    // the way round itself pulled in: no round converges
    assert!(route_around(&field, &[(-50.0, 40.0), (150.0, 60.0)], -5.0, &mut t).is_none());
    // either way round: the shorter one taken
    let left = route_around(&field, &[(40.0, -50.0), (60.0, 150.0)], 17.0, &mut t).expect("round");
    assert!(!crosses(&left, &field));
}

#[test]
fn the_ends_and_the_measures_the_thread_reads() {
    let mut t = Counts::default();
    let s = square(0.0, 0.0, 20.0, 20.0);
    let fab = [(s.clone(), poly_box(&s))];
    assert_eq!(
        push_clear_of_fabric((50.0, 10.0), (1.0, 0.0), 0.0, &fab, 7.0, &mut t),
        (50.0, 10.0)
    );
    let p = push_clear_of_fabric((15.0, 10.0), (1.0, 0.0), 0.0, &fab, 7.0, &mut t);
    assert!((p.0 - 27.0).abs() < 1e-9);
    let big = square(-10.0, -3.0, 1000.0, 3.0);
    let walled = [(big.clone(), poly_box(&big))];
    assert!(
        (push_clear_of_fabric((0.0, 0.0), (1.0, 0.0), 0.0, &walled, 7.0, &mut t).0 - 144.0).abs()
            < 1e-9
    );
    // a band end walked out toward the far end, or pushed past its nearest edge
    let band = vec![square(0.0, 0.0, 100.0, 100.0)];
    assert_eq!(
        out_of_bands((200.0, 50.0), &band, (0.0, 0.0)),
        (200.0, 50.0)
    );
    let w = out_of_bands((50.0, 90.0), &band, (50.0, 300.0));
    assert!(w.1 > 100.0 && w.1 < 115.0);
    let n = out_of_bands((50.0, 95.0), &band, (50.0, 96.0));
    assert!((n.1 - 108.0).abs() < 1e-9);
    assert_eq!(
        water_crossings(&[(0.0, 0.0), (10.0, 0.0)], &[((5.0, -1.0), (5.0, 1.0))]),
        1
    );
    assert_eq!(
        inner(&[(0.0, 0.0), (10.0, 0.0)]),
        vec![(3.0, 0.0), (7.0, 0.0)]
    );
    assert_eq!(
        inner(&[(0.0, 0.0), (5.0, 0.0)]),
        vec![(0.0, 0.0), (5.0, 0.0)]
    );
}

fn fabric<'a>(
    steadings: &'a [(Vec<Pt>, bool)],
    envelope: &'a [Pt],
    houses: &'a [Pt],
) -> Fabric<'a> {
    Fabric {
        steadings,
        envelope,
        crops: &[],
        wet: &[],
        paddy: &[],
        lines: &[],
        houses,
        crossing: None,
    }
}

#[test]
fn the_thread_routes_round_the_steadings_swings_or_takes_the_bands_fallbacks() {
    let mut t = Counts::default();
    let env = square(5000.0, 5000.0, 5100.0, 5100.0);
    let houses = [(100.0, 100.0)];
    // nothing standing: the run as it is; a run of one point as it is
    assert_eq!(
        thread_the_fabric(
            &fabric(&[], &env, &houses),
            &[(0.0, 0.0), (10.0, 0.0)],
            &mut t
        )
        .len(),
        2
    );
    let one = [(square(0.0, 0.0, 1.0, 1.0), false)];
    assert_eq!(
        thread_the_fabric(&fabric(&one, &env, &houses), &[(0.0, 0.0)], &mut t).len(),
        1
    );
    // a steading on the line: routed round it
    let st = [(square(90.0, -20.0, 110.0, 20.0), false)];
    let r = thread_the_fabric(
        &fabric(&st, &env, &houses),
        &[(0.0, 0.0), (200.0, 0.0)],
        &mut t,
    );
    assert!(r.len() >= 3 && !crosses(&r, &st[0].0));
    // too long to route: clipped clear where nothing it crosses is held
    let long = thread_the_fabric(
        &fabric(&st, &env, &houses),
        &[(0.0, 300.0), (3000.0, 300.0)],
        &mut t,
    );
    assert_eq!(long.len(), 2);
    // too long to route and ending in a steading: the swing is tried, then nothing
    let wall = [(square(2900.0, -2000.0, 2950.0, 2000.0), false)];
    let none = thread_the_fabric(
        &fabric(&wall, &env, &houses),
        &[(0.0, 0.0), (3000.0, 0.0)],
        &mut t,
    );
    assert!(none.last().is_some_and(|p| p.0 < 2900.0));
    // a short run through a wall the router cannot pass: swung out from the cluster
    let blocker = [(square(40.0, -30.0, 60.0, 30.0), false)];
    let shut: Vec<Pt> = square(-200.0, 35.0, 300.0, 400.0);
    let walled = Fabric {
        wet: std::slice::from_ref(&shut),
        ..fabric(&blocker, &env, &[(50.0, 100.0)])
    };
    let sw = thread_the_fabric(&walled, &[(0.0, 0.0), (100.0, 0.0)], &mut t);
    assert!(sw.is_empty() || !crosses(&sw, &blocker[0].0));
    // a run across a grove band: routed round the bands
    let band = [(square(80.0, -40.0, 120.0, 40.0), true)];
    let g = thread_the_fabric(
        &fabric(&band, &env, &[(100.0, -500.0)]),
        &[(100.0, 0.0), (100.0, 600.0)],
        &mut t,
    );
    assert!(g.is_empty() || !crosses(&g, &band[0].0));
}

#[test]
fn the_connector_is_threaded_or_takes_the_dry_exit_and_a_seat_last() {
    let mut t = Counts::default();
    let env = square(0.0, 600.0, 1000.0, 1000.0);
    let houses = [(500.0, 500.0)];
    let st = [(square(480.0, 300.0, 520.0, 340.0), false)];
    let f = fabric(&st, &env, &houses);
    let law = Law {
        solid: &[],
        forbidding: &[],
        seats: &[],
        brooks: &[],
        waters: &[],
    };
    let dry = DrySite {
        wet: &[],
        fabric: &[],
        avoid: &[],
        pond: None,
        lines: &[],
        course: &[],
        canvas: (1000.0, 1000.0),
    };
    // north past the steading, threaded and lawful
    let (run, seats) =
        connector_through(&[(500.0, 500.0), (500.0, -400.0)], &f, &law, &dry, &mut t)
            .expect("a way");
    assert!(!seats && run.len() >= 2);
    // across a building's box: the dry exit
    let solid = [(400.0, -500.0, 600.0, 450.0)];
    let walled = Law {
        solid: &solid,
        ..law
    };
    let (d, _) = connector_through(
        &[(500.0, 500.0), (500.0, -400.0)],
        &fabric(&[], &env, &houses),
        &walled,
        &dry,
        &mut t,
    )
    .expect("dry");
    assert!(d.len() >= 2);
    // a reserved seat on the only way out: taken
    let ring = [
        square(-100.0, -100.0, 1100.0, 450.0),
        square(-100.0, 550.0, 1100.0, 1100.0),
        square(-100.0, 450.0, 450.0, 550.0),
    ];
    let seat = [square(900.0, 450.0, 1100.0, 550.0)];
    let walls = DrySite {
        avoid: &ring,
        ..dry
    };
    let far = square(5000.0, 5000.0, 5010.0, 5010.0);
    let forbidding = [(far.clone(), poly_box(&far))];
    let seated = Law {
        solid: &solid,
        seats: &seat,
        forbidding: &forbidding,
        ..law
    };
    let (_, taken) = connector_through(
        &[(500.0, 500.0), (500.0, -400.0)],
        &fabric(&[], &env, &houses),
        &seated,
        &walls,
        &mut t,
    )
    .expect("over the seat");
    assert!(taken);
    // walled in on every side: none
    let shut = [square(-200.0, -200.0, 1200.0, 1200.0)];
    let closed = DrySite { wet: &shut, ..dry };
    assert!(connector_through(
        &[(500.0, 500.0), (500.0, -400.0)],
        &fabric(&[], &env, &houses),
        &walled,
        &closed,
        &mut t
    )
    .is_none());
    // a threaded run that stops short of its far end: the dry exit
    let wall = [(square(-2000.0, 100.0, 3000.0, 140.0), false)];
    let short = connector_through(
        &[(500.0, 500.0), (500.0, -400.0)],
        &fabric(&wall, &env, &houses),
        &law,
        &dry,
        &mut t,
    );
    assert!(short.is_some());
}

#[test]
fn the_thread_falls_back_to_the_swing_and_the_band_routes() {
    let mut t = Counts::default();
    let env = square(5000.0, 5000.0, 5100.0, 5100.0);
    // too long to route, a steading by the start: the clip too short, the swing at 220 ft clears it
    let peg = [(square(45.0, -5.0, 55.0, 5.0), false)];
    let sw = thread_the_fabric(
        &fabric(&peg, &env, &[(800.0, -100.0)]),
        &[(0.0, 0.0), (1600.0, 0.0)],
        &mut t,
    );
    assert_eq!(sw.len(), 3);
    assert!(sw[1].1 > 200.0);
    // a run held by the paddy and walled from every swing: nothing, the kept run the clip
    let wall = [(square(2900.0, -2000.0, 2950.0, 2000.0), false)];
    let paddy = [square(100.0, -3000.0, 120.0, 3000.0)];
    let held = Fabric {
        paddy: &paddy,
        ..fabric(&wall, &env, &[(1500.0, -100.0)])
    };
    assert!(thread_the_fabric(&held, &[(0.0, 0.0), (3000.0, 0.0)], &mut t).is_empty());
    // across a grove band by the start, the crop leaving too little room for the first route: round the band alone
    let band = [(square(30.0, -60.0, 50.0, 60.0), true)];
    let crops = [
        square(-200.0, 80.0, 500.0, 300.0),
        square(-200.0, -300.0, 500.0, -80.0),
    ];
    let roomy = Fabric {
        crops: &crops,
        ..fabric(&band, &env, &[(150.0, -100.0)])
    };
    let around = thread_the_fabric(&roomy, &[(0.0, 0.0), (300.0, 0.0)], &mut t);
    assert!(around.len() >= 3 && !crosses(&around, &band[0].0));
    // and with the crop closer and a paddy on the far part: nothing
    let tight = [
        square(-200.0, 72.0, 500.0, 300.0),
        square(-200.0, -300.0, 500.0, -72.0),
    ];
    let plot = [square(200.0, -10.0, 220.0, 10.0)];
    let closed = Fabric {
        crops: &tight,
        paddy: &plot,
        ..fabric(&band, &env, &[(150.0, -100.0)])
    };
    assert!(thread_the_fabric(&closed, &[(0.0, 0.0), (300.0, 0.0)], &mut t).is_empty());
}

#[test]
fn a_dry_exit_squared_across_a_band_is_walled_past_its_reach_or_kept_as_the_fallback() {
    let mut t = Counts::default();
    let env = square(0.0, 600.0, 1000.0, 1000.0);
    let houses = [(500.0, 500.0)];
    let track = [(500.0, 300.0), (500.0, -400.0)];
    // a building's box over the track: the threaded run is not lawful, so the dry exit is asked
    let solid = [(400.0, -500.0, 600.0, 450.0)];
    let law = Law {
        solid: &solid,
        forbidding: &[],
        seats: &[],
        brooks: &[],
        waters: &[],
    };
    // the dry exit skirts its band at the band's gap, which is inside the wider band the run is held off
    let near = [(square(350.0, 150.0, 650.0, 170.0), true)];
    let wider = [(square(335.0, 135.0, 665.0, 185.0), true)];
    let dry = DrySite {
        wet: &[],
        fabric: &near,
        avoid: &[],
        pond: None,
        lines: &[],
        course: &[],
        canvas: (1000.0, 1000.0),
    };
    let (held, _) = connector_ways(&track, &fabric(&wider, &env, &houses), &law, &dry, &mut t);
    let (run, _) = held.expect("walled past the band's reach");
    assert!(!run
        .iter()
        .any(|p| (335.0..=665.0).contains(&p.0) && (135.0..=185.0).contains(&p.1)));
    // a band right across the sheet and far past it, which the dry exit does not know: no way held, the first that cuts it kept
    let across = [(square(-20000.0, 150.0, 20000.0, 170.0), true)];
    let blind = DrySite { fabric: &[], ..dry };
    let (none, cut) = connector_ways(
        &track,
        &fabric(&across, &env, &houses),
        &law,
        &blind,
        &mut t,
    );
    assert!(none.is_none() && cut.is_some());
    // the start boxed in by bands but for a gap wide enough for the dry exit at the band's gap, closed once the bands are grown
    // past a squared leg's reach: the widened search finds no way out, and the first way that cuts the band is kept
    let pair = [
        (square(380.0, 200.0, 480.0, 220.0), true),
        (square(520.0, 200.0, 620.0, 220.0), true),
        (square(380.0, 380.0, 620.0, 400.0), true),
        (square(380.0, 200.0, 400.0, 400.0), true),
        (square(600.0, 200.0, 620.0, 400.0), true),
    ];
    let gapped = DrySite {
        fabric: &pair,
        ..dry
    };
    let (held, kept) = connector_ways(
        &track,
        &fabric(&across, &env, &houses),
        &law,
        &gapped,
        &mut t,
    );
    assert!(held.is_none() && kept.is_some());
    // the wood seats walling the near edge: walled by them the dry exit cuts a band to north or south, and over them it leaves
    // west, off every band - kept, the first cut kept beside it
    let west = [(150.0, 500.0), (150.0, -400.0)];
    let solid_w = [(100.0, -500.0, 200.0, 550.0)];
    let seats = [square(-100.0, -100.0, 140.0, 1100.0)];
    let walled_w = Law {
        solid: &solid_w,
        seats: &seats,
        ..law
    };
    let rows = [
        (square(-20000.0, 100.0, 20000.0, 120.0), true),
        (square(-20000.0, 880.0, 20000.0, 900.0), true),
    ];
    let open_dry = DrySite { fabric: &[], ..dry };
    let (over, first) = connector_ways(
        &west,
        &fabric(&rows, &env, &houses),
        &walled_w,
        &open_dry,
        &mut t,
    );
    assert!(over.is_some_and(|(_, taken)| taken) && first.is_some());
}
