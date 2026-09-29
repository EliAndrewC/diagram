"""Feature 287, plan M3's seat half (homes H16, ways W01): the access-corridor tree reserved at seating."""

from __future__ import annotations

import pytest

from l7r.diagram import hamletgen as hg
from l7r.diagram.settlement import Settlement
from l7r.diagram.settlement.rolling import access
from l7r.diagram.settlement.rolling.access import AccessTree, _seg_box_gap, access_corridor, corridor_clear, doors_of, reserve, start_tree
from tests.hamletgen._builders import a_plan


def _open(W: float = 1400.0) -> Settlement:
    s = Settlement(W, W, seed=3)
    s.meta(name="V", scale="hamlet", ftpx=1, toscale=True, households=10, down_deg=90, water_flow=90, nucleated=True)
    s._nucleated = True
    return s


def test_the_segment_box_gap_is_zero_where_they_meet_and_the_true_gap_elsewhere() -> None:
    box = (0.0, 0.0, 10.0, 10.0)
    assert _seg_box_gap((0.0, 0.0), (20.0, 0.0), box) == 0.0, "an end inside"
    assert _seg_box_gap((-20.0, 0.0), (20.0, 0.0), box) == 0.0, "a crossing"
    assert _seg_box_gap((10.0, -20.0), (10.0, 20.0), box) == 5.0
    assert _seg_box_gap((20.0, 20.0), (30.0, 30.0), box) == ((15**2) * 2) ** 0.5


def test_the_tree_covers_a_box_its_strip_meets_and_offers_its_nearest_points() -> None:
    tree = AccessTree(7.0)
    tree.add((0.0, 0.0), (100.0, 0.0))
    tree.add((0.0, 200.0), (100.0, 200.0))
    assert tree.covers_box((50.0, 10.0, 10.0, 8.0)), "the box's edge 6 px off the line: inside the 7 px strip"
    assert not tree.covers_box((50.0, 10.0, 10.0, 4.0)), "8 px off: clear"
    assert not tree.covers_box((50.0, 30.0, 10.0, 10.0))
    assert not tree.covers_box((500.0, 0.0, 10.0, 10.0)), "far along: the index returns nothing"
    got = tree.targets((50.0, 60.0))
    assert got[0] == (50.0, 0.0) and (50.0, 200.0) in got and (0.0, 0.0) in got, "the nearest point first, then the points along"


def test_a_homestead_leaves_by_its_dooryard_never_a_back_wall() -> None:
    """The forecourt, then the yard's far edge and its two flanks - every door in the dooryard (ways W57)."""
    doors = doors_of({"house": (0.0, 0.0, 40.0, 20.0), "yard": (0.0, 30.0, 30.0, 20.0)}, 7.0)
    assert doors == [(0.0, 30.0), (0.0, 40.0), (-28.0, 30.0), (28.0, 30.0)], "the flanks carried past the gable: 20 + 7 + 1"
    assert all(y > 10.0 for _x, y in doors), "none behind or beside the house"
    assert doors_of({"house": (0.0, 0.0, 10.0, 20.0), "yard": (0.0, 30.0, 30.0, 20.0)})[2] == (-15.0, 30.0), "a yard wider than its house"
    assert doors_of({"house": (0.0, 0.0, 40.0, 20.0), "yard": None}) == [(0.0, 12.0)], "no yard: a step off the front wall"


def test_the_exit_strip_starts_the_tree_and_the_manifest_records_it() -> None:
    s = _open()
    tree = start_tree(s, (100.0, 100.0), (0.0, 1.0), 50.0)
    assert s._access is tree and tree.segs == [((100.0, 100.0), (100.0, 150.0))]
    assert s.M["access_exit"] == [[100.0, 100.0], [100.0, 150.0]] and s.M["access_corridors"] == []
    reserve(s, ((0.0, 0.0), (100.0, 100.0)))
    assert len(tree.segs) == 2 and s.M["access_corridors"] == [{"pts": [[0.0, 0.0], [100.0, 100.0]]}]
    reserve(s, ((1.0, 1.0), (2.0, 2.0)), of=(5.0, 5.0))
    assert s.M["access_corridors"][-1] == {"pts": [[1.0, 1.0], [2.0, 2.0]], "of": [5.0, 5.0]}


def test_a_corridor_through_another_homestead_or_its_own_house_is_refused() -> None:
    """W01 (a): two placed homesteads close the only straight run to the tree; a seat with a clear run is admitted."""
    s = _open()
    start_tree(s, (700.0, 300.0), (1.0, 0.0), 300.0)
    s.placed.append((700.0, 500.0, 120.0, 60.0))  # a neighbor square across the direct run to the strip
    blocked = s._bundle_geom(700.0, 700.0, 46.0, 28.0, "SE", rot=0.0)
    assert not corridor_clear(s, doors_of(blocked)[0], (700.0, 300.0), blocked)
    assert not corridor_clear(s, (700.0, 740.0), (700.0, 650.0), blocked), "a run through its own house"
    got = access_corridor(s, blocked)
    assert got is not None and got[1][0] > 800.0, "...but a point further along the strip is reached round the neighbor"
    s.placed.append((640.0, 620.0, 120.0, 400.0))
    s.placed.append((760.0, 620.0, 120.0, 400.0))
    s.placed.append((700.0, 800.0, 400.0, 60.0))
    assert access_corridor(s, blocked) is None, "hemmed in on every side: refused"
    open_ = s._bundle_geom(1000.0, 300.0, 46.0, 28.0, "SE", rot=0.0)
    assert access_corridor(s, open_) is not None


def test_a_corridor_over_ground_the_boundary_refuses_is_refused() -> None:
    plan = a_plan(households=10)
    plan.seat = hg.seat_cluster(plan)
    s = _open()
    s.field_polys.append(list(plan.envelope))
    cx, cy = float(plan.seat["cx"]), float(plan.seat["cy"])
    s.block_polys.append([(cx + 150.0, cy - 40.0), (cx + 250.0, cy - 40.0), (cx + 250.0, cy + 40.0), (cx + 150.0, cy + 40.0)])  # no-build ground
    hg.homesteads.boundary.install_site_boundary(s, plan)
    start_tree(s, (cx, cy), plan.seat["out"], 100.0)
    geom = s._bundle_geom(cx, cy, 46.0, 28.0, "SE", rot=0.0)
    assert not corridor_clear(s, (cx, cy + 40.0), (700.0, 700.0), geom), "into the paddy: the field side of a chord"
    assert not corridor_clear(s, (cx + 60.0, cy), (cx + 300.0, cy), geom), "through the outline of the other ground"
    assert corridor_clear(s, (cx - 60.0, cy), (cx - 300.0, cy), geom), "open ground"


def test_no_tree_admits_no_corridor_and_the_placer_asks_none() -> None:
    s = _open()
    geom = s._bundle_geom(500.0, 500.0, 46.0, 28.0, "SE")
    assert access_corridor(s, geom) is None
    s._seat_search = {"candidates": 0, "placer_calls": 0, "positions": 0, "rects": 0, "rounds": 0}
    assert s._parts_fit(geom) and "access" not in geom


def test_the_placer_admits_a_seat_only_with_its_corridor_and_reserves_it() -> None:
    """The seat half end to end: `_parts_fit` refuses a boxed-in seat, admits an open one with its corridor on the geometry,
    `try_place` reserves the corridor, and the envelope of a later homestead on the corridor is refused."""
    s = _open()
    s._seat_search = {"candidates": 0, "placer_calls": 0, "positions": 0, "rects": 0, "rounds": 0}
    start_tree(s, (700.0, 300.0), (0.0, -1.0), 200.0)
    assert s.try_place(700.0, 520.0, "plain")
    assert len(s.M["access_corridors"]) == 1 and len(s._access.segs) == 2
    a, b = s._access.segs[1]
    mid = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
    assert s._envelope_blocked((mid[0], mid[1], 20.0, 20.0)) is True, "no homestead on a reserved corridor"
    s.placed.extend([(640.0, 900.0, 60.0, 400.0), (760.0, 900.0, 60.0, 400.0), (700.0, 1120.0, 200.0, 60.0), (700.0, 760.0, 200.0, 40.0)])
    geom = s._bundle_geom(700.0, 900.0, 46.0, 28.0, "SE", rot=0.0)
    assert not s._parts_fit(geom), "boxed in: no corridor, no seat"
    assert access.TARGETS_TRIED >= 2


def test_a_corridor_the_ways_ground_test_refuses_is_refused_and_the_exit_strip_turns_off_it() -> None:
    """The ways' own ground test, installed by the hamlet's seating (`_corridor_ground`): a corridor it refuses is refused
    though the site boundary admits it; the exit strip is held to it, turned off its bearing where refused straight out,
    and a margin whose every turn is refused has no way out."""
    s = _open()
    start_tree(s, (100.0, 100.0), (0.0, 1.0), 50.0)
    geom = s._bundle_geom(1000.0, 1000.0, 46.0, 28.0, "SE", rot=0.0)
    assert corridor_clear(s, (500.0, 500.0), (500.0, 300.0), geom), "no test installed (a village roll): the boundary's alone"
    s._corridor_ground = lambda run: run[-1][0] <= 500.0  # a stand-in: ground east of x = 500 is unlawful
    assert corridor_clear(s, (500.0, 500.0), (500.0, 300.0), geom)
    assert not corridor_clear(s, (500.0, 500.0), (700.0, 300.0), geom), "the ground test refuses it"
    assert access.exit_bearing(s, (500.0, 500.0), (0.0, -1.0), 100.0) == (0.0, -1.0), "straight out"
    u = access.exit_bearing(s, (500.0, 500.0), (1.0, 0.0), 100.0)
    assert u is not None and u[0] < 1e-9 and abs(u[1]) == pytest.approx(1.0), "east refused: turned a quarter"
    s._corridor_ground = lambda run: False
    assert access.exit_bearing(s, (500.0, 500.0), (0.0, -1.0), 100.0) is None


def test_a_tree_behind_the_house_is_reached_round_the_gable_from_the_dooryard() -> None:
    """No straight run from the dooryard reaches a tree behind the house past its neighbors; a flank door carried back
    along the gable does, in two legs - and each leg is its own record, the first naming the house."""
    s = _open()
    start_tree(s, (720.0, 470.0), (0.0, -1.0), 20.0)  # the tree starts just behind the back wall: every straight run crosses the house
    geom = s._bundle_geom(720.0, 520.0, 46.0, 28.0, "SE", rot=0.0)
    got = access_corridor(s, geom)
    assert got is not None and len(got) == 3, "round the gable"
    door, turn, _q = got
    assert door[1] > 520.0 and turn[1] < 520.0 - 14.0 - 7.0, "leaves the dooryard, turns past the back wall"
    assert access.round_the_gable(geom, door, 7.0) == turn
    reserve(s, got, of=(720.0, 520.0))
    recs = s.M["access_corridors"]
    assert len(recs) == 2 and recs[0]["of"] == [720.0, 520.0] and "of" not in recs[1] and recs[0]["pts"][1] == recs[1]["pts"][0]
    assert access.legs(got) == [(door, turn), (turn, _q)]


def test_what_stands_is_asked_once_while_nothing_of_it_changes() -> None:
    s = _open()
    start_tree(s, (100.0, 100.0), (0.0, 1.0), 50.0)
    calls: list[int] = []
    s._corridor_ground = lambda run: calls.append(1) or True
    geom = s._bundle_geom(1000.0, 1000.0, 46.0, 28.0, "SE", rot=0.0)
    assert corridor_clear(s, (500.0, 500.0), (500.0, 300.0), geom) and corridor_clear(s, (500.0, 500.0), (500.0, 300.0), geom)
    assert len(calls) == 1, "remembered"
    s.placed.append((900.0, 900.0, 10.0, 10.0))
    assert corridor_clear(s, (500.0, 500.0), (500.0, 300.0), geom) and len(calls) == 2, "a box placed since: asked again"
    start_tree(s, (100.0, 100.0), (0.0, 1.0), 50.0)
    assert "_corridor_memo" not in s.__dict__, "a new seating forgets"
