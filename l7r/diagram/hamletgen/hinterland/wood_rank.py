"""Where a village's fuel wood ranks (269 B27, feature 328): the field ground's edge sampled once, the height of the field
beside a seat, the houses' floor and the rank itself. Lifted out of `parcels.py` at the 1,000-line bar (feature 328);
`parcels` re-exports every name.

Research: plumbing - NONE: the ranking's helpers
"""

import math
from collections.abc import Sequence

from ..consts import Poly, Pt

_EDGE_SAMPLE = 30.0  # px between the samples `crop_edge_points` takes along a field edge: a third of the scan's 90 px lattice


class FieldEdge:
    """The field ground's edge, sampled: each sample's x, y and height up the fall held as arrays, so the field beside a seat
    is one vector pass (feature 328 batch 3's pair: asked of the PointGrid sample by sample, `field_height_near` took 9 of a
    40-household hinterland's 13 profiled seconds, 9.9 million distances; the same answer, read whole)."""

    def __init__(self, pts: Sequence[Pt]) -> None:
        import numpy as np  # bound here, not at import (feature 237: no heavy library at import time)

        self.xy = np.array(pts, dtype=float).reshape(-1, 2)


def crop_edge_points(crops: Sequence[Poly], every: float = _EDGE_SAMPLE) -> FieldEdge:
    """The edges of the field ground, sampled every `every` px and held whole (`FieldEdge`), so the height of the field
    nearest a seat is one vector pass (269 B27; a paddy envelope's vertices can stand hundreds of px apart, so the vertices
    alone would measure the wrong stretch of edge)."""
    pts: list[Pt] = []
    for ring in crops:
        for (ax, ay), (bx, by) in zip(ring, [*ring[1:], ring[0]], strict=False):
            n = max(1, math.ceil(math.dist((ax, ay), (bx, by)) / every))
            pts.extend((ax + (bx - ax) * k / n, ay + (by - ay) * k / n) for k in range(n))
    return FieldEdge(pts)


FIELD_BESIDE_FT = 300.0
"""Research: the fields beside a wood - UNRESEARCHED: the field edge within 300 ft past the nearest point, about a wood's own span"""

FIELD_REACH_PX = 8192.0
"""How far a seat looks for field ground at all: past it, the seat has none beside it (-inf). Research: plumbing - NONE: the
search's reach, the widening pad's old ceiling"""


def field_height_near(p: Pt, fall: Pt, edge: FieldEdge, beside: float = FIELD_BESIDE_FT) -> float:
    """The height (up the fall, -p.fall) of the field ground beside `p` - the highest point of the field edge within `beside`
    past the nearest one, the field a wood at `p` would adjoin (feature 328, glyph-check of Kashikawa's woodland commons: one
    nearest point stood 53 ft below a wood whose paddy beside it ran up past its top). With no field ground within
    `FIELD_REACH_PX`, -inf (every seat stands above it).

    Research: higher than the fields beside it - research/questions/0077-village-fuel-woods-and-their-coppice-satoyama.drawing.html: on ground higher than the fields beside it"""
    import numpy as np  # bound here, not at import (feature 237)

    if not len(edge.xy):
        return -math.inf
    d = np.hypot(edge.xy[:, 0] - p[0], edge.xy[:, 1] - p[1])
    d0 = float(d.min())
    if d0 > FIELD_REACH_PX:
        return -math.inf
    near = edge.xy[d <= d0 + beside]
    return float((-(near[:, 0] * fall[0] + near[:, 1] * fall[1])).max())


def house_floor(houses: Sequence[Pt], fall: Pt) -> float:
    """The height below which a wood stands below the houses: the houses' median height up the fall (feature 328, glyph-check
    of Kashikawa's woodland commons: against the lowest house alone, a wood below 19 of the 20 houses ranked as above them);
    -inf with no houses.

    Research: never below the houses - research/questions/0077-village-fuel-woods-and-their-coppice-satoyama.drawing.html: a wood below the houses stands where the record puts grass"""
    hs = sorted(-(x * fall[0] + y * fall[1]) for x, y in houses)
    if not hs:
        return -math.inf
    m = len(hs) // 2
    return hs[m] if len(hs) % 2 else (hs[m - 1] + hs[m]) / 2


def woodland_tier(p: Pt, fall: Pt, house_floor: float, field_height: float) -> int:
    """Where the record puts a village's fuel wood, as a rank (269 B27, research/questions/0077-village-fuel-woods-and-their-coppice-satoyama.html): 0 - higher than the field
    it adjoins and not below the houses (`house_floor`, their median) (the nearest hill ground beyond the fields); 1 - not below the houses but
    not above that field (the level beside the fields, the record's fallback); 2 - below the houses' median height, where the
    record puts the grass and riverbank commons, never the wood. Heights run up the fall: -p.fall.

    Research: where the fuel wood stands - research/questions/0077-village-fuel-woods-and-their-coppice-satoyama.drawing.html: higher ground beyond the fields first, the level next, never below the houses
    """
    h = -(p[0] * fall[0] + p[1] * fall[1])
    if h < house_floor:
        return 2
    return 0 if h > field_height else 1
