//! The comb stage end to end (feature 444 T16): the stage's own knobs rolled, the fields counted under the cap, and each field
//! built - fan, brook and weir, lattice held to its rules, channels, the water index, the plots drawn apart, beans, the dry hem,
//! the pocket pond and the grave - with the derivation's counts (D6).
//!
//! Research:
//!     the comb - research/questions/0005-rice-paddies-and-their-plots-suiden.drawing.html: the fan of paddies, its basins and bunds

use std::collections::HashMap;

use super::beans::bean_runs;
use super::brook::{brook, clearance, file as file_brook, weir, Brook, BrookIn};
use super::channels::{channels, Channel};
use super::dry::{hem, DryPlot, GRAIN_ACRES_PER_HOUSEHOLD};
use super::fan::{fan, Fan, Pt};
use super::features::{grave, pocket_pond, Grave, Pond};
use super::index::Index;
use super::lattice::{basins, Basin};
use super::rules::{held, FieldRefused};
use super::states::{states, State};
use super::{cap_sq_ft, fields_for, paddy_sq_ft};
use crate::counts::Counts;
use crate::pyrand::roll;

/// Square feet in an acre.
///
/// Research:
///     the acre - NONE: a unit
const SQ_FT_PER_ACRE: f64 = 43_560.0;
/// A weir's thickness where its form is missing from the plan's table (feet): the thinnest form's, the fence's.
///
/// Research:
///     the fallback - research/questions/0059-where-the-ditch-leaves-the-brook-the-intake-and-its-weir-toshuko-and-seki.drawing.html: four forms 1.5 to 5 ft thick; the fence's 1.5
const WEIR_THIN_FT: f64 = 1.5;

/// One knob the stage rolls itself (D3): its name, its typing-filtered forms, their weights (empty for an even roll) and the
/// spec's pin, if any.
///
/// Research:
///     a knob's record - NONE: the plan's knob as Python gathered it
pub type KnobIn = (String, Vec<String>, Vec<f64>, Option<String>);

/// What the stage reads (T16 D1): the seed, the households, the fall, the fan's aspect, where the first field's middle sits, the
/// brook's flank and figures, the delivery ditches' fractions, the weir's figures by form, the rows' spacing and the basin's cell,
/// and the knobs.
///
/// Research:
///     the stage's inputs - NONE: the plan's figures carried in; each is claimed where the plan sets it
#[derive(Debug, Clone)]
pub struct FieldIn {
    pub seed: i64,
    pub households: u32,
    pub down_deg: f64,
    pub aspect: f64,
    pub center: Pt,
    /// The canvas's size (feet): the brook runs off it both ways.
    pub canvas: Pt,
    pub brook_side: f64,
    pub brook: BrookIn,
    pub offtakes: (Vec<f64>, Vec<f64>),
    pub weir: (f64, f64, HashMap<String, f64>),
    pub row_ft: f64,
    pub cell: f64,
    pub knobs: Vec<KnobIn>,
}

/// One field built.
///
/// Research:
///     a field's record - NONE: the record's type, holding what `one` decides
#[derive(Debug, Clone)]
pub struct Field {
    pub fan: Fan,
    pub brook: Brook,
    pub weir: Option<([Pt; 4], f64, String)>,
    pub basins: Vec<Basin>,
    pub states: Vec<State>,
    pub channels: Vec<Channel>,
    pub beans: Vec<Vec<Pt>>,
    pub dry: Vec<DryPlot>,
    pub pond: Option<(usize, Pond)>,
    pub grave: Option<Grave>,
    pub segments: Vec<(Pt, Pt, f64)>,
}

/// The stage's output: the knobs as rolled, the fields, the coarse grain's acres (drawn, needed, the room) and the counts.
///
/// Research:
///     the stage's record - NONE: the record's type, holding what `build` decides
#[derive(Debug, Clone)]
pub struct FieldOut {
    pub knobs: HashMap<String, String>,
    pub fields: Vec<Field>,
    pub grain: (f64, f64, f64),
    pub counts: HashMap<String, u64>,
}

/// The stage's knobs: each pinned form taken, else rolled from its table as `Knob.roll` draws it.
///
/// Research:
///     knobs rolled from the seed - research/questions/0031-clustered-and-scattered-villages-shuson-sanson.drawing.html: each knob's form rolled per hamlet, never chosen
fn rolled(seed: i64, knobs: &[KnobIn], counts: &mut Counts) -> HashMap<String, String> {
    knobs
        .iter()
        .filter(|(_, forms, _, pin)| pin.is_some() || !forms.is_empty())
        .map(|(name, forms, weights, pin)| {
            counts.add("candidate@_roll", 1);
            let v = pin.clone().unwrap_or_else(|| {
                let n = u32::try_from(forms.len()).unwrap_or(u32::MAX);
                forms[roll(seed, name, n, weights) as usize].clone()
            });
            (name.clone(), v)
        })
        .collect()
}

/// The stage: the knobs, then each field of the settlement's paddy under the cap.
///
/// Research:
///     the fields under the cap - research/questions/0017-how-much-farmland-a-settlement-works-and-in-what-tracts.html: a settlement with more farmland had several tracts - the paddy shared evenly among them, a GUESS (no page gives how a settlement's tracts compare)
///     fields side by side - GUESS: the record silent on where a settlement's tracts stood to each other; across the fall, each fan's half-breadths apart with the brook between them, its width and twice its skirt and wander
///     the grain owed - research/questions/0011-where-a-farming-hamlet-grew-its-coarse-grain.drawing.html: about 0.85 acre a household (`GRAIN_ACRES_PER_HOUSEHOLD`)
///     barley on the drained paddy - research/questions/0011-where-a-farming-hamlet-grew-its-coarse-grain.drawing.html: barley followed the rice on a paddy that drained, never on a wet one, and a drained paddy's winter barley is counted acre for acre against the dry field it spares
///     the hem's line - research/questions/0011-where-a-farming-hamlet-grew-its-coarse-grain.drawing.html: where the middle is left wild the dry plots climb from the toe into the middle; on a fan whose middle is cleared, the hem runs along the whole canal - the first field's far flank up from its foot, and across its head where cleared
///     the hem on the first field - GUESS: the record silent on which of several fields a hamlet's dry hem fringes; the first, on its flank away from the brook
///
/// # Errors
/// `FieldRefused` when a basin or a grave breaks a rule where it is decided (D7).
pub fn build(inp: &FieldIn) -> Result<FieldOut, FieldRefused> {
    let mut counts = Counts::default();
    let knobs = rolled(inp.seed, &inp.knobs, &mut counts);
    let is = |k: &str, v: &str| knobs.get(k).is_some_and(|x| x == v);
    let paddy = paddy_sq_ft(inp.households);
    let n = fields_for(paddy, cap_sq_ft(inp.seed));
    counts.add("write@area", 2);
    let mut fields = Vec::new();
    let need = f64::from(inp.households) * GRAIN_ACRES_PER_HOUSEHOLD * SQ_FT_PER_ACRE;
    let mut drained = 0.0;
    for k in 0..n {
        let tag = format!("f{k}");
        let area = paddy / f64::from(n);
        let first = fan(area, inp.aspect, inp.down_deg, inp.center, inp.seed);
        // the next field beside the last, across the fall, past its brook's skirt
        let step = (first.half_head + first.half_foot)
            + 2.0 * (inp.brook.skirt + inp.brook.wander)
            + inp.brook.w;
        let off = step * f64::from(k);
        let center = (
            inp.center.0 + first.across.0 * off,
            inp.center.1 + first.across.1 * off,
        );
        let f = fan(
            area,
            inp.aspect,
            inp.down_deg,
            center,
            inp.seed + i64::from(k),
        );
        let field = one(inp, &f, &tag, &knobs, &mut counts)?;
        drained += field
            .basins
            .iter()
            .zip(&field.states)
            .filter(|(_, s)| **s != State::Wet)
            .map(|(b, _)| super::geom::signed_area(&b.ring).abs())
            .sum::<f64>();
        fields.push(field);
    }
    // the coarse grain: a drained winter paddy grows its barley acre for acre; what is left goes to the dry hem of the first field
    let dry_need = if is("winter_crop", "barley") {
        (need - drained).max(0.0)
    } else {
        need
    };
    // a wild middle keeps the hem to the toe, climbing up the far flank from the foot only as far as the grain asks; a cleared
    // one hems the whole canal, the upper edge too (fields_for draws at least one field)
    let (drawn, room) = {
        let f = &mut fields[0];
        let far = -inp.brook_side;
        // the flank's drawn course from the foot up, every edge step; a cleared middle carries on across the head
        let steps = 24_u32;
        let mut line: Vec<Pt> = (0..=steps)
            .map(|k| {
                f.fan
                    .at(f.fan.length * (1.0 - f64::from(k) / f64::from(steps)), far)
            })
            .collect();
        if !is("fan_middle", "wild") {
            line.extend((1..=steps).map(|k| {
                f.fan
                    .at(0.0, far - 2.0 * far * f64::from(k) / f64::from(steps))
            }));
        }
        let out = (f.fan.across.0 * far, f.fan.across.1 * far);
        let mut ix = Index::default();
        for (a, b, w) in &f.segments {
            ix.file_w(*a, *b, *w);
        }
        let (dry, r) = hem(
            &line,
            out,
            dry_need,
            &f.fan.ring,
            &mut ix,
            1.0,
            inp.seed,
            "f0",
        );
        counts.add("write@dry_plot", 4 * dry.len() as u64);
        #[expect(clippy::cast_precision_loss, reason = "a hamlet's hundred dry plots")]
        let plots = dry.len() as f64;
        f.dry = dry;
        (plots * super::dry::PLOT_FT.0 * super::dry::PLOT_FT.1, r)
    };
    Ok(FieldOut {
        knobs,
        fields,
        grain: (
            drawn / SQ_FT_PER_ACRE,
            dry_need / SQ_FT_PER_ACRE,
            room / SQ_FT_PER_ACRE,
        ),
        counts: counts.0,
    })
}

/// One field on its fan.
///
/// Research:
///     the weir - research/questions/0059-where-the-ditch-leaves-the-brook-the-intake-and-its-weir-toshuko-and-seki.drawing.html: a weir hamlet's weir in one of four forms, each its own thickness - drawn only where the `intake` knob is a weir, a form missing from the table at the thinnest, the fence's 1.5 ft
///     the basins' rules where decided - research/questions/0005-rice-paddies-and-their-plots-suiden.drawing.html: no basin sharper than 25 degrees, none under a quarter of its cell, none an arrowhead - asked of each row's two outermost basins, where the fan's taper makes them sharpest (D7)
///     the field off the brook - research/questions/0059-where-the-ditch-leaves-the-brook-the-intake-and-its-weir-toshuko-and-seki.drawing.html: the fan of paddies is cut away from the brook, leaving the stream its margin - an outline point within the brook's skirt refuses the field
///     resting plots - research/questions/0013-paddies-left-to-rest-kataarashi.drawing.html: an unsettled settlement rests two to four whole plots (`paddy_rest`, rolled)
///     the grave's form - research/questions/0008-ponds-rocks-and-graves-in-the-middle-of-the-fields.drawing.html: an island inside a plot or a grave in a plot's corner - the `grave_form` knob's, an island where the knob gave none
///     the water filed - NONE: each ditch's segments at the wider of its two ends, the brook at its width, so every test of the water asks its widest
fn one(
    inp: &FieldIn,
    f: &Fan,
    tag: &str,
    knobs: &HashMap<String, String>,
    counts: &mut Counts,
) -> Result<Field, FieldRefused> {
    let br = brook(f, inp.brook_side, inp.brook, inp.canvas);
    counts.add("write@brook", 2 * br.pts.len() as u64);
    let weir = knobs.get("intake").filter(|v| *v == "weir").map(|_| {
        let form = knobs.get("weir_form").cloned().unwrap_or_default();
        let thick = inp.weir.2.get(&form).copied().unwrap_or(WEIR_THIN_FT);
        let (ring, deg) = weir(&br, f, inp.brook_side, inp.weir.0, inp.weir.1, thick);
        (ring, deg, form)
    });
    counts.add("write@intake", 10);
    let bs = basins(f, inp.seed, inp.row_ft);
    // the comb's angles tested once a row, at its two outermost basins, the sharpest (D7)
    let rows = bs.iter().map(|b| b.row).max().map_or(0, |r| r + 1);
    for row in 0..rows {
        let ends = [
            bs.iter().find(|b| b.row == row),
            bs.iter().rev().find(|b| b.row == row),
        ];
        for b in ends.into_iter().flatten() {
            held(&b.ring, inp.cell)?;
        }
    }
    counts.add("write@basin", 5 * bs.len() as u64);
    let chans = channels(
        f,
        br.intake,
        (&inp.offtakes.0, &inp.offtakes.1),
        inp.row_ft,
        inp.brook_side,
        inp.seed,
    );
    let mut ix = Index::default();
    let mut segments = Vec::new();
    let mut widths = Vec::new();
    for c in &chans {
        for w in c.pts.windows(2) {
            ix.file(w[0], w[1]);
            widths.push(c.w.max(c.w_tail));
            segments.push((w[0], w[1], c.w.max(c.w_tail)));
        }
    }
    for id in file_brook(&br, &mut ix) {
        let (a, b) = ix.segs[id];
        widths.push(inp.brook.w);
        segments.push((a, b, inp.brook.w));
    }
    // the outline placed point by point, each point asked of the brook in its cells: the field keeps outside the brook's skirt
    let mut brook_ix = Index::default();
    file_brook(&br, &mut brook_ix);
    for p in &f.ring {
        let d = clearance(*p, 2.0 * inp.brook.skirt, &mut brook_ix);
        if d < inp.brook.skirt - 1e-6 {
            return Err(FieldRefused {
                rule: "the brook's skirt",
                detail: format!("an outline point {d:.1} ft from the brook"),
            });
        }
    }
    counts.add("candidate@outline", 2 * f.ring.len() as u64);
    counts.add("write@ditch", segments.len() as u64);
    counts.add("write@water_index", ix.touched + brook_ix.touched);
    let unsettled = knobs.get("paddy_rest").is_some_and(|v| v == "unsettled");
    let st = states(&bs, inp.seed, tag, unsettled);
    counts.add(
        "write@drawn_apart",
        2 * st.iter().filter(|s| **s != State::Green).count() as u64,
    );
    let beans = bean_runs(&bs, inp.seed, tag, &mut ix, &widths);
    counts.add(
        "write@bean",
        2 * beans.iter().map(Vec::len).sum::<usize>() as u64,
    );
    let pond = pocket_pond(&bs, inp.seed, tag);
    let form =
        knobs.get("grave_form").map_or(
            "island",
            |v| if v == "corner" { "corner" } else { "island" },
        );
    let gr = grave(&bs, inp.seed, tag, form, pond.map(|(i, _)| i), inp.cell)?;
    counts.add("write@feature", 6);
    Ok(Field {
        fan: f.clone(),
        brook: br,
        weir,
        basins: bs,
        states: st,
        channels: chans,
        beans,
        dry: Vec::new(),
        pond,
        grave: gr,
        segments,
    })
}

#[cfg(test)]
mod tests {
    use std::collections::HashMap;

    use super::{build, FieldIn};
    use crate::field::brook::BrookIn;
    use crate::field::lattice::ROW_FT;
    use crate::field::states::State;

    fn inp(households: u32, seed: i64) -> FieldIn {
        FieldIn {
            seed,
            households,
            down_deg: 90.0,
            aspect: 1.0,
            center: (3200.0, 3200.0),
            canvas: (6400.0, 6400.0),
            brook_side: 1.0,
            brook: BrookIn {
                lead: 105.0,
                offtake_deg: 35.0,
                tap_run: 70.0,
                slew: 22.0,
                skirt: 34.0,
                wander: 10.0,
                station: 35.0,
                w: 7.0,
            },
            offtakes: (vec![0.30, 0.62, 0.93], vec![0.55]),
            weir: (7.0, 30.0, HashMap::from([("fence".to_owned(), 1.5)])),
            row_ft: ROW_FT,
            cell: 1488.0,
            knobs: vec![
                (
                    "intake".to_owned(),
                    vec!["weir".to_owned(), "open".to_owned()],
                    vec![],
                    Some("weir".to_owned()),
                ),
                (
                    "weir_form".to_owned(),
                    vec!["fence".to_owned()],
                    vec![],
                    None,
                ),
                (
                    "paddy_rest".to_owned(),
                    vec!["settled".to_owned(), "unsettled".to_owned()],
                    vec![0.8, 0.2],
                    None,
                ),
                (
                    "winter_crop".to_owned(),
                    vec!["barley".to_owned(), "none".to_owned()],
                    vec![0.5, 0.5],
                    Some("none".to_owned()),
                ),
                (
                    "fan_middle".to_owned(),
                    vec!["wild".to_owned(), "cleared".to_owned()],
                    vec![0.75, 0.25],
                    None,
                ),
                (
                    "grave_form".to_owned(),
                    vec!["island".to_owned(), "corner".to_owned()],
                    vec![],
                    None,
                ),
                ("unused".to_owned(), vec![], vec![], None),
            ],
        }
    }

    #[test]
    fn a_hamlet_s_comb_end_to_end() {
        let out = build(&inp(20, 4)).unwrap();
        assert_eq!(out.fields.len(), 1);
        let f = &out.fields[0];
        assert!(f.basins.len() > 400);
        assert_eq!(f.states.len(), f.basins.len());
        assert!(f.states.contains(&State::Wet));
        assert!(f.weir.is_some(), "the pinned weir");
        assert!(!f.beans.is_empty() && !f.dry.is_empty());
        let (drawn, need, room) = out.grain;
        assert!(drawn >= need && room >= drawn, "{:?}", out.grain);
        let (dx, dy) = f.fan.down;
        let toe_first = f
            .dry
            .first()
            .map(|d| (d.poly[0].0 - f.fan.fork.0) * dx + (d.poly[0].1 - f.fan.fork.1) * dy);
        assert!(toe_first.unwrap() > f.fan.length * 0.66);
        assert_eq!(out.knobs["winter_crop"], "none");
        assert!(!out.knobs.contains_key("unused"));
        assert!(!f.segments.is_empty());
        let past_cap = build(&inp(220, 4)).unwrap();
        assert!(past_cap.fields.len() >= 3, "several fields past the cap");
        let mut barley = inp(20, 5);
        barley.knobs[3].3 = Some("barley".to_owned());
        let b = build(&barley).unwrap();
        assert!(b.grain.1 < 1e-9 && b.fields[0].dry.is_empty());
        let mut open = inp(20, 4);
        open.knobs[0].3 = Some("open".to_owned());
        assert!(build(&open).unwrap().fields[0].weir.is_none());
        // a race leaving along the fall from beside the corner itself brings the brook past it within its skirt: refused by name
        let mut hug = inp(20, 4);
        hug.brook.offtake_deg = 0.0;
        hug.brook.lead = 5.0;
        assert_eq!(build(&hug).unwrap_err().rule, "the brook's skirt");
    }
}
