//! The wall's checks (feature 449 T175, the second half of `pack_audit/checks.py`): its openings measured from the INK
//! ([`wall_openings`]), what stands in a gate's passage ([`passage_blockers`]), a structure drawn across a wall's ink
//! ([`structures_on_walls`]) and the aligned gaps between buildings stacked on a shared edge ([`aligned_gaps`], [`gap_tag`]).
//!
//! Research:
//!     the wall's checks - NONE: a parsed sheet's walls and buildings measured against the thresholds whose claims stand on each, deciding nothing more

use super::{overlap_px, sort_desc};
use crate::grids::FTPX;
use crate::parse::{ParsedPlan, Rect, WALL_STROKE};
use crate::py::{half_sum, max, min, round_to};

/// The gateway zone reaches 3 ft in front of and behind the wall ink: a stone set just inside or just outside the masonry is still in
/// the track a cart drives through.
///
/// Research:
///     gateway zone depth - GUESS: the gateway zone reaches 9 px (3 ft) in front of and behind the wall ink, the strip where a stone would block a cart track; no page gives it.
pub const PASSAGE_DEPTH_PX: f64 = 9.0;
/// Sub-pixel contact is a flush jamb (a gate post abutting the opening edge) plus integer-emit rounding, not an object in the passage.
///
/// Research:
///     passage contact floor - NONE: contact under 0.5 px in a passage is a flush jamb plus emit rounding, an audit pixel tolerance.
pub const PASSAGE_CLEAR_MIN_PX: f64 = 0.5;
/// A wider gap in the wall is a structural break (a wall drawn around a building that IS part of it), not a gate.
///
/// Research:
///     wall opening ceiling - GUESS: no page sets it; a gap wider than 80 px (about 27 ft at 3 px to the foot) in a wall is a structural break, not a gate - a gate-width ceiling above the record's 18-24 ft yamen gatehouse.
pub const OPENING_MAX_PX: f64 = 80.0;
/// Sub-pixel contact is a flush abutment plus integer-emit rounding.
///
/// Research:
///     wall overlap floor - NONE: contact under 0.5 px with a wall is a flush abutment plus emit rounding, an audit pixel tolerance.
pub const WALL_OVERLAP_MIN_PX: f64 = 0.5;
/// A STRUCTURE STANDS A FOOT OR TWO CLEAR OF THE WALL'S FACE (feature 374 wave 134): 0092's "a foot or two", the least of it held
/// across the wall's thickness, never past a segment's ends.
///
/// Research:
///     least clearance from wall face - GUESS research/questions/0092-compound-walls-neribei-and-tsuijibei.drawing.html: the audit holds a structure at least 1 ft off the wall's face, the least of the page's 'a foot or two', which the page records as a guess.
pub const WALL_FACE_CLEAR_FT: f64 = 1.0;

/// An empty gap (ft) between two buildings stacked on a shared edge: "V" or "H", its middle, and whether a kura is one of the pair.
#[derive(Debug, Clone, PartialEq)]
pub struct Gap {
    pub ft: f64,
    pub orient: &'static str,
    pub mx: f64,
    pub my: f64,
    pub kura: bool,
}

/// A gap in the compound wall's INK - the passage a cart drives through: its middle, its width (ft), its axis, and the gateway rect
/// (`span1..span2` along the wall, `across1..across2` the ink's thickness) that [`passage_blockers`] keeps clear.
#[derive(Debug, Clone, PartialEq)]
pub struct WallOpening {
    pub x: f64,
    pub y: f64,
    pub ft: f64,
    pub horiz: bool,
    pub span1: f64,
    pub span2: f64,
    pub across1: f64,
    pub across2: f64,
}

/// A furniture-scale object standing in a gateway, where the traffic goes.
#[derive(Debug, Clone, PartialEq)]
pub struct PassageBlocker {
    pub x: f64,
    pub y: f64,
    pub w_ft: f64,
    pub h_ft: f64,
    pub opening_ft: f64,
}

/// A built footprint drawn across the ink of a wall: its center, its size (ft), how far it reaches into the ink and the foot clear of
/// its face (ft), and which wall.
#[derive(Debug, Clone, PartialEq)]
pub struct StructureOnWall {
    pub x: f64,
    pub y: f64,
    pub w_ft: f64,
    pub h_ft: f64,
    pub into_ft: f64,
    pub wall: &'static str,
}

/// Openings in the compound wall, measured from the INK (`wall_bands`, which model a square cap), widest first: consecutive collinear
/// bands of the compound wall's stroke, grouped by their axis's line (Python's `round(..., 1)`), a gap between `0` and
/// [`OPENING_MAX_PX`]. WHY (2026-07-25): every stated 13.3 ft main gate had rendered as 10.3 ft of passage once its caps were inked.
#[must_use]
pub fn wall_openings(plan: &ParsedPlan) -> Vec<WallOpening> {
    let mut out = Vec::new();
    for horiz in [true, false] {
        let mut groups: Vec<(f64, Vec<&Rect>)> = Vec::new();
        for band in &plan.wall_bands {
            if band.fill != WALL_STROKE || (band.w >= band.h) != horiz {
                continue;
            }
            let line = if horiz {
                band.y + band.h / 2.0
            } else {
                band.x + band.w / 2.0
            };
            let key = round_to(line, 1);
            // a dict keyed by a float: an equal key (a negative zero is zero) is the first one's
            #[expect(clippy::float_cmp, reason = "a Python dict's key equality")]
            let found = groups.iter_mut().find(|(k, _)| *k == key);
            match found {
                Some((_, segs)) => segs.push(band),
                None => groups.push((key, vec![band])),
            }
        }
        for (key, mut segs) in groups {
            segs.sort_by(|a, b| {
                let (p, q) = if horiz { (a.x, b.x) } else { (a.y, b.y) };
                p.partial_cmp(&q).unwrap_or(std::cmp::Ordering::Equal)
            });
            for pair in segs.windows(2) {
                let (a, b) = (pair[0], pair[1]);
                let gap = if horiz { b.x - a.x2() } else { b.y - a.y2() };
                if 0.0 < gap && gap < OPENING_MAX_PX {
                    let mid = if horiz {
                        half_sum(a.x2(), b.x)
                    } else {
                        half_sum(a.y2(), b.y)
                    };
                    let (s1, s2) = if horiz { (a.x2(), b.x) } else { (a.y2(), b.y) };
                    let (t1, t2) = if horiz { (a.y, a.y2()) } else { (a.x, a.x2()) };
                    out.push(WallOpening {
                        x: if horiz { mid } else { key },
                        y: if horiz { key } else { mid },
                        ft: gap / FTPX,
                        horiz,
                        span1: s1,
                        span2: s2,
                        across1: t1,
                        across2: t2,
                    });
                }
            }
        }
    }
    sort_desc(&mut out, |o| o.ft);
    out
}

/// Furniture-scale objects (furniture, wells, glyphs, tubs) standing in a gate's PASSAGE (GM 2026-07-25: a threshold stone FLANKS the
/// road): the gateway rect grown [`PASSAGE_DEPTH_PX`] across the wall, more than [`PASSAGE_CLEAR_MIN_PX`] into it both ways. Buildings
/// and ground cover do not count. Largest first.
#[must_use]
pub fn passage_blockers(plan: &ParsedPlan) -> Vec<PassageBlocker> {
    let mut out = Vec::new();
    for o in wall_openings(plan) {
        let (x1, y1, x2, y2) = if o.horiz {
            (
                o.span1,
                o.across1 - PASSAGE_DEPTH_PX,
                o.span2,
                o.across2 + PASSAGE_DEPTH_PX,
            )
        } else {
            (
                o.across1 - PASSAGE_DEPTH_PX,
                o.span1,
                o.across2 + PASSAGE_DEPTH_PX,
                o.span2,
            )
        };
        for r in plan
            .furniture
            .iter()
            .chain(&plan.wells)
            .chain(&plan.glyphs)
            .chain(&plan.tubs)
        {
            if min(r.x2(), x2) - max(r.x, x1) > PASSAGE_CLEAR_MIN_PX
                && min(r.y2(), y2) - max(r.y, y1) > PASSAGE_CLEAR_MIN_PX
            {
                out.push(PassageBlocker {
                    x: r.x + r.w / 2.0,
                    y: r.y + r.h / 2.0,
                    w_ft: r.w / FTPX,
                    h_ft: r.h / FTPX,
                    opening_ft: o.ft,
                });
            }
        }
    }
    sort_desc(&mut out, |b| b.w_ft * b.h_ft);
    out
}

/// `band` grown by `clear` px on both of its long faces (across the wall's thickness), not at its ends.
fn with_clearance(band: &Rect, clear: f64) -> Rect {
    if band.w >= band.h {
        Rect::new(
            band.x,
            band.y - clear,
            band.w,
            band.h + 2.0 * clear,
            &band.fill,
            -1,
        )
    } else {
        Rect::new(
            band.x - clear,
            band.y,
            band.w + 2.0 * clear,
            band.h,
            &band.fill,
            -1,
        )
    }
}

/// Structures overlapping the ink of a compound wall or a court divider - grown by [`WALL_FACE_CLEAR_FT`] on its faces - by more than
/// `min_px`, worst first. A wall is a built object with real thickness: a structure ABUTS it or the wall is drawn as segments BROKEN
/// around a structure that IS part of it.
#[must_use]
pub fn structures_on_walls(plan: &ParsedPlan, min_px: f64) -> Vec<StructureOnWall> {
    let mut out = Vec::new();
    let clear = WALL_FACE_CLEAR_FT * FTPX;
    for s in &plan.structures {
        let mut worst: Option<(f64, &'static str)> = None;
        for band in &plan.wall_bands {
            let ov = overlap_px(s.x, s.y, s.x2(), s.y2(), &with_clearance(band, clear));
            if ov > min_px && worst.is_none_or(|(w, _)| ov > w) {
                // every band the parse keeps is inked in one of the two walls' strokes (T182: a lookup whose miss could not run)
                let wall = if band.fill == WALL_STROKE {
                    "compound wall"
                } else {
                    "court divider"
                };
                worst = Some((ov, wall));
            }
        }
        if let Some((ov, wall)) = worst {
            out.push(StructureOnWall {
                x: s.x + s.w / 2.0,
                y: s.y + s.h / 2.0,
                w_ft: s.w / FTPX,
                h_ft: s.h / FTPX,
                into_ft: ov / FTPX,
                wall,
            });
        }
    }
    sort_desc(&mut out, |r| r.into_ft);
    out
}

/// Does a third building stand in the corridor between buildings `i` and `j`, its x-interval `(lo, hi)` and y-interval `(near, far)`?
fn blocked(buildings: &[Rect], i: usize, j: usize, x: (f64, f64), y: (f64, f64)) -> bool {
    buildings
        .iter()
        .enumerate()
        .any(|(k, r)| k != i && k != j && r.x < x.1 && r.x2() > x.0 && r.y < y.1 && r.y2() > y.0)
}

/// Empty gaps (5-30 ft) between buildings stacked on a shared edge, largest first, one within 15 px of a larger kept.
///
/// Research:
///     its search steps and tolerances - GUESS: no source could speak to it, a value of ours (feature 417 T38 pass N13, 2026-10-25) - 30 (reporting window: 10 ft shared edge, gaps from 5 ft)
///     its salts, guards and sentinels - NONE: they decide nothing about the place - 15 (dedupe radius)
///     its reported gap - GUESS: no source could speak to it, a value of ours, the top of the reporting window above - 90 (upper bound on the reported gap, 30 ft: buildings farther apart are not judged for spacing)
#[must_use]
pub fn aligned_gaps(plan: &ParsedPlan) -> Vec<Gap> {
    let b = &plan.buildings;
    let mut raw = Vec::new();
    for (i, a) in b.iter().enumerate() {
        for (j, c) in b.iter().enumerate() {
            if i == j {
                continue;
            }
            let ox = min(a.x2(), c.x2()) - max(a.x, c.x);
            if ox >= 30.0 && c.y >= a.y2() && (15.0..=90.0).contains(&(c.y - a.y2())) {
                let (xl, xr) = (max(a.x, c.x), min(a.x2(), c.x2()));
                if !blocked(b, i, j, (xl, xr), (a.y2(), c.y)) {
                    raw.push(Gap {
                        ft: (c.y - a.y2()) / FTPX,
                        orient: "V",
                        mx: half_sum(xl, xr),
                        my: half_sum(a.y2(), c.y),
                        kura: a.is_kura() || c.is_kura(),
                    });
                }
            }
            let oy = min(a.y2(), c.y2()) - max(a.y, c.y);
            if oy >= 30.0 && c.x >= a.x2() && (15.0..=90.0).contains(&(c.x - a.x2())) {
                let (yl, yr) = (max(a.y, c.y), min(a.y2(), c.y2()));
                if !blocked(b, i, j, (a.x2(), c.x), (yl, yr)) {
                    raw.push(Gap {
                        ft: (c.x - a.x2()) / FTPX,
                        orient: "H",
                        mx: half_sum(a.x2(), c.x),
                        my: half_sum(yl, yr),
                        kura: a.is_kura() || c.is_kura(),
                    });
                }
            }
        }
    }
    sort_desc(&mut raw, |g| g.ft);
    let mut out: Vec<Gap> = Vec::new();
    for gp in raw {
        if !out
            .iter()
            .any(|o| (gp.mx - o.mx).abs() < 15.0 && (gp.my - o.my).abs() < 15.0)
        {
            out.push(gp);
        }
    }
    out
}

/// Heuristic label for an aligned gap (a kura keeps a fire-gap; wooden slack tightens).
///
/// Research:
///     its figures guessed on 0116 - GUESS research/questions/0116-the-size-of-a-compound-and-the-rank-of-its-buildings.drawing.html: 8 (wooden gap over 8 ft is loose)
///     its loose gap - GUESS research/questions/0116-the-size-of-a-compound-and-the-rank-of-its-buildings.drawing.html: 10 (a kura fire-gap over 10 ft is loose)
///     its fire-gap floor - GUESS research/questions/0116-the-size-of-a-compound-and-the-rank-of-its-buildings.drawing.html: 6 (a kura fire-gap under 6 ft is too tight, the bottom of the page's 6-10 ft)
#[must_use]
pub fn gap_tag(gap: &Gap) -> &'static str {
    if gap.kura {
        // FEATURE 449 T182: a kura gap under the page's 6 ft floor was tagged OK, the floor never enforced
        if gap.ft < 6.0 {
            "TIGHT (kura gap <6 ft)"
        } else if gap.ft <= 10.0 {
            "fire-gap OK (kura)"
        } else {
            "LOOSE (kura gap >10 ft)"
        }
    } else if gap.ft <= 8.0 {
        "tight"
    } else {
        "LOOSE (wooden >8 ft)"
    }
}
