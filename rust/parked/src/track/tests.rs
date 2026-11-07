//! The track stage's unit tests (feature 444 T32).
//!
//! Research:
//!     the track's tests - NONE: fixtures and assertions, deciding nothing about the place

use super::{
    brook_bounds, ford_crossing, row_reach, row_road, run_to_edge, street_runs_out, street_span,
    thread_over_the_ford, RoadSite, BEYOND_FT, FORD_LANDING_FT, ROW_FRAME_FT, VERTEX_FT,
};
use crate::counts::Counts;
use crate::field::fan::Pt;
use crate::ways::through::Fabric;

fn line(x0: f64, x1: f64, y: f64, step: f64) -> Vec<Pt> {
    let mut out = vec![(x0, y)];
    while out[out.len() - 1].0 + step <= x1 + 1e-9 {
        out.push((out[out.len() - 1].0 + step, y));
    }
    out
}

fn bare<'a>(
    none: &'a [(Vec<Pt>, bool)],
    env: &'a [Pt],
    rings: &'a [Vec<Pt>],
    lines: &'a [(Pt, Pt)],
    pts: &'a [Pt],
) -> Fabric<'a> {
    Fabric {
        steadings: none,
        envelope: env,
        crops: rings,
        wet: rings,
        paddy: rings,
        lines,
        houses: pts,
        crossing: None,
    }
}

#[test]
fn a_street_spans_its_farms_and_stops_short_of_the_brook_past_its_end_farm() {
    let mut t = Counts::default();
    let street = line(0.0, 2000.0, 500.0, 8.0);
    let farms = [
        (400.0, 560.0),
        (900.0, 440.0),
        (1300.0, 560.0),
        (1300.0, 900.0),
    ];
    // the far farm stands off its street; the others span 400 to 1300, half a frame past each end
    let (reach, pad) = row_reach(&[200.0, 240.0]);
    assert!((reach - 360.0).abs() < 1e-9 && (pad - 120.0).abs() < 1e-9);
    assert_eq!(row_reach(&[]), (1.5 * ROW_FRAME_FT, 0.5 * ROW_FRAME_FT));
    let span = street_span(&street, &farms, (reach, pad), &[], &mut t);
    assert!((span[0].0 - 280.0).abs() <= 8.0 && (span[span.len() - 1].0 - 1420.0).abs() <= 8.0);
    assert!(span
        .windows(2)
        .all(|w| w[1].0 - w[0].0 >= VERTEX_FT - 8.0 || w[1] == span[span.len() - 1]));
    // a brook across the line 40 ft past the last farm: the span ends there, no nearer than the farm itself
    let brook = [(1340.0, 0.0), (1340.0, 1000.0)];
    let short = street_span(&street, &farms, (reach, pad), &brook, &mut t);
    assert!(
        short[short.len() - 1].0 <= 1340.0 - FORD_LANDING_FT + 1e-9
            && short[short.len() - 1].0 >= 1296.0 - 1e-9
    );
    // ...and before the first: the near end drawn in
    let arc: Vec<f64> = street.iter().map(|p| p.0).collect();
    let (lo, hi) = brook_bounds(
        &street,
        &arc,
        (400.0, 1300.0),
        (280.0, 1420.0),
        &[(300.0, 0.0), (300.0, 1000.0)],
        &mut t,
    );
    assert!((lo - (300.0 + FORD_LANDING_FT)).abs() < 1e-9 && (hi - 1420.0).abs() < 1e-9);
    assert_eq!(
        brook_bounds(&street, &arc, (400.0, 1300.0), (1.0, 2.0), &[], &mut t),
        (1.0, 2.0)
    );
    // no farm near: no span; a line of one point: none
    assert!(street_span(&street, &[(0.0, 5000.0)], (reach, pad), &[], &mut t).is_empty());
    assert!(street_span(&street[..1], &farms, (reach, pad), &[], &mut t).is_empty());
}

#[test]
fn a_street_runs_on_off_the_sheet_at_both_ends_the_nearer_first() {
    let sheet = (3000.0, 2000.0);
    let (t, run) = run_to_edge((2500.0, 1000.0), (2400.0, 1000.0), sheet);
    assert!((t - 500.0).abs() < 1e-9 && (run[1].0 - (3000.0 + BEYOND_FT)).abs() < 1e-9);
    let (t, run) = run_to_edge((500.0, 300.0), (500.0, 400.0), sheet);
    assert!((t - 300.0).abs() < 1e-9 && (run[1].1 + BEYOND_FT).abs() < 1e-9);
    // a leg of no length points nowhere: no edge is met (as `run_to_edge` reads it)
    assert!(run_to_edge((10.0, 10.0), (10.0, 10.0), sheet)
        .0
        .is_infinite());
    let street = line(600.0, 2500.0, 1000.0, 50.0);
    let [a, b] = street_runs_out(&street, sheet);
    assert!(
        a.0 > b.0
            && (a.1[1].0 + BEYOND_FT).abs() < 1e-9
            && (b.1[1].0 - 3000.0 - BEYOND_FT).abs() < 1e-9
    );
}

#[test]
fn a_road_over_the_brook_crosses_at_the_ford_that_makes_the_walk_shortest() {
    let mut t = Counts::default();
    let brook = [(1000.0, 0.0), (1000.0, 2000.0)];
    let fords = [(1000.0, 200.0), (1000.0, 900.0)];
    let via = ford_crossing((500.0, 1000.0), (1500.0, 1000.0), &brook, &fords, &mut t);
    assert_eq!(
        via,
        vec![
            (1000.0 - FORD_LANDING_FT, 900.0),
            (1000.0 + FORD_LANDING_FT, 900.0)
        ]
    );
    let back = ford_crossing((1500.0, 1000.0), (500.0, 1000.0), &brook, &fords, &mut t);
    assert_eq!(back[0], (1000.0 + FORD_LANDING_FT, 900.0));
    // a run that does not cross, or no ford: none
    assert!(ford_crossing((500.0, 1000.0), (900.0, 1000.0), &brook, &fords, &mut t).is_empty());
    assert!(ford_crossing((500.0, 1000.0), (1500.0, 1000.0), &brook, &[], &mut t).is_empty());
    // threaded through no steading, the run keeps its landings; landings off any ford, threaded whole
    let (none, env, rings, lines, pts) = (vec![], vec![], vec![], vec![], vec![]);
    let f = bare(&none, &env, &rings, &lines, &pts);
    let run = thread_over_the_ford(
        &f,
        ((500.0, 1000.0), &via, (1500.0, 1000.0)),
        &fords,
        &mut t,
    );
    assert!(run.contains(&via[0]) && run.contains(&via[1]));
    let whole = thread_over_the_ford(
        &f,
        ((500.0, 1000.0), &via, (1500.0, 1000.0)),
        &[(0.0, 0.0)],
        &mut t,
    );
    assert_eq!(whole.len(), 4);
    assert_eq!(
        thread_over_the_ford(&f, ((0.0, 0.0), &[], (10.0, 0.0)), &fords, &mut t).len(),
        2
    );
}

#[test]
fn a_row_villages_road_is_its_street_run_on_at_both_ends() {
    let mut t = Counts::default();
    let (none, env, rings, lines, pts) = (vec![], vec![], vec![], vec![], vec![]);
    let f = bare(&none, &env, &rings, &lines, &pts);
    let street = line(600.0, 2500.0, 1000.0, 8.0);
    let farms = [(1000.0, 1060.0), (1600.0, 940.0), (2200.0, 1060.0)];
    let brook = [(300.0, 0.0), (300.0, 2000.0)];
    let fords = [(300.0, 1200.0)];
    let r = RoadSite {
        street: &street,
        farms: &farms,
        frames: &[200.0],
        brook: &brook,
        fords: &fords,
        sheet: (3000.0, 2000.0),
        waters: &[],
        fabric: &f,
    };
    let runs = row_road(&r, &mut t);
    assert_eq!(runs.len(), 2);
    // the east end is nearer its edge: its run first, off the sheet; the west run over the brook at its ford
    assert!(runs[0][runs[0].len() - 1].0 > 3000.0 && runs[1][runs[1].len() - 1].0 < 0.0);
    assert!(runs[1].contains(&(300.0 + FORD_LANDING_FT, 1200.0)));
    // the planned street where its farms' span is short; no street, no road
    let lone = RoadSite { farms: &[], ..r };
    assert_eq!(row_road(&lone, &mut t).len(), 2);
    let empty = RoadSite { street: &[], ..r };
    assert!(row_road(&empty, &mut t).is_empty());
}

#[test]
fn the_span_keeps_its_last_vertex_and_reads_a_point_leg_and_a_road_runs_down_off_the_sheet() {
    let mut t = Counts::default();
    // a line with a doubled point, its farms' span ending between two vertex steps: the last vertex kept
    let street = vec![
        (0.0, 0.0),
        (10.0, 0.0),
        (10.0, 0.0),
        (20.0, 0.0),
        (30.0, 0.0),
        (40.0, 0.0),
        (50.0, 0.0),
        (60.0, 0.0),
        (70.0, 0.0),
    ];
    let span = street_span(
        &street,
        &[(10.0, 5.0), (42.0, 5.0)],
        (20.0, 7.0),
        &[],
        &mut t,
    );
    assert_eq!(span, vec![(10.0, 0.0), (40.0, 0.0)]);
    // a farm beside the doubled point projects onto its leg of no length
    assert!(!street_span(&street[1..3], &[(10.0, 3.0)], (20.0, 0.0), &[], &mut t).is_empty());
    let (d, run) = run_to_edge((100.0, 1900.0), (100.0, 1800.0), (3000.0, 2000.0));
    assert!((d - 100.0).abs() < 1e-9 && run[1].1 > 2000.0);
}

#[test]
fn a_ford_lands_square_to_its_own_reach_and_a_leg_clipped_short_is_threaded_whole() {
    let mut t = Counts::default();
    // a bent brook: the ford stands on its second leg, the landings square to that leg
    let brook = [(1000.0, 0.0), (1000.0, 500.0), (1500.0, 1000.0)];
    let via = ford_crossing(
        (1000.0, 1000.0),
        (1500.0, 500.0),
        &brook,
        &[(1250.0, 750.0)],
        &mut t,
    );
    let h = FORD_LANDING_FT / std::f64::consts::SQRT_2;
    assert!(
        via.iter()
            .all(|p| ((p.0 - 1250.0).abs() - h).abs() < 1e-6
                && ((p.1 - 750.0).abs() - h).abs() < 1e-6)
    );
    // a steading over the near landing: the leg to it is routed round and ends off it, so the run is threaded whole
    let block = vec![
        (via[0].0 - 40.0, via[0].1 - 40.0),
        (via[0].0 + 40.0, via[0].1 - 40.0),
        (via[0].0 + 40.0, via[0].1 + 40.0),
        (via[0].0 - 40.0, via[0].1 + 40.0),
    ];
    let steadings = vec![(block, false)];
    let (env, rings, lines, pts) = (vec![], vec![], vec![], vec![]);
    let f = bare(&steadings, &env, &rings, &lines, &pts);
    let run = thread_over_the_ford(
        &f,
        ((1000.0, 1000.0), &via, (1500.0, 500.0)),
        &[(1250.0, 750.0)],
        &mut t,
    );
    assert!(run.len() >= 2);
}
