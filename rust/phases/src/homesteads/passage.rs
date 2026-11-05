//! A household reached across a neighbor's yard (feature 444 T30, from `rolling/passage.py`, feature 317): the custom of passage over
//! a neighbor's land for land with no way of its own. Within the settlement's share, each standing house the custom may cross to
//! offers tight seats against its land; a household is seated at one only where no layout there opens onto lane ground of its own
//! (`landlocked`) and its own land adjoins the neighbor's, and a walk from one of its doors to the neighbor's threshing yard stays
//! on the two households' land and clears both households' parts, every other homestead, the taken ground and the reserved wood
//! (`passage_of`, routed by `walk_of`). The walk is kept clear of every later homestead and never drawn.
//!
//! Research:
//!     passage over a neighbor's land - research/questions/0081-village-lanes.html: land with no road access of its own passes over the neighbor's (Wigmore 1892, Part V Section 8), and as a chain (Echigo)
//!     a tight seat only by passage - research/questions/0081-village-lanes.html, research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: admitted only with a walk across the neighbor's yard, refused where its yard opens onto lane ground of its own (`passage.opens`)
//!     walk not drawn as a lane - GUESS research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: the walk is recorded and kept clear, never drawn
//!     passage machinery - NONE: box geometry, the chain's bookkeeping and the walk's sampling; the units that decide carry their own claims

#![expect(
    clippy::many_single_char_names,
    clippy::manual_midpoint,
    reason = "the plane geometry's own names; two half-sizes summed at a map's few hundred feet, where no overflow is possible"
)]

use std::cmp::Ordering;
use std::collections::{BinaryHeap, HashMap};

use super::access::{
    house_gap, parts_of, point_clear, seg_box_within, taut, Parts, ACCESS_HALF_FT, TREAD,
};
use super::layout::Rect;
use super::Counts;
use crate::field::fan::Pt;
use crate::field::geom::dist;

/// How far beyond the parting a household's land may stand from its neighbor's and still adjoin it, and the longest chain of
/// passages to a way of its own.
///
/// Research:
///     land against land - GUESS research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: a foot beyond the growth's 2 px parting - 1
///     chain of passages - GUESS research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: across one neighbor reached across another and no farther, the Echigo chain - 2
pub const PASSAGE: (f64, u32) = (1.0, 2);

/// The tight seat's parting from its neighbor's land (feet), and how far off the bearing to the neighbor's yard a tight seat may be
/// offered (degrees).
///
/// Research:
///     the parting - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: the 2 ft the cluster's growth leaves between neighbors
///     tight seats on the yard's side - GUESS: no source could speak to it, a value of ours; within a quarter turn of the bearing to the neighbor's yard - 90
pub const TIGHT: (f64, f64) = (2.0, 90.0);

/// The walk's routing: the grid's step, the heuristic's weight and the taut pull's legs; and the pitch it is sampled at to stay on
/// the two households' land (feet).
///
/// Research:
///     its search steps and tolerances - NONE: a search's grain and breadth - 12, 1.5, 5 (`route.py` `ROUTE_STEP_PX`, `ROUTE_WEIGHT`, `ROUTE_LEGS`)
///     walk sampling pitch - NONE: 4 ft
pub const WALK: (f64, f64, usize, f64) = (12.0, 1.5, 5, 4.0);

/// A household's passage: its walk, the neighbor it is reached across, and the chain's depth.
#[derive(Clone, Debug, PartialEq)]
pub struct Passage {
    /// The walk from its door to the neighbor's threshing yard.
    pub walk: Vec<Pt>,
    /// The neighbor's index among the seated.
    pub of: usize,
    /// How many passages lie between it and a way of its own.
    pub depth: u32,
}

impl Passage {
    /// The passage as the door hands it over: its walk, whom it is reached across, and the chain's depth.
    #[must_use]
    pub fn parts(&self) -> (Vec<Pt>, usize, u32) {
        (self.walk.clone(), self.of, self.depth)
    }
}

/// A tight seat's context: the neighbor's index, its land as the growth parts it, and the household's own allotted reach (west,
/// east, north, south from its house).
#[derive(Clone, Copy, Debug)]
pub struct Tight {
    /// The neighbor.
    pub nb: usize,
    /// The neighbor's land.
    pub land: Rect,
    /// The household's allotted reach.
    pub own: (f64, f64, f64, f64),
}

/// The box a footprint reaching `reach` (west, east, north, south) from `c` covers.
#[must_use]
pub fn land_box(c: Pt, reach: (f64, f64, f64, f64)) -> Rect {
    let (w, e, n, s) = reach;
    (c.0 + (e - w) / 2.0, c.1 + (s - n) / 2.0, w + e, n + s)
}

/// The box grown by `by` on every side.
#[must_use]
pub fn grown(b: Rect, by: f64) -> Rect {
    (b.0, b.1, b.2 + 2.0 * by, b.3 + 2.0 * by)
}

/// How far apart two boxes stand: the larger of their gaps on the two axes.
#[must_use]
pub fn apart(a: Rect, b: Rect) -> f64 {
    ((a.0 - b.0).abs() - (a.2 + b.2) / 2.0).max((a.1 - b.1).abs() - (a.3 + b.3) / 2.0)
}

/// Does the bearing `ang` (radians) from a house at `c` stand within the tight seat's bearing of the bearing to its yard?
#[must_use]
pub fn yard_side(c: Pt, yard: Pt, ang: f64) -> bool {
    let to = (yard.1 - c.1).atan2(yard.0 - c.0);
    (((ang - to).to_degrees() + 180.0).rem_euclid(360.0) - 180.0).abs() < TIGHT.1
}

/// The point of the box nearest `p`.
#[must_use]
pub fn box_foot(p: Pt, b: Rect) -> Pt {
    (
        p.0.clamp(b.0 - b.2 / 2.0, b.0 + b.2 / 2.0),
        p.1.clamp(b.1 - b.3 / 2.0, b.1 + b.3 / 2.0),
    )
}

fn in_box(p: Pt, b: Rect) -> bool {
    (p.0 - b.0).abs() <= b.2 / 2.0 + 1e-9 && (p.1 - b.1).abs() <= b.3 / 2.0 + 1e-9
}

/// Does every point of the walk a-b, sampled at the walk's pitch, lie on one of the lands?
#[must_use]
#[expect(
    clippy::cast_possible_truncation,
    clippy::cast_sign_loss,
    clippy::cast_precision_loss,
    reason = "a walk's few dozen samples"
)]
pub fn on_their_land(a: Pt, b: Pt, lands: &[Rect]) -> bool {
    let n = ((dist(a, b) / WALK.3).ceil() as usize).max(1);
    (0..=n).all(|k| {
        let t = k as f64 / n as f64;
        let p = (a.0 + (b.0 - a.0) * t, a.1 + (b.1 - a.1) * t);
        lands.iter().any(|&l| in_box(p, l))
    })
}

/// What a household's own parts keep a walk off, each with the gap its leg test keeps: the house at the house gap, the annexes and
/// beds at the tread's, the fixtures but the persimmon at the corridor's half-width.
#[must_use]
pub fn own_parts(p: &Parts) -> Vec<(Rect, f64)> {
    let pgap = TREAD.0 + TREAD.2;
    let mut out = vec![(p.house, house_gap())];
    out.extend(p.sheds.iter().chain(&p.gardens).map(|&b| (b, pgap)));
    out.extend(
        p.fixtures
            .iter()
            .filter(|(k, _)| *k != super::fixtures::Kind::Persimmon)
            .map(|&(_, b)| (b, ACCESS_HALF_FT)),
    );
    out
}

/// What a walk keeps off besides the two households' parts: every other homestead's box, the taken ground (past its window, as
/// `beyond` says) and the reserved wood within the lane gap.
pub struct Walls<'a> {
    /// Every other homestead's box, each held off at the corridor's half-width.
    pub boxes: Vec<Rect>,
    /// The free ground.
    pub ground: &'a super::ground::Ground,
    /// Whether a point past the ground's window is taken.
    pub beyond: &'a dyn Fn(Pt) -> bool,
    /// The households' wood reservations.
    pub wood: &'a super::wood::Shares,
    /// The gap a way keeps off a reserved seat.
    pub lane_gap: f64,
}

impl Walls<'_> {
    /// Is `p` on taken ground?
    #[must_use]
    pub fn taken(&self, p: Pt) -> bool {
        self.ground.taken_at(p).unwrap_or_else(|| (self.beyond)(p))
    }

    /// Does the leg a-b run within the lane gap of a reserved wood seat?
    pub fn wood_bars(&self, a: Pt, b: Pt, tests: &mut Counts) -> bool {
        self.wood.corridor_bars(a, b, self.lane_gap, tests)
    }
}

/// Is the walk a-b clear of both households' parts, every other homestead, the taken ground (sampled at the walk's pitch) and
/// the reserved wood?
pub fn walk_clear(a: Pt, b: Pt, me: &Parts, nb: &Parts, walls: &Walls, tests: &mut Counts) -> bool {
    let parts = |p: &Parts, tests: &mut Counts| {
        p.house_clear(a, b, tests) && p.fixtures_clear(a, b, tests) && p.parts_clear(a, b, tests)
    };
    parts(me, tests)
        && parts(nb, tests)
        && !walls
            .boxes
            .iter()
            .any(|&bx| seg_box_within(a, b, bx, ACCESS_HALF_FT, tests))
        && on_ground(a, b, walls)
        && !walls.wood_bars(a, b, tests)
}

#[expect(
    clippy::cast_possible_truncation,
    clippy::cast_sign_loss,
    clippy::cast_precision_loss,
    reason = "a walk's few dozen samples"
)]
fn on_ground(a: Pt, b: Pt, walls: &Walls) -> bool {
    let n = ((dist(a, b) / WALK.3).ceil() as usize).max(1);
    (0..=n).all(|k| {
        let t = k as f64 / n as f64;
        !walls.taken((a.0 + (b.0 - a.0) * t, a.1 + (b.1 - a.1) * t))
    })
}

#[derive(PartialEq)]
struct Q(f64, (i64, i64));

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

/// Weighted A* from the cell (0, 0) over the cells within `n` of it on each axis, eight neighbors, the first step reaching two
/// cells: the first cell `goal_of` answers, as the path of cells and the goal's point (`route.py` `search`).
#[expect(clippy::cast_precision_loss, reason = "cell indices of a few dozen")]
fn search(
    is_open: &mut dyn FnMut((i64, i64)) -> bool,
    goal_of: &dyn Fn((i64, i64)) -> Option<Pt>,
    aim: Pt,
    n: i64,
    first_ok: &mut dyn FnMut((i64, i64)) -> bool,
    tests: &mut Counts,
) -> Option<(Vec<(i64, i64)>, Pt)> {
    let h = |c: (i64, i64)| WALK.1 * (c.0 as f64 - aim.0).hypot(c.1 as f64 - aim.1);
    let start = (0, 0);
    let mut best: HashMap<(i64, i64), f64> = HashMap::from([(start, 0.0)]);
    let mut prev: HashMap<(i64, i64), (i64, i64)> = HashMap::new();
    let mut opened: HashMap<(i64, i64), bool> = HashMap::new();
    let mut heap = BinaryHeap::from([Q(h(start), start)]);
    while let Some(Q(f, c)) = heap.pop() {
        // a stale entry - its cell reached cheaper since it was pushed - is passed over
        if f <= best[&c] + h(c) + 1e-9 {
            if c != start {
                if let Some(q) = goal_of(c) {
                    let mut cells = vec![c];
                    while let Some(&p) = prev.get(cells.last()?) {
                        cells.push(p);
                    }
                    cells.reverse();
                    return Some((cells, q));
                }
            }
            let reach: &[i64] = if c == start {
                &[-2, -1, 0, 1, 2]
            } else {
                &[-1, 0, 1]
            };
            for &di in reach {
                for &dj in reach {
                    tests.add("candidate@search", 1);
                    let nc = (c.0 + di, c.1 + dj);
                    if nc == c || nc.0.abs() > n || nc.1.abs() > n {
                        continue;
                    }
                    let open = *opened.entry(nc).or_insert_with(|| is_open(nc));
                    if !open || (c == start && !first_ok(nc)) {
                        continue;
                    }
                    let nd = best[&c] + (di as f64).hypot(dj as f64);
                    if nd < best.get(&nc).copied().unwrap_or(f64::INFINITY) {
                        best.insert(nc, nd);
                        prev.insert(nc, c);
                        heap.push(Q(nd + h(nc), nc));
                    }
                }
            }
        }
    }
    None
}

/// The walk from `door` to the neighbor's `yard`, routed over the cells on the two `lands` that clear both households' parts and
/// the walls, and pulled taut through `walk_clear` and `on_their_land`; its last point on the yard's edge. None where none is found.
#[expect(
    clippy::cast_possible_truncation,
    clippy::cast_precision_loss,
    reason = "a grid of a few dozen cells a side"
)]
pub fn walk_of(
    door: Pt,
    yard: Rect,
    lands: &[Rect],
    me: &Parts,
    nb: &Parts,
    walls: &Walls,
    tests: &mut Counts,
) -> Option<Vec<Pt>> {
    let step = WALK.0;
    let at = |c: (i64, i64)| (door.0 + c.0 as f64 * step, door.1 + c.1 as f64 * step);
    let keep: Vec<(Rect, f64)> = own_parts(me).into_iter().chain(own_parts(nb)).collect();
    let mut inner = Counts::default();
    let mut is_open = |c: (i64, i64)| {
        let p = at(c);
        lands
            .iter()
            .any(|&l| (p.0 - l.0).abs() <= l.2 / 2.0 && (p.1 - l.1).abs() <= l.3 / 2.0)
            && !walls.taken(p)
            && point_clear(p, &keep)
            && !walls
                .boxes
                .iter()
                .any(|&bx| seg_box_within(p, p, bx, ACCESS_HALF_FT, &mut inner))
            && !walls.wood_bars(p, p, &mut inner)
    };
    let goal_of = |c: (i64, i64)| {
        let p = at(c);
        let foot = box_foot(p, yard);
        (dist(p, foot) <= step).then_some(foot)
    };
    let mut first = Counts::default();
    let mut first_ok = |c: (i64, i64)| {
        let p = at(c);
        me.house_clear(door, p, &mut first)
            && me.fixtures_clear(door, p, &mut first)
            && me.parts_clear(door, p, &mut first)
    };
    let span = lands.iter().map(|l| l.2.max(l.3)).fold(0.0, f64::max);
    let aim = ((yard.0 - door.0) / step, (yard.1 - door.1) / step);
    let found = search(
        &mut is_open,
        &goal_of,
        aim,
        (span / step) as i64 + 2,
        &mut first_ok,
        tests,
    );
    for (k, v) in inner.0.into_iter().chain(first.0) {
        tests.add(&k, v);
    }
    let (cells, q) = found?;
    let mut pts = vec![door];
    pts.extend(cells[1..].iter().map(|&c| at(c)));
    pts.push(q);
    let mut legs = Counts::default();
    let run = taut(
        &pts,
        &mut |a, b| on_their_land(a, b, lands) && walk_clear(a, b, me, nb, walls, &mut legs),
        WALK.2,
        tests,
    );
    for (k, v) in legs.0 {
        tests.add(&k, v);
    }
    run
}

/// The passage a household laid as `b` at the tight seat `tight` is reached by - its walk from the first of its first two dooryard
/// doors that has one - or None: where the neighbor is past the chain or has no yard, or the household's land does not adjoin the
/// neighbor's. `nb` is the neighbor's bundle, `depth` its depth.
pub fn passage_of(
    b: &super::bundle::Bundle,
    nb: &super::bundle::Bundle,
    depth: Option<u32>,
    tight: &Tight,
    walls: &Walls,
    tests: &mut Counts,
) -> Option<Passage> {
    let depth = depth.filter(|&d| d < PASSAGE.1)?;
    let (hx, hy) = (b.boxes[0].0, b.boxes[0].1);
    let own = land_box((hx, hy), tight.own);
    let tol = TIGHT.0 + PASSAGE.0;
    if apart(own, tight.land) > tol {
        return None;
    }
    let lands = [grown(own, tol), grown(tight.land, tol)];
    let (me, them) = (parts_of(b), parts_of(nb));
    me.doors(ACCESS_HALF_FT)
        .into_iter()
        .take(2)
        .find_map(|door| {
            walk_of(door, them.yard, &lands, &me, &them, walls, tests).map(|walk| Passage {
                walk,
                of: tight.nb,
                depth: depth + 1,
            })
        })
}
