"""`waterfields/settle.py` (feature 302): the partition held to the ring rules at construction - split, merged, or left bare.

Every test asks the cells `settle` returns the rules' ONE predicate, `ring_violations` (with the toe discipline), and finds
nothing: what the deleted weld-ladder tests held of the seam pass (the plan review's round-3 note).
"""

from __future__ import annotations

from typing import Any

import pytest

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


def test_lawful_cells_come_back_as_they_were() -> None:
    ctx = RingContext(cell=CELL, g=1.0)
    cells = [_box(0, 0, 48, 31), _box(48, 0, 96, 31)]
    kept, scraps = st.settle_cells(cells, ctx, ACROSS, CELL)
    assert scraps == [] and sorted(round(c.area) for c in kept) == [1488, 1488]
    _lawful(kept, ctx)


def test_a_sliver_is_merged_into_the_neighbor_it_shares_the_longest_bund_with() -> None:
    ctx = RingContext(cell=CELL, g=1.0)
    big, other, sliver = _box(0, 0, 48, 31), _box(0, 31, 48, 62), _box(48, 0, 51, 31)
    kept, scraps = st.settle_cells([big, other, sliver], ctx, ACROSS, CELL)
    assert scraps == [] and len(kept) == 2
    assert any(round(c.area) == 48 * 31 + 3 * 31 for c in kept), "the sliver went to the basin it ran along"
    _lawful(kept, ctx)


def test_a_cluster_of_small_cells_grows_into_a_basin() -> None:
    """Four cells each far under the area floor (93 px against the toe's 372), neighbors only to each other: no single merge
    makes a lawful basin, so two failing cells may merge when the union's only fault is its size - and the cluster grows until
    it is one."""
    ctx = RingContext(cell=CELL, g=1.0)
    parts = [_box(3 * k, 0, 3 * k + 3, 31) for k in range(4)]
    kept, scraps = st.settle_cells(parts, ctx, ACROSS, CELL)
    assert scraps == [] and len(kept) == 1 and round(kept[0].area) == 12 * 31
    _lawful(kept, ctx)


def test_a_scrap_no_neighbor_can_take_is_left_bare() -> None:
    ctx = RingContext(cell=CELL, g=1.0)
    kept, scraps = st.settle_cells([_box(0, 0, 48, 31), _box(500, 500, 503, 503)], ctx, ACROSS, CELL)
    assert len(kept) == 1 and len(scraps) == 1, "an isolated sliver is left bare, as the repair left it"
    _lawful(kept, ctx)


def test_a_staircase_is_split_on_its_hops() -> None:
    from l7r.diagram.waterfields.ring_rules import staircase

    stairs = [(0.0, 0.0), (60.0, 0.0), (60.0, 6.0), (90.0, 6.0), (90.0, 12.0), (150.0, 12.0), (150.0, 80.0), (0.0, 80.0)]
    ctx = RingContext(cell=CELL, g=1.0)
    assert staircase(stairs, 1.0), "the fixture is a flight of steps"
    kept, _scraps = st.settle_cells([_poly(stairs)], ctx, ACROSS, CELL)
    assert len(kept) >= 2, "split, not shipped whole"
    _lawful(kept, ctx)


def test_verdict_names_the_toe_discipline_and_a_collapsed_ring() -> None:
    ctx = RingContext(cell=CELL, g=1.0)
    assert "toe" in st.verdict(_box(0, 0, 100, 2), ctx, ACROSS, CELL), "too thin to hold water"
    assert "toe" in st.verdict(_poly([(0.0, 0.0), (200.0, 0.0), (0.0, 20.0)]), ctx, ACROSS, CELL), "pointed"
    assert {"area", "toe"} <= st.verdict(_poly([(0.0, 0.0), (0.04, 0.0), (0.0, 0.04)]), ctx, ACROSS, CELL), "rounded away to nothing"
    assert not st.verdict(_box(0, 0, 48, 31), ctx, ACROSS, CELL)


def test_valid_keeps_the_largest_part_of_a_pinched_cell() -> None:
    bowtie = _poly([(0.0, 0.0), (10.0, 10.0), (10.0, 0.0), (0.0, 10.0)])
    assert not bowtie.is_valid and st.valid(bowtie).is_valid and st.valid(bowtie).area > 0
    sq = _box(0, 0, 1, 1)
    assert st.valid(sq) is sq
    empty = _poly([(0.0, 0.0), (1.0, 1.0), (2.0, 2.0)])
    assert st.valid(empty) is empty, "nothing to keep: handed back as it is"


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


@pytest.mark.parametrize("fn", ["opened_union", "shared_length"])
def test_a_geometry_shapely_refuses_does_not_kill_the_roll(fn: str, monkeypatch: pytest.MonkeyPatch) -> None:
    import shapely
    from shapely.errors import GEOSException

    def boom(*_a: Any, **_k: Any) -> Any:
        raise GEOSException("synthetic")

    a, b = _box(0, 0, 10, 10), _box(10, 0, 20, 10)
    if fn == "opened_union":
        monkeypatch.setattr(shapely, "union", boom)
        assert st.opened_union(a, b) is None
    else:
        from shapely.geometry.base import BaseGeometry

        monkeypatch.setattr(BaseGeometry, "intersection", boom)
        assert st.shared_length(a, b) == 0.0


def test_ring_of_and_polygons() -> None:
    assert st.ring_of(_box(0, 0, 1.04, 1)) == [(1.0, 0.0), (1.0, 1.0), (0.0, 1.0), (0.0, 0.0)]
    assert len(st.polygons(_box(0, 0, 1, 1).union(_box(5, 5, 6, 6)))) == 2


def test_no_split_without_a_grain() -> None:
    stairs = [(0.0, 0.0), (60.0, 0.0), (60.0, 6.0), (90.0, 6.0), (90.0, 12.0), (150.0, 12.0), (150.0, 80.0), (0.0, 80.0)]
    fab = st.Fabric([_poly(stairs)], RingContext(cell=CELL, g=None), ACROSS, CELL)
    assert len(fab.alive) == 1, "with no grain the steps rule is not asked, and nothing is split"


def test_no_merge_grows_a_cell_past_the_recut_bound() -> None:
    """Glyph check, Inashiro (feature 302): three ragged cells merged into one of 4.2 design cells, undoing the partition's recut
    backstop. A union over `RECUT_OVER` design cells is never kept: the sliver beside a basin of 2.4 cells is left bare."""
    from l7r.diagram.waterfields.partition import RECUT_OVER

    ctx = RingContext(cell=CELL, g=1.0)
    big, sliver = _box(0, 0, 48, 31 * 2.4), _box(48, 0, 51, 31 * 2.4)
    assert (big.area + sliver.area) > RECUT_OVER * CELL > big.area, "the fixture straddles the bound"
    kept, scraps = st.settle_cells([big, sliver], ctx, ACROSS, CELL)
    assert len(kept) == 1 and round(kept[0].area) == round(big.area) and len(scraps) == 1
    assert st.takes(_box(0, 0, 48, 31), lambda _p: set(), big, sliver, False, most=CELL / 2) is None, "over the bound: refused"


def test_a_needle_whose_every_merge_would_stay_a_needle_is_left_bare() -> None:
    """A long thin wedge against a lawful basin: merged, the basin would carry the wedge's needle, so the basin refuses it (a
    lawful neighbor is only handed a lawful union) and the wedge is left bare."""
    ctx = RingContext(cell=CELL, g=1.0)
    basin, wedge = _box(0, 0, 48, 31), _poly([(48.0, 0.0), (400.0, 15.0), (48.0, 31.0)])
    kept, scraps = st.settle_cells([basin, wedge], ctx, ACROSS, CELL)
    assert len(kept) == 1 and round(kept[0].area) == 48 * 31, "the basin is kept as it was"
    assert len(scraps) == 1
    _lawful(kept, ctx)
