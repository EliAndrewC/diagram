//! The ways laid in the gaps (feature 444 T30): once the last house stands, lane ground as one raster over the cluster, one flood
//! from the way out, and each household - nearest the way out first - searched out of its own homestead from its dooryard's
//! doors, traced back along the flood to the way out or to a way already laid, its foot gathered onto a junction, pulled taut and
//! admitted; a household none of whose exits is admitted is reached across its nearest reached neighbor's yard
//! (`rolling/gap_ways.py`).
//!
//! Research:
//!     the ways laid in the gaps - GUESS research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: the lanes as the gaps left between the house plots, the record's own reading, no page stating it
//!     raster, flood and search plumbing - NONE: the cells, steps and marks the passes above are built from
//!     each household's way laid once every house stands - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: the homesteads built first and the lanes after; the corridor's own tests and the tree's lane law admit each
//!     households' ways laid in order, nearest the way out first - GUESS: a search order, so a nearer household's way is there for a farther one to join
//!     a household no way reaches is pinched across its nearest reached neighbor's yard - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: reached across a neighbor's land, whose own way is always drawn
//!     reached across a neighbor's yard in a pinch - CANON: the GM's ruling of 2026-10-03, "it's okay for people to cut through neighbors' yards in a pinch"
//!     lane ground - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html, research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.html: a way keeps the corridor's half-width off every homestead and to ground the site admits, and off the woodlots' seats
//!     a way keeps to the middle of its gap - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: along the middle of the gaps
//!     the shortest or easiest way - research/questions/0081-village-lanes.drawing.html: a worn path takes the shortest or easiest way
//!     a way leaves its own homestead from its dooryard - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: from the doors it is given, round its own house, beds and fixtures
//!     ways join at a T - research/questions/0081-village-lanes.drawing.html, research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: a lane meets another at a T, never beside it
//!     lane ends gathered - research/questions/0081-village-lanes.drawing.html: ends within 25 ft of one another are joined at a single point
#![expect(
    clippy::many_single_char_names,
    clippy::cast_possible_truncation,
    clippy::cast_possible_wrap,
    clippy::cast_sign_loss,
    clippy::cast_precision_loss,
    reason = "the plane geometry's own names, and raster indices of a few hundred"
)]

use std::cmp::Ordering;
use std::collections::{BinaryHeap, HashMap};

use super::access::{point_clear, taut, AccessTree, Parts, ACCESS_HALF_FT};
use super::ground::Ground;
use super::layout::Rect;
use super::standing::Standing;
use super::wood::Shares;
use super::Counts;
use crate::field::fan::Pt;
use crate::field::geom::dist;

/// The lane raster's cell (ft): the 6 ft band a way's line has between two homesteads parted by the threading gap always holds a
/// cell's center.
///
/// Research:
///     lane raster cell - NONE: a raster's resolution, measured (specs/318-grow-outward-no-restart/research.md R4)
pub const GAP_CELL: f64 = 5.0;

/// How far past the homesteads the raster runs, and the flood past the last household's ring (ft).
///
/// Research:
///     lane raster margin - NONE: the raster's extent - 160
///     flood extent - NONE: a search breadth - 400
pub const REACH: (f64, f64) = (160.0, 400.0);

/// How much dearer a step beside blocked ground is, over how many cells.
///
/// Research:
///     how hard it keeps the middle - GUESS: no source could speak to it, a value of ours (feature 417 T36 pass P3, 2026-10-25); `CENTER_WEIGHT` (3) over `CENTER_CELLS` (3) (405 T127)
pub const CENTER: (f64, usize) = (3.0, 3);

/// A homestead's ring, the exits tried, the breadth before a knotted foot is kept, and the taut pull's legs.
///
/// Research:
///     a homestead's ring - NONE: the search's extent about the homestead, in cells - 4
///     ways out tried - NONE: a search breadth, measured (research R4) - 6
///     ways out tried before a knotted foot is kept - research/questions/0081-village-lanes.drawing.html: ends within 25 ft are joined at a single point, so a knotted foot is the last resort; the breadth (three times `GAP_TRIES`) NONE: a search breadth, measured on Kuwabata - 3
///     at most twelve legs - NONE: a search breadth, the taut pull's cap - 12
pub const SEARCH: (usize, usize, usize, usize) = (4, 6, 3, 12);

/// The join reaches: near, then far, and the reach a foot is gathered onto a junction (ft).
///
/// Research:
///     ways join at a T - GUESS: searched, the record silent (feature 417 T36 pass P3, 2026-10-25); a 25 ft join radius, under the 30 ft shadow; the T itself is the drawing page's
///     a farther join - GUESS: searched, the record silent (feature 417 T36 pass P3, 2026-10-25); tried 45 ft off where the nearer join breaks the lane law
///     lane ends gathered - research/questions/0081-village-lanes.drawing.html: ends within 25 ft of one another are joined at a single point
pub const JOINS: (f64, f64, f64) = (25.0, 45.0, 25.0);

const STEPS: [(i64, i64, f64); 8] = [
    (-1, 0, 1.0),
    (1, 0, 1.0),
    (0, -1, 1.0),
    (0, 1, 1.0),
    (-1, -1, std::f64::consts::SQRT_2),
    (1, 1, std::f64::consts::SQRT_2),
    (-1, 1, std::f64::consts::SQRT_2),
    (1, -1, std::f64::consts::SQRT_2),
];

/// Lane ground over the cluster: how many homesteads hold each cell off, and the site's ground and the wood seats.
pub struct Layers {
    x0: f64,
    y0: f64,
    nx: usize,
    ny: usize,
    cover: Vec<i16>,
    site: Vec<bool>,
}

impl Layers {
    fn at(&self, c: (usize, usize)) -> Pt {
        (
            self.x0 + (c.0 as f64 + 0.5) * GAP_CELL,
            self.y0 + (c.1 as f64 + 0.5) * GAP_CELL,
        )
    }

    fn idx(&self, c: (usize, usize)) -> usize {
        c.0 * self.ny + c.1
    }

    fn cell_of(&self, p: Pt) -> Option<(usize, usize)> {
        let (i, j) = (
            ((p.0 - self.x0) / GAP_CELL).floor(),
            ((p.1 - self.y0) / GAP_CELL).floor(),
        );
        (i >= 0.0 && j >= 0.0 && (i as usize) < self.nx && (j as usize) < self.ny)
            .then_some((i as usize, j as usize))
    }

    /// The cells whose centers lie in the box, as (i0, i1, j0, j1), the ends exclusive.
    fn span(&self, x0: f64, y0: f64, x1: f64, y1: f64) -> (usize, usize, usize, usize) {
        let first = |v: f64, org: f64, n: usize| {
            (((v - org) / GAP_CELL - 0.5).ceil().max(0.0) as usize).min(n)
        };
        (
            first(x0, self.x0, self.nx),
            first(x1, self.x0, self.nx),
            first(y0, self.y0, self.ny),
            first(y1, self.y0, self.ny),
        )
    }

    fn blocked(&self, k: usize) -> bool {
        self.site[k] || self.cover[k] > 0
    }
}

/// What the gaps' ways read beside the households: the site's ground, the wood seats, the canvas, the corridor's half-width and the
/// lane's gap off a seat.
pub struct GapSite<'a> {
    /// The free ground's raster.
    pub ground: &'a Ground,
    /// The site beyond the raster's window (true: taken).
    pub beyond: &'a dyn Fn(Pt) -> bool,
    /// The wood seats reserved.
    pub wood: &'a Shares,
    /// The canvas (ft).
    pub canvas: Pt,
    /// The lane's gap off a reserved seat.
    pub lane_gap: f64,
    /// What else the seating placed that holds lane ground off: the persimmons, bamboo strips, retirement houses and pockets.
    pub extra: &'a [Rect],
}

/// A household as its way reads it: its parts, its homestead's box, and its house's center.
pub struct Household {
    /// Its homestead's parts.
    pub parts: Parts,
    /// The box round its homestead.
    pub bbox: Rect,
    /// Its house's center.
    pub at: Pt,
}

/// The lane law's verdicts a household's way is asked: each leg on lawful ground, and the whole tree lawful with the way drawn;
/// and the drawn way reserved.
pub trait Judge {
    /// Would the web's way along the leg stand on lawful ground?
    fn lawful_leg(&mut self, a: Pt, b: Pt, tests: &mut Counts) -> bool;
    /// Would the tree, the drawn way of household `k` added, keep the lane law?
    fn tree_admits(&mut self, drawn: &[Pt], k: usize, tests: &mut Counts) -> bool;
    /// The drawn way of household `k` reserved.
    fn reserve(&mut self, drawn: &[Pt], k: usize);
}

/// Lane ground over the homesteads' boxes and the way out, the raster's margin round them, clipped to the canvas.
#[must_use]
pub fn lane_layers(
    site: &GapSite,
    boxes: &[Rect],
    segs: &[(Pt, Pt)],
    tests: &mut Counts,
) -> Layers {
    let half = ACCESS_HALF_FT;
    let pts = segs.iter().flat_map(|&(a, b)| [a, b]);
    let lo = boxes
        .iter()
        .map(|b| (b.0 - b.2 / 2.0, b.1 - b.3 / 2.0))
        .chain(pts.clone())
        .fold((f64::INFINITY, f64::INFINITY), |m, p| {
            (m.0.min(p.0), m.1.min(p.1))
        });
    let hi = boxes
        .iter()
        .map(|b| (b.0 + b.2 / 2.0, b.1 + b.3 / 2.0))
        .chain(pts)
        .fold((f64::NEG_INFINITY, f64::NEG_INFINITY), |m, p| {
            (m.0.max(p.0), m.1.max(p.1))
        });
    let (x0, y0) = ((lo.0 - REACH.0).max(0.0), (lo.1 - REACH.0).max(0.0));
    let (x1, y1) = (
        (hi.0 + REACH.0).min(site.canvas.0),
        (hi.1 + REACH.0).min(site.canvas.1),
    );
    let (nx, ny) = (
        ((x1 - x0) / GAP_CELL) as usize + 1,
        ((y1 - y0) / GAP_CELL) as usize + 1,
    );
    let mut l = Layers {
        x0,
        y0,
        nx,
        ny,
        cover: vec![0; nx * ny],
        site: vec![false; nx * ny],
    };
    for b in boxes {
        let (i0, i1, j0, j1) = l.span(
            b.0 - b.2 / 2.0 - half,
            b.1 - b.3 / 2.0 - half,
            b.0 + b.2 / 2.0 + half,
            b.1 + b.3 / 2.0 + half,
        );
        for i in i0..i1 {
            for j in j0..j1 {
                l.cover[i * ny + j] += 1;
            }
        }
    }
    let g = site.lane_gap;
    for &(sx, sy) in site.wood.all_seats() {
        let (i0, i1, j0, j1) = l.span(sx - g, sy - g, sx + g, sy + g);
        for i in i0..i1 {
            for j in j0..j1 {
                let p = l.at((i, j));
                if (p.0 - sx).powi(2) + (p.1 - sy).powi(2) < g * g {
                    l.site[i * ny + j] = true;
                }
            }
        }
    }
    tests.add("write@lane_layers", (nx * ny) as u64);
    for i in 0..nx {
        for j in 0..ny {
            let p = l.at((i, j));
            if site.ground.taken_at(p).unwrap_or_else(|| (site.beyond)(p)) {
                l.site[i * ny + j] = true;
            }
        }
    }
    l
}

#[derive(PartialEq)]
struct Q(f64, usize, usize);

impl Eq for Q {}

impl PartialOrd for Q {
    fn partial_cmp(&self, o: &Self) -> Option<Ordering> {
        Some(self.cmp(o))
    }
}

impl Ord for Q {
    fn cmp(&self, o: &Self) -> Ordering {
        o.0.total_cmp(&self.0)
            .then(o.1.cmp(&self.1))
            .then(o.2.cmp(&self.2))
    }
}

/// The flood: the cheapest walk from the way out to every cell of lane ground and each cell's step back, 8-way with no diagonal
/// cutting a blocked corner, each step dearer beside blocked ground; stopped past the first time every ring is reached.
pub struct Flood {
    /// Each cell's cost from the way out (infinite where it never reached).
    pub dist: Vec<f64>,
    /// Each cell's step back toward the way out.
    pub pred: Vec<Option<(usize, usize)>>,
}

/// The flood from `segs` over the layers, `rings` each homestead's cell span.
#[must_use]
pub fn flood(
    l: &Layers,
    segs: &[(Pt, Pt)],
    rings: &[(usize, usize, usize, usize)],
    tests: &mut Counts,
) -> Flood {
    let (nx, ny) = (l.nx, l.ny);
    let (weight, r) = CENTER;
    // the share of blocked cells in each cell's square of side 2r + 1, by a summed-area table
    let mut sat = vec![0i64; (nx + 1) * (ny + 1)];
    for i in 0..nx {
        for j in 0..ny {
            sat[(i + 1) * (ny + 1) + j + 1] = i64::from(l.blocked(l.idx((i, j))))
                + sat[i * (ny + 1) + j + 1]
                + sat[(i + 1) * (ny + 1) + j]
                - sat[i * (ny + 1) + j];
        }
    }
    let area = |i0: usize, i1: usize, j0: usize, j1: usize| {
        sat[i1 * (ny + 1) + j1] - sat[i0 * (ny + 1) + j1] - sat[i1 * (ny + 1) + j0]
            + sat[i0 * (ny + 1) + j0]
    };
    let w = (2 * r + 1) as f64;
    let wt: Vec<f64> = (0..nx * ny)
        .map(|k| {
            let (i, j) = (k / ny, k % ny);
            let n = area(
                i.saturating_sub(r),
                (i + r + 1).min(nx),
                j.saturating_sub(r),
                (j + r + 1).min(ny),
            );
            1.0 + weight * n as f64 / (w * w)
        })
        .collect();
    let mut dist_v = vec![f64::INFINITY; nx * ny];
    let mut pred = vec![None; nx * ny];
    let mut heap = BinaryHeap::new();
    let mut seen = std::collections::HashSet::new();
    let sources: Vec<(usize, usize)> = segs
        .iter()
        .flat_map(|&(a, b)| {
            let n = (dist(a, b) / GAP_CELL) as usize + 1;
            (0..=n).map(move |t| {
                let f = t as f64 / n as f64;
                (a.0 + (b.0 - a.0) * f, a.1 + (b.1 - a.1) * f)
            })
        })
        .filter_map(|p| l.cell_of(p))
        .filter(|&c| seen.insert(c))
        .collect();
    for c in sources {
        dist_v[l.idx(c)] = 0.0;
        heap.push(Q(0.0, c.0, c.1));
    }
    let mut owner: HashMap<(usize, usize), Vec<usize>> = HashMap::new();
    for (k, &(i0, i1, j0, j1)) in rings.iter().enumerate() {
        for i in i0..i1 {
            for j in j0..j1 {
                owner.entry((i, j)).or_default().push(k);
            }
        }
    }
    let mut need = vec![true; rings.len()];
    let mut left = rings.len();
    let mut stop = f64::INFINITY;
    while let Some(Q(d, i, j)) = heap.pop().filter(|q| q.0 <= stop) {
        if left > 0 {
            for &k in owner.get(&(i, j)).map_or(&[][..], Vec::as_slice) {
                if need[k] {
                    need[k] = false;
                    left -= 1;
                    if left == 0 {
                        stop = d + REACH.1;
                    }
                }
            }
        }
        if d > dist_v[l.idx((i, j))] {
            continue;
        }
        for &(di, dj, ln) in &STEPS {
            tests.add("candidate@flood", 1);
            let (u, v) = (i as i64 + di, j as i64 + dj);
            if u < 0 || v < 0 || u >= nx as i64 || v >= ny as i64 {
                continue;
            }
            let (u, v) = (u as usize, v as usize);
            let corner =
                di != 0 && dj != 0 && (l.blocked(l.idx((u, j))) || l.blocked(l.idx((i, v))));
            if l.blocked(l.idx((u, v))) || corner {
                continue;
            }
            let nd = d + ln * GAP_CELL * wt[l.idx((u, v))];
            if nd < dist_v[l.idx((u, v))] {
                dist_v[l.idx((u, v))] = nd;
                pred[l.idx((u, v))] = Some((i, j));
                heap.push(Q(nd, u, v));
            }
        }
    }
    Flood { dist: dist_v, pred }
}

/// The nearest point to `p` on the segments, the first of equals kept; None where there are none.
#[must_use]
pub fn nearest_foot(p: Pt, segs: &[(Pt, Pt)]) -> Option<Pt> {
    segs.iter()
        .map(|&(a, b)| {
            let (dx, dy) = (b.0 - a.0, b.1 - a.1);
            let dd = dx * dx + dy * dy;
            let t = if dd == 0.0 {
                0.0
            } else {
                (((p.0 - a.0) * dx + (p.1 - a.1) * dy) / dd).clamp(0.0, 1.0)
            };
            (a.0 + t * dx, a.1 + t * dy)
        })
        .fold(None, |best: Option<Pt>, c| match best {
            Some(b) if dist(b, p) <= dist(c, p) => Some(b),
            _ => Some(c),
        })
}

/// The tree's junctions and free ends: every segment end but a bend, where one way's leg runs on into its next and nothing else
/// stands.
#[must_use]
pub fn junction_points(segs: &[(Pt, Pt)]) -> Vec<Pt> {
    let key = |q: Pt| ((q.0 * 10.0).round() as i64, (q.1 * 10.0).round() as i64);
    let mut seen: Vec<((i64, i64), usize, Pt)> = Vec::new();
    for &(a, b) in segs {
        for q in [a, b] {
            match seen.iter_mut().find(|e| e.0 == key(q)) {
                Some(e) => e.1 += 1,
                None => seen.push((key(q), 1, q)),
            }
        }
    }
    let bends: Vec<(i64, i64)> = segs
        .windows(2)
        .filter(|w| key(w[0].1) == key(w[1].0))
        .map(|w| key(w[0].1))
        .collect();
    seen.into_iter()
        .filter(|e| e.1 != 2 || !bends.contains(&e.0))
        .map(|e| e.2)
        .collect()
}

/// The junction a way's foot is moved onto: the nearest within `reach` of it and not on it, or None.
#[must_use]
pub fn gathered_foot(foot: Pt, junctions: &[Pt], reach: f64) -> Option<Pt> {
    junctions
        .iter()
        .copied()
        .filter(|&j| {
            let d = dist(j, foot);
            1e-6 < d && d <= reach
        })
        .min_by(|a, b| dist(*a, foot).total_cmp(&dist(*b, foot)))
}

fn ended_at(pts: &[Pt], foot: Pt) -> Vec<Pt> {
    let mut out = pts.to_vec();
    if out.last().is_none_or(|&l| dist(foot, l) > 1e-6) {
        out.push(foot);
    }
    out
}

fn mark_laid(l: &Layers, laid: &mut [bool], run: &[Pt], r: usize) {
    for w in run.windows(2) {
        let (a, b) = (w[0], w[1]);
        let n = (dist(a, b) / GAP_CELL) as usize + 1;
        for t in 0..=n {
            let f = t as f64 / n as f64;
            let i = ((a.0 + (b.0 - a.0) * f - l.x0) / GAP_CELL).floor() as i64;
            let j = ((a.1 + (b.1 - a.1) * f - l.y0) / GAP_CELL).floor() as i64;
            let r = r as i64;
            for u in (i - r).max(0)..(i + r + 1).max(0).min(l.nx as i64) {
                for v in (j - r).max(0)..(j + r + 1).max(0).min(l.ny as i64) {
                    laid[u as usize * l.ny + v as usize] = true;
                }
            }
        }
    }
}

/// Where each household's way lands: drawn, or reached across its nearest reached neighbor's yard, or neither.
#[derive(Debug, Default, PartialEq)]
pub struct Ways {
    /// Each household's drawn way, where admitted.
    pub drawn: Vec<Option<Vec<Pt>>>,
    /// Each household pinched across a neighbor's yard: the neighbor.
    pub pinched: Vec<Option<usize>>,
}

/// What one household's search reads.
struct Search<'s, 'a> {
    l: &'s Layers,
    fl: &'s Flood,
    st: &'s mut Standing<'a>,
    tree: &'s AccessTree,
    lays: &'s [Vec<bool>; 3],
}

/// Lay every household's way in the gaps, nearest the way out first; the tree's segments are the way out to begin with, and each
/// admitted way is reserved in it.
pub fn lay_the_ways(
    site: &GapSite,
    households: &[Household],
    tree: &mut AccessTree,
    judge: &mut dyn Judge,
    tests: &mut Counts,
) -> Ways {
    let mut out = Ways {
        drawn: vec![None; households.len()],
        pinched: vec![None; households.len()],
    };
    if households.is_empty() || tree.segs.is_empty() {
        return out;
    }
    // the households' own boxes first, so a household's index is its box's; what else was placed after them
    let boxes: Vec<Rect> = households
        .iter()
        .map(|h| h.bbox)
        .chain(site.extra.iter().copied())
        .collect();
    let segs = tree.segs.clone();
    let l = lane_layers(site, &boxes, &segs, tests);
    let ring = ACCESS_HALF_FT + SEARCH.0 as f64 * GAP_CELL;
    let rings: Vec<_> = boxes[..households.len()]
        .iter()
        .map(|b| {
            l.span(
                b.0 - b.2 / 2.0 - ring,
                b.1 - b.3 / 2.0 - ring,
                b.0 + b.2 / 2.0 + ring,
                b.1 + b.3 / 2.0 + ring,
            )
        })
        .collect();
    let fl = flood(&l, &segs, &rings, tests);
    let nearest: Vec<f64> = rings
        .iter()
        .map(|&(i0, i1, j0, j1)| {
            (i0..i1)
                .flat_map(|i| (j0..j1).map(move |j| (i, j)))
                .map(|c| fl.dist[l.idx(c)])
                .fold(f64::INFINITY, f64::min)
        })
        .collect();
    let mut order: Vec<usize> = (0..households.len()).collect();
    order.sort_by(|&a, &b| nearest[a].total_cmp(&nearest[b]));
    let mut lays = [
        vec![false; l.nx * l.ny],
        vec![false; l.nx * l.ny],
        vec![false; l.nx * l.ny],
    ];
    let radii = [(JOINS.0 / GAP_CELL) as usize, (JOINS.1 / GAP_CELL) as usize];
    let mut st = Standing::new(
        site.ground,
        site.beyond,
        site.wood,
        &boxes,
        (ACCESS_HALF_FT, site.lane_gap),
    );
    for k in order {
        let mut s = Search {
            l: &l,
            fl: &fl,
            st: &mut st,
            tree,
            lays: &lays,
        };
        let Some(got) = way_for(&mut s, households, k, rings[k], judge, tests) else {
            continue;
        };
        for w in got.windows(2) {
            tree.add(w[0], w[1]);
        }
        judge.reserve(&got, k);
        for (laid, &r) in lays.iter_mut().zip(&radii) {
            mark_laid(&l, laid, &got, r);
        }
        out.drawn[k] = Some(got);
    }
    // the lane law's predicates counted in the thread's tally, drained into the stage's
    crate::counts::drain_into(tests);
    for k in 0..households.len() {
        if out.drawn[k].is_none() {
            let h = households[k].at;
            out.pinched[k] = (0..households.len())
                .filter(|&o| out.drawn[o].is_some())
                .min_by(|&a, &b| dist(households[a].at, h).total_cmp(&dist(households[b].at, h)));
        }
    }
    out
}

/// A household's search out of its homestead: from its doors over the cells of its ring its own test admits to the flood's
/// cells; its exits (walk and flood, cell), cheapest first, and each cell's step back (a door's cell to the door itself).
type Back = HashMap<(usize, usize), Result<(usize, usize), Pt>>;

fn way_out(
    s: &Search,
    doors: &[Pt],
    area: (usize, usize, usize, usize),
    open_here: &dyn Fn((usize, usize)) -> bool,
    tests: &mut Counts,
) -> (Vec<(f64, usize, usize)>, Back) {
    let (i0, i1, j0, j1) = area;
    let mut seen: HashMap<(usize, usize), bool> = HashMap::new();
    let mut ok = |c: (usize, usize), tests: &mut Counts| {
        *seen.entry(c).or_insert_with(|| {
            tests.add("candidate@way_out", 1);
            s.fl.dist[s.l.idx(c)].is_finite() || open_here(c)
        })
    };
    let mut best: HashMap<(usize, usize), f64> = HashMap::new();
    let mut back: Back = HashMap::new();
    let mut heap = BinaryHeap::new();
    let mut cells = std::collections::HashSet::new();
    let starts: Vec<((usize, usize), Pt)> = doors
        .iter()
        .filter_map(|&d| s.l.cell_of(d).map(|c| (c, d)))
        .filter(|(c, _)| cells.insert(*c))
        .collect();
    for (c, door) in starts {
        best.insert(c, 0.0);
        back.insert(c, Err(door));
        heap.push(Q(0.0, c.0, c.1));
    }
    let mut exits = Vec::new();
    while let Some(Q(d, i, j)) = heap.pop() {
        if s.fl.dist[s.l.idx((i, j))].is_finite() {
            exits.push((d + s.fl.dist[s.l.idx((i, j))], i, j));
            continue;
        }
        for &(di, dj, ln) in &STEPS {
            let (u, v) = (i as i64 + di, j as i64 + dj);
            let inside = |u: i64, v: i64| {
                u >= i0 as i64
                    && u < i1 as i64
                    && v >= j0 as i64
                    && v < j1 as i64
                    && u >= 0
                    && v >= 0
                    && (u as usize) < s.l.nx
                    && (v as usize) < s.l.ny
            };
            if !inside(u, v) || !ok((u as usize, v as usize), tests) {
                continue;
            }
            let (u, v) = (u as usize, v as usize);
            if di != 0 && dj != 0 && !(ok((u, j), tests) && ok((i, v), tests)) {
                continue;
            }
            let nd = d + ln * GAP_CELL;
            if nd < best.get(&(u, v)).copied().unwrap_or(f64::INFINITY) {
                best.insert((u, v), nd);
                back.insert((u, v), Ok((i, j)));
                heap.push(Q(nd, u, v));
            }
        }
    }
    exits.sort_by(|a, b| a.0.total_cmp(&b.0).then(a.1.cmp(&b.1)).then(a.2.cmp(&b.2)));
    (exits, back)
}

/// The way on from the exit cell: back along the flood to the way out, or to where it first comes within the join's mark of a
/// way already laid and the leg onto it is clear; the cells' points after the exit and the point on the tree it joins.
fn trace(
    s: &mut Search,
    laid: &[bool],
    start: (usize, usize),
    own: usize,
    tests: &mut Counts,
) -> (Vec<Pt>, Pt) {
    let mut path = Vec::new();
    let mut c = start;
    loop {
        let here = s.l.at(c);
        let k = s.l.idx(c);
        // a cell with a finite cost steps back toward the way out, so the walk ends at the way out at the latest
        let met = (laid[k] || s.fl.dist[k] == 0.0).then(|| {
            tests.add("candidate@trace", 1);
            nearest_foot(here, &s.tree.segs).unwrap_or(here)
        });
        let source = s.fl.dist[k] == 0.0;
        if let Some(foot) = met.filter(|&f| source || s.st.clear(here, f, Some(own), tests)) {
            return (path, foot);
        }
        c = s.fl.pred[k].unwrap_or(c);
        path.push(s.l.at(c));
    }
}

/// The household's admitted way: up to the tries' distinct exits from its homestead, each traced joined near, joined far and run
/// on to the way out, pulled taut and admitted; its foot as traced only where no gathered join is admitted.
fn way_for(
    s: &mut Search,
    households: &[Household],
    k: usize,
    area: (usize, usize, usize, usize),
    judge: &mut dyn Judge,
    tests: &mut Counts,
) -> Option<Vec<Pt>> {
    let h = &households[k];
    let p = &h.parts;
    let (ring, tries, knotted_tries, _) = SEARCH;
    let mut gaps = vec![(p.house, super::access::house_gap())];
    gaps.extend(p.part_gaps());
    gaps.extend(p.fixture_gaps());
    let own_span = s.l.span(
        h.bbox.0 - h.bbox.2 / 2.0 - ACCESS_HALF_FT,
        h.bbox.1 - h.bbox.3 / 2.0 - ACCESS_HALF_FT,
        h.bbox.0 + h.bbox.2 / 2.0 + ACCESS_HALF_FT,
        h.bbox.1 + h.bbox.3 / 2.0 + ACCESS_HALF_FT,
    );
    let l = s.l;
    let open_here = |c: (usize, usize)| {
        let kk = l.idx(c);
        let mine = own_span.0 <= c.0 && c.0 < own_span.1 && own_span.2 <= c.1 && c.1 < own_span.3;
        !l.site[kk] && i32::from(l.cover[kk]) - i32::from(mine) <= 0 && point_clear(l.at(c), &gaps)
    };
    let doors: Vec<Pt> = p
        .doors(ACCESS_HALF_FT)
        .into_iter()
        .filter(|&d| p.fixtures_clear(d, d, tests) && p.parts_clear(d, d, tests))
        .collect();
    let (exits, back) = way_out(s, &doors, area, &open_here, tests);
    let junctions = junction_points(&s.tree.segs);
    let mut picked: Vec<(usize, usize)> = Vec::new();
    let mut knotted: Vec<Vec<Pt>> = Vec::new();
    for &(_, i, j) in &exits {
        tests.add("candidate@way_for", 1);
        let limit = tries * if knotted.is_empty() { 1 } else { knotted_tries };
        if picked.len() >= limit {
            break;
        }
        if picked
            .iter()
            .any(|&(a, b)| a.abs_diff(i) + b.abs_diff(j) < ring)
        {
            continue;
        }
        picked.push((i, j));
        let mut local = Vec::new();
        let mut c = (i, j);
        let door = loop {
            local.push(s.l.at(c));
            match back[&c] {
                Ok(prev) => c = prev,
                Err(door) => break door,
            }
        };
        let mut gathered = Vec::new();
        let lays = s.lays;
        for laid in lays {
            let (path, foot) = trace(s, laid, (i, j), k, tests);
            let mut pts = vec![door];
            pts.extend(local.iter().rev());
            pts.extend(path);
            let g = gathered_foot(foot, &junctions, JOINS.2);
            gathered.push(ended_at(&pts, g.unwrap_or(foot)));
            knotted.extend(g.is_some().then_some(ended_at(&pts, foot)));
        }
        if let Some(d) = first_admitted(s, &gathered, k, h, judge, tests) {
            return Some(d);
        }
    }
    first_admitted(s, &knotted, k, h, judge, tests)
}

/// The first of the runs, pulled taut, every leg of which clears the household's own parts and lawful ground, drawn from past its
/// yard and admitted by the tree; or None.
fn first_admitted(
    s: &mut Search,
    runs: &[Vec<Pt>],
    k: usize,
    h: &Household,
    judge: &mut dyn Judge,
    tests: &mut Counts,
) -> Option<Vec<Pt>> {
    let p = &h.parts;
    for q in runs {
        tests.add("candidate@first_admitted", 1);
        let st = &mut *s.st;
        let mut leg_ok = |a: Pt, b: Pt| {
            let mut t = Counts::default();
            let ok = p.house_clear(a, b, &mut t)
                && p.fixtures_clear(a, b, &mut t)
                && p.parts_clear(a, b, &mut t)
                && st.clear(a, b, Some(k), &mut t);
            for (key, n) in t.0 {
                tests.add(&key, n);
            }
            ok
        };
        let mut inner = Counts::default();
        let run = taut(q, &mut leg_ok, SEARCH.3, &mut inner);
        for (key, n) in inner.0 {
            tests.add(&key, n);
        }
        let drawn = run
            .filter(|run| {
                let last = run.len() - 2;
                run.windows(2).enumerate().all(|(n, w)| {
                    (n == last && dist(w[0], w[1]) < 1e-6)
                        || (p.fixtures_clear(w[0], w[1], tests)
                            && p.parts_clear(w[0], w[1], tests)
                            && judge.lawful_leg(w[0], w[1], tests))
                })
            })
            .map(|run| p.drawn_corridor(&run));
        if let Some(d) = drawn.filter(|d| judge.tree_admits(d, k, tests)) {
            return Some(d);
        }
    }
    None
}
