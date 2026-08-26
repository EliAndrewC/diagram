"""tier town tests split out of `tests.check_village.test_segments_08_kosatsuba_and_basins` (feature 133 T29, GM 2026-08-26): `make quick` collects
`tests/` minus the tier, gate and tooling trees, so these are neither imported nor collected while the scope is
locked to another tier; the gate collects everything. Helpers stay in the source module and are imported."""

import pytest

from tests.check_village._builders import (
    _dw,
    _kosatsuba,
    bldg,
    f,
    f_only,
    manifest,
)


@pytest.mark.tiers("town")
def test_kosatsuba_at_a_junction_may_face_either_way():
    # ANY route segment inside the siting band counts, not merely the nearest: a board at a
    # crossing legitimately fronts one of the two ways that meet there (the real case -
    # Nagahara's north-ward board sits nearer a cross street than the ward street it fronts)
    M = {
        "meta": {"scale": "town"},
        "kosatsuba": [dict(_kosatsuba(500, 480), rot=90)],
        "town_streets": [{"pts": [[0, 500], [1000, 500]], "w": 28}, {"pts": [[540, 0], [540, 1000]], "w": 28}],
    }
    assert "kosatsuba_faces_the_road" not in f_only(M, "kosatsuba_faces_the_road")


@pytest.mark.tiers("city", "town")
def test_city_kosatsuba_siting_threshold_is_scale_aware():
    # the ~60 ft siting limit is REAL feet: 30 px off the road passes at town grain (30 ft)
    # but fires at city grain (1 px = 3 ft -> 90 ft)
    road = [[0, 500], [1000, 500]]
    assert "kosatsuba_by_the_road" not in f_only({"meta": {"scale": "town"}, "kosatsuba": [_kosatsuba(500, 530)], "road": road}, "kosatsuba_by_the_road")
    assert "kosatsuba_by_the_road" in f_only({"meta": {"scale": "city", "ftpx": 3}, "kosatsuba": [_kosatsuba(500, 530)], "road": road}, "kosatsuba_by_the_road")
    ok = f({"meta": {"scale": "city", "ftpx": 3}, "kosatsuba": [_kosatsuba(500, 515)], "road": road})
    assert "kosatsuba_by_the_road" not in ok and "city_has_kosatsuba" not in ok


@pytest.mark.tiers("town")
def test_defense_marsh_girds_the_walls_fires_inside_the_circuit():
    # the wet belt reaches INSIDE the wall - the inundation protects the wall; inside is the town
    M = {
        "meta": {},
        "wall": [[300, 300], [700, 300], [700, 700], [300, 700]],
        "marshes": [{"x": 500, "y": 500, "w": 100, "h": 100, "role": "defense", "poly": [[450, 450], [550, 450], [550, 550], [450, 550]]}],
    }
    assert "defense_marsh_girds_the_walls" in f_only(M, "defense_marsh_girds_the_walls")


@pytest.mark.tiers("town")
def test_town_samurai_housing_varied_fires_on_uniform_small_houses():
    M = {"meta": {"scale": "town", "population": 100}, "buildings": [_dw(400 + i * 60, 400, "samurai") for i in range(6)]}
    assert "town_samurai_housing_varied" in f_only(M, "town_samurai_housing_varied")


@pytest.mark.tiers("town")
def test_town_samurai_housing_varied_passes_with_a_senior_house():
    M = {"meta": {"scale": "town", "population": 100}, "buildings": [_dw(400, 340, "samurai_large")] + [_dw(400 + i * 60, 400, "samurai") for i in range(5)]}
    assert "town_samurai_housing_varied" not in f_only(M, "town_samurai_housing_varied")


@pytest.mark.tiers("town")
def test_burakumin_quarter_segregated_fires_when_interleaved():
    M = {"meta": {"scale": "town", "population": 100}, "buildings": [_dw(500, 500, "burakumin"), _dw(530, 510, "laborer")]}
    assert "burakumin_quarter_segregated" in f_only(M, "burakumin_quarter_segregated")


@pytest.mark.tiers("town")
def test_burakumin_quarter_segregated_passes_with_open_ground_between():
    M = {"meta": {"scale": "town", "population": 100}, "buildings": [_dw(500, 500, "burakumin"), _dw(700, 500, "laborer")]}
    assert "burakumin_quarter_segregated" not in f_only(M, "burakumin_quarter_segregated")


@pytest.mark.tiers("town")
def test_burakumin_quarter_segregated_passes_across_a_real_seam():
    # The control for the ratchet entry: 60 ft of open ground between the walls is the rule met.
    M = manifest(meta={"scale": "town", "ftpx": 1, "W": 2000, "H": 2000}, buildings=[bldg(500, 500, kind="burakumin", w=38, h=26), bldg(500 + 19 + 17 + 61, 500, kind="laborer", w=34, h=24)])
    assert "burakumin_quarter_segregated" not in f_only(M, "burakumin_quarter_segregated")
