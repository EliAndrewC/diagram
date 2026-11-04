//! The web as walked (feature 444 T30): lanes met end to end read as one way; a way may not run beside another past a pitch; a
//! free end that stops short of a way it is making for is carried onto it, as the settle carries it; and a farmhouse discharges at
//! most two free ends (`joints.py` `as_walked`; `serve.py` `sampled`, `shadow_measure`, `runs_beside`, `shadowed_by`; `tree.py`
//! `tree_shadows`, `walked_shadows`, `as_joined`; `law/meet.py` `near_misses`, `free_end`, `box_gap`, `span_walkable`,
//! `meets_clean`; `law/shape.py` `reach_to_steading`; `law/ends.py` `fronting_ends`).
//!
//! Research:
//!     lanes met end to end are one - research/questions/0081-village-lanes.drawing.html: read as one way
//!     no doubled band - DEVIATION research/questions/0081-village-lanes.drawing.html: two paths running side by side are drawn as one, and two lanes met end to end are read as one (`walked_shadows`) - an access lane may not run beside another past a pitch, measured with no angle where the page's test is under 20 degrees, a departure the code keeps until feature 417 T32
//!     two ways read apart - CONVENTION: 30 ft at fit zoom
//!     the along-row span - NONE: the pitch a way may run beside another for, 100 ft
//!     a join that stops short - research/questions/0081-village-lanes.drawing.html: ends within 25 ft of one another are joined
//!     making for a way - CONVENTION: within 60 degrees of the end's heading
//!     an end reaches a farmhouse - GUESS research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: "within 60 ft of the house, or within 12 ft of the steading's built ground" (the page's own guess)
//!     free ends at a house - GUESS: searched, the record silent (feature 417 T29 pass A2, 2026-10-25) - one main door served a minka's household (JAANUS, Edo period, pass A2); no page gives how many ends meet at one; at most `DOORSTEP_MAX` (2) free lane ends at a house
#![expect(
    clippy::many_single_char_names,
    clippy::cast_possible_truncation,
    clippy::cast_sign_loss,
    clippy::cast_precision_loss,
    reason = "the plane geometry's own names, and sample counts of a few hundred"
)]

use super::ground::{hooked, house_hit, House, LawGround};
use super::meet::{
    connector_hairpin_ends, folded_joint_pairs, foot, joints, needle_ends, Lane, TOUCH,
};
use super::Counts;
use crate::field::fan::Pt;
use crate::field::geom::{dist, seg_dist};
use crate::ways::route::length;
use crate::ways::squaring::kink_spans;
use crate::ways::track::{crosses_fabric, in_poly, poly_box, segments_cross, Box4};

/// How near two ways read as one, and how long beside one another they may run (ft).
///
/// Research:
///     two ways read apart - CONVENTION: 30 ft at fit zoom
///     the along-row span - NONE: the pitch a way may run beside another for, 100 ft
pub const SHADOW: (f64, f64) = (30.0, 100.0);

/// A join's reach, the bearing it is made for within (degrees), and the most free ends one farmhouse may discharge.
///
/// Research:
///     a join that stops short - research/questions/0081-village-lanes.drawing.html: ends within 25 ft of one another are joined
///     making for a way - CONVENTION: within 60 degrees of the end's heading
///     ends one house may absolve - GUESS: searched, the record silent (feature 417 T29 pass A2, 2026-10-25); two
pub const JOIN: (f64, f64, usize) = (25.0, 60.0, 2);

/// An end's reach to a farmhouse: from its center, and from its steading's built ground (ft).
///
/// Research:
///     an end reaches a farmhouse - GUESS research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: within 60 ft of the house, or within 12 ft of the steading's built ground
pub const STEADING: (f64, f64) = (60.0, 12.0);

/// The ways a walker reads: every chain of lanes met end to end joined into one polyline, and each lane's way.
#[must_use]
pub fn as_walked(lanes: &[Lane]) -> (Vec<Vec<Pt>>, Vec<usize>) {
    crate::counts::note("write@as_walked", lanes.len() as u64);
    let n = lanes.len();
    let mut link: std::collections::HashMap<(usize, i8), (usize, i8)> =
        std::collections::HashMap::new();
    for (i, ei, j, ej) in joints(lanes) {
        link.insert((i, ei), (j, ej));
        link.insert((j, ej), (i, ei));
    }
    let other = |e: i8| -1 - e;
    let mut owner = vec![usize::MAX; n];
    let mut ways: Vec<Vec<Pt>> = Vec::new();
    for start in 0..n {
        if owner[start] != usize::MAX {
            continue;
        }
        let (mut cur, mut free) = (start, 0i8);
        let mut seen = vec![start];
        while let Some(&(nxt, at)) = link.get(&(cur, free)).filter(|l| !seen.contains(&l.0)) {
            (cur, free) = (nxt, other(at));
            seen.push(cur);
        }
        let k = ways.len();
        let mut way: Vec<Pt> = Vec::new();
        loop {
            owner[cur] = k;
            let mut p = lanes[cur].pts.clone();
            if free != 0 {
                p.reverse();
            }
            if way.is_empty() {
                way = p;
            } else {
                way.extend(p.into_iter().skip(1));
            }
            match link.get(&(cur, other(free))) {
                Some(&(nxt, at)) if owner[nxt] == usize::MAX => (cur, free) = (nxt, at),
                _ => break,
            }
        }
        ways.push(way);
    }
    (ways, owner)
}

/// A way's points every 4 ft, and its last.
#[must_use]
pub fn sampled(p: &[Pt]) -> Vec<Pt> {
    let mut out = Vec::new();
    for w in p.windows(2) {
        let (a, b) = (w[0], w[1]);
        let n = ((dist(a, b) / 4.0) as usize).max(1);
        out.extend((0..n).map(|k| {
            let f = k as f64 / n as f64;
            (a.0 + (b.0 - a.0) * f, a.1 + (b.1 - a.1) * f)
        }));
    }
    out.push(p[p.len() - 1]);
    out
}

/// Does way `p` (its samples `run`) run beside way `o`, within the shadow, unbroken, for more than a pitch?
#[must_use]
pub fn runs_beside(p: &[Pt], run: &[Pt], o: &[Pt], tests: &mut Counts) -> bool {
    let (near, pitch) = SHADOW;
    let (pb, ob) = (poly_box(p), poly_box(o));
    if o.len() < 2
        || ob.2 < pb.0 - near
        || ob.0 > pb.2 + near
        || ob.3 < pb.1 - near
        || ob.1 > pb.3 + near
    {
        return false;
    }
    tests.add("dist@runs_beside", (run.len() * (o.len() - 1)) as u64);
    let step = length(run) / (run.len().max(2) - 1) as f64;
    let (mut worst, mut cur) = (0usize, 0usize);
    for &q in run {
        let close = o.windows(2).any(|w| seg_dist(q, w[0], w[1]) < near);
        cur = if close { cur + 1 } else { 0 };
        worst = worst.max(cur);
    }
    worst as f64 * step > pitch
}

/// The first other way that way `i` runs beside, or None.
#[must_use]
pub fn shadowed_by(ways: &[Vec<Pt>], i: usize, tests: &mut Counts) -> Option<usize> {
    let p = &ways[i];
    if p.len() < 2 {
        return None;
    }
    let run = sampled(p);
    (0..ways.len()).find(|&j| j != i && runs_beside(p, &run, &ways[j], tests))
}

/// Does the last way run beside another past a pitch, or another beside it?
#[must_use]
pub fn tree_shadows(ways: &[Vec<Pt>], tests: &mut Counts) -> bool {
    let last = ways.len() - 1;
    shadowed_by(ways, last, tests).is_some()
        || (0..last)
            .any(|i| shadowed_by(&[ways[i].clone(), ways[last].clone()], 0, tests).is_some())
}

/// Does the way the last lane is read as - the lanes met end to end joined - run beside another way past a pitch, or another
/// beside it?
#[must_use]
pub fn walked_shadows(lanes: &[Lane], tests: &mut Counts) -> bool {
    let (ways, owner) = as_walked(lanes);
    let k = owner[lanes.len() - 1];
    let mut order: Vec<Vec<Pt>> = ways
        .iter()
        .enumerate()
        .filter(|&(m, _)| m != k)
        .map(|(_, w)| w.clone())
        .collect();
    order.push(ways[k].clone());
    tree_shadows(&order, tests)
}

/// How far `q` lies from the box (0 inside it).
#[must_use]
pub fn box_gap(q: Pt, b: Box4) -> f64 {
    crate::counts::note("dist@box_gap", 1);
    (b.0 - q.0)
        .max(0.0)
        .max(q.0 - b.2)
        .hypot((b.1 - q.1).max(0.0).max(q.1 - b.3))
}

/// Does the end `q` of way `i` touch no other way?
#[must_use]
pub fn free_end(ways: &[Vec<Pt>], i: usize, q: Pt) -> bool {
    crate::counts::note("seg_test@free_end", ways.len().saturating_sub(1) as u64);
    ways.iter()
        .enumerate()
        .filter(|&(k, _)| k != i)
        .all(|(_, o)| {
            o.len() < 2
                || box_gap(q, poly_box(o)) > TOUCH.1
                || o.windows(2)
                    .map(|w| seg_dist(q, w[0], w[1]))
                    .fold(f64::INFINITY, f64::min)
                    > TOUCH.1
        })
}

/// Does the run's last end meet the way `tread` as the law asks: no hook, no needle, no hairpin at the track's start, no fold?
#[must_use]
pub fn meets_clean(run: &[Pt], tread: &[Pt], connector: bool) -> bool {
    let pair = [
        Lane {
            pts: run.to_vec(),
            w: 3.0,
            ..Lane::default()
        },
        Lane {
            pts: tread.to_vec(),
            w: 3.0,
            connector,
            ..Lane::default()
        },
    ];
    let mut open = |_a: Pt, _b: Pt, _w: f64| false;
    !hooked(run).contains(&-1)
        && !needle_ends(&pair, &mut open)
            .iter()
            .any(|n| n.0 == 0 && n.1 == -1)
        && !connector_hairpin_ends(&pair, &mut open)
            .iter()
            .any(|h| h.1 == 0 && h.2 == -1)
        && !folded_joint_pairs(&pair, &mut open)
            .iter()
            .any(|&(i, ei, j, ej)| (i, ei) == (0, -1) || (j, ej) == (0, -1))
}

/// May a short span of tread be laid from `p` to `q`: across no water, no field, dry plot or marsh, no farmhouse, no yard or
/// garden, and not along a way other than the lanes `skip`?
#[must_use]
pub fn span_walkable(
    g: &LawGround,
    ways: &[Vec<Pt>],
    p: Pt,
    q: Pt,
    skip: (usize, usize),
    tests: &mut Counts,
) -> bool {
    let crosses = |course: &[Pt], closed: bool| {
        let n = course.len();
        let legs = if closed { n } else { n.saturating_sub(1) };
        (0..legs).any(|k| segments_cross(p, q, course[k], course[(k + 1) % n]))
    };
    if g.waters.crossed.iter().any(|(c, _)| crosses(c, false))
        || g.open_rings.iter().any(|r| crosses(r, true))
    {
        return false;
    }
    if house_hit(&[p, q], 3.0, &g.houses, tests) {
        return false;
    }
    if g.yards
        .iter()
        .any(|(r, b, _)| crosses_fabric(&[p, q], r, *b, 7.0, tests))
    {
        return false;
    }
    let mid = (f64::midpoint(p.0, q.0), f64::midpoint(p.1, q.1));
    dist(p, q) <= 2.0 * TOUCH.1
        || ways.iter().enumerate().all(|(k, o)| {
            k == skip.0
                || k == skip.1
                || o.len() < 2
                || o.windows(2)
                    .map(|w| seg_dist(mid, w[0], w[1]))
                    .fold(f64::INFINITY, f64::min)
                    > TOUCH.1
        })
}

/// Every free lane end that stops short of a way it is making for - within a join's reach, within the bearing, a walkable span
/// to it that meets the way cleanly and bends no worse - as (lane, end, the point it should meet). A household's way's door end
/// serves its house, and the track out's ends are never joins.
#[must_use]
pub fn near_misses(g: &LawGround, lanes: &[Lane], tests: &mut Counts) -> Vec<(usize, i8, Pt)> {
    let ways: Vec<Vec<Pt>> = lanes.iter().map(|l| l.pts.clone()).collect();
    let (reach, aim, _) = JOIN;
    let mut out = Vec::new();
    for (i, ln) in lanes.iter().enumerate() {
        let p = &ln.pts;
        if ln.connector || p.len() < 2 || length(p) < 1.0 {
            continue;
        }
        for (end, q, b) in [(-1i8, p[p.len() - 1], p[p.len() - 2]), (0, p[0], p[1])] {
            if !free_end(&ways, i, q) || dist(q, b) < 1e-6 || (end == 0 && ln.of.is_some()) {
                continue;
            }
            let head = ((q.0 - b.0) / dist(q, b), (q.1 - b.1) / dist(q, b));
            let mut best: Option<(f64, usize, Pt)> = None;
            for (k, o) in ways
                .iter()
                .enumerate()
                .filter(|&(k, o)| k != i && o.len() >= 2)
            {
                if box_gap(q, poly_box(o)) > reach {
                    continue;
                }
                let f = o
                    .windows(2)
                    .map(|w| foot(q, (w[0], w[1])))
                    .fold(None, |m: Option<Pt>, c| match m {
                        Some(x) if dist(q, x) <= dist(q, c) => Some(x),
                        _ => Some(c),
                    })
                    .unwrap_or(q);
                let d = dist(q, f);
                let ahead =
                    (f.0 - q.0) * head.0 + (f.1 - q.1) * head.1 >= d * aim.to_radians().cos();
                if d <= reach && best.is_none_or(|b| d < b.0) && ahead {
                    best = Some((d, k, f));
                }
            }
            let Some((_, k, f)) =
                best.filter(|&(_, k, f)| span_walkable(g, &ways, q, f, (i, k), tests))
            else {
                continue;
            };
            let mut run: Vec<Pt> = if end == -1 {
                p.clone()
            } else {
                p.iter().rev().copied().collect()
            };
            run.push(f);
            if meets_clean(&run, &ways[k], lanes[k].connector)
                && kink_spans(&run).len() <= kink_spans(p).len()
            {
                out.push((i, end, f));
            }
        }
    }
    out
}

/// The first `n` lanes of the trial web with every end that stops short of a way carried onto it.
#[must_use]
pub fn as_joined(g: &LawGround, trial: &[Lane], n: usize, tests: &mut Counts) -> Vec<Lane> {
    let mut out: Vec<Lane> = trial[..n].to_vec();
    for (i, end, f) in near_misses(g, trial, tests) {
        if i < n {
            if end == -1 {
                out[i].pts.push(f);
            } else {
                out[i].pts.insert(0, f);
            }
        }
    }
    out
}

/// A farmhouse and the built ground of its steading, as an end reaches them.
pub struct Steading {
    /// The house.
    pub house: House,
    /// Its byres, sheds, threshing yard and gardens.
    pub parts: Vec<Vec<Pt>>,
}

fn ring_gap(q: Pt, r: &[Pt]) -> f64 {
    if in_poly(q, r) {
        return 0.0;
    }
    (0..r.len())
        .map(|k| seg_dist(q, r[k], r[(k + 1) % r.len()]))
        .fold(f64::INFINITY, f64::min)
}

/// Does a lane end reach this farmhouse: within its reach of the house's center, or of its steading's built ground?
#[must_use]
pub fn reach_to_steading(end: Pt, s: &Steading) -> bool {
    let (center, built) = STEADING;
    dist(end, s.house.at) <= center
        || ring_gap(end, &s.house.quad) <= built
        || s.parts.iter().any(|r| ring_gap(end, r) <= built)
}

/// How many free lane ends each farmhouse discharges: an end, the track out's aside, touching no other way and reaching its
/// nearest farmhouse.
#[must_use]
pub fn fronting_counts(lanes: &[Lane], steadings: &[Steading]) -> Vec<usize> {
    let ways: Vec<Vec<Pt>> = lanes.iter().map(|l| l.pts.clone()).collect();
    let mut counts = vec![0; steadings.len()];
    if steadings.is_empty() {
        return counts;
    }
    for (i, ln) in lanes
        .iter()
        .enumerate()
        .filter(|(_, l)| !l.connector && l.pts.len() >= 2)
    {
        for end in [ln.pts[0], ln.pts[ln.pts.len() - 1]] {
            if !free_end(&ways, i, end) {
                continue;
            }
            let best = (0..steadings.len())
                .min_by(|&a, &b| {
                    dist(end, steadings[a].house.at).total_cmp(&dist(end, steadings[b].house.at))
                })
                .unwrap_or(0);
            if reach_to_steading(end, &steadings[best]) {
                counts[best] += 1;
            }
        }
    }
    counts
}
