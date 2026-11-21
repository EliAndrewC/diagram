//! The checks feature 254 added (feature 449 T175, `pack_audit/shared.py` whole): the shared layer's - two footprints lapping
//! ([`structures_overlap`]), the scale bar ([`scale_bar_present`]), the viewBox crop ([`ink::viewbox_cropped`]), the gates' widths
//! ([`gate_widths`]), a tree's canopy ([`trees_overlap`]) and the well's gear ([`grounds::well_gear`]) - and the magistracy's and the
//! shrine's: the coverage band, perimeter hugging, two-court zoning, the postern's approach and the shrine's own ([`grounds`]).
//!
//! The GM (feature 254): a shared check is "whether different shapes end up overlapping with each other"; each here is a pure function of
//! a parsed plan (and, where it reads tags, of the sheet's text) returning finding strings; [`super::registry`] gives each its types, its
//! red fixture and its fix sentence.
//!
//! Research:
//!     the shared checks - NONE: a sheet measured against the thresholds whose claims stand on each, deciding nothing more

use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_gate_research::pyre::py;
use l7r_gate_research::Error;
use l7r_shared::py_text::strip;

use super::checks::{first_max, wall_openings, WALL_OVERLAP_MIN_PX};
use crate::grids::{coverage, perimeter_hugging_pct, CELL, FTPX, HUG_DEPTH_FT};
use crate::parse::{ParsedPlan, Rect, COURT_FLOORS};
use crate::py::{fixed, hypot, max, min, round_int, sum};

pub mod grounds;
pub mod ink;

pub use grounds::{
    arch_on_approach, hall_at_an_end, no_precinct_enclosure, one_compound_shrine,
    sanctuary_on_axis, shrine_tree, stall_width, well_clear_of_arch, well_gear, ARCH_COUNTS,
    AXIS_TOL_FT, EDGE_TOL_FT, HALL_MIN_SPAN_FT, INNERMOST_FT, INNERMOST_TOL_FT, SHRINE_TREE_FT,
    STALL_FT,
};
pub use ink::{ink_bounds, viewbox_cropped, CROP_MAX_MARGIN_PX, CROP_TOL_PX, PARCHMENT_SHARE};

/// A structure may CONTAIN another and two blocks of one building may join by a corridor that laps a few px into each; an accident is a
/// lap of more than this share of the smaller footprint, neither rect inside the other (tuned on the five pool sheets, 2026-09-19).
///
/// Research:
///     building overlap share - NONE: an overlap over 0.30 of the smaller footprint is an accident, a tolerance tuned on the pool sheets.
pub const OVERLAP_SHARE: f64 = 0.30;
/// The coverage band's floor: 0116's drawing page as corrected on 2026-10-01 (feature 372 wave 105), about 30-42%, the bottom the one
/// office measured.
///
/// Research:
///     building coverage floor - research/questions/0116-the-size-of-a-compound-and-the-rank-of-its-buildings.drawing.html: a compound's buildings cover about 30-42% of its walled ground; the bottom, 30%, is near Takayama's ~31% of floor against site.
pub const COVERAGE_FLOOR: f64 = 0.30;
/// The coverage band's ceiling.
///
/// Research:
///     building coverage ceiling - GUESS research/questions/0116-the-size-of-a-compound-and-the-rank-of-its-buildings.drawing.html: the top of the 30-42% coverage range, 42%, is the project's estimate from plans, which the page records as a guess.
pub const COVERAGE_CEILING: f64 = 0.42;
/// Two points over the ceiling, for a rule written with a tilde.
///
/// Research:
///     coverage tolerance - GUESS: two points above the band's ceiling only, for the page's "about" 30-42%, the floor of 30% held exactly; no page gives the slack.
pub const COVERAGE_TOL: f64 = 0.02;
/// The hugging floor is DERIVED, not typed from a source: one building pulled into a court's center under the lowest shipped sheet.
///
/// Research:
///     wall-hugging floor - GUESS: at least 0.45 of building footprint stands within 25 ft of a wall; derived from the pool sheets (51-58%) and no source gives a historical figure.
pub const HUGGING_FLOOR: f64 = 0.45;
/// Narrower is not a passage anyone drives or walks through.
///
/// Research:
///     narrowest gate - GUESS: a wall opening under 5 ft is not a passage anyone drives or walks through; the record's gates run 6 to 12 ft (0093) and no page gives the audit's floor.
pub const GATE_MIN_FT: f64 = 5.0;
/// Wider is a structure's width, not a passage's (the gate lesson of 2026-07), unless a structure spans it.
///
/// Research:
///     widest gate - GUESS: a wall opening over 16 ft is a structure's width, not a passage's; no page sets a widest gate; the record's Japanese gates run 6 to 12 ft (0093) and a yamen's 18-24 ft is a guess on both 0093's and 0092's drawing pages.
pub const GATE_MAX_FT: f64 = 16.0;

static SCALE_LABEL: LazyLock<Regex> = LazyLock::new(|| py(r"^\d+\s*ft$"));
static SCALE_NOTE: LazyLock<Regex> = LazyLock::new(|| py(r"3\s*px\s*=\s*1\s*ft"));

/// The overlap of two rects along x and along y.
pub(crate) fn lap(a: &Rect, b: &Rect) -> (f64, f64) {
    (
        min(a.x2(), b.x2()) - max(a.x, b.x),
        min(a.y2(), b.y2()) - max(a.y, b.y),
    )
}

fn contains(outer: &Rect, inner: &Rect) -> bool {
    let tol = WALL_OVERLAP_MIN_PX;
    outer.x - tol <= inner.x
        && outer.y - tol <= inner.y
        && inner.x2() <= outer.x2() + tol
        && inner.y2() <= outer.y2() + tol
}

/// Two built footprints lapping each other by more than `share` of the smaller, neither inside the other: a sorted-edge sweep, rects
/// ordered by x, each compared only with those whose x-span reaches it.
#[must_use]
pub fn structures_overlap(plan: &ParsedPlan, share: f64) -> Vec<String> {
    let mut rects: Vec<&Rect> = plan.structures.iter().collect();
    rects.sort_by(|a, b| a.x.partial_cmp(&b.x).unwrap_or(std::cmp::Ordering::Equal));
    let mut out = Vec::new();
    for (i, a) in rects.iter().enumerate() {
        for b in &rects[i + 1..] {
            if b.x >= a.x2() - WALL_OVERLAP_MIN_PX {
                break;
            }
            let (lx, ly) = lap(a, b);
            if lx <= WALL_OVERLAP_MIN_PX
                || ly <= WALL_OVERLAP_MIN_PX
                || contains(a, b)
                || contains(b, a)
            {
                continue;
            }
            let smaller = min(a.area_px(), b.area_px());
            if smaller > 0.0 && lx * ly / smaller > share {
                out.push(format!(
                    "a {} x {} ft footprint at svg({},{}) and a {} x {} ft one at svg({},{}) overlap by {} x {} ft ({}% of the smaller)",
                    fixed(a.w / FTPX, 0),
                    fixed(a.h / FTPX, 0),
                    fixed(a.x, 0),
                    fixed(a.y, 0),
                    fixed(b.w / FTPX, 0),
                    fixed(b.h / FTPX, 0),
                    fixed(b.x, 0),
                    fixed(b.y, 0),
                    fixed(lx / FTPX, 1),
                    fixed(ly / FTPX, 1),
                    fixed(100.0 * lx * ly / smaller, 0)
                ));
            }
        }
    }
    out
}

/// The scale bar's two labels - a length in ft and the `(3 px = 1 ft)` note - are on the sheet.
#[must_use]
pub fn scale_bar_present(plan: &ParsedPlan) -> Vec<String> {
    let texts: Vec<&str> = plan.labels.iter().map(|lb| strip(&lb.text)).collect();
    let mut missing = Vec::new();
    if !texts
        .iter()
        .any(|t| SCALE_LABEL.is_match(t).unwrap_or(false))
    {
        missing.push("no scale-bar length label (e.g. `30 ft`)".to_owned());
    }
    if !texts
        .iter()
        .any(|t| SCALE_NOTE.is_match(t).unwrap_or(false))
    {
        missing.push("no `(3 px = 1 ft)` note".to_owned());
    }
    missing
}

/// The fix the coverage check names (feature 433 D3, the GM 2026-10-26: "whatever other changes need to be made should be made in order
/// to make the whole thing correspond to our research"): a wall moves in only as a DEVIATION recorded on 0116's drawing page.
pub const COVERAGE_FIX: &str = "consolidate loose slack or add a program building below it; never shrink the envelope to hide slack - a wall moves in only when a house drawn at the record's size leaves the sheet under the band and nothing else can close it, as a DEVIATION recorded on 0116's drawing page (feature 433)";

/// Building coverage of the precinct within the band (the ceiling two points loose).
///
/// # Errors
/// [`coverage`]'s refusal (a precinct of no area).
pub fn coverage_band(
    plan: &ParsedPlan,
    floor: f64,
    ceiling: f64,
    tol: f64,
) -> Result<Vec<String>, Error> {
    let cov = coverage(plan, CELL)?;
    if floor <= cov && cov <= ceiling + tol {
        return Ok(Vec::new());
    }
    Ok(vec![format!(
        "building coverage is {}% - a jin'ya runs ~{}-{}% built ({COVERAGE_FIX})",
        fixed(100.0 * cov, 0),
        fixed(100.0 * floor, 0),
        fixed(100.0 * ceiling, 0)
    )])
}

/// Most building footprint rings the courts: at least `floor` of it within 25 ft of a wall or divider.
///
/// # Errors
/// [`perimeter_hugging_pct`]'s refusal.
pub fn perimeter_hugging(plan: &ParsedPlan, floor: f64) -> Result<Vec<String>, Error> {
    let hug = perimeter_hugging_pct(plan, HUG_DEPTH_FT, CELL)?;
    if hug >= floor {
        return Ok(Vec::new());
    }
    Ok(vec![format!(
        "only {}% of building footprint lies within 25 ft of a wall (floor {}%) - buildings ring the courts, the center stays open",
        fixed(100.0 * hug, 0),
        fixed(100.0 * floor, 0)
    )])
}

/// Every opening in the compound wall is a passable gate, or a break a structure stands in.
///
/// Research:
///     a wide break a structure spans - research/questions/0093-the-main-gate-and-its-gatekeepers-nagaya-mon.drawing.html: an opening wider than the widest gate passes where a structure spans it, a gate drawn as a building (a yamen's roofed gate of three bays, a gate range) rather than as an opening in the wall.
///     the fix text's gate width - research/questions/0093-the-main-gate-and-its-gatekeepers-nagaya-mon.drawing.html: the fix sentence draws a gate at passage width, about 6 to 12 ft, the width the page gives a Japanese magistrate's office's gate, the form the compounds follow (feature 449 T177: it gave about 13 ft, outside every width the record gives).
#[must_use]
pub fn gate_widths(plan: &ParsedPlan, lo_ft: f64, hi_ft: f64) -> Vec<String> {
    let mut out = Vec::new();
    let tol = WALL_OVERLAP_MIN_PX;
    for o in wall_openings(plan) {
        if o.ft < lo_ft {
            out.push(format!(
                "a {} ft opening at svg({},{}) is too narrow for a passage - pull the flanking endpoints back by half a stroke, or close it",
                fixed(o.ft, 1),
                fixed(o.x, 0),
                fixed(o.y, 0)
            ));
        } else if o.ft > hi_ft {
            let (x1, y1, x2, y2) = super::roads::opening_box(&o);
            let spanned = plan.structures.iter().any(|s| {
                let along = s.x <= x1 + tol && s.x2() >= x2 - tol;
                let across = s.y <= y1 + tol && s.y2() >= y2 - tol;
                along && across
            });
            if !spanned {
                out.push(format!(
                    "a {} ft opening at svg({},{}) is a structure's width, not a passage's - a gate is drawn at passage width (about 6 to 12 ft, 0093), or a structure stands in the break",
                    fixed(o.ft, 1),
                    fixed(o.x, 0),
                    fixed(o.y, 0)
                ));
            }
        }
    }
    out
}

/// A divider line: its axis (horizontal) and where it runs across it, rounded to an integer.
type DividerLine = (bool, f64);

/// The openings in the court divider, in feet: the gaps between consecutive runs of one divider line (its runs share an axis and a line,
/// to the Python's `round()`).
///
/// # Errors
/// A divider's line that is no number: Python's `round()` refusal.
pub fn divider_gates_ft(plan: &ParsedPlan) -> Result<Vec<f64>, Error> {
    let mut lines: Vec<(DividerLine, Vec<(f64, f64)>)> = Vec::new();
    for d in &plan.dividers {
        let horiz = d.w >= d.h;
        let line = round_int(if horiz {
            d.y + d.h / 2.0
        } else {
            d.x + d.w / 2.0
        })?;
        let run = if horiz { (d.x, d.x2()) } else { (d.y, d.y2()) };
        // a Python dict's key equality, of integers
        let found = lines.iter_mut().find(|(k, _)| *k == (horiz, line));
        match found {
            Some((_, runs)) => runs.push(run),
            None => lines.push(((horiz, line), vec![run])),
        }
    }
    let mut out = Vec::new();
    for (_, mut runs) in lines {
        runs.sort_by(|a, b| {
            a.0.partial_cmp(&b.0)
                .unwrap_or(std::cmp::Ordering::Equal)
                .then(a.1.partial_cmp(&b.1).unwrap_or(std::cmp::Ordering::Equal))
        });
        out.extend(runs.windows(2).map(|w| (w[1].0 - w[0].1) / FTPX));
    }
    Ok(out)
}

/// A divider wall splits the compound, the divider has its own gate (the nakamon, feature 267 pass 3), and the sanded hearing court lies
/// on the main gate's side of it.
///
/// Research:
///     two courts and the gate between - research/questions/0090-magistrates-compounds-jinya-and-yamen.drawing.html: a magistracy is two courts, the office in front and the residence behind, with a gate between them dividing the office from the home; the page records that order in a Japanese compound as a deliberate simplification.
///     the hearing court on the gate's side - research/questions/0090-magistrates-compounds-jinya-and-yamen.drawing.html: the hearing court lies before the office hall in the outer court, so on the main gate's side of the divider; a vertical divider is not judged.
///     the middle gate's width in the message - UNRESEARCHED: the message gives the middle gate (nakamon) as about 6-8 ft, narrower than the main gate; the check holds only the narrowest gate's floor, and no page gives a middle gate's width.
///
/// # Errors
/// [`divider_gates_ft`]'s refusal.
pub fn two_court_zoning(plan: &ParsedPlan) -> Result<Vec<String>, Error> {
    let one = |s: &str| Ok(vec![s.to_owned()]);
    if plan.dividers.is_empty() {
        return one("no court divider - a magistracy is an outer (public) court at the gate and an inner (private) court behind a divider");
    }
    if !divider_gates_ft(plan)?.iter().any(|g| *g >= GATE_MIN_FT) {
        return one("the court divider has no gate - the household's middle gate (nakamon, ~6-8 ft, narrower than the main gate) joins the courts");
    }
    let sand: Vec<&Rect> = plan
        .open_features
        .iter()
        .filter(|r| COURT_FLOORS.contains(&r.fill.as_str()))
        .collect();
    let Some(court) = sand.first() else {
        return one(
            "no hearing court (oshirasu) - the bench overlooks it from the office hall's dais",
        );
    };
    let gates: Vec<_> = wall_openings(plan)
        .into_iter()
        .filter(|o| o.ft <= GATE_MAX_FT)
        .collect();
    let Some(main) = first_max(gates.iter(), |o| o.ft) else {
        return one("no gate opening in the compound wall");
    };
    let horiz: Vec<&Rect> = plan.dividers.iter().filter(|d| d.w >= d.h).collect();
    if horiz.is_empty() {
        return Ok(Vec::new()); // a vertical divider: the sides are east/west; the sheet's own composition rule, not checked here
    }
    #[expect(
        clippy::cast_precision_loss,
        reason = "a sheet's divider count, far inside f64's integers"
    )]
    let dy = sum(horiz.iter().map(|d| d.y + d.h / 2.0)) / horiz.len() as f64;
    if ((court.y + court.h / 2.0) > dy) != (main.y > dy) {
        return Ok(vec![format!(
            "the hearing court at svg({},{}) lies on the far side of the divider from the main gate - the public court is at the gate, the private court behind",
            fixed(court.x, 0),
            fixed(court.y, 0)
        )]);
    }
    Ok(Vec::new())
}

/// A TREE STANDS ON OPEN GROUND AND ON NOTHING ELSE (feature 257; the GM, 2026-09-20): how far a canopy of radius `r` at (cx, cy) reaches
/// into `rect` (px); zero or less is clear of it.
fn canopy_depth(cx: f64, cy: f64, r: f64, rect: &Rect) -> f64 {
    let dx = max(max(rect.x - cx, 0.0), cx - rect.x2());
    let dy = max(max(rect.y - cy, 0.0), cy - rect.y2());
    r - hypot(dx, dy)
}

/// Everything a canopy may not cover, named: built footprints, furniture, walls, the fence, glyphs, tubs - open ground (the precinct, a
/// court, a garden bed - any pattern-filled or open-feature rect) left out.
fn things_under_a_tree(plan: &ParsedPlan) -> Vec<(&'static str, &Rect)> {
    let ground = |r: &Rect| plan.interior.contains(r) || plan.open_features.contains(r);
    let mut out: Vec<(&str, &Rect)> = plan.structures.iter().map(|r| ("a building", r)).collect();
    out.extend(
        plan.furniture
            .iter()
            .filter(|r| !ground(r) && !r.fill.starts_with("url(") && !plan.structures.contains(r))
            .map(|r| ("furniture", r)),
    );
    out.extend(plan.wall_bands.iter().map(|r| ("a wall", r)));
    out.extend(plan.dividers.iter().map(|r| ("a divider", r)));
    out.extend(plan.fence_segs.iter().map(|r| ("the fence", r)));
    out.extend(plan.glyphs.iter().map(|r| ("a glyph", r)));
    out.extend(plan.tubs.iter().map(|r| ("a fire-water tub", r)));
    out
}

/// Trunks closer than this share of the smaller crown's radius are one tree drawn twice (a GUESS, spec 270 R2).
pub const DUPLICATE_TREE_FRACTION: f64 = 1.0 / 3.0;

/// Every canopy that covers something that is not open ground, and every tree drawn on top of another (crowns may overlap each other,
/// feature 270, the GM 2026-09-27: "tree crowns may overlap, I never said they couldn't").
#[must_use]
pub fn trees_overlap(plan: &ParsedPlan, tol: f64) -> Vec<String> {
    let mut out = Vec::new();
    let things = things_under_a_tree(plan);
    let trees: Vec<(f64, f64, f64)> = plan
        .trees
        .iter()
        .map(|t| (t.x + t.w / 2.0, t.y + t.h / 2.0, t.w / 2.0))
        .collect();
    for &(cx, cy, r) in &trees {
        for (kind, rect) in &things {
            let depth = canopy_depth(cx, cy, r, rect);
            if depth > tol {
                out.push(format!(
                    "a tree at svg({},{}) ({} ft canopy) reaches {} ft into {kind} at svg({},{})",
                    fixed(cx, 0),
                    fixed(cy, 0),
                    fixed(2.0 * r / FTPX, 0),
                    fixed(depth / FTPX, 1),
                    fixed(rect.x, 0),
                    fixed(rect.y, 0)
                ));
            }
        }
    }
    for (i, &(ax, ay, ar)) in trees.iter().enumerate() {
        for &(bx, by, br) in &trees[i + 1..] {
            let gap = hypot(ax - bx, ay - by);
            if gap < min(ar, br) * DUPLICATE_TREE_FRACTION {
                out.push(format!(
                    "a tree at svg({},{}) is drawn on top of the tree at svg({},{}) - their trunks stand {} ft apart",
                    fixed(bx, 0),
                    fixed(by, 0),
                    fixed(ax, 0),
                    fixed(ay, 0),
                    fixed(gap / FTPX, 1)
                ));
            }
        }
    }
    out
}

/// A POSTERN'S APPROACH (feature 374 batch 4, plan R4-2): on each face of its wall a strip as wide as the opening and this deep keeps a
/// clear run.
///
/// Research:
///     gateway approach depth - GUESS: a wall opening keeps a clear strip 6 ft deep, one ken before the wall, on each face; no page gives it.
pub const APPROACH_FT: f64 = 6.0;
/// The clear run a gateway's approach keeps.
///
/// Research:
///     gateway clear run - GUESS: the gateway approach keeps a clear run of 3 ft, room for a carrier and a handcart; no page gives it.
pub const CLEAR_FT: f64 = 3.0;

/// Each wall opening whose approach on one face has no clear run of [`CLEAR_FT`] within [`APPROACH_FT`] of the wall; a building
/// STRADDLING the wall's ink is the wall-broken-around-a-structure idiom, not counted.
#[must_use]
pub fn postern_approach(plan: &ParsedPlan) -> Vec<String> {
    let mut out = Vec::new();
    for o in wall_openings(plan) {
        let depth = APPROACH_FT * FTPX;
        for (a1, a2) in [
            (o.across1 - depth, o.across1),
            (o.across2, o.across2 + depth),
        ] {
            let mut spans: Vec<(f64, f64)> = Vec::new();
            for r in &plan.structures {
                let (s1, s2, t1, t2) = if o.horiz {
                    (r.x, r.x2(), r.y, r.y2())
                } else {
                    (r.y, r.y2(), r.x, r.x2())
                };
                if t1 <= o.across1 && t2 >= o.across2 {
                    continue;
                }
                if min(t2, a2) - max(t1, a1) > 0.0 && min(s2, o.span2) - max(s1, o.span1) > 0.0 {
                    spans.push((max(s1, o.span1), min(s2, o.span2)));
                }
            }
            spans.sort_by(|a, b| {
                a.0.partial_cmp(&b.0)
                    .unwrap_or(std::cmp::Ordering::Equal)
                    .then(a.1.partial_cmp(&b.1).unwrap_or(std::cmp::Ordering::Equal))
            });
            let (mut free, mut at) = (0.0, o.span1);
            for (s1, s2) in spans {
                free = max(free, s1 - at);
                at = max(at, s2);
            }
            free = max(free, o.span2 - at);
            if free < CLEAR_FT * FTPX {
                out.push(format!(
                    "the {} ft opening at svg({},{}) has {} ft clear on one face (under {} ft) - a building seals the way through",
                    fixed(o.ft, 1),
                    fixed(o.x, 0),
                    fixed(o.y, 0),
                    fixed(free / FTPX, 1),
                    fixed(CLEAR_FT, 0)
                ));
                break;
            }
        }
    }
    out
}
