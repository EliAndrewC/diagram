"""tier city tests split out of `tests.settlement.test_rolling` (feature 133 T29, GM 2026-08-26): `make quick` collects
`tests/` minus the tier, gate and tooling trees, so these are neither imported nor collected while the scope is
locked to another tier; the gate collects everything. Helpers stay in the source module and are imported."""

import pytest

from l7r.diagram.settlement import Settlement


@pytest.mark.tiers("city")
def test_farmsteads_legacy_skips_grove_for_a_city_intramural_farm():
    # the legacy farmsteads inwall-grove skip: a farm INSIDE a city wall (scale=city, inwall_groves off)
    # gets no windward grove (intramural land is too precious and the urban fabric shelters it). Uses the
    # legacy house-first path (city is not to-scale), with a wall enclosing the whole ring of farms.
    s = Settlement(1200, 900, seed=3)
    s.meta(name="C", scale="city")  # city + not toscale -> legacy path
    fld = (300, 300, 620, 560)
    s.paddy_field(fld, "", "f", amp=20)
    s.ring(fld, 8, 16, ["plain"])
    s.M["wall"] = [(120, 120), (760, 120), (760, 720), (120, 720)]  # encloses the whole ring of farms
    n = s.farmsteads()
    assert n > 0 and not s.M["groves"]  # every intramural farm skipped its grove
