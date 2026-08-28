"""Town, city and capital segments moved out of `segments_07b_ponds_hems_and_land_fall.py` by feature 145.

The GM ruled on 2026-08-28 that the hamlet path owes 100% coverage and the other tiers owe none while
nothing exercises them - and the floor is MODULE level, so a city segment sharing a file with a hamlet
segment put its whole body under the hamlet floor. Execution order is by the segment's numeric key
(`registry._ordered_names`), never by file, so moving one costs nothing and needs no placement row."""

from typing import Any

from l7r.diagram.settlement._geom import boxed_seg_hit

from .common_01_geometry import point_in_poly, poly_dist
from .common_02_overlap_policy import in_ellipse
from .common_03_capacity import _UNBOUND, _kept


def _seg_0438_011__nr_lines_1(*, nr_lines: Any = _UNBOUND, road: Any = _UNBOUND, scale: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 0438.011 (nr_lines) - body verbatim from _seg_0438__near_ring_cultivated_fraction (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale in ('town', 'city') and road:
        nr_lines.append((road, 60.0))
    return _kept(locals(), ('nr_lines',))


def _seg_0438_012__nr_lines_2(*, M: Any = _UNBOUND, nr_lines: Any = _UNBOUND, scale: Any = _UNBOUND, st_: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 0438.012 (nr_lines, st_) - body verbatim from _seg_0438__near_ring_cultivated_fraction (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale in ('town', 'city'):
        nr_lines += [(st_["pts"], st_["w"] / 2 + 40) for st_ in M.get("town_streets", [])]
    return _kept(locals(), ('nr_lines', 'st_'))


def _seg_0438_013__ln_(*, M: Any = _UNBOUND, ln_: Any = _UNBOUND, nr_lines: Any = _UNBOUND, scale: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 0438.013 (ln_, nr_lines) - body verbatim from _seg_0438__near_ring_cultivated_fraction (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale in ('town', 'city'):
        nr_lines += [(ln_["pts"], 30.0) for ln_ in M.get("lanes", [])]
    return _kept(locals(), ('ln_', 'nr_lines'))


def _seg_0438_014__c2_(*, M: Any = _UNBOUND, c2_: Any = _UNBOUND, d_: Any = _UNBOUND, nr_lines: Any = _UNBOUND, s_: Any = _UNBOUND, scale: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 0438.014 (c2_, d_, nr_lines, s_) - body verbatim from _seg_0438__near_ring_cultivated_fraction (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale in ('town', 'city'):
        nr_lines += [(s_["poly"], 30.0) for s_ in M.get("streams", [])] + [(c2_["poly"], 24.0) for c2_ in M.get("channels", [])] + [(d_["poly"], 20.0) for d_ in M.get("field_ditches", [])]
    return _kept(locals(), ('c2_', 'd_', 'nr_lines', 's_'))


def _seg_0438_015__nr_moat(*, M: Any = _UNBOUND, scale: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 0438.015 (nr_moat) - body verbatim from _seg_0438__near_ring_cultivated_fraction (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale in ('town', 'city'):
        nr_moat = M.get("moat")
    return _kept(locals(), ('nr_moat',))


def _seg_0438_017__nr_wall(*, M: Any = _UNBOUND, scale: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 0438.017 (nr_wall) - body verbatim from _seg_0438__near_ring_cultivated_fraction (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale in ('town', 'city'):
        nr_wall = M.get("wall")
    return _kept(locals(), ('nr_wall',))


def _seg_0438_018__nr_hill(*, M: Any = _UNBOUND, scale: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 0438.018 (nr_hill) - body verbatim from _seg_0438__near_ring_cultivated_fraction (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale in ('town', 'city'):
        nr_hill = M.get("hill")
    return _kept(locals(), ('nr_hill',))


def _seg_0438_019__nr_pond(*, M: Any = _UNBOUND, scale: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 0438.019 (nr_pond) - body verbatim from _seg_0438__near_ring_cultivated_fraction (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale in ('town', 'city'):
        nr_pond = M.get("pond")
    return _kept(locals(), ('nr_pond',))


def _seg_0438_020__nr_band(*, URBAN: Any = _UNBOUND, meta: Any = _UNBOUND, nr_wall: Any = _UNBOUND, scale: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 0438.020 (nr_band) - body verbatim from _seg_0438__near_ring_cultivated_fraction (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale in ('town', 'city'):
        nr_band = (800.0 / (meta.get("ftpx") or 1)) if (URBAN and nr_wall is not None and len(nr_wall) >= 3) else None
    return _kept(locals(), ('nr_band',))


def _seg_0438_021__SX0(
    *,
    EX0: Any = _UNBOUND,
    EX1: Any = _UNBOUND,
    EY0: Any = _UNBOUND,
    EY1: Any = _UNBOUND,
    Hd: Any = _UNBOUND,
    Wd: Any = _UNBOUND,
    _wxs: Any = _UNBOUND,
    _wys: Any = _UNBOUND,
    nr_band: Any = _UNBOUND,
    nr_wall: Any = _UNBOUND,
    p_: Any = _UNBOUND,
    scale: Any = _UNBOUND,
) -> dict[str, Any]:
    """Gate segment 0438.021 (SX0, SX1, SY0, SY1) - body verbatim from _seg_0438__near_ring_cultivated_fraction (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale in ('town', 'city'):
        if nr_band is not None and nr_wall is not None:
            _wxs = [p_[0] for p_ in nr_wall]
            _wys = [p_[1] for p_ in nr_wall]
            SX0, SY0 = max(0.0, min(_wxs) - nr_band - 25), max(0.0, min(_wys) - nr_band - 25)
            SX1, SY1 = min(float(Wd), max(_wxs) + nr_band + 25), min(float(Hd), max(_wys) + nr_band + 25)
        else:
            SX0, SY0, SX1, SY1 = EX0, EY0, EX1, EY1
    return _kept(locals(), ('SX0', 'SX1', 'SY0', 'SY1', '_wxs', '_wys', 'p_'))


def _seg_0438_022__nr_cultc(*, scale: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 0438.022 (nr_cultc, nr_elig) - body verbatim from _seg_0438__near_ring_cultivated_fraction (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale in ('town', 'city'):
        nr_elig = nr_cultc = 0
    return _kept(locals(), ('nr_cultc', 'nr_elig'))


def _seg_0438_023__gy(*, SY0: Any = _UNBOUND, scale: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 0438.023 (gy) - body verbatim from _seg_0438__near_ring_cultivated_fraction (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale in ('town', 'city'):
        gy = SY0 + 12.5
    return _kept(locals(), ('gy',))


def _seg_0438_024__bx0(
    *,
    SX0: Any = _UNBOUND,
    SX1: Any = _UNBOUND,
    SY1: Any = _UNBOUND,
    bx0: Any = _UNBOUND,
    bx1: Any = _UNBOUND,
    by0: Any = _UNBOUND,
    by1: Any = _UNBOUND,
    committed: Any = _UNBOUND,
    gx: Any = _UNBOUND,
    gy: Any = _UNBOUND,
    nr_band: Any = _UNBOUND,
    nr_boxes_b: Any = _UNBOUND,
    nr_cult: Any = _UNBOUND,
    nr_cultc: Any = _UNBOUND,
    nr_elig: Any = _UNBOUND,
    nr_hill: Any = _UNBOUND,
    nr_lines_b: Any = _UNBOUND,
    nr_pond: Any = _UNBOUND,
    nr_skip: Any = _UNBOUND,
    nr_wall: Any = _UNBOUND,
    p_: Any = _UNBOUND,
    scale: Any = _UNBOUND,
) -> dict[str, Any]:
    """Gate segment 0438.024 (bx0, bx1, by0, by1) - body verbatim from _seg_0438__near_ring_cultivated_fraction (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale in ('town', 'city'):
        while gy < SY1:
            gx = SX0 + 12.5
            while gx < SX1:
                # a cell inside the rampart of a walled town/city is URBAN FLOOR, not near-ring farmland
                # (same reading as town_margins_clothed's inside-the-rampart exemption) - the near ring is
                # the EXTRAMURAL flat ground; the intramural chrysanthemum field / open squares are the town
                committed = (
                    (nr_wall is not None and len(nr_wall) >= 3 and point_in_poly(gx, gy, nr_wall))
                    or (nr_band is not None and nr_wall is not None and poly_dist(gx, gy, nr_wall) > nr_band)  # beyond the near ring: countryside, not judged here
                    or (nr_hill is not None and in_ellipse(gx, gy, nr_hill, 1.45))
                    or (nr_pond is not None and in_ellipse(gx, gy, [nr_pond[0], nr_pond[1], nr_pond[2] + 20, nr_pond[3] + 20]))
                    or any(bx0 <= gx <= bx1 and by0 <= gy <= by1 for bx0, by0, bx1, by1 in nr_boxes_b.near(gx, gy))  # indexed (segment 016)
                    or boxed_seg_hit(gx, gy, nr_lines_b.near(gx, gy))  # indexed; same test as the scan it replaced (see segment 016)
                    or any(point_in_poly(gx, gy, p_) for p_ in nr_skip)
                )
                if committed:
                    gx += 25
                    continue
                nr_elig += 1
                if any(point_in_poly(gx, gy, p_) for p_ in nr_cult):
                    nr_cultc += 1
                gx += 25
            gy += 25
    return _kept(locals(), ('bx0', 'bx1', 'by0', 'by1', 'committed', 'gx', 'gy', 'nr_cultc', 'nr_elig', 'p_'))


def _seg_0438_029__f__1(*, M: Any = _UNBOUND, f_: Any = _UNBOUND, scale: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 0438.029 (f_, nrp_paddy) - body verbatim from _seg_0438__near_ring_cultivated_fraction (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale in ('town', 'city'):
        nrp_paddy = [f_["outline"] for f_ in M.get("fields", []) if f_.get("kind") == "paddy"]
    return _kept(locals(), ('f_', 'nrp_paddy'))


def _seg_0438_030___HEM(*, scale: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 0438.030 (_HEM) - body verbatim from _seg_0438__near_ring_cultivated_fraction (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale in ('town', 'city'):
        _HEM = 135.0
    return _kept(locals(), ('_HEM',))


def _seg_0438_031__f__2(*, M: Any = _UNBOUND, f_: Any = _UNBOUND, scale: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 0438.031 (f_, nrp_pbbox) - body verbatim from _seg_0438__near_ring_cultivated_fraction (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale in ('town', 'city'):
        nrp_pbbox = [f_["bbox"] for f_ in M.get("fields", []) if f_.get("kind") == "paddy" and f_.get("bbox")]
    return _kept(locals(), ('f_', 'nrp_pbbox'))


def _seg_0438_032__nrp_drygrain(*, scale: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 0438.032 (nrp_drygrain) - body verbatim from _seg_0438__near_ring_cultivated_fraction (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale in ('town', 'city'):
        nrp_drygrain = []  # type: ignore[var-annotated]
    return _kept(locals(), ('nrp_drygrain',))


def _seg_0438_033__bx0_(
    *,
    M: Any = _UNBOUND,
    _HEM: Any = _UNBOUND,
    bx0_: Any = _UNBOUND,
    bx1_: Any = _UNBOUND,
    by0_: Any = _UNBOUND,
    by1_: Any = _UNBOUND,
    dcx_: Any = _UNBOUND,
    dcy_: Any = _UNBOUND,
    nrp_drygrain: Any = _UNBOUND,
    nrp_pbbox: Any = _UNBOUND,
    o_: Any = _UNBOUND,
    p_: Any = _UNBOUND,
    scale: Any = _UNBOUND,
    v_: Any = _UNBOUND,
) -> dict[str, Any]:
    """Gate segment 0438.033 (bx0_, bx1_, by0_, by1_) - body verbatim from _seg_0438__near_ring_cultivated_fraction (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale in ('town', 'city'):
        for o_ in M.get("dry_plots", []) or []:
            p_ = o_.get("poly") if isinstance(o_, dict) else o_
            if p_ is not None and len(p_) >= 3 and (not isinstance(o_, dict) or o_.get("crop") != "garden"):
                dcx_ = sum(v_[0] for v_ in p_) / len(p_)
                dcy_ = sum(v_[1] for v_ in p_) / len(p_)
                if not any(bx0_ - _HEM <= dcx_ <= bx1_ + _HEM and by0_ - _HEM <= dcy_ <= by1_ + _HEM for bx0_, by0_, bx1_, by1_ in nrp_pbbox):
                    nrp_drygrain.append(p_)
    return _kept(locals(), ('bx0_', 'bx1_', 'by0_', 'by1_', 'dcx_', 'dcy_', 'nrp_drygrain', 'o_', 'p_', 'v_'))


def _seg_0438_034__nrp_dc(*, scale: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 0438.034 (nrp_dc, nrp_pc) - body verbatim from _seg_0438__near_ring_cultivated_fraction (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale in ('town', 'city'):
        nrp_pc = nrp_dc = 0
    return _kept(locals(), ('nrp_dc', 'nrp_pc'))


def _seg_0438_035__gy_1(*, SY0: Any = _UNBOUND, scale: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 0438.035 (gy) - body verbatim from _seg_0438__near_ring_cultivated_fraction (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale in ('town', 'city'):
        gy = SY0 + 12.5  # the same canvas-space band window as the fraction sampler above
    return _kept(locals(), ('gy',))


def _seg_0438_036__bx0_1(
    *,
    SX0: Any = _UNBOUND,
    SX1: Any = _UNBOUND,
    SY1: Any = _UNBOUND,
    bx0: Any = _UNBOUND,
    bx1: Any = _UNBOUND,
    by0: Any = _UNBOUND,
    by1: Any = _UNBOUND,
    committed: Any = _UNBOUND,
    gx: Any = _UNBOUND,
    gy: Any = _UNBOUND,
    nr_band: Any = _UNBOUND,
    nr_boxes_b: Any = _UNBOUND,
    nr_hill: Any = _UNBOUND,
    nr_lines_b: Any = _UNBOUND,
    nr_pond: Any = _UNBOUND,
    nr_skip: Any = _UNBOUND,
    nr_wall: Any = _UNBOUND,
    nrp_dc: Any = _UNBOUND,
    nrp_drygrain: Any = _UNBOUND,
    nrp_paddy: Any = _UNBOUND,
    nrp_pc: Any = _UNBOUND,
    p_: Any = _UNBOUND,
    scale: Any = _UNBOUND,
) -> dict[str, Any]:
    """Gate segment 0438.036 (bx0, bx1, by0, by1) - body verbatim from _seg_0438__near_ring_cultivated_fraction (feature 024 per-check split; guards re-evaluated in the body, see split_oversized.py)."""
    if scale in ('town', 'city'):
        while gy < SY1:
            gx = SX0 + 12.5
            while gx < SX1:
                committed = (
                    (nr_wall is not None and len(nr_wall) >= 3 and point_in_poly(gx, gy, nr_wall))
                    or (nr_band is not None and nr_wall is not None and poly_dist(gx, gy, nr_wall) > nr_band)  # beyond the near ring: countryside (same cap as the fraction sampler above)
                    or (nr_hill is not None and in_ellipse(gx, gy, nr_hill, 1.45))
                    or (nr_pond is not None and in_ellipse(gx, gy, [nr_pond[0], nr_pond[1], nr_pond[2] + 20, nr_pond[3] + 20]))
                    or any(bx0 <= gx <= bx1 and by0 <= gy <= by1 for bx0, by0, bx1, by1 in nr_boxes_b.near(gx, gy))  # indexed (segment 016)
                    or boxed_seg_hit(gx, gy, nr_lines_b.near(gx, gy))  # indexed; same test as the scan it replaced (see segment 016)
                    or any(point_in_poly(gx, gy, p_) for p_ in nr_skip)
                )
                if not committed and any(point_in_poly(gx, gy, p_) for p_ in nrp_paddy):
                    nrp_pc += 1
                elif any(point_in_poly(gx, gy, p_) for p_ in nrp_drygrain):
                    nrp_dc += 1
                gx += 25
            gy += 25
    return _kept(locals(), ('bx0', 'bx1', 'by0', 'by1', 'committed', 'gx', 'gy', 'nrp_dc', 'nrp_pc', 'p_'))
