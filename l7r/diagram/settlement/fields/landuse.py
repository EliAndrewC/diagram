"""The land-use overlay pass (mulberry-and-fishpond, lotus, hill tea) and its row helpers.

Split from settlement/fields.py by feature 112 - see settlement/fields/CLAUDE.md for the index.

Research: plumbing - NONE: row cutting, geometry and manifest records
"""

import math
from collections.abc import Sequence
from typing import TYPE_CHECKING

from .._knobs import Knob, register_knob

if TYPE_CHECKING:
    pass


# THE POND'S WATER INSET INSIDE ITS PARCEL (feature 280 M58, research/questions/0018-dike-ponds-fish-ponds-ringed-by-mulberry-dikes-sangji-yutang.html): 23 ft of planted dike round the
# water leaves about six parts in ten of a parcel water, the reading of Qu Dajun's figures for Jiujiang (1678) - the
# oldest there are; every ratio written as a number is modern. It was 11 ft, which left 80%, wetter than any figure read.
DIKEPOND_WATER_INSET = 23.0
"""Research: pond bank width - research/questions/0018-dike-ponds-fish-ponds-ringed-by-mulberry-dikes-sangji-yutang.drawing.html: 23 ft, the water-heavy split's inset on Kuwabata's parcels; since feature 385 T10 the inset is derived per map from the rolled split (`dikepond_inset`), and this the fallback where no parcel is known"""


# A DIKE-POND VILLAGE'S SPLIT OF WATER AND DIKE (feature 385 T10, 0018): six parts water to four of dike, six of dike to four of
# pond, seven of water to three of dike, one to one, or three of water to seven of dike - the water share of a parcel, rolled per village; the inset is derived from it
# (`fields.landuse.dikepond_inset`).
DIKEPOND_SPLIT = register_knob(Knob("dikepond_split", [0.6, 0.4, 0.7, 0.5, 0.3], default=0.6))
"""Research:
    dike-pond split values - research/questions/0018-dike-ponds-fish-ponds-ringed-by-mulberry-dikes-sangji-yutang.drawing.html: water six to four, dike six to four, water seven to three, one to one, and the gazetteer's three of water to seven of dike
    dike-pond split odds - GUESS: even odds (the record gives no share between them)"""


def dikepond_inset(polys: Sequence[Sequence[Sequence[float]]], share: float) -> float:
    """The water inset, in px, at which the map's MEDIAN parcel (by area) is `share` water: the pond is the parcel scaled about its
    centroid by `1 - inset / apothem` (`_rounded_pond`), so its share is that scale squared, and the inset is
    `apothem * (1 - sqrt(share))`. `DIKEPOND_WATER_INSET` where no parcel is known (feature 385 T10).

    Research:
        the inset from the split - research/questions/0018-dike-ponds-fish-ponds-ringed-by-mulberry-dikes-sangji-yutang.drawing.html: a parcel drawn at the rolled share water, the planted bank the ring between
        one inset per map, on its median parcel - GUESS: the share holds on the median parcel; a smaller parcel runs a little drier and a larger a little wetter"""
    if not polys:
        return DIKEPOND_WATER_INSET

    def area(q: Sequence[Sequence[float]]) -> float:
        return abs(sum(q[i][0] * q[(i + 1) % len(q)][1] - q[(i + 1) % len(q)][0] * q[i][1] for i in range(len(q)))) / 2

    q = sorted(polys, key=area)[len(polys) // 2]
    n = len(q)
    cx, cy = sum(v[0] for v in q) / n, sum(v[1] for v in q) / n
    apo = sum(math.hypot((q[i][0] + q[(i + 1) % n][0]) / 2 - cx, (q[i][1] + q[(i + 1) % n][1]) / 2 - cy) for i in range(n)) / n
    return apo * (1.0 - math.sqrt(share))


def line_cuts(poly: Sequence[Sequence[float]], px: float, py: float, dx: float, dy: float) -> list[tuple[float, float]] | None:
    """Where the line through (px, py) with direction (dx, dy) lies inside `poly`, as `[(t0, t1)]` in the line's own
    parameter - the general form of `row_cuts` for the comb's angled dry rows (feature 225 FR-004). `[]` when the
    line misses the polygon, None when it meets the edges other than twice (a concave plot keeps its clip). Each
    edge is crossed where the edge's endpoints lie on opposite sides of the line (half-open, so a vertex on the
    line counts once), the same rule as the horizontal case."""
    ts: list[float] = []
    n = len(poly)
    for i in range(n):
        (x1, y1), (x2, y2) = (poly[i][0], poly[i][1]), (poly[(i + 1) % n][0], poly[(i + 1) % n][1])
        s1 = (x1 - px) * dy - (y1 - py) * dx  # the side of the line each endpoint lies on
        s2 = (x2 - px) * dy - (y2 - py) * dx
        if (s1 > 0) != (s2 > 0):
            f = s1 / (s1 - s2)  # the crossing along the edge
            cx, cy = x1 + (x2 - x1) * f, y1 + (y2 - y1) * f
            ts.append((cx - px) * dx + (cy - py) * dy)
    if not ts:
        return []
    if len(ts) != 2:
        return None
    return [(min(ts), max(ts))]
