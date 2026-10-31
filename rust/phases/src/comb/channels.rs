//! The comb's channels (feature 444 T16): the head race from the intake to the fork, the two supply canals along the fan's high
//! margins, the delivery ditches leaving them at their offtakes, and the drain down the low middle to the foot. Written from
//! `phases/field.md`'s "The comb's design, next" and the record's pages; the old field code unread.
//!
//! Research:
//!     the comb's layout - research/questions/0053-irrigation-canals-and-how-they-are-laid-out-yosuiro.drawing.html: supply canals along the high margins, delivery ditches leaving them, one drain along the lowest line
//!     the widths - research/questions/0068-how-wide-canals-and-ditches-are-the-ladder-of-channel-widths.drawing.html: head race 6.0, supply 4.5 and 4.0 to 1.5, delivery 2.5 to 1.2, drain 1.2 to 5.5 ft
//!     the sweeps - research/questions/0054-which-way-water-flows-and-how-channels-bend-and-join.drawing.html: every turn on a sweep of about 2.5 channel widths

use super::fan::{Fan, Pt};
use crate::pyrand::knob_rng;

/// One channel: its role (`main` for the head race and each leg of a supply canal, `branch` for a delivery ditch, `drain`; the
/// manifest's `field_ditches` roles), its course from head to tail, and its width at each end (feet).
#[derive(Debug, Clone, PartialEq)]
pub struct Channel {
    pub role: &'static str,
    pub pts: Vec<Pt>,
    pub w: f64,
    pub w_tail: f64,
}

/// The head race's width (feet).
///
/// Research:
///     head race - research/questions/0068-how-wide-canals-and-ditches-are-the-ladder-of-channel-widths.drawing.html: 6.0 ft, the small end of the main-canal rung
pub const HEAD_W: f64 = 6.0;
/// Supply canal A's width at its head and B's, both tapering to `THREAD_W` (feet).
///
/// Research:
///     supply canals - research/questions/0068-how-wide-canals-and-ditches-are-the-ladder-of-channel-widths.drawing.html: 4.5 -> 1.5 along the upper edge, 4.0 -> 1.5 along the far edge
pub const SUPPLY_W: (f64, f64) = (4.5, 4.0);
/// The width a supply canal tapers to (feet).
///
/// Research:
///     the canal's tail - research/questions/0053-irrigation-canals-and-how-they-are-laid-out-yosuiro.drawing.html: its tail narrows to a thread, about 1.5 ft across
pub const THREAD_W: f64 = 1.5;
/// A delivery ditch's width at its head and its tail (feet).
///
/// Research:
///     delivery ditch - research/questions/0068-how-wide-canals-and-ditches-are-the-ladder-of-channel-widths.drawing.html: 2.5 -> 1.2
pub const DELIVERY_W: (f64, f64) = (2.5, 1.2);
/// The drain's width at its head and at its outfall (feet).
///
/// Research:
///     drain - research/questions/0068-how-wide-canals-and-ditches-are-the-ladder-of-channel-widths.drawing.html: 1.2 -> 5.5, a field ditch gathering to a branch drain
pub const DRAIN_W: (f64, f64) = (1.2, 5.5);
/// A sweep's radius in channel widths.
///
/// Research:
///     sweeps - research/questions/0054-which-way-water-flows-and-how-channels-bend-and-join.drawing.html: a radius of about two and a half channel widths
pub const SWEEP_WIDTHS: f64 = 2.5;
/// The points an arc of a sweep is drawn with (a CONVENTION of the drawing: enough that a quarter turn reads round).
///
/// Research:
///     the sweep's points - CONVENTION: four segments a turn
const SWEEP_STEPS: usize = 4;

/// How a supply canal ends: running past its last offtake as a thread to the edge of the crop, or handing its whole flow to that
/// offtake's ditch and stopping at the junction; both attested, so a knob rolled from the seed's `canal_tail` stream.
///
/// Research:
///     the canal's tail - research/questions/0053-irrigation-canals-and-how-they-are-laid-out-yosuiro.drawing.html: its tail narrows to a thread and ends at the edge of the crop (Inashiro, Kashikawa, Mizuguchi); where it ends at its offtake it stops at the junction (Sawada)
#[must_use]
pub fn tail_runs_on(seed: i64) -> bool {
    knob_rng(seed, "canal_tail").randbelow(2) == 0
}

/// `pts` with every interior corner rounded on a sweep of `SWEEP_WIDTHS` times `w`, cut back so it never overruns either leg's
/// middle.
///
/// Research:
///     sweeps - research/questions/0054-which-way-water-flows-and-how-channels-bend-and-join.drawing.html: every ditch turns on a sweep, never a sharp corner
#[must_use]
pub fn swept(pts: &[Pt], w: f64) -> Vec<Pt> {
    if pts.len() < 3 {
        return pts.to_vec();
    }
    let mut out = vec![pts[0]];
    for i in 1..pts.len() - 1 {
        let (a, b, c) = (pts[i - 1], pts[i], pts[i + 1]);
        let (l0, l1) = (dist(a, b), dist(b, c));
        let (u0, u1) = (unit(b, a), unit(b, c));
        let cos = (u0.0 * u1.0 + u0.1 * u1.1).clamp(-1.0, 1.0);
        let half = cos.acos() / 2.0; // half the angle between the legs
        if half.tan().abs() < 1e-9 || (half - std::f64::consts::FRAC_PI_2).abs() < 1e-9 {
            out.push(b);
            continue;
        }
        let back = (SWEEP_WIDTHS * w / half.tan()).min(l0 / 2.0).min(l1 / 2.0);
        let p0 = (b.0 + u0.0 * back, b.1 + u0.1 * back);
        let p1 = (b.0 + u1.0 * back, b.1 + u1.1 * back);
        // a quadratic Bezier through the corner: tangent to both legs, inside the turn
        for k in 0..=SWEEP_STEPS {
            #[expect(clippy::cast_precision_loss, reason = "a small step count")]
            let t = k as f64 / SWEEP_STEPS as f64;
            let m = (1.0 - t) * (1.0 - t);
            let n = 2.0 * (1.0 - t) * t;
            let q = t * t;
            out.push((
                m * p0.0 + n * b.0 + q * p1.0,
                m * p0.1 + n * b.1 + q * p1.1,
            ));
        }
    }
    out.push(pts[pts.len() - 1]);
    out
}

fn dist(a: Pt, b: Pt) -> f64 {
    ((b.0 - a.0).powi(2) + (b.1 - a.1).powi(2)).sqrt()
}

fn unit(from: Pt, to: Pt) -> Pt {
    let d = dist(from, to).max(1e-12);
    ((to.0 - from.0) / d, (to.1 - from.1) / d)
}

/// The comb's channels on `fan`, its head race from `intake`; `offtakes` are the delivery ditches' fractions down each flank
/// (canal A on the fan's left looking downhill, B on its right), from the plan's `offtakes_a` and `offtakes_b`. A delivery ditch
/// leaves its canal along the bund of the row its fraction falls on and runs across the fall to the drain; the fan's taper turns
/// the flank inward, so the ditch leaves its canal leaning downstream.
///
/// Research:
///     the comb - research/questions/0053-irrigation-canals-and-how-they-are-laid-out-yosuiro.drawing.html: delivery ditches leaving the supply canals at right angles, one drain gathering the water along the lowest line
///     the lean - research/questions/0054-which-way-water-flows-and-how-channels-bend-and-join.drawing.html: a branch leaves its parent leaning downstream
///     the canals taper - research/questions/0053-irrigation-canals-and-how-they-are-laid-out-yosuiro.drawing.html: every drawn canal tapers from its head toward its tail
#[must_use]
pub fn channels(fan: &Fan, intake: Pt, offtakes: (&[f64], &[f64]), row_ft: f64, seed: i64) -> Vec<Channel> {
    let mut out = vec![Channel {
        role: "main",
        pts: vec![intake, fan.fork],
        w: HEAD_W,
        w_tail: HEAD_W,
    }];
    let runs_on = tail_runs_on(seed);
    let on_row = |f: f64| {
        let u = (f.clamp(0.0, 1.0) * fan.length / row_ft).round() * row_ft;
        u.min(fan.length)
    };
    for (side, (fracs, w)) in [(offtakes.0, SUPPLY_W.0), (offtakes.1, SUPPLY_W.1)]
    .into_iter()
    .enumerate()
    {
        let s = if side == 0 { -1.0 } else { 1.0 };
        let last = fracs.iter().copied().fold(0.0, f64::max);
        let end = if runs_on { fan.length } else { on_row(last) };
        // the canal's legs: the fork to its head corner (swept), then down the flank cut at each offtake, the width stepping down
        // a leg from `w` to the thread (the manifest's `main` pieces, each with its own taper)
        let mut stops: Vec<f64> = fracs.iter().map(|&f| on_row(f)).filter(|&u| u > 0.0 && u < end).collect();
        stops.sort_by(f64::total_cmp);
        stops.dedup();
        stops.push(end);
        let corner = swept(&[fan.fork, fan.at(0.0, s), fan.at(stops[0], s)], w);
        let mut legs: Vec<Vec<Pt>> = vec![corner];
        for pair in stops.windows(2) {
            legs.push(vec![fan.at(pair[0], s), fan.at(pair[1], s)]);
        }
        #[expect(clippy::cast_precision_loss, reason = "a handful of legs")]
        let n = legs.len() as f64;
        for (i, pts) in legs.into_iter().enumerate() {
            #[expect(clippy::cast_precision_loss, reason = "a handful of legs")]
            let (a, b) = (i as f64 / n, (i + 1) as f64 / n);
            out.push(Channel {
                role: "main",
                pts,
                w: w + (THREAD_W - w) * a,
                w_tail: w + (THREAD_W - w) * b,
            });
        }
        for &f in fracs {
            let u = on_row(f);
            out.push(Channel {
                role: "branch",
                pts: vec![fan.at(u, s), fan.at(u, 0.0)],
                w: DELIVERY_W.0,
                w_tail: DELIVERY_W.1,
            });
        }
    }
    out.push(Channel {
        role: "drain",
        pts: vec![fan.at(0.0, 0.0), fan.foot],
        w: DRAIN_W.0,
        w_tail: DRAIN_W.1,
    });
    out
}

#[cfg(test)]
mod tests {
    use super::{channels, dist, swept, tail_runs_on, unit, SWEEP_WIDTHS};
    use crate::comb::fan::fan;

    #[test]
    fn the_comb_has_its_head_race_canals_ditches_and_drain() {
        let f = fan(26.0 * 43_560.0, 1.0, 315.0, (3200.0, 3200.0));
        let intake = (f.fork.0 - 200.0, f.fork.1);
        let c = channels(&f, intake, (&[0.30, 0.62, 0.93], &[0.55]), 48.0, 4);
        let roles: Vec<_> = c.iter().map(|x| x.role).collect();
        assert_eq!(roles.iter().filter(|r| **r == "branch").count(), 4);
        assert_eq!(roles[0], "main");
        assert_eq!(*roles.last().unwrap(), "drain");
        assert!(c.iter().all(|x| x.w >= x.w_tail || x.role == "drain"));
        let mains: Vec<_> = c.iter().filter(|x| x.role == "main").skip(1).collect();
        for pair in mains.windows(2) {
            if (pair[0].w_tail - pair[1].w).abs() < 1e-9 {
                assert!(pair[1].w_tail < pair[0].w, "the canal tapers leg by leg");
            }
        }
        for d in c.iter().filter(|x| x.role == "branch") {
            // the ditch leaves its flank leaning downstream: under a right angle to the canal's downstream run
            let parent = c
                .iter()
                .filter(|x| x.role == "main")
                .find(|x| x.pts.iter().any(|p| dist(*p, d.pts[0]) < 1e-6))
                .unwrap();
            let n = parent.pts.len();
            let down = unit(parent.pts[n - 2], parent.pts[n - 1]);
            let out = unit(d.pts[0], d.pts[1]);
            assert!(down.0 * out.0 + down.1 * out.1 > 0.0, "leaning downstream");
        }
        let both: Vec<_> = (0..16).map(tail_runs_on).collect();
        assert!(both.contains(&true) && both.contains(&false), "both tails attested and rolled");
        let short = channels(&f, intake, (&[0.5], &[]), 48.0, 4);
        assert!(short.iter().filter(|x| x.role == "branch").count() == 1);
    }

    #[test]
    fn a_turn_is_swept_and_a_straight_run_left_alone() {
        let pts = [(0.0, 0.0), (100.0, 0.0), (100.0, 100.0)];
        let s = swept(&pts, 4.0);
        assert!(s.len() > 3);
        assert!(s.iter().all(|p| dist(*p, (100.0, 0.0)) > SWEEP_WIDTHS * 4.0 * 0.2));
        let line = [(0.0, 0.0), (50.0, 0.0), (100.0, 0.0)];
        assert_eq!(swept(&line, 4.0).len(), 3);
        assert_eq!(swept(&pts[..2], 4.0).len(), 2);
    }
}
