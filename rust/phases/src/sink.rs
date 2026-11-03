//! The sink (feature 444 T26): where the field's runoff ends - a pond at the field's foot with its ditch and reeds, or, on the
//! off-map roll, the drain joining the passing brook or run off the map - laid once, every rule asked before anything is written.
//!
//! Research:
//!     where the runoff goes - research/questions/0060-field-drains-akusuiro.drawing.html: "Where the passing brook comes near the collector's outfall, the drain joins it ... where it does not, the drain runs on as a ditch to the edge of the map, or to the pond at the field's foot"

use std::collections::HashMap;
use std::fmt;

use crate::field::fan::Pt;
use crate::field::geom::dist;

pub mod brook;
pub mod crop;
pub mod offmap;
pub mod pond;
pub mod py;

use brook::{Brook, Stations};
use crop::Crop;

/// The span back up the collector its heading at the outfall is measured over (feet): a collector's last few feet can hook any
/// way, so its bearing where it ends is read over a chord.
///
/// Research:
///     the collector's heading - NONE: a measuring chord, 40 ft
pub const HEADING_SPAN: f64 = 40.0;

/// Why the sink lays nothing: a run no rule allows, refused by name, never drawn in breach (S4).
#[derive(Debug, PartialEq, Eq)]
pub struct SinkRefused(pub String);

impl fmt::Display for SinkRefused {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        f.write_str(&self.0)
    }
}

/// What the thin Python gathered (D1).
pub struct SinkIn {
    /// The plan's sink form: a pond, or off the map.
    pub pond: bool,
    /// The canvas's width and height (feet).
    pub canvas: Pt,
    /// The fall of the land, a unit vector.
    pub fall: Pt,
    /// The drainage bearing (degrees clockwise from east on the map).
    pub flow_deg: f64,
    /// The field's outline.
    pub outline: Vec<Pt>,
    /// The drain collector's points, its outfall last.
    pub drain: Vec<Pt>,
    /// The brook's drawn width (feet).
    pub brook_w: f64,
    /// The heads of the races taken off the brook (its taps).
    pub taps: Vec<Pt>,
    /// The resting basins' rings, which no run crosses.
    pub resting: Vec<Vec<Pt>>,
    /// The reeds' width out from the pond's shore (feet; Python's `SINK_FRINGE`, which the pond's bank reads too).
    pub reed_ft: f64,
    /// The brook's length on the canvas below a confluence, so the junction reads (feet; Python's `BROOK_JOIN_TRUNK`, which the
    /// hinterland's frame reads too).
    pub join_trunk: f64,
}

/// What the sink laid (D1): the run and what it ends at, the pond and its reeds, the confluence and the brook as drawn round it.
#[derive(Debug, Default)]
pub struct Sunk {
    /// "pond" or "offmap", as drawn.
    pub form: &'static str,
    /// The run from the outfall.
    pub run: Vec<Pt>,
    /// What the run ends at: "pond", "stream" or "offmap".
    pub to: &'static str,
    /// The pond's center and radii.
    pub pond: Option<(Pt, f64, f64)>,
    /// The reeds' ring at the shore.
    pub reeds: Vec<Pt>,
    /// Where the run joins the brook.
    pub confluence: Option<Pt>,
    /// The brook as drawn again round a confluence held on a bend (D2), where one was.
    pub brook_drawn: Option<Vec<Pt>>,
    /// The counters (D7).
    pub counts: HashMap<String, u64>,
}

/// The collector's heading at its outfall, read over `HEADING_SPAN` back up it.
#[must_use]
pub fn heading(drain: &[Pt]) -> Option<Pt> {
    let end = *drain.last()?;
    let mut back = *drain.get(drain.len().checked_sub(2)?)?;
    for &q in drain.iter().rev().skip(1) {
        back = q;
        if dist(q, end) >= HEADING_SPAN {
            break;
        }
    }
    let d = dist(back, end);
    (d > 0.0).then(|| ((end.0 - back.0) / d, (end.1 - back.1) / d))
}

/// Add `n` to the counter `key`.
pub fn tally(counts: &mut HashMap<String, u64>, key: &str, n: u64) {
    if n > 0 {
        *counts.entry(key.to_owned()).or_insert(0) += n;
    }
}

/// The sink: the pond where the plan rolls one and its seat is found, else the off-map run (0060: "A map whose pond would have to
/// sit far below the fields sends its drain off the map as well"). None where the field has no collector.
///
/// # Errors
/// `SinkRefused` where no run the rules allow exists.
pub fn sink(inp: &SinkIn, stations: &mut dyn Stations) -> Result<Option<Sunk>, SinkRefused> {
    let (Some(&out), Some(head)) = (inp.drain.last(), heading(&inp.drain)) else {
        return Ok(None);
    };
    let mut counts = HashMap::new();
    tally(&mut counts, "read@drain", inp.drain.len() as u64);
    let crop = Crop::read(&inp.outline, out, inp.fall, &mut counts);
    let mut brook = Brook::new(stations, inp.fall);
    let mut sunk = if inp.pond {
        pond::lay(inp, &crop, &mut brook, out, head, &mut counts)
    } else {
        None
    };
    if sunk.is_none() {
        sunk = Some(offmap::lay(inp, &crop, &mut brook, out, head, &mut counts)?);
    }
    tally(&mut counts, "read@brook", brook.reads);
    tally(&mut counts, "test@brook", brook.tests);
    let mut s = sunk.unwrap_or_default();
    s.counts = counts;
    Ok(Some(s))
}

#[cfg(test)]
mod tests;
