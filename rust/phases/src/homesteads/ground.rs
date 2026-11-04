//! The free ground (feature 444 T30): the seating's window painted once on a raster of cells - every no-build ring filled, every
//! watercourse's keep-out strip painted, the ground behind the paddy's facing chords - so a seat on ground a cell refuses is refused
//! by one lookup, and a rectangle by nine. The raster is the union of the members: nothing is unioned as a shape.
//!
//! Research:
//!     the free ground - NONE: the seating's machinery; each member's rule is claimed where the stage gathers it

use crate::field::fan::Pt;

/// The raster's cell (feet): under half the narrowest gap a homestead leaves, so a gap of free ground holds two cells.
///
/// Research:
///     the free ground's cell - NONE: a raster's grain, under half the 18 ft narrowest gap a homestead leaves
pub const CELL: f64 = 8.0;

/// A window of the canvas painted on cells of `CELL` feet: a cell is taken where its center lies in a member.
pub struct Ground {
    x0: f64,
    y0: f64,
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
    pub fn new(lo: Pt, hi: Pt, tests: &mut u64) -> Self {
        let (x0, y0) = ((lo.0 / CELL).floor() * CELL, (lo.1 / CELL).floor() * CELL);
        let nx = (((hi.0 - x0) / CELL).ceil() as usize).max(1);
        let ny = (((hi.1 - y0) / CELL).ceil() as usize).max(1);
        *tests += (nx * ny) as u64;
        Self {
            x0,
            y0,
            nx,
            ny,
            taken: vec![false; nx * ny],
        }
    }

    /// The center of cell (i, j).
    #[expect(clippy::cast_precision_loss, reason = "cell indices of a few hundred")]
    fn center(&self, i: usize, j: usize) -> Pt {
        (
            self.x0 + (i as f64 + 0.5) * CELL,
            self.y0 + (j as f64 + 0.5) * CELL,
        )
    }

    /// The cell holding `p`, or None outside the window.
    #[expect(
        clippy::cast_possible_truncation,
        clippy::cast_sign_loss,
        reason = "a cell index, its sign tested first"
    )]
    fn cell_of(&self, p: Pt) -> Option<(usize, usize)> {
        let (fi, fj) = ((p.0 - self.x0) / CELL, (p.1 - self.y0) / CELL);
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
        let lo = ((ya.min(yb) - self.y0) / CELL - 0.5).ceil().max(0.0) as usize;
        let hi = (((ya.max(yb) - self.y0) / CELL - 0.5).floor() + 1.0).max(0.0) as usize;
        lo.min(self.ny)..hi.min(self.ny)
    }

    /// Fill the cells whose centers lie inside `ring` (even-odd, by scanlines through the cell centers): each edge stepped
    /// through the rows it spans, the spans between its crossings filled.
    #[expect(
        clippy::cast_possible_truncation,
        clippy::cast_sign_loss,
        reason = "column indices clamped into the window"
    )]
    pub fn fill_ring(&mut self, ring: &[Pt], tests: &mut u64) {
        let n = ring.len();
        if n < 3 {
            return;
        }
        let (lo, hi) = ring
            .iter()
            .fold((f64::MAX, f64::MIN), |(a, b), p| (a.min(p.1), b.max(p.1)));
        *tests += n as u64;
        for j in self.rows(lo, hi) {
            let y = self.center(0, j).1;
            let mut xs: Vec<f64> = Vec::new();
            for k in 0..n {
                let (a, b) = (ring[k], ring[(k + 1) % n]);
                if (a.1 > y) != (b.1 > y) {
                    xs.push(a.0 + (y - a.1) / (b.1 - a.1) * (b.0 - a.0));
                }
            }
            *tests += xs.len() as u64;
            xs.sort_by(f64::total_cmp);
            for pair in xs.chunks_exact(2) {
                let a = ((pair[0] - self.x0) / CELL - 0.5).ceil().max(0.0) as usize;
                let b = (((pair[1] - self.x0) / CELL - 0.5).floor() + 1.0).max(0.0) as usize;
                for i in a.min(self.nx)..b.min(self.nx) {
                    self.taken[j * self.nx + i] = true;
                    *tests += 1;
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
    pub fn paint_strip(&mut self, a: Pt, b: Pt, r: f64, tests: &mut u64) {
        let lo = (a.0.min(b.0) - r, a.1.min(b.1) - r);
        let hi = (a.0.max(b.0) + r, a.1.max(b.1) + r);
        for j in self.rows(lo.1, hi.1) {
            let i0 = ((lo.0 - self.x0) / CELL - 0.5).ceil().max(0.0) as usize;
            let i1 = (((hi.0 - self.x0) / CELL - 0.5).floor() + 1.0).max(0.0) as usize;
            for i in i0.min(self.nx)..i1.min(self.nx) {
                *tests += 1;
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
        tests: &mut u64,
    ) -> bool {
        let (mx, my) = (f64::midpoint(lo.0, hi.0), f64::midpoint(lo.1, hi.1));
        [lo.0, mx, hi.0]
            .iter()
            .flat_map(|&x| [lo.1, my, hi.1].map(|y| (x, y)))
            .any(|p| {
                *tests += 1;
                self.taken_at(p).unwrap_or_else(|| beyond(p))
            })
    }
}
