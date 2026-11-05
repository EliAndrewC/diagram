//! A homestead's bundle (feature 444 T30): its house, its yard, its beds, its storehouse annex, its byre and its fixtures, laid
//! unturned about the house's center from the household's rolls (`layout`, `fixtures`), then carried round the house's center by
//! the seat's rake - the homestead turns as one piece - each part's box as drawn, and the box round them all.
//!
//! Research:
//!     homestead turns as one piece - research/questions/0029-farmhouses-minka.drawing.html: the yard and beds turn with the house about its center, the ground cleared as drawn
//!     no grove of its own in a cluster - research/questions/0031-clustered-and-scattered-villages-shuson-sanson.drawing.html, research/questions/0072-shelter-belts-on-a-villages-windward-side-bofurin.drawing.html: a nucleated homestead carries no grove of its own
//!     farmstead fixtures - research/questions/0028-the-farmstead-and-what-stood-on-it-yashiki.drawing.html: the kinds the household's lot keeps, laid in its own frame

use super::bearing::turned_box;
use super::dispersed::{
    cut_east, dispersed_layout, door_room, way_in_strip, Depth, Face, Spec, Turn, FT,
};
use super::fixtures::{lay, Forms, Frame, Kind, Wall};
use super::layout::{beds, byre, kura, yard, Byre, Rect, Side, PART_GAP_FT, SIDES};
use super::Counts;
use crate::field::fan::Pt;

/// What a household's lot keeps, as the seating rolls it.
#[derive(Debug)]
pub struct Lot {
    /// The house's width and depth (feet).
    pub house: (f64, f64),
    /// Whether it keeps a storehouse annex on its north wall.
    pub kura: bool,
    /// The byre's form, where it keeps one.
    pub byre: Option<Byre>,
    /// The fixture kinds it keeps.
    pub fixtures: Vec<Kind>,
}

/// A homestead laid: each part's rectangle (center, width, height) in the map's frame - the house at its seat, the others carried
/// round it by `turn` - and each part's box as drawn, the box round them all, the bath room's wall where one was laid, and the
/// kind whose rule found no seat where one did not (the layout then is not the household's).
#[derive(Debug, Default)]
pub struct Bundle {
    /// The house.
    pub house: Rect,
    /// The threshing yard.
    pub yard: Rect,
    /// The kitchen beds.
    pub gardens: Vec<Rect>,
    /// The storehouse annex.
    pub kura: Option<Rect>,
    /// The byre and its turn against the house's.
    pub byre: Option<(Rect, f64)>,
    /// The fixtures.
    pub fixtures: Vec<(Kind, Rect)>,
    /// The wall the bath room took.
    pub bath: Option<Wall>,
    /// The kind whose rule found no seat.
    pub unlaid: Option<String>,
    /// The rake (degrees).
    pub turn: f64,
    /// Every part's box as drawn.
    pub boxes: Vec<Rect>,
    /// The box round them all.
    pub bbox: Rect,
    /// A grove farm's bands, unraked, each with its face as turned and its depth.
    pub groves: Vec<(Rect, Face, Depth)>,
    /// A grove farm's own well pocket, carried with its house.
    pub well: Option<Rect>,
}

/// How a grove farm is laid: its grove's side count, the symmetry carrying it to the map's wind, whether the map keeps the sun
/// (`sun_band`), its well pocket's side, and the yard's sun strip a ring's south band keeps out of.
#[derive(Clone, Copy, Debug)]
pub struct Grove {
    /// How many sides the grove takes.
    pub sides: u32,
    /// The symmetry to the map's wind.
    pub turn: Turn,
    /// Whether the map keeps every tree out of the plots' sun.
    pub sun_band: bool,
    /// The well pocket's side.
    pub well: f64,
    /// The yard's sun strip.
    pub yard_sun: f64,
}

/// How a fixture's persimmon keeps out of the plots' sun: how far, and at which rakes.
pub struct Sun<'a> {
    /// How far the plots' sun ground reaches (feet).
    pub shade: f64,
    /// The rakes the crown is asked at (degrees).
    pub turns: &'a [f64],
}

/// The box round `rects`.
#[must_use]
pub fn bbox_of(rects: &[Rect]) -> Rect {
    let (mut x0, mut y0, mut x1, mut y1) = (f64::MAX, f64::MAX, f64::MIN, f64::MIN);
    for r in rects {
        x0 = x0.min(r.0 - r.2 / 2.0);
        x1 = x1.max(r.0 + r.2 / 2.0);
        y0 = y0.min(r.1 - r.3 / 2.0);
        y1 = y1.max(r.1 + r.3 / 2.0);
    }
    (
        f64::midpoint(x0, x1),
        f64::midpoint(y0, y1),
        x1 - x0,
        y1 - y0,
    )
}

/// The household's bundle on garden `side`, its rolls keyed on `seat`, laid at `at` and turned by `turn`.
#[must_use]
#[expect(
    clippy::too_many_arguments,
    reason = "the lot, its seat, its side, its place, its rake, the forms and the sun"
)]
pub fn bundle(
    lot: &Lot,
    seat: Pt,
    side: Side,
    at: Pt,
    turn: f64,
    forms: &Forms,
    sun: &Sun,
    tests: &mut Counts,
) -> Bundle {
    let (hw, hh) = lot.house;
    let house = (0.0, 0.0, hw, hh);
    let y = yard(seat, hw, hh);
    let gardens = beds(seat, hw, hh, side);
    let annex = lot.kura.then(|| kura(hw, hh, true));
    let stall = lot.byre.map(|form| byre(hw, hh, side, form));
    let mut roofs = vec![house];
    roofs.extend(annex);
    roofs.extend(stall.map(|(dx, dy, w, h, _)| (dx, dy, w, h)));
    let mut ground = vec![y];
    ground.extend(&gardens);
    let roll = |s: f64| super::layout::hjit(seat.0, seat.1, s);
    let fr = Frame {
        house: (hw, hh),
        roofs: &roofs,
        ground: &ground,
        yard: Some(y),
        kura: lot.kura,
        shade: (sun.shade, sun.turns),
        keep: &[],
        fruit: &[],
    };
    let (fixtures, bath, unlaid) = if lot.fixtures.is_empty() {
        (Vec::new(), None, None)
    } else {
        match lay(&lot.fixtures, &fr, &roll, forms, tests) {
            Ok((laid, bath)) => (laid, bath, None),
            Err(why) => (Vec::new(), None, Some(why.0)),
        }
    };
    let th = turn.to_radians();
    let (c, s) = (th.cos(), th.sin());
    let carried = |r: Rect| (at.0 + r.0 * c - r.1 * s, at.1 + r.0 * s + r.1 * c, r.2, r.3);
    let mut b = Bundle {
        house: (at.0, at.1, hw, hh),
        yard: carried(y),
        gardens: gardens.iter().map(|&g| carried(g)).collect(),
        kura: annex.map(carried),
        byre: stall.map(|(dx, dy, w, h, t)| (carried((dx, dy, w, h)), t)),
        fixtures: fixtures.iter().map(|&(k, r)| (k, carried(r))).collect(),
        bath,
        unlaid,
        turn,
        ..Bundle::default()
    };
    let mut boxes = vec![turned_box(b.house, turn), turned_box(b.yard, turn)];
    boxes.extend(b.gardens.iter().map(|&g| turned_box(g, turn)));
    boxes.extend(b.kura.map(|k| turned_box(k, turn)));
    boxes.extend(b.byre.map(|(r, t)| turned_box(r, turn + t)));
    boxes.extend(b.fixtures.iter().map(|&(_, r)| turned_box(r, turn)));
    tests.add("write@bundle", boxes.len() as u64 * 4);
    b.bbox = bbox_of(&boxes);
    b.boxes = boxes;
    b
}

/// The door's room past the yard and its half-width (feet).
///
/// Research:
///     the door's room past the yard - GUESS: no source could speak to it, a value of ours (feature 417 T36 pass P3, 2026-10-25); `DOOR_OUT_FT` (8 ft) past the yard's far edge, where the web's door path starts - 8
///     the door's room - GUESS: no source could speak to it, a value of ours (feature 417 T36 pass P1, 2026-10-25); `DOOR_ROOM_HALF_FT`, a routing tolerance - 12
pub const DOOR_FT: (f64, f64) = (8.0, 12.0);

/// A grove farm's homestead at `at` (`bundle._bundle_layout`'s dispersed branch): its yard rolled at the seat, its garden capped at
/// an ordinary farm's, its own grove on the rolled sides turned to the wind (`dispersed.rs`), its fixtures laid round its own bands
/// (its persimmon may stand in them) and off its way in, the house's rake carrying the yard, the bed, the well and the fixtures, the
/// bands kept out of the bed's morning sun, each part's box as drawn and the box round them with the grove's frame.
///
/// Research:
///     garden size - research/questions/0039-kitchen-gardens-beside-farmhouses-yashikibatake.drawing.html: 0.48 x 0.85 of the house, capped at 42 x 30 ft on a grove farm, under 0039's 1,507 sq ft
///     dispersed farm's grove - research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.drawing.html: the farm's own grove on its rolled sides, turned to the wind
///     a grove farm's way in kept clear - research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.drawing.html: the way-in strip and the door's room handed to the fixtures as `keep`
#[must_use]
#[expect(
    clippy::too_many_arguments,
    reason = "the lot, its seat, its place, its rake, the forms, the sun and the grove"
)]
pub fn grove_bundle(
    lot: &Lot,
    seat: Pt,
    at: Pt,
    turn: f64,
    forms: &Forms,
    sun: &Sun,
    grove: &Grove,
    tests: &mut Counts,
) -> Bundle {
    let (hw, hh) = lot.house;
    let house = (0.0, 0.0, hw, hh);
    let y = yard(seat, hw, hh);
    let garden = ((0.48 * hw).min(42.0), (0.85 * hh).min(30.0));
    let (_, way_in, room, back, _, thin, east) = FT;
    let spec = Spec {
        gap: PART_GAP_FT,
        garden,
        yard: (y.2, y.3),
        sides: grove.sides,
        garden_by_yard: false,
        thin,
        sun_east: east,
        way_in,
        yard_sun: grove.yard_sun,
        sun_band: grove.sun_band,
        back,
        well: grove.well,
    };
    let lay_out = dispersed_layout(house, &spec, grove.turn, room / 2.0);
    let faces: Vec<Face> = lay_out.faces.iter().map(|f| f.0).collect();
    let mut roofs = vec![house];
    roofs.extend(lay_out.well);
    let ground = [lay_out.yard, lay_out.garden];
    let mut keep: Vec<Rect> = way_in_strip(house, &lay_out.groves, &faces)
        .into_iter()
        .collect();
    if !lay_out.groves.is_empty() {
        keep.push(door_room(house, lay_out.yard, DOOR_FT.0, DOOR_FT.1));
    }
    let roll = |s: f64| super::layout::hjit(seat.0, seat.1, s);
    let fr = Frame {
        house: (hw, hh),
        roofs: &roofs,
        ground: &ground,
        yard: Some(lay_out.yard),
        kura: false,
        shade: (sun.shade, sun.turns),
        keep: &keep,
        fruit: &lay_out.groves,
    };
    let (fixtures, bath, unlaid) = if lot.fixtures.is_empty() {
        (Vec::new(), None, None)
    } else {
        match lay(&lot.fixtures, &fr, &roll, forms, tests) {
            Ok((laid, bath)) => (laid, bath, None),
            Err(why) => (Vec::new(), None, Some(why.0)),
        }
    };
    let th = turn.to_radians();
    let (c, s) = (th.cos(), th.sin());
    let carried = |r: Rect| (at.0 + r.0 * c - r.1 * s, at.1 + r.0 * s + r.1 * c, r.2, r.3);
    let moved = |r: Rect| (at.0 + r.0, at.1 + r.1, r.2, r.3);
    let gardens = vec![carried(lay_out.garden)];
    let groves = lay_out
        .groves
        .iter()
        .zip(&lay_out.faces)
        .filter_map(|(&r, &(f, d))| cut_east(moved(r), &gardens, east).map(|k| (k, f, d)))
        .collect();
    let mut b = Bundle {
        house: (at.0, at.1, hw, hh),
        yard: carried(lay_out.yard),
        gardens,
        fixtures: fixtures.iter().map(|&(k, r)| (k, carried(r))).collect(),
        bath,
        unlaid,
        turn,
        groves,
        well: lay_out.well.map(carried),
        ..Bundle::default()
    };
    let mut boxes = vec![turned_box(b.house, turn), turned_box(b.yard, turn)];
    boxes.extend(b.gardens.iter().map(|&g| turned_box(g, turn)));
    boxes.extend(b.fixtures.iter().map(|&(_, r)| turned_box(r, turn)));
    tests.add("write@grove_bundle", boxes.len() as u64 * 4);
    let mut framed = vec![moved(lay_out.frame), boxes[1], boxes[2]];
    framed.extend(b.well.map(|w| turned_box(w, turn)));
    framed.extend(boxes[3..].iter().copied());
    b.bbox = bbox_of(&framed);
    b.boxes = boxes;
    b
}

/// The homestead's envelope at a seat: the box round its bundles on every garden side - tested once before any side is laid, so a
/// part laid inside it never needs ground the envelope did not clear.
#[must_use]
pub fn envelope(
    lot: &Lot,
    seat: Pt,
    at: Pt,
    turn: f64,
    forms: &Forms,
    sun: &Sun,
    tests: &mut Counts,
) -> Rect {
    let boxes: Vec<Rect> = SIDES
        .iter()
        .map(|&side| bundle(lot, seat, side, at, turn, forms, sun, tests).bbox)
        .collect();
    bbox_of(&boxes)
}
