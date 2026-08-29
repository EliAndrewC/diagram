"""Split from test_checks.py by feature 025 - see tests/check_village/CLAUDE.md for the index."""

from tests.check_village._builders import _bridge_map, _skew_bridge_map, f_only, manifest


def test_bridges_align_with_their_way_passes_a_solved_deck():
    # a deck seated on the crossing and bearing with the road - what s.bridges() produces
    assert "bridges_align_with_their_way" not in f_only(_skew_bridge_map(), "bridges_align_with_their_way")
    # ...and a deck may point either way along the road: a plank has no forward direction
    assert "bridges_align_with_their_way" not in f_only(_skew_bridge_map(rot=180), "bridges_align_with_their_way")


def test_bridges_align_with_their_way_fires_on_a_deck_that_carries_nothing():
    # a deck over water with no way on it at all: either the way or the watercourse is unrecorded
    M = _bridge_map([{"x": 500, "y": 500, "rot": 0, "span": 37, "w": 26}])
    del M["road"]
    assert "bridges_align_with_their_way" in f_only(M, "bridges_align_with_their_way")


def test_bridges_align_with_their_way_exempts_standalone_footplanks():
    """A `foot` plank is carried by no way and crosses its ditch PERPENDICULAR by construction, so
    the alignment rule would fire on every correct one. Its own rules are long_ditches_have_a_
    footbridge and footbridges_reach_useful_ground."""
    M = _skew_bridge_map(rot=90, foot=True)  # square across the road it is nowhere near carrying
    assert "bridges_align_with_their_way" not in f_only(M, "bridges_align_with_their_way")


# ---- feature 021: the capital housing layer ---------------------------------------------------


def test_bridges_align_with_their_way():
    """A deck seated on its crossing but turned across the road it carries. The seat and the skew are
    separate failures on purpose - `seat_off` names a deck in the wrong PLACE, this one names a deck at the
    wrong ANGLE, and a hand-placed deck is usually both."""
    M = manifest(
        roads=[{"pts": [[500, 100], [500, 900]], "w": 20}],
        streams=[{"poly": [[100, 500], [900, 500]], "w": 12}],
        bridges=[{"x": 500, "y": 500, "rot": 40.0, "span": 40, "w": 10}],
    )
    assert "bridges_align_with_their_way" in f_only(M, "bridges_align_with_their_way")
    square = {**M, "bridges": [{"x": 500, "y": 500, "rot": 90.0, "span": 40, "w": 10}]}
    assert "bridges_align_with_their_way" not in f_only(square, "bridges_align_with_their_way")


def test_waterside_works_follow_the_bank():
    """A granary, jetty, tanning yard or dye yard within 140 px of water is a WATERSIDE instance and lies
    along the bank - hides are soaked at the water, a store is loaded from it. An inland store is not
    bank-parallel and is not asked to be."""
    M = manifest(
        streams=[{"poly": [[100, 500], [900, 500]], "w": 12}],
        granaries=[{"x": 500, "y": 540, "w": 40, "h": 24, "rot": 33.0, "kind": "granary"}],
    )
    assert "waterside_works_follow_the_bank" in f_only(M, "waterside_works_follow_the_bank")
    aligned = {**M, "granaries": [{"x": 500, "y": 540, "w": 40, "h": 24, "rot": 0.0, "kind": "granary"}]}
    assert "waterside_works_follow_the_bank" not in f_only(aligned, "waterside_works_follow_the_bank")
    inland = {**M, "granaries": [{"x": 500, "y": 900, "w": 40, "h": 24, "rot": 33.0, "kind": "granary"}]}
    assert "waterside_works_follow_the_bank" not in f_only(inland, "waterside_works_follow_the_bank")


def test_ways_not_inside_road_beds():
    """Two ways drawn where the ground has one. A lane running 45+ px INSIDE a road's paved bed is a
    duplicate: the road itself serves the frontage."""
    M = manifest(roads=[{"pts": [[100, 500], [900, 500]], "w": 30}], lanes=[{"pts": [[200, 500], [400, 500]], "w": 4}])
    assert "ways_not_inside_road_beds" in f_only(M, "ways_not_inside_road_beds")
    beside = {**M, "lanes": [{"pts": [[200, 560], [400, 560]], "w": 4}]}
    assert "ways_not_inside_road_beds" not in f_only(beside, "ways_not_inside_road_beds")
