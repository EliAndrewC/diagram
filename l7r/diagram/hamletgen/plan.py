"""The spec a caller writes, and the site plan derived from it.

Split from hamletgen.py by feature 111; bodies verbatim. See hamletgen/CLAUDE.md.

Research: spec and plan plumbing - NONE: fields, unit vectors, positional draws and canvas sizing
"""

from __future__ import annotations

import math
from collections.abc import Iterator, Mapping, Sequence
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass, field
from typing import Any

from l7r.diagram.settlement import knob_rng
from l7r.diagram.settlement._knobs import KNOBS

from .consts import (
    BAMBOO_FORMS,
    BROOK_FLANKS,
    CARDINAL_BEARINGS,
    CLUSTER_BAND_ASPECT,
    CLUSTER_SHAPES,
    COPSE_SITINGS,
    DEFAULT_HARVEST_WEATHER,
    DEFAULT_WINDWARD,
    DIKE_CROPS,
    FALL_BEARINGS,
    FAN_ASPECTS,
    FARM_WATERS,
    FIELD_ARCHETYPES,
    FRY_FORMS,
    GRAIN_DRIFTS,
    GROSS_ACRES_PER_HOUSEHOLD,
    GROVE_FLANKS,
    GROVE_SIDES,
    GROVE_SIDES_FLOOD,
    HARVEST_WEATHERS,
    HEAD_RACE_LEAD,
    HOMESTEAD_GROUND_FT,
    HOUSEHOLD_BAND,
    INTAKE_FORMS,
    KOSATSUBA_SITINGS,
    LANE_SKELETONS,
    LANE_WEBS,
    LEFTOVER_FORMS,
    MANURE_FORMS,
    OFFTAKE_DEG,
    OFFTAKE_LADDER,
    PLOT_SIZES,
    POLDER_ARCHETYPES,
    POND_LAYOUTS,
    REF_HOUSEHOLDS,
    ROLLED_ARCHETYPES,
    ROW_LINES,
    ROW_SIDES,
    ROW_WATERS,
    SETTLEMENT_FORMS,
    SINKS,
    SQ_FT_PER_ACRE,
    WIND_BACK_MIN_DOT,
    WIND_VECTORS,
    Poly,
    Pt,
)

# ---- the spec and the derived plan --------------------------------------------------------------

#: Set while the perf bookend measures a size past the hamlet band (feature 304, plan D2).
_BEYOND_THE_BAND: ContextVar[bool] = ContextVar("_BEYOND_THE_BAND", default=False)


@contextmanager
def beyond_the_band() -> Iterator[None]:
    """Admit a spec of any household count while this is entered - THE MEASURING TOOL ALONE (feature 304, FR-003).

    The perf bookend times the reference spec at 40 households so a slowdown that only shows at a village's size cannot land
    unseen (`tools/perf_snapshot.SCALING_SIZES`); a GM-written hamlet stays held to `HOUSEHOLD_BAND`, and a test holds every
    pool generator off this (`tests/tools/test_perf_scaling.py`)."""
    token = _BEYOND_THE_BAND.set(True)
    try:
        yield
    finally:
        _BEYOND_THE_BAND.reset(token)


@dataclass(frozen=True)
class HamletSpec:
    """WHAT THE GM DECLARES. Everything optional is rolled from `seed`; everything given is honored.

    The split is deliberate and is the whole ergonomic claim of the experiment: the REQUIRED fields
    are the facts only a person knows (what the place is called, how big it is, and - when the
    surrounding geography is settled - which way its water runs), and everything that follows from
    those is the script's job. A spec of `HamletSpec("Ikegami", seed=4, households=15)` is a
    complete, gate-passing hamlet.

    Research:
        default households - UNRESEARCHED: 15 when none declared (REF_HOUSEHOLDS), Ikegami's count
        declared fields honored, the rest rolled - NONE: the spec's plumbing; each knob table carries its own claim in consts"""

    name: str
    seed: int
    households: int = REF_HOUSEHOLDS
    # The landscape facts. `down_deg` is the LAND's fall and `water_flow` the drainage BEARING; the
    # skill's rule is that these are two different facts and must not be derived from each other, so
    # they are two fields. A hamlet's single comb drains down its own fall, so when only one is
    # given the other follows it - that is a statement about a one-field hamlet, not a general rule.
    down_deg: float | None = None
    water_flow: float | None = None
    windward: str | None = None
    harvest_weather: str | None = None  # settled | changeable - declared, never rolled (feature 282; `HARVEST_WEATHERS`)
    # The rolled knobs, pinnable.
    water_sink: str | None = None
    intake: str | None = None  # the intake's form at the brook: weir | open (feature 230; `INTAKE_FORMS`)
    brook_side: int | None = None  # which flank the brook passes on: +1 / -1 (feature 230; `BROOK_FLANKS`), pinnable so the pool can exhibit a sink the roll happens not to reach
    cluster_shape: str | None = None
    lane_skeleton: str | None = None
    lane_web: str | None = None
    bamboo: str | None = None
    fixtures_min: dict[str, int] | None = None  # at least N of a farmstead fixture kind, e.g. {"shrine": 1} (feature 133 T61)
    settlement_form: str | None = None
    grove_sides: int | None = None  # how many sides each farmstead's grove takes, 2 | 3 | 4 (feature 291; `GROVE_SIDES`)
    flood_ground: bool | None = None  # the farms stand on flood-prone ground (feature 291); None reads it off the site
    row_line: str | None = None  # a linear row's line, street | edge (feature 291; `ROW_LINES`); None rolls it (flood ground: edge)
    row_sides: str | None = None  # one | both sides of the row's street (feature 291; `ROW_SIDES`)
    row_water: str | None = None  # own | shared wells along a row (feature 291; `ROW_WATERS`)
    farm_water: str | None = None  # a dispersed farm's own water, channel | well (feature 291 amendment 5; `FARM_WATERS`)
    field_archetype: str | None = None
    pond_layout: str | None = None  # a dike-pond's arrangement, grid | mosaic (feature 150; `POND_LAYOUTS`)
    manure_form: str | None = None  # the manure fixture's form, heap | pit (feature 150; `MANURE_FORMS`)
    copse_siting: str | None = None  # among_the_houses, the one form left (feature 328; `COPSE_SITINGS`)
    kosatsuba_siting: str | None = None  # frontage, the one form left (feature 328; `KOSATSUBA_SITINGS`)
    byre_form: str | None = None  # courtyard | yard_shed | detached_commons - the settlement engine's knob, pinnable so the pool can exhibit each (feature 261; 269 B16)
    dike_crop: str | None = None  # a dike-pond's dike planting, mulberry | fruit | tea (feature 150, 269 B34; `DIKE_CROPS`)
    leftover: str | None = None  # a dike-pond block's unconverted parcels, rice | pond (feature 150, 269 E9; `LEFTOVER_FORMS`)
    plot_size: str | None = None
    grain_drift: int | None = None
    woodland_patches: int | None = None
    # Passed through to the engine's own knob catalog (`Settlement.pin_knob`).
    pins: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Refuse a spec outside what the generator draws.

        Research:
            hamlet household band - research/questions/0001-the-five-sizes-of-settlement-hamlet-village-town-provincial-city-and-capital.drawing.html: 10 to 20 households
            pond layout values - DEVIATION research/questions/0019-polders-fields-diked-against-the-fluctuating-water-weitian-waju.drawing.html: the mosaic only
            water sink values - research/questions/0060-field-drains-akusuiro.drawing.html: a pond at the foot or off the map
            knob values - NONE: each table carries its own claim in consts
        """
        if self.field_archetype is not None and self.field_archetype not in FIELD_ARCHETYPES:
            raise ValueError(f"field_archetype {self.field_archetype!r} is not one this generator draws: {sorted(FIELD_ARCHETYPES)}")
        if self.dike_crop is not None and self.dike_crop not in DIKE_CROPS:
            raise ValueError(f"dike_crop {self.dike_crop!r} must be one of {sorted(set(DIKE_CROPS))}")
        if self.leftover is not None and self.leftover not in LEFTOVER_FORMS:
            raise ValueError(f"leftover {self.leftover!r} must be one of {sorted(set(LEFTOVER_FORMS))}")
        if self.manure_form is not None and self.manure_form not in MANURE_FORMS:
            raise ValueError(f"manure_form {self.manure_form!r} must be one of {sorted(set(MANURE_FORMS))}")
        if self.copse_siting is not None and self.copse_siting not in COPSE_SITINGS:
            raise ValueError(f"copse_siting {self.copse_siting!r} must be one of {sorted(set(COPSE_SITINGS))}")
        if self.kosatsuba_siting is not None and self.kosatsuba_siting not in KOSATSUBA_SITINGS:
            raise ValueError(f"kosatsuba_siting {self.kosatsuba_siting!r} must be one of {sorted(set(KOSATSUBA_SITINGS))}")
        if self.pond_layout is not None and self.pond_layout not in POND_LAYOUTS:
            raise ValueError(
                f"pond_layout {self.pond_layout!r} must be one of {sorted(set(POND_LAYOUTS))} (research/questions/0019-polders-fields-diked-against-the-fluctuating-water-weitian-waju.drawing.html)"
            )
        lo, hi = HOUSEHOLD_BAND
        if not lo <= self.households <= hi and not _BEYOND_THE_BAND.get():
            raise ValueError(
                f"{self.households} households is outside the hamlet band {lo}-{hi} - a smaller place is an outlying farmstead, a larger one is a village (which needs a headman, a shrine and tax-free plots this generator does not draw)"
            )
        if self.harvest_weather is not None and self.harvest_weather not in HARVEST_WEATHERS:
            raise ValueError(f"harvest_weather {self.harvest_weather!r} must be one of {list(HARVEST_WEATHERS)}")
        if self.windward is not None and self.windward not in WIND_VECTORS:
            raise ValueError(f"windward {self.windward!r} is not a compass quarter: {sorted(WIND_VECTORS)}")
        if self.brook_side is not None and self.brook_side not in BROOK_FLANKS:
            raise ValueError(f"brook_side {self.brook_side!r} must be one of {sorted(BROOK_FLANKS)} - the two flanks the brook may pass the fan on")
        if self.byre_form is not None and self.byre_form not in KNOBS["byre_form"].value_space:
            raise ValueError(f"byre_form {self.byre_form!r} must be one of {KNOBS['byre_form'].value_space}")
        for _name, _val, _space in (
            ("row_line", self.row_line, ROW_LINES),
            ("row_sides", self.row_sides, ROW_SIDES),
            ("row_water", self.row_water, ROW_WATERS),
            ("farm_water", self.farm_water, FARM_WATERS),
        ):
            if _val is not None and _val not in _space:
                raise ValueError(f"{_name} {_val!r} must be one of {sorted(set(_space))}")
        if self.water_sink is not None and self.water_sink not in ("pond", "offmap"):
            raise ValueError(f"water_sink {self.water_sink!r} must be 'pond' (a tameike below the fields) or 'offmap' (the drain brook leaves the frame)")


@dataclass
class SitePlan:
    """THE DERIVED PLAN - everything decided before a single shape is drawn.

    Separating this from `build` is what makes the generator testable without rendering: `plan_site`
    is pure, so the sizing arithmetic, the knob rolls and the canvas derivation can be asserted
    directly, and a stage that misbehaves can be handed a hand-made plan."""

    spec: HamletSpec
    down_deg: float
    water_flow: float
    windward: str
    water_sink: str
    cluster_shape: str
    lane_skeleton: str
    lane_web: str
    bamboo: str
    # WHICH KIND OF SETTLEMENT THIS IS - nucleated, dispersed or linear. Read by seating (which
    # passes offer seats), by the lane derivation (whether an internal network exists at all), by
    # the grove choice (one village belt or a kainyo per farmstead), and by the two access checks.
    # `settlement_form_asked` preserves the ROLL when a site cannot take that form; see `stage_track`.
    settlement_form: str
    # HOW MANY SIDES EACH FARM'S GROVE TAKES (feature 291): rolled for every hamlet and recorded, drawn only where the
    # farms carry their own grove (not nucleated). `flood_ground` chooses the table; `grove_flank` completes a
    # cardinal wind's windward pair (`GROVE_FLANKS`).
    grove_sides: int
    flood_ground: bool
    grove_flank: int
    field_archetype: str
    # THE DIKE-POND'S ARRANGEMENT (feature 150): "grid" or "mosaic", rolled for a dike-pond hamlet
    # and pinned to "grid" for a rice polder (see `POND_LAYOUTS`). Read by `stage_polder`.
    pond_layout: str
    manure_form: str  # heap | pit (feature 150, `MANURE_FORMS`), read by `farmstead_fixtures`
    harvest_weather: str  # settled | changeable (feature 282): the spec's declaration or the regional default, never a roll
    copse_siting: str  # among_the_houses (feature 328, `COPSE_SITINGS`)
    kosatsuba_siting: str  # frontage (feature 328, `KOSATSUBA_SITINGS`)
    dike_crop: str  # the dike-pond's planting (feature 150 A6), read by `stage_polder`
    leftover: str  # the dike-pond's unconverted parcels (feature 150 B2), read by `stage_polder`
    plot_size: str
    grain_drift: int
    woodland_patches: int
    fan_aspect: float
    intake: str  # weir | open (feature 230, `INTAKE_FORMS`) - what stands where the head race leaves the brook
    brook_side: int  # +1 / -1: which flank of the fan the brook passes on, the head race leaving toward the other
    head_lead: float  # px from the intake to the division point, rolled within `HEAD_RACE_LEAD`
    target_acres: float
    W: int
    H: int
    ftpx: float = 1.0
    # THE FIELD'S OWN SQUARE (feature 287, homes H31): the side `canvas_for` sizes from the acreage, inside the canvas
    # the seat's room grows round it. The field is laid from the canvas middle at this span (`head_sluice`), so the
    # room added for the seat and its belt moves nothing of the field's own geometry. 0 reads as min(W, H).
    field_span: float = 0.0
    offtakes_a: tuple[float, ...] = ()
    offtakes_b: tuple[float, ...] = ()
    # filled in by the stages as the map is built, so a later stage can read an earlier one's result
    net: dict[str, Any] = field(default_factory=dict)

    envelope: Poly = field(default_factory=list)
    sink_pond: tuple[float, float, float, float] | None = None
    sink_brook: Poly = field(default_factory=list)
    brook: Poly = field(default_factory=list)  # the feed brook's whole course, past the fan to the frame (feature 230)
    watercourses: list[tuple[Pt, Pt]] = field(default_factory=list)
    belt: Poly = field(default_factory=list)
    # The coppice patches, scanned in `stage_hinterland` BEFORE the scrub is scattered so the scrub
    # keeps out of them, and drawn by `stage_woodland` (T35, GM 2026-08-27).
    woodland_polys: list[Poly] = field(default_factory=list)
    # The bamboo stands (T47), scanned in `stage_hinterland` before the scrub, drawn by `stage_bamboo`.
    bamboo_polys: list[Poly] = field(default_factory=list)
    bamboo_roles: list[str] = field(default_factory=list)
    bamboo_of: dict[int, Pt] = field(default_factory=dict)  # a homestead strip's owner house, by its index in `bamboo_polys` (feature 287, homes H01)
    # points a way must reach (feature 287, homes H36); the web serves each. Its one producer, the hamlet's own burial
    # ground, was eliminated by feature 280 M68 (modern-only), so none is registered until a form that owes a path returns
    way_targets: list[Pt] = field(default_factory=list)
    fixtures_min: dict[str, int] = field(
        default_factory=dict
    )  # the spec's floor per fixture kind (T61); the placer forces presence up to it  # "thicket" (communal, one) or "homestead" (per farmstead), parallel to bamboo_polys
    seat: dict[str, Any] = field(default_factory=dict)
    title_pocket: tuple[float, float, float, float] | None = None  # reserved ONCE, at the first ask (feature 150 T50 fallout - see hinterland.title_pocket)
    title_pocket_outside: bool = False  # the reservation lies OUTSIDE the content and the crop must take it in (hamletgen.stage_frame)
    placed: int = 0
    acres: float = 0.0
    # WHERE THE DRAIN MEETS THE BROOK, when it does (feature 230). Set by `stage_sink`; read by `stage_frame`,
    # which reserves it as content so the crop cannot leave the junction off the sheet. A confluence is the one
    # thing on a watercourse that is a FEATURE rather than a runner - two waters meeting is a place - and the
    # crop deliberately ignores runners, which is how one came to be drawn 7.4 ft outside the picture.
    confluence: Pt | None = None
    # THE ROW VILLAGE'S THREE CHOICES (feature 291 amendment 3; `ROW_LINES`, `ROW_SIDES`, `ROW_WATERS`): rolled for every
    # hamlet and recorded, drawn only where the form is linear.
    row_line: str = "edge"
    row_sides: str = "one"
    row_water: str = "own"
    farm_water: str = "well"  # ...and a DISPERSED farm's own water (amendment 5; `FARM_WATERS`), drawn only where the form is dispersed
    # THE VIEW, DECIDED ONCE (feature 287, M6): (x, y, w, h), fixed at the end of `stage_hinterland`'s seating by
    # `hinterland.frame.frame_for`, and set exactly by `stage_frame`. Every rule that reads the picture reads this.
    view: tuple[float, float, float, float] | None = None
    # THE FARMS' OWN GROVE BANDS, as the ways read them (feature 291): set by `stage_track` for the connector's dry exit, which
    # keeps a band at a footpath's gap rather than a track's - a dispersed hamlet's farms stand a lane's room apart
    grove_bands: list[Poly] = field(default_factory=list)
    fry_form: str = "none"  # none | fry_village (feature 280 M60, `FRY_FORMS`): a dike-pond hamlet's nursery, read by `stage_polder`

    @property
    def fall(self) -> Pt:
        """Unit vector pointing DOWNHILL, in screen coordinates."""
        return (math.cos(math.radians(self.down_deg)), math.sin(math.radians(self.down_deg)))

    @property
    def head_deg(self) -> float:
        """The bearing the head race leaves the intake on (feature 230).

        An offtake leaves its parent pointing downstream at an acute angle, so the race turns off the
        brook's own downstream heading - which is the land's fall, the brook running downhill - by the
        offtake angle, and it turns AWAY from the flank the brook takes, so that the two never run
        alongside one another.

        Research:
            head race leaves leaning downstream - research/questions/0054-which-way-water-flows-and-how-channels-bend-and-join.drawing.html: OFFTAKE_DEG off the fall
            turned away from the brook's flank - UNRESEARCHED"""
        return self.down_deg - self.brook_side * OFFTAKE_DEG

    @property
    def wind(self) -> Pt:
        """Unit vector pointing at the quarter the cold wind blows FROM (so: the sheltered BACK)."""
        return WIND_VECTORS[self.windward]


def _roll(seed: int, knob: str, choices: Sequence[Any]) -> Any:
    """One deterministic, INDEPENDENT draw. Uses the engine's `knob_rng`, so a draw depends only on
    (map seed, knob name) - never on how much randomness has been drawn before it. That is the
    skill's positional-randomness rule at the knob level: adding a knob here cannot re-roll the
    others, so a cohort's earlier maps do not silently change when a later knob is added."""
    return choices[knob_rng(seed, knob).randrange(len(choices))]


def offtakes_for(households: int) -> tuple[tuple[float, ...], tuple[float, ...]]:
    """The delivery-ditch fractions for a hamlet of this size - see `OFFTAKE_LADDER`.

    Research:
        delivery ditches by size - research/questions/0053-irrigation-canals-and-how-they-are-laid-out-yosuiro.drawing.html: the second canal feeds at least one
        delivery-ditch count and fractions - UNRESEARCHED: 2, 3 or 4 by household band (OFFTAKE_LADDER)"""
    for ceiling, a, b in OFFTAKE_LADDER:
        if households < ceiling:
            return a, b
    return OFFTAKE_LADDER[-1][1], OFFTAKE_LADDER[-1][2]


LINEAR_CANVAS = 1.0
"""A linear or dispersed hamlet's canvas over `canvas_for`'s: room for grove farms (feature 291 plan D14) - a map drawing
convention, sized so a twenty-farm row finds its streets on the sheet, and twenty dispersed farms their frames.

Research: linear and dispersed canvas - CONVENTION: 1.0 times the clustered canvas"""


def canvas_for(target_acres: float, ftpx: float) -> tuple[int, int]:
    """A working canvas comfortably larger than the fan it must hold.

    The canvas is NOT the map: `crop_to_content` frames the finished drawing to its hard features,
    so this only has to be big enough that `build_comb` never clamps the fan against a canvas edge
    (which truncates threads and leaves a fan with a flat, obviously-artificial side) and big enough
    to leave margin ground for the cluster, its grove and the hinterland.

    A comb fan fills roughly 40% of its own bounding box (it is a fan, not a rectangle), and the
    settlement plus its margins needs about as much ground again as the field, so the span is sized
    from the field's bbox and doubled. Erring LARGE is cheap - unused canvas is cropped away - while
    erring small is a silently mis-shaped field, so the multiplier errs high.

    IT WAS TRIED AT 1.75x and reverted. A review nitpick (fair, and still open) is that ~68% of the
    canvas is drawn and then cropped away - ink nobody sees, a 16 MB SVG, a slower render. But the
    canvas also has to hold what sits BELOW the field: `stage_sink` walks the tameike downslope from
    the drain outfall until it clears the crop, and then clamps it to the canvas. At 1.75x the clamp
    started winning, which puts the pond back on the paddy and its ditch running uphill - four
    checks failing on a third of a cohort, all from one number. Trimming the canvas needs the CROP
    to be trimmed instead, not the ground the map still uses."""
    field_px2 = target_acres * SQ_FT_PER_ACRE / (ftpx * ftpx)
    span = math.sqrt(field_px2 / 0.40)
    side = int(round(span * 2.0 / 50.0) * 50)
    return side, side


def band_extent(households: int, shape: str | None, ground: float | None = None) -> tuple[float, float]:
    """The seat band's half-depth and half-length (the ellipse's semi-axes), `(dep, lat)`, from the household count and the cluster shape - the ONE
    derivation `seat_cluster` seats with and `seat_room` sizes the canvas with (feature 287, homes H31). Area is held
    (`households * HOMESTEAD_GROUND_FT^2`, the ground a homestead takes), so the shape sets only the band's aspect.

    Research:
        band area - UNRESEARCHED: households times HOMESTEAD_GROUND_FT squared; 0037 sizes only the yard
        band aspect by shape - UNRESEARCHED: CLUSTER_BAND_ASPECT
        band floors and caps - UNRESEARCHED: half-depth 112 to 300 ft, half-length 240 to 1,100 ft"""
    asp = CLUSTER_BAND_ASPECT.get(shape or "crescent", 3.0)
    g = HOMESTEAD_GROUND_FT if ground is None else ground
    dep = max(112.0, min(math.sqrt(households * (g**2) / (asp * math.pi)), 300.0))
    lat = max(240.0, min(households * (g**2) / (math.pi * dep), 1100.0))
    return dep, lat


SEAT_STANDOFF = 12.0
"""px from the field margin to the seat band's near edge (`cluster._seat_frame`'s standoff).

Research: standoff from the field - UNRESEARCHED: 12 ft"""
BELT_REACH = 146.0
"""px upwind of the cluster's windward fringe to the belt's far row (`belt_off_canvas` samples 36, 90 and 146).

Research:
    belt's far row - research/questions/0071-groves-around-a-southern-chinese-village-the-fengshui-woods-fengshuilin-and-the-dooryard-copse.drawing.html: the band's 100 ft depth inside the drawn 80 to 120 ft, a convention, and a 10 ft ragged edge, behind a near face that stands back from the nearest houses (the page; its 36 ft a GUESS - the 50 ft sun rule on yards and beds is applied to the clumps)"""


FAN_OVERHANG = 0.22
"""How far a fitted fan may stand past its own square (`canvas_for`), as a share of the square's side - MEASURED, not
derived: the head sluice is rolled up to 0.24 of the square off the fall axis (`HEAD_OFFSETS`) and the fan grows toward
its untrimmed flank, so a fan is not centered in its square. Over the pool and cohort 1-60 on the grown canvas
(2026-09-29) the largest overhang was 0.20 (cohort seed 45, whose fan the old canvas clamped 26% short of its acreage);
0.22 holds that with a plot row's margin. The canvas carries it on every side, so the seat's room is counted from the
fan as drawn, not from the square."""


def seat_room(households: int, shape: str | None) -> float:
    """The ground the seat and its windbreak need beyond the field, px (feature 287, homes H31 and plan D8): the band's
    depth and standoff to its center, then the farther of its half-length `lat` (the band on the canvas, `seat_cluster`'s
    HARD 3) and its windward fringe plus the belt's reach (the belt on the canvas, `belt_off_canvas`). A seat whose back
    is within 45 degrees of the wind has its fringe at most `0.7071 * lat + dep` upwind of its center.

    A CLOSED-FORM BOUND FROM THE SEAT'S OWN QUANTITIES, not a tuned margin: the canvas grows by this on every side, so
    whichever margin faces the wind has the room. The frame crops to content, so the room costs no ink."""
    dep, lat = band_extent(households, shape)
    return dep + SEAT_STANDOFF + max(lat, WIND_BACK_MIN_DOT * lat + dep + BELT_REACH)  # `lat` is the band's half-length


def _fall_into_wind(down_deg: float, windward: str) -> float:
    """The cosine between the land's fall and the quarter the wind comes from: 1 for a fall straight into the wind."""
    wx, wy = WIND_VECTORS[windward]
    return math.cos(math.radians(down_deg)) * wx + math.sin(math.radians(down_deg)) * wy


def fall_backs_the_wind(down_deg: float, windward: str) -> bool:
    """Does the fall leave the seat a wind-facing margin above the drain on EVERY field it can draw (feature 287, homes
    H30 and plan D3)? True when the fall runs square to the wind or away from it: the wind then meets a flank or the
    head. A fall 45 degrees off the wind, or into it, may still offer a seat - a flank's back turned to the wind
    (`cluster.margin_candidates`) - but its wind-facing margins are only
    the toe's corner - a fan widens downhill, so its flanks' normals lean UPHILL, away from the wind - and whether the
    corner stands clear of the toe depends on the field the fit draws: 16 of 17 such cohort maps had one, cohort seed
    24 had none (measured 2026-09-29, on the canvas `seat_room` grows). A rolled fall is rolled over the falls this
    admits, so the seat's back to the wind holds by construction; it is also 背山面水 read whole - the back to the
    hill AND to the wind, the high side and the windward side being one side (`seat_cluster`).

    Research:
        high side and windward side as one - research/questions/0031-clustered-and-scattered-villages-shuson-sanson.drawing.html: the high windward margin
        fall square to or away from the wind - UNRESEARCHED: 0072 sets the belt to the wind, not the fall"""
    return _fall_into_wind(down_deg, windward) <= 1e-9


def plan_site(spec: HamletSpec) -> SitePlan:
    """Turn a spec into a fully-resolved plan. PURE - no drawing, no engine, no RNG stream.

    Research:
        polder on the survey grid - research/questions/0019-polders-fields-diked-against-the-fluctuating-water-weitian-waju.drawing.html: a surveyed grid
        polder grid's orientation - DEVIATION research/questions/0031-clustered-and-scattered-villages-shuson-sanson.drawing.html: falls from the four cardinals only, the dike-pond mosaic too, never tilted
        dike-pond knobs only on a dike-pond - research/questions/0019-polders-fields-diked-against-the-fluctuating-water-weitian-waju.drawing.html: a rice polder's layout fixed to the grid
        regional wind - research/questions/0072-shelter-belts-on-a-villages-windward-side-bofurin.drawing.html: DEFAULT_WINDWARD unless declared
        rolled fall backs the wind - research/questions/0031-clustered-and-scattered-villages-shuson-sanson.drawing.html: only falls leaving a windward margin
        water flow follows the fall - research/questions/0054-which-way-water-flows-and-how-channels-bend-and-join.drawing.html: unless declared
        flood-prone ground - research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.drawing.html: a polder's farms
        paddy by households - research/questions/0017-how-much-farmland-a-settlement-works-and-in-what-tracts.drawing.html: GROSS_ACRES_PER_HOUSEHOLD each
        row on the edge on flood ground - research/questions/0033-row-villages-resson.drawing.html
        woodland patches - research/questions/0077-village-fuel-woods-and-their-coppice-satoyama.drawing.html: 2 to 4, rolled
        knob rolls - research/questions/0031-clustered-and-scattered-villages-shuson-sanson.drawing.html: cluster_shape, lane_skeleton, plot_size and grain_drift rolled per hamlet; each table's own claim in consts
        harvest weather default - research/questions/0016-rice-drying-racks-hasa-hasagi.drawing.html: settled unless declared
        canvas - NONE: the field's square, the fan's overhang and the seat's room, cropped later
        grove sides refused outside two to four - research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.drawing.html: two, three or four sides"""
    # A POLDER IS LAID TO THE CARDINAL SURVEY GRID, so its fall is rolled from the four cardinals
    # rather than the eight compass points. This is not a workaround for `polder_fills_its_bbox`
    # (which a diagonal block fails, correctly - a rotated rectangle cannot fill an axis-aligned
    # bbox): it is what the archetype IS. A wei-tian polder is a SURVEYED orthogonal module diked
    # out of standing water, and the survey runs with the cardinal directions; the organic comb fan,
    # which follows its own water down whatever slope it finds, is the one that sits on a diagonal.
    # A GM who pins `down_deg` is still honored - the pin is a fact about that place.
    _archetype = spec.field_archetype or str(_roll(spec.seed, "field_archetype", ROLLED_ARCHETYPES))
    _falls = CARDINAL_BEARINGS if _archetype in POLDER_ARCHETYPES else FALL_BEARINGS
    # A dike-pond rolls its arrangement; a rice polder IS the surveyed grid (`POND_LAYOUTS`), and
    # pinning it there rather than rolling keeps every polder_grid map exactly as it was.
    _pond_layout = (spec.pond_layout or str(_roll(spec.seed, "pond_layout", POND_LAYOUTS))) if _archetype == "mulberry_dike_fishpond" else "grid"
    # THE REGIONAL NORTHWEST unless the spec declares a local wind (feature 261; `DEFAULT_WINDWARD` for why).
    windward = spec.windward or DEFAULT_WINDWARD
    # THE FALL LEAVES THE SEAT A BACK TO THE WIND (feature 287, homes H30, plan D3): a ROLLED fall is rolled over the
    # falls that leave a wind-facing margin above the drain on any field (`fall_backs_the_wind`) - the knob narrowed where
    # it cannot be honored. A DECLARED fall is the GM's fact about the place and is taken as written: its site is refused
    # only where `seat_cluster` finds no margin whose back it can turn to the wind (`SeatRefused`), never for its bearing.
    down_deg = spec.down_deg if spec.down_deg is not None else float(_roll(spec.seed, "down_deg", tuple(f for f in _falls if fall_backs_the_wind(f, windward))))
    # A hamlet is ONE comb draining down ONE valley, so its drainage bearing IS its fall unless the
    # GM declares otherwise. Recording both separately keeps the map honest about which fact is
    # which (skill SKILL.md: "these are not the same fact and must not be derived from each other")
    # and leaves the door open for a spec that sets a channel running across the fall.
    water_flow = spec.water_flow if spec.water_flow is not None else down_deg
    _form = spec.settlement_form or str(_roll(spec.seed, "settlement_form", SETTLEMENT_FORMS))
    # FLOOD-PRONE GROUND (feature 291): the farms stand on reclaimed low ground behind dikes, or on a dike - the ground
    # the Izumo ring guarded against floods. This project's decision (research/contents.json#homesteads, the grove's shape); a
    # spec pins it either way.
    _flood = spec.flood_ground if spec.flood_ground is not None else (_archetype in POLDER_ARCHETYPES or _form == "dike_top")
    if spec.grove_sides is not None and spec.grove_sides not in (2, 3, 4):
        raise ValueError(f"grove_sides={spec.grove_sides!r}: a farmstead grove takes 2, 3 or 4 sides")
    target_acres = spec.households * GROSS_ACRES_PER_HOUSEHOLD
    a, b = offtakes_for(spec.households)
    _cluster_shape = spec.cluster_shape or str(_roll(spec.seed, "cluster_shape", CLUSTER_SHAPES))
    # THE CANVAS HOLDS THE FIELD AND, ON EVERY SIDE, THE SEAT WITH ITS BELT (feature 287, homes H31): the field's own
    # square from the acreage, grown by `seat_room` all round, so the margin facing the wind always has the room
    # `seat_cluster` asks of it - the seat is never cramped against the canvas edge.
    span, _ = canvas_for(target_acres, 1.0)
    W = H = int(round((span * (1.0 + 2.0 * FAN_OVERHANG) + 2.0 * seat_room(spec.households, _cluster_shape)) / 50.0) * 50)
    if _form in ("linear", "dispersed"):
        # A ROW VILLAGE NEEDS ITS LENGTH (feature 291 plan D14): its farms stand one grove frame (some 240 ft) apart along
        # their streets, and a canvas sized for a clustered hamlet ran each street off the sheet after a few lots (cohort
        # seed 12: 13 of 17 seated on six streets). The unused ground is cropped away with the rest (`crop_to_content`).
        # ...AND SO DOES A DISPERSED HAMLET OF GROVE FARMS, each farm the same frame: a twenty-farm one ran off the sheet's
        # edge at sixteen (the pinned Audit-905, the same with a well or a channel)
        W, H = int(W * LINEAR_CANVAS), int(H * LINEAR_CANVAS)
    return SitePlan(
        spec=spec,
        down_deg=down_deg,
        water_flow=water_flow,
        windward=windward,
        water_sink=spec.water_sink or str(_roll(spec.seed, "water_sink", SINKS)),
        cluster_shape=_cluster_shape,
        lane_skeleton=spec.lane_skeleton or str(_roll(spec.seed, "lane_skeleton", LANE_SKELETONS)),
        lane_web=spec.lane_web or str(_roll(spec.seed, "lane_web", LANE_WEBS)),
        bamboo=spec.bamboo or str(_roll(spec.seed, "bamboo", BAMBOO_FORMS)),
        fixtures_min={k: int(v) for k, v in (spec.fixtures_min or {}).items()},
        settlement_form=_form,
        grove_sides=spec.grove_sides or int(_roll(spec.seed, "grove_sides", GROVE_SIDES_FLOOD if _flood else GROVE_SIDES)),
        flood_ground=_flood,
        grove_flank=int(_roll(spec.seed, "grove_flank", GROVE_FLANKS)),
        row_line=spec.row_line or ("edge" if _flood else str(_roll(spec.seed, "row_line", ROW_LINES))),
        row_sides=spec.row_sides or str(_roll(spec.seed, "row_sides", ROW_SIDES)),
        row_water=spec.row_water or str(_roll(spec.seed, "row_water", ROW_WATERS)),
        farm_water=spec.farm_water or str(_roll(spec.seed, "farm_water", FARM_WATERS)),
        field_archetype=_archetype,
        pond_layout=_pond_layout,
        manure_form=spec.manure_form or str(_roll(spec.seed, "manure_form", MANURE_FORMS)),
        harvest_weather=spec.harvest_weather or DEFAULT_HARVEST_WEATHER,  # declared, never rolled (`HARVEST_WEATHERS`)
        copse_siting=spec.copse_siting or str(_roll(spec.seed, "copse_siting", COPSE_SITINGS)),
        kosatsuba_siting=spec.kosatsuba_siting or str(_roll(spec.seed, "kosatsuba_siting", KOSATSUBA_SITINGS)),
        dike_crop=(spec.dike_crop or str(_roll(spec.seed, "dike_crop", DIKE_CROPS))) if _archetype == "mulberry_dike_fishpond" else "mulberry",
        leftover=(spec.leftover or str(_roll(spec.seed, "leftover", LEFTOVER_FORMS))) if _archetype == "mulberry_dike_fishpond" else "rice",
        fry_form=str(_roll(spec.seed, "fry_form", FRY_FORMS)) if _archetype == "mulberry_dike_fishpond" else "none",
        plot_size=spec.plot_size or str(_roll(spec.seed, "plot_size", PLOT_SIZES)),
        grain_drift=spec.grain_drift if spec.grain_drift is not None else int(_roll(spec.seed, "grain_drift", GRAIN_DRIFTS)),
        woodland_patches=spec.woodland_patches if spec.woodland_patches is not None else int(_roll(spec.seed, "woodland_patches", (2, 3, 3, 4))),
        fan_aspect=float(_roll(spec.seed, "fan_aspect", FAN_ASPECTS)),
        intake=spec.intake or str(_roll(spec.seed, "intake", INTAKE_FORMS)),
        brook_side=spec.brook_side if spec.brook_side is not None else int(_roll(spec.seed, "brook_side", BROOK_FLANKS)),
        head_lead=float(_roll(spec.seed, "head_lead", HEAD_RACE_LEAD)),
        target_acres=target_acres,
        W=W,
        H=H,
        field_span=float(span),
        offtakes_a=a,
        offtakes_b=b,
    )
