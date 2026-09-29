"""Where water meets water on a rolled map (feature 166): what is left of it after feature 287.

Feature 166 carried the confluence rules here that the retired battery re-measured on every finished map. Feature 287
moved all but one into their placers, each with a unit test on the violating case, and retired their finished-map tests
(specs/287-placer-guarantees/research.md R8): the lateral's two ends (`waterfields/polder.py`'s tip snap), a channel
declaring a stream reaching its bed (`fields/comb.py`'s intake snap, `round_the_brooks` holding the joins), the
confluence composited once and the pond fill over the mouths (`settlement/finish.py`'s one water stack), the pond
connected to its field (`hamletgen/sink.py`'s pond run) and the field pond sunk into one plot
(`fields/features.py:_pond_fit`, `ring_meets_ellipse`).

KEPT, because no placer guarantees it yet: `channels_join_water_not_cross`. `brook_violations` refuses a crossing on
every candidate course but the feed brook's LAST one (`hamletgen/water/brook.py:feed_brook`, the route round the field),
which is returned unjudged - so a watercourse can still be drawn across the brook mid-run.
"""

from __future__ import annotations

import math

import pytest

from tests import rolls
from tests.gate import _pool

SPEC = rolls.REFERENCE  # the pool's brief (feature 215)

TRUNK_TOL = 13.0
"""How near a joiner's end must come to the water it discharges into for a crossing there to count as its mouth. A
course is a stroke with width, not a line, so the tolerance is the band rather than a snap tolerance."""


def _seg_dist(px: float, py: float, a, b) -> float:
    ax, ay, bx, by = a[0], a[1], b[0], b[1]
    vx, vy = bx - ax, by - ay
    L2 = vx * vx + vy * vy
    t = 0.0 if L2 == 0 else max(0.0, min(1.0, ((px - ax) * vx + (py - ay) * vy) / L2))
    return math.hypot(px - (ax + t * vx), py - (ay + t * vy))


def _poly_dist(pt, poly) -> float:
    return min(_seg_dist(pt[0], pt[1], poly[i], poly[i + 1]) for i in range(len(poly) - 1))


def _crosses(a0, a1, b0, b1) -> bool:
    """Do the two OPEN segments properly cross? A shared endpoint is a junction, not a crossing."""

    def side(p, q, r):
        return (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])

    d1, d2 = side(a0, a1, b0), side(a0, a1, b1)
    d3, d4 = side(b0, b1, a0), side(b0, b1, a1)
    return ((d1 > 0) != (d2 > 0)) and ((d3 > 0) != (d4 > 0))


@pytest.fixture(scope="module")
def rolled():
    return _pool.rolled_map(SPEC)


def test_no_watercourse_crosses_another_mid_run(rolled) -> None:
    """`channels_join_water_not_cross`, `water_channels_join_not_cross` and
    `channels_join_not_cross_at_fork`. Water joins water at a CONFLUENCE - the mouth ends at the bank,
    engine-trimmed and water-colored. It never runs straight across the open water like a painted line.

    A shared endpoint is deliberately NOT a crossing: that is the confluence itself, and a predicate that
    could not tell the two apart would forbid the very thing the rule exists to require."""
    _plan, M = rolled
    water = [[(float(p[0]), float(p[1])) for p in s["poly"]] for s in (M.get("streams") or [])]
    joiners = [[(float(p[0]), float(p[1])) for p in c["poly"]] for c in (M.get("channels") or [])]
    joiners += [[(float(p[0]), float(p[1])) for p in d["poly"]] for d in (M.get("field_ditches") or [])]
    assert water and joiners, "the roll drew no open water or nothing joining it, so nothing could cross"
    crossings = []
    for w in water:
        for j in joiners:
            for i in range(len(j) - 1):
                for k in range(len(w) - 1):
                    if not _crosses(j[i], j[i + 1], w[k], w[k + 1]):
                        continue
                    # the mouth ENDING on the bed is the confluence; a crossing away from the joiner's
                    # own ends is the painted line the rule forbids
                    if min(_poly_dist(e, w) for e in (j[0], j[-1])) < TRUNK_TOL:
                        continue
                    crossings.append((round(j[i][0]), round(j[i][1])))
    assert not crossings, f"watercourse(s) cross the open water mid-run at {sorted(set(crossings))[:4]} instead of joining it"
