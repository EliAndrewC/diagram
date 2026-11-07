//! The free ground (feature 444 T30): the seating's window painted once on a raster of cells - every no-build ring filled, every
//! watercourse's keep-out strip painted, the ground behind the paddy's facing chords - so a seat on ground a cell refuses is refused
//! by one lookup, and a rectangle by nine. The raster is the union of the members: nothing is unioned as a shape.
//!
//! Research:
//!     the free ground - NONE: the seating's machinery; each member's rule is claimed where the stage gathers it

use super::Counts;
use crate::field::fan::Pt;

/// The raster's cell (feet): under half the narrowest gap a homestead leaves, so a gap of free ground holds two cells.
///
/// Research:
///     the free ground's cell - NONE: a raster's grain, under half the 18 ft narrowest gap a homestead leaves
pub const CELL: f64 = 8.0;

/// How far the taken ground is grown before the reach is flooded over it (feet): a lane's room, so a sliver of free ground no lane
/// can pass reaches nothing beyond it.
///
/// Research:
///     a lane's room - NONE: the seat region's flood (`region.py` `LaneGround`) reads the taken cells grown by one free-ground cell, about a corridor's half-width - 8
pub const LANE_GROW_FT: f64 = 8.0;

/// A window of the canvas painted on cells of `CELL` feet: a cell is taken where its center lies in a member.
#[derive(Clone)]
pub struct Ground {
    x0: f64,
    y0: f64,
    cell: f64,
    nx: usize,
    ny: usize,
    taken: Vec<bool>,
}

impl Ground {
    /// A clear window from `lo` to `hi`, snapped outward to whole cells.
    #[must_use]
    #[expect(
        clippy::cast_possible_truncation,
        clippy::cast_sign_loss,
        reason = "a window of a few hundred cells a side, its sizes positive"
    )]
    pub fn new(lo: Pt, hi: Pt, tests: &mut Counts) -> Self {
        let (x0, y0) = ((lo.0 / CELL).floor() * CELL, (lo.1 / CELL).floor() * CELL);
        let nx = (((hi.0 - x0) / CELL).ceil() as usize).max(1);
        let ny = (((hi.1 - y0) / CELL).ceil() as usize).max(1);
        tests.add("write@new", (nx * ny) as u64);
        Self {
            x0,
            y0,
            cell: CELL,
            nx,
            ny,
            taken: vec![false; nx * ny],
        }
    }

    /// A window from `x0, y0`, `nx` cells to a row of `cell` feet, its cells `taken` - row by row - taken, not snapped: the raster
    /// the door hands over at another raster's own cells; None where the flags are not one a cell.
    #[must_use]
    pub fn from_cells(origin: Pt, cell: f64, nx: usize, taken: Vec<bool>) -> Option<Self> {
        let ny = taken.len().checked_div(nx)?;
        (nx * ny == taken.len() && ny > 0).then_some(Self {
            x0: origin.0,
            y0: origin.1,
            cell,
            nx,
            ny,
            taken,
        })
    }

    /// The center of cell (i, j).
    #[expect(clippy::cast_precision_loss, reason = "cell indices of a few hundred")]
    fn center(&self, i: usize, j: usize) -> Pt {
        (
            self.x0 + (i as f64 + 0.5) * self.cell,
            self.y0 + (j as f64 + 0.5) * self.cell,
        )
    }

    /// The cell holding `p`, or None outside the window.
    #[expect(
        clippy::cast_possible_truncation,
        clippy::cast_sign_loss,
        reason = "a cell index, its sign tested first"
    )]
    fn cell_of(&self, p: Pt) -> Option<(usize, usize)> {
        let (fi, fj) = ((p.0 - self.x0) / self.cell, (p.1 - self.y0) / self.cell);
        (fi >= 0.0 && fj >= 0.0 && (fi as usize) < self.nx && (fj as usize) < self.ny)
            .then_some((fi as usize, fj as usize))
    }

    /// Whether `p` lies on taken ground; outside the window, None (the window's owner decides it).
    #[must_use]
    pub fn taken_at(&self, p: Pt) -> Option<bool> {
        self.cell_of(p).map(|(i, j)| self.taken[j * self.nx + i])
    }

    /// The rows of cells whose centers lie between `ya` and `yb`, clipped to the window.
    #[expect(
        clippy::cast_possible_truncation,
        clippy::cast_sign_loss,
        reason = "row indices clamped into the window"
    )]
    fn rows(&self, ya: f64, yb: f64) -> std::ops::Range<usize> {
        let lo = ((ya.min(yb) - self.y0) / self.cell - 0.5).ceil().max(0.0) as usize;
        let hi = (((ya.max(yb) - self.y0) / self.cell - 0.5).floor() + 1.0).max(0.0) as usize;
        lo.min(self.ny)..hi.min(self.ny)
    }

    /// Fill the cells whose centers lie inside `ring` (even-odd, by scanlines through the cell centers): each edge stepped
    /// through the rows it spans, the spans between its crossings filled.
    #[expect(
        clippy::cast_possible_truncation,
        clippy::cast_sign_loss,
        reason = "column indices clamped into the window"
    )]
    pub fn fill_ring(&mut self, ring: &[Pt], tests: &mut Counts) {
        let n = ring.len();
        if n < 3 {
            return;
        }
        let (lo, hi) = ring
            .iter()
            .fold((f64::MAX, f64::MIN), |(a, b), p| (a.min(p.1), b.max(p.1)));
        tests.add("pt_test@fill_ring", n as u64);
        for j in self.rows(lo, hi) {
            let y = self.center(0, j).1;
            let mut xs: Vec<f64> = Vec::new();
            for k in 0..n {
                let (a, b) = (ring[k], ring[(k + 1) % n]);
                if (a.1 > y) != (b.1 > y) {
                    xs.push(a.0 + (y - a.1) / (b.1 - a.1) * (b.0 - a.0));
                }
            }
            tests.add("write@fill_ring", xs.len() as u64);
            xs.sort_by(f64::total_cmp);
            for pair in xs.chunks_exact(2) {
                let a = ((pair[0] - self.x0) / self.cell - 0.5).ceil().max(0.0) as usize;
                let b = (((pair[1] - self.x0) / self.cell - 0.5).floor() + 1.0).max(0.0) as usize;
                for i in a.min(self.nx)..b.min(self.nx) {
                    self.taken[j * self.nx + i] = true;
                    tests.add("write@fill_ring", 1);
                }
            }
        }
    }

    /// Paint the cells whose centers lie within `r` of the segment from `a` to `b` (a watercourse's keep-out strip).
    #[expect(
        clippy::cast_possible_truncation,
        clippy::cast_sign_loss,
        reason = "column indices clamped into the window"
    )]
    pub fn paint_strip(&mut self, a: Pt, b: Pt, r: f64, tests: &mut Counts) {
        let lo = (a.0.min(b.0) - r, a.1.min(b.1) - r);
        let hi = (a.0.max(b.0) + r, a.1.max(b.1) + r);
        for j in self.rows(lo.1, hi.1) {
            let i0 = ((lo.0 - self.x0) / self.cell - 0.5).ceil().max(0.0) as usize;
            let i1 = (((hi.0 - self.x0) / self.cell - 0.5).floor() + 1.0).max(0.0) as usize;
            for i in i0.min(self.nx)..i1.min(self.nx) {
                tests.add("write@paint_strip", 1);
                if crate::field::geom::seg_dist(self.center(i, j), a, b) <= r {
                    self.taken[j * self.nx + i] = true;
                }
            }
        }
    }

    /// Whether a rectangle (its corners `lo`, `hi`) is refused: any of its nine points - the corners, the edges' midpoints and the
    /// center - on taken ground. A point outside the window is asked of `beyond`.
    pub fn rect_refused(
        &self,
        lo: Pt,
        hi: Pt,
        beyond: &dyn Fn(Pt) -> bool,
        tests: &mut Counts,
    ) -> bool {
        let (mx, my) = (f64::midpoint(lo.0, hi.0), f64::midpoint(lo.1, hi.1));
        [lo.0, mx, hi.0]
            .iter()
            .flat_map(|&x| [lo.1, my, hi.1].map(|y| (x, y)))
            .any(|p| {
                tests.add("pt_test@rect_refused", 1);
                self.taken_at(p).unwrap_or_else(|| beyond(p))
            })
    }

    /// The taken cells grown by `LANE_GROW_FT` on every side (a square of cells, by a row pass then a column pass, each a running
    /// count read at the window's two ends): ground a lane cannot pass at its width is not free to the reach.
    #[expect(
        clippy::cast_possible_truncation,
        clippy::cast_sign_loss,
        reason = "a few cells' reach"
    )]
    fn lane_blocked(&self, taken: &[bool], tests: &mut Counts) -> Vec<bool> {
        let r = (LANE_GROW_FT / self.cell).round().max(1.0) as usize;
        let (nx, ny) = (self.nx, self.ny);
        let mut rows = vec![false; nx * ny];
        let mut run = vec![0u32; nx.max(ny) + 1];
        for j in 0..ny {
            for i in 0..nx {
                run[i + 1] = run[i] + u32::from(taken[j * nx + i]);
            }
            for i in 0..nx {
                rows[j * nx + i] = run[(i + r + 1).min(nx)] > run[i.saturating_sub(r)];
            }
        }
        let mut out = vec![false; nx * ny];
        for i in 0..nx {
            for j in 0..ny {
                run[j + 1] = run[j] + u32::from(rows[j * nx + i]);
            }
            for j in 0..ny {
                out[j * nx + i] = run[(j + r + 1).min(ny)] > run[j.saturating_sub(r)];
            }
        }
        tests.add("write@lane_blocked", (4 * nx * ny) as u64);
        out
    }

    /// The reach over the seating's WINDOW alone (`boundary.seating_window`, a cost window, never an answer - feature 318): the
    /// ground cropped to the window grown by a lane's room on every side (so the lane-blocked ground at its edges is the canvas's),
    /// flooded from `seeds` and from every free cell on the window's inner edges - where a way can run on to the rest of the
    /// canvas - and a box reaching out of it touches the reach (`Reach::touches`). The whole canvas flooded after every household
    /// was most of the stage's counted work (the work-budget run of 2026-11-05: 792 million of the reach's cells at 40).
    #[must_use]
    #[expect(
        clippy::cast_possible_truncation,
        clippy::cast_sign_loss,
        clippy::cast_precision_loss,
        reason = "cell indices clamped into the canvas"
    )]
    pub fn reach_in(&self, window: (Pt, Pt), seeds: &[Pt], tests: &mut Counts) -> Reach {
        let r = (LANE_GROW_FT / self.cell).round().max(1.0);
        let pad = (r + 1.0) * self.cell;
        let clip = |v: f64, n: usize| (v.max(0.0) as usize).min(n);
        let i0 = clip(((window.0 .0 - pad - self.x0) / self.cell).floor(), self.nx);
        let j0 = clip(((window.0 .1 - pad - self.y0) / self.cell).floor(), self.ny);
        let i1 = clip(((window.1 .0 + pad - self.x0) / self.cell).ceil(), self.nx).max(i0 + 1);
        let j1 = clip(((window.1 .1 + pad - self.y0) / self.cell).ceil(), self.ny).max(j0 + 1);
        let (wx, wy) = (i1 - i0, j1 - j0);
        let mut taken = Vec::with_capacity(wx * wy);
        for j in j0..j1 {
            taken.extend_from_slice(&self.taken[j * self.nx + i0..j * self.nx + i1]);
        }
        tests.add("write@reach_in", (wx * wy) as u64);
        let crop = Self {
            x0: self.x0 + i0 as f64 * self.cell,
            y0: self.y0 + j0 as f64 * self.cell,
            cell: self.cell,
            nx: wx,
            ny: wy,
            taken,
        };
        // ...seeded at the inner edges too: a free cell on an edge the canvas runs on past leads on out of the window
        let mut all = seeds.to_vec();
        let edges = (i0 > 0, j0 > 0, i1 < self.nx, j1 < self.ny);
        for j in 0..wy {
            for i in 0..wx {
                let edge = (edges.0 && i == 0)
                    || (edges.1 && j == 0)
                    || (edges.2 && i == wx - 1)
                    || (edges.3 && j == wy - 1);
                if edge && !crop.taken[j * wx + i] {
                    all.push(crop.center(i, j));
                }
            }
        }
        let mut reach = crop.flood(&all, tests);
        reach.open = edges;
        reach
    }

    /// The free cells joined to any of `seeds` through free cells, 4-connected, the taken ground grown by a lane's room first
    /// (`lane_blocked`): every cell labeled in one pass reading its west and north neighbors (union-find over the labels), the seeds'
    /// labels kept - nothing changes the free ground while the houses are seated (no way stands, no house is painted: 0246), so the
    /// reach is labeled once.
    #[must_use]
    pub fn reach(&self, seeds: &[Pt], tests: &mut Counts) -> Reach {
        self.flood(seeds, tests)
    }

    /// The free cells joined to any of `seeds` through free cells, the taken ground grown by a lane's room first (`lane_blocked`).
    fn flood(&self, seeds: &[Pt], tests: &mut Counts) -> Reach {
        let n = self.nx * self.ny;
        let blocked = self.lane_blocked(&self.taken, tests);
        let mut parent: Vec<usize> = (0..n).collect();
        for j in 0..self.ny {
            for i in 0..self.nx {
                let k = j * self.nx + i;
                tests.add("index_query@reach", 3);
                if blocked[k] {
                    continue;
                }
                for nb in [(i > 0).then(|| k - 1), (j > 0).then(|| k - self.nx)]
                    .into_iter()
                    .flatten()
                {
                    if !blocked[nb] {
                        let (a, b) = (root(&mut parent, k), root(&mut parent, nb));
                        parent[a.max(b)] = a.min(b);
                    }
                }
            }
        }
        let mut keep: Vec<usize> = seeds
            .iter()
            .filter_map(|&p| self.cell_of(p))
            .map(|(i, j)| j * self.nx + i)
            .filter(|&k| !blocked[k])
            .map(|k| root(&mut parent, k))
            .collect();
        keep.sort_unstable();
        keep.dedup();
        let reached = (0..n)
            .map(|k| !blocked[k] && keep.binary_search(&root(&mut parent, k)).is_ok())
            .collect();
        tests.add("write@reach", n as u64);
        Reach {
            open: (false, false, false, false),
            x0: self.x0,
            y0: self.y0,
            cell: self.cell,
            nx: self.nx,
            ny: self.ny,
            reached,
        }
    }
}

/// The root of `k`'s label in the union-find, halving the path as it climbs.
fn root(parent: &mut [usize], mut k: usize) -> usize {
    while parent[k] != k {
        parent[k] = parent[parent[k]];
        k = parent[k];
    }
    k
}

/// The reach: which cells of the free ground a way from the way out's anchor can come to.
pub struct Reach {
    /// Which of its sides (west, north, east, south) the canvas runs on past - a box reaching past one touches the reach.
    open: (bool, bool, bool, bool),
    x0: f64,
    y0: f64,
    cell: f64,
    nx: usize,
    ny: usize,
    reached: Vec<bool>,
}

impl Reach {
    /// Whether a box (its corners `lo`, `hi`) touches a reached cell: the cells it covers, clipped to the window.
    #[must_use]
    #[expect(
        clippy::cast_possible_truncation,
        clippy::cast_sign_loss,
        clippy::cast_precision_loss,
        reason = "cell indices clamped into the window"
    )]
    pub fn touches(&self, lo: Pt, hi: Pt, tests: &mut Counts) -> bool {
        // ...a box reaching past a side of the window the canvas runs on past touches it: the window bounds a cost, never a seat
        let (x1, y1) = (
            self.x0 + self.nx as f64 * self.cell,
            self.y0 + self.ny as f64 * self.cell,
        );
        if (self.open.0 && lo.0 < self.x0)
            || (self.open.1 && lo.1 < self.y0)
            || (self.open.2 && hi.0 > x1)
            || (self.open.3 && hi.1 > y1)
        {
            return true;
        }
        let i0 = ((lo.0 - self.x0) / self.cell).floor().max(0.0) as usize;
        let j0 = ((lo.1 - self.y0) / self.cell).floor().max(0.0) as usize;
        let i1 = (((hi.0 - self.x0) / self.cell).floor().max(-1.0) + 1.0) as usize;
        let j1 = (((hi.1 - self.y0) / self.cell).floor().max(-1.0) + 1.0) as usize;
        (j0..j1.min(self.ny)).any(|j| {
            (i0..i1.min(self.nx)).any(|i| {
                tests.add("index_query@touches", 1);
                self.reached[j * self.nx + i]
            })
        })
    }
}
