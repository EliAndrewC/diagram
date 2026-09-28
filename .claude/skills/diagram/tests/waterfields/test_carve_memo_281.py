"""Feature 281, FR-007's exact half: the carve remembers each bund vertex once the row wander is live, and no plot moves."""

from __future__ import annotations

import pytest

from l7r.diagram.waterfields import carve
from l7r.diagram.waterfields.comb import carve_comb


@pytest.mark.parametrize("down_deg,banks", [(90, True), (45, False)])
def test_the_vertex_memo_changes_no_plot(monkeypatch: pytest.MonkeyPatch, down_deg: float, banks: bool) -> None:
    """The same comb carved with and without the memo gives the same plots, point for point - with supply banks (the push
    every vertex pays) and without."""
    kw = dict(down_deg=down_deg, supply_banks=banks, field_fall=700.0)
    with_memo = carve_comb(1800, 1800, (500.0, 300.0), 7, **kw).net["plots"]
    monkeypatch.setattr(carve, "_VERTEX_MEMO", False)
    without = carve_comb(1800, 1800, (500.0, 300.0), 7, **kw).net["plots"]
    assert with_memo, "non-vacuity: the comb carved plots"
    assert with_memo == without


def test_a_shared_edge_is_one_verdict_and_the_quads_are_the_old_quads_but_for_rounding() -> None:
    """Feature 281, FR-007's moving half (B1): with the memo an edge shared by two plots gives one verdict whichever plot
    asks first, and every plot of a grid of quads round a supply stroke gets the old walk's verdict - the one kind of
    difference allowed being a sample within rounding of the threshold, of which this grid shows none."""
    import random

    sup = carve._supply_index([{"pts": [(0.0, 0.0), (400.0, 60.0), (700.0, 20.0)], "w": 14.0, "w_tail": 8.0}], 1.0)
    rng = random.Random(281)
    xs = [i * 30.0 + rng.uniform(-4, 4) for i in range(-2, 26)]
    ys = [j * 26.0 + rng.uniform(-4, 4) for j in range(-6, 8)]
    memo: dict = {}
    hits = 0
    for i in range(len(xs) - 1):
        for j in range(len(ys) - 1):
            quad = [(xs[i], ys[j]), (xs[i + 1], ys[j]), (xs[i + 1], ys[j + 1]), (xs[i], ys[j + 1])]
            old = carve._quad_in_supply(quad, sup, 1.0)
            assert carve._quad_in_supply(quad, sup, 1.0, memo) == old
            hits += old
    assert 0 < hits < (len(xs) - 1) * (len(ys) - 1), "non-vacuity: some quads meet the stroke's bank and some do not"
    a, b = (xs[3], ys[5]), (xs[3], ys[6])
    fresh: dict = {}
    carve._quad_in_supply([a, b, (a[0] + 30.0, b[1]), (a[0] + 30.0, a[1])], sup, 1.0, fresh)
    assert fresh[(a, b)] == carve._edge_in_supply(b, a, sup, 1.0) == carve._edge_in_supply(a, b, sup, 1.0)
