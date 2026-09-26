"""`hamletgen/ways/joints.py`: two lanes meeting end to end are one way to the walker (GM 2026-09-26)."""

import math

from l7r.diagram.hamletgen.ways.joints import joints, keeps_the_web, oriented, pulled, straighten_joints, tee, unhooked

from ._builders import _webbed


def _lanes(s):
    return [ln["pts"] for ln in s.M["lanes"] if ln.get("pts")]


def test_a_fold_at_a_joint_becomes_a_t() -> None:
    # Inashiro's bamboo stand: lane 8 comes down, turns back west to where lane 7 begins, and lane 7 runs back east
    s = _webbed([{"pts": [[100.0, 100.0], [200.0, 100.0], [200.0, 140.0], [160.0, 150.0]], "w": 3}, {"pts": [[160.0, 150.0], [300.0, 160.0]], "w": 3}])
    assert joints(s.M["lanes"]) == [(0, -1, 1, 0)]
    assert straighten_joints(s, [], [], []) == 1
    stem, bar = s.M["lanes"][0]["pts"], s.M["lanes"][1]["pts"]
    assert stem[-2] == [200.0, 140.0] and abs(stem[-1][0] - 199.1) < 0.2, "the stem drops from its last vertex to the bar's side"
    assert bar == [[160.0, 150.0], [300.0, 160.0]], "the bar keeps the ground it served"


def test_a_jog_across_a_chain_of_joints_is_pulled_straight() -> None:
    # Inashiro's northeast lane: three records, one line, a 3 ft step in the middle one
    s = _webbed([{"pts": [[100.0, 300.0], [300.0, 300.0]], "w": 3}, {"pts": [[300.0, 300.0], [310.0, 303.0], [320.0, 300.0]], "w": 3}, {"pts": [[320.0, 300.0], [500.0, 300.0]], "w": 3}])
    assert straighten_joints(s, [], [], []) == 2
    assert _lanes(s) == [[[100.0, 300.0], [500.0, 300.0]]]


def test_a_cart_route_and_a_footpath_meeting_end_to_end_stay_two_ways() -> None:
    s = _webbed([{"pts": [[100.0, 500.0], [300.0, 500.0]], "w": 5}, {"pts": [[300.0, 500.0], [310.0, 503.0], [500.0, 500.0]], "w": 3}])
    assert straighten_joints(s, [], [], []) == 0


def test_a_joint_with_nothing_to_straighten_is_left_alone() -> None:
    s = _webbed([{"pts": [[100.0, 700.0], [300.0, 700.0]], "w": 3}, {"pts": [[300.0, 700.0], [300.0, 900.0]], "w": 3}])
    wall = [[(190.0, 790.0), (210.0, 790.0), (210.0, 810.0), (190.0, 810.0)]]  # across the corner's chord
    assert straighten_joints(s, wall, [], []) == 0


def test_a_fold_no_t_can_mend_is_left_for_the_bends_check() -> None:
    # a lane doubling straight back along the next: both T links cross the same block
    s = _webbed([{"pts": [[100.0, 1000.0], [200.0, 1000.0]], "w": 3}, {"pts": [[200.0, 1000.0], [100.0, 1010.0]], "w": 3}])
    block = [[(90.0, 1003.0), (110.0, 1003.0), (110.0, 1007.0), (90.0, 1007.0)]]
    assert joints(s.M["lanes"]) == [(0, -1, 1, 0)]
    assert straighten_joints(s, block, [], []) == 0


def test_joints_skip_a_loop_a_third_way_and_the_connector() -> None:
    loop = [{"pts": [[0.0, 0.0], [50.0, 0.0]]}, {"pts": [[50.0, 0.0], [0.0, 0.0]]}]
    assert joints(loop) == []
    crossed = [{"pts": [[0.0, 0.0], [50.0, 0.0]]}, {"pts": [[50.0, 0.0], [90.0, 0.0]]}, {"pts": [[50.0, -30.0], [50.0, 30.0]]}]
    assert joints(crossed) == []
    assert joints([{"pts": [[0.0, 0.0], [50.0, 0.0]], "connector": True}, {"pts": [[50.0, 0.0], [90.0, 0.0]]}]) == []
    x, y = oriented([{"pts": [[50.0, 0.0], [0.0, 0.0]]}, {"pts": [[90.0, 0.0], [50.0, 0.0]]}], 0, 0, 1, -1)
    assert x[-1] == y[0] == (50.0, 0.0)


def test_tee_refuses_what_it_cannot_improve() -> None:
    assert tee([(0.0, 0.0), (10.0, 0.0)], [(10.0, 0.0), (10.0, 10.0)], [], [], []) is None, "the foot is the joint"
    y = [(10.0, 0.0), (-10.0, 0.0)]
    assert tee([(0.0, 2.0), (10.0, 0.0)], y, [], [], []) is None, "already touching, and nothing left to keep"
    assert tee([(-5.0, 30.0), (0.0, 2.0), (10.0, 0.0)], y, [], [], []) == [(-5.0, 30.0), (0.0, 2.0)], "already touching: it stops there"
    assert tee([(0.0, 0.0), (100.0, 0.0), (60.0, 10.0)], [(60.0, 10.0), (60.0, -40.0)], [], [], []) is None, "the new last turn is itself a hairpin"
    hard = [[(98.0, 10.0), (104.0, 10.0), (104.0, 30.0), (98.0, 30.0)]]
    assert tee([(0.0, 0.0), (100.0, 0.0), (130.0, 45.0)], [(130.0, 45.0), (40.0, 50.0)], hard, [], []) is None, "the link is not walkable"


def test_pulled_takes_the_furthest_chord_allowed() -> None:
    pts = [(0.0, 0.0), (1.0, 1.0), (2.0, 0.0), (3.0, 1.0)]
    assert pulled(pts, lambda a, b: True) == [(0.0, 0.0), (3.0, 1.0)]
    assert pulled(pts, lambda a, b: b == a + 1) == pts


def test_keeps_the_web_refuses_a_lost_junction_a_split_and_a_stranded_house() -> None:
    other = {"pts": [[50.0, 3.0], [50.0, 60.0]]}
    lanes = [{"pts": [[0.0, 0.0], [100.0, 0.0]]}, other]
    old = [(0.0, 0.0), (100.0, 0.0)]
    assert keeps_the_web(lanes, {0}, old, [(0.0, 0.0), (0.0, 50.0)], []) is False, "the other lane's end no longer meets a way"
    tee_web = [{"pts": [[0.0, 0.0], [98.0, 0.0]]}, {"pts": [[100.0, -50.0], [100.0, 50.0]]}]
    assert keeps_the_web(tee_web, {0}, [(0.0, 0.0), (98.0, 0.0)], [(0.0, 0.0), (50.0, 0.0)], []) is False, "the web would fall into two pieces"
    assert keeps_the_web(lanes, {0}, old, [(0.0, 0.0), (100.0, 0.0), (100.0, 1.0)], [(50.0, 90.0)]) is True
    assert keeps_the_web([{"pts": [[0.0, 0.0], [100.0, 0.0]]}], {0}, old, [(0.0, 400.0), (100.0, 400.0)], [(50.0, 10.0)]) is False, "a farmhouse loses its way"


def test_unhooked_takes_the_hook_off_a_lane_end() -> None:
    assert unhooked([(0.0, 0.0), (100.0, 0.0), (130.0, 5.0)], []) is None, "a long last leg is a route, not a hook"
    assert unhooked([(0.0, 0.0), (100.0, 0.0), (108.0, 6.0)], []) is None, "a shallow last turn is a bend"
    assert unhooked([(0.0, 0.0), (100.0, 0.0), (92.0, 6.0)], []) == [(0.0, 0.0), (100.0, 0.0)], "a nub reaching nothing"
    # Kashikawa: the vertex before the hook already stands on a way the hook met
    on = [(98.0, -40.0), (98.0, 40.0)]
    assert unhooked([(0.0, 0.0), (100.0, 0.0), (94.0, 8.0)], [on]) == [(0.0, 0.0), (100.0, 0.0)]
    # the leg before overshoots the way it joins: cut where it crosses
    o = [(210.0, 650.0), (210.0, 720.0)]
    assert unhooked([(100.0, 700.0), (220.0, 700.0), (212.0, 694.0)], [o]) == [(100.0, 700.0), (210.0, 700.0)]
    assert unhooked([(100.0, 700.0), (220.0, 700.0), (212.0, 694.0)], [o, [(212.0, 690.0), (212.0, 600.0)]]) is None, "two ways met: no single cut"
    assert unhooked([(100.0, 700.0), (220.0, 700.0), (212.0, 694.0)], [[(212.0, 690.0), (260.0, 600.0)]]) is None, "the leg never reaches the way"


def test_the_pass_takes_hooks_off_both_ends() -> None:
    s = _webbed([{"pts": [[108.0, 1206.0], [100.0, 1200.0], [300.0, 1200.0], [292.0, 1206.0]], "w": 3}, {"pts": [[500.0, 1200.0], [600.0, 1200.0], [592.0, 1206.0]], "w": 3}])
    s.M["lanes"][1]["connector"] = True  # the cart route out is never re-shaped here, hook or no hook
    assert straighten_joints(s, [], [], []) == 2
    assert s.M["lanes"][0]["pts"] == [[100.0, 1200.0], [300.0, 1200.0]]
    assert math.isclose(s.M["lanes"][1]["pts"][-1][0], 592.0)
