"""The smoothing pass (`hamletgen/ways/smooth.py`).

Created by feature 174: the split's derived mapping put no test here, because every test that
exercised smoothing did so through a name that lives in another module. The one statement this
file exists for is the collapse guard below - a lane whose every vertex falls inside a knot.
"""

from __future__ import annotations

import math

from l7r.diagram.hamletgen.ways.smooth import _JOG_FT, _KNOT_FT, _smooth_web, string_pull_chord_ok

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


# A shed whose near edge stands 6 ft off the chord y = 0: inside the web's 8 ft hard margin (`_clear_link` refuses the
# chord) and outside a 5 ft lane's own 4.5 ft keep-out (`_clear_touch` allows it) - the only ground on which the
# jog bound decides.
_SHED = [(40.0, 6.0), (60.0, 6.0), (60.0, 20.0), (40.0, 20.0)]


def test_a_chord_at_the_lanes_own_margin_is_taken_when_every_skipped_vertex_is_a_JOG() -> None:
    """Feature 133 T32 / 134 T50: the 4 ft stepping and the jogs a junction leaves are the SAME line drawn badly, so a
    chord the web's margins refuse is still taken at the lane's own keep-out when every vertex it replaces lies within
    `_JOG_FT` of it. Lifted out of `_smooth_web` because the straggler pass that reached it is gone."""
    pts = [(0.0, 0.0), (30.0, -2.0), (70.0, -_JOG_FT + 0.5), (100.0, 0.0)]
    assert not string_pull_chord_ok(pts, 0, 3, [_SHED], [], [], 10.0), "a keep-out wider than the shed's 6 ft refuses it outright"
    assert string_pull_chord_ok(pts, 0, 3, [_SHED], [], [], 4.5), "every skipped vertex is a jog: the chord is a simplification"


def test_a_chord_skipping_a_vertex_farther_than_the_jog_bound_is_refused() -> None:
    """The same chord across the same ground, with one skipped vertex `_JOG_FT` + 4 ft off it: that vertex is a BEND, and
    a new line across open ground owes the houses their corridor - the chord is refused at footprint margins."""
    pts = [(0.0, 0.0), (30.0, -2.0), (70.0, -_JOG_FT - 4.0), (100.0, 0.0)]
    assert not string_pull_chord_ok(pts, 0, 3, [_SHED], [], [], 4.5)
    assert string_pull_chord_ok(pts, 0, 3, [], [], [], 4.5), "on open ground the web's own margins take it, bend or not"


# A hairpin whose short HEAD's tip is the lane's only contact with another way (the way runs north from just under the tip),
# with a bar under the fold so no chord replaces the hairpin and the arm cut is the only repair.
_BAR = [[(560.0, 310.0), (700.0, 310.0), (700.0, 314.0), (560.0, 314.0)]]


def _tipped(head_ft: float) -> object:
    from ._builders import _webbed

    tip = 690.0 - head_ft
    return _webbed([{"pts": [[tip, 298.0], [tip, 200.0]], "w": 5}, {"pts": [[tip, 300.0], [690.0, 300.0], [630.0, 318.0], [560.0, 318.0]], "w": 5}])


def test_a_returning_leg_that_was_the_only_contact_is_cut_and_the_lane_joined_at_the_fold() -> None:
    """0081: "a returning leg under 40 ft is cut" - with no exception for an arm whose tip is the lane's only contact (feature
    328 wave 46: the smoother kept such an arm). The fold stands 20 ft from the way, inside the 25 ft join reach, so the cut
    lane is joined again there."""
    s = _tipped(20.0)
    _smooth_web(s, _BAR, [], [])
    pts = [tuple(p) for p in s.M["lanes"][1]["pts"]]
    assert (670.0, 300.0) not in pts, f"the 20 ft arm is cut: {pts}"
    assert pts[-1] == (560.0, 318.0), "the long arm stays"


def test_a_cut_no_join_can_mend_is_left_for_the_settle() -> None:
    """Where the fold stands past the 25 ft join reach (30 ft here), the cut would strand the lane: `commit_lane` refuses it
    and the lane is committed uncut - the settle's `_unkinked` cuts every returning leg and mends the network."""
    s = _tipped(30.0)
    _smooth_web(s, _BAR, [], [])
    pts = [tuple(p) for p in s.M["lanes"][1]["pts"]]
    assert len(pts) == 4 and pts[1] == (690.0, 300.0) and pts[0][0] == 660.0, f"the arm is kept (its tip gathered onto the way's end): {pts}"
