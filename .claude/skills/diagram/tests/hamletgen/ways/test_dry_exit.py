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
