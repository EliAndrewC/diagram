"""The access tree refuses a lane that runs beside another past a pitch, either way round (feature 294, a Sawada roll)."""

from __future__ import annotations

from l7r.diagram.hamletgen.ways.tree import tree_shadows


def test_a_lane_beside_another_past_a_pitch_is_refused_either_way_round() -> None:
    trunk = [(0.0, 0.0), (300.0, 0.0)]
    beside = [(20.0, 20.0), (200.0, 20.0)]  # 180 ft at 20 ft off: a doubled band
    assert tree_shadows([trunk, beside])
    assert tree_shadows([beside, trunk])


def test_a_lane_meeting_another_square_on_is_not() -> None:
    trunk = [(0.0, 0.0), (300.0, 0.0)]
    spur = [(150.0, 200.0), (150.0, 0.0)]  # meets the trunk square-on: within 30 ft only at the junction
    assert not tree_shadows([trunk, spur])
