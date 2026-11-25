//! The margins (feature 444 T27 D2): every margin of the field that can turn the settlement's back to the wind, refused where it
//! breaks a rule of the seat - the cheapest first - and the rest scored and ranked, the chosen seat and its ladder.
//!
//! Research:
//!     the margins - NONE: the seat's machinery; each rule's claim is at the unit that keeps it

#![expect(
    clippy::cast_possible_truncation,
    clippy::cast_precision_loss,
    reason = "grid cells and counts of a few thousand, well inside f64's mantissa and i64"
)]
use std::collections::HashMap;

use super::index::{area, clipped, Cells, Strips, CELL};
use super::{tally, Frame, SeatIn};
use crate::field::fan::Pt;
use crate::field::geom::{hull, seg_dist, unit};

/// How far past the 45-degree bar a margin's back is turned off a flank (radians): a hair, so the turned back passes the bar
/// without resting on it.
///
/// Research:
///     its salts, guards and sentinels - NONE: they decide nothing about the place - half a degree past the bar
pub const TURN_SLACK: f64 = 0.5 * std::f64::consts::PI / 180.0;

/// The share of the belt's band that may fall off the canvas before a margin is refused.
///
/// Research:
///     belt room off the canvas - CONVENTION: at most 0.2 of the band; the seat's belt room is geometry, not a researched figure
pub const BELT_ROOM_MAX_OFF: f64 = 0.2;

/// The share of the back's ground under the dry crop past which a margin is refused.
///
/// Research:
///     clear ground behind - GUESS: no source could speak to it, a value of ours (feature 417 T29 pass B, 2026-10-25); refused past 0.30 of the back under dry crop, the back's area now measured where it was sampled
pub const BACK_FOUL_MAX: f64 = 0.30;

/// The band's standoff out from the field's margin (feet).
///
/// Research:
///     seat standoff from the field - GUESS research/questions/0029-farmhouses-minka.drawing.html: our maps draw farmhouses 10 to 13 ft from the paddy, a figure the page builds from guesses; 12 ft, the band's near edge hugging the field
pub const STANDOFF: f64 = 12.0;

/// The back's depth behind the margin, in band depths.
///
/// Research:
///     depth behind the margin - GUESS: no source could speak to it, a value of ours (feature 417 T29 pass E, 2026-10-25); 2.6 band depths, the cluster and its belt
pub const BACK_DEPTHS: f64 = 2.6;

/// The band's sample depths out from the margin, in band depths and feet: its near edge, past its middle, its far edge.
///
/// Research:
///     the band's sample points - GUESS: no page gives a sampling, a knob of ours (feature 444 T27); half a band depth, a depth and 34 ft, two depths
pub const SAMPLE_DEPTHS: [(f64, f64); 3] = [(0.5, 0.0), (1.0, 34.0), (2.0, 0.0)];

/// Where along the band its open-ground and reed points stand, in half-lengths either side of its middle.
///
/// Research:
///     the band's sample points - GUESS: no page gives a sampling, a knob of ours (feature 444 T27); the middle and 0.6 of the half-length either side
pub const SAMPLE_ALONG: [f64; 3] = [-0.6, 0.0, 0.6];

/// Where along the band its brook points stand, in half-lengths: closer than the reeds' because the brook is a line a third-point
/// grid can miss.
///
/// Research:
///     the brook's sample points - GUESS: no page gives a sampling, a knob of ours (feature 444 T27); 0, 0.45 and 0.9 of the half-length either side
pub const BROOK_ALONG: [f64; 5] = [-0.9, -0.45, 0.0, 0.45, 0.9];

/// The reach within which a band point counts as on the brook (feet).
///
/// Research:
///     brook reach on the band - GUESS: searched, the record silent (feature 417 T29 pass B, 2026-10-25) on the 30 ft - homesteads faced their channel (Takamine 1977, pass B); a band point within 30 ft of the brook counts as on the water
pub const BROOK_REACH: f64 = 30.0;

/// The belt's band upwind of the cluster's windward fringe (feet): its near face and its far edge.
///
/// Research:
///     belt's depth - research/questions/0071-groves-around-a-southern-chinese-village-the-fengshui-woods-fengshuilin-and-the-dooryard-copse.drawing.html: a back wood drawn 80 to 120 ft deep, a convention; the band's 36 to 146 ft
///     belt's distance upwind - GUESS: the near face 36 ft behind the fringe, whatever the wind; this only asks for room on the canvas - where the clumps stand is the belt's own placer's
pub const BELT_BAND: (f64, f64) = (36.0, 146.0);

/// The belt's band across the wind, in the cluster's half-widths.
///
/// Research:
///     its search steps and tolerances - GUESS: no source could speak to it, a value of ours (feature 417 T38 pass N5, 2026-10-25) - 0.9 of the cluster's half-width either side
pub const BELT_ACROSS: f64 = 0.9;

/// The score's weights.
///
/// Research:
///     wind and upslope weights - GUESS: no source could speak to it, a value of ours (feature 417 T29 pass B, 2026-10-25); 1.0 for facing the wind, 0.8 for upslope
///     reed-fringe share weight - GUESS: no source could speak to it, a value of ours (feature 417 T29 pass B, 2026-10-25); 2.5 times the band's share in the reeds
///     dry hem penalty - GUESS: no source could speak to it, a value of ours (feature 417 T29 pass B, 2026-10-25); 1.6 within two band depths, plus 2.5 times the back's foul
///     belt room scored - CONVENTION: 2.5 times the belt's share off the canvas
pub const WEIGHTS: Weights = Weights {
    wind: 1.0,
    upslope: 0.8,
    reeds: 2.5,
    hem: 1.6,
    back: 2.5,
    belt: 2.5,
};

/// The score's weights, by term.
pub struct Weights {
    /// Facing the wind.
    pub wind: f64,
    /// The upslope end.
    pub upslope: f64,
    /// The band's share in the reeds.
    pub reeds: f64,
    /// The dry hem within two band depths.
    pub hem: f64,
    /// The back's share under crop.
    pub back: f64,
    /// The belt's share off the canvas.
    pub belt: f64,
}

/// How far past square to the wind a margin's dot may fall and still count as square: a margin 90 degrees off the wind is in tier
/// 1 (its floating point's own slack).
///
/// Research:
///     the square end in - GUESS research/questions/0031-clustered-and-scattered-villages-shuson-sanson.drawing.html: a fall "across" the wind is admitted and such a hamlet sits by the windward side of its
///     fields, so tier 1 takes "a margin 45 to 90 degrees off the wind" with both ends in, as the falls are admitted (square to the
///     wind or away, `water_frame.rs` `admitted`): a fall square to the wind leaves the head square to it, and with the end out a
///     roll so falling whose windward flank is refused has its head refused too (the Rust gate's seed 901280, when its windward
///     flank lay on the wet toe, before 449 T432 cut the toe at the fields' lower corners; it seats with its back to the wind
///     either way since 449 T426, measured 2026-11-25)
pub(super) const SQUARE_EPS: f64 = 1e-9;

/// The candidate seats a field's outline offers, `(margin midpoint, the back's direction, tier)`, in the outline's order.
///
/// Research:
///     one seat a margin - GUESS: no page divides a field's edge into seats; each outline edge offers one, at its midpoint
///     back faces the wind - research/questions/0072-shelter-belts-on-a-villages-windward-side-bofurin.drawing.html: a clustered village shelters behind one belt at its windward edge - tier 0, the margin's own outward normal within 45 degrees of the wind
///     45 degree bar - GUESS: searched, the record silent (feature 417 T29 pass B, 2026-10-25) on the bar; 0072 gives no tolerance
///     back turned off a flank - GUESS: no page gives a cap; tier 1, a margin 45 to 90 degrees off the wind (both ends in, `SQUARE_EPS`) offers its back turned toward the wind just past the 45-degree bar, at most 45.5 degrees off its own normal (the bar and its half-degree slack), so the band still stands off the field; research/questions/0029-farmhouses-minka.drawing.html's quarter turn is a house's off the fall line, on a slope our maps do not draw
#[must_use]
pub fn candidates(
    outline: &[Pt],
    wind: Pt,
    back_min_dot: f64,
    tests: &mut u64,
) -> Vec<(Pt, Pt, u8)> {
    let n = outline.len();
    let cen = (
        outline.iter().map(|p| p.0).sum::<f64>() / n as f64,
        outline.iter().map(|p| p.1).sum::<f64>() / n as f64,
    );
    let mut out = Vec::new();
    for i in 0..n {
        let (a, b) = (outline[i], outline[(i + 1) % n]);
        *tests += 2;
        let mid = (f64::midpoint(a.0, b.0), f64::midpoint(a.1, b.1));
        let mut nrm = unit((0.0, 0.0), (-(b.1 - a.1), b.0 - a.0));
        if nrm.0 * (mid.0 - cen.0) + nrm.1 * (mid.1 - cen.1) < 0.0 {
            nrm = (-nrm.0, -nrm.1); // the outward side, whichever way the ring turns
        }
        let dot = nrm.0 * wind.0 + nrm.1 * wind.1;
        if dot >= back_min_dot {
            out.push((mid, nrm, 0));
        } else if dot > -SQUARE_EPS {
            let off = (nrm.0 * wind.1 - nrm.1 * wind.0).atan2(dot);
            let turn = off - (std::f64::consts::FRAC_PI_4 - TURN_SLACK).copysign(off);
            let ang = nrm.1.atan2(nrm.0) + turn;
            out.push((mid, (ang.cos(), ang.sin()), 1));
        }
    }
    out
}

/// The belt's ground behind a band reaching `far` ft upwind of its windward fringe: the band (`center`, `along`, `out`, its
/// half-depth and half-length `band`) and its copy carried `far` along the wind, their convex hull, cut to `BELT_ACROSS` of the
/// band's width across the wind about its middle, and never past `margin` (a point on the field's margin, `out` its dry side) - the
/// band swept upwind, so the ground follows the windward faces the belt is planted along, its near face and, on an oblique wind,
/// its windward end, on the dry side alone.
///
/// Research:
///     the belt along the windward fringe - research/questions/0072-shelter-belts-on-a-villages-windward-side-bofurin.drawing.html: each cluster carries its own band along its windward edge, the band hugging the cluster - so the belt's ground is the band's windward faces carried upwind (the deleted belt placer's fringe profile, 449 T293), never a rectangle off the band's windward-most corner, which on a wind 20 to 45 degrees off square lay up to 0.61 to 0.95 of the band's half-length nearer the margin than the fringe's belt (measured 2026-11-22, a probe of the seat's frames on the pool and Sawada's declared fall swept 180 to 270 degrees: the rectangle 34 and 73 percent on the paddy at 230 and 240, the fringe's belt 12.6 and 17 ft off the margin)
///     its across-wind share - GUESS: no source could speak to it, a value of ours (`BELT_ACROSS`)
///     on the dry side of the margin - GUESS research/questions/0019-polders-fields-diked-against-the-fluctuating-water-weitian-waju.drawing.html: a polder's village keeps its belt on the windward side its polder leaves dry, none between the houses and the dike - the record silent on a belt between houses and a dike or a field to windward (the research pass of 2026-11-22, 449 T292), so the belt's ground is kept on the band's side of the line through the margin's midpoint square to the band's back - the margin's own dry side on a tier-0 seat, turned with the band on a tier-1 seat, where it acts only through `belt_off`'s share under a separate belt wind (the algorithmically easier route); on a comb whose band stands off a windward field (`ranked`'s lead) the fringe's belt stands past the standoff, so the cut takes nothing there
#[must_use]
pub fn belt_swept(
    center: Pt,
    along: Pt,
    out: Pt,
    band: Pt,
    wind: Pt,
    far: f64,
    margin: Pt,
) -> Vec<Pt> {
    let (dep, lat) = band;
    let w = unit((0.0, 0.0), wind);
    let p = (-w.1, w.0);
    let corners = [(-1.0, -1.0), (1.0, -1.0), (1.0, 1.0), (-1.0, 1.0)].map(|(a, b): (f64, f64)| {
        (
            center.0 + along.0 * lat * a + out.0 * dep * b,
            center.1 + along.1 * lat * a + out.1 * dep * b,
        )
    });
    let pts: Vec<Pt> = corners
        .iter()
        .flat_map(|&c| [c, (c.0 + w.0 * far, c.1 + w.1 * far)])
        .collect();
    let half = BELT_ACROSS
        * ((p.0 * along.0 + p.1 * along.1).abs() * lat + (p.0 * out.0 + p.1 * out.1).abs() * dep);
    let long = far + 2.0 * (lat + dep) + 1.0;
    let at = |v: f64, u: f64| (center.0 + p.0 * v + w.0 * u, center.1 + p.1 * v + w.1 * u);
    let slab = [
        at(-half, -long),
        at(half, -long),
        at(half, long),
        at(-half, long),
    ];
    let reach = long + (center.0 - margin.0).hypot(center.1 - margin.1);
    let side = |v: f64, u: f64| {
        (
            margin.0 + along.0 * v + out.0 * u,
            margin.1 + along.1 * v + out.1 * u,
        )
    };
    let dry = [
        side(-reach, 0.0),
        side(reach, 0.0),
        side(reach, reach),
        side(-reach, reach),
    ];
    clipped(&clipped(&hull(&pts), &slab), &dry)
}

/// The share of the belt's ground behind a seat at `center` that falls off the canvas: the band swept from `BELT_BAND.0` to
/// `BELT_BAND.1` upwind of its windward fringe on the dry side of `margin` (`belt_swept`); none where the band sweeps no ground.
///
/// Research:
///     belt room on the canvas - CONVENTION: scored, refused past `BELT_ROOM_MAX_OFF`; the belt's ground between the band's fringe carried 36 and 146 ft upwind, clipped to the canvas
#[must_use]
pub fn belt_off(center: Pt, along: Pt, out: Pt, band: Pt, wind: Pt, canvas: Pt, margin: Pt) -> f64 {
    let frame = [
        (0.0, 0.0),
        (canvas.0, 0.0),
        (canvas.0, canvas.1),
        (0.0, canvas.1),
    ];
    let off = |r: &[Pt]| area(r) - area(&clipped(r, &frame));
    let near = belt_swept(center, along, out, band, wind, BELT_BAND.0, margin);
    let whole = belt_swept(center, along, out, band, wind, BELT_BAND.1, margin);
    let room = area(&whole) - area(&near);
    if room <= 1e-9 {
        return 0.0;
    }
    ((off(&whole) - off(&near)) / room).clamp(0.0, 1.0)
}

/// The brook's course in its order along the fall, asked for its nearest segment by bisection where the course falls the whole
/// way, by a scan of every segment where it does not.
pub struct Brook<'a> {
    course: &'a [Pt],
    along: Vec<f64>,
    ordered: bool,
}

impl<'a> Brook<'a> {
    /// The course read once, each station's place along the fall.
    #[must_use]
    pub fn new(course: &'a [Pt], fall: Pt, reads: &mut u64) -> Self {
        let along: Vec<f64> = course.iter().map(|p| p.0 * fall.0 + p.1 * fall.1).collect();
        *reads += course.len() as u64;
        let ordered = along.windows(2).all(|w| w[0] <= w[1]);
        Self {
            course,
            along,
            ordered,
        }
    }

    /// The distance from `q` to the brook where it is under `reach`, else `reach`: from the segments whose stations lie within
    /// `reach` of `q`'s place along the fall, and one either side.
    #[must_use]
    pub fn near(&self, q: Pt, fall: Pt, reach: f64, tests: &mut u64) -> f64 {
        let n = self.course.len();
        if n < 2 {
            return reach;
        }
        let (lo, hi) = if self.ordered {
            let u = q.0 * fall.0 + q.1 * fall.1;
            *tests += 2 * u64::from(usize::BITS - n.leading_zeros());
            let lo = self
                .along
                .partition_point(|&a| a < u - reach)
                .saturating_sub(1);
            let hi = self.along.partition_point(|&a| a <= u + reach).min(n - 1);
            (lo, hi)
        } else {
            (0, n - 1)
        };
        let mut best = reach;
        for i in lo..hi {
            *tests += 1;
            best = best.min(seg_dist(q, self.course[i], self.course[i + 1]));
        }
        best
    }
}

/// The ground the margins are asked against, indexed once (the derivation's Indexes).
struct Ground<'a> {
    outline: Strips,
    toe: Option<Strips>,
    reeds: Vec<Strips>,
    plots: &'a [Vec<Pt>],
    cells: Cells,
    brook: Brook<'a>,
}

impl<'a> Ground<'a> {
    fn new(inp: &'a SeatIn, counts: &mut HashMap<String, u64>) -> Self {
        let mut filed = 0;
        let outline = Strips::new(&inp.outline, &mut filed);
        tally(counts, "write@outline_strips", filed);
        let mut filed = 0;
        let toe = (inp.toe.len() >= 3).then(|| Strips::new(&inp.toe, &mut filed));
        let fringes = inp
            .reeds
            .iter()
            .filter(|r| r.len() >= 3)
            .map(|r| Strips::new(r, &mut filed))
            .collect();
        tally(counts, "write@wet_strips", filed);
        let mut cells = Cells::new(CELL);
        let mut filed = 0;
        for (i, p) in inp.plots.iter().enumerate() {
            filed += cells.file(i, p);
        }
        tally(
            counts,
            "read@plots",
            inp.plots.iter().map(Vec::len).sum::<usize>() as u64,
        );
        tally(counts, "write@plot_cells", filed);
        let mut reads = 0;
        let brook = Brook::new(&inp.brook, inp.fall, &mut reads);
        tally(counts, "read@brook", reads);
        Self {
            outline,
            toe,
            reeds: fringes,
            plots: &inp.plots,
            cells,
            brook,
        }
    }

    /// The share of the back's rectangle under the dry plots.
    fn back_share(&self, rect: &[Pt; 4], tests: &mut u64) -> f64 {
        *tests += 1;
        if self.plots.is_empty() {
            return 0.0; // no dry plot stands (the hem is laid after the seat): no cell is read
        }
        let lo = (
            rect.iter().map(|p| p.0).fold(f64::MAX, f64::min),
            rect.iter().map(|p| p.1).fold(f64::MAX, f64::min),
        );
        let hi = (
            rect.iter().map(|p| p.0).fold(f64::MIN, f64::max),
            rect.iter().map(|p| p.1).fold(f64::MIN, f64::max),
        );
        let (near, read) = self.cells.in_box(lo, hi);
        *tests += read + 8 * near.len() as u64;
        let crop: f64 = near
            .iter()
            .map(|&i| area(&clipped(&self.plots[i], rect)))
            .sum();
        crop / area(rect).max(1e-9)
    }

    /// The nearest dry-plot edge to `p` within `reach`, else `reach`: the cells round `p` ring by ring, stopped at the first ring
    /// that cannot hold an edge nearer than the nearest found.
    fn hem(&self, p: Pt, reach: f64, tests: &mut u64) -> f64 {
        let mut best = reach;
        let rings = (reach / CELL).ceil() as i64;
        let (cx, cy) = ((p.0 / CELL).floor() as i64, (p.1 / CELL).floor() as i64);
        let mut seen: Vec<usize> = Vec::new();
        for r in 0..=rings {
            if (r - 1) as f64 * CELL > best {
                break;
            }
            for gx in cx - r..=cx + r {
                for gy in cy - r..=cy + r {
                    if (gx - cx).abs() != r && (gy - cy).abs() != r {
                        continue; // inside the ring, read before
                    }
                    let lo = (gx as f64 * CELL + 0.5, gy as f64 * CELL + 0.5);
                    let (items, read) = self.cells.in_box(lo, lo);
                    *tests += read;
                    for i in items {
                        if seen.contains(&i) {
                            continue;
                        }
                        seen.push(i);
                        let ring = &self.plots[i];
                        for k in 0..ring.len() {
                            *tests += 1;
                            best = best.min(seg_dist(p, ring[k], ring[(k + 1) % ring.len()]));
                        }
                    }
                }
            }
        }
        best
    }
}

/// How deep into the band a corner of the field may stand, as a share of the band's depth, before the margin is refused.
///
/// Research:
///     the band along a bending margin - GUESS: research/questions/0031-clustered-and-scattered-villages-shuson-sanson.drawing.html puts the cluster beside its paddy and is silent on how closely a straight band follows a bending field edge; a tenth of the band's depth - with none allowed 70 of 3,200 rolls found no seat, with a tenth 2, the most of any band on the paddy 3.5 percent of it (measured 2026-11-24, seeds 1 to 400 at eight sizes and falls)
pub const FIELD_IN_BAND_MAX: f64 = 0.1;

/// The margins in the order the seat prefers them, and how many each refusal stopped (off the frame, the belt off the canvas, on
/// the toe, on the field, in the reeds, crop behind) - wind-facing ones first, each tier by score, the brook's share on the band
/// the tie-break between margins otherwise level, the first met winning a tie - every one that breaks a rule refused.
///
/// Research:
///     seat on the field's margin - research/questions/0031-clustered-and-scattered-villages-shuson-sanson.drawing.html: higher, drier ground beside the paddy, scored upslope
///     band on the canvas - CONVENTION: the seat center at least the band's half-length inside the frame
///     not on the wet toe - research/questions/0058-ground-too-wet-to-build-on.drawing.html, research/questions/0057-marshes-and-wetlands-shitchi.drawing.html: nothing is built on the marsh below the fields - the seat, its margin's midpoint and every sample of its band off it, and where the toe stops at the fields' lower corners (a comb's) the band's corners and its ends' middles too (449 T432: the two points alone passed a band at the fields' lower corner swung under their foot); a polder's toe, spanning its ring and 90 ft up beside it, is asked at the samples alone, its rim refusing 654 of 6,000 polders (measured 2026-11-25)
///     the band on open ground - research/questions/0031-clustered-and-scattered-villages-shuson-sanson.drawing.html: beside its paddy, the band's points off the field, and no corner of the field's outline deeper in the band than `FIELD_IN_BAND_MAX` of its depth - a margin whose band holds one is refused with those on the field (449 T423: the nine points alone passed a band with the paddy's corner between them), and none of the band's four corners past that dip on the field (449 T435: a margin shorter than the band, the field's next edge rising across the band's end, 574 of 41,000 sweep rolls)
///     not in the reed fringe - CANON: the GM's ruling of 2026-08-28, refused centered in a pond's reed fringe, scored down at an end; it departs from research/questions/0058-ground-too-wet-to-build-on.drawing.html, which does not count the fringe as marsh
///     no drain rule at the seat - research/questions/0058-ground-too-wet-to-build-on.drawing.html: the ground below a drain kept only from dispersed farmsteads, not a nucleated cluster
///     brook across the band - research/questions/0035-villages-beside-their-stream-one-bank-or-both.drawing.html: "A hamlet site the brook does not cross is preferred when two sites are otherwise equally good", the brook's share the tie-break, never refused
///     the back's width - GUESS: no page sizes the ground behind a seat; one half-depth across the margin's midpoint, the strip behind the band's middle, which the belt cannot bend away from
///     the dry hem's reach - GUESS: no source could speak to it, a value of ours; a dry plot within two band half-depths of where the band's room starts - the margin, or the belt's room past it where the band is stood out for the belt - the band's own depth, scores the seat down
///     the ladder - research/questions/0031-clustered-and-scattered-villages-shuson-sanson.drawing.html: a hamlet never splits, so the margins it falls back to are whole seats, ranked
///     the belt between the houses and a windward field - GUESS research/questions/0031-clustered-and-scattered-villages-shuson-sanson.drawing.html: where a declared fall into the wind backs the cluster to the hill (`belt_wind`, the map's own wind), the belt still stands on the windward side (research/questions/0072-shelter-belts-on-a-villages-windward-side-bofurin.drawing.html: the wind decides the side), so a margin whose field lies within 45 degrees of the wind stands its band the belt's far edge (`BELT_BAND`) further off it, the belt's ground between the houses and the paddy, and every sample of the band moves with it; a wind along the band leaves the belt at a band end, no room added; the belt's room on the canvas is asked of the map's own wind
#[expect(
    clippy::too_many_lines,
    reason = "the refusals in order, cheapest first, then the score: one pass a candidate"
)]
pub fn ranked(
    inp: &SeatIn,
    belt_wind: Option<Pt>,
    counts: &mut HashMap<String, u64>,
) -> (Vec<Frame>, [u64; 6]) {
    let (dep, lat) = inp.band;
    let ground = Ground::new(inp, counts);
    let mut scan = 0;
    let cands = candidates(&inp.outline, inp.wind, inp.back_min_dot, &mut scan);
    tally(counts, "test@margins", scan);
    let cen = (
        inp.outline.iter().map(|p| p.0).sum::<f64>() / inp.outline.len().max(1) as f64,
        inp.outline.iter().map(|p| p.1).sum::<f64>() / inp.outline.len().max(1) as f64,
    );
    let (mut refusal, mut scoring) = (0, 0);
    let mut kept: Vec<(f64, f64, u8, Frame)> = Vec::new();
    let mut stopped = [0u64; 6];
    // the wind the belt stands against: the map's own, where the seat is ranked against another (the hill's, `seat`; a polder's
    // landward shore, `SeatIn::belt_wind`)
    let wind = belt_wind.or(inp.belt_wind).unwrap_or(inp.wind);
    for (mid, n, tier) in cands {
        let along = (-n.1, n.0);
        // THE BELT'S ROOM ON A WINDWARD FIELD (449 T277): the band stood the belt's far edge further out, where the field below
        // the margin lies to windward of the houses, so the belt has its ground between them
        let lead = if belt_wind.is_some() && -(n.0 * wind.0 + n.1 * wind.1) >= inp.back_min_dot {
            BELT_BAND.1
        } else {
            0.0
        };
        let band_pt = |d: f64, t: f64| {
            (
                mid.0 + n.0 * (d + lead) + along.0 * lat * t,
                mid.1 + n.1 * (d + lead) + along.1 * lat * t,
            )
        };
        let center = (
            mid.0 + n.0 * (dep + STANDOFF + lead),
            mid.1 + n.1 * (dep + STANDOFF + lead),
        );
        refusal += 2;
        if !(lat <= center.0
            && center.0 <= inp.canvas.0 - lat
            && lat <= center.1
            && center.1 <= inp.canvas.1 - lat)
        {
            stopped[0] += 1;
            continue;
        }
        refusal += 8;
        let off = belt_off(center, along, n, inp.band, wind, inp.canvas, mid);
        if off > BELT_ROOM_MAX_OFF {
            stopped[1] += 1;
            continue;
        }
        if let Some(toe) = &ground.toe {
            if toe.inside(center, &mut refusal) || toe.inside(mid, &mut refusal) {
                stopped[2] += 1;
                continue;
            }
        }
        let pts: Vec<Pt> = SAMPLE_DEPTHS
            .iter()
            .flat_map(|&(k, ft)| SAMPLE_ALONG.iter().map(move |&t| (k * dep + ft, t)))
            .map(|(d, t)| band_pt(d, t))
            .collect();
        // ...AND NONE OF THE BAND'S SAMPLES ON IT (449 T432): asked of the center and the margin's midpoint alone, a band at the
        // fields' lower corner swung under their foot - 1,643 of 6,000 declared falls into the wind a quarter or more on the toe
        // once it stopped at the corners, and 9,627 of 41,000 sweep rolls a twentieth or more before, the worst 32.7 percent; with
        // the samples and the rim, none past 0.1 percent (measured 2026-11-25, each seated band's rectangle cut by its toe)
        // ...and, where the toe stops at the fields' lower corners, its four corners and its ends' middles, where the toe's end
        // reached in between the samples (a polder's toe spans its ring: its rim not asked, `SeatIn::toe_rim`)
        if let Some(toe) = &ground.toe {
            let rim = [
                (0.0, -1.0),
                (0.0, 1.0),
                (1.0, -1.0),
                (1.0, 1.0),
                (2.0, -1.0),
                (2.0, 1.0),
            ]
            .map(|(k, t)| band_pt(STANDOFF + k * dep, t));
            let asked = if inp.toe_rim { &rim[..] } else { &[] };
            if pts
                .iter()
                .chain(asked)
                .any(|&p| toe.inside(p, &mut refusal))
            {
                stopped[2] += 1;
                continue;
            }
        }
        if pts.iter().any(|&p| ground.outline.inside(p, &mut refusal)) {
            stopped[3] += 1;
            continue;
        }
        // ...AND NO CORNER OF THE FIELD DEEP IN THE BAND (449 T423): the samples stand at the band's middle and 0.6 of its
        // half-length either side, and a corner of the field between them went unseen - a band turned off a flank swung over the
        // paddy's corner, a tenth of it on the rice (14 of 446 seated rolls, measured 2026-11-24 over seeds 1 to 150 at three
        // sizes); a straight band along a bending flank still dips into it at its near edge, up to `FIELD_IN_BAND_MAX`
        refusal += 2 * inp.outline.len() as u64;
        if inp.outline.iter().any(|p| {
            let r = (p.0 - mid.0, p.1 - mid.1);
            let (d, t) = (r.0 * n.0 + r.1 * n.1 - lead, r.0 * along.0 + r.1 * along.1);
            STANDOFF + FIELD_IN_BAND_MAX * 2.0 * dep < d
                && d < STANDOFF + 2.0 * dep
                && t.abs() < lat
        }) {
            stopped[3] += 1;
            continue;
        }
        // ...AND NO PART OF THE FIELD PAST THAT DIP IN IT (449 T435): a margin shorter than the band leaves the band's ends past
        // its own corners, and the field's next edge, rising, crossed a band's end with no corner of the field inside it - 574 of
        // 41,000 sweep rolls had the paddy in the band past the tenth, up to 44 ft into it (measured 2026-11-25, the whole-area
        // `seat_on_field` check); with the band's corners asked, one still had a field corner a foot past the band's end, its
        // edges reaching 16 ft in - so the band past the dip is asked whole: a corner of it on the field, or an edge of the field
        // across a side of it
        let held = [
            band_pt(STANDOFF + FIELD_IN_BAND_MAX * 2.0 * dep, -1.0),
            band_pt(STANDOFF + FIELD_IN_BAND_MAX * 2.0 * dep, 1.0),
            band_pt(STANDOFF + 2.0 * dep, 1.0),
            band_pt(STANDOFF + 2.0 * dep, -1.0),
        ];
        // each edge of the field's outline asked by its box first, its four sides only of an edge whose box meets the band's
        let m = inp.outline.len();
        let (lo, hi) = (
            held.iter()
                .fold((f64::MAX, f64::MAX), |b, p| (b.0.min(p.0), b.1.min(p.1))),
            held.iter()
                .fold((f64::MIN, f64::MIN), |b, p| (b.0.max(p.0), b.1.max(p.1))),
        );
        refusal += m as u64;
        if held.iter().any(|&p| ground.outline.inside(p, &mut refusal))
            || (0..m).any(|i| {
                let (a, b) = (inp.outline[i], inp.outline[(i + 1) % m]);
                if a.0.max(b.0) < lo.0
                    || a.0.min(b.0) > hi.0
                    || a.1.max(b.1) < lo.1
                    || a.1.min(b.1) > hi.1
                {
                    return false;
                }
                refusal += 4;
                (0..4).any(|k| super::exit::seg_seg(a, b, held[k], held[(k + 1) % 4]) == 0.0)
            })
        {
            stopped[3] += 1;
            continue;
        }
        if ground.reeds.iter().any(|r| r.inside(center, &mut refusal)) {
            stopped[4] += 1;
            continue;
        }
        let wet = pts
            .iter()
            .filter(|&&p| ground.reeds.iter().any(|r| r.inside(p, &mut refusal)))
            .count() as f64
            / pts.len() as f64;
        let back = [
            band_pt(0.0, -0.5 * dep / lat.max(1e-9)),
            band_pt(BACK_DEPTHS * dep, -0.5 * dep / lat.max(1e-9)),
            band_pt(BACK_DEPTHS * dep, 0.5 * dep / lat.max(1e-9)),
            band_pt(0.0, 0.5 * dep / lat.max(1e-9)),
        ];
        let foul = ground.back_share(&back, &mut refusal);
        if foul > BACK_FOUL_MAX {
            stopped[5] += 1;
            continue;
        }
        let rel = unit(cen, mid);
        let mut score = WEIGHTS.wind * (n.0 * inp.wind.0 + n.1 * inp.wind.1)
            - WEIGHTS.upslope * (rel.0 * inp.fall.0 + rel.1 * inp.fall.1)
            - WEIGHTS.reeds * wet
            - WEIGHTS.belt * off;
        if !inp.plots.is_empty() {
            let hem = ground.hem(band_pt(0.0, 0.0), 2.0 * dep, &mut scoring);
            score -= WEIGHTS.hem * (1.0 - hem / (2.0 * dep)).max(0.0) + WEIGHTS.back * foul;
        }
        let on_brook = SAMPLE_DEPTHS
            .iter()
            .flat_map(|&(k, ft)| BROOK_ALONG.iter().map(move |&t| band_pt(k * dep + ft, t)))
            .filter(|&q| ground.brook.near(q, inp.fall, BROOK_REACH, &mut scoring) < BROOK_REACH)
            .count() as f64
            / (SAMPLE_DEPTHS.len() * BROOK_ALONG.len()) as f64;
        scoring += 6;
        let frame = Frame {
            center,
            along,
            out: n,
            band: (lat, dep),
            anchor: mid,
            offwind: n.0 * inp.wind.0 + n.1 * inp.wind.1 < inp.back_min_dot,
        };
        kept.push((score, on_brook, tier, frame));
    }
    tally(counts, "test@refusals", refusal);
    tally(counts, "test@score", scoring);
    tally(counts, "candidate@margins", kept.len() as u64);
    // ONE RANKING, BEST FIRST: tier by tier, each by score, the brook's share the tie-break, then the order met (a stable sort)
    kept.sort_by(|a, b| {
        a.2.cmp(&b.2)
            .then(b.0.total_cmp(&a.0))
            .then(a.1.total_cmp(&b.1))
    });
    let n = kept.len() as u64;
    tally(
        counts,
        "test@ranking",
        n * u64::from(64 - n.leading_zeros()),
    );
    tally(counts, "candidate@margins_refused", stopped.iter().sum());
    (kept.into_iter().map(|k| k.3).collect(), stopped)
}
