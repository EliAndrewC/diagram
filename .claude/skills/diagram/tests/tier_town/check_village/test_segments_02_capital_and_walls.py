"""tier town tests split out of `tests.check_village.test_segments_02_capital_and_walls` (feature 133 T29, GM 2026-08-26): `make quick` collects
`tests/` minus the tier, gate and tooling trees, so these are neither imported nor collected while the scope is
locked to another tier; the gate collects everything. Helpers stay in the source module and are imported."""

import pytest

from tests.check_village._builders import (
    WALLSQ,
    _mest_city,
    bldg,
    f_only,
)


@pytest.mark.tiers("town")
def test_outside_fields_farmhouse_density_passes_when_edge_is_a_tiny_sliver():
    # a field whose only on-map edge is a tiny corner (< 120px) is too small a sliver to require
    # farmhouses - its workers are off-map with the rest of the field. Must NOT fire.
    field = {"name": "f1", "kind": "paddy", "bbox": [-400, -400, 50, 50], "outline": [[-400, -400], [50, -400], [50, 50], [-400, 50]]}  # only a ~50x50 corner shows
    M = {"meta": {"scale": "town", "W": 1000, "H": 1000}, "fields": [field], "houses": []}
    assert "outside_fields_farmhouse_density" not in f_only(M, "outside_fields_farmhouse_density")


@pytest.mark.tiers("city", "town")
def test_poor_housing_mostly_interior_fires_when_laborers_on_the_street():
    M = {
        "meta": {"scale": "city", "walled": True},
        "wall": WALLSQ,
        "gates": [[500, 200], [500, 800]],
        "town_streets": [{"pts": [[250, 500], [750, 500]], "w": 18}],
        "buildings": [bldg(300 + i * 40, 512, kind="laborer") for i in range(8)],
    }  # all jammed ONTO the street
    assert "poor_housing_mostly_interior" in f_only(M, "poor_housing_mostly_interior")


@pytest.mark.tiers("city", "town")
def test_no_isolated_dwelling_cluster_fires_on_a_cut_off_block():
    # a 36-house block whose only street is far away - a giant cluster with no street OR alley near it
    blds = [bldg(380 + (i % 6) * 26, 380 + (i // 6) * 26, kind="laborer") for i in range(36)]
    M = {
        "meta": {"scale": "city", "walled": True},
        "wall": WALLSQ,
        "gates": [[500, 200], [500, 800]],
        "town_streets": [{"pts": [[210, 210], [790, 210]], "w": 18}],  # only street, along the top edge
        "buildings": blds,
    }
    assert "no_isolated_dwelling_cluster" in f_only(M, "no_isolated_dwelling_cluster")


@pytest.mark.tiers("city", "town")
def test_no_isolated_dwelling_cluster_passes_when_an_alley_reaches_it():
    blds = [bldg(380 + (i % 6) * 26, 380 + (i // 6) * 26, kind="laborer") for i in range(36)]
    M = {
        "meta": {"scale": "city", "walled": True},
        "wall": WALLSQ,
        "gates": [[500, 200], [500, 800]],
        "town_streets": [{"pts": [[210, 210], [790, 210]], "w": 18}],
        "alleys": [{"pts": [[380, 360], [380, 540]], "w": 10}, {"pts": [[510, 360], [510, 540]], "w": 10}],  # alleys lace the block
        "buildings": blds,
    }
    assert "no_isolated_dwelling_cluster" not in f_only(M, "no_isolated_dwelling_cluster")


@pytest.mark.tiers("city", "town")
def test_city_wall_matches_budget_is_scoped_to_walled_cities_only():
    town = {"meta": {"scale": "town", "walled": True}, "wall": [[200, 200], [800, 200], [800, 800], [200, 800]]}
    assert "city_wall_matches_budget" not in f_only(town, "city_wall_matches_budget")
    unwalled = {"meta": {"scale": "city"}, "wall": [[200, 200], [800, 200], [800, 800], [200, 800]]}
    assert "city_wall_matches_budget" not in f_only(unwalled, "city_wall_matches_budget")


@pytest.mark.tiers("city", "town")
def test_merchant_estate_wall_fires_on_a_street_crossing():
    # a city street's band running under the estate's west wall (GM 2026-07-19 follow-up)
    hit = _mest_city(town_streets=[{"pts": [[470, 400], [470, 600]], "w": 6.0}])
    assert "merchant_estate_wall_clear_of_streets" in f_only(hit, "merchant_estate_wall_clear_of_streets")
    # the trunk road under the south wall is the same error
    road = _mest_city(road=[[400, 523], [600, 523]], road_width=8.7)
    assert "merchant_estate_wall_clear_of_streets" in f_only(road, "merchant_estate_wall_clear_of_streets")


@pytest.mark.tiers("town")
def test_merchant_estate_wall_passes_streets_at_a_distance():
    clear = _mest_city(town_streets=[{"pts": [[440, 400], [440, 600]], "w": 6.0}], road=[[400, 560], [600, 560]], road_width=8.7)
    assert "merchant_estate_wall_clear_of_streets" not in f_only(clear, "merchant_estate_wall_clear_of_streets")
