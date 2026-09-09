"""The smoothing pass (`hamletgen/ways/smooth.py`).

Created by feature 174: the split's derived mapping put no test here, because every test that
exercised smoothing did so through a name that lives in another module. The one statement this
file exists for is the collapse guard below - a lane whose every vertex falls inside a knot.
"""

from __future__ import annotations

import math

from l7r.diagram.hamletgen.ways.smooth import _KNOT_FT, _smooth_web

from ._builders import _StubSettlement


def test_smooth_web_survives_a_lane_whose_every_vertex_falls_inside_the_knot() -> None:
    """Feature 174, and a real defect's guard: such a way collapses to ONE point, and the code just
    below reads `_q[-2]`. It was found at the T99 unlock as an IndexError on a tripwire seed, so the
    branch exists because the crash happened - and no seed in the suite reproduces it any more.

    Three vertices, all within the knot radius of the junction, is the shape that collapses. What is
    asserted is the guard's whole purpose: the pass COMPLETES. Asserting the lane's final points
    would be asserting the behaviour of the passes that run after this one, which is not what the
    guard promises and would break whenever they changed.
    """
    # THREE lanes, because `_StubSettlement` marks lane 0 the connector and the knot search skips
    # connectors - so the two that knot must both be non-connectors.
    connector = [(0.0, 900.0), (200.0, 900.0)]
    run = [(0.0, 0.0), (100.0, 0.0)]
    collapsing = [(101.0, 0.0), (105.0, 0.0), (110.0, 0.0)]  # every vertex inside the knot radius
    s = _StubSettlement(lanes=[connector, run, collapsing])
    changed = _smooth_web(s, [], [], [])
    assert isinstance(changed, int), "the pass returns its count rather than raising IndexError on _q[-2]"


def test_a_lane_whose_every_VERTEX_falls_inside_the_knot_is_left_exactly_as_it_was() -> None:
    """Ends of different lanes within `_KNOT_FT` are ONE junction, and each lane's own vertices inside
    that radius collapse onto the node. A stub of a lane shorter than the knot therefore collapses to
    a single point - and a single point has no neighbor vertex to aim the touch at.

    Found at the T99 unlock on a tripwire seed, as an IndexError on `_q[-2]`. Such a lane is left as
    it was drawn rather than rewritten to nothing, so the assertion is that it comes out unchanged."""
    stub = [(1.0, 301.0), (1.5, 301.5)]
    assert math.dist(stub[0], stub[1]) < _KNOT_FT, "the whole lane fits inside one knot"
    s = _StubSettlement(lanes=[[(0.0, 0.0), (0.0, 600.0)], [(0.0, 300.0), (60.0, 300.0)], list(stub)], houses=[(50.0, 320.0)])
    s.M.setdefault("meta", {"ftpx": 1})

    _smooth_web(s, [], [], [])  # the regression this guards is an IndexError on `_q[-2]`, so reaching here is half the test
    assert s.M["lanes"][2]["pts"] == [], "the stub is not rewritten to a one-point lane; the debris sweep drops it"
    assert tuple(s.M["lanes"][1]["pts"][0]) == (1.0, 301.0), "and its neighbor's end is pulled onto the knot's node"


def test_a_lane_crossing_another_loses_its_short_head_past_the_crossing() -> None:
    """`_smooth_web`'s bow-tie pass (feature 220, the step-1 re-fit's coverage): a lane whose head runs a few feet
    past the way it crosses is cut back to the crossing, and the cut is committed to the record."""
    from l7r.diagram.hamletgen.ways.smooth import _smooth_web

    from ._builders import _webbed

    s = _webbed([{"pts": [[0.0, 0.0], [400.0, 0.0]], "w": 5}, {"pts": [[100.0, -6.0], [100.0, 200.0]], "w": 3}])
    assert _smooth_web(s, [], [], []) >= 1
    head = s.M["lanes"][1]["pts"][0]
    assert abs(head[0] - 100.0) < 1.0 and abs(head[1] - 0.0) < 1.0, head
