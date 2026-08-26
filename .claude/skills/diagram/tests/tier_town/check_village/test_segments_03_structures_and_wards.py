"""tier town tests split out of `tests.check_village.test_segments_03_structures_and_wards` (feature 133 T29, GM 2026-08-26): `make quick` collects
`tests/` minus the tier, gate and tooling trees, so these are neither imported nor collected while the scope is
locked to another tier; the gate collects everything. Helpers stay in the source module and are imported."""

import pytest

from tests.check_village._builders import (
    FEAT,
    WALL,
    WALLSQ,
    _feature_overlap,
    _tower,
    bldg,
    f,
    f_only,
)


@pytest.mark.tiers("town")
def test_no_structure_on_wall_fires():
    # on the TOP rampart segment - note the wall is an OPEN polyline (the closing edge is not
    # a real wall segment, since a real rampart is an arc anchored to a hill), so the building
    # must sit on one of its drawn segments, not the implicit closure.
    M = {"meta": {"scale": "town", "walled": True}, "wall": WALL, "buildings": [bldg(400, 50)]}
    assert "no_structure_on_wall" in f_only(M, "no_structure_on_wall")


@pytest.mark.tiers("town")
def test_flophouse_on_road_overlaps_like_any_structure():
    # a standalone civic building (flophouse) is now checked for overlaps too: one sitting on
    # the road must trip no_structure_on_road, exactly as a shop would.
    M = {"meta": {"scale": "town"}, "road": [[100, 500], [900, 500]], "road_width": 26, "flophouses": [{"x": 500, "y": 500, "w": 104, "h": 46, "rot": 0}]}
    assert "no_structure_on_road" in f_only(M, "no_structure_on_road")  # 1 < 2


@pytest.mark.tiers("town")
def test_no_structure_on_street_branch():
    assert "no_structure_on_street" in _feature_overlap({"walled": True}, "town_streets", [{"pts": FEAT, "w": 24}])


@pytest.mark.tiers("town")
def test_businesses_front_streets_fires():
    M = {
        "meta": {"scale": "town", "walled": True},
        "wall": WALL,
        "town_streets": [{"pts": [[120, 120], [120, 400]], "w": 20}],
        "buildings": [bldg(800, 800, kind="shop")],
    }  # a shop nowhere near the street
    assert "businesses_front_streets" in f_only(M, "businesses_front_streets")


@pytest.mark.tiers("town")
def test_housing_off_main_street_fires():
    M = {
        "meta": {"scale": "town", "walled": True},
        "wall": WALL,
        "town_streets": [{"pts": [[500, 120], [500, 800]], "w": 20, "main": True}],
        "buildings": [bldg(540, 500, kind="laborer", rot=-90)],
    }  # a dwelling on the MAIN frontage
    assert "housing_off_main_street" in f_only(M, "housing_off_main_street")


@pytest.mark.tiers("town")
def test_roads_drawn_under_overlays_fires():
    M = {
        "meta": {"scale": "town"},
        "road": [[100, 500], [900, 500]],
        "road_width": 26,
        "road_z": 1000,
        "labels": [
            [480, 480, 520, 520, 5],  # a label (z=5) the road (z=1000) is painted OVER
            [100, 100, 140, 140, 5],
        ],
    }  # a low-z label the road does NOT touch (the no-hit path)
    assert "roads_drawn_under_overlays" in f_only(M, "roads_drawn_under_overlays")


@pytest.mark.tiers("city", "town")
def test_city_lanes_layered_by_width_fires_when_narrow_over_wide():
    # the wide Imperial road (26) is drawn EARLY (low z) and a narrow street (18) that crosses it is
    # drawn later (high z): the narrow lane paints over the wider road - the wider must be on top.
    M = {
        "meta": {"scale": "city", "walled": True, "W": 1000, "H": 1000},
        "wall": WALLSQ,
        "gates": [[500, 200], [500, 800]],
        "road": [[500, 150], [500, 850]],
        "road_width": 26,
        "road_z": 5,
        "town_streets": [{"pts": [[300, 500], [700, 500]], "w": 18, "z": 50}],
    }  # crosses the road at (500,500)
    assert "city_lanes_layered_by_width" in f_only(M, "city_lanes_layered_by_width")


@pytest.mark.tiers("city", "town")
def test_city_lane_under_wall_handles_an_open_town_wall():
    # a town wall is an open arc (not a closed ring); a street touching it off-gate still fires
    M = {"meta": {"scale": "town"}, "wall": [[200, 500], [500, 200], [800, 500]], "wall_z": 10, "gate": [500, 200], "town_streets": [{"pts": [[300, 600], [352, 352]], "w": 18, "z": 100}]}
    assert "city_lane_under_wall" in f_only(M, "city_lane_under_wall")


@pytest.mark.tiers("city", "town")
def test_city_lane_under_wall_fires_when_street_crosses_wall_off_gate():
    # an E-W street punched clean through the wall (crossing both side faces, far from the N/S gates)
    # and drawn OVER it: a lane must run UNDER the rampart except at a gate.
    M = {
        "meta": {"scale": "city", "walled": True, "W": 1000, "H": 1000},
        "wall": WALLSQ,
        "gates": [[500, 200], [500, 800]],
        "wall_z": 5,
        "town_streets": [{"pts": [[100, 500], [900, 500]], "w": 18, "z": 50}],
    }  # crosses x=200 and x=800, far from gates
    assert "city_lane_under_wall" in f_only(M, "city_lane_under_wall")


@pytest.mark.tiers("city", "town")
def test_businesses_front_streets_fires_when_shops_are_interior():
    M = {
        "meta": {"scale": "city", "walled": True},
        "wall": WALLSQ,
        "gates": [[500, 200], [500, 800]],
        "town_streets": [{"pts": [[250, 250], [750, 250]], "w": 18}],  # the only street, along the top
        "buildings": [bldg(300 + i * 50, 550, kind="shop") for i in range(6)],
    }  # shops marooned in the interior
    assert "businesses_front_streets" in f_only(M, "businesses_front_streets")


@pytest.mark.tiers("city", "town")
def test_alleys_serve_buildings_fires_on_a_redundant_lane_beside_a_street():
    # an alley laid parallel and CLOSE to a street it duplicates: every dwellling fronts the
    # street (it is nearer), so the alley uniquely serves nothing - a redundant lane. Buildings
    # are within the alley's band but closer to the street, so nearest-lane assignment credits
    # them to the street and the alley reads empty.
    blds = [bldg(330 + i * 40, 415, kind="laborer") for i in range(9)]  # y415: 15px from street, 35px from alley
    M = {
        "meta": {"scale": "city", "walled": True},
        "wall": WALLSQ,
        "gates": [[500, 200], [500, 800]],
        "town_streets": [{"pts": [[300, 400], [700, 400]], "w": 18}],
        "alleys": [{"pts": [[300, 450], [700, 450]], "w": 10}],  # parallel, 50px south of the street
        "buildings": blds,
    }
    assert "alleys_serve_buildings" in f_only(M, "alleys_serve_buildings")


@pytest.mark.tiers("town")
def test_no_structure_on_street_fires_on_alley_over_building():
    M = {
        "meta": {"scale": "town", "walled": False},
        "wall": WALL,
        "alleys": [{"pts": [[400, 500], [600, 500]], "w": 10}],
        "buildings": [bldg(500, 500, kind="laborer")],
    }  # the alley runs straight over the dwelling
    assert "no_structure_on_street" in f_only(M, "no_structure_on_street")


@pytest.mark.tiers("town")
def test_fire_tower_on_wall_overlaps_like_any_structure():
    # fire_towers are in _OVERLAP_STRUCTS, so a tower on the wall trips no_structure_on_wall
    M = {"meta": {"scale": "town", "walled": True}, "wall": [[100, 500], [900, 500]], "gate": [500, 500], "fire_towers": [_tower(500, 500)]}
    assert "no_structure_on_wall" in f_only(M, "no_structure_on_wall")


@pytest.mark.tiers("town")
def test_fire_tower_standoff_fires_when_flush_with_a_building():
    # tower half-width 13 + shop half-width 20 -> centers 536 apart leave a 3px gap: too tight
    # (the far building exercises the distance prefilter)
    M = {"meta": {"scale": "town", "walled": True}, "fire_towers": [_tower(500, 500)], "buildings": [bldg(536, 500, "laborer", w=40, h=28), bldg(900, 900, "laborer")]}
    fails = f(M)
    assert "fire_tower_standoff" in fails
    assert "no_structure_overlaps" not in fails  # a 3px gap is NOT an overlap - only the new check sees it
