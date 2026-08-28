"""tier city tests split out of `tests.check_village.test_segments_02_capital_and_walls` (feature 133 T29, GM 2026-08-26): `make quick` collects
`tests/` minus the tier, gate and tooling trees, so these are neither imported nor collected while the scope is
locked to another tier; the gate collects everything. Helpers stay in the source module and are imported."""

import pytest

from l7r.diagram import check_village
from tests.check_village._builders import (
    WALLSQ,
    _agri_city,
    _fort_city,
    _ring_towers,
    f_only,
)


@pytest.mark.tiers("city")
def test_city_interior_fields_farmhouse_density_passes_when_densely_ringed():
    # a dense ring wrapping the WHOLE perimeter (top, bottom, both sides) - a worked in-wall field
    houses = (
        [{"x": x, "y": 330} for x in range(360, 545, 30)]
        + [{"x": x, "y": 570} for x in range(360, 545, 30)]
        + [{"y": y, "x": 330} for y in range(380, 525, 30)]
        + [{"y": y, "x": 570} for y in range(380, 525, 30)]
    )
    M = _agri_city(houses)
    assert "city_interior_fields_farmhouse_density" not in f_only(M, "city_interior_fields_farmhouse_density")


@pytest.mark.tiers("city")
def test_city_interior_fields_farmhouse_density_skipped_without_agricultural_district():
    # an ordinary city (no in-wall farming declared) is not held to the rule even if a field strays inside
    M = _agri_city([], agri=False)
    assert "city_interior_fields_farmhouse_density" not in f_only(M, "city_interior_fields_farmhouse_density")


@pytest.mark.tiers("city")
def test_city_interior_fields_farmhouse_density_skips_a_tiny_field_sliver():
    # an in-wall field too small to merit its own farmhouse ring (edge < 120px) is skipped, not flagged
    tiny = {"name": "tiny", "kind": "paddy", "bbox": [480, 480, 505, 505], "outline": [[480, 480], [505, 480], [505, 505], [480, 505]]}  # ~100px perimeter
    M = {"meta": {"scale": "city", "walled": True, "agricultural_district": True, "W": 1000, "H": 1000}, "wall": WALLSQ, "gates": [[500, 200], [500, 800]], "fields": [tiny], "houses": []}
    assert "city_interior_fields_farmhouse_density" not in f_only(M, "city_interior_fields_farmhouse_density")


@pytest.mark.tiers("city")
def test_city_wall_tower_coverage_exempts_the_kido_keepclear_band():
    # a 300px tower hole in a dense 30px ring on the west curtain: mid-hole, points lose their 2nd tower
    # (garrison R ~121: the 2nd comes from 30px beyond a hole edge, so the thin band is y~441-559) and the
    # check fires - unless the hole is a recorded ward-junction keep-clear (wall_tower_keepclears), the
    # band placement itself refuses to tower (the kido chokepoint; check keep-outs mirror placement
    # keep-outs, same as the water-gate exemption)
    tw = [t for t in _ring_towers(30) if not (t["x"] == 200 and 350 < t["y"] < 650)]
    assert "city_wall_tower_coverage" in f_only(_fort_city(wall_towers=tw), "city_wall_tower_coverage")
    assert "city_wall_tower_coverage" not in f_only(_fort_city(wall_towers=tw, wall_tower_keepclears=[[200, 500]]), "city_wall_tower_coverage")


@pytest.mark.tiers("city")
def test_city_wall_tower_coverage_fires_when_sparse():
    # only the 2 gate towers: the whole curtain between them sits out of flanking range of a 2nd tower
    M = _fort_city(wall_towers=[{"x": 500, "y": 200}, {"x": 500, "y": 800}])
    assert "city_wall_tower_coverage" in f_only(M, "city_wall_tower_coverage")


@pytest.mark.tiers("city")
def test_city_wall_tower_coverage_passes_when_densely_ringed():
    # a 60px-spaced ring keeps every curtain point within garrison range (328 ft / ~121 px) of >= 2 towers
    assert "city_wall_tower_coverage" not in f_only(_fort_city(wall_towers=_ring_towers(60)), "city_wall_tower_coverage")


@pytest.mark.tiers("city")
def test_city_wall_tower_coverage_siege_tier_demands_more_than_garrison():
    # the SAME 100px-spaced ring passes garrison (R~121) but fails siege (R~78, still >=2): the tier tightens it
    ring = _ring_towers(100)
    assert "city_wall_tower_coverage" not in f_only(_fort_city(wall_towers=ring), "city_wall_tower_coverage")
    siege = _fort_city(wall_towers=ring)
    siege["meta"] = {**siege["meta"], "wall_defense": "siege"}
    assert "city_wall_tower_coverage" in f_only(siege, "city_wall_tower_coverage")


@pytest.mark.tiers("city")
def test_merchant_estate_wall_checks_skip_maps_without_estates():
    assert "merchant_estate_wall_clear_of_water" not in f_only({"meta": {"scale": "city"}, "docks": [{"x": 540, "y": 490, "w": 54, "h": 34, "rot": 0}]}, "merchant_estate_wall_clear_of_water")


@pytest.mark.tiers("capital", "city")
def test_capital_wall_matches_budget_reuses_the_provincial_tolerances():
    """Inherited deliberately - they are pinned by the shipped-Tango / rejected-Nagahara pair, and
    nothing about a capital argues for different slack."""
    assert check_village.BUDGET_TOL_OVER == 0.08
    assert check_village.BUDGET_TOL_UNDER == 0.05
