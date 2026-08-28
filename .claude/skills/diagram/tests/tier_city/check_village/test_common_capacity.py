"""tier city tests split out of `tests.check_village.test_common_capacity` (feature 133 T29, GM 2026-08-26): `make quick` collects
`tests/` minus the tier, gate and tooling trees, so these are neither imported nor collected while the scope is
locked to another tier; the gate collects everything. Helpers stay in the source module and are imported."""

import pytest

from l7r.diagram import check_village
from tests.check_village._builders import _CITY_WALL_SMALL, _FULL_Q, _diamond_city, _dwell_grid, _pop_city, bldg


@pytest.mark.tiers("city")
def test_city_capacity_skips_footprintless_item():
    # a dwelling dict with no "w" is skipped by _rects (no rect to sample) but still COUNTS
    # toward placed D - exercises the "if 'w' not in it: continue" guard without crashing.
    M = _diamond_city(185)
    M["buildings"] = [{"x": 200, "y": 200, "kind": "laborer"}]  # footprint-less
    rep = check_village.city_capacity(M)
    assert rep["placed"] == 1


@pytest.mark.tiers("city")
def test_city_capacity_counts_only_in_wall_dwellings():
    # extramural dwellings do not inflate the placed count
    wall = _CITY_WALL_SMALL
    inside = [bldg(300 + (i % 10) * 20, 300, "laborer") for i in range(20)]
    M = {"meta": {"scale": "city", "population": 100}, "wall": wall, "buildings": inside + [bldg(50, 500, "laborer")]}
    assert check_village.city_capacity(M)["placed"] == 20  # the outside one is not counted


@pytest.mark.tiers("city")
def test_city_capacity_per_quarter_table_lists_residential_quarters():
    q = {"poly": _FULL_Q, "zone": "residential", "kind": None, "name": "warren"}
    civic = {"poly": [[600, 600], [790, 600], [790, 790], [600, 790]], "zone": "civic", "kind": None, "name": "yamen"}
    M = _pop_city(_dwell_grid(210, 560, 210, 560, 12), population=400, quarters=[q, civic])
    rep = check_village.city_capacity(M)
    names = {pq["name"] for pq in rep["per_quarter"]}
    assert "warren" in names and "yamen" not in names  # residential listed; pure civic not in the density table
