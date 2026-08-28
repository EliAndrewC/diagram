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
