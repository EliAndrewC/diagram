"""Town, city and capital segments moved out of `segments_01b_quarters_and_civic_reserve.py` by feature 145.

The GM ruled on 2026-08-28 that the hamlet path owes 100% coverage and the other tiers owe none while
nothing exercises them - and the floor is MODULE level, so a city segment sharing a file with a hamlet
segment put its whole body under the hamlet floor. Execution order is by the segment's numeric key
(`registry._ordered_names`), never by file, so moving one costs nothing and needs no placement row."""

from typing import Any

from l7r.diagram.overlap.taxonomy import (
    point_in_poly,
    sweep_hi,
)
from .common_03_capacity import (
    _UNBOUND,
    _kept,
)


def _seg_0040_000__wall_p(*, M: Any = _UNBOUND, scale: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 0040.000 (wall_p) - body verbatim from _seg_0040__city_commoner_dwellings_inside_walls (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale in ('city', 'capital') and M.get('wall'):
        wall_p = M["wall"]
    return _kept(locals(), ('wall_p',))


def _seg_0040_007__quarters(*, M: Any = _UNBOUND, scale: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 0040.007 (quarters) - body verbatim from _seg_0040__city_commoner_dwellings_inside_walls (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale in ('city', 'capital') and M.get('wall'):
        quarters = M.get("quarters", [])
    return _kept(locals(), ('quarters',))


def _seg_0040_018__p(*, M: Any = _UNBOUND, p: Any = _UNBOUND, q: Any = _UNBOUND, quarters: Any = _UNBOUND, scale: Any = _UNBOUND, v: Any = _UNBOUND, wall_p: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 0040.018 (p, q, v, wxs) - body verbatim from _seg_0040__city_commoner_dwellings_inside_walls (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale in ('city', 'capital') and M.get('wall') and quarters:
        wxs = [p[0] for p in wall_p] + [v[0] for q in quarters for v in q["poly"]]
    return _kept(locals(), ('p', 'q', 'v', 'wxs'))


def _seg_0040_019__p_1(*, M: Any = _UNBOUND, p: Any = _UNBOUND, q: Any = _UNBOUND, quarters: Any = _UNBOUND, scale: Any = _UNBOUND, v: Any = _UNBOUND, wall_p: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 0040.019 (p, q, v, wys) - body verbatim from _seg_0040__city_commoner_dwellings_inside_walls (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale in ('city', 'capital') and M.get('wall') and quarters:
        wys = [p[1] for p in wall_p] + [v[1] for q in quarters for v in q["poly"]]
    return _kept(locals(), ('p', 'q', 'v', 'wys'))


def _seg_0040_020__interior_cells(*, M: Any = _UNBOUND, quarters: Any = _UNBOUND, scale: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 0040.020 (interior_cells, overlapped, spill_cells, uncovered) - body verbatim from _seg_0040__city_commoner_dwellings_inside_walls (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale in ('city', 'capital') and M.get('wall') and quarters:
        interior_cells = uncovered = overlapped = spill_cells = 0
    return _kept(locals(), ('interior_cells', 'overlapped', 'spill_cells', 'uncovered'))


def _seg_0040_021___hx(*, M: Any = _UNBOUND, quarters: Any = _UNBOUND, scale: Any = _UNBOUND, wxs: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 0040.021 (_hx) - body verbatim from _seg_0040__city_commoner_dwellings_inside_walls (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale in ('city', 'capital') and M.get('wall') and quarters:
        _hx = sweep_hi(min(wxs), max(wxs), 40)  # bounded so a malformed vertex cannot hang the sweep
    return _kept(locals(), ('_hx',))


def _seg_0040_022___hy(*, M: Any = _UNBOUND, quarters: Any = _UNBOUND, scale: Any = _UNBOUND, wys: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 0040.022 (_hy) - body verbatim from _seg_0040__city_commoner_dwellings_inside_walls (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale in ('city', 'capital') and M.get('wall') and quarters:
        _hy = sweep_hi(min(wys), max(wys), 40)
    return _kept(locals(), ('_hy',))


def _seg_0040_023__gx(*, M: Any = _UNBOUND, quarters: Any = _UNBOUND, scale: Any = _UNBOUND, wxs: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 0040.023 (gx) - body verbatim from _seg_0040__city_commoner_dwellings_inside_walls (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale in ('city', 'capital') and M.get('wall') and quarters:
        gx = min(wxs)
    return _kept(locals(), ('gx',))


def _seg_0040_024__gx_1(
    *,
    M: Any = _UNBOUND,
    _hx: Any = _UNBOUND,
    _hy: Any = _UNBOUND,
    gx: Any = _UNBOUND,
    gy: Any = _UNBOUND,
    interior_cells: Any = _UNBOUND,
    n_in: Any = _UNBOUND,
    overlapped: Any = _UNBOUND,
    q: Any = _UNBOUND,
    quarters: Any = _UNBOUND,
    scale: Any = _UNBOUND,
    spill_cells: Any = _UNBOUND,
    uncovered: Any = _UNBOUND,
    wall_p: Any = _UNBOUND,
    wys: Any = _UNBOUND,
) -> dict[str, Any]:
    """Gate segment 0040.024 (gx, gy, interior_cells, n_in) - body verbatim from _seg_0040__city_commoner_dwellings_inside_walls (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale in ('city', 'capital') and M.get('wall') and quarters:
        while gx <= _hx:
            gy = min(wys)
            while gy <= _hy:
                n_in = sum(1 for q in quarters if point_in_poly(gx, gy, q["poly"]))
                if point_in_poly(gx, gy, wall_p):
                    interior_cells += 1
                    if n_in == 0:
                        uncovered += 1
                    elif n_in > 1:
                        overlapped += 1
                elif n_in >= 1:
                    spill_cells += 1
                gy += 40
            gx += 40
    return _kept(locals(), ('gx', 'gy', 'interior_cells', 'n_in', 'overlapped', 'q', 'spill_cells', 'uncovered'))
