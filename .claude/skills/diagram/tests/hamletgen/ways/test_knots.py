"""`hamletgen/ways/knots.py`: lane ends that nearly meet are joined (research/questions/0081-village-lanes.drawing.html, "Ends
within 25 ft of one another are joined at a single point") - the knot found on plain lanes and gathered by the settle's step
(feature 328 wave 4, glyph-check of Inashiro)."""

import math

from l7r.diagram.hamletgen.ways import knots as kn
from l7r.diagram.hamletgen.ways.smooth import _KNOT_FT

from .test_settle import _S, CONN


def _ln(*pts, **kw):
    return {"pts": [list(q) for q in pts], "w": 3, **kw}


def test_ends_within_the_joint_tolerance_are_one_node_standing_at_a_fixed_end() -> None:
    lanes = [_ln((0.0, 0.0), (100.0, 0.0)), _ln((100.4, 0.0), (100.0, 80.0), connector=True), _ln((5.0, 5.0))]
    nodes = kn.end_nodes(lanes)
    at = [q for q, ends in nodes if (0, -1) in ends]
    assert at == [(100.4, 0.0)], "the connector's end is the node's point"
    assert len(nodes) == 3, "a one-point lane has no ends"


def test_a_knot_is_two_nodes_within_the_reach_no_one_lane_runs_between() -> None:
    lanes = [
        _ln((0.0, 0.0), (-500.0, 0.0), connector=True),
        _ln((10.0, 100.0), (10.0, 0.0)),  # a T on the connector 10 ft from its head
        _ln((0.0, -15.0), (0.0, 0.0)),  # a 15 ft lane from the head: its own two ends are its join
        _ln((300.0, 100.0), (300.0, 0.0)),  # far off
    ]
    got = kn.knots(lanes)
    pairs = [{q for q in (kn.end_nodes(lanes)[a][0], kn.end_nodes(lanes)[b][0])} for a, b, _d in got]
    assert {(10.0, 0.0), (0.0, 0.0)} in pairs
    assert {(0.0, -15.0), (0.0, 0.0)} not in pairs, "spanned by one lane"
    assert all(d <= _KNOT_FT for _a, _b, d in got) and [d for *_x, d in got] == sorted(d for *_x, d in got)


def test_an_end_is_moved_onto_the_node_with_its_corner_in_the_knot_taken_out_as_a_second_form() -> None:
    p = [(0.0, 100.0), (0.0, 10.0), (3.0, 0.0)]
    first, second = kn.moved_onto(p, -1, (20.0, 0.0))
    assert first == [(0.0, 100.0), (0.0, 10.0), (20.0, 0.0)] and second == [(0.0, 100.0), (20.0, 0.0)]
    assert kn.moved_onto(p[::-1], 0, (20.0, 0.0))[0] == [(20.0, 0.0), (0.0, 10.0), (0.0, 100.0)], "the start end"
    assert kn.moved_onto([(0.0, 100.0), (20.0, 0.0), (3.0, 0.0)], -1, (20.0, 0.0)) == [[(0.0, 100.0), (20.0, 0.0)]], "no point repeated, no form twice"


def test_the_smaller_node_moves_a_fixed_end_never_and_a_refusal_turns_it_round() -> None:
    lanes = [_ln((0.0, 0.0), (-500.0, 0.0), connector=True), _ln((60.0, 100.0), (10.0, 0.0))]
    assert kn.next_gather(lanes, lambda edits: True) == {1: [(60.0, 100.0), (0.0, 0.0)]}, "onto the connector's head"
    assert kn.next_gather(lanes, lambda edits: False) is None, "never the connector onto the lane"
    two = [_ln((0.0, 100.0), (0.0, 0.0)), _ln((0.0, 0.0), (0.0, -100.0)), _ln((60.0, 100.0), (10.0, 0.0))]
    asked: list[dict] = []
    assert kn.next_gather(two, lambda e: asked.append(e) or 2 not in e) == {0: [(0.0, 100.0), (10.0, 0.0)], 1: [(10.0, 0.0), (0.0, -100.0)]}
    assert 2 in asked[0], "the one-end node asked first"
    loop = [_ln((0.0, 0.0), (50.0, 50.0), (0.5, 0.0)), _ln((60.0, 100.0), (10.0, 0.0))]
    assert kn.next_gather(loop, lambda e: 0 not in e) == {1: [(60.0, 100.0), (0.0, 0.0)]}, "a loop's node is not moved, only gathered onto"


def test_the_settle_gathers_two_lanes_tied_onto_the_connector_a_few_feet_apart() -> None:
    """Inashiro's knot in small: two lanes meet the connector 6 ft apart, each from its own farmhouse - one point after."""
    s = _S([CONN, [(-100.0, 150.0), (-100.0, 0.0)], [(-106.0, -150.0), (-106.0, 0.0)]], houses=[(-100.0, 180.0), (-106.0, -180.0)])
    assert kn.knots(s.M["lanes"])
    assert kn.settle_knots(s) == 1
    assert kn.knots(s.M["lanes"]) == []
    assert s.M["lanes"][0]["pts"] == [[0.0, 0.0], [-1000.0, 0.0]], "the connector is not moved"
    assert math.dist(s.M["lanes"][1]["pts"][-1], s.M["lanes"][2]["pts"][-1]) < 1e-6


def test_a_gather_the_matrix_refuses_is_left_and_not_asked_again() -> None:
    s = _S([CONN, [(-100.0, 150.0), (-100.0, 0.0)], [(-106.0, -150.0), (-106.0, 0.0)]], houses=[(-100.0, 180.0), (-106.0, -180.0)])
    s.reshape_lane = lambda ln, pts: False
    assert kn.settle_knots(s) == 0
    assert kn.knots(s.M["lanes"]), "left as it was"


def test_a_gather_that_would_split_the_web_is_refused() -> None:
    """A lane that joins its farmhouse to the connector is not carried off onto an island's end beside it: the island's two
    ends make the bigger node, so the lane's end is asked to move first - and refused, the house left unreached otherwise."""
    lane = [(-100.0, 150.0), (-100.0, 0.0)]
    island = [[(-60.0, 200.0), (-88.0, 15.0)], [(-30.0, 100.0), (-88.0, 15.0)]]  # off the connector, east of the lane
    s = _S([CONN, lane, *island], houses=[(-100.0, 180.0)])
    kn.settle_knots(s)
    assert s.M["lanes"][1]["pts"][-1] == [-100.0, 0.0], "still on the connector"
