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

use super::rules::{breaks_through, forbidden_segment_among};
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
    house_hit_among(p, width, &houses.iter().collect::<Vec<_>>(), tests)
}

/// `house_hit` asked of the houses given.
fn house_hit_among(p: &[Pt], width: f64, houses: &[&House], tests: &mut Counts) -> bool {
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
    over_a_fixture_among(p, width, &quads.iter().collect::<Vec<_>>(), tests)
}

/// `over_a_fixture` asked of the fixtures given.
fn over_a_fixture_among(
    p: &[Pt],
    width: f64,
    quads: &[&(Vec<Pt>, Box4)],
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
    crate::counts::note(
        "seg_test@through_a_building",
        (5 * run.len() * quads.len()) as u64,
    );
    quads.iter().any(|q| quad_hit(run, q))
}

/// Does the run stand inside the quad or cross one of its walls?
fn quad_hit(run: &[Pt], q: &[Pt]) -> bool {
    run.iter().any(|&p| in_poly(p, q))
        || run
            .windows(2)
            .any(|w| (0..4).any(|k| segments_cross(w[0], w[1], q[k], q[(k + 1) % 4])))
}

/// The grid's cell (feet).
///
/// Research:
///     the law's box grid - NONE: plumbing, a lookup grid's 64 ft, the derivations' Indexes (Python's `GroundIndex` cell)
const GRID_FT: f64 = 64.0;

/// The pad on a query's box (feet): a crossing found by the orientation tests lies within both boxes up to rounding.
const GRID_PAD_FT: f64 = 1e-6;

/// Boxes filed in every 64 ft cell they cover, built once: a segment asks only the boxes of the cells its own box overlaps, so a
/// box it can meet is always among them (the audit at T30's landing: the outlines and the buildings walked whole per run).
///
/// Research:
///     the law's box grid - NONE: plumbing, the water index's 64 ft cells
#[derive(Default)]
pub struct BoxGrid {
    cells: std::collections::HashMap<(i64, i64), Vec<usize>>,
}

#[expect(
    clippy::cast_possible_truncation,
    reason = "a map's cells number in the hundreds"
)]
fn grid_cell(v: f64) -> i64 {
    (v / GRID_FT).floor() as i64
}

impl BoxGrid {
    /// The grid of `boxes`, each filed under its index.
    #[must_use]
    pub fn new(boxes: impl IntoIterator<Item = Box4>) -> Self {
        let mut g = Self::default();
        for (i, b) in boxes.into_iter().enumerate() {
            for cx in grid_cell(b.0)..=grid_cell(b.2) {
                for cy in grid_cell(b.1)..=grid_cell(b.3) {
                    g.cells.entry((cx, cy)).or_default().push(i);
                }
            }
        }
        g
    }

    /// The boxes filed in the cells the box `b` overlaps, each once, in the order filed.
    #[must_use]
    pub fn near(&self, b: Box4) -> Vec<usize> {
        let mut out = Vec::new();
        for cx in grid_cell(b.0 - GRID_PAD_FT)..=grid_cell(b.2 + GRID_PAD_FT) {
            for cy in grid_cell(b.1 - GRID_PAD_FT)..=grid_cell(b.3 + GRID_PAD_FT) {
                if let Some(ids) = self.cells.get(&(cx, cy)) {
                    out.extend_from_slice(ids);
                }
            }
        }
        out.sort_unstable();
        out.dedup();
        out
    }
}

/// The box of the segment a-b.
fn seg_box(a: Pt, b: Pt) -> Box4 {
    (a.0.min(b.0), a.1.min(b.1), a.0.max(b.0), a.1.max(b.1))
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
    /// The open rings' edges and their grid, built on first ask.
    pub open_grid: std::cell::OnceCell<(Vec<(Pt, Pt)>, BoxGrid)>,
    /// The buildings' grid, built on first ask.
    pub building_grid: std::cell::OnceCell<BoxGrid>,
    /// The grids of the houses (each box its reach of half a diagonal), the yards, the fixtures and what the matrix forbids,
    /// built on first ask.
    pub fabric_grids: std::cell::OnceCell<[BoxGrid; 4]>,
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
        tests.add("candidate@fouled_segment", 1);
        let [houses, yards, fixtures, forbidding] = self.fabric_grids.get_or_init(|| {
            [
                BoxGrid::new(self.houses.iter().map(|h| {
                    let r = h.half_diag;
                    (h.at.0 - r, h.at.1 - r, h.at.0 + r, h.at.1 + r)
                })),
                BoxGrid::new(self.yards.iter().map(|y| y.1)),
                BoxGrid::new(self.fixtures.iter().map(|f| f.1)),
                BoxGrid::new(self.forbidding.iter().map(|f| f.1)),
            ]
        });
        let grown = |b: Box4, g: f64| (b.0 - g, b.1 - g, b.2 + g, b.3 + g);
        let theirs = |(_, _, own): &(Vec<Pt>, Box4, Option<Pt>)| {
            own.is_none_or(|o| owner.is_none_or(|w| dist(o, w) > 1.0))
        };
        let matrix =
            forbidden_segment_among(p, width, &self.forbidding, |b| forbidding.near(b), tests);
        let (fixture_gap, house_reach) = (width / 2.0 + GAPS.1, width / 2.0 + GAPS.0);
        p.windows(2).enumerate().find_map(|(k, w)| {
            let seg = [w[0], w[1]];
            let sb = seg_box(w[0], w[1]);
            let near_fixtures: Vec<&(Vec<Pt>, Box4)> = fixtures
                .near(grown(sb, fixture_gap))
                .into_iter()
                .map(|i| &self.fixtures[i])
                .collect();
            let near_houses: Vec<&House> = houses
                .near(grown(sb, house_reach))
                .into_iter()
                .map(|i| &self.houses[i])
                .collect();
            let near = yards.near(grown(sb, GAPS.2)).into_iter().any(|i| {
                let y = &self.yards[i];
                theirs(y) && crosses_fabric(&seg, &y.0, y.1, GAPS.2, tests)
            });
            (over_a_fixture_among(&seg, width, &near_fixtures, tests).is_some()
                || Some(k) == matrix
                || house_hit_among(&seg, width, &near_houses, tests)
                || near
                || !breaks_through(&seg, &self.solid).is_empty())
            .then_some(k)
        })
    }

    /// Does the run cross no field outline, dry plot or marsh? Each leg asks the grid only for the edges near it.
    #[must_use]
    pub fn open_ground(&self, run: &[Pt]) -> bool {
        let (edges, grid) = self.open_grid.get_or_init(|| {
            let edges: Vec<(Pt, Pt)> = self
                .open_rings
                .iter()
                .flat_map(|ring| (0..ring.len()).map(|k| (ring[k], ring[(k + 1) % ring.len()])))
                .collect();
            let grid = BoxGrid::new(edges.iter().map(|&(a, b)| seg_box(a, b)));
            (edges, grid)
        });
        let mut asked = 0u64;
        let crossed = run.windows(2).any(|w| {
            let near = grid.near(seg_box(w[0], w[1]));
            asked += near.len() as u64 + 1;
            near.iter()
                .any(|&i| segments_cross(w[0], w[1], edges[i].0, edges[i].1))
        });
        crate::counts::note("seg_test@open_ground", asked);
        !crossed
    }

    /// Does any leg of the run cross a building's wall, or stand inside one? Each leg asks the grid only for the quads near it.
    #[must_use]
    pub fn through_a_building(&self, run: &[Pt]) -> bool {
        if run.len() < 2 {
            return through_a_building(run, &self.buildings);
        }
        let grid = self
            .building_grid
            .get_or_init(|| BoxGrid::new(self.buildings.iter().map(|q| poly_box(q))));
        let mut asked = 0u64;
        let hit = run.windows(2).any(|w| {
            let near = grid.near(seg_box(w[0], w[1]));
            asked += 5 * near.len() as u64 + 1;
            near.iter().any(|&i| quad_hit(w, &self.buildings[i]))
        });
        crate::counts::note("seg_test@through_a_building", asked);
        hit
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
        if self.through_a_building(run) {
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
