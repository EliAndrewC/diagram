//! Where a sheet's roads go (feature 449 T175, `pack_audit/roads.py` whole; feature 294, plan B21 and B23): a road leaves the frame or
//! arrives somewhere ([`roads_leave_the_frame`]: a MAP DRAWING CONVENTION, the approach runs off the viewBox edge, never a stub stopping
//! short), and a road into a gate is no wider than the gate it feeds ([`gate_feeds_its_road`], research 0093; one-sided).
//!
//! A road is a stroked path or line tagged `road` or `footpath`, its ink width its stroke; a road drawn twice is one road.
//!
//! Research:
//!     the roads - NONE: a sheet's tagged ways measured against the conventions and the tolerance whose claim stands on it, deciding nothing more

use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_gate_research::pyre::py;
use l7r_gate_research::Error;

use super::checks::{main_gate_passage_ft, max_of, min_of, wall_openings, WallOpening};
use super::program_rules::entrances;
use super::Sheet;
use crate::grids::FTPX;
use crate::parse::ParsedPlan;
use crate::py::{fixed, float, hypot, max, min};
use crate::tagged::Mark;

/// The kinds a road is drawn under: the hand manors' `road`, the shrine's `footpath`.
pub const ROAD_KINDS: [&str; 2] = ["road", "footpath"];
/// The kinds an arch is drawn under (a shrine's way ends at its torii).
pub const ARCH_KINDS: [&str; 1] = ["torii"];
/// The places a way inside a precinct is walked TO (drawing convention, feature 294 escalation-check 2026-10-01).
pub const DESTINATION_KINDS: [&str; 2] = ["well", "precinct clearing"];
/// A road may be this much wider than the gate it feeds: the 3 px authoring grain.
///
/// Research:
///     road wider than gate - NONE: a road may be 1 ft wider than the gate it feeds, the 3 px authoring grain.
pub const ROAD_GATE_TOL_FT: f64 = 1.0;

static VIEWBOX: LazyLock<Regex> =
    LazyLock::new(|| py(r#"viewBox="\s*([\-\d.]+)\s+([\-\d.]+)\s+([\d.]+)\s+([\d.]+)\s*""#));

/// A box `(x0, y0, x1, y1)`.
pub type Frame = (f64, f64, f64, f64);

/// One road: its points in order and its ink width (px).
#[derive(Debug, Clone, PartialEq)]
pub struct Road {
    pub pts: Vec<(f64, f64)>,
    pub width: f64,
}

impl Road {
    #[must_use]
    pub fn half(&self) -> f64 {
        self.width / 2.0
    }

    /// From (px, py) to the road's centerline.
    #[must_use]
    pub fn distance(&self, px: f64, py: f64) -> f64 {
        if self.pts.len() == 1 {
            return hypot(px - self.pts[0].0, py - self.pts[0].1);
        }
        min_of(
            self.pts.windows(2).map(|w| seg(px, py, w[0], w[1])),
            f64::INFINITY,
        )
    }
}

/// From a point to a segment.
pub(crate) fn seg(px: f64, py: f64, a: (f64, f64), b: (f64, f64)) -> f64 {
    let ((ax, ay), (bx, by)) = (a, b);
    let (dx, dy) = (bx - ax, by - ay);
    if dx == 0.0 && dy == 0.0 {
        return hypot(px - ax, py - ay);
    }
    let t = max(
        0.0,
        min(1.0, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)),
    );
    hypot(px - ax - t * dx, py - ay - t * dy)
}

fn box_distance(px: f64, py: f64, b: Frame) -> f64 {
    let (x0, y0, x1, y1) = b;
    hypot(
        max(max(x0 - px, 0.0), px - x1),
        max(max(y0 - py, 0.0), py - y1),
    )
}

/// Every road on the sheet, each drawn path once (the widest where one line is inked twice), in the order first drawn.
///
/// # Errors
/// The sheet's marks refused.
pub fn roads(svg: &Sheet) -> Result<Vec<Road>, Error> {
    let mut out: Vec<Road> = Vec::new();
    for m in svg.marks()? {
        if matches!(m.tag.as_str(), "path" | "line")
            && m.kind.as_deref().is_some_and(|k| ROAD_KINDS.contains(&k))
            && m.pts.len() >= 2
        {
            let width = m.stroke_width()?;
            match out.iter_mut().find(|r| r.pts == m.pts) {
                Some(r) => r.width = max(r.width, width),
                None => out.push(Road {
                    pts: m.pts.clone(),
                    width: max(0.0, width),
                }),
            }
        }
    }
    Ok(out)
}

/// A wall opening's gateway rect: the gap along the wall by the ink's thickness.
#[must_use]
pub fn opening_box(o: &WallOpening) -> Frame {
    if o.horiz {
        (o.span1, o.across1, o.span2, o.across2)
    } else {
        (o.across1, o.span1, o.across2, o.span2)
    }
}

/// The box the `main gate`'s posts bound - its passage and the posts themselves; None without posts.
#[must_use]
pub fn gate_passage_box(plan: &ParsedPlan) -> Option<Frame> {
    let posts = &plan.gate_posts;
    if posts.is_empty() {
        return None;
    }
    Some((
        min_of(posts.iter().map(|r| r.x), 0.0),
        min_of(posts.iter().map(|r| r.y), 0.0),
        max_of(posts.iter().map(crate::parse::Rect::x2), 0.0),
        max_of(posts.iter().map(crate::parse::Rect::y2), 0.0),
    ))
}

/// The widths (ft) of every gate an end at `end` meets within `reach` px: a wall opening's gateway, the main gate's passage.
#[must_use]
pub fn gates_met(end: (f64, f64), reach: f64, plan: &ParsedPlan) -> Vec<f64> {
    let (px, py) = end;
    let mut out: Vec<f64> = wall_openings(plan)
        .iter()
        .filter(|o| box_distance(px, py, opening_box(o)) <= reach)
        .map(|o| o.ft)
        .collect();
    if let (Some(b), Some(ft)) = (gate_passage_box(plan), main_gate_passage_ft(plan)) {
        if box_distance(px, py, b) <= reach {
            out.push(ft);
        }
    }
    out
}

fn meets_a_mark<'m>(end: (f64, f64), reach: f64, ms: impl IntoIterator<Item = &'m Mark>) -> bool {
    ms.into_iter()
        .any(|m| box_distance(end.0, end.1, (m.x, m.y, m.x2(), m.y2())) <= reach)
}

/// The sheet's viewBox as a box, None without one.
///
/// Research:
///     the sheet's frame - NONE: the viewBox's four numbers read as a box, deciding nothing about the place
///
/// # Errors
/// A viewBox number `float()` refuses (the pattern takes `1.2.3`).
pub fn frame(svg: &str) -> Result<Option<Frame>, Error> {
    let Some(found) = VIEWBOX.captures(svg).ok().flatten() else {
        return Ok(None);
    };
    let (left, top) = (float(&found[1])?, float(&found[2])?);
    let (width, height) = (float(&found[3])?, float(&found[4])?);
    Ok(Some((left, top, left + width, top + height)))
}

/// What the road's end at `end` meets - 'the frame', 'a gate', 'a door', 'an arch', 'a road', 'a well or clearing' - or None.
///
/// # Errors
/// The viewBox or the sheet's marks refused.
pub fn end_meets(
    end: (f64, f64),
    road: &Road,
    others: &[&Road],
    svg: &Sheet,
    plan: &ParsedPlan,
) -> Result<Option<&'static str>, Error> {
    let (px, py) = end;
    if let Some((x0, y0, x1, y1)) = frame(svg.text)? {
        if min(min(min(px - x0, x1 - px), py - y0), y1 - py) <= road.half() {
            return Ok(Some("the frame"));
        }
    }
    if !gates_met(end, road.half(), plan).is_empty() {
        return Ok(Some("a gate"));
    }
    if meets_a_mark(end, road.half(), &entrances(svg, plan)?) {
        return Ok(Some("a door"));
    }
    let ms = svg.marks()?;
    let arches = ms.iter().filter(|m| {
        m.kind.as_deref().is_some_and(|k| ARCH_KINDS.contains(&k)) || m.ident == "arch"
    });
    if meets_a_mark(end, road.half(), arches) {
        return Ok(Some("an arch"));
    }
    if others.iter().any(|o| o.distance(px, py) <= o.half()) {
        return Ok(Some("a road"));
    }
    let places = ms.iter().filter(|m| {
        m.kind
            .as_deref()
            .is_some_and(|k| DESTINATION_KINDS.contains(&k))
    });
    if meets_a_mark(end, road.half(), places) {
        return Ok(Some("a well or clearing"));
    }
    Ok(None)
}

/// Each end of every road meets the frame (within half its ink of the edge, or past it), a gate, a door, an arch, or another road's ink;
/// an end that meets none is a stub stopping short.
///
/// # Errors
/// The viewBox or the sheet's marks refused.
pub fn roads_leave_the_frame(svg: &Sheet, plan: &ParsedPlan) -> Result<Vec<String>, Error> {
    let rs = roads(svg)?;
    let mut out = Vec::new();
    for (i, road) in rs.iter().enumerate() {
        let others: Vec<&Road> = rs
            .iter()
            .enumerate()
            .filter(|(j, _)| *j != i)
            .map(|(_, o)| o)
            .collect();
        for end in [road.pts[0], road.pts[road.pts.len() - 1]] {
            if end_meets(end, road, &others, svg, plan)?.is_none() {
                out.push(format!(
                    "a {} ft road ends at svg({},{}) in the open - it runs off the frame or arrives at a gate, a door, an arch or another road",
                    fixed(road.width / FTPX, 1),
                    fixed(end.0, 0),
                    fixed(end.1, 0)
                ));
            }
        }
    }
    Ok(out)
}

/// A road ending at a gate is no wider than the widest gate that end meets, plus `tol_ft`.
///
/// # Errors
/// The sheet's marks refused.
pub fn gate_feeds_its_road(
    svg: &Sheet,
    plan: &ParsedPlan,
    tol_ft: f64,
) -> Result<Vec<String>, Error> {
    let mut out = Vec::new();
    for road in roads(svg)? {
        for end in [road.pts[0], road.pts[road.pts.len() - 1]] {
            let met = gates_met(end, road.half(), plan);
            let w_ft = road.width / FTPX;
            if met.is_empty() {
                continue;
            }
            let widest = max_of(met.iter().copied(), 0.0);
            if w_ft > widest + tol_ft {
                out.push(format!(
                    "a {} ft road meets a {} ft gate at svg({},{}) - a road is no wider than the gate it feeds",
                    fixed(w_ft, 1),
                    fixed(widest, 1),
                    fixed(end.0, 0),
                    fixed(end.1, 0)
                ));
            }
        }
    }
    Ok(out)
}

#[cfg(test)]
mod tests {
    use super::Road;

    #[test]
    fn a_road_of_one_point_is_measured_to_it() {
        // no road the sheet draws has one point (`roads` keeps two or more); the Python's branch is kept
        let road = Road {
            pts: vec![(0.0, 0.0)],
            width: 2.0,
        };
        assert_eq!((road.distance(3.0, 4.0), road.half()), (5.0, 1.0));
    }
}
