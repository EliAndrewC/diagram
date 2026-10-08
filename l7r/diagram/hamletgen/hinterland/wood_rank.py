"""Where a village's fuel wood ranks (269 B27, feature 328): the field ground's edge sampled once, the height of the field
beside a seat, the houses' floor and the rank itself. Lifted out of `parcels.py` at the 1,000-line bar (feature 328);
`parcels` re-exports every name.

Research: plumbing - NONE: the ranking's helpers
"""

import math
from collections.abc import Sequence

from ...settlement._geom import PointGrid
from ..consts import Poly, Pt

_EDGE_SAMPLE = 30.0  # px between the samples `crop_edge_points` takes along a field edge: a third of the scan's 90 px lattice


def crop_edge_points(crops: Sequence[Poly], every: float = _EDGE_SAMPLE) -> PointGrid:
    """The edges of the field ground, sampled every `every` px and filed in a grid, so the height of the field nearest a
    seat is one grid read (269 B27; a paddy envelope's vertices can stand hundreds of px apart, so the vertices alone
    would measure the wrong stretch of edge)."""
    grid = PointGrid(128.0)
    for ring in crops:
        for (ax, ay), (bx, by) in zip(ring, [*ring[1:], ring[0]], strict=False):
            n = max(1, math.ceil(math.dist((ax, ay), (bx, by)) / every))
            grid.extend([(ax + (bx - ax) * k / n, ay + (by - ay) * k / n, ax + (bx - ax) * k / n, ay + (by - ay) * k / n, ax + (bx - ax) * k / n, ay + (by - ay) * k / n) for k in range(n)])
    return grid


FIELD_BESIDE_FT = 300.0
"""Research: the fields beside a wood - UNRESEARCHED: the field edge within 300 ft past the nearest point, about a wood's own span"""


def field_height_near(p: Pt, fall: Pt, grid: PointGrid, beside: float = FIELD_BESIDE_FT) -> float:
    """The height (up the fall, -p.fall) of the field ground beside `p` - the highest point of the field edge within `beside`
    past the nearest one, the field a wood at `p` would adjoin (feature 328, glyph-check of Kashikawa's woodland commons: one
    nearest point stood 53 ft below a wood whose paddy beside it ran up past its top). The grid is asked at a widening pad
    until it answers; with no field ground at all, -inf (every seat stands above it).

    Research: higher than the fields beside it - research/questions/0077-village-fuel-woods-and-their-coppice-satoyama.drawing.html: on ground higher than the fields beside it"""
    pad = 128.0
    while pad <= 8192.0:
        near = [(math.dist(p, (q[0], q[1])), q) for q in grid.near(p[0], p[1], pad + beside)]
        if any(t[0] <= pad for t in near):
            d0 = min(t[0] for t in near)
            return max(-(float(q[0]) * fall[0] + float(q[1]) * fall[1]) for d, q in near if d <= d0 + beside)
        pad *= 2.0
    return -math.inf


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
    not above that field (the level beside the fields, the record's fallback); 2 - downslope of every house, where the
    record puts the grass and riverbank commons, never the wood. Heights run up the fall: -p.fall.

    Research: where the fuel wood stands - research/questions/0077-village-fuel-woods-and-their-coppice-satoyama.drawing.html: higher ground beyond the fields first, the level next, never below the houses
    """
    h = -(p[0] * fall[0] + p[1] * fall[1])
    if h < house_floor:
        return 2
    return 0 if h > field_height else 1
