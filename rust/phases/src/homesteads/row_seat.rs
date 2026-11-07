//! A row village's farms seated along its streets (feature 444 T30, `rows.py` `seat_rows`): the first street on the stretch of the
//! hard ground's edge that holds the most clear frames, the further streets set out parallel past its far row and their holdings,
//! each seat offered once to the placer at the frame's own house offset, exact, while every planned street's tread is reserved.
//!
//! Research:
//!     row farm faces its street - DEVIATION research/questions/0033-row-villages-resson.drawing.html: the page draws only the first of the two attested forms; never turned to its street - every frame keeps the settlement's one windward orientation (grove to windward, open front to lee) on either side of the street, so only the grove-to-windward form is drawn
//!     far-row dry-field share - research/questions/0033-row-villages-resson.html, research/questions/0033-row-villages-resson.drawing.html: each far-row farm's holding one lot wide and `HOLDING_DEPTH_FRAMES` lots deep, all dry field; the near row and a one-sided row hold none
//!     far-row farm only with its holding - research/questions/0033-row-villages-resson.drawing.html: a far-row seat whose holding does not fit clear is passed over
//!     farms to a street - research/questions/0033-row-villages-resson.drawing.html: a full street gets a further street set out parallel beside it, never a second row behind
//!     farms one frame apart, the holding never more than 240 ft - research/questions/0033-row-villages-resson.drawing.html: the row steps one frame along its street (`row_step`, the frame's reach), its holding one lot wide, never past Santome's 240 ft lots
//!     the next street past the last one's holdings - research/questions/0033-row-villages-resson.drawing.html: each further street is set out past the last street's frames and their holdings
//!     holding set behind its frame - GUESS: searched, the record silent (feature 417 T29 pass B, 2026-10-25); the strip starts half the 15 ft gap (7.5 ft) behind its farm's frame
//!     at most `MAX_STREETS` (6) parallel streets - research/questions/0033-row-villages-resson.drawing.html: six parallel streets at most
//!     front door's ground: a frame refused without `DOOR_ROOM_FT` (16 ft) and half `LANE_ROOM_FT` clear before its front - GUESS: searched, the record silent (feature 417 T29 pass B, 2026-10-25); the 16 ft door room
//!     frame off the street - GUESS: searched, the record silent (feature 417 T29 pass B, 2026-10-25); half the street plus half `FIELD_KEEP_FT`, 15 ft off its centerline
//!     first street on the hard ground's edge - research/questions/0033-row-villages-resson.drawing.html: the first street runs along the stretch of the hard ground's edge that holds the most clear frames (`best_row_line`)
//!     streets rounded at a corner - GUESS: no source could speak to it, a value of ours (feature 417 T29 pass B, 2026-10-25); a street is rounded on the inside of a corner at `street_bend_radius_ft`
//!     the leeward row marked sheltered - research/questions/0033-row-villages-resson.drawing.html: on a street with farms on both sides, where the settlement rolled the sheltered form, a farm with its street and the grove row beyond it to windward is seated as a full farm and marked `sheltered`
//!     a street across the wind - GUESS: within 67.5 degrees of the farm's windward bearing; no page gives an angle
//!     its drawn sizes - CONVENTION: sizes on the sheet, not in the world - 30 (holdings clipped 30 px inside the sheet)
//!     its street run - GUESS: searched, the record silent (feature 417 T38, 2026-10-25) - the street laid one lot longer than its row, with a row's length of slack (where no street of that length has room for every farm, one laid twice as long, its room asked before any farm stands), kept half a frame inside the sheet (two lots of slack, the Python's, left a row against the sheet one farm short: the Rust stage gate's seed 729966, 18 of 19); where that row falls short of the households, the row is seated too on the street Python chose - two lots of slack, ranked by its own clear frames - and the one seating more kept (seed 290494: 14 of 19 on the first, 19 on Python's)
//!     street tread reserved - research/questions/0081-village-lanes.drawing.html: a way's corridor kept clear of built and worked ground while its farms are seated; released when the row is seated

#![expect(
    clippy::cast_precision_loss,
    clippy::similar_names,
    reason = "a row of a few dozen farms; the frame's two offsets, the holdings held and the one being laid"
)]

use super::grove_seat::GroveSite;
use super::level::Hard;
use super::place::Seating;
use super::rows::{
    clear_frames, frame_extent, frame_refused, holding_clear, holding_quad, inside_the_sheet,
    parallel, row_lines, row_offsets, row_seats, row_step, street_bend_radius_ft, Form, Frames,
    FIELD_KEEP_FT, HOLDING_DEPTH_FRAMES, MAX_STREETS, ROW_FRONTAGE_MAX_FT, STREET_HALF_FT,
};
use super::Counts;
use crate::field::fan::Pt;

/// Half a lane's room before a farm's front door (`LANE_ROOM_FT` / 2).
///
/// Research:
///     lane room - research/questions/0081-village-lanes.drawing.html: 32 ft of lane room, half of it before the door
const LANE_PAD_FT: f64 = 32.0 / 2.0;

/// A street within 67.5 degrees of the farm's windward bearing shelters it.
fn sheltered_by_the_row_across(side: i32, normal: Pt, wind: Pt) -> bool {
    -f64::from(side) * (normal.0 * wind.0 + normal.1 * wind.1) > 67.5_f64.to_radians().cos()
}

/// What a row village is seated on beyond its grove farms' site: the hard ground, the planned seat, the line's form and sides, the
/// sheltered form's roll and the wind, the farms' front face, and the sheet.
#[derive(Clone, Copy)]
pub struct RowSite<'a> {
    /// The grove farms' site (its `streets` filled here).
    pub gs: GroveSite<'a>,
    /// The ground a row may not stand on.
    pub hard: &'a Hard,
    /// The planned seat's point.
    pub anchor: Pt,
    /// Both sides of the street, or the far side only?
    pub both: bool,
    /// A street laid first, or the dry edge.
    pub form: Form,
    /// Did the settlement roll the sheltered leeward row, and the wind's vector.
    pub shelter: (bool, Pt),
    /// The face a farm's grove leaves open, where its way in is (a page direction).
    pub front: Pt,
    /// The sheet (its width and height).
    pub sheet: (f64, f64),
}

/// A row village seated: the seating, each street that seated a farm (its points on the sheet) with its farms' houses, each holding
/// reserved (its ring, the street's tangent and normal at its farm, its depth, its farm's lot), and each seated farm's sheltered mark.
#[derive(Default)]
pub struct Rows {
    /// The seating.
    pub seating: Seating,
    /// The streets that seated a farm, and the houses of each one's farms.
    pub streets: Vec<(Vec<Pt>, Vec<Pt>)>,
    /// The holdings: (ring, tangent, normal, depth, lot).
    pub holdings: Vec<(Vec<Pt>, Pt, Pt, f64, usize)>,
    /// Each seated farm's sheltered mark.
    pub sheltered: Vec<bool>,
    /// Asked only (`seat_along`'s `ask_only`): the farms the row's frames admit, every rule asked and none stood.
    pub room: usize,
}

/// A row's streets: `first` and the streets set out parallel beside it, each past the last street's far row (its holdings with it,
/// on both sides) and a lane's room, by the frame's depth along the line's normal (cohort seed 901: on a diagonal street a frame
/// reaches deeper), each rounded on the inside of a corner.
fn planned_streets(
    first: &[(Pt, Pt)],
    frame: super::layout::Rect,
    rows: (bool, f64, f64),
    tests: &mut Counts,
) -> Vec<super::rows::Line> {
    let offsets = street_offsets(first, frame, rows);
    offsets
        .iter()
        .map(|o| parallel(first, o - offsets[0], street_bend_radius_ft(), tests))
        .collect()
}

/// How far each of a row's streets stands out from `first` (`planned_streets`), the first's own offset first.
fn street_offsets(
    first: &[(Pt, Pt)],
    frame: super::layout::Rect,
    (both, gap, hold_depth): (bool, f64, f64),
) -> Vec<f64> {
    let depth_n = first
        .iter()
        .map(|&(_, n)| frame_extent(frame, n))
        .reduce(f64::max)
        .unwrap_or_else(|| frame.2.min(frame.3));
    row_offsets(
        depth_n,
        both,
        MAX_STREETS,
        FIELD_KEEP_FT,
        gap,
        hold_depth + gap,
    )
}

/// Seat a row village's farms (`rows.seat_rows`).
#[must_use]
pub fn seat_rows(rs: &RowSite) -> Rows {
    seat_rows_as(rs, false)
}

/// The farms a row village's frames admit on its seat, every rule asked and none stood: the larger room of its first streets
/// (`seat_rows`' choice), for the seating to choose its margin before any house stands (feature 444 T31, S4).
#[must_use]
pub fn row_room(rs: &RowSite) -> Rows {
    seat_rows_as(rs, true)
}

/// `seat_rows`, or - `ask_only` - its room alone (`Rows::room`, the street chosen's), nothing seated.
#[expect(
    clippy::too_many_lines,
    reason = "the row's setup and its first streets' rooms asked in the one order the seating reads them"
)]
fn seat_rows_as(rs: &RowSite, ask_only: bool) -> Rows {
    let mut out = Rows::default();
    let gs0 = &rs.gs;
    let want = gs0.want;
    let per_line = want.div_ceil(if rs.both { 2 } else { 1 });
    let gap = STREET_HALF_FT.0 + FIELD_KEEP_FT / 2.0;
    let frame = out.seating.largest(gs0, (0.0, 0.0), Some(0.0)).bbox;
    let (fw, fd) = (frame.2.max(frame.3), frame.2.min(frame.3));
    let lot = fw.min(ROW_FRONTAGE_MAX_FT);
    let hold_depth = lot
        * if rs.form == Form::Street {
            HOLDING_DEPTH_FRAMES.0
        } else {
            HOLDING_DEPTH_FRAMES.1
        };
    let (w, h) = rs.sheet;
    let bounds = (30.0, 30.0, w - 30.0, h - 30.0);
    let fr = Frames {
        frame,
        both: rs.both,
        gap,
        bounds,
        door: (rs.front, LANE_PAD_FT, super::rows::DOOR_FT.1),
    };
    let tests = &mut out.seating.tests;
    // WHERE THE ROW GOES: the stretch of the hard ground's edge whose whole row - its street and the streets set out beside it, each
    // on the sheet - holds the most farms, up to the households wanted
    let first_off = row_offsets(fd, rs.both, 1, FIELD_KEEP_FT, gap, 0.0)[0];
    let sheet = (fd / 2.0, fd / 2.0, w - fd / 2.0, h - fd / 2.0);
    // ...EACH STREET SET OUT ONLY WHILE THE ROW STILL HOLDS FEWER THAN THE HOUSEHOLDS WANTED (the GM 2026-11-07: "the literal most
    // important thing here is making things FAST"): all six were set out for every stretch asked, most never read
    let capacity = |first: &[(Pt, Pt)], tests: &mut Counts| {
        let offsets = street_offsets(first, frame, (rs.both, gap, hold_depth));
        let mut held = 0;
        for o in &offsets {
            let line = parallel(first, o - offsets[0], street_bend_radius_ft(), tests);
            held += clear_frames(&inside_the_sheet(&line, sheet), &fr, rs.hard, tests);
            if held >= want {
                break;
            }
        }
        held.min(want)
    };
    let (by_row, _) = row_lines(
        rs.hard,
        rs.anchor,
        (
            first_off,
            per_line as f64 * lot + lot,
            per_line as f64 * lot,
        ),
        rs.form,
        &fr,
        &capacity,
        tests,
    );
    let plan = Plan {
        frame,
        fr,
        hold_depth,
        gap,
        sheet,
    };
    // ...seated from the street its whole row ranks first, a row's length of slack; where that falls short of the households
    // wanted, from the street Python chose too - two lots of slack, ranked by its own clear frames - the row that seats more kept
    // (each count a promise the seating may not keep: the Rust stage gate's seed 729966 seated 18 of 19 on Python's street, seed
    // 290494 14 of 19 on the whole row's, all 19 on Python's)
    let tried = std::mem::take(&mut out.seating.tests);
    // ...THE ROW SEATED ONCE, along the street with the most room: the whole row's street, the street Python chose and one twice the
    // row's length on the same edge, each street's room asked before any farm stands (S4)
    let mut tries = vec![seat_along(rs, &by_row, &plan, true)];
    let mut lines = vec![by_row];
    {
        let (_, by_own) = row_lines(
            rs.hard,
            rs.anchor,
            (first_off, per_line as f64 * lot + lot, 2.0 * lot),
            rs.form,
            &fr,
            &capacity,
            &mut tries[0].seating.tests,
        );
        tries.push(seat_along(rs, &by_own, &plan, true));
        lines.push(by_own);
    }
    // ...AND WHERE BOTH FALL SHORT, ROOM FROM THE MARGIN'S LENGTH (the round arbiter on ask:444-T30-fresh-seed-refusals): the first
    // street laid twice the row's length along the same edge, its room asked as the others' (the Rust gate's seed 20104: every
    // margin's streets held 10 of 15, the further streets falling off the sheet; on the longer street, 15)
    {
        let (long, _) = row_lines(
            rs.hard,
            rs.anchor,
            (
                first_off,
                2.0 * (per_line as f64 * lot + lot),
                2.0 * per_line as f64 * lot,
            ),
            rs.form,
            &fr,
            &capacity,
            &mut tries[0].seating.tests,
        );
        tries.push(seat_along(rs, &long, &plan, true));
        lines.push(long);
    }
    // the first of the streets with the most room (the last maximum of the tries reversed), every ask's work counted
    let k = (0..tries.len())
        .rev()
        .max_by_key(|&i| tries[i].room)
        .unwrap_or(0);
    let room = tries[k].room;
    let mut got = if ask_only {
        Rows {
            room,
            ..Rows::default()
        }
    } else {
        seat_along(rs, &lines[k], &plan, false)
    };
    for (k, n) in tries.into_iter().flat_map(|t| t.seating.tests.0) {
        got.seating.tests.add(&k, n);
    }
    for (k, n) in tried.0 {
        got.seating.tests.add(&k, n);
    }
    got
}

/// What a row's seating along a first street reads beyond the site: the frame, its judgment, the holding's depth, the frame's gap off
/// the street and the sheet's inner bounds.
struct Plan {
    frame: super::layout::Rect,
    fr: Frames,
    hold_depth: f64,
    gap: f64,
    sheet: (f64, f64, f64, f64),
}

#[expect(
    clippy::too_many_lines,
    reason = "the row's one loop, as `seat_rows` runs it, its room asked by the same steps"
)]
/// The row's farms seated along `first` and the streets set out beside it; `ask_only`, its room counted instead - each frame
/// asked every rule a farm is seated by, the farms admitted counted (`Rows::room`), nothing stood (S4: every rule asked of a
/// candidate before it is placed; nothing placed is dropped).
fn seat_along(rs: &RowSite, first: &[(Pt, Pt)], plan: &Plan, ask_only: bool) -> Rows {
    let mut out = Rows::default();
    let gs0 = &rs.gs;
    let want = gs0.want;
    let Plan {
        frame,
        fr,
        hold_depth,
        gap,
        sheet,
    } = *plan;
    let (hx_off, hy_off) = (frame.0, frame.1);
    let (w, h) = rs.sheet;
    let bounds = fr.bounds;
    let tests = &mut out.seating.tests;
    let planned = planned_streets(first, frame, (rs.both, gap, hold_depth), tests);
    let all_streets: Vec<Vec<Pt>> = planned
        .iter()
        .filter(|l| l.len() >= 2)
        .map(|l| l.iter().map(|s| s.0).collect())
        .collect();
    // THE STREETS' TREAD IS RESERVED WHILE THEIR FARMS ARE SEATED: a part a farm lays is admitted only off every planned street's tread
    let tread: Vec<(Pt, Pt)> = planned
        .iter()
        .flat_map(|l| l.windows(2).map(|w| (w[0].0, w[1].0)))
        .collect();
    let gs = GroveSite {
        streets: (&tread, STREET_HALF_FT.0 + STREET_HALF_FT.1),
        ..*gs0
    };
    let st = &mut out.seating;
    let mut asked: Vec<super::layout::Rect> = Vec::new();
    for line in &planned {
        if st.seated.len().max(out.room) >= want {
            break;
        }
        // ...its stretch inside the sheet by half a frame
        let line = inside_the_sheet(line, sheet);
        let mut mine: Vec<Pt> = Vec::new();
        // ...one frame apart along the street, its holding one lot wide (the frame's reach, never past the 240 ft frontage)
        let step = row_step(&line, frame);
        let along = step.min(ROW_FRONTAGE_MAX_FT);
        let seats = one_reach(
            &line,
            row_seats(&line, frame, rs.both, gap, step)
                .into_iter()
                .filter(|&((fx, fy), ..)| {
                    0.0 < fx - hx_off && fx - hx_off < w && 0.0 < fy - hy_off && fy - hy_off < h
                })
                .collect(),
            (gs0.site.streams, rs.hard),
            &mut st.tests,
        );
        for ((fx, fy), side, t, nrm) in seats {
            st.tests.add("candidate@seat_rows", 1);
            if st.seated.len().max(out.room) >= want {
                break;
            }
            let held: Vec<Vec<Pt>> = out.holdings.iter().map(|q| q.0.clone()).collect();
            if frame_refused(
                (fx, fy, frame.2, frame.3),
                fr.door,
                rs.hard,
                &all_streets,
                &held,
                &mut st.tests,
            ) {
                continue;
            }
            // A FAR-ROW FARM IS SEATED ONLY WITH ITS HOLDING, behind its lot, clear of the hard ground and every reserved box
            let mut hold = None;
            if rs.both && side > 0 {
                let back = frame_extent(frame, nrm) / 2.0 + gap / 2.0 + hold_depth / 2.0;
                let hc = (fx + nrm.0 * back, fy + nrm.1 * back);
                let boxes: Vec<_> = gs
                    .site
                    .rules
                    .placed
                    .iter()
                    .copied()
                    .chain(st.seated.iter().map(|s| s.bundle.bbox))
                    .chain(asked.iter().copied())
                    .collect();
                hold = holding_clear(
                    &holding_quad(hc, t, nrm, along, hold_depth),
                    rs.hard,
                    &boxes,
                    bounds,
                    &mut st.tests,
                );
                if hold.is_none() {
                    continue;
                }
            }
            if ask_only {
                // ...the frames admitted so far held as their farms would hold them: each frame's box and its holding, so a later
                // frame is asked against them as against a seated farm's (nothing stands)
                if st.admits_grove_as(&gs, out.room, fx - hx_off, fy - hy_off) {
                    out.room += 1;
                    asked.push((fx, fy, frame.2, frame.3));
                    if let Some(q) = hold {
                        out.holdings.push((q, t, nrm, hold_depth, out.room - 1));
                    }
                }
                continue;
            }
            let shelter =
                rs.both && rs.shelter.0 && sheltered_by_the_row_across(side, nrm, rs.shelter.1);
            if !st.offer_grove_as(&gs, fx - hx_off, fy - hy_off, true) {
                continue;
            }
            out.sheltered.push(shelter);
            let b = &st.seated[st.seated.len() - 1].bundle;
            mine.push((b.house.0, b.house.1));
            if let Some(q) = hold {
                st.holdings.push(q.clone());
                out.holdings
                    .push((q, t, nrm, hold_depth, st.seated.len() - 1));
            }
        }
        if !mine.is_empty() {
            // all of it on the sheet (`inside_the_sheet` kept it half a frame in), where Python filters to the sheet's part
            out.streets.push((line.iter().map(|s| s.0).collect(), mine));
        }
    }
    out
}

/// The seats of one stretch of `line` between its crossings of the streams and the hard ground its tread meets - the stretch
/// holding the most, the first of a tie - so a street's farms stand on one bank and on one stretch of open ground, and the street
/// laid along its farms (`street.drawn_span`) crosses neither.
///
/// Research:
///     a row's farms on one stretch of its street - GUESS: no source could speak to it, a value of ours (feature 444 T32: cohort seed
///     3, a street laid twice its row's length ran on across its brook, a farm was seated on the far bank, and the street crossed the
///     brook between two crossing places; pinned row 901, a street's farms seated either side of the dry hem's plots, and the street
///     between them refused on the plots); the street's further stretch is laid as another street would be, never between its farms
#[expect(
    clippy::many_single_char_names,
    reason = "the plane geometry's own names"
)]
fn one_reach(
    line: &[(Pt, Pt)],
    seats: Vec<super::rows::Seat>,
    (streams, hard): (&[(Pt, Pt)], &Hard),
    tests: &mut Counts,
) -> Vec<super::rows::Seat> {
    use crate::field::geom::dist;
    use crate::ways::track::{seg_intersect, segments_cross};
    let mut arc = vec![0.0];
    for w in line.windows(2) {
        arc.push(arc[arc.len() - 1] + dist(w[0].0, w[1].0));
    }
    let mut cuts: Vec<f64> = Vec::new();
    for (k, w) in line.windows(2).enumerate() {
        let (a, b) = (w[0].0, w[1].0);
        tests.add("seg_test@one_reach", streams.len() as u64);
        for &(c, d) in streams {
            if segments_cross(a, b, c, d) {
                if let Some(x) = seg_intersect(a, b, c, d) {
                    cuts.push(arc[k] + dist(a, x));
                }
            }
        }
    }
    // ...and each run of the line's samples whose tread meets the hard ground, one cut at its start
    let half = STREET_HALF_FT.0 + STREET_HALF_FT.1;
    let mut on = false;
    for (k, &(p, _)) in line.iter().enumerate() {
        let hit = hard.dist(p, half, tests) < half;
        if hit && !on {
            cuts.push(arc[k]);
        }
        on = hit;
    }
    if cuts.is_empty() || seats.is_empty() {
        return seats;
    }
    // ...each seat's stretch by the arc of its nearest point on the line
    let reach_of = |p: Pt, tests: &mut Counts| {
        tests.add("pt_test@one_reach", (line.len() - 1) as u64);
        let (mut best, mut at) = (f64::INFINITY, 0.0);
        for (k, w) in line.windows(2).enumerate() {
            let (a, b) = (w[0].0, w[1].0);
            let (vx, vy) = (b.0 - a.0, b.1 - a.1);
            let l2 = vx * vx + vy * vy;
            // ...a point segment's own end: its dot product is 0, so any positive divisor gives 0
            let t =
                (((p.0 - a.0) * vx + (p.1 - a.1) * vy) / l2.max(f64::MIN_POSITIVE)).clamp(0.0, 1.0);
            let q = (a.0 + vx * t, a.1 + vy * t);
            let d = dist(p, q);
            if d < best {
                (best, at) = (d, arc[k] + t * l2.sqrt());
            }
        }
        cuts.iter().filter(|&&c| c < at).count()
    };
    let of: Vec<usize> = seats.iter().map(|s| reach_of(s.0, tests)).collect();
    let mut count = vec![0usize; cuts.len() + 1];
    for &r in &of {
        count[r] += 1;
    }
    let keep = (0..count.len())
        .max_by(|&i, &j| count[i].cmp(&count[j]).then(j.cmp(&i)))
        .unwrap_or(0);
    seats
        .into_iter()
        .zip(of)
        .filter(|&(_, r)| r == keep)
        .map(|(s, _)| s)
        .collect()
}
