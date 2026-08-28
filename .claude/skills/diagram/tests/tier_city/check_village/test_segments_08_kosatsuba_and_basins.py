"""tier city tests split out of `tests.check_village.test_segments_08_kosatsuba_and_basins` (feature 133 T29, GM 2026-08-26): `make quick` collects
`tests/` minus the tier, gate and tooling trees, so these are neither imported nor collected while the scope is
locked to another tier; the gate collects everything. Helpers stay in the source module and are imported."""

import pytest

from tests.check_village._builders import (
    _drain_map,
    _kosatsuba,
    f,
    f_only,
)


@pytest.mark.tiers("city")
def test_city_has_kosatsuba_fires_when_absent():
    # cities port the institution up (GM 2026-07-24): a city DRAWS the set
    assert "city_has_kosatsuba" in f_only({"meta": {"scale": "city"}}, "city_has_kosatsuba")
    assert "city_has_kosatsuba" not in f_only({"meta": {"scale": "city", "kosatsuba": False}}, "city_has_kosatsuba")


@pytest.mark.tiers("city")
def test_city_kosatsuba_floor_is_gates_plus_central():
    # the principal central board + one per main gate (GM 2026-07-24): 2 gates -> floor 3
    road = [[0, 500], [2000, 500]]
    gates = [[520, 500], [1900, 500]]
    two = f({"meta": {"scale": "city", "ftpx": 3}, "kosatsuba": [_kosatsuba(500, 520), _kosatsuba(1880, 520)], "road": road, "gates": gates})
    assert "city_has_kosatsuba" in two
    three = f({"meta": {"scale": "city", "ftpx": 3}, "kosatsuba": [_kosatsuba(500, 520), _kosatsuba(1880, 520), _kosatsuba(1200, 515)], "road": road, "gates": gates})
    assert "city_has_kosatsuba" not in three


@pytest.mark.tiers("city")
def test_drain_runs_cross_slope_uses_the_FIELD_s_own_fall_not_the_map_s():
    # same drain, but this field falls EAST (0 deg) - so the drain now runs across its own contour
    # and is correct. A city ringed by farmland drains several ways at once; one map-level constant
    # cannot describe it (Tango's fans span 210 deg).
    M = _drain_map()
    M["fields"][0]["down_deg"] = 0
    assert "drain_runs_cross_slope" not in f_only(M, "drain_runs_cross_slope")


@pytest.mark.tiers("city")
def test_drainage_slope_checks_skip_a_drain_whose_field_declares_no_fall():
    # a city declares no map-level down_deg (no single bearing can describe a settlement whose fans
    # fall 210 deg apart), so a drain belonging to a field WITHOUT its own slope has nothing to be
    # judged against - it is skipped rather than measured against a fiction
    M = {
        "meta": {"scale": "city", "ftpx": 3, "W": 3200, "H": 2700},
        "fields": [
            {"name": "has_slope", "kind": "paddy", "outline": [[200, 200], [900, 200], [900, 900], [200, 900]], "bbox": [200, 200, 900, 900], "vis_bbox": [200, 200, 900, 900], "down_deg": 90},
            {"name": "no_slope", "kind": "paddy", "outline": [[1200, 200], [1900, 200], [1900, 900], [1200, 900]], "bbox": [1200, 200, 1900, 900], "vis_bbox": [1200, 200, 1900, 900]},
        ],
        "field_ditches": [{"role": "drain", "field": "no_slope", "poly": [[1300, 300], [1330, 800]], "w": 1.5}],
    }
    fails = f(M)
    assert "drain_flows_downhill" not in fails
    assert "drain_runs_cross_slope" not in fails
