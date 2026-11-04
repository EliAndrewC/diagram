//! The drain off the map (feature 444 T26 D5): joining the passing brook where it runs on within reach of the outfall, else run
//! out of the collector's exit off the map - the run searched nearest first, the first that keeps every rule taken, and where none
//! does, the sink refused by name (the round arbiter, ask:444-T26-constructed-turn: a route constructed round the field's hull
//! held 0060's 55-degree turn on its first leg only, and no seed of the Rust gate's 54 nor any pool map took it).
//!
//! Research:
//!     the off-map branch - NONE: the branch's machinery; each rule's claim is at the unit that keeps it

#![expect(
    clippy::many_single_char_names,
    reason = "the plane geometry's own names"
)]

use std::collections::HashMap;

use super::brook::{Brook, TWIN_RUN};
use super::crop::{off_resting, Crop};
use super::{tally, SinkIn, SinkRefused, Sunk};
use crate::field::fan::Pt;
use crate::field::geom::dist;

/// How far from the outfall the brook is joined (feet).
///
/// Research:
///     join reach - GUESS: searched, the record silent (feature 417 T36 pass P2a, 2026-10-25); 500 ft from the outfall (420 until feature 444 T26: the field port laid Kashikawa's brook 464 ft off its outfall, and the confluence its generator declares was lost)
pub const JOIN_REACH: f64 = 500.0;
/// The stride the brook is walked at for a confluence (feet).
///
/// Research:
///     the walk's stride - NONE: a search step, 10 ft
pub const JOIN_STRIDE: f64 = 10.0;
/// How far below the outfall a confluence has fallen, so the drain's run descends to it (feet).
///
/// Research:
///     confluence fallen below the outfall - GUESS: no source could speak to it, a value of ours (feature 417 T36 pass P2a, 2026-10-25); 20 ft down the fall
pub const JOIN_DESCENT: f64 = 20.0;
/// The share of a run to a confluence that may lie in the rice as the field's own edge.
///
/// Research:
///     crop lead tolerance - GUESS: no source could speak to it, a value of ours (feature 417 T36 pass P2a, 2026-10-25); 0.3 of the drain's run
pub const JOIN_LEAD: f64 = 0.3;
/// The most a drain run off the map turns out of the collector's exit (degrees).
///
/// Research:
///     drain junction turn - research/questions/0060-field-drains-akusuiro.drawing.html: "The turn is held to 55 degrees or less"
pub const TURN_MAX_DEG: f64 = 55.0;
/// The swings off a base bearing a run tries, nearest first (degrees).
///
/// Research:
///     bearing swings - GUESS: no source could speak to it, a value of ours (feature 417 T38 pass N5, 2026-10-25); 12, 24, 38 and 54 degrees each way, inside the 55 degree turn
pub const SWINGS: [f64; 9] = [0.0, 12.0, -12.0, 24.0, -24.0, 38.0, -38.0, 54.0, -54.0];
/// The junction distances a run tries, the near sweep then the wide (feet).
///
/// Research:
///     junction distances - GUESS: no source could speak to it, a value of ours (feature 417 T38 pass N5, 2026-10-25); 70 to 230 ft, then 300 and 400
pub const JUNCTIONS: ([f64; 4], [f64; 2]) = ([70.0, 110.0, 160.0, 230.0], [300.0, 400.0]);
/// How far back up the collector the run's start may move to stand inside the field (feet), nearest first.
///
/// Research:
///     the start inside the field - GUESS: no source could speak to it, a value of ours (feature 417 T38 pass N5, 2026-10-25); 0 to 60 ft back
pub const BACK_OFF: [f64; 5] = [0.0, 12.0, 24.0, 40.0, 60.0];
/// How far past the canvas edge a run is carried (feet), and the least it runs to the edge.
///
/// Research:
///     run carried off the canvas - GUESS: no source could speak to it, a value of ours (feature 417 T38 pass N5, 2026-10-25); 260 ft past the edge, at least 120 to it
pub const OFF_CANVAS: (f64, f64) = (260.0, 120.0);
fn u(p: Pt, f: Pt) -> f64 {
    p.0 * f.0 + p.1 * f.1
}

/// The angle between two bearings in degrees, 0 to 180.
fn off(a: f64, b: f64) -> f64 {
    ((a - b + 180.0).rem_euclid(360.0) - 180.0).abs()
}

/// The run's rules, every one asked of a candidate before it is drawn: the turn out of the collector, the rice, downhill, the
/// drainage bearing, the brook (not crossed mid-run, not run beside as its twin) and the resting basins.
///
/// Research:
///     runs downhill - research/questions/0054-which-way-water-flows-and-how-channels-bend-and-join.drawing.html: net travel down the fall, strictly under 90 degrees off it
///     with the drainage bearing - research/questions/0054-which-way-water-flows-and-how-channels-bend-and-join.drawing.html: under 90 degrees off the water's flow
///     not the brook's twin - research/questions/0067-do-two-ditches-run-side-by-side-across-the-fields-not-in-the-old-forms-the-map-draws.html
fn keeps(
    inp: &SinkIn,
    crop: &Crop,
    brook: &mut Brook,
    run: &[Pt],
    head: Pt,
    anchored: bool,
    tests: &mut u64,
) -> bool {
    let out = run[0];
    let lead = (run[1].0 - out.0, run[1].1 - out.1);
    let ln = (lead.0 * lead.0 + lead.1 * lead.1).sqrt().max(1e-9);
    let turn = ((head.0 * lead.0 + head.1 * lead.1) / ln)
        .clamp(-1.0, 1.0)
        .acos()
        .to_degrees();
    let end = run[run.len() - 1];
    let net = (end.0 - out.0, end.1 - out.1);
    let bear = net.1.atan2(net.0).to_degrees();
    *tests += 3;
    turn <= TURN_MAX_DEG
        && u(net, inp.fall) > 0.0
        && off(bear, inp.flow_deg) < 90.0
        && crop.run_clear(run, anchored, tests)
        && !brook.crossed(run, inp.brook_w)
        && brook.twin_run(run) <= TWIN_RUN
        && off_resting(run, &inp.resting, inp.run_w, anchored, tests)
}

/// The confluence: the nearest point on the brook as drawn within `JOIN_REACH` of the outfall, fallen `JOIN_DESCENT` below it,
/// with the trunk's length (`SinkIn::join_trunk`) of brook on the canvas below it, reached without crossing the crop past the run's
/// lead - a point of the drawn course, so the drain's mouth lies in it (D2).
///
/// Research:
///     the nearest fallen point, off the crop - GUESS: no source could speak to it, a value of ours (feature 417 T36 pass P2a, 2026-10-25); the nearest fallen candidate is the confluence
fn confluence(
    inp: &SinkIn,
    crop: &Crop,
    brook: &mut Brook,
    out: Pt,
    tests: &mut u64,
) -> Option<Pt> {
    let f = inp.fall;
    let mut best: Option<(f64, Pt)> = None;
    for i in brook.span(u(out, f) + JOIN_DESCENT, u(out, f) + JOIN_REACH) {
        let (a, b) = brook.seg(i);
        let run = dist(a, b);
        let steps = (run / JOIN_STRIDE).floor();
        let mut s = 0.0;
        while s <= steps {
            let t = (s * JOIN_STRIDE / run.max(1e-9)).min(1.0);
            s += 1.0;
            *tests += 1;
            let q = (a.0 + (b.0 - a.0) * t, a.1 + (b.1 - a.1) * t);
            let d = dist(q, out);
            if d > JOIN_REACH
                || u((q.0 - out.0, q.1 - out.1), f) < JOIN_DESCENT
                || best.is_some_and(|(m, _)| d >= m)
            {
                continue;
            }
            if !trunk_below(inp, brook, i, q, tests) || through_crop(crop, out, q, tests) {
                continue;
            }
            best = Some((d, q));
        }
    }
    best.map(|(_, q)| q)
}

/// Whether the brook runs on the trunk's length on the canvas below `q` on segment `i`, walked down from it until it has.
///
/// Research:
///     brook below a confluence - CONVENTION: the trunk's length on the canvas, so the junction reads
fn trunk_below(inp: &SinkIn, brook: &mut Brook, i: usize, q: Pt, tests: &mut u64) -> bool {
    let mut len = 0.0;
    let mut from = q;
    for k in i + 1..brook.len() {
        *tests += 1;
        let p = brook.at(k);
        len += on_canvas(from, p, inp.canvas);
        if len >= inp.join_trunk {
            return true;
        }
        from = p;
    }
    false
}

/// The length of segment `a-b` on the canvas (Liang-Barsky's clip to the canvas's box).
#[must_use]
pub fn on_canvas(a: Pt, b: Pt, canvas: Pt) -> f64 {
    let (dx, dy) = (b.0 - a.0, b.1 - a.1);
    let (mut t0, mut t1) = (0.0_f64, 1.0_f64);
    for (p, q) in [
        (-dx, a.0),
        (dx, canvas.0 - a.0),
        (-dy, a.1),
        (dy, canvas.1 - a.1),
    ] {
        if p == 0.0 {
            if q < 0.0 {
                return 0.0;
            }
        } else {
            let r = q / p;
            if p < 0.0 {
                t0 = t0.max(r);
            } else {
                t1 = t1.min(r);
            }
        }
    }
    (t1 - t0).max(0.0) * dist(a, b)
}

/// Whether a straight run from the outfall to `q` goes through the rice past its lead: the first `JOIN_LEAD` of it, where it
/// leaves the field, is the field's own edge.
///
/// Research:
///     not through the rice - GUESS: no source could speak to it, a value of ours (feature 417 T36 pass P2a, 2026-10-25); the run leaves the field within its lead and never re-enters it
fn through_crop(crop: &Crop, out: Pt, q: Pt, tests: &mut u64) -> bool {
    let at = |t: f64| (out.0 + (q.0 - out.0) * t, out.1 + (q.1 - out.1) * t);
    let lead = (0..=20)
        .map(|k| f64::from(k) / 20.0)
        .find(|&t| !crop.holds(at(t), tests))
        .unwrap_or(1.0);
    lead > JOIN_LEAD || !crop.run_clear(&[at(lead), q], false, tests)
}

/// The runs searched, nearest first: bearings swung round the fall and round the collector's heading, at the near junction
/// distances and then the wide; the junction on the bisector of the heading and the bearing, so the run turns half the angle
/// twice; the run carried past the canvas edge along its bearing.
///
/// Research:
///     the run's form and order - GUESS: no source could speak to it, a value of ours (feature 417 T38 pass N5, 2026-10-25); a lead on the bisector, then straight off the map, the fall's bearings before the heading's and the near junctions before the wide
fn searched(inp: &SinkIn, out: Pt, head: Pt) -> Vec<Vec<Pt>> {
    let fall_deg = inp.fall.1.atan2(inp.fall.0).to_degrees();
    let head_deg = head.1.atan2(head.0).to_degrees();
    let mut order: Vec<(f64, f64, f64)> = Vec::new();
    for &sw in &SWINGS {
        for base in [fall_deg, head_deg] {
            for &j in &JUNCTIONS.0 {
                order.push((base, sw, j));
            }
        }
    }
    for &j in &JUNCTIONS.1 {
        for &sw in &SWINGS {
            for base in [fall_deg, head_deg] {
                order.push((base, sw, j));
            }
        }
    }
    order
        .into_iter()
        .map(|(base, sw, j)| {
            let th = (base + sw).to_radians();
            let (c, s) = (th.cos(), th.sin());
            let (bx, by) = (head.0 + c, head.1 + s);
            let bn = (bx * bx + by * by).sqrt().max(1e-9);
            let mid = (out.0 + bx / bn * j, out.1 + by / bn * j);
            let span = |v: f64, d: f64, edge: f64| {
                if d.abs() > 1e-6 {
                    ((if d > 0.0 { edge } else { 0.0 }) - v) / d
                } else {
                    f64::INFINITY
                }
            };
            let run = span(mid.0, c, inp.canvas.0)
                .min(span(mid.1, s, inp.canvas.1))
                .max(OFF_CANVAS.1)
                + OFF_CANVAS.0;
            vec![out, mid, (mid.0 + c * run, mid.1 + s * run)]
        })
        .collect()
}

/// The off-map sink: the confluence where one is found, else the first searched run that keeps every rule - refused by name where
/// none does.
///
/// # Errors
/// `SinkRefused` where no searched run keeps every rule.
///
/// Research:
///     the drain joins the passing brook - research/questions/0060-field-drains-akusuiro.drawing.html: "Where the passing brook comes near the collector's outfall, the drain joins it, as a district's drainage returned to the river to be taken up below"
///     else off the map - research/questions/0060-field-drains-akusuiro.drawing.html: "where it does not, the drain runs on as a ditch to the edge of the map"
///     the run to the brook bowed - GUESS: no source could speak to it, a value of ours; bowed off its chord as the pond's ditch is (`pond::BOW`)
pub fn lay(
    inp: &SinkIn,
    crop: &Crop,
    brook: &mut Brook,
    out: Pt,
    head: Pt,
    counts: &mut HashMap<String, u64>,
) -> Result<Sunk, SinkRefused> {
    let mut tests = 0;
    let found = confluence(inp, crop, brook, out, &mut tests);
    if let Some(q) = found {
        let bow = (super::pond::BOW.0 * dist(out, q)).min(super::pond::BOW.1);
        let run = vec![
            out,
            (
                f64::midpoint(out.0, q.0) - inp.fall.1 * bow,
                f64::midpoint(out.1, q.1) + inp.fall.0 * bow,
            ),
            q,
        ];
        if off_resting(
            &run,
            &inp.resting,
            inp.run_w,
            crop.holds_low(out, &mut tests),
            &mut tests,
        ) {
            tally(counts, "test@offmap", tests);
            tally(counts, "write@run", 3);
            return Ok(Sunk {
                form: "offmap",
                run,
                to: "stream",
                confluence: Some(q),
                ..Sunk::default()
            });
        }
    }
    let start = BACK_OFF
        .iter()
        .map(|&b| (out.0 - head.0 * b, out.1 - head.1 * b))
        .find(|&p| crop.holds(p, &mut tests))
        .unwrap_or(out);
    let anchored = crop.holds(start, &mut tests);
    let mut tried = 0;
    for run in searched(inp, start, head) {
        tried += 1;
        if keeps(inp, crop, brook, &run, head, anchored, &mut tests) {
            tally(counts, "candidate@offmap_run", tried);
            tally(counts, "test@offmap", tests);
            tally(counts, "write@run", 3);
            return Ok(Sunk {
                form: "offmap",
                run,
                to: "offmap",
                ..Sunk::default()
            });
        }
    }
    tally(counts, "candidate@offmap_run", tried);
    tally(counts, "test@offmap", tests);
    // where none keeps every rule the sink refuses: the remedy is a finer `SWINGS` or a longer run, never a route constructed round
    // the field (the round arbiter, ask:444-T26-constructed-turn)
    Err(SinkRefused(
        "no searched run off the map keeps every rule of the drain".to_owned(),
    ))
}
