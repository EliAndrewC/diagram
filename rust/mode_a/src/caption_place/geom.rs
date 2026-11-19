//! The plain geometry the caption placer measures with (feature 449 T202): boxes, the caption's block as a four-cornered outline turned
//! with it, and the tests the derivation's `exact_test` and `shape_distance` count - whether a block meets a drawn outline, and how far
//! apart they stand. Written for the placer alone, from its derivation (`specs/449-rust-codebase/derivations/T198-placer.md`).
//!
//! Research: the placer's geometry - NONE: points, boxes and outlines measured, deciding nothing about where a caption stands

#![expect(
    clippy::many_single_char_names,
    reason = "geometry's points, boxes and sizes as the derivation names them: a, b, c, d, p, q, w, h"
)]

/// A point on the sheet, in px.
pub type Pt = (f64, f64);

/// A box `(x0, y0, x1, y1)`.
pub type Bx = (f64, f64, f64, f64);

/// How far inside one another two outlines must reach to meet: a block touching ink edge to edge does not cover it.
///
/// Research: touching is not covering - NONE: a numerical tolerance, 1e-6 px, far under anything drawn
pub const EPS: f64 = 1e-6;

/// The box around some points.
#[must_use]
pub fn bbox(pts: &[Pt]) -> Bx {
    pts.iter().fold(
        (
            f64::INFINITY,
            f64::INFINITY,
            f64::NEG_INFINITY,
            f64::NEG_INFINITY,
        ),
        |b, p| (b.0.min(p.0), b.1.min(p.1), b.2.max(p.0), b.3.max(p.1)),
    )
}

/// Do two boxes overlap by more than a touch?
#[must_use]
pub fn boxes_meet(a: Bx, b: Bx) -> bool {
    a.0 < b.2 - EPS && b.0 < a.2 - EPS && a.1 < b.3 - EPS && b.1 < a.3 - EPS
}

/// Does `outer` hold `inner` whole?
#[must_use]
pub fn holds(outer: Bx, inner: Bx) -> bool {
    outer.0 <= inner.0 + EPS
        && outer.1 <= inner.1 + EPS
        && outer.2 >= inner.2 - EPS
        && outer.3 >= inner.3 - EPS
}

/// `b` grown by `d` on every side.
#[must_use]
pub fn grow(b: Bx, d: f64) -> Bx {
    (b.0 - d, b.1 - d, b.2 + d, b.3 + d)
}

/// `p` turned by `deg` degrees about the origin.
#[must_use]
pub fn turn(p: Pt, deg: f64) -> Pt {
    let (s, c) = deg.to_radians().sin_cos();
    (p.0 * c - p.1 * s, p.0 * s + p.1 * c)
}

/// The four corners of a `w` x `h` block centered on `c` (sheet coordinates), turned by `deg` about its center, in drawing order.
#[must_use]
pub fn block(c: Pt, w: f64, h: f64, deg: f64) -> [Pt; 4] {
    let (hw, hh) = (w / 2.0, h / 2.0);
    [(-hw, -hh), (hw, -hh), (hw, hh), (-hw, hh)].map(|q| {
        let t = turn(q, deg);
        (c.0 + t.0, c.1 + t.1)
    })
}

/// The edges of a closed outline, its last point joined to its first.
pub fn ring(poly: &[Pt]) -> impl Iterator<Item = (Pt, Pt)> + '_ {
    let n = poly.len();
    (0..n).map(move |i| (poly[i], poly[(i + 1) % n]))
}

/// The edges of an open line.
pub fn path(poly: &[Pt]) -> impl Iterator<Item = (Pt, Pt)> + '_ {
    poly.windows(2).map(|w| (w[0], w[1]))
}

fn cross(o: Pt, a: Pt, b: Pt) -> f64 {
    (a.0 - o.0) * (b.1 - o.1) - (a.1 - o.1) * (b.0 - o.0)
}

/// Do two segments cross, each passing strictly through the other (a touch at an end is no crossing)?
#[must_use]
pub fn segments_cross(a: Pt, b: Pt, c: Pt, d: Pt) -> bool {
    let (d1, d2) = (cross(a, b, c), cross(a, b, d));
    let (d3, d4) = (cross(c, d, a), cross(c, d, b));
    ((d1 > EPS && d2 < -EPS) || (d1 < -EPS && d2 > EPS))
        && ((d3 > EPS && d4 < -EPS) || (d3 < -EPS && d4 > EPS))
}

/// Is `p` strictly inside the closed outline `poly` (even-odd, as a filled outline is read)?
#[must_use]
pub fn inside(p: Pt, poly: &[Pt]) -> bool {
    let mut odd = false;
    for (a, b) in ring(poly) {
        if (a.1 > p.1) != (b.1 > p.1) {
            let x = a.0 + (p.1 - a.1) / (b.1 - a.1) * (b.0 - a.0);
            if p.0 < x {
                odd = !odd;
            }
        }
    }
    odd && ring(poly).all(|(a, b)| seg_dist(p, a, b) > EPS)
}

/// Is the closed outline convex (every turn the same way)?
#[must_use]
pub fn convex(poly: &[Pt]) -> bool {
    let n = poly.len();
    let (mut pos, mut neg) = (false, false);
    for i in 0..n {
        let z = cross(poly[i], poly[(i + 1) % n], poly[(i + 2) % n]);
        pos |= z > EPS;
        neg |= z < -EPS;
    }
    !(pos && neg)
}

/// Do two convex outlines overlap by more than a touch (separating axes over both outlines' edges)?
#[must_use]
pub fn convex_meet(a: &[Pt], b: &[Pt]) -> bool {
    for (p, q) in ring(a).chain(ring(b)) {
        let axis = (q.1 - p.1, p.0 - q.0);
        let span = |poly: &[Pt]| {
            poly.iter()
                .fold((f64::INFINITY, f64::NEG_INFINITY), |(lo, hi), v| {
                    let t = v.0 * axis.0 + v.1 * axis.1;
                    (lo.min(t), hi.max(t))
                })
        };
        let (a0, a1) = span(a);
        let (b0, b1) = span(b);
        let len = axis.0.hypot(axis.1).max(EPS);
        if a1 <= b0 + EPS * len || b1 <= a0 + EPS * len {
            return false;
        }
    }
    true
}

/// Does the convex `quad` overlap the closed outline `poly`, convex or not, by more than a touch?
#[must_use]
pub fn quad_meets(quad: &[Pt; 4], poly: &[Pt], poly_convex: bool) -> bool {
    if poly_convex {
        return convex_meet(quad, poly);
    }
    ring(quad).any(|(a, b)| ring(poly).any(|(c, d)| segments_cross(a, b, c, d)))
        || poly.iter().any(|&p| inside(p, quad))
        || inside(centroid(quad), poly)
        || quad.iter().any(|&p| inside(p, poly))
}

/// The mean of a block's corners: its center.
#[must_use]
pub fn centroid(quad: &[Pt; 4]) -> Pt {
    (
        quad.iter().map(|p| p.0).sum::<f64>() / 4.0,
        quad.iter().map(|p| p.1).sum::<f64>() / 4.0,
    )
}

/// The point of segment `ab` nearest `p`, and its share `t` of the way from `a`.
#[must_use]
pub fn nearest_on(p: Pt, a: Pt, b: Pt) -> (Pt, f64) {
    let (dx, dy) = (b.0 - a.0, b.1 - a.1);
    let len2 = dx * dx + dy * dy;
    let t = if len2 <= 0.0 {
        0.0
    } else {
        (((p.0 - a.0) * dx + (p.1 - a.1) * dy) / len2).clamp(0.0, 1.0)
    };
    ((a.0 + t * dx, a.1 + t * dy), t)
}

/// How far `p` stands from segment `ab`.
#[must_use]
pub fn seg_dist(p: Pt, a: Pt, b: Pt) -> f64 {
    let (q, _) = nearest_on(p, a, b);
    (p.0 - q.0).hypot(p.1 - q.1)
}

/// The nearest pair of points between segments `ab` and `cd` (`(on ab, on cd)`): none apart when they cross.
#[must_use]
pub fn seg_pair(a: Pt, b: Pt, c: Pt, d: Pt) -> (Pt, Pt) {
    if segments_cross(a, b, c, d) {
        let (q, _) = nearest_on(c, a, b);
        return (q, q);
    }
    let cands = [
        (a, nearest_on(a, c, d).0),
        (b, nearest_on(b, c, d).0),
        (nearest_on(c, a, b).0, c),
        (nearest_on(d, a, b).0, d),
    ];
    cands
        .into_iter()
        .min_by(|x, y| dist(x.0, x.1).total_cmp(&dist(y.0, y.1)))
        .unwrap_or((a, c))
}

/// The distance between two points.
#[must_use]
pub fn dist(p: Pt, q: Pt) -> f64 {
    (p.0 - q.0).hypot(p.1 - q.1)
}

/// The box of a closed outline's part within the box `b`: its edges clipped to `b` and the corners of `b` inside it, or `None` where the
/// outline does not reach `b`. A concave outline's box may reach far past it; its part within a search's strip is what the search meets.
#[must_use]
pub fn clip_box(poly: &[Pt], b: Bx) -> Option<Bx> {
    let mut pts: Vec<Pt> = Vec::new();
    for (p, q) in ring(poly) {
        // Liang-Barsky: the share of the edge inside the box
        let (dx, dy) = (q.0 - p.0, q.1 - p.1);
        let (mut t0, mut t1) = (0.0_f64, 1.0_f64);
        let mut inside_box = true;
        for (pk, qk) in [
            (-dx, p.0 - b.0),
            (dx, b.2 - p.0),
            (-dy, p.1 - b.1),
            (dy, b.3 - p.1),
        ] {
            if pk.abs() < EPS {
                if qk < 0.0 {
                    inside_box = false;
                }
            } else {
                let r = qk / pk;
                if pk < 0.0 {
                    t0 = t0.max(r);
                } else {
                    t1 = t1.min(r);
                }
            }
        }
        if inside_box && t0 <= t1 {
            pts.push((p.0 + t0 * dx, p.1 + t0 * dy));
            pts.push((p.0 + t1 * dx, p.1 + t1 * dy));
        }
    }
    for c in [(b.0, b.1), (b.2, b.1), (b.2, b.3), (b.0, b.3)] {
        if inside(c, poly) {
            pts.push(c);
        }
    }
    (!pts.is_empty()).then(|| bbox(&pts))
}

/// How far a block stands from a closed outline (0 where they meet).
#[must_use]
pub fn quad_gap(quad: &[Pt; 4], poly: &[Pt], poly_convex: bool) -> f64 {
    if quad_meets(quad, poly, poly_convex) {
        return 0.0;
    }
    ring(quad)
        .flat_map(|(a, b)| {
            ring(poly).map(move |(c, d)| {
                let (p, q) = seg_pair(a, b, c, d);
                dist(p, q)
            })
        })
        .fold(f64::INFINITY, f64::min)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn boxes_meet_only_past_a_touch_and_hold_whole() {
        assert!(boxes_meet((0.0, 0.0, 2.0, 2.0), (1.0, 1.0, 3.0, 3.0)));
        assert!(!boxes_meet((0.0, 0.0, 2.0, 2.0), (2.0, 0.0, 3.0, 3.0)));
        assert!(holds((0.0, 0.0, 4.0, 4.0), (1.0, 1.0, 4.0, 2.0)));
        assert!(!holds((0.0, 0.0, 4.0, 4.0), (1.0, 1.0, 5.0, 2.0)));
        assert_eq!(grow((1.0, 1.0, 2.0, 2.0), 1.0), (0.0, 0.0, 3.0, 3.0));
        assert_eq!(bbox(&[(1.0, 5.0), (3.0, 2.0)]), (1.0, 2.0, 3.0, 5.0));
    }

    #[test]
    fn a_block_turns_about_its_center() {
        let q = block((10.0, 10.0), 4.0, 2.0, 90.0);
        let b = bbox(&q);
        assert!((b.0 - 9.0).abs() < 1e-9 && (b.3 - 12.0).abs() < 1e-9);
        assert_eq!(centroid(&q), (10.0, 10.0));
        assert_eq!(path(&[(0.0, 0.0), (1.0, 0.0), (1.0, 1.0)]).count(), 2);
    }

    #[test]
    fn segments_cross_strictly_and_points_lie_inside_strictly() {
        assert!(segments_cross(
            (0.0, 0.0),
            (2.0, 2.0),
            (0.0, 2.0),
            (2.0, 0.0)
        ));
        assert!(!segments_cross(
            (0.0, 0.0),
            (1.0, 1.0),
            (1.0, 1.0),
            (2.0, 0.0)
        ));
        let l = [
            (0.0, 0.0),
            (4.0, 0.0),
            (4.0, 1.0),
            (1.0, 1.0),
            (1.0, 4.0),
            (0.0, 4.0),
        ];
        assert!(inside((0.5, 3.0), &l));
        assert!(!inside((3.0, 3.0), &l));
        assert!(!inside((0.0, 2.0), &l)); // on the edge
        assert!(!convex(&l));
        assert!(convex(&[(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)]));
    }

    #[test]
    fn a_block_meets_a_concave_outline_only_where_it_reaches_the_ink() {
        let l = [
            (0.0, 0.0),
            (4.0, 0.0),
            (4.0, 1.0),
            (1.0, 1.0),
            (1.0, 4.0),
            (0.0, 4.0),
        ];
        let notch = block((3.0, 3.0), 1.0, 1.0, 0.0);
        assert!(!quad_meets(&notch, &l, false));
        assert!(quad_meets(&block((0.5, 2.0), 0.4, 0.4, 0.0), &l, false)); // wholly inside the outline
        assert!(quad_meets(&block((2.0, 2.0), 6.0, 6.0, 0.0), &l, false)); // the outline wholly inside the block
        assert!(quad_meets(&block((1.0, 2.0), 1.0, 0.5, 0.0), &l, false)); // edges crossing
        let gap = quad_gap(&notch, &l, false);
        assert!((gap - 1.5).abs() < 1e-9, "{gap}");
        assert!(quad_gap(&block((0.5, 2.0), 0.4, 0.4, 0.0), &l, false).abs() < 1e-12);
    }

    #[test]
    fn convex_outlines_meet_by_their_axes() {
        let a = block((0.0, 0.0), 2.0, 2.0, 0.0);
        assert!(quad_meets(&a, &block((1.5, 0.0), 2.0, 2.0, 45.0), true));
        assert!(!quad_meets(&a, &block((2.0, 0.0), 2.0, 2.0, 0.0), true));
        assert!(!convex_meet(&a, &block((0.0, 3.0), 2.0, 2.0, 0.0)));
    }

    /// A concave outline's part within a box is what is there, not its own box; a box wholly inside it is all of it.
    #[test]
    fn an_outlines_part_in_a_box_is_clipped_to_it() {
        let l = [
            (0.0, 0.0),
            (10.0, 0.0),
            (10.0, 2.0),
            (2.0, 2.0),
            (2.0, 10.0),
            (0.0, 10.0),
        ];
        assert_eq!(
            clip_box(&l, (-1.0, 5.0, 20.0, 6.0)),
            Some((0.0, 5.0, 2.0, 6.0))
        );
        assert_eq!(
            clip_box(&l, (-1.0, 0.5, 20.0, 1.0)),
            Some((0.0, 0.5, 10.0, 1.0))
        );
        assert_eq!(clip_box(&l, (5.0, 5.0, 8.0, 8.0)), None);
        assert_eq!(
            clip_box(&l, (0.5, 4.0, 1.5, 5.0)),
            Some((0.5, 4.0, 1.5, 5.0))
        );
    }

    #[test]
    fn nearest_points_on_segments() {
        let ((x, y), t) = nearest_on((5.0, 3.0), (0.0, 0.0), (4.0, 0.0));
        assert!((x - 4.0).abs() + y.abs() + (t - 1.0).abs() < 1e-12);
        assert!(nearest_on((1.0, 1.0), (2.0, 2.0), (2.0, 2.0)).1.abs() < 1e-12);
        assert!((seg_dist((2.0, 3.0), (0.0, 0.0), (4.0, 0.0)) - 3.0).abs() < 1e-12);
        let (p, q) = seg_pair((0.0, 0.0), (4.0, 0.0), (2.0, 1.0), (2.0, 3.0));
        assert_eq!((p, q), ((2.0, 0.0), (2.0, 1.0)));
        let (p, q) = seg_pair((0.0, 0.0), (2.0, 2.0), (0.0, 2.0), (2.0, 0.0));
        assert_eq!(p, q);
        assert_eq!(turn((1.0, 0.0), 0.0), (1.0, 0.0));
    }
}
