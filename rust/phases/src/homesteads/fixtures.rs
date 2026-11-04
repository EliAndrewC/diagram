//! A homestead's fixtures (feature 444 T30): each kind laid beside the parts already laid, in the house's unturned frame centered on
//! it, in the order the seating lays them - the retirement house, the bath room joined to the house, the wood shed a ken off a
//! wall, the privy within its reach, the manure heap beyond it, the coop, the household shrine and grave at a corner, the
//! persimmon in the dooryard. A kind whose rule finds no seat refuses the homestead's layout (`Unlaid`), never a fixture walked out
//! into the yard. The hamlet's sheet is drawn at a foot a pixel, so every figure is in feet.
//!
//! Research:
//!     fixture gap 3.5 ft off every other part and bath room slide 4 ft - GUESS research/questions/0043-firewood-stacks-and-sheds-kigoya.drawing.html: the gap of about 3.5 ft our maps keep between a house wall and anything beside it
//!     seating order - GUESS: no source could speak to it, a value of ours (feature 417 T36 pass P1, 2026-10-25); the retirement house, bath, wood shed, privy, manure, coop, shrine, grave, persimmon
//!     stepped outward - GUESS: no source could speak to it, a value of ours (feature 417 T36 pass P1, 2026-10-25); a fixture with no recorded seat free is offered the same seats a pace further out

#![expect(
    clippy::many_single_char_names,
    reason = "the plane geometry's and the seating's own names: w, d, g, u for a seat's width, depth, gap and roll"
)]
#![expect(
    clippy::manual_midpoint,
    reason = "two half-sizes summed at a map's few hundred feet, where no overflow is possible"
)]

use super::layout::{kura, Rect};

/// A fixture's kind.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Kind {
    /// The retirement house.
    Retirement,
    /// The bath room, joined to the house.
    Bath,
    /// The wood shed.
    Woodpile,
    /// The privy.
    Privy,
    /// The manure heap or pit.
    Manure,
    /// The chicken coop.
    Coop,
    /// The household shrine.
    Shrine,
    /// The household grave.
    Grave,
    /// The yard persimmon.
    Persimmon,
}

/// The order the kinds are laid in.
pub const ORDER: [Kind; 9] = [
    Kind::Retirement,
    Kind::Bath,
    Kind::Woodpile,
    Kind::Privy,
    Kind::Manure,
    Kind::Coop,
    Kind::Shrine,
    Kind::Grave,
    Kind::Persimmon,
];

/// Each kind's salt for the household's position roll.
///
/// Research:
///     its salts, guards and sentinels - NONE: they decide nothing about the place - 101 to 108 and 131.7 (salts)
#[must_use]
pub fn salt(kind: Kind) -> f64 {
    match kind {
        Kind::Privy => 101.0,
        Kind::Manure => 102.0,
        Kind::Woodpile => 103.0,
        Kind::Bath => 104.0,
        Kind::Coop => 105.0,
        Kind::Shrine => 106.0,
        Kind::Persimmon => 107.0,
        Kind::Retirement => 131.7,
        Kind::Grave => 108.0,
    }
}

/// The gap a fixture keeps off the walls and parts it stands by (feet).
pub const WALL_GAP_FT: f64 = 3.5;

/// The outward pace a fixture takes when every recorded seat is taken (feet), and the paces offered.
pub const STEP: (f64, usize) = (8.0, 24);

/// The spacing of the places offered along a wall to a bath room or a wood shed (feet).
pub const WALL_SLIDE_FT: f64 = 4.0;

/// The yard privy a ken past the wall gap, the front privy's edge 8 ft out from the front wall (feet).
///
/// Research:
///     privy in the yard off the back wall - research/questions/0047-farm-privies-and-their-night-soil-benjo.drawing.html: held at a ken plus the wall gap, past the page's ken
///     privy in the front yard - GUESS research/questions/0047-farm-privies-and-their-night-soil-benjo.drawing.html: its edge 8 ft out from the front wall
pub const PRIVY_STEPS_FT: (f64, f64) = (6.0, 8.0 - WALL_GAP_FT);

/// The privy's sun-side search from 18 to 48 ft, the share of privies seated there, and its reach from its house (feet).
///
/// Research:
///     privy sun-side radii - research/questions/0047-farm-privies-and-their-night-soil-benjo.drawing.html: tried from 18 ft out to the reach, every 4 ft
///     the privy's reach - research/questions/0047-farm-privies-and-their-night-soil-benjo.drawing.html: no more than 48 ft from its house
///     privy sunny share - research/questions/0047-farm-privies-and-their-night-soil-benjo.drawing.html: 72.7% of outhouses SE to S (Wang and Ochiai 2022, used literally)
pub const PRIVY_SUN: (f64, f64, f64) = (18.0, 48.0, 0.727);

/// The wood shed a ken past the wall gap (feet).
///
/// Research:
///     wood shed off its wall - GUESS research/questions/0043-firewood-stacks-and-sheds-kigoya.drawing.html: held at a ken plus the wall gap
pub const WOODSHED_STEP_FT: f64 = 6.0;

/// The bath room: a ken out from its wall, one to two ken along it (feet).
///
/// Research:
///     bath room size - research/questions/0044-baths-on-the-farm-furo.drawing.html: 6 ft out by 6 to 12 ft along
pub const BATH_FT: (f64, (f64, f64)) = (6.0, (6.0, 12.0));

/// The household shrine and grave a plot corner off the house's corner (feet).
///
/// Research:
///     shrine off its corner - research/questions/0219-household-shrines-yashikigami.html: the household shrine stood at a corner of the plot, northwest, northeast or southwest; the 14 ft is ours
pub const CORNER_FT: f64 = 14.0;

/// The persimmon's crown radius, its trunk box, its crown's pad off a roof, its paces out and its dooryard (feet).
///
/// Research:
///     persimmon crown - research/questions/0046-fruit-trees-in-the-farmyard-persimmon-chestnut-and-plum-kaki.html: 11.5 ft radius, a full-grown 23 ft crown
///     crown over no roof - CONVENTION: the crown kept off every roof so the building stays visible
///     within the dooryard - research/questions/0046-fruit-trees-in-the-farmyard-persimmon-chestnut-and-plum-kaki.drawing.html: paced out no farther than 30 ft, else none
///     its trunk gap - GUESS: searched, the record silent (feature 417 T38, 2026-10-25) - 2 (trunk kept 2 ft clear of every part)
pub const PERSIMMON: (f64, f64, f64, (f64, f64), f64) = (11.5, 4.0, 0.6, (10.0, 20.0), 30.0);

/// The margin a persimmon's seat keeps stricter than the map's shade check (feet).
pub const SHADE_MARGIN_FT: f64 = 2.0;

/// The privy's sizes, the Kakimochi table's sixteen, equally likely (feet, along its wall by out from it).
///
/// Research:
///     privy sizes - research/questions/0047-farm-privies-and-their-night-soil-benjo.drawing.html: the Kakimochi table's sixteen, equally likely
pub const PRIVY_SIZES_FT: [(f64, f64); 16] = [
    (27.0, 15.0),
    (6.0, 5.0),
    (12.0, 6.0),
    (18.0, 12.0),
    (15.0, 12.0),
    (15.0, 9.0),
    (24.0, 12.0),
    (24.0, 12.0),
    (5.0, 5.0),
    (24.0, 12.0),
    (18.0, 12.0),
    (15.0, 9.0),
    (9.0, 6.0),
    (24.0, 12.0),
    (24.0, 12.0),
    (6.0, 6.0),
];

/// The other kinds' sizes (feet).
///
/// Research:
///     other fixtures' sizes - research/questions/0028-the-farmstead-and-what-stood-on-it-yashiki.drawing.html: the wood shed 24 x 12 ft
///     manure heap size - research/questions/0042-manure-heaps-and-compost-kyuhi.drawing.html: 8 x 6 ft
///     manure pit size - research/questions/0042-manure-heaps-and-compost-kyuhi.html: 3.5 ft, inside the night-soil jar's mouth of about 3-5 ft
///     coop size - research/questions/0045-chickens-and-chicken-coops.drawing.html: 5 x 5 ft
///     shrine size - research/questions/0219-household-shrines-yashikigami.drawing.html: 6 x 6 ft, larger than life
///     household grave - research/questions/0236-where-a-village-buries-its-dead-its-own-ground-the-temple-yard-the-fields-or-the-home-plot.html: a few stones on a small cleared patch, 8 x 6 ft at the plot's scale
pub const SIZES_FT: [(Kind, (f64, f64)); 5] = [
    (Kind::Woodpile, (24.0, 12.0)),
    (Kind::Manure, (8.0, 6.0)),
    (Kind::Coop, (5.0, 5.0)),
    (Kind::Shrine, (6.0, 6.0)),
    (Kind::Grave, (8.0, 6.0)),
];

/// The manure pit's side (feet).
pub const PIT_FT: f64 = 3.5;

/// A privy's attested places on a hamlet farm.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Place {
    /// By the stable.
    Stable,
    /// In the yard off the back wall.
    Yard,
    /// In the front yard.
    Front,
    /// By the barn - none on a hamlet, which draws no barn.
    Barn,
}

/// The bath room's three attested walls.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Wall {
    /// Beside the main door, the front wall.
    MainDoor,
    /// At the far end of the stable wing, the west end wall.
    StableEnd,
    /// Joined to the floored rooms, the east end wall.
    FlooredRooms,
}

/// The hamlet's fixture forms, rolled once a map.
///
/// Research:
///     privy seat weights - research/questions/0047-farm-privies-and-their-night-soil-benjo.drawing.html: stable 35, yard 30, front 20, barn 15
///     bath room beyond the stable wing - research/questions/0044-baths-on-the-farm-furo.html: most baths there, 17 of 21 at Shimohasuda and 12 of 15 at Ukiya, so 0.8
///     persimmon front share - research/questions/0046-fruit-trees-in-the-farmyard-persimmon-chestnut-and-plum-kaki.drawing.html: 0.7 by default
///     manure form - research/questions/0042-manure-heaps-and-compost-kyuhi.drawing.html: heap by default, or pit
///     retirement house gaps - GUESS research/questions/0028-the-farmstead-and-what-stood-on-it-yashiki.drawing.html: no page gives how far from the main house it stood; 6 or 12 ft off the house
#[derive(Debug)]
pub struct Forms {
    /// The privy's places and their weights, in the page's order.
    pub privy_weights: Vec<(Place, f64)>,
    /// The share of bath rooms beyond the stable wing, and joined to the floored rooms.
    pub bath_shares: (f64, f64),
    /// The share of persimmons in front of the house.
    pub persimmon_front: f64,
    /// Whether the manure is kept in a pit.
    pub manure_pit: bool,
    /// The retirement house's size (feet).
    pub retirement_ft: (f64, f64),
    /// The retirement house's gaps off the house (feet).
    pub retirement_gaps: Vec<f64>,
}

impl Default for Forms {
    fn default() -> Self {
        Self {
            privy_weights: vec![
                (Place::Stable, 0.35),
                (Place::Yard, 0.30),
                (Place::Front, 0.20),
                (Place::Barn, 0.15),
            ],
            bath_shares: (0.8, 0.03),
            persimmon_front: 0.7,
            manure_pit: false,
            retirement_ft: (18.0, 15.0),
            retirement_gaps: vec![6.0, 12.0],
        }
    }
}

/// A fixture kind whose rule found no seat: the layout is not the household's.
#[derive(Debug, PartialEq, Eq)]
pub struct Unlaid(pub String);

/// A kind's size in feet, along its wall by out from it: the privy one of the sixteen and the bath room's length rolled off the
/// household's roll, every other kind its one size.
///
/// Research:
///     its salts, guards and sentinels - NONE: they decide nothing about the place - 101.3 and 104.3 (roll salts)
#[must_use]
#[expect(
    clippy::cast_possible_truncation,
    clippy::cast_sign_loss,
    reason = "an index into the sixteen from a roll in [0, 1)"
)]
pub fn size_ft(kind: Kind, forms: &Forms, roll: &dyn Fn(f64) -> f64) -> (f64, f64) {
    match kind {
        Kind::Privy => PRIVY_SIZES_FT[(roll(101.3) * 16.0) as usize % 16],
        Kind::Bath => {
            let (d, (lo, hi)) = BATH_FT;
            ((lo + (hi - lo) * roll(104.3)).round(), d)
        }
        Kind::Manure if forms.manure_pit => (PIT_FT, PIT_FT),
        Kind::Persimmon => (PERSIMMON.0 * 2.0, PERSIMMON.0 * 2.0),
        Kind::Retirement => forms.retirement_ft,
        _ => SIZES_FT
            .iter()
            .find(|(k, _)| *k == kind)
            .map_or((6.0, 6.0), |(_, s)| *s),
    }
}

/// Does `r` stand clear of every rect in `taken` by `gap` - apart by the two half-sizes and the gap on one axis at least?
#[must_use]
pub fn clears(r: Rect, taken: &[Rect], gap: f64, tests: &mut u64) -> bool {
    taken.iter().all(|t| {
        *tests += 1;
        (r.0 - t.0).abs() >= (r.2 + t.2) / 2.0 + gap || (r.1 - t.1).abs() >= (r.3 + t.3) / 2.0 + gap
    })
}

/// Does `r` stand with its far corner no more than `reach` from `house`'s walls?
///
/// Research:
///     the privy's reach - research/questions/0047-farm-privies-and-their-night-soil-benjo.drawing.html: no more than 48 ft from its house
#[must_use]
pub fn within_reach_of(r: Rect, house: Rect, reach: f64) -> bool {
    let gx = ((r.0 - house.0).abs() + r.2 / 2.0 - house.2 / 2.0).max(0.0);
    let gy = ((r.1 - house.1).abs() + r.3 / 2.0 - house.3 / 2.0).max(0.0);
    gx * gx + gy * gy <= reach * reach
}

/// Does a seat stand against a wall of `rects` - its edge within `g` (plus `tol`) of one, overlapping it along that wall?
///
/// Research:
///     its salts, guards and sentinels - NONE: they decide nothing about the place - 1.5 (slack in the "stands against a wall" test)
#[must_use]
pub fn against_a_wall(seat: Rect, rects: &[Rect], g: f64, tol: f64) -> bool {
    rects.iter().any(|r| {
        let gx = (seat.0 - r.0).abs() - (seat.2 + r.2) / 2.0;
        let gy = (seat.1 - r.1).abs() - (seat.3 + r.3) / 2.0;
        (gx <= g + tol && gy < 0.0) || (gy <= g + tol && gx < 0.0)
    })
}

/// Offsets along a wall from its middle out, `step` apart, and its two ends.
#[must_use]
#[expect(
    clippy::cast_possible_truncation,
    clippy::cast_precision_loss,
    reason = "a wall's few dozen steps"
)]
pub fn along(half: f64, step: f64) -> Vec<f64> {
    if half <= 0.0 {
        return vec![0.0];
    }
    let n = (half / step).floor() as i64;
    let mut ks: Vec<i64> = (-n..=n).collect();
    ks.sort_by_key(|k| k.abs());
    let mut out: Vec<f64> = ks.iter().map(|&k| k as f64 * step).collect();
    if (n as f64) * step < half {
        out.extend([-half, half]);
    }
    out
}

/// Every place along the outside of each rect's four walls, `off` out from it, `step` apart and at each wall's ends: a seat `w`
/// along a wall and `d` out from it, the back wall first, then the front, then the flanks (turned to lie along them).
#[must_use]
pub fn wall_places(rects: &[Rect], w: f64, d: f64, off: f64, step: f64) -> Vec<Rect> {
    let mut out = Vec::new();
    for &(rx, ry, rw, rh) in rects {
        for sy in [-1.0, 1.0] {
            out.extend(
                along((rw + w) / 2.0 - 1.0, step)
                    .into_iter()
                    .map(|u| (rx + u, ry + sy * (rh / 2.0 + off + d / 2.0), w, d)),
            );
        }
        for sx in [-1.0, 1.0] {
            out.extend(
                along((rh + w) / 2.0 - 1.0, step)
                    .into_iter()
                    .map(|u| (rx + sx * (rw / 2.0 + off + d / 2.0), ry + u, d, w)),
            );
        }
    }
    out
}

/// The seats stepped `step` further from the house's center, `n` times, each along its own bearing from the center.
#[must_use]
#[expect(clippy::cast_precision_loss, reason = "a pace count of a few dozen")]
pub fn outward(seats: &[Rect], step: f64, n: usize) -> Vec<Rect> {
    (1..=n)
        .flat_map(|k| {
            seats.iter().map(move |&(lx, ly, w, d)| {
                let r = lx.hypot(ly);
                let r = if r > 0.0 { r } else { 1.0 };
                let s = step * k as f64;
                (lx + lx / r * s, ly + ly / r * s, w, d)
            })
        })
        .collect()
}

/// `seat` slid along its wall toward its own end, `step` at a time, `n` times, only while the whole seat stands along the wall.
///
/// Research:
///     slid only while along its wall - research/questions/0047-farm-privies-and-their-night-soil-benjo.drawing.html: "while the whole privy still stands along the wall"
///     slid toward its own end only - GUESS: no source could speak to it, a value of ours (feature 417 T36 pass P1, 2026-10-25); never back across the house's middle, where the door's way out leaves
#[must_use]
#[expect(clippy::cast_precision_loss, reason = "a pace count of a few dozen")]
pub fn along_its_wall(seat: Rect, step: f64, n: usize, half_wall: f64) -> Vec<Rect> {
    let (x, y, w, d) = seat;
    let sign = if x >= 0.0 { 1.0 } else { -1.0 };
    (1..=n)
        .map(|k| x + sign * step * k as f64)
        .take_while(|nx| nx.abs() + w / 2.0 <= half_wall + 1e-9)
        .map(|nx| (nx, y, w, d))
        .collect()
}

/// The index `u` falls on across the cumulative `weights` (the last past their sum).
#[must_use]
pub fn weighted(weights: &[f64], u: f64) -> usize {
    let mut acc = 0.0;
    weights
        .iter()
        .position(|w| {
            acc += w;
            u < acc
        })
        .unwrap_or(weights.len() - 1)
}

/// The privy's sun-side seats, SE to S (112.5 to 202.5 degrees, every 7.5), at each of `radii`, nearest first.
///
/// Research:
///     sunny-side sector - research/questions/0047-farm-privies-and-their-night-soil-benjo.drawing.html: bearings 112.5 to 202.5 degrees, nearest first
#[must_use]
pub fn sun_sector(w: f64, d: f64, radii: &[f64]) -> Vec<Rect> {
    radii
        .iter()
        .flat_map(|&rr| {
            (0..13).map(move |k| {
                let b = (112.5 + 7.5 * f64::from(k)).to_radians();
                (rr * b.sin(), -rr * b.cos(), w, d)
            })
        })
        .collect()
}

/// The recorded seats of one kind in the house frame, first choice first.
///
/// Research:
///     privy seats - research/questions/0047-farm-privies-and-their-night-soil-benjo.drawing.html: the sun-side sector on 72.7%, else the attested places a hamlet farm has - the yard, the front, by the stable; not the barn while a hamlet draws none
///     privy by the stable - research/questions/0047-farm-privies-and-their-night-soil-benjo.drawing.html: by the stable, at the house's stable end against the front wall's clear strip
///     manure beyond the privy - research/questions/0042-manure-heaps-and-compost-kyuhi.drawing.html: on the side of the privy away from the house, along the line from its center; jittered a few feet; behind or beside the house where there is no privy
///     manure heap fallback spots - GUESS research/questions/0042-manure-heaps-and-compost-kyuhi.drawing.html: beside the privy at 1.1 and 1.9 of its width, then 10 ft further out; with no privy, at 0.3 of the house's width and depth
///     its figures guessed on 0042 - GUESS research/questions/0042-manure-heaps-and-compost-kyuhi.drawing.html: 9 (heap's distance from the privy varies over a 9 ft spread)
///     retirement house - research/questions/0047-farm-privies-and-their-night-soil-benjo.html: storehouses and retirement houses stood to the southwest and west of the house (Wang and Ochiai, Meiji)
///     coop seats - research/questions/0045-chickens-and-chicken-coops.drawing.html: the east flank, the back wall or the west flank, rolled
///     wood shed seats - GUESS research/questions/0043-firewood-stacks-and-sheds-kigoya.drawing.html: off the back wall and the flanks
///     shrine corner - research/questions/0219-household-shrines-yashikigami.drawing.html: NW, NE or SW of the house
///     household grave corner - research/questions/0236-where-a-village-buries-its-dead-its-own-ground-the-temple-yard-the-fields-or-the-home-plot.html: SE or NW of the house, then the other two corners
///     seat positions along each wall - GUESS: no source could speak to it, a value of ours (feature 417 T36 pass P1, 2026-10-25); privy 0.3 / 0.40 / -0.35 hw, coop 0.34 hw spread and 0.3 hh, wood shed 0.25 hw and 0.1 hh
///     its salts, guards and sentinels - NONE: they decide nothing about the place - 102.4 (salt); 105.9 (salt); 105.5 (salt)
#[must_use]
#[expect(
    clippy::too_many_arguments,
    clippy::too_many_lines,
    reason = "one table a kind, as the seating keeps it"
)]
#[expect(
    clippy::cast_possible_truncation,
    clippy::cast_sign_loss,
    reason = "a roll's index into a few seats"
)]
pub fn seats(
    kind: Kind,
    hw: f64,
    hh: f64,
    w: f64,
    d: f64,
    privy: Option<Rect>,
    roll: &dyn Fn(f64) -> f64,
    u: f64,
    forms: &Forms,
) -> Vec<Rect> {
    let g = WALL_GAP_FT;
    match kind {
        Kind::Privy => {
            let at = |p: Place| match p {
                Place::Yard => (hw * 0.3, -(hh / 2.0 + g + PRIVY_STEPS_FT.0 + d / 2.0), w, d),
                Place::Front => (hw * 0.40, hh / 2.0 + g + PRIVY_STEPS_FT.1 + d / 2.0, w, d),
                Place::Stable | Place::Barn => (-hw * 0.35, hh / 2.0 + g + d / 2.0, w, d),
            };
            let weights: Vec<(Place, f64)> = forms
                .privy_weights
                .iter()
                .copied()
                .filter(|(p, _)| *p != Place::Barn)
                .collect();
            let ws: Vec<f64> = weights.iter().map(|(_, p)| *p).collect();
            let first = weights[weighted(&ws, u * ws.iter().sum::<f64>())].0;
            let mut attested = vec![at(first)];
            attested.extend(
                weights
                    .iter()
                    .filter(|(p, _)| *p != first)
                    .map(|(p, _)| at(*p)),
            );
            if roll(salt(kind) + 0.25) >= PRIVY_SUN.2 {
                return attested;
            }
            let radii: Vec<f64> = (0..=7)
                .map(|k| PRIVY_SUN.0 + 4.0 * f64::from(k))
                .filter(|r| *r <= PRIVY_SUN.1)
                .collect();
            let mut out = sun_sector(w, d, &radii);
            out.extend(attested);
            out
        }
        Kind::Manure => {
            let Some(p) = privy else {
                return vec![
                    (hw * 0.3, -(hh / 2.0 + g + d / 2.0), w, d),
                    (hw / 2.0 + g + d / 2.0, hh * 0.3, d, w),
                ];
            };
            let n = p.0.hypot(p.1);
            let (ux, uy) = if n > 1e-9 {
                (p.0 / n, p.1 / n)
            } else {
                (0.0, 1.0)
            };
            let (sx, sy) = (-uy, ux);
            let pout = ux.abs() * p.2 / 2.0
                + uy.abs() * p.3 / 2.0
                + g
                + ux.abs() * w / 2.0
                + uy.abs() * d / 2.0
                + 9.0 * (roll(102.4) - 0.5);
            let at = |al: f64, ac: f64| (p.0 + ux * al + sx * ac, p.1 + uy * al + sy * ac, w, d);
            vec![
                at(pout, 0.0),
                at(0.0, w * 1.1),
                at(0.0, -w * 1.1),
                at(pout, w * 1.1),
                at(pout, -w * 1.1),
                at(pout + 10.0, 0.0),
                at(0.0, w * 1.9),
                at(0.0, -w * 1.9),
            ]
        }
        Kind::Retirement => {
            let sides = [(0.0, -1.0), (1.0, 0.0), (-1.0, 0.0)];
            let k = (u * 3.0) as usize % 3;
            let mut out = Vec::new();
            for &gap in &forms.retirement_gaps {
                for &(sx, sy) in sides[k..].iter().chain(&sides[..k]) {
                    out.push(if sy == 0.0 {
                        (sx * (hw / 2.0 + gap + d / 2.0), 0.0, d, w)
                    } else {
                        (0.0, -(hh / 2.0 + gap + d / 2.0), w, d)
                    });
                }
            }
            out
        }
        Kind::Coop => {
            let cjx = hw * 0.34 * (roll(105.9) - 0.5) * 2.0;
            let s = [
                (hw / 2.0 + g + d / 2.0, hh * 0.3, d, w),
                (cjx, -(hh / 2.0 + g + d / 2.0), w, d),
                (-(hw / 2.0 + g + d / 2.0), -hh * 0.3, d, w),
            ];
            let k = (roll(105.5) * 3.0) as usize % 3;
            s[k..].iter().chain(&s[..k]).copied().collect()
        }
        Kind::Woodpile => {
            let (st, back) = (WOODSHED_STEP_FT, -(hh / 2.0 + g + d / 2.0));
            vec![
                (-hw * 0.25, back - st, w, d),
                (hw * 0.25, back - st, w, d),
                (hw / 2.0 + g + st + d / 2.0, hh * 0.1, d, w),
                (-(hw / 2.0 + g + st + d / 2.0), hh * 0.1, d, w),
            ]
        }
        _ => {
            let off = CORNER_FT;
            let corner = |c: (f64, f64)| (c.0 * (hw / 2.0 + off), c.1 * (hh / 2.0 + off), w, d);
            let (nw, ne, sw, se) = ((-1.0, -1.0), (1.0, -1.0), (-1.0, 1.0), (1.0, 1.0));
            let table: Vec<((f64, f64), f64)> = if kind == Kind::Grave {
                vec![(se, 0.5), (nw, 0.5)]
            } else {
                vec![(nw, 0.45), (ne, 0.35), (sw, 0.20)]
            };
            let ws: Vec<f64> = table.iter().map(|(_, p)| *p).collect();
            let first = table[weighted(&ws, u)].0;
            let mut out = vec![corner(first)];
            out.extend(
                table
                    .iter()
                    .filter(|(c, _)| *c != first)
                    .map(|(c, _)| corner(*c)),
            );
            if kind == Kind::Grave {
                out.extend([corner(ne), corner(sw)]);
            }
            out
        }
    }
}

/// The wall a house's bath room is joined to, from its roll: beyond the stable wing, joined to the floored rooms, else by the
/// main door.
///
/// Research:
///     the three walls rolled - research/questions/0044-baths-on-the-farm-furo.html: most beyond the stable, a few at the floored rooms
///     the rest by the main door - research/questions/0044-baths-on-the-farm-furo.drawing.html: this project's choice, where the earliest registers' baths stood
#[must_use]
pub fn bath_wall(u: f64, forms: &Forms) -> Wall {
    let (stable, floored) = forms.bath_shares;
    if u < stable {
        Wall::StableEnd
    } else if u < stable + floored {
        Wall::FlooredRooms
    } else {
        Wall::MainDoor
    }
}

/// The bath room's recorded seats, `first`'s wall first then the others in the table's order, each with its wall: beside the
/// main door (either side of the door and past the yard's sides), and the stable and floored ends at the middle and quarters -
/// then every place along the three walls, `WALL_SLIDE_FT` apart.
///
/// Research:
///     three attested walls - research/questions/0044-baths-on-the-farm-furo.drawing.html: the rolled wall first
///     bath room seat fallback - GUESS: where the rolled wall has no room the other attested walls are tried in table order; 0044 gives each house's place and its share but no fallback
///     places along each wall - research/questions/0044-baths-on-the-farm-furo.html: the bath stood by the main door, at the stable wing's far end or by the floored rooms; the 0.22 is ours
///     its wall points - GUESS: searched, the record silent (feature 417 T38, 2026-10-25) - 0.25 (the bath room's quarter points on the floored-rooms and stable-end walls)
///     its bath set-out - GUESS: searched, the record silent (feature 417 T38, 2026-10-25) - 3 (bath room 3 ft past the yard's side on the front wall)
///     anywhere along the walls - GUESS: the spot along a wall slid toward either end, and the fall to the other walls in table order; 0044 gives the walls, not the spot
#[must_use]
pub fn bath_seats(
    first: Wall,
    hw: f64,
    hh: f64,
    w: f64,
    d: f64,
    yard: Option<(f64, f64)>,
) -> Vec<(Rect, Wall)> {
    let (front, side) = (hh / 2.0 + d / 2.0, hw / 2.0 + d / 2.0);
    let order = [Wall::MainDoor, Wall::StableEnd, Wall::FlooredRooms];
    let walls: Vec<Wall> = std::iter::once(first)
        .chain(order.into_iter().filter(|k| *k != first))
        .collect();
    let recorded = |k: Wall| -> Vec<Rect> {
        match k {
            Wall::MainDoor => {
                let mut v = vec![
                    (hw * 0.22 + w / 2.0, front, w, d),
                    (-(hw * 0.22 + w / 2.0), front, w, d),
                ];
                if let Some((yx, yhalf)) = yard {
                    v.extend(
                        [1.0, -1.0]
                            .iter()
                            .map(|sx| yx + sx * (yhalf + w / 2.0 + 3.0))
                            .filter(|x| x.abs() + w / 2.0 <= hw / 2.0)
                            .map(|x| (x, front, w, d)),
                    );
                }
                v
            }
            Wall::StableEnd => vec![
                (-side, 0.0, d, w),
                (-side, -hh * 0.25, d, w),
                (-side, hh * 0.25, d, w),
            ],
            Wall::FlooredRooms => vec![
                (side, 0.0, d, w),
                (side, -hh * 0.25, d, w),
                (side, hh * 0.25, d, w),
            ],
        }
    };
    let slides = |k: Wall| -> Vec<Rect> {
        match k {
            Wall::MainDoor => along(((hw - w) / 2.0).max(0.0), WALL_SLIDE_FT)
                .into_iter()
                .map(|u| (u, front, w, d))
                .collect(),
            Wall::StableEnd => along(((hh - w) / 2.0).max(0.0), WALL_SLIDE_FT)
                .into_iter()
                .map(|u| (-side, u, d, w))
                .collect(),
            Wall::FlooredRooms => along(((hh - w) / 2.0).max(0.0), WALL_SLIDE_FT)
                .into_iter()
                .map(|u| (side, u, d, w))
                .collect(),
        }
    };
    let mut out: Vec<(Rect, Wall)> = walls
        .iter()
        .flat_map(|&k| recorded(k).into_iter().map(move |q| (q, k)))
        .collect();
    out.extend(
        walls
            .iter()
            .flat_map(|&k| slides(k).into_iter().map(move |q| (q, k))),
    );
    out
}

/// Does any part of `seat` stand past the front wall, into the dooryard?
///
/// Research:
///     the front yard - GUESS research/questions/0043-firewood-stacks-and-sheds-kigoya.drawing.html: never the front yard
#[must_use]
pub fn forward_of_front(seat: Rect, hh: f64) -> bool {
    seat.1 + seat.3 / 2.0 > hh + 1e-6
}

/// The wood shed's rule: a ken off a wall of its house - clear of every wall of the steading by the gap and the ken, against the
/// house's own wall at no tolerance, and no part forward of the front wall.
///
/// Research:
///     wood shed a ken off a wall - GUESS research/questions/0043-firewood-stacks-and-sheds-kigoya.drawing.html: never out across the dooryard
///     a ken off the house, clear of the kura - GUESS research/questions/0043-firewood-stacks-and-sheds-kigoya.drawing.html: a short step off a house wall, and the kura's wall kept as far, a building of its own
#[must_use]
pub fn shed_off_a_wall(seat: Rect, walls: &[Rect], tests: &mut u64) -> bool {
    let off = WALL_GAP_FT + WOODSHED_STEP_FT;
    clears(seat, walls, off - 1e-6, tests)
        && against_a_wall(seat, &walls[..1], off + 1e-6, 0.0)
        && !forward_of_front(seat, walls[0].3 / 2.0)
}

/// Does a crown of radius `r` at (x, y) keep its edge within `reach` of the house's walls?
#[must_use]
pub fn in_dooryard(x: f64, y: f64, r: f64, hw: f64, hh: f64, reach: f64) -> bool {
    let (dx, dy) = ((x.abs() - hw / 2.0).max(0.0), (y.abs() - hh / 2.0).max(0.0));
    dx.hypot(dy) - r <= reach
}

/// Does a crown at (x, y) of radius `r` meet a plot's sun ground - the plot widened `reach` east and west and deepened `reach`
/// south from its north edge - at any of the rakes in `turns`, the crown and the plots turned together about the house's center?
///
/// Research:
///     sun ground as a rectangle - research/questions/0038-sunlight-and-shade-on-the-farm.drawing.html: from the plot's north edge, widened east and west and deepened south by the reach
///     persimmon out of the plots' sun - research/questions/0038-sunlight-and-shade-on-the-farm.drawing.html
#[must_use]
pub fn shades(x: f64, y: f64, r: f64, ground: &[Rect], reach: f64, turns: &[f64]) -> bool {
    turns.iter().any(|t| {
        let th = t.to_radians();
        let (c, s) = (th.cos(), th.sin());
        let (ac, as_) = (c.abs(), s.abs());
        let (cx, cy) = (x * c - y * s, x * s + y * c);
        ground.iter().any(|q| {
            let (qx, qy) = (q.0 * c - q.1 * s, q.0 * s + q.1 * c);
            let (qw, qh) = (q.2 * ac + q.3 * as_, q.2 * as_ + q.3 * ac);
            let (x0, x1, y0, y1) = (
                qx - qw / 2.0 - reach,
                qx + qw / 2.0 + reach,
                qy - qh / 2.0,
                qy + qh / 2.0 + reach,
            );
            let (dx, dy) = (cx - cx.clamp(x0, x1), cy - cy.clamp(y0, y1));
            dx * dx + dy * dy < r * r
        })
    })
}

/// The fixtures laid, each its kind and its box, and the wall the bath room took.
pub type Laid = (Vec<(Kind, Rect)>, Option<Wall>);

/// What the house frame holds for the fixtures to be laid beside.
pub struct Frame<'a> {
    /// The house's width and depth.
    pub house: (f64, f64),
    /// The built parts - the house first, then its kura, byre and other buildings.
    pub roofs: &'a [Rect],
    /// The open parts whose sun a persimmon keeps out of - the yard and the beds.
    pub ground: &'a [Rect],
    /// The threshing yard.
    pub yard: Option<Rect>,
    /// Whether the house keeps its kura on its north wall.
    pub kura: bool,
    /// How far a persimmon's crown keeps off the plots' sun, and the rakes it is asked at.
    pub shade: (f64, &'a [f64]),
    /// The ground no fixture but the bath room stands on (a grove farm's way in and its door's room).
    pub keep: &'a [Rect],
}

/// Each of `kinds` laid beside the parts already laid, in the order of `ORDER`, the box as laid; the bath room's wall where one
/// is laid. Refused (`Unlaid`, naming the kind) for a bath room with no place on the house's three walls, a wood shed with no place
/// a ken off a wall of its house, a privy with no seat within 48 ft of it, or any other kind with no seat beside its house; a
/// persimmon with no seat in the dooryard is simply not kept.
///
/// Research:
///     no seat, no persimmon - research/questions/0046-fruit-trees-in-the-farmyard-persimmon-chestnut-and-plum-kaki.drawing.html: the farm keeps none
///     no fixture on the way in - research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.drawing.html: the way in by the open front, through the ring's break - every kind but the bath room kept off `keep`
///     wood shed's walls - GUESS research/questions/0043-firewood-stacks-and-sheds-kigoya.drawing.html: the house's walls, a short step off the house - never the byre's or the retirement house's
///     the kura's walls too - GUESS: the house's storehouse annex counts as a wall of the house for the shed
///     persimmon front or behind - research/questions/0046-fruit-trees-in-the-farmyard-persimmon-chestnut-and-plum-kaki.drawing.html: in front of the house or behind it, rolled per house
///     bath room joined - research/questions/0044-baths-on-the-farm-furo.drawing.html: refused rather than walked out
///     its salts, guards and sentinels - NONE: they decide nothing about the place - 0.25 (salt offset for the bath-wall roll); 0.5 (salt offset for the place roll)
///
/// # Errors
///
/// `Unlaid` names the kind whose rule found no seat.
#[expect(
    clippy::too_many_lines,
    reason = "one arm a kind's rule, as the seating lays them"
)]
pub fn lay(
    kinds: &[Kind],
    fr: &Frame,
    roll: &dyn Fn(f64) -> f64,
    forms: &Forms,
    tests: &mut u64,
) -> Result<Laid, Unlaid> {
    let (hw, hh) = fr.house;
    let g = WALL_GAP_FT;
    let mut taken: Vec<Rect> = fr
        .roofs
        .iter()
        .chain(fr.ground)
        .chain(fr.keep)
        .copied()
        .collect();
    let mut built: Vec<Rect> = fr.roofs.to_vec();
    let mut laid: Vec<(Kind, Rect)> = Vec::new();
    let mut bath = None;
    for kind in ORDER.into_iter().filter(|k| kinds.contains(k)) {
        let (w, d) = size_ft(kind, forms, roll);
        let u = roll(salt(kind) + 0.5);
        let seat = match kind {
            Kind::Persimmon => {
                let (r, trunk, pad, (s1, s2), dooryard) = PERSIMMON;
                let reach = (hw / 2.0).hypot(hh / 2.0) + r + pad + 1.0;
                let front = [
                    (reach * 0.75, reach * 0.75),
                    (-reach * 0.75, reach * 0.75),
                    (0.0, reach),
                ];
                let back = [
                    (reach * 0.75, -reach * 0.75),
                    (-reach * 0.75, -reach * 0.75),
                    (0.0, -reach),
                ];
                let ring: Vec<(f64, f64)> = if u < forms.persimmon_front {
                    front.iter().chain(&back).copied().collect()
                } else {
                    back.iter().chain(&front).copied().collect()
                };
                let mut steps = vec![s1, s2];
                steps.extend(
                    (1..=STEP.1)
                        .map(|k| STEP.0 * f64::from(u32::try_from(k).unwrap_or(u32::MAX)) + s2),
                );
                let paced = steps.iter().flat_map(|st| {
                    ring.iter().map(move |&(lx, ly)| {
                        (lx * (reach + st) / reach, ly * (reach + st) / reach)
                    })
                });
                let shade = r + SHADE_MARGIN_FT;
                let found = ring.iter().copied().chain(paced).find(|&(lx, ly)| {
                    *tests += 1;
                    in_dooryard(lx, ly, r, hw, hh, dooryard)
                        && clears((lx, ly, trunk, trunk), &taken, 2.0, tests)
                        && clears((lx, ly, 2.0 * r, 2.0 * r), &built, pad, tests)
                        && (fr.shade.0 <= 0.0
                            || !shades(lx, ly, shade, fr.ground, fr.shade.0, fr.shade.1))
                });
                let Some((lx, ly)) = found else {
                    continue;
                };
                laid.push((kind, (lx, ly, 2.0 * r, 2.0 * r)));
                taken.push((lx, ly, trunk, trunk));
                continue;
            }
            Kind::Woodpile => {
                let mut walls = vec![(0.0, 0.0, hw, hh)];
                if fr.kura {
                    walls.push(kura(hw, hh, true));
                }
                let recorded = seats(kind, hw, hh, w, d, None, roll, 0.0, forms);
                let along_walls =
                    wall_places(&walls[..1], w, d, g + WOODSHED_STEP_FT, WALL_SLIDE_FT)
                        .into_iter()
                        .filter(|q| !forward_of_front(*q, hh / 2.0));
                recorded
                    .into_iter()
                    .chain(along_walls)
                    .find(|q| shed_off_a_wall(*q, &walls, tests) && clears(*q, &taken, g, tests))
                    .ok_or_else(|| {
                        Unlaid(
                            "a wood shed found no place a ken off any wall of its steading"
                                .to_owned(),
                        )
                    })?
            }
            Kind::Bath => {
                let wall = bath_wall(roll(salt(kind) + 0.25), forms);
                let house = fr.roofs[0];
                let others: Vec<Rect> = taken
                    .iter()
                    .copied()
                    .filter(|t| *t != house && !fr.keep.contains(t))
                    .collect();
                let (q, k) = bath_seats(wall, hw, hh, w, d, fr.yard.map(|y| (y.0, y.2 / 2.0)))
                    .into_iter()
                    .find(|(q, _)| clears(*q, &[house], -1e-6, tests) && clears(*q, &others, g, tests))
                    .ok_or_else(|| Unlaid("a bath room found no place on the house's front wall or either end wall".to_owned()))?;
                bath = Some(k);
                q
            }
            _ => {
                let privy = laid
                    .iter()
                    .find(|(k, _)| *k == Kind::Privy)
                    .map(|(_, r)| *r);
                let recorded = seats(kind, hw, hh, w, d, privy, roll, u, forms);
                let offered: Vec<Rect> = if kind == Kind::Privy {
                    let places = forms
                        .privy_weights
                        .iter()
                        .filter(|(p, _)| *p != Place::Barn)
                        .count();
                    let sun = recorded.len() - places;
                    let k = sun.max(1);
                    let mut v: Vec<Rect> = recorded[..k].to_vec();
                    if k == 1 {
                        v.extend(along_its_wall(recorded[0], STEP.0, STEP.1, hw / 2.0));
                    }
                    v.extend_from_slice(&recorded[k..]);
                    v.extend(outward(&recorded, STEP.0, STEP.1));
                    let house = fr.roofs[0];
                    v.into_iter()
                        .filter(|q| within_reach_of(*q, house, PRIVY_SUN.1))
                        .collect()
                } else {
                    let mut v = recorded.clone();
                    v.extend(outward(&recorded, STEP.0, STEP.1));
                    v
                };
                offered
                    .into_iter()
                    .find(|q| clears(*q, &taken, g, tests))
                    .ok_or_else(|| {
                        Unlaid(if kind == Kind::Privy {
                            "a privy found no place within 48 ft of its house".to_owned()
                        } else {
                            format!("a {kind:?} found no place beside its house")
                        })
                    })?
            }
        };
        laid.push((kind, seat));
        taken.push(seat);
        built.push(seat);
    }
    Ok((laid, bath))
}
