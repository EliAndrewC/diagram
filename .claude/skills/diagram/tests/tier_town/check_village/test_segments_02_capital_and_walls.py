"""tier town tests split out of `tests.check_village.test_segments_02_capital_and_walls` (feature 133 T29, GM 2026-08-26): `make quick` collects
`tests/` minus the tier, gate and tooling trees, so these are neither imported nor collected while the scope is
locked to another tier; the gate collects everything. Helpers stay in the source module and are imported."""

import pytest

from tests.check_village._builders import (
    _mest_city,
    f_only,
)


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
