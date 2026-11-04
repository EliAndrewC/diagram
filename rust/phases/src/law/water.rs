//! The lane law's water (feature 444 T30): a run crosses each brook at most once, only at a crossing place, square to the brook
//! and to a drawn channel, and only where a deck seats - grown along the way until its corners clear the whole course, skewed
//! toward square where growth alone cannot, landing dry, and admitted by what stands (`law_water.py` `off_ford_at`,
//! `oblique_at`, `off_square`; `city/bridges.py` `crossing_deck`, `seat_deck`, `_deck_corners_clear`, `_lands_dry`,
//! `undeckable_at`, `deck_admitted`; `settle/shapes.py` `_crossing_fault`).
//!
//! Research:
//!     crossings - research/questions/0035-villages-beside-their-stream-one-bank-or-both.drawing.html: `_crossing_fault`
//!     crossed at a ford - research/questions/0035-villages-beside-their-stream-one-bank-or-both.drawing.html
//!     how far off a crossing place - research/questions/0035-villages-beside-their-stream-one-bank-or-both.drawing.html: within `FORD_HALF`, half the crossing place's 60 ft
//!     square brook crossing - research/questions/0035-villages-beside-their-stream-one-bank-or-both.drawing.html
//!     square ditch crossing - research/questions/0087-road-bridges-over-rivers-and-canals-hashi.drawing.html: a carried deck crosses at its way's angle, solved for it; the code squares a channel crossing within `FORD_SQUARE_TOL_DEG`, 10 degrees
//!     each brook crossed at most once - research/questions/0035-villages-beside-their-stream-one-bank-or-both.drawing.html
//!     deck grown until its corners clear - research/questions/0087-road-bridges-over-rivers-and-canals-hashi.drawing.html: up to 14 steps of 12% of the span
//!     skewed toward square - research/questions/0087-road-bridges-over-rivers-and-canals-hashi.drawing.html: at most 7 deg, inside the 8 deg a deck may lie off its way
//!     its search steps and tolerances - GUESS: no source could speak to it, a value of ours (feature 417 T38 pass N12, 2026-10-25) - 6 (a skew step, bounded by the record "8 degrees"); 0.12 (growth step of the deck search (the record has no 12%))
//!     carried deck corners on dry ground - research/questions/0087-road-bridges-over-rivers-and-canals-hashi.drawing.html: each corner at least 6 ft back from the water
#![expect(
    clippy::many_single_char_names,
    reason = "the plane geometry's own names"
)]

use super::rules::{crossing_points, sat_overlap};
use super::Counts;
use crate::field::fan::Pt;
use crate::field::geom::{dist, seg_dist};
use crate::ways::squaring::SQUARE_TOL_DEG;
use crate::ways::track::{in_poly, poly_box, seg_intersect, segments_cross, Box4};

/// Half a crossing place's length: a crossing farther than this from every ford is off it (ft).
///
/// Research:
///     crossing place's length - CONVENTION: a 60 ft gap (30 ft either side of a crossing place), so a deck crossing near square lands on both banks; 0035 sets the places and their spacing, not their length
pub const FORD_HALF_FT: f64 = 30.0;

/// A carried deck's landing past each bank, and the floor a seated deck's corners keep off the water past its half-width (ft).
///
/// Research:
///     a carried deck lands dry - research/questions/0087-road-bridges-over-rivers-and-canals-hashi.drawing.html: about 10 ft onto dry ground past each bank
///     carried deck corners on dry ground - research/questions/0087-road-bridges-over-rivers-and-canals-hashi.drawing.html: each corner at least 6 ft back from the water
pub const LANDING: (f64, f64) = (10.0, 6.0);

/// The water a run is judged against.
#[derive(Default)]
pub struct Waters {
    /// The brooks' courses.
    pub brooks: Vec<Vec<Pt>>,
    /// The drawn channels' courses.
    pub channels: Vec<Vec<Pt>>,
    /// Every course a way may be carried over, with its width.
    pub crossed: Vec<(Vec<Pt>, f64)>,
    /// The brook's crossing places.
    pub fords: Vec<Pt>,
    /// The flooded paddy plots a deck may not land on.
    pub wet: Vec<Vec<Pt>>,
    /// What stands that a deck may not stand on, each with its box.
    pub deck_forbidding: Vec<(Vec<Pt>, Box4)>,
}

/// How many degrees the run a-b crosses the course u-v off square.
#[must_use]
pub fn off_square(a: Pt, b: Pt, u: Pt, v: Pt) -> f64 {
    let t = ((b.1 - a.1).atan2(b.0 - a.0) - (v.1 - u.1).atan2(v.0 - u.0))
        .to_degrees()
        .rem_euclid(180.0);
    (90.0 - t).abs()
}

/// A deck's four corners: centered at `p`, `w` along `deg`, `h` across.
#[must_use]
pub fn deck_quad(p: Pt, w: f64, h: f64, deg: f64) -> [Pt; 4] {
    let (s, c) = deg.to_radians().sin_cos();
    [
        (-w / 2.0, -h / 2.0),
        (w / 2.0, -h / 2.0),
        (w / 2.0, h / 2.0),
        (-w / 2.0, h / 2.0),
    ]
    .map(|(dx, dy)| (p.0 + dx * c - dy * s, p.1 + dx * s + dy * c))
}

/// Does every corner of the deck stand `need` clear of the whole crossed course?
#[must_use]
pub fn corners_clear(
    p: Pt,
    rot: f64,
    span: f64,
    rw: f64,
    course: &[Pt],
    need: f64,
    tests: &mut Counts,
) -> bool {
    tests.add("dist@corners_clear", 4 * course.len() as u64);
    deck_quad(p, span, rw, rot).iter().all(|&q| {
        course
            .windows(2)
            .map(|w| seg_dist(q, w[0], w[1]))
            .fold(f64::INFINITY, f64::min)
            >= need
    })
}

/// A deck that clears the water at this crossing: grown along the way, and failing that skewed toward square and grown again;
/// (rotation, span, seated), the original span unseated where nothing seats. The deck is its center, rotation, span and width.
#[must_use]
pub fn seat_deck(
    deck: (Pt, f64, f64, f64),
    course: &[Pt],
    need: f64,
    water: (Pt, Pt),
    tests: &mut Counts,
) -> (f64, f64, bool) {
    let (p, rot, span, rw) = deck;
    let grown = |r: f64, tests: &mut Counts| {
        (0..14u8)
            .map(|g| span * (1.0 + 0.12 * f64::from(g)))
            .find(|&wider| corners_clear(p, r, wider, rw, course, need, tests))
    };
    if let Some(wider) = grown(rot, tests) {
        return (rot, wider, true);
    }
    let (wa, wb) = water;
    let toward = ((wb.1 - wa.1).atan2(wb.0 - wa.0).to_degrees() + 90.0 - rot + 90.0)
        .rem_euclid(180.0)
        - 90.0;
    let sign = if toward == 0.0 { 1.0 } else { toward.signum() };
    [2.0, 4.0, 6.0, 7.0]
        .iter()
        .find_map(|&sk| {
            let r = rot + sign * sk;
            grown(r, tests).map(|w| (r, w, true))
        })
        .unwrap_or((rot, span, false))
}

/// Does no corner of the deck stand inside a flooded plot?
#[must_use]
pub fn lands_dry(p: Pt, rot: f64, span: f64, rw: f64, wet: &[Vec<Pt>]) -> bool {
    let corners = deck_quad(p, span, rw, rot);
    wet.iter().all(|ring| {
        let b = poly_box(ring);
        !corners
            .iter()
            .any(|&c| b.0 <= c.0 && c.0 <= b.2 && b.1 <= c.1 && c.1 <= b.3 && in_poly(c, ring))
    })
}

/// The deck laid where the way segment ra-rb (width `rw`) crosses the water segment wa-wb of the course (width `ww`): the
/// crossing point, its rotation, its span and whether it seats - the span solving the oblique crossing, the deck grown until its
/// corners clear, and landing dry.
#[must_use]
pub fn crossing_deck(
    way: (Pt, Pt, f64),
    water: (Pt, Pt, f64),
    course: &[Pt],
    wet: &[Vec<Pt>],
    tests: &mut Counts,
) -> (Pt, f64, f64, bool) {
    let ((ra, rb, rw), (wa, wb, ww)) = (way, water);
    let p = seg_intersect(ra, rb, wa, wb).unwrap_or(ra);
    let rot = (rb.1 - ra.1).atan2(rb.0 - ra.0).to_degrees();
    let one = |l: f64| if l == 0.0 { 1.0 } else { l };
    let (rl, wl) = (one(dist(ra, rb)), one(dist(wa, wb)));
    let cs = ((rb.0 - ra.0) * (wb.0 - wa.0) + (rb.1 - ra.1) * (wb.1 - wa.1)) / (rl * wl);
    let sn = (1.0 - cs * cs).max(0.0).sqrt().max(0.25);
    let span = (ww + rw * cs.abs()) / sn + 2.0 * LANDING.0;
    let need = ww / 2.0 + LANDING.1;
    let (r, span, seated) = seat_deck((p, rot, span, rw), course, need, (wa, wb), tests);
    (p, r, span, seated && lands_dry(p, r, span, rw, wet))
}

impl Waters {
    /// Does a deck at `p` stand clear of what stands that a deck may not stand on?
    fn deck_admitted(&self, p: Pt, rot: f64, span: f64, width: f64, tests: &mut Counts) -> bool {
        let r = |v: f64| (v * 10.0).round() / 10.0;
        let q = deck_quad((r(p.0), r(p.1)), r(span), r(width), r(rot));
        let qb = poly_box(&q);
        tests.add(
            "index_examined@deck_admitted",
            self.deck_forbidding.len() as u64,
        );
        !self.deck_forbidding.iter().any(|(e, eb)| {
            !(qb.2 < eb.0 || qb.0 > eb.2 || qb.3 < eb.1 || qb.1 > eb.3) && sat_overlap(&q, e)
        })
    }

    /// Is there a crossing of the run where no deck seats or what stands refuses one?
    #[must_use]
    pub fn undeckable(&self, run: &[Pt], width: f64, tests: &mut Counts) -> bool {
        run.windows(2).any(|w| {
            let (ra, rb) = (w[0], w[1]);
            self.crossed.iter().any(|(course, ww)| {
                course.windows(2).any(|c| {
                    let (wa, wb) = (c[0], c[1]);
                    tests.add("seg_test@undeckable", 1);
                    segments_cross(ra, rb, wa, wb) && {
                        let (p, rot, span, seated) =
                            crossing_deck((ra, rb, width), (wa, wb, *ww), course, &self.wet, tests);
                        !seated || !self.deck_admitted(p, rot, span, width, tests)
                    }
                })
            })
        })
    }

    /// Does the run cross a brook farther than half a crossing place from every ford?
    #[must_use]
    pub fn off_a_ford(&self, run: &[Pt], tests: &mut Counts) -> bool {
        self.brooks.iter().any(|b| {
            crossing_points(run, b, tests).iter().any(|&(_, x)| {
                self.fords
                    .iter()
                    .map(|&f| dist(x, f))
                    .fold(f64::INFINITY, f64::min)
                    > FORD_HALF_FT
            })
        })
    }

    /// Does the run cross a brook or a drawn channel more than the tolerance off square?
    #[must_use]
    pub fn oblique(&self, run: &[Pt]) -> bool {
        let edges: usize = self.brooks.iter().chain(&self.channels).map(Vec::len).sum();
        crate::counts::note(
            "seg_test@oblique",
            (run.len().saturating_sub(1) * edges) as u64,
        );
        let rb = poly_box(run);
        self.brooks.iter().chain(&self.channels).any(|course| {
            let cb = poly_box(course);
            !(rb.2 < cb.0 || cb.2 < rb.0 || rb.3 < cb.1 || cb.3 < rb.1)
                && run.windows(2).any(|w| {
                    course.windows(2).any(|c| {
                        segments_cross(w[0], w[1], c[0], c[1])
                            && off_square(w[0], w[1], c[0], c[1]) > SQUARE_TOL_DEG
                    })
                })
        })
    }

    /// The run's crossing fault: a brook crossed twice, a crossing off a ford, off square, or where no deck seats.
    #[must_use]
    pub fn crossing_fault(&self, run: &[Pt], width: f64, tests: &mut Counts) -> bool {
        self.brooks
            .iter()
            .any(|b| crossing_points(run, b, tests).len() >= 2)
            || self.off_a_ford(run, tests)
            || self.oblique(run)
            || self.undeckable(run, width, tests)
    }
}
