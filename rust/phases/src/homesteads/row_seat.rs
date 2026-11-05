//! A row village's farms seated along its streets (feature 444 T30, `rows.py` `seat_rows`): the first street on the stretch of the
//! hard ground's edge that holds the most clear frames, the further streets set out parallel past its far row and their holdings,
//! each seat offered once to the placer at the frame's own house offset, exact, while every planned street's tread is reserved.
//!
//! Research:
//!     row farm faces its street - DEVIATION research/questions/0033-row-villages-resson.drawing.html: the page draws only the first of the two attested forms; never turned to its street - every frame keeps the settlement's one windward orientation (grove to windward, open front to lee) on either side of the street, so only the grove-to-windward form is drawn
//!     far-row dry-field share - research/questions/0033-row-villages-resson.html, research/questions/0033-row-villages-resson.drawing.html: each far-row farm's holding one lot wide and `HOLDING_DEPTH_FRAMES` lots deep, all dry field; the near row and a one-sided row hold none
//!     far-row farm only with its holding - research/questions/0033-row-villages-resson.drawing.html: a far-row seat whose holding does not fit clear is passed over
//!     farms to a street - research/questions/0033-row-villages-resson.drawing.html: a full street gets a further street set out parallel beside it, never a second row behind
//!     farms one frame apart, never more than 240 ft - research/questions/0033-row-villages-resson.drawing.html: the row steps one frame, `lot = min(fw, ROW_FRONTAGE_MAX_FT)`
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
//!     its street run - GUESS: searched, the record silent (feature 417 T38, 2026-10-25) - the street laid one lot longer than its row, with two lots of slack, kept half a frame inside the sheet
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
    best_row_line, frame_extent, frame_refused, holding_clear, holding_quad, inside_the_sheet,
    parallel, row_offsets, row_seats, street_bend_radius_ft, Form, Frames, FIELD_KEEP_FT,
    HOLDING_DEPTH_FRAMES, MAX_STREETS, ROW_FRONTAGE_MAX_FT, STREET_HALF_FT,
};
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
}

/// Seat a row village's farms (`rows.seat_rows`).
#[must_use]
#[expect(
    clippy::too_many_lines,
    reason = "the row's one loop, as `seat_rows` runs it"
)]
pub fn seat_rows(rs: &RowSite) -> Rows {
    let mut out = Rows::default();
    let gs0 = &rs.gs;
    let want = gs0.want;
    let per_line = want.div_ceil(if rs.both { 2 } else { 1 });
    let gap = STREET_HALF_FT.0 + FIELD_KEEP_FT / 2.0;
    let frame = out.seating.largest(gs0, (0.0, 0.0), Some(0.0)).bbox;
    let (fw, fd) = (frame.2.max(frame.3), frame.2.min(frame.3));
    let lot = fw.min(ROW_FRONTAGE_MAX_FT);
    let (hx_off, hy_off) = (frame.0, frame.1);
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
        pitch: lot,
    };
    let tests = &mut out.seating.tests;
    // WHERE THE ROW GOES: the stretch of the hard ground's edge whose line holds the most clear frames
    let first_off = row_offsets(fd, rs.both, 1, FIELD_KEEP_FT, gap, 0.0)[0];
    let first = best_row_line(
        rs.hard,
        rs.anchor,
        (first_off, per_line as f64 * lot + lot, 2.0 * lot),
        rs.form,
        &fr,
        tests,
    );
    // ...and the streets beyond it set out by the frame's depth along the line's normal (cohort seed 901)
    let depth_n = first
        .iter()
        .map(|&(_, n)| frame_extent(frame, n))
        .reduce(f64::max)
        .unwrap_or(fd);
    let offsets = row_offsets(
        depth_n,
        rs.both,
        MAX_STREETS,
        FIELD_KEEP_FT,
        gap,
        hold_depth + gap,
    );
    let planned: Vec<_> = offsets
        .iter()
        .map(|o| parallel(&first, o - offsets[0], street_bend_radius_ft(), tests))
        .collect();
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
    for line in &planned {
        if st.seated.len() >= want {
            break;
        }
        // ...its stretch inside the sheet by half a frame
        let line = inside_the_sheet(line, (fd / 2.0, fd / 2.0, w - fd / 2.0, h - fd / 2.0));
        let mut mine: Vec<Pt> = Vec::new();
        let seats = row_seats(&line, frame, rs.both, gap, lot)
            .into_iter()
            .filter(|&((fx, fy), ..)| {
                0.0 < fx - hx_off && fx - hx_off < w && 0.0 < fy - hy_off && fy - hy_off < h
            });
        for ((fx, fy), side, t, nrm) in seats {
            st.tests.add("candidate@seat_rows", 1);
            if st.seated.len() >= want {
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
                    .collect();
                hold = holding_clear(
                    &holding_quad(hc, t, nrm, lot, hold_depth),
                    rs.hard,
                    &boxes,
                    bounds,
                    &mut st.tests,
                );
                if hold.is_none() {
                    continue;
                }
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
