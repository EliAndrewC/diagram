"""Gate segments (city streets and docks; keys 0563_309-0563_333) - bodies verbatim, registry order preserved."""

import math
from typing import Any

from .common_01_geometry import Pt, point_in_poly, seg_dist
from .common_03_capacity import _UNBOUND, _kept

# the Imperial-road label must sit OUTSIDE the walls (inside, the roadway is a city street)


# ROADSIDE LAND on a larger city street is PRIME real estate: a paved through-street in a
# commercial/residential quarter must be LINED with buildings (houses, shops, civic halls)
# close to it, not left with a long bare margin. This is stricter than city_streets_have_buildings
# (which tolerates a building up to ~105px away): here a building must sit WITHIN ~58px of the
# street, the way storefronts and house-fronts actually line a road. Only the narrow gravel
# ALLEYS that thread the block interiors are exempt (those are the "small streets" that need no
# frontage), and so is the GOVERNMENT avenue - its frontage is the spaced ministry compounds,
# governed by city_ministries_front_a_street, not shops/houses. (The merchant avenue once read
# bare because its storefront frontage was silently blocked by the avenue's own corridor.)


def _seg_0563_314__line_blds(*, M: Any = _UNBOUND, gov: Any = _UNBOUND, meta: Any = _UNBOUND, scale: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 563.314 (line_blds) - body verbatim from the city mega-segment (feature 023; guards preserved, see research.md R2/R3)."""
    if scale in ('city', 'capital') and meta.get('walled'):
        line_blds = M.get("buildings", []) + M.get("religious", []) + M.get("ministries", []) + M.get("flophouses", []) + ([gov] if gov else [])
    return _kept(locals(), ('line_blds',))


def _seg_0563_315__gov_pts(*, M: Any = _UNBOUND, gov: Any = _UNBOUND, meta: Any = _UNBOUND, scale: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 563.315 (gov_pts) - body verbatim from the city mega-segment (feature 023; guards preserved, see research.md R2/R3)."""
    if scale in ('city', 'capital') and meta.get('walled'):
        gov_pts = M.get("ministries", []) + ([gov] if gov else [])
    return _kept(locals(), ('gov_pts',))


def _seg_0563_316__LINE_D(*, meta: Any = _UNBOUND, scale: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 563.316 (LINE_D, LINE_RUN) - body verbatim from the city mega-segment (feature 023; guards preserved, see research.md R2/R3)."""
    if scale in ('city', 'capital') and meta.get('walled'):
        LINE_D, LINE_RUN = 58, 140
    return _kept(locals(), ('LINE_D', 'LINE_RUN'))


def _seg_0563_317__bare_streets(*, meta: Any = _UNBOUND, scale: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 563.317 (bare_streets) - body verbatim from the city mega-segment (feature 023; guards preserved, see research.md R2/R3)."""
    if scale in ('city', 'capital') and meta.get('walled'):
        bare_streets = []  # type: ignore[var-annotated]
    return _kept(locals(), ('bare_streets',))


def _seg_0563_318___lg_open(
    *,
    LINE_D: Any = _UNBOUND,
    LINE_RUN: Any = _UNBOUND,
    M: Any = _UNBOUND,
    _lg_open: Any = _UNBOUND,
    a: Any = _UNBOUND,
    b: Any = _UNBOUND,
    bare_streets: Any = _UNBOUND,
    bl: Any = _UNBOUND,
    cg9: Any = _UNBOUND,
    gov_pts: Any = _UNBOUND,
    gp9: Any = _UNBOUND,
    i: Any = _UNBOUND,
    i9: Any = _UNBOUND,
    j: Any = _UNBOUND,
    ki: Any = _UNBOUND,
    line_blds: Any = _UNBOUND,
    m: Any = _UNBOUND,
    meta: Any = _UNBOUND,
    pts: Any = _UNBOUND,
    run: Any = _UNBOUND,
    scale: Any = _UNBOUND,
    st: Any = _UNBOUND,
    steps: Any = _UNBOUND,
    t: Any = _UNBOUND,
    w: Any = _UNBOUND,
    worst: Any = _UNBOUND,
    x: Any = _UNBOUND,
    y: Any = _UNBOUND,
) -> dict[str, Any]:
    """Gate segment 563.318 (_lg_open, a, b, bare_streets) - body verbatim from the city mega-segment (feature 023; guards preserved, see research.md R2/R3)."""
    if scale in ('city', 'capital') and meta.get('walled'):
        for st in M.get("town_streets", []):
            pts = st["pts"]
            if sum(1 for m in gov_pts if min(seg_dist(m["x"], m["y"], pts[i], pts[i + 1]) for i in range(len(pts) - 1)) < 70) >= 2:
                continue  # a government avenue - lined by ministry compounds
            worst = run = 0
            for ki in range(len(pts) - 1):
                a, b = pts[ki], pts[ki + 1]
                steps = max(1, int(math.hypot(b[0] - a[0], b[1] - a[1]) // 20))
                for j in range(steps):
                    t = j / steps
                    x, y = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
                    _lg_open = any(
                        point_in_poly(x, y, gp9) or min(seg_dist(x, y, gp9[i9], gp9[(i9 + 1) % len(gp9)]) for i9 in range(len(gp9))) < 70
                        for gp9 in (cg9["poly"] for cg9 in M.get("commons", []) if cg9.get("poly"))
                    )  # open-ground frontage (commons/pasture): same exemption as empty_street_runs (021)
                    if not point_in_poly(x, y, w) or any((bl["x"] - x) ** 2 + (bl["y"] - y) ** 2 < LINE_D * LINE_D for bl in line_blds) or _lg_open:
                        run = 0
                    else:
                        run += 20
                        worst = max(worst, run)
            if worst > LINE_RUN:
                bare_streets.append(("main" if st.get("main") else f"@{(round(pts[0][0]), round(pts[0][1]))}", worst))
    return _kept(locals(), ('_lg_open', 'a', 'b', 'bare_streets', 'bl', 'cg9', 'gp9', 'i', 'i9', 'j', 'ki', 'm', 'pts', 'run', 'st', 'steps', 't', 'worst', 'x', 'y'))


def _seg_0563_320__road_1(*, M: Any = _UNBOUND, meta: Any = _UNBOUND, scale: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 563.320 (road) - body verbatim from the city mega-segment (feature 023; guards preserved, see research.md R2/R3)."""
    if scale in ('city', 'capital') and meta.get('walled'):
        road = M.get("road") or []
    return _kept(locals(), ('road',))


def _seg_0563_321__city_imperial_road_through(
    *,
    EX0: Any = _UNBOUND,
    EX1: Any = _UNBOUND,
    EY0: Any = _UNBOUND,
    EY1: Any = _UNBOUND,
    M: Any = _UNBOUND,
    check: Any = _UNBOUND,
    dead: Any = _UNBOUND,
    e: Any = _UNBOUND,
    exits: Any = _UNBOUND,
    meta: Any = _UNBOUND,
    offend: Any = _UNBOUND,
    p: Any = _UNBOUND,
    r: Any = _UNBOUND,
    rds: Any = _UNBOUND,
    road: Any = _UNBOUND,
    road_through: Any = _UNBOUND,
    scale: Any = _UNBOUND,
) -> dict[str, Any]:
    """Gate segment 563.321 (city_imperial_road_through, city_roads_run_offmap) - body verbatim from the city mega-segment (feature 023; guards preserved, see research.md R2/R3)."""
    if scale in ('city', 'capital') and meta.get('walled'):
        if meta.get("imperial_road", True):
            road_through = bool(road) and any(p[1] < EY0 for p in road) and any(p[1] > EY1 for p in road)
            pass  # `` retired under feature 141 (the GM's cut); the segment stays for the check it keeps or the value it writes
        else:
            # NO Imperial road (it passes miles away): the city still lives on through-traffic,
            # so its road net must leave the map in at least TWO directions (one polyline
            # bending through the city - off-map N, through the gates, off-map SE - counts
            # as two; a dead-end road serves nobody)
            rds = [r["pts"] for r in M.get("roads", [])] or ([road] if road else [])

            def offend(p: Pt) -> bool:
                return p[0] < EX0 or p[0] > EX1 or p[1] < EY0 or p[1] > EY1  # type: ignore[no-any-return]

            exits = sum(1 for r in rds for e in (r[0], r[-1]) if offend(e))
            dead = [(round(e[0]), round(e[1])) for r in rds for e in (r[0], r[-1]) if not offend(e)]
            pass  # `` retired under feature 141 (the GM's cut); the segment stays for the check it keeps or the value it writes
    return _kept(locals(), ('dead', 'e', 'exits', 'offend', 'p', 'r', 'rds', 'road_through'))


# INTRAMURAL groves OFF: a farm inside the wall carries NO windbreak grove - an in-wall plot is not
# an isolated farmstead (the urban fabric already breaks the wind) and sits on land too precious for
# a tree belt. So the in-wall agricultural district stays grove-free. WHY: settlements.md "Homestead groves".


def _seg_0563_324__moat_2(*, M: Any = _UNBOUND, meta: Any = _UNBOUND, scale: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 563.324 (moat) - body verbatim from the city mega-segment (feature 023; guards preserved, see research.md R2/R3)."""
    if scale in ('city', 'capital') and meta.get('walled'):
        moat = M.get("moat")
    return _kept(locals(), ('moat',))


# RIVER-CITY WATERWORKS (a cargo canal + wharf; only where they are drawn):


# (1) THE CANAL CONNECTS THE DOCK TO THE WATER, like a street reaching the road: one end
# taps the river OR hands off to the moat (the Suzhou shared-mouth pattern - the city's
# canals communicate with the MOAT, and the moat's own downstream river junction is the
# navigation entrance), the other feeds the in-city dock basin - a canal that stops short
# of the dock is a ditch to nowhere (GM, 2026-07: Nagahara's canal left a visible gap to
# the dock). "Reaches" = the end's bed physically meets the target (within the target's
# half-extent + the canal half-width + a small tolerance).


# (2) THE WHARF JETTIES REACH THE BANK: a jetty is a finger running out from the river's
# near bank into the water - its landward end must TOUCH the bank, not float mid-stream
# (GM, 2026-07: Nagahara's jetties floated in the middle of the river). The near bank is
# the river centerline offset by half its width toward the city; a jetty's nearest end
# must sit within ~14px of it.


# (3) THE LOG BOOM IS A SHORE-FAST PEN, NOT STICKS IN THE STREAM (GM 2026-08-02, "it
# just looks like a bunch of logs in the middle of the river"; the research is in
# research/urban-features.md "The log boom"). A boom is a floating fence - anchored to
# nothing it holds nothing. Attested booms anchor to the bank and run ALONG a navigated
# river, the pen between chain and shore (Susquehanna: seven miles along one side;
# St. Croix: log channels beside a navigation channel kept clear by statute); only a
# loose-log CATCH boom on an unnavigated reach ever spans the water (the Kiso tsunaba
# at the gorge mouth), never a port's holding pen. GAP-VERDICT family: both rules below
# measure the pen's DERIVED CORNERS (x/y/rot/len/pen_w, the same local frame the glyph
# draws - bank on local +y) against the river's stroked centerline; a center measure
# would condemn the good bank-hugging pen and pass the mid-stream chain (see the test
# pair). pen_w defaults to the ~14px the pre-2026-08 chain glyph drew.
