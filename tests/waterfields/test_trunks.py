"""Feature 287 (water W13-W15): the comb holds its trunks - the collector and the main canals - to the rules the
finished-map tests used to measure, by construction (`comb._comb_drain`) and by repair (`trunks.anchor_trunk_ends`). Each
test drives the placer on constructed inputs that include the violating case and asks the rule's one predicate in
`waterfields/trunks.py`."""

from __future__ import annotations

from types import SimpleNamespace

from l7r.diagram.waterfields.trunks import outfall_rise, sharpest_turn


class _Scripted:
    """A random stream whose draws are scripted per (low, high) range, in order; an unscripted draw returns the top of
    its range - the worst case for a jitter."""

    def __init__(self, script: dict[tuple[float, float], list[float]]) -> None:
        self.script = {k: list(v) for k, v in script.items()}

    def uniform(self, a: float, b: float) -> float:
        queue = self.script.get((a, b))
        return queue.pop(0) if queue else b


def _thread(u: float, bottom: float) -> SimpleNamespace:
    """A delivery column at contour `u` whose ditch is dug to fall `bottom` (on a 90 deg fall, u is x and f is y)."""
    return SimpleNamespace(pts=[(u, 0.0), (u, bottom), (u, bottom + 400.0)], ditch_f=bottom, f0=0.0)


def test_the_predicates_read_the_fall_and_the_turn() -> None:
    assert abs(outfall_rise([(0.0, 0.0), (100.0, 5.0)], 90.0) - 5.0) < 1e-9
    assert abs(outfall_rise([(0.0, 5.0), (100.0, 0.0)], 90.0) + 5.0) < 1e-9
    assert sharpest_turn([(0.0, 0.0), (10.0, 0.0), (10.0, 10.0)]) == 90.0
    assert sharpest_turn([(0.0, 0.0), (0.0, 0.0), (10.0, 0.0)]) == 0.0, "a leg with no length turns nothing"
