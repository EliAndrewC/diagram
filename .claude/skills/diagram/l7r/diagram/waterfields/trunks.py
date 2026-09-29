"""The comb's trunk ditches - its main canals and its collector - as the rules read them (feature 287, water W13-W15).

Three finished-map tests used to measure a comb's trunks after the map was drawn: the collector discharges at its
lowest point (`test_a_collector_discharges_at_its_lowest_point`), it never turns a hard corner
(`test_the_runoff_curves_out_of_the_collector`), and no trunk end stops in bare ground
(`test_no_watercourse_end_dangles_in_bare_ground`). Each is a property the comb builder DECIDES, so each is written once
here, as the predicate the builder is held to (`comb.py`) and the test calls. Split out of `comb.py`, which sits at the
1,000-line bar, rather than grown past it.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from typing import Any

from .frame import Poly, Pt, _pip

DRAIN_MIN_LEG = 84.0
"""The shortest leg the collector is drawn with into its outfall, px (water W13, W14). The drain is sampled at 120-170 px
steps with a +/-6 px fall jitter along a line falling 0.06-0.35 px per px, and the last sample used to land anywhere
short of the outfall - 2 px short on a bad draw, where the jitter turned the last leg back on itself (the 'short hook').

Two bounds set the figure, both by construction rather than by luck. THE TURN (W14): with every leg at least this long,
a leg's slope lies within +/-12/84 of the fitted line's, so no two legs meet at more than ~40 deg, far under the 100 the
rule forbids. THE FALL (W13): a sample this far short of the outfall sits at least 0.06 x 84 = 5.04 px up the fitted line
from it, more than its 6 px jitter less the 1 px slack - so EVERY point of the collector, not only its head, lies no more
than 1 px below the outfall, and the rule still holds if `trunks.anchor_trunk_ends` has to walk the head back."""

SHARP_TURN_DEG = 100.0
"""The collector turns at a hard corner at or past this: the water would pile against the far bank rather than take it
(`drainage_junction_smooth`)."""

UPHILL_SLACK = 1.0
"""How far the outfall may sit up the fall from the head, px: a collector runs cross-slope, so its ends may sit at nearly
one height; what is forbidden is an outfall measurably UPHILL (`drain_flows_downhill`)."""

JOIN_TOL = 14.0
"""How near a trunk end must come to another course to count as joining it (`watercourse_ends_reach_water`)."""

CROP_TOL = 2.0
"""A trunk end at or within this of the crop it feeds has reached what it was dug for - the canal arriving, not
dangling."""

FRAME_TOL = 1.0
"""An end within this of the frame edge runs off the map."""


def _seg_dist(p: Pt, a: Pt, b: Pt) -> float:
    vx, vy = b[0] - a[0], b[1] - a[1]
    L2 = vx * vx + vy * vy
    t = 0.0 if L2 == 0 else max(0.0, min(1.0, ((p[0] - a[0]) * vx + (p[1] - a[1]) * vy) / L2))
    return math.hypot(p[0] - (a[0] + t * vx), p[1] - (a[1] + t * vy))


def _poly_dist(p: Pt, poly: Sequence[Pt]) -> float:
    return min((_seg_dist(p, poly[i], poly[i + 1]) for i in range(len(poly) - 1)), default=math.inf)


def outfall_rise(pts: Sequence[Sequence[float]], down_deg: float) -> float:
    """How far the collector's outfall (`pts[-1]`) sits DOWN the fall from its head (`pts[0]`), px - negative where it
    sits uphill. The rule (W13) is `outfall_rise(...) >= -UPHILL_SLACK`."""
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


def end_anchored(end: Pt, crops: Sequence[Sequence[Pt]], others: Sequence[Sequence[Pt]], W: float, H: float) -> bool:
    """Whether a trunk end has somewhere for its water to go (W15): off the frame, at or inside a crop it feeds, or
    within `JOIN_TOL` of another course. (The finished-map test also passes an end in the source pond; the comb cannot
    see the pond, and the one end that meets it - the head race's sluice - is anchored by the source drawn there.)"""
    if end[0] <= FRAME_TOL or end[1] <= FRAME_TOL or end[0] >= W - FRAME_TOL or end[1] >= H - FRAME_TOL:
        return True
    if any(_pip(end[0], end[1], list(ring)) or _poly_dist(end, [*ring, ring[0]]) <= CROP_TOL for ring in crops if len(ring) >= 3):
        return True
    return any(_poly_dist(end, o) <= JOIN_TOL for o in others if len(o) >= 2)


def _clip_to_anchor(pts: Poly, crops: Sequence[Sequence[Pt]], others: Sequence[Sequence[Pt]], W: float, H: float) -> Poly | None:
    """`pts` with its LAST end walked back along the course, in 1 px steps, to the first point that is anchored - the
    water stopping where it reaches the crop instead of running on into bare ground. None where no point of the course
    is anchored at all."""
    for i in range(len(pts) - 1, 0, -1):
        a, b = pts[i], pts[i - 1]
        n = max(1, math.ceil(math.dist(a, b)))
        for k in range(n + 1):
            q = (a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n)
            if end_anchored(q, crops, others, W, H):
                return [*pts[:i], q] if k < n else list(pts[:i])
    return None


def anchor_trunk_ends(channels: list[dict[str, Any]], envelope: Poly, W: float, H: float) -> None:
    """Hold every trunk end of a comb to W15, in place: each main-canal and collector end that is not anchored is clipped
    back along its own course to where it reaches the crop (the fan's envelope), another channel, or the frame edge.

    Two ends are the business of what lies beyond the comb and are left alone: the head race's first point, the sluice
    the source is drawn at (`draw_comb_field` puts the tameike or the feeder brook there), and the collector's outfall,
    which the sink continues (`hamletgen/sink.py`, water W10-W12). A trunk no point of which is anchored carries water
    from nowhere to nowhere and is dropped - never drawn dangling."""
    crops = [envelope]
    drop: list[int] = []
    for k, c in enumerate(channels):
        if c.get("role") not in ("main", "drain") or len(c["pts"]) < 2:
            continue
        others = [o["pts"] for j, o in enumerate(channels) if j != k and j not in drop]
        pts: Poly | None = list(c["pts"])
        for at_head in (True, False):
            if pts is None or (at_head and k == 0) or (not at_head and c["role"] == "drain"):
                continue  # the sluice and the outfall: see the docstring
            course = pts[::-1] if at_head else pts
            if end_anchored(course[-1], crops, others, W, H):
                continue
            clipped = _clip_to_anchor(course, crops, others, W, H)
            pts = None if clipped is None or len(clipped) < 2 else (clipped[::-1] if at_head else clipped)
        if pts is None:
            drop.append(k)
        else:
            c["pts"][:] = pts  # IN PLACE: the builder holds the collector's list as `dpts` too, and both must see the clip
    for k in reversed(drop):
        del channels[k]
