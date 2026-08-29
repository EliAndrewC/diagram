"""Split from test_checks.py by feature 025 - see tests/check_village/CLAUDE.md for the index."""

from tests.check_village._builders import _fall_map, f_only

# ---- streets_have_buildings: the case that motivated this file ----------------------------
# A building beside a north-south lane but FRONTING the east-west cross-street (it is nearer
# the cross) must NOT count as serving the lane - so a lane with only such neighbors reads as
# empty. The old proximity-only check missed this; this fixture pins the fix.


# ---- wall_hugs_the_town: a wall that encloses large empty corner space ---------------------
# Walls are expensive; one should hug the built town. A single building tucked in one corner of
# a big square enclosure leaves three faces running over empty space - that must fire. A town
# whose buildings sit near every face must NOT. (The hill, when present, counts as occupancy -
# a wall may legitimately climb/skirt terrain rather than leveling it.)


def test_settlement_declares_a_land_fall_accepts_a_map_level_bearing():
    M = _fall_map()
    M["meta"]["down_deg"] = 90
    assert "settlement_declares_a_land_fall" not in f_only(M, "settlement_declares_a_land_fall")


def test_settlement_declares_a_land_fall_accepts_per_field_falls_with_no_map_bearing():
    # what a settlement ringed by farmland needs: its fans drain several ways, so no single bearing
    M = _fall_map()
    M["fields"][0]["down_deg"] = 90
    assert "settlement_declares_a_land_fall" not in f_only(M, "settlement_declares_a_land_fall")


def test_settlement_declares_a_land_fall_is_not_satisfied_by_water_flow_alone():
    # water_flow is where the water GOES; down_deg is how the land LIES. Different facts.
    M = _fall_map()
    M["meta"]["water_flow"] = 90
    assert "settlement_declares_a_land_fall" in f_only(M, "settlement_declares_a_land_fall")
