//! The pond at the field's foot (feature 444 T26 D4): sized from the paddy it drains, seated on the drainage line below the
//! collector's outfall where its rim clears the crop and the brook, its ditch run downhill from the outfall, its reeds at the shore.
//!
//! Research:
//!     a pond at the field's foot - research/questions/0060-field-drains-akusuiro.drawing.html: "about two maps in three lay a pond at the field's foot"
//!     a drain ending in a pond of its own - GUESS: research/questions/0060-field-drains-akusuiro.drawing.html: "A drain that ends in a pond of its own is our own guess"

#![expect(
    clippy::many_single_char_names,
    reason = "the plane geometry's own names"
)]

use std::collections::HashMap;

use super::brook::Brook;
use super::crop::{off_resting, Crop};
use super::{tally, SinkIn, Sunk};
use crate::field::fan::Pt;
use crate::field::geom::dist;

/// The pond's area, a share of the paddy it drains.
///
/// Research:
///     pond area - GUESS research/questions/0060-field-drains-akusuiro.drawing.html: "The pond at a field's foot covers about three parts in a hundred of the paddy it drains"
pub const SHARE: f64 = 0.03;
/// The pond's long radius over its short.
///
/// Research:
///     pond's shape - GUESS research/questions/0060-field-drains-akusuiro.drawing.html: "In a hamlet of fifteen households it is about 230 by 150 ft"
pub const ASPECT: f64 = 230.0 / 150.0;
/// How far the pond's rim keeps off the brook (feet).
///
/// Research:
///     the pond off the brook - GUESS: no source could speak to it, a value of ours (feature 417 T36 pass P2a, 2026-10-25); 12 ft off the brook
pub const BROOK_GAP: f64 = 12.0;
/// How far below the outfall the pond's near rim may stand before the drain goes off the map instead (feet).
///
/// Research:
///     set-back limit - GUESS: searched, the record silent (feature 417 T36 pass P2a, 2026-10-25); 300 ft below the outfall - research/questions/0060-field-drains-akusuiro.drawing.html: "A map whose pond would have to sit far below the fields sends its drain off the map as well"
pub const SETBACK_LIMIT: f64 = 300.0;
/// The pond's rim below the outfall at the nearest seat (feet).
///
/// Research:
///     the first seat's cushion - GUESS: no source could speak to it, a value of ours (feature 417 T36 pass P2a, 2026-10-25); a 12 ft cushion below the outfall
pub const CUSHION: f64 = 12.0;
/// The steps across the fall a blocked seat tries, in long radii, nearest first.
///
/// Research:
///     sways across the fall - GUESS: no source could speak to it, a value of ours (feature 417 T36 pass P2a, 2026-10-25); 0.9 and 1.8 long radii
pub const SWAYS: [f64; 5] = [0.0, -0.9, 0.9, -1.8, 1.8];
/// How far inside the canvas the pond's rim keeps (feet).
///
/// Research:
///     the pond on the canvas - NONE: the canvas's own margin, 20 ft
pub const CANVAS_INSET: f64 = 20.0;
/// The reeds' ring's points.
///
/// Research:
///     the ring's points - GUESS: no source could speak to it, a value of ours (feature 417 T38 pass N11, 2026-10-25); 16
pub const REED_PTS: u32 = 16;
/// The ditch's bow off its chord, a share of the run, and its most (feet).
///
/// Research:
///     bowed ditch - CONVENTION: up to 10 ft off the chord, 0.08 of the run, so it reads as dug earth
pub const BOW: (f64, f64) = (0.08, 10.0);
/// Past this off the collector's heading the ditch is led round to the pond on a curve, not run straight back (degrees).
///
/// Research:
///     led round a pond behind - CONVENTION: a cubic past 100 degrees off the heading, its handle 0.45 of the run, sampled at twelfths
pub const LED_ROUND_DEG: f64 = 100.0;

/// The pond's radii: its area `SHARE` of the paddy, its shape `ASPECT`.
#[must_use]
pub fn radii(area: f64) -> (f64, f64) {
    let ry = (SHARE * area / (std::f64::consts::PI * ASPECT)).sqrt();
    (ASPECT * ry, ry)
}

/// The ditch from the outfall `out` to the pond's center `c`: bowed off the chord where the pond lies ahead of the collector's
/// `head`ing, led round on a cubic where it lies more than `LED_ROUND_DEG` off it.
#[must_use]
pub fn ditch(out: Pt, head: Pt, c: Pt, fall: Pt) -> Vec<Pt> {
    let (tx, ty) = (c.0 - out.0, c.1 - out.1);
    let d = dist(out, c).max(1e-9);
    if (tx * head.0 + ty * head.1) / d >= LED_ROUND_DEG.to_radians().cos() {
        let bow = (BOW.0 * d).min(BOW.1);
        return vec![
            out,
            (
                f64::midpoint(out.0, c.0) - fall.1 * bow,
                f64::midpoint(out.1, c.1) + fall.0 * bow,
            ),
            c,
        ];
    }
    let (cx, cy) = (tx / d, ty / d);
    let (bx, by) = (head.0 + cx, head.1 + cy);
    let bn = (bx * bx + by * by).sqrt();
    let (bx, by) = if bn < 1e-9 {
        (cx, cy)
    } else {
        (bx / bn, by / bn)
    };
    let k = 0.45 * d;
    let c1 = (out.0 + bx * k, out.1 + by * k);
    let c2 = (c.0 - cx * k * 0.5, c.1 - cy * k * 0.5);
    (0..=12)
        .map(|n| {
            let u = f64::from(n) / 12.0;
            let m = 1.0 - u;
            (
                m * m * m * out.0
                    + 3.0 * m * m * u * c1.0
                    + 3.0 * m * u * u * c2.0
                    + u * u * u * c.0,
                m * m * m * out.1
                    + 3.0 * m * m * u * c1.1
                    + 3.0 * m * u * u * c2.1
                    + u * u * u * c.1,
            )
        })
        .collect()
}

/// Whether the pond centered at `c` stands on the canvas, clear of the crop and `BROOK_GAP` off the brook.
fn fits(
    inp: &SinkIn,
    crop: &Crop,
    brook: &mut Brook,
    c: Pt,
    r: (f64, f64),
    tests: &mut u64,
) -> bool {
    let (rx, ry) = r;
    if c.0 - rx < CANVAS_INSET
        || c.1 - ry < CANVAS_INSET
        || c.0 + rx > inp.canvas.0 - CANVAS_INSET
        || c.1 + ry > inp.canvas.1 - CANVAS_INSET
    {
        return false;
    }
    if !crop.pond_clear(c, rx, ry, tests) {
        return false;
    }
    let h = (rx * inp.fall.0).hypot(ry * inp.fall.1) + BROOK_GAP;
    let u = c.0 * inp.fall.0 + c.1 * inp.fall.1;
    let (gx, gy) = (rx + BROOK_GAP, ry + BROOK_GAP);
    for i in brook.span(u - h, u + h) {
        let (a, b) = brook.seg(i);
        if super::crop::meets_ellipse(a, b, c, gx, gy) {
            return false;
        }
    }
    true
}

/// The pond and its ditch, seated nearest first: on the drainage line below the outfall, stepped on by the pond's half-length
/// along the fall, then a step across the fall each way (`SWAYS`), until a seat fits and its ditch runs downhill clear of the
/// brook and the resting basins; None past `SETBACK_LIMIT` at every sway.
pub fn lay(
    inp: &SinkIn,
    crop: &Crop,
    brook: &mut Brook,
    out: Pt,
    head: Pt,
    counts: &mut HashMap<String, u64>,
) -> Option<Sunk> {
    let (rx, ry) = radii(crop.area);
    let f = inp.fall;
    let h = (rx * f.0).hypot(ry * f.1);
    let across = (-f.1, f.0);
    let mut tests = 0;
    let anchored = crop.holds(out, &mut tests);
    let mut seats = 0;
    let mut found = None;
    'sways: for sway in SWAYS {
        let mut d = h + CUSHION;
        while d - h <= SETBACK_LIMIT {
            seats += 1;
            let c = (
                out.0 + across.0 * sway * rx + f.0 * d,
                out.1 + across.1 * sway * rx + f.1 * d,
            );
            if fits(inp, crop, brook, c, (rx, ry), &mut tests) {
                let run = ditch(out, head, c, f);
                tests += 1;
                if !brook.crossed(&run, inp.brook_w)
                    && off_resting(&run, &inp.resting, anchored, &mut tests)
                {
                    found = Some((c, run));
                    break 'sways;
                }
            }
            d += h;
        }
    }
    tally(counts, "candidate@pond_seat", seats);
    tally(counts, "test@pond_seat", tests);
    let (c, run) = found?;
    let reeds: Vec<Pt> = (0..REED_PTS)
        .map(|i| {
            let a = f64::from(i) * std::f64::consts::TAU / f64::from(REED_PTS);
            (
                c.0 + (rx + inp.reed_ft) * a.cos(),
                c.1 + (ry + inp.reed_ft) * a.sin(),
            )
        })
        .collect();
    tally(counts, "write@pond", 3);
    tally(counts, "write@ditch", run.len() as u64);
    tally(counts, "write@reeds", u64::from(REED_PTS));
    Some(Sunk {
        form: "pond",
        run,
        to: "pond",
        pond: Some((c, rx, ry)),
        reeds,
        ..Sunk::default()
    })
}
