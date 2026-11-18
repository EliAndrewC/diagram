//! An entrance board's ways out (feature 449 T171): every household's way out walked over the manifest's `lanes` from its `houses`,
//! and how many of those ways pass the board - the count the notes census's entrance-board line states.
//!
//! WHY IT IS HERE (T171, the round arbiter's route (a), `ask:set-down-449-pilot`): feature 444 cut the census's entrance branch with
//! the Python hamlet engine, and the line fell back to a 250-ft farmhouse count, which feature 261 does not judge an entrance board by -
//! it stands where the approach meets the settlement, so the houses near it say nothing about whether every departure passes it (261
//! FR-015). The count is `rust/parked/src/law/routes.rs`'s `departure_routes` (the deleted `structures/fixtures/_helpers.py`'s), ported
//! here rather than depended on: `parked` compiles nothing until the GM resumes its stages.
//!
//! The walk starts from the connector's end farthest from the houses, as the parked port does: the Python started there too, and only
//! gated the walk on a handover (`kosatsuba_handover`), which stands wherever another way meets the track - every household's way
//! does, by construction, on an engine-drawn hamlet. A connector the router extends past the frame (`run_on`) is the road going on, not
//! the way out, and gives no end, as the Python's `departure_routes` read it.
//!
//! Research:
//!     an entrance board passed by every way out - research/questions/0190-notice-boards-kosatsuba.drawing.html: a board at a rolled settlement's entrance is set near where the households' ways have joined the way out, so every household passes it
//!     its search steps and tolerances - GUESS: no source could speak to it, a value of ours (feature 417 T38 pass N12, 2026-10-25) - 10 (sample step); 7 (graph join tolerance)
//!     a dwelling's reach - NONE: one number with the entrance's, 150 ft from a way a dwelling may stand and still be walked out by it
//!     entrance board beside the handover - GUESS: searched, the record silent (feature 417 T36 pass P1, 2026-10-25); within 20 ft of where every departure passes

#![expect(
    clippy::many_single_char_names,
    reason = "the plane geometry's own names, as the parked port's"
)]

use std::cmp::Ordering;
use std::collections::{BinaryHeap, HashMap};

use l7r_gate_research::Error;
use l7r_guard::shared::pyjson::truthy;
use serde_json::Value;

use super::{get, items, number};
use crate::py::iterate;

/// A point of the plane, in the manifest's units.
pub type Pt = (f64, f64);

/// The graph's sample step and its join (ft).
///
/// Research:
///     its search steps and tolerances - GUESS: no source could speak to it, a value of ours (feature 417 T38 pass N12, 2026-10-25) - 10 (sample step); 7 (graph join tolerance)
pub const WALK: (f64, f64) = (10.0, 7.0);

/// How far from a way a dwelling may stand and still be walked out by it (ft).
///
/// Research:
///     a dwelling's reach - NONE: one number with the entrance's - 150
pub const REACH_FT: f64 = 150.0;

/// How far from a way out's points the board may stand and still be passed by it (ft): the board's own verge off the tread plus a
/// board's length either way along it (feature 261, `KOSATSUBA_HANDOVER_BAND_FT`).
///
/// Research:
///     entrance board beside the handover - GUESS: searched, the record silent (feature 417 T36 pass P1, 2026-10-25); within 20 ft of where every departure passes - 20
pub const BAND_FT: f64 = 20.0;

/// One drawn lane: its points, whether it is the track out, and whether it runs on past the frame.
#[derive(Debug, Clone, Default, PartialEq)]
pub struct Lane {
    pub pts: Vec<Pt>,
    pub connector: bool,
    pub run_on: bool,
}

/// The manifest's `lanes`: each lane's `pts` as (x, y) pairs, `connector` and `run_on` read as Python's truth.
///
/// # Errors
/// A lane that is no dict, a point that is no pair, or a coordinate `float()` refuses.
pub fn lanes(m: &Value) -> Result<Vec<Lane>, Error> {
    let mut out = Vec::new();
    for ln in items(m, "lanes")? {
        let flag = |key: &str| -> Result<bool, Error> { Ok(get(&ln, key)?.is_some_and(truthy)) };
        let mut pts = Vec::new();
        for p in items(&ln, "pts")? {
            let xy = iterate(&p)?;
            let [x, y] = xy.as_slice() else {
                return Err(Error::new(
                    "ValueError",
                    format!("a lane point has {} values, not 2", xy.len()),
                ));
            };
            pts.push((number(x)?, number(y)?));
        }
        out.push(Lane {
            pts,
            connector: flag("connector")?,
            run_on: flag("run_on")?,
        });
    }
    Ok(out)
}

fn dist(a: Pt, b: Pt) -> f64 {
    (a.0 - b.0).hypot(a.1 - b.1)
}

/// A heap entry, least distance first, then least node.
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

#[expect(
    clippy::cast_possible_truncation,
    reason = "a sheet's coordinates over the join are a few thousand cells"
)]
fn cell(v: f64) -> i64 {
    (v / WALK.1).floor() as i64
}

/// The drawn lanes sampled every step into a graph, its samples within the join of each other one junction.
fn lane_graph(lanes: &[Lane]) -> (Vec<Pt>, Vec<Vec<(usize, f64)>>) {
    let (step, join) = WALK;
    let mut nodes: Vec<Pt> = Vec::new();
    let mut edges: Vec<Vec<(usize, f64)>> = Vec::new();
    for l in lanes {
        let mut prev: Option<usize> = None;
        for w in l.pts.windows(2) {
            let (a, b) = (w[0], w[1]);
            #[expect(
                clippy::cast_possible_truncation,
                clippy::cast_sign_loss,
                reason = "a lane's samples are a few hundred"
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
    for (i, &q) in nodes.iter().enumerate() {
        for dx in -1..=1 {
            for dy in -1..=1 {
                let near = grid.get(&(cell(q.0) + dx, cell(q.1) + dy));
                for &j in near.map_or(&[][..], Vec::as_slice) {
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

/// Every household's way out, as the points it walks from its nearest reached sample to the track's outer end; none without a
/// track (a connector that does not run on) or a house, and none for a house farther than [`REACH_FT`] from every reached sample.
#[must_use]
pub fn departure_routes(lanes: &[Lane], houses: &[Pt]) -> Vec<Vec<Pt>> {
    let near = |q: Pt| {
        houses
            .iter()
            .map(|&h| dist(q, h))
            .fold(f64::INFINITY, f64::min)
    };
    let outer = lanes
        .iter()
        .filter(|l| l.connector && !l.run_on && l.pts.len() >= 2)
        .flat_map(|l| [l.pts[0], l.pts[l.pts.len() - 1]])
        .max_by(|a, b| near(*a).total_cmp(&near(*b)));
    let Some(outer) = outer.filter(|_| !houses.is_empty()) else {
        return Vec::new();
    };
    let (nodes, edges) = lane_graph(lanes);
    // a connector of two or more points always gives a sample, so the graph has a node to start from
    let src = (0..nodes.len())
        .min_by(|&a, &b| dist(nodes[a], outer).total_cmp(&dist(nodes[b], outer)))
        .unwrap_or_default();
    let mut d = vec![f64::INFINITY; nodes.len()];
    let mut back = vec![usize::MAX; nodes.len()];
    d[src] = 0.0;
    let mut heap = BinaryHeap::from([Q(0.0, src)]);
    while let Some(Q(du, u)) = heap.pop() {
        // an entry passed over where a cheaper one already settled its node
        let live = du <= d[u];
        for &(v, w) in edges[u].iter().filter(|_| live) {
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
            (dist(nodes[s], h) <= REACH_FT).then(|| {
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

/// How many of `routes` never come within `near` of `at` - the ways out that do not pass a board there.
#[must_use]
pub fn routes_missed(routes: &[Vec<Pt>], at: Pt, near: f64) -> usize {
    routes
        .iter()
        .filter(|r| !r.iter().any(|&q| dist(q, at) <= near))
        .count()
}

#[cfg(test)]
mod tests {
    use serde_json::json;

    use super::{departure_routes, lanes, routes_missed, Lane, BAND_FT};

    fn lane(pts: &[(f64, f64)], connector: bool) -> Lane {
        Lane {
            pts: pts.to_vec(),
            connector,
            run_on: false,
        }
    }

    /// A track in from the west to a junction at (100, 0), and two lanes off it: one north to a house, one east to another.
    fn hamlet() -> Vec<Lane> {
        vec![
            lane(&[(-200.0, 0.0), (100.0, 0.0)], true),
            lane(&[(100.0, 0.0), (100.0, 80.0)], false),
            lane(&[(100.0, 0.0), (250.0, 0.0)], false),
        ]
    }

    #[test]
    fn every_house_walks_out_to_the_track_s_outer_end() {
        let routes = departure_routes(&hamlet(), &[(110.0, 85.0), (255.0, 10.0)]);
        assert_eq!(routes.len(), 2);
        let ends: Vec<(f64, f64)> = routes.iter().map(|r| r[r.len() - 1]).collect();
        assert_eq!(ends, [(-200.0, 0.0), (-200.0, 0.0)]);
        // a board at the junction is passed by both; one up the north lane by one; one off every lane by none
        assert_eq!(routes_missed(&routes, (100.0, 5.0), BAND_FT), 0);
        assert_eq!(routes_missed(&routes, (100.0, 70.0), BAND_FT), 1);
        assert_eq!(routes_missed(&routes, (400.0, 400.0), BAND_FT), 2);
    }

    #[test]
    fn a_house_out_of_reach_a_lone_lane_and_no_track_walk_nothing() {
        // the house 300 ft off every lane has no way out; a lane joined to nothing is never reached
        let mut ls = hamlet();
        ls.push(lane(&[(1000.0, 1000.0), (1100.0, 1000.0)], false));
        let routes = departure_routes(&ls, &[(110.0, 85.0), (100.0, 400.0), (1050.0, 1005.0)]);
        assert_eq!(routes.len(), 1);
        // no house, no connector, or a connector that runs on past the frame: no ways out
        assert!(departure_routes(&hamlet(), &[]).is_empty());
        assert!(departure_routes(&hamlet()[1..], &[(110.0, 85.0)]).is_empty());
        let mut on = hamlet();
        on[0].run_on = true;
        assert!(departure_routes(&on, &[(110.0, 85.0)]).is_empty());
        // a one-point connector gives no end
        assert!(departure_routes(&[lane(&[(0.0, 0.0)], true)], &[(0.0, 0.0)]).is_empty());
    }

    #[test]
    fn a_way_out_takes_the_cheaper_of_two_ways_round() {
        // a loop: the house is reached both ways round, the short way kept
        let ls = vec![
            lane(&[(0.0, 0.0), (100.0, 0.0)], true),
            lane(&[(100.0, 0.0), (100.0, 50.0), (300.0, 50.0)], false),
            lane(&[(100.0, 0.0), (300.0, 0.0), (300.0, 50.0)], false),
            lane(
                &[(100.0, 0.0), (100.0, -400.0), (300.0, -400.0), (300.0, 0.0)],
                false,
            ),
        ];
        let routes = departure_routes(&ls, &[(310.0, 25.0)]);
        assert_eq!(routes.len(), 1);
        assert!(routes[0].iter().all(|q| q.1 > -1.0), "{:?}", routes[0]);
    }

    #[test]
    fn the_manifest_s_lanes_are_read_as_python_reads_them() {
        let m = json!({"lanes": [{"pts": [[0, "1.5"], [2, 3]], "connector": 1, "run_on": 0}, {"pts": null}]});
        assert_eq!(
            lanes(&m).unwrap(),
            vec![
                Lane {
                    pts: vec![(0.0, 1.5), (2.0, 3.0)],
                    connector: true,
                    run_on: false
                },
                Lane::default()
            ]
        );
        assert!(lanes(&json!({})).unwrap().is_empty());
        for bad in [
            json!({"lanes": [{"pts": [[0, 1, 2]]}]}),
            json!({"lanes": [{"pts": [[0, "x"]]}]}),
            json!({"lanes": [{"pts": [5]}]}),
            json!({"lanes": [3]}),
            json!({"lanes": [{"pts": [[0, 1]], "connector": 1}, {"run_on": 1, "pts": [[[1], 2]]}]}),
        ] {
            assert!(lanes(&bad).is_err(), "{bad}");
        }
    }
}
