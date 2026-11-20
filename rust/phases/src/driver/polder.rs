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
/// The sluice gate's side (ft): a square drawn on each sluice's point.
///
/// Research:
///     the sluice gate's size - DEVIATION research/questions/0179-water-gates-and-sluices-shuimen.drawing.html: a square 8 ft on a side on each sluice's point, the deleted ink's, carried as it stood, where the page draws a sluice as a board between two posts across its channel, a field channel's spanning about 16 to 24 ft - a departure the code keeps until feature 449 T234
const SLUICE_FT: f64 = 8.0;
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
/// The waterside strip's half-breadth at a cut (ft).
///
/// Research:
///     the strip's cut - GUESS: research/questions/0019-polders-fields-diked-against-the-fluctuating-water-weitian-waju.drawing.html puts reeds on the water-facing flanks but records no width; the deleted waterward stage's 15 ft
const STRIP_CUT_HW: f64 = 15.0;
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

/// The polder drawn: the wild pond and its fringe at the head, the plots by state, the ditches by role, the outfall, the dike's
/// band with its crowns and sluices, a dike-pond's parcels with their banks, water and crops, a rice polder's pocket pond.
///
/// Research:
///     the polder drawn - CONVENTION: the deleted `ink.dike` and `dikeponds`, each record drawn as the engine drew it
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
    svg.kind("sluice gate");
    let h = SLUICE_FT / 2.0;
    for g in &s.polder.sluices {
        svg.polygon(
            &[
                (g.0 - h, g.1 - h),
                (g.0 + h, g.1 - h),
                (g.0 + h, g.1 + h),
                (g.0 - h, g.1 + h),
            ],
            SLUICE.0,
            Some((SLUICE.1, 0.8)),
        );
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

/// The waterside reeds (stage 6, a polder's only): a strip outside the dike on each flank that faces the water.
///
/// Research:
///     the reed strips - research/questions/0019-polders-fields-diked-against-the-fluctuating-water-weitian-waju.drawing.html: reeds on the flanks of a dike that face the water
fn stage_waterward(p: &Plan, s: &PolderStage, seated: Option<&Seated>) -> Fringe {
    let rad = p.down_deg.to_radians();
    let ring: Vec<(f64, f64)> = s
        .dike
        .outer
        .iter()
        .chain(s.dike.inner.iter().rev())
        .copied()
        .collect();
    // the dike's two faces copied into the one outline the fringe reads, a point each (feature 449 T226: uncounted before)
    let copied = ring.len() as u64;
    let mut ward = fringe(
        &[(ring, s.dike.gaps.clone())],
        s.dike.widths.1,
        STRIP_CUT_HW,
        STRIP_DEPTH,
        (p.w, p.h),
        (rad.cos(), rad.sin()),
        seated.and_then(|x| x.frames.first()).map(|f| f.out),
    );
    crate::counts::tally(&mut ward.counts, "read@stage_waterward", copied);
    ward
}

/// The hamlet on a polder: the block, its seat and its waterside reeds, drawn.
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
    let ground = Ground {
        ring: &s.polder.outline,
        lines,
        brook: &[],
        reeds: vec![s.polder.fringe.clone()],
        pond: None,
    };
    let seated = kept(stage_seat(&p, &ground), &mut refusals);
    let ward = stage_waterward(&p, &s, seated.as_ref());
    let mut svg = Svg::default();
    draw_polder(&mut svg, &s);
    svg.kind("marsh");
    for strip in &ward.strips {
        svg.reeds(strip);
    }
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
