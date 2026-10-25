"""`hamletgen/ways/joints.py`: two lanes meeting end to end are one way to the walker (GM 2026-09-26)."""

from l7r.diagram.hamletgen.ways.joints import as_walked, joints, keeps_the_web, oriented, pulled


def _lanes(s):
    return [ln["pts"] for ln in s.M["lanes"] if ln.get("pts")]


def test_joints_skip_a_loop_a_third_way_and_the_connector() -> None:
    loop = [{"pts": [[0.0, 0.0], [50.0, 0.0]]}, {"pts": [[50.0, 0.0], [0.0, 0.0]]}]
    assert joints(loop) == []
    crossed = [{"pts": [[0.0, 0.0], [50.0, 0.0]]}, {"pts": [[50.0, 0.0], [90.0, 0.0]]}, {"pts": [[50.0, -30.0], [50.0, 30.0]]}]
    assert joints(crossed) == []
    assert joints([{"pts": [[0.0, 0.0], [50.0, 0.0]], "connector": True}, {"pts": [[50.0, 0.0], [90.0, 0.0]]}]) == []
    x, y = oriented([{"pts": [[50.0, 0.0], [0.0, 0.0]]}, {"pts": [[90.0, 0.0], [50.0, 0.0]]}], 0, 0, 1, -1)
    assert x[-1] == y[0] == (50.0, 0.0)


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


def test_lanes_met_end_to_end_are_walked_as_one_way() -> None:
    """`as_walked` (feature 318): two records meeting end to end at a joint are one way, in walking order whichever way each
    was drawn; a lane a third way touches at its end, and a lane of one point, stand alone."""
    lanes = [
        {"pts": [[0.0, 0.0], [100.0, 0.0]]},
        {"pts": [[200.0, 0.0], [100.0, 0.0]]},  # drawn backwards, met end to end at (100, 0)
        {"pts": [[500.0, 0.0], [600.0, 0.0]]},
        {"pts": [[600.0, 0.0], [700.0, 0.0]]},
        {"pts": [[600.0, -50.0], [600.0, 50.0]]},  # a third way through the second joint: no joint there
        {"pts": [[900.0, 900.0]]},
    ]
    ways, owner = as_walked(lanes)
    assert owner[0] == owner[1] and ways[owner[0]] in ([(0.0, 0.0), (100.0, 0.0), (200.0, 0.0)], [(200.0, 0.0), (100.0, 0.0), (0.0, 0.0)])
    assert len({owner[2], owner[3], owner[4]}) == 3, "a joint a third way touches is no joint"
    assert ways[owner[5]] == [(900.0, 900.0)] and len(ways) == 5
    loop = [{"pts": [[0.0, 0.0], [100.0, 0.0], [100.0, 100.0]]}, {"pts": [[100.0, 100.0], [0.0, 100.0], [0.0, 0.0]]}]
    ways, owner = as_walked(loop)
    assert len(ways) == 2 and owner == [0, 1], "two lanes meeting at both ends are a loop, not a joint"


def test_a_chain_met_at_its_first_lane_s_start_is_walked_back_to_its_true_first_lane() -> None:
    """`as_walked` (feature 320): a walk starting at a lane whose START is a joint walks back along the chain to the lane
    with a free end first, so the chain reads as ONE way from that free end, both records mapped to it."""
    lanes = [{"pts": [[10.0, 0.0], [20.0, 0.0]]}, {"pts": [[0.0, 0.0], [10.0, 0.0]]}]
    assert joints(lanes) == [(0, 0, 1, -1)]
    ways, owner = as_walked(lanes)
    assert owner == [0, 0] and ways == [[(0.0, 0.0), (10.0, 0.0), (20.0, 0.0)]], "one way, walked from lane 1's free end"
