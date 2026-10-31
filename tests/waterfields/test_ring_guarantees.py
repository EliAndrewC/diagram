"""Feature 287 (water W16-W25): the seam pass GUARANTEES every paddy-ring rule where it decides the rings.

Each test drives the placer - `hold_ring_rules`, which a later cut (a grave island) re-holds the rules with, or the split it
shares with `waterfields/settle.py` - on constructed rings that include the violating case (feature 302 retired the seam pass and
its weld ladder; the construction's own guarantee is `tests/waterfields/test_settle.py`), and asks the finished rings the rule's ONE
predicate in `waterfields/ring_rules.py`, the one the finished-map tests call. A staircase (W23) is one of the five rules
the GM named (`test_a_bund_does_not_build_a_flight_of_steps`).
"""

from __future__ import annotations

from typing import Any

G = 2.0  # the grain at a hamlet's 1 ft per px: 2 / ftpx


def _poly(ring: Any) -> Any:
    from shapely.geometry import Polygon

    return Polygon(ring).buffer(0)


def _rect(x0: float, y0: float, x1: float, y1: float) -> list[tuple[float, float]]:
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def _union_area(rings: list[Any]) -> float:
    from shapely.ops import unary_union

    return float(unary_union([_poly(r) for r in rings]).area)


# A bund stepping sideways twice along its low wall: y 0, then 6 px over, then 6 px more - the GM's "flight of steps".
TWO_STEPS = [(0.0, 0.0), (40.0, 0.0), (40.0, 6.0), (80.0, 6.0), (80.0, 12.0), (120.0, 12.0), (120.0, 60.0), (0.0, 60.0)]
# ...and four times, the worst ring the record names (cohort seed 12's four steps).
FOUR_STEPS = [
    (0.0, 0.0),
    (30.0, 0.0),
    (30.0, 6.0),
    (60.0, 6.0),
    (60.0, 12.0),
    (90.0, 12.0),
    (90.0, 18.0),
    (120.0, 18.0),
    (120.0, 24.0),
    (150.0, 24.0),
    (150.0, 80.0),
    (0.0, 80.0),
]
