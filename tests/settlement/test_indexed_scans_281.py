"""Feature 281's exact removals on the board, the watercourse tests and the caption probe: each index PRUNES and the old
test DECIDES, compared here against a copy of the old scan (the oracle `dev/performance.md` prescribes)."""

from __future__ import annotations

import math
import random

from l7r.diagram.settlement._geom import seg_dist, segments_cross
from l7r.diagram.settlement.structures.fixtures import _helpers as fx

Pt = tuple[float, float]


def _walk(rng: random.Random, n: int, x0: float = 0.0, y0: float = 0.0) -> list[Pt]:
    out = [(x0 + rng.uniform(0, 600), y0 + rng.uniform(0, 600))]
    for _ in range(n - 1):
        out.append((out[-1][0] + rng.uniform(-80, 80), out[-1][1] + rng.uniform(-80, 80)))
    return out


def _old_join(track, others, step=5.0):
    for a, b in zip(track, track[1:], strict=False):
        n = max(1, int(math.dist(a, b) // step))
        for i in range(n + 1):
            q = (a[0] + (b[0] - a[0]) * i / n, a[1] + (b[1] - a[1]) * i / n)
            if any(seg_dist(q[0], q[1], c, d) <= fx.KOSATSUBA_HANDOVER_PX for o in others for c, d in zip(o, o[1:], strict=False)):
                return q
    return None


def test_the_handover_walk_from_its_index_is_the_old_walk() -> None:
    """FR-004: `outermost_join` finds the same first point - including a way passing exactly at the handover reach."""
    rng = random.Random(2814)
    for _ in range(200):
        track = _walk(rng, rng.randint(2, 6))
        others = [_walk(rng, rng.randint(2, 5)) for _ in range(rng.randint(0, 6))]
        assert fx.outermost_join(track, others) == _old_join(track, others)
    track = [(0.0, 0.0), (100.0, 0.0)]
    at = [[(50.0, fx.KOSATSUBA_HANDOVER_PX), (50.0, 60.0)]]
    assert fx.outermost_join(track, at) == _old_join(track, at) == (50.0, 0.0)
    assert fx.outermost_join(track, []) is None


def _old_missed(routes, x, y, near):
    return sum(1 for r in routes if not any(math.hypot(q[0] - x, q[1] - y) <= near for q in r))


def test_the_departure_count_from_its_index_is_the_old_count() -> None:
    """FR-004: `RouteReach.missed` counts the routes that never come within `near` exactly as the scan did - a route passing
    at exactly `near`, an empty route, no routes."""
    rng = random.Random(2815)
    for _ in range(60):
        routes = [_walk(rng, rng.randint(1, 30)) for _ in range(rng.randint(0, 12))] + [[]]
        reach = fx.RouteReach(routes)
        for _ in range(40):
            x, y, near = rng.uniform(-50, 650), rng.uniform(-50, 650), rng.choice((6.0, 20.0, 45.0))
            assert reach.missed(x, y, near) == _old_missed(routes, x, y, near) == fx.routes_missed(routes, x, y, near)
    assert fx.RouteReach([[(0.0, 0.0)]]).missed(3.0, 4.0, 5.0) == 0 == _old_missed([[(0.0, 0.0)]], 3.0, 4.0, 5.0)
    assert fx.RouteReach([]).missed(0.0, 0.0, 10.0) == 0


def _old_on_stream(gc, pts, streams):
    for f in streams:
        poly = f.get("poly") or []
        hw = float(f.get("w", 9.0)) / 2 + 5
        for k in range(len(poly) - 1):
            a, b = poly[k], poly[k + 1]
            if any(seg_dist(px, py, a, b) < hw for px, py in pts) or any(segments_cross(a, b, gc[e], gc[(e + 1) % 4]) for e in range(4)):
                return True
    return False


def _old_lanes_clear(b, lanes):
    for ln in lanes:
        pts = ln.get("pts") or []
        half = float(ln.get("w", 5)) / 2 + 3.0 + 2.0
        for k in range(len(pts) - 1):
            a, b2 = pts[k], pts[k + 1]
            cx, cy = (b[0] + b[2]) / 2, (b[1] + b[3]) / 2
            if seg_dist(cx, cy, (float(a[0]), float(a[1])), (float(b2[0]), float(b2[1]))) < half + max(b[2] - b[0], b[3] - b[1]) / 2:
                return False
    return True
