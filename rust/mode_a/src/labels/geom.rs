//! Plain geometry for the placer (feature 449 T151, `labels/geom.py` whole): convex polygons and segments as tuples, owned by neither
//! mode. Every measure is the Python's in its order of operations - `math.dist` and `math.hypot` as `CPython`'s `vector_norm`
//! ([`crate::py::hypot`]), `sum()` compensated ([`crate::py::sum`]), `min` and `max` the first - so a seat the Python measured free is free
//! here: the hand sheet's captions land where they did wherever no shapely call stands between (the port's comparison,
//! `parse/lockstep_labels.rs`).
//!
//! LOCKSTEP (`ask:449-engine-order` condition 3, as the GM's 2026-11-17 rule for a drawn sheet amends it): `geom.py` stays for its Python
//! importers (`compound.py`, `compound_view.py`) until step 3b; an edit of it makes the same change here in the same commit.
//!
//! Research: geometry - NONE: polygon and segment measures

#![expect(
    clippy::similar_names,
    reason = "the Python's names, kept so each line reads against its original (x0 and x1, bx0 and by0)"
)]

use crate::py::{hypot, max, min, sum};

/// A point.
pub type Pt = (f64, f64);

/// A polygon or polyline, its vertices in order.
pub type Poly = Vec<Pt>;

/// A box: `(x0, y0, x1, y1)`.
pub type BBox = (f64, f64, f64, f64);

/// `math.dist(p, q)`.
#[must_use]
pub fn dist(p: Pt, q: Pt) -> f64 {
    hypot(p.0 - q.0, p.1 - q.1)
}

/// A rectangle of half-extents `(hw, hh)` centered at `(cx, cy)`, turned by `angle` degrees about its center.
#[must_use]
pub fn rect(cx: f64, cy: f64, hw: f64, hh: f64, angle: f64) -> Poly {
    let (ca, sa) = (angle.to_radians().cos(), angle.to_radians().sin());
    [(-hw, -hh), (hw, -hh), (hw, hh), (-hw, hh)]
        .iter()
        .map(|&(dx, dy)| (cx + dx * ca - dy * sa, cy + dx * sa + dy * ca))
        .collect()
}

/// The box of the vertices: each extreme the first of its value, as Python's `min` and `max` take it.
///
/// # Panics
/// An outline of no vertex, which Python's `min` refused too.
#[must_use]
pub fn bbox(poly: &[Pt]) -> BBox {
    let (x, y) = poly[0];
    poly[1..]
        .iter()
        .fold((x, y, x, y), |(x0, y0, x1, y1), &(px, py)| {
            (min(x0, px), min(y0, py), max(x1, px), max(y1, py))
        })
}

/// The mean of the vertices - a center, not the area centroid; enough to say which side of a subject is which.
#[must_use]
#[expect(clippy::cast_precision_loss, reason = "Python's `len()` as a float")]
pub fn centroid(poly: &[Pt]) -> Pt {
    let n = poly.len() as f64;
    (
        sum(poly.iter().map(|p| p.0)) / n,
        sum(poly.iter().map(|p| p.1)) / n,
    )
}

/// The closing edges of a ring: each vertex with the next, the last with the first.
pub(crate) fn ring_edges(poly: &[Pt]) -> impl Iterator<Item = (Pt, Pt)> + '_ {
    poly.iter()
        .zip(poly.iter().skip(1).chain(poly.first()))
        .map(|(&a, &b)| (a, b))
}

/// The open edges of a polyline: each vertex with the next.
pub(crate) fn open_edges(poly: &[Pt]) -> impl Iterator<Item = (Pt, Pt)> + '_ {
    poly.windows(2).map(|w| (w[0], w[1]))
}

/// The area centroid of a simple polygon; the vertex mean for a degenerate one.
#[must_use]
pub fn area_centroid(poly: &[Pt]) -> Pt {
    let (mut a, mut cx, mut cy) = (0.0, 0.0, 0.0);
    for ((x0, y0), (x1, y1)) in ring_edges(poly) {
        let c = x0 * y1 - x1 * y0;
        a += c;
        cx += (x0 + x1) * c;
        cy += (y0 + y1) * c;
    }
    if a.abs() < 1e-9 {
        return centroid(poly);
    }
    (cx / (3.0 * a), cy / (3.0 * a))
}

/// Ray-cast point-in-polygon.
#[must_use]
pub fn inside(x: f64, y: f64, poly: &[Pt]) -> bool {
    let mut hit = false;
    for ((x0, y0), (x1, y1)) in ring_edges(poly) {
        if (y0 > y) != (y1 > y) && x < x0 + (y - y0) * (x1 - x0) / (y1 - y0) {
            hit = !hit;
        }
    }
    hit
}

/// The distance from `p` to the segment `ab`.
#[must_use]
pub fn seg_dist(p: Pt, a: Pt, b: Pt) -> f64 {
    dist(p, seg_closest(p, a, b))
}

/// The point of the segment `ab` nearest `p`.
#[must_use]
pub fn seg_closest(p: Pt, a: Pt, b: Pt) -> Pt {
    let (dx, dy) = (b.0 - a.0, b.1 - a.1);
    let d2 = dx * dx + dy * dy;
    let t = if d2 == 0.0 {
        0.0
    } else {
        max(0.0, min(1.0, ((p.0 - a.0) * dx + (p.1 - a.1) * dy) / d2))
    };
    (a.0 + t * dx, a.1 + t * dy)
}

/// Python's `min(a, b, ...)` over several floats: each taken only when strictly less than the least so far.
pub(crate) fn least(values: impl IntoIterator<Item = f64>) -> f64 {
    let mut it = values.into_iter();
    let first = it.next().unwrap_or(f64::INFINITY);
    it.fold(first, min)
}

/// Python's `max(a, b, ...)` over several floats: each taken only when strictly greater than the largest so far.
pub(crate) fn most(values: impl IntoIterator<Item = f64>) -> f64 {
    let mut it = values.into_iter();
    let first = it.next().unwrap_or(f64::NEG_INFINITY);
    it.fold(first, max)
}

/// The gap between two boxes, `math.hypot(max(0.0, bx0 - x1, x0 - bx1), max(0.0, by0 - y1, y0 - by1))`: 0 where they meet.
#[must_use]
pub fn box_gap(a: BBox, b: BBox) -> f64 {
    let (x0, y0, x1, y1) = a;
    let (bx0, by0, bx1, by1) = b;
    hypot(
        most([0.0, bx0 - x1, x0 - bx1]),
        most([0.0, by0 - y1, y0 - by1]),
    )
}

fn cross(o: Pt, a: Pt, b: Pt) -> f64 {
    (a.0 - o.0) * (b.1 - o.1) - (a.1 - o.1) * (b.0 - o.0)
}

/// Do the closed segments `ab` and `cd` meet? (A NaN is true to Python, as `!= 0.0` is here.)
#[must_use]
pub fn segments_cross(a: Pt, b: Pt, c: Pt, d: Pt) -> bool {
    let (d1, d2, d3, d4) = (
        cross(c, d, a),
        cross(c, d, b),
        cross(a, b, c),
        cross(a, b, d),
    );
    if ((d1 > 0.0) != (d2 > 0.0))
        && ((d3 > 0.0) != (d4 > 0.0))
        && d1 != 0.0
        && d2 != 0.0
        && d3 != 0.0
        && d4 != 0.0
    {
        return true;
    }
    least([
        seg_dist(a, c, d),
        seg_dist(b, c, d),
        seg_dist(c, a, b),
        seg_dist(d, a, b),
    ]) == 0.0
}

/// How far apart two boxes must stand for [`nearest_points`] to skip its crossing and containment tests - more than any rounding in
/// them, so that no answer they would give is skipped.
const APART: f64 = 1e-6;

/// The gap between two polygons: 0 when they touch, overlap or one holds the other, else the least edge distance.
#[must_use]
pub fn poly_gap(p: &[Pt], q: &[Pt]) -> f64 {
    let (a, b) = nearest_points(p, q, true);
    dist(a, b)
}

/// The nearest pair of points, one on each outline - the same point twice when they meet. `p` is a polygon; `q` is a polygon, or with
/// `closed` false an open polyline (a road). Checked by vertices against edges both ways, which is exact for outlines that do not cross;
/// crossing and containment are tested first.
///
/// # Panics
/// An outline of no vertex, which the Python's assertion refused too.
#[must_use]
pub fn nearest_points(p: &[Pt], q: &[Pt], closed: bool) -> (Pt, Pt) {
    let qe: Vec<(Pt, Pt)> = if closed {
        ring_edges(q).collect()
    } else {
        open_edges(q).collect()
    };
    // BOXES APART, OUTLINES APART (feature 287, the board's 216 s siting: this test was four fifths of proving a seat): two outlines
    // whose boxes stand more than a rounding apart can neither cross nor hold one another, so the tests below would all answer no
    let (px0, py0, px1, py1) = bbox(p);
    let (qx0, qy0, qx1, qy1) = bbox(q);
    if !(px0 - qx1 > APART || qx0 - px1 > APART || py0 - qy1 > APART || qy0 - py1 > APART) {
        if inside(p[0].0, p[0].1, q) && closed {
            return (p[0], p[0]);
        }
        if inside(q[0].0, q[0].1, p) {
            return (q[0], q[0]);
        }
        for (a, b) in ring_edges(p) {
            for &(c, d) in &qe {
                if segments_cross(a, b, c, d) {
                    return (a, a);
                }
            }
        }
    }
    let mut best: Option<(f64, Pt, Pt)> = None;
    for &v in p {
        for &(c, d) in &qe {
            let w = seg_closest(v, c, d);
            let dd = dist(v, w);
            if best.is_none_or(|b| dd < b.0) {
                best = Some((dd, v, w));
            }
        }
    }
    for &v in q {
        for (a, b) in ring_edges(p) {
            let w = seg_closest(v, a, b);
            let dd = dist(v, w);
            if best.is_none_or(|b| dd < b.0) {
                best = Some((dd, w, v));
            }
        }
    }
    let (_, a, b) = best.expect("both outlines have vertices");
    (a, b)
}

/// The gap between a polygon and a segment: 0 when the segment touches or enters it.
#[must_use]
pub fn poly_seg_gap(poly: &[Pt], a: Pt, b: Pt) -> f64 {
    if inside(a.0, a.1, poly) || inside(b.0, b.1, poly) {
        return 0.0;
    }
    let mut best = f64::INFINITY;
    for (c, d) in ring_edges(poly) {
        if segments_cross(a, b, c, d) {
            return 0.0;
        }
        best = least([
            best,
            seg_dist(c, a, b),
            seg_dist(d, a, b),
            seg_dist(a, c, d),
            seg_dist(b, c, d),
        ]);
    }
    best
}

#[cfg(test)]
mod tests;
