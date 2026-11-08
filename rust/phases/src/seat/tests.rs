//! The seat's unit tests (feature 444 T27).
//!
//! Research:
//!     the seat's tests - NONE: fixtures and assertions, deciding nothing about the place

#![expect(
    clippy::many_single_char_names,
    reason = "the plane geometry's own names"
)]
use std::collections::HashMap;

use super::exit::{in_any, seg_seg, Exit};
use super::fords::{fords, gapped};
use super::index::{area, clipped, Cells, Strips};
use super::margins::{belt_off, candidates, Brook};
use super::{seat, SeatIn};
use crate::field::fan::Pt;

fn square(x0: f64, y0: f64, x1: f64, y1: f64) -> Vec<Pt> {
    vec![(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
}

/// A field 1,000 ft square in a 6,000 ft canvas, the wind from the north-west, the land falling south.
fn inp() -> SeatIn {
    let field = square(2500.0, 2500.0, 3500.0, 3500.0);
    let s = 0.5f64.sqrt();
    SeatIn {
        canvas: (6000.0, 6000.0),
        fall: (0.0, 1.0),
        wind: (-s, -s),
        back_min_dot: std::f64::consts::FRAC_1_SQRT_2,
        outline: field.clone(),
        band: (150.0, 300.0),
        plots: Vec::new(),
        toe: Vec::new(),
        reeds: Vec::new(),
        brook: Vec::new(),
        walls: vec![(field, 0.0)],
        lines: Vec::new(),
        streams: Vec::new(),
        ford: (160.0, 30.0, 20.0),
    }
}

#[test]
fn the_seat_faces_the_wind_on_the_field_s_high_side_and_ranks_its_ladder() {
    let s = seat(&inp()).unwrap();
    let head = &s.frames[0];
    // its back to the north, upslope and into the wind
    assert!(head.out.1 < 0.0);
    assert!(head.center.1 < 2500.0 && !head.offwind);
    // the west margin, its back turned to the wind off the flank, is the ladder
    assert!(s.frames.len() >= 2);
    #[cfg(feature = "counters")] // a count, kept by the counting build alone (FR-012)
    assert!(s.counts["candidate@margins"] >= 2);
}

#[test]
fn a_margin_that_breaks_a_rule_is_refused_and_a_site_with_none_named() {
    let mut i = inp();
    i.canvas = (3600.0, 3600.0);
    i.band = (150.0, 1300.0);
    let e = seat(&i).unwrap_err();
    assert!(e.0.starts_with("no field margin turns its back to the wind clear of the dry hem, the toe and the canvas edge (of the margins facing it: ") && e.0.contains("off the frame"));
    assert_eq!(e.to_string(), e.0);
    // the toe at the north margin, the reeds at the west, crop behind both: each refused or scored down
    let mut i = inp();
    i.toe = square(2000.0, 2100.0, 4000.0, 2400.0);
    let s = seat(&i).unwrap();
    // the north margin's seat stands on the toe: the west one seats
    assert!(s.frames.iter().all(|f| f.out.0 < -0.5));
    i.reeds = vec![square(2000.0, 2600.0, 2400.0, 3400.0)];
    // the west one's center in the reeds: no seat
    assert!(seat(&i).is_err());
    let mut i = inp();
    i.reeds = vec![square(2000.0, 2900.0, 2400.0, 3400.0)];
    // an end of the band in the reeds scores it down, no more
    assert!(seat(&i).is_ok());
    let mut i = inp();
    i.plots = vec![
        square(2700.0, 1800.0, 3300.0, 2480.0),
        square(2000.0, 2500.0, 2480.0, 3000.0),
    ];
    let s = seat(&i).unwrap_err();
    assert!(s.0.contains("dry hem"));
    let mut i = inp();
    i.plots = vec![square(2940.0, 2380.0, 3060.0, 2440.0)];
    // a plot near the margin scores the hem down, no more
    assert!(seat(&i).is_ok());
}

#[test]
fn the_brook_breaks_a_tie_and_opens_its_fords() {
    let mut i = inp();
    i.brook = (0..=300).map(|k| (1500.0, f64::from(k) * 20.0)).collect();
    i.streams = vec![i.brook.clone()];
    let s = seat(&i).unwrap();
    let len = |segs: &[(Pt, Pt)]| {
        segs.iter()
            .map(|(a, b)| crate::field::geom::dist(*a, *b))
            .sum::<f64>()
    };
    // each ford gaps the stream
    assert!(
        !s.fords.is_empty()
            && len(&s.stream_segs)
                < 6000.0 - 50.0 * f64::from(u32::try_from(s.fords.len()).unwrap())
    );
    let mut counts = HashMap::new();
    let bend: Vec<Pt> = vec![(0.0, 0.0), (200.0, 0.0), (200.0, 200.0)];
    // the corner's place skipped
    assert!(fords(&bend, 400.0, 30.0, 20.0, &mut counts).is_empty());
    // both places on straight reaches
    assert_eq!(fords(&bend, 160.0, 30.0, 20.0, &mut counts).len(), 2);
    assert!(fords(&[(0.0, 0.0), (0.0, 0.0)], 160.0, 30.0, 20.0, &mut counts).is_empty());
    let g = gapped(
        &[vec![(0.0, 0.0), (100.0, 0.0)], vec![(5.0, 5.0), (5.0, 5.0)]],
        &[(50.0, 0.0), (0.0, 0.0), (100.0, 0.0)],
        10.0,
        &mut counts,
    );
    // the middle cut, both ends cut away, the point kept
    assert_eq!(g.len(), 3);
    let line: Vec<Pt> = (0..=10).map(|k| (f64::from(k) * 10.0, 0.0)).collect();
    let mut reads = 0;
    let b = Brook::new(&line, (1.0, 0.0), &mut reads);
    let mut t = 0;
    assert!((b.near((50.0, 5.0), (1.0, 0.0), 30.0, &mut t) - 5.0).abs() < 1e-9);
    let back: Vec<Pt> = line.iter().rev().copied().collect();
    let b = Brook::new(&back, (1.0, 0.0), &mut reads);
    // a course that climbs is scanned whole
    assert!((b.near((50.0, 5.0), (1.0, 0.0), 30.0, &mut t) - 5.0).abs() < 1e-9);
    // walled on three sides and the water: the walk finds the gap
    assert!(
        (Brook::new(&line[..1], (1.0, 0.0), &mut reads).near((0.0, 0.0), (1.0, 0.0), 30.0, &mut t)
            - 30.0)
            .abs()
            < 1e-9
    );
}
#[test]
fn the_way_out_runs_straight_or_walks_and_remembers() {
    let walls = vec![
        (square(-100.0, 400.0, 700.0, 500.0), 0.0),
        (square(400.0, -100.0, 500.0, 450.0), 0.0),
    ];
    let lines = vec![
        ((-100.0, 200.0), (300.0, 200.0)),
        ((200.0, -100.0), (200.0, 300.0)),
    ];
    let mut counts = HashMap::new();
    let mut way = Exit::new(&walls, &lines, (600.0, 600.0), &mut counts);
    assert!(way.has_exit((300.0, 300.0), &mut counts));
    // remembered
    assert!(way.has_exit((310.0, 310.0), &mut counts));
    // a seat in the same walled ground, its walk reaching cells the first walk tested and reached
    assert!(way.has_exit((250.0, 250.0), &mut counts));
    #[cfg(feature = "counters")] // a count, kept by the counting build alone (FR-012)
    assert!(counts["test@exit_walk"] > 0);
    let shut = vec![(square(100.0, 100.0, 500.0, 500.0), 0.0)];
    let ring = vec![
        ((50.0, 50.0), (550.0, 50.0)),
        ((550.0, 50.0), (550.0, 550.0)),
        ((550.0, 550.0), (50.0, 550.0)),
        ((50.0, 550.0), (50.0, 50.0)),
    ];
    let mut way = Exit::new(&shut, &ring, (600.0, 600.0), &mut counts);
    // inside the water's ring there is no way out
    assert!(!way.has_exit((75.0, 300.0), &mut counts));
    // remembered walled in
    assert!(!way.has_exit((75.0, 310.0), &mut counts));
    // inside a wall
    assert!(!way.has_exit((300.0, 300.0), &mut counts));
    let open: Vec<(Vec<Pt>, f64)> = Vec::new();
    let mut way = Exit::new(&open, &[], (600.0, 600.0), &mut counts);
    assert!(way.has_exit((300.0, 300.0), &mut counts));
    assert!(in_any((300.0, 300.0), &shut) && !in_any((0.0, 0.0), &shut));
    assert!(seg_seg((0.0, 0.0), (10.0, 10.0), (0.0, 10.0), (10.0, 0.0)) < 1e-9);
    assert!((seg_seg((0.0, 0.0), (10.0, 0.0), (0.0, 5.0), (10.0, 5.0)) - 5.0).abs() < 1e-9);
}

#[test]
fn the_indexes_answer_as_the_whole_ring_does() {
    let ring: Vec<Pt> = vec![
        (0.0, 0.0),
        (300.0, 0.0),
        (300.0, 300.0),
        (150.0, 100.0),
        (0.0, 300.0),
    ];
    let mut filed = 0;
    let st = Strips::new(&ring, &mut filed);
    let mut t = 0;
    for p in [
        (150.0, 50.0),
        (150.0, 200.0),
        (50.0, 200.0),
        (400.0, 50.0),
        (150.0, -100.0),
    ] {
        assert_eq!(st.inside(p, &mut t), crate::field::geom::inside(p, &ring));
    }
    let mut cells = Cells::new(64.0);
    assert_eq!(cells.file(0, &[(0.0, 0.0), (100.0, 10.0)]), 2);
    assert_eq!(cells.in_box((0.0, 0.0), (130.0, 10.0)).0, vec![0]);
    let c = clipped(
        &square(0.0, 0.0, 10.0, 10.0),
        &[(5.0, 5.0), (5.0, 15.0), (15.0, 15.0), (15.0, 5.0)],
    );
    // a clip window turning either way
    assert!((area(&c) - 25.0).abs() < 1e-9);
    let wind = (0.0, -1.0);
    assert!(
        belt_off(
            (100.0, 40.0),
            (1.0, 0.0),
            (0.0, -1.0),
            (50.0, 50.0),
            wind,
            (1000.0, 1000.0)
        ) > 0.99
    );
    assert!(
        belt_off(
            (500.0, 600.0),
            (1.0, 0.0),
            (0.0, -1.0),
            (50.0, 50.0),
            wind,
            (1000.0, 1000.0)
        ) < 1e-9
    );
    let mut t = 0;
    let c = candidates(
        &square(0.0, 0.0, 10.0, 10.0),
        (0.0, -1.0),
        std::f64::consts::FRAC_1_SQRT_2,
        &mut t,
    );
    // only the north margin faces a north wind; the east and west, square to it, turn their backs off the flank (tier 1, the square
    // end in); the south is behind
    assert_eq!(c.iter().filter(|k| k.2 == 0).count(), 1);
    assert_eq!(c.iter().filter(|k| k.2 == 1).count(), 2);
    assert!(c.iter().all(|k| k.0 .1 < 10.0));
}

#[test]
fn a_flank_turns_its_back_and_a_notch_or_a_cramped_belt_is_refused() {
    let mut t = 0;
    let wind = (0.5, -(0.75f64.sqrt()));
    let c = candidates(
        &square(0.0, 0.0, 10.0, 10.0),
        wind,
        std::f64::consts::FRAC_1_SQRT_2,
        &mut t,
    );
    // the north margin faces a wind 30 degrees east of north; the east one turns its back to it off the flank
    assert_eq!(c.iter().map(|k| k.2).collect::<Vec<_>>(), vec![0, 1]);
    let mut i = inp();
    i.outline = vec![
        (2500.0, 2500.0),
        (2900.0, 2500.0),
        (2900.0, 2800.0),
        (3100.0, 2800.0),
        (3100.0, 2500.0),
        (3500.0, 2500.0),
        (3500.0, 3500.0),
        (2500.0, 3500.0),
    ];
    // the notch's floor faces north, its band on the field's arms: refused; the outer margins seat
    let s = seat(&i).unwrap();
    assert!(s.frames.iter().all(|f| (f.anchor.1 - 2800.0).abs() > 1.0));
    let mut i = inp();
    i.canvas = (3900.0, 6000.0);
    i.outline = square(500.0, 2500.0, 1500.0, 3500.0);
    i.walls = vec![(i.outline.clone(), 0.0)];
    // the west margin's belt runs off the canvas: refused, the north one seats
    let s = seat(&i).unwrap();
    assert!(s.frames.iter().all(|f| f.out.1 < 0.0));
}

#[test]
fn a_walled_in_head_gives_way_to_the_next_margin() {
    let mut i = inp();
    // a ring of water round the north margin's seat alone
    let (cx, cy) = (3000.0, 2338.0);
    i.lines = vec![
        ((cx - 120.0, cy - 120.0), (cx + 120.0, cy - 120.0)),
        ((cx + 120.0, cy - 120.0), (cx + 120.0, cy + 120.0)),
        ((cx + 120.0, cy + 120.0), (cx - 120.0, cy + 120.0)),
        ((cx - 120.0, cy + 120.0), (cx - 120.0, cy - 120.0)),
    ];
    let s = seat(&i).unwrap();
    // the west margin heads the ranking
    assert!(s.frames[0].out.0 < -0.5);
}
