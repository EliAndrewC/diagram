//! The comb stage end to end (feature 444 T16): the stage's own knobs rolled, the fields counted under the cap, and each field
//! built - fan, brook and weir, lattice held to its rules, channels, the water index, the plots drawn apart, beans, the dry hem,
//! the pocket pond and the grave - with the derivation's counts (D6).
//!
//! Research:
//!     the comb - research/questions/0005-rice-paddies-and-their-plots-suiden.drawing.html: the fan of paddies, its basins and bunds

use std::collections::HashMap;

use super::beans::bean_runs;
use super::brook::{brook, clearance, weir, Brook, BrookIn};
use super::channels::{channels, Channel};
use super::dry::{hem, DryPlot, GRAIN_ACRES_PER_HOUSEHOLD, MAX_BANDS};
use super::fan::{fan, Fan, Pt};
use super::features::{grave, pocket_pond, Grave, Pond};
use super::index::Index;
use super::lattice::{basins_counted, Basin};
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
    /// The water index of `segments`, each at its width: the field's beans and the hem ask it, filed once.
    pub water: Index,
    /// Each basin's box (x0, y0, x1, y1), middle and area (square feet), from one walk of its ring (`ring_stats`): the field's
    /// record and the barley's ground read them, no ring walked again (the work-budget audit, T16).
    pub stats: Vec<RingStats>,
    /// The field's plots' area (square feet), summed as their `stats` were read; the low row's plots (the last the lattice laid)
    /// and the resting plots (`states`), so the drained plots' area is the field's less theirs, with no walk of the basins.
    pub area: f64,
    /// The plots' box (x0, y0, x1, y1), the ink's floor's clip.
    pub plots_box: [f64; 4],
    pub low: std::ops::Range<usize>,
    pub rested: Vec<usize>,
}

/// A ring's box (x0, y0, x1, y1), middle (the mean of its points) and area (square feet).
///
/// Research:
///     the plot's figures - NONE: geometry of the ring, the record's type
pub type RingStats = ([f64; 4], Pt, f64);

/// A ring's `RingStats` in one walk, each figure as the record has always taken it: the box's least and most, the points' mean,
/// the shoelace sum's half, unsigned.
///
/// Research:
///     the plot's figures - NONE: geometry of the ring; what they record is the field record's
fn ring_stats(ring: &[Pt]) -> RingStats {
    let n = ring.len();
    let (mut bx, mut s, mut cross) = (
        [
            f64::INFINITY,
            f64::INFINITY,
            f64::NEG_INFINITY,
            f64::NEG_INFINITY,
        ],
        (0.0, 0.0),
        0.0,
    );
    for (i, p) in ring.iter().enumerate() {
        bx = [
            bx[0].min(p.0),
            bx[1].min(p.1),
            bx[2].max(p.0),
            bx[3].max(p.1),
        ];
        s = (s.0 + p.0, s.1 + p.1);
        let q = ring[(i + 1) % n];
        cross += p.0 * q.1 - q.0 * p.1;
    }
    #[expect(clippy::cast_precision_loss, reason = "a ring of a handful of points")]
    let m = n as f64;
    (bx, (s.0 / m, s.1 / m), cross.abs() / 2.0)
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
///     the hem's line - research/questions/0011-where-a-farming-hamlet-grew-its-coarse-grain.drawing.html: where the middle is left wild the dry plots climb from the toe into the middle, as far as `hem_bounds` lets them; on a fan whose middle is cleared, the cleared ground is drawn only as the hem along the whole canal, one band of its tracts whatever the grain asks - canal A's, the first field's far flank up from its foot, and across its head where cleared
///     the brook's flank unhemmed - GUESS: research/questions/0011-where-a-farming-hamlet-grew-its-coarse-grain.drawing.html silent on dry plots between canal B and the brook; that flank left to the brook's skirt, the hem the high margin's
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
    let area = paddy / f64::from(n);
    // the first field's fan, laid once: the next fields step from it, and the first IS it (the work-budget audit at T16's
    // landing: the same fan traced twice for the first field)
    let first = laid_fan(inp, area, inp.center, inp.seed, &mut counts);
    for k in 0..n {
        let tag = format!("f{k}");
        let f = if k == 0 {
            first.clone()
        } else {
            // the next field beside the last, across the fall, past its brook's skirt
            let step = (first.half_head + first.half_foot)
                + 2.0 * (inp.brook.skirt + inp.brook.wander)
                + inp.brook.w;
            let off = step * f64::from(k);
            let center = (
                inp.center.0 + first.across.0 * off,
                inp.center.1 + first.across.1 * off,
            );
            laid_fan(inp, area, center, inp.seed + i64::from(k), &mut counts)
        };
        let field = one(inp, &f, (&tag, k == 0), &knobs, &mut counts)?;
        // the drained plots' area, read only where the barley counts it (the audit, T16: every roll walked every ring for it)
        if is("winter_crop", "barley") {
            drained += drained_area(&field, &mut counts);
        }
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
        // the field's own water index, filed once in `one`: only what the hem's queries add is counted here
        let ix = &mut f.water;
        let before = (ix.touched, ix.examined, ix.tests);
        let (dry, r, tested) = hem(
            &line,
            out,
            f.fan.down,
            hem_bounds(
                is("fan_middle", "wild"),
                is("winter_crop", "barley"),
                dry_need,
            ),
            &f.fan.ring,
            ix,
            1.0,
            inp.seed,
            "f0",
        );
        counts.add("write@dry_plot", 4 * dry.len() as u64);
        // the hem's index and its grid of laid plots: their cells and what their queries handed back
        counts.add("write@hem_index", ix.touched - before.0);
        counts.add("candidate@hem_index", ix.examined - before.1);
        counts.add("pt_test@hem_onto", tested);
        counts.add("pt_test@hem_refused", ix.tests - before.2);
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

/// The comb's angles tested once a row, at its two outermost basins, where the fan's taper makes them sharpest (D7): each row's
/// first and last basin found in one pass over the basins, not a search of them all per row.
///
/// Research:
///     the basins' rules where decided - research/questions/0005-rice-paddies-and-their-plots-suiden.drawing.html: no basin sharper than 25 degrees, none under a quarter of its cell, none an arrowhead - asked of each row's two outermost basins, where the fan's taper makes them sharpest (D7)
///
/// # Errors
/// `FieldRefused` when an outermost basin breaks a basin's rule.
fn rows_held(
    bs: &[Basin],
    ends: &[(usize, usize)],
    cell: f64,
    counts: &mut Counts,
) -> Result<(), FieldRefused> {
    // the rows' ends as the lattice recorded them while it laid the comb (the work-budget audit, T16: two walks of the basins)
    counts.add("candidate@rows_held", 2 * ends.len() as u64);
    for &(first, last) in ends {
        for i in std::iter::once(first).chain((last != first).then_some(last)) {
            held(&bs[i].ring, cell)?;
            counts.add("candidate@held", bs[i].ring.len() as u64);
        }
    }
    Ok(())
}

/// A water segment and its width (feet).
///
/// Research:
///     the segment - NONE: a tuple of the water index's, deciding nothing about the place
type Seg = (Pt, Pt, f64);

/// The field's water index (D5): the brook filed first, so the outline - placed point by point, each point asked of the brook in
/// its cells - keeps outside the brook's skirt while the index holds only the brook (one index, not a second of the brook's own:
/// the MODE BUDGET, T16); then the ditches, each segment at the wider of its two ends. Returns the index and the segments.
///
/// Research:
///     the field off the brook - research/questions/0059-where-the-ditch-leaves-the-brook-the-intake-and-its-weir-toshuko-and-seki.drawing.html: the fan of paddies is cut away from the brook, leaving the stream its margin - an outline point within the brook's skirt refuses the field
///     the water filed - NONE: each ditch's segments at the wider of its two ends, the brook at its width, so every test of the water asks its widest
///
/// # Errors
/// `FieldRefused` when an outline point stands within the brook's skirt.
fn water(
    chans: &[Channel],
    br: &Brook,
    inp: &FieldIn,
    f: &Fan,
    counts: &mut Counts,
) -> Result<(Index, Vec<Seg>), FieldRefused> {
    let mut ix = Index::default();
    let mut segments = Vec::new();
    for c in chans {
        for w in c.pts.windows(2) {
            segments.push((w[0], w[1], c.w.max(c.w_tail)));
        }
    }
    let ditches = segments.len();
    segments.extend(br.pts.windows(2).map(|p| (p[0], p[1], inp.brook.w)));
    for (a, b, w) in &segments[ditches..] {
        ix.file_w(*a, *b, *w);
    }
    for p in &f.ring {
        // asked within the skirt itself: a segment nearer than the skirt crosses the box the skirt draws round the point, so the
        // twice-the-skirt box this asked before read four times the cells for the same answer (the MODE BUDGET, T16)
        let d = clearance(*p, inp.brook.skirt, &mut ix);
        if d < inp.brook.skirt - 1e-6 {
            return Err(FieldRefused {
                rule: "the brook's skirt",
                detail: format!("an outline point {d:.1} ft from the brook"),
            });
        }
    }
    for (a, b, w) in &segments[..ditches] {
        ix.file_w(*a, *b, *w);
    }
    counts.add("candidate@outline", 2 * f.ring.len() as u64);
    counts.add("write@ditch", ditches as u64);
    Ok((ix, segments))
}

/// One field on its fan.
///
/// Research:
///     the weir - research/questions/0059-where-the-ditch-leaves-the-brook-the-intake-and-its-weir-toshuko-and-seki.drawing.html: a weir hamlet's weir in one of four forms, each its own thickness - drawn only where the `intake` knob is a weir, a form missing from the table at the thinnest, the fence's 1.5 ft
///     resting plots - research/questions/0013-paddies-left-to-rest-kataarashi.drawing.html: an unsettled settlement rests two to four whole plots (`paddy_rest`, rolled)
///     the grave's form - research/questions/0008-ponds-rocks-and-graves-in-the-middle-of-the-fields.drawing.html: an island inside a plot or a grave in a plot's corner - the `grave_form` knob's, an island where the knob gave none
///     the intake's place and siting - research/questions/0059-where-the-ditch-leaves-the-brook-the-intake-and-its-weir-toshuko-and-seki.drawing.html: the intake at the left, the center or the right of the fan's head, and (research/questions/0059-where-the-ditch-leaves-the-brook-the-intake-and-its-weir-toshuko-and-seki.html) in a straight reach or on the outside of a bend - the `intake_place` knob rolling the head's middle or a shoulder, the shoulder the one on the brook's side (`brook_side`, the plan's), and the `intake_siting` knob, read here for the brook
///     the grave once a map - research/questions/0008-ponds-rocks-and-graves-in-the-middle-of-the-fields.drawing.html: about three maps in ten draw a grave in the fields - rolled once, on the first field
///     the grave off the pond's plot - GUESS: research/questions/0008-ponds-rocks-and-graves-in-the-middle-of-the-fields.drawing.html silent on a grave beside a pocket pond; never in the pond's plot
///     the hem later - NONE: each field built without its dry plots; `build` hems the first one once every field stands
fn one(
    inp: &FieldIn,
    f: &Fan,
    (tag, first): (&str, bool),
    knobs: &HashMap<String, String>,
    counts: &mut Counts,
) -> Result<Field, FieldRefused> {
    let center = knobs.get("intake_place").is_some_and(|v| v == "center");
    let straight = knobs.get("intake_siting").is_some_and(|v| v == "straight");
    let br = brook(f, inp.brook_side, inp.brook, (center, straight), inp.canvas);
    counts.add("write@brook", br.work);
    let weir = knobs.get("intake").filter(|v| *v == "weir").map(|_| {
        let form = knobs.get("weir_form").cloned().unwrap_or_default();
        let thick = inp.weir.2.get(&form).copied().unwrap_or(WEIR_THIN_FT);
        let (ring, deg) = weir(&br, f, inp.brook_side, inp.weir.0, inp.weir.1, thick);
        (ring, deg, form)
    });
    counts.add("write@intake", 9);
    let mut work = 0;
    let mut ends = Vec::new();
    let bs = basins_counted(f, inp.seed, inp.row_ft, &mut work, &mut ends);
    counts.add("write@basin", work);
    let (stats, area, plots_box) = plot_figures(&bs, counts);
    rows_held(&bs, &ends, inp.cell, counts)?;
    let (chans, probes) = channels(
        f,
        br.intake,
        (&inp.offtakes.0, &inp.offtakes.1),
        inp.row_ft,
        inp.brook_side,
        center,
        inp.seed,
    );
    // the canals' courses as laid, each flank point a write, and each offtake's lean as it was asked (the work-budget audit, T16)
    counts.add(
        "write@channel_pts",
        chans.iter().map(|c| c.pts.len() as u64).sum(),
    );
    counts.add("pt_test@offtake_lines", probes);
    let (ix, _segments) = water(&chans, &br, inp, f, counts)?;
    let unsettled = knobs.get("paddy_rest").is_some_and(|v| v == "unsettled");
    let mut work = 0;
    let (st, rested) = states(&bs, inp.seed, tag, &ends, unsettled, &mut work);
    counts.add("candidate@states", work);
    counts.add(
        "write@drawn_apart",
        2 * st.iter().filter(|s| **s != State::Green).count() as u64,
    );
    let mut work = 0;
    let beans = bean_runs(&bs, inp.seed, tag, &mut work);
    counts.add("write@bean", work);
    let mut work = 0;
    #[expect(
        clippy::range_plus_one,
        reason = "a half-open range, the type `Field::low` keeps"
    )]
    let low = ends.last().map_or(0..0, |e| e.0..e.1 + 1);
    let pond = pocket_pond(&bs, Some(low.clone()), inp.seed, tag, &mut work);
    let form =
        knobs.get("grave_form").map_or(
            "island",
            |v| if v == "corner" { "corner" } else { "island" },
        );
    // a map's grave, at its odds once: only the first field may hold it
    let gr = grave(
        if first { &bs } else { &[] },
        inp.seed,
        tag,
        form,
        pond.map(|(i, _)| i),
        inp.cell,
        &mut work,
    )?;
    counts.add("candidate@feature", work);
    // the water index's cells and the segments its queries handed back, the beans' among them (the audit, T16)
    counts.add("write@water_index", ix.touched);
    counts.add("candidate@water_index", ix.examined);
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
        water: ix,
        stats,
        area,
        plots_box,
        low,
        rested,
    })
}

/// Each basin's `RingStats`, the field's area and its plots' box (x0, y0, x1, y1): each ring walked once, then its figures read
/// once for the area and the box, both counted.
///
/// Research:
///     the plots' figures - NONE: geometry of the rings; what they record is the field record's
fn plot_figures(bs: &[Basin], counts: &mut Counts) -> (Vec<RingStats>, f64, [f64; 4]) {
    let stats: Vec<RingStats> = bs.iter().map(|b| ring_stats(&b.ring)).collect();
    // the field's area and its plots' box, read off each plot's figures once (the ink's floor takes the box: 444 T16's audit)
    counts.add("candidate@plots_box", stats.len() as u64);
    let area: f64 = stats.iter().map(|x| x.2).sum();
    let plots_box = stats.iter().fold(
        [
            f64::INFINITY,
            f64::INFINITY,
            f64::NEG_INFINITY,
            f64::NEG_INFINITY,
        ],
        |b, x| {
            [
                b[0].min(x.0[0]),
                b[1].min(x.0[1]),
                b[2].max(x.0[2]),
                b[3].max(x.0[3]),
            ]
        },
    );
    counts.add(
        "write@plot_record",
        bs.iter().map(|b| b.ring.len() as u64).sum(),
    );
    (stats, area, plots_box)
}

/// A field's fan of `area` square feet at `center`, rolled from `seed`: its two traces and its area's walk counted.
///
/// Research:
///     the fan - NONE: the fan's own claims are `fan::fan`'s; this counts its work
fn laid_fan(
    inp: &FieldIn,
    area: f64,
    center: Pt,
    seed: i64,
    counts: &mut Counts,
) -> super::fan::Fan {
    let laid = fan(area, inp.aspect, inp.down_deg, center, seed);
    counts.add("write@fan_outline", 3 * laid.ring.len() as u64);
    laid
}

/// The area of a field's drained plots (square feet), neither wet nor resting - the barley's ground, read from each plot's
/// `stats`.
///
/// Research:
///     the drained plots - research/questions/0011-where-a-farming-hamlet-grew-its-coarse-grain.drawing.html: barley followed the rice on a paddy that drained, never on a wet one, so only the drained plots count
///     no barley on a resting plot - research/questions/0013-paddies-left-to-rest-kataarashi.drawing.html: a resting plot is grazed among the cropped ones that year, not cropped, so it grows no winter barley - its area taken out with the wet plots'
fn drained_area(field: &Field, counts: &mut Counts) -> f64 {
    // only the low row is ever wet (`states`), and the rested plots are named: the field's area less theirs
    counts.add(
        "candidate@drained",
        (field.low.len() + field.rested.len()) as u64,
    );
    let wet: f64 = field
        .low
        .clone()
        .filter(|&i| field.states[i] == State::Wet)
        .map(|i| field.stats[i].2)
        .sum();
    let rested: f64 = field.rested.iter().map(|&i| field.stats[i].2).sum();
    field.area - wet - rested
}

/// The hem's bounds, (the grain it holds, the bands it may climb): a wild middle's hem climbs until the grain is held where the
/// paddy lies bare over the winter, and stays on the toe, one band, where it carries barley; a cleared middle's is the one band
/// along the whole canal, whatever the grain asks.
///
/// Research:
///     the hem's climb - research/questions/0011-where-a-farming-hamlet-grew-its-coarse-grain.drawing.html: where a hamlet's paddy lies bare over the winter its dry fields climb from the toe into the wild middle until they hold the grain; where it carries barley its dry fields stay on the toe; a cleared middle drawn only as the hem along the whole canal - the toe one band, the climb bounded only by `MAX_BANDS`, a guard far past any canvas
///     a barley hamlet's shortfall - GUESS: research/questions/0011-where-a-farming-hamlet-grew-its-coarse-grain.drawing.html silent on where the grain goes when the toe's one band holds less than the drained barley left owed; drawn short, the shortfall recorded beside the need (`grain`: drawn, needed, the room), never refused
fn hem_bounds(wild: bool, barley: bool, need: f64) -> (f64, u32) {
    match (wild, barley) {
        (true, false) => (need, MAX_BANDS),
        (true, true) => (need, 1),
        (false, _) => (f64::INFINITY, 1),
    }
}

#[cfg(test)]
mod tests {
    use std::collections::HashMap;

    use super::{build, hem_bounds, FieldIn};
    use crate::field::brook::BrookIn;
    use crate::field::dry::MAX_BANDS;
    use crate::field::lattice::ROW_FT;
    use crate::field::states::State;

    #[test]
    fn a_barley_hamlets_hem_stays_on_the_toe() {
        assert_eq!(hem_bounds(true, false, 9.0), (9.0, MAX_BANDS));
        assert_eq!(hem_bounds(true, true, 9.0), (9.0, 1));
        assert_eq!(hem_bounds(false, false, 9.0), (f64::INFINITY, 1));
        assert_eq!(hem_bounds(false, true, 9.0), (f64::INFINITY, 1));
    }

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
        assert!(!f.water.segs.is_empty());
        let past_cap = build(&inp(220, 4)).unwrap();
        assert!(past_cap.fields.len() >= 3, "several fields past the cap");
        let mut barley = inp(20, 5);
        barley.knobs[3].3 = Some("barley".to_owned());
        let b = build(&barley).unwrap();
        assert!(b.grain.1 < 1e-9 && b.fields[0].dry.is_empty());
        // ...and on an unsettled field the resting plots and the wet ones are taken out of the barley's ground
        barley.knobs[2].3 = Some("unsettled".to_owned());
        let u = build(&barley).unwrap();
        let f0 = &u.fields[0];
        assert!(!f0.rested.is_empty() && f0.low.clone().any(|i| f0.states[i] == State::Wet));
        assert!(
            u.grain.1
                <= b.grain.1
                    + f0.rested.iter().map(|&i| f0.stats[i].2).sum::<f64>() / 43_560.0
                    + 1e-9
        );
        let mut open = inp(20, 4);
        open.knobs[0].3 = Some("open".to_owned());
        assert!(build(&open).unwrap().fields[0].weir.is_none());
        // the intake straight into the head's middle: the fork there, the brook still clear of the field
        let mut middle = inp(20, 4);
        middle.knobs.push((
            "intake_place".to_owned(),
            vec![],
            vec![],
            Some("center".to_owned()),
        ));
        middle.knobs.push((
            "intake_siting".to_owned(),
            vec![],
            vec![],
            Some("straight".to_owned()),
        ));
        let m = build(&middle).unwrap();
        let fork = super::super::channels::division(&m.fields[0].fan, 1.0, true);
        assert!(m.fields[0].channels[0]
            .pts
            .last()
            .is_some_and(|p| super::super::geom::dist(*p, fork) < 1e-6));
        // a race leaving along the fall from beside the corner itself brings the brook past it within its skirt: refused by name
        let mut hug = inp(20, 4);
        hug.brook.offtake_deg = 0.0;
        hug.brook.lead = 5.0;
        assert_eq!(build(&hug).unwrap_err().rule, "the brook's skirt");
    }
}
