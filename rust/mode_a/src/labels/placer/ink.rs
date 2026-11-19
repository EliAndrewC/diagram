//! Where a leader ends on the ink (feature 449 T193, T194; the Python's `_nearest_ink`, `_part_nearest`, `_outline_corners`, `_join`,
//! `stroke_band`, `_dashes` and `band_nearest` in `labels/placer.py`): the drawn part a leader ends on and its nearest drawn point, a
//! stroke's band as SVG draws it - its caps, its joins and their miter limit, its dashes - and a closed outline's stroked corners. Split
//! from `placer.rs` at the 1,000-line bar (constitution X clause 13).
//!
//! Research: caption search plumbing - NONE: the geometry of the drawn ink, each rule claimed where it is set

use super::super::geom::{bbox, dist, nearest_points, Poly, Pt};
use super::{Cap, InkPart, Join};
use crate::py::{hypot, max};

/// The nearest pair of points, one on the block and one on the drawn parts (the Python's `_nearest_ink`): the part whose drawn edge
/// stands nearest the block, and on it the nearest drawn point (feature 449 T193) - a closed outline, inside it on it, and its own stroke
/// drawn about it at its half-width (`half`, 0 unstroked) with its corners joined as SVG joins them, a stroke's band as SVG draws it
/// ([`band_nearest`]: its edge, its corners' joins, and past its end the end its cap draws) - the ink
/// [`leader_to_ink`](super::hand_sheet::leader_to_ink) ends on - or the block's own point twice where the block reaches the ink; None
/// where no part draws any ink (a stroke of no length ending flat). On an exact tie a closed outline before a stroke, then the wider, then
/// the first in their order.
///
/// Chosen by the stroke's line instead (feature 449 T192), a leader to a stroke drawn along a stroked building's edge ended on the
/// building's outline, inside its own drawn stroke. Two forms of the edge rule were priced by T192 and not kept, each the rule here less a
/// part of the ink it reads (measured 2026-11-18 on the four caption-placing pool sheets, scratchpad t193/variants.log): with round caps
/// assumed and the outline's own stroke left out, a 1 px partition's cap, half a pixel past Ochiba's SERVANTS' QUARTERS' outline where its
/// butt end draws nothing, took the leader and the caption went from ring 4 to ring 20 (t192/why1.log, why2.log); with the caps read but
/// the outline's stroke left out, the 0.8 px dashed roof edge across its passage, 0.4 px past the outline where the outline's 1.5 px
/// stroke reaches 0.75, took it 95.58 px over, under the latrine, which went from ring 0 to ring 3 (t192/reach-band.log,
/// t193/variants.log). With both read, no pool caption moves, and 28 of the 33 leaders its 190 captions draw end 0.3 to 1.25 px
/// shorter, on the drawn stroke (t193/reach-new.log).
///
/// Research:
///     which part a leader ends on - research/questions/0330-how-a-leader-line-ties-a-caption-to-its-feature.drawing.html: it ends at the nearest drawn point - a disc's curve, a stroke's edge, a scattered part - not a box that may hold bare ground; the part chosen by its drawn edge, an outline's own stroke and a stroke's cap and joins read as the sheet draws them (feature 449 T193, T194)
///     a tie between parts - research/questions/0330-how-a-leader-line-ties-a-caption-to-its-feature.drawing.html: where two drawn parts stand exactly as near, the leader goes to a closed outline before a stroke, and to the wider of two strokes; between two like parts equally near, the one drawn first - the page's map drawing convention; the first two decide no pool leader's part, the sheet's order the one of two equal parts equally near, as two posts (feature 449 T192, T193, T194)
#[expect(
    clippy::float_cmp,
    reason = "an exact tie: two parts whose drawn edges stand exactly as near the block"
)]
#[must_use]
pub fn nearest_ink(block: &[Pt], ink: &[InkPart]) -> Option<(Pt, Pt)> {
    let mut best: Option<(f64, bool, f64, Pt, Pt)> = None;
    for part in ink {
        let Some((a, b)) = part_nearest(block, part) else {
            continue;
        };
        let d = dist(a, b);
        // on a tie, an outline before a stroke, then the wider - Python's `(d, (line, -half)) < best`
        let better = best.is_none_or(|(bd, bl, bh, _, _)| {
            d < bd || (d == bd && ((!part.line && bl) || (part.line == bl && part.half > bh)))
        });
        if better {
            best = Some((d, part.line, part.half, a, b));
        }
    }
    best.map(|(_, _, _, a, b)| (a, b))
}

/// How much nearer than the round measure a corner's miter must stand to take a leader (px; the Python's `CORNER_EPS`): a corner level
/// with the outline's drawn edge - a block's edge parallel to it - is as near, and only a rounding apart; it keeps the round measure's
/// point (feature 449 T194: the Ebisu shrine's leader, led to an altar's corner by a rounding, crossed a roof edge).
///
/// Research: its salts, guards and sentinels - NONE: a rounding guard, deciding nothing about the place
pub const CORNER_EPS: f64 = 1e-9;

/// The nearest pair of points, one on the block and one on one drawn part ([`nearest_ink`]; the Python's `_part_nearest`); None where it
/// draws no ink. A closed outline is measured as before (feature 449 T193) - inside it on it, else its outline drawn out round by its
/// stroke's half-width - and then each corner's miter point, which SVG draws past that round corner, is tried ([`outline_corners`]); where
/// a corner bevels, which draws less than the round corner, the outline's whole band is measured ([`band_nearest`]). The round measure
/// first keeps the point it chose among equally near ones - a block's edge parallel to the outline's - where a corner's miter is not
/// nearer.
///
/// Research: a closed outline's drawn edge - research/questions/0330-how-a-leader-line-ties-a-caption-to-its-feature.drawing.html: a leader ends on the ink as it is drawn, on a corner's point; the outline measured round by its stroke and each corner's miter point then tried, its whole band where a corner bevels, so the round measure keeps the point it chose among equally near ones (feature 449 T194)
#[must_use]
pub fn part_nearest(block: &[Pt], part: &InkPart) -> Option<(Pt, Pt)> {
    if part.line {
        return band_nearest(block, part);
    }
    let (a, b) = nearest_points(block, &part.pts, true);
    if a == b || part.half == 0.0 {
        return Some((a, b));
    }
    let (beveled, corners) = outline_corners(part);
    if beveled {
        return band_nearest(block, part);
    }
    let d = dist(a, b);
    if d <= part.half {
        return Some((a, a));
    }
    let mut best = (
        d - part.half,
        a,
        (
            b.0 + (a.0 - b.0) * part.half / d,
            b.1 + (a.1 - b.1) * part.half / d,
        ),
    );
    let (bx0, by0, bx1, by1) = bbox(block);
    for poly in &corners {
        let (cx0, cy0, cx1, cy1) = bbox(poly);
        let gap = hypot(
            max(0.0, max(cx0 - bx1, bx0 - cx1)),
            max(0.0, max(cy0 - by1, by0 - cy1)),
        );
        if gap >= best.0 {
            continue;
        }
        let (a2, b2) = nearest_points(block, poly, true);
        let d2 = dist(a2, b2);
        if d2 < best.0 - CORNER_EPS {
            best = (d2, a2, b2);
        }
    }
    Some(if best.0 == 0.0 {
        (best.1, best.1)
    } else {
        (best.1, best.2)
    })
}

/// A closed outline's stroke's corners as SVG joins them ([`join`]; the Python's `_outline_corners`): whether any bevels, and each
/// miter's polygon.
#[must_use]
pub fn outline_corners(part: &InkPart) -> (bool, Vec<Poly>) {
    let pts = &part.pts;
    let n = pts.len();
    let segs: Vec<(Pt, Pt)> = (0..n)
        .map(|k| (pts[k], pts[(k + 1) % n]))
        .filter(|(a, b)| a != b)
        .collect();
    let dirs: Vec<Pt> = segs.iter().map(|&(a, b)| unit(a, b)).collect();
    let mut corners = Vec::new();
    let mut beveled = false;
    for k in 0..segs.len() {
        let before = dirs[(k + dirs.len() - 1) % dirs.len()];
        match join(segs[k].0, before, dirs[k], part.half, part.join, part.miter) {
            (Some(poly), _) if poly.len() == 3 => beveled = beveled || poly[1] != poly[2],
            (Some(poly), _) => corners.push(poly),
            _ => {}
        }
    }
    (beveled, corners)
}

/// The unit vector from `a` to `b` (they differ).
fn unit(a: Pt, b: Pt) -> Pt {
    let d = dist(a, b);
    ((b.0 - a.0) / d, (b.1 - a.1) / d)
}

/// What SVG draws at a corner of a stroke of half-width `h` where it turns from direction `u1` to `u2` (unit vectors), beyond the two
/// segments' own rectangles (the Python's `_join`): nothing where it runs straight on; a disc of the half-width for a round join; for a
/// miter the two outer edges drawn on until they meet - a point `h / sin(half the angle between the segments)` from the corner - and a
/// bevel joining the two outer corners where that ratio passes the miter limit, as SVG 1.1 draws it (11.4). The polygon, or the disc's
/// center.
///
/// Research: a stroke's corner - research/questions/0330-how-a-leader-line-ties-a-caption-to-its-feature.drawing.html: its corners drawn square to their point, or cut off where they are very sharp, or rounded where the sheet rounds them - SVG 1.1's miter, its bevel past `stroke-miterlimit`, a round join's disc (feature 449 T194)
#[must_use]
pub fn join(p: Pt, u1: Pt, u2: Pt, h: f64, kind: Join, miter: f64) -> (Option<Poly>, Option<Pt>) {
    let cross = u1.0 * u2.1 - u1.1 * u2.0;
    let dot = u1.0 * u2.0 + u1.1 * u2.1;
    if cross == 0.0 && dot > 0.0 {
        return (None, None);
    }
    if kind == Join::Round {
        return (None, Some(p));
    }
    let s = if cross > 0.0 { -h } else { h }; // the outer side: away from the turn
    let (o1, o2) = (
        (p.0 - u1.1 * s, p.1 + u1.0 * s),
        (p.0 - u2.1 * s, p.1 + u2.0 * s),
    );
    let ratio = if dot > -1.0 {
        1.0 / max(0.0, f64::midpoint(1.0, dot)).sqrt()
    } else {
        f64::INFINITY
    };
    if kind == Join::Bevel || ratio > miter {
        return (Some(vec![p, o1, o2]), None);
    }
    let w = hypot(u1.0 - u2.0, u1.1 - u2.1);
    let tip = (
        p.0 + (u1.0 - u2.0) / w * h * ratio,
        p.1 + (u1.1 - u2.1) / w * h * ratio,
    );
    (Some(vec![p, o1, tip, o2]), None)
}

/// A stroke's drawn band as SVG draws it (the Python's `stroke_band`, feature 449 T193, T194): each segment's rectangle at the half-width,
/// at each corner its join ([`join`]: a miter, its bevel past the miter limit, a round join's disc), and at each end its cap - nothing for
/// butt (SVG's default: the stroke ends flat at its end point), the end segment's rectangle drawn on past it by the half-width for square,
/// a disc for round. A closed outline's stroke, or a stroke a path's `Z` closed, runs all the way round, a join at every corner and no cap;
/// a dashed stroke is its dashes ([`dashes`]), each drawn so. The polygons and the discs' centers; a stroke of no length draws its cap
/// alone - nothing for butt, a disc for round, a level square for square (SVG 2, 13.5.5).
///
/// Research: a stroke's drawn band - research/questions/0330-how-a-leader-line-ties-a-caption-to-its-feature.drawing.html: a leader ends on the ink as it is drawn: on a corner's point, on a line's end, and never in a dashed line's gap - the page's map drawing convention; a stroke's band as SVG draws it, its `stroke-linecap`, `stroke-linejoin`, `stroke-miterlimit` and `stroke-dasharray` read (SVG's defaults butt, miter, 4 and solid unless the sheet says otherwise) (feature 449 T193, T194)
#[must_use]
pub fn stroke_band(part: &InkPart) -> (Vec<Poly>, Vec<Pt>) {
    if part.line && !part.dash.is_empty() {
        let (mut polys, mut discs) = (Vec::new(), Vec::new());
        for piece in dashes(part) {
            let (p2, d2) = stroke_band(&InkPart {
                pts: piece,
                closed: false,
                dash: Vec::new(),
                ..part.clone()
            });
            polys.extend(p2);
            discs.extend(d2);
        }
        return (polys, discs);
    }
    let ring = !part.line || part.closed;
    let mut pts = part.pts.clone();
    if part.line && part.closed && pts.len() > 1 && pts.first() == pts.last() {
        pts.pop();
    }
    let closing = if ring { pts.first().copied() } else { None };
    let segs: Vec<(Pt, Pt)> = pts
        .iter()
        .copied()
        .zip(pts.iter().skip(1).copied().chain(closing))
        .filter(|(a, b)| a != b)
        .collect();
    let h = part.half;
    if segs.is_empty() {
        let p = pts[0];
        return match (ring, part.cap) {
            (true, _) | (false, Cap::Butt) => (Vec::new(), Vec::new()),
            (false, Cap::Round) => (Vec::new(), vec![p]),
            (false, Cap::Square) => (
                vec![vec![
                    (p.0 - h, p.1 - h),
                    (p.0 + h, p.1 - h),
                    (p.0 + h, p.1 + h),
                    (p.0 - h, p.1 + h),
                ]],
                Vec::new(),
            ),
        };
    }
    let (last, square) = (segs.len() - 1, !ring && part.cap == Cap::Square);
    let dirs: Vec<Pt> = segs.iter().map(|&(a, b)| unit(a, b)).collect();
    let mut polys: Vec<Poly> = segs
        .iter()
        .enumerate()
        .map(|(k, &(a, b))| {
            let (ux, uy) = dirs[k];
            let e0 = if k == 0 && square { h } else { 0.0 };
            let e1 = if k == last && square { h } else { 0.0 };
            let (a, b) = (
                (a.0 - ux * e0, a.1 - uy * e0),
                (b.0 + ux * e1, b.1 + uy * e1),
            );
            let (nx, ny) = (-uy * h, ux * h);
            vec![
                (a.0 + nx, a.1 + ny),
                (b.0 + nx, b.1 + ny),
                (b.0 - nx, b.1 - ny),
                (a.0 - nx, a.1 - ny),
            ]
        })
        .collect();
    let mut discs = Vec::new();
    for k in usize::from(!ring)..segs.len() {
        let before = dirs[(k + dirs.len() - 1) % dirs.len()];
        let (poly, disc) = join(segs[k].0, before, dirs[k], h, part.join, part.miter);
        polys.extend(poly);
        discs.extend(disc);
    }
    if !ring && part.cap == Cap::Round {
        discs.extend([segs[0].0, segs[last].1]);
    }
    (polys, discs)
}

/// A dashed stroke's dashes, each the run of its polyline a dash covers (the Python's `_dashes`, SVG 1.1, 11.4): the pattern laid along
/// the stroke from its start, `offset` into it, and round again from its start where a path's `Z` closed it; a dash of no length is its one
/// point, which draws only a round or square cap.
///
/// Research: a dashed stroke's dashes - research/questions/0330-how-a-leader-line-ties-a-caption-to-its-feature.drawing.html: never in a dashed line's gap - the pattern laid from the stroke's start and its `stroke-dashoffset`, each dash a stroke of its own with the stroke's caps (feature 449 T194)
#[must_use]
pub fn dashes(part: &InkPart) -> Vec<Vec<Pt>> {
    let pts = &part.pts;
    let period: f64 = part.dash.iter().sum();
    let (mut at_dash, mut into) = (0, part.offset.rem_euclid(period));
    while into >= part.dash[at_dash] {
        into -= part.dash[at_dash];
        at_dash = (at_dash + 1) % part.dash.len();
    }
    let mut out = Vec::new();
    let mut cur: Option<Vec<Pt>> = (at_dash % 2 == 0).then(|| vec![pts[0]]);
    let mut left = part.dash[at_dash] - into;
    for w in pts.windows(2) {
        let (from, to) = (w[0], w[1]);
        let seg = dist(from, to);
        let mut along = 0.0;
        while seg - along >= left {
            along += left;
            let t = if seg == 0.0 { 0.0 } else { along / seg };
            let p = (from.0 + (to.0 - from.0) * t, from.1 + (to.1 - from.1) * t);
            if let Some(mut c) = cur.take() {
                c.push(p);
                out.push(c);
            } else {
                cur = Some(vec![p]);
            }
            at_dash = (at_dash + 1) % part.dash.len();
            left = part.dash[at_dash];
        }
        left -= seg - along;
        if let Some(c) = cur.as_mut() {
            if c.last() != Some(&to) {
                c.push(to);
            }
        }
    }
    out.extend(cur);
    out
}

/// The nearest pair of points, one on the block and one on a stroke's drawn band ([`stroke_band`]), the block's own point twice where the
/// block reaches the band (the Python's `band_nearest`, feature 449 T193): a leader to a stroke ends at its edge, at a corner on the join
/// SVG draws, and past its end on the end its cap draws; None where the stroke draws nothing (one of no length ending flat).
#[must_use]
pub fn band_nearest(block: &[Pt], part: &InkPart) -> Option<(Pt, Pt)> {
    let (polys, discs) = stroke_band(part);
    let mut best: Option<(f64, Pt, Pt)> = None;
    for r in &polys {
        let (a, b) = nearest_points(block, r, true);
        let d = dist(a, b);
        if best.is_none_or(|x| d < x.0) {
            best = Some((d, a, b));
        }
    }
    for &c in &discs {
        let (a, _) = nearest_points(block, &[c], false);
        let dc = dist(a, c);
        let d = max(0.0, dc - part.half);
        if best.is_none_or(|x| d < x.0) {
            let b = if d == 0.0 {
                a
            } else {
                (
                    c.0 + (a.0 - c.0) * part.half / dc,
                    c.1 + (a.1 - c.1) * part.half / dc,
                )
            };
            best = Some((d, a, b));
        }
    }
    let (d, a, b) = best?;
    Some(if d == 0.0 { (a, a) } else { (a, b) })
}
