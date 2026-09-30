"""`hamletgen/ways/dry_exit.py`: the flood fill that finds a track out of the frame over ground it may stand on (feature
287, ways W23-W25) - the connector's way out where no bearing of the sweep is dry and clear of the steadings."""

from l7r.diagram.hamletgen.ways.dry_exit import EXIT_CELL_FT, dry_exit
from l7r.diagram.settlement import edge_dist, point_in_poly, segments_cross

# a toe marsh spanning the canvas but for one dry neck, 60 ft wide, at x 700-760
MARSH_W = [(-100.0, 600.0), (700.0, 600.0), (700.0, 700.0), (-100.0, 700.0)]
MARSH_E = [(760.0, 600.0), (1500.0, 600.0), (1500.0, 700.0), (760.0, 700.0)]


def _clear_of(path, poly, margin):
    samples = [(a[0] + (b[0] - a[0]) * k / 40, a[1] + (b[1] - a[1]) * k / 40) for a, b in zip(path, path[1:], strict=False) for k in range(41)]
    return all(not point_in_poly(x, y, poly) and edge_dist(x, y, poly) >= margin for x, y in samples)


def test_the_fill_finds_the_one_dry_neck_out_of_a_pocket() -> None:
    walls = [(MARSH_W, 0.0), (MARSH_E, 0.0)]
    path = dry_exit((300.0, 300.0), walls, [], 1400.0, 1000.0)
    assert path is not None
    assert not (0.0 <= path[-1][0] <= 1400.0 and 0.0 <= path[-1][1] <= 1000.0), "it leaves the canvas"
    assert _clear_of(path, MARSH_W, 0.0) and _clear_of(path, MARSH_E, 0.0), "no point of it stands in the marsh"
    assert len(path) <= 8, "string-pulled to a few legs"


def test_a_wall_keeps_its_margin_and_a_water_line_is_never_crossed() -> None:
    block = [(400.0, 0.0), (500.0, 0.0), (500.0, 500.0), (400.0, 500.0)]
    brook = ((0.0, 800.0), (1400.0, 800.0))
    path = dry_exit((450.0, 700.0), [(block, 16.0)], [brook], 1400.0, 1000.0)
    assert path is not None and _clear_of(path[1:], block, 16.0)
    assert not any(segments_cross(a, b, *brook) for a, b in zip(path, path[1:], strict=False)), "it does not cross the brook"


def test_a_start_walled_in_has_no_dry_exit() -> None:
    hole = (700.0, 500.0)  # inside a box of four walls
    walls = [([(500.0, 300.0), (900.0, 300.0), (900.0, 320.0), (500.0, 320.0)], 0.0), ([(500.0, 680.0), (900.0, 680.0), (900.0, 700.0), (500.0, 700.0)], 0.0)]
    walls += [([(480.0, 300.0), (500.0, 300.0), (500.0, 700.0), (480.0, 700.0)], 0.0), ([(900.0, 300.0), (920.0, 300.0), (920.0, 700.0), (900.0, 700.0)], 0.0)]
    assert dry_exit(hole, walls, [], 1400.0, 1000.0) is None
    assert dry_exit(hole, [], [], 1400.0, 1000.0, cell=EXIT_CELL_FT) is not None, "open ground has an exit"
    assert dry_exit(hole, [([(0.0, 0.0), (1.0, 1.0)], 0.0)], [], 1400.0, 1000.0) is not None, "a wall of under three points is no wall"


def test_the_raster_is_built_once_for_the_same_walls_and_lines_whatever_the_start() -> None:
    """Homes wave 5 (performance): the margins of one site ask the same walls and lines from different starts; the blocked
    cells are remembered by what they read (`_blocked_memo`), and the answer from each start is the fresh build's."""
    from l7r.diagram.hamletgen.ways import dry_exit as de

    de._blocked_memo.cache_clear()
    wall = [([(40.0, 0.0), (60.0, 0.0), (60.0, 90.0), (40.0, 90.0)], 2.0)]
    lines = [((0.0, 95.0), (100.0, 95.0))]
    a = de.dry_exit((20.0, 50.0), wall, lines, 100.0, 100.0)
    b = de.dry_exit((80.0, 50.0), [(list(p), m) for p, m in wall], list(lines), 100.0, 100.0)
    assert a is not None and b is not None
    info = de._blocked_memo.cache_info()
    assert (info.misses, info.hits) == (1, 1)
    x0, n = -2 * de.EXIT_CELL_FT, int((100.0 + 4 * de.EXIT_CELL_FT) // de.EXIT_CELL_FT) + 1
    assert de._blocked_memo(tuple((tuple(p), m) for p, m in wall), tuple(lines), x0, x0, n, n, de.EXIT_CELL_FT) == frozenset(de._blocked_cells(wall, lines, x0, x0, n, n, de.EXIT_CELL_FT))


def test_the_connector_leaves_between_two_farms_groves_by_the_finer_grid() -> None:
    """`connector_dry_exit` (feature 291 on 287): two grove bands a lane's room (32 ft) apart, the gateway between them - at a
    track's gap on the 20 ft grid no way out; a band kept at a footpath's gap on the 10 ft grid leaves one."""
    import types

    import pytest as _pt

    from l7r.diagram.hamletgen.ways.track import NoDryExit, connector_dry_exit

    west = [(0.0, 400.0), (484.0, 400.0), (484.0, 600.0), (0.0, 600.0)]
    east = [(516.0, 400.0), (1000.0, 400.0), (1000.0, 600.0), (516.0, 600.0)]
    south = [(0.0, 600.0), (1000.0, 600.0), (1000.0, 1000.0), (0.0, 1000.0)]  # the field: the way out is north, between the bands
    plan = types.SimpleNamespace(W=1000.0, H=1000.0, sink_pond=None, sink_brook=[], envelope=south, grove_bands=[])
    with _pt.raises(NoDryExit):
        connector_dry_exit(plan, (500.0, 590.0), [south], [], [], [west, east])  # type: ignore[arg-type]
    plan.grove_bands = [west, east]
    path = connector_dry_exit(plan, (500.0, 590.0), [south], [], [], [west, east])  # type: ignore[arg-type]
    assert path[-1][1] < 0.0, "out of the frame to the north"
