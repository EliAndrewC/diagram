//! The seat's indexes (feature 444 T27, the derivation's Indexes): a ring's edges filed by horizontal strip, so a point is tested
//! against the edges of its own strip; and a grid of cells, each holding the items whose boxes cover it.
//!
//! Research:
//!     the indexes - NONE: plane geometry and its indexes

#![expect(
    clippy::many_single_char_names,
    clippy::cast_possible_truncation,
    reason = "the plane geometry's own names; grid cells of a few thousand, inside i64"
)]
use std::collections::HashMap;

use crate::field::fan::Pt;
use crate::field::geom::signed_area;

/// The strips' and the cells' side (feet).
///
/// Research:
///     index cells - NONE: an index's grain, which decides nothing about the place - 64 ft
pub const CELL: f64 = 64.0;

fn row(y: f64) -> i64 {
    (y / CELL).floor() as i64
}

/// A ring's edges filed by horizontal strip.
pub struct Strips {
    strips: HashMap<i64, Vec<(Pt, Pt)>>,
}

impl Strips {
    /// The ring's edges, each filed in every strip its height spans.
    #[must_use]
    pub fn new(ring: &[Pt], filed: &mut u64) -> Self {
        let mut strips: HashMap<i64, Vec<(Pt, Pt)>> = HashMap::new();
        let n = ring.len();
        for i in 0..n {
            let (a, b) = (ring[i], ring[(i + 1) % n]);
            for k in row(a.1.min(b.1))..=row(a.1.max(b.1)) {
                strips.entry(k).or_default().push((a, b));
                *filed += 1;
            }
        }
        Self { strips }
    }

    /// Whether `p` lies inside the ring (even-odd), from the edges of its strip alone: an edge the point's horizontal ray can
    /// cross spans the point's height, so it is filed in the point's strip.
    #[must_use]
    pub fn inside(&self, p: Pt, tests: &mut u64) -> bool {
        *tests += 1;
        let Some(edges) = self.strips.get(&row(p.1)) else {
            return false;
        };
        let mut odd = false;
        for &(a, b) in edges {
            *tests += 1;
            if (a.1 > p.1) != (b.1 > p.1) && p.0 < (b.0 - a.0) * (p.1 - a.1) / (b.1 - a.1) + a.0 {
                odd = !odd;
            }
        }
        odd
    }
}

/// A grid of cells, each holding the indexes of the items whose boxes cover it.
pub struct Cells {
    side: f64,
    cells: HashMap<(i64, i64), Vec<usize>>,
}

impl Cells {
    /// An empty grid of cells `side` feet across.
    #[must_use]
    pub fn new(side: f64) -> Self {
        Self {
            side,
            cells: HashMap::new(),
        }
    }

    fn at(&self, v: f64) -> i64 {
        (v / self.side).floor() as i64
    }

    /// Item `i` filed in every cell its box covers; returns the cells filed.
    pub fn file(&mut self, i: usize, pts: &[Pt]) -> u64 {
        let (mut x0, mut y0, mut x1, mut y1) = (f64::MAX, f64::MAX, f64::MIN, f64::MIN);
        for p in pts {
            x0 = x0.min(p.0);
            y0 = y0.min(p.1);
            x1 = x1.max(p.0);
            y1 = y1.max(p.1);
        }
        let mut n = 0;
        for cx in self.at(x0)..=self.at(x1) {
            for cy in self.at(y0)..=self.at(y1) {
                self.cells.entry((cx, cy)).or_default().push(i);
                n += 1;
            }
        }
        n
    }

    /// The distinct items filed in the cells a box covers, and the cells read.
    #[must_use]
    pub fn in_box(&self, lo: Pt, hi: Pt) -> (Vec<usize>, u64) {
        let mut seen = Vec::new();
        let mut read = 0;
        for cx in self.at(lo.0)..=self.at(hi.0) {
            for cy in self.at(lo.1)..=self.at(hi.1) {
                read += 1;
                for &i in self.cells.get(&(cx, cy)).map_or(&[][..], Vec::as_slice) {
                    read += 1; // each item read and checked against those already handed back, a handful a box
                    if !seen.contains(&i) {
                        seen.push(i);
                    }
                }
            }
        }
        (seen, read)
    }
}

/// `subject` clipped to the convex ring `clip` (Sutherland-Hodgman), its corners turning either way.
#[must_use]
pub fn clipped(subject: &[Pt], clip: &[Pt]) -> Vec<Pt> {
    let sense = signed_area(clip).signum();
    let mut out = subject.to_vec();
    let n = clip.len();
    for i in 0..n {
        let (a, b) = (clip[i], clip[(i + 1) % n]);
        let side = |p: Pt| sense * ((b.0 - a.0) * (p.1 - a.1) - (b.1 - a.1) * (p.0 - a.0)) >= 0.0;
        let input = std::mem::take(&mut out);
        let m = input.len();
        for k in 0..m {
            let (p, q) = (input[k], input[(k + 1) % m]);
            let (pin, qin) = (side(p), side(q));
            if pin {
                out.push(p);
            }
            if pin != qin {
                let (dp, dq) = (
                    (b.0 - a.0) * (p.1 - a.1) - (b.1 - a.1) * (p.0 - a.0),
                    (b.0 - a.0) * (q.1 - a.1) - (b.1 - a.1) * (q.0 - a.0),
                );
                let t = dp / (dp - dq);
                out.push((p.0 + (q.0 - p.0) * t, p.1 + (q.1 - p.1) * t));
            }
        }
    }
    out
}

/// The area of a ring, unsigned.
#[must_use]
pub fn area(ring: &[Pt]) -> f64 {
    signed_area(ring).abs()
}
