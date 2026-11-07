//! The site plan (feature 444 T42, plan D5): what the deleted `plan_site` resolved before the first stage, in Rust - the canvas
//! from the acreage and the seat's room, the fall and the water frame's 21 knobs (`water_frame::roll_plan`), the field's own rolls.
//! Read from `specs/444-work-budget-program/t42-brief.md`, section 2; each table as the deleted `hamletgen/consts*.py` held it.
//!
//! Research:
//!     the plan's rolls - research/questions/0031-clustered-and-scattered-villages-shuson-sanson.drawing.html: each knob's form rolled per hamlet from the seed, only where the map's form uses it

use std::collections::BTreeMap;

use super::spec::Spec;
use crate::pyrand::knob_rng;
use crate::water_frame::{admitted, roll_plan};

/// The water frame's 21 knobs in the order they roll, each with its table (a table's weights its repeated entries) and branch.
///
/// Research:
///     the knobs' tables - GUESS: rolled per hamlet from their tables, each table's own claim in the deleted `hamletgen/consts*.py` (feature 444 T19), carried here as they stood
///     the settlement form's shares - research/questions/0031-clustered-and-scattered-villages-shuson-sanson.drawing.html: half clustered, three in ten scattered, two in ten as rows
pub const KNOBS: [(&str, &[&str], &str); 21] = [
    (
        "settlement_form",
        &[
            "nucleated",
            "nucleated",
            "nucleated",
            "nucleated",
            "nucleated",
            "dispersed",
            "dispersed",
            "dispersed",
            "linear",
            "linear",
        ],
        "all",
    ),
    (
        "cluster_shape",
        &["round", "round", "elongated", "crescent"],
        "all",
    ),
    ("water_sink", &["pond", "pond", "offmap"], "all"),
    ("lane_skeleton", &["spine", "T", "Y", "cross"], "all"),
    ("lane_web", &["alleys", "back_lane"], "not_dispersed"),
    (
        "bamboo",
        &["homestead", "homestead", "thicket", "both", "none"],
        "all",
    ),
    (
        "grove_sides",
        &["2", "2", "2", "2", "2", "3", "3", "3", "4", "4"],
        "not_nucleated",
    ),
    ("grove_flank", &["-1", "1"], "not_nucleated"),
    ("row_line", &["street", "edge"], "linear"),
    ("row_sides", &["one", "both"], "linear"),
    ("row_water", &["own", "shared"], "linear"),
    ("row_shelter", &["own_grove", "sheltered"], "linear"),
    ("well_siting", &["lane", "cluster"], "all"),
    ("farm_water", &["channel", "well"], "dispersed"),
    ("manure_form", &["heap", "pit"], "all"),
    ("copse_siting", &["among_the_houses"], "all"),
    ("kosatsuba_siting", &["frontage"], "all"),
    (
        "plot_size",
        &["small_irregular", "medium", "medium", "large_block"],
        "all",
    ),
    ("grain_drift", &["-8", "-4", "0", "0", "4", "8"], "all"),
    ("intake", &["weir", "open"], "brook"),
    ("brook_side", &["1", "-1"], "brook"),
];

/// The polder archetypes, laid to the survey grid.
///
/// Research:
///     the polder archetypes - research/questions/0019-polders-fields-diked-against-the-fluctuating-water-weitian-waju.drawing.html: a surveyed grid diked out of standing water
pub const POLDERS: [&str; 2] = ["polder_grid", "mulberry_dike_fishpond"];

/// The fan's aspect, rolled.
///
/// Research:
///     the fan's aspect - GUESS: rolled per hamlet from its table (the deleted `FAN_ASPECTS`)
const FAN_ASPECTS: [f64; 5] = [0.88, 0.95, 1.0, 1.08, 1.16];
/// The head race's lead (ft from the intake to the division), rolled.
///
/// Research:
///     the head race's lead - GUESS: rolled per hamlet from its table (the deleted `HEAD_RACE_LEAD`)
const HEAD_LEAD: [f64; 3] = [80.0, 105.0, 130.0];
/// The ground a homestead takes (ft square), sizing the settlement's band.
///
/// Research:
///     band area - GUESS: no source could speak to it, a value of ours (feature 417 T36 pass P7, 2026-10-25); households times this squared
const HOMESTEAD_GROUND_FT: f64 = 104.0;
/// The seat's standoff and the belt's reach (ft), the room the canvas keeps on every side.
///
/// Research:
///     the seat's room - GUESS: the deleted `SEAT_STANDOFF` 12 ft and `BELT_REACH` 146 ft, the belt's band 100 ft deep inside the drawn 80 to 120 ft (0071), a convention
const SEAT_STANDOFF: f64 = 12.0;
const BELT_REACH: f64 = 146.0;
/// A fan's overhang of its square, carried on every side of the canvas.
///
/// Research:
///     the fan's overhang - GUESS: 0.22, the largest measured 0.20 with a plot row's margin (the deleted `FAN_OVERHANG`)
const FAN_OVERHANG: f64 = 0.22;
/// The back within 45 degrees of the wind.
///
/// Research:
///     the back to the wind - research/questions/0072-shelter-belts-on-a-villages-windward-side-bofurin.drawing.html: the settlement laid out with its back to the wind, within 45 degrees
pub const WIND_BACK_MIN_DOT: f64 = std::f64::consts::FRAC_1_SQRT_2;

/// The resolved plan.
///
/// Research:
///     the plan - NONE: the record's type
#[derive(Debug, Clone)]
pub struct Plan {
    pub name: String,
    pub seed: i64,
    pub households: u32,
    pub archetype: String,
    pub windward: String,
    pub down_deg: f64,
    pub water_flow: f64,
    pub rolled: BTreeMap<String, String>,
    pub fan_aspect: f64,
    pub head_lead: f64,
    pub offtakes: (Vec<f64>, Vec<f64>),
    pub w: f64,
    pub h: f64,
    pub pins: BTreeMap<String, String>,
}

impl Plan {
    /// A rolled knob's form, as its table holds it.
    #[must_use]
    pub fn knob(&self, name: &str) -> &str {
        self.rolled.get(name).map_or("", String::as_str)
    }
}

fn pick<T: Copy>(seed: i64, name: &str, table: &[T]) -> T {
    table[knob_rng(seed, name).randbelow(u32::try_from(table.len()).unwrap_or(u32::MAX)) as usize]
}

/// The delivery-ditch fractions of each canal by household band.
///
/// Research:
///     delivery-ditch count and fractions - GUESS: no source could speak to it, a value of ours (feature 417 T36 pass P7, 2026-10-25); 2, 3 or 4 by household band
#[must_use]
pub fn offtakes_for(households: u32) -> (Vec<f64>, Vec<f64>) {
    if households < 11 {
        (vec![0.36, 0.93], vec![0.55])
    } else if households < 21 {
        (vec![0.30, 0.62, 0.93], vec![0.55])
    } else {
        (vec![0.26, 0.52, 0.78, 0.93], vec![0.6])
    }
}

/// The settlement band's half-depth and half-length (ft) by its households and cluster shape.
///
/// Research:
///     band aspect by shape - GUESS: no source could speak to it, a value of ours (feature 417 T36 pass P7, 2026-10-25); round 2.2, crescent and split 3, elongated 5
///     band floors and caps - GUESS: no source could speak to it, a value of ours (feature 417 T36 pass P7, 2026-10-25); half-depth 112 to 300 ft, half-length 240 to 1,100 ft
#[must_use]
pub fn band_extent(households: u32, shape: &str) -> (f64, f64) {
    let asp = match shape {
        "round" => 2.2,
        "elongated" => 5.0,
        _ => 3.0,
    };
    let area = f64::from(households) * HOMESTEAD_GROUND_FT * HOMESTEAD_GROUND_FT;
    let dep = (area / (asp * std::f64::consts::PI))
        .sqrt()
        .clamp(112.0, 300.0);
    let lat = (area / (std::f64::consts::PI * dep)).clamp(240.0, 1100.0);
    (dep, lat)
}

/// The room the canvas keeps beyond the fan on every side, for the seat with its belt.
///
/// Research:
///     the seat's room - GUESS: a closed-form bound from the seat's own quantities - its depth and standoff, then the farther of its half-length and its windward fringe plus the belt's reach
#[must_use]
pub fn seat_room(households: u32, shape: &str) -> f64 {
    let (dep, lat) = band_extent(households, shape);
    dep + SEAT_STANDOFF + lat.max(WIND_BACK_MIN_DOT * lat + dep + BELT_REACH)
}

/// The canvas's side (ft): the field's square from its acreage, the fan's overhang and the seat's room all round, to 50 ft.
///
/// Research:
///     the canvas - GUESS: a fan fills about 40% of its own box (the deleted `canvas_for`), the span doubled and rounded to 50 ft; working ground the crop cuts away
#[must_use]
pub fn canvas_side(households: u32, shape: &str) -> f64 {
    let field = f64::from(households) * crate::field::ACRES_PER_HOUSEHOLD * 43_560.0;
    let span = ((field / 0.40).sqrt() * 2.0 / 50.0).round() * 50.0;
    ((span * (1.0 + 2.0 * FAN_OVERHANG) + 2.0 * seat_room(households, shape)) / 50.0).round() * 50.0
}

/// The plan from the spec.
///
/// Research:
///     the fall backs the wind - DEVIATION research/questions/0031-clustered-and-scattered-villages-shuson-sanson.drawing.html: a rolled fall only from the falls that leave a windward margin (`water_frame::admitted`)
///     regional wind - research/questions/0072-shelter-belts-on-a-villages-windward-side-bofurin.drawing.html: the northwest unless declared
///     water flow follows the fall - DEVIATION research/questions/0054-which-way-water-flows-and-how-channels-bend-and-join.drawing.html: a hamlet's flow taken as its fall
#[must_use]
pub fn plan(spec: &Spec) -> Plan {
    let archetype = spec
        .field_archetype
        .clone()
        .unwrap_or_else(|| "valley_paddy".to_owned());
    let windward = spec.windward.clone().unwrap_or_else(|| "NW".to_owned());
    let polder = POLDERS.contains(&archetype.as_str());
    let pinned = |name: &str| -> Option<String> {
        match name {
            "settlement_form" => spec.settlement_form.clone(),
            "water_sink" => spec.water_sink.clone(),
            "intake" => spec.intake.clone(),
            "brook_side" => spec.brook_side.map(|s| s.to_string()),
            _ => spec.pins.get(name).cloned(),
        }
    };
    let forms: Vec<String> = pinned("settlement_form").map_or_else(
        || KNOBS[0].1.iter().map(|s| (*s).to_owned()).collect(),
        |p| vec![p],
    );
    let knobs: Vec<(String, u32, bool, String)> = KNOBS
        .iter()
        .map(|(name, table, branch)| {
            let branch = if *branch == "brook" {
                if polder {
                    "off"
                } else {
                    "all"
                }
            } else {
                branch
            };
            (
                (*name).to_owned(),
                u32::try_from(table.len()).unwrap_or(u32::MAX),
                pinned(name).is_some(),
                branch.to_owned(),
            )
        })
        .collect();
    let (fall, picks, _counts) = roll_plan(
        spec.seed,
        &admitted(&windward, polder),
        spec.down_deg.is_some(),
        &forms,
        &knobs,
    );
    let down_deg = spec.down_deg.or(fall).unwrap_or(0.0);
    let rolled: BTreeMap<String, String> = KNOBS
        .iter()
        .zip(&picks)
        .enumerate()
        .map(|(i, ((name, table, _), pick))| {
            let v = if i == 0 {
                forms[pick.map_or(0, |k| k as usize).min(forms.len() - 1)].clone()
            } else {
                pinned(name).unwrap_or_else(|| (*table)[pick.map_or(0, |k| k as usize)].to_owned())
            };
            ((*name).to_owned(), v)
        })
        .collect();
    let side = canvas_side(
        spec.households,
        rolled
            .get("cluster_shape")
            .map_or("crescent", String::as_str),
    );
    Plan {
        name: spec.name.clone(),
        seed: spec.seed,
        households: spec.households,
        archetype,
        windward,
        down_deg,
        water_flow: down_deg,
        fan_aspect: pick(spec.seed, "fan_aspect", &FAN_ASPECTS),
        head_lead: pick(spec.seed, "head_lead", &HEAD_LEAD),
        offtakes: offtakes_for(spec.households),
        w: side,
        h: side,
        rolled,
        pins: spec.pins.clone(),
    }
}

#[cfg(test)]
mod tests {
    use super::{band_extent, canvas_side, offtakes_for, plan, seat_room};
    use crate::driver::spec::parse;

    #[test]
    fn the_canvas_holds_the_fan_and_the_seat_s_room() {
        assert_eq!(offtakes_for(10).0.len(), 2);
        assert_eq!(offtakes_for(15).0.len(), 3);
        assert_eq!(offtakes_for(25).0.len(), 4);
        let (dep, lat) = band_extent(15, "round");
        assert!((112.0..=300.0).contains(&dep) && (240.0..=1100.0).contains(&lat));
        assert!(band_extent(15, "elongated").0 < dep);
        assert!(seat_room(15, "round") > lat);
        let side = canvas_side(15, "round");
        assert!(side > 0.0 && (side / 50.0).fract() == 0.0);
    }

    #[test]
    fn a_pinned_value_stands_and_a_rolled_one_is_from_its_table() {
        let p = plan(&parse(r#"{"name": "Sawada", "seed": 24, "households": 19, "down_deg": 225, "water_sink": "offmap", "intake": "open", "settlement_form": "nucleated"}"#).unwrap());
        assert_eq!(
            (
                p.down_deg,
                p.knob("water_sink"),
                p.knob("intake"),
                p.knob("settlement_form")
            ),
            (225.0, "offmap", "open", "nucleated")
        );
        assert!(["round", "elongated", "crescent"].contains(&p.knob("cluster_shape")));
        assert_eq!(p.knob("row_line"), "street");
        let q = plan(&parse(r#"{"name": "R", "seed": 7}"#).unwrap());
        assert!([0.0, 45.0, 90.0, 135.0, 180.0, 225.0, 270.0, 315.0].contains(&q.down_deg));
        let polder = plan(&parse(r#"{"name": "K", "seed": 21, "households": 16, "field_archetype": "mulberry_dike_fishpond", "brook_side": -1}"#).unwrap());
        assert_eq!(polder.knob("brook_side"), "-1");
        assert_eq!(polder.knob("intake"), "weir");
        assert_eq!(p.knob("no_such_knob"), "");
    }
}
