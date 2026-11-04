//! A homestead's layout (feature 444 T30): its rolled parts around the house's center, unturned - the yard before the south wall, the
//! kitchen garden on its side, split into two beds in about one household in four - each roll keyed on the seat the household is
//! sought from (`hjit`), so a layout is the household's wherever the seat lands.
//!
//! Research:
//!     the homestead's layout - NONE: the layout's machinery; each part's rule is claimed at its constant

use crate::field::fan::Pt;

/// A rectangle: its center, width and height (feet).
pub type Rect = (f64, f64, f64, f64);

/// A deterministic draw in [0, 1) from a position and a salt: each homestead's parts jittered with no draw from a shared stream, so
/// no other placement ripples - the hash the Python seating keyed its rolls on, kept so a seat rolls as it did.
///
/// Research:
///     its salts, guards and sentinels - NONE: they decide nothing about the place - 43758.5 (hash constants); 7.373 (hash constants); 12.9898 (hash constants); 4.1414 (hash constants)
#[must_use]
pub fn hjit(x: f64, y: f64, salt: f64) -> f64 {
    let v = (x * 12.9898 + y * 4.1414 + salt * 7.373).sin() * 43_758.545_3;
    v - v.floor()
}

/// The ordinary minka's footprint (feet).
///
/// Research:
///     ordinary minka - research/questions/0038-sunlight-and-shade-on-the-farm.drawing.html: 46 x 28 ft
pub const MINKA_FT: (f64, f64) = (46.0, 28.0);

/// The yard's median area (tsubo).
///
/// Research:
///     yard median - research/questions/0037-threshing-and-drying-yards-at-farmhouses-niwa.drawing.html: 25 tsubo, rice and dry field alike
pub const YARD_MEDIAN_TSUBO: f64 = 25.0;

/// The yard's spread, as the log-normal's sigma.
///
/// Research:
///     yard spread - research/questions/0037-threshing-and-drying-yards-at-farmhouses-niwa.drawing.html: lognormal, sigma 0.40 in log space
pub const YARD_SIGMA_LN: f64 = 0.40;

/// How much of the household's own deviation, in log space, its yard inherits.
///
/// Research:
///     larger household, larger yard - research/questions/0037-threshing-and-drying-yards-at-farmhouses-niwa.drawing.html: the house's log deviation times 2.2
pub const YARD_HOUSE_BETA: f64 = 2.2;

/// The least yard (tsubo): nobody is yardless.
///
/// Research:
///     least yard - research/questions/0037-threshing-and-drying-yards-at-farmhouses-niwa.drawing.html: 8 tsubo
pub const YARD_MIN_TSUBO: f64 = 8.0;

/// A tsubo (square feet).
///
/// Research:
///     a tsubo - NONE: a unit's conversion, 3.306 sq m
pub const TSUBO_FT2: f64 = 35.583;

/// The yard's aspect, wide to deep.
///
/// Research:
///     yard aspect - GUESS: searched, the record silent (feature 417 T36 pass P1, 2026-10-25); 1.45 wide to deep
pub const YARD_ASPECT: f64 = 1.45;

/// The gap between the house and its yard and garden (feet).
///
/// Research:
///     house-to-part gap - GUESS: searched, the record silent (feature 417 T36 pass P3, 2026-10-25); 3 ft between the house and its yard and garden
pub const PART_GAP_FT: f64 = 3.0;

/// The garden's size against the house's, before its jitter, and its cap (feet).
///
/// Research:
///     garden size - research/questions/0039-kitchen-gardens-beside-farmhouses-yashikibatake.drawing.html: 0.48 x 0.85 of the house, jittered up to 1.25x, capped at 44 x 34 ft, under 0039's 1,507
pub const GARDEN: ((f64, f64), f64, (f64, f64)) = ((0.48, 0.85), 0.25, (44.0, 34.0));

/// The share of households that split the garden into two beds, the share of those that flank the house, and the least bed (ft).
///
/// Research:
///     bed split share - GUESS: searched, the record silent (feature 417 T36 pass P3, 2026-10-25); about one household in four splits its plot into two beds
///     bed split forms - GUESS: searched, the record silent (feature 417 T36 pass P3, 2026-10-25) - 0039 has where a bed lay, nothing on splitting one; half flank the house on opposite walls, the rest stacked (south gardens) or side by side; each bed at least 6 ft wide
///     its figures against 0039 - research/questions/0039-kitchen-gardens-beside-farmhouses-yashikibatake.drawing.html: 0.55 (each flanking bed 0.55 of the garden, so the two pass the 1,507 sq ft ceiling) - a departure the code keeps until feature 417 T33
pub const BEDS: (f64, f64, f64, f64) = (0.26, 0.5, 0.55, 6.0);

/// The garden's side of the house: the two south corners and the two walls.
///
/// Research:
///     garden side - research/questions/0038-sunlight-and-shade-on-the-farm.drawing.html: southeast, southwest, east or west of the house
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Side {
    /// Tucked beside the south yard, east.
    SE,
    /// Tucked beside the south yard, west.
    SW,
    /// The east wall, the house's mid-height.
    E,
    /// The west wall, the house's mid-height.
    W,
}

/// The four sides in the order the placer asks them.
pub const SIDES: [Side; 4] = [Side::SE, Side::SW, Side::E, Side::W];

/// The yard's area (square feet) for a house `hw` by `hh` sought at `seat`: the household's deviation from the ordinary minka,
/// damped and amplified, plus a near-normal draw (six positional draws summed, standardized), log-normal about the median.
///
/// Research:
///     yard roll - research/questions/0037-threshing-and-drying-yards-at-farmhouses-niwa.drawing.html: lognormal about the median, the house's deviation inherited, at least 8 tsubo
///     its salts, guards and sentinels - NONE: they decide nothing about the place - 23 (salts); 29 (salts); 31 (salts); 37 (salts); 43 (salts); 47 (salts)
#[must_use]
pub fn yard_area_ft2(seat: Pt, hw: f64, hh: f64) -> f64 {
    let tilt = ((hw * hh).max(1.0) / (MINKA_FT.0 * MINKA_FT.1)).ln() * YARD_HOUSE_BETA;
    let z = ([23.0, 29.0, 31.0, 37.0, 43.0, 47.0]
        .iter()
        .map(|&k| hjit(seat.0, seat.1, k))
        .sum::<f64>()
        - 3.0)
        / 0.5f64.sqrt();
    (YARD_MEDIAN_TSUBO * (tilt + YARD_SIGMA_LN * z).exp()).max(YARD_MIN_TSUBO) * TSUBO_FT2
}

/// The yard's width and depth at its aspect.
#[must_use]
pub fn yard_dims(seat: Pt, hw: f64, hh: f64) -> (f64, f64) {
    let depth = (yard_area_ft2(seat, hw, hh) / YARD_ASPECT).sqrt();
    (depth * YARD_ASPECT, depth)
}

/// The garden's size for a house `hw` by `hh`, jittered at `seat` and capped.
#[must_use]
pub fn garden_size(seat: Pt, hw: f64, hh: f64) -> (f64, f64) {
    let ((fw, fh), jit, (cw, ch)) = GARDEN;
    (
        (fw * hw * (1.0 + hjit(seat.0, seat.1, 3.0) * jit)).min(cw),
        (fh * hh * (1.0 + hjit(seat.0, seat.1, 4.0) * jit)).min(ch),
    )
}

/// The garden's beds on `side`, unturned about the house's center at the origin: one bed, or - in about one household in four -
/// two: flanking the house on opposite walls, stacked (a south garden) or side by side, each bed at least its least width.
///
/// Research:
///     beds on sunny sides - research/questions/0038-sunlight-and-shade-on-the-farm.drawing.html: never the north back
///     its salts, guards and sentinels - NONE: they decide nothing about the place - 8 (jitter salt); 9 (jitter salt); 10 (jitter salt)
#[must_use]
pub fn beds(seat: Pt, hw: f64, hh: f64, side: Side) -> Vec<Rect> {
    let (gw, gh) = garden_size(seat, hw, hh);
    let gap = PART_GAP_FT;
    let (gx, gy) = match side {
        Side::SE => (hw / 2.0 + gap + gw / 2.0, hh / 2.0 + gap + gh / 2.0),
        Side::SW => (-hw / 2.0 - gap - gw / 2.0, hh / 2.0 + gap + gh / 2.0),
        Side::E => (hw / 2.0 + gap + gw / 2.0, 0.0),
        Side::W => (-hw / 2.0 - gap - gw / 2.0, 0.0),
    };
    let (share, flank, part, least) = BEDS;
    if hjit(seat.0, seat.1, 8.0) >= share {
        return vec![(gx, gy, gw, gh)];
    }
    if hjit(seat.0, seat.1, 9.0) < flank && gw * part >= least {
        let pw = gw * part;
        return vec![
            (hw / 2.0 + gap + pw / 2.0, gy, pw, gh),
            (-hw / 2.0 - gap - pw / 2.0, gy, pw, gh),
        ];
    }
    let south = matches!(side, Side::SE | Side::SW);
    if south && hjit(seat.0, seat.1, 10.0) < flank && (gh - gap) / 2.0 >= least {
        let ph = (gh - gap) / 2.0;
        return vec![
            (gx, gy - f64::midpoint(gap, ph), gw, ph),
            (gx, gy + f64::midpoint(gap, ph), gw, ph),
        ];
    }
    if (gw - gap) / 2.0 >= least {
        let pw = (gw - gap) / 2.0;
        return vec![
            (gx - f64::midpoint(gap, pw), gy, pw, gh),
            (gx + f64::midpoint(gap, pw), gy, pw, gh),
        ];
    }
    vec![(gx, gy, gw, gh)]
}

/// The yard before the south wall, unturned about the house's center at the origin.
#[must_use]
pub fn yard(seat: Pt, hw: f64, hh: f64) -> Rect {
    let (yw, yh) = yard_dims(seat, hw, hh);
    (0.0, hh / 2.0 + PART_GAP_FT + yh / 2.0, yw, yh)
}
