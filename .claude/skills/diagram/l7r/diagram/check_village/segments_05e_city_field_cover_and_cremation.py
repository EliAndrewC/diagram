"""Town, city and capital segments moved out of `segments_05a_field_cover_and_cremation.py` by feature 145.

The GM ruled on 2026-08-28 that the hamlet path owes 100% coverage and the other tiers owe none while
nothing exercises them - and the floor is MODULE level, so a city segment sharing a file with a hamlet
segment put its whole body under the hamlet floor. Execution order is by the segment's numeric key
(`registry._ordered_names`), never by file, so moving one costs nothing and needs no placement row."""

import math
from typing import Any

from .common_01_geometry import point_in_poly, seg_dist
from .common_03_capacity import _UNBOUND, _kept


def _seg_0286_000__cems(*, M: Any = _UNBOUND, scale: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 0286.000 (cems) - body verbatim from _seg_0286__cemetery_clear_of_shrine (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale in ('village', 'town', 'city', 'capital'):
        cems = M.get("cemeteries", [])
    return _kept(locals(), ('cems',))


def _seg_0286_001__maus(*, M: Any = _UNBOUND, scale: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 0286.001 (maus) - body verbatim from _seg_0286__cemetery_clear_of_shrine (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale in ('village', 'town', 'city', 'capital'):
        maus = M.get("mausoleums", [])
    return _kept(locals(), ('maus',))


def _seg_0286_002__crem(*, M: Any = _UNBOUND, scale: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 0286.002 (crem) - body verbatim from _seg_0286__cemetery_clear_of_shrine (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale in ('village', 'town', 'city', 'capital'):
        crem = M.get("cremation_grounds", [])
    return _kept(locals(), ('crem',))


def _seg_0286_003__oss(*, M: Any = _UNBOUND, scale: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 0286.003 (oss) - body verbatim from _seg_0286__cemetery_clear_of_shrine (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale in ('village', 'town', 'city', 'capital'):
        oss = M.get("ossuaries", [])
    return _kept(locals(), ('oss',))


def _seg_0286_004__relig(*, M: Any = _UNBOUND, scale: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 0286.004 (relig) - body verbatim from _seg_0286__cemetery_clear_of_shrine (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale in ('village', 'town', 'city', 'capital'):
        relig = M.get("religious", [])
    return _kept(locals(), ('relig',))


def _seg_0286_005__r(*, r: Any = _UNBOUND, relig: Any = _UNBOUND, scale: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 0286.005 (r, shrines) - body verbatim from _seg_0286__cemetery_clear_of_shrine (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale in ('village', 'town', 'city', 'capital'):
        shrines = [r for r in relig if r.get("kind") in ("shrine", "small_shrine")]
    return _kept(locals(), ('r', 'shrines'))


def _seg_0286_006__r_1(*, r: Any = _UNBOUND, relig: Any = _UNBOUND, scale: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 0286.006 (r, temples) - body verbatim from _seg_0286__cemetery_clear_of_shrine (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale in ('village', 'town', 'city', 'capital'):
        temples = [r for r in relig if r.get("kind") in ("monastery", "temple")]
    return _kept(locals(), ('r', 'temples'))


def _seg_0286_007__wall(*, M: Any = _UNBOUND, scale: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 0286.007 (wall) - body verbatim from _seg_0286__cemetery_clear_of_shrine (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale in ('village', 'town', 'city', 'capital'):
        wall = M.get("wall")
    return _kept(locals(), ('wall',))


def _seg_0286_008___inside(*, px: Any = _UNBOUND, py: Any = _UNBOUND, scale: Any = _UNBOUND, wall: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 0286.008 (_inside) - body verbatim from _seg_0286__cemetery_clear_of_shrine (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale in ('village', 'town', 'city', 'capital'):

        def _inside(px: float, py: float) -> bool:
            return bool(wall) and point_in_poly(px, py, wall)

    return _kept(locals(), ('_inside',))


def _seg_0286_018__pond(*, M: Any = _UNBOUND, scale: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 0286.018 (pond) - body verbatim from _seg_0286__cemetery_clear_of_shrine (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale in ('village', 'town', 'city', 'capital'):
        pond = M.get("pond")
    return _kept(locals(), ('pond',))


def _seg_0286_024__cremation_ground_by_external_cemetery(
    *,
    M: Any = _UNBOUND,
    ROAD_SETBACK: Any = _UNBOUND,
    _edge_gap: Any = _UNBOUND,
    _rdist: Any = _UNBOUND,
    a: Any = _UNBOUND,
    b: Any = _UNBOUND,
    between: Any = _UNBOUND,
    c: Any = _UNBOUND,
    cems: Any = _UNBOUND,
    check: Any = _UNBOUND,
    cr: Any = _UNBOUND,
    crem: Any = _UNBOUND,
    crem_on_road: Any = _UNBOUND,
    ext_cems: Any = _UNBOUND,
    gx: Any = _UNBOUND,
    gy: Any = _UNBOUND,
    k: Any = _UNBOUND,
    lonely: Any = _UNBOUND,
    mainroad: Any = _UNBOUND,
    near_t: Any = _UNBOUND,
    scale: Any = _UNBOUND,
    t: Any = _UNBOUND,
    temples_r: Any = _UNBOUND,
    wall: Any = _UNBOUND,
    x: Any = _UNBOUND,
    y: Any = _UNBOUND,
) -> dict[str, Any]:
    """Gate segment 0286.024 (cremation_ground_by_external_cemetery, cremation_ground_not_between_temple_and_road, cremation_ground_set_back_from_main_road) - body verbatim from _seg_0286__cemetery_clear_of_shrine (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale in ('village', 'town', 'city', 'capital') and crem:
        ext_cems = [c for c in cems if not (wall and point_in_poly(c["x"], c["y"], wall))]

        def _edge_gap(a: dict[str, Any], b: dict[str, Any]) -> float:
            gx = max(0.0, abs(a["x"] - b["x"]) - (a["w"] + b["w"]) / 2)
            gy = max(0.0, abs(a["y"] - b["y"]) - (a["h"] + b["h"]) / 2)
            return math.hypot(gx, gy)

        lonely = [(round(cr["x"]), round(cr["y"])) for cr in crem if not any(_edge_gap(cr, c) <= 70 for c in ext_cems)]
        pass  # `` retired under feature 141 (the GM's cut); the segment stays for the check it keeps or the value it writes

        # SET BACK FROM THE MAIN ROAD: the crematory is marginal, polluting land reached by a minor
        # funeral path, NOT the high street - so it keeps clear of the Imperial / trunk road (town
        # streets and minor lanes don't count; only the main road). The temple's own parish graveyard
        # may sit by the temple wherever it is, but the smoking pyre stays off the main thoroughfare.
        ROAD_SETBACK = 130
        mainroad = M.get("road")
        if mainroad:

            def _rdist(x: float, y: float) -> float:
                return min(seg_dist(x, y, mainroad[k], mainroad[k + 1]) for k in range(len(mainroad) - 1))

            crem_on_road = [(round(cr["x"]), round(cr["y"])) for cr in crem if _rdist(cr["x"], cr["y"]) < ROAD_SETBACK]
            pass  # `` retired under feature 141 (the GM's cut); the segment stays for the check it keeps or the value it writes
            # NOT BETWEEN its temple and the road: you should not walk past the pyre to reach the
            # monastery. The crematory sits BEHIND or beside its nearest temple (at least as far from
            # the road as that temple, less a small tolerance), never on the road-side approach to it.
            # (The temple's own graveyard may still sit road-side by the temple - this is the pyre only.)
            temples_r = [t for t in M.get("religious", []) if t.get("kind") in ("monastery", "temple")]
            between = []
            for cr in crem:
                near_t = [t for t in temples_r if math.hypot(t["x"] - cr["x"], t["y"] - cr["y"]) <= 400]
                if near_t:
                    t = min(near_t, key=lambda t: math.hypot(t["x"] - cr["x"], t["y"] - cr["y"]))
                    if _rdist(cr["x"], cr["y"]) < _rdist(t["x"], t["y"]) - 40:
                        between.append((round(cr["x"]), round(cr["y"])))
            pass  # `` retired under feature 141 (the GM's cut); the segment stays for the check it keeps or the value it writes
    return _kept(locals(), ('ROAD_SETBACK', '_edge_gap', '_rdist', 'between', 'c', 'cr', 'crem_on_road', 'ext_cems', 'lonely', 'mainroad', 'near_t', 't', 'temples_r'))


def _seg_0286_026__walled_graveyards_inside_and_outside(
    *,
    _inside: Any = _UNBOUND,
    bi: Any = _UNBOUND,
    bo: Any = _UNBOUND,
    c: Any = _UNBOUND,
    cems: Any = _UNBOUND,
    check: Any = _UNBOUND,
    ins: Any = _UNBOUND,
    out: Any = _UNBOUND,
    scale: Any = _UNBOUND,
    wall: Any = _UNBOUND,
) -> dict[str, Any]:
    """Gate segment 0286.026 (walled_exterior_cemetery_larger, walled_graveyards_inside_and_outside) - body verbatim from _seg_0286__cemetery_clear_of_shrine (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale in ('village', 'town', 'city', 'capital') and wall and cems:
        ins = [c for c in cems if _inside(c["x"], c["y"])]
        out = [c for c in cems if not _inside(c["x"], c["y"])]
        pass  # `` retired under feature 141 (the GM's cut); the segment stays for the check it keeps or the value it writes
        if ins and out:
            bi = max(c["w"] * c["h"] for c in ins)
            bo = max(c["w"] * c["h"] for c in out)
            pass  # `` retired under feature 141 (the GM's cut); the segment stays for the check it keeps or the value it writes
    return _kept(locals(), ('bi', 'bo', 'c', 'ins', 'out'))


def _seg_0286_027__walled_settlement_has_drum_tower(
    *,
    M: Any = _UNBOUND,
    _dt_at_crossing: Any = _UNBOUND,
    _inside: Any = _UNBOUND,
    a: Any = _UNBOUND,
    angs: Any = _UNBOUND,
    b: Any = _UNBOUND,
    check: Any = _UNBOUND,
    dts: Any = _UNBOUND,
    i: Any = _UNBOUND,
    ok_dt: Any = _UNBOUND,
    scale: Any = _UNBOUND,
    st: Any = _UNBOUND,
    t: Any = _UNBOUND,
    wall: Any = _UNBOUND,
    ways: Any = _UNBOUND,
    wy: Any = _UNBOUND,
) -> dict[str, Any]:
    """Gate segment 0286.027 (walled_settlement_has_drum_tower) - body verbatim from _seg_0286__cemetery_clear_of_shrine (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale in ('village', 'town', 'city', 'capital') and wall and scale in ("town", "city"):
        dts = M.get("drum_towers", [])
        ways = ([M["road"]] if M.get("road") else []) + [st.get("pts", []) for st in M.get("town_streets", [])]

        def _dt_at_crossing(t: dict[str, Any]) -> bool:
            angs = []
            for wy in ways:
                for i in range(len(wy) - 1):
                    if seg_dist(t["x"], t["y"], wy[i], wy[i + 1]) < 80:
                        angs.append(math.atan2(wy[i + 1][1] - wy[i][1], wy[i + 1][0] - wy[i][0]) % math.pi)
            return any(min(abs(a - b), math.pi - abs(a - b)) > 0.5 for a in angs for b in angs)

        ok_dt = len(dts) == 1 and _inside(dts[0]["x"], dts[0]["y"]) and _dt_at_crossing(dts[0])
        pass  # `` retired under feature 141 (the GM's cut); the segment stays for the check it keeps or the value it writes
    return _kept(locals(), ('_dt_at_crossing', 'angs', 'dts', 'ok_dt', 'st', 'ways'))


def _seg_0286_029__city_temples_have_graveyards(
    *,
    M: Any = _UNBOUND,
    URBAN: Any = _UNBOUND,
    _inside: Any = _UNBOUND,
    anchor: Any = _UNBOUND,
    b: Any = _UNBOUND,
    c: Any = _UNBOUND,
    cems: Any = _UNBOUND,
    check: Any = _UNBOUND,
    crem: Any = _UNBOUND,
    crem_out: Any = _UNBOUND,
    gov: Any = _UNBOUND,
    m2: Any = _UNBOUND,
    maus: Any = _UNBOUND,
    maus_ok: Any = _UNBOUND,
    needy: Any = _UNBOUND,
    o: Any = _UNBOUND,
    oss: Any = _UNBOUND,
    oss_ok: Any = _UNBOUND,
    r: Any = _UNBOUND,
    sam: Any = _UNBOUND,
    scale: Any = _UNBOUND,
    temples: Any = _UNBOUND,
    unserved: Any = _UNBOUND,
) -> dict[str, Any]:
    """Gate segment 0286.029 (city_has_cremation_ground, city_has_mausoleum, city_has_ossuary, city_temples_have_graveyards) - body verbatim from _seg_0286__cemetery_clear_of_shrine (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale in ('village', 'town', 'city', 'capital') and URBAN:
        # every temple that CAN host a graveyard has one in its precinct (graveyard=False opts out)
        needy = [r for r in temples if r.get("graveyard", True)]
        unserved = [r.get("label", (round(r["x"]), round(r["y"]))) for r in needy if not any(math.hypot(c["x"] - r["x"], c["y"] - r["y"]) < 230 for c in cems)]
        pass  # `` retired under feature 141 (the GM's cut); the segment stays for the check it keeps or the value it writes
        # CLAN MAUSOLEUM: a walled crypt precinct inside the walls, by the samurai/government quarter
        gov = M.get("governor_mansion")
        sam = [b for b in M.get("buildings", []) if b.get("kind") in ("samurai", "samurai_large")]
        if gov:
            anchor = (gov["x"], gov["y"])
        elif sam:
            anchor = (sum(b["x"] for b in sam) / len(sam), sum(b["y"] for b in sam) / len(sam))
        else:
            anchor = None
        maus_ok = bool(maus) and any(_inside(m2["x"], m2["y"]) for m2 in maus) and (anchor is None or any(math.hypot(m2["x"] - anchor[0], m2["y"] - anchor[1]) < 640 for m2 in maus))
        pass  # `` retired under feature 141 (the GM's cut); the segment stays for the check it keeps or the value it writes
        # CREMATION GROUND: smoke, fire, and pollution push the crematory OUTSIDE the walls
        crem_out = [c for c in crem if not _inside(c["x"], c["y"])]
        pass  # `` retired under feature 141 (the GM's cut); the segment stays for the check it keeps or the value it writes
        # PAUPER OSSUARY: outside the walls, beside the cremation ground
        oss_ok = any(not _inside(o["x"], o["y"]) and any(math.hypot(o["x"] - c["x"], o["y"] - c["y"]) < 320 for c in crem) for o in oss)
        pass  # `` retired under feature 141 (the GM's cut); the segment stays for the check it keeps or the value it writes
    return _kept(locals(), ('anchor', 'b', 'c', 'crem_out', 'gov', 'm2', 'maus_ok', 'needy', 'o', 'oss_ok', 'r', 'sam', 'unserved'))
