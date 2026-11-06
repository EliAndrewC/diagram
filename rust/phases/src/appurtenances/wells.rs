//! The communal wells' seats (feature 444 T33 D5, D7a, D7b): the households a well owes cut into its groups, each group's seats
//! the gaps between its houses (the cluster form) or the track's verges (the lane-side form), ranked by the neighborhood ladder's
//! rung and then the distance to the group's middle; and a row village's shared wells, a mark at the middle of each stretch of its
//! street, each tried a half and a quarter lot either way, either side of the tread.
//!
//! Research:
//!     wells among the houses - research/questions/0196-communal-wells-ido.drawing.html: seats with a dwelling near and a neighborhood round them
//!     one well to about ten households - research/questions/0196-communal-wells-ido.drawing.html: the five to ten houses each dug well served at Karihama - the households cut into the wells' groups by halving the longer side at its median (`groups`)
//!     the seat between two houses - GUESS: no page says where among the houses a well stands; the middle of the open ground between two of a group's houses, a dwelling's wall on either side
#![expect(
    clippy::cast_precision_loss,
    reason = "counts of a few dozen houses and seats"
)]

use crate::counts::Counts;
use crate::field::fan::Pt;
use crate::field::geom::{dist, seg_dist};

/// A house: its center, its drawn width and depth, and its turn (degrees).
pub type House = (f64, f64, f64, f64, f64);

/// The neighborhood ladder: (how far, how many houses) - a seat's rung the first whose `how many`-th nearest house stands within
/// `how far`.
pub type Rungs<'a> = &'a [(f64, usize)];

/// The point of segment `a`-`b` nearest `p`.
fn closest(p: Pt, a: Pt, b: Pt) -> Pt {
    let (vx, vy) = (b.0 - a.0, b.1 - a.1);
    let l2 = vx * vx + vy * vy;
    let t = if l2 > 0.0 {
        (((p.0 - a.0) * vx + (p.1 - a.1) * vy) / l2).clamp(0.0, 1.0)
    } else {
        0.0
    };
    (a.0 + vx * t, a.1 + vy * t)
}

fn corners(h: House) -> [Pt; 4] {
    let (x, y, w, d, rot) = h;
    let (c, s) = (rot.to_radians().cos(), rot.to_radians().sin());
    [(-w, -d), (w, -d), (w, d), (-w, d)].map(|(u, v)| (x + (u * c - v * s) / 2.0, y + (u * s + v * c) / 2.0))
}

/// The nearest point of house `h`'s wall to `p`.
fn wall_point(h: House, p: Pt) -> Pt {
    let q = corners(h);
    (0..4)
        .map(|k| closest(p, q[k], q[(k + 1) % 4]))
        .min_by(|a, b| dist(*a, p).total_cmp(&dist(*b, p)))
        .unwrap_or((h.0, h.1))
}

/// How far `p` stands from house `h`'s wall: 0 inside it.
fn wall_dist(h: House, p: Pt) -> f64 {
    let q = corners(h);
    if crate::ways::track::in_poly(p, &q) {
        return 0.0;
    }
    (0..4)
        .map(|k| seg_dist(p, q[k], q[(k + 1) % 4]))
        .fold(f64::INFINITY, f64::min)
}

/// The houses `pts` cut into `k` groups: the largest group halved along its longer side at its median, until there are `k` (or
/// none is left to halve). In the order cut, the lower half first.
#[must_use]
pub fn groups(pts: &[Pt], k: usize, tests: &mut Counts) -> Vec<Vec<usize>> {
    let mut gs: Vec<Vec<usize>> = vec![(0..pts.len()).collect()];
    while gs.len() < k {
        let Some((i, _)) = gs
            .iter()
            .enumerate()
            .max_by(|a, b| a.1.len().cmp(&b.1.len()).then(b.0.cmp(&a.0)))
        else {
            break;
        };
        if gs[i].len() < 2 {
            break;
        }
        let mut g = gs.remove(i);
        tests.add("write@well_groups", g.len() as u64);
        let (xs, ys): (Vec<f64>, Vec<f64>) = g.iter().map(|&j| pts[j]).unzip();
        let span = |v: &[f64]| {
            v.iter().copied().fold(f64::NEG_INFINITY, f64::max) - v.iter().copied().fold(f64::INFINITY, f64::min)
        };
        let by_x = span(&xs) >= span(&ys);
        g.sort_by(|&a, &b| {
            let (p, q) = (pts[a], pts[b]);
            if by_x { p.0.total_cmp(&q.0) } else { p.1.total_cmp(&q.1) }.then(a.cmp(&b))
        });
        let hi = g.split_off(g.len() / 2);
        gs.insert(i, hi);
        gs.insert(i, g);
    }
    gs
}

/// A seat's rung on the ladder: the first `(how far, how many)` whose `how many`-th nearest house center stands within `how far`;
/// None where none does.
fn rung(p: Pt, centers: &[Pt], rungs: Rungs, tests: &mut Counts) -> Option<usize> {
    tests.add("dist@well_rung", centers.len() as u64);
    let mut d: Vec<f64> = centers.iter().map(|&c| dist(p, c)).collect();
    d.sort_by(f64::total_cmp);
    rungs
        .iter()
        .position(|&(far, n)| n >= 1 && n <= d.len() && d[n - 1] <= far)
}

fn middle(pts: &[Pt], g: &[usize]) -> Pt {
    let n = g.len().max(1) as f64;
    let (sx, sy) = g.iter().fold((0.0, 0.0), |s, &j| (s.0 + pts[j].0, s.1 + pts[j].1));
    (sx / n, sy / n)
}

/// What the cluster form's seats read: the households the wells serve (their houses), which of them a communal well owes
/// (`needy`), the wells owed, the neighborhood ladder and the seat's gap to a dwelling's wall.
pub struct Cluster<'a> {
    /// The houses the communal wells serve.
    pub houses: &'a [House],
    /// Which of them a communal well owes (the rest watered by open water); all where none is.
    pub needy: &'a [bool],
    /// The wells owed.
    pub want: usize,
    /// The neighborhood ladder.
    pub rungs: Rungs<'a>,
    /// The most a seat may stand from a dwelling's wall (px).
    pub gap: f64,
}

/// The cluster form's seats: for each of `want` groups of the needy households, the middles of the open ground between each pair
/// of its houses whose walls stand within twice the gap, and a step either side across that gap, each within the gap of a
/// dwelling's wall and inside no house, ranked by its rung and then its distance to the group's middle.
///
/// Research:
///     the pair's reach - GUESS: 0196's 80 ft seat doubled, a pair a well may stand between (`WELL_SEAT_FT`)
///     a step either side - GUESS: no page says; a quarter of the gap across the pair's line, so a seat a yard or a bed covers has
///         a neighbor either side
#[must_use]
pub fn cluster_seats(c: &Cluster, tests: &mut Counts) -> Vec<Vec<Pt>> {
    let centers: Vec<Pt> = c.houses.iter().map(|h| (h.0, h.1)).collect();
    let owed: Vec<usize> = (0..c.houses.len()).filter(|&i| c.needy.get(i).copied().unwrap_or(true)).collect();
    let owed = if owed.is_empty() { (0..c.houses.len()).collect() } else { owed };
    let pts: Vec<Pt> = owed.iter().map(|&i| centers[i]).collect();
    groups(&pts, c.want.max(1), tests)
        .into_iter()
        .map(|g| {
            let g: Vec<usize> = g.into_iter().map(|j| owed[j]).collect();
            let mid = middle(&centers, &g);
            let mut seats: Vec<Pt> = Vec::new();
            for (n, &i) in g.iter().enumerate() {
                for &j in &g[n + 1..] {
                    tests.add("candidate@cluster_pairs", 1);
                    let (hi, hj) = (c.houses[i], c.houses[j]);
                    let (p, q) = (wall_point(hi, (hj.0, hj.1)), wall_point(hj, (hi.0, hi.1)));
                    if dist(p, q) > 2.0 * c.gap {
                        continue;
                    }
                    let m = ((p.0 + q.0) / 2.0, (p.1 + q.1) / 2.0);
                    let (ux, uy) = crate::field::geom::unit(p, q);
                    let step = c.gap / 4.0;
                    seats.extend([m, (m.0 - uy * step, m.1 + ux * step), (m.0 + uy * step, m.1 - ux * step)]);
                }
            }
            if g.len() == 1 {
                // ...a group of one house: a step off the middle of each of its walls
                let h = c.houses[g[0]];
                let q = corners(h);
                for k in 0..4 {
                    let (a, b) = (q[k], q[(k + 1) % 4]);
                    let e = ((a.0 + b.0) / 2.0, (a.1 + b.1) / 2.0);
                    let (ux, uy) = crate::field::geom::unit((h.0, h.1), e);
                    seats.push((e.0 + ux * c.gap / 2.0, e.1 + uy * c.gap / 2.0));
                }
            }
            rank(&seats, &centers, c, mid, tests)
        })
        .collect()
}

fn rank(seats: &[Pt], centers: &[Pt], c: &Cluster, mid: Pt, tests: &mut Counts) -> Vec<Pt> {
    let mut kept: Vec<(usize, f64, Pt)> = Vec::new();
    for &p in seats {
        tests.add("dist@cluster_walls", c.houses.len() as u64);
        let walls = c.houses.iter().map(|&h| wall_dist(h, p)).fold(f64::INFINITY, f64::min);
        if walls <= 0.0 || walls > c.gap {
            continue;
        }
        if let Some(r) = rung(p, centers, c.rungs, tests) {
            kept.push((r, dist(p, mid), p));
        }
    }
    kept.sort_by(|a, b| a.0.cmp(&b.0).then(a.1.total_cmp(&b.1)));
    kept.into_iter().map(|k| k.2).collect()
}

/// The lane-side form's seats beside the track out: points along it every `step`, `off` either side of its line, grouped and
/// ranked as the cluster form's are (D7a) - each within the gap of a dwelling's wall, on the ladder's rungs.
///
/// Research:
///     a lane-side well's seat - research/questions/0196-communal-wells-ido.drawing.html: on a lane's verge, clear of the tread
#[must_use]
pub fn verge_seats(c: &Cluster, track: &[Pt], (off, step): (f64, f64), tests: &mut Counts) -> Vec<Vec<Pt>> {
    let centers: Vec<Pt> = c.houses.iter().map(|h| (h.0, h.1)).collect();
    let mut seats: Vec<Pt> = Vec::new();
    for w in track.windows(2) {
        let (a, b) = (w[0], w[1]);
        let n = ((dist(a, b) / step.max(1.0)).floor() as usize).max(1);
        let (ux, uy) = crate::field::geom::unit(a, b);
        for k in 0..n {
            let f = k as f64 / n as f64;
            let p = (a.0 + (b.0 - a.0) * f, a.1 + (b.1 - a.1) * f);
            tests.add("candidate@verge_seats", 2);
            seats.extend([(p.0 - uy * off, p.1 + ux * off), (p.0 + uy * off, p.1 - ux * off)]);
        }
    }
    let owed: Vec<usize> = (0..c.houses.len()).filter(|&i| c.needy.get(i).copied().unwrap_or(true)).collect();
    let owed = if owed.is_empty() { (0..c.houses.len()).collect() } else { owed };
    let pts: Vec<Pt> = owed.iter().map(|&i| centers[i]).collect();
    groups(&pts, c.want.max(1), tests)
        .into_iter()
        .map(|g| {
            let g: Vec<usize> = g.into_iter().map(|j| owed[j]).collect();
            rank(&seats, &centers, c, middle(&centers, &g), tests)
        })
        .collect()
}

/// A row village's street and what its shared wells read: the street, its farms, the widest frame, the watering reach, the
/// offset off the tread, and the bend rule's look and turn.
pub struct RowWells<'a> {
    /// The streets.
    pub streets: &'a [Vec<Pt>],
    /// The farms' centers.
    pub farms: &'a [Pt],
    /// The widest farm frame (px).
    pub frame: f64,
    /// The watering reach (px).
    pub reach: f64,
    /// The seat's offset off the street's line (px).
    pub off: f64,
    /// How far along the street a mark looks for a bend (px), and the turn past which none is dug (degrees).
    pub bend: (f64, f64),
}

fn heading(line: &[Pt], arc: &[f64], at: f64) -> f64 {
    let at = at.clamp(0.0, arc[arc.len() - 1]);
    let k = (0..arc.len() - 1).find(|&j| arc[j + 1] >= at).unwrap_or(arc.len() - 2);
    let (a, b) = (line[k], line[k + 1]);
    (b.1 - a.1).atan2(b.0 - a.0).to_degrees()
}

/// How far the street turns on either side of `u` along it - the larger of its turn from `look` before to `u` and from `u` to
/// `look` after (`wells.street_turns_at`).
fn turns_at(line: &[Pt], arc: &[f64], u: f64, look: f64) -> f64 {
    let between = |p: f64, q: f64| {
        let t = (heading(line, arc, q) - heading(line, arc, p)).abs() % 360.0;
        t.min(360.0 - t)
    };
    between(u - look, u).max(between(u, u + look))
}

/// Each shared well's seats, mark by mark: along each street, the row cut into equal stretches no longer than 1.6 reaches, a mark
/// at each one's middle; each mark tried as it stands, then a half and a quarter lot either way, either side of the tread - never
/// where the street turns past the bend rule's turn (`shared_row_wells`).
///
/// Research:
///     shared wells spaced - research/questions/0033-row-villages-resson.drawing.html: one at the middle of each stretch of at most 1.6 reaches
///     beside the street - research/questions/0196-communal-wells-ido.drawing.html: the lane-side form, on the verge clear of the tread, either side
///     fallback seats along the street - GUESS: a seat tried at the mark, then a half and a quarter lot either way along the street; no page gives the offsets
///     a farm counted to each street within two farmstead frames - GUESS: every street within two frames of it, not only the nearest
#[must_use]
pub fn row_well_seats(r: &RowWells, tests: &mut Counts) -> Vec<Vec<Pt>> {
    let mut out = Vec::new();
    for line in r.streets.iter().filter(|l| l.len() >= 2) {
        let mut arc = vec![0.0];
        for w in line.windows(2) {
            arc.push(arc[arc.len() - 1] + dist(w[0], w[1]));
        }
        let total = arc[arc.len() - 1];
        let mut us: Vec<f64> = Vec::new();
        for &h in r.farms {
            tests.add("dist@row_wells", (line.len() - 1) as u64);
            let (mut best, mut at) = (f64::INFINITY, 0.0);
            for (k, w) in line.windows(2).enumerate() {
                let q = closest(h, w[0], w[1]);
                let d = dist(h, q);
                if d < best {
                    (best, at) = (d, arc[k] + dist(w[0], q));
                }
            }
            if best <= 2.0 * r.frame {
                us.push(at);
            }
        }
        if us.is_empty() {
            continue;
        }
        us.sort_by(f64::total_cmp);
        let (lo, span) = (us[0], us[us.len() - 1] - us[0]);
        let stretches = ((span / (1.6 * r.reach)).ceil() as usize).max(1);
        for j in 0..stretches {
            let u = lo + span * (j as f64 + 0.5) / stretches as f64;
            let mut seats = Vec::new();
            for du in [0.0, r.frame / 2.0, -r.frame / 2.0, r.frame / 4.0, -r.frame / 4.0] {
                let uu = (u + du).clamp(0.0, total);
                if turns_at(line, &arc, uu, r.bend.0) >= r.bend.1 {
                    continue;
                }
                let k = (0..arc.len() - 1).find(|&k| arc[k + 1] >= uu).unwrap_or(arc.len() - 2);
                let (a, b) = (line[k], line[k + 1]);
                let seg = dist(a, b).max(1e-9);
                let f = (uu - arc[k]) / seg;
                let p = (a.0 + (b.0 - a.0) * f, a.1 + (b.1 - a.1) * f);
                let (nx, ny) = (-(b.1 - a.1) / seg, (b.0 - a.0) / seg);
                tests.add("candidate@row_wells", 2);
                seats.extend([(p.0 + nx * r.off, p.1 + ny * r.off), (p.0 - nx * r.off, p.1 - ny * r.off)]);
            }
            out.push(seats);
        }
    }
    out
}
