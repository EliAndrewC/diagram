"""THE WELLS THE LANES WAIT FOR (`stage_lane_wells`) and the water reach they hold (split from `homesteads/wells.py` at the
1,000-line bar, feature 444 T33).

Research: well arithmetic - NONE: distances, scores and ground tests; the units that decide carry their own claims
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from typing import Any

from l7r.diagram.settlement import Settlement
from l7r.diagram.settlement.shrines_wells.wells import WELL_AMONG_DWELLINGS_PX
from l7r.diagram.settlement.shrines_wells.wells import well_gap_to_dwellings as well_gap_to_dwellings  # re-exported: the tests ask it here

from ...plan import SitePlan
from .core import (
    THREE_THEN_TWO,
    WATER_REACH_FT,
    WELL_SERVES_MAX,
    most_served_after,
    watered_by_open_water,
)
from .seating import (
    lane_stage_cluster,
    on_a_verge,
    seat_wells,
)


def stage_lane_wells(s: Settlement, plan: SitePlan) -> None:
    """THE WELLS THE LANES WAIT FOR (feature 374 wave 154): once the web stands, the communal wells still owed - the
    lane-side form's, or the cluster form's that found no seat - are seated: on a lane's verge (unless the lane-side form
    was tried), then among five houses (unless the cluster form was), then by the old three-then-two ladder at the 95 ft
    check, each such well marked `fallback` and counted (`meta.well_fallback`) - a recorded deviation, never silent.

    Steps:
        l7r.diagram.hamletgen.homesteads.wells.lane_and_fallback_wells
        l7r.diagram.hamletgen.homesteads.wells.reach_wells
        l7r.diagram.hamletgen.homesteads.wells.record_over_ten

    Research:
        lane-side wells after the lanes - research/questions/0196-communal-wells-ido.drawing.html: the lane-side form on a lane verge, clear of the tread, within reach of the houses
        the other form only after the reach widened - research/questions/0196-communal-wells-ido.drawing.html: both forms the research's
        the old ladder a recorded deviation - DEVIATION research/questions/0196-communal-wells-ido.drawing.html: three, then two houses at the 95 ft check, marked `fallback`, past both forms"""
    owed = getattr(s, "_wells_owed", None)
    if not owed:
        return
    s._well_memo = {}  # type: ignore[attr-defined]  # the belt and the seat sweeps, kept while only wells are added (`seat_wells`)
    try:
        lane_and_fallback_wells(s, plan, owed)
        reach_wells(s, plan)
    finally:
        s._well_memo = None  # type: ignore[attr-defined]
        record_over_ten(s)


def dry_households(s: Settlement, houses: Sequence[Mapping[str, Any]]) -> list[Mapping[str, Any]]:
    """The households beyond `WATER_REACH_FT` of every communal well and of open water (`surface_water_dist`, the measure
    the seat search and the gate's watered rule read).

    Research: every household watered - research/questions/0196-communal-wells-ido.drawing.html: a well, channel, pond or stream within 760 ft"""
    reach = s.px(WATER_REACH_FT)
    ws = [(float(w["x"]), float(w["y"])) for w in s.M.get("wells") or [] if not w.get("private") and not w.get("shrine")]
    near_water = watered_by_open_water(s, houses, reach)
    return [h for h, wet in zip(houses, near_water, strict=True) if not any(math.hypot(float(h["x"]) - x, float(h["y"]) - y) <= reach for x, y in ws) and not wet]


def reach_wells(s: Settlement, plan: SitePlan) -> None:
    """THE WATER REACH HELD BY THE WELLS (feature 374 wave 155, row 787): the guarantee the first household's well pocket
    carried by construction - every household within `WATER_REACH_FT` of a well or open water - is held here, once the forms
    have seated what `well_target` owes. While a household is dry, one more shared well is seated: the rolled form first, then
    the other, then the recorded fallback, each ranking the seat that best serves the worst-served household. A well beyond
    `well_target` is counted (`meta.wells_for_reach`), and a household still dry past all three (`meta.dry_households`).
    ...AND THE CEILING OF TEN (feature 374 wave 155, W155-6): while a well is nearest to more than `WELL_SERVES_MAX`
    households, one more shared well is seated the same way (`meta.wells_for_ten` counts those) - a clustered hamlet's
    homesteads stand edge to edge, and with no pocket no seat among a full share's houses may be open; a third well for
    sixteen households is one to five, within the record's one to 2-20 for a hamlet (0196).

    Research:
        a well for every household beyond reach - research/questions/0196-communal-wells-ido.drawing.html: every household within 760 ft of a well or open water, one more shared well where the houses spread past the hamlet's one or two
        one more well where one serves more than ten - research/questions/0196-communal-wells-ido.drawing.html: the five to ten houses a Karihama well served, a hamlet's wells as many as one to 2-20 households
        the forms' order - research/questions/0196-communal-wells-ido.drawing.html: the rolled siting first, the other form, then the fallback (`lane_and_fallback_wells`)
        its search steps and tolerances - GUESS: no source could speak to it, a value of ours (feature 417 T38 pass N3, 2026-10-25) - 11 (lattice step)
    """
    houses = [h for h in s.M.get("houses") or [] if not (h.get("geom") or {}).get("groves") and h.get("kind") != "abandoned"]
    added = over = 0
    last = len(houses) + 1
    for _ in range(len(houses)):
        placed = [(float(w["x"]), float(w["y"])) for w in s.M.get("wells") or [] if not w.get("private") and not w.get("shrine")]
        most = most_served_after((0.0, placed[-1][0], placed[-1][1]), houses, placed[:-1]) if placed else 0
        busy = most > WELL_SERVES_MAX and most < last  # a well that left the busiest count where it was is not tried again
        if not dry_households(s, houses) and not busy:
            break
        last, over = most, over + int(busy)
        want = len(placed) + 1
        for form in (plan.well_siting, "cluster" if plan.well_siting == "lane" else "lane"):
            if len(placed) < want:
                if form == "lane":
                    seat_wells(s, plan, houses, placed, want, THREE_THEN_TWO, "lane", seat_ok=on_a_verge(s), step=11.0)
                else:
                    lane_stage_cluster(s, plan, houses, placed, want)
        if len(placed) < want:
            if not seat_wells(s, plan, houses, placed, want, THREE_THEN_TWO, "fallback", gap=WELL_AMONG_DWELLINGS_PX):
                break
            s.M["meta"]["well_fallback"] = int(s.M["meta"].get("well_fallback", 0)) + 1
        added += 1
    if added - over:
        s.M["meta"]["wells_for_reach"] = added - over
    if over:
        s.M["meta"]["wells_for_ten"] = over
    dry = dry_households(s, houses)
    if dry:
        s.M["meta"]["dry_households"] = len(dry)


def record_over_ten(s: Settlement) -> None:
    """A communal well nearest to more than `WELL_SERVES_MAX` households, recorded (`meta.wells_over_ten`: each such well's
    count) - a recorded deviation, never silent: the seat search ranks a seat that keeps every well at ten first, and where
    none does the well stands and is counted.

    Research: more than ten to a well, recorded - DEVIATION research/questions/0196-communal-wells-ido.drawing.html: the well serving more than ten stands where no seat keeps every well to ten, marked on the map's record"""
    ws = [(float(w["x"]), float(w["y"])) for w in s.M.get("wells") or [] if not w.get("private") and not w.get("shrine")]
    houses = [h for h in s.M.get("houses") or [] if not (h.get("geom") or {}).get("groves") and h.get("kind") != "abandoned"]
    if not ws or not houses:
        return
    count = [0] * len(ws)
    for h in houses:
        count[min(range(len(ws)), key=lambda i: math.hypot(float(h["x"]) - ws[i][0], float(h["y"]) - ws[i][1]))] += 1
    over = [c for c in count if c > WELL_SERVES_MAX]
    if over:
        s.M["meta"]["wells_over_ten"] = over


def lane_and_fallback_wells(s: Settlement, plan: SitePlan, owed: tuple[int, Sequence[str]]) -> None:
    """The wells still owed once the lanes stand: the lane-side form, the cluster form, then the recorded fallback.

    Research:
        the order of the forms - research/questions/0196-communal-wells-ido.drawing.html: the lane-side form on a verge once the lanes stand, the other form where no verge has room
        the fallback - DEVIATION research/questions/0196-communal-wells-ido.drawing.html: among three houses, then two, at the 95 ft, where neither form finds a seat, marked `fallback`
        its search steps and tolerances - GUESS: no source could speak to it, a value of ours (feature 417 T38 pass N3, 2026-10-25) - 11 (lattice step)
    """
    want, tried = owed
    houses = [h for h in s.M.get("houses") or [] if not (h.get("geom") or {}).get("groves")]
    placed = [(float(w["x"]), float(w["y"])) for w in s.M.get("wells") or [] if not w.get("private") and not w.get("shrine")]
    if len(placed) >= want or not houses:
        return
    if "lane" not in tried:
        # the lattice at 11 px, half its step elsewhere: the verge test admits a band only `WELL_VERGE_FT` wide beside each
        # lane, which a 22 px lattice steps over rather than samples - the same ground offered, never a tighter fit
        # (hour:374-match-the-research-continued@3 ruled the step and the seat gap fixed: make room, never pack)
        seat_wells(s, plan, houses, placed, want, THREE_THEN_TWO, "lane", seat_ok=on_a_verge(s), step=11.0)
    if len(placed) < want and "cluster" not in tried:
        lane_stage_cluster(s, plan, houses, placed, want)
    if len(placed) < want:
        n = len(seat_wells(s, plan, houses, placed, want, THREE_THEN_TWO, "fallback", gap=WELL_AMONG_DWELLINGS_PX))
        s.M["meta"]["well_fallback"] = int(s.M["meta"].get("well_fallback", 0)) + n
