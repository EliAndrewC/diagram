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

/// How far round a reserved wood seat the reach's ground is taken (feet), before the lane's room is grown about it.
///
/// Research:
///     reserved wood seats bar lane ground - GUESS research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.drawing.html: a household's reserved wood seats are no ground its way runs on; no page read shows a way through a household's grove - the seat region's disc, two of its 8 ft cells and an eighth (`Region.circle`'s growth) - 17
pub const WOOD_PAINT_FT: f64 = 17.0;

/// A window of the canvas painted on cells of `CELL` feet: a cell is taken where its center lies in a member.
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

    /// The columns of cells whose centers lie between `xa` and `xb`, clipped to the window.
    #[expect(
        clippy::cast_possible_truncation,
        clippy::cast_sign_loss,
        reason = "column indices clamped into the window"
    )]
    fn rows_x(&self, xa: f64, xb: f64) -> std::ops::Range<usize> {
        let lo = ((xa.min(xb) - self.x0) / self.cell - 0.5).ceil().max(0.0) as usize;
        let hi = (((xa.max(xb) - self.x0) / self.cell - 0.5).floor() + 1.0).max(0.0) as usize;
        lo.min(self.nx)..hi.min(self.nx)
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

    /// The taken cells grown by `LANE_GROW_FT` on every side (a square of cells, by a row pass then a column pass): ground a lane
    /// cannot pass at its width is not free to the reach.
    #[expect(
        clippy::cast_possible_truncation,
        clippy::cast_sign_loss,
        reason = "a few cells' reach"
    )]
    fn lane_blocked(&self, taken: &[bool], tests: &mut Counts) -> Vec<bool> {
        let r = (LANE_GROW_FT / self.cell).round().max(1.0) as usize;
        let (nx, ny) = (self.nx, self.ny);
        let mut rows = vec![false; nx * ny];
        for j in 0..ny {
            for i in 0..nx {
                rows[j * nx + i] =
                    (i.saturating_sub(r)..(i + r + 1).min(nx)).any(|u| taken[j * nx + u]);
            }
        }
        tests.add("write@lane_blocked", (2 * nx * ny * (2 * r + 1)) as u64);
        (0..nx * ny)
            .map(|k| {
                let (i, j) = (k % nx, k / nx);
                (j.saturating_sub(r)..(j + r + 1).min(ny)).any(|v| rows[v * nx + i])
            })
            .collect()
    }

    /// The free cells joined to any of `seeds` through free cells, 4-connected, the taken ground grown by a lane's room first
    /// (`lane_blocked`): every cell labeled in one pass reading its west and north neighbors (union-find over the labels), the seeds'
    /// labels kept - nothing changes the free ground while the houses are seated (no way stands, no house is painted: 0246), so the
    /// reach is labeled once.
    #[must_use]
    pub fn reach(&self, seeds: &[Pt], tests: &mut Counts) -> Reach {
        self.reach_painted(seeds, &[], tests)
    }

    /// The reach with `discs` painted onto the taken ground first, each `WOOD_PAINT_FT` round - the wood seats the households
    /// seated so far reserved, which no way runs through (`region.py` `SeatRegion.sync`).
    #[must_use]
    pub fn reach_painted(&self, seeds: &[Pt], discs: &[Pt], tests: &mut Counts) -> Reach {
        let n = self.nx * self.ny;
        let mut taken = self.taken.clone();
        let paint = WOOD_PAINT_FT;
        for &(x, y) in discs {
            for j in self.rows(y - paint, y + paint) {
                for i in self.rows_x(x - paint, x + paint) {
                    let c = self.center(i, j);
                    tests.add("write@reach_painted", 1);
                    if (c.0 - x).hypot(c.1 - y) <= paint {
                        taken[j * self.nx + i] = true;
                    }
                }
            }
        }
        let blocked = self.lane_blocked(&taken, tests);
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
            seeds: seeds.to_vec(),
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
    /// Where it was flooded from.
    pub seeds: Vec<Pt>,
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
        reason = "cell indices clamped into the window"
    )]
    pub fn touches(&self, lo: Pt, hi: Pt, tests: &mut Counts) -> bool {
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
