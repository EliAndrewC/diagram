//! The waterward fringe (feature 444 T29): a polder's reed strips outside its dike, on the flanks that face the water it was
//! reclaimed from - laid once the seat names the flank the village stands on, before the houses and the track, so both treat it as
//! the wet ground it is. Nothing on a valley hamlet.
//!
//! Research:
//!     the waterward fringe - NONE: the stage's machinery; each rule's claim is at the unit that keeps it

use std::collections::HashMap;

use crate::field::fan::Pt;

#[cfg(feature = "python")]
pub mod py;

/// How far the strip runs past the dike's ends, across the other axis (feet): before its start and past its end.
///
/// Research:
///     its reed strip's run - GUESS: searched, the record silent (feature 417 T38, 2026-10-25) - 30 ft before the dike's start, 20 ft past its end
pub const RUN_PAST: (f64, f64) = (30.0, 20.0);

/// How far off the canvas a strip may reach (feet).
///
/// Research:
///     the strip off the frame - CONVENTION: wild ground continuing, carried 20 ft past the canvas edge
pub const OFF_CANVAS: f64 = 20.0;

/// How many bins sample the dike's outer face.
///
/// Research:
///     its search steps and tolerances - GUESS: no source could speak to it, a value of ours (feature 417 T38 pass N1, 2026-10-25) - 32 bins along the face
pub const BINS: usize = 32;

/// The compass letter a map vector points to (the map's y grows down, so +y is S).
fn compass(v: Pt) -> char {
    if v.0.abs() >= v.1.abs() {
        if v.0 > 0.0 {
            'E'
        } else {
            'W'
        }
    } else if v.1 > 0.0 {
        'S'
    } else {
        'N'
    }
}

/// Which flanks of the dike face the water it was reclaimed from: the foot (the outfall side, already wet) and the cross flanks the
/// village does not stand on - not the head, where the header reservoir stands as the wild water.
///
/// Research:
///     waterward flanks - research/questions/0019-polders-fields-diked-against-the-fluctuating-water-weitian-waju.drawing.html: every flank but the landward one holds water back; a reed fringe along the low foot where the outfall drains and along the cross flank off the shore, the wild pond that feeds the polder at its head - its water drawn there as the pond, so no reed strip is laid off the head
#[must_use]
pub fn flanks(fall: Pt, seat_out: Option<Pt>) -> Vec<char> {
    let (dx, dy) = fall;
    let cluster = seat_out.map(compass);
    [compass((-dy, dx)), compass((dy, -dx)), compass((dx, dy))]
        .into_iter()
        .filter(|q| Some(*q) != cluster)
        .collect()
}

/// The dike's outer face along one flank, as a polyline spanning `lo` to `hi`: the outline's points binned along the flank's axis,
/// the outermost of each bin its face, a bin the ring does not reach keeping its neighbor's; stepped in by `cut` through each notch
/// in `cuts` (`cut_hw` either side of it); a run of bins at one face its first and last points only.
///
/// Research:
///     strip at the dike's outer face - GUESS: searched, the record silent (feature 417 T36 pass P2a, 2026-10-25); the reeds stop at the outermost face, stepping in through a notch
#[must_use]
#[expect(
    clippy::too_many_arguments,
    clippy::float_cmp,
    reason = "the face's ring, flank, span, cut and notches; a run of bins holds the one value taken, compared exactly"
)]
pub fn face(
    pts: &[Pt],
    flank: char,
    lo: f64,
    hi: f64,
    cut: f64,
    cuts: &[Pt],
    cut_hw: f64,
    tests: &mut u64,
) -> Vec<Pt> {
    let horiz = matches!(flank, 'W' | 'E');
    let get = |p: &Pt, axis: usize| if axis == 0 { p.0 } else { p.1 };
    let (ai, fi) = if horiz { (1, 0) } else { (0, 1) };
    let outward_min = matches!(flank, 'W' | 'N');
    let fs: Vec<f64> = pts.iter().map(|p| get(p, fi)).collect();
    let (fmin, fmax) = fs
        .iter()
        .fold((f64::MAX, f64::MIN), |(a, b), &v| (a.min(v), b.max(v)));
    let mid = f64::midpoint(fmin, fmax);
    *tests += 2 * pts.len() as u64; // the face's coordinates read and their extremes found, two passes
    #[expect(clippy::cast_precision_loss, reason = "32 bins")]
    let step = (hi - lo) / BINS as f64;
    let mut buckets: Vec<Vec<f64>> = vec![Vec::new(); BINS];
    for p in pts {
        *tests += 1;
        let k = ((get(p, ai) - lo) / step).floor();
        let own = if outward_min {
            get(p, fi) <= mid
        } else {
            get(p, fi) >= mid
        };
        #[expect(
            clippy::cast_possible_truncation,
            clippy::cast_sign_loss,
            reason = "a bin of 32, its sign tested first"
        )]
        if k >= 0.0 && (k as usize) < BINS && own {
            buckets[k as usize].push(get(p, fi));
        }
    }
    let filled: Vec<usize> = (0..BINS).filter(|&k| !buckets[k].is_empty()).collect();
    let (first, last_filled) = (
        filled.first().copied().unwrap_or(BINS),
        filled.last().copied(),
    );
    let mut last = if outward_min { fmin } else { fmax };
    let mut vals = Vec::with_capacity(BINS);
    for (k, b) in buckets.iter().enumerate() {
        if !b.is_empty() {
            last = b
                .iter()
                .copied()
                .fold(if outward_min { f64::MAX } else { f64::MIN }, |a, v| {
                    if outward_min {
                        a.min(v)
                    } else {
                        a.max(v)
                    }
                });
        }
        #[expect(clippy::cast_precision_loss, reason = "32 bins")]
        let c = lo + (k as f64 + 0.5) * step;
        let mut v = last;
        *tests += cuts.len() as u64;
        if last_filled.is_some_and(|f| first <= k && k <= f)
            && cuts
                .iter()
                .any(|g| (get(g, ai) - c).abs() <= cut_hw + step / 2.0)
        {
            v = last + if outward_min { cut } else { -cut };
        }
        vals.push(v);
    }
    let round = |v: f64| (v * 10.0).round() / 10.0;
    let mut out = Vec::new();
    for (k, &v) in vals.iter().enumerate() {
        if k == 0 || k == BINS - 1 || v != vals[k - 1] || v != vals[k + 1] {
            #[expect(clippy::cast_precision_loss, reason = "32 bins")]
            let c = lo + (k as f64 + 0.5) * step;
            out.push(if horiz {
                (round(v), round(c))
            } else {
                (round(c), round(v))
            });
        }
    }
    out
}

/// What the fringe laid: each water-facing flank's strip, in the order the flanks are asked, and the counters.
#[derive(Debug, Default)]
pub struct Fringe {
    /// The flanks facing the water.
    pub flanks: Vec<char>,
    /// Each flank's strip.
    pub strips: Vec<Vec<Pt>>,
    /// The counters (D5).
    pub counts: HashMap<String, u64>,
}

/// The fringe of a polder whose dike rings are `dikes` (each its outline and its notch centers), its band `cut` wide at its widest,
/// the strip `depth` deep, on a `canvas`; nothing where no dike stands.
///
/// Research:
///     reed fringe on the waterward flanks - research/questions/0019-polders-fields-diked-against-the-fluctuating-water-weitian-waju.drawing.html: a marsh strip off each water-facing flank
///     each notch one flank's - GUESS: no page assigns a notch to a flank; the flank whose face it stands nearest, so a cut near a corner bites one strip, not two
#[must_use]
pub fn fringe(
    dikes: &[(Vec<Pt>, Vec<Pt>)],
    cut: f64,
    cut_hw: f64,
    depth: f64,
    canvas: Pt,
    fall: Pt,
    seat_out: Option<Pt>,
) -> Fringe {
    let mut counts = HashMap::new();
    let pts: Vec<Pt> = dikes.iter().flat_map(|(o, _)| o.iter().copied()).collect();
    if pts.is_empty() {
        return Fringe {
            counts,
            ..Fringe::default()
        };
    }
    let (mut x0, mut y0, mut x1, mut y1) = (f64::MAX, f64::MAX, f64::MIN, f64::MIN);
    for p in &pts {
        x0 = x0.min(p.0);
        y0 = y0.min(p.1);
        x1 = x1.max(p.0);
        y1 = y1.max(p.1);
    }
    let mut by: HashMap<char, Vec<Pt>> = HashMap::new();
    let mut gaps = 0;
    for g in dikes.iter().flat_map(|(_, g)| g.iter()) {
        gaps += 1;
        let near = [
            ('W', g.0 - x0),
            ('E', x1 - g.0),
            ('N', g.1 - y0),
            ('S', y1 - g.1),
        ];
        let q = near
            .iter()
            .fold(near[0], |a, &b| if b.1 < a.1 { b } else { a })
            .0;
        by.entry(q).or_default().push(*g);
    }
    let (ylo, yhi, xlo, xhi) = (
        y0 - RUN_PAST.0,
        y1 + RUN_PAST.1,
        x0 - RUN_PAST.0,
        x1 + RUN_PAST.1,
    );
    let mut tests = 0;
    let fl = flanks(fall, seat_out);
    let none = Vec::new();
    let strips = fl
        .iter()
        .map(|&q| {
            let notch = by.get(&q).unwrap_or(&none);
            let (outer, lo, hi) = match q {
                'W' => ((x0 - depth).max(-OFF_CANVAS), ylo, yhi),
                'E' => ((x1 + depth).min(canvas.0 + OFF_CANVAS), ylo, yhi),
                'N' => ((y0 - depth).max(-OFF_CANVAS), xlo, xhi),
                _ => ((y1 + depth).min(canvas.1 + OFF_CANVAS), xlo, xhi),
            };
            let f = face(&pts, q, lo, hi, cut, notch, cut_hw, &mut tests);
            let (a, b) = if matches!(q, 'W' | 'E') {
                ((outer, lo), (outer, hi))
            } else {
                ((lo, outer), (hi, outer))
            };
            let mut ring = vec![a];
            ring.extend(f);
            ring.push(b);
            ring
        })
        .collect::<Vec<_>>();
    *counts.entry("read@dike".to_owned()).or_insert(0) += pts.len() as u64 + gaps;
    *counts.entry("test@face".to_owned()).or_insert(0) += tests;
    *counts.entry("write@strip".to_owned()).or_insert(0) +=
        strips.iter().map(Vec::len).sum::<usize>() as u64;
    Fringe {
        flanks: fl,
        strips,
        counts,
    }
}

#[cfg(test)]
mod tests;
