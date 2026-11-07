//! A dispersed farm's own water as a channel led into its grounds (feature 444 T33 D7b; `homesteads/farm_water.py`, feature 291
//! amendment 5): each farm, nearest the water first, a channel from the nearest points of the irrigation water to a step off its
//! threshing yard, routed round every building, yard and garden, every other farm's grove and well pocket, the crop and the lanes,
//! crossing no other water past its mouth - the shortest found; a later farm's channel may be led off one already drawn.
//!
//! Research:
//!     channel routing - NONE: candidate points, lattices, crossings and search budgets; the units that decide carry their own claims
//!     a channel into the grounds - research/questions/0031-clustered-and-scattered-villages-shuson-sanson.drawing.html: the shortest route found from the nearest sources
//!     farms nearest the water first - GUESS: no source could speak to it, a value of ours (feature 417 T29 pass C, 2026-10-25); the order channels are laid
//!     led off an earlier channel - research/questions/0031-clustered-and-scattered-villages-shuson-sanson.drawing.html: each drawn channel a source for the next
//!     a farm no channel reaches - research/questions/0031-clustered-and-scattered-villages-shuson-sanson.drawing.html: returned for a well of its own
//!     crosses no other water - GUESS: no source could speak to it, a value of ours (feature 417 T29 pass C, 2026-10-25); a route crossing other drawn water more than 6 ft past its mouth is refused
//!     how far a channel's source is sought - GUESS: no source could speak to it, a value of ours (feature 417 T29 pass C, 2026-10-25); 20 ft steps, 60 ft spread, widened fourfold where the nearest find nothing
#![expect(
    clippy::cast_possible_truncation,
    clippy::cast_sign_loss,
    clippy::cast_precision_loss,
    reason = "sample counts of a few hundred"
)]

use crate::counts::Counts;
use crate::field::fan::Pt;
use crate::field::geom::{dist, seg_dist};
use crate::ways::route::{route, Ask, Grounds};
use crate::ways::track::{crosses_fabric, edge_dist, in_poly, poly_box, segments_cross};

/// The candidate sources tried a farm, nearest first.
///
/// Research: its search steps - GUESS: the router's own budget (`farm_water.SOURCE_TRIES`)
pub const SOURCE_TRIES: usize = 6;
/// The spacing of candidate points along each supply course (ft).
///
/// Research: its search steps - GUESS
pub const SOURCE_STEP_FT: f64 = 20.0;
/// How far apart two tried sources stand at least (ft).
///
/// Research: its search steps - GUESS
pub const SOURCE_SPREAD_FT: f64 = 60.0;
/// The router's lattice for a channel (ft), finer than a lane's.
///
/// Research: its search steps - GUESS
pub const ROUTE_CELL_FT: f64 = 8.0;
/// How far off its threshing yard the channel ends (ft): a step.
///
/// Research: channel end off the yard - research/questions/0031-clustered-and-scattered-villages-shuson-sanson.drawing.html: a 6 ft step off the threshing yard
pub const DOORYARD_STEP_FT: f64 = 6.0;
/// The channel's gap off what it is routed round (ft), and how far past its mouth it may meet its own course (ft).
///
/// Research: its unstated figures - GUESS: 2 ft off the walls; 3 ft its own course; 6 ft its mouth
pub const GAPS: (f64, f64, f64) = (2.0, 3.0, 6.0);

/// A farm: its center, its threshing yard's ring, and its walls the others' channels keep off (its grove bands and well pocket).
pub struct Farm {
    /// The house's center.
    pub at: Pt,
    /// Its threshing yard's ring.
    pub yard: Vec<Pt>,
    /// Its own grove bands and well pocket: walls to every other farm's channel, not to its own.
    pub own: Vec<Vec<Pt>>,
}

/// What every farm's channel is routed round: the crop and paddies (hard), every building, yard, garden and lane (walls), the
/// irrigation courses it may be led off, and the drawn water it may not cross.
pub struct Ground<'a> {
    /// The crop and the paddies.
    pub hard: &'a [Vec<Pt>],
    /// Every building, yard, garden and lane.
    pub walls: &'a [Vec<Pt>],
    /// The supply courses.
    pub courses: &'a [Vec<Pt>],
    /// The drawn water.
    pub water: &'a [(Pt, Pt)],
}

fn closest(p: Pt, a: Pt, b: Pt) -> Pt {
    let (vx, vy) = (b.0 - a.0, b.1 - a.1);
    let l2 = vx * vx + vy * vy;
    // ...a point segment's own end: its dot product is 0, so any positive divisor gives 0
    let t = (((p.0 - a.0) * vx + (p.1 - a.1) * vy) / l2.max(f64::MIN_POSITIVE)).clamp(0.0, 1.0);
    (a.0 + vx * t, a.1 + vy * t)
}

fn length(p: &[Pt]) -> f64 {
    p.windows(2).map(|w| dist(w[0], w[1])).sum()
}

/// The `n` points along `courses`, every `step` and at each segment's point nearest `near`, nearest `near` first, each at least
/// `spread` from those before it (`farm_water.source_points`).
pub(crate) fn source_points(
    courses: &[Vec<Pt>],
    near: Pt,
    step: f64,
    n: usize,
    spread: f64,
    tests: &mut Counts,
) -> Vec<Pt> {
    let mut pts = Vec::new();
    for c in courses {
        for w in c.windows(2) {
            let k = ((dist(w[0], w[1]) / step) as usize).max(1);
            pts.extend((0..k).map(|i| {
                let f = i as f64 / k as f64;
                (
                    w[0].0 + (w[1].0 - w[0].0) * f,
                    w[0].1 + (w[1].1 - w[0].1) * f,
                )
            }));
            pts.push(closest(near, w[0], w[1]));
        }
    }
    tests.add("write@source_points", pts.len() as u64);
    pts.sort_by(|a, b| dist(*a, near).total_cmp(&dist(*b, near)));
    let mut out: Vec<Pt> = Vec::new();
    for q in pts {
        tests.add("dist@source_points", out.len() as u64);
        if out.iter().all(|&o| dist(q, o) >= spread) {
            out.push(q);
            if out.len() == n {
                break;
            }
        }
    }
    out
}

/// `step` off the yard's ring at the ring's point nearest `toward`, out along the line from the yard's middle.
pub(crate) fn dooryard_end(yard: &[Pt], toward: Pt, step: f64) -> Pt {
    let n = yard.len() as f64;
    let (cx, cy) = yard
        .iter()
        .fold((0.0, 0.0), |s, p| (s.0 + p.0 / n, s.1 + p.1 / n));
    let edge = (0..yard.len())
        .map(|k| closest(toward, yard[k], yard[(k + 1) % yard.len()]))
        .min_by(|a, b| dist(*a, toward).total_cmp(&dist(*b, toward)))
        .unwrap_or((cx, cy));
    let (dx, dy) = (edge.0 - cx, edge.1 - cy);
    let d = dx.hypot(dy).max(1e-12);
    (edge.0 + dx / d * step, edge.1 + dy / d * step)
}

pub(crate) fn cross_t(a: Pt, b: Pt, c: Pt, d: Pt) -> f64 {
    let den = (b.0 - a.0) * (d.1 - c.1) - (b.1 - a.1) * (d.0 - c.0);
    if den.abs() < 1e-12 {
        return 0.0;
    }
    ((c.0 - a.0) * (d.1 - c.1) - (c.1 - a.1) * (d.0 - c.0)) / den
}

/// Does `path` cross any of `water` more than `free` along it from its start?
pub(crate) fn crosses_other_water(
    path: &[Pt],
    water: &[(Pt, Pt)],
    free: f64,
    tests: &mut Counts,
) -> bool {
    let mut run = 0.0;
    for w in path.windows(2) {
        let (a, b) = (w[0], w[1]);
        let l = dist(a, b);
        tests.add("seg_test@crosses_other_water", water.len() as u64);
        if water
            .iter()
            .any(|&(c, d)| segments_cross(a, b, c, d) && run + cross_t(a, b, c, d) * l > free)
        {
            return true;
        }
        run += l;
    }
    false
}

fn inside_the_crop(q: Pt, hard: &[Vec<Pt>]) -> bool {
    hard.iter()
        .any(|r| r.len() >= 3 && in_poly(q, r) && edge_dist(q, r) > 1.0)
}

/// The straight chord where it crosses nothing, else the routed way.
fn straight_or_routed(
    src: Pt,
    end: Pt,
    walls: &[Vec<Pt>],
    water: &[(Pt, Pt)],
    ask: Ask,
    tests: &mut Counts,
) -> Vec<Pt> {
    let chord = [src, end];
    let clear = !walls
        .iter()
        .any(|r| r.len() >= 3 && crosses_fabric(&chord, r, poly_box(r), 0.0, tests))
        && !water.iter().any(|&(c, d)| segments_cross(src, end, c, d));
    if clear {
        return chord.to_vec();
    }
    routed(src, end, walls, water, ask, tests)
}

fn routed(
    src: Pt,
    end: Pt,
    walls: &[Vec<Pt>],
    water: &[(Pt, Pt)],
    ask: Ask,
    tests: &mut Counts,
) -> Vec<Pt> {
    let g = Grounds {
        hard: &[],
        walls,
        water,
    };
    route(src, end, &g, None, ask, tests)
}

/// The channel into `farm`'s grounds (`farm_water.farm_channel`): the nearest sources and a step off the yard's side facing each,
/// routed, the shortest kept; where none is found, the wider search - more sources, off the crop, the straight chord tried first.
/// Empty where no course reaches its dooryard.
fn farm_channel(
    farm: &Farm,
    walls: &[Vec<Pt>],
    ground: &Ground,
    courses: &[Vec<Pt>],
    water: &[(Pt, Pt)],
    tests: &mut Counts,
) -> Vec<Pt> {
    let ring = &farm.yard;
    if ring.len() < 3 {
        return Vec::new();
    }
    let n = ring.len() as f64;
    let c = ring
        .iter()
        .fold((0.0, 0.0), |s, p| (s.0 + p.0 / n, s.1 + p.1 / n));
    let sides: Vec<Pt> = (0..ring.len())
        .map(|k| {
            let (a, b) = (ring[k], ring[(k + 1) % ring.len()]);
            (f64::midpoint(a.0, b.0), f64::midpoint(a.1, b.1))
        })
        .collect();
    let all: Vec<Vec<Pt>> = ground.hard.iter().chain(walls).cloned().collect();
    let ask = Ask {
        cell: ROUTE_CELL_FT,
        gap: GAPS.0,
        ..Ask::default()
    };
    let offered = source_points(
        courses,
        c,
        SOURCE_STEP_FT,
        SOURCE_TRIES * 4,
        SOURCE_SPREAD_FT * 4.0,
        tests,
    );
    let near = source_points(
        courses,
        c,
        SOURCE_STEP_FT,
        SOURCE_TRIES,
        SOURCE_SPREAD_FT,
        tests,
    );
    let wider: Vec<Pt> = near
        .iter()
        .copied()
        .chain(
            offered
                .iter()
                .copied()
                .filter(|q| !near.contains(q) && !inside_the_crop(*q, ground.hard))
                .take(SOURCE_TRIES),
        )
        .collect();
    let mut routes: Vec<Vec<Pt>> = Vec::new();
    for (srcs, straight) in [(&near, false), (&wider, true)] {
        for &src in srcs {
            let mine: Vec<(Pt, Pt)> = water
                .iter()
                .copied()
                .filter(|&(a, b)| seg_dist(src, a, b) > GAPS.1)
                .collect();
            let mut toward = vec![src];
            let mut by: Vec<Pt> = sides.clone();
            by.sort_by(|a, b| dist(*a, src).total_cmp(&dist(*b, src)));
            toward.extend(by);
            for t in toward {
                tests.add("candidate@farm_channel", 1);
                let e = dooryard_end(ring, t, DOORYARD_STEP_FT);
                let p = if straight {
                    straight_or_routed(src, e, &all, &mine, ask, tests)
                } else {
                    routed(src, e, &all, &mine, ask, tests)
                };
                if p.len() >= 2 && !crosses_other_water(&p, water, GAPS.2, tests) {
                    routes.push(p);
                }
            }
        }
        if !routes.is_empty() {
            break;
        }
    }
    routes
        .into_iter()
        .min_by(|a, b| length(a).total_cmp(&length(b)))
        .unwrap_or_default()
}

/// Each farm's channel, in the farms' order (`farm_water.farm_channels`): taken nearest the water first, each drawn channel a
/// course and water for the next; an empty run for a farm no course reaches.
#[must_use]
pub fn farm_channels(farms: &[Farm], ground: &Ground, tests: &mut Counts) -> Vec<Vec<Pt>> {
    let mut out = vec![Vec::new(); farms.len()];
    if ground.courses.is_empty() {
        return out;
    }
    let mut courses: Vec<Vec<Pt>> = ground.courses.to_vec();
    let mut water: Vec<(Pt, Pt)> = ground.water.to_vec();
    let mut order: Vec<(f64, usize)> = farms
        .iter()
        .enumerate()
        .map(|(i, f)| {
            let q = source_points(&courses, f.at, SOURCE_STEP_FT, 1, 0.0, tests);
            (q.first().map_or(f64::INFINITY, |&q| dist(f.at, q)), i)
        })
        .collect();
    order.sort_by(|a, b| a.0.total_cmp(&b.0).then(a.1.cmp(&b.1)));
    for (_, i) in order {
        let walls: Vec<Vec<Pt>> = ground
            .walls
            .iter()
            .cloned()
            .chain(
                farms
                    .iter()
                    .enumerate()
                    .filter(|&(j, _)| j != i)
                    .flat_map(|(_, f)| f.own.iter().cloned()),
            )
            .collect();
        tests.add("write@channel_walls", walls.len() as u64);
        let path = farm_channel(&farms[i], &walls, ground, &courses, &water, tests);
        if path.len() >= 2 {
            courses.push(path.clone());
            water.extend(path.windows(2).map(|w| (w[0], w[1])));
        }
        out[i] = path;
    }
    out
}
