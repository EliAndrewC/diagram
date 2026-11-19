//! Where a leader line runs (feature 449 T202; research/questions/0330-how-a-leader-line-ties-a-caption-to-its-feature.drawing.html):
//! from the caption's block to the nearest drawn point of what it names - a disc's curve, a stroke's edge, an outline's ink - ending on
//! the ink as it is drawn, never in a dashed line's gap, a closed outline taken before a stroke and the wider stroke before the thinner
//! where two stand exactly as near.
//!
//! Research: the leader's end - research/questions/0330-how-a-leader-line-ties-a-caption-to-its-feature.drawing.html: a leader ends at the nearest drawn point of its feature's own parts, on the ink as drawn, never in a dash's gap

#![expect(
    clippy::many_single_char_names,
    reason = "geometry's points, boxes and sizes as the derivation names them: a, b, c, d, p, q, w, h"
)]

use super::geom::{block, dist, nearest_on, path, ring, seg_pair, Pt};
use super::Shape;
use crate::labels::hand_sheet::Cap;
use crate::work_counts::count;

/// The least number of points a turned or unequal disc's curve is sampled at.
///
/// Research: a disc's samples - NONE: at least 16 points, and as many as keep each chord within 0.05 px of the curve (the reader's sag), a drawing tolerance
pub const DISC_MIN_SAMPLES: usize = 16;

/// How far inside a drawn curve a sampled chord may stand.
///
/// Research: the curve's sag - CONVENTION: 0.05 px, the sheet reader's flattening tolerance (feature 449 T195); a drawn size on the sheet, not in the world
pub const SAG_PX: f64 = 0.05;

/// One candidate end: how far it stands, whether it is a stroke (a closed outline wins a tie), the stroke's half-width (the wider wins),
/// the part's order (the first drawn wins), the end on the ink and the start on the block.
type End = (f64, bool, f64, usize, Pt, Pt);

/// Two ends compared as 0330 orders them: the nearer, then a closed outline before a stroke, then the wider stroke, then the first drawn.
fn better(a: &End, b: &End) -> bool {
    let tie = (a.0 - b.0).abs() <= 1e-6;
    if !tie {
        return a.0 < b.0;
    }
    (a.1, -a.2, a.3) < (b.1, -b.2, b.3)
}

/// The block's nearest point to the segment `cd`, and the segment's nearest point to it.
fn block_pair(quad: &[Pt; 4], c: Pt, d: Pt) -> (Pt, Pt) {
    ring(quad)
        .map(|(a, b)| seg_pair(a, b, c, d))
        .min_by(|x, y| dist(x.0, x.1).total_cmp(&dist(y.0, y.1)))
        .unwrap_or((c, c))
}

/// `q` moved `by` toward `p`, not past it.
fn toward(q: Pt, p: Pt, by: f64) -> Pt {
    let d = dist(p, q);
    if d <= 0.0 {
        return q;
    }
    let t = by.min(d) / d;
    (q.0 + (p.0 - q.0) * t, q.1 + (p.1 - q.1) * t)
}

/// The point at arc length `s` along a polyline.
fn at_length(poly: &[Pt], s: f64) -> Pt {
    let mut left = s.max(0.0);
    for (a, b) in path(poly) {
        let l = dist(a, b);
        if left <= l && l > 0.0 {
            return (a.0 + (b.0 - a.0) * left / l, a.1 + (b.1 - a.1) * left / l);
        }
        left -= l;
    }
    poly[poly.len() - 1]
}

/// Where along a dash pattern an arc length falls: `None` on a dash, else the gap's bounds as arc lengths. A list of odd length is
/// read as SVG reads it, repeated to an even length (the sheet reader already hands one so; a caller handing the odd list gets the same answer).
///
/// Research: dashes - research/questions/0330-how-a-leader-line-ties-a-caption-to-its-feature.drawing.html: a dashed line is measured as its dashes alone, since a gap holds no ink; the dash list read as SVG reads it, an odd one repeated to an even length
#[must_use]
pub fn dash_gap(s: f64, dash: &[f64], offset: f64) -> Option<(f64, f64)> {
    let doubled;
    let dash = if dash.len() % 2 == 1 {
        doubled = [dash, dash].concat();
        doubled.as_slice()
    } else {
        dash
    };
    let period: f64 = dash.iter().sum();
    if dash.is_empty() || period <= 0.0 {
        return None;
    }
    let pos = (s + offset).rem_euclid(period);
    let start = s - pos;
    let mut at = 0.0;
    let mut i = 0;
    while i + 1 < dash.len() && pos >= at + dash[i] {
        at += dash[i];
        i += 1;
    }
    (i % 2 == 1).then_some((start + at, start + at + dash[i]))
}

/// The nearest end on a stroke: its segments' nearest point (`shape_distance`, one a segment), moved off a dash's gap to the nearer
/// dash end, then out to the band's edge - flat at a butt end, as the sheet draws it.
fn stroke_end(quad: &[Pt; 4], s: &Shape) -> (f64, Pt, Pt) {
    let half = s.half.max(super::index::MIN_HALF_PX);
    // (centerline distance, on block, on line, arc length): a stroke has a segment, so the first replaces this
    let mut best: (f64, Pt, Pt, f64) = (f64::INFINITY, (0.0, 0.0), (0.0, 0.0), 0.0);
    let mut walked = 0.0;
    for (a, b) in path(&s.poly) {
        count("shape_distance@leader", 1);
        let (p, q) = block_pair(quad, a, b);
        let d = dist(p, q);
        let (_, t) = nearest_on(q, a, b);
        if d < best.0 {
            best = (d, p, q, walked + t * dist(a, b));
        }
        walked += dist(a, b);
    }
    let (_, mut p, mut q, s_at) = best;
    if let Some((g0, g1)) = dash_gap(s_at, &s.dash, s.offset) {
        let ends = [
            at_length(&s.poly, g0.max(0.0)),
            at_length(&s.poly, g1.min(walked)),
        ];
        q = ends
            .into_iter()
            .min_by(|x, y| dist(p, *x).total_cmp(&dist(p, *y)))
            .unwrap_or(q);
        p = block_pair(quad, q, q).0;
    }
    let ended = s_at <= 1e-9 || s_at >= walked - 1e-9;
    let end = if ended && matches!(s.cap, Cap::Butt) {
        // the flat end: only the part of the step to the block across the line reaches ink
        let (a, b) = if s_at <= 1e-9 {
            (s.poly[0], s.poly[1])
        } else {
            (s.poly[s.poly.len() - 1], s.poly[s.poly.len() - 2])
        };
        let l = dist(a, b).max(1e-12);
        let (ux, uy) = ((b.0 - a.0) / l, (b.1 - a.1) / l);
        let (vx, vy) = (p.0 - q.0, p.1 - q.1);
        let along = vx * ux + vy * uy;
        let (nx, ny) = (vx - along * ux, vy - along * uy);
        let n = nx.hypot(ny);
        if n > 0.0 {
            (q.0 + nx / n * half.min(n), q.1 + ny / n * half.min(n))
        } else {
            q
        }
    } else {
        toward(q, p, half)
    };
    (dist(p, end), block_pair(quad, end, end).0, end)
}

/// The nearest end on a closed outline: its drawn edge (a disc's curve), out by the stroke drawn on it.
fn outline_end(quad: &[Pt; 4], s: &Shape) -> (f64, Pt, Pt) {
    let disc = (s.tag == "circle" || s.tag == "ellipse") && s.poly.len() == 4;
    let pts: Vec<Pt> = if disc {
        let (p0, p1, p3) = (s.poly[0], s.poly[1], s.poly[3]);
        let c = (
            f64::midpoint(p0.0, s.poly[2].0),
            f64::midpoint(p0.1, s.poly[2].1),
        );
        let (u, v) = (
            ((p1.0 - p0.0) / 2.0, (p1.1 - p0.1) / 2.0),
            ((p3.0 - p0.0) / 2.0, (p3.1 - p0.1) / 2.0),
        );
        let (ru, rv) = (u.0.hypot(u.1), v.0.hypot(v.1));
        if (ru - rv).abs() < 1e-9 {
            // a circle: its nearest point straight from the center toward the block's nearest point to the center
            count("shape_distance@leader", 1);
            let p = block_pair(quad, c, c).0;
            let q = toward(c, p, ru);
            let end = toward(q, p, s.edge);
            return (dist(p, end), p, end);
        }
        let r = ru.max(rv);
        #[expect(
            clippy::cast_possible_truncation,
            clippy::cast_sign_loss,
            reason = "a positive sample count"
        )]
        let n = ((std::f64::consts::PI / (1.0 - SAG_PX / r).clamp(-1.0, 1.0).acos()).ceil()
            as usize)
            .max(DISC_MIN_SAMPLES);
        (0..n)
            .map(|k| {
                #[expect(clippy::cast_precision_loss, reason = "a sample index")]
                let t = 2.0 * std::f64::consts::PI * k as f64 / n as f64;
                (
                    c.0 + t.cos() * u.0 + t.sin() * v.0,
                    c.1 + t.cos() * u.1 + t.sin() * v.1,
                )
            })
            .collect()
    } else {
        s.poly.clone()
    };
    // an outline has an edge, so the first replaces this
    let mut best: (f64, Pt, Pt) = (f64::INFINITY, (0.0, 0.0), (0.0, 0.0));
    for (a, b) in ring(&pts) {
        count("shape_distance@leader", 1);
        let (p, q) = block_pair(quad, a, b);
        if dist(p, q) < best.0 {
            best = (dist(p, q), p, q);
        }
    }
    let (_, p, q) = best;
    let end = toward(q, p, s.edge);
    (dist(p, end), p, end)
}

/// The leader from a block (`c`, `w` x `h` at `deg`) to the nearest drawn point of its feature's parts: `(start on the block, end on the
/// ink)`, or `None` where the parts draw nothing.
///
/// Research:
///     the nearest drawn point - research/questions/0330-how-a-leader-line-ties-a-caption-to-its-feature.drawing.html: it ends at the nearest drawn point, not a box that may hold bare ground
///     the tie order - research/questions/0330-how-a-leader-line-ties-a-caption-to-its-feature.drawing.html: a closed outline before a stroke, the wider of two strokes, the one drawn first
///     a butt end - research/questions/0330-how-a-leader-line-ties-a-caption-to-its-feature.drawing.html: its ends flat, squared off or round as drawn; a butt end is flat, a square or round one read as round (CONVENTION of this placer: a square cap's corner is within half a stroke of its round reading)
#[must_use]
pub fn leader(
    c: Pt,
    (w, h, deg): (f64, f64, f64),
    shapes: &[Shape],
    parts: &[usize],
) -> Option<(Pt, Pt)> {
    let quad = block(c, w, h, deg);
    let mut best: Option<End> = None;
    for (order, &i) in parts.iter().enumerate() {
        let s = &shapes[i];
        let found = if s.line {
            if s.poly.len() < 2 {
                continue;
            }
            let (d, p, q) = stroke_end(&quad, s);
            (d, true, s.half, order, q, p)
        } else {
            if s.poly.len() < 3 {
                continue;
            }
            let (d, p, q) = outline_end(&quad, s);
            (d, false, 0.0, order, q, p)
        };
        if best.as_ref().is_none_or(|b| better(&found, b)) {
            best = Some(found);
        }
    }
    best.map(|e| (e.5, e.4))
}

#[cfg(test)]
mod tests {
    use super::{dash_gap, leader};
    use crate::caption_place::Shape;
    use crate::labels::hand_sheet::Cap;

    fn stroke(pts: Vec<(f64, f64)>, half: f64) -> Shape {
        Shape {
            poly: pts,
            line: true,
            half,
            cap: Cap::of("round").unwrap_or(Cap::Butt),
            tag: "line".to_owned(),
            ..Shape::default()
        }
    }

    fn outline(tag: &str, pts: Vec<(f64, f64)>, edge: f64) -> Shape {
        Shape {
            poly: pts,
            tag: tag.to_owned(),
            edge,
            filled: true,
            ..Shape::default()
        }
    }

    /// 0330: a dashed line is measured as its dashes alone.
    #[test]
    fn a_dashes_gap_holds_no_ink() {
        assert_eq!(dash_gap(3.0, &[4.0, 2.0], 0.0), None);
        assert_eq!(dash_gap(5.0, &[4.0, 2.0], 0.0), Some((4.0, 6.0)));
        assert_eq!(dash_gap(11.0, &[4.0, 2.0], 0.0), Some((10.0, 12.0)));
        assert_eq!(dash_gap(1.0, &[4.0, 2.0], 4.0), Some((0.0, 2.0)));
        assert_eq!(dash_gap(1.0, &[], 0.0), None);
        assert_eq!(dash_gap(1.0, &[0.0, 0.0], 0.0), None);
    }

    /// 0330, a dash list of odd length read as SVG reads it: the list repeated to an even length, so `3` is a dash of 3 and a gap of
    /// 3, and `4 2 1` the dashes 4, 1, 2 and the gaps 2, 4, 1 - never a stroke of solid ink.
    #[test]
    fn an_odd_dash_list_is_repeated_to_an_even_one() {
        assert_eq!(dash_gap(1.0, &[3.0], 0.0), None);
        assert_eq!(dash_gap(4.0, &[3.0], 0.0), Some((3.0, 6.0)));
        assert_eq!(dash_gap(7.0, &[3.0], 0.0), None);
        assert_eq!(dash_gap(5.0, &[4.0, 2.0, 1.0], 0.0), Some((4.0, 6.0)));
        assert_eq!(dash_gap(6.5, &[4.0, 2.0, 1.0], 0.0), None);
        assert_eq!(dash_gap(8.0, &[4.0, 2.0, 1.0], 0.0), Some((7.0, 11.0)));
        assert_eq!(dash_gap(12.0, &[4.0, 2.0, 1.0], 0.0), None);
        assert_eq!(dash_gap(13.5, &[4.0, 2.0, 1.0], 0.0), Some((13.0, 14.0)));
        assert_eq!(dash_gap(1.0, &[3.0], 3.0), Some((0.0, 3.0)));
    }

    /// 0330: a leader to a dashed line ends on a dash, never in a gap.
    #[test]
    fn a_leader_never_ends_in_a_dash_gap() {
        // dashes of 4 then gaps of 4 from x = 0: the point under the block (x = 6) is in a gap, so the leader ends on a dash end
        let mut s = stroke(vec![(0.0, 0.0), (40.0, 0.0)], 0.5);
        s.dash = vec![4.0, 4.0];
        let (_, end) = leader((6.0, 20.0), (2.0, 2.0, 0.0), &[s], &[0]).unwrap();
        assert!((end.0 - 4.0).abs() < 0.1 || (end.0 - 8.0).abs() < 0.1);
    }

    /// 0330: equally near, a closed outline is taken before a stroke, and the wider stroke before the thinner.
    #[test]
    fn ties_go_to_a_closed_outline_then_the_wider_stroke() {
        // a block above a stroke and an outline whose ink both stands 9 px below it
        let line = stroke(vec![(0.0, 10.0), (10.0, 10.0)], 1.0);
        let rect = outline(
            "rect",
            vec![(40.0, 9.0), (50.0, 9.0), (50.0, 12.0), (40.0, 12.0)],
            0.0,
        );
        let (_, end) = leader(
            (25.0, -1.0),
            (60.0, 2.0, 0.0),
            &[line.clone(), rect],
            &[0, 1],
        )
        .unwrap();
        assert!(end.0 >= 40.0, "the outline first: {end:?}");
        // two strokes whose ink both stands 1 px below the block, the wider second
        let wide = stroke(vec![(20.0, 11.0), (30.0, 11.0)], 2.0);
        let (_, end) = leader((15.0, 7.0), (40.0, 2.0, 0.0), &[line, wide], &[0, 1]).unwrap();
        assert!(end.0 >= 20.0, "the wider stroke: {end:?}");
    }

    /// 0330: a leader ends on the ink as drawn - a disc's curve, a stroke's flat butt end, an outline out by its stroke.
    #[test]
    fn a_leader_ends_on_the_ink_as_drawn() {
        let disc = outline(
            "circle",
            vec![(-5.0, -5.0), (5.0, -5.0), (5.0, 5.0), (-5.0, 5.0)],
            0.0,
        );
        let (_, end) = leader((0.0, 30.0), (4.0, 2.0, 0.0), &[disc], &[0]).unwrap();
        assert!((end.1 - 5.0).abs() < 1e-6 && end.0.abs() < 1e-6, "{end:?}");
        let oval = outline(
            "ellipse",
            vec![(-10.0, -5.0), (10.0, -5.0), (10.0, 5.0), (-10.0, 5.0)],
            1.0,
        );
        let (_, end) = leader((0.0, 30.0), (4.0, 2.0, 0.0), &[oval], &[0]).unwrap();
        assert!((end.1 - 6.0).abs() < 0.1, "out by the stroke: {end:?}");
        let mut butt = stroke(vec![(0.0, 0.0), (10.0, 0.0)], 2.0);
        butt.cap = Cap::Butt;
        let (_, end) = leader((30.0, 3.0), (2.0, 2.0, 0.0), &[butt.clone()], &[0]).unwrap();
        assert!((end.0 - 10.0).abs() < 1e-6 && (end.1 - 2.0).abs() < 1e-6);
        let (_, end) = leader((30.0, 0.0), (2.0, 2.0, 0.0), &[butt.clone()], &[0]).unwrap();
        assert!((end.0 - 10.0).abs() < 1e-6, "straight on its end: {end:?}");
        let (_, end) = leader((-30.0, 1.0), (2.0, 2.0, 0.0), &[butt], &[0]).unwrap();
        assert!(end.0.abs() < 1e-6, "its first end: {end:?}");
        let rect = outline(
            "rect",
            vec![(0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0)],
            1.0,
        );
        let (_, end) = leader((5.0, 30.0), (2.0, 2.0, 0.0), &[rect], &[0]).unwrap();
        assert!((end.1 - 11.0).abs() < 1e-6, "{end:?}");
    }

    /// The nearest of several parts, along a stroke of several segments, past its dashes; a block already touching its ink.
    #[test]
    fn the_nearest_part_and_segment_win() {
        let far = stroke(vec![(0.0, 50.0), (10.0, 50.0)], 0.5);
        let mut bent = stroke(vec![(0.0, 0.0), (10.0, 0.0), (10.0, 10.0)], 0.5);
        bent.dash = vec![3.0, 1.0];
        let (_, end) = leader((20.0, 8.0), (4.0, 2.0, 0.0), &[far, bent.clone()], &[0, 1]).unwrap();
        assert!((end.0 - 10.5).abs() < 0.1, "{end:?}");
        let (start, end) = leader((10.0, 12.0), (4.0, 4.0, 0.0), &[bent.clone()], &[0]).unwrap();
        assert_eq!(start, end, "touching: no length");
        assert_eq!(super::at_length(&bent.poly, 100.0), (10.0, 10.0));
        let far = stroke(vec![(0.0, 50.0), (10.0, 50.0)], 0.5);
        let (_, end) = leader((20.0, 8.0), (4.0, 2.0, 0.0), &[bent, far], &[0, 1]).unwrap();
        assert!((end.0 - 10.5).abs() < 0.1);
    }

    /// Parts that draw nothing give no leader.
    #[test]
    fn parts_that_draw_nothing_give_no_leader() {
        let dot = stroke(vec![(0.0, 0.0)], 1.0);
        let flat = outline("polygon", vec![(0.0, 0.0), (1.0, 0.0)], 0.0);
        assert_eq!(
            leader((0.0, 10.0), (2.0, 2.0, 0.0), &[dot, flat], &[0, 1]),
            None
        );
    }
}
