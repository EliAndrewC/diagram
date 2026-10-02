"""`waterfields/partition.py` (feature 302): the comb's plots BY CONSTRUCTION - the planted region tiled by its bunds at once.

The scene is hand-built at a 90 deg fall (u = x, f = y): two threads down the sheet at x = 100 and x = 300, a drain across the foot,
and a region that runs past both threads - so the sector between them, the strips past each outermost thread and the toe past
the threads' ends are all present. The property under test throughout is the partition's: the cells TILE the region (no gap,
no overlap) and every bund is shared by the two cells it divides.
"""

from __future__ import annotations

import random
from typing import Any

from l7r.diagram.waterfields import partition as pt
from l7r.diagram.waterfields.frame import _Frame, _Thread


def _box(x0: float, y0: float, x1: float, y1: float) -> Any:
    from shapely.geometry import box

    return box(x0, y0, x1, y1)


def _thread(x: float, y0: float, y1: float) -> _Thread:
    t = _Thread(x, y0, 0.0, y0)
    t.pts = [(x, y0 + (y1 - y0) * k / 10) for k in range(11)]
    return t


def _sectors(region: Any, threads: list[_Thread], across: float = 48.0) -> pt.Sectors:
    return pt.Sectors(_Frame(90.0), threads, region, random.Random(1), random.Random(2), across, (26.0, 36.0), 1.0)


def _tiles(region: Any, cells: list[Any]) -> None:
    from shapely.ops import unary_union

    assert cells, "the region is cut into cells"
    union = unary_union(cells)
    assert abs(union.area - region.area) < 1e-6 * region.area + 1e-3, "the cells cover the region exactly"
    assert abs(sum(c.area for c in cells) - region.area) < 1e-6 * region.area + 1e-3, "and no two cells overlap"


def test_the_planted_region_is_the_envelope_less_its_water_and_what_it_cannot_command() -> None:
    env = [(0.0, 0.0), (400.0, 0.0), (400.0, 400.0), (0.0, 400.0)]
    chan = [{"pts": [(200.0, -10.0), (200.0, 410.0)], "w": 12.0, "w_tail": 12.0, "role": "branch"}]
    region = pt.planted_region(_Frame(90.0), env, chan, [(-500.0, -500.0), (900.0, -500.0)], [(-500.0, 900.0), (900.0, 900.0)], 1.0, lambda _u: 2.0)
    assert region.geom_type == "MultiPolygon", "the ditch splits the field in two"
    assert not region.contains(_box(199, 100, 201, 101)), "the ditch and its banks are not planted"
    assert 0.9 * 160000 < region.area < 160000
    rings = pt.region_rings(region)
    assert len(rings) == 2 and all(len(r) >= 4 for r in rings)
    assert len(pt.region_rings(_box(0, 0, 10, 10))) == 1, "a single polygon has its one ring"


def test_extend_pushes_both_ends_out_along_their_own_directions() -> None:
    assert pt._extend([(0.0, 0.0), (10.0, 0.0)], 2.0) == [(-2.0, 0.0), (0.0, 0.0), (10.0, 0.0), (12.0, 0.0)]
    assert pt._extend([(0.0, 0.0)], 2.0) == [(0.0, 0.0)], "a single point has no direction"
    assert pt._extend([(1.0, 1.0), (1.0, 1.0)], 2.0)[0] == (1.0, 1.0), "a zero-length end does not move"


def test_a_threads_bound_runs_straight_down_the_fall_past_its_own_end() -> None:
    region = _box(0, 0, 400, 500)
    sec = _sectors(region, [_thread(100.0, 0.0, 300.0), _thread(300.0, 0.0, 300.0)])
    assert sec.bound(sec.threads[0], 150.0) == (100.0, 150.0), "within its course, its own course"
    x, y = sec.bound(sec.threads[0], 420.0)
    assert abs(x - 100.0) < 1e-9 and abs(y - 420.0) < 1e-9, "past its end, straight down the fall - not along the drain"


def test_a_thread_is_continued_until_it_meets_another_thread() -> None:
    region = _box(0, 0, 400, 500)
    a, b = _thread(100.0, 0.0, 300.0), _thread(300.0, 0.0, 300.0)
    b.pts += [(200.0, 450.0), (50.0, 460.0)]  # thread B swings across under A's end
    lines = _sectors(region, [a, b]).thread_lines()
    ext_a = lines[2]
    assert abs(ext_a.coords[-1][1] - 450.0) < 10.0, "A's continuation stops where it meets B, not at the canvas"
    assert lines[3].length >= 100.0, "B's runs on, meeting nothing"


def test_column_kept_halves_as_the_sector_narrows() -> None:
    assert all(pt._column_kept(240.0, 5, j, 48.0) for j in range(1, 5)), "full width: every column"
    kept = [j for j in range(1, 8) if pt._column_kept(48.0 * 3, 8, j, 48.0)]
    assert kept and all(j % 2 == 0 for j in kept), "under two thirds of its columns: every other one, ending in a T"
    assert not any(pt._column_kept(10.0, 8, j, 48.0) for j in range(1, 8)), "a sliver of a sector: none"


def test_keep_far_drops_a_bund_lying_wholly_beside_the_edge() -> None:
    from shapely.geometry import LineString

    ground = _box(0, 0, 100, 100)
    hugging, crossing = LineString([(5, 2), (95, 2)]), LineString([(0, 50), (100, 50)])  # the crossing has its vertices ON the sides
    assert pt.keep_far([hugging, crossing], ground, 10.0) == [crossing]
    assert pt.keep_far([hugging], ground, 0.0) == [hugging], "a zero limit keeps every piece"
    assert pt.keep_far([], ground, 10.0) == []


def test_inside_and_lines_in_answer_empty_inputs() -> None:
    assert pt.inside(_box(0, 0, 1, 1), []) == []
    assert pt._lines_in(_box(0, 0, 1, 1), []) == []
    assert pt.inside(_box(0, 0, 10, 10), [_box(1, 1, 2, 2), _box(20, 20, 21, 21)]) == [_box(1, 1, 2, 2)]


def test_sector_of_brackets_names_the_outer_side_and_needs_two_threads() -> None:
    region = _box(0, 0, 400, 500)
    sec = _sectors(region, [_thread(100.0, 0.0, 300.0), _thread(300.0, 0.0, 300.0)])
    assert sec.sector_of(200.0, 150.0) == (0, "")
    assert sec.sector_of(50.0, 150.0) == (0, "lo"), "past thread A"
    assert sec.sector_of(350.0, 150.0) == (0, "hi"), "past thread B"
    assert _sectors(region, [_thread(100.0, 0.0, 300.0)]).sector_of(200.0, 150.0) is None


def test_the_partition_tiles_the_region_and_shares_every_bund() -> None:
    """The sector between the threads, both outer strips (the outer lattice) and the toe past the threads' ends: every cell
    inside the region, together exactly the region, and every interior edge one cell's AND its neighbor's."""

    region = _box(0, 0, 420, 500)
    cells = pt.cut(_sectors(region, [_thread(100.0, 0.0, 300.0), _thread(300.0, 0.0, 300.0)]))
    _tiles(region, cells)
    assert len(cells) > 20, "the lattice cuts the sector and both strips at the fan's grain"
    # EVERY BUND SHARED, counted rather than searched: the cells' perimeters sum to the region's edge once and every interior
    # bund TWICE - a bund only one cell had would be counted once, and the sum would fall short
    import shapely

    # on a 0.01 px grid: a vertex `recut` sets where it splits an edge lies a float's width off the neighbor's line, and an
    # exact union would count that stretch twice
    network = shapely.union_all([c.boundary for c in cells], grid_size=0.01).length
    assert network > region.length, "there are interior bunds"
    assert abs(sum(c.length for c in cells) - (2 * network - region.length)) < 1e-4 * network, "a bund only one cell has"


def test_a_narrow_sector_spaces_its_rows_and_keeps_them() -> None:
    """A sector narrower than a plot: its rows are spaced out (`_rows_kept`) and exempt from the hug test, so the strip is cut
    into cells about a design cell in size rather than left one long ring."""
    region = _box(100, 0, 120, 400)
    sec = _sectors(region, [_thread(100.0, 0.0, 400.0), _thread(120.0, 0.0, 400.0)])
    cells = pt.cut(sec)
    assert sec.narrow, "a 20 px sector at a 48 px plot is narrow: fewer rows, exempt from the hug test"
    _tiles(region, cells)
    assert len(cells) >= 3, "the strip is cut across, not left whole"


def test_a_sector_with_no_ground_in_the_region_is_skipped() -> None:
    region = _box(500, 0, 600, 100)  # wholly past thread B: the strip lattice alone cuts it
    cells = pt.cut(_sectors(region, [_thread(100.0, 0.0, 300.0), _thread(300.0, 0.0, 300.0)]))
    _tiles(region, cells)


def test_a_fan_with_one_thread_is_one_cell() -> None:
    region = _box(0, 0, 200, 200)
    cells = pt.cut(_sectors(region, [_thread(100.0, 0.0, 150.0)]))
    _tiles(region, cells)


def test_a_converging_sector_ends_its_columns_in_a_T_and_still_tiles() -> None:
    """Thread B slants in toward A: the sector is six plots wide at its head and under one at its foot, so its columns end, one
    halving at a time, on a row bund (a T) - fewer, wider basins - and the cells still tile the ground."""
    region = _box(100, 0, 400, 400).intersection(_poly_tri())
    a = _thread(100.0, 0.0, 400.0)
    b = _Thread(400.0, 0.0, 0.0, 0.0)
    b.pts = [(400.0 - 27.0 * k, 40.0 * k) for k in range(11)]
    sec = _sectors(region, [a, b])
    _tiles(region, pt.cut(sec))
    cols = sec.grid_lines(a, b)[sec.n_rows :]
    assert cols and any(len(c) < len(sec.rows) for c in cols), "a column ends before the sector's foot, in a T on a row"


def test_a_row_is_noded_only_where_a_column_runs() -> None:
    """Glyph check, Inashiro (feature 302): a row passed through every column's point, the thinned ones too, and where the sector
    narrowed those points stood a few px apart, each with its own wobble and wander - a sawtooth of hair teeth, and folds, whose
    cells failed the toe rule. A row's interior vertices are its meetings with the columns that run there, never closer together
    than a column spacing allows."""
    import math

    a = _thread(100.0, 0.0, 400.0)
    b = _Thread(400.0, 0.0, 0.0, 0.0)
    b.pts = [(400.0 - 27.0 * k, 40.0 * k) for k in range(11)]
    sec = _sectors(_box(100, 0, 400, 400).intersection(_poly_tri()), [a, b])
    rows = sec.grid_lines(a, b)[: sec.n_rows]
    full = max(len(r) for r in rows)
    assert any(len(r) < full for r in rows), "non-vacuity: where the sector narrows a row carries fewer vertices"
    for r in rows:
        cols = r[2:-2]  # past the extension and the two bounds: the columns' meetings
        assert all(math.dist(p, q) > 0.25 * 48.0 for p, q in zip(cols, cols[1:], strict=False)), r
        xs = [p[0] for p in r[1:-1]]
        assert xs == sorted(xs), f"the row runs one way across its sector, never folding back: {r}"


def _poly_tri() -> Any:
    from shapely.geometry import Polygon

    return Polygon([(100.0, 0.0), (400.0, 0.0), (130.0, 400.0), (100.0, 400.0)])


def test_keep_rows_keeps_a_strips_crossing_and_drops_a_slivers() -> None:
    """A short row piece crosses a strip of its ground: kept where the strip is at least `MIN_ROW` plot widths across (a
    ditch-side strip), dropped where it is narrower (a hair-wide strip); a longer piece takes the hug test."""
    from shapely.geometry import LineString

    ground = _box(0, 0, 300, 100)
    strip, sliver, long_hug, long_cross = LineString([(0, 50), (30, 50)]), LineString([(0, 50), (8, 50)]), LineString([(5, 3), (295, 3)]), LineString([(0, 60), (300, 60)])
    kept = pt.keep_rows([strip, sliver, long_hug, long_cross], ground, 13.0, 48.0)
    assert strip in kept and sliver not in kept and long_cross in kept and long_hug not in kept


def test_rows_kept_spaces_rows_by_the_cell_they_close() -> None:
    rows = [float(30 * k) for k in range(12)]
    assert pt._rows_kept(rows, [240.0] * 12, 5, 48.0, (26.0, 36.0), 10.0) == set(range(12)), "full width: every row"
    thin = pt._rows_kept(rows, [20.0] * 12, 1, 48.0, (26.0, 36.0), 5.0)
    assert 0 in thin and len(thin) < 12, "a strip under half a plot: fewer rows, each closing about a basin"
    assert pt._rows_kept(rows, [4.0] * 12, 1, 48.0, (26.0, 36.0), 10.0) == {0}, "under the tip's width: no row past the first"


def test_recut_cuts_an_oversized_cell_at_the_fans_grain() -> None:
    big = _box(0, 0, 150, 100)
    parts = pt.recut(big, _Frame(90.0), 48.0, 31.0)
    _tiles(big, parts)
    assert len(parts) == 3 * 3, "three columns of 50 and three rows of 33"
    one = _box(0, 0, 40, 30)
    assert pt.recut(one, _Frame(90.0), 48.0, 31.0) == [one], "already a basin: nothing to cut"


def test_f_top_reads_the_least_fall_over_an_outline() -> None:
    assert abs(pt._f_top(_Frame(90.0), _box(10, 25, 40, 90)) - 25.0) < 1e-9
    assert abs(pt._f_top(_Frame(90.0), _box(10, 25, 40, 90).union(_box(100, 5, 120, 30))) - 5.0) < 1e-9
