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
