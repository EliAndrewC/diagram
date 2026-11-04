//! The sink's own tests (feature 444 T26): each rule the stage keeps, on a field small enough to read.
//!
//! Research:
//!     the sink's tests - NONE: fixtures and assertions; each rule's claim is at the unit it tests

#![expect(
    clippy::many_single_char_names,
    reason = "the plane geometry's own names"
)]

use super::brook::{proper_cross, Brook};
use super::crop::{meets_ellipse, off_resting, Crop};
use super::*;
use crate::course::{drawn, mouth};

fn square(x0: f64, y0: f64, x1: f64, y1: f64) -> Vec<Pt> {
    vec![(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
}

/// A field 1,600 by 1,200 ft, its collector along its foot to an outfall on the outline, the land falling south.
fn inp(pond: bool) -> SinkIn {
    SinkIn {
        pond,
        canvas: (4000.0, 4000.0),
        fall: (0.0, 1.0),
        flow_deg: 90.0,
        outline: square(1000.0, 800.0, 2600.0, 2000.0),
        drain: vec![(1100.0, 1900.0), (1600.0, 1950.0), (2000.0, 1990.0)],
        brook_w: 5.25,
        run_w: 5.5,
        resting: vec![],
        reed_ft: 44.0,
        join_trunk: 150.0,
    }
}

/// A brook down the canvas at `x`, wandering a few feet, off the canvas at both ends.
fn brook_at(x: f64) -> Vec<Pt> {
    (0..=210)
        .map(|k| (x + 3.0 * f64::from(k % 7), -10.0 + 20.0 * f64::from(k)))
        .collect()
}

fn far() -> Vec<Pt> {
    brook_at(700.0)
}

#[test]
fn a_pond_is_seated_below_the_outfall_clear_of_the_crop() {
    let s = sink(&inp(true), &mut far()).unwrap().unwrap();
    assert_eq!((s.form, s.to), ("pond", "pond"));
    let ((_, cy), rx, ry) = s.pond.unwrap();
    assert!(cy - ry >= 1990.0);
    assert!((std::f64::consts::PI * rx * ry - 0.03 * 1600.0 * 1200.0).abs() < 1.0);
    assert_eq!(s.reeds.len(), 16);
    assert_eq!(s.run.len(), 3);
    assert!(s.counts.get("candidate@pond_seat").is_some_and(|&n| n >= 1));
}

#[test]
fn a_pond_is_stepped_across_the_fall_off_a_brook_below_the_outfall() {
    let s = sink(&inp(true), &mut brook_at(2000.0)).unwrap().unwrap();
    let ((cx, _), rx, _) = s.pond.unwrap();
    assert!((cx - 2000.0).abs() > rx);
    assert!(s.counts["candidate@pond_seat"] > 1);
}

#[test]
fn no_room_for_a_pond_drains_off_the_map() {
    let mut i = inp(true);
    i.canvas = (4000.0, 2100.0);
    let s = sink(&i, &mut far()).unwrap().unwrap();
    assert_eq!(s.form, "offmap");
}

#[test]
fn no_collector_lays_nothing() {
    let mut i = inp(true);
    i.drain.clear();
    assert!(sink(&i, &mut far()).unwrap().is_none());
    i.drain = vec![(5.0, 5.0)];
    assert!(sink(&i, &mut far()).unwrap().is_none());
    assert!(heading(&[(0.0, 0.0), (0.0, 0.0)]).is_none());
}

#[test]
fn the_drain_joins_a_brook_running_on_within_reach_below_the_outfall() {
    let s = sink(&inp(false), &mut brook_at(2150.0)).unwrap().unwrap();
    assert_eq!((s.form, s.to), ("offmap", "stream"));
    let q = s.confluence.unwrap();
    assert!(q.1 >= 1990.0 + offmap::JOIN_DESCENT);
    assert!(dist(q, (2000.0, 1990.0)) <= offmap::JOIN_REACH);
}

#[test]
fn a_brook_numbered_uphill_is_read_in_its_own_order() {
    let mut b = brook_at(2150.0);
    b.reverse();
    let s = sink(&inp(false), &mut b).unwrap().unwrap();
    assert_eq!(s.to, "stream");
}

#[test]
fn a_brook_out_of_reach_sends_the_drain_off_the_map_on_a_searched_run() {
    let s = sink(&inp(false), &mut far()).unwrap().unwrap();
    assert_eq!((s.form, s.to), ("offmap", "offmap"));
    assert_eq!(s.run.len(), 3);
    let end = s.run[2];
    assert!(end.1 > 4000.0);
    assert!(s.counts["candidate@offmap_run"] >= 1);
}

#[test]
fn a_confluence_on_a_bend_or_with_no_trunk_below_is_not_taken() {
    // a brook that bends hard just below the outfall and leaves the canvas at once
    let b: Vec<Pt> = vec![(2150.0, 1500.0), (2150.0, 2050.0), (4100.0, 2060.0)];
    let mut i = inp(false);
    i.canvas = (4000.0, 4000.0);
    let s = sink(&i, &mut b.clone()).unwrap().unwrap();
    let q = s.confluence.expect("joined below the bend");
    assert!(dist(q, (2150.0, 2050.0)) >= crate::course::BEND_WIDTHS * i.brook_w);
    i.canvas = (2200.0, 4000.0);
    let s = sink(&i, &mut b.clone()).unwrap().unwrap();
    assert!(s.confluence.is_none());
}

#[test]
fn where_every_searched_run_crosses_the_brook_the_sink_refuses() {
    // the brook across the fall just below the outfall, its every point too short a trunk to join: each searched run crosses it
    let b: Vec<Pt> = (0..=60)
        .map(|k| (-100.0 + 70.0 * f64::from(k), 2100.0 + 0.5 * f64::from(k)))
        .collect();
    let mut i = inp(false);
    i.join_trunk = 1e9;
    let e = sink(&i, &mut b.clone()).unwrap_err();
    assert!(e.0.contains("no searched run"));
}

#[test]
fn a_run_beside_the_brook_is_its_twin() {
    let mut src: Vec<Pt> = (0..=50).map(|k| (700.0, 20.0 * f64::from(k))).collect();
    let mut br = Brook::new(&mut src, (0.0, 1.0));
    let route = vec![(720.0, 100.0), (720.0, 900.0)];
    assert!(br.twin_run(&route) > brook::TWIN_RUN);
    let mut src2: Vec<Pt> = vec![(700.0, 0.0), (700.0, 1000.0)];
    let mut br = Brook::new(&mut src2, (0.0, 1.0));
    assert!(br.twin_run(&[(800.0, 0.0), (800.0, 900.0)]) < 1.0);
    assert!(br.twin_run(&[(800.0, 0.0)]) < 1.0);
}

#[test]
fn a_run_across_a_resting_basin_or_beside_its_edge_is_refused() {
    let ring = square(0.0, 0.0, 100.0, 100.0);
    let mut t = 0;
    assert!(!off_resting(
        &[(-50.0, 50.0), (150.0, 50.0)],
        &[ring.clone()],
        2.5,
        false,
        &mut t
    ));
    assert!(!off_resting(
        &[(-50.0, 101.0), (150.0, 101.0)],
        &[ring.clone()],
        2.5,
        false,
        &mut t
    ));
    assert!(off_resting(
        &[(-50.0, 110.0), (150.0, 110.0)],
        &[ring.clone()],
        2.5,
        false,
        &mut t
    ));
    assert!(off_resting(
        &[(50.0, 50.0), (50.0, 150.0), (50.0, 300.0)],
        &[ring.clone()],
        2.5,
        true,
        &mut t
    ));
    assert!(!off_resting(
        &[(50.0, 50.0), (60.0, 60.0), (70.0, 70.0)],
        &[ring],
        2.5,
        true,
        &mut t
    ));
}

#[test]
fn the_crop_tests_read_the_outline_once() {
    let mut counts = HashMap::new();
    let c = Crop::read(
        &square(0.0, 0.0, 100.0, 100.0),
        (50.0, 100.0),
        (0.0, 1.0),
        &mut counts,
    );
    assert_eq!(counts["read@outline"], 4);
    assert!((c.area - 10_000.0).abs() < 1e-9);
    let mut t = 0;
    assert!(!c.pond_clear((50.0, 50.0), 10.0, 10.0, &mut t));
    assert!(!c.pond_clear((50.0, 105.0), 10.0, 10.0, &mut t));
    assert!(c.pond_clear((50.0, 200.0), 10.0, 10.0, &mut t));
    assert!(!c.run_clear(&[(50.0, 150.0), (50.0, 120.0), (50.0, 50.0)], false, &mut t));
    assert!(!c.run_clear(&[(50.0, 150.0), (50.0, 50.0), (150.0, 50.0)], true, &mut t));
    assert!(c.run_clear(&[(50.0, 50.0), (50.0, 150.0), (50.0, 300.0)], true, &mut t));
    assert!(meets_ellipse((0.0, 0.0), (10.0, 0.0), (5.0, 1.0), 2.0, 2.0));
    assert!(!proper_cross(
        (0.0, 0.0),
        (1.0, 0.0),
        (0.0, 1.0),
        (1.0, 1.0)
    ));
}

#[test]
fn a_pond_behind_the_collector_is_reached_by_a_curve() {
    let run = pond::ditch((0.0, 0.0), (0.0, -1.0), (0.0, 300.0), (0.0, 1.0));
    assert_eq!(run.len(), 13);
    let run = pond::ditch((0.0, 0.0), (0.6, -0.8), (0.0, 300.0), (0.0, 1.0));
    assert_eq!(run.len(), 13);
    assert_eq!(
        pond::ditch((0.0, 0.0), (0.0, 1.0), (0.0, 300.0), (0.0, 1.0)).len(),
        3
    );
}

#[test]
fn the_brook_as_drawn_rounds_its_bends_on_arcs_and_a_mouth_lies_on_it() {
    let course = vec![(0.0, 0.0), (300.0, 0.0), (300.0, 300.0), (600.0, 300.0)];
    let mut t = 0;
    let d = drawn(&course, 5.25, &[], &mut t);
    assert!(d.len() > course.len() && !d.contains(&(300.0, 0.0)));
    // the first bend's arc: every point the radius from its center, 2.5 widths
    let r = crate::course::BEND_WIDTHS * 5.25;
    let c = (300.0 - r, r);
    assert!(d[1..=7].iter().all(|p| (dist(*p, c) - r).abs() < 1e-6));
    let m = mouth((300.0, 0.0), &d, &mut t);
    assert!(dist(m, (300.0, 0.0)) < r && dist(m, (300.0, 0.0)) > 0.0);
    assert_eq!(drawn(&course[..2], 5.25, &[], &mut t).len(), 2);
    let repeated = vec![(0.0, 0.0), (10.0, 0.0), (10.0, 0.0), (20.0, 5.0)];
    assert_eq!(drawn(&repeated, 3.0, &[], &mut t).len(), 2);
    assert_eq!(
        drawn(&[(0.0, 0.0), (10.0, 0.0), (20.0, 0.5)], 3.0, &[], &mut t).len(),
        3
    );
    // a hairpin's tangent capped at half its legs
    let pin = drawn(&[(0.0, 0.0), (100.0, 0.0), (0.0, 10.0)], 50.0, &[], &mut t);
    assert!(drawn(&course, 5.25, &[(300.0, 0.5)], &mut t).contains(&(300.0, 0.0)));
    assert!(pin[1..pin.len() - 1].iter().all(|p| p.0 >= 45.0));
}

#[test]
fn a_refusal_names_itself() {
    assert_eq!(SinkRefused("no route".to_owned()).to_string(), "no route");
    let mut counts = HashMap::new();
    tally(&mut counts, "x", 0);
    assert!(counts.is_empty());
}

/// A collector whose outfall heads up the page: every searched run turns past 55 degrees or climbs, so no run keeps every rule.
fn uphill() -> SinkIn {
    let mut i = inp(false);
    i.drain = vec![(2000.0, 1990.0), (2000.0, 1900.0)];
    i
}

#[test]
fn with_no_brook_the_sink_still_lays_its_pond_or_its_run() {
    assert_eq!(
        sink(&inp(true), &mut Vec::new()).unwrap().unwrap().form,
        "pond"
    );
    assert!(sink(&uphill(), &mut Vec::new()).is_err());
    let mut none: Vec<Pt> = Vec::new();
    let mut br = Brook::new(&mut none, (0.0, 1.0));
    assert!(!br.crossed(&[(0.0, 0.0), (1.0, 1.0)], 5.0) && br.span(0.0, 1.0).is_empty());
}

#[test]
fn a_confluence_whose_run_crosses_a_resting_basin_is_not_taken() {
    let mut i = inp(false);
    i.resting = vec![square(2040.0, 1992.0, 2400.0, 2300.0)];
    let s = sink(&i, &mut brook_at(2150.0)).unwrap().unwrap();
    assert!(s.confluence.is_none());
}

#[test]
fn a_pond_whose_seat_meets_the_crop_steps_on() {
    let mut i = inp(true);
    i.drain = vec![(1100.0, 1600.0), (2000.0, 1700.0)];
    let s = sink(&i, &mut far()).unwrap().unwrap();
    assert!(s.counts["candidate@pond_seat"] > 1);
}

#[test]
fn the_brook_reads_repeated_stations_and_runs_ending_on_it() {
    let mut src: Vec<Pt> = vec![
        (700.0, 0.0),
        (700.0, 500.0),
        (700.0, 500.0),
        (700.0, 1000.0),
    ];
    let mut br = Brook::new(&mut src, (0.0, 1.0));
    assert!(!br.crossed(&[(700.0, 300.0), (800.0, 300.0)], 5.25));
    assert!(br.twin_run(&[(720.0, 100.0), (720.0, 100.0), (720.0, 900.0)]) > brook::TWIN_RUN);
    let c = Crop::read(
        &square(0.0, 0.0, 100.0, 100.0),
        (50.0, 100.0),
        (0.0, 1.0),
        &mut HashMap::new(),
    );
    assert!(!c.run_clear(&[(50.0, 50.0), (60.0, 60.0), (70.0, 70.0)], true, &mut 0));
    let mut i = inp(false);
    let mut rep = brook_at(2150.0);
    rep.insert(105, rep[105]);
    i.canvas = (4000.0, 4000.0);
    assert_eq!(sink(&i, &mut rep).unwrap().unwrap().to, "stream");
}

#[test]
fn a_run_is_measured_on_the_canvas() {
    assert!(offmap::on_canvas((-10.0, 5.0), (-10.0, 50.0), (100.0, 100.0)) < 1e-9);
    assert!((offmap::on_canvas((50.0, 50.0), (150.0, 50.0), (100.0, 100.0)) - 50.0).abs() < 1e-9);
}

#[test]
fn a_field_whose_land_falls_north_drains_up_the_page() {
    let mut i = inp(false);
    i.fall = (0.0, -1.0);
    i.flow_deg = 270.0;
    i.drain = vec![(1100.0, 900.0), (1600.0, 850.0), (2000.0, 810.0)];
    let s = sink(&i, &mut Vec::new()).unwrap().unwrap();
    assert!(s.run[s.run.len() - 1].1 < 0.0);
    i.drain = vec![(2000.0, 810.0), (2000.0, 900.0)];
    assert!(
        sink(&i, &mut Vec::new()).is_err(),
        "a collector heading against the fall has no searched run"
    );
    i.fall = (-1.0, 0.0);
    i.flow_deg = 180.0;
    i.drain = vec![(1100.0, 1100.0), (1050.0, 1500.0), (1010.0, 1900.0)];
    assert!(sink(&i, &mut Vec::new()).unwrap().unwrap().run.len() >= 3);
}

#[test]
fn a_run_ending_on_the_brook_is_no_twin_near_its_mouth() {
    let mut src: Vec<Pt> = (0..=50).map(|k| (700.0, 20.0 * f64::from(k))).collect();
    let mut br = Brook::new(&mut src, (0.0, 1.0));
    assert!(br.twin_run(&[(720.0, 100.0), (720.0, 900.0), (700.0, 950.0)]) > brook::TWIN_RUN);
}

#[test]
fn a_crossing_at_the_runs_own_mouth_is_its_junction_and_a_twin_reads_the_brooks_own_order() {
    let mut src: Vec<Pt> = (0..=50).map(|k| (700.0, 20.0 * f64::from(k))).collect();
    let mut br = Brook::new(&mut src, (0.0, 1.0));
    assert!(!br.crossed(&[(600.0, 310.0), (701.0, 310.0)], 5.25));
    assert!(br.crossed(&[(600.0, 310.0), (800.0, 310.0)], 5.25));
    assert!(br.twin_run(&[(720.0, 900.0), (720.0, 100.0)]) < 1.0);
    let mut up: Vec<Pt> = (0..=50)
        .rev()
        .map(|k| (700.0, 20.0 * f64::from(k)))
        .collect();
    let mut br = Brook::new(&mut up, (0.0, 1.0));
    assert!(br.twin_run(&[(720.0, 100.0), (720.0, 900.0)]) > brook::TWIN_RUN);
}

#[test]
fn a_collector_heading_up_the_fall_from_outside_the_field_is_refused() {
    let mut i = uphill();
    i.drain = vec![(3200.0, 2200.0), (3200.0, 2100.0)];
    let e = sink(&i, &mut Vec::new()).unwrap_err();
    assert!(e.0.contains("no searched run"));
}

#[test]
fn the_outfall_is_found_in_the_field_from_its_low_segments_alone() {
    let ring = vec![
        (0.0, 0.0),
        (100.0, 0.0),
        (100.0, 80.0),
        (60.0, 100.0),
        (0.0, 80.0),
    ];
    let c = Crop::read(&ring, (50.0, 90.0), (0.0, 1.0), &mut HashMap::new());
    let mut t = 0;
    for p in [
        (50.0, 90.0),
        (50.0, 99.0),
        (90.0, 70.0),
        (50.0, 110.0),
        (150.0, 90.0),
    ] {
        assert_eq!(c.holds_low(p, &mut t), c.holds(p, &mut t));
    }
}
