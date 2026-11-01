//! The field's water index (feature 444 T16 D5): cells of 64 ft, each segment filed in every cell it crosses, a box asked of the
//! cells it overlaps. Written from the derivation's Indexes.
//!
//! Research:
//!     the water index - NONE: plumbing, cells of 64 ft (the derivations' Indexes), each segment filed in every cell it crosses

use std::collections::HashMap;

use super::fan::Pt;

/// The index's cell (feet).
///
/// Research:
///     the index's cell - NONE: plumbing, a lookup grid's 64 ft, the derivations' Indexes
pub const CELL_FT: f64 = 64.0;

/// The segments filed, and the cells each lies in.
#[derive(Debug, Default, Clone)]
pub struct Index {
    pub segs: Vec<(Pt, Pt)>,
    /// Each segment's width (feet): zero unless filed with `file_w`.
    pub widths: Vec<f64>,
    cells: HashMap<(i64, i64), Vec<usize>>,
    /// The widest segment filed (feet), kept as each is filed so a query's reach is never a scan of every width.
    pub widest: f64,
    /// The cells examined and written, for the counters (D6).
    pub touched: u64,
    /// The segments a query handed back to be tested, for the counters (D6).
    pub examined: u64,
    /// The geometric tests asked of what the queries handed back - the hem's water, lap and row-direction tests - for the
    /// counters (S5: the work counted where it happens, the work-budget audit at T16's landing).
    pub tests: u64,
}

/// Boxes filed in every cell they cover, a box asked of the cells it overlaps: the hem's plots laid so far, asked of each
/// candidate (a candidate lapping onto a plot has a point in that plot's box, so the plot is filed in a cell the candidate asks).
///
/// Research:
///     the box grid - NONE: plumbing, the water index's 64 ft cells
#[derive(Debug, Default)]
pub struct Boxes {
    cells: HashMap<(i64, i64), Vec<usize>>,
    n: usize,
    /// The cells examined and written, and the boxes handed back, for the counters (D6).
    pub touched: u64,
    pub examined: u64,
}

impl Boxes {
    /// File the box `lo`..`hi`; returns its id (the order filed).
    pub fn file(&mut self, lo: Pt, hi: Pt) -> usize {
        let id = self.n;
        self.n += 1;
        for cx in cell_of(lo.0)..=cell_of(hi.0) {
            for cy in cell_of(lo.1)..=cell_of(hi.1) {
                self.cells.entry((cx, cy)).or_default().push(id);
                self.touched += 1;
            }
        }
        id
    }

    /// The ids of the boxes filed in the cells the box `lo`..`hi` overlaps (each once).
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
        // each id the cells handed back is sorted and deduplicated: counted as it is handed back, not after (the audit, T16)
        self.examined += out.len() as u64;
        out.sort_unstable();
        out.dedup();
        out
    }
}

/// A ring's edges binned by band of y, `CELL_FT` deep, each edge in every band its y-range covers: a point's inside test casts
/// its ray only across the edges of its own band, the only ones it can cross (the hem's tests against the field's outline, which
/// walked the whole ring a point - the audit, T16). The same crossing rule as `geom::inside`, edge for edge, so the same answer.
///
/// Research:
///     the bands - NONE: plumbing, the water index's 64 ft cells
#[derive(Debug, Default)]
pub struct Bands {
    edges: Vec<(Pt, Pt)>,
    by_band: HashMap<i64, Vec<usize>>,
    /// The edges a test crossed its ray against, for the counters (D6).
    pub tested: u64,
}

impl Bands {
    /// The bands of `ring`'s edges (each corner to the one before it, as `geom::inside` walks them).
    #[must_use]
    pub fn new(ring: &[Pt]) -> Self {
        let mut out = Self::default();
        for i in 0..ring.len() {
            let (a, b) = (ring[i], ring[(i + ring.len() - 1) % ring.len()]);
            let id = out.edges.len();
            out.edges.push((a, b));
            for band in cell_of(a.1.min(b.1))..=cell_of(a.1.max(b.1)) {
                out.by_band.entry(band).or_default().push(id);
                out.tested += 1; // each edge filed in each band it spans, counted with the bands' tests (the audit, T16)
            }
        }
        out
    }

    /// Whether `p` lies inside the ring.
    pub fn inside(&mut self, p: Pt) -> bool {
        let mut odd = false;
        for &i in self
            .by_band
            .get(&cell_of(p.1))
            .map_or(&[][..], Vec::as_slice)
        {
            let (a, b) = self.edges[i];
            self.tested += 1;
            if (a.1 > p.1) != (b.1 > p.1) && p.0 < (b.0 - a.0) * (p.1 - a.1) / (b.1 - a.1) + a.0 {
                odd = !odd;
            }
        }
        odd
    }
}

/// A ring's bounding box.
#[must_use]
pub fn bbox(ring: &[Pt]) -> (Pt, Pt) {
    ring.iter().fold(
        (
            (f64::INFINITY, f64::INFINITY),
            (f64::NEG_INFINITY, f64::NEG_INFINITY),
        ),
        |(l, h), p| ((l.0.min(p.0), l.1.min(p.1)), (h.0.max(p.0), h.1.max(p.1))),
    )
}

#[expect(
    clippy::cast_possible_truncation,
    reason = "a map's cells number in the hundreds"
)]
fn cell_of(v: f64) -> i64 {
    (v / CELL_FT).floor() as i64
}

impl Index {
    /// File a segment in every cell it crosses (Amanatides-Woo traversal); returns its id - for the tests, the stage filing each
    /// segment with its width (`file_w`).
    #[cfg(test)]
    pub fn file(&mut self, a: Pt, b: Pt) -> usize {
        self.file_w(a, b, 0.0)
    }

    /// File a segment `w` feet wide.
    pub fn file_w(&mut self, a: Pt, b: Pt, w: f64) -> usize {
        let id = self.segs.len();
        self.segs.push((a, b));
        self.widths.push(w);
        self.widest = self.widest.max(w);
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
        // each id the cells handed back is sorted and deduplicated: counted as it is handed back, not after (the audit, T16)
        self.examined += out.len() as u64;
        out.sort_unstable();
        out.dedup();
        out
    }
}

#[cfg(test)]
mod tests {
    use super::{bbox, Bands, Boxes, Index, CELL_FT};
    use crate::field::geom::inside;

    #[test]
    fn the_bands_answer_as_the_ring_walk_does() {
        let ring = [
            (0.0, 0.0),
            (300.0, 10.0),
            (280.0, 400.0),
            (150.0, 120.0),
            (-20.0, 380.0),
        ];
        let mut bands = Bands::new(&ring);
        for x in (-40..340).step_by(13) {
            for y in (-30..420).step_by(11) {
                let p = (f64::from(x) + 0.5, f64::from(y) + 0.25);
                assert_eq!(bands.inside(p), inside(p, &ring), "{p:?}");
            }
        }
        assert!(bands.tested > 0);
        assert!(!bands.inside((0.0, 5000.0)), "a band no edge reaches");
    }

    #[test]
    fn a_box_is_found_from_every_cell_it_covers() {
        let mut bx = Boxes::default();
        let a = bx.file((10.0, 10.0), (140.0, 20.0));
        let b = bx.file((500.0, 500.0), (510.0, 510.0));
        assert_eq!(bx.near((130.0, 0.0), (131.0, 1.0)), vec![a]);
        assert_eq!(bx.near((505.0, 505.0), (506.0, 506.0)), vec![b]);
        assert!(bx.near((900.0, 900.0), (901.0, 901.0)).is_empty());
        assert_eq!(bx.examined, 2);
        assert_eq!(bbox(&[(1.0, 5.0), (3.0, -2.0)]), ((1.0, -2.0), (3.0, 5.0)));
    }

    #[test]
    fn a_segment_is_filed_in_every_cell_it_crosses() {
        let mut ix = Index::default();
        let id = ix.file((10.0, 10.0), (10.0 + 3.0 * CELL_FT, 10.0));
        assert_eq!(ix.touched, 4, "four cells along a row");
        let diag = ix.file_w((1.0, 1.0), (130.0, 120.0), 4.0);
        assert!((ix.widest - 4.0).abs() < 1e-9, "the widest kept as filed");
        assert!(ix.near((100.0, 100.0), (101.0, 101.0)).contains(&diag));
        assert!(ix.near((5.0, 5.0), (6.0, 6.0)).contains(&id));
        assert!(ix.near((1000.0, 1000.0), (1001.0, 1001.0)).is_empty());
        let back = ix.file((200.0, 300.0), (-50.0, -10.0));
        assert!(ix.near((-1.0, -9.0), (199.0, 299.0)).contains(&back));
        let dot = ix.file((5.0, 5.0), (5.0, 5.0));
        assert!(ix.near((0.0, 0.0), (1.0, 1.0)).contains(&dot));
    }
}
