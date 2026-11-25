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
use super::margins::{belt_off, candidates, Brook, BELT_BAND, STANDOFF};
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
        belt_wind: None,
        back_min_dot: std::f64::consts::FRAC_1_SQRT_2,
        outline: field.clone(),
        band: (150.0, 300.0),
        plots: Vec::new(),
        toe: Vec::new(),
        toe_rim: true,
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

/// A BAND WITH AN END ON THE WET TOE IS REFUSED THERE, ITS CENTER AND MARGIN OFF IT (449 T432): with the toe cut at the fields'
/// lower corners a margin at a corner can seat with its band swung under the fields' foot, and the toe was asked only of the
/// band's center and its margin's midpoint - the band's own samples are asked it too, as the field is.
#[test]
fn a_band_with_an_end_on_the_toe_is_refused_on_the_toe() {
    let mut i = inp();
    // the wet ground under the north margin band's west end alone: its center (3,000 ft east) and the margin's midpoint are off it
    i.toe = square(2000.0, 2000.0, 2850.0, 2490.0);
    let s = seat(&i).unwrap();
    let on_toe = |p: Pt| p.0 < 2850.0 && p.1 > 2000.0 && p.1 < 2490.0;
    for f in &s.frames {
        let (lat, dep) = f.band;
        for (a, b) in [(-0.6, 0.0), (0.0, 0.0), (0.6, 0.0)] {
            let p = (
                f.center.0 + f.along.0 * lat * a + f.out.0 * dep * b,
                f.center.1 + f.along.1 * lat * a + f.out.1 * dep * b,
            );
            assert!(!on_toe(p), "{f:?}");
        }
    }
    // the west margin seats
    assert!(s.frames[0].out.0 < -0.5, "{:?}", s.frames[0]);
}

/// ...AND ITS RIM, WHERE THE TOE STOPS AT THE FIELDS' LOWER CORNERS (449 T432): a toe reaching in at the band's end between the
/// samples refused the band (a comb's); a polder's toe, spanning its ring, is asked at the samples alone (`SeatIn::toe_rim`).
#[test]
fn a_band_whose_end_corner_is_on_the_toe_is_refused_where_the_toe_is_cut() {
    let mut i = inp();
    // under the north margin band's west end, west of every sample (the nearest at 2,820 ft east)
    i.toe = square(2000.0, 2150.0, 2750.0, 2495.0);
    let s = seat(&i).unwrap();
    assert!(s.frames[0].out.0 < -0.5, "{:?}", s.frames[0]);
    i.toe_rim = false;
    let s = seat(&i).unwrap();
    assert!(s.frames[0].out.1 < -0.5, "{:?}", s.frames[0]);
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
            (1000.0, 1000.0),
            (100.0, 102.0)
        ) > 0.99
    );
    assert!(
        belt_off(
            (500.0, 600.0),
            (1.0, 0.0),
            (0.0, -1.0),
            (50.0, 50.0),
            wind,
            (1000.0, 1000.0),
            (500.0, 662.0)
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
fn an_oblique_winds_belt_room_follows_the_bands_windward_fringe() {
    // the field below the margin to windward, the wind 30 degrees off square to it (449 T293): the belt is planted along the band's
    // windward faces (its near face and its windward end), so its room is asked there, never of a rectangle off the band's
    // windward-most corner, which would lie past the margin, here off the canvas's top edge where the fringe's belt stands on it
    let wind = (0.5, -(0.75f64.sqrt()));
    let off = belt_off(
        (500.0, 300.0),
        (1.0, 0.0),
        (0.0, 1.0),
        (100.0, 300.0),
        wind,
        (1000.0, 1000.0),
        (500.0, 42.0),
    );
    assert!(off < 1e-9, "{off}");
    // the swept ground keeps BELT_ACROSS of the band's width across the wind, and reaches no nearer the margin than the fringe's
    // carry: the near face at y 200, carried at most 146 ft along a wind 30 degrees off square, stops at y 73.6
    let g = super::margins::belt_swept(
        (500.0, 300.0),
        (1.0, 0.0),
        (0.0, 1.0),
        (100.0, 300.0),
        wind,
        BELT_BAND.1,
        (500.0, 42.0),
    );
    let low = g.iter().map(|p| p.1).fold(f64::MAX, f64::min);
    let want = 200.0 - 146.0 * 0.75f64.sqrt();
    assert!((low - want).abs() < 1e-6, "{low}");
    // a polder's seat 12 ft off its margin, the wind straight off the field (449 T292): the belt's ground is kept on the dry side,
    // so none stands between the houses and the margin, and no room is asked
    let g = super::margins::belt_swept(
        (500.0, 300.0),
        (1.0, 0.0),
        (0.0, 1.0),
        (100.0, 300.0),
        (0.0, -1.0),
        BELT_BAND.1,
        (500.0, 188.0),
    );
    assert!(g.iter().all(|p| p.1 >= 188.0 - 1e-6), "{g:?}");
    assert!(
        belt_off(
            (500.0, 300.0),
            (1.0, 0.0),
            (0.0, 1.0),
            (100.0, 300.0),
            (0.0, -1.0),
            (1000.0, 1000.0),
            (500.0, 188.0)
        ) < 1e-9
    );
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
    // the band 200 ft long either side, the field 380 ft off the west edge: the west margin's band stands 218 ft in, its belt swept
    // up to 146 ft west of its west face, past the edge (449 T293: the belt's room asked of the band's windward faces, so the field
    // stands nearer the edge than the rectangle off the band's corner needed)
    i.band = (150.0, 200.0);
    i.outline = square(380.0, 2500.0, 1380.0, 3500.0);
    i.walls = vec![(i.outline.clone(), 0.0)];
    // the west margin's belt runs off the canvas: refused, the north one seats
    let s = seat(&i).unwrap();
    assert!(s.frames.iter().all(|f| f.out.1 < 0.0));
}

/// THE BAND HOLDS NO CORNER OF THE FIELD (449 T423): a tooth of the field 40 ft wide stands 150 ft into the band of each north
/// margin beside it, between the points the band is sampled at (the middle and 0.6 of its half-length either side) - before T423
/// both margins seated, a tenth of the houses' band on the paddy (14 of 446 seated rolls, measured 2026-11-24).
#[test]
fn a_band_holding_a_corner_of_the_field_between_its_samples_is_refused() {
    let mut i = inp();
    i.outline = vec![
        (2500.0, 2500.0),
        (2880.0, 2500.0),
        (2880.0, 2350.0),
        (2920.0, 2350.0),
        (2920.0, 2500.0),
        (3500.0, 2500.0),
        (3500.0, 3500.0),
        (2500.0, 3500.0),
    ];
    i.walls = vec![(i.outline.clone(), 0.0)];
    let s = seat(&i).unwrap();
    let held = s
        .frames
        .iter()
        .filter(|f| {
            i.outline.iter().any(|p| {
                let r = (p.0 - f.center.0, p.1 - f.center.1);
                (r.0 * f.along.0 + r.1 * f.along.1).abs() < f.band.0
                    && (r.0 * f.out.0 + r.1 * f.out.1).abs() < f.band.1
            })
        })
        .count();
    assert_eq!((s.frames.is_empty(), held), (false, 0));
}

/// THE BAND'S CORNERS OFF THE FIELD PAST ITS DIP (449 T435): the north margin, 500 ft, is shorter than the 600 ft band, and the
/// field's next edge rises north-east across the band's east end with no corner of the field inside the band - before T435 the
/// margin seated with that end's corner on the paddy past the tenth of the band's depth the seat allows (574 of 41,000 sweep
/// rolls, measured 2026-11-25).
#[test]
fn a_band_whose_end_corner_a_rising_field_edge_crosses_is_refused() {
    let mut i = inp();
    i.outline = vec![
        (2700.0, 2500.0),
        (3200.0, 2500.0),
        (3700.0, 1800.0),
        (3700.0, 3500.0),
        (2700.0, 3500.0),
    ];
    i.walls = vec![(i.outline.clone(), 0.0)];
    let s = seat(&i).unwrap();
    let on = |f: &super::Frame| {
        let near = f.band.1 - super::margins::FIELD_IN_BAND_MAX * 2.0 * f.band.1;
        [
            (-1.0, -near),
            (1.0, -near),
            (-1.0, f.band.1),
            (1.0, f.band.1),
        ]
        .iter()
        .any(|&(s, t)| {
            let p = (
                f.center.0 + f.along.0 * f.band.0 * s + f.out.0 * t,
                f.center.1 + f.along.1 * f.band.0 * s + f.out.1 * t,
            );
            crate::field::geom::inside(p, &i.outline)
        })
    };
    let north = s.frames.iter().any(|f| (f.anchor.1 - 2500.0).abs() < 1.0);
    let held = s.frames.iter().filter(|f| on(f)).count();
    assert_eq!((s.frames.is_empty(), north, held), (false, false, 0));
}

/// A TONGUE OF THE FIELD ACROSS THE BAND (449 T435): a tongue 20 ft wide runs north through both north margins' bands, its tip past
/// their far edge, its foot in the tenth of the band the seat lets the field dip into, between the band's samples - so no corner of
/// either holds the field and no corner of the field stands in either; before T435 both margins seated with the tongue across
/// their houses.
#[test]
fn a_band_a_tongue_of_the_field_crosses_is_refused() {
    let mut i = inp();
    i.outline = vec![
        (2700.0, 2500.0),
        (2990.0, 2500.0),
        (2990.0, 2100.0),
        (3010.0, 2100.0),
        (3010.0, 2500.0),
        (3300.0, 2500.0),
        (3300.0, 3500.0),
        (2700.0, 3500.0),
    ];
    i.walls = vec![(i.outline.clone(), 0.0)];
    let s = seat(&i).unwrap();
    let north = s
        .frames
        .iter()
        .filter(|f| (f.anchor.1 - 2500.0).abs() < 1.0)
        .count();
    assert_eq!((s.frames.is_empty(), north), (false, 0));
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

#[test]
fn only_a_fall_toward_the_wind_backs_the_hill() {
    // the land falling north-east, square across the north-west wind: the high side is the south-west
    let s = 0.5f64.sqrt();
    let mut i = inp();
    i.fall = (s, -s);
    // the north margin's seat on the toe, the west one's center in the reeds: no margin faces the wind
    i.toe = square(2000.0, 2100.0, 4000.0, 2400.0);
    i.reeds = vec![square(2000.0, 2600.0, 2400.0, 3400.0)];
    // refused by name, never seated on the high south margin off the wind (0031: the rolled falls keep their back to it)
    assert!(seat(&i).is_err());
    // the same field falling north-west, into the wind: the high south-east margin is taken, off the wind
    i.fall = (-s, -s);
    let h = seat(&i).unwrap();
    assert!(h.frames.iter().all(|f| f.offwind));
    // the belt on the windward side, between the houses and the field (0072: the wind decides the side; 449 T277): a seat whose
    // field lies to windward stands its band the belt's depth further off the margin, so its belt's ground is the near strip
    for f in &h.frames {
        let off = (f.center.0 - f.anchor.0) * f.out.0 + (f.center.1 - f.anchor.1) * f.out.1;
        let windward = -(f.out.0 * i.wind.0 + f.out.1 * i.wind.1) >= i.back_min_dot;
        let room = if windward { BELT_BAND.1 } else { 0.0 };
        assert!((off - (STANDOFF + room + f.band.1)).abs() < 1e-6, "{off}");
    }
    assert!(h
        .frames
        .iter()
        .any(|f| -(f.out.0 * i.wind.0 + f.out.1 * i.wind.1) >= i.back_min_dot));
}

#[test]
fn a_fall_into_the_wind_backs_the_hill_when_its_one_windward_margin_is_walled_in() {
    // the field falling north-west, into the wind; the north margin's seat on the toe, the west margin's kept by the ranking
    let s = 0.5f64.sqrt();
    let mut i = inp();
    i.fall = (-s, -s);
    i.toe = square(2000.0, 2100.0, 4000.0, 2400.0);
    // ...and a ring of water round the whole west margin's ground: every seat the ranking kept has no dry way out
    let (x0, y0, x1, y1) = (2050.0, 2450.0, 2490.0, 3550.0);
    i.lines = vec![
        ((x0, y0), (x1, y0)),
        ((x1, y0), (x1, y1)),
        ((x1, y1), (x0, y1)),
        ((x0, y1), (x0, y0)),
    ];
    // before 449 T423 the hill-backed seat was asked only when the ranking kept no margin, so this site was refused "walled
    // in" (seeds 115 and 260 of 12 households falling at 180 degrees); the high margin is taken, off the wind
    let h = seat(&i).unwrap();
    assert!(!h.frames.is_empty() && h.frames.iter().all(|f| f.offwind));
    // a fall square across the wind still refuses by name, its walled-in margin counted
    i.fall = (s, -s);
    let refused = seat(&i).unwrap_err().to_string();
    let named = refused.contains("walled in") && !refused.contains(" 0 walled in");
    assert!(named, "{refused}");
}

#[test]
fn a_seat_walled_in_at_its_center_leaves_by_its_bands_end_once_no_margin_is_left() {
    // the land falling north-east, square across the north-west wind; the north margin's seat on the toe, the west margin's kept
    let s = 0.5f64.sqrt();
    let mut i = inp();
    i.fall = (s, -s);
    i.toe = square(2000.0, 2100.0, 4000.0, 2400.0);
    // a ring of water round the west seat's center alone, its band's ends on open ground: before 449 T426 the site was refused
    // "1 walled in" (seeds 941239097 and 508: the center in the pocket between the brook, the feeder and the field's corner)
    let (cx, cy) = (2338.0, 3000.0);
    i.lines = vec![
        ((cx - 120.0, cy - 120.0), (cx + 120.0, cy - 120.0)),
        ((cx + 120.0, cy - 120.0), (cx + 120.0, cy + 120.0)),
        ((cx + 120.0, cy + 120.0), (cx - 120.0, cy + 120.0)),
        ((cx - 120.0, cy + 120.0), (cx - 120.0, cy - 120.0)),
    ];
    let seated = seat(&i).unwrap();
    // the west margin, its back still to the wind
    assert!(seated.frames.len() == 1 && seated.frames[0].out.0 < -0.5 && !seated.frames[0].offwind);
}

#[test]
fn a_fall_square_across_the_wind_from_either_side_never_backs_the_hill() {
    // the driver's fall of 315 degrees against the north-west wind: square across it, its dot with the wind a rounding hair above
    // nothing where 135 degrees' is a hair below - before 449 T426 the hair asked the hill-backed seat (3 of 20,000 cohort combs)
    let mut i = inp();
    let rad = 315.0f64.to_radians();
    i.fall = (rad.cos(), rad.sin());
    assert!(i.fall.0 * i.wind.0 + i.fall.1 * i.wind.1 > 0.0);
    i.toe = square(2000.0, 2100.0, 4000.0, 2400.0);
    i.reeds = vec![square(2000.0, 2600.0, 2400.0, 3400.0)];
    assert!(seat(&i).is_err());
}
