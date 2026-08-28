"""tier city tests split out of `tests.check_village.test_segments_10_city_battery_b` (feature 133 T29, GM 2026-08-26): `make quick` collects
`tests/` minus the tier, gate and tooling trees, so these are neither imported nor collected while the scope is
locked to another tier; the gate collects everything. Helpers stay in the source module and are imported."""

import pytest

from tests.check_village._builders import (
    _temple_city,
    f_only,
)


@pytest.mark.tiers("city")
def test_city_temple_neighborhood_has_shrines_fires_when_bare():
    rel = [{"kind": "temple", "x": 400, "y": 400, "w": 80, "h": 60}, {"kind": "temple", "x": 550, "y": 420, "w": 80, "h": 60}]
    assert "city_temple_neighborhood_has_shrines" in f_only(_temple_city(rel), "city_temple_neighborhood_has_shrines")


@pytest.mark.tiers("city")
def test_city_temple_neighborhood_has_shrines_passes_with_shrines():
    rel = [{"kind": "temple", "x": 400, "y": 400, "w": 80, "h": 60}, {"kind": "temple", "x": 550, "y": 420, "w": 80, "h": 60}]
    rel += [{"kind": "small_shrine", "x": 450 + i * 20, "y": 480, "w": 32, "h": 24, "rot": 0} for i in range(3)]
    assert "city_temple_neighborhood_has_shrines" not in f_only(_temple_city(rel), "city_temple_neighborhood_has_shrines")


@pytest.mark.tiers("city")
def test_city_temple_neighborhood_has_shrines_skips_a_lone_temple():
    # a single temple (e.g. the warrior-fortune temple among the samurai) is not a neighborhood
    assert "city_temple_neighborhood_has_shrines" not in f_only(_temple_city([{"kind": "temple", "x": 400, "y": 400, "w": 80, "h": 60}]), "city_temple_neighborhood_has_shrines")
