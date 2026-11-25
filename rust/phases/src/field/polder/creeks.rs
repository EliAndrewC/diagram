//! A dike-pond block's creeks and the lattice every polder channel reads (feature 449 T420): the creek's width, each column's
//! sides and the middle of the corridor between two columns, the narrowest corridor, and the mosaic's drift eased until every
//! corridor holds its creek. The channels themselves are `super::ditches` and `super::row_ditches`.
//!
//! Research:
//!     the creeks' module - NONE: the units below carry each decision's claim

use super::Plot;
use crate::field::fan::Pt;
use crate::field::geom::seg_dist;
use crate::pyrand::knob_rng;

/// The width of a channel between a dike-pond block's ponds, least and most (feet): each block's one width is rolled between them
/// (`creek_width`).
///
/// Research:
///     the creek's width - GUESS research/questions/0018-dike-ponds-fish-ponds-ringed-by-mulberry-dikes-sangji-yutang.drawing.html#creek-width-between-ponds: a canal between ponds drawn about 6 to 8 ft wide, no page giving a channel between ponds a width before modern times
pub const CREEK_FT: (f64, f64) = (6.0, 8.0);
/// The steps a mosaic's drift is eased in, each this share of its full strength (`eased`).
///
/// Research:
///     the easing's steps - GUESS research/questions/0019-polders-fields-diked-against-the-fluctuating-water-weitian-waju.drawing.html#pinched-mosaic-eased: a mosaic that would pinch a creek is bent less, the bend eased a twentieth at a time until every corridor holds its creek - twenty steps, a twentieth of the full strength each, fine enough that an eased block keeps nearly all its drift (the worst of 51 rolled mosaics, 2026-11-24, feature 449 T420, needed its corridors about a fifth straighter)
pub const EASE_STEPS: u32 = 20;
/// A dike-pond block's creek width (feet): one figure for every channel between its ponds, down the columns and across the rows,
/// rolled between `CREEK_FT`'s ends from the seed's own `polder_creek` stream, so no other roll of the block moves with it.
///
/// Research:
///     one width a block - GUESS research/questions/0018-dike-ponds-fish-ponds-ringed-by-mulberry-dikes-sangji-yutang.drawing.html#one-creek-width-a-block: each dike-pond block takes one creek width, chosen by chance anywhere in the 6 to 8 ft (#creek-width-between-ponds), every creek of the block drawn at it, down a column and across a row, end to end with no taper - each block's width rolled evenly over the range, to a thousandth of it, from the seed's own `polder_creek` stream
pub(super) fn creek_width(seed: i64) -> f64 {
    let mut rng = knob_rng(seed, "polder_creek");
    CREEK_FT.0 + (CREEK_FT.1 - CREEK_FT.0) * f64::from(rng.randbelow(1001)) / 1000.0
}

/// The block's plots with room for its creeks: the lattice's deformation kept whole where every corridor between the plots is
/// at least `creek` wide, and where one is pinched narrower, eased a step in `EASE_STEPS` at a time until none is - the share
/// kept and the plots laid at it. A rice polder (no `creek`) keeps the whole.
///
/// Research:
///     room for the creeks - GUESS research/questions/0019-polders-fields-diked-against-the-fluctuating-water-weitian-waju.drawing.html#pinched-mosaic-eased: where the full bend would leave a corridor between two ponds narrower than the creek drawn in it (a canal between ponds about 6 to 8 ft wide, GUESS research/questions/0018-dike-ponds-fish-ponds-ringed-by-mulberry-dikes-sangji-yutang.drawing.html#creek-width-between-ponds), that block is bent less, so no creek is laid over a bank and no pond is drawn smaller (the GM 2026-10-12, room before packing) - the drift eased block by block, a mosaic no corridor of which is pinched keeping it whole (Kuwabata's does); 13 of 51 rolled mosaics held a corridor of 4 to 7 ft under a creek of 6 to 8 (measured 2026-11-24, feature 449 T420)
pub(super) fn eased(
    put_at: &dyn Fn(f64, f64, f64) -> Pt,
    lay: &dyn Fn(f64) -> Vec<Plot>,
    lattice: (f64, (f64, f64)),
    grid: (usize, usize),
    creek: Option<f64>,
) -> (f64, u64, Vec<Plot>) {
    let whole = lay(1.0);
    let Some(w) = creek else {
        return (1.0, 0, whole);
    };
    let mut tests = 0_u64;
    let mut roomy = |ease: f64| {
        let put = |u: f64, x: f64| put_at(ease, u, x);
        let lattice = Lattice {
            put: &put,
            plots: &whole,
            module: lattice.0,
            gaps: lattice.1,
        };
        let (least, asked) = lattice.narrowest(grid);
        tests += asked;
        least >= w
    };
    // the deformation scales with the share kept, and with none kept every corridor is its whole gap
    let ease = (0..EASE_STEPS)
        .map(|k| 1.0 - f64::from(k) / f64::from(EASE_STEPS))
        .find(|&ease| roomy(ease))
        .unwrap_or(0.0);
    if ease < 1.0 {
        (ease, tests, lay(ease))
    } else {
        (1.0, tests, whole)
    }
}

/// The stations of a channel down a column corridor of `row_n` rows, from `head` to `tail` down the fall: every row's start and
/// end and the middle of every gap between rows, where the plots beside it keep their corners (`plots`).
///
/// Research:
///     the stations - NONE: geometry, the plots' own corner lines
pub(super) fn stations(row_n: usize, module: f64, row_gap: f64, ends: (f64, f64)) -> Vec<f64> {
    let mut out = vec![ends.0];
    for r in 0..row_n {
        #[expect(clippy::cast_precision_loss, reason = "a small count")]
        let u0 = r as f64 * (module + row_gap);
        out.extend([u0, u0 + module]);
        if r + 1 < row_n {
            out.push(u0 + module + row_gap / 2.0);
        }
    }
    out.push(ends.1);
    out
}

/// The block's lattice as its channels read it: the warped frame (`put`), the plots laid on it, the module and the gaps between
/// rows and between columns (feet).
///
/// Research:
///     the lattice's record - NONE: the record's type, holding what `polder` hands its channels
pub(super) struct Lattice<'a> {
    pub(super) put: &'a dyn Fn(f64, f64) -> Pt,
    pub(super) plots: &'a [Plot],
    pub(super) module: f64,
    pub(super) gaps: (f64, f64),
}

impl Lattice<'_> {
    /// The point of column `col`'s side on the lattice line `x` (its first or last edge), `u` down the fall: on a plot's side,
    /// the point of the straight run between the corners it keeps there - its ends and, on a merged pair, the middle row line's -
    /// and off every plot (a gap between rows, the block's ends) the lattice's own.
    ///
    /// Research:
    ///     a side's point - NONE: geometry, the plots' own sides as `plots` lays them
    #[expect(
        clippy::many_single_char_names,
        reason = "the plane geometry's own names"
    )]
    pub(super) fn side(&self, col: usize, x: f64, u: f64) -> Pt {
        let pitch = self.module + self.gaps.0;
        #[expect(clippy::cast_precision_loss, reason = "a small count")]
        let ends = |p: &Plot| {
            (
                p.row as f64 * pitch,
                (p.row + p.span) as f64 * pitch - self.gaps.0,
            )
        };
        let Some(p) = self.plots.iter().find(|p| {
            let (u0, u1) = ends(p);
            p.col == col && u0 < u && u < u1
        }) else {
            return (self.put)(u, x);
        };
        let (u0, u1) = ends(p);
        #[expect(clippy::cast_precision_loss, reason = "a small count")]
        let um = (p.row + 1) as f64 * pitch - self.gaps.0 / 2.0;
        // a merged pair keeps a corner on its middle row line; a single plot runs straight from end to end
        let mid = if p.span == 2 { um } else { u1 };
        let (a, b) = if u < mid { (u0, mid) } else { (mid, u1) };
        let (pa, pb, t) = ((self.put)(a, x), (self.put)(b, x), (u - a) / (b - a));
        (pa.0 + (pb.0 - pa.0) * t, pa.1 + (pb.1 - pa.1) * t)
    }

    /// The middle of the corridor between column `c - 1` and column `c`, `u` down the fall: midway between the two sides it runs
    /// between (`side`), so a channel on it stands as far from one bank as from the other.
    ///
    /// Research:
    ///     midway between its banks - research/questions/0022-parcels-and-bunds-inside-a-polder-aze.drawing.html: between one column of modules and the next, a ditch corridor - the channel on the corridor's middle as the plots' sides draw it; a merged pair keeps one straight side from its end to the middle row line, where the lattice's own line bows away from it, and a channel on the lattice's line stood up to 4.6 ft off the middle beside such a side (27 of 51 rolled mosaics, measured 2026-11-24, feature 449 T420)
    #[expect(
        clippy::many_single_char_names,
        reason = "the plane geometry's own names"
    )]
    pub(super) fn midway(&self, c: usize, u: f64) -> Pt {
        #[expect(clippy::cast_precision_loss, reason = "a small count")]
        let x = c as f64 * (self.module + self.gaps.1);
        let (l, r) = (self.side(c - 1, x - self.gaps.1, u), self.side(c, x, u));
        (f64::midpoint(l.0, r.0), f64::midpoint(l.1, r.1))
    }

    /// The narrowest corridor between the block's plots (feet) and the distances measured for it, `grid` its rows and columns: between two columns, the least
    /// distance from a side's point at a station to the facing side's runs either way of it; between two plots of one column,
    /// from each facing corner to the other plot's edge.
    ///
    /// Research:
    ///     the corridors measured - NONE: geometry, each column's sides read at the channels' own stations, a few hundred distances a block, no scan of plot against plot (constitution X clause 15)
    pub(super) fn narrowest(&self, grid: (usize, usize)) -> (f64, u64) {
        let (module, (row_gap, col_gap)) = (self.module, self.gaps);
        let pitch = module + row_gap;
        #[expect(clippy::cast_precision_loss, reason = "a small count")]
        let length = grid.0 as f64 * pitch - row_gap;
        let at = stations(grid.0, module, row_gap, (0.0, length));
        let (mut least, mut tests) = (f64::INFINITY, 0_u64);
        let mut facing = |a: &[Pt], b: &[Pt]| {
            for (i, &p) in a.iter().enumerate() {
                for seg in b[i.saturating_sub(1)..(i + 2).min(b.len())].windows(2) {
                    least = least.min(seg_dist(p, seg[0], seg[1]));
                    tests += 1;
                }
            }
        };
        for c in 0..grid.1 {
            #[expect(clippy::cast_precision_loss, reason = "a small count")]
            let x = c as f64 * (module + col_gap);
            if c > 0 {
                let left: Vec<Pt> = at
                    .iter()
                    .map(|&u| self.side(c - 1, x - col_gap, u))
                    .collect();
                let right: Vec<Pt> = at.iter().map(|&u| self.side(c, x, u)).collect();
                facing(&left, &right);
                facing(&right, &left);
            }
            for p in self
                .plots
                .iter()
                .filter(|p| p.col == c && p.row + p.span < grid.0)
            {
                #[expect(clippy::cast_precision_loss, reason = "a small count")]
                let u = (p.row + p.span) as f64 * pitch;
                let upper = [
                    (self.put)(u - row_gap, x),
                    (self.put)(u - row_gap, x + module),
                ];
                let lower = [(self.put)(u, x), (self.put)(u, x + module)];
                facing(&upper, &lower);
                facing(&lower, &upper);
            }
        }
        (least, tests)
    }
}
