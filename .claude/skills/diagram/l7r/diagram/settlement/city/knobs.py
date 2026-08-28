"""City knob helpers - the machi mouths and the swept moat tap (feature 145: moved out of _knobs.py, whose knob engine every map executes)."""

import math
from typing import Any

from .._geom import Pt, point_in_poly, seg_intersect, segments_cross
from .._knobs import moat_current_at


def machi_mouths(M: Any) -> list[tuple[float, float]]:
    """Every point where a town street ENTERS a machi-kind district - the ward mouths the kido
    mesh bars at night (research 021 item 6: Edo's machi-kido, Qing's zhalan; ward_style
    "mesh" has NO ward walls - the block's own gate closes its mouth). THE SINGLE SOURCE for
    both the placer (Settlement.kido_mesh) and the validator (kido_close_the_machi_mouths),
    same doctrine as bridge_carried_ways. Out-wall suburb districts are skipped: the gate
    wards live outside the curfew mesh (their bar is the city gate itself). Mouths within
    40px collapse to one (a street grazing a district corner is one entry, not two)."""
    wall = M.get("wall")
    out: list[tuple[float, float]] = []
    for d in M.get("districts", []):
        if d.get("kind") != "machi":
            continue
        poly = d["poly"]
        if wall:
            cx = sum(p[0] for p in poly) / len(poly)
            cy = sum(p[1] for p in poly) / len(poly)
            if not point_in_poly(cx, cy, wall):
                continue
        ring = [tuple(p) for p in poly] + [tuple(poly[0])]
        for st in M.get("town_streets", []):
            pts = st["pts"]
            for i in range(len(pts) - 1):
                for j in range(len(ring) - 1):
                    if not segments_cross(tuple(pts[i]), tuple(pts[i + 1]), ring[j], ring[j + 1]):
                        continue
                    xpt = seg_intersect(tuple(pts[i]), tuple(pts[i + 1]), ring[j], ring[j + 1])
                    if xpt is not None and not any(math.hypot(xpt[0] - ox, xpt[1] - oy) < 40 for ox, oy in out):
                        out.append((xpt[0], xpt[1]))
    return out


def moat_swept_tap(ring: Any, inlet: Pt, outlet: Pt, other: Pt, near: Pt, want_deg: float = 50.0, max_back: float = 220.0, arriving: bool = False) -> Pt:
    """The rim point an offtake should leave from so its throat is SWEPT DOWNSTREAM into the sluice.

    Canal practice: an offtake leaves its parent at an ACUTE angle pointing downstream - best
    alignment 0 deg separating out in transition, with the studied optimum for water and sediment at
    15-45 deg, explicitly "30 or 45 instead of 90". A square tap sheds sediment into its own mouth
    and, on the page, says nothing about which way the water runs.

    Only the MOAT-SIDE end moves. The sluice stays exactly where it is, so the comb field it feeds
    does not shift by a pixel; the throat simply becomes a diagonal from a point further upstream.
    Walks upstream by ARC LENGTH, not by vertex: a vertex step on these rings is ~140 px against a
    ~30 px throat, which overshoots past the target into a channel running nearly parallel to the
    rim. The wanted offset is a fraction of an edge (~36 px for a 30 px throat at 40 deg), so the
    walk samples every few px and takes the FIRST point that is swept enough - the nearest such
    point, keeping the tap close to the field it feeds."""
    n = len(ring)
    if n < 3:
        return near

    def ix(q: Pt) -> int:
        return min(range(n), key=lambda k: math.hypot(ring[k][0] - q[0], ring[k][1] - q[1]))

    i0, i_in, i_out = ix(near), ix(inlet), ix(outlet)
    step = 1 if (i0 - i_in) % n <= (i_out - i_in) % n else -1  # +1 where travel runs with the index
    # An OFFTAKE leaves the ring, so its rim end walks UPSTREAM and the throat (other - cand) then
    # runs with the current. A DRAIN arrives, so its landing walks DOWNSTREAM and the arriving
    # segment (cand - other) runs with the current. Same geometry, mirrored.
    if arriving:
        step = -step
        max_back = min(max_back, 90.0)  # a culvert landing must stay NEAR its drain's tail: walk too
        # far and the culvert's sink end ends up closer to the drain's HEAD than its tail, which flips
        # the outfall attribution drain_flows_downhill depends on (Nagahara's fnn2 did exactly this).

    def sweep(p: Pt) -> float:
        cur = moat_current_at(ring, inlet, outlet, p)
        vx, vy = (p[0] - other[0], p[1] - other[1]) if arriving else (other[0] - p[0], other[1] - p[1])
        L = math.hypot(vx, vy)
        if cur is None or L == 0:
            return 999.0
        return math.degrees(math.acos(max(-1.0, min(1.0, (vx * cur[0] + vy * cur[1]) / L))))

    best, best_ang, walked, cur_i = near, sweep(near), 0.0, i0
    while walked < max_back:
        a, b = ring[cur_i % n], ring[(cur_i - step) % n]  # the edge running UPSTREAM from here
        seg = math.hypot(b[0] - a[0], b[1] - a[1])
        if seg == 0:
            cur_i -= step
            continue
        t = 0.0
        while t < seg and walked < max_back:
            t, walked = t + 5.0, walked + 5.0
            f = min(1.0, t / seg)
            cand = (a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f)
            ang = sweep(cand)
            if ang < best_ang:
                best, best_ang = cand, ang
            if ang <= want_deg:
                return (round(cand[0], 1), round(cand[1], 1))
        cur_i -= step
    return (round(best[0], 1), round(best[1], 1))
