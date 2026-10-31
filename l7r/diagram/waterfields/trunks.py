"""The comb's trunk ditches - its main canals and its collector - as the rules read them (feature 287, water W13-W15).

Three finished-map tests used to measure a comb's trunks after the map was drawn: the collector discharges at its
lowest point (`test_a_collector_discharges_at_its_lowest_point`), it never turns a hard corner
(`test_the_runoff_curves_out_of_the_collector`), and no trunk end stops in bare ground
(`test_no_watercourse_end_dangles_in_bare_ground`). Each is a property the comb builder DECIDES, so each is written once
here, as the predicate the builder is held to (`comb.py`) and the test calls. Split out of `comb.py`, which sits at the
1,000-line bar, rather than grown past it.

Research: trunk geometry - NONE: distances, turn measures and join tolerances
"""

from __future__ import annotations

import math
from collections.abc import Sequence

from l7r.diagram.work_counts import OPS

from .frame import Pt

SHARP_TURN_DEG = 100.0
"""The collector turns at a hard corner at or past this: the water would pile against the far bank rather than take it
(`drainage_junction_smooth`).

Research: no hard corner on the collector - GUESS: no source could speak to it, a value of ours (feature 417 T36 pass P2b, 2026-10-25); a turn of 100 deg or more is refused, water piling against the far bank
"""

UPHILL_SLACK = 1.0
"""How far the outfall may sit up the fall from the head, px: a collector runs cross-slope, so its ends may sit at nearly
one height; what is forbidden is an outfall measurably UPHILL (`drain_flows_downhill`).

Research: outfall not uphill - research/questions/0060-field-drains-akusuiro.drawing.html: the outfall may sit no more than 1 px up the fall from the head
"""

JOIN_TOL = 14.0
"""How near a trunk end must come to another course to count as joining it (`watercourse_ends_reach_water`)."""


def _seg_dist(p: Pt, a: Pt, b: Pt) -> float:
    if __debug__:
        OPS["dist@_seg_dist"] += 1  # the counted work (feature 443)
    vx, vy = b[0] - a[0], b[1] - a[1]
    L2 = vx * vx + vy * vy
    t = 0.0 if L2 == 0 else max(0.0, min(1.0, ((p[0] - a[0]) * vx + (p[1] - a[1]) * vy) / L2))
    return math.hypot(p[0] - (a[0] + t * vx), p[1] - (a[1] + t * vy))


def outfall_rise(pts: Sequence[Sequence[float]], down_deg: float) -> float:
    """How far the collector's outfall (`pts[-1]`) sits DOWN the fall from its head (`pts[0]`), px - negative where it
    sits uphill. The rule (W13) is `outfall_rise(...) >= -UPHILL_SLACK`.

    Research: water only moves downhill - research/questions/0060-field-drains-akusuiro.drawing.html: the outfall's rise down the fall from the head
    """
    dx, dy = math.cos(math.radians(down_deg)), math.sin(math.radians(down_deg))
    return (float(pts[-1][0]) - float(pts[0][0])) * dx + (float(pts[-1][1]) - float(pts[0][1])) * dy


def sharpest_turn(pts: Sequence[Sequence[float]]) -> float:
    """The sharpest turn at any interior vertex of a polyline, degrees (0 straight on, 180 straight back); a vertex with
    a zero-length leg turns nothing. The rule (W14) is `sharpest_turn(collector) < SHARP_TURN_DEG`."""
    out = 0.0
    for k in range(1, len(pts) - 1):
        v1 = (float(pts[k][0]) - float(pts[k - 1][0]), float(pts[k][1]) - float(pts[k - 1][1]))
        v2 = (float(pts[k + 1][0]) - float(pts[k][0]), float(pts[k + 1][1]) - float(pts[k][1]))
        n1, n2 = math.hypot(*v1), math.hypot(*v2)
        if n1 < 1e-6 or n2 < 1e-6:
            continue
        out = max(out, math.degrees(math.acos(max(-1.0, min(1.0, (v1[0] * v2[0] + v1[1] * v2[1]) / (n1 * n2))))))
    return out
