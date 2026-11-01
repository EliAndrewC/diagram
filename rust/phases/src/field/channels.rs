//! The comb's channels (feature 444 T16): the head race from the intake to the fork, the two supply canals along the fan's high
//! margins, the delivery ditches leaving them at their offtakes, and the drain down the low middle to the foot. Written from
//! `phases/field.md`'s "The comb's design, next" and the record's pages; the old field code unread.
//!
//! Research:
//!     the comb's layout - research/questions/0053-irrigation-canals-and-how-they-are-laid-out-yosuiro.drawing.html: supply canals along the high margins, delivery ditches leaving them, one drain along the lowest line
//!     the widths - research/questions/0068-how-wide-canals-and-ditches-are-the-ladder-of-channel-widths.drawing.html: head race 6.0, supply 4.5 and 4.0 to 1.5, delivery 2.5 to 1.2, drain 1.2 to 5.5 ft
//!     the sweeps - research/questions/0054-which-way-water-flows-and-how-channels-bend-and-join.drawing.html: every turn on a sweep of about 2.5 channel widths

use super::fan::EDGE_STEP_FT;
use super::fan::{Fan, Pt};
use super::geom::{dist, unit};
use super::lattice::Lines;
use crate::pyrand::knob_rng;

/// One channel: its role (`main` for the head race and each leg of a supply canal, `branch` for a delivery ditch, `drain`; the
/// manifest's `field_ditches` roles), its course from head to tail, and its width at each end (feet).
///
/// Research:
///     a channel's record - NONE: the record's type, holding what `channels` decides
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
/// A delivery ditch's head at most this share of its canal's width where it leaves it.
///
/// Research:
///     the delivery's cap - research/questions/0068-how-wide-canals-and-ditches-are-the-ladder-of-channel-widths.drawing.html: a delivery ditch's head is capped at 0.8 of its canal's local width where it leaves it
pub const DELIVERY_CAP: f64 = 0.8;
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
/// A turn under this is left sharp (degrees), and a bend's radius at most this share of the straight run on either side.
///
/// Research:
///     the sweep's limits - research/questions/0054-which-way-water-flows-and-how-channels-bend-and-join.drawing.html: a turn of under about 8 degrees is left sharp, and a bend's radius is capped at 35% of the straight run on either side
pub const SWEEP_LIMITS: (f64, f64) = (8.0, 0.35);

/// How a supply canal ends: running past its last offtake as a thread to the edge of the crop, or handing its whole flow to that
/// offtake's ditch and stopping at the junction; both attested, so a knob rolled from the seed's `canal_tail` stream.
///
/// Research:
///     the canal's tail - research/questions/0053-irrigation-canals-and-how-they-are-laid-out-yosuiro.drawing.html: its tail narrows to a thread and ends at the edge of the crop (Inashiro, Kashikawa, Mizuguchi); where it ends at its offtake it stops at the junction (Sawada)
///     the endings' odds - GUESS: research/questions/0053-irrigation-canals-and-how-they-are-laid-out-yosuiro.drawing.html silent on how often each ending was dug; even odds
#[must_use]
pub fn tail_runs_on(seed: i64) -> bool {
    knob_rng(seed, "canal_tail").randbelow(2) == 0
}

/// `pts` with every interior corner rounded on a sweep of `SWEEP_WIDTHS` times `w`, cut back so it never overruns either leg's
/// middle.
///
/// Research:
///     sweeps - research/questions/0054-which-way-water-flows-and-how-channels-bend-and-join.drawing.html: every ditch turns on a sweep, never a sharp corner
///     a bend's radius - research/questions/0054-which-way-water-flows-and-how-channels-bend-and-join.drawing.html: about two and a half channel widths (`SWEEP_WIDTHS`), capped at 35% of the straight run on either side, a turn under about 8 degrees left sharp (`SWEEP_LIMITS`); the setback never past either leg's middle
#[expect(
    clippy::many_single_char_names,
    reason = "the plane geometry's own names"
)]
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
                                     // the turn's own angle, the deflection off straight on: a fold back has none to sweep, and a slight one is left sharp
        let turn = std::f64::consts::PI - 2.0 * half;
        if half.tan().abs() < 1e-9 || turn.to_degrees() < SWEEP_LIMITS.0 {
            out.push(b);
            continue;
        }
        let radius = (SWEEP_WIDTHS * w).min(SWEEP_LIMITS.1 * l0.min(l1));
        let back = (radius / half.tan()).min(l0 / 2.0).min(l1 / 2.0);
        let p0 = (b.0 + u0.0 * back, b.1 + u0.1 * back);
        let p1 = (b.0 + u1.0 * back, b.1 + u1.1 * back);
        // a quadratic Bezier through the corner: tangent to both legs, inside the turn
        for k in 0..=SWEEP_STEPS {
            #[expect(clippy::cast_precision_loss, reason = "a small step count")]
            let t = k as f64 / SWEEP_STEPS as f64;
            let m = (1.0 - t) * (1.0 - t);
            let n = 2.0 * (1.0 - t) * t;
            let q = t * t;
            out.push((m * p0.0 + n * b.0 + q * p1.0, m * p0.1 + n * b.1 + q * p1.1));
        }
    }
    out.push(pts[pts.len() - 1]);
    out
}

/// Each offtake's row line: the one its fraction of the fan's length falls on, or the nearest where the flank leans in, so the
/// ditch leaves its canal leaning downstream (D7: the rule held where it is decided); a fraction with no such line within three
/// rows draws no ditch.
///
/// Research:
///     the lean - research/questions/0054-which-way-water-flows-and-how-channels-bend-and-join.drawing.html: a delivery ditch in the comb follows its row's bund, leaving nearly square to its canal, drawn only where that bund leans downstream off the canal's flank; the 35 degrees a branch's where nothing on the ground sets the angle
///     where an offtake goes - GUESS: research/questions/0053-irrigation-canals-and-how-they-are-laid-out-yosuiro.drawing.html silent on moving an offtake to a leaning row; the nearest within three rows, never the first or last row, none where no row leans
fn offtake_lines(fan: &Fan, lines: &Lines, fracs: &[f64], s: f64) -> Vec<usize> {
    let mut lines_at: Vec<usize> = Vec::new();
    for &f in fracs {
        #[expect(
            clippy::cast_possible_truncation,
            clippy::cast_sign_loss,
            reason = "a row index"
        )]
        let r0 = ((f.clamp(0.0, 1.0) * fan.length / lines.step).round() as usize)
            .clamp(1, lines.rows.max(2) - 1);
        let leans = |r: usize| {
            let j = fan.at(lines.u(r, s), s);
            let up = fan.at((lines.u(r, s) - lines.step).max(0.0), s);
            let inward = fan.at(lines.u(r, s * 0.8), s * 0.8);
            let (d, o) = (unit(up, j), unit(j, inward));
            d.0 * o.0 + d.1 * o.1 > 0.0
        };
        let pick = [0_i64, 1, -1, 2, -2, 3, -3]
            .iter()
            .filter_map(|d| usize::try_from(i64::try_from(r0).unwrap_or(0) + d).ok())
            .find(|&r| r >= 1 && r < lines.rows && leans(r));
        lines_at.extend(pick);
    }
    lines_at
}

/// The division point, where the head race forks into the two supply canals: the head corner on the brook's flank (`brook_side`
/// +1 the fan's right looking downhill, -1 its left), so the race is short and the brook keeps outside the crop beside it.
///
/// Research:
///     the fork - research/questions/0068-how-wide-canals-and-ditches-are-the-ladder-of-channel-widths.drawing.html: the head race splits into a supply canal along the upper edge and one along the far edge
///     the fork's place - research/questions/0059-where-the-ditch-leaves-the-brook-the-intake-and-its-weir-toshuko-and-seki.drawing.html: the race runs from the intake down to the fork at the head of the fan - at the head's corner on the brook's side where the intake stands at that shoulder, at its middle where the intake does
#[must_use]
pub fn division(fan: &Fan, brook_side: f64, center: bool) -> Pt {
    fan.at(0.0, if center { 0.0 } else { brook_side })
}

/// The comb's channels on `fan`, its head race from `intake` to the `division`; `offtakes` are the delivery ditches' fractions down each flank
/// (canal A along the upper edge and down the far flank, B down the brook's flank), from the plan's `offtakes_a` and `offtakes_b`. A delivery ditch
/// leaves its canal along the bund of the row its fraction falls on and runs across the fall to the drain; the fan's taper turns
/// the flank inward, so the ditch leaves its canal leaning downstream.
///
/// Research:
///     the comb - research/questions/0053-irrigation-canals-and-how-they-are-laid-out-yosuiro.drawing.html: supply canals along the high margins, delivery ditches leaving them nearly at right angles, one drain gathering the water along the lowest line - each delivery along its row's bund, leaning downstream as the bund does (research/questions/0054-which-way-water-flows-and-how-channels-bend-and-join.drawing.html: a delivery ditch in the comb follows its row's bund; `offtake_lines`)
///     the canals taper - research/questions/0053-irrigation-canals-and-how-they-are-laid-out-yosuiro.drawing.html: every drawn canal tapers from its head toward its tail
///     the delivery's head - research/questions/0068-how-wide-canals-and-ditches-are-the-ladder-of-channel-widths.drawing.html: capped at 0.8 of its canal's local width where it leaves it (`DELIVERY_CAP`), biting wherever the canal is under about 3.1 ft - low in the net, and at every offtake of a canal with only one or two - its tail no wider than its head; where a canal stops at its last offtake, narrowed to 1.5 ft, that last delivery leaves at 1.2 ft and runs flat
///     the canals' courses - research/questions/0053-irrigation-canals-and-how-they-are-laid-out-yosuiro.drawing.html: supply canals along the high margins - canal A along the head to the far corner, swept, then down the far flank; canal B down the brook's flank from a corner fork, or swept along the head to its own corner from a middle one
///     the head race - research/questions/0068-how-wide-canals-and-ditches-are-the-ladder-of-channel-widths.drawing.html: the head race 6.0 ft, the whole fan's above the fork - at that width throughout
///     the head race's course - research/questions/0059-where-the-ditch-leaves-the-brook-the-intake-and-its-weir-toshuko-and-seki.drawing.html: the race runs from the intake down to the fork at the head of the fan - one straight run
///     the widths by role - research/questions/0068-how-wide-canals-and-ditches-are-the-ladder-of-channel-widths.drawing.html: the head race 6.0, supply 4.5 to 1.5 along the upper edge and 4.0 to 1.5 along the other, delivery 2.5 to 1.2, drain 1.2 to 5.5 ft - canal A the upper edge's, along the head and down the far flank, canal B the other edge's, down the brook's flank (`HEAD_W`, `SUPPLY_W`, `DELIVERY_W`, `DRAIN_W`)
///     the first canal with no offtake - GUESS: research/questions/0053-irrigation-canals-and-how-they-are-laid-out-yosuiro.drawing.html silent on a first canal its fractions leave no offtake; canal A runs on to the crop's edge
///     the second canal with none - research/questions/0053-irrigation-canals-and-how-they-are-laid-out-yosuiro.drawing.html: the second canal is drawn partway down its edge - half way, where its fractions leave it no offtake
///     the canal's steps - research/questions/0068-how-wide-canals-and-ditches-are-the-ladder-of-channel-widths.drawing.html: a canal narrows in equal steps from its head to 1.5 ft - an equal step a leg from its head's width to the thread
///     a delivery's course - research/questions/0053-irrigation-canals-and-how-they-are-laid-out-yosuiro.drawing.html: delivery ditches leaving the supply canals - each along its row's bund from the flank to the drain at the middle, bowed as the bund is
///     the canal's end - research/questions/0053-irrigation-canals-and-how-they-are-laid-out-yosuiro.drawing.html: its tail narrows to a thread and ends at the edge of the crop, or stops at its last offtake's junction (`tail_runs_on`) - tapering to the thread at its end either way
///     the second canal partway - research/questions/0053-irrigation-canals-and-how-they-are-laid-out-yosuiro.drawing.html: the second canal feeds at least one delivery ditch, so it is drawn partway down its edge - stopping at its last offtake's junction, the first canal taking either ending
#[must_use]
pub fn channels(
    fan: &Fan,
    intake: Pt,
    offtakes: (&[f64], &[f64]),
    row_ft: f64,
    brook_side: f64,
    center: bool,
    seed: i64,
) -> Vec<Channel> {
    let fork = division(fan, brook_side, center);
    let mut out = vec![Channel {
        role: "main",
        pts: vec![intake, fork],
        w: HEAD_W,
        w_tail: HEAD_W,
    }];
    let runs_on = tail_runs_on(seed);
    let lines = Lines::new(fan, seed, row_ft);
    // the flank's course from `u0` to `u1` as drawn: a point every `EDGE_STEP_FT`
    let flank = |u0: f64, u1: f64, s: f64| -> Vec<Pt> {
        #[expect(
            clippy::cast_possible_truncation,
            clippy::cast_sign_loss,
            reason = "a small positive count of steps"
        )]
        let n = (((u1 - u0) / EDGE_STEP_FT).ceil() as usize).max(1);
        #[expect(clippy::cast_precision_loss, reason = "a small step count")]
        let at = |k: usize| u0 + (u1 - u0) * k as f64 / n as f64;
        (0..=n).map(|k| fan.at(at(k), s)).collect()
    };
    for (side, (fracs, w)) in [(offtakes.0, SUPPLY_W.0), (offtakes.1, SUPPLY_W.1)]
        .into_iter()
        .enumerate()
    {
        // canal A on the far flank, along the upper edge first; canal B down the brook's flank from the fork
        let s = if side == 0 { -brook_side } else { brook_side };
        let mut lines_at = offtake_lines(fan, &lines, fracs, s);
        lines_at.sort_unstable();
        lines_at.dedup();
        // canal A runs on to the crop's edge when its tail runs on; canal B, partway down its edge, stops at its last offtake
        let last = lines_at.last().copied();
        let end = match (last, runs_on, side) {
            (Some(r), false, _) | (Some(r), _, 1) => lines.u(r, s),
            (None, _, 1) => fan.length / 2.0,
            _ => fan.length,
        };
        // the canal's legs: the fork to its head corner (swept), then down the flank cut at each offtake, the width stepping down
        // a leg from `w` to the thread (the manifest's `main` pieces, each with its own taper)
        let mut stops: Vec<f64> = lines_at
            .iter()
            .map(|&r| lines.u(r, s))
            .filter(|&u| u < end)
            .collect();
        stops.push(end);
        let mut legs: Vec<Vec<Pt>> = Vec::new();
        let mut down = flank(0.0, stops[0], s);
        // from a middle fork both canals run along the head to their corners
        if side == 0 || center {
            let mut head = swept(&[fork, fan.at(0.0, s), down[1]], w);
            head.extend(down.drain(2..));
            legs.push(head);
        } else {
            down[0] = fork;
            legs.push(down);
        }
        for pair in stops.windows(2) {
            legs.push(flank(pair[0], pair[1], s));
        }
        #[expect(clippy::cast_precision_loss, reason = "a handful of legs")]
        let n = legs.len() as f64;
        // every canal narrows to a thread, the one stopping at its last offtake there; that ditch's head is capped against it
        let tail = THREAD_W;
        for (i, pts) in legs.into_iter().enumerate() {
            #[expect(clippy::cast_precision_loss, reason = "a handful of legs")]
            let (a, b) = (i as f64 / n, (i + 1) as f64 / n);
            out.push(Channel {
                role: "main",
                pts,
                w: w + (tail - w) * a,
                w_tail: w + (tail - w) * b,
            });
        }
        for (j, &r) in lines_at.iter().enumerate() {
            // along its row's bund, bowed as the bund is, from the flank to the drain
            let pts = (0..=5).map(|k| {
                let q = s * (1.0 - f64::from(k) / 5.0);
                fan.at(lines.u(r, q), q)
            });
            // the canal's width where it leaves it: the tail of the leg the junction ends
            #[expect(clippy::cast_precision_loss, reason = "a handful of legs")]
            let local = w + (tail - w) * ((j + 1) as f64 / n).min(1.0);
            let head = DELIVERY_W.0.min(DELIVERY_CAP * local);
            out.push(Channel {
                role: "branch",
                pts: pts.collect(),
                w: head,
                w_tail: DELIVERY_W.1.min(head),
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
    use super::{channels, swept, tail_runs_on, SWEEP_WIDTHS};
    use crate::field::fan::fan;
    use crate::field::geom::{dist, unit};

    #[test]
    fn the_comb_has_its_head_race_canals_ditches_and_drain() {
        let f = fan(26.0 * 43_560.0, 1.0, 315.0, (3200.0, 3200.0), 4);
        let intake = (f.fork.0 - 200.0, f.fork.1);
        let c = channels(
            &f,
            intake,
            (&[0.30, 0.62, 0.93], &[0.55]),
            48.0,
            1.0,
            false,
            4,
        );
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
        assert!(both.contains(&true) && both.contains(&false));
        let short = channels(&f, intake, (&[0.5], &[]), 48.0, -1.0, false, 4);
        assert!(short.iter().filter(|x| x.role == "branch").count() == 1);
        // canal A with no offtake runs on to the crop's edge
        let bare = channels(&f, intake, (&[], &[0.5]), 48.0, -1.0, false, 4);
        assert!(bare.iter().filter(|x| x.role == "branch").count() <= 1);
    }

    #[test]
    fn a_turn_is_swept_and_a_straight_run_left_alone() {
        let pts = [(0.0, 0.0), (100.0, 0.0), (100.0, 100.0)];
        let s = swept(&pts, 4.0);
        assert!(s.len() > 3);
        assert!(s
            .iter()
            .all(|p| dist(*p, (100.0, 0.0)) > SWEEP_WIDTHS * 4.0 * 0.2));
        let line = [(0.0, 0.0), (50.0, 0.0), (100.0, 0.0)];
        assert_eq!(swept(&line, 4.0).len(), 3);
        assert_eq!(swept(&pts[..2], 4.0).len(), 2);
    }
}
