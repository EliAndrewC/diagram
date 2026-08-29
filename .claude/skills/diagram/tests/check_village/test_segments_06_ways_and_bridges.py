"""Split from test_checks.py by feature 025 - see tests/check_village/CLAUDE.md for the index."""

from tests.check_village._builders import f_only, manifest

# ---- feature 021: the capital housing layer ---------------------------------------------------


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
