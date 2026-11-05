//! The rules the track out asks (feature 444 T30): it bends like a path, no long leg runs through a building, it lies on nothing
//! the overlap matrix forbids a way on, and it crosses each brook at most once (`ways/track.py` `connector_keeps_the_law`;
//! `law/shape.py` `bends_badly`, `law/ends.py` `breaks_through`, `law_water.py` `crossing_points`, `overlap/registry.py`
//! `forbidden_segment`).
//!
//! Research:
//!     the track's law - NONE: each rule's claim is at its function or constant
#![expect(
    clippy::many_single_char_names,
    clippy::cast_possible_truncation,
    reason = "the plane geometry's own names, and grid cells of a few hundred"
)]

use std::collections::{BTreeSet, HashMap};

use super::Counts;
use crate::field::fan::Pt;
use crate::field::geom::dist;
use crate::ways::squaring::kink_spans;
use crate::ways::track::{poly_box, seg_intersect, segments_cross, Box4};

/// A leg longer than this whose midpoint stands in a building's box has run straight through it (ft).
///
/// Research:
///     a leg long enough to break - GUESS: no source could speak to it, a value of ours (feature 417 T29 pass A2, 2026-10-25); only a leg over `BREAK_SPAN_FT` (60 ft) with its midpoint in a building counts
pub const BREAK_SPAN_FT: f64 = 60.0;

/// The placer's margin each side of a way's width when the matrix is asked of it (ft).
///
/// Research:
///     its drawn sizes - CONVENTION: sizes on the sheet, not in the world - 0.2 (the placer's margin either side of a way)
pub const PLACER_MARGIN_FT: f64 = 0.2;

/// The connector's tread (ft).
///
/// Research:
///     connector width - research/questions/0081-village-lanes.drawing.html: 6 ft
pub const CONNECTOR_WIDTH_FT: f64 = 6.0;

/// Does the run fail to bend like a path?
///
/// Research:
///     bends like a path - research/questions/0081-village-lanes.drawing.html: no hairpin, no zigzag
#[must_use]
pub fn bends_badly(p: &[Pt]) -> bool {
    !kink_spans(p).is_empty()
}

/// Each leg of the run longer than the break span whose midpoint stands inside one of the buildings' boxes (houses, farm sheds
/// and byres), with its midpoint.
///
/// Research:
///     no tread through a building - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html
#[must_use]
pub fn breaks_through(p: &[Pt], solid: &[Box4]) -> Vec<(usize, Pt)> {
    p.windows(2)
        .enumerate()
        .filter(|(_, w)| dist(w[0], w[1]) > BREAK_SPAN_FT)
        .map(|(k, w)| {
            (
                k,
                (f64::midpoint(w[0].0, w[1].0), f64::midpoint(w[0].1, w[1].1)),
            )
        })
        .filter(|(_, m)| {
            solid
                .iter()
                .any(|b| b.0 <= m.0 && m.0 <= b.2 && b.1 <= m.1 && m.1 <= b.3)
        })
        .collect()
}

fn cell(v: f64) -> i64 {
    (v / 64.0).floor() as i64
}

/// Every crossing of the course by the run, as its run segment and point, in the run's order: the course's segments filed by
/// 64 ft cell once, each run segment asking the cells its box covers.
///
/// Research:
///     each brook crossed at most once - research/questions/0035-villages-beside-their-stream-one-bank-or-both.drawing.html
///     its salts, guards and sentinels - NONE: they decide nothing about the place - 64 (spatial-index cell)
#[must_use]
pub fn crossing_points(p: &[Pt], course: &[Pt], tests: &mut Counts) -> Vec<(usize, Pt)> {
    tests.add("pt_test@crossing_points", course.len() as u64);
    crossing_points_in(p, course, poly_box(course), tests)
}

/// `crossing_points` with the course's box known (`Waters`, `Tree`: read once where the courses are held): none where the run's box
/// misses it, the course filed only where it meets (a household's way, short and far from the brook, filed the whole course afresh on
/// every ask - 9 million cells at 40, the work-budget run of 2026-11-05).
#[must_use]
pub fn crossing_points_in(
    p: &[Pt],
    course: &[Pt],
    cb: Box4,
    tests: &mut Counts,
) -> Vec<(usize, Pt)> {
    if p.len() < 2 || course.len() < 2 {
        return Vec::new();
    }
    tests.add("pt_test@crossing_points", p.len() as u64);
    let rb = poly_box(p);
    if rb.2 < cb.0 || cb.2 < rb.0 || rb.3 < cb.1 || cb.3 < rb.1 {
        return Vec::new();
    }
    let mut grid: HashMap<(i64, i64), Vec<usize>> = HashMap::new();
    for (j, w) in course.windows(2).enumerate() {
        let b = poly_box(w);
        for i in cell(b.0)..=cell(b.2) {
            for k in cell(b.1)..=cell(b.3) {
                grid.entry((i, k)).or_default().push(j);
                tests.add("write@crossing_points", 1);
            }
        }
    }
    let mut out = Vec::new();
    for (k, w) in p.windows(2).enumerate() {
        let (a, b) = (w[0], w[1]);
        let bx = poly_box(w);
        let near: BTreeSet<usize> = (cell(bx.0)..=cell(bx.2))
            .flat_map(|i| (cell(bx.1)..=cell(bx.3)).map(move |m| (i, m)))
            .filter_map(|c| grid.get(&c))
            .flatten()
            .copied()
            .collect();
        tests.add("seg_test@crossing_points", near.len() as u64);
        out.extend(near.into_iter().filter_map(|j| {
            let (c, d) = (course[j], course[j + 1]);
            segments_cross(a, b, c, d)
                .then(|| seg_intersect(a, b, c, d))
                .flatten()
                .map(|x| (k, x))
        }));
    }
    out
}

/// Do two convex polygons overlap (the separating axes; touching edges do not count)?
#[must_use]
pub fn sat_overlap(p: &[Pt], q: &[Pt]) -> bool {
    [p, q].iter().all(|poly| {
        (0..poly.len()).all(|i| {
            let (a, b) = (poly[i], poly[(i + 1) % poly.len()]);
            let (nx, ny) = (-(b.1 - a.1), b.0 - a.0);
            let span = |s: &[Pt]| {
                s.iter().fold((f64::INFINITY, f64::NEG_INFINITY), |m, v| {
                    let d = nx * v.0 + ny * v.1;
                    (m.0.min(d), m.1.max(d))
                })
            };
            let (pa, qa) = (span(p), span(q));
            !(pa.1 < qa.0 || qa.1 < pa.0)
        })
    })
}

/// A segment's ribbon at half-width `hw`: its four corners.
#[must_use]
pub fn ribbon(a: Pt, b: Pt, hw: f64) -> [Pt; 4] {
    let l = dist(a, b);
    let l = if l == 0.0 { 1.0 } else { l };
    let (nx, ny) = (-(b.1 - a.1) / l * hw, (b.0 - a.0) / l * hw);
    [
        (a.0 + nx, a.1 + ny),
        (b.0 + nx, b.1 + ny),
        (b.0 - nx, b.1 - ny),
        (a.0 - nx, a.1 - ny),
    ]
}

/// The first segment of the run, drawn `width` wide and the placer's margin each side, rounded to the record's 0.1 ft, that lies
/// on one of the extents the matrix forbids a way on (each with its box); None where it lies on none.
///
/// Research:
///     nothing the matrix forbids - research/questions/0081-village-lanes.drawing.html, research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: no dry plot, well or steading part
#[must_use]
pub fn forbidden_segment(
    p: &[Pt],
    width: f64,
    forbidding: &[(Vec<Pt>, Box4)],
    tests: &mut Counts,
) -> Option<usize> {
    let r = |v: f64| (v * 10.0).round() / 10.0;
    p.windows(2).position(|w| {
        let (a, b) = ((r(w[0].0), r(w[0].1)), (r(w[1].0), r(w[1].1)));
        let q = ribbon(a, b, width / 2.0 + PLACER_MARGIN_FT);
        let qb = poly_box(&q);
        tests.add("index_examined@forbidden_segment", forbidding.len() as u64);
        forbidding.iter().any(|(e, eb)| {
            !(qb.2 < eb.0 || qb.0 > eb.2 || qb.3 < eb.1 || qb.1 > eb.3) && sat_overlap(&q, e)
        })
    })
}

/// May the run be drawn as the connector: it bends like a path, no leg runs through a building, it lies on nothing the matrix
/// forbids a way on, and it crosses each brook at most once?
///
/// Research:
///     no building on the connector - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: no leg through a building's box
///     bends like a path - research/questions/0081-village-lanes.drawing.html: no hairpin and no zigzag on the track out either
#[must_use]
pub fn connector_keeps_the_law(
    run: &[Pt],
    solid: &[Box4],
    forbidding: &[(Vec<Pt>, Box4)],
    brooks: &[Vec<Pt>],
    tests: &mut Counts,
) -> bool {
    breaks_through(run, solid).is_empty()
        && !bends_badly(run)
        && forbidden_segment(run, CONNECTOR_WIDTH_FT, forbidding, tests).is_none()
        && brooks
            .iter()
            .all(|b| crossing_points(run, b, tests).len() <= 1)
}
