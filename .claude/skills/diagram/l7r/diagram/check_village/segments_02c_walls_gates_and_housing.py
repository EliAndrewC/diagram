"""Gate segments (walls gates and housing; keys 0124-0133_030) - bodies verbatim, registry order preserved."""

from typing import Any

from .common_01_geometry import point_in_poly, seg_dist
from .common_03_capacity import (
    _UNBOUND,
    _kept,
)


def _seg_0124___hq_tol(*, _hq_ftpx: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 124 (_hq_tol) - body verbatim from the legacy gate() (feature 022)."""
    _hq_tol = 8.0 / _hq_ftpx
    return _kept(locals(), ('_hq_tol',))


def _seg_0125___hq_bare() -> dict[str, Any]:
    """Gate segment 125 (_hq_bare, _hq_total) - body verbatim from the legacy gate() (feature 022)."""
    _hq_bare = _hq_total = 0
    return _kept(locals(), ('_hq_bare', '_hq_total'))


def _seg_0126___hq_fields(*, M: Any = _UNBOUND, f: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 126 (_hq_fields, f) - body verbatim from the legacy gate() (feature 022)."""
    _hq_fields = [f for f in M.get("fields", []) if f.get("kind") == "paddy" and f.get("plot_polys")]
    return _kept(locals(), ('_hq_fields', 'f'))


# PADDY FANS ARE GAPLESS inside their command area: bare parchment inside a comb fan is
# ground the water commands that nobody planted - the "white spots" bug. The carve's minimum
# plot/sector/closer thresholds are REAL-FEET quantities (build_comb's `grain` scales them:
# tuned at 2 ft/px, a 3 ft/px city passes grain=2/3); left unscaled they silently drop
# sectors, head plots and gap-closers a village would plant (Tango/Nagahara re-exposed
# exactly this at the city grain, 2026-07-21 - the frozen fixture). Only fields that record
# their drawn "plot_polys" are gated (the city gens do; a village gen can opt in by recording
# them). The rim is inset away (canal berms / drain set-backs legitimately live there) and
# the tolerance covers bunds and the delivery-ditch strips between plot columns.


def _seg_0128___gpx(*, meta: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 128 (_gpx) - body verbatim from the legacy gate() (feature 022)."""
    _gpx = float(meta.get("ftpx", 1) or 1)
    return _kept(locals(), ('_gpx',))


def _seg_0129___g_inset(*, _gpx: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 129 (_g_inset, _g_step, _g_tol) - body verbatim from the legacy gate() (feature 022)."""
    _g_inset, _g_tol, _g_step = 56.0 / _gpx, 6.0 / _gpx, 24.0 / _gpx
    return _kept(locals(), ('_g_inset', '_g_step', '_g_tol'))


# the plot tolerance is BUND-scale (6 real ft): anything wider than a bund must be planted
# or be WATER - the field's recorded ditches count as covered ground (they draw over the
# fan), so the delivery-ditch strips between plot columns never read as bare


def _seg_0130__gap_fields() -> dict[str, Any]:
    """Gate segment 130 (gap_fields) - body verbatim from the legacy gate() (feature 022)."""
    gap_fields = []  # type: ignore[var-annotated]
    return _kept(locals(), ('gap_fields',))


def _seg_0131__bx0(
    *,
    M: Any = _UNBOUND,
    _g_inset: Any = _UNBOUND,
    _g_step: Any = _UNBOUND,
    _g_tol: Any = _UNBOUND,
    _gpx: Any = _UNBOUND,
    bx0: Any = _UNBOUND,
    bx1: Any = _UNBOUND,
    by0: Any = _UNBOUND,
    by1: Any = _UNBOUND,
    d: Any = _UNBOUND,
    dp: Any = _UNBOUND,
    f: Any = _UNBOUND,
    fditch: Any = _UNBOUND,
    gap_fields: Any = _UNBOUND,
    gbare: Any = _UNBOUND,
    gout: Any = _UNBOUND,
    gp: Any = _UNBOUND,
    gplots: Any = _UNBOUND,
    gtotal: Any = _UNBOUND,
    gx: Any = _UNBOUND,
    gy: Any = _UNBOUND,
    hw: Any = _UNBOUND,
    i: Any = _UNBOUND,
    ok_pt: Any = _UNBOUND,
    pboxes: Any = _UNBOUND,
    px0: Any = _UNBOUND,
    px1: Any = _UNBOUND,
    py0: Any = _UNBOUND,
    py1: Any = _UNBOUND,
    q: Any = _UNBOUND,
) -> dict[str, Any]:
    """Gate segment 131 (bx0, bx1, by0, by1) - body verbatim from the legacy gate() (feature 022)."""
    for f in M.get("fields", []):
        if f.get("kind") != "paddy" or not f.get("plot_polys") or not f.get("outline"):
            continue
        gout = [(q[0], q[1]) for q in f["outline"]]
        gplots = [[(q[0], q[1]) for q in gp] for gp in f["plot_polys"]]
        pboxes = [(min(q[0] for q in gp) - _g_tol, min(q[1] for q in gp) - _g_tol, max(q[0] for q in gp) + _g_tol, max(q[1] for q in gp) + _g_tol) for gp in gplots]
        fditch = [d for d in M.get("field_ditches", []) if d.get("field") == f.get("name")]
        bx0, by0 = min(q[0] for q in gout), min(q[1] for q in gout)
        bx1, by1 = max(q[0] for q in gout), max(q[1] for q in gout)
        gbare = gtotal = 0
        gy = by0
        while gy <= by1:
            gx = bx0
            while gx <= bx1:
                if point_in_poly(gx, gy, gout) and all(seg_dist(gx, gy, gout[i], gout[(i + 1) % len(gout)]) > _g_inset for i in range(len(gout))):
                    gtotal += 1
                    ok_pt = False
                    for gp, (px0, py0, px1, py1) in zip(gplots, pboxes, strict=True):
                        if not (px0 <= gx <= px1 and py0 <= gy <= py1):
                            continue
                        if point_in_poly(gx, gy, gp) or any(seg_dist(gx, gy, gp[i], gp[(i + 1) % len(gp)]) < _g_tol for i in range(len(gp))):
                            ok_pt = True
                            break
                    if not ok_pt:
                        for d in fditch:
                            hw = float(d.get("w", 4)) / 2 + 6.0 / _gpx
                            dp = d["poly"]
                            if any(seg_dist(gx, gy, dp[i], dp[i + 1]) < hw for i in range(len(dp) - 1)):
                                ok_pt = True
                                break
                    if not ok_pt:
                        gbare += 1
                gx += _g_step
            gy += _g_step
        if gtotal and gbare > max(2, 0.02 * gtotal):
            gap_fields.append(f"{f.get('name')} ({gbare}/{gtotal} bare)")
    return _kept(
        locals(),
        ('bx0', 'bx1', 'by0', 'by1', 'd', 'dp', 'f', 'fditch', 'gap_fields', 'gbare', 'gout', 'gp', 'gplots', 'gtotal', 'gx', 'gy', 'hw', 'i', 'ok_pt', 'pboxes', 'px0', 'px1', 'py0', 'py1', 'q'),
    )


# ALMOST all shops front a street (commerce wants the street); POOR housing (laborer/burakumin)
# mostly packs the block INTERIOR, reached by alleys, not the paved street frontage. (The towns
# set the template: businesses on the frontage via s.frontage, dwellings interior via s.pack.)


# surrounding farmland must be WORKED: the part of each outside field that SHOWS on the map
# carries farmhouses at roughly the village/hamlet linear density (~12 per 1000px of field edge,
# min ~4). Off-map field portions have their farmhouses off-screen (fine, expected), but a field
# presenting a real on-map edge with almost no farmhouses beside it is wrong - farmers build
# close to the fields they work. We count only IN-VIEW houses against the on-map field edge, so
# a partially-rendered field is held to its SHOWN extent (the gap the old per-field >=2 missed).


# the IN-WALL agricultural district (the unusual city that farms inside its walls) is REAL
# farmland too. Unlike the SURROUNDING fields above - mostly off the cropped map, so only a
# FLOOR (7) is enforceable on their shown sliver - an in-wall field sits ENTIRELY in view, so
# its WHOLE perimeter must read as worked: ring it DENSELY all the way round, not a sparse few
# on one side leaving long bare edges. Held to a much higher density (the dense end of village
# ringing). Only bites when meta(agricultural_district=True) - most cities have no in-wall fields.


# housing packs DEEP, but no GIANT cluster may be cut off from circulation: a big block of
# dwellings with no street OR alley anywhere near it has no way in or out. Deep blocks must
# be laced with gravel alleys (s.alley) so every dwelling is reachable.


# an alley must EARN its length by UNIQUELY serving dwellings. A building is credited to its
# NEAREST lane only (the one it actually fronts), exactly as empty_street_runs scores streets -
# so a lane counts only what no other lane already reaches. This catches BOTH a lane running off
# into a half-empty corner (a "lane to nowhere") AND a redundant lane laid beside or across one
# that already serves the same block (a perpendicular arm the block's spine already reaches, or a
# second lane shadowing a parallel street). Scaled to the buildings (~1 dwelling per 30px of its
# own length), so it holds at the city's dense small-footprint grain, not a fixed town pixel gap.
