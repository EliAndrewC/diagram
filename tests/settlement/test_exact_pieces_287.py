"""Feature 287's perf pass, its exact pieces, each against a copy of the scan it replaced: the hem's watercourses filed once
(`WetLines`), the wild middle's rings boxed once (`BoxedRings`), the copse's brook barriers filed once (`BankNear`), the site corridors' box test before the
distance (`SiteCorridors.hit_points`). Each index PRUNES; the old test DECIDES (`dev/performance.md`). (The seat's back went to the Rust
seat, feature 444 T27, with its own tests.)"""

from __future__ import annotations

import math
import random

from l7r.diagram.hamletgen.homesteads.boundary import SiteCorridors
from l7r.diagram.settlement._geom import point_quad_dist, quad_hits_seg, seg_dist, segments_cross
from l7r.diagram.settlement.homestead_parts.stands import BankNear


def _quad(rng: random.Random, span: float = 600.0) -> list[tuple[float, float]]:
    cx, cy, w, h, t = rng.uniform(0, span), rng.uniform(0, span), rng.uniform(4, 60), rng.uniform(4, 60), rng.uniform(0, math.pi)
    c, s = math.cos(t), math.sin(t)
    return [(cx + dx * c - dy * s, cy + dx * s + dy * c) for dx, dy in ((-w, -h), (w, -h), (w, h), (-w, h))]


def _polyline(rng: random.Random, span: float = 600.0) -> list[tuple[float, float]]:
    return [(rng.uniform(0, span), rng.uniform(0, span)) for _ in range(rng.randint(2, 6))]


def _old_hem_on_water(poly, wet, pond) -> bool:
    if any(quad_hits_seg(poly, pl_[i], pl_[i + 1], hw_) for pl_, hw_ in wet for i in range(len(pl_) - 1)):
        return True
    return bool(pond is not None and point_quad_dist(pond[0], pond[1], poly) < max(pond[2], pond[3]))


def _old_overlaps_any(poly, rings) -> bool:
    from shapely.geometry import Polygon

    a = Polygon(poly).buffer(0)
    x0, y0, x1, y1 = a.bounds
    for r in rings:
        if max(q[0] for q in r) < x0 or min(q[0] for q in r) > x1 or max(q[1] for q in r) < y0 or min(q[1] for q in r) > y1:
            continue
        if a.intersection(Polygon(r).buffer(0)).area > 1.0:
            return True
    return False


def _old_too_near(points, reach, barriers, x, y) -> bool:
    return any(math.dist((x, y), p) <= reach and not any(segments_cross((x, y), p, a, b) for a, b in barriers) for p in points)


def test_the_copses_filed_brook_is_every_brook_segment() -> None:
    """A clump is near a house on its own bank by the filed barriers exactly when the scan over every barrier says so -
    brooks crossing the reach, lying beside it and far off, houses inside and beyond it."""
    rng = random.Random(2873)
    near = 0
    for _ in range(60):
        points = [(rng.uniform(0, 500), rng.uniform(0, 500)) for _ in range(rng.randint(0, 8))]
        brook = _polyline(rng, 500.0)
        barriers = list(zip(brook, brook[1:], strict=False))
        reach = rng.choice((40.0, 90.0, 150.0))
        index = BankNear(points, reach, barriers)
        for _k in range(40):
            x, y = rng.uniform(-20, 520), rng.uniform(-20, 520)
            want = _old_too_near(points, reach, barriers, x, y)
            near += want
            assert index.too_near(x, y) is want
    assert 100 < near < 2300, "the sample holds clumps near a house on its bank, and not"


def test_the_site_corridors_box_test_is_the_distance() -> None:
    """A point on the water corridors by `hit_points` exactly when the distance to some corridor segment is under its
    clearance - a rectangle's nine points and single points, corridors of every clearance."""
    rng = random.Random(2875)
    hits = 0
    for _ in range(60):
        water = [(a, b, rng.choice((6.0, 12.0, 20.0))) for pl in (_polyline(rng) for _ in range(rng.randint(0, 5))) for a, b in zip(pl, pl[1:], strict=False)]
        corridors = SiteCorridors((water, []))
        for _k in range(30):
            cx, cy, w, h = rng.uniform(0, 600), rng.uniform(0, 600), rng.uniform(0, 50), rng.uniform(0, 50)
            pts = [(cx - w, cy - h), (cx + w, cy - h), (cx + w, cy + h), (cx - w, cy + h), (cx, cy)] if rng.random() < 0.5 else [(cx, cy)]
            want = any(seg_dist(x, y, a, b) < clr for a, b, clr in water for x, y in pts)
            hits += want
            assert corridors.hit_points(pts) is want
    assert 100 < hits < 1700, "the sample holds points on the corridors and off them"
