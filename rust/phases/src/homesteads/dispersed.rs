//! The dispersed farmstead's layout (feature 444 T30, from `rolling/dispersed.py`, feature 291): the house, its yard and garden,
//! and its own grove on the sides its settlement rolled, laid in one canonical frame - the cold wind from the northwest, the deep
//! bands on the north and west, the yard on the south front, the garden against the east wall - and carried to the map's wind by a
//! symmetry of the square (`grove_sides.bundle_turn`). Pure geometry.
//!
//! Research:
//!     grove sides and depths - research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.drawing.html: deep bands on the two windward sides, a thin band on a third and fourth rolled side, the corners closed
//!     yard on the south front - research/questions/0029-farmhouses-minka.drawing.html, research/questions/0037-threshing-and-drying-yards-at-farmhouses-niwa.drawing.html: the yard before the house's south wall, 3 ft (`gap`) off it
//!     garden placement - research/questions/0038-sunlight-and-shade-on-the-farm.drawing.html: against the east wall, or beside the yard when the map keeps the sun
//!     thin bands clear of the plots' sun - research/questions/0038-sunlight-and-shade-on-the-farm.drawing.html, research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.drawing.html: east band past the garden's reach (`sun_east`, 50 ft), south band past the yard's strip
//!     homestead turned to the map's wind - research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.drawing.html: the canonical northwest frame carried by a symmetry of the square
//!     garden beside the yard when turned - research/questions/0038-sunlight-and-shade-on-the-farm.drawing.html: so it never stands on the house's north or west wall
//!     band cut out of a bed's morning sun - research/questions/0038-sunlight-and-shade-on-the-farm.drawing.html: no crown within 50 ft east of a bed - a band cut back out of the reach, a band whose cut run would be a stub dropped

#![expect(
    clippy::manual_midpoint,
    clippy::many_single_char_names,
    reason = "two edges summed at a map's few thousand feet, where no overflow is possible; the plane geometry's own names"
)]

use super::layout::Rect;

/// A face: the unit vector out of the house through it (y grows southward).
pub type Face = (i32, i32);

/// A symmetry of the square, `(a, b, c, d)`: a face (x, y) goes to (a x + b y, c x + d y).
pub type Turn = (i32, i32, i32, i32);

/// The four faces.
pub const N: Face = (0, -1);
/// East.
pub const E: Face = (1, 0);
/// South.
pub const S: Face = (0, 1);
/// West.
pub const W: Face = (-1, 0);

/// A band's depth.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Depth {
    /// The windward stand.
    Deep,
    /// One tree deep.
    Thin,
}

/// The dispersed layout's figures (feet): the yard's drying strip a band keeps out of on an unkept map, the way in through a ring,
/// the lane's room between two farms' groves, the service strip behind the house, the windward stand's depth in house depths, a
/// thin band's depth, and a bed's morning-sun reach.
///
/// Research:
///     yard drying strip width - research/questions/0038-sunlight-and-shade-on-the-farm.drawing.html: the project's sun figures leave 39 ft open before a yard - the strip is 22 ft, a departure the code keeps until feature 417 T33 - 22
///     way in through a ring - GUESS research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.drawing.html: one 36 ft break at the front's middle - 36
///     lane room between groves - GUESS research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.drawing.html: neighbors' groves at least 32 ft apart - 32
///     service strip behind the house - research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.drawing.html: windward stand 24 ft off the back and windward end walls - 24
///     windward stand depth - research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.drawing.html: 1.57 house depths, the grove about 6x the house - 1.57
///     thin band depth - research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.drawing.html: one tree, 17 ft - 17
///     a bed's morning sun - research/questions/0038-sunlight-and-shade-on-the-farm.drawing.html: no band within 50 ft east of a bed - 50
pub const FT: (f64, f64, f64, f64, f64, f64, f64) = (22.0, 36.0, 32.0, 24.0, 1.57, 17.0, 50.0);

/// The farmstead in the canonical frame: the yard, the garden, the bands (each its rect, face and depth) and the farm's well pocket.
#[derive(Clone, Debug, PartialEq)]
pub struct Farmstead {
    /// The threshing yard.
    pub yard: Rect,
    /// The garden bed.
    pub garden: Rect,
    /// The grove's bands.
    pub groves: Vec<(Rect, Face, Depth)>,
    /// The well pocket, where the farm keeps one.
    pub well: Option<Rect>,
}

/// What a canonical farmstead is laid with besides its house: the gap off the house, the garden's and the yard's sizes, the grove's
/// side count, whether the garden stands beside the yard, the thin band's depth, the garden's morning reach, the way in, the yard's
/// sun strip, whether the map keeps the sun (`sun_band`), the service strip, and the well pocket's side.
#[derive(Clone, Copy, Debug)]
pub struct Spec {
    /// The gap between the house and its yard and garden.
    pub gap: f64,
    /// The garden's width and depth.
    pub garden: (f64, f64),
    /// The yard's width and depth.
    pub yard: (f64, f64),
    /// How many sides the grove takes.
    pub sides: u32,
    /// Whether the garden stands beside the yard.
    pub garden_by_yard: bool,
    /// A thin band's depth.
    pub thin: f64,
    /// The garden's morning-sun reach east.
    pub sun_east: f64,
    /// The way in through a ring.
    pub way_in: f64,
    /// The yard's sun strip.
    pub yard_sun: f64,
    /// Whether the map keeps every tree out of the plots' sun.
    pub sun_band: bool,
    /// The service strip behind the house.
    pub back: f64,
    /// The well pocket's side (0 for none).
    pub well: f64,
}

fn boxed(x0: f64, y0: f64, x1: f64, y1: f64) -> Rect {
    ((x0 + x1) / 2.0, (y0 + y1) / 2.0, x1 - x0, y1 - y0)
}

fn edges(r: Rect) -> (f64, f64, f64, f64) {
    (
        r.0 - r.2 / 2.0,
        r.1 - r.3 / 2.0,
        r.0 + r.2 / 2.0,
        r.1 + r.3 / 2.0,
    )
}

/// The farmstead in the canonical frame about a house of `cw` by `ch` centered on the origin (`dispersed.canonical_farmstead`).
#[must_use]
pub fn canonical_farmstead(cw: f64, ch: f64, sp: &Spec) -> Farmstead {
    let (gap, (gw, gh), (yw, yh)) = (sp.gap, sp.garden, sp.yard);
    let yard = (0.0, ch / 2.0 + gap + yh / 2.0, yw, yh);
    let mut garden = if sp.garden_by_yard || sp.sun_band {
        (yw / 2.0 + gap + gw / 2.0, yard.1, gw, gh)
    } else {
        (cw / 2.0 + gap + gw / 2.0, 0.0, gw, gh)
    };
    if sp.sun_band {
        garden.1 = garden.1.max(ch / 2.0 + gap + gh / 2.0);
    }
    let mut works = vec![
        (-cw / 2.0, -ch / 2.0, cw / 2.0, ch / 2.0),
        edges(yard),
        edges(garden),
    ];
    let under = yw / 2.0 + gap < cw / 2.0;
    let well = (sp.well > 0.0).then(|| {
        let y = if under {
            yard.1.max(ch / 2.0 + sp.well / 2.0 - gap + gap / 3.0)
        } else {
            yard.1
        };
        (-(yw / 2.0 + gap + sp.well / 2.0), y, sp.well, sp.well)
    });
    works.extend(well.map(edges));
    let west_in = works.iter().map(|e| e.0).fold(f64::INFINITY, f64::min) - gap - sp.back;
    let north_in = works.iter().map(|e| e.1).fold(f64::INFINITY, f64::min) - gap - sp.back;
    let east_w = works.iter().map(|e| e.2).fold(f64::NEG_INFINITY, f64::max);
    let south_w = works.iter().map(|e| e.3).fold(f64::NEG_INFINITY, f64::max);
    let b = FT.4 * ch;
    let east_out = if sp.sides >= 3 {
        east_w + gap.max(sp.sun_east + 1.0) + sp.thin
    } else {
        east_w
    };
    let south_in = south_w + gap.max(sp.yard_sun + 1.0);
    let south_out = if sp.sides == 4 {
        south_in + sp.thin
    } else {
        south_w
    };
    let mut groves = vec![
        (
            boxed(west_in - b, north_in - b, east_out, north_in),
            N,
            Depth::Deep,
        ),
        (
            boxed(west_in - b, north_in, west_in, south_out),
            W,
            Depth::Deep,
        ),
    ];
    if sp.sides >= 3 {
        let east_end = if sp.sun_band {
            ch / 2.0
        } else if sp.sides == 4 {
            south_out
        } else {
            south_w
        };
        groves.push((
            boxed(east_out - sp.thin, north_in, east_out, east_end),
            E,
            Depth::Thin,
        ));
    }
    if sp.sides == 4 {
        let mid = yard.0;
        groves.push((
            boxed(west_in - b, south_in, mid - sp.way_in / 2.0, south_out),
            S,
            Depth::Thin,
        ));
        groves.push((
            boxed(mid + sp.way_in / 2.0, south_in, east_out, south_out),
            S,
            Depth::Thin,
        ));
    }
    Farmstead {
        yard,
        garden,
        groves,
        well,
    }
}

/// Whether the turn exchanges the axes.
#[must_use]
pub fn turns_axes(t: Turn) -> bool {
    t.0 == 0
}

/// A canonical face carried by the turn.
#[must_use]
pub fn turn_face(t: Turn, f: Face) -> Face {
    (t.0 * f.0 + t.1 * f.1, t.2 * f.0 + t.3 * f.1)
}

/// The symmetry carrying the canonical farmstead to the windward pair `key` ("NW", "NE", "SW" or "SE"); the unchanged frame for any
/// other key.
///
/// Research:
///     yard on the lee face - research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.html: the yard turned to the lee face nearest the south
#[must_use]
pub fn bundle_turn(key: &str) -> Turn {
    match key {
        "NE" => (-1, 0, 0, 1),
        "SW" => (0, 1, -1, 0),
        "SE" => (0, -1, -1, 0),
        _ => (1, 0, 0, 1),
    }
}

fn carried(r: Rect, t: Turn, hx: f64, hy: f64) -> Rect {
    let (x, y) = (
        f64::from(t.0) * r.0 + f64::from(t.1) * r.1,
        f64::from(t.2) * r.0 + f64::from(t.3) * r.1,
    );
    let (w, h) = if turns_axes(t) {
        (r.3, r.2)
    } else {
        (r.2, r.3)
    };
    (hx + x, hy + y, w, h)
}

/// The dispersed farmstead about a house at (hx, hy) of `hw` by `hh`, carried from the canonical frame by `turn`: its parts, its
/// bands with their faces as turned, its well pocket, and the frame the placer reserves, padded by `pad` (half the lane's room).
#[derive(Clone, Debug, PartialEq)]
pub struct Layout {
    /// The house.
    pub house: Rect,
    /// The yard.
    pub yard: Rect,
    /// The garden bed.
    pub garden: Rect,
    /// The bands.
    pub groves: Vec<Rect>,
    /// Each band's face as turned, and its depth.
    pub faces: Vec<(Face, Depth)>,
    /// The well pocket.
    pub well: Option<Rect>,
    /// The frame reserved, unraked.
    pub frame: Rect,
}

/// The dispersed farmstead (`dispersed.dispersed_layout`): in every frame but the northwest the garden goes beside the yard.
#[must_use]
pub fn dispersed_layout(house: Rect, sp: &Spec, turn: Turn, pad: f64) -> Layout {
    let (hx, hy, hw, hh) = house;
    let moved = turn != (1, 0, 0, 1);
    let (cw, ch) = if turns_axes(turn) { (hh, hw) } else { (hw, hh) };
    let can = canonical_farmstead(
        cw,
        ch,
        &Spec {
            garden_by_yard: moved,
            ..*sp
        },
    );
    let yard = carried(can.yard, turn, hx, hy);
    let garden = carried(can.garden, turn, hx, hy);
    let well = can.well.map(|w| carried(w, turn, hx, hy));
    let groves: Vec<Rect> = can
        .groves
        .iter()
        .map(|&(r, _, _)| carried(r, turn, hx, hy))
        .collect();
    let faces = can
        .groves
        .iter()
        .map(|&(_, f, d)| (turn_face(turn, f), d))
        .collect();
    let all: Vec<_> = groves
        .iter()
        .chain([&yard, &garden, &house])
        .chain(well.as_ref())
        .map(|&r| edges(r))
        .collect();
    let frame = boxed(
        all.iter().map(|e| e.0).fold(f64::INFINITY, f64::min) - pad,
        all.iter().map(|e| e.1).fold(f64::INFINITY, f64::min) - pad,
        all.iter().map(|e| e.2).fold(f64::NEG_INFINITY, f64::max) + pad,
        all.iter().map(|e| e.3).fold(f64::NEG_INFINITY, f64::max) + pad,
    );
    Layout {
        house,
        yard,
        garden,
        groves,
        faces,
        well,
        frame,
    }
}

/// The bands, each standing in a bed's east reach and overlapping the bed's height cut back at its near end to a foot clear of the
/// bed; a band whose cut run would be shorter than it is wide dropped (`dispersed.clear_east_of_beds`).
#[must_use]
pub fn clear_east_of_beds(groves: &[Rect], beds: &[Rect], reach: f64) -> Vec<Rect> {
    groves
        .iter()
        .filter_map(|&g| cut_east(g, beds, reach))
        .collect()
}

/// One band cut back out of each bed's east reach it stands in, or None where its cut run would be shorter than it is wide.
#[must_use]
pub fn cut_east(band: Rect, beds: &[Rect], reach: f64) -> Option<Rect> {
    let mut r = band;
    for &(bx, by, bw, bh) in beds {
        let east = bx + bw / 2.0;
        let (top, bottom) = (by - bh / 2.0, by + bh / 2.0);
        let west = r.0 - r.2 / 2.0;
        if !(east - 2.0 <= west
            && west < east + reach
            && r.1 - r.3 / 2.0 < bottom + 1.0
            && top - 1.0 < r.1 + r.3 / 2.0)
        {
            continue;
        }
        let (y0, y1) = if r.1 < by {
            (r.1 - r.3 / 2.0, top - 1.0)
        } else {
            (bottom + 1.0, r.1 + r.3 / 2.0)
        };
        if y1 - y0 < r.2 {
            return None;
        }
        r = (r.0, (y0 + y1) / 2.0, r.2, y1 - y0);
    }
    Some(r)
}

/// The ground a grove farm's way in crosses: from its house's front wall to the break in its front band, as wide as the break - None
/// where no band is broken (`fixture_seats.way_in_strip`). Bands and house in one frame.
///
/// Research:
///     a grove farm's way in kept clear - research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.drawing.html: the way-in strip handed to the fixtures as `keep`
#[must_use]
pub fn way_in_strip(house: Rect, bands: &[Rect], faces: &[Face]) -> Option<Rect> {
    let front = faces
        .iter()
        .copied()
        .find(|f| faces.iter().filter(|g| *g == f).count() >= 2)?;
    let pieces: Vec<Rect> = bands
        .iter()
        .zip(faces)
        .filter(|(_, f)| **f == front)
        .map(|(r, _)| *r)
        .collect();
    let ns = front.0 == 0;
    let h = along_of(house, ns);
    let lo = pieces
        .iter()
        .map(|&r| along_of(r, ns))
        .filter(|a| a.0 < h.0)
        .map(|a| a.0 + a.1 / 2.0)
        .reduce(f64::max)?;
    let hi = pieces
        .iter()
        .map(|&r| along_of(r, ns))
        .filter(|a| a.0 > h.0)
        .map(|a| a.0 - a.1 / 2.0)
        .reduce(f64::min)?;
    let sign = f64::from(if ns { front.1 } else { front.0 });
    let near = h.2 + sign * h.3 / 2.0;
    let band = pieces
        .iter()
        .map(|&r| {
            let a = along_of(r, ns);
            a.2 - sign * a.3 / 2.0
        })
        .min_by(|a, b| (a - near).abs().total_cmp(&(b - near).abs()))?;
    let (mid, span) = ((lo + hi) / 2.0, (hi - lo).max(0.0));
    let (mid_across, depth) = ((near + band) / 2.0, (band - near).abs());
    Some(if ns {
        (mid, mid_across, span, depth)
    } else {
        (mid_across, mid, depth, span)
    })
}

/// A rect read along a front: its center and size along the band, then across it.
fn along_of(r: Rect, ns: bool) -> (f64, f64, f64, f64) {
    if ns {
        (r.0, r.2, r.1, r.3)
    } else {
        (r.1, r.3, r.0, r.2)
    }
}

/// The square kept clear about a grove farm's front door - `out` past the yard's far edge, straight out along the line from the house
/// through the yard, `half` each way (`fixture_seats.door_room`).
///
/// Research:
///     the door's room past the yard - GUESS: no source could speak to it, a value of ours (feature 417 T36 pass P3, 2026-10-25); 8 ft past the yard's far edge, where the web's door path starts
///     the door's room - GUESS: no source could speak to it, a value of ours (feature 417 T36 pass P1, 2026-10-25); `half` each way, a routing tolerance
#[must_use]
pub fn door_room(house: Rect, yard: Rect, out: f64, half: f64) -> Rect {
    let (dx, dy) = (yard.0 - house.0, yard.1 - house.1);
    if dx.abs() >= dy.abs() {
        let s = if dx >= 0.0 { 1.0 } else { -1.0 };
        (
            yard.0 + s * (yard.2 / 2.0 + out),
            yard.1,
            2.0 * half,
            2.0 * half,
        )
    } else {
        let s = if dy >= 0.0 { 1.0 } else { -1.0 };
        (
            yard.0,
            yard.1 + s * (yard.3 / 2.0 + out),
            2.0 * half,
            2.0 * half,
        )
    }
}
