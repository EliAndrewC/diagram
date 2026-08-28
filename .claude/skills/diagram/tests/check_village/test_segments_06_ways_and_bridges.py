"""Split from test_checks.py by feature 025 - see tests/check_village/CLAUDE.md for the index."""

from tests.check_village._builders import _bridge_map, _skew_bridge_map, f_only


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
