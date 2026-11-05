//! The row village's streets (feature 444 T30, `rows.py`): a linear hamlet's farms stand in rows along their streets, never in ranks
//! behind a row. This module is the plane geometry of it - the first street (`best_row_line`, `street_on`), the streets set out
//! parallel to it (`parallel`), the frame centers along a street (`row_seats`), a far-row farm's holding (`holding_quad`,
//! `holding_clear`) and the tests a seat's frame meets (`door_clear`, `frame_refused`); `row_seat.rs` seats the farms on it.
//!
//! Research:
//!     row geometry - NONE: lines, offsets, clipping and seat arithmetic; the units that decide carry their own claims
//!     line form - research/questions/0033-row-villages-resson.html, research/questions/0033-row-villages-resson.drawing.html: a street laid first straight, the dry edge curving with the field's margin
//!     farm spacing - research/questions/0033-row-villages-resson.html, research/questions/0033-row-villages-resson.drawing.html: one frame apart (its longer side), or the lot's frontage where narrower
//!     one side or both - research/questions/0033-row-villages-resson.html, research/questions/0033-row-villages-resson.drawing.html: the far side only, or both sides of the street
//!     seat order - GUESS: no source could speak to it, a value of ours (feature 417 T29 pass B, 2026-10-25); from the line's middle outward, alternating ends
//!     next street beside, never behind - research/questions/0033-row-villages-resson.html, research/questions/0033-row-villages-resson.drawing.html: each further street past the far row's holdings and a lane's room
//!     further streets parallel - research/questions/0033-row-villages-resson.html, research/questions/0033-row-villages-resson.drawing.html: each next street a true parallel of the first
//!     the parallel traced - NONE: the raw offset (each segment set out, a round join at each vertex) sampled every 2 ft and every sample nearer the line than the offset dropped, in place of shapely's `offset_curve` (a departure: GEOS splits a near-collinear offset into parts and Python kept the longest, 8 ft short of the line at each offset; ours is the whole curve)
//!     where the street runs - research/questions/0033-row-villages-resson.drawing.html: the stretch within a row's length of the seat that holds the most farms
//!     its search steps and tolerances - GUESS: no source could speak to it, a value of ours (feature 417 T38 pass N3, 2026-10-25) - 8 (street sampled every 8 ft), 16 (candidate lines sampled)

#![expect(
    clippy::cast_possible_truncation,
    clippy::cast_sign_loss,
    clippy::cast_precision_loss,
    clippy::many_single_char_names,
    clippy::similar_names,
    reason = "sample counts of a few hundred; the plane geometry's own names"
)]

use super::layout::Rect;
use super::level::{interpolate, length as ring_length, project, ring_dist, Hard};
use super::track_out::box_poly;
use super::Counts;
use crate::field::fan::Pt;
use crate::field::geom::{dist, signed_area};
use crate::seat::exit::seg_seg;
use crate::seat::index::area;
use crate::ways::track::in_poly;

/// How far a row's street runs off its field's margin: the lane's room less the tread's half - a map drawing convention.
///
/// Research:
///     street off the field - research/questions/0081-village-lanes.drawing.html: 24 ft, the lane's room (homesteads/715) less the tread's half
pub const FIELD_KEEP_FT: f64 = 24.0;

/// Half a street's tread, and the pad its reserved tread is grown by while its farms are seated.
///
/// Research:
///     street tread - research/questions/0081-village-lanes.drawing.html: a 6 ft street; 0.5 ft pad (NONE: a tolerance)
pub const STREET_HALF_FT: (f64, f64) = (3.0, 0.5);

/// The widest lot a row farm stands on along its street (Santome's 240 ft lots).
///
/// Research:
///     farms one frame apart, never more than 240 ft - research/questions/0033-row-villages-resson.drawing.html: the row steps one frame, never past Santome's 240 ft lots
pub const ROW_FRONTAGE_MAX_FT: f64 = 240.0;

/// The most parallel streets a row village grows.
///
/// Research:
///     most streets - research/questions/0033-row-villages-resson.drawing.html: six parallel streets at most
pub const MAX_STREETS: usize = 6;

/// A far-row farm's holding behind its lot, in lots: a street laid first, and the dry edge.
///
/// Research:
///     far-row dry-field share - research/questions/0033-row-villages-resson.html, research/questions/0033-row-villages-resson.drawing.html: a fixed depth behind the lot, 3 lots on a street laid first and 1 on the dry edge
pub const HOLDING_DEPTH_FRAMES: (f64, f64) = (3.0, 1.0);

/// How far past the yard's front edge the door `door_clear` tests stands (`DOOR_STEP_FT`, 8 ft, and 4 ft), and the room it needs
/// off the hard ground.
///
/// Research:
///     door point past the yard's front - GUESS: no source could speak to it, a value of ours (feature 417 T29 pass B, 2026-10-25); 12 ft past the yard's front edge
///     door room - NONE: 16 ft, a routing tolerance a way needs to start
pub const DOOR_FT: (f64, f64) = (8.0 + 4.0, 16.0);

/// The radius a further street is rounded at on the inside of a corner: twice the radius at which one 40 ft step of the lane law's
/// bend run turns a 50 degree kink - about 92 ft.
///
/// Research:
///     street bend radius - CONVENTION: about 92 ft, from the lane law's bend figures
#[must_use]
pub fn street_bend_radius_ft() -> f64 {
    2.0 * 40.0 / 50.0_f64.to_radians()
}

/// The street's sampling, the parallel's tracing step, and the probe that orients a normal (feet).
///
/// Research:
///     its search steps and tolerances - NONE: an 8 ft street sample, a 2 ft tracing step, a 5 ft probe
const STEP_FT: (f64, f64, f64) = (8.0, 2.0, 5.0);

/// A street: its samples, each a point and the outward normal there.
pub type Line = Vec<(Pt, Pt)>;

/// The two line forms: a street laid first, straight, or the dry edge, curving with the ground.
#[derive(Clone, Copy, PartialEq, Eq, Debug)]
pub enum Form {
    /// Straight, fitted to the ground's edge.
    Street,
    /// The ground's edge itself.
    Edge,
}

/// The exterior of the part of the hard ground grown by `d` nearest `anchor`, clockwise as shapely gives a buffer's; None where
/// there is no hard ground.
#[must_use]
pub fn ring_near(hard: &Hard, anchor: Pt, d: f64, tests: &mut Counts) -> Option<Vec<Pt>> {
    let rings = hard.grown_rings(d, tests);
    tests.add(
        "seg_test@ring_near",
        rings.iter().map(|r| r.len() as u64).sum(),
    );
    let mut ring = rings
        .into_iter()
        .min_by(|a, b| ring_dist(a, anchor).total_cmp(&ring_dist(b, anchor)))?;
    if signed_area(&ring) > 0.0 {
        ring.reverse();
    }
    Some(ring)
}

/// The unit normal to tangent `t` at `p` that points away from the hard ground.
fn normal_away(hard: &Hard, p: Pt, t: Pt, tests: &mut Counts) -> Pt {
    let n1 = (-t.1, t.0);
    let k = STEP_FT.2;
    let a = hard.dist((p.0 + n1.0 * k, p.1 + n1.1 * k), 1e6, tests);
    let b = hard.dist((p.0 - n1.0 * k, p.1 - n1.1 * k), 1e6, tests);
    if a >= b {
        n1
    } else {
        (-n1.0, -n1.1)
    }
}

/// `n` points `length` long along `ring`, centered on arc length `s0`.
fn arc_of(ring: &[Pt], s0: f64, length: f64) -> Vec<Pt> {
    let n = 2.max((length / STEP_FT.0) as usize + 1);
    (0..n)
        .map(|k| interpolate(ring, s0 - length / 2.0 + k as f64 * length / (n - 1) as f64))
        .collect()
}

/// The street on `ring` (the hard ground's edge grown by the street's offset) as samples every 8 ft, `length` long, centered on the
/// point of it nearest `anchor`. The dry EDGE follows the ring; a STREET laid first is the line fitted to the same stretch (its
/// principal axis), set out until the whole stretch lies behind it. `slack` lengthens the line at both ends without changing the
/// stretch it is fitted to.
#[must_use]
pub fn street_on(
    ring: &[Pt],
    hard: &Hard,
    anchor: Pt,
    length: f64,
    form: Form,
    slack: f64,
    tests: &mut Counts,
) -> Line {
    if length <= 0.0 {
        return Vec::new();
    }
    let s0 = project(ring, anchor);
    tests.add("seg_test@street_on", ring.len() as u64);
    if form == Form::Edge {
        let pts = arc_of(ring, s0, length + slack.max(0.0));
        let n = pts.len();
        return (0..n)
            .map(|k| {
                let (q, r) = (pts[(k + 1).min(n - 1)], pts[k.saturating_sub(1)]);
                let m = dist(q, r);
                let m = if m == 0.0 { 1.0 } else { m };
                (
                    pts[k],
                    normal_away(hard, pts[k], ((q.0 - r.0) / m, (q.1 - r.1) / m), tests),
                )
            })
            .collect();
    }
    let pts = arc_of(ring, s0, length);
    let n = pts.len() as f64;
    let (mx, my) = (
        pts.iter().map(|p| p.0).sum::<f64>() / n,
        pts.iter().map(|p| p.1).sum::<f64>() / n,
    );
    let (sxx, syy, sxy) = pts.iter().fold((0.0, 0.0, 0.0), |s, p| {
        (
            s.0 + (p.0 - mx).powi(2),
            s.1 + (p.1 - my).powi(2),
            s.2 + (p.0 - mx) * (p.1 - my),
        )
    });
    let th = 0.5 * (2.0 * sxy).atan2(sxx - syy);
    let t = (th.cos(), th.sin());
    let nrm = normal_away(hard, (mx, my), t, tests);
    // through the stretch's outermost point: all of it behind
    let push = pts
        .iter()
        .map(|p| (p.0 - mx) * nrm.0 + (p.1 - my) * nrm.1)
        .fold(f64::MIN, f64::max);
    let (cx, cy) = (mx + nrm.0 * push, my + nrm.1 * push);
    let full = length + slack;
    let m = 2.max((full / STEP_FT.0) as usize + 1);
    (0..m)
        .map(|k| {
            let u = -full / 2.0 + k as f64 * full / (m - 1) as f64;
            ((cx + t.0 * u, cy + t.1 * u), nrm)
        })
        .collect()
}

/// How far an axis-aligned frame (`cx, cy, w, h`) reaches along a unit `direction`, end to end.
#[must_use]
pub fn frame_extent(frame: Rect, direction: Pt) -> f64 {
    direction.0.abs() * frame.2 + direction.1.abs() * frame.3
}

/// How far apart a street's farms stand: the frame's reach along the street, the most over every turn of the line (an axis-aligned
/// frame reaches farther along a diagonal street than its longer side, `(w + h) / sqrt 2` at 45 degrees) - its longer side where
/// the line has no length.
///
/// Research:
///     farms one frame apart - research/questions/0033-row-villages-resson.html, research/questions/0033-row-villages-resson.drawing.html: one frame apart, a grove farm's own ground, grove and lane room, a physical necessity since a grove farm cannot stand on a narrower lot: stepped at the frame's longer side capped at the 240 ft frontage, every other farm on a diagonal street or a frame past 240 ft lapped its neighbor and was refused (the Rust stage gate, seeds 406155 and 406169), so the 240 ft bounds the holding's width and the step is the frame's reach
#[must_use]
pub fn row_step(line: &[(Pt, Pt)], frame: Rect) -> f64 {
    line.windows(2)
        .filter(|w| w[0].0 != w[1].0)
        .map(|w| {
            let l = dist(w[0].0, w[1].0);
            frame_extent(
                frame,
                ((w[1].0 .0 - w[0].0 .0) / l, (w[1].0 .1 - w[0].0 .1) / l),
            )
        })
        .reduce(f64::max)
        .unwrap_or_else(|| frame.2.max(frame.3))
}

/// A row seat: its frame's center, its side of the street (+1 the far side, away from the field, -1 the near), the street's
/// tangent and its outward normal there.
pub type Seat = (Pt, i32, Pt, Pt);

/// The frame centers along one street, `pitch` apart (the frame's longer side where it is unbounded), from the middle outward
/// alternating the two ends; each on the far side and, for `both`, the near side too, `gap` off the centerline.
#[must_use]
pub fn row_seats(line: &[(Pt, Pt)], frame: Rect, both: bool, gap: f64, pitch: f64) -> Vec<Seat> {
    if line.len() < 2 {
        return Vec::new();
    }
    let mut arc = vec![0.0];
    for w in line.windows(2) {
        arc.push(arc[arc.len() - 1] + dist(w[0].0, w[1].0));
    }
    let total = arc[arc.len() - 1];
    let step = if pitch.is_finite() {
        pitch
    } else {
        frame.2.max(frame.3)
    };
    let at = |u: f64| {
        let k = (0..arc.len() - 1)
            .find(|&i| arc[i + 1] >= u)
            .unwrap_or(0)
            .min(line.len() - 2);
        let seg = arc[k + 1] - arc[k];
        let seg = if seg == 0.0 { 1.0 } else { seg };
        let f = (u - arc[k]) / seg;
        let (a, b) = (line[k].0, line[k + 1].0);
        (
            (a.0 + (b.0 - a.0) * f, a.1 + (b.1 - a.1) * f),
            line[k].1,
            ((b.0 - a.0) / seg, (b.1 - a.1) / seg),
        )
    };
    let mid = total / 2.0;
    let rounds = (total / step) as usize + 1;
    let order = std::iter::once(mid)
        .chain((1..=rounds).flat_map(|k| [mid + k as f64 * step, mid - k as f64 * step]));
    let mut out = Vec::new();
    for u in order.filter(|u| (0.0..=total).contains(u)) {
        let (p, n, t) = at(u);
        let depth = frame_extent(frame, n);
        for side in if both { &[1, -1][..] } else { &[1][..] } {
            let off = f64::from(*side) * (gap + depth / 2.0);
            out.push(((p.0 + n.0 * off, p.1 + n.1 * off), *side, t, n));
        }
    }
    out
}

/// Each street's offset from the field's margin: the first `keep` out for one side, or past a near row for `both`; each next past
/// the last street's far row, its holdings (`holding` deep, `both` only) and a lane's room.
#[must_use]
pub fn row_offsets(
    frame_depth: f64,
    both: bool,
    streets: usize,
    keep: f64,
    gap: f64,
    holding: f64,
) -> Vec<f64> {
    let first = if both { keep + frame_depth + gap } else { keep };
    let per = if both {
        frame_depth * 2.0 + 2.0 * gap + keep + holding
    } else {
        frame_depth + 2.0 * gap + keep
    };
    (0..streets).map(|i| first + i as f64 * per).collect()
}

/// A holding's rectangle, `along` wide on the tangent `t` and `depth` deep on the normal `n`, about `center`.
#[must_use]
pub fn holding_quad(center: Pt, t: Pt, n: Pt, along: f64, depth: f64) -> Vec<Pt> {
    let (ax, ay) = (t.0 * along / 2.0, t.1 * along / 2.0);
    let (nx, ny) = (n.0 * depth / 2.0, n.1 * depth / 2.0);
    let (cx, cy) = center;
    vec![
        (cx - ax - nx, cy - ay - ny),
        (cx + ax - nx, cy + ay - ny),
        (cx + ax + nx, cy + ay + ny),
        (cx - ax + nx, cy - ay + ny),
    ]
}

/// A convex polygon clipped to the box `(x0, y0, x1, y1)` (Sutherland-Hodgman).
#[must_use]
pub fn clip_to(poly: &[Pt], b: (f64, f64, f64, f64)) -> Vec<Pt> {
    let edges: [(usize, f64, bool); 4] = [
        (0, b.0, true),
        (0, b.2, false),
        (1, b.1, true),
        (1, b.3, false),
    ];
    let mut out = poly.to_vec();
    for (axis, v, lo) in edges {
        let get = |p: Pt| if axis == 0 { p.0 } else { p.1 };
        let keep = |p: Pt| if lo { get(p) >= v } else { get(p) <= v };
        let mut next = Vec::new();
        for k in 0..out.len() {
            let (a, c) = (out[k], out[(k + 1) % out.len()]);
            if keep(a) {
                next.push(a);
            }
            if keep(a) != keep(c) {
                let f = (v - get(a)) / (get(c) - get(a));
                next.push((a.0 + (c.0 - a.0) * f, a.1 + (c.1 - a.1) * f));
            }
        }
        out = next;
    }
    out
}

/// Do two polygons meet - touch or overlap?
#[must_use]
pub fn polys_meet(a: &[Pt], b: &[Pt], tests: &mut Counts) -> bool {
    tests.add("seg_test@polys_meet", (a.len() * b.len()) as u64);
    in_poly(a[0], b)
        || in_poly(b[0], a)
        || (0..a.len()).any(|i| {
            (0..b.len())
                .any(|j| seg_seg(a[i], a[(i + 1) % a.len()], b[j], b[(j + 1) % b.len()]) == 0.0)
        })
}

/// The holding clipped to the sheet's `bounds`, or None where it meets the hard ground or any reserved box, or where less than a
/// quarter of it is on the sheet.
///
/// Research:
///     its drawn sizes - CONVENTION: sizes on the sheet, not in the world - 0.25 (holding drawn only if a quarter of it is on the sheet)
#[must_use]
pub fn holding_clear(
    quad: &[Pt],
    hard: &Hard,
    boxes: &[Rect],
    bounds: (f64, f64, f64, f64),
    tests: &mut Counts,
) -> Option<Vec<Pt>> {
    let clipped = clip_to(quad, bounds);
    if clipped.len() < 3 || area(&clipped) < area(quad) * 0.25 || hard.meets(&clipped, tests) {
        return None;
    }
    (!boxes
        .iter()
        .any(|&b| polys_meet(&box_poly(b), &clipped, tests)))
    .then_some(clipped)
}

/// Is a frame's front door - the middle of its `front` edge, less its lane `pad`, `DOOR_FT.0` out - at least `room` off the hard
/// ground?
#[must_use]
pub fn door_clear(
    frame: Rect,
    front: Pt,
    pad: f64,
    hard: &Hard,
    room: f64,
    tests: &mut Counts,
) -> bool {
    let (x, y, w, h) = frame;
    let reach = front.0.abs() * w / 2.0 + front.1.abs() * h / 2.0 - pad + DOOR_FT.0;
    hard.dist(
        (x + front.0 * reach, y + front.1 * reach),
        room + 1.0,
        tests,
    ) >= room
}

/// Is a row seat's frame refused: its door has no room, it reaches across any of the row's streets, or it stands on a holding
/// already reserved?
#[must_use]
pub fn frame_refused(
    frame: Rect,
    (front, pad, room): (Pt, f64, f64),
    hard: &Hard,
    streets: &[Vec<Pt>],
    holdings: &[Vec<Pt>],
    tests: &mut Counts,
) -> bool {
    if !door_clear(frame, front, pad, hard, room, tests) {
        return true;
    }
    tests.add(
        "seg_test@frame_refused",
        streets.iter().map(|s| s.len() as u64).sum(),
    );
    let fb = box_poly(frame);
    streets.iter().any(|s| {
        s.windows(2)
            .any(|w| super::fit::seg_in_box(w[0], w[1], frame))
    }) || holdings.iter().any(|q| polys_meet(&fb, q, tests))
}

/// The longest run of consecutive `line` samples inside `bounds` (x0, y0, x1, y1); empty where none is.
#[must_use]
pub fn inside_the_sheet(line: &[(Pt, Pt)], bounds: (f64, f64, f64, f64)) -> Line {
    let (mut best, mut run): (&[(Pt, Pt)], usize) = (&[], 0);
    for (k, &(p, _)) in line.iter().enumerate() {
        if bounds.0 <= p.0 && p.0 <= bounds.2 && bounds.1 <= p.1 && p.1 <= bounds.3 {
            run += 1;
            if run > best.len() {
                best = &line[k + 1 - run..=k];
            }
        } else {
            run = 0;
        }
    }
    best.to_vec()
}

/// `pts` set out `d` on its left (`d` < 0 its right) as a true parallel curve, rounded at the joins: the raw offset - each segment
/// set out, a round join round each vertex - sampled every `STEP_FT.1`, every sample nearer the line than `d` dropped (the inside
/// of a bend, where the raw offset loops), the runs either side of a dropped loop joined, the longest run kept.
pub(crate) fn offset_curve(pts: &[Pt], d: f64, tests: &mut Counts) -> Vec<Pt> {
    let segs: Vec<(Pt, Pt)> = pts
        .windows(2)
        .filter(|w| w[0] != w[1])
        .map(|w| (w[0], w[1]))
        .collect();
    if segs.is_empty() {
        return Vec::new();
    }
    let (r, s) = (d.abs(), d.signum());
    let left = |a: Pt, b: Pt| {
        let l = dist(a, b);
        (-(b.1 - a.1) / l * s, (b.0 - a.0) / l * s)
    };
    let step = STEP_FT.1;
    let mut raw: Vec<Pt> = Vec::new();
    let push_run = |raw: &mut Vec<Pt>, a: Pt, b: Pt| {
        let k = 1.max((dist(a, b) / step).ceil() as usize);
        raw.extend((0..=k).map(|i| {
            let f = i as f64 / k as f64;
            (a.0 + (b.0 - a.0) * f, a.1 + (b.1 - a.1) * f)
        }));
    };
    for (i, &(a, b)) in segs.iter().enumerate() {
        let n = left(a, b);
        if i > 0 {
            // the round join, the short way from the last segment's normal to this one's
            let m = left(segs[i - 1].0, segs[i - 1].1);
            let (t0, mut t1) = (m.1.atan2(m.0), n.1.atan2(n.0));
            while t1 - t0 > std::f64::consts::PI {
                t1 -= std::f64::consts::TAU;
            }
            while t0 - t1 > std::f64::consts::PI {
                t1 += std::f64::consts::TAU;
            }
            let k = 1.max(((t1 - t0).abs() * r / step).ceil() as usize);
            raw.extend((1..k).map(|j| {
                let t = t0 + (t1 - t0) * j as f64 / k as f64;
                (a.0 + t.cos() * r, a.1 + t.sin() * r)
            }));
        }
        push_run(
            &mut raw,
            (a.0 + n.0 * r, a.1 + n.1 * r),
            (b.0 + n.0 * r, b.1 + n.1 * r),
        );
    }
    let base = Hard::line(pts, tests);
    // a sample short of `r` by less than a twentieth of a foot is on the curve: a 2 ft chord of a concave line ends inside its
    // neighbor's offset by r * theta^2 / 2, a thousandth of a foot, and a tighter tolerance dropped every chord whole
    let tol = STEP_FT.1 / 40.0;
    let mut runs: Vec<Vec<Pt>> = Vec::new();
    let mut open = false;
    for q in raw {
        if base.dist(q, r + 1.0, tests) < r - tol {
            open = false;
            continue;
        }
        // a run resumed within three steps of the last one's end is one run: the two sides of a dropped loop
        let join = runs
            .last()
            .is_some_and(|l: &Vec<Pt>| dist(l[l.len() - 1], q) <= 3.0 * step);
        match runs.last_mut() {
            Some(l) if open || join => {
                // (two segments' shared end, set out twice, coincides only to the float's error: kept once, or the next offset
                // turns round a segment of no length)
                if dist(l[l.len() - 1], q) > STEP_FT.1 / 20.0 {
                    l.push(q);
                }
            }
            _ => runs.push(vec![q]),
        }
        open = true;
    }
    runs.into_iter()
        .filter(|r| r.len() >= 2)
        .max_by(|a, b| poly_len(a).total_cmp(&poly_len(b)))
        .unwrap_or_default()
}

/// An open polyline's length.
fn poly_len(pts: &[Pt]) -> f64 {
    pts.windows(2).map(|w| dist(w[0], w[1])).sum()
}

/// `line` set out `d` on its outward side (the next street of a row village), as a true parallel curve rounded on the inside of a
/// corner at `radius` (set out `d + radius`, then back `radius`: a closing), resampled at the line's own spacing, each sample's
/// normal square to the new street's own tangent on the first street's outward side.
#[must_use]
pub fn parallel(line: &[(Pt, Pt)], d: f64, radius: f64, tests: &mut Counts) -> Line {
    if line.len() < 2 || d == 0.0 {
        return line
            .iter()
            .map(|&(p, n)| ((p.0 + n.0 * d, p.1 + n.1 * d), n))
            .collect();
    }
    let pts: Vec<Pt> = line.iter().map(|s| s.0).collect();
    // the outward side from the normals themselves: each sample's normal asked whether it stands left of the line's tangent
    let left: f64 = line
        .windows(2)
        .map(|w| {
            let ((a, n), (b, _)) = (w[0], w[1]);
            n.0 * -(b.1 - a.1) + n.1 * (b.0 - a.0)
        })
        .sum();
    let side = (if left >= 0.0 { 1.0 } else { -1.0 }) * d.signum();
    let mut coords = offset_curve(&pts, side * (d.abs() + radius), tests);
    if radius > 0.0 && coords.len() >= 2 {
        coords = offset_curve(&coords, -side * radius, tests);
    }
    if coords.len() < 2 {
        return Vec::new();
    }
    let total = poly_len(&coords);
    let step = dist(pts[0], pts[1]).max(1.0);
    let k = 1.max((total / step).floor() as usize);
    let qs: Vec<Pt> = (0..=k)
        .map(|i| along(&coords, total * i as f64 / k as f64))
        .collect();
    tests.add("seg_test@parallel", (qs.len() * line.len()) as u64);
    (0..qs.len())
        .map(|i| {
            let (a, b) = (qs[i.saturating_sub(1)], qs[(i + 1).min(qs.len() - 1)]);
            let tl = dist(a, b);
            let tl = if tl == 0.0 { 1.0 } else { tl };
            let n0 = line
                .iter()
                .min_by(|x, y| dist(x.0, qs[i]).total_cmp(&dist(y.0, qs[i])))
                .map_or((0.0, 0.0), |s| s.1);
            let (nx, ny) = (-(b.1 - a.1) / tl, (b.0 - a.0) / tl);
            (
                qs[i],
                if nx * n0.0 + ny * n0.1 >= 0.0 {
                    (nx, ny)
                } else {
                    (-nx, -ny)
                },
            )
        })
        .collect()
}

/// The point at arc length `s` along an open polyline (clamped to its ends).
fn along(pts: &[Pt], s: f64) -> Pt {
    let mut s = s.max(0.0);
    for w in pts.windows(2) {
        let l = dist(w[0], w[1]);
        if s <= l && l > 0.0 {
            return (
                w[0].0 + (w[1].0 - w[0].0) * s / l,
                w[0].1 + (w[1].1 - w[0].1) * s / l,
            );
        }
        s -= l;
    }
    pts[pts.len() - 1]
}

/// What a row seat's frame is judged by: the frame itself (its offset from the house, its size), whether both sides of the street
/// are seated, the frame's gap off the street, the sheet's bounds, and the front face, its lane pad and the door's room.
#[derive(Clone, Copy, Debug)]
pub struct Frames {
    /// The frame (its center's offset from the house, its width and height).
    pub frame: Rect,
    /// Both sides of the street?
    pub both: bool,
    /// The frame's gap off the street's centerline.
    pub gap: f64,
    /// The sheet's bounds a frame stays inside.
    pub bounds: (f64, f64, f64, f64),
    /// The front face (a page direction), its lane pad and the door's room.
    pub door: (Pt, f64, f64),
}

/// How many of a line's row seats hold a frame clear of the hard ground, inside the bounds, with room at its door.
#[must_use]
pub fn clear_frames(line: &[(Pt, Pt)], fr: &Frames, hard: &Hard, tests: &mut Counts) -> usize {
    let (w, h) = (fr.frame.2, fr.frame.3);
    let b = fr.bounds;
    row_seats(line, fr.frame, fr.both, fr.gap, row_step(line, fr.frame))
        .into_iter()
        .filter(|&((fx, fy), ..)| {
            tests.add("candidate@clear_frames", 1);
            let inside = b.0 <= fx - w / 2.0
                && fx + w / 2.0 <= b.2
                && b.1 <= fy - h / 2.0
                && fy + h / 2.0 <= b.3;
            inside
                && !hard.meets(&box_poly((fx, fy, w, h)), tests)
                && door_clear((fx, fy, w, h), fr.door.0, fr.door.1, hard, fr.door.2, tests)
        })
        .count()
}

/// How many farms a row whose first street is the line given holds, its further streets with it.
pub type Capacity<'a> = dyn Fn(&[(Pt, Pt)], &mut Counts) -> usize + 'a;

/// The first street of a row village: of the lines centered on the planned seat's point of the hard ground's edge grown by
/// `offset` and on 16 points of that edge within a row's `length` either way of it, the one whose whole row - this street and the
/// streets `capacity` sets out beside it, each on the sheet - holds the most farms, then the one holding the most clear frames
/// itself, the nearest the seat among equals. Empty where there is no hard ground.
///
/// Research:
///     where the street runs - research/questions/0033-row-villages-resson.drawing.html: the stretch within a row's length of the seat that holds the most farms - the whole row's farms, its further streets with it: ranked by its first street alone, a row against the sheet's edge set its further streets off the sheet and seated 8 of 13 (the Rust stage gate, seed 406155)
#[must_use]
pub fn best_row_line(
    hard: &Hard,
    anchor: Pt,
    (offset, length, slack): (f64, f64, f64),
    form: Form,
    fr: &Frames,
    capacity: &Capacity,
    tests: &mut Counts,
) -> Line {
    const SAMPLES: usize = 16;
    let Some(ring) = ring_near(hard, anchor, offset, tests) else {
        return Vec::new();
    };
    let (s0, total) = (project(&ring, anchor), ring_length(&ring));
    // ...within one row's length of the seat along the edge (cohort seed 12: a stretch at the sheet's far side was refused)
    let near = (total / 2.0).min(length);
    let tries = std::iter::once(anchor).chain((0..SAMPLES).map(|k| {
        interpolate(
            &ring,
            s0 + near * (2.0 * k as f64 / (SAMPLES - 1) as f64 - 1.0),
        )
    }));
    let mut best: Option<((usize, usize, f64), Line)> = None;
    for a in tries {
        tests.add("candidate@best_row_line", 1);
        let line = street_on(&ring, hard, a, length, form, slack, tests);
        let score = (
            capacity(&line, tests),
            clear_frames(&line, fr, hard, tests),
            -dist(a, anchor),
        );
        if best.as_ref().is_none_or(|b| {
            score.0 > b.0 .0
                || (score.0 == b.0 .0
                    && (score.1 > b.0 .1 || (score.1 == b.0 .1 && score.2 > b.0 .2)))
        }) {
            best = Some((score, line));
        }
    }
    best.map(|b| b.1).unwrap_or_default()
}
