//! The plane geometry the comb is built with (feature 444 T16): distances, a point inside a ring, a ring clipped to a convex
//! window, a ray to a ring's edge and the angle at a corner.
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

/// `subject` clipped to the convex `window` (Sutherland-Hodgman): the part of the subject inside it. The subject may be any simple
/// ring; a window cutting it in two returns both pieces joined along the window's edge, which the comb's caller refuses by area.
#[expect(
    clippy::many_single_char_names,
    reason = "the plane geometry's own names"
)]
#[must_use]
pub fn clip(subject: &[Pt], window: &[Pt]) -> Vec<Pt> {
    let turn = signed_area(window).signum();
    let mut out = subject.to_vec();
    let n = window.len();
    for i in 0..n {
        if out.is_empty() {
            break;
        }
        let (a, b) = (window[i], window[(i + 1) % n]);
        let side = |p: Pt| turn * ((b.0 - a.0) * (p.1 - a.1) - (b.1 - a.1) * (p.0 - a.0)) >= 0.0;
        let input = std::mem::take(&mut out);
        let m = input.len();
        for k in 0..m {
            let (p, q) = (input[(k + m - 1) % m], input[k]);
            let (sp, sq) = (side(p), side(q));
            if sq {
                if !sp {
                    out.push(cross(p, q, a, b));
                }
                out.push(q);
            } else if sp {
                out.push(cross(p, q, a, b));
            }
        }
    }
    out
}

/// Where the line through `p`-`q` meets the line through `a`-`b` (the two are not parallel where `clip` asks).
#[expect(
    clippy::many_single_char_names,
    reason = "the plane geometry's own names"
)]
fn cross(p: Pt, q: Pt, a: Pt, b: Pt) -> Pt {
    let (r, s) = ((q.0 - p.0, q.1 - p.1), (b.0 - a.0, b.1 - a.1));
    let den = r.0 * s.1 - r.1 * s.0;
    if den.abs() < 1e-12 {
        return q;
    }
    let t = ((a.0 - p.0) * s.1 - (a.1 - p.1) * s.0) / den;
    (p.0 + r.0 * t, p.1 + r.1 * t)
}

/// The nearest point where a ray from `from` along the unit vector `dir` leaves the ring, if it does.
#[expect(
    clippy::many_single_char_names,
    reason = "the plane geometry's own names"
)]
#[must_use]
pub fn ray_exit(from: Pt, dir: Pt, ring: &[Pt]) -> Option<Pt> {
    let n = ring.len();
    let mut best: Option<(f64, Pt)> = None;
    for i in 0..n {
        let (a, b) = (ring[i], ring[(i + 1) % n]);
        let s = (b.0 - a.0, b.1 - a.1);
        let den = dir.0 * s.1 - dir.1 * s.0;
        if den.abs() < 1e-12 {
            continue;
        }
        let t = ((a.0 - from.0) * s.1 - (a.1 - from.1) * s.0) / den;
        let v = ((a.0 - from.0) * dir.1 - (a.1 - from.1) * dir.0) / den;
        if t > 1e-9 && (0.0..=1.0).contains(&v) && best.is_none_or(|(bt, _)| t < bt) {
            best = Some((t, (from.0 + dir.0 * t, from.1 + dir.1 * t)));
        }
    }
    best.map(|(_, p)| p)
}

/// The angle at corner `i` of a ring, in degrees (0 to 180).
#[expect(
    clippy::many_single_char_names,
    reason = "the plane geometry's own names"
)]
#[must_use]
pub fn corner_deg(ring: &[Pt], i: usize) -> f64 {
    let n = ring.len();
    let (a, b, c) = (ring[(i + n - 1) % n], ring[i], ring[(i + 1) % n]);
    let (u, v) = (unit(b, a), unit(b, c));
    (u.0 * v.0 + u.1 * v.1).clamp(-1.0, 1.0).acos().to_degrees()
}

#[cfg(test)]
mod tests {
    use super::{clip, corner_deg, cross, dist, inside, ray_exit, seg_dist, signed_area, unit};

    #[test]
    fn the_plane_geometry() {
        let sq = [(0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0)];
        assert!((signed_area(&sq) - 100.0).abs() < 1e-9);
        assert!(inside((5.0, 5.0), &sq) && !inside((15.0, 5.0), &sq));
        assert!((seg_dist((5.0, 3.0), (0.0, 0.0), (10.0, 0.0)) - 3.0).abs() < 1e-9);
        assert!((seg_dist((-4.0, 3.0), (0.0, 0.0), (10.0, 0.0)) - 5.0).abs() < 1e-9);
        assert!((seg_dist((1.0, 1.0), (0.0, 0.0), (0.0, 0.0)) - 2f64.sqrt()).abs() < 1e-9);
        assert!((dist(unit((0.0, 0.0), (3.0, 4.0)), (0.6, 0.8))) < 1e-9);
        let win = [(5.0, -5.0), (15.0, -5.0), (15.0, 15.0), (5.0, 15.0)];
        let c = clip(&sq, &win);
        assert!(
            (signed_area(&c).abs() - 50.0).abs() < 1e-9,
            "half the square"
        );
        let rev: Vec<_> = win.iter().rev().copied().collect();
        assert!(
            (signed_area(&clip(&sq, &rev)).abs() - 50.0).abs() < 1e-9,
            "either winding"
        );
        let far = [(50.0, 50.0), (60.0, 50.0), (60.0, 60.0)];
        assert!(clip(&sq, &far).is_empty());
        let hit = ray_exit((5.0, 5.0), (1.0, 0.0), &sq).unwrap();
        assert!(dist(hit, (10.0, 5.0)) < 1e-9);
        assert!(ray_exit((50.0, 5.0), (1.0, 0.0), &sq).is_none());
        assert!((corner_deg(&sq, 0) - 90.0).abs() < 1e-9);
        let q = cross((0.0, 0.0), (1.0, 0.0), (0.0, 1.0), (1.0, 1.0));
        assert!(
            dist(q, (1.0, 0.0)) < 1e-12,
            "parallel lines give the far end"
        );
    }
}
