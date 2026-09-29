"""`hamletgen/ways/corridors.py`: the access tree's roles and the runs the seating reserves (feature 287, plan M3; ways W01,
W03, homes H36, water W57) - each helper on constructed records, the violating case among them."""

import math

from l7r.diagram.hamletgen.ways import corridors as co
from l7r.diagram.hamletgen.ways.geom import WorkedGround


def _house(x, y, rot=180.0, w=40.0, h=28.0):
    return {"x": x, "y": y, "w": w, "h": h, "rot": rot}


def test_the_tree_is_the_connector_and_the_lanes_the_web_draws_for_what_it_owes() -> None:
    assert co.is_tree({"connector": True}) and co.is_tree({"role": co.ACCESS_ROLE}) and co.is_tree({"role": co.FIELD_ROLE})
    assert co.is_tree({"role": co.TARGET_ROLE}) and co.is_tree({"role": co.STRIP_ROLE}) and not co.is_tree({"role": "straggler"}) and not co.is_tree({})


def test_an_end_behind_a_house_is_carried_round_the_nearer_gable_into_the_dooryard() -> None:
    """Water W57: Kuwabata's lane 5 ended 11 ft behind house 1 and counted as its dooryard."""
    from l7r.diagram.settlement.water_ways.lanes import behind_house, reaches_dooryard

    h = _house(0.0, 0.0, rot=0.0)  # the front faces +y
    for end, side in (((10.0, -25.0), 1.0), ((-10.0, -25.0), -1.0)):
        run = co.round_the_gable([(end[0], -200.0), end], h)
        assert behind_house(h, end) and reaches_dooryard(h, run[-1]) and not behind_house(h, run[-1])
        assert math.copysign(1.0, run[-1][0]) == side, "round the gable on the side the end stands"
    tie = co.round_the_gable([(-50.0, -200.0), (0.0, -25.0)], h)
    assert tie[-1][0] < 0, "on a tie, the side the lane came from"
    assert co.round_the_gable([(0.0, -25.0)], h)[-1][0] > 0


def test_spurs_leave_the_network_nearest_first() -> None:
    segs = [((0.0, 0.0), (100.0, 0.0))]
    assert co.samples_along(segs, step=50.0) == [(0.0, 0.0), (50.0, 0.0), (100.0, 0.0)]
    runs = co.spur_runs(segs, (50.0, 60.0), limit=3)
    assert runs[0] == [(50.0, 0.0), (50.0, 60.0)] and len(runs) == 3
    assert co.spur_runs(segs, (50.0, 0.5)) == [r for r in co.spur_runs(segs, (50.0, 0.5)) if math.dist(r[0], r[1]) > 1.0], "no spur of no length"


def test_a_field_run_goes_straight_to_the_bund_or_over_the_brook_at_a_ford() -> None:
    paddy = WorkedGround([[(200.0, -100.0), (400.0, -100.0), (400.0, 100.0), (200.0, 100.0)]])
    segs = [((0.0, 0.0), (0.0, 50.0))]
    straight = co.field_runs(segs, [paddy], 2.5)
    assert straight and straight[0][0] == (0.0, 0.0) and 190.0 < straight[0][-1][0] < 200.0, "stops on the bund, the half-tread off it"
    brook, fords = [(100.0, -500.0), (100.0, 500.0)], [(100.0, 25.0)]
    over = co.field_runs(segs, [paddy], 2.5, brook, fords)
    assert all(len(r) == 4 for r in over), "every run crosses the brook, so every one crosses it at the ford"
    assert any(abs(r[1][0] - 78.0) < 1e-6 and abs(r[2][0] - 122.0) < 1e-6 for r in over), "square over the ford, landing to landing"
    landed = co.field_runs([((78.0, 25.0), (78.0, 26.0))], [paddy], 2.5, brook, fords)
    assert landed[0][0] == (78.0, 25.0) and len(landed[0]) == 3, "a network point on the near landing starts the crossing itself"
    inside = WorkedGround([[(-10.0, -10.0), (10.0, -10.0), (10.0, 60.0), (-10.0, 60.0)]])
    assert co.field_runs(segs, [inside], 2.5) == [], "a network inside the ground has no run to it"


def test_a_routed_field_way_threads_to_a_ford_and_on_to_the_bund() -> None:
    paddy = WorkedGround([[(200.0, -100.0), (400.0, -100.0), (400.0, 100.0), (200.0, 100.0)]])
    segs = [((0.0, 0.0), (0.0, 50.0))]
    straight = lambda a, b: [a, b]  # noqa: E731 - the router stood in for by a ruler
    alone = co.routed_field_runs(segs, paddy, 2.5, straight)
    assert len(alone) == 1 and alone[0][0] == (0.0, 0.0) and 190.0 < alone[0][-1][0] < 200.0
    brook, fords = [(100.0, -500.0), (100.0, 500.0)], [(100.0, 25.0), (100.0, 400.0)]
    over = co.routed_field_runs(segs, paddy, 2.5, straight, brook, fords)
    assert over and over[0][1] == (78.0, 25.0) and over[0][2] == (122.0, 25.0), "to the near landing, over, from the far"
    assert co.routed_field_runs(segs, paddy, 2.5, lambda a, b: [], brook, fords) == [], "a leg the router finds no way for"
    assert co.routed_field_runs([], paddy, 2.5, straight) == []
    inside = WorkedGround([[(-10.0, -10.0), (500.0, -10.0), (500.0, 600.0), (-10.0, 600.0)]])
    assert co.routed_field_runs(segs, inside, 2.5, straight) == [] and co.routed_field_runs(segs, inside, 2.5, straight, brook, fords) == []


def test_the_ground_index_hands_back_only_what_comes_within_the_pad_in_filing_order() -> None:
    """`GroundIndex` prunes: a part whose box comes within the pad of the run is handed back, in the order filed; water near
    a run is found by its box; an outline edge the run crosses is found."""
    ix = co.GroundIndex(
        [[(100.0, -500.0), (100.0, 500.0)], [(0.0, 0.0)]],
        [[(200.0, 200.0), (300.0, 200.0), (300.0, 300.0)]],
        {"houses": [("b", (50.0, 50.0, 60.0, 60.0)), ("a", (0.0, 0.0, 10.0, 10.0)), ("far", (900.0, 900.0, 910.0, 910.0))]},
    )
    run = [(0.0, 20.0), (40.0, 20.0)]
    assert ix.near("houses", run, 31.0) == ["b", "a"], "within 31: both near ones, filing order kept"
    assert ix.near("houses", run, 12.0) == ["a"] and ix.near("houses", run, 5.0) == []
    assert ix.water_near([(60.0, 0.0), (90.0, 0.0)], 12.0) and not ix.water_near([(60.0, 0.0), (90.0, 0.0)], 5.0)
    assert not ix.open_ground([(250.0, 150.0), (250.0, 250.0)]), "into the outline"
    assert ix.open_ground([(250.0, 150.0), (250.0, 190.0)]) and ix.open_ground([(400.0, 150.0), (400.0, 400.0)])
