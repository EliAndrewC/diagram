//! The rules a homestead's layout is asked once the ground admitted its envelope (feature 444 T30): the south sun of every yard and
//! bed - its own and the neighbors' - two roofs shedding apart, the farmstead on one bank of the brook, every part off the taken
//! ground, and the yard opening onto ground a way can reach. Each asks the standing homesteads near it through a grid, never all.
//!
//! Research:
//!     yard and bed sun to the south - research/questions/0038-sunlight-and-shade-on-the-farm.drawing.html, research/questions/0037-threshing-and-drying-yards-at-farmhouses-niwa.drawing.html: no house within 39 ft south of a yard or a bed, both directions
//!     roofs shed apart - research/questions/0247-a-houses-setback-from-the-road-and-its-eaves-drip-strip.html: a house's drip ground ran 2 to 3 chi and its eaves 2.2 chi (north China, Qing); the footpath between is ours; 8 ft, two drip lines and a footpath
//!     a farmstead on one bank - GUESS: no part across a stream from its house, nor on the stream
//!     no path searched while houses are seated - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: no way is sought for a household while it is seated; the yard opens onto lane ground connected to the way out

#![expect(
    clippy::manual_midpoint,
    reason = "two half-sizes summed at a map's few hundred feet, where no overflow is possible"
)]

use super::Counts;
use std::collections::HashMap;

use super::bundle::Bundle;
use super::ground::{Ground, Reach, CELL};
use super::layout::Rect;
use crate::field::fan::Pt;

/// The sun corridor south of a yard or a bed, and the placer's margin past it on both axes (feet).
///
/// Research:
///     a yard's south sun - research/questions/0038-sunlight-and-shade-on-the-farm.drawing.html: 39 ft clear south of every yard and bed
///     the placer stricter by a hair - NONE: 2 ft so the finished map's check, which reads the drawn records, never disagrees
pub const SUN_FT: (f64, f64) = (39.0, 2.0);

/// The gap two farmhouses keep wall to wall, and the placer's margin past it (feet).
pub const EAVE_FT: (f64, f64) = (8.0, 2.0);

/// The standing homesteads' grid cell (feet).
///
/// Research:
///     its salts, guards and sentinels - NONE: they decide nothing about the place - 64 (spatial-index cell)
pub const GRID: f64 = 64.0;

/// A homestead standing: its house (drawn rectangle and rake), its yard and beds as drawn, and the box round it.
#[derive(Debug, Clone)]
pub struct Placed {
    /// The house's rectangle and its rake (degrees).
    pub house: (Rect, f64),
    /// The house's box as drawn.
    pub house_box: Rect,
    /// The yard's box as drawn.
    pub yard: Rect,
    /// The beds' boxes as drawn.
    pub beds: Vec<Rect>,
    /// The box round the whole homestead.
    pub bbox: Rect,
    /// Its persimmon's center, where it keeps one.
    pub persimmon: Option<Pt>,
}

/// The standing homesteads, filed in a grid by their boxes.
#[derive(Default)]
pub struct Standing {
    /// The homesteads, in the order they were seated.
    pub all: Vec<Placed>,
    cells: HashMap<(i64, i64), Vec<usize>>,
}

#[expect(
    clippy::cast_possible_truncation,
    reason = "cell indices of a few hundred"
)]
fn cell(v: f64) -> i64 {
    (v / GRID).floor() as i64
}

impl Standing {
    /// File a homestead standing.
    pub fn add(&mut self, p: Placed, tests: &mut Counts) {
        let k = self.all.len();
        let b = p.bbox;
        for i in cell(b.0 - b.2 / 2.0)..=cell(b.0 + b.2 / 2.0) {
            for j in cell(b.1 - b.3 / 2.0)..=cell(b.1 + b.3 / 2.0) {
                self.cells.entry((i, j)).or_default().push(k);
                tests.add("write@add", 1);
            }
        }
        self.all.push(p);
    }

    /// The homesteads whose boxes meet the box from `lo` to `hi`, each once.
    #[must_use]
    pub fn meeting(&self, lo: Pt, hi: Pt, tests: &mut Counts) -> Vec<usize> {
        let mut out: Vec<usize> = Vec::new();
        for i in cell(lo.0)..=cell(hi.0) {
            for j in cell(lo.1)..=cell(hi.1) {
                tests.add("index_examined@meeting", 1);
                for &k in self.cells.get(&(i, j)).map_or(&[][..], Vec::as_slice) {
                    let b = self.all[k].bbox;
                    if !out.contains(&k)
                        && b.0 - b.2 / 2.0 <= hi.0
                        && b.0 + b.2 / 2.0 >= lo.0
                        && b.1 - b.3 / 2.0 <= hi.1
                        && b.1 + b.3 / 2.0 >= lo.1
                    {
                        out.push(k);
                    }
                }
            }
        }
        out
    }
}

/// Does a house box (center, width, height, as drawn) shade a plot box - its north wall within `reach` south of the plot's south
/// edge, overlapping it across the corridor by more than `side`?
#[must_use]
pub fn shades(house: Rect, plot: Rect, reach: f64, side: f64) -> bool {
    (plot.0 - house.0).abs() < (plot.2 + house.2) / 2.0 + side && {
        let gap = (house.1 - house.3 / 2.0) - (plot.1 + plot.3 / 2.0);
        gap > 0.0 && gap < reach
    }
}

/// Does `b` leave every yard and bed its sun - this house shading no standing plot, no standing house shading its plots?
#[must_use]
pub fn sun_ok(b: &Bundle, standing: &Standing, tests: &mut Counts) -> bool {
    let (reach, side) = (SUN_FT.0 + SUN_FT.1, SUN_FT.1);
    let house = b.boxes[0];
    let north = house.1 - house.3 / 2.0;
    let lo = (house.0 - house.2 / 2.0 - side, north - reach);
    let hi = (house.0 + house.2 / 2.0 + side, north);
    for k in standing.meeting(lo, hi, tests) {
        let p = &standing.all[k];
        tests.add("pt_test@sun_ok", 1 + p.beds.len() as u64);
        if shades(house, p.yard, reach, side)
            || p.beds.iter().any(|&g| shades(house, g, reach, side))
        {
            return false;
        }
    }
    let plots: Vec<Rect> = std::iter::once(b.boxes[1])
        .chain(b.boxes[2..2 + b.gardens.len()].iter().copied())
        .collect();
    plots.iter().all(|&plot| {
        let south = plot.1 + plot.3 / 2.0;
        let near = standing.meeting(
            (plot.0 - plot.2 / 2.0 - side, south),
            (plot.0 + plot.2 / 2.0 + side, south + reach),
            tests,
        );
        near.iter().all(|&k| {
            tests.add("pt_test@sun_ok", 1);
            !shades(standing.all[k].house_box, plot, reach, side)
        })
    })
}

/// A rectangle's four corners, turned by `rot` degrees about its center.
#[must_use]
pub fn corners(r: Rect, rot: f64) -> [Pt; 4] {
    let th = rot.to_radians();
    let (c, s) = (th.cos(), th.sin());
    let (hw, hh) = (r.2 / 2.0, r.3 / 2.0);
    [(-hw, -hh), (hw, -hh), (hw, hh), (-hw, hh)]
        .map(|(x, y)| (r.0 + x * c - y * s, r.1 + x * s + y * c))
}

/// The gap between two convex quads wall to wall: 0 where they overlap (separating axes), else the least distance between
/// their edges.
#[must_use]
pub fn quad_gap(a: &[Pt; 4], b: &[Pt; 4]) -> f64 {
    let separated = |p: &[Pt; 4], q: &[Pt; 4]| {
        (0..4).any(|i| {
            let (x1, y1) = p[i];
            let (x2, y2) = p[(i + 1) % 4];
            let (nx, ny) = (-(y2 - y1), x2 - x1);
            let pa = p.iter().map(|v| nx * v.0 + ny * v.1);
            let qa = q.iter().map(|v| nx * v.0 + ny * v.1);
            let (pmin, pmax) = pa.fold((f64::MAX, f64::MIN), |(lo, hi), v| (lo.min(v), hi.max(v)));
            let (qmin, qmax) = qa.fold((f64::MAX, f64::MIN), |(lo, hi), v| (lo.min(v), hi.max(v)));
            pmax < qmin || qmax < pmin
        })
    };
    if !separated(a, b) && !separated(b, a) {
        return 0.0;
    }
    let seg = |p: Pt, s0: Pt, s1: Pt| crate::field::geom::seg_dist(p, s0, s1);
    let mut best = f64::MAX;
    for i in 0..4 {
        for j in 0..4 {
            best = best
                .min(seg(a[i], b[j], b[(j + 1) % 4]))
                .min(seg(b[j], a[i], a[(i + 1) % 4]));
        }
    }
    best
}

/// Would this house (its rectangle and rake) stand nearer a standing house than the two roofs' drip lines and the path between?
#[must_use]
pub fn too_near(house: Rect, rot: f64, standing: &Standing, tests: &mut Counts) -> bool {
    let lim = EAVE_FT.0 + EAVE_FT.1;
    let reach = lim + house.2.hypot(house.3) / 2.0;
    let mine = corners(house, rot);
    standing
        .meeting(
            (house.0 - reach, house.1 - reach),
            (house.0 + reach, house.1 + reach),
            tests,
        )
        .into_iter()
        .any(|k| {
            let (r, t) = standing.all[k].house;
            tests.add("seg_test@too_near", 16);
            quad_gap(&mine, &corners(r, t)) < lim
        })
}

/// Does the straight line from the house's center to any part's cross a stream, or a stream run through a part - a farmstead
/// keeps to one bank?
#[must_use]
pub fn across_a_stream(b: &Bundle, streams: &[(Pt, Pt)], tests: &mut Counts) -> bool {
    let h = (b.house.0, b.house.1);
    b.boxes[1..].iter().any(|r| {
        streams.iter().any(|&(s0, s1)| {
            tests.add("seg_test@across_a_stream", 2);
            crossing((h, (r.0, r.1)), (s0, s1)) || seg_in_box(s0, s1, *r)
        })
    })
}

/// Do two segments cross?
#[must_use]
pub fn crossing(a: (Pt, Pt), b: (Pt, Pt)) -> bool {
    let cross = |o: Pt, p: Pt, q: Pt| (p.0 - o.0) * (q.1 - o.1) - (p.1 - o.1) * (q.0 - o.0);
    let (d1, d2) = (cross(b.0, b.1, a.0), cross(b.0, b.1, a.1));
    let (d3, d4) = (cross(a.0, a.1, b.0), cross(a.0, a.1, b.1));
    (d1 > 0.0) != (d2 > 0.0) && (d3 > 0.0) != (d4 > 0.0)
}

/// Does the segment from `a` to `b` meet the box `r` (its center, width, height)?
#[must_use]
pub fn seg_in_box(a: Pt, b: Pt, r: Rect) -> bool {
    let (x0, x1, y0, y1) = (
        r.0 - r.2 / 2.0,
        r.0 + r.2 / 2.0,
        r.1 - r.3 / 2.0,
        r.1 + r.3 / 2.0,
    );
    let inside = |p: Pt| p.0 >= x0 && p.0 <= x1 && p.1 >= y0 && p.1 <= y1;
    if inside(a) || inside(b) {
        return true;
    }
    let c = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)];
    (0..4).any(|i| crossing((a, b), (c[i], c[(i + 1) % 4])))
}

/// Does every part of `b` stand on free ground - none of its nine points on a taken cell (the field, the water, the no-build
/// ground)? A point outside the window is asked of `beyond`.
#[must_use]
pub fn on_free_ground(
    b: &Bundle,
    ground: &Ground,
    beyond: &dyn Fn(Pt) -> bool,
    tests: &mut Counts,
) -> bool {
    b.boxes.iter().all(|r| {
        !ground.rect_refused(
            (r.0 - r.2 / 2.0, r.1 - r.3 / 2.0),
            (r.0 + r.2 / 2.0, r.1 + r.3 / 2.0),
            beyond,
            tests,
        )
    })
}

/// Does the yard open onto ground a way can reach - its box, grown by a cell, touching the reach?
#[must_use]
pub fn opens(b: &Bundle, reach: &Reach, tests: &mut Counts) -> bool {
    let y = b.boxes[1];
    let g = CELL;
    reach.touches(
        (y.0 - y.2 / 2.0 - g, y.1 - y.3 / 2.0 - g),
        (y.0 + y.2 / 2.0 + g, y.1 + y.3 / 2.0 + g),
        tests,
    )
}
