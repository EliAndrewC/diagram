"""Split from hamletgen/homesteads.py by feature 173 - see this package's CLAUDE.md for the index.

Research: well arithmetic - NONE: distances, scores and ground tests; the units that decide carry their own claims
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from typing import Any

from l7r.diagram.settlement import Settlement, point_in_poly, seg_dist, surface_water_dist
from l7r.diagram.settlement.homestead_parts.wood_share import ReservedSeats, well_keepout
from l7r.diagram.settlement.shrines_wells.wells import WELL_AMONG_DWELLINGS_PX, well_gap_to_dwellings

from ..consts import Pt
from ..plan import SitePlan
from .holds import release_held

_WELL_DRAWN_R = 12.376
"""The wellhead's DRAWN half-extent, used when asking how far a candidate seat would push the crop: the glyph's own `vr`
(`Settlement._well_vr`, the well-house roof's half-size, 12.376 ft on a to-scale map - the hamlet's 1 ft per px), not the
`r` clearance radius, because the frame follows the ink. `drawn_r` asks the glyph; this is its value where the
settlement is a stand-in that draws no well (feature 328: it was a separate 12, with a docstring saying 16 px across).

Research: wellhead drawn extent - CONVENTION: the glyph's 12.376 ft roof half-size, a marker larger than life (0196)
"""


def drawn_r(s: Any) -> float:
    """The wellhead's drawn half-extent on `s`: its glyph's `vr`, or `_WELL_DRAWN_R` on a stand-in with no glyph.

    Research: wellhead drawn extent - NONE: reads the glyph's `vr`, or the stand-in value
    """
    return float(s._well_vr()) if hasattr(s, "_well_vr") else _WELL_DRAWN_R


# THE AMONG-THE-DWELLINGS RULE lives with the wellhead (`settlement/shrines_wells/wells.py`: `WELL_AMONG_DWELLINGS_PX`,
# `well_gap_to_dwellings`), moved there so the bundle's well pocket asks the same predicate (feature 287, homes H09)


def _among_dwellings(houses: Sequence[Mapping[str, Any]], x: float, y: float) -> bool:
    """Would a well at (x, y) stand among the dwellings - judged where the manifest will record it, to 0.1 px.

    Research: among the dwellings - research/questions/0196-communal-wells-ido.drawing.html: a dwelling's wall within `WELL_AMONG_DWELLINGS_PX`
    """
    return well_gap_to_dwellings(houses, round(x, 1), round(y, 1)) <= WELL_AMONG_DWELLINGS_PX


def crop_extent_added(s: Any, c: Pt, xs: Sequence[float], ys: Sequence[float]) -> float:
    """How far past the crop's predicted box a wellhead at `c` (its drawn radius included) reaches - 0 inside it
    (feature 287, homes H12). The box is `_crop_boxes`, what `crop_to_content` reads; a settlement that keeps none (a
    stand-in) is judged against the house centers' own box."""
    boxes = s._crop_boxes(city=False) if hasattr(s, "_crop_boxes") else []
    bx0, bx1 = min((b[0] for b in boxes), default=min(xs)), max((b[1] for b in boxes), default=max(xs))
    by0, by1 = min((b[2] for b in boxes), default=min(ys)), max((b[3] for b in boxes), default=max(ys))
    r = drawn_r(s)
    return max(0.0, bx0 - (c[0] - r), (c[0] + r) - bx1, by0 - (c[1] - r), (c[1] + r) - by1)


def well_target(households: int) -> int:
    """How many communal draw-wells a hamlet of this size keeps.

    One per ~6 households, but never past the two a hamlet draws: 0196's drawing page reads the 2-20 households a well
    serves at hamlet scale as "a hamlet draws one or two" (feature 328: the cap was 6, so 16-20 households drew three).

    Research: how many wells - research/questions/0196-communal-wells-ido.drawing.html: one per 6 households, one or two
    """
    return max(1, min(2, round(households / 6.0)))


def worst_after(c: tuple[float, float, float], needy: Sequence[Mapping[str, Any]], standing: Sequence[float]) -> float:
    """The walk of the household WORST served once a well is dug at `c` - the minimax objective of the greedy
    pass in `place_wells`, lifted out (feature 223). `standing[i]` is needy house i's distance to its nearest
    well already standing, computed once per sort by the caller; the house's walk after the dig is the smaller
    of that and its distance to `c`, and the seat's score is the largest such walk."""
    return max(min(sd, math.hypot(h["x"] - c[1], h["y"] - c[2])) for h, sd in zip(needy, standing, strict=True))


def own_well_clear(s: Settlement, x: float, y: float, half: float, boxes: Sequence[tuple[float, float, float, float]]) -> bool:
    """May a farm's own wellhead of drawn half-size `half` stand at (x, y)? Tested by FOOTPRINT: its box a 2 ft gap off
    every reserved box (`boxes`: the placed boxes but the farm's own frame, and the grove bands), and the engine's own
    ground tests - no water, crop or bog (`_well_ground_clear`), no scrub cover, nothing blocked. `well_at` asks `_fits`,
    whose circumscribed circle round a 150 ft grove band covered most of the farm it shelters (Kashikawa: 0 wells)."""
    if x < 55 or y < 88 or x > s.W - 55 or y > s.H - 26:
        return False
    if s._in_scrub_cover(x, y) or not s._well_ground_clear(x, y) or s._in_blocked(x, y):
        return False
    return not any(abs(x - bx) < half + bw / 2 + 2.0 and abs(y - by) < half + bh / 2 + 2.0 for bx, by, bw, bh in boxes)


WATER_REACH_FT = 760.0
"""The watering rule's reach (`surface_water_dist` against 760 ft, `place_wells` below; the gate's `WATER_REACH_FT`).

Research: watering reach - research/questions/0033-row-villages-resson.drawing.html, research/questions/0196-communal-wells-ido.drawing.html: 760 ft
"""


BEND_LOOK_FT = 40.0
"""How far along the street, either way, a shared well's mark looks for a bend (the law's zigzag run, `law.BEND_RUN_FT`).

Research: well arithmetic - GUESS: the bend rule's look-along; the 40 ft is the zigzag run of research/questions/0081-village-lanes.drawing.html
"""

BEND_WELL_DEG = 30.0
"""The street's turn, over `BEND_LOOK_FT` either way, past which no shared well is dug at a mark (feature 315): a GUESS, the
law's zigzag turn (50 degrees) less a margin, so a bend the street may yet be straightened through is left clear.

Research: well arithmetic - GUESS: no shared well where the street turns 30 degrees (a placement rule)
"""


def street_turns_at(line: Sequence[Pt], arc: Sequence[float], u: float, look: float) -> float:
    """How far, in degrees, the street `line` (its running lengths `arc`) turns on either side of the point `u` along it - the
    larger of its turn from `look` before to `u` and from `u` to `look` after. Either side alone, not end to end: a step in
    the street turns one way and back, and its two turns cancel between the far ends."""

    def heading(at: float) -> float:
        at = max(0.0, min(arc[-1], at))
        k = max(0, min(len(arc) - 2, next((j for j in range(len(arc) - 1) if arc[j + 1] >= at), len(arc) - 2)))
        a, b = line[k], line[k + 1]
        return math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))

    def between(p: float, q: float) -> float:
        turn = abs(heading(q) - heading(p)) % 360.0
        return min(turn, 360.0 - turn)

    return max(between(u - look, u), between(u, u + look))


def shared_row_wells(s: Settlement, houses: Sequence[Mapping[str, Any]], streets: Sequence[Sequence[Pt]]) -> int:
    """A row village that shares its water (`row_water` shared, feature 291 plan D18): along each street, wells beside the
    street, one at the middle of each equal stretch of the row no longer than 1.6 reaches (the watering rule's reach), so
    every farm of every row stands within reach of one. A seat is tried at each mark and a half and a quarter lot either
    way, on either side of the tread. Returns the wells seated.

    Research:
        shared wells spaced - research/questions/0033-row-villages-resson.drawing.html: one at the middle of each stretch of at most 1.6 reaches
        beside the street - research/questions/0196-communal-wells-ido.drawing.html: the lane-side form, on the verge clear of the tread, either side
        off the tread - GUESS: the wellhead's half-extent and 8 ft off the street's centerline
        no well in a street bend - GUESS: no shared well at a mark where the street turns `BEND_WELL_DEG` (30 degrees) or more within `BEND_LOOK_FT` (40 ft, the zigzag run) on either side; no page gives a bend rule for wells
        fallback seats along the street - GUESS: a seat tried at the mark, then a half and a quarter lot either way along the street; no page gives the offsets
    """
    if not streets or not houses:
        return 0
    half = s._well_vr()
    boxes = [(float(p[0]), float(p[1]), float(p[2]), float(p[3])) for p in s.placed] + [
        (float(g["x"]), float(g["y"]), float(g["w"]), float(g["h"])) for g in s.M.get("groves", []) if all(k in g for k in ("x", "y", "w", "h"))
    ]
    frame_w = max((max(float(b[2]), float(b[3])) for b in ((h.get("geom") or {}).get("bbox") for h in houses) if b), default=s.px(240.0))
    reach = s.px(WATER_REACH_FT)
    n = 0
    for line in streets:
        if len(line) < 2:
            continue
        arc = [0.0]
        for a, b in zip(line, line[1:], strict=False):
            arc.append(arc[-1] + math.dist(a, b))

        def along(p: Pt, _line: Sequence[Pt] = line, _arc: Sequence[float] = arc) -> tuple[float, float, Pt]:
            best = min(((seg_dist(p[0], p[1], a, b), i) for i, (a, b) in enumerate(zip(_line, _line[1:], strict=False))), key=lambda t: t[0])
            a, b = _line[best[1]], _line[best[1] + 1]
            seg = math.dist(a, b) or 1.0
            t = max(0.0, min(1.0, ((p[0] - a[0]) * (b[0] - a[0]) + (p[1] - a[1]) * (b[1] - a[1])) / (seg * seg)))
            q = (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
            return _arc[best[1]] + seg * t, best[0], q

        mine = sorted(((along((float(h["x"]), float(h["y"]))), h) for h in houses), key=lambda t: t[0][0])
        mine = [(u, h) for (u, d, _q), h in mine if d <= 2.0 * frame_w]
        if not mine:
            continue
        us = [u for u, _h in mine]
        # SPACED BY DISTANCE ALONG THE STREET, not by farms: a both-sided row has two farms at every step, and a stride in
        # farms dug a well at every one and a half lots (Kashikawa: 16 wells for 20 farms). The row is cut into equal
        # stretches no longer than 1.6 reaches and a well dug at each one's middle: every farm is then within 0.8 of a
        # reach of one along the street, the rest of the reach left for the lot's depth across it.
        span = us[-1] - us[0]
        stretches = max(1, math.ceil(span / (1.6 * reach)))
        for u in [us[0] + span * (j + 0.5) / stretches for j in range(stretches)]:
            for du in (0.0, frame_w / 2, -frame_w / 2, frame_w / 4, -frame_w / 4):
                uu = max(0.0, min(arc[-1], u + du))
                if street_turns_at(line, arc, uu, s.px(BEND_LOOK_FT)) >= BEND_WELL_DEG:
                    continue  # ...never in the street's bend (feature 315, cohort seed 903: a well in the inside of a step in the
                    # street held the street to its two right-angle turns, a kink on a tree lane, and the web was refused)
                k = max(0, min(len(arc) - 2, next(j for j in range(len(arc) - 1) if arc[j + 1] >= uu)))
                a, b = line[k], line[k + 1]
                seg = math.dist(a, b) or 1.0
                f = (uu - arc[k]) / seg
                p = (a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f)
                nx, ny = -(b[1] - a[1]) / seg, (b[0] - a[0]) / seg
                seated = False
                for sgn in (1.0, -1.0):
                    off = half + s.px(8.0)  # off the street's tread, beside it
                    x, y = p[0] + sgn * nx * off, p[1] + sgn * ny * off
                    if own_well_clear(s, x, y, half, boxes):
                        s.well(x, y)
                        boxes.append((x, y, 2 * half, 2 * half))
                        n += 1
                        seated = True
                        break
                if seated:
                    break
    return n


def grove_water(s: Settlement, plan: SitePlan, farms: Sequence[Mapping[str, Any]]) -> int:
    """Each grove farm's water, by its settlement's knob (feature 291 FR-018 and FR-019), from the well pocket its seating
    laid in its dooryard (`dispersed.canonical_farmstead`, feature 287's guarantee that a household is watered where it is
    seated): a row that SHARES its water digs wells beside its streets (`shared_row_wells`) and a dispersed farm on the
    CHANNEL form takes a channel into its grounds (`farm_channels`); a farm either serves releases its pocket, and every
    other farm draws its own well there. Returns the private wells drawn.

    Research:
        a row's water - research/questions/0033-row-villages-resson.drawing.html: shared wells along the streets, or a well at every farm
        a scattered farm's water - research/questions/0031-clustered-and-scattered-villages-shuson-sanson.drawing.html: a channel, or its own well in its dooryard pocket
    """
    streets = getattr(s, "_row_streets", None) or []
    served: list[Mapping[str, Any]] = []
    if plan.settlement_form == "linear" and plan.row_water == "shared" and streets:
        shared_row_wells(s, farms, streets)
        reach = s.px(WATER_REACH_FT)
        shared = [(float(w["x"]), float(w["y"])) for w in s.M.get("wells") or [] if not w.get("private")]
        served = [h for h in farms if any(math.dist((float(h["x"]), float(h["y"])), q) <= reach for q in shared)]
    elif plan.settlement_form == "dispersed" and plan.farm_water == "channel":
        from .farm_water import farm_channels  # local: it reads the ways' routing, a later layer

        dry = farm_channels(s, farms)
        served = [h for h in farms if h not in dry]
    s.M["meta"]["row_water_drawn"] = plan.row_water if plan.settlement_form == "linear" else None
    s.M["meta"]["farm_water_drawn"] = plan.farm_water if plan.settlement_form == "dispersed" else None
    n = 0
    for h in farms:
        pocket = h.get("well_pocket")
        if not pocket:
            continue
        release_held(s, "wells", float(pocket[0]), float(pocket[1]))
        if h not in served:
            s.well(float(pocket[0]), float(pocket[1]), private=True)
            n += 1
    return n


def place_wells(s: Settlement, plan: SitePlan, houses: Sequence[Mapping[str, Any]]) -> int:
    """Seat the communal wells INSIDE the house cloud, not on a box around it.

    The engine's `place_wells` sweeps a grid over a bbox, which is right for a town's street blocks
    and wrong for a loose farm cluster: the bbox corners are open ground, so a well lands past the
    outermost homestead and, being a hard crop feature with a 16 px extent, drags the map's frame
    out after it and leaves a band of empty scrub on that side
    (`crop_not_held_open_by_one_feature`). Insetting the bbox was tried first and is not the fix -
    it starves an elongated cluster of wells entirely, because the inset box no longer holds a grid
    cell (`settlement_has_wells`, seed 3).

    The well pockets the seating laid in the households' bundles are drawn first (feature 287, homes H10), and a grove
    farm takes its own water; the communal wells beyond them are seated here. Their seats are derived from the HOUSES: a
    candidate must have several homesteads around it and none too far, which is what "among the dwellings" means, and
    the innermost candidates are tried first. `well_at` gives the engine's own verdict on each - it refuses a seat on a lane, a crop, a
    footprint or too near another well - so nothing here restates a placement rule.

    Research:
        wells among the houses - research/questions/0196-communal-wells-ido.drawing.html: seats with a dwelling near and a neighborhood round them, the first innermost, each later one serving the worst-served household
        well pockets drawn first - research/questions/0196-communal-wells-ido.drawing.html, research/questions/0028-the-farmstead-and-what-stood-on-it-yashiki.drawing.html: each household's pocket drawn as a well
        surface water counts - research/questions/0196-communal-wells-ido.drawing.html: a house within 760 ft (over the map's ft per px) of surface water needs no well
        not in the windbreak - research/questions/0072-shelter-belts-on-a-villages-windward-side-bofurin.drawing.html: belt seats sorted last, never refused
        neighborhood ladder - research/questions/0196-communal-wells-ido.drawing.html: the third-nearest house within 190, 300, 520 px, then two houses
        wells apart - UNRESEARCHED: 170 px between wells
        no well past the crop - research/questions/0196-communal-wells-ido.drawing.html: every well stands among the houses it serves; refused where the wellhead would widen the crop
        grove farms take their own water - research/questions/0196-communal-wells-ido.drawing.html, research/questions/0031-clustered-and-scattered-villages-shuson-sanson.drawing.html: a dispersed farm draws from its own channel or well, not the shared-well rule of towns, so every grove farm takes its own water (`grove_water`) and is left out of the communal wells
        no well over a household's wood floor - UNRESEARCHED: no well seated over a household's reserved wood-floor seats
    """
    grove_farms = [h for h in houses if (h.get("geom") or {}).get("groves")]
    if grove_farms:
        grove_water(s, plan, grove_farms)
        houses = [h for h in houses if h not in grove_farms]  # the communal wells serve the rest, if any
        if not houses:
            return len(s.M.get("wells", []))
    xs = [h["x"] for h in houses]
    ys = [h["y"] for h in houses]
    ccx, ccy = sum(xs) / len(xs), sum(ys) / len(ys)
    want = well_target(plan.spec.households)
    placed: list[Pt] = []
    # THE POCKETS FIRST (feature 287, homes H10 and H11): each household the seating gave a well pocket (`well_pocket`)
    # has its wellhead's ground reserved inside its own homestead, before its yard - drawn there as a well, with no seat to
    # seek. The lattice below adds the rest of `well_target`, held off every pocket as off every well.
    for h in houses:
        if h.get("well_pocket"):
            wx, wy = float(h["well_pocket"][0]), float(h["well_pocket"][1])
            release_held(s, "wells", wx, wy)  # held since the seating, so the track kept off it (`hold_laid_parts`)
            s.well(wx, wy)
            placed.append((wx, wy))
    # A WELLHEAD MAY NOT STAND IN THE SHELTER BELT (settlement-review, Inashiro 2026-08-18). The
    # belt is drawn later, but `village_grove` SKIPS any clump whose canopy would reach a wellhead
    # (`wells_clear_of_trees` - a well lost under the grove reads wrong), so a well seated inside
    # the belt's footprint silently deletes the clumps around it. Measured on Inashiro after the
    # tie-break change moved a well to (1098,1387), inside the belt's own footprint: the 40 ft band
    # at y1360-1400 went from 8 clumps to 1, and the belt acquired its first zero-canopy latitude in
    # a 930 ft run - a hole straight through the WINDWARD side, which is the entire point of a
    # windbreak. Nothing caught it: the belt's continuity is not gated, and the well checks are all
    # about the well.
    #
    # The belt is DERIVED from the houses, which already stand, so the prospective footprint can be
    # asked for now - the same expression `stage_woodland` will call, so the two cannot disagree.
    # This is a PREFERENCE and not a veto, per this function's standing rule that a settlement with
    # a badly-placed well beats one with no well: it sorts belt seats last, so one is taken only
    # when nothing outside the belt serves at all. It also happens to push wells toward the
    # dooryards, which is where the idiom 井戸端会議 puts them.
    from ..hinterland import belt_polygon  # local: hinterland is a later stage, module-level would invert the pipeline's reading order

    _belt = belt_polygon(s, plan)

    def _in_belt(c: tuple[float, float, float]) -> int:
        return 1 if _belt and point_in_poly(c[1], c[2], _belt) else 0

    # THE MINIMAX SERVES THE HOUSES THAT NEED A WELL (known-open ledger 2026-08-16): the
    # worst-served objective used to count every house, including those
    # `settlement_dwellings_watered` already treats as watered by a nearby stream / channel /
    # pond (Kashikawa's SW pocket, 77-182 ft from the stream head - the GM-settled "no redundant
    # well beside a living stream" case), so the objective and the check read two definitions of
    # "needs a well". `surface_water_dist` is the check's own predicate; a house within its
    # reach of surface water drops out of the objective and out of the rescue pass below. If
    # EVERY house is surface-watered the objective falls back to all of them - wells are still
    # dug (well_target), they just stop chasing houses the water already serves.
    _sw_reach = 760.0 / max(plan.ftpx, 0.01)
    needy = [h for h in houses if surface_water_dist(s.M, h["x"], h["y"]) > _sw_reach] or list(houses)
    # A RELAXATION LADDER, not a single rule. The tight neighborhood test is right for a compact
    # cluster and impossible for a stretched one: an `elongated` cluster strung along a margin has
    # no point with three homesteads inside 190 px, so the strict pass found nothing at all and the
    # map shipped with no well (seeds 3 and 12). A settlement WITHOUT a well is a much worse map
    # than one whose well sits a little wide, so the test loosens until it finds seats. It never
    # loosens into "anywhere": every seat still has to be nearer a house than the crop.
    # Only the THIRD-nearest distance relaxes - the "is this in a neighborhood" test. The gap to the
    # NEAREST house never relaxes: every rung holds it to `well_gap_to_dwellings` <= 95 px, the rule's
    # own predicate (feature 287, FR-003 - the rungs used to ask a house CENTER within 105-112 px, which
    # admitted a wall 99 px off). A well 220 px from its closest farmhouse is standing in the fields by
    # any measure, and relaxing that rung traded one failure for another.
    # The last rung also serves a PAIR. Every rung above asks for three homesteads around a seat,
    # which is the right shape for a nucleus and leaves a two-farm satellite with no well of its own
    # - and then the coverage pass cannot rescue it either, because the ground among two farms is
    # their own courtyards. Seed 18 stranded exactly that: a pair 500 px off the cluster, 760 and
    # 777 px from the nearest well, with all 118 legal-neighborhood probes around them refused.
    # Two households sharing a draw-well is an ordinary thing; three is not a threshold nature knows.
    reach_r = max((math.hypot(h["w"], h["h"]) / 2 for h in houses), default=0.0)  # the prefilter's widest house
    # ...AND NO WELL OVER A HOUSEHOLD'S SHARE OF THE WOOD FLOOR (feature 287, woods W25): the copse keeps its clumps off a
    # wellhead, so a well seated among the reserved seats would take the ground the household's floor stands on
    _wood = ReservedSeats(houses)
    _well_r = well_keepout(s) if _wood.grid.n else 0.0  # nothing reserved (a settlement seated without shares): nothing held
    # ONE WELL INDEX FOR THE WHOLE LADDER (dev/performance.md, `frozen_terrain`): a well laid here moves no water and no crop,
    # and each `well_at` built the water, dry-plot and wet-ring grids again for its one seat (cohort seed 44: 71 builds);
    # the scope asserts on exit that the terrain it froze is the terrain that stands
    with s.frozen_terrain():
        for third, want_near in ((190.0, 3), (300.0, 3), (520.0, 3), (520.0, 2)):
            if len(placed) >= want:
                break
            seats: list[tuple[float, float, float]] = []
            step = 22.0
            # THE SWEEP BOX IS THE HOMESTEADS', NOT THE HOUSE CENTERS' (2026-08-15, cohort seed 44).
            # A bundle's courtyard ground extends ~a house-length past its house CENTER, so a cluster
            # strung along its field margin can keep every legal well pocket just OUTSIDE the centers'
            # bbox - seed 44 had 84 legal seats, nearly all north-west of min(xs)/min(ys), and the
            # unpadded grid visited none of them (0 of 1440 probes passed; the map shipped well-less).
            # The pad only restores ground the bundles themselves cover: every rung still demands a
            # dwelling's wall within 95 px, so an open-field corner of the padded box is rejected exactly
            # as the docstring above promises.
            pad = 120.0
            y = min(ys) - pad
            while y <= max(ys) + pad:
                x = min(xs) - pad
                while x <= max(xs) + pad:
                    near = sorted(math.hypot(x - h["x"], y - h["y"]) for h in houses)
                    # the center distance PREFILTERS (a wall is never nearer than its center less the half-diagonal); the
                    # rule's own predicate decides
                    if (
                        len(near) >= want_near
                        and near[want_near - 1] <= third
                        and near[0] <= WELL_AMONG_DWELLINGS_PX + reach_r
                        and _among_dwellings(houses, x, y)
                        and not _wood.disc_covers(x, y, _well_r)
                    ):
                        seats.append((math.hypot(x - ccx, y - ccy), x, y))
                    x += step
                y += step
            # GREEDY COVERAGE, not central-first throughout (settlement-review, Mizuguchi/Sawada
            # 2026-08-15): sorting every well toward the centroid put both of Mizuguchi's wells in one
            # lobe of a two-lobed cluster - the six eastern households walked 248-424 ft while the west
            # had a well within 63. The FIRST well is central (innermost legal seat, as before); every
            # LATER well takes the legal seat FARTHEST from the wells already standing, ties toward the
            # center - i.e. it serves the households the placed wells do not, which is why a real hamlet
            # digs a second well at all.
            pool = sorted(seats, key=lambda c: (_in_belt(c), c[0]))  # the FIRST well is central too, but never in the belt if anywhere else will do
            # RE-SORTED ONLY WHEN A WELL HAS LANDED (feature 278, FR-004). The key reads the wells placed and the crop boxes, and
            # inside this loop only a well that lands changes either - so a pass that popped a seat and placed nothing left a
            # list already sorted by the key it would be sorted by again (Kuwabata: 168 sorts, 72,324 key evaluations, the
            # most of its 1.8 s appurtenance stage). The house-distance part of the key never reads the wells, so it is
            # computed once per seat.
            _sorted_at = -1
            _near_of: dict[tuple[float, float, float], float] = {}
            while pool and len(placed) < want:
                if placed and len(placed) != _sorted_at:
                    # ...by MINIMAX NEED, in ~3-grid-step buckets, centrality breaking ties inside a
                    # bucket. Two failed rankings led here, and both are worth remembering. Strict
                    # farthest-first (the 2026-08-15 greedy-coverage fix) let a seat 91 px OUTSIDE the
                    # cluster beat an interior seat covering the same households - the exterior well
                    # held Sawada's whole frame open (crop_not_held_open_by_one_feature). Bucketing
                    # that same farthest-first score fixed the frame and re-broke coverage the other
                    # way: on Mizuguchi the spread rung walked EAST past the last house into scrub
                    # while the one under-served household stood at the WEST end (settlement-review
                    # 2026-08-16). Both fail because "far from the standing wells" is a proxy for the
                    # real quantity, which is the walk of the household WORST served after the well is
                    # dug - so score that directly: pick the seat minimizing the farthest any house
                    # would remain from its nearest well. A seat past the row's end cannot beat an
                    # in-row seat (it serves nobody the row seat does not), and a seat in an unserved
                    # lobe wins outright, which is what the greedy fix was for in the first place.
                    # ONCE PER SORT, ONCE PER CANDIDATE (feature 223, GM 2026-09-11: "the wells key"). The standing wells do
                    # not change while the pool is sorted, so each needy house's walk to its nearest standing well is
                    # taken once here, and the key tuple below is built once per candidate - it used to call
                    # `_worst_after` and `_extent_added` twice each per candidate and re-derive every house's walk to every
                    # standing well inside each call (70,416 calls, 1.2 million terms on Kuwabata). Same numbers, same
                    # order: `worst_after` is the lifted body, held to the nested form by its test.
                    _standing = [min(math.hypot(h["x"] - wx, h["y"] - wy) for wx, wy in placed) for h in needy]

                    def _worst_after(c: tuple[float, float, float], standing: Sequence[float] = _standing) -> float:
                        return worst_after(c, needy, standing)

                    # AND AN INTERIOR SEAT BEATS A PADDED ONE THAT SERVES THE SAME HOUSEHOLDS. The sweep
                    # box above is padded 120 px past the house CENTERS because a bundle's courtyard
                    # really does reach that far, and without the pad seed 44 shipped well-less. But the
                    # pad is symmetric, so it equally offers seats BEYOND the outermost homestead on
                    # every side - and a wellhead is a hard crop feature with a 16 px extent, so one
                    # seated out there drags the map's frame after it and leaves a band of empty scrub
                    # (`crop_not_held_open_by_one_feature`). The RESCUE pass below already refuses
                    # exactly that, with its `min(xs) <= x <= max(xs)` test and a comment giving this
                    # very reason; the greedy pass did not - two passes carrying two definitions of
                    # "inside the house cloud", with the looser one running first.
                    #
                    # MEASURED on cohort seed 41: the second well won its minimax bucket on the strength
                    # of one north-east household, then seated 76 px NORTH of that household and 66 px
                    # past every other feature on the map. The minimax objective is right and is not
                    # what moved here - the tie-break was, because distance-to-centroid cannot express
                    # "this seat is outside the settlement".
                    #
                    # SO IT IS A TIE-BREAK AHEAD OF CENTRALITY, NOT A FILTER. The padded ground stays in
                    # the pool and still wins when nothing inside the cloud serves the same households,
                    # which is what the pad was added for; it simply can no longer outrank an interior
                    # seat that does. Same shape as every other rule in this function: relax rather than
                    # forbid, because a settlement with a badly-placed well beats one with no well.
                    # OUTSIDE WHAT, EXACTLY - the CROP's own box, not a box round the house CENTERS. The
                    # first version of this tie-break tested `min(xs)..max(xs)`, an AABB of house centers,
                    # and settlement-review (Inashiro 2026-08-17) named the flaw before it bit: an AABB
                    # cannot tell "in the settlement" from "in the box", so on a two-lobed cluster the
                    # ~345 px of grove and scrub BETWEEN the lobes scores as interior, exactly like a
                    # courtyard. Cohort seed 29 then did bite - a well 64 px north of every other feature,
                    # inside the centers' box and holding the whole frame open.
                    #
                    # `_crop_boxes` is what `crop_to_content` itself reads, so asking it is asking the
                    # question the check will ask: a seat inside the box the crop will set cannot hold the
                    # frame open, whatever its relation to the house centers. Same-source doctrine, and it
                    # picks up the houses' DRAWN extents plus their yards, gardens, sheds and byres rather
                    # than a point per house. (The box can only GROW later - the woodland and the pond are
                    # placed after - so this is conservative in the safe direction.)
                    _cb = s._crop_boxes(city=False)
                    _bx0 = min((b[0] for b in _cb), default=min(xs))
                    _bx1 = max((b[1] for b in _cb), default=max(xs))
                    _by0 = min((b[2] for b in _cb), default=min(ys))
                    _by1 = max((b[3] for b in _cb), default=max(ys))

                    # A TIE-BREAK CANNOT REACH A SEAT WITH NO RIVAL IN ITS BUCKET, so the FRAME goes into
                    # the score itself. Ranking outside-ness ahead of centrality fixed cohort seed 29 and
                    # left seed 7 failing for the reason a tie-break always leaves one: its pad seat was
                    # alone in its minimax bucket, so there was nothing to break the tie against. Seed 7's
                    # well sits 25 px past the northernmost byre and holds the whole frame open
                    # (`crop_not_held_open_by_one_feature`), because a wellhead is a hard crop feature with
                    # a 16 px extent and the crop follows it out.
                    #
                    # THE EXCHANGE RATE IS 1:1 IN PIXELS, which is what makes this a rule rather than a
                    # knob: a seat that drags the frame out by N px must save at least N px of the
                    # worst-served household's walk to be worth it. Both quantities are distances in the
                    # same units, so no weighting has to be invented - and the well that genuinely serves
                    # an outlying lobe still wins, because the coverage it buys is real.
                    def _extent_added(c: tuple[float, float, float], bx0: float = _bx0, bx1: float = _bx1, by0: float = _by0, by1: float = _by1) -> float:
                        """How far past the crop's predicted box this seat (drawn radius included) reaches."""
                        r = drawn_r(s)
                        return max(0.0, bx0 - (c[1] - r), (c[1] + r) - bx1, by0 - (c[2] - r), (c[2] + r) - by1)

                    # ...AND THE LAST TIE-BREAK IS THE NEIGHBORHOOD, NOT THE CENTROID (settlement-review,
                    # Sawada 2026-08-18). Once the minimax bucket and the frame term are equal, the
                    # remaining sort was `c[0]` - the seat's distance to the cluster CENTROID, computed
                    # when the pool was built. On a ONE-lobed cluster that reads as "the most central
                    # seat wins" and is fine. On a TWO-lobed one the centroid is the empty ground
                    # BETWEEN the lobes, so the tie-break actively prefers the gap: Sawada's second well
                    # moved off a seat serving 11 households within 300 ft onto one serving 5, and the
                    # worst walk went 364 -> 493 ft. Same family as the `_extent_added` fix above and as
                    # the standing rule against letting an aggregate stand in for the distributed thing
                    # a verdict is about - a centroid is not a place anybody lives.
                    #
                    # The measure that IS the question: how tightly is this seat surrounded by
                    # homesteads - the distance to the `want_near`-th nearest house, which is exactly
                    # the rung's own "is this in a neighborhood" test, reused rather than restated.
                    # Distance to the SINGLE nearest house was the ledger's sketch and is rejected: it
                    # is minimized by hugging one outlying farmhouse, which is the same mistake in the
                    # other direction. Every seat in the pool already passed the rung, so this only
                    # orders seats that are all legally "among the dwellings".
                    def _neighborhood(c: tuple[float, float, float], wn: int = want_near, memo: dict[tuple[float, float, float], float] = _near_of) -> float:
                        if c not in memo:
                            memo[c] = sorted(math.hypot(c[1] - h["x"], c[2] - h["y"]) for h in houses)[wn - 1]
                        return memo[c]

                    # THE BELT TERM SITS BEHIND COVERAGE, not in front of it. Ranked first it is a
                    # filter, and it behaved like every other filter this function has tried: Mizuguchi's
                    # second well moved off a seat inside the belt and its worst walk went 203 -> 264 ft,
                    # on a map whose belt hole turned out not to be well-caused at all, so the trade
                    # bought nothing. Behind the minimax bucket it can only decide between seats that
                    # serve the households equally well - which is all "do not stand in the windbreak"
                    # was ever entitled to decide.
                    def _key(c: tuple[float, float, float]) -> tuple[float, int, float, float, float]:
                        _w, _e = _worst_after(c), _extent_added(c)
                        return ((_w + _e) // 66.0, _in_belt(c), _e, _w, _neighborhood(c))

                    pool.sort(key=_key)
                    _sorted_at = len(placed)
                _, x, y = pool.pop(0)
                if any(math.hypot(x - px, y - py) < 170.0 for px, py in placed):
                    continue  # `wells_not_clustered`: shared wells serve separate courtyards
                if crop_extent_added(s, (x, y), xs, ys) > 0.0:
                    # NO WELL HOLDS THE CROP OPEN (feature 287, homes H12): the frame term was a score because a padded seat was
                    # sometimes the only way to water a household; the pockets water every one now, so a lattice well that
                    # reaches past the box the crop will set is refused, not drawn
                    continue
                if s.well_at(x, y):
                    placed.append((x, y))
    # NO RESCUE AND NO LAST RESORT (feature 287, homes H10-H12). A ring probe spiraled out from each dry household and
    # `open_seat` was asked when the lattice found nothing; both are gone, because what they rescued is carried by
    # construction now: every household seated is within `WATER_REACH_FT` of a well pocket or of open water
    # (`needs_pocket`), and the first always carries one - so no house is left dry and no settlement wellless, and no
    # well is drawn outside its among-the-dwellings floor or past the crop to rescue one.
    return len(placed)
