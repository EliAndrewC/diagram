//! One caption's seat (feature 449 T202; `specs/449-rust-codebase/derivations/T198-placer.md`, "The algorithm"): tried in the order
//! 0242 ranks the places, each rule asked before the caption is placed, and nothing placed and then moved -
//!
//! 1. on its feature, where the block fits the feature's box: over the middle, and failing that the nearest free place to the middle
//!    inside the box, swept outward in the ranked directions;
//! 2. the usual gap: the eight ranked places half the letter height off the feature's drawn box (out to its outline's stroke), the first
//!    clean one that stands nearer its own feature than any other;
//! 3. past the usual gap: a sweep outward from 1.5 gaps off that drawn box per ranked direction, all eight a grid cell at a time, each direction's first
//!    free offset read off the intervals its obstacles cover; the nearest wins, rank breaking ties, and a leader past twice the gap;
//! 4. no clean place within reach: the place that covers least, the highest ranked among equals (cuts into two then three lines are
//!    tried at the usual gap, where one line clears none of its places).
//!
//! All of it in the feature's own frame (its angle), so the ranked places are read as the words read.
//!
//! Research: the caption's seat - research/questions/0242-labels-on-maps-cartographic-label-placement.drawing.html: on its feature where it fits, else beside it at the ranked places stepping outward, the nearer free place winning; covering least where nothing is free

#![expect(
    clippy::many_single_char_names,
    reason = "geometry's points, boxes and sizes as the derivation names them: a, b, c, d, p, q, w, h"
)]

use super::captions::{drawn_half, Caption, PITCH_EM};
use super::geom::{bbox, block, grow, holds, quad_gap, turn, Bx, Pt, EPS};
use super::index::{band, covers, near, Index, Met, Own, Stance, Weight};
use super::leader::leader_span;
use super::wrap::cut;
use super::Shape;
use crate::work_counts::count;

mod sweep;

/// The eight places beside a feature, in the order readers ranked them: above, below, right, upper right, lower right, left, upper left,
/// lower left (as `(x, y)` steps in the feature's frame, y down).
///
/// Research: the ranked places - research/questions/0242-labels-on-maps-cartographic-label-placement.drawing.html: directly above, directly below, to its right, upper right, lower right, to its left, upper left, lower left (the readers' study)
pub const RANKS: [(i8, i8); 8] = [
    (0, -1),
    (0, 1),
    (1, 0),
    (1, -1),
    (1, 1),
    (-1, 0),
    (-1, -1),
    (-1, 1),
];

/// Where the sweep past the usual gap starts, in gaps off the feature: past the usual gap by at least half a gap, so a place the
/// nearness test refused is not taken again a hair further out.
///
/// Research: the sweep's start - GUESS research/questions/0242-labels-on-maps-cartographic-label-placement.drawing.html: 1.5 gaps; the page fixes no step ("a step further out"), and started at one gap 27 of the six pool sheets' 65 swept captions sat within a quarter gap of the usual one, dodging the nearness test (the derivation's assumption 5)
pub const SWEEP_START_GAPS: f64 = 1.5;

/// How far the sweep reaches, in gaps, before the cover-least place is taken.
///
/// Research: the sweep's reach - GUESS: 96 gaps (about 450 px, 150 ft, nine chunks); the page fixes no reach, and no swept caption of the six pool sheets came near it, the farthest stopping in its fifth chunk (the derivation's assumption 5)
pub const SWEEP_REACH_GAPS: f64 = 96.0;

/// How far one sweep chunk reaches, in px: one grid cell.
///
/// Research: the sweep's chunk - NONE: one grid cell (48 px), the index's own unit, measured within 1.14x of seven other schedules (the derivation's "The sweep's chunk"), a search's grain deciding no seat
pub const CHUNK_PX: f64 = super::index::CELL_PX;

/// The farthest a caption stands from its feature with no leader, in gaps.
///
/// Research: no leader within twice the gap - research/questions/0330-how-a-leader-line-ties-a-caption-to-its-feature.drawing.html: a caption more than twice the usual gap from its feature is tied to it by a leader line
pub const LEADER_PAST_GAPS: f64 = 2.0;

/// How many of a loose feature's parts are tried, nearest the middle first, for a place at the usual gap.
///
/// Research:
///     beside a part - DEVIATION research/questions/0242-labels-on-maps-cartographic-label-placement.drawing.html: the page seats a block named among loose parts beside the smallest box holding them all; loose parts are tried one by one instead, on and beside each part's own box, nearest the middle of them all first - because the box of parts scattered across a sheet spans the compound, and a name beside it names nothing (`captions::members`)
///     the parts tried - GUESS research/questions/0242-labels-on-maps-cartographic-label-placement.drawing.html: four; the page records the four tries as a guess, and four tries of eight places each bound the work while finding a free place beside one of a pool sheet's scattered fire-water tubs
pub const MEMBERS_TRIED: usize = 4;

/// How a caption came to its seat.
#[derive(Clone, Copy, Debug, PartialEq)]
pub enum How {
    /// On its feature, this far from its middle.
    Inside(f64),
    /// Beside it at the usual gap, at this rank.
    Gap(usize),
    /// Past the usual gap at this offset (px), at this rank.
    Swept(f64, usize),
    /// Where it covers least: the weight it covers.
    CoverLeast(f64),
}

impl How {
    /// How far from the feature's middle (inside) or box (swept) the caption stands, where that is the measure of its place.
    #[must_use]
    pub fn offset(self) -> Option<f64> {
        match self {
            How::Inside(d) | How::Swept(d, _) => Some(d),
            How::Gap(_) | How::CoverLeast(_) => None,
        }
    }
}

/// A caption's seat: its block's center and size, its angle, the lines its head is drawn in (its declared ones unless cut), and its
/// leader.
#[derive(Clone, Debug, PartialEq)]
pub struct Seat {
    pub center: Pt,
    pub w: f64,
    pub h: f64,
    pub angle: f64,
    /// The head element's lines where they were cut; `None` keeps every element's declared lines.
    pub cut: Option<Vec<String>>,
    pub leader: Option<(Pt, Pt)>,
    pub how: How,
}

/// A layout tried: its width, height and the head's cut lines (`None` the declared block).
type Layout = (f64, f64, Option<Vec<String>>);

/// The middle of a box.
fn mid(b: Bx) -> Pt {
    (f64::midpoint(b.0, b.2), f64::midpoint(b.1, b.3))
}

/// The center, in the feature's frame, of a `w` x `h` block at offset `d` off the feature's box in direction `r`: each stepped axis
/// `d` clear of the box's side, each still one on the box's middle.
#[must_use]
pub fn seat_center(fb: Bx, (w, h): (f64, f64), r: (i8, i8), d: f64) -> Pt {
    let m = mid(fb);
    let at = |step: i8, lo: f64, hi: f64, c: f64, size: f64| match step {
        0 => c,
        1 => hi + d + size / 2.0,
        _ => lo - d - size / 2.0,
    };
    (at(r.0, fb.0, fb.2, m.0, w), at(r.1, fb.1, fb.3, m.1, h))
}

/// The offsets `d` at which a `w` x `h` block centered on `c0 + d * r` overlaps the box `o` (all in the feature's frame), open at both
/// ends; `None` where it never does.
#[must_use]
pub fn interval(c0: Pt, (w, h): (f64, f64), r: (i8, i8), o: Bx) -> Option<(f64, f64)> {
    let (mut lo, mut hi) = (f64::NEG_INFINITY, f64::INFINITY);
    for (step, c, size, o0, o1) in [(r.0, c0.0, w, o.0, o.2), (r.1, c0.1, h, o.1, o.3)] {
        let (a, b) = (o0 - c - size / 2.0 + EPS, o1 - c + size / 2.0 - EPS);
        match step {
            0 => {
                if !(a < 0.0 && 0.0 < b) {
                    return None;
                }
            }
            1 => {
                lo = lo.max(a);
                hi = hi.min(b);
            }
            _ => {
                lo = lo.max(-b);
                hi = hi.min(-a);
            }
        }
    }
    (lo < hi).then_some((lo, hi))
}

/// Is an angle level?
fn level(deg: f64) -> bool {
    deg.abs() < 1e-12
}

/// The placer's state over one sheet: the shapes and the grid.
pub struct Placer<'a> {
    pub shapes: &'a [Shape],
    pub ix: Index,
}

/// A caption's frame: its angle and its feature's box in that frame.
struct Frame {
    angle: f64,
    fb: Bx,
}

impl Frame {
    /// The block's four corners on the sheet, for a center in the frame.
    fn quad(&self, c: Pt, w: f64, h: f64) -> [Pt; 4] {
        block(turn(c, self.angle), w, h, self.angle)
    }

    /// A box in the frame, as the sheet box that holds it.
    fn sheet(&self, b: Bx) -> Bx {
        if level(self.angle) {
            b
        } else {
            bbox(&[(b.0, b.1), (b.2, b.1), (b.2, b.3), (b.0, b.3)].map(|p| turn(p, self.angle)))
        }
    }
}

impl Placer<'_> {
    fn in_view(&self, quad: &[Pt; 4]) -> bool {
        holds(self.ix.view, bbox(quad))
    }

    /// What a block covers, in buildings (0: clean) - every entry its box meets tested against its true outline, each feature counted
    /// once.
    ///
    /// Research: a feature counted once - research/questions/0242-labels-on-maps-cartographic-label-placement.drawing.html: a road or stream crossed counts as half a building, and "crossing one is better than crossing two" - what is weighed is the features covered, so the drawn elements of one tagged feature (a road's bed and the dashed texture over it, a board's footing, frame and rail) count as that feature once, and an untagged shape as itself (feature 449 T209: one road drawn as two paths weighed a whole building, and a bounty board's name was led across the notice board beside it rather than set across that road)
    fn covered(&mut self, quad: &[Pt; 4], own: &Own<'_>) -> f64 {
        let b = bbox(quad);
        let found = self.ix.query(b, "covered");
        // each feature once: its tagged group's, or an untagged shape's own
        let mut hit: Vec<(bool, usize)> = Vec::new();
        let mut total = 0.0;
        for id in found {
            let e = &self.ix.entries[id as usize];
            if !near(b, e) {
                continue;
            }
            let stance = own.stance(&self.ix, e);
            let feature = e.shape.map(|i| match self.shapes[i].group {
                0 => (false, i),
                g => (true, g),
            });
            if covers(quad, e, stance, (own.region, own.stack))
                && feature.is_none_or(|f| !hit.contains(&f))
            {
                hit.extend(feature);
                total += e.weight.of();
            }
        }
        total
    }

    /// Does a block at the usual gap stand nearer its own feature than any other: no other drawn thing within a gap of it?
    ///
    /// Research: nearer its own - research/questions/0242-labels-on-maps-cartographic-label-placement.drawing.html: a caption at the usual gap must stand nearer its own feature than any other; one a step out need not (the page's DEVIATION)
    fn nearest_own(&mut self, quad: &[Pt; 4], own: &Own<'_>, gap: f64) -> bool {
        let b = grow(bbox(quad), gap);
        for id in self.ix.query(b, "nearest_own") {
            let e = &self.ix.entries[id as usize];
            if e.weight == Weight::Text
                || e.shape.is_none()
                || !near(b, e)
                || own.stance(&self.ix, e) != Stance::Ink
            {
                continue;
            }
            count("shape_distance@nearest_own", 1);
            if quad_gap(quad, &e.poly, e.convex) < gap - EPS {
                return false;
            }
        }
        true
    }

    /// The layout the inside seat tries: the declared block where it fits the feature's box, else the first of two then three lines
    /// that does.
    ///
    /// Research: a wrap to fit - research/questions/0242-labels-on-maps-cartographic-label-placement.drawing.html: a feature large enough to hold its name is named on itself, its words breaking across two then three lines where one line would not fit the feature's box (DEVIATION from the derivation's reading A, which tried a cut only where nothing cleared: the river of a pool sheet holds its name on two lines, not one)
    pub(crate) fn inside_layout(cap: &Caption, fb: Bx) -> Option<Layout> {
        let fits = |w: f64, h: f64| w <= fb.2 - fb.0 + EPS && h <= fb.3 - fb.1 + EPS;
        if fits(cap.w, cap.h) {
            return Some((cap.w, cap.h, None));
        }
        if !cap.cuttable() {
            return None;
        }
        (2..=3).find_map(|k| {
            let (w, h, lines) = cut_layout(cap, k)?;
            fits(w, h).then_some((w, h, lines))
        })
    }

    /// The first step, on the feature: its middle, then a free place on it - a row of the block's height at a time, from the middle row outward (above
    /// before below), each row's free stretches read off the intervals its obstacles cover, the first row holding one taking the free
    /// place nearest the middle along it.
    ///
    /// Research:
    ///     elsewhere on it - CONVENTION: 0242 names an area "over its middle when that is free" and is silent on where the name goes when the middle is taken; this placer fills that silence with the nearest free place on the feature, before the caption goes beside it - a court or a river holds its name off its middle; the derivation's assumption 2 priced the reading that searches elsewhere inside as about neutral
    ///     the nearest row first - GUESS research/questions/0242-labels-on-maps-cartographic-label-placement.drawing.html: the first row from the middle holding a free place wins, its place nearest the middle along it - "over its middle" read row by row; a free place nearer in a straight line on a farther row is not sought (that search read every row of a pool sheet's cluttered courts, 2.1x the sheet's budget, measured 2026-11-19)
    ///     the row step - GUESS research/questions/0242-labels-on-maps-cartographic-label-placement.drawing.html: rows one block's height apart, so the rows tile the feature, the last row on each side at the feature's edge (a kitchen two blocks tall had only its middle row tried, its free edge rows missed: observed 2026-11-19); a free band as tall as the block straddling two rows is missed, and the page fixes no step
    fn inside(
        &mut self,
        cap: &Caption,
        fr: &Frame,
        own: &Own<'_>,
        (hold, hb): (usize, Bx),
    ) -> Option<(Pt, Layout, f64)> {
        let (w, h, lines) = Self::inside_layout(cap, hb)?;
        let m = mid(hb);
        let outline = &self.shapes[hold].poly;
        let boxy = outline.len() == 4;
        let on_it = |c: Pt| boxy || super::geom::inside(turn(c, fr.angle), outline);
        count("seat@inside", 1);
        let quad = fr.quad(m, w, h);
        if on_it(m) && self.in_view(&quad) && self.covered(&quad, own) <= 0.0 {
            return Some((m, (w, h, lines), 0.0));
        }
        // inside the outline's stroke, so a row at the edge does not lie on it
        let inset = if own.on_outline {
            0.0
        } else {
            self.shapes[hold].edge
        };
        let mut xr = (hb.0 + inset + w / 2.0, hb.2 - inset - w / 2.0);
        let mut yr = (hb.1 + inset + h / 2.0, hb.3 - inset - h / 2.0);
        if level(fr.angle) {
            let v = self.ix.view;
            xr = (xr.0.max(v.0 + w / 2.0), xr.1.min(v.2 - w / 2.0));
            yr = (yr.0.max(v.1 + h / 2.0), yr.1.min(v.3 - h / 2.0));
        }
        if xr.0 > xr.1 + EPS || yr.0 > yr.1 + EPS {
            return None;
        }
        let step = h.max(1.0);
        let mut k = 0.0_f64;
        // each side's last row, so a row past the feature's edge is tried once, at the edge
        let first = m.1.clamp(yr.0, yr.1);
        let mut last = [first, first];
        while k * step < (m.1 - yr.0).max(yr.1 - m.1) + step {
            let rows: &[usize] = if k == 0.0 { &[0] } else { &[0, 1] };
            for &side in rows {
                let sign = if side == 0 { -1.0 } else { 1.0 };
                let y = (m.1 + sign * k * step).clamp(yr.0, yr.1);
                if k > 0.0 && (y - last[side]).abs() < EPS {
                    continue;
                }
                last[side] = y;
                let dy = (y - m.1).abs();
                let Some(x) = self.free_in_row(fr, own, (w, h), (y, xr, m.0)) else {
                    continue;
                };
                let c = (x, y);
                if on_it(c) && (level(fr.angle) || self.in_view(&fr.quad(c, w, h))) {
                    return Some((c, (w, h, lines), (x - m.0).hypot(dy)));
                }
            }
            k += 1.0;
        }
        None
    }

    /// The box, in the frame, an obstacle presents to a search's strip (`strip`, a box in the frame): on a level frame an upright box its
    /// own box; any other outline - a concave one, a slanting band such as a leader, or any outline on a turned frame - its part within
    /// the strip, the outline turned into the frame first (`exact_test`, one an edge clipped).
    ///
    /// Research: an outline's part in the strip - NONE: an exact reading of the outline's extent within the strip, in the caption's own frame, deciding nothing; read by its box, a garden reaching round a house blocked every place beside it, and a slanting leader the whole granary it crossed a corner of (observed 2026-11-19), and on a turned frame every outline's box covered places beside it its ink does not reach
    fn met_box(fr: &Frame, poly: &[Pt], convex: bool, strip: Bx) -> Bx {
        let flat = level(fr.angle);
        let boxy = poly.len() == 4
            && super::geom::ring(poly)
                .all(|(a, b)| (a.0 - b.0).abs() < EPS || (a.1 - b.1).abs() < EPS);
        if flat && convex && boxy {
            return bbox(poly);
        }
        count("exact_test@met_box", poly.len() as u64);
        let turned: Vec<Pt>;
        let poly = if flat {
            poly
        } else {
            turned = poly.iter().map(|&p| turn(p, -fr.angle)).collect();
            &turned
        };
        // no part within the strip: a box no block meets
        super::geom::clip_box(poly, strip).unwrap_or((
            f64::INFINITY,
            f64::INFINITY,
            f64::NEG_INFINITY,
            f64::NEG_INFINITY,
        ))
    }

    /// The free center nearest `mx` along one row (center height `y`, centers between `xr`): the row read once, its obstacles'
    /// intervals sorted, and its free stretches walked.
    fn free_in_row(
        &mut self,
        fr: &Frame,
        own: &Own<'_>,
        (w, h): (f64, f64),
        (y, xr, mx): (f64, (f64, f64), f64),
    ) -> Option<f64> {
        count("seat@inside", 1);
        let (top, bottom) = (y - h / 2.0, y + h / 2.0);
        let local = (xr.0 - w / 2.0, top, xr.1 + w / 2.0, bottom);
        let strip = fr.sheet(local);
        let mut ivs: Vec<(f64, f64)> = Vec::new();
        for id in self.ix.query(strip, "inside") {
            let e = &self.ix.entries[id as usize];
            if !near(strip, e) || own.stance(&self.ix, e) == Stance::Skip {
                continue;
            }
            let o = Self::met_box(fr, &e.reach((own.region, own.stack)), e.convex, local);
            count("sweep_interval@inside", 1);
            if o.1 < bottom - EPS && o.3 > top + EPS && o.0 - w / 2.0 < xr.1 && o.2 + w / 2.0 > xr.0
            {
                ivs.push((o.0 - w / 2.0 + EPS, o.2 + w / 2.0 - EPS));
            }
        }
        let n = ivs.len();
        if n > 0 {
            #[expect(
                clippy::cast_possible_truncation,
                clippy::cast_sign_loss,
                clippy::cast_precision_loss,
                reason = "a small sort's comparisons"
            )]
            let sorting = (n as f64 * (n as f64 + 1.0).log2().ceil().max(1.0)) as u64;
            count("sweep_compare@free_in_row", sorting);
        }
        ivs.sort_by(|a, b| a.0.total_cmp(&b.0));
        nearest_free(&ivs, xr, mx)
    }

    /// The first step's passes: clear of the feature's own lines, then across them where they were met, then - a region holding named
    /// rooms that were met - across the rooms; each on its filled outline, with what lies beneath it hidden. `last`: the one pass after
    /// every place at the usual gap, across the outline's own stroke.
    ///
    /// Research: the passes on its feature - CONVENTION: a place on the feature clear of its own inner lines first, then one across them, then - a region holding named parts it met - one across those parts, a line's height off their names; and only after every place at the usual gap, one across the outline's own stroke; 0242 says only "over its middle when that is free", so the cleanest place on the feature is sought before a busier one
    fn on_it(
        &mut self,
        cap: &Caption,
        fr: &Frame,
        own: &Own<'_>,
        last: bool,
    ) -> Option<(Pt, Layout, f64)> {
        let holders: Vec<(usize, Bx, Option<Bx>)> = match cap.holder {
            Some((h, hb)) => vec![(h, hb, cap.fsheet)],
            None => cap
                .members
                .iter()
                .take(MEMBERS_TRIED)
                .map(|&(h, lb, sb)| (h, lb, Some(sb)))
                .collect(),
        };
        for (hold, hb, sb) in holders {
            let s = &self.shapes[hold];
            let base = Own {
                under: s.filled.then_some(s.at),
                fbox_sheet: sb,
                ..*own
            };
            if last {
                // the feature's very last try, after every place at the usual gap: across its own outline's stroke
                let found = self.inside(
                    cap,
                    fr,
                    &Own {
                        on_outline: true,
                        ..base
                    },
                    (hold, hb),
                );
                if found.is_some() {
                    return found;
                }
                continue;
            }
            own.met.own_lines.set(false);
            own.met.held_named.set(false);
            let mut found = self.inside(
                cap,
                fr,
                &Own {
                    clear_own_lines: true,
                    ..base
                },
                (hold, hb),
            );
            if found.is_none() && own.met.own_lines.get() {
                found = self.inside(cap, fr, &base, (hold, hb));
            }
            if found.is_none() && own.met.held_named.get() {
                found = self.inside(
                    cap,
                    fr,
                    &Own {
                        region: true,
                        stack: super::captions::PITCH_EM * cap.elems[0].size,
                        ..base
                    },
                    (hold, hb),
                );
            }
            if found.is_some() {
                return found;
            }
        }
        None
    }

    /// The second step, the eight ranked places at the usual gap, for a block `w` x `h`: the first clean one that stands nearer its own feature; every place's cover kept for
    /// the last resort.
    fn at_gap(
        &mut self,
        cap: &Caption,
        fr: &Frame,
        own: &Own<'_>,
        scored: &mut Vec<(f64, usize, Pt)>,
        (w, h): (f64, f64),
    ) -> Option<(Pt, usize)> {
        for (rank, &r) in RANKS.iter().enumerate() {
            let c = seat_center(fr.fb, (w, h), r, cap.gap);
            count("seat@at_gap", 1);
            let quad = fr.quad(c, w, h);
            if !self.in_view(&quad) {
                continue;
            }
            let cover = self.covered(&quad, own);
            scored.push((cover, rank + 1, c));
            if cover <= 0.0 && self.nearest_own(&quad, own, cap.gap) {
                return Some((c, rank));
            }
        }
        None
    }

    /// One caption seated, its block and leader filed so no later caption covers them.
    ///
    /// Research:
    ///     never left off - research/questions/0242-labels-on-maps-cartographic-label-placement.drawing.html: a caption the map calls for is never left off; on a sheet with no free ground it goes where it covers the least
    ///     cover least, highest ranked - research/questions/0242-labels-on-maps-cartographic-label-placement.drawing.html: failing empty ground, the place that covers the least and lies highest in the order, a road or stream counting half a building
    ///     wrap where it clears - research/questions/0242-labels-on-maps-cartographic-label-placement.drawing.html: one line if that clears, else the first of two then three that does, else back to one; the wrapped block takes the single line's ranked place and its angle, its near edge at the usual gap off the feature's edge (its center: the next claim) - tried at the usual gap where one line clears none of its places (DEVIATION from the derivation's reading A, which tried cuts only at the last resort: a pool sheet's weighing floor, its one line too wide for any place by its crowded floor, was swept 211 px onto another court)
    ///     the wrapped block's center - DEVIATION research/questions/0242-labels-on-maps-cartographic-label-placement.drawing.html: the page has a wrapped caption keep the single line's center; here it keeps the single line's ranked place and angle and stands, at its own size, its near edge the usual gap off the feature's edge, so its center moves - the single line had no free place to keep, and a block taller than the line kept on that line's center above or below its feature would reach into the feature
    ///     a leader filed - CONVENTION: a drawn leader is filed as a thin band at a caption's weight, so no later caption is set across it while any other choice exists - a name lying across a leader blurs which name the leader ties to its feature
    ///     air between captions - GUESS research/questions/0242-labels-on-maps-cartographic-label-placement.drawing.html: a seated caption is filed with its usual gap (half its letter height) of air on every side, so no later caption touches it - two captions edge to edge read as one name (observed 2026-11-19 on a pool sheet: "INNER COURT" and "RESIDENCE" run together); the page fixes the gap only off a caption's own feature
    ///     its writes - NONE: six fields a caption written (center x and y, anchor, angle, lines, leader), the derivation's `write`
    pub fn seat(&mut self, cap: &Caption) -> Seat {
        let fr = Frame {
            angle: cap.angle,
            fb: cap.fbox.unwrap_or_default(),
        };
        let parts = cap.parts.clone();
        let met = Met::default();
        let own = Own {
            parts: &parts,
            fbox_sheet: cap.fsheet,
            ground: cap.ground,
            at: cap.at,
            clear_own_lines: false,
            under: None,
            region: false,
            met: &met,
            subtree: cap.subtree,
            stack: 0.0,
            on_outline: false,
        };
        let mut seat = self.search(cap, &fr, &own);
        if let How::Swept(d, _) = seat.how {
            if d > LEADER_PAST_GAPS * cap.gap {
                seat.leader = leader_span(
                    seat.center,
                    (seat.w, seat.h, seat.angle),
                    self.shapes,
                    &cap.parts,
                )
                .map(|t| self.led(t, cap.gap, &own));
            }
        }
        count("write@seat", 6);
        // filed with the usual gap of air around it, so no later caption runs into it
        let quad = block(
            seat.center,
            seat.w + 2.0 * cap.gap,
            seat.h + 2.0 * cap.gap,
            seat.angle,
        );
        self.ix
            .file(None, quad.to_vec(), Weight::Text, (0.0, 1, false));
        let filed = self.ix.entries.len() - 1;
        self.ix.entries[filed].core = block(seat.center, seat.w, seat.h, seat.angle).to_vec();
        if let Some((a, b)) = seat.leader {
            self.ix.file(
                None,
                band(a, b, super::index::MIN_HALF_PX),
                Weight::Text,
                (0.0, 1, false),
            );
        }
        seat
    }

    /// One caption's seat in 0242's order: on its feature, beside it at the usual gap, a step further out, and failing free ground the
    /// place that covers least.
    ///
    /// Research:
    ///     the caption's seat - research/questions/0242-labels-on-maps-cartographic-label-placement.drawing.html: on its feature where it fits, else beside it at the ranked places stepping outward, the nearer free place winning; only when no free ground is left does it cover something
    ///     a leader's seat not free - CONVENTION: a swept seat whose leader would cross another building (`leader_crosses`, the leader convention) is not free ground - its leader lies across that building as words over it would - so where the only seats left within reach are such seats, no free ground is left
    ///     covering least - research/questions/0242-labels-on-maps-cartographic-label-placement.drawing.html: failing empty ground, the place that covers the least and lies highest in the order, a road or stream counting half a building - the places at the usual gap, and the nearest leader-crossing seat weighed as one building covered, whatever its leader crosses
    ///     a leader's seat at equal cover - CONVENTION: between the leader-crossing seat and a place at the usual gap that covers a building or more, the leader's seat is kept, its words over nothing; 0242's order ranks places at the gap and a step out, and says nothing of a leader across a building set against words over one (observed 2026-11-19 on the pool sheets: two latrines and an altar kept on their leaders rather than written over a building, while a bounty board's name, its only free seats led across the notice board, was set on the road above its board)
    fn search(&mut self, cap: &Caption, fr: &Frame, own: &Own<'_>) -> Seat {
        let done = |c: Pt, (w, h, cut): Layout, how: How| Seat {
            center: turn(c, fr.angle),
            w,
            h,
            angle: fr.angle,
            cut,
            leader: None,
            how,
        };
        if let Some((c, layout, d)) = self.on_it(cap, fr, own, false) {
            return done(c, layout, How::Inside(d));
        }
        let mut scored: Vec<(f64, usize, Pt)> = Vec::new();
        if let Some((_, hb)) = cap
            .holder
            .filter(|h| Self::inside_layout(cap, h.1).is_some())
        {
            let m = mid(hb);
            let quad = fr.quad(m, cap.w, cap.h);
            if self.in_view(&quad) {
                let cover = self.covered(&quad, own);
                scored.push((cover, 0, m));
            }
        }
        // beside the feature - or, its parts loose, beside the parts nearest the middle of them all, then swept from the nearest - each
        // off its drawn edge, its outline's stroke included, as the nearness test measures it
        let beside: Vec<(Bx, Option<Bx>)> = if cap.members.is_empty() {
            vec![(cap.dbox.unwrap_or(fr.fb), cap.fsheet)]
        } else {
            cap.members
                .iter()
                .take(MEMBERS_TRIED)
                .map(|&(p, lb, sb)| (grow(lb, drawn_half(&self.shapes[p])), Some(sb)))
                .collect()
        };
        for &(fb, sb) in &beside {
            let frm = Frame {
                angle: fr.angle,
                fb,
            };
            let ownm = Own {
                fbox_sheet: sb,
                ..*own
            };
            if let Some((c, rank)) = self.at_gap(cap, &frm, &ownm, &mut scored, (cap.w, cap.h)) {
                return done(c, (cap.w, cap.h, None), How::Gap(rank));
            }
        }
        // where one line clears no place at the usual gap, the first of two then three lines that does
        if cap.cuttable() {
            let frm = Frame {
                angle: fr.angle,
                fb: beside[0].0,
            };
            let ownm = Own {
                fbox_sheet: beside[0].1,
                ..*own
            };
            for k in 2..=3 {
                let Some((w, h, lines)) = cut_layout(cap, k) else {
                    break;
                };
                if let Some((c, rank)) = self.at_gap(cap, &frm, &ownm, &mut Vec::new(), (w, h)) {
                    return done(c, (w, h, lines), How::Gap(rank));
                }
            }
        }
        // no clean place beside it: a name as wide as its feature is named on it, across its own outline, before it is led away
        if let Some((c, layout, d)) = self.on_it(cap, fr, own, true) {
            return done(c, layout, How::Inside(d));
        }
        let frm = Frame {
            angle: fr.angle,
            fb: beside[0].0,
        };
        let ownm = Own {
            fbox_sheet: beside[0].1,
            ..*own
        };
        if let Some((c, d, rank, crossed)) = self.beyond(cap, &frm, &ownm) {
            // a seat led across another building is not free: it weighs that building, and a place at the usual gap covering less wins
            let cheaper = crossed && scored.iter().any(|sc| sc.0 < Weight::Block.of() - EPS);
            if !cheaper {
                return done(c, (cap.w, cap.h, None), How::Swept(d, rank));
            }
        }
        // 4. the last resort: where it covers least, highest ranked, on one line (cuts having been tried at the usual gap)
        let (cover, _, c) = scored
            .into_iter()
            .min_by(|a, b| a.0.total_cmp(&b.0).then(a.1.cmp(&b.1)))
            .unwrap_or((f64::INFINITY, 0, self.clamped(fr, cap)));
        done(c, (cap.w, cap.h, None), How::CoverLeast(cover))
    }

    /// The feature's middle, moved the least that keeps the block on the sheet: the last resort's place when no ranked place is on it.
    ///
    /// Research: no place in view - CONVENTION: a caption none of whose ranked places lies on the sheet is set on its feature's middle, moved the least that keeps its block on the sheet - 0242 never takes a place off the edge and never leaves a caption off, and is silent on where it goes when both bind; its own feature's middle is the place that most plainly names it
    fn clamped(&self, fr: &Frame, cap: &Caption) -> Pt {
        let m = turn(mid(fr.fb), fr.angle);
        let b = bbox(&block(m, cap.w, cap.h, fr.angle));
        let v = self.ix.view;
        let shift = |lo: f64, hi: f64, vlo: f64, vhi: f64| {
            if lo < vlo {
                vlo - lo
            } else if hi > vhi {
                vhi - hi
            } else {
                0.0
            }
        };
        let sheet = (
            m.0 + shift(b.0, b.2, v.0, v.2),
            m.1 + shift(b.1, b.3, v.1, v.3),
        );
        turn(sheet, -fr.angle)
    }
}

/// The free point of `span` nearest `mx`, outside every interval of the sorted list (`sweep_compare`, one an interval read).
fn nearest_free(ivs: &[(f64, f64)], span: (f64, f64), mx: f64) -> Option<f64> {
    let mut best: Option<f64> = None;
    let mut take = |a: f64, b: f64| {
        if a <= b {
            let x = mx.clamp(a, b);
            if best.is_none_or(|v| (x - mx).abs() < (v - mx).abs()) {
                best = Some(x);
            }
        }
    };
    let mut free_from = span.0;
    for &(lo, hi) in ivs {
        count("sweep_compare@nearest_free", 1);
        if hi <= free_from {
            continue;
        }
        if lo >= span.1 {
            break;
        }
        take(free_from, lo);
        free_from = hi;
    }
    take(free_from, span.1);
    best
}

/// A caption's head cut into `k` lines: its block and lines, the width of a character the declared line's own (as the reader measured
/// it).
///
/// Research: the cut block's size - CONVENTION: a cut line's width is its character count times the declared line's average character width, as the reader measured it, and its lines stand 1.15 em apart (`PITCH_EM`), the pitch the caption writer draws them at
#[must_use]
pub fn cut_layout(cap: &Caption, k: usize) -> Option<Layout> {
    let e = &cap.elems[0];
    let text = &e.lines[0];
    #[expect(clippy::cast_precision_loss, reason = "a line's character count")]
    let char_w = e.width / text.chars().count().max(1) as f64;
    let lines = cut(text, k, char_w)?;
    #[expect(clippy::cast_precision_loss, reason = "a line's character count")]
    let w = lines
        .iter()
        .map(|l| l.chars().count() as f64 * char_w)
        .fold(0.0, f64::max);
    #[expect(clippy::cast_precision_loss, reason = "a caption's line count")]
    let h = k as f64 * PITCH_EM * e.size;
    Some((w, h, Some(lines)))
}

#[cfg(test)]
mod tests {
    use super::{interval, nearest_free, seat_center, Frame, Placer, RANKS};

    /// 0242, the true outlines: on a turned frame an outline is read where it meets the strip, not as its whole box in the frame - a
    /// thin band slanting across the frame blocks only the stretch of a row it crosses.
    #[test]
    fn a_turned_frame_reads_the_outline_within_the_strip() {
        let fr = Frame {
            angle: 45.0,
            fb: (0.0, 0.0, 1.0, 1.0),
        };
        // a band along the sheet's x axis: in the frame it runs along y = -x
        let band = [(0.0, -1.0), (100.0, -1.0), (100.0, 1.0), (0.0, 1.0)];
        let row = (-100.0, -10.0, 100.0, -5.0);
        let o = Placer::met_box(&fr, &band, true, row);
        assert!(o.0 > 2.0 && o.2 < 13.0, "{o:?}");
        assert!(o.1 >= -10.0 - 1e-9 && o.3 <= -5.0 + 1e-9, "{o:?}");
        // the strip missing it: a box no block meets
        let o = Placer::met_box(&fr, &band, true, (-100.0, 10.0, -50.0, 20.0));
        assert!(o.0 > o.2, "{o:?}");
        // level, an upright box is its own box
        let lv = Frame {
            angle: 0.0,
            fb: (0.0, 0.0, 1.0, 1.0),
        };
        assert_eq!(
            Placer::met_box(&lv, &band, true, row),
            (0.0, -1.0, 100.0, 1.0)
        );
    }

    /// A place's center steps clear of the feature's box in each ranked direction.
    #[test]
    fn a_place_stands_off_the_box_by_the_offset() {
        let fb = (0.0, 0.0, 10.0, 10.0);
        assert_eq!(seat_center(fb, (4.0, 2.0), RANKS[0], 1.0), (5.0, -2.0));
        assert_eq!(seat_center(fb, (4.0, 2.0), RANKS[2], 1.0), (13.0, 5.0));
        assert_eq!(seat_center(fb, (4.0, 2.0), RANKS[6], 1.0), (-3.0, -2.0));
    }

    /// The offsets a block overlaps a box, in each direction, open at both ends (a touch is no overlap).
    #[test]
    fn an_obstacles_interval_is_where_the_block_meets_it() {
        // a 4 x 2 block stepping right from x = 10 (center 12 at offset 0): a box over x 20..24 is met for offsets 6..14
        let (lo, hi) = interval((12.0, 5.0), (4.0, 2.0), (1, 0), (20.0, 4.0, 24.0, 6.0)).unwrap();
        assert!((lo - 6.0).abs() < 1e-5 && (hi - 14.0).abs() < 1e-5);
        // stepping left from x = -2: a box over x -12..-8 is met for offsets 4..12
        let (lo, hi) = interval((-2.0, 5.0), (4.0, 2.0), (-1, 0), (-12.0, 4.0, -8.0, 6.0)).unwrap();
        assert!((lo - 4.0).abs() < 1e-5 && (hi - 12.0).abs() < 1e-5);
        // a box beside the block's still axis is never met
        assert_eq!(
            interval((12.0, 5.0), (4.0, 2.0), (1, 0), (20.0, 7.0, 24.0, 9.0)),
            None
        );
        // a box behind the block, never reached at a positive offset, gives an interval below zero, and boxes apart none
        assert!(
            interval((12.0, 5.0), (4.0, 2.0), (1, 0), (0.0, 4.0, 2.0, 6.0))
                .unwrap()
                .1
                < 0.0
        );
        assert_eq!(
            interval((0.0, 0.0), (2.0, 2.0), (1, 1), (10.0, -20.0, 12.0, -18.0)),
            None
        );
    }

    /// The free point nearest the middle, outside every interval.
    #[test]
    fn the_free_point_nearest_the_middle() {
        assert_eq!(nearest_free(&[], (0.0, 10.0), 5.0), Some(5.0));
        assert_eq!(nearest_free(&[(3.0, 6.0)], (0.0, 10.0), 5.0), Some(6.0));
        assert_eq!(nearest_free(&[(3.0, 8.0)], (0.0, 10.0), 4.0), Some(3.0));
        assert_eq!(nearest_free(&[(-1.0, 11.0)], (0.0, 10.0), 5.0), None);
        assert_eq!(
            nearest_free(&[(-5.0, -1.0), (2.0, 4.0), (20.0, 30.0)], (0.0, 10.0), 3.5),
            Some(4.0)
        );
    }
}
