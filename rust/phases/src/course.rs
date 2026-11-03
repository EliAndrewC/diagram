//! The brook as the map draws it (feature 444 T26 D2): its course with every bend rounded, each tap and confluence held where it
//! joins - laid once by the stage that lays the brook (the field), redrawn by the sink only where a confluence it seats moves it.
//!
//! Research:
//!     the brook as drawn - NONE: the course's geometry; each rule's claim is at the function that keeps it

#![expect(
    clippy::many_single_char_names,
    reason = "the plane geometry's own names"
)]

use crate::field::fan::Pt;
use crate::field::geom::{dist, seg_dist};

/// The cut-back of a bend along each leg, in drawn widths of the course.
///
/// Research:
///     the brook's bend - research/questions/0054-which-way-water-flows-and-how-channels-bend-and-join.drawing.html: every corner filleted at 2.5 bed widths
pub const BEND_WIDTHS: f64 = 2.5;
/// The least turn a bend is rounded at (degrees): a gentler one shows no elbow.
///
/// Research:
///     turn left sharp - research/questions/0054-which-way-water-flows-and-how-channels-bend-and-join.drawing.html: a turn under 8 deg is not rounded
pub const MIN_TURN_DEG: f64 = 8.0;
/// The most of either leg a bend's cut-back takes, so two neighboring bends never eat the leg between them.
///
/// Research:
///     the fillet's cap - GUESS: searched, the record silent (feature 417 T38, 2026-10-25); 0.35 of each leg
pub const LEG_CAP: f64 = 0.35;
/// The points a bend is drawn with past its first (a quadratic, the corner its control point).
///
/// Research:
///     the bend's samples - NONE: drawing resolution, six steps a bend
pub const BEND_STEPS: u32 = 6;
/// How near a declared channel end lies ON the course to be its tap or confluence (feet).
///
/// Research:
///     a mouth on the course - NONE: a tolerance, a foot
pub const ON_COURSE: f64 = 1.0;

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

/// `pts` with every interior bend of at least `MIN_TURN_DEG` rounded: a quadratic from a point `cut` back along the leg before to
/// one `cut` on along the leg after (each at most `LEG_CAP` of its leg), the corner its control point. `tests` counts the bends
/// asked and the points written.
///
/// Research:
///     an earthen channel bends on a sweep - research/questions/0054-which-way-water-flows-and-how-channels-bend-and-join.html: every interior corner filleted
#[must_use]
pub fn fillet(pts: &[Pt], cut: f64, tests: &mut u64) -> Vec<Pt> {
    if pts.len() < 3 || cut <= 0.0 {
        return pts.to_vec();
    }
    let mut out = vec![pts[0]];
    for i in 1..pts.len() - 1 {
        *tests += 1;
        match turn(pts, i) {
            None => {}
            Some(t) if t < MIN_TURN_DEG => out.push(pts[i]),
            Some(_) => {
                let (p0, p1, p2) = (pts[i - 1], pts[i], pts[i + 1]);
                let (l0, l1) = (dist(p0, p1), dist(p1, p2));
                let d = cut.min(LEG_CAP * l0).min(LEG_CAP * l1);
                let a = (p1.0 + (p0.0 - p1.0) / l0 * d, p1.1 + (p0.1 - p1.1) / l0 * d);
                let b = (p1.0 + (p2.0 - p1.0) / l1 * d, p1.1 + (p2.1 - p1.1) / l1 * d);
                for s in 0..=BEND_STEPS {
                    let t = f64::from(s) / f64::from(BEND_STEPS);
                    let m = 1.0 - t;
                    out.push((
                        m * m * a.0 + 2.0 * m * t * p1.0 + t * t * b.0,
                        m * m * a.1 + 2.0 * m * t * p1.1 + t * t * b.1,
                    ));
                }
                *tests += u64::from(BEND_STEPS) + 1;
            }
        }
    }
    out.push(pts[pts.len() - 1]);
    *tests += 2;
    out
}

/// Whether `q` stands on a bend of `course` - within `ON_COURSE` of an interior vertex the rounding bends: a mouth held there would
/// leave the bend mitered, so no confluence is seated on one.
///
/// Research:
///     no mitered corner at a mouth - research/questions/0054-which-way-water-flows-and-how-channels-bend-and-join.drawing.html: "no watercourse on them has a mitered corner"
#[must_use]
pub fn on_bend(q: Pt, course: &[Pt]) -> bool {
    (1..course.len().saturating_sub(1)).any(|k| {
        dist(course[k], q) <= ON_COURSE && turn(course, k).is_some_and(|t| t >= MIN_TURN_DEG)
    })
}

/// `course` with each end in `ends` that lies on it made a vertex, and the vertices to hold: an end within `ON_COURSE` of a vertex
/// holds that vertex (a bend only where `corners` says), an end mid-leg is inserted there. Each end walks the course's legs once
/// for its nearest and its vertices once for one it stands on, counted in `tests`.
fn hold(course: &[Pt], ends: &[Pt], corners: bool, tests: &mut u64) -> (Vec<Pt>, Vec<Pt>) {
    let mut pts = course.to_vec();
    let mut held = Vec::new();
    for &q in ends {
        if pts.len() < 2 {
            break;
        }
        *tests += 2 * pts.len() as u64;
        let (best, d) = (0..pts.len() - 1)
            .map(|k| (k, seg_dist(q, pts[k], pts[k + 1])))
            .fold((0, f64::INFINITY), |m, c| if c.1 < m.1 { c } else { m });
        if d > ON_COURSE {
            continue;
        }
        if let Some(near) = (0..pts.len()).find(|&k| dist(pts[k], q) <= ON_COURSE) {
            if corners || !on_bend(pts[near], &pts) {
                held.push(pts[near]);
            }
            continue;
        }
        let (a, b) = (pts[best], pts[best + 1]);
        let ab = (b.0 - a.0, b.1 - a.1);
        let t = ((q.0 - a.0) * ab.0 + (q.1 - a.1) * ab.1) / (ab.0 * ab.0 + ab.1 * ab.1).max(1e-12);
        let on = (a.0 + ab.0 * t, a.1 + ab.1 * t);
        pts.insert(best + 1, on);
        held.push(on);
    }
    (pts, held)
}

/// The brook as drawn: each tap (the first point of a race taken off it) and each confluence (the last point of a drain joining
/// it) made a vertex and held - a tap even on a bend, a confluence never - and every stretch between two held vertices rounded at
/// `BEND_WIDTHS` of the drawn width `w`. `tests` counts the work.
///
/// Research:
///     a tap is a junction, not a bend - research/questions/0054-which-way-water-flows-and-how-channels-bend-and-join.drawing.html: a vertex at a tap is held
///     a confluence held - research/questions/0054-which-way-water-flows-and-how-channels-bend-and-join.drawing.html: a junction only where an end lies inside the other's drawn width
#[must_use]
pub fn drawn(course: &[Pt], taps: &[Pt], joins: &[Pt], w: f64, tests: &mut u64) -> Vec<Pt> {
    let (pts, mut held) = hold(course, taps, true, tests);
    let (pts, held_j) = hold(&pts, joins, false, tests);
    held.extend(held_j);
    if pts.len() < 3 {
        return pts;
    }
    // the held vertices' places, each found once among the course's vertices (a held vertex is one of them, by `hold`)
    let mut cuts: Vec<usize> = held
        .iter()
        .filter_map(|&h| (1..pts.len() - 1).find(|&k| dist(h, pts[k]) <= 1e-9))
        .collect();
    *tests += (held.len() * pts.len()) as u64;
    cuts.sort_unstable();
    cuts.dedup();
    cuts.push(pts.len() - 1);
    let mut out: Vec<Pt> = Vec::new();
    let mut start = 0;
    for k in cuts {
        let part = fillet(&pts[start..=k], BEND_WIDTHS * w, tests);
        out.extend(if out.is_empty() {
            &part[..]
        } else {
            &part[1..]
        });
        start = k;
    }
    out
}
