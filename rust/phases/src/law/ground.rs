//! The ground half of the lane law (feature 444 T30): what a run keeps whatever lanes are drawn beside it - no kink or hook the
//! ground does not force, no foul of a farmhouse, another household's yard or garden, a building's box or a fixture, nothing the
//! overlap matrix forbids under it, no field, dry plot or marsh crossed, no building's wall crossed, and no crossing fault
//! (`settle/lawful.py` `Lawful.ground_fault`, `on_lawful_ground`, `blocked`; `forced.py` `forced_turn`; `law/shape.py`
//! `hooked`, `hook_faults`, `kink_faults`; `settle/shapes.py` `fouled_segment`, `theirs`; `fabric.py` `house_hit`;
//! `law/ends.py` `over_a_fixture`; `corridors.py` `through_a_building`, `GroundIndex.open_ground`).
//!
//! Research:
//!     bends like a path - research/questions/0081-village-lanes.drawing.html: no kink or hook
//!     a forced turn is lawful - research/questions/0081-village-lanes.drawing.html: "A turn the ground forces is drawn as walked" - the chord the vertex before the first turn to the vertex after the last
//!     crossings - research/questions/0035-villages-beside-their-stream-one-bank-or-both.drawing.html: `_crossing_fault`
//!     nothing built on a lane - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: no foul of house, yard, building, fixture
//!     off crop and marsh - research/questions/0081-village-lanes.drawing.html: no field, dry plot or marsh underfoot
//!     the fence gap - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: 7 ft from a lane's middle to another household's garden fence, a map drawing convention
//!     a way beside its own garden - DEVIATION research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: "A lane's middle keeps at least 7 ft clear of a garden fence" is a convention for the room between neighbors; a household's way may run beside its own fence
#![expect(
    clippy::many_single_char_names,
    reason = "the plane geometry's own names"
)]

use super::rules::{breaks_through, forbidden_segment};
use super::water::Waters;
use super::Counts;
use crate::field::fan::Pt;
use crate::field::geom::{dist, seg_dist};
use crate::ways::route::turn_deg;
use crate::ways::squaring::{kink_spans, Kink};
use crate::ways::track::{crosses_fabric, in_poly, poly_box, segments_cross, Box4};

/// A hook: a lane's last leg this short turning this much (ft, degrees).
///
/// Research:
///     a lane's end loses its hook - research/questions/0081-village-lanes.drawing.html: 12 ft, 90 degrees
pub const HOOK: (f64, f64) = (12.0, 90.0);

/// A tread's setback off a farmhouse wall, a fixture's pad past the half-tread, and the fence gap off another household's yard or
/// garden (ft).
///
/// Research:
///     tread clear of a wall - research/questions/0081-village-lanes.drawing.html: 3 ft, a Japanese village house's setback from a road
///     fixture pad - CONVENTION: 0.5 ft past the half-tread
///     the fence gap - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: 7 ft from a lane's middle to another household's garden fence
pub const GAPS: (f64, f64, f64) = (3.0, 0.5, 7.0);

/// A turned rectangle's corners: centered at (x, y), `w` by `h`, turned `deg`.
#[must_use]
pub fn rot_rect(x: f64, y: f64, w: f64, h: f64, deg: f64) -> Vec<Pt> {
    let (s, c) = deg.to_radians().sin_cos();
    [
        (-w / 2.0, -h / 2.0),
        (w / 2.0, -h / 2.0),
        (w / 2.0, h / 2.0),
        (-w / 2.0, h / 2.0),
    ]
    .iter()
    .map(|&(dx, dy)| (x + dx * c - dy * s, y + dx * s + dy * c))
    .collect()
}

/// Which ends of a run are hooked: -1 its last, 0 its first.
#[must_use]
pub fn hooked(p: &[Pt]) -> Vec<i8> {
    if p.len() < 3 {
        return Vec::new();
    }
    let n = p.len();
    let rev: Vec<Pt> = p.iter().rev().copied().collect();
    [(-1, p), (0, rev.as_slice())]
        .into_iter()
        .filter(|(_, q)| {
            dist(q[n - 2], q[n - 1]) <= HOOK.0 && turn_deg(q[n - 3], q[n - 2], q[n - 1]) >= HOOK.1
        })
        .map(|(e, _)| e)
        .collect()
}

/// A house as the fouls read it: its turned quad, its center and the reach within which a tread may meet it.
pub struct House {
    /// Its quad.
    pub quad: Vec<Pt>,
    /// Its center.
    pub at: Pt,
    /// Half its diagonal.
    pub half_diag: f64,
}

/// Does a run drawn `width` wide put ink on a house: a point inside it, a wall crossed, or a wall within the half-tread and the
/// setback?
#[must_use]
pub fn house_hit(p: &[Pt], width: f64, houses: &[House], tests: &mut Counts) -> bool {
    let half = width / 2.0 + GAPS.0;
    let rb = poly_box(p);
    houses.iter().any(|h| {
        let reach = h.half_diag + half;
        if h.at.0 + reach < rb.0
            || h.at.0 - reach > rb.2
            || h.at.1 + reach < rb.1
            || h.at.1 - reach > rb.3
        {
            return false;
        }
        tests.add("seg_test@house_hit", 4 * p.len() as u64);
        p.windows(2).any(|w| {
            let (a, b) = (w[0], w[1]);
            in_poly(a, &h.quad)
                || (0..4).any(|k| {
                    let (u, v) = (h.quad[k], h.quad[(k + 1) % 4]);
                    segments_cross(a, b, u, v)
                        || seg_dist(u, a, b)
                            .min(seg_dist(v, a, b))
                            .min(seg_dist(a, u, v))
                            .min(seg_dist(b, u, v))
                            < half
                })
        })
    })
}

/// The first segment whose tread, `width` wide, meets a fixture: crosses it, stands in it, or passes within the half-tread and
/// the pad of it.
#[must_use]
pub fn over_a_fixture(
    p: &[Pt],
    width: f64,
    quads: &[(Vec<Pt>, Box4)],
    tests: &mut Counts,
) -> Option<usize> {
    let gap = width / 2.0 + GAPS.1;
    p.windows(2).position(|w| {
        let (a, b) = (w[0], w[1]);
        quads.iter().any(|(q, qb)| {
            !(qb.0 - gap > a.0.max(b.0)
                || qb.2 + gap < a.0.min(b.0)
                || qb.1 - gap > a.1.max(b.1)
                || qb.3 + gap < a.1.min(b.1))
                && (in_poly(a, q) || in_poly(b, q) || crosses_fabric(&[a, b], q, *qb, gap, tests))
        })
    })
}

/// Does any leg of the run cross a building's wall, or stand inside one?
#[must_use]
pub fn through_a_building(run: &[Pt], quads: &[Vec<Pt>]) -> bool {
    quads.iter().any(|q| {
        run.iter().any(|&p| in_poly(p, q))
            || run
                .windows(2)
                .any(|w| (0..4).any(|k| segments_cross(w[0], w[1], q[k], q[(k + 1) % 4])))
    })
}

/// The map's ground a run is judged on: its houses, the yards and gardens with their households, the buildings' boxes and quads,
/// the fixtures, the outlines a run may not cross, what the matrix forbids under a way, and the water.
#[derive(Default)]
pub struct LawGround {
    /// The houses.
    pub houses: Vec<House>,
    /// The yards and gardens, each with its household's center.
    pub yards: Vec<(Vec<Pt>, Box4, Option<Pt>)>,
    /// The buildings' boxes a long leg may not run through.
    pub solid: Vec<Box4>,
    /// The fixtures' quads and trunks.
    pub fixtures: Vec<(Vec<Pt>, Box4)>,
    /// The buildings' quads.
    pub buildings: Vec<Vec<Pt>>,
    /// The field outlines, dry plots and marshes a run may not cross.
    pub open_rings: Vec<Vec<Pt>>,
    /// What the overlap matrix forbids under a way.
    pub forbidding: Vec<(Vec<Pt>, Box4)>,
    /// The water.
    pub waters: Waters,
}

impl LawGround {
    /// Is the straight way a-b at `width` not lawful ground? A chord has no turn of its own, so it never asks itself again.
    pub fn blocked(&self, a: Pt, b: Pt, width: f64, tests: &mut Counts) -> bool {
        dist(a, b) > 1e-6 && self.ground_fault(&[a, b], width, None, tests).is_some()
    }

    /// Is the turn between `before` and `after` forced: the chord between them not lawful ground?
    fn forced(&self, before: Pt, after: Pt, width: f64, tests: &mut Counts) -> bool {
        self.blocked(before, after, width, tests)
    }

    /// The run's kinks and hooks the ground does not force.
    pub fn bends(&self, p: &[Pt], width: f64, tests: &mut Counts) -> bool {
        let n = p.len();
        let hook = hooked(p).into_iter().any(|e| {
            let (before, after) = if e == -1 {
                (p[n - 3], p[n - 1])
            } else {
                (p[2], p[0])
            };
            !self.forced(before, after, width, tests)
        });
        hook || kink_spans(p).into_iter().any(|k| {
            let (first, last) = match k {
                Kink::DoublesBack(v) => (v, v),
                Kink::Kinks(a, b) => (a, b),
            };
            !(first >= 1 && last + 1 < n && self.forced(p[first - 1], p[last + 1], width, tests))
        })
    }

    /// The first segment that fouls the fabric: ink on a farmhouse, within the fence gap of another household's yard or garden,
    /// a long leg through a building's box, a tread over a fixture, or what the matrix forbids under a way.
    pub fn fouled(
        &self,
        p: &[Pt],
        width: f64,
        owner: Option<Pt>,
        tests: &mut Counts,
    ) -> Option<usize> {
        let theirs: Vec<(Vec<Pt>, Box4)> = self
            .yards
            .iter()
            .filter(|(_, _, own)| own.is_none_or(|o| owner.is_none_or(|w| dist(o, w) > 1.0)))
            .map(|(r, b, _)| (r.clone(), *b))
            .collect();
        let over = over_a_fixture(p, width, &self.fixtures, tests);
        let matrix = forbidden_segment(p, width, &self.forbidding, tests);
        p.windows(2).enumerate().find_map(|(k, w)| {
            let seg = [w[0], w[1]];
            let near = theirs
                .iter()
                .any(|(r, b)| crosses_fabric(&seg, r, *b, GAPS.2, tests));
            (Some(k) == over
                || Some(k) == matrix
                || house_hit(&seg, width, &self.houses, tests)
                || near
                || !breaks_through(&seg, &self.solid).is_empty())
            .then_some(k)
        })
    }

    /// Does the run cross no field outline, dry plot or marsh?
    #[must_use]
    pub fn open_ground(&self, run: &[Pt]) -> bool {
        !self.open_rings.iter().any(|ring| {
            let n = ring.len();
            run.windows(2)
                .any(|w| (0..n).any(|k| segments_cross(w[0], w[1], ring[k], ring[(k + 1) % n])))
        })
    }

    /// The first rule of the ground half the run breaks, by name, or None.
    pub fn ground_fault(
        &self,
        run: &[Pt],
        width: f64,
        owner: Option<Pt>,
        tests: &mut Counts,
    ) -> Option<&'static str> {
        tests.add("candidate@ground_fault", 1);
        if run.len() < 2 {
            return Some("too short");
        }
        if self.bends(run, width, tests) {
            return Some("bends");
        }
        if self.fouled(run, width, owner, tests).is_some() {
            return Some("fabric");
        }
        if !self.open_ground(run) {
            return Some("off open ground");
        }
        if through_a_building(run, &self.buildings) {
            return Some("through a building");
        }
        self.waters
            .crossing_fault(run, width, tests)
            .then_some("crossing")
    }

    /// Is the run on lawful ground?
    pub fn on_lawful_ground(
        &self,
        run: &[Pt],
        width: f64,
        owner: Option<Pt>,
        tests: &mut Counts,
    ) -> bool {
        self.ground_fault(run, width, owner, tests).is_none()
    }
}
