//! The driver on a polder (feature 444 T42): the block, its seat and its waterside reeds, drawn as the deleted polder stage drew
//! them (`t42-brief.md` section 4, item 11).
//!
//! Research:
//!     the polder - research/questions/0019-polders-fields-diked-against-the-fluctuating-water-weitian-waju.drawing.html: enclosed by its dike all the way round, from outside in the dike, the ring canal, the field ditches and the paddies

use std::collections::HashMap;

use super::plan::Plan;
use super::svg::{ink, Svg, BUND_W};
use super::{
    fill, kept, paddy_kind, settlement_ground, stage_seat, Ground, Rolled, CROP_MARGIN,
    RESERVED_INK, RUN_W,
};
use crate::field::fan::Pt;
use crate::field::geom::{dist, seg_dist, unit};
use crate::field::staged::{polder_stage, PolderStage};
use crate::seat::Seated;
use crate::waterward::{fringe, Fringe};

/// The polder's inks: the dike's earth and edge, its crowns by crop, a pond's bank, the sluice gates, the tea hedges.
///
/// Research:
///     the polder's paint - CONVENTION: the deleted engine's dike, crown, bank and sluice inks, carried as they stood
pub(super) const DIKE_EARTH: &str = "#B79B68";
/// The dike's edge.
///
/// Research:
///     the polder's paint - CONVENTION: the deleted engine's ink, carried as it stood
const DIKE_EDGE: &str = "#9C8150";
/// A pond's bank.
///
/// Research:
///     the polder's paint - CONVENTION: the deleted engine's ink, carried as it stood
const BANK_FILL: &str = "#A9AE7C";
/// A fry pond's water.
///
/// Research:
///     the polder's paint - CONVENTION: the deleted engine's ink, carried as it stood
const NURSERY_WATER: &str = "#A7B3AE";
/// The sluice gate's fill and edge.
///
/// Research:
///     the polder's paint - CONVENTION: the deleted engine's ink, carried as it stood
const SLUICE: (&str, &str) = ("#8C7A5A", "#5A4A32");
/// The tea hedge's line.
///
/// Research:
///     the polder's paint - CONVENTION: the deleted engine's ink, carried as it stood
const HEDGE: &str = "#5E7C40";
/// The kind a pond bank and its crowns depict by the bank's crop: the mulberry, fruit or tea dike of a dike-pond.
///
/// Research:
///     the bank's kind - CONVENTION: the registry's dike-pond kinds (`mulberry dike`, `fruit dike`, `tea dike`), the review's legend named by the bank's crop
fn dike_kind(crop: &str) -> &'static str {
    match crop {
        "fruit" => "fruit dike",
        "tea" => "tea dike",
        _ => "mulberry dike",
    }
}

/// A dike crown's color by its crop.
///
/// Research:
///     the polder's paint - CONVENTION: the deleted engine's ink, carried as it stood
pub(super) fn crown_fill(crop: &str) -> &'static str {
    match crop {
        "willow" => "#6E8B4A",
        "fruit" => "#7C9A54",
        "tea" => "#5E7C40",
        _ => "#87A45C",
    }
}
/// A sluice's span (ft), post to post, on a field channel: a channel too wide for it between the posts takes a frame from bank to
/// bank (`sluice_frame`).
///
/// Research:
///     the sluice's span - research/questions/0179-water-gates-and-sluices-shuimen.drawing.html: the frame's span drawn true, post to post, a field channel's sluice spanning about 16 to 24 ft and a wider channel's bank to bank; 20 ft, the band's middle and the deleted `sluice_gate`'s default where no span was given, a GUESS (the page's band is its own GUESS)
const SLUICE_SPAN_FT: f64 = 20.0;
/// A sluice's timbers (ft): the board's thickness along its channel, a post's breadth across and along it, the crossbeam's
/// width and its offset up the channel from the board, the windlass drum's side.
///
/// Research:
///     the timbers drawn larger than life - research/questions/0179-water-gates-and-sluices-shuimen.drawing.html: the frame's timbers and its drum drawn at the smallest size the map draws anything, a CONVENTION, as the wells are; the deleted `sluice_gate`'s sizes at a hamlet's scale (a 2.8 ft board, 2 by 4 ft posts, a 1.2 ft beam 3.1 ft off, a 2.2 ft drum), carried as they stood
const SLUICE_TIMBER_FT: (f64, (f64, f64), f64, f64, f64) = (2.8, (2.0, 4.0), 1.2, 3.1, 2.2);
/// The feeder's width (ft), from the wild pond to the inlet.
///
/// Research:
///     the feeder's width - GUESS: a line 3 ft wide, the deleted ink's, carried as it stood; no page sizes a polder's feeder - research/questions/0068-how-wide-canals-and-ditches-are-the-ladder-of-channel-widths.drawing.html's ladder puts a pond feeder at roughly twice its 1.5 ft floor and the head race carrying a whole fan's water at 6.0 ft, and says neither is this channel
const FEEDER_W: f64 = 3.0;
/// The tea hedge row's width (ft), on a tea-planted dike.
///
/// Research:
///     the tea hedge row's width - GUESS: a line 3 ft wide, the deleted ink's, carried as it stood; no page in the record sizes a hedge row on a polder's dike (impl-drift on feature 449 T226, 2026-11-20)
const HEDGE_W: f64 = 3.0;
/// The waterside strip's depth off the dike (ft).
///
/// Research:
///     the strip's depth - GUESS: the page records no depth; the deleted waterward stage's 280 ft
const STRIP_DEPTH: f64 = 280.0;
/// The denser reed band's width on each bank of a channel through the reeds (ft).
///
/// Research:
///     the bank band - research/questions/0074-reed-beds-and-the-marshs-edge-yoshihara.drawing.html: where a stream or ditch crosses the marsh the reeds run to the water and a narrow band of denser, slightly darker reeds lines each bank, so the water stays easy to follow - a map drawing CONVENTION; 6 ft, the deleted `BANK_FT` that page's feature 300 drew it at
const BANK_FT: f64 = 6.0;
/// How far apart a channel's banks are sampled for the reeds beside them (ft).
///
/// Research:
///     the bank's samples - NONE: a drawing's grain, under the band's own width
const BANK_STEP_FT: f64 = 2.0;

/// The polder (stage 2 on a polder archetype): the block, its dike, outfall, resting plots and pocket pond, and on a dike-pond its
/// conversion (`field::staged::polder_stage`), each knob it reads rolled as the deleted polder stage rolled it.
///
/// Research:
///     the polder - research/questions/0019-polders-fields-diked-against-the-fluctuating-water-weitian-waju.drawing.html: enclosed by its dike all the way round, from outside in the dike, the ring canal, the field ditches and the paddies
///     the dike-pond's split - GUESS: the share of a parcel a pond takes, rolled from 0.3 to 0.7 (the registry's `dikepond_split`)
///     the paddy's rest - GUESS: settled 0.8 and unsettled 0.2, a knob between the two forms (the registry's `paddy_rest`)
fn stage_polder(p: &Plan) -> PolderStage {
    let pinned = |name: &str, forms: &[&str], weights: &[f64]| -> String {
        p.pins.get(name).cloned().unwrap_or_else(|| {
            forms[crate::pyrand::roll(
                p.seed,
                name,
                u32::try_from(forms.len()).unwrap_or(1),
                weights,
            ) as usize]
                .to_owned()
        })
    };
    let dikepond = p.archetype == "mulberry_dike_fishpond";
    let rest = pinned("paddy_rest", &["settled", "unsettled"], &[0.8, 0.2]);
    let split: f64 = if dikepond {
        pinned("dikepond_split", &["0.6", "0.4", "0.7", "0.5", "0.3"], &[])
            .parse()
            .unwrap_or(0.6)
    } else {
        0.5
    };
    polder_stage(
        p.seed,
        p.households,
        dikepond,
        &p.pond_layout,
        p.down_deg,
        (p.w / 2.0, p.h / 2.0),
        p.fan_aspect,
        (p.w, p.h),
        rest == "unsettled",
        (split, &p.leftover, &p.fry_form, &p.dike_crop),
    )
}

/// A sluice gate's frame as drawn: its span post to post, the board across the channel, the two posts on its ends, the crossbeam
/// over them and the windlass drum at the beam's middle.
///
/// Research:
///     a sluice's frame - NONE: the record's type, holding what `sluice_frame` decides
#[derive(Debug, Clone, PartialEq)]
struct SluiceFrame {
    span: f64,
    board: Vec<Pt>,
    posts: [Vec<Pt>; 2],
    beam: [Pt; 2],
    drum: Vec<Pt>,
}

/// The channel a sluice at `at` shuts, of `channels` (each its course and drawn width): the first whose course runs through the
/// point, as its segment's unit direction there and its width; `None` when none does.
///
/// Research:
///     the channel it shuts - research/questions/0179-water-gates-and-sluices-shuimen.drawing.html: the board lies across the channel it blocks; on a polder the channel that crosses the dike at the sluice (research/questions/0019-polders-fields-diked-against-the-fluctuating-water-weitian-waju.drawing.html: water crosses the dike only at gated sluices), the feeder at the inlet and the outfall's drain at the outfall, found by its course rather than pinned
fn sluice_channel(at: Pt, channels: &[(&[Pt], f64)]) -> Option<(Pt, f64)> {
    channels.iter().find_map(|&(pts, w)| {
        pts.windows(2).find_map(|seg| {
            let (a, b) = (seg[0], seg[1]);
            let len = dist(a, b);
            (len > 1e-9 && seg_dist(at, a, b) < 1e-6)
                .then(|| (((b.0 - a.0) / len, (b.1 - a.1) / len), w))
        })
    })
}

/// The frame of a sluice at `at` on a channel running along `dir` (a unit vector) `w` feet wide: its span across the channel the
/// field channel's `SLUICE_SPAN_FT`, or on a channel too wide for it wide enough that each post stands wholly on its bank; the
/// crossbeam up the channel (against `dir`) from the board.
///
/// Research:
///     the frame across its channel - research/questions/0179-water-gates-and-sluices-shuimen.drawing.html: a sluice drawn as a timber board across its channel between two posts, with the crossbeam and windlass that lifted it, the frame's span drawn true, post to post - about 16 to 24 ft on a field channel (`SLUICE_SPAN_FT`), bank to bank on a wider one; the frame itself the page's GUESS from how a lifting gate works
///     the timbers - research/questions/0179-water-gates-and-sluices-shuimen.drawing.html: drawn larger than life, a CONVENTION (`SLUICE_TIMBER_FT`)
fn sluice_frame(at: Pt, dir: Pt, w: f64) -> SluiceFrame {
    let (board_t, (post_a, post_d), _, beam_off, drum) = SLUICE_TIMBER_FT;
    let across = (-dir.1, dir.0);
    let span = SLUICE_SPAN_FT.max(w + 2.0 * post_a);
    // a rectangle centered `along` the channel and `side` across it from the sluice's point, `ha` and `hs` its half-sides
    let rect = |along: f64, side: f64, ha: f64, hs: f64| -> Vec<Pt> {
        [(-1.0, -1.0), (-1.0, 1.0), (1.0, 1.0), (1.0, -1.0)]
            .iter()
            .map(|&(u, v)| {
                let (a, c) = (along + u * ha, side + v * hs);
                (
                    at.0 + dir.0 * a + across.0 * c,
                    at.1 + dir.1 * a + across.1 * c,
                )
            })
            .collect()
    };
    let inner = span / 2.0 - post_a / 2.0;
    let on = |along: f64, side: f64| {
        (
            at.0 + dir.0 * along + across.0 * side,
            at.1 + dir.1 * along + across.1 * side,
        )
    };
    SluiceFrame {
        span,
        board: rect(0.0, 0.0, board_t / 2.0, inner),
        posts: [
            rect(0.0, -inner, post_d / 2.0, post_a / 2.0),
            rect(0.0, inner, post_d / 2.0, post_a / 2.0),
        ],
        beam: [on(-beam_off, -inner), on(-beam_off, inner)],
        drum: rect(-beam_off, 0.0, drum / 2.0, drum / 2.0),
    }
}

/// The polder drawn: the wild pond and its fringe at the head, the plots by state, the ditches by role, the outfall, the dike's
/// band with its crowns, a dike-pond's parcels with their banks, water and crops, a rice polder's pocket pond; the sluices are
/// `draw_sluices`', drawn on top.
///
/// Research:
///     the polder drawn - CONVENTION: the deleted `ink.dike` and `dikeponds`, each record drawn as the engine drew it, the sluices apart
///     the pocket pond's ring - GUESS: flooded ground 2.5 ft wide round the pond inside a bund line 2.2 ft wide, the deleted ink's; no page sizes the margin
fn draw_polder(svg: &mut Svg, s: &PolderStage) {
    let (c, rx, ry) = s.polder.pond;
    svg.kind("marsh");
    svg.reeds(&s.polder.fringe);
    svg.kind("pond");
    svg.ellipse(c, rx, ry, ink::POND_WATER, Some((ink::RIM, 2.4)));
    for (x, st) in s.polder.plots.iter().zip(&s.states) {
        svg.kind(paddy_kind(*st));
        svg.polygon(&x.ring, fill(*st), Some((ink::AZE, BUND_W)));
    }
    if let Some((parcels, crops, _)) = &s.converted {
        svg.kind(dike_kind(&crops.crop));
        for (_, ring) in parcels.iter().filter_map(|q| q.bank.as_ref()) {
            svg.polygon(ring, BANK_FILL, Some((ink::AZE, BUND_W)));
        }
    }
    let waters = s
        .converted
        .iter()
        .flat_map(|(parcels, _, _)| parcels)
        .filter_map(|q| q.water.as_ref().map(|(_, ring)| (q.kind == "fry", ring)));
    for (fry, ring) in waters {
        let (kind, water) = if fry {
            ("fry pond", NURSERY_WATER)
        } else {
            ("fish pond", ink::POND_WATER)
        };
        svg.kind(kind);
        svg.polygon(ring, water, Some((ink::RIM, 1.0)));
    }
    for d in &s.polder.ditches {
        svg.kind(if d.role == "drain" || d.seg == "drain" {
            "drainage ditch"
        } else {
            "irrigation ditch"
        });
        svg.taper(
            &d.pts,
            if d.role == "drain" || d.seg == "drain" {
                ink::DRAIN
            } else {
                ink::SUPPLY
            },
            d.w,
            d.w_tail,
        );
    }
    svg.kind("irrigation ditch");
    svg.line(&s.polder.feeder, ink::SUPPLY, FEEDER_W);
    svg.kind("drainage ditch");
    svg.unframed(&s.outfall, ink::DRAIN, RUN_W);
    svg.kind("perimeter dike");
    svg.band(&s.dike.outer, &s.dike.inner, DIKE_EARTH, (DIKE_EDGE, 1.0));
    svg.group(0.92);
    let bank_crowns = s
        .converted
        .iter()
        .flat_map(|(_, crops, _)| crops.crowns.iter().map(move |c| (crops.crop.as_str(), *c)));
    // a perimeter dike's trees are its own glyph's, a pond bank's crowns its dike's
    svg.kind("perimeter dike");
    for (crop, crowns) in &s.dike.trees {
        for &(x, y, r) in crowns {
            svg.ellipse((x, y), r, r, crown_fill(crop), None);
        }
    }
    for (crop, (x, y, r)) in bank_crowns {
        svg.kind(dike_kind(crop));
        svg.ellipse((x, y), r, r, crown_fill(crop), None);
    }
    svg.close();
    svg.kind("tea dike");
    for hedge in s.converted.iter().flat_map(|(_, crops, _)| &crops.hedges) {
        svg.line(hedge, HEDGE, HEDGE_W);
    }
    if let Some((_, x, y, prx, pry)) = s.pocket {
        svg.kind("field pond");
        svg.ellipse(
            (x, y),
            prx + 2.5,
            pry + 2.5,
            ink::FLOODED,
            Some((ink::AZE, 2.2)),
        );
        svg.ellipse((x, y), prx, pry, ink::POND_WATER, Some((ink::RIM, 1.2)));
    }
}

/// The polder's sluices drawn, each a frame across the channel through its point (`sluice_channel`, `sluice_frame`), on top of
/// the map's water and reeds; one whose channel is not found is left undrawn and named in `missing`.
///
/// Research:
///     the sluices drawn - research/questions/0179-water-gates-and-sluices-shuimen.drawing.html: each a frame across the channel that crosses the dike at its point, at that channel's drawn width; none drawn where no channel is known, the gap named rather than guessed
///     on top - CONVENTION: the frame drawn above the water and the reeds, as the deleted `sluice_gate` drew it (its top layer)
///     the board's place - research/questions/0179-water-gates-and-sluices-shuimen.drawing.html: the board a few steps down the blocked channel from the junction, so that it plainly crosses the channel it blocks, not the one it branches from; a polder's sluice point stands 8.5 ft out from the ring canal's corner or its drain trunk's end (`RING_FT`, 6 ft each way, measured on Kuwabata 2026-11-22, feature 449 T249), joined to that junction by a drawn reach (`field::polder::joins`, 449 T263) and no other channel through it, so the board is drawn on the point, 8.5 ft down the blocked channel from the junction
fn draw_sluices(svg: &mut Svg, s: &PolderStage, missing: &mut Vec<String>) {
    svg.kind("sluice gate");
    let channels = [
        (s.polder.feeder.as_slice(), FEEDER_W),
        (s.outfall.as_slice(), RUN_W),
    ];
    for (i, &at) in s.polder.sluices.iter().enumerate() {
        let Some((dir, w)) = sluice_channel(at, &channels) else {
            missing.push(format!(
                "the sluice gate at ({:.1}, {:.1}) (sluice {i}) not drawn: no channel the stage records runs through its point, so its width and the direction across it are unknown",
                at.0, at.1
            ));
            continue;
        };
        let f = sluice_frame(at, dir, w);
        svg.polygon(&f.board, SLUICE.0, Some((SLUICE.1, 0.8)));
        svg.line(&f.beam, SLUICE.1, SLUICE_TIMBER_FT.2);
        for post in &f.posts {
            svg.polygon(post, SLUICE.1, None);
        }
        svg.polygon(&f.drum, SLUICE.0, Some((SLUICE.1, 0.8)));
    }
}

/// The waterside reeds (stage 6, a polder's only): a strip outside the dike on each flank that faces the water, stopped at the
/// banks of the two channels that cross the dike at its sluices - the feeder into the inlet and the outfall's drain out of the tail.
///
/// Research:
///     the reed strips - research/questions/0019-polders-fields-diked-against-the-fluctuating-water-weitian-waju.drawing.html: reeds on the flanks of a dike that face the water
///     the channels they stop at - research/questions/0019-polders-fields-diked-against-the-fluctuating-water-weitian-waju.drawing.html: water crosses the dike only at gated sluices, the feeder at the inlet and the outfall's drain at the outfall, each at its drawn width (`FEEDER_W`, `RUN_W`); research/questions/0074-reed-beds-and-the-marshs-edge-yoshihara.drawing.html: the reeds drawn to the water's edge, kept out of the water
fn stage_waterward(p: &Plan, s: &PolderStage, seated: Option<&Seated>) -> Fringe {
    let rad = p.down_deg.to_radians();
    fringe(
        &s.dike.outer,
        &[
            (s.polder.feeder.as_slice(), FEEDER_W),
            (s.outfall.as_slice(), RUN_W),
        ],
        STRIP_DEPTH,
        (p.w, p.h),
        (rad.cos(), rad.sin()),
        seated.and_then(|x| x.frames.first()).map(|f| f.out),
    )
}

/// The denser bands of reeds along the banks of the feeder and the outfall's drain where they run through the reeds - the
/// waterside strips and the wild pond's fringe, never on the pond's water: each bank's line, `BANK_FT` wide, its middle half the
/// band past the channel's edge, cut into the runs whose samples stand in the reeds. Each reach of a bank is clipped once to each
/// ring's box, and where it meets the box it is crossed once against the ring's edges (`crossings`): a sample on the reach is in
/// the ring by the start's side and the crossings before it, read off the sorted crossings in order. The outfall runs on to the
/// canvas edge, most of it past every ring's box, and those samples are out of the reeds without a test.
///
/// Research:
///     the band on each bank - research/questions/0074-reed-beds-and-the-marshs-edge-yoshihara.drawing.html: a narrow band of denser reeds lines each bank where a stream or ditch crosses the marsh (`BANK_FT`)
///     only in the reeds - research/questions/0074-reed-beds-and-the-marshs-edge-yoshihara.drawing.html: the band lines the water through the marsh, so it runs only where the bank's ground is reeds, and stops at the wild pond's rim, the water itself
///     the reach crossed once per ring - NONE: plane geometry, which decides nothing about the place
#[expect(
    clippy::many_single_char_names,
    reason = "the plane geometry's own names"
)]
fn bank_bands(
    s: &PolderStage,
    strips: &[Vec<Pt>],
    counts: &mut HashMap<String, u64>,
) -> Vec<Vec<Pt>> {
    let ((c, rx, ry), mut tests) = (s.polder.pond, 0_u64);
    let rings: Vec<(&[Pt], [f64; 4])> = strips
        .iter()
        .chain(std::iter::once(&s.polder.fringe))
        .filter(|r| r.len() >= 3)
        .map(|r| {
            let b = r
                .iter()
                .fold([f64::MAX, f64::MAX, f64::MIN, f64::MIN], |b, q| {
                    [b[0].min(q.0), b[1].min(q.1), b[2].max(q.0), b[3].max(q.1)]
                });
            (r.as_slice(), b)
        })
        .collect();
    // each ring boxed, a test a corner
    tests += rings.iter().map(|(r, _)| r.len() as u64).sum::<u64>();
    let mut bands = Vec::new();
    for (course, w) in [
        (s.polder.feeder.as_slice(), FEEDER_W),
        (s.outfall.as_slice(), RUN_W),
    ] {
        for side in [1.0, -1.0] {
            let off = side * (w + BANK_FT) / 2.0;
            // the bank's samples, numbered along it across its reaches: a run breaks at a sample out of the reeds, and at a gap
            // of samples no ring's box holds
            let (mut run, mut last, mut base): (Vec<Pt>, Option<usize>, usize) =
                (Vec::new(), None, 0);
            for seg in course.windows(2) {
                let (a, b) = (seg[0], seg[1]);
                let d = unit(a, b);
                let nrm = (-d.1 * off, d.0 * off);
                #[expect(
                    clippy::cast_possible_truncation,
                    clippy::cast_sign_loss,
                    reason = "a reach's samples, a few thousand at most"
                )]
                let n = (dist(a, b) / BANK_STEP_FT).ceil().max(1.0) as u32;
                let (p, z) = ((a.0 + nrm.0, a.1 + nrm.1), (b.0 + nrm.0, b.1 + nrm.1));
                // each ring the reach meets: its samples' span, the side the reach starts on, its crossings in order, read so far
                let mut met: Vec<(u32, u32, bool, Vec<f64>, usize)> = Vec::new();
                for (r, bx) in &rings {
                    tests += 1;
                    if let Some((t0, t1)) = clip(p, z, bx) {
                        #[expect(
                            clippy::cast_possible_truncation,
                            clippy::cast_sign_loss,
                            reason = "a sample's number on its reach, 0 to n"
                        )]
                        let (lo, hi) = (
                            ((t0 * f64::from(n)).floor().max(1.0) as u32) - 1,
                            ((t1 * f64::from(n)).ceil() as u32 + 1).min(n),
                        );
                        let (inside, ts) = crossings(p, z, r, &mut tests);
                        met.push((lo, hi, inside, ts, 0));
                    }
                }
                let spans = merged(met.iter().map(|m| (m.0, m.1)).collect(), &mut tests);
                for k in spans.into_iter().flat_map(|(lo, hi)| lo..=hi) {
                    let g = base + k as usize;
                    if last.is_none_or(|l| g != l + 1) {
                        close(&mut run, &mut bands);
                    }
                    last = Some(g);
                    let t = f64::from(k) / f64::from(n);
                    let q = (a.0 + (b.0 - a.0) * t + nrm.0, a.1 + (b.1 - a.1) * t + nrm.1);
                    let (dx, dy) = ((q.0 - c.0) / (rx + BANK_FT), (q.1 - c.1) / (ry + BANK_FT));
                    tests += 1;
                    let mut reeds = false;
                    for (lo, hi, inside, ts, read) in &mut met {
                        tests += 1;
                        while *read < ts.len() && ts[*read] < t {
                            *read += 1;
                            tests += 1;
                        }
                        reeds |= *lo <= k && k <= *hi && (*inside != (*read % 2 == 1));
                    }
                    if reeds && dx * dx + dy * dy >= 1.0 {
                        run.push(q);
                    } else {
                        close(&mut run, &mut bands);
                    }
                }
                base += n as usize + 1;
            }
            close(&mut run, &mut bands);
        }
    }
    crate::counts::tally(counts, "test@bank", tests);
    crate::counts::tally(
        counts,
        "write@bank",
        bands.iter().map(Vec::len).sum::<usize>() as u64,
    );
    bands
}

/// The samples some met ring's span `spans` holds (each its first and last sample on the reach), as runs each once and in order:
/// the spans put in order by their starts, a comparison each, and walked once, a test each, into runs where those that overlap or
/// abut are merged.
///
/// Research:
///     the spans merged - NONE: bookkeeping, the same samples the spans hold
fn merged(mut spans: Vec<(u32, u32)>, tests: &mut u64) -> Vec<(u32, u32)> {
    spans.sort_by(|x, y| {
        *tests += 1;
        x.0.cmp(&y.0)
    });
    let mut runs: Vec<(u32, u32)> = Vec::new();
    for (lo, hi) in spans {
        *tests += 1;
        match runs.last_mut() {
            Some(m) if lo <= m.1 + 1 => m.1 = m.1.max(hi),
            _ => runs.push((lo, hi)),
        }
    }
    runs
}

/// The reach from `p` to `z` against a ring, in one pass over the ring's edges: whether `p` lies inside it (even-odd, as
/// `inside`), and the reach's parameters in 0..=1 where it crosses an edge, sorted.
///
/// Research:
///     the crossings - NONE: plane geometry
#[expect(
    clippy::many_single_char_names,
    reason = "the plane geometry's own names"
)]
fn crossings(p: Pt, z: Pt, ring: &[Pt], tests: &mut u64) -> (bool, Vec<f64>) {
    let (dx, dy) = (z.0 - p.0, z.1 - p.1);
    let (mut odd, mut ts) = (false, Vec::new());
    let mut j = ring.len() - 1;
    for i in 0..ring.len() {
        *tests += 1;
        let (u, v) = (ring[i], ring[j]);
        if (u.1 > p.1) != (v.1 > p.1) && p.0 < (v.0 - u.0) * (p.1 - u.1) / (v.1 - u.1) + u.0 {
            odd = !odd;
        }
        let (ex, ey) = (v.0 - u.0, v.1 - u.1);
        let den = dx * ey - dy * ex;
        if den.abs() > f64::EPSILON {
            let (wx, wy) = (u.0 - p.0, u.1 - p.1);
            let (t, e) = ((wx * ey - wy * ex) / den, (wx * dy - wy * dx) / den);
            if (0.0..=1.0).contains(&t) && (0.0..1.0).contains(&e) {
                ts.push(t);
            }
        }
        j = i;
    }
    // the crossings put in order along the reach, a comparison each
    ts.sort_by(|a, b| {
        *tests += 1;
        a.total_cmp(b)
    });
    (odd, ts)
}

/// A run of a bank's samples in the reeds ended: kept as a band where it holds two samples or more.
///
/// Research:
///     a band of two samples or more - NONE: a line needs two points; the band's place is `bank_bands`' claims
fn close(run: &mut Vec<Pt>, bands: &mut Vec<Vec<Pt>>) {
    if run.len() >= 2 {
        bands.push(std::mem::take(run));
    } else {
        run.clear();
    }
}

/// The span of `t` in 0..=1 over which the reach from `p` to `z` lies in the box `[x0, y0, x1, y1]` (Liang-Barsky), or None
/// where it misses the box.
///
/// Research:
///     the clip - NONE: plane geometry
fn clip(p: Pt, z: Pt, bx: &[f64; 4]) -> Option<(f64, f64)> {
    let (dx, dy) = (z.0 - p.0, z.1 - p.1);
    let (mut t0, mut t1) = (0.0_f64, 1.0_f64);
    for (q, r) in [
        (-dx, p.0 - bx[0]),
        (dx, bx[2] - p.0),
        (-dy, p.1 - bx[1]),
        (dy, bx[3] - p.1),
    ] {
        if q.abs() < f64::EPSILON {
            if r < 0.0 {
                return None;
            }
        } else {
            let t = r / q;
            if q < 0.0 {
                t0 = t0.max(t);
            } else {
                t1 = t1.min(t);
            }
        }
    }
    (t0 <= t1).then_some((t0, t1))
}

/// The ring the seat is handed on a polder: each side of the block's outline (the plots' edge, four sides) pushed straight out to
/// the dike's outer face at its widest on that side, and the sides met again at their corners - so every point of the outer face
/// lies inside it, and the settlement's ground laid off it stands off the dike. The outer face is read once, each point projected
/// on every side's outward normal, tallied to the seat.
///
/// Research:
///     a ring off the outer face - research/questions/0019-polders-fields-diked-against-the-fluctuating-water-weitian-waju.drawing.html: the village on the dry ground just off the dike (the page's own GUESS); research/questions/0027-polder-dikes-what-they-were-made-of-how-big-and-what-grew-on-them.drawing.html: the outer face the inner one pushed out by the breadth rolled along it
///     straight at the widest - GUESS: research/questions/0027-polder-dikes-what-they-were-made-of-how-big-and-what-grew-on-them.drawing.html: the breadth 14 to 40 ft, changing along the length, so a side held straight at its widest stands off a pinched stretch by up to the waves' spread, about 26 ft; the outer face itself handed instead (its 136 to 178 stations each a margin) offered 68 to 89 candidate seats on the five polders measured, their backs turned with each wave, where the four straight sides offer 2 (measured 2026-11-20, feature 449 T239) - priced and not taken
///     the corners - NONE: two offset sides met at their crossing; a block's sides are never parallel at a corner
fn off_the_dike(outline: &[Pt], outer: &[Pt], counts: &mut HashMap<String, u64>) -> Vec<Pt> {
    let sides = outline.len();
    #[expect(clippy::cast_precision_loss, reason = "a ring's few corners")]
    let mid = (
        outline.iter().map(|p| p.0).sum::<f64>() / sides as f64,
        outline.iter().map(|p| p.1).sum::<f64>() / sides as f64,
    );
    // each side's start, direction along it and outward normal
    let frames: Vec<(Pt, Pt, Pt)> = (0..sides)
        .map(|i| {
            let (start, end) = (outline[i], outline[(i + 1) % sides]);
            let along = unit(start, end);
            let flip = (along.0 * (start.1 - mid.1) - along.1 * (start.0 - mid.0)).signum();
            (start, along, (-along.1 * flip, along.0 * flip))
        })
        .collect();
    // ONE PASS over the outer face, each point's reach past every side kept at its widest
    let mut reach = vec![0.0_f64; sides];
    for pt in outer {
        for (r, &(start, _, nrm)) in reach.iter_mut().zip(&frames) {
            *r = r.max((pt.0 - start.0) * nrm.0 + (pt.1 - start.1) * nrm.1);
        }
    }
    crate::counts::tally(counts, "test@seat_ring", (outer.len() * sides) as u64);
    let pushed: Vec<(Pt, Pt)> = frames
        .iter()
        .zip(&reach)
        .map(|(&(start, along, nrm), &r)| ((start.0 + nrm.0 * r, start.1 + nrm.1 * r), along))
        .collect();
    (0..sides)
        .map(|k| {
            let ((from, dir), (to, dir_next)) = (pushed[(k + sides - 1) % sides], pushed[k]);
            let t = ((to.0 - from.0) * dir_next.1 - (to.1 - from.1) * dir_next.0)
                / (dir.0 * dir_next.1 - dir.1 * dir_next.0);
            (from.0 + dir.0 * t, from.1 + dir.1 * t)
        })
        .collect()
}

/// The polder's landward shore: of its two cross flanks (square to the fall), the one turned away from the wild pond at its head,
/// as a unit vector out of the block - the one nearer the wind on a pond standing square on the head's middle.
///
/// Research:
///     the village on the landward shore - research/questions/0019-polders-fields-diked-against-the-fluctuating-water-weitian-waju.drawing.html: the pool's polders drawn against the landward shore, the wild pond that feeds them at the head's corner to the northwest, the reeds on the low foot and on the west flank, the dry landward shore and the village to the east - every flank but the landward one holding water back; the head holds the wild pond and the foot the outfall's marsh, so the landward shore is a cross flank, and on the page's polders it is the one away from the pond. GUESS: that the cross flank away from the wild pond is the landward one on every polder is this project's reading of the two drawn
///     the shore over the wind - research/questions/0072-shelter-belts-on-a-villages-windward-side-bofurin.drawing.html: a settlement backs onto the wind except where a polder's village backs onto its landward shore, its belt still to windward; research/questions/0019-polders-fields-diked-against-the-fluctuating-water-weitian-waju.drawing.html lays the polder village on the landward dry ground - so the seat's back is handed the shore's normal and recorded off the wind where it does not face it
///     the tie - GUESS: a pond square on the head's middle names neither flank; the one nearer the wind, so the back is turned toward it where it can be
fn landward(p: &Plan, s: &PolderStage) -> Pt {
    let rad = p.down_deg.to_radians();
    let (fx, fy) = (rad.cos(), rad.sin());
    let ring = &s.polder.outline;
    #[expect(clippy::cast_precision_loss, reason = "a ring's few corners")]
    let n = ring.len().max(1) as f64;
    let mid = (
        ring.iter().map(|q| q.0).sum::<f64>() / n,
        ring.iter().map(|q| q.1).sum::<f64>() / n,
    );
    let pond = s.polder.pond.0;
    let (cross, wind) = ((-fy, fx), super::wind(&p.windward));
    let toward = (pond.0 - mid.0) * cross.0 + (pond.1 - mid.1) * cross.1;
    let side = if toward.abs() > 1e-6 {
        -toward.signum()
    } else if cross.0 * wind.0 + cross.1 * wind.1 >= 0.0 {
        1.0
    } else {
        -1.0
    };
    (cross.0 * side, cross.1 * side)
}

/// The hamlet on a polder: the block, its seat and its waterside reeds, drawn. The seat is handed the polder's own ground: a ring
/// off the dike's outer face as the ring it seats against (`off_the_dike`), the field ditches, the feeder and the outfall as the
/// lines its way out may not cross, the wild pond's reed fringe as wet ground, and its landward shore as the way its back faces
/// (`landward`); the waterside strips come after it, laid off the flanks it does not take.
///
/// Research:
///     the village off its polder's dike - research/questions/0019-polders-fields-diked-against-the-fluctuating-water-weitian-waju.drawing.html: the village drawn on the dry ground just off the dike, a few steps off it (the page's own GUESS), and hard against its own polder (its GUESS) - the seat handed a ring off the dike's outer face (`off_the_dike`), as a comb hands its fan, so the settlement's ground runs out from the dike's foot and never over the dike or the ring canal inside it (the cohort's `seat_on_dike` and `seat_on_canal`), its houses `STANDOFF_FT` off that ring; the page puts no number on "a few steps", so the 12 ft is a GUESS and a knob, and with the ring's side held straight at the face's widest the houses stand 12 to about 36 ft off the outer face (the face 2.7 to 24.3 ft inside the side along Kuwabata's band, 0 to 22.9 ft along a grid polder's falling obliquely; measured 2026-11-22, feature 449 T240)
///     its wet ground - research/questions/0081-village-lanes.drawing.html: a track keeps off wet ground and every way off every marsh's reeds - the wild pond's reed fringe handed as the seat's reeds; the waterside strips are laid after the seat, on the flanks it does not take, so its way out is asked again past them by the cohort's check (`check::walled_by_reeds`), clear on Kuwabata and on a grid polder falling obliquely (measured 2026-11-22, feature 449 T240)
///     its back to the landward shore - research/questions/0019-polders-fields-diked-against-the-fluctuating-water-weitian-waju.drawing.html: the village on the dry landward shore, every other flank holding water back - the seat's back handed the shore (`landward`), each seat then recorded against the map's own wind
///     its belt to windward on the dry side - GUESS research/questions/0072-shelter-belts-on-a-villages-windward-side-bofurin.drawing.html: the wind decides the belt's side, on one or two windward sides of the houses - so a polder seat's belt room is asked of the map's own wind (`SeatIn::belt_wind`), not the shore's way, and its ground kept on the margin's dry side (`margins::belt_swept`), the village staying a few steps off the dike (research/questions/0019-polders-fields-diked-against-the-fluctuating-water-weitian-waju.drawing.html); the record is silent on a belt between the houses and a dike (the research pass of 2026-11-22, 449 T292: the Nobi plain's ring-dike groves north to west of the homestead, a row village by the dike one belt along one side, which side unsaid), so Kuwabata's belt takes the band's north end, the windward side its polder leaves dry
///     its lines and no pond - GUESS: the field ditches, the feeder and the outfall handed as the lines `stage_seat` keeps its way out from crossing, as a comb's channels are; the wild pond not handed as a pond at its berth, the reed fringe round it standing for it
///     the strips after the seat - research/questions/0019-polders-fields-diked-against-the-fluctuating-water-weitian-waju.drawing.html: every flank but the landward one holds water back - the seat's side names the landward flank, so the waterside strips are laid once it is known (`stage_waterward`)
pub(super) fn roll_polder(p: Plan) -> Rolled {
    let s = stage_polder(&p);
    let mut refusals = Vec::new();
    let lines: Vec<&[(f64, f64)]> = s
        .polder
        .ditches
        .iter()
        .map(|d| d.pts.as_slice())
        .chain([s.polder.feeder.as_slice(), s.outfall.as_slice()])
        .collect();
    let mut ring_counts = HashMap::new();
    let ring = off_the_dike(&s.polder.outline, &s.dike.outer, &mut ring_counts);
    let ground = Ground {
        ring: &ring,
        lines,
        brook: &[],
        reeds: vec![s.polder.fringe.clone()],
        pond: None,
        back: Some(landward(&p, &s)),
    };
    let wind = super::wind(&p.windward);
    let seated = kept(stage_seat(&p, &ground), &mut refusals).map(|mut x| {
        crate::counts::merge(&mut x.counts, &ring_counts);
        // each seat recorded against the map's own wind, its back turned to the shore
        for f in &mut x.frames {
            f.offwind = f.out.0 * wind.0 + f.out.1 * wind.1 < super::plan::WIND_BACK_MIN_DOT;
        }
        x
    });
    let mut ward = stage_waterward(&p, &s, seated.as_ref());
    let bands = bank_bands(&s, &ward.strips, &mut ward.counts);
    let mut svg = Svg::default();
    draw_polder(&mut svg, &s);
    svg.kind("marsh");
    for strip in &ward.strips {
        svg.reeds(strip);
    }
    // the denser reeds on each bank of a channel through them, over the strips and the fringe
    for band in &bands {
        svg.reed_bank(band, BANK_FT);
    }
    // the sluices on top, above the water and the reeds, as the deleted `sluice_gate` drew them
    draw_sluices(&mut svg, &s, &mut refusals);
    // the settlement's ground marked, as on a comb (`roll`)
    if let Some(frame) = seated.as_ref().and_then(|x| x.frames.first()) {
        svg.kind("-");
        svg.reserved(
            &settlement_ground(frame, super::wind(&p.windward)),
            RESERVED_INK,
            "the settlement",
        );
    }
    let by_stage: Vec<(&'static str, HashMap<String, u64>)> = [
        ("water_frame", p.counts.clone()),
        ("field", s.counts.0.clone()),
    ]
    .into_iter()
    .chain(seated.iter().map(|x| ("seat", x.counts.clone())))
    .chain([("waterward", ward.counts.clone())])
    .collect();
    let mut counts: HashMap<String, u64> = s.counts.0.clone();
    crate::counts::merge(
        &mut counts,
        seated
            .iter()
            .flat_map(|x| &x.counts)
            .chain(&ward.counts)
            .chain(&p.counts),
    );
    let stages: Vec<&'static str> = ["water_frame", "field"]
        .into_iter()
        .chain(seated.as_ref().map(|_| "seat"))
        .chain(["waterward"])
        .collect();
    let doc = svg.finish(p.w, p.h, CROP_MARGIN);
    Rolled {
        plan: p,
        polder: Some(s),
        waterward: Some(ward),
        sunk: None,
        seated,
        dry: Vec::new(),
        grain: None,
        field_grain: None,
        refusals,
        stages,
        knobs: HashMap::new(),
        fields: Vec::new(),
        brooks: Vec::new(),
        counts,
        by_stage,
        svg: doc,
        ink: svg.census().clone(),
    }
}

#[cfg(test)]
mod tests;
