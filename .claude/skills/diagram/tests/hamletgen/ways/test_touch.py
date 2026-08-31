"""Split from test_ways.py by feature 173 - see this directory's CLAUDE.md."""

import math

from l7r.diagram import hamletgen as hg

from ._builders import _StubSettlement


def test_touch_junctions_does_not_close_a_short_lane_onto_its_own_start() -> None:
    """Feature 150, Kuwabata seed 21: a 30 ft lane whose two ends both stood near the same spot on
    a neighbor was touched there at BOTH ends and became a 28 ft loop - a hairpin to
    `lanes_bend_like_paths`, invisible to `_smooth_web`, which had already run. A foot within a few
    feet of the lane's other end is that end's own junction, not a new one."""
    main = [(0.0, 0.0), (400.0, 0.0)]
    short = [(200.0, 20.0), (215.0, 32.0), (203.0, 24.0)]
    s = _StubSettlement(lanes=[main, short])
    hg.ways._touch_junctions(s, [], [], [])
    pts = [tuple(q) for q in s.M["lanes"][1]["pts"]]
    assert math.dist(pts[0], (200.0, 0.0)) <= 1.0, "the start is touched down onto the main lane"
    assert math.dist(pts[0], pts[-1]) > 6.0, f"the lane closed onto itself: {pts}"


def test_a_final_pass_junction_ends_the_lane_where_it_first_meets_the_way() -> None:
    """settlement-review 2026-08-28 (Kuwabata lane 9): a lane that came within the touch gap of the way
    it was being joined to part-way along, then ran on beside it and hooked back, left two treads 5-9 ft
    apart enclosing a sliver of ground - a 113 deg V, legal to the bend rule and wrong on the sheet. In
    the final pass the lane is ended where it first meets the way."""
    main = [(0.0, 0.0), (400.0, 0.0)]
    lane = [
        (300.0, 60.0),
        (150.0, -5.0),
        (142.0, 15.0),
    ]  # crosses the main lane near x=161 mid-segment (no vertex within the 4 ft "already met" test), runs 33 ft on and turns back; its far end is out of reach
    s = _StubSettlement(lanes=[main, lane])
    hg.ways._touch_junctions(s, [], [], [], final=True)
    pts = [tuple(q) for q in s.M["lanes"][1]["pts"]]
    assert len(pts) == 2 and pts[0] == (300.0, 60.0), pts
    assert abs(pts[-1][1]) < 0.01 and 155.0 <= pts[-1][0] <= 170.0, pts
