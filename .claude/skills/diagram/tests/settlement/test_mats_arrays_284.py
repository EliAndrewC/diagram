"""Feature 284 (FR-011, plan A8): the threshing yards' mats found by array operations and a box prefilter are the mats the
scalar search found - over every yard of the five pool hamlets, recorded with its inputs and its mats at `5f15c65bd` (the
code before this feature), and over synthetic yards."""

from __future__ import annotations

import json
from pathlib import Path

from l7r.diagram.settlement.homestead_parts import yards as Y

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "mat_cells_pool_5f15c65bd.json"


def test_every_pool_yard_lays_the_mats_it_laid_before() -> None:
    recorded = json.loads(FIXTURE.read_text())
    assert len(recorded) >= 50, "non-vacuity: the pool's yards"
    for k, rec in enumerate(recorded):
        w, h, poly, ftpx, keep, salt = rec["args"]
        got = Y.mat_cells(w, h, [tuple(p) for p in poly], ftpx, tuple(keep) if keep else None, salt)
        assert [list(m) for m in got] == rec["mats"], k


def test_a_floor_of_fewer_than_three_points_holds_no_mat() -> None:
    """A8: `floor_grid` over a degenerate floor answers no point clear, as the scalar test over no polygon did."""
    from l7r.diagram.settlement.homestead_parts.yards import floor_grid

    grid = floor_grid([0.0, 1.0, 2.0], [0.0, 1.0], [(0.0, 0.0), (5.0, 5.0)], 0.5)
    assert grid.shape == (3, 2) and not grid.any()
