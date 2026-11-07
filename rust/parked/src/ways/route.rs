//! The lane router and the clearance tests it asks (feature 444 T30): the ground a way may not stand on filed by grid cell once
//! and asked per point (`hamletgen/clearance.py` `FabricIndex`), a link walkable where a clear run along it is long enough
//! (`ways/clearance.py` `_clear_link`, `link_survives`, `_clear_touch`, `clear_runs`, `clip_to_clear`), and the route itself -
//! Dijkstra on a lattice, string-pulled, its jogs taken out (`ways/route.py` `_route`, `lattice_search`, `_unjog`,
//! `_ease_corner`). The lattice is the index and decides nothing: every shortcut is asked of the real geometry before it is
//! taken.
//!
//! Research:
//!     routing machinery - NONE
//!     a worn path takes the shortest way - research/questions/0081-village-lanes.drawing.html: least cost through the steadings, then pulled taut like a string
//!     clear of the fabric - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: the line 7 ft off by default (the page's fence to the middle of the lane), a tread's edge 5.5 ft
//!     clear of the crop - research/questions/0081-village-lanes.drawing.html: half the widest tread off the crop (`WEB_CROP_GAP`, carried by the crop polygons) at each cell's center, unpadded so a way can come up to the bund (padded half a cell as the walls are, cohort Audit-10's field way could not); every link the pull takes is tested at that gap, and a lattice step it keeps as it is is asked of the crop's outline (`crosses_the_crop`) - a route that would cut a crop corner is no route
//!     clear of the toe and marsh - GUESS: searched, the record silent (feature 417 T29 pass A1, 2026-10-25); 8 ft (`WEB_HARD_GAP`)
//!     lattice off the water - research/questions/0055-where-a-field-meets-its-ditch-the-bank-the-bund-and-the-inlet-mizuguchi.html, research/questions/0014-bunds-between-the-paddies-aze.drawing.html: a path runs on the channel's bank and the bund is a path - the router keeps its lattice 14 ft off the water lines, a departure the code keeps until feature 417 T32
//!     a brook crossing tolled - GUESS research/questions/0035-villages-beside-their-stream-one-bank-or-both.drawing.html: the search charges a crossing (`_CROSSING["cost"]`) and the pull refuses a shortcut that adds one (`_new_crossing`)
//!     its search steps and tolerances - GUESS: no source could speak to it, a value of ours (feature 417 T38 pass N4, 2026-10-25) - 0.75 (search-box pad as a share of span); 80 (least search-box pad); 90000 (lattice cell budget); 5 (brook sampling step); 3 (link sample pitch); 8 (sampling step along a run)
//!     its salts, guards and sentinels - NONE: they decide nothing about the place - 0.71 (half a cell's diagonal (geometry)); 16 (floor on the spatial-index cell); 20 (spatial-index cell floor); 256 (an entry filed as big past this many cells)
#![expect(
    clippy::many_single_char_names,
    clippy::cast_possible_truncation,
    clippy::cast_sign_loss,
    clippy::cast_precision_loss,
    reason = "the plane geometry's own names, and lattice indices of a few hundred"
)]

use super::Counts;
use std::cmp::Ordering;
use std::collections::{BinaryHeap, HashMap};

use super::track::{edge_dist, in_poly, poly_box, seg_dist, segments_cross, Box4};
use crate::field::fan::Pt;

/// A lane's middle off a garden fence (ft).
///
/// Research:
///     clear of the fabric - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: 7 ft from a garden fence to a lane's middle
pub const WEB_FABRIC_GAP: f64 = 7.0;

/// A lane off the toe band and the marsh (ft).
///
/// Research:
///     clear of the toe and marsh - GUESS: searched, the record silent (feature 417 T29 pass A1, 2026-10-25); 8 ft
pub const WEB_HARD_GAP: f64 = 8.0;

/// A lane off a water line (ft).
///
/// Research:
///     lane off a water line - research/questions/0055-where-a-field-meets-its-ditch-the-bank-the-bund-and-the-inlet-mizuguchi.html, research/questions/0014-bunds-between-the-paddies-aze.drawing.html: a path runs on the bank of every grade of field channel, and the bund is a path - the lane is held 14 ft off a water line, a departure the code keeps until feature 417 T32
pub const LINE_GAP: f64 = 14.0;

/// The router's standard lattice cell (ft), kept at 10 by measurement: a coarser lattice stranded houses this one did not.
///
/// Research:
///     its search steps and tolerances - GUESS: no source could speak to it, a value of ours (feature 284 B2, measured) - 10 (the lattice cell, under the 18 ft narrowest gap)
pub const ROUTE_CELL: f64 = 10.0;

/// The bends the jogs are taken out at: a hairpin's turn, a zigzag's two turns and the run they fall within (degrees, degrees,
/// ft).
///
/// Research:
///     hairpin - research/questions/0081-village-lanes.drawing.html: a turn past 140 degrees
///     zigzag turn - research/questions/0081-village-lanes.drawing.html: two turns past 50 degrees
///     zigzag run - research/questions/0081-village-lanes.drawing.html: within 40 ft of path
pub const BENDS: (f64, f64, f64) = (140.0, 50.0, 40.0);

/// How far a blocked corner is eased off its apex (ft), in so many steps.
///
/// Research:
///     how far a corner is eased - CONVENTION: a drawing smoothing of the map's - Smith (1899) has village streets turning suddenly, (feature 417 T29 pass E2, 2026-10-25); up to 24 ft off its apex
pub const EASE: (f64, u32) = (24.0, 6);

/// The shortest arm `clip_to_clear` keeps (ft).
///
/// Research:
///     shortest arm - GUESS: no source could speak to it, a value of ours (feature 417 T29 pass A1, 2026-10-25); under 70 ft is not drawn
pub const SHORTEST_ARM_FT: f64 = 70.0;

/// A polygon a way may not stand on, carrying its own margin where it has one (the crop at a lane's half-tread, the toe and the
/// marsh at the hard gap); one with a margin of its own is a crop the lattice's steps may not cross.
#[derive(Clone, Debug)]
pub struct Ground {
    /// Its ring.
    pub ring: Vec<Pt>,
    /// Its own margin, if one.
    pub gap: Option<f64>,
}

impl Ground {
    /// A polygon kept off at the group's margin.
    #[must_use]
    pub fn plain(ring: Vec<Pt>) -> Self {
        Self { ring, gap: None }
    }
}

/// The length of a polyline.
#[must_use]
pub fn length(p: &[Pt]) -> f64 {
    p.windows(2)
        .map(|w| (w[1].0 - w[0].0).hypot(w[1].1 - w[0].1))
        .sum()
}

/// The change of heading at `b` on the run a, b, c in degrees: 0 straight on, 180 doubled back.
#[must_use]
pub fn turn_deg(a: Pt, b: Pt, c: Pt) -> f64 {
    let (v1, v2) = ((b.0 - a.0, b.1 - a.1), (c.0 - b.0, c.1 - b.1));
    let (n1, n2) = (v1.0.hypot(v1.1), v2.0.hypot(v2.1));
    if n1 < 1e-6 || n2 < 1e-6 {
        return 0.0;
    }
    ((v1.0 * v2.0 + v1.1 * v2.1) / (n1 * n2))
        .clamp(-1.0, 1.0)
        .acos()
        .to_degrees()
}

enum Entry {
    Ring(Vec<Pt>),
    Line(Pt, Pt),
}

/// The ground a way may not stand on, each item grown by its margin, filed by grid cell once and asked per point.
pub struct Fouling {
    entries: Vec<(Entry, f64, Box4)>,
    big: Vec<usize>,
    grid: HashMap<(i64, i64), Vec<usize>>,
    cell: f64,
    origin: Pt,
}

fn floor_i(v: f64) -> i64 {
    v.floor() as i64
}

impl Fouling {
    /// The index over the obstacles at `margin` (or each's own), the tight polygons at `tight_margin` (or each's own) and the
    /// lines at `line_margin`.
    #[must_use]
    pub fn new(
        obstacles: &[Ground],
        margin: f64,
        tight: &[Vec<Pt>],
        tight_margin: f64,
        lines: &[(Pt, Pt)],
        line_margin: f64,
    ) -> Self {
        let mut entries: Vec<(Entry, f64, Box4)> = Vec::new();
        let rings = obstacles
            .iter()
            .map(|g| (&g.ring, g.gap.unwrap_or(margin)))
            .chain(tight.iter().map(|r| (r, tight_margin)));
        for (ring, m) in rings.filter(|(r, _)| !r.is_empty()) {
            let b = poly_box(ring);
            entries.push((
                Entry::Ring(ring.clone()),
                m,
                (b.0 - m, b.1 - m, b.2 + m, b.3 + m),
            ));
        }
        for &(a, b) in lines {
            let m = line_margin;
            entries.push((
                Entry::Line(a, b),
                m,
                (
                    a.0.min(b.0) - m,
                    a.1.min(b.1) - m,
                    a.0.max(b.0) + m,
                    a.1.max(b.1) + m,
                ),
            ));
        }
        let mut extents: Vec<f64> = entries
            .iter()
            .map(|e| (e.2 .2 - e.2 .0).max(e.2 .3 - e.2 .1))
            .collect();
        extents.sort_by(f64::total_cmp);
        let cell = extents.get(extents.len() / 2).map_or(1.0, |&mid| {
            (2.0 * margin.max(tight_margin).max(line_margin))
                .max(mid)
                .max(16.0)
        });
        let origin = entries.iter().fold((f64::INFINITY, f64::INFINITY), |o, e| {
            (o.0.min(e.2 .0), o.1.min(e.2 .1))
        });
        let mut grid: HashMap<(i64, i64), Vec<usize>> = HashMap::new();
        let mut big = Vec::new();
        for (k, e) in entries.iter().enumerate() {
            let (x0, x1) = (
                floor_i((e.2 .0 - origin.0) / cell),
                floor_i((e.2 .2 - origin.0) / cell),
            );
            let (y0, y1) = (
                floor_i((e.2 .1 - origin.1) / cell),
                floor_i((e.2 .3 - origin.1) / cell),
            );
            if (x1 - x0 + 1) * (y1 - y0 + 1) > 256 {
                big.push(k);
                continue;
            }
            for i in x0..=x1 {
                for j in y0..=y1 {
                    grid.entry((i, j)).or_default().push(k);
                }
            }
        }
        Self {
            entries,
            big,
            grid,
            cell,
            origin,
        }
    }

    /// Is `q` inside a polygon, within a polygon's margin of its edge, or within a line's margin?
    #[must_use]
    pub fn fouled(&self, q: Pt, tests: &mut Counts) -> bool {
        let at = (
            floor_i((q.0 - self.origin.0) / self.cell),
            floor_i((q.1 - self.origin.1) / self.cell),
        );
        let near = self.grid.get(&at).map_or(&[][..], Vec::as_slice);
        tests.add(
            "index_examined@fouled",
            1 + (self.big.len() + near.len()) as u64,
        );
        self.big.iter().chain(near).any(|&k| {
            let (e, m, b) = &self.entries[k];
            if q.0 < b.0 || q.0 > b.2 || q.1 < b.1 || q.1 > b.3 {
                return false;
            }
            match e {
                Entry::Line(a, c) => seg_dist(q, *a, *c) < *m,
                Entry::Ring(r) => in_poly(q, r) || edge_dist(q, r) < *m,
            }
        })
    }
}

/// Does a clear run of the link a-b, sampled every 3 ft and asked of `fouled`, reach `need` - decided as soon as it is known?
pub fn link_survives(a: Pt, b: Pt, idx: &Fouling, need: f64, tests: &mut Counts) -> bool {
    let (floor, eps) = (0.5, 1e-6);
    let n = (((b.0 - a.0).hypot(b.1 - a.1) / 3.0) as usize).max(1);
    let thr = need.max(floor);
    let mut run: Vec<Pt> = Vec::new();
    let mut done = 0.0;
    for k in 0..=n {
        let f = k as f64 / n as f64;
        let q = if k == 0 {
            a
        } else {
            (a.0 + (b.0 - a.0) * f, a.1 + (b.1 - a.1) * f)
        };
        if idx.fouled(q, tests) {
            if run.len() >= 2 && length(&run) >= floor && length(&run) >= need {
                return true;
            }
            if (q.0 - b.0).hypot(q.1 - b.1) + eps < thr {
                return false;
            }
            run.clear();
            done = 0.0;
            continue;
        }
        if let Some(l) = run.last() {
            done += (q.0 - l.0).hypot(q.1 - l.1);
        }
        run.push(q);
        if run.len() >= 2 && done > thr + eps {
            return true;
        }
    }
    run.len() >= 2 && length(&run) >= floor && length(&run) >= need
}

/// The ground a router or a link reads: the hard ground, the steadings it threads between, and the water lines.
#[derive(Clone, Copy)]
pub struct Grounds<'a> {
    /// The hard ground (the field, crop, toe band and wet ground).
    pub hard: &'a [Ground],
    /// The steadings.
    pub walls: &'a [Vec<Pt>],
    /// The water lines.
    pub water: &'a [(Pt, Pt)],
}

impl Grounds<'_> {
    /// The index a link at `gap` is asked of.
    #[must_use]
    pub fn link_index(&self, gap: f64) -> Fouling {
        Fouling::new(
            self.hard,
            WEB_HARD_GAP,
            self.walls,
            gap,
            self.water,
            LINE_GAP,
        )
    }

    /// Is the short link a-b that closes a junction walkable at `gap` off everything but the water?
    #[must_use]
    pub fn clear_touch(&self, a: Pt, b: Pt, gap: f64, tests: &mut Counts) -> bool {
        let span = (b.0 - a.0).hypot(b.1 - a.1);
        if span < 1.0 {
            return true;
        }
        let idx = Fouling::new(self.hard, gap, self.walls, gap, self.water, LINE_GAP);
        clear_runs(&[a, b], &idx, 3.0, 0.5, tests)
            .iter()
            .any(|r| length(r) >= span - 0.5)
    }
}

/// Is the link a-b walkable: a clear run along it within 3 ft of its length, asked of the link index?
#[must_use]
pub fn clear_link(a: Pt, b: Pt, idx: &Fouling, tests: &mut Counts) -> bool {
    let span = (b.0 - a.0).hypot(b.1 - a.1);
    span < 1.0 || link_survives(a, b, idx, span - 3.0, tests)
}

/// Every clear stretch of the polyline at least `floor` long, sampled every `step`.
#[must_use]
pub fn clear_runs(
    pts: &[Pt],
    idx: &Fouling,
    step: f64,
    floor: f64,
    tests: &mut Counts,
) -> Vec<Vec<Pt>> {
    let mut samples = vec![pts[0]];
    for w in pts.windows(2) {
        let (a, b) = (w[0], w[1]);
        let n = (((b.0 - a.0).hypot(b.1 - a.1) / step) as usize).max(1);
        samples.extend((1..=n).map(|k| {
            let f = k as f64 / n as f64;
            (a.0 + (b.0 - a.0) * f, a.1 + (b.1 - a.1) * f)
        }));
    }
    let mut runs = Vec::new();
    let mut run: Vec<Pt> = Vec::new();
    for q in samples {
        if idx.fouled(q, tests) {
            if run.len() >= 2 && length(&run) >= floor {
                runs.push(std::mem::take(&mut run));
            }
            run.clear();
            continue;
        }
        run.push(q);
    }
    if run.len() >= 2 && length(&run) >= floor {
        runs.push(run);
    }
    runs
}

/// The polyline shortened to stop before the first ground it may not cross (each obstacle at `margin`, each line at the line
/// gap), sampled every 8 ft; nothing where what is left is shorter than an arm.
#[must_use]
pub fn clip_to_clear(
    pts: &[Pt],
    obstacles: &[Vec<Pt>],
    margin: f64,
    lines: &[(Pt, Pt)],
    tests: &mut Counts,
) -> Vec<Pt> {
    if obstacles.is_empty() && lines.is_empty() {
        return pts.to_vec();
    }
    let ground: Vec<Ground> = obstacles.iter().cloned().map(Ground::plain).collect();
    let idx = Fouling::new(&ground, margin, &[], 0.0, lines, LINE_GAP);
    let mut out = vec![pts[0]];
    for w in pts.windows(2) {
        let (a, b) = (w[0], w[1]);
        let n = (((b.0 - a.0).hypot(b.1 - a.1) / 8.0) as usize).max(1);
        let mut last = a;
        for k in 1..=n {
            let f = k as f64 / n as f64;
            let q = (a.0 + (b.0 - a.0) * f, a.1 + (b.1 - a.1) * f);
            if idx.fouled(q, tests) {
                out.push(last);
                return if length(&out) >= SHORTEST_ARM_FT {
                    out
                } else {
                    Vec::new()
                };
            }
            last = q;
        }
        out.push(b);
    }
    out
}

/// The brook's band a route pays its toll to enter: the brook sampled every 5 ft, filed by cell, `radius` either side.
pub struct Crossing {
    grid: HashMap<(i64, i64), Vec<Pt>>,
    radius: f64,
    cell: f64,
    /// The toll for entering the band (ft of walk).
    pub cost: f64,
}

impl Crossing {
    /// The band about `brook`, `radius` either side, tolled `cost`.
    #[must_use]
    pub fn new(brook: &[Pt], radius: f64, cost: f64, tests: &mut Counts) -> Self {
        let cell = (radius + 1.0).max(20.0);
        let mut grid: HashMap<(i64, i64), Vec<Pt>> = HashMap::new();
        for w in brook.windows(2) {
            let (a, b) = (w[0], w[1]);
            let n = (((b.0 - a.0).hypot(b.1 - a.1) / 5.0) as usize).max(1);
            for i in 0..=n {
                let f = i as f64 / n as f64;
                let q = (a.0 + (b.0 - a.0) * f, a.1 + (b.1 - a.1) * f);
                grid.entry((floor_i(q.0 / cell), floor_i(q.1 / cell)))
                    .or_default()
                    .push(q);
                tests.add("write@new", 1);
            }
        }
        let cost = if grid.is_empty() { 0.0 } else { cost };
        Self {
            grid,
            radius,
            cell,
            cost,
        }
    }

    /// Is `p` within the brook's band?
    #[must_use]
    pub fn in_band(&self, p: Pt, tests: &mut Counts) -> bool {
        let (gx, gy) = (floor_i(p.0 / self.cell), floor_i(p.1 / self.cell));
        (-1..=1).any(|dx| {
            (-1..=1).any(|dy| {
                self.grid.get(&(gx + dx, gy + dy)).is_some_and(|v| {
                    tests.add("dist@in_band", v.len() as u64);
                    v.iter()
                        .any(|q| (p.0 - q.0).hypot(p.1 - q.1) <= self.radius)
                })
            })
        })
    }

    /// Would pulling `path[i..=j]` straight enter the band where the lattice route between them stayed out of it?
    #[must_use]
    pub fn new_crossing(&self, path: &[Pt], i: usize, j: usize, tests: &mut Counts) -> bool {
        if path[i..=j].iter().any(|&q| self.in_band(q, tests)) {
            return false;
        }
        let (a, b) = (path[i], path[j]);
        let n = (((b.0 - a.0).hypot(b.1 - a.1) / 5.0) as usize).max(1);
        (0..=n).any(|k| {
            let f = k as f64 / n as f64;
            self.in_band((a.0 + (b.0 - a.0) * f, a.1 + (b.1 - a.1) * f), tests)
        })
    }
}

#[derive(PartialEq)]
struct Queued(f64, i64, i64);

impl Eq for Queued {}

impl PartialOrd for Queued {
    fn partial_cmp(&self, o: &Self) -> Option<Ordering> {
        Some(self.cmp(o))
    }
}

impl Ord for Queued {
    // the least cost first, ties by the lower cell: a min-heap on (cost, ix, iy)
    fn cmp(&self, o: &Self) -> Ordering {
        o.0.total_cmp(&self.0)
            .then(o.1.cmp(&self.1))
            .then(o.2.cmp(&self.2))
    }
}

/// The lattice a route searches: its origin, cell and size.
struct Lattice {
    x0: f64,
    y0: f64,
    cell: f64,
    nx: i64,
    ny: i64,
}

impl Lattice {
    fn pt(&self, (i, j): (i64, i64)) -> Pt {
        (
            self.x0 + i as f64 * self.cell,
            self.y0 + j as f64 * self.cell,
        )
    }

    fn near(&self, p: Pt) -> (i64, i64) {
        (
            (((p.0 - self.x0) / self.cell).round() as i64).clamp(0, self.nx - 1),
            (((p.1 - self.y0) / self.cell).round() as i64).clamp(0, self.ny - 1),
        )
    }

    fn at(&self, (i, j): (i64, i64)) -> usize {
        (j * self.nx + i) as usize
    }
}

/// How the router is asked: its lattice cell, its gap off the steadings, and its search box's pad as a share of the span.
#[derive(Clone, Copy)]
pub struct Ask {
    /// The lattice cell (ft).
    pub cell: f64,
    /// The line's gap off the steadings (ft).
    pub gap: f64,
    /// The search box's pad as a share of the span.
    pub pad: f64,
}

impl Default for Ask {
    fn default() -> Self {
        Self {
            cell: ROUTE_CELL,
            gap: WEB_FABRIC_GAP,
            pad: 0.75,
        }
    }
}

/// The lattice's search: Dijkstra from `s` until `g` is settled, each cell's walkability asked once.
fn search(
    lat: &Lattice,
    s: (i64, i64),
    g: (i64, i64),
    free: &mut dyn FnMut((i64, i64), &mut Counts) -> bool,
    band: &mut dyn FnMut((i64, i64), &mut Counts) -> bool,
    toll: f64,
    tests: &mut Counts,
) -> Option<Vec<(i64, i64)>> {
    let n = (lat.nx * lat.ny) as usize;
    let (mut dist, mut prev) = (vec![f64::INFINITY; n], vec![usize::MAX; n]);
    dist[lat.at(s)] = 0.0;
    let mut heap = BinaryHeap::from([Queued(0.0, s.0, s.1)]);
    while let Some(Queued(d, ix, iy)) = heap.pop() {
        if (ix, iy) == g {
            break;
        }
        if d > dist[lat.at((ix, iy))] {
            continue;
        }
        for (dx, dy) in [
            (-1, -1),
            (-1, 0),
            (-1, 1),
            (0, -1),
            (0, 1),
            (1, -1),
            (1, 0),
            (1, 1),
        ] {
            tests.add("candidate@search", 1);
            let j = (ix + dx, iy + dy);
            if !((0..lat.nx).contains(&j.0) && (0..lat.ny).contains(&j.1)) {
                continue;
            }
            let diag = dx != 0 && dy != 0;
            if !(free(j, tests) && (!diag || (free((j.0, iy), tests) && free((ix, j.1), tests)))) {
                continue;
            }
            let extra = if toll > 0.0 && band(j, tests) && !band((ix, iy), tests) {
                toll
            } else {
                0.0
            };
            let step = if diag { std::f64::consts::SQRT_2 } else { 1.0 };
            let nd = d + step * lat.cell + extra;
            if nd < dist[lat.at(j)] {
                dist[lat.at(j)] = nd;
                prev[lat.at(j)] = lat.at((ix, iy));
                heap.push(Queued(nd, j.0, j.1));
            }
        }
    }
    if dist[lat.at(g)].is_infinite() {
        return None;
    }
    let mut chain = vec![g];
    let mut cur = lat.at(g);
    while cur != lat.at(s) {
        cur = prev[cur];
        let c = i64::try_from(cur).unwrap_or(0);
        chain.push((c % lat.nx, c / lat.nx));
    }
    chain.reverse();
    Some(chain)
}

/// Does the step a-b cross the outline of a crop polygon (one carrying its own gap)?
#[must_use]
pub fn crosses_the_crop(a: Pt, b: Pt, hard: &[Ground]) -> bool {
    hard.iter()
        .filter(|g| g.gap.is_some() && g.ring.len() >= 3)
        .any(|g| {
            let n = g.ring.len();
            (0..n).any(|k| segments_cross(a, b, g.ring[k], g.ring[(k + 1) % n]))
        })
}

/// A walkable route from `start` to `goal` threading the steadings: Dijkstra on a lattice over a box padded about the two,
/// then string-pulled over links the real geometry clears, then its jogs taken out; nothing where there is no way through, or
/// the box is past the lattice's budget.
#[must_use]
pub fn route(
    start: Pt,
    goal: Pt,
    grounds: &Grounds,
    crossing: Option<&Crossing>,
    ask: Ask,
    tests: &mut Counts,
) -> Vec<Pt> {
    let span = (goal.0 - start.0).hypot(goal.1 - start.1);
    if span < 1.0 {
        return vec![start, goal];
    }
    let (cell, gap) = (ask.cell, ask.gap);
    let pad = (span * ask.pad).max(80.0);
    let (x0, y0) = (start.0.min(goal.0) - pad, start.1.min(goal.1) - pad);
    let (x1, y1) = (start.0.max(goal.0) + pad, start.1.max(goal.1) + pad);
    let lat = Lattice {
        x0,
        y0,
        cell,
        nx: ((x1 - x0) / cell) as i64 + 1,
        ny: ((y1 - y0) / cell) as i64 + 1,
    };
    if lat.nx * lat.ny > 90_000 {
        return Vec::new();
    }
    let plan = Fouling::new(
        grounds.hard,
        WEB_HARD_GAP,
        grounds.walls,
        gap + cell * 0.71,
        grounds.water,
        LINE_GAP,
    );
    let (s, g) = (lat.near(start), lat.near(goal));
    let mut free_memo: HashMap<(i64, i64), bool> = HashMap::from([(s, true), (g, true)]);
    let mut free = |c: (i64, i64), t: &mut Counts| {
        *free_memo
            .entry(c)
            .or_insert_with(|| !plan.fouled(lat.pt(c), t))
    };
    let mut band_memo: HashMap<(i64, i64), bool> = HashMap::new();
    let mut band = |c: (i64, i64), t: &mut Counts| {
        *band_memo
            .entry(c)
            .or_insert_with(|| crossing.is_some_and(|x| x.in_band(lat.pt(c), t)))
    };
    let toll = crossing.map_or(0.0, |c| c.cost);
    let Some(chain) = search(&lat, s, g, &mut free, &mut band, toll, tests) else {
        return Vec::new();
    };
    let inner = chain.len().saturating_sub(1).max(1);
    let mut path: Vec<Pt> = vec![start];
    path.extend(chain[1..inner].iter().map(|&c| lat.pt(c)));
    path.push(goal);
    let links = grounds.link_index(gap);
    let mut out = vec![path[0]];
    let mut i = 0;
    while i < path.len() - 1 {
        let mut j = path.len() - 1;
        while j > i + 1
            && (!clear_link(path[i], path[j], &links, tests)
                || (toll > 0.0 && crossing.is_some_and(|c| c.new_crossing(&path, i, j, tests))))
        {
            j -= 1;
        }
        if j == i + 1 && crosses_the_crop(path[i], path[j], grounds.hard) {
            return Vec::new();
        }
        out.push(path[j]);
        i = j;
    }
    unjog(out, grounds, tests)
}

/// The lattice's jogs taken out of a routed path where the chord clears the fabric at a lane's gap: a hairpin chorded or eased, a
/// zigzag chorded, kneed or eased.
///
/// Research:
///     no hairpin - research/questions/0081-village-lanes.drawing.html: a turn of 140 degrees chorded or eased
///     no zigzag - research/questions/0081-village-lanes.drawing.html: two 50 degree turns within 40 ft chorded
///     chord clear of the fabric - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: the chord's line 7 ft (`WEB_FABRIC_GAP`) off a garden fence, the page's fence to the middle of the lane
#[must_use]
pub fn unjog(mut out: Vec<Pt>, grounds: &Grounds, tests: &mut Counts) -> Vec<Pt> {
    let (hairpin, zigzag, run) = BENDS;
    let gap = WEB_FABRIC_GAP;
    let mut k = 1;
    while k + 1 < out.len() {
        if turn_deg(out[k - 1], out[k], out[k + 1]) >= hairpin {
            if grounds.clear_touch(out[k - 1], out[k + 1], gap, tests) {
                out.remove(k);
                k = (k - 1).max(1);
                continue;
            }
            if let Some(e) = ease_corner(out[k - 1], out[k], out[k + 1], grounds, tests) {
                out[k] = e;
                k = (k - 1).max(1);
                continue;
            }
        }
        if k + 2 < out.len()
            && turn_deg(out[k - 1], out[k], out[k + 1]) >= zigzag
            && turn_deg(out[k], out[k + 1], out[k + 2]) >= zigzag
            && (out[k].0 - out[k + 1].0).hypot(out[k].1 - out[k + 1].1) <= run
        {
            if grounds.clear_touch(out[k - 1], out[k + 2], gap, tests) {
                out.drain(k..k + 2);
                k = (k - 1).max(1);
                continue;
            }
            let knee = (
                f64::midpoint(out[k].0, out[k + 1].0),
                f64::midpoint(out[k].1, out[k + 1].1),
            );
            if grounds.clear_touch(out[k - 1], knee, gap, tests)
                && grounds.clear_touch(knee, out[k + 2], gap, tests)
            {
                out.splice(k..k + 2, [knee]);
                k = (k - 1).max(1);
                continue;
            }
            if let Some(e) = ease_corner(out[k - 1], out[k], out[k + 2], grounds, tests) {
                out.splice(k..k + 2, [e]);
                k = (k - 1).max(1);
                continue;
            }
        }
        k += 1;
    }
    out
}

/// A hairpin or zigzag whose chord is blocked, walked round instead: the corner slid off its apex across the chord, both ways,
/// the nearest place whose legs clear and whose turn is no hairpin.
///
/// Research:
///     a path goes round what stands - research/questions/0081-village-lanes.drawing.html: no hairpin, the apex's side
#[must_use]
pub fn ease_corner(a: Pt, apex: Pt, b: Pt, grounds: &Grounds, tests: &mut Counts) -> Option<Pt> {
    let (m, (dx, dy)) = (
        (f64::midpoint(a.0, b.0), f64::midpoint(a.1, b.1)),
        (b.0 - a.0, b.1 - a.1),
    );
    let span = dx.hypot(dy);
    if span < 1.0 {
        return None;
    }
    let (px, py) = (-dy / span, dx / span);
    let side = if (apex.0 - m.0) * px + (apex.1 - m.1) * py >= 0.0 {
        1.0
    } else {
        -1.0
    };
    let (reach, steps) = EASE;
    for i in 1..=steps {
        let off = reach * f64::from(i) / f64::from(steps);
        for sign in [side, -side] {
            tests.add("candidate@ease_corner", 1);
            let c = (m.0 + px * off * sign, m.1 + py * off * sign);
            if turn_deg(a, c, b) >= BENDS.0 {
                continue;
            }
            if grounds.clear_touch(a, c, WEB_FABRIC_GAP, tests)
                && grounds.clear_touch(c, b, WEB_FABRIC_GAP, tests)
            {
                return Some(c);
            }
        }
    }
    None
}
