//! Each household's share of the homestead wood (feature 444 T30): reserved at its seat, a lattice of seats within the dooryard's
//! reach taken behind the house first and spreading to the flanks, each seat kept where no part's keep-out, no other homestead's,
//! no taken ground, no stream between it and its house and no other household's ground bars it, until the ground the kept seats
//! hold covers the floor - else the seat is refused. A seat's ground is its own lattice square, which its crown covers; the
//! lattice is the map's, so two households' squares are one grid and a square is reserved once.
//!
//! Research:
//!     each household's floor reserved - research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.drawing.html: crowns covering the floor on ground no other household holds, or the seat refused
//!     seats behind the house - research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.html: the deep stands stood windward, northwest by default, the house's south left open (0028); the 0.7 is ours
//!     a seat's ground its lattice square - GUESS: the crown (22 ft across) covers its 15.6 ft lattice square, its half-diagonal 11 ft, so the floor counted by squares is at most the floor drawn (feature 444 T30's derivation)

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

/// The copse's clump, across (ft), and the lattice's pitch: the clump's radius times the square root of two, the widest square
/// lattice whose crowns leave no point of a cell bare.
///
/// Research:
///     copse clump size - research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.drawing.html: 22 bscale units, an 11 ft radius against the 8.5 ft mean crown
pub const CLUMP_FT: f64 = 22.0;

/// The lattice's pitch (ft).
pub const PITCH_FT: f64 = 11.0 * std::f64::consts::SQRT_2;

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

/// The households' wood reservations for one seating: the keep-outs of every homestead admitted, the squares reserved, and the
/// seats.
#[derive(Default)]
pub struct Shares {
    bars: Vec<Keepouts>,
    bar_cells: HashMap<(i64, i64), Vec<usize>>,
    squares: HashSet<(i64, i64)>,
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

    /// The seats a homestead at `house`, turned `rot` degrees, would reserve among its keep-outs `own`: the lattice within the reach,
    /// nearest a point behind the house first, each kept where it is not barred and its square no household holds, until the
    /// squares kept cover the floor; None where the ground within the reach cannot hold it.
    #[must_use]
    #[expect(
        clippy::cast_precision_loss,
        reason = "a lattice index of a few hundred"
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
        let th = rot.to_radians();
        let (back, aside) = ((th.sin(), -th.cos()), (th.cos(), th.sin()));
        let (depth, lateral) = (FOCUS.0 * reach, FOCUS.1);
        let mut lattice: Vec<(f64, Pt, (i64, i64))> = Vec::new();
        for i in cell(house.0 - reach, PITCH_FT)..=cell(house.0 + reach, PITCH_FT) {
            for j in cell(house.1 - reach, PITCH_FT)..=cell(house.1 + reach, PITCH_FT) {
                let p = ((i as f64 + 0.5) * PITCH_FT, (j as f64 + 0.5) * PITCH_FT);
                let (dx, dy) = (p.0 - house.0, p.1 - house.1);
                if dx.hypot(dy) > reach {
                    continue;
                }
                let (u, v) = (dx * aside.0 + dy * aside.1, dx * back.0 + dy * back.1);
                lattice.push((lateral * u * u + (v - depth).powi(2), p, (i, j)));
            }
        }
        lattice.sort_by(|a, b| a.0.total_cmp(&b.0));
        tests.add("candidate@share", lattice.len() as u64 * 7);
        let mut seats = Vec::new();
        for (_, p, sq) in lattice {
            if self.squares.contains(&sq) || self.barred(p, house, own, site, tests) {
                continue;
            }
            seats.push(p);
            if seats.len() as f64 * PITCH_FT * PITCH_FT >= floor {
                return Some(seats);
            }
        }
        None
    }

    /// Reserve a homestead's seats and file its keep-outs for every later seat.
    pub fn commit(&mut self, seats: &[Pt], own: Keepouts, tests: &mut Counts) {
        for &p in seats {
            self.squares
                .insert((cell(p.0, PITCH_FT), cell(p.1, PITCH_FT)));
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
