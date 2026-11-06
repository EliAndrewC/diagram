"""The communal wells this stage seats - the cluster form among the houses, the lane-side form beside the track - and the lattice
search `stage_lane_wells` keeps until its phase (split from `homesteads/wells.py` at the 1,000-line bar, feature 444 T33).

Research: well arithmetic - NONE: distances, scores and ground tests; the units that decide carry their own claims
"""

from __future__ import annotations

import math
from collections.abc import Callable, Mapping, Sequence
from typing import Any

from l7r.diagram.settlement import Settlement, seg_dist
from l7r.diagram.settlement._geom.indexes import PointGrid
from l7r.diagram.settlement._geom.primitives import points_in_poly, seg_dists
from l7r.diagram.settlement.homestead_parts.wood_share import ReservedSeats, well_keepout
from l7r.diagram.settlement.shrines_wells.wells import well_gap_to_dwellings as well_gap_to_dwellings  # re-exported: the tests ask it here
from l7r.diagram.work_counts import OPS

from ...consts import WELL_VERGE_FT, Pt
from ...plan import SitePlan
from ..well_seats import PairAhead, PoolScore, SeatSweep, SeatTest, cells, discs_cover
from .core import (
    THREE_THEN_TWO,
    WELL_SEAT_FT,
    WELL_SERVES_MAX,
    crop_box,
    drawn_r,
    extent_past,
    first_share_middle,
    grid_points,
    grove_water,
    mark_form,
    watered_by_open_water,
    well_target,
)

PAIR_LOOK = 40
"""How many of the seats nearest the first share's middle the first well's look ahead ranks (feature 374 wave 155): a
bound on the pairs it measures, the nearest 40 of a rung's few hundred seats.

Research: the look ahead's bound - GUESS: no source could speak to it, an algorithm's breadth of ours (feature 427 T06, 2026-10-26); the 40 seats nearest the first share's middle are the only ones re-ranked by whether a second well keeps both at ten, so it moves which seat the first of two wells takes"""


def place_wells(s: Settlement, plan: SitePlan, houses: Sequence[Mapping[str, Any]]) -> int:
    """Seat the communal wells INSIDE the house cloud, not on a box around it.

    The engine's `place_wells` sweeps a grid over a bbox, which is right for a town's street blocks
    and wrong for a loose farm cluster: the bbox corners are open ground, so a well lands past the
    outermost homestead and, being a hard crop feature with a 16 px extent, drags the map's frame
    out after it and leaves a band of empty scrub on that side
    (`crop_not_held_open_by_one_feature`). Insetting the bbox was tried first and is not the fix -
    it starves an elongated cluster of wells entirely, because the inset box no longer holds a grid
    cell (`settlement_has_wells`, seed 3).

    A grove farm takes its own water; the communal wells are ALL seated by the hamlet's rolled `well_siting` (feature 374
    waves 154 and 155): the cluster form here (`seat_cluster`), among the houses before the lanes; the lane-side form once
    the lanes stand (`stage_lane_wells`), with the wells the water reach still owes (`reach_wells`). `seat_wells` carries the
    seat search and `well_at` the engine's own verdict on each seat.

    Research:
        no well in a household's homestead - research/questions/0028-the-farmstead-and-what-stood-on-it-yashiki.drawing.html, research/questions/0196-communal-wells-ido.drawing.html: the well shared off the farmstead, by the lane or among the houses, never a pocket inside one household's homestead
        grove farms take their own water - research/questions/0196-communal-wells-ido.drawing.html, research/questions/0031-clustered-and-scattered-villages-shuson-sanson.drawing.html: a dispersed farm draws from its own channel or well, not the shared-well rule of towns, so every grove farm takes its own water (`grove_water`) and is left out of the communal wells
        the wells' siting rolled - research/questions/0196-communal-wells-ido.drawing.html: by the lane or among the houses, a knob; the cluster form seated before the lanes, the lane-side form tried beside the track first and seated on a lane's verge once the lanes stand
        its search steps and tolerances - GUESS: no source could speak to it, a value of ours (feature 417 T38 pass N3, 2026-10-25) - 11 (lattice step, lane-side seats)
    """
    grove_farms = [h for h in houses if (h.get("geom") or {}).get("groves")]
    if grove_farms:
        grove_water(s, plan, grove_farms)
        houses = [h for h in houses if h not in grove_farms]  # the communal wells serve the rest, if any
        if not houses:
            return len(s.M.get("wells", []))
    want = well_target(plan.spec.households)
    placed: list[Pt] = []
    # NO WELL POCKET IN A CLUSTERED HAMLET'S HOMESTEADS (feature 374 wave 155, row 787): the seating laid the first household
    # a well inside its own homestead, before its yard, and this drew it there - where 0028 draws "the well, shared off the
    # farmstead". Every well `well_target` owes is now a shared well of the rolled siting, and the water reach the pocket
    # carried by construction is held by the wells once the lanes stand (`reach_wells`). No ring probe and no `open_seat`
    # rescue (feature 287, homes H10-H12): no well is drawn outside its among-the-dwellings floor or past the crop to rescue one.
    # THE ROLLED SITING (feature 374 wave 154, 0196's knob): the cluster form is seated now, among the houses before the lanes
    # are laid; the lane-side form waits for the lanes (`stage_lane_wells`), as do any wells the cluster form could not seat
    s.M.setdefault("meta", {})["well_siting"] = plan.well_siting
    if plan.well_siting == "cluster":
        seat_cluster(s, plan, houses, placed, want)
    else:
        # ...the lane-side form first beside the way already laid - the track out, through the open ground at the cluster's
        # gateway, a wayside well (0196) - since the web's lanes run between the homesteads, where a verge is a yard or a
        # bed (measured on the 44 rolls: no lane-side seat beside a web lane ever cleared them)
        track = next(([(float(q[0]), float(q[1])) for q in ln["pts"]] for ln in s.M.get("lanes") or [] if ln.get("connector")), [])
        if track:
            seats_in_rust(s, plan, houses, placed, want, THREE_THEN_TWO, "lane", on_a_verge(s), track=track)
    s._wells_owed = (want, ("cluster",) if plan.well_siting == "cluster" else ())  # type: ignore[attr-defined]
    return len(placed)


def seats_in_rust(
    s: Settlement, plan: SitePlan, houses: Sequence[Mapping[str, Any]], placed: list[Pt], want: int, rungs: Sequence[tuple[float, int]], form: str, seat_ok: SeatTest, track: Sequence[Pt] | None = None
) -> list[Pt]:
    """The communal wells seated from the Rust's seats (feature 444 T33 D5, D7a): the households a well owes cut into its groups,
    each group's seats ranked in Rust (`l7r_phases.well_seats`: the gaps between its houses, or given `track` the track's verges),
    each asked here in that order - `seat_ok`, off the reserved wood floor, inside the crop's box, 170 px off a standing well, and
    the engine's own verdict (`well_at`) - the first admitted drawn, one a group, until `placed` holds `want`. Returns the seats drawn.

    Research:
        wells among the houses - research/questions/0196-communal-wells-ido.drawing.html: seats with a dwelling near and a neighborhood round them, the households cut into the wells' groups
        seated a little closer than the check - GUESS research/questions/0196-communal-wells-ido.drawing.html: a dwelling's wall within `WELL_SEAT_FT` (80 ft, a GUESS the page names), the 95 ft check unchanged
        surface water counts - research/questions/0196-communal-wells-ido.drawing.html: a house within 760 ft (over the map's ft per px) of surface water owes no well
        wells apart - GUESS: searched, the record silent (feature 417 T29 pass C, 2026-10-25); 170 px between wells
        no well past the crop - research/questions/0196-communal-wells-ido.drawing.html: every well stands among the houses it serves; refused where the wellhead would widen the crop
        no well over a household's wood floor - GUESS: no source could speak to it, a value of ours (feature 417 T29 pass C, 2026-10-25); no well seated over a household's reserved wood-floor seats
        lane-side seats off the tread - research/questions/0196-communal-wells-ido.drawing.html: on a lane's verge, the curb within `WELL_VERGE_FT` of the tread, at the verge's middle
        its salts, guards and sentinels - NONE: they decide nothing about the place - 0.01 (divide-by-zero guard); 11 (the verge's step, px)
    """
    from ...phases_ext import phases
    from ...ways.track import CONNECTOR_WIDTH

    new: list[Pt] = []
    if not houses or len(placed) >= want:
        return new
    reach = 760.0 / max(plan.ftpx, 0.01)
    needy = [not wet for wet in watered_by_open_water(s, houses, reach)]
    vr = drawn_r(s)
    got = phases().well_seats(
        {
            "houses": [(float(h["x"]), float(h["y"]), float(h["w"]), float(h["h"]), float(h.get("rot", 0.0))) for h in houses],
            "needy": needy,
            "want": want - len(placed),
            "rungs": [(float(a), int(b)) for a, b in rungs],
            "gap": WELL_SEAT_FT / max(plan.ftpx, 0.01),
            "track": [(float(q[0]), float(q[1])) for q in track] if track else None,
            "verge": (s.px(CONNECTOR_WIDTH) / 2.0 + vr + s.px(WELL_VERGE_FT) / 2.0, 11.0),
        }
    )
    for k, n in got["counts"].items():  # the Rust's counted work on the stage's (feature 444 D5)
        OPS[k] += n
    wood = ReservedSeats(houses)
    keep = well_keepout(s) if wood.grid.n else 0.0
    pts = [(float(q[0]), float(q[1])) for q in wood.pts]
    xs, ys = [float(h["x"]) for h in houses], [float(h["y"]) for h in houses]
    box = None
    with s.frozen_terrain():
        for seats in got["groups"]:
            if len(placed) >= want:
                break
            for x, y in seats:
                OPS["candidate@well_seats"] += 1
                if not seat_ok(x, y) or any(math.dist((x, y), q) < keep for q in pts) or any(math.dist((x, y), q) < 170.0 for q in placed):
                    continue
                if box is None or box[0] != len(placed):  # the crop's box moves only when a well lands (feature 387)
                    box = (len(placed), crop_box(s, xs, ys))
                if extent_past(box[1], vr, (x, y)) > 0.0:
                    continue
                if s.well_at(x, y):
                    mark_form(s, x, y, form)
                    placed.append((x, y))
                    new.append((x, y))
                    break
    return new


def stage_kept(s: Settlement, key: Any, make: Callable[[], Any]) -> Any:
    """What `make` builds, kept under `key` while `stage_lane_wells` holds its memo (only wells are added inside it); built
    afresh outside it (feature 427 T05).

    Research: plumbing - NONE: a cache, deciding nothing about the place"""
    memo: dict[Any, Any] | None = getattr(s, "_well_memo", None)
    if memo is None:
        return make()
    if key not in memo:
        memo[key] = make()
    return memo[key]


def seat_wells(
    s: Settlement,
    plan: SitePlan,
    houses: Sequence[Mapping[str, Any]],
    placed: list[Pt],
    want: int,
    rungs: Sequence[tuple[float, int]],
    form: str,
    gap: float = 0.0,
    seat_ok: SeatTest | None = None,
    candidates: Sequence[Pt] | None = None,
    step: float = 22.0,
) -> list[Pt]:
    """Seat communal wells among `houses` until `placed` holds `want`: the neighborhood ladder `rungs` - (third, want_near):
    the `want_near`-th nearest house within `third` px - over the lattice (or `candidates`), each seat with a dwelling's wall
    within `gap` (`WELL_SEAT_FT` by default), passing `seat_ok`, ranked by the worst-served household's walk with no well
    serving more than `WELL_SERVES_MAX` households where a seat avoids it, and the engine's `well_at` verdict. Each well it
    draws records its `form`. Returns the seats drawn. (Lifted out of `place_wells`, feature 374 wave 154.)

    Research:
        wells among the houses - research/questions/0196-communal-wells-ido.drawing.html: seats with a dwelling near and a neighborhood round them, each later one serving the worst-served household
        the first well's seat - GUESS: the innermost seat where one well is owed; where two or more are, the middle of its own share of the houses, the shares cut along the cluster's long axis (`first_share_middle`)
        seated a little closer than the check - GUESS research/questions/0196-communal-wells-ido.drawing.html: a dwelling's wall within `WELL_SEAT_FT` (80 ft, a GUESS the page names), the 95 ft check unchanged
        no well serving more than ten - research/questions/0196-communal-wells-ido.drawing.html: the five to ten houses each dug well served at Karihama; a seat that keeps every well at ten or fewer ranked first
        not in the windbreak - research/questions/0072-shelter-belts-on-a-villages-windward-side-bofurin.drawing.html: belt seats sorted last, never refused
        surface water counts - research/questions/0196-communal-wells-ido.drawing.html: a house within 760 ft (over the map's ft per px) of surface water needs no well
        wells apart - GUESS: searched, the record silent (feature 417 T29 pass C, 2026-10-25); 170 px between wells
        no well past the crop - research/questions/0196-communal-wells-ido.drawing.html: every well stands among the houses it serves; refused where the wellhead would widen the crop
        no well over a household's wood floor - GUESS: no source could speak to it, a value of ours (feature 417 T29 pass C, 2026-10-25); no well seated over a household's reserved wood-floor seats
        later wells by the worst walk - GUESS: no source could speak to it, a value of ours (feature 417 T29 pass C, 2026-10-25); ranked by the worst-served household's walk after the dig, in 66 px buckets, the crop's overreach added 1:1
        ties among later wells - GUESS: no source could speak to it, an algorithm's order, breadth or tolerance of ours (feature 417 T29 pass E, judged by the session from the code, 2026-10-25); the belt, then the crop's overreach, then the exact worst walk, then the want_near-th nearest house
        its search steps and tolerances - GUESS: no source could speak to it, a value of ours (feature 417 T38 pass N3, 2026-10-25) - 22 (default lattice step); 120 (sweep box pad)
        its salts, guards and sentinels - NONE: they decide nothing about the place - 0.01 (divide-by-zero guard)
    """
    new: list[Pt] = []
    if not houses or len(placed) >= want:
        return new
    gap = gap or WELL_SEAT_FT / max(plan.ftpx, 0.01)
    seat_ok = seat_ok or ANYWHERE
    xs = [h["x"] for h in houses]
    ys = [h["y"] for h in houses]
    ccx, ccy = sum(xs) / len(xs), sum(ys) / len(ys)
    served = list(houses)
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
    from ...hinterland import belt_polygon  # local: hinterland is a later stage, module-level would invert the pipeline's reading order

    # ...ONCE A STAGE WHERE THE STAGE HOLDS A MEMO (feature 427 T05): inside `stage_lane_wells` only wells are added, and the belt
    # reads the houses, the lanes and the crop - eight calls rebuilt the same polygon on a 40-household roll
    memo: dict[Any, Any] | None = getattr(s, "_well_memo", None)
    _belt = stage_kept(s, "belt", lambda: belt_polygon(s, plan))

    # ...each seat asked once for the stage, every seat of a pool in one array (feature 435 T06): the belt stands still while wells land
    _belt_of: dict[tuple[float, float], int] = stage_kept(s, "belt_of", dict)

    def _belt_all(seats: Sequence[tuple[float, float, float]]) -> None:
        new = [(c[1], c[2]) for c in seats if (c[1], c[2]) not in _belt_of]
        for xy, inside in zip(new, points_in_poly(new, _belt) if _belt and new else [False] * len(new), strict=True):
            _belt_of[xy] = int(inside)

    def _in_belt(c: tuple[float, float, float]) -> int:
        """Asked once per seat, not once per sort (feature 427 T05, D5): every seat of a rung is asked by `_belt_all` first."""
        return _belt_of[(c[1], c[2])]

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
    needy = [h for h, wet in zip(houses, watered_by_open_water(s, houses, _sw_reach), strict=True) if not wet] or list(houses)
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
    sweep: SeatSweep | None = None
    # ...AND A SEAT `well_at` REFUSED IS NOT ASKED AGAIN BY A LATER RUNG (feature 427 T05): the terrain is frozen and inside this
    # call (and inside `stage_lane_wells`, whose memo keeps the set) only a well that lands changes what stands, which can add a refusal and never lift one (seed 25 at 40 households
    # asked 21,093 times, most of them seats an earlier rung had already been refused)
    _refused: set[tuple[float, float]] = memo.setdefault("refused", set()) if memo is not None else set()

    # `seat_ok` and the wood floor, neither reading the wells placed (feature 427 T05), ASKED OF THE LATTICE AS ARRAYS AND KEPT ON
    # THE SWEEP (feature 435 T06): every seat a rung reaches asked at once, each verdict read by every later rung and call
    _centers = None

    def _many(P: Any) -> Any:
        nonlocal _centers
        import numpy as np

        if _centers is None:
            _centers = np.asarray(_wood.pts, dtype=float).reshape(-1, 2)
        return np.asarray(seat_ok.many(P), dtype=bool) & ~discs_cover(P, _centers, _well_r)

    many = ((seat_ok.key, _well_r), _many)

    with s.frozen_terrain():
        for third, want_near in rungs:
            if len(placed) >= want:
                break
            seats: list[tuple[float, float, float]] = []
            # THE SWEEP BOX IS THE HOMESTEADS', NOT THE HOUSE CENTERS' (2026-08-15, cohort seed 44).
            # A bundle's courtyard ground extends ~a house-length past its house CENTER, so a cluster
            # strung along its field margin can keep every legal well pocket just OUTSIDE the centers'
            # bbox - seed 44 had 84 legal seats, nearly all north-west of min(xs)/min(ys), and the
            # unpadded grid visited none of them (0 of 1440 probes passed; the map shipped well-less).
            # The pad only restores ground the bundles themselves cover: every rung still demands a
            # dwelling's wall within 95 px, so an open-field corner of the padded box is rejected exactly
            # as the docstring above promises.
            pad = 120.0
            if sweep is None:  # ...ONE DISTANCE TABLE FOR EVERY RUNG (feature 387, plan D9): the lattice and the houses do not change
                # ...and for every call of the stage that asks the same lattice of the same houses at the same gap (feature 427 T05):
                # the sweep's wall gaps hold for its gap's reach, and nothing it measures moves while only wells are added
                key = ("sweep", step, gap, reach_r, tuple(candidates or ()), tuple((h["x"], h["y"], h["w"], h["h"], h.get("rot", 0.0), h.get("kind")) for h in houses))
                sweep = stage_kept(
                    s, key, lambda pad=pad: SeatSweep(list(candidates) if candidates is not None else list(grid_points(min(xs) - pad, max(xs) + pad, min(ys) - pad, max(ys) + pad, step)), houses)
                )
            seats, _near_of = sweep.seats(third, want_near, gap, reach_r, seat_ok, (ccx, ccy), many)
            _belt_all(seats)
            # GREEDY COVERAGE, not central-first throughout (settlement-review, Mizuguchi/Sawada
            # 2026-08-15): sorting every well toward the centroid put both of Mizuguchi's wells in one
            # lobe of a two-lobed cluster - the six eastern households walked 248-424 ft while the west
            # had a well within 63. The FIRST well is central (innermost legal seat, as before); every
            # LATER well takes the legal seat FARTHEST from the wells already standing, ties toward the
            # center - i.e. it serves the households the placed wells do not, which is why a real hamlet
            # digs a second well at all.
            # THE FIRST OF SEVERAL WELLS AT ITS SHARE'S MIDDLE (feature 374 wave 155): with the pocket gone, a first well at the
            # cluster's middle left the second, held 170 px off it, three or four households - the first served 12 or 13 on four
            # of the 44 rolls (m:w155-wells). Seated at the middle of its own share of the houses, the shares split along the
            # cluster's long axis, it leaves the second the other share (`first_share_middle`)
            _fx, _fy = first_share_middle(houses, want - len(placed)) if not placed and want - len(placed) >= 2 else (ccx, ccy)
            pool = sorted(seats, key=lambda c: (_in_belt(c), math.hypot(c[1] - _fx, c[2] - _fy)))  # never in the belt if anywhere else will do
            if not placed and want - len(placed) >= 2:
                # ...AND ONE STEP AHEAD: the nearest seats to the share's middle are ranked by whether the best second well
                # this rung offers, 170 px off, would leave both at ten or fewer (`well_seats.PairAhead`) - a first seat the rung's
                # ground pushed off its share left the second three or four households on three of the 44 rolls (m:w155-wells)
                ahead = PairAhead(seats, served)  # the second seats and the households, as arrays once (feature 387)
                pool[:PAIR_LOOK] = sorted(pool[:PAIR_LOOK], key=lambda c: not ahead.keeps_ten(c))
            # RE-SORTED ONLY WHEN A WELL HAS LANDED (feature 278, FR-004). The key reads the wells placed and the crop boxes, and
            # inside this loop only a well that lands changes either - so a pass that popped a seat and placed nothing left a
            # list already sorted by the key it would be sorted by again (Kuwabata: 168 sorts, 72,324 key evaluations, the
            # most of its 1.8 s appurtenance stage). The house-distance part of the key never reads the wells, so it is
            # computed once per seat.
            _sorted_at = -1
            _crop_box: tuple[int, tuple[float, float, float, float]] | None = None
            _score = PoolScore(pool, served, needy)  # the pool's seats-by-households distances, once a rung (feature 427 T05)
            while pool and len(placed) < want:
                if __debug__:
                    OPS["candidate@seat_wells"] += 1
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
                    # `_crop_boxes` is what `content_view` itself reads, so asking it is asking the
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
                    # (the overreach: how far past the crop's predicted box a seat, drawn radius included, reaches - `PoolScore`)

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
                    # (the neighborhood: the rung's own want_near-th nearest house, taken once by the sweep - `SeatSweep.seats`)

                    # THE BELT TERM SITS BEHIND COVERAGE, not in front of it. Ranked first it is a
                    # filter, and it behaved like every other filter this function has tried: Mizuguchi's
                    # second well moved off a seat inside the belt and its worst walk went 203 -> 264 ft,
                    # on a map whose belt hole turned out not to be well-caused at all, so the trade
                    # bought nothing. Behind the minimax bucket it can only decide between seats that
                    # serve the households equally well - which is all "do not stand in the windbreak"
                    # was ever entitled to decide.
                    # ...THE KEY ABOVE, FOR THE WHOLE POOL AT ONCE (feature 427 T05, D5): `_worst_after`, `_extent_added`,
                    # `most_served_after` and `_neighborhood` per seat walked every household against every standing well -
                    # 2.19M inner calls at 40 households (the T01 survey); `PoolScore` computes the same key in array
                    # operations, the one-seat forms kept as its reference (`tests/hamletgen/homesteads/test_pool_score.py`)
                    _keys = _score.keys(pool, placed, _standing, (_bx0, _bx1, _by0, _by1), drawn_r(s), _in_belt, _near_of, WELL_SERVES_MAX, 66.0)  # the worst walk's bucket, in px (the claim above)
                    _order = sorted(range(len(pool)), key=_keys.__getitem__)
                    pool[:] = [pool[i] for i in _order]
                    _sorted_at = len(placed)
                _, x, y = pool.pop(0)
                if any(math.hypot(x - px, y - py) < 170.0 for px, py in placed):
                    continue  # `wells_not_clustered`: shared wells serve separate courtyards
                if _crop_box is None or _crop_box[0] != len(placed):  # the crop's box moves only when a well lands (feature 387)
                    _crop_box = (len(placed), crop_box(s, xs, ys))
                if extent_past(_crop_box[1], drawn_r(s), (x, y)) > 0.0:
                    # NO WELL HOLDS THE CROP OPEN (feature 287, homes H12): the frame term was a score because a padded seat was
                    # sometimes the only way to water a household; a lattice well that reaches past the box the crop will set
                    # is refused, not drawn, and the reach is held by `reach_wells` (feature 374 wave 155)
                    continue
                if (x, y) in _refused:
                    continue
                if s.well_at(x, y):
                    mark_form(s, x, y, form)
                    placed.append((x, y))
                    new.append((x, y))
                else:
                    _refused.add((x, y))
    return new


def seat_cluster(s: Settlement, plan: SitePlan, houses: Sequence[Mapping[str, Any]], placed: list[Pt], want: int) -> list[Pt]:
    """The cluster form (feature 374 wave 154): wells in the open ground among five houses, the neighborhood's reach widened
    (190, 300, 520 px, then 0196's 760 ft) before the count gives way; three, then two, only where fewer than five households
    need the communal wells. Returns the seats drawn.

    Research:
        among five to ten houses - research/questions/0196-communal-wells-ido.drawing.html: the cluster form in the open ground among five to ten houses, off every lane
        the reach widens first - GUESS research/questions/0196-communal-wells-ido.drawing.html: how far round a seat the five may stand is this project's choice - 190, 300, 520 px, then 760 ft - widened before the count gives way
        off every lane - research/questions/0196-communal-wells-ido.drawing.html: the cluster well off every lane, its verge included (`on_a_verge`)
        three, then two, only where five cannot be gathered - research/questions/0196-communal-wells-ido.drawing.html: a household is still owed a well within reach
        its figures from 0196 - research/questions/0196-communal-wells-ido.drawing.html: 5 (fewer than five households: three, then two)
        its salts, guards and sentinels - NONE: they decide nothing about the place - 0.01 (divide-by-zero guard)
    """
    reach = max(520.0, 760.0 / max(plan.ftpx, 0.01))
    verge = on_a_verge(s)
    off_lanes = SeatTest("off-verge", lambda x, y: not verge(x, y), lambda P: ~verge.many(P))  # off every lane, its verge included (0196), where lanes stand
    rungs = ((190.0, 5), (300.0, 5), (520.0, 5), (reach, 5), *(THREE_THEN_TWO if len(houses) < 5 else ()))
    return seats_in_rust(s, plan, houses, placed, want, rungs, "cluster", off_lanes)


def lane_stage_cluster(s: Settlement, plan: SitePlan, houses: Sequence[Mapping[str, Any]], placed: list[Pt], want: int) -> list[Pt]:
    """The cluster form as `stage_lane_wells` seats it once the lanes stand - its own Python lattice search (`seat_wells`), kept
    until that stage's phase moves it to Rust (feature 444 T33 D7a). Returns the seats drawn.

    Research:
        among five to ten houses - research/questions/0196-communal-wells-ido.drawing.html: the cluster form in the open ground among five to ten houses, off every lane
        the reach widens first - GUESS research/questions/0196-communal-wells-ido.drawing.html: 190, 300, 520 px, then 760 ft
        its salts, guards and sentinels - NONE: they decide nothing about the place - 0.01 (divide-by-zero guard)
    """
    reach = max(520.0, 760.0 / max(plan.ftpx, 0.01))
    verge = on_a_verge(s)
    off_lanes = SeatTest("off-verge", lambda x, y: not verge(x, y), lambda P: ~verge.many(P))
    new = seat_wells(s, plan, houses, placed, want, ((190.0, 5), (300.0, 5), (520.0, 5), (reach, 5)), "cluster", seat_ok=off_lanes)
    if len(placed) < want and len(houses) < 5:
        new += seat_wells(s, plan, houses, placed, want, THREE_THEN_TWO, "cluster", seat_ok=off_lanes)
    return new


def _anywhere_many(P: Any) -> Any:
    import numpy as np

    return np.ones(len(P), dtype=bool)


ANYWHERE = SeatTest("anywhere", lambda _x, _y: True, _anywhere_many)
"""Research: plumbing - NONE: the seat test of a form that sets none"""


def on_a_verge(s: Settlement) -> SeatTest:
    """The lane-side form's seat test: the wellhead's curb within `WELL_VERGE_FT` of a lane's tread - its center no farther
    from the tread's edge than the wellhead's half-extent and the verge (a curb ON the tread is `well_at`'s to refuse).

    Research: a lane-side well's seat - research/questions/0196-communal-wells-ido.drawing.html: on a lane's verge, clear of the tread, its curb within `WELL_VERGE_FT`"""
    # the lanes standing and the households' ways the seating reserved (`access_corridors`), drawn as lanes later: a cluster well
    # seated before the web keeps their verges too (feature 374 wave 154: two cohort wells stood on an access way's verge)
    memo: dict[Any, Any] | None = getattr(s, "_well_memo", None)
    if memo is not None and "verge" in memo:
        return memo["verge"]  # the lanes stand still while `stage_lane_wells` adds wells: one test, its answers kept (feature 427 T05)
    M = getattr(s, "M", None) or {}
    lanes = [([(float(p[0]), float(p[1])) for p in ln["pts"]], float(ln.get("w", 3.0)) / 2) for ln in [*(M.get("lanes") or []), *(M.get("access_corridors") or [])] if len(ln.get("pts") or []) >= 2]
    reach = s._well_vr() + s.px(WELL_VERGE_FT) if lanes else 0.0
    # ...EACH LEG FILED ONCE, its box padded by its half-width and the reach (feature 387): a seat asks the legs near it, not every
    # leg of every lane (the lattice at 11 px asked them all, seat by seat)
    entries = [
        (a, b, half, min(a[0], b[0]) - half - reach, min(a[1], b[1]) - half - reach, max(a[0], b[0]) + half + reach, max(a[1], b[1]) + half + reach)
        for pts, half in lanes
        for a, b in zip(pts, pts[1:], strict=False)
    ]
    legs = PointGrid()
    legs.extend(entries)

    asked: dict[tuple[float, float], bool] = {}

    def ok(x: float, y: float) -> bool:
        if (x, y) not in asked:
            asked[(x, y)] = any(seg_dist(x, y, a, b) - half <= reach for a, b, half, *_ in legs.near(x, y, 0.0))
        return asked[(x, y)]

    def many(P: Any) -> Any:
        """`ok` for every seat of `P` at once (feature 435 T06): each cell's seats against the legs whose padded box meets it."""
        import numpy as np

        out = np.zeros(len(P), dtype=bool)
        if not entries:
            return out
        box = np.asarray([e[3:] for e in entries], dtype=float)
        halves = np.asarray([e[2] for e in entries], dtype=float)
        for rows in cells(P):
            B = P[rows]
            (x0, y0), (x1, y1) = B.min(axis=0), B.max(axis=0)
            near = np.nonzero((box[:, 0] <= x1) & (box[:, 2] >= x0) & (box[:, 1] <= y1) & (box[:, 3] >= y0))[0]
            if len(near):
                out[rows] = ((seg_dists(B, [(entries[i][0], entries[i][1]) for i in near]) - halves[near][None, :]) <= reach).any(axis=1)
        return out

    test = SeatTest("verge", ok, many)
    if memo is not None:
        memo["verge"] = test
    return test
