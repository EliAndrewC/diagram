//! Every household's way out (feature 444 T30): the drawn lanes sampled every 10 ft into a graph whose samples within 7 ft are
//! one junction, each dwelling's nearest sample within its reach walked the shortest way to the track out's outer end; and the
//! ways out that cross one brook more than once, which a tree lane may not add (`structures/fixtures/_helpers.py`
//! `departure_routes`; `law/ends.py` `way_outs_crossing`, `adds_a_way_out_crossing`).
//!
//! The route starts from the track's end farthest from the houses, where Python reads it from the notice board's handover: a
//! handover stands wherever another way meets the track, which every admitted household's way does by construction, so a tree
//! with a household's way always has one.
//!
//! Research:
//!     way out crosses each brook once - research/questions/0035-villages-beside-their-stream-one-bank-or-both.drawing.html
//!     its search steps and tolerances - GUESS: no source could speak to it, a value of ours (feature 417 T38 pass N12, 2026-10-25) - 10 (sample step); 7 (graph join tolerance)
//!     a dwelling's reach - NONE: one number with the entrance's, 150 ft from a way a dwelling may stand and still be walked out by it

#![expect(
    clippy::many_single_char_names,
    reason = "the plane geometry's own names"
)]

use std::cmp::Ordering;
use std::collections::{BinaryHeap, HashMap};

use super::meet::Lane;
use super::rules::crossing_points;
use super::Counts;
use crate::field::fan::Pt;
use crate::field::geom::dist;

/// The graph's sample step, its join, and a dwelling's reach (ft).
///
/// Research:
///     its search steps and tolerances - GUESS: no source could speak to it, a value of ours (feature 417 T38 pass N12, 2026-10-25) - 10 (sample step); 7 (graph join tolerance)
///     a dwelling's reach - NONE: one number with the entrance's - 150
pub const WALK: (f64, f64, f64) = (10.0, 7.0, 150.0);

#[derive(PartialEq)]
struct Q(f64, usize);

impl Eq for Q {}

impl PartialOrd for Q {
    fn partial_cmp(&self, o: &Self) -> Option<Ordering> {
        Some(self.cmp(o))
    }
}

impl Ord for Q {
    fn cmp(&self, o: &Self) -> Ordering {
        o.0.total_cmp(&self.0).then(o.1.cmp(&self.1))
    }
}

#[expect(clippy::cast_possible_truncation, reason = "cells of a few hundred")]
fn cell(v: f64) -> i64 {
    (v / WALK.1).floor() as i64
}

/// The drawn lanes sampled every step into a graph, its samples within the join of each other one junction.
fn lane_graph(lanes: &[Lane], tests: &mut Counts) -> (Vec<Pt>, Vec<Vec<(usize, f64)>>) {
    let (step, join, _) = WALK;
    let mut nodes: Vec<Pt> = Vec::new();
    let mut edges: Vec<Vec<(usize, f64)>> = Vec::new();
    for l in lanes {
        let mut prev: Option<usize> = None;
        for w in l.pts.windows(2) {
            let (a, b) = (w[0], w[1]);
            #[expect(
                clippy::cast_possible_truncation,
                clippy::cast_sign_loss,
                reason = "a few hundred samples"
            )]
            let n = ((dist(a, b) / step) as u32).max(1);
            for i in 0..=n {
                let f = f64::from(i) / f64::from(n);
                nodes.push((a.0 + (b.0 - a.0) * f, a.1 + (b.1 - a.1) * f));
                edges.push(Vec::new());
                let j = nodes.len() - 1;
                if let Some(p) = prev {
                    let d = dist(nodes[p], nodes[j]);
                    edges[p].push((j, d));
                    edges[j].push((p, d));
                }
                prev = Some(j);
            }
        }
    }
    let mut grid: HashMap<(i64, i64), Vec<usize>> = HashMap::new();
    for (i, q) in nodes.iter().enumerate() {
        grid.entry((cell(q.0), cell(q.1))).or_default().push(i);
    }
    for i in 0..nodes.len() {
        let q = nodes[i];
        for dx in -1..=1 {
            for dy in -1..=1 {
                for &j in grid
                    .get(&(cell(q.0) + dx, cell(q.1) + dy))
                    .map_or(&[][..], Vec::as_slice)
                {
                    tests.add("dist@departure_routes", 1);
                    if j > i && dist(q, nodes[j]) < join {
                        edges[i].push((j, 0.0));
                        edges[j].push((i, 0.0));
                    }
                }
            }
        }
    }
    (nodes, edges)
}

/// Every household's way out, as the points it walks from its nearest sample to the track's outer end; none without a track or a
/// house.
#[must_use]
pub fn departure_routes(lanes: &[Lane], houses: &[Pt], tests: &mut Counts) -> Vec<Vec<Pt>> {
    let reach = WALK.2;
    let ends: Vec<Pt> = lanes
        .iter()
        .filter(|l| l.connector && l.pts.len() >= 2)
        .flat_map(|l| [l.pts[0], l.pts[l.pts.len() - 1]])
        .collect();
    let Some(outer) = ends.iter().copied().max_by(|a, b| {
        let near = |q: Pt| {
            houses
                .iter()
                .map(|&h| dist(q, h))
                .fold(f64::INFINITY, f64::min)
        };
        near(*a).total_cmp(&near(*b))
    }) else {
        return Vec::new();
    };
    if houses.is_empty() {
        return Vec::new();
    }
    let (nodes, edges) = lane_graph(lanes, tests);
    let src = (0..nodes.len())
        .min_by(|&a, &b| dist(nodes[a], outer).total_cmp(&dist(nodes[b], outer)))
        .unwrap_or(0);
    let mut d = vec![f64::INFINITY; nodes.len()];
    let mut back = vec![usize::MAX; nodes.len()];
    let mut heap = BinaryHeap::new();
    if !nodes.is_empty() {
        d[src] = 0.0;
        heap.push(Q(0.0, src));
    }
    while let Some(Q(du, u)) = heap.pop() {
        // an entry passed over where a cheaper one already settled its node
        let live = du <= d[u];
        for &(v, w) in edges[u].iter().filter(|_| live) {
            tests.add("candidate@departure_routes", 1);
            if du + w < d[v] {
                d[v] = du + w;
                back[v] = u;
                heap.push(Q(du + w, v));
            }
        }
    }
    let reached: Vec<usize> = (0..nodes.len()).filter(|&i| d[i].is_finite()).collect();
    houses
        .iter()
        .filter_map(|&h| {
            let s = reached
                .iter()
                .copied()
                .min_by(|&a, &b| dist(nodes[a], h).total_cmp(&dist(nodes[b], h)))?;
            (dist(nodes[s], h) <= reach).then(|| {
                let mut path = vec![nodes[s]];
                let mut c = s;
                while c != src {
                    c = back[c];
                    path.push(nodes[c]);
                }
                path
            })
        })
        .collect()
}

/// How many households' ways out cross one brook more than once.
#[must_use]
pub fn way_outs_crossing(brooks: &[Vec<Pt>], routes: &[Vec<Pt>], tests: &mut Counts) -> usize {
    brooks
        .iter()
        .map(|b| {
            routes
                .iter()
                .filter(|r| crossing_points(r, b, tests).len() > 1)
                .count()
        })
        .sum()
}

/// Would drawing `run` as a lane beside `lanes` leave more households' ways out crossing a brook more than once than without it?
#[must_use]
pub fn adds_a_way_out_crossing(
    lanes: &[Lane],
    run: &[Pt],
    width: f64,
    houses: &[Pt],
    brooks: &[Vec<Pt>],
    tests: &mut Counts,
) -> bool {
    if brooks.is_empty() {
        return false;
    }
    let mut added = lanes.to_vec();
    added.push(Lane {
        pts: run.to_vec(),
        w: width,
        ..Lane::default()
    });
    let after = way_outs_crossing(brooks, &departure_routes(&added, houses, tests), tests);
    after > 0 && after > way_outs_crossing(brooks, &departure_routes(lanes, houses, tests), tests)
}
