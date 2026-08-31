"""The smoothing pass (`hamletgen/ways/smooth.py`).

Created by feature 174: the split's derived mapping put no test here, because every test that
exercised smoothing did so through a name that lives in another module. The one statement this
file exists for is the collapse guard below - a lane whose every vertex falls inside a knot.
"""

from __future__ import annotations

from l7r.diagram.hamletgen.ways.smooth import _smooth_web

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
