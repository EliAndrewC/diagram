//! The row village's street geometry: its unit tests, against the values `rows.py` gives with shapely (feature 444 T30).
//!
//! Research:
//!     the row geometry's tests - NONE: fixtures and assertions, deciding nothing about the place

use super::level::Hard;
use super::rows::{
    best_row_line, clip_to, door_clear, frame_extent, frame_refused, holding_clear, holding_quad,
    inside_the_sheet, offset_curve, parallel, polys_meet, ring_near, row_offsets, row_seats,
    street_bend_radius_ft, street_on, Form, Frames,
};
use super::Counts;
use crate::field::fan::Pt;
use crate::field::geom::{dist, seg_dist};

fn hard(t: &mut Counts) -> Hard {
    let field = vec![
        (200.0, 1500.0),
        (2200.0, 1500.0),
        (2200.0, 2300.0),
        (200.0, 2300.0),
    ];
    let pond = vec![
        (2600.0, 600.0),
        (2800.0, 600.0),
        (2800.0, 800.0),
        (2600.0, 800.0),
    ];
    Hard::new(
        &[field, pond],
        &[((1000.0, 1100.0), (1000.0, 1490.0), 8.0)],
        t,
    )
}

fn near(p: Pt, q: Pt, tol: f64) -> bool {
    dist(p, q) <= tol
}

#[test]
fn a_street_runs_off_the_hard_ground_as_shapely_draws_it() {
    let mut t = Counts::default();
    let h = hard(&mut t);
    let anchor = (1200.0, 1250.0);
    let ring = ring_near(&h, anchor, 60.0, &mut t).expect("a ring");
    // the dry edge, 450 ft with its slack, round the brook's clearance: (1103, 1440) facing north to (1030.6, 1039.3)
    let edge = street_on(&ring, &h, anchor, 400.0, Form::Edge, 50.0, &mut t);
    assert_eq!(edge.len(), 57);
    assert!(near(edge[0].0, (1103.0, 1440.0), 2.0) && near(edge[0].1, (0.0, -1.0), 0.05));
    assert!(near(edge[28].0, (1068.0, 1250.0), 2.0));
    assert!(near(edge[56].0, (1030.615, 1039.342), 2.0) && near(edge[56].1, (0.505, -0.863), 0.1));
    // a street laid first: straight, set out past the stretch
    let street = street_on(&ring, &h, anchor, 400.0, Form::Street, 50.0, &mut t);
    assert_eq!(street.len(), 57);
    assert!(near(street[0].0, (1071.437, 1024.854), 2.0) && near(street[0].1, (1.0, -0.016), 0.02));
    assert!(near(street[56].0, (1078.55, 1474.798), 2.0));
    assert!(street_on(&ring, &h, anchor, 0.0, Form::Street, 0.0, &mut t).is_empty());
    assert!(ring_near(&Hard::new(&[], &[], &mut t), anchor, 60.0, &mut t).is_none());
}

#[test]
fn the_seats_and_offsets_are_pythons() {
    let mut t = Counts::default();
    let h = hard(&mut t);
    let anchor = (1200.0, 1250.0);
    let ring = ring_near(&h, anchor, 60.0, &mut t).expect("a ring");
    let line = street_on(&ring, &h, anchor, 400.0, Form::Street, 0.0, &mut t);
    let seats = row_seats(&line, (0.0, 5.0, 120.0, 90.0), true, 15.0, 100.0);
    let want = [
        (1150.688, 1248.63, 1),
        (999.299, 1251.023, -1),
        (1152.269, 1348.617, 1),
        (1000.88, 1351.01, -1),
        (1149.107, 1148.642, 1),
        (997.718, 1151.035, -1),
    ];
    for (s, w) in seats.iter().zip(want) {
        assert!(near(s.0, (w.0, w.1), 2.5) && s.1 == w.2);
    }
    assert_eq!(
        row_seats(&line, (0.0, 5.0, 120.0, 90.0), false, 15.0, f64::INFINITY).len(),
        3
    );
    assert!(row_seats(&line[..1], (0.0, 5.0, 120.0, 90.0), false, 15.0, 100.0).is_empty());
    assert_eq!(
        row_offsets(90.0, true, 3, 24.0, 15.0, 315.0),
        vec![129.0, 678.0, 1227.0]
    );
    assert_eq!(
        row_offsets(90.0, false, 2, 24.0, 15.0, 0.0),
        vec![24.0, 168.0]
    );
    assert!((frame_extent((0.0, 0.0, 120.0, 90.0), (0.6, 0.8)) - 144.0).abs() < 1e-9);
    assert!((street_bend_radius_ft() - 91.67).abs() < 0.01);
}

/// The least and most distance from a line's samples to the polyline `base`.
fn spread(line: &[(Pt, Pt)], base: &[Pt]) -> (f64, f64) {
    line.iter()
        .map(|&(p, _)| {
            base.windows(2)
                .map(|w| seg_dist(p, w[0], w[1]))
                .fold(f64::INFINITY, f64::min)
        })
        .fold((f64::INFINITY, 0.0), |m, d| (m.0.min(d), m.1.max(d)))
}

#[test]
fn a_further_street_is_a_true_parallel_rounded_at_its_corners() {
    let mut t = Counts::default();
    let h = hard(&mut t);
    let anchor = (1200.0, 1250.0);
    let ring = ring_near(&h, anchor, 60.0, &mut t).expect("a ring");
    // straight: the whole line set out 300 ft along its normal (shapely split it, and Python kept a part 8 ft short at its far end)
    let line = street_on(&ring, &h, anchor, 400.0, Form::Street, 0.0, &mut t);
    let par = parallel(&line, 300.0, street_bend_radius_ft(), &mut t);
    let base: Vec<Pt> = line.iter().map(|s| s.0).collect();
    let (lo, hi) = spread(&par, &base);
    assert!(lo > 299.0 && hi < 301.0);
    assert!(
        near(par[0].0, (1371.795, 1045.109), 1.0)
            && near(par[par.len() - 1].0, (1378.1, 1445.06), 1.0)
    );
    assert!(par.iter().all(|(_, n)| near(*n, line[0].1, 0.02)));
    // round the field's corner: never nearer the first street than 300 ft, its turns no sharper than the lane law's
    let edge = street_on(&ring, &h, anchor, 900.0, Form::Edge, 0.0, &mut t);
    let bent = parallel(&edge, 300.0, street_bend_radius_ft(), &mut t);
    let base: Vec<Pt> = edge.iter().map(|s| s.0).collect();
    let (lo, _) = spread(&bent, &base);
    assert!(lo > 298.0 && bent.len() > 100, "{lo} {}", bent.len());
    let turn = bent.windows(3).map(|w| {
        let (a, b) = (
            (w[1].0 .0 - w[0].0 .0, w[1].0 .1 - w[0].0 .1),
            (w[2].0 .0 - w[1].0 .0, w[2].0 .1 - w[1].0 .1),
        );
        (a.0 * b.1 - a.1 * b.0)
            .atan2(a.0 * b.0 + a.1 * b.1)
            .to_degrees()
            .abs()
    });
    assert!(turn.fold(0.0, f64::max) < 30.0);
    // set out nothing, or from a single sample: moved along its normals
    assert_eq!(
        parallel(&line[..1], 10.0, 0.0, &mut t)[0].0,
        (
            line[0].0 .0 + line[0].1 .0 * 10.0,
            line[0].0 .1 + line[0].1 .1 * 10.0
        )
    );
    assert_eq!(parallel(&line, 0.0, 0.0, &mut t).len(), line.len());
    // set inside a U wider than it is: nothing left, as shapely gives; round its outside 1,286 ft, 4 ft in a 14 ft curve resampled at the line's 10 ft to its two ends, as Python
    // a line of no length: no curve
    assert!(parallel(
        &[((1.0, 1.0), (0.0, 1.0)), ((1.0, 1.0), (0.0, 1.0))],
        5.0,
        0.0,
        &mut t
    )
    .is_empty());
    let short = vec![
        ((0.0, 0.0), (0.0, 1.0)),
        ((10.0, 0.0), (0.0, 1.0)),
        ((10.0, 10.0), (-1.0, 0.0)),
        ((0.0, 10.0), (0.0, -1.0)),
    ];
    assert!(parallel(&short, 20.0, 0.0, &mut t).is_empty());
    let len = |l: &[(Pt, Pt)]| l.windows(2).map(|w| dist(w[0].0, w[1].0)).sum::<f64>();
    assert!((len(&parallel(&short, -400.0, 0.0, &mut t)) - 1286.1).abs() < 15.0);
    let inner = parallel(&short, 4.0, 0.0, &mut t);
    assert!(
        inner.len() == 2 && near(inner[0].0, (0.0, 4.0), 0.5) && near(inner[1].0, (0.0, 6.0), 0.5)
    );
}

#[test]
fn a_holding_a_door_and_a_frame_are_judged_as_python_judges_them() {
    let mut t = Counts::default();
    let h = hard(&mut t);
    let q = holding_quad((1200.0, 1100.0), (1.0, 0.0), (0.0, -1.0), 120.0, 300.0);
    let sheet = (30.0, 30.0, 3000.0, 3000.0);
    let got = holding_clear(&q, &h, &[], sheet, &mut t).expect("clear");
    assert!([
        (1260.0, 1250.0),
        (1260.0, 950.0),
        (1140.0, 950.0),
        (1140.0, 1250.0)
    ]
    .iter()
    .all(|p| got.iter().any(|g| near(*g, *p, 1e-9))));
    assert!(holding_clear(&q, &h, &[(1200.0, 1100.0, 10.0, 10.0)], sheet, &mut t).is_none());
    let cut = holding_clear(&q, &h, &[], (30.0, 1000.0, 3000.0, 3000.0), &mut t).expect("clipped");
    assert!(cut.iter().all(|p| p.1 >= 1000.0 - 1e-9) && cut.len() == 4);
    assert!(holding_clear(&q, &h, &[], (30.0, 1240.0, 3000.0, 3000.0), &mut t).is_none());
    assert!(holding_clear(&q, &h, &[], (5000.0, 5000.0, 6000.0, 6000.0), &mut t).is_none());
    let wet = holding_quad((1000.0, 1200.0), (1.0, 0.0), (0.0, -1.0), 120.0, 100.0);
    assert!(holding_clear(&wet, &h, &[], sheet, &mut t).is_none());
    let field = holding_quad((1200.0, 1500.0), (1.0, 0.0), (0.0, -1.0), 120.0, 100.0);
    assert!(holding_clear(&field, &h, &[], sheet, &mut t).is_none());
    let round = holding_quad((2700.0, 700.0), (1.0, 0.0), (0.0, 1.0), 600.0, 600.0);
    assert!(holding_clear(&round, &h, &[], (0.0, 0.0, 5000.0, 5000.0), &mut t).is_none());
    // the door: in the clear, or on the field
    assert!(door_clear(
        (1200.0, 1400.0, 120.0, 90.0),
        (0.0, 1.0),
        16.0,
        &h,
        16.0,
        &mut t
    ));
    assert!(!door_clear(
        (1200.0, 1460.0, 120.0, 90.0),
        (0.0, 1.0),
        16.0,
        &h,
        16.0,
        &mut t
    ));
    assert!(door_clear(
        (0.0, 0.0, 10.0, 10.0),
        (0.0, 1.0),
        0.0,
        &Hard::new(&[], &[], &mut t),
        16.0,
        &mut t
    ));
    // a frame on a street, on a holding, or with no door
    let door = ((0.0, 1.0), 16.0, 16.0);
    let fr = (1200.0, 1100.0, 120.0, 90.0);
    assert!(!frame_refused(fr, door, &h, &[], &[], &mut t));
    assert!(frame_refused(
        fr,
        door,
        &h,
        &[vec![(1100.0, 1100.0), (1300.0, 1100.0)]],
        &[],
        &mut t
    ));
    assert!(frame_refused(fr, door, &h, &[], &[q.clone()], &mut t));
    assert!(frame_refused(
        (1200.0, 1460.0, 120.0, 90.0),
        door,
        &h,
        &[],
        &[],
        &mut t
    ));
    assert!(!Hard::new(&[], &[], &mut t).meets(&q, &mut t));
    assert!(!polys_meet(
        &q,
        &holding_quad((1500.0, 1100.0), (1.0, 0.0), (0.0, 1.0), 10.0, 10.0),
        &mut t
    ));
    assert_eq!(clip_to(&q, (0.0, 0.0, 10.0, 10.0)).len(), 0);
}

#[test]
fn the_sheet_keeps_the_longest_run_and_the_best_line_the_most_frames() {
    let mut t = Counts::default();
    let line: Vec<(Pt, Pt)> = [5.0, 20.0, 30.0, 200.0, 40.0, 50.0, 60.0, 70.0]
        .iter()
        .map(|&x| ((x, 0.0), (0.0, 1.0)))
        .collect();
    let run = inside_the_sheet(&line, (0.0, -1.0, 100.0, 1.0));
    assert_eq!(
        run.iter().map(|s| s.0 .0).collect::<Vec<_>>(),
        vec![40.0, 50.0, 60.0, 70.0]
    );
    assert!(inside_the_sheet(&line, (500.0, 500.0, 600.0, 600.0)).is_empty());
    let h = hard(&mut t);
    let fr = Frames {
        frame: (0.0, 5.0, 120.0, 90.0),
        both: false,
        gap: 15.0,
        bounds: (30.0, 30.0, 2970.0, 2970.0),
        door: ((0.0, 1.0), 16.0, 16.0),
        pitch: 100.0,
    };
    let best = best_row_line(
        &h,
        (1200.0, 1250.0),
        (60.0, 400.0, 100.0),
        Form::Street,
        &fr,
        &mut t,
    );
    assert_eq!(best.len(), 63);
    assert!(
        near(best[0].0, (1063.164, 974.114), 3.0) && near(best[62].0, (1082.262, 1473.749), 3.0)
    );
    assert!(best_row_line(
        &Hard::new(&[], &[], &mut t),
        (0.0, 0.0),
        (60.0, 400.0, 0.0),
        Form::Edge,
        &fr,
        &mut t
    )
    .is_empty());
}

#[test]
fn an_offset_pinched_in_two_keeps_its_longer_part() {
    let mut t = Counts::default();
    // a U whose right arm bulges within 30 ft of its left: set 20 ft inside, the curve is cut where the bulge comes near the arm
    let u = [
        (0.0, 0.0),
        (0.0, 100.0),
        (100.0, 100.0),
        (100.0, 60.0),
        (30.0, 50.0),
        (100.0, 40.0),
        (100.0, 0.0),
    ];
    let off = offset_curve(&u, -20.0, &mut t);
    let gap = |p: Pt| {
        u.windows(2)
            .map(|w| seg_dist(p, w[0], w[1]))
            .fold(f64::INFINITY, f64::min)
    };
    assert!(off.len() > 20 && off.iter().all(|&p| gap(p) > 19.9));
    // the upper part, round the top: the lower stretch of the left arm is the shorter piece and is dropped
    assert!(off.iter().all(|p| p.1 > 40.0));
}
