"""tier town tests split out of `tests.check_village.test_segments_10_city_battery_b` (feature 133 T29, GM 2026-08-26): `make quick` collects
`tests/` minus the tier, gate and tooling trees, so these are neither imported nor collected while the scope is
locked to another tier; the gate collects everything. Helpers stay in the source module and are imported."""

import pytest

from tests.check_village._builders import (
    WALLSQ,
    _fort_city,
    f_only,
)


@pytest.mark.tiers("city", "town")
def test_city_streets_meet_through_lanes_fires_at_the_imperial_road():
    # a street stopping short of the Imperial road (road centerline x=500; the street ends at x=470)
    M = _fort_city(road=[[500, 100], [500, 900]], road_width=26, town_streets=[{"pts": [[300, 500], [470, 500]], "w": 18}])
    assert "city_streets_meet_through_lanes" in f_only(M, "city_streets_meet_through_lanes")


@pytest.mark.tiers("city", "town")
def test_city_ministries_front_a_street_fires_when_floating():
    # a ministry with the nearest street ~290px away - it floats mid-block, fronting nothing
    M = {
        "meta": {"scale": "city", "walled": True, "W": 1000, "H": 1000},
        "wall": WALLSQ,
        "gates": [[500, 200], [500, 800]],
        "ministries": [{"x": 500, "y": 500, "w": 88, "h": 58, "name": "Ministry of War"}],
        "town_streets": [{"pts": [[250, 250], [350, 250]], "w": 18}],
    }
    assert "city_ministries_front_a_street" in f_only(M, "city_ministries_front_a_street")


@pytest.mark.tiers("city", "town")
def test_city_ministries_front_a_street_passes_when_on_a_street():
    M = {
        "meta": {"scale": "city", "walled": True, "W": 1000, "H": 1000},
        "wall": WALLSQ,
        "gates": [[500, 200], [500, 800]],
        "ministries": [{"x": 500, "y": 500, "w": 88, "h": 58, "name": "Ministry of War"}],
        "town_streets": [{"pts": [[300, 560], [700, 560]], "w": 18}],
    }  # an avenue 60px from the office
    assert "city_ministries_front_a_street" not in f_only(M, "city_ministries_front_a_street")


@pytest.mark.tiers("city", "town")
def test_city_samurai_quarter_gated_fires_when_no_ward_gates():
    M = {
        "meta": {"scale": "city", "walled": True},
        "wall": WALLSQ,
        "gates": [[500, 200], [500, 800]],
        "governor_mansion": {"x": 600, "y": 600, "w": 120, "h": 90},
        "town_streets": [{"pts": [[400, 600], [800, 600]], "w": 18}],
        "kido": [],
    }  # the quarter has no ward gates
    assert "city_samurai_quarter_gated" in f_only(M, "city_samurai_quarter_gated")


@pytest.mark.tiers("city", "town")
def test_city_samurai_quarter_gated_passes_with_two_gates_on_streets():
    M = {
        "meta": {"scale": "city", "walled": True},
        "wall": WALLSQ,
        "gates": [[500, 200], [500, 800]],
        "governor_mansion": {"x": 600, "y": 600, "w": 120, "h": 90},
        "town_streets": [{"pts": [[400, 600], [800, 600]], "w": 18}, {"pts": [[600, 400], [600, 800]], "w": 18}],
        "kido": [{"x": 500, "y": 600, "horizontal": True}, {"x": 600, "y": 500, "horizontal": False}],
    }
    assert "city_samurai_quarter_gated" not in f_only(M, "city_samurai_quarter_gated")


@pytest.mark.tiers("city", "town")
def test_city_samurai_ward_sealed_fires_on_ungated_crossing():
    # a street pierces the ward fence with no kido at the crossing - the gate can be walked around
    M = {
        "meta": {"scale": "city", "walled": True},
        "wall": WALLSQ,
        "gates": [[500, 200], [500, 800]],
        "governor_mansion": {"x": 600, "y": 600, "w": 120, "h": 90},
        "wards": [{"name": "samurai", "boundary": [[400, 800], [400, 400], [800, 400]]}],
        "town_streets": [{"pts": [[300, 500], [700, 500]], "w": 18}],  # crosses the W fence at (400,500)
        "kido": [],
    }
    assert "city_samurai_ward_sealed" in f_only(M, "city_samurai_ward_sealed")


@pytest.mark.tiers("city", "town")
def test_city_samurai_ward_sealed_fires_on_open_fence_end():
    # the fence has an end floating in the interior (not abutting the wall) - you walk around it
    M = {
        "meta": {"scale": "city", "walled": True},
        "wall": WALLSQ,
        "gates": [[500, 200], [500, 800]],
        "governor_mansion": {"x": 600, "y": 600, "w": 120, "h": 90},
        "wards": [{"name": "samurai", "boundary": [[400, 500], [400, 400], [800, 400]]}],  # (400,500) floats
        "town_streets": [],
        "kido": [],
    }
    assert "city_samurai_ward_sealed" in f_only(M, "city_samurai_ward_sealed")


@pytest.mark.tiers("city", "town")
def test_city_streets_clear_of_wall_fires():
    M = {
        "meta": {"scale": "city", "walled": True, "W": 1000, "H": 1000},
        "wall": WALLSQ,
        "gates": [[500, 200], [500, 800]],
        "town_streets": [{"pts": [[500, 500], [990, 500]], "w": 18}],
    }  # a vertex outside the wall
    assert "city_streets_clear_of_wall" in f_only(M, "city_streets_clear_of_wall")


@pytest.mark.tiers("city", "town")
def test_city_streets_clear_of_moat_fires_on_alley():
    M = {
        "meta": {"scale": "city", "walled": True, "W": 1000, "H": 1000},
        "wall": WALLSQ,
        "gates": [[500, 200], [500, 800]],
        "moat": [[150, 150], [850, 150], [850, 850], [150, 850], [150, 150]],
        "town_streets": [],
        "alleys": [{"pts": [[500, 700], [500, 900]], "w": 10}],
    }  # alley crosses the moat ring
    assert "city_streets_clear_of_moat" in f_only(M, "city_streets_clear_of_moat")
