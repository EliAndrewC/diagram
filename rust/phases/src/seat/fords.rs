//! The brook's fords (feature 444 T27 D4): the places along the brook's course where a way may cross it, on its straight reaches
//! at their spacing, and the streams' segments gapped at each, so every later way is routed over the brook there and nowhere else.
//!
//! Research:
//!     the fords - NONE: the seat's machinery; each rule's claim is at the unit that keeps it

#![expect(
    clippy::many_single_char_names,
    reason = "the plane geometry's own names"
)]
use std::collections::HashMap;

use super::index::{Cells, CELL};
use super::tally;
use crate::field::fan::Pt;
use crate::field::geom::dist;

/// The point `d` along a course of `legs` (each its start, end and length; `before[k]` the length of the legs before leg `k`) and
/// the unit along the leg it lies on, the leg found by bisection; a point past the end is the last leg's far end.
fn at(legs: &[(Pt, Pt, f64)], before: &[f64], d: f64) -> (Pt, Pt) {
    let k = before
        .partition_point(|&r| r < d)
        .saturating_sub(1)
        .min(legs.len() - 1);
    let (a, b, n) = legs[k];
    let t = ((d - before[k]) / n).clamp(0.0, 1.0);
    (
        (a.0 + (b.0 - a.0) * t, a.1 + (b.1 - a.1) * t),
        ((b.0 - a.0) / n, (b.1 - a.1) / n),
    )
}

/// The fords along `brook`: points every `spacing` along its course, starting half a spacing in, where it runs straight for the
/// crossing's length either side - the turn between the reaches `half` behind and `half` ahead under `bend_deg` - so a way
/// crossing there crosses it square and lands on both banks. A bend is skipped, not moved: the next place is `spacing` on.
///
/// Research:
///     crossing places along the brook - research/questions/0035-villages-beside-their-stream-one-bank-or-both.drawing.html: a way crosses the brook only at a crossing place; every `spacing` along it (Python's `FORD_SPACING`, its claim there)
///     only on a straight reach - research/questions/0035-villages-beside-their-stream-one-bank-or-both.drawing.html: a bend skipped, so the crossing is square (Python's `FORD_BEND_DEG`, its claim there)
pub fn fords(
    brook: &[Pt],
    spacing: f64,
    half: f64,
    bend_deg: f64,
    counts: &mut HashMap<String, u64>,
) -> Vec<Pt> {
    let legs: Vec<(Pt, Pt, f64)> = brook
        .windows(2)
        .map(|w| (w[0], w[1], dist(w[0], w[1])))
        .filter(|l| l.2 > 0.0)
        .collect();
    tally(counts, "read@brook_course", brook.len() as u64);
    let mut before = Vec::with_capacity(legs.len());
    let mut total = 0.0;
    for l in &legs {
        before.push(total);
        total += l.2;
    }
    let mut out = Vec::new();
    let mut d = spacing / 2.0;
    let mut tests = 0;
    while !legs.is_empty() && d + half < total && d - half > 0.0 {
        tests += 3;
        let (c, _u) = at(&legs, &before, d);
        let (_p, u0) = at(&legs, &before, d - half);
        let (_q, u1) = at(&legs, &before, d + half);
        if (u0.0 * u1.0 + u0.1 * u1.1)
            .clamp(-1.0, 1.0)
            .acos()
            .to_degrees()
            < bend_deg
        {
            out.push(c);
        }
        d += spacing;
    }
    tally(
        counts,
        "test@fords",
        tests * (u64::from((legs.len() as u64).max(1).ilog2()) + 1),
    );
    tally(counts, "write@fords", out.len() as u64);
    out
}

/// The streams' segments with every stretch within `half` of a ford cut out, the pieces either side kept.
///
/// Research:
///     the brook crossed only at a ford - research/questions/0035-villages-beside-their-stream-one-bank-or-both.drawing.html: a way crosses the brook only at a crossing place, the stream's segments gapped at each
///     the crossing place's length - UNRESEARCHED: 0035 sets the places and their spacing, not their length; a 60 ft gap, `half` either side (Python's `FORD_HALF`), so a deck crossing near square lands on both banks
pub fn gapped(
    streams: &[Vec<Pt>],
    fords: &[Pt],
    half: f64,
    counts: &mut HashMap<String, u64>,
) -> Vec<(Pt, Pt)> {
    let mut near = Cells::new(CELL);
    for (i, &f) in fords.iter().enumerate() {
        near.file(i, &[f]);
    }
    let mut out = Vec::new();
    let mut tests = 0;
    for (a, b) in streams
        .iter()
        .flat_map(|c| c.windows(2).map(|w| (w[0], w[1])))
    {
        // a segment is cut only by the fords within `half` of it: those filed in the cells its box grown by `half` covers, in
        // their order along the brook, each cutting the pieces the ones before it left
        let lo = (a.0.min(b.0) - half, a.1.min(b.1) - half);
        let hi = (a.0.max(b.0) + half, a.1.max(b.1) + half);
        let (mut by, read) = near.in_box(lo, hi);
        by.sort_unstable();
        tests += read;
        let mut pieces = vec![(a, b)];
        for i in by {
            tests += 1;
            pieces = pieces
                .into_iter()
                .flat_map(|(p, q)| cut(p, q, fords[i], half))
                .collect();
        }
        out.extend(pieces);
    }
    tally(counts, "test@gaps", tests);
    tally(counts, "write@watercourses", out.len() as u64);
    out
}

/// The segment `a`-`b` with its stretch within `half` of `c` cut out: the pieces either side, or the segment whole.
fn cut(a: Pt, b: Pt, c: Pt, half: f64) -> Vec<(Pt, Pt)> {
    let (dx, dy) = (b.0 - a.0, b.1 - a.1);
    let n2 = dx * dx + dy * dy;
    let t = if n2 > 0.0 {
        ((c.0 - a.0) * dx + (c.1 - a.1) * dy) / n2
    } else {
        0.0
    };
    let (px, py) = (a.0 + dx * t, a.1 + dy * t);
    let d2 = (c.0 - px).powi(2) + (c.1 - py).powi(2);
    if n2 == 0.0 || d2 >= half * half {
        return vec![(a, b)];
    }
    let w = (half * half - d2).sqrt() / n2.sqrt();
    let (t0, t1) = (t - w, t + w);
    let mut out = Vec::new();
    if t0 > 0.0 {
        out.push((a, (a.0 + dx * t0.min(1.0), a.1 + dy * t0.min(1.0))));
    }
    if t1 < 1.0 {
        out.push(((a.0 + dx * t1.max(0.0), a.1 + dy * t1.max(0.0)), b));
    }
    out
}
