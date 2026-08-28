"""Gate segments (city torii and estate grounds; keys 0563_334-0563_376) - bodies verbatim, registry order preserved."""

import math
from typing import Any

from .common_01_geometry import Pt, point_in_poly, seg_dist, segments_cross
from .common_03_capacity import _UNBOUND, _kept

# the street network must be CONNECTED - one coherent grid wired to the Imperial
# road, not isolated stubs (ported from the town "no street to nowhere" thinking).


def _seg_0563_334__streets(*, M: Any = _UNBOUND, meta: Any = _UNBOUND, scale: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 563.334 (streets) - body verbatim from the city mega-segment (feature 023; guards preserved, see research.md R2/R3)."""
    if scale in ('city', 'capital') and meta.get('walled'):
        streets = M.get("town_streets", [])
    return _kept(locals(), ('streets',))


def _seg_0563_335__city_streets_connected(
    *,
    M: Any = _UNBOUND,
    _w21: Any = _UNBOUND,
    a: Any = _UNBOUND,
    ai: Any = _UNBOUND,
    beds_meet: Any = _UNBOUND,
    bi: Any = _UNBOUND,
    check: Any = _UNBOUND,
    comps: Any = _UNBOUND,
    end: Any = _UNBOUND,
    find2: Any = _UNBOUND,
    i: Any = _UNBOUND,
    ia: Any = _UNBOUND,
    ib: Any = _UNBOUND,
    k: Any = _UNBOUND,
    ki: Any = _UNBOUND,
    meta: Any = _UNBOUND,
    nbr: Any = _UNBOUND,
    near_miss: Any = _UNBOUND,
    parent: Any = _UNBOUND,
    q21: Any = _UNBOUND,
    sa: Any = _UNBOUND,
    sb: Any = _UNBOUND,
    scale: Any = _UNBOUND,
    seg_seg_dist: Any = _UNBOUND,
    slines: Any = _UNBOUND,
    sseg: Any = _UNBOUND,
    st: Any = _UNBOUND,
    streets: Any = _UNBOUND,
    stub: Any = _UNBOUND,
    tol: Any = _UNBOUND,
    widths: Any = _UNBOUND,
) -> dict[str, Any]:
    """Gate segment 563.335 (city_streets_connected, city_streets_no_intersection_stub, city_streets_no_near_miss) - body verbatim from the city mega-segment (feature 023; guards preserved, see research.md R2/R3)."""
    if scale in ('city', 'capital'):  # noqa: SIM102
        if meta.get('walled'):  # noqa: SIM102
            if streets:
                # at the CAPITAL the suburb streets (wholly outside the rampart - the kashi
                # quay street) are their own lawful networks reached through the gates; the
                # connectivity rule binds the IN-WALL grid (021)
                if scale == "capital" and len(M.get("wall") or []) >= 3:
                    _w21 = M["wall"]
                    streets = [st for st in streets if any(point_in_poly(q21[0], q21[1], _w21) for q21 in st["pts"])]
                sseg = [st["pts"] for st in streets] + ([M["road"]] if M.get("road") else [])
                # width of each segment's paved bed (the road counts as a street here): two streets
                # are CONNECTED only if you can walk between them, i.e. their beds actually overlap -
                # centerline gap < the sum of their half-widths. A street whose end stops even a roadbed
                # short of the next one is a SEPARATE network (you cannot step from one to the other),
                # which is exactly the laborer grid that ended 40px shy of the Imperial road. (Kido ward
                # gates do NOT break this: the street centerline runs on under the gate, uninterrupted.)
                widths = [st.get("w", 18) for st in streets] + ([M.get("road_width", 26)] if M.get("road") else [])
                parent = list(range(len(sseg)))

                def find2(a: int) -> int:
                    while parent[a] != a:
                        parent[a] = parent[parent[a]]
                        a = parent[a]
                    return a

                def beds_meet(ia: int, ib: int) -> bool:  # beds overlap: segments cross, or a centerline endpoint lies
                    sa, sb = sseg[ia], sseg[ib]  # within the two beds' combined half-widths (+2px slack)
                    tol = widths[ia] / 2 + widths[ib] / 2 + 2
                    for i in range(len(sa) - 1):
                        for k in range(len(sb) - 1):
                            if segments_cross(sa[i], sa[i + 1], sb[k], sb[k + 1]):
                                return True
                            if (
                                seg_dist(sa[i][0], sa[i][1], sb[k], sb[k + 1]) < tol
                                or seg_dist(sa[i + 1][0], sa[i + 1][1], sb[k], sb[k + 1]) < tol
                                or seg_dist(sb[k][0], sb[k][1], sa[i], sa[i + 1]) < tol
                                or seg_dist(sb[k + 1][0], sb[k + 1][1], sa[i], sa[i + 1]) < tol
                            ):
                                return True
                    return False

                for ai in range(len(sseg)):
                    for bi in range(ai + 1, len(sseg)):
                        if beds_meet(ai, bi):
                            parent[find2(ai)] = find2(bi)
                comps = {find2(i) for i in range(len(streets))}
                pass  # `` retired under feature 141 (the GM's cut); the segment stays for the check it keeps or the value it writes

                # two streets that come ALMOST together without meeting read as a mistake - they
                # should either JOIN (cross/touch) or stay clearly apart, never leave a sliver gap
                def seg_seg_dist(a0: Pt, a1: Pt, b0: Pt, b1: Pt) -> float:
                    return min(seg_dist(a0[0], a0[1], b0, b1), seg_dist(a1[0], a1[1], b0, b1), seg_dist(b0[0], b0[1], a0, a1), seg_dist(b1[0], b1[1], a0, a1))

                slines = [st["pts"] for st in streets]
                near_miss = set()
                for ia in range(len(slines)):
                    for ib in range(ia + 1, len(slines)):
                        for i in range(len(slines[ia]) - 1):
                            for ki in range(len(slines[ib]) - 1):
                                if segments_cross(slines[ia][i], slines[ia][i + 1], slines[ib][ki], slines[ib][ki + 1]):
                                    continue
                                if 2 < seg_seg_dist(slines[ia][i], slines[ia][i + 1], slines[ib][ki], slines[ib][ki + 1]) < 30:
                                    near_miss.add((ia, ib))
                pass  # `` retired under feature 141 (the GM's cut); the segment stays for the check it keeps or the value it writes
                # a street that crosses another and then STOPS a little way past it leaves an ugly
                # dangling stub. Fine to cross and keep going (to the next block/edge), or to
                # terminate AT the junction (an L/T corner), but not to overshoot it by a sliver.
                stub = set()
                for ia, sa in enumerate(slines):
                    for end, nbr in ((sa[0], sa[1]), (sa[-1], sa[-2])):
                        for ib, sb in enumerate(slines):
                            if ib == ia:
                                continue
                            for ki in range(len(sb) - 1):
                                if segments_cross(nbr, end, sb[ki], sb[ki + 1]) and 3 < seg_dist(end[0], end[1], sb[ki], sb[ki + 1]) < 50:
                                    stub.add((ia, ib))
                pass  # `` retired under feature 141 (the GM's cut); the segment stays for the check it keeps or the value it writes
    return _kept(
        locals(),
        (
            '_w21',
            'ai',
            'beds_meet',
            'bi',
            'comps',
            'end',
            'find2',
            'i',
            'ia',
            'ib',
            'ki',
            'nbr',
            'near_miss',
            'parent',
            'q21',
            'sa',
            'sb',
            'seg_seg_dist',
            'slines',
            'sseg',
            'st',
            'streets',
            'stub',
            'widths',
        ),
    )


# a temple a city street runs UP TO (a street that terminates at its front) marks a
# sacred approach - it needs torii arches on that street, just in front of the temple


def _seg_0563_336__torii(*, M: Any = _UNBOUND, meta: Any = _UNBOUND, scale: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 563.336 (torii) - body verbatim from the city mega-segment (feature 023; guards preserved, see research.md R2/R3)."""
    if scale in ('city', 'capital') and meta.get('walled'):
        torii = M.get("torii", [])
    return _kept(locals(), ('torii',))


def _seg_0563_337__pt_rect(*, dx: Any = _UNBOUND, dy: Any = _UNBOUND, meta: Any = _UNBOUND, px: Any = _UNBOUND, py: Any = _UNBOUND, scale: Any = _UNBOUND, t: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 563.337 (pt_rect) - body verbatim from the city mega-segment (feature 023; guards preserved, see research.md R2/R3)."""
    if scale in ('city', 'capital') and meta.get('walled'):

        def pt_rect(px: float, py: float, t: dict[str, Any]) -> float:
            dx = max(t["x"] - t["w"] / 2 - px, 0, px - t["x"] - t["w"] / 2)
            dy = max(t["y"] - t["h"] / 2 - py, 0, py - t["y"] - t["h"] / 2)
            return math.hypot(dx, dy)

    return _kept(locals(), ('pt_rect',))


def _seg_0563_338__no_torii(*, meta: Any = _UNBOUND, scale: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 563.338 (no_torii) - body verbatim from the city mega-segment (feature 023; guards preserved, see research.md R2/R3)."""
    if scale in ('city', 'capital') and meta.get('walled'):
        no_torii = []  # type: ignore[var-annotated]
    return _kept(locals(), ('no_torii',))


def _seg_0563_339__e_2(
    *,
    M: Any = _UNBOUND,
    e: Any = _UNBOUND,
    meta: Any = _UNBOUND,
    no_torii: Any = _UNBOUND,
    pt_rect: Any = _UNBOUND,
    r: Any = _UNBOUND,
    runs_up: Any = _UNBOUND,
    scale: Any = _UNBOUND,
    st: Any = _UNBOUND,
    t: Any = _UNBOUND,
    to: Any = _UNBOUND,
    torii: Any = _UNBOUND,
) -> dict[str, Any]:
    """Gate segment 563.339 (e, no_torii, r, runs_up) - body verbatim from the city mega-segment (feature 023; guards preserved, see research.md R2/R3)."""
    if scale in ('city', 'capital') and meta.get('walled'):
        for t in [r for r in M.get("religious", []) if r.get("kind") == "temple"]:
            runs_up = any(min(pt_rect(e[0], e[1], t) for e in (st["pts"][0], st["pts"][-1])) < 28 for st in M.get("town_streets", []))
            if runs_up and not any(math.hypot(to[0] - t["x"], to[1] - t["y"]) < 95 for to in torii):
                no_torii.append(t.get("label"))
    return _kept(locals(), ('e', 'no_torii', 'r', 'runs_up', 'st', 't', 'to'))


# (RETIRED 2026-07-24: city_temple_torii_fill_approach - "an avenue with open room takes
# another arch" - is superseded by the per-temple seeded ROLL: shrine_hall now rolls each
# hall's count on the tier's TORII_WEIGHTS column and records the target on the religious
# rec, so avenue completeness is defined by the roll, not by remaining street room. A
# rolled 1 beside an open street is a hall with one patron gate, not an unfinished avenue.
# torii_match_roll (with torii_count_canonical) now carries the teeth. Same precedent as
# torii_full_avenue_is_seven's retirement when the numerology rule landed.)
# a torii arch stands OVER the street it spans - the street passes beneath it - so a
# torii sitting on a street must be drawn after (higher z than) that street, not under it


def _seg_0563_341__to_under(*, meta: Any = _UNBOUND, scale: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 563.341 (to_under) - body verbatim from the city mega-segment (feature 023; guards preserved, see research.md R2/R3)."""
    if scale in ('city', 'capital') and meta.get('walled'):
        to_under = []  # type: ignore[var-annotated]
    return _kept(locals(), ('to_under',))


def _seg_0563_342__i_5(
    *, M: Any = _UNBOUND, i: Any = _UNBOUND, meta: Any = _UNBOUND, scale: Any = _UNBOUND, sp: Any = _UNBOUND, st: Any = _UNBOUND, t: Any = _UNBOUND, to_under: Any = _UNBOUND, torii: Any = _UNBOUND
) -> dict[str, Any]:
    """Gate segment 563.342 (i, sp, st, t) - body verbatim from the city mega-segment (feature 023; guards preserved, see research.md R2/R3)."""
    if scale in ('city', 'capital') and meta.get('walled'):
        for t in torii:
            for st in M.get("town_streets", []):
                sp = st["pts"]
                if any(seg_dist(t[0], t[1], sp[i], sp[i + 1]) <= st.get("w", 24) / 2 + 12 for i in range(len(sp) - 1)) and t[2] <= st.get("z", 0):
                    to_under.append((t[0], t[1]))
    return _kept(locals(), ('i', 'sp', 'st', 't', 'to_under'))


# no LARGE empty swath inside the walls (ported from wall_hugs_the_town; REBUILT
# footprint-aware, GM 2026-07-23, after Tango shipped a ~230x95px bare pocket just
# inside its north gate that read fully green). The old detector sampled an 80px grid
# and called a cell "used" within 120px of any building CENTER - a single house
# sanitized a 240px-wide disc, so only vast voids could ever fire. Now every claiming
# feature counts with its real FOOTPRINT: building/compound/grove rects, field and
# ground polys, well / stable-yard / torii discs, the road / street / alley / ring-road
# / water rights-of-way, ward fences, the rampart + its patrol strip, and the pond. A
# 32px grid marks cells >= 20px clear of ALL of them as dead ground; any contiguous
# dead cluster >= 4,000 px2 of core fails. Calibration (2026-07-23, pool-wide dry-run,
# settlements.md): Tango's north-gate pocket measures 6,144 px2 of core; the largest
# LEGITIMATE opens anywhere else measure 2,048 (Tango) / 1,024 (Nagahara), so the
# threshold sits between with ~2x headroom both ways. A city keeps SOME open ground,
# but every deliberate open is CLAIMED by a feature record (a working stable yard /
# animal ground, a right-of-way, a field); ground claimed by nothing, at
# wall-protected premium, would not have been left bare.


# the CITADEL claims its ground (021): a castle court is deliberately BLANK (the
# sync doctrine) - blank is not unclaimed, and its moat band goes with it
