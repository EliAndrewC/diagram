"""Town, city and capital segments moved out of `segments_02c_walls_gates_and_housing.py` by feature 145.

The GM ruled on 2026-08-28 that the hamlet path owes 100% coverage and the other tiers owe none while
nothing exercises them - and the floor is MODULE level, so a city segment sharing a file with a hamlet
segment put its whole body under the hamlet floor. Execution order is by the segment's numeric key
(`registry._ordered_names`), never by file, so moving one costs nothing and needs no placement row."""

import math
from typing import Any

from .common_01_geometry import Poly, point_in_poly, poly_dist, seg_closest, seg_dist
from .common_02_overlap_policy import onmap_field_edge
from .common_03_capacity import (
    _UNBOUND,
    _kept,
)


def _seg_0133_006__ADJ(*, scale: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 0133.006 (ADJ) - body verbatim from _seg_0133__outside_fields_farmhouse_density (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale in ('town', 'city', 'capital'):
        ADJ = 165
    return _kept(locals(), ('ADJ',))


def _seg_0133_011__FARM_LD_INWALL(*, scale: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 0133.011 (FARM_LD_INWALL) - body verbatim from _seg_0133__outside_fields_farmhouse_density (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale in ('town', 'city', 'capital'):
        FARM_LD_INWALL = 16.0  # houses per 1000px of edge - a full, all-round ring, not the off-map floor
    return _kept(locals(), ('FARM_LD_INWALL',))


def _seg_0133_012__city_interior_fields_farmhouse_density(
    *,
    ADJ: Any = _UNBOUND,
    EX0: Any = _UNBOUND,
    EX1: Any = _UNBOUND,
    EY0: Any = _UNBOUND,
    EY1: Any = _UNBOUND,
    FARM_LD_INWALL: Any = _UNBOUND,
    M: Any = _UNBOUND,
    URBAN: Any = _UNBOUND,
    check: Any = _UNBOUND,
    cx: Any = _UNBOUND,
    cy: Any = _UNBOUND,
    edge: Any = _UNBOUND,
    f: Any = _UNBOUND,
    fields: Any = _UNBOUND,
    h: Any = _UNBOUND,
    houses: Any = _UNBOUND,
    meta: Any = _UNBOUND,
    nv: Any = _UNBOUND,
    scale: Any = _UNBOUND,
    thin: Any = _UNBOUND,
) -> dict[str, Any]:
    """Gate segment 0133.012 (city_interior_fields_farmhouse_density) - body verbatim from _seg_0133__outside_fields_farmhouse_density (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale in ('town', 'city', 'capital') and URBAN and meta.get("agricultural_district") and M.get("wall"):
        thin = []
        for f in fields:
            cx, cy = (f["bbox"][0] + f["bbox"][2]) / 2, (f["bbox"][1] + f["bbox"][3]) / 2
            if not point_in_poly(cx, cy, M["wall"]):
                continue  # only the in-wall plots
            # VEGETABLE tracts are exempt from the farmstead ring: urban garden ground is
            # worked by the residents of the surrounding quarters (well/night-soil fed
            # intensive plots), not by dedicated in-wall farm households - only in-wall
            # PADDY carries the village-density farmhouse ring
            if f.get("kind") != "paddy":
                continue
            edge = onmap_field_edge(f["outline"], EX0, EY0, EX1, EY1)
            if edge < 120:
                continue
            nv = sum(1 for h in houses if poly_dist(h["x"], h["y"], f["outline"]) <= ADJ)
            if nv < FARM_LD_INWALL * edge / 1000:
                thin.append((f["name"], nv, round(FARM_LD_INWALL * edge / 1000, 1)))
        pass  # `` retired under feature 141 (the GM's cut); the segment stays for the check it keeps or the value it writes
    return _kept(locals(), ('cx', 'cy', 'edge', 'f', 'h', 'nv', 'thin'))


def _seg_0133_020__alley_blds(*, M: Any = _UNBOUND, scale: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 0133.020 (alley_blds) - body verbatim from _seg_0133__outside_fields_farmhouse_density (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale in ('town', 'city', 'capital'):
        alley_blds = M.get("buildings", []) + M.get("houses", [])
    return _kept(locals(), ('alley_blds',))


def _seg_0133_021__a_1(*, M: Any = _UNBOUND, a: Any = _UNBOUND, scale: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 0133.021 (a, alleys) - body verbatim from _seg_0133__outside_fields_farmhouse_density (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale in ('town', 'city', 'capital'):
        alleys = [a["pts"] for a in M.get("alleys", [])]
    return _kept(locals(), ('a', 'alleys'))


def _seg_0133_022__other(*, M: Any = _UNBOUND, s: Any = _UNBOUND, scale: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 0133.022 (other, s) - body verbatim from _seg_0133__outside_fields_farmhouse_density (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale in ('town', 'city', 'capital'):
        other = [s["pts"] for s in M.get("town_streets", [])] + ([M["road"]] if M.get("road") else [])
    return _kept(locals(), ('other', 's'))


def _seg_0133_023__kido(*, M: Any = _UNBOUND, scale: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 0133.023 (kido) - body verbatim from _seg_0133__outside_fields_farmhouse_density (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale in ('town', 'city', 'capital'):
        kido = M.get("kido", [])
    return _kept(locals(), ('kido',))


def _seg_0133_024__lane_dist(*, b: Any = _UNBOUND, i: Any = _UNBOUND, pts: Any = _UNBOUND, scale: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 0133.024 (lane_dist) - body verbatim from _seg_0133__outside_fields_farmhouse_density (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale in ('town', 'city', 'capital'):

        def lane_dist(b: dict[str, Any], pts: Poly) -> float:
            return min(seg_dist(b["x"], b["y"], pts[i], pts[i + 1]) for i in range(len(pts) - 1))

    return _kept(locals(), ('lane_dist',))


def _seg_0133_025__foot(*, b: Any = _UNBOUND, c: Any = _UNBOUND, i: Any = _UNBOUND, pts: Any = _UNBOUND, scale: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 0133.025 (foot) - body verbatim from _seg_0133__outside_fields_farmhouse_density (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale in ('town', 'city', 'capital'):

        def foot(b: dict[str, Any], pts: Poly) -> tuple[float, float]:
            return min((seg_closest(b["x"], b["y"], pts[i], pts[i + 1]) for i in range(len(pts) - 1)), key=lambda c: math.hypot(b["x"] - c[0], b["y"] - c[1]))

    return _kept(locals(), ('foot',))


def _seg_0133_026__gate_spur(
    *,
    E: Any = _UNBOUND,
    alley_blds: Any = _UNBOUND,
    b: Any = _UNBOUND,
    c: Any = _UNBOUND,
    foot: Any = _UNBOUND,
    g: Any = _UNBOUND,
    kido: Any = _UNBOUND,
    lane_dist: Any = _UNBOUND,
    pts: Any = _UNBOUND,
    reach: Any = _UNBOUND,
    scale: Any = _UNBOUND,
) -> dict[str, Any]:
    """Gate segment 0133.026 (gate_spur) - body verbatim from _seg_0133__outside_fields_farmhouse_density (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale in ('town', 'city', 'capital'):

        def gate_spur(pts: Poly) -> float:
            # a terminal stretch running OUT to a ward GATE past the last served building is a legitimate
            # gate-access spur (the lane pulls in to a kido), NOT a lane-to-nowhere - so it does not count
            # toward the serve ratio. Trim it from each gated end (distance from the gate to the nearest
            # building the lane fronts, measured along the lane).
            spur = 0.0
            for E in (pts[0], pts[-1]):
                if not any(math.hypot(E[0] - g["x"], E[1] - g["y"]) < 20 for g in kido):
                    continue
                reach = [math.hypot(E[0] - (c := foot(b, pts))[0], E[1] - c[1]) for b in alley_blds if lane_dist(b, pts) < 60]
                if reach:
                    spur += min(reach)
            return spur

    return _kept(locals(), ('gate_spur',))


def _seg_0133_027__uniq(*, alleys: Any = _UNBOUND, scale: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 0133.027 (uniq) - body verbatim from _seg_0133__outside_fields_farmhouse_density (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale in ('town', 'city', 'capital'):
        uniq = [0] * len(alleys)
    return _kept(locals(), ('uniq',))


def _seg_0133_028__b_3(
    *,
    alley_blds: Any = _UNBOUND,
    alleys: Any = _UNBOUND,
    b: Any = _UNBOUND,
    best_d: Any = _UNBOUND,
    best_i: Any = _UNBOUND,
    d: Any = _UNBOUND,
    lane_dist: Any = _UNBOUND,
    li: Any = _UNBOUND,
    other: Any = _UNBOUND,
    pts: Any = _UNBOUND,
    scale: Any = _UNBOUND,
    uniq: Any = _UNBOUND,
) -> dict[str, Any]:
    """Gate segment 0133.028 (b, best_d, best_i, d) - body verbatim from _seg_0133__outside_fields_farmhouse_density (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale in ('town', 'city', 'capital'):
        for b in alley_blds:
            best_d, best_i = 60.0, None  # only buildings within a frontage band count for any lane
            for li, pts in enumerate(alleys):
                d = lane_dist(b, pts)
                if d < best_d:
                    best_d, best_i = d, li
            if best_i is None:
                continue
            if all(lane_dist(b, pts) > best_d for pts in other):  # no street/road is closer - this alley owns it
                uniq[best_i] += 1
    return _kept(locals(), ('b', 'best_d', 'best_i', 'd', 'li', 'pts', 'uniq'))


def _seg_0133_029__thin(*, scale: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 0133.029 (thin) - body verbatim from _seg_0133__outside_fields_farmhouse_density (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale in ('town', 'city', 'capital'):
        thin = []  # type: ignore[var-annotated]
    return _kept(locals(), ('thin',))


def _seg_0133_030__i(
    *,
    alleys: Any = _UNBOUND,
    gate_spur: Any = _UNBOUND,
    i: Any = _UNBOUND,
    length: Any = _UNBOUND,
    li: Any = _UNBOUND,
    pts: Any = _UNBOUND,
    scale: Any = _UNBOUND,
    thin: Any = _UNBOUND,
    uniq: Any = _UNBOUND,
) -> dict[str, Any]:
    """Gate segment 0133.030 (i, length, li, pts) - body verbatim from _seg_0133__outside_fields_farmhouse_density (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale in ('town', 'city', 'capital'):
        for li, pts in enumerate(alleys):
            length = sum(math.hypot(pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1]) for i in range(len(pts) - 1))
            length -= gate_spur(pts)  # the run out to a ward gate is access, not block-service
            if uniq[li] * 30 < length:
                thin.append((pts[0], uniq[li], round(length)))
    return _kept(locals(), ('i', 'length', 'li', 'pts', 'thin'))
