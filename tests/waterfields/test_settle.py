"""`waterfields/settle.py` (feature 302): the partition held to the ring rules at construction - split, merged, or left bare.

Every test asks the cells `settle` returns the rules' ONE predicate, `ring_violations` (with the toe discipline), and finds
nothing: what the deleted weld-ladder tests held of the seam pass (the plan review's round-3 note).
"""

from __future__ import annotations

from typing import Any

from l7r.diagram.waterfields import settle as st
from l7r.diagram.waterfields.ring_rules import RingContext

CELL = 48.0 * 31.0
ACROSS = 48.0


def _poly(ring: list[tuple[float, float]]) -> Any:
    from shapely.geometry import Polygon

    return Polygon(ring)


def _box(x0: float, y0: float, x1: float, y1: float) -> Any:
    from shapely.geometry import box

    return box(x0, y0, x1, y1)


def _lawful(cells: list[Any], ctx: RingContext) -> None:
    for c in cells:
        assert not st.verdict(c, ctx, ACROSS, CELL), (st.verdict(c, ctx, ACROSS, CELL), list(c.exterior.coords))


def test_verdict_names_the_toe_discipline_and_a_collapsed_ring() -> None:
    ctx = RingContext(cell=CELL, g=1.0)
    assert "toe" in st.verdict(_box(0, 0, 100, 2), ctx, ACROSS, CELL), "too thin to hold water"
    assert "toe" in st.verdict(_poly([(0.0, 0.0), (200.0, 0.0), (0.0, 20.0)]), ctx, ACROSS, CELL), "pointed"
    assert {"area", "toe"} <= st.verdict(_poly([(0.0, 0.0), (0.04, 0.0), (0.0, 0.04)]), ctx, ACROSS, CELL), "rounded away to nothing"
    assert not st.verdict(_box(0, 0, 48, 31), ctx, ACROSS, CELL)


def test_takes_judges_a_union_by_the_rules_and_by_growth() -> None:
    ctx = RingContext(cell=CELL, g=1.0)

    def judged(p: Any) -> set[str]:
        return st.verdict(p, ctx, ACROSS, CELL)

    small, other = _box(0, 0, 3, 31), _box(3, 0, 6, 31)
    assert st.takes(None, judged, small, other, True) is None
    assert st.takes(_box(0, 0, 20, 31).union(_box(40, 0, 50, 31)), judged, small, other, True) is None, "two pieces"
    assert st.takes(_box(0, 0, 48, 31), judged, small, other, False) == set(), "lawful"
    assert st.takes(_box(0, 0, 6, 31), judged, small, other, True) is not None, "growing, only its size short"
    assert st.takes(_box(0, 0, 6, 31), judged, small, other, False) is None, "a lawful neighbor is never handed a failing union"
    assert st.takes(_box(0, 0, 2, 31), judged, small, other, True) is None, "a union no larger than its parts is not growing"
