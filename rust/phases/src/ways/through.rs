//! The connector as drawn (feature 444 T30): the swept track bent round the field and threaded through the steadings; where
//! either cannot make it clean, the flood fill's dry exit from the same gateway - never the track still across the field or a
//! farmstead (`ways/track.py` `connector_through`, `ways/clearance.py` `route_around`, `ways/thread.py` `_thread_the_fabric`
//! and its fallbacks, `ways/geom.py` `push_clear_of_fabric`).
//!
//! Research:
//!     square at the water, as laid - research/questions/0035-villages-beside-their-stream-one-bank-or-both.drawing.html, research/questions/0084-plank-bridges-over-farm-ditches-itabashi.drawing.html: a way crosses the brook or a ditch square, squared where it is laid (`square_run`, feature 417 T49)
//!     connector round the field and the steadings - research/questions/0081-village-lanes.drawing.html, research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: bent and threaded, else the dry exit
//!     never stopping in open country - research/questions/0081-village-lanes.drawing.html: the track out never stops in open country, so a threaded run that no longer reaches its far end, past the frame, takes the dry exit (405 T124)
//!     gives up a wood seat as last resort - GUESS: searched, the record silent (feature 417 T29 pass D, 2026-10-25); the seats the way out crosses are released; the accounts read have a farm's own way in through a gap in its grove, and none covers a through-way taking a household's wood seat
//!     connector's berth off the field - research/questions/0081-village-lanes.drawing.html, research/questions/0014-bunds-between-the-paddies-aze.drawing.html: a lane may touch a plot's boundary and the field path runs onto the outer bund - the track is held 17 ft off the field, a departure the code keeps until feature 417 T32; bent round the field at `SPUR_SETBACK`, 17 ft off its envelope
//!     track round the steadings - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: routed round, else clipped, else none
//!     gap off a grove band - research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.drawing.html: the grove fallback's route and clip keep `CONNECTOR_BAND_GAP_FT` (0036's working room past the connector's half-width, 12.5 ft) off the trees
//!     detour swing - GUESS: no source could speak to it, a value of ours (feature 417 T29 pass D, 2026-10-25); the midpoint swung 40, 80, 140 then 220 px out from the cluster
//!     never across a grove - research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.drawing.html: routed round the bands, else only the part clear of them kept
//!     the track's route walled - research/questions/0081-village-lanes.drawing.html: never across row crops or the flooded paddy, and off wet ground (the field, crop, toe band and wet ground walled - a defense belt's reeds too, since no map draws a causeway: 405 T09)
//!     the track kept off drawn water - research/questions/0035-villages-beside-their-stream-one-bank-or-both.drawing.html: a way crosses water only at a crossing
//!     an end walked clear along its own leg - GUESS: an end standing within the gap of the fabric is pushed out along the run's own first or last leg, so the track still leaves from where it was aimed
//!     the grove fallback's two routes in order - GUESS: each with the toe band and the wet ground walled, round the grown bands and the crop, then the bands alone; the first that crosses no band, nothing held, no steading at a footpath's gap and no more water than the run it replaces is taken
//!     no more crossings than the run it replaces - GUESS: a grove fallback route is taken only where it crosses no more water than the run it replaces; 0035 does not say how many crossings a way may make
//!     the ends drawn in - GUESS: 3 ft at each end, so a fallback whose end stands on the bund or at the field's edge is not read as crossing it; a crossing nearer an end than that goes untested
//!     a track's end out of the grove bands - research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.drawing.html: a lane keeps a footpath's clearance and working room off the trees - the track's end is set only 8 ft clear of a band, a departure the code keeps until feature 417 T32; set 8 ft (`FOOTPATH_FABRIC_GAP` + 1) clear of a grove band
//!     which side it leaves by - GUESS: no source could speak to it, an algorithm's order, breadth or tolerance of ours (feature 417 T29 pass E, 2026-10-25); walked toward the run's other end, or pushed out the nearest edge, whichever lands nearer it
//!     track gateway off the fabric - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: nothing built on a lane, walked out until clear
//!     its search steps and tolerances - GUESS: no source could speak to it, a value of ours (feature 417 T38 pass N4, 2026-10-25) - 24 (step count walking out until clear); 6 (step length of that walk)
#![expect(
    clippy::many_single_char_names,
    reason = "the plane geometry's own names"
)]

use super::dry_exit::{connector_dry_exit, push_out_of, DrySite, BAND_GAP_FT};
use super::route::{clip_to_clear, route, Ask, Crossing, Ground, Grounds};
use super::squaring::square_run;
use super::track::{
    crosses_fabric, edge_dist, grown, in_poly, poly_box, seg_intersect, segments_cross, Box4,
    FABRIC_GAP_FT,
};
use super::Counts;
use crate::field::fan::Pt;
use crate::field::geom::dist;
use crate::law::rules::connector_keeps_the_law;

/// How far outside the field's outline the track is bent round it (ft).
///
/// Research:
///     connector's berth off the field - research/questions/0081-village-lanes.drawing.html, research/questions/0014-bunds-between-the-paddies-aze.drawing.html: 17 ft off its envelope, a departure the code keeps until feature 417 T32
pub const SPUR_SETBACK_FT: f64 = 17.0;

/// A footpath's gap off the fabric (ft).
///
/// Research:
///     a footpath's clearance - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: 7 ft, 0246's fence to a lane's middle (feature 385 T96)
pub const FOOTPATH_GAP_FT: f64 = 7.0;

/// The detour's swings of the midpoint out from the cluster (ft).
///
/// Research:
///     detour swing - GUESS: no source could speak to it, a value of ours (feature 417 T29 pass D, 2026-10-25); 40, 80, 140 then 220
pub const SWINGS: [f64; 4] = [40.0, 80.0, 140.0, 220.0];

/// A drawn way bent out of the ring by walking its outline round the obstruction: where a leg enters at one edge and leaves at
/// another, the outline's vertices between them (the shorter way round) spliced in, each stepped `margin` clear; until no leg
/// crosses, the rounds bounded by the ring's vertex count; None where a leg still crosses after them.
///
/// Research:
///     a track goes round the field - research/questions/0081-village-lanes.drawing.html: never across the crop, the shorter way round its outline
#[must_use]
pub fn route_around(ring: &[Pt], path: &[Pt], margin: f64, tests: &mut Counts) -> Option<Vec<Pt>> {
    let n = ring.len();
    let mut out: Vec<Pt> = path.iter().map(|&q| push_out_of(ring, q, margin)).collect();
    let edge = |k: usize| (ring[k], ring[(k + 1) % n]);
    for _ in 0..n.max(1) {
        let mut redo = Vec::new();
        let mut cut = false;
        for w in out.windows(2) {
            let (a, b) = (w[0], w[1]);
            redo.push(a);
            tests.add("seg_test@route_around", n as u64);
            let mut hits: Vec<(usize, Pt)> = (0..n)
                .filter_map(|k| {
                    let (c, d) = edge(k);
                    segments_cross(a, b, c, d)
                        .then(|| seg_intersect(a, b, c, d))
                        .flatten()
                        .map(|h| (k, h))
                })
                .collect();
            // a leg from outside to outside crosses a closed ring an even number of times; one crossing alone is a leg grazing
            // a vertex, stepped clear at the crossing
            if hits.len() == 1 {
                redo.push(push_out_of(ring, hits[0].1, margin));
                cut = true;
            }
            if hits.len() < 2 {
                continue;
            }
            hits.sort_by(|p, q| dist(p.1, a).total_cmp(&dist(q.1, a)));
            let (k0, k1) = (hits[0].0, hits[hits.len() - 1].0);
            let fwd: Vec<usize> = (0..(k1 + n - k0) % n).map(|t| (k0 + 1 + t) % n).collect();
            let bwd: Vec<usize> = (0..(k0 + n - k1) % n).map(|t| (k0 + n - t) % n).collect();
            let way = if fwd.len() <= bwd.len() { fwd } else { bwd };
            redo.extend(way.iter().map(|&t| push_out_of(ring, ring[t], margin)));
            cut = true;
        }
        redo.push(out[out.len() - 1]);
        out = redo;
        if !cut {
            return Some(out);
        }
    }
    let crosses = out.windows(2).any(|w| {
        (0..n).any(|k| {
            let (c, d) = edge(k);
            segments_cross(w[0], w[1], c, d)
        })
    });
    (!crosses).then_some(out)
}

/// Walk out from `base` along `unit`, starting `edge` out, until the point clears every steading by `gap`; 24 steps of 6 ft,
/// then the point one step past the last tried.
#[must_use]
pub fn push_clear_of_fabric(
    base: Pt,
    unit: Pt,
    mut edge: f64,
    fabric: &[(Vec<Pt>, Box4)],
    gap: f64,
    tests: &mut Counts,
) -> Pt {
    for _ in 0..24 {
        let g = (base.0 + unit.0 * edge, base.1 + unit.1 * edge);
        tests.add("pt_test@push_clear_of_fabric", fabric.len() as u64);
        if !fabric.iter().any(|(ring, b)| {
            b.0 - gap <= g.0
                && g.0 <= b.2 + gap
                && b.1 - gap <= g.1
                && g.1 <= b.3 + gap
                && edge_dist(g, ring) < gap
        }) {
            return g;
        }
        edge += 6.0;
    }
    (base.0 + unit.0 * edge, base.1 + unit.1 * edge)
}

/// `p` set outside the grove bands it stands in: walked toward `toward` until clear by a footpath's gap and a foot, or pushed out
/// past the nearest edge, whichever lands nearer `toward`; a point already outside comes back untouched.
#[must_use]
pub fn out_of_bands(p: Pt, bands: &[Vec<Pt>], toward: Pt) -> Pt {
    if !bands.iter().any(|b| in_poly(p, b)) {
        return p;
    }
    let clear = FOOTPATH_GAP_FT + 1.0;
    let d = dist(p, toward);
    #[expect(
        clippy::cast_possible_truncation,
        clippy::cast_sign_loss,
        reason = "a walk of a few hundred 2 ft steps"
    )]
    let steps = (d / 2.0) as u32;
    let walked = (0..steps)
        .map(|k| {
            let f = 2.0 * f64::from(k) / d;
            (p.0 + (toward.0 - p.0) * f, p.1 + (toward.1 - p.1) * f)
        })
        .find(|&q| {
            !bands
                .iter()
                .any(|b| in_poly(q, b) || edge_dist(q, b) < clear)
        });
    let mut near = p;
    for b in bands {
        if in_poly(near, b) {
            near = push_out_of(b, near, clear);
        }
    }
    match walked {
        Some(w) if dist(w, toward) < dist(near, toward) => w,
        _ => near,
    }
}

/// How many times the polyline crosses the water segments.
#[must_use]
pub fn water_crossings(pts: &[Pt], lines: &[(Pt, Pt)]) -> usize {
    pts.windows(2)
        .map(|w| {
            lines
                .iter()
                .filter(|&&(c, d)| segments_cross(w[0], w[1], c, d))
                .count()
        })
        .sum()
}

/// `run` with each end drawn in 3 ft along its own leg; a leg shorter than twice that kept whole.
#[must_use]
pub fn inner(run: &[Pt]) -> Vec<Pt> {
    let d = 3.0;
    let mut out = run.to_vec();
    let last = out.len() - 1;
    for (i, j) in [(0, 1), (last, last - 1)] {
        let n = dist(out[i], out[j]);
        if n > 2.0 * d {
            out[i] = (
                out[i].0 + (out[j].0 - out[i].0) * d / n,
                out[i].1 + (out[j].1 - out[i].1) * d / n,
            );
        }
    }
    out
}

fn crosses_any(run: &[Pt], polys: &[(Vec<Pt>, Box4)], gap: f64, tests: &mut Counts) -> bool {
    polys
        .iter()
        .any(|(r, b)| crosses_fabric(run, r, *b, gap, tests))
}

fn boxed(polys: &[Vec<Pt>]) -> Vec<(Vec<Pt>, Box4)> {
    polys
        .iter()
        .filter(|p| !p.is_empty())
        .map(|p| (p.clone(), poly_box(p)))
        .collect()
}

/// What the thread reads: the steadings (each marked where it is a grove band), the field and its crop, paddy and wet ground,
/// the water lines and the houses.
pub struct Fabric<'a> {
    /// The homestead polygons, each marked where it is a grove band.
    pub steadings: &'a [(Vec<Pt>, bool)],
    /// The field's envelope.
    pub envelope: &'a [Pt],
    /// The crop polygons.
    pub crops: &'a [Vec<Pt>],
    /// The toe band and the marsh ground.
    pub wet: &'a [Vec<Pt>],
    /// Each field's outline.
    pub paddy: &'a [Vec<Pt>],
    /// The planned watercourses and the drawn channels.
    pub lines: &'a [(Pt, Pt)],
    /// The houses' centers.
    pub houses: &'a [Pt],
    /// The brook's toll, if one is recorded.
    pub crossing: Option<&'a Crossing>,
}

/// The unrouted piece may be drawn: it crosses nothing held and none of the water, each tested with its ends drawn in.
fn unrouted_clear(
    run: &[Pt],
    held: &[(Vec<Pt>, Box4)],
    lines: &[(Pt, Pt)],
    tests: &mut Counts,
) -> bool {
    let i = inner(run);
    !crosses_any(&i, held, 0.0, tests) && water_crossings(&i, lines) == 0
}

/// The track routed round the steadings standing, and clipped where it may not run: routed, else swung out from the cluster,
/// else - across a grove band - routed round the bands, else the part clear of them; nothing where none is clean.
#[must_use]
pub fn thread_the_fabric(f: &Fabric, run: &[Pt], tests: &mut Counts) -> Vec<Pt> {
    let gap = FABRIC_GAP_FT;
    if run.len() < 2 || f.steadings.is_empty() {
        return run.to_vec();
    }
    let rings: Vec<Vec<Pt>> = f
        .steadings
        .iter()
        .map(|(p, band)| {
            if *band {
                grown(p, BAND_GAP_FT - gap)
            } else {
                p.clone()
            }
        })
        .collect();
    let fabric = boxed(&rings);
    let mut obstacles: Vec<Ground> = vec![Ground::plain(f.envelope.to_vec())];
    obstacles.extend(
        f.crops
            .iter()
            .chain(&rings)
            .chain(f.wet)
            .cloned()
            .map(Ground::plain),
    );
    let held = boxed(&[f.paddy, f.crops, f.wet].concat());
    let mut run = run.to_vec();
    let last = run.len() - 1;
    for (i, j) in [(0, 1), (last, last - 1)] {
        let u = (run[j].0 - run[i].0, run[j].1 - run[i].1);
        let n = u.0.hypot(u.1);
        if n > 1e-9 {
            run[i] = push_clear_of_fabric(run[i], (u.0 / n, u.1 / n), 0.0, &fabric, gap, tests);
        }
    }
    let grounds = Grounds {
        hard: &obstacles,
        walls: &[],
        water: f.lines,
    };
    let routed = route(
        run[0],
        run[last],
        &grounds,
        f.crossing,
        Ask::default(),
        tests,
    );
    let routed_ok = routed.len() >= 2;
    let out = clip_to_clear(
        if routed_ok { &routed } else { &run },
        &rings,
        gap,
        &[],
        tests,
    );
    if out.len() >= 2
        && !crosses_any(&out, &fabric, gap, tests)
        && (routed_ok || unrouted_clear(&out, &held, f.lines, tests))
    {
        return out;
    }
    if let Some(d) = swing(f, &run, &rings, &fabric, &held, tests) {
        return d;
    }
    let kept = if out.len() >= 2 {
        out.clone()
    } else {
        run.clone()
    };
    let clean = Clean {
        fabric: &fabric,
        held: &held,
        plain_far: out.len() >= 2 && routed_ok,
    };
    band_fallback(f, &run, &kept, &clean, tests)
}

/// What a fallback is held to: the steadings at the track's gap, the ground held, and whether the far clip is tested without
/// the water (the kept run was routed, and crossed only at the crossing places).
struct Clean<'a> {
    fabric: &'a [(Vec<Pt>, Box4)],
    held: &'a [(Vec<Pt>, Box4)],
    plain_far: bool,
}

/// Across a grove band: the ends walked out of the bands, routed round the grown bands and the crop, then the bands alone, the
/// first that is clean taken; else the part of the kept run clear of them; else nothing.
fn band_fallback(
    f: &Fabric,
    run: &[Pt],
    kept: &[Pt],
    clean: &Clean,
    tests: &mut Counts,
) -> Vec<Pt> {
    let (fabric, held) = (clean.fabric, clean.held);
    let last = run.len() - 1;
    let bands: Vec<Vec<Pt>> = f
        .steadings
        .iter()
        .filter(|s| s.1)
        .map(|s| s.0.clone())
        .collect();
    let band_boxes = boxed(&bands);
    if bands.is_empty() || !crosses_any(kept, &band_boxes, 0.0, tests) {
        return Vec::new();
    }
    let ends = [
        out_of_bands(run[0], &bands, run[last]),
        out_of_bands(run[last], &bands, run[0]),
    ];
    let roomy: Vec<Vec<Pt>> = bands
        .iter()
        .map(|b| grown(b, BAND_GAP_FT - FOOTPATH_GAP_FT))
        .collect();
    for hard in [
        [&roomy[..], f.crops, f.wet].concat(),
        [&roomy[..], f.wet].concat(),
    ] {
        let hard: Vec<Ground> = hard.into_iter().map(Ground::plain).collect();
        let g = Grounds {
            hard: &hard,
            walls: &[],
            water: f.lines,
        };
        let ask = Ask {
            gap: FOOTPATH_GAP_FT,
            ..Ask::default()
        };
        let around = route(ends[0], ends[1], &g, f.crossing, ask, tests);
        if around.len() >= 2
            && !crosses_any(&around, &band_boxes, 0.0, tests)
            && !crosses_any(&inner(&around), held, 0.0, tests)
            && water_crossings(&around, f.lines) <= water_crossings(kept, f.lines)
            && !crosses_any(&around, fabric, FOOTPATH_GAP_FT, tests)
        {
            return around;
        }
    }
    let mut back = kept.to_vec();
    back.reverse();
    let mut far_part = clip_to_clear(&back, &roomy, FOOTPATH_GAP_FT, &[], tests);
    far_part.reverse();
    let lines: &[(Pt, Pt)] = if clean.plain_far { &[] } else { f.lines };
    if far_part.len() >= 2
        && !crosses_any(&far_part, fabric, FOOTPATH_GAP_FT, tests)
        && unrouted_clear(&far_part, held, lines, tests)
    {
        return far_part;
    }
    Vec::new()
}

/// The swing: the run's midpoint pushed out from the cluster's center, 40, 80, 140 then 220 ft, the first detour clear of the
/// fabric, over nothing held and no water.
fn swing(
    f: &Fabric,
    run: &[Pt],
    rings: &[Vec<Pt>],
    fabric: &[(Vec<Pt>, Box4)],
    held: &[(Vec<Pt>, Box4)],
    tests: &mut Counts,
) -> Option<Vec<Pt>> {
    let (a, b) = (run[0], run[run.len() - 1]);
    let m = (f64::midpoint(a.0, b.0), f64::midpoint(a.1, b.1));
    #[expect(clippy::cast_precision_loss, reason = "a household count")]
    let k = f.houses.len().max(1) as f64;
    let c = f
        .houses
        .iter()
        .fold((0.0, 0.0), |s, h| (s.0 + h.0 / k, s.1 + h.1 / k));
    let u = crate::field::geom::unit(c, m);
    SWINGS.iter().find_map(|&step| {
        let detour = [a, (m.0 + u.0 * step, m.1 + u.1 * step), b];
        let cand = clip_to_clear(&detour, rings, FABRIC_GAP_FT, &[], tests);
        if cand.len() < 2 {
            return None;
        }
        let walled =
            crosses_any(&inner(&cand), held, 0.0, tests) || water_crossings(&cand, f.lines) > 0;
        (!walled && !crosses_any(&cand, fabric, FABRIC_GAP_FT, tests)).then_some(cand)
    })
}

/// What the connector's law and its dry exit read beside the fabric: the buildings' boxes, the extents the matrix forbids a way
/// on, the reserved wood seats' walls, the brooks and the waters it is squared against.
pub struct Law<'a> {
    /// The buildings' boxes.
    pub solid: &'a [Box4],
    /// The extents the matrix forbids a way on, the wood seats aside, each with its box.
    pub forbidding: &'a [(Vec<Pt>, Box4)],
    /// The reserved wood seats' walls.
    pub seats: &'a [Vec<Pt>],
    /// The brooks' courses.
    pub brooks: &'a [Vec<Pt>],
    /// The waters a run is squared against: each course and its half-width with the leg's margin.
    pub waters: &'a [(Vec<Pt>, f64)],
}

/// The connector as drawn: the swept track bent round the field and threaded through the steadings, squared and judged; where
/// it is not lawful, the dry exit walled by what the matrix forbids and the wood seats, and only then over a seat, which it takes.
/// The run rounded to the record's 0.1 ft and whether it gave up a seat; None where no dry exit leaves the frame.
#[must_use]
pub fn connector_through(
    track: &[Pt],
    fabric: &Fabric,
    law: &Law,
    dry: &DrySite,
    tests: &mut Counts,
) -> Option<(Vec<Pt>, bool)> {
    let r = |p: Vec<Pt>| {
        p.into_iter()
            .map(|q| ((q.0 * 10.0).round() / 10.0, (q.1 * 10.0).round() / 10.0))
            .collect()
    };
    let around = route_around(fabric.envelope, track, SPUR_SETBACK_FT, tests);
    let mut run = around
        .as_ref()
        .map_or_else(Vec::new, |a| thread_the_fabric(fabric, a, tests));
    if run.len() >= 2
        && around
            .as_ref()
            .is_some_and(|a| dist(run[run.len() - 1], a[a.len() - 1]) > 1.0)
    {
        run.clear();
    }
    if run.len() >= 2 {
        run = square_run(&run, law.waters, tests);
        if connector_keeps_the_law(&run, law.solid, law.forbidding, law.brooks, tests) {
            return Some((r(run), false));
        }
    }
    let matrix: Vec<Vec<Pt>> = law.forbidding.iter().map(|e| e.0.clone()).collect();
    let walled = [dry.avoid, &matrix, law.seats].concat();
    let site = DrySite {
        avoid: &walled,
        ..*dry
    };
    if let Some(p) = connector_dry_exit(&site, track[0], tests) {
        return Some((r(square_run(&p, law.waters, tests)), false));
    }
    let open = [dry.avoid, &matrix].concat();
    let site = DrySite {
        avoid: &open,
        ..*dry
    };
    connector_dry_exit(&site, track[0], tests)
        .map(|p| (r(square_run(&p, law.waters, tests)), !law.seats.is_empty()))
}
