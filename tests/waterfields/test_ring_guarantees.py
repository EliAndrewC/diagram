"""Feature 287 (water W16-W25): the seam pass GUARANTEES every paddy-ring rule where it decides the rings.

Each test drives the placer - `hold_ring_rules`, which a later cut (a grave island) re-holds the rules with, or the split it
shares with `waterfields/settle.py` - on constructed rings that include the violating case (feature 302 retired the seam pass and
its weld ladder; the construction's own guarantee is `tests/waterfields/test_settle.py`), and asks the finished rings the rule's ONE
predicate in `waterfields/ring_rules.py`, the one the finished-map tests call. A staircase (W23) is one of the five rules
the GM named (`test_a_bund_does_not_build_a_flight_of_steps`).
"""

from __future__ import annotations

from typing import Any

from l7r.diagram.waterfields.ring_rules import RingContext, arrowhead, needle, ring_area, ring_violations, too_small

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


def test_a_needle_hidden_from_the_deduplicated_ring_is_judged_raw() -> None:
    """W18: the dedup blind spot - a 0.4 px collapsed edge hiding a raw apex under 15 deg. The rule reads the ring as
    recorded, raw, and so does the pass: the plot goes."""
    hidden = [(0.0, 0.0), (60.0, 0.0), (60.0, 40.0), (0.0, 40.0), (0.0, 0.4), (40.0, 5.0)]
    assert needle(hidden)
    plots = _hold([hidden], RingContext(cell=1500.0, g=G))
    assert all(not needle(p["poly"]) for p in plots)


def test_a_scrap_under_the_area_floor_is_welded_into_its_neighbor() -> None:
    """W21: a basin under 0.20 of the design cell is taken into the basin it shares the most bund with, when the union
    keeps every rule - here a 10 x 40 strip beside a 40 x 40 basin, which comes out a 50 x 40 basin."""
    small, big = _rect(40.0, 0.0, 50.0, 40.0), _rect(0.0, 0.0, 40.0, 40.0)
    ctx = RingContext(cell=2500.0, g=G)
    assert too_small(small, 2500.0)
    plots = _hold([small, big], ctx)
    assert len(plots) == 1 and abs(ring_area(plots[0]["poly"]) - 2000.0) < 2.0, "welded in, ground kept"
    assert not ring_violations(plots[0]["poly"], ctx)


def test_a_weld_that_would_leave_a_flight_of_steps_is_refused() -> None:
    """W21 with W23: an L-shaped weld - a small square on one end of a basin's wall - reads to the rule as two steps
    (the run, the hop and the run resumed, twice), so the scrap stays bare rather than make the host a staircase."""
    small, big = _rect(40.0, 0.0, 50.0, 10.0), _rect(0.0, 0.0, 40.0, 40.0)
    plots = _hold([small, big], RingContext(cell=1600.0, g=G))
    assert [p["poly"] for p in plots] == [big]


def test_a_scrap_is_offered_only_to_the_neighbors_it_shares_a_bund_with() -> None:
    """The weld's candidates: a near basin that shares no bund is passed over (the ranking stops there), and one within
    reach whose union with the grown scrap is still two pieces is refused, so the scrap stays bare."""
    small = _rect(40.0, 0.0, 50.0, 10.0)
    apart = _rect(50.3, 0.0, 90.0, 40.0)  # 0.3 px off: within the weld's 0.4 px reach, beyond its 0.02 px growth
    beyond = _rect(0.0, 10.8, 39.5, 50.0)  # its box is within a px of the scrap's, but no bund is shared
    plots = _hold([small, apart, beyond], RingContext(cell=1600.0, g=G))
    assert [p["poly"] for p in plots] == [apart, beyond]


def test_an_arrowhead_is_left_bare_rather_than_kept() -> None:
    """W25 at the last word: a basin pointed and notched at the gate line is not kept whole."""
    arrow = [(0.0, 0.0), (100.0, -30.0), (60.0, 0.0), (100.0, 30.0)]
    assert arrowhead(arrow)
    assert not [p for p in _hold([arrow], RingContext()) if arrowhead(p["poly"])]
