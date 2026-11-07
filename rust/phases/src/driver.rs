//! The hamlet driver (feature 444 T42, FR-024 part 5): a pool hamlet rolled from its spec through the plan and the Rust stages
//! through the cut, its map written as SVG and its record as JSON, with no Python. Enabled stage by stage, each once it draws:
//! the water frame and the field first. What each stage is handed and what the deleted Python drew is
//! `specs/444-work-budget-program/t42-brief.md`.
//!
//! Research:
//!     the driver - NONE: the stages' plumbing; each placement is claimed at the Rust that makes it

pub mod plan;
pub mod spec;
pub mod svg;

use std::collections::{BTreeMap, HashMap};
use std::fmt::Write as _;

use crate::field::brook::BrookIn;
use crate::field::build::{build, Field, FieldIn, KnobIn};
use crate::field::states::State;
use plan::Plan;
use svg::{ink, Svg, BUND_W};

/// The brook's figures handed the field: the offtake's angle, the tap's run, the slew, the skirt, the wander and the station
/// spacing (ft and degrees), and its drawn width.
///
/// Research:
///     the brook's course - research/questions/0054-which-way-water-flows-and-how-channels-bend-and-join.drawing.html: a brook wanders and slews down its valley; the figures the deleted `consts_water.py` held, each its own GUESS there
///     the brook's width - research/questions/0068-how-wide-canals-and-ditches-are-the-ladder-of-channel-widths.drawing.html: a village creek at roughly three and a half times the 1.5 ft floor, 5.25 ft
const OFFTAKE_DEG: f64 = 35.0;
const BROOK_TAP_RUN: f64 = 70.0;
const BROOK_SLEW: f64 = 22.0;
const BROOK_SKIRT: f64 = 34.0;
const BROOK_WANDER: f64 = 10.0;
const BROOK_STATION: f64 = 20.0;
pub const BROOK_W: f64 = 5.25;
/// The weir's skew off square across the brook, and its thickness by form (ft).
///
/// Research:
///     the weir's skew - research/questions/0059-where-the-ditch-leaves-the-brook-the-intake-and-its-weir-toshuko-and-seki.drawing.html: a weir drawn across the whole brook, diagonally upstream
///     the weir's thickness by form - research/questions/0059-where-the-ditch-leaves-the-brook-the-intake-and-its-weir-toshuko-and-seki.drawing.html: four forms, 1.5 to 5 ft thick
///     the weir keyed into the banks - GUESS: the page silent on how far a weir runs into each bank; a foot either side
const WEIR_SKEW_DEG: f64 = 30.0;
const WEIR_KEY_FT: f64 = 1.0;
/// A basin's cell share along its canal (ft).
///
/// Research:
///     a basin's cell - research/questions/0005-rice-paddies-and-their-plots-suiden.drawing.html: about 48 ft across its canal and 26 to 36 ft along it, the cell the row's spacing times the middle, 31 ft
const CELL_SHARE: f64 = 31.0;
/// The crop's margin round what is drawn (ft).
///
/// Research:
///     the crop - CONVENTION: the deleted `CROP_MARGIN`, the drawing framed to its features with 48 ft round them
const CROP_MARGIN: f64 = 48.0;

/// The field stage's knobs in the order they roll, each with its forms and weights as the registry (`l7r/diagram/knobs.json`) holds
/// them: `plot_regularity` only `organic` on a hamlet, its `grid` form a planned field's.
///
/// Research:
///     the field's knobs - research/questions/0009-the-paddy-through-the-rice-year-flooding-draining-transplanting-and-after-the-harvest.drawing.html: each rolled per settlement from its table and weights (`knobs.json`), a spec's pin standing
///     the planned grid on no hamlet - research/questions/0005-rice-paddies-and-their-plots-suiden.drawing.html: a hamlet's basins organic, "never as the tidy grid"; the grid a planned field's
const FIELD_KNOBS: [(&str, &[&str], &[f64]); 8] = [
    ("town_nearness", &["near", "far"], &[]),
    ("winter_crop", &["barley", "none"], &[0.5, 0.5]),
    ("fan_middle", &["wild", "cleared"], &[0.75, 0.25]),
    ("paddy_rest", &["settled", "unsettled"], &[0.8, 0.2]),
    ("plot_regularity", &["organic"], &[]),
    ("weir_form", &["fence", "gabion", "frame", "crib"], &[]),
    ("intake_place", &["shoulder", "center"], &[]),
    ("intake_siting", &["bend", "straight"], &[]),
];

/// Why a hamlet could not be rolled.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Refused(pub String);

impl std::fmt::Display for Refused {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.write_str(&self.0)
    }
}

/// A rolled hamlet: its plan, the stages run, the field's record, its map and its counted work.
#[derive(Debug)]
pub struct Rolled {
    pub plan: Plan,
    pub stages: Vec<&'static str>,
    pub knobs: HashMap<String, String>,
    pub fields: Vec<Field>,
    pub brooks: Vec<Vec<(f64, f64)>>,
    pub counts: HashMap<String, u64>,
    pub svg: String,
}

fn field_in(p: &Plan) -> FieldIn {
    let knobs: Vec<KnobIn> = FIELD_KNOBS
        .iter()
        .map(|(name, forms, weights)| {
            (
                (*name).to_owned(),
                forms.iter().map(|s| (*s).to_owned()).collect(),
                weights.to_vec(),
                p.pins.get(*name).cloned(),
            )
        })
        .chain(std::iter::once((
            "intake".to_owned(),
            vec![p.knob("intake").to_owned()],
            vec![],
            Some(p.knob("intake").to_owned()),
        )))
        .collect();
    let weir_half = BROOK_W / 2.0 / WEIR_SKEW_DEG.to_radians().cos() + WEIR_KEY_FT;
    let thick: HashMap<String, f64> = [
        ("fence", 1.5),
        ("gabion", 2.0),
        ("frame", 5.0),
        ("crib", 5.0),
    ]
    .iter()
    .map(|(k, v)| ((*k).to_owned(), *v))
    .collect();
    let row_ft = crate::field::lattice::row_ft_for(p.knob("plot_size"));
    FieldIn {
        seed: p.seed,
        households: p.households,
        down_deg: p.down_deg,
        aspect: p.fan_aspect,
        center: (p.w / 2.0, p.h / 2.0),
        canvas: (p.w, p.h),
        brook_side: p.knob("brook_side").parse().unwrap_or(1.0),
        brook: BrookIn {
            lead: p.head_lead,
            offtake_deg: OFFTAKE_DEG,
            tap_run: BROOK_TAP_RUN,
            slew: BROOK_SLEW,
            skirt: BROOK_SKIRT,
            wander: BROOK_WANDER,
            station: BROOK_STATION,
            w: BROOK_W,
        },
        offtakes: p.offtakes.clone(),
        weir: (weir_half, WEIR_SKEW_DEG, thick),
        row_ft,
        cell: row_ft * CELL_SHARE,
        knobs,
    }
}

fn fill(s: State) -> &'static str {
    match s {
        State::Green => ink::RICE_GREEN,
        State::Wet => ink::FLOODED,
        State::Flooded => ink::POND_WATER,
        State::Gold => ink::RIPE_GOLD,
        State::Rest => ink::REST_GRASS,
    }
}

/// The field drawn as the deleted `ink.draw` drew it: the fan's floor, the paddies by state, then the water - the ditches by
/// role, the brook's bed and sheen - the beans, the weir, the pocket pond and the grave.
///
/// Research:
///     the field's floor - CONVENTION: the fan's ring in the rice green beneath its plots, so no seam shows between them
///     ditches by role - research/questions/0053-irrigation-canals-and-how-they-are-laid-out-yosuiro.drawing.html: supply and drainage kept apart; drawn in two hues, a map drawing convention
fn draw_field(svg: &mut Svg, f: &Field, brook: &[(f64, f64)]) {
    svg.polygon(&f.fan.ring, ink::RICE_GREEN, None);
    for (b, s) in f.basins.iter().zip(&f.states) {
        svg.polygon(&b.ring, fill(*s), Some((ink::AZE, BUND_W)));
    }
    for c in &f.channels {
        svg.taper(
            &c.pts,
            if c.role == "drain" {
                ink::DRAIN
            } else {
                ink::SUPPLY
            },
            c.w,
            c.w_tail,
        );
    }
    svg.unframed(brook, ink::POND_WATER, BROOK_W);
    svg.group(0.55);
    svg.unframed(brook, ink::SHEEN, (0.35 * BROOK_W).max(2.0));
    svg.close();
    svg.group(0.85);
    for run in &f.beans {
        for p in run {
            svg.ellipse(*p, 1.5, 1.5, ink::BEAN, None);
        }
    }
    svg.close();
    if let Some((ring, _deg, _form)) = &f.weir {
        svg.polygon(ring, ink::WEIR_FILL, Some((ink::WEIR_EDGE, 0.6)));
    }
    if let Some((_, q)) = &f.pond {
        svg.ellipse(
            (q.x, q.y),
            q.rx + 2.5,
            q.ry + 2.5,
            ink::FLOODED,
            Some((ink::AZE, 2.2)),
        );
        svg.ellipse(
            (q.x, q.y),
            q.rx,
            q.ry,
            ink::POND_WATER,
            Some((ink::RIM, 1.2)),
        );
    }
    if let Some(g) = &f.grave {
        svg.ellipse(g.at, 6.5, 4.5, ink::MOUND, Some((ink::MOUND_EDGE, 1.2)));
    }
}

#[expect(
    clippy::needless_pass_by_value,
    reason = "`map_err` hands the refusal over by value"
)]
fn field_refused(e: crate::field::rules::FieldRefused) -> Refused {
    Refused(format!("the field refused: {e}"))
}

/// The hamlet rolled from its spec through the stages enabled so far.
///
/// # Errors
/// When the spec asks for a form the driver does not yet draw (a polder), or a stage refuses.
///
/// Research:
///     the stages in order - research/questions/0054-which-way-water-flows-and-how-channels-bend-and-join.drawing.html: the fall and the water decided before anything is placed, the field laid from them
pub fn roll(spec: &spec::Spec) -> Result<Rolled, Refused> {
    let p = plan::plan(spec);
    if plan::POLDERS.contains(&p.archetype.as_str()) {
        return Err(Refused(format!(
            "{}: a polder ({}) is not drawn by the driver yet (feature 444 T42)",
            p.name, p.archetype
        )));
    }
    let mut out = build(&field_in(&p)).map_err(field_refused)?;
    let mut work = 0;
    let mut brooks = Vec::new();
    for f in &mut out.fields {
        let taps: Vec<(f64, f64)> = f
            .channels
            .first()
            .and_then(|c| c.pts.first().copied())
            .into_iter()
            .collect();
        let drawn = crate::course::drawn(&f.brook.pts, BROOK_W, &taps, &mut work);
        if let Some(tap) = f.channels.first_mut().and_then(|c| c.pts.first_mut()) {
            *tap = crate::course::mouth(*tap, &drawn, &mut work);
        }
        brooks.push(drawn);
    }
    *out.counts
        .entry("write@brook_drawn".to_owned())
        .or_insert(0) += work;
    let mut svg = Svg::default();
    for (f, b) in out.fields.iter().zip(&brooks) {
        draw_field(&mut svg, f, b);
    }
    let doc = svg.finish(p.w, p.h, CROP_MARGIN);
    Ok(Rolled {
        plan: p,
        stages: vec!["water_frame", "field"],
        knobs: out.knobs,
        fields: out.fields,
        brooks,
        counts: out.counts,
        svg: doc,
    })
}

fn js(s: &str) -> String {
    let mut o = String::from("\"");
    for c in s.chars() {
        match c {
            '"' => o.push_str("\\\""),
            '\\' => o.push_str("\\\\"),
            '\n' => o.push_str("\\n"),
            c => o.push(c),
        }
    }
    o.push('"');
    o
}

fn ring_js(ring: &[(f64, f64)]) -> String {
    let mut o = String::from("[");
    for (i, (x, y)) in ring.iter().enumerate() {
        let _ = write!(o, "{}[{:.1},{:.1}]", if i == 0 { "" } else { "," }, x, y);
    }
    o.push(']');
    o
}

/// The hamlet's record as JSON: the plan, the rolled forms, the stages run, each field's outline and plots, and the counted work.
#[must_use]
pub fn manifest(r: &Rolled) -> String {
    let p = &r.plan;
    let mut o = String::new();
    let _ = write!(
        o,
        "{{\n \"name\": {},\n \"seed\": {},\n \"households\": {},\n \"generated_by\": \"rust/phases driver (feature 444 T42)\",\n \"stages\": [{}],\n \"down_deg\": {},\n \"water_flow\": {},\n \"windward\": {},\n \"field_archetype\": {},\n \"canvas\": [{}, {}],\n",
        js(&p.name),
        p.seed,
        p.households,
        r.stages.iter().map(|s| js(s)).collect::<Vec<_>>().join(", "),
        p.down_deg,
        p.water_flow,
        js(&p.windward),
        js(&p.archetype),
        p.w,
        p.h
    );
    let knobs: BTreeMap<&String, &String> = p.rolled.iter().chain(r.knobs.iter()).collect();
    let _ = writeln!(
        o,
        " \"knobs\": {{{}}},",
        knobs
            .iter()
            .map(|(k, v)| format!("{}: {}", js(k), js(v)))
            .collect::<Vec<_>>()
            .join(", ")
    );
    o.push_str(" \"fields\": [\n");
    for (i, (f, b)) in r.fields.iter().zip(&r.brooks).enumerate() {
        let states: Vec<String> = f
            .states
            .iter()
            .map(|s| js(&format!("{s:?}").to_lowercase()))
            .collect();
        let _ = writeln!(
            o,
            "  {{\"name\": {}, \"outline\": {}, \"brook\": {}, \"plots\": [{}], \"states\": [{}], \"channels\": [{}]}}{}",
            js(&format!("{}-paddies-{}", p.name, i + 1)),
            ring_js(&f.fan.ring),
            ring_js(b),
            f.basins.iter().map(|x| ring_js(&x.ring)).collect::<Vec<_>>().join(","),
            states.join(","),
            f.channels.iter().map(|c| format!("{{\"role\": {}, \"w\": {:.2}, \"w_tail\": {:.2}, \"pts\": {}}}", js(c.role), c.w, c.w_tail, ring_js(&c.pts))).collect::<Vec<_>>().join(","),
            if i + 1 < r.fields.len() { "," } else { "" }
        );
    }
    o.push_str(" ],\n");
    let counts: BTreeMap<&String, &u64> = r.counts.iter().collect();
    let _ = writeln!(
        o,
        " \"counts\": {{{}}}\n}}",
        counts
            .iter()
            .map(|(k, v)| format!("{}: {}", js(k), v))
            .collect::<Vec<_>>()
            .join(", ")
    );
    o
}

#[cfg(test)]
mod tests {
    use super::{manifest, roll, spec::parse};

    #[test]
    fn a_comb_hamlet_rolls_and_draws_its_field() {
        let r = roll(&parse(r#"{"name": "Inashiro", "seed": 4, "households": 15, "down_deg": 90, "water_sink": "pond", "settlement_form": "nucleated"}"#).unwrap()).unwrap();
        assert_eq!(r.stages, vec!["water_frame", "field"]);
        assert!(!r.fields.is_empty() && !r.fields[0].basins.is_empty());
        assert!(
            r.svg.starts_with("<svg") && r.svg.matches("<path").count() > r.fields[0].basins.len()
        );
        let m = manifest(&r);
        assert!(
            m.contains("\"name\": \"Inashiro\"")
                && m.contains("\"stages\": [\"water_frame\", \"field\"]")
                && m.contains("\"plot_size\"")
        );
    }

    #[test]
    fn a_polder_is_refused_until_the_driver_draws_one() {
        let e = roll(&parse(r#"{"name": "Kuwabata", "seed": 21, "households": 16, "down_deg": 90, "field_archetype": "mulberry_dike_fishpond"}"#).unwrap()).unwrap_err();
        assert!(e.to_string().contains("not drawn by the driver yet"));
    }

    #[test]
    fn every_state_has_its_fill_and_a_field_refusal_names_its_rule() {
        use crate::field::states::State;
        let fills: Vec<&str> = [
            State::Green,
            State::Wet,
            State::Flooded,
            State::Gold,
            State::Rest,
        ]
        .into_iter()
        .map(super::fill)
        .collect();
        assert_eq!(
            fills.iter().collect::<std::collections::HashSet<_>>().len(),
            5
        );
        let e = super::field_refused(crate::field::rules::FieldRefused {
            rule: "a_rule",
            detail: "why".into(),
        });
        assert!(e.0.starts_with("the field refused: "));
    }

    #[test]
    fn a_name_is_escaped_in_the_record() {
        assert_eq!(super::js("a\"b\\c\nd"), "\"a\\\"b\\\\c\\nd\"");
    }
}
