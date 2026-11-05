//! Each household's share of the homestead wood (feature 444 T30): reserved at its seat, a lattice of seats within the dooryard's
//! reach taken behind the house first and spreading to the flanks, each seat kept where no part's keep-out, no other homestead's,
//! no taken ground, no stream between it and its house and no other household's ground bars it, until the ground the kept seats'
//! crowns cover - the canopy raster's cells no household holds - covers the floor; else the seat is refused. The lattice is
//! anchored on the house, as `wood_share.py` anchors it (`WoodShares.share`, `crown_cells`).
//!
//! Research:
//!     each household's floor reserved - research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.drawing.html: crowns covering the floor on ground no other household holds, or the seat refused
//!     seats behind the house - research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.html: the deep stands stood windward, northwest by default, the house's south left open (0028); the 0.7 is ours
//!     a seat's ground its crown's cells - research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.drawing.html: crowns covering the floor on ground no other household holds; the canopy raster's 2 ft cells, a cell held where its center lies within a crown (`wood_canopy`'s raster)

use super::Counts;
use std::collections::{HashMap, HashSet};

use super::fit::{crossing, GRID};
use super::ground::Ground;
use super::layout::Rect;
use crate::field::fan::Pt;

/// The homestead's wood: its floor (sq ft) and its reach from the house (ft).
///
/// Research:
///     the homestead's wood - research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.drawing.html: at least 6,000 sq ft within 90 ft of the house
pub const WOOD: (f64, f64) = (6000.0, 90.0);

/// The gap a corridor's line keeps off a reserved seat: the corridor's half-width, the crown's reach (or 0.45 of the clump and
/// 4 ft) and the placer's margin.
///
/// Research:
///     path refused over a household's reserved grove seats - research/questions/0081-village-lanes.drawing.html: a path goes round a grove, never across one (0036, 0072)
#[must_use]
pub fn lane_gap(half: f64, bscale: f64) -> f64 {
    let (clump, lift) = (CLUMP_FT * bscale, 3.0 * bscale / 0.82);
    let r = clump / 2.0 - 2.0;
    half + (clump * 0.45 + 4.0).max(r.hypot(r + lift)) + MARGINS.0
}

/// The copse's clump, across (ft), and the lattice's pitch: the clump's radius times the square root of two, the widest square
/// lattice whose crowns leave no point of a cell bare.
///
/// Research:
///     copse clump size - research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.drawing.html: 22 bscale units, an 11 ft radius against the 8.5 ft mean crown
pub const CLUMP_FT: f64 = 22.0;

/// The lattice's pitch (ft).
pub const PITCH_FT: f64 = 11.0 * std::f64::consts::SQRT_2;

/// The canopy raster's cell (ft) and a reserved crown's radius (ft, the clump's half to a tenth, as the planted copse records it).
///
/// Research:
///     the canopy raster - CONVENTION: `wood_canopy`'s raster, 2 bscale units a cell, the cells a crown covers counted as its ground
pub const CANOPY: (f64, f64) = (2.0, 11.0);

/// Where the reservation is centered behind the house (a share of the reach), and how much dearer a foot aside is than a foot
/// deeper.
///
/// Research:
///     flanks after the back - GUESS: no source could speak to it, a value of ours (feature 417 T36 pass P1, 2026-10-25); a foot aside costs twice a foot deeper
pub const FOCUS: (f64, f64) = (0.7, 2.0);

/// The plots' sun the copse keeps off: south of each yard and bed, the morning lane east of it, the afternoon lane west (ft).
///
/// Research:
///     plots' sun strips - research/questions/0038-sunlight-and-shade-on-the-farm.drawing.html: a tree's 50 ft south of each yard and bed, 50 ft east of each down to 50 ft below it, and west and southwest at the map's afternoon lane
pub const SUN_LANES_FT: (f64, f64, f64) = (50.0, 50.0, 50.0);

/// How far a clump's center keeps off a well pocket's center (ft): the wellhead's drawn half-size, 1.05 clumps, a foot and the
/// placer's margin.
///
/// Research:
///     copse off the wellhead - GUESS: no source could speak to it, a value of ours (feature 417 T36 pass P1, 2026-10-25); its drawn half-size (12.376 ft, research/questions/0196-communal-wells-ido.drawing.html) plus 1.05 clumps
pub const WELL_KEEPOUT_FT: f64 = 12.376 + CLUMP_FT * 1.05 + 1.0 + MARGINS.0;

/// The margin a keep-out is grown by, and the sheet's inset a seat keeps (ft).
///
/// Research:
///     its drawn sizes - CONVENTION: sizes on the sheet, not in the world - 6 (seats kept 6 px off the sheet's edge); 0.5 (the placer's margin over the planting's own keep-outs)
pub const MARGINS: (f64, f64) = (0.5, 6.0);

/// A homestead's copse keep-outs: discs a clump's center may not enter, and open rectangles (x0, y0, x1, y1) it may not stand in.
pub type Keepouts = (Vec<(f64, f64, f64)>, Vec<(f64, f64, f64, f64)>);

/// The copse keep-outs of one homestead's parts: a disc round each building and plot (half its diagonal, the clump's radius and
/// 2 ft), the sunny strip south of each yard and bed, its morning lane east, and its afternoon lane west and southwest.
///
/// Research:
///     clump beside, never on, a building - research/questions/0071-groves-around-a-southern-chinese-village-the-fengshui-woods-fengshuilin-and-the-dooryard-copse.drawing.html: half the diagonal plus the clump's radius and 2 px
#[must_use]
pub fn keepouts(solids: &[Rect], plots: &[Rect]) -> Keepouts {
    let (cr, m) = (CLUMP_FT / 2.0, MARGINS.0);
    let (south_ft, east_ft, west_ft) = SUN_LANES_FT;
    let circles = solids
        .iter()
        .chain(plots)
        .map(|r| (r.0, r.1, 0.5 * r.2.hypot(r.3) + cr + 2.0 + m))
        .collect();
    let mut rects = Vec::new();
    for r in plots {
        let (half, south) = (r.2 / 2.0 + cr + 2.0, r.1 + r.3 / 2.0);
        rects.push((
            r.0 - half - m,
            south - cr - 2.0 - m,
            r.0 + half + m,
            south + south_ft + 2.0 + cr + m,
        ));
        let (east, ehalf) = (r.0 + r.2 / 2.0, r.3 / 2.0 + cr + 2.0);
        rects.push((
            east - cr - 2.0 - m,
            r.1 - ehalf - m,
            east + east_ft + cr + m,
            r.1 + ehalf + east_ft + m,
        ));
        let (west_x, top_y, bottom_y) = (r.0 - r.2 / 2.0, r.1 - r.3 / 2.0, r.1 + r.3 / 2.0);
        rects.push((
            west_x - west_ft - cr - 3.0 - m,
            top_y - cr - 1.0 - m,
            west_x + cr + 1.0 + m,
            bottom_y + west_ft + cr + 1.0 + m,
        ));
    }
    (circles, rects)
}

/// Is (x, y) inside any of the keep-outs?
#[must_use]
pub fn in_keepouts(p: Pt, k: &Keepouts) -> bool {
    k.0.iter()
        .any(|&(cx, cy, r)| (p.0 - cx).powi(2) + (p.1 - cy).powi(2) < r * r)
        || k.1
            .iter()
            .any(|&(x0, y0, x1, y1)| x0 < p.0 && p.0 < x1 && y0 < p.1 && p.1 < y1)
}

#[expect(
    clippy::cast_possible_truncation,
    reason = "cell indices of a few hundred"
)]
fn cell(v: f64, size: f64) -> i64 {
    (v / size).floor() as i64
}

/// The canopy cells a crown at `p` of radius `r` covers, the raster `c` a side: each cell whose center lies within the crown,
/// found a column at a time (`wood_share.py` `crown_cells`).
#[must_use]
#[expect(
    clippy::cast_possible_truncation,
    clippy::cast_precision_loss,
    clippy::many_single_char_names,
    reason = "cell indices of a few thousand; the plane geometry's own names"
)]
pub fn crown_cells(p: Pt, r: f64, c: f64) -> Vec<(i64, i64)> {
    let (x, y) = p;
    let r2 = r * r;
    let (j_lo, j_hi) = (((y - r) / c).floor() as i64, ((y + r) / c).floor() as i64);
    let mut out = Vec::new();
    for i in ((x - r) / c).floor() as i64..=((x + r) / c).floor() as i64 {
        let dx2 = ((i as f64 + 0.5) * c - x).powi(2);
        if dx2 > r2 {
            continue;
        }
        let s = (r2 - dx2).sqrt();
        // a cell wider than the circle's span each side, then narrowed by the same test
        let mut lo = j_lo.max(((y - s) / c - 0.5).ceil() as i64 - 1);
        let mut hi = j_hi.min(((y + s) / c - 0.5).floor() as i64 + 1);
        while lo <= hi && dx2 + ((lo as f64 + 0.5) * c - y).powi(2) > r2 {
            lo += 1;
        }
        while hi >= lo && dx2 + ((hi as f64 + 0.5) * c - y).powi(2) > r2 {
            hi -= 1;
        }
        out.extend((lo..=hi).map(|j| (i, j)));
    }
    out
}

/// A value to a tenth (`round(v, 1)`).
fn tenth(v: f64) -> f64 {
    (v * 10.0).round() / 10.0
}

/// The households' wood reservations for one seating: the keep-outs of every homestead admitted, the canopy cells the reserved
/// crowns cover, and the seats.
#[derive(Default)]
pub struct Shares {
    bars: Vec<Keepouts>,
    bar_cells: HashMap<(i64, i64), Vec<usize>>,
    cells: HashSet<(i64, i64)>,
    seats: HashMap<(i64, i64), Vec<Pt>>,
}

/// What a wood share reads besides the reservations: the free ground, the streams, the canvas.
pub struct WoodSite<'a> {
    /// The free ground's raster; a seat on taken ground is barred.
    pub ground: &'a Ground,
    /// The streams' segments.
    pub streams: &'a [(Pt, Pt)],
    /// The canvas (ft).
    pub canvas: Pt,
}

impl Shares {
    /// Would a homestead's keep-outs stand over a seat another household reserved?
    #[must_use]
    pub fn covers_a_seat(&self, own: &Keepouts, tests: &mut Counts) -> bool {
        let boxes = own
            .0
            .iter()
            .map(|&(x, y, r)| (x - r, y - r, x + r, y + r))
            .chain(own.1.iter().copied());
        boxes.into_iter().any(|(x0, y0, x1, y1)| {
            (cell(x0, GRID)..=cell(x1, GRID)).any(|i| {
                (cell(y0, GRID)..=cell(y1, GRID)).any(|j| {
                    tests.add("index_query@covers_a_seat", 1);
                    self.seats
                        .get(&(i, j))
                        .is_some_and(|v| v.iter().any(|&p| in_keepouts(p, own)))
                })
            })
        })
    }

    fn barred(
        &self,
        p: Pt,
        house: Pt,
        own: &Keepouts,
        site: &WoodSite,
        tests: &mut Counts,
    ) -> bool {
        tests.add("pt_test@barred", 4);
        let inset = MARGINS.1;
        if !(inset <= p.0
            && p.0 <= site.canvas.0 - inset
            && inset <= p.1
            && p.1 <= site.canvas.1 - inset)
        {
            return true;
        }
        if (p.0 - house.0).hypot(p.1 - house.1) > WOOD.1 - MARGINS.0 || in_keepouts(p, own) {
            return true;
        }
        let near = self
            .bar_cells
            .get(&(cell(p.0, GRID), cell(p.1, GRID)))
            .map_or(&[][..], Vec::as_slice);
        if near.iter().any(|&k| in_keepouts(p, &self.bars[k])) {
            return true;
        }
        if site.ground.taken_at(p).unwrap_or(true) {
            return true;
        }
        site.streams
            .iter()
            .any(|&(a, b)| crossing((p, house), (a, b)))
    }

    /// The seats a homestead at `house`, turned `rot` degrees, would reserve among its keep-outs `own`: the lattice anchored on the
    /// house within the reach, nearest a point behind the house first, each kept where it is not barred and its crown covers cells
    /// no household holds, until the cells kept cover the floor; None where the ground within the reach cannot hold it.
    #[must_use]
    #[expect(
        clippy::cast_precision_loss,
        clippy::cast_possible_truncation,
        clippy::many_single_char_names,
        reason = "a lattice index of a few, a cell count of a few thousand; the plane geometry's own names"
    )]
    pub fn share(
        &self,
        house: Pt,
        rot: f64,
        own: &Keepouts,
        site: &WoodSite,
        tests: &mut Counts,
    ) -> Option<Vec<Pt>> {
        let (floor, reach) = WOOD;
        let (c, cr) = CANOPY;
        let th = rot.to_radians();
        let (back, aside) = ((th.sin(), -th.cos()), (th.cos(), th.sin()));
        let (depth, lateral) = (FOCUS.0 * reach, FOCUS.1);
        let n = (reach / PITCH_FT).floor() as i64;
        let mut lattice: Vec<(f64, Pt)> = Vec::new();
        for i in -n..=n {
            for j in -n..=n {
                let p = (
                    tenth(house.0 + i as f64 * PITCH_FT),
                    tenth(house.1 + j as f64 * PITCH_FT),
                );
                let (dx, dy) = (p.0 - house.0, p.1 - house.1);
                let (u, v) = (dx * aside.0 + dy * aside.1, dx * back.0 + dy * back.1);
                lattice.push((lateral * u * u + (v - depth).powi(2), p));
            }
        }
        lattice.sort_by(|a, b| a.0.total_cmp(&b.0));
        tests.add("candidate@share", lattice.len() as u64 * 7);
        let mut mine: HashSet<(i64, i64)> = HashSet::new();
        let mut seats = Vec::new();
        for (_, p) in lattice {
            if self.barred(p, house, own, site, tests) {
                continue;
            }
            let crown = crown_cells(p, cr, c);
            tests.add("write@crown_cells", crown.len() as u64);
            let fresh: Vec<(i64, i64)> = crown
                .into_iter()
                .filter(|k| !self.cells.contains(k) && !mine.contains(k))
                .collect();
            if fresh.is_empty() {
                continue;
            }
            mine.extend(fresh);
            seats.push(p);
            if mine.len() as f64 * c * c >= floor {
                return Some(seats);
            }
        }
        None
    }

    /// Every reserved seat.
    pub fn all_seats(&self) -> impl Iterator<Item = &Pt> {
        self.seats.values().flatten()
    }

    /// Would a corridor a-b run within `gap` of a reserved seat? Each seat cell near enough the segment asked of its seats.
    #[must_use]
    pub fn corridor_bars(&self, a: Pt, b: Pt, gap: f64, tests: &mut Counts) -> bool {
        let reach = gap + GRID * 0.5f64.sqrt();
        (cell(a.0.min(b.0) - gap, GRID)..=cell(a.0.max(b.0) + gap, GRID)).any(|i| {
            (cell(a.1.min(b.1) - gap, GRID)..=cell(a.1.max(b.1) + gap, GRID)).any(|j| {
                self.seats.get(&(i, j)).is_some_and(|v| {
                    #[expect(clippy::cast_precision_loss, reason = "a cell index of a few hundred")]
                    let c = ((i as f64 + 0.5) * GRID, (j as f64 + 0.5) * GRID);
                    tests.add("dist@corridor_bars", 1 + v.len() as u64);
                    crate::field::geom::seg_dist(c, a, b) < reach
                        && v.iter()
                            .any(|&p| crate::field::geom::seg_dist(p, a, b) < gap)
                })
            })
        })
    }

    /// Reserve a homestead's seats and file its keep-outs for every later seat.
    pub fn commit(&mut self, seats: &[Pt], own: Keepouts, tests: &mut Counts) {
        for &p in seats {
            let crown = crown_cells(p, CANOPY.1, CANOPY.0);
            tests.add("write@crown_cells", crown.len() as u64);
            self.cells.extend(crown);
            self.seats
                .entry((cell(p.0, GRID), cell(p.1, GRID)))
                .or_default()
                .push(p);
        }
        let k = self.bars.len();
        let boxes: Vec<(f64, f64, f64, f64)> = own
            .0
            .iter()
            .map(|&(x, y, r)| (x - r, y - r, x + r, y + r))
            .chain(own.1.iter().copied())
            .collect();
        for (x0, y0, x1, y1) in boxes {
            for i in cell(x0, GRID)..=cell(x1, GRID) {
                for j in cell(y0, GRID)..=cell(y1, GRID) {
                    let v = self.bar_cells.entry((i, j)).or_default();
                    if v.last() != Some(&k) {
                        v.push(k);
                    }
                    tests.add("write@commit", 1);
                }
            }
        }
        self.bars.push(own);
    }
}
