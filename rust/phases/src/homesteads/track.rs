//! The track out (feature 444 T30): the connector from the cluster's gateway past the frame, its bearing swept outward from
//! "away from the field, leaning downslope", alternate sides at growing angles, and the first bearing clean of wet ground, the
//! steadings and the crop, the pond and the water taken; else the least-bad bearing where it is dry and clear of every steading,
//! else the dry exit (`ways/track.py` `connector_track`, `ways/checks.py` `PathChecker`, `ways/fabric.py` `fabric_hits_boxed`).
//!
//! Research:
//!     track out off the wet - research/questions/0081-village-lanes.drawing.html: away from the field leaning downslope, wet ground refused first, run past the frame
//!     wet, then steadings, then crop - research/questions/0081-village-lanes.drawing.html, research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: wet ground and crop refused (0081), no tread on a steading (0246)
//!     the three ranked - NONE: search order; wet and steaded bearings are both refused in the end
//!     track drawn taut - research/questions/0081-village-lanes.drawing.html: every lane pulled taut like a string - the candidate a straight run from the gateway past the frame
//!     track clear of the pond and the brook - research/questions/0035-villages-beside-their-stream-one-bank-or-both.drawing.html: a way crosses the water only at a crossing place, and with none on its line the track leaves on its own bank - the fallback keeps the best bearing even where it crosses, a departure the code keeps until feature 417 T32; the pond, the drain brook and the watercourses scored with the crop, a crossing tolerated only in the fallback

#![expect(
    clippy::many_single_char_names,
    reason = "the plane geometry's own names"
)]

use crate::field::fan::Pt;

/// A pond: its center and half-axes (ft).
pub type Pond = (f64, f64, f64, f64);

/// The water a path is scored against: the pond, the drain brook's segments and the watercourses'.
pub type Water<'a> = (Option<Pond>, &'a [(Pt, Pt)], &'a [(Pt, Pt)]);

/// The ideal bearing's weights: away from the field, and downslope.
///
/// Research:
///     leaning downslope - GUESS: searched, the record silent (feature 417 T29 pass D, 2026-10-25) on the weights - the way out leaves at the water mouth, running with the stream (Wang, Ming-Qing Huizhou, pass D), which the lean follows; the ideal bearing weighs 0.55 away from the field and 0.85 downslope
pub const LEAN: (f64, f64) = (0.55, 0.85);

/// The sweep: its step (degrees) and the steps either side of the ideal bearing.
///
/// Research:
///     its search steps and tolerances - GUESS: no source could speak to it, a value of ours (feature 417 T38 pass N4, 2026-10-25) - 9 (41 bearings at 9 deg steps); 20 (41 bearings at 9 deg steps)
pub const SWEEP: (f64, i32) = (9.0, 20);

/// How far past the canvas edge the track runs (ft).
///
/// Research:
///     track past the frame - CONVENTION: 400 ft past the canvas edge on its own bearing
pub const PAST_FRAME_FT: f64 = 400.0;

/// The track's clearance off a steading (ft).
///
/// Research:
///     track off a steading - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: 7 ft from the track's middle to a garden fence, as every lane
pub const FABRIC_GAP_FT: f64 = 7.0;

/// Wet ground grown by the lane (ft): the web's own bar off wet ground, so the sweep scores the tread the gate measures.
///
/// Research:
///     its unstated figures - GUESS: searched, the record silent (feature 417 T38 pass N4, 2026-10-25) - 8 (wet ground grown 8 ft (`WEB_HARD_GAP` written as a literal))
pub const WET_GROWN_FT: f64 = 8.0;

/// The gateway stepped clear of the crop: its margin, step and tries (ft).
///
/// Research:
///     the gateway off the crop - research/questions/0081-village-lanes.drawing.html, research/questions/0014-bunds-between-the-paddies-aze.drawing.html: a lane may touch a plot's boundary and the field path runs onto the outer bund - the gateway is held 12 ft off the crop, a departure the code keeps until feature 417 T32; stepped 12 ft clear of the crop (`pull_clear(..., 12.0)`), so the track does not start on a paddy's edge
pub const CLEAR_OF_CROP: (f64, f64, usize) = (12.0, 12.0, 24);

/// The water's rules a path keeps: the pond's berth past its larger half-axis, the least crossing angle (degrees), a deck's pad
/// off the crop, and the least distance between two crossings (ft).
///
/// Research:
///     pond kept off - GUESS: searched, the record silent (feature 417 T29 pass A1, 2026-10-25); 80 ft past the pond's larger half-axis
///     square over water - research/questions/0084-plank-bridges-over-farm-ditches-itabashi.drawing.html: no crossing under 42 degrees
///     no deck on crop - research/questions/0084-plank-bridges-over-farm-ditches-itabashi.drawing.html: the lanes among the houses cross a ditch where their line takes them, a crossing landing on cultivated ground, wet or dry - a deck landing on crop is refused, a departure the code keeps until feature 417 T32; a crossing within 14 ft of a crop fouls
///     two decks too close - CONVENTION: crossings under 46 ft apart counted
pub const WATER_RULES: (f64, f64, f64, f64) = (80.0, 42.0, 14.0, 46.0);

/// A polygon sampled along a segment: one sample every 8 ft, at most 900.
///
/// Research:
///     its search steps and tolerances - GUESS: no source could speak to it, a value of ours (feature 417 T38 pass N11, 2026-10-25) - 8 (sampling step); 900 (sample cap)
pub const SAMPLING: (f64, usize) = (8.0, 900);

/// A box (x0, y0, x1, y1).
pub type Box4 = (f64, f64, f64, f64);

/// Is `p` inside the ring (even-odd, the engine's own epsilon on the edge's rise)?
#[must_use]
pub fn in_poly(p: Pt, ring: &[Pt]) -> bool {
    let n = ring.len();
    let mut odd = false;
    let mut j = n.wrapping_sub(1);
    for i in 0..n {
        let (a, b) = (ring[i], ring[j]);
        if (a.1 > p.1) != (b.1 > p.1) && p.0 < (b.0 - a.0) * (p.1 - a.1) / (b.1 - a.1 + 1e-9) + a.0
        {
            odd = !odd;
        }
        j = i;
    }
    odd
}

/// The distance from `p` to the segment `a`-`b`.
#[must_use]
pub fn seg_dist(p: Pt, a: Pt, b: Pt) -> f64 {
    crate::field::geom::seg_dist(p, a, b)
}

/// Do the segments `a`-`b` and `c`-`d` cross (strictly, the engine's own orientation test)?
#[must_use]
pub fn segments_cross(a: Pt, b: Pt, c: Pt, d: Pt) -> bool {
    let ccw = |p: Pt, q: Pt, r: Pt| (r.1 - p.1) * (q.0 - p.0) > (q.1 - p.1) * (r.0 - p.0);
    ccw(a, c, d) != ccw(b, c, d) && ccw(a, b, c) != ccw(a, b, d)
}

/// Where the segments `a`-`b` and `c`-`d` meet, bounded on both.
#[must_use]
pub fn seg_intersect(a: Pt, b: Pt, c: Pt, d: Pt) -> Option<Pt> {
    let den = (a.0 - b.0) * (c.1 - d.1) - (a.1 - b.1) * (c.0 - d.0);
    if den.abs() < 1e-9 {
        return None;
    }
    let t = ((a.0 - c.0) * (c.1 - d.1) - (a.1 - c.1) * (c.0 - d.0)) / den;
    let u = -((a.0 - b.0) * (a.1 - c.1) - (a.1 - b.1) * (a.0 - c.0)) / den;
    ((0.0..=1.0).contains(&t) && (0.0..=1.0).contains(&u))
        .then_some((a.0 + t * (b.0 - a.0), a.1 + t * (b.1 - a.1)))
}

/// The least distance from `p` to the ring's edges.
#[must_use]
pub fn edge_dist(p: Pt, ring: &[Pt]) -> f64 {
    (0..ring.len())
        .map(|i| seg_dist(p, ring[i], ring[(i + 1) % ring.len()]))
        .fold(f64::INFINITY, f64::min)
}

/// Does the segment `a`-`b` pass through the ring: an edge crossed, or a sample along it inside?
#[expect(
    clippy::cast_possible_truncation,
    clippy::cast_sign_loss,
    clippy::cast_precision_loss,
    reason = "a sample count of at most 900"
)]
#[must_use]
pub fn crosses_poly(a: Pt, b: Pt, ring: &[Pt], tests: &mut u64) -> bool {
    let n = ring.len();
    *tests += n as u64;
    if (0..n).any(|i| segments_cross(a, b, ring[i], ring[(i + 1) % n])) {
        return true;
    }
    let (step, cap) = SAMPLING;
    let k = ((((b.0 - a.0).hypot(b.1 - a.1)) / step) as usize).clamp(2, cap);
    *tests += (k + 1) as u64;
    (0..=k).any(|i| {
        let f = i as f64 / k as f64;
        in_poly((a.0 + (b.0 - a.0) * f, a.1 + (b.1 - a.1) * f), ring)
    })
}

/// Does the segment `a`-`b` cross the water segment `p`-`q` at under the least angle?
#[must_use]
pub fn shallow_crossing(a: Pt, b: Pt, p: Pt, q: Pt) -> bool {
    if seg_intersect(a, b, p, q).is_none() {
        return false;
    }
    let (u, v) = (
        crate::field::geom::unit(a, b),
        crate::field::geom::unit(p, q),
    );
    (u.0 * v.1 - u.1 * v.0)
        .clamp(-1.0, 1.0)
        .asin()
        .to_degrees()
        .abs()
        < WATER_RULES.1
}

/// Does the crossing of `a`-`b` over `p`-`q` land on or within the pad of a crop?
#[must_use]
pub fn crossing_lands_on_crop(a: Pt, b: Pt, p: Pt, q: Pt, crops: &[&[Pt]]) -> bool {
    seg_intersect(a, b, p, q).is_some_and(|hit| {
        crops
            .iter()
            .any(|c| in_poly(hit, c) || edge_dist(hit, c) < WATER_RULES.2)
    })
}

#[expect(
    clippy::cast_possible_truncation,
    reason = "cell indices of a few hundred"
)]
fn cell(v: f64, size: f64) -> i64 {
    (v / size).floor() as i64
}

/// How many pairs of points lie within `reach` of each other, by cells of side `reach`.
#[must_use]
pub fn pairs_within(points: &[Pt], reach: f64, tests: &mut u64) -> u64 {
    if reach <= 0.0 || points.len() < 2 {
        return 0;
    }
    let mut cells: std::collections::BTreeMap<(i64, i64), Vec<Pt>> =
        std::collections::BTreeMap::new();
    for &p in points {
        cells
            .entry((cell(p.0, reach), cell(p.1, reach)))
            .or_default()
            .push(p);
    }
    let near = |u: Pt, v: Pt, tests: &mut u64| {
        *tests += 1;
        u64::from((u.0 - v.0).hypot(u.1 - v.1) < reach)
    };
    let mut count = 0;
    for (&(cx, cy), mine) in &cells {
        for (i, &u) in mine.iter().enumerate() {
            for &v in &mine[i + 1..] {
                count += near(u, v, tests);
            }
        }
        for (dx, dy) in [(1, -1), (1, 0), (1, 1), (0, 1)] {
            for &v in cells
                .get(&(cx + dx, cy + dy))
                .map_or(&[][..], Vec::as_slice)
            {
                for &u in mine {
                    count += near(u, v, tests);
                }
            }
        }
    }
    count
}

/// A ring's box.
#[must_use]
pub fn poly_box(ring: &[Pt]) -> Box4 {
    ring.iter().fold(
        (
            f64::INFINITY,
            f64::INFINITY,
            f64::NEG_INFINITY,
            f64::NEG_INFINITY,
        ),
        |b, p| (b.0.min(p.0), b.1.min(p.1), b.2.max(p.0), b.3.max(p.1)),
    )
}

fn boxes_meet(a: Box4, b: Box4) -> bool {
    !(a.2 < b.0 || a.0 > b.2 || a.3 < b.1 || a.1 > b.3)
}

fn seg_box(a: Pt, b: Pt, pad: f64) -> Box4 {
    (
        a.0.min(b.0) - pad,
        a.1.min(b.1) - pad,
        a.0.max(b.0) + pad,
        a.1.max(b.1) + pad,
    )
}

/// Does the run pass within `gap` of the ring: an edge crossed, a corner of either near the other, or a leg's end inside it?
#[must_use]
pub fn crosses_fabric(run: &[Pt], ring: &[Pt], rb: Box4, gap: f64, tests: &mut u64) -> bool {
    run.windows(2).any(|w| {
        let (a, b) = (w[0], w[1]);
        if !boxes_meet(seg_box(a, b, gap), rb) {
            return false;
        }
        *tests += 2 * ring.len() as u64 + 2;
        (0..ring.len()).any(|j| {
            let (c, d) = (ring[j], ring[(j + 1) % ring.len()]);
            segments_cross(a, b, c, d) || seg_dist(c, a, b) < gap
        }) || edge_dist(a, ring) < gap
            || edge_dist(b, ring) < gap
            || in_poly(a, ring)
            || in_poly(b, ring)
    })
}

/// How many of the steadings the run fouls within `gap`, each skipped whose box, widened by `gap`, misses the run's.
#[must_use]
pub fn fabric_hits(run: &[Pt], fabric: &[(Vec<Pt>, Box4)], gap: f64, tests: &mut u64) -> usize {
    let rb = poly_box(run);
    let rb = (rb.0 - gap, rb.1 - gap, rb.2 + gap, rb.3 + gap);
    fabric
        .iter()
        .filter(|(ring, b)| {
            *tests += 1;
            boxes_meet(*b, rb) && crosses_fabric(run, ring, *b, gap, tests)
        })
        .count()
}

/// How far along `theta` (radians) from `start` the track runs: to where it leaves the `w` x `h` canvas, and past it.
#[must_use]
pub fn past_the_frame(start: Pt, theta: f64, w: f64, h: f64) -> f64 {
    let (c, s) = (theta.cos(), theta.sin());
    let exit = |lim: f64, at: f64, v: f64| {
        if v > 1e-12 {
            (lim - at) / v
        } else if v < -1e-12 {
            -at / v
        } else {
            f64::INFINITY
        }
    };
    [exit(w, start.0, c), exit(h, start.1, s)]
        .into_iter()
        .filter(|t| (0.0..f64::INFINITY).contains(t))
        .fold(None, |m: Option<f64>, t| Some(m.map_or(t, |m| m.min(t))))
        .unwrap_or(0.0)
        + PAST_FRAME_FT
}

/// A ring grown `out` along its own outward normals, mitered (the miter capped at 4x): the outer ring of `ring_offset`.
#[must_use]
pub fn grown(ring: &[Pt], out: f64) -> Vec<Pt> {
    let n = ring.len();
    let ccw = crate::field::geom::signed_area(ring) > 0.0;
    let normal = |a: Pt, b: Pt| {
        let (ex, ey) = (b.0 - a.0, b.1 - a.1);
        let l = ex.hypot(ey);
        let l = if l == 0.0 { 1.0 } else { l };
        if ccw {
            (ey / l, -ex / l)
        } else {
            (-ey / l, ex / l)
        }
    };
    (0..n)
        .map(|i| {
            let (a, b, c) = (ring[(i + n - 1) % n], ring[i], ring[(i + 1) % n]);
            let (n1, n2) = (normal(a, b), normal(b, c));
            let (mut mx, mut my) = (n1.0 + n2.0, n1.1 + n2.1);
            let mut ml = mx.hypot(my);
            if ml < 1e-9 {
                (mx, my, ml) = (n1.0, n1.1, 1.0);
            }
            (mx, my) = (mx / ml, my / ml);
            let scale = 1.0 / (mx * n1.0 + my * n1.1).max(0.25);
            (b.0 + mx * out * scale, b.1 + my * out * scale)
        })
        .collect()
}

/// The gateway stepped toward `toward` until it stands clear of every obstacle by the margin, or the tries run out.
#[must_use]
pub fn pull_clear(pt: Pt, toward: Pt, obstacles: &[&[Pt]], tests: &mut u64) -> Pt {
    let (margin, step, tries) = CLEAR_OF_CROP;
    let mut p = pt;
    for _ in 0..tries {
        *tests += obstacles.len() as u64;
        if !obstacles
            .iter()
            .any(|o| in_poly(p, o) || edge_dist(p, o) < margin)
        {
            return p;
        }
        let u = crate::field::geom::unit(p, toward);
        p = (p.0 + u.0 * step, p.1 + u.1 * step);
    }
    p
}

/// The crop, the pond and the water a path is scored against, each item with its box.
pub struct Checker {
    avoid: Vec<(Vec<Pt>, Box4)>,
    pond: Option<Pond>,
    brook: Vec<(Pt, Pt)>,
    waters: Vec<(Pt, Pt)>,
}

impl Checker {
    /// A checker over the crop polygons (each of three corners or more), the pond (center and half-axes), the brook and the
    /// watercourses.
    #[must_use]
    pub fn new(
        avoid: &[Vec<Pt>],
        pond: Option<Pond>,
        brook: &[(Pt, Pt)],
        waters: &[(Pt, Pt)],
    ) -> Self {
        Self {
            avoid: avoid
                .iter()
                .filter(|p| p.len() >= 3)
                .map(|p| (p.clone(), poly_box(p)))
                .collect(),
            pond,
            brook: brook.to_vec(),
            waters: waters.to_vec(),
        }
    }

    /// How many of the path's segments foul the crop, the pond, the brook or the water, and how many pairs of its crossings
    /// stand too close (0 = clear).
    #[must_use]
    pub fn violations(&self, path: &[Pt], tests: &mut u64) -> u64 {
        let (berth, _, pad, apart) = WATER_RULES;
        let mut bad = 0;
        let mut hits = Vec::new();
        for w in path.windows(2) {
            let (a, b) = (w[0], w[1]);
            let bx = seg_box(a, b, 0.0);
            *tests += (self.avoid.len() + self.brook.len() + 2 * self.waters.len()) as u64;
            let meets = |s: &(Pt, Pt)| boxes_meet(bx, seg_box(s.0, s.1, 0.0));
            let waters: Vec<&(Pt, Pt)> = self.waters.iter().filter(|s| meets(s)).collect();
            let landing: Vec<&[Pt]> = self
                .avoid
                .iter()
                .filter(|(_, pb)| boxes_meet(seg_box(a, b, pad), *pb))
                .map(|(p, _)| p.as_slice())
                .collect();
            let foul = self
                .pond
                .is_some_and(|(cx, cy, rx, ry)| seg_dist((cx, cy), a, b) < rx.max(ry) + berth)
                || self
                    .brook
                    .iter()
                    .filter(|s| meets(s))
                    .any(|&(p, q)| seg_intersect(a, b, p, q).is_some())
                || self
                    .avoid
                    .iter()
                    .filter(|(_, pb)| boxes_meet(bx, *pb))
                    .any(|(p, _)| crosses_poly(a, b, p, tests))
                || waters.iter().any(|&&(p, q)| shallow_crossing(a, b, p, q))
                || waters
                    .iter()
                    .any(|&&(p, q)| crossing_lands_on_crop(a, b, p, q, &landing));
            bad += u64::from(foul);
            hits.extend(
                waters
                    .iter()
                    .filter_map(|&&(p, q)| seg_intersect(a, b, p, q)),
            );
        }
        bad + pairs_within(&hits, apart, tests)
    }
}

/// What the sweep found: a clean bearing's path, the least-bad bearing's where it is dry and clear of every steading, or none.
#[derive(Debug, PartialEq)]
pub enum Swept {
    /// A bearing clean of everything.
    Clean(Vec<Pt>),
    /// The least-bad bearing, dry and clear of the steadings; `route_around` bends it round the crop.
    Least(Vec<Pt>),
    /// No bearing dry and clear of the steadings: the dry exit's flood fill finds the way out.
    DryExit,
}

/// What the sweep reads: the gateway's ground and the map's.
pub struct TrackSite<'a> {
    /// The field's way out (the seat's `out`) and the fall.
    pub lean: (Pt, Pt),
    /// The cluster's seat, the gateway is pulled toward.
    pub seat: Pt,
    /// The crop polygons (the field's envelope where none).
    pub avoid: &'a [Vec<Pt>],
    /// The wet polygons.
    pub wet: &'a [Vec<Pt>],
    /// The steadings.
    pub fabric: &'a [Vec<Pt>],
    /// The pond (center and half-axes), the drain brook's segments and the watercourses' (planned and drawn).
    pub water: Water<'a>,
    /// The canvas (ft).
    pub canvas: Pt,
}

/// The track out from `start`: the gateway stepped clear of the crop, then the bearings swept nearest the ideal first, ranked by
/// wet ground, then steadings, then crop and water; the start it was drawn from beside what it found.
#[must_use]
pub fn connector(site: &TrackSite, start: Pt, tests: &mut u64) -> (Pt, Swept) {
    let ((ox, oy), (fx, fy)) = site.lean;
    let base = (LEAN.0 * oy + LEAN.1 * fy)
        .atan2(LEAN.0 * ox + LEAN.1 * fx)
        .to_degrees();
    let crops: Vec<&[Pt]> = site.avoid.iter().map(Vec::as_slice).collect();
    let start = pull_clear(start, site.seat, &crops, tests);
    let wet: Vec<Checker> = site
        .wet
        .iter()
        .filter(|w| w.len() >= 3)
        .map(|w| Checker::new(&[grown(w, WET_GROWN_FT)], None, &[], &[]))
        .collect();
    let (pond, brook, waters) = site.water;
    let ground = Checker::new(site.avoid, pond, brook, waters);
    let fabric: Vec<(Vec<Pt>, Box4)> = site
        .fabric
        .iter()
        .map(|p| (p.clone(), poly_box(p)))
        .collect();
    let (step, steps) = SWEEP;
    let mut swings: Vec<i32> = (-steps..=steps).collect();
    swings.sort_by_key(|k| k.abs());
    let mut best: Option<((u64, usize, u64), Vec<Pt>)> = None;
    for k in swings {
        *tests += 1;
        let theta = (base + step * f64::from(k)).to_radians();
        let far = past_the_frame(start, theta, site.canvas.0, site.canvas.1);
        let path = vec![
            start,
            (start.0 + theta.cos() * far, start.1 + theta.sin() * far),
        ];
        let soaked: u64 = wet.iter().map(|c| c.violations(&path, tests)).sum();
        let steaded = fabric_hits(&path, &fabric, FABRIC_GAP_FT, tests);
        if best
            .as_ref()
            .is_some_and(|(r, _)| (soaked, steaded) > (r.0, r.1))
        {
            continue;
        }
        let fouls = ground.violations(&path, tests);
        if (soaked, steaded, fouls) == (0, 0, 0) {
            return (start, Swept::Clean(path));
        }
        if best
            .as_ref()
            .is_none_or(|(r, _)| (soaked, steaded, fouls) < *r)
        {
            best = Some(((soaked, steaded, fouls), path));
        }
    }
    match best {
        Some(((0, 0, _), path)) => (start, Swept::Least(path)),
        _ => (start, Swept::DryExit),
    }
}
