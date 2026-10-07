"""Whether a walk from the houses crosses the field - the woods' side of their field (feature 261, feature 328). Lifted out of
`parcels.py` at the 1,000-line bar (feature 328); `parcels` re-exports every name.

Research: crossing geometry - NONE: segment crossings and point sampling along a walk
"""

from __future__ import annotations

import math

from l7r.diagram.settlement import point_in_poly, segments_cross

from ..consts import Poly, Pt

__all__ = ["REAL_CROSSING_SHARE", "crossed_through", "reached_across"]


def reached_across(field: Poly, frm: Pt, to: Pt) -> bool:
    """Whether the straight walk `frm` -> `to` crosses the field's outline - the seat lies across the field (feature 261)."""
    return any(segments_cross(frm, to, a, b) for a, b in zip(field, list(field[1:]) + list(field[:1]), strict=False))


REAL_CROSSING_SHARE = 0.5
"""Research: a real crossing - UNRESEARCHED: the walk inside the field at least half the field's depth along it"""


def crossed_through(field: Poly, frm: Pt, to: Pt, share: float = REAL_CROSSING_SHARE, samples: int = 64) -> bool:
    """Whether the straight walk `frm` -> `to` runs THROUGH the field rather than clipping a corner (feature 328, the woodland
    glyph check on Inashiro: a walk that crossed 42 ft of a 1,381 ft field counted as across it): the length of the walk
    inside the field is at least `share` of the field's depth along the walk's direction.

    Research: beyond the fields on the level - research/questions/0077-village-fuel-woods-and-their-coppice-satoyama.drawing.html: the far side of the fields from the houses"""
    length = math.dist(frm, to)
    if length <= 0.0 or not field:
        return False
    ux, uy = (to[0] - frm[0]) / length, (to[1] - frm[1]) / length
    inside = sum(1 for i in range(samples) if point_in_poly(frm[0] + (to[0] - frm[0]) * (i + 0.5) / samples, frm[1] + (to[1] - frm[1]) * (i + 0.5) / samples, field)) * length / samples
    depth = max(p[0] * ux + p[1] * uy for p in field) - min(p[0] * ux + p[1] * uy for p in field)
    return depth > 0.0 and inside >= share * depth
