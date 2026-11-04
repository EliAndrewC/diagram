//! A household's way, leg by leg (feature 444 T30): the tests every leg of a household's way is asked of its own homestead - off
//! its house by the tread and the wall's setback, off its fixtures and well at the corridor's half-width, its tread off its beds
//! and outbuildings - where it may start (its dooryard's doors), that it leaves its yard once and is drawn from where it leaves it,
//! the taut pull, and the access tree the admitted ways are reserved in (`rolling/access.py`, `rolling/route.py` `taut`).
//!
//! Research:
//!     a household's way - NONE: the corridor's machinery; each rule's claim is at its function or constant
#![expect(
    clippy::many_single_char_names,
    reason = "the plane geometry's own names"
)]

use std::collections::HashMap;

use super::bundle::Bundle;
use super::fixtures::Kind;
use super::layout::Rect;
use super::Counts;
use crate::field::fan::Pt;
use crate::field::geom::{dist, seg_dist};

/// The corridor's room either side of the way's line (ft).
///
/// Research:
///     corridor room - DEVIATION research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: 7 ft either side of the way's line, so a 3 ft tread's edge may pass 5.5 ft off a fence
pub const ACCESS_HALF_FT: f64 = 7.0;

/// A footpath's half-tread, a tread's setback off a wall, and the corridor's margin (ft).
///
/// Research:
///     footpath tread - research/questions/0081-village-lanes.html, research/questions/0081-village-lanes.drawing.html: 3 ft wide, the field road's 3 shaku
///     tread clear of a wall - research/questions/0081-village-lanes.drawing.html: 3 ft, a Japanese village house's setback from a road and within a north Chinese house's drip strip
///     the corridor's margin - GUESS: no source could speak to it, a value of ours (feature 417 T36 pass P3, 2026-10-25); `PART_MARGIN_FT`, half a foot more
pub const TREAD: (f64, f64, f64) = (1.5, 3.0, 0.5);

/// A persimmon's trunk box, the part of it a way keeps off (ft).
///
/// Research:
///     a persimmon by its trunk alone - GUESS: held off by a 4 ft trunk box, the crown free to overhang the path
pub const TRUNK_FT: f64 = 4.0;

/// A turn a corridor never takes (degrees): at this or more it doubles back.
///
/// Research:
///     hairpin turn - research/questions/0081-village-lanes.drawing.html: a turn of more than 140 degrees, which a lane never takes (`doubles_back` refuses 140 itself too)
pub const HAIRPIN_DEG: f64 = 140.0;

/// How far past the yard's tread a corridor is drawn from (ft).
///
/// Research:
///     path not drawn on its own yard - GUESS: searched, the record silent (feature 417 T36 pass P3, 2026-10-25); the drawn path starts where it leaves the threshing yard, a foot past its tread
pub const YARD_EXIT_PAD_FT: f64 = 1.0;

/// The gap a corridor's line keeps off its own house: the half-tread, the wall's setback and the margin.
///
/// Research:
///     a corridor off its own house - research/questions/0081-village-lanes.drawing.html: the line a 3 ft footpath's half-tread and the 3 ft a tread keeps off a farmhouse wall off the wall, 5 ft in all with the margin
#[must_use]
pub fn house_gap() -> f64 {
    TREAD.0 + TREAD.1 + TREAD.2
}

/// The least distance from the segment a-b to the box `(cx, cy, w, h)`; 0 where they meet (its clip to the box, Liang-Barsky,
/// leaves a part).
#[must_use]
pub fn seg_box_gap(a: Pt, b: Pt, bx: Rect) -> f64 {
    let (x0, y0, x1, y1) = (
        bx.0 - bx.2 / 2.0,
        bx.1 - bx.3 / 2.0,
        bx.0 + bx.2 / 2.0,
        bx.1 + bx.3 / 2.0,
    );
    if super::track_out::clip(a, b, (x0, y0, x1, y1)).is_some() {
        return 0.0;
    }
    let ends = [a, b]
        .iter()
        .map(|p| {
            let gx = (x0 - p.0).max(p.0 - x1).max(0.0);
            let gy = (y0 - p.1).max(p.1 - y1).max(0.0);
            gx.hypot(gy)
        })
        .fold(f64::INFINITY, f64::min);
    [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
        .iter()
        .map(|&q| seg_dist(q, a, b))
        .fold(ends, f64::min)
}

/// Is the segment a-b nearer than `t` to the box? The box beyond the segment's own box grown by `t` is not; the center's distance
/// from the line decides where it can, the exact gap the rest.
#[must_use]
pub fn seg_box_within(a: Pt, b: Pt, bx: Rect, t: f64, tests: &mut Counts) -> bool {
    tests.add("dist@seg_box_within", 1);
    if a.0.min(b.0) - t > bx.0 + bx.2 / 2.0
        || a.0.max(b.0) + t < bx.0 - bx.2 / 2.0
        || a.1.min(b.1) - t > bx.1 + bx.3 / 2.0
        || a.1.max(b.1) + t < bx.1 - bx.3 / 2.0
    {
        return false;
    }
    let d = seg_dist((bx.0, bx.1), a, b);
    if d < t {
        return true;
    }
    if d - bx.2.hypot(bx.3) / 2.0 >= t {
        return false;
    }
    seg_box_gap(a, b, bx) < t
}

/// The parts of a homestead a household's way reads, from its bundle: the house's turned box, the yard's, the beds', the annexes'
/// and each fixture's with its kind.
#[must_use]
pub fn parts_of(b: &Bundle) -> Parts {
    let mut it = b.boxes.iter().copied();
    let house = it.next().unwrap_or(b.house);
    let yard = it.next().unwrap_or(b.yard);
    let gardens: Vec<Rect> = it.by_ref().take(b.gardens.len()).collect();
    let sheds: Vec<Rect> = it
        .by_ref()
        .take(usize::from(b.kura.is_some()) + usize::from(b.byre.is_some()))
        .collect();
    let fixtures = b.fixtures.iter().map(|f| f.0).zip(it).collect();
    Parts {
        house,
        yard,
        gardens,
        sheds,
        fixtures,
        raw: (b.house, b.yard),
        turn: b.turn,
        well: None,
    }
}

/// A homestead's parts as its way reads them.
#[derive(Clone, Debug, PartialEq)]
pub struct Parts {
    /// The house's turned box.
    pub house: Rect,
    /// The yard's turned box.
    pub yard: Rect,
    /// The beds' turned boxes.
    pub gardens: Vec<Rect>,
    /// The storehouse annex's and the byre's.
    pub sheds: Vec<Rect>,
    /// Each fixture's, with its kind.
    pub fixtures: Vec<(Kind, Rect)>,
    /// The house and the yard before the turn.
    pub raw: (Rect, Rect),
    /// The turn (degrees).
    pub turn: f64,
    /// The well pocket's wellhead, where the household has one (a dispersed farm's, or a nucleated household's own).
    pub well: Option<Rect>,
}

impl Parts {
    /// Does the leg keep the house gap off its own house?
    #[must_use]
    pub fn house_clear(&self, a: Pt, b: Pt, tests: &mut Counts) -> bool {
        !seg_box_within(a, b, self.house, house_gap(), tests)
    }

    /// The boxes a way's line keeps off at the corridor's half-width: the well pocket's wellhead, then each fixture's (a persimmon
    /// by its trunk).
    ///
    /// Research:
    ///     path clear of its own well - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: nothing built on a lane; the wellhead's own box
    ///
    /// Research:
    ///     path clear of its own fixtures - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: routed round its own garden beds and fixtures - the corridor off privy, stack and shed
    ///     fixtures held off at the corridor's half-width - GUESS research/questions/0081-village-lanes.drawing.html: no page gives how far a household's own way keeps off its own fixtures or well; held off at the corridor's half-width (`ACCESS_HALF_FT`, 7 ft from the line), so a 3 ft tread's edge stands 5.5 ft off
    #[must_use]
    pub fn fixture_gaps(&self) -> Vec<(Rect, f64)> {
        self.well
            .iter()
            .map(|&w| (w, ACCESS_HALF_FT))
            .chain(self.fixtures.iter().map(|&(k, r)| {
                let r = if k == Kind::Persimmon {
                    (r.0, r.1, TRUNK_FT, TRUNK_FT)
                } else {
                    r
                };
                (r, ACCESS_HALF_FT)
            }))
            .collect()
    }

    /// The boxes a way's tread keeps off: the annexes by the tread and the wall's setback, the beds by the tread.
    ///
    /// Research:
    ///     path off its own beds - research/questions/0081-village-lanes.drawing.html, research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: a lane never crosses row crops and nothing is built on it; the tread's 0.5 ft margin is 0246's half foot spare at each side of the 3 ft footpath, a map drawing convention
    ///     tread 3 ft off its own kura and byre - research/questions/0081-village-lanes.drawing.html: the maps keep the same 3 ft off a farmstead's other buildings as off its farmhouse wall
    #[must_use]
    pub fn part_gaps(&self) -> Vec<(Rect, f64)> {
        let (gap, wall) = (TREAD.0 + TREAD.2, house_gap());
        self.sheds
            .iter()
            .map(|&r| (r, wall))
            .chain(self.gardens.iter().map(|&r| (r, gap)))
            .collect()
    }

    /// Does the leg clear its own fixtures?
    #[must_use]
    pub fn fixtures_clear(&self, a: Pt, b: Pt, tests: &mut Counts) -> bool {
        !self
            .fixture_gaps()
            .iter()
            .any(|&(r, t)| seg_box_within(a, b, r, t, tests))
    }

    /// Does the leg's tread clear its own beds and outbuildings?
    #[must_use]
    pub fn parts_clear(&self, a: Pt, b: Pt, tests: &mut Counts) -> bool {
        !self
            .part_gaps()
            .iter()
            .any(|&(r, t)| seg_box_within(a, b, r, t, tests))
    }

    /// Where a homestead's way may start, in preference order, in its dooryard: the forecourt, the yard's far edge, then the
    /// dooryard's two flanks carried out past the gable by `half` and a foot.
    ///
    /// Research:
    ///     path starts in the dooryard - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: forecourt, then the yard's far edge, then the two flanks past the gable; never a back wall
    #[must_use]
    pub fn doors(&self, half: f64) -> Vec<Pt> {
        let (h, y) = (self.house, self.yard);
        let d = dist((y.0, y.1), (h.0, h.1));
        let d = if d == 0.0 { 1.0 } else { d };
        let (ux, uy) = ((y.0 - h.0) / d, (y.1 - h.1) / d);
        let (s, c) = self.turn.to_radians().sin_cos();
        let (tw, th) = (self.raw.1 .2, self.raw.1 .3);
        let along = tw / 2.0 * (ux * c + uy * s).abs() + th / 2.0 * (-ux * s + uy * c).abs();
        let across = (y.2 / 2.0 * uy.abs() + y.3 / 2.0 * ux.abs())
            .max(h.2 / 2.0 * uy.abs() + h.3 / 2.0 * ux.abs() + half + 1.0);
        vec![
            (y.0, y.1),
            (y.0 + ux * along, y.1 + uy * along),
            (y.0 - uy * across, y.1 + ux * across),
            (y.0 + uy * across, y.1 - ux * across),
        ]
    }

    /// The threshing yard as the overlap matrix reads it: its rect turned with its house.
    #[must_use]
    pub fn yard_quad(&self) -> [Pt; 4] {
        let (x, y, w, h) = self.raw.1;
        let (s, c) = self.turn.to_radians().sin_cos();
        [
            (-w / 2.0, -h / 2.0),
            (w / 2.0, -h / 2.0),
            (w / 2.0, h / 2.0),
            (-w / 2.0, h / 2.0),
        ]
        .map(|(dx, dy)| (x + dx * c - dy * s, y + dx * s + dy * c))
    }

    /// The threshing yard as the least that will be drawn of it - its rect shrunk by the drawing's jitter and turned with its
    /// house - the record a way's end is judged to reach (`tree.records_of`).
    ///
    /// Research:
    ///     the yard drawn - NONE: the drawing's 0.10 jitter of the yard's corners, which every drawn yard contains
    #[must_use]
    pub fn yard_records_quad(&self) -> Vec<Pt> {
        let (x, y, w, h) = self.raw.1;
        let k = 1.0 - 0.10;
        let (s, c) = self.turn.to_radians().sin_cos();
        [
            (-w * k / 2.0, -h * k / 2.0),
            (w * k / 2.0, -h * k / 2.0),
            (w * k / 2.0, h * k / 2.0),
            (-w * k / 2.0, h * k / 2.0),
        ]
        .iter()
        .map(|&(dx, dy)| (x + dx * c - dy * s, y + dx * s + dy * c))
        .collect()
    }

    /// The corridor as the web will draw it: from where its tread leaves the homestead's own yard, else as found.
    #[must_use]
    pub fn drawn_corridor(&self, corridor: &[Pt]) -> Vec<Pt> {
        past_the_yard(corridor, &self.yard_quad(), TREAD.0)
            .filter(|p| p.len() >= 2)
            .unwrap_or_else(|| corridor.to_vec())
    }
}

/// `not seg_box_within(q, q, ...)` for every gap - a point's distance to each box, compared squared.
#[must_use]
pub fn point_clear(q: Pt, gaps: &[(Rect, f64)]) -> bool {
    gaps.iter().all(|&((cx, cy, w, h), t)| {
        let (ex, ey) = (
            ((q.0 - cx).abs() - w / 2.0).max(0.0),
            ((q.1 - cy).abs() - h / 2.0).max(0.0),
        );
        !(ex * ex + ey * ey < t * t && t > 0.0)
    })
}

/// Does the run a-b-c turn at b by a hairpin's turn or more?
///
/// Research:
///     path never doubles back - research/questions/0081-village-lanes.drawing.html: a turn at `HAIRPIN_DEG` or more refuses the corridor
#[must_use]
pub fn doubles_back(a: Pt, b: Pt, c: Pt) -> bool {
    let (u, v) = ((b.0 - a.0, b.1 - a.1), (c.0 - b.0, c.1 - b.1));
    let (nu, nv) = (u.0.hypot(u.1), v.0.hypot(v.1));
    if nu < 1e-9 || nv < 1e-9 {
        return false;
    }
    ((u.0 * v.0 + u.1 * v.1) / (nu * nv))
        .clamp(-1.0, 1.0)
        .acos()
        .to_degrees()
        >= HAIRPIN_DEG
}

/// Does a corridor leave its own yard (grown by `gap`) at most once, sampled every 2 ft, never to cross it again?
///
/// Research:
///     path leaves its yard once - GUESS: searched, the record silent (feature 417 T36 pass P3, 2026-10-25); a corridor that re-enters its own threshing yard is refused
#[must_use]
pub fn leaves_its_yard(corridor: &[Pt], yard: Rect, gap: f64) -> bool {
    let inside = |p: Pt| {
        (p.0 - yard.0).abs() < yard.2 / 2.0 + gap && (p.1 - yard.1).abs() < yard.3 / 2.0 + gap
    };
    let mut left = false;
    for w in corridor.windows(2) {
        let (a, b) = (w[0], w[1]);
        #[expect(
            clippy::cast_possible_truncation,
            clippy::cast_sign_loss,
            reason = "a few hundred 2 ft steps"
        )]
        let n = ((dist(a, b) / 2.0) as u32).max(1);
        for k in 0..=n {
            let f = f64::from(k) / f64::from(n);
            if inside((a.0 + (b.0 - a.0) * f, a.1 + (b.1 - a.1) * f)) {
                if left {
                    return false;
                }
            } else {
                left = true;
            }
        }
    }
    true
}

/// The distance from `p` to a convex quad (0 inside it).
fn quad_dist(p: Pt, q: &[Pt; 4]) -> f64 {
    if crate::field::geom::inside(p, q) {
        return 0.0;
    }
    (0..4)
        .map(|k| seg_dist(p, q[k], q[(k + 1) % 4]))
        .fold(f64::INFINITY, f64::min)
}

/// `run` from where its tread, `half` either side, leaves the yard quad for good: the run past the last point within `half` and
/// the pad of the yard. None where the run never comes that near the yard, or ends on it.
#[must_use]
pub fn past_the_yard(run: &[Pt], yard: &[Pt; 4], half: f64) -> Option<Vec<Pt>> {
    let r = half + YARD_EXIT_PAD_FT;
    let at = |a: Pt, b: Pt, t: f64| (a.0 + (b.0 - a.0) * t, a.1 + (b.1 - a.1) * t);
    // the distance to a convex quad is convex along a segment: on each, the last t within r is the end, or found by halving from
    // the segment's nearest point (a ternary search) to its end
    let mut acc = 0.0;
    let mut last: Option<f64> = None;
    for w in run.windows(2) {
        let (a, b) = (w[0], w[1]);
        let d = dist(a, b);
        let f = |t: f64| quad_dist(at(a, b, t), yard);
        let t = if f(1.0) <= r {
            Some(1.0)
        } else {
            let (mut lo, mut hi) = (0.0, 1.0);
            for _ in 0..60 {
                let (m1, m2) = (lo + (hi - lo) / 3.0, hi - (hi - lo) / 3.0);
                if f(m1) <= f(m2) {
                    hi = m2;
                } else {
                    lo = m1;
                }
            }
            (f(lo) <= r).then(|| {
                let (mut i, mut o) = (lo, 1.0);
                for _ in 0..60 {
                    let m = f64::midpoint(i, o);
                    if f(m) <= r {
                        i = m;
                    } else {
                        o = m;
                    }
                }
                i
            })
        };
        if let Some(t) = t {
            last = Some(acc + t * d);
        }
        acc += d;
    }
    let s0 = last?;
    if s0 >= acc - 1.0 {
        return None;
    }
    let mut out = Vec::new();
    let mut acc = 0.0;
    for w in run.windows(2) {
        let (a, b) = (w[0], w[1]);
        let d = dist(a, b);
        if acc + d > s0 && d > 0.0 {
            if out.is_empty() {
                out.push(at(a, b, ((s0 - acc) / d).max(0.0)));
            }
            out.push(b);
        }
        acc += d;
    }
    Some(out)
}

/// The polyline through `pts` pulled taut: from each point the farthest later point a leg to which `leg_ok` admits without
/// turning back on the leg before; None where a point admits no leg onward or more than `most` legs are needed.
///
/// Research:
///     path pulled taut - research/questions/0081-village-lanes.drawing.html: straight from point to point where it can, never doubling back
pub fn taut(
    pts: &[Pt],
    leg_ok: &mut dyn FnMut(Pt, Pt) -> bool,
    most: usize,
    tests: &mut Counts,
) -> Option<Vec<Pt>> {
    let mut out = vec![pts[0]];
    let mut k = 0;
    while k < pts.len() - 1 {
        tests.add("candidate@taut", 1);
        if out.len() > most {
            return None;
        }
        let far = (k + 1..pts.len()).rev().find(|&m| {
            leg_ok(pts[k], pts[m])
                && (out.len() < 2 || !doubles_back(out[out.len() - 2], out[out.len() - 1], pts[m]))
        })?;
        out.push(pts[far]);
        k = far;
    }
    (out.len() - 1 <= most).then_some(out)
}

#[expect(clippy::cast_possible_truncation, reason = "cells of a few hundred")]
fn cell(v: f64) -> i64 {
    (v / 128.0).floor() as i64
}

/// The reserved corridors: segments a footpath wide, `half` either side, and the passages' walks kept clear as one, filed by
/// their widened boxes.
///
/// Research:
///     every house reached by a path - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: each household's way laid in the gaps to the track out, no later homestead covering it - but for the few households reached across a neighbor's yard
///     its salts, guards and sentinels - NONE: they decide nothing about the place - 128 (spatial-index cell)
#[derive(Default)]
pub struct AccessTree {
    /// The corridors' segments, in the order reserved.
    pub segs: Vec<(Pt, Pt)>,
    /// The corridors' half-width.
    pub half: f64,
    walks: Vec<(Pt, Pt)>,
    grid: HashMap<(i64, i64), Vec<usize>>,
}

impl AccessTree {
    /// An empty tree of corridors `half` either side.
    #[must_use]
    pub fn new(half: f64) -> Self {
        Self {
            half,
            ..Self::default()
        }
    }

    fn file(&mut self, a: Pt, b: Pt) {
        let k = self.walks.len();
        self.walks.push((a, b));
        let h = self.half;
        for i in cell(a.0.min(b.0) - h)..=cell(a.0.max(b.0) + h) {
            for j in cell(a.1.min(b.1) - h)..=cell(a.1.max(b.1) + h) {
                self.grid.entry((i, j)).or_default().push(k);
            }
        }
    }

    /// Reserve a corridor's leg.
    pub fn add(&mut self, a: Pt, b: Pt) {
        self.segs.push((a, b));
        self.file(a, b);
    }

    /// Keep the walk a-b clear of every later homestead as a corridor is, without making it a corridor (a passage, a drawn leg).
    ///
    /// Research:
    ///     a passage walk kept clear - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: on the two households' land, never drawn as a lane
    pub fn bar(&mut self, a: Pt, b: Pt) {
        self.file(a, b);
    }

    /// Does any corridor's strip, or a kept walk, meet the box?
    #[must_use]
    pub fn covers_box(&self, bx: Rect, tests: &mut Counts) -> bool {
        let (x0, y0, x1, y1) = (
            bx.0 - bx.2 / 2.0,
            bx.1 - bx.3 / 2.0,
            bx.0 + bx.2 / 2.0,
            bx.1 + bx.3 / 2.0,
        );
        let mut seen = Vec::new();
        for i in cell(x0)..=cell(x1) {
            for j in cell(y0)..=cell(y1) {
                for &k in self.grid.get(&(i, j)).map_or(&[][..], Vec::as_slice) {
                    if seen.contains(&k) {
                        continue;
                    }
                    seen.push(k);
                    let (a, b) = self.walks[k];
                    if seg_box_within(a, b, bx, self.half, tests) {
                        return true;
                    }
                }
            }
        }
        false
    }
}
