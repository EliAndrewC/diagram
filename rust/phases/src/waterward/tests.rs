//! The waterward fringe's unit tests (feature 444 T29).
//!
//! Research:
//!     the fringe's tests - NONE: fixtures and assertions, deciding nothing about the place

use super::{bed, clip, difference, face, face_at, flanks, fringe, nearest};
use crate::field::fan::Pt;

/// A box's outline walked round, 21 corners a side (each side's last the next one's first, so 84 in all).
fn ring(x0: f64, y0: f64, x1: f64, y1: f64) -> Vec<(f64, f64)> {
    let side = |a: Pt, b: Pt| {
        (0..=20).map(move |k| {
            let t = f64::from(k) / 20.0;
            (a.0 + (b.0 - a.0) * t, a.1 + (b.1 - a.1) * t)
        })
    };
    side((x0, y0), (x1, y0))
        .chain(side((x1, y0), (x1, y1)))
        .chain(side((x1, y1), (x0, y1)))
        .chain(side((x0, y1), (x0, y0)))
        .collect()
}

const SQUARE: (f64, f64, f64, f64) = (1000.0, 1000.0, 2000.0, 2000.0);

#[test]
fn the_foot_and_the_cross_flanks_the_village_does_not_stand_on() {
    // the land falls south: the head north, the foot south, the cross flanks west and east
    assert_eq!(flanks((0.0, 1.0), None), vec!['W', 'E', 'S']);
    // the village on the east flank
    assert_eq!(flanks((0.0, 1.0), Some((1.0, 0.0))), vec!['W', 'S']);
    // falling west, the village on the north
    assert_eq!(flanks((-1.0, 0.0), Some((0.0, -1.0))), vec!['S', 'W']);
}

#[test]
fn a_point_is_the_side_it_stands_nearest() {
    assert_eq!(nearest((1001.0, 1500.0), SQUARE), 'W');
    assert_eq!(nearest((1999.0, 1500.0), SQUARE), 'E');
    assert_eq!(nearest((1500.0, 1001.0), SQUARE), 'N');
    assert_eq!(nearest((1500.0, 1999.0), SQUARE), 'S');
    // a tie the first named
    assert_eq!(nearest((1000.0, 1000.0), SQUARE), 'W');
}

#[test]
fn the_strip_follows_the_dike_s_outer_face() {
    let dike = ring(1000.0, 1000.0, 2000.0, 2000.0);
    let mut t = 0;
    // the outermost face of the west side, a run at one face its ends only
    let west = face(&dike, SQUARE, 'W', 970.0, 2020.0, &mut t);
    assert!(west.iter().all(|p| (p.0 - 1000.0).abs() < 1e-9) && west.len() < 32);
    let north = face(&dike, SQUARE, 'N', 970.0, 2020.0, &mut t);
    let south = face(&dike, SQUARE, 'S', 970.0, 2020.0, &mut t);
    let east = face(&dike, SQUARE, 'E', 970.0, 2020.0, &mut t);
    assert!(
        north.iter().all(|p| (p.1 - 1000.0).abs() < 1e-9)
            && south.iter().all(|p| (p.1 - 2000.0).abs() < 1e-9)
            && east.iter().all(|p| (p.0 - 2000.0).abs() < 1e-9)
    );
    // a span past the ring takes the box's side in the bins the face does not reach
    let wide = face(&dike, SQUARE, 'W', 0.0, 3000.0, &mut t);
    assert!(wide.iter().all(|p| (p.0 - 1000.0).abs() < 1e-9));
}

/// THE STRIP KEEPS OFF THE DIKE (449 T236): round a cut-off corner the strip's end holds only the next face's corners - the old rule,
/// the outermost of the flank's half in each of 32 bins, took them and turned the strip 40 ft onto the north face; and where the
/// face steps out, the face follows it corner for corner, so it never runs inside the ring.
#[test]
fn the_face_keeps_to_its_own_side_round_a_corner_and_never_runs_inside_the_ring() {
    // a square with its north-west corner cut off 40 ft each way, and its west face stepped 10 ft out below y = 1500
    let mut dike: Vec<Pt> = vec![(1040.0, 1000.0)];
    dike.extend((0..=20).map(|k| (1040.0 + 48.0 * f64::from(k), 1000.0)));
    dike.extend((0..=20).map(|k| (2000.0, 1000.0 + 50.0 * f64::from(k))));
    dike.extend((0..=20).map(|k| (2000.0 - 50.0 * f64::from(k), 2000.0)));
    dike.extend((0..=10).map(|k| (990.0, 2000.0 - 50.0 * f64::from(k))));
    dike.extend((0..=9).map(|k| (1000.0, 1490.0 - 50.0 * f64::from(k))));
    dike.push((1000.0, 1040.0));
    let bbox = (990.0, 1000.0, 2000.0, 2000.0);
    let mut t = 0;
    let west = face(&dike, bbox, 'W', 970.0, 2020.0, &mut t);
    // never past the corner's own west face
    assert!(west.iter().all(|p| p.0 <= 1000.0), "{west:?}");
    // every point of the west face the strip reaches at or outside it
    for k in 0..=400 {
        let y = 1040.0 + f64::from(k) * 2.4;
        let x = if y < 1500.0 { 1000.0 } else { 990.0 };
        if !(1490.0..=1510.0).contains(&y) {
            let along: Vec<(f64, f64)> = west.iter().map(|p| (p.1, p.0)).collect();
            assert!(face_at(&along, y, &mut t) <= x + 1e-9, "at {y}: {west:?}");
        }
    }
}

#[test]
fn the_face_is_read_between_its_points_and_held_past_its_ends() {
    let f = vec![(0.0, 10.0), (0.0, 10.0), (100.0, 30.0)];
    let mut t = 0;
    assert!((face_at(&f, 50.0, &mut t) - 20.0).abs() < 1e-9);
    assert!((face_at(&f, -5.0, &mut t) - 10.0).abs() < 1e-9);
    assert!((face_at(&f, 150.0, &mut t) - 30.0).abs() < 1e-9);
    assert!((face_at(&[], 5.0, &mut t)).abs() < 1e-9);
}

/// Whether the strip `s` reaches into the band `lo` to `hi` along `axis`: any of its points inside it.
fn reaches(s: &[Pt], axis: usize, lo: f64, hi: f64) -> bool {
    s.iter().any(|p| {
        let v = if axis == 0 { p.0 } else { p.1 };
        v > lo + 1e-9 && v < hi - 1e-9
    })
}

/// THE REEDS STOP AT THE CUT (449 T236): a channel through the foot's middle parts its strip in two, each ending at a bank; a
/// channel out of a corner cuts the cross flank's run past the corner off, and the foot's sliver beyond it is dropped.
#[test]
fn a_strip_stops_at_each_bank_of_the_channel_that_crosses_it() {
    let dike = ring(1000.0, 1000.0, 2000.0, 2000.0);
    let mid: [Pt; 2] = [(1500.0, 1990.0), (1500.0, 2400.0)];
    let f = fringe(
        &dike,
        &[(&mid, 6.0)],
        280.0,
        (3000.0, 3000.0),
        (0.0, 1.0),
        Some((1.0, 0.0)),
    );
    assert_eq!(f.flanks, vec!['W', 'S']);
    assert_eq!(f.strips.len(), 3);
    let (left, right) = (&f.strips[1], &f.strips[2]);
    assert!(
        left.iter().all(|p| p.0 <= 1497.0 + 1e-9) && right.iter().all(|p| p.0 >= 1503.0 - 1e-9)
    );
    assert!(
        left.iter().any(|p| (p.0 - 1497.0).abs() < 1e-9)
            && right.iter().any(|p| (p.0 - 1503.0).abs() < 1e-9)
    );
    // two channels through the foot, named out of order: its strip in three, each between two banks
    let east: [Pt; 2] = [(1700.0, 1990.0), (1700.0, 2400.0)];
    let f = fringe(
        &dike,
        &[(&east, 6.0), (&mid, 6.0)],
        280.0,
        (3000.0, 3000.0),
        (0.0, 1.0),
        Some((1.0, 0.0)),
    );
    assert_eq!(f.strips.len(), 4);
    assert!(f.strips[2]
        .iter()
        .all(|p| p.0 >= 1503.0 - 1e-9 && p.0 <= 1697.0 + 1e-9));
    // out of the south-west corner, then straight down outside the west face
    let corner: [Pt; 3] = [(1000.0, 2000.0), (990.0, 2010.0), (990.0, 2400.0)];
    let f = fringe(
        &dike,
        &[(&corner, 5.0)],
        280.0,
        (3000.0, 3000.0),
        (0.0, 1.0),
        Some((1.0, 0.0)),
    );
    assert_eq!(f.strips.len(), 2);
    // the west strip ends above the channel's straight run (its bed carried 2.5 ft past the bend), the foot's begins at its east
    // bank, and nothing west of it on the foot
    assert!(f.strips[0].iter().all(|p| p.1 <= 2007.5 + 1e-9));
    assert!(reaches(&f.strips[0], 1, 1990.0, 2010.0));
    assert!(f.strips[1].iter().all(|p| p.0 >= 992.5 - 1e-9));
    assert!(f.strips[1].iter().any(|p| (p.0 - 992.5).abs() < 1e-9));
}

#[test]
fn a_polder_s_strips_run_off_toward_the_frame_and_none_without_a_dike() {
    let dike = ring(1000.0, 1000.0, 2000.0, 2000.0);
    let f = fringe(
        &dike,
        &[],
        280.0,
        (3000.0, 3000.0),
        (0.0, 1.0),
        Some((1.0, 0.0)),
    );
    assert_eq!(f.flanks, vec!['W', 'S']);
    // each strip 280 ft deep off its face
    assert!(
        f.strips.len() == 2
            && (f.strips[0][0].0 - 720.0).abs() < 1e-9
            && (f.strips[1][0].1 - 2280.0).abs() < 1e-9
    );
    #[cfg(feature = "counters")] // a count, kept by the counting build alone (FR-012)
    assert!(f.counts["write@strip"] > 0);
    // EVERY LOOP COUNTED (feature 449 T226, rubric S5; 449 T236): the ring's 84 corners. Each face files every corner to its side
    // and walks them again for its own (2 x 84), sorts its own along the axis, a comparison each, asks its two ends' neighbors (4)
    // and writes its own out (23) - the face's own tally; each strip turns its face to (along, depth) (n), filters its points into
    // the strip (n) and reads the face at its two ends by halving (the bits of n and one more, each), boxes the strip (its n + 2
    // corners: the face but its two ends, the face read at them, the two outer corners) and reads its one piece's span (n + 2), no
    // bed asked and no sort to make; the fringe boxes the ring (84); the three flanks asked of the seat's side.
    #[cfg(feature = "counters")]
    {
        let mut t = 0;
        let w = face(&dike, SQUARE, 'W', 970.0, 2020.0, &mut t);
        let s = face(&dike, SQUARE, 'S', 970.0, 2020.0, &mut t);
        // the 21 corners of a side and its two neighbors' ends on it, 23 own, sorted: more than 22 comparisons each
        assert!(t > 2 * (2 * 84 + 4 + 23 + 22));
        let steps = |n: u64| u64::from(u64::BITS - n.leading_zeros()) + 1;
        let per = |n: u64| n + n + 2 * steps(n) + 2 * (n + 2);
        let want = t + per(w.len() as u64) + per(s.len() as u64);
        assert_eq!(
            (
                f.counts.get("test@face"),
                f.counts.get("test@fringe"),
                f.counts.get("test@flanks"),
                f.counts.get("read@dike")
            ),
            (Some(&want), Some(&84), Some(&3), Some(&84))
        );
    }
    // held to 20 ft off the frame
    let big = ring(100.0, 100.0, 2900.0, 2900.0);
    let tight = fringe(&big, &[], 280.0, (3000.0, 3000.0), (0.0, -1.0), None);
    assert!(tight
        .strips
        .iter()
        .flatten()
        .all(|p| p.0 >= -20.0 && p.0 <= 3020.0 && p.1 >= -20.0 && p.1 <= 3020.0));
    assert!(fringe(&[], &[], 280.0, (3000.0, 3000.0), (0.0, 1.0), None)
        .strips
        .is_empty());
}

/// How far out from the channel `a` to `b` (`w` feet wide) the reeds stand beside its banks, at depths `ys` into the foot's strip:
/// for each depth and each bank, the least step along the strip past the bank (to 300 ft, by half a foot) that lands inside a
/// strip, the worst of them; and whether any point of the channel's own course at those depths lies under the reeds.
#[expect(
    clippy::many_single_char_names,
    reason = "the plane geometry's own names"
)]
fn stand_off(strips: &[Vec<Pt>], (a, b): (Pt, Pt), w: f64, ys: &[f64]) -> (f64, bool) {
    let len = crate::field::geom::dist(a, b);
    let (dx, dy) = ((b.0 - a.0) / len, (b.1 - a.1) / len);
    // the bank's offset along the strip from the course, at one depth
    let bank = w / 2.0 / dy.abs();
    let under = |p: Pt| strips.iter().any(|s| crate::field::geom::inside(p, s));
    let (mut worst, mut wet) = (0.0_f64, false);
    for &y in ys {
        // the course at depth y
        let s = (y - a.1) / dy;
        let c = (a.0 + dx * s, y);
        wet |= under(c);
        for side in [1.0, -1.0] {
            let k = (1..600)
                .map(|i| f64::from(i) * 0.5)
                .find(|&k| under((c.0 + side * (bank + k), c.1)))
                .unwrap_or(300.0);
            worst = worst.max(k);
        }
    }
    (worst, wet)
}

/// THE REEDS RUN TO THE BANK OF A SLANTING CHANNEL (449 T236, research/questions/0074-reed-beds-and-the-marshs-edge-yoshihara.drawing.html
/// "How our maps draw the marsh's edge": where a ditch crosses the marsh the reeds are drawn right to the water's edge). A reach 30
/// degrees off square across the foot's whole strip, and a reach 45 degrees off square ending inside it (Kuwabata's outfall's first
/// stretch), each leave the reeds within half a foot of each bank at every depth sampled, and none over the water. Red before the
/// fix: the box round each reach took the reeds beside its banks, 156 and 56 ft along the strip from the nearest bank at worst.
#[test]
fn the_reeds_reach_each_bank_of_a_slanting_channel() {
    let dike = ring(1000.0, 1000.0, 2000.0, 2000.0);
    let rad = 30_f64.to_radians();
    let across: [Pt; 2] = [
        (1500.0, 1990.0),
        (1500.0 + 400.0 * rad.sin(), 1990.0 + 400.0 * rad.cos()),
    ];
    let f = fringe(
        &dike,
        &[(&across, 6.0)],
        280.0,
        (3000.0, 3000.0),
        (0.0, 1.0),
        Some((1.0, 0.0)),
    );
    let ys: Vec<f64> = (0..14).map(|k| 2010.0 + 20.0 * f64::from(k)).collect();
    let crossing = stand_off(&f.strips, (across[0], across[1]), 6.0, &ys);
    let half = 45_f64.to_radians();
    let short: [Pt; 2] = [
        (1500.0, 1990.0),
        (1500.0 + 100.0 * half.sin(), 1990.0 + 100.0 * half.cos()),
    ];
    let f = fringe(
        &dike,
        &[(&short, 5.5)],
        280.0,
        (3000.0, 3000.0),
        (0.0, 1.0),
        Some((1.0, 0.0)),
    );
    let ys: Vec<f64> = (0..6).map(|k| 2005.0 + 10.0 * f64::from(k)).collect();
    let ending = stand_off(&f.strips, (short[0], short[1]), 5.5, &ys);
    // the worst stand-off from a bank (ft) and whether the water is under the reeds: across the strip, then ending in it
    assert_eq!((crossing, ending), ((0.5, false), (0.5, false)));
}

/// The area of a ring, unsigned.
fn area(r: &[Pt]) -> f64 {
    crate::field::geom::signed_area(r).abs()
}

/// A BED TAKEN OUT ALONG ITS OWN SIDES (449 T236): a bed biting into a ring's edge leaves one ring notched by it, whichever way
/// the ring runs and wherever it starts; a bed across it leaves two; a bed wholly inside is parted across its middle and leaves
/// two, round it; a notch reaching into the bed from one side is walked round the bed's whole far side; a ring wholly inside the
/// bed is gone; a bed beside it takes nothing.
#[test]
fn a_bed_is_taken_out_of_a_ring_along_its_own_sides() {
    let square = vec![(0.0, 0.0), (100.0, 0.0), (100.0, 100.0), (0.0, 100.0)];
    let mut t = 0;
    let q = |a: Pt, b: Pt, w: f64| bed(a, b, w).unwrap();
    // a bed 10 ft wide up from below the bottom edge to y 40, carried 5 ft past: 450 sq ft taken
    let notch = q((50.0, -20.0), (50.0, 40.0), 10.0);
    for ring in [
        square.clone(),
        square.iter().rev().copied().collect(),
        vec![
            (50.0, 0.0),
            (100.0, 0.0),
            (100.0, 100.0),
            (0.0, 100.0),
            (0.0, 0.0),
        ],
    ] {
        let left = difference(&ring, &notch, &mut t);
        assert_eq!(left.len(), 1);
        assert!((area(&left[0]) - 9550.0).abs() < 1e-6, "{left:?}");
        assert!(!crate::field::geom::inside((50.0, 20.0), &left[0]));
    }
    let across = difference(&square, &q((50.0, -20.0), (50.0, 120.0), 10.0), &mut t);
    assert_eq!(across.len(), 2);
    assert!(across.iter().all(|r| (area(r) - 4500.0).abs() < 1e-6));
    // wholly inside: 30 by 10 ft taken, the ring in two halves round it
    let hole = difference(&square, &q((40.0, 50.0), (60.0, 50.0), 10.0), &mut t);
    assert_eq!(hole.len(), 2);
    assert!((hole.iter().map(|r| area(r)).sum::<f64>() - 9700.0).abs() < 1e-6);
    assert!(hole
        .iter()
        .all(|r| !crate::field::geom::inside((50.0, 50.0), r)));
    // a notch 50 by 10 ft in from the left edge reaching into a bed 40 by 80 ft: what is left is the square less both
    let dented = vec![
        (0.0, 0.0),
        (100.0, 0.0),
        (100.0, 100.0),
        (0.0, 100.0),
        (0.0, 55.0),
        (50.0, 55.0),
        (50.0, 45.0),
        (0.0, 45.0),
    ];
    let left = difference(&dented, &q((50.0, 30.0), (50.0, 70.0), 40.0), &mut t);
    assert_eq!(left.len(), 1);
    assert!((area(&left[0]) - 6500.0).abs() < 1e-6, "{left:?}");
    // a ring wholly inside the bed, and a bed beside the ring
    let small = vec![(49.0, 49.0), (51.0, 49.0), (51.0, 51.0), (49.0, 51.0)];
    assert!(difference(&small, &q((50.0, 0.0), (50.0, 100.0), 10.0), &mut t).is_empty());
    assert_eq!(
        difference(&square, &q((150.0, 0.0), (150.0, 100.0), 10.0), &mut t),
        vec![square.clone()]
    );
    // a reach of no length has no bed
    assert!(bed((5.0, 5.0), (5.0, 5.0), 6.0).is_none());
    // a ring cut to a half-plane
    assert_eq!(clip(&square, (1.0, 0.0), 50.0, &mut t).len(), 4);
}

/// THE RUN PAST THE DIKE STOPS AT THE CHANNEL AT EITHER END (449 T236): a channel out of the north-west corner and up outside the
/// west face ends the west strip's run before the dike's start at its south bank, as one out of the south-west corner ends its run
/// past the dike's end; a reach of no length is passed over.
#[test]
fn the_run_past_the_dike_ends_at_a_channel_at_either_end_of_the_span() {
    let dike = ring(1000.0, 1000.0, 2000.0, 2000.0);
    let north: [Pt; 3] = [(1000.0, 1000.0), (990.0, 990.0), (990.0, 600.0)];
    let none: [Pt; 2] = [(500.0, 500.0), (500.0, 500.0)];
    let f = fringe(
        &dike,
        &[(&north, 5.0), (&none, 5.0)],
        280.0,
        (3000.0, 3000.0),
        (0.0, 1.0),
        Some((1.0, 0.0)),
    );
    assert_eq!(f.flanks, vec!['W', 'S']);
    // the west strip begins at the straight run's bed, carried 2.5 ft past the bend
    let west = f
        .strips
        .iter()
        .find(|s| s.iter().all(|p| p.0 <= 1000.0 + 1e-9))
        .unwrap();
    assert!(west.iter().all(|p| p.1 >= 992.5 - 1e-9), "{west:?}");
    assert!(west.iter().any(|p| (p.1 - 992.5).abs() < 1e-9));
}

/// A SQUARE REACH ENDING INSIDE THE STRIP IS BITTEN OUT, AS BEFORE (449 T236): a reach straight out of the foot, 6 ft wide, ending
/// 100 ft out, leaves the foot's strip in one piece notched by its bed - the reeds at each bank and past its end, none on the bed.
#[test]
fn a_square_reach_ending_inside_the_strip_is_bitten_out_of_one_piece() {
    let dike = ring(1000.0, 1000.0, 2000.0, 2000.0);
    let out: [Pt; 2] = [(1500.0, 1990.0), (1500.0, 2100.0)];
    let f = fringe(
        &dike,
        &[(&out, 6.0)],
        280.0,
        (3000.0, 3000.0),
        (0.0, 1.0),
        Some((1.0, 0.0)),
    );
    assert_eq!(f.strips.len(), 2);
    let foot = &f.strips[1];
    let under = |p: Pt| crate::field::geom::inside(p, foot);
    // the bed from x 1497 to 1503 out to y 2103, its banks and its end the notch's sides
    assert!([(1496.5, 2050.0), (1503.5, 2050.0), (1500.0, 2103.5)]
        .iter()
        .all(|&p| under(p)));
    assert!([(1500.0, 2050.0), (1497.5, 2102.5), (1502.5, 2001.0)]
        .iter()
        .all(|&p| !under(p)));
    assert!((area(foot) - (1050.0 * 280.0 - 6.0 * 103.0)).abs() < 1e-6);
}

/// EVERY PASS OVER THE RING COUNTED (449 T236, the work-budget audit's UNCOUNTED): a bed whose box meets a ring but takes nothing
/// walks the ring five times - its sense read (n), each edge asked of the bed's four sides (4n), each corner asked whether it
/// stands within the bed (4n), and the bed's middle asked of the ring (n): 10 tests a corner, 40 for a square.
#[cfg(feature = "counters")]
#[test]
fn a_bed_that_takes_nothing_counts_every_pass_over_the_ring() {
    let square = vec![(0.0, 0.0), (100.0, 0.0), (100.0, 100.0), (0.0, 100.0)];
    // a slanting bed across the square's corner region, its box over the square's, wholly outside the square itself
    let q = [(95.0, 120.0), (120.0, 95.0), (125.0, 100.0), (100.0, 125.0)];
    let mut t = 0;
    assert_eq!(difference(&square, &q, &mut t), vec![square.clone()]);
    assert_eq!(t, 40);
}
