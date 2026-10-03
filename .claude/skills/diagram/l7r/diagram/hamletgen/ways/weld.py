"""THE CORNER WELD (feature 315, cohort seed 22): two ways that meet, drawn as though they crossed twice.

A lane's corner standing a fraction of a foot past another lane's tread closes a face of the noded lane web with next to no
area - on seed 22 a face 3.5 px long and 0.6 px across between two access corridors, one corner 0.4 px off the other's tread
(`law.needle_loops` counts it a needle of grass: it has no width). No cut opens it there, because both are tree lanes, which
no settle repair cuts, and the last resort refused the map. The two ways MEET; nothing is drawn round a sliver of grass. So
the corner is moved onto the tread it stands beside, at its nearest point, and that same point is written into the tread as
a vertex, so the two share one vertex exactly (a record keeps 0.1 px, `reshape_lane`: a corner merely moved onto the tread
would be rounded back off it). Only a SLIVER is welded - a face whose mean width is under `WELD_PX` - and only a corner
within `WELD_PX` of the other tread: a real needle, a way drawn round ground a person could stand on, is the cut's
(`settle.settle_needles`) or the tree's. A map drawing convention: the weld moves a line by under a foot.
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from typing import Any

from ..consts import Poly, Pt

#: a face narrower than this on average is a sliver of noding, not ground (px; under a foot at every map scale we draw)
WELD_PX = 2.0


def _at(p: Poly, along: float) -> tuple[int, Pt]:
    """(the index of the segment of `p` holding arc length `along`, the point there)."""
    run = 0.0
    for k in range(len(p) - 1):
        seg = math.dist(p[k], p[k + 1])
        if seg > 0 and run + seg >= along:
            t = (along - run) / seg
            return k, (p[k][0] + t * (p[k + 1][0] - p[k][0]), p[k][1] + t * (p[k + 1][1] - p[k][1]))
        run += seg
    return len(p) - 2, p[-1]


def weld_corner(lanes: Sequence[Mapping[str, Any]], face: Any, bounding: Sequence[int]) -> dict[int, Poly] | None:
    """{lane: its new points} for the two lanes bounding the sliver `face` - one lane's corner inside it moved onto the other's
    tread, and the shared point written into that tread - or None where `face` is no sliver or no corner stands within
    `WELD_PX` of the other tread."""
    from shapely.geometry import LineString, Point

    if face.length <= 0 or 2.0 * face.area / face.length >= WELD_PX:
        return None
    near = face.buffer(1.0)
    pts = {i: [(float(x), float(y)) for x, y in lanes[i].get("pts") or []] for i in bounding}
    for i in bounding:
        for k, v in enumerate(pts[i]):
            if not near.contains(Point(v)):
                continue
            for j in bounding:
                tread = pts[j]
                if j == i or len(tread) < 2:
                    continue
                seg, q = _at(tread, LineString(tread).project(Point(v)))
                at = (round(q[0], 1), round(q[1], 1))
                if not 0.0 < math.dist(v, q) <= WELD_PX:
                    continue
                moved = [*pts[i][:k], at, *pts[i][k + 1 :]]
                return {i: moved} if at in tread else {i: moved, j: [*tread[: seg + 1], at, *tread[seg + 1 :]]}
    return None
