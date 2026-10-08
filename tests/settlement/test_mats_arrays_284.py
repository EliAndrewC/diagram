"""The threshing yards' mats over every yard of the five pool hamlets, recorded with its inputs at `5f15c65bd` (feature 284,
plan A8): since feature 297 the floor is FILLED, and the mats are held to the mat rules rather than to the search's own mats."""

from __future__ import annotations

import json
from pathlib import Path

from l7r.diagram.settlement.homestead_parts import yards as Y

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "mat_cells_pool_5f15c65bd.json"


def test_every_pool_yard_lays_lawful_mats() -> None:
    """THE RULES, NOT THE BYTES (feature 297, FR-003; the GM, 2026-09-30: maps "do NOT need to remain identical in output"): over
    every yard of the pool recorded at `5f15c65bd`, the mats the fill lays each stand on the floor by `MAT_EDGE_CLEAR_FT` and off
    the rack, no two nearer than the ink gap, at least the third-of-cover floor (or as many as the search found, where it found
    fewer) and at most the two-thirds ceiling. The test that held them to the search's own mats went with the search's role."""
    import math

    from l7r.diagram.settlement._geom import edge_dist, point_in_poly

    recorded = json.loads(FIXTURE.read_text())
    assert len(recorded) >= 50, "non-vacuity: the pool's yards"
    for k, rec in enumerate(recorded):
        w, h, poly, ftpx, keep, salt = rec["args"]
        floor_poly = [tuple(p) for p in poly]
        got = Y.mat_cells(w, h, floor_poly, ftpx, tuple(keep) if keep else None, salt)
        third = math.ceil((w * ftpx) * (h * ftpx) / Y.MAT_SQ_FT / 3.0)
        assert len(got) >= min(third, len(rec["mats"])), (k, len(got), third, len(rec["mats"]))
        assert len(got) <= max(1, math.floor((w * ftpx) * (h * ftpx) / Y.MAT_SQ_FT * 2.0 / 3.0)), k
        quads = [Y._mat_corners(x, y, mw, mh, a) for x, y, mw, mh, a in got]
        clear = Y.MAT_EDGE_CLEAR_FT / ftpx
        for q in quads:
            assert all(point_in_poly(px, py, floor_poly) and edge_dist(px, py, floor_poly) >= clear - 1e-6 for px, py in q), k
            if keep:
                xs, ys = [p[0] for p in q], [p[1] for p in q]
                assert not (min(xs) < keep[2] and max(xs) > keep[0] and min(ys) < keep[3] and max(ys) > keep[1]), k
        need = (Y.MAT_INK_CLEAR_FT + 2 * Y.MAT_STROKE_FT) / ftpx
        for i in range(len(quads)):
            for j in range(i + 1, len(quads)):
                assert Y._quad_gap(quads[i], quads[j]) >= need - 1e-6, (k, i, j)


def test_a_floor_of_fewer_than_three_points_holds_no_mat() -> None:
    """A8: `floor_grid` over a degenerate floor answers no point clear, as the scalar test over no polygon did."""
    from l7r.diagram.settlement.homestead_parts.yards import floor_grid

    grid = floor_grid([0.0, 1.0, 2.0], [0.0, 1.0], [(0.0, 0.0), (5.0, 5.0)], 0.5)
    assert grid.shape == (3, 2) and not grid.any()


def test_the_fill_has_no_box_on_a_floor_too_small_and_hands_an_unreached_floor_to_the_search() -> None:
    """Feature 297: `inner_box` is None where the floor moved in by the clearance is empty or not a quad; `_filled_lattice` is
    None where no gap's centered lattice seats the floor - and `mat_cells` then searches, as before."""
    assert Y.inner_box([(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)], 2.0) is None  # moved in past itself
    assert Y.inner_box([(0.0, 0.0), (10.0, 0.0), (5.0, 8.0)], 0.5) is None  # a triangle: three corners
    assert Y.inner_box([(0.0, 0.0), (40.0, 0.0), (40.0, 30.0), (0.0, 30.0)], 1.0) == (1.0, 1.0, 39.0, 29.0)
    sq = [(-20.0, -15.0), (20.0, -15.0), (20.0, 15.0), (-20.0, 15.0)]
    assert Y._filled_lattice(sq, 1.0, None, 6.0, 3.0, 1.0, 10_000, lambda q: True) is None  # a floor no lattice reaches
    assert Y._filled_lattice([(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)], 2.0, None, 6.0, 3.0, 1.0, 1, lambda q: True) is None
    narrow = [(-2.0, -15.0), (2.0, -15.0), (2.0, 15.0), (-2.0, 15.0)]  # narrower than one mat: no column fits, the search decides
    assert Y._filled_lattice(narrow, 0.5, None, 6.0, 3.0, 1.0, 1, lambda q: True) is None
    keep = (-2.0, -2.0, 2.0, 2.0)
    mats = Y.mat_cells(40.0, 30.0, sq, 1.0, keep, 0.0)
    assert mats and all(not (x < keep[2] and x + mw > keep[0] and y < keep[3] and y + mh > keep[1]) for x, y, mw, mh, a in mats if a == 0.0)
