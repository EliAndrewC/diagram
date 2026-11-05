//! The track stage (feature 444 T32): a row village's road - its first street's drawn span run on off the sheet at both ends
//! along each end's last leg, each run over the brook at the ford that makes the walk shortest, threaded through the steadings
//! and squared where it crosses water (`ways/track.py` `stage_track`; `ways/street.py` `drawn_span`, `street_span`,
//! `brook_bounds`, `row_reach`, `street_runs_out`, `run_to_edge`; `ways/checks.py` `ford_crossing`, `ford_leg`;
//! `ways/track.py` `thread_over_the_ford`). Every other form draws the track out the homesteads chose (`way_out_track`).
//!
//! Research:
//!     street runs on off the map - research/questions/0033-row-villages-resson.drawing.html: the street runs on off the map as the road into it; it stands for the road the row stands on
//!     street spans its farms - research/questions/0033-row-villages-resson.drawing.html, research/questions/0031-clustered-and-scattered-villages-shuson-sanson.drawing.html: from its first farm to its last, plus the run past them
//!     square at the ford - research/questions/0035-villages-beside-their-stream-one-bank-or-both.drawing.html: the ford that makes the walk shortest, landings square to the reach
//!     square at the water, as laid - research/questions/0035-villages-beside-their-stream-one-bank-or-both.drawing.html, research/questions/0084-plank-bridges-over-farm-ditches-itabashi.drawing.html: a way crosses the brook or a ditch square
//!     street end short of the brook - research/questions/0035-villages-beside-their-stream-one-bank-or-both.drawing.html: a way crosses the water only at one of its crossing places; the street stops short of the crossing

pub mod py;
#[cfg(test)]
mod tests;

use crate::counts::Counts;
use crate::field::fan::Pt;
use crate::field::geom::{dist, seg_dist};
use crate::law::ground::BoxGrid;
use crate::law::rules::crossing_points;
use crate::ways::squaring::square_run;
use crate::ways::through::{thread_the_fabric, Fabric};

/// How far the road is carried past the sheet's edge (ft).
///
/// Research:
///     its drawn sizes - CONVENTION: sizes on the sheet, not in the world - 60 (run carried past the sheet's edge)
pub const BEYOND_FT: f64 = 60.0;

/// A ford's landing off the brook, square to its reach (ft).
///
/// Research:
///     street end's stand-off - GUESS: `FORD_LANDING_FT` (22 ft) short of the crossing, a stand-off of ours; 0035, which gives the crossing places, is silent on the distance (searched, feature 417 T29 pass D)
pub const FORD_LANDING_FT: f64 = 22.0;

/// The street's vertices kept no nearer than this along it (ft).
///
/// Research:
///     its search steps and tolerances - GUESS: no source could speak to it, a value of ours - 40 (the drawn street's vertex step)
pub const VERTEX_FT: f64 = 40.0;

/// A row farm's frame where none is recorded (ft).
///
/// Research:
///     a farm frame where none is recorded - research/questions/0033-row-villages-resson.drawing.html: a row village's holding 220 to 260 ft, drawn at its middle
pub const ROW_FRAME_FT: f64 = 240.0;

/// How far off a street a farm may stand and still be its own, and how far the street runs past its end farms, in frames.
///
/// Research:
///     a farm's own street - GUESS: no source could speak to it, a value of ours (feature 417 T29 pass B, 2026-10-25); a farm within 1.5 frames of the street is its own
///     street run past its end farms - GUESS: searched, the record silent (feature 417 T29 pass B, 2026-10-25); half a frame past the end farms at both ends of the span
pub const ROW_REACH_FRAMES: (f64, f64) = (1.5, 0.5);

/// The nearest point of the segment a-b to `p`.
fn closest(p: Pt, a: Pt, b: Pt) -> Pt {
    let (vx, vy) = (b.0 - a.0, b.1 - a.1);
    let len2 = vx * vx + vy * vy;
    let t = if len2 > 0.0 {
        (((p.0 - a.0) * vx + (p.1 - a.1) * vy) / len2).clamp(0.0, 1.0)
    } else {
        0.0
    };
    (a.0 + vx * t, a.1 + vy * t)
}

/// How far off a planned street a farm may stand and still be its own, and how far the street runs past its end farms: from
/// the widest farm's frame (each frame's longer side), else `ROW_FRAME_FT`.
#[must_use]
pub fn row_reach(frames: &[f64]) -> (f64, f64) {
    let fw = frames
        .iter()
        .copied()
        .reduce(f64::max)
        .unwrap_or(ROW_FRAME_FT);
    (ROW_REACH_FRAMES.0 * fw, ROW_REACH_FRAMES.1 * fw)
}

/// `lo` and `hi` (arc lengths along `line`, cumulative `arc`) drawn in to `FORD_LANDING_FT` short of the nearest crossing of
/// `brook` beyond the end farms' projections `first` and `last` - never past those projections themselves.
#[must_use]
pub fn brook_bounds(
    line: &[Pt],
    arc: &[f64],
    (first, last): (f64, f64),
    (mut lo, mut hi): (f64, f64),
    brook: &[Pt],
    tests: &mut Counts,
) -> (f64, f64) {
    if brook.len() < 2 || line.len() < 2 {
        return (lo, hi);
    }
    let at: Vec<f64> = crossing_points(line, brook, tests)
        .into_iter()
        .map(|(k, x)| arc[k] + dist(line[k], x))
        .collect();
    let beyond = at.iter().copied().filter(|&u| u >= last).reduce(f64::min);
    if let Some(b) = beyond {
        hi = last.max(hi.min(b - FORD_LANDING_FT));
    }
    let before = at.iter().copied().filter(|&u| u <= first).reduce(f64::max);
    if let Some(b) = before {
        lo = first.min(lo.max(b + FORD_LANDING_FT));
    }
    (lo, hi)
}

/// The stretch of a planned street its farms stand along: from the first farm's projection less `pad` to the last's plus
/// `pad`, over the farms within `reach` of the line, stopped short of the brook past its end farms; empty when no farm is. The
/// line's own vertices are kept, thinned to `VERTEX_FT`, its last kept.
#[must_use]
pub fn street_span(
    line: &[Pt],
    farms: &[Pt],
    (reach, pad): (f64, f64),
    brook: &[Pt],
    tests: &mut Counts,
) -> Vec<Pt> {
    if line.len() < 2 {
        return Vec::new();
    }
    let mut arc = vec![0.0];
    for w in line.windows(2) {
        arc.push(arc[arc.len() - 1] + dist(w[0], w[1]));
    }
    // ...each farm asks only the segments whose boxes come within its reach (a segment nearer than the reach has one)
    let grid = BoxGrid::new(line.windows(2).map(|w| {
        (
            w[0].0.min(w[1].0),
            w[0].1.min(w[1].1),
            w[0].0.max(w[1].0),
            w[0].1.max(w[1].1),
        )
    }));
    let mut along = Vec::new();
    for &h in farms {
        // the nearest segment, the lower index on a tie
        let near = grid.near((h.0 - reach, h.1 - reach, h.0 + reach, h.1 + reach));
        tests.add("dist@street_span", near.len() as u64 + 1);
        let mut best = (f64::INFINITY, 0usize);
        for i in near {
            let d = seg_dist(h, line[i], line[i + 1]);
            if d < best.0 {
                best = (d, i);
            }
        }
        if best.0 > reach {
            continue;
        }
        let i = best.1;
        along.push(arc[i] + dist(line[i], closest(h, line[i], line[i + 1])));
    }
    let (Some(first), Some(last)) = (
        along.iter().copied().reduce(f64::min),
        along.iter().copied().reduce(f64::max),
    ) else {
        return Vec::new();
    };
    let total = arc[arc.len() - 1];
    let (lo, hi) = brook_bounds(
        line,
        &arc,
        (first, last),
        ((first - pad).max(0.0), total.min(last + pad)),
        brook,
        tests,
    );
    let idx: Vec<usize> = (0..arc.len())
        .filter(|&i| lo <= arc[i] && arc[i] <= hi)
        .collect();
    let mut kept: Vec<usize> = Vec::new();
    for &i in &idx {
        if kept.last().is_none_or(|&k| arc[i] - arc[k] >= VERTEX_FT) {
            kept.push(i);
        }
    }
    // ...the stretch ends where its last farm does, not at the last whole vertex step
    if let Some(&l) = idx.last().filter(|&&l| kept.last() != Some(&l)) {
        kept.push(l);
    }
    kept.into_iter().map(|i| line[i]).collect()
}

/// How far `end` stands from the sheet's edge straight on along the leg from `prev`, and that run carried `BEYOND_FT` past it.
#[must_use]
pub fn run_to_edge(end: Pt, prev: Pt, sheet: Pt) -> (f64, Vec<Pt>) {
    let (dx, dy) = (end.0 - prev.0, end.1 - prev.1);
    let m = dx.hypot(dy);
    let m = if m == 0.0 { 1.0 } else { m };
    let (ux, uy) = (dx / m, dy / m);
    let tx = if ux < 0.0 {
        -end.0 / ux
    } else if ux > 0.0 {
        (sheet.0 - end.0) / ux
    } else {
        f64::INFINITY
    };
    let ty = if uy < 0.0 {
        -end.1 / uy
    } else if uy > 0.0 {
        (sheet.1 - end.1) / uy
    } else {
        f64::INFINITY
    };
    let t = tx.min(ty).max(0.0);
    (
        t,
        vec![
            end,
            (end.0 + ux * (t + BEYOND_FT), end.1 + uy * (t + BEYOND_FT)),
        ],
    )
}

/// The run off the sheet from each end of a street, its first end's then its last's, each along that end's last leg (the 9th
/// point in, or the street's other end where it is shorter).
#[must_use]
pub fn street_runs_out(street: &[Pt], sheet: Pt) -> [(f64, Vec<Pt>); 2] {
    let n = street.len();
    [
        run_to_edge(street[0], street[8.min(n - 1)], sheet),
        run_to_edge(street[n - 1], street[n - 9.min(n)], sheet),
    ]
}

/// The two landings of a square crossing at the ford that makes start -> ford -> end shortest, ordered from the start's bank;
/// none where the straight run does not cross the brook or there is no ford.
#[must_use]
pub fn ford_crossing(
    start: Pt,
    end: Pt,
    brook: &[Pt],
    fords: &[Pt],
    tests: &mut Counts,
) -> Vec<Pt> {
    if fords.is_empty()
        || brook.len() < 2
        || crossing_points(&[start, end], brook, tests).is_empty()
    {
        return Vec::new();
    }
    let walk = |c: Pt| dist(start, c) + dist(c, end);
    let mut f = fords[0];
    for &c in &fords[1..] {
        if walk(c) < walk(f) {
            f = c;
        }
    }
    tests.add(
        "dist@ford_crossing",
        2 * fords.len() as u64 + brook.len() as u64,
    );
    let mut leg = (brook[0], brook[1]);
    for w in brook.windows(2) {
        if seg_dist(f, w[0], w[1]) < seg_dist(f, leg.0, leg.1) {
            leg = (w[0], w[1]);
        }
    }
    let m = dist(leg.0, leg.1).max(1e-12);
    let (ux, uy) = ((leg.1 .0 - leg.0 .0) / m, (leg.1 .1 - leg.0 .1) / m);
    let (nx, ny) = (-uy, ux);
    let (p1, p2) = (
        (f.0 + nx * FORD_LANDING_FT, f.1 + ny * FORD_LANDING_FT),
        (f.0 - nx * FORD_LANDING_FT, f.1 - ny * FORD_LANDING_FT),
    );
    if dist(start, p1) <= dist(start, p2) {
        vec![p1, p2]
    } else {
        vec![p2, p1]
    }
}

/// A run threaded round the steadings that crosses the brook at the ford it was laid over (`via`, the two landings): each leg
/// threaded to its landing apart and the deck kept; threaded whole where the landings' middle is no recorded ford or a leg is
/// clipped short of its landing.
#[must_use]
pub fn thread_over_the_ford(
    f: &Fabric,
    (start, via, end): (Pt, &[Pt], Pt),
    fords: &[Pt],
    tests: &mut Counts,
) -> Vec<Pt> {
    let whole = |tests: &mut Counts| {
        let mut run = vec![start];
        run.extend_from_slice(via);
        run.push(end);
        thread_the_fabric(f, &run, tests)
    };
    if via.len() < 2 {
        return whole(tests);
    }
    let mid = (
        f64::midpoint(via[0].0, via[1].0),
        f64::midpoint(via[0].1, via[1].1),
    );
    if !fords.iter().any(|&c| dist(mid, c) <= 1.0) {
        return whole(tests);
    }
    let near = thread_the_fabric(f, &[start, via[0]], tests);
    let far = thread_the_fabric(f, &[via[1], end], tests);
    if near.len() < 2
        || far.len() < 2
        || dist(near[near.len() - 1], via[0]) > 1.0
        || dist(far[0], via[1]) > 1.0
    {
        return whole(tests);
    }
    near.into_iter().chain(far).collect()
}

/// What a row village's road reads: its first planned street, that street's farms, the farms' frames, the brook, its fords,
/// the sheet, the water the road is squared at, and the fabric it is threaded through.
pub struct RoadSite<'a> {
    /// The first planned street.
    pub street: &'a [Pt],
    /// The houses of that street's farms.
    pub farms: &'a [Pt],
    /// Each farm's frame's longer side.
    pub frames: &'a [f64],
    /// The brook.
    pub brook: &'a [Pt],
    /// Its fords.
    pub fords: &'a [Pt],
    /// The sheet (its width and height).
    pub sheet: Pt,
    /// The water a run is squared at: each course with its half-width.
    pub waters: &'a [(Vec<Pt>, f64)],
    /// What a run is threaded through.
    pub fabric: &'a Fabric<'a>,
}

/// A row village's road: the street as drawn (its farms' span, or the planned street where that span is short) run on off
/// the sheet at both ends, the nearer end's run first, each over the brook at a ford, threaded and squared; the second the
/// road running on.
#[must_use]
pub fn row_road(r: &RoadSite, tests: &mut Counts) -> Vec<Vec<Pt>> {
    if r.street.len() < 2 {
        return Vec::new();
    }
    let span = street_span(r.street, r.farms, row_reach(r.frames), r.brook, tests);
    let base: &[Pt] = if span.len() >= 2 { &span } else { r.street };
    let mut runs = street_runs_out(base, r.sheet).to_vec();
    runs.sort_by(|a, b| a.0.total_cmp(&b.0));
    tests.add("candidate@row_road", 2);
    runs.into_iter()
        .map(|(_, out)| {
            let (a, b) = (out[0], out[out.len() - 1]);
            let via = ford_crossing(a, b, r.brook, r.fords, tests);
            let run = thread_over_the_ford(r.fabric, (a, &via, b), r.fords, tests);
            square_run(&run, r.waters, tests)
        })
        .collect()
}
