//! The field's water index (feature 444 T16 D5): cells of 64 ft, each segment filed in every cell it crosses, a box asked of the
//! cells it overlaps. Written from the derivation's Indexes.
//!
//! Research:
//!     the water index - CONVENTION: cells of 64 ft, the derivations' Indexes; each segment filed in every cell it crosses

use std::collections::HashMap;

use super::fan::Pt;

/// The index's cell (feet).
///
/// Research:
///     the index's cell - CONVENTION: 64 ft, the derivations' Indexes
pub const CELL_FT: f64 = 64.0;

/// The segments filed, and the cells each lies in.
#[derive(Debug, Default)]
pub struct Index {
    pub segs: Vec<(Pt, Pt)>,
    cells: HashMap<(i64, i64), Vec<usize>>,
    /// The cells examined and written, for the counters (D6).
    pub touched: u64,
}

#[expect(
    clippy::cast_possible_truncation,
    reason = "a map's cells number in the hundreds"
)]
fn cell_of(v: f64) -> i64 {
    (v / CELL_FT).floor() as i64
}

impl Index {
    /// File a segment in every cell it crosses (Amanatides-Woo traversal); returns its id.
    pub fn file(&mut self, a: Pt, b: Pt) -> usize {
        let id = self.segs.len();
        self.segs.push((a, b));
        let (mut cx, mut cy) = (cell_of(a.0), cell_of(a.1));
        let (ex, ey) = (cell_of(b.0), cell_of(b.1));
        let (dx, dy) = (b.0 - a.0, b.1 - a.1);
        let step = |d: f64| i64::from(d > 0.0) - i64::from(d < 0.0);
        let (sx, sy) = (step(dx), step(dy));
        let next = |c: i64, s: i64| {
            #[expect(clippy::cast_precision_loss, reason = "a small cell index")]
            let edge = (c + i64::from(s > 0)) as f64 * CELL_FT;
            edge
        };
        let mut tx = if dx == 0.0 {
            f64::INFINITY
        } else {
            (next(cx, sx) - a.0) / dx
        };
        let mut ty = if dy == 0.0 {
            f64::INFINITY
        } else {
            (next(cy, sy) - a.1) / dy
        };
        let (step_x, step_y) = (CELL_FT / dx.abs(), CELL_FT / dy.abs());
        loop {
            self.cells.entry((cx, cy)).or_default().push(id);
            self.touched += 1;
            if (cx, cy) == (ex, ey) || (tx > 1.0 && ty > 1.0) {
                break;
            }
            if tx < ty {
                cx += sx;
                tx += step_x;
            } else {
                cy += sy;
                ty += step_y;
            }
        }
        id
    }

    /// The ids of the segments filed in the cells a box overlaps (each once).
    pub fn near(&mut self, lo: Pt, hi: Pt) -> Vec<usize> {
        let mut out = Vec::new();
        for cx in cell_of(lo.0)..=cell_of(hi.0) {
            for cy in cell_of(lo.1)..=cell_of(hi.1) {
                self.touched += 1;
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

#[cfg(test)]
mod tests {
    use super::{Index, CELL_FT};

    #[test]
    fn a_segment_is_filed_in_every_cell_it_crosses() {
        let mut ix = Index::default();
        let id = ix.file((10.0, 10.0), (10.0 + 3.0 * CELL_FT, 10.0));
        assert_eq!(ix.touched, 4, "four cells along a row");
        let diag = ix.file((1.0, 1.0), (130.0, 120.0));
        assert!(ix.near((100.0, 100.0), (101.0, 101.0)).contains(&diag));
        assert!(ix.near((5.0, 5.0), (6.0, 6.0)).contains(&id));
        assert!(ix.near((1000.0, 1000.0), (1001.0, 1001.0)).is_empty());
        let back = ix.file((200.0, 300.0), (-50.0, -10.0));
        assert!(ix.near((-1.0, -9.0), (199.0, 299.0)).contains(&back));
        let dot = ix.file((5.0, 5.0), (5.0, 5.0));
        assert!(ix.near((0.0, 0.0), (1.0, 1.0)).contains(&dot));
    }
}
