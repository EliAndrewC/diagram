//! THE caption placer (feature 449 T151, `labels/placer.py` whole; feature 266): one for every caption. The GM, 2026-09-27: *"I also
//! agree with one placer for all labels"*, adopting the cartographic standard
//! (research/questions/0242-labels-on-maps-cartographic-label-placement.drawing.html). [`place`] takes what a caption NAMES - a point
//! feature's drawn footprint, a line, or an area - and returns where the words go, at what angle, on how many lines, and whether a leader
//! line ties them back. The standard, in the order it decides: NEARER FIRST, the RANKED POSITIONS within a ring, FREE SPACE WINS, and a
//! LEADER for a caption past twice the usual gap, no longer directly beside its feature. The candidates are [`cands`]'.
//!
//! The Python's arithmetic in its order, its candidates in its order and its ties broken as it broke them, so a caption lands where the
//! Python's did wherever the sheet's own geometry is the same (`parse/lockstep_labels.rs` measures the four caption-placing sheets).
//!
//! Research: caption search plumbing - NONE: candidate bookkeeping, geometry and search bounds

#![expect(
    clippy::similar_names,
    reason = "the Python's names, kept so each line reads against its original (x0 and x1, bx0 and by0)"
)]

use super::geom::{
    bbox, centroid, dist, inside, most, nearest_points, poly_gap, rect, seg_closest, BBox, Poly, Pt,
};
use super::obstacles::{Asker, ObstacleIndex, Way};
#[cfg(doc)]
use super::standard::WAY_NOTCH;
use super::standard::{CENTER_ABOVE_BASELINE_EM, CHAR_W_EM, CLEAR_EM, WEIGHT_OBSTACLE};
use crate::py::{half_sum, hypot, max, min};
use crate::work_counts::count;
use l7r_gate_research::Error;

pub mod cands;

use cands::{area_cands, extended_cands, lays_of, line_cands, point_cands, Gen};
pub use cands::{outer_rings, rings, sized_half, Cand, HUG_RING, NUDGE_PX};

/// What a caption names: a point (a feature beside which the caption stands), a line (the caption running along it near `hint`) or an
/// area (an outline the caption lies inside). The Python's `kind` string; any other word was its `ValueError`, which a type rules out.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Kind {
    Point,
    Line,
    Area,
}

/// What a caption names (the Python's `Subject`): its kind, its drawn outline or polyline, its rotation, a line's drawn half-width, the
/// point a line's caption runs near, and whether it is itself a named civic building (FR-014).
#[derive(Debug, Clone, PartialEq)]
pub struct Subject {
    pub kind: Kind,
    pub poly: Vec<Pt>,
    pub angle: f64,
    pub half_width: f64,
    pub hint: Option<Pt>,
    pub civic: bool,
}

impl Subject {
    /// A subject of `kind` and `poly` at `angle`, every other field its default.
    #[must_use]
    pub fn new(kind: Kind, poly: Vec<Pt>, angle: f64) -> Self {
        Self {
            kind,
            poly,
            angle,
            half_width: 0.0,
            hint: None,
            civic: false,
        }
    }
}

/// Where a caption goes: `(x, y)` the anchor `label()` takes - the middle of the first line's baseline, the block turned by `angle` about
/// its own center; `block` that drawn block; `ring` 0 the preferred offset.
#[derive(Debug, Clone, PartialEq)]
pub struct Placement {
    pub x: f64,
    pub y: f64,
    pub angle: f64,
    pub lines: Vec<String>,
    pub block: Vec<Pt>,
    pub ring: usize,
    pub rank: usize,
    pub position: &'static str,
    pub cost: f64,
    pub leader: Option<(Pt, Pt)>,
}

/// The picture's frame `(x0, y0, x1, y1)`.
pub type Frame = BBox;

/// A seat accepted or refused by a strict caller (the board's siter).
pub type Accept<'a> = &'a dyn Fn(&Placement) -> bool;

/// [`place`]'s optional arguments, the Python's keywords: the frame a block may not leave, fixed lines, the width per character, what a
/// leader may not cross, each fixed line's size, whether the fallback runs, strictness, the farthest ring, and a strict caller's test.
#[derive(Clone, Copy)]
pub struct Ask<'a> {
    pub frame: Option<Frame>,
    pub lines: Option<&'a [String]>,
    pub char_w: f64,
    pub leader_index: Option<&'a ObstacleIndex>,
    pub line_sizes: Option<&'a [f64]>,
    pub extended: bool,
    pub strict: bool,
    pub max_ring: Option<usize>,
    pub accept: Option<Accept<'a>>,
}

impl Default for Ask<'_> {
    fn default() -> Self {
        Self {
            frame: None,
            lines: None,
            char_w: CHAR_W_EM,
            leader_index: None,
            line_sizes: None,
            extended: true,
            strict: false,
            max_ring: None,
            accept: None,
        }
    }
}

/// The farthest a nudge carries a seat, with a margin over rounding: a seat blocked by more than this stays blocked under every nudge.
#[must_use]
pub fn nudge_reach() -> f64 {
    f64::from(NUDGE_PX) * 2.0_f64.sqrt() + 1e-3
}

/// The rings a caption takes with no leader: the preferred offset and each step out to twice it (rings 0 and 1, 1 em) -
/// `int(round((2 * PREFERRED_OFFSET_EM - PREFERRED_OFFSET_EM) / RING_STEP_EM)) + 1`.
///
/// Research: no leader within twice the usual gap - research/questions/0242-labels-on-maps-cartographic-label-placement.drawing.html: it may go as far as twice the usual gap with nothing more
pub const LEADERLESS_RINGS: usize = 2;

/// A line subject of fewer than two points refused by name (feature 449 T184; the Python raised its walk's `AssertionError`, or `min()`'s
/// `ValueError` given a hint): a line of one point has no bearing for its caption to run along.
pub const ONE_POINT_LINE: &str =
    "a line subject needs two points: a line of one has no bearing to run along - name it a point";

/// A caption of no size refused by name (feature 449 T184; the Python looped forever, its leader rings never passing the hug): a size
/// of zero, less, or no number has no block to seat.
pub const NO_SIZE: &str =
    "a caption of no size cannot be seated: give its text a font-size above 0";

/// The box of what a caption names, as its record carries it: a point subject's UNROTATED box - its extents in its own frame, about its
/// center - an area's box, or for a LINE the drawn way's width across from where the caption landed.
///
/// Research: the box a caption hugs - CONVENTION: the hug measures to a point subject's unturned extents about its center (conservative), an area's box, a line's drawn width where the caption landed
#[must_use]
pub fn referent_box(subject: &Subject, block: &[Pt]) -> BBox {
    match subject.kind {
        Kind::Point => {
            let a = subject.angle.to_radians();
            let (u, v) = ((a.cos(), a.sin()), (-a.sin(), a.cos()));
            let c = centroid(&subject.poly);
            let su = most(
                subject
                    .poly
                    .iter()
                    .map(|q| ((q.0 - c.0) * u.0 + (q.1 - c.1) * u.1).abs()),
            );
            let sv = most(
                subject
                    .poly
                    .iter()
                    .map(|q| ((q.0 - c.0) * v.0 + (q.1 - c.1) * v.1).abs()),
            );
            (c.0 - su, c.1 - sv, c.0 + su, c.1 + sv)
        }
        Kind::Area => bbox(&subject.poly),
        Kind::Line => {
            let (cx, cy) = centroid(block);
            let q = super::geom::open_edges(&subject.poly)
                .map(|(a, b)| seg_closest((cx, cy), a, b))
                .reduce(|best, c| {
                    if dist(c, (cx, cy)) < dist(best, (cx, cy)) {
                        c
                    } else {
                        best
                    }
                })
                .unwrap_or((cx, cy));
            let h = subject.half_width;
            (q.0 - h, q.1 - h, q.0 + h, q.1 + h)
        }
    }
}

/// A drawn block's record box - the block unturned about its own center, as `_record_label` writes elements [0:4].
#[must_use]
pub fn record_box(block: &[Pt]) -> BBox {
    let (cx, cy) = centroid(block);
    let (hw, hh) = (
        dist(block[0], block[1]) / 2.0,
        dist(block[1], block[2]) / 2.0,
    );
    (cx - hw, cy - hh, cx + hw, cy + hh)
}

/// THE ONE PREDICATE of `label_hugs_its_referent` (feature 287, labels L10): the box-to-box gap between a caption's record box and the box
/// of what it names. The placer never offers a seat past [`HUG_PX`] by it.
///
/// Research: the hug - CONVENTION: no seat past the hug from what it names, measured box to box
#[must_use]
pub fn hug_gap(block: &[Pt], r: BBox) -> f64 {
    let a = record_box(block);
    hypot(
        most([a.0 - r.2, r.0 - a.2, 0.0]),
        most([a.1 - r.3, r.1 - a.3, 0.0]),
    )
}

/// THE ONE PREDICATE of `captions_clear_the_ways_they_stand_on` (feature 287, labels L5): no way comes within its drawn half-width plus
/// [`WAY_NOTCH`] of the block, segment against polygon - the index's own way term ([`ObstacleIndex::score`]), so a curved tread's middle
/// crossing an edge between the block's corners is not missed.
///
/// Research:
///     a caption clear of every way - research/questions/0242-labels-on-maps-cartographic-label-placement.drawing.html: a way the block comes within its drawn half-width of is a way crossed
///     the way notch - CONVENTION: the clearance runs 2 ft past a way's half-width (`WAY_NOTCH`), where a caption's halo would bite the tread
#[must_use]
pub fn caption_clears_ways(block: &[Pt], ways: &[Way]) -> bool {
    let who = Asker {
        subject: None,
        text: "",
        civic: false,
    };
    ObstacleIndex::new(Vec::new(), ways.to_vec()).cost(block, 0.0, who, None) == 0.0
}

/// One search's fixed context: the caption, its subject, the index, its clearance and the leader's index.
struct Search<'a> {
    text: &'a str,
    subject: &'a Subject,
    index: &'a ObstacleIndex,
    clear: f64,
    frame: Option<Frame>,
    leader_index: Option<&'a ObstacleIndex>,
}

/// A seat measured: its cost, its place in the search, the candidate and its block.
type Seat = (f64, usize, Cand, Poly);

impl Search<'_> {
    fn who(&self) -> Asker<'_> {
        let own = (self.subject.kind != Kind::Line).then_some(self.subject.poly.as_slice());
        Asker {
            subject: own,
            text: self.text,
            civic: self.subject.civic,
        }
    }

    fn block(c: &Cand) -> Poly {
        rect(c.center.0, c.center.1, c.half.0, c.half.1, c.angle)
    }

    fn spills(&self, block: &[Pt]) -> bool {
        self.subject.kind == Kind::Area
            && !block.iter().all(|p| inside(p.0, p.1, &self.subject.poly))
    }

    /// A seat's weight and whether it overlaps: what the block covers (with the association term for a point subject's seat beside it), an
    /// area's name spilling out of the area, and what its leader passes over. THE ASSOCIATION TERM IS ASKED OF A SEAT WITH NO LEADER
    /// (feature 287, labels L6): a leader carries the association itself. It is asked of the preferred offset's seats (ring 0) alone: the
    /// same bound holds for ring 1, leaderless too - its block, where ring 0's was blocked, stands within its own gap of the blocker, a tie
    /// counting - and asked there it refused every ring-1 seat on the pool sheets (feature 449 T184, measured 2026-11-18: 13 ring-1
    /// captions beside their subjects, 0 once asked; 16 captions moved, 4 more on ink, 9 more leaders), so ring 1 stays unasked.
    ///
    /// Research:
    ///     association beside a point - research/questions/0242-labels-on-maps-cartographic-label-placement.drawing.html: asked of a seat at the preferred offset (ring 0) alone; ring 1, leaderless too, is not asked, where the term with its tie refuses every ring-1 seat
    ///     an area's name inside it - research/questions/0242-labels-on-maps-cartographic-label-placement.drawing.html: spilling out costs an obstacle
    fn score(&self, c: &Cand, block: &[Pt]) -> (f64, bool) {
        let og = (self.subject.kind == Kind::Point && c.ring == 0)
            .then(|| poly_gap(block, &self.subject.poly));
        let (mut cost, mut hard) = self.index.score(block, self.clear, self.who(), og);
        if self.spills(block) {
            (cost, hard) = (cost + WEIGHT_OBSTACLE, true); // an area's name lies inside the area
        }
        if let Some(li) = self.leader_index {
            let (lc, lh) = leader_score(c, block, self.subject, li, self.clear, self.who());
            (cost, hard) = (cost + lc, hard || lh);
        }
        (cost, hard)
    }

    /// The least-cost seat, or the cheapest one within [`NUDGE_PX`] of it in the caption's own frame - never a seat off the frame, never
    /// one that spills an area's name outside the area, and with `soft_only` never one that overlaps.
    ///
    /// Research: the nudge - NONE: a whole-pixel search round the least-cost seat for a cheaper one, a search bound
    fn nudge(&self, cost: f64, cand: &Cand, block: Poly, soft_only: bool) -> (f64, Cand, Poly) {
        let mut best = (cost, cand.clone(), block);
        for dx in -NUDGE_PX..=NUDGE_PX {
            for dy in -NUDGE_PX..=NUDGE_PX {
                if best.0 == 0.0 {
                    return best;
                }
                let c = Cand {
                    center: (cand.center.0 + f64::from(dx), cand.center.1 + f64::from(dy)),
                    ..cand.clone()
                };
                let b = Self::block(&c);
                if !in_frame(&b, self.frame) || self.spills(&b) {
                    continue;
                }
                let (k, hard) = self.score(&c, &b);
                if k < best.0 && !(soft_only && hard) {
                    best = (k, c, b);
                }
            }
        }
        best
    }

    /// A strict search's answer once no candidate was free: the least-cost seat nudged free, or None - THE SAME ANSWER AS MEASURING EVERY
    /// SEAT (feature 287): a seat blocked beyond a nudge's reach can be neither free nor nudged free.
    ///
    /// Research: a strict seat - NONE: the least-cost seat nudged free or none, the same answer as measuring every seat
    fn strict_seat(&self, best: Option<Seat>, deep: Vec<(usize, Cand, Poly)>) -> Option<Placement> {
        count("candidate@_strict_seat", 1);
        let mut best = best?;
        let orders: Vec<usize> = deep.iter().map(|d| d.0).collect();
        for (order, cand, block) in deep {
            let cost = self.score(&cand, &block).0;
            // Python's `(cost, order) < best[:2]`
            if cost
                .partial_cmp(&best.0)
                .map(|o| o.then(order.cmp(&best.1)))
                == Some(std::cmp::Ordering::Less)
            {
                best = (cost, order, cand, block);
            }
        }
        if orders.contains(&best.1) {
            return None;
        }
        let (cost, cand, block) = self.nudge(best.0, &best.2, best.3, false);
        (cost == 0.0).then(|| placement(&cand, block, cost, self.subject))
    }
}

/// Seat one caption by the standard (the module's doc). `ask.frame` is the finished picture's; a block that leaves it is never a
/// candidate, because a clipped caption cannot be read. WHEN NO STANDARD SEAT IS FREE (features 286, 287): the fallback search, then the
/// leader rings past the reach out to the hug. A seat covering only `soft` ink is then taken at the least cost; a caption whose every seat
/// overlaps goes down where it covers the least (0242), and one with no seat in the frame at all takes the first seat beside it moved
/// inward until it fits (0241). Never dropped, never in a key, never past the hug. `ask.strict` returns None instead of anything but a
/// free seat; `ask.accept` is asked of every free candidate and of the strict search's nudged seat.
///
/// Research:
///     free space wins - research/questions/0242-labels-on-maps-cartographic-label-placement.drawing.html: the first seat covering nothing is taken
///     never clipped - research/questions/0242-labels-on-maps-cartographic-label-placement.drawing.html: a seat leaving the picture is never a candidate
///     never left off - research/questions/0242-labels-on-maps-cartographic-label-placement.drawing.html: with no free seat, the seat covering the least - soft ink first, then whatever it covers
///     no key - research/questions/0241-the-map-sheet-its-title-legend-frame-and-margins.drawing.html: there is no key box
///     no seat in the frame - GUESS: no source could speak to it, a value of ours (feature 417 T36 pass P7, 2026-10-25); a caption with no seat inside the frame takes the first seat beside it, moved inward until it fits (`moved_inward`)
///     the hug - CONVENTION: no seat past the hug from what it names
///     caption clearance - GUESS research/questions/0242-labels-on-maps-cartographic-label-placement.drawing.html: half the caption's letter height (`CLEAR_EM`) kept off other ink, the figure the page records as our calibration, not a finding, for the gap off a caption's own feature (feature 417 T36 pass P7, 2026-10-25)
///
/// # Errors
/// A line subject of fewer than two points ([`ONE_POINT_LINE`]) and a caption of no size ([`NO_SIZE`]), each refused by name.
#[expect(
    clippy::too_many_lines,
    reason = "the Python's one search, its stages and its answers in its order"
)]
pub fn place(
    text: &str,
    size: f64,
    subject: &Subject,
    index: &ObstacleIndex,
    ask: &Ask<'_>,
) -> Result<Option<Placement>, Error> {
    if subject.kind == Kind::Line && subject.poly.len() < 2 {
        return Err(Error::new("ValueError", ONE_POINT_LINE));
    }
    if size.is_nan() || size <= 0.0 {
        return Err(Error::new("ValueError", NO_SIZE));
    }
    let s = Search {
        text,
        subject,
        index,
        clear: CLEAR_EM * size,
        frame: ask.frame,
        leader_index: ask.leader_index,
    };
    let lines = ask.lines.filter(|l| !l.is_empty());
    let lays = lays_of(text, lines);
    let sizes = if lines.is_some() {
        ask.line_sizes
    } else {
        None
    }; // per-line sizes hold only for fixed lines
    let point = subject.kind == Kind::Point;
    let r = point.then(|| referent_box(subject, &subject.poly));
    // `max_ring` generates only the rings up to it - the rings past it are never offered, so they are never built
    let near: Option<Vec<(usize, f64)>> = ask
        .max_ring
        .map(|m| rings(size).into_iter().enumerate().take(m + 1).collect());
    let g = Gen {
        size,
        char_w: ask.char_w,
        lays: &lays,
        line_sizes: sizes,
        ring_gaps: near.as_deref(),
    };
    let outer = outer_rings(size);
    let lead = Gen {
        ring_gaps: Some(&outer),
        ..g
    };
    // the standard's candidates, then - reached only when none was free - the fallback search and the leader rings
    let stages: [&dyn Fn() -> Vec<Cand>; 4] = [
        &|| match subject.kind {
            Kind::Point => point_cands(&g, subject),
            Kind::Line => line_cands(&g, subject),
            Kind::Area => area_cands(&g, subject),
        },
        &|| {
            if ask.extended {
                extended_cands(&g, subject)
            } else {
                Vec::new()
            }
        },
        &|| {
            if !ask.extended
                || ask.max_ring.is_some()
                || outer.is_empty()
                || subject.kind == Kind::Area
            {
                Vec::new()
            } else if subject.kind == Kind::Line {
                line_cands(&lead, subject)
            } else {
                point_cands(&lead, subject)
            }
        },
        &|| {
            if !ask.extended || ask.max_ring.is_some() || outer.is_empty() || !point {
                Vec::new()
            } else {
                extended_cands(&lead, subject)
            }
        },
    ];
    let (mut best, mut soft): (Option<Seat>, Option<Seat>) = (None, None);
    let mut deep = Vec::new(); // strict: the seats no nudge can free, measured only if one might be the best
    let mut outside: Option<(Cand, Poly)> = None; // the first seat beside the subject that leaves the frame
    let mut order = 0;
    for stage in stages {
        for cand in stage() {
            let here = order;
            order += 1;
            let block = Search::block(&cand);
            // the hug is held with the nudge's room to spare, so no nudge can carry a seat past it (labels L10)
            if subject.kind != Kind::Area
                && hug_gap(&block, r.unwrap_or_else(|| referent_box(subject, &block))) > *HUG_RING
            {
                continue;
            }
            if !in_frame(&block, ask.frame) {
                outside = outside.or(Some((cand, block)));
                continue;
            }
            if ask.strict && index.blocked(&block, s.clear, nudge_reach(), s.who()) {
                deep.push((here, cand, block));
                continue;
            }
            let (cost, hard) = s.score(&cand, &block);
            if cost == 0.0 {
                let free = placement(&cand, block, cost, subject);
                if ask.accept.is_none_or(|ok| ok(&free)) {
                    return Ok(Some(free));
                }
                continue;
            }
            if best.as_ref().is_none_or(|b| cost < b.0) {
                best = Some((cost, here, cand.clone(), block.clone()));
            }
            if !hard && soft.as_ref().is_none_or(|b| cost < b.0) {
                soft = Some((cost, here, cand, block));
            }
        }
    }
    if ask.strict {
        let got = s.strict_seat(best, deep);
        return Ok(got.filter(|g| ask.accept.is_none_or(|ok| ok(g))));
    }
    Ok(Some(settle(&s, best, soft, outside)))
}

/// A non-strict search's answer once no candidate was free: the least-cost seat nudged when that frees it or carries it off every overlap
/// and costs no more than the softest; else the softest seat nudged over soft ink only; else, WITH NO FREE GROUND AT ALL, the seat covering
/// the least (feature 328 wave 49, 0242's drawing page: "On a sheet with no free ground at all, the caption still goes down, where it
/// covers the least"); and WITH NO SEAT INSIDE THE FRAME AT ALL, the first seat beside it moved inward (0241).
///
/// Research:
///     never left off - research/questions/0242-labels-on-maps-cartographic-label-placement.drawing.html: with no free seat, the seat covering the least - soft ink first, then whatever it covers
///     no seat in the frame - GUESS: no source could speak to it, a value of ours (feature 417 T36 pass P7, 2026-10-25); a caption with no seat inside the frame takes the first seat beside it, moved inward until it fits (`moved_inward`)
fn settle(
    s: &Search<'_>,
    best: Option<Seat>,
    soft: Option<Seat>,
    outside: Option<(Cand, Poly)>,
) -> Placement {
    if let Some((cost, _, cand, block)) = best.clone() {
        let (cost, cand, block) = s.nudge(cost, &cand, block, false);
        if (cost == 0.0 || !s.score(&cand, &block).1) && soft.as_ref().is_none_or(|sf| cost <= sf.0)
        {
            return placement(&cand, block, cost, s.subject);
        }
    }
    if let Some((cost, _, cand, block)) = soft {
        let (cost, cand, block) = s.nudge(cost, &cand, block, true);
        return placement(&cand, block, cost, s.subject);
    }
    if let Some((cost, _, cand, block)) = best {
        let (cost, cand, block) = s.nudge(cost, &cand, block, false);
        return placement(&cand, block, cost, s.subject);
    }
    let (cand, block) = outside.expect("the standard offers a seat beside every subject");
    let (cand, block) = moved_inward(&cand, &block, s.frame);
    let cost = s.score(&cand, &block).0;
    placement(&cand, block, cost, s.subject)
}

/// `cand` shifted by the least that brings `block` inside `frame` on each axis - centered on an axis the frame is narrower than the
/// block on.
///
/// Research: moved inward - GUESS: no source could speak to it, a value of ours (feature 417 T36 pass P7, 2026-10-25); shifted by the least that brings it inside the frame, centered where the frame is narrower (0241's caption moved inward is the crop's, not a fixed frame's)
#[must_use]
pub fn moved_inward(cand: &Cand, block: &[Pt], frame: Option<Frame>) -> (Cand, Poly) {
    let Some(f) = frame else {
        return (cand.clone(), block.to_vec());
    };
    let (bx0, by0, bx1, by1) = bbox(block);
    let shift = |lo: f64, hi: f64, f0: f64, f1: f64| {
        if hi - lo > f1 - f0 {
            half_sum(f0, f1) - half_sum(lo, hi)
        } else {
            max(f0 - lo, 0.0) - max(hi - f1, 0.0)
        }
    };
    let (dx, dy) = (shift(bx0, bx1, f.0, f.2), shift(by0, by1, f.1, f.3));
    let moved = Cand {
        center: (cand.center.0 + dx, cand.center.1 + dy),
        ..cand.clone()
    };
    (
        moved,
        block.iter().map(|&(x, y)| (x + dx, y + dy)).collect(),
    )
}

/// Does the block stay inside the frame?
///
/// Research: never clipped - research/questions/0242-labels-on-maps-cartographic-label-placement.drawing.html: a seat leaving the picture is never a candidate
#[must_use]
pub fn in_frame(block: &[Pt], frame: Option<Frame>) -> bool {
    let Some(f) = frame else { return true };
    let (bx0, by0, bx1, by1) = bbox(block);
    !(bx0 < f.0 || by0 < f.1 || bx1 > f.2 || by1 > f.3)
}

/// The leader a seat past twice the usual gap draws: from the caption's block to the nearest point of what it names, trimmed a little at
/// each end. None within [`LEADERLESS_RINGS`] and for an area, whose name lies inside it; None too where the block touches what it names
/// (a line that bends back can hold a leader ring's block across another of its segments) - nothing is left to tie back, where the Python
/// divided by the zero distance (feature 449 T184).
///
/// Research:
///     when a leader is drawn - research/questions/0242-labels-on-maps-cartographic-label-placement.drawing.html: a caption more than twice the usual gap from its feature is tied to it by a thin leader line, to the nearest point of the feature
///     leader end trim - CONVENTION: a leader stops short of the words and of the feature by a quarter of its length, at most 1 px, so neither end touches the ink it joins; a drawn size on the sheet, not in the world
#[must_use]
pub fn leader_of(ring: usize, block: &[Pt], subject: &Subject) -> Option<(Pt, Pt)> {
    if ring < LEADERLESS_RINGS || subject.kind == Kind::Area {
        return None;
    }
    let (a, b) = nearest_points(block, &subject.poly, subject.kind != Kind::Line);
    let d = dist(a, b);
    if d == 0.0 {
        return None;
    }
    let trim = min(1.0, d / 4.0);
    let (ux, uy) = ((b.0 - a.0) / d, (b.1 - a.1) / d);
    Some((
        (a.0 + ux * trim, a.1 + uy * trim),
        (b.0 - ux * trim, b.1 - uy * trim),
    ))
}

/// What a seat's leader line passes over or ends against, of the things `index` holds, and whether that is an overlap: a leader through
/// another caption, or ending on a tub beside the feature it names, reads as naming the wrong thing (feature 283).
///
/// Research: leader keeps clear - CONVENTION: a leader through a caption or ending on a small glyph counts as covering it
#[must_use]
pub fn leader_score(
    c: &Cand,
    block: &[Pt],
    subject: &Subject,
    index: &ObstacleIndex,
    clear: f64,
    who: Asker<'_>,
) -> (f64, bool) {
    let Some(((ax, ay), (bx, by))) = leader_of(c.ring, block, subject) else {
        return (0.0, false);
    };
    let len = dist((ax, ay), (bx, by));
    if len < 1e-6 {
        return (0.0, false);
    }
    let band = rect(
        half_sum(ax, bx),
        half_sum(ay, by),
        len / 2.0,
        0.5,
        (by - ay).atan2(bx - ax).to_degrees(),
    );
    index.score(&band, clear, who, None)
}

/// What a drawn caption's block covers by the placer's own measure, and whether any of it is an overlap - a seat's score asked again of
/// a finished placement (the port's comparison, feature 449 T151).
///
/// Research: a seat's standing - NONE: the placer's own score asked of a finished seat, deciding nothing
#[must_use]
pub fn judge(
    text: &str,
    size: f64,
    subject: &Subject,
    index: &ObstacleIndex,
    leader_index: Option<&ObstacleIndex>,
    p: &Placement,
) -> (f64, bool) {
    let s = Search {
        text,
        subject,
        index,
        clear: CLEAR_EM * size,
        frame: None,
        leader_index,
    };
    let c = Cand {
        ring: p.ring,
        rank: p.rank,
        position: p.position,
        center: (p.x, p.y),
        angle: p.angle,
        lines: Vec::new(),
        half: (0.0, 0.0),
        size,
    };
    s.score(&c, &p.block)
}

fn placement(c: &Cand, block: Poly, cost: f64, subject: &Subject) -> Placement {
    Placement {
        x: c.center.0,
        y: c.center.1 + CENTER_ABOVE_BASELINE_EM * c.size,
        angle: c.angle,
        lines: c.lines.clone(),
        leader: leader_of(c.ring, &block, subject),
        block,
        ring: c.ring,
        rank: c.rank,
        position: c.position,
        cost,
    }
}

#[cfg(test)]
mod tests;
