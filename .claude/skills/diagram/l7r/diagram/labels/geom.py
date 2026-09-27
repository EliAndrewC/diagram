"""Plain geometry for the placer (feature 266) - convex polygons and segments as tuples, owned by neither mode."""

from __future__ import annotations

import math
from collections.abc import Sequence

Pt = tuple[float, float]
Poly = list[Pt]


def rect(cx: float, cy: float, hw: float, hh: float, angle: float = 0.0) -> Poly:
    """A rectangle of half-extents (hw, hh) centered at (cx, cy), turned by `angle` degrees about its center."""
    ca, sa = math.cos(math.radians(angle)), math.sin(math.radians(angle))
    return [(cx + dx * ca - dy * sa, cy + dx * sa + dy * ca) for dx, dy in ((-hw, -hh), (hw, -hh), (hw, hh), (-hw, hh))]


def bbox(poly: Sequence[Pt]) -> tuple[float, float, float, float]:
    xs = [p[0] for p in poly]
    ys = [p[1] for p in poly]
    return min(xs), min(ys), max(xs), max(ys)


def centroid(poly: Sequence[Pt]) -> Pt:
    """The mean of the vertices - a center, not the area centroid; enough to say which side of a subject is which."""
    return sum(p[0] for p in poly) / len(poly), sum(p[1] for p in poly) / len(poly)


def area_centroid(poly: Sequence[Pt]) -> Pt:
    """The area centroid of a simple polygon; the vertex mean for a degenerate one."""
    a = cx = cy = 0.0
    for (x0, y0), (x1, y1) in zip(poly, [*poly[1:], poly[0]], strict=True):
        c = x0 * y1 - x1 * y0
        a += c
        cx += (x0 + x1) * c
        cy += (y0 + y1) * c
    if abs(a) < 1e-9:
        return centroid(poly)
    return cx / (3.0 * a), cy / (3.0 * a)


def inside(x: float, y: float, poly: Sequence[Pt]) -> bool:
    """Ray-cast point-in-polygon."""
    hit = False
    for (x0, y0), (x1, y1) in zip(poly, [*poly[1:], poly[0]], strict=True):
        if (y0 > y) != (y1 > y) and x < x0 + (y - y0) * (x1 - x0) / (y1 - y0):
            hit = not hit
    return hit


def seg_dist(p: Pt, a: Pt, b: Pt) -> float:
    return math.dist(p, seg_closest(p, a, b))


def seg_closest(p: Pt, a: Pt, b: Pt) -> Pt:
    dx, dy = b[0] - a[0], b[1] - a[1]
    d2 = dx * dx + dy * dy
    t = 0.0 if d2 == 0 else max(0.0, min(1.0, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / d2))
    return a[0] + t * dx, a[1] + t * dy


def _cross(o: Pt, a: Pt, b: Pt) -> float:
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


def segments_cross(a: Pt, b: Pt, c: Pt, d: Pt) -> bool:
    """Do the closed segments ab and cd meet?"""
    d1, d2, d3, d4 = _cross(c, d, a), _cross(c, d, b), _cross(a, b, c), _cross(a, b, d)
    if ((d1 > 0) != (d2 > 0)) and ((d3 > 0) != (d4 > 0)) and d1 and d2 and d3 and d4:
        return True
    return min(seg_dist(a, c, d), seg_dist(b, c, d), seg_dist(c, a, b), seg_dist(d, a, b)) == 0.0


def _edges(poly: Sequence[Pt]) -> list[tuple[Pt, Pt]]:
    return list(zip(poly, [*poly[1:], poly[0]], strict=True))


def poly_gap(p: Sequence[Pt], q: Sequence[Pt]) -> float:
    """The gap between two polygons: 0 when they touch, overlap or one holds the other, else the least edge distance."""
    return math.dist(*nearest_points(p, q))


def nearest_points(p: Sequence[Pt], q: Sequence[Pt], closed: bool = True) -> tuple[Pt, Pt]:
    """The nearest pair of points, one on each outline - the same point twice when they meet. `p` is a polygon; `q` is a
    polygon, or with `closed=False` an open polyline (a road). Checked by vertices against edges both ways, which is
    exact for outlines that do not cross; crossing and containment are tested first."""
    qe = _edges(q) if closed else list(zip(q, q[1:], strict=False))
    if inside(p[0][0], p[0][1], q) and closed:
        return p[0], p[0]
    if inside(q[0][0], q[0][1], p):
        return q[0], q[0]
    for a, b in _edges(p):
        for c, d in qe:
            if segments_cross(a, b, c, d):
                return a, a
    best: tuple[float, Pt, Pt] | None = None
    for v in p:
        for c, d in qe:
            w = seg_closest(v, c, d)
            dd = math.dist(v, w)
            if best is None or dd < best[0]:
                best = (dd, v, w)
    for v in q:
        for a, b in _edges(p):
            w = seg_closest(v, a, b)
            dd = math.dist(v, w)
            if best is None or dd < best[0]:
                best = (dd, w, v)
    assert best is not None  # both polygons have vertices
    return best[1], best[2]


def poly_seg_gap(poly: Sequence[Pt], a: Pt, b: Pt) -> float:
    """The gap between a polygon and a segment: 0 when the segment touches or enters it."""
    if inside(a[0], a[1], poly) or inside(b[0], b[1], poly):
        return 0.0
    best = math.inf
    for c, d in _edges(poly):
        if segments_cross(a, b, c, d):
            return 0.0
        best = min(best, seg_dist(c, a, b), seg_dist(d, a, b), seg_dist(a, c, d), seg_dist(b, c, d))
    return best
