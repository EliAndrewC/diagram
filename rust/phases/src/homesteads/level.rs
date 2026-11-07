//! The hard ground's distance and its level sets (feature 444 T30, for the row village's streets, `rows.py`): the ground a row may
//! not stand on - the field, the site's other no-build rings, each water course at its clearance - as an exact distance (0 inside a
//! polygon, else to its nearest edge; a course's segment less its clearance), and the line at a given distance from it traced on a
//! grid by marching squares (`hard.buffer(d)`'s outline, which shapely draws with round joins). The grid is windowed to the hard
//! ground's box grown by the distance, its members filed by cell, so a sample reads only the edges near it.
//!
//! Research:
//!     the hard ground - research/questions/0033-row-villages-resson.drawing.html: a row's line runs off the field, the site's other no-build outline and each water course at its clearance, not the field alone
//!     the line traced on a grid - NONE: a level set on 4 ft cells, linearly interpolated, in place of shapely's buffer (a departure: within a foot of shapely's ring)

#![expect(
    clippy::cast_possible_truncation,
    clippy::cast_sign_loss,
    clippy::cast_precision_loss,
    clippy::cast_possible_wrap,
    clippy::many_single_char_names,
    reason = "grid indices and counts of a few thousand; the plane geometry's own names"
)]

use std::collections::HashMap;

use super::Counts;
use crate::field::fan::Pt;
use crate::field::geom::{dist, seg_dist};
use crate::seat::exit::seg_seg;
use crate::ways::track::in_poly;

/// The level set's cell and the members' filing cell (feet).
///
/// Research:
///     its salts, guards and sentinels - NONE: a sampling grain (4 ft) and a spatial-index cell (64 ft)
pub const CELLS: (f64, f64) = (4.0, 64.0);

/// The hard ground: its polygons, and every polygon edge and strip (a segment with its clearance) filed in a dense grid of cells by
/// the cells it reaches.
pub struct Hard {
    /// The polygons (the field and the other rings).
    pub polys: Vec<Vec<Pt>>,
    edges: Vec<(Pt, Pt, f64)>,
    /// Each filing cell's members, row by row over the cells they reach.
    cells: Vec<Vec<usize>>,
    /// The first filing cell, and how many a side.
    span: ((i64, i64), (usize, usize)),
}

fn cell(v: f64) -> i64 {
    (v / CELLS.1).floor() as i64
}

/// The filing cells a member reaches: its box grown by its clearance.
fn reach(&(a, b, c): &(Pt, Pt, f64)) -> (i64, i64, i64, i64) {
    (
        cell(a.0.min(b.0) - c),
        cell(a.1.min(b.1) - c),
        cell(a.0.max(b.0) + c),
        cell(a.1.max(b.1) + c),
    )
}

impl Hard {
    /// The hard ground of `polys` (rings of three points or more) and `strips` (a zero-length one passed, a clearance at least half a
    /// foot), filed.
    #[must_use]
    pub fn new(polys: &[Vec<Pt>], strips: &[(Pt, Pt, f64)], tests: &mut Counts) -> Self {
        let polys: Vec<Vec<Pt>> = polys.iter().filter(|p| p.len() >= 3).cloned().collect();
        let mut edges: Vec<(Pt, Pt, f64)> = polys
            .iter()
            .flat_map(|r| (0..r.len()).map(move |i| (r[i], r[(i + 1) % r.len()], 0.0)))
            .collect();
        edges.extend(
            strips
                .iter()
                .filter(|s| s.0 != s.1)
                .map(|&(a, b, c)| (a, b, c.max(0.5))),
        );
        let mut h = Self {
            polys,
            edges,
            cells: Vec::new(),
            span: ((0, 0), (0, 0)),
        };
        h.refile(tests);
        h
    }

    /// A bare polyline as hard ground: its segments, no clearance - the ground a parallel street is offset from.
    #[must_use]
    pub fn line(pts: &[Pt], tests: &mut Counts) -> Self {
        let mut h = Self::new(&[], &[], tests);
        h.edges = pts
            .windows(2)
            .filter(|w| w[0] != w[1])
            .map(|w| (w[0], w[1], 0.0))
            .collect();
        h.refile(tests);
        h
    }

    /// File every member in the dense grid of cells it reaches.
    fn refile(&mut self, tests: &mut Counts) {
        let (i0, j0, i1, j1) = self
            .edges
            .iter()
            .map(reach)
            .fold((i64::MAX, i64::MAX, i64::MIN, i64::MIN), |m, r| {
                (m.0.min(r.0), m.1.min(r.1), m.2.max(r.2), m.3.max(r.3))
            });
        let (w, h) = if self.edges.is_empty() {
            (0, 0)
        } else {
            ((i1 - i0 + 1) as usize, (j1 - j0 + 1) as usize)
        };
        let mut cells: Vec<Vec<usize>> = vec![Vec::new(); w * h];
        for (k, e) in self.edges.iter().enumerate() {
            let (a0, b0, a1, b1) = reach(e);
            for j in b0..=b1 {
                for i in a0..=a1 {
                    cells[(j - j0) as usize * w + (i - i0) as usize].push(k);
                }
            }
        }
        tests.add("write@Hard::refile", self.edges.len() as u64);
        self.cells = cells;
        self.span = ((i0, j0), (w, h));
    }

    /// Is there no hard ground?
    #[must_use]
    pub fn is_empty(&self) -> bool {
        self.edges.is_empty()
    }

    /// The box round the hard ground, its strips' clearance in it.
    #[must_use]
    pub fn bounds(&self) -> (f64, f64, f64, f64) {
        self.edges
            .iter()
            .fold((f64::MAX, f64::MAX, f64::MIN, f64::MIN), |m, &(a, b, c)| {
                (
                    m.0.min(a.0.min(b.0) - c),
                    m.1.min(a.1.min(b.1) - c),
                    m.2.max(a.0.max(b.0) + c),
                    m.3.max(a.1.max(b.1) + c),
                )
            })
    }

    /// Is `p` inside a polygon?
    #[must_use]
    pub fn inside(&self, p: Pt, tests: &mut Counts) -> bool {
        tests.add("pt_test@Hard::inside", self.polys.len() as u64);
        self.polys.iter().any(|r| in_poly(p, r))
    }

    /// The distance from `p` to the hard ground, read no farther than `cap` (beyond it, `cap`): 0 inside a polygon, else the least of
    /// its distance to a polygon's edge and to a strip's segment less the strip's clearance.
    #[must_use]
    pub fn dist(&self, p: Pt, cap: f64, tests: &mut Counts) -> f64 {
        if self.inside(p, tests) {
            return 0.0;
        }
        self.near(p, cap, tests)
    }

    /// `dist` for a point known to stand outside every polygon: the members filed in the cells about it, ring by ring of cells outward,
    /// stopped once a ring's nearest point lies past the best distance found or past `cap`; a member filed in two cells read twice,
    /// the least kept.
    fn near(&self, p: Pt, cap: f64, tests: &mut Counts) -> f64 {
        let ((i0, j0), (w, h)) = self.span;
        let (ci, cj) = (cell(p.0) - i0, cell(p.1) - j0);
        let mut best = cap;
        let (mut r, last) = (0, (cap / CELLS.1).ceil() as i64 + 1);
        // (every cell of ring r stands at least r - 1 cells from the point)
        while r <= last && (r - 1) as f64 * CELLS.1 <= best {
            for j in (cj - r).max(0)..=(cj + r).min(h as i64 - 1) {
                let rim = j == cj - r || j == cj + r;
                for i in ((ci - r).max(0)..=(ci + r).min(w as i64 - 1))
                    .filter(|&i| rim || i == ci - r || i == ci + r)
                {
                    let members = &self.cells[j as usize * w + i as usize];
                    tests.add("seg_test@Hard::near", members.len() as u64);
                    for &k in members {
                        let (a, b, c) = self.edges[k];
                        best = best.min((seg_dist(p, a, b) - c).max(0.0));
                    }
                }
            }
            r += 1;
        }
        best
    }

    /// Is `p` nearer than `d` to the hard ground? The cells within `d` of it read ring by ring, stopped at the first member nearer.
    #[must_use]
    pub fn nearer_than(&self, p: Pt, d: f64, tests: &mut Counts) -> bool {
        if self.inside(p, tests) {
            return true;
        }
        let ((i0, j0), (w, h)) = self.span;
        let (ci, cj) = (cell(p.0) - i0, cell(p.1) - j0);
        let last = (d / CELLS.1).ceil() as i64 + 1;
        // (the tests tallied here and counted once: a counter's lookup a member cost as much as the member's test)
        let mut asked = 0u64;
        let found = 'rings: {
            for r in 0..=last {
                for j in (cj - r).max(0)..=(cj + r).min(h as i64 - 1) {
                    let rim = j == cj - r || j == cj + r;
                    for i in ((ci - r).max(0)..=(ci + r).min(w as i64 - 1))
                        .filter(|&i| rim || i == ci - r || i == ci + r)
                    {
                        for &k in &self.cells[j as usize * w + i as usize] {
                            let (a, b, c) = self.edges[k];
                            asked += 1;
                            if seg_dist(p, a, b) - c < d {
                                break 'rings true;
                            }
                        }
                    }
                }
            }
            false
        };
        tests.add("seg_test@Hard::nearer_than", asked);
        found
    }

    /// Does the polygon `poly` meet the hard ground - touch or overlap a polygon, or come within a strip's clearance (shapely's
    /// `intersects` of the hard ground)? A vertex on the ground, a member's end inside the polygon, or an edge within a member's
    /// clearance of one of the polygon's, the members read from the cells the polygon's box reaches.
    #[must_use]
    pub fn meets(&self, poly: &[Pt], tests: &mut Counts) -> bool {
        if self.is_empty() || poly.len() < 3 {
            return false;
        }
        if poly.iter().any(|&p| self.dist(p, 1.0, tests) == 0.0) {
            return true;
        }
        let ((i0, j0), (w, h)) = self.span;
        let (x0, y0, x1, y1) = poly
            .iter()
            .fold((f64::MAX, f64::MAX, f64::MIN, f64::MIN), |m, p| {
                (m.0.min(p.0), m.1.min(p.1), m.2.max(p.0), m.3.max(p.1))
            });
        let mut ks: Vec<usize> = Vec::new();
        for j in (cell(y0) - j0).max(0)..=(cell(y1) - j0).min(h as i64 - 1) {
            for i in (cell(x0) - i0).max(0)..=(cell(x1) - i0).min(w as i64 - 1) {
                ks.extend(&self.cells[j as usize * w + i as usize]);
            }
        }
        ks.sort_unstable();
        ks.dedup();
        tests.add("seg_test@Hard::meets", (ks.len() * poly.len()) as u64);
        ks.into_iter().any(|k| {
            let (a, b, c) = self.edges[k];
            in_poly(a, poly)
                || (0..poly.len()).any(|m| seg_seg(poly[m], poly[(m + 1) % poly.len()], a, b) <= c)
        })
    }

    /// The exterior rings of the ground within `d` of the hard ground - each a closed ring, the first point not repeated - traced on a
    /// grid of `CELLS.0` over the hard ground's box grown by `d` and two cells.
    #[must_use]
    pub fn grown_rings(&self, d: f64, tests: &mut Counts) -> Vec<Vec<Pt>> {
        if self.is_empty() {
            return Vec::new();
        }
        let h = CELLS.0;
        let pad = d + 2.0 * h;
        let (x0, y0, x1, y1) = self.bounds();
        let (ox, oy) = (x0 - pad, y0 - pad);
        let (nx, ny) = (
            ((x1 - x0 + 2.0 * pad) / h).ceil() as usize + 1,
            ((y1 - y0 + 2.0 * pad) / h).ceil() as usize + 1,
        );
        let at = |i: usize, j: usize| (ox + i as f64 * h, oy + j as f64 * h);
        // each node's value, the distance less `d`, negative inside the grown ground; a polygon's inside filled by scanlines first
        let mut inside = vec![false; nx * ny];
        for r in &self.polys {
            fill(r, (ox, oy), h, (nx, ny), &mut inside, tests);
        }
        // ...EACH MEMBER SPREAD OVER THE NODES WITHIN ITS REACH, NOT EACH NODE ASKING THE CELLS ABOUT IT (the GM 2026-11-07, on a
        // test of 101 s: "498 seconds is still pretty crazy, right?!"): a node's value is the least distance to any member within
        // `cap`, else `cap` - the same values `near` gave, at the members' reach in nodes rather than every node times the members
        // its rings of 64 ft cells hold (a long field edge filed in every cell it crosses, read again by every node near it)
        let cap = d + 2.0 * h;
        let mut v = vec![cap; nx * ny];
        let node = |x: f64, o: f64, n: usize| (((x - o) / h).max(0.0) as usize).min(n - 1);
        for &(a, b, c) in &self.edges {
            let (i0, i1) = (
                node(a.0.min(b.0) - c - cap, ox, nx),
                node(a.0.max(b.0) + c + cap + h, ox, nx),
            );
            let (j0, j1) = (
                node(a.1.min(b.1) - c - cap, oy, ny),
                node(a.1.max(b.1) + c + cap + h, oy, ny),
            );
            tests.add(
                "seg_test@grown_rings",
                ((i1 - i0 + 1) * (j1 - j0 + 1)) as u64,
            );
            for j in j0..=j1 {
                for i in i0..=i1 {
                    let k = j * nx + i;
                    v[k] = v[k].min((seg_dist(at(i, j), a, b) - c).max(0.0));
                }
            }
        }
        for (k, x) in v.iter_mut().enumerate() {
            *x = if inside[k] { -d } else { *x - d };
        }
        tests.add("write@grown_rings", (nx * ny) as u64);
        let rings = march(&v, (nx, ny), &at);
        exteriors(rings)
    }
}

/// Fill the nodes of a grid (origin `o`, cell `h`, `n` nodes a side) whose points lie inside `ring`, by scanlines through the nodes.
fn fill(ring: &[Pt], o: Pt, h: f64, n: (usize, usize), out: &mut [bool], tests: &mut Counts) {
    let (nx, ny) = n;
    let (lo, hi) = ring
        .iter()
        .fold((f64::MAX, f64::MIN), |m, p| (m.0.min(p.1), m.1.max(p.1)));
    let j0 = (((lo - o.1) / h).ceil().max(0.0) as usize).min(ny);
    let j1 = ((((hi - o.1) / h).floor() + 1.0).max(0.0) as usize).min(ny);
    for j in j0..j1 {
        let y = o.1 + j as f64 * h;
        let mut xs: Vec<f64> = (0..ring.len())
            .filter_map(|k| {
                let (a, b) = (ring[k], ring[(k + 1) % ring.len()]);
                ((a.1 > y) != (b.1 > y)).then(|| a.0 + (y - a.1) / (b.1 - a.1) * (b.0 - a.0))
            })
            .collect();
        tests.add("write@fill", xs.len() as u64);
        xs.sort_by(f64::total_cmp);
        for w in xs.chunks_exact(2) {
            let i0 = (((w[0] - o.0) / h).ceil().max(0.0) as usize).min(nx);
            let i1 = ((((w[1] - o.0) / h).floor() + 1.0).max(0.0) as usize).min(nx);
            for i in i0..i1 {
                out[j * nx + i] = true;
            }
        }
    }
}

/// The zero level of a grid's values traced by marching squares into closed rings (the grid's border nodes read as above the level,
/// so every ring closes), each crossing on a cell edge interpolated linearly; a saddle cell joined through its center where the
/// center's mean is below the level. Each crossing is shared by the two cells either side of its grid edge, so the rings are linked
/// undirected.
/// A crossing named by the grid edge it lies on: (i, j, 0) the edge from node (i, j) east, (i, j, 1) south.
type Edge = (usize, usize, u8);

pub(crate) fn march(v: &[f64], n: (usize, usize), at: &dyn Fn(usize, usize) -> Pt) -> Vec<Vec<Pt>> {
    let (nx, ny) = n;
    let val = |i: usize, j: usize| {
        if i == 0 || j == 0 || i + 1 >= nx || j + 1 >= ny {
            1.0
        } else {
            v[j * nx + i]
        }
    };
    // a crossing named by the grid edge it lies on: (i, j, 0) the edge from node (i, j) east, (i, j, 1) south
    let point = |e: (usize, usize, u8)| {
        let (i, j, s) = e;
        let (i2, j2) = if s == 0 { (i + 1, j) } else { (i, j + 1) };
        let (a, b) = (val(i, j), val(i2, j2));
        let t = a / (a - b);
        let (p, q) = (at(i, j), at(i2, j2));
        (p.0 + (q.0 - p.0) * t, p.1 + (q.1 - p.1) * t)
    };
    let mut adj: HashMap<Edge, Vec<Edge>> = HashMap::new();
    for j in 0..ny - 1 {
        for i in 0..nx - 1 {
            // corners: 0 north-west, 1 north-east, 2 south-east, 3 south-west; a bit set where the corner is below the level
            let corners = [val(i, j), val(i + 1, j), val(i + 1, j + 1), val(i, j + 1)];
            let code = corners
                .iter()
                .enumerate()
                .fold(0u8, |c, (k, &x)| c | (u8::from(x < 0.0) << k));
            let (top, right, bottom, left) = ((i, j, 0), (i + 1, j, 1), (i, j + 1, 0), (i, j, 1));
            let joined = corners.iter().sum::<f64>() / 4.0 < 0.0;
            let pairs: Vec<(Edge, Edge)> = match code {
                1 | 14 => vec![(top, left)],
                2 | 13 => vec![(top, right)],
                4 | 11 => vec![(right, bottom)],
                8 | 7 => vec![(bottom, left)],
                3 | 12 => vec![(left, right)],
                6 | 9 => vec![(top, bottom)],
                5 if joined => vec![(top, right), (bottom, left)],
                5 => vec![(top, left), (right, bottom)],
                10 if joined => vec![(top, left), (right, bottom)],
                10 => vec![(top, right), (bottom, left)],
                _ => Vec::new(),
            };
            for (a, b) in pairs {
                adj.entry(a).or_default().push(b);
                adj.entry(b).or_default().push(a);
            }
        }
    }
    let mut rings = Vec::new();
    let mut keys: Vec<Edge> = adj.keys().copied().collect();
    keys.sort_unstable();
    let mut done: std::collections::HashSet<Edge> = std::collections::HashSet::new();
    for start in keys {
        if !done.insert(start) {
            continue;
        }
        let mut ring = vec![point(start)];
        let (mut prev, mut e) = (start, adj[&start][0]);
        while done.insert(e) {
            ring.push(point(e));
            let nb = &adj[&e];
            let f = if nb[0] == prev { nb[1] } else { nb[0] };
            (prev, e) = (e, f);
        }
        if ring.len() >= 3 {
            rings.push(ring);
        }
    }
    rings
}

/// The rings inside no other ring.
fn exteriors(rings: Vec<Vec<Pt>>) -> Vec<Vec<Pt>> {
    let held: Vec<bool> = rings
        .iter()
        .enumerate()
        .map(|(k, r)| {
            rings
                .iter()
                .enumerate()
                .any(|(m, o)| m != k && in_poly(r[0], o))
        })
        .collect();
    rings
        .into_iter()
        .zip(held)
        .filter(|(_, h)| !h)
        .map(|(r, _)| r)
        .collect()
}

/// A closed ring's arc length to the point of it nearest `p` (`LinearRing.project`).
#[must_use]
pub fn project(ring: &[Pt], p: Pt) -> f64 {
    let (mut best, mut at, mut run) = (f64::INFINITY, 0.0, 0.0);
    for k in 0..ring.len() {
        let (a, b) = (ring[k], ring[(k + 1) % ring.len()]);
        let l = dist(a, b);
        let t = if l == 0.0 {
            0.0
        } else {
            (((p.0 - a.0) * (b.0 - a.0) + (p.1 - a.1) * (b.1 - a.1)) / (l * l)).clamp(0.0, 1.0)
        };
        let d = dist(p, (a.0 + (b.0 - a.0) * t, a.1 + (b.1 - a.1) * t));
        if d < best {
            (best, at) = (d, run + t * l);
        }
        run += l;
    }
    at
}

/// A closed ring's length.
#[must_use]
pub fn length(ring: &[Pt]) -> f64 {
    (0..ring.len())
        .map(|k| dist(ring[k], ring[(k + 1) % ring.len()]))
        .sum()
}

/// The point at arc length `s` along a closed ring, `s` taken round it (`LinearRing.interpolate` of `s` modulo its length).
#[must_use]
pub fn interpolate(ring: &[Pt], s: f64) -> Pt {
    let total = length(ring);
    let mut s = s.rem_euclid(total.max(1e-12));
    for k in 0..ring.len() {
        let (a, b) = (ring[k], ring[(k + 1) % ring.len()]);
        let l = dist(a, b);
        if s <= l && l > 0.0 {
            let t = s / l;
            return (a.0 + (b.0 - a.0) * t, a.1 + (b.1 - a.1) * t);
        }
        s -= l;
    }
    ring[0]
}

/// The distance from `p` to a closed ring's line.
#[must_use]
pub fn ring_dist(ring: &[Pt], p: Pt) -> f64 {
    (0..ring.len())
        .map(|k| seg_dist(p, ring[k], ring[(k + 1) % ring.len()]))
        .fold(f64::INFINITY, f64::min)
}
