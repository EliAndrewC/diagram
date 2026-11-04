//! Every crossing square (feature 444 T30): a run squared where it crosses the brook and the drawn channels, as every placer
//! squares the run it lays (`ways/squaring.py` `square_run`, `squared_against`; `ways/checks.py` `square_crossings`), and where a
//! run fails to bend like a path (`ways/clearance.py` `kink_spans`).
//!
//! Research:
//!     squaring plumbing - NONE: each rule is claimed at its function or constant

use super::route::{turn_deg, BENDS};
use super::track::{seg_intersect, segments_cross};
use super::Counts;
use crate::field::fan::Pt;
use crate::field::geom::{dist, seg_dist};

/// How far off square a crossing may be left as drawn (degrees).
///
/// Research:
///     square brook crossing - research/questions/0035-villages-beside-their-stream-one-bank-or-both.drawing.html: within 10 deg
pub const SQUARE_TOL_DEG: f64 = 10.0;

/// How far past the water's half-width the square leg reaches each side (ft): enough that the leg's own points stand outside the
/// elbow pass's reach, so squaring a squared run changes nothing.
///
/// Research:
///     the leg's pad - CONVENTION: 1 ft past the half-width, a drawing convention that keeps the squaring idempotent
pub const LEG_PAD_FT: f64 = 1.0;

/// How many times one run is squared against one water - squaring is idempotent after the first, so this bounds a run that
/// crosses the same course several times.
///
/// Research:
///     its passes - NONE: a bound on an idempotent step - 4
pub const PASSES: usize = 4;

/// The square leg's reach past the water's half-width (ft), what the door adds to each course's half-width.
///
/// Research:
///     the square leg - GUESS: no source could speak to it, a value of ours (feature 417 T29 pass A1, 2026-10-25); 6 ft past the water's half-width
pub const SQUARE_MARGIN_FT: f64 = 6.0;

/// A kink in a run: a turn past a hairpin's at one vertex, or two turns past a zigzag's within its run of path.
#[derive(Debug, PartialEq, Eq)]
pub enum Kink {
    /// A turn past 140 degrees, at its vertex.
    DoublesBack(usize),
    /// Two turns past 50 degrees within 40 ft of path, at their vertices.
    Kinks(usize, usize),
}

/// Where a run fails to bend like a path: each turn past a hairpin's, and each pair of turns past a zigzag's whose summed path
/// between them is a zigzag's run or less.
///
/// Research:
///     no hairpin - research/questions/0081-village-lanes.drawing.html: a turn of more than 140 degrees
///     no zigzag - research/questions/0081-village-lanes.drawing.html: two 50 degree turns within 40 ft of path
#[must_use]
pub fn kink_spans(p: &[Pt]) -> Vec<Kink> {
    let (hairpin, zigzag, run) = BENDS;
    let mut bad = Vec::new();
    let mut turns = Vec::new();
    for k in 1..p.len().saturating_sub(1) {
        if dist(p[k - 1], p[k]) < 1e-6 || dist(p[k], p[k + 1]) < 1e-6 {
            continue;
        }
        let deg = turn_deg(p[k - 1], p[k], p[k + 1]);
        if deg > hairpin {
            bad.push(Kink::DoublesBack(k));
        } else if deg > zigzag {
            turns.push(k);
        }
    }
    for w in turns.windows(2) {
        if (w[0]..w[1]).map(|j| dist(p[j], p[j + 1])).sum::<f64>() <= run {
            bad.push(Kink::Kinks(w[0], w[1]));
        }
    }
    bad
}

/// `pts` with every crossing of `brook` more than the tolerance off square replaced by a leg along the brook's normal at the
/// crossing, `half` and the pad each side; an interior vertex within `half` of the brook dropped first, and a run starting or
/// ending too near the water to hold the leg started or ended on it.
///
/// Research:
///     square brook crossing - research/questions/0035-villages-beside-their-stream-one-bank-or-both.drawing.html
#[expect(
    clippy::many_single_char_names,
    reason = "the plane geometry's own names"
)]
#[must_use]
pub fn square_crossings(pts: &[Pt], brook: &[Pt], half: f64, tests: &mut Counts) -> Vec<Pt> {
    let mut pts = pts.to_vec();
    if pts.len() > 2 && brook.len() > 1 {
        let n = pts.len();
        tests.add(
            "dist@square_crossings",
            ((n - 2) * (brook.len() - 1)) as u64,
        );
        let keep: Vec<Pt> = pts[1..n - 1]
            .iter()
            .copied()
            .filter(|&p| {
                brook
                    .windows(2)
                    .map(|w| seg_dist(p, w[0], w[1]))
                    .fold(f64::INFINITY, f64::min)
                    > half
            })
            .collect();
        pts = [vec![pts[0]], keep, vec![pts[n - 1]]].concat();
    }
    let leg = half + LEG_PAD_FT;
    let mut out: Vec<Pt> = pts.first().copied().into_iter().collect();
    let last = pts.len().saturating_sub(2);
    for (k, w) in pts.windows(2).enumerate() {
        let (a, b) = (w[0], w[1]);
        let seg = dist(a, b);
        let mut legs: Vec<(f64, Pt, Pt)> = Vec::new();
        tests.add("seg_test@square_crossings", (brook.len().max(1) - 1) as u64);
        for c in brook.windows(2) {
            let (c, d) = (c[0], c[1]);
            let cd = dist(c, d);
            // segments that cross are not parallel, so the meeting is found wherever they cross
            let Some(x) = (seg > 0.0 && cd > 0.0 && segments_cross(a, b, c, d))
                .then(|| seg_intersect(a, b, c, d))
                .flatten()
            else {
                continue;
            };
            let (mut nx, mut ny) = (-(d.1 - c.1) / cd, (d.0 - c.0) / cd);
            let (ux, uy) = ((b.0 - a.0) / seg, (b.1 - a.1) / seg);
            let mut dot = ux * nx + uy * ny;
            if dot < 0.0 {
                (nx, ny, dot) = (-nx, -ny, -dot);
            }
            if dot.min(1.0).acos().to_degrees() <= SQUARE_TOL_DEG {
                continue;
            }
            legs.push((
                dist(a, x),
                (x.0 - nx * leg, x.1 - ny * leg),
                (x.0 + nx * leg, x.1 + ny * leg),
            ));
        }
        legs.sort_by(|p, q| p.0.total_cmp(&q.0));
        for (n, &(along, p0, p1)) in legs.iter().enumerate() {
            if k == 0 && n == 0 && along <= leg {
                let i = out.len() - 1;
                out[i] = p0;
            } else {
                out.push(p0);
            }
            out.push(p1);
        }
        if legs.last().is_some_and(|l| k == last && seg - l.0 <= leg) {
            continue;
        }
        out.push(b);
    }
    out
}

/// `q` squared at its crossings of one course, up to the passes - on a leg long enough to read as a bend where the usual one
/// leaves a zigzag.
///
/// Research:
///     square crossing - research/questions/0035-villages-beside-their-stream-one-bank-or-both.drawing.html, research/questions/0084-plank-bridges-over-farm-ditches-itabashi.drawing.html
///     a square leg long enough to bend - research/questions/0081-village-lanes.drawing.html: two turns of more than 50 degrees within 40 ft of path are a zigzag, so the leg runs past 40 ft where the short one leaves one
#[must_use]
pub fn squared_against(q: &[Pt], course: &[Pt], half: f64, tests: &mut Counts) -> Vec<Pt> {
    let squared = |reach: f64, tests: &mut Counts| {
        let mut r = q.to_vec();
        for _ in 0..PASSES {
            let nr = square_crossings(&r, course, reach, tests);
            if nr == r {
                break;
            }
            r = nr;
        }
        r
    };
    let short = squared(half, tests);
    if short == q || kink_spans(&short).len() <= kink_spans(q).len() {
        return short;
    }
    squared(half.max(BENDS.2 / 2.0 + 1.0), tests)
}

/// Do the boxes of two polylines come within `pad` of each other? Two empty ones never do.
#[must_use]
pub fn boxes_meet(a: &[Pt], b: &[Pt], pad: f64) -> bool {
    if a.is_empty() || b.is_empty() {
        return false;
    }
    let (ba, bb) = (super::track::poly_box(a), super::track::poly_box(b));
    !(ba.2 + pad < bb.0 || bb.2 + pad < ba.0 || ba.3 + pad < bb.1 || bb.3 + pad < ba.1)
}

/// A water the door squares a run against: its course and its half-width with the leg's margin.
#[must_use]
pub fn water(course: Vec<Pt>, width: f64) -> (Vec<Pt>, f64) {
    (course, width / 2.0 + SQUARE_MARGIN_FT)
}

/// `run` squared at every crossing of the waters - each a course and its half-width with the leg's margin - out of whose reach
/// the squaring changes nothing.
#[must_use]
pub fn square_run(run: &[Pt], waters: &[(Vec<Pt>, f64)], tests: &mut Counts) -> Vec<Pt> {
    let mut q = run.to_vec();
    for (course, half) in waters {
        if boxes_meet(&q, course, *half) {
            q = squared_against(&q, course, *half, tests);
        }
    }
    q
}
