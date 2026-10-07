"""Whether a walk from the houses crosses the field - the woods' side of their field (feature 261, feature 328). Lifted out of
`parcels.py` at the 1,000-line bar (feature 328); `parcels` re-exports every name.

Research: crossing geometry - NONE: segment crossings and point sampling along a walk
"""

from __future__ import annotations

from collections.abc import Sequence

from l7r.diagram.settlement import segments_cross

from ..consts import Poly, Pt

__all__ = ["REAL_CROSSING_SHARE", "crossed_through", "crossed_through_many", "reached_across"]


def reached_across(field: Poly, frm: Pt, to: Pt) -> bool:
    """Whether the straight walk `frm` -> `to` crosses the field's outline - the seat lies across the field (feature 261)."""
    return any(segments_cross(frm, to, a, b) for a, b in zip(field, list(field[1:]) + list(field[:1]), strict=False))


REAL_CROSSING_SHARE = 0.5
"""Research: a real crossing - UNRESEARCHED: the walk inside the field at least half the field's depth along it"""


def crossed_through(field: Poly, frm: Pt, to: Pt, share: float = REAL_CROSSING_SHARE) -> bool:
    """Whether the straight walk `frm` -> `to` runs THROUGH the field rather than clipping a corner (feature 328, the woodland
    glyph check on Inashiro: a walk that crossed 42 ft of a 1,381 ft field counted as across it): the length of the walk
    inside the field is at least `share` of the field's depth along the walk's direction. One walk of `crossed_through_many`.

    Research: beyond the fields on the level - research/questions/0077-village-fuel-woods-and-their-coppice-satoyama.drawing.html: the far side of the fields from the houses"""
    return crossed_through_many(field, frm, [to], share)[0]


def crossed_through_many(field: Poly, frm: Pt, tos: Sequence[Pt], share: float = REAL_CROSSING_SHARE) -> list[bool]:
    """`crossed_through` for every walk from `frm` to each of `tos`, asked in one vectorized call (wave 20's pair: sampling
    each candidate's walk against the field cost the hinterland stage up to +1.1 s a roll): the exact length of each walk
    inside the field against the field's depth along it.

    Research: walk through the field - NONE: the geometry of `crossed_through`, vectorized"""
    if len(field) < 3 or not tos:
        return [False] * len(tos)
    import numpy as np  # noqa: PLC0415 - bound on first use
    import shapely  # noqa: PLC0415

    poly = shapely.Polygon(list(field))
    lines = shapely.linestrings([[frm, to] for to in tos])
    inside = shapely.length(shapely.intersection(lines, poly))
    d = np.asarray(tos, dtype=float) - np.asarray(frm, dtype=float)
    length = np.hypot(d[:, 0], d[:, 1])
    u = d / np.where(length > 0.0, length, 1.0)[:, None]
    pts = np.asarray(field, dtype=float)
    proj = u @ pts.T  # each walk's direction against every vertex of the field
    depth = proj.max(axis=1) - proj.min(axis=1)
    return [bool(n > 0.0 and dp > 0.0 and i >= share * dp) for n, dp, i in zip(length, depth, inside, strict=True)]
