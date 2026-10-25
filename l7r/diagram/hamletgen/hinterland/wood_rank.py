"""Where a village's fuel wood ranks (269 B27, feature 328): the field ground's edge sampled once, the height of the field
beside a seat, the houses' floor and the rank itself. Lifted out of `parcels.py` at the 1,000-line bar (feature 328);
`parcels` re-exports every name.

Research: plumbing - NONE: the ranking's helpers
"""

import math
from collections.abc import Sequence
from typing import Any

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
"""Research: the fields beside a wood - GUESS: no source could speak to it, a value of ours (feature 417 T36 pass P5, 2026-10-25); the field edge within 300 ft past the nearest point, about a wood's own span"""

FIELD_REACH_PX = 8192.0
"""How far a seat looks for field ground at all: past it, the seat has none beside it (-inf). Research: plumbing - NONE: the
search's reach, the widening pad's old ceiling"""


def field_height_near(p: Pt, fall: Pt, edge: FieldEdge, beside: float = FIELD_BESIDE_FT) -> float:
    # `beside` is in the edge samples' units (px); the caller converts `FIELD_BESIDE_FT` at the map's scale
    """The height (up the fall, -p.fall) of the field ground beside `p` - the highest point of the field edge within `beside`
    past the nearest one, the field a wood at `p` would adjoin (feature 328, glyph-check of Kashikawa's woodland commons: one
    nearest point stood 53 ft below a wood whose paddy beside it ran up past its top). With no field ground within
    `FIELD_REACH_PX`, -inf (every seat stands above it).


    Research:
        how far beside reaches - GUESS: FIELD_BESIDE_FT, 300 ft past the nearest edge point; no page gives a distance
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

    Research: the houses' height - research/questions/0077-village-fuel-woods-and-their-coppice-satoyama.drawing.html: a wood below the houses and by the water stands where the record puts grass
    the median house - GUESS: no source could speak to it, a value of ours (feature 417 T36 pass P8, 2026-10-25); "below the houses" read against their median height, not the lowest house's"""
    hs = sorted(-(x * fall[0] + y * fall[1]) for x, y in houses)
    if not hs:
        return -math.inf
    m = len(hs) // 2
    return hs[m] if len(hs) % 2 else (hs[m - 1] + hs[m]) / 2


def woodland_tier(p: Pt, fall: Pt, field_height: float) -> int:
    """Where the record puts a village's fuel wood, as a rank (269 B27, research/questions/0077-village-fuel-woods-and-their-coppice-satoyama.html): 0 - higher than the field
    it adjoins (the nearest slope beyond the fields); 1 - not above that field (the level beyond the fields, the record's
    fallback). The page ranks by the field alone: the houses' height refuses a seat only by the water (`low_by_the_water`,
    feature 374 wave 120 - a seat below the houses on dry ground had been refused, then ranked last). Heights run up the
    fall: -p.fall.

    Research: where the fuel wood stands - research/questions/0077-village-fuel-woods-and-their-coppice-satoyama.drawing.html: on ground higher than the fields beside it first, on the level beyond the fields where there is no higher ground
    """
    h = -(p[0] * fall[0] + p[1] * fall[1])
    return 0 if h > field_height else 1


LOW_BY_WATER_FT = 46.0
"""How near a river or a marsh "beside" is, for a wood seat below the houses (feature 374 wave 120): the width over which the
maps draw reeds and grass interleaving at a marsh's edge (0077), taken for a river's bank too.

Research: beside a river or marsh - GUESS research/questions/0077-village-fuel-woods-and-their-coppice-satoyama.drawing.html: within 46 ft of the water's edge, the reed and grass margin"""


class WaterZone:
    """The rivers' courses and the marshes as ONE geometry, built once and asked per seat (feature 374 wave 120: asked of every
    lattice seat by distance loops, the hinterland stage ran a pool roll 2.5 times slower): a seat's distance to it is one
    GEOS read, whatever the reach the square's size gives."""

    def __init__(self, rivers: Sequence[Sequence[Pt]], marshes: Sequence[Poly]) -> None:
        import shapely  # noqa: PLC0415 - bound on first use
        from shapely.ops import unary_union  # noqa: PLC0415

        parts = [shapely.LineString(list(r)) for r in rivers if len(r) >= 2] + [shapely.make_valid(shapely.Polygon(list(m))) for m in marshes if len(m) >= 3]
        self.zone: Any = unary_union(parts) if parts else None
        if self.zone is not None:
            shapely.prepare(self.zone)

    def near(self, p: Pt, reach: float) -> bool:
        """Is `p` within `reach` of a river's course or of a marsh (inside it included)?"""
        import shapely  # noqa: PLC0415

        return self.zone is not None and float(shapely.distance(self.zone, shapely.Point(p[0], p[1]))) <= reach


def low_by_the_water(p: Pt, fall: Pt, house_floor: float, rivers: Sequence[Sequence[Pt]] | WaterZone, marshes: Sequence[Poly], reach: float) -> bool:
    """Is a wood seat low ground by a river or marsh - below the houses' median height (`house_floor`) and within `reach` of
    a river's course or a marsh? There 0077 puts the village's grass and riverbank commons, not its wood.

    Research: low ground left to grass - research/questions/0077-village-fuel-woods-and-their-coppice-satoyama.drawing.html: a wood seated below the houses, past the fields and beside a river or marsh refused"""
    if -(p[0] * fall[0] + p[1] * fall[1]) >= house_floor:
        return False  # asked first: most seats stand above the houses, and need no zone at all
    zone = rivers if isinstance(rivers, WaterZone) else WaterZone(rivers, marshes)
    return zone.near(p, reach)
