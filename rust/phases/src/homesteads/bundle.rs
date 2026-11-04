//! A homestead's bundle (feature 444 T30): its house, its yard, its beds, its storehouse annex, its byre and its fixtures, laid
//! unturned about the house's center from the household's rolls (`layout`, `fixtures`), then carried round the house's center by
//! the seat's rake - the homestead turns as one piece - each part's box as drawn, and the box round them all.
//!
//! Research:
//!     homestead turns as one piece - research/questions/0029-farmhouses-minka.drawing.html: the yard and beds turn with the house about its center, the ground cleared as drawn
//!     no grove of its own in a cluster - research/questions/0031-clustered-and-scattered-villages-shuson-sanson.drawing.html, research/questions/0072-shelter-belts-on-a-villages-windward-side-bofurin.drawing.html: a nucleated homestead carries no grove of its own
//!     farmstead fixtures - research/questions/0028-the-farmstead-and-what-stood-on-it-yashiki.drawing.html: the kinds the household's lot keeps, laid in its own frame

use super::bearing::turned_box;
use super::fixtures::{lay, Forms, Frame, Kind, Wall};
use super::layout::{beds, byre, kura, yard, Byre, Rect, Side, SIDES};
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
    tests: &mut u64,
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
    *tests += boxes.len() as u64 * 4;
    b.bbox = bbox_of(&boxes);
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
    tests: &mut u64,
) -> Rect {
    let boxes: Vec<Rect> = SIDES
        .iter()
        .map(|&side| bundle(lot, seat, side, at, turn, forms, sun, tests).bbox)
        .collect();
    bbox_of(&boxes)
}
