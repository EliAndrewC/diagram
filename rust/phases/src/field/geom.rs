//! The plane geometry the comb is built with (feature 444 T16): distances, a point inside a ring, and the angle at a corner.
//!
//! Research:
//!     geometry - NONE: plane geometry

use super::fan::Pt;

/// The distance between two points.
#[must_use]
pub fn dist(a: Pt, b: Pt) -> f64 {
    ((b.0 - a.0).powi(2) + (b.1 - a.1).powi(2)).sqrt()
}

/// The unit vector from one point toward another (zero-safe).
#[must_use]
pub fn unit(from: Pt, to: Pt) -> Pt {
    let d = dist(from, to).max(1e-12);
    ((to.0 - from.0) / d, (to.1 - from.1) / d)
}

/// The distance from a point to a segment.
#[must_use]
pub fn seg_dist(p: Pt, a: Pt, b: Pt) -> f64 {
    let (vx, vy) = (b.0 - a.0, b.1 - a.1);
    let len2 = vx * vx + vy * vy;
    let t = if len2 > 0.0 {
        (((p.0 - a.0) * vx + (p.1 - a.1) * vy) / len2).clamp(0.0, 1.0)
    } else {
        0.0
    };
    dist(p, (a.0 + vx * t, a.1 + vy * t))
}

/// A closed ring's area by the shoelace formula, signed (positive when its corners turn clockwise on the map's y-down axes).
#[must_use]
pub fn signed_area(ring: &[Pt]) -> f64 {
    let n = ring.len();
    (0..n)
        .map(|i| {
            let (a, b) = (ring[i], ring[(i + 1) % n]);
            a.0 * b.1 - b.0 * a.1
        })
        .sum::<f64>()
        / 2.0
}

/// Whether a point lies inside a closed ring (even-odd).
#[expect(
    clippy::many_single_char_names,
    reason = "the plane geometry's own names"
)]
#[must_use]
pub fn inside(p: Pt, ring: &[Pt]) -> bool {
    let n = ring.len();
    let mut odd = false;
    let mut j = n.wrapping_sub(1);
    for i in 0..n {
        let (a, b) = (ring[i], ring[j]);
        if (a.1 > p.1) != (b.1 > p.1) && p.0 < (b.0 - a.0) * (p.1 - a.1) / (b.1 - a.1) + a.0 {
            odd = !odd;
        }
        j = i;
    }
    odd
}

/// The interior angle at corner `i` of a ring, in degrees (0 to 360: over 180 at a reflex corner).
#[expect(
    clippy::many_single_char_names,
    reason = "the plane geometry's own names"
)]
#[must_use]
pub fn corner_deg(ring: &[Pt], i: usize) -> f64 {
    let n = ring.len();
    let (a, b, c) = (ring[(i + n - 1) % n], ring[i], ring[(i + 1) % n]);
    let (u, v) = (unit(b, a), unit(b, c));
    let open = (u.0 * v.0 + u.1 * v.1).clamp(-1.0, 1.0).acos().to_degrees();
    let z = (b.0 - a.0) * (c.1 - b.1) - (b.1 - a.1) * (c.0 - b.0);
    if z * signed_area(ring).signum() < 0.0 {
        360.0 - open
    } else {
        open
    }
}

/// A ring's convex hull (Andrew's monotone chain), its corners in turn.
#[must_use]
pub fn hull(ring: &[Pt]) -> Vec<Pt> {
    let mut pts = ring.to_vec();
    pts.sort_by(|a, b| a.0.total_cmp(&b.0).then(a.1.total_cmp(&b.1)));
    let turn = |o: Pt, a: Pt, b: Pt| (a.0 - o.0) * (b.1 - o.1) - (a.1 - o.1) * (b.0 - o.0);
    let mut lower: Vec<Pt> = Vec::new();
    for &p in &pts {
        while lower.len() >= 2 && turn(lower[lower.len() - 2], lower[lower.len() - 1], p) <= 0.0 {
            lower.pop();
        }
        lower.push(p);
    }
    let mut upper: Vec<Pt> = Vec::new();
    for &p in pts.iter().rev() {
        while upper.len() >= 2 && turn(upper[upper.len() - 2], upper[upper.len() - 1], p) <= 0.0 {
            upper.pop();
        }
        upper.push(p);
    }
    lower.pop();
    upper.pop();
    lower.extend(upper);
    lower
}

#[cfg(test)]
mod tests {
    use super::{corner_deg, dist, hull, inside, seg_dist, signed_area, unit};

    #[test]
    fn the_plane_geometry() {
        let sq = [(0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0)];
        assert!((signed_area(&sq) - 100.0).abs() < 1e-9);
        assert!(inside((5.0, 5.0), &sq) && !inside((15.0, 5.0), &sq));
        assert!((seg_dist((5.0, 3.0), (0.0, 0.0), (10.0, 0.0)) - 3.0).abs() < 1e-9);
        assert!((seg_dist((-4.0, 3.0), (0.0, 0.0), (10.0, 0.0)) - 5.0).abs() < 1e-9);
        assert!((seg_dist((1.0, 1.0), (0.0, 0.0), (0.0, 0.0)) - 2f64.sqrt()).abs() < 1e-9);
        assert!((dist(unit((0.0, 0.0), (3.0, 4.0)), (0.6, 0.8))) < 1e-9);
        assert!((corner_deg(&sq, 0) - 90.0).abs() < 1e-9);
        let notched = [(100.0, 0.0), (0.0, 27.0), (30.0, 0.0), (0.0, -27.0)];
        assert!(corner_deg(&notched, 2) > 180.0);
        assert_eq!(hull(&notched).len(), 3, "the notch is inside the hull");
    }
}
