//! The audit's raster measurements (feature 449 T174): `l7r/diagram/tools/pack_audit/grids.py` ported whole - the occupancy grids
//! ([`grids`]) and what is counted on them: [`coverage`], [`perimeter_hugging_pct`], [`top_vacant_rects`], [`region_density`]. The size
//! marks read its [`FTPX`]; the audit's core reads the rest next (the plan's step 1).
//!
//! Every count and figure is the Python's: a cell index is `int(float // int)` as `CPython` computes a float floor division
//! ([`crate::py::floordiv`]), a share is the Python's int-by-int division, and an area its `round()`, half to even.
//!
//! LOCKSTEP (`ask:449-engine-order` condition 3): `grids.py` stays for `pack_audit`'s Python checks and report until step 3; an edit of it
//! makes the same change here in the same commit, and `parse/lockstep.rs` holds the two equal on every pool sheet. Its claims stay keyed
//! to the `.py` units (`ask:449-phase4-slices` Q10); each copy here carries the same claim.
//!
//! Research:
//!     the grid measures - NONE: a sheet's rects counted on a grid of cells, deciding nothing about a building

use l7r_gate_research::Error;

use crate::parse::{ParsedPlan, Rect};
use crate::py::{floordiv, int, round_int};

/// 3 px = 1 ft.
///
/// Research:
///     feet to pixels - NONE: the audit's 3 px to 1 ft scale, a pixel scale.
pub const FTPX: f64 = 3.0;

// THE PYTHON'S DEFAULT ARGUMENTS, as constants (feature 449 T174): Rust has no default arguments, so each figure `grids.py`'s signatures
// default to lives here - where its claim can stand beside it, and where an edit of a default there is made in the same commit (the
// lockstep compares each to the Python's signature, `parse/lockstep_audit.rs`). A caller passes them as the Python's caller took them.

/// The grid's cell, px (every measure's `cell=2`).
pub const CELL: usize = 2;

/// The perimeter band's depth for [`perimeter_hugging_pct`], ft (its `depth_ft=25.0`).
///
/// Research:
///     its band depth - GUESS: searched, the record silent (feature 417 T38, 2026-10-25) - 25 ("one building-depth" from a wall)
pub const HUG_DEPTH_FT: f64 = 25.0;

/// How many vacant rectangles [`top_vacant_rects`] reports (its `n=3`).
pub const VACANT_N: usize = 3;

/// The smallest vacant rectangle [`top_vacant_rects`] reports, sq ft (its `min_area_sqft=150.0`).
///
/// Research:
///     its search steps and tolerances - GUESS: no source could speak to it, a value of ours (feature 417 T38 pass N13, 2026-10-25) - 150 (smallest vacant rect reported)
pub const VACANT_MIN_SQFT: f64 = 150.0;

/// The perimeter band's depth a vacant rectangle is zoned by, ft (its `perimeter_depth_ft=25.0`).
///
/// Research:
///     its unstated figures - GUESS: searched, the record silent (feature 417 T38 pass N13, 2026-10-25) - 25 (perimeter band depth)
pub const VACANT_DEPTH_FT: f64 = 25.0;

/// The tiles of [`region_density`], rows by columns (its `rows=3, cols=3`).
pub const DENSITY_TILES: (usize, usize) = (3, 3);

/// One flag a cell, rows of columns.
pub type Grid = Vec<Vec<bool>>;

/// A maximal empty rectangle, sized in feet with its SVG-pixel top-left.
#[derive(Debug, Clone, PartialEq)]
pub struct VacantRect {
    pub w_ft: f64,
    pub h_ft: f64,
    /// the Python's `round()`, an integer
    pub area_sqft: i64,
    pub x: f64,
    pub y: f64,
    /// "central" (courtyard) or "perimeter" (gap in the wall ring)
    pub zone: &'static str,
}

impl VacantRect {
    /// Its long axis.
    #[must_use]
    pub fn orient(&self) -> &'static str {
        if self.w_ft >= self.h_ft {
            "horizontal"
        } else {
            "vertical"
        }
    }
}

/// Building coverage within one tile of the interior grid.
#[derive(Debug, Clone, PartialEq)]
pub struct RegionTile {
    pub row: usize,
    pub col: usize,
    pub coverage_pct: f64,
    /// the Python's `round()`, an integer
    pub interior_sqft: i64,
}

/// The plan's four masks on one grid (the Python's `_Grids`): inside the walls, built, occupied, and court dividers.
#[derive(Debug, Clone, PartialEq)]
pub struct Grids {
    pub inside: Grid,
    pub building: Grid,
    pub occ: Grid,
    pub divider: Grid,
    pub w: usize,
    pub h: usize,
    pub minx: f64,
    pub miny: f64,
    pub cell: usize,
}

/// `int(v // cell)`.
fn cell_of(v: f64, cell: usize) -> Result<i64, Error> {
    int(floordiv(v, as_f(cell))?)
}

#[expect(
    clippy::cast_precision_loss,
    reason = "a cell count as Python's int-to-float converts it, exact below 2^53"
)]
fn as_f(n: usize) -> f64 {
    n as f64
}

/// A grid's extent in cells: `max(1, int(span // cell) + 1)`.
fn extent(span: f64, cell: usize) -> Result<usize, Error> {
    let n = cell_of(span, cell)?.saturating_add(1).max(1);
    Ok(usize::try_from(n).unwrap_or(usize::MAX))
}

/// A grid index range `max(0, lo)..min(len, hi)`, empty where it crosses.
fn span(lo: i64, hi: i64, len: usize) -> std::ops::Range<usize> {
    let clamp = |v: i64| usize::try_from(v.max(0)).unwrap_or(0).min(len);
    clamp(lo)..clamp(hi).max(clamp(lo))
}

fn paint(mask: &mut Grid, r: &Rect, g: (usize, f64, f64, usize, usize)) -> Result<(), Error> {
    let (cell, left, top, w, h) = g;
    let rows = span(
        cell_of(r.y - top, cell)?,
        cell_of(r.y + r.h - top, cell)?.saturating_add(1),
        h,
    );
    let cols = span(
        cell_of(r.x - left, cell)?,
        cell_of(r.x + r.w - left, cell)?.saturating_add(1),
        w,
    );
    for row in &mut mask[rows] {
        for c in &mut row[cols.clone()] {
            *c = true;
        }
    }
    Ok(())
}

/// The plan's masks on a grid of `cell` px: the interior painted inside, the buildings built and occupied, the open features and glyphs
/// occupied, the dividers apart.
///
/// # Errors
/// The Python's: no interior (`min()` of nothing), a `cell` of 0, a bound that is not a number.
pub fn grids(plan: &ParsedPlan, cell: usize) -> Result<Grids, Error> {
    let (left, top, right, bottom) = plan.bounds()?;
    let w = extent(right - left, cell)?;
    let h = extent(bottom - top, cell)?;
    if w.checked_mul(h).is_none_or(|n| n > 1 << 34) {
        // the Python's `[[False] * w for _ in range(h)]` past memory
        return Err(Error::new("MemoryError", ""));
    }
    let blank = || vec![vec![false; w]; h];
    let (mut inside, mut building, mut occ, mut divider) = (blank(), blank(), blank(), blank());
    let g = (cell, left, top, w, h);
    for r in &plan.interior {
        paint(&mut inside, r, g)?;
    }
    for r in &plan.buildings {
        paint(&mut building, r, g)?;
        paint(&mut occ, r, g)?;
    }
    for r in plan.open_features.iter().chain(&plan.glyphs) {
        paint(&mut occ, r, g)?;
    }
    for r in &plan.dividers {
        paint(&mut divider, r, g)?;
    }
    Ok(Grids {
        inside,
        building,
        occ,
        divider,
        w,
        h,
        minx: left,
        miny: top,
        cell,
    })
}

/// Building footprint as a fraction (0..1) of the walled interior.
///
/// # Errors
/// [`grids`]'; an interior of no cell, the Python's division by zero.
pub fn coverage(plan: &ParsedPlan, cell: usize) -> Result<f64, Error> {
    let g = grids(plan, cell)?;
    let (mut inside, mut built) = (0_usize, 0_usize);
    for (i, b) in g.inside.iter().flatten().zip(g.building.iter().flatten()) {
        if *i {
            inside += 1;
            built += usize::from(*b);
        }
    }
    if inside == 0 {
        return Err(Error::new("ZeroDivisionError", "division by zero"));
    }
    Ok(as_f(built) / as_f(inside))
}

/// Inside cells within `depth_cells` of the interior edge (a wall), by cardinal rays: a DISTANCE TRANSFORM, two sweeps an axis giving each
/// cell its distance to the nearest blocking cell (outside the plan, a divider, or the grid's edge one step out) in each direction, a
/// cell's own status never counting - what a ray walk from every cell decided, at a fraction of its checks (the Python's reason, the GM
/// 2026-08-26).
#[must_use]
pub fn perimeter_band(g: &Grids, depth_cells: i64) -> Grid {
    let (w, h) = (g.w, g.h);
    let blocking = |y: usize, x: usize| !g.inside[y][x] || g.divider[y][x];
    let mut dist = vec![vec![usize::MAX; w]; h];
    let mut sweep = |cells: &mut dyn Iterator<Item = (usize, usize)>| {
        let mut d = 1;
        for (y, x) in cells {
            dist[y][x] = dist[y][x].min(d);
            d = if blocking(y, x) { 1 } else { d + 1 };
        }
    };
    for y in 0..h {
        sweep(&mut (0..w).map(|x| (y, x)));
        sweep(&mut (0..w).rev().map(|x| (y, x)));
    }
    for x in 0..w {
        sweep(&mut (0..h).map(|y| (y, x)));
        sweep(&mut (0..h).rev().map(|y| (y, x)));
    }
    let depth = usize::try_from(depth_cells).unwrap_or(0);
    (0..h)
        .map(|y| {
            (0..w)
                .map(|x| g.inside[y][x] && dist[y][x] <= depth)
                .collect()
        })
        .collect()
}

/// The band's depth in cells: `max(1, int(depth_ft * FTPX / cell))`.
fn depth_cells(depth_ft: f64, cell: usize) -> Result<i64, Error> {
    Ok(int(depth_ft * FTPX / as_f(cell))?.max(1))
}

/// Fraction of building footprint sitting within `depth_ft` of a wall (high = a good ring); the Python's default depth is
/// [`HUG_DEPTH_FT`], which carries its claim.
///
/// Research:
///     its band depth - NONE: the share of built cells within the depth its caller passes; the figure is the hugging band's depth constant's
///
/// # Errors
/// [`grids`]'.
pub fn perimeter_hugging_pct(plan: &ParsedPlan, depth_ft: f64, cell: usize) -> Result<f64, Error> {
    let g = grids(plan, cell)?;
    let band = perimeter_band(&g, depth_cells(depth_ft, cell)?);
    let (mut built, mut hugging) = (0_usize, 0_usize);
    let cells = g.building.iter().flatten().zip(g.inside.iter().flatten());
    for ((b, i), near) in cells.zip(band.iter().flatten()) {
        if *b && *i {
            built += 1;
            hugging += usize::from(*near);
        }
    }
    Ok(if built == 0 {
        0.0
    } else {
        as_f(hugging) / as_f(built)
    })
}

/// Largest all-true axis-aligned rectangle: (area, left, top, width, height) in cells, the first of equal areas kept.
fn max_rect(mask: &Grid, w: usize) -> (usize, usize, usize, usize, usize) {
    let mut heights = vec![0_usize; w];
    let mut best = (0, 0, 0, 0, 0);
    for (y, row) in mask.iter().enumerate() {
        for (x, cell) in row.iter().enumerate() {
            heights[x] = if *cell { heights[x] + 1 } else { 0 };
        }
        let mut stack: Vec<usize> = Vec::new();
        let mut x = 0;
        while x <= w {
            let cur = if x < w { heights[x] } else { 0 };
            match stack.last() {
                Some(&t) if cur < heights[t] => {
                    stack.pop();
                    let left = stack.last().map_or(0, |&s| s + 1);
                    let width = x - left;
                    let area = heights[t] * width;
                    if area > best.0 {
                        best = (area, left, y + 1 - heights[t], width, heights[t]);
                    }
                }
                _ => {
                    stack.push(x);
                    x += 1;
                }
            }
        }
    }
    best
}

/// The `n` largest non-overlapping empty rectangles, largest first (greedy), each tagged "central" (courtyard - good) or "perimeter" (a
/// gap in the wall ring - slack) by whether its centroid sits in the perimeter band. The Python's defaults are [`VACANT_N`], [`CELL`],
/// [`VACANT_MIN_SQFT`] and [`VACANT_DEPTH_FT`], which carry their claims.
///
/// Research:
///     its search steps and tolerances - NONE: the greedy search for the largest empty rectangles over the floor and band depth its caller passes; the figures are the vacant floor's and band depth's constants'
///
/// # Errors
/// [`grids`]'.
pub fn top_vacant_rects(
    plan: &ParsedPlan,
    n: usize,
    cell: usize,
    min_area_sqft: f64,
    perimeter_depth_ft: f64,
) -> Result<Vec<VacantRect>, Error> {
    let g = grids(plan, cell)?;
    let band = perimeter_band(&g, depth_cells(perimeter_depth_ft, cell)?);
    let mut vacant: Grid = g
        .inside
        .iter()
        .zip(&g.occ)
        .map(|(i, o)| i.iter().zip(o).map(|(i, o)| *i && !*o).collect())
        .collect();
    let floor_px = min_area_sqft * FTPX * FTPX;
    let mut out = Vec::new();
    for _ in 0..n {
        let (area, left, top, wc, hc) = max_rect(&vacant, g.w);
        if as_f(area * cell * cell) < floor_px {
            break;
        }
        let (cy, cx) = (top + hc / 2, left + wc / 2);
        out.push(VacantRect {
            w_ft: as_f(wc * cell) / FTPX,
            h_ft: as_f(hc * cell) / FTPX,
            area_sqft: whole(as_f(area * cell * cell) / (FTPX * FTPX)),
            x: as_f(left * cell) + g.minx,
            y: as_f(top * cell) + g.miny,
            zone: if band[cy][cx] { "perimeter" } else { "central" },
        });
        for row in &mut vacant[top..top + hc] {
            for v in &mut row[left..left + wc] {
                *v = false;
            }
        }
    }
    Ok(out)
}

/// `round()` of a finite count's share, an integer.
#[expect(
    clippy::cast_possible_truncation,
    reason = "a count of cells' feet, whole and far inside i64"
)]
fn whole(v: f64) -> i64 {
    round_int(v).unwrap_or(0.0) as i64
}

/// Per-tile building coverage over the interior (exposes local sparsity).
///
/// # Errors
/// [`grids`]'.
pub fn region_density(
    plan: &ParsedPlan,
    rows: usize,
    cols: usize,
    cell: usize,
) -> Result<Vec<RegionTile>, Error> {
    let g = grids(plan, cell)?;
    let mut tiles = Vec::new();
    for row in 0..rows {
        let (top, bottom) = (row * g.h / rows, (row + 1) * g.h / rows);
        for col in 0..cols {
            let (left, right) = (col * g.w / cols, (col + 1) * g.w / cols);
            let (mut inside, mut built) = (0_usize, 0_usize);
            for y in top..bottom {
                for x in left..right {
                    if g.inside[y][x] {
                        inside += 1;
                        built += usize::from(g.building[y][x]);
                    }
                }
            }
            let pct = if inside == 0 {
                0.0
            } else {
                as_f(built) / as_f(inside)
            };
            tiles.push(RegionTile {
                row,
                col,
                coverage_pct: pct,
                interior_sqft: whole(as_f(inside * cell * cell) / (FTPX * FTPX)),
            });
        }
    }
    Ok(tiles)
}

#[cfg(test)]
mod tests;
