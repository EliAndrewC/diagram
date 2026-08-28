"""Town, city and capital segments moved out of `segments_01b_quarters_and_civic_reserve.py` by feature 145.

The GM ruled on 2026-08-28 that the hamlet path owes 100% coverage and the other tiers owe none while
nothing exercises them - and the floor is MODULE level, so a city segment sharing a file with a hamlet
segment put its whole body under the hamlet floor. Execution order is by the segment's numeric key
(`registry._ordered_names`), never by file, so moving one costs nothing and needs no placement row."""

from typing import Any

from .common_01_geometry import (
    _struct_rect,
    largest_empty_gap,
    point_in_poly,
    poly_area,
    sweep_hi,
)
from .common_03_capacity import (
    _UNBOUND,
    DEAD_ZONE_MAX,
    DWELLING_KINDS,
    QUARTER_DENSITY_CEIL,
    QUARTER_DENSITY_FLOOR,
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


def _seg_0040_014__b(*, M: Any = _UNBOUND, b: Any = _UNBOUND, quarters: Any = _UNBOUND, scale: Any = _UNBOUND, wall_p: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 0040.014 (b, dwell_pts) - body verbatim from _seg_0040__city_commoner_dwellings_inside_walls (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale in ('city', 'capital') and M.get('wall') and quarters:
        dwell_pts = [(b["x"], b["y"]) for b in M.get("buildings", []) if b.get("kind") in DWELLING_KINDS and point_in_poly(b["x"], b["y"], wall_p)]
    return _kept(locals(), ('b', 'dwell_pts'))


def _seg_0040_015___yq(
    *,
    M: Any = _UNBOUND,
    _yq: Any = _UNBOUND,
    d9: Any = _UNBOUND,
    dwell_pts: Any = _UNBOUND,
    m9: Any = _UNBOUND,
    p9: Any = _UNBOUND,
    quarters: Any = _UNBOUND,
    scale: Any = _UNBOUND,
    t9: Any = _UNBOUND,
) -> dict[str, Any]:
    """Gate segment 0040.015 (_yq, d9, dwell_pts, m9) - body verbatim from _seg_0040__city_commoner_dwellings_inside_walls (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale in ('city', 'capital') and M.get('wall') and quarters and scale == "capital":
        # capital fabric counts its OTHER dwelling forms (021, same arithmetic as the
        # population check): yashiki-band manors are households, and a terrace range is
        # `units` households at one seat - without them the samurai quarters read empty
        # to the density rule while being fully built.
        _yq = [d9["poly"] for d9 in M.get("districts", []) if d9.get("rank_band") == "yashiki"]
        dwell_pts += [(m9["x"], m9["y"]) for m9 in M.get("manors", []) if any(point_in_poly(m9["x"], m9["y"], p9) for p9 in _yq)]
        for t9 in M.get("terraces", []):
            dwell_pts += [(t9["x"], t9["y"])] * int(t9.get("units", 0))
    return _kept(locals(), ('_yq', 'd9', 'dwell_pts', 'm9', 'p9', 't9'))


def _seg_0040_016___civic(*, M: Any = _UNBOUND, quarters: Any = _UNBOUND, scale: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 0040.016 (_civic) - body verbatim from _seg_0040__city_commoner_dwellings_inside_walls (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale in ('city', 'capital') and M.get('wall') and quarters:
        _civic = (
            M.get("ministries", [])
            + M.get("religious", [])
            + M.get("cemeteries", [])
            + M.get("mausoleums", [])
            + M.get("storehouses", [])
            + ([M["governor_mansion"]] if M.get("governor_mansion") else [])
        )
    return _kept(locals(), ('_civic',))


def _seg_0040_017__c(*, M: Any = _UNBOUND, _civic: Any = _UNBOUND, c: Any = _UNBOUND, quarters: Any = _UNBOUND, scale: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 0040.017 (c, civic_rects) - body verbatim from _seg_0040__city_commoner_dwellings_inside_walls (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale in ('city', 'capital') and M.get('wall') and quarters:
        civic_rects = [_struct_rect(c) for c in _civic if "w" in c]
    return _kept(locals(), ('c', 'civic_rects'))


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


def _seg_0040_028__thin_q(*, M: Any = _UNBOUND, quarters: Any = _UNBOUND, scale: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 0040.028 (thin_q) - body verbatim from _seg_0040__city_commoner_dwellings_inside_walls (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale in ('city', 'capital') and M.get('wall') and quarters:
        thin_q = []  # type: ignore[var-annotated]
    return _kept(locals(), ('thin_q',))


def _seg_0040_029__civic_in_q(
    *,
    M: Any = _UNBOUND,
    civic_in_q: Any = _UNBOUND,
    civic_rects: Any = _UNBOUND,
    dens: Any = _UNBOUND,
    dwell_pts: Any = _UNBOUND,
    eff_area: Any = _UNBOUND,
    nm: Any = _UNBOUND,
    p: Any = _UNBOUND,
    q: Any = _UNBOUND,
    qarea: Any = _UNBOUND,
    qd: Any = _UNBOUND,
    qpoly: Any = _UNBOUND,
    quarters: Any = _UNBOUND,
    r: Any = _UNBOUND,
    scale: Any = _UNBOUND,
    thin_q: Any = _UNBOUND,
    w: Any = _UNBOUND,
    x: Any = _UNBOUND,
    y: Any = _UNBOUND,
) -> dict[str, Any]:
    """Gate segment 0040.029 (civic_in_q, dens, eff_area, nm) - body verbatim from _seg_0040__city_commoner_dwellings_inside_walls (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale in ('city', 'capital') and M.get('wall') and quarters:
        for q in quarters:
            if q.get("zone") not in ("residential", "mixed"):
                continue
            qpoly = q["poly"]
            qarea = poly_area(qpoly)
            if qarea <= 0:
                continue
            qd = [(x, y) for x, y in dwell_pts if point_in_poly(x, y, qpoly)]
            # density is measured over HOUSING-AVAILABLE ground: subtract any civic compound
            # footprint sitting in the quarter (a government ward or a temple in a merchant
            # district eats area that was never going to be housing), so a mixed quarter is not
            # wrongly flagged under-built for the ground its compounds occupy.
            civic_in_q = sum(r["w"] * r["h"] for r in civic_rects if point_in_poly(r["x"], r["y"], qpoly))
            eff_area = max(qarea - civic_in_q, 1.0)
            dens = len(qd) / eff_area
            nm = q.get("name") or f"quarter@({round(sum(p[0] for p in qpoly) / len(qpoly))},{round(sum(p[1] for p in qpoly) / len(qpoly))})"
            if dens < QUARTER_DENSITY_FLOOR:
                thin_q.append((nm, f"{len(qd)} dwellings, density {dens * 1000:.2f}/1000px^2 < floor {QUARTER_DENSITY_FLOOR * 1000:.2f} (under-built)"))
            elif dens > QUARTER_DENSITY_CEIL:
                thin_q.append((nm, f"density {dens * 1000:.2f}/1000px^2 > ceil {QUARTER_DENSITY_CEIL * 1000:.2f} (implausibly crammed)"))
            elif (
                q.get("zone") == "residential"
                and largest_empty_gap(
                    qpoly, qd + [(w["x"], w["y"]) for w in M.get("wells", []) if point_in_poly(w["x"], w["y"], qpoly)], occupied=[r for r in civic_rects if point_in_poly(r["x"], r["y"], qpoly)]
                )
                > DEAD_ZONE_MAX
            ):
                # the dead-zone guard applies to PURE residential quarters (uniform housing, no
                # empty blocks); a MIXED quarter legitimately holds a civic forecourt/plaza, so it
                # is judged on the density AVERAGE only. An all-empty region declared to dodge this
                # still fails: as residential it fires here, as civic it fires city_civic_quarter,
                # as mixed its average density is too low.
                thin_q.append((nm, f"dead zone: an empty pocket wider than a firebreak ({DEAD_ZONE_MAX:.0f}px) inside a residential quarter"))
    return _kept(locals(), ('civic_in_q', 'dens', 'eff_area', 'nm', 'p', 'q', 'qarea', 'qd', 'qpoly', 'r', 'thin_q', 'w', 'x', 'y'))
