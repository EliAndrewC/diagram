"""Feature 297, FR-001 (plan B1): the seat region - where a homestead can stand and a door can reach the access tree."""

from __future__ import annotations

from types import SimpleNamespace

import numpy as np

from l7r.diagram.hamletgen.homesteads.region import SeatRegion, flood_from, free_components, touches_many
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
    region.lane.line([(400.0, 300.0), (1100.0, 300.0)], 6.0)  # cut a pocket of lane ground north of a wall, no way to the tree
    region.lane.line([(400.0, 300.0), (400.0, 100.0)], 6.0)
    region.lane.line([(1100.0, 300.0), (1100.0, 100.0)], 6.0)
    region.lane.line([(400.0, 100.0), (1100.0, 100.0)], 6.0)
    region._reach = None
    assert region.offer([(750.0, 180.0)]) == [False], "free ground, but walled off from the tree"
    _ = fence


def test_a_seat_outside_the_regions_window_is_offered_unjudged() -> None:
    """Feature 318 (the perf-audit's correction): the window bounds the rasters' cost, never where a house may stand - a seat
    outside it is offered for the placer's own tests to decide, though the ground there is taken."""
    s = _open()
    s._free_ground = SimpleNamespace(taken={(i, j) for i in range(0, 175) for j in range(0, 175)}, cell=8.0, x0=0.0, y0=0.0)
    s.placed = []
    region = SeatRegion(s, (400.0, 400.0, 800.0, 800.0))
    assert region.offer([(600.0, 600.0), (1100.0, 600.0), (600.0, 100.0)]) == [False, True, True], "inside: judged; outside: offered"


def test_the_seating_window_grows_with_the_households_and_stays_on_the_canvas() -> None:
    """`boundary.seating_window` (feature 318): the seat out twice the radius the households' seating ground would fill
    (`SEATING_GROUND_FT` each), clipped to the canvas."""
    import math

    from l7r.diagram.hamletgen.consts import SEATING_GROUND_FT
    from l7r.diagram.hamletgen.homesteads.boundary import FREE_GROUND_CELL, seating_window

    s = _open(4000.0)
    r = 2.0 * SEATING_GROUND_FT * math.sqrt(15 / math.pi)
    lo = math.floor((2000.0 - r) / FREE_GROUND_CELL) * FREE_GROUND_CELL  # snapped to the canvas's own cell grid
    assert seating_window(s, (2000.0, 2000.0), 15) == (lo, lo, 2000.0 + r, 2000.0 + r)
    assert lo % FREE_GROUND_CELL == 0.0 and 2000.0 - r - FREE_GROUND_CELL < lo <= 2000.0 - r
    big = seating_window(s, (2000.0, 2000.0), 40)
    assert big[2] - big[0] > 2 * r, "more households, a wider window"
    assert seating_window(s, (100.0, 3950.0), 15) == (0.0, math.floor((3950.0 - r) / FREE_GROUND_CELL) * FREE_GROUND_CELL, 100.0 + r, 4000.0), "clipped to the canvas"
    assert seating_window(s, (2000.0, 2000.0), 0) == seating_window(s, (2000.0, 2000.0), 1)


def test_a_seat_whose_box_crosses_the_windows_edge_is_offered_and_reach_runs_round_the_outside() -> None:
    """Feature 318: a seat inside the window whose envelope crosses its edge is judged by no raster cell of its own - offered;
    and with an access tree, ground cut off from it inside the window but open to the window's inner edge is reached."""
    s = _open()
    s._free_ground = SimpleNamespace(taken=set(), cell=8.0, x0=0.0, y0=0.0)
    s.placed = []
    region = SeatRegion(s, (400.0, 400.0, 800.0, 800.0))
    near_edge = 800.0 - min(b[2] for b in region.sides) + 4.0  # its east box reaches 4 px past the window's east edge
    assert region.offer([(near_edge, 600.0)]) == [True]
    tree = AccessTree(half=7.0)
    tree.add((420.0, 420.0), (460.0, 420.0))
    s._access = tree
    walled = SeatRegion(s, (400.0, 400.0, 800.0, 800.0))
    walled.buildable.line([(500.0, 400.0), (500.0, 800.0)], 4.0)  # a wall between the tree and the east of the window
    walled._reach = None
    assert walled.offer([(650.0, 600.0)]) == [True], "reached round the outside, through the window's open east edge"


def test_a_yard_opens_onto_lane_ground_connected_to_the_way_out() -> None:
    """`SeatRegion.opens` (feature 318, FR-012): the yard (its house where it has none), grown by the half-width and a cell,
    touching reached lane ground; a yard past the window is counted open; a pocket walled off from the way out is not."""
    s = _open()
    s.placed = []
    s._access = AccessTree(7.0)
    s._access.add((600.0, 900.0), (900.0, 900.0))
    region = SeatRegion(s, (0.0, 0.0, 1400.0, 1400.0))
    assert region.opens({"boxes": {"yard": (700.0, 700.0, 30.0, 20.0)}}), "open ground to the way out"
    assert region.opens({"house": (720.0, 700.0, 40.0, 20.0)}), "no yard: its house"
    for a, b in (((400.0, 300.0), (1100.0, 300.0)), ((400.0, 300.0), (400.0, 100.0)), ((1100.0, 300.0), (1100.0, 100.0)), ((400.0, 100.0), (1100.0, 100.0))):
        region.lane.line([a, b], 6.0)
    region._reach = None
    assert not region.opens({"boxes": {"yard": (750.0, 200.0, 30.0, 20.0)}}), "walled off from the way out"
    assert region.opens({"boxes": {"yard": (5.0, 700.0, 30.0, 20.0)}}), "past the window's edge: counted open"


def test_lane_ground_grows_the_taken_cells_by_one_and_paints_the_water_courses() -> None:
    """`LaneGround` (feature 318): a taken cell closes its eight neighbors too; and the water courses (`_site_corridors.water`)
    are painted onto lane ground at their clearance, so a cluster is not grown across a brook no way can cross."""
    from l7r.diagram.hamletgen.homesteads.region import LaneGround

    r = Region((0.0, 0.0, 80.0, 80.0), 8.0)
    r.cells({(5, 5)}, 8.0, 0.0, 0.0)
    a = LaneGround(r).array()
    assert a[5, 5] and a[4, 4] and a[6, 6] and a[4, 6] and a[6, 4] and not a[2, 2]
    s = _open()
    s.placed = []
    s._site_corridors = SimpleNamespace(water=[((0.0, 700.0), (1400.0, 700.0), 30.0)])
    region = SeatRegion(s, (0.0, 0.0, 1400.0, 1400.0))
    assert region.lane.taken(700.0, 700.0) and not region.lane.taken(700.0, 300.0)
