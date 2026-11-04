//! The lane law where lanes meet (feature 444 T30): two lanes met end to end are one way and may not fold back; a lane's short
//! last leg may not double back on the track out's start; a lane's end leg may not run back along another way's tread at a
//! needle's angle; an end may not run on beside another way; and every end reaches something worth walking to
//! (`law/meet.py` `folded_joint_pairs`, `connector_hairpin_ends`, `needle_ends`, `_tread_bearings`; `joints.py` `joints`,
//! `oriented`, `hairpin_over_a_short_leg`; `tails.py` `along_tail`, `_parallel`; `law/ends.py` `dangling_lane_ends`,
//! `_walked_to`; `geom.py` `end_serves`).
//!
//! Research:
//!     lanes meet as a T - research/questions/0081-village-lanes.drawing.html: no needle, fold or hairpin at either end
//!     an end reaches something seen - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: no dangling end
//!     no doubled tail - research/questions/0081-village-lanes.drawing.html: an end running back along another way under 20 degrees, either way round; asked here at 15 (`_DOUBLED_DEG`) - a known gap, carried to 405 T101 (the side-by-side family)
//!     a forced turn is lawful - research/questions/0081-village-lanes.drawing.html: the angle limits read as describing open ground; a turn or meeting whose straighter way the mapped ground blocks is drawn as walked (the GM, 2026-10-17)
#![expect(
    clippy::many_single_char_names,
    clippy::cast_possible_truncation,
    clippy::cast_sign_loss,
    clippy::cast_precision_loss,
    reason = "the plane geometry's own names, and sample counts of a few hundred"
)]

use crate::field::fan::Pt;
use crate::field::geom::{dist, seg_dist};
use crate::ways::route::{length, turn_deg};

/// Is the straight way from one point to another, at a width, not lawful ground?
pub type Blocked<'a> = &'a mut dyn FnMut(Pt, Pt, f64) -> bool;

/// A lane as the law reads it: its points, its width, and whether it is the track out or a row's street.
#[derive(Clone, Debug, Default, PartialEq)]
pub struct Lane {
    /// Its points.
    pub pts: Vec<Pt>,
    /// Its width (ft).
    pub w: f64,
    /// The track out.
    pub connector: bool,
    /// A row village's street.
    pub street: bool,
    /// The household whose way it is, by its house's center.
    pub of: Option<Pt>,
}

/// The point of the segment u-v nearest `q`.
#[must_use]
pub fn foot(q: Pt, (u, v): (Pt, Pt)) -> Pt {
    let (dx, dy) = (v.0 - u.0, v.1 - u.1);
    let l2 = dx * dx + dy * dy;
    let t = if l2 == 0.0 {
        0.0
    } else {
        (((q.0 - u.0) * dx + (q.1 - u.1) * dy) / l2).clamp(0.0, 1.0)
    };
    (u.0 + t * dx, u.1 + t * dy)
}

/// Two lane ends this close are one point; a way within this of an end touches it (ft).
///
/// Research:
///     one point - NONE: the knot and touch passes put two ends on one vertex - 1
///     the web's join tolerance - NONE: the ink's touch - 4
pub const TOUCH: (f64, f64) = (1.0, 4.0);

/// A hairpin's turn, a short returning leg, a needle's angle and leg, the connector's start (degrees and ft).
///
/// Research:
///     hairpin - research/questions/0081-village-lanes.drawing.html: 140 degrees
///     two turns read as one - research/questions/0081-village-lanes.drawing.html: a returning leg under 40 ft is cut
///     a needle, not a T - CONVENTION: under 20 degrees two treads read as one smudged wedge
///     needle leg - GUESS: no source could speak to it, a value of ours (feature 417 T29 pass A2, 2026-10-25); a leg over 20 ft, shorter is the approach to the junction
///     the connector's start - NONE: a lane end within 1.5 ft of the connector's first point meets its start
pub const MEET: (f64, f64, f64, f64, f64) = (140.0, 40.0, 20.0, 20.0, 1.5);

/// The doubled tail: centerlines this close, for at least this long, within this angle (ft, ft, degrees).
///
/// Research:
///     doubled tread distance - CONVENTION: centerlines within 14 ft read as one tread
///     tail run length - GUESS: no source could speak to it, a value of ours (feature 417 T29 pass A2, 2026-10-25); 30 ft beside a way before it is a doubled tail
///     doubled tail angle - CANON: the GM's ruling of 2026-10-25 - the angle is a goal of 20, "arbitrary and not an actual hard requirement", free to move to 15 or 25 if placement or the look needs it; asked here at 15
pub const ALONG: (f64, f64, f64) = (14.0, 30.0, 15.0);

/// An end's reaches: a way or a farmhouse, the bund, a steading's built ground (ft).
///
/// Research:
///     an end reaches a way - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: within 60 ft of another way or a farmhouse
///     reached on the bund - GUESS research/questions/0014-bunds-between-the-paddies-aze.drawing.html: within 6 ft of its edge
///     arrived at a steading - GUESS research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: within 12 ft of its built ground, how close counts as serving
pub const REACHES: (f64, f64, f64) = (60.0, 6.0, 12.0);

/// Every point where exactly two lane ends meet and no other way touches, as `(i, end_i, j, end_j)` (an end 0 or -1); the
/// track out and a street count as a way touching, and two lanes that meet at both ends are a loop, not a joint.
#[must_use]
pub fn joints(lanes: &[Lane]) -> Vec<(usize, i8, usize, i8)> {
    let at = |m: usize, e: i8| {
        if e == 0 {
            lanes[m].pts[0]
        } else {
            lanes[m].pts[lanes[m].pts.len() - 1]
        }
    };
    let ends: Vec<(usize, i8, Pt)> = lanes
        .iter()
        .enumerate()
        .filter(|(_, l)| !(l.connector || l.street) && l.pts.len() >= 2)
        .flat_map(|(m, _)| [(m, 0i8, at(m, 0)), (m, -1i8, at(m, -1))])
        .collect();
    let mut out = Vec::new();
    for (a, &(i, ei, q)) in ends.iter().enumerate() {
        for &(j, ej, r) in &ends[a + 1..] {
            if j == i || dist(q, r) > TOUCH.0 || dist(at(i, -1 - ei), at(j, -1 - ej)) <= TOUCH.0 {
                continue;
            }
            let third = lanes.iter().enumerate().any(|(k, l)| {
                k != i
                    && k != j
                    && l.pts.len() >= 2
                    && l.pts.windows(2).any(|w| seg_dist(q, w[0], w[1]) <= TOUCH.1)
            });
            if !third {
                out.push((i, ei, j, ej));
            }
        }
    }
    out
}

/// The two lanes of a joint as one walk: the first ends at the joint and the second starts there.
#[must_use]
pub fn oriented(lanes: &[Lane], j: (usize, i8, usize, i8)) -> (Vec<Pt>, Vec<Pt>) {
    let (i, ei, k, ek) = j;
    let mut x = lanes[i].pts.clone();
    let mut y = lanes[k].pts.clone();
    if ei == 0 {
        x.reverse();
    }
    if ek == -1 {
        y.reverse();
    }
    (x, y)
}

/// The joints where two lanes met end to end turn back by a hairpin's turn or more, but those the ground forces.
pub fn folded_joint_pairs(lanes: &[Lane], blocked: Blocked) -> Vec<(usize, i8, usize, i8)> {
    joints(lanes)
        .into_iter()
        .filter(|&j| {
            let (x, y) = oriented(lanes, j);
            turn_deg(x[x.len() - 2], x[x.len() - 1], y[1]) >= MEET.0
                && !blocked(x[x.len() - 2], y[1], lanes[j.0].w)
        })
        .collect()
}

/// Do a lane's last two points a -> b, its short last leg b -> j and the other way's first leg j -> c double back - more than a
/// hairpin's turn in all, the leg under the returning leg's length?
#[must_use]
pub fn hairpin_over_a_short_leg(a: Pt, b: Pt, j: Pt, c: Pt) -> bool {
    let signed = |p: Pt, q: Pt, r: Pt| {
        let (h1, h2) = ((q.1 - p.1).atan2(q.0 - p.0), (r.1 - q.1).atan2(r.0 - q.0));
        ((h2 - h1 + std::f64::consts::PI).rem_euclid(2.0 * std::f64::consts::PI)
            - std::f64::consts::PI)
            .to_degrees()
    };
    dist(b, j) <= MEET.1 && (signed(a, b, j) + signed(b, j, c)).abs() > MEET.0
}

/// (connector, lane, end) wherever a lane's short last leg meets the track out's start and the two double back, but where the
/// ground forces it.
pub fn connector_hairpin_ends(lanes: &[Lane], blocked: Blocked) -> Vec<(usize, usize, i8)> {
    let mut out = Vec::new();
    for (ci, co) in lanes
        .iter()
        .enumerate()
        .filter(|(_, l)| l.connector && l.pts.len() >= 2)
    {
        let cp = &co.pts;
        for (i, ln) in lanes
            .iter()
            .enumerate()
            .filter(|(_, l)| !l.connector && l.pts.len() >= 3)
        {
            let rev: Vec<Pt> = ln.pts.iter().rev().copied().collect();
            for (end, seq) in [(-1i8, ln.pts.as_slice()), (0, rev.as_slice())] {
                let n = seq.len();
                let (a, b, j) = (seq[n - 3], seq[n - 2], seq[n - 1]);
                if dist(j, cp[0]) <= MEET.4
                    && hairpin_over_a_short_leg(a, b, j, cp[1])
                    && !blocked(b, cp[1], ln.w)
                {
                    out.push((ci, i, end));
                }
            }
        }
    }
    out
}

/// The unit directions a tread u-v runs from the point on it nearest `q`, toward each end it still extends to.
#[must_use]
pub fn tread_bearings(q: Pt, u: Pt, v: Pt) -> Vec<Pt> {
    let l2 = (v.0 - u.0).powi(2) + (v.1 - u.1).powi(2);
    let t = if l2 == 0.0 {
        0.0
    } else {
        (((q.0 - u.0) * (v.0 - u.0) + (q.1 - u.1) * (v.1 - u.1)) / l2).clamp(0.0, 1.0)
    };
    let foot = (u.0 + t * (v.0 - u.0), u.1 + t * (v.1 - u.1));
    [u, v]
        .iter()
        .filter_map(|&e| {
            let d = dist(foot, e);
            (d >= 1.0).then(|| ((e.0 - foot.0) / d, (e.1 - foot.1) / d))
        })
        .collect()
}

/// Is a needle forced: a rung across the sliver between the end leg back -> end and the tread u-v, at a third, two thirds and
/// the leg's far vertex, not lawful ground?
fn forced_meeting(
    blocked: &mut dyn FnMut(Pt, Pt, f64) -> bool,
    end: Pt,
    back: Pt,
    uv: (Pt, Pt),
    width: f64,
) -> bool {
    [1.0 / 3.0, 2.0 / 3.0, 1.0].iter().any(|&t| {
        let q = (end.0 + (back.0 - end.0) * t, end.1 + (back.1 - end.1) * t);
        let f = foot(q, uv);
        dist(q, f) > 1.0 && blocked(q, f, width)
    })
}

/// (lane, end, tread lane, u, v) wherever a lane's end leg longer than a needle's meets another way's tread within the touch and
/// runs back along it under a needle's angle, but where the ground forces it.
pub fn needle_ends(lanes: &[Lane], blocked: Blocked) -> Vec<(usize, i8, usize, Pt, Pt)> {
    let mut out = Vec::new();
    let tol = TOUCH.1;
    for (i, ln) in lanes
        .iter()
        .enumerate()
        .filter(|(_, l)| !l.connector && l.pts.len() >= 2)
    {
        let p = &ln.pts;
        for (end, q, b) in [(-1i8, p[p.len() - 1], p[p.len() - 2]), (0, p[0], p[1])] {
            let leg = dist(q, b);
            if leg <= MEET.3 {
                continue;
            }
            let back = ((b.0 - q.0) / leg, (b.1 - q.1) / leg);
            for (k, o) in lanes
                .iter()
                .enumerate()
                .filter(|&(k, o)| k != i && o.pts.len() >= 2)
            {
                for w in o.pts.windows(2) {
                    let (u, v) = (w[0], w[1]);
                    let far = (u.0 - tol > q.0 && v.0 - tol > q.0)
                        || (u.0 + tol < q.0 && v.0 + tol < q.0)
                        || (u.1 - tol > q.1 && v.1 - tol > q.1)
                        || (u.1 + tol < q.1 && v.1 + tol < q.1);
                    if far || seg_dist(q, u, v) > tol {
                        continue;
                    }
                    let along = tread_bearings(q, u, v).iter().any(|d| {
                        (back.0 * d.0 + back.1 * d.1)
                            .clamp(-1.0, 1.0)
                            .acos()
                            .to_degrees()
                            < MEET.2
                    });
                    if along && !forced_meeting(blocked, q, b, (u, v), ln.w) {
                        out.push((i, end, k, u, v));
                    }
                }
            }
        }
    }
    out
}

fn parallel(u: Pt, v: Pt, deg: f64) -> bool {
    let (nu, nv) = (u.0.hypot(u.1), v.0.hypot(v.1));
    nu == 0.0
        || nv == 0.0
        || ((u.0 * v.0 + u.1 * v.1).abs() / (nu * nv))
            .min(1.0)
            .acos()
            .to_degrees()
            <= deg
}

/// The index of the sample of `pts` (every 4 ft from its end inward) where its end starts running alongside `other` - within the
/// doubled tread's distance of it, within `deg` of parallel, for at least the tail's run - or None.
#[must_use]
pub fn along_tail(pts: &[Pt], other: &[Pt], deg: f64) -> Option<usize> {
    let mut samples: Vec<Pt> = Vec::new();
    for w in pts.windows(2) {
        let (a, b) = (w[0], w[1]);
        let n = ((dist(a, b) / 4.0) as usize).max(1);
        samples.extend((0..n).map(|i| {
            let f = i as f64 / n as f64;
            (a.0 + (b.0 - a.0) * f, a.1 + (b.1 - a.1) * f)
        }));
    }
    samples.push(pts[pts.len() - 1]);
    if other.len() < 2 {
        return None;
    }
    let mut k = samples.len() - 1;
    while k > 0 {
        let q = samples[k];
        let u = (
            samples[k].0 - samples[k - 1].0,
            samples[k].1 - samples[k - 1].1,
        );
        let near: Vec<(Pt, Pt)> = other
            .windows(2)
            .map(|w| (w[0], w[1]))
            .filter(|&(a, b)| seg_dist(q, a, b) <= ALONG.0)
            .collect();
        let beside = near
            .iter()
            .any(|&(a, b)| parallel(u, (b.0 - a.0, b.1 - a.1), deg))
            || length(&samples[k - 1..]) <= ALONG.0;
        if near.is_empty() || !beside {
            break;
        }
        k -= 1;
    }
    (length(&samples[k..]) >= ALONG.1).then_some(k)
}

/// Does either end of `p` run on beside `o` at the doubled tail's angle?
#[must_use]
pub fn tail_doubled(p: &[Pt], o: &[Pt]) -> bool {
    let rev: Vec<Pt> = p.iter().rev().copied().collect();
    o.len() >= 2 && (along_tail(p, o, ALONG.2).is_some() || along_tail(&rev, o, ALONG.2).is_some())
}

/// What an end may reach besides the ways: the farmhouses and way targets, the worked ground's edge, the steadings' built
/// ground.
#[derive(Default)]
pub struct Destinations {
    /// The farmhouses' centers and the way targets.
    pub centers: Vec<Pt>,
    /// The worked ground's edge, as segments.
    pub edge: Vec<(Pt, Pt)>,
    /// The steadings' built ground.
    pub steadings: Vec<Vec<Pt>>,
}

/// Does a lane end reach something worth walking to: another way, a farmhouse, the bund, or the built ground of a steading?
#[must_use]
pub fn end_serves(q: Pt, segs: &[(Pt, Pt)], d: &Destinations) -> bool {
    let (reach, bund, steading) = REACHES;
    segs.iter().any(|&(a, b)| seg_dist(q, a, b) <= reach)
        || d.centers.iter().any(|&h| dist(q, h) <= reach)
        || d.edge.iter().any(|&(a, b)| seg_dist(q, a, b) <= bund)
        || d.steadings.iter().any(|r| {
            crate::ways::track::in_poly(q, r)
                || (0..r.len()).any(|k| seg_dist(q, r[k], r[(k + 1) % r.len()]) <= steading)
        })
}

/// (lane, end) for every end of a lane but the track out that reaches nothing other than the way its own far end stands on:
/// the other ways' segments asked, less those within the touch of the lane's far end and those the lane did not walk toward.
#[must_use]
pub fn dangling_lane_ends(
    lanes: &[Lane],
    d: &Destinations,
    only: Option<usize>,
) -> Vec<(usize, i8)> {
    let mut out = Vec::new();
    for (i, ln) in lanes.iter().enumerate() {
        if ln.connector || ln.pts.len() < 2 || only.is_some_and(|o| o != i) {
            continue;
        }
        let p = &ln.pts;
        let others: Vec<(Pt, Pt)> = lanes
            .iter()
            .enumerate()
            .filter(|&(k, o)| k != i && o.pts.len() >= 2)
            .flat_map(|(_, o)| o.pts.windows(2).map(|w| (w[0], w[1])).collect::<Vec<_>>())
            .collect();
        for (e, end, far) in [(-1i8, p[p.len() - 1], p[0]), (0, p[0], p[p.len() - 1])] {
            let segs: Vec<(Pt, Pt)> = others
                .iter()
                .copied()
                .filter(|&(a, b)| {
                    seg_dist(far, a, b) > TOUCH.1 && {
                        let c = foot(end, (a, b));
                        dist(c, end) < dist(c, far)
                    }
                })
                .collect();
            if !end_serves(end, &segs, d) {
                out.push((i, e));
            }
        }
    }
    out
}
