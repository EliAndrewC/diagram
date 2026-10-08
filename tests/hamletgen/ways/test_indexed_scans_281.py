"""Feature 281's exact removals on the ways: each index PRUNES and the old test DECIDES, so each answer here is the old
scan's, compared against a copy of that scan kept in this file (the oracle `dev/performance.md` prescribes)."""

from __future__ import annotations

import math
import random

from l7r.diagram.hamletgen.ways import clearance as wc
from l7r.diagram.hamletgen.ways import route as wr
from l7r.diagram.settlement._geom import point_in_poly, seg_dist

Pt = tuple[float, float]


def _old_clip(pts, obstacles, margin, step=8.0, lines=(), line_margin=14.0):
    """`clip_to_clear` as it stood at c13a6ebe6: every obstacle edge and every line, per sample."""
    if not obstacles and not lines:
        return pts

    def fouled(q):
        if any(seg_dist(q[0], q[1], a, b) < line_margin for a, b in lines):
            return True
        return any(point_in_poly(q[0], q[1], list(o)) or min(seg_dist(q[0], q[1], o[j], o[(j + 1) % len(o)]) for j in range(len(o))) < margin for o in obstacles)

    out = [pts[0]]
    for i in range(len(pts) - 1):
        a, b = pts[i], pts[i + 1]
        n = max(1, int(math.hypot(b[0] - a[0], b[1] - a[1]) / step))
        last = a
        for k in range(1, n + 1):
            q = (a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n)
            if fouled(q):
                trimmed = out + [last]
                return trimmed if wc.polyline_len(trimmed) >= 70.0 else []
            last = q
        out.append(b)
    return out


def _ring(rng: random.Random, concave: bool) -> list[Pt]:
    cx, cy = rng.uniform(100, 900), rng.uniform(100, 900)
    k = rng.randint(4, 12)
    out = []
    for i in range(k):
        a = 2 * math.pi * i / k
        r = rng.uniform(20, 90) * (0.4 if concave and i % 2 else 1.0)
        out.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return out


def test_the_clip_through_the_fabric_index_is_the_old_clip() -> None:
    """FR-001: `clip_to_clear` answers every clip exactly as the per-edge scan did - concave rings, lines, and a polyline
    whose samples fall exactly on an edge's margin."""
    rng = random.Random(281)
    for _ in range(300):
        obstacles = [_ring(rng, rng.random() < 0.5) for _ in range(rng.randint(0, 8))]
        lines = [((rng.uniform(0, 1000), rng.uniform(0, 1000)), (rng.uniform(0, 1000), rng.uniform(0, 1000))) for _ in range(rng.randint(0, 4))]
        pts = [(rng.uniform(0, 1000), rng.uniform(0, 1000)) for _ in range(rng.randint(2, 6))]
        margin, line_margin = rng.choice((6.0, 12.0, 20.0)), rng.choice((8.0, 14.0))
        assert wc.clip_to_clear(pts, obstacles, margin, lines=lines, line_margin=line_margin) == _old_clip(pts, obstacles, margin, lines=lines, line_margin=line_margin)
    # a sample landing exactly `margin` off an edge: strictly-under, in both forms
    square = [(100.0, 100.0), (200.0, 100.0), (200.0, 200.0), (100.0, 200.0)]
    run = [(0.0, 88.0), (400.0, 88.0)]
    assert wc.clip_to_clear(run, [square], 12.0) == _old_clip(run, [square], 12.0)
    assert wc.clip_to_clear(run, [], 12.0) == run


def _old_band(p: Pt, brook: list[Pt], r: float) -> bool:
    """`in_brook_band` as it stood: 5 ft samples in 20 px cells, the (2k+1)^2 cells round the point read."""
    grid: dict[tuple[int, int], list[Pt]] = {}
    for a, b in zip(brook, brook[1:], strict=False):
        n = max(1, int(math.dist(a, b) // 5.0))
        for i in range(n + 1):
            q = (a[0] + (b[0] - a[0]) * i / n, a[1] + (b[1] - a[1]) * i / n)
            grid.setdefault((int(q[0] // 20), int(q[1] // 20)), []).append(q)
    gx, gy, k = int(p[0] // 20), int(p[1] // 20), int(r // 20) + 1
    return any(math.dist(p, q) <= r for dx in range(-k, k + 1) for dy in range(-k, k + 1) for q in grid.get((gx + dx, gy + dy), ()))


def test_the_toll_grid_sized_to_the_band_is_the_old_band() -> None:
    """FR-003: the band read from 3 x 3 cells of the radius answers as the 25 cells of 20 px did - points far off, near,
    and exactly at the radius from a sample; for the ford's 30 px and for radii under and over the old cell."""
    rng = random.Random(2813)
    brook = [(0.0, 300.0), (180.0, 330.0), (360.0, 290.0), (540.0, 400.0), (700.0, 380.0)]
    try:
        for r in (30.0, 12.0, 45.0, 64.0):
            wr.set_crossing(brook, r, 10.0)
            pts = [(rng.uniform(-60, 760), rng.uniform(200, 500)) for _ in range(3000)]
            pts += [(brook[1][0], brook[1][1] + r), (brook[1][0] + r, brook[1][1]), (brook[0][0] - r, brook[0][1])]
            for p in pts:
                assert wr.in_brook_band(p) == _old_band(p, brook, r), (r, p)
    finally:
        wr.set_crossing([], 0.0, 0.0)
