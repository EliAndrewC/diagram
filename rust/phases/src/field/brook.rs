//! The brook that feeds the comb (feature 444 T16): down the valley through its intake, on along the fall for its tap's stride,
//! then bending in to run past the fan's flank outside the crop, meandering, and on to the frame. Its figures are the
//! plan's (`consts_water.py`, passed in); the course is rebuilt from them, the old field code unread.
//!
//! Research:
//!     the intake on the brook - research/questions/0059-where-the-ditch-leaves-the-brook-the-intake-and-its-weir-toshuko-and-seki.drawing.html: the head race leaves the brook at its intake
//!     the brook bends - research/questions/0054-which-way-water-flows-and-how-channels-bend-and-join.drawing.html: a step over 22 ft led in over two

use super::fan::{Fan, Pt};
use super::geom::seg_dist;
use super::index::Index;

/// How far past the canvas each end of the brook runs, so both ends lie off the map (feet).
///
/// Research:
///     off-map ends - CONVENTION: the brook's rules ask both ends off the map; one station past the edge
pub const OFF_MAP_FT: f64 = 20.0;
/// The meander's swing, from its trough to its crest (feet).
///
/// Research:
///     the meander's swing - GUESS: research/questions/0054-which-way-water-flows-and-how-channels-bend-and-join.drawing.html silent on how far a brook swings; 12 ft, past twice the rules' 4 ft level tolerance
pub const MEANDER_FT: f64 = 12.0;
/// The meander's wave down the fall (feet).
///
/// Research:
///     the meander's wave - GUESS: research/questions/0054-which-way-water-flows-and-how-channels-bend-and-join.drawing.html silent on a meander's length; 80 ft, about fifteen of the brook's widths, which keeps every straight run under the ten widths a natural stream rarely passes (`brook_rules.RULED_MAX_FT`)
pub const MEANDER_WAVE_FT: f64 = 80.0;
/// The least lean a brook segment keeps off the screen's axes (degrees): past the brook rules' 1.6.
///
/// Research:
///     no screen axis - CANON: the GM, 2026-08-26, on a brook drawn level along the frame: "appears to run exactly east to west parallel to the edge of the map. that makes it look like a mistake"; the brook rules refuse 1.6 degrees, and this keeps a margin past it, 2
pub const AXIS_OFF_DEG: f64 = 2.0;
/// A bound on the stations either way (a guard: a canvas is a few thousand feet across).
///
/// Research:
///     the bound - NONE: a guard
const MAX_STATIONS: usize = 1000;

/// The brook's figures, every one the plan's (`consts_water.py`): the head race's length (the plan's rolled `head_lead`), the angle
/// it leaves the brook at, the tap's straight stride, the most the course moves across in one station, its skirt outside the crop
/// and its wander past the skirt, the station spacing, and its width.
///
/// Research:
///     the brook's figures - NONE: the plan's, carried in; each is claimed where the plan sets it (`consts_water.py`)
#[derive(Debug, Clone, Copy)]
pub struct BrookIn {
    pub lead: f64,
    pub offtake_deg: f64,
    pub tap_run: f64,
    pub slew: f64,
    pub skirt: f64,
    pub wander: f64,
    pub station: f64,
    pub w: f64,
}

/// The brook: its stations from upstream to down, and the intake on it.
///
/// Research:
///     the brook's record - NONE: the record's type, holding what `brook` decides
#[derive(Debug, Clone, PartialEq)]
pub struct Brook {
    pub pts: Vec<Pt>,
    pub intake: Pt,
}

/// A point `u` feet down the fall from the fan's head middle and `x` feet across it (toward the fan's right looking downhill).
///
/// Research:
///     the frame - NONE: a coordinate transform
fn local(fan: &Fan, u: f64, x: f64) -> Pt {
    (
        fan.fork.0 + fan.down.0 * u + fan.across.0 * x,
        fan.fork.1 + fan.down.1 * u + fan.across.1 * x,
    )
}

/// The brook past the fan on its `side` (+1 the fan's right, -1 its left). The head race leaves the division point's intake turned
/// `offtake_deg` off the fall away from the brook's flank, so the intake lies `lead` up that line from the fork; the brook comes
/// down the fall to it, holds the intake's line for `tap_run`, then each `station` moves across at most `slew` toward its line -
/// the flank, plus the skirt - and runs on past the fan's foot, off the `canvas` both ways, meandering outward by the wider of
/// `wander` and `MEANDER_FT`, the meander's trough at the intake.
///
/// Research:
///     the race turns away from the brook - research/questions/0059-where-the-ditch-leaves-the-brook-the-intake-and-its-weir-toshuko-and-seki.html: the intake stands on the bank of the land it serves; the race's turn away from the brook is ours
///     on past the intake - research/questions/0059-where-the-ditch-leaves-the-brook-the-intake-and-its-weir-toshuko-and-seki.drawing.html: the brook runs on past the intake - down the fall, holding the intake's line across for the plan's tap stride, meandering as everywhere
///     outside the crop - GUESS: the record silent on how far outside the crop the brook keeps; the plan's `BROOK_SKIRT` square to the flank (wider across the fall by the flank's lean), moving in by at most a station's slew and out at once
///     the meander outward - GUESS: the record silent on a brook's swing; held to the side away from the fan so the skirt is kept, its swing the wider of the plan's wander and `MEANDER_FT`, so one wave carries the course's whole stray
///     the trough at the intake - NONE: the wave's phase set so the brook at the intake runs down the fall, the line the race's angle is read from
#[expect(
    clippy::many_single_char_names,
    reason = "the plane geometry's own names"
)]
#[must_use]
pub fn brook(fan: &Fan, side: f64, b: BrookIn, canvas: Pt) -> Brook {
    let (sin, cos) = b.offtake_deg.to_radians().sin_cos();
    let corner_x = side * fan.half_side(0.0, side);
    let (u_i, x_i) = (-b.lead * cos, corner_x + side * b.lead * sin);
    let intake = local(fan, u_i, x_i);
    let off = |p: Pt| {
        p.0 < -OFF_MAP_FT
            || p.1 < -OFF_MAP_FT
            || p.0 > canvas.0 + OFF_MAP_FT
            || p.1 > canvas.1 + OFF_MAP_FT
    };
    // the wave's trough at the intake: no offset and no slope there, so the brook passes through the intake heading down the fall
    // (a straight stride at the tap, measured on 120 rolls, ran 110-160 ft straight against 0054's ten widths; T16's claims round)
    let phase = -std::f64::consts::FRAC_PI_2 - u_i / MEANDER_WAVE_FT * std::f64::consts::TAU;
    // the meander held to the outward side, so the skirt is kept; a wave of `MEANDER_WAVE_FT` down the fall
    // its swing the plan's wander or the meander's, whichever is wider: the one wave carries the course's whole stray, so no
    // second walk can cancel it into a level run
    let swing = MEANDER_FT.max(b.wander);
    let meander = |u: f64| {
        side * swing * (1.0 + (u / MEANDER_WAVE_FT * std::f64::consts::TAU + phase).sin()) / 2.0
    };
    // upstream: from off the map down the fall to the intake
    let mut up = Vec::new();
    let mut v = u_i;
    while up.len() < MAX_STATIONS {
        v -= b.station;
        let p = local(fan, v, x_i + meander(v));
        up.push(p);
        if off(p) {
            break;
        }
    }
    up.reverse();
    let mut pts = up;
    pts.push(intake);
    let (mut u, mut x) = (u_i, x_i);
    // the flank leans in as the fan narrows: a skirt held square to it is wider across the fall by the lean's secant
    let lean = (fan.half_head - fan.half_foot) / fan.length.max(1.0);
    let secant = lean.hypot(1.0);
    for _ in 0..MAX_STATIONS {
        u += b.station;
        // the flank as drawn, its waves applied, at its widest within half a station either way (past the foot, the foot's)
        let at = |v: f64| fan.half_side(v.clamp(0.0, fan.length), side);
        let flank = at(u)
            .max(at(u - b.station / 2.0))
            .max(at(u + b.station / 2.0));
        let want = side * (flank + b.skirt * secant);
        // the course keeps outside its line: it may move out at once, in by at most a slew - and none in for the tap's stride
        x = if (want - x) * side > 0.0 {
            want
        } else if u <= u_i + b.tap_run {
            x
        } else {
            x + (want - x).clamp(-b.slew, b.slew)
        };
        let p = local(fan, u, x + meander(u));
        pts.push(p);
        if u > fan.length && off(p) {
            break;
        }
    }
    off_the_axes(&mut pts, intake, (fan.across.0 * side, fan.across.1 * side));
    Brook { pts, intake }
}

/// The brook kept off the screen's axes: a segment within `AXIS_OFF_DEG` of the map's x or y axis has its downstream end moved
/// outward (`out`) until it leans that far off - its upstream end where the downstream end is the intake, which stays put.
///
/// Research:
///     no screen axis - CANON: the GM, 2026-08-26: "appears to run exactly east to west parallel to the edge of the map. that makes it look like a mistake"; the brook rules refuse a segment within 1.6 degrees of an axis, so each is leaned to `AXIS_OFF_DEG`
fn off_the_axes(pts: &mut [Pt], intake: Pt, out: Pt) {
    // a move can bring a neighbor onto an axis: passes until none moves, a bounded number
    for _ in 0..8 {
        if !off_the_axes_once(pts, intake, out) {
            return;
        }
    }
}

/// One pass of `off_the_axes`; whether it moved a point.
///
/// Research:
///     no screen axis - CANON: the GM, 2026-08-26: "appears to run exactly east to west parallel to the edge of the map. that makes it look like a mistake" - a segment within `AXIS_OFF_DEG` of an axis leaned off it
///     the push - CONVENTION: half a degree past `AXIS_OFF_DEG`, so one push clears the bar; the intake never moved, the race's start held where `brook` set it
fn off_the_axes_once(pts: &mut [Pt], intake: Pt, out: Pt) -> bool {
    let mut moved_any = false;
    for k in 0..pts.len().saturating_sub(1) {
        let (a, b) = (pts[k], pts[k + 1]);
        let deg = (b.1 - a.1).atan2(b.0 - a.0).to_degrees().rem_euclid(90.0);
        let near = deg.min(90.0 - deg);
        if near >= AXIS_OFF_DEG {
            continue;
        }
        let len = super::geom::dist(a, b);
        let push = len * (AXIS_OFF_DEG + 0.5).to_radians().tan();
        let moved = if b == intake { k } else { k + 1 };
        let sign = if b == intake { -1.0 } else { 1.0 };
        pts[moved] = (
            pts[moved].0 + out.0 * push * sign,
            pts[moved].1 + out.1 * push * sign,
        );
        moved_any = true;
    }
    moved_any
}

/// The weir at a `weir` intake: a bar across the brook, `half` feet either side of the intake, running diagonally upstream
/// `skew_deg` from square as it crosses away from the field, `thick` feet through (its form's). Returns the bar's four corners and
/// its bearing on the maps' angles.
///
/// Research:
///     the weir - research/questions/0059-where-the-ditch-leaves-the-brook-the-intake-and-its-weir-toshuko-and-seki.drawing.html: across the whole brook, 7 ft half-length, diagonally upstream at 30 degrees, 1.5 to 5 ft thick by form
#[expect(
    clippy::many_single_char_names,
    reason = "the plane geometry's own names"
)]
#[must_use]
pub fn weir(
    brook: &Brook,
    fan: &Fan,
    side: f64,
    half: f64,
    skew_deg: f64,
    thick: f64,
) -> ([Pt; 4], f64) {
    let c = brook.intake;
    let next = brook
        .pts
        .iter()
        .position(|p| *p == c)
        .map_or(c, |i| brook.pts[(i + 1).min(brook.pts.len() - 1)]);
    let t = super::geom::unit(c, next);
    // square to the brook where it runs, turned to the side away from the field
    let side_of = (fan.across.0 * side, fan.across.1 * side);
    let square = if -t.1 * side_of.0 + t.0 * side_of.1 >= 0.0 {
        (-t.1, t.0)
    } else {
        (t.1, -t.0)
    };
    let (sin, cos) = skew_deg.to_radians().sin_cos();
    let bar = (square.0 * cos - t.0 * sin, square.1 * cos - t.1 * sin);
    let (a, b) = (
        (c.0 - bar.0 * half, c.1 - bar.1 * half),
        (c.0 + bar.0 * half, c.1 + bar.1 * half),
    );
    let n = (-bar.1 * thick / 2.0, bar.0 * thick / 2.0);
    let ring = [
        (a.0 - n.0, a.1 - n.1),
        (b.0 - n.0, b.1 - n.1),
        (b.0 + n.0, b.1 + n.1),
        (a.0 + n.0, a.1 + n.1),
    ];
    (ring, bar.1.atan2(bar.0).to_degrees().rem_euclid(360.0))
}

/// The brook's segments filed in the water index (D5).
///
/// Research:
///     the filing - NONE: the index's bookkeeping
pub fn file(brook: &Brook, ix: &mut Index) -> Vec<usize> {
    brook.pts.windows(2).map(|p| ix.file(p[0], p[1])).collect()
}

/// The least distance from `p` to the brook's filed segments near it, asked of the index within `r` (infinite if none lies near).
///
/// Research:
///     the clearance - NONE: a distance asked of the index
#[must_use]
pub fn clearance(p: Pt, r: f64, ix: &mut Index) -> f64 {
    let near = ix.near((p.0 - r, p.1 - r), (p.0 + r, p.1 + r));
    near.iter()
        .map(|&i| {
            let (a, b) = ix.segs[i];
            seg_dist(p, a, b)
        })
        .fold(f64::INFINITY, f64::min)
}

#[cfg(test)]
mod tests {
    use super::{brook, clearance, file, weir, BrookIn};
    use crate::field::fan::fan;
    use crate::field::geom::{dist, signed_area};
    use crate::field::index::Index;

    const B: BrookIn = BrookIn {
        lead: 105.0,
        offtake_deg: 35.0,
        tap_run: 70.0,
        slew: 22.0,
        skirt: 34.0,
        wander: 10.0,
        station: 35.0,
        w: 7.0,
    };

    #[test]
    fn the_brook_keeps_outside_the_crop_and_bends_gently() {
        for side in [1.0, -1.0] {
            let f = fan(26.0 * 43_560.0, 1.0, 90.0, (3200.0, 3200.0), 4);
            let br = brook(&f, side, B, (6400.0, 6400.0));
            let mut ix = Index::default();
            let ids = file(&br, &mut ix);
            assert_eq!(ids.len(), br.pts.len() - 1);
            for p in &f.ring {
                assert!(clearance(*p, B.skirt * 2.0, &mut ix) >= B.skirt - 1e-6);
            }
            for w in br.pts.windows(2).skip(2) {
                let across = (w[1].0 - w[0].0).abs();
                assert!(across <= B.slew + B.skirt + B.wander, "{across}");
            }
            assert!(br.pts.len() > 30);
        }
        let f = fan(26.0 * 43_560.0, 1.0, 90.0, (0.0, 0.0), 4);
        let br = brook(&f, 1.0, B, (6400.0, 6400.0));
        let (ring, deg) = weir(&br, &f, 1.0, 7.0, 30.0, 1.5);
        assert!((signed_area(&ring).abs() - 14.0 * 1.5).abs() < 1e-6);
        assert!((dist(ring[0], ring[1]) - 14.0).abs() < 1e-9);
        // the brook runs south; the bar runs 30 degrees off square, its far end (away from the field) upstream
        let far = (
            f64::midpoint(ring[1].0, ring[2].0),
            f64::midpoint(ring[1].1, ring[2].1),
        );
        assert!(far.1 < br.intake.1, "the far end upstream");
        assert!((0.0..360.0).contains(&deg));
        let mut ix = Index::default();
        assert!(clearance((0.0, 0.0), 10.0, &mut ix).is_infinite());
    }
}
