"""tier town tests split out of `tests.check_village.test_segments_09_justice_and_tanning` (feature 133 T29, GM 2026-08-26): `make quick` collects
`tests/` minus the tier, gate and tooling trees, so these are neither imported nor collected while the scope is
locked to another tier; the gate collects everything. Helpers stay in the source module and are imported."""

import pytest

from tests.check_village._builders import WALL, _dw, _tower, bldg, f_only


@pytest.mark.tiers("town")
def test_streets_have_buildings_fires_when_building_fronts_the_other_street():
    M = {
        "meta": {"scale": "town", "walled": True},
        "wall": WALL,
        "town_streets": [
            {"pts": [[700, 380], [700, 620]], "w": 18},  # the lane (should read empty)
            {"pts": [[200, 500], [950, 500]], "w": 22, "main": True},  # the cross it actually fronts
        ],
        "buildings": [bldg(760, 500)],  # nearest the cross, not the lane
    }
    assert "streets_have_buildings" in f_only(M, "streets_have_buildings")


@pytest.mark.tiers("town")
def test_streets_have_buildings_passes_when_a_building_fronts_the_street():
    M = {
        "meta": {"scale": "town", "walled": True},
        "wall": WALL,
        "town_streets": [{"pts": [[700, 400], [700, 600]], "w": 18, "main": True}],
        "buildings": [bldg(720, 500)],  # nearest THIS street, covers its short length
    }
    assert "streets_have_buildings" not in f_only(M, "streets_have_buildings")


@pytest.mark.tiers("town")
def test_wall_hugs_the_town_fires_on_empty_corner_space():
    M = {"meta": {"scale": "town", "walled": True}, "wall": WALL, "buildings": [bldg(120, 120)]}  # one building, far from the right/bottom faces
    assert "wall_hugs_the_town" in f_only(M, "wall_hugs_the_town")


@pytest.mark.tiers("town")
def test_wall_hugs_the_town_passes_when_buildings_line_every_face():
    near = [bldg(x, y) for x in (120, 500, 880) for y in (120, 500, 880)]  # a 3x3 grid hugging all faces
    M = {"meta": {"scale": "town", "walled": True}, "wall": WALL, "buildings": near}
    assert "wall_hugs_the_town" not in f_only(M, "wall_hugs_the_town")


@pytest.mark.tiers("town")
def test_walled_town_has_gate_market_fires_when_no_market_outside():
    # the only business sits INSIDE the wall, so there is no extramural market at the gate
    M = {"meta": {"scale": "town", "walled": True}, "wall": WALL, "gate": [500, 950], "buildings": [bldg(500, 500, kind="merchant")]}
    assert "walled_town_has_gate_market" in f_only(M, "walled_town_has_gate_market")


@pytest.mark.tiers("town")
def test_walled_town_gate_market_opt_out_suppresses_the_check():
    # meta(gate_market=False) - a purely military or suppressed gate - skips the requirement
    M = {"meta": {"scale": "town", "walled": True, "gate_market": False}, "wall": WALL, "gate": [500, 950], "buildings": [bldg(500, 500, kind="merchant")]}
    assert "walled_town_has_gate_market" not in f_only(M, "walled_town_has_gate_market")


@pytest.mark.tiers("town")
def test_walled_town_commoners_inside_walls_fires_on_an_outside_laborer():
    M = {
        "meta": {"scale": "town", "walled": True},
        "wall": [[300, 300], [700, 300], [700, 700], [300, 700]],
        "gate": [500, 700],
        "buildings": [_dw(900, 500, "laborer")],
        "fire_towers": [_tower(500, 500)],
    }
    assert "walled_town_commoners_inside_walls" in f_only(M, "walled_town_commoners_inside_walls")


@pytest.mark.tiers("town")
def test_walled_town_commoners_inside_walls_allows_burakumin_and_gate_merchants():
    M = {
        "meta": {"scale": "town", "walled": True},
        "wall": [[300, 300], [700, 300], [700, 700], [300, 700]],
        "gate": [500, 700],
        "buildings": [_dw(900, 500, "burakumin"), _dw(520, 780, "merchant"), _dw(500, 500, "laborer")],
        "fire_towers": [_tower(500, 500)],
    }
    assert "walled_town_commoners_inside_walls" not in f_only(M, "walled_town_commoners_inside_walls")
