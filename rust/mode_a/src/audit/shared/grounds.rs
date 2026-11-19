//! The program's own grounds (feature 449 T175, the rest of `shared.py`): the country shrine's checks, each reading a DECLARED feature by
//! id (feature 254, D8) - [`sanctuary_on_axis`], [`arch_on_approach`], [`well_clear_of_arch`], [`no_precinct_enclosure`],
//! [`hall_at_an_end`] - and the compound's tagged ones: [`one_compound_shrine`], [`stall_width`], [`shrine_tree`], [`well_gear`].
//!
//! Research:
//!     the program's grounds - NONE: lookups, geometry and the tag patterns the checks read by, deciding nothing; each check of the shrine's and the compound's grounds carries its own claim

use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_gate_research::pyre::py;
use l7r_gate_research::Error;

use super::lap;
use crate::audit::checks::{first_max, WALL_OVERLAP_MIN_PX};
use crate::audit::Sheet;
use crate::grids::FTPX;
use crate::parse::{is_structure, ParsedPlan, Rect, WALL_STROKE, WELL_FILL};
use crate::py::{fixed, float, hypot, max, min};
use crate::tagged::Mark;

/// The sanctuary's center may stray this far from the approach axis.
///
/// Research:
///     shrine axis tolerance - GUESS: no page says how exactly a sanctuary sat on its approach's axis; its center may stray 3 ft from it.
pub const AXIS_TOL_FT: f64 = 3.0;
/// The arch stands AT the precinct edge: within this of it.
///
/// Research:
///     arch edge tolerance - GUESS: no page gives it; the arch stands within 2 ft of the precinct edge.
pub const EDGE_TOL_FT: f64 = 2.0;

fn one<'p>(plan: &'p ParsedPlan, ident: &str) -> Option<&'p Rect> {
    plan.by_id(ident).first().copied()
}

fn center(r: &Rect) -> (f64, f64) {
    (r.x + r.w / 2.0, r.y + r.h / 2.0)
}

/// The sanctuary stands on the approach's axis, BEHIND the hall (farther from the arch than the hall).
///
/// Research:
///     the sanctuary behind the hall - research/questions/0222-inside-a-village-shrines-precinct-halls-basin-sacred-tree-and-offerings-keidai.drawing.html: the sanctuary stands at the rear of the shrine, behind the hall on the worship hall's axis.
///     the approach on the same axis - CONVENTION: the approach runs on the hall's and the sanctuary's axis, a map drawing convention research/questions/0222-inside-a-village-shrines-precinct-halls-basin-sacred-tree-and-offerings-keidai.drawing.html records, neither of its sources naming the approach.
#[must_use]
pub fn sanctuary_on_axis(plan: &ParsedPlan, tol_ft: f64) -> Vec<String> {
    let named = ["hall", "sanctuary", "approach", "arch"].map(|k| (k, one(plan, k)));
    let missing: Vec<&str> = named
        .iter()
        .filter(|(_, v)| v.is_none())
        .map(|(k, _)| *k)
        .collect();
    let [(_, Some(hall)), (_, Some(sanctuary)), (_, Some(approach)), (_, Some(arch))] = named
    else {
        return vec![format!(
            "the sheet declares no {} (mark the rect id=\"<name>\")",
            missing.join(" / ")
        )];
    };
    let vertical = approach.h >= approach.w;
    let (ax, ay) = center(approach);
    let (sx, sy) = center(sanctuary);
    let (hx, hy) = center(hall);
    let (gx, gy) = center(arch);
    let off = if vertical {
        (sx - ax).abs()
    } else {
        (sy - ay).abs()
    };
    let mut out = Vec::new();
    if off > tol_ft * FTPX {
        out.push(format!(
            "the sanctuary's center is {} ft off the approach axis",
            fixed(off / FTPX, 1)
        ));
    }
    let along = |v: f64| {
        if vertical {
            (v - gy).abs()
        } else {
            (v - gx).abs()
        }
    };
    if along(if vertical { sy } else { sx }) <= along(if vertical { hy } else { hx }) {
        out.push(
            "the sanctuary stands nearer the arch than the hall - it belongs BEHIND the hall on the axis"
                .to_owned(),
        );
    }
    out
}

const NO_APPROACH: &str =
    "the sheet declares no approach / arch (mark the rects id=\"approach\", id=\"arch\")";

/// The counts of arches an avenue takes (0220's drawing page: one, three or seven, a deliberate deviation of the setting's).
///
/// Research:
///     the arch count - DEVIATION research/questions/0220-shrine-gateways-and-the-approach-to-the-hall-torii-sando.drawing.html: a shrine's approach runs under one, three or seven arches, the counts the page records as a deliberate deviation.
pub const ARCH_COUNTS: [usize; 3] = [1, 3, 7];
/// The innermost arch off the hall's nearest face (ft).
///
/// Research:
///     the innermost arch off the hall - CONVENTION: the innermost arch stands 12 ft off the hall's nearest face, measured to the building's outline, a map drawing convention research/questions/0220-shrine-gateways-and-the-approach-to-the-hall-torii-sando.drawing.html records.
pub const INNERMOST_FT: f64 = 12.0;
/// The innermost arch's play about its distance off the hall (ft).
///
/// Research:
///     the innermost arch's tolerance - GUESS: the innermost arch passes within 2 ft of its 12 ft off the hall, the arch edge tolerance's figure; no page gives it.
pub const INNERMOST_TOL_FT: f64 = 2.0;

/// The clear distance between two rects (zero where they touch or overlap).
fn box_gap(a: &Rect, b: &Rect) -> f64 {
    let dx = max(max(a.x - b.x2(), b.x - a.x2()), 0.0);
    let dy = max(max(a.y - b.y2(), b.y - a.y2()), 0.0);
    hypot(dx, dy)
}

/// The arches straddle the approach, one, three or seven of them, and the first - the one farthest from the hall - stands where the way
/// enters the precinct, unless the innermost stands its 12 ft off the hall, which holds where both cannot (feature 449 T177: the check
/// judged one arch, in document order, and refused a first arch moved inward for the innermost).
///
/// Research:
///     the arch over the approach at the ground's edge - research/questions/0220-shrine-gateways-and-the-approach-to-the-hall-torii-sando.drawing.html, research/questions/0222-inside-a-village-shrines-precinct-halls-basin-sacred-tree-and-offerings-keidai.drawing.html: the approach runs under its arches, and the first arch stands where the approach enters the shrine's ground.
///     the first arch moved for the innermost - research/questions/0220-shrine-gateways-and-the-approach-to-the-hall-torii-sando.drawing.html: where the first arch and the innermost cannot both keep their places, the innermost holds and the first arch moves with the run, off the place where the approach enters the shrine's ground.
///
/// # Errors
/// A plan with no interior: the Python's `min()` of nothing in `bounds`.
pub fn arch_on_approach(plan: &ParsedPlan, edge_tol_ft: f64) -> Result<Vec<String>, Error> {
    let arches = plan.by_id("arch");
    let (Some(approach), Some(&leading)) = (one(plan, "approach"), arches.first()) else {
        return Ok(vec![NO_APPROACH.to_owned()]);
    };
    let mut out = Vec::new();
    if !ARCH_COUNTS.contains(&arches.len()) {
        out.push(format!(
            "the approach runs under {} arches - a shrine's avenue is one, three or seven",
            arches.len()
        ));
    }
    if arches.iter().any(|a| {
        let (lx, ly) = lap(approach, a);
        lx <= 0.0 || ly <= 0.0
    }) {
        out.push(
            "the arch does not straddle the approach - a gateway stands over the way".to_owned(),
        );
    }
    let hall = one(plan, "hall");
    let (mut first, mut innermost) = (leading, leading);
    if let Some(h) = hall {
        // strict comparisons, so the first of equals is kept, as the Python's loop keeps it
        for &a in &arches[1..] {
            if box_gap(a, h) > box_gap(first, h) {
                first = a;
            }
            if box_gap(a, h) < box_gap(innermost, h) {
                innermost = a;
            }
        }
    }
    let (left, top, right, bottom) = plan.bounds()?;
    let (gx, gy) = center(first);
    let reach = edge_tol_ft * FTPX;
    let edge = min(
        min(min((gx - left).abs(), (gx - right).abs()), (gy - top).abs()),
        (gy - bottom).abs(),
    );
    let at_edge = edge <= reach + max(first.w, first.h) / 2.0;
    let held = hall.is_some_and(|h| {
        (box_gap(innermost, h) - INNERMOST_FT * FTPX).abs() <= INNERMOST_TOL_FT * FTPX
    });
    if !at_edge && !held {
        out.push(
            "the arch stands inside the precinct rather than at its edge, where the way enters"
                .to_owned(),
        );
    }
    Ok(out)
}

/// The basin, and the shrine's own well, stand beside the approach, never on it and never under an arch (feature 449 T182: the check judged
/// the well alone, under the basin's claim, and the first arch alone - the basin 0222 places beside the approach was judged by nothing,
/// and the well is 0196's, a shrine's own water).
///
/// Research:
///     the basin beside the approach - research/questions/0222-inside-a-village-shrines-precinct-halls-basin-sacred-tree-and-offerings-keidai.drawing.html: a plain stone basin for rinsing the hands and mouth stands beside the approach at the innermost torii, so the basin a sheet declares (id=basin) is never on the approach or under an arch.
///     a shrine draws its basin - research/questions/0222-inside-a-village-shrines-precinct-halls-basin-sacred-tree-and-offerings-keidai.drawing.html, research/questions/0196-communal-wells-ido.drawing.html: a village shrine has its stone basin beside the approach (0222), and the ablution well a shrine set apart from the houses keeps (0196) comes in addition, never in its place, so a sheet without its basin is refused.
///     the well off the way - research/questions/0196-communal-wells-ido.drawing.html: a shrine's own ablution well (the sheet's id=well or its well-curb fill) stands beside the hall, measured from the hall's edge, so it stands off the approach and clear of the arches.
#[must_use]
pub fn well_clear_of_arch(plan: &ParsedPlan) -> Vec<String> {
    let basins = plan.by_id("basin");
    let declared = plan.by_id("well");
    let wells: Vec<&Rect> = if declared.is_empty() {
        plan.wells.iter().filter(|w| !basins.contains(w)).collect()
    } else {
        declared
    };
    // T182 (its claims round): a well stood in for the basin; 0222 draws the basin at every village shrine, and 0196's well comes in
    // addition
    if basins.is_empty() {
        return vec!["no basin on the sheet - a village shrine has its stone basin beside the approach (mark it id=\"basin\"); a well comes in addition, never in its place".to_owned()];
    }
    let arches = plan.by_id("arch");
    let Some(approach) = one(plan, "approach").filter(|_| !arches.is_empty()) else {
        return vec![NO_APPROACH.to_owned()];
    };
    let on = |w: &Rect, r: &Rect| {
        let (lx, ly) = lap(w, r);
        lx > WALL_OVERLAP_MIN_PX && ly > WALL_OVERLAP_MIN_PX
    };
    let mut out = Vec::new();
    for (what, found) in [("basin", &basins), ("well", &wells)] {
        for w in found {
            for (name, hit) in [
                ("approach", on(w, approach)),
                ("arch", arches.iter().any(|a| on(w, a))),
            ] {
                if hit {
                    out.push(format!(
                        "the {what} at svg({},{}) stands on the {name}",
                        fixed(w.x, 0),
                        fixed(w.y, 0)
                    ));
                }
            }
        }
    }
    out
}

/// A village shrine's precinct is NOT enclosed (feature 268; research 0223): a fence group whose extent takes in the hall, one whose
/// extent takes in the sanctuary (feature 449 T177: it passed, as a richer shrine's donation, where 0223's drawing page draws none
/// however rich the parish), and a compound wall stroke at the sheet's edge, are reported.
///
/// Research:
///     the precinct left open - research/questions/0223-shrine-woods-and-fences-chinju-no-mori-tamagaki.drawing.html: a village shrine's precinct has no fence, wall or hedge round it, so a fence whose extent takes in the hall and a compound wall at the sheet's edge are refused.
///     no fence round the sanctuary - research/questions/0223-shrine-woods-and-fences-chinju-no-mori-tamagaki.drawing.html: no fence is drawn round a village shrine's sanctuary, however rich the parish, so a fence whose extent takes in the sanctuary is refused; a fence lining the approach alone is not judged, the page saying only that none is drawn round the precinct or the sanctuary.
///
/// # Errors
/// A plan with no interior: the Python's `min()` of nothing in `bounds`.
pub fn no_precinct_enclosure(plan: &ParsedPlan) -> Result<Vec<String>, Error> {
    let mut out = Vec::new();
    let (hall, sanctuary) = (one(plan, "hall"), one(plan, "sanctuary"));
    if !plan.fence_segs.is_empty() {
        let fs = &plan.fence_segs;
        let left = crate::audit::checks::min_of(fs.iter().map(|r| r.x), 0.0);
        let top = crate::audit::checks::min_of(fs.iter().map(|r| r.y), 0.0);
        let right = crate::audit::checks::max_of(fs.iter().map(|r| r.x + r.w), 0.0);
        let bottom = crate::audit::checks::max_of(fs.iter().map(|r| r.y + r.h), 0.0);
        let ringed =
            |h: &Rect| left <= h.x && top <= h.y && right >= h.x + h.w && bottom >= h.y + h.h;
        if hall.is_some_and(ringed) {
            out.push("a fence rings the precinct (its extent takes in the hall) - a village shrine's ground is marked by its arch and its wood, with no fence round its precinct or its sanctuary".to_owned());
        } else if sanctuary.is_some_and(ringed) {
            out.push("a fence rings the sanctuary - no fence is drawn round a village shrine's sanctuary, however rich the parish".to_owned());
        }
    }
    let (left, top, right, bottom) = plan.bounds()?;
    let reach = EDGE_TOL_FT * FTPX;
    for band in plan.wall_bands.iter().filter(|b| b.fill == WALL_STROKE) {
        let (cx, cy) = center(band);
        let edge = min(
            min(min((cx - left).abs(), (cx - right).abs()), (cy - top).abs()),
            (cy - bottom).abs(),
        );
        if edge <= reach + max(band.w, band.h) {
            out.push(format!(
                "a compound wall stroke at svg({},{}) bounds the precinct - a village shrine is neither walled nor fenced",
                fixed(band.x, 0),
                fixed(band.y, 0)
            ));
            break;
        }
    }
    Ok(out)
}

static SHRINE_GROUP: LazyLock<Regex> =
    LazyLock::new(|| py(r#"<g data-kind="compound shrine"([^>]*)>"#));

/// A compound draws ONE modest shrine (0218's drawing page, a deliberate deviation); a second kami's own shrine, where the sheet's roll
/// says so, declares `data-form="own shrine"` and is not counted (feature 374 wave 123).
///
/// Research:
///     one shrine per compound - DEVIATION research/questions/0218-the-compounds-own-shrine-yashikigami.drawing.html: a compound draws one modest shrine however many a real office kept, a deliberate deviation; a second kami's own shrine, where the sheet's roll declares one, is not counted.
#[must_use]
pub fn one_compound_shrine(text: &str) -> Vec<String> {
    let main = SHRINE_GROUP
        .captures_iter(text)
        .map_while(Result::ok)
        .filter(|g| !g[1].contains("data-form=\"own shrine\""))
        .count();
    if main > 1 {
        vec![format!("{main} compound shrines drawn - a compound draws one modest shrine; enshrine a second god in its hall, or declare its rolled own shrine data-form=\"own shrine\"")]
    } else {
        Vec::new()
    }
}

/// One ken (~6 ft) a stall, with a drawing's play either side.
///
/// Research:
///     stall width band - research/questions/0108-stables-umaya.drawing.html: a stall is one ken (~6 ft) wide, as the page draws it, with 4.5 to 7.5 ft allowed for a drawing's play.
pub const STALL_FT: (f64, f64) = (4.5, 7.5);

/// A sorted set of floats (an equal value, a negative zero among them, kept once, the first).
fn sorted_set(values: impl IntoIterator<Item = f64>) -> Vec<f64> {
    let mut out: Vec<f64> = Vec::new();
    for v in values {
        if !out.contains(&v) {
            out.push(v);
        }
    }
    out.sort_by(|a, b| a.partial_cmp(b).unwrap_or(std::cmp::Ordering::Equal));
    out
}

/// A warrior's stall was one bay wide, a ken (0108's drawing page; feature 374 wave 126): in each stable (its outlined rect), the
/// partitions drawn across one of its axes part it into spans, and along one axis at least two must be a stall's width.
///
/// Research:
///     at least two stalls - GUESS research/questions/0108-stables-umaya.drawing.html: a stable a few bays long is parted into at least two stalls of a stall's width; the page records the number of horses as a guess.
///
/// # Errors
/// The sheet's marks refused.
pub fn stall_width(svg: &Sheet) -> Result<Vec<String>, Error> {
    let found = svg.marks()?;
    let mut out = Vec::new();
    let bodies = found.iter().filter(|m| {
        m.tag == "rect"
            && m.kind.as_deref() == Some("stables")
            && m.lineage.last().map(String::as_str) == Some("stables")
            && m.paint.get("stroke").map_or("none", String::as_str) != "none"
    });
    for body in bodies {
        let inside: Vec<&Mark> = found
            .iter()
            .filter(|m| {
                m.tag == "line"
                    && m.kind.as_deref() == Some("stables")
                    && body.x <= m.x
                    && m.x2() <= body.x2()
                    && body.y <= m.y
                    && m.y2() <= body.y2()
            })
            .collect();
        let mut best: Vec<f64> = Vec::new();
        let mut parted = false;
        for along_x in [true, false] {
            let (lo, hi) = if along_x {
                (body.x, body.x2())
            } else {
                (body.y, body.y2())
            };
            let cuts = sorted_set(inside.iter().filter_map(|m| {
                let (at, thin) = if along_x {
                    (m.x, m.w < 1.0)
                } else {
                    (m.y, m.h < 1.0)
                };
                (thin && lo < at && at < hi).then_some(at)
            }));
            let edges: Vec<f64> = std::iter::once(lo)
                .chain(cuts)
                .chain(std::iter::once(hi))
                .collect();
            let spans: Vec<f64> = edges.windows(2).map(|w| w[1] - w[0]).collect();
            let stalls = spans
                .iter()
                .filter(|w| STALL_FT.0 * FTPX <= **w && **w <= STALL_FT.1 * FTPX)
                .count();
            if stalls >= 2 {
                parted = true;
                break;
            }
            if best.is_empty() {
                best = spans;
            }
        }
        if !parted {
            let widths: Vec<String> = best.iter().map(|w| fixed(w / FTPX, 1)).collect();
            out.push(format!(
                "the stable at svg({},{}) parts its length into {} ft - draw its stalls one ken (~6 ft) wide",
                fixed(body.x, 0),
                fixed(body.y, 0),
                widths.join(", ")
            ));
        }
    }
    Ok(out)
}

/// An open stretch of the building shorter than this is a partition's gap, not the hall.
///
/// Research:
///     hall span floor - GUESS: no page gives it; an open stretch of a building under 6 ft (one ken) is a partition's gap, not the hall.
pub const HALL_MIN_SPAN_FT: f64 = 6.0;

/// The spans, along the building's long axis, of every mark drawn as a part of its dwelling end (a group tagged
/// `data-part-of="hall and dwelling"`), clipped to the building.
fn dwelling_spans(found: &[Mark], hall: &Rect, along_x: bool) -> Vec<(f64, f64)> {
    let (lo, hi) = if along_x {
        (hall.x, hall.x + hall.w)
    } else {
        (hall.y, hall.y + hall.h)
    };
    let mut spans: Vec<(f64, f64)> = found
        .iter()
        .filter(|m| {
            m.lineage.len() >= 2
                && m.lineage[0] == "hall and dwelling"
                && m.kind.as_deref() != Some("hall and dwelling")
        })
        .filter_map(|m| {
            let (a, b) = if along_x {
                (m.x, m.x2())
            } else {
                (m.y, m.y2())
            };
            (min(b, hi) > max(a, lo)).then(|| (max(a, lo), min(b, hi)))
        })
        .collect();
    spans.sort_by(|a, b| {
        a.0.partial_cmp(&b.0)
            .unwrap_or(std::cmp::Ordering::Equal)
            .then(a.1.partial_cmp(&b.1).unwrap_or(std::cmp::Ordering::Equal))
    });
    spans
}

/// Under one roof the villagers' hall is one END of the building and the monk's dwelling the other (0221's drawing page): the hall is the
/// longest stretch no dwelling part covers, and the dwelling's parts on BOTH sides of it put the hall in the middle.
///
/// Research:
///     the hall at one end - research/questions/0221-the-country-monk-who-keeps-a-village-shrine-and-their-dwelling-kuri.drawing.html: under one roof the villagers' hall is one end of the building and the monk's dwelling the other.
///
/// # Errors
/// The sheet's marks refused.
pub fn hall_at_an_end(svg: &Sheet, plan: &ParsedPlan) -> Result<Vec<String>, Error> {
    let Some(hall) = one(plan, "hall") else {
        return Ok(Vec::new()); // sanctuary_on_axis names a sheet that declares no hall
    };
    let along_x = hall.w >= hall.h;
    let spans = dwelling_spans(svg.marks()?, hall, along_x);
    if spans.is_empty() {
        return Ok(Vec::new());
    }
    let (lo, hi) = if along_x {
        (hall.x, hall.x + hall.w)
    } else {
        (hall.y, hall.y + hall.h)
    };
    let (mut gaps, mut edge) = (Vec::new(), lo);
    for &(a, b) in &spans {
        if a > edge {
            gaps.push((edge, a));
        }
        edge = max(edge, b);
    }
    if hi > edge {
        gaps.push((edge, hi));
    }
    let gaps: Vec<(f64, f64)> = gaps
        .into_iter()
        .filter(|g| g.1 - g.0 >= HALL_MIN_SPAN_FT * FTPX)
        .collect();
    let Some(&(h0, h1)) = first_max(gaps.iter(), |g| g.1 - g.0) else {
        return Ok(Vec::new());
    };
    if spans.iter().any(|&(_, b)| b <= h0) && spans.iter().any(|&(a, _)| a >= h1) {
        return Ok(vec![format!(
            "the hall stands between the dwelling's rooms (svg {}-{} of {}-{}) - under one roof it is one end of the building, the dwelling the other",
            fixed(h0, 0),
            fixed(h1, 0),
            fixed(lo, 0),
            fixed(hi, 0)
        )]);
    }
    Ok(Vec::new())
}

/// THE SHRINE'S TREE (feature 374 wave 130): the compound shrine's `sacred tree` crown stands within this of the hall's walls.
///
/// Research:
///     shrine tree reach - GUESS: the compound shrine's tree trunk stands within 15 ft of the hall's walls; no source gives how near the tree stood.
pub const SHRINE_TREE_FT: f64 = 15.0;

/// The compound shrine stands beside its tree: a `sacred tree` crown that is a part of the `compound shrine`, its trunk within
/// [`SHRINE_TREE_FT`] of the hall (the shrine's largest rect).
///
/// Research:
///     a tree beside the compound shrine - research/questions/0218-the-compounds-own-shrine-yashikigami.drawing.html: the compound's shrine stands beside a tree, where a household kept its god at an old tree; the reach carries a claim of its own.
///
/// # Errors
/// The sheet's marks refused.
pub fn shrine_tree(svg: &Sheet) -> Result<Vec<String>, Error> {
    let found = svg.marks()?;
    let halls = found.iter().filter(|m| {
        m.tag == "rect"
            && m.kind.as_deref() == Some("compound shrine")
            && !m.lineage.iter().any(|k| k == "sacred tree")
    });
    let Some(hall) = first_max(halls, |m| m.w * m.h) else {
        return Ok(Vec::new());
    };
    let crowns = found.iter().filter(|m| {
        m.tag == "circle"
            && m.kind.as_deref() == Some("sacred tree")
            && m.lineage.iter().any(|k| k == "compound shrine")
    });
    for c in crowns {
        let (cx, cy) = (c.x + c.w / 2.0, c.y + c.h / 2.0);
        let dx = max(max(hall.x - cx, 0.0), cx - hall.x - hall.w);
        let dy = max(max(hall.y - cy, 0.0), cy - hall.y - hall.h);
        if hypot(dx, dy) <= SHRINE_TREE_FT * FTPX {
            return Ok(Vec::new());
        }
    }
    Ok(vec![format!(
        "the compound shrine at svg({},{}) has no tree beside it",
        fixed(hall.x, 0),
        fixed(hall.y, 0)
    )])
}

static GEAR: LazyLock<Regex> = LazyLock::new(|| {
    py(
        r#"<g data-kind="well" data-gear="(sweep|pulley frame|beam pulley)" data-at="([\d.]+),([\d.]+)""#,
    )
});
static ROOF: LazyLock<Regex> = LazyLock::new(|| {
    py(r#"(?s)<g data-kind="well" data-roof="1" data-at="([\d.]+),([\d.]+)">(.*?)</g>"#)
});
static OUTLINE: LazyLock<Regex> = LazyLock::new(|| py(r#"<(?:rect|path)[^>]*fill="none""#));

/// The point stands inside a building: a rect of a structure's fill, not a part of a well, holding it.
fn indoor(cx: f64, cy: f64, found: &[Mark]) -> bool {
    found.iter().any(|m| {
        m.tag == "rect"
            && m.kind.as_deref() != Some("well")
            && m.paint.get("fill").is_some_and(|f| is_structure(f))
            && m.x < cx
            && cx < m.x2()
            && m.y < cy
            && cy < m.y2()
    })
}

/// A WELL'S LIFTING GEAR (feature 374 wave 135; research 0196 draws every well with "a well-sweep or a pulley frame over it"): every curb,
/// a rect of the curb's stone tagged a `well` of a curb marker's size, carries a `data-gear` group at its center (within 2 px); an indoor
/// well's gear is the beam pulley and it has no roof, an open-air well's is never the beam pulley; a roof is an unfilled outline on four
/// posts.
///
/// Research:
///     its drawn sizes - CONVENTION: sizes on the sheet, not in the world - 15 (smallest curb marker read as a well (px))
///     every well carries gear - research/questions/0196-communal-wells-ido.drawing.html: a well in the open is drawn with lifting gear over its curb; an indoor well carries the beam pulley, labeled on its own claim.
///     an open-air well's gear - research/questions/0196-communal-wells-ido.drawing.html: a well in the open takes a sweep or a pulley frame, both attested, never the beam pulley.
///     an indoor well's pulley - GUESS research/questions/0196-communal-wells-ido.drawing.html: a well indoors hangs its pulley from the beams, which the page records as a guess, no page naming an indoor well's gear.
///     an indoor well unroofed - research/questions/0196-communal-wells-ido.drawing.html: a well indoors takes no roof of its own, the house already roofing it.
///     a well roof drawn on four posts - CONVENTION: a well's roof is an unfilled outline on four corner posts, so it reads as a roof over the well and not as the paved apron, the map drawing convention research/questions/0196-communal-wells-ido.drawing.html records.
///
/// # Errors
/// A `data-at` number `float()` refuses, or the sheet's marks refused.
pub fn well_gear(svg: &Sheet) -> Result<Vec<String>, Error> {
    let text = svg.text;
    let mut gears = Vec::new();
    for m in GEAR.captures_iter(text).map_while(Result::ok) {
        gears.push((m[1].to_owned(), float(&m[2])?, float(&m[3])?));
    }
    let mut roofs = Vec::new();
    for m in ROOF.captures_iter(text).map_while(Result::ok) {
        roofs.push((float(&m[1])?, float(&m[2])?, m[3].to_owned()));
    }
    let found = svg.marks()?;
    let mut out = Vec::new();
    for m in found {
        if m.tag != "rect"
            || m.kind.as_deref() != Some("well")
            || m.paint.get("fill").map(String::as_str) != Some(WELL_FILL)
            || min(m.w, m.h) < 15.0
        {
            continue;
        }
        let (cx, cy) = (m.x + m.w / 2.0, m.y + m.h / 2.0);
        let at = format!("svg({},{})", fixed(cx, 0), fixed(cy, 0));
        let near = |gx: f64, gy: f64| (gx - cx).abs() <= 2.0 && (gy - cy).abs() <= 2.0;
        let gear = gears
            .iter()
            .find(|(_, gx, gy)| near(*gx, *gy))
            .map(|(g, _, _)| g.as_str());
        let roof = roofs
            .iter()
            .find(|(rx, ry, _)| near(*rx, *ry))
            .map(|(_, _, b)| b.as_str());
        let inside = indoor(cx, cy, found);
        match gear {
            None => out.push(format!("the well at {at} carries no lifting gear")),
            Some(g) if inside && g != "beam pulley" => out.push(format!(
                "the well at {at} stands indoors but draws a {g} - an indoor well hangs its pulley from the beams"
            )),
            Some("beam pulley") if !inside => out.push(format!(
                "the well at {at} stands in the open but draws a beam pulley - its gear is a sweep or a pulley frame"
            )),
            Some(_) => {}
        }
        match roof {
            Some(_) if inside => out.push(format!(
                "the well at {at} stands indoors under its building's roof but draws a roof of its own"
            )),
            Some(body)
                if body.matches("<circle").count() != 4 || !OUTLINE.is_match(body).unwrap_or(false) =>
            {
                out.push(format!(
                    "the roof over the well at {at} is not an outline on four posts - a filled square reads as a paved apron"
                ));
            }
            _ => {}
        }
    }
    Ok(out)
}
