//! The hamlet driver (feature 444 T42, FR-024 part 5): a pool hamlet rolled from its spec through the plan and the Rust stages
//! through the cut, its map written as SVG and its record as JSON, with no Python. Enabled stage by stage, each once it draws:
//! the water frame and the field first. What each stage is handed and what the deleted Python drew is
//! `specs/444-work-budget-program/t42-brief.md`.
//!
//! Research:
//!     the driver - NONE: the stages' plumbing; each placement is claimed at the Rust that makes it

pub mod check;
pub mod plan;
mod polder;
mod record;
pub mod seeds;
pub mod spec;
pub mod svg;
pub mod toe;

pub use record::manifest;

use std::collections::{BTreeMap, HashMap};

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

/// The head race's angle off the brook (degrees).
///
/// Research:
///     the offtake's angle - GUESS: research/questions/0054-which-way-water-flows-and-how-channels-bend-and-join.drawing.html records the head race leaving the brook at 35 degrees as a guess; the deleted `consts_water.py`'s figure
const OFFTAKE_DEG: f64 = 35.0;
/// The brook's course: the tap's straight run, the most it moves across in one station, its skirt past the fan, its wander past
/// the skirt and the spacing of its stations (ft).
///
/// Research:
///     the brook's course - GUESS: research/questions/0054-which-way-water-flows-and-how-channels-bend-and-join.drawing.html silent on a brook's run, slew, skirt and wander (it covers a channel's bends, offtakes and junctions); these are the deleted `consts_water.py`'s, each its own GUESS there
const BROOK_TAP_RUN: f64 = 70.0;
/// Research:
///     the brook's course - GUESS: as `BROOK_TAP_RUN`'s, the slew a station
const BROOK_SLEW: f64 = 22.0;
/// Research:
///     the brook's course - GUESS: as `BROOK_TAP_RUN`'s, the skirt past the fan
const BROOK_SKIRT: f64 = 34.0;
/// Research:
///     the brook's course - GUESS: as `BROOK_TAP_RUN`'s, the wander past the skirt
const BROOK_WANDER: f64 = 10.0;
/// Research:
///     the brook's course - GUESS: as `BROOK_TAP_RUN`'s, the spacing of the stations the slew is measured across
const BROOK_STATION: f64 = 20.0;
/// The brook's drawn width (ft).
///
/// Research:
///     the brook's width - research/questions/0068-how-wide-canals-and-ditches-are-the-ladder-of-channel-widths.drawing.html: a village creek at roughly three and a half times the 1.5 ft floor, 5.25 ft
pub const BROOK_W: f64 = 5.25;
/// The weir's skew off square across the brook (degrees).
///
/// Research:
///     the weir's skew - research/questions/0059-where-the-ditch-leaves-the-brook-the-intake-and-its-weir-toshuko-and-seki.drawing.html: a weir drawn across the whole brook, diagonally upstream
const WEIR_SKEW_DEG: f64 = 30.0;
/// How far the weir is keyed into each bank (ft).
///
/// Research:
///     the weir keyed into the banks - GUESS: the page silent on how far a weir runs into each bank; a foot either side
const WEIR_KEY_FT: f64 = 1.0;
/// A basin's cell length along its canal (ft), the row's spacing times it the cell.
///
/// Research:
///     a basin's cell - research/questions/0005-rice-paddies-and-their-plots-suiden.drawing.html: about 48 ft across its canal and 26 to 36 ft along it, the cell the row's spacing times the middle, 31 ft
const CELL_SHARE: f64 = 31.0;
/// The drain's run, drawn at the collector's outfall width (ft).
///
/// Research:
///     the drain's run drawn - research/questions/0068-how-wide-canals-and-ditches-are-the-ladder-of-channel-widths.drawing.html: the drawn drain widens from a 1.2 ft head to a 5.5 ft outfall, the drain's own run onward drawn at that outfall width, 5.5 ft (the deleted `DRAIN_FT`), in research/questions/0060-field-drains-akusuiro.drawing.html's drainage-ditch class - a rice polder's outfall run too; on a dike-pond block the run past the outfall sluice is drawn at the ring canal's width instead (`driver::polder::sluice_channels`, 449 T431)
const RUN_W: f64 = 5.5;
/// The reeds' width out from the pond's shore (ft).
///
/// Research:
///     the pond's reeds - GUESS: the deleted `SINK_FRINGE`, 44 ft of reeds out from the shore
const REED_FT: f64 = 44.0;
/// The brook drawn below a confluence (ft).
///
/// Research:
///     the brook below a confluence - GUESS: the deleted `BROOK_JOIN_TRUNK`, 150 ft so the junction reads
const JOIN_TRUNK: f64 = 150.0;
/// The ink of a ground kept for a stage past the cut.
///
/// Research:
///     the placeholder's ink - CONVENTION: a dark brown that reads on the land and the paddy alike
const RESERVED_INK: &str = "#5A3E22";
/// The fords' spacing along the brook, their half-length and the bend past which a reach is no crossing place (ft, degrees).
///
/// Research:
///     the fords - GUESS: the deleted `FORD_SPACING` 160 ft, `FORD_HALF` 30 ft and `FORD_BEND_DEG` 20, a crossing place every so far along a straight reach
const FORD: (f64, f64, f64) = (160.0, 30.0, 20.0);
/// The berth the way out keeps from the tameike (ft).
///
/// Research:
///     tameike berth - GUESS: searched, the record silent (feature 417 T29 pass B, 2026-10-25); 80 ft
const POND_BERTH: f64 = 80.0;
/// How far wet ground is grown for the way out round it (ft).
///
/// Research:
///     the lane's width round wet ground - GUESS: the deleted `wet_grown_by_the_lane`, 8 ft
const LANE_FT: f64 = 8.0;
/// The settlement's standoff behind the seat's margin (ft).
///
/// Research:
///     the settlement's standoff - GUESS: research/questions/0006-dry-fields-and-their-crops-hatake.drawing.html gives the order (the paddy, the houses, the dry fields) but no distance; 12 ft
///     on a polder - GUESS research/questions/0019-polders-fields-diked-against-the-fluctuating-water-weitian-waju.drawing.html: the village "a few steps off the dike", the page's own guess, with no distance; the same 12 ft off the seat's ring; the ring's side held straight at the outer face's widest, the houses stand further off the dike where the face pinches in (by up to the waves' spread, measured on Kuwabata and a grid polder 2026-11-22, feature 449 T240, its figures in the plan's T240 section)
const STANDOFF_FT: f64 = 12.0;
/// How far the settlement's ground reaches toward its belt (ft): the seat's belt band's far edge, one figure (449 T277).
///
/// Research:
///     the belt's ground kept - research/questions/0072-shelter-belts-on-a-villages-windward-side-bofurin.drawing.html: a clustered village shelters behind one belt at its windward edge, so the belt's ground is the settlement's too
const BELT_FAR_FT: f64 = crate::seat::margins::BELT_BAND.1;
/// A dry plot's outline: its ink and width (ft).
///
/// Research:
///     the plot's outline - CONVENTION: a tan-brown line 1.4 ft wide round each dry plot, the deleted engine's (research/questions/0006-dry-fields-and-their-crops-hatake.drawing.html)
const DRY_EDGE: (&str, f64) = ("#A98C58", 1.4);
/// Each crop's fill and furrow.
///
/// Research:
///     the crops' paint - CONVENTION: the deleted engine's `CROP_FILL` and `CROP_FURROW`, each crop at its ripe or summer color - barley tan-gold, millet ochre, buckwheat pale with reddish stems, soy green (research/questions/0006-dry-fields-and-their-crops-hatake.drawing.html)
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
///     the field's knobs - research/questions/0009-the-paddy-through-the-rice-year-flooding-draining-transplanting-and-after-the-harvest.drawing.html: each rolled per settlement from its table and weights (`knobs.json`), a spec's pin standing - but for the winter crop's weights, which the site sets (the claim after next)
///     a town's nearness - GUESS: near or far at even odds; no hamlet's spec records the distance to its market town (the deleted `TOWN_NEARNESS`)
///     the winter crop's odds off the table - research/questions/0009-the-paddy-through-the-rice-year-flooding-draining-transplanting-and-after-the-harvest.drawing.html: a settlement's drainage and the nearness of a town set the odds, so the table names the winter crop's forms alone and the field stage rolls it once its fields are built (`field::build::winter_crop`), from the drained share of the paddy and the town nearness rolled here
///     the fan's middle - GUESS research/questions/0006-dry-fields-and-their-crops-hatake.drawing.html: left wild on three maps in four, a GUESS there (0.75 and 0.25)
///     the weir's forms - GUESS research/questions/0059-where-the-ditch-leaves-the-brook-the-intake-and-its-weir-toshuko-and-seki.drawing.html: a weir built in one of four ways, chosen at random with even odds, the even odds a GUESS there
///     the intake's place and siting - GUESS research/questions/0059-where-the-ditch-leaves-the-brook-the-intake-and-its-weir-toshuko-and-seki.drawing.html: the intake at the left, the center or the right of the fan's head at odds of 1:2:1, a GUESS there - the shoulder or the center at even odds here, the shoulder's side the brook's (`brook_side`, itself even); on a bend or a straight reach, the two equally likely
///     the planned grid on no hamlet - research/questions/0005-rice-paddies-and-their-plots-suiden.drawing.html: a hamlet's basins organic, "never as the tidy grid"; the grid a planned field's
const FIELD_KNOBS: [(&str, &[&str], &[f64]); 8] = [
    ("town_nearness", &["near", "far"], &[]),
    ("winter_crop", &["barley", "none"], &[]),
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
    /// The stages that refused, each with why - empty on every roll `roll` hands back: a roll that kept one is refused whole
    /// (`whole`, 449 T426), so the record's `refusals` is always `[]`.
    pub refusals: Vec<String>,
    pub counts: HashMap<String, u64>,
    /// Each stage run and its counted operations, the work budget's unit (`ops`).
    pub by_stage: Vec<(&'static str, HashMap<String, u64>)>,
    pub svg: String,
    /// The ink census of the drawing: each kind of the registry drawn, with how many marks (`Svg::census`, 449 T230).
    pub ink: BTreeMap<String, usize>,
}

/// The field's inputs from the plan: its knobs as they roll, the weir, the rows and the cell.
///
/// Research:
///     the weir's thickness by form - research/questions/0059-where-the-ditch-leaves-the-brook-the-intake-and-its-weir-toshuko-and-seki.drawing.html: four forms, 1.5 to 5 ft thick
///     the weir across the brook - research/questions/0059-where-the-ditch-leaves-the-brook-the-intake-and-its-weir-toshuko-and-seki.drawing.html: a weir drawn across the whole brook, so its half-length spans the brook on its skew, with its key into each bank
///     a basin's cell - research/questions/0005-rice-paddies-and-their-plots-suiden.drawing.html: the cell the row's spacing times the share along the canal (`CELL_SHARE`'s)
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

/// The kind a paddy depicts by its state: the wet paddy that never drains its own, every other state a paddy.
///
/// Research:
///     the paddy's kind - CONVENTION: the registry's `wet paddy` for a basin wet the year round, `paddy` for every other state, the review's legend
fn paddy_kind(s: State) -> &'static str {
    if s == State::Wet {
        "wet paddy"
    } else {
        "paddy"
    }
}

/// A paddy's paint by its state.
///
/// Research:
///     the paddy's paint by state - CONVENTION: green, wet, flooded, gold and at rest, each state of the rice year in research/questions/0009-the-paddy-through-the-rice-year-flooding-draining-transplanting-and-after-the-harvest.drawing.html drawn in its color
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
///     the bean beads - CONVENTION: a bead 3 ft across in a single row on the bund (research/questions/0014-bunds-between-the-paddies-aze.drawing.html)
///     the pocket pond's ring - GUESS: flooded ground 2.5 ft wide round the pond inside a bund line 2.2 ft wide, the deleted ink's; no page sizes the margin
///     the grave mound's size - UNRESEARCHED: the deleted ink's 13 by 9 ft mound (research/questions/0008-ponds-rocks-and-graves-in-the-middle-of-the-fields.drawing.html places a grave, not its size)
fn draw_field(svg: &mut Svg, f: &Field, brook: &[(f64, f64)], beans: &[Vec<(f64, f64)>]) {
    svg.kind("paddy");
    svg.polygon(&f.fan.ring, ink::RICE_GREEN, None);
    for (b, s) in f.basins.iter().zip(&f.states) {
        svg.kind(paddy_kind(*s));
        svg.polygon(&b.ring, fill(*s), Some((ink::AZE, BUND_W)));
    }
    for c in &f.channels {
        svg.kind(if c.role == "drain" {
            "drainage ditch"
        } else {
            "irrigation ditch"
        });
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
    svg.kind("stream");
    svg.unframed(brook, ink::POND_WATER, BROOK_W);
    svg.group(0.55);
    svg.unframed(brook, ink::SHEEN, (0.35 * BROOK_W).max(2.0));
    svg.close();
    svg.group(0.85);
    svg.kind("bund beans");
    for run in beans {
        for p in run {
            svg.ellipse(*p, 1.5, 1.5, ink::BEAN, None);
        }
    }
    svg.close();
    if let Some((ring, _deg, _form)) = &f.weir {
        svg.kind("weir");
        svg.polygon(ring, ink::WEIR_FILL, Some((ink::WEIR_EDGE, 0.6)));
    }
    if let Some((_, q)) = &f.pond {
        svg.kind("field pond");
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
        svg.kind("field grave");
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
    /// The way the settlement's back must face where the site, not the wind, decides it (a polder's landward shore); none on a comb.
    back: Option<(f64, f64)>,
    /// The fields' two lower corners, where the wet toe stops across the slope (a comb's fan, 449 T432); none on a polder.
    foot: Option<[(f64, f64); 2]>,
}

/// A comb field's ground for the seat: its fan, its ditches and the drain's run, its brook, the tameike and its reeds.
fn comb_ground<'a>(f: &'a Field, sunk: Option<&'a Sunk>) -> Ground<'a> {
    Ground {
        ring: &f.fan.ring,
        foot: Some([f.fan.at(f.fan.length, -1.0), f.fan.at(f.fan.length, 1.0)]),
        lines: f
            .channels
            .iter()
            .map(|c| c.pts.as_slice())
            .chain(sunk.map(|s| s.run.as_slice()))
            .collect(),
        brook: &f.brook.pts,
        reeds: sunk.map(|s| s.reeds.clone()).into_iter().collect(),
        pond: sunk.and_then(|s| s.pond),
        back: None,
    }
}

/// The seat (stage 4): where the settlement will sit on the first field's margin, its back to the wind, the brook's fords - handed
/// what the deleted seat stage handed it: the wet toe below the field and the reeds, each grown by the lane's width, the field and
/// the tameike at its berth as the way out's walls, the ditches and the drain's run as its lines. It draws nothing.
///
/// Research:
///     the seat's back to the wind - research/questions/0072-shelter-belts-on-a-villages-windward-side-bofurin.drawing.html: the settlement laid out with its back to the wind - on a comb, but where a declared fall runs into the wind (the seat backs the hill, the claim at `seat::seat`; its belt still windward, at `margins::ranked`); a polder hands its landward shore as the way the back faces (`Ground::back`, the claim at `polder::landward`), its belt's room still asked of the map's own wind (`SeatIn::belt_wind`, the claim at `polder::roll_polder`)
///     the way out's walls - research/questions/0081-village-lanes.drawing.html: a track keeps off wet ground and runs off the map - the wet toe and the reed fringe grown by the lane's width, the field, the pond at its berth; the drain's run and every watercourse lines it may not cross
fn stage_seat(p: &Plan, g: &Ground) -> Result<Seated, Refused> {
    let rad = p.down_deg.to_radians();
    let mut counts = HashMap::new();
    let toe = toe::toe_band(&[g.ring], g.foot, p.down_deg, (p.w, p.h), &mut counts);
    let reeds: Vec<Vec<(f64, f64)>> = g.reeds.iter().filter(|r| r.len() >= 3).cloned().collect();
    let mut walls: Vec<(Vec<(f64, f64)>, f64)> = std::iter::once(&toe)
        .chain(&reeds)
        .filter(|w| w.len() >= 3)
        .map(|w| (toe::grow(w, LANE_FT, &mut counts), 0.0))
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
        wind: g.back.unwrap_or_else(|| wind(&p.windward)),
        belt_wind: g.back.map(|_| wind(&p.windward)),
        back_min_dot: plan::WIND_BACK_MIN_DOT,
        outline: g.ring.to_vec(),
        band: plan::band_extent(p.households, p.knob("cluster_shape")),
        plots: Vec::new(),
        toe,
        toe_rim: g.foot.is_some(),
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
    seat(&inp).map_err(seat_refused).map(|mut s| {
        crate::counts::merge(&mut s.counts, &counts);
        s
    })
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
/// along it - the ground the dry hem keeps off (the deleted `settlement_ground`) - widened to the belt's own ground, the band swept
/// up to `BELT_FAR_FT` along `wind` (the map's own) on the margin's dry side (`margins::belt_swept`), so a belt that wraps the band's
/// windward end on an oblique wind is kept too. Where the seat stood the band the belt's depth off a windward field
/// (`margins::ranked`), the same depth holds the belt first, then the houses, and nothing past their back.
///
/// Research:
///     the settlement's ground - research/questions/0006-dry-fields-and-their-crops-hatake.drawing.html: the houses between the canal and the dry fields, so the hem keeps off the band where they stand
///     the belt's ground kept - research/questions/0072-shelter-belts-on-a-villages-windward-side-bofurin.drawing.html: a clustered village shelters behind one belt along its windward edge, so its ground reaches past the band to the belt on the band's windward faces - behind it where its back faces the wind, round its windward end where the wind falls obliquely (Inashiro's and Mizuguchi's belts 52 and 54 percent outside the old strip, measured 2026-11-22, 449 T294), between it and the field where a declared fall into the wind backs it to the hill (GUESS, research/questions/0031-clustered-and-scattered-villages-shuson-sanson.drawing.html), on the margin's dry side alone (GUESS, `margins::belt_swept`)
///     the back strip a belt's depth whatever the wind - GUESS: the record is silent on the ground behind a village whose back is off the wind; the strip behind the band reaches `BELT_FAR_FT` on every seat, a polder's whose back is its landward shore too (Kuwabata's, back to the east under a northwest wind), so the dry hem stands a belt's depth behind the houses where no belt stands (the algorithmically easier route: one strip for every seat)
fn settlement_ground(s: &crate::seat::Frame, wind: (f64, f64)) -> Vec<(f64, f64)> {
    let ((ax, ay), (ox, oy), (lx, ly)) = (s.anchor, s.out, s.along);
    let (lat, deep) = (s.band.0, STANDOFF_FT + 2.0 * s.band.1 + BELT_FAR_FT);
    let mut pts = vec![
        (ax - lx * lat, ay - ly * lat),
        (ax + lx * lat, ay + ly * lat),
        (ax + lx * lat + ox * deep, ay + ly * lat + oy * deep),
        (ax - lx * lat + ox * deep, ay - ly * lat + oy * deep),
    ];
    pts.extend(crate::seat::margins::belt_swept(
        s.center,
        s.along,
        s.out,
        (s.band.1, s.band.0),
        wind,
        BELT_FAR_FT,
        s.anchor,
    ));
    crate::field::geom::hull(&pts)
}

/// The dry hem (stage 5): laid behind the settlement and along the canal elsewhere, keeping off the settlement's ground.
///
/// Research:
///     the dry hem behind the settlement - research/questions/0006-dry-fields-and-their-crops-hatake.drawing.html: paddy, then the houses, then the dry fields behind them
fn stage_hem(f: &Field, seated: &Seated, wind: (f64, f64)) -> Option<crate::hem::Laid> {
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
        .map(|s| settlement_ground(s, wind))
        .into_iter()
        .collect();
    Some(crate::hem::lay(h, &f.fan.ring, &water, &keep))
}

/// The dry hem laid, and laid again as a barley hamlet's where a rolled bare winter's dry fields came out short of the grain
/// (`barley_instead`): the first hem is then not drawn, and both hems' work is counted. A pinned bare winter that came out short
/// refuses the roll.
///
/// Research:
///     the winter crop asked of the hem as laid - research/questions/0011-where-a-farming-hamlet-grew-its-coarse-grain.drawing.html: a bare winter paddy is drawn only where the fan's dry ground can grow the hamlet's whole grain need - the room is known only once the hem is laid behind the seat, so the hem is laid, asked, and where it is short laid once more for a barley hamlet (449 T418); never a third time, the barley hem drawn as it stands
///     a pinned bare winter refused - research/questions/0011-where-a-farming-hamlet-grew-its-coarse-grain.drawing.html: the same rule - a spec that pins its winter bare where the hem as laid is short of the need is refused, the whole roll and not the hem alone, so no map draws a bare winter beside dry fields short of the grain; the refusal names the pin, the acres drawn and needed, and the two ways out
fn stage_hem_fed(
    inp: &FieldIn,
    out: &mut crate::field::build::FieldOut,
    seated: &Seated,
    wind: (f64, f64),
) -> Option<Result<crate::hem::Laid, Refused>> {
    use crate::field::build::{barley_instead, Winter};
    let first = stage_hem(out.fields.first()?, seated, wind)?;
    Some(match barley_instead(inp, out, first.grain.0) {
        Winter::Stands => Ok(first),
        Winter::Unfed => Err(Refused(format!(
            "the winter crop refused: winter_crop is pinned none, a bare winter paddy, and the dry fields this ground holds grow {:.2} of the {:.2} acres of grain the hamlet needs - pin barley, or leave winter_crop unpinned and it is rolled",
            first.grain.0, out.grain.1
        ))),
        Winter::Barley => {
            let mut again = stage_hem(&out.fields[0], seated, wind)?;
            crate::counts::merge(&mut again.counts, &first.counts);
            Ok(again)
        }
    })
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

/// The sink drawn: the run in the drain's hue at its outfall width, the pond with its rim and sheen (its reeds are drawn under
/// the field, `roll`).
///
/// Research:
///     the drain's run drawn - research/questions/0060-field-drains-akusuiro.drawing.html: the drainage-ditch class whichever way it runs, at the collector's own outfall width
fn draw_sink(svg: &mut Svg, s: &Sunk) {
    svg.kind("drainage ditch");
    svg.line(&s.run, ink::DRAIN, RUN_W);
    if let Some((c, rx, ry)) = s.pond {
        svg.kind("pond");
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

/// The dry hem drawn: each plot furrowed in its crop's ink, then the settlement's ground the seat keeps, marked.
///
/// Research:
///     the hem drawn - CONVENTION: each dry plot in its crop's fill and furrows (`crop_ink`), the placeholder over them
fn draw_hem(
    svg: &mut Svg,
    laid: Option<&crate::hem::Laid>,
    seated: Option<&Seated>,
    wind: (f64, f64),
) {
    for d in laid.iter().flat_map(|l| &l.plots) {
        let (fill, furrow) = crop_ink(d.crop);
        svg.kind(d.crop);
        svg.furrowed(&d.poly, fill, DRY_EDGE, furrow, d.theta);
    }
    // THE SETTLEMENT'S GROUND MARKED (feature 444 amendment 11; the GM's look at the partial map): the seat keeps the ground the
    // hem lays round, and with the homesteads past the cut nothing fills it, so it is dashed and named (CONVENTION: a placeholder
    // for the stage that draws the houses, gone when it runs)
    if let Some(frame) = seated.and_then(|s| s.frames.first()) {
        svg.kind("-");
        svg.reserved(
            &settlement_ground(frame, wind),
            RESERVED_INK,
            "the settlement",
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

/// A stage's result kept, or its refusal recorded and nothing kept, so every stage that refuses is named together; the roll is then
/// refused whole (`whole`).
fn kept<T>(r: Result<T, Refused>, refusals: &mut Vec<String>) -> Option<T> {
    match r {
        Ok(x) => Some(x),
        Err(e) => {
            refusals.push(e.0);
            None
        }
    }
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
    crate::counts::tally(counts, "index_query@settle_runs", work[0]);
    crate::counts::tally(counts, "moved@settle_runs", work[1]);
    out
}

/// A stage's counted operations: every counter but the placements, drops and moves it reports and does not do (the deleted
/// `work_budget.py`'s total).
///
/// Research:
///     the operations counted - NONE: the work budget's own unit (feature 443)
#[must_use]
pub fn ops<S: std::hash::BuildHasher>(counts: &HashMap<String, u64, S>) -> u64 {
    counts
        .iter()
        .filter(|(k, _)| !matches!(k.split('@').next(), Some("placed" | "dropped" | "moved")))
        .map(|(_, n)| n)
        .sum()
}

/// A cohort seed's spec, as the deleted cohort audit rolled it: `Audit-<seed>`, its households 10 to 20 by the seed, nothing pinned
/// but the field's archetype where one is asked (a rolled field is always a valley paddy, so a polder is asked by name).
///
/// Research:
///     the cohort's households - NONE: a test bed's spread, 10 + (seed x 7) mod 11, the deleted `cohort_audit`'s
#[must_use]
pub fn cohort_spec(seed: i64, archetype: Option<&str>) -> spec::Spec {
    spec::Spec {
        name: format!("Audit-{seed:02}"),
        seed,
        households: 10 + u32::try_from((seed * 7).rem_euclid(11)).unwrap_or(0),
        field_archetype: archetype.map(str::to_owned),
        ..spec::Spec::default()
    }
}

/// A roll whose every stage stood, or its refusal: a hamlet a stage refused is not a map.
///
/// # Errors
/// When a stage's refusal was kept (`kept`): each named, joined.
///
/// Research:
///     no map of a refused hamlet - research/questions/0011-where-a-farming-hamlet-grew-its-coarse-grain.drawing.html: a bare winter paddy is drawn only where the dry ground holds the hamlet's grain need - a roll whose seat was refused laid no dry hem, and was still written as a map with a bare winter, a 17-acre grain need and no dry field (seed 508 of 20 households falling at 135 degrees, found 2026-11-24, 449 T418); so a kept refusal refuses the whole roll, nothing is written, and `make seeds` and `make cohort` count the seed failed
fn whole(r: Rolled) -> Result<Rolled, Refused> {
    if r.refusals.is_empty() {
        return Ok(r);
    }
    Err(Refused(format!(
        "{} - no map is drawn of a hamlet a stage refused",
        r.refusals.join("; ")
    )))
}

/// The hamlet rolled from its spec through the stages enabled so far.
///
/// # Errors
/// When the spec asks for a form the driver does not yet draw, or a stage refuses - a comb's seat and a polder's seat or sluices
/// with the rest (`whole`).
///
/// Research:
///     the stages in order - research/questions/0054-which-way-water-flows-and-how-channels-bend-and-join.drawing.html: the fall and the water decided before anything is placed, the field laid from them
pub fn roll(spec: &spec::Spec) -> Result<Rolled, Refused> {
    let p = plan::plan(spec);
    if plan::POLDERS.contains(&p.archetype.as_str()) {
        return whole(polder::roll_polder(p));
    }
    let fin = field_in(&p);
    let mut out = build(&fin).map_err(field_refused)?;
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
    crate::counts::tally(&mut out.counts, "write@brook_drawn", work);
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
    let laid = seated
        .as_ref()
        .and_then(|s| stage_hem_fed(&fin, &mut out, s, wind(&p.windward)))
        .transpose()?;
    let mut svg = Svg::default();
    // THE REEDS UNDER THE FIELD (feature 444 T42; the cohort's reeds_on_paddy check, 183 of 300 seeds): the reed ring runs its
    // 44 ft out from the shore into the paddy above the pond's berth, and the deleted `pond_reeds` cut it there against the drawn
    // ground; here the field is painted over it, the same cut on the sheet (CONVENTION: the ring is kept whole in the record, the
    // seat's walls read it grown, and the field is a wall too)
    svg.kind("marsh");
    sunk.iter().for_each(|s| svg.reeds(&s.reeds));
    for (i, (f, b)) in out.fields.iter().zip(&brooks).enumerate() {
        let beans = settled(f, b, sunk.as_ref().filter(|_| i == 0), &mut out.counts);
        draw_field(&mut svg, f, b, &beans);
    }
    sunk.iter().for_each(|s| draw_sink(&mut svg, s));
    draw_hem(&mut svg, laid.as_ref(), seated.as_ref(), wind(&p.windward));
    let by_stage: Vec<(&'static str, HashMap<String, u64>)> = [
        ("water_frame", p.counts.clone()),
        ("field", out.counts.clone()),
    ]
    .into_iter()
    .chain(sunk.iter().map(|s| ("sink", s.counts.clone())))
    .chain(seated.iter().map(|s| ("seat", s.counts.clone())))
    .chain(laid.iter().map(|l| ("hem", l.counts.clone())))
    .collect();
    let mut all = out.counts.clone();
    crate::counts::merge(
        &mut all,
        sunk.iter()
            .flat_map(|s| &s.counts)
            .chain(seated.iter().flat_map(|s| &s.counts))
            .chain(laid.iter().flat_map(|l| &l.counts))
            .chain(&p.counts),
    );
    out.counts = all;
    let doc = svg.finish(p.w, p.h, CROP_MARGIN);
    let stages: Vec<&'static str> = ["water_frame", "field"]
        .into_iter()
        .chain(sunk.as_ref().map(|_| "sink"))
        .chain(seated.as_ref().map(|_| "seat"))
        .chain(laid.as_ref().map(|_| "hem"))
        .collect();
    whole(Rolled {
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
        by_stage,
        svg: doc,
        ink: svg.census().clone(),
    })
}

#[cfg(test)]
mod tests;
