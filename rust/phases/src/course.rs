//! The brook as the map draws it (feature 444 T26 D2): its course with every bend rounded on an arc, laid once by the stage that
//! lays the brook (the field); a channel that leaves or joins it starts or ends on that drawn course.
//!
//! Research:
//!     the brook as drawn - NONE: the course's geometry; each rule's claim is at the unit that keeps it

#![expect(
    clippy::many_single_char_names,
    reason = "the plane geometry's own names"
)]

use crate::field::fan::Pt;
use crate::field::geom::dist;

/// A bend's radius, in drawn widths of the course.
///
/// Research:
///     the brook's bend - research/questions/0054-which-way-water-flows-and-how-channels-bend-and-join.drawing.html: "About 2.5 channel widths in radius"
pub const BEND_WIDTHS: f64 = 2.5;
/// The least turn a bend is rounded at (degrees): a gentler one shows no elbow.
///
/// Research:
///     turn left sharp - research/questions/0054-which-way-water-flows-and-how-channels-bend-and-join.drawing.html: a turn under 8 deg is not rounded
pub const MIN_TURN_DEG: f64 = 8.0;
/// The most of either straight leg a bend's radius takes.
///
/// Research:
///     the bend's cap - research/questions/0054-which-way-water-flows-and-how-channels-bend-and-join.drawing.html: "A bend's radius is capped at 35% of the straight run on either side"
pub const LEG_CAP: f64 = 0.35;
/// The most of either leg a bend's tangent run takes, so two neighboring bends never meet past the middle of the leg between them.
///
/// Research:
///     neighboring bends apart - GUESS: no source could speak to it, a value of ours; half of each leg
pub const TANGENT_CAP: f64 = 0.5;
/// The points a bend's arc is drawn with past its first.
///
/// Research:
///     the bend's samples - NONE: drawing resolution, six steps a bend
pub const BEND_STEPS: u32 = 6;

/// The turn at interior vertex `i` of `pts`, in degrees (0 straight on), or None at a repeated vertex.
fn turn(pts: &[Pt], i: usize) -> Option<f64> {
    let (p0, p1, p2) = (pts[i - 1], pts[i], pts[i + 1]);
    let (v0, v1) = ((p0.0 - p1.0, p0.1 - p1.1), (p2.0 - p1.0, p2.1 - p1.1));
    let (l0, l1) = (dist(p0, p1), dist(p1, p2));
    if l0 < 1e-6 || l1 < 1e-6 {
        return None;
    }
    let cos = ((v0.0 * v1.0 + v0.1 * v1.1) / (l0 * l1)).clamp(-1.0, 1.0);
    Some(180.0 - cos.acos().to_degrees())
}

/// The arc rounding the bend at `p1` between legs from `p0` and to `p2`, turning `deg`, its radius `r` capped by the legs
/// (`LEG_CAP`, `TANGENT_CAP`): from the tangent point on the leg before to the one on the leg after, `BEND_STEPS` steps.
fn arc(p0: Pt, p1: Pt, p2: Pt, deg: f64, r: f64) -> Vec<Pt> {
    let (l0, l1) = (dist(p0, p1), dist(p1, p2));
    let half = (deg / 2.0).to_radians();
    let mut radius = r.min(LEG_CAP * l0).min(LEG_CAP * l1);
    let mut d = radius * half.tan();
    let most = TANGENT_CAP * l0.min(l1);
    if d > most {
        d = most;
        radius = d / half.tan();
    }
    let (u0, u1) = (
        ((p0.0 - p1.0) / l0, (p0.1 - p1.1) / l0),
        ((p2.0 - p1.0) / l1, (p2.1 - p1.1) / l1),
    );
    let (a, b) = (
        (p1.0 + u0.0 * d, p1.1 + u0.1 * d),
        (p1.0 + u1.0 * d, p1.1 + u1.1 * d),
    );
    let (bx, by) = (u0.0 + u1.0, u0.1 + u1.1);
    let bn = (bx * bx + by * by).sqrt();
    let off = radius / half.cos();
    let c = (p1.0 + bx / bn * off, p1.1 + by / bn * off);
    let (t0, t1) = ((a.1 - c.1).atan2(a.0 - c.0), (b.1 - c.1).atan2(b.0 - c.0));
    let sweep =
        (t1 - t0 + std::f64::consts::PI).rem_euclid(std::f64::consts::TAU) - std::f64::consts::PI;
    (0..=BEND_STEPS)
        .map(|s| {
            let t = t0 + sweep * f64::from(s) / f64::from(BEND_STEPS);
            (c.0 + radius * t.cos(), c.1 + radius * t.sin())
        })
        .collect()
}

/// The brook as drawn: every interior bend of at least `MIN_TURN_DEG` rounded on an arc of `BEND_WIDTHS` drawn widths `w`, capped
/// by its legs. `tests` counts the bends asked and the points written.
///
/// Research:
///     an earthen channel bends on a sweep - research/questions/0054-which-way-water-flows-and-how-channels-bend-and-join.html: every interior corner filleted
///     no mitered corner - research/questions/0054-which-way-water-flows-and-how-channels-bend-and-join.drawing.html: "no watercourse on them has a mitered corner", so no vertex is held unrounded; a channel's mouth is set on the drawn course instead (`mouth`)
#[must_use]
pub fn drawn(course: &[Pt], w: f64, tests: &mut u64) -> Vec<Pt> {
    if course.len() < 3 {
        return course.to_vec();
    }
    let mut out = vec![course[0]];
    for i in 1..course.len() - 1 {
        *tests += 1;
        match turn(course, i) {
            None => {}
            Some(t) if t < MIN_TURN_DEG => out.push(course[i]),
            Some(t) => {
                let pts = arc(course[i - 1], course[i], course[i + 1], t, BEND_WIDTHS * w);
                *tests += pts.len() as u64;
                out.extend(pts);
            }
        }
    }
    out.push(course[course.len() - 1]);
    *tests += 2;
    out
}

/// Where a channel leaving or joining the course at `q` meets it as drawn: the nearest point of `drawn` (each segment asked once,
/// counted in `tests`).
///
/// Research:
///     a junction on the drawn course - research/questions/0054-which-way-water-flows-and-how-channels-bend-and-join.drawing.html: "a meeting is a junction when either channel's end lies inside the other's drawn width"
#[must_use]
pub fn mouth(q: Pt, drawn: &[Pt], tests: &mut u64) -> Pt {
    *tests += drawn.len() as u64;
    drawn
        .windows(2)
        .map(|s| crate::sink::crop::nearest_on(q, s[0], s[1]))
        .fold((q, f64::INFINITY), |m, p| {
            if dist(p, q) < m.1 {
                (p, dist(p, q))
            } else {
                m
            }
        })
        .0
}
