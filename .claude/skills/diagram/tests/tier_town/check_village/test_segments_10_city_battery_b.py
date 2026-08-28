"""tier town tests split out of `tests.check_village.test_segments_10_city_battery_b` (feature 133 T29, GM 2026-08-26): `make quick` collects
`tests/` minus the tier, gate and tooling trees, so these are neither imported nor collected while the scope is
locked to another tier; the gate collects everything. Helpers stay in the source module and are imported."""

import pytest

from tests.check_village._builders import (
    WALLSQ,
    f_only,
)


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
