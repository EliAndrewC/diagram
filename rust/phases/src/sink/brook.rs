//! The brook as the sink reads it (feature 444 T26 D4, D5): the course as drawn, its points in order along the fall, so the
//! stretch beside a pond or a run is found by bisection, and only the points read are read.
//!
//! Research:
//!     the brook as read - NONE: its reading and geometry; each rule's claim is at the unit that keeps it

#![expect(
    clippy::many_single_char_names,
    reason = "the plane geometry's own names"
)]

use std::collections::HashMap;

use crate::field::fan::Pt;
use crate::field::geom::{dist, seg_dist};

/// The stations of a course, read one at a time.
pub trait Stations {
    /// How many stations.
    fn len(&self) -> usize;
    /// Station `i` (each read counted by the reader).
    fn at(&mut self, i: usize) -> Pt;
}

impl Stations for Vec<Pt> {
    fn len(&self) -> usize {
        Vec::len(self)
    }
    fn at(&mut self, i: usize) -> Pt {
        self[i]
    }
}

/// A course's half-width at which another channel's end meets it at a confluence (feet).
///
/// Research:
///     a joiner meets the water - research/questions/0054-which-way-water-flows-and-how-channels-bend-and-join.drawing.html: "a meeting is a junction when either channel's end lies inside the other's drawn width"
pub const JOIN_TOL_SHARE: f64 = 0.5;
/// Two courses nearer than this are one course or a junction, not twins (feet).
///
/// Research:
///     twin band floor - research/questions/0067-do-two-ditches-run-side-by-side-across-the-fields-not-in-the-old-forms-the-map-draws.html: "within about 12 to 32 ft of it" - the floor of the band, which the page records as a guess
pub const TWIN_LO: f64 = 12.0;
/// The twins' band's ceiling (feet).
///
/// Research:
///     twin band ceiling - research/questions/0067-do-two-ditches-run-side-by-side-across-the-fields-not-in-the-old-forms-the-map-draws.html: "within about 12 to 32 ft of it" - the ceiling of the band, which the page records as a guess
pub const TWIN_HI: f64 = 32.0;
/// Running the same way: within this of the other's bearing (degrees).
///
/// Research:
///     running the same way - GUESS: research/questions/0067-do-two-ditches-run-side-by-side-across-the-fields-not-in-the-old-forms-the-map-draws.html says "running the same way" and gives no angle; within 15 deg of the other's bearing is ours
pub const TWIN_DEG: f64 = 15.0;
/// Longer than this side by side is a twin (feet).
///
/// Research:
///     twin run - research/questions/0067-do-two-ditches-run-side-by-side-across-the-fields-not-in-the-old-forms-the-map-draws.html: "for more than 60 ft past where it leaves" - the run, which the page records as a guess, a sixth of the shortest delivery
pub const TWIN_RUN: f64 = 60.0;
/// The twin measure's sampling step along a run (feet).
///
/// Research:
///     the twin's samples - NONE: measuring resolution, five feet
pub const TWIN_STEP: f64 = 5.0;

/// The brook, read through `Stations`, its stations' places along the fall cached as read.
pub struct Brook<'a> {
    src: &'a mut dyn Stations,
    fall: Pt,
    seen: HashMap<usize, Pt>,
    /// Stations read, and segments tested, for the counters (D7).
    pub reads: u64,
    pub tests: u64,
    rising: bool,
}

impl<'a> Brook<'a> {
    /// The brook over `src`, falling along `fall` (a unit vector): which way its points run, read from its two ends.
    ///
    /// Research:
    ///     the brook's order - NONE: the field lays its brook a station at a time, each a station further down the fall (`field::brook::brook`), and the drawn course's arcs turn between two falling legs, so its points stand in order along the fall
    pub fn new(src: &'a mut dyn Stations, fall: Pt) -> Self {
        let mut b = Brook {
            src,
            fall,
            seen: HashMap::new(),
            reads: 0,
            tests: 0,
            rising: true,
        };
        if b.len() >= 2 {
            let n = b.len();
            b.rising = b.u(n - 1) >= b.u(0);
        }
        b
    }

    /// How many stations.
    pub fn len(&self) -> usize {
        self.src.len()
    }

    /// Station `i`.
    pub fn at(&mut self, i: usize) -> Pt {
        if let Some(&p) = self.seen.get(&i) {
            return p;
        }
        self.reads += 1;
        let p = self.src.at(i);
        self.seen.insert(i, p);
        p
    }

    fn u(&mut self, i: usize) -> f64 {
        let p = self.at(i);
        p.0 * self.fall.0 + p.1 * self.fall.1
    }

    /// Station `i`'s place in the brook's order of falling: its place along the fall, negated where the stations run uphill.
    fn key(&mut self, i: usize) -> f64 {
        if self.rising {
            self.u(i)
        } else {
            -self.u(i)
        }
    }

    /// The first station whose key is at least `k` (`above`: past `k`).
    fn first_from(&mut self, k: f64, above: bool) -> usize {
        let (mut lo, mut hi) = (0, self.len());
        while lo < hi {
            let mid = usize::midpoint(lo, hi);
            let key = self.key(mid);
            if key < k || (above && key <= k) {
                lo = mid + 1;
            } else {
                hi = mid;
            }
        }
        lo
    }

    /// The segments `(i, i + 1)` of the brook that can reach places along the fall between `lo` and `hi`: from the one ending at or
    /// past `lo` to the one starting at or before `hi`.
    pub fn span(&mut self, lo: f64, hi: f64) -> std::ops::Range<usize> {
        if self.len() < 2 {
            return 0..0;
        }
        let (a, b) = if self.rising { (lo, hi) } else { (-hi, -lo) };
        let first = self.first_from(a, false);
        let last = self.first_from(b, true);
        first.saturating_sub(1)..last.min(self.len() - 1)
    }

    /// Segment `i` of the brook.
    pub fn seg(&mut self, i: usize) -> (Pt, Pt) {
        self.tests += 1;
        (self.at(i), self.at(i + 1))
    }

    /// The distance from `p` to the brook, over the segments whose places along the fall lie within `reach` of `p`'s.
    pub fn dist_near(&mut self, p: Pt, reach: f64) -> f64 {
        let u = p.0 * self.fall.0 + p.1 * self.fall.1;
        let mut best = f64::INFINITY;
        for i in self.span(u - reach, u + reach) {
            let (a, b) = self.seg(i);
            best = best.min(seg_dist(p, a, b));
        }
        best
    }

    /// Whether `run` crosses the brook away from a confluence (0054: a ditch meets the brook only at a confluence, never across
    /// it): neither end of the run within the brook's half drawn width `w`, and a leg crossing a brook segment properly.
    ///
    /// Research:
    ///     no crossing mid-run - research/questions/0054-which-way-water-flows-and-how-channels-bend-and-join.html: a ditch meets the brook only at a confluence, never across it
    ///     either end makes the junction - research/questions/0054-which-way-water-flows-and-how-channels-bend-and-join.drawing.html: "a meeting is a junction when either channel's end lies inside the other's drawn width"
    pub fn crossed(&mut self, run: &[Pt], w: f64) -> bool {
        if run.len() < 2 || self.len() < 2 {
            return false;
        }
        // an end of the run within the brook's half drawn width is its mouth: a crossing there is the junction, any other a crossing
        let tol = JOIN_TOL_SHARE * w;
        let mouths: Vec<Pt> = [run[0], run[run.len() - 1]]
            .into_iter()
            .filter(|&e| self.dist_near(e, tol) < tol)
            .collect();
        for leg in run.windows(2) {
            let (ua, ub) = (
                leg[0].0 * self.fall.0 + leg[0].1 * self.fall.1,
                leg[1].0 * self.fall.0 + leg[1].1 * self.fall.1,
            );
            for i in self.span(ua.min(ub), ua.max(ub)) {
                let (a, b) = self.seg(i);
                if proper_cross(leg[0], leg[1], a, b)
                    && !mouths.iter().any(|&m| {
                        seg_dist(m, a, b) < tol
                            && (dist(m, leg[0]) < 2.0 * tol || dist(m, leg[1]) < 2.0 * tol)
                    })
                {
                    return true;
                }
            }
        }
        false
    }

    /// The longest stretch, in feet, along which `run` runs beside the brook as its twin: within `TWIN_LO`-`TWIN_HI` of it, within
    /// `TWIN_DEG` of its bearing and running the same way (down it, as the run flows from the outfall); sampled every `TWIN_STEP`.
    ///
    /// Research:
    ///     twin run measure - research/questions/0067-do-two-ditches-run-side-by-side-across-the-fields-not-in-the-old-forms-the-map-draws.html: "within about 12 to 32 ft of it, running the same way, for more than 60 ft past where it leaves" - the stretch measured from the run's start, with no further reach set aside
    pub fn twin_run(&mut self, run: &[Pt]) -> f64 {
        if run.len() < 2 || self.len() < 2 {
            return 0.0;
        }
        let (mut best, mut cur) = (0.0_f64, 0.0_f64);
        for leg in run.windows(2) {
            let len = dist(leg[0], leg[1]);
            if len <= 0.0 {
                continue;
            }
            let d = ((leg[1].0 - leg[0].0) / len, (leg[1].1 - leg[0].1) / len);
            let mut t = 0.0;
            while t <= len {
                let p = (leg[0].0 + d.0 * t, leg[0].1 + d.1 * t);
                if self.beside(p, d) {
                    cur += TWIN_STEP;
                    best = best.max(cur);
                } else {
                    cur = 0.0;
                }
                t += TWIN_STEP;
            }
        }
        best
    }

    /// Research:
    ///     twin run measure - research/questions/0067-do-two-ditches-run-side-by-side-across-the-fields-not-in-the-old-forms-the-map-draws.html: "within about 12 to 32 ft of it, running the same way"
    ///
    /// Whether `p`, heading `d`, runs beside the brook: its nearest brook segment within the twins' band and its bearing within
    /// `TWIN_DEG`.
    fn beside(&mut self, p: Pt, d: Pt) -> bool {
        let u = p.0 * self.fall.0 + p.1 * self.fall.1;
        let mut best: Option<(f64, Pt)> = None;
        for i in self.span(u - TWIN_HI, u + TWIN_HI) {
            let (a, b) = self.seg(i);
            let e = seg_dist(p, a, b);
            if best.is_none_or(|(m, _)| e < m) {
                best = Some((e, (b.0 - a.0, b.1 - a.1)));
            }
        }
        let Some((e, v)) = best else { return false };
        let len = (v.0 * v.0 + v.1 * v.1).sqrt();
        if !(TWIN_LO..=TWIN_HI).contains(&e) || len <= 0.0 {
            return false;
        }
        // the brook's segment turned to run down the brook, the way its water flows, as the run's does from the outfall
        let down = if self.rising { 1.0 } else { -1.0 };
        down * (d.0 * v.0 + d.1 * v.1) / len >= TWIN_DEG.to_radians().cos()
    }
}

/// Whether segments `a0-a1` and `b0-b1` cross properly (each strictly either side of the other's line).
#[must_use]
pub fn proper_cross(a0: Pt, a1: Pt, b0: Pt, b1: Pt) -> bool {
    let side = |p: Pt, q: Pt, r: Pt| (q.0 - p.0) * (r.1 - p.1) - (q.1 - p.1) * (r.0 - p.0);
    let (d1, d2) = (side(b0, b1, a0), side(b0, b1, a1));
    let (d3, d4) = (side(a0, a1, b0), side(a0, a1, b1));
    d1 * d2 < 0.0 && d3 * d4 < 0.0
}
