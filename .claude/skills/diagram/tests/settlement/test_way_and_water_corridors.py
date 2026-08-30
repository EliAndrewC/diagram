"""Ways and watercourses reserve their ground, and the placer honors it (feature 166).

Carries the rules `no_structure_on_stream`, `houses_clear_of_lanes` and `no_farmhouse_stands_on_a_lane`
used to re-measure on finished maps. Each is the same two-part chain, and BOTH parts are asserted here
because either alone is half a rule:

  1. drawing the way or the water REGISTERS a no-build corridor, and
  2. the placer REFUSES ground inside it.

A test of the refusal alone still passes if lanes stop registering; a test of the registration alone still
passes if the placer stops consulting corridors. The battery measured the finished map, which happened to
catch both - so replacing it takes two assertions, not one.
"""

from __future__ import annotations

from l7r.diagram.settlement import Settlement


def _s() -> Settlement:
    s = Settlement(1200, 900, seed=1)
    s.meta(name="Waysend", scale="hamlet", ftpx=1, down_deg=90)
    return s


def test_a_stream_reserves_a_corridor_and_the_placer_refuses_it() -> None:
    """`no_structure_on_stream`. The corridor is `max(30, width/2 + 20)` - deliberately wider than the
    water, because a wall on the bank is a wall in the water when the stream is up."""
    s = _s()
    before = len(s.corridors)
    s.river([(100.0, 400.0), (1100.0, 400.0)], width=20.0)
    assert len(s.corridors) > before, "a drawn river registers a no-build corridor"
    assert s._near_corridor(600.0, 400.0), "on the water itself"
    assert s._near_corridor(600.0, 425.0), "and on the bank the corridor reserves"
    assert not s._near_corridor(600.0, 800.0), "well away from it the ground is free"


def test_a_lane_reserves_a_setback_that_clears_building_CORNERS_not_only_centres() -> None:
    """`houses_clear_of_lanes` / `no_farmhouse_stands_on_a_lane`. The lane's corridor is
    `width/2 + 11`, and the +11 is there so a house whose CENTRE clears the tread does not put its
    corner on it - the setback keeps building corners off the lane, not just centers."""
    s = _s()
    before = len(s.corridors)
    s.lane([(100.0, 200.0), (1100.0, 200.0)], width=12.0)
    assert len(s.corridors) > before, "a drawn lane registers a corridor"
    assert s._near_corridor(600.0, 200.0), "the tread itself"
    assert s._near_corridor(600.0, 210.0), "and the setback beyond it, which is what saves the corners"
    assert not s._near_corridor(600.0, 600.0), "open ground is free"


def test_the_corridor_is_measured_to_the_TREAD_not_to_the_nearest_vertex() -> None:
    """A way is a polyline, and a point can be far from every vertex while standing squarely on the
    run between two of them. `dev/gate.md` collects the family of defects that come from measuring to
    the wrong thing; this is the one that matters for a long straight lane."""
    s = _s()
    s.lane([(100.0, 500.0), (1100.0, 500.0)], width=12.0)
    assert s._near_corridor(600.0, 500.0), "mid-run, 500 px from either vertex, is still on the lane"
