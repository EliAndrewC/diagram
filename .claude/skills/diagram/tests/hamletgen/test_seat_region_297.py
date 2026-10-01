"""Feature 297, FR-001 (plan B1): the seat region - where a homestead can stand and a door can reach the access tree."""

from __future__ import annotations

from types import SimpleNamespace

import numpy as np

from l7r.diagram.hamletgen.homesteads.region import SeatRegion, flood_from, free_components, seat_window, touches_many
from l7r.diagram.settlement import Settlement
from l7r.diagram.settlement._geom.region import Region
from l7r.diagram.settlement.rolling.access import AccessTree


def _open(W: float = 1400.0) -> Settlement:
    s = Settlement(W, W, seed=3)
    s.meta(name="V", scale="hamlet", ftpx=1, toscale=True, households=10, down_deg=90, water_flow=90, nucleated=True)
    s._nucleated = True
    return s


def test_the_free_cells_are_labeled_by_their_four_connected_components() -> None:
    free = np.array([[1, 1, 0, 1], [0, 1, 0, 1], [1, 0, 0, 1], [1, 1, 0, 0]], dtype=bool)
    lab = free_components(free)
    assert (lab == 0).sum() == (~free).sum()
    assert lab[0, 0] == lab[0, 1] == lab[1, 1], "a run joined to the run below it"
    assert lab[0, 3] == lab[2, 3] and lab[0, 3] != lab[0, 0]
    assert lab[2, 0] == lab[3, 1] and lab[2, 0] != lab[1, 1], "diagonal is not 4-connected"
    lab2 = free_components(np.array([[1, 0, 1], [1, 1, 1]], dtype=bool))
    assert lab2[0, 0] == lab2[0, 2], "two runs joined through the row below (the union step)"


def test_the_flood_reaches_only_free_ground_connected_to_the_tree() -> None:
    r = Region((0.0, 0.0, 400.0, 400.0), 8.0)
    r.line([(200.0, 0.0), (200.0, 400.0)], 4.0)  # a wall down the middle
    reach = flood_from(r, [((40.0, 100.0), (120.0, 100.0))], 3.0)
    assert reach[25, 5] and not reach[25, 45], "the tree's side only"
    assert not flood_from(r, [], 3.0).any()
    full = Region((0.0, 0.0, 40.0, 40.0), 8.0)
    full.rect(0.0, 0.0, 40.0, 40.0)
    assert not flood_from(full, [((5.0, 5.0), (30.0, 5.0))], 1.0).any(), "no free ground at all"


def test_a_box_touches_reach_where_any_of_its_cells_is_reachable() -> None:
    r = Region((0.0, 0.0, 80.0, 80.0), 8.0)
    reach = np.zeros((10, 10), dtype=bool)
    reach[2, 3] = True
    sat = np.zeros((11, 11), dtype=np.int32)
    sat[1:, 1:] = reach.astype(np.int32).cumsum(0).cumsum(1)
    got = touches_many(sat, r, [20.0, 60.0], [10.0, 60.0], [30.0, 70.0], [20.0, 70.0])
    assert got.tolist() == [True, False]


def test_a_seat_is_offered_where_a_side_fits_and_its_yard_reaches_the_tree() -> None:
    s = _open()
    s._free_ground = SimpleNamespace(taken={(i, j) for i in range(0, 20) for j in range(0, 175)}, cell=8.0, x0=0.0, y0=0.0)  # the west strip, 160 px, surely taken
    s.placed = []
    region = SeatRegion(s, (0.0, 0.0, 1400.0, 1400.0))
    assert region.cell == 8.0 and region.window[0] == 0.0
    assert region.offer([]) == []
    assert region.offer([(60.0, 700.0), (700.0, 700.0)]) == [False, True], "on taken ground / open ground, no tree: reach not asked"
    s._access = AccessTree(7.0)
    s._access.add((600.0, 900.0), (900.0, 900.0))
    s.M["houses"] = [{"x": 1.0, "y": 1.0, "wood_share": {"seats": [(1000.0, 1000.0)]}}]
    s.placed = [(500.0, 500.0, 30.0, 30.0)]
    assert region.offer([(700.0, 700.0)]) == [True], "a door with free ground to the tree"
    fence = Region((0.0, 0.0, 1400.0, 1400.0), 8.0)
    region.buildable.line([(400.0, 300.0), (1100.0, 300.0)], 6.0)  # cut a pocket north of a wall, no way to the tree
    region.buildable.line([(400.0, 300.0), (400.0, 100.0)], 6.0)
    region.buildable.line([(1100.0, 300.0), (1100.0, 100.0)], 6.0)
    region.buildable.line([(400.0, 100.0), (1100.0, 100.0)], 6.0)
    region._reach = None
    assert region.offer([(750.0, 180.0)]) == [False], "free ground, but walled off from the tree"
    _ = fence


def test_the_seat_window_is_the_chains_grown_by_reach_and_a_pitch() -> None:
    s = _open()
    assert seat_window(s, 100.0) == (0.0, 0.0, 1400.0, 1400.0), "no chains: the canvas"
    s._site_chains = [[((600.0, 600.0), (700.0, 650.0), (0.0, 1.0))]]
    x0, y0, x1, y1 = seat_window(s, 100.0)
    assert 0.0 < x0 < 600.0 and x1 > 700.0 and y1 > 650.0
