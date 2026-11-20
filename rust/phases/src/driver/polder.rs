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
///     the board's place - GUESS: research/questions/0179-water-gates-and-sluices-shuimen.drawing.html sets the board a few steps down the channel from the junction so that it plainly crosses the channel it blocks, not the one it branches from; a polder's sluice point is where its one channel crosses the dike's inner face, no other channel meeting it there, so the board is drawn on the point itself
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

/// The hamlet on a polder: the block, its seat and its waterside reeds, drawn. The seat is handed the polder's own ground: a ring
/// off the dike's outer face as the ring it seats against (`off_the_dike`), the field ditches, the feeder and the outfall as the
/// lines its way out may not cross, and the wild pond's reed fringe as wet ground; the waterside strips come after it, laid off
/// the flanks it does not take.
///
/// Research:
///     the village off its polder's dike - research/questions/0019-polders-fields-diked-against-the-fluctuating-water-weitian-waju.drawing.html: the village drawn on the dry ground just off the dike, a few steps off it (the page's own GUESS), and hard against its own polder (its GUESS) - the seat handed a ring off the dike's outer face (`off_the_dike`), as a comb hands its fan, so the settlement's ground runs out from the dike's foot and never over the dike or the ring canal inside it, its houses `STANDOFF_FT` off that ring
///     its wet ground - research/questions/0081-village-lanes.drawing.html: a track keeps off wet ground - the wild pond's reed fringe handed as the seat's reeds
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
    };
    let mut seated = kept(stage_seat(&p, &ground), &mut refusals);
    if let Some(x) = seated.as_mut() {
        crate::counts::merge(&mut x.counts, &ring_counts);
    }
    let ward = stage_waterward(&p, &s, seated.as_ref());
    let mut svg = Svg::default();
    draw_polder(&mut svg, &s);
    svg.kind("marsh");
    for strip in &ward.strips {
        svg.reeds(strip);
    }
    // the sluices on top, above the water and the reeds, as the deleted `sluice_gate` drew them
    draw_sluices(&mut svg, &s, &mut refusals);
    // the settlement's ground marked, as on a comb (`roll`)
    if let Some(frame) = seated.as_ref().and_then(|x| x.frames.first()) {
        svg.kind("-");
        svg.reserved(&settlement_ground(frame), RESERVED_INK, "the settlement");
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
mod tests {
    use super::{
        draw_sluices, sluice_channel, sluice_frame, Svg, SLUICE_SPAN_FT, SLUICE_TIMBER_FT,
    };
    use crate::driver::{roll, spec::parse};
    use crate::field::fan::Pt;
    use crate::field::geom::{dist, inside, seg_dist};

    fn dot(a: Pt, b: Pt) -> f64 {
        a.0 * b.0 + a.1 * b.1
    }

    /// A ring's extent along `d` about `at`: its least and greatest projection.
    fn extent(ring: &[Pt], at: Pt, d: Pt) -> (f64, f64) {
        ring.iter()
            .map(|p| dot((p.0 - at.0, p.1 - at.1), d))
            .fold((f64::INFINITY, f64::NEG_INFINITY), |(lo, hi), x| {
                (lo.min(x), hi.max(x))
            })
    }

    /// The frame lies across its channel: its span `span`, the board running post to post across `dir` and thin along it, each
    /// post at a span's end and wholly on its bank, the crossbeam across, the drum up the channel from the board.
    fn assert_across(at: Pt, dir: Pt, w: f64, span: f64) {
        let f = sluice_frame(at, dir, w);
        let across = (-dir.1, dir.0);
        let (post_a, _) = SLUICE_TIMBER_FT.1;
        assert!((f.span - span).abs() < 1e-9);
        let (lo, hi) = extent(&f.board, at, across);
        assert!((hi - lo - (span - post_a)).abs() < 1e-9);
        let (lo, hi) = extent(&f.board, at, dir);
        assert!(hi - lo <= SLUICE_TIMBER_FT.0 + 1e-9);
        let (l, r) = (
            extent(&f.posts[0], at, across),
            extent(&f.posts[1], at, across),
        );
        assert!((l.0 + span / 2.0).abs() < 1e-9 && (r.1 - span / 2.0).abs() < 1e-9);
        assert!(-l.1 >= w / 2.0 - 1e-9 && r.0 >= w / 2.0 - 1e-9);
        let beam = (f.beam[1].0 - f.beam[0].0, f.beam[1].1 - f.beam[0].1);
        assert!(dot(beam, dir).abs() < 1e-9 && dot(beam, across) > 0.0);
        assert!(extent(&f.drum, at, dir).1 < 0.0);
    }

    /// THE GATE SPANS ITS CHANNEL, ACROSS IT (449 T234): a field channel's sluice 20 ft post to post, a wider channel's bank to bank,
    /// on a channel running obliquely.
    #[test]
    fn a_sluice_spans_its_channel_across_its_direction() {
        let dir = (30f64.to_radians().cos(), 30f64.to_radians().sin());
        assert!((16.0..=24.0).contains(&SLUICE_SPAN_FT));
        assert_across((100.0, 50.0), dir, 5.5, SLUICE_SPAN_FT);
        assert_across((100.0, 50.0), (0.0, 1.0), 3.0, SLUICE_SPAN_FT);
        // Shiro Daika's 66 ft feeder: its posts on the banks
        assert_across((0.0, 0.0), dir, 66.0, 66.0 + 2.0 * SLUICE_TIMBER_FT.1 .0);
    }

    #[test]
    fn a_sluice_finds_the_channel_through_its_point() {
        let feeder: [Pt; 3] = [(0.0, 0.0), (0.0, 0.0), (0.0, 40.0)];
        let drain: [Pt; 2] = [(10.0, 10.0), (20.0, 20.0)];
        let channels = [(&feeder[..], 3.0), (&drain[..], 5.5)];
        assert_eq!(
            sluice_channel((0.0, 40.0), &channels),
            Some(((0.0, 1.0), 3.0))
        );
        let (d, w) = sluice_channel((15.0, 15.0), &channels).unwrap();
        assert!((d.0 - d.1).abs() < 1e-12 && (w - 5.5).abs() < 1e-12);
        assert_eq!(sluice_channel((5.0, 0.0), &channels), None);
    }

    /// THE OLD SQUARE IS GONE (449 T234): on a rolled polder falling obliquely and on Kuwabata, both sluices are drawn as frames
    /// across their channels - the inlet across the feeder, the outfall across its drain's diagonal leg, two different
    /// directions - each of five marks (board, beam, two posts, drum), and the deleted 8 ft square on the point is drawn nowhere.
    #[test]
    fn a_rolled_polder_draws_its_sluices_across_their_channels_not_as_the_old_square() {
        for spec in [
            r#"{"name": "R", "seed": 5, "households": 12, "down_deg": 30, "field_archetype": "polder_grid"}"#,
            r#"{"name": "Kuwabata", "seed": 21, "households": 16, "down_deg": 90, "field_archetype": "mulberry_dike_fishpond", "pond_layout": "mosaic", "dike_crop": "mulberry"}"#,
        ] {
            let r = roll(&parse(spec).unwrap()).unwrap();
            let s = r.polder.as_ref().unwrap();
            let channels = [
                (s.polder.feeder.as_slice(), super::FEEDER_W),
                (s.outfall.as_slice(), super::RUN_W),
            ];
            let found: Vec<(Pt, f64)> = s
                .polder
                .sluices
                .iter()
                .filter_map(|&at| sluice_channel(at, &channels))
                .collect();
            assert_eq!(found.len(), 2);
            assert!(dot(found[0].0, found[1].0).abs() < 0.9);
            for (&at, &(d, w)) in s.polder.sluices.iter().zip(&found) {
                assert_across(at, d, w, SLUICE_SPAN_FT);
                let h = 4.0;
                let mut old = Svg::default();
                old.polygon(
                    &[
                        (at.0 - h, at.1 - h),
                        (at.0 + h, at.1 - h),
                        (at.0 + h, at.1 + h),
                        (at.0 - h, at.1 + h),
                    ],
                    super::SLUICE.0,
                    Some((super::SLUICE.1, 0.8)),
                );
                let doc = old.finish(1e4, 1e4, 0.0);
                let square = doc.lines().find(|l| l.starts_with("<path")).unwrap();
                assert!(!r.svg.contains(square));
            }
            assert_eq!(r.ink.get("sluice gate"), Some(&10));
            assert!(!r.refusals.join("\n").contains("sluice"));
        }
    }

    /// Whether segments `ab` and `cd` cross or touch.
    fn crosses(a: Pt, b: Pt, c: Pt, d: Pt) -> bool {
        let side = |p: Pt, q: Pt, r: Pt| (q.0 - p.0) * (r.1 - p.1) - (q.1 - p.1) * (r.0 - p.0);
        let (d1, d2) = (side(c, d, a), side(c, d, b));
        let (d3, d4) = (side(a, b, c), side(a, b, d));
        d1 * d2 <= 0.0 && d3 * d4 <= 0.0
    }

    /// The least distance between segments `ab` and `cd`: nothing where they cross.
    fn seg_seg(a: Pt, b: Pt, c: Pt, d: Pt) -> f64 {
        let apart = [
            seg_dist(a, c, d),
            seg_dist(b, c, d),
            seg_dist(c, a, b),
            seg_dist(d, a, b),
        ]
        .into_iter()
        .fold(f64::INFINITY, f64::min);
        f64::from(u8::from(!crosses(a, b, c, d))) * apart
    }

    /// The segment `a` to `b` walked every foot, both ends included.
    #[expect(
        clippy::cast_possible_truncation,
        clippy::cast_sign_loss,
        reason = "a segment's length in whole feet, a small positive count"
    )]
    fn walk(a: Pt, b: Pt) -> impl Iterator<Item = Pt> {
        let n = dist(a, b).ceil().max(1.0) as u32;
        (0..=n).map(move |k| {
            let t = f64::from(k) / f64::from(n);
            (a.0 + (b.0 - a.0) * t, a.1 + (b.1 - a.1) * t)
        })
    }

    /// Feet of a channel's course (each of its segments walked every foot) lying in a strip or within its half-width of one.
    fn feet_under(strip: &[Pt], course: &[Pt], w: f64) -> usize {
        let edges: Vec<(Pt, Pt)> = (0..strip.len())
            .map(|i| (strip[i], strip[(i + 1) % strip.len()]))
            .collect();
        course
            .windows(2)
            .flat_map(|s| walk(s[0], s[1]))
            .filter(|&p| {
                inside(p, strip)
                    || edges
                        .iter()
                        .any(|&(a, b)| seg_dist(p, a, b) < w / 2.0 - 1e-6)
            })
            .count()
    }

    /// THE REEDS STOP AT THE CUT (449 T236): on Kuwabata and a polder falling obliquely, no waterside strip crosses a sluice's
    /// channel - the feeder into the inlet, the outfall's drain out of the tail - or comes within its half-width of one; no strip
    /// lies on the dike: each strip's edges, walked every foot, stay off the band inside its outer face (half a foot of rounding
    /// allowed); and on Kuwabata the foot's reeds reach the outfall's bank. Red before T236: Kuwabata's west strip had 57 ft of
    /// the feeder and 45 ft of the outfall under its reeds and its foot strip 341 ft of the outfall, and its three strips 258, 258
    /// and 259 ft of edge on the dike.
    #[test]
    fn the_waterside_strips_stop_at_the_sluices_channels_and_keep_off_the_dike() {
        let (mut got, mut want) = (Vec::new(), Vec::new());
        for spec in [
            r#"{"name": "Kuwabata", "seed": 21, "households": 16, "down_deg": 90, "field_archetype": "mulberry_dike_fishpond", "pond_layout": "mosaic", "dike_crop": "mulberry"}"#,
            r#"{"name": "R", "seed": 5, "households": 12, "down_deg": 30, "field_archetype": "polder_grid"}"#,
        ] {
            let r = roll(&parse(spec).unwrap()).unwrap();
            let s = r.polder.as_ref().unwrap();
            let ward = r.waterward.as_ref().unwrap();
            assert!(!ward.strips.is_empty());
            let name = &r.plan.name;
            let channels = [
                ("feeder", s.polder.feeder.as_slice(), super::FEEDER_W),
                ("outfall", s.outfall.as_slice(), super::RUN_W),
            ];
            for (i, strip) in ward.strips.iter().enumerate() {
                for &(channel, course, w) in &channels {
                    let near = (0..strip.len())
                        .flat_map(|j| {
                            course.windows(2).map(move |c| {
                                seg_seg(strip[j], strip[(j + 1) % strip.len()], c[0], c[1])
                            })
                        })
                        .fold(f64::INFINITY, f64::min);
                    let under = feet_under(strip, course, w);
                    got.push(format!(
                        "{name} strip {i} over the {channel}: {under} ft of its course under the reeds, within its half-width {}",
                        near < w / 2.0 - 1e-6
                    ));
                    want.push(format!(
                        "{name} strip {i} over the {channel}: 0 ft of its course under the reeds, within its half-width false"
                    ));
                }
                let on_dike = (0..strip.len())
                    .flat_map(|j| walk(strip[j], strip[(j + 1) % strip.len()]))
                    .filter(|&p| {
                        // both asked of every point, so the walk off the band is read whole
                        let deep = (0..s.dike.outer.len()).all(|k| {
                            seg_dist(
                                p,
                                s.dike.outer[k],
                                s.dike.outer[(k + 1) % s.dike.outer.len()],
                            ) > 0.5
                        });
                        inside(p, &s.dike.outer) && deep
                    })
                    .count();
                got.push(format!(
                    "{name} strip {i} on the dike: {on_dike} ft of its edge inside the outer face"
                ));
                want.push(format!(
                    "{name} strip {i} on the dike: 0 ft of its edge inside the outer face"
                ));
            }
            // on Kuwabata the foot's reeds run to the outfall's bank where it runs straight out down the fall, not short of it
            if name == "Kuwabata" {
                let run = (s.outfall[1], s.outfall[2]);
                assert!(ward
                    .strips
                    .iter()
                    .flatten()
                    .any(|&p| (seg_dist(p, run.0, run.1) - super::RUN_W / 2.0).abs() < 1e-6));
            }
        }
        assert_eq!(got, want);
    }

    /// The settlement's ground walked on a one-foot grid: the square feet of it inside the dike's outer face (deeper than half a
    /// foot past it, the rounding allowed), and those within the head canal's half-width of its course.
    #[expect(
        clippy::cast_possible_truncation,
        reason = "a grid's bounds in whole feet"
    )]
    fn ground_over(ground: &[Pt], s: &crate::field::staged::PolderStage) -> (usize, usize) {
        let outer = &s.dike.outer;
        let head = s.polder.ditches.iter().find(|d| d.seg == "feeder").unwrap();
        let (lo, hi) = ground.iter().fold(
            (
                (f64::INFINITY, f64::INFINITY),
                (f64::NEG_INFINITY, f64::NEG_INFINITY),
            ),
            |(lo, hi), p| {
                (
                    (lo.0.min(p.0), lo.1.min(p.1)),
                    (hi.0.max(p.0), hi.1.max(p.1)),
                )
            },
        );
        let (mut dike, mut canal) = (0, 0);
        for x in (lo.0.floor() as i64)..=(hi.0.ceil() as i64) {
            for y in (lo.1.floor() as i64)..=(hi.1.ceil() as i64) {
                #[expect(clippy::cast_precision_loss, reason = "whole feet on a map")]
                let p = (x as f64 + 0.5, y as f64 + 0.5);
                if !inside(p, ground) {
                    continue;
                }
                let deep = (0..outer.len())
                    .all(|k| seg_dist(p, outer[k], outer[(k + 1) % outer.len()]) > 0.5);
                dike += usize::from(inside(p, outer) && deep);
                canal += usize::from(
                    head.pts
                        .windows(2)
                        .any(|c| seg_dist(p, c[0], c[1]) < head.w / 2.0),
                );
            }
        }
        (dike, canal)
    }

    /// The ring off the dike holds the whole outer face, each side touching it at its widest, on a block turned obliquely.
    #[test]
    fn the_ring_off_the_dike_holds_the_outer_face_and_touches_it() {
        let (c, sn) = (30f64.to_radians().cos(), 30f64.to_radians().sin());
        let at = |x: f64, y: f64| (100.0 + x * c - y * sn, 50.0 + x * sn + y * c);
        let outline = [
            at(0.0, 0.0),
            at(0.0, 200.0),
            at(300.0, 200.0),
            at(300.0, 0.0),
        ];
        // a waving face, 20 to 40 ft out on each side
        let outer: Vec<Pt> = (0..40)
            .map(|k| {
                let w = 30.0 + 10.0 * (f64::from(k) * 0.7).sin();
                let t = f64::from(k % 10) / 10.0;
                match k / 10 {
                    0 => at(-w, 200.0 * t),
                    1 => at(300.0 * t, 200.0 + w),
                    2 => at(300.0 + w, 200.0 * (1.0 - t)),
                    _ => at(300.0 * (1.0 - t), -w),
                }
            })
            .collect();
        let ring = super::off_the_dike(&outline, &outer, &mut std::collections::HashMap::new());
        assert_eq!(ring.len(), 4);
        // the same ring whichever way the block's corners turn
        let mut back = outline;
        back.reverse();
        let mut turned = super::off_the_dike(&back, &outer, &mut std::collections::HashMap::new());
        turned.reverse();
        for (p, q) in ring.iter().zip(&turned) {
            assert!(dist(*p, *q) < 1e-9, "{ring:?} against {turned:?}");
        }
        for &p in &outer {
            let edge = (0..4)
                .map(|i| seg_dist(p, ring[i], ring[(i + 1) % 4]))
                .fold(f64::INFINITY, f64::min);
            assert!(inside(p, &ring) || edge < 1e-9, "{p:?} outside {ring:?}");
        }
        for i in 0..4 {
            let near = outer
                .iter()
                .map(|&p| seg_dist(p, ring[i], ring[(i + 1) % 4]))
                .fold(f64::INFINITY, f64::min);
            assert!(near < 1e-9, "side {i} stands {near} ft off the face");
        }
    }

    /// THE SETTLEMENT STANDS OFF THE DIKE (449 T239): on Kuwabata and on a grid polder falling obliquely, no square foot of the
    /// settlement's ground lies inside the dike's outer face - on the dike, the ring canal or the fields - nor within the head
    /// canal's half-width of its course. Red before T239, the seat handed the plots' edge as its ring: Kuwabata's ground had
    /// 27,322 ft2 inside the outer face and 2,784 ft2 on the head canal, the oblique polder's 26,583 and 3,168.
    #[test]
    fn the_settlement_stands_off_the_dike_and_the_head_canal() {
        let (mut got, mut want) = (Vec::new(), Vec::new());
        for spec in [
            r#"{"name": "Kuwabata", "seed": 21, "households": 16, "down_deg": 90, "field_archetype": "mulberry_dike_fishpond", "pond_layout": "mosaic", "dike_crop": "mulberry"}"#,
            r#"{"name": "R", "seed": 5, "households": 12, "down_deg": 30, "field_archetype": "polder_grid"}"#,
        ] {
            let r = roll(&parse(spec).unwrap()).unwrap();
            let s = r.polder.as_ref().unwrap();
            let frame = &r.seated.as_ref().expect("a seat").frames[0];
            let (dike, head) = ground_over(&crate::driver::settlement_ground(frame), s);
            got.push(format!(
                "{}: {dike} ft2 inside the dike's outer face, {head} ft2 on the head canal",
                r.plan.name
            ));
            want.push(format!(
                "{}: 0 ft2 inside the dike's outer face, 0 ft2 on the head canal",
                r.plan.name
            ));
        }
        assert_eq!(got, want);
    }

    /// A sluice whose channel is not known is not drawn: the gap is named, not guessed.
    #[test]
    fn a_sluice_with_no_channel_is_named_not_drawn() {
        let r = roll(&parse(r#"{"name": "R", "seed": 5, "households": 12, "down_deg": 30, "field_archetype": "polder_grid"}"#).unwrap()).unwrap();
        let mut s = r.polder.unwrap();
        s.polder.feeder.clear();
        let (mut svg, mut missing) = (Svg::default(), Vec::new());
        draw_sluices(&mut svg, &s, &mut missing);
        assert_eq!(missing.len(), 1, "{missing:?}");
        assert!(missing[0].contains("(sluice 0) not drawn: no channel"));
        assert_eq!(svg.census().get("sluice gate"), Some(&5));
    }
}
