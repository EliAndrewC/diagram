//! A scattered hamlet's rounds (feature 444 T30, from `homesteads/stages.py` `_seat_households_as`, `rank_rounds.py` and
//! `capacity.py`): its front row along the facing chains, each seat turned and pushed off the other ground; then - unless its farms
//! stand in single file round the fields - its ranks behind the row in a brick, the rescue rounds and their cloud, and every free
//! point of the ground nearest the seat first. The offers are `grove_seat.rs`'s.
//!
//! The front row's dead ends, carried from the Python stage it replaced (settlement-review, Inashiro, 2026-08-17) so they are not
//! tried again: TIGHTENING THE BAND is wrong - dropping the row's `bound * 1.3` allowance to `bound` made Inashiro's house-to-lane
//! median worse (109 to 158 ft) and Mizuguchi's (65 to 93): a row that cannot follow the field outline loses its seats to the cloud,
//! which sits further from the tracks still. A CAP, NOT A LADDER: offering the standoff ladder twice, capped then uncapped, moved no
//! median (the uncapped pass seated the houses the cap refused). And ONE COMPUTED RUNG for the standoff (feature 227 FR-002), never a
//! ladder of them: a rung of one house depth seated nobody on Kuwabata's dike heads and the cluster drifted 112 ft off its field.
//!
//! Research:
//!     a scattered hamlet's seating - research/questions/0031-clustered-and-scattered-villages-shuson-sanson.drawing.html: a front row along the paddy's chords, ranks behind in a brick pattern (off the line only on an alleys hamlet), a rescue cloud, then the exhaustive pass
//!     the front row's size - research/questions/0031-clustered-and-scattered-villages-shuson-sanson.drawing.html: the square root of the households times the rolled shape's aspect band, at least 6, ranks seated behind it
//!     the line's step - research/questions/0031-clustered-and-scattered-villages-shuson-sanson.drawing.html: each homestead with its own grove keeps its own spacing - the line's farms one farmstead's own box apart
//!     the seating's reach - GUESS: searched, the record silent on how far a hamlet of 10-20 households spread (feature 417 T29 pass F, 2026-10-25); a front-row seat within 1.3 times the band's reach of the seat center
//!     rank jitter and the cloud's lean - GUESS: no source gives the figures, (feature 417 T29 pass E2, 2026-10-25); seats nudged up to a tenth of a pitch along the band; the cloud leaned toward the field at 0.75
//!     rank depth jitter's size - GUESS: no source gives the size, (feature 417 T29 pass E2, 2026-10-25); a rank seat moved up to half of a quarter pitch nearer or farther, on an alleys hamlet, in the rounds before the rescue

use super::bundle::{grove_bundle, Bundle, Lot, Sun};
use super::fit::Placed;
use super::grove_seat::{
    cluster_seeds, drawn_aspect, front_row, ground_push, row_span, turned_reach, GroveSite, SEAT,
};
use super::layout::hjit;
use super::place::{field_distance, Seating};
use crate::field::fan::Pt;
use crate::field::geom::dist;
use crate::pyrand::PyRandom;

impl Seating {
    /// A grove farm stands: filed among the standing homesteads with its bands, seated, reached by a way of its own.
    pub fn stand_grove(&mut self, seat: Pt, b: Bundle) {
        let placed = Placed {
            house: (b.house, b.turn),
            house_box: b.boxes[0],
            yard: b.boxes[1],
            beds: b.boxes[2..2 + b.gardens.len()].to_vec(),
            bbox: b.bbox,
            persimmon: super::fit_rules::persimmon_of(&b),
            groves: b.groves.iter().map(|g| g.0).collect(),
        };
        self.standing.add(placed, &mut self.tests);
        let lot = self.seated.len();
        self.seated.push(super::place::Seated {
            lot,
            seat,
            bundle: b,
            wood: Vec::new(),
            passage: None,
        });
        self.depth.push(Some(0));
    }

    /// The bundle of the largest house the roll can take at `at`, unturned where `turn` is 0, no fixtures laid - the box a seat is
    /// pushed and the ranks stepped by (`_bundle_envelope` at the largest house).
    pub(crate) fn largest(&mut self, gs: &GroveSite, at: Pt, turn: Option<f64>) -> Bundle {
        let site = gs.site;
        let rot = turn.unwrap_or_else(|| {
            super::bearing::house_rot(
                at,
                site.bearing.1,
                site.bearing.0.follow(at, &mut self.tests),
            )
        });
        let lot = Lot {
            house: gs.house_max,
            kura: false,
            byre: None,
            fixtures: Vec::new(),
        };
        let sun = Sun {
            shade: site.shade,
            turns: &[rot],
        };
        grove_bundle(
            &lot,
            at,
            at,
            rot,
            site.forms,
            &sun,
            &gs.grove,
            &mut self.tests,
        )
    }
}

/// A scattered hamlet's households seated (`stages._seat_households_as`'s scattered branch): the front row, then - off the single
/// file - the ranks and the rescue, then the exhaustive pass. The seating; fewer seated than wanted where the ground is full.
#[must_use]
#[expect(
    clippy::cast_possible_truncation,
    clippy::cast_sign_loss,
    clippy::cast_precision_loss,
    reason = "a front row of a few dozen seats"
)]
pub fn seat_scattered(gs: &GroveSite) -> Seating {
    let mut st = Seating::default();
    let ax = gs.axes;
    // the front row: its size from the rolled shape's aspect band; each seat at the largest farmstead's core reach off its chord
    let g0 = st.largest(gs, (0.0, 0.0), Some(0.0));
    let core_parts: Vec<_> = std::iter::once(g0.house)
        .chain([g0.yard])
        .chain(g0.well)
        .collect();
    let core = super::bundle::bbox_of(&core_parts);
    let reach_core = (
        core.0 - core.2 / 2.0,
        core.1 - core.3 / 2.0,
        core.0 + core.2 / 2.0,
        core.1 + core.3 / 2.0,
    );
    let (lo, hi) = drawn_aspect(gs.shape);
    let n = gs.want;
    let front_cap = if gs.single_file {
        n
    } else {
        n.min(6usize.max(((n as f64) * (lo + hi)).sqrt().round_ties_even() as usize))
    };
    let (pitch, reach) = if gs.single_file {
        (g0.bbox.2.max(g0.bbox.3), f64::INFINITY)
    } else {
        (SEAT.0, ax.lat * row_span(gs.shape))
    };
    for (q, nrm) in front_row(gs.chains, &ax, reach_core, pitch, reach) {
        if st.seated.len() >= front_cap {
            break;
        }
        let toward = (-nrm.0, -nrm.1);
        let base = turned_reach(reach_core, 0.0, toward);
        let (mut extra, mut at): (f64, Pt) = (0.0, q);
        for _ in 0..2 {
            let rot = super::bearing::house_rot(
                at,
                gs.site.bearing.1,
                gs.site.bearing.0.follow(at, &mut st.tests),
            );
            extra = extra.max(turned_reach(reach_core, rot, toward) - base);
            at = (q.0 + nrm.0 * extra, q.1 + nrm.1 * extra);
        }
        let bx = st.largest(gs, at, None).bbox;
        let (pushed, by_water) = ground_push(at, nrm, bx, gs.corridors, &mut st.tests);
        let mut tries = vec![pushed];
        if by_water {
            tries.extend(
                [SEAT.0 / 4.0, -SEAT.0 / 4.0].map(|d| (pushed.0 - nrm.1 * d, pushed.1 + nrm.0 * d)),
            );
        }
        for t in tries {
            if (gs.single_file || dist(t, ax.c) <= gs.bound * 1.3) && st.offer_grove(gs, t.0, t.1) {
                break;
            }
        }
    }
    if !gs.single_file {
        rank_rounds(gs, &mut st);
        seat_the_rest(gs, &mut st);
    }
    st
}

/// The ranks behind the front row and the rescue rounds (`rank_rounds._seat_rank_rounds`).
#[expect(
    clippy::too_many_lines,
    reason = "the rounds' one loop, as the seating runs it"
)]
fn rank_rounds(gs: &GroveSite, st: &mut Seating) {
    let ax = gs.axes;
    let (along, out, c) = (ax.along, ax.out, ax.c);
    let pitch = SEAT.0;
    let row: Vec<Pt> = st
        .seated
        .iter()
        .map(|s| (s.bundle.house.0, s.bundle.house.1))
        .collect();
    let env = st.largest(gs, c, None).bbox;
    let step = out.0.abs() * env.2 + out.1.abs() * env.3 + SEAT.4.max(out.1.abs() * SEAT.5);
    let mut rng = PyRandom::new((gs.seed.unsigned_abs().wrapping_mul(2_654_435_761)) & 0xFFFF_FFFF);
    let a_of = |q: Pt| (q.0 - c.0) * along.0 + (q.1 - c.1) * along.1;
    let o_of = |q: Pt| (q.0 - c.0) * out.0 + (q.1 - c.1) * out.1;
    for attempt in 0..7 {
        if st.seated.len() >= gs.want {
            break;
        }
        let (wlat, wdep) = (
            gs.band.0 * (1.0 + 0.22 * f64::from(attempt)),
            gs.band.1 * (1.0 + 0.16 * f64::from(attempt)),
        );
        let standing: Vec<Pt> = st
            .seated
            .iter()
            .map(|s| (s.bundle.house.0, s.bundle.house.1))
            .collect();
        let (cands, ends) = if attempt < 4 && !standing.is_empty() {
            let mut sorted = standing.clone();
            sorted.sort_by(|p, q| a_of(*p).total_cmp(&a_of(*q)));
            let row_out = if row.is_empty() { &standing } else { &row }
                .iter()
                .map(|&q| o_of(q))
                .fold(f64::INFINITY, f64::min);
            let depth = row_out + step * f64::from(attempt + 1);
            let seat_at = |u: f64| {
                (
                    c.0 + along.0 * u + out.0 * depth,
                    c.1 + along.1 * u + out.1 * depth,
                )
            };
            let us: Vec<f64> = sorted.iter().map(|&q| a_of(q)).collect();
            let (first, last) = (sorted[0], sorted[sorted.len() - 1]);
            let mut ends = vec![
                (first.0 - along.0 * pitch, first.1 - along.1 * pitch),
                (last.0 + along.0 * pitch, last.1 + along.1 * pitch),
            ];
            let mut cands: Vec<Pt> = if attempt % 2 == 0 {
                ends.extend([
                    seat_at(us[0] - pitch / 2.0),
                    seat_at(us[us.len() - 1] + pitch / 2.0),
                ]);
                us.windows(2)
                    .map(|w| seat_at(f64::midpoint(w[0], w[1])))
                    .collect()
            } else {
                us.iter().map(|&u| seat_at(u)).collect()
            };
            cands.sort_by(|p, q| dist(*p, c).total_cmp(&dist(*q, c)));
            if attempt == 0 {
                let gaps: Vec<Pt> = sorted
                    .windows(2)
                    .filter(|w| dist(w[0], w[1]) > pitch * 1.45)
                    .map(|w| (f64::midpoint(w[0].0, w[1].0), f64::midpoint(w[0].1, w[1].1)))
                    .collect();
                cands = gaps.into_iter().chain(cands).collect();
            }
            (cands, ends)
        } else {
            let mut cands = Vec::new();
            if !standing.is_empty() {
                let mut sorted = standing.clone();
                sorted.sort_by(|p, q| a_of(*p).total_cmp(&a_of(*q)));
                let (first, last) = (sorted[0], sorted[sorted.len() - 1]);
                cands = vec![
                    (first.0 - along.0 * pitch, first.1 - along.1 * pitch),
                    (last.0 + along.0 * pitch, last.1 + along.1 * pitch),
                    (
                        first.0 - along.0 * pitch / 2.0 + out.0 * step,
                        first.1 - along.1 * pitch / 2.0 + out.1 * step,
                    ),
                    (
                        last.0 + along.0 * pitch / 2.0 + out.0 * step,
                        last.1 + along.1 * pitch / 2.0 + out.1 * step,
                    ),
                ];
            }
            for (lx, ly) in cluster_seeds(gs.shape, wlat, wdep, gs.want * 6 + 30, &mut rng) {
                let ly = -wdep + (ly + wdep) * 0.75;
                cands.push((
                    c.0 + along.0 * lx + out.0 * ly,
                    c.1 + along.1 * lx + out.1 * ly,
                ));
            }
            (cands, Vec::new())
        };
        let before = st.seated.len();
        let mut kept: Vec<Pt> = Vec::new();
        let (mut offered, mut along_field) = (cands, false);
        loop {
            for q in offered.iter().map(|&q| {
                let j = (hjit(q.0, q.1, 13.0) - 0.5) * pitch * 0.2;
                (q.0 + along.0 * j, q.1 + along.1 * j)
            }) {
                if st.seated.len() >= gs.want {
                    break;
                }
                if attempt >= 4 && dist(q, c) > gs.bound {
                    continue;
                }
                let same = pitch * if attempt < 4 { 0.5 } else { 0.3 };
                if kept.iter().any(|&k| dist(q, k) < same)
                    || st
                        .seated
                        .iter()
                        .any(|s| dist(q, (s.bundle.house.0, s.bundle.house.1)) < pitch * 0.5)
                {
                    continue;
                }
                kept.push(q);
                let dj = if attempt < 4 && !along_field && gs.alleys {
                    (hjit(q.0, q.1, 14.0) - 0.5) * pitch * 0.25
                } else {
                    0.0
                };
                let tries: Vec<Pt> = if dj == 0.0 {
                    vec![q]
                } else {
                    vec![(q.0 + out.0 * dj, q.1 + out.1 * dj), q]
                };
                for t in tries {
                    if st.offer_grove(gs, t.0, t.1) {
                        break;
                    }
                }
            }
            if along_field
                || !(attempt < 4
                    && !standing.is_empty()
                    && st.seated.len() == before
                    && st.seated.len() < gs.want)
            {
                break;
            }
            offered.clone_from(&ends);
            along_field = true;
        }
    }
}

/// The exhaustive pass (`capacity.seat_the_rest`): every free grid point of the ground a third of a pitch apart, nearest the seat first
/// within a pitch's ring and nearer the field breaking ties, offered until every household stands or 400 offers in a row seat none.
#[expect(
    clippy::cast_possible_truncation,
    clippy::cast_sign_loss,
    clippy::cast_precision_loss,
    reason = "a grid of a few hundred points a side"
)]
fn seat_the_rest(gs: &GroveSite, st: &mut Seating) {
    if st.seated.len() >= gs.want {
        return;
    }
    let site = gs.site;
    let (pitch, inset, dry) = (SEAT.0 / 3.0, 6.0, 400);
    let (ni, nj) = (
        ((site.canvas.0 - 2.0 * inset) / pitch) as usize + 1,
        ((site.canvas.1 - 2.0 * inset) / pitch) as usize + 1,
    );
    let mut grid: Vec<(i64, f64, f64, f64, Pt)> = Vec::new();
    for i in 0..ni {
        for j in 0..nj {
            let q = (inset + i as f64 * pitch, inset + j as f64 * pitch);
            st.tests.add("candidate@seat_the_rest", 1);
            if site.ground.taken_at(q).unwrap_or_else(|| (site.beyond)(q))
                || st
                    .seated
                    .iter()
                    .any(|s| dist(q, (s.bundle.house.0, s.bundle.house.1)) < SEAT.0 * 0.5)
            {
                continue;
            }
            let ring = (dist(q, gs.axes.c) / pitch).round_ties_even() as i64;
            grid.push((ring, field_distance(q, site.field), q.0, q.1, q));
        }
    }
    grid.sort_by(|a, b| {
        a.0.cmp(&b.0)
            .then(a.1.total_cmp(&b.1))
            .then(a.2.total_cmp(&b.2))
            .then(a.3.total_cmp(&b.3))
    });
    let (mut since, mut left) = (0, grid.into_iter());
    // ...until every household stands or the dry spell ends it
    while let Some((.., q)) = (st.seated.len() < gs.want && since < dry)
        .then(|| left.next())
        .flatten()
    {
        if st
            .seated
            .iter()
            .any(|s| dist(q, (s.bundle.house.0, s.bundle.house.1)) < SEAT.6)
        {
            continue;
        }
        since += 1;
        if st.offer_grove(gs, q.0, q.1) {
            since = 0;
        }
    }
}
