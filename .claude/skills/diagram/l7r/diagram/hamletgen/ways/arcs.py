"""A lane as a run of arc length: the part of a run between two lengths, a point's length along it, a stretch cut out of it.

Lifted out of `settle.py` at the 1,000-line bar (feature 315); `settle` re-exports all three, which `tree.py` and the tests name.

Research: arc-length plumbing - NONE
"""

from __future__ import annotations

import math

from ..consts import Poly, Pt
from .geom import polyline_len


def sub_run(p: Poly, s0: float, s1: float) -> Poly:
    """The part of the run `p` between arc lengths `s0` and `s1` (clamped to the run) - [] when that is nothing."""
    total = polyline_len(p)
    s0, s1 = max(0.0, s0), min(total, s1)
    if s1 - s0 < 1e-6 or len(p) < 2:
        return []
    out: Poly = []
    acc = 0.0
    for a, b in zip(p, p[1:], strict=False):
        d = math.dist(a, b)
        lo, hi = acc, acc + d
        if hi >= s0 and lo <= s1 and d > 0:
            t0 = max(0.0, (s0 - lo) / d)
            t1 = min(1.0, (s1 - lo) / d)
            q0 = (a[0] + (b[0] - a[0]) * t0, a[1] + (b[1] - a[1]) * t0)
            q1 = (a[0] + (b[0] - a[0]) * t1, a[1] + (b[1] - a[1]) * t1)
            if not out:
                out.append(q0)
            if math.dist(out[-1], q1) > 1e-9:
                out.append(q1)
        acc = hi
    return out if len(out) >= 2 else []


def arc_at(p: Poly, k: int, x: Pt) -> float:
    """The arc length along `p` of the point `x` on its segment `k`."""
    return polyline_len(p[: k + 1]) + math.dist(p[k], x)


def cut_around(p: Poly, at: float, gap: float) -> list[Poly]:
    """`p` with the stretch within `gap` of arc length `at` taken out: the pieces either side."""
    return [q for q in (sub_run(p, 0.0, at - gap), sub_run(p, at + gap, polyline_len(p))) if q]
