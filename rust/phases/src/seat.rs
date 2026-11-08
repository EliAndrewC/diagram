//! The seat (feature 444 T27): where the settlement sits on the field's margin, its back to the wind, ranked with the margins the
//! house seating falls back down - and the brook's fords, the only places a later way crosses it - decided once, drawn nowhere.
//!
//! Research:
//!     the seat - NONE: the stage's machinery; each rule's claim is at the unit that keeps it

use std::collections::HashMap;
use std::fmt;

use crate::field::fan::Pt;

pub mod exit;
pub mod fords;
pub mod index;
pub mod margins;

/// Why no margin seats the settlement: refused by name, never seated off the wind (S4).
#[derive(Debug, PartialEq, Eq)]
pub struct SeatRefused(pub String);

impl fmt::Display for SeatRefused {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        f.write_str(&self.0)
    }
}

/// A wall the way out keeps off: a ring and the margin it is kept by (feet).
pub type Wall = (Vec<Pt>, f64);

/// What the seat is handed (the driver's, D1).
#[derive(Clone)]
pub struct SeatIn {
    /// The canvas's width and height (feet).
    pub canvas: Pt,
    /// The fall of the land, a unit vector.
    pub fall: Pt,
    /// The wind, a unit vector pointing to where it comes from.
    pub wind: Pt,
    /// The dot of a margin's back with the wind at or past which the back faces it (Python's `WIND_BACK_MIN_DOT`).
    pub back_min_dot: f64,
    /// The field's outline.
    pub outline: Vec<Pt>,
    /// The band's half-depth and half-length (feet; Python's `band_extent`, which the canvas is sized by too).
    pub band: Pt,
    /// The dry plots' rings.
    pub plots: Vec<Vec<Pt>>,
    /// The wet toe below the fields, where the roll lays one.
    pub toe: Vec<Pt>,
    /// A tail pond's reed fringes.
    pub reeds: Vec<Vec<Pt>>,
    /// The brook's course as first laid.
    pub brook: Vec<Pt>,
    /// The way out's walls: the wet ground grown by the lane, the outline, the pond's ring at its berth.
    pub walls: Vec<Wall>,
    /// The way out's water lines that are no stream: the drain's run off the map, the field's ditches and the farm channels.
    pub lines: Vec<(Pt, Pt)>,
    /// The streams' courses, gapped at the fords for the way out and for every later way.
    pub streams: Vec<Vec<Pt>>,
    /// The fords' spacing along the brook, half-length and the bend past which a reach is no crossing place (Python's
    /// `FORD_SPACING`, `FORD_HALF` and `FORD_BEND_DEG`, which the ways read too).
    pub ford: (f64, f64, f64),
}

/// The seat on one margin: its center, its along and away units, the band's half-extents, the anchor, and whether its back is
/// off the wind.
#[derive(Debug, Clone, PartialEq)]
pub struct Frame {
    /// The band's center.
    pub center: Pt,
    /// The unit along the margin.
    pub along: Pt,
    /// The unit away from the field, the back.
    pub out: Pt,
    /// The band's half-length along the margin and half-depth away from it (feet).
    pub band: Pt,
    /// The margin's midpoint.
    pub anchor: Pt,
    /// Whether the back is off the wind.
    pub offwind: bool,
}

/// What the seat decided (D1): the chosen frame and its ladder, the fords, and the watercourses every later way is routed
/// against.
#[derive(Debug)]
pub struct Seated {
    /// The chosen margin's frame, then the ladder's, best first.
    pub frames: Vec<Frame>,
    /// The fords along the brook.
    pub fords: Vec<Pt>,
    /// The streams' segments gapped at the fords.
    pub stream_segs: Vec<(Pt, Pt)>,
    /// The counters (D7).
    pub counts: HashMap<String, u64>,
}

pub use crate::counts::tally;

/// The seat: the fords opened first, every later way gapped at them; the candidate margins refused and ranked; the head given a
/// dry way out of the frame, the next margin taken where it has none.
///
/// # Errors
/// `SeatRefused` where no margin keeps every rule.
///
/// Research:
///     a walled-in head gives way - research/questions/0081-village-lanes.drawing.html: lanes keep to dry ground, so a margin whose seat has no dry way out of the frame is dropped and the next in the ranking taken
///     the fords before the seat - research/questions/0035-villages-beside-their-stream-one-bank-or-both.drawing.html: a way crosses the brook only at a crossing place, so the seat's way out is asked of the brook gapped at them
///     the back to the hill where the wind cannot be backed - GUESS: research/questions/0031-clustered-and-scattered-villages-shuson-sanson.drawing.html weighs no hill against the wind - its rolled falls run away from the wind or square across it; 背山面水, the back to the hill and to the wind, the high side and the windward side one side; where a declared fall runs into the wind no margin backs both, and the hill is kept - the margins ranked with the high side as the wind's, each seat recorded off the wind (GUESS: the record draws no fall into the wind, the rolled falls never take one)
pub fn seat(inp: &SeatIn) -> Result<Seated, SeatRefused> {
    let mut counts = HashMap::new();
    let (spacing, half, bend) = inp.ford;
    let fords = fords::fords(&inp.brook, spacing, half, bend, &mut counts);
    let stream_segs = fords::gapped(&inp.streams, &fords, half, &mut counts);
    let (mut ranked, stopped) = margins::ranked(inp, &mut counts);
    // THE BACK TO THE HILL WHERE NO MARGIN CAN TURN IT TO THE WIND (feature 444 T27, Sawada's declared fall of 225 degrees into
    // its northwest wind): the margins ranked again as if the wind came down from the high side, each seat recorded off the wind
    if ranked.is_empty() {
        let uphill = SeatIn {
            wind: (-inp.fall.0, -inp.fall.1),
            ..inp.clone()
        };
        ranked = margins::ranked(&uphill, &mut counts)
            .0
            .into_iter()
            .map(|f| Frame { offwind: true, ..f })
            .collect();
    }
    let mut walled = 0;
    let mut lines = inp.lines.clone();
    lines.extend(stream_segs.iter().copied());
    let mut way = exit::Exit::new(&inp.walls, &lines, inp.canvas, &mut counts);
    while let Some(head) = ranked.first() {
        if way.has_exit(head.center, &mut counts) {
            break;
        }
        ranked.remove(0);
        walled += 1;
    }
    if ranked.is_empty() {
        let [frame, belt, toe, field, reeds, back] = stopped;
        return Err(SeatRefused(format!(
            "no field margin turns its back to the wind clear of the dry hem, the toe and the canvas edge (of the margins facing it: \
             {frame} off the frame, {belt} with the belt off the canvas, {toe} on the toe, {field} on the field, {reeds} in the reeds, \
             {back} with crop behind, {walled} walled in)"
        )));
    }
    tally(&mut counts, "write@frames", 8 * ranked.len() as u64 + 3);
    Ok(Seated {
        frames: ranked,
        fords,
        stream_segs,
        counts,
    })
}

#[cfg(test)]
mod tests;
