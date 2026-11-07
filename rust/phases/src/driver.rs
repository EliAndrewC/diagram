//! The hamlet driver (feature 444 T42, FR-024 part 5): a pool hamlet rolled from its spec through the plan and the Rust stages
//! through the cut, its map written as SVG and its record as JSON, with no Python. Enabled stage by stage, each once it draws:
//! the water frame and the field first. What each stage is handed and what the deleted Python drew is
//! `specs/444-work-budget-program/t42-brief.md`.
//!
//! Research:
//!     the driver - NONE: the stages' plumbing; each placement is claimed at the Rust that makes it

pub mod plan;
mod polder;
mod record;
pub mod spec;
pub mod svg;
pub mod toe;

pub use record::manifest;

use std::collections::HashMap;

use crate::field::brook::BrookIn;
use crate::field::build::{build, Field, FieldIn, KnobIn};
use crate::field::dry::DryPlot;
use crate::field::staged::PolderStage;
use crate::field::states::State;
use crate::seat::{seat, SeatIn, Seated};
use crate::sink::{sink, SinkIn, Sunk};
use crate::waterward::Fringe;
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
/// The sink's figures: the drain's run at the collector's outfall width, the reeds' width out from the pond's shore and the
/// brook's length below a confluence (ft).
///
/// Research:
///     the drain's run drawn - research/questions/0060-field-drains-akusuiro.drawing.html: the drainage-ditch class, at the collector's own outfall width, 5.5 ft (the deleted `DRAIN_FT`)
///     the pond's reeds - GUESS: the deleted `SINK_FRINGE`, 44 ft of reeds out from the shore
///     the brook below a confluence - GUESS: the deleted `BROOK_JOIN_TRUNK`, 150 ft so the junction reads
const RUN_W: f64 = 5.5;
const REED_FT: f64 = 44.0;
const JOIN_TRUNK: f64 = 150.0;
/// The reeds' tint, a pale wet green beneath their ticks.
///
/// Research:
///     the reeds' tint - CONVENTION: the engine's reed cover read as a pale wet green with sparse ticks; the tile itself went with the deleted engine
const REED_TINT: &str = "#C3D0A4";
/// The fords' spacing along the brook, their half-length and the bend past which a reach is no crossing place; the tameike's berth
/// the way out keeps (ft, degrees).
///
/// Research:
///     the fords - GUESS: the deleted `FORD_SPACING` 160 ft, `FORD_HALF` 30 ft and `FORD_BEND_DEG` 20, a crossing place every so far along a straight reach
///     tameike berth - GUESS: searched, the record silent (feature 417 T29 pass B, 2026-10-25); 80 ft
///     the lane's width round wet ground - GUESS: the deleted `wet_grown_by_the_lane`, 8 ft
const FORD: (f64, f64, f64) = (160.0, 30.0, 20.0);
const POND_BERTH: f64 = 80.0;
const LANE_FT: f64 = 8.0;
/// The settlement's ground behind the seat's margin: its standoff and the belt's far edge (ft).
///
/// Research:
///     the settlement's ground - research/questions/0006-dry-fields-and-their-crops-hatake.drawing.html: the houses between the canal and the dry fields where the settlement stands, the dry fields behind it
///     the belt's ground kept - research/questions/0072-shelter-belts-on-a-villages-windward-side-bofurin.drawing.html: a clustered village shelters behind one belt at its windward edge, so the belt's ground is the settlement's too
const STANDOFF_FT: f64 = 12.0;
const BELT_FAR_FT: f64 = 146.0;
/// A dry plot's edge, and each crop's fill and furrow.
///
/// Research:
///     the crops' paint - CONVENTION: the deleted engine's `CROP_FILL` and `CROP_FURROW`, each crop at its ripe or summer color (0006)
const DRY_EDGE: (&str, f64) = ("#A98C58", 1.4);
fn crop_ink(crop: &str) -> (&'static str, &'static str) {
    match crop {
        "millet" => ("#C29A55", "#8E6E36"),
        "buckwheat" => ("#D9CFC0", "#A8574A"),
        "soy" => ("#8DAA6A", "#5E7A44"),
        _ => ("#C9B57A", "#9C8650"),
    }
}
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
    pub polder: Option<PolderStage>,
    pub waterward: Option<Fringe>,
    pub sunk: Option<Sunk>,
    pub seated: Option<Seated>,
    pub dry: Vec<DryPlot>,
    /// The coarse grain the hem drew and the room it left (acres).
    pub grain: Option<(f64, f64)>,
    /// The coarse grain the field's barley drew, the need it handed the hem and the room it left (acres).
    pub field_grain: Option<(f64, f64, f64)>,
    /// The stages that refused, each with why: the stages before it drawn, none after it.
    pub refusals: Vec<String>,
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
fn draw_field(svg: &mut Svg, f: &Field, brook: &[(f64, f64)], beans: &[Vec<(f64, f64)>]) {
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
    for run in beans {
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

/// The wind's quarter as a unit vector pointing where it comes from.
///
/// Research:
///     regional wind - research/questions/0072-shelter-belts-on-a-villages-windward-side-bofurin.drawing.html: the eight quarters, the northwest unless declared
fn wind(quarter: &str) -> (f64, f64) {
    let d = std::f64::consts::FRAC_1_SQRT_2;
    match quarter {
        "N" => (0.0, -1.0),
        "NE" => (d, -d),
        "E" => (1.0, 0.0),
        "SE" => (d, d),
        "S" => (0.0, 1.0),
        "SW" => (-d, d),
        "W" => (-1.0, 0.0),
        _ => (-d, -d),
    }
}

/// What the seat seats against: the field's outline, the water lines the way out may not cross, the brook as first laid, the
/// reeds and the tameike - a comb's or a polder's.
struct Ground<'a> {
    ring: &'a [(f64, f64)],
    lines: Vec<&'a [(f64, f64)]>,
    brook: &'a [(f64, f64)],
    reeds: Vec<Vec<(f64, f64)>>,
    pond: Option<((f64, f64), f64, f64)>,
}

/// A comb field's ground for the seat: its fan, its ditches and the drain's run, its brook, the tameike and its reeds.
fn comb_ground<'a>(f: &'a Field, sunk: Option<&'a Sunk>) -> Ground<'a> {
    Ground {
        ring: &f.fan.ring,
        lines: f
            .channels
            .iter()
            .map(|c| c.pts.as_slice())
            .chain(sunk.map(|s| s.run.as_slice()))
            .collect(),
        brook: &f.brook.pts,
        reeds: sunk.map(|s| s.reeds.clone()).into_iter().collect(),
        pond: sunk.and_then(|s| s.pond),
    }
}

/// The seat (stage 4): where the settlement will sit on the first field's margin, its back to the wind, the brook's fords - handed
/// what the deleted seat stage handed it: the wet toe below the field and the reeds, each grown by the lane's width, the field and
/// the tameike at its berth as the way out's walls, the ditches and the drain's run as its lines. It draws nothing.
///
/// Research:
///     the seat's back to the wind - research/questions/0072-shelter-belts-on-a-villages-windward-side-bofurin.drawing.html: the settlement laid out with its back to the wind
///     the way out's walls - research/questions/0081-village-lanes.drawing.html: a track keeps off wet ground and runs off the map - the wet toe and the reed fringe grown by the lane's width, the field, the pond at its berth; the drain's run and every watercourse lines it may not cross
fn stage_seat(p: &Plan, g: &Ground) -> Result<Seated, Refused> {
    let rad = p.down_deg.to_radians();
    let toe = toe::toe_band(&[g.ring], p.down_deg, (p.w, p.h));
    let reeds: Vec<Vec<(f64, f64)>> = g.reeds.iter().filter(|r| r.len() >= 3).cloned().collect();
    let mut walls: Vec<(Vec<(f64, f64)>, f64)> = std::iter::once(&toe)
        .chain(&reeds)
        .filter(|w| w.len() >= 3)
        .map(|w| (toe::grow(w, LANE_FT), 0.0))
        .collect();
    walls.push((g.ring.to_vec(), 0.0));
    if let Some((c, rx, ry)) = g.pond {
        let r = rx.max(ry);
        walls.push((
            (0..16)
                .map(|k| {
                    let a = f64::from(k) * std::f64::consts::PI / 8.0;
                    (c.0 + r * a.cos(), c.1 + r * a.sin())
                })
                .collect(),
            POND_BERTH,
        ));
    }
    let lines: Vec<((f64, f64), (f64, f64))> = g
        .lines
        .iter()
        .flat_map(|pts| pts.windows(2).map(|s| (s[0], s[1])))
        .collect();
    let inp = SeatIn {
        canvas: (p.w, p.h),
        fall: (rad.cos(), rad.sin()),
        wind: wind(&p.windward),
        back_min_dot: plan::WIND_BACK_MIN_DOT,
        outline: g.ring.to_vec(),
        band: plan::band_extent(p.households, p.knob("cluster_shape")),
        plots: Vec::new(),
        toe,
        reeds,
        brook: g.brook.to_vec(),
        walls,
        lines,
        streams: if g.brook.is_empty() {
            Vec::new()
        } else {
            vec![g.brook.to_vec()]
        },
        ford: FORD,
    };
    seat(&inp).map_err(seat_refused)
}

#[expect(
    clippy::needless_pass_by_value,
    reason = "`map_err` hands the refusal over by value"
)]
fn seat_refused(e: crate::seat::SeatRefused) -> Refused {
    Refused(format!("the seat refused: {e}"))
}

/// A water segment at its width: its two ends and its drawn width (ft).
type Segment = ((f64, f64), (f64, f64), f64);

/// The ground the seat chose for the settlement and its belt: from the margin out past the band and the belt, the band's length
/// along it - the ground the dry hem keeps off (the deleted `settlement_ground`).
fn settlement_ground(s: &crate::seat::Frame) -> Vec<(f64, f64)> {
    let ((ax, ay), (ox, oy), (lx, ly)) = (s.anchor, s.out, s.along);
    let (lat, deep) = (s.band.0, STANDOFF_FT + 2.0 * s.band.1 + BELT_FAR_FT);
    vec![
        (ax - lx * lat, ay - ly * lat),
        (ax + lx * lat, ay + ly * lat),
        (ax + lx * lat + ox * deep, ay + ly * lat + oy * deep),
        (ax - lx * lat + ox * deep, ay - ly * lat + oy * deep),
    ]
}

/// The dry hem (stage 5): laid behind the settlement and along the canal elsewhere, keeping off the settlement's ground.
///
/// Research:
///     the dry hem behind the settlement - research/questions/0006-dry-fields-and-their-crops-hatake.drawing.html: paddy, then the houses, then the dry fields behind them
fn stage_hem(f: &Field, seated: &Seated) -> Option<crate::hem::Laid> {
    let h = f.hem.as_ref()?;
    let water: Vec<Segment> = f
        .water
        .segs
        .iter()
        .zip(&f.water.widths)
        .map(|(&(a, b), &w)| (a, b, w))
        .collect();
    let keep: Vec<Vec<(f64, f64)>> = seated
        .frames
        .first()
        .map(settlement_ground)
        .into_iter()
        .collect();
    Some(crate::hem::lay(h, &f.fan.ring, &water, &keep))
}

/// The sink (stage 3): the first field's collector run to its pond, to the passing brook or off the map.
///
/// Research:
///     where the runoff goes - research/questions/0060-field-drains-akusuiro.drawing.html: a pond at the foot, the passing brook, or off the map
fn stage_sink(p: &Plan, f: &Field, brook: &[(f64, f64)]) -> Result<Option<Sunk>, Refused> {
    // a field with no collector hands the sink an empty drain, which lays nothing (`sink::sink`)
    let drain = f
        .channels
        .iter()
        .find(|c| c.role == "drain")
        .map(|c| c.pts.clone())
        .unwrap_or_default();
    let rad = p.down_deg.to_radians();
    let inp = SinkIn {
        pond: p.knob("water_sink") == "pond",
        canvas: (p.w, p.h),
        fall: (rad.cos(), rad.sin()),
        flow_deg: p.water_flow,
        outline: f.fan.ring.clone(),
        drain,
        brook_w: BROOK_W,
        run_w: RUN_W,
        resting: f
            .basins
            .iter()
            .zip(&f.states)
            .filter(|(_, s)| **s == State::Rest)
            .map(|(b, _)| b.ring.clone())
            .collect(),
        reed_ft: REED_FT,
        join_trunk: JOIN_TRUNK,
    };
    sink(&inp, &mut brook.to_vec()).map_err(sink_refused)
}

#[expect(
    clippy::needless_pass_by_value,
    reason = "`map_err` hands the refusal over by value"
)]
fn sink_refused(e: crate::sink::SinkRefused) -> Refused {
    Refused(format!("the sink refused: {e}"))
}

/// The sink drawn: the reeds round the pond, the run in the drain's hue at its outfall width, the pond with its rim and sheen.
///
/// Research:
///     the drain's run drawn - research/questions/0060-field-drains-akusuiro.drawing.html: the drainage-ditch class whichever way it runs, at the collector's own outfall width
fn draw_sink(svg: &mut Svg, s: &Sunk) {
    svg.polygon(&s.reeds, REED_TINT, None);
    svg.line(&s.run, ink::DRAIN, RUN_W);
    if let Some((c, rx, ry)) = s.pond {
        svg.ellipse(c, rx, ry, ink::POND_WATER, Some((ink::RIM, 2.4)));
        svg.ellipse(
            c,
            (rx - 12.0).max(1.0),
            (ry - 10.0).max(1.0),
            "none",
            Some((ink::SHEEN, 1.0)),
        );
    }
}

#[expect(
    clippy::needless_pass_by_value,
    reason = "`map_err` hands the refusal over by value"
)]
fn field_refused(e: crate::field::rules::FieldRefused) -> Refused {
    Refused(format!("the field refused: {e}"))
}

/// A stage's result kept, or its refusal recorded and nothing kept: the stages before it drawn, none that read it.
fn kept<T>(r: Result<T, Refused>, refusals: &mut Vec<String>) -> Option<T> {
    r.map_err(|e| refusals.push(e.0)).ok()
}

/// The bean runs that survive the map's final water (`beans::settle`): the field's ditches at their widths, the brook, the drain's
/// run, the tameike and the pocket pond.
///
/// Research:
///     no bead in the water - research/questions/0014-bunds-between-the-paddies-aze.drawing.html: in a single row on the bund - none inside a pond, none on a line's water
fn settled(
    f: &Field,
    brook: &[(f64, f64)],
    sunk: Option<&Sunk>,
    counts: &mut HashMap<String, u64>,
) -> Vec<Vec<(f64, f64)>> {
    let segs: Vec<Segment> = f
        .channels
        .iter()
        .flat_map(|c| {
            c.pts
                .windows(2)
                .map(move |s| (s[0], s[1], c.w.max(c.w_tail)))
        })
        .chain(brook.windows(2).map(|s| (s[0], s[1], BROOK_W)))
        .chain(
            sunk.into_iter()
                .flat_map(|s| s.run.windows(2).map(|w| (w[0], w[1], RUN_W))),
        )
        .collect();
    let ponds: Vec<(f64, f64, f64, f64)> = sunk
        .and_then(|s| s.pond)
        .map(|(c, rx, ry)| (c.0, c.1, rx, ry))
        .into_iter()
        .chain(f.pond.as_ref().map(|(_, q)| (q.x, q.y, q.rx, q.ry)))
        .collect();
    let mut work = [0_u64; 2];
    let out = crate::field::beans::settle(&f.beans, &segs, &ponds, &mut work);
    *counts
        .entry("index_query@settle_runs".to_owned())
        .or_insert(0) += work[0];
    *counts.entry("moved@settle_runs".to_owned()).or_insert(0) += work[1];
    out
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
        return Ok(polder::roll_polder(p));
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
    let sunk = out
        .fields
        .iter()
        .zip(&brooks)
        .next()
        .map(|(f, b)| stage_sink(&p, f, b))
        .transpose()?
        .flatten();
    let mut refusals = Vec::new();
    let seated = out.fields.first().and_then(|f| {
        kept(
            stage_seat(&p, &comb_ground(f, sunk.as_ref())),
            &mut refusals,
        )
    });
    let laid = out
        .fields
        .first()
        .zip(seated.as_ref())
        .and_then(|(f, s)| stage_hem(f, s));
    let mut svg = Svg::default();
    for (i, (f, b)) in out.fields.iter().zip(&brooks).enumerate() {
        let beans = settled(f, b, sunk.as_ref().filter(|_| i == 0), &mut out.counts);
        draw_field(&mut svg, f, b, &beans);
    }
    sunk.iter().for_each(|s| draw_sink(&mut svg, s));
    for d in laid.iter().flat_map(|l| &l.plots) {
        let (fill, furrow) = crop_ink(d.crop);
        svg.furrowed(&d.poly, fill, DRY_EDGE, furrow, d.theta);
    }
    sunk.iter()
        .flat_map(|s| &s.counts)
        .chain(seated.iter().flat_map(|s| &s.counts))
        .chain(laid.iter().flat_map(|l| &l.counts))
        .for_each(|(k, n)| *out.counts.entry(k.clone()).or_insert(0) += n);
    let doc = svg.finish(p.w, p.h, CROP_MARGIN);
    let stages: Vec<&'static str> = ["water_frame", "field"]
        .into_iter()
        .chain(sunk.as_ref().map(|_| "sink"))
        .chain(seated.as_ref().map(|_| "seat"))
        .chain(laid.as_ref().map(|_| "hem"))
        .collect();
    Ok(Rolled {
        plan: p,
        polder: None,
        waterward: None,
        sunk,
        seated,
        grain: laid.as_ref().map(|l| l.grain),
        field_grain: Some(out.grain),
        dry: laid.map(|l| l.plots).unwrap_or_default(),
        refusals,
        stages,
        knobs: out.knobs,
        fields: out.fields,
        brooks,
        counts: out.counts,
        svg: doc,
    })
}

#[cfg(test)]
mod tests {
    use super::{manifest, roll, spec::parse};

    #[test]
    fn a_comb_hamlet_rolls_and_draws_its_field() {
        let r = roll(&parse(r#"{"name": "Inashiro", "seed": 4, "households": 15, "down_deg": 90, "water_sink": "pond", "settlement_form": "nucleated"}"#).unwrap()).unwrap();
        assert_eq!(
            r.stages,
            vec!["water_frame", "field", "sink", "seat", "hem"]
        );
        assert!(!r.dry.is_empty() && r.grain.is_some_and(|g| g.0 > 0.0));
        assert_eq!(
            ["barley", "millet", "buckwheat", "soy"]
                .map(|c| super::crop_ink(c).0)
                .iter()
                .collect::<std::collections::HashSet<_>>()
                .len(),
            4
        );
        assert!(r.sunk.as_ref().is_some_and(|s| s.pond.is_some()));
        assert!(!r.fields.is_empty() && !r.fields[0].basins.is_empty());
        assert!(
            r.svg.starts_with("<svg") && r.svg.matches("<path").count() > r.fields[0].basins.len()
        );
        let m = manifest(&r);
        assert!(m.contains("\"grain_acres\": {\"field\": {\"drawn\": "));
        assert!(
            m.contains("\"name\": \"Inashiro\"")
                && m.contains(
                    "\"stages\": [\"water_frame\", \"field\", \"sink\", \"seat\", \"hem\"]"
                )
                && m.contains("\"plot_size\"")
        );
    }

    #[test]
    fn a_resting_field_drains_off_the_map() {
        let r = roll(&parse(r#"{"name": "Sawada", "seed": 24, "households": 19, "down_deg": 225, "water_sink": "offmap", "intake": "open", "pins": {"paddy_rest": "unsettled"}}"#).unwrap()).unwrap();
        assert!(r.fields[0]
            .states
            .contains(&crate::field::states::State::Rest));
        assert!(r
            .sunk
            .as_ref()
            .is_some_and(|s| s.pond.is_none() && !s.run.is_empty()));
        // its fall runs into the wind: the seat finds no margin, and the record says so
        assert!(r.seated.is_none() && r.refusals[0].starts_with("the seat refused"));
        assert!(manifest(&r).contains("\"refusals\": [\"the seat refused"));
    }

    #[test]
    fn a_dike_pond_polder_rolls_through_its_seat_and_its_waterside_reeds() {
        let r = roll(&parse(r#"{"name": "Kuwabata", "seed": 21, "households": 16, "down_deg": 90, "field_archetype": "mulberry_dike_fishpond", "pond_layout": "mosaic", "dike_crop": "mulberry"}"#).unwrap()).unwrap();
        assert!(
            r.stages.contains(&"waterward")
                && r.polder.as_ref().is_some_and(|s| s.converted.is_some())
        );
        assert!(r.svg.contains(DIKE_EARTH_FOR_TEST));
        assert!(manifest(&r).contains("\"grain_acres\": {\"field\": null, \"hem\": null}"));
        let rice = roll(&parse(r#"{"name": "R", "seed": 5, "households": 12, "down_deg": 0, "field_archetype": "polder_grid", "pins": {"paddy_rest": "unsettled"}}"#).unwrap()).unwrap();
        assert!(rice.polder.as_ref().is_some_and(|s| s.converted.is_none()));
        let tea = roll(&parse(r#"{"name": "T", "seed": 21, "households": 16, "down_deg": 0, "field_archetype": "mulberry_dike_fishpond", "dike_crop": "tea"}"#).unwrap()).unwrap();
        assert!(tea
            .polder
            .as_ref()
            .is_some_and(|s| s.converted.as_ref().is_some_and(|c| !c.1.hedges.is_empty())));
        assert_eq!(
            ["willow", "fruit", "tea", "mulberry"]
                .map(super::polder::crown_fill)
                .iter()
                .collect::<std::collections::HashSet<_>>()
                .len(),
            4
        );
    }

    const DIKE_EARTH_FOR_TEST: &str = super::polder::DIKE_EARTH;

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
        assert!(super::seat_refused(crate::seat::SeatRefused("x".into()))
            .0
            .starts_with("the seat refused"));
        assert_eq!(
            ["N", "NE", "E", "SE", "S", "SW", "W", "NW", "?"]
                .map(super::wind)
                .iter()
                .filter(|w| (w.0.hypot(w.1) - 1.0).abs() < 1e-9)
                .count(),
            9
        );
        assert!(super::sink_refused(crate::sink::SinkRefused("x".into()))
            .0
            .starts_with("the sink refused"));
        let e = super::field_refused(crate::field::rules::FieldRefused {
            rule: "a_rule",
            detail: "why".into(),
        });
        assert!(e.0.starts_with("the field refused: "));
    }

    #[test]
    fn a_name_is_escaped_in_the_record() {
        assert_eq!(super::Refused("why".into()).to_string(), "why");
        assert_eq!(super::record::js("a\"b\\c\nd"), "\"a\\\"b\\\\c\\nd\"");
    }
}
