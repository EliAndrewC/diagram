"""Split from hamletgen/homesteads.py by feature 173 - see this package's CLAUDE.md for the index."""

from __future__ import annotations

import math
import random
from collections.abc import Callable, Iterator, Sequence
from typing import Any

from l7r.diagram.settlement import Settlement, seg_dist
from l7r.diagram.settlement._knobs import knob_rng
from l7r.diagram.settlement.homestead_parts.groves import HOMESTEAD_WOOD_FT2, crown_lift
from l7r.diagram.settlement.homestead_parts.stands import crown_reach
from l7r.diagram.settlement.homestead_parts.wood_share import COPSE_CLUMP_BS, install_wood_shares
from l7r.diagram.settlement.land.wet import marsh_ground
from l7r.diagram.settlement.rolling.access import ACCESS_HALF_FT, exit_bearing, start_tree
from l7r.diagram.settlement.rolling.bearing import COMMON_BEARING_DEG, MarginBearing, turned_reach, wrap_line_deg
from l7r.diagram.settlement.rolling.fit import FIELD_REACH_FT
from l7r.diagram.settlement.rolling.lot import HouseholdLots
from l7r.diagram.settlement.shrines_wells.byres import COMMONS_BYRE_FRACTION, COMMONS_BYRE_GAP, commons_byre_target, household_byre_form

from ..cluster import seat_has_dry_exit
from ..consts import BUNDLE_PITCH, CLUSTER_DRAWN_ASPECT, CLUSTER_SHAPES, COPSE_HOUSE_REACH_FT, MIN_WEB_GAP, POLDER_ARCHETYPES, SEATING_GROUND_FT, SUN_CORRIDOR_FT, WEB_FABRIC_GAP, WEST_SUN_FT, Pt
from ..plan import SitePlan, _roll, band_extent
from .boundary import install_site_boundary
from .capacity import SiteRefused, margin_ladder, seat_the_rest, seating_mark, unseat_to
from .fixtures import farmstead_fixtures, fixture_forms, fixture_quota
from .holds import hold_laid_parts
from .region import SeatRegion, seat_window
from .retirement import retirement_houses, retirement_quota
from .seats import cluster_aspect, front_row
from .wells import place_wells

#: The range a rank seat may stand off its exact rank, as a share of `BUNDLE_PITCH` - half of it each way (feature 261,
#: settlement-review of Mizuguchi): a GUESS calibrated against main's roll of that map, whose rows spread 24 and 78 ft - a
#: quarter pitch keeps a rank a rank while taking it off the surveyed line.
RANK_DEPTH_JITTER = 0.25

FORM_BOUND: dict[str, float] = {"linear": 2.5}
"""Per-FORM override of how far from the seat center a homestead may stand, as a multiple of the
seat band's diagonal; every other form uses the 1.15 default.

A ROW NEEDS ITS LENGTH (feature 291). With the linear form's row taking every household (`front_cap`), the radius sized for
a compact cluster ended the row after about seven farms carrying their own groves, and the rest were seated in ranks
behind it - a block again (cohort seed 12). The row village grows long, not wide; 2.5 is a GUESS at the length a row of
ten to twenty farms with their groves needs, not a researched extent.

A FAILED FIX, recorded so it is not tried again (feature 126). Dispersed and linear maps were given
2.2 and 1.8 here to cure Inashiro seating 13 of its 15 households. It did not cure it: the cause was
`_nucleated` being set from the FORM, which gave a linear map grove-wrapped bundles too large to
fit, and fixing that fixed the count. Measured afterwards on Sawada, the dispersed pool map:
19/19 households in 53.4s at the uniform 1.15, against 19/19 in 53.7s at 2.2 - no seats gained, no
time lost, nothing bought. A wider search bound only permits sprawl the feature exists to prevent,
so the honest value is no override at all."""


def water_push(water: Sequence[tuple[Pt, Pt, float]], center: Pt, n: Pt, half_lat: float, near: float, far: float) -> float:
    """How far a box must move along `n` so that no water course (`(a, b, clearance)` segments) lies within its clearance
    of the box: the box spans `near`-`far` along `n` and `half_lat` either side of `center` across it. Zero when clear.
    Each segment is sampled every 8 ft, which is finer than any clearance the courses carry (half-width + 5)."""
    lx, ly = -n[1], n[0]
    push = 0.0
    for a, b, clr in water:
        if seg_dist(center[0], center[1], a, b) > half_lat + (far - near) + clr:
            continue
        k = max(1, int(math.dist(a, b) / 8.0))
        for j in range(k + 1):
            x, y = a[0] + (b[0] - a[0]) * j / k, a[1] + (b[1] - a[1]) * j / k
            if abs((x - center[0]) * lx + (y - center[1]) * ly) <= half_lat + clr:
                d = x * n[0] + y * n[1]
                if near - clr <= d <= far + clr:
                    push = max(push, d + clr - near)
    return push


def face_the_houses(s: Settlement, plan: SitePlan) -> None:
    """Which way this hamlet's farmhouses face (269 B18, research/questions/0029-farmhouses-minka.html), set before the first house is seated.

    The COMMON BEARING is rolled per settlement from the map's seed within `COMMON_BEARING_DEG` of south (a degree
    along a continuum, so calibrated liberty rather than a knob) and recorded as `meta.house_bearing_deg`; each house
    turns from it with the field margin its lanes will follow (`MarginBearing`, on the paddy's envelope and the seat's
    own axis), plus its own by-eye spread, and one in ten a quarter turn (`Settlement._house_rot`)."""
    common = round((knob_rng(s.seed, "house_bearing").random() * 2.0 - 1.0) * COMMON_BEARING_DEG, 2)
    s._house_bearing = common
    ax, ay = plan.seat["along"]
    s._bearing_follow = MarginBearing(plan.envelope, math.degrees(math.atan2(ay, ax))) if len(plan.envelope) >= 3 else None
    s.M["meta"]["house_bearing_deg"] = common


def turn_the_seat(s: Settlement, seat: Pt, n: Pt, core: tuple[float, float, float, float]) -> Pt:
    """A front-row seat moved out along `n` by how much further the homestead's core reaches toward its chord once
    turned (269 B18). `front_row` offsets every seat by the unturned core (`core`: left, top, right, bottom about the house
    center); the turn is the seat's own, known before it is offered, so the extra is measured, not a slack. Asked twice -
    the seat it moves to may take a different turn - and the larger move kept; the placer's own tests stay the judge."""
    toward = (-n[0], -n[1])
    base = turned_reach(core, 0.0, toward)
    extra = 0.0
    q = seat
    for _ in range(2):
        extra = max(extra, turned_reach(core, s._house_rot(q[0], q[1]), toward) - base)
        q = (seat[0] + n[0] * extra, seat[1] + n[1] * extra)
    return q


def bank_of(x: float, y: float, brook: Sequence[Pt]) -> int:
    """Which side of the brook a point stands on: the sign of its offset from the NEAREST reach of the course.

    A CROSSING TEST IS NOT A SIDE TEST, and that mistake cost two rolls. Asking whether the line from one house
    to another crosses the brook reads a curving course wrongly - the brook comes down one flank and wraps the
    field's toe, so two houses on the same bank can have the water between them as the crow flies, and every
    candidate after the first was refused (1 house of 15 seated on three maps). The side of the nearest reach is
    local, so a bend cannot invert it."""
    j = min(range(len(brook) - 1), key=lambda i: seg_dist(x, y, brook[i], brook[i + 1]))
    (ax, ay), (bx, by) = brook[j], brook[j + 1]
    return 1 if (bx - ax) * (y - ay) - (by - ay) * (x - ax) >= 0 else -1


def stage_homesteads(s: Settlement, plan: SitePlan) -> None:
    """The farmhouses.

    Every household is seated here, and at this moment there is NOT ONE LANE ANYWHERE ON THE MAP: the houses
    answer to the field, the water and each other, and nothing else has taken ground before them. Every way on the
    finished map - the connector, the field spur, the cluster's spine and the alleys - is laid after this plate and
    positioned from where these houses actually landed.

    The ground is asked ONCE. Before the first seat, the site boundary is computed from everything the map holds:
    the paddy's outline as a few facing chords, everything else - the hem, the marshes, the ponds, the reed toe that
    will be drawn later, the no-build ground - as one outline with holes, and the water courses and registered
    corridors as segments. A candidate rectangle is judged at nine points against those and nothing else.

    The seats are proposed where a house can stand. The FRONT ROW walks the paddy's chords at the bundle pitch, each
    seat at a computed standoff - the wall rule's distance plus the reach of the homestead's core (the house, its
    yard, its kura) toward that chord - pushed once further where the boundary's outline lies beyond the chord (a
    dike's bank), and takes about the square root of (households times the rolled shape's aspect) houses, so a
    crescent fronts the field with more of its houses than a round cluster does. The RANKS BEHIND are proposed behind
    every standing house, one homestead's depth further from the field (and the yard's sun corridor where the ranks
    climb north), in a brick pattern; only when a round seats nothing behind does the cluster grow along the field,
    by the seats a pitch beyond each end of the rank. Only while the quota is still short after four rounds do the RESCUE rounds run: the old random cloud
    over a wider band, seeded a third of a pitch apart, spending guesses on purpose. A re-roll after a stranded
    farmhouse draws a different cloud.

    Each seat is one placer call, and a call tests one rectangle first: the box around the homestead's
    configurations, against the boundary and the placed boxes; where that is refused, each configuration's own box
    in turn, with at most one computed move away from a single overlapping neighbor. The parts - the garden's side,
    its beds, the kura - are laid inside a box the ground admitted, and the rules that read the parts (the wall rule,
    the eave gap, the sun corridors) are asked once. No spiral of offsets, no sliding: a seat that does not fit is
    refused and the next seat is offered. `meta.seat_search` counts every guess - candidates, placer calls,
    rectangles, part layouts, the front row's share and the rounds - so the search is measured, never assumed.

    `households_consistent` wants the occupied farmhouses within 0.85-1.05x the declared households - a to-scale map
    depicts essentially every household (research/questions/0001-the-five-sizes-of-settlement-hamlet-village-town-provincial-city-and-capital.drawing.html) -
    and the stage aims at one apiece: EVERY declared household is seated, or the site is refused (feature 287, homes
    H14 and plan D2; `seat_every_household`) - the exhaustive pass over the ground within reach, then the next margin,
    never a shortfall shipped and never a whole-map re-roll.

    Steps:
        l7r.diagram.hamletgen.homesteads.stages.seat_every_household
        l7r.diagram.hamletgen.homesteads.boundary.install_site_boundary
        l7r.diagram.hamletgen.homesteads.boundary.site_boundary
        l7r.diagram.settlement.homestead_parts.wood_share.install_wood_shares
        l7r.diagram.settlement.rolling.access.start_tree
        l7r.diagram.settlement.rolling.lot.household_parts
        l7r.diagram.hamletgen.homesteads.seats.front_row
        l7r.diagram.hamletgen.homesteads.seats._front_row_from_chains
        l7r.diagram.hamletgen.homesteads.rows.seat_rows
        l7r.diagram.settlement.Settlement.try_place
        l7r.diagram.settlement.Settlement._place_bundle_nucleated
        l7r.diagram.settlement.Settlement._bundle_envelope
        l7r.diagram.settlement.Settlement._envelope_blocked
        l7r.diagram.settlement.Settlement._parts_fit
        l7r.diagram.settlement.rolling.access.access_corridor
        l7r.diagram.settlement.homestead_parts.wood_share.WoodShares.share
        l7r.diagram.settlement.rolling.lot.record_parts
        l7r.diagram.settlement.rolling.access.reserve
        l7r.diagram.settlement.Settlement.cluster_seeds
        l7r.diagram.settlement.Settlement.farmsteads
    """
    # A YARD KEEPS ITS SUN (GM 2026-08-13; researched in research/questions/0038-sunlight-and-shade-on-the-farm.drawing.html). 39 ft is the 9-to-3 drying window at 38N in the 10th month for a minka's ~20 ft
    # ridge; the noon figure is 21. The engine's rule is opt-in and this is where the scripted tier
    # opts in - the hand-authored maps keep their packing until they are converted.
    s.sun_corridor(SUN_CORRIDOR_FT)
    # ...AND THE SAME CORRIDOR NOW COVERS THE GARDEN BEDS (feature 133 T10), inside `sun_corridor`.
    # The belt's afternoon lane is opted into HERE too, though it is only read at `stage_windbreak`:
    # the two sun rules are one decision, made at the same place, for the same reason.
    s.west_sun_lane(WEST_SUN_FT)
    _placed, _cloud_placed = seat_every_household(s, plan)

    # THE SHAPE IS RECORDED ONLY IF THE CLOUD ACTUALLY SHAPED THE CLUSTER (2026-08-17).
    # `cluster_seeds` used to stamp `meta.cluster_shape` on its first attempt, BEFORE it knew how
    # many seats it would win - which was harmless while the cloud either ran for the whole hamlet
    # or not at all. The front-row cap changed that: the rows now seat one rank and the cloud seats
    # the SURPLUS, so on Sawada and Inashiro a knob describing a minority of the houses started
    # being stamped for the first time. It is not idle bookkeeping - `check_village/driver.py`'s
    # `TWIN_AXES` reads "the declared knob if present, else the cluster-bbox aspect", so Sawada
    # began reporting its shape as "round" to the twin detector while drawing a 3.48:1 band.
    #
    # A DECLARATION MUST DESCRIBE THE DRAWING. The cloud shaped the cluster only if it seated most
    # of it; below that the frontage rows did, and the rolled shape went unhonored exactly as it
    # does when the cloud never runs at all. `meta.cluster_seeding` still records which happened, so
    # nothing goes silent - that is the invariant `settlement_records_cluster_seeding` holds.
    # THE SHAPE IS ALWAYS HONORED NOW, so it is always declared (2026-08-19). This used to stamp the
    # knob only when the CLOUD seated most of the cluster, on the correct principle that a
    # declaration must describe the drawing - but the census behind `CLUSTER_BAND_ASPECT` showed the
    # cloud never runs at all, so the guard meant the knob was declared on no map and honored on no
    # map. It binds at the cluster BAND now (`seat_cluster`), which is what the front rows are seated
    # along, so every map both honors and declares it and `TWIN_AXES` reads a shape the sheet
    # actually has.
    # ...BUT ONLY IF THE SHEET ACTUALLY HAS THAT SHAPE. Measured, and this is the third thing the
    # shape work turned up: on a 20-household hamlet the LANE SKELETON seats most of the cluster
    # through `lane_frontage`, and a T spreads houses two ways whatever the band and the row do -
    # Kashikawa declares `elongated` and draws 1.0:1. The band and row bindings are real (Inashiro
    # 3.3:1 crescent, Mizuguchi 1.7:1 round, Sawada 1.1:1 round) but they do not outrank the
    # skeleton, so a blanket declaration would put a shape on the manifest that `TWIN_AXES` reads
    # and the sheet does not have - the same "declaration must describe the drawing" failure the
    # old cloud-only guard was written for, in a worse form because it would look honored.
    #
    # So the DRAWN aspect decides. Where the shape bound, it is declared; where the skeleton
    # overrode it, `cluster_shape_unhonored` records the roll that did not take, because a knob
    # that silently fails to bind is what this whole defect was. `cluster_shape_matches_the_drawing`
    # gates it.
    # MEASURED ON THE CLUSTER'S OWN AXIS, NOT THE PAGE'S (2026-08-19, and this is the second time
    # this one guard has been caught measuring the wrong quantity). The first cut took
    # `max(dx,dy)/min(dx,dy)` over the axis-aligned bbox of house centers - and that ratio collapses
    # toward 1.0 for a band on a diagonal no matter how string-like the cluster is, because it is a
    # function of the field margin's COMPASS BEARING rather than of the cluster's proportion. It is
    # maximally blind at exactly 45 degrees.
    #
    # Three independent settlement-review passes caught it on the same day, with numbers, and it
    # failed in BOTH directions across the shipped pool - axis-aligned vs own-axis:
    #     Kashikawa 1.22 vs 3.83  (rolled `elongated`, DREW 3.8:1, and was recorded unhonored)
    #     Sawada    1.25 vs 3.02  (declared `round`, drew a string - falsely HONORED)
    #     Mizuguchi 2.36 vs 2.77  (declared `round` over its own ceiling on the honest measure)
    #     Inashiro  3.18 vs 3.59  (band near vertical, so the two roughly agree)
    # So it denied an honored knob on one map and honored a contradicted one on another, and
    # `TWIN_AXES` reads this field. The `CLUSTER_DRAWN_ASPECT` docstring promises a quantity that can
    # be "read off a finished map with a ruler" - and a reader lays the ruler ALONG the cluster.
    _declared = declare_cluster_shape(s.M.get("houses", []), plan.cluster_shape, plan.spec.seed)  # the one declaration (homes H04, H05)
    s.M["meta"].update(_declared)
    plan.cluster_shape = _declared["cluster_shape"]  # the knob as resolved over what the band draws (plan D4)
    s.M["meta"]["seat_search"] = dict(s._seat_search)  # the guesses counted (feature 226 FR-003): candidates, placer calls, positions, rectangles
    s._site_chains = None  # the boundary is the homestead stage's; every later placer runs the fit test's own path
    s._site_corridors = None
    s._free_ground = None
    s._seat_region = None
    s._unreachable = None
    s._access = None  # the access tree is the seating's; the manifest keeps it (`access_exit`, `access_corridors`)
    s._pockets = None  # the pockets are drawn by `place_wells` from the house records (`well_pocket`)
    s._corridor_ground = None  # the corridors' ground test is the seating's
    setattr(s, "_corridor_tree", None)  # noqa: B010 - ...and so is the tree's (`ways/tree.py`); read by `access.tree_admits` with a default
    s._wood = None  # the reservations are the seating's; each household's record keeps its own (`wood_share`)
    s._lots = None  # the lots are the seating's (the byre form stays: `draft_byres` draws the stalls it reserved)
    # THE ROLLED SHAPE MUST LEAVE A TRACE EVEN WHEN THE CLOUD NEVER RUNS (known-open ledger
    # 2026-08-16, Kashikawa: the front rows + lane frontage seated all 20 households, the
    # cluster-seeds cloud never ran, and the rolled cluster_shape knob went unhonored with no
    # trace on the manifest - a knob that can silently not-record is the "check that never runs"
    # shape). Record the seeding mode always: "cloud" when cluster_seeds ran (it records
    # meta.cluster_shape itself), "frontage" when the rows/frontage passes seated every house and
    # the rolled shape went unhonored. `settlement_records_cluster_seeding` holds the invariant.
    # ...and this stays a SEPARATE record, keyed on what actually seated the houses rather than on
    # whether the shape got stamped. It used to be derived from the presence of `cluster_shape`,
    # which stopped meaning anything the moment the shape was always declared.
    s.M["meta"]["cluster_seeding"] = "cloud" if _cloud_placed * 2 >= max(1, plan.spec.households) else "frontage"
    s._household_bamboo = plan.bamboo in ("homestead", "both")  # type: ignore[attr-defined]  # a grove farm draws the bamboo it rolls (feature 291)
    plan.placed = s.farmsteads()
    # A ROW VILLAGE'S FAR-ROW HOLDINGS, reserved at seating (feature 291 plan D16), drawn now - before the track and the web,
    # so every way treats them as the crop they are (drawn after the track, Kashikawa's connector ran across one)
    if getattr(s, "_row_holdings", None):
        from .rows import draw_holdings

        s.M["meta"]["row_holdings_drawn"] = draw_holdings(s)
    hold_laid_parts(s, s.M.get("houses") or [])  # the pockets and fixtures stand for the ways laid before they are drawn (M8)
    reserve_the_seating(s)  # ...and the corridors and wood seats it reserved, for every placer after it (M8, `overlap/reserved.py`)
    # how many farmhouses the quarter turn took (269 B18) - measured on what was drawn, so the share is a count, not a hope
    s.M["meta"]["house_quarter_turns"] = sum(1 for h in s.M.get("houses") or [] if abs(wrap_line_deg(float(h.get("rot", 0.0)) - (s._house_bearing or 0.0))) > 45.0)
    # THE TRIM MOVED OUT OF THIS STAGE (feature 126). It existed because the skeleton was laid
    # before the houses, so its arms had to be shortened afterwards once there was something to
    # measure them against. The arms are now laid after the houses and fitted to them, so there is
    # nothing here to trim: at this moment the only ways drawn are the connector and the field spur,
    # and trimming those against house positions is meaningless. `stage_web` trims once the lanes it
    # trims actually exist.


def shapes_drawn_at(drawn: float) -> list[str]:
    """The cluster shapes whose drawn band (`CLUSTER_DRAWN_ASPECT`) holds a drawn aspect - a shape other than round only
    past round's ceiling (the settlement-review of Inashiro, feature 261: crescent's band starts at 1.9 and round's ends
    at 2.0, and a quarter-disc of houses drawn at 1.97 is round). Past every band, the nearest band's shape."""
    ceiling = CLUSTER_DRAWN_ASPECT["round"][1]
    held = [k for k, (lo, hi) in CLUSTER_DRAWN_ASPECT.items() if (lo if k == "round" else max(lo, ceiling + 1e-9)) <= drawn <= hi]
    return held or [min(CLUSTER_DRAWN_ASPECT, key=lambda k: min(abs(drawn - CLUSTER_DRAWN_ASPECT[k][0]), abs(drawn - CLUSTER_DRAWN_ASPECT[k][1])))]


def in_a_shapes_band(houses: Sequence[dict[str, Any]]) -> bool:
    """THE ONE PREDICATE of `test_the_cluster_draws_inside_the_band_of_the_shape_it_declared` (feature 287, homes wave 5):
    do the houses draw an aspect (`cluster_aspect`) some shape's band holds (`CLUSTER_DRAWN_ASPECT`)? Every aspect is at
    least round's floor, so the one way out is past the longest band's ceiling - elongated's 12:1 - where `shapes_drawn_at`
    could only name the nearest band, which the drawing breaks. `seat_every_household` keeps no seating that fails it."""
    drawn = cluster_aspect([h["x"] for h in houses] or [0.0], [h["y"] for h in houses] or [0.0])
    return any(lo <= drawn <= hi for lo, hi in CLUSTER_DRAWN_ASPECT.values())


def drawn_in_band(s: Settlement, plan: SitePlan) -> bool:
    """Does this seating draw a shape's band - or is it a row village, which is no cluster and takes no band?

    A ROW VILLAGE IS A ROW (the GM, 2026-10-01, tripwire seed 33): its farms stand one frontage apart along their street,
    54 to 240 ft on the measured planned rows (research/questions/0033-row-villages-resson.html), so ten farms run 490 to
    2,160 ft - 5:1 to 22:1 against one homestead's depth - and the 12:1 ceiling, a CLUSTER's (`CLUSTER_DRAWN_ASPECT`),
    refused every margin of a ten-farm row. The linear form's row is held by `row_rules` (each farm on its street, none
    behind another); the band holds the forms that draw a cluster."""
    return plan.settlement_form == "linear" or in_a_shapes_band(s.M.get("houses") or [])


def declare_cluster_shape(houses: Sequence[dict[str, Any]], shape: str | None, seed: int) -> dict[str, Any]:
    """The cluster shape the manifest declares, and the plan keeps: the rolled shape wherever the houses draw it, and
    otherwise the knob RESOLVED OVER THE SHAPES THE DRAWING ADMITS (feature 287, homes H05, plan D4) - `shapes_drawn_at`,
    rolled from the map's seed with the knob's own weights (`CLUSTER_SHAPES`). The drawn shape is the declared shape on
    every map; there is no `cluster_shape_unhonored` record. The stage and its unit test read this one function.

    D4'S OTHER HALF WAS TRIED FIRST AND MEASURED A NO-OP (2026-09-29): steering the rank rounds toward the rolled shape -
    the along-the-field ends offered before the ranks while the standing houses draw rounder than the shape's band - left
    31 of 64 maps (pool and cohort 1-60) drawing a crescent or a string rounder than its band, the same 31 as without it:
    the front row, the brook's far bank and the field's chords seat the cluster, and the ends are refused where the ranks
    were. The record of three earlier failed bindings (`CLUSTER_BAND_ASPECT`) says the same. So the knob is narrowed to
    what the band draws, which D4 allows: on that measurement round is declared on 57 of the 64 maps, crescent on
    6, elongated on 1."""
    drawn = cluster_aspect([h["x"] for h in houses] or [0.0], [h["y"] for h in houses] or [0.0])
    space = shapes_drawn_at(drawn)
    rolled = shape or "crescent"
    resolved = rolled if rolled in space else str(_roll(seed, "cluster_shape", tuple(v for v in CLUSTER_SHAPES if v in space) or tuple(space)))
    return {"cluster_shape": resolved, "cluster_aspect_drawn": round(drawn, 2)}


def seat_every_household(s: Settlement, plan: SitePlan) -> tuple[int, int]:
    """Every declared household seated, or the site refused (feature 287, homes H14 and plan D2).

    The chosen margin is seated first (`_seat_households`, whose last round is the exhaustive pass). Where even that
    leaves a household without a house, the ground within reach of this margin is full, and the houses it seated are
    taken back and the next margin of `seat_cluster`'s ranking is seated instead (`margin_ladder`; on a polder only the
    margins on the chosen flank, the waterward fringe being drawn already). The seating kept is the one pass that
    seated everyone - no second roll of anything. Past the last margin the site is refused, naming it: `SiteRefused`,
    raised HERE rather than at `stage_seat` where plan D2 places it, because a margin's capacity is known only by
    seating it. `meta.seat_margin` records which rung seated the hamlet (1: the chosen margin)."""
    want = plan.spec.households
    mark = seating_mark(s)
    placed, cloud = _seat_households(s, plan)
    tried = [placed]
    ladder = margin_ladder(plan, plan.field_archetype in POLDER_ARCHETYPES)
    toe: Any = None
    banded = drawn_in_band(s, plan)
    # ...AND A SEATING WHOSE HOUSES DRAW NO SHAPE'S BAND IS NOT KEPT (feature 287, homes wave 5): past the longest band's
    # ceiling (`in_a_shapes_band`, a string past 12:1) the margin is taken back as one that seated too few is
    for margin in ladder if placed < want or not banded else ():
        # A RUNG WITH NO DRY WAY OUT IS NOT SEATED (feature 287, ways W23): `seat_cluster` asked the head; each rung is
        # asked the same, lazily, before the houses on it are taken back
        toe = (s.toe_band() or None,) if toe is None else toe
        if not seat_has_dry_exit(plan, (float(margin["cx"]), float(margin["cy"])), toe[0], marsh_ground(s.M, only=("pond_fringe",))):
            continue
        unseat_to(s, mark)
        plan.seat = {**margin, "ladder": ladder}
        s.field_face = (float(margin["cx"]), float(margin["cy"]))
        s.M["meta"]["seat_offwind"] = bool(margin.get("offwind"))
        placed, cloud = _seat_households(s, plan)
        tried.append(placed)
        banded = drawn_in_band(s, plan)
        if placed >= want and banded:
            break
    if placed < want:
        raise SiteRefused(f"{plan.spec.name} (seed {plan.spec.seed}): no margin seats all {want} households - seated {tried} on the {len(tried)} margin(s) tried")
    if not banded:
        raise SiteRefused(f"{plan.spec.name} (seed {plan.spec.seed}): no margin seats its households inside a cluster shape's band")
    s.M["meta"]["seat_margin"] = len(tried)
    return placed, cloud


def reserve_the_seating(s: Settlement) -> None:
    """THE SEATING'S RESERVATIONS, HANDED TO THE REGISTRY OF WHAT STANDS (feature 287 M8; plan M3's keep-out, woods W25): the
    access corridors (each leg at the corridor's half-width, for the household whose door it leaves - the legs a house's
    corridor records follow its first, which names the house; the field's corridor and the exit strip are nobody's) and
    every household's wood seats, with the clump the copse plants them at and the copse's own lane buffer about a lane
    (`crown_reach` at the drawn lift, `village_grove`'s). Every placer after the seating then keeps off them by asking the
    registry (`Settlement.admits`), and one that did not is refused at record time."""
    res = s.standing.reserved
    half = s.px(ACCESS_HALF_FT)
    owner: Any = None
    for c in s.M.get("access_corridors") or []:
        owner = c["of"] if c.get("of") else (None if c.get("field") else owner)
        pts = c.get("pts") or []
        if len(pts) >= 2:
            res.reserve_corridor(pts[0], pts[1], half, owner)
    exit_seg = s.M.get("access_exit")
    if exit_seg and len(exit_seg) >= 2:
        res.reserve_corridor(exit_seg[0], exit_seg[1], half, None)
    clump = COPSE_CLUMP_BS * s.bscale
    seats = [p for h in s.M.get("houses") or [] for p in (h.get("wood_share") or {}).get("seats") or ()]
    res.reserve_seats(seats, clump, max(clump * 0.45 + 4, crown_reach(clump, 0.0, lift=crown_lift(s.bscale))))


def corridor_ground(s: Settlement) -> Callable[[list[Pt]], bool]:
    """The ways' own test of a corridor's ground (`settle.corridor_on_lawful_ground`: the run squared at its crossings, then
    `Lawful.on_lawful_ground`), for the seating to admit a corridor by (`access.lawful_ground`) - the settlement package
    cannot import the hamlet generator, so it is installed on the settlement as `_corridor_ground`. The law it reads is the
    seating's (`tree.seating_law`), built once per house seated, not per corridor asked."""
    from ..ways.corridors import ACCESS_WIDTH
    from ..ways.tree import seating_law

    def ground(run: list[Pt]) -> bool:
        law_ = seating_law(s)
        return bool(law_.on_lawful_ground(law_.squared(run), ACCESS_WIDTH))

    return ground


def reserve_field_corridor(s: Settlement) -> bool:
    """THE FIELD'S CORRIDOR, reserved with the exit strip (feature 287, ways W03; homes wave 5): on a brook map a way of the
    hamlet's own must reach its field (`law.field_unreached`), and the web used to look for one only among what the seating
    had left - reported where none kept the law, never refused. So the run the web draws first is reserved before any house
    stands: the ways' own field paths from the tree, the straight ones and then the ones the web's router threads
    (`corridors.field_runs`, `routed_field_runs`: on to the bund, over the brook at a ford where it lies between) - the
    first on lawful ground (`settle.corridor_on_lawful_ground`, the seating's question of every corridor). It joins the
    tree, so no envelope covers it (`AccessTree.covers_box`) and no share of the wood floor stands on it
    (`WoodShares.share`), and it is recorded as the tree's legs are (`field` on each), oriented toward the tree, for the web
    to draw where no way of its own reaches the field (`settle.settle_field`), bowed round a shed on it as a house's
    corridor is. True where one is reserved or the rule asks none (no brook, no field); False where no lawful run reaches
    the field from this margin - `_seat_households` then seats no one on it and the ladder offers the next."""
    from ..ways import law
    from ..ways.bund import BRANCH_WIDTH, paddy_ground
    from ..ways.corridors import FIELD_ROLE, field_router, field_runs, routed_field_runs
    from ..ways.geom import memo_ground, worked_ground
    from ..ways.settle import corridor_on_lawful_ground
    from ..ways.tree import admits, seating_law

    tree = getattr(s, "_access", None)
    brook = next(iter(law._brooks(s.M)), [])
    if tree is None or len(brook) < 2:
        return True
    grounds = [g for g in (paddy_ground(s), memo_ground(s, "worked", worked_ground)) if g.edge is not None]
    if not grounds:
        return True
    fords = [(float(x), float(y)) for x, y in (s.M.get("meta") or {}).get("brook_fords") or []]
    segs = list(tree.segs)

    def candidates() -> Iterator[list[Pt]]:
        yield from field_runs(segs, grounds, BRANCH_WIDTH / 2.0, brook, fords)
        route = field_router(s, brook)
        for ground in grounds:
            yield from routed_field_runs(segs, ground, BRANCH_WIDTH / 2.0, route, brook, fords)

    # ...AND WHERE THE TREE STAYS LAWFUL WITH IT (feature 287 wave 6, `tree.admits`): the web draws it as a tree lane, never
    # cut, so its joint with the exit strip is judged here with every other rule of the lane law
    run = next(
        (r for r in candidates() if len(r) >= 2 and corridor_on_lawful_ground(s.M, r, BRANCH_WIDTH) and admits(seating_law(s), s.M, [(float(x), float(y)) for x, y in r[::-1]], FIELD_ROLE)), None
    )
    if run is None:
        return False
    back = [(float(x), float(y)) for x, y in run[::-1]]
    for a, b in zip(back, back[1:], strict=False):
        tree.add(a, b)
        s.M.setdefault("access_corridors", []).append({"pts": [[round(a[0], 1), round(a[1], 1)], [round(b[0], 1), round(b[1], 1)]], "field": True})
    return True


def _seat_households(s: Settlement, plan: SitePlan) -> tuple[int, int]:
    """Seat the households on `plan.seat`'s margin: the site boundary installed for it, the front row, the ranks, the
    rescue rounds, then the exhaustive pass over the legal ground within reach (homes H14). Returns `(placed, the
    cloud's share)`; the boundary stays installed for the stage to take down."""
    seat = plan.seat
    # THE SITE BOUNDARY FIRST (feature 226): one outline separating the buildable ground from everything the map holds,
    # computed once; the fit test reads it instead of its five ground scans, and the seats below are proposed from it.
    install_site_boundary(s, plan)
    face_the_houses(s, plan)
    s._seat_region = None  # built below once the access tree stands (feature 297, plan B1); none for a form without one
    # EACH HOUSEHOLD'S LOT, keyed on seat order (feature 287, plan M5): the k-th house seated takes rung k of the size
    # ladder and the k-th place in the kura quota, so the counts close whatever seat each household lands on
    s._byre_form, _share = household_byre_form(s)
    s._byre_pockets = []
    s._pockets = []  # the well pockets this seating has laid (feature 287, homes H10-H11; `needs_pocket`)
    # ...AND EACH HOUSEHOLD'S SHARE OF THE WOOD FLOOR (feature 287, woods W25 made absolute; plan D9): a household is seated
    # only where it can reserve copse seats covering `HOMESTEAD_WOOD_FT2`'s floor within the dooryard copse's reach of its
    # own house, and no later household or corridor takes them (`homestead_parts/wood_share.py`)
    if getattr(s, "_nucleated", False):
        install_wood_shares(s, HOMESTEAD_WOOD_FT2[0], COPSE_HOUSE_REACH_FT, ACCESS_HALF_FT)
    # ...AND ITS FARMSTEAD FIXTURES (feature 287, homes H32): a quota per kind, laid in the bundle with the hamlet's forms
    s._fixture_forms = fixture_forms(plan.spec.seed, plan.manure_form)
    _quota = {**fixture_quota(plan.spec.seed, plan.spec.households, {k: int(v) for k, v in plan.fixtures_min.items()}), **retirement_quota(s, plan.spec.households)}
    # ...ON EVERY FORM (feature 291 on 287): a grove farm keeps its fixtures in its lot as a clustered household does; its byre
    # is not a part of its bundle (no stall is laid beside a grove farm's house), so its lot keeps no beast
    s._lots = HouseholdLots(plan.spec.seed, plan.spec.households, _share if getattr(s, "_nucleated", False) else 0.0, _quota)
    s._seat_search = {"candidates": 0, "placer_calls": 0, "positions": 0, "rects": 0, "rounds": 0}  # rounds: lattice rounds run (0 when the front row seated everything; over 4 = the rescue ran)
    _house_max = (s.px(46) * 1.35, s.px(28) * 1.10)  # the LARGEST house `_try_place_bundle` rolls: the front row's computed standoff clears it

    def _pretest(x: float, y: float) -> bool:
        """Count a candidate (feature 226 FR-003). The cheap refusal that stood here - a house-sized box against the
        boundary and the placed boxes - is the placer's own first test now (feature 227: the whole homestead's
        ENVELOPE, `_envelope_blocked`). OPEN DEFECT (the 227/230 merge, 2026-09-13): with 230's far-bank rule as the only
        refusal here, the reference cluster seats 195 px from its fields against the 60 px `cluster_abuts_fields` bar,
        and 48 of 82 pool farmhouses stand beyond the engine's own `_field_adjacent` 165 px (settlement-review). The
        fix is NOT to restore the box test - those locals are the envelope's now - it is to assert field adjacency on
        the PLACED position and to score the envelope for it, which is the next piece of work on this feature.

        THE BROOK'S FAR BANK IS NO LONGER REFUSED HERE (feature 261). Feature 230 refused a house across the brook from
        the rest because no way could reach it - Kashikawa shipped one 52 ft beyond the water with no bridge anywhere.
        Ways cross the brook at a ford now and `bridges()` decks the crossing, so a hamlet may stand astride its own
        small channel, as the record has it (Harie, specs/230 R6); a house the web still cannot reach is caught by the
        reach check and re-rolled, as any stranded house is. Both forms are attested at a stream's size (269 B23;
        research/questions/0035-villages-beside-their-stream-one-bank-or-both.html: Hongcun beside its stream, Xidi and Likeng on both banks), so neither bank is refused;
        each farmstead stays whole on one bank, which the same entry records as a guess."""
        s._seat_search["candidates"] += 1
        region = getattr(s, "_seat_region", None)
        return region is None or region.offer([(x, y)])[0]

    ax, ay = seat["along"]
    ox, oy = seat["out"]
    # THE LATTICE'S DRAW, one per map: the seed's own hash (feature 226's re-roll salt went with the re-roll, feature 287;
    # the first roll's draw is this one, so no map moves).
    rng = random.Random((plan.spec.seed * 2654435761) & 0xFFFFFFFF)
    placed = 0
    # THE SEATING'S BAND (feature 306): the margin was chosen, and the canvas and belt sized, with `HOMESTEAD_GROUND_FT`'s band;
    # the households are spread over one holding their whole ground, wood floor and all (`SEATING_GROUND_FT`, research R12)
    dep, lat = band_extent(plan.spec.households, plan.cluster_shape, SEATING_GROUND_FT)

    # THE FRONT ROW GOES DOWN FIRST, along the band's field-facing face. A cluster seeded only by
    # its SHAPE fills its whole depth evenly, and on a small hamlet that can leave the field ringed
    # by four houses where `field_ringed` (retired, feature 141) wants five - the map then reads as a settlement that
    # happens to be near a paddy rather than one that works it. Seating a row against the margin
    # first is also just what a farming hamlet looks like: the houses front the field they farm, and
    # the back rows fill in behind them.
    # (no quota guard here: the row is capped at 8 seats and the tier's floor is 10 households, so
    # the front row alone can never meet the ask)
    # TWO passes at two standoffs. `field_ringed` (retired, feature 141) wants five farmhouses within 165 px of the field
    # outline, and a single row of eight candidates at one standoff can land four when the near
    # ground is awkward - the placer refuses a bundle that laps a bund or a ditch, and every refusal
    # is a house that ends up in the back rows instead. Offering the same row again a little further
    # out costs nothing when the first pass filled it and rescues the ring when it did not.
    # EVERY SEAT MUST LIE IN THE BAND. The front row follows the field OUTLINE and the frontage rows
    # follow the lanes, and both can wander well past the cluster on a long fan - which produced a
    # nucleated hamlet with three or four farmsteads strung hundreds of px down the margin. That is
    # a form defect on its own (a nucleus is supposed to read as a nucleus), and it was ALSO the
    # cause of three separate gate failures: a windbreak sized off the furthest house became a green
    # blanket, a copse over the full house bbox left the map no blank ground, and a stray farm past
    # the last well tripped `settlement_dwellings_watered`. Fixing the seats fixes all of it at the
    # source, which is why the percentile guards elsewhere are belt-and-braces rather than the cure.
    # HOW FAR FROM THE SEAT CENTER A HOMESTEAD MAY STAND, and it depends on the FORM (feature 126).
    #
    # A nucleated cluster is the tight case this number was calibrated for and keeps 1.15. The other
    # two forms are not looser versions of it, they are different settlements, and their farmsteads
    # are physically BIGGER: a non-nucleated bundle carries its own grove and yard (see
    # `_place_bundle`, which branches on `_nucleated`), so the same bound seats fewer of them. Left
    # at 1.15 the generator simply dropped households - Inashiro rolled linear and seated 13 of 15,
    # which is a silent shortfall rather than an error.
    #
    # THIS WAS NOT WHAT FIXED THE SHORTFALL, and saying so here saves the next reader from crediting
    # it. Inashiro's 13-of-15 was caused by `_nucleated` being set from the FORM, which gave a linear
    # map grove-wrapped bundles too large to fit; the fix was to set `_nucleated` from whether the
    # form is dispersed (see `stage_water_frame`). Widening the bound alone changed nothing.
    #
    # It is kept because it is DESCRIPTIVE rather than corrective: a dispersed settlement genuinely
    # occupies more ground than a nucleated one - that is what the form IS - and holding it to a
    # nucleated cluster's radius would misrepresent it. The multipliers are not measured optima, and
    # they should not be quoted as if they were; they are the extents the two forms plausibly want.
    #   dispersed - the Tonami case: each farmstead sits in the middle of its OWN holding, so the
    #               settlement's extent is the extent of the land it farms, not of a cluster band.
    #   linear    - strung along the connector, so it grows LONG rather than wide; the bound is a
    #               radius, so a smaller widening buys the length the form needs.
    bound = FORM_BOUND.get(plan.settlement_form, 1.15) * math.hypot(lat, dep)

    def in_band(q: Pt) -> bool:
        return math.hypot(q[0] - seat["cx"], q[1] - seat["cy"]) <= bound

    # THE ACCESS TREE'S FIRST CORRIDOR, THE EXIT STRIP (feature 287, plan M3's seat half): from the cluster's center
    # outward past the furthest seat any round may offer, so every house after is admitted only with a corridor to it
    # (`settlement/rolling/access.py`). A dispersed hamlet has no internal network and is not held to one.
    # ...ON LAWFUL GROUND (feature 287, ways): the strip is held to the corridors' own test, turned off the outward bearing
    # as far as a quarter turn where it is refused straight out; a margin with no lawful way out seats no one here, and
    # the ladder offers the next (`seat_every_household`)
    # ...NOT ON A GROVE FARM'S FORM (feature 291 on 287): a dispersed hamlet's farms are reached by their own paths, and a row
    # village's by its planned streets, its road running on from the first street's end (`street.street_run_out`) - an exit
    # strip from the seat's center was a corridor no way of the row follows, and the settle, drawing it, kinked it across the
    # brook off its ford (cohort seed 903)
    if plan.settlement_form == "nucleated":
        from ..ways.tree import seating_judge

        s._corridor_ground = corridor_ground(s)
        setattr(s, "_corridor_tree", seating_judge(s))  # noqa: B010 - ...and the whole tree judged as lanes with each corridor (feature 287 wave 6)
        _length = bound * 1.5 + BUNDLE_PITCH
        _out = exit_bearing(s, (float(seat["cx"]), float(seat["cy"])), (float(ox), float(oy)), _length)
        if _out is None:
            return 0, 0
        start_tree(s, (float(seat["cx"]), float(seat["cy"])), _out, _length)
        if not reserve_field_corridor(s):
            return 0, 0  # ...AND ITS FIELD'S CORRIDOR (ways W03): a margin with no lawful way on to its field seats no one here
    # THE SEAT REGION (feature 297, FR-001, plan B1): built once the exit strip and the field's corridor stand, kept current as
    # houses are seated; every round below offers only the seats it holds (`region.SeatRegion`)
    s._seat_region = SeatRegion(s, seat_window(s, s.px(FIELD_REACH_FT))) if getattr(s, "_nucleated", False) else None
    # THE SHARED SHEDS' POCKETS BEFORE ANY HOUSE (feature 287, homes H06): on the `detached_commons` form the sheds are no
    # household's part, so their ground is reserved in the band first and the houses pack round it - AFTER the exit strip
    # and the field's corridor, whose strips a pocket keeps off (`_commons_pocket_clear`; M8: the registry refuses a shed on
    # a corridor, and the first pocket, nearest the band's middle, stood where every exit strip starts), and filed with the
    # wood shares so no household's seat is reserved under one
    if getattr(s, "_nucleated", False) and s.resolve("byre_form") == "detached_commons":
        want = commons_byre_target(plan.spec.households)
        if len(s.reserve_commons_byres(seat, plan.spec.households)) < want:
            raise SiteRefused(f"{plan.spec.name} (seed {plan.spec.seed}): the seat band holds no ground for {want} shared byres")
        if s._wood is not None:
            s._wood.file_byre_pockets(s, s._byre_pockets)

    # THREE standoffs, not two. `field_ringed` (retired, feature 141) wants five farmhouses within 165 px of the field
    # outline and the placer refuses any bundle that laps a bund or a ditch, so a single ring of
    # candidates can land four on awkward ground. Each extra pass is free when the earlier one
    # filled the row.
    # The FRONT ROW is allowed a little further out than the rest - a house hugging the field is
    # part of the settlement wherever the band's nominal circle happens to fall, and `field_ringed` (retired, feature 141)
    # wants five of them within 165 px of the outline.
    # Standoffs run out to 150 px, which is still inside `field_ringed` (retired, feature 141)'s 165 px band. The near
    # ground is often the busiest on the map - crop up to the bund, the collector's out-of-crop
    # stretches with their corridors, the field spur - so a row that stops at 92 px can land four
    # houses where five are wanted while perfectly good ground sits at 120. A farmhouse 150 px from
    # its paddy is still a farmhouse on its paddy.
    # THE FRONT ROW IS ONE RANK, NOT THE WHOLE HAMLET (settlement-review on Inashiro and Mizuguchi,
    # 2026-08-17). Once the row began sampling by density it could seat every household by itself,
    # and it did: the cluster came out a single file along the paddy margin - Mizuguchi 891 x 123 ft,
    # aspect 7.24, with an rms residual of 22 ft about a smooth curve, so NO house stood behind any
    # other anywhere on the map. Inashiro went the same way (elongation 3.79 -> 5.42, width 569 ->
    # 445 ft at unchanged length) against 1.22 for the authored Ikegami on the identical brief. It
    # took the courtyards with it: Mizuguchi's copse collapsed 11 -> 4 clumps and its byres were
    # pushed 20+ ft out of the homestead courtyards into the windbreak, because a one-rank cluster
    # has no interior gap ground left. `consts.py` says the pitch is chosen to keep the cluster
    # "dense enough to read as a nucleus and open enough for its courtyards, its wells and its
    # byres"; a single rank has neither half.
    #
    # THE CAP IS ONE RANK'S WORTH OF THE BAND, derived rather than picked: the margin band is `lat`
    # long, and homesteads in it stand a bundle pitch apart, so `2 * lat / pitch` is how many fit in
    # the rank that fronts the field. Everything past that is a household the flanking and cloud
    # passes should seat BEHIND, which is what makes a nucleus a nucleus. Floored at 6 so
    # `field_ringed` (retired, feature 141) (five farmhouses within 165 px of a big field's outline) can always be met by
    # the row alone - the defect this row exists to prevent.
    # THE ROW'S SHARE FOLLOWS THE ROLLED SHAPE (feature 227): under the envelope-first placer the row fills every seat it
    # is offered, and "one rank's worth of the band" (2 * lat / pitch) is the whole quota on a long margin - Inashiro
    # strung all 15 along the paddy at a drawn aspect of 5.07 against a rolled crescent's 1.9-4.2. A cluster of N
    # houses drawn at aspect A is about sqrt(N * A) houses long, so that many front the field and the lattice seats the
    # rest behind them, and the shape knob binds where the band alone could not. The middle of the shape's band is
    # the aspect aimed at; the floor of 6 keeps `field_ringed` (retired, feature 141) reachable by the row alone, as before.
    _lo_a, _hi_a = CLUSTER_DRAWN_ASPECT.get(plan.cluster_shape or "crescent", (1.9, 4.2))
    # ...times two, MEASURED: the ranks stand an envelope's depth apart (about 1.2 pitches) along an ARC, and the drawn
    # aspect is read on the house centers' own axis, so a block of L by N/L houses reads about half of L*L/N - seven
    # in Inashiro's row drew 1.66 on a rolled crescent (1.9-4.2), six in Kuwabata's 1.71 on a round (1.0-2.0).
    front_cap = min(plan.spec.households, max(6, round(math.sqrt(plan.spec.households * (_lo_a + _hi_a)))))
    # ...BUT A ROW VILLAGE IS ONE ROW (feature 291; research/questions/0031-clustered-and-scattered-villages-shuson-sanson.html, "LINEAR": farmsteads strung along the way, each
    # holding behind its house). The cap above exists to make a nucleated cluster stand in ranks; applied to the linear form
    # it did the same, and since feature 126 every linear roll drew a block (settlement-review 2026-09-29: Mizuguchi 611 x
    # 715 ft with 1 of 12 houses on its track, Kashikawa 2 of 20). The frontage pass below could not help: it fronts the
    # CONNECTOR, which `stage_track` lays only after the houses, so at this moment it offers nothing. A linear hamlet's row
    # takes every household it can seat along its field, and the track is then laid along the row (`stage_track`).
    _linear = plan.settlement_form == "linear"
    _rows_seated = False  # a row village whose streets were planned takes no ranks (feature 291 plan D15)
    if _linear:
        front_cap = plan.spec.households

    # ...AND A FRONT-ROW SEAT MUST ALSO BE REACHABLE FROM A TRACK, not merely near the paddy
    # (settlement-review, Inashiro 2026-08-17 - the same review round as the rank cap above, which
    # is the OTHER half of this defect: that one bounds HOW MANY seats the row takes, this one bounds
    # WHICH). The row runs FIRST and follows the field OUTLINE, which on a long fan strings it
    # hundreds of px past wherever the rolled lane skeleton lies - so the row won every seat and the
    # frontage pass below got the leftovers. Measured on Inashiro: house-to-lane median 109 ft, five
    # houses past 150, a whole seven-farmstead lobe fronting nothing, and a 252 ft lane spur with no
    # house within 96 ft anywhere. That is the defect the frontage pass's own comment below records
    # curing ("a median house-to-lane distance of 94 ft ... with one lane dead-ending in open
    # ground"), returned by a different route - and no gate check can see it, because `field_ringed` (retired, feature 141)
    # is satisfied by exactly the seats that cause it.
    #
    # A CAP, NOT A LADDER - the difference was MEASURED, because the ladder is the shape every other
    # rung in this function uses and here it did nothing. Offering the whole standoff ladder twice,
    # once capped and once admitting anything, left every median where it started (109/59/65/118 ft):
    # the capped pass cannot fill the row on a long fan, so the uncapped pass seated the very houses
    # the cap had just refused. A cap only bites when there is no second chance at the same seats -
    # and none is needed, because the passes BELOW this one (lane frontage, the in-band cloud, four
    # widening rounds) are the real fallback and seat in-band ground by construction.
    #
    # TIGHTENING THE BAND INSTEAD WAS TRIED AND IS WRONG - recorded so it is not retried. Dropping the
    # row's `bound * 1.3` allowance to `bound` made Inashiro WORSE (109 -> 158 ft, houses past 150 px
    # 4 -> 8) and Mizuguchi too (65 -> 93). A front row that cannot follow the field outline does not
    # move inward; it loses its seats to the cloud, which sits further from the tracks still. The
    # row's reach past the band was never the defect - its blindness to the tracks was.
    #
    # ONE RUNG, COMPUTED (feature 227 FR-002), where a ladder of eight standoffs (46 to 150 px) stood: the seat is where
    # the homestead stands - the wall rule, the tilt's slack, and the whole homestead's reach toward the chord (the
    # union envelope at the largest house the roll can take: a paddy the yard faces gets the yard's depth, a paddy the
    # kura faces the kura's). The ladder's other rungs were a second rank built ten to twenty pixels at a time behind
    # the first, which under the envelope-first placer (no spiral to slide the seats apart) was two hundred refused
    # candidates per map and a cluster strung along the paddy whatever shape it rolled; a rung of one house depth
    # seated NOBODY on Kuwabata's dike heads (the yard faces the paddy there) and the cluster drifted 112 px off its
    # field. The ranks behind the front row are proposed behind the standing houses, below.
    def _ground_push(s_: Settlement, seat_: Pt, n_: Pt, house_: tuple[float, float]) -> tuple[Pt, bool]:
        """The seat moved once along `n_` by the outline's reach past the homestead's near edge - zero when the box is clear."""
        _bx = s_._bundle_envelope(seat_[0], seat_[1], house_[0], house_[1], shed=True)
        _pts = [(_bx[0] + dx * _bx[2] / 2, _bx[1] + dy * _bx[3] / 2) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
        if s_._site_corridors is None or not s_._site_corridors.hit_points(_pts):
            return seat_, False
        lx, ly = -n_[1], n_[0]  # the lateral axis
        half_lat = abs(lx) * _bx[2] / 2 + abs(ly) * _bx[3] / 2
        near = _bx[0] * n_[0] + _bx[1] * n_[1] - (abs(n_[0]) * _bx[2] / 2 + abs(n_[1]) * _bx[3] / 2)  # the box's near edge along n
        far = near + (abs(n_[0]) * _bx[2] + abs(n_[1]) * _bx[3])
        push = 0.0
        for ring in s_._site_corridors.ring_pts:
            for x, y in ring:
                if abs((x - _bx[0]) * lx + (y - _bx[1]) * ly) <= half_lat:
                    d = x * n_[0] + y * n_[1]
                    if near <= d <= far:
                        push = max(push, d - near)
        # ...AND ACROSS A BROOK THAT RUNS BETWEEN THE ROW AND ITS FIELD (feature 261, Inashiro's rolled crescent). The
        # brook skirts the fan 34-44 ft outside its margin, so on a seat facing the wind down that flank every front seat
        # lay in the water's corridor and was refused; the displaced households were seated by the cloud behind, and a
        # crescent that drew 4.07:1 on main drew 1.62:1. The row stands on the brook's far bank instead, fronting its field
        # across the water - the push is the course's reach past the box's near edge, by its own clearance. A row across
        # its brook from its field is one of the two forms the record gives a hamlet at a stream's size (269 B23,
        # research/questions/0035-villages-beside-their-stream-one-bank-or-both.html), not an exception to it.
        wet = water_push(s_._site_corridors.water, (_bx[0], _bx[1]), n_, half_lat, near, far)
        by_water = wet > push
        push = max(push, wet)
        if push <= 0.0:
            return seat_, False
        # ...cleared by a FOOTPATH's room, not a hair: a homestead pushed to two pixels off a dike's bank left no way a
        # lane could pass between them, the web stranded it, and the re-roll then forbade the only front seats the
        # dike heads offer (Kuwabata: front 0 on the kept roll, the cluster 162 px off its polder)
        push += WEB_FABRIC_GAP * 2.0 + 6.0
        return (seat_[0] + n_[0] * push, seat_[1] + n_[1] * push), by_water

    # the homestead's CORE - the house, the yard south of it, the kura north - is what always faces the paddy the same
    # way; the garden's side is chosen later by the sun, so it is not in the reach (counted, it stood every front house
    # off a paddy beside it by a garden's width, 81 px on Inashiro against the 60 the cluster is held to)
    # ...AND THE WELL POCKET (feature 287, homes H10): a household carrying one - the first always does, and it is the most
    # central front seat - reaches that much further toward a paddy beside or before its yard, so the row stands off by it
    s._household_well = True
    try:
        _g0 = s._bundle_geom(0.0, 0.0, _house_max[0], _house_max[1], "E", shed=True, rot=0.0)  # unturned: each seat adds its own turn
    finally:
        s._household_well = False
    _core = s._bbox_of([r for r in (_g0["house"], _g0["yard"], _g0.get("shed"), _g0.get("well")) if r is not None])
    _reach = (_core[0] - _core[2] / 2, _core[1] - _core[3] / 2, _core[0] + _core[2] / 2, _core[1] + _core[3] / 2)  # (left, top, right, bottom) about the house center
    # A ROW VILLAGE'S ROW (feature 291): the whole farmstead - its grove too, which may face the field - stands off the field,
    # the seats step at the farmstead's own width rather than the nucleated pitch, and the row runs the field's whole edge
    _row_kw: dict[str, Any] = {}
    if _linear:
        from .rows import ROW_FRONTAGE_MAX_FT

        _bb = _g0["bbox"]
        _reach = (_bb[0] - _bb[2] / 2, _bb[1] - _bb[3] / 2, _bb[0] + _bb[2] / 2, _bb[1] + _bb[3] / 2)
        _row_kw = {"pitch": min(max(_bb[2], _bb[3]), s.px(ROW_FRONTAGE_MAX_FT)), "reach": float("inf")}  # never past a lot's frontage (`rows.py`)
    # A ROW VILLAGE'S FARMS STAND IN ROWS ALONG THEIR STREETS (feature 291 amendment 3, `rows.py`; research/questions/0033-row-villages-resson.html
    # and 156): the row takes every household it can, and no front-row, frontage or rank pass takes the rest. Where its
    # streets cannot hold every farm, `seat_every_household` takes them back and seats the next margin, and past the last
    # the site is refused (feature 287 plan D2 - the GM's choice of 2026-09-30, over the unseated remainder 291 reported).
    if _linear:
        from .rows import seat_rows  # the row module reads this stage's frame; imported where it is used

        placed += seat_rows(s, plan, _g0["bbox"])
        front_cap = placed
        _rows_seated = True  # NEVER IN RANKS (FR-013, plan D15): a margin whose streets cannot hold every farm is left for the next
    for _rung in (0,):
        for (fx, fy), _n in front_row(
            plan, plan.spec.households if _linear else min(plan.spec.households, 12), standoff=None, chains=s._site_chains, house=_house_max, envelope=_reach, with_normals=True, **_row_kw
        ):
            if placed >= front_cap:
                break
            # THE ONE COMPUTED MOVE AGAINST THE GROUND (feature 227 FR-002, the GM's "measuring the distance ... and then
            # moving however much the correct amount is", applied to the outline): the chord is the crop's edge, but the
            # buildable line is the outline's - the dike's bank, a pond's fringe - which can lie tens of pixels beyond
            # it (Kuwabata's dike heads: every front seat refused, the cluster 112 px off its polder). Where the seat's
            # box is inside the outline, it is pushed once along the chord's normal by the outline's measured reach
            # past the box's near edge, and offered there.
            (fx, fy), _by_water = _ground_push(s, turn_the_seat(s, (fx, fy), _n, _reach), _n, _house_max)
            # NO LANE TEST HERE ANY MORE (feature 126). This used to read
            # `_row_seats < _FIELD_RING_FLOOR or _lane_dist(...) <= _FRONT_ROW_LANE_CAP`, which
            # judged a front-row seat by how near it fell to a drawn lane. The internal lanes are
            # now laid AFTER this stage, so at this moment the only ways on the map are the
            # connector and the field spur - and the cap was therefore demoting good seats for
            # being far from a track that has nothing to do with them. Worse, it made the
            # settlement's shape depend on a way that has not been decided yet, which is the exact
            # inversion this feature exists to remove: a farmhouse is sited by the FIELD it works
            # and the ground it can stand on, and the lane is worn afterwards between the houses.
            # A SEAT PUSHED ACROSS THE BROOK TRIES A QUARTER PITCH EITHER WAY ALONG THE ROW (feature 261): each seat moves by
            # the water's own reach at its place, so seats a pitch apart on the chord land nearer than a pitch on the far
            # bank and every other one collided - Inashiro's crescent seated 5 of 10 in its row and drew 1.95:1. Sampling
            # the whole row at three quarters of a pitch honored it and moved Kuwabata, which has no brook, enough to
            # split its lane web in two; the extra tries go only where the water moved the seat.
            _tries = [(fx, fy)] + ([(fx - _n[1] * d, fy + _n[0] * d) for d in (BUNDLE_PITCH / 4.0, -BUNDLE_PITCH / 4.0)] if _by_water else [])
            for tx, ty in _tries:
                if math.hypot(tx - seat["cx"], ty - seat["cy"]) <= bound * 1.3 and _pretest(tx, ty) and s.try_place(tx, ty, "plain"):
                    placed += 1
                    break
    # ...then rows FLANKING the lanes, before any shape fill. A lane exists to be fronted, and a
    # cluster seeded only by its shape leaves them running across empty middle: the review of the
    # first draft measured a median house-to-lane distance of 94 ft against Ikegami's 55, with one
    # lane dead-ending in open ground and no house at its end. Offering the placer seats at exactly
    # the corridor's edge is what puts the doors on the street.
    #
    # THIS PASS IS WHAT BUILDS THE BACK RANK (2026-08-17, and the history is worth two sentences
    # because a comment here was briefly WRONG about it). For part of one day `front_row` sampled by
    # density with no cap and seated every household by itself, this pass placed nothing, and a
    # comment was written saying so - "now a fallback". Three settlement-reviews then showed what
    # that actually meant: the cluster had become a single rank along the paddy, Mizuguchi at aspect
    # 7.24 with no house standing behind any other. The cap above is the fix, and it makes THIS pass
    # load-bearing again: the households past one rank's worth are seated here, behind the front row.
    # Measured on Mizuguchi after the cap, distance from each house to the field outline falls in
    # four bands - 18/41/58/58, then 96/101/116/128, then 193/193/216, then 297 ft - and everything
    # past 150 ft (the front row's furthest standoff) came from this loop.
    #
    # WHAT THE CAP COSTS, recorded rather than left implied: fronting loosens. Mizuguchi's median
    # house-to-lane went back to ~98 ft from the ribbon's 77, with 4 of 12 within 60 ft rather than
    # 10. The ribbon's tighter fronting was an artifact of the defect, not a baseline worth keeping -
    # but ~98 is the figure an early review criticized against Ikegami's 55, and this loop is where
    # a future tightening belongs, since it is the pass now doing the seating.
    # THE CONNECTOR-FRONTAGE PASS IS RETIRED (feature 291 amendment 3): it seated a linear hamlet along the connector, which
    # does not exist when the homesteads are seated, so it placed nothing; a row village's farms now stand along the
    # streets its row planned (`rows.py`, research/questions/0033-row-villages-resson.html), and a linear hamlet takes no other pass.
    _cloud_placed = 0
    s._seat_search["front"] = placed  # the households the front row seated (R2 reads it beside the cap)
    _row: list[Pt] = [(h["x"], h["y"]) for h in s.M.get("houses", [])]  # the front row as it stands: the lattice's rank 0
    # THE RANKS BEHIND THE FRONT ROW ARE PROPOSED BEHIND THE STANDING HOUSES (feature 227 FR-002/D8). The random cloud
    # deduped to a lattice (feature 226) relied on the placer's spiral to slide its seeds into a fit; the envelope-first
    # placer takes the seat it is given or makes one computed move, so the seats have to be RIGHT: each round offers,
    # behind every house of the rank before it, the seat one envelope's depth further from the field along the band's
    # outward vector, and the staggered seat behind the midpoint of each neighboring pair (a brick pattern). A house
    # seated there fits by construction unless the ground refuses it or the band ends. Measured before this: Kuwabata
    # 14 of 16 and Inashiro strung along the paddy at 5.1 (rolled crescent, 1.9-4.2) on the deduped cloud.
    # The rescue (rounds five to seven) keeps the old cloud over a wider band, seeded a third of a pitch apart.
    _env = s._bundle_envelope(seat["cx"], seat["cy"], _house_max[0], _house_max[1], shed=True)
    # one envelope's depth along the outward vector, plus THE ROOM A LANE NEEDS BETWEEN THE RANKS (`MIN_WEB_GAP`,
    # both neighbors' clearance and the tread between them) - four pixels was the first figure and it left the pool's
    # ranks abutting at a median 4 px, which no alley can thread: the web then could not reach the interior and
    # cohort seed 39 stranded a farmhouse the re-roll could not save. A rank is separated from the rank in front by
    # the lane that serves it. And, where the ranks climb NORTH away from the
    # field, the sun corridor a yard owes to its south (`SUN_CORRIDOR_FT`): the rank in front stands exactly there,
    # and at the bare depth every seat behind it was clear of the ground and refused by the parts' rules (cohort
    # seed 8, the paddy to the south: the "clear" seats of every rank round failed, 9 of 11 seated)
    _rank_step = abs(ox) * _env[2] + abs(oy) * _env[3] + s.px(MIN_WEB_GAP) + max(0.0, -oy) * s.px(SUN_CORRIDOR_FT)
    for attempt in range(7):
        if placed >= plan.spec.households or _rows_seated:  # NEVER IN RANKS BEHIND A ROW (FR-016): a farm its streets could not hold is reported unseated
            break
        s._seat_search["rounds"] = attempt + 1  # the rounds this roll needed (over 4 = the rescue ran); R2 reads it per map
        wlat, wdep = lat * (1.0 + 0.22 * attempt), dep * (1.0 + 0.16 * attempt)
        _kept: list[Pt] = []
        _standing: list[Pt] = [(h["x"], h["y"]) for h in s.M.get("houses", [])]
        if attempt < 4 and _standing:
            # A LATTICE MEASURED FROM THE ROW, NOT A STEP BEHIND WHOEVER STANDS IN FRONT (settlement-review, feature
            # 227). Offering each seat one step behind a STANDING house compounds: rank 2 is measured from rank 1,
            # which was measured from the row, and every refusal along the way shifts what follows it, so the cluster's
            # centroid walks away from the field round by round and the ranks stop being ranks. Kuwabata's cluster
            # ended 114 px off its polder and Sawada's resolved into eight pieces. The lateral positions still come
            # from the houses that stand - the cluster is as wide as it is - but the DEPTH of round k is the row's own
            # depth plus k steps, measured once from the seat, so a rank is where a rank should be and four rounds
            # reach exactly four steps back. A brick: the even rounds offer the midpoints between neighbors, the odd
            # rounds the seats straight behind.
            _a_of = lambda q: (q[0] - seat["cx"]) * ax + (q[1] - seat["cy"]) * ay  # noqa: E731 - the band's two coordinates, used here only
            _o_of = lambda q: (q[0] - seat["cx"]) * ox + (q[1] - seat["cy"]) * oy  # noqa: E731
            _along = sorted(_standing, key=_a_of)
            _row_out = min(_o_of(q) for q in (_row or _standing))  # the front row's own depth: `out` runs away from the field
            _depth = _row_out + _rank_step * (attempt + 1)

            def _seat_at(u: float, _d: float = _depth) -> Pt:
                return (seat["cx"] + ax * u + ox * _d, seat["cy"] + ay * u + oy * _d)

            _us = [_a_of(q) for q in _along]
            _ends = [(_along[0][0] - ax * BUNDLE_PITCH, _along[0][1] - ay * BUNDLE_PITCH), (_along[-1][0] + ax * BUNDLE_PITCH, _along[-1][1] + ay * BUNDLE_PITCH)]
            if attempt % 2 == 0:
                _cands = [_seat_at((p + q) / 2) for p, q in zip(_us, _us[1:], strict=False)]
                # the brick's outer half-seats grow the rank along the field by half a pitch each: with the full-pitch
                # ends, offered only when the back is refused (Mizuguchi's round strung to 4.5 with them in every round)
                _ends += [_seat_at(_us[0] - BUNDLE_PITCH / 2), _seat_at(_us[-1] + BUNDLE_PITCH / 2)]
            else:
                _cands = [_seat_at(u) for u in _us]
            _cands.sort(key=lambda q: math.hypot(q[0] - seat["cx"], q[1] - seat["cy"]))  # center-out, as every proposer here
            # FILL BEFORE YOU GROW (settlement-review, feature 227): a seat the front row could not take leaves a HOLE
            # in the row, and the ranks - proposed behind the houses that did stand - carry the hole backward through
            # the whole cluster. Inashiro shipped a 211 px gap in its row and read as three pieces (components
            # [10, 4, 1] at a 165 px link) on a map whose form is nucleated. So the first rank round offers the
            # midpoints of the row's own over-wide gaps AT THE ROW'S OWN DEPTH, ahead of anything behind it.
            if attempt == 0:
                _cands = [((p[0] + q[0]) / 2, (p[1] + q[1]) / 2) for p, q in zip(_along, _along[1:], strict=False) if math.dist(p, q) > BUNDLE_PITCH * 1.45] + _cands
        else:
            # THE RESCUE offers the along-the-field seats first - a pitch beyond each end of the standing rank, and the
            # brick's outer half-seats behind it - then the old cloud over the widened band; a quota the ranks could not
            # seat (cohort seed 25: 19 of 20 once the ends left the ordinary rounds) is seated where the ground is
            _ends = []
            _cands = []
            if _standing:
                _along = sorted(_standing, key=lambda q: (q[0] - seat["cx"]) * ax + (q[1] - seat["cy"]) * ay)
                _cands = [(_along[0][0] - ax * BUNDLE_PITCH, _along[0][1] - ay * BUNDLE_PITCH), (_along[-1][0] + ax * BUNDLE_PITCH, _along[-1][1] + ay * BUNDLE_PITCH)]
                _cands += [
                    (_along[0][0] - ax * BUNDLE_PITCH / 2 + ox * _rank_step, _along[0][1] - ay * BUNDLE_PITCH / 2 + oy * _rank_step),
                    (_along[-1][0] + ax * BUNDLE_PITCH / 2 + ox * _rank_step, _along[-1][1] + ay * BUNDLE_PITCH / 2 + oy * _rank_step),
                ]
            want = plan.spec.households * 6 + 30
            for lx, ly in s.cluster_seeds(plan.cluster_shape, 0.0, 0.0, wlat, wdep, want, rng, record=False):
                ly = -wdep + (ly + wdep) * 0.75  # the cloud leans toward the field (feature 133)
                _cands.append((seat["cx"] + ax * lx + ox * ly, seat["cy"] + ay * lx + oy * ly))
        _before_round = placed
        # THE ENDS GO THROUGH THE SAME BODY (feature 227): they are offered only after a round that seated nothing
        # behind - the cluster grows along the field only when its back is refused - but a second loop of its own
        # meant a second copy of the dedupe and the jitter, which is how two rules drift apart.
        _offered, _along_the_field = _cands, False
        while True:
            # THE ROUND'S SEATS JITTERED, THEN OFFERED AT ONCE (feature 297, FR-001, plan B1): one region read for the list
            _jittered = [(_q[0] + ax * (s._hjit(_q[0], _q[1], 13.0) - 0.5) * BUNDLE_PITCH * 0.2, _q[1] + ay * (s._hjit(_q[0], _q[1], 13.0) - 0.5) * BUNDLE_PITCH * 0.2) for _q in _offered]
            _region = getattr(s, "_seat_region", None)
            _in = _region.offer(_jittered) if _region is not None else [True] * len(_jittered)
            for (_sx4, _sy4), _held in zip(_jittered, _in, strict=True):
                if placed >= plan.spec.households:
                    break
                if not _held:
                    continue
                # A PITCH IS A SPACING, NOT A RULING (settlement-review, feature 227: 11 of Mizuguchi's 12 houses fell in
                # one 10 px bucket of nearest-neighbor distance, where the hand-packed maps spread over three). The seat is
                # nudged along the band by up to a tenth of a pitch, from the map's own position hash - enough to break the
                # modal spike, far too little to move a rank or to reopen a gap the round above just filled.
                if not in_band((_sx4, _sy4)) and attempt >= 4:
                    continue
                if any(math.hypot(_sx4 - kx, _sy4 - ky) < BUNDLE_PITCH * (0.5 if attempt < 4 else 0.3) for kx, ky in _kept) or any(
                    math.hypot(_sx4 - h["x"], _sy4 - h["y"]) < BUNDLE_PITCH * 0.5 for h in s.M.get("houses", [])
                ):
                    continue  # the same guess again
                _kept.append((_sx4, _sy4))
                # ...AND A RANK IS NOT A SURVEYED LINE EITHER (settlement-review of Mizuguchi, feature 261): with the depth
                # exact, 11 of its 12 houses stood on four rows within 5 ft and three columns within 3 ft - a lattice, where
                # the record's nucleated village is houses gathered irregularly (kaison-jawiki) and main's roll of the same
                # map spread its rows by 24 and 78 ft. A rank seat stands up to half of `RANK_DEPTH_JITTER` of a pitch nearer
                # to or further from the field, from the same position hash; the placer still holds the lane room and the sun
                # corridor, and the exact seat is offered where the jittered one is refused, so no household is lost to it.
                # (Outward only was tried first: the last rank stands against the band's outer edge, the placer's computed move
                # pulled every jittered seat back to that one line, and Mizuguchi's back rank stood within 3 ft again.)
                # ...ONLY WHERE THE VILLAGE GREW BY ACCRETION. The record gives two forms and rolls between them per map
                # (research/contents.json#ways "How our maps draw village lanes"): a back lane implies PLANNING - the framework laid
                # out at once and the plots regular - and alleys off a spine imply ACCRETION, each household cutting its own way,
                # the result irregular. So the ranks of a `back_lane` hamlet stay regular and an `alleys` hamlet's are taken off
                # the line. (Jittering every form was tried first: each amplitude re-laid all five maps into a new draw, and 0.15,
                # 0.18 and 0.25 each tipped Inashiro's rolled crescent under round's ceiling - a knob that moves which map fails.)
                _dj = (s._hjit(_sx4, _sy4, 14.0) - 0.5) * BUNDLE_PITCH * RANK_DEPTH_JITTER if attempt < 4 and not _along_the_field and plan.lane_web == "alleys" else 0.0
                for _tx, _ty in ((_sx4 + ox * _dj, _sy4 + oy * _dj), (_sx4, _sy4)) if _dj != 0.0 else ((_sx4, _sy4),):
                    if _pretest(_tx, _ty) and s.try_place(_tx, _ty, "plain"):
                        placed += 1
                        _cloud_placed += 1
                        break
            if _along_the_field or not (attempt < 4 and _standing and placed == _before_round and placed < plan.spec.households):
                break
            _offered, _along_the_field = _ends, True
    # THE EXHAUSTIVE PASS (feature 287, homes H14): while the quota is short, every free point of the legal ground within
    # the field's reach, a third of a pitch apart, is offered to the same placer - cohort seed 32 seated 13 of 14 when the
    # rounds above alone decided.
    if not _rows_seated:  # ...but never behind a row village's rows (FR-016): its next margin is tried instead
        placed = seat_the_rest(s, plan, placed)
    return placed, _cloud_placed


# ---- STAGE 6: what stands among the houses ------------------------------------------------------


def stage_appurtenances(s: Settlement, plan: SitePlan) -> None:
    """Yards, gardens, byres, wells, sheds.

    The rest of each steading, plus the shared fixtures. Kept as its own stage after the houses because several
    of them are sited RELATIVE to a house that must already exist - a threshing yard south of its own farmhouse,
    a byre off the frontage, a well between steadings.

    Communal wells and shared draft byres, dropped into the courtyards the homesteads left.

    AFTER the houses (they slot into the gaps the final layout produced, which is a thing only the
    finished layout knows) and BEFORE the grove (whose canopy then skips them). Both are sized off
    the houses that actually landed, not off the declared household count: a byre is roughly one per
    four or five households, and the wells cover the cluster's real extent.

    Steps:
        l7r.diagram.hamletgen.homesteads.wells.place_wells
        l7r.diagram.settlement.Settlement.draft_byres
        l7r.diagram.hamletgen.homesteads.fixtures.farmstead_fixtures
        l7r.diagram.hamletgen.homesteads.retirement.retirement_houses
    """
    houses = s.M.get("houses", [])
    place_wells(s, plan, houses)
    s.draft_byres(fraction=COMMONS_BYRE_FRACTION, gap=COMMONS_BYRE_GAP)
    farmstead_fixtures(s, plan, houses, early=True)  # the fixtures the seating laid in each bundle (homes H32), before the web
    retirement_houses(s, plan)  # after the byres, so the draft team keeps the seats it always had (269 B42)
